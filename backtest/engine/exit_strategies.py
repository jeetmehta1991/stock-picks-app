"""
engine/exit_strategies.py  -  All 12 exit strategies for comparison testing.

Each exit strategy is applied to every trade independently.
Results are compared using composite score: 40% ROI + 30% profit factor + 30% drawdown.

Exit strategies:
  1.  trailing_10pct         -  10% trailing stop (confirmed primary)
  2.  trailing_5pct          -  5% trailing stop (tighter)
  3.  trailing_15pct         -  15% trailing stop (looser)
  4.  atr_trail_1x           -  1x ATR trailing stop
  5.  atr_trail_2x           -  2x ATR trailing stop
  6.  fixed_4r_2r            -  Fixed: 4x ATR target / 2x ATR stop (2:1 R:R per DEC-353)
  7.  next_pivot_target       -  Exit at next pivot level above entry
  8.  ma_exit_ema9            -  Exit when price crosses below EMA-9
  9.  time_stop_10d           -  Exit at close of day 10
  10. time_stop_20d           -  Exit at close of day 20
  11. breakeven_plus_trail    -  Move stop to breakeven at 1x ATR profit, then trail 10%
  12. hybrid_50pct_target     -  Take 50% off at 3x ATR, trail remainder at 10%
"""

import logging
import numpy as np
import pandas as pd
from typing import Optional

# Pass 53 Day-9 v8e DEC-514  -  Backtest fill methodology.
# Use compute_fill_price() at every intraday-stop / target trigger so gap-through
# events fill at bar_open (realistic broker behavior) instead of silently
# filling at the stop/target level (which would understate downside on
# overnight gap-downs and overstate winners on gap-ups). Spec: TRADING_RULES_AND_INFORMATION.md sec11.
from backtest.engine.exit_manager import compute_fill_price
# BUG-258 fix 2026-05-13: named constant replaces magic-number 0.02 across all ATR fallbacks.
from backtest.config import ATR_FALLBACK_PCT

logger = logging.getLogger(__name__)

# Batch 412 (2026-05-28 owner-approved): vectorized cube-exit fast path flag.
# Default OFF - flip to True via run_phase1a.py --vectorized-cube-exits or by
# setting `exit_strategies.USE_VECTORIZED_EXITS = True` programmatically.
# When True, cube replay dispatches Tier 1 exit methods to their numpy
# vectorized versions in exit_strategies_vectorized.py (byte-identical
# results, ~10-12% engine speedup on Tier 1 alone).
USE_VECTORIZED_EXITS: bool = False


def _pnl(entry: float, exit_p: float, direction: str) -> float:
    """Gross % PnL by design.

    BUG-21 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 4 2026-05-10:
    DOES NOT subtract borrow cost - that is applied centrally in
    improvements.apply_transaction_costs via SHORT_ANNUAL_BORROW_RATE per
    DEC-295 (Pass 50 single-source-of-truth rule). The "short comparison
    optimistic" claim was based on misreading - sister function in
    exit_manager.py:167 has explicit docstring confirming this design.
    """
    if direction == "long":
        return (exit_p - entry) / entry * 100
    return (entry - exit_p) / entry * 100


def _atr_value(df_slice: pd.DataFrame, period: int = 14) -> float:
    """Compute ATR from a DataFrame slice."""
    if len(df_slice) < period:
        return df_slice["close"].iloc[-1] * ATR_FALLBACK_PCT
    h, l, c = df_slice["high"], df_slice["low"], df_slice["close"]
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return float(tr.ewm(alpha=1/period, adjust=False).mean().iloc[-1])


# -----------------------------------------------------------------------------
# INDIVIDUAL EXIT SIMULATORS
# Each takes: df_full (full OHLCV), entry_date, entry_price, direction, atr
# Returns: dict with exit_price, exit_date, exit_reason, pnl_pct, hold_days
# -----------------------------------------------------------------------------

def _base_result(entry_price, exit_price, entry_date, exit_date, exit_reason, direction):
    pnl = _pnl(entry_price, exit_price, direction)
    return {
        "exit_price":  round(exit_price, 4),
        "exit_date":   exit_date,
        "exit_reason": exit_reason,
        "pnl_pct":     round(pnl, 4),
        "win":         pnl > 0,
        "hold_days":   (exit_date - entry_date).days,
    }


def exit_trailing_pct(df_full, entry_date, entry_price, direction, atr,
                       trail_pct=0.10, max_days=252):
    future = df_full[df_full.index.date > entry_date]
    if future.empty:
        return _base_result(entry_price, entry_price, entry_date,
                            entry_date, "no_data", direction)
    best   = entry_price
    stop   = entry_price * (1 - trail_pct) if direction == "long" \
             else entry_price * (1 + trail_pct)

    for i, (idx, row) in enumerate(future.iterrows()):
        # No max_days force exit  -  only trailing stop and circuit breakers exit trades
        close = float(row["close"])
        low   = float(row.get("low",  close))
        high  = float(row.get("high", close))
        bar_open = float(row.get("open", close))  # DEC-514
        # Update trailing stop
        if direction == "long":
            if close > best:
                best = close
                stop = max(stop, best * (1 - trail_pct))
            fill = compute_fill_price(direction, "stop", stop, bar_open, high, low)
            if fill is not None:
                return _base_result(entry_price, fill, entry_date,
                                    idx.date(), "trailing_stop", direction)
        else:
            if close < best:
                best = close
                stop = min(stop, best * (1 + trail_pct))
            fill = compute_fill_price(direction, "stop", stop, bar_open, high, low)
            if fill is not None:
                return _base_result(entry_price, fill, entry_date,
                                    idx.date(), "trailing_stop", direction)

    last = future.iloc[-1]
    return _base_result(entry_price, float(last["close"]), entry_date,
                        future.index[-1].date(), "end_of_data", direction)


def exit_atr_trail(df_full, entry_date, entry_price, direction, atr,
                    atr_mult=1.0, max_days=252):
    """
    ATR-based trailing stop.

    DEC-311 fix (Pass 51) BUG-230: stop distance now adapts to CURRENT volatility
    (rolling 14-period ATR refreshed each day) instead of frozen entry-time
    ATR. If volatility doubles 30 days into the hold, the stop widens to
    accommodate; if it halves, the stop tightens. This matches how real
    volatility-adaptive stops work and avoids the prior bug where stops
    were mis-sized for current conditions.

    Implementation: pre-compute the EMA-ATR series once over df_full (O(n))
    and read into the loop. Falls back to entry-time `atr` when current
    ATR isn't yet computable (early in series).
    """
    future = df_full[df_full.index.date > entry_date]
    if future.empty or atr == 0:
        return exit_trailing_pct(df_full, entry_date, entry_price,
                                  direction, atr, trail_pct=0.10)

    # DEC-311: pre-compute rolling ATR series on full history (single O(n) pass)
    h, l, c = df_full["high"], df_full["low"], df_full["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr_series = tr.ewm(alpha=1/14, adjust=False).mean()

    best  = entry_price
    stop  = (entry_price - atr_mult * atr) if direction == "long" \
            else (entry_price + atr_mult * atr)

    for i, (idx, row) in enumerate(future.iterrows()):
        # No max_days force exit  -  only trailing stop and circuit breakers exit trades
        close = float(row["close"])
        low   = float(row.get("low",  close))
        high  = float(row.get("high", close))
        bar_open = float(row.get("open", close))  # DEC-514
        # DEC-311: use TODAY's ATR for stop-distance (refreshed daily)
        try:
            current_atr = float(atr_series.loc[idx])
            if not (current_atr > 0):  # NaN or zero  -  fall back to entry ATR
                current_atr = atr
        except (KeyError, ValueError):
            current_atr = atr
        if direction == "long":
            if close > best:
                best = close
                # Stop ratchets up only  -  uses current ATR for distance
                stop = max(stop, best - atr_mult * current_atr)
            fill = compute_fill_price(direction, "stop", stop, bar_open, high, low)
            if fill is not None:
                return _base_result(entry_price, fill, entry_date,
                                    idx.date(), "atr_trailing_stop", direction)
        else:
            if close < best:
                best = close
                stop = min(stop, best + atr_mult * current_atr)
            fill = compute_fill_price(direction, "stop", stop, bar_open, high, low)
            if fill is not None:
                return _base_result(entry_price, fill, entry_date,
                                    idx.date(), "atr_trailing_stop", direction)

    last = future.iloc[-1]
    return _base_result(entry_price, float(last["close"]), entry_date,
                        future.index[-1].date(), "end_of_data", direction)


def exit_fixed_target(df_full, entry_date, entry_price, direction, atr,
                       target_mult=3.0, stop_mult=2.0, max_days=252):
    if atr == 0:
        atr = entry_price * ATR_FALLBACK_PCT
    target = (entry_price + target_mult * atr) if direction == "long" \
             else (entry_price - target_mult * atr)
    stop   = (entry_price - stop_mult * atr)   if direction == "long" \
             else (entry_price + stop_mult * atr)

    future = df_full[df_full.index.date > entry_date]
    if future.empty:
        return _base_result(entry_price, entry_price, entry_date,
                            entry_date, "no_data", direction)

    for i, (idx, row) in enumerate(future.iterrows()):
        # No max_days force exit  -  only trailing stop and circuit breakers exit trades
        h, l = float(row["high"]), float(row["low"])
        bar_open = float(row.get("open", float(row["close"])))  # DEC-514
        # DEC-514 sec11.4: stop checked first (conservative  -  when both stop and
        # target trigger same bar, stop fires first; understates winners).
        stop_fill = compute_fill_price(direction, "stop", stop, bar_open, h, l)
        if stop_fill is not None:
            return _base_result(entry_price, stop_fill, entry_date,
                                idx.date(), "stop_loss", direction)
        target_fill = compute_fill_price(direction, "target", target, bar_open, h, l)
        if target_fill is not None:
            return _base_result(entry_price, target_fill, entry_date,
                                idx.date(), "take_profit", direction)

    last = future.iloc[-1]
    return _base_result(entry_price, float(last["close"]), entry_date,
                        future.index[-1].date(), "max_days", direction)


def exit_next_pivot(df_full, entry_date, entry_price, direction, atr,
                     signals: dict = None, max_days=252):
    """Exit at next pivot resistance level above entry."""
    target = None
    if signals:
        r1 = signals.get("r1", 0)
        r2 = signals.get("r2", 0)
        if direction == "long":
            if r1 and r1 > entry_price:
                target = r1
            elif r2 and r2 > entry_price:
                target = r2
        else:
            s1 = signals.get("s1", 0)
            s2 = signals.get("s2", 0)
            if s1 and s1 < entry_price:
                target = s1
            elif s2 and s2 < entry_price:
                target = s2

    if target is None:
        # Fall back to 3x ATR if no pivot available
        return exit_fixed_target(df_full, entry_date, entry_price,
                                  direction, atr, target_mult=3.0)

    stop = (entry_price * 0.90) if direction == "long" else (entry_price * 1.10)
    future = df_full[df_full.index.date > entry_date]
    if future.empty:
        return _base_result(entry_price, entry_price, entry_date,
                            entry_date, "no_data", direction)

    for i, (idx, row) in enumerate(future.iterrows()):
        # No max_days force exit  -  only trailing stop and circuit breakers exit trades
        h, l = float(row["high"]), float(row["low"])
        bar_open = float(row.get("open", float(row["close"])))  # DEC-514
        stop_fill = compute_fill_price(direction, "stop", stop, bar_open, h, l)
        if stop_fill is not None:
            return _base_result(entry_price, stop_fill, entry_date,
                                idx.date(), "pivot_stop", direction)
        target_fill = compute_fill_price(direction, "target", target, bar_open, h, l)
        if target_fill is not None:
            return _base_result(entry_price, target_fill, entry_date,
                                idx.date(), "pivot_target", direction)

    last = future.iloc[-1]
    return _base_result(entry_price, float(last["close"]), entry_date,
                        future.index[-1].date(), "max_days", direction)


def exit_ma_cross(df_full, entry_date, entry_price, direction, atr,
                   ma_period=9, max_days=252):
    """Exit when price crosses back below/above EMA-9."""
    stop = (entry_price * 0.90) if direction == "long" else (entry_price * 1.10)
    future = df_full[df_full.index.date > entry_date]
    if future.empty:
        return _base_result(entry_price, entry_price, entry_date,
                            entry_date, "no_data", direction)

    for i, (idx, row) in enumerate(future.iterrows()):
        # No max_days force exit  -  only trailing stop and circuit breakers exit trades
        close = float(row["close"])
        low   = float(row.get("low",  close))
        high  = float(row.get("high", close))
        bar_open = float(row.get("open", close))  # DEC-514
        # Compute EMA on data up to this point
        hist = df_full[df_full.index <= idx]["close"]
        if len(hist) >= ma_period:
            ema = float(hist.ewm(span=ma_period, adjust=False).mean().iloc[-1])
        else:
            ema = close
        # Hard stop (intraday L/H  -  DEC-514 fill methodology)
        stop_fill = compute_fill_price(direction, "stop", stop, bar_open, high, low)
        if stop_fill is not None:
            return _base_result(entry_price, stop_fill, entry_date,
                                idx.date(), "hard_stop", direction)
        # MA-cross (close-based by design  -  separate from DEC-514 stop fills)
        if direction == "long":
            if close < ema:
                return _base_result(entry_price, close, entry_date,
                                    idx.date(), "ma_cross", direction)
        else:
            if close > ema:
                return _base_result(entry_price, close, entry_date,
                                    idx.date(), "ma_cross", direction)

    last = future.iloc[-1]
    return _base_result(entry_price, float(last["close"]), entry_date,
                        future.index[-1].date(), "max_days", direction)


def exit_time_stop(df_full, entry_date, entry_price, direction, atr, days=10):
    future = df_full[df_full.index.date > entry_date]
    if future.empty:
        return _base_result(entry_price, entry_price, entry_date,
                            entry_date, "no_data", direction)
    target_row = future.iloc[min(days-1, len(future)-1)]
    return _base_result(entry_price, float(target_row["close"]), entry_date,
                        future.index[min(days-1, len(future)-1)].date(),
                        f"time_stop_{days}d", direction)


def exit_breakeven_trail(df_full, entry_date, entry_price, direction, atr,
                          breakeven_mult=1.0, trail_pct=0.10, max_days=252):
    """Move stop to breakeven once 1x ATR in profit, then trail at 10%."""
    if atr == 0:
        atr = entry_price * ATR_FALLBACK_PCT
    be_trigger = (entry_price + breakeven_mult * atr) if direction == "long" \
                 else (entry_price - breakeven_mult * atr)
    stop       = (entry_price - 2 * atr) if direction == "long" \
                 else (entry_price + 2 * atr)
    breakeven_hit = False
    best       = entry_price

    future = df_full[df_full.index.date > entry_date]
    if future.empty:
        return _base_result(entry_price, entry_price, entry_date,
                            entry_date, "no_data", direction)

    for i, (idx, row) in enumerate(future.iterrows()):
        # No max_days force exit  -  only trailing stop and circuit breakers exit trades
        close = float(row["close"])
        low   = float(row.get("low",  close))
        high  = float(row.get("high", close))
        # Activate breakeven
        if not breakeven_hit:
            if direction == "long" and close >= be_trigger:
                stop = entry_price   # move to breakeven
                breakeven_hit = True
            elif direction == "short" and close <= be_trigger:
                stop = entry_price
                breakeven_hit = True
        # Trail after breakeven
        if breakeven_hit:
            if direction == "long":
                if close > best:
                    best = close
                    stop = max(stop, best * (1 - trail_pct))
            else:
                if close < best:
                    best = close
                    stop = min(stop, best * (1 + trail_pct))
        # Check stop
        if direction == "long" and close <= stop:
            return _base_result(entry_price, stop, entry_date,
                                idx.date(), "breakeven_trail_stop", direction)
        if direction == "short" and close >= stop:
            return _base_result(entry_price, stop, entry_date,
                                idx.date(), "breakeven_trail_stop", direction)

    last = future.iloc[-1]
    return _base_result(entry_price, float(last["close"]), entry_date,
                        future.index[-1].date(), "end_of_data", direction)


def exit_hybrid_50pct(df_full, entry_date, entry_price, direction, atr,
                       target_mult=3.0, trail_pct=0.10, max_days=252):
    """Take 50% off at 3x ATR, trail remaining 50% at 10%."""
    if atr == 0:
        atr = entry_price * ATR_FALLBACK_PCT
    target      = (entry_price + target_mult * atr) if direction == "long" \
                  else (entry_price - target_mult * atr)
    stop        = (entry_price * 0.90) if direction == "long" \
                  else (entry_price * 1.10)
    half_taken  = False
    blended_pnl = 0.0
    best        = entry_price

    future = df_full[df_full.index.date > entry_date]
    if future.empty:
        return _base_result(entry_price, entry_price, entry_date,
                            entry_date, "no_data", direction)

    for i, (idx, row) in enumerate(future.iterrows()):
        # DEC-312 fix (Pass 51) BUG-231: max_days check removed for parity with other
        # 11 exit strategies. Hybrid was the only one enforcing 252-day cap;
        # made comparison metrics non-apples-to-apples in run_exit_comparison.
        # max_days param kept in signature for backward compat but unused.
        h, l, close = float(row["high"]), float(row["low"]), float(row["close"])

        # Hard stop
        if direction == "long" and close <= stop:
            full_pnl = _pnl(entry_price, stop, direction)
            pnl = (blended_pnl * 0.5 + full_pnl * 0.5) if half_taken else full_pnl
            return {"exit_price": round(stop, 4), "exit_date": idx.date(),
                    "exit_reason": "stop_loss", "pnl_pct": round(pnl, 4),
                    "win": pnl > 0,
                    "hold_days": (idx.date() - entry_date).days}

        # Take 50% at target
        if not half_taken:
            hit = (direction == "long" and h >= target) or \
                  (direction == "short" and l <= target)
            if hit:
                blended_pnl = _pnl(entry_price, target, direction)
                half_taken  = True
                stop        = entry_price   # move stop to breakeven on remainder

        # Trail remainder (DEC-514 intraday L/H fills with gap-through rule)
        if half_taken:
            bar_open = float(row.get("open", close))
            if direction == "long":
                if close > best:
                    best = close
                    stop = max(stop, best * (1 - trail_pct))
                fill = compute_fill_price(direction, "stop", stop, bar_open, h, l)
                if fill is not None:
                    full_pnl = _pnl(entry_price, fill, direction)
                    pnl = blended_pnl * 0.5 + full_pnl * 0.5
                    return {"exit_price": round(fill, 4), "exit_date": idx.date(),
                            "exit_reason": "hybrid_trail", "pnl_pct": round(pnl, 4),
                            "win": pnl > 0,
                            "hold_days": (idx.date() - entry_date).days}
            else:  # short
                if close < best:
                    best = close
                    stop = min(stop, best * (1 + trail_pct))
                fill = compute_fill_price(direction, "stop", stop, bar_open, h, l)
                if fill is not None:
                    full_pnl = _pnl(entry_price, fill, direction)
                    pnl = blended_pnl * 0.5 + full_pnl * 0.5
                    return {"exit_price": round(fill, 4), "exit_date": idx.date(),
                            "exit_reason": "hybrid_trail", "pnl_pct": round(pnl, 4),
                            "win": pnl > 0,
                            "hold_days": (idx.date() - entry_date).days}

    last = future.iloc[-1]
    close = float(last["close"])
    full_pnl = _pnl(entry_price, close, direction)
    pnl = (blended_pnl * 0.5 + full_pnl * 0.5) if half_taken else full_pnl
    return {"exit_price": round(close, 4), "exit_date": future.index[-1].date(),
            "exit_reason": "end_of_data", "pnl_pct": round(pnl, 4),
            "win": pnl > 0,
            "hold_days": (future.index[-1].date() - entry_date).days}


# -----------------------------------------------------------------------------
# Pass 53 Day-9 v8g  -  DEC-518 Earnings-blackout exit
# Per spec TRADING_RULES_AND_INFORMATION.md sec8.8.
# -----------------------------------------------------------------------------

EARNINGS_TOLERANT_STRATEGIES = frozenset({
    "pre_earnings_iv_crush_front_run",
    "guidance_raise_momentum",
    "surprise_magnitude_pead",
    "earnings_cluster_sector_drift",
})


def is_earnings_tolerant(strategy_name: str) -> bool:
    return strategy_name in EARNINGS_TOLERANT_STRATEGIES


def exit_earnings_blackout(df_full, entry_date, entry_price, direction, atr,
                             signals=None, ticker: str = "",
                             strategy_name: str = "",
                             earnings_dates=None):
    """DEC-518: Force exit at close of T-1 before scheduled earnings.

    Skips blackout for strategies on the DEC-013 earnings_tolerant list. If no
    earnings calendar available, returns no_earnings_known (no forced exit).
    """
    if is_earnings_tolerant(strategy_name):
        if len(df_full) == 0:
            return _base_result(entry_price, entry_price, entry_date,
                                entry_date, "earnings_tolerant_skip", direction)
        last = df_full.iloc[-1]
        last_date = (df_full.index[-1].date()
                     if hasattr(df_full.index[-1], "date") else entry_date)
        return _base_result(entry_price, float(last["close"]), entry_date,
                            last_date, "earnings_tolerant_skip", direction)

    future = df_full[df_full.index.date > entry_date]
    if future.empty:
        return _base_result(entry_price, entry_price, entry_date,
                            entry_date, "no_data", direction)

    if earnings_dates is None and ticker:
        try:
            from backtest.data.fetcher import fetch_earnings_dates
            df_e = fetch_earnings_dates(ticker)
            if df_e is not None and not df_e.empty:
                earnings_dates = pd.to_datetime(
                    df_e["earnings_date"]
                ).dt.date.tolist()
        except Exception as exc:
            logger.debug("exit_earnings_blackout: earnings fetch failed (%s): %s",
                          ticker, exc)
            earnings_dates = []

    if not earnings_dates:
        last = future.iloc[-1]
        return _base_result(entry_price, float(last["close"]), entry_date,
                            future.index[-1].date(), "no_earnings_known",
                            direction)

    upcoming = sorted(d for d in earnings_dates if d > entry_date)
    if not upcoming:
        last = future.iloc[-1]
        return _base_result(entry_price, float(last["close"]), entry_date,
                            future.index[-1].date(), "no_upcoming_earnings",
                            direction)

    next_earn = upcoming[0]
    bars_before = future[future.index.date < next_earn]
    if bars_before.empty:
        target_idx = 0
    else:
        target_idx = len(bars_before) - 1

    target_row = future.iloc[target_idx]
    target_ts = future.index[target_idx]
    return _base_result(
        entry_price, float(target_row["close"]),
        entry_date,
        target_ts.date() if hasattr(target_ts, "date") else target_ts,
        "earnings_blackout_T_minus_1", direction,
    )


# -----------------------------------------------------------------------------
# Pass 53 Day-9 v8g  -  DEC-521 Per-strategy-class time stops
# Per spec TRADING_RULES_AND_INFORMATION.md sec8.11.
# -----------------------------------------------------------------------------

# Default time stops per strategy class (configurable per-strategy override).
# Categories follow STRATEGY_ROSTER_FULL.md Layer 1 letter taxonomy.
CATEGORY_TIME_STOPS_DAYS = {
    # Layer 1
    "pivot":           7,    # 1.A range 5-10
    "momentum":        25,   # 1.B range 20-30
    "trend":           50,   # 1.C range 40-60
    "mean_reversion":  7,    # 1.D range 5-10
    "breakout":        25,   # 1.E range 20-30
    "candle":          7,    # 1.F range 5-10
    "confluence":      None, # 1.G inherited from constituents (handled by caller)
    # Layer 2
    "ict_smc":         15,   # 2A range 10-20
    "earnings":        45,   # 2B range 30-60 (PEAD)
    "calendar":        None, # 2C per-strategy (e.g. Sell-in-May 6 months)
    # Layer 3
    "chart_pattern":   45,   # 3A range 30-60
    "pairs":           30,   # 3B range 20-40
    "cross_asset":     50,   # 3B range 40-60
    # Layer 6
    "cross_sectional": 25,   # 6A range 21-30
    "vol_regime":      10,   # 6B range 5-15
    "overnight_gap":   2,    # 6C range 1-3
    "insider":         60,   # 6D range 30-90
    "breadth":         30,   # 6E range 20-40
    "drift":           45,   # 6F range 30-60
    "microstructure":  10,   # 6G range 5-15
}


def get_max_days_for_category(category: str, default: int = 30) -> int:
    """Return DEC-521 default max_days for a strategy category.

    Returns ``default`` if category is unknown OR ``None`` (e.g. confluence,
    calendar)  -  caller should compute strictest constituent for confluence
    or per-strategy override for calendar.
    """
    val = CATEGORY_TIME_STOPS_DAYS.get(category, default)
    return val if val is not None else default


def exit_class_time_stop(df_full, entry_date, entry_price, direction, atr,
                          signals=None, category: str = "momentum",
                          override_days=None):
    """DEC-521: Time stop at close of bar `max_days` per strategy category.

    Args:
        category: Layer 1 category (e.g. 'momentum', 'mean_reversion').
        override_days: optional per-strategy override; takes precedence over
                       category default.
    """
    days = override_days if override_days is not None \
           else get_max_days_for_category(category)

    future = df_full[df_full.index.date > entry_date]
    if future.empty:
        return _base_result(entry_price, entry_price, entry_date,
                            entry_date, "no_data", direction)

    target_idx = min(days - 1, len(future) - 1)
    target_row = future.iloc[target_idx]
    target_ts = future.index[target_idx]
    return _base_result(
        entry_price, float(target_row["close"]),
        entry_date,
        target_ts.date() if hasattr(target_ts, "date") else target_ts,
        f"class_time_stop_{category}_{days}d", direction,
    )


# -----------------------------------------------------------------------------
# EXIT STRATEGY REGISTRY
# -----------------------------------------------------------------------------

def exit_regime_flip(df_full, entry_date, entry_price, direction, atr, signals=None,
                     regime_series=None, max_days=20):
    """DEC-516 regime-flip exit (Pass 53 owner-approved 2026-05-06).

    Symmetric to Layer 5 entry gating: when the regime classification flips
    from the entry-day regime during the hold period, exit immediately at
    next bar's close. Falls back to time_stop_max_days if regime data
    unavailable or regime never flips within window.

    Args:
        df_full: full OHLCV DataFrame for the ticker.
        entry_date: trade entry date.
        entry_price: trade entry price.
        direction: 'long' or 'short'.
        atr: ATR at entry.
        signals: signals dict at entry (used to extract entry-regime if available).
        regime_series: optional pandas Series of regime per date (key = date).
            If not provided, falls back to signals.get('regime_at_entry') and
            re-uses it (no flip detection possible).
        max_days: maximum hold without flip -> defaults to time stop at this many days.

    Returns:
        Same _base_result dict as other exit functions.
    """
    future = df_full[df_full.index.date > entry_date] if hasattr(df_full.index, 'date') \
             else df_full[pd.to_datetime(df_full["date"]).dt.date > entry_date]
    if future.empty:
        return _base_result(entry_price, entry_price, entry_date,
                            entry_date, "no_data", direction)

    # Determine entry-day regime from signals (best-effort)
    entry_regime = None
    if isinstance(signals, dict):
        entry_regime = signals.get("regime_at_entry") or signals.get("regime")

    # If we have a regime_series, scan for the flip
    if regime_series is not None and entry_regime:
        # Future bars within max_days window
        for i, ts in enumerate(future.index[:max_days]):
            try:
                bar_date = ts.date() if hasattr(ts, 'date') else ts
                cur_regime = regime_series.get(bar_date)
                if cur_regime and cur_regime != entry_regime and cur_regime != "unknown":
                    # Flip detected  -  exit at this bar's close
                    return _base_result(
                        entry_price, float(future.iloc[i]["close"]),
                        entry_date, bar_date,
                        f"regime_flip_{entry_regime}_to_{cur_regime}", direction,
                    )
            except Exception:
                continue

    # No flip detected (or no regime data) -> fall back to time_stop at max_days
    target_idx = min(max_days - 1, len(future) - 1)
    target_row = future.iloc[target_idx]
    target_ts = future.index[target_idx]
    return _base_result(
        entry_price, float(target_row["close"]),
        entry_date,
        target_ts.date() if hasattr(target_ts, 'date') else target_ts,
        f"regime_flip_max_days_{max_days}", direction,
    )


# -----------------------------------------------------------------------------
# Pass 53 Day-9 v8g  -  DEC-517 R-multiple exits + break-even moves
# -----------------------------------------------------------------------------
# Per spec TRADING_RULES_AND_INFORMATION.md sec8.7:
#   18 exit_r_multiple_2r:    target = entry +/- 2 x stop_distance (initial-risk-parameterized)
#   19 exit_r_multiple_3r:    target = entry +/- 3 x stop_distance
#   20 exit_break_even_at_1r: move stop to entry once price reaches +1R; trail thereafter
#
# Stop distance defaults: ATR-based (1x ATR) when atr provided, else 2% of entry.
# Combined behaviors (BE+0.5R cushion, BE+1R cushion) are stretch  -  left for
# future as exit composition variants per DEC-523.


def _stop_distance(entry_price: float, atr: float, direction: str) -> float:
    """Compute initial stop distance per DEC-517 conventions."""
    if atr and atr > 0:
        return float(atr)
    return entry_price * ATR_FALLBACK_PCT


def exit_r_multiple_2r(df_full, entry_date, entry_price, direction, atr,
                        signals=None):
    """DEC-517 #18: Take profit at 2x initial risk."""
    return _exit_r_multiple_impl(df_full, entry_date, entry_price, direction,
                                  atr, r_multiple=2.0)


def exit_r_multiple_3r(df_full, entry_date, entry_price, direction, atr,
                        signals=None):
    """DEC-517 #19: Take profit at 3x initial risk."""
    return _exit_r_multiple_impl(df_full, entry_date, entry_price, direction,
                                  atr, r_multiple=3.0)


def _exit_r_multiple_impl(df_full, entry_date, entry_price, direction, atr,
                            r_multiple: float):
    """Shared R-multiple-target implementation. Stop = -1R; target = +NR.

    Uses DEC-514 fill methodology for both stop and target fills.
    """
    sd = _stop_distance(entry_price, atr, direction)
    if direction == "long":
        stop = entry_price - sd
        target = entry_price + r_multiple * sd
    else:
        stop = entry_price + sd
        target = entry_price - r_multiple * sd

    future = df_full[df_full.index.date > entry_date]
    if future.empty:
        return _base_result(entry_price, entry_price, entry_date,
                            entry_date, "no_data", direction)

    for idx, row in future.iterrows():
        bar_open = float(row.get("open", float(row["close"])))
        h = float(row["high"])
        l = float(row["low"])
        # Stop checked first (DEC-514 sec11.4 conservative bias)
        stop_fill = compute_fill_price(direction, "stop", stop, bar_open, h, l)
        if stop_fill is not None:
            return _base_result(entry_price, stop_fill, entry_date,
                                idx.date(), "r_multiple_stop", direction)
        target_fill = compute_fill_price(direction, "target", target, bar_open, h, l)
        if target_fill is not None:
            return _base_result(entry_price, target_fill, entry_date,
                                idx.date(),
                                f"r_multiple_{r_multiple:.0f}r_target", direction)

    last = future.iloc[-1]
    return _base_result(entry_price, float(last["close"]), entry_date,
                        future.index[-1].date(), "max_days", direction)


def exit_break_even_at_1r(df_full, entry_date, entry_price, direction, atr,
                            signals=None, trail_pct: float = 0.10):
    """DEC-517 #20: Move stop to break-even at +1R, then trail at trail_pct.

    Phase 1 (entry -> +1R): stop fixed at -1R from entry.
    Phase 2 (after +1R hit): stop moves to entry (break-even); trails by trail_pct
    on subsequent highs (longs) / lows (shorts).
    """
    sd = _stop_distance(entry_price, atr, direction)
    one_r = entry_price + sd if direction == "long" else entry_price - sd
    stop = entry_price - sd if direction == "long" else entry_price + sd
    be_hit = False
    best = entry_price

    future = df_full[df_full.index.date > entry_date]
    if future.empty:
        return _base_result(entry_price, entry_price, entry_date,
                            entry_date, "no_data", direction)

    for idx, row in future.iterrows():
        bar_open = float(row.get("open", float(row["close"])))
        h = float(row["high"])
        l = float(row["low"])
        close = float(row["close"])

        # Trigger break-even when +1R reached intraday
        if not be_hit:
            if direction == "long" and h >= one_r:
                stop = entry_price  # BE
                be_hit = True
            elif direction == "short" and l <= one_r:
                stop = entry_price
                be_hit = True

        # Trail after BE hit
        if be_hit:
            if direction == "long":
                if close > best:
                    best = close
                    stop = max(stop, best * (1 - trail_pct))
            else:
                if close < best:
                    best = close
                    stop = min(stop, best * (1 + trail_pct))

        # Stop fill (DEC-514)
        stop_fill = compute_fill_price(direction, "stop", stop, bar_open, h, l)
        if stop_fill is not None:
            reason = "be_trail_stop" if be_hit else "initial_1r_stop"
            return _base_result(entry_price, stop_fill, entry_date,
                                idx.date(), reason, direction)

    last = future.iloc[-1]
    return _base_result(entry_price, float(last["close"]), entry_date,
                        future.index[-1].date(), "max_days", direction)


def exit_chandelier(df_full, entry_date, entry_price, direction, atr,
                     period=22, atr_mult=3.0, max_days=252):
    """Chandelier exit (LeBeau-Lucas 1992; refined StockCharts ChartSchool
    2024). Trail stop from `rolling_high - N*ATR` (long) or
    `rolling_low + N*ATR` (short). Less whipsaw than vanilla ATR-trail
    because the anchor is the rolling extreme rather than the close.

    Batch 226 (2026-05-18 owner-approved research review exits gap).
    Default period=22 / atr_mult=3.0 matches LeBeau's original spec.
    """
    future = df_full[df_full.index.date > entry_date]
    if future.empty or atr == 0:
        return exit_trailing_pct(df_full, entry_date, entry_price,
                                  direction, atr, trail_pct=0.10)
    # Pre-compute rolling ATR (same as exit_atr_trail uses)
    h, l, c = df_full["high"], df_full["low"], df_full["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr_series = tr.ewm(alpha=1/14, adjust=False).mean()
    # Rolling extreme over `period` bars
    rolling_high = h.rolling(period).max()
    rolling_low  = l.rolling(period).min()

    stop = (entry_price - atr_mult * atr) if direction == "long" \
           else (entry_price + atr_mult * atr)

    for idx, row in future.iterrows():
        close = float(row["close"])
        low   = float(row.get("low",  close))
        high  = float(row.get("high", close))
        bar_open = float(row.get("open", close))
        try:
            current_atr = float(atr_series.loc[idx])
            if not (current_atr > 0):
                current_atr = atr
        except (KeyError, ValueError):
            current_atr = atr
        try:
            rh = float(rolling_high.loc[idx]) if direction == "long" else None
            rl = float(rolling_low.loc[idx])  if direction == "short" else None
        except (KeyError, ValueError):
            rh, rl = None, None
        if direction == "long" and rh is not None and not pd.isna(rh):
            new_stop = rh - atr_mult * current_atr
            stop = max(stop, new_stop)
        elif direction == "short" and rl is not None and not pd.isna(rl):
            new_stop = rl + atr_mult * current_atr
            stop = min(stop, new_stop)
        fill = compute_fill_price(direction, "stop", stop, bar_open, high, low)
        if fill is not None:
            return _base_result(entry_price, fill, entry_date,
                                idx.date(), "chandelier_exit", direction)
    last = future.iloc[-1]
    return _base_result(entry_price, float(last["close"]), entry_date,
                        future.index[-1].date(), "end_of_data", direction)


def exit_atr_trail_vix_conditional(df_full, entry_date, entry_price, direction, atr,
                                    signals=None, base_mult=1.0, max_days=252):
    """VIX-regime conditional ATR trailing stop. Tighter ATR multiplier
    in low-VIX (0.75x base), wider in high-VIX (1.5x base). The vix_band
    signal is set at entry by Batch 204; this exit reads it from the
    signals dict to set the per-trade ATR multiplier.

    Batch 226 (2026-05-18). Source: TradingSetupsReview 2024 "Ultimate
    Guide to Volatility Stop-Losses"; addresses the documented
    whipsaw-in-low-vol / premature-exit-in-high-vol asymmetry.

    Signals dict expected keys (optional; default to base_mult):
      vix_band_low / vix_band_mid / vix_band_high (Batch 204 macro overlay)
    """
    s = signals if signals else {}
    if s.get("vix_band_low"):
        atr_mult = base_mult * 0.75
    elif s.get("vix_band_high"):
        atr_mult = base_mult * 1.5
    else:
        atr_mult = base_mult
    # Delegate to atr_trail with the VIX-conditional multiplier
    return exit_atr_trail(df_full, entry_date, entry_price, direction, atr,
                           atr_mult=atr_mult, max_days=max_days)


def exit_mfe_lockin_trail(df_full, entry_date, entry_price, direction, atr,
                           mfe_threshold_atr=2.0, lock_back_atr=1.0, max_days=252):
    """MFE-lock-in trailing stop. When unrealized gain reaches
    `mfe_threshold_atr * ATR`, ratchet the stop to (MFE - lock_back_atr * ATR)
    to actively defend gains. Before that threshold, behaves like a
    1xATR trailing stop.

    Batch 226 (2026-05-18). Source: Howard Bandy 2014 *Quantitative
    Technical Analysis* Ch 8. Solves the "winners give back" failure
    mode of pure-trailing stops on extended winners.
    """
    future = df_full[df_full.index.date > entry_date]
    if future.empty or atr == 0:
        return exit_trailing_pct(df_full, entry_date, entry_price,
                                  direction, atr, trail_pct=0.10)
    h, l, c = df_full["high"], df_full["low"], df_full["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr_series = tr.ewm(alpha=1/14, adjust=False).mean()
    best_close = entry_price
    best_high  = entry_price
    best_low   = entry_price
    stop = (entry_price - 1.0 * atr) if direction == "long" \
           else (entry_price + 1.0 * atr)

    for idx, row in future.iterrows():
        close = float(row["close"])
        low   = float(row.get("low",  close))
        high  = float(row.get("high", close))
        bar_open = float(row.get("open", close))
        try:
            current_atr = float(atr_series.loc[idx])
            if not (current_atr > 0):
                current_atr = atr
        except (KeyError, ValueError):
            current_atr = atr
        if direction == "long":
            if high > best_high:
                best_high = high
            mfe = best_high - entry_price
            mfe_threshold = mfe_threshold_atr * current_atr
            if mfe >= mfe_threshold:
                # Lock-in: tighten stop to (best_high - lock_back_atr * ATR)
                stop = max(stop, best_high - lock_back_atr * current_atr)
            else:
                # Pre-threshold: vanilla 1xATR trail from close
                if close > best_close:
                    best_close = close
                    stop = max(stop, best_close - 1.0 * current_atr)
            fill = compute_fill_price(direction, "stop", stop, bar_open, high, low)
            if fill is not None:
                reason = ("mfe_lockin_trail" if (best_high - entry_price) >= mfe_threshold_atr * current_atr
                          else "mfe_pre_threshold_trail")
                return _base_result(entry_price, fill, entry_date,
                                    idx.date(), reason, direction)
        else:
            if low < best_low:
                best_low = low
            mfe = entry_price - best_low
            mfe_threshold = mfe_threshold_atr * current_atr
            if mfe >= mfe_threshold:
                stop = min(stop, best_low + lock_back_atr * current_atr)
            else:
                if close < best_close:
                    best_close = close
                    stop = min(stop, best_close + 1.0 * current_atr)
            fill = compute_fill_price(direction, "stop", stop, bar_open, high, low)
            if fill is not None:
                reason = ("mfe_lockin_trail" if (entry_price - best_low) >= mfe_threshold_atr * current_atr
                          else "mfe_pre_threshold_trail")
                return _base_result(entry_price, fill, entry_date,
                                    idx.date(), reason, direction)
    last = future.iloc[-1]
    return _base_result(entry_price, float(last["close"]), entry_date,
                        future.index[-1].date(), "end_of_data", direction)


def per_strategy_mae_75th_pct_of_winners(
    trade_log,
    strategy: str,
    lookback_days: int = 252,
    as_of=None,
    default_atr_mult: float = 1.0,
):
    """Compute the 75th-percentile MAE-of-winners for a strategy.

    Batch 226 (2026-05-18; deferred from research review D.4). Source:
    Sweeney 1988 *TASC*; Bandy 2014 *Quantitative Technical Analysis*.
    Per-strategy MAE-of-winners distribution gives a tailored stop
    distance: where most winners survive their worst adverse excursion.

    Returns float ATR multiplier in [0.5, 2.5] derived from |MAE_75| /
    median(|MAE|). Falls back to default_atr_mult on insufficient data.
    """
    import pandas as pd
    if trade_log is None or trade_log.empty:
        return default_atr_mult
    if "strategy" not in trade_log.columns or strategy not in trade_log["strategy"].values:
        return default_atr_mult
    df = trade_log[trade_log["strategy"] == strategy].copy()
    if as_of is not None and "entry_date" in df.columns:
        df = df[pd.to_datetime(df["entry_date"]) <= as_of]
        window_start = pd.to_datetime(as_of) - pd.Timedelta(days=lookback_days)
        df = df[pd.to_datetime(df["entry_date"]) >= window_start]
    if df.empty or "win" not in df.columns or "mae_pct" not in df.columns:
        return default_atr_mult
    winners = df[df["win"] == True]
    if len(winners) < 20:
        return default_atr_mult
    mae_abs = winners["mae_pct"].abs().dropna()
    if len(mae_abs) < 20:
        return default_atr_mult
    try:
        p75 = float(mae_abs.quantile(0.75))
        p50 = float(mae_abs.quantile(0.50))
        if p50 <= 0:
            return default_atr_mult
        # Use p75/p50 as a "tightness" ratio - winners that need more
        # room get larger ATR multipliers.
        ratio = p75 / p50
        # Map ratio to ATR multiplier in [0.5, 2.5]
        mult = float(max(0.5, min(2.5, default_atr_mult * ratio)))
        return round(mult, 3)
    except Exception:
        return default_atr_mult


def exit_atr_trail_mae_conditional(df_full, entry_date, entry_price, direction, atr,
                                     signals=None, max_days=252):
    """ATR-trailing stop with MAE-conditional multiplier per Sweeney 1988
    + Bandy 2014. Looks up the strategy's rolling MAE-of-winners 75th
    percentile from the trade log (threaded via signals['mae_atr_mult']);
    uses that as the ATR multiplier. Falls back to 1.0 (vanilla 1x ATR
    trail) when the multiplier is absent.

    Batch 226 (2026-05-18; deferred from research review D.4).
    """
    s = signals if signals else {}
    mae_mult = s.get("mae_atr_mult", 1.0)
    try:
        mae_mult = float(mae_mult)
    except (TypeError, ValueError):
        mae_mult = 1.0
    mae_mult = max(0.5, min(2.5, mae_mult))
    return exit_atr_trail(df_full, entry_date, entry_price, direction, atr,
                           atr_mult=mae_mult, max_days=max_days)


# Batch 227a (2026-05-18 owner-approved): reverse-signal exit registry.
# Maps entry strategy name -> reverse-condition evaluator callable taking
# df_slice (OHLCV up to current bar) and returning bool. Connors discipline:
# when entry signal was X-oversold, exit when X-overbought triggers. Only
# the most-fired strategies have explicit reverse mappings; strategies
# not in the registry fall back to atr_trail inside exit_reverse_signal.
def _bb_upper_touch(df, period=20, std_mult=2.0):
    if len(df) < period + 1:
        return False
    closes = df["close"].tail(period)
    mean = float(closes.mean())
    std = float(closes.std())
    return float(df["close"].iloc[-1]) >= mean + std_mult * std


def _bb_lower_touch(df, period=20, std_mult=2.0):
    if len(df) < period + 1:
        return False
    closes = df["close"].tail(period)
    mean = float(closes.mean())
    std = float(closes.std())
    return float(df["close"].iloc[-1]) <= mean - std_mult * std


def _rsi14_overbought(df, threshold=65):
    if len(df) < 16:
        return False
    closes = df["close"].tail(15)
    delta = closes.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    last_loss = float(loss.iloc[-1])
    rs_last = float(gain.iloc[-1]) / last_loss if last_loss > 0 else float("inf")
    rsi = 100 - 100 / (1 + rs_last)
    return rsi > threshold


def _rsi14_oversold(df, threshold=35):
    if len(df) < 16:
        return False
    closes = df["close"].tail(15)
    delta = closes.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    last_loss = float(loss.iloc[-1])
    rs_last = float(gain.iloc[-1]) / last_loss if last_loss > 0 else float("inf")
    rsi = 100 - 100 / (1 + rs_last)
    return rsi < threshold


def _williams_r_overbought(df, period=14, threshold=-20):
    if len(df) < period + 1:
        return False
    sub = df.tail(period)
    high_p = float(sub["high"].max())
    low_p = float(sub["low"].min())
    close = float(df["close"].iloc[-1])
    if high_p == low_p:
        return False
    wr = -100.0 * (high_p - close) / (high_p - low_p)
    return wr > threshold


def _pivot_r1_loss(df):
    """Loss of prev-day pivot R1 from below (long held above R1; reverse
    when close falls back below R1)."""
    if len(df) < 3:
        return False
    prev = df.iloc[-2]
    H, L, C = float(prev["high"]), float(prev["low"]), float(prev["close"])
    P = (H + L + C) / 3.0
    R1 = 2 * P - L
    today = float(df["close"].iloc[-1])
    return today < R1


REVERSE_SIGNAL_EVALUATORS = {
    # Mean-reversion long entries -> exit on opposing overbought touch
    "bollinger_lower":       _bb_upper_touch,
    "bollinger_tight":       _bb_upper_touch,
    "rsi_oversold":          _rsi14_overbought,
    "williams_r_oversold":   _williams_r_overbought,
    # Trend-continuation long entries -> exit on pivot R1 loss
    "pivot_r1_breakout":     _pivot_r1_loss,
    "pivot_r2_continuation": _pivot_r1_loss,
    # Short-side: reverse on oversold opposing
    "bollinger_upper_short": _bb_lower_touch,
    "rsi_overbought_short":  _rsi14_oversold,
}


def exit_reverse_signal(df_full, entry_date, entry_price, direction, atr,
                         signals=None, max_days=252):
    """Reverse-signal exit (Batch 227a 2026-05-18 owner-approved). Exit when
    the OPPOSING technical condition fires - e.g. bollinger_lower entry
    (long) exits when bb_upper touches; rsi_oversold (long) exits on
    rsi_14 > 65. Connors *Short-Term Trading Strategies That Work* discipline.

    Strategy name is read from signals['strategy_name'] (threaded by engine).
    Strategies not in REVERSE_SIGNAL_EVALUATORS fall back to vanilla
    atr_trail_1x. Bounded by max_days as a safety floor.
    """
    s = signals if signals else {}
    strategy = s.get("strategy_name") or s.get("strategy") or ""
    evaluator = REVERSE_SIGNAL_EVALUATORS.get(strategy)
    if not evaluator:
        return exit_atr_trail(df_full, entry_date, entry_price, direction, atr,
                               atr_mult=1.0, max_days=max_days)
    future = df_full[df_full.index.date > entry_date]
    if future.empty:
        return exit_trailing_pct(df_full, entry_date, entry_price,
                                  direction, atr, trail_pct=0.10)
    for idx, row in future.iterrows():
        df_slice = df_full[df_full.index <= idx]
        try:
            triggered = bool(evaluator(df_slice))
        except Exception:
            triggered = False
        if triggered:
            return _base_result(entry_price, float(row["close"]), entry_date,
                                 idx.date(),
                                 f"reverse_signal_{strategy}_batch227a",
                                 direction)
    last = future.iloc[-1]
    return _base_result(entry_price, float(last["close"]), entry_date,
                         future.index[-1].date(), "end_of_data", direction)


def exit_smc_mitigation_zone(df_full, entry_date, entry_price, direction, atr,
                              signals=None, max_days=252, smc_check_every=5):
    """SMC mitigation-zone exit (Batch 227a 2026-05-18 owner-approved).
    Exit LONG when next bearish SMC primitive fires (bearish FVG / bearish
    CHoCH / bearish OB); SHORT symmetric. Uses Batch 216 SMC infrastructure.

    SMC compute is expensive (3+ library calls per bar); to keep exit cost
    bounded we only evaluate every smc_check_every bars (default 5 trading
    days). On in-between bars we trail-stop via vanilla 1xATR as safety.
    """
    future = df_full[df_full.index.date > entry_date]
    if future.empty or atr == 0:
        return exit_trailing_pct(df_full, entry_date, entry_price,
                                  direction, atr, trail_pct=0.10)
    h, l, c = df_full["high"], df_full["low"], df_full["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr_series = tr.ewm(alpha=1/14, adjust=False).mean()
    best = entry_price
    stop = (entry_price - 1.0 * atr) if direction == "long" else (entry_price + 1.0 * atr)
    try:
        from backtest.signals.smc_ict import compute_smc_signals
    except Exception:
        compute_smc_signals = None
    for i, (idx, row) in enumerate(future.iterrows()):
        close = float(row["close"])
        high = float(row.get("high", close))
        low = float(row.get("low", close))
        bar_open = float(row.get("open", close))
        try:
            current_atr = float(atr_series.loc[idx])
            if not (current_atr > 0):
                current_atr = atr
        except (KeyError, ValueError):
            current_atr = atr
        if direction == "long":
            if close > best:
                best = close
                stop = max(stop, best - 1.0 * current_atr)
        else:
            if close < best:
                best = close
                stop = min(stop, best + 1.0 * current_atr)
        fill = compute_fill_price(direction, "stop", stop, bar_open, high, low)
        if fill is not None:
            return _base_result(entry_price, fill, entry_date,
                                 idx.date(), "smc_trail_safety_batch227a",
                                 direction)
        if compute_smc_signals is not None and (i % smc_check_every == 0):
            df_slice = df_full[df_full.index <= idx]
            try:
                smc = compute_smc_signals(df_slice)
            except Exception:
                smc = {}
            if direction == "long":
                opposing = (
                    smc.get("smc_fvg_bearish_active", False)
                    or smc.get("smc_choch_bearish", False)
                    or smc.get("smc_ob_bearish_active", False)
                )
            else:
                opposing = (
                    smc.get("smc_fvg_bullish_active", False)
                    or smc.get("smc_choch_bullish", False)
                    or smc.get("smc_ob_bullish_active", False)
                )
            if opposing:
                return _base_result(entry_price, close, entry_date,
                                     idx.date(), "smc_mitigation_batch227a",
                                     direction)
    last = future.iloc[-1]
    return _base_result(entry_price, float(last["close"]), entry_date,
                         future.index[-1].date(), "end_of_data", direction)


def exit_multi_tier_partial(df_full, entry_date, entry_price, direction, atr,
                              signals=None, max_days=252,
                              tier1_atr=1.0, tier2_atr=2.0,
                              tier1_frac=1.0/3, tier2_frac=1.0/3):
    """Multi-tier partial-fill exit (Batch 227b 2026-05-18 owner-approved).

    Source: Van Tharp *Trade Your Way to Financial Freedom*; Mark Douglas
    *Trading in the Zone*. Documented +0.2 Sharpe in retail-tested systems.

    Semantic:
      - Exit `tier1_frac` of position at `tier1_atr * ATR` profit (1R)
      - Exit `tier2_frac` of position at `tier2_atr * ATR` profit (2R)
      - Exit remaining (`1 - tier1_frac - tier2_frac`) on 1x ATR trail-stop
      - After 1R hit, ratchet stop to breakeven (locks gains on remaining)

    Implementation note: partial fills are tracked INTERNALLY via a list
    of (date, price, fraction) tuples; final PnL is the
    fraction-weighted average exit price. This avoids invasive
    OpenTrade/ClosedTrade plumbing changes - engine still sees one
    OpenTrade per signal and one ClosedTrade on full exit. Empirical
    backtest behavior matches a true partial-fill simulation; only
    portfolio gross-heat accounting is approximate (heat counts full
    position until trailing-stop closes the residual; this is a
    documented backtest convention, not a live-trading mismatch).
    """
    future = df_full[df_full.index.date > entry_date]
    if future.empty or atr == 0:
        return exit_trailing_pct(df_full, entry_date, entry_price,
                                  direction, atr, trail_pct=0.10)

    target_1r = ((entry_price + tier1_atr * atr) if direction == "long"
                  else (entry_price - tier1_atr * atr))
    target_2r = ((entry_price + tier2_atr * atr) if direction == "long"
                  else (entry_price - tier2_atr * atr))

    # Pre-compute ATR series for the trailing-stop tier
    h, l, c = df_full["high"], df_full["low"], df_full["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr_series = tr.ewm(alpha=1/14, adjust=False).mean()

    partial_fills = []   # list of (date, price, fraction)
    target_1r_hit = False
    target_2r_hit = False
    best = entry_price
    # Initial stop at -1x ATR; ratchets to breakeven after 1R hit; trails
    # thereafter via the remaining-third logic.
    stop = (entry_price - 1.0 * atr) if direction == "long" \
           else (entry_price + 1.0 * atr)

    for idx, row in future.iterrows():
        close = float(row["close"])
        high = float(row.get("high", close))
        low = float(row.get("low", close))
        bar_open = float(row.get("open", close))
        try:
            current_atr = float(atr_series.loc[idx])
            if not (current_atr > 0):
                current_atr = atr
        except (KeyError, ValueError):
            current_atr = atr

        # Tier 1: 1R target partial exit
        if not target_1r_hit:
            t1_hit = ((direction == "long" and high >= target_1r)
                      or (direction == "short" and low <= target_1r))
            if t1_hit:
                partial_fills.append((idx.date(), float(target_1r), float(tier1_frac)))
                target_1r_hit = True
                # Ratchet stop to breakeven after 1R hit
                stop = max(stop, entry_price) if direction == "long" \
                       else min(stop, entry_price)

        # Tier 2: 2R target partial exit
        if target_1r_hit and not target_2r_hit:
            t2_hit = ((direction == "long" and high >= target_2r)
                      or (direction == "short" and low <= target_2r))
            if t2_hit:
                partial_fills.append((idx.date(), float(target_2r), float(tier2_frac)))
                target_2r_hit = True

        # Tier 3: trailing stop on remaining position
        if direction == "long":
            if close > best:
                best = close
                stop = max(stop, best - 1.0 * current_atr)
        else:
            if close < best:
                best = close
                stop = min(stop, best + 1.0 * current_atr)

        fill = compute_fill_price(direction, "stop", stop, bar_open, high, low)
        if fill is not None:
            remaining = 1.0 - sum(f[2] for f in partial_fills)
            if remaining > 0:
                partial_fills.append((idx.date(), float(fill), float(remaining)))
            # Weighted-average exit price across all tiers
            total_frac = sum(f[2] for f in partial_fills)
            if total_frac <= 0:
                avg_exit = float(fill)
            else:
                avg_exit = sum(f[1] * f[2] for f in partial_fills) / total_frac
            tier_reasons = []
            if target_1r_hit: tier_reasons.append("1R")
            if target_2r_hit: tier_reasons.append("2R")
            tier_reasons.append("trail")
            return _base_result(
                entry_price, avg_exit, entry_date, idx.date(),
                f"multi_tier_{'_'.join(tier_reasons)}_batch227b",
                direction,
            )

    # End of data - exit any remaining at last close
    last_close = float(future.iloc[-1]["close"])
    remaining = 1.0 - sum(f[2] for f in partial_fills)
    if remaining > 0:
        partial_fills.append((future.index[-1].date(), last_close, float(remaining)))
    total_frac = sum(f[2] for f in partial_fills)
    avg_exit = (sum(f[1] * f[2] for f in partial_fills) / total_frac
                 if total_frac > 0 else last_close)
    return _base_result(entry_price, avg_exit, entry_date,
                         future.index[-1].date(),
                         "multi_tier_end_of_data_batch227b", direction)


def exit_smart_money_reversal(df_full, entry_date, entry_price, direction,
                                atr, signals=None, max_days=252,
                                check_every=5):
    """Batch 487 / SM2 (2026-05-30 owner-approved): smart-money reversal
    exit. While in a LONG, exit at next bar open if smart-money signal
    flips BEARISH during the hold (insider cluster_sell OR concentrated_sell
    in the trailing 5d window). For SHORT, symmetric -- exit on smart-money
    buy flip.

    Sampling: check every `check_every` bars (default 5) to keep cost
    bounded; trail-stop fallback (1xATR) on between-bars.

    Source: Cohen-Malloy-Pomorski 2012 -- insider sells while institutional
    flow remains positive is a stronger reversal signal than either alone.
    Tests: Stage 2 Phase 1A-beta cube replay; if exit-method dominance
    materialises this method earns a permanent slot in the cube via
    DEC-067.
    """
    future = df_full[df_full.index.date > entry_date]
    if future.empty or atr == 0:
        return exit_trailing_pct(df_full, entry_date, entry_price,
                                  direction, atr, trail_pct=0.10)
    ticker = (signals or {}).get("ticker", "")
    if not ticker:
        # No ticker -> fall back to ATR trail
        return exit_atr_trail(df_full, entry_date, entry_price, direction,
                              atr, 1.0)
    try:
        from backtest.data.smart_money import insider_signal
    except Exception:
        insider_signal = None
    h, l, c = df_full["high"], df_full["low"], df_full["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()],
                   axis=1).max(axis=1)
    atr_series = tr.ewm(alpha=1/14, adjust=False).mean()
    best = entry_price
    stop = (entry_price - 1.0 * atr) if direction == "long" \
        else (entry_price + 1.0 * atr)
    for i, (idx, row) in enumerate(future.iterrows()):
        close = float(row["close"])
        high = float(row.get("high", close))
        low = float(row.get("low", close))
        bar_open = float(row.get("open", close))
        try:
            current_atr = float(atr_series.loc[idx])
            if not (current_atr > 0):
                current_atr = atr
        except (KeyError, ValueError):
            current_atr = atr
        if direction == "long":
            if close > best:
                best = close
                stop = max(stop, best - 1.0 * current_atr)
        else:
            if close < best:
                best = close
                stop = min(stop, best + 1.0 * current_atr)
        # ATR trail-stop safety check
        fill = compute_fill_price(direction, "stop", stop, bar_open, high, low)
        if fill is not None:
            return _base_result(entry_price, fill, entry_date, idx.date(),
                                 "smart_money_trail_safety_batch487",
                                 direction)
        # Smart-money signal check every N bars
        if insider_signal is not None and (i % check_every == 0):
            try:
                sm = insider_signal(ticker, idx.date(), lookback_days=5)
            except Exception:
                sm = {}
            if direction == "long":
                # Exit long on bearish smart-money flip
                bearish_flip = bool(
                    sm.get("signal") in ("cluster_sell", "concentrated_sell")
                    or sm.get("concentrated_sell", False)
                )
                if bearish_flip:
                    return _base_result(
                        entry_price, bar_open, entry_date, idx.date(),
                        "smart_money_reversal_bearish_flip_batch487",
                        direction,
                    )
            else:
                # Exit short on bullish smart-money flip
                bullish_flip = bool(
                    sm.get("signal") in ("buy", "strong_buy")
                    or sm.get("cluster_buy", False)
                    or sm.get("cfo_buy", False)
                    or sm.get("large_dollar_buy", False)
                )
                if bullish_flip:
                    return _base_result(
                        entry_price, bar_open, entry_date, idx.date(),
                        "smart_money_reversal_bullish_flip_batch487",
                        direction,
                    )
    # No flip detected -> fall back to end-of-data exit at max_days
    target_idx = min(max_days - 1, len(future) - 1)
    target_row = future.iloc[target_idx]
    return _base_result(
        entry_price, float(target_row["close"]),
        entry_date, future.index[target_idx].date(),
        "smart_money_reversal_end_of_data_batch487", direction,
    )


EXIT_STRATEGIES = {
    # Batch 487 (2026-05-30 owner-approved SM2): smart-money reversal exit.
    # Exit LONG on bearish smart-money flip (cluster_sell / concentrated_sell);
    # SHORT symmetric. Roster grows 25 -> 26.
    "smart_money_reversal":   lambda df, ed, ep, d, a, s: exit_smart_money_reversal(df, ed, ep, d, a, s),
    # Batch 227b (2026-05-18 owner-approved): multi-tier partial-fill exit
    # (1/3 at 1R, 1/3 at 2R, 1/3 trails). Roster grows 24 -> 25.
    "multi_tier_partial":     lambda df, ed, ep, d, a, s: exit_multi_tier_partial(df, ed, ep, d, a, s),
    # Batch 227a (2026-05-18 owner-approved): reverse-signal + SMC
    # mitigation-zone exits. Roster grows 22 -> 24.
    "reverse_signal":         lambda df, ed, ep, d, a, s: exit_reverse_signal(df, ed, ep, d, a, s),
    "smc_mitigation_zone":    lambda df, ed, ep, d, a, s: exit_smc_mitigation_zone(df, ed, ep, d, a, s),
    # Batch 226 (2026-05-18 owner-approved research review exit gaps):
    # 4 new exit methods + VIX-spike portfolio-level kill switch in
    # exit_manager.process_day_exits. Roster grows 17 -> 21 exit methods.
    "chandelier_3x":              lambda df, ed, ep, d, a, s: exit_chandelier(df, ed, ep, d, a, period=22, atr_mult=3.0),
    "atr_trail_vix_conditional":  lambda df, ed, ep, d, a, s: exit_atr_trail_vix_conditional(df, ed, ep, d, a, s),
    "mfe_lockin_trail":           lambda df, ed, ep, d, a, s: exit_mfe_lockin_trail(df, ed, ep, d, a),
    "atr_trail_mae_conditional":  lambda df, ed, ep, d, a, s: exit_atr_trail_mae_conditional(df, ed, ep, d, a, s),
    "trailing_10pct":       lambda df, ed, ep, d, a, s: exit_trailing_pct(df, ed, ep, d, a, 0.10),
    "trailing_5pct":        lambda df, ed, ep, d, a, s: exit_trailing_pct(df, ed, ep, d, a, 0.05),
    "trailing_15pct":       lambda df, ed, ep, d, a, s: exit_trailing_pct(df, ed, ep, d, a, 0.15),
    "atr_trail_1x":         lambda df, ed, ep, d, a, s: exit_atr_trail(df, ed, ep, d, a, 1.0),
    "atr_trail_2x":         lambda df, ed, ep, d, a, s: exit_atr_trail(df, ed, ep, d, a, 2.0),
    # BUG-285 fix 2026-05-13: fixed_3r_2r had 3R/2R = 1.5:1 R:R, BELOW DEC-353 2:1 minimum.
    # Renamed to fixed_4r_2r (4R target / 2R stop = 2.0:1 R:R, meets DEC-353). Per DEC-067.
    "fixed_4r_2r":          lambda df, ed, ep, d, a, s: exit_fixed_target(df, ed, ep, d, a, 4.0, 2.0),
    "next_pivot_target":    lambda df, ed, ep, d, a, s: exit_next_pivot(df, ed, ep, d, a, s),
    "ma_exit_ema9":         lambda df, ed, ep, d, a, s: exit_ma_cross(df, ed, ep, d, a, 9),
    "time_stop_10d":        lambda df, ed, ep, d, a, s: exit_time_stop(df, ed, ep, d, a, 10),
    "time_stop_20d":        lambda df, ed, ep, d, a, s: exit_time_stop(df, ed, ep, d, a, 20),
    "breakeven_plus_trail": lambda df, ed, ep, d, a, s: exit_breakeven_trail(df, ed, ep, d, a),
    "hybrid_50pct_target":  lambda df, ed, ep, d, a, s: exit_hybrid_50pct(df, ed, ep, d, a),
    # DEC-516 (Pass 53 owner-approved 2026-05-06; engine compliance Pass 53 Day-9-evening)
    "regime_flip":          lambda df, ed, ep, d, a, s: exit_regime_flip(df, ed, ep, d, a, s),
    # DEC-517 (Pass 53 owner-approved 2026-05-06 Q2 P1; engine compliance Day-9 v8g 2026-05-07)
    "r_multiple_2r":        lambda df, ed, ep, d, a, s: exit_r_multiple_2r(df, ed, ep, d, a, s),
    "r_multiple_3r":        lambda df, ed, ep, d, a, s: exit_r_multiple_3r(df, ed, ep, d, a, s),
    "break_even_at_1r":     lambda df, ed, ep, d, a, s: exit_break_even_at_1r(df, ed, ep, d, a, s),
    # DEC-518 (Pass 53 owner-approved 2026-05-06 Q2 P1; engine compliance Day-9 v8g 2026-05-07)
    # Note: requires ticker + strategy_name; signals dict expected to carry them
    "earnings_blackout":    lambda df, ed, ep, d, a, s: exit_earnings_blackout(
        df, ed, ep, d, a, s,
        ticker=(s or {}).get("ticker", ""),
        strategy_name=(s or {}).get("strategy_name", ""),
    ),
    # DEC-521 (Pass 53 owner-approved 2026-05-06 Q2 P1; engine compliance Day-9 v8g 2026-05-07)
    # Note: category provided via signals dict; default 'momentum' (25d)
    "class_time_stop":      lambda df, ed, ep, d, a, s: exit_class_time_stop(
        df, ed, ep, d, a, s,
        category=(s or {}).get("category", "momentum"),
    ),
}


# -----------------------------------------------------------------------------
# COMPOSITE SCORE + COMPARISON
# -----------------------------------------------------------------------------

# Batch 266 cube methodology hardening (2026-05-20):
# exit_reasons that indicate the exit method did NOT actually trigger.
# When earnings_blackout etc. defaults to "no_earnings_known" the trade rides
# to end-of-data and inflates total_roi via bull-market exposure, not via the
# exit method's intended logic. These are filtered from `actual_fire_rate`.
NON_FIRE_EXIT_REASONS = {
    "no_data",
    "end_of_data",
    "max_days",
    "no_earnings_known",
    "no_upcoming_earnings",
    "earnings_tolerant_skip",
}

# Recommended-flag guardrails per COMPREHENSIVE_REVIEW_2026_05_20.md:
# (1) avg_hold_days > 250 = long-hold artifact; exit isn't doing the work.
# (2) actual_fire_rate < 0.5 = exit triggers in less than half of trades.
CUBE_MAX_AVG_HOLD_DAYS = 250
CUBE_MIN_FIRE_RATE = 0.5


def composite_score(win_rate: float, profit_factor: float,
                    max_drawdown: float) -> float:
    """
    Composite score: 40% ROI (via win_rate proxy) + 30% profit factor + 30% drawdown.
    Score 0-100. Higher = better.
    """
    # Normalise each component to 0-100
    wr_score  = min(win_rate * 100, 100)                         # 0-100
    pf_score  = min((profit_factor - 1.0) / 1.0 * 100, 100)     # PF 1.0=0, 2.0=100
    pf_score  = max(pf_score, 0)
    dd_score  = max(100 - abs(max_drawdown) * 5, 0)              # 0% DD=100, 20% DD=0
    return round(0.40 * wr_score + 0.30 * pf_score + 0.30 * dd_score, 2)


def run_exit_comparison(
    strategy_name: str,
    trades_data: list,           # list of dicts: {entry_date, entry_price, direction, atr, signals, df, ticker}
) -> tuple:
    """
    Run all 12 exit strategies against a list of trade setups.
    Returns:
      - DataFrame with one row per exit strategy (strategy-level summary)
      - DataFrame with one row per trade x exit method (trade-level detail)
    """
    results = []
    trade_detail_rows = []

    # Batch 412: dispatch table. When USE_VECTORIZED_EXITS is True, replace
    # scalar exit functions with their byte-identical numpy-vectorized
    # versions for Tier 1 methods. Methods absent from the vectorized
    # registry fall through to the scalar version.
    if USE_VECTORIZED_EXITS:
        try:
            from backtest.engine.exit_strategies_vectorized import (
                EXIT_STRATEGIES_VECTORIZED,
            )
        except ImportError as _e:
            # Batch 458 (AU2): log first import failure so a missing
            # vectorized-exits module silently degrading the engine to the
            # scalar path is visible in run logs.
            from backtest.util.silent_failure_logger import log_silent_failure
            log_silent_failure("exit_strategies_vectorized.import", _e)
            EXIT_STRATEGIES_VECTORIZED = {}
    else:
        EXIT_STRATEGIES_VECTORIZED = {}

    for exit_name, exit_fn in EXIT_STRATEGIES.items():
        # Batch 412 fast path - same key in vectorized registry overrides
        # the scalar lambda. Falls through to scalar for un-vectorized methods.
        if exit_name in EXIT_STRATEGIES_VECTORIZED:
            exit_fn = EXIT_STRATEGIES_VECTORIZED[exit_name]

        pnl_list    = []
        win_list    = []
        hold_list   = []
        reason_list = []   # Batch 266 cube hardening: track exit_reason per trade

        for t in trades_data:
            try:
                # Batch 415 (2026-05-28 owner-approved): enrich the signals
                # dict with ticker + strategy_name + category so exits that
                # depend on these keys work in cube replay. Without this,
                # exit_earnings_blackout returned no_earnings_known for 100%
                # of trades (ticker="" -> fetch_earnings_dates("") -> []),
                # and exit_class_time_stop defaulted to "momentum" regardless
                # of the strategy's real category. Other exits (atr_trail_*,
                # next_pivot_target, ma_exit_ema9, etc.) ignore unknown keys.
                base_sig = t.get("signals", {})
                if not isinstance(base_sig, dict):
                    base_sig = {}
                enriched_sig = {
                    **base_sig,
                    "ticker":        t.get("ticker", ""),
                    "strategy_name": strategy_name,
                    "category":      t.get("category",
                                          base_sig.get("category", "momentum")),
                }
                r = exit_fn(
                    t["df"], t["entry_date"], t["entry_price"],
                    t["direction"], t["atr"], enriched_sig,
                )
                pnl_list.append(r["pnl_pct"])
                win_list.append(r["win"])
                hold_list.append(r["hold_days"])
                reason_list.append(r.get("exit_reason", ""))

                # Per-trade detail row + Pass 53 Day-9-evening Tier 1-4 context
                # (DEC-594 same-commit; ~25 columns added per owner directive)
                row = {
                    "ticker":       t.get("ticker", ""),
                    "strategy":     strategy_name,
                    "entry_date":   str(t["entry_date"]),
                    "direction":    t["direction"],
                    "entry_price":  t["entry_price"],
                    "exit_method":  exit_name,
                    "pnl_pct":      round(r["pnl_pct"], 4),
                    "win":          r["win"],
                    "hold_days":    r["hold_days"],
                    "exit_price":   round(r.get("exit_price", t["entry_price"]), 4),
                    "exit_date":    str(r.get("exit_date", "")),
                    "exit_reason":  r.get("exit_reason", ""),
                }
                # Propagate entry_context (Tiers 1-4)  -  see exit_context.py
                ctx = t.get("entry_context")
                if isinstance(ctx, dict):
                    row.update(ctx)
                trade_detail_rows.append(row)
            except Exception as exc:
                logger.debug("Exit %s on %s: %s", exit_name, strategy_name, exc)

        if len(pnl_list) < 5:
            continue

        pnl_s   = pd.Series(pnl_list)
        wins    = pnl_s[pnl_s > 0].sum()
        losses  = abs(pnl_s[pnl_s < 0].sum())
        pf      = round(wins / losses, 4) if losses > 0 else 999.0
        wr      = round(sum(win_list) / len(win_list), 4)
        avg_pnl = round(pnl_s.mean(), 4)
        tot_roi = round(pnl_s.sum(), 4)

        # Max drawdown
        cum    = pnl_s.cumsum()
        peak   = cum.cummax()
        mdd    = round(float((cum - peak).min()), 4)

        cscore = composite_score(wr, pf, mdd)

        # Batch 266 cube hardening: fire-rate = fraction of trades where the
        # exit method's intended trigger actually fired (vs defaulted to a
        # non-fire reason like end_of_data / no_earnings_known). Low fire-rate
        # means total_roi is bull-market exposure, not exit-method edge.
        fired = sum(1 for rsn in reason_list if rsn not in NON_FIRE_EXIT_REASONS)
        fire_rate = round(fired / len(reason_list), 4) if reason_list else 0.0
        avg_hold = round(sum(hold_list) / len(hold_list), 1)

        results.append({
            "strategy":         strategy_name,
            "exit_method":      exit_name,
            "trades":           len(pnl_list),
            "win_rate":         wr,
            "profit_factor":    pf,
            "avg_pnl_pct":      avg_pnl,
            "total_roi_pct":    tot_roi,
            "max_drawdown_pct": mdd,
            "avg_hold_days":    avg_hold,
            "actual_fire_rate": fire_rate,
            "composite_score":  cscore,
        })

    df = pd.DataFrame(results)
    if df.empty:
        return df, pd.DataFrame()
    if "composite_score" not in df.columns:
        df["composite_score"] = 0.0
    df = df.sort_values("composite_score", ascending=False)
    if not df.empty:
        # Batch 266 cube hardening guardrails: a row is `recommended` only if
        # (a) it has the top composite_score AND (b) avg_hold_days <= 250 AND
        # (c) actual_fire_rate >= 0.5. Falls back to next-best row that
        # satisfies the guardrails. If none qualify, no row is recommended
        # (caller should treat the (strategy x regime) bucket as unresolved).
        valid_mask = (
            (df["avg_hold_days"] <= CUBE_MAX_AVG_HOLD_DAYS)
            & (df["actual_fire_rate"] >= CUBE_MIN_FIRE_RATE)
        )
        df["recommended"] = False
        if valid_mask.any():
            top_valid_idx = df[valid_mask]["composite_score"].idxmax()
            df.loc[top_valid_idx, "recommended"] = True

    trade_detail_df = pd.DataFrame(trade_detail_rows)
    return df, trade_detail_df


# ---------------------------------------------------------------------------
# Batch 394 (2026-05-27): cube-replay pool worker.
#
# save_all_outputs iterates over ~185 strategies and calls
# run_exit_comparison per strategy.  Each strategy is independent, so the
# loop is embarrassingly parallel.  This worker reuses the Batch 322
# screen-pool's `_WORKER_OHLCV` module-global so the per-task IPC payload
# stays small (no df_full sent per trade -- worker looks up by ticker).
#
# Pool lifecycle: the engine defers `_teardown_screen_pool` until AFTER
# `save_all_outputs` returns (Batch 394), so the same long-lived spawn
# pool services both screen + cube replay.
# ---------------------------------------------------------------------------
def _pool_cube_replay_worker(strategy_name, trades_data_lite):
    """Worker called by multiprocessing.Pool.starmap.

    Args:
        strategy_name: str -- strategy id
        trades_data_lite: list of dicts WITHOUT `df` key; worker pulls
            OHLCV from screener._WORKER_OHLCV (initialized via _pool_init
            with the engine's ohlcv_dict).

    Returns:
        (exit_compare_df, trade_detail_df) -- same shape as
        run_exit_comparison's output.
    """
    from backtest.signals import screener  # for _WORKER_OHLCV
    ohlcv = getattr(screener, "_WORKER_OHLCV", None)
    if ohlcv is None:
        # Worker not initialized (initializer never ran); return empty
        # to surface the issue at the merge step rather than crashing.
        logger.warning(
            "Batch 394 cube worker: _WORKER_OHLCV is None for %s; "
            "returning empty (pool initializer never fired)", strategy_name,
        )
        return pd.DataFrame(), pd.DataFrame()

    trades_data_full = []
    for t in trades_data_lite:
        ticker = t.get("ticker")
        df_full = ohlcv.get(ticker)
        if df_full is None:
            continue
        trades_data_full.append({**t, "df": df_full})

    if not trades_data_full:
        return pd.DataFrame(), pd.DataFrame()
    return run_exit_comparison(strategy_name, trades_data_full)
