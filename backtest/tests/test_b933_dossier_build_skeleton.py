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
    """B933 schema invariant: exactly 19 dossier sections per PATH 13.3."""
    from scripts.dossier_build import DOSSIER_SECTIONS
    assert len(DOSSIER_SECTIONS) == 19, (
        f"DOSSIER_SECTIONS must have exactly 19 entries per PATH 13.3; "
        f"got {len(DOSSIER_SECTIONS)}"
    )
    # IDs must be 1..19 contiguous
    ids = sorted(s[0] for s in DOSSIER_SECTIONS)
    assert ids == list(range(1, 20)), f"Section IDs must be 1..19; got {ids}"


def test_b933_dossier_section_keys_unique():
    """B933 schema invariant: section keys must be unique."""
    from scripts.dossier_build import DOSSIER_SECTIONS
    keys = [s[1] for s in DOSSIER_SECTIONS]
    assert len(keys) == len(set(keys)), (
        f"Section keys must be unique; duplicates: "
        f"{[k for k in keys if keys.count(k) > 1]}"
    )


def test_b933_empty_dossier_has_19_null_sections():
    """B933 init contract: empty dossier has 19 sections, all null."""
    from scripts.dossier_build import _empty_dossier_schema
    schema = _empty_dossier_schema("test_strategy")
    assert "sections" in schema
    assert len(schema["sections"]) == 19, (
        f"Empty dossier must have 19 section slots; got {len(schema['sections'])}"
    )
    nulls = [k for k, v in schema["sections"].items() if v is None]
    assert len(nulls) == 19, (
        f"All 19 sections must initialize to None; got {19 - len(nulls)} populated"
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
        assert data["dossier_build_batch"] == "B933"
        assert data["phase"] == "P1"
        assert len(data["sections"]) == 19
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
