"""
data/universe.py — Instrument manager.

Handles:
  - Fetching S&P 500 constituent list from Wikipedia (point-in-time approximate)
  - Applying liquidity filters to reduce ~500 → ~380-420 tradeable names
  - Appending new instruments to existing universe without re-fetching
  - Sector breakdown for correlation analysis

Universe tiers:
  Phase 1A: SP50 + 17 ETFs = 67 instruments (hardcoded — pipeline validation)
  Phase 1B: Filtered S&P 500 + all ETFs = ~400 instruments (dynamic)
  Phase 1C: Passing strategies only, full universe
"""

import logging
import time
from datetime import date, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf

from backtest.config import SP50, ETFS, LIQUIDITY

logger = logging.getLogger(__name__)

# Full ETF list for Phase 1B+
ETFS_FULL = [
    # Broad market
    "SPY", "QQQ", "IWM", "DIA", "VTI",
    # Sector
    "XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE",
    # Volatility
    "VXX",
    # Bonds
    "TLT", "HYG", "LQD", "IEF", "SHY",
    # Commodities
    "GLD", "SLV", "GDX", "USO",
    # International
    "EEM", "EFA",
    # No leveraged ETFs — volatility decay invalidates results
]


def get_sp500_constituents(max_tickers: int = 500) -> list[str]:
    """
    Fetch S&P 500 constituent list from Wikipedia.
    Returns tickers in approximate market-cap order (Wikipedia order).
    """
    try:
        tables = pd.read_html(
            "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
            attrs={"id": "constituents"},
        )
        sp500 = tables[0]
        tickers = (sp500["Symbol"]
                   .str.replace(".", "-", regex=False)
                   .tolist())
        logger.info("Loaded %d S&P 500 constituents from Wikipedia", len(tickers))
        return tickers[:max_tickers]
    except Exception as exc:
        logger.error("Could not fetch S&P 500 list: %s — using SP50 fallback", exc)
        return SP50


def apply_liquidity_filter(
    tickers: list[str],
    ohlcv_dict: dict[str, pd.DataFrame],
    info_dict: dict[str, dict],
    as_of: date,
    min_price: float = None,
    min_avg_volume: float = None,
    min_market_cap_m: float = None,
) -> tuple[list[str], dict[str, str]]:
    """
    Apply liquidity filters to a list of tickers.
    Returns (passing_tickers, {ticker: fail_reason}).

    Uses config defaults if parameters not specified.
    """
    min_price        = min_price        or LIQUIDITY["min_price"]
    min_avg_volume   = min_avg_volume   or LIQUIDITY["min_avg_volume"]
    min_market_cap_m = min_market_cap_m or LIQUIDITY["min_market_cap_m"]

    passing = []
    failing = {}

    for ticker in tickers:
        df = ohlcv_dict.get(ticker)
        if df is None or df.empty:
            failing[ticker] = "no_price_data"
            continue

        # Slice to as_of
        sliced = df[df.index.date <= as_of]
        if len(sliced) < 20:
            failing[ticker] = "insufficient_history"
            continue

        # Price filter
        last_close = float(sliced["close"].iloc[-1])
        if last_close < min_price:
            failing[ticker] = f"price_${last_close:.2f}_below_${min_price}"
            continue

        # Volume filter — 20-day average
        avg_vol = float(sliced["volume"].tail(20).mean())
        if avg_vol < min_avg_volume:
            failing[ticker] = f"avg_vol_{int(avg_vol):,}_below_{int(min_avg_volume):,}"
            continue

        # Market cap — skip check if data unavailable (rate limit graceful fallback)
        info = info_dict.get(ticker, {})
        mkt_cap_m = (info.get("market_cap") or 0) / 1_000_000
        if mkt_cap_m > 0 and mkt_cap_m < min_market_cap_m:
            failing[ticker] = f"mkt_cap_${mkt_cap_m:.0f}M_below_${min_market_cap_m:.0f}M"
            continue

        passing.append(ticker)

    logger.info(
        "Liquidity filter: %d/%d passed (%.0f%% pass rate)",
        len(passing), len(tickers),
        len(passing) / len(tickers) * 100 if tickers else 0,
    )
    return passing, failing


def get_sector_map(tickers: list[str], info_dict: dict[str, dict]) -> dict[str, str]:
    """Return {ticker: sector} mapping from cached info."""
    return {
        t: info_dict.get(t, {}).get("sector", "Unknown")
        for t in tickers
    }


def get_correlation_matrix(
    ohlcv_dict: dict[str, pd.DataFrame],
    as_of: date,
    lookback_days: int = 60,
) -> pd.DataFrame:
    """
    Compute return correlation matrix for all instruments.
    Used by correlation filter to prevent over-concentrated positions.
    """
    start = as_of - timedelta(days=lookback_days + 5)
    returns = {}
    for ticker, df in ohlcv_dict.items():
        sliced = df[(df.index.date >= start) & (df.index.date <= as_of)]
        if len(sliced) >= 20:
            returns[ticker] = sliced["close"].pct_change().dropna()

    if not returns:
        return pd.DataFrame()

    ret_df = pd.DataFrame(returns).dropna(how="all")
    return ret_df.corr()


def build_phase1b_universe(
    ohlcv_dict: dict[str, pd.DataFrame],
    info_dict:  dict[str, dict],
    as_of: date,
) -> tuple[list[str], dict[str, str]]:
    """
    Build the full Phase 1B universe: filtered S&P 500 + all ETFs.
    Returns (passing_tickers, fail_reasons).
    """
    sp500 = get_sp500_constituents(500)
    all_tickers = list(dict.fromkeys(sp500 + ETFS_FULL))  # deduplicated, order preserved
    return apply_liquidity_filter(all_tickers, ohlcv_dict, info_dict, as_of)


def fetch_info_bulk(
    tickers: list[str],
    delay: float = 0.2,
    cache_file: str = "data/cache/info_cache.json",
) -> dict[str, dict]:
    """
    Fetch company info (sector, market cap, IPO date) for all tickers.
    Uses a simple JSON cache to avoid re-fetching on every run.
    """
    import json
    from pathlib import Path

    cache_path = Path(cache_file)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing cache
    cached = {}
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text())
        except Exception:
            cached = {}

    to_fetch = [t for t in tickers if t not in cached]
    if to_fetch:
        logger.info("Fetching info for %d new tickers...", len(to_fetch))

    for i, ticker in enumerate(to_fetch):
        if i > 0 and i % 20 == 0:
            time.sleep(2)
        try:
            info = yf.Ticker(ticker).info
            cached[ticker] = {
                "name":       info.get("longName", ticker),
                "sector":     info.get("sector", "Unknown"),
                "industry":   info.get("industry", "Unknown"),
                "market_cap": info.get("marketCap", 0) or 0,
                "exchange":   info.get("exchange", ""),
                "ipo_date":   info.get("firstTradeDateEpochUtc"),
            }
        except Exception as exc:
            cached[ticker] = {
                "name": ticker, "sector": "Unknown",
                "industry": "Unknown", "market_cap": 0,
                "exchange": "", "ipo_date": None,
            }
            logger.debug("fetch_info(%s): %s", ticker, exc)
        time.sleep(delay)

    # Save updated cache
    try:
        cache_path.write_text(json.dumps(cached, default=str, indent=2))
    except Exception as exc:
        logger.warning("Info cache write failed: %s", exc)

    return {t: cached.get(t, {"sector": "Unknown", "market_cap": 0}) for t in tickers}
