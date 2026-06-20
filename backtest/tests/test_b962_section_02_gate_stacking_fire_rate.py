"""B962 (2026-06-20): pyramid tests for Section 2 gate_stacking_fire_rate.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 2 + Council 67 verdict
# per owner directive 2026-06-20 'Continue council this. Continue without
# stopping till all sections in P1 are done.' per CHECKLIST #77.
"""
from __future__ import annotations

import json

import pytest


def test_b962_section_02_extractor_importable():
    """B962 contract: module importable + functions exposed."""
    from backtest.diagnostics import section_02_gate_stacking_fire_rate as mod
    assert hasattr(mod, "extract_section_02_for_strategy")
    assert hasattr(mod, "populate_section_02_for_dossier")
    assert hasattr(mod, "_load_b660_index")


def test_b962_b660_index_loads_and_has_strategies():
    """B962: B660 index loads from output_audit/ and has > 100 strategies."""
    from backtest.diagnostics.section_02_gate_stacking_fire_rate import _load_b660_index
    index = _load_b660_index()
    # B660 results list contains 222 entries per PRE-BUILD CHECK
    assert len(index) > 100, f"Expected >100 strategies in B660 index, got {len(index)}"


def test_b962_extract_measured_strategy_returns_gate_marginals():
    """B962: a strategy present in B660 returns populated gate_marginals."""
    from backtest.diagnostics.section_02_gate_stacking_fire_rate import (
        extract_section_02_for_strategy,
        _load_b660_index,
    )
    index = _load_b660_index()
    # Pick first strategy with non-empty gate_marginals
    test_strat = None
    for s, entry in index.items():
        if entry.get("gate_marginals"):
            test_strat = s
            break
    if test_strat is None:
        pytest.skip("No strategy with gate_marginals in B660")
    result = extract_section_02_for_strategy(test_strat)
    assert result["gate_marginals"] is not None
    assert result["n_gates_stacked"] > 0
    assert result["min_marginal_fire_rate"] is not None
    assert result["tightest_gate"] in result["gate_marginals"]
    assert result["gate_stacking_check"] in {"passed", "failed", "not_measured"}


def test_b962_extract_unmeasured_strategy_returns_not_measured():
    """B962: a strategy not in B660 returns gate_stacking_check='not_measured'."""
    from backtest.diagnostics.section_02_gate_stacking_fire_rate import extract_section_02_for_strategy
    result = extract_section_02_for_strategy("nonexistent_strategy_xyz_123")
    assert result["gate_stacking_check"] == "not_measured"
    assert result["gate_marginals"] is None
    assert result["n_gates_stacked"] is None


def test_b962_failed_strategy_below_30_per_year_floor():
    """B962: a strategy with measured_fires_per_year < 30 returns 'failed'."""
    from backtest.diagnostics.section_02_gate_stacking_fire_rate import (
        extract_section_02_for_strategy,
        _load_b660_index,
    )
    index = _load_b660_index()
    # Find a FAIL_FIRE_STARVED strategy (verdict in B660 already says this)
    test_strat = None
    for s, entry in index.items():
        verdict = entry.get("verdict", "")
        fires = entry.get("projected_fires_per_calendar_year_total_full_t1a", 0)
        if verdict == "FAIL_FIRE_STARVED" and fires is not None and fires < 30:
            test_strat = s
            break
    if test_strat is None:
        pytest.skip("No FAIL_FIRE_STARVED strategy with <30 fires/yr in B660")
    result = extract_section_02_for_strategy(test_strat)
    assert result["gate_stacking_check"] == "failed"
    assert result["b660_verdict"] == "FAIL_FIRE_STARVED"


def test_b962_passed_strategy_above_30_per_year_floor():
    """B962: a strategy with measured_fires_per_year >= 30 returns 'passed'."""
    from backtest.diagnostics.section_02_gate_stacking_fire_rate import (
        extract_section_02_for_strategy,
        _load_b660_index,
    )
    index = _load_b660_index()
    test_strat = None
    for s, entry in index.items():
        fires = entry.get("projected_fires_per_calendar_year_total_full_t1a", 0)
        if fires is not None and fires >= 30:
            test_strat = s
            break
    if test_strat is None:
        pytest.skip("No strategy with >=30 fires/yr in B660")
    result = extract_section_02_for_strategy(test_strat)
    assert result["gate_stacking_check"] == "passed"


def test_b962_schema_keys_complete():
    """B962: extract returns expected schema keys."""
    from backtest.diagnostics.section_02_gate_stacking_fire_rate import extract_section_02_for_strategy
    result = extract_section_02_for_strategy("any_strategy")
    expected_keys = {
        "n_gates_stacked", "gate_marginals", "min_marginal_fire_rate",
        "tightest_gate", "independence_predicted_joint_prob",
        "measured_fires_per_year_full_t1a", "b660_verdict",
        "gate_stacking_check", "method", "source", "limitation",
        "memory_rule_reference",
    }
    assert set(result.keys()) == expected_keys


def test_b962_populate_writes_to_dossier(tmp_path):
    """B962: populate_section_02_for_dossier writes section slot."""
    from backtest.diagnostics.section_02_gate_stacking_fire_rate import populate_section_02_for_dossier
    dossier_path = tmp_path / "dossier.json"
    dossier_path.write_text(json.dumps({"strategy": "any", "sections": {}}))
    populate_section_02_for_dossier("any", dossier_path)
    with open(dossier_path) as f:
        dossier = json.load(f)
    assert "section_02_gate_stacking_fire_rate" in dossier["sections"]


def test_b962_min_marginal_is_minimum_of_gates():
    """B962: min_marginal_fire_rate matches min of gate_marginals values."""
    from backtest.diagnostics.section_02_gate_stacking_fire_rate import (
        extract_section_02_for_strategy,
        _load_b660_index,
    )
    index = _load_b660_index()
    test_strat = None
    for s, entry in index.items():
        gms = entry.get("gate_marginals") or {}
        if len(gms) >= 2:
            test_strat = s
            break
    if test_strat is None:
        pytest.skip("No multi-gate strategy in B660")
    result = extract_section_02_for_strategy(test_strat)
    actual_min = min(result["gate_marginals"].values())
    assert abs(result["min_marginal_fire_rate"] - actual_min) < 1e-6


def test_b962_b660_universe_is_503_post_b648():
    """B962 contract: B660 universe is 503 (post-B648 hardcoded-220 bug fix)."""
    from backtest.diagnostics.section_02_gate_stacking_fire_rate import B660_PATH
    with open(B660_PATH) as f:
        data = json.load(f)
    # Post-B648 fix: n_tickers_full_t1a_pit_active should be ~503 not 220
    n_tickers = data.get("n_tickers_full_t1a_pit_active")
    assert n_tickers is not None, "n_tickers_full_t1a_pit_active key absent"
    assert n_tickers >= 500, (
        f"B660 universe={n_tickers} suggests pre-B648 hardcoded-220 bug. "
        f"Re-run measure_fire_count.py with --universe=full_t1a_pit."
    )
