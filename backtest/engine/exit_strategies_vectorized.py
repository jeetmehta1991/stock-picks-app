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
# Tier 2 (Batch 413, 2026-05-28 owner-approved follow-up):
# atr_trail_1x/2x + atr_trail_mae_conditional, break_even_at_1r,
# breakeven_plus_trail, chandelier_3x, mfe_lockin_trail, hybrid_50pct_target.
# ---------------------------------------------------------------------------

def _slice_future_full(df_full, entry_date):
    """Like ``_slice_future_arrays`` but also returns the boolean mask so
    callers can align full-df-computed series (DEC-311 ATR EWM, rolling
    extremes) to the future bars."""
    if df_full is None or len(df_full) == 0:
        return None
    idx = df_full.index
    if hasattr(idx, "date"):
        mask = idx.date > entry_date
    else:
        mask = pd.to_datetime(df_full["date"]).dt.date.values > entry_date
    if not mask.any():
        return None
    future = df_full[mask]
    dates = np.array([t.date() if hasattr(t, "date") else t
                      for t in future.index])
    closes = future["close"].to_numpy(dtype=float)
    highs = (future["high"] if "high" in future.columns
             else future["close"]).to_numpy(dtype=float)
    lows = (future["low"] if "low" in future.columns
            else future["close"]).to_numpy(dtype=float)
    opens = (future["open"] if "open" in future.columns
             else future["close"]).to_numpy(dtype=float)
    return mask, dates, opens, highs, lows, closes


def _atr_series_future(df_full, mask):
    """DEC-311 EWM ATR (alpha=1/14) computed on FULL df, sliced to mask.

    Matches the scalar pandas idiom exactly so per-bar atr_eff[i] is
    bit-identical to scalar's ``atr_series.loc[idx]``.
    """
    h = df_full["high"]
    l = df_full["low"]
    c = df_full["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(),
                    (l - c.shift()).abs()], axis=1).max(axis=1)
    atr_series = tr.ewm(alpha=1/14, adjust=False).mean()
    return atr_series[mask].to_numpy(dtype=float)


def _first_true(bool_arr):
    """Return index of first True in ``bool_arr``, or -1 if none."""
    if bool_arr.size == 0:
        return -1
    if not bool_arr.any():
        return -1
    return int(np.argmax(bool_arr))


def _safe_atr_eff(atr_future_arr, fallback_atr):
    """Replace NaN / non-positive ATR values with the entry-time scalar
    (mirrors scalar's ``current_atr = atr`` fallback path)."""
    return np.where(np.isfinite(atr_future_arr) & (atr_future_arr > 0),
                    atr_future_arr, fallback_atr)


def vexit_atr_trail(df_full, entry_date, entry_price, direction, atr,
                    atr_mult: float = 1.0):
    """DEC-311 rolling-ATR trailing stop. Scalar semantics:

      best = entry_price
      stop = entry_price - atr_mult * atr  (init, for longs)
      for bar in future:
          if close > best:               # strict new-high check
              best = close
              stop = max(stop, best - atr_mult * current_atr)
          fill = DEC-514(stop, open, high, low)
          if fill: return atr_trailing_stop

    Empty future OR atr == 0 -> delegate to trailing_pct(0.10) per scalar.
    """
    if df_full is None or len(df_full) == 0:
        return vexit_trailing_pct(df_full, entry_date, entry_price,
                                  direction, atr, 0.10)
    full = _slice_future_full(df_full, entry_date)
    if full is None or atr == 0:
        return vexit_trailing_pct(df_full, entry_date, entry_price,
                                  direction, atr, 0.10)
    mask, dates, opens, highs, lows, closes = full
    atr_eff = _safe_atr_eff(_atr_series_future(df_full, mask), atr)

    if direction == "long":
        init_stop = entry_price - atr_mult * atr
        running_best = np.maximum.accumulate(
            np.maximum(closes, entry_price))
        prev_best = np.concatenate([[entry_price], running_best[:-1]])
        is_new_high = running_best > prev_best
        candidate = np.where(is_new_high,
                             running_best - atr_mult * atr_eff,
                             -np.inf)
        acc_input = np.concatenate([[init_stop], candidate])
        stop_levels = np.maximum.accumulate(acc_input)[1:]
        fills = _fill_price_long_stop(stop_levels, opens, highs, lows)
        idx_first = _first_non_nan(fills)
        if idx_first < 0:
            return _base_result(entry_price, float(closes[-1]), entry_date,
                                dates[-1], "end_of_data", direction)
        return _base_result(entry_price, float(fills[idx_first]),
                            entry_date, dates[idx_first],
                            "atr_trailing_stop", direction)
    else:
        init_stop = entry_price + atr_mult * atr
        running_best = np.minimum.accumulate(
            np.minimum(closes, entry_price))
        prev_best = np.concatenate([[entry_price], running_best[:-1]])
        is_new_low = running_best < prev_best
        candidate = np.where(is_new_low,
                             running_best + atr_mult * atr_eff,
                             np.inf)
        acc_input = np.concatenate([[init_stop], candidate])
        stop_levels = np.minimum.accumulate(acc_input)[1:]
        fills = _fill_price_short_stop(stop_levels, opens, highs, lows)
        idx_first = _first_non_nan(fills)
        if idx_first < 0:
            return _base_result(entry_price, float(closes[-1]), entry_date,
                                dates[-1], "end_of_data", direction)
        return _base_result(entry_price, float(fills[idx_first]),
                            entry_date, dates[idx_first],
                            "atr_trailing_stop", direction)


def vexit_break_even_at_1r(df_full, entry_date, entry_price, direction, atr,
                           trail_pct: float = 0.10):
    """DEC-517 #20. Phase 1: stop fixed at -1R. Phase 2 (after intraday
    high crosses +1R for longs / low crosses -1R for shorts): stop -> entry
    (BE), then trail from running max close at trail_pct.

    DEC-514 fill applies throughout. Reason: 'initial_1r_stop' (pre-BE) or
    'be_trail_stop' (post-BE).
    """
    sd = _stop_distance(entry_price, atr, direction)
    full = _slice_future_full(df_full, entry_date)
    if full is None:
        return _no_data_result(entry_price, entry_date, direction)
    mask, dates, opens, highs, lows, closes = full

    if direction == "long":
        one_r = entry_price + sd
        init_stop = entry_price - sd
        # First bar where intraday high reaches +1R
        be_hit_idx = _first_true(highs >= one_r)
        n = closes.size

        if be_hit_idx < 0:
            # No BE phase. Stop fixed at -1R throughout.
            stop_levels = np.full(n, init_stop, dtype=float)
        else:
            # Pre-BE bars [0, be_hit_idx-1]: stop = init_stop.
            # From bar be_hit_idx onwards: stop transitions to entry (BE)
            # and trails from running max close (anchored at entry).
            post_closes = closes[be_hit_idx:]
            post_best_close = np.maximum.accumulate(
                np.maximum(post_closes, entry_price))
            prev_post = np.concatenate([[entry_price],
                                        post_best_close[:-1]])
            post_is_new_high = post_best_close > prev_post
            candidate_post = np.where(
                post_is_new_high,
                post_best_close * (1.0 - trail_pct),
                -np.inf,
            )
            # BE level (entry_price) is the floor for post-BE stops.
            acc_input = np.concatenate([[entry_price], candidate_post])
            post_stop_levels = np.maximum.accumulate(acc_input)[1:]
            stop_levels = np.empty(n, dtype=float)
            stop_levels[:be_hit_idx] = init_stop
            stop_levels[be_hit_idx:] = post_stop_levels

        fills = _fill_price_long_stop(stop_levels, opens, highs, lows)
        idx_first = _first_non_nan(fills)
        if idx_first < 0:
            return _base_result(entry_price, float(closes[-1]), entry_date,
                                dates[-1], "max_days", direction)
        reason = ("be_trail_stop"
                  if (be_hit_idx >= 0 and idx_first >= be_hit_idx)
                  else "initial_1r_stop")
        return _base_result(entry_price, float(fills[idx_first]),
                            entry_date, dates[idx_first], reason, direction)
    else:
        # Short side - symmetric
        one_r = entry_price - sd
        init_stop = entry_price + sd
        be_hit_idx = _first_true(lows <= one_r)
        n = closes.size

        if be_hit_idx < 0:
            stop_levels = np.full(n, init_stop, dtype=float)
        else:
            post_closes = closes[be_hit_idx:]
            post_best_close = np.minimum.accumulate(
                np.minimum(post_closes, entry_price))
            prev_post = np.concatenate([[entry_price],
                                        post_best_close[:-1]])
            post_is_new_low = post_best_close < prev_post
            candidate_post = np.where(
                post_is_new_low,
                post_best_close * (1.0 + trail_pct),
                np.inf,
            )
            acc_input = np.concatenate([[entry_price], candidate_post])
            post_stop_levels = np.minimum.accumulate(acc_input)[1:]
            stop_levels = np.empty(n, dtype=float)
            stop_levels[:be_hit_idx] = init_stop
            stop_levels[be_hit_idx:] = post_stop_levels

        fills = _fill_price_short_stop(stop_levels, opens, highs, lows)
        idx_first = _first_non_nan(fills)
        if idx_first < 0:
            return _base_result(entry_price, float(closes[-1]), entry_date,
                                dates[-1], "max_days", direction)
        reason = ("be_trail_stop"
                  if (be_hit_idx >= 0 and idx_first >= be_hit_idx)
                  else "initial_1r_stop")
        return _base_result(entry_price, float(fills[idx_first]),
                            entry_date, dates[idx_first], reason, direction)


def vexit_breakeven_plus_trail(df_full, entry_date, entry_price, direction,
                               atr, breakeven_mult: float = 1.0,
                               trail_pct: float = 0.10):
    """exit_breakeven_trail mirror. Pre-BE: stop fixed at entry - 2*atr
    (long). BE triggers when close (not high) crosses entry + 1*atr (long).
    Post-BE: stop = entry, then trail from running max close at 10%.

    NOTE: this exit uses CLOSE-BASED stop checks (NOT DEC-514 intraday
    fills) - both pre and post BE. Exit price returned is the stop level.
    """
    if atr == 0:
        atr = entry_price * ATR_FALLBACK_PCT
    full = _slice_future_full(df_full, entry_date)
    if full is None:
        return _no_data_result(entry_price, entry_date, direction)
    _mask, dates, _opens, _highs, _lows, closes = full
    n = closes.size

    if direction == "long":
        be_trigger = entry_price + breakeven_mult * atr
        init_stop = entry_price - 2 * atr
        be_hit_idx = _first_true(closes >= be_trigger)

        if be_hit_idx < 0:
            stop_levels = np.full(n, init_stop, dtype=float)
        else:
            post_closes = closes[be_hit_idx:]
            post_best_close = np.maximum.accumulate(
                np.maximum(post_closes, entry_price))
            prev_post = np.concatenate([[entry_price],
                                        post_best_close[:-1]])
            post_is_new_high = post_best_close > prev_post
            candidate_post = np.where(
                post_is_new_high,
                post_best_close * (1.0 - trail_pct),
                -np.inf,
            )
            acc_input = np.concatenate([[entry_price], candidate_post])
            post_stop_levels = np.maximum.accumulate(acc_input)[1:]
            stop_levels = np.empty(n, dtype=float)
            stop_levels[:be_hit_idx] = init_stop
            stop_levels[be_hit_idx:] = post_stop_levels

        # Close-based stop check
        stop_hit = closes <= stop_levels
        idx_first = _first_true(stop_hit)
        if idx_first < 0:
            return _base_result(entry_price, float(closes[-1]), entry_date,
                                dates[-1], "end_of_data", direction)
        return _base_result(entry_price, float(stop_levels[idx_first]),
                            entry_date, dates[idx_first],
                            "breakeven_trail_stop", direction)
    else:
        be_trigger = entry_price - breakeven_mult * atr
        init_stop = entry_price + 2 * atr
        be_hit_idx = _first_true(closes <= be_trigger)

        if be_hit_idx < 0:
            stop_levels = np.full(n, init_stop, dtype=float)
        else:
            post_closes = closes[be_hit_idx:]
            post_best_close = np.minimum.accumulate(
                np.minimum(post_closes, entry_price))
            prev_post = np.concatenate([[entry_price],
                                        post_best_close[:-1]])
            post_is_new_low = post_best_close < prev_post
            candidate_post = np.where(
                post_is_new_low,
                post_best_close * (1.0 + trail_pct),
                np.inf,
            )
            acc_input = np.concatenate([[entry_price], candidate_post])
            post_stop_levels = np.minimum.accumulate(acc_input)[1:]
            stop_levels = np.empty(n, dtype=float)
            stop_levels[:be_hit_idx] = init_stop
            stop_levels[be_hit_idx:] = post_stop_levels

        stop_hit = closes >= stop_levels
        idx_first = _first_true(stop_hit)
        if idx_first < 0:
            return _base_result(entry_price, float(closes[-1]), entry_date,
                                dates[-1], "end_of_data", direction)
        return _base_result(entry_price, float(stop_levels[idx_first]),
                            entry_date, dates[idx_first],
                            "breakeven_trail_stop", direction)


def vexit_chandelier(df_full, entry_date, entry_price, direction, atr,
                     period: int = 22, atr_mult: float = 3.0):
    """LeBeau-Lucas chandelier exit. Stop anchor = rolling_high - atr_mult *
    current_atr (long) or rolling_low + atr_mult * current_atr (short).
    DEC-514 fill. Empty future OR atr == 0 -> delegate to trailing_pct(0.10).
    """
    if df_full is None or len(df_full) == 0:
        return vexit_trailing_pct(df_full, entry_date, entry_price,
                                  direction, atr, 0.10)
    full = _slice_future_full(df_full, entry_date)
    if full is None or atr == 0:
        return vexit_trailing_pct(df_full, entry_date, entry_price,
                                  direction, atr, 0.10)
    mask, dates, opens, highs, lows, closes = full
    atr_eff = _safe_atr_eff(_atr_series_future(df_full, mask), atr)

    rh_full = df_full["high"].rolling(period).max()
    rl_full = df_full["low"].rolling(period).min()
    rh = rh_full[mask].to_numpy(dtype=float)
    rl = rl_full[mask].to_numpy(dtype=float)

    if direction == "long":
        init_stop = entry_price - atr_mult * atr
        valid_rh = np.isfinite(rh)
        candidate = np.where(valid_rh, rh - atr_mult * atr_eff, -np.inf)
        acc_input = np.concatenate([[init_stop], candidate])
        stop_levels = np.maximum.accumulate(acc_input)[1:]
        fills = _fill_price_long_stop(stop_levels, opens, highs, lows)
        idx_first = _first_non_nan(fills)
        if idx_first < 0:
            return _base_result(entry_price, float(closes[-1]), entry_date,
                                dates[-1], "end_of_data", direction)
        return _base_result(entry_price, float(fills[idx_first]),
                            entry_date, dates[idx_first],
                            "chandelier_exit", direction)
    else:
        init_stop = entry_price + atr_mult * atr
        valid_rl = np.isfinite(rl)
        candidate = np.where(valid_rl, rl + atr_mult * atr_eff, np.inf)
        acc_input = np.concatenate([[init_stop], candidate])
        stop_levels = np.minimum.accumulate(acc_input)[1:]
        fills = _fill_price_short_stop(stop_levels, opens, highs, lows)
        idx_first = _first_non_nan(fills)
        if idx_first < 0:
            return _base_result(entry_price, float(closes[-1]), entry_date,
                                dates[-1], "end_of_data", direction)
        return _base_result(entry_price, float(fills[idx_first]),
                            entry_date, dates[idx_first],
                            "chandelier_exit", direction)


def vexit_mfe_lockin_trail(df_full, entry_date, entry_price, direction, atr,
                           mfe_threshold_atr: float = 2.0,
                           lock_back_atr: float = 1.0):
    """Bandy 2014 MFE-lock-in. Pre-threshold (MFE < N*ATR): trail stop from
    running max close at 1xATR. Post-threshold: lock stop at running max
    high minus lock_back_atr * ATR. Phase can flip back and forth if ATR
    fluctuates (best_high keeps growing; threshold = mfe_threshold_atr *
    current_atr).

    DEC-514 fill. Reason at fill bar = lockin status at that bar.
    """
    if df_full is None or len(df_full) == 0:
        return vexit_trailing_pct(df_full, entry_date, entry_price,
                                  direction, atr, 0.10)
    full = _slice_future_full(df_full, entry_date)
    if full is None or atr == 0:
        return vexit_trailing_pct(df_full, entry_date, entry_price,
                                  direction, atr, 0.10)
    mask, dates, opens, highs, lows, closes = full
    atr_eff = _safe_atr_eff(_atr_series_future(df_full, mask), atr)

    if direction == "long":
        init_stop = entry_price - 1.0 * atr
        best_high = np.maximum.accumulate(np.maximum(highs, entry_price))
        mfe = best_high - entry_price
        threshold = mfe_threshold_atr * atr_eff
        is_lockin = mfe >= threshold
        # Pre-threshold trail uses running max close - over non-lockin bars only
        closes_filt = np.where(is_lockin, -np.inf, closes)
        best_close = np.maximum.accumulate(
            np.concatenate([[entry_price], closes_filt]))[1:]
        prev_best_close = np.concatenate([[entry_price], best_close[:-1]])
        is_pre_threshold_update = (~is_lockin) & (closes > prev_best_close)
        candidate_pre = np.where(is_pre_threshold_update,
                                 best_close - 1.0 * atr_eff,
                                 -np.inf)
        candidate_lockin = np.where(is_lockin,
                                    best_high - lock_back_atr * atr_eff,
                                    -np.inf)
        combined = np.maximum(candidate_pre, candidate_lockin)
        acc_input = np.concatenate([[init_stop], combined])
        stop_levels = np.maximum.accumulate(acc_input)[1:]
        fills = _fill_price_long_stop(stop_levels, opens, highs, lows)
        idx_first = _first_non_nan(fills)
        if idx_first < 0:
            return _base_result(entry_price, float(closes[-1]), entry_date,
                                dates[-1], "end_of_data", direction)
        reason = ("mfe_lockin_trail"
                  if bool(is_lockin[idx_first])
                  else "mfe_pre_threshold_trail")
        return _base_result(entry_price, float(fills[idx_first]),
                            entry_date, dates[idx_first], reason, direction)
    else:
        init_stop = entry_price + 1.0 * atr
        best_low = np.minimum.accumulate(np.minimum(lows, entry_price))
        mfe = entry_price - best_low
        threshold = mfe_threshold_atr * atr_eff
        is_lockin = mfe >= threshold
        closes_filt = np.where(is_lockin, np.inf, closes)
        best_close = np.minimum.accumulate(
            np.concatenate([[entry_price], closes_filt]))[1:]
        prev_best_close = np.concatenate([[entry_price], best_close[:-1]])
        is_pre_threshold_update = (~is_lockin) & (closes < prev_best_close)
        candidate_pre = np.where(is_pre_threshold_update,
                                 best_close + 1.0 * atr_eff,
                                 np.inf)
        candidate_lockin = np.where(is_lockin,
                                    best_low + lock_back_atr * atr_eff,
                                    np.inf)
        combined = np.minimum(candidate_pre, candidate_lockin)
        acc_input = np.concatenate([[init_stop], combined])
        stop_levels = np.minimum.accumulate(acc_input)[1:]
        fills = _fill_price_short_stop(stop_levels, opens, highs, lows)
        idx_first = _first_non_nan(fills)
        if idx_first < 0:
            return _base_result(entry_price, float(closes[-1]), entry_date,
                                dates[-1], "end_of_data", direction)
        reason = ("mfe_lockin_trail"
                  if bool(is_lockin[idx_first])
                  else "mfe_pre_threshold_trail")
        return _base_result(entry_price, float(fills[idx_first]),
                            entry_date, dates[idx_first], reason, direction)


def vexit_hybrid_50pct(df_full, entry_date, entry_price, direction, atr,
                       target_mult: float = 3.0, trail_pct: float = 0.10):
    """Pre-target: close-based hard stop at entry * 0.90 (long) / 1.10
    (short). Target trigger when intraday high >= entry + 3*ATR (long).
    Half taken at target -> blended_pnl = _pnl(entry, target). Post-target:
    stop moves to entry (BE) and trails via DEC-514 fill. On every bar
    after target, close-based stop check fires FIRST (scalar order); if it
    misses, DEC-514 trail-fill check fires. Reasons: 'stop_loss' (close-
    based hit), 'hybrid_trail' (DEC-514 fill), 'end_of_data'.
    """
    if atr == 0:
        atr = entry_price * ATR_FALLBACK_PCT
    full = _slice_future_full(df_full, entry_date)
    if full is None:
        return _no_data_result(entry_price, entry_date, direction)
    _mask, dates, opens, highs, lows, closes = full

    if direction == "long":
        target = entry_price + target_mult * atr
        initial_stop = entry_price * 0.90
        pre_stop_hit = closes <= initial_stop
        target_hit = highs >= target
        first_pre_stop = _first_true(pre_stop_hit)
        first_target = _first_true(target_hit)

        # Pre-target stop fires (or both same bar - stop wins)
        if first_pre_stop >= 0 and (first_target < 0
                                     or first_pre_stop <= first_target):
            full_pnl = _pnl(entry_price, initial_stop, direction)
            pnl = full_pnl
            exit_date = dates[first_pre_stop]
            return {
                "exit_price":  round(initial_stop, 4),
                "exit_date":   exit_date,
                "exit_reason": "stop_loss",
                "pnl_pct":     round(pnl, 4),
                "win":         pnl > 0,
                "hold_days":   (exit_date - entry_date).days,
            }

        if first_target < 0:
            # No target, no pre-target stop -> end of data
            last_close = closes[-1]
            full_pnl = _pnl(entry_price, last_close, direction)
            pnl = full_pnl
            return {
                "exit_price":  round(last_close, 4),
                "exit_date":   dates[-1],
                "exit_reason": "end_of_data",
                "pnl_pct":     round(pnl, 4),
                "win":         pnl > 0,
                "hold_days":   (dates[-1] - entry_date).days,
            }

        blended_pnl = _pnl(entry_price, target, direction)
        t = first_target

        # Post-target window: bars [t, n-1]
        post_closes = closes[t:]
        post_opens = opens[t:]
        post_highs = highs[t:]
        post_lows = lows[t:]
        # Trail anchored at entry (BE), trails from running max close
        post_best_close = np.maximum.accumulate(
            np.maximum(post_closes, entry_price))
        prev_post = np.concatenate([[entry_price], post_best_close[:-1]])
        post_is_new_high = post_best_close > prev_post
        candidate_post = np.where(post_is_new_high,
                                  post_best_close * (1.0 - trail_pct),
                                  -np.inf)
        acc_input = np.concatenate([[entry_price], candidate_post])
        post_stop_at_end = np.maximum.accumulate(acc_input)[1:]
        # Close-based check uses stop-at-START-of-bar: stop_at_start[0] is
        # initial_stop (which we already verified didn't fire at bar t);
        # stop_at_start[i] for i>=1 is post_stop_at_end[i-1].
        post_stop_at_start = np.empty_like(post_stop_at_end)
        post_stop_at_start[0] = initial_stop
        post_stop_at_start[1:] = post_stop_at_end[:-1]
        close_stop_hit = post_closes <= post_stop_at_start
        trail_fills = _fill_price_long_stop(post_stop_at_end, post_opens,
                                            post_highs, post_lows)
        first_close_stop = _first_true(close_stop_hit)
        first_trail = _first_non_nan(trail_fills)

        # Per-bar order in scalar: close-based first, then trail-fill.
        # Cross-bar: pick whichever fires earliest (close wins on same bar).
        winning_idx = -1
        reason = None
        fill_price = None
        if first_close_stop >= 0 and (first_trail < 0
                                       or first_close_stop <= first_trail):
            winning_idx = first_close_stop
            fill_price = float(post_stop_at_start[first_close_stop])
            reason = "stop_loss"
        elif first_trail >= 0:
            winning_idx = first_trail
            fill_price = float(trail_fills[first_trail])
            reason = "hybrid_trail"

        if winning_idx >= 0:
            full_pnl = _pnl(entry_price, fill_price, direction)
            pnl = blended_pnl * 0.5 + full_pnl * 0.5
            exit_date = dates[t + winning_idx]
            return {
                "exit_price":  round(fill_price, 4),
                "exit_date":   exit_date,
                "exit_reason": reason,
                "pnl_pct":     round(pnl, 4),
                "win":         pnl > 0,
                "hold_days":   (exit_date - entry_date).days,
            }

        # End of data in post-target phase
        last_close = closes[-1]
        full_pnl = _pnl(entry_price, last_close, direction)
        pnl = blended_pnl * 0.5 + full_pnl * 0.5
        return {
            "exit_price":  round(last_close, 4),
            "exit_date":   dates[-1],
            "exit_reason": "end_of_data",
            "pnl_pct":     round(pnl, 4),
            "win":         pnl > 0,
            "hold_days":   (dates[-1] - entry_date).days,
        }
    else:
        # SHORT side - B1320 (Council 352, M3=a): symmetric mirror of the LONG
        # branch. Previously shorts had NO close-based hard stop (matching the
        # pre-B1320 scalar bug), so a losing short rode to end_of_data ->
        # -32.7%/trade + -11,941pp additive DD on short strategies (B1315/
        # B1316). Now a close-based hard stop at entry*1.10 fires pre- AND
        # post-target, mirroring scalar `if direction == "short" and close >= stop`.
        target = entry_price - target_mult * atr
        initial_stop = entry_price * 1.10
        pre_stop_hit = closes >= initial_stop
        target_hit = lows <= target
        first_pre_stop = _first_true(pre_stop_hit)
        first_target = _first_true(target_hit)

        # Pre-target stop fires (or both same bar - stop wins)
        if first_pre_stop >= 0 and (first_target < 0
                                     or first_pre_stop <= first_target):
            full_pnl = _pnl(entry_price, initial_stop, direction)
            pnl = full_pnl
            exit_date = dates[first_pre_stop]
            return {
                "exit_price":  round(initial_stop, 4),
                "exit_date":   exit_date,
                "exit_reason": "stop_loss",
                "pnl_pct":     round(pnl, 4),
                "win":         pnl > 0,
                "hold_days":   (exit_date - entry_date).days,
            }

        if first_target < 0:
            last_close = closes[-1]
            full_pnl = _pnl(entry_price, last_close, direction)
            pnl = full_pnl
            return {
                "exit_price":  round(last_close, 4),
                "exit_date":   dates[-1],
                "exit_reason": "end_of_data",
                "pnl_pct":     round(pnl, 4),
                "win":         pnl > 0,
                "hold_days":   (dates[-1] - entry_date).days,
            }

        blended_pnl = _pnl(entry_price, target, direction)
        t = first_target
        post_closes = closes[t:]
        post_opens = opens[t:]
        post_highs = highs[t:]
        post_lows = lows[t:]
        post_best_close = np.minimum.accumulate(
            np.minimum(post_closes, entry_price))
        prev_post = np.concatenate([[entry_price], post_best_close[:-1]])
        post_is_new_low = post_best_close < prev_post
        candidate_post = np.where(post_is_new_low,
                                  post_best_close * (1.0 + trail_pct),
                                  np.inf)
        acc_input = np.concatenate([[entry_price], candidate_post])
        post_stop_at_end = np.minimum.accumulate(acc_input)[1:]
        post_stop_at_start = np.empty_like(post_stop_at_end)
        post_stop_at_start[0] = initial_stop
        post_stop_at_start[1:] = post_stop_at_end[:-1]
        close_stop_hit = post_closes >= post_stop_at_start
        trail_fills = _fill_price_short_stop(post_stop_at_end, post_opens,
                                             post_highs, post_lows)
        first_close_stop = _first_true(close_stop_hit)
        first_trail = _first_non_nan(trail_fills)

        winning_idx = -1
        reason = None
        fill_price = None
        if first_close_stop >= 0 and (first_trail < 0
                                       or first_close_stop <= first_trail):
            winning_idx = first_close_stop
            fill_price = float(post_stop_at_start[first_close_stop])
            reason = "stop_loss"
        elif first_trail >= 0:
            winning_idx = first_trail
            fill_price = float(trail_fills[first_trail])
            reason = "hybrid_trail"

        if winning_idx >= 0:
            full_pnl = _pnl(entry_price, fill_price, direction)
            pnl = blended_pnl * 0.5 + full_pnl * 0.5
            exit_date = dates[t + winning_idx]
            return {
                "exit_price":  round(fill_price, 4),
                "exit_date":   exit_date,
                "exit_reason": reason,
                "pnl_pct":     round(pnl, 4),
                "win":         pnl > 0,
                "hold_days":   (exit_date - entry_date).days,
            }

        last_close = closes[-1]
        full_pnl = _pnl(entry_price, last_close, direction)
        pnl = blended_pnl * 0.5 + full_pnl * 0.5
        return {
            "exit_price":  round(last_close, 4),
            "exit_date":   dates[-1],
            "exit_reason": "end_of_data",
            "pnl_pct":     round(pnl, 4),
            "win":         pnl > 0,
            "hold_days":   (dates[-1] - entry_date).days,
        }


def vexit_atr_trail_mae_conditional(df_full, entry_date, entry_price,
                                     direction, atr, signals=None):
    """Thin wrapper - reads mae_atr_mult from signals dict, clamps to
    [0.5, 2.5], delegates to vexit_atr_trail."""
    s = signals if signals else {}
    mae_mult = s.get("mae_atr_mult", 1.0)
    try:
        mae_mult = float(mae_mult)
    except (TypeError, ValueError):
        mae_mult = 1.0
    mae_mult = max(0.5, min(2.5, mae_mult))
    return vexit_atr_trail(df_full, entry_date, entry_price, direction,
                            atr, atr_mult=mae_mult)


# ---------------------------------------------------------------------------
# Registry - matches keys in exit_strategies.EXIT_STRATEGIES exactly
# ---------------------------------------------------------------------------

EXIT_STRATEGIES_VECTORIZED = {
    # Tier 1 (Batch 412)
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
    # Tier 2 (Batch 413)
    "atr_trail_1x":             lambda df, ed, ep, d, a, s: vexit_atr_trail(
        df, ed, ep, d, a, 1.0),
    "atr_trail_2x":             lambda df, ed, ep, d, a, s: vexit_atr_trail(
        df, ed, ep, d, a, 2.0),
    "atr_trail_mae_conditional": lambda df, ed, ep, d, a, s: vexit_atr_trail_mae_conditional(
        df, ed, ep, d, a, s),
    "break_even_at_1r":         lambda df, ed, ep, d, a, s: vexit_break_even_at_1r(
        df, ed, ep, d, a),
    "breakeven_plus_trail":     lambda df, ed, ep, d, a, s: vexit_breakeven_plus_trail(
        df, ed, ep, d, a),
    "chandelier_3x":            lambda df, ed, ep, d, a, s: vexit_chandelier(
        df, ed, ep, d, a, period=22, atr_mult=3.0),
    "mfe_lockin_trail":         lambda df, ed, ep, d, a, s: vexit_mfe_lockin_trail(
        df, ed, ep, d, a),
    "hybrid_50pct_target":      lambda df, ed, ep, d, a, s: vexit_hybrid_50pct(
        df, ed, ep, d, a),
}
