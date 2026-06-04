"""Batch 594 (2026-06-05) -- Stage 4 walk for donchian_10_breakout_retest
per owner directives 2026-06-05:

  (a) RENAME donchian_10_breakout_retest -> donchian_20_breakout_retest
      (name now matches the DC20-anchored producer)
  (b) FLIP vol_above_avg -> vol_below_avg (Bulkowski 2005 thesis: retest
      forms on LOWER volume = supply absorption)
  (c) retain 1.5*ATR retest tolerance
  (d) retain 2-8 lag window
  (e) ADD strong-breakout requirement on the original break bar (LOCAL
      via new signals dc20_resistance_break_retest_strong /
      dc20_support_break_retest_strong - breakout bar cleared the level
      by >= 0.5*ATR(14) instead of merely crossing it)
  (f) Regime affinity: rely on Batch 291 direction-aware default
      (long -> {bull, neutral}, short -> {bear, crisis, neutral}).

Pins:
  (1) strat_donchian_20_breakout_retest registered; old name absent
  (2) dc20_resistance_break_retest_strong emitted when breakout bar
      cleared by >= 0.5*ATR
  (3) dc20_resistance_break_retest_strong DOES NOT fire when breakout
      bar barely crossed the level (< 0.5*ATR clearance)
  (4) dc20_support_break_retest_strong mirror
  (5) vol_below_avg emitted globally (ratio < 1.0)
  (6) strat_donchian_20_breakout_retest LONG requires all 5 gates
  (7) strat_donchian_20_breakout_retest SHORT requires all 5 gates
  (8) Regime affinity: LONG default = {bull, neutral}; SHORT default
      = {bear, crisis, neutral} (Batch 291 direction-aware default)
  (9) ALL_STRATEGIES count preserved at 218 (rename does not change count)
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


def test_batch594_renamed_in_registry():
    """Pin (1): old name absent; new name present."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "donchian_10_breakout_retest" not in ALL_STRATEGIES
    assert "donchian_20_breakout_retest" in ALL_STRATEGIES


def test_batch594_old_function_symbol_absent():
    """Pin (1) extension: old function symbol no longer importable."""
    from backtest.signals import screener
    assert hasattr(screener, "strat_donchian_20_breakout_retest")
    assert not hasattr(screener, "strat_donchian_10_breakout_retest")


def _build_retest_fixture(strong: bool):
    """Build 35-bar synthetic where DC20-anchored breakout occurs 5 bars
    ago, then price retests, and today still holds above level.

    strong=True: breakout bar closes 1*ATR above level -> passes 0.5*ATR
                 strong-breakout filter
    strong=False: breakout bar closes 0.1*ATR above level -> fails
                  strong-breakout filter but passes the original
                  resistance_break_retest gate
    """
    n = 35
    # Bars 0..29: close range 95-100, high 96-101, low 94-99 (DC20 level
    # = max close in bars 9..28 ~= 100). ATR ~= 2.
    base_close = np.linspace(95.0, 100.0, 30)
    base_high  = base_close + 1.0
    base_low   = base_close - 1.0
    # Bar 30 (breakout, lag=5 from today=34): close above DC20 level
    level = 100.0  # ~ DC20 prior level
    breakout_clearance = 2.0 if strong else 0.2  # ~1*ATR vs ~0.1*ATR
    bar30_close = level + breakout_clearance
    bar30_high  = bar30_close + 1.0
    bar30_low   = level + 0.5
    # Bars 31..33: retest down toward level then bounce
    retest_close = [level + 0.3, level + 0.8, level + 1.2]
    retest_high  = [level + 1.0, level + 1.5, level + 1.8]
    retest_low   = [level - 0.5, level - 0.2, level + 0.3]  # retest_low <= level + 1.5*ATR
    # Bar 34 (today): close still above level
    today_close = level + 0.8
    today_high  = level + 1.2
    today_low   = level + 0.3
    closes = list(base_close) + [bar30_close] + retest_close + [today_close]
    highs  = list(base_high)  + [bar30_high]  + retest_high  + [today_high]
    lows   = list(base_low)   + [bar30_low]   + retest_low   + [today_low]
    return _build_df(closes, highs, lows)


def test_batch594_dc20_resistance_strong_fires_on_clear_break():
    """Pin (2): strong-break filter passes when breakout cleared by ~1 ATR."""
    from backtest.signals.technical import compute_break_retest_signals
    df = _build_retest_fixture(strong=True)
    out = compute_break_retest_signals(df)
    assert out["resistance_break_retest"] == True, (
        f"Standard retest signal should fire too: {out}"
    )
    assert out["dc20_resistance_break_retest_strong"] == True, (
        f"Strong-break filter should pass when breakout clearance >= 0.5*ATR: {out}"
    )


def test_batch594_dc20_resistance_strong_blocks_weak_break():
    """Pin (3): strong-break filter blocks when breakout barely crossed."""
    from backtest.signals.technical import compute_break_retest_signals
    df = _build_retest_fixture(strong=False)
    out = compute_break_retest_signals(df)
    # Standard pattern still detects this weak breakout
    assert out["resistance_break_retest"] == True
    # But strong filter blocks it
    assert out["dc20_resistance_break_retest_strong"] == False, (
        f"Strong-break filter should reject < 0.5*ATR clearance: {out}"
    )


def test_batch594_dc20_support_strong_mirror():
    """Pin (4): support side mirrors symmetrically."""
    from backtest.signals.technical import compute_break_retest_signals
    n = 35
    # Inverted fixture: breakdown 5 bars ago, then retest from below
    base_close = np.linspace(105.0, 100.0, 30)
    base_high  = base_close + 1.0
    base_low   = base_close - 1.0
    level = 100.0  # DC20 prior min close ~ 100
    bar30_close = level - 2.0  # strong: ~1*ATR below
    bar30_high  = level - 0.5
    bar30_low   = bar30_close - 1.0
    retest_close = [level - 0.3, level - 0.8, level - 1.2]
    retest_high  = [level + 0.5, level + 0.2, level - 0.3]  # high >= level - 1.5*ATR
    retest_low   = [level - 1.0, level - 1.5, level - 1.8]
    today_close = level - 0.8
    today_high  = level - 0.3
    today_low   = level - 1.2
    closes = list(base_close) + [bar30_close] + retest_close + [today_close]
    highs  = list(base_high)  + [bar30_high]  + retest_high  + [today_high]
    lows   = list(base_low)   + [bar30_low]   + retest_low   + [today_low]
    df = _build_df(closes, highs, lows)
    out = compute_break_retest_signals(df)
    assert out["support_break_retest"] == True
    assert out["dc20_support_break_retest_strong"] == True


def test_batch594_vol_below_avg_emitted():
    """Pin (5): vol_below_avg emitted globally when ratio < 1.0."""
    from backtest.signals.technical import compute_volume
    n = 25
    closes = [100.0] * n
    highs  = [101.0] * n
    lows   = [99.0] * n
    # Today vol below avg: 0.5x baseline -> ratio < 1.0
    vol_low = [1_000_000] * (n - 1) + [500_000]
    df = _build_df(closes, highs, lows, volumes=vol_low)
    out = compute_volume(df)
    assert out["vol_below_avg"] == True
    assert out["vol_above_avg"] == False
    # Quiet day at baseline -> ratio = 1.0 -> NOT below avg (strict <)
    vol_eq = [1_000_000] * n
    df2 = _build_df(closes, highs, lows, volumes=vol_eq)
    out2 = compute_volume(df2)
    assert out2["vol_below_avg"] == False
    assert out2["vol_above_avg"] == True


def test_batch594_strategy_long_requires_5_gates():
    """Pin (6): LONG fires only with all 5 new gates."""
    from backtest.signals.screener import strat_donchian_20_breakout_retest
    s_all = {"dc20_resistance_break_retest_strong": True,
             "vol_below_avg": True,
             "macd_12_26_9_bullish": True,
             "close_above_open": True,
             "close_in_top_40pct_of_range": True}
    out = strat_donchian_20_breakout_retest(s_all)
    assert out["fires"] == True and out["direction"] == "long"
    # Legacy resistance_break_retest (without _strong) should NOT fire
    s_legacy = dict(s_all)
    s_legacy["dc20_resistance_break_retest_strong"] = False
    s_legacy["resistance_break_retest"] = True
    assert strat_donchian_20_breakout_retest(s_legacy)["fires"] == False
    # vol_above_avg alone (without vol_below_avg) should NOT fire post-B594
    s_old_vol = dict(s_all); s_old_vol["vol_below_avg"] = False
    s_old_vol["vol_above_avg"] = True
    assert strat_donchian_20_breakout_retest(s_old_vol)["fires"] == False, (
        "Post-B594 strategy consumes vol_below_avg; vol_above_avg alone should not fire"
    )


def test_batch594_strategy_short_requires_5_gates():
    """Pin (7): SHORT mirror."""
    from backtest.signals.screener import strat_donchian_20_breakout_retest
    s_all = {"dc20_support_break_retest_strong": True,
             "vol_below_avg": True,
             "macd_12_26_9_bullish": False,
             "close_below_open": True,
             "close_in_bottom_40pct_of_range": True}
    out = strat_donchian_20_breakout_retest(s_all)
    assert out["fires"] == True and out["direction"] == "short"
    s_no_strong = dict(s_all); s_no_strong["dc20_support_break_retest_strong"] = False
    assert strat_donchian_20_breakout_retest(s_no_strong)["fires"] == False


def test_batch594_regime_affinity_direction_aware_default():
    """Pin (8): LONG = {bull, neutral} per Batch 291 default; SHORT =
    {bear, crisis, neutral}. Strategy is NOT in STRATEGY_REGIME_AFFINITY -
    the direction-aware default applies."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime
    )
    # Confirm strategy NOT in explicit affinity map
    assert "donchian_20_breakout_retest" not in STRATEGY_REGIME_AFFINITY
    # LONG side: bull + neutral allowed; bear + crisis blocked
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime(
            "donchian_20_breakout_retest", r, direction="long"
        ) is True, f"LONG should fire in {r}"
    for r in ["bear", "crisis"]:
        assert should_strategy_fire_in_regime(
            "donchian_20_breakout_retest", r, direction="long"
        ) is False, f"LONG should NOT fire in {r}"
    # SHORT side: bear + crisis + neutral allowed; bull blocked
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime(
            "donchian_20_breakout_retest", r, direction="short"
        ) is True, f"SHORT should fire in {r}"
    assert should_strategy_fire_in_regime(
        "donchian_20_breakout_retest", "bull", direction="short"
    ) is False


def test_batch594_all_strategies_count_preserved_at_218():
    """Pin (9): rename does not change count."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 218
