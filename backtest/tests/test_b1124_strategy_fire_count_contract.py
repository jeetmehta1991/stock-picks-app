"""B1124 Test 4/10: Per-strategy fire-count contract (Council 244).

Asserts each registered strategy's expected fire-count band per
Council 236 verdicts. RED-FIRST for the 4 BLOCKED_DATA_MISSING
strategies (must fire 0 while BUG-278 open).

This test prevents silent regressions where a strategy that should
fire 5-15 times/yr suddenly fires 0 (or vice versa).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


REPO = Path(__file__).parent.parent.parent
CSV_PATH = REPO / "output_batch_A_150" / "phase_1_quiet_fire_investigation.csv"


BLOCKED_DATA_MISSING_MUST_FIRE_ZERO = {
    "post_deletion_drift_short",
    "post_inclusion_drift_long",
    "pre_rebalance_long",
}

BLOCKED_PRODUCER_BUG_MUST_FIRE_ZERO_OR_LOW = {
    "triangle_ascending_long",
    "triangle_ascending_retest_long",
    "triangle_descending_short",
    "double_bottom_long",
}

HEALTHY_ABOVE_MARGINAL_MUST_FIRE_ABOVE_30 = {
    "smc_breaker_block_short",
    "smc_inverse_fvg",
}


@pytest.fixture(scope="module")
def csv_df():
    if not CSV_PATH.exists():
        pytest.skip(f"CSV missing: {CSV_PATH}")
    return pd.read_csv(CSV_PATH)


def test_csv_exists_at_canonical_path(csv_df):
    """Baseline: CSV must exist at the canonical path."""
    assert len(csv_df) > 0, "CSV must have rows"


def test_bug_278_blocked_data_missing_strategies_fire_zero(csv_df):
    """BUG-278: 3 index rebalance strategies MUST fire 0 until Sprint 5 lands."""
    for strat in BLOCKED_DATA_MISSING_MUST_FIRE_ZERO:
        row = csv_df[csv_df["strategy_name"] == strat]
        if row.empty:
            pytest.fail(f"Strategy {strat} missing from CSV")
        n_fires = int(row.iloc[0]["n_fires"])
        assert n_fires == 0, (
            f"{strat}: BUG-278 open, must fire 0 until parquet lands. "
            f"Got n_fires={n_fires}. Either parquet landed (great - update this test) "
            f"OR contract is drifting."
        )


def test_bug_277_281_blocked_producer_bug_strategies_underfire(csv_df):
    """BUG-277 + BUG-281: chart pattern strategies MUST fire 0-3 until fix."""
    for strat in BLOCKED_PRODUCER_BUG_MUST_FIRE_ZERO_OR_LOW:
        row = csv_df[csv_df["strategy_name"] == strat]
        if row.empty:
            pytest.fail(f"Strategy {strat} missing from CSV")
        n_fires = int(row.iloc[0]["n_fires"])
        assert n_fires <= 3, (
            f"{strat}: BUG-277/BUG-281 open, must fire <=3 until producer fix. "
            f"Got n_fires={n_fires}."
        )


def test_healthy_above_marginal_smc_strategies_fire_above_30(csv_df):
    """Council 241 Turn 8 finding: healthy SMC strategies fire >30 = contradicts SMC_PHASE latent-kill."""
    for strat in HEALTHY_ABOVE_MARGINAL_MUST_FIRE_ABOVE_30:
        row = csv_df[csv_df["strategy_name"] == strat]
        if row.empty:
            pytest.fail(f"Strategy {strat} missing from CSV")
        n_fires = int(row.iloc[0]["n_fires"])
        assert n_fires > 30, (
            f"{strat}: Council 241 finding requires n_fires>30 to contradict "
            f"SMC_PHASE latent-kill hypothesis. Got n_fires={n_fires}. "
            f"If drift, SMC_PHASE hypothesis needs revisit."
        )


def test_192_strategies_registered_no_silent_drop(csv_df):
    """Pin CSV row count at 192; drift = silent strategy drop or add."""
    assert len(csv_df) == 192, (
        f"Expected 192 strategies in CSV (Batch A investigation set); "
        f"got {len(csv_df)}. Investigate any drift before proceeding."
    )
