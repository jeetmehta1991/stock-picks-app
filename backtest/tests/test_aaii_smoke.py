"""Sprint 0A.10 BATCH 14 — AAII SMOKE.

Validates the AAII weekly bull/bear/neutral sentiment prefetch.

Per CHECKLIST #68 + DEC-503.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
AAII_DIR = REPO / "data_prefetch" / "aaii"


def test_aaii_cache_exists():
    p = AAII_DIR / "weekly_sentiment.parquet"
    assert p.is_file(), "AAII weekly_sentiment.parquet not cached"


def test_aaii_smoke_schema():
    df = pd.read_parquet(AAII_DIR / "weekly_sentiment.parquet")
    assert {"date", "bullish", "neutral", "bearish"} <= set(df.columns)
    assert len(df) >= 100, f"AAII only has {len(df)} weekly readings"


def test_aaii_percentages_sum_to_one():
    """Bull + neutral + bear should be ~1.0 (or ~100% in pp form)."""
    df = pd.read_parquet(AAII_DIR / "weekly_sentiment.parquet")
    sample = df.head(10)
    totals = sample["bullish"] + sample["neutral"] + sample["bearish"]
    # Tolerate either fraction (≈1.0) or percent (≈100) form
    assert (
        ((totals - 1.0).abs() < 0.05).all()
        or ((totals - 100.0).abs() < 5.0).all()
    ), f"bull+neutral+bear doesn't sum sensibly: {totals.tolist()}"
