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
    """B942 spot check: at least one dossier has section_06 + section_09 + section_20 populated.

    B947 (2026-06-20) fix: changed from specific 'donchian_10_breakout' fixture
    to ANY-dossier-search because round-trip tests in test_b935/test_b944 use
    init_dossier(overwrite=True) on specific strategies + don't repopulate
    section 6 (they only populate the sections being tested).

    Validates Stream E population script succeeded for AT LEAST one dossier.
    """
    from scripts.dossier_build import DOSSIERS_DIR
    if not DOSSIERS_DIR.exists():
        pytest.skip("Dossiers directory not populated; run scripts/populate_all_dossiers.py first")
    found_complete = False
    for d in DOSSIERS_DIR.iterdir():
        if not d.is_dir():
            continue
        f = d / "dossier.json"
        if not f.exists():
            continue
        with open(f) as fh:
            dossier = json.load(fh)
        sections = dossier.get("sections", {})
        if (
            sections.get("section_06_producer_state_event") is not None
            and sections.get("section_09_r4_cube_metrics") is not None
            and sections.get("section_20_pre_cube_evidence_9b") is not None
        ):
            found_complete = True
            break
    assert found_complete, (
        "No dossier has all three sections (6, 9, 9b) populated. "
        "Run scripts/populate_all_dossiers.py to restore state."
    )
