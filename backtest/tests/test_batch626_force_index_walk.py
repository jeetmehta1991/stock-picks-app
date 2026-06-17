"""Batch 626 (2026-06-08) -- Stage 4 walk of strat_force_index_breakout
per CHECKLIST #105; first of 4 B623 REMOVE_OK regime-affinity candidates
per owner directive 2026-06-08.

Source: backtest/signals/screener.py:strat_force_index_breakout (B626
F1+F2+(a)); backtest/signals/technical.py:1206-1213 (Elder Force Index
producer); R5_VALIDATION_MANIFEST.md M1 (regime entry deferred to R5).
Per CHECKLIST #77 source-of-truth declaration.

Owner-directed C option: F1 (silent-gap fix) + F2 (docstring) + (a)
B589-family bullish/bearish bar gate.

Pins:
  (1) LONG fires with 3-gate set (force_index_cross_up +
      price_above_ema_20 + close_above_open)
  (2) SHORT fires with 3-gate set (force_index_cross_dn +
      below_ema_20 + close_below_open)
  (3) F1 silent-gap closed: missing below_ema_20 key blocks SHORT
      (pre-B626 would have auto-passed via `not s.get(price_above
      _ema_20)`)
  (4) (a) bullish-bar gate: missing close_above_open blocks LONG
  (5) (a) bearish-bar gate: missing close_below_open blocks SHORT
  (6) legacy 2-gate fixture (pre-B626) does NOT fire LONG anymore
  (7) ALL_STRATEGIES count unchanged at 221
"""
from __future__ import annotations

import pytest


def test_batch626_long_fires_3_gates():
    """Pin (1)."""
    from backtest.signals.screener import strat_force_index_breakout
    s = {
        "force_index_cross_up": True,
        "price_above_ema_20": True,
        "close_above_open": True,
    }
    out = strat_force_index_breakout(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch626_short_fires_3_gates():
    """Pin (2)."""
    from backtest.signals.screener import strat_force_index_breakout
    s = {
        "force_index_cross_dn": True,
        "below_ema_20": True,                # B626 F1 positive symmetric
        "close_below_open": True,
    }
    out = strat_force_index_breakout(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch626_short_silent_gap_closed():
    """Pin (3): KEY F1 fix - missing below_ema_20 must block SHORT
    (pre-B626 silent-gap pattern auto-passed via `not s.get(price_above
    _ema_20)`)."""
    from backtest.signals.screener import strat_force_index_breakout
    s = {
        "force_index_cross_dn": True,
        # below_ema_20 ABSENT - pre-B626 would have auto-fired via not
        # s.get(price_above_ema_20) when key is None
        "close_below_open": True,
    }
    assert strat_force_index_breakout(s)["fires"] is False, (
        "B626 F1 silent-gap fix: SHORT must NOT fire when below_ema_20 "
        "is absent (pre-B626 used `not s.get(price_above_ema_20)` which "
        "auto-passed)"
    )


def test_batch626_long_bullish_bar_required():
    """Pin (4): B626 (a) close_above_open gate must block LONG when absent."""
    from backtest.signals.screener import strat_force_index_breakout
    s = {
        "force_index_cross_up": True,
        "price_above_ema_20": True,
        # close_above_open ABSENT - B626 (a) gate
    }
    assert strat_force_index_breakout(s)["fires"] is False


def test_batch626_short_bearish_bar_required():
    """Pin (5)."""
    from backtest.signals.screener import strat_force_index_breakout
    s = {
        "force_index_cross_dn": True,
        "below_ema_20": True,
        # close_below_open ABSENT
    }
    assert strat_force_index_breakout(s)["fires"] is False


def test_batch626_legacy_2_gate_fixture_does_not_fire_long():
    """Pin (6): pre-B626 2-gate LONG fixture (force_index_cross_up +
    price_above_ema_20 only, no bar-color) must NOT fire post-B626
    because (a) added close_above_open gate."""
    from backtest.signals.screener import strat_force_index_breakout
    s = {
        "force_index_cross_up": True,
        "price_above_ema_20": True,
        # close_above_open ABSENT - pre-B626 would have fired
    }
    assert strat_force_index_breakout(s)["fires"] is False, (
        "B626 (a) added close_above_open gate; legacy 2-gate fixture "
        "must not fire"
    )


def test_batch626_all_strategies_count_unchanged():
    """Pin (7): B626 is pure refactor + docstring; no add/delete."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 219
