"""Batch 594 (2026-06-05) -- Stage 4 walk producer-signal additions.

This file originally pinned the donchian_10_breakout_retest -> donchian
_20_breakout_retest rename + the 5 owner-approved walk changes on the
DUAL retest strategy. Batch 599 (2026-06-05 owner B596 convergence
option 2) DELETED the dual strategy as a duplicate of the explicit
pair (donchian_breakout_retest_long + donchian_breakdown_retest_short).

Tests retained in this file cover the PRODUCER-level additions from
B594 that are still in use post-B599 (consumed by the surviving pair):
  - dc20_resistance_break_retest_strong / dc20_support_break_retest
    _strong (LOCAL strong-break variants on compute_break_retest_signals)
  - vol_below_avg (global signal on compute_volume)
  - old strat_donchian_10_breakout_retest symbol confirmed absent

Strategy-level tests (LONG/SHORT 5-gate fires; regime defaults)
removed because the dual strategy is deleted; the same semantics live
in the explicit pair and are pinned by test_batch596_donchian_retest
_pair_walk.py.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _build_df(closes, highs, lows, opens=None, volumes=None):
    n = len(closes)
    if opens is None: opens = closes[:]
    if volumes is None: volumes = [1_000_000] * n
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    }, index=pd.date_range("2024-01-01", periods=n))


def test_batch594_old_function_symbol_absent():
    """Pin: legacy strat_donchian_10_breakout_retest symbol absent
    (was renamed to strat_donchian_20_breakout_retest in B594, then
    that itself was deleted in B599 - so both names are absent now)."""
    from backtest.signals import screener
    assert not hasattr(screener, "strat_donchian_10_breakout_retest"), (
        "Renamed in B594; should never be back"
    )
    # B599: dual deleted; symbol no longer exists either
    assert not hasattr(screener, "strat_donchian_20_breakout_retest"), (
        "Deleted in B599 per B596 convergence option 2; explicit pair "
        "donchian_breakout_retest_long + donchian_breakdown_retest_short "
        "carries the semantics."
    )


def _build_retest_fixture(strong: bool):
    """Build 35-bar synthetic where DC20-anchored breakout occurs 5 bars
    ago, then price retests, and today still holds above level."""
    n = 35
    base_close = np.linspace(95.0, 100.0, 30)
    base_high  = base_close + 1.0
    base_low   = base_close - 1.0
    level = 100.0
    breakout_clearance = 2.0 if strong else 0.2
    bar30_close = level + breakout_clearance
    bar30_high  = bar30_close + 1.0
    bar30_low   = level + 0.5
    retest_close = [level + 0.3, level + 0.8, level + 1.2]
    retest_high  = [level + 1.0, level + 1.5, level + 1.8]
    retest_low   = [level - 0.5, level - 0.2, level + 0.3]
    today_close = level + 0.8
    today_high  = level + 1.2
    today_low   = level + 0.3
    closes = list(base_close) + [bar30_close] + retest_close + [today_close]
    highs  = list(base_high)  + [bar30_high]  + retest_high  + [today_high]
    lows   = list(base_low)   + [bar30_low]   + retest_low   + [today_low]
    return _build_df(closes, highs, lows)


def test_batch594_dc20_resistance_strong_fires_on_clear_break():
    """Pin (producer-level): strong filter passes when clearance >= 0.5*ATR."""
    from backtest.signals.technical import compute_break_retest_signals
    df = _build_retest_fixture(strong=True)
    out = compute_break_retest_signals(df)
    assert out["resistance_break_retest"] == True
    assert out["dc20_resistance_break_retest_strong"] == True


def test_batch594_dc20_resistance_strong_blocks_weak_break():
    """Pin (producer-level): strong filter blocks weak breakout."""
    from backtest.signals.technical import compute_break_retest_signals
    df = _build_retest_fixture(strong=False)
    out = compute_break_retest_signals(df)
    assert out["resistance_break_retest"] == True
    assert out["dc20_resistance_break_retest_strong"] == False


def test_batch594_dc20_support_strong_mirror():
    """Pin (producer-level): support side mirror."""
    from backtest.signals.technical import compute_break_retest_signals
    n = 35
    base_close = np.linspace(105.0, 100.0, 30)
    base_high  = base_close + 1.0
    base_low   = base_close - 1.0
    level = 100.0
    bar30_close = level - 2.0
    bar30_high  = level - 0.5
    bar30_low   = bar30_close - 1.0
    retest_close = [level - 0.3, level - 0.8, level - 1.2]
    retest_high  = [level + 0.5, level + 0.2, level - 0.3]
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
    """Pin (producer-level): vol_below_avg emitted globally."""
    from backtest.signals.technical import compute_volume
    n = 25
    closes = [100.0] * n
    highs  = [101.0] * n
    lows   = [99.0] * n
    vol_low = [1_000_000] * (n - 1) + [500_000]
    df = _build_df(closes, highs, lows, volumes=vol_low)
    out = compute_volume(df)
    assert out["vol_below_avg"] == True
    assert out["vol_above_avg"] == False
    vol_eq = [1_000_000] * n
    df2 = _build_df(closes, highs, lows, volumes=vol_eq)
    out2 = compute_volume(df2)
    assert out2["vol_below_avg"] == False
    assert out2["vol_above_avg"] == True


def test_batch594_all_strategies_count_post_b599():
    """Pin (post-B599): B594 had count = 218; B599 deleted the dual
    strategy -> 217. The B594 producer-level work survives in the
    explicit pair."""
    from backtest.signals.screener import ALL_STRATEGIES
    # B622 floor-pin (converted from ==): subsequent batches added more.
    assert len(ALL_STRATEGIES) >= 217
