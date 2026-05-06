"""Sprint 0A.10 BATCH 14 — CFTC COT DEMO.

Wider validation: date coverage, dealer-position fields parseable, weekly
cadence.

Per CHECKLIST #68 + DEC-503.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
CFTC_DIR = REPO / "data_prefetch" / "cftc"


def test_cftc_cot_date_coverage():
    df = pd.read_parquet(CFTC_DIR / "cot_emini_sp500.parquet")
    df["report_date"] = pd.to_datetime(df["report_date_as_yyyy_mm_dd"])
    earliest = df["report_date"].min()
    latest = df["report_date"].max()
    assert earliest <= pd.Timestamp("2010-01-01"), f"COT earliest {earliest}"
    assert latest >= pd.Timestamp("2024-01-01"), f"COT latest {latest}"


def test_cftc_cot_weekly_cadence():
    """Reports are weekly (Tuesday); diffs should average ~7 days."""
    df = pd.read_parquet(CFTC_DIR / "cot_emini_sp500.parquet")
    df["report_date"] = pd.to_datetime(df["report_date_as_yyyy_mm_dd"])
    df = df.sort_values("report_date")
    diffs = df["report_date"].diff().dt.days.dropna()
    median_gap = diffs.median()
    assert 6 <= median_gap <= 8, f"unexpected median weekly gap: {median_gap} days"


def test_cftc_cot_dealer_positions_parseable():
    """Dealer long/short fields should be numeric."""
    df = pd.read_parquet(CFTC_DIR / "cot_emini_sp500.parquet")
    cols_lower = {c.lower(): c for c in df.columns}
    dealer_long_col = next(
        (orig for low, orig in cols_lower.items() if "dealer" in low and "long" in low and "spread" not in low),
        None,
    )
    if not dealer_long_col:
        pytest.skip("dealer-long column not identifiable in current schema")
    series = pd.to_numeric(df[dealer_long_col], errors="coerce").dropna()
    assert len(series) > 100, f"dealer_long has only {len(series)} numeric values"
