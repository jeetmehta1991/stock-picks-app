"""
data/universe.py — Instrument manager.

Handles:
  - Loading S&P 500 constituent list from committed static CSV (sp500_tickers.csv)
    The CSV is refreshed quarterly via slickcharts.com (or S&P press releases).
    See LEARNINGS L88: Wikipedia is unreliable as a runtime data source — the
    static CSV pattern is the correct approach.
  - Applying liquidity filters to reduce ~500 → ~380-420 tradeable names
  - Appending new instruments to existing universe without re-fetching
  - Sector breakdown for correlation analysis

Universe tiers:
  Phase 1A: SP50 + 17 ETFs = 67 instruments (hardcoded — pipeline validation)
  Phase 1B: Filtered S&P 500 + all ETFs = ~400 instruments (CSV-backed)
  Phase 1C: Passing strategies only, full universe

Resolves: DEC-341 (Pass 52), closes BUG-264.
"""

import logging
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf

from backtest.config import SP50, ETFS, LIQUIDITY

logger = logging.getLogger(__name__)

# Universe CSVs moved to top-level "Backtesting universe/" folder (Pass 53 owner directive)
# for repo-wide visibility. Path resolves from backtest/data/universe.py → repo root.
UNIVERSE_DIR = Path(__file__).parent.parent.parent / "Backtesting universe"

# Full ETF list for Phase 1B+
# Per DEC-494 / Pass 53 owner directive: ETFs migrated from hardcoded list to
# `backtest/data/tier1_etfs.csv` (Item 4 (ii) CSV + code migration). Module-level
# ETFS_FULL is computed at import time from the CSV via get_etfs_full() so that
# legacy callers (universe.py functions, agents, tests) continue to work without
# refactor. CSV is the source of truth; updates flow through the CSV, not this
# module.

def get_etfs_full() -> list[str]:
    """
    Load Tier 1 ETF list from `backtest/data/tier1_etfs.csv`.

    Per DEC-494 (Pass 53 owner-approved Sprint 1) — ETFs are now declared in
    a CSV file alongside T1a/T1b/T1c membership files for consistency.
    No leveraged ETFs included — volatility decay invalidates backtest results.

    Returns list of ticker symbols. Falls back to empty list on read failure
    (callers should treat empty as a catastrophic config error).
    """
    csv_path = UNIVERSE_DIR / "tier1_etfs.csv"
    try:
        df = pd.read_csv(csv_path)
        tickers = df["Symbol"].drop_duplicates().tolist()
        logger.info("Loaded %d Tier 1 ETFs from tier1_etfs.csv", len(tickers))
        return tickers
    except Exception as exc:
        logger.error("Could not read tier1_etfs.csv: %s", exc)
        return []


# Computed at module import time — preserves legacy `from universe import ETFS_FULL`
# callers. CSV-backed; update tier1_etfs.csv to change the list.
ETFS_FULL = get_etfs_full()


def get_sp500_constituents(max_tickers: int = 500) -> list[str]:
    """
    Load S&P 500 constituent list from the committed CSV file.

    Uses backtest/data/sp500_tickers.csv — a maintained static file.
    No network calls, no rate limiting, works in all environments.
    Update sp500_tickers.csv manually when index membership changes
    (typically 10-20 changes per year).
    """
    csv_path = UNIVERSE_DIR / "sp500_tickers.csv"
    try:
        df = pd.read_csv(csv_path)
        # Remove duplicates (companies with two share classes)
        tickers = df["Symbol"].drop_duplicates().tolist()
        logger.info("Loaded %d S&P 500 constituents from sp500_tickers.csv", len(tickers))
        return tickers[:max_tickers]
    except Exception as exc:
        logger.error("Could not read sp500_tickers.csv: %s", exc)
        return []


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


def get_sector_map(tickers: list[str], info_dict: dict[str, dict] = None) -> dict[str, str]:
    """
    Return {ticker: sector} mapping.
    Reads from sp500_tickers.csv first (fast, no network).
    Falls back to info_dict if ticker not in CSV (e.g. ETFs).
    """
    csv_path = UNIVERSE_DIR / "sp500_tickers.csv"
    sector_map = {}

    # Load from CSV
    try:
        df = pd.read_csv(csv_path)
        df = df.drop_duplicates(subset=["Symbol"])
        sector_map = dict(zip(df["Symbol"], df["Sector"]))
    except Exception:
        pass

    # ETF sector labels
    etf_sectors = {
        "SPY": "Broad Market", "QQQ": "Technology", "IWM": "Small Cap",
        "DIA": "Broad Market", "VTI": "Broad Market", "XLK": "Information Technology",
        "XLF": "Financials", "XLE": "Energy", "XLV": "Health Care",
        "XLI": "Industrials", "XLY": "Consumer Discretionary", "XLP": "Consumer Staples",
        "XLU": "Utilities", "XLB": "Materials", "XLRE": "Real Estate",
        "VXX": "Volatility", "TLT": "Fixed Income", "HYG": "Fixed Income",
        "LQD": "Fixed Income", "GLD": "Commodities", "SLV": "Commodities",
        "GDX": "Commodities", "USO": "Commodities", "EEM": "Emerging Markets",
        "EFA": "International",
    }
    sector_map.update(etf_sectors)

    # Fill remaining from info_dict if provided
    result = {}
    for t in tickers:
        if t in sector_map:
            result[t] = sector_map[t]
        elif info_dict and t in info_dict:
            result[t] = info_dict[t].get("sector", "Unknown")
        else:
            result[t] = "Unknown"
    return result


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




def get_extended_universe() -> list[str]:
    """
    Load Tier 2 extended universe — spinoffs, large non-S&P stocks.
    Refreshed monthly via scripts/refresh_extended_universe.py (Stage 3+ only).
    Empty CSV = Tier 2 not yet populated (Phase 1B/1C/1D use Tier 1 only).
    """
    csv_path = UNIVERSE_DIR / "extended_universe.csv"
    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            return []
        tickers = df["Symbol"].drop_duplicates().tolist()
        logger.info("Loaded %d Tier 2 extended universe tickers", len(tickers))
        return tickers
    except Exception as exc:
        logger.debug("extended_universe.csv not found or empty: %s", exc)
        return []


def get_momentum_watchlist() -> list[str]:
    """
    Load Tier 3 momentum watchlist — top non-S&P momentum names.
    Refreshed monthly via scripts/build_momentum_watchlist.py (Stage 3+ only).
    For backtesting: fixed at run start (static, no look-ahead).
    For live: recomputed monthly, updated at month-end.
    Empty CSV = Tier 3 not yet populated.
    """
    csv_path = UNIVERSE_DIR / "momentum_watchlist.csv"
    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            return []
        tickers = df["Symbol"].drop_duplicates().tolist()
        logger.info("Loaded %d Tier 3 momentum watchlist tickers", len(tickers))
        return tickers
    except Exception as exc:
        logger.debug("momentum_watchlist.csv not found or empty: %s", exc)
        return []


def get_full_live_universe() -> list[str]:
    """
    Build full live universe for Stage 3+: Tier 1 + Tier 2 + Tier 3 + ETFs.
    For backtesting (Phase 1B/1C/1D): use build_phase1b_universe() instead.
    
    Universe tiers:
      Tier 1 — S&P 500 (~500 tickers, quarterly refresh)
      Tier 2 — Extended: spinoffs, large non-S&P (~50-100 tickers, monthly refresh)
      Tier 3 — Momentum watchlist: top non-S&P momentum (~50 tickers, monthly refresh)
      ETFs   — Sector, bond, commodity, volatility ETFs (~25 tickers, static)
    """
    tier1  = get_sp500_constituents(500)
    tier2  = get_extended_universe()
    tier3  = get_momentum_watchlist()
    etfs   = ETFS_FULL

    # Deduplicate, preserve tier priority order
    full = list(dict.fromkeys(tier1 + tier2 + tier3 + etfs))
    logger.info(
        "Full live universe: %d tickers (T1=%d T2=%d T3=%d ETF=%d)",
        len(full), len(tier1), len(tier2), len(tier3), len(etfs)
    )
    return full

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
        # File lock prevents race conditions in parallel batch runs
        import filelock
        lock_path = str(cache_path) + ".lock"
        try:
            with filelock.FileLock(lock_path, timeout=30):
                # Re-read before writing to merge any updates from other batches
                existing = {}
                if cache_path.exists():
                    try:
                        existing = json.loads(cache_path.read_text())
                    except Exception:
                        existing = {}
                existing.update(cached)
                cache_path.write_text(json.dumps(existing, default=str, indent=2))
        except Exception:
            cache_path.write_text(json.dumps(cached, default=str, indent=2))
    except Exception as exc:
        logger.warning("Info cache write failed: %s", exc)

    return {t: cached.get(t, {"sector": "Unknown", "market_cap": 0}) for t in tickers}
