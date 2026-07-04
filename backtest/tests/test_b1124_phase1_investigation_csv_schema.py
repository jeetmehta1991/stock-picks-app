"""B1124 Test 8/10: phase_1_quiet_fire_investigation.csv schema pin (Council 244).

Per L183 lesson (B1118): any new column added to shared CSV must be paired
with a schema pin test. This test asserts all 23 columns are present +
required columns are fully populated.

Locks the CSV structure so downstream analysis scripts fail-loud on rename.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


REPO = Path(__file__).parent.parent.parent
CSV_PATH = REPO / "output_batch_A_150" / "phase_1_quiet_fire_investigation.csv"


REQUIRED_COLUMNS = [
    "strategy_name",
    "direction",
    "category",
    "n_fires",
    "class",
    "fired_regimes",
    "regime_affinity",
    "disabled_flag",
    "exploratory_flag",
    "producer_signals",
    "root_cause_hypothesis",
    "notes",
    "cluster_id",
    "owner_review_notes",
    "recommendation",
    "priority",
    "exploratory_loose_variant",
    "post_investigation_verdict",
    "post_investigation_recommendation",
    "final_recommended_actions",
    "execution_status",
    "execution_batch_ref",
    "execution_comments",
]

FULLY_POPULATED_COLUMNS = {
    "strategy_name",
    "n_fires",
    "recommendation",
    "priority",
    "post_investigation_verdict",
    "post_investigation_recommendation",
    "final_recommended_actions",
    "execution_status",
    "execution_comments",
}

EXPECTED_ROW_COUNT = 192


@pytest.fixture(scope="module")
def csv_df():
    if not CSV_PATH.exists():
        pytest.skip(f"CSV missing: {CSV_PATH}")
    return pd.read_csv(CSV_PATH)


def test_csv_has_expected_row_count(csv_df):
    """192 registered quiet-fire strategies; drift = silent add/drop."""
    assert len(csv_df) == EXPECTED_ROW_COUNT, (
        f"Expected {EXPECTED_ROW_COUNT} rows; got {len(csv_df)}"
    )


def test_all_required_columns_present(csv_df):
    """All 23 columns from B1117-B1121 must be present."""
    missing = [c for c in REQUIRED_COLUMNS if c not in csv_df.columns]
    assert not missing, f"Missing columns: {missing}"


def test_no_extra_unexpected_columns(csv_df):
    """Column set should match REQUIRED_COLUMNS exactly (no silent additions)."""
    extra = [c for c in csv_df.columns if c not in REQUIRED_COLUMNS]
    assert not extra, (
        f"Unexpected extra columns: {extra}. If genuine addition, "
        f"add to REQUIRED_COLUMNS in this test."
    )


def test_fully_populated_columns_have_no_empty_rows(csv_df):
    """Certain columns must be populated for every strategy (no silent gaps)."""
    for col in FULLY_POPULATED_COLUMNS:
        if col not in csv_df.columns:
            continue
        empty_count = csv_df[col].fillna("").astype(str).str.len().eq(0).sum()
        assert empty_count == 0, (
            f"Column {col!r} has {empty_count} empty rows; "
            f"must be fully populated (no silent gaps)"
        )


def test_investigation_coverage_100_percent(csv_df):
    """Council 243 milestone: 100% investigation coverage."""
    populated = csv_df["post_investigation_verdict"].fillna("").str.len() > 0
    coverage_pct = 100 * populated.sum() / len(csv_df)
    assert coverage_pct == 100.0, (
        f"Investigation coverage regressed to {coverage_pct:.1f}%; must be 100%"
    )


def test_execution_status_values_bounded(csv_df):
    """execution_status values must be from bounded set."""
    valid_status_prefixes = (
        "PENDING", "IN_PROGRESS_B", "DONE_B", "SKIPPED_", "BLOCKED_", "SUPERSEDED_B",
        "SKIP_",  # B1145 autonomous executor SKIP prefixes
        "FAIL_",  # B1145 pyramid failure prefixes
    )
    for val in csv_df["execution_status"].fillna("").unique():
        if not val:
            continue
        assert any(val.startswith(prefix) for prefix in valid_status_prefixes), (
            f"execution_status value {val!r} not in bounded set: {valid_status_prefixes}"
        )
