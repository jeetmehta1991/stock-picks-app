"""B1127 Tier-4 Empirical: Investigation coverage audit (Council 246).

CATCHES: Turn 3 SMC count mismatch (14 said in doc, only 10 populated in
CSV); silent misses uncovered by Council 238 audit.
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


def test_coverage_claim_matches_actual(df):
    """Council 243 milestone: 100% coverage. Actual populated count must match."""
    populated = df["post_investigation_verdict"].fillna("").str.len() > 0
    total = len(df)
    coverage_pct = 100 * populated.sum() / total
    assert coverage_pct == 100.0, (
        f"Coverage claim {coverage_pct:.1f}% != 100%; populated={populated.sum()}, total={total}"
    )


def test_execution_comments_populated_for_all_investigations(df):
    """Every investigated strategy must have execution_comments."""
    comments_present = df["execution_comments"].fillna("").str.len() > 0
    assert comments_present.sum() == len(df), (
        f"execution_comments missing on {(~comments_present).sum()} rows"
    )


def test_family_verdict_siblings_consistent(df):
    """When siblings share a producer family, no isolated verdict on 1 of N."""
    triangle = df[df["strategy_name"].str.contains("triangle", case=False, na=False)]
    if len(triangle) >= 2:
        verdicts = triangle["post_investigation_verdict"].fillna("").str.len() > 0
        assert verdicts.all(), (
            f"Triangle family: {verdicts.sum()}/{len(triangle)} investigated. "
            f"Family verdicts must cover all siblings."
        )


def test_no_silent_bulk_status_drift(df):
    """execution_status values bounded (regression check)."""
    statuses = df["execution_status"].fillna("PENDING").unique()
    valid_prefixes = ("PENDING", "IN_PROGRESS_B", "DONE_B", "SKIPPED_", "BLOCKED_", "SUPERSEDED_B")
    for status in statuses:
        assert any(status.startswith(p) for p in valid_prefixes), (
            f"Invalid execution_status: {status!r}"
        )
