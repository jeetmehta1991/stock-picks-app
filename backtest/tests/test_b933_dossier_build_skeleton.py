"""B933 (2026-06-19): pyramid tests for dossier_build.py skeleton + JSON schema.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.2 + Council 44 batch 1 commit 1
# per owner directive 2026-06-19 Option A autonomous proceed.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent.parent


def test_b933_dossier_sections_count():
    """B933+B934 schema invariant: exactly 20 dossier sections.

    PATH 13.3 baseline = 19; B934 Council 45 (owner-approved) added
    Section 9b (pre_cube_evidence) addressing R4=102 vs roster=219 drift.
    Total: 20 sections numbered 1..20.
    """
    from scripts.dossier_build import DOSSIER_SECTIONS
    assert len(DOSSIER_SECTIONS) == 20, (
        f"DOSSIER_SECTIONS must have exactly 20 entries (PATH 13.3 + B934 Council 45); "
        f"got {len(DOSSIER_SECTIONS)}"
    )
    # IDs must be 1..20 contiguous
    ids = sorted(s[0] for s in DOSSIER_SECTIONS)
    assert ids == list(range(1, 21)), f"Section IDs must be 1..20; got {ids}"


def test_b933_dossier_section_keys_unique():
    """B933 schema invariant: section keys must be unique."""
    from scripts.dossier_build import DOSSIER_SECTIONS
    keys = [s[1] for s in DOSSIER_SECTIONS]
    assert len(keys) == len(set(keys)), (
        f"Section keys must be unique; duplicates: "
        f"{[k for k in keys if keys.count(k) > 1]}"
    )


def test_b933_b934_empty_dossier_has_20_null_sections():
    """B933+B934 init contract: empty dossier has 20 sections (all null)
    + r5_inclusion_criterion field.

    B934 Council 45 (owner-approved): added Section 9b + r5_inclusion_criterion.
    """
    from scripts.dossier_build import _empty_dossier_schema, R5_INCLUSION_CRITERIA
    schema = _empty_dossier_schema("test_strategy")
    assert "sections" in schema
    assert len(schema["sections"]) == 20, (
        f"Empty dossier must have 20 section slots (PATH 13.3 + B934 9b); "
        f"got {len(schema['sections'])}"
    )
    nulls = [k for k, v in schema["sections"].items() if v is None]
    assert len(nulls) == 20, (
        f"All 20 sections must initialize to None; got {20 - len(nulls)} populated"
    )
    # B934 Council 45 r5_inclusion_criterion field
    assert "r5_inclusion_criterion" in schema, (
        "B934 schema must include r5_inclusion_criterion field per Council 45"
    )
    assert schema["r5_inclusion_criterion"] is None, (
        "r5_inclusion_criterion initializes None (set after Sections 9 + 9b populated)"
    )
    # Validate enum values
    assert R5_INCLUSION_CRITERIA == (
        "r4_metrics_passed", "pre_cube_evidence_sufficient", "deferred"
    )


def test_b933_evidence_hash_deterministic():
    """B933 content-addressed hash: same inputs -> same hash."""
    from scripts.dossier_build import _compute_evidence_hash
    h1 = _compute_evidence_hash("strat_x", "section_09", date(2024, 6, 30), "abc123")
    h2 = _compute_evidence_hash("strat_x", "section_09", date(2024, 6, 30), "abc123")
    assert h1 == h2, "Same inputs must produce same hash"
    # Different strategy -> different hash
    h3 = _compute_evidence_hash("strat_y", "section_09", date(2024, 6, 30), "abc123")
    assert h1 != h3, "Different strategy must produce different hash"
    # Hash truncated to 16 chars
    assert len(h1) == 16


def test_b933_init_dossier_creates_json():
    """B933 init_dossier: creates JSON file with 19-section schema."""
    import tempfile
    from scripts.dossier_build import init_dossier, DOSSIERS_DIR
    # Use real DOSSIERS_DIR to test schema; cleanup test file
    test_strategy = "_test_b933_init_dossier_canary"
    try:
        path = init_dossier(test_strategy, overwrite=True)
        assert path.exists()
        with open(path) as f:
            data = json.load(f)
        assert data["strategy"] == test_strategy
        # B934 Council 45 architecture: batch tag updated to current builder version
        assert data["dossier_build_batch"] in ("B933", "B934"), (
            f"Expected B933 or B934 builder; got {data['dossier_build_batch']!r}"
        )
        assert data["phase"] == "P1"
        # B934 Council 45: 20 sections (B933 baseline 19 + Section 9b)
        assert len(data["sections"]) == 20, (
            f"Expected 20 sections post-B934; got {len(data['sections'])}"
        )
        assert all(v is None for v in data["sections"].values())
    finally:
        # Cleanup canary dossier
        test_dir = DOSSIERS_DIR / test_strategy
        if test_dir.exists():
            for child in test_dir.iterdir():
                child.unlink()
            test_dir.rmdir()


def test_b933_evidence_store_manifest_init():
    """B933 evidence_store: manifest.json initialized with schema_version."""
    from scripts.dossier_build import init_evidence_store, EVIDENCE_STORE_DIR
    store_path = init_evidence_store()
    assert store_path.exists()
    manifest = store_path / "manifest.json"
    assert manifest.exists()
    with open(manifest) as f:
        data = json.load(f)
    assert data["schema_version"] == "1.0"
    assert data["hash_algorithm"] == "sha256"
    assert data["created_batch"] == "B933"


def test_b933_list_strategies_returns_218_plus_minus():
    """B933 strategy enumeration: list_strategies_for_dossier returns ALL_STRATEGIES."""
    from scripts.dossier_build import list_strategies_for_dossier
    strategies = list_strategies_for_dossier()
    # Per CLAUDE.md live count 2026-06-18: ALL_STRATEGIES has 219 (B874 deletions)
    # Allow flex range 215-225 to permit ongoing roster changes
    assert 215 <= len(strategies) <= 225, (
        f"Expected 215-225 strategies in ALL_STRATEGIES; got {len(strategies)}. "
        f"If roster materially changed, update test bounds + investigate."
    )
