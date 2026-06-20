"""B953 (2026-06-20): pyramid tests for Section 5 regime_affinity_lineage extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 5 + Council 57 UNANIMOUS
# 4/4 verdict per owner directive 2026-06-20 'Continue council this' +
# memory rule feedback_regime_selector_lineage_grep_before_delete (B663).
"""
from __future__ import annotations

import json

import pytest


def test_b953_section_05_extractor_importable():
    """B953 contract: section_05_regime_affinity_lineage module importable + functions callable."""
    from backtest.diagnostics import section_05_regime_affinity_lineage as mod
    assert hasattr(mod, "extract_section_05_for_strategy")
    assert hasattr(mod, "populate_section_05_for_dossier")
    assert hasattr(mod, "_parse_regime_selector_strategy_index")


def test_b953_regime_selector_parse_returns_strategies():
    """B953: AST parser returns dict mapping strategy names to regime entries."""
    from backtest.diagnostics.section_05_regime_affinity_lineage import (
        _parse_regime_selector_strategy_index,
    )
    index = _parse_regime_selector_strategy_index()
    if not index:
        pytest.skip("STRATEGY_REGIME_AFFINITY dict not found; cannot test")
    # Should have multiple strategies (regime_selector.py defines many)
    assert len(index) >= 20, f"Expected >=20 strategies in regime affinity; got {len(index)}"
    # Each entry has required fields
    for strat, entry in index.items():
        assert "regimes" in entry
        assert "line_no" in entry
        assert "leading_comments" in entry
        assert "batch_refs" in entry


def test_b953_known_strategy_has_explicit_entry():
    """B953: known strategy with explicit affinity returns has_explicit_entry=True."""
    from backtest.diagnostics.section_05_regime_affinity_lineage import (
        extract_section_05_for_strategy, _parse_regime_selector_strategy_index,
    )
    index = _parse_regime_selector_strategy_index()
    if not index:
        pytest.skip("No regime affinity entries")
    # Pick first strategy with explicit entry
    test_strategy = next(iter(index.keys()))
    result = extract_section_05_for_strategy(test_strategy)
    assert result["has_explicit_entry"] is True
    assert result["current_regimes"] is not None
    assert result["regime_selector_line_number"] is not None


def test_b953_unknown_strategy_returns_no_explicit_entry():
    """B953: strategy without explicit affinity entry returns has_explicit_entry=False."""
    from backtest.diagnostics.section_05_regime_affinity_lineage import extract_section_05_for_strategy
    result = extract_section_05_for_strategy("nonexistent_strategy_xyz_b953")
    assert result["has_explicit_entry"] is False
    assert result["current_regimes"] is None
    assert result["batch_refs"] == []


def test_b953_batch_refs_extracted_from_lineage_comments():
    """B953: strategy with batch references in lineage comments has batch_refs populated.

    Per memory rule (B263 lineage example): regime_selector.py has inline
    comment blocks referencing batches like 'Batch 252' / 'B418' / 'DEC-368'.
    """
    from backtest.diagnostics.section_05_regime_affinity_lineage import (
        extract_section_05_for_strategy, _parse_regime_selector_strategy_index,
    )
    index = _parse_regime_selector_strategy_index()
    if not index:
        pytest.skip("No regime affinity entries")
    # Find a strategy with batch_refs populated (any strategy with batch
    # mentioned in leading comment block)
    strat_with_refs = None
    for strat, entry in index.items():
        if entry["batch_refs"]:
            strat_with_refs = strat
            break
    if strat_with_refs is None:
        pytest.skip("No strategy has batch refs in lineage comments")
    result = extract_section_05_for_strategy(strat_with_refs)
    assert len(result["batch_refs"]) >= 1
    # batch_refs should match B### or S4-B### or DEC-### format
    for ref in result["batch_refs"]:
        assert ref.startswith(("B", "S4-B", "DEC-"))


def test_b953_schema_keys_complete():
    """B953: extract returns expected schema keys."""
    from backtest.diagnostics.section_05_regime_affinity_lineage import extract_section_05_for_strategy
    result = extract_section_05_for_strategy("some_strategy")
    expected_keys = {
        "current_regimes", "has_explicit_entry", "lineage_comment_block",
        "batch_refs", "regime_selector_line_number", "method", "source",
        "anti_iteration_mandate",
    }
    assert set(result.keys()) == expected_keys


def test_b953_populate_writes_to_dossier(tmp_path):
    """B953: populate_section_05_for_dossier writes section slot."""
    from backtest.diagnostics.section_05_regime_affinity_lineage import (
        populate_section_05_for_dossier, _parse_regime_selector_strategy_index,
    )
    index = _parse_regime_selector_strategy_index()
    if not index:
        pytest.skip("No regime affinity entries")
    test_strategy = next(iter(index.keys()))
    dossier_path = tmp_path / "dossier.json"
    dossier_path.write_text(json.dumps({"strategy": test_strategy, "sections": {}}))
    populate_section_05_for_dossier(test_strategy, dossier_path)
    with open(dossier_path) as f:
        updated = json.load(f)
    assert "section_05_regime_affinity_lineage" in updated["sections"]
    section = updated["sections"]["section_05_regime_affinity_lineage"]
    assert section["has_explicit_entry"] is True
    assert "feedback_regime_selector_lineage_grep_before_delete" in section["anti_iteration_mandate"]
