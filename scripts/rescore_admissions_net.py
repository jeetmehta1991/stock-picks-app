#!/usr/bin/env python
"""S6-B3122 (owner-approved 2026-09-29, "Approve all recs"): READ-ONLY
net-basis re-score of the admitted Phase-1B lines whose Step-2 reads of record
scored the cube's RAW pnl_pct (no cost, no winsor cap - L879 / #290 INSTANCE).

RULES OF THIS INSTRUMENT
- Results become LABELS on the admission rows. NO admission is changed here;
  any removal is a separate per-line owner ruling.
- STORED trades only, NO re-selection: each line's trade set is reproduced
  from its cube at the ADMITTED combination (recorded in
  phase_1b_step2_admissions.json), never re-searched.
- FAIL CLOSED per line (#290 reproduction gate): the RAW reconstruction must
  reproduce the admission-grid row's recorded holdout metrics (sharpe, ci_lo,
  psr, profit_factor, sortino within 1e-3; holdout_n and full_period_n EXACT)
  or the line is labelled NET-RESCORE-UNAVAILABLE with the mismatch, and no
  net number is published for it.
- The net basis is roster_core's basis of record (roster_core.py:181):
  pnl.clip(-WINSORIZE, WINSORIZE) - COST_BPS/100.
- Ops: where a row records gate_op it is used; where it does not (the pead
  offline rows), the op-set is SOLVED BY REPRODUCTION over {ge, le, eq} per
  axis - any op-set that reproduces every recorded metric and both trade
  counts defines the SAME trade set, which is the object being re-scored.
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if not (ROOT / "EXECUTION_QUEUE.md").is_file():          # L846 marker rule
    ROOT = Path(r"C:/Users/jeetm/Github/stock-picks-app")
    assert (ROOT / "EXECUTION_QUEUE.md").is_file(), "repo root not found"
sys.path.insert(0, str(ROOT / "scripts"))

import roster_core as rc                       # noqa: E402

ADMISSIONS = ROOT / "output_audit" / "phase_1b_step2_admissions.json"
OUT = ROOT / "output_audit" / "b3128_admissions_net_rescore.json"

R5_CUBE = ROOT / "output_r5_merged_1_7" / "trade_exit_detail.csv"
R5_TLOG = ROOT / "output_r5_merged_1_7" / "trade_log.csv"

METRIC_TOL = {"sharpe": 1e-3, "ci_lo": 1e-3, "profit_factor": 1e-3,
              "sortino": 1e-3, "psr": 1e-3}

# L849 (label vs key): an admission's `combination` records the CAMPAIGN'S
# PARAMETER names; the cube records SIGNAL keys. The pead offline campaign's
# parameters map onto persisted signal keys as below (MEASURED: 200 of 200
# sampled pead fires carry these keys). The op stays SOLVED BY REPRODUCTION -
# the map only names the column, never the direction.
PARAM_KEY_MAP = {
    "drift_window_days": "days_since_last_earnings",
    "yoy_growth_long_threshold": "earnings_eps_yoy_growth",
    "yoy_growth_threshold": "earnings_eps_yoy_growth",
    "announcement_return_threshold": "earnings_announcement_return",
}


def net(pnl: pd.Series) -> pd.Series:
    return pnl.clip(-rc.WINSORIZE, rc.WINSORIZE) - rc.COST_BPS / 100.0


def _parse_sig(s):
    import ast
    if isinstance(s, dict):
        return s
    try:
        return ast.literal_eval(s)
    except Exception:
        try:
            return json.loads(str(s).replace("'", '"')
                              .replace("True", "true").replace("False", "false")
                              .replace("None", "null"))
        except Exception:
            return {}


_FRAME_CACHE: dict[str, pd.DataFrame] = {}


def cube_frame(cube_dir: Path, strategy: str,
               sig_keys: list[str]) -> pd.DataFrame:
    """One cube's per-exit rows for one strategy, with the named signal
    magnitudes joined on (ticker, entry_date) - offline_level_sweep.load's
    join, reproduced (that module's axes carry ops; here ops are separate)."""
    ck = str(cube_dir) + "|" + strategy + "|" + ",".join(sorted(sig_keys))
    if ck in _FRAME_CACHE:
        return _FRAME_CACHE[ck]
    cube = pd.read_csv(cube_dir / "trade_exit_detail.csv", low_memory=False,
                       usecols=["ticker", "strategy", "entry_date", "direction",
                                "exit_method", "pnl_pct", "hold_days"])
    g = cube[cube.strategy == strategy].copy()
    if sig_keys:
        tl = pd.read_csv(cube_dir / "trade_log.csv", low_memory=False,
                         usecols=["ticker", "strategy", "entry_date",
                                  "signals_at_entry"])
        t = tl[tl.strategy == strategy].copy()
        sig = t["signals_at_entry"].map(_parse_sig)
        for k in sig_keys:
            t[k] = sig.map(lambda d, k=k: d.get(k) if isinstance(d, dict) else None)
        cols = ["ticker", "entry_date"] + sig_keys
        g = g.merge(t[cols].drop_duplicates(["ticker", "entry_date"]),
                    on=["ticker", "entry_date"], how="left")
    g["entry_date"] = pd.to_datetime(g["entry_date"], errors="coerce").dt.date
    _FRAME_CACHE[ck] = g
    return g


def r5_frame(strategy: str, sig_keys: list[str]) -> pd.DataFrame:
    return cube_frame(ROOT / "output_r5_merged_1_7", strategy, sig_keys)


def apply_ops(frame: pd.DataFrame, conds: list[tuple[str, str, float]]):
    m = pd.Series(True, index=frame.index)
    for key, op, level in conds:
        col = pd.to_numeric(frame[key], errors="coerce")
        if op == "ge":
            m &= col >= level
        elif op == "le":
            m &= col <= level
        else:
            m &= col == level
    return frame[m]


def score_both(sub: pd.DataFrame) -> dict:
    ho, is_ = rc.holdout(sub), rc.in_sample(sub)
    raw = rc.evaluate(ho["pnl_pct"], ho["hold_days"], min_n=15,
                      full_period_n=len(sub))
    nv = rc.evaluate(net(ho["pnl_pct"]), ho["hold_days"], min_n=15,
                     full_period_n=len(sub))
    is_raw = rc.evaluate(is_["pnl_pct"], is_["hold_days"], min_n=15,
                         full_period_n=len(sub))
    is_net = rc.evaluate(net(is_["pnl_pct"]), is_["hold_days"], min_n=15,
                         full_period_n=len(sub))
    return {"holdout_n": len(ho), "full_period_n": len(sub),
            "raw": raw, "net": nv, "is_raw": is_raw, "is_net": is_net}


def repro_ok(raw: dict, target: dict, ho_n: int, full_n: int):
    """The #290 gate: raw reconstruction == the recorded admission row."""
    bad = []
    if ho_n != int(target["holdout_n"]):
        bad.append(f"holdout_n {ho_n} != {target['holdout_n']}")
    if full_n != int(target["full_period_n"]):
        bad.append(f"full_period_n {full_n} != {target['full_period_n']}")
    if raw is None:
        bad.append("raw evaluate returned None (below floor)")
        return bad
    for k, tol in METRIC_TOL.items():
        want = target.get(k)
        got = raw.get(k)
        if want is None:
            continue
        if got is None or abs(float(got) - float(want)) > tol:
            bad.append(f"{k} {got} != {want}")
    return bad


def _explained(bad: list, rows) -> list:
    """S6-B3139h: a COUNT mismatch (holdout_n / full_period_n) carries the
    candidate rows' entry-window split, so the gap names its own make-up."""
    if any(b.startswith(("holdout_n ", "full_period_n ")) for b in bad):
        import free_level_window as _flw
        return bad + [_flw.window_note(rows)]
    return bad


def find_target(art: dict, adm: dict) -> dict | None:
    """The admission-grid row matching this admission's identity."""
    rows = art.get("results") or art.get("rows") or []
    combo = adm.get("combination") or {}
    strat = adm["strategy"]
    for r in rows:
        if r.get("strategy") not in (None, strat):
            continue
        if r.get("exit") != adm["exit"]:
            continue
        keys = {k: v for k, v in combo.items() if k not in ("strategy",)}
        if all(abs(float(r.get(k, float("nan"))) - float(v)) < 1e-9
               for k, v in keys.items() if k in r):
            # b3114 dialect: axis/op/level + holdout_sharpe/holdout_n/full_n
            if "axis" in r and "axis" in keys:
                if r["axis"] != combo["axis"]:
                    continue
            return r
    return None


def rescore_r5_line(adm: dict, art: dict) -> dict:
    return reproduce_r5_line(adm, art)[0]


def reproduce_r5_line(adm: dict, art: dict):
    """The r5 line reproduced (#290). Returns (result, sub): `sub` is the
    reproduced trade set when status is RESCORED, else None - the S6-B3134a
    eligibility re-score scores the SAME rows this function reproduced."""
    strat = adm["strategy"]
    combo = {k: v for k, v in (adm.get("combination") or {}).items()
             if k != "strategy"}
    target = find_target(art, adm)
    if target is None:
        return {"status": "NET-RESCORE-UNAVAILABLE",
                "reason": "admitted row not found in grid artifact"}, None
    tgt = {k: float(target[k]) for k in
           ("sharpe", "ci_lo", "psr", "profit_factor", "sortino")
           if target.get(k) is not None}
    tgt["holdout_n"] = target["holdout_n"]
    tgt["full_period_n"] = target["full_period_n"]

    keys = [PARAM_KEY_MAP.get(k, k) for k in combo.keys()]
    levels = [float(v) for v in combo.values()]
    frame = r5_frame(strat, keys)
    base = frame[frame["exit_method"] == adm["exit"]]

    rec_op = target.get("gate_op")
    op_space = ([tuple([rec_op] * len(keys))] if rec_op and rec_op != "none"
                else [()] if not keys
                else list(itertools.product(("ge", "le", "eq"), repeat=len(keys))))
    if not keys:
        op_space = [()]
    tried = []
    for ops in op_space:
        conds = [(k, o, lv) for k, o, lv in zip(keys, ops, levels)]
        sub = apply_ops(base, conds) if conds else base
        sc = score_both(sub)
        bad = _explained(repro_ok(sc["raw"], tgt, sc["holdout_n"],
                                  sc["full_period_n"]), sub)
        tried.append({"ops": list(ops), "mismatches": bad[:4],
                      "holdout_n": sc["holdout_n"]})
        if not bad:
            return {"status": "RESCORED", "ops": list(ops),
                    "reproduced": {k: tgt[k] for k in tgt}, **sc}, sub
    return {"status": "NET-RESCORE-UNAVAILABLE",
            "reason": "raw reproduction failed for every op-set (fail closed)",
            "attempts": tried}, None


def rescore_tws_line(adm: dict) -> dict:
    return reproduce_tws_line(adm)[0]


def reproduce_tws_line(adm: dict):
    """(result, sub) - see reproduce_r5_line. three_white_soldiers: the c14 Step-2 cube (depth_base None - the c14
    anatomy lives in the producer), breadth axis re-applied from the admitted
    identity, same loader as the r5 lines."""
    art = json.load(open(ROOT / adm["grid_artifact"], encoding="utf-8"))
    cube_dir = art.get("cube_dir")
    combo = adm["combination"]
    row = next((r for r in art.get("rows", [])
                if r.get("axis") == combo["axis"] and r.get("op") == combo["op"]
                and abs(float(r.get("level")) - float(combo["level"])) < 1e-9
                and r.get("exit") == adm["exit"]), None)
    if row is None:
        return {"status": "NET-RESCORE-UNAVAILABLE",
                "reason": "admitted cell not found in b3114 artifact"}, None
    tgt = {"sharpe": float(row["holdout_sharpe"]), "ci_lo": float(row["ci_lo"]),
           "psr": float(row["psr"]), "profit_factor": float(row["profit_factor"]),
           "sortino": float(row["sortino"]), "holdout_n": row["holdout_n"],
           "full_period_n": row["full_n"]}
    cdir = Path(cube_dir) if Path(cube_dir).is_absolute() else ROOT / cube_dir
    frame = cube_frame(cdir, adm["strategy"], [combo["axis"]])
    base = frame[frame["exit_method"] == adm["exit"]]
    sub = apply_ops(base, [(combo["axis"], combo["op"], float(combo["level"]))])
    sc = score_both(sub)
    bad = _explained(repro_ok(sc["raw"], tgt, sc["holdout_n"],
                              sc["full_period_n"]), sub)
    if bad:
        return {"status": "NET-RESCORE-UNAVAILABLE",
                "reason": "raw reproduction failed (fail closed)",
                "mismatches": bad}, None
    return {"status": "RESCORED", "ops": [combo["op"]],
            "reproduced": tgt, **sc}, sub


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None,
                    help="comma-separated strategies to re-run; other rows "
                         "are carried from the existing artifact unchanged")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None
    prior = {}
    if only and OUT.is_file():
        prior = {r["strategy"]: r
                 for r in json.load(open(OUT, encoding="utf-8"))["rows"]}
    doc = json.load(open(ADMISSIONS, encoding="utf-8"))
    out_rows = []
    for adm in doc["admissions"]:
        if only and adm["strategy"] not in only:
            assert adm["strategy"] in prior, adm["strategy"]
            out_rows.append(prior[adm["strategy"]])
            continue
        strat = adm["strategy"]
        if strat == "smc_breaker_block_long":
            out_rows.append({"strategy": strat, "status": "ALREADY-NET",
                             "reason": "Step-2 read of record ran through "
                                       "roster_core.load_cube (net basis)"})
            continue
        art = json.load(open(ROOT / adm["grid_artifact"], encoding="utf-8"))
        if strat == "three_white_soldiers":
            res = rescore_tws_line(adm)
        else:
            res = rescore_r5_line(adm, art)
        res = {"strategy": strat, "exit": adm["exit"],
               "combination": adm.get("combination"), **res}
        if res.get("status") == "RESCORED":
            for side in ("raw", "net", "is_raw", "is_net"):
                if res.get(side):
                    res[side] = {k: v for k, v in res[side].items()}
        out_rows.append(res)
        nv = res.get("net") or {}
        print(f"{strat:45s} {res['status']:24s} "
              f"raw_sh={((res.get('raw') or {}).get('sharpe'))} "
              f"net_sh={nv.get('sharpe')} net_all_gates={nv.get('all_live_gates')}")
    payload = {
        "_doc": ("B3128 (S6-B3122, owner-approved 2026-09-29): read-only "
                 "net-basis re-score of the admitted lines judged on raw "
                 "pnl_pct. Labels only; no admission changed; any removal is "
                 "a separate per-line owner ruling. Fail-closed #290 "
                 "reproduction gate: raw reconstruction must equal the "
                 "recorded admission row before any net figure is published."),
        "basis": ("net = pnl.clip(+/-%s) - %s/100 per roster_core.py:181"
                  % (rc.WINSORIZE, rc.COST_BPS)),
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rows": out_rows,
    }
    from roster_core import stamp_metric_code as _smc  # S6-B3139i
    _smc(payload)
    OUT.write_text(json.dumps(payload, indent=1, default=str) + "\n",
                   encoding="utf-8", newline="\n")
    n_res = sum(1 for r in out_rows if r["status"] == "RESCORED")
    n_un = sum(1 for r in out_rows if r["status"] == "NET-RESCORE-UNAVAILABLE")
    print(f"\n{n_res} RESCORED / {n_un} UNAVAILABLE / "
          f"{len(out_rows) - n_res - n_un} other -> {OUT.name}")
    return 0 if n_un == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
