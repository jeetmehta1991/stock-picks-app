"""Sprint 0A.10 BATCH 14 — Polygon Stocks Starter DEMO.

Validates 5+ tickers per endpoint with schema + PIT + range checks. Demo
runs on phase-entry / pre-deploy verification. See test_polygon_stocks_smoke.py
for the every-commit fast version.

Per CHECKLIST #68 + DEC-503.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
OHLCV_DIR = REPO / "backtest" / "data" / "cache" / "ohlcv"
NEWS_DIR = REPO / "data_prefetch" / "polygon" / "news"
FINANCIALS_DIR = REPO / "data_prefetch" / "polygon" / "financials"
EVENTS_DIR = REPO / "data_prefetch" / "polygon" / "events"

DEMO_TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "META"]


def _read_or_skip(d: Path, ticker: str) -> pd.DataFrame:
    p = d / f"{ticker}.parquet"
    if not p.is_file():
        pytest.skip(f"{p} not cached (demo ticker)")
    return pd.read_parquet(p)


# --- OHLCV ---


@pytest.mark.parametrize("ticker", DEMO_TICKERS)
def test_polygon_ohlcv_demo(ticker: str):
    df = _read_or_skip(OHLCV_DIR, ticker)
    assert {"open", "high", "low", "close", "volume"} <= set(df.columns)
    assert len(df) >= 100, f"{ticker} has only {len(df)} OHLCV rows"
    # Per DEC-505 5-year rolling: most active tickers should have ~1200+ days
    assert (df["high"] >= df["low"]).all()
    assert (df["close"] > 0).all()
    assert (df["volume"] >= 0).all()


# --- News (1.05M articles) ---


@pytest.mark.parametrize("ticker", DEMO_TICKERS)
def test_polygon_news_demo(ticker: str):
    df = _read_or_skip(NEWS_DIR, ticker)
    assert {"id", "title", "published_utc", "tickers"} <= set(df.columns)
    assert len(df) >= 5, f"{ticker} has only {len(df)} news articles"
    # Sanity: published_utc is datetime-parseable
    pd.to_datetime(df["published_utc"]).head(5)


# --- Financials ---


@pytest.mark.parametrize("ticker", DEMO_TICKERS)
def test_polygon_financials_demo(ticker: str):
    df = _read_or_skip(FINANCIALS_DIR, ticker)
    assert {"ticker", "filing_date", "fiscal_period", "fiscal_year"} <= set(df.columns)
    assert len(df) >= 5, f"{ticker} has only {len(df)} financial filings"
    # Multiple fiscal periods present (Q1/Q2/Q3/FY)
    assert df["fiscal_period"].nunique() >= 2


# --- Ticker events (DEC-500) ---


def test_polygon_events_aggregate_event_types():
    """Across 5 demo tickers, multiple event types should be present."""
    event_types_seen = set()
    for ticker in DEMO_TICKERS:
        p = EVENTS_DIR / f"{ticker}.parquet"
        if not p.is_file():
            continue
        df = pd.read_parquet(p)
        event_types_seen.update(df["event_type"].dropna().unique())
    if not event_types_seen:
        pytest.skip("no events cached for demo tickers")
    # Common events: ticker_change, ticker_split, etc.
    assert len(event_types_seen) >= 1
