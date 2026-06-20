"""B947 (2026-06-20): pyramid tests for 140-deferred classifier.

# Source: Council 51 hybrid epsilon verdict per owner directive 2026-06-20 Option A.
"""
from __future__ import annotations

import pytest


def test_b947_classifier_script_importable():
    """B947 contract: classify_deferred_140.py importable + main() callable."""
    from scripts import classify_deferred_140
    assert hasattr(classify_deferred_140, "main")
    assert hasattr(classify_deferred_140, "classify_strategy")
    assert hasattr(classify_deferred_140, "_load_walk_doc_strategy_index")


def test_b947_classifier_buckets_priority_ordered():
    """B947 logic: priority order V > IV > III > II > I; highest evidence wins (disjoint)."""
    from scripts.classify_deferred_140 import classify_strategy
    # Strategy with EVERY evidence type; bucket should be V (highest priority)
    dossier = {
        "sections": {
            "section_20_pre_cube_evidence_9b": {
                "walk_batches": ["B583"],
                "status_tags": ["PATTERN_AA"],
                "fire_count_projection": {"fires_per_year_long": 10.0, "source_file": "b660.json"},
            }
        }
    }
    walk_doc_index = {"strat_x": ["STAGE_4_X.md"]}
    result = classify_strategy("strat_x", dossier, walk_doc_index)
    assert result["bucket"] == "V_walk_doc_mentioned"


def test_b947_classifier_bucket_iv_below_threshold_fire():
    """B947 logic: fire-count > 0 but < 30 -> Bucket IV (when not in walk doc)."""
    from scripts.classify_deferred_140 import classify_strategy
    dossier = {
        "sections": {
            "section_20_pre_cube_evidence_9b": {
                "walk_batches": [],
                "status_tags": [],
                "fire_count_projection": {"fires_per_year_long": 5.0},
            }
        }
    }
    result = classify_strategy("strat_x", dossier, walk_doc_index={})
    assert result["bucket"] == "IV_below_threshold_fire"


def test_b947_classifier_bucket_iii_lineage_tags_only():
    """B947 logic: lineage tags but no fire-count + no walk-doc + no walks -> Bucket III."""
    from scripts.classify_deferred_140 import classify_strategy
    dossier = {
        "sections": {
            "section_20_pre_cube_evidence_9b": {
                "walk_batches": [],
                "status_tags": ["PATTERN_AA", "Wave_lineage"],
                "fire_count_projection": None,
            }
        }
    }
    result = classify_strategy("strat_x", dossier, walk_doc_index={})
    assert result["bucket"] == "III_lineage_tags_only"


def test_b947_classifier_bucket_ii_batch_markers_only():
    """B947 logic: generic batch markers only (no lineage, no fc, no walk-doc) -> Bucket II."""
    from scripts.classify_deferred_140 import classify_strategy
    dossier = {
        "sections": {
            "section_20_pre_cube_evidence_9b": {
                "walk_batches": ["B583", "B600"],
                "status_tags": [],
                "fire_count_projection": None,
            }
        }
    }
    result = classify_strategy("strat_x", dossier, walk_doc_index={})
    assert result["bucket"] == "II_batch_markers_only"


def test_b947_classifier_bucket_i_truly_deferred():
    """B947 logic: zero evidence -> Bucket I."""
    from scripts.classify_deferred_140 import classify_strategy
    dossier = {
        "sections": {
            "section_20_pre_cube_evidence_9b": {
                "walk_batches": [],
                "status_tags": [],
                "fire_count_projection": None,
            }
        }
    }
    result = classify_strategy("strat_x", dossier, walk_doc_index={})
    assert result["bucket"] == "I_truly_deferred"
