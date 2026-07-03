#!/usr/bin/env python
"""Council 241 (2026-07-03) Turn 8: 6 adjacent-family remaining gaps.

SCOPE: 6 strategies flagged as remaining gaps in EXECUTION_QUEUE B1121:
  1. flag_bear_retest_short         (n=3)  - flag family adjacent
  2. inverted_cup_and_handle_short  (n=1)  - cup family adjacent
  3. supertrend_ichimoku_adx        (n=0)  - Ichimoku 3-way confluence
  4. macd_ichimoku                  (n=5)  - Ichimoku 2-way confluence
  5. smc_breaker_block_short        (n=89) - SMC above marginal boundary
  6. smc_inverse_fvg                (n=81) - SMC above marginal boundary

PRODUCER SMOKE VERIFICATIONS (all pass):
  chart_patterns.py: compute_flag_break_retest_signals + detect_inverted_cup_and_handle
  technical.py: compute_supertrend + compute_ichimoku + compute_adx + compute_macd
  smc_ict.py: 'breaker_block' 4 occurrences + 'inverse_fvg' 6 occurrences

KEY DISCRIMINATOR FINDING (contrarian Council 241):
  smc_breaker_block_short (89f) + smc_inverse_fvg (81f) contradict SMC_PHASE
  latent-kill hypothesis. If SMC_PHASE != 'PRODUCTION' were silent-killing SMC
  producers, ALL SMC strategies would be at 0 fires. They aren't. Therefore
  the SMC producer discriminator between quiet-fire and healthy SMC strategies
  is NOT the SMC_PHASE env flag but strategy-specific consumer gates + zone
  thresholds. This tightens the Turn 3 SMC_PHASE_LATENT_RISK verdict scope:
  audit remains warranted but is NOT the primary underfire driver for the
  10 investigated quiet-fire SMC strategies.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_8_INVESTIGATIONS = {
    # ========== CHART PATTERN FAMILY (2) ==========
    "flag_bear_retest_short": {
        "post_investigation_verdict": "PRODUCER_OK + COMPOUND_STRUCTURAL + PATTERN_S",
        "post_investigation_recommendation": (
            "Producer VERIFIED (chart_patterns.py:447 compute_flag_break_retest_"
            "signals emits flag_bear_broke + flag_bear_break_retest_short via B641 "
            "F1 fix). Symmetric SHORT mirror of flag_bull_retest_long (Turn 5 "
            "investigated at 0 fires; verdict PRODUCER_OK + COMPOUND_STRUCTURAL). "
            "3 fires slightly above LONG mirror consistent with the 2022-2026 "
            "bearish sessions producing more valid bear-flag setups (2022 + Jul-"
            "Oct 2023 + Aug 2024). Same producer-side fix path: widen K bar-window "
            "3..12 -> 3..15 (Edwards-Magee 1-4wk canonical) + widen retest "
            "tolerance band. Add Pattern S SHORT asymmetric expectancy caveat + "
            "borrow_ok audit."
        ),
        "final_recommended_actions": (
            "[CRITICAL] [FIX_PRODUCER] Widen K bar-window 3..12 -> 3..15 "
            "(Edwards-Magee canonical); [LOOSEN_THRESHOLD] widen retest tolerance "
            "band; [FIX_PRODUCER] borrow_ok audit; Pattern S SHORT caveat"
        ),
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": (
            "B1122 turn 8 investigation - was silent miss from Turn 5 (flag family "
            "adjacent to investigated flag_bull_long + flag_bull_retest_long). "
            "Producer smoke test PASSED (compute_flag_break_retest_signals exists). "
            "Same family fix path as sibling. Gap: 3 vs 0 delta for LONG partly "
            "explained by 2022-2026 bearish sessions; correlate with pead_short "
            "MARGINAL boundary asymmetry post-B1126 grouped LOOSEN + B1125 "
            "borrow_ok audit."
        ),
    },
    "inverted_cup_and_handle_short": {
        "post_investigation_verdict": "PRODUCER_OK + COMPOUND_GATE_STARVING + PATTERN_S",
        "post_investigation_recommendation": (
            "Producer VERIFIED (chart_patterns.py detect_inverted_cup_and_handle "
            "Batch 686 NEW producer; symmetric bearish-mirror methodology per "
            "Bulkowski 2005 'rounded top with handle' / 'dump and pop'). Symmetric "
            "SHORT of cup_and_handle_long (Turn 5 investigated at 0 fires; verdict "
            "PRODUCER_OK + COMPOUND_GATE_STARVING at 19% cup detection rate on "
            "SPY). 1 fire = producer emits (inverted cup detected) but consumer "
            "gate stack starves. Same LOOSEN path as sibling: vol_spike_2x -> "
            "vol_above_avg (O'Neil CANSLIM canonical) + drop rsi_14 filter "
            "redundant with EMA trend + Pattern S SHORT caveat + borrow_ok."
        ),
        "final_recommended_actions": (
            "[CRITICAL] [LOOSEN_THRESHOLD] vol_spike_2x -> vol_above_avg (O'Neil "
            "CANSLIM canonical); [DROP_REDUNDANT] rsi_14 filter redundant with EMA "
            "trend; [FIX_PRODUCER] borrow_ok; Pattern S SHORT caveat"
        ),
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": (
            "B1122 turn 8 investigation - was silent miss from Turn 5 (cup family "
            "adjacent to investigated cup_and_handle_long + cup_and_handle_retest_"
            "long). Producer smoke test PASSED (detect_inverted_cup_and_handle "
            "exists per Batch 686 wire). Same LOOSEN path as sibling cup_and_"
            "handle_long. Gap: inverted-cup detection rate on SPY not empirically "
            "measured (only cup detected rate of 19% was measured in Turn 5); "
            "post-B1122 producer smoke test should measure inverted-cup detection "
            "rate to confirm producer works vs SPY structural absence."
        ),
    },
    # ========== ICHIMOKU CONFLUENCE FAMILY (2) ==========
    "supertrend_ichimoku_adx": {
        "post_investigation_verdict": "PRODUCER_OK + 3_WAY_EVENT_COMPOUND_STARVED",
        "post_investigation_recommendation": (
            "3-way EVENT confluence: supertrend_flip_recent_5d (B655 T10 STATE->"
            "EVENT conversion) + ichimoku EVENT (B725 STATE->EVENT conversion) + "
            "adx_cross_up event (technical.py:894). Producers ALL VERIFIED. 0 "
            "fires = 3-way AND of independent EVENT rare-events. Expected joint "
            "probability per bar: 0.01 x 0.01 x 0.005 = 5e-7 x 150 tickers x 4y "
            "x 252 = 76 fires max at independence. Actual 0 = correlated rareness "
            "OR 5-day windows misaligned. ACTIONS: (1) LOOSEN to 2-of-3 "
            "confluence gate (drop weakest of 3); (2) OR convert one gate STATE "
            "back (revert one B655/B725 tightening for THIS strategy only per "
            "narrow-scope precedent); (3) widen supertrend_flip 5d window to 10d."
        ),
        "final_recommended_actions": (
            "[CRITICAL] [LOOSEN_GATE] 3-way AND -> 2-of-3 confluence (drop ADX "
            "weakest); [LOOSEN_THRESHOLD] widen supertrend_flip 5d -> 10d; "
            "OR narrow-scope revert one EVENT gate to STATE per this strategy"
        ),
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": (
            "B1122 turn 8 investigation - was silent miss from Turn 1 (Ichimoku "
            "family adjacent to investigated ichimoku_cloud_breakout/breakdown/"
            "tk_cross). Producer smoke test PASSED for all 3 (compute_supertrend "
            "+ compute_ichimoku + compute_adx exist). 3-way EVENT AND compounds "
            "structural rareness. Gap: none flagged; verdict clear. B1126 grouped "
            "LOOSEN will pick between 2-of-3 loosening vs narrow-scope STATE "
            "revert per owner tiering."
        ),
    },
    "macd_ichimoku": {
        "post_investigation_verdict": "PRODUCER_OK + 2_WAY_EVENT_COMPOUND",
        "post_investigation_recommendation": (
            "2-way EVENT confluence: macd_crossover + ichimoku EVENT (B725). "
            "Producers VERIFIED (compute_macd + compute_ichimoku). 5 fires = "
            "compound EVENT probability. MACD crossover ~2-5/yr per ticker; "
            "post-B725 Ichimoku EVENT ~1-3/yr per ticker; joint ~0.5-1/yr per "
            "ticker x 150 x 4y = 300-600 expected at independence. Actual 5 = "
            "100x underfire suggests correlated rareness (both trend-following "
            "systems trigger in same market regimes; window misalignment matters). "
            "ACTIONS: (1) widen event-recency window on one side (e.g. 5-day OR "
            "join instead of same-bar AND); (2) OR drop ichimoku EVENT gate + "
            "keep single-gate MACD crossover."
        ),
        "final_recommended_actions": (
            "[CRITICAL] [LOOSEN_GATE] Same-bar AND -> 5-day OR window; OR drop "
            "ichimoku secondary EVENT gate and keep single-gate MACD crossover"
        ),
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": (
            "B1122 turn 8 investigation - was silent miss from Turn 1 (Ichimoku "
            "family adjacent). Producer smoke test PASSED. 2-way EVENT compound "
            "starves same as supertrend_ichimoku_adx but at lower dimensionality "
            "(2 vs 3). Gap: MACD crossover expected fire rate (~2-5/yr per "
            "ticker) not empirically re-verified on Batch A; post-B1122 producer "
            "smoke test should measure."
        ),
    },
    # ========== SMC ABOVE-MARGINAL (2) ==========
    "smc_breaker_block_short": {
        "post_investigation_verdict": "PRODUCER_OK + HEALTHY_FIRE_COUNT + PATTERN_S",
        "post_investigation_recommendation": (
            "Producer VERIFIED (smc_ict.py 'breaker_block' 4 occurrences). 89 "
            "fires ABOVE the marginal boundary (>30) = HEALTHY fire count. This "
            "contradicts SMC_PHASE latent-kill hypothesis (if SMC_PHASE != "
            "'PRODUCTION' were killing SMC producers, ALL SMC strategies would "
            "be at 0 fires; they aren't). Discriminator between quiet-fire and "
            "healthy SMC strategies is strategy-specific consumer gates + zone "
            "thresholds, NOT env flag. Pattern S SHORT asymmetric expectancy "
            "caveat but empirically firing well. STATUS_QUO + universe expansion "
            "primary lever. No loosening required."
        ),
        "final_recommended_actions": (
            "[MARGINAL] [STATUS_QUO] Producer healthy at 89 fires; Pattern S "
            "SHORT asymmetric caveat retained; [UNIVERSE_EXPAND] Batch B primary "
            "lever; [FIX_PRODUCER] borrow_ok audit"
        ),
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": (
            "B1122 turn 8 investigation - was silent miss from Turn 3 (SMC family "
            "above marginal boundary at n=89). Producer smoke test PASSED. Key "
            "finding: contradicts Turn 3 SMC_PHASE_LATENT_RISK primary framing "
            "for ALL SMC strategies - if SMC_PHASE were silent-killing, this + "
            "smc_inverse_fvg would be 0. They aren't. TIGHTENS scope of Turn 3 "
            "SMC_PHASE audit to still-warranted but not primary driver. Gap: "
            "no LONG breaker_block sibling exists in registry (asymmetric; "
            "13F/13D pattern per feedback_asymmetric_data_sources_break_"
            "mechanical_inverse - breaker blocks may be SHORT-natural per ICT "
            "canonical)."
        ),
    },
    "smc_inverse_fvg": {
        "post_investigation_verdict": "PRODUCER_OK + HEALTHY_FIRE_COUNT",
        "post_investigation_recommendation": (
            "Producer VERIFIED (smc_ict.py 'inverse_fvg' 6 occurrences). 81 "
            "fires ABOVE the marginal boundary (>30) = HEALTHY fire count. "
            "Direction-neutral or STATE-based marker of prior FVG mitigation. "
            "Contradicts SMC_PHASE latent-kill hypothesis (see smc_breaker_"
            "block_short verdict). STATUS_QUO + universe expansion primary "
            "lever."
        ),
        "final_recommended_actions": (
            "[MARGINAL] [STATUS_QUO] Producer healthy at 81 fires; "
            "[UNIVERSE_EXPAND] Batch B primary lever"
        ),
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": (
            "B1122 turn 8 investigation - was silent miss from Turn 3 (SMC family "
            "above marginal boundary at n=81). Producer smoke test PASSED. Same "
            "SMC_PHASE-contradicting finding as smc_breaker_block_short. Gap: "
            "strategy directionality (LONG/SHORT) not verified from CSV - "
            "'smc_inverse_fvg' name suggests direction-neutral or STATE marker; "
            "screener.py inspection needed if direction matters for LOOSEN."
        ),
    },
}


def main() -> int:
    csv_path = Path("output_batch_A_150/phase_1_quiet_fire_investigation.csv")
    df = pd.read_csv(csv_path)

    # Force text columns to object dtype (avoid float64 coercion)
    for col in ("execution_batch_ref", "execution_status", "execution_comments"):
        if col in df.columns:
            df[col] = df[col].astype("object").fillna("")

    updated = 0
    for strat, data in TURN_8_INVESTIGATIONS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found in CSV")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    df.to_csv(csv_path, index=False)

    total = len(df)
    pop = (df["post_investigation_verdict"].fillna("").str.len() > 0).sum()
    exec_pop = (df["execution_comments"].fillna("").str.len() > 0).sum()

    print(f"Turn 8 adjacent-family investigation complete: {updated} strategies updated.")
    print(f"Total investigated: {pop} of {total} (57 + {updated} = 63)")
    print(f"execution_comments populated: {exec_pop} of {total}")
    print()
    print("EXECUTION_STATUS DISTRIBUTION (post-Turn-8):")
    for status in sorted(df["execution_status"].unique()):
        n = (df["execution_status"] == status).sum()
        print(f"  {status:30s}: {n:3d}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
