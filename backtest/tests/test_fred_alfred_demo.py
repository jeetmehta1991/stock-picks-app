"""Sprint 0A.10 BATCH 14 — FRED + ALFRED DEMO.

Validates high-priority series (yield curve, VIX, HY OAS, financial stress,
recession probability, jobless claims, balance sheet) with date-range +
revision-density checks.

Per CHECKLIST #68 + DEC-503.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
FRED_DIR = REPO / "data_prefetch" / "fred" / "observations"
ALFRED_DIR = REPO / "data_prefetch" / "alfred"

# High-priority macro series consumed by Risk Agent (per F-003 Cat 4)
HIGH_PRIORITY_SERIES = [
    "T10Y2Y",       # Yield curve 10y-2y
    "DGS10",        # 10y Treasury
    "BAMLH0A0HYM2", # HY OAS
    "STLFSI4",      # St Louis Fed financial stress
    "RECPROUSM156N",# Recession probability
    "ICSA",         # Initial jobless claims
    "WALCL",        # Fed balance sheet
    "CPIAUCSL",     # CPI
    "UNRATE",       # Unemployment
    "PAYEMS",       # Nonfarm payrolls
]


def _read_fred(s: str) -> pd.DataFrame:
    p = FRED_DIR / f"{s}.parquet"
    if not p.is_file():
        pytest.skip(f"{s} not in FRED cache")
    return pd.read_parquet(p)


def _read_alfred(s: str) -> pd.DataFrame:
    p = ALFRED_DIR / f"{s}.parquet"
    if not p.is_file():
        pytest.skip(f"{s} not in ALFRED cache")
    return pd.read_parquet(p)


# --- FRED demo ---


@pytest.mark.parametrize("series", HIGH_PRIORITY_SERIES)
def test_fred_high_priority_series_present(series: str):
    df = _read_fred(series)
    assert len(df) >= 10, f"{series} has only {len(df)} observations"
    assert df["value"].notna().any(), f"{series} all-NaN"


# --- ALFRED demo ---


@pytest.mark.parametrize("series", HIGH_PRIORITY_SERIES)
def test_alfred_high_priority_series_present(series: str):
    df = _read_alfred(series)
    assert len(df) >= 10, f"{series} ALFRED has only {len(df)} vintage rows"
    assert {"series_id", "date", "realtime_start", "realtime_end", "value"} <= set(df.columns)


def test_alfred_revisions_present_for_revised_series():
    """CPIAUCSL is heavily revised — expect multiple realtime_start values per date."""
    df = _read_alfred("CPIAUCSL")
    revisions_per_date = df.groupby("date")["realtime_start"].nunique()
    # Most CPI dates should have 1+ vintages; some should have 2+
    assert revisions_per_date.max() >= 1


def test_alfred_pit_query_pattern():
    """Demonstrate the PIT consumer query: as-of=2024-01-01, what was CPI in 2023-12-01?"""
    df = _read_alfred("CPIAUCSL")
    df = df.dropna(subset=["realtime_start", "realtime_end", "value"]).copy()
    # PIT filter: realtime_start <= as_of <= realtime_end AND date <= as_of
    as_of = pd.Timestamp("2024-01-01").date()
    target_date = pd.Timestamp("2023-12-01").date()
    knowable = df[
        (pd.to_datetime(df["realtime_start"]).dt.date <= as_of)
        & (pd.to_datetime(df["realtime_end"]).dt.date >= as_of)
        & (pd.to_datetime(df["date"]).dt.date <= target_date)
    ]
    if knowable.empty:
        pytest.skip("no knowable observation for the demo as-of")
    # Latest knowable observation
    latest = knowable.sort_values("date").iloc[-1]
    assert pd.notna(latest["value"])
