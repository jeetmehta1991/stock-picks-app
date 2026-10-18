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


def _window_stats(series, lo=None, hi=None) -> dict:
    import numpy as np
    s = series
    if lo is not None:
        s = s[[d >= lo for d in s.index]]
    if hi is not None:
        s = s[[d < hi for d in s.index]]
    r = s.values * TRADE_FRACTION / 100.0      # daily portfolio return
    if len(r) < 20 or float(np.std(r)) == 0:
        return {"days": int(len(r)), "sharpe": None, "mdd_pct": None}
    sharpe = float(np.mean(r) / np.std(r) * np.sqrt(252))
    eq = np.cumprod(1.0 + r)
    mdd = float((eq / np.maximum.accumulate(eq) - 1.0).min())
    return {"days": int(len(r)), "sharpe": round(sharpe, 3),
            "mdd_pct": round(100 * mdd, 2),
            "total_return_pct": round(100 * (eq[-1] - 1.0), 2)}


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
            "mdd_pct": round(100 * float((eq / eq.cummax() - 1).min()), 2)}


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolve", action="store_true",
                    help="run stage 1 and write the resolution artifact")
    ap.add_argument("--blend", action="store_true",
                    help="run stages 2+3 and write the portfolio evaluation")
    a = ap.parse_args()
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
