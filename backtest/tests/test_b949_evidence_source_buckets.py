"""B949 (2026-06-20): pyramid tests for evidence-source bucket investigation.

# Source: Council 53 UNANIMOUS option-epsilon hybrid beta+delta verdict per
# owner directive 2026-06-20 Option B.
"""
from __future__ import annotations

import pytest


def test_b949_script_importable():
    """B949 contract: investigation script importable + main() callable."""
    from scripts import b949_investigate_evidence_source_buckets as mod
    assert hasattr(mod, "main")
    assert hasattr(mod, "_classify_sufficient_by_source")
    assert hasattr(mod, "_classify_deferred_by_bucket")


def test_b949_classify_sufficient_d_only_detected():
    """B949 BETA: strategy with ONLY walk_verdict_ledger entry should be D-only.

    Test fixture: empty section_9b but mock ledger should classify as D.
    """
    from scripts.b949_investigate_evidence_source_buckets import _classify_sufficient_by_source
    from backtest.diagnostics.r5_inclusion_criterion import _load_walk_verdict_ledger
    ledger = _load_walk_verdict_ledger()
    if not ledger:
        pytest.skip("Ledger not built")
    # B950 (2026-06-20) update: with LEDGER_REQUIRE_VERDICT_BEARING=True default,
    # need a strategy with verdict_strength in ('strong','medium') to detect D source.
    test_strategy = None
    for strat, entries in ledger.items():
        if any(e.get("verdict_strength") in ("strong", "medium") for e in entries):
            test_strategy = strat
            break
    if test_strategy is None:
        pytest.skip("No verdict-bearing ledger entry")
    # Empty section_9b: only D should fire
    dossier = {
        "sections": {
            "section_20_pre_cube_evidence_9b": {
                "walk_batches": [],
                "status_tags": [],
                "fire_count_projection": None,
            }
        }
    }
    result = _classify_sufficient_by_source(test_strategy, dossier)
    assert "D" in result["sources_active"]


def test_b949_classify_sufficient_a_b_c_combinations():
    """B949 BETA: A+B+C combinations correctly identified."""
    from scripts.b949_investigate_evidence_source_buckets import _classify_sufficient_by_source
    dossier = {
        "sections": {
            "section_20_pre_cube_evidence_9b": {
                "walk_batches": ["S4-B600", "W5"],
                "status_tags": ["EXPLORATORY"],
                "fire_count_projection": {"fires_per_year_long": 50.0},
            }
        }
    }
    result = _classify_sufficient_by_source("unknown_strategy_not_in_ledger", dossier)
    assert "A" in result["sources_active"]
    assert "B" in result["sources_active"]
    assert "C" in result["sources_active"]


def test_b949_classify_deferred_bucket_i_not_in_walk_doc():
    """B949 DELTA: strategy not in any walk doc -> Bucket I."""
    from scripts.b949_investigate_evidence_source_buckets import _classify_deferred_by_bucket
    dossier = {
        "sections": {
            "section_20_pre_cube_evidence_9b": {
                "walk_batches": [],
                "status_tags": [],
                "fire_count_projection": None,
            }
        }
    }
    result = _classify_deferred_by_bucket("unknown_strategy", dossier, walk_doc_index={})
    assert result["bucket"] == "I_not_in_any_walk_doc"


def test_b949_classify_deferred_bucket_ii_walk_doc_no_header():
    """B949 DELTA: in walk doc, no ledger entry -> Bucket II (parser gap)."""
    from scripts.b949_investigate_evidence_source_buckets import _classify_deferred_by_bucket
    dossier = {
        "sections": {
            "section_20_pre_cube_evidence_9b": {
                "walk_batches": [],
                "status_tags": [],
                "fire_count_projection": None,
            }
        }
    }
    # Strategy mentioned in walk doc but NOT in ledger
    walk_doc_index = {"strat_x": ["STAGE_4_PIVOT_CLUSTER_WALKS.md"]}
    result = _classify_deferred_by_bucket("strat_x", dossier, walk_doc_index)
    assert result["bucket"] == "II_in_walk_doc_no_structured_header"
