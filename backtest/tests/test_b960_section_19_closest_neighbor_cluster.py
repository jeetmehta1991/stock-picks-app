"""B960 (2026-06-20): pyramid tests for Section 19 closest_neighbor_cluster extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 19 + Council 65 UNANIMOUS
# 4/4 verdict per owner directive 2026-06-20 'Council this. Approve your rec. Continue.'
"""
from __future__ import annotations

import json

import pytest


def test_b960_section_19_extractor_importable():
    """B960 contract: section_19 module importable + functions callable."""
    from backtest.diagnostics import section_19_closest_neighbor_cluster as mod
    assert hasattr(mod, "extract_section_19_for_strategy")
    assert hasattr(mod, "populate_section_19_for_dossier")
    assert hasattr(mod, "_load_family_cluster_index")
    assert hasattr(mod, "_load_signal_jaccard_matrix")
    assert hasattr(mod, "_load_regime_affinity_index")


def test_b960_family_cluster_index_loads_from_ledger():
    """B960: family_cluster_id index loads from walk_verdict_ledger_v2.json."""
    from backtest.diagnostics.section_19_closest_neighbor_cluster import (
        _load_family_cluster_index,
    )
    index = _load_family_cluster_index()
    if not index:
        pytest.skip("walk_verdict_ledger_v2.json absent or empty")
    # B948 ledger has 125 entries with cluster_id like BR-1, CC-2
    assert len(index) >= 50, f"Expected >=50 strategies with cluster_id; got {len(index)}"
    # Sample cluster_id format: <PREFIX>-<N> where PREFIX is alpha
    sample = next(iter(index.values()))
    assert "-" in sample or sample.isalnum(), f"cluster_id format unexpected: {sample}"


def test_b960_signal_jaccard_matrix_symmetric_and_bounded():
    """B960: signal-overlap Jaccard matrix is symmetric and values in [0,1]."""
    from backtest.diagnostics.section_19_closest_neighbor_cluster import (
        _load_signal_jaccard_matrix,
    )
    matrix = _load_signal_jaccard_matrix()
    if not matrix:
        pytest.skip("Signal Jaccard matrix unavailable (Section 1 helper empty)")
    # Pick a strategy with neighbors
    strat_with_neighbors = None
    for s, neighbors in matrix.items():
        if neighbors:
            strat_with_neighbors = s
            break
    if strat_with_neighbors is None:
        pytest.skip("No strategy has signal-overlap neighbors")
    # Check symmetry + bounds for first 3 neighbors
    for peer, (j, shared) in list(matrix[strat_with_neighbors].items())[:3]:
        assert 0.0 < j <= 1.0, f"Jaccard out of bounds: {j}"
        assert shared >= 1, f"shared_signals must be >=1 when jaccard>0; got {shared}"
        # Symmetric
        back = matrix.get(peer, {}).get(strat_with_neighbors)
        assert back is not None, f"Matrix not symmetric for {strat_with_neighbors}<->{peer}"
        assert back[0] == j, "Symmetric Jaccard values must match"


def test_b960_extract_returns_complete_schema():
    """B960: extract returns expected schema keys regardless of strategy."""
    from backtest.diagnostics.section_19_closest_neighbor_cluster import (
        extract_section_19_for_strategy,
    )
    result = extract_section_19_for_strategy("nonexistent_strategy_xyz_b960")
    expected_keys = {
        "family_cluster_id",
        "cluster_prefix",
        "signal_overlap_neighbors",
        "regime_bias_neighbors",
        "closest_passing_neighbor",
        "closest_neighbor_composite_score",
        "sharpe_signature_axis_status",
        "method",
        "source",
        "limitation",
        "memory_rule_reference",
    }
    assert set(result.keys()) == expected_keys
    # Honest pre-R5 framing
    assert "NULL_PRE_R5" in result["sharpe_signature_axis_status"]
    assert result["method"] == "static_3_axis_pre_r5"


def test_b960_known_strategy_in_ledger_returns_family_cluster_id():
    """B960: a strategy known to walk_verdict_ledger_v2 returns its cluster_id."""
    from backtest.diagnostics.section_19_closest_neighbor_cluster import (
        _load_family_cluster_index, extract_section_19_for_strategy,
    )
    index = _load_family_cluster_index()
    if not index:
        pytest.skip("Ledger empty")
    strat = next(iter(index.keys()))
    result = extract_section_19_for_strategy(strat)
    assert result["family_cluster_id"] == index[strat]


def test_b960_neighbors_capped_at_top_k():
    """B960: signal + regime neighbor lists capped at TOP_K=3."""
    from backtest.diagnostics.section_19_closest_neighbor_cluster import (
        TOP_K, _load_family_cluster_index, extract_section_19_for_strategy,
    )
    index = _load_family_cluster_index()
    if not index:
        pytest.skip("Ledger empty")
    strat = next(iter(index.keys()))
    result = extract_section_19_for_strategy(strat)
    assert len(result["signal_overlap_neighbors"]) <= TOP_K
    assert len(result["regime_bias_neighbors"]) <= TOP_K


def test_b960_closest_passing_neighbor_is_same_family():
    """B960: composite closest_passing_neighbor must be in same family_cluster_id."""
    from backtest.diagnostics.section_19_closest_neighbor_cluster import (
        _load_family_cluster_index, extract_section_19_for_strategy,
    )
    index = _load_family_cluster_index()
    if not index:
        pytest.skip("Ledger empty")
    # Find a cluster with >=2 members (so a same-family peer can be picked)
    from collections import Counter
    cluster_counts = Counter(index.values())
    multi_clusters = [cid for cid, n in cluster_counts.items() if n >= 2]
    if not multi_clusters:
        pytest.skip("No multi-member clusters")
    target_cid = multi_clusters[0]
    target_strat = next(s for s, cid in index.items() if cid == target_cid)
    result = extract_section_19_for_strategy(target_strat)
    if result["closest_passing_neighbor"] is None:
        # All same-family peers had zero composite (no signal/regime overlap).
        # Honest NULL is acceptable - skip the family-match assertion.
        pytest.skip("All same-family peers had zero composite score")
    assert result["family_cluster_id"] == target_cid
    assert index.get(result["closest_passing_neighbor"]) == target_cid


def test_b960_composite_score_in_valid_range():
    """B960: composite_score when non-None is bounded [0,1] (weighted Jaccard)."""
    from backtest.diagnostics.section_19_closest_neighbor_cluster import (
        _load_family_cluster_index, extract_section_19_for_strategy,
    )
    index = _load_family_cluster_index()
    if not index:
        pytest.skip("Ledger empty")
    for strat in list(index.keys())[:20]:
        result = extract_section_19_for_strategy(strat)
        score = result["closest_neighbor_composite_score"]
        if score is not None:
            assert 0.0 <= score <= 1.0, f"Composite score out of bounds for {strat}: {score}"


def test_b960_regime_overlap_disjoint_returns_zero():
    """B960: _regime_overlap with disjoint regime sets returns ('disjoint', 0.0)."""
    from backtest.diagnostics.section_19_closest_neighbor_cluster import _regime_overlap
    label, pct = _regime_overlap(frozenset({"bull"}), frozenset({"bear", "crisis"}))
    assert label == "disjoint"
    assert pct == 0.0


def test_b960_regime_overlap_identical_returns_one():
    """B960: _regime_overlap with identical regime sets returns ('identical', 1.0)."""
    from backtest.diagnostics.section_19_closest_neighbor_cluster import _regime_overlap
    label, pct = _regime_overlap(frozenset({"bull", "neutral"}), frozenset({"bull", "neutral"}))
    assert label == "identical"
    assert pct == 1.0


def test_b960_populate_writes_to_dossier(tmp_path):
    """B960: populate_section_19_for_dossier writes section slot."""
    from backtest.diagnostics.section_19_closest_neighbor_cluster import (
        _load_family_cluster_index, populate_section_19_for_dossier,
    )
    index = _load_family_cluster_index()
    if not index:
        pytest.skip("Ledger empty")
    test_strategy = next(iter(index.keys()))
    dossier_path = tmp_path / "dossier.json"
    dossier_path.write_text(json.dumps({"strategy": test_strategy, "sections": {}}))
    populate_section_19_for_dossier(test_strategy, dossier_path)
    with open(dossier_path) as f:
        updated = json.load(f)
    assert "section_19_closest_neighbor_cluster" in updated["sections"]
    section = updated["sections"]["section_19_closest_neighbor_cluster"]
    assert section["family_cluster_id"] == index[test_strategy]
    assert "NULL_PRE_R5" in section["sharpe_signature_axis_status"]


def test_b960_cluster_prefix_coarsens_family_cluster_id():
    """B960: cluster_prefix strips trailing -N for P4 stratification fallback.

    B948 ledger has 128 unique cluster_ids across 130 mappings (near-singleton);
    coarsening BR-1, BR-2, ... -> BR enables meaningful P4 sampling categories.
    """
    from backtest.diagnostics.section_19_closest_neighbor_cluster import (
        _load_family_cluster_index, extract_section_19_for_strategy,
    )
    index = _load_family_cluster_index()
    if not index:
        pytest.skip("Ledger empty")
    # Find a strategy with hyphenated cluster_id (BR-1 / CC-2 / etc.)
    hyphenated = next(
        (s for s, cid in index.items() if "-" in cid),
        None,
    )
    if hyphenated is None:
        pytest.skip("No hyphenated cluster_id in ledger")
    result = extract_section_19_for_strategy(hyphenated)
    assert result["cluster_prefix"] is not None
    assert result["cluster_prefix"] == index[hyphenated].split("-")[0]
    # Prefix is shorter than full cluster_id
    assert len(result["cluster_prefix"]) < len(result["family_cluster_id"])


def test_b960_path_load_bearing_for_p4_documented():
    """B960: extractor docstring documents PATH-load-bearing-for-P4 framing per Council 65."""
    from backtest.diagnostics import section_19_closest_neighbor_cluster as mod
    doc = mod.__doc__ or ""
    assert "P4" in doc, "Docstring must reference P4 stratification dependency"
    assert "PATH-load-bearing" in doc or "PATH Section13" in doc, "Docstring must cite PATH source"
