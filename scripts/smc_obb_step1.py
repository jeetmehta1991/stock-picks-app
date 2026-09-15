#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} per CHECKLIST #77.
"""S6-B2752a: smc_order_block_bounce (hub 2) STEP-1 grader.

WHY THIS FILE IMPORTS ITS SIBLING'S BUILDER RATHER THAN COPYING IT. L799,
written the turn before this one, says a new helper starts without its
siblings' lessons - and the trigger it added is: if your output summarises a
population, grep for who else summarises that population BEFORE writing the
summary. smc_lsr_step1.build already carries the fail-closed path check, the
per-fire de-duplication and the bool->float coercion; a fresh copy would have
had to rediscover all three. So `build` was PARAMETERIZED (S6-B2752a) and this
grader calls it.

HUB-2'S GATE, read at screener.py:4693 not recalled:
    long  = smc_ob_bullish_tap_recent_5d AND rsi_14 < 45 AND price_above_ema_200
    short = smc_ob_bearish_tap_recent_5d AND rsi_14 > 55 AND below_ema_200
                                          AND NOT _short_borrow_trap_active

THE SEARCH IS ENTIRELY FREE - NO ENGINE TIME. MEASURED on the R5 cube
(output_r5_merged_1_7): rsi_14 is persisted on 1340 of 1340 fires, and its
values respect the gate per leg (long max 44.99, short min 55.04), so it is the
AT-ENTRY value. Tightening the ceiling (long) or raising the floor (short)
therefore keeps a strict SUBSET of the recorded fires and is gradable offline,
which is what Table A's P4/P5 free_band claims. This grader spends zero engine
hours; the producer knobs P1/P2 identify the CUBE and are not searched here.

  CELLS: the production base (both legs, 45/55) plus, per leg, that leg's
    Table A threshold band - 1 + 4 + 4 = 9 cells, each graded across all exits.
  GRADING: IS sharpe (min 10), rc.in_sample only - HOLDOUT UNTOUCHED.
  npt excluded from ranking.
  MULTIPLICITY: the threshold search is priced by a PERMUTATION NULL - rsi_14
    shuffled across fires within leg, so the null asks "how high a sharpe does
    an 8-level threshold search find when the threshold means nothing?"

DISCLOSED LIMIT, on the artifact's face rather than in a footnote: the gate's
PRIMARY key `smc_ob_*_tap_recent_5d` is NOT persisted in signals_at_entry -
MEASURED coverage 0.0000 over all 1340 fires, while the cube does persist the
superseded `smc_ob_*_active` STATE keys B2076 replaced. So every fire graded
here is one the engine already decided tapped an order block; this grader
cannot re-derive that decision and does not claim to (S6-B2752b).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import roster_core as rc  # noqa: E402
from breadth_step1_grid import BARRED_EXIT  # noqa: E402
from smc_lsr_step1 import build as _build  # noqa: E402

STRAT = "smc_order_block_bounce"
R5_DIR = ROOT / "output_r5_merged_1_7"
# Table A P4/P5 bands (producer_variant_table SPECS). Production first.
RSI_BANDS = {"long": [45, 40, 35, 30], "short": [55, 60, 65, 70]}
GATE_KEYS = ["rsi_14", "price_above_ema_200", "below_ema_200"]
# S6-B2810f (L801 applied): the baseline fire count is DERIVED from the
# committed pre-gate artifact, exactly as the sibling smc_lsr_step1 does -
# a hardcoded 1340 was a fixture naming a world-fact, and the lesson that
# says derive-at-runtime (B2801) landed the same day the constant did.
def _r5_baseline_fires() -> int:
    import json as _j
    pre = _j.loads((ROOT / "output_audit" / "b2690_smc_pregate.json")
                   .read_text(encoding="utf-8"))
    return int(pre["members"][STRAT]["n_trades"])


def _leg_mask(m: pd.DataFrame, leg: str, thr: float) -> pd.Series:
    """The subset a threshold keeps, in the direction the gate reads it.

    long tightens a CEILING (rsi below thr), short raises a FLOOR (rsi above).
    Production is the first band level, so the production cell is `thr` at its
    band head and the mask is then the identity on that leg.
    """
    d = m.direction == leg
    return d & ((m.rsi_14 < thr) if leg == "long" else (m.rsi_14 > thr))


def grade_cells(m: pd.DataFrame, min_n: int) -> list[dict]:
    rows: list[dict] = []

    def emit(tag, axis, level, sub):
        for ex, cell in sub.groupby("exit_method"):
            si = rc.in_sample(cell)
            r = rc._sharpe(si["pnl_pct"].values, si["hold_days"], min_n=min_n)
            if r is None:
                # B2775/#262: a cell that produced no gradable candidate is a
                # NON-OBSERVATION, and the partition needs it NAMED rather
                # than dropped - a row leaving the denominator silently is
                # the defect that report exists to stop.
                rows.append({"is_sharpe": None, "cell": tag, "axis": axis,
                             "level": level, "exit": ex, "is_n": int(len(si)),
                             "full_n_count_only": int(len(cell)),
                             "npt_barred": ex == BARRED_EXIT,
                             "verdict": "BELOW_POWER_FLOOR"})
                continue
            rows.append({"is_sharpe": r["sharpe"], "is_ci_lo": r.get("ci_lo"),
                         "cell": tag, "axis": axis, "level": level, "exit": ex,
                         "is_n": int(len(si)),
                         "full_n_count_only": int(len(cell)),
                         "npt_barred": ex == BARRED_EXIT})

    emit("base:both/production", None, None, m)
    for leg, band in RSI_BANDS.items():
        for thr in band:
            emit(f"rsi:{leg}/{thr}", f"rsi_threshold_{leg}", float(thr),
                 m[_leg_mask(m, leg, thr)])
    return rows


def threshold_null(m: pd.DataFrame, min_n: int, n_perms: int, seed: int) -> list:
    """Permutation null for the THRESHOLD search (SYNTHETIC maxima).

    rsi_14 is shuffled WITHIN leg, so each permutation preserves how many fires
    each threshold keeps and destroys only the association between the rsi
    value and the trade's outcome. The maximum over the 8 searched levels is
    recorded, which is the quantity the search actually selects on.
    """
    rng = np.random.default_rng(seed)
    IS = rc.in_sample(m)
    maxima = []
    for _ in range(n_perms):
        mm = IS.copy()
        for leg in RSI_BANDS:
            idx = mm.index[mm.direction == leg]
            if len(idx) > 1:
                mm.loc[idx, "rsi_14"] = rng.permutation(mm.loc[idx, "rsi_14"].values)
        best = None
        for leg, band in RSI_BANDS.items():
            for thr in band:
                sub = mm[_leg_mask(mm, leg, thr)]
                for _ex, cell in sub.groupby("exit_method"):
                    r = rc._sharpe(cell["pnl_pct"].values, cell["hold_days"],
                                   min_n=min_n)
                    if r and (best is None or r["sharpe"] > best):
                        best = r["sharpe"]
        maxima.append(best)
    return maxima


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--null-perms", type=int, default=100)
    ap.add_argument("--null-seed", type=int, default=13)
    ap.add_argument("--out", required=True)
    # the cube to grade, and this config's knob IDENTITY. P1/P2 are NOT
    # search axes here - they are baked into the cube by the engine run, so
    # they name the config rather than sweeping one (the S6-B2732a contract).
    ap.add_argument("--cube", default="",
                    help="cube DIRECTORY to grade; default the R5 baseline")
    ap.add_argument("--swing-length", type=int, default=None)
    ap.add_argument("--ob-close-mitigation", default=None)
    a = ap.parse_args()
    t0 = time.time()

    cube_dir = Path(a.cube).resolve() if a.cube else None
    if cube_dir is not None and cube_dir.is_file():
        cube_dir = cube_dir.parent
    is_r5 = cube_dir is None or cube_dir == R5_DIR.resolve()
    m = _build(None if is_r5 else cube_dir, strat=STRAT, keys=GATE_KEYS)
    fires = m.drop_duplicates(["ticker", "entry_date"])

    # S6-B2732a contract: the reproduction gate binds the BASELINE only. A
    # variant cube fires a DIFFERENT set by construction - changing a producer
    # knob is the whole point of the depth leg - so comparing it to the R5
    # count would refuse every config that did what it was asked. Recorded
    # either way; never silent.
    if is_r5:
        _want = _r5_baseline_fires()
        if len(fires) != _want:
            raise SystemExit(f"REFUSED: {len(fires)} unique fires != R5 "
                             f"baseline {_want} (fail closed)")
        repro = f"R5 BASELINE reproduction OK: {len(fires)} fires == {_want}"
    else:
        repro = ("VARIANT-CUBE-NO-R5-REPRODUCTION: this cube was produced at "
                 f"knobs swing_length={a.swing_length} "
                 f"ob_close_mitigation={a.ob_close_mitigation}, so its fire set "
                 f"DIFFERS from the R5 baseline by design; own fires {len(fires)}")
    print(f"{repro} ({time.time()-t0:.0f}s)")

    rows = grade_cells(m, a.min_n)
    graded = [r for r in rows if r["is_sharpe"] is not None]
    ranked = sorted((r for r in graded if not r["npt_barred"]),
                    key=lambda r: -r["is_sharpe"])
    print(f"{len(graded)} graded cells of {len(rows)} ({time.time()-t0:.0f}s)")

    pn = {}
    if a.null_perms > 0:
        best = max((r["is_sharpe"] for r in ranked
                    if str(r["cell"]).startswith("rsi:")), default=None)
        maxima = threshold_null(m, a.min_n, a.null_perms, a.null_seed)
        valid = [x for x in maxima if x is not None]
        p = ((1 + sum(1 for x in valid if x >= best)) / (len(valid) + 1)
             if (best is not None and valid) else None)
        pn = {"provenance": "SYNTHETIC - rng permutations of rsi_14 within leg; "
                            "prices the THRESHOLD search, never performance",
              "n_perms": a.null_perms, "seed": a.null_seed,
              "observed_threshold_best_is_sharpe": best,
              "null_max_quantiles": {str(q): round(float(np.quantile(valid, q)), 3)
                                     for q in (0.5, 0.9, 0.95, 0.99)} if valid else {},
              "p_value_best": round(p, 4) if p is not None else None}
        print(f"threshold null: best {best} vs q95 "
              f"{pn['null_max_quantiles'].get('0.95')} p {pn['p_value_best']} "
              f"({time.time()-t0:.0f}s)")

    rec = {"strategy": STRAT,
           # B2774/#309: an artifact names its CUBE and its GENERATOR, because
           # two JSONs about one cube look comparable and are not.
           "generator": "scripts/smc_obb_step1.py",
           "cube": str(cube_dir) if cube_dir else str(R5_DIR),
           "config": {"P1_swing_length": a.swing_length,
                      "P2_ob_close_mitigation": a.ob_close_mitigation},
           "reproduction": repro,
           "design": "1 production base + 8 threshold cells (per-leg Table A "
                     "bands); IS-only; holdout untouched; npt barred from "
                     "ranking; ZERO engine hours - every cell is a subset of "
                     "the recorded fires",
           "leg_a_limit": ("smc_ob_*_tap_recent_5d is NOT persisted in "
                           "signals_at_entry (MEASURED coverage 0.0000 over "
                           "1340 fires; the cube keeps the superseded "
                           "smc_ob_*_active STATE keys instead). Every fire "
                           "graded here is one the ENGINE decided tapped an "
                           "order block - this grader cannot re-derive that "
                           "and does not claim to (S6-B2752b)"),
           "reproduction_fires": int(len(fires)),
           "cells_graded": len(graded),
           "permutation_null": pn,
           # B2768/B2775: grid-stage BH-FDR as a COMPLETE PARTITION,
           # REPORT-ONLY - changes no gate and no ranking (B1608). The null is
           # handed in because this grader establishes significance that way.
           "multiplicity": rc.bh_fdr_report(rows, permutation_null=pn),
           "step1_ranking": ranked[:80], "rows": rows,
           "holdout_read": "NOT FIRED - Step 2 needs its own owner word (11.2c)"}
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
