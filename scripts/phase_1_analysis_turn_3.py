#!/usr/bin/env python
"""Phase 1 deep-dive analysis TURN 3 (Council 235 owner-approved 2026-07-02).

Turn 3 scope: SILENT strategies 31-45 alphabetically.
Same schema + depth as Turns 1-2.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_3_ANALYSIS = {
    "macd_bullish_with_smart_money_long": {
        "cluster_id": "SMART_MONEY_SLEEVE_FAMILY",
        "owner_review_notes": (
            "3-gate + smart_money union filter: macd_12_26_9_crossover_up + "
            "price_above_ema_200 + _has_smart_money_buy(s). B975 fixed the key-mismatch "
            "silent-gap ('macd_bullish_cross' -> 'macd_12_26_9_crossover_up'). "
            "_has_smart_money_buy is a UNION eligibility filter mixing EVENT (insider "
            "cluster, cfo_buy, large_dollar_buy) + STATE (13F institutional). Root cause: "
            "MACD crossover is a specific bar-of-fire event (~2-5/yr per ticker) AND "
            "coincidence with smart-money buy day is rare (union of multi-signal rarity)."
        ),
        "recommendation": (
            "LOOSEN: expand MACD gate to macd_12_26_9_bullish (state) OR keep crossover "
            "but drop smart_money AND requirement; move smart_money to secondary tier "
            "boost. Per feedback_signal_temporality: STATE smart-money should be "
            "SPONSORSHIP not TIMING. Expected fire uplift 3-5x. Producer-side note: "
            "_has_smart_money_buy is a UNION of 10+ components; if any component "
            "producers are broken (e.g., insider_cluster), the whole gate weakens."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "mfi_oversold_with_smart_money_long": {
        "cluster_id": "SMART_MONEY_SLEEVE_FAMILY",
        "owner_review_notes": (
            "3-gate + smart_money: mfi_oversold + price_above_ema_200 + "
            "_has_smart_money_buy(s). B975 fixed key-mismatch ('mfi_14_oversold' -> "
            "'mfi_oversold' since technical.py:1650 emits latter). Root cause: MFI < 20 "
            "is genuine oversold (~5-10% of bars) AND smart-money confluence AND EMA200 "
            "uptrend = 3-way scarce conjunction on top of STATE-timing miscredit issue."
        ),
        "recommendation": (
            "LOOSEN: expand mfi_oversold to (mfi_oversold OR mfi_14 < 30) - MFI < 30 is "
            "broader (~15% of bars) still oversold. Retain EMA200 + smart_money as "
            "confluence. Expected fire uplift 2-3x. Consider ablation: split into "
            "'mfi_oversold_pure_long' (no smart_money) to isolate smart_money contribution."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "news_momentum_long": {
        "cluster_id": "NEWS_SENTIMENT_FAMILY",
        "owner_review_notes": (
            "7-gate stack (Batch 603 walk): news_sentiment_5d >= +0.5 + news_volume_"
            "zscore_5d >= 1.5 + dc20_breakout_up + close_above_open + "
            "close_in_top_40pct_of_range + vol_above_avg + above_avwap_20low. Tetlock 2007 "
            "+ Da-Engelberg-Gao 2011 news-attention alpha. Root cause: news_sentiment_5d "
            ">= +0.5 is TOP QUARTILE-ISH sentiment (rare); news_volume_zscore >= 1.5 is "
            "unusual news volume (rare); Donchian breakout (rare); 4 other confirmation "
            "gates. 7-way AND with SPOF sentinel warning (B832) that Polygon sentiment "
            "field may be silently dropped for 100+ returns."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FIRST per B832 SPOF SENTINEL: verify Polygon sentiment "
            "field populates non-null in news_sentiment.py. If producer OK, LOOSEN: "
            "news_sentiment_5d >= +0.3 (moderate positive vs top-quartile) AND "
            "news_volume_zscore >= 1.0 (above-mean vs +1.5 stdev). Drop above_avwap_20low "
            "(redundant with dc20_breakout + strong close). Expected fire uplift 5-10x."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "news_momentum_short": {
        "cluster_id": "NEWS_SENTIMENT_FAMILY",
        "owner_review_notes": (
            "7-gate stack (mirror of news_momentum_long): news_sentiment_5d <= -0.5 + "
            "news_volume_zscore_5d >= 1.5 + dc20_breakdown_dn + close_below_open + "
            "close_in_bottom_40pct_of_range + vol_above_avg + NOT above_avwap_20high. "
            "Tetlock 2007 negative-tone stronger than positive. Same 7-way rarity + SPOF "
            "sentinel concerns as long variant. Pattern S SHORT asymmetric expectancy "
            "adds further drag."
        ),
        "recommendation": (
            "Same as news_momentum_long: producer investigation first (B832 SPOF); "
            "LOOSEN sentiment threshold to -0.3 + zscore to 1.0; drop AVWAP confluence. "
            "Retain candle + range + volume + Donchian. Expected fire uplift 5-10x. "
            "NOTE Pattern S SHORT asymmetric expectancy."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "news_reversal_long": {
        "cluster_id": "NEWS_SENTIMENT_FAMILY",
        "owner_review_notes": (
            "Multi-gate stack (Batch 614): sentiment <= -0.7 + pct_change_5d < -10% + "
            "news_count_5d >= 3 + news_sentiment_shift > +0.2 + close_above_open + "
            "close_in_top_40pct_of_range. Tetlock 2007 overreaction fade. Root cause: "
            "sentiment <= -0.7 is EXTREME negative (rare); -10% 5d move is rare crash; "
            "sentiment_shift +0.2 is turn-point (rare); 3-article threshold. Compound = "
            "very rare fires per year. Also SPOF sentinel."
        ),
        "recommendation": (
            "Producer investigation first (B832 SPOF for news_sentiment_shift populates). "
            "LOOSEN: sentiment <= -0.5 (still negative but broader) + pct_change_5d < "
            "-5% (broader crash zone) + retain shift/count/candle gates. Expected fire "
            "uplift 3-5x. Reversal event-driven strategy inherently produces low fire "
            "count; owner may accept LOW as intentional design."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "news_reversal_short": {
        "cluster_id": "NEWS_SENTIMENT_FAMILY",
        "owner_review_notes": (
            "Mirror of news_reversal_long: sentiment >= +0.7 + pct_change_5d > +10% + "
            "news_count_5d >= 3 + news_sentiment_shift < -0.2 + close_below_open + "
            "close_in_bottom_40pct_of_range. Same rarity + SPOF + Pattern S SHORT "
            "asymmetry as long variant."
        ),
        "recommendation": (
            "Same as news_reversal_long: producer check + loosen sentiment/pct_change "
            "thresholds. Expected fire uplift 3-5x. Pattern S SHORT asymmetric caveat."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "pivot_r2_continuation": {
        "cluster_id": "FLOOR_PIVOT_FAMILY",
        "owner_review_notes": (
            "11-gate stack (post-B879 reframe as daily-bar): pivot_R2 secondary breakout + "
            "AVWAP + 2x volume + EMA 50/200 trend + regime + candle + range confluence. "
            "Root cause: 11-signal joint probability. R2 breakouts alone are rare "
            "(~10-20/yr per ticker); adding vol_spike_2x + AVWAP + EMA50 + EMA200 + "
            "candle/range confluence gates compounds to sub-1/yr per ticker."
        ),
        "recommendation": (
            "LOOSEN: drop 3-4 confluence gates - specifically AVWAP defaults (per "
            "feedback_avwap_redundant_with_ema_trend_filter, redundant with EMA trend) + "
            "vol_spike_2x -> vol_above_avg (Bulkowski canonical). Retain pivot R2 + "
            "EMA200 + strong-close candle. 5-gate lean version. Expected fire uplift "
            "5-10x. NOTE: post-B879 the strategy is REFRAMED as 'daily-bar deep-"
            "resistance zone' not 'intraday-precision pivot' - lean version aligns with "
            "reframe."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "pivot_r3_blowoff_short": {
        "cluster_id": "FLOOR_PIVOT_FAMILY",
        "owner_review_notes": (
            "2-gate structure (Batch 645 Class 7 NEW mirror of B643-redesigned pivot_s3_"
            "capitulation): recent_blowoff_at_r3 + bearish-reversal trigger today "
            "(bearish_engulfing OR shooting_star OR below_prev_low). Wyckoff Buying Climax + "
            "Upthrust-Test. STATUS: EXPLORATORY POST-B652 (DO NOT DEPLOY until M10 "
            "cost-aware cube + S5-MULTIPLE-TESTING-CORRECTION ship). Pattern S SHORT "
            "asymmetric expectancy caveat. B643 measured 18.3/yr = FAIL_FIRE_STARVED."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_pivot_r3_blowoff_wider_short: LOOSEN bearish-reversal candle set to "
            "any bearish_reversal_family (add hanging_man, dark_cloud_cover, bearish_"
            "harami). Retain recent_blowoff_at_r3. Expected fire uplift 2-3x. Preserves "
            "Wyckoff blowoff-top thesis."
        ),
    },
    "pivot_s3_capitulation": {
        "cluster_id": "FLOOR_PIVOT_FAMILY",
        "owner_review_notes": (
            "2-gate structure (Batch 643 redesign per owner directive option C): "
            "recent_capitulation_at_s3 (5-bar window) + reversal trigger today "
            "(bullish_engulfing OR hammer OR above_prev_high). Wyckoff Spring/Test. B650 "
            "added vol_below_avg AND-required on reversal (LOW-volume Test bar). "
            "STATUS: EXPLORATORY POST-B652. Measured 18.3/yr FAIL_FIRE_STARVED per B643."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_pivot_s3_capitulation_wider_long: LOOSEN reversal-candle set to any "
            "bullish_reversal_family (add piercing_line, morning_star, bullish_harami) "
            "AND drop vol_below_avg AND-required (make it OR - relax LOW-volume Test bar "
            "canonical Wyckoff to any-Test bar). Preserves Spring/Test thesis. Expected "
            "fire uplift 3-5x."
        ),
    },
    "post_deletion_drift_short": {
        "cluster_id": "INDEX_REBALANCE_FAMILY",
        "owner_review_notes": (
            "Index-rebalance short (post-index-deletion drift). DEC-370/DEC-373 index-"
            "rebalance event-driven strategy. Requires ticker deletion event from S&P/Russell "
            "index_rebalance_events.parquet (Sprint 5 automation) + drift window "
            "gates. Root cause: index deletion events are ~10-30/yr universe-wide S&P + "
            "Russell combined; T1a batch A universe (150 stratified from ~1937 Master) may "
            "have 0-3 deletions across 4y window. Also Sprint 5 monthly automation may not "
            "populate historical events fully."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FIRST: verify index_rebalance_events.parquet is "
            "populated for 2022-2026 window with deletion events. If EMPTY, this strategy "
            "cannot fire regardless of gate loosening - producer-side dependency. "
            "If producer has events, this is inherently rare (deletion events "
            "structurally limited); accept LOW fire count as intentional. "
            "Pattern S SHORT asymmetric caveat."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "post_inclusion_drift_long": {
        "cluster_id": "INDEX_REBALANCE_FAMILY",
        "owner_review_notes": (
            "Mirror LONG of post_deletion_drift_short: post-index-inclusion drift. Same "
            "producer dependency (index_rebalance_events.parquet). Chen-Noronha-Singal "
            "2004 index inclusion price impact. Inclusion events are ~10-30/yr universe-"
            "wide; Batch A 150 tickers may have 0-3 inclusion events across 4y window."
        ),
        "recommendation": (
            "Same producer investigation as post_deletion_drift_short. If producer "
            "populated, accept LOW fires as structural. Universe-agnostic pattern - "
            "expanding to Batch B 1787 tickers may improve fire count 10-20x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "pre_fomc_quality_momentum_long": {
        "cluster_id": "EVENT_DRIVEN_MACRO_FAMILY",
        "owner_review_notes": (
            "3-gate stack (Batch 224): pre_fomc_d1 + xs_momentum_top_decile + "
            "price_above_ema_200. STATUS: EXPLORATORY -- DO NOT DEPLOY (B738 2026-06-12 "
            "owner-approved per B737 Decision 4 B1 verdict FAIL). Pre-FOMC timing "
            "component empirically DEAD per strat_pre_fomc_long_sleeve. Quality-momentum "
            "top-decile alone may still have edge but not tested here."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B. NOTE: pre_fomc_d1 gate is "
            "empirically dead per B737/B738; even loosening won't help if the timing "
            "component itself lacks alpha."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_quality_momentum_long: DROP pre_fomc_d1 gate entirely (dead per B738); "
            "retain xs_momentum_top_decile + EMA200 gates. Isolates quality-momentum "
            "selection (Goyal-Jegadeesh 2024) from FOMC timing. Effectively a NEW "
            "strategy testing whether cross-sectional momentum + trend confluence has "
            "edge without the empirically-dead FOMC leg."
        ),
    },
    "pre_rebalance_long": {
        "cluster_id": "INDEX_REBALANCE_FAMILY",
        "owner_review_notes": (
            "Pre-index-rebalance long (front-running expected inclusions). Requires "
            "pre-rebalance signal from index_rebalance_events.parquet ANNOUNCED-BUT-"
            "NOT-EFFECTIVE window (typically 5-10 days between announcement and "
            "effective date). Same producer dependency as post_inclusion/deletion. "
            "STATUS likely EXPLORATORY per event-driven scarcity."
        ),
        "recommendation": (
            "Same producer investigation as post_inclusion_drift_long. Pre-rebalance "
            "window is even narrower than post-inclusion (5-10 day window vs 30-90 day "
            "drift), so fires per year will be SMALLER than post_inclusion. Accept as "
            "structurally rare."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_pre_rebalance_wider_long: extend announced-not-effective window from "
            "5-10 days to 5-30 days (broader front-running zone). Preserves front-run "
            "thesis with more available fires. Expected fire uplift 2-3x."
        ),
    },
    "rsi21_slow": {
        "cluster_id": "RSI_MEAN_REVERSION_FAMILY",
        "owner_review_notes": (
            "Dual-direction mean-reversion: LONG = rsi_21 < 35 + price_above_sma_50; "
            "SHORT = rsi_21 > 65 + below_sma_50 + borrow_ok. B831 PATTERN S SHORT-SIDE "
            "ANNOTATION: dual strategy; LONG cube-authoritative, SHORT EXPLORATORY per "
            "STAGE_4_OSCILLATOR_MEAN_REVERSION_CLUSTER_WALKS Pattern S. LONG-side reasonably "
            "loose (rsi_21 < 35 + trend), so silent likely due to SHORT-side pull-down "
            "or B830 EXPLORATORY marker applied to the whole entry."
        ),
        "recommendation": (
            "LOOSEN LONG: rsi_21 < 35 -> rsi_21 < 40 (broader oversold, still meaningfully "
            "oversold vs neutral 50). Retain price_above_sma_50 trend. Keep SHORT as-is "
            "with Pattern S EXPLORATORY interpretation per B831 - don't delete a-priori. "
            "Expected fire uplift LONG side 2-3x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "rsi9_extreme": {
        "cluster_id": "RSI_MEAN_REVERSION_FAMILY",
        "owner_review_notes": (
            "3-gate LONG-only: rsi_9_extreme_os (RSI-9 < 20) + price_above_ema_200 + "
            "rsi_9_rising. RSI-9 < 20 is EXTREME oversold - rare event even in bear "
            "markets (~1-3/yr per ticker). rsi_9_rising confirms turn but compounds "
            "rarity. Universe-agnostic mean-reversion setup."
        ),
        "recommendation": (
            "LOOSEN: rsi_9_extreme_os (< 20) -> rsi_9 < 25 (still extreme, broader). "
            "Retain EMA200 + rsi_9_rising. Expected fire uplift 3-5x. NOTE: name is "
            "'extreme' - loosening beyond 25 dilutes the thesis. If fire count still "
            "below viable at RSI < 25, accept as structurally-limited."
        ),
        "priority": "MED",
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
    for strat, data in TURN_3_ANALYSIS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found in CSV")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    df.to_csv(csv_path, index=False)
    total_analyzed = (df["owner_review_notes"].fillna("").str.len() > 0).sum()
    print(f"Turn 3 complete: updated {updated}. Cumulative {total_analyzed} of {len(df)} ({100*total_analyzed/len(df):.1f}%)")

    from collections import Counter
    print(f"Turn 3 clusters: {Counter(d['cluster_id'] for d in TURN_3_ANALYSIS.values())}")
    print(f"Turn 3 priorities: {Counter(d['priority'] for d in TURN_3_ANALYSIS.values())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
