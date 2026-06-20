"""B957 (2026-06-20): pyramid tests for retrospective trial-count audit script.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.2 + Council 61+62 UNANIMOUS
# per owner directive 2026-06-20 'C then B' per CHECKLIST #77.
"""
from __future__ import annotations

import pytest


def test_b957_script_importable():
    """B957 contract: script importable + classifier/parser functions exposed."""
    from scripts import b957_audit_retrospective_trial_counts as mod
    assert hasattr(mod, "main")
    assert hasattr(mod, "_classify_commit")
    assert hasattr(mod, "_extract_batch_number")
    assert hasattr(mod, "TRIAL_KEYWORDS")


def test_b957_extract_batch_number_long_form():
    """B957: 'Batch 957 ...' extracts batch 957."""
    from scripts.b957_audit_retrospective_trial_counts import _extract_batch_number
    assert _extract_batch_number("Batch 957 (2026-06-20): test") == 957
    assert _extract_batch_number("Batch 100: alpha") == 100


def test_b957_classify_new_strategy_commit():
    """B957: commit with NEW_STRATEGY keyword classifies as new_strategy."""
    from scripts.b957_audit_retrospective_trial_counts import _classify_commit
    cats = _classify_commit("Class 7 NEW: wired strat_xyz")
    assert "new_strategy" in cats


def test_b957_classify_gate_change_commit():
    """B957: commit with gate keyword classifies as gate_change."""
    from scripts.b957_audit_retrospective_trial_counts import _classify_commit
    cats = _classify_commit("loosen gate vol_spike on strat_abc")
    assert "gate_change" in cats


def test_b957_classify_regime_affinity_commit():
    """B957: commit with STRATEGY_REGIME_AFFINITY keyword classifies as regime_affinity."""
    from scripts.b957_audit_retrospective_trial_counts import _classify_commit
    cats = _classify_commit("update STRATEGY_REGIME_AFFINITY for strat_abc")
    assert "regime_affinity" in cats


def test_b957_classify_state_event_commit():
    """B957: STATE->EVENT conversion classifies correctly."""
    from scripts.b957_audit_retrospective_trial_counts import _classify_commit
    cats = _classify_commit("STATE -> EVENT conversion for strat_abc")
    assert "state_event_conversion" in cats


def test_b957_classify_docstring_only_excluded():
    """B957: docstring-only commits classified separately (not a trial)."""
    from scripts.b957_audit_retrospective_trial_counts import _classify_commit
    cats = _classify_commit("docstring fix for strat_abc")
    assert "docstring_only" in cats
