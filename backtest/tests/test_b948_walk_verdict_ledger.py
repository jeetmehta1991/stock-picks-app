"""B948 (2026-06-20): pyramid tests for walk_verdict_ledger + Section 9b integration.

# Source: Council 52 UNANIMOUS option-epsilon verdict per owner directive
# 2026-06-20 Option B.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent.parent


def test_b948_ledger_builder_script_importable():
    """B948 contract: build_walk_verdict_ledger.py importable + main() callable."""
    from scripts import build_walk_verdict_ledger
    assert hasattr(build_walk_verdict_ledger, "main")
    assert hasattr(build_walk_verdict_ledger, "build_walk_verdict_ledger")
    assert hasattr(build_walk_verdict_ledger, "parse_walk_doc")


def test_b948_walk_header_pattern_matches_canonical_format():
    """B948: WALK_HEADER_PATTERN matches '### BR-1. `strat_NAME`' format."""
    from scripts.build_walk_verdict_ledger import WALK_HEADER_PATTERN
    sample = "### BR-1. `strat_52w_high_breakout` (Batch 586+589, 52w family, walked B676)"
    m = WALK_HEADER_PATTERN.match(sample)
    assert m is not None
    assert m.group("strategy") == "strat_52w_high_breakout"
    assert m.group("cluster_id") == "BR-1"
    assert "Batch 586" in m.group("context")


def test_b948_parse_walk_doc_extracts_entries():
    """B948: parse_walk_doc returns structured entries from a cluster walk doc."""
    from scripts.build_walk_verdict_ledger import parse_walk_doc
    sample_doc = REPO / "STAGE_4_BREAKOUT_CLUSTER_WALKS.md"
    if not sample_doc.exists():
        pytest.skip("STAGE_4_BREAKOUT_CLUSTER_WALKS.md missing; cannot test parser")
    entries = parse_walk_doc(sample_doc)
    # Per console output: 19 entries
    assert len(entries) >= 15, f"Expected >=15 walk entries; got {len(entries)}"
    # Each entry has required fields
    for e in entries:
        assert "strategy" in e
        assert "confidence" in e
        assert e["confidence"] == "high"
        assert "source" in e


def test_b948_ledger_loaded_in_r5_inclusion_criterion_module():
    """B948: walk_verdict_ledger.json is loadable from the criterion module."""
    from backtest.diagnostics.r5_inclusion_criterion import _load_walk_verdict_ledger
    ledger = _load_walk_verdict_ledger()
    if not ledger:
        pytest.skip("walk_verdict_ledger.json not generated; run build_walk_verdict_ledger.py")
    # Ledger should have at least 50 strategies per Council 52 sparse-acceptable
    assert len(ledger) >= 50, f"Ledger should have >=50 entries; got {len(ledger)}"


def test_b948_strong_evidence_includes_ledger_entry():
    """B948: _has_strong_evidence returns True when strategy has ledger entry, even without other markers."""
    from backtest.diagnostics.r5_inclusion_criterion import _has_strong_evidence, _load_walk_verdict_ledger
    ledger = _load_walk_verdict_ledger()
    if not ledger:
        pytest.skip("Ledger not built")
    # Pick a strategy known to be in ledger
    test_strategy = next(iter(ledger.keys()))
    # Section 9b with NO other evidence
    section_9b = {
        "walk_batches": [],
        "fire_count_projection": None,
        "status_tags": [],
    }
    passes, breakdown = _has_strong_evidence(section_9b, strategy=test_strategy)
    assert passes is True, (
        f"Strategy {test_strategy!r} in walk_verdict_ledger should pass STRONG check"
    )
    assert breakdown["walk_verdict_ledger_entries_count"] > 0


def test_b948_strong_evidence_excludes_ledger_when_no_strategy_passed():
    """B948: _has_strong_evidence ignores ledger when strategy=None (backward-compat)."""
    from backtest.diagnostics.r5_inclusion_criterion import _has_strong_evidence
    section_9b = {
        "walk_batches": [],
        "fire_count_projection": None,
        "status_tags": [],
    }
    # No strategy passed -> ledger check skipped; only other criteria checked
    passes, _ = _has_strong_evidence(section_9b)
    assert passes is False
