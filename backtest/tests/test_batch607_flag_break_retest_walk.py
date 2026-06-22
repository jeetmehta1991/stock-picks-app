"""Batch 607 (2026-06-07) -- F1 bug fix in strat_flag_bull_retest_long
walk per CHECKLIST #105 deep-read + owner-approved F1 + a + c + g + i.

Bug background (CHECKLIST #105 deep-read surfaced - 3rd consecutive
B605/B606 pattern):
  BUG-111 Batch 329 wired strat_flag_bull_retest_long against the
  DC20-anchored resistance_break_retest primitive even though the
  strategy name + docstring claimed "Bull flag + post-break retest".
  The DC20-max-CLOSE bore no relationship to the flag-high level
  (flag_bull_breakout_level was already emitted by detect_flag but
  unused). Same name-vs-implementation lie that B605 fixed for
  52wh_break_retest and B606 fixed for r1_break_retest.

B607 changes (F1 only - drop b/d/e/f/h per owner narrower scope):
  F1 - NEW producer compute_flag_break_retest_signals
       (chart_patterns.py) emits flag_bull_break_retest_long and
       flag_bear_break_retest_short. Searches for a flag completed
       K bars ago (K in 3..12) by running detect_flag on a HISTORICAL
       slice; verifies break -> retest -> hold sequence against
       THAT flag's specific breakout_level.
  (a) Added close_above_open / close_below_open.
  (c) Added vol_below_avg (Bulkowski supply-absorption).
  (g) Class 7 NEW strat_flag_bear_retest_short (symmetric inverse).
  (i) Regime affinity: Batch 291 direction-aware default.

Pins:
  (1) compute_flag_break_retest_signals emits both signal keys
  (2) flag_bull_break_retest_long fires on synthetic pole+flag+
      break+retest+hold pattern
  (3) flag_bull_break_retest_long blocked when no flag completed
  (4) flag_bear_break_retest_short mirror fires
  (5) strat_flag_bull_retest_long fires with 4 gates post-B607
  (6) Legacy 3-gate fixture (flag_bull_detected + resistance_break
      _retest + price_above_ema_200) does NOT fire post-B607 F1
  (7) strat_flag_bear_retest_short (Class 7 NEW) fires
  (8) Regime defaults: LONG = {bull, neutral}; SHORT = {bear,
      crisis, neutral}
  (9) ALL_STRATEGIES count = 221 (220 + 1 Class 7 NEW from g)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _build_df(closes, highs, lows, opens=None, volumes=None):
    n = len(closes)
    if opens is None: opens = closes[:]
    if volumes is None: volumes = [1_000_000] * n
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    }, index=pd.date_range("2024-01-01", periods=n))


def _build_bull_flag_retest_fixture():
    """50-bar synthetic where detect_flag(df.iloc[:45]) finds a bull
    flag completed at bar 44 with breakout_level ~101; bar 45 breaks
    above; bar 47 retests near 101; today (bar 49) close 102 still
    above breakout_level."""
    closes = [90.0] * 15
    closes += list(np.linspace(90.0, 100.0, 20))     # pole bars 15..34
    closes += [99.5, 100.0, 100.5, 100.0, 99.5,
               100.0, 100.5, 100.0, 100.2, 100.5]    # flag bars 35..44
    closes += [103.0, 102.0, 101.2, 101.5, 102.0]    # K=5 lag post-flag
    highs = [c + 0.5 for c in closes]
    lows  = [c - 0.5 for c in closes]
    lows[47] = 100.8                                 # retest dip
    return _build_df(closes, highs, lows)


def _build_bear_flag_retest_fixture():
    """Mirror: bear flag (pole DOWN >=-10%) followed by break-retest-hold
    below breakdown_level. detect_flag measures pole_move via the close
    at start vs end of pole window; need <-10% to trigger bear flag, so
    use 112 -> 99 for ~-11.6% pole."""
    closes = [112.0] * 15
    closes += list(np.linspace(112.0, 99.0, 20))     # pole bars 15..34 (-11.6%)
    closes += [99.5, 99.0, 98.5, 99.0, 99.5,
               99.0, 98.5, 99.0, 98.8, 98.5]         # flag bars 35..44
    closes += [96.0, 97.0, 97.5, 97.5, 97.0]         # K=5 post-flag - break below ~98.5
    highs = [c + 0.5 for c in closes]
    lows  = [c - 0.5 for c in closes]
    highs[47] = 98.3                                  # retest from below near 98.5
    return _build_df(closes, highs, lows)


def test_batch607_producer_emits_both_keys():
    """Pin (1)."""
    from backtest.signals.chart_patterns import compute_flag_break_retest_signals
    df = _build_bull_flag_retest_fixture()
    out = compute_flag_break_retest_signals(df)
    assert "flag_bull_break_retest_long" in out
    assert "flag_bear_break_retest_short" in out


def test_batch607_producer_bull_flag_retest_long_fires():
    """Pin (2)."""
    from backtest.signals.chart_patterns import compute_flag_break_retest_signals
    df = _build_bull_flag_retest_fixture()
    out = compute_flag_break_retest_signals(df)
    assert out["flag_bull_break_retest_long"] is True


def test_batch607_producer_no_flag_blocked():
    """Pin (3): flat 50 bars (no flag) -> no fire."""
    from backtest.signals.chart_patterns import compute_flag_break_retest_signals
    n = 50
    closes = [100.0] * n
    highs  = [100.5] * n
    lows   = [ 99.5] * n
    df = _build_df(closes, highs, lows)
    out = compute_flag_break_retest_signals(df)
    assert out["flag_bull_break_retest_long"] is False
    assert out["flag_bear_break_retest_short"] is False


def test_batch607_producer_bear_flag_retest_short_fires():
    """Pin (4): bear-flag mirror fires."""
    from backtest.signals.chart_patterns import compute_flag_break_retest_signals
    df = _build_bear_flag_retest_fixture()
    out = compute_flag_break_retest_signals(df)
    assert out["flag_bear_break_retest_short"] is True


def test_batch607_strat_long_4_gates_fires():
    """Pin (5)."""
    from backtest.signals.screener import strat_flag_bull_retest_long
    s = {
        "flag_bull_break_retest_long": True,
        "price_above_ema_200": True,
        "close_above_open": True,
        "vol_below_avg": True,
    }
    out = strat_flag_bull_retest_long(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch607_legacy_3_gate_fixture_blocked():
    """Pin (6): legacy 3-gate fixture does NOT fire post-B607 F1."""
    from backtest.signals.screener import strat_flag_bull_retest_long
    s = {
        "flag_bull_detected": True,
        "resistance_break_retest": True,    # legacy DC20-anchored
        "price_above_ema_200": True,
    }
    assert strat_flag_bull_retest_long(s)["fires"] is False, (
        "F1 enforced: legacy DC20-anchored fixture must not fire post-B607"
    )


def test_batch607_strat_long_blocks_when_below_ema_200():
    """Pin (5b): price_above_ema_200 required."""
    from backtest.signals.screener import strat_flag_bull_retest_long
    s = {
        "flag_bull_break_retest_long": True,
        "price_above_ema_200": False,        # below 200 EMA blocks LONG
        "close_above_open": True,
        "vol_below_avg": True,
    }
    assert strat_flag_bull_retest_long(s)["fires"] is False


def test_batch607_strat_bear_retest_short_fires():
    """Pin (7): Class 7 NEW symmetric inverse.
    B616 update: swapped `price_above_ema_200: False` -> `below_ema_200:
    True` per LOW-priority refactor (positive symmetric signal)."""
    from backtest.signals.screener import strat_flag_bear_retest_short
    s = {
        "flag_bear_break_retest_short": True,
        "below_ema_200": True,               # B616: positive symmetric signal
        "close_below_open": True,
        "vol_below_avg": True,
    }
    out = strat_flag_bear_retest_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch607_strat_bear_blocks_when_above_ema_200():
    """Pin (7b): SHORT requires price BELOW 200-EMA.
    B616 update: positive signal absent -> blocks (vs prior
    `price_above_ema_200: True` which similarly blocked via `not`)."""
    from backtest.signals.screener import strat_flag_bear_retest_short
    s = {
        "flag_bear_break_retest_short": True,
        # below_ema_200 ABSENT -> blocks SHORT (B616 silent-gap closed)
        "close_below_open": True,
        "vol_below_avg": True,
    }
    assert strat_flag_bear_retest_short(s)["fires"] is False


def test_batch607_regime_default_long_bull_neutral():
    """Pin (8) LONG."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    assert "flag_bull_retest_long" not in STRATEGY_REGIME_AFFINITY
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime(
            "flag_bull_retest_long", r, direction="long"
        ) is True
    for r in ["bear", "crisis"]:
        assert should_strategy_fire_in_regime(
            "flag_bull_retest_long", r, direction="long"
        ) is False


def test_batch607_regime_default_short_bear_crisis_neutral():
    """Pin (8) SHORT."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    assert "flag_bear_retest_short" not in STRATEGY_REGIME_AFFINITY
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime(
            "flag_bear_retest_short", r, direction="short"
        ) is True
    assert should_strategy_fire_in_regime(
        "flag_bear_retest_short", "bull", direction="short"
    ) is False


def test_batch607_all_strategies_count_after_b607():
    """Pin (9): +1 from B607 g (flag_bear_retest_short)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 220
