"""B959 (2026-06-20): pyramid tests for Section 4 redundancy_phi_matrix.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 4 + Council 64 UNANIMOUS
# Option (beta) verdict per owner directive 2026-06-20 per CHECKLIST #77.
"""
from __future__ import annotations

import json

import pytest


def test_b959_section_04_extractor_importable():
    """B959 contract: module importable + functions exposed."""
    from backtest.diagnostics import section_04_redundancy_phi_matrix as mod
    assert hasattr(mod, "extract_section_04_for_strategy")
    assert hasattr(mod, "populate_section_04_for_dossier")
    assert hasattr(mod, "_load_strategy_fire_sets")
    assert hasattr(mod, "_compute_pairwise_jaccard_matrix")
    assert hasattr(mod, "_jaccard")
    assert hasattr(mod, "write_shared_matrix_parquet")
    assert mod.TRACK_A_THRESHOLD == 0.70


def test_b959_jaccard_function_correct():
    """B959: _jaccard returns correct similarity for simple sets."""
    from backtest.diagnostics.section_04_redundancy_phi_matrix import _jaccard
    a = frozenset([(1, "2024-01-01"), (1, "2024-01-02"), (2, "2024-01-01")])
    b = frozenset([(1, "2024-01-01"), (2, "2024-01-01"), (3, "2024-01-01")])
    # intersection: {(1,"2024-01-01"), (2,"2024-01-01")} -> 2
    # union: {(1,"2024-01-01"), (1,"2024-01-02"), (2,"2024-01-01"), (3,"2024-01-01")} -> 4
    # jaccard = 2/4 = 0.5
    assert _jaccard(a, b) == 0.5


def test_b959_jaccard_empty_returns_zero():
    """B959: empty sets return 0.0."""
    from backtest.diagnostics.section_04_redundancy_phi_matrix import _jaccard
    assert _jaccard(frozenset(), frozenset([(1, "2024-01-01")])) == 0.0
    assert _jaccard(frozenset([(1, "2024-01-01")]), frozenset()) == 0.0
    assert _jaccard(frozenset(), frozenset()) == 0.0


def test_b959_jaccard_identical_returns_one():
    """B959: identical sets return 1.0."""
    from backtest.diagnostics.section_04_redundancy_phi_matrix import _jaccard
    s = frozenset([(1, "2024-01-01"), (2, "2024-02-01")])
    assert _jaccard(s, s) == 1.0


def test_b959_jaccard_disjoint_returns_zero():
    """B959: disjoint sets return 0.0."""
    from backtest.diagnostics.section_04_redundancy_phi_matrix import _jaccard
    a = frozenset([(1, "2024-01-01")])
    b = frozenset([(2, "2024-01-01")])
    assert _jaccard(a, b) == 0.0


def test_b959_r4_trade_detail_loads():
    """B959: R4 trade_exit_detail.csv loads per-strategy fire sets."""
    from backtest.diagnostics.section_04_redundancy_phi_matrix import _load_strategy_fire_sets
    sets = _load_strategy_fire_sets()
    if not sets:
        pytest.skip("R4 trade_exit_detail.csv not present")
    # Should have >=50 strategies from R4
    assert len(sets) >= 50, f"Expected >=50 strategies in R4 trade detail; got {len(sets)}"
    # Each value is a frozenset of tuples
    sample_strat = next(iter(sets.keys()))
    sample_set = sets[sample_strat]
    assert isinstance(sample_set, frozenset)


def test_b959_extract_in_r4_strategy_returns_neighbors():
    """B959: strategy in R4 returns top-5 neighbors + jaccard values."""
    from backtest.diagnostics.section_04_redundancy_phi_matrix import (
        extract_section_04_for_strategy, _load_strategy_fire_sets,
    )
    sets = _load_strategy_fire_sets()
    if not sets:
        pytest.skip("R4 not present")
    test_strategy = next(iter(sets.keys()))
    result = extract_section_04_for_strategy(test_strategy)
    assert result["method"] == "pairwise_trade_day_jaccard"
    assert result["n_fires_in_r4"] > 0
    assert result["threshold"] == 0.70
    # top_5_neighbors should be a list (may be empty if no overlaps)
    assert isinstance(result["top_5_neighbors"], list)
    assert len(result["top_5_neighbors"]) <= 5


def test_b959_extract_unknown_strategy_returns_not_in_r4():
    """B959: strategy not in R4 returns method='not_in_r4_cube'."""
    from backtest.diagnostics.section_04_redundancy_phi_matrix import extract_section_04_for_strategy
    result = extract_section_04_for_strategy("nonexistent_strategy_xyz_b959")
    assert result["method"] == "not_in_r4_cube"
    assert result["n_fires_in_r4"] == 0
    assert result["track_a_candidate"] is False
    assert result["top_5_neighbors"] == []


def test_b959_schema_keys_complete():
    """B959: extract returns expected schema keys."""
    from backtest.diagnostics.section_04_redundancy_phi_matrix import extract_section_04_for_strategy
    result = extract_section_04_for_strategy("any_strategy")
    expected_keys = {
        "n_fires_in_r4", "top_5_neighbors", "max_jaccard_neighbor",
        "max_jaccard_value", "track_a_candidate", "method", "source",
        "threshold", "memory_rule_reference",
    }
    assert set(result.keys()) == expected_keys


def test_b959_track_a_threshold_documented():
    """B959: track_a_candidate flagged when max_jaccard >= 0.70 (B709 PEAD precedent)."""
    from backtest.diagnostics.section_04_redundancy_phi_matrix import TRACK_A_THRESHOLD
    assert TRACK_A_THRESHOLD == 0.70


def test_b959_populate_writes_to_dossier(tmp_path):
    """B959: populate_section_04_for_dossier writes section slot."""
    from backtest.diagnostics.section_04_redundancy_phi_matrix import (
        populate_section_04_for_dossier, _load_strategy_fire_sets,
    )
    sets = _load_strategy_fire_sets()
    if not sets:
        pytest.skip("R4 not present")
    test_strategy = next(iter(sets.keys()))
    dossier_path = tmp_path / "dossier.json"
    dossier_path.write_text(json.dumps({"strategy": test_strategy, "sections": {}}))
    populate_section_04_for_dossier(test_strategy, dossier_path)
    with open(dossier_path) as f:
        updated = json.load(f)
    assert "section_04_redundancy_phi_matrix" in updated["sections"]
    section = updated["sections"]["section_04_redundancy_phi_matrix"]
    assert section["threshold"] == 0.70
    assert "feedback_no_prior_edge_consolidate_before_tune" in section["memory_rule_reference"]
