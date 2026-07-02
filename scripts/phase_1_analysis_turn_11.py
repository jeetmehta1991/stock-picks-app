#!/usr/bin/env python
"""Phase 1 deep-dive analysis TURN 11 (Council 235 owner-approved 2026-07-02).

Turn 11 scope: FINAL STARVED batch - 11 strategies at 1 fire each.
Completes STARVED class (101/101 after this turn).
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_11_ANALYSIS = {
    "institutional_insider_combo_long": {
        "cluster_id": "INSTITUTIONAL_INSIDER_COMBO_FAMILY",
        "owner_review_notes": (
            "1 fire. Wave 3 Batch 331: dual smart-money confirmation - institutional_buy "
            "(13F STATE) + insider_cluster_active (Form 4 EVENT) + EMA200. "
            "Cohen-Malloy 2012 insider + Cohen-Frazzini-Malloy 2008 institutional. "
            "Multiplicative edge thesis: independent info channels. Root cause: 3-way "
            "joint (13F STATE + insider cluster EVENT + trend) = ultra-scarce - insider "
            "clusters are already rare (~5-15/yr universe-wide on T1a); requiring "
            "concurrent 13F institutional_buy narrows further."
        ),
        "recommendation": (
            "UNIVERSE EXPANSION primary lever (Cohen-Malloy 2012 documented alpha across "
            "all cap; T1a large-caps filter out mid/small where insider clusters more "
            "common). Consumer-side gates minimal - 3 gates already lean. If keeping "
            "T1a, LOOSEN insider_cluster_active AND -> OR (either signal counts vs "
            "requiring both). Expected fire uplift 5-8x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "institutional_persistence_oversold_long": {
        "cluster_id": "INSTITUTIONAL_13F_FAMILY",
        "owner_review_notes": (
            "1 fire. Wave 3 Batch 337: institutional_increased >= 5 + rsi_14 < 40 + "
            "EMA200. Persistence variant of institutional_oversold_long (Turn 3 base "
            "version 3-gate). Same >=5 threshold pattern as 5 other institutional_* "
            "strategies flagged HIGH."
        ),
        "recommendation": (
            "LOOSEN: institutional_increased >= 5 -> >= 3 (Cohen-Malloy canonical - 8th "
            "strategy with this same fix). Also widen rsi_14 < 40 -> rsi_14 < 45 (broader "
            "oversold per Bondt-Thaler). Expected fire uplift 3-5x. Combined loosening "
            "should lift to MARGINAL/VIABLE."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "institutional_with_officers_long": {
        "cluster_id": "INSTITUTIONAL_INSIDER_COMBO_FAMILY",
        "owner_review_notes": (
            "1 fire. Wave 3 Batch 336: institutional_buy + insider_officer_buyers_30d "
            ">= 1 + EMA200. Officer variant of institutional_with_directors_long (Turn "
            "10). CEO/CFO/COO buying own stock - competence + conviction signal. Lower "
            "information value than directors but higher than 10% owners. Same 3-way "
            "13F + insider EVENT + trend joint scarcity."
        ),
        "recommendation": (
            "LOOSEN: same as institutional_with_directors - widen officer-only insider "
            "set to (officer OR director) per Akbas-Jiang-Koch 2024 both signal above-"
            "baseline. Retain institutional_buy + EMA200. Expected fire uplift 3-4x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "inverted_cup_and_handle_short": {
        "cluster_id": "CHART_PATTERN_FAMILY",
        "owner_review_notes": (
            "1 fire. Batch 686 Class 7 NEW per B683 self-critique CP-1 missing-inverse "
            "audit. STATUS POST-B773: EXPLORATORY per B769 council F5 - Class 7 NEW "
            "inverse-mirror registered B686 but NEVER cluster-walked + inherits chart-"
            "pattern repaint/phantom-breakout risk + Pattern S SHORT-side asymmetric "
            "expectancy + previously flagged EXPLORATORY-candidate post-B660 fire-"
            "starve risk class."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B. Chart-pattern-repaint + "
            "Pattern S structural headwinds make FAIL-expected."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_inverted_cup_and_handle_wider_short: LOOSEN cup rim tolerance + "
            "widen handle break threshold. Also add PIT-anchor to prevent chart-pattern "
            "repaint per feedback_walk_step3. Expected fire uplift 2-3x. Pattern S "
            "FAIL-expected."
        ),
    },
    "january_effect_small_cap_long": {
        "cluster_id": "SEASONAL_CALENDAR_FAMILY",
        "owner_review_notes": (
            "1 fire. Batch 254 Rozeff-Kinney 1976 January Effect. STATUS POST-B830: "
            "EXPLORATORY - PATTERN AA event-strategy structurally-limited effective-N "
            "per W5 council + S5-MULTIPLE-TESTING-CORRECTION precedent. DO NOT DEPLOY "
            "marker. Small-cap subset filter narrows to ~small-cap names in T1a (few - "
            "S&P 500 is large-cap by design). Universe mismatch + rare January window."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B. UNIVERSE MISMATCH: "
            "small-cap January effect on T1a S&P 500 is architecturally wrong universe - "
            "requires small-cap universe (Russell 2000 style). Batch B / T3 mid-cap "
            "expansion may capture some effect."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_january_effect_smid_cap_long: expand universe filter from small-cap "
            "only to smid-cap (small + mid) + extend window from January-only to "
            "December-January (turn-of-year drift per Rozeff-Kinney). Preserves seasonal "
            "thesis; universe alignment needs Batch B/T3 fires to be meaningful."
        ),
    },
    "judas_swing_long": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "1 fire. Batch 581 Layer 2A ICT: smc_liquidity_swept_down + return to pivot "
            "midpoint + bullish bar. Distinct from smc_liquidity_sweep_reversal (needs "
            "CHoCH/BOS) + turtle_soup_long (needs close back above prior_low). Judas "
            "focuses on FALSE RANGE BREAK + DEEP return to interior. Root cause: 3-way "
            "compound ICT sweep + deep-return + candle = ultra-rare. Same "
            "smartmoneyconcepts producer family dependency (16th SMC strategy affected)."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FAMILY (per Turn 6 SMC family finding). Verify "
            "smc_liquidity_swept_down + pivot midpoint proximity + candle producers. "
            "If OK, retain 3-gate as canonical ICT Judas structure. Universe expansion "
            "may 2-3x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "mfi_oversold": {
        "cluster_id": "OSCILLATOR_CONFLUENCE_FAMILY",
        "owner_review_notes": (
            "1 fire. B791 REVERT-OF-B789 #43: B789 demo (30 tickers x 1yr) CONTRADICTED "
            "B789 smoke (5 tickers) - obv_bullish SELECTIVE not anti-selecting. Restored "
            "B628 F1 symmetric obv gates pending full T1a test per feedback_audit_"
            "recommendations_against_existing_directives empirical-evidence-supersedes-"
            "rule. Root cause: MFI < 20 (~2-5% of bars extreme oversold) + obv_bullish "
            "compound = 3-4% of bars per ticker. Producer-side note: Sister "
            "mfi_oversold_with_smart_money_long has B975 key-mismatch fixed already."
        ),
        "recommendation": (
            "LOOSEN MFI threshold from strict oversold (<20) to broader (<30). Same "
            "widening pattern as rsi_9_extreme (Turn 3), rsi_21_slow (Turn 3), "
            "stoch_oversold (Turn 9). Expected fire uplift 2-3x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "pead_with_insider_confirmation_long": {
        "cluster_id": "PEAD_FAMILY",
        "owner_review_notes": (
            "1 fire. Batch 222 PEAD + insider confluence: within_pead_window + "
            "pead_positive_surprise + insider_cluster_active. Higher-conviction PEAD "
            "variant (insider validates surprise is fundamental not noise). Same PEAD "
            "producer dependency as pead_long (Turn 8 HIGH) + insider cluster rarity "
            "compound = ultra-scarce joint."
        ),
        "recommendation": (
            "PEAD producer investigation (Turn 8 finding) + insider_cluster AND -> OR "
            "as secondary confluence. Loosen ann-day return >+2% -> >+1% per Garfinkel "
            "2024. Expected fire uplift 5-8x."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "pivot_s2_bounce": {
        "cluster_id": "FLOOR_PIVOT_FAMILY",
        "owner_review_notes": (
            "1 fire. REFRAMED POST-B879 as daily S2/R2 reaction zone (not pivot-"
            "precision intraday). Dual: LONG = near_s2 + rsi_14 < 40 + (hammer OR "
            "bullish_engulfing); SHORT = near_r2 + rsi_14 > 60 + bearish_engulfing + "
            "borrow. Root cause: S2 proximity (~5-8% of bars) + RSI extreme + specific "
            "candle = 3-way ultra-scarce joint."
        ),
        "recommendation": (
            "LOOSEN: widen candle set (hammer OR bullish_engulfing OR bullish_pin_bar OR "
            "piercing_line) for LONG; symmetric SHORT. Also widen rsi_14 < 40 -> < 45. "
            "Expected fire uplift 2-3x. Same candle-widening pattern as pivot_fib_"
            "confluence (Turn 10) + bullish_engulfing_support (Turn 7)."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "smc_fvg_retest_long": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "1 fire. Batch 216 SMC/ICT: smc_fvg_retest_long_zone + EMA200. Simple 2-gate "
            "but smc_fvg_retest_long_zone is a specific ICT-library producer signal "
            "(unmitigated bullish 3-bar imbalance + retest). Sister smc_fvg_retest_"
            "short (Turn 8, 8 fires). Same smartmoneyconcepts producer family "
            "dependency (17th SMC strategy)."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FAMILY (per Turn 6 finding). LONG vs SHORT count "
            "asymmetry (1 vs 8 fires) suggests producer symmetry issue - verify "
            "smc_fvg_retest_long_zone populates similarly to _short_zone. Also verify "
            "producer emits on canonical unmitigated FVG cases."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "smc_mitigation_block_short": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "1 fire. Batch 216 SMC/ICT: smc_mitigation_block_short + below_ema_200 + "
            "rsi_14 > 50 + borrow. Sister of smc_mitigation_block_long (Turn 4 HIGH; "
            "SILENT). Same producer dependency + Pattern S SHORT asymmetric expectancy. "
            "Also B416 silent-producer empty-return warning during Batch A run for "
            "smc_ict.compute_smc_signals."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER (per Turn 4 finding + B416 warning). Verify "
            "compute_smc_signals emits mitigation_block_short reliably. If producer OK, "
            "widen rsi_14 > 50 -> > 45 (broader rally context). Pattern S SHORT "
            "asymmetric caveat."
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
    for strat, data in TURN_11_ANALYSIS.items():
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
    print(f"Turn 11 complete: updated {updated}. Cumulative {total_analyzed}/{len(df)} ({100*total_analyzed/len(df):.1f}%)")
    print(f"STARVED class: {starved_analyzed}/{starved_total} (100% if 101/101)")

    from collections import Counter
    print(f"Turn 11 priorities: {Counter(d['priority'] for d in TURN_11_ANALYSIS.values())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
