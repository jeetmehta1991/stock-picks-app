"""Sprint 0A.7 (Pass 53 v8h+1 2026-05-10) - StockTwits DEMO.

Wider validation: ticker-level coverage, sentiment distribution, recency.

Per CHECKLIST #68 + DEC-503 + DEC-599.
"""
from __future__ import annotations

import random
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
ST_DIR = REPO / "data_prefetch" / "stocktwits"


def test_stocktwits_full_universe_coverage():
    """Per DEC-599 BG complete: 1937/1937 underlyings cached."""
    files = list(ST_DIR.glob("*.parquet"))
    assert len(files) >= 1900, (
        f"StockTwits coverage drift: {len(files)} files; expected ~1937"
    )


def test_stocktwits_random_sample_schema_consistent():
    """Walk a random sample of 20 tickers; assert schema parity."""
    files = list(ST_DIR.glob("*.parquet"))
    if len(files) < 20:
        pytest.skip(f"Insufficient cache size for sampling: {len(files)}")
    rng = random.Random(2026)
    sample = rng.sample(files, 20)
    expected = {"id", "body", "created_at", "sentiment", "user_id",
                "user_username", "likes_total", "conversation_count"}
    drifted = []
    for p in sample:
        try:
            df = pd.read_parquet(p)
        except Exception as exc:
            drifted.append(f"{p.stem}: read failure {exc}")
            continue
        missing = expected - set(df.columns)
        if missing:
            drifted.append(f"{p.stem}: missing {missing}")
    assert not drifted, "Schema drift in random sample:\n" + "\n".join(drifted)


def test_stocktwits_sentiment_categorical_values():
    """sentiment column should contain Bullish / Bearish / None values."""
    p = ST_DIR / "AAPL.parquet"
    if not p.is_file():
        pytest.skip("AAPL StockTwits cache missing")
    df = pd.read_parquet(p)
    if "sentiment" not in df.columns:
        pytest.skip("sentiment column not present")
    distinct = set(df["sentiment"].dropna().unique())
    # Allowable values from the StockTwits API
    allowed = {"Bullish", "Bearish"}
    unexpected = distinct - allowed
    assert not unexpected, f"AAPL sentiment has unexpected values: {unexpected}"


def test_stocktwits_created_at_datetime():
    """created_at should be parseable as datetime."""
    p = ST_DIR / "AAPL.parquet"
    if not p.is_file():
        pytest.skip("AAPL StockTwits cache missing")
    df = pd.read_parquet(p)
    # Either already datetime or convertible
    try:
        dt = pd.to_datetime(df["created_at"])
        assert dt.notna().all()
    except Exception as exc:
        pytest.fail(f"AAPL.created_at not parseable as datetime: {exc}")
