#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} per CHECKLIST #77.
"""B2819 (S6-B2752): the SHARED Step-1 grader for smc strategies with NO free
numeric axis - the base cell (per leg) across all exits, IS-only.

WHY ONE FILE FOR TWO REGISTRATIONS. smc_equal_lows_sweep_long and
smc_inverse_fvg both gate on PERSISTED BOOLEANS only (measured against the
28-key persisted smc_* census: smc_equal_lows_swept, smc_fvg_bullish_active,
smc_inverse_fvg_bullish/bearish all persist), so neither has a threshold to
sweep offline - their Step-1 grid is legs x exits on the recorded fires, and
writing that twice would be the L799 failure the hub-2 batch already corrected
once. The strategy is an ARGUMENT (--strategy), exactly as offline_level_sweep
made the axis map an argument (R5 of the on-ramp: "a new strategy is a new
--axes, not a new script").

WHAT IS AND IS NOT SEARCHED. The producer knobs (P1 swing_length, P2
liquidity_range_pct, P3 event_recency_bars) identify the CUBE - they are baked
in by the engine run and recorded, never swept here (the S6-B2732a contract).
The offline axes are LEG (for a dual) and EXIT only. Multiplicity rides as the
mandatory report-only block (11.2b2d): with no numeric search there is no
permutation null to hand in, and the partition's scored_unpriced bucket says
so rather than claiming graded: 0 (S6-B2777 lineage).

Reproduction gate: R5 baseline fires must equal the committed pre-gate count
(b2690_smc_pregate.json members[<strategy>].n_trades - DERIVED, never a
constant, L801); a variant cube records VARIANT-CUBE-NO-R5-REPRODUCTION with
its own count (the L754 portability contract).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import roster_core as rc  # noqa: E402
from breadth_step1_grid import BARRED_EXIT  # noqa: E402
from smc_lsr_step1 import build as _build  # noqa: E402

R5_DIR = ROOT / "output_r5_merged_1_7"

# the two no-free-axis registrations this grader serves (S6-B2752). A dual
# strategy grades both legs plus the pooled cell; a single-leg only its own.
FAMILY = {
    "smc_equal_lows_sweep_long": {"legs": ("long",)},
    "smc_inverse_fvg": {"legs": ("long", "short")},
}


def _baseline_fires(strat: str) -> int:
    pre = json.loads((ROOT / "output_audit" / "b2690_smc_pregate.json")
                     .read_text(encoding="utf-8"))
    return int(pre["members"][strat]["n_trades"])


def grade_cells(m, strat: str, min_n: int) -> list:
    rows = []
    legs = FAMILY[strat]["legs"]

    def emit(tag, sub):
        for ex, cell in sub.groupby("exit_method"):
            si = rc.in_sample(cell)
            r = rc._sharpe(si["pnl_pct"].values, si["hold_days"], min_n=min_n)
            if r is None:
                # S6-B2777 lineage: a non-observation is NAMED, never dropped
                rows.append({"is_sharpe": None, "cell": tag, "exit": ex,
                             "is_n": int(len(si)),
                             "full_n_count_only": int(len(cell)),
                             "npt_barred": ex == BARRED_EXIT,
                             "verdict": "BELOW_POWER_FLOOR"})
                continue
            rows.append({"is_sharpe": r["sharpe"], "is_ci_lo": r.get("ci_lo"),
                         "cell": tag, "exit": ex, "is_n": int(len(si)),
                         "full_n_count_only": int(len(cell)),
                         "npt_barred": ex == BARRED_EXIT})

    if len(legs) > 1:
        emit("base:both", m)
    for leg in legs:
        emit(f"base:{leg}", m[m.direction == leg])
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", required=True, choices=sorted(FAMILY))
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cube", default="",
                    help="cube DIRECTORY to grade; default the R5 baseline")
    # knob IDENTITY - baked into the cube by the engine, recorded not swept
    ap.add_argument("--swing-length", type=int, default=None)
    ap.add_argument("--liquidity-range-pct", type=float, default=None)
    ap.add_argument("--event-recency-bars", type=int, default=None)
    a = ap.parse_args()
    t0 = time.time()
    strat = a.strategy

    cube_dir = Path(a.cube).resolve() if a.cube else None
    if cube_dir is not None and cube_dir.is_file():
        cube_dir = cube_dir.parent
    is_r5 = cube_dir is None or cube_dir == R5_DIR.resolve()
    m = _build(None if is_r5 else cube_dir, strat=strat, keys=[])
    fires = m.drop_duplicates(["ticker", "entry_date"])

    if is_r5:
        want = _baseline_fires(strat)
        if len(fires) != want:
            raise SystemExit(f"REFUSED: {len(fires)} unique fires != R5 "
                             f"baseline {want} (fail closed)")
        repro = f"R5 BASELINE reproduction OK: {len(fires)} fires == {want}"
    else:
        repro = ("VARIANT-CUBE-NO-R5-REPRODUCTION: produced at knobs "
                 f"swing_length={a.swing_length} "
                 f"liquidity_range_pct={a.liquidity_range_pct} "
                 f"event_recency_bars={a.event_recency_bars}; own fires "
                 f"{len(fires)}")
    print(f"{repro} ({time.time()-t0:.0f}s)")

    rows = grade_cells(m, strat, a.min_n)
    graded = [r for r in rows if r["is_sharpe"] is not None]
    ranked = sorted((r for r in graded if not r["npt_barred"]),
                    key=lambda r: -r["is_sharpe"])
    print(f"{len(graded)} graded cells of {len(rows)}")

    rec = {"strategy": strat,
           "generator": "scripts/smc_family_step1.py",
           "cube": str(cube_dir) if cube_dir else str(R5_DIR),
           "config": {"P1_swing_length": a.swing_length,
                      "P2_liquidity_range_pct": a.liquidity_range_pct,
                      "P3_event_recency_bars": a.event_recency_bars},
           "reproduction": repro,
           "design": ("base cell per leg x exits, IS-only; holdout untouched; "
                      "npt barred; NO free numeric axis - the gate is all "
                      "persisted booleans, so depth lives in the producer "
                      "knobs (engine) and breadth in 11.2b3"),
           "reproduction_fires": int(len(fires)),
           "cells_graded": len(graded),
           # 11.2b2d: mandatory, report-only. No numeric search here, so no
           # permutation null exists to hand in - the partition's
           # scored_unpriced bucket carries the graded rows honestly.
           "multiplicity": rc.bh_fdr_report(rows),
           "step1_ranking": ranked[:80], "rows": rows,
           "holdout_read": "NOT FIRED - Step 2 needs its own owner word (11.2c)"}
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
