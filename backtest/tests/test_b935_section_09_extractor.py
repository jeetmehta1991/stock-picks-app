"""B935 (2026-06-19): pyramid tests for Section 9 TWO-TRACK R4 extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 + Council 45 owner-A TWO-TRACK
# design per owner directive 2026-06-19 Option A.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest


def test_b935_extract_section_09_in_r4_strategy_returns_track_1():
    """B935 TRACK 1: A strategy known to be in R4 cube returns track=1 with metrics."""
    from backtest.diagnostics.section_09_r4_cube_metrics import extract_section_09
    # donchian_10_breakout is in R4 per B934 self-test
    result = extract_section_09("donchian_10_breakout")
    assert result["track"] == 1, (
        f"R4-included strategy should return track=1; got {result['track']!r}. "
        f"r4_status: {result.get('r4_status')!r}"
    )
    assert result["r4_status"] == "in_r4_cube"
    assert result["added_after_r4"] is False
    assert result["metrics"] is not None, "Track 1 must populate metrics dict"
    # Basic metric fields present
    assert "sharpe_ratio" in result["metrics"]
    assert "total_trades" in result["metrics"]


def test_b935_extract_section_09_post_r4_strategy_returns_track_2():
    """B935 TRACK 2: A strategy added post-R4 returns track=2 with null metrics."""
    from backtest.diagnostics.section_09_r4_cube_metrics import extract_section_09
    # smc_breaker_block_long was added after R4 (B901 SMC fix landed POST-R4)
    result = extract_section_09("smc_breaker_block_long")
    assert result["track"] == 2, (
        f"Post-R4 strategy should return track=2; got {result['track']!r}. "
        f"r4_status: {result.get('r4_status')!r}"
    )
    assert result["r4_status"] == "post_r4_addition"
    assert result["added_after_r4"] is True
    assert result["metrics"] is None, "Track 2 must have null metrics"
    assert result["evidence_source"] == "section_9b", (
        "Track 2 must point to Section 9b for evidence"
    )
    assert result["r5_inclusion_criterion_hint"] == "pre_cube_evidence_sufficient_candidate"


def test_b935_extract_section_09_unknown_strategy_returns_track_2():
    """B935 unknown strategy: graceful handling - returns track=2 (post-R4) since not in R4 CSV."""
    from backtest.diagnostics.section_09_r4_cube_metrics import extract_section_09
    result = extract_section_09("_nonexistent_canary_test_strat_xyz123")
    assert result["track"] == 2  # not in R4 -> treated as post-R4 addition
    assert result["metrics"] is None


def test_b935_r4_metric_columns_canonical_set():
    """B935 invariant: R4_METRIC_COLUMNS includes all PASSING_CRITERIA fields."""
    from backtest.diagnostics.section_09_r4_cube_metrics import R4_METRIC_COLUMNS
    # Per CLAUDE.md passing criteria #1-14 + 3 AUTO-FAIL screens
    required = {
        "total_trades", "win_rate", "profit_factor", "expected_value",
        "win_loss_ratio", "max_drawdown_pct", "total_roi_pct",
        "sharpe_ratio", "sortino_ratio", "calmar_ratio", "deflated_sharpe",
        # Cost-sensitivity per DEC-612
        "sharpe_at_20bps",
        # Chow per DEC-613
        "chow_p_value", "has_structural_break",
        # ADF per DEC-614
        "adf_p_value", "is_stationary",
    }
    missing = required - set(R4_METRIC_COLUMNS)
    assert not missing, (
        f"R4_METRIC_COLUMNS missing canonical PASSING_CRITERIA fields: {missing}"
    )


def test_b935_populate_section_09_for_dossier_round_trip():
    """B935 populate-then-read: section_09 value persists in JSON correctly."""
    from scripts.dossier_build import init_dossier, DOSSIERS_DIR
    from backtest.diagnostics.section_09_r4_cube_metrics import (
        populate_section_09_for_dossier,
    )

    test_strategy = "_test_b935_populate_section9_canary"
    try:
        dossier_path = init_dossier(test_strategy, overwrite=True)
        populate_section_09_for_dossier(test_strategy, dossier_path)

        with open(dossier_path) as f:
            dossier = json.load(f)
        section_9 = dossier["sections"]["section_09_r4_cube_metrics"]
        assert section_9 is not None, "Section 9 not populated"
        assert "track" in section_9
        assert "r4_status" in section_9
        # Test strategy is post-R4 (canary name)
        assert section_9["track"] == 2
    finally:
        # Cleanup
        test_dir = DOSSIERS_DIR / test_strategy
        if test_dir.exists():
            for child in test_dir.iterdir():
                child.unlink()
            test_dir.rmdir()


def test_b935_r4_dataframe_loads_or_handles_missing():
    """B935: R4 CSV must load successfully OR extractor handles missing gracefully."""
    from backtest.diagnostics.section_09_r4_cube_metrics import (
        _load_r4_dataframe, R4_RESULTS_CSV,
    )
    df = _load_r4_dataframe()
    if R4_RESULTS_CSV.exists():
        assert not df.empty
        assert "strategy" in df.columns
        # R4 expected ~102 strategies per B934 self-test
        n_strategies = df["strategy"].nunique()
        assert 80 <= n_strategies <= 130, (
            f"R4 strategy count {n_strategies} outside expected 80-130 range. "
            f"If R4 was re-run, update bounds."
        )
    else:
        assert df.empty, "Missing CSV must produce empty DataFrame"
