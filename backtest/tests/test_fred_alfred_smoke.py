"""Sprint 0A.10 BATCH 14 — FRED + ALFRED SMOKE.

Validates the 50-series FRED prefetch and the matching ALFRED vintage
prefetch (PIT corrections per DEC-301).

Per CHECKLIST #68 + DEC-503.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
FRED_DIR = REPO / "data_prefetch" / "fred" / "observations"
ALFRED_DIR = REPO / "data_prefetch" / "alfred"


def _first_parquet(d: Path) -> Path:
    files = sorted(d.glob("*.parquet"))
    if not files:
        pytest.skip(f"no parquet files in {d}")
    return files[0]


# --- FRED ---


def test_fred_50_series_cached():
    files = list(FRED_DIR.glob("*.parquet"))
    assert len(files) >= 45, f"expected ~50 FRED series, got {len(files)}"


def test_fred_smoke_schema():
    df = pd.read_parquet(_first_parquet(FRED_DIR))
    assert {"date", "value"} <= set(df.columns)
    assert len(df) > 0


# --- ALFRED ---


def test_alfred_50_series_cached():
    files = list(ALFRED_DIR.glob("*.parquet"))
    assert len(files) >= 45, f"expected ~50 ALFRED vintage files, got {len(files)}"


def test_alfred_smoke_schema():
    df = pd.read_parquet(_first_parquet(ALFRED_DIR))
    assert {"series_id", "date", "realtime_start", "realtime_end", "value"} <= set(df.columns)
    assert len(df) > 0


def test_alfred_vintages_have_realtime_ranges():
    """ALFRED rows must carry realtime_start <= realtime_end (PIT semantics)."""
    df = pd.read_parquet(_first_parquet(ALFRED_DIR))
    sample = df.dropna(subset=["realtime_start", "realtime_end"]).head(10)
    if sample.empty:
        pytest.skip("no realtime ranges in sample")
    assert (sample["realtime_start"] <= sample["realtime_end"]).all()
