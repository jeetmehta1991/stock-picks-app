"""Multi-timeframe bias signals + Power of 3 (PO3) daily candle pattern.

Batch 217 (2026-05-18 owner-approved expansion of the SMC/ICT family).
Two complementary additions:

1. Multi-timeframe bias: resample daily OHLCV -> weekly and monthly,
   compute trend orientation on each higher timeframe, expose as
   signals daily strategies can read via the signal dict. Higher-TF
   bias as a filter on lower-TF entries is a canonical institutional
   discipline ("trade in the direction of the weekly trend"). The
   existing compute_ichimoku already does a weekly Kumo resample
   (Batch 207); this module generalizes to EMA / momentum / range
   signals at weekly and monthly granularity.

2. Power of 3 (PO3): Inner Circle Trader concept describing daily
   candle structure as Accumulation -> Manipulation -> Distribution.
   - Bullish PO3 daily: open near high of the candle, manipulation
     sweeps below prior day low to grab sell-side liquidity, then
     distribution drives price up, closing in the upper third of
     the bar's range. The intraday low/high info from daily OHLCV
     is enough to detect this pattern on daily bars.
   - Bearish PO3: symmetric inverse - open near low, manipulation
     sweeps above prior high, then distribution down, close in
     lower third.

Both modules expose computation helpers that screener.py merges into
the per-ticker signal dict. New strategies in screener.py consume the
resulting signal keys.

References:
  - ICT Power of 3 concept (Inner Circle Trader Mentorship)
  - Multi-timeframe analysis canonical institutional discipline
    (Brian Shannon "Maximum Trading Gains" 2022; Linda Raschke
    weekly-trend filter)
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def compute_weekly_bias(df: pd.DataFrame) -> dict:
    """Resample daily OHLCV to weekly bars and return bias signals.

    Requires DatetimeIndex on the input + 100+ daily bars (about 20
    weekly bars after resample for stable EMA/momentum). Returns empty
    dict when prerequisites not met (no exception).

    Output keys (all optional; absent when insufficient data):
      - weekly_close:        last weekly close
      - weekly_ema_10:       10-week EMA
      - weekly_ema_20:       20-week EMA
      - weekly_above_ema_10: bool (above short-term weekly trend)
      - weekly_above_ema_20: bool (above intermediate weekly trend)
      - weekly_bias_bull:    bool (weekly_above_ema_10 AND _20)
      - weekly_bias_bear:    bool (NOT above either)
      - weekly_momentum_4w:  4-week price change pct (decimal)
      - weekly_momentum_pos: bool (4w momentum > 0)
    """
    if df is None or df.empty or not isinstance(df.index, pd.DatetimeIndex):
        return {}
    if len(df) < 100:
        return {}
    try:
        wk = df.resample("W").agg({
            "open":   "first",
            "high":   "max",
            "low":    "min",
            "close":  "last",
            "volume": "sum",
        }).dropna()
    except Exception:
        return {}
    if len(wk) < 22:
        return {}
    out: dict = {}
    close = float(wk["close"].iloc[-1])
    ema_10 = float(wk["close"].ewm(span=10, adjust=False).mean().iloc[-1])
    ema_20 = float(wk["close"].ewm(span=20, adjust=False).mean().iloc[-1])
    above_10 = close > ema_10
    above_20 = close > ema_20
    out["weekly_close"]        = round(close, 4)
    out["weekly_ema_10"]       = round(ema_10, 4)
    out["weekly_ema_20"]       = round(ema_20, 4)
    out["weekly_above_ema_10"] = above_10
    out["weekly_above_ema_20"] = above_20
    out["weekly_bias_bull"]    = bool(above_10 and above_20)
    out["weekly_bias_bear"]    = bool((not above_10) and (not above_20))
    # 4-week momentum (1 month)
    if len(wk) >= 5:
        prior = float(wk["close"].iloc[-5])
        if prior > 0:
            mom_4w = (close - prior) / prior
            out["weekly_momentum_4w"]  = round(mom_4w, 4)
            out["weekly_momentum_pos"] = bool(mom_4w > 0)
    return out


def compute_monthly_bias(df: pd.DataFrame) -> dict:
    """Resample daily OHLCV to month-end bars and return bias signals.

    Requires DatetimeIndex + ~260 daily bars (~12 monthly bars after
    resample for stable 6-month SMA). Returns empty dict on
    insufficient data.

    Output keys:
      - monthly_close:        last monthly close
      - monthly_sma_6:        6-month SMA
      - monthly_sma_12:       12-month SMA
      - monthly_above_sma_6:  bool
      - monthly_above_sma_12: bool
      - monthly_bias_bull:    bool (above BOTH SMAs)
      - monthly_bias_bear:    bool (below BOTH SMAs)
      - monthly_momentum_6m:  6-month price change pct
      - monthly_momentum_pos: bool (6m momentum > 0)
    """
    if df is None or df.empty or not isinstance(df.index, pd.DatetimeIndex):
        return {}
    if len(df) < 260:
        return {}
    try:
        # ME = month-end resample. ('M' is deprecated alias for 'ME' in
        # recent pandas; use 'ME' for compatibility with current and
        # future versions.)
        try:
            m = df.resample("ME").agg({
                "open":   "first",
                "high":   "max",
                "low":    "min",
                "close":  "last",
                "volume": "sum",
            }).dropna()
        except (ValueError, KeyError):
            m = df.resample("M").agg({
                "open":   "first",
                "high":   "max",
                "low":    "min",
                "close":  "last",
                "volume": "sum",
            }).dropna()
    except Exception:
        return {}
    if len(m) < 13:
        return {}
    out: dict = {}
    close = float(m["close"].iloc[-1])
    sma_6  = float(m["close"].rolling(6).mean().iloc[-1])
    sma_12 = float(m["close"].rolling(12).mean().iloc[-1])
    above_6  = close > sma_6
    above_12 = close > sma_12
    out["monthly_close"]        = round(close, 4)
    out["monthly_sma_6"]        = round(sma_6, 4)
    out["monthly_sma_12"]       = round(sma_12, 4)
    out["monthly_above_sma_6"]  = above_6
    out["monthly_above_sma_12"] = above_12
    out["monthly_bias_bull"]    = bool(above_6 and above_12)
    out["monthly_bias_bear"]    = bool((not above_6) and (not above_12))
    if len(m) >= 7:
        prior = float(m["close"].iloc[-7])
        if prior > 0:
            mom = (close - prior) / prior
            out["monthly_momentum_6m"]  = round(mom, 4)
            out["monthly_momentum_pos"] = bool(mom > 0)
    return out


def compute_htf_alignment(weekly: dict, monthly: dict) -> dict:
    """Compose weekly + monthly bias into HTF alignment signals.

    Returns:
      - htf_aligned_bull: weekly_bias_bull AND monthly_bias_bull
      - htf_aligned_bear: weekly_bias_bear AND monthly_bias_bear
      - htf_disagreement: True when timeframes disagree (chop / regime
        transition signal)
    """
    out: dict = {}
    if not weekly and not monthly:
        return out
    wk_bull = weekly.get("weekly_bias_bull", False)
    wk_bear = weekly.get("weekly_bias_bear", False)
    mo_bull = monthly.get("monthly_bias_bull", False)
    mo_bear = monthly.get("monthly_bias_bear", False)
    out["htf_aligned_bull"] = bool(wk_bull and mo_bull)
    out["htf_aligned_bear"] = bool(wk_bear and mo_bear)
    out["htf_disagreement"] = bool(
        (wk_bull and mo_bear) or (wk_bear and mo_bull)
    )
    return out


def compute_po3_signal(df: pd.DataFrame) -> dict:
    """Compute Power of 3 (PO3) daily candle pattern signals.

    PO3 (Inner Circle Trader): each daily candle has 3 phases -
    Accumulation -> Manipulation -> Distribution. Bullish PO3:
      - open near high of day's range
      - manipulation sweeps below prior day's low (sell-side liquidity grab)
      - distribution: close in upper third of today's range
    Bearish PO3 symmetric inverse.

    Detection on daily bars:
      Bullish PO3:
        today_low <= prev_day_low * (1 + sweep_tol)  (manipulation sweep)
        today_close > today_open                       (distribution up)
        (today_close - today_low) / (today_high - today_low) > 0.66
          (close in upper third)
      Bearish PO3:
        today_high >= prev_day_high * (1 - sweep_tol)
        today_close < today_open
        (today_close - today_low) / (today_high - today_low) < 0.33

    Returns empty dict when insufficient data (need >=2 daily bars).

    Output keys:
      - po3_bullish: bool
      - po3_bearish: bool
      - po3_close_position: float in [0, 1] (0=at low, 1=at high)
      - po3_sweep_below_prior_low: bool
      - po3_sweep_above_prior_high: bool
    """
    if df is None or df.empty or len(df) < 2:
        return {}
    try:
        today = df.iloc[-1]
        prev  = df.iloc[-2]
        t_open  = float(today["open"])
        t_high  = float(today["high"])
        t_low   = float(today["low"])
        t_close = float(today["close"])
        p_high  = float(prev["high"])
        p_low   = float(prev["low"])
    except (KeyError, ValueError, TypeError):
        return {}
    rng = t_high - t_low
    if rng <= 0:
        return {}
    close_position = (t_close - t_low) / rng
    sweep_tol = 0.001  # 0.1% tolerance on sweep below/above prior
    sweep_below = t_low <= p_low * (1 + sweep_tol)
    sweep_above = t_high >= p_high * (1 - sweep_tol)
    po3_bull = bool(
        sweep_below
        and t_close > t_open
        and close_position > 0.66
    )
    po3_bear = bool(
        sweep_above
        and t_close < t_open
        and close_position < 0.33
    )
    return {
        "po3_bullish":                  po3_bull,
        "po3_bearish":                  po3_bear,
        "po3_close_position":           round(close_position, 4),
        "po3_sweep_below_prior_low":    sweep_below,
        "po3_sweep_above_prior_high":   sweep_above,
    }
