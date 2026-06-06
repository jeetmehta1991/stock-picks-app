"""Batch 606 (2026-06-06) -- F1 bug fix in strat_r1_break_retest walk
per CHECKLIST #105 deep-read + owner-approved Interpretation I
(F1 only) + a+b+d+e+i.

Bug background (CHECKLIST #105 deep-read surfaced):
  BUG-111 Batch 162 wired strat_r1_break_retest against the DC20-
  anchored resistance_break_retest primitive even though the strategy
  name + docstring claimed "Pivot R1 break-and-retest". R1 is a 1-day
  level recomputed daily from prior day's H/L/C; the DC20 max-CLOSE
  bore no relationship to any specific R1 value. The above_r1 gate
  was a same-day position filter, not a "broken R1 acting as support"
  check. Same name-vs-implementation lie that B605 F1 fixed for
  strat_52wh_break_retest.

B606 changes (Interpretation I: F1 only - drop c):
  F1 - NEW producer compute_pivot_break_retest_signals emits
       r1_break_retest_long + s1_break_retest_short. Anchored on the
       SPECIFIC R1/S1 value at the break-bar B (computed from bar
       B-1's H/L/C per standard pivot formula).
  (a) Added close_above_open / close_below_open.
  (b) Added close_in_top_40pct_of_range / close_in_bottom_40pct_of_range.
  (d) Added vol_below_avg (Bulkowski supply-absorption).
  (e) Added above_avwap_20low / NOT above_avwap_20high.
  (i) Regime affinity: Batch 291 direction-aware default.

Pins:
  (1) compute_pivot_break_retest_signals emits both signal keys
  (2) r1_break_retest_long fires on synthetic break+retest+hold
  (3) r1_break_retest_long blocked when no break occurred
  (4) s1_break_retest_short mirror fires
  (5) strat_r1_break_retest LONG fires with all 7 gates
  (6) strat_r1_break_retest SHORT fires with all 7 mirror gates
  (7) Legacy 3-gate fixture (resistance_break_retest + above_r1 +
      macd_bullish) does NOT fire post-B606 (F1 enforcement)
  (8) Regime defaults: LONG = {bull, neutral}; SHORT = {bear,
      crisis, neutral}
  (9) ALL_STRATEGIES count unchanged at 220 (F1 is bug fix, not
      a new strategy)
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


def _build_r1_break_retest_fixture():
    """30 bars where R1 at bar 25 was broken (close[25] > R1_25),
    retest at bar 27, today (bar 29) still above R1_25.

    Pre bars 0..24: H=101, L=99, C=100 (so R1_25 derived from bar 24
                                          = 2*100 - 99 = 101).
    Bar 25 (break): close = 103 (> 101).
    Bar 26: close 102.5.
    Bar 27 (retest): low 100.8 within tolerance of 101.
    Bars 28-29 (today): close 101.5 (still above 101).
    """
    n = 30
    closes = [100.0] * 25 + [103.0, 102.5, 101.5, 101.7, 101.5]
    highs  = [101.0] * 25 + [103.5, 103.0, 102.0, 102.0, 102.0]
    lows   = [ 99.0] * 25 + [102.0, 101.0, 100.8, 101.0, 101.0]
    return _build_df(closes, highs, lows)


def _build_s1_break_retest_fixture():
    """Mirror: S1 at bar 25 was broken (close[25] < S1_25), retest
    at bar 27, today still below.

    Pre bars 0..24: H=101, L=99, C=100, so S1_25 = 2*100 - 101 = 99.
    Bar 25 (break): close = 97 (< 99).
    Bar 26: close 97.5.
    Bar 27 (retest): high 99.2 (within tolerance from below).
    Bars 28-29: close 98.5 (still below 99).
    """
    n = 30
    closes = [100.0] * 25 + [97.0, 97.5, 98.5, 98.3, 98.5]
    highs  = [101.0] * 25 + [98.0, 99.0, 99.2, 99.0, 99.0]
    lows   = [ 99.0] * 25 + [96.5, 97.0, 98.0, 98.0, 98.0]
    return _build_df(closes, highs, lows)


def test_batch606_producer_emits_both_keys():
    """Pin (1)."""
    from backtest.signals.technical import compute_pivot_break_retest_signals
    df = _build_r1_break_retest_fixture()
    out = compute_pivot_break_retest_signals(df)
    assert "r1_break_retest_long" in out
    assert "s1_break_retest_short" in out


def test_batch606_producer_r1_break_retest_long_fires():
    """Pin (2)."""
    from backtest.signals.technical import compute_pivot_break_retest_signals
    df = _build_r1_break_retest_fixture()
    out = compute_pivot_break_retest_signals(df)
    assert out["r1_break_retest_long"] is True


def test_batch606_producer_no_break_blocked():
    """Pin (3): flat 30 bars with no break -> no fire."""
    from backtest.signals.technical import compute_pivot_break_retest_signals
    n = 30
    closes = [100.0] * n
    highs  = [100.5] * n
    lows   = [ 99.5] * n
    df = _build_df(closes, highs, lows)
    out = compute_pivot_break_retest_signals(df)
    assert out["r1_break_retest_long"] is False
    assert out["s1_break_retest_short"] is False


def test_batch606_producer_s1_break_retest_short_fires():
    """Pin (4)."""
    from backtest.signals.technical import compute_pivot_break_retest_signals
    df = _build_s1_break_retest_fixture()
    out = compute_pivot_break_retest_signals(df)
    assert out["s1_break_retest_short"] is True


def test_batch606_strat_long_7_gates_fires():
    """Pin (5)."""
    from backtest.signals.screener import strat_r1_break_retest
    s = {
        "r1_break_retest_long": True,
        "above_r1": True,
        "macd_12_26_9_bullish": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
        "vol_below_avg": True,
        "above_avwap_20low": True,
    }
    out = strat_r1_break_retest(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch606_strat_short_7_gates_fires():
    """Pin (6)."""
    from backtest.signals.screener import strat_r1_break_retest
    s = {
        "s1_break_retest_short": True,
        "below_s1": True,
        "macd_12_26_9_bullish": False,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "vol_below_avg": True,
        "above_avwap_20high": False,
    }
    out = strat_r1_break_retest(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch606_legacy_3_gate_fixture_blocked():
    """Pin (7): legacy 3-gate fixture (DC20 retest + above_r1 +
    macd_bullish) does NOT fire post-B606 F1."""
    from backtest.signals.screener import strat_r1_break_retest
    s = {
        "resistance_break_retest": True,    # legacy DC20-anchored signal
        "above_r1": True,
        "macd_12_26_9_bullish": True,
    }
    assert strat_r1_break_retest(s)["fires"] is False, (
        "F1 enforced: legacy DC20-anchored fixture must not fire post-B606"
    )


def test_batch606_long_blocks_when_not_above_r1():
    """Pin (5b): missing above_r1 (today's close not above today's R1)
    blocks the LONG fire even if anchored R1 retest pattern is True."""
    from backtest.signals.screener import strat_r1_break_retest
    s = {
        "r1_break_retest_long": True,
        "above_r1": False,    # today's intraday position fails
        "macd_12_26_9_bullish": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
        "vol_below_avg": True,
        "above_avwap_20low": True,
    }
    assert strat_r1_break_retest(s)["fires"] is False


def test_batch606_regime_default_long_bull_neutral():
    """Pin (8) LONG."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    assert "r1_break_retest" not in STRATEGY_REGIME_AFFINITY
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime(
            "r1_break_retest", r, direction="long"
        ) is True
    for r in ["bear", "crisis"]:
        assert should_strategy_fire_in_regime(
            "r1_break_retest", r, direction="long"
        ) is False


def test_batch606_regime_default_short_bear_crisis_neutral():
    """Pin (8) SHORT."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime(
            "r1_break_retest", r, direction="short"
        ) is True
    assert should_strategy_fire_in_regime(
        "r1_break_retest", "bull", direction="short"
    ) is False


def test_batch606_all_strategies_count_unchanged_at_220():
    """Pin (9): F1 is a bug fix, not a new strategy. Count unchanged."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 220
