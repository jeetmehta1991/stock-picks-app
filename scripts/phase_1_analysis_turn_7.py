#!/usr/bin/env python
"""Phase 1 deep-dive analysis TURN 7 (Council 235 owner-approved 2026-07-02).

Turn 7 scope: STARVED strategies 31-45 by fire count (14-10 fires).
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_7_ANALYSIS = {
    "roc_burst": {
        "cluster_id": "MOMENTUM_OSCILLATOR_FAMILY",
        "owner_review_notes": (
            "14 fires. Dual: LONG = roc_turning_up + vol_spike_15x; SHORT = roc_turning_dn "
            "+ vol_spike_15x + borrow. Root cause: vol_spike_15x is the fire-starving leg "
            "(same as pattern flagged across many strategies); combined with ROC-12 "
            "directional flip (rare EVENT) = joint. Universe-agnostic momentum-onset "
            "setup."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_15x -> vol_spike_2x. Expected fire uplift 3-5x (14 -> 40-70, "
            "MARGINAL/VIABLE). Same fix pattern as htf_aligned_breakout, prev_day_high_"
            "break, double_bottom. Universe-agnostic high-value fix."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "smc_discount_long": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "14 fires. 3-gate: smc_in_discount_zone + (smc_bos_bullish OR smc_choch_"
            "bullish) + price_above_ema_200. Batch 216 ICT Premium/Discount discipline. "
            "Root cause: same smartmoneyconcepts producer dependency as smc_liquidity_"
            "sweep (Turn 6) + smc_bos_continuation (Turn 5). Family-wide producer "
            "investigation warranted."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FAMILY (per Turn 6 SMC family finding). Verify "
            "smc_in_discount_zone + smc_bos/choch_bullish populate on canonical cases. "
            "If OK, retain 3-gate as canonical ICT discipline; accept 14 fires as "
            "structural for T1a. Universe expansion may 2-3x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "smc_ote_long": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "14 fires. 2-gate: smc_ote_long_zone (Fib 62-79%) + (smc_bos_bullish OR "
            "smc_choch_bullish). Batch 216 canonical ICT OTE 'sweet spot' entry. Root "
            "cause: OTE zone requires specific Fib retracement (62-79% - narrow band) "
            "AFTER BOS/CHoCH confirmation - two rare producer events in sequence."
        ),
        "recommendation": (
            "Same as smc_discount_long: producer family investigation. If OK, retain "
            "as canonical ICT setup. LOOSEN Fib zone from 62-79% -> 50-79% (broader "
            "retracement zone captures Fib 50% golden ratio). Expected fire uplift "
            "1.5-2x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "xs_low_beta_long": {
        "cluster_id": "CROSS_SECTIONAL_FAMILY",
        "owner_review_notes": (
            "13 fires. Batch 220/358: Frazzini-Pedersen 2014 BAB + Blitz-van Vliet 2024. "
            "B358 REMOVED price_above_ema_200 regime gate (published BAB Sharpe is full-"
            "sample; ~30 trades in neutral regime showed -6.22% mean when EMA gate let "
            "through). Currently gates only on xs_low_beta_bottom_2_decile. Root cause: "
            "bottom-2-decile of beta cross-section is ~20% of universe per day; rebalancing "
            "cadence + T1a-only universe caps fires."
        ),
        "recommendation": (
            "INVESTIGATE UNIVERSE: bottom-2-decile of beta on T1a 503 S&P 500 (typically "
            "1.0+ market beta) will have relatively FEW low-beta names. Universe expansion "
            "to Batch B including sectors like Utilities/Staples/Real Estate (naturally "
            "low-beta) should lift fires 5-10x. Consumer-side gates minimal; producer "
            "OK per B358 cell audit."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "head_and_shoulders_top_short": {
        "cluster_id": "CHART_PATTERN_FAMILY",
        "owner_review_notes": (
            "12 fires. Batch 685 Class 7 NEW inverse mirror. STATUS: EXPLORATORY POST-B773 "
            "per B769 council F5 - NEVER cluster-walked + inherits chart-pattern repaint/"
            "phantom-breakout risk + Pattern S SHORT-side asymmetric expectancy. Producer "
            "= detect_head_and_shoulders in chart_patterns.py. Non-deletion marker per "
            "feedback_no_a_priori_strategy_pruning."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B. Chart-pattern repaint risk "
            "+ Pattern S SHORT asymmetry mean cube likely measures FAIL but useful for "
            "measurement."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_head_and_shoulders_top_wider_short: LOOSEN symmetry tolerance for "
            "shoulder heights (canonical 5-10% -> 15%). Also add producer PIT-anchor to "
            "prevent repaint. Expected fire uplift 1.5-2x. Preserves H&S top thesis with "
            "less strict pattern-detection."
        ),
    },
    "totm_long": {
        "cluster_id": "SEASONAL_CALENDAR_FAMILY",
        "owner_review_notes": (
            "12 fires. Batch 254 Ariel 1987 TOTM (last-4 + first-3 trading days). Batch "
            "723 STATE -> EVENT: is_totm_window_first_day (single bar entering window) "
            "post-B655 T10 + B721 precedent + S4-B717 ceiling routing. Root cause: EVENT "
            "TOTM fires ~12/yr per ticker (12 months x first-day). T1a 150 tickers x 4y = "
            "expected 4,800 fires theoretically but requires PIT-active + TOTM proximity "
            "producers. 12 fires suggests producer is firing correctly (~fires only on "
            "EVENT day)."
        ),
        "recommendation": (
            "STATUS QUO on B723 EVENT conversion (empirically justified per S4-B717 "
            "ceiling). Fire count matches expected TOTM cadence. Universe expansion "
            "(more tickers) is only lever for more fires. Accept as structural."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": "",
    },
    "macd_crossover_short": {
        "cluster_id": "MACD_MOMENTUM_FAMILY",
        "owner_review_notes": (
            "11 fires. Single-gate + borrow: macd_12_26_9_crossover_dn. Simple MACD "
            "bearish cross short-only strategy. Root cause: MACD 12/26/9 crossover_dn "
            "fires ~2-5/yr per ticker (bar-of-fire EVENT). 150 tickers x 4y = ~1,200-"
            "3,000 expected fires universe-wide. 11 actual suggests either producer "
            "underfires OR borrow_ok gate blocks most fires (small-cap stocks common in "
            "SHORT candidates)."
        ),
        "recommendation": (
            "INVESTIGATE: check macd_12_26_9_crossover_dn producer + borrow_ok gate. If "
            "producer OK, single-gate strategies inherently structurally rare on T1a. "
            "Pattern S SHORT asymmetric expectancy caveat. Universe expansion + borrow "
            "gate audit likely levers."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "smc_ote_short": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "11 fires. Symmetric mirror of smc_ote_long. Same producer dependency (Fib "
            "62-79% + BOS/CHoCH bearish). Pattern S SHORT asymmetric expectancy caveat."
        ),
        "recommendation": (
            "Same as smc_ote_long: producer family investigation + LOOSEN Fib zone to "
            "50-79%. Expected fire uplift 1.5-2x. Pattern S caveat."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "ultimate_oscillator": {
        "cluster_id": "OSCILLATOR_CONFLUENCE_FAMILY",
        "owner_review_notes": (
            "11 fires. Williams 1976 Ultimate Oscillator. Batch 206 Connors stack: (uo_"
            "oversold OR rsi_2 < 5) + 200-SMA regime gate. Phase 1A-beta showed UO best "
            "Sharpe (0.49) in oversold family but only 27 trades. Root cause: UO < 30 is "
            "genuine extreme oversold (~5% of bars); rsi_2 < 5 is very rare EVENT; OR "
            "combines them broadly but joint with 200-SMA still limits fires."
        ),
        "recommendation": (
            "LOOSEN: expand OR set - (uo_oversold OR rsi_2 < 5 OR rsi_14 < 30) - broader "
            "oversold family. Retain 200-SMA regime gate. Expected fire uplift 2-3x. "
            "STATUS QUO on 200-SMA (Connors discipline empirically justified)."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "xs_low_beta_with_smart_money_long": {
        "cluster_id": "SMART_MONEY_SLEEVE_FAMILY",
        "owner_review_notes": (
            "11 fires. 3-gate + smart_money: xs_low_beta_top_quintile + price_above_"
            "ema_200 + _has_smart_money_buy. Frazzini-Pedersen BAB + smart-money "
            "confluence. Root cause: low_beta top quintile on T1a (S&P 500 majority "
            "beta ~1) is inherently rare + smart_money union rarity + EMA200 = 3-way "
            "joint scarce. Same universe issue as xs_low_beta_long base version."
        ),
        "recommendation": (
            "Same universe finding as xs_low_beta_long: T1a S&P 500 has few natively "
            "low-beta names. Universe expansion is primary lever. NOTE: this variant "
            "gates on TOP quintile vs BASE's BOTTOM 2 deciles - inconsistent thresholds; "
            "audit and align."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "bullish_engulfing_support": {
        "cluster_id": "CANDLE_PATTERN_FAMILY",
        "owner_review_notes": (
            "10 fires. Dual: LONG = bullish_engulfing + (near_s1 OR near_s2 OR at_key_"
            "fib) + obv_bullish; SHORT = mirror + borrow. B628 F1 sweep for positive "
            "symmetric obv_bearish. Root cause: bullish/bearish_engulfing candles are "
            "1-3% of bars; pivot proximity narrows further; OBV directional gate "
            "compounds. Universe-agnostic mean-reversion at support."
        ),
        "recommendation": (
            "LOOSEN: widen candle set (bullish_engulfing OR piercing_line OR bullish_pin_"
            "bar OR morning_star) - broader bullish-reversal family per Nison 1991. "
            "Expected fire uplift 2-3x. Retain pivot proximity + OBV per feedback_obv_"
            "avwap_macd_non_redundancy."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "institutional_committed_growth_long": {
        "cluster_id": "INSTITUTIONAL_13F_FAMILY",
        "owner_review_notes": (
            "10 fires. Batch 344/333b: committed_growth_holders >= 5 (funds growing "
            ">10% share over 4 quarters) + price_above_ema_200. Distinct from Batch "
            "333's same-quarter increased proxy - requires multi-quarter committed "
            "GROWTH not just position increases. Reads from data_prefetch/derived/"
            "institutional_persistence_t1a/. Root cause: 4-quarter committed growth is "
            "structurally rare + 5-fund cluster threshold."
        ),
        "recommendation": (
            "LOOSEN: committed_growth_holders >= 5 -> >= 3 (Cohen-Malloy-Pomorski "
            "cluster canonical). Retain EMA200. Expected fire uplift 2-3x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "orb_stocks_in_play_short": {
        "cluster_id": "GAP_AND_GO_FAMILY",
        "owner_review_notes": (
            "10 fires. Batch 211 symmetric short mirror of orb_stocks_in_play_long. "
            "4-gate: gap_dn_2pct + close_below_open + vol_spike_2x + below_ema_200 + "
            "borrow. Same daily-bar ORB proxy for Zarattini-Barbon-Aziz 2024 5-min "
            "intraday. Pattern S SHORT asymmetric expectancy caveat."
        ),
        "recommendation": (
            "LOOSEN: gap_dn_2pct -> gap_dn_1_5pct (mirror of Turn 6 orb_long "
            "recommendation). Expected fire uplift 1.5-2x. Pattern S caveat."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "smc_premium_short": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "10 fires. Batch 216 symmetric mirror of smc_discount_long. 3-gate: smc_"
            "in_premium_zone + (smc_bos_bearish OR smc_choch_bearish) + below_ema_200 + "
            "borrow. Same smartmoneyconcepts producer dependency. Pattern S caveat."
        ),
        "recommendation": (
            "Same as smc_discount_long: producer family investigation. Accept as "
            "structural if producer OK. Pattern S caveat."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "volume_spike_breakout": {
        "cluster_id": "PRICE_ACTION_FAMILY",
        "owner_review_notes": (
            "10 fires. Batch 597 walk (a+c+d): close_above_open + close_in_top_40pct + "
            "vol_spike_15x (loosened from 2x per B597c) + above_avwap_20high (Shannon "
            "2022). Universe-agnostic breakout. Root cause: vol_spike_15x is fire-"
            "starving even after B597 loosening from 2x; AVWAP-from-20-high requires "
            "20-day swing high anchor + hold above."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_15x -> vol_spike_2x (same pattern as multiple other "
            "strategies flagged). Retain candle + range + AVWAP. Expected fire uplift "
            "3-5x. Universe-agnostic high-value fix."
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
    for strat, data in TURN_7_ANALYSIS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found in CSV")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    df.to_csv(csv_path, index=False)
    total_analyzed = (df["owner_review_notes"].fillna("").str.len() > 0).sum()
    starved_total = (df["class"] == "STARVED").sum()
    starved_analyzed = ((df["class"] == "STARVED") & (df["owner_review_notes"].fillna("").str.len() > 0)).sum()
    print(f"Turn 7 complete: updated {updated}. Cumulative {total_analyzed}/{len(df)} ({100*total_analyzed/len(df):.1f}%)")
    print(f"STARVED class: {starved_analyzed}/{starved_total}")

    from collections import Counter
    print(f"Turn 7 priorities: {Counter(d['priority'] for d in TURN_7_ANALYSIS.values())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
