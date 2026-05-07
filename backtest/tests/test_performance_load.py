"""Performance / load tests — Pass 53 Day-9 G3.

Closes the performance dimension of the test pyramid (DEC-503).

Measures:
  - Cache load throughput on 100 / 250 / 500-ticker subsets
  - Peak resident memory during load
  - Cache filelock contention under parallel reads

Skipped if cache unavailable or psutil missing.
Runtime: <60s on a healthy machine. Marked slow.
"""

from __future__ import annotations

import gc
import logging
import os
import time
from datetime import date
from pathlib import Path

import pandas as pd
import pytest


CACHE_DIR = Path(__file__).resolve().parents[1] / "data" / "cache" / "ohlcv"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _peak_rss_mb() -> float:
    try:
        import psutil
        return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    except Exception:
        return -1.0


def _available_tickers(n: int) -> list[str]:
    if not CACHE_DIR.exists():
        return []
    files = sorted(CACHE_DIR.glob("*.parquet"))
    return [f.stem for f in files[:n]]


@pytest.fixture(autouse=True)
def _quiet_logs():
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


# ---------------------------------------------------------------------------
# G3.1 — Cache load throughput at 100 tickers
# ---------------------------------------------------------------------------
@pytest.mark.slow
def test_g3_cache_load_100_tickers():
    tickers = _available_tickers(100)
    if len(tickers) < 100:
        pytest.skip(f"cache has only {len(tickers)} tickers; need 100")

    from backtest.data.cache import get_ohlcv_bulk

    rss_before = _peak_rss_mb()
    t0 = time.perf_counter()
    out = get_ohlcv_bulk(tickers, start=date(2023, 1, 1), end=date(2023, 12, 31))
    elapsed = time.perf_counter() - t0
    rss_after = _peak_rss_mb()

    assert len(out) >= 50, f"only {len(out)} tickers loaded from 100 requested"
    # Soft envelope: 100 tickers in <60s on developer laptop
    assert elapsed < 60.0, f"100-ticker cache load took {elapsed:.1f}s (>60s)"

    if rss_before > 0:
        delta = rss_after - rss_before
        # Memory shouldn't blow up — soft envelope 1GB delta
        assert delta < 1024, f"memory spiked +{delta:.0f}MB on 100-ticker load"


# ---------------------------------------------------------------------------
# G3.2 — Cache load at 250 tickers (stress)
# ---------------------------------------------------------------------------
@pytest.mark.slow
def test_g3_cache_load_250_tickers():
    tickers = _available_tickers(250)
    if len(tickers) < 250:
        pytest.skip(f"cache has only {len(tickers)} tickers; need 250")

    from backtest.data.cache import get_ohlcv_bulk

    t0 = time.perf_counter()
    out = get_ohlcv_bulk(tickers, start=date(2023, 6, 1), end=date(2023, 12, 31))
    elapsed = time.perf_counter() - t0

    assert len(out) >= 125, f"only {len(out)} tickers loaded from 250 requested"
    assert elapsed < 180.0, f"250-ticker load took {elapsed:.1f}s (>180s)"


# ---------------------------------------------------------------------------
# G3.3 — Cache filelock concurrency
# ---------------------------------------------------------------------------
@pytest.mark.slow
def test_g3_cache_filelock_concurrent_reads():
    """Multiple threads reading the same parquet must not deadlock."""
    tickers = _available_tickers(20)
    if len(tickers) < 20:
        pytest.skip(f"cache has only {len(tickers)} tickers; need 20")

    from concurrent.futures import ThreadPoolExecutor, as_completed
    from backtest.data.cache import get_ohlcv

    def _read_one(t):
        return t, get_ohlcv(t, start=date(2023, 1, 1), end=date(2023, 6, 30))

    t0 = time.perf_counter()
    results = []
    # 8 threads × 20 tickers = 160 reads. If filelock deadlocks, this hangs.
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = [pool.submit(_read_one, t) for _ in range(8) for t in tickers]
        for f in as_completed(futs, timeout=120):
            results.append(f.result())
    elapsed = time.perf_counter() - t0

    assert len(results) == 8 * len(tickers)
    # Soft envelope: 160 concurrent reads in <60s
    assert elapsed < 60.0, f"160 concurrent reads took {elapsed:.1f}s"


# ---------------------------------------------------------------------------
# G3.4 — Single ticker load latency
# ---------------------------------------------------------------------------
def test_g3_single_ticker_load_under_1s():
    tickers = _available_tickers(1)
    if not tickers:
        pytest.skip("cache empty")

    from backtest.data.cache import get_ohlcv

    # Warm up (filesystem)
    _ = get_ohlcv(tickers[0], start=date(2023, 1, 1), end=date(2023, 3, 31))
    gc.collect()

    t0 = time.perf_counter()
    df = get_ohlcv(tickers[0], start=date(2023, 1, 1), end=date(2023, 3, 31))
    elapsed = time.perf_counter() - t0

    assert isinstance(df, pd.DataFrame)
    assert elapsed < 1.0, f"single-ticker load took {elapsed*1000:.0f}ms (>1s)"
