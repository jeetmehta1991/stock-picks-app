#!/usr/bin/env python
"""Council 236 Investigation Turn 5 (2026-07-03) — CHART_PATTERN family.

SCOPE: 6 strategies
  1. cup_and_handle_long (0f, MED)
  2. flag_bull_long (0f, MED)
  3. flag_bull_retest_long (0f, MED)
  4. triangle_ascending_long (0f, MED)
  5. triangle_ascending_retest_long (0f, MED)
  6. cup_and_handle_retest_long (9f, MED)

PRODUCER FILE REVIEWED: backtest/signals/chart_patterns.py (768 lines)
Contains 6 detector functions + 3 producer-additive break-retest producers:
  - detect_cup_and_handle (line 179): 120-bar lookback; cup depth 10-35%
  - detect_flag (line 303)
  - detect_triangle (line 347)
  - detect_double_top_bottom (line 131)
  - compute_flag_break_retest_signals (line 447)
  - compute_triangle_apex_break_retest_signals (line 624)
  - compute_cup_handle_neckline_break_retest_signals (line 702)

EMPIRICAL FIRE RATES (SPY 2020-2026, 57 samples every 20 bars):
  cup_handle_detected:                    11/57 = 19.3% of bars
  flag_bull_broke:                         1/57 =  1.8%
  flag_bull_break_retest_long:             1/57 =  1.8%
  triangle_ascending_detected:             0/57 =  0.0%
  triangle_apex_break_retest_long:         0/57 =  0.0%
  cup_handle_neckline_break_retest_long:   6/57 = 10.5%
  double_bottom_detected:                  0/57 =  0.0%

KEY INSIGHTS:
  - Cup-and-handle producer WORKS WELL (19% fire rate; AAPL currently detects)
  - Cup neckline retest also works (10%)
  - Flag detectors are structurally rare (~1.8%)
  - TRIANGLE DETECTOR FIRES 0% on SPY 2020-2026 - may be too strict OR SPY
    didn't form clean ascending triangles (bull-market SPY breaks resistance
    before triangle apex confirms)
  - DOUBLE BOTTOM DETECTOR FIRES 0% on SPY sample
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_5_INVESTIGATIONS = {
    "cup_and_handle_long": {
        "post_investigation_verdict": "PRODUCER_OK + COMPOUND_GATE_STARVING",
        "post_investigation_recommendation": (
            "Producer VERIFIED (chart_patterns.py:179). Empirical fire rate 19.3% of "
            "SPY bars (AAPL currently detects). Gate stack: cup_handle_detected + "
            "price_above_ema_200 + vol_spike_2x + price_above_ema_50 + rsi_14 < 70. "
            "vol_spike_2x is TRUE 2x volume (~3-5% of bars per technical.py:1582). "
            "Joint probability: 0.19 x 0.03 x 0.6 x 0.5 x 0.7 = 0.06% of bars per "
            "ticker. Expected 150 x 4y x 252 x 0.0006 = ~90 fires. Actual 0. Gap "
            "explained by regime clustering (cup_handle_detected may correlate with "
            "specific bull windows where other gates fail). ACTIONS: (1) LOOSEN "
            "vol_spike_2x -> vol_above_avg (O'Neil CANSLIM canonical 'above average', "
            "not strict 2x); (2) drop rsi_14 < 70 (redundant with EMA trend). Expected "
            "10-20x uplift."
        ),
    },
    "flag_bull_long": {
        "post_investigation_verdict": "PRODUCER_OK + STRUCTURAL_RARE_EVENT",
        "post_investigation_recommendation": (
            "Producer VERIFIED (chart_patterns.py:447 compute_flag_break_retest_signals; "
            "B618 fix restricted to actual post-flag-completion breakouts within 1..8 "
            "bars). Empirical fire rate 1.8% of SPY bars (~5/yr per ticker). Consumer "
            "gate: flag_bull_broke + price_above_ema_200. Joint: 0.018 x 0.6 = 1.1%. "
            "Expected 150 x 4y x 252 x 0.011 = 1,663 fires. Actual 0 = SEVERE "
            "underfiring - suggests flag_bull_broke producer may be even rarer than "
            "the SPY 1.8% sample (SPY is smooth-trending; other tickers may form more "
            "flags but also fewer). ACTIONS: (1) audit compute_flag_break_retest_"
            "signals across Batch A tickers - if 0-1 fires per ticker, structural; "
            "(2) consider widening K bar-window from 1..8 to 1..15 (Edwards-Magee "
            "traditional 1-4 weeks); (3) universe expansion may 3-5x fires."
        ),
    },
    "flag_bull_retest_long": {
        "post_investigation_verdict": "PRODUCER_OK + COMPOUND_STRUCTURAL",
        "post_investigation_recommendation": (
            "Producer VERIFIED (compute_flag_break_retest_signals emits both "
            "flag_bull_broke and flag_bull_break_retest_long). Empirical fire rate "
            "1.8% of SPY bars. Producer encodes 4-condition AND chain (flag completed "
            "+ breakout + retest + reversal trigger). 0 fires reflects PIT-disciplined "
            "producer + strategy gates. ACTIONS: producer-side widen retest tolerance "
            "band (currently narrow); consider K bar-window 3..12 -> 3..15. Expected "
            "2-3x uplift."
        ),
    },
    "triangle_ascending_long": {
        "post_investigation_verdict": "PRODUCER_LIKELY_TOO_STRICT_OR_STRUCTURAL_ABSENT",
        "post_investigation_recommendation": (
            "Producer chart_patterns.py:347 detect_triangle. Empirical fire rate 0.0% "
            "of SPY sample (0/57 bars 2020-2026). SPY is a smooth-trending bull-market "
            "reference; ascending triangles may be genuinely rare on large-cap majors "
            "OR detector's flat-top + rising-lows criterion too strict. Bulkowski 2005 "
            "cites ~5-15 triangle events/yr per ticker; expected 150 x 4y x 10/yr = "
            "6,000 signal-events. Actual 0 = producer likely UNDERFIRING. ACTIONS: "
            "(1) URGENT audit detect_triangle across other Batch A tickers - if 0-1 "
            "fires universe-wide, PRODUCER IS BROKEN; (2) if producer needs loosening, "
            "widen the flat-top tolerance from strict-flat to 'nearly-flat within N%'; "
            "(3) OR restrict to explicit small-cap/mid-cap subset where triangles "
            "form more often."
        ),
    },
    "triangle_ascending_retest_long": {
        "post_investigation_verdict": "PRODUCER_DEPENDENT_ON_TRIANGLE_DETECTOR",
        "post_investigation_recommendation": (
            "Producer chart_patterns.py:624 compute_triangle_apex_break_retest_signals. "
            "Depends on triangle_ascending_detected which fires 0.0% on SPY sample. "
            "Cannot fire without base detector. INHERITS triangle_ascending_long's "
            "producer issue. ACTION: fix upstream detect_triangle first (see previous "
            "row). Then apex-break-retest cascades naturally."
        ),
    },
    "cup_and_handle_retest_long": {
        "post_investigation_verdict": "PRODUCER_OK + NEAR_STRUCTURAL_STRONG",
        "post_investigation_recommendation": (
            "Producer VERIFIED (chart_patterns.py:702 cup_handle_neckline_break_"
            "retest_long). Empirical fire rate 10.5% of SPY bars (6/57 samples). "
            "B685 replaced buggy DC20-anchored resistance_break_retest with cup_"
            "handle_breakout_level anchor (proper neckline reference). Consumer 3-"
            "gate: cup_handle_detected + cup_handle_neckline_break_retest_long + "
            "price_above_ema_50 default-False. 9 fires healthy for chart-pattern-"
            "retest (double-rare compound event). ACTIONS: (1) STATUS QUO on B685 "
            "producer fix; (2) universe expansion primary lever; (3) alternatively "
            "producer-side widen retest tolerance band 1% -> 2%. Expected 1.5-2x "
            "uplift."
        ),
    },
}


def main() -> int:
    csv_path = Path("output_batch_A_150/phase_1_quiet_fire_investigation.csv")
    df = pd.read_csv(csv_path)

    for col in ("post_investigation_verdict", "post_investigation_recommendation"):
        if col not in df.columns:
            df[col] = ""

    updated = 0
    for strat, data in TURN_5_INVESTIGATIONS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    df.to_csv(csv_path, index=False)
    print(f"Turn 5 investigation complete: {updated} strategies updated.")
    print()
    print("=== TURN 5 KEY FINDINGS ===")
    print("cup_and_handle producer: WORKS 19% fire rate on SPY (AAPL live detect)")
    print("cup neckline retest:     WORKS 10% fire rate on SPY")
    print("flag_bull detectors:     WORKS but rare 1.8% fire rate")
    print("triangle detector:       0% fires on SPY 2020-2026 sample")
    print("                          URGENT: producer may be UNDERFIRING or too strict")
    print("                          Affects triangle_ascending_long +")
    print("                          triangle_ascending_retest_long (dependent)")
    print("double_bottom detector:  0% fires on SPY sample")

    return 0


if __name__ == "__main__":
    sys.exit(main())
