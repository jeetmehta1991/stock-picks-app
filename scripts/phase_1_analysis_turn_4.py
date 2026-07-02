#!/usr/bin/env python
"""Phase 1 deep-dive analysis TURN 4 (Council 235 owner-approved 2026-07-02).

Turn 4 scope: SILENT strategies 46-60 (FINAL SILENT batch - 60/60 complete).
Same schema + depth as Turns 1-3.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_4_ANALYSIS = {
    "rsi_overbought_short": {
        "cluster_id": "RSI_MEAN_REVERSION_FAMILY",
        "owner_review_notes": (
            "4-gate stack: rsi_14 > 68 + below_sma_50 + (bearish_engulfing OR NOT rsi_14"
            "_rising) + borrow_ok. STATUS: EXPLORATORY POST-B803 per B766/B768 Pattern S "
            "empirical validation showing 100% direction-asymmetry (LONG 7/7 EDGE_EXISTS "
            "vs SHORT 7/7 EDGE_NEGATIVE on 14 triggers). SHORT-side structural headwinds "
            "(drift + borrow + squeeze + STATE-form anti-edge). NON-DELETION marker per "
            "feedback_no_a_priori_strategy_pruning."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_rsi_overbought_wider_short: LOOSEN rsi_14 > 68 -> rsi_14 > 63 (still "
            "overbought, broader). Retain trend + candle + borrow gates. Expected fire "
            "uplift 2-3x. Pattern S SHORT asymmetric expectancy remains - cube likely "
            "measures FAIL_EDGE but useful for measurement per feedback_no_a_priori."
        ),
    },
    "rsi_oversold_with_smart_money_long": {
        "cluster_id": "SMART_MONEY_SLEEVE_FAMILY",
        "owner_review_notes": (
            "3-gate + smart_money union: rsi_14_oversold + price_above_ema_200 + "
            "_has_smart_money_buy(s). Same architecture as macd_bullish_with_smart_money "
            "+ mfi_oversold_with_smart_money analyzed Turn 3. Classic mean-reversion "
            "confluence but rsi_14 < 30 concurrent with smart-money buy event/state = "
            "3-way scarce conjunction. Same STATE-timing miscredit issue per feedback_"
            "signal_temporality."
        ),
        "recommendation": (
            "LOOSEN: rsi_14_oversold -> rsi_14 < 35 (broader oversold band per Bondt-"
            "Thaler overreaction). Retain EMA200 + smart_money. Expected fire uplift 2-"
            "3x. Also consider ablation: 'strat_rsi_oversold_pure_long' without smart_"
            "money AND to isolate smart_money contribution vs raw oversold."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "rsi_volume_200ema": {
        "cluster_id": "RSI_MEAN_REVERSION_FAMILY",
        "owner_review_notes": (
            "3-gate dual: LONG = rsi_14 < 35 + vol_above_avg + price_above_ema_200; "
            "SHORT = symmetric (RSI>65 + below_ema_200 + borrow). Batch 320 loosened "
            "vol_spike_2x -> vol_above_avg per owner directive (2x + RSI<35 was fire-"
            "starving). B831 Pattern S SHORT annotation: LONG 7/7 EDGE_EXISTS / SHORT "
            "7/7 EDGE_NEGATIVE. Currently 3 non-tight gates on LONG - silent likely due "
            "to Pattern S EXPLORATORY tag applied to whole entry."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B (SHORT-side). LONG-side "
            "should be firing at 3-gate config per B320 loosening; verify producer emits "
            "rsi_14_oversold + vol_above_avg reliably on Batch A cache."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_rsi_volume_200ema_wider_long: split into LONG-only strategy (per "
            "B831 recommendation), LOOSEN rsi_14 < 35 -> rsi_14 < 40. Split off from "
            "SHORT-side EXPLORATORY. LONG cube-authoritative per B768."
        ),
    },
    "sector_rotation_defensive_long": {
        "cluster_id": "CROSS_ASSET_FAMILY",
        "owner_review_notes": (
            "2-gate stack: defensive_leadership + sector in {Utilities, Consumer Staples, "
            "Health Care}. Conover-Jensen-Johnson-Mercer 2008 JoF defensive sector rotation. "
            "Root cause: defensive_leadership is a RARE regime state (XLU/XLP/XLV all "
            "leading XLY/XLK simultaneously is uncommon in bull markets). Batch A 2022-"
            "2026 window had extended bull 2023-2024 = few defensive-leadership days."
        ),
        "recommendation": (
            "LOOSEN: expand sector set to include Real Estate (defensive quartet). "
            "Consider loosening defensive_leadership to require ANY 2 of 3 defensive "
            "ETFs leading (vs all 3). Also expand to Financials-Utilities-Staples "
            "'staples-adjacent' broader defensive set. Expected fire uplift 2-3x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "short_borrow_trap_avoid": {
        "cluster_id": "META_AVOID_FAMILY",
        "owner_review_notes": (
            "This is an AVOID-side gate strategy, NOT an entry strategy. Batch 519 P15 "
            "sleeve. Blocks SHORT entries when days_to_cover > 8.0 (B671 tightened from "
            "5.0). By design it emits AVOID signals that centralized _strat() / _strat3() "
            "gate helpers consume - NOT a strategy that produces trade entries. 0 fires "
            "in trade log is EXPECTED because it's a filter, not an entry."
        ),
        "recommendation": (
            "STATUS QUO: this is a META-filter, not an entry strategy. Effectiveness "
            "measured by how many SHORT entries it blocks across other strategies "
            "(available in skipped_trades.csv). Not applicable to fire-count loosening. "
            "Consider re-classifying in ALL_STRATEGIES registration to make its META "
            "nature explicit (would eliminate confusion in future fire-count audits)."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": "",
    },
    "smc_mitigation_block_long": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "3-gate stack: smc_mitigation_block_long + price_above_ema_200 + rsi_14 < 50. "
            "Batch 216 SMC un-mitigated bullish Order Block entry. Root cause: smc_"
            "mitigation_block_long is a RARE ICT-library producer signal (requires "
            "un-mitigated bullish OB zone identified via smartmoneyconcepts library); "
            "compound with RSI < 50 (pullback context) narrows further."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FIRST: verify compute_smc_signals in smc_ict.py "
            "populates smc_mitigation_block_long non-zero on canonical cases. If producer "
            "OK, LOOSEN rsi_14 < 50 -> rsi_14 < 60 (broader pullback context - OB entry "
            "doesn't require strict oversold). Expected fire uplift 2-3x. Producer-side "
            "note: B416 silent-producer empty-return warning was emitted for smc_ict."
            "compute_smc_signals in launch_resume.log - investigate producer schema."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "squeeze_setup_long": {
        "cluster_id": "SQUEEZE_SETUP_FAMILY",
        "owner_review_notes": (
            "L1 (STATE eligibility) + L2 (EVENT trigger) 2-layer architecture per B615 "
            "reframe. L1: short_interest_pct + days_to_cover + institutional_buy (13F "
            "STATE eligibility, NOT bar-of-fire conviction). L2: news_sentiment_shift OR "
            "PEAD (event catalyst, B748d confirmed news producer works). Root cause: L1 "
            "state signals + L2 catalyst joint = ultra-rare (positioning + catalyst "
            "coincidence). Universe-mismatch caveat: high-short-interest names typically "
            "not in T1a S&P 500 majors; likely need T3 (momentum) or non-T1a for fires."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FIRST: L1 short_interest_pct + days_to_cover producers "
            "(FINRA bi-monthly) may not have full coverage across Batch A 150 stratified "
            "tickers. If producers OK, LOOSEN L2 to broader catalyst set (add earnings_"
            "surprise + analyst_upgrade). Universe expansion (Batch B / T3) more likely "
            "to help than gate loosening for this strategy. Expected fire uplift on wider "
            "universe: 5-10x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "supertrend_ichimoku_adx": {
        "cluster_id": "TREND_CONFLUENCE_FAMILY",
        "owner_review_notes": (
            "Symmetric LONG + SHORT per B779 owner directive 'want symmetric only' "
            "(supersedes B773 asymmetric): supertrend_flip_recent_5d + ichi_cloud_break_"
            "recent_5d + adx_strong. Post-B655 EVENT-conversion (from STATE supertrend_"
            "bullish to EVENT 5-bar flip window). Root cause: THREE 5-day EVENT windows "
            "simultaneously is doubly rare (each 5-day flip ~5-10% of bars; joint ~<1%). "
            "B660 measured 63/yr SHORT with ~10x reduction expected = ~6/yr SHORT. "
            "SHORT below min_trades=30/regime threshold."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B (SHORT-side per B779 "
            "expected)."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_supertrend_ichimoku_adx_wider: expand EVENT window from 5-day to "
            "10-day recent flip. Preserves EVENT-alpha vs STATE-anti-edge distinction "
            "while allowing more fires. Expected fire uplift 3-5x. Retain adx_strong "
            "STATE confirmation."
        ),
    },
    "triangle_ascending_long": {
        "cluster_id": "TRIANGLE_PATTERN_FAMILY",
        "owner_review_notes": (
            "2-gate stack: triangle_ascending_detected + price_above_ema_200. Batch 252 "
            "ascending triangle long (Bulkowski 2005 ~70% WR on confirmed breakouts). "
            "Root cause: triangle_ascending_detected is a producer-side rare event "
            "(chart pattern detection); compute_triangle_patterns in chart_patterns.py "
            "must identify flat top + rising lows to fire. Producer investigation "
            "warranted - pattern detection is inherently 5-30/yr per ticker."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FIRST: verify compute_triangle_patterns emits "
            "triangle_ascending_detected on canonical cases (AAPL 2020 pre-breakout, "
            "MSFT 2019). If producer OK, consumer-side is already minimal (2 gates); "
            "chart pattern strategies fire structurally-few. Accept LOW as intentional "
            "OR add supplementary strategies capturing similar setup (e.g., wedge, "
            "rectangle)."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "triangle_ascending_retest_long": {
        "cluster_id": "TRIANGLE_PATTERN_FAMILY",
        "owner_review_notes": (
            "3-gate stack (Batch 685 post-BUG-111 F1 fix per B683 self-critique): "
            "triangle_ascending_detected + triangle_apex_break_retest_long. B685 replaced "
            "buggy DC20-anchored resistance_break_retest with apex-anchored producer. "
            "Root cause: triangle detection AND breakout AND retest = triply rare (chart "
            "pattern -> break -> return-to-test). Bulkowski canonical entry but "
            "structurally scarce."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify compute_triangle_apex_break_retest_signals "
            "in chart_patterns.py fires on canonical cases. If producer OK, chart-"
            "pattern-retest strategies inherently rare; accept LOW. Producer-side "
            "loosening (widen retest-tolerance band 1% -> 2%) may help 2-3x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "triangle_descending_short": {
        "cluster_id": "TRIANGLE_PATTERN_FAMILY",
        "owner_review_notes": (
            "2-gate stack (Batch 685 Class 7 NEW mirror of triangle_ascending_long): "
            "triangle_descending_detected + price_below_ema_200 + borrow_ok. Bulkowski "
            "~64% WR on breakdowns. Same producer dependency. Pattern S SHORT asymmetric "
            "expectancy caveat."
        ),
        "recommendation": (
            "Same producer investigation as triangle_ascending_long. Accept LOW as "
            "intentional. NOTE Pattern S SHORT asymmetric expectancy - cube likely "
            "measures lower expectancy than mirror LONG."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "value_area_breakout_long": {
        "cluster_id": "VOLUME_PROFILE_FAMILY",
        "owner_review_notes": (
            "3-gate stack: vp_above_value_area + vol_spike_2x + price_above_ema_200. "
            "Batch 255 Dalton-Jones-Dalton 1990 Market Profile. Root cause: vp_above_"
            "value_area is a producer signal that requires computing Value Area (POC + "
            "70% volume range) from volume_profile.py. Compound with vol_spike_2x makes "
            "fires rare. B1035 confirmed volume_profile producers exist and emit non-"
            "zero values."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_2x -> vol_above_avg (Dalton 1990 canonical says 'increased "
            "volume' not 2x). Retain vp_above_value_area + EMA200. Expected fire uplift "
            "2-3x. Universe-agnostic pattern; should be a HIGH-priority fix but chart-"
            "pattern-like structural scarcity keeps at MED."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "weekly_bias_pullback_long": {
        "cluster_id": "MULTI_TIMEFRAME_FAMILY",
        "owner_review_notes": (
            "3-gate stack: weekly_bias_bull + rsi_14 < 40 + (hammer OR bullish_engulfing). "
            "Batch 217 multi-timeframe (weekly bias + daily pullback). Root cause: (a) "
            "hammer OR bullish_engulfing is a candle-specific event (~2-5% of bars each; "
            "~4-8% combined), (b) rsi_14 < 40 pullback (~15-20% of bars), (c) weekly_"
            "bias_bull filter narrows further. 3-way joint ~<1% of bars per ticker."
        ),
        "recommendation": (
            "LOOSEN: widen candle set (hammer OR bullish_engulfing OR bullish_pin_bar "
            "OR piercing_line OR morning_star) - broader bullish-reversal family per "
            "Nison 1991. Retain weekly_bias + RSI. Expected fire uplift 2-3x. Also "
            "consider: rsi_14 < 40 -> rsi_14 < 45 for broader pullback zone."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "weekly_bias_pullback_short": {
        "cluster_id": "MULTI_TIMEFRAME_FAMILY",
        "owner_review_notes": (
            "3-gate stack (symmetric mirror): weekly_bias_bear + rsi_14 > 60 + "
            "(shooting_star OR bearish_engulfing) + borrow_ok. Same architecture as long. "
            "Pattern S SHORT asymmetric expectancy caveat."
        ),
        "recommendation": (
            "Same as weekly_bias_pullback_long: widen bearish candle set (shooting_star "
            "OR bearish_engulfing OR bearish_pin_bar OR dark_cloud_cover OR evening_star) "
            "+ rsi_14 > 60 -> rsi_14 > 55. Expected fire uplift 2-3x. Pattern S "
            "asymmetric caveat."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "xs_combined_momentum_low_ivol": {
        "cluster_id": "CROSS_SECTIONAL_FAMILY",
        "owner_review_notes": (
            "3-gate stack: xs_momentum_top_decile + xs_avoid_high_ivol + price_above_"
            "ema_200. Asness-Moskowitz-Pedersen 2013 JF Value+Momentum Sharpe 1.4 "
            "combined. STATUS: EXPLORATORY POST-B787 per B786 #56 GATE FINAL verdict "
            "FAIL_FIRE_STARVED 0/yr under full B779+B781 config. xs_momentum_top_decile "
            "fires 43/yr universe-wide POST-B58e universe expansion; compound with "
            "xs_avoid_high_ivol drives joint to ~0."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_xs_combined_momentum_wider_long: LOOSEN xs_momentum_top_decile -> "
            "xs_momentum_top_quintile (top 20% vs top 10%). Retain low-IVOL confluence "
            "per Asness-Moskowitz thesis. Expected fire uplift 3-5x. Preserves core "
            "quality-momentum combination hypothesis with broader base."
        ),
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
    for strat, data in TURN_4_ANALYSIS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found in CSV")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    df.to_csv(csv_path, index=False)
    total_analyzed = (df["owner_review_notes"].fillna("").str.len() > 0).sum()
    silent_total = (df["class"] == "SILENT").sum()
    silent_analyzed = ((df["class"] == "SILENT") & (df["owner_review_notes"].fillna("").str.len() > 0)).sum()
    print(f"Turn 4 complete: updated {updated}. Cumulative {total_analyzed}/{len(df)} ({100*total_analyzed/len(df):.1f}%)")
    print(f"SILENT class: {silent_analyzed}/{silent_total} complete")

    from collections import Counter
    print(f"Turn 4 clusters: {Counter(d['cluster_id'] for d in TURN_4_ANALYSIS.values())}")
    print(f"Turn 4 priorities: {Counter(d['priority'] for d in TURN_4_ANALYSIS.values())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
