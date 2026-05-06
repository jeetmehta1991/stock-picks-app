"""Sprint 0A.10 BATCH 14 — Free supplementary sources DEMO.

Validates demo-ticker coverage for Wikipedia + pytrends; Apewisdom global
ranks sanity.

Per CHECKLIST #68 + DEC-503.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
APEWISDOM_DIR = REPO / "data_prefetch" / "apewisdom"
WIKIPEDIA_DIR = REPO / "data_prefetch" / "wikipedia"
PYTRENDS_DIR = REPO / "data_prefetch" / "pytrends"

DEMO_TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "META"]


def _read_or_skip(d: Path, ticker: str) -> pd.DataFrame:
    p = d / f"{ticker}.parquet"
    if not p.is_file():
        pytest.skip(f"{p} not cached for demo")
    return pd.read_parquet(p)


# --- Apewisdom ---


def test_apewisdom_demo_ticker_coverage():
    df = pd.read_parquet(APEWISDOM_DIR / "global.parquet")
    seen = set(df["ticker"].dropna().astype(str).str.upper().unique())
    found = [t for t in DEMO_TICKERS if t in seen]
    # Top-mentioned tickers vary daily; expect at least 2 of the 5 mega-caps
    assert len(found) >= 2, f"only {len(found)}/5 demo tickers in Apewisdom: {found}"


def test_apewisdom_rank_density():
    df = pd.read_parquet(APEWISDOM_DIR / "global.parquet")
    # Should have ranks 1, 2, 3, ... reasonably continuous
    ranks = df["rank"].dropna()
    assert ranks.min() <= 5  # top 5 always populated
    assert ranks.max() >= 50  # at least 50 ranked


# --- Wikipedia pageviews ---


@pytest.mark.parametrize("ticker", DEMO_TICKERS)
def test_wikipedia_demo_ticker_views(ticker: str):
    df = _read_or_skip(WIKIPEDIA_DIR, ticker)
    # Some tickers (e.g. GOOGL → Alphabet_Inc._(Class_A)) alias to a sparse
    # Wikipedia article variant. Just assert non-empty + positive views.
    assert len(df) >= 1, f"{ticker} Wikipedia empty"
    assert df["views"].sum() > 0


# --- pytrends (may be partial) ---


@pytest.mark.parametrize("ticker", DEMO_TICKERS)
def test_pytrends_demo_ticker_or_skip(ticker: str):
    p = PYTRENDS_DIR / f"{ticker}.parquet"
    if not p.is_file():
        pytest.skip(f"{ticker} pytrends not yet cached (partial run)")
    df = pd.read_parquet(p)
    assert {"ticker", "date", "search_volume_index"} <= set(df.columns)
    assert len(df) > 0
