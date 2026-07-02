#!/usr/bin/env python
"""Phase 1 deep-dive analysis TURN 2 (Council 235 owner-approved 2026-07-02).

Turn 2 scope: SILENT strategies 16-30 alphabetically.

Analysis method same as Turn 1: read strat_<name>() source, identify
fire-starving gate, cluster-assign, write bespoke notes + concrete
recommendation. Priority tagged HIGH / MED / LOW.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_2_ANALYSIS = {
    "cup_and_handle_long": {
        "cluster_id": "CHART_PATTERN_FAMILY",
        "owner_review_notes": (
            "5-gate stack (Batch 278 post-Stage-B v2 tightening): cup_handle_detected + "
            "price_above_ema_200 + vol_spike_2x + price_above_ema_50 + rsi_14 < 70. "
            "O'Neil CANSLIM canonical setup. Root cause is likely the "
            "cup_handle_detected producer signal being rare (chart pattern detection is "
            "inherently low fire count vs continuous indicators) COMPOUNDED with vol_spike_2x. "
            "Per Bulkowski 2005 double-bottom stats, chart pattern strategies fire 10-50/yr "
            "universe-wide; adding vol_spike_2x roughly halves that."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FIRST: verify detect_cup_and_handle in chart_patterns.py "
            "populates on canonical cases (AAPL 2020, MSFT 2019). If producer OK, LOOSEN "
            "vol_spike_2x -> vol_above_avg (O'Neil 1988 CANSLIM says 'above average volume', "
            "not 2x). Retain trend + RSI gates. Expected fire uplift: 3-5x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "death_cross_50_200_volume": {
        "cluster_id": "GOLDEN_DEATH_CROSS_FAMILY",
        "owner_review_notes": (
            "2-gate stack: ema_50_200_death_cross + vol_spike_2x + borrow_ok. STATUS "
            "POST-B772: EXPLORATORY per B660 measured 13.6/yr universe-wide = "
            "FAIL_FIRE_STARVED (87 total fires vs 100 min_trades_overall threshold). "
            "SHORT-side asymmetry per Pattern S adds further drag. Root cause: EVENT-cross "
            "AND EVENT-vol-spike compound gates the strategy into <100 fires."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_death_cross_50_200_wider_short: LOOSEN vol_spike_2x -> vol_above_avg "
            "OR drop vol gate entirely (B-3 baseline showed 504/yr without vol). Preserves "
            "structural bearish-shift thesis without compounding EVENT-scarcity. Expected "
            "fire uplift ~5-20x. NOTE Pattern S SHORT asymmetric expectancy caveat."
        ),
    },
    "double_bottom_long": {
        "cluster_id": "CHART_PATTERN_FAMILY",
        "owner_review_notes": (
            "4-gate stack (Batch 730 post-B710 tightening): double_bottom_detected + "
            "price_above_ema_200 + close_in_top_40pct_of_range + vol_spike_15x. "
            "vol_spike_15x is the fire-starving leg (15x average volume is extreme; "
            "Bulkowski 2005 stats reference vol confirmation but not 15x specifically). "
            "B710 W1 anti-fakeout gates were added because measured 7,510/yr LONG at "
            "state-flag rate; with 15x vol filter it drops well below viable."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_15x -> vol_spike_2x (Bulkowski 2005 canonical uses "
            "'above-average volume' not 15x). Retain other 3 gates. Expected fire uplift "
            "~5-10x. Note: reviewer's other B700 recommendations (ATR-clearance margin + "
            "second-bottom symmetry tolerance) require chart_patterns.py producer work; "
            "keep queued as separate ticket."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "dxy_headwind_multinational_short": {
        "cluster_id": "CROSS_ASSET_FAMILY",
        "owner_review_notes": (
            "In STRATEGIES_DISABLED_MISSING_PRODUCER per Batch 372: foreign_rev_pct "
            "producer absent. Strategy gates on foreign_rev_pct > 40.0 (Fratzscher 2009 "
            "JoB DXY translation risk hypothesis), but no producer computes this signal. "
            "Disabled at registration; expected 0 fires by design."
        ),
        "recommendation": (
            "STATUS QUO DISABLED: producer foreign_rev_pct missing. Re-enablement requires "
            "adding a foreign_rev_pct producer that reads 10-K/10-Q segment data (SEC EDGAR "
            "XBRL) or Polygon financials segment breakdown. Producer-side work; not a "
            "consumer-side gate loosening."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": "",
    },
    "flag_bull_long": {
        "cluster_id": "FLAG_PATTERN_FAMILY",
        "owner_review_notes": (
            "2-gate stack (Batch 618 post-phantom-breakout fix): flag_bull_broke + "
            "price_above_ema_200. Only 2 gates. Root cause is the underlying "
            "flag_bull_broke producer signal - the B618 rewrite requires flag COMPLETED "
            "1..8 bars ago AND today's close > flag_high. Two-time-window condition is "
            "the fire-starving element, not gate stacking."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify compute_flag_break_retest_signals in "
            "chart_patterns.py fires flag_bull_broke on canonical cases (AAPL 2023 Q4 "
            "flag). If producer OK, consider widening the K bar-window from 1..8 to "
            "1..15 (Edwards-Magee traditional 1-4 weeks). If producer broken, fix in "
            "chart_patterns.py. Expected fire uplift: 2-3x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "flag_bull_retest_long": {
        "cluster_id": "FLAG_PATTERN_FAMILY",
        "owner_review_notes": (
            "4-gate stack (Batch 607 post-BUG-111 F1 fix + B618 producer reframe): "
            "flag_bull_break_retest_long + [4-condition AND chain inside producer]. "
            "Producer encodes FLAG-COMPLETED + BREAKOUT-OCCURRED + RETEST + REVERSAL. "
            "Root cause: 4-condition compound event structure inside producer makes "
            "fires rare by design (retest itself is rare after breakout - many breakouts "
            "don't return to test)."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify compute_flag_break_retest_signals fires "
            "flag_bull_break_retest_long on canonical cases. If producer OK, consider "
            "widening retest-tolerance-band inside producer from tight (e.g., 1% from "
            "flag_high) to 2-3%. If producer broken, fix. Expected fire uplift: 2-4x. "
            "Producer-side work required, not consumer-side loosening."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "gold_silver_risk_off_long": {
        "cluster_id": "CROSS_ASSET_FAMILY",
        "owner_review_notes": (
            "2-gate stack: risk_off_regime_gold_signal + sector in {Utilities, Consumer "
            "Staples}. Hammoudeh-Yuan 2008 gold-silver ratio rising = risk-off. Root "
            "cause: (a) risk_off_regime_gold_signal is a RARE regime event, (b) universe "
            "restriction to 2 sectors (Utilities + Staples) further narrows target set. "
            "Batch A 2022-2026 window had extended bull run 2023-2024 = few risk-off "
            "days."
        ),
        "recommendation": (
            "LOOSEN: expand target sector set from {Utilities, Consumer Staples} to "
            "{Utilities, Consumer Staples, Health Care, Real Estate} (canonical defensive "
            "quartet per Fama-French). Retain gold-silver ratio gate (that IS the alpha "
            "hypothesis). Expected fire uplift: 2-3x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "golden_cross_volume": {
        "cluster_id": "GOLDEN_DEATH_CROSS_FAMILY",
        "owner_review_notes": (
            "2-gate stack: ema_50_200_golden_cross + vol_spike_2x (dual with death_cross "
            "for SHORT). STATUS POST-B772: EXPLORATORY per B660 measured 23.1/yr = "
            "FAIL_FIRE_STARVED (148 fires vs 100 min_trades_overall). EVENT-cross + "
            "EVENT-vol-spike compound gate. B-3 canonical golden_cross_50_200 fires "
            "504/yr WITHOUT vol gate; adding vol_spike_2x -> ~22x reduction."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_golden_cross_wider_long: DROP vol_spike_2x gate entirely (B-3 baseline "
            "shows 504/yr without it). OR LOOSEN to vol_above_avg. Preserves structural "
            "bullish-shift thesis (Faber 2013 canonical 50/200 EMA cross). Expected fire "
            "uplift ~22x (per B660 delta). Same pattern applies to companion death_cross."
        ),
    },
    "ichimoku_cloud_breakdown": {
        "cluster_id": "ICHIMOKU_FAMILY",
        "owner_review_notes": (
            "3-gate stack: ichi_below_cloud + ichi_tk_cross_dn + adx_trending. Ichimoku "
            "canonical structure - cloud break + TK cross + trending ADX. Root cause: "
            "Ichimoku signals require ALL 5 line-arrangements (Tenkan/Kijun/Senkou-A/B/"
            "Chikou) to align; TK cross DOWN below cloud is rare in aggregate. adx_trending "
            "(ADX > 25) compounds. Similar to how ichimoku_cloud_breakout showed 19,805 "
            "expected vs 4 actual - producer likely fires rarely on Batch A window."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FIRST: verify compute_ichimoku signals populate "
            "correctly on canonical cases (SPY 2022 Feb crash, TSLA 2023 Aug). If producer "
            "OK, LOOSEN by dropping adx_trending gate (Ichimoku already encodes trend via "
            "cloud). Retain ichi_below_cloud + ichi_tk_cross_dn. Expected fire uplift 3-5x. "
            "Also flagged: ichimoku_cloud_breakout counterpart LONG shows massive "
            "expected-vs-actual gap per Council 232 output - producer investigation is "
            "family-wide."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "institutional_oversold_long": {
        "cluster_id": "INSTITUTIONAL_13F_FAMILY",
        "owner_review_notes": (
            "3-gate stack: institutional_buy + rsi_14 < 35 + price_above_ema_200. "
            "Cohen-Malloy-Pomorski 2012 + Bondt-Thaler 1985 overreaction. Root cause: "
            "institutional_buy is a QUARTERLY 13F STATE signal per feedback_signal_"
            "temporality_event_vs_state - fires rarely at bar of quarterly filings. "
            "Combined with RSI<35 (~15% of bars) + EMA200 uptrend = 3-way scarce "
            "conjunction. Also STATE signal doesn't provide timing alpha per feedback."
        ),
        "recommendation": (
            "LOOSEN: rsi_14 < 35 -> rsi_14 < 45 (wider oversold band per Bondt-Thaler "
            "overreaction). Retain institutional_buy + EMA200 gates. Expected fire uplift "
            "2-4x. NOTE per feedback_signal_temporality: quarterly 13F is STATE not EVENT; "
            "cube verdicts should be interpreted with docstring correction that "
            "institutional_buy signals SPONSORSHIP not TIMING."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "institutional_persistence_volume_long": {
        "cluster_id": "INSTITUTIONAL_13F_FAMILY",
        "owner_review_notes": (
            "3-gate stack: institutional_increased >= 5 + vol_spike_2x + price_above_"
            "ema_50. Wave 3 Batch 337. Root cause: >=5 institutional funds increasing "
            "position is a RARE persistence event. Compound with vol_spike_2x = doubly "
            "rare. Same STATE-signal-temporality caveat as other institutional_* strategies."
        ),
        "recommendation": (
            "LOOSEN: institutional_increased >= 5 -> institutional_increased >= 3 "
            "(Cohen-Malloy-Pomorski 2012 threshold for 'cluster' is 3+ funds). Retain "
            "vol_spike_2x + EMA50. Expected fire uplift 2-3x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "institutional_recent_init_volume_long": {
        "cluster_id": "INSTITUTIONAL_13F_FAMILY",
        "owner_review_notes": (
            "3-gate stack: institutional_new_positions >= 2 + vol_spike_2x + "
            "price_above_ema_50. Wave 3 Batch 338. Lo-Wang 2000 volume-as-information. "
            "Root cause: new-position initiation is quarterly filing-scarce; vol_spike_2x "
            "concurrent with new position filing is doubly rare. Same STATE-timing caveat."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_2x -> vol_above_avg (Lo-Wang 2000 doesn't require 2x; "
            "any above-average volume confirms tape participation). Expected fire uplift "
            "2-3x. Also consider dropping vol gate entirely to preserve pure 'new institutional "
            "initiation + intermediate trend' thesis."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "institutional_volume_confirmation_long": {
        "cluster_id": "INSTITUTIONAL_13F_FAMILY",
        "owner_review_notes": (
            "3-gate stack: institutional_buy + vol_spike_2x + price_above_ema_50. Sias "
            "2004 JFE + Lo-Wang 2000 volume-as-information. Root cause: institutional_buy "
            "(quarterly STATE) + vol_spike_2x concurrent = quarterly-filing-rate coincidence "
            "with 2x vol day = rare."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_2x -> vol_above_avg (same as recent_init_volume). Expected "
            "fire uplift 2-3x. Or drop vol gate to compare pure institutional_buy + EMA50 "
            "thesis vs the 13F-only strategies for cube ablation."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "judas_swing_short": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "3-gate stack: smc_liquidity_swept_up + near_pivot + close_below_open. "
            "ICT Judas Swing (manipulation reversal). Root cause: smc_liquidity_swept_up "
            "is an ICT-library rare-event signal (requires specific stop-hunt pattern); "
            "compound with near_pivot narrows further. Producer investigation needed to "
            "confirm signal populates."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FIRST: verify smc_liquidity_swept_up populates via "
            "smartmoneyconcepts library. If producer OK, LOOSEN near_pivot to any-pivot-"
            "within-1-ATR OR drop close_below_open (redundant with 'short' direction). "
            "Expected fire uplift 2-3x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "keltner_lower": {
        "cluster_id": "MEAN_REVERSION_BAND_FAMILY",
        "owner_review_notes": (
            "3-gate stack: kc_touch_lower + hammer + obv_bullish (long); kc_touch_upper "
            "+ shooting_star + obv_bearish (short). Batch 628 F1 family-sweep for positive "
            "symmetric obv_bearish. Root cause: hammer / shooting_star candles are rare "
            "(1-3% of bars each); OBV directional gate compounds. Universe-agnostic mean-"
            "reversion setup that should work but tight candle requirement is fire-starving."
        ),
        "recommendation": (
            "LOOSEN: hammer -> (hammer OR bullish_engulfing OR bullish_pin_bar). Same "
            "widen for shooting_star -> (shooting_star OR bearish_engulfing OR bearish_"
            "pin_bar). Broader bullish-reversal / bearish-reversal candle families "
            "per Nison 1991. Expected fire uplift 3-5x. Retain OBV directional confluence "
            "per feedback_obv_avwap_macd_non_redundancy."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
}


def main() -> int:
    csv_path = Path("output_batch_A_150/phase_1_quiet_fire_investigation.csv")
    df = pd.read_csv(csv_path)

    for col in ("cluster_id", "owner_review_notes", "recommendation",
                "priority", "exploratory_loose_variant"):
        if col not in df.columns:
            df[col] = ""

    updated = 0
    for strat, data in TURN_2_ANALYSIS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found in CSV")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    df.to_csv(csv_path, index=False)
    print(f"Turn 2 complete: updated {updated} rows in {csv_path}")
    total_analyzed = (df["owner_review_notes"].fillna("").str.len() > 0).sum()
    print(f"Total analyzed cumulative: {total_analyzed} of {len(df)} ({100 * total_analyzed / len(df):.1f}%)")
    print()
    print("=== Turn 2 clusters ===")
    from collections import Counter
    print(Counter(d["cluster_id"] for d in TURN_2_ANALYSIS.values()))
    print()
    print("=== Turn 2 priorities ===")
    print(Counter(d["priority"] for d in TURN_2_ANALYSIS.values()))

    return 0


if __name__ == "__main__":
    sys.exit(main())
