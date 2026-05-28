"""Batch 412 (2026-05-28 owner-approved): unit tests for vectorized cube
exit fast path. Each test asserts the vectorized return dict equals the
scalar return dict field-for-field (rounded to 4 decimals per
``_base_result``) across a hand-built suite of OHLCV fixtures.

Scope this commit (Tier 1, 9 methods):
    time_stop_10d, time_stop_20d, class_time_stop,
    trailing_5pct, trailing_10pct, trailing_15pct,
    fixed_4r_2r, r_multiple_2r, r_multiple_3r

If any test here fails the byte-equal assertion, the vectorized fast path
must be considered drifted from scalar and the feature flag must NOT be
flipped until the drift is resolved.
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from backtest.engine.exit_strategies import EXIT_STRATEGIES
from backtest.engine.exit_strategies_vectorized import (
    EXIT_STRATEGIES_VECTORIZED,
)


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------

def _df(prices_open, prices_high, prices_low, prices_close,
        start_date=date(2024, 1, 2)):
    """Build OHLCV DataFrame with DatetimeIndex (business days)."""
    n = len(prices_close)
    idx = pd.bdate_range(start=start_date, periods=n)
    return pd.DataFrame({
        "open":   prices_open,
        "high":   prices_high,
        "low":    prices_low,
        "close":  prices_close,
        "volume": [1_000_000] * n,
    }, index=idx)


def _flat_df(n=40, base=100.0, drift=0.0):
    """Slowly-drifting OHLCV: same OHLC each bar with small intra-bar range."""
    closes = np.array([base + drift * i for i in range(n)])
    opens  = closes.copy()
    highs  = closes + 0.5
    lows   = closes - 0.5
    return _df(opens, highs, lows, closes)


def _trending_df(n=40, base=100.0, daily_pct=0.01):
    """Upward-trending OHLCV; intraday range = 1% above/below close."""
    closes = np.array([base * (1 + daily_pct) ** i for i in range(n)])
    opens  = closes / (1 + daily_pct)
    highs  = closes * 1.01
    lows   = closes * 0.99
    return _df(opens, highs, lows, closes)


# Pre-entry padding bar so entry_date != df_full.index[0].date() and
# `future = df_full[df_full.index.date > entry_date]` slices correctly.
def _add_entry_bar(df, entry_price):
    pre_idx = pd.bdate_range(end=df.index[0], periods=2)[:1]  # 1 bar before
    pre = pd.DataFrame({
        "open":   [entry_price],
        "high":   [entry_price + 0.5],
        "low":    [entry_price - 0.5],
        "close":  [entry_price],
        "volume": [1_000_000],
    }, index=pre_idx)
    return pd.concat([pre, df]).sort_index(), pre_idx[-1].date()


# ---------------------------------------------------------------------------
# Equality helper
# ---------------------------------------------------------------------------

def _assert_equal(scalar_r, vec_r, ctx=""):
    assert scalar_r["exit_price"] == vec_r["exit_price"], (
        f"{ctx}: exit_price mismatch scalar={scalar_r['exit_price']} "
        f"vec={vec_r['exit_price']}")
    assert scalar_r["exit_date"] == vec_r["exit_date"], (
        f"{ctx}: exit_date mismatch scalar={scalar_r['exit_date']} "
        f"vec={vec_r['exit_date']}")
    assert scalar_r["exit_reason"] == vec_r["exit_reason"], (
        f"{ctx}: exit_reason mismatch scalar={scalar_r['exit_reason']} "
        f"vec={vec_r['exit_reason']}")
    assert scalar_r["pnl_pct"] == vec_r["pnl_pct"], (
        f"{ctx}: pnl_pct mismatch scalar={scalar_r['pnl_pct']} "
        f"vec={vec_r['pnl_pct']}")
    assert scalar_r["win"] == vec_r["win"], (
        f"{ctx}: win mismatch scalar={scalar_r['win']} vec={vec_r['win']}")
    assert scalar_r["hold_days"] == vec_r["hold_days"], (
        f"{ctx}: hold_days mismatch scalar={scalar_r['hold_days']} "
        f"vec={vec_r['hold_days']}")


def _both(method_name, df_full, entry_date, entry_price, direction, atr,
          signals=None):
    if signals is None:
        signals = {}
    scalar_fn = EXIT_STRATEGIES[method_name]
    vec_fn = EXIT_STRATEGIES_VECTORIZED[method_name]
    scalar_r = scalar_fn(df_full, entry_date, entry_price, direction, atr,
                         signals)
    vec_r = vec_fn(df_full, entry_date, entry_price, direction, atr, signals)
    return scalar_r, vec_r


# ---------------------------------------------------------------------------
# Tier 1: time_stop_10d / time_stop_20d / class_time_stop
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("method", ["time_stop_10d", "time_stop_20d"])
@pytest.mark.parametrize("direction", ["long", "short"])
def test_time_stop_byte_equal_trending(method, direction):
    df = _trending_df(n=40, base=100.0, daily_pct=0.005)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both(method, df, entry_date, 100.0, direction, 1.0)
    _assert_equal(s, v, ctx=f"{method}-{direction}-trending")


@pytest.mark.parametrize("method", ["time_stop_10d", "time_stop_20d"])
def test_time_stop_short_future(method):
    """Future shorter than `days` -> last bar's close is used."""
    df = _trending_df(n=5, base=100.0)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both(method, df, entry_date, 100.0, "long", 1.0)
    _assert_equal(s, v, ctx=f"{method}-short-future")


def test_time_stop_empty_future():
    df = _trending_df(n=0)
    if df.empty:
        df = _trending_df(n=1)
    df, entry_date = _add_entry_bar(df, 100.0)
    # entry_date is the last bar -> future empty
    last_date = df.index[-1].date()
    s, v = _both("time_stop_10d", df, last_date, 100.0, "long", 1.0)
    _assert_equal(s, v, ctx="time_stop-empty-future")


@pytest.mark.parametrize("category", ["momentum", "trend", "mean_reversion",
                                       "pivot", "breakout"])
def test_class_time_stop_by_category(category):
    df = _trending_df(n=80, base=100.0, daily_pct=0.003)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("class_time_stop", df, entry_date, 100.0, "long", 1.0,
                 signals={"category": category})
    _assert_equal(s, v, ctx=f"class_time_stop-{category}")


# ---------------------------------------------------------------------------
# Tier 1: trailing_5pct / trailing_10pct / trailing_15pct
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("method", ["trailing_5pct", "trailing_10pct",
                                     "trailing_15pct"])
@pytest.mark.parametrize("direction", ["long", "short"])
def test_trailing_pct_byte_equal_trending(method, direction):
    df = _trending_df(n=60, base=100.0, daily_pct=0.005)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both(method, df, entry_date, 100.0, direction, 1.0)
    _assert_equal(s, v, ctx=f"{method}-{direction}-trending")


def test_trailing_pct_immediate_stop():
    """Sharp drop on first bar - stop should fire bar 1."""
    closes = np.array([85.0] + [80.0] * 30)  # gap-down 15%
    opens  = closes.copy()
    highs  = closes + 0.5
    lows   = closes - 0.5
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    for method in ["trailing_5pct", "trailing_10pct"]:
        s, v = _both(method, df, entry_date, 100.0, "long", 1.0)
        _assert_equal(s, v, ctx=f"{method}-immediate-stop")


def test_trailing_pct_no_trigger_flat():
    """Flat market - never triggers -> end_of_data."""
    df = _flat_df(n=30, base=100.0)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("trailing_5pct", df, entry_date, 100.0, "long", 1.0)
    _assert_equal(s, v, ctx="trailing-flat-no-trigger")


def test_trailing_pct_ratchet_then_stop():
    """Rise then sharp drop - trailing stop should have ratcheted up."""
    rising = [100 + i for i in range(1, 15)]   # 101..114
    dropping = [114.0, 95.0, 95.0]              # gap-down crashes trailing
    closes = np.array(rising + dropping)
    opens  = closes.copy()
    highs  = closes + 0.5
    lows   = closes - 0.5
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("trailing_10pct", df, entry_date, 100.0, "long", 1.0)
    _assert_equal(s, v, ctx="trailing-ratchet-then-stop")


# ---------------------------------------------------------------------------
# Tier 1: fixed_4r_2r
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("direction", ["long", "short"])
def test_fixed_4r_2r_target_hit(direction):
    """Construct trending bars so target hits before stop."""
    if direction == "long":
        closes = np.array([100 + i * 1.5 for i in range(30)])
    else:
        closes = np.array([100 - i * 1.5 for i in range(30)])
    opens  = closes.copy()
    highs  = closes + 0.5
    lows   = closes - 0.5
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("fixed_4r_2r", df, entry_date, 100.0, direction, 1.0)
    _assert_equal(s, v, ctx=f"fixed_4r_2r-{direction}-target")


@pytest.mark.parametrize("direction", ["long", "short"])
def test_fixed_4r_2r_stop_hit(direction):
    """Construct opposite-trend bars so stop hits before target."""
    if direction == "long":
        closes = np.array([100 - i * 1.0 for i in range(30)])
    else:
        closes = np.array([100 + i * 1.0 for i in range(30)])
    opens  = closes.copy()
    highs  = closes + 0.5
    lows   = closes - 0.5
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("fixed_4r_2r", df, entry_date, 100.0, direction, 1.0)
    _assert_equal(s, v, ctx=f"fixed_4r_2r-{direction}-stop")


def test_fixed_4r_2r_gap_through_stop():
    """Gap-down through stop level - DEC-514 fill at open."""
    # entry 100, atr 1.0 -> stop = 98, target = 104
    # Bar 1 opens at 95 (gap below stop 98) -> fill at 95
    closes = np.array([95.0, 96.0, 97.0])
    opens  = np.array([95.0, 96.0, 97.0])
    highs  = np.array([95.5, 96.5, 97.5])
    lows   = np.array([94.5, 95.5, 96.5])
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("fixed_4r_2r", df, entry_date, 100.0, "long", 1.0)
    _assert_equal(s, v, ctx="fixed_4r_2r-gap-through-stop")


def test_fixed_4r_2r_no_trigger():
    """Range-bound bars within target/stop band -> max_days reason."""
    closes = np.array([100.5 + (i % 3) * 0.1 for i in range(20)])
    opens  = closes.copy()
    highs  = closes + 0.2
    lows   = closes - 0.2
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("fixed_4r_2r", df, entry_date, 100.0, "long", 1.0)
    _assert_equal(s, v, ctx="fixed_4r_2r-no-trigger")


# ---------------------------------------------------------------------------
# Tier 1: r_multiple_2r / r_multiple_3r
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("method", ["r_multiple_2r", "r_multiple_3r"])
@pytest.mark.parametrize("direction", ["long", "short"])
def test_r_multiple_target_hit(method, direction):
    if direction == "long":
        closes = np.array([100 + i * 1.0 for i in range(30)])
    else:
        closes = np.array([100 - i * 1.0 for i in range(30)])
    opens  = closes.copy()
    highs  = closes + 0.5
    lows   = closes - 0.5
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both(method, df, entry_date, 100.0, direction, 1.0)
    _assert_equal(s, v, ctx=f"{method}-{direction}-target")


@pytest.mark.parametrize("method", ["r_multiple_2r", "r_multiple_3r"])
def test_r_multiple_stop_hit(method):
    closes = np.array([100 - i * 0.5 for i in range(20)])
    opens  = closes.copy()
    highs  = closes + 0.2
    lows   = closes - 0.5
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both(method, df, entry_date, 100.0, "long", 1.0)
    _assert_equal(s, v, ctx=f"{method}-stop")


def test_r_multiple_zero_atr_uses_fallback():
    """When atr=0, scalar uses ATR_FALLBACK_PCT * entry_price = 2."""
    closes = np.array([100 + i * 0.3 for i in range(50)])
    opens  = closes.copy()
    highs  = closes + 0.1
    lows   = closes - 0.1
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("r_multiple_2r", df, entry_date, 100.0, "long", 0.0)
    _assert_equal(s, v, ctx="r_multiple_2r-zero-atr")


# ---------------------------------------------------------------------------
# Registry sanity
# ---------------------------------------------------------------------------

def test_registry_keys_are_subset_of_exit_strategies():
    """Every vectorized key must exist in EXIT_STRATEGIES so dispatch falls
    back cleanly for scalar-only methods."""
    missing = set(EXIT_STRATEGIES_VECTORIZED.keys()) - set(
        EXIT_STRATEGIES.keys())
    assert not missing, f"Vectorized keys not in EXIT_STRATEGIES: {missing}"


# ---------------------------------------------------------------------------
# Tier 2 (Batch 413): atr_trail_1x/2x + atr_trail_mae_conditional,
# break_even_at_1r, breakeven_plus_trail, chandelier_3x, mfe_lockin_trail,
# hybrid_50pct_target.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("method", ["atr_trail_1x", "atr_trail_2x"])
@pytest.mark.parametrize("direction", ["long", "short"])
def test_atr_trail_byte_equal_trending(method, direction):
    df = _trending_df(n=60, base=100.0, daily_pct=0.005)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both(method, df, entry_date, 100.0, direction, 2.0)
    _assert_equal(s, v, ctx=f"{method}-{direction}-trending")


@pytest.mark.parametrize("method", ["atr_trail_1x", "atr_trail_2x"])
def test_atr_trail_zero_atr_falls_back_to_trailing_pct(method):
    """When atr == 0, scalar delegates to exit_trailing_pct(0.10)."""
    df = _trending_df(n=40, base=100.0, daily_pct=0.005)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both(method, df, entry_date, 100.0, "long", 0.0)
    _assert_equal(s, v, ctx=f"{method}-zero-atr")


def test_atr_trail_immediate_gap_down():
    closes = np.array([85.0] + [80.0] * 30)
    opens  = closes.copy()
    highs  = closes + 0.5
    lows   = closes - 0.5
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("atr_trail_1x", df, entry_date, 100.0, "long", 2.0)
    _assert_equal(s, v, ctx="atr_trail_1x-gap-down")


def test_atr_trail_no_trigger_flat():
    df = _flat_df(n=30, base=100.0)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("atr_trail_1x", df, entry_date, 100.0, "long", 5.0)
    _assert_equal(s, v, ctx="atr_trail_1x-flat-no-trigger")


def test_atr_trail_mae_conditional_uses_signal():
    df = _trending_df(n=50, base=100.0, daily_pct=0.004)
    df, entry_date = _add_entry_bar(df, 100.0)
    for mult in [0.5, 1.0, 1.5, 2.0, 2.5]:
        signals = {"mae_atr_mult": mult}
        s, v = _both("atr_trail_mae_conditional", df, entry_date, 100.0,
                     "long", 1.5, signals=signals)
        _assert_equal(s, v, ctx=f"atr_trail_mae_conditional-mult={mult}")


def test_atr_trail_mae_conditional_clamps_out_of_range():
    df = _trending_df(n=40, base=100.0, daily_pct=0.005)
    df, entry_date = _add_entry_bar(df, 100.0)
    for raw_mult in [0.1, 5.0, "bad"]:
        signals = {"mae_atr_mult": raw_mult}
        s, v = _both("atr_trail_mae_conditional", df, entry_date, 100.0,
                     "long", 2.0, signals=signals)
        _assert_equal(s, v, ctx=f"atr_trail_mae_conditional-clamp={raw_mult}")


@pytest.mark.parametrize("direction", ["long", "short"])
def test_break_even_at_1r_no_be_hit(direction):
    """When price never reaches +1R, only initial 1R stop can fire."""
    if direction == "long":
        closes = np.array([100 - i * 0.5 for i in range(20)])
    else:
        closes = np.array([100 + i * 0.5 for i in range(20)])
    opens  = closes.copy()
    highs  = closes + 0.3
    lows   = closes - 0.3
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("break_even_at_1r", df, entry_date, 100.0, direction, 1.5)
    _assert_equal(s, v, ctx=f"break_even_at_1r-{direction}-no-be")


@pytest.mark.parametrize("direction", ["long", "short"])
def test_break_even_at_1r_be_triggers_then_trail_exit(direction):
    """Price reaches +1R then drifts back to BE -> be_trail_stop."""
    if direction == "long":
        rising = [100 + i * 0.5 for i in range(1, 12)]   # crosses 1R early
        retrace = [105.0, 100.0, 95.0]
    else:
        rising = [100 - i * 0.5 for i in range(1, 12)]
        retrace = [95.0, 100.0, 105.0]
    closes = np.array(rising + retrace)
    opens  = closes.copy()
    highs  = closes + 0.5
    lows   = closes - 0.5
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("break_even_at_1r", df, entry_date, 100.0, direction, 1.5)
    _assert_equal(s, v, ctx=f"break_even_at_1r-{direction}-be-then-trail")


@pytest.mark.parametrize("direction", ["long", "short"])
def test_breakeven_plus_trail_basic(direction):
    df = _trending_df(n=50, base=100.0,
                      daily_pct=0.006 if direction == "long" else -0.006)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("breakeven_plus_trail", df, entry_date, 100.0, direction,
                 2.0)
    _assert_equal(s, v, ctx=f"breakeven_plus_trail-{direction}")


def test_breakeven_plus_trail_no_be_initial_stop_hit():
    """Sharp drop (>2*ATR) without crossing BE trigger -> initial stop hit."""
    closes = np.array([100.0, 96.0, 92.0, 90.0])
    opens  = closes.copy()
    highs  = closes + 0.3
    lows   = closes - 0.3
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("breakeven_plus_trail", df, entry_date, 100.0, "long", 2.0)
    _assert_equal(s, v, ctx="breakeven_plus_trail-initial-stop")


def test_breakeven_plus_trail_zero_atr_fallback():
    df = _trending_df(n=30, base=100.0, daily_pct=0.005)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("breakeven_plus_trail", df, entry_date, 100.0, "long", 0.0)
    _assert_equal(s, v, ctx="breakeven_plus_trail-zero-atr")


@pytest.mark.parametrize("direction", ["long", "short"])
def test_chandelier_3x_basic(direction):
    df = _trending_df(n=60, base=100.0,
                      daily_pct=0.004 if direction == "long" else -0.004)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("chandelier_3x", df, entry_date, 100.0, direction, 1.5)
    _assert_equal(s, v, ctx=f"chandelier_3x-{direction}")


def test_chandelier_3x_zero_atr_fallback():
    df = _trending_df(n=40, base=100.0, daily_pct=0.005)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("chandelier_3x", df, entry_date, 100.0, "long", 0.0)
    _assert_equal(s, v, ctx="chandelier_3x-zero-atr")


@pytest.mark.parametrize("direction", ["long", "short"])
def test_mfe_lockin_trail_pre_threshold(direction):
    """Modest trend that never crosses 2*ATR MFE -> pre-threshold trail."""
    if direction == "long":
        closes = np.array([100 + i * 0.3 for i in range(20)])
    else:
        closes = np.array([100 - i * 0.3 for i in range(20)])
    opens  = closes.copy()
    highs  = closes + 0.3
    lows   = closes - 0.3
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("mfe_lockin_trail", df, entry_date, 100.0, direction, 2.0)
    _assert_equal(s, v, ctx=f"mfe_lockin_trail-{direction}-pre")


@pytest.mark.parametrize("direction", ["long", "short"])
def test_mfe_lockin_trail_post_threshold(direction):
    """Strong trend crosses 2*ATR MFE then retraces -> lockin trail fires."""
    if direction == "long":
        rising = [100 + i * 1.5 for i in range(1, 12)]
        retrace = [115.0, 110.0, 108.0]
    else:
        rising = [100 - i * 1.5 for i in range(1, 12)]
        retrace = [85.0, 90.0, 92.0]
    closes = np.array(rising + retrace)
    opens  = closes.copy()
    highs  = closes + 0.5
    lows   = closes - 0.5
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("mfe_lockin_trail", df, entry_date, 100.0, direction, 2.0)
    _assert_equal(s, v, ctx=f"mfe_lockin_trail-{direction}-lockin")


def test_mfe_lockin_trail_zero_atr_fallback():
    df = _trending_df(n=30, base=100.0, daily_pct=0.005)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("mfe_lockin_trail", df, entry_date, 100.0, "long", 0.0)
    _assert_equal(s, v, ctx="mfe_lockin_trail-zero-atr")


@pytest.mark.parametrize("direction", ["long", "short"])
def test_hybrid_50pct_pre_target_stop_hit(direction):
    """Sharp drop below entry*0.90 (long) before reaching target -> stop_loss."""
    if direction == "long":
        closes = np.array([100.0, 95.0, 90.0, 88.0, 86.0])
    else:
        closes = np.array([100.0, 105.0, 110.0, 112.0, 114.0])
    opens  = closes.copy()
    highs  = closes + 0.3
    lows   = closes - 0.3
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("hybrid_50pct_target", df, entry_date, 100.0, direction, 1.0)
    _assert_equal(s, v, ctx=f"hybrid_50pct-{direction}-pre-stop")


@pytest.mark.parametrize("direction", ["long", "short"])
def test_hybrid_50pct_target_hit_then_trail_exit(direction):
    """Reach target (+3*ATR), half taken, then retrace -> trail fires."""
    if direction == "long":
        # entry 100, atr 2 -> target = 106
        rising = [101.0, 103.0, 105.0, 107.0]   # bar 4 crosses target
        retrace = [105.0, 100.5, 99.0]
    else:
        rising = [99.0, 97.0, 95.0, 93.0]      # short: target = 94
        retrace = [95.0, 99.5, 101.0]
    closes = np.array(rising + retrace)
    opens  = closes.copy()
    highs  = closes + 0.5
    lows   = closes - 0.5
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("hybrid_50pct_target", df, entry_date, 100.0, direction, 2.0)
    _assert_equal(s, v, ctx=f"hybrid_50pct-{direction}-target-trail")


def test_hybrid_50pct_no_target_no_stop_end_of_data():
    """Flat - never hits target or stop -> end_of_data."""
    closes = np.array([100.5] * 20)
    opens  = closes.copy()
    highs  = closes + 0.1
    lows   = closes - 0.1
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("hybrid_50pct_target", df, entry_date, 100.0, "long", 2.0)
    _assert_equal(s, v, ctx="hybrid_50pct-end-of-data")


def test_hybrid_50pct_zero_atr_fallback_atr():
    """When atr=0, scalar uses ATR_FALLBACK_PCT * entry = 2."""
    closes = np.array([102.0, 104.0, 106.0, 108.0])
    opens  = closes.copy()
    highs  = closes + 0.5
    lows   = closes - 0.5
    df = _df(opens, highs, lows, closes)
    df, entry_date = _add_entry_bar(df, 100.0)
    s, v = _both("hybrid_50pct_target", df, entry_date, 100.0, "long", 0.0)
    _assert_equal(s, v, ctx="hybrid_50pct-zero-atr")


def test_tier_1_methods_present():
    """Tier 1 (Batch 412) ships 9 specific methods."""
    tier_1 = {
        "time_stop_10d", "time_stop_20d", "class_time_stop",
        "trailing_5pct", "trailing_10pct", "trailing_15pct",
        "fixed_4r_2r", "r_multiple_2r", "r_multiple_3r",
    }
    have = set(EXIT_STRATEGIES_VECTORIZED.keys())
    missing = tier_1 - have
    assert not missing, f"Tier 1 missing methods: {missing}"


def test_tier_2_methods_present():
    """Tier 2 (Batch 413) adds 8 methods on top of Tier 1."""
    tier_2 = {
        "atr_trail_1x", "atr_trail_2x", "atr_trail_mae_conditional",
        "break_even_at_1r", "breakeven_plus_trail",
        "chandelier_3x", "mfe_lockin_trail", "hybrid_50pct_target",
    }
    have = set(EXIT_STRATEGIES_VECTORIZED.keys())
    missing = tier_2 - have
    assert not missing, f"Tier 2 missing methods: {missing}"


def test_total_vectorized_count_matches_tiers():
    """Tier 1 (9) + Tier 2 (8) = 17 vectorized methods after Batch 413."""
    assert len(EXIT_STRATEGIES_VECTORIZED) == 17, (
        f"Vectorized roster count drift: have "
        f"{len(EXIT_STRATEGIES_VECTORIZED)}, expected 17 (9 Tier 1 + 8 "
        f"Tier 2). Tier 3 ship will raise this to 25.")
