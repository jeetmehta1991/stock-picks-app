"""Batch 605 (2026-06-06) -- F1 bug fix in strat_52wh_break_retest walk
per CHECKLIST #105 deep-read + owner-approved a+b+c+g+e.

Bug background (surfaced from B605 producer deep-read):
  BUG-111 Batch 162 wired strat_52wh_break_retest against the DC20-
  anchored resistance_break_retest primitive even though the strategy
  name + docstring claimed "52-week high break-and-retest". The DC20
  max-close could be ANY price and bore no relationship to the
  year_high; the near_52w_high gate was a proximity filter that did
  NOT tie the retest event to the year_high break.

B605 changes:
  F1 - NEW producer compute_52w_break_retest_signals emitting
       year_high_break_retest_long + year_low_break_retest_short.
       True 52w-anchored retest pattern: bar 2-8 ago closed above
       year_high; subsequent bar low touched within 1.5*ATR(14) of
       year_high; today's close still >= year_high.
  (a) Added close_above_open + close_in_top_40pct_of_range.
  (b) Added vol_below_avg (Bulkowski supply-absorption).
  (c) Added above_avwap_20low (Brian Shannon AVWAP).
  (g) Class 7 NEW strat_52wl_break_retest_short - symmetric inverse.
  (e) Regime affinity: Batch 291 direction-aware default.

Pins:
  (1) compute_52w_break_retest_signals emits both signal keys
  (2) year_high_break_retest_long fires on synthetic break+retest+hold
  (3) year_high_break_retest_long blocked when no break above year_high
  (4) year_low_break_retest_short mirror fires
  (5) Strategy fires with all 7 gates
  (6) Legacy fixture (resistance_break_retest + near_52w_high +
      ema_200) does NOT fire post-B605 (F1 enforced)
  (7) Mirror strategy strat_52wl_break_retest_short fires
  (8) Mirror sentiment-sign: positive bar fixture on SHORT does NOT fire
  (9) Regime defaults: LONG = {bull, neutral}; SHORT = {bear, crisis, neutral}
  (10) ALL_STRATEGIES count = 220
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


def _build_year_high_break_retest_fixture():
    """280 bars: 260 bars flat near 90 (year_high ~= 90.5), then a
    break at bar (n-5) to close 95, retest near 90.7 at bar (n-3),
    still above 90.5 today (close 91.5)."""
    n = 280
    pre_closes = list(np.linspace(85.0, 90.0, n - 5))
    breakout_seq = [95.0, 93.0, 92.0, 91.5, 91.5]
    closes = pre_closes + breakout_seq
    highs  = [c + 0.5 for c in closes]
    lows   = [c - 0.5 for c in closes]
    lows[-3] = 90.7  # retest low touches near year_high
    return _build_df(closes, highs, lows)


def _build_year_low_break_retest_fixture():
    """Mirror: 280 bars from 95 -> 90 in baseline (year_low ~= 89.5),
    breakdown at bar (n-5) to close 85, retest near 89.3, still below."""
    n = 280
    pre_closes = list(np.linspace(95.0, 90.0, n - 5))
    breakdown_seq = [85.0, 87.0, 88.0, 88.5, 88.5]
    closes = pre_closes + breakdown_seq
    highs  = [c + 0.5 for c in closes]
    lows   = [c - 0.5 for c in closes]
    highs[-3] = 89.3  # retest high touches near year_low
    return _build_df(closes, highs, lows)


def test_batch605_producer_emits_both_keys():
    """Pin (1)."""
    from backtest.signals.technical import compute_52w_break_retest_signals
    df = _build_year_high_break_retest_fixture()
    out = compute_52w_break_retest_signals(df)
    assert "year_high_break_retest_long" in out
    assert "year_low_break_retest_short" in out


def test_batch605_producer_year_high_break_retest_long_fires():
    """Pin (2): synthetic break+retest+hold fixture fires the long signal."""
    from backtest.signals.technical import compute_52w_break_retest_signals
    df = _build_year_high_break_retest_fixture()
    out = compute_52w_break_retest_signals(df)
    assert out["year_high_break_retest_long"] is True


def test_batch605_producer_no_break_blocked():
    """Pin (3): flat 280 bars with no break -> no fire."""
    from backtest.signals.technical import compute_52w_break_retest_signals
    n = 280
    closes = [90.0] * n
    highs  = [90.5] * n
    lows   = [89.5] * n
    df = _build_df(closes, highs, lows)
    out = compute_52w_break_retest_signals(df)
    assert out["year_high_break_retest_long"] is False
    assert out["year_low_break_retest_short"] is False


def test_batch605_producer_year_low_break_retest_short_fires():
    """Pin (4): mirror fixture fires the short signal."""
    from backtest.signals.technical import compute_52w_break_retest_signals
    df = _build_year_low_break_retest_fixture()
    out = compute_52w_break_retest_signals(df)
    assert out["year_low_break_retest_short"] is True


def test_batch605_52wh_break_retest_7_gates_fires():
    """Pin (5): all 7 post-B605 gates satisfied -> fires."""
    from backtest.signals.screener import strat_52wh_break_retest
    s = {
        "year_high_break_retest_long": True,
        "near_52w_high": True,
        "price_above_ema_200": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
        "vol_below_avg": True,
        "above_avwap_20low": True,
    }
    out = strat_52wh_break_retest(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch605_legacy_fixture_blocked():
    """Pin (6): legacy 3-gate fixture (DC20-anchored resistance_break
    _retest + near_52w_high + price_above_ema_200) does NOT fire
    post-B605 F1."""
    from backtest.signals.screener import strat_52wh_break_retest
    s = {
        "resistance_break_retest": True,    # legacy DC20-anchored signal
        "near_52w_high": True,
        "price_above_ema_200": True,
    }
    assert strat_52wh_break_retest(s)["fires"] is False, (
        "F1 enforced: legacy DC20-anchored fixture must not fire post-B605"
    )


def test_batch605_52wl_break_retest_short_7_gates_fires():
    """Pin (7): mirror strategy fires with all 7 gates."""
    from backtest.signals.screener import strat_52wl_break_retest_short
    s = {
        "year_low_break_retest_short": True,
        "near_52w_low": True,
        "price_above_ema_200": False,        # required NOT-above per inverse
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "vol_below_avg": True,
        "above_avwap_20high": False,          # required NOT-above per inverse
    }
    out = strat_52wl_break_retest_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch605_52wl_break_retest_short_blocks_when_above_ema_200():
    """Pin (8): SHORT mirror requires price BELOW 200-EMA; with price
    ABOVE 200-EMA, the strategy must NOT fire."""
    from backtest.signals.screener import strat_52wl_break_retest_short
    s = {
        "year_low_break_retest_short": True,
        "near_52w_low": True,
        "price_above_ema_200": True,         # ABOVE - wrong for SHORT
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "vol_below_avg": True,
        "above_avwap_20high": False,
    }
    assert strat_52wl_break_retest_short(s)["fires"] is False


def test_batch605_regime_default_long_bull_neutral():
    """Pin (9) LONG: Batch 291 direction-aware default."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    assert "52wh_break_retest" not in STRATEGY_REGIME_AFFINITY
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime(
            "52wh_break_retest", r, direction="long"
        ) is True
    for r in ["bear", "crisis"]:
        assert should_strategy_fire_in_regime(
            "52wh_break_retest", r, direction="long"
        ) is False


def test_batch605_regime_default_short_bear_crisis_neutral():
    """Pin (9) SHORT."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    assert "52wl_break_retest_short" not in STRATEGY_REGIME_AFFINITY
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime(
            "52wl_break_retest_short", r, direction="short"
        ) is True
    assert should_strategy_fire_in_regime(
        "52wl_break_retest_short", "bull", direction="short"
    ) is False


def test_batch605_all_strategies_count_after_b605():
    """Pin (10): +1 from B605 g (52wl_break_retest_short)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 220, (
        f"Expected 220 post-B605 (+1 Class 7 NEW); got {len(ALL_STRATEGIES)}"
    )
