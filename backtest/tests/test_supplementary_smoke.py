"""Sprint 0A.10 BATCH 14 — Free supplementary sources SMOKE.

Validates Apewisdom, Wikipedia pageviews, and pytrends prefetch. pytrends
may be partial (rate-limited per Pass 53 Batch 12-b).

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


# --- Apewisdom ---


def test_apewisdom_cache_exists():
    p = APEWISDOM_DIR / "global.parquet"
    assert p.is_file(), "Apewisdom global.parquet not cached"


def test_apewisdom_smoke_schema():
    df = pd.read_parquet(APEWISDOM_DIR / "global.parquet")
    assert {"ticker", "mentions", "rank"} <= set(df.columns)
    assert len(df) > 0


# --- Wikipedia pageviews ---


def test_wikipedia_per_ticker_populated():
    files = list(WIKIPEDIA_DIR.glob("*.parquet"))
    assert len(files) >= 1000, f"Wikipedia only {len(files)} ticker files"


def test_wikipedia_smoke_schema():
    files = sorted(WIKIPEDIA_DIR.glob("*.parquet"))
    if not files:
        pytest.skip("Wikipedia empty")
    df = pd.read_parquet(files[0])
    assert {"date", "views"} <= set(df.columns)
    assert (df["views"] >= 0).all()


# --- pytrends (may be partial — rate-limited) ---


def test_pytrends_cache_present():
    files = list(PYTRENDS_DIR.glob("*.parquet"))
    # Partial OK; just assert non-empty so we know prefetch ran
    assert len(files) >= 50, f"pytrends only {len(files)} files (expected partial 500+)"


def test_pytrends_smoke_schema():
    files = sorted(PYTRENDS_DIR.glob("*.parquet"))
    if not files:
        pytest.skip("pytrends empty")
    df = pd.read_parquet(files[0])
    assert {"ticker", "date", "search_volume_index"} <= set(df.columns)
    if not df.empty:
        sample = df["search_volume_index"].dropna().head(10)
        # search-volume index is 0-100
        assert (sample >= 0).all() and (sample <= 100).all()
