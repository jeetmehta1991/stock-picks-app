"""Batch 412 (2026-05-28 owner-approved): vectorized cube-exit fast path.

Behind feature flag ``USE_VECTORIZED_EXITS`` (default OFF). When ON, the cube
replay dispatches Tier 1 exit methods to numpy-vectorized implementations
that produce bit-identical results to the scalar versions in
``exit_strategies.py`` but skip the per-bar ``iterrows()`` Python overhead.

Scope this commit (Tier 1, 9 methods):
    time_stop_10d, time_stop_20d, class_time_stop,
    trailing_5pct, trailing_10pct, trailing_15pct,
    fixed_4r_2r, r_multiple_2r, r_multiple_3r

Tier 2 (atr_trail_1x/2x, hybrid_50pct_target, breakeven variants, chandelier,
mfe_lockin_trail, atr_trail_mae_conditional) deferred to Batch 413.

Correctness contract: for every (df_full, entry_date, entry_price, direction,
atr, signals) input, the vectorized return dict MUST equal
``exit_strategies.EXIT_STRATEGIES[name](...)`` field-for-field (rounded to 4
decimals per ``_base_result``). The unit tests in
``backtest/tests/test_batch412_vectorized_exits.py`` enforce this.
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from backtest.config import ATR_FALLBACK_PCT

logger = logging.getLogger(__name__)


def _pnl(entry: float, exit_p: float, direction: str) -> float:
    if direction == "long":
        return (exit_p - entry) / entry * 100
    return (entry - exit_p) / entry * 100


def _base_result(entry_price, exit_price, entry_date, exit_date, exit_reason,
                 direction):
    pnl = _pnl(entry_price, exit_price, direction)
    return {
        "exit_price":  round(exit_price, 4),
        "exit_date":   exit_date,
        "exit_reason": exit_reason,
        "pnl_pct":     round(pnl, 4),
        "win":         pnl > 0,
        "hold_days":   (exit_date - entry_date).days,
    }


def _slice_future_arrays(df_full, entry_date):
    """Return (dates, opens, highs, lows, closes) numpy arrays for bars after
    ``entry_date``. Empty arrays if no future bars.

    Mirrors ``future = df_full[df_full.index.date > entry_date]`` from the
    scalar functions.
    """
    if df_full is None or len(df_full) == 0:
        return None
    idx = df_full.index
    if hasattr(idx, "date"):
        mask = idx.date > entry_date
    else:
        mask = pd.to_datetime(df_full["date"]).dt.date.values > entry_date
    future = df_full[mask]
    if future.empty:
        return None
    dates = np.array([t.date() if hasattr(t, "date") else t
                      for t in future.index])
    closes = future["close"].to_numpy(dtype=float)
    if "high" in future.columns:
        highs = future["high"].to_numpy(dtype=float)
    else:
        highs = closes.copy()
    if "low" in future.columns:
        lows = future["low"].to_numpy(dtype=float)
    else:
        lows = closes.copy()
    if "open" in future.columns:
        opens = future["open"].to_numpy(dtype=float)
    else:
        opens = closes.copy()
    return dates, opens, highs, lows, closes


def _fill_price_long_stop(level, bar_open, bar_high, bar_low):
    """Vectorized DEC-514 long-stop fill. Returns NaN where no trigger.

    Logic from ``exit_manager.compute_fill_price`` (direction=long,
    level_type=stop):
        bar_low > stop  -> no trigger
        bar_open < stop -> fill at bar_open (gap-down through stop)
        else            -> fill at stop level
    """
    no_trigger = bar_low > level
    gap_through = bar_open < level
    fill = np.where(gap_through, bar_open, level)
    fill = np.where(no_trigger, np.nan, fill)
    return fill


def _fill_price_long_target(level, bar_open, bar_high, bar_low):
    no_trigger = bar_high < level
    gap_through = bar_open > level
    fill = np.where(gap_through, bar_open, level)
    fill = np.where(no_trigger, np.nan, fill)
    return fill


def _fill_price_short_stop(level, bar_open, bar_high, bar_low):
    no_trigger = bar_high < level
    gap_through = bar_open > level
    fill = np.where(gap_through, bar_open, level)
    fill = np.where(no_trigger, np.nan, fill)
    return fill


def _fill_price_short_target(level, bar_open, bar_high, bar_low):
    no_trigger = bar_low > level
    gap_through = bar_open < level
    fill = np.where(gap_through, bar_open, level)
    fill = np.where(no_trigger, np.nan, fill)
    return fill


def _first_non_nan(arr):
    """Return the index of the first non-NaN entry, or -1 if all NaN."""
    if arr.size == 0:
        return -1
    finite = np.isfinite(arr)
    if not finite.any():
        return -1
    return int(np.argmax(finite))


# ---------------------------------------------------------------------------
# Tier 1 vectorized exits
# ---------------------------------------------------------------------------

def _no_data_result(entry_price, entry_date, direction):
    return _base_result(entry_price, entry_price, entry_date, entry_date,
                        "no_data", direction)


def vexit_time_stop(df_full, entry_date, entry_price, direction, atr,
                    days: int = 10):
    arrs = _slice_future_arrays(df_full, entry_date)
    if arrs is None:
        return _no_data_result(entry_price, entry_date, direction)
    dates, opens, highs, lows, closes = arrs
    idx = min(days - 1, closes.size - 1)
    return _base_result(entry_price, float(closes[idx]), entry_date,
                        dates[idx], f"time_stop_{days}d", direction)


def vexit_class_time_stop(df_full, entry_date, entry_price, direction, atr,
                          signals=None, category: str = "momentum",
                          override_days=None):
    # Mirrors exit_class_time_stop: same CATEGORY_TIME_STOPS_DAYS table.
    from backtest.engine.exit_strategies import (
        get_max_days_for_category,
    )
    days = override_days if override_days is not None \
        else get_max_days_for_category(category)
    arrs = _slice_future_arrays(df_full, entry_date)
    if arrs is None:
        return _no_data_result(entry_price, entry_date, direction)
    dates, opens, highs, lows, closes = arrs
    idx = min(days - 1, closes.size - 1)
    return _base_result(
        entry_price, float(closes[idx]), entry_date, dates[idx],
        f"class_time_stop_{category}_{days}d", direction,
    )


def vexit_trailing_pct(df_full, entry_date, entry_price, direction, atr,
                       trail_pct: float = 0.10):
    """Vectorized trailing % stop.

    Scalar semantics from ``exit_trailing_pct``:
      - long: ``best = max(close so far)``; ``stop = max(stop_so_far,
        best * (1 - trail_pct))``; trigger when intraday low <= stop
        (DEC-514 fill applies).
      - short: symmetric.
    """
    arrs = _slice_future_arrays(df_full, entry_date)
    if arrs is None:
        return _no_data_result(entry_price, entry_date, direction)
    dates, opens, highs, lows, closes = arrs

    if direction == "long":
        # Running best = entry_price OR cumulative max of close, whichever
        # higher (scalar starts `best = entry_price` and updates only when
        # `close > best`).
        running_best = np.maximum.accumulate(np.maximum(closes, entry_price))
        candidate_stop = running_best * (1.0 - trail_pct)
        # Stop ratchets up only: stop_t = max(stop_{t-1}, candidate_stop_t).
        # Initial stop = entry_price * (1 - trail_pct).
        init_stop = entry_price * (1.0 - trail_pct)
        candidate_stop_with_init = np.maximum(candidate_stop, init_stop)
        stop_levels = np.maximum.accumulate(candidate_stop_with_init)
        fills = _fill_price_long_stop(stop_levels, opens, highs, lows)
        idx = _first_non_nan(fills)
        if idx < 0:
            return _base_result(entry_price, float(closes[-1]), entry_date,
                                dates[-1], "end_of_data", direction)
        return _base_result(entry_price, float(fills[idx]), entry_date,
                            dates[idx], "trailing_stop", direction)
    else:  # short
        running_best = np.minimum.accumulate(np.minimum(closes, entry_price))
        candidate_stop = running_best * (1.0 + trail_pct)
        init_stop = entry_price * (1.0 + trail_pct)
        candidate_stop_with_init = np.minimum(candidate_stop, init_stop)
        stop_levels = np.minimum.accumulate(candidate_stop_with_init)
        fills = _fill_price_short_stop(stop_levels, opens, highs, lows)
        idx = _first_non_nan(fills)
        if idx < 0:
            return _base_result(entry_price, float(closes[-1]), entry_date,
                                dates[-1], "end_of_data", direction)
        return _base_result(entry_price, float(fills[idx]), entry_date,
                            dates[idx], "trailing_stop", direction)


def vexit_fixed_target(df_full, entry_date, entry_price, direction, atr,
                       target_mult: float = 4.0, stop_mult: float = 2.0):
    """Vectorized fixed-target / fixed-stop with DEC-514 fill.

    Scalar precedence (``exit_fixed_target``): stop checked BEFORE target on
    same bar. Vectorized: find first stop trigger and first target trigger
    independently; if they coincide on the same bar, stop wins.
    """
    if atr == 0:
        atr = entry_price * ATR_FALLBACK_PCT
    arrs = _slice_future_arrays(df_full, entry_date)
    if arrs is None:
        return _no_data_result(entry_price, entry_date, direction)
    dates, opens, highs, lows, closes = arrs

    if direction == "long":
        target = entry_price + target_mult * atr
        stop = entry_price - stop_mult * atr
        stop_fills = _fill_price_long_stop(stop, opens, highs, lows)
        target_fills = _fill_price_long_target(target, opens, highs, lows)
    else:
        target = entry_price - target_mult * atr
        stop = entry_price + stop_mult * atr
        stop_fills = _fill_price_short_stop(stop, opens, highs, lows)
        target_fills = _fill_price_short_target(target, opens, highs, lows)

    stop_idx = _first_non_nan(stop_fills)
    target_idx = _first_non_nan(target_fills)

    if stop_idx < 0 and target_idx < 0:
        # No trigger - scalar returns "max_days" reason
        return _base_result(entry_price, float(closes[-1]), entry_date,
                            dates[-1], "max_days", direction)

    # Stop-first precedence on same bar
    if stop_idx >= 0 and (target_idx < 0 or stop_idx <= target_idx):
        return _base_result(entry_price, float(stop_fills[stop_idx]),
                            entry_date, dates[stop_idx], "stop_loss",
                            direction)
    return _base_result(entry_price, float(target_fills[target_idx]),
                        entry_date, dates[target_idx], "take_profit",
                        direction)


def _stop_distance(entry_price: float, atr: float, direction: str) -> float:
    if atr and atr > 0:
        return float(atr)
    return entry_price * ATR_FALLBACK_PCT


def vexit_r_multiple(df_full, entry_date, entry_price, direction, atr,
                     r_multiple: float):
    """Vectorized R-multiple target / 1R stop with DEC-514 fill.

    Mirrors ``_exit_r_multiple_impl``: stop = -1R, target = +NR. Same
    stop-first precedence as fixed_target.
    """
    sd = _stop_distance(entry_price, atr, direction)
    arrs = _slice_future_arrays(df_full, entry_date)
    if arrs is None:
        return _no_data_result(entry_price, entry_date, direction)
    dates, opens, highs, lows, closes = arrs

    if direction == "long":
        stop = entry_price - sd
        target = entry_price + r_multiple * sd
        stop_fills = _fill_price_long_stop(stop, opens, highs, lows)
        target_fills = _fill_price_long_target(target, opens, highs, lows)
    else:
        stop = entry_price + sd
        target = entry_price - r_multiple * sd
        stop_fills = _fill_price_short_stop(stop, opens, highs, lows)
        target_fills = _fill_price_short_target(target, opens, highs, lows)

    stop_idx = _first_non_nan(stop_fills)
    target_idx = _first_non_nan(target_fills)

    if stop_idx < 0 and target_idx < 0:
        return _base_result(entry_price, float(closes[-1]), entry_date,
                            dates[-1], "max_days", direction)

    if stop_idx >= 0 and (target_idx < 0 or stop_idx <= target_idx):
        return _base_result(entry_price, float(stop_fills[stop_idx]),
                            entry_date, dates[stop_idx], "r_multiple_stop",
                            direction)
    return _base_result(entry_price, float(target_fills[target_idx]),
                        entry_date, dates[target_idx],
                        f"r_multiple_{r_multiple:.0f}r_target", direction)


# ---------------------------------------------------------------------------
# Registry - matches keys in exit_strategies.EXIT_STRATEGIES exactly
# ---------------------------------------------------------------------------

EXIT_STRATEGIES_VECTORIZED = {
    "time_stop_10d":   lambda df, ed, ep, d, a, s: vexit_time_stop(
        df, ed, ep, d, a, days=10),
    "time_stop_20d":   lambda df, ed, ep, d, a, s: vexit_time_stop(
        df, ed, ep, d, a, days=20),
    "class_time_stop": lambda df, ed, ep, d, a, s: vexit_class_time_stop(
        df, ed, ep, d, a, s, category=(s or {}).get("category", "momentum")),
    "trailing_5pct":   lambda df, ed, ep, d, a, s: vexit_trailing_pct(
        df, ed, ep, d, a, 0.05),
    "trailing_10pct":  lambda df, ed, ep, d, a, s: vexit_trailing_pct(
        df, ed, ep, d, a, 0.10),
    "trailing_15pct":  lambda df, ed, ep, d, a, s: vexit_trailing_pct(
        df, ed, ep, d, a, 0.15),
    "fixed_4r_2r":     lambda df, ed, ep, d, a, s: vexit_fixed_target(
        df, ed, ep, d, a, 4.0, 2.0),
    "r_multiple_2r":   lambda df, ed, ep, d, a, s: vexit_r_multiple(
        df, ed, ep, d, a, 2.0),
    "r_multiple_3r":   lambda df, ed, ep, d, a, s: vexit_r_multiple(
        df, ed, ep, d, a, 3.0),
}
