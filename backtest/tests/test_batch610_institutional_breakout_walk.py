"""Batch 610 (2026-06-07) -- Stage 4 walk of strat_institutional_breakout
_confirmation_long per CHECKLIST #105 deep-read + owner-approved
a + d + g + i.

CHECKLIST #105 verdict: ZERO bugs surfaced. Only walk in the B605-B610
cluster to come up clean:
  - NO F1 name-vs-impl bug (strategy honestly named; DC20 retest
    matches Bulkowski generic "retest" claim)
  - NO F1 regime affinity bug (not in STRATEGY_REGIME_AFFINITY map;
    Batch 291 default already correctly applies)
  - NO silent-gap on inverted .get() (long-only with positive gates)
  - Producer institutional_buy correctness verified end-to-end:
    13F two-source resolution (B294 fix for BUG-273), 45-day reporting
    lag (DEC-325) correctly applied

B610 changes (NO F1 bug fixes; ONLY owner-approved standardization):
  (a) Added close_above_open (B589 bullish bar).
  (d) Added vol_below_avg (Bulkowski supply-absorption thesis).
  (g) Class 7 NEW strat_institutional_breakdown_confirmation_short -
      symmetric inverse using institutional_negative + support_break
      _retest + below-200-EMA + B589 bearish bar + Bulkowski vol.
  (i) Regime: Batch 291 direction-aware default (already in effect;
      strategy correctly NOT in STRATEGY_REGIME_AFFINITY map).

Skipped: (b) strong-close 40pct / (c) B594 strong variants / (e)
  AVWAP / (f) institutional_strong_buy upgrade - narrower scope to
  preserve fire rate on rare 13F-anchored strategies.

Pins:
  (1) strat_institutional_breakout_confirmation_long LONG 5-gate
      fixture fires
  (2) Legacy 3-gate fixture (no a/d) does NOT fire post-B610
  (3) strat_institutional_breakdown_confirmation_short (Class 7 NEW)
      fires with 5 mirror gates
  (4) SHORT mirror requires institutional_negative (not institutional
      _buy) - sentiment-sign asymmetry pin
  (5) SHORT mirror requires NOT-above-200-EMA - trend filter
      direction pin
  (6) Regime defaults: LONG = {bull, neutral}; SHORT = {bear, crisis,
      neutral}
  (7) ALL_STRATEGIES count = 222 (221 + 1 Class 7 NEW from g)
"""
from __future__ import annotations

import pytest


def test_batch610_long_5_gates_fires():
    """Pin (1)."""
    from backtest.signals.screener import strat_institutional_breakout_confirmation_long
    s = {
        "institutional_buy": True,
        "resistance_break_retest": True,
        "price_above_ema_200": True,
        "close_above_open": True,
        "vol_below_avg": True,
    }
    out = strat_institutional_breakout_confirmation_long(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch610_legacy_3_gate_fixture_blocked():
    """Pin (2): legacy 3-gate fixture (institutional_buy + resistance
    _break_retest + price_above_ema_200) does NOT fire post-B610 due
    to required (a) + (d) gates."""
    from backtest.signals.screener import strat_institutional_breakout_confirmation_long
    s = {
        "institutional_buy": True,
        "resistance_break_retest": True,
        "price_above_ema_200": True,
        # close_above_open + vol_below_avg ABSENT
    }
    assert strat_institutional_breakout_confirmation_long(s)["fires"] is False, (
        "B610 added (a)+(d) gates; legacy 3-gate fixture must not fire"
    )


def test_batch610_long_blocks_without_close_above_open():
    """Pin (1b): missing close_above_open (a) blocks."""
    from backtest.signals.screener import strat_institutional_breakout_confirmation_long
    s = {
        "institutional_buy": True,
        "resistance_break_retest": True,
        "price_above_ema_200": True,
        "close_above_open": False,
        "vol_below_avg": True,
    }
    assert strat_institutional_breakout_confirmation_long(s)["fires"] is False


def test_batch610_long_blocks_without_vol_below_avg():
    """Pin (1c): missing vol_below_avg (d) blocks."""
    from backtest.signals.screener import strat_institutional_breakout_confirmation_long
    s = {
        "institutional_buy": True,
        "resistance_break_retest": True,
        "price_above_ema_200": True,
        "close_above_open": True,
        "vol_below_avg": False,
    }
    assert strat_institutional_breakout_confirmation_long(s)["fires"] is False


def test_batch611_short_strategy_deleted():
    """B611 external-AI critique fix: institutional_breakdown_confirmation
    _short was deleted same-day after B610 wired it. 13F data is long-only
    by SEC rule; the mechanical mirror was economically false."""
    from backtest.signals.screener import ALL_STRATEGIES
    from backtest.signals import screener
    assert "institutional_breakdown_confirmation_short" not in ALL_STRATEGIES
    assert not hasattr(screener, "strat_institutional_breakdown_confirmation_short"), (
        "B611 deleted the symmetric short - 13F has no short-side data; "
        "institutional_negative (decreased > increased) means trimmed longs, "
        "not short conviction. Cohen-Frazzini-Malloy 2008 long-side alpha "
        "has no analog for the SHORT direction."
    )


def test_batch610_regime_default_long_bull_neutral():
    """Pin (6) LONG: Batch 291 direction-aware default."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    assert "institutional_breakout_confirmation_long" not in STRATEGY_REGIME_AFFINITY
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime(
            "institutional_breakout_confirmation_long", r, direction="long"
        ) is True
    for r in ["bear", "crisis"]:
        assert should_strategy_fire_in_regime(
            "institutional_breakout_confirmation_long", r, direction="long"
        ) is False


def test_batch611_all_strategies_count_after_b611_delete():
    """B611 reverted B610's Class 7 NEW addition - count back to 221."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 221, (
        f"Expected 221 post-B611 (B610 added 1, B611 deleted same-day); "
        f"got {len(ALL_STRATEGIES)}"
    )
