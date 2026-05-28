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


def test_batch417_did_not_silently_override_existing_curated_entries():
    """Owner approved '14 NEW only' scope. The 15 OVERRIDE candidates (where
    cube disagreed with curated entries) MUST NOT have been touched in
    Batch 417. Pin them at their pre-Batch-417 values."""
    # Spot-check a few of the overrides that were intentionally NOT applied
    # (cube would have set these to different values).
    assert STRATEGY_REGIME_AFFINITY.get("adx_initiation") == {"bull", "neutral"}, (
        "Batch 417 must not override adx_initiation (cube said {bear}; "
        "owner deferred override to per-strategy review)")
    assert STRATEGY_REGIME_AFFINITY.get("bollinger_tight") == {"bull", "neutral"}, (
        "Batch 417 must not override bollinger_tight (cube said {bull}; "
        "owner deferred override)")
    assert STRATEGY_REGIME_AFFINITY.get("pairs_mean_reversion_long") == {"bull", "neutral"}, (
        "Batch 417 must not override pairs_mean_reversion_long (cube said "
        "{bear}; owner deferred override)")
    assert STRATEGY_REGIME_AFFINITY.get("xs_momentum_top_decile") == {"bull", "neutral"}, (
        "Batch 417 must not override xs_momentum_top_decile (cube said "
        "{bull}; owner deferred override)")
