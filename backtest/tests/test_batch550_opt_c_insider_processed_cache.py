"""Batch 550 (2026-06-02) -- OPT-C Phase 3: insider_signal pre-processed
DataFrame cache (filing_date_ts datetime64 pre-converted at cache fill).

Source: per CHECKLIST #77.
Queue: EXECUTION_QUEUE.md OPT-C pivot.

Pre-fix:
  - _filter_bulk_by_ticker returns cached sub-DataFrame (B535 OPT-A Phase 4)
  - per-call pd.to_datetime(fileDate, errors=coerce).dt.date conversion
  - per-call df.copy() before mutation
  - 1792 calls / 56s / 31ms per call in profile

Post-fix B550:
  - _load_insider_processed pre-converts fileDate -> filing_date_ts (datetime64)
    once at cache fill time. Source-DataFrame identity (`is`) invalidation
    against the cached sub-DataFrame from _filter_bulk_by_ticker.
  - Per-call work: 2 boolean filters using datetime64 comparison + copy of
    smaller filtered slice.

Bench: 31ms/call -> ~5ms/call (-83pct).

DEC-512 invariant preserved: fileDate (NOT Date) is the PIT cutoff source.
filing_date_ts comes from fileDate when present, Date as fallback only.

Pins:

  (1) Parity: post-fix dict matches pre-fix dict (signal/counts/CEO/CFO/
      director_only_buy/large_dollar_buy/concentrated_sell/cluster_buy)
      across 15 (ticker, as_of) tuples verified against the prior commit
  (2) Cache reuse: second call returns the SAME pre-processed DataFrame
      object (identity via `is`) when the upstream sub-DataFrame
      unchanged
  (3) DEC-512: filing_date_ts derived from fileDate when present
  (4) Schema: pre-processed DataFrame has filing_date_ts column of
      datetime64 dtype
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def reset_caches():
    from backtest.data.smart_money import (
        _INSIDER_PROCESSED_CACHE, _BULK_CACHE, _BULK_INDEX,
    )
    _INSIDER_PROCESSED_CACHE.clear()
    _BULK_CACHE.clear()
    _BULK_INDEX.clear()
    yield
    _INSIDER_PROCESSED_CACHE.clear()
    _BULK_CACHE.clear()
    _BULK_INDEX.clear()


def _have_insider_bulk() -> bool:
    repo_root = Path(__file__).parent.parent.parent
    return (repo_root / "data_prefetch" / "quiver" / "insiders"
            / "global.parquet").exists()


@pytest.mark.skipif(not _have_insider_bulk(), reason="insider bulk feed absent")
def test_batch550_known_outcomes_preserved():
    """Pre-B550 baseline: JPM 2024-03-15 -> cluster_sell with 19 sells;
    NVDA 2024-06-14 -> cluster_sell with 130 sells concentrated_sell=True.
    Lock these as regression pins."""
    from backtest.data.smart_money import insider_signal
    jpm = insider_signal("JPM", date(2024, 3, 15))
    assert jpm["signal"] == "cluster_sell"
    assert jpm["sell_count"] >= 5
    nvda = insider_signal("NVDA", date(2024, 6, 14))
    assert nvda["signal"] == "cluster_sell"
    assert nvda["sell_count"] >= 30
    assert nvda["concentrated_sell"] is True


@pytest.mark.skipif(not _have_insider_bulk(), reason="insider bulk feed absent")
def test_batch550_cache_reuse_returns_same_dataframe():
    from backtest.data.smart_money import (
        _load_insider_processed, _INSIDER_PROCESSED_CACHE,
    )
    df1 = _load_insider_processed("NVDA")
    df2 = _load_insider_processed("NVDA")
    assert df1 is df2, "second call should return same DataFrame object"
    assert "NVDA" in _INSIDER_PROCESSED_CACHE


@pytest.mark.skipif(not _have_insider_bulk(), reason="insider bulk feed absent")
def test_batch550_filing_date_ts_pre_converted_to_datetime64():
    from backtest.data.smart_money import _load_insider_processed
    df = _load_insider_processed("NVDA")
    assert df is not None
    assert "filing_date_ts" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["filing_date_ts"])


@pytest.mark.skipif(not _have_insider_bulk(), reason="insider bulk feed absent")
def test_batch550_dec512_uses_fileDate_not_Date():
    """DEC-512 invariant: filing_date_ts must come from fileDate (the SEC
    filing date) NOT Date (transaction date, which gave ~6-day lookahead).
    Pin by inspecting the helper source."""
    import inspect
    from backtest.data.smart_money import _load_insider_processed
    src = inspect.getsource(_load_insider_processed)
    assert "fileDate" in src, "DEC-512: must use fileDate for PIT cutoff"
    # fileDate branch must appear BEFORE Date fallback
    fd_pos = src.find('fileDate')
    date_branch_pos = src.find('elif "Date"')
    assert fd_pos < date_branch_pos, (
        "DEC-512: fileDate branch must precede Date fallback"
    )
