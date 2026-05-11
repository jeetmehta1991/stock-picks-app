"""
engine/regime_filter.py  -  VIX + SPY regime classification (Option B).

Classifies market into: bull / neutral / bear / crisis
Used to:
  - Gate which trade directions are allowed
  - Scale position sizes
  - Determine if short-to-long conversion is permitted
"""

import logging
from datetime import date, timedelta
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


def classify_regime(
    vix_value: Optional[float],
    spy_above_200ema: Optional[bool],
) -> str:
    """
    Classify market regime from VIX level and SPY vs 200 EMA.

    Returns: 'bull' | 'neutral' | 'bear' | 'crisis' | 'unknown'

    DEC-316 fix (Pass 51): returns 'unknown' on missing VIX data instead of
    silently defaulting to 'neutral'. Previously, a cache miss or data feed
    failure caused the system to trade as if conditions were normal. Now
    'unknown' is a fail-closed signal  -  REGIME_FILTER['unknown'] blocks new
    entries; existing positions continue under their original stop logic.
    """
    if vix_value is None:
        return "unknown"

    if vix_value >= 40:
        return "crisis"
    if vix_value >= 30 and spy_above_200ema is False:
        return "bear"
    if vix_value < 20 and spy_above_200ema is True:
        return "bull"
    return "neutral"


def get_regime_context(
    vix_value: Optional[float],
    spy_close: Optional[float],
    spy_ema200: Optional[float],
) -> dict:
    """
    Full regime context dict including position size multipliers.
    Used by engine and site card generator.
    """
    from backtest.config import REGIME_FILTER, POSITION_SIZE_MULT

    spy_above = (spy_close > spy_ema200
                 if spy_close and spy_ema200 else None)
    regime    = classify_regime(vix_value, spy_above)
    # DEC-316 fix (Pass 51): when regime is 'unknown', use unknown config (block).
    # Previously fell through to 'neutral' which silently allowed trading on
    # missing data. Now 'unknown' has long='none' / short='none' -> blocks entries.
    cfg       = REGIME_FILTER.get(regime, REGIME_FILTER["unknown"])

    long_mult  = POSITION_SIZE_MULT.get(cfg.get("long", "full"), 1.0)
    short_mult = POSITION_SIZE_MULT.get(cfg.get("short", "full"), 1.0)

    return {
        "regime":              regime,
        "vix":                 round(vix_value, 2) if vix_value else None,
        "spy_above_200ema":    spy_above,
        "long_allowed":        long_mult > 0,
        "short_allowed":       short_mult > 0,
        "long_size_mult":      long_mult,
        "short_size_mult":     short_mult,
        "conversion_allowed":  regime == "bull",
        "description":         {
            "bull":    "VIX < 20, SPY above 200 EMA  -  risk-on, favour longs",
            "neutral": "Mixed conditions  -  both directions allowed at full size",
            "bear":    "VIX > 30, SPY below 200 EMA  -  favour shorts",
            "crisis":  "VIX > 40  -  reduce long size to 50%, require VERY HIGH min tier. Do NOT tighten stops (causes whipsawing).",
            "unknown": "Insufficient data (no VIX)  -  fail closed, block new entries (DEC-316)",
        }.get(regime, ""),
    }


def get_spy_ema200(spy_df: pd.DataFrame, as_of: date) -> Optional[float]:
    """Compute SPY 200-day EMA as of a given date."""
    if spy_df is None or spy_df.empty:
        return None
    sliced = spy_df[spy_df.index.date <= as_of]
    if len(sliced) < 200:
        return None
    ema = sliced["close"].ewm(span=200, adjust=False).mean()
    return float(ema.iloc[-1])


# DEC-317 + DEC-388 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 42
# 2026-05-11 (owner-approved Path C). VIX 5-day SMA smoothing + hysteresis
# prevents regime flips on single noisy VIX prints. Previously hard
# thresholds (40/30/20) on raw VIX caused regime oscillation during spikes
# that reverted within 1-2 days.

def get_vix_smoothed(vix_series: pd.Series, as_of: date, window: int = 5) -> Optional[float]:
    """Return N-day SMA of VIX at or before `as_of`.

    DEC-388 Phase 3 Batch 42: smooths VIX before threshold application.
    Default window=5 trading days per DEC-388 spec ("vix_sma_5 = VIX.rolling(5).mean()").

    Inputs:
      vix_series: pd.Series of VIX values indexed by date
      as_of: target date
      window: SMA window (default 5)

    Returns float SMA or None if insufficient data.
    """
    if vix_series is None or len(vix_series) < window:
        return None
    try:
        # Filter to as_of-or-before
        if hasattr(vix_series.index, 'date'):
            sliced = vix_series[vix_series.index.date <= as_of]
        else:
            sliced = vix_series[vix_series.index <= as_of]
        if len(sliced) < window:
            return None
        sma = float(sliced.rolling(window).mean().iloc[-1])
        if pd.isna(sma):
            return None
        return sma
    except Exception:
        return None


def classify_regime_with_hysteresis(
    vix_value: Optional[float],
    spy_above_200ema: Optional[bool],
    prev_regime: Optional[str] = None,
    hysteresis_buffer: float = 5.0,
) -> str:
    """Classify regime with hysteresis-buffer applied to VIX thresholds.

    DEC-317 + DEC-388: prevents oscillation when VIX hovers near a threshold.
    Once in a regime, the VIX must move past threshold +/- buffer to switch.
    Without hysteresis a VIX print of 39.9 -> 40.1 -> 39.5 would flip the
    regime 3 times in 3 days. With hysteresis (buffer=5), to EXIT crisis the
    VIX must drop to <= 35 (40 - 5); to ENTER crisis it must rise to >= 40.

    Buffers applied symmetrically to all threshold pairs:
      crisis entry: VIX >= 40; exit: VIX < 35
      bear entry: VIX >= 30; exit: VIX < 25
      bull entry: VIX < 20; exit: VIX >= 25 (back to neutral)

    Inputs:
      vix_value: smoothed VIX (use get_vix_smoothed); raw VIX also acceptable
        for callers that don't want smoothing
      spy_above_200ema: same as classify_regime
      prev_regime: previous day's regime (passed by engine); None first day
      hysteresis_buffer: VIX points (default 5)

    Returns: 'bull' | 'neutral' | 'bear' | 'crisis' | 'unknown'
    """
    if vix_value is None:
        return "unknown"

    # Hysteresis thresholds depend on prev_regime
    if prev_regime == "crisis":
        # Stay in crisis until VIX drops well below 40
        if vix_value >= 40 - hysteresis_buffer:
            return "crisis"
        # else fall through to lower thresholds
    if prev_regime == "bear":
        # Stay in bear until VIX drops well below 30
        if vix_value >= 30 - hysteresis_buffer and spy_above_200ema is False:
            return "bear"
    if prev_regime == "bull":
        # Stay in bull until VIX rises well above 20
        if vix_value < 20 + hysteresis_buffer and spy_above_200ema is True:
            return "bull"

    # Standard entry thresholds (same as classify_regime)
    if vix_value >= 40:
        return "crisis"
    if vix_value >= 30 and spy_above_200ema is False:
        return "bear"
    if vix_value < 20 and spy_above_200ema is True:
        return "bull"
    return "neutral"
