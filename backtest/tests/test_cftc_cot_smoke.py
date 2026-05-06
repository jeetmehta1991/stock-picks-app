"""Sprint 0A.10 BATCH 14 — CFTC COT SMOKE.

Validates the CFTC E-mini S&P 500 Traders in Financial Futures (TFF) report
prefetch. 1,293 weekly reports expected.

Per CHECKLIST #68 + DEC-503.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
CFTC_DIR = REPO / "data_prefetch" / "cftc"


def test_cftc_cot_cache_exists():
    p = CFTC_DIR / "cot_emini_sp500.parquet"
    assert p.is_file(), "CFTC COT E-mini SP500 parquet not cached"


def test_cftc_cot_weekly_count():
    df = pd.read_parquet(CFTC_DIR / "cot_emini_sp500.parquet")
    assert len(df) >= 1000, f"expected ≥1000 weekly TFF reports, got {len(df)}"


def test_cftc_cot_smoke_schema():
    df = pd.read_parquet(CFTC_DIR / "cot_emini_sp500.parquet")
    assert "report_date_as_yyyy_mm_dd" in df.columns
    # Wide schema (~88 columns); spot-check key fields exist
    cols_lower = {c.lower() for c in df.columns}
    has_dealer = any("dealer" in c for c in cols_lower)
    has_position = any("position" in c or "long" in c or "short" in c for c in cols_lower)
    assert has_dealer and has_position, "TFF report should have dealer + position columns"
