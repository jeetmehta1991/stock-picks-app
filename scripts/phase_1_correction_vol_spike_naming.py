#!/usr/bin/env python
"""Phase 1 CORRECTION: vol_spike_XX naming convention error (owner catch 2026-07-02).

Owner correction: 'vol_spike_17x - isnt its 70% more than average vs 17 times?'

Confirmed via backtest/signals/technical.py:1578-1583:
  vol_spike_12x = ratio >= 1.2   # 20% above average
  vol_spike_15x = ratio >= 1.5   # 50% above average
  vol_spike_17x = ratio >  1.7   # 70% above average
  vol_spike_2x  = ratio >= 2.0   # 100% above (actual 2x)
  vol_spike_3x  = ratio >= 3.0   # actual 3x
  vol_above_avg = ratio >= 1.0   # at or above average

The naming is MISLEADING - suffixes 12/15/17 are DECIMALS shifted, not multipliers.
Only 2x and 3x are true integer multiples.

This inverts the direction of all 13 recommendations that said:
  vol_spike_15x -> vol_spike_2x  (I called it 'loosening'; actually TIGHTENING 1.5x -> 2.0x)
  vol_spike_17x -> vol_spike_5x  (5x doesn't exist; and 5.0x > 1.7x = TIGHTENING)

CORRECT loosening direction:
  vol_spike_17x (1.7x) -> vol_spike_15x (1.5x) OR vol_above_avg (1.0x)
  vol_spike_15x (1.5x) -> vol_spike_12x (1.2x) OR vol_above_avg (1.0x)

This script rewrites the recommendation column for 13 affected strategies with
CORRECTED direction + prefixed with 'CORRECTED 2026-07-02'.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


CORRECTED_RECOMMENDATIONS = {
    "52w_low_breakdown": {
        "recommendation": (
            "CORRECTED 2026-07-02: vol_spike_17x is 1.7x avg (70% above), NOT 17x. "
            "LOOSEN: vol_spike_17x (1.7x) -> vol_spike_15x (1.5x) OR vol_above_avg "
            "(1.0x). 1.5x still captures institutional distribution while allowing "
            "normal capitulation days to fire. Retain other 4 gates. Expected fire "
            "uplift 2-4x depending on choice."
        ),
        "owner_review_notes_append": (
            " [CORRECTED 2026-07-02: 'vol_spike_17x is extreme' was wrong claim - "
            "actually 1.7x = 70% above avg, not 17x. Producer definition in "
            "technical.py:1581.]"
        ),
    },
    "avwap_20high_rejection_short": {
        "recommendation": (
            "CORRECTED 2026-07-02: vol_spike_15x is 1.5x avg, NOT 15x; vol_spike_5x "
            "does NOT EXIST (only 12/15/17/2/3 in producer). LOOSEN: vol_spike_15x "
            "(1.5x) -> vol_spike_12x (1.2x) OR vol_above_avg (1.0x) AND widen "
            "abs(pct_from_avwap) < 1% -> < 2%. Expected fire uplift 2-4x."
        ),
        "owner_review_notes_append": (
            " [CORRECTED 2026-07-02: vol_spike_15x is 1.5x avg not 15x; original "
            "'15x is extreme' was wrong.]"
        ),
    },
    "double_bottom_long": {
        "recommendation": (
            "CORRECTED 2026-07-02: vol_spike_15x is 1.5x avg (50% above), NOT 15x. "
            "vol_spike_2x (2.0x) is TIGHTER not looser. LOOSEN: vol_spike_15x (1.5x) "
            "-> vol_spike_12x (1.2x) OR vol_above_avg (1.0x). Bulkowski 2005 canonical "
            "'above-average volume' = vol_above_avg. Expected fire uplift 2-4x."
        ),
        "owner_review_notes_append": (
            " [CORRECTED 2026-07-02: vol_spike_15x is 1.5x not 15x.]"
        ),
    },
    "htf_aligned_breakout_long": {
        "recommendation": (
            "CORRECTED 2026-07-02: vol_spike_15x is 1.5x avg, NOT 15x. vol_spike_2x "
            "would TIGHTEN not loosen. LOOSEN: vol_spike_15x (1.5x) -> vol_above_avg "
            "(1.0x) per Shannon canonical 'above-average volume'. Retain above_prev_"
            "high + HTF alignment. Expected fire uplift 2-3x."
        ),
        "owner_review_notes_append": (
            " [CORRECTED 2026-07-02: vol_spike_15x is 1.5x not 15x.]"
        ),
    },
    "prev_day_high_break": {
        "recommendation": (
            "CORRECTED 2026-07-02: vol_spike_15x is 1.5x avg. LOOSEN: vol_spike_15x "
            "(1.5x) -> vol_spike_12x (1.2x) OR vol_above_avg (1.0x). Canonical says "
            "above-average not 1.5x. Expected fire uplift 1.5-3x."
        ),
        "owner_review_notes_append": (
            " [CORRECTED 2026-07-02: vol_spike_15x is 1.5x not 15x.]"
        ),
    },
    "htf_aligned_breakout_short": {
        "recommendation": (
            "CORRECTED 2026-07-02: vol_spike_15x is 1.5x avg. LOOSEN: vol_spike_15x "
            "(1.5x) -> vol_above_avg (1.0x) - symmetric to long variant corrected fix. "
            "Expected fire uplift 2-3x. Pattern S caveat."
        ),
        "owner_review_notes_append": (
            " [CORRECTED 2026-07-02: vol_spike_15x is 1.5x not 15x.]"
        ),
    },
    "roc_burst": {
        "recommendation": (
            "CORRECTED 2026-07-02: vol_spike_15x is 1.5x avg. LOOSEN: vol_spike_15x "
            "(1.5x) -> vol_spike_12x (1.2x) OR vol_above_avg (1.0x). Expected fire "
            "uplift 1.5-3x. Retain ROC-12 directional flip + borrow (SHORT)."
        ),
        "owner_review_notes_append": (
            " [CORRECTED 2026-07-02: vol_spike_15x is 1.5x not 15x.]"
        ),
    },
    "volume_spike_breakout": {
        "recommendation": (
            "CORRECTED 2026-07-02: vol_spike_15x is 1.5x avg (Batch 597c already "
            "loosened from vol_spike_2x=2.0x to vol_spike_15x=1.5x per its own "
            "docstring). Further LOOSEN: vol_spike_15x (1.5x) -> vol_above_avg (1.0x). "
            "Retain candle + range + AVWAP. Expected fire uplift 2-3x."
        ),
        "owner_review_notes_append": (
            " [CORRECTED 2026-07-02: vol_spike_15x is 1.5x not 15x; B597c already "
            "moved from 2x tighter to 1.5x looser - docstring makes this explicit.]"
        ),
    },
    "doji_at_resistance_short": {
        "recommendation": (
            "CORRECTED 2026-07-02: vol_spike_15x is 1.5x avg. LOOSEN: vol_spike_15x "
            "(1.5x) -> vol_spike_12x (1.2x) OR vol_above_avg (1.0x). Expected fire "
            "uplift 1.5-3x. Retain wide-pivot proximity + doji + borrow. Pattern S "
            "caveat."
        ),
        "owner_review_notes_append": (
            " [CORRECTED 2026-07-02: vol_spike_15x is 1.5x not 15x.]"
        ),
    },
    "donchian_breakdown_short": {
        "recommendation": (
            "CORRECTED 2026-07-02: vol_spike_15x is 1.5x avg. LOOSEN: vol_spike_15x "
            "(1.5x) -> vol_spike_12x (1.2x). Expected fire uplift 1.5-2x. Retain "
            "DC10 + MACD_bearish + borrow. Pattern S caveat."
        ),
        "owner_review_notes_append": (
            " [CORRECTED 2026-07-02: vol_spike_15x is 1.5x not 15x.]"
        ),
    },
    "prev_day_low_breakdown": {
        "recommendation": (
            "CORRECTED 2026-07-02: vol_spike_15x is 1.5x avg. LOOSEN: vol_spike_15x "
            "(1.5x) -> vol_spike_12x (1.2x) OR vol_above_avg (1.0x). Expected fire "
            "uplift 1.5-3x. Pattern S caveat."
        ),
        "owner_review_notes_append": (
            " [CORRECTED 2026-07-02: vol_spike_15x is 1.5x not 15x.]"
        ),
    },
    "doji_at_support": {
        "recommendation": (
            "CORRECTED 2026-07-02: vol_spike_15x is 1.5x avg. LOOSEN: vol_spike_15x "
            "(1.5x) -> vol_spike_12x (1.2x) OR vol_above_avg (1.0x). Expected fire "
            "uplift 1.5-3x. Retain doji + wide-pivot + support."
        ),
        "owner_review_notes_append": (
            " [CORRECTED 2026-07-02: vol_spike_15x is 1.5x not 15x.]"
        ),
    },
    "donchian_breakout_long": {
        "recommendation": (
            "CORRECTED 2026-07-02: vol_spike_15x is 1.5x avg. LOOSEN: vol_spike_15x "
            "(1.5x) -> vol_spike_12x (1.2x) OR vol_above_avg (1.0x). Expected fire "
            "uplift 1.5-3x. Retain other 4 gates."
        ),
        "owner_review_notes_append": (
            " [CORRECTED 2026-07-02: vol_spike_15x is 1.5x not 15x.]"
        ),
    },
}


def main() -> int:
    csv_path = Path("output_batch_A_150/phase_1_quiet_fire_investigation.csv")
    df = pd.read_csv(csv_path)

    updated = 0
    for strat, data in CORRECTED_RECOMMENDATIONS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found in CSV")
            continue

        # Rewrite recommendation
        df.loc[mask, "recommendation"] = data["recommendation"]
        # Append correction note to owner_review_notes
        current_notes = df.loc[mask, "owner_review_notes"].values[0]
        df.loc[mask, "owner_review_notes"] = current_notes + data["owner_review_notes_append"]
        updated += 1

    df.to_csv(csv_path, index=False)
    print(f"Correction applied: {updated} strategies fixed for vol_spike naming bug.")
    print()
    print("Signal ladder confirmed from technical.py:1568-1583 (loosest -> tightest):")
    print("  vol_below_avg  (<  1.0x)")
    print("  vol_above_avg  (>= 1.0x)")
    print("  vol_spike_12x  (>= 1.2x)  <- 20% above avg")
    print("  vol_spike_15x  (>= 1.5x)  <- 50% above avg")
    print("  vol_spike_17x  (>  1.7x)  <- 70% above avg")
    print("  vol_spike_2x   (>= 2.0x)  <- ACTUAL 2x (double)")
    print("  vol_spike_3x   (>= 3.0x)  <- ACTUAL 3x")
    print()
    print("NOTE: vol_spike_5x DOES NOT EXIST in producer.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
