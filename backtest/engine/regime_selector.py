"""Regime SELECTOR + VIX-conditional sizing overlay.

Batch 203 (2026-05-17 owner-approved per Phase 1A-beta research review).
Addresses two findings from the deep-research analysis:

1. AMH critique (Andrew Lo, Adaptive Markets Hypothesis, SSRN 602222):
   the system has a regime TAG but no regime SELECTOR. Year-by-year
   sum-PnL (-117 / +43 / +517 / +792 / -27 pp by year) shows strong
   regime-coupling but no mechanism to route strategies to their fit
   regime. This module adds STRATEGY_REGIME_AFFINITY + selector gate.

2. VIX-conditional sizing overlay (Cederburg, Johnson, Maio 2024
   "VIX-managed portfolios" Finance Research Letters): monthly resize
   of equity exposure by prior-month VIX returns 9%->12%, vol 20%->16%,
   max DD 56%->29%, Sharpe +71%. Pure overlay on top of existing tier
   sizing.

Design:
- The selector is opt-in per strategy via STRATEGY_REGIME_AFFINITY.
  Strategies WITHOUT an entry default to "allow all regimes" so existing
  behavior is preserved on day-1; owner populates affinity after each
  Phase 1B-alpha tuning cycle.
- The selector composes with the existing BUG-34 STRATEGY_REGIME_BLOCKLIST
  (config.py): blocklist is a HARD exclusion, affinity is a SOFT
  preference encoded as allowed-regime set. Both must permit for entry.
- VIX sizing multiplier is bounded [0.3, 1.5] per Cederburg's risk-parity
  scaling spec; full-Kelly equivalence requires bounded exposure.

Cross-references: DEC-106 (multi-input regime score), DEC-150 (multi-asset
regime score), DEC-317 (hysteresis), DEC-388 (VIX SMA smoothing).
"""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np
import pandas as pd


# Strategy -> set of regimes in which the strategy is allowed to fire.
# Default behavior (strategy NOT in map) = allow all regimes. Empty set =
# block all regimes (effectively disabled). Owner populates from Phase
# 1B-alpha empirical results; Batch 203 initial values are derived from
# Phase 1A-beta carriers analysis (research report E section).
#
# Initial calibration rationale:
# - bollinger_lower / bollinger_tight: mean-reversion strategies. AMH +
#   Mag-7 dominance research suggests these struggle in mega-cap-driven
#   bull regimes (they fade winners). Allow in neutral/bear; block in bull
#   pending Phase 1B-alpha re-validation.
# - pivot_r1_breakout / pivot_r2_continuation: trend-continuation. Allow
#   in bull/neutral; block in bear/crisis where breakouts fail more.
# - williams_r_oversold / stochrsi_oversold / ultimate_oscillator:
#   Connors-style oversold strategies. Per Connors discipline, require
#   regime gate (price > 200-MA) which approximates allow-in-bull only.
#   Allow in bull/neutral, block in bear/crisis.
# - cpr_narrow_bullish: long-only narrow-range breakout. Allow in
#   bull/neutral; block in bear/crisis.
# - ichimoku_cloud_breakout: trend-continuation. Same as pivot family.
# - cmf_flip: volume-flow-driven; allow in all.
# - Short-side strategies (hull_rsi_short, etc.): allow in bear/crisis only.
#
# Conservative default: explicit affinity ONLY for strategies that fired
# in Phase 1A-beta (25 active). All inactive strategies retain default
# allow-all behavior so they can demonstrate edge before being gated.
# =============================================================================
# Batch 617 (2026-06-07) -- BATCH 271 FAMILY-BUG AUDIT (external-AI critique
# follow-up on the B608/B609/B610 walk series).
#
# AUDIT FINDING: of 62 dual (_strat3) strategies in screener.py, 40 had
# explicit STRATEGY_REGIME_AFFINITY entries that constrain BOTH directions
# identically. A `{bull, neutral}` entry on a dual strategy silently blocks
# the SHORT side from firing in bear/crisis (where short alpha lives);
# a `{bear}` entry symmetrically blocks the LONG side from bull/neutral.
# This is the Batch 271-era mass-edit signature - explicit single-direction
# regime sets were stamped onto dual strategies without direction-awareness,
# distorting per-regime PASS/FAIL for ~27 strategies for many batches.
#
# REMEDIATION SCOPE (CONSERVATIVE): B617 removes 19 clear Class A entries
# (LONG-bias `{bull,neutral}` or `{neutral,bear}` on dual where SHORT side
# is mis-regimed). The Batch 291 direction-aware default automatically
# applies LONG -> {bull, neutral} / SHORT -> {bear, crisis, neutral}
# correctly per direction once the explicit entry is removed.
#
# Removed in B617:
#   avwap_50_reclaim, bollinger_lower, cpr_narrow_bullish,
#   cpr_narrow_momentum, donchian_10_breakout, hull_rsi,
#   ichimoku_cloud_breakout, macd_crossover, mfi_oversold,
#   pivot_r1_breakout, pivot_r2_continuation, rsi_oversold,
#   smc_bos_continuation, smc_choch_reversal,
#   smc_liquidity_sweep_reversal, smc_order_block_bounce,
#   stoch_oversold, stochrsi_oversold, williams_r_oversold
#
# DEFERRED (kept with B617 audit comment; ~21 entries needing direction-
# disaggregated cube validation before removal):
#   B417 cube-derived single-bucket entries (awesome_oscillator, morning_star,
#   parabolic_sar_flip, ppo_crossover, tema_dema, williams_stoch_dual,
#   macd_fast_crossover, three_white_soldiers) - cube was direction-agnostic;
#   re-run direction-disaggregated cube before removal.
#   B418 cube-overrides (bollinger_tight, supertrend_macd, ultimate_oscillator,
#   adx_initiation, prev_day_high_break, avwap_252_breakout, cmf_flip,
#   force_index_breakout) - same caveat.
#   Counter-trend mean-reversion intentionals (pivot_s1/s2_bounce,
#   prev_day_low_bounce, camarilla_s3_bounce) - intent ambiguous; revisit.
# =============================================================================
STRATEGY_REGIME_AFFINITY: dict[str, set[str]] = {
    # Batch 252 (Phase 1C+ Wave 1 registrations 2026-05-20):
    # Chart patterns (DEC-355-362): allow bull/neutral; bear typically
    # invalidates Edwards-Magee setups
    "head_and_shoulders_bottom_long":   {"bull", "neutral"},
    # double_bottom_long: theoretical bottom-reversal works in bear, but
    # Stage C v3 empirical: 7 trades / 0% WR / -50 pp. Batch 293 tightening
    # removes bear; revisit if D1 evidence shows pattern works at scale.
    "double_bottom_long":               {"bull", "neutral"},
    "cup_and_handle_long":              {"bull", "neutral"},
    "flag_bull_long":                   {"bull", "neutral"},
    "triangle_ascending_long":          {"bull", "neutral"},
    # Index rebalance (DEC-370): event-driven; allow all regimes since
    # effect is index-flow-driven not market-momentum-driven.
    "post_inclusion_drift_long":        {"bull", "neutral", "bear", "crisis"},
    "post_inclusion_reversal_short":    {"bull", "neutral", "bear", "crisis"},
    "post_deletion_drift_short":        {"bear", "crisis", "neutral"},
    "pre_rebalance_long":               {"bull", "neutral", "bear", "crisis"},
    # Pairs trading (Batch 253 / DEC-369): mean-reversion fails in trending
    # markets; allow bull/neutral only per Krauss 2024.
    "pairs_mean_reversion_long":        {"bear"},  # Batch 418 cube override (was {bull, neutral}; bear=+0.28 Sharpe PASS, others negative)
    "pairs_mean_reversion_short":       {"bull", "neutral"},
    # News sentiment (Batch 253 / DEC-411): bull/neutral - sentiment momentum
    # tracks risk-on; bad-news cluster overwhelms in crisis.
    "news_sentiment_long":              {"bull", "neutral"},
    "news_sentiment_shift_long":        {"bull", "neutral"},
    # Calendar effects (Batch 254 / DEC-368): all-regime except crisis -
    # calendar anomalies don't survive stress regimes per literature.
    # Batch 293 (2026-05-21 owner-approved option 2): calendar effects
    # tightened to bull/neutral only. Stage C v3 empirical 2022 evidence
    # was small (totm_long: 17 trades, 12% WR, -77 pp;
    # halloween_seasonal: 3 trades, 0% WR, -23 pp).
    #
    # Batch 370 Fix 2 (owner-approved 2026-05-26): bear-regime narrowing
    # reversed. Methodologically symmetric with Batch 316a un-deprecation:
    # the Stage C v3 samples (3-17 trades) were too small to justify
    # a-priori pruning. Per memory directive "empirical validation over
    # literature pruning", let Phase-1A-beta at 1937-ticker scale produce
    # the verdict; if bear-regime calendar effects truly fail, the FAIL
    # verdict will codify the pruning with statistical power. Calendar
    # strategies were 0-trades in Phase-1A-beta because 56-67% of skips
    # were regime_affinity_block_bear; this Fix unblocks those for the
    # next 1A-beta re-run. Crisis NOT added per the original "calendar
    # premia presume risk-on" reasoning (full panic overrides seasonal).
    "totm_long":                        {"bull", "neutral", "bear"},
    "pre_holiday_long":                 {"bull", "neutral", "bear"},
    "january_effect_small_cap_long":    {"bull", "neutral", "bear"},
    "halloween_seasonal_long":          {"bull", "neutral", "bear"},
    # Cross-asset (Batch 254 / DEC-369): stress-regime activations preferred
    # for risk-off signals; DXY headwind works in all regimes.
    "risk_off_bond_equity_short":       {"bear", "crisis"},
    "vix_backwardation_long":           {"bear", "crisis"},
    "sector_rotation_defensive_long":   {"bear", "crisis"},
    "gold_silver_risk_off_long":        {"bear", "crisis"},
    "dxy_headwind_multinational_short": {"bull", "neutral", "bear", "crisis"},
    # Volume profile (Batch 255 / Batch 233 module): POC magnetism + Value
    # Area work in trending + range markets; break down in crisis (panic
    # selling overrides structure).
    "poc_magnet_long":                  {"bull", "neutral"},
    "value_area_breakout_long":         {"bull", "neutral"},
    "naked_poc_retest_long":            {"bull", "neutral"},
    # Mean-reversion: avoid bull (Mag-7 fade trap)
    # B617 REMOVED bollinger_lower {neutral,bear} - dual; SHORT side was
    # mis-regimed (couldn't fire in bull where mean-reversion-sell-at-top
    # belongs). Falls back to Batch 291 direction-aware default.
    "bollinger_tight":          {"bull"},  # B617 KEPT: B418 cube override; direction-disagg validation pending
    # B617 REMOVED stochrsi_oversold / williams_r_oversold / rsi_oversold /
    # mfi_oversold / stoch_oversold {bull,neutral} - all dual mean-reversion
    # strategies where SHORT side (overbought) was blocked from firing in
    # bear/crisis where it belongs. Falls back to Batch 291 default.
    "ultimate_oscillator":      {"bull"},  # B617 KEPT: B418 cube override; direction-disagg validation pending
    # Trend continuation: avoid bear/crisis
    # B617 REMOVED pivot_r1_breakout / pivot_r2_continuation /
    # cpr_narrow_bullish / ichimoku_cloud_breakout / macd_crossover /
    # donchian_10_breakout {bull,neutral} - all dual trend strategies where
    # SHORT side was mis-regimed. Falls back to Batch 291 default.
    "supertrend_macd":          {"bull"},  # B617 KEPT: B418 cube override; direction-disagg validation pending
    "adx_initiation":           {"bear"},  # B617 KEPT: B418 cube override; direction-disagg validation pending
    "prev_day_high_break":      {"bear"},  # B617 KEPT: B418 cube override; direction-disagg validation pending
    "52w_high_breakout":        {"bull", "neutral"},  # LONG-only (no _strat3 short side)
    # Counter-trend bounces: allow neutral/bear (oversold bounces)
    # B641 W3 (2026-06-09 owner-directed Tier 1 via external-AI audit
    # of B640 walk bundle): pivot_s1_bounce {neutral, bear} entry
    # DELETED -- B271 mass-edit single-direction-era family-bug. Strategy
    # is DUAL via _strat3; entry capped BOTH directions. LONG mis-regimed
    # (bull excluded despite valid buy-the-dip-in-uptrend reading); SHORT
    # mis-regimed (should be {bear, crisis, neutral} per B291 default).
    # Same fix pattern as B608/B609/B617/B639.
    # B641 W4 (2026-06-09): pivot_s2_bounce {neutral, bear} entry
    # DELETED for same B271 family-bug reason. Per CHECKLIST (g)
    # sequence-or-split, W4 F1 (add shooting_star to SHORT OR) + F2
    # (docstring) + RSI<40 mislabel correction queued separately
    # (S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL) -- not bundled here.
    # B651 (2026-06-09 owner-directed external-AI critique #3b): expanded
    # from {neutral, bear, crisis} to all regimes. Pre-B643 the entry was
    # correct for "buy the crash day" (capitulation day only). Post-B643
    # the strategy buys the turn UP TO 5 days later via the lookback
    # window, by which point the regime classifier (especially post-B642
    # sticky-bear hysteresis) may still be reading bear/crisis or may
    # have transitioned to neutral/bull -- either way, blocking the
    # capitulation-LONG at the recovery moment is exactly the failure
    # mode the B643 redesign was supposed to fix. Permissive all-regimes
    # entry preserves fires across the transition window; safe because
    # the strategy is highly selective (FAIL_FIRE_STARVED to borderline
    # rate post-B650 vol_below_avg AND-gate).
    "pivot_s3_capitulation":    {"bull", "neutral", "bear", "crisis"},
    "prev_day_low_bounce":      {"neutral", "bear"},
    "camarilla_s3_bounce":      {"neutral", "bear", "crisis"},
    # Volume-flow: allow all (signal is regime-agnostic)
    "cmf_flip":                 {"bear", "neutral"},  # Batch 418 cube override (was {bull, neutral, bear, crisis}; bull negative + 0 crisis trades)
    "force_index_breakout":     {"bull", "neutral", "bear", "crisis"},
    # Batch 597 (2026-06-05 owner-directed Stage 4 walk of
    # volume_spike_breakout): REMOVED explicit allow-all entry. Now
    # uses Batch 291 direction-aware default - LONG -> {bull, neutral};
    # SHORT -> {bear, crisis, neutral}.
    # AVWAP family (Batch 208): allow all regimes; signal self-gates via
    # above_avwap_* + 200-EMA logic inside the strategy itself.
    "avwap_252_breakout":           {"bear", "neutral"},  # B617 KEPT: B418 cube override; direction-disagg validation pending
    # B617 REMOVED avwap_50_reclaim {bull, neutral} - dual; SHORT side
    # mis-regimed (avwap-rejection-from-above SHORT should fire in bear).
    # Falls back to Batch 291 direction-aware default.
    "avwap_20high_rejection_short": {"neutral", "bear", "crisis"},
    # PEAD family (Batch 209): event-driven; allow all regimes (signal
    # self-gates via within_pead_window + pead_*_surprise inside strategy).
    # Bernard-Thomas effect is documented robust across regimes.
    "pead_long":                    {"bear", "bull"},  # Batch 418 cube override (was all-4-regimes; neutral Sharpe lower + 0 crisis trades)
    "pead_short":                   {"bull", "neutral", "bear", "crisis"},
    # SMC / ICT family (Batch 210 + Batch 263 Class C tightening 2026-05-20):
    # Phase 1A-alpha showed SMC structural signals firing in WRONG regimes
    # cause significant losses (bear/crisis 20-22pct WR vs bull/neutral 33pct).
    # Tightened: structural strategies now bull/neutral only (matching
    # explicit-long/short pairs already restricted). The "regime-agnostic"
    # original framing was wishful per Quantum Algo 2026 but unsupported
    # by Phase 1A-alpha data.
    # B617 REMOVED smc_bos_continuation / smc_choch_reversal /
    # smc_order_block_bounce / smc_liquidity_sweep_reversal {bull,neutral} -
    # all dual SMC strategies where SHORT side was blocked from firing in
    # bear/crisis. Tightening rationale in 2026-05-20 comment block above
    # (Phase 1A-alpha SMC structural-short signals) referred to
    # SMC SHORT explicit-pairs (smc_bos_continuation_short etc.) and not the
    # dual entries; the dual constraint silently double-gated the dual SHORT
    # arms. Batch 291 direction-aware default applies the same
    # {bull, neutral} to dual LONG arm + {bear, crisis, neutral} to dual
    # SHORT arm - preserves the intent without the family-bug side-effect.
    # Cross-sectional factor (Batch 220): momentum top decile allow
    # bull/neutral; bottom decile short in bear/crisis; BAB long in
    # bull/neutral; momentum+low-IVOL combined allow all (filter is
    # self-gating).
    "xs_momentum_top_decile":           {"bull"},  # Batch 418 cube override (was {bull, neutral}; neutral Sharpe lower)
    "xs_momentum_bottom_decile_short":  {"bear", "crisis"},
    "xs_low_beta_long":                 {"bear", "bull"},  # Batch 418 cube override (was {bull, neutral}; cube bear=+0.14 + bull=+0.15)
    "xs_combined_momentum_low_ivol":    {"bull", "neutral", "bear"},
    # Event-driven + quality (Batch 222): insider clusters work across
    # all regimes (Cohen-Malloy-Pomorski 2012); quality factor long-
    # only in bull/neutral; PEAD+insider confirmation similarly long-bias.
    # Batch 263 Class C tightening: long-bias strategies should NOT fire
    # in crisis. Even strong smart-money signals (insider clusters) fail
    # in crisis regime (Phase 1A-alpha: 36 crisis trades at 22pct WR).
    "insider_cluster_long":                {"bull", "neutral", "bear"},
    "insider_cluster_with_director_long":  {"bull", "neutral", "bear"},
    "xs_quality_top_quintile_long":        {"bear"},  # Batch 418 cube override (was {bull, neutral}; bear=+0.31 Sharpe, bull lower)
    "xs_momentum_quality_combined":        {"bull", "neutral"},
    "pead_with_insider_confirmation_long": {"bull", "neutral", "bear"},  # Batch 263: drop crisis
    # Pre-FOMC + 8-K event-driven (Batch 224): allow long-bias regimes.
    # Lucca-Moench drift is documented robust through 2015; conditional
    # on bullish backdrop per Cieslak-Pang 2024.
    "pre_fomc_long_sleeve":                {"bear", "neutral"},  # Batch 418 cube override (was {bull, neutral}; bull Sharpe negative)
    "pre_fomc_quality_momentum_long":      {"bull", "neutral"},
    "buyback_8k_recent_long":              {"bull", "neutral"},
    # PO3 + multi-TF (Batch 217): self-gate via 200-EMA + weekly/monthly
    # biases; symmetric pairs get explicit regime restrictions.
    "po3_bullish":                  {"bull"},  # Batch 418 cube override (was {bull, neutral}; neutral Sharpe negative)
    "po3_bearish":                  {"bear", "crisis", "neutral"},  # Batch 271 expand
    "po3_htf_aligned_long":         {"bull"},  # Batch 418 cube override (was {bull, neutral}; neutral Sharpe negative)
    "po3_htf_aligned_short":        {"bear", "crisis", "neutral"},  # Batch 271 expand
    "htf_aligned_breakout_long":    {"bull", "neutral"},
    "htf_aligned_breakout_short":   {"bear", "crisis", "neutral"},  # Batch 271 expand
    "weekly_bias_pullback_long":    {"bull", "neutral"},
    "weekly_bias_pullback_short":   {"bear", "crisis", "neutral"},  # Batch 271 expand
    "monthly_bias_momentum_long":   {"bull", "neutral"},
    # SMC expansion (Batch 216 + Batch 271 short-affinity expansion):
    # all variants self-gate via 200-EMA; allow all regimes for symmetric
    # long/short pairs; restrict explicit-long to bull/neutral and
    # explicit-short to bear/crisis + neutral (Batch 271 - neutral added
    # since SMC structural-short signals self-gate via 200-EMA and price
    # action, and the prior bear/crisis-only restriction prevented all
    # firing during the neutral-dominant 4y backtest window).
    "smc_fvg_retest_long":          {"bull", "neutral"},
    "smc_fvg_retest_short":         {"bear", "crisis", "neutral"},
    "smc_inverse_fvg":              {"bull", "neutral", "bear"},  # Batch 263: drop crisis
    "smc_breaker_block_long":       {"bull", "neutral"},
    "smc_breaker_block_short":      {"bear", "crisis", "neutral"},
    "smc_mitigation_block_long":    {"bull", "neutral"},
    "smc_mitigation_block_short":   {"bear", "crisis", "neutral"},
    "smc_discount_long":            {"bull", "neutral"},
    "smc_premium_short":            {"bear", "crisis", "neutral"},
    "smc_ote_long":                 {"bull", "neutral"},
    "smc_ote_short":                {"bear", "crisis", "neutral"},
    "smc_equal_highs_sweep_short":  {"neutral", "bear", "crisis"},
    "smc_equal_lows_sweep_long":    {"bull", "neutral", "bear"},
    "smc_bos_retest_entry":         {"bull", "neutral", "bear", "crisis"},
    # ORB stocks-in-play (Batch 211 + Batch 271 expansion): allow long in
    # bull/neutral (Zarattini criterion + 200-EMA gate); short in bear /
    # crisis / neutral (Batch 271 added neutral per T1a forensic).
    "orb_stocks_in_play_long":      {"bull", "neutral"},
    "orb_stocks_in_play_short":     {"bear", "crisis", "neutral"},
    # Short-side: bear/crisis + neutral
    # Batch 271 (Tier 2 expansion of T1A_COMPREHENSIVE_REVIEW 2026-05-20):
    # T1a forensic showed `regime_affinity_block_neutral_batch203` blocking
    # 942/1212 hull_rsi_short candidates + 833/1083 cpr_narrow_momentum_short
    # candidates - the neutral regime was ~70% of the 4y window and these
    # shorts could not fire at all. The signals themselves self-gate via
    # technical conditions (e.g., RSI>70 for rsi_overbought_short); the
    # regime affinity should not double-gate them out of the dominant
    # regime. Cross-asset signals (risk_off_bond_equity_short) NOT expanded
    # because their signals are regime-defined (TLT/SPY ratio rising =
    # risk-off regime).
    "bollinger_upper_short":    {"bear", "crisis", "neutral"},
    "rsi_overbought_short":     {"bear", "crisis", "neutral"},
    "stochrsi_overbought_short":{"bear", "crisis", "neutral"},
    "macd_crossover_short":     {"bear", "crisis", "neutral"},
    "ichimoku_cloud_breakdown": {"bear", "crisis", "neutral"},
    "hull_rsi_short":           {"bear", "crisis", "neutral"},
    "parabolic_sar_flip_short": {"bear", "crisis", "neutral"},
    "supertrend_macd_short":    {"bear", "crisis", "neutral"},
    "donchian_breakdown_short": {"bear", "crisis", "neutral"},
    # evening_star_short entry DELETED Batch 639 (2026-06-09) - strategy
    # deleted from screener.py same batch as redundant with
    # strat_morning_star SHORT post option-2 reconciliation. Entry would
    # become dangling.
    "shooting_star_short":      {"bear", "crisis", "neutral"},
    "camarilla_rsi_obv_short":  {"bear", "crisis", "neutral"},
    "cpr_narrow_momentum_short":{"bear", "crisis", "neutral"},
    "52w_low_breakdown":        {"bear", "crisis", "neutral"},
    "death_cross_50_200_volume":{"bear", "crisis", "neutral"},
    "prev_day_low_breakdown":   {"bear", "crisis", "neutral"},

    # ----- Batch 417 (2026-05-28 owner-approved) -----
    # Cube-derived per-regime affinity for 14 strategies that had NO prior
    # entry in this map. Per-regime Sharpe + n>=30 computed from
    # output_batch395_final/trade_exit_detail.csv x trade_log.csv merge;
    # regimes INCLUDED iff sharpe > 0 AND n >= 30.
    #
    # Source: scripts/optimize_strategies_from_cube.py Dim C output +
    # ad-hoc per-(strategy x regime) verdict computed from the AWS cube
    # 2026-05-28. Owner approved "14 NEW only" scope (no overrides of
    # existing 113 curated entries from Batches 203/293/370).
    #
    # The 15 OVERRIDE candidates (where cube disagrees with existing
    # entry) were intentionally NOT applied this batch - those need
    # per-strategy review since they reverse owner curation. See commit
    # message for the override list + cube-vs-existing diff.
    #
    # Per-strategy cube Sharpe (per regime; only INCLUDED regimes shown):
    #   awesome_oscillator                bear=+0.05
    #   break_retest_confluence           bull=+0.11
    #   break_retest_volume               bear=+0.07  neutral=+0.42
    #   cpr_narrow_momentum               bull=+0.06  neutral=+0.42
    #   hull_rsi                          bull=+0.08  neutral=+0.27
    #   institutional_buy_momentum_long   bull=+0.12
    #   institutional_cluster_long        bear=+0.16
    #   macd_fast_crossover               bull=+0.12
    #   morning_star                      bear=+0.13
    #   parabolic_sar_flip                bear=+0.16
    #   ppo_crossover                     bear=+0.05
    #   tema_dema                         bear=+0.18
    #   three_white_soldiers              bear=+0.06  bull=+0.08
    #   williams_stoch_dual               bear=+0.06
    "awesome_oscillator":              {"bear"},
    # Batch 609 F1 (2026-06-07 owner-directed break_retest_confluence walk):
    # removed `break_retest_confluence: {"bull"}` explicit entry - strategy
    # is DUAL but the entry capped BOTH directions to bull-only since
    # Batch 271 mass-edit. LONG was over-restricted (couldn't fire in
    # neutral); SHORT was mis-regimed (firing in bull = wrong). Now falls
    # back to Batch 291 direction-aware default (LONG -> {bull, neutral};
    # SHORT -> {bear, crisis, neutral}). Same fix pattern as B608 F1.
    # Batch 608 F1 (2026-06-07 owner-directed break_retest_volume walk):
    # removed `break_retest_volume: {"bear", "neutral"}` explicit entry -
    # strategy is DUAL but the entry capped LONG side to short-bias regimes
    # which silently mis-regimed long fires since Batch 271 mass-edit. Now
    # falls back to Batch 291 direction-aware default
    # (LONG -> {bull, neutral}; SHORT -> {bear, crisis, neutral}).
    # B617 REMOVED cpr_narrow_momentum + hull_rsi {bull, neutral} - both
    # dual; SHORT side mis-regimed. B417 cube source comment lists
    # bull/neutral Sharpe but cube was direction-agnostic; direction-
    # disaggregated re-run pending.
    "institutional_buy_momentum_long": {"bull"},
    "institutional_cluster_long":      {"bear"},
    "macd_fast_crossover":             {"bull"},
    # morning_star entry DELETED Batch 639 (2026-06-09 owner-directed walk
    # F3) - strategy is DUAL via _strat3 but explicit {bear} entry capped
    # BOTH directions; LONG side (post-B639 option-2 reconciliation =
    # morning_star + rsi<45) literally never fires under bear-only gate
    # since Nison bottom reversal pattern doesn't form mid-bear-trend
    # continuation. SHORT side over-restricted vs B291 default
    # {bear,crisis,neutral}. Same family-bug pattern as B608/B609/B617
    # B271 mass-edit dual entries. Now falls back to B291 direction-aware
    # default (LONG -> {bull,neutral}; SHORT -> {bear,crisis,neutral}).
    "parabolic_sar_flip":              {"bear"},
    "ppo_crossover":                   {"bear"},
    "tema_dema":                       {"bear"},
    "three_white_soldiers":            {"bear", "bull"},
    "williams_stoch_dual":             {"bear"},
}


def should_strategy_fire_in_regime(
    strategy: str,
    regime: str,
    affinity: Optional[dict] = None,
    direction: Optional[str] = None,
) -> bool:
    """Return True if the strategy is permitted to fire in the current regime.

    Logic:
      - If strategy is NOT in affinity map and direction is supplied ->
        apply direction-aware default (Batch 291 owner-approved option B):
          long-bias strategies default to {bull, neutral}
          short-bias strategies default to {bear, crisis, neutral}
        Avoid direction defaults to allow-all (treated as informational).
      - If strategy is NOT in affinity map and direction NOT supplied ->
        legacy allow-all behavior (preserves backward-compat for callers
        that haven't been updated to pass direction).
      - If strategy IS in affinity map -> only fire if regime is in the
        allowed set.
      - 'unknown' regime always blocks (fail-closed per DEC-316).
      - Strategy with affinity == empty set blocks all regimes (effective
        disable).

    Batch 291 (2026-05-21 owner-approved option B per Stage C v2 forensic):
    Stage C v2 showed 25 long trades fired in correctly-classified BEAR
    regime in 2022, contributing -133 pp. Root cause: many long strategies
    (hull_rsi, cpr_narrow_momentum, supertrend_ichimoku_adx, macd_*) had
    NO entry in STRATEGY_REGIME_AFFINITY -> defaulted to allow-all -> fired
    in bear despite being long-bias. The direction-aware default flips
    the safety bias to "long-bias defaults to {bull, neutral}, short-bias
    defaults to {bear, crisis, neutral}" instead of allow-all.

    Composes with BUG-34 STRATEGY_REGIME_BLOCKLIST at the engine call
    site (engine/backtest.py); both must permit for the entry to fire.
    """
    if regime == "unknown":
        return False
    mapping = affinity if affinity is not None else STRATEGY_REGIME_AFFINITY
    if strategy not in mapping:
        # Batch 291: direction-aware default instead of legacy allow-all.
        if direction == "long":
            return regime in {"bull", "neutral"}
        if direction == "short":
            return regime in {"bear", "crisis", "neutral"}
        # No direction passed -> preserve legacy allow-all behavior.
        return True
    return regime in mapping[strategy]


def vix_percentile_sizing_multiplier(
    vix_today: Optional[float],
    vix_history: Optional[Sequence[float]],
    lookback_days: int = 252,
    min_mult: float = 0.3,
    max_mult: float = 1.5,
) -> float:
    """Cederburg-Johnson-Maio (2024) VIX-managed portfolio sizing.

    Computes a position-size multiplier from today's VIX vs a trailing
    distribution. Paper: monthly rebalance scales equity exposure
    inversely with VIX percentile, returning Sharpe +71% on US equity
    overlay backtest.

    Implementation matches their bounded inverse-percentile:
      - VIX in lowest decile (calm)  -> mult = max_mult (1.5x)
      - VIX in highest decile (panic) -> mult = min_mult (0.3x)
      - VIX at median                 -> mult = 1.0
      - Linear interpolation between

    Returns 1.0 (no-op) when vix_today or vix_history is missing /
    insufficient (caller falls back to existing tier sizing).

    Inputs:
      vix_today: today's VIX level
      vix_history: sequence of historical VIX values (typically last
        lookback_days trading days)
      lookback_days: history window (default 252 trading days = 1 yr)
      min_mult / max_mult: clamp bounds per Cederburg spec

    Returns float multiplier in [min_mult, max_mult].
    """
    if vix_today is None or vix_history is None:
        return 1.0
    arr = np.asarray([v for v in vix_history if v is not None], dtype=float)
    if len(arr) < max(20, lookback_days // 4):
        # Insufficient history (need at least 1 month of VIX data)
        return 1.0
    # Use most recent lookback_days
    if len(arr) > lookback_days:
        arr = arr[-lookback_days:]
    # Percentile of vix_today within trailing distribution
    percentile = float(np.sum(arr <= vix_today) / len(arr))  # 0..1
    # Inverse-percentile linear map: pct=0 -> max_mult, pct=1 -> min_mult
    mult = max_mult - (max_mult - min_mult) * percentile
    return float(max(min_mult, min(max_mult, round(mult, 4))))


def regime_position_count_cap(
    regime: str,
    bull_cap: int = 40,
    neutral_cap: int = 25,
    bear_cap: int = 15,
    crisis_cap: int = 10,
) -> int:
    """Regime-conditional position-count cap.

    Risk-management research (Lo AMH + Lopez de Prado) recommends tighter
    concurrent-position limits in adverse regimes. The current system
    has a static cap (25 per Batch 185); this function returns the
    regime-conditioned cap that engine/backtest.py can apply.

    Defaults match the research report E.3 recommendation:
      bull:    40 (full diversification)
      neutral: 25 (current default - balanced)
      bear:    15 (concentrated to high-conviction)
      crisis:  10 (minimum exposure)
      unknown: 5  (extreme fail-closed)
    """
    return {
        "bull":    bull_cap,
        "neutral": neutral_cap,
        "bear":    bear_cap,
        "crisis":  crisis_cap,
        "unknown": 5,
    }.get(regime, neutral_cap)
