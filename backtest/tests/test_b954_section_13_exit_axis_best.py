"""B954 (2026-06-20): pyramid tests for Section 13 exit_axis_best extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 13 + Council 58 UNANIMOUS
# 4/4 verdict per owner directive 2026-06-20 'Continue council this autonomous'.
"""
from __future__ import annotations

import json

import pytest


def test_b954_section_13_extractor_importable():
    """B954 contract: section_13_exit_axis_best module importable + functions callable."""
    from backtest.diagnostics import section_13_exit_axis_best as mod
    assert hasattr(mod, "extract_section_13_for_strategy")
    assert hasattr(mod, "populate_section_13_for_dossier")
    assert hasattr(mod, "_load_r4_best_exit_index")


def test_b954_r4_best_exit_csv_loads():
    """B954: R4 exit_strategy_best.csv loads with >=50 strategies."""
    from backtest.diagnostics.section_13_exit_axis_best import _load_r4_best_exit_index
    index = _load_r4_best_exit_index()
    if not index:
        pytest.skip("R4 exit_strategy_best.csv not present")
    assert len(index) >= 50, f"Expected >=50 strategies in R4 best-exit index; got {len(index)}"


def test_b954_extract_in_r4_strategy_returns_metrics():
    """B954: strategy in R4 CSV returns populated metrics + in_r4_cube=True."""
    from backtest.diagnostics.section_13_exit_axis_best import (
        extract_section_13_for_strategy, _load_r4_best_exit_index,
    )
    index = _load_r4_best_exit_index()
    if not index:
        pytest.skip("R4 CSV not present")
    test_strategy = next(iter(index.keys()))
    result = extract_section_13_for_strategy(test_strategy)
    assert result["in_r4_cube"] is True
    assert result["best_exit_method"] is not None
    assert result["best_exit_total_pnl_pct"] is not None
    assert result["best_exit_n_trades"] is not None
    assert result["stage_5_swap_relevant"] is True


def test_b954_extract_unknown_strategy_returns_null():
    """B954: strategy not in R4 returns in_r4_cube=False + all metrics None."""
    from backtest.diagnostics.section_13_exit_axis_best import extract_section_13_for_strategy
    result = extract_section_13_for_strategy("nonexistent_strategy_xyz_b954")
    assert result["in_r4_cube"] is False
    assert result["best_exit_method"] is None
    assert result["best_exit_total_pnl_pct"] is None
    assert result["stage_5_swap_relevant"] is False


def test_b954_schema_keys_complete():
    """B954: extract returns expected schema keys."""
    from backtest.diagnostics.section_13_exit_axis_best import extract_section_13_for_strategy
    result = extract_section_13_for_strategy("some_strategy")
    expected_keys = {
        "best_exit_method", "best_exit_total_pnl_pct", "best_exit_n_trades",
        "best_exit_win_rate", "ranking_metric", "in_r4_cube", "source",
        "method", "limitation", "stage_5_swap_relevant",
    }
    assert set(result.keys()) == expected_keys


def test_b954_ranking_metric_documented():
    """B954: ranking_metric field documented as total_pnl_pct (NOT Sharpe per CLAUDE.md #10)."""
    from backtest.diagnostics.section_13_exit_axis_best import extract_section_13_for_strategy
    result = extract_section_13_for_strategy("any_strategy")
    assert result["ranking_metric"] == "total_pnl_pct"
    assert result["method"] == "r4_passthrough"


def test_b954_populate_writes_to_dossier(tmp_path):
    """B954: populate_section_13_for_dossier writes section slot."""
    from backtest.diagnostics.section_13_exit_axis_best import (
        populate_section_13_for_dossier, _load_r4_best_exit_index,
    )
    index = _load_r4_best_exit_index()
    if not index:
        pytest.skip("R4 CSV not present")
    test_strategy = next(iter(index.keys()))
    dossier_path = tmp_path / "dossier.json"
    dossier_path.write_text(json.dumps({"strategy": test_strategy, "sections": {}}))
    populate_section_13_for_dossier(test_strategy, dossier_path)
    with open(dossier_path) as f:
        updated = json.load(f)
    assert "section_13_exit_axis_best_26" in updated["sections"]
    section = updated["sections"]["section_13_exit_axis_best_26"]
    assert section["in_r4_cube"] is True
    assert section["method"] == "r4_passthrough"
