#!/usr/bin/env python
"""S6-B3204 (DECISION A, owner approved 2026-10-18): the Phase-1B PORTFOLIO-UNIT
evaluation - stage 1, admission -> trade-source resolution.

WHY THIS STAGE EXISTS SEPARATELY. The 16 Step-2 admissions carry heterogeneous
provenance: 3 name a Step-2 cube directly; 13 are offline campaigns whose
grids re-scored the R5 merged cube (their own _doc lines, or the grader's CUBE
constant in institutional_companion_grid.py, name output_r5_merged_1_7). A
blend built on a guessed join would inherit every accident of the guess
(L722/L724), so resolution is its own stage with its own artifact, and ANY
admission the resolver cannot trace is REFUSED BY NAME - never skipped
silently (#279). Stage 2 (trade extraction + NET blend at the tiered position
sizes) consumes this artifact and refuses while any admission is unresolved.

Resolution rules, in order, each keyed on the admission's OWN artifact:
  1. grid_artifact named output_<cube>_grid_auto.json -> that cube dir.
  2. the artifact json carries cube_dir -> that cube dir.
  3. the artifact's _doc names output_r5_merged_1_7 -> the R5 merged cube
     (an offline re-score; the combination re-applies at stage 2).
  4. otherwise REFUSED with the reason.
A resolved source must hold trade_exit_detail.csv on disk or the admission is
REFUSED (fail closed - absence of the data is not a quiet shrink of the book).

Usage:
  python scripts/build_phase1b_portfolio.py --resolve
      writes output_audit/b3204_portfolio_resolution.json and prints the table.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADMISSIONS = ROOT / "output_audit" / "phase_1b_step2_admissions.json"
RESOLUTION = ROOT / "output_audit" / "b3204_portfolio_resolution.json"
R5_CUBE = "output_r5_merged_1_7"
TRADE_FILE = "trade_exit_detail.csv"
GRID_SUFFIX = "_grid_auto.json"


def load_admissions(path=None) -> list[dict]:
    p = Path(path) if path else ADMISSIONS
    return json.loads(p.read_text(encoding="utf-8"))["admissions"]


def resolve_one(adm: dict, root=None) -> dict:
    """One admission -> its trade-source record (or a REFUSED record)."""
    root = Path(root) if root else ROOT
    strat = adm.get("strategy") or "<unnamed>"
    ga = adm.get("grid_artifact") or ""
    out = {"strategy": strat, "grid_artifact": ga,
           "combination": adm.get("combination"), "exit": adm.get("exit"),
           "direction": adm.get("direction")}
    gp = root / ga
    if not ga or not gp.exists():
        return {**out, "resolution": "REFUSED",
                "reason": f"grid artifact missing: {ga!r}"}
    name = gp.name
    cube = None
    how = None
    if name.startswith("output_") and name.endswith(GRID_SUFFIX):
        # the cube DIR keeps the output_ prefix: output_<x>_grid_auto.json
        # names the dir output_<x> (first run refused smc by stripping it)
        cube = name[:-len(GRID_SUFFIX)]
        how = "DIRECT (cube named by the grid artifact's own filename)"
    else:
        art = json.loads(gp.read_text(encoding="utf-8"))
        cd = art.get("cube_dir") or art.get("cube") or ""
        doc = str(art.get("_doc") or "")
        if cd:
            cube = cd
            how = "DIRECT (artifact's own cube_dir field)"
        elif R5_CUBE in doc:
            cube = R5_CUBE
            how = ("R5_RESCORE (the artifact's _doc names the R5 merged cube "
                   "as its source; the combination re-applies at stage 2)")
    if cube is None:
        return {**out, "resolution": "REFUSED",
                "reason": "no cube pointer: filename not output_*_grid_auto, "
                          "no cube_dir field, _doc names no known cube"}
    tf = root / cube / TRADE_FILE
    if not tf.exists():
        return {**out, "resolution": "REFUSED", "cube": cube,
                "reason": f"{cube}/{TRADE_FILE} not on disk"}
    return {**out, "resolution": "RESOLVED", "cube": cube, "how": how,
            "trade_file": f"{cube}/{TRADE_FILE}",
            "trade_file_bytes": tf.stat().st_size}


def resolve(admissions=None, root=None) -> dict:
    adms = admissions if admissions is not None else load_admissions()
    rows = [resolve_one(a, root=root) for a in adms]
    refused = [r for r in rows if r["resolution"] == "REFUSED"]
    return {
        "_doc": ("S6-B3204 stage 1 - admission -> trade-source resolution for "
                 "the Phase-1B portfolio-unit evaluation (owner approved "
                 "2026-10-18). Every admission resolves or is REFUSED by "
                 "name; stage 2 refuses to blend while any row is REFUSED."),
        "admissions": len(rows),
        "resolved": len(rows) - len(refused),
        "refused": [r["strategy"] for r in refused],
        "rows": rows,
    }


BLEND_OUT = ROOT / "output_audit" / "b3204_portfolio_eval.json"
# MDD needs a capital scale (Sharpe does not): each trade is sized at the
# MEDIUM-HIGH tier, 1.5 pct of book (backtest.config position-sizing tiers
# 5/4/3/1.5/0.75) - DECLARED, since no admitted line carries a ruled tier.
TRADE_FRACTION = 0.015
N_ADMISSIONS = 16


def _trade_set(adm: dict):
    """One admission's reproduced NET trade set -> (status, reason, frame).

    14 of 16 lines ride scripts/rescore_admissions_net.py's fail-closed
    reproduction (#290: the raw reconstruction must equal the recorded
    admission row, or the line is refused). The two ALREADY-NET lines (their
    reads of record are net-basis) extract directly from their cubes with a
    count check against the resolution artifact's source."""
    import rescore_admissions_net as ran
    strat = adm["strategy"]
    art = json.loads((ROOT / adm["grid_artifact"]).read_text(encoding="utf-8"))
    if strat == "smc_breaker_block_long":
        return _smc_line(adm, art)
    if strat == "pairs_mean_reversion_long":
        combo = adm["combination"]
        cube = ROOT / str(art.get("cube_dir"))
        f = ran.cube_frame(cube, strat, [combo["axis"]])
        sub = ran.apply_ops(f[f["exit_method"] == adm["exit"]],
                            [(combo["axis"], combo["op"],
                              float(combo["level"]))])
        row = next((r for r in (art.get("qualifiers_all_six_gates")
                                or art.get("qualifiers") or [])
                    if r.get("axis") == combo["axis"]
                    and r.get("op") == combo["op"]
                    and abs(float(r.get("level")) - float(combo["level"])) < 1e-9
                    and r.get("exit") == adm["exit"]), None)
        if row is None:
            return ("REFUSED", "admitted pairs cell not found in its read", None)
        bad = _count_gate(sub, row.get("holdout_n"),
                          row.get("full_n") or row.get("full_period_n"))
        if bad:
            return ("REFUSED", f"pairs count reproduction failed: {bad}", None)
        return ("OK", "ALREADY-NET read (artifact basis=net); condition "
                      "re-applied on the Step-2 cube; counts reproduce "
                      f"{row.get('holdout_n')}/{row.get('full_n')}", sub)
    if strat == "three_white_soldiers":
        res, sub = ran.reproduce_tws_line(adm)
    else:
        res, sub = ran.reproduce_r5_line(adm, art)
    if sub is None:
        return ("REFUSED", f"{res.get('status')}: {res.get('reason')}", None)
    return ("OK", f"reproduced (#290 gate): ops={res.get('ops')}", sub)


def _count_gate(sub, ho_target, fp_target) -> list:
    """#290 for the directly-extracted lines: the reproduced trade set's
    holdout and full-period counts must EQUAL the recorded admission row's,
    or the line is refused. Returns the mismatches (empty = reproduced)."""
    import roster_core as rc
    bad = []
    ho_n, fp_n = len(rc.holdout(sub)), len(sub)
    if ho_target is None or int(ho_target) != ho_n:
        bad.append(f"holdout_n {ho_n} vs recorded {ho_target}")
    if fp_target is None or int(fp_target) != fp_n:
        bad.append(f"full_period_n {fp_n} vs recorded {fp_target}")
    return bad


def _smc_line(adm: dict, grid: dict):
    """smc_breaker_block_long: its admitted combination (close_mitigation,
    break_pct_max, age_bars_max, tail_n) is NOT a persisted signal - the
    grade of record re-diagnosed every fire's order blocks from OHLCV
    (tighten_breaker_block.diagnose_fire / survives). Reproduced with those
    SAME functions at the grid's own swing length, then count-gated against
    the grid row the admission names. The first build of this file took all
    cube rows at the exit (437) for a 180-trade line - caught before any
    figure was reported (S6-B3204)."""
    import pandas as pd
    import rescore_admissions_net as ran
    import tighten_breaker_block as tbb
    strat = adm["strategy"]
    combo = adm["combination"]
    sw = int((grid.get("config") or {})["P1_swing_length"])
    row = next((r for r in grid.get("results") or []
                if r.get("exit") == adm["exit"]
                and r.get("close_mitigation") == combo["close_mitigation"]
                and r.get("break_pct_max") == combo["break_pct_max"]
                and r.get("age_bars_max") == combo["age_bars_max"]
                and r.get("tail_n") == combo["tail_n"]), None)
    if row is None:
        return ("REFUSED", "admitted smc row not found in its grid", None)
    cube = ROOT / Path(adm["grid_artifact"]).name[:-len(GRID_SUFFIX)]
    f = ran.cube_frame(cube, strat, [])
    base = f[f["exit_method"] == adm["exit"]]
    keep = set()
    for t in sorted(base["ticker"].unique()):
        df = tbb._load_ohlcv(t)
        if df is None:
            return ("REFUSED", f"no OHLCV parquet for {t}", None)
        for when in base.loc[base["ticker"] == t, "entry_date"].unique():
            d = tbb.diagnose_fire(df, pd.Timestamp(when), swing_length=sw,
                                  close_mitigation=bool(combo["close_mitigation"]))
            if d and tbb.survives(d, combo["break_pct_max"],
                                  combo["age_bars_max"], int(combo["tail_n"])):
                keep.add((t, when))
    sub = base[[(r.ticker, r.entry_date) in keep for r in base.itertuples()]]
    bad = _count_gate(sub, row.get("holdout_n"), row.get("full_period_n"))
    if bad:
        return ("REFUSED", f"smc count reproduction failed: {bad}", None)
    return ("OK", "re-diagnosed with tighten_breaker_block at sw="
                  f"{sw}; counts reproduce {row.get('holdout_n')}/"
                  f"{row.get('full_period_n')}", sub)


def _daily_curve(frames: dict) -> "object":
    """Equal-weight blend: each trade's NET pnl is realized at its exit date
    (entry + hold_days business days). Sharpe is scale-free; MDD is computed
    at TRADE_FRACTION capital per trade. Realized-only curves understate
    intra-trade drawdown - DISCLOSED on the artifact."""
    import pandas as pd
    import roster_core as rc
    rows = []
    for strat, sub in frames.items():
        import numpy as np
        pnl = rc.net_pnl(pd.to_numeric(sub["pnl_pct"], errors="coerce"))
        ed = pd.to_datetime(sub["entry_date"].astype(str), errors="coerce")
        hd = (pd.to_numeric(sub["hold_days"], errors="coerce")
              .fillna(0).clip(lower=0).astype(int))
        ok = ed.notna()
        # vectorized business-day shift; the BDay-per-row map left the column
        # object-dtype and the .dt accessor refused it (first live run)
        exit_d = pd.to_datetime(np.busday_offset(
            ed[ok].values.astype("datetime64[D]"), hd[ok].values,
            roll="forward"))
        rows.append(pd.DataFrame({"strategy": strat, "exit_date": exit_d,
                                  "net_pnl_pct": pnl[ok].values}))
    allt = pd.concat(rows, ignore_index=True).dropna(subset=["exit_date"])
    daily = (allt.groupby(allt["exit_date"].dt.date)["net_pnl_pct"].sum()
             .sort_index())
    idx = pd.bdate_range(daily.index.min(), daily.index.max())
    series = daily.reindex(idx.date, fill_value=0.0)
    return allt, series


def _risk_diagnostics(r) -> dict:
    """S6-B3096b (owner-approved Phase-1B entry work, 2026-10-19): the
    DEMOTED diagnostics (roster_core.DEMOTED) on a BLENDED daily return
    series - REPORTED, never gated. The line evaluator scores one trade
    series, so a book's drawdown lives here (the B3139 council's restated
    home for the 2026-09-24 approval). calmar = annualised return / |max
    drawdown| of the daily equity curve; deflated_sharpe and psr come from
    the function roster_core.evaluate calls (L593), fed the PER-PERIOD
    Sharpe and RAW kurtosis (B2646), the deflated figure annualised like
    the window's sharpe. None where a figure is not measurable - fewer
    than 30 days for the deflated pair, a flat curve, no drawdown, or a
    curve that ends at or below zero - never a fabricated 0 (L580)."""
    import numpy as np
    import pandas as pd
    import roster_core as rc
    out = {"calmar": None, "deflated_sharpe": None, "psr": None}
    r = np.asarray(r, dtype=float)
    n = len(r)
    sd = float(np.std(r)) if n else 0.0
    if n < 2 or sd == 0:
        return out
    eq = np.cumprod(1.0 + r)
    mdd = float((eq / np.maximum.accumulate(eq) - 1.0).min())
    if mdd < 0 and float(eq[-1]) > 0:
        ann = float(eq[-1]) ** (252.0 / n) - 1.0
        out["calmar"] = round(ann / abs(mdd), 3)
    s = pd.Series(r)
    d = rc._deflated_sharpe(float(np.mean(r)) / sd, n, float(s.skew()),
                            float(s.kurtosis()) + 3.0)
    if d.get("deflated_sharpe") is not None:
        out["deflated_sharpe"] = round(float(d["deflated_sharpe"]) * float(np.sqrt(252)), 3)
    if d.get("psr") is not None:
        out["psr"] = round(float(d["psr"]), 4)
    return out


def _window_stats(series, lo=None, hi=None) -> dict:
    import numpy as np
    s = series
    if lo is not None:
        s = s[[d >= lo for d in s.index]]
    if hi is not None:
        s = s[[d < hi for d in s.index]]
    r = s.values * TRADE_FRACTION / 100.0      # daily portfolio return
    if len(r) < 20 or float(np.std(r)) == 0:
        return {"days": int(len(r)), "sharpe": None, "mdd_pct": None,
                "calmar": None, "deflated_sharpe": None, "psr": None}
    sharpe = float(np.mean(r) / np.std(r) * np.sqrt(252))
    eq = np.cumprod(1.0 + r)
    mdd = float((eq / np.maximum.accumulate(eq) - 1.0).min())
    return {"days": int(len(r)), "sharpe": round(sharpe, 3),
            "mdd_pct": round(100 * mdd, 2),
            "total_return_pct": round(100 * (eq[-1] - 1.0), 2),
            **_risk_diagnostics(r)}


def _benchmark(lo, hi) -> dict:
    """The CONTROL: SPY buy-and-hold over the same window, daily
    mark-to-market. All 16 admitted lines are LONG, so a strong market year
    lifts every line regardless of edge; a portfolio figure is read against
    this, never alone. NOT method-identical to the blend (the blend realizes
    pnl at exit, which is lumpier and understates its Sharpe) - disclosed."""
    import numpy as np
    import pandas as pd
    p = ROOT / "backtest" / "data" / "cache" / "ohlcv" / "SPY.parquet"
    df = pd.read_parquet(p)
    if not isinstance(df.index, pd.DatetimeIndex) and "date" in df.columns:
        df = df.set_index("date")
    df.index = pd.to_datetime(df.index)
    col = "close" if "close" in df.columns else "Close"
    r = df[col].sort_index().pct_change().dropna()
    s = r[(r.index.date >= lo) & (r.index.date < hi)]
    eq = (1 + s).cumprod()
    return {"days": int(len(s)),
            "sharpe": round(float(s.mean() / s.std() * np.sqrt(252)), 3),
            "total_return_pct": round(100 * float(eq.iloc[-1] - 1), 2),
            "mdd_pct": round(100 * float((eq / eq.cummax() - 1).min()), 2),
            **_risk_diagnostics(s.values)}


def blend() -> dict:
    import roster_core as rc
    res = resolve()
    if res["refused"]:
        raise SystemExit(f"REFUSED at stage 1: {res['refused']}")
    frames, lines = {}, []
    for adm in load_admissions():
        status, why, sub = _trade_set(adm)
        lines.append({"strategy": adm["strategy"], "exit": adm["exit"],
                      "status": status, "how": why,
                      "trades": None if sub is None else int(len(sub))})
        if status != "OK":
            continue
        frames[adm["strategy"]] = sub
    refused = [l["strategy"] for l in lines if l["status"] != "OK"]
    if refused:
        return {"status": "REFUSED", "refused": refused, "lines": lines}
    allt, series = _daily_curve(frames)
    boundary = rc.HO_START      # the IS/HO boundary of record, never retyped
    out = {
        "_doc": ("S6-B3204 (owner approved 2026-10-18): the Phase-1B "
                 "PORTFOLIO-UNIT evaluation - equal-weight blend of the 16 "
                 "admitted lines' reproduced NET trade sets. DISCLOSED-RE-READ:"
                 " the holdout window was read per-strategy at admission; this"
                 " blend re-uses those banked trades and spends no new read. "
                 "DISCLOSURES: equal weight per line (no admitted line carries"
                 " a ruled tier); each trade at TRADE_FRACTION of book for the"
                 " MDD scale; pnl realized at exit date, so intra-trade "
                 "drawdown is understated."),
        "basis": "net = roster_core.net_pnl (winsorize %s, cost %s bps)" % (
            rc.WINSORIZE, rc.COST_BPS),
        "trade_fraction": TRADE_FRACTION,
        "is_holdout_boundary": str(boundary),
        "lines": lines,
        "portfolio": {
            "full": _window_stats(series),
            "in_sample": _window_stats(series, hi=boundary),
            "holdout": _window_stats(series, lo=boundary),
        },
        "benchmark_spy": {
            "in_sample": _benchmark(rc.IS_START, rc.IS_END),
            "holdout": _benchmark(rc.HO_START, rc.HO_END),
        },
        "per_line_holdout": {
            s: _window_stats(
                _daily_curve({s: f})[1], lo=boundary)
            for s, f in frames.items()
        },
        # L525: a pooled IS-vs-holdout gap is decomposed per line before it
        # is explained - the in-sample leg per line, beside the holdout leg
        "per_line_in_sample": {
            s: _window_stats(
                _daily_curve({s: f})[1], hi=boundary)
            for s, f in frames.items()
        },
        "status": "OK",
    }
    return out


# ---------------------------------------------------------------- S6-B3288
# (B3139q-r108; owner ruling 2026-10-22 on S6-B2178c Decision 1, option a):
# the SELECTED-EXIT correlation over the Phase-1B members that carry a graded
# selected-exit line - the Step-2 admissions (reproduced above through the
# #290 gate) plus the graded funnel cells (reproduced here against the
# sidecar's own holdout record) - on the holdout window. Mirrors carry no
# graded line and are listed, never blended. Zero engine runs.
CORR_OUT = ROOT / "output_audit" / "b3288_selected_exit_correlation.json"
CORR_MD = ROOT / "output_audit" / "b3288_selected_exit_correlation_summary.md"
SIDECAR = ROOT / "output_audit" / "b1453_phase_1b_roster.json"
# the funnel's grade of record cast pnl to float32 before the net basis
# (build_phase_1b_roster.main); a float64 re-read lands within one rounding
# step of its 3-decimal Sharpe. Counts are EXACT.
SHARPE_TOL = 2e-3


def _funnel_trade_sets(root=None):
    """The graded funnel cells' trade sets at their selected exit - one cube
    read per cube label, each cell gated (#290) on its holdout count EXACT
    and its NET holdout Sharpe within SHARPE_TOL of the sidecar's record.
    The sidecar stores the TRUTHFUL exit name (roster_core.truthful_exit_name),
    so a cell whose cube column carries the pre-B1593 label is matched
    through DEGRADED_EXITS_PRE_B1593, one label at a time - never both at
    once, which would double-count. Returns (lines, frames); a cell that
    fails the gate is a REFUSED line naming the mismatch, with no frame."""
    import pandas as pd
    import roster_core as rc
    root = Path(root) if root else ROOT
    side = json.loads((root / "output_audit" / "b1453_phase_1b_roster.json")
                      .read_text(encoding="utf-8"))
    cells = side.get("roster")
    if not isinstance(cells, list) or not isinstance(side.get("cubes"), dict):
        raise ValueError("b1453_phase_1b_roster.json: no 'roster' list or "
                         "'cubes' map - refusing a partial set (L642)")
    lines, frames = [], {}
    for label in sorted({c["cube"] for c in cells}):
        mine = [c for c in cells if c["cube"] == label]
        p = root / side["cubes"][label] / TRADE_FILE
        if not p.exists():
            for c in mine:
                lines.append({"strategy": c["strategy"], "role": "FUNNEL_CELL",
                              "exit": c["exit"], "status": "REFUSED",
                              "how": f"{p} not on disk", "trades": None,
                              "holdout_trades": None})
            continue
        df = pd.read_csv(p, usecols=["ticker", "strategy", "entry_date",
                                     "direction", "exit_method", "pnl_pct",
                                     "hold_days"], low_memory=False,
                         dtype={"strategy": "category", "direction": "category",
                                "exit_method": "category", "ticker": "category"})
        df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
        for c in mine:
            labels = [[c["exit"]]] + [[k] for k, v in
                                      rc.DEGRADED_EXITS_PRE_B1593.items()
                                      if v == c["exit"]]
            first_bad, sub_ok = None, None
            for names in labels:
                sub = df[(df["strategy"] == c["strategy"])
                         & (df["direction"] == c["direction"])
                         & (df["exit_method"].isin(names))].copy()
                ho = rc.holdout(sub)
                ev = (rc.evaluate(rc.net_pnl(ho["pnl_pct"]), ho["hold_days"],
                                  full_period_n=len(sub)) if len(sub) else None)
                bad = []
                if len(ho) != int(c["holdout"]["n"]):
                    bad.append(f"holdout_n {len(ho)} vs recorded {c['holdout']['n']}")
                got = None if ev is None else ev.get("sharpe")
                want = c["holdout"].get("sharpe")
                if got is None or want is None or abs(float(got) - float(want)) > SHARPE_TOL:
                    bad.append(f"holdout sharpe {got} vs recorded {want}")
                if not bad:
                    sub_ok = sub
                    break
                first_bad = first_bad or (names[0], bad)
            if sub_ok is None:
                lines.append({"strategy": c["strategy"], "role": "FUNNEL_CELL",
                              "exit": c["exit"], "status": "REFUSED",
                              "how": f"funnel reproduction failed at exit "
                                     f"{first_bad[0]}: {first_bad[1]}",
                              "trades": None, "holdout_trades": None})
                continue
            frames[c["strategy"]] = sub_ok
            lines.append({"strategy": c["strategy"], "role": "FUNNEL_CELL",
                          "exit": c["exit"], "status": "OK",
                          "how": f"{label} cube at exit {c['exit']}; holdout n "
                                 f"and net Sharpe reproduce the sidecar "
                                 f"({c['holdout']['n']}, {c['holdout']['sharpe']})",
                          "trades": int(len(sub_ok)),
                          "holdout_trades": int(c["holdout"]["n"])})
    return lines, frames


def _holdout_matrix(frames: dict):
    """Per-member daily NET pnl over the holdout business days, exit-date
    attributed by _daily_curve, 0.0 where a member has no exit that day -
    the COMBINATION grain (B2182's disclosed choice): right for how streams
    add, wrong for a standalone Sharpe claim."""
    import pandas as pd
    import roster_core as rc
    idx = [d for d in pd.bdate_range(rc.HO_START, rc.HO_END).date if d < rc.HO_END]
    cols = {}
    for s, f in frames.items():
        _, ser = _daily_curve({s: f})
        cols[s] = ser.reindex(idx, fill_value=0.0).astype(float)
    return pd.DataFrame(cols, index=idx)


def _effective_n(corr):
    """(sum lambda)^2 / sum lambda^2 over the correlation matrix's
    eigenvalues: N for uncorrelated members, 1 for perfectly correlated
    ones - the roster's de-dup basis restated as a count. None on an empty
    or NaN-bearing matrix (a member with no holdout variance), never 0."""
    import numpy as np
    a = corr.to_numpy(dtype=float)
    if a.size == 0 or np.isnan(a).any():
        return None
    lam = np.clip(np.linalg.eigvalsh(a), 0.0, None)
    s2 = float((lam ** 2).sum())
    return None if s2 == 0 else round(float(lam.sum()) ** 2 / s2, 3)


def correlation() -> dict:
    """The selected-exit correlation artifact. Every long roster member from
    phase1b_membership.members() gets a line: admissions through _trade_set
    (#290), funnel cells through _funnel_trade_sets (#290), and a member with
    neither is REFUSED by name. Any refused line refuses the artifact
    (blend()'s convention - a matrix over a smaller set would describe a
    book nobody admitted). Prints each member's source and row count as it
    is extracted, before any series is built (the cost disclosure the
    ticket asked for)."""
    import numpy as np
    import roster_core as rc
    import phase1b_membership as pm
    mem = pm.members()
    longs = sorted(n for n, r in mem.items() if set(pm.LONG_ROLES) & set(r["roles"]))
    mirrors = sorted(n for n, r in mem.items()
                     if set(pm.MIRROR_ROLES) & set(r["roles"]) and n not in longs)
    res = resolve()
    if res["refused"]:
        raise SystemExit(f"REFUSED at stage 1: {res['refused']}")
    frames, lines = {}, []
    for adm in load_admissions():
        status, why, sub = _trade_set(adm)
        row = {"strategy": adm["strategy"], "role": "STEP2_ADMISSION",
               "exit": adm["exit"], "status": status, "how": why,
               "trades": None if sub is None else int(len(sub)),
               "holdout_trades": None if sub is None else int(len(rc.holdout(sub)))}
        lines.append(row)
        print(f"  {row['role']:16s} {row['strategy'][:44]:44} {status:8s} "
              f"trades={row['trades']} holdout={row['holdout_trades']}")
        if status == "OK":
            frames[adm["strategy"]] = sub
    f_lines, f_frames = _funnel_trade_sets()
    for row in f_lines:
        print(f"  {row['role']:16s} {row['strategy'][:44]:44} {row['status']:8s} "
              f"trades={row['trades']} holdout={row['holdout_trades']}")
    lines += f_lines
    frames.update(f_frames)
    have = {l["strategy"] for l in lines}
    for n in longs:
        if n not in have:
            lines.append({"strategy": n, "role": "MEMBER-NO-LINE", "exit": None,
                          "status": "REFUSED", "trades": None, "holdout_trades": None,
                          "how": "a long roster member with neither an admission "
                                 "nor a funnel cell - no selected-exit line to read"})
    extra = sorted(have - set(longs))
    refused = sorted(l["strategy"] for l in lines if l["status"] != "OK")
    base = {
        "_doc": ("S6-B3288 (B3139q-r108; owner ruling 2026-10-22 on S6-B2178c "
                 "Decision 1, option a): the SELECTED-EXIT correlation over the "
                 "Phase-1B members with a graded selected-exit line - the Step-2 "
                 "admissions reproduced through rescore_admissions_net / "
                 "_trade_set (#290) and the funnel cells reproduced against "
                 "the sidecar's holdout record (#290) - on the holdout window. "
                 "DISCLOSED-RE-READ: the holdout trades were banked at admission; "
                 "this artifact spends no new read. Mirrors carry no graded line "
                 "and are listed, not blended. Daily streams are exit-date "
                 "attributed and zero-filled (the combination grain). Zero "
                 "engine runs. Changes no admission and no gate; it measures."),
        "basis": "net = roster_core.net_pnl (winsorize %s, cost %s bps)" % (
            rc.WINSORIZE, rc.COST_BPS),
        "window": {"holdout": [str(rc.HO_START), str(rc.HO_END)]},
        "members_long": len(longs), "members_with_line": len(lines),
        "members_not_in_membership": extra, "lines": lines,
        "mirrors_not_blended": mirrors, "refused": refused,
    }
    if refused or extra:
        return {**base, "status": "REFUSED"}
    m = _holdout_matrix(frames)
    corr = m.corr()
    names = list(corr.columns)
    iu = np.triu_indices(len(names), k=1)
    vals = corr.to_numpy()[iu]
    pairs = sorted(((names[i], names[j], round(float(corr.iat[i, j]), 4))
                    for i, j in zip(*iu)), key=lambda t: -abs(t[2]))
    _, series = _daily_curve(frames)
    # r108b: bounded at BOTH ends - exits realised after HO_END (trailing
    # exits on late holdout entries) are outside the window the label names;
    # the first run counted 456 days for a 1-year window (L717)
    port = _window_stats(series, lo=rc.HO_START, hi=rc.HO_END)
    adm_names = [l["strategy"] for l in lines if l["role"] == "STEP2_ADMISSION"]
    fun_names = [l["strategy"] for l in lines if l["role"] == "FUNNEL_CELL"]
    gate = float(rc.PC["min_sharpe_overall"])
    out = {
        **base, "status": "OK", "members_blended": len(names),
        "active_days_per_member": {s: int((m[s] != 0).sum()) for s in names},
        "avg_pairwise_rho": round(float(np.nanmean(vals)), 4),
        "median_pairwise_rho": round(float(np.nanmedian(vals)), 4),
        "pairs_total": int(len(vals)),
        "pairs_above_0_5": int((np.abs(vals) > 0.5).sum()),
        "top_pairs": pairs[:10],
        "per_member_mean_rho": {s: round(float(np.nanmean([corr.at[s, t] for t in names if t != s])), 4)
                                for s in names},
        "effective_n": _effective_n(corr),
        "portfolio_holdout": port,
        "portfolio_holdout_admissions_only": _window_stats(
            _daily_curve({s: frames[s] for s in adm_names})[1], lo=rc.HO_START, hi=rc.HO_END),
        "portfolio_holdout_funnel_only": _window_stats(
            _daily_curve({s: frames[s] for s in fun_names})[1], lo=rc.HO_START, hi=rc.HO_END),
        "gate": {"min_sharpe_overall": gate,
                 "clears": bool(port["sharpe"] is not None and port["sharpe"] >= gate),
                 "note": "the live pooled Sharpe bar applied to the equal-weight "
                         "holdout blend - a measurement, not an admission"},
        "benchmark_spy_holdout": _benchmark(rc.HO_START, rc.HO_END),
        "correlation_matrix": {"members": names,
                               "rho": [[None if np.isnan(x) else round(float(x), 4)
                                        for x in row] for row in corr.to_numpy()]},
        "caveats": [
            "exit-date attribution with zero-filled days deflates every "
            "pairwise rho toward 0 and every standalone vol; right for how "
            "streams add, wrong for a standalone Sharpe claim (B2182)",
            "one holdout year, one regime: the crisis rho is the one that "
            "matters and this window cannot measure it",
            "the members were SELECTED on this holdout (each line's gates were "
            "read on it at admission), so the blend inherits that selection - "
            "DISCLOSED-RE-READ, no new read spent",
            "equal weight per line (no admitted line carries a ruled tier); "
            "pnl realized at exit, so intra-trade drawdown is understated",
            "the blend stats and the matrix cover the holdout business days only: "
            "pnl realised after the holdout end (late entries on trailing exits) is "
            "outside every figure here",
        ],
    }
    rc.stamp_metric_code(out)
    return out


def _corr_md(out: dict) -> str:
    L = ["# Selected-exit correlation over the Phase-1B members (S6-B3288, zero engine runs)", ""]
    if out.get("status") != "OK":
        L += [f"**REFUSED** - refused members: {', '.join(out.get('refused') or [])}; "
              f"not in membership: {', '.join(out.get('members_not_in_membership') or [])}", ""]
        return "\n".join(L) + "\n"
    p = out["portfolio_holdout"]
    L += [f"- members blended: {out['members_blended']} of {out['members_long']} long roster members "
          f"(mirrors listed, not blended: {len(out['mirrors_not_blended'])})",
          f"- holdout window {out['window']['holdout'][0]} .. {out['window']['holdout'][1]}; "
          f"basis {out['basis']}",
          f"- average pairwise rho {out['avg_pairwise_rho']}, median {out['median_pairwise_rho']}, "
          f"{out['pairs_above_0_5']} of {out['pairs_total']} pairs above 0.5 in magnitude",
          f"- eigenvalue effective N {out['effective_n']} of {out['members_blended']}",
          f"- equal-weight holdout blend: Sharpe {p['sharpe']} over {p['days']} days, "
          f"max drawdown {p['mdd_pct']} pct; the live pooled bar {out['gate']['min_sharpe_overall']} "
          f"is {'cleared' if out['gate']['clears'] else 'NOT cleared'}",
          f"- admissions-only blend Sharpe {out['portfolio_holdout_admissions_only']['sharpe']}; "
          f"funnel-only blend Sharpe {out['portfolio_holdout_funnel_only']['sharpe']}; "
          f"SPY buy-and-hold Sharpe {out['benchmark_spy_holdout']['sharpe']} (the control)",
          "", "| pair | rho |", "|---|---|"]
    for a, b, r in out["top_pairs"]:
        L.append(f"| {a} / {b} | {r} |")
    L += ["", "Caveats: " + " / ".join(out["caveats"])]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolve", action="store_true",
                    help="run stage 1 and write the resolution artifact")
    ap.add_argument("--blend", action="store_true",
                    help="run stages 2+3 and write the portfolio evaluation")
    ap.add_argument("--correlation", action="store_true",
                    help="S6-B3288: the selected-exit correlation over the "
                         "Phase-1B members with a graded line (holdout window)")
    a = ap.parse_args()
    if a.correlation:
        out = correlation()
        CORR_OUT.write_bytes((json.dumps(out, indent=2, ensure_ascii=False,
                                         default=str) + "\n").encode("utf-8"))
        CORR_MD.write_bytes(_corr_md(out).encode("utf-8"))
        print(json.dumps({k: out.get(k) for k in (
            "status", "refused", "members_blended", "members_long",
            "avg_pairwise_rho", "effective_n", "portfolio_holdout", "gate")},
            indent=2, default=str))
        print(f"wrote {CORR_OUT}")
        return 0 if out.get("status") == "OK" else 1
    if a.blend:
        out = blend()
        BLEND_OUT.write_bytes((json.dumps(out, indent=2, ensure_ascii=False)
                               + "\n").encode("utf-8"))
        print(json.dumps({"portfolio": out.get("portfolio"),
                          "status": out.get("status"),
                          "refused": out.get("refused", [])}, indent=2))
        print(f"wrote {BLEND_OUT}")
        return 0 if out.get("status") == "OK" else 1
    if not a.resolve:
        ap.print_help()
        return 2
    res = resolve()
    RESOLUTION.write_bytes(
        (json.dumps(res, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"admissions {res['admissions']} | resolved {res['resolved']} | "
          f"refused {len(res['refused'])}")
    for r in res["rows"]:
        tag = r["resolution"]
        tgt = r.get("cube") or r.get("reason")
        print(f"  {r['strategy'][:44]:44} {tag:9} {tgt}")
    if res["refused"]:
        print(f"REFUSED by name: {', '.join(res['refused'])}")
        return 1
    print(f"wrote {RESOLUTION}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
