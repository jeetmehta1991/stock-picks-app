#!/usr/bin/env python
"""Phase 1 deep-dive analysis TURN 12 (Council 235 owner-approved 2026-07-02).

Turn 12 scope: MARGINAL top 15 by fire count (98-49 fires).
Near-boundary strategies - small threshold widening likely lifts to VIABLE.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_12_ANALYSIS = {
    "three_white_soldiers": {
        "cluster_id": "CANDLE_PATTERN_FAMILY",
        "owner_review_notes": (
            "98 fires. Batch 636 Nison 3-candle bullish reversal (each closing higher + "
            "opening higher, RSI<60 avoid overbought). Very close to VIABLE 100 "
            "threshold - only 2 fires short. Universe-agnostic reversal pattern. "
            "Root cause: 3-candle sequence is naturally rare (~1-2/yr per ticker); "
            "RSI<60 filter is reasonable non-overbought gate."
        ),
        "recommendation": (
            "LOOSEN: rsi_14 < 60 -> rsi_14 < 65 (broader non-overbought zone; still "
            "avoids overbought). Retain 3-candle sequence. Expected fire uplift 1.2-"
            "1.5x (98 -> 120-150, VIABLE). Universe-agnostic near-boundary quick win."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "institutional_cluster_long": {
        "cluster_id": "INSTITUTIONAL_13F_FAMILY",
        "owner_review_notes": (
            "93 fires. Wave 3 Batch 330: institutional_strong_buy + EMA200. Uses "
            "strong_buy composite (new_positions >= 3 OR new_pos >= 1 AND increased >= 2). "
            "Close to VIABLE. Root cause: institutional_strong_buy is quarterly 13F "
            "STATE (~15% of bars where filings arrive) + EMA200 uptrend = 2-way joint. "
            "Same 13F STATE-timing miscredit caveat as broader family."
        ),
        "recommendation": (
            "STATUS QUO on 2-gate (already minimal). To lift over VIABLE consider "
            "producer investigation for 13F cadence + universe expansion. 7 fires shy "
            "of VIABLE - close boundary."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "avwap_50_reclaim": {
        "cluster_id": "AVWAP_REJECTION_FAMILY",
        "owner_review_notes": (
            "89 fires. B790 EVENT-on-reclaim conversion (avwap_50low_reclaim_recent_3d "
            "vs pre-fix STATE above_avwap_50low). Fires only on FRESH reclaim event "
            "within last 3 days. Batch 790 was tightening move per CHECKLIST #108. "
            "89 fires post-EVENT-conversion is expected outcome."
        ),
        "recommendation": (
            "STATUS QUO on B790 EVENT conversion (empirically justified). To lift to "
            "VIABLE: widen recent-3d window to recent-5d (still EVENT vs STATE). "
            "Expected fire uplift 1.3-1.5x. Consider trade-off: EVENT-alpha strongest "
            "at 1-3d post-reclaim."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "smc_breaker_block_short": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "89 fires. Batch 216 SMC/ICT: smc_breaker_block_bearish + below_ema_200 + "
            "borrow. Bullish OB mitigated -> role flipped to resistance. Simple 2-gate "
            "ICT setup. Higher fire count than most SMC family (structural signal + "
            "simple trend gate). Family-wide producer investigation applies per Turn 6."
        ),
        "recommendation": (
            "STATUS QUO on 2-gate structure. Producer family investigation may "
            "increase fires. 11 fires shy of VIABLE. Pattern S SHORT asymmetric "
            "expectancy caveat."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "three_black_crows_short": {
        "cluster_id": "CANDLE_PATTERN_FAMILY",
        "owner_review_notes": (
            "83 fires. Batch 636 Nison 3-candle bearish reversal symmetric mirror of "
            "three_white_soldiers. RSI > 40 non-oversold gate. Pattern S SHORT "
            "asymmetric expectancy caveat."
        ),
        "recommendation": (
            "LOOSEN: rsi_14 > 40 -> rsi_14 > 35 (broader non-oversold). Expected fire "
            "uplift 1.2-1.5x (83 -> 100-125, VIABLE). Symmetric to three_white_soldiers "
            "fix. Pattern S caveat."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "smc_inverse_fvg": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "81 fires. Batch 262 fix (Pass 53 Day 9+): B216 original signal fired 478 "
            "trades / 40% of all flow / 24.7% WR / -1659pp loss = ~95% of aggregate "
            "loss. Added regime + volume + momentum filters. Post-B262 gate stack is "
            "TIGHTENED for empirical reasons. Loosening RISKS reintroducing the "
            "24.7% WR issue."
        ),
        "recommendation": (
            "STATUS QUO on B262 tightening (empirically justified per catastrophic "
            "loss avoidance). 19 fires shy of VIABLE; accept as intentional trade-off. "
            "Producer investigation could increase without loosening gates."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": "",
    },
    "institutional_buy_momentum_long": {
        "cluster_id": "INSTITUTIONAL_13F_FAMILY",
        "owner_review_notes": (
            "80 fires. Wave 3 Batch 330: institutional_buy + macd_12_26_9_bullish + "
            "price_above_ema_50. Yan-Zhang 2009 institutional persistence + price "
            "trend agreement. Looser 13F signal (any buy vs strong_buy). Same STATE "
            "13F miscredit caveat + MACD STATE compound."
        ),
        "recommendation": (
            "LOOSEN: macd_12_26_9_bullish (STATE) -> macd_12_26_9_crossover_up (EVENT) "
            "per feedback_signal_temporality. Or drop MACD to isolate institutional "
            "+ trend thesis. Expected fire uplift 1.5-2x (80 -> 120-160, VIABLE)."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "smc_choch_reversal": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "73 fires. Batch 210 ICT/SMC: smc_choch_bullish + smc_fvg_bullish_active "
            "(LONG); smc_choch_bearish + smc_fvg_bearish_active + borrow (SHORT). "
            "High-conviction reversal per ICT discipline. Same producer family "
            "dependency as other SMC strategies."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FAMILY per Turn 6 finding. Consumer-side gates lean; "
            "producer symmetry issues (per Turn 11 smc_fvg_retest LONG vs SHORT) may "
            "affect this too. 27 fires shy of VIABLE."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "cpr_narrow_momentum_short": {
        "cluster_id": "FLOOR_PIVOT_FAMILY",
        "owner_review_notes": (
            "61 fires. B718 switched cpr_narrow -> cpr_narrow_tight (0.05 threshold; "
            "B654 producer) per B710 reviewer fire-count-ceiling. Pre-B718 measurement: "
            "13,906/yr SHORT = state-flag above 5K ceiling. Post-B718 = MARGINAL "
            "territory. Symmetric mirror of cpr_narrow_momentum (Turn 5)."
        ),
        "recommendation": (
            "STATUS QUO on B718 tightening (empirically justified per B710 ceiling). "
            "Producer verify cpr_narrow_tight populates. Universe expansion primary "
            "lever. Pattern S SHORT asymmetric caveat."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "awesome_oscillator": {
        "cluster_id": "MOMENTUM_OSCILLATOR_FAMILY",
        "owner_review_notes": (
            "59 fires. Bill Williams AO zero-line cross + EMA-20 trend filter. Batch "
            "627 F1 family-sweep: positive symmetric below_ema_20 per B609 producer. "
            "Root cause: AO zero-line cross is EVENT (~5-10/yr per ticker); EMA-20 "
            "trend gate = ~40% of bars trend-aligned. Compound = specific."
        ),
        "recommendation": (
            "LOOSEN: drop EMA-20 gate (AO zero-line cross IS a momentum-direction "
            "signal; redundant with trend confirmation). Expected fire uplift 2-3x "
            "(59 -> 120-180, VIABLE). Similar redundancy pattern as feedback_avwap_"
            "redundant + Turn 10 parabolic_sar_flip_short."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "smc_bos_retest_entry": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "56 fires. Batch 216 ICT: BOS retest within 0.5% of broken structure + "
            "EMA200. Higher hit rate than naive BOS continuation per ICT discipline. "
            "Same producer family dependency. Retest strategies inherently rarer than "
            "base continuation."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FAMILY. Producer-side widen retest tolerance from "
            "0.5% -> 1.0% may 1.5-2x fires. 44 fires shy of VIABLE - meaningful gap."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "naked_poc_retest_long": {
        "cluster_id": "VOLUME_PROFILE_FAMILY",
        "owner_review_notes": (
            "52 fires. Batch 255: naked_poc_count > 0 + naked_poc_nearest_distance_pct "
            "< 0.02 (2% proximity per B314 loosen from 1%) + EMA200. B1035 confirmed "
            "producer works. Root cause: 2% naked POC proximity is specific (~5-10% of "
            "bars); untested POC count > 0 is common in trending markets."
        ),
        "recommendation": (
            "LOOSEN: naked_poc_nearest_distance_pct < 0.02 -> < 0.03 (3% proximity - "
            "still tight vs pre-B314 1%). Expected fire uplift 1.5-2x. Retain EMA200. "
            "Note B724 tightened poc_magnet_long back to 2% - consistency check with "
            "poc_magnet family alignment."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "donchian_breakout_retest_long": {
        "cluster_id": "BREAK_RETEST_FAMILY",
        "owner_review_notes": (
            "50 fires. Batch 591 Class 7 NEW tight long-only retest mirror. Batch 596 "
            "walk: flipped vol_spike_15x -> vol_below_avg per Bulkowski retest thesis. "
            "5-gate: resistance_break_retest + vol_below_avg + macd_bullish + "
            "close_above_open + close_in_top_40pct_of_range. Post-B596 lean version. "
            "50 fires close to VIABLE."
        ),
        "recommendation": (
            "STATUS QUO on B596 Bulkowski-canonical vol_below_avg. Retest strategies "
            "structurally lower fire than base breakout. 50 fires shy of VIABLE; "
            "producer investigation for resistance_break_retest may help."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "parabolic_sar_flip": {
        "cluster_id": "TREND_FAMILY",
        "owner_review_notes": (
            "50 fires. Dual: LONG = psar_flip_up + adx_trending; SHORT = psar_flip_dn "
            "+ adx_trending + borrow. Base version of parabolic_sar_flip_short (Turn 10). "
            "Same adx_trending redundancy pattern applies - PSAR flip IS a trend "
            "signal."
        ),
        "recommendation": (
            "LOOSEN: drop adx_trending gate (PSAR flip IS a trend-change signal - "
            "redundant with ADX confirmation). Expected fire uplift 2-3x (50 -> 100-"
            "150, VIABLE). Same pattern as parabolic_sar_flip_short recommendation."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "institutional_persistent_holders_long": {
        "cluster_id": "INSTITUTIONAL_13F_FAMILY",
        "owner_review_notes": (
            "49 fires. Wave 3 Batch 333: institutional_increased >= 5 + EMA200 (Yan-"
            "Zhang 2009 persistence proxy). Same >=5 threshold pattern as 6+ other "
            "institutional_* strategies flagged for canonical 3-threshold widening. "
            "Simple 2-gate structure."
        ),
        "recommendation": (
            "LOOSEN: institutional_increased >= 5 -> >= 3 (Cohen-Malloy canonical - "
            "9th strategy with same fix). Expected fire uplift 2-3x (49 -> 100-150, "
            "VIABLE). Simple threshold change lifts to VIABLE territory."
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
    for strat, data in TURN_12_ANALYSIS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found in CSV")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    df.to_csv(csv_path, index=False)
    total_analyzed = (df["owner_review_notes"].fillna("").str.len() > 0).sum()
    marginal_total = (df["class"] == "MARGINAL").sum()
    marginal_analyzed = ((df["class"] == "MARGINAL") & (df["owner_review_notes"].fillna("").str.len() > 0)).sum()
    print(f"Turn 12 complete: updated {updated}. Cumulative {total_analyzed}/{len(df)} ({100*total_analyzed/len(df):.1f}%)")
    print(f"MARGINAL class: {marginal_analyzed}/{marginal_total}")

    from collections import Counter
    print(f"Turn 12 priorities: {Counter(d['priority'] for d in TURN_12_ANALYSIS.values())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
