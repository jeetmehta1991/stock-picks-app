"""B1127 Tier-4 Empirical: Family sibling behavior diff (Council 246).

CATCHES: L184 SMC_PHASE over-scoping (family verdict extrapolated to
all siblings when 2 siblings contradicted the hypothesis with n=89,81
fires).

For each family-inheritance verdict, verify at least one sibling that
CONTRADICTS the family pattern is documented + verdict scope tightened.
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


def test_smc_family_has_contradicting_healthy_siblings(df):
    """L184 finding: smc_breaker_block_short (89f) + smc_inverse_fvg (81f) contradict SMC_PHASE latent-kill.

    If ALL SMC strategies fire 0-15, family latent-kill hypothesis stands.
    If any fire >30, hypothesis is falsified.
    """
    smc = df[df["strategy_name"].str.startswith("smc_")]
    healthy = smc[smc["n_fires"] > 30]
    assert len(healthy) >= 1, (
        f"L184 regression: SMC family expected at least 1 healthy-fire "
        f"sibling to keep SMC_PHASE hypothesis DEFENSIVE not PRIMARY. "
        f"Got {len(healthy)} healthy siblings from {len(smc)} SMC strategies."
    )


def test_triangle_family_all_or_none_reclassified(df):
    """Triangle family: all 3 members reclassified together (B1126 fix)."""
    triangle = df[df["strategy_name"].str.contains("triangle_", case=False, na=False)]
    if len(triangle) >= 3:
        done = triangle[triangle["execution_status"].str.startswith("DONE_", na=False)]
        blocked = triangle[triangle["execution_status"].str.startswith("BLOCKED_", na=False)]
        assert len(done) == 3 or len(blocked) == 3 or (len(done) == 0 and len(blocked) == 0), (
            f"Triangle family split state: done={len(done)}, blocked={len(blocked)} "
            f"of {len(triangle)}. Family should transition together."
        )


def test_calendar_family_reclassification_consistent(df):
    """Calendar B723 family (halloween, totm, pre_holiday): all-or-none reclassification."""
    calendar = df[
        df["strategy_name"].isin(["halloween_seasonal_long", "totm_long", "pre_holiday_long"])
    ]
    if len(calendar) == 3:
        blocked = calendar[calendar["execution_status"].str.startswith("BLOCKED_", na=False)]
        assert len(blocked) == 0 or len(blocked) == 3, (
            f"Calendar family split state: {len(blocked)}/3 blocked. "
            f"Family reclassification must be consistent."
        )


def test_index_rebalance_family_all_blocked(df):
    """Index rebalance family: all 4 must remain BLOCKED_DATA_MISSING until Sprint 5."""
    idx = df[
        df["strategy_name"].isin(
            [
                "post_deletion_drift_short",
                "post_inclusion_drift_long",
                "post_inclusion_reversal_short",
                "pre_rebalance_long",
            ]
        )
    ]
    if len(idx) >= 4:
        blocked = idx[idx["execution_status"] == "BLOCKED_DATA_MISSING"]
        assert len(blocked) == 4, (
            f"Index rebalance family: {len(blocked)}/4 BLOCKED_DATA_MISSING. "
            f"All 4 must remain blocked until Sprint 5 DEC-380 parquet lands."
        )
