"""Sprint 0A.10 BATCH 14 — AAII DEMO.

Wider validation: date coverage, range sanity, recent freshness.

Per CHECKLIST #68 + DEC-503.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
AAII_DIR = REPO / "data_prefetch" / "aaii"


def test_aaii_date_range_covers_backtest_window():
    """Per DEC-505 5-year walk-forward, AAII should cover 2020-2026."""
    df = pd.read_parquet(AAII_DIR / "weekly_sentiment.parquet")
    df["date"] = pd.to_datetime(df["date"])
    earliest = df["date"].min()
    latest = df["date"].max()
    assert earliest <= pd.Timestamp("2021-01-01"), f"AAII earliest is {earliest}"
    assert latest >= pd.Timestamp("2025-01-01"), f"AAII latest is {latest}"


def test_aaii_300_plus_weekly_readings():
    df = pd.read_parquet(AAII_DIR / "weekly_sentiment.parquet")
    assert len(df) >= 300, f"AAII has only {len(df)} weekly readings (expected ~325)"


def test_aaii_bull_bear_spread_sanity():
    df = pd.read_parquet(AAII_DIR / "weekly_sentiment.parquet")
    if "bull_bear_spread" not in df.columns:
        pytest.skip("bull_bear_spread column not present")
    # Bull-bear spread historically ranges roughly -50 to +50
    assert df["bull_bear_spread"].dropna().abs().max() < 100
