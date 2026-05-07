"""
data/fetcher.py — OHLCV price data and fundamentals.

Pass 53 Batch 13 sub-task 6 (DEC-497 NO-LIVE-API HARD CUT + D4 yfinance total
cut owner directive 2026-05-06): yfinance REMOVED from runtime. All data reads
come from prefetched caches:
  - OHLCV: cache/ohlcv/{TICKER}.parquet (Sprint 0A Batch 2)
  - Reference (sector/cap/IPO): data_prefetch/polygon/reference/ (FUTURE)
  - Earnings dates: derive from data_prefetch/polygon/financials/ (Batch 4)
  - Dividends: data_prefetch/polygon/dividends/ (FUTURE)

CRITICAL: Every function that retrieves data accepts an `as_of` date parameter.
Data returned NEVER includes anything after `as_of`. This is the primary defence
against look-ahead bias in the backtesting engine.

Pre-prefetch state (FUTURE prefetch pending): functions return empty/stub
gracefully (per DEC-503 test pyramid acceptance). Cache miss does NOT fall back
to live API — DEC-497 HARD CUT.
"""

import os
import time
import logging
from datetime import date, datetime, timedelta
from typing import Optional
from pathlib import Path

import pandas as pd
# yfinance removed from runtime per DEC-497 D4 (Pass 53 Batch 13 sub-task 6 2026-05-06).

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
    # Pass 53 Batch 13 sub-task 6 (DEC-497 D4 yfinance HARD CUT 2026-05-06):
    # Read from cache/ohlcv/{TICKER}.parquet (Sprint 0A Batch 2 prefetched).
    # NO live API fallback. Cache miss → empty DataFrame.
    effective_end = min(end, as_of) if as_of else end
    safe_ticker = ticker.replace(".", "-")
    cache_path = Path(__file__).parent / "cache" / "ohlcv" / f"{safe_ticker}.parquet"
    if not cache_path.exists():
        logger.debug("OHLCV cache miss for %s (DEC-497 HARD CUT — no live fallback)", ticker)
        return pd.DataFrame()
    try:
        df = pd.read_parquet(cache_path)
        # Cache may use either 'date' column or DatetimeIndex
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")
        elif not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize(None) if df.index.tz else df.index
        # Filter to requested window
        mask = (df.index.date >= start) & (df.index.date <= effective_end)
        df = df[mask].copy()
        # Enforce date ceiling (PIT guard)
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

    Pass 53 Batch 13 sub-task 6 (DEC-497 D4 yfinance HARD CUT 2026-05-06):
    yfinance removed. Reads from Polygon reference data.

    Pass 53 Day-9 v8 G4 fix (BUG-PF-REFPATH): path was
    ``data_prefetch/polygon/reference/`` (never existed); actual data is in
    ``data_prefetch/polygon/legacy_archive_pass53/reference/`` (599 tickers).
    Schema columns are ``sic_code/sic_description/primary_exchange/list_date``
    — NOT ``sector/industry/exchange/ipo_date`` — so we map them. Sector
    canonical source remains universe CSVs (B++ schema) per L146 separation;
    Polygon reference only fills market_cap / industry-via-SIC / exchange /
    list_date.
    """
    safe_ticker = ticker.replace(".", "-")
    repo_root = Path(__file__).parent.parent.parent
    # Day-9 v8 G4 fix: search canonical path first, then legacy archive
    candidate_paths = [
        repo_root / "data_prefetch" / "polygon" / "reference" / f"{safe_ticker}.parquet",
        repo_root / "data_prefetch" / "polygon" / "legacy_archive_pass53" / "reference" / f"{safe_ticker}.parquet",
    ]
    ref_path = next((p for p in candidate_paths if p.exists()), None)
    default = {"ticker": ticker, "name": ticker, "sector": "Unknown",
               "industry": "Unknown", "market_cap": 0, "exchange": "",
               "ipo_date": None}
    if ref_path is None:
        return default
    try:
        df = pd.read_parquet(ref_path)
        if df.empty:
            return default
        row = df.iloc[0]
        # Schema mapping (Polygon reference → canonical info dict):
        #   name            -> name
        #   market_cap      -> market_cap
        #   sic_description -> industry (Polygon uses SIC, not GICS)
        #   primary_exchange-> exchange (XNAS / XNYS / etc.)
        #   list_date       -> ipo_date
        # sector remains "Unknown" — universe CSVs are the canonical sector source.
        return {
            "ticker":       ticker,
            "name":         row.get("name", ticker) or ticker,
            "sector":       row.get("sector", "Unknown") or "Unknown",
            "industry":     row.get("industry") or row.get("sic_description") or "Unknown",
            "market_cap":   row.get("market_cap", 0) or 0,
            "exchange":     row.get("exchange") or row.get("primary_exchange") or "",
            "ipo_date":     row.get("ipo_date") or row.get("list_date"),
        }
    except Exception as exc:
        logger.error("fetch_info(%s): %s", ticker, exc)
        return default


def fetch_earnings_dates(
    ticker: str,
    as_of: Optional[date] = None,
) -> pd.DataFrame:
    """
    Return historical earnings dates for `ticker`, filtered to on/before as_of.

    Pass 53 Batch 13 sub-task 6 (DEC-497 D4): yfinance removed. Derives earnings
    dates from data_prefetch/polygon/financials/{TICKER}.parquet (Sprint 0A Batch 4).
    Polygon financials filing_date approximates earnings release date.
    """
    safe_ticker = ticker.replace(".", "-")
    fin_path = Path(__file__).parent.parent.parent / "data_prefetch" / "polygon" / "financials" / f"{safe_ticker}.parquet"
    if not fin_path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_parquet(fin_path)
        if df.empty or "filing_date" not in df.columns:
            return pd.DataFrame()
        df["earnings_date"] = pd.to_datetime(df["filing_date"])
        df = df.dropna(subset=["earnings_date"])
        if as_of:
            df = df[df["earnings_date"].dt.date <= as_of]
        return df[["earnings_date"]].drop_duplicates().sort_values("earnings_date")
    except Exception as exc:
        logger.debug("fetch_earnings_dates(%s): %s", ticker, exc)
        return pd.DataFrame()


def days_to_next_earnings(ticker: str, as_of: date) -> Optional[int]:
    """
    Return number of calendar days until next earnings announcement after `as_of`.
    Returns None if no upcoming earnings data available.

    Pass 53 Batch 13 sub-task 6 (DEC-497 D4): yfinance removed. Polygon
    financials provides historical filing_date but not FORWARD earnings calendar
    out of the box; pre-Polygon-events expansion this returns None gracefully.
    Future enhancement: derive from Polygon ticker events feed (Batch 5).
    """
    # Stage 2 backtest doesn't need forward earnings (uses historical_membership);
    # Phase 1B Risk Agent needs forward calendar → wire via Polygon /vX/reference
    # /financials with filing_date.gte=today (Batch 13 future).
    return None


def fetch_dividends(
    ticker: str,
    start: date = BACKTEST_START,
    as_of: Optional[date] = None,
) -> pd.DataFrame:
    """
    Return dividend history for `ticker` on or before `as_of`.

    Pass 53 Batch 13 sub-task 6 (DEC-497 D4): yfinance removed. Reads from
    data_prefetch/polygon/dividends/{TICKER}.parquet.

    Pass 53 Day-9 v8 G5 fix (BUG-PF-DIVPATH): path was
    ``data_prefetch/polygon/dividends/`` (never existed); only 2 files actually
    in ``data_prefetch/polygon/legacy_archive_pass53/dividends/``. Pre-coverage
    returns empty DataFrame gracefully.
    """
    safe_ticker = ticker.replace(".", "-")
    repo_root_div = Path(__file__).parent.parent.parent
    candidate_paths = [
        repo_root_div / "data_prefetch" / "polygon" / "dividends" / f"{safe_ticker}.parquet",
        repo_root_div / "data_prefetch" / "polygon" / "legacy_archive_pass53" / "dividends" / f"{safe_ticker}.parquet",
    ]
    div_path = next((p for p in candidate_paths if p.exists()), None)
    if div_path is None:
        return pd.DataFrame()
    try:
        df = pd.read_parquet(div_path)
        if df.empty:
            return pd.DataFrame()
        # Schema TBD post-prefetch; expected: ex_dividend_date, cash_amount, declared_date
        end = as_of or BACKTEST_END
        if "ex_dividend_date" in df.columns:
            df["date"] = pd.to_datetime(df["ex_dividend_date"])
            df = df.rename(columns={"cash_amount": "dividend"} if "cash_amount" in df.columns else {})
            mask = (df["date"].dt.date >= start) & (df["date"].dt.date <= end)
            return df[mask].reset_index(drop=True)
        return df
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


# ─────────────────────────────────────────────────────────────────────────────
# Pass 53 Day-9 v8c Wave D — L146 G6 Polygon events accessor
# ─────────────────────────────────────────────────────────────────────────────
def get_ticker_change_history(ticker: str) -> list[dict]:
    """Return historical ticker_change events from Polygon events prefetch.

    Source: data_prefetch/polygon/events/<TICKER>.parquet
    Schema: ticker / event_type / event_date / details_json

    Useful for survivorship adjustment (mapping current ticker to historical
    tickers it was previously known by). Currently only `ticker_change`
    events are populated; other event types may appear in future prefetches.

    Returns list of dicts with keys: event_type, event_date, details_json.
    Empty list if no prefetch found.
    """
    safe = ticker.replace(".", "-")
    path = (Path(__file__).parent.parent.parent / "data_prefetch"
            / "polygon" / "events" / f"{safe}.parquet")
    if not path.exists():
        return []
    try:
        df = pd.read_parquet(path)
        if df.empty:
            return []
        return [
            {
                "event_type":  row.get("event_type", ""),
                "event_date":  row.get("event_date"),
                "details_json": row.get("details_json", ""),
            }
            for _, row in df.iterrows()
        ]
    except Exception as exc:
        logger.debug("get_ticker_change_history(%s): %s", ticker, exc)
        return []
