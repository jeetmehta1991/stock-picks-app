"""Sprint 0A.10 BATCH 14 — Quiver Trader DEMO.

Validates 5+ tickers per per-ticker endpoint and statistical sanity for bulk
endpoints. Per CHECKLIST #68 + DEC-503.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
QUIVER_DIR = REPO / "backtest" / "data" / "cache" / "quiver"

DEMO_TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "META"]


def _read_or_skip(d: Path, ticker: str) -> pd.DataFrame:
    p = d / f"{ticker}.parquet"
    if not p.is_file():
        pytest.skip(f"{p} not cached (demo ticker)")
    return pd.read_parquet(p)


# --- Bulk endpoints — slice by ticker ---


def test_quiver_insiders_demo_ticker_coverage():
    df = pd.read_parquet(QUIVER_DIR / "insiders" / "global.parquet")
    seen = set(df["Ticker"].dropna().astype(str).str.upper().unique())
    found = [t for t in DEMO_TICKERS if t in seen]
    assert len(found) >= 4, f"only {len(found)}/5 demo tickers in insiders bulk: {found}"


def test_quiver_sec13fchanges_demo_ticker_coverage():
    df = pd.read_parquet(QUIVER_DIR / "sec13fchanges" / "global.parquet")
    seen = set(df["Ticker"].dropna().astype(str).str.upper().unique())
    found = [t for t in DEMO_TICKERS if t in seen]
    assert len(found) >= 4, f"only {len(found)}/5 demo tickers in 13F bulk: {found}"


# --- Per-ticker endpoints ---


@pytest.mark.parametrize("ticker", DEMO_TICKERS)
def test_quiver_offexchange_demo(ticker: str):
    df = _read_or_skip(QUIVER_DIR / "offexchange", ticker)
    assert {"Ticker", "Date"} <= set(df.columns)
    assert len(df) >= 50, f"{ticker} only {len(df)} off-exchange rows"


@pytest.mark.parametrize("ticker", DEMO_TICKERS)
def test_quiver_congressional_demo(ticker: str):
    df = _read_or_skip(QUIVER_DIR / "congressional", ticker)
    assert {"Ticker", "TransactionDate", "Transaction"} <= set(df.columns)
    # Some demo tickers may have 0 congressional trades; that's valid
    assert df.empty or {"Purchase", "Sale", "Sale (Partial)", "Sale (Full)", "Exchange", "Receive"} & set(df["Transaction"].unique())


def test_quiver_lobbying_demo_aggregate():
    """Across demo tickers, expect at least some lobbying records."""
    total = 0
    for ticker in DEMO_TICKERS:
        p = QUIVER_DIR / "lobbying" / f"{ticker}.parquet"
        if not p.is_file():
            continue
        total += len(pd.read_parquet(p))
    if total == 0:
        pytest.skip("no lobbying records cached for demo tickers")
    assert total >= 5
