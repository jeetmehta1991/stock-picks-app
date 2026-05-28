"""Batch 414 (2026-05-28 owner-approved): test-pin the 9 STRATEGY_EXIT_OVERRIDE
updates derived from the post-AWS Phase 1A-beta cube run.

Source attribution (per CHECKLIST #77):
  Cube data:  output_batch395_final/trade_exit_detail.csv (AWS merge)
  Optimizer:  scripts/optimize_strategies_from_cube.py (Batches 388 + 391)
  Lens A Dim D: per-strategy best-exit pairing.
  Owner directive 2026-05-28 selected "4-of-5 relaxed gate" threshold
  (n>=30, p<0.05 Bonferroni, t>=3.4, R:R>=2.0; PSR<0.95) further filtered
  by Batch 266 fire-rate guardrail (actual_fire_rate >= 0.95).

These 9 strategies pair with breakeven_plus_trail as the cube-empirical
winning exit. Test fails if any entry drifts off this mapping (preventing
silent revert) and if the count drifts (per
feedback_doc_count_drift_must_be_test_pinned).
"""
from __future__ import annotations

import pytest

from backtest.config import STRATEGY_EXIT_OVERRIDE


# Batch 414 cube-empirical winners
BATCH_414_BREAKEVEN_PLUS_TRAIL = {
    "bollinger_tight",
    "xs_momentum_top_decile",
    "monthly_bias_momentum_long",
    "xs_low_beta_long",
    "cmf_flip",
    "xs_quality_top_quintile_long",
    "pead_long",
    "pairs_mean_reversion_long",
    "adx_initiation",
}


@pytest.mark.parametrize("strategy", sorted(BATCH_414_BREAKEVEN_PLUS_TRAIL))
def test_batch414_strategy_exit_override_mapped_to_breakeven_plus_trail(
        strategy):
    """Each of the 9 cube-derived winners must point to breakeven_plus_trail."""
    assert strategy in STRATEGY_EXIT_OVERRIDE, (
        f"{strategy} missing from STRATEGY_EXIT_OVERRIDE - Batch 414 not "
        f"applied or reverted")
    cfg = STRATEGY_EXIT_OVERRIDE[strategy]
    assert cfg.get("exit_method") == "breakeven_plus_trail", (
        f"{strategy}: STRATEGY_EXIT_OVERRIDE.exit_method = "
        f"{cfg.get('exit_method')!r}, expected 'breakeven_plus_trail' "
        f"(Batch 414 cube-empirical winner)")


def test_batch414_strategy_exit_override_count_floor():
    """STRATEGY_EXIT_OVERRIDE must contain at least the 9 Batch 414 entries
    plus the 6 retained legacy entries (stochrsi_oversold, po3_bullish,
    avwap_50_reclaim, cpr_narrow_bullish, bollinger_lower, smc_choch_reversal,
    po3_bearish = 7 legacy after Batch 414 drops the 4 updated)."""
    # Floor: 9 Batch 414 + at least the explicit non-updated legacy entries
    assert len(STRATEGY_EXIT_OVERRIDE) >= 16, (
        f"STRATEGY_EXIT_OVERRIDE has {len(STRATEGY_EXIT_OVERRIDE)} entries, "
        f"expected >= 16 (9 Batch 414 + at least 7 legacy retained)")


def test_batch414_breakeven_plus_trail_is_dominant_exit():
    """After Batch 414, breakeven_plus_trail should be the most-used exit
    method across STRATEGY_EXIT_OVERRIDE (9 entries vs <= 4 for any other).
    Empirical signal from Lens B L1 + L2 of the cube."""
    from collections import Counter
    exits = Counter()
    for cfg in STRATEGY_EXIT_OVERRIDE.values():
        em = cfg.get("exit_method")
        if em:
            exits[em] += 1
    # breakeven_plus_trail is the dominant exit
    most_common_em, most_common_count = exits.most_common(1)[0]
    assert most_common_em == "breakeven_plus_trail", (
        f"Expected breakeven_plus_trail dominant in STRATEGY_EXIT_OVERRIDE; "
        f"got {most_common_em!r} with {most_common_count} entries. "
        f"Full distribution: {dict(exits)}")
    # And it should have at least 9 entries (Batch 414 minimum)
    assert most_common_count >= 9, (
        f"breakeven_plus_trail entry count = {most_common_count}, expected "
        f">= 9 (Batch 414 cube winners)")
