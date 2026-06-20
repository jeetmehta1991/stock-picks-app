"""B942 (2026-06-20): pyramid tests for Stream E full-roster validation script.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.2 + Council 48 batch 4 commit 1
# per owner directive 2026-06-20 Option A.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_b942_populate_all_dossiers_script_imports():
    """B942 contract: populate_all_dossiers.py must be importable + main() callable."""
    from scripts import populate_all_dossiers
    assert hasattr(populate_all_dossiers, "main")


def test_b942_dossiers_dir_exists_post_init_all():
    """B942: after --init-all, output_audit/dossiers/ must exist with subdirs."""
    from scripts.dossier_build import DOSSIERS_DIR
    assert DOSSIERS_DIR.exists(), f"{DOSSIERS_DIR} not initialized via dossier_build --init-all"


def test_b942_sample_dossier_has_three_populated_sections():
    """B942 spot check: a sample dossier has section_06 + section_09 + section_20 populated.

    Validates Stream E population script succeeded for at least the spot-check.
    """
    from scripts.dossier_build import DOSSIERS_DIR
    # Pick a strategy known to be in current roster
    sample_dossier = DOSSIERS_DIR / "donchian_10_breakout" / "dossier.json"
    if not sample_dossier.exists():
        pytest.skip("Sample dossier not populated; run scripts/populate_all_dossiers.py first")
    with open(sample_dossier) as f:
        dossier = json.load(f)
    sections = dossier["sections"]
    assert sections.get("section_06_producer_state_event") is not None, (
        "Section 6 missing from sample dossier post-B942 population"
    )
    assert sections.get("section_09_r4_cube_metrics") is not None, (
        "Section 9 missing from sample dossier post-B942 population"
    )
    assert sections.get("section_20_pre_cube_evidence_9b") is not None, (
        "Section 9b (slot 20) missing from sample dossier post-B942 population"
    )
