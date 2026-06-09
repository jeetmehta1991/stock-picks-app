"""Batch 636 (2026-06-08) -- Stage 4 walk of strat_three_white_soldiers
per CHECKLIST #105. Class 7 NEW symmetric inverse wired same-turn:
strat_three_black_crows_short.

Source: backtest/signals/screener.py:strat_three_white_soldiers (B636
F2 docstring) + strat_three_black_crows_short (B636 F1 Class 7 NEW);
backtest/signals/technical.py:1479-1486 (Nison 1991 three_white
_soldiers + three_black_crows producer pair). Per CHECKLIST #77.

Owner-directed B option: F1 (Class 7 NEW SHORT mirror) + F2 (docstring).
Per `feedback_wire_new_strategies_on_the_spot`: Class 7 NEW wires
same-turn since producer signal `three_black_crows` already exists.

Pins:
  (1) strat_three_black_crows_short importable
  (2) SHORT fires with three_black_crows + RSI>40
  (3) SHORT blocked when RSI <= 40 (oversold cap)
  (4) SHORT blocked when three_black_crows is False
  (5) LONG (existing strat_three_white_soldiers) unchanged behavior
  (6) Registry: three_black_crows_short in ALL_STRATEGIES
  (7) Regime affinity default: SHORT -> {bear, crisis, neutral} per
      B291 direction-aware default (no explicit map entry)
  (8) ALL_STRATEGIES count = 222 post-B636
"""
from __future__ import annotations

import pytest


def test_batch636_three_black_crows_short_importable():
    """Pin (1)."""
    from backtest.signals.screener import strat_three_black_crows_short
    assert callable(strat_three_black_crows_short)


def test_batch636_short_fires_with_pattern_and_rsi_above_40():
    """Pin (2)."""
    from backtest.signals.screener import strat_three_black_crows_short
    s = {
        "three_black_crows": True,
        "rsi_14": 55,                    # > 40 floor
    }
    out = strat_three_black_crows_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch636_short_blocked_when_rsi_below_40():
    """Pin (3): RSI<=40 cap (mirror of LONG's RSI<60 cap; SHORT entry
    avoided when already oversold)."""
    from backtest.signals.screener import strat_three_black_crows_short
    s = {
        "three_black_crows": True,
        "rsi_14": 30,                    # < 40
    }
    assert strat_three_black_crows_short(s)["fires"] is False


def test_batch636_short_blocked_when_pattern_absent():
    """Pin (4): missing three_black_crows blocks."""
    from backtest.signals.screener import strat_three_black_crows_short
    s = {
        # three_black_crows ABSENT
        "rsi_14": 55,
    }
    assert strat_three_black_crows_short(s)["fires"] is False


def test_batch636_long_unchanged():
    """Pin (5): existing LONG strategy unchanged by B636 (F2 docstring
    only; gates preserved)."""
    from backtest.signals.screener import strat_three_white_soldiers
    s = {
        "three_white_soldiers": True,
        "rsi_14": 55,
    }
    out = strat_three_white_soldiers(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch636_short_registered_in_all_strategies():
    """Pin (6)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "three_black_crows_short" in ALL_STRATEGIES


def test_batch636_short_regime_default_bear_crisis_neutral():
    """Pin (7): no explicit STRATEGY_REGIME_AFFINITY entry; B291
    direction-aware default applies."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    assert "three_black_crows_short" not in STRATEGY_REGIME_AFFINITY
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime(
            "three_black_crows_short", r, direction="short"
        ) is True
    assert should_strategy_fire_in_regime(
        "three_black_crows_short", "bull", direction="short"
    ) is False


def test_batch636_three_black_crows_short_still_registered():
    """Pin (8): three_black_crows_short remains registered after subsequent
    batches. Total count assertion moved to drift-floor pyramid pins in
    test_silent_gap_pyramid.py + test_unit.py (B639 dropped count 222 ->
    221 by deleting strat_evening_star_short as redundant; B636's pin
    intent is that the Class 7 NEW remains alive, not a count snapshot)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "three_black_crows_short" in ALL_STRATEGIES
    assert len(ALL_STRATEGIES) >= 220  # drift-floor
