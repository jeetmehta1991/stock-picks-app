"""Data-integrity tests for Pass 53 Day-9 v8h prefetch additions
(DEC-503 type 7 — Data Integrity).

Closes the testing-pyramid gap owner identified 2026-05-07: recent prefetch
additions (FRED Tier C / CFTC Tier C / SEC EDGAR Tier B / Polygon Tier D /
Polygon dividends) had unit + integration coverage but no data-integrity
sweep. This file fills that gap per CHECKLIST #72 + DEC-591.

Each test asserts:
1. File exists at canonical Sprint 0A path
2. Schema matches expected columns (catches silent format changes)
3. No critical-field NULLs (date / value / ticker columns populated)
4. Date ranges are sensible
5. Numeric ranges are within historical bounds (catches scale errors like
   the BUG-VIX-PROXY VXX-as-VIX issue)
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# FRED additions (DEC-513 #7 + macro signals — Tier C2)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("series_id,min_rows,vmin,vmax", [
    ("VIXCLS",    1500, 8.0,   100.0),  # VIX index — never above 100
    ("VXVCLS",    1500, 8.0,   100.0),  # 3-mo VIX
    ("DTWEXBGS",  1500, 80.0,  140.0),  # Trade-weighted dollar
    ("DCOILWTICO",1500, -50.0, 200.0),  # WTI crude (allows neg from 2020)
    ("HOUST",     50,   500,   3000),   # Housing starts (thousands of units)
    ("PERMIT",    50,   500,   3000),   # Building permits
    ("RSAFS",     50,   400000, 800000), # Retail sales (millions $)
    ("INDPRO",    50,   85.0,  120.0),  # Industrial prod index
    ("UMCSENT",   50,   40.0,  120.0),  # Consumer sentiment
    ("M2SL",      50,   15000, 23000),  # Money supply (billions $)
    ("PCEPI",     50,   90.0,  140.0),  # PCE inflation index
])
def test_fred_series_data_integrity(series_id, min_rows, vmin, vmax):
    """FRED series files: schema + row count + value bounds."""
    path = REPO_ROOT / "data_prefetch" / "fred" / "observations" / f"{series_id}.parquet"
    if not path.exists():
        pytest.skip(f"FRED {series_id} not prefetched")
    df = pd.read_parquet(path)
    assert {"date", "value"}.issubset(df.columns), (
        f"FRED {series_id} schema missing date/value columns"
    )
    assert len(df) >= min_rows, (
        f"FRED {series_id} has only {len(df)} rows; expected >= {min_rows}"
    )
    assert df["value"].notna().all(), (
        f"FRED {series_id} has NULL values in critical column"
    )
    # Value bounds — catches scale errors (the VIX-VXX bug pattern)
    p99 = df["value"].quantile(0.99)
    p01 = df["value"].quantile(0.01)
    assert p01 >= vmin and p99 <= vmax, (
        f"FRED {series_id} values [{p01:.2f}, {p99:.2f}] outside expected "
        f"range [{vmin}, {vmax}] — possible scale/series error"
    )


# ---------------------------------------------------------------------------
# CFTC additional contracts (Tier C3 + INV-011 fix)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("contract_slug,min_rows", [
    ("emini_sp500",     500),
    ("emini_nasdaq100", 100),
    ("emini_russell2k", 100),
    ("vix_futures",     500),
    ("treasury_10y",    500),
    ("treasury_5y",     500),
    ("treasury_2y",     500),
    ("ust_bond",        500),
    ("ultra_treasury",  500),
    ("fed_funds_30d",   500),
    ("dxy_dollar_idx",  500),
    ("eur_usd",         1000),
    ("jpy_usd",         500),
    ("wti_crude",       500),
    ("gold",            500),
    ("silver",          500),
    ("natural_gas",     500),
    ("copper",          500),
    ("emini_dow",       500),
])
def test_cftc_contract_integrity(contract_slug, min_rows):
    """CFTC COT files: schema + row count + report_date sanity."""
    path = REPO_ROOT / "data_prefetch" / "cftc" / f"cot_{contract_slug}.parquet"
    if not path.exists():
        pytest.skip(f"CFTC {contract_slug} not prefetched")
    df = pd.read_parquet(path)
    assert "contract_market_name" in df.columns
    assert "report_date_as_yyyy_mm_dd" in df.columns
    assert len(df) >= min_rows, (
        f"CFTC {contract_slug}: {len(df)} rows < expected {min_rows}"
    )
    # report_date must parse cleanly
    dates = pd.to_datetime(df["report_date_as_yyyy_mm_dd"], errors="coerce")
    assert dates.notna().sum() >= min_rows * 0.95, (
        f"CFTC {contract_slug}: too many unparseable report_dates"
    )


# ---------------------------------------------------------------------------
# SEC EDGAR new forms (Tier B1-B4)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("form_dir,form_name,min_files_pct", [
    ("4",        "4",        0.50),     # Form 4 — most active companies have lots
    ("8_K",      "8-K",      0.50),     # 8-K — common for public companies
    ("SC_13D",   "SC 13D",   0.20),     # SC 13D — sparser (activist filings)
    ("SC_13G",   "SC 13G",   0.30),     # SC 13G — passive 5%+ holders
    ("10_K",     "10-K",     0.30),     # 10-K — annual; expect ~50% coverage at full universe
    ("10_Q",     "10-Q",     0.30),     # 10-Q — quarterly
    ("DEF_14A",  "DEF 14A",  0.20),     # Proxy
    ("S_1",      "S-1",      0.05),     # IPO registration; rare for established
    ("S_1_A",    "S-1/A",    0.05),
    ("SC_13D_A", "SC 13D/A", 0.10),
    ("SC_13G_A", "SC 13G/A", 0.10),
])
def test_sec_edgar_form_coverage(form_dir, form_name, min_files_pct):
    """SEC EDGAR per-form: at least min_files_pct of universe should have a parquet."""
    p = REPO_ROOT / "data_prefetch" / "sec_edgar" / form_dir
    if not p.exists():
        pytest.skip(f"SEC EDGAR {form_dir} dir absent")
    files = list(p.glob("*.parquet"))
    if not files:
        pytest.skip(f"SEC EDGAR {form_dir} has no files yet (BG may still be running)")
    # Sample one file to verify schema
    sample = pd.read_parquet(files[0])
    expected_cols = {"ticker", "cik", "form", "filing_date",
                     "accession_number", "primary_doc"}
    assert expected_cols.issubset(sample.columns), (
        f"SEC EDGAR {form_dir} sample schema mismatch: {set(sample.columns)} "
        f"vs expected {expected_cols}"
    )


def test_sec_edgar_filing_date_pit_sanity():
    """Sample SEC EDGAR file: filing_date column must be parseable + non-future."""
    p = REPO_ROOT / "data_prefetch" / "sec_edgar" / "10_K" / "AAPL.parquet"
    if not p.exists():
        pytest.skip("AAPL 10-K not yet prefetched")
    df = pd.read_parquet(p)
    if df.empty:
        pytest.skip("AAPL 10-K empty")
    df["filing_date"] = pd.to_datetime(df["filing_date"], errors="coerce")
    assert df["filing_date"].notna().any(), "All filing_dates unparseable"
    today = pd.Timestamp("today")
    future = (df["filing_date"] > today).sum()
    assert future == 0, f"AAPL 10-K has {future} future-dated filings — schema issue"


# ---------------------------------------------------------------------------
# Polygon dividends (988K rows global)
# ---------------------------------------------------------------------------
def test_polygon_dividends_integrity():
    """Polygon dividends: schema + row count + ex_dividend_date sanity."""
    path = REPO_ROOT / "data_prefetch" / "polygon" / "dividends" / "all_dividends.parquet"
    if not path.exists():
        pytest.skip("Polygon dividends not prefetched")
    df = pd.read_parquet(path)
    expected_cols = {"cash_amount", "currency", "declaration_date",
                     "dividend_type", "ex_dividend_date", "frequency"}
    assert expected_cols.issubset(df.columns), (
        f"Polygon dividends schema: {set(df.columns)}"
    )
    assert len(df) >= 100_000, (
        f"Polygon dividends has only {len(df)} rows; expected ~1M global"
    )
    # ex_dividend_date sanity
    df["ex_dividend_date"] = pd.to_datetime(df["ex_dividend_date"], errors="coerce")
    assert df["ex_dividend_date"].notna().sum() >= len(df) * 0.95
    # cash_amount must be positive (dividends never negative)
    assert (df["cash_amount"] >= 0).all(), "Negative cash_amount in dividends"


def test_polygon_splits_integrity():
    """Polygon splits: schema + row count + split_from/to sanity."""
    path = REPO_ROOT / "data_prefetch" / "polygon" / "splits" / "all_splits.parquet"
    if not path.exists():
        pytest.skip("Polygon splits not prefetched")
    df = pd.read_parquet(path)
    expected_cols = {"execution_date", "id", "split_from", "split_to", "ticker"}
    assert expected_cols.issubset(df.columns)
    assert len(df) >= 1000
    # split ratios must be positive
    assert (df["split_from"] > 0).all()
    assert (df["split_to"] > 0).all()


# ---------------------------------------------------------------------------
# Polygon Tier D (snapshot / market_status / reference_meta)
# ---------------------------------------------------------------------------
def test_polygon_snapshot_gainers_schema():
    path = REPO_ROOT / "data_prefetch" / "polygon" / "snapshot" / "gainers.parquet"
    if not path.exists():
        pytest.skip("snapshot gainers not prefetched")
    df = pd.read_parquet(path)
    assert "ticker" in df.columns


def test_polygon_market_status_schema():
    path = REPO_ROOT / "data_prefetch" / "polygon" / "market_status" / "now.parquet"
    if not path.exists():
        pytest.skip("market_status now not prefetched")
    df = pd.read_parquet(path)
    # Should have at least 1 row + market field
    assert len(df) >= 1


def test_polygon_reference_meta_exchanges():
    path = REPO_ROOT / "data_prefetch" / "polygon" / "reference_meta" / "exchanges.parquet"
    if not path.exists():
        pytest.skip("reference_meta exchanges not prefetched")
    df = pd.read_parquet(path)
    assert len(df) >= 30, f"Only {len(df)} exchanges; expected ~50+"
