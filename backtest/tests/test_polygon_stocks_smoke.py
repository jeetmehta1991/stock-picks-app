"""Sprint 0A.10 BATCH 14 — Polygon Stocks Starter SMOKE.

Validates that every Polygon-cached endpoint can be opened, schema-checked,
and sampled at minimal scale (1 file / 1-3 records). Smoke runs every commit
via CI. See test_polygon_stocks_demo.py for wider validation.

Endpoints covered: OHLCV daily, news, financials, ticker events.

Per CHECKLIST #68 (smoke→demo→full) + DEC-503 9-layer test pyramid.
NO live API calls (DEC-497 NO-LIVE-API HARD CUT).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
OHLCV_DIR = REPO / "backtest" / "data" / "cache" / "ohlcv"
NEWS_DIR = REPO / "data_prefetch" / "polygon" / "news"
FINANCIALS_DIR = REPO / "data_prefetch" / "polygon" / "financials"
EVENTS_DIR = REPO / "data_prefetch" / "polygon" / "events"


def _first_parquet(d: Path) -> Path:
    files = sorted(d.glob("*.parquet"))
    if not files:
        pytest.skip(f"no parquet files in {d}")
    return files[0]


# --- OHLCV ---


def test_polygon_ohlcv_cache_populated():
    files = list(OHLCV_DIR.glob("*.parquet"))
    assert len(files) >= 1500, f"expected ≥1500 OHLCV tickers cached, got {len(files)}"


def test_polygon_ohlcv_smoke_schema():
    df = pd.read_parquet(_first_parquet(OHLCV_DIR))
    assert {"open", "high", "low", "close", "volume"} <= set(df.columns)
    assert len(df) > 0
    # Sanity: high ≥ low for first 3 rows
    sample = df.head(3)
    assert (sample["high"] >= sample["low"]).all()


# --- News ---


def test_polygon_news_cache_populated():
    files = list(NEWS_DIR.glob("*.parquet"))
    assert len(files) >= 1500, f"expected ≥1500 ticker news files, got {len(files)}"


def test_polygon_news_smoke_schema():
    df = pd.read_parquet(_first_parquet(NEWS_DIR))
    assert {"id", "title", "published_utc", "tickers"} <= set(df.columns)
    assert len(df) > 0


# --- Financials ---


def test_polygon_financials_cache_populated():
    files = list(FINANCIALS_DIR.glob("*.parquet"))
    assert len(files) >= 1500, f"expected ≥1500 financials files, got {len(files)}"


def test_polygon_financials_smoke_schema():
    df = pd.read_parquet(_first_parquet(FINANCIALS_DIR))
    assert {"ticker", "filing_date", "fiscal_period", "fiscal_year"} <= set(df.columns)
    assert len(df) > 0


# --- Ticker events (DEC-500) ---


def test_polygon_events_cache_populated():
    files = list(EVENTS_DIR.glob("*.parquet"))
    assert len(files) >= 1500, f"expected ≥1500 ticker-events files, got {len(files)}"


def test_polygon_events_smoke_schema():
    df = pd.read_parquet(_first_parquet(EVENTS_DIR))
    assert {"ticker", "event_type", "event_date"} <= set(df.columns)
    assert len(df) > 0
