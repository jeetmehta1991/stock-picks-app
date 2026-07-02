#!/usr/bin/env python
"""Phase 1 deep-dive analysis TURN 10 (Council 235 owner-approved 2026-07-02).

Turn 10 scope: STARVED strategies 76-90 by fire count (4-1 fires).
Lowest-firing STARVED strategies.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_10_ANALYSIS = {
    "doji_at_support": {
        "cluster_id": "CANDLE_PATTERN_FAMILY",
        "owner_review_notes": (
            "4 fires. B574 narrow-scope: consumes _wide variants (1.5% band) exclusively. "
            "3-gate: doji + (near_s1_wide OR near_s2_wide OR at_key_fib_wide) + "
            "vol_spike_15x. Universe-agnostic support-reversal setup. vol_spike_15x is "
            "the fire-starving leg (same pattern as doji_at_resistance_short Turn 8 + "
            "13+ other strategies)."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_15x -> vol_spike_2x (16th strategy with same recurring "
            "fix). Expected fire uplift 3-5x. Retain doji + wide-pivot + support."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "head_and_shoulders_bottom_long": {
        "cluster_id": "CHART_PATTERN_FAMILY",
        "owner_review_notes": (
            "4 fires. Batch 252 inverse H&S long. STATUS POST-B732: EXPLORATORY DO NOT "
            "DEPLOY per Decision 2 Group C #11. B699 audit verdict: MISS on textbook "
            "synthetic geometry (detection too strict OR real fire-starvation). Bulkowski "
            "2005 cites ~5-15/yr per ticker = sub-min_trades by design. Same disposition "
            "as CP-1 cup_and_handle_long (Turn 1)."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_head_and_shoulders_bottom_wider_long: LOOSEN shoulder-height symmetry "
            "tolerance (canonical 5-10% -> 15%) + widen neckline break tolerance (1% -> "
            "2%). Preserves H&S bottom thesis with less strict geometry. Expected fire "
            "uplift 2-3x."
        ),
    },
    "insider_cluster_long": {
        "cluster_id": "INSIDER_FORM4_FAMILY",
        "owner_review_notes": (
            "4 fires. Batch 222: insider_cluster_active (>=2 unique insiders + open-"
            "market buys + last 30d) + price_above_ema_200. Cohen-Malloy-Pomorski 2012 + "
            "Akbas-Jiang-Koch 2024. Root cause: insider clusters are structurally rare "
            "on T1a large-caps (Cohen-Malloy 2012 documented alpha on all-caps universe; "
            "large-caps have LESS insider activity than mid/small caps). Batch A T1a "
            "150 tickers = expected 5-20 clusters/yr. 4 fires low but not extreme."
        ),
        "recommendation": (
            "UNIVERSE EXPANSION primary lever: Cohen-Malloy 2012 documented alpha across "
            "all market cap; T1a filters out mid/small caps where insider clustering is "
            "more common. Batch B (Master 1937) or T3 (momentum non-T1a) would 3-5x "
            "fires. Consumer-side gates minimal."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "institutional_with_directors_long": {
        "cluster_id": "INSTITUTIONAL_INSIDER_COMBO_FAMILY",
        "owner_review_notes": (
            "4 fires. Wave 3 Batch 336: institutional_buy (13F STATE) + insider_director_"
            "buyers_30d >= 1 + EMA200. Akbas-Jiang-Koch 2024 director-premium + Cohen-"
            "Frazzini-Malloy institutional. Root cause: 13F STATE + insider EVENT + "
            "trend = 3-way scarce joint. Director-only threshold is narrow (director "
            "trades are subset of insider trades; ~30-40% of insider volume)."
        ),
        "recommendation": (
            "LOOSEN: insider_director_buyers_30d >= 1 -> insider_buyers_30d >= 1 "
            "(broader insider set - includes officers + 10% owners). Preserves "
            "institutional_buy + insider composite thesis. Expected fire uplift 3-4x. "
            "Retain director premium as secondary tier if desired."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "parabolic_sar_flip_short": {
        "cluster_id": "TREND_FAMILY",
        "owner_review_notes": (
            "4 fires. 2-gate: psar_flip_dn + adx_trending + borrow. Parabolic SAR flip "
            "is a specific EVENT (~5-10/yr per ticker on daily bars). adx_trending "
            "(ADX > 25) filters ~30% of bars. Compound = specific. Universe-agnostic. "
            "Pattern S SHORT asymmetric expectancy caveat."
        ),
        "recommendation": (
            "LOOSEN: drop adx_trending gate (PSAR flip IS a trend-change signal - "
            "redundant with ADX confirmation). Retain psar_flip_dn + borrow. Expected "
            "fire uplift 2-3x. Pattern S caveat. Similar redundancy pattern as "
            "feedback_avwap_redundant_with_ema_trend_filter."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "flag_bear_retest_short": {
        "cluster_id": "FLAG_PATTERN_FAMILY",
        "owner_review_notes": (
            "3 fires. Batch 607 Class 7 NEW symmetric mirror of flag_bull_retest_long. "
            "4-gate: flag_bear_break_retest_short + below_ema_200 + close_below_open + "
            "vol_below_avg + borrow. Same producer dependency as flag_bull_retest (Turn "
            "2) + Pattern S SHORT asymmetric expectancy caveat."
        ),
        "recommendation": (
            "Same producer investigation as flag_bull_retest_long: verify compute_flag_"
            "break_retest_signals emits flag_bear_break_retest_short on canonical cases. "
            "If OK, retest strategies structurally rare. Producer-side widening. "
            "Pattern S caveat."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "shooting_star_short": {
        "cluster_id": "CANDLE_PATTERN_FAMILY",
        "owner_review_notes": (
            "3 fires. 3-gate: shooting_star + (near_r1 OR near_r2 OR bb_20_20_touch_"
            "upper) + rsi_14 > 65 + borrow. Nison canonical bearish reversal at "
            "resistance. Root cause: shooting_star ~2-3% of bars + resistance proximity "
            "+ RSI overbought = 3-way scarce joint. Pattern S SHORT asymmetric "
            "expectancy caveat."
        ),
        "recommendation": (
            "LOOSEN: widen candle set to (shooting_star OR bearish_pin_bar OR "
            "hanging_man OR dark_cloud_cover) - broader bearish-reversal family per "
            "Nison 1991. Expected fire uplift 2-3x. Pattern S caveat. Same widening "
            "pattern as keltner_lower (Turn 2 HIGH) + weekly_bias_pullback (Turn 4)."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "adx_initiation": {
        "cluster_id": "TREND_FAMILY",
        "owner_review_notes": (
            "2 fires. Dual: LONG = adx_cross_up + adx_di_bull; SHORT = adx_cross_up + "
            "adx_di_bear + borrow. B634 positive-symmetric adx_di_bear sweep. Root "
            "cause: adx_cross_up (ADX crossing above 25) is a specific EVENT (~2-5/yr "
            "per ticker); combined with DI direction filter. Universe-agnostic trend-"
            "initiation setup."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify adx_cross_up + adx_di_bull/bear producers fire "
            "on canonical trend-initiation days. If OK, LOOSEN adx_cross_up threshold "
            "(above 25 -> above 20 - still trending but earlier entry). Expected fire "
            "uplift 3-5x. Universe-agnostic pattern."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "bollinger_upper_short": {
        "cluster_id": "BOLLINGER_MEAN_REVERSION_FAMILY",
        "owner_review_notes": (
            "2 fires. STATUS: EXPLORATORY POST-B803 per B766 council #51 + B768 Pattern "
            "S 100% direction-asymmetry (SHORT mean-reversion structurally headwinded). "
            "3-gate: bb_20_20_touch_upper + rsi_14 > 70 + shooting_star + borrow. "
            "Explicitly separated from bollinger_lower's SHORT branch which got its own "
            "EVENT conversion. Pattern S caveat + rare candle event compounds."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B. Pattern S structural "
            "headwind makes SHORT mean-reversion FAIL-expected."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_bollinger_upper_wider_short: widen candle set (shooting_star OR "
            "bearish_engulfing OR hanging_man). Retain BB touch + RSI overbought + "
            "borrow. Expected fire uplift 2-3x. Pattern S FAIL-expected."
        ),
    },
    "donchian_breakout_long": {
        "cluster_id": "DONCHIAN_FAMILY",
        "owner_review_notes": (
            "2 fires. Batch 591 Class 7 NEW tight long-only mirror of donchian_"
            "breakdown_short. 5-gate: dc10_breakout_up + vol_spike_15x + macd_12_26_9_"
            "bullish + close_above_open + close_in_top_40pct_of_range. B595: no changes "
            "here (already had all 5 gates from B591 inception). Same vol_spike_15x "
            "fire-starving pattern PLUS 5-way AND compound."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_15x -> vol_spike_2x (same recurring fix - 17th strategy). "
            "Expected fire uplift 3-5x. Retain other 4 gates. Universe-agnostic breakout."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "institutional_increased_with_directors_long": {
        "cluster_id": "INSTITUTIONAL_INSIDER_COMBO_FAMILY",
        "owner_review_notes": (
            "2 fires. Wave 3 Batch 338: institutional_increased >= 5 + insider_director_"
            "buyers_30d >= 1 + EMA200. Triple validation: 13F persistence + director "
            "insider + trend. Akbas-Jiang-Koch 2024 director premium + Cohen-Malloy "
            "13F cluster. Same >=5 institutional threshold + director-only insider "
            "narrow set = 3-way ultra-scarce."
        ),
        "recommendation": (
            "LOOSEN: (a) institutional_increased >= 5 -> >= 3 (Cohen-Malloy canonical "
            "cluster - same as 5 other institutional strategies flagged); (b) also "
            "widen insider set from director-only to any insider (director-only is "
            "too narrow for 2-fire outcome). Expected fire uplift 5-8x."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "pivot_fib_confluence": {
        "cluster_id": "FLOOR_PIVOT_FAMILY",
        "owner_review_notes": (
            "2 fires. Dual: LONG = (near_s1 OR near_s2) + at_key_fib + (hammer OR "
            "bullish_engulfing); SHORT = (near_r1 OR near_r2) + at_key_fib + "
            "bearish_engulfing + borrow. Two-system confluence at same level. Root "
            "cause: pivot proximity (~5-10% of bars near S1/R1) + Fibonacci proximity "
            "(~3-5% of bars near key Fib) + specific candle = 3-way ultra-scarce joint."
        ),
        "recommendation": (
            "LOOSEN: widen candle set (hammer OR bullish_engulfing OR bullish_pin_bar "
            "OR piercing_line) for LONG; symmetric for SHORT. Also widen 'at_key_fib' "
            "tolerance if narrow. Expected fire uplift 2-3x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "supertrend_macd_short": {
        "cluster_id": "TREND_CONFLUENCE_FAMILY",
        "owner_review_notes": (
            "2 fires. B630 F1 sweep double-fix: supertrend_bearish + macd_12_26_9_"
            "bearish + adx > 20 + borrow. NOT the B655 EVENT-converted variant (that "
            "is supertrend_macd). This is legacy STATE version - all 3 STATE gates. "
            "Root cause: 3 STATE confirmations concurrent + borrow = ultra-rare. "
            "Consider whether B655 EVENT conversion should apply here too."
        ),
        "recommendation": (
            "AUDIT: is this the intended legacy STATE version or should it get B655 "
            "EVENT treatment applied? If EVENT-converted (supertrend_flip_recent_short_"
            "5d + macd_crossover_dn + adx_strong), gains B655 fire uplift + Pattern S "
            "SHORT caveat interpretation clarity. Otherwise LOOSEN: adx > 20 -> adx > "
            "15."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "halloween_seasonal_long": {
        "cluster_id": "SEASONAL_CALENDAR_FAMILY",
        "owner_review_notes": (
            "1 fire. Batch 254 Bouman-Jacobsen 2002 Halloween Indicator. Batch 723 "
            "STATE -> EVENT: is_halloween_period_first_day (single bar entering Nov) "
            "post-B655 T10 + B721 precedent + S4-B717 ceiling routing. B660 measured "
            "22,417/yr LONG at state-flag rate; post-B723 = 1 fire per ticker per year "
            "(first trading day of Nov). 150 tickers x 4y = 600 fires theoretical; "
            "1 actual is EXTREMELY LOW = producer investigation needed."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify is_halloween_period_first_day producer emits "
            "on first trading day of Nov each year for all tickers. 1 fire on 150 "
            "tickers x 4y (Nov 2022, 2023, 2024, 2025) suggests producer is severely "
            "underfiring. Expected fires per year should be 150 (one per ticker on "
            "Nov 1)."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "insider_cluster_with_director_long": {
        "cluster_id": "INSIDER_FORM4_FAMILY",
        "owner_review_notes": (
            "1 fire. Batch 222 higher-conviction insider variant: insider_cluster_active "
            "+ insider_director_buyers_30d >= 1 + EMA200. Lakonishok-Lee 2001 director "
            "premium. Same insider_cluster base + director-narrow filter as "
            "insider_cluster_long (Turn 10) but with director confluence. Ultra-scarce."
        ),
        "recommendation": (
            "UNIVERSE EXPANSION primary lever + LOOSEN director narrow filter: director-"
            "only insider is narrow (~30% of insider trades). Widen to (director OR "
            "officer + insider_cluster_active) - preserves conviction while allowing "
            "more fires. Expected fire uplift 3-5x."
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
    for strat, data in TURN_10_ANALYSIS.items():
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
    print(f"Turn 10 complete: updated {updated}. Cumulative {total_analyzed}/{len(df)} ({100*total_analyzed/len(df):.1f}%)")
    print(f"STARVED class: {starved_analyzed}/{starved_total}")

    from collections import Counter
    print(f"Turn 10 priorities: {Counter(d['priority'] for d in TURN_10_ANALYSIS.values())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
