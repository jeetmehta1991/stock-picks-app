"""Batch 586 (2026-06-04) -- sector strength producer per owner
directive 2026-06-04 (52w_high_breakout walk): "Sector strength
filter - add".

Emits `sector_outperforming_spy` boolean: True when the stock's
sector ETF's trailing 20-day return is greater than SPY's trailing
20-day return as of `as_of`. Used as additional confluence filter
on 52w_high_breakout (and potentially other breakout strategies in
future).

PIT-safe: reads OHLCV parquets at `as_of`, no look-ahead.
Local-scope: only consumed by strat_52w_high_breakout (B586). Future
additive consumers welcomed.

Sector -> ETF mapping (GICS-aligned with backtest/data/universe.py):
  Information Technology -> XLK
  Financials             -> XLF
  Energy                 -> XLE
  Health Care            -> XLV
  Industrials            -> XLI
  Consumer Discretionary -> XLY
  Consumer Staples       -> XLP
  Utilities              -> XLU
  Materials              -> XLB
  Real Estate            -> XLRE
  Communication Services -> XLC (added; not in universe.py ETF map yet)

Returns empty dict if:
  - Stock sector unknown / not in SECTOR_TO_ETF map
  - Sector ETF OHLCV cache missing or too short
  - SPY OHLCV cache missing
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd


REPO = Path(__file__).resolve().parents[2]
OHLCV_DIR = REPO / "data_prefetch" / "polygon" / "ohlcv_daily"

# GICS sector -> sector-SPDR ETF ticker
SECTOR_TO_ETF: dict[str, str] = {
    "Information Technology": "XLK",
    "Financials":             "XLF",
    "Energy":                 "XLE",
    "Health Care":            "XLV",
    "Industrials":            "XLI",
    "Consumer Discretionary": "XLY",
    "Consumer Staples":       "XLP",
    "Utilities":              "XLU",
    "Materials":              "XLB",
    "Real Estate":            "XLRE",
    "Communication Services": "XLC",
}

# Module-level cache: one read per ETF/SPY per process.
_OHLCV_BY_TICKER: dict[str, pd.DataFrame] = {}


def _load_ohlcv(ticker: str) -> Optional[pd.DataFrame]:
    """Load OHLCV parquet for ticker. Returns None on miss."""
    if ticker in _OHLCV_BY_TICKER:
        return _OHLCV_BY_TICKER[ticker]
    path = OHLCV_DIR / f"{ticker}.parquet"
    if not path.exists():
        _OHLCV_BY_TICKER[ticker] = None
        return None
    try:
        df = pd.read_parquet(path)
        # Normalize date column
        if "date" in df.columns:
            df = df.set_index(pd.to_datetime(df["date"]))
        elif not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        _OHLCV_BY_TICKER[ticker] = df
        return df
    except Exception:
        _OHLCV_BY_TICKER[ticker] = None
        return None


def _trailing_return(df: pd.DataFrame, as_of: date, lookback_days: int = 20) -> Optional[float]:
    """Return = (close_at_as_of / close_at_as_of_minus_lookback) - 1.
    Returns None if not enough data."""
    if df is None or df.empty:
        return None
    as_of_ts = pd.Timestamp(as_of)
    sub = df[df.index <= as_of_ts]
    if len(sub) < lookback_days + 1:
        return None
    close_now = float(sub["close"].iloc[-1])
    close_then = float(sub["close"].iloc[-(lookback_days + 1)])
    if close_then <= 0:
        return None
    return (close_now / close_then) - 1.0


def compute_sector_strength_signals(
    ticker_sector: str,
    as_of: date,
    lookback_days: int = 20,
) -> dict:
    """Compute sector_outperforming_spy boolean for a stock given its
    sector name.

    Args:
      ticker_sector: GICS sector name (e.g. "Information Technology").
        Caller resolves via universe.get_sector_pit(ticker, as_of).
      as_of: PIT date for the comparison.
      lookback_days: trailing return window (default 20 trading days).

    Returns:
      {
        "sector_outperforming_spy":   bool,
        "sector_etf_return_20d":      float,  # decimal e.g. 0.034 = 3.4%
        "spy_return_20d":             float,
        "sector_etf_ticker":          str (e.g. "XLK")
      }
      Empty dict if mapping miss / data miss.
    """
    out: dict = {}
    etf = SECTOR_TO_ETF.get(ticker_sector)
    if not etf:
        return out
    sector_df = _load_ohlcv(etf)
    spy_df = _load_ohlcv("SPY")
    if sector_df is None or spy_df is None:
        return out
    sec_ret = _trailing_return(sector_df, as_of, lookback_days)
    spy_ret = _trailing_return(spy_df, as_of, lookback_days)
    if sec_ret is None or spy_ret is None:
        return out
    return {
        "sector_outperforming_spy":  bool(sec_ret > spy_ret),
        # B587 (2026-06-04): inverse signal for short strategies per owner
        # directive "apply same as 52w_high_breakout inversed" to 52w_low_breakdown.
        # Strict less-than (boundary equality emits neither True for this).
        "sector_underperforming_spy": bool(sec_ret < spy_ret),
        "sector_etf_return_20d":     round(float(sec_ret), 4),
        "spy_return_20d":            round(float(spy_ret), 4),
        "sector_etf_ticker":         etf,
    }
