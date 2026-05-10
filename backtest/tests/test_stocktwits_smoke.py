"""Sprint 0A.7 (Pass 53 v8h+1 2026-05-10) - StockTwits SMOKE.

Per-API smoke test for StockTwits retail-attention prefetch (DEC-599).

Validates: cache exists, expected schema cols, smoke ticker fixtures readable.

Per CHECKLIST #68 + DEC-503 + DEC-599.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
ST_DIR = REPO / "data_prefetch" / "stocktwits"

EXPECTED_COLS = {"id", "body", "created_at", "sentiment", "user_id",
                 "user_username", "likes_total", "conversation_count"}

SMOKE_TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "TSLA"]


def test_stocktwits_cache_dir_exists():
    assert ST_DIR.is_dir(), f"StockTwits cache dir missing: {ST_DIR}"


def test_stocktwits_universe_population_minimum():
    files = list(ST_DIR.glob("*.parquet"))
    # Per DEC-599 BG b27jw7urk completed 1937/1937 underlyings
    assert len(files) >= 1500, (
        f"StockTwits only has {len(files)} ticker files; expected ~1937"
    )


@pytest.mark.parametrize("ticker", SMOKE_TICKERS)
def test_stocktwits_smoke_ticker_schema(ticker: str):
    p = ST_DIR / f"{ticker}.parquet"
    if not p.is_file():
        pytest.skip(f"StockTwits cache miss for {ticker}")
    df = pd.read_parquet(p)
    missing = EXPECTED_COLS - set(df.columns)
    assert not missing, f"StockTwits {ticker} missing cols: {missing}"


@pytest.mark.parametrize("ticker", SMOKE_TICKERS)
def test_stocktwits_smoke_ticker_has_messages(ticker: str):
    p = ST_DIR / f"{ticker}.parquet"
    if not p.is_file():
        pytest.skip(f"StockTwits cache miss for {ticker}")
    df = pd.read_parquet(p)
    # Per DEC-599 ~30 messages/ticker target
    assert len(df) >= 5, (
        f"StockTwits {ticker} only has {len(df)} messages (expected ~30)"
    )
