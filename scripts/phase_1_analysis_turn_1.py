#!/usr/bin/env python
"""Phase 1 deep-dive analysis TURN 1 (Council 235 owner-approved 2026-07-02).

Owner directive: Option A (manual per-strategy, ~10-16 hr total). This is Turn 1
covering first 15 SILENT strategies alphabetically.

Analysis method:
  1. Read strat_<name>() function source from screener.py
  2. Identify gate stack + producer signals
  3. Diagnose why it's not firing in Batch A
  4. Recommend specific remediation with concrete gate change
  5. Assign priority (HIGH universe-agnostic + high projected fires;
     MED conditional; LOW rare-by-design)

Outputs updated phase_1_quiet_fire_investigation.csv with 5 NEW columns:
  cluster_id                - shared architecture / producer family
  owner_review_notes        - per-strategy diagnostic reasoning
  recommendation            - concrete action to take
  priority                  - HIGH / MED / LOW
  exploratory_loose_variant - for EXPLORATORY: proposed looser companion

Turn 1 scope: strategies 1-15 alphabetically SILENT (per Council 235 plan).
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


# Turn 1: first 15 SILENT strategies analyzed manually
TURN_1_ANALYSIS = {
    "52w_low_breakdown": {
        "cluster_id": "52W_BREAKOUT_FAMILY",
        "owner_review_notes": (
            "5-gate stack: break_52w_low + vol_spike_17x + sector_underperforming_spy "
            "+ close_below_open + close_in_bottom_40pct_of_range. The vol_spike_17x (17x "
            "average volume) is the fire-starving leg. 52w low + weak close + underperform "
            "would fire far more often at 5x vol. Batch 587 tightened vol_spike_2x -> "
            "vol_spike_17x citing George-Hwang 2004 institutional distribution; the citation "
            "supports the DIRECTION but not the 17x magnitude specifically."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_17x -> vol_spike_5x. Rationale: 17x is extreme; 5x still "
            "captures institutional distribution while allowing normal capitulation days to "
            "fire. Retain other 4 gates. Expected fire count uplift: ~10-20x."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "52wh_break_retest": {
        "cluster_id": "52W_BREAKOUT_FAMILY",
        "owner_review_notes": (
            "7-gate stack (Batch 605 post-BUG-111 fix): year_high_break_retest_long + "
            "near_52w_high + price_above_ema_200 + close_above_open + "
            "close_in_top_40pct_of_range + vol_below_avg + above_avwap_20low. 7-way AND is "
            "statistically rare. vol_below_avg (Bulkowski retest supply-absorption) AND "
            "above_avwap_20low are the two 'confluence' gates - both institutional-price-"
            "reference redundant with EMA200 trend. Per feedback_avwap_redundant_with_ema"
            "_trend_filter both can go."
        ),
        "recommendation": (
            "LOOSEN: drop vol_below_avg AND above_avwap_20low. 5-gate core "
            "(year_high_break_retest_long + near_52w_high + price_above_ema_200 + "
            "close_above_open + close_in_top_40pct_of_range) is the textbook retest. "
            "Expected fire count uplift: ~5-10x."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "52wl_break_retest_short": {
        "cluster_id": "52W_BREAKOUT_FAMILY",
        "owner_review_notes": (
            "8-gate stack (mirror of 52wh_break_retest): year_low_break_retest_short + "
            "near_52w_low + below_ema_200 + close_below_open + close_in_bottom_40pct_of_"
            "range + vol_below_avg + below_avwap_20high + borrow_ok. Same architecture as "
            "long variant - vol_below_avg + below_avwap_20high are redundant confluence. "
            "Also carries SHORT-side asymmetric expectancy per feedback_structural_"
            "symmetry_not_economic_symmetry (equity upward drift bias)."
        ),
        "recommendation": (
            "LOOSEN: drop vol_below_avg AND below_avwap_20high (symmetric to 52wh_break_"
            "retest recommendation). Keep 5-gate core + borrow_ok. Expected fire count "
            "uplift ~5-10x. NOTE per feedback_structural_symmetry_not_economic_symmetry: "
            "even after loosening, this SHORT may have lower expected value than the LONG "
            "mirror due to equity upward drift + squeeze risk."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "avwap_20high_rejection_short": {
        "cluster_id": "AVWAP_REJECTION_FAMILY",
        "owner_review_notes": (
            "6-gate stack: below_avwap_20high + abs(pct_from_avwap_20high) < 1% + "
            "(shooting_star OR bearish_engulfing) + vol_spike_15x + below_ema_200 + "
            "borrow_ok. Two fire-starving legs: (a) vol_spike_15x is 15x average - extreme, "
            "(b) abs(pct_from_avwap) < 1% is a NARROW band that requires precise AVWAP "
            "kissing. In combination with specific candle + trend gate the joint probability "
            "is very low."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_15x -> vol_spike_5x AND widen abs(pct_from_avwap) < 1% -> "
            "< 2%. Rationale: 5x vol still confirms rejection; 2% AVWAP band captures near-"
            "kisses without requiring precision. Retain candle + EMA200 + borrow_ok. "
            "Expected fire count uplift: ~15-30x."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "bb_squeeze_volume": {
        "cluster_id": "BOLLINGER_SQUEEZE_FAMILY",
        "owner_review_notes": (
            "3-gate stack: squeeze_fire_up + vol_spike_2x + above_vwap (mirror short). "
            "Only 3 gates - not gate-stacking. Root cause is likely the squeeze_fire_up/dn "
            "producer signal being rare. compute_bb_squeeze produces squeeze_fire_up only "
            "when BB width contracts below 20-day min then expands - a genuine squeeze "
            "event. Universe-agnostic pattern but rare during trending markets. "
            "Batch A 2022-2026 window had extended bull run 2023-2024 which reduces "
            "squeeze events."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FIRST: verify squeeze_fire_up populates non-zero for "
            "canonical squeeze events (e.g., 2022 Q3 consolidation). If producer OK, "
            "consider LOOSEN vol_spike_2x -> vol_above_avg (Bollinger 1992 canonical says "
            "expansion + rising volume, no 2x mandate). If producer broken, fix "
            "compute_bb_squeeze in signals/technical.py. Expected fire count uplift after "
            "loosening: ~3-5x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "classification_change_recent_long": {
        "cluster_id": "CLASSIFICATION_CHANGE_PATTERN_AA",
        "owner_review_notes": (
            "PATTERN AA (Batch 332): recent GICS reclassification (30-90d lookback) + "
            "price_above_ema_200. Brogaard-Heath-Saadi 2019 analyst re-rating alpha. "
            "STATUS: EXPLORATORY POST-B830 - PATTERN AA structurally-limited effective-N "
            "per W5 council + S5-MULTIPLE-TESTING-CORRECTION precedent. Reclassifications "
            "are RARE events (< 30/yr universe-wide). DO NOT DEPLOY marker in docstring."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B. This is a rare-event "
            "strategy by design; the point is measuring the effect, not fire count."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_classification_change_recent_2y_long: extend reclassification lookback "
            "window from 30-90d to 90-730d (2-year) to accumulate more fires. Same alpha "
            "hypothesis (Brogaard-Heath-Saadi 2019 re-rating window is 6-24 months post-"
            "reclassification per literature). Loose variant should hit min_trades floor "
            "for statistical validity while preserving the event-driven thesis."
        ),
    },
    "classification_change_to_tech_long": {
        "cluster_id": "CLASSIFICATION_CHANGE_PATTERN_AA",
        "owner_review_notes": (
            "PATTERN AA (Batch 332): reclassification INTO growth sectors (IT / Comms / "
            "Health Care). Chen-Chen 2010 growth re-rating alpha. Batch A window 2022-2026 "
            "had few large-cap growth reclassifications - META/GOOGL example (2018) is "
            "outside window; V/MA (2023 IT->Financials) gated OFF correctly as non-growth "
            "target. Rare event by structural design."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B. Growth-sector "
            "reclassifications are rare but potentially high-alpha per Chen-Chen 2010."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_classification_change_to_growth_wider_long: extend lookback to 2y AND "
            "expand target sector set from {IT, Comms, Health} to {IT, Comms, Health, "
            "Discretionary} (Consumer Discretionary also carries growth premium per "
            "Fama-French SMB HML). Preserves growth-rating alpha with broader coverage."
        ),
    },
    "classification_change_to_defensive_short": {
        "cluster_id": "CLASSIFICATION_CHANGE_PATTERN_AA",
        "owner_review_notes": (
            "PATTERN AA (Batch 332): reclassification INTO defensive sectors (Materials / "
            "Utilities / Real Estate / Staples) + bearish trend. Defensive re-classification "
            "means low-multiple re-rating - continuation short setup. Rare event by design; "
            "defensive re-classifications are less common than growth."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_classification_change_to_defensive_wider_short: extend lookback to 2y + "
            "add Consumer Staples-adjacent Financials to target sector set. Preserves low-"
            "multiple re-rating alpha with broader defensive coverage."
        ),
    },
    "classification_change_volume_long": {
        "cluster_id": "CLASSIFICATION_CHANGE_PATTERN_AA",
        "owner_review_notes": (
            "PATTERN AA (Batch 335): recent reclassification + volume spike confirming "
            "market notice (Lo-Wang 2000 volume price discovery). Rare event by design + "
            "volume gate compounds rarity."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_classification_change_volume_wider_long: extend lookback to 2y + LOOSEN "
            "vol gate from vol_spike_2x to vol_above_avg. Preserves volume-confirmation "
            "thesis while allowing more fires. Companion to strat_classification_change_"
            "recent_2y_long."
        ),
    },
    "classification_change_momentum_long": {
        "cluster_id": "CLASSIFICATION_CHANGE_PATTERN_AA",
        "owner_review_notes": (
            "PATTERN AA (Batch 335): reclassification + MACD bullish (momentum confirmation "
            "per Chen-Chen 2010). Rare event by design + MACD state gate compounds rarity."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_classification_change_momentum_wider_long: extend lookback to 2y + "
            "LOOSEN MACD gate to ema_50_above_ema_200 (canonical trend). Preserves "
            "momentum-confirmation without the tight MACD state requirement."
        ),
    },
    "classification_change_from_tech_short": {
        "cluster_id": "CLASSIFICATION_CHANGE_PATTERN_AA",
        "owner_review_notes": (
            "PATTERN AA (Batch 335): symmetric inverse of to_tech long. Ticker moved OUT "
            "of growth sector + bearish trend. Rare event by design. Also carries SHORT-"
            "side asymmetric expectancy per feedback_structural_symmetry_not_economic_"
            "symmetry."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B. Also queue for economic-"
            "symmetry audit post-cube per feedback_structural_symmetry."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_classification_change_from_growth_wider_short: extend lookback to 2y "
            "+ mirror of to_growth_wider_long. Note asymmetric expectancy risk."
        ),
    },
    "classification_change_breakout_long": {
        "cluster_id": "CLASSIFICATION_CHANGE_PATTERN_AA",
        "owner_review_notes": (
            "PATTERN AA (Batch 335): recent reclassification + post-break retest. "
            "Institutional-sponsorship signature of re-rating-driven breakout. Rare event "
            "by design + retest gate (rare event itself) = doubly rare."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_classification_change_breakout_wider_long: extend lookback to 2y + "
            "LOOSEN retest gate to any_donchian_20_breakout (drops the retest requirement). "
            "Preserves reclassification + technical-confirmation thesis without doubling "
            "rare-event compounding."
        ),
    },
    "classification_change_with_institutional_long": {
        "cluster_id": "CLASSIFICATION_CHANGE_PATTERN_AA",
        "owner_review_notes": (
            "PATTERN AA (Batch 337): re-rating + institutional accumulation. Brogaard-"
            "Heath-Saadi 2019 + Cohen-Frazzini-Malloy 2008. Highest-conviction re-rating "
            "signal but rare event x rare institutional-cluster = doubly rare."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_classification_change_with_institutional_wider_long: extend "
            "reclassification lookback to 2y + LOOSEN institutional_cluster gate to "
            "institutional_positive (broader smart-money signal). Preserves both "
            "confluences with less strict thresholds."
        ),
    },
    "classification_change_with_insider_long": {
        "cluster_id": "CLASSIFICATION_CHANGE_PATTERN_AA",
        "owner_review_notes": (
            "PATTERN AA (Batch 337): re-rating + insider cluster. Cohen-Malloy-Pomorski "
            "2012 insider signal. Similar doubly-rare compounding as institutional variant."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_classification_change_with_insider_wider_long: extend "
            "reclassification lookback to 2y + LOOSEN insider_cluster gate to "
            "any_insider_buy_last_90d (broader insider signal). Preserves the confluence "
            "thesis with more available fires."
        ),
    },
    "classification_change_oversold_long": {
        "cluster_id": "CLASSIFICATION_CHANGE_PATTERN_AA",
        "owner_review_notes": (
            "PATTERN AA (Batch 337): re-rating at oversold + RSI < 35 + above 200-EMA. "
            "Early-entry mean-reversion post-reclassification. Rare event x RSI condition "
            "= rare fires."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_classification_change_oversold_wider_long: extend reclassification "
            "lookback to 2y + LOOSEN RSI < 35 to RSI < 45 (wider oversold band). "
            "Preserves early-entry thesis while allowing more fires."
        ),
    },
}


def main() -> int:
    csv_path = Path("output_batch_A_150/phase_1_quiet_fire_investigation.csv")
    df = pd.read_csv(csv_path)

    # Add new columns if not present
    for col in ("cluster_id", "owner_review_notes", "recommendation",
                "priority", "exploratory_loose_variant"):
        if col not in df.columns:
            df[col] = ""

    # Update rows for Turn 1 analyzed strategies
    updated = 0
    for strat, data in TURN_1_ANALYSIS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found in CSV")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    df.to_csv(csv_path, index=False)
    print(f"Turn 1 complete: updated {updated} rows in {csv_path}")
    print()
    print("=== Turn 1 summary ===")
    print(f"Analyzed strategies: {list(TURN_1_ANALYSIS.keys())}")
    print(f"Clusters covered: {sorted(set(d['cluster_id'] for d in TURN_1_ANALYSIS.values()))}")
    print(f"Remaining unanalyzed: {192 - updated} of 192 rows")

    return 0


if __name__ == "__main__":
    sys.exit(main())
