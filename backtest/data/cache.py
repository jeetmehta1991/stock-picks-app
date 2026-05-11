"""
data/cache.py  -  Local Parquet cache for OHLCV data.

Eliminates repeated yfinance API calls across runs.
First run: fetches from yfinance, saves to Parquet.
Subsequent runs: loads from disk in seconds.
Adding new instruments: fetches only the new ones.
Extending date range: fetches only missing dates.

Cache location: data/cache/ohlcv/{ticker}.parquet
Cache index:    data/cache/index.json  (tracks what is cached and up to what date)

GitHub Actions cache key: backtest-ohlcv-{hash of universe list}
"""

import json
import logging
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
# yfinance removed from runtime per DEC-497 D4 (Pass 53 Batch 13 sub-task 6
# 2026-05-06). All OHLCV reads come from cache/ohlcv/ (Polygon-prefetched).
# `_fetch_from_yfinance` retained as no-op stub for transition; cache miss
# returns empty DataFrame.

logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).parent.parent / "data" / "cache" / "ohlcv"
INDEX_FILE = Path(__file__).parent.parent / "data" / "cache" / "index.json"


def _load_index() -> dict:
    if INDEX_FILE.exists():
        try:
            return json.loads(INDEX_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save_index(index: dict):
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    lock_path = str(INDEX_FILE) + ".lock"
    try:
        import filelock
        with filelock.FileLock(lock_path, timeout=30):
            INDEX_FILE.write_text(json.dumps(index, default=str, indent=2))
    except Exception:
        # filelock unavailable or timeout  -  fall back to direct write
        INDEX_FILE.write_text(json.dumps(index, default=str, indent=2))


def _cache_path(ticker: str) -> Path:
    return CACHE_DIR / f"{ticker.replace('-', '_').replace('.', '_')}.parquet"


class TickerCollisionError(ValueError):
    """Raised when two distinct ticker symbols map to the same cache filename. DEC-309."""
    pass


def _assert_no_ticker_collision(ticker: str, index: dict) -> None:
    """
    DEC-309 fix (Pass 51): detect tickers that share a cache filename.

    `_cache_path` replaces both `-` and `.` with `_`, so BRK-B and BRK.B
    both map to BRK_B.parquet. yfinance accepts both forms; whichever
    runs second silently overwrote the first. This guard makes the
    collision a hard error at write time rather than silent corruption.
    """
    target_filename = _cache_path(ticker).name
    for cached_ticker in index:
        if cached_ticker != ticker and _cache_path(cached_ticker).name == target_filename:
            raise TickerCollisionError(
                f"Ticker collision: {ticker!r} and {cached_ticker!r} "
                f"both map to cache filename {target_filename!r}. "
                f"Cache cannot store both. If both must be tracked, the "
                f"_cache_path encoding scheme must be revised."
            )


def _fetch_from_yfinance(
    ticker: str,
    start: date,
    end: date,
    delay: float = 0.3,
) -> pd.DataFrame:
    """Pass 53 Batch 13 sub-task 6 (DEC-497 + D4 yfinance HARD CUT 2026-05-06):
    DEPRECATED  -  yfinance removed from runtime per owner directive. Cache miss
    returns empty DataFrame; legitimate Stage 2 backtest reads come from
    cache/ohlcv/ (Polygon-prefetched per Sprint 0A Batch 2 + Batch 9 v2).

    Function preserved as no-op stub to avoid breaking imports during transition.
    Prior implementation: yf.Ticker.history() with retries.
    """
    logger.warning(
        "_fetch_from_yfinance(%s) called  -  yfinance HARD CUT per DEC-497 D4. "
        "Returning empty DataFrame. Cache miss for ticker not in Sprint 0A "
        "prefetch  -  investigate.", ticker
    )
    return pd.DataFrame()


def get_ohlcv(
    ticker: str,
    start: date,
    end: date,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """
    Get OHLCV for ticker from cache if available, else fetch and cache.

    On first call: fetches from yfinance, saves to Parquet.
    On subsequent calls: loads from Parquet in milliseconds.
    If cache exists but doesn't cover full range: fetches only missing dates.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    index = _load_index()
    cache_file = _cache_path(ticker)
    cached_end_str = index.get(ticker, {}).get("end")
    cached_start_str = index.get(ticker, {}).get("start")

    # Pass 53 H6 fix 2026-05-07: cache now uses Schema-B (RangeIndex + date col)
    # post Polygon migration. Auto-detect index.json staleness by checking actual
    # file if cache_file exists but index entry missing OR appears stale.
    if not force_refresh and cache_file.exists() and (not cached_start_str or not cached_end_str):
        # Index missing  -  derive from file
        try:
            df_check = pd.read_parquet(cache_file)
            if "date" in df_check.columns:
                dates_series = pd.to_datetime(df_check["date"])
                cached_start_str = str(dates_series.min().date())
                cached_end_str = str(dates_series.max().date())
            elif isinstance(df_check.index, pd.DatetimeIndex):
                cached_start_str = str(df_check.index.min().date())
                cached_end_str = str(df_check.index.max().date())
            # Update index.json for future calls
            index[ticker] = {
                "start": cached_start_str,
                "end": cached_end_str,
                "rows": len(df_check),
            }
            _save_index(index)
        except Exception as exc:
            logger.debug("Cache index recovery failed for %s: %s", ticker, exc)

    # Load from cache if available and covers the range
    if (not force_refresh and cache_file.exists() and cached_end_str and cached_start_str):
        cached_start = date.fromisoformat(cached_start_str)
        cached_end   = date.fromisoformat(cached_end_str)

        # Pass 53 H6 fix 2026-05-07 (revised): use cache for ANY overlap with
        # request range. Mask filter at end trims to actual request data.
        # Strict full-coverage check was wrong because (a) DEC-497 yfinance HARD
        # CUT means we can't fetch missing tail anyway; (b) request ends often
        # overshoot cache_end (e.g., macro_snapshot requests end=2026-12-31 but
        # cache has 2026-05-05  -  that's fine, just use what we have).
        # Original strict check + my +/-7-day buffer both failed for this case.
        from datetime import timedelta as _td
        has_overlap = cached_start <= end + _td(days=7) and cached_end >= start - _td(days=7)
        if has_overlap:
            # Full cache hit
            try:
                df = pd.read_parquet(cache_file)
                # Pass 53 H6 fix: detect Schema-B (date col + RangeIndex) vs
                # legacy Schema-A (DatetimeIndex). Normalize to DatetimeIndex.
                if "date" in df.columns:
                    dt = pd.to_datetime(df["date"])
                    if isinstance(dt.dtype, pd.DatetimeTZDtype):
                        dt = dt.dt.tz_localize(None)
                    df["date"] = dt
                    df = df.set_index("date").sort_index()
                else:
                    df.index = pd.to_datetime(df.index)
                    if df.index.tz is not None:
                        df.index = df.index.tz_localize(None)
                mask = (df.index.date >= start) & (df.index.date <= end)
                logger.debug("Cache hit: %s (%d rows)", ticker, mask.sum())
                return df[mask]
            except Exception as exc:
                logger.warning("Cache read failed for %s: %s  -  refetching", ticker, exc)

        # Partial cache  -  fetch missing tail
        if cached_end < end:
            fetch_start = cached_end + timedelta(days=1)
            new_df = _fetch_from_yfinance(ticker, fetch_start, end)
            if not new_df.empty:
                try:
                    existing = pd.read_parquet(cache_file)
                    existing.index = pd.to_datetime(existing.index).tz_localize(None)
                    combined = pd.concat([existing, new_df]).sort_index()
                    combined = combined[~combined.index.duplicated(keep="last")]
                    combined.to_parquet(cache_file)
                    index[ticker] = {
                        "start": str(combined.index[0].date()),
                        "end":   str(combined.index[-1].date()),
                        "rows":  len(combined),
                    }
                    _save_index(index)
                    mask = (combined.index.date >= start) & (combined.index.date <= end)
                    return combined[mask]
                except Exception as exc:
                    logger.warning("Cache append failed for %s: %s", ticker, exc)

        # DEC-307 + DEC-381 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 44
        # 2026-05-11 (owner-approved Path C). Front-extension: when cache
        # starts after requested start, fetch the missing front segment and
        # prepend. Previously only tail was extended; user requesting start
        # before cache.start got truncated data.
        if cached_start > start:
            fetch_end = cached_start - timedelta(days=1)
            new_df = _fetch_from_yfinance(ticker, start, fetch_end)
            if not new_df.empty:
                try:
                    existing = pd.read_parquet(cache_file)
                    existing.index = pd.to_datetime(existing.index).tz_localize(None)
                    # Prepend new_df (older) to existing (newer)
                    combined = pd.concat([new_df, existing]).sort_index()
                    combined = combined[~combined.index.duplicated(keep="first")]
                    combined.to_parquet(cache_file)
                    index[ticker] = {
                        "start": str(combined.index[0].date()),
                        "end":   str(combined.index[-1].date()),
                        "rows":  len(combined),
                    }
                    _save_index(index)
                    mask = (combined.index.date >= start) & (combined.index.date <= end)
                    return combined[mask]
                except Exception as exc:
                    logger.warning("Cache front-extension failed for %s: %s", ticker, exc)

    # Full fetch
    logger.info("Fetching %s from yfinance (%s -> %s)", ticker, start, end)
    df = _fetch_from_yfinance(ticker, start, end)
    if df.empty:
        return df

    # Save to cache
    try:
        # DEC-309 fix (Pass 51): collision check  -  fail loud, not silent overwrite
        _assert_no_ticker_collision(ticker, index)
        df.to_parquet(cache_file)
        index[ticker] = {
            "start": str(df.index[0].date()),
            "end":   str(df.index[-1].date()),
            "rows":  len(df),
        }
        _save_index(index)
    except TickerCollisionError:
        raise  # Don't swallow collisions  -  must surface
    except Exception as exc:
        logger.warning("Cache write failed for %s: %s", ticker, exc)

    mask = (df.index.date >= start) & (df.index.date <= end)
    return df[mask]


def get_ohlcv_bulk(
    tickers: list[str],
    start: date,
    end: date,
    force_refresh: bool = False,
    delay: float = 0.3,
) -> dict[str, pd.DataFrame]:
    """
    Fetch OHLCV for multiple tickers using cache.
    Only makes API calls for tickers not already cached.
    """
    index = _load_index()
    results = {}
    to_fetch = []

    # Separate cached from uncached
    for ticker in tickers:
        cache_file = _cache_path(ticker)
        cached = index.get(ticker, {})
        if (not force_refresh and cache_file.exists() and
                cached.get("end") and
                date.fromisoformat(cached["end"]) >= end and
                cached.get("start") and
                date.fromisoformat(cached["start"]) <= start):
            try:
                df = pd.read_parquet(cache_file)
                df.index = pd.to_datetime(df.index).tz_localize(None)
                mask = (df.index.date >= start) & (df.index.date <= end)
                # DEC-308 + DEC-382 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3
                # Batch 44 2026-05-11: lowered hardcoded 20-day rejection to
                # 1-row minimum. Previously cache was silently rejected for
                # short-window requests; downstream caller knows their min-rows
                # needs (e.g. liquidity filter requires >=30 days; signal
                # compute requires >=200 days). Cache should serve what it has;
                # downstream filters reject if insufficient.
                if mask.sum() >= 1:
                    results[ticker] = df[mask]
                    continue
            except Exception:
                pass
        to_fetch.append(ticker)

    cached_count = len(results)
    if cached_count:
        logger.info("Cache: loaded %d/%d tickers from disk", cached_count, len(tickers))

    # Fetch uncached tickers
    if to_fetch:
        logger.info("Fetching %d tickers from yfinance...", len(to_fetch))
        for i, ticker in enumerate(to_fetch):
            if i > 0 and i % 10 == 0:
                logger.info("  Progress: %d/%d fetched", i, len(to_fetch))
                time.sleep(2)  # extra pause every 10 tickers
            df = get_ohlcv(ticker, start, end, force_refresh=force_refresh)
            if not df.empty:
                results[ticker] = df
            time.sleep(delay)

    logger.info("get_ohlcv_bulk: %d/%d tickers available", len(results), len(tickers))
    return results


def cache_status() -> dict:
    """Return cache statistics."""
    index = _load_index()
    total_size = sum(
        _cache_path(t).stat().st_size
        for t in index
        if _cache_path(t).exists()
    )
    return {
        "tickers_cached": len(index),
        "total_size_mb":  round(total_size / 1_000_000, 1),
        "cache_dir":      str(CACHE_DIR),
        "tickers":        list(index.keys()),
    }


def append_universe(
    new_tickers: list[str],
    start: date,
    end: date,
) -> dict[str, pd.DataFrame]:
    """
    Add new tickers to the cache without re-fetching existing ones.
    Used when expanding from S&P 200 to S&P 500.
    """
    index = _load_index()
    truly_new = [t for t in new_tickers if t not in index]
    if not truly_new:
        logger.info("All %d tickers already cached", len(new_tickers))
        return {}
    logger.info("Appending %d new tickers to cache", len(truly_new))
    return get_ohlcv_bulk(truly_new, start, end)
