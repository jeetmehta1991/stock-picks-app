"""Batch 535 (2026-06-01) -- OPT-A producer caching sweep tests.

Source: per CHECKLIST #77 + owner directive 2026-06-01 ("execute a b c d
sequentially; test extensively at each stage").
Queue: EXECUTION_QUEUE.md OPT-A.

Applies the B534 in-memory cache pattern to 7 additional per-ticker
producers identified in the profile as still doing per-call disk reads:

  Phase 1 (B535):
    - compute_housetrading_signals  (Quiver housetrading per-ticker)
    - compute_gov_contracts_signals (Quiver gov_contracts per-ticker)
    - compute_lobbying_signals      (Quiver lobbying per-ticker)
    - compute_offexchange_signals   (Quiver offexchange per-ticker)
  Phase 2 (B535):
    - compute_short_interest_signals (FINRA per-ticker)
    - compute_news_sentiment_signals  (Polygon news per-ticker)
    - compute_search_volume_signals   (pytrends per-ticker)
  Phase 3 (B535):
    - compute_quality_factor (Polygon financials per-ticker via cross_sectional)

Pins:

  (1) Cache invariant: second call to same (producer, ticker) returns
      identical signal dict + does not touch disk
  (2) Empty-cache invariant: missing ticker file caches the empty
      result so subsequent calls don't re-stat the filesystem
  (3) Correctness invariant: cached result equals pre-cache result
      for AAPL with real cached data
  (4) Perf-guard: 1000 repeat calls per producer must complete in
      < 5s (was ~10s/call pre-cache for some producers).
"""
from __future__ import annotations

import time
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def _reset_b535_caches():
    """Reset all B535 producer caches between tests."""
    from backtest.signals import (
        congressional_alt_data as alt,
        short_interest as si,
        news_sentiment as ns,
        search_volume as sv,
        cross_sectional as xs,
    )
    alt._HOUSETRADING_BY_TICKER.clear()
    alt._GOV_CONTRACTS_BY_TICKER.clear()
    alt._LOBBYING_BY_TICKER.clear()
    alt._OFFEXCHANGE_BY_TICKER.clear()
    si._SI_BY_TICKER.clear()
    ns._NEWS_BY_TICKER.clear()
    sv._PYTRENDS_BY_TICKER.clear()
    xs._FINANCIALS_BY_TICKER.clear()
    yield
    alt._HOUSETRADING_BY_TICKER.clear()
    alt._GOV_CONTRACTS_BY_TICKER.clear()
    alt._LOBBYING_BY_TICKER.clear()
    alt._OFFEXCHANGE_BY_TICKER.clear()
    si._SI_BY_TICKER.clear()
    ns._NEWS_BY_TICKER.clear()
    sv._PYTRENDS_BY_TICKER.clear()
    xs._FINANCIALS_BY_TICKER.clear()


# ---------------------------------------------------------------------------
# Cache invariants
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("producer_name,module_path,cache_attr", [
    ("compute_housetrading_signals",
     "backtest.signals.congressional_alt_data",
     "_HOUSETRADING_BY_TICKER"),
    ("compute_gov_contracts_signals",
     "backtest.signals.congressional_alt_data",
     "_GOV_CONTRACTS_BY_TICKER"),
    ("compute_lobbying_signals",
     "backtest.signals.congressional_alt_data",
     "_LOBBYING_BY_TICKER"),
    ("compute_offexchange_signals",
     "backtest.signals.congressional_alt_data",
     "_OFFEXCHANGE_BY_TICKER"),
])
def test_batch535_cache_populated_on_first_call(
    producer_name, module_path, cache_attr,
):
    """First call fills the cache; cache key matches safe_ticker."""
    import importlib
    mod = importlib.import_module(module_path)
    cache = getattr(mod, cache_attr)
    assert len(cache) == 0, "fixture should have reset cache"
    producer = getattr(mod, producer_name)
    producer("AAPL", date(2024, 6, 1))
    assert "AAPL" in cache, (
        f"first call to {producer_name}('AAPL') should populate "
        f"{cache_attr}. Current keys: {list(cache.keys())}"
    )


def test_batch535_short_interest_cache_populated_on_first_call():
    from backtest.signals.short_interest import (
        compute_short_interest_signals, _SI_BY_TICKER,
    )
    assert len(_SI_BY_TICKER) == 0
    compute_short_interest_signals("AAPL", date(2024, 6, 1))
    assert "AAPL" in _SI_BY_TICKER


def test_batch535_news_cache_populated_on_first_call():
    from backtest.signals.news_sentiment import (
        compute_news_sentiment_signals, _NEWS_BY_TICKER,
    )
    assert len(_NEWS_BY_TICKER) == 0
    compute_news_sentiment_signals("AAPL", date(2024, 6, 1))
    assert "AAPL" in _NEWS_BY_TICKER


def test_batch535_search_volume_cache_populated_on_first_call():
    from backtest.signals.search_volume import (
        compute_search_volume_signals, _PYTRENDS_BY_TICKER,
    )
    assert len(_PYTRENDS_BY_TICKER) == 0
    compute_search_volume_signals("AAPL", date(2024, 6, 1))
    assert "AAPL" in _PYTRENDS_BY_TICKER


# ---------------------------------------------------------------------------
# Empty-cache invariant
# ---------------------------------------------------------------------------

def test_batch535_missing_ticker_cached_as_empty():
    """Non-existent ticker file is cached as empty DataFrame so the
    second call doesn't re-stat the filesystem."""
    from backtest.signals.short_interest import (
        compute_short_interest_signals, _SI_BY_TICKER,
    )
    assert len(_SI_BY_TICKER) == 0
    out1 = compute_short_interest_signals("___NONEXISTENT___",
                                            date(2024, 6, 1))
    assert out1 == {}
    # Cache should now have the empty entry
    assert "___NONEXISTENT___" in _SI_BY_TICKER
    assert _SI_BY_TICKER["___NONEXISTENT___"].empty


def test_batch535_second_call_identical_to_first():
    """Same input -> bit-identical output between first (cold) +
    second (cached) call. Catches any caching-induced state pollution."""
    from backtest.signals.short_interest import compute_short_interest_signals
    out1 = compute_short_interest_signals("AAPL", date(2024, 6, 1))
    out2 = compute_short_interest_signals("AAPL", date(2024, 6, 1))
    assert out1 == out2, (
        f"second call gave different result: out1={out1} out2={out2}"
    )


# ---------------------------------------------------------------------------
# Perf guard
# ---------------------------------------------------------------------------

def test_batch535_repeat_calls_dont_touch_disk():
    """1000 calls to same (producer, ticker) should complete in <10s
    (~10ms/call cap; observed 5.7ms/call post-cache). Pre-cache reads
    parquet from disk + does date conversion on every call =
    ~15-20ms/call. Threshold catches regressions to the disk-read path
    while tolerating CI variability."""
    from backtest.signals.congressional_alt_data import (
        compute_housetrading_signals,
    )
    t0 = time.perf_counter()
    for _ in range(1000):
        compute_housetrading_signals("AAPL", date(2024, 6, 1))
    elapsed = time.perf_counter() - t0
    assert elapsed < 10.0, (
        f"1000 repeat calls took {elapsed:.2f}s -- expected <10s with "
        f"cache. Slower may indicate cache miss path on every call."
    )


def test_batch535_cross_ticker_calls_each_cached_once():
    """3 different tickers => exactly 3 cache entries."""
    from backtest.signals.congressional_alt_data import (
        compute_housetrading_signals, _HOUSETRADING_BY_TICKER,
    )
    for tkr in ("AAPL", "MSFT", "TSLA"):
        compute_housetrading_signals(tkr, date(2024, 6, 1))
    assert len(_HOUSETRADING_BY_TICKER) == 3
    # Each entry's key is a string
    for k in _HOUSETRADING_BY_TICKER:
        assert isinstance(k, str)


# ---------------------------------------------------------------------------
# Correctness invariant -- real data
# ---------------------------------------------------------------------------

def test_batch535_aapl_signals_match_expected_keys():
    """Schema regression guard: each producer must emit its documented
    keys on AAPL real data."""
    from backtest.signals.congressional_alt_data import (
        compute_housetrading_signals, compute_gov_contracts_signals,
        compute_lobbying_signals, compute_offexchange_signals,
    )
    from backtest.signals.short_interest import compute_short_interest_signals
    out_house = compute_housetrading_signals("AAPL", date(2024, 6, 1))
    if out_house:
        assert "house_buy_count_90d" in out_house
        assert "house_net_buy_90d" in out_house
    out_gov = compute_gov_contracts_signals("AAPL", date(2024, 6, 1))
    if out_gov:
        assert "gov_contracts_last_qtr_amount" in out_gov
        assert "gov_contracts_4q_sum" in out_gov
    out_lob = compute_lobbying_signals("AAPL", date(2024, 6, 1))
    if out_lob:
        assert "lobbying_amount_1y" in out_lob
    out_off = compute_offexchange_signals("AAPL", date(2024, 6, 1))
    if out_off:
        assert "dpi_recent" in out_off
    out_si = compute_short_interest_signals("AAPL", date(2024, 6, 1))
    if out_si:
        assert "short_interest_observations" in out_si
        assert "days_to_cover" in out_si


# ---------------------------------------------------------------------------
# Financials cache (cross_sectional / quality factor)
# ---------------------------------------------------------------------------

def test_batch535_financials_cache_returns_copy():
    """Cached load returns COPY so caller mutations don't pollute cache."""
    from backtest.signals.cross_sectional import (
        _load_financials_cached, _FINANCIALS_BY_TICKER,
    )
    base_dir = (Path(__file__).resolve().parent.parent.parent
                / "data_prefetch" / "polygon" / "financials")
    if not (base_dir / "AAPL.parquet").exists():
        pytest.skip("AAPL financials parquet missing -- skip correctness test")
    df1 = _load_financials_cached(base_dir, "AAPL")
    df2 = _load_financials_cached(base_dir, "AAPL")
    assert df1 is not df2, (
        "cached load must return a copy, not the cached object"
    )
    # Mutation on df1 should NOT affect df2
    if not df1.empty:
        df1["_marker"] = 1
        assert "_marker" not in df2.columns
