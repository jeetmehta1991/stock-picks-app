"""Batch 597 (2026-06-05) -- Stage 4 walk of strat_volume_spike_breakout
(dual) per owner directives 2026-06-05.

Owner directives applied (answers A + C + D + E approved):
  (a) Added close_above_open + close_in_top_40pct_of_range (long) /
      close_below_open + close_in_bottom_40pct_of_range (short).
      Standardizes with the donchian family upgrades.
  (c) Loosened vol gate vol_spike_2x -> vol_spike_15x (>=1.5x).
      The 2.0x threshold was gating too many real breakouts.
  (d) Replaced cumulative-since-history above_vwap with Brian Shannon
      (2022) anchored VWAP:
        LONG : above_avwap_20low (above AVWAP from recent 50-day
               swing low - upleg intact)
        SHORT: NOT above_avwap_20high (below AVWAP from recent
               20-day swing high - recent rally given back)
      NOTE: timeframe asymmetry (50 vs 20) - producer only emits
      {252low, 50low, 20high}; symmetric anchors would need new
      producer fields. Flagged for follow-up.
  (e) REMOVED explicit allow-all entry from STRATEGY_REGIME_AFFINITY.
      Strategy now uses Batch 291 direction-aware default
      (LONG -> {bull, neutral}; SHORT -> {bear, crisis, neutral}).

Skipped: (b) B592-style strong-breakout filter (would need new
producer signals); (f) MACD trend filter; (g) retest mirror gets its
own walk.

Pins:
  (1) LONG fires with all 5 new gates True
  (2) SHORT fires with all 5 new gates True
  (3) Legacy 3-gate fixture (dc20_breakout_up + vol_spike_2x +
      above_vwap) does NOT fire post-B597
  (4) vol_spike_2x alone (without vol_spike_15x) does NOT fire
      (B597 (c) verifies the vol-gate widening)
  (5) above_vwap alone (without above_avwap_20low) does NOT fire LONG
      (B597 (d) AVWAP swap verification)
  (6) Regime default LONG = {bull, neutral}; SHORT = {bear, crisis,
      neutral} -- strategy no longer in STRATEGY_REGIME_AFFINITY map
  (7) ALL_STRATEGIES count preserved at 218
"""
from __future__ import annotations

import pytest


def test_batch597_volume_spike_breakout_long_5_gates():
    """Pin (1)."""
    from backtest.signals.screener import strat_volume_spike_breakout
    s = {
        "dc20_breakout_up": True,
        "vol_spike_15x": True,
        "above_avwap_20low": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
    }
    out = strat_volume_spike_breakout(s)
    assert out["fires"] is True
    assert out["direction"] == "long"


def test_batch597_volume_spike_breakout_short_5_gates():
    """Pin (2)."""
    from backtest.signals.screener import strat_volume_spike_breakout
    s = {
        "dc20_breakout_dn": True,
        "vol_spike_15x": True,
        "below_avwap_20high": True,  # B612 refactor: positive signal
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    out = strat_volume_spike_breakout(s)
    assert out["fires"] is True
    assert out["direction"] == "short"


def test_batch597_legacy_3_gate_fixture_blocked():
    """Pin (3): legacy fixture (dc20_breakout_up + vol_spike_2x +
    above_vwap) does NOT fire post-B597."""
    from backtest.signals.screener import strat_volume_spike_breakout
    s_legacy = {
        "dc20_breakout_up": True,
        "vol_spike_2x": True,
        "above_vwap": True,
    }
    assert strat_volume_spike_breakout(s_legacy)["fires"] is False, (
        "B597 added 2 new gates + swapped 2 others; legacy fixture must not fire"
    )


def test_batch597_vol_gate_widened_15x_not_2x():
    """Pin (4): vol_spike_2x alone is now INSUFFICIENT - strategy now
    consumes vol_spike_15x (>=1.5x; vol_spike_2x being True does NOT
    imply vol_spike_15x is True in a synthetic dict)."""
    from backtest.signals.screener import strat_volume_spike_breakout
    s = {
        "dc20_breakout_up": True,
        "vol_spike_2x": True,
        "vol_spike_15x": False,  # below the NEW threshold
        "above_avwap_20low": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
    }
    assert strat_volume_spike_breakout(s)["fires"] is False, (
        "vol_spike_15x is the new gate; vol_spike_2x alone should not fire"
    )


def test_batch597_avwap_swap_above_vwap_alone_blocked():
    """Pin (5): legacy above_vwap signal alone (without above_avwap_20low)
    does NOT fire."""
    from backtest.signals.screener import strat_volume_spike_breakout
    s = {
        "dc20_breakout_up": True,
        "vol_spike_15x": True,
        "above_vwap": True,           # legacy signal True
        "above_avwap_20low": False,   # but new signal False
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
    }
    assert strat_volume_spike_breakout(s)["fires"] is False, (
        "B597 (d) swapped to AVWAP; legacy above_vwap alone should not fire"
    )


def test_batch597_regime_default_long_bull_neutral():
    """Pin (6) LONG: direction-aware default after explicit map
    entry was removed."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    assert "volume_spike_breakout" not in STRATEGY_REGIME_AFFINITY, (
        "B597 (e) removed allow-all entry"
    )
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime(
            "volume_spike_breakout", r, direction="long"
        ) is True
    for r in ["bear", "crisis"]:
        assert should_strategy_fire_in_regime(
            "volume_spike_breakout", r, direction="long"
        ) is False


def test_batch597_regime_default_short_bear_crisis_neutral():
    """Pin (6) SHORT."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime(
            "volume_spike_breakout", r, direction="short"
        ) is True
    assert should_strategy_fire_in_regime(
        "volume_spike_breakout", "bull", direction="short"
    ) is False


def test_batch597_all_strategies_count_post_b599():
    """Pin (7): subsequent batches added; current count 221."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 220
