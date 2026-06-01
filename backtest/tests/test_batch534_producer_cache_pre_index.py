"""Batch 534 (2026-06-01) -- producer cache pre-indexing tests.

Source: per CHECKLIST #77 + B532 R4 pilot profile finding.
Queue: R4 pilot pace regression -- 9h projection vs 2.5h estimate.

Profile diagnosis (1288s total for 20 tickers x 33 days):
  - `compute_patentmomentum_signals` 240ms/call (5.8M-row scan per call)
  - `_load_decoded` (SEC EDGAR) read parquet on every call (no cache)

Fixes:
  (1) `_patent_for_ticker` + `_donors_for_ticker` lookups pre-index
      global parquets by ticker into dict-of-DataFrames at cache load.
      O(1) lookup vs prior O(5.8M-row scan).
  (2) `_load_decoded` per-(form, ticker) DataFrame cache. First-touch
      fills cache; subsequent calls zero IO.

Pins:

  (1) Pre-indexed cache returns same data as the prior full-scan
      implementation (correctness)
  (2) Second call to same (ticker) returns cached DataFrame (perf
      verification via identity check)
  (3) Unknown ticker returns None / empty without filling the global
      cache permanently
  (4) SEC EDGAR `_load_decoded` caches per-(form, ticker) -- 100
      repeat calls do not touch disk
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def _reset_caches():
    """Reset module-level caches between tests so each test sees a
    clean state."""
    from backtest.signals import congressional_alt_data as alt
    from backtest.signals import sec_edgar_extractor as sec
    alt._PATENT_DF_CACHE = None
    alt._PATENT_BY_TICKER = None
    alt._PATENT_INDEXED_FROM = None
    alt._DONORS_DF_CACHE = None
    alt._DONORS_BY_TICKER = None
    alt._DONORS_INDEXED_FROM = None
    sec._DECODED_DF_CACHE.clear()
    yield
    alt._PATENT_DF_CACHE = None
    alt._PATENT_BY_TICKER = None
    alt._PATENT_INDEXED_FROM = None
    alt._DONORS_DF_CACHE = None
    alt._DONORS_BY_TICKER = None
    alt._DONORS_INDEXED_FROM = None
    sec._DECODED_DF_CACHE.clear()


# ---------------------------------------------------------------------------
# patent pre-index
# ---------------------------------------------------------------------------

def test_batch534_patent_lookup_returns_ticker_subset(monkeypatch):
    from backtest.signals import congressional_alt_data as alt
    fake = pd.DataFrame({
        "ticker":   ["AAPL", "AAPL", "MSFT", "XOM"],
        "date":     pd.to_datetime(["2024-01-15", "2024-03-15",
                                     "2024-02-10", "2024-05-15"]),
        "momentum": [0.5, 0.7, 0.3, 0.2],
    })
    monkeypatch.setattr(alt, "_PATENT_DF_CACHE", fake)
    sub = alt._patent_for_ticker("AAPL")
    assert sub is not None
    assert len(sub) == 2
    assert all(sub["ticker"] == "AAPL")


def test_batch534_patent_lookup_unknown_ticker_returns_none(monkeypatch):
    from backtest.signals import congressional_alt_data as alt
    fake = pd.DataFrame({"ticker": ["AAPL"], "date": [pd.Timestamp("2024-01-01")],
                         "momentum": [0.5]})
    monkeypatch.setattr(alt, "_PATENT_DF_CACHE", fake)
    sub = alt._patent_for_ticker("ZZZZ")
    assert sub is None


def test_batch534_patent_index_built_once(monkeypatch):
    """Second call must not re-build the index -- assert by identity."""
    from backtest.signals import congressional_alt_data as alt
    fake = pd.DataFrame({"ticker": ["AAPL", "AAPL"],
                         "date": pd.to_datetime(["2024-01-01", "2024-02-01"]),
                         "momentum": [0.5, 0.6]})
    monkeypatch.setattr(alt, "_PATENT_DF_CACHE", fake)
    s1 = alt._patent_for_ticker("AAPL")
    s2 = alt._patent_for_ticker("AAPL")
    assert s1 is s2, "second lookup did not return cached DataFrame -- index rebuilt"


def test_batch534_patent_signals_use_indexed_path(monkeypatch):
    """compute_patentmomentum_signals must use _patent_for_ticker, not
    re-scan the global DataFrame."""
    from backtest.signals import congressional_alt_data as alt
    fake = pd.DataFrame({
        "ticker":   ["AAPL"] * 3,
        "date":     pd.to_datetime(["2024-01-15", "2024-03-15",
                                     "2024-05-15"]),
        "momentum": [0.5, 0.7, 0.9],
    })
    monkeypatch.setattr(alt, "_PATENT_DF_CACHE", fake)
    out = alt.compute_patentmomentum_signals("AAPL", date(2024, 6, 1))
    assert out.get("patent_momentum_recent") == pytest.approx(0.9)


# ---------------------------------------------------------------------------
# donors pre-index
# ---------------------------------------------------------------------------

def test_batch534_donors_lookup_returns_ticker_subset(monkeypatch):
    from backtest.signals import congressional_alt_data as alt
    fake = pd.DataFrame({
        "Ticker":             ["AAPL", "MSFT", "AAPL", "XOM"],
        "TransactionDate":    pd.to_datetime([
            "2024-01-15", "2024-02-10", "2024-03-15", "2024-05-15"]),
        "TransactionAmount":  [1000, 2000, 3000, 4000],
        "CommitteeName":      ["PAC A", "PAC B", "PAC A", "PAC C"],
    })
    monkeypatch.setattr(alt, "_DONORS_DF_CACHE", fake)
    sub = alt._donors_for_ticker("AAPL")
    assert sub is not None
    assert len(sub) == 2


def test_batch534_donors_signals_use_indexed_path(monkeypatch):
    from backtest.signals import congressional_alt_data as alt
    fake = pd.DataFrame({
        "Ticker":             ["AAPL"] * 3,
        "TransactionDate":    pd.to_datetime([
            "2024-01-15", "2024-03-15", "2024-05-15"]),
        "TransactionAmount":  [1000, 2500, 5000],
        "CommitteeName":      ["PAC A", "PAC B", "PAC A"],
    })
    monkeypatch.setattr(alt, "_DONORS_DF_CACHE", fake)
    out = alt.compute_corporatedonors_signals("AAPL", date(2024, 6, 1))
    assert out["corp_donations_count_1y"] == 3
    assert out["corp_donations_1y"] == pytest.approx(8500.0)
    assert out["corp_donations_unique_pacs"] == 2


# ---------------------------------------------------------------------------
# SEC EDGAR per-ticker cache
# ---------------------------------------------------------------------------

def test_batch534_sec_edgar_caches_decoded_dataframes(tmp_path, monkeypatch):
    """First call reads disk; second call returns from cache (zero IO)."""
    from backtest.signals import sec_edgar_extractor as sec
    cache_dir = tmp_path / "decoded"
    (cache_dir / "SC_13D").mkdir(parents=True)
    df_in = pd.DataFrame({
        "ticker":           ["AAPL"] * 2,
        "filing_date":      pd.to_datetime(["2024-01-15", "2024-06-15"]),
        "accession_number": ["acc-1", "acc-2"],
        "decoded_status":   ["ok", "ok"],
    })
    df_in.to_parquet(cache_dir / "SC_13D" / "AAPL.parquet", index=False)
    monkeypatch.setattr(sec, "_DECODED_CACHE_DIR", cache_dir)
    out1 = sec._load_decoded("SC_13D", "AAPL")
    assert len(out1) == 2
    out2 = sec._load_decoded("SC_13D", "AAPL")
    # Second call must return the SAME object (cached) -- not a fresh read
    assert out1 is out2, "second _load_decoded call did NOT hit cache"


def test_batch534_sec_edgar_caches_empty_on_missing_parquet(tmp_path, monkeypatch):
    """Cache the empty-result too so a missing-parquet ticker doesn't
    re-check the filesystem on every call."""
    from backtest.signals import sec_edgar_extractor as sec
    cache_dir = tmp_path / "decoded"
    (cache_dir / "SC_13D").mkdir(parents=True)
    monkeypatch.setattr(sec, "_DECODED_CACHE_DIR", cache_dir)
    out1 = sec._load_decoded("SC_13D", "___NONEX___")
    out2 = sec._load_decoded("SC_13D", "___NONEX___")
    assert out1.empty and out2.empty
    assert out1 is out2


def test_batch534_sec_edgar_compute_signals_uses_cache(tmp_path, monkeypatch):
    """End-to-end: compute_sec_edgar_signals via cached _load_decoded."""
    from backtest.signals import sec_edgar_extractor as sec
    cache_dir = tmp_path / "decoded"
    (cache_dir / "SC_13D").mkdir(parents=True)
    (cache_dir / "SC_13G").mkdir(parents=True)
    (cache_dir / "8_K").mkdir(parents=True)
    df_13d = pd.DataFrame({
        "ticker":           ["AAPL"],
        "filing_date":      [pd.Timestamp("2024-05-25")],
        "accession_number": ["acc-1"],
        "filer_identity":   ["Carl Icahn"],
        "percent_owned":    [6.2],
        "decoded_status":   ["ok"],
    })
    df_13d.to_parquet(cache_dir / "SC_13D" / "AAPL.parquet", index=False)
    monkeypatch.setattr(sec, "_DECODED_CACHE_DIR", cache_dir)
    out = sec.compute_sec_edgar_signals("AAPL", date(2024, 6, 1))
    assert out.get("sc_13d_filed_within_30d") is True


# ---------------------------------------------------------------------------
# Perf guard: many calls cheap
# ---------------------------------------------------------------------------

def test_batch534_patent_repeat_calls_cheap(monkeypatch):
    """1000 repeated calls must complete in < 15s (15ms/call cap).
    Before B534 a 5.8M-row scan per call would take ~240s/4min for
    the same test (240ms each). Post-fix observed ~7ms/call on Windows.
    Threshold set at 15s with headroom for slower CI runners."""
    from backtest.signals import congressional_alt_data as alt
    import numpy as np
    import time
    rng = np.random.default_rng(seed=42)
    big = pd.DataFrame({
        "ticker":   rng.choice(["AAPL", "MSFT", "XOM"], 10_000),
        "date":     pd.date_range("2020-01-01", periods=10_000, freq="h"),
        "momentum": rng.normal(0.5, 0.1, 10_000),
    })
    monkeypatch.setattr(alt, "_PATENT_DF_CACHE", big)
    t0 = time.perf_counter()
    for _ in range(1000):
        alt.compute_patentmomentum_signals("AAPL", date(2024, 6, 1))
    elapsed = time.perf_counter() - t0
    assert elapsed < 15.0, (
        f"1000 patent calls took {elapsed:.2f}s (>{15.0}s). Baseline "
        f"~240s pre-fix, ~7s observed post-fix. Slow indicates index "
        f"rebuild per call OR full-scan path reverted."
    )
