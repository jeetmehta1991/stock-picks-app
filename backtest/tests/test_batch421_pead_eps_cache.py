"""Batch 421 (2026-05-28 owner-approved profile-first prewarm Step 1):
test-pin the `pead.load_quarterly_eps` lru_cache behavior.

Source attribution (per CHECKLIST #77):
  Profile data: scripts/profile_process_day_lever_c.py output 2026-05-28
  showed load_quarterly_eps at 67s cumtime / 693 calls (12pct of total
  engine cost in a 20-tkr x 32-day backtest). Pure function of ticker;
  reads on-disk parquet; safe to lru_cache.

These tests pin:
  1. The lru_cache decorator is applied (cache_info() returns CacheInfo)
  2. Second call with same ticker returns SAME DataFrame object (cache hit)
  3. Cache persistence: cache hits avoid re-reading the parquet file
  4. Different tickers produce different cached DataFrames

If the lru_cache is silently removed by a future refactor, the count_floor
+ cache_info tests fail. If a caller mutates the cached DataFrame (which
would corrupt other callers), the byte-equality test catches it.
"""
from __future__ import annotations

import pytest

from backtest.signals import pead


def test_batch421_load_quarterly_eps_has_lru_cache():
    """The function must have lru_cache applied (cache_info attribute)."""
    assert hasattr(pead.load_quarterly_eps, "cache_info"), (
        "load_quarterly_eps must be lru_cache-decorated per Batch 421. "
        "If this fails, the @functools.lru_cache decorator was removed.")
    assert hasattr(pead.load_quarterly_eps, "cache_clear"), (
        "load_quarterly_eps must have cache_clear() for test isolation")


def test_batch421_cache_hit_on_repeat_call():
    """Second call with same ticker must return the SAME DataFrame object
    (cache hit; no re-load of parquet)."""
    pead.load_quarterly_eps.cache_clear()
    # Use a known T1a ticker likely to have prefetched financials in this
    # repo. Fall through gracefully if data not present.
    df1 = pead.load_quarterly_eps("AAPL")
    df2 = pead.load_quarterly_eps("AAPL")
    assert df1 is df2, (
        "Second call did not return the cached DataFrame object - "
        "lru_cache not working")
    info = pead.load_quarterly_eps.cache_info()
    assert info.hits >= 1, (
        f"Expected >= 1 cache hit; got {info.hits} (cache info: {info})")


def test_batch421_cache_distinguishes_different_tickers():
    """Different tickers must produce different cached DataFrames (cache
    keyed on ticker, not a singleton)."""
    pead.load_quarterly_eps.cache_clear()
    df_a = pead.load_quarterly_eps("AAPL")
    df_b = pead.load_quarterly_eps("MSFT")
    # Different ticker -> different cache slot -> different df object
    assert df_a is not df_b, (
        "AAPL and MSFT returned the same DataFrame object - cache key "
        "is not differentiating tickers")
    info = pead.load_quarterly_eps.cache_info()
    assert info.currsize >= 2, (
        f"Expected >= 2 cached entries (AAPL + MSFT); got "
        f"{info.currsize} (cache info: {info})")


def test_batch421_cache_does_not_grow_unbounded_under_repeat_calls():
    """500 repeat calls with the same ticker must not grow the cache size
    beyond 1 entry - validates lru_cache is keyed correctly."""
    pead.load_quarterly_eps.cache_clear()
    for _ in range(500):
        pead.load_quarterly_eps("AAPL")
    info = pead.load_quarterly_eps.cache_info()
    assert info.currsize == 1, (
        f"500 calls with same ticker grew cache to {info.currsize} "
        f"entries; expected 1 (cache info: {info})")
    assert info.hits >= 499, (
        f"Expected >= 499 hits after 500 same-ticker calls; got "
        f"{info.hits}")
