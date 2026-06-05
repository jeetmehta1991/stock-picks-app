"""Batch 595 (2026-06-05) -- Stage 4 walk for tight non-retest donchian
pair (donchian_breakout_long + donchian_breakdown_short) per owner
directives 2026-06-05:

  (a) APPROVED -- Restore long/short symmetry. B591 added bullish-bar
      + strong-close gates to donchian_breakout_long but NOT to
      donchian_breakdown_short. B595 brings the SHORT to parity:
        donchian_breakdown_short now requires close_below_open +
        close_in_bottom_40pct_of_range in addition to its original
        3 gates (dc10_breakout_dn + vol_spike_15x + NOT macd_bullish).
  (e) APPROVED -- Regime affinity via Batch 291 direction-aware default
      (LONG -> {bull, neutral}, SHORT -> {bear, crisis, neutral}).
      Neither strategy in STRATEGY_REGIME_AFFINITY map; default handles.

Pins:
  (1) donchian_breakdown_short LONG-side semantics unchanged (still
      short-only; _strat helper)
  (2) donchian_breakdown_short requires all 5 gates post-B595
  (3) donchian_breakdown_short blocked when bearish-bar missing
  (4) donchian_breakdown_short blocked when bottom-40pct missing
  (5) Long/short symmetry: donchian_breakout_long + donchian_breakdown
      _short have parallel 5-gate structure
  (6) donchian_breakout_long regime default (bull/neutral allowed;
      bear/crisis blocked)
  (7) donchian_breakdown_short regime default (bear/crisis/neutral
      allowed; bull blocked)
  (8) ALL_STRATEGIES count preserved at 218
"""
from __future__ import annotations

import pytest


def test_batch595_donchian_breakdown_short_5_gates_fires():
    """Pin (2): all 5 gates True -> fires short."""
    from backtest.signals.screener import strat_donchian_breakdown_short
    s = {
        "dc10_breakout_dn": True,
        "vol_spike_15x": True,
        "macd_12_26_9_bullish": False,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    out = strat_donchian_breakdown_short(s)
    assert out["fires"] is True
    assert out["direction"] == "short"


def test_batch595_donchian_breakdown_short_blocks_no_bearish_bar():
    """Pin (3): missing close_below_open -> no fire."""
    from backtest.signals.screener import strat_donchian_breakdown_short
    s = {
        "dc10_breakout_dn": True,
        "vol_spike_15x": True,
        "macd_12_26_9_bullish": False,
        "close_below_open": False,
        "close_in_bottom_40pct_of_range": True,
    }
    assert strat_donchian_breakdown_short(s)["fires"] is False


def test_batch595_donchian_breakdown_short_blocks_no_bottom_40pct():
    """Pin (4): missing strong-close bottom -> no fire."""
    from backtest.signals.screener import strat_donchian_breakdown_short
    s = {
        "dc10_breakout_dn": True,
        "vol_spike_15x": True,
        "macd_12_26_9_bullish": False,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": False,
    }
    assert strat_donchian_breakdown_short(s)["fires"] is False


def test_batch595_donchian_breakdown_short_legacy_3_gates_blocked():
    """Post-B595 the legacy 3-gate signal set (without bar/close gates)
    must NOT fire - confirms the symmetry tightening took effect."""
    from backtest.signals.screener import strat_donchian_breakdown_short
    s_legacy = {
        "dc10_breakout_dn": True,
        "vol_spike_15x": True,
        "macd_12_26_9_bullish": False,
        # close_below_open + close_in_bottom_40pct_of_range absent
    }
    assert strat_donchian_breakdown_short(s_legacy)["fires"] is False, (
        "B595 added gates - legacy 3-gate fixture must not fire"
    )


def test_batch595_pair_symmetry_5_vs_5_gates():
    """Pin (5): LONG and SHORT both fire with parallel 5-gate sets."""
    from backtest.signals.screener import (
        strat_donchian_breakout_long, strat_donchian_breakdown_short
    )
    s_long = {
        "dc10_breakout_up": True,
        "vol_spike_15x": True,
        "macd_12_26_9_bullish": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
    }
    s_short = {
        "dc10_breakout_dn": True,
        "vol_spike_15x": True,
        "macd_12_26_9_bullish": False,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    assert strat_donchian_breakout_long(s_long)["fires"] is True
    assert strat_donchian_breakdown_short(s_short)["fires"] is True


def test_batch595_regime_default_long_bull_neutral_only():
    """Pin (6): donchian_breakout_long regime default = {bull, neutral}."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    assert "donchian_breakout_long" not in STRATEGY_REGIME_AFFINITY
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime(
            "donchian_breakout_long", r, direction="long"
        ) is True
    for r in ["bear", "crisis"]:
        assert should_strategy_fire_in_regime(
            "donchian_breakout_long", r, direction="long"
        ) is False


def test_batch595_regime_short_bear_crisis_neutral():
    """Pin (7): donchian_breakdown_short fires in {bear, crisis, neutral}
    only - blocked in bull. Note: donchian_breakdown_short ALREADY has
    an explicit entry in STRATEGY_REGIME_AFFINITY = {bear, crisis,
    neutral} (legacy Batch 271 expansion); the explicit-map mechanism
    achieves the same SHORT-direction semantics as the Batch 291
    direction-aware default. Behavior validated below regardless of
    which mechanism applied."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    # Confirm the {bear, crisis, neutral} set holds regardless of source
    explicit = STRATEGY_REGIME_AFFINITY.get("donchian_breakdown_short")
    if explicit is not None:
        assert explicit == {"bear", "crisis", "neutral"}, (
            f"explicit affinity must be SHORT-canonical set; got {explicit}"
        )
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime(
            "donchian_breakdown_short", r, direction="short"
        ) is True
    assert should_strategy_fire_in_regime(
        "donchian_breakdown_short", "bull", direction="short"
    ) is False


def test_batch595_all_strategies_count_preserved_at_218():
    """Pin (8): no add/delete in B595; count unchanged."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 218
