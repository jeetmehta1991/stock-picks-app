"""
engine/exit_strategies.py — All 12 exit strategies for comparison testing.

Each exit strategy is applied to every trade independently.
Results are compared using composite score: 40% ROI + 30% profit factor + 30% drawdown.

Exit strategies:
  1.  trailing_10pct        — 10% trailing stop (confirmed primary)
  2.  trailing_5pct         — 5% trailing stop (tighter)
  3.  trailing_15pct        — 15% trailing stop (looser)
  4.  atr_trail_1x          — 1× ATR trailing stop
  5.  atr_trail_2x          — 2× ATR trailing stop
  6.  fixed_3r_2r           — Fixed: 3× ATR target / 2× ATR stop
  7.  next_pivot_target      — Exit at next pivot level above entry
  8.  ma_exit_ema9           — Exit when price crosses below EMA-9
  9.  time_stop_10d          — Exit at close of day 10
  10. time_stop_20d          — Exit at close of day 20
  11. breakeven_plus_trail   — Move stop to breakeven at 1× ATR profit, then trail 10%
  12. hybrid_50pct_target    — Take 50% off at 3× ATR, trail remainder at 10%
"""

import logging
import numpy as np
import pandas as pd
from typing import Optional

# Pass 53 Day-9 v8e DEC-514 — Backtest fill methodology.
# Use compute_fill_price() at every intraday-stop / target trigger so gap-through
# events fill at bar_open (realistic broker behavior) instead of silently
# filling at the stop/target level (which would understate downside on
# overnight gap-downs and overstate winners on gap-ups). Spec: TRADING_RULES_AND_INFORMATION.md §11.
from backtest.engine.exit_manager import compute_fill_price

logger = logging.getLogger(__name__)


def _pnl(entry: float, exit_p: float, direction: str) -> float:
    if direction == "long":
        return (exit_p - entry) / entry * 100
    return (entry - exit_p) / entry * 100


def _atr_value(df_slice: pd.DataFrame, period: int = 14) -> float:
    """Compute ATR from a DataFrame slice."""
    if len(df_slice) < period:
        return df_slice["close"].iloc[-1] * 0.02
    h, l, c = df_slice["high"], df_slice["low"], df_slice["close"]
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return float(tr.ewm(alpha=1/period, adjust=False).mean().iloc[-1])


# ─────────────────────────────────────────────────────────────────────────────
# INDIVIDUAL EXIT SIMULATORS
# Each takes: df_full (full OHLCV), entry_date, entry_price, direction, atr
# Returns: dict with exit_price, exit_date, exit_reason, pnl_pct, hold_days
# ─────────────────────────────────────────────────────────────────────────────

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
        # No max_days force exit — only trailing stop and circuit breakers exit trades
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

    DEC-311 fix (Pass 51): stop distance now adapts to CURRENT volatility
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
        # No max_days force exit — only trailing stop and circuit breakers exit trades
        close = float(row["close"])
        low   = float(row.get("low",  close))
        high  = float(row.get("high", close))
        bar_open = float(row.get("open", close))  # DEC-514
        # DEC-311: use TODAY's ATR for stop-distance (refreshed daily)
        try:
            current_atr = float(atr_series.loc[idx])
            if not (current_atr > 0):  # NaN or zero — fall back to entry ATR
                current_atr = atr
        except (KeyError, ValueError):
            current_atr = atr
        if direction == "long":
            if close > best:
                best = close
                # Stop ratchets up only — uses current ATR for distance
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
        atr = entry_price * 0.02
    target = (entry_price + target_mult * atr) if direction == "long" \
             else (entry_price - target_mult * atr)
    stop   = (entry_price - stop_mult * atr)   if direction == "long" \
             else (entry_price + stop_mult * atr)

    future = df_full[df_full.index.date > entry_date]
    if future.empty:
        return _base_result(entry_price, entry_price, entry_date,
                            entry_date, "no_data", direction)

    for i, (idx, row) in enumerate(future.iterrows()):
        # No max_days force exit — only trailing stop and circuit breakers exit trades
        h, l = float(row["high"]), float(row["low"])
        bar_open = float(row.get("open", float(row["close"])))  # DEC-514
        # DEC-514 §11.4: stop checked first (conservative — when both stop and
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
        # Fall back to 3× ATR if no pivot available
        return exit_fixed_target(df_full, entry_date, entry_price,
                                  direction, atr, target_mult=3.0)

    stop = (entry_price * 0.90) if direction == "long" else (entry_price * 1.10)
    future = df_full[df_full.index.date > entry_date]
    if future.empty:
        return _base_result(entry_price, entry_price, entry_date,
                            entry_date, "no_data", direction)

    for i, (idx, row) in enumerate(future.iterrows()):
        # No max_days force exit — only trailing stop and circuit breakers exit trades
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
        # No max_days force exit — only trailing stop and circuit breakers exit trades
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
        # Hard stop (intraday L/H — DEC-514 fill methodology)
        stop_fill = compute_fill_price(direction, "stop", stop, bar_open, high, low)
        if stop_fill is not None:
            return _base_result(entry_price, stop_fill, entry_date,
                                idx.date(), "hard_stop", direction)
        # MA-cross (close-based by design — separate from DEC-514 stop fills)
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
    """Move stop to breakeven once 1× ATR in profit, then trail at 10%."""
    if atr == 0:
        atr = entry_price * 0.02
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
        # No max_days force exit — only trailing stop and circuit breakers exit trades
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
    """Take 50% off at 3× ATR, trail remaining 50% at 10%."""
    if atr == 0:
        atr = entry_price * 0.02
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
        # DEC-312 fix (Pass 51): max_days check removed for parity with other
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


# ─────────────────────────────────────────────────────────────────────────────
# EXIT STRATEGY REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

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
        max_days: maximum hold without flip → defaults to time stop at this many days.

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
                    # Flip detected — exit at this bar's close
                    return _base_result(
                        entry_price, float(future.iloc[i]["close"]),
                        entry_date, bar_date,
                        f"regime_flip_{entry_regime}_to_{cur_regime}", direction,
                    )
            except Exception:
                continue

    # No flip detected (or no regime data) → fall back to time_stop at max_days
    target_idx = min(max_days - 1, len(future) - 1)
    target_row = future.iloc[target_idx]
    target_ts = future.index[target_idx]
    return _base_result(
        entry_price, float(target_row["close"]),
        entry_date,
        target_ts.date() if hasattr(target_ts, 'date') else target_ts,
        f"regime_flip_max_days_{max_days}", direction,
    )


EXIT_STRATEGIES = {
    "trailing_10pct":       lambda df, ed, ep, d, a, s: exit_trailing_pct(df, ed, ep, d, a, 0.10),
    "trailing_5pct":        lambda df, ed, ep, d, a, s: exit_trailing_pct(df, ed, ep, d, a, 0.05),
    "trailing_15pct":       lambda df, ed, ep, d, a, s: exit_trailing_pct(df, ed, ep, d, a, 0.15),
    "atr_trail_1x":         lambda df, ed, ep, d, a, s: exit_atr_trail(df, ed, ep, d, a, 1.0),
    "atr_trail_2x":         lambda df, ed, ep, d, a, s: exit_atr_trail(df, ed, ep, d, a, 2.0),
    "fixed_3r_2r":          lambda df, ed, ep, d, a, s: exit_fixed_target(df, ed, ep, d, a, 3.0, 2.0),
    "next_pivot_target":    lambda df, ed, ep, d, a, s: exit_next_pivot(df, ed, ep, d, a, s),
    "ma_exit_ema9":         lambda df, ed, ep, d, a, s: exit_ma_cross(df, ed, ep, d, a, 9),
    "time_stop_10d":        lambda df, ed, ep, d, a, s: exit_time_stop(df, ed, ep, d, a, 10),
    "time_stop_20d":        lambda df, ed, ep, d, a, s: exit_time_stop(df, ed, ep, d, a, 20),
    "breakeven_plus_trail": lambda df, ed, ep, d, a, s: exit_breakeven_trail(df, ed, ep, d, a),
    "hybrid_50pct_target":  lambda df, ed, ep, d, a, s: exit_hybrid_50pct(df, ed, ep, d, a),
    # DEC-516 (Pass 53 owner-approved 2026-05-06; engine compliance Pass 53 Day-9-evening)
    "regime_flip":          lambda df, ed, ep, d, a, s: exit_regime_flip(df, ed, ep, d, a, s),
}


# ─────────────────────────────────────────────────────────────────────────────
# COMPOSITE SCORE + COMPARISON
# ─────────────────────────────────────────────────────────────────────────────

def composite_score(win_rate: float, profit_factor: float,
                    max_drawdown: float) -> float:
    """
    Composite score: 40% ROI (via win_rate proxy) + 30% profit factor + 30% drawdown.
    Score 0–100. Higher = better.
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
      - DataFrame with one row per trade × exit method (trade-level detail)
    """
    results = []
    trade_detail_rows = []

    for exit_name, exit_fn in EXIT_STRATEGIES.items():
        pnl_list  = []
        win_list  = []
        hold_list = []

        for t in trades_data:
            try:
                r = exit_fn(
                    t["df"], t["entry_date"], t["entry_price"],
                    t["direction"], t["atr"], t.get("signals", {}),
                )
                pnl_list.append(r["pnl_pct"])
                win_list.append(r["win"])
                hold_list.append(r["hold_days"])

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
                }
                # Propagate entry_context (Tiers 1-4) — see exit_context.py
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

        results.append({
            "strategy":         strategy_name,
            "exit_method":      exit_name,
            "trades":           len(pnl_list),
            "win_rate":         wr,
            "profit_factor":    pf,
            "avg_pnl_pct":      avg_pnl,
            "total_roi_pct":    tot_roi,
            "max_drawdown_pct": mdd,
            "avg_hold_days":    round(sum(hold_list) / len(hold_list), 1),
            "composite_score":  cscore,
        })

    df = pd.DataFrame(results)
    if df.empty:
        return df, pd.DataFrame()
    if "composite_score" not in df.columns:
        df["composite_score"] = 0.0
    df = df.sort_values("composite_score", ascending=False)
    if not df.empty:
        df["recommended"] = df.index == df["composite_score"].idxmax()

    trade_detail_df = pd.DataFrame(trade_detail_rows)
    return df, trade_detail_df
