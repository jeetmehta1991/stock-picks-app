"""
data/fetcher.py — OHLCV price data and fundamentals via yfinance.

CRITICAL: Every function that retrieves data accepts an `as_of` date parameter.
Data returned NEVER includes anything after `as_of`. This is the primary defence
against look-ahead bias in the backtesting engine.

When backtesting date D:
  - OHLCV: rows with index <= D
  - Fundamentals: last available filing on or before D
  - Volume averages: trailing 20 days ending on D

If a function does not have an `as_of` parameter, it is safe to call anytime
(e.g. fetching the full S&P 500 constituent list for universe construction).
"""

import os
import time
import logging
from datetime import date, datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf

from backtest.config import (
    BACKTEST_START, BACKTEST_END, LIQUIDITY,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _to_date(d) -> date:
    """Normalise date/datetime/str to date."""
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str):
        return datetime.strptime(d[:10], "%Y-%m-%d").date()
    return d


def _assert_no_lookahead(df: pd.DataFrame, as_of: date, label: str) -> pd.DataFrame:
    """
    Strip any rows after `as_of` and RAISE if any were found.

    DEC-305 fix (Pass 50): previously logged WARNING and silently returned
    filtered df. Backtest leaks were swallowed in production. Now raises
    LookAheadBiasError so the issue is forced to surface.

    Bypass: set env var ALLOW_LOOKAHEAD_LEAK=1 to revert to warning-only mode.
    Use ONLY for debugging or in narrowly-scoped paths pending fix.
    """
    if df.empty:
        return df
    idx = df.index
    if hasattr(idx, "date"):
        mask = pd.Series([d.date() if hasattr(d, "date") else d for d in idx], index=idx) <= as_of
    else:
        mask = pd.Series([_to_date(str(d)[:10]) for d in idx], index=idx) <= as_of
    leaked = (~mask).sum()
    if leaked:
        msg = (f"LOOK-AHEAD BIAS DETECTED [{label}]: {leaked} rows after "
               f"as_of={as_of} would have leaked into backtest.")
        if os.environ.get("ALLOW_LOOKAHEAD_LEAK") == "1":
            logger.warning(msg + " (bypass via ALLOW_LOOKAHEAD_LEAK=1)")
        else:
            raise LookAheadBiasError(msg)
    return df[mask]


class LookAheadBiasError(RuntimeError):
    """Raised when PIT guard detects rows after the as_of cutoff. DEC-305."""
    pass


# ---------------------------------------------------------------------------
# UNIVERSE HELPERS
# ---------------------------------------------------------------------------

def get_sp500_constituents() -> list[str]:
    """
    Load S&P 500 constituents from the committed CSV file.
    NEVER use Wikipedia — blocked in Codespaces, not point-in-time, fragile (L88).
    Refresh backtest/data/Current Snapshot_SP500 Tickers_May 2026.csv quarterly via scripts/refresh_sp500_universe.py.
    """
    from backtest.data.universe import get_sp500_constituents as _get
    return _get()


def get_sp200() -> list[str]:
    """Return top 200 S&P 500 tickers by approximate market cap."""
    return get_sp500_constituents()[:200]


# ---------------------------------------------------------------------------
# PRICE DATA
# ---------------------------------------------------------------------------

def fetch_ohlcv(
    ticker: str,
    start: date = BACKTEST_START,
    end: date   = BACKTEST_END,
    as_of: Optional[date] = None,
) -> pd.DataFrame:
    """
    Fetch daily OHLCV data for `ticker` between `start` and `end`.

    If `as_of` is provided, data is stripped to rows on or before `as_of`.
    This is the standard call pattern inside the backtest loop:

        df = fetch_ohlcv("AAPL", as_of=backtest_date)

    Returns DataFrame with columns: Open, High, Low, Close, Volume, AdjClose
    Index: DatetimeIndex (UTC-naive).
    Returns empty DataFrame on failure.
    """
    # The end ceiling is whichever is earlier: requested end OR as_of
    effective_end = min(end, as_of) if as_of else end
    # Add one day so yfinance includes effective_end
    fetch_end = effective_end + timedelta(days=1)

    try:
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(
            start=start.isoformat(),
            end=fetch_end.isoformat(),
            auto_adjust=True,
            actions=False,
        )
        if df.empty:
            logger.debug("No OHLCV data returned for %s", ticker)
            return pd.DataFrame()

        # Normalise column names
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df.rename(columns={"Open": "open", "High": "high", "Low": "low",
                            "Close": "close", "Volume": "volume"}, inplace=True)
        df = df[["open", "high", "low", "close", "volume"]].copy()

        # Enforce date ceiling
        if as_of:
            df = _assert_no_lookahead(df, as_of, f"OHLCV:{ticker}")

        return df

    except Exception as exc:
        logger.error("fetch_ohlcv(%s): %s", ticker, exc)
        return pd.DataFrame()


def fetch_ohlcv_bulk(
    tickers: list[str],
    start: date = BACKTEST_START,
    end: date   = BACKTEST_END,
    as_of: Optional[date] = None,
    delay_sec: float = 0.3,
) -> dict[str, pd.DataFrame]:
    """
    Fetch OHLCV for multiple tickers. Returns dict {ticker: DataFrame}.
    Uses individual calls with a small delay to avoid rate limiting.
    """
    results: dict[str, pd.DataFrame] = {}
    for i, ticker in enumerate(tickers):
        df = fetch_ohlcv(ticker, start=start, end=end, as_of=as_of)
        if not df.empty:
            results[ticker] = df
        if i > 0 and delay_sec > 0:
            time.sleep(delay_sec)
    logger.info("fetch_ohlcv_bulk: loaded %d/%d tickers", len(results), len(tickers))
    return results


# ---------------------------------------------------------------------------
# FUNDAMENTALS
# ---------------------------------------------------------------------------

def fetch_info(ticker: str, as_of: Optional[date] = None) -> dict:
    """
    Fetch static company info: market cap, sector, industry, listing date.
    `as_of` is accepted for API consistency but yfinance info is point-in-time
    approximate for backtesting purposes (survivorship note: we use current
    constituents which introduces mild survivorship bias — acceptable for Phase 1).
    """
    try:
        info = yf.Ticker(ticker).info
        return {
            "ticker":       ticker,
            "name":         info.get("longName", ticker),
            "sector":       info.get("sector", "Unknown"),
            "industry":     info.get("industry", "Unknown"),
            "market_cap":   info.get("marketCap", 0) or 0,
            "exchange":     info.get("exchange", ""),
            "ipo_date":     info.get("firstTradeDateEpochUtc"),   # epoch seconds
        }
    except Exception as exc:
        logger.error("fetch_info(%s): %s", ticker, exc)
        return {"ticker": ticker, "name": ticker, "sector": "Unknown",
                "industry": "Unknown", "market_cap": 0, "exchange": ""}


def fetch_earnings_dates(
    ticker: str,
    as_of: Optional[date] = None,
) -> pd.DataFrame:
    """
    Return historical earnings dates for `ticker`, filtered to on/before as_of.
    Used by agents to check earnings proximity (avoid entering before reports).

    Returns DataFrame with columns: earnings_date, eps_estimate, eps_actual
    """
    try:
        cal = yf.Ticker(ticker).earnings_dates
        if cal is None or cal.empty:
            return pd.DataFrame()

        cal = cal.copy()
        cal.index = pd.to_datetime(cal.index).tz_localize(None)
        cal.index.name = "earnings_date"
        cal = cal.reset_index()
        cal["earnings_date"] = pd.to_datetime(cal["earnings_date"])

        if as_of:
            # Only use earnings dates that were known before as_of
            # (i.e. the announcement had already happened or was scheduled and public)
            cal = cal[cal["earnings_date"].dt.date <= as_of]

        return cal[["earnings_date"]].drop_duplicates().sort_values("earnings_date")

    except Exception as exc:
        logger.debug("fetch_earnings_dates(%s): %s", ticker, exc)
        return pd.DataFrame()


def days_to_next_earnings(ticker: str, as_of: date) -> Optional[int]:
    """
    Return number of calendar days until next earnings announcement after `as_of`.
    Returns None if no upcoming earnings data available.
    Used by Risk Agent to flag earnings proximity.
    """
    try:
        cal = yf.Ticker(ticker).earnings_dates
        if cal is None or cal.empty:
            return None
        future = [
            d.date() if hasattr(d, "date") else _to_date(str(d)[:10])
            for d in cal.index
            if (d.date() if hasattr(d, "date") else _to_date(str(d)[:10])) > as_of
        ]
        if not future:
            return None
        next_date = min(future)
        return (next_date - as_of).days
    except Exception:
        return None


def fetch_dividends(
    ticker: str,
    start: date = BACKTEST_START,
    as_of: Optional[date] = None,
) -> pd.DataFrame:
    """
    Return dividend history for `ticker` on or before `as_of`.
    Used to detect dividend changes (signal in Category 6).
    """
    try:
        end = as_of or BACKTEST_END
        df = yf.Ticker(ticker).dividends
        if df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        df.columns = ["date", "dividend"]
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
        mask = (df["date"].dt.date >= start) & (df["date"].dt.date <= end)
        return df[mask].reset_index(drop=True)
    except Exception as exc:
        logger.debug("fetch_dividends(%s): %s", ticker, exc)
        return pd.DataFrame()


# ---------------------------------------------------------------------------
# LIQUIDITY FILTER
# ---------------------------------------------------------------------------

def passes_liquidity_filter(
    ticker: str,
    df_ohlcv: pd.DataFrame,
    info: dict,
    as_of: date,
) -> tuple[bool, str]:
    """
    Apply all minimum liquidity filters from section 4.4 of project plan.
    Returns (passes: bool, reason_if_failed: str).

    Filters:
      - Price > $5
      - 20-day avg volume > 500,000
      - Listed > 1 year
      - Market cap > $100M
    """
    if df_ohlcv.empty:
        return False, "no_price_data"

    # Price filter — use last close on or before as_of
    last_close = df_ohlcv["close"].iloc[-1]
    if last_close < 5.0:
        return False, f"price_${last_close:.2f}_below_$5"

    # Volume filter — 20-day rolling average
    vol_20d = df_ohlcv["volume"].tail(20).mean()
    if vol_20d < 500_000:
        return False, f"avg_vol_{int(vol_20d):,}_below_500k"

    # Market cap filter — skip if data unavailable (e.g. rate limited or ETF)
    market_cap_m = (info.get("market_cap") or 0) / 1_000_000
    if market_cap_m > 0 and market_cap_m < 100:
        return False, f"mkt_cap_${market_cap_m:.0f}M_below_$100M"

    # Listing age filter — IPO date from yfinance info
    ipo_epoch = info.get("ipo_date")
    if ipo_epoch:
        ipo_date = date.fromtimestamp(ipo_epoch)
        years_listed = (as_of - ipo_date).days / 365.25
        if years_listed < 1.0:
            return False, f"listed_only_{years_listed:.1f}yr_(<1yr)"

    return True, ""


# ---------------------------------------------------------------------------
# VOLUME STATS HELPER
# ---------------------------------------------------------------------------

def volume_spike_factor(df_ohlcv: pd.DataFrame, window: int = 20) -> float:
    """
    Return today's volume divided by the trailing `window`-day average.
    Used by technical screener to flag 2x and 3x volume spikes.
    Requires at least window+1 rows in df_ohlcv.
    """
    if len(df_ohlcv) < window + 1:
        return 1.0
    avg_vol = df_ohlcv["volume"].iloc[-(window + 1):-1].mean()
    today_vol = df_ohlcv["volume"].iloc[-1]
    if avg_vol == 0:
        return 1.0
    return today_vol / avg_vol
