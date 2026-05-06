"""Sprint 0A.10 BATCH 14 — SEC EDGAR DEMO.

Validates demo-ticker coverage across 4 form types + filing date sanity.

NOTE: SEC EDGAR consumer state is 🔴 NOT WIRED (parsers + Fundamentals
Analyst Sprint 4 work). These tests validate the PREFETCH layer only.

Per CHECKLIST #68 + DEC-503.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
EDGAR_DIR = REPO / "data_prefetch" / "sec_edgar"
FORM_DIRS = {
    "Form 4": EDGAR_DIR / "4",
    "8-K": EDGAR_DIR / "8_K",
    "SC 13D": EDGAR_DIR / "SC_13D",
    "SC 13G": EDGAR_DIR / "SC_13G",
}

DEMO_TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "META"]


def _read_or_skip(d: Path, ticker: str) -> pd.DataFrame:
    p = d / f"{ticker}.parquet"
    if not p.is_file():
        pytest.skip(f"{p} not cached for demo")
    return pd.read_parquet(p)


@pytest.mark.parametrize("form_label,form_dir", list(FORM_DIRS.items()))
@pytest.mark.parametrize("ticker", DEMO_TICKERS)
def test_sec_edgar_demo_ticker_x_form(form_label: str, form_dir: Path, ticker: str):
    df = _read_or_skip(form_dir, ticker)
    assert {"ticker", "filing_date"} <= set(df.columns), f"{form_label} {ticker} missing required cols"
    # Filing dates should be parseable
    dates = pd.to_datetime(df["filing_date"], errors="coerce").dropna()
    assert len(dates) > 0, f"{form_label} {ticker} no parseable filing dates"


def test_sec_edgar_form_4_filing_recency():
    """Form 4 (insider transactions) should have recent filings for AAPL."""
    p = FORM_DIRS["Form 4"] / "AAPL.parquet"
    if not p.is_file():
        pytest.skip("AAPL Form 4 not cached")
    df = pd.read_parquet(p)
    dates = pd.to_datetime(df["filing_date"], errors="coerce").dropna()
    if dates.empty:
        pytest.skip("no filing dates")
    assert dates.max() >= pd.Timestamp("2023-01-01"), f"AAPL Form 4 latest {dates.max()}"


def test_sec_edgar_8k_event_density():
    """Demo tickers should have ≥10 8-K filings each (corporate event density)."""
    counts = {}
    for ticker in DEMO_TICKERS:
        p = FORM_DIRS["8-K"] / f"{ticker}.parquet"
        if not p.is_file():
            continue
        counts[ticker] = len(pd.read_parquet(p))
    if not counts:
        pytest.skip("no 8-K demo files cached")
    for ticker, n in counts.items():
        assert n >= 10, f"{ticker} has only {n} 8-K filings"
