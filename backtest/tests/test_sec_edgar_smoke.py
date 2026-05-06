"""Sprint 0A.10 BATCH 14 — SEC EDGAR SMOKE.

Validates Form 4 / 8-K / SC 13D / SC 13G prefetch (4 form types per DEC-484).
6,056 files expected total across the 4 subfolders.

Per CHECKLIST #68 + DEC-503.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
EDGAR_DIR = REPO / "data_prefetch" / "sec_edgar"
FORM_4 = EDGAR_DIR / "4"
FORM_8K = EDGAR_DIR / "8_K"
SC_13D = EDGAR_DIR / "SC_13D"
SC_13G = EDGAR_DIR / "SC_13G"


def test_sec_edgar_form_4_cached():
    files = list(FORM_4.glob("*.parquet"))
    assert len(files) >= 1000, f"Form 4: only {len(files)} cached"


def test_sec_edgar_8k_cached():
    files = list(FORM_8K.glob("*.parquet"))
    assert len(files) >= 1000, f"8-K: only {len(files)} cached"


def test_sec_edgar_sc_13d_cached():
    files = list(SC_13D.glob("*.parquet"))
    assert len(files) >= 500, f"SC 13D: only {len(files)} cached"


def test_sec_edgar_sc_13g_cached():
    files = list(SC_13G.glob("*.parquet"))
    assert len(files) >= 500, f"SC 13G: only {len(files)} cached"


def test_sec_edgar_smoke_schema_form_4():
    p = next(FORM_4.glob("*.parquet"))
    df = pd.read_parquet(p)
    assert {"ticker", "cik", "form", "filing_date", "accession_number"} <= set(df.columns)
    assert (df["form"] == "4").all() or (df["form"].astype(str).str.upper() == "4").all()


def test_sec_edgar_smoke_schema_8k():
    p = next(FORM_8K.glob("*.parquet"))
    df = pd.read_parquet(p)
    assert {"ticker", "form", "filing_date"} <= set(df.columns)


def test_sec_edgar_total_file_count():
    """Aggregate across 4 form types: ~6,056 files expected."""
    total = sum(len(list(d.glob("*.parquet"))) for d in [FORM_4, FORM_8K, SC_13D, SC_13G])
    assert total >= 5000, f"SEC EDGAR total only {total} files (expected ~6,056)"
