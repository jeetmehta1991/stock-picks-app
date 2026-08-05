#!/usr/bin/env python
"""Council 236 fix (2026-07-03): add proper investigation columns to CSV.

Owner catch: 'Are these verdicts being tabulated in the csv in a new column?'
NO - I was overwriting the pre-investigation recommendation. Fixing now.

Actions:
1. Add 2 new columns: post_investigation_verdict + post_investigation_recommendation
2. RESTORE pre-investigation recommendation for 3 Ichimoku rows (retrieved
   from git commit bc391dd5e)
3. Move POST-INVESTIGATION text to new columns for those 3 rows
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


ICHIMOKU_RESTORE_AND_INVESTIGATE = {
    "ichimoku_cloud_breakout": {
        "recommendation": (
            "INVESTIGATE PRODUCER FAMILY-WIDE: Council 232 flagged massive gap. Verify "
            "compute_ichimoku emits ichi_above_cloud + weekly Kumo signals correctly. "
            "This is HIGHER priority than earlier due to expected-vs-actual delta. If "
            "producer OK, B657 tightening + 18.6% WR history suggest strategy has no "
            "edge - accept LOW or delete post-cube."
        ),
        "post_investigation_verdict": "BASELINE_STALE + PRODUCER_OK",
        "post_investigation_recommendation": (
            "Producer VERIFIED CORRECT (technical.py:962-1036) per B725 EVENT design "
            "(2026-06-12 owner-approved). Council 232's '19,805 expected' was PRE-B725 "
            "STATE-based baseline (11K/yr universe-wide). Post-B725 expected 655-954 "
            "fires (95% reduction per B655 precedent, scaled 150/503 x 4y). Actual 5 = "
            "still 130-190x gap. Contributing: (a) B657 strict weekly Kumo default=False "
            "affects first ~2 weeks; (b) T1a large-cap trends smoothly (few TURN events); "
            "(c) 4-way AND. ACTION: LOOSEN _recent_5d -> _recent_10d event window "
            "(producer-additive, symmetric to Turn 4 supertrend_ichimoku wider). "
            "Expected 2-3x uplift."
        ),
    },
    "ichimoku_cloud_breakdown": {
        "recommendation": (
            "INVESTIGATE PRODUCER FIRST: verify compute_ichimoku signals populate "
            "correctly on canonical cases (SPY 2022 Feb crash, TSLA 2023 Aug). If "
            "producer OK, LOOSEN by dropping adx_trending gate (Ichimoku already encodes "
            "trend via cloud). Retain ichi_below_cloud + ichi_tk_cross_dn. Expected fire "
            "uplift 3-5x. Also flagged: ichimoku_cloud_breakout counterpart LONG shows "
            "massive expected-vs-actual gap per Council 232 output - producer "
            "investigation is family-wide."
        ),
        "post_investigation_verdict": "STRATEGY_ASYMMETRY + PRODUCER_OK",
        "post_investigation_recommendation": (
            "Producer VERIFIED CORRECT (identical logic to LONG variant). STRATEGY-SIDE "
            "ASYMMETRY: LONG counterpart got B725 EVENT conversion; SHORT still uses "
            "STATE ichi_below_cloud. Producer emits ichi_below_cloud_break_recent_5d "
            "but strategy doesn't consume it. 0 fires suspicious given STATE below_cloud "
            "fires ~30-40% in bear regime. Likely _short_borrow_trap_active blocks most "
            "SHORT on T1a. ACTIONS: (a) apply B725 mirror EVENT-conversion to SHORT "
            "(code change, needs owner approval); (b) audit _short_borrow_trap_active "
            "blocking rate across ALL SHORT strategies. Pattern S caveat."
        ),
    },
    "ichimoku_tk_cross": {
        "recommendation": (
            "INVESTIGATE PRODUCER FIRST (family-wide): verify compute_ichimoku emits "
            "TK cross + cloud position on canonical cases. Council 232 showed "
            "ichimoku_cloud_breakout massive expected-vs-actual gap. If producer OK, "
            "this is structurally low-fire (TK crosses ~2/yr); accept 17 fires as "
            "reasonable for 4y x 150 tickers."
        ),
        "post_investigation_verdict": "PRODUCER_OK + LOOSEN_AVAILABLE",
        "post_investigation_recommendation": (
            "Producer VERIFIED CORRECT (technical.py:982-984). 2-gate simple structure. "
            "Underfiring 35-70x (17 actual vs 600-1200 expected). Root: strict same-bar "
            "TK cross EVENT + STATE cloud position. ACTION: extend TK cross to "
            "_recent_3d event window per williams_stoch_dual widening precedent "
            "(producer-additive). Alternative: drop cloud STATE gate (Ichimoku canonical "
            "uses TK cross as PRIMARY, cloud as CONFIRMATION only). Expected 2-3x uplift."
        ),
    },
}


def main() -> int:
    csv_path = Path("output_batch_A_150/phase_1_quiet_fire_investigation.csv")
    df = pd.read_csv(csv_path)

    # Add new columns if not present
    for col in ("post_investigation_verdict", "post_investigation_recommendation"):
        if col not in df.columns:
            df[col] = ""
            print(f"Added column: {col}")

    # Restore + populate Ichimoku rows
    for strat, data in ICHIMOKU_RESTORE_AND_INVESTIGATE.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found")
            continue
        df.loc[mask, "recommendation"] = data["recommendation"]  # restore original
        df.loc[mask, "post_investigation_verdict"] = data["post_investigation_verdict"]
        df.loc[mask, "post_investigation_recommendation"] = data["post_investigation_recommendation"]

    df.to_csv(csv_path, index=False)
    print(f"\nCSV updated. New column count: {len(df.columns)}")
    print(f"Ichimoku rows: original recommendation RESTORED; verdicts in new columns.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
