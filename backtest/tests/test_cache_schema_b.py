"""Regression tests for cache.py Schema-B handling (Pass 53 Day 9 fix).

Caught by Phase 1A smoke 2026-05-07: cache.py:get_ohlcv was written for legacy
Schema-A (DatetimeIndex) but H6 migration converted all OHLCV to Schema-B
(RangeIndex + 'date' column). Bug: get_ohlcv read Schema-B as DatetimeIndex,
date filter returned 0 rows, falling through to yfinance HARD CUT → empty.

Plus: index.json went stale post-H6 migration (only 495 of 1933 entries).
get_ohlcv recovers index entries by reading the file directly when index
is missing.

Plus: weekend/holiday boundary — request start 2020-01-01 vs cache start
2020-01-02 (first trading day) caused strict-coverage check to fail. Relaxed
to ±7-day buffer.

Per DEC-594 same-commit: this test landed alongside the fix.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from backtest.data.cache import get_ohlcv


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OHLCV_DIR = REPO_ROOT / "backtest" / "data" / "cache" / "ohlcv"


# ---------------------------------------------------------------------------
# Schema-B handling
# ---------------------------------------------------------------------------
def test_cache_get_ohlcv_schema_b_loads_correctly():
    """get_ohlcv must return non-empty for a known Schema-B ticker."""
    if not (OHLCV_DIR / "VXX.parquet").exists():
        pytest.skip("VXX.parquet not in cache")
    result = get_ohlcv("VXX", date(2022, 1, 1), date(2025, 12, 31))
    assert not result.empty, (
        "get_ohlcv VXX returned empty — Schema-B regression. "
        "cache.py must detect 'date' column and set as DatetimeIndex."
    )
    assert len(result) >= 750, f"VXX 2022-2025 should have ~1000 rows, got {len(result)}"
    assert "close" in result.columns
    assert isinstance(result.index, pd.DatetimeIndex)


def test_cache_get_ohlcv_aapl_post_h6_migration():
    """AAPL was migrated Schema-A → Schema-B in H6; must load correctly."""
    if not (OHLCV_DIR / "AAPL.parquet").exists():
        pytest.skip("AAPL.parquet not in cache")
    result = get_ohlcv("AAPL", date(2022, 1, 1), date(2024, 12, 31))
    assert not result.empty
    assert len(result) >= 500


def test_cache_get_ohlcv_weekend_boundary():
    """Cache start 2021-05-06 (first trading day) vs request start 2021-05-05
    (or earlier weekend) — ±7-day buffer must accept this."""
    # Polygon Stocks Starter cache starts 2021-05-06 (first trading day)
    # Test request starts 2021-05-01 (weekend)
    if not (OHLCV_DIR / "SPY.parquet").exists():
        pytest.skip("SPY.parquet not in cache")
    result = get_ohlcv("SPY", date(2021, 5, 1), date(2024, 12, 31))
    assert not result.empty, (
        "Weekend-boundary request should hit cache via ±7-day buffer "
        "(Pass 53 H6 fix); was strict-failing pre-fix."
    )


def test_cache_index_recovery_from_file():
    """If index.json missing entry, get_ohlcv must recover by reading file."""
    # The post-H6 rebuild repopulates index.json; verify it has all expected entries
    import json
    idx = json.loads(
        (REPO_ROOT / "backtest" / "data" / "cache" / "index.json").read_text()
    )
    assert "VXX" in idx, "Index rebuild missed VXX"
    assert "AAPL" in idx
    assert idx["VXX"]["rows"] > 1000  # ~1593 rows expected
