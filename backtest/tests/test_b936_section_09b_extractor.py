"""B936 (2026-06-19): pyramid tests for Section 9b pre-cube evidence extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 9b (B934 Council 45) +
# Council 46 batch 2 commit 1 per owner directive 2026-06-19 Option A.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_b936_extract_section_09b_returns_schema():
    """B936 schema invariant: extract_section_09b returns canonical 5-field dict."""
    from backtest.diagnostics.section_09b_pre_cube_evidence import extract_section_09b
    result = extract_section_09b("smc_breaker_block_long")
    required_keys = {
        "fire_count_projection",
        "walk_batches",
        "status_tags",
        "attribution_narrative",
        "has_pre_cube_evidence",
    }
    assert required_keys.issubset(set(result.keys())), (
        f"Section 9b missing required keys: {required_keys - set(result.keys())}"
    )


def test_b936_smc_breaker_has_walk_batch_references():
    """B936: smc_breaker_block_long should have walk-batch references in docstring or evidence."""
    from backtest.diagnostics.section_09b_pre_cube_evidence import extract_section_09b
    result = extract_section_09b("smc_breaker_block_long")
    # Per Council 45 self-test: must have AT LEAST one evidence source
    assert result["has_pre_cube_evidence"], (
        f"smc_breaker_block_long must have pre-cube evidence; got: {result!r}"
    )


def test_b936_b906_measurement_disputed_strategy_has_status_tag():
    """B936: institutional_persistent_holders_long (B906 MEASUREMENT_DISPUTED) must surface that tag."""
    from backtest.diagnostics.section_09b_pre_cube_evidence import extract_section_09b
    result = extract_section_09b("institutional_persistent_holders_long")
    assert "MEASUREMENT_DISPUTED" in result["status_tags"], (
        f"institutional_persistent_holders_long must surface MEASUREMENT_DISPUTED tag; "
        f"got tags: {result['status_tags']!r}"
    )


def test_b936_disabled_strategy_has_status_tag():
    """B936: dxy_headwind_multinational_short (STRATEGIES_DISABLED_MISSING_PRODUCER) tag surfaces."""
    from backtest.diagnostics.section_09b_pre_cube_evidence import extract_section_09b
    result = extract_section_09b("dxy_headwind_multinational_short")
    assert "DISABLED_MISSING_PRODUCER" in result["status_tags"], (
        f"dxy_headwind_multinational_short must surface DISABLED_MISSING_PRODUCER; "
        f"got: {result['status_tags']!r}"
    )


def test_b936_unknown_strategy_returns_no_evidence():
    """B936: an unknown strategy should return has_pre_cube_evidence=False."""
    from backtest.diagnostics.section_09b_pre_cube_evidence import extract_section_09b
    result = extract_section_09b("_nonexistent_canary_strategy_xyz")
    assert result["has_pre_cube_evidence"] is False
    assert result["fire_count_projection"] is None
    assert result["walk_batches"] == []
    assert result["status_tags"] == []
    assert "NO pre-cube evidence" in result["attribution_narrative"]


def test_b936_populate_section_09b_round_trip():
    """B936 populate-then-read: section_20_pre_cube_evidence_9b persists in JSON."""
    from scripts.dossier_build import init_dossier, DOSSIERS_DIR
    from backtest.diagnostics.section_09b_pre_cube_evidence import (
        populate_section_09b_for_dossier,
    )

    test_strategy = "institutional_persistent_holders_long"
    try:
        dossier_path = init_dossier(test_strategy, overwrite=True)
        populate_section_09b_for_dossier(test_strategy, dossier_path)

        with open(dossier_path) as f:
            dossier = json.load(f)
        section_9b = dossier["sections"]["section_20_pre_cube_evidence_9b"]
        assert section_9b is not None, "Section 9b not populated"
        assert "MEASUREMENT_DISPUTED" in section_9b["status_tags"]
    finally:
        test_dir = DOSSIERS_DIR / test_strategy
        if test_dir.exists():
            for child in test_dir.iterdir():
                child.unlink()
            test_dir.rmdir()


def test_b936_council_45_assertion_3_all_post_r4_known_good_have_evidence():
    """B936 Council 45 Assertion 3 (load-bearing): all KNOWN_GOOD_STRATEGIES_POST_R4 have Section 9b evidence.

    This is the architectural-safety assertion: if post-R4 known-good
    strategies LACK pre-cube evidence, then `r5_inclusion_criterion =
    pre_cube_evidence_sufficient` cannot be set for them, and they get
    laundered into the R5 cube with no documented justification.
    """
    from scripts.dossier_self_test import KNOWN_GOOD_STRATEGIES_POST_R4
    from backtest.diagnostics.section_09b_pre_cube_evidence import extract_section_09b
    for strat in KNOWN_GOOD_STRATEGIES_POST_R4:
        result = extract_section_09b(strat)
        assert result["has_pre_cube_evidence"], (
            f"Council 45 Assertion 3 FAIL: {strat} lacks pre-cube evidence; "
            f"cannot set r5_inclusion_criterion=pre_cube_evidence_sufficient. "
            f"Add walk-batch markers OR config status tag OR fire-count projection. "
            f"Got Section 9b: {result!r}"
        )
