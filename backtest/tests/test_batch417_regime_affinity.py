"""Batch 417 (2026-05-28 owner-approved): test-pin the 14 NEW
STRATEGY_REGIME_AFFINITY entries derived from the post-AWS Phase 1A-beta
cube run.

Source attribution (per CHECKLIST #77):
  Cube data: output_batch395_final/trade_exit_detail.csv x trade_log.csv
  Computation: per-(strategy x regime) Sharpe + n>=30 filter from the
  ad-hoc analysis in 2026-05-28 conversation log; regimes INCLUDED iff
  sharpe > 0 AND n >= 30.
  Owner approved "14 NEW only" scope: do NOT override the existing 113
  curated entries (from Batches 203/293/370 + literature) even where
  cube empirical disagrees. The 15 OVERRIDE candidates are deferred to
  per-strategy approval in a later batch.

These entries pin the cube-derived regime affinity for 14 strategies that
had NO prior entry. Test fails if any entry drifts (e.g., someone
silently reverts) or if the count drops below the expected floor.
"""
from __future__ import annotations

import pytest

from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY


# Batch 417 cube-empirical affinity (regime set per strategy)
BATCH_417_NEW_ENTRIES = {
    "awesome_oscillator":              {"bear"},
    "break_retest_confluence":         {"bull"},
    "break_retest_volume":             {"bear", "neutral"},
    "cpr_narrow_momentum":             {"bull", "neutral"},
    "hull_rsi":                        {"bull", "neutral"},
    "institutional_buy_momentum_long": {"bull"},
    "institutional_cluster_long":      {"bear"},
    "macd_fast_crossover":             {"bull"},
    "morning_star":                    {"bear"},
    "parabolic_sar_flip":              {"bear"},
    "ppo_crossover":                   {"bear"},
    "tema_dema":                       {"bear"},
    "three_white_soldiers":            {"bear", "bull"},
    "williams_stoch_dual":             {"bear"},
}


@pytest.mark.parametrize("strategy,expected_regimes",
                          sorted(BATCH_417_NEW_ENTRIES.items()))
def test_batch417_strategy_regime_affinity_entry(strategy, expected_regimes):
    """Each Batch 417 NEW entry must be present + match cube-derived set."""
    assert strategy in STRATEGY_REGIME_AFFINITY, (
        f"{strategy} missing from STRATEGY_REGIME_AFFINITY - Batch 417 "
        f"not applied or silently reverted")
    actual = STRATEGY_REGIME_AFFINITY[strategy]
    assert actual == expected_regimes, (
        f"{strategy}: STRATEGY_REGIME_AFFINITY = {actual!r}, expected "
        f"{expected_regimes!r} (Batch 417 cube-empirical)")


def test_batch417_strategy_regime_affinity_count_floor():
    """STRATEGY_REGIME_AFFINITY must have at least 113 prior + 14 Batch 417
    = 127 entries. Floor (not exact) because future batches may add more."""
    assert len(STRATEGY_REGIME_AFFINITY) >= 127, (
        f"STRATEGY_REGIME_AFFINITY has {len(STRATEGY_REGIME_AFFINITY)} "
        f"entries, expected >= 127 (113 pre-Batch-417 + 14 Batch 417 new)")


# Batch 418 (2026-05-28 owner-approved "proceed"): 15 OVERRIDES of existing
# curated entries where cube empirical disagrees. Supersedes the prior
# test_batch417 "override-not-applied" guards; those entries are now the
# cube-derived values pinned below.
BATCH_418_OVERRIDES = {
    "adx_initiation":               {"bear"},
    "avwap_252_breakout":           {"bear", "neutral"},
    "bollinger_tight":              {"bull"},
    "cmf_flip":                     {"bear", "neutral"},
    "pairs_mean_reversion_long":    {"bear"},
    "pead_long":                    {"bear", "bull"},
    "po3_bullish":                  {"bull"},
    "po3_htf_aligned_long":         {"bull"},
    "pre_fomc_long_sleeve":         {"bear", "neutral"},
    "prev_day_high_break":          {"bear"},
    "supertrend_macd":              {"bull"},
    "ultimate_oscillator":          {"bull"},
    "xs_low_beta_long":             {"bear", "bull"},
    "xs_momentum_top_decile":       {"bull"},
    "xs_quality_top_quintile_long": {"bear"},
}


@pytest.mark.parametrize("strategy,expected_regimes",
                          sorted(BATCH_418_OVERRIDES.items()))
def test_batch418_strategy_regime_affinity_override(strategy, expected_regimes):
    """Each Batch 418 OVERRIDE must be present + match cube-derived set.
    These supersede prior Batch 203/293/370 curation per
    project_no_apriori_strategy_pruning (cube empirical supersedes literature).
    """
    assert strategy in STRATEGY_REGIME_AFFINITY, (
        f"{strategy} missing from STRATEGY_REGIME_AFFINITY - Batch 418 "
        f"override not applied or silently reverted")
    actual = STRATEGY_REGIME_AFFINITY[strategy]
    assert actual == expected_regimes, (
        f"{strategy}: STRATEGY_REGIME_AFFINITY = {actual!r}, expected "
        f"{expected_regimes!r} (Batch 418 cube-empirical override)")


def test_batch418_total_cube_derived_entries():
    """Total entries with explicit cube-derivation = 14 (Batch 417 NEW) + 15
    (Batch 418 OVERRIDES) = 29 distinct strategies whose affinity is now
    cube-empirical rather than literature-derived. Count-floor still applies."""
    cube_derived_count = len(BATCH_417_NEW_ENTRIES) + len(BATCH_418_OVERRIDES)
    assert cube_derived_count == 29, (
        f"Expected 14 + 15 = 29 cube-derived entries; got "
        f"{cube_derived_count}")
    # No collision between the two sets (Batch 417 NEW were not-prior-entries;
    # Batch 418 OVERRIDES were prior-entries being changed):
    overlap = set(BATCH_417_NEW_ENTRIES) & set(BATCH_418_OVERRIDES)
    assert not overlap, (
        f"Batch 417 NEW and Batch 418 OVERRIDE sets must be disjoint; "
        f"overlap = {overlap}")
