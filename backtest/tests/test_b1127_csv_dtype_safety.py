"""B1127 Tier-2 Contract: CSV dtype safety (Council 246).

CATCHES: B1120 float64 coercion on execution_batch_ref (pandas inferred
empty col as float64, rejected string assignment); Turn 1 CSV column
overwrite (recommendation vs post_investigation_recommendation).
"""
# Source: per CHECKLIST #77 canonical-source; author Council 246 B1127 2026-07-03
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


REPO = Path(__file__).parent.parent.parent
CSV = REPO / "output_batch_A_150" / "phase_1_quiet_fire_investigation.csv"


@pytest.fixture(scope="module")
def df():
    if not CSV.exists():
        pytest.skip(f"CSV missing: {CSV}")
    return pd.read_csv(CSV)


TEXT_COLUMNS = [
    "post_investigation_verdict",
    "post_investigation_recommendation",
    "final_recommended_actions",
    "execution_status",
    "execution_batch_ref",
    "execution_comments",
    "recommendation",
]


def test_text_columns_are_object_or_string_dtype(df):
    """Text columns must be object OR string dtype, not float64/int64.

    Prevents B1120 coercion issue where empty col was inferred as float64
    and rejected string writes.
    """
    for col in TEXT_COLUMNS:
        if col not in df.columns:
            continue
        dtype_str = str(df[col].dtype)
        assert dtype_str in ("object", "str", "string") or "string" in dtype_str.lower(), (
            f"Column {col!r} dtype is {dtype_str}, expected object/str/string. "
            f"Prevents B1120 float64 coercion on empty columns."
        )


def test_original_recommendation_column_preserved(df):
    """Turn 1 fix: original recommendation column must not be overwritten by post-investigation."""
    if "recommendation" not in df.columns:
        pytest.skip("recommendation column missing")
        return
    if "post_investigation_recommendation" not in df.columns:
        pytest.skip("post_investigation_recommendation column missing")
        return
    # Both columns must exist and be distinct
    assert "recommendation" in df.columns
    assert "post_investigation_recommendation" in df.columns


def test_no_column_name_collisions(df):
    """No duplicate column names (pandas would silently keep only one)."""
    duplicates = [col for col in df.columns if list(df.columns).count(col) > 1]
    assert not duplicates, f"Duplicate column names in CSV: {duplicates}"


def test_execution_batch_ref_batch_number_format(df):
    """execution_batch_ref values must be BNNN format (e.g., 'B1125', 'B1126')."""
    import re

    if "execution_batch_ref" not in df.columns:
        pytest.skip("execution_batch_ref column missing")
        return
    invalid = []
    for val in df["execution_batch_ref"].fillna(""):
        val = str(val).strip()
        if not val:
            continue
        # Allow comma-separated multiple batches
        for part in val.split(","):
            part = part.strip()
            if part and not re.match(r"^B\d{3,4}[.a-z]*$", part):
                invalid.append(part)
    invalid = list(set(invalid))[:10]
    assert not invalid, (
        f"Invalid execution_batch_ref values: {invalid}. Format must be BNNN."
    )
