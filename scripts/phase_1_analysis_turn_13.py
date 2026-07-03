#!/usr/bin/env python
"""Phase 1 deep-dive analysis TURN 13 (FINAL) - Council 235 owner-approved 2026-07-02.

Turn 13 scope: FINAL 16 MARGINAL strategies (48-30 fires).
Completes ALL 192 rows of phase_1_quiet_fire_investigation.csv.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_13_ANALYSIS = {
    "ppo_crossover": {
        "cluster_id": "MOMENTUM_OSCILLATOR_FAMILY",
        "owner_review_notes": (
            "48 fires. Dual: LONG = ppo_crossover_up + adx_trending; SHORT = symmetric "
            "+ borrow. PPO (Percentage Price Oscillator) is normalized MACD. Same "
            "redundant ADX pattern as awesome_oscillator (Turn 12 HIGH) + parabolic_"
            "sar_flip (Turn 12 HIGH) - momentum-cross signal + trend-strength gate is "
            "redundant since the cross ITSELF confirms momentum direction."
        ),
        "recommendation": (
            "LOOSEN: drop adx_trending gate (PPO cross IS momentum-direction signal). "
            "Expected fire uplift 2-3x (48 -> 100-150, VIABLE). Same redundancy pattern "
            "as feedback_avwap_redundant_with_ema_trend_filter applied to oscillator "
            "family."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "institutional_strong_conviction_long": {
        "cluster_id": "INSTITUTIONAL_13F_FAMILY",
        "owner_review_notes": (
            "47 fires. Wave 3 Batch 333: institutional_increased >= 5 + institutional_"
            "new_positions >= 2 + EMA200. Frazzini-Lamont 2008 dual conviction signature "
            "(new + existing agree). Same >=5 institutional_increased threshold pattern "
            "flagged 10x now; also has >=2 new_positions second threshold."
        ),
        "recommendation": (
            "LOOSEN: institutional_increased >= 5 -> >= 3 AND institutional_new_positions "
            ">= 2 -> >= 1 (both threshold widenings). Frazzini-Lamont dual-signature "
            "thesis preserved. Expected fire uplift 3-4x (47 -> 140-200, VIABLE)."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "hull_rsi": {
        "cluster_id": "OSCILLATOR_CONFLUENCE_FAMILY",
        "owner_review_notes": (
            "46 fires. Batch 207 Hull MA + RSI(9) + ADX(14) > 20 trend confirmation. "
            "B358 added price_above_ema_200 bear-regime block on long leg per cell "
            "audit (hull_rsi x atr_trail_1x lost -1371pp at WR 25% in bear regime). "
            "Multi-gate structure was empirically tightened per cell-audit findings."
        ),
        "recommendation": (
            "STATUS QUO on B358 tightening (empirically justified). LOOSEN adx > 20 -> "
            "adx > 15 as low-risk boundary widen. Expected fire uplift 1.3-1.5x (46 -> "
            "60-70, still MARGINAL near-VIABLE)."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "break_retest_volume": {
        "cluster_id": "BREAK_RETEST_FAMILY",
        "owner_review_notes": (
            "44 fires. Batch 617 external-AI critique re-fix on B608 walk. Multi-gate "
            "break-retest with OBV vs 20-bar MA flow confirmation + Bulkowski retest "
            "dry-up volume. B617 addressed 3 critique items missed by B608 (B320 "
            "vol_spike_2x reconciliation + other refinements). Post-B617 empirically-"
            "justified structure."
        ),
        "recommendation": (
            "STATUS QUO on B617 tightening. Retest strategies structurally lower "
            "fire count. Universe expansion + producer-side widening likely levers "
            "to lift over VIABLE."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "smc_equal_lows_sweep_long": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "41 fires. Batch 216 SMC/ICT: smc_equal_lows_swept + smc_fvg_bullish_active. "
            "Symmetric mirror of smc_equal_highs_sweep_short (Turn 6, 22 fires). "
            "2-gate ICT reversal-confluence setup. Same producer family dependency."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FAMILY. Same widening as smc_equal_highs (Turn 6): "
            "allow bullish_fvg_active_last_5d (rolling window vs same-bar) instead "
            "of concurrent requirement. Expected fire uplift 1.5-2x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "pivot_s1_bounce": {
        "cluster_id": "FLOOR_PIVOT_FAMILY",
        "owner_review_notes": (
            "40 fires. REFRAMED POST-B879 as daily S1/R1 reaction zone. Similar pattern "
            "to pivot_s2_bounce (Turn 11, 1 fire STARVED). S1 pivot proximity + candle "
            "confirmation. Post-B879 daily-bar reframe explicitly drops pivot-precision "
            "language."
        ),
        "recommendation": (
            "LOOSEN: widen candle confirmation set (hammer/shooting_star OR bullish_"
            "engulfing/bearish_engulfing OR pin_bar family) per Nison 1991. Expected "
            "fire uplift 1.5-2x. Same widening pattern as bullish_engulfing_support "
            "(Turn 7) + pivot_fib_confluence (Turn 10)."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "squeeze_breakout": {
        "cluster_id": "BOLLINGER_SQUEEZE_FAMILY",
        "owner_review_notes": (
            "39 fires. Simple single-gate: squeeze_fire_up. LazyBear TTM Squeeze release "
            "signal (BB inside KC = coiling; release = energy). One of highest-"
            "probability breakout signals in trading literature. Related to bb_squeeze_"
            "volume (Turn 1, SILENT) which failed producer investigation."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify compute_squeeze emits squeeze_fire_up "
            "reliably on canonical squeeze release events. Single-gate structure is "
            "already lean. If producer OK, 39 fires reflects the structural rate of "
            "squeeze events - accept as intentional design or seek universe expansion."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "golden_cross_9_21": {
        "cluster_id": "GOLDEN_DEATH_CROSS_FAMILY",
        "owner_review_notes": (
            "38 fires. Dual: LONG = ema_9_21_golden_cross + price_above_sma_50; SHORT = "
            "symmetric + borrow. Fastest golden-cross variant (9/21 vs 20/50 vs 50/200). "
            "B630 positive-symmetric below_sma_50 sweep. Same 50-SMA regime redundancy "
            "as golden_cross_20_50 (Turn 9 HIGH) - EMA cross IS the trend signal."
        ),
        "recommendation": (
            "LOOSEN: drop 50-SMA regime gate (EMA 9/21 cross IS trend-direction signal - "
            "redundant per feedback_avwap_redundant precedent). Expected fire uplift "
            "2-3x (38 -> 80-115, MARGINAL/VIABLE). Same fix as golden_cross_20_50."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "avwap_252_breakout": {
        "cluster_id": "AVWAP_REJECTION_FAMILY",
        "owner_review_notes": (
            "32 fires. Batch 208 Shannon 2022 Anchored VWAP from 252-day swing low. "
            "LONG: price reclaims AVWAP-252-low + volume + RSI not extreme-overbought. "
            "SHORT: price loses AVWAP-252-low + volume. Institutional-level year-anchor "
            "inflection setup. Root cause: 252-day AVWAP reclaim/loss is specific EVENT "
            "(~5-10/yr per ticker); volume + RSI compound."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify avwap_252 reclaim/loss producer fires on "
            "canonical cases. If OK, LOOSEN vol threshold (if vol_spike_15x present) "
            "or drop RSI extreme filter. Expected fire uplift 1.5-2x. Producer already "
            "specific enough."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "xs_momentum_top_decile": {
        "cluster_id": "CROSS_SECTIONAL_FAMILY",
        "owner_review_notes": (
            "32 fires. STATUS POST-B787: EXPLORATORY per B786 verdict FAIL_FIRE_STARVED "
            "43/yr under full config (200x drop from B780 8,996/yr baseline due to "
            "#58(e) survivorship-bias correction). Post-#58(e) T1a names mostly NOT in "
            "top decile when T2+T3 momentum names join rank universe."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B. 200x drop reveals "
            "structural universe issue - T1a alone can't populate top-decile momentum "
            "when T2+T3 join ranking universe."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_xs_momentum_top_quintile_long: LOOSEN top-decile -> top-quintile "
            "(20% vs 10% breadth). Preserves cross-sectional momentum thesis with more "
            "T1a inclusions. Expected fire uplift 2-3x. Same pattern as Turn 4 "
            "xs_combined_momentum_low_ivol variant."
        ),
    },
    "donchian_10_breakout": {
        "cluster_id": "DONCHIAN_FAMILY",
        "owner_review_notes": (
            "31 fires. Batch 320 loosened vol gate from vol_spike_15x to vol_above_avg "
            "(the 1.5x bar gated out all 10-day breakouts). B591 walk added narrow-"
            "scope 1% tolerance variants + close_above_open + close_in_top_40pct_of_"
            "range. Post-B591 5-gate structure. 31 fires is close to VIABLE."
        ),
        "recommendation": (
            "STATUS QUO on B591 walk (empirically justified). To lift to VIABLE: "
            "LOOSEN close_in_top_40pct_of_range -> close_in_top_50pct (broader strong-"
            "close band). Expected fire uplift 1.5-2x (31 -> 45-60, MARGINAL/VIABLE)."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "prev_day_low_bounce": {
        "cluster_id": "PRICE_ACTION_FAMILY",
        "owner_review_notes": (
            "31 fires. Dual: LONG = near_prev_low + hammer + cmf_positive; SHORT = "
            "near_prev_high + shooting_star + cmf_negative + borrow. B629 F1 cmf-family "
            "sweep for positive symmetric cmf_negative. Root cause: same candle-single-"
            "gate limitation pattern as bullish_engulfing_support (Turn 7)."
        ),
        "recommendation": (
            "LOOSEN: widen candle set (hammer OR bullish_engulfing OR bullish_pin_bar "
            "OR piercing_line) for LONG; symmetric SHORT. Retain proximity + CMF flow. "
            "Expected fire uplift 2-3x (31 -> 60-90, MARGINAL/near-VIABLE)."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "camarilla_r4_breakout": {
        "cluster_id": "FLOOR_PIVOT_FAMILY",
        "owner_review_notes": (
            "30 fires. REFRAMED POST-B787 as daily momentum context (R4 break + volume "
            "confirms daily momentum, not pivot-precision intraday). Camarilla R4 "
            "breakout / S4 breakdown with volume confirmation. Post-B641 renamed from "
            "R3->R4 per Camarilla source-system re-anchor."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify Camarilla R4/S4 producers populate correctly "
            "(post-B641 rename). If OK, this is at MARGINAL boundary; consider LOOSEN "
            "volume threshold. Expected fire uplift 1.5-2x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "dc20_break_retest": {
        "cluster_id": "BREAK_RETEST_FAMILY",
        "owner_review_notes": (
            "30 fires. Batch 682 thesis-implementation alignment: swapped vol_spike_15x "
            "-> vol_below_avg per Bulkowski 2005 retest absorption thesis (retests form "
            "on LOWER volume than breakout bar). Empirically-motivated tightening + "
            "canonical alignment. B682 also same as flag_bull_retest / 52wh_break_retest "
            "family pattern."
        ),
        "recommendation": (
            "STATUS QUO on B682 Bulkowski-canonical vol_below_avg. Retest inherently "
            "rarer than base breakout. Producer investigation for dc20_break_retest "
            "signal may help. 30 fires at MARGINAL boundary."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "pead_short": {
        "cluster_id": "PEAD_FAMILY",
        "owner_review_notes": (
            "30 fires. Batch 209 PEAD short symmetric mirror: within_pead_window + "
            "pead_negative_surprise + borrow. Garfinkel et al. 2024 bottom-decile-"
            "surprise underperformance in 60-day window. Same pead_positive_surprise "
            "producer dependency as pead_long (Turn 8 HIGH). Pattern S SHORT asymmetric "
            "expectancy caveat."
        ),
        "recommendation": (
            "Same as pead_long: investigate PEAD producer + LOOSEN ann-day return "
            "threshold if present. 30 fires at MARGINAL boundary; producer investigation "
            "may lift meaningfully. Pattern S caveat."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "rsi_oversold": {
        "cluster_id": "RSI_MEAN_REVERSION_FAMILY",
        "owner_review_notes": (
            "30 fires. Batch 206 Connors stack: primary signal (rsi_2 < 5 OR rsi_14 < "
            "35) + 200-EMA regime + 50-SMA pullback context. Multi-tier oversold with "
            "Connors discipline. Pre-B206 rsi_14 < 35 alone had 0 trades in Phase 1A-"
            "beta (rarely triggers); rsi_2 < 5 path opens strategy to fire on extreme "
            "intraday. 30 fires post-B206 upgrade."
        ),
        "recommendation": (
            "STATUS QUO on B206 Connors stack (empirically justified). To lift to "
            "VIABLE: LOOSEN rsi_14 < 35 -> rsi_14 < 40 (still meaningfully oversold). "
            "Retain rsi_2 < 5 event trigger. Expected fire uplift 1.5-2x (30 -> 45-60, "
            "MARGINAL boundary)."
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
    for strat, data in TURN_13_ANALYSIS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found in CSV")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    df.to_csv(csv_path, index=False)
    total_analyzed = (df["owner_review_notes"].fillna("").str.len() > 0).sum()
    print(f"Turn 13 (FINAL) complete: updated {updated}.")
    print(f"CUMULATIVE: {total_analyzed} of {len(df)} ({100*total_analyzed/len(df):.1f}%)")
    print()
    print("=== PHASE 1 CLASS COMPLETION ===")
    for cls in ("SILENT", "STARVED", "MARGINAL"):
        cls_total = (df["class"] == cls).sum()
        cls_analyzed = ((df["class"] == cls) & (df["owner_review_notes"].fillna("").str.len() > 0)).sum()
        print(f"  {cls}: {cls_analyzed}/{cls_total}")
    print()

    from collections import Counter
    all_priorities = df[df["priority"].fillna("").str.len() > 0]["priority"].value_counts()
    print("=== FINAL PRIORITY DISTRIBUTION (all 192 strategies) ===")
    for p in ("HIGH", "MED", "LOW"):
        print(f"  {p}: {all_priorities.get(p, 0)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
