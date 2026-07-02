#!/usr/bin/env python
"""Phase 1 deep-dive analysis TURN 5 (Council 235 owner-approved 2026-07-02).

Turn 5 scope: STARVED strategies top 15 by fire count (29-20 fires).
Focus: near-boundary strategies that could lift to MARGINAL/VIABLE with
minor threshold widening.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_5_ANALYSIS = {
    "bollinger_lower": {
        "cluster_id": "BOLLINGER_MEAN_REVERSION_FAMILY",
        "owner_review_notes": (
            "29 fires. Dual: LONG = below lower BB + (RSI_2<5 OR RSI_14<40 per VIX-band) + "
            "price_above_ema_200 + adx<30 (Connors discipline + Su 2024 confluence). "
            "SHORT = below_ema_200 + upper BB + RSI symmetric. Near-boundary at 29 fires "
            "(1 below min_trades_per_regime=30). Root cause: 4-way conjunction of BB touch + "
            "oversold RSI + trend regime + weak-ADX is genuine mean-reversion setup but "
            "specific. Universe-agnostic pattern."
        ),
        "recommendation": (
            "LOOSEN adx < 30 -> adx < 35 (still weak-ADX, broader). Or drop adx gate "
            "entirely (Connors 2024 canonical doesn't require ADX condition). Expected "
            "fire uplift 1.5-2x (would move from 29 -> 45-60, MARGINAL territory)."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "htf_aligned_breakout_long": {
        "cluster_id": "MULTI_TIMEFRAME_FAMILY",
        "owner_review_notes": (
            "29 fires. 3-gate stack: above_prev_high + vol_spike_15x + htf_aligned_bull. "
            "Batch 217 Brian Shannon triple-timeframe (daily breakout + weekly + monthly "
            "bull bias). Root cause: vol_spike_15x is the fire-starving leg (15x volume) "
            "combined with HTF alignment requirement (~30-50% of bars have full HTF "
            "alignment in bull markets). Same vol_spike pattern flagged 8x across Turns "
            "1-4."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_15x -> vol_spike_2x (Shannon canonical says 'above-average "
            "volume' not 15x). Retain above_prev_high + HTF alignment. Expected fire "
            "uplift 3-5x (29 -> 90-150, VIABLE territory)."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "break_retest_confluence": {
        "cluster_id": "BREAK_RETEST_FAMILY",
        "owner_review_notes": (
            "28 fires. Batch 609 walk (F1 regime-affinity fix + F2 3-gate silent-gap fix). "
            "Multi-indicator confluence break-and-retest. Root cause not shown in visible "
            "excerpt but B609 note indicates 3 SHORT-side positive-symmetric signals were "
            "added; likely gate stack is 5-7 signals per direction. Near-boundary at 28 "
            "fires."
        ),
        "recommendation": (
            "INVESTIGATE FULL GATE STACK: read complete B609 walk output + F2 fixes. If "
            "6+ gates per direction, LOOSEN one confluence gate (typically AVWAP OR OBV) "
            "per feedback_avwap_redundant + feedback_obv_avwap_macd_non_redundancy. "
            "Expected fire uplift 2-3x. Producer-side note: verify all 3 B609 F2 positive-"
            "symmetric signals populate correctly."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "williams_stoch_dual": {
        "cluster_id": "OSCILLATOR_CONFLUENCE_FAMILY",
        "owner_review_notes": (
            "28 fires. Batch 729 STATE -> EVENT conversion (stoch_oversold state -> "
            "stoch_bullish_cross event) per B655 pattern. Williams %R oversold + Stoch "
            "cross + near pivot (S1/S2/S3-Camarilla). Root cause: EVENT stoch cross "
            "is bar-of-fire (~2-5% of bars); combined with pivot proximity + WillR = "
            "specific joint. B660 measured 4,091/yr LONG + 6,587/yr SHORT pre-EVENT-"
            "conversion; post-B729 significantly reduced fires (~20x per B655 T10 "
            "precedent)."
        ),
        "recommendation": (
            "LOOSEN: widen pivot proximity from strict (near_s1/s2/s3) to (within 1 ATR "
            "of any pivot support level). Retain WillR + EVENT stoch cross. Expected "
            "fire uplift 2-3x. Also consider extending EVENT window from 1-bar to 3-bar "
            "recent-cross (B722 precedent)."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "inside_bar_breakout": {
        "cluster_id": "PRICE_ACTION_FAMILY",
        "owner_review_notes": (
            "27 fires. 3-gate: inside_bar + adx_trending + above_vwap. Universe-agnostic "
            "consolidation-breakout setup. Root cause: inside_bar is a specific candle "
            "pattern (~5-8% of bars); combined with adx_trending (~30% of bars) + "
            "above_vwap (~50% in uptrend) = joint ~1-2% per ticker per year."
        ),
        "recommendation": (
            "LOOSEN adx_trending gate (ADX > 25 -> ADX > 20; still trending but broader). "
            "Retain inside_bar + above_vwap. Expected fire uplift 1.5-2x. Also consider: "
            "widen inside_bar to inside_or_narrow_range (2-bar NR7 pattern) - broader "
            "consolidation family."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "institutional_persistence_momentum_long": {
        "cluster_id": "INSTITUTIONAL_13F_FAMILY",
        "owner_review_notes": (
            "26 fires. 3-gate: institutional_increased >= 5 + macd_12_26_9_bullish + "
            "price_above_ema_50. Wave 3 Batch 336. Same STATE-timing miscredit as other "
            "institutional_* + threshold of 5 funds is on the high side (Cohen-Malloy-"
            "Pomorski 2012 uses 3+ for 'cluster')."
        ),
        "recommendation": (
            "LOOSEN: institutional_increased >= 5 -> >= 3 (Cohen-Malloy-Pomorski "
            "canonical cluster threshold). Retain MACD + EMA50. Expected fire uplift 2-"
            "3x (26 -> 55-80, MARGINAL/VIABLE)."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "cpr_narrow_momentum": {
        "cluster_id": "FLOOR_PIVOT_FAMILY",
        "owner_review_notes": (
            "25 fires. Dual with 200-EMA regime gates (Batch 358 cell-audit added). "
            "B718 STATE -> EVENT: cpr_narrow (STATE ~15% of bars fired at 0.15 threshold) "
            "-> cpr_narrow_tight (0.05 threshold, ~5% of bars per B654 W8 fix precedent). "
            "REFRAMED post-B879 as daily-momentum-context. LONG requires above_ema_200; "
            "SHORT below."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify cpr_narrow_tight producer fires on canonical "
            "narrow-CPR days. If OK, LOOSEN cpr threshold from 0.05 -> 0.08 (still tight "
            "but broader). Expected fire uplift 1.5-2x. NOTE B718 tightened deliberately "
            "for W8 fix; loosening should be tested cube-side before deployment."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "institutional_recent_init_momentum_long": {
        "cluster_id": "INSTITUTIONAL_13F_FAMILY",
        "owner_review_notes": (
            "25 fires. 3-gate: institutional_new_positions >= 2 + macd_12_26_9_bullish + "
            "price_above_ema_200. Wave 3 Batch 338. Same 13F STATE-timing caveat. "
            "new_positions >= 2 threshold is reasonable (smaller cluster than "
            "persistence variant); MACD bullish state gate compounds."
        ),
        "recommendation": (
            "LOOSEN: macd_12_26_9_bullish (STATE) -> macd_12_26_9_crossover_up "
            "(EVENT, recent crossover) OR keep MACD but drop the AND to make MACD an "
            "OR with other momentum (rsi > 50). Expected fire uplift 2x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "smc_bos_continuation": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "25 fires. Batch 210 SMC BOS continuation. B278 tightening added vol_confirms "
            "(vol_spike_2x OR force_index_cross_up) + RSI direction-aligned per cell-"
            "audit findings (13 trades / 15.4% WR / -6.60% mean / -86pp pre-tightening). "
            "B975 fixed key-mismatch. 4-5 gate stack. B278 tightening was RESULT-driven; "
            "loosening risks reintroducing the 15.4% WR issue."
        ),
        "recommendation": (
            "STATUS QUO on B278 tightening (was empirically justified). Investigate "
            "producer: verify smc_bos_up populates via smartmoneyconcepts library. If "
            "producer sparse, universe expansion (Batch B / T3 momentum) more likely to "
            "help than gate loosening."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": "",
    },
    "turtle_soup_long": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "24 fires. Batch 580 first Layer 2D ICT inline-spec pattern (Raschke 1996 "
            "Street Smarts). 3-gate: smc_liquidity_swept_dn + above_prev_low + "
            "close_above_open. Universe-agnostic failed-breakdown mean-reversion. Root "
            "cause: smc_liquidity_swept_dn is a specific ICT producer event (stop-hunt "
            "below prior support); compound with same-bar reversal + bullish close = "
            "genuine setup but rare."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify smartmoneyconcepts library populates "
            "smc_liquidity_swept_dn on canonical failed-breakdowns (SPY 2020-03-23, "
            "2022-10-13 lows). If producer OK, retain 3-gate structure as canonical "
            "Raschke pattern - accept ~25 fires as structural minimum. Universe "
            "expansion may help."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "smc_equal_highs_sweep_short": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "22 fires. Batch 216: 2-gate stack: smc_equal_highs_swept + smc_fvg_bearish_"
            "active + borrow_ok. ICT stop-hunt-then-reverse. Root cause: equal_highs "
            "cluster identification is a producer-side rare event AND concurrent bearish "
            "FVG is doubly rare. Pattern S SHORT asymmetric expectancy caveat."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify smc_ict.py populates smc_equal_highs_swept + "
            "smc_fvg_bearish_active correctly. If producer OK, LOOSEN 'concurrent' "
            "requirement - allow bearish_fvg_active_last_5d (rolling window vs same-bar). "
            "Expected fire uplift 2x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "pivot_r1_breakout": {
        "cluster_id": "FLOOR_PIVOT_FAMILY",
        "owner_review_notes": (
            "21 fires. Batch 205 R1 breakout + AVWAP-from-252-day-low + DiNapoli volume "
            "confirmation. REFRAMED post-B879 as daily-momentum-context. Root cause: 3+ "
            "gates (R1 break + AVWAP + volume) is confluence stack; AVWAP redundant with "
            "R1 break per feedback_avwap_redundant_with_ema_trend_filter (both are "
            "institutional reference levels)."
        ),
        "recommendation": (
            "LOOSEN: drop AVWAP-from-252-day-low gate (redundant institutional reference "
            "vs R1). Retain R1 break + volume. Expected fire uplift 2-3x. NOTE: pivot_r2 "
            "already recommended similar drop (Turn 3 HIGH priority)."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "pre_fomc_long_sleeve": {
        "cluster_id": "EVENT_DRIVEN_MACRO_FAMILY",
        "owner_review_notes": (
            "21 fires. Batch 224 Lucca-Moench 2015 pre-FOMC drift + Cieslak-Pang 2024 "
            "yield-curve conditional. STATUS: EXPLORATORY DO NOT DEPLOY (B738 verdict FAIL "
            "on 2022-2026 sample - SPY mean pre-FOMC return +5.7bp; p=0.401 on n=35 FOMC "
            "dates). Fires at 21/yr through 8 FOMC per year x 2-3 pre-FOMC eligible days = "
            "matches expected rate for STRUCTURALLY rare event."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B. Pre-FOMC timing "
            "empirically DEAD per B738; loosening won't help unless the underlying "
            "hypothesis is revisited."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_pre_fomc_long_yield_curve_conditional: extract only the Cieslak-Pang "
            "2024 yield-curve-slope-conditional variant (steep curve is CONDITIONAL "
            "predictor per literature). Preserves theoretical basis while dropping the "
            "dead unconditional Lucca-Moench 2015 leg. Fire count similar (~20/yr) but "
            "cube can test whether conditional variant preserves alpha."
        ),
    },
    "prev_day_high_break": {
        "cluster_id": "PRICE_ACTION_FAMILY",
        "owner_review_notes": (
            "20 fires. Dual: LONG = above_prev_high + vol_spike_15x + above_vwap; SHORT = "
            "below_prev_low + vol_spike_15x + below_vwap + borrow_ok. Same vol_spike_15x "
            "pattern flagged across many strategies. above_prev_high is universe-agnostic "
            "common (~40% of bars in uptrend); vol_spike_15x is the fire-starving leg."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_15x -> vol_spike_2x (canonical says above-average, not "
            "15x). Expected fire uplift 3-5x (20 -> 60-100, VIABLE territory). Universe-"
            "agnostic pattern; high-value fix."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "turtle_soup_short": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "20 fires. Batch 580 mirror of turtle_soup_long. Setup: smc_liquidity_swept_"
            "up + below_prev_high + close_below_open + borrow_ok. Failed-breakout stop-"
            "hunt. Symmetric structure. Pattern S SHORT asymmetric expectancy caveat "
            "but Raschke 1996 canonical."
        ),
        "recommendation": (
            "Same as turtle_soup_long: investigate smartmoneyconcepts producer for "
            "smc_liquidity_swept_up. If producer OK, retain 3-gate + borrow as canonical. "
            "NOTE Pattern S SHORT asymmetric expectancy - cube may measure lower "
            "expectancy than LONG mirror."
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
    for strat, data in TURN_5_ANALYSIS.items():
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
    print(f"Turn 5 complete: updated {updated}. Cumulative {total_analyzed}/{len(df)} ({100*total_analyzed/len(df):.1f}%)")
    print(f"STARVED class: {starved_analyzed}/{starved_total}")

    from collections import Counter
    print(f"Turn 5 priorities: {Counter(d['priority'] for d in TURN_5_ANALYSIS.values())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
