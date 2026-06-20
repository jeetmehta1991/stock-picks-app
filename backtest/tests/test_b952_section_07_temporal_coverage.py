"""B952 (2026-06-20): pyramid tests for Section 7 temporal_coverage_probe extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 7 + Council 56 UNANIMOUS
# 4/4 verdict per owner directive 2026-06-20 'Continue council this'.
"""
from __future__ import annotations

import json

import pytest


def test_b952_section_07_extractor_importable():
    """B952 contract: section_07_temporal_coverage module importable + functions callable."""
    from backtest.diagnostics import section_07_temporal_coverage as mod
    assert hasattr(mod, "extract_section_07_for_strategy")
    assert hasattr(mod, "populate_section_07_for_dossier")
    assert hasattr(mod, "_load_b660_index")
    assert mod.MIN_TRADES_FLOOR == 30


def test_b952_b660_index_loads():
    """B952: B660 fire-count JSON loads as strategy-indexed dict with >=200 entries."""
    from backtest.diagnostics.section_07_temporal_coverage import _load_b660_index
    index = _load_b660_index()
    if not index:
        pytest.skip("B660 JSON not present; cannot test")
    assert len(index) >= 200, f"Expected >=200 strategies in B660 index; got {len(index)}"


def test_b952_extract_for_known_b660_strategy_returns_schema():
    """B952: extract for canonical strategy returns dict with expected schema keys."""
    from backtest.diagnostics.section_07_temporal_coverage import (
        extract_section_07_for_strategy, _load_b660_index,
    )
    index = _load_b660_index()
    if not index:
        pytest.skip("B660 JSON not present")
    test_strategy = next(iter(index.keys()))
    result = extract_section_07_for_strategy(test_strategy)
    expected_keys = {
        "verdict", "n_fires_long_total", "n_fires_short_total", "n_fires_avoid_total",
        "fires_per_year_long", "fires_per_year_short", "fires_per_year_total",
        "calendar_year_span", "first_fire_date", "last_fire_date",
        "min_trades_floor", "passes_min_trades_floor_long",
        "passes_min_trades_floor_short", "passes_min_trades_floor_either",
        "source", "method", "limitation",
    }
    assert set(result.keys()) == expected_keys
    assert result["method"] == "static_from_b660_measured_json"
    assert result["min_trades_floor"] == 30


def test_b952_extract_for_unknown_strategy_returns_unknown_verdict():
    """B952: strategy not in B660 returns verdict=UNKNOWN with all metrics None."""
    from backtest.diagnostics.section_07_temporal_coverage import extract_section_07_for_strategy
    result = extract_section_07_for_strategy("nonexistent_strategy_xyz_b952")
    assert result["verdict"] == "UNKNOWN"
    assert result["n_fires_long_total"] is None
    assert result["fires_per_year_long"] is None
    assert result["passes_min_trades_floor_long"] is False
    assert result["passes_min_trades_floor_either"] is False


def test_b952_fail_fire_starved_detection():
    """B952: B660-FAIL_FIRE_STARVED rows correctly fail min_trades_floor check.

    Find any B660 strategy with verdict=FAIL_FIRE_STARVED and confirm
    passes_min_trades_floor_either is False.
    """
    from backtest.diagnostics.section_07_temporal_coverage import (
        extract_section_07_for_strategy, _load_b660_index,
    )
    index = _load_b660_index()
    if not index:
        pytest.skip("B660 JSON not present")
    fail_starved_strat = None
    for strat, row in index.items():
        if row.get("projected_verdict_full_t1a") == "FAIL_FIRE_STARVED":
            fail_starved_strat = strat
            break
    if fail_starved_strat is None:
        pytest.skip("No FAIL_FIRE_STARVED strategy in B660")
    result = extract_section_07_for_strategy(fail_starved_strat)
    assert result["verdict"] == "FAIL_FIRE_STARVED"
    assert result["passes_min_trades_floor_either"] is False


def test_b952_pass_cube_detection():
    """B952: B660-PASS_CUBE rows have fires_per_year >= 30 floor."""
    from backtest.diagnostics.section_07_temporal_coverage import (
        extract_section_07_for_strategy, _load_b660_index,
    )
    index = _load_b660_index()
    if not index:
        pytest.skip("B660 JSON not present")
    pass_strat = None
    for strat, row in index.items():
        if row.get("projected_verdict_full_t1a") == "PASS_CUBE":
            pass_strat = strat
            break
    if pass_strat is None:
        pytest.skip("No PASS_CUBE strategy in B660")
    result = extract_section_07_for_strategy(pass_strat)
    assert result["verdict"] == "PASS_CUBE"
    assert result["passes_min_trades_floor_either"] is True


def test_b952_populate_writes_to_dossier(tmp_path):
    """B952: populate_section_07_for_dossier writes section slot."""
    from backtest.diagnostics.section_07_temporal_coverage import populate_section_07_for_dossier
    from backtest.diagnostics.section_07_temporal_coverage import _load_b660_index
    index = _load_b660_index()
    if not index:
        pytest.skip("B660 JSON not present")
    test_strategy = next(iter(index.keys()))
    dossier_path = tmp_path / "dossier.json"
    dossier_path.write_text(json.dumps({"strategy": test_strategy, "sections": {}}))
    populate_section_07_for_dossier(test_strategy, dossier_path)
    with open(dossier_path) as f:
        updated = json.load(f)
    assert "section_07_temporal_coverage_probe" in updated["sections"]
    section = updated["sections"]["section_07_temporal_coverage_probe"]
    assert section["min_trades_floor"] == 30
    assert section["method"] == "static_from_b660_measured_json"
