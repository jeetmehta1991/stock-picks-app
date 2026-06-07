"""Batch 596 (2026-06-05) -- Stage 4 walk for tight retest donchian pair
(donchian_breakout_retest_long + donchian_breakdown_retest_short) per
owner directives 2026-06-05.

Owner directives applied (answers A + B + C + E approved):
  (a) Restore long/short symmetry. SHORT was 3 gates; LONG had 5.
      Added close_below_open + close_in_bottom_40pct_of_range to SHORT.
  (b) Flip vol_spike_15x -> vol_below_avg in BOTH directions per
      Bulkowski 2005 thesis (retest forms on lower volume).
  (c) Replace standard resistance_break_retest / support_break_retest
      with the B594 LOCAL strong variants dc20_resistance_break_retest
      _strong / dc20_support_break_retest_strong (already-existing
      additive fields; no new producer code).
  (e) Regime affinity: rely on Batch 291 direction-aware default
      (LONG -> {bull, neutral}; SHORT -> {bear, crisis, neutral}).

CONVERGENCE FLAG: post-B596 the tight retest pair is FUNCTIONALLY
IDENTICAL to the long/short sides of donchian_20_breakout_retest (B594).
Same gate sets per direction. Surfaced for owner resolution in B596
end-of-turn summary.

Pins:
  (1) donchian_breakout_retest_long requires all 5 new gates post-B596
  (2) donchian_breakdown_retest_short requires all 5 new gates post-B596
  (3) Legacy 3-gate fixture no longer fires SHORT
  (4) Legacy vol_spike_15x alone no longer fires LONG
  (5) Convergence: tight LONG fires IFF donchian_20_breakout_retest
      LONG fires (same gate set)
  (6) Convergence mirror: tight SHORT fires IFF donchian_20_breakout
      _retest SHORT fires
  (7) Regime default LONG = {bull, neutral}; SHORT = {bear, crisis,
      neutral} (Batch 291 direction-aware default - neither in
      STRATEGY_REGIME_AFFINITY map)
  (8) ALL_STRATEGIES count preserved at 218
"""
from __future__ import annotations

import pytest


def test_batch596_breakout_retest_long_5_gates():
    """Pin (1): all 5 new gates True -> fires long."""
    from backtest.signals.screener import strat_donchian_breakout_retest_long
    s = {
        "dc20_resistance_break_retest_strong": True,
        "vol_below_avg": True,
        "macd_12_26_9_bullish": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
    }
    out = strat_donchian_breakout_retest_long(s)
    assert out["fires"] is True
    assert out["direction"] == "long"


def test_batch596_breakdown_retest_short_5_gates():
    """Pin (2): SHORT all 5 new gates True -> fires."""
    from backtest.signals.screener import strat_donchian_breakdown_retest_short
    s = {
        "dc20_support_break_retest_strong": True,
        "vol_below_avg": True,
        "macd_12_26_9_bearish": True,  # B612 refactor: positive signal
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    out = strat_donchian_breakdown_retest_short(s)
    assert out["fires"] is True
    assert out["direction"] == "short"


def test_batch596_short_legacy_3_gate_fixture_blocked():
    """Pin (3): legacy fixture (support_break_retest + vol_spike_15x +
    NOT macd_bullish, missing the new gates) does NOT fire post-B596."""
    from backtest.signals.screener import strat_donchian_breakdown_retest_short
    s = {
        "support_break_retest": True,
        "vol_spike_15x": True,
        "macd_12_26_9_bearish": True,  # B612 refactor: positive signal
    }
    assert strat_donchian_breakdown_retest_short(s)["fires"] is False, (
        "B596 replaced support_break_retest with _strong variant + "
        "vol_spike_15x with vol_below_avg; legacy fixture must not fire"
    )


def test_batch596_long_legacy_vol_spike_blocked():
    """Pin (4): vol_spike_15x alone (without vol_below_avg) does NOT
    fire post-B596 vol flip."""
    from backtest.signals.screener import strat_donchian_breakout_retest_long
    s = {
        "dc20_resistance_break_retest_strong": True,
        "vol_spike_15x": True,
        "vol_below_avg": False,
        "macd_12_26_9_bullish": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
    }
    assert strat_donchian_breakout_retest_long(s)["fires"] is False


def test_batch596_convergence_resolved_via_b599_deletion():
    """Pins (5)+(6) post-B599: convergence between the explicit pair and
    the dual strat_donchian_20_breakout_retest was the original
    finding. Owner picked Option 2 in B599 - delete the dual, keep
    the pair. Verify the dual is gone and the pair still fires under
    the post-B596 gate set."""
    from backtest.signals import screener
    from backtest.signals.screener import (
        strat_donchian_breakout_retest_long,
        strat_donchian_breakdown_retest_short,
    )
    assert not hasattr(screener, "strat_donchian_20_breakout_retest"), (
        "B599 deleted the dual; semantics live in the explicit pair"
    )
    # Pair still fires with the post-B596 5-gate set
    s_long = {
        "dc20_resistance_break_retest_strong": True,
        "vol_below_avg": True,
        "macd_12_26_9_bullish": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
    }
    assert strat_donchian_breakout_retest_long(s_long)["fires"] is True
    s_short = {
        "dc20_support_break_retest_strong": True,
        "vol_below_avg": True,
        "macd_12_26_9_bearish": True,  # B612 refactor: positive signal
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    assert strat_donchian_breakdown_retest_short(s_short)["fires"] is True


def test_batch596_regime_default_long_bull_neutral():
    """Pin (7) LONG side: direction-aware default."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    assert "donchian_breakout_retest_long" not in STRATEGY_REGIME_AFFINITY
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime(
            "donchian_breakout_retest_long", r, direction="long"
        ) is True
    for r in ["bear", "crisis"]:
        assert should_strategy_fire_in_regime(
            "donchian_breakout_retest_long", r, direction="long"
        ) is False


def test_batch596_regime_default_short_bear_crisis_neutral():
    """Pin (7) SHORT side: direction-aware default."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    assert "donchian_breakdown_retest_short" not in STRATEGY_REGIME_AFFINITY
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime(
            "donchian_breakdown_retest_short", r, direction="short"
        ) is True
    assert should_strategy_fire_in_regime(
        "donchian_breakdown_retest_short", "bull", direction="short"
    ) is False


def test_batch596_all_strategies_count_post_b599():
    """Pin (8) post-B599: B596 was net 0; B599 deleted dual -> 217.
    Subsequent batches: B603 +2 -> 219; B605 +1 -> 220; B607 +1 -> 221;
    B610 +1 -> 222; B611 -1 -> 221. Current count = 221."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 221
