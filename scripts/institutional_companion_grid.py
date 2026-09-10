#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} per CHECKLIST #77.
"""B2662 (owner directive 2026-09-10, verbatim: "some of these producers can be
added to the strategies to ensure sharpe lift and evaluate if the strategies
clear step 2 gates?" + the re-stated two asks + "Be thorough"): the FULL
institutional companion/knob grid, graded on the HOLDOUT under the owner's
admission doctrine (B2660: clearing all six live gates on the holdout is
phase-1B admissible; provenance labels travel as information).

WHAT IT DOES - for EVERY institutional strategy (all 20), for EVERY axis in
AXES (ask-1 knob axes: institutional_new_positions / institutional_increased;
ask-2 companion axes: momentum, anomaly, macro, sector-avoid, avwap), at
retention-derived levels, for all 26 exits:
  - filter the strategy's landed fires by the axis level (tightening only -
    subset-safe, zero engine hours),
  - grade IS sharpe AND the six live holdout gates (roster_core.evaluate),
  - record every line; every line clearing all six is ADMISSIBLE per the
    ruling and reported with the grid's full trials count on its face.

MULTIPLICITY IS DISCLOSED, NEVER HIDDEN: the artifact carries trials_total
and every qualifier row repeats it. Under a null, a grid this size clears
gates somewhere by luck; the owner's doctrine accepts holdout-clearing as
sufficient and the flag stands on record (B2660 queue row).

COVERAGE RULE per axis x strategy: an axis is skipped for a strategy when the
magnitude is present on < MIN_COVERAGE of its fires (the level would silently
drop the uncovered rows - the offline_level_sweep reproduction class); every
skip is recorded.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import roster_core as rc  # noqa: E402

CUBE = ROOT / "output_r5_merged_1_7" / "trade_exit_detail.csv"
TRADE_LOG = ROOT / "output_r5_merged_1_7" / "trade_log.csv"
FAMILY = "institutional_"
MIN_COVERAGE = 0.98
QUANTS = (0.2, 0.4, 0.6, 0.8)          # retention-derived levels per axis

# (key, direction) - ge keeps values >= level (tighten upward), le keeps <=.
AXES = [
    # ask 1 - the institutional producer knobs (persisted counts)
    ("institutional_new_positions", "ge"),
    ("institutional_increased", "ge"),
    # ask 2 - companions from the B2657 screen (momentum cluster: 2 reps)
    ("roc_12", "ge"),
    ("xs_max_anomaly", "ge"),
    ("cot_copper_commercials_net_pct", "ge"),
    ("sector_strongest_rs", "le"),      # AVOID the hottest sector
    ("pct_from_avwap_20low", "ge"),
]


def _parse(s):
    try:
        return json.loads(s)
    except Exception:
        try:
            return ast.literal_eval(s)
        except Exception:
            return {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()

    tl = pd.read_csv(TRADE_LOG, low_memory=False,
                     usecols=["strategy", "ticker", "entry_date", "signals_at_entry"])
    fam = tl[tl.strategy.str.startswith(FAMILY)].copy()
    sigs = [_parse(s) for s in fam["signals_at_entry"]]
    for key, _ in AXES:
        fam[key] = pd.to_numeric(pd.Series([d.get(key) for d in sigs]),
                                 errors="coerce").values
    fam = fam.drop(columns=["signals_at_entry"])
    print(f"fires {len(fam):,} across {fam.strategy.nunique()} strategies "
          f"({time.time()-t0:.0f}s)")

    cube = pd.read_csv(CUBE, low_memory=False,
                       usecols=["strategy", "ticker", "entry_date",
                                "exit_method", "pnl_pct", "hold_days"])
    cube = cube[cube.strategy.str.startswith(FAMILY)]
    m = cube.merge(fam, on=["strategy", "ticker", "entry_date"], how="left")
    m["entry_d"] = pd.to_datetime(m["entry_date"], errors="coerce").dt.date
    print(f"cube rows {len(m):,} joined ({time.time()-t0:.0f}s)")

    rows, skips = [], []
    trials = 0
    for strat, g in m.groupby("strategy"):
        base_fires = g.drop_duplicates(["ticker", "entry_date"])
        for key, op in AXES:
            vals = base_fires[key]
            cov = float(vals.notna().mean())
            if cov < MIN_COVERAGE:
                skips.append({"strategy": strat, "axis": key,
                              "coverage": round(cov, 3)})
                continue
            qs = vals.quantile(QUANTS).round(4).unique()
            levels = sorted(set(qs), reverse=(op == "le"))
            for lev in levels:
                mask = (g[key] >= lev) if op == "ge" else (g[key] <= lev)
                sub_all = g[mask & g[key].notna()]
                if sub_all.empty:
                    continue
                for ex, sub in sub_all.groupby("exit_method"):
                    trials += 1
                    is_slice = sub[sub.entry_d < rc.IS_START.__class__(2025, 5, 5)]
                    ho = sub[sub.entry_d >= rc.HO_START]
                    r = rc.evaluate(ho["pnl_pct"], ho["hold_days"], min_n=15,
                                    full_period_n=len(sub))
                    if r is None:
                        continue
                    is_r = rc._sharpe(is_slice["pnl_pct"].values,
                                      is_slice["hold_days"], min_n=10) \
                        if len(is_slice) >= 10 else None
                    rows.append({
                        "strategy": strat, "axis": key, "op": op,
                        "level": float(lev), "exit": ex,
                        "is_sharpe": is_r["sharpe"] if is_r else None,
                        "holdout_sharpe": r["sharpe"], "psr": r["psr"],
                        "profit_factor": r["profit_factor"],
                        "sortino": r["sortino"], "holdout_n": r["n"],
                        "full_n": int(len(sub)),
                        "n_gates": r["n_gates"],
                        "n_gates_evaluable": r["n_gates_evaluable"],
                        "all_live_gates": r["all_live_gates"]})
        print(f"  {strat} done ({time.time()-t0:.0f}s)")

    quals = [r for r in rows if r["all_live_gates"]]
    quals.sort(key=lambda r: -r["holdout_sharpe"])
    rec = {"family": FAMILY, "strategies": int(m.strategy.nunique()),
           "axes": [{"key": k, "op": o} for k, o in AXES],
           "quantile_levels": list(QUANTS), "min_coverage": MIN_COVERAGE,
           "trials_total": trials, "graded_lines": len(rows),
           "qualifiers_all_six_gates": len(quals),
           "doctrine": "owner ruling 2026-09-10 (B2660): all-six-holdout-gates "
                       "= admissible; selection provenance travels as a label; "
                       "every qualifier is a max-candidate from trials_total "
                       "trials - disclosed, per the standing flagged risk",
           "skipped_axis_strategy_pairs": skips,
           "qualifiers": quals, "rows": rows}
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")

    md = [f"# INSTITUTIONAL COMPANION/KNOB GRID - holdout-graded (B2662)",
          "",
          f"{rec['strategies']} strategies x {len(AXES)} axes x retention "
          f"levels x 26 exits = {trials:,} trials; {len(rows):,} lines above "
          f"the power floor; **{len(quals)} clear all six gates**. "
          f"{len(skips)} (axis, strategy) pairs skipped on coverage.",
          "",
          "| # | strategy | axis | level | exit | HO sharpe | psr | PF | HO n | full n |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for i, r2 in enumerate(quals[:30], 1):
        md.append(f"| {i} | {r2['strategy']} | {r2['axis']} {r2['op']} "
                  f"{r2['level']} | {r2['level']} | {r2['exit']} | "
                  f"{r2['holdout_sharpe']:.3f} | {r2['psr']} | "
                  f"{r2['profit_factor']} | {r2['holdout_n']} | {r2['full_n']} |")
    Path(a.out).with_suffix(".md").write_text("\n".join(md) + "\n",
                                              encoding="utf-8")
    print(f"\n{trials:,} trials | {len(rows):,} graded | {len(quals)} "
          f"qualifiers -> {a.out} ({time.time()-t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
