"""Wave B regression tests — G7 SEC EDGAR catalyst accessors (Pass 53 Day-9 v8c).

Closes 1 of 13 remaining L146/DEC-507 wiring gaps. Wires the 6056-file SEC
EDGAR prefetch (4 form types) into smart_money.py via:
  - get_sec_filings(ticker, as_of, lookback_days, form)
  - sec_catalyst_signal(ticker, as_of)

Strategy-side wiring deferred to Phase 1B+ (Layer-2 catalyst signal candidate).
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_g7_sec_edgar_prefetch_present():
    """All 4 form types must have prefetched parquets."""
    base = REPO_ROOT / "data_prefetch" / "sec_edgar"
    for sub in ["4", "8_K", "SC_13D", "SC_13G"]:
        d = base / sub
        assert d.exists(), f"SEC EDGAR {sub} prefetch dir missing"
        files = list(d.glob("*.parquet"))
        assert len(files) > 100, (
            f"SEC EDGAR {sub} has only {len(files)} files — expected >100"
        )


def test_g7_get_sec_filings_returns_data():
    from backtest.data.smart_money import get_sec_filings
    # AAPL filed 8-K on 2024-05-02 + 2024-05-03 → date 2024-05-06 lookback 10d
    # should return count=2
    r = get_sec_filings("AAPL", date(2024, 5, 6), 10, "8-K")
    assert r["count"] >= 1, (
        f"AAPL 2024-05-06 8-K(10d) returned count={r['count']}; expected ≥1 "
        f"(known filings 2024-05-02 + 2024-05-03)"
    )
    assert r["days_since"] is not None
    assert r["days_since"] >= 0


def test_g7_get_sec_filings_unknown_ticker_safe():
    from backtest.data.smart_money import get_sec_filings
    r = get_sec_filings("ZZZZ_NOT_REAL_TICKER", date(2024, 6, 15), 30, "8-K")
    assert r == {"count": 0, "most_recent": None, "days_since": None,
                  "filings": []}


def test_g7_sec_catalyst_signal_composite():
    from backtest.data.smart_money import sec_catalyst_signal
    s = sec_catalyst_signal("AAPL", date(2024, 5, 6))
    assert "score" in s
    assert "label" in s
    assert s["8k"]["count"] >= 1
    # 2024-05-03 8-K within 5 trading days of 2024-05-06 → score ≥ 1
    assert s["score"] >= 1


def test_g7_sec_filing_form_types_complete():
    """All 4 form types reachable via SEC_EDGAR_FORM_DIRS map."""
    from backtest.data.smart_money import SEC_EDGAR_FORM_DIRS
    assert set(SEC_EDGAR_FORM_DIRS.keys()) == {"4", "8-K", "SC 13D", "SC 13G"}


def test_g7_filings_pit_correctness():
    """Filings filed AFTER as_of must NOT be returned (point-in-time correctness)."""
    from backtest.data.smart_money import get_sec_filings
    # Get all AAPL 8-Ks up to 2020-12-31; none should be from 2021+
    r = get_sec_filings("AAPL", date(2020, 12, 31), 10000, "8-K")
    if r["count"] > 0:
        for f in r["filings"]:
            assert f["filing_date"] <= pd.Timestamp(date(2020, 12, 31)), (
                f"PIT violation: filing_date {f['filing_date']} > as_of 2020-12-31"
            )


# Need pd for the pytest module-level
import pandas as pd
