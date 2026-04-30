"""
engine/regime_filter.py — VIX + SPY regime classification (Option B).

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
    'unknown' is a fail-closed signal — REGIME_FILTER['unknown'] blocks new
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
    # missing data. Now 'unknown' has long='none' / short='none' → blocks entries.
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
            "bull":    "VIX < 20, SPY above 200 EMA — risk-on, favour longs",
            "neutral": "Mixed conditions — both directions allowed at full size",
            "bear":    "VIX > 30, SPY below 200 EMA — favour shorts",
            "crisis":  "VIX > 40 — reduce long size to 50%, require VERY HIGH min tier. Do NOT tighten stops (causes whipsawing).",
            "unknown": "Insufficient data (no VIX) — fail closed, block new entries (DEC-316)",
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
