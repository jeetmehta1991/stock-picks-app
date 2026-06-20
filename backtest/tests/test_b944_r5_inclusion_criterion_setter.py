"""B944 (2026-06-20): pyramid tests for r5_inclusion_criterion setter.

# Source: PATH_TO_PHASE_1B_ALPHA.md 13.8.1 + B934 Council 45 enum + Council 48
# batch 4 commit 3 "highest leverage in entire Phase P1" verdict.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_b944_valid_criteria_match_council_45_enum():
    """B944 enum contract: VALID_CRITERIA matches Council 45 design + B934 schema."""
    from backtest.diagnostics.r5_inclusion_criterion import VALID_CRITERIA
    expected = ("r4_metrics_passed", "pre_cube_evidence_sufficient", "deferred")
    assert VALID_CRITERIA == expected


def test_b944_track_1_passing_strategy_returns_r4_metrics_passed():
    """B944 decision tree: Track 1 + passes_all=True + gates clear -> r4_metrics_passed."""
    from backtest.diagnostics.r5_inclusion_criterion import compute_r5_inclusion_criterion
    dossier = {
        "sections": {
            "section_09_r4_cube_metrics": {
                "track": 1,
                "metrics": {"passes_all": True},
            },
            "section_10_cost_sensitivity_ratio": {"passes_dec_612_gate": True},
            "section_11_chow_break_point": {"passes_dec_613_gate": True},
            "section_12_adf_p_value": {"passes_dec_614_gate": True},
            "section_20_pre_cube_evidence_9b": {"has_pre_cube_evidence": True},
        }
    }
    result = compute_r5_inclusion_criterion(dossier)
    assert result["value"] == "r4_metrics_passed"
    assert result["track"] == 1


def test_b944_track_1_failing_with_evidence_fallback_to_pre_cube():
    """B944 fallback: Track 1 + passes_all=False but 9b evidence -> pre_cube_evidence_sufficient."""
    from backtest.diagnostics.r5_inclusion_criterion import compute_r5_inclusion_criterion
    dossier = {
        "sections": {
            "section_09_r4_cube_metrics": {
                "track": 1,
                "metrics": {"passes_all": False},
            },
            "section_10_cost_sensitivity_ratio": {"passes_dec_612_gate": False},
            "section_11_chow_break_point": {"passes_dec_613_gate": True},
            "section_12_adf_p_value": {"passes_dec_614_gate": True},
            "section_20_pre_cube_evidence_9b": {"has_pre_cube_evidence": True},
        }
    }
    result = compute_r5_inclusion_criterion(dossier)
    assert result["value"] == "pre_cube_evidence_sufficient"


def test_b944_track_1_failing_no_evidence_deferred():
    """B944: Track 1 + passes_all=False + no 9b evidence -> deferred."""
    from backtest.diagnostics.r5_inclusion_criterion import compute_r5_inclusion_criterion
    dossier = {
        "sections": {
            "section_09_r4_cube_metrics": {
                "track": 1,
                "metrics": {"passes_all": False},
            },
            "section_10_cost_sensitivity_ratio": {"passes_dec_612_gate": False},
            "section_11_chow_break_point": {"passes_dec_613_gate": True},
            "section_12_adf_p_value": {"passes_dec_614_gate": True},
            "section_20_pre_cube_evidence_9b": {"has_pre_cube_evidence": False},
        }
    }
    result = compute_r5_inclusion_criterion(dossier)
    assert result["value"] == "deferred"


def test_b944_track_2_with_evidence_returns_pre_cube_sufficient():
    """B944: Track 2 (post-R4) + 9b evidence -> pre_cube_evidence_sufficient."""
    from backtest.diagnostics.r5_inclusion_criterion import compute_r5_inclusion_criterion
    dossier = {
        "sections": {
            "section_09_r4_cube_metrics": {"track": 2},
            "section_20_pre_cube_evidence_9b": {"has_pre_cube_evidence": True},
        }
    }
    result = compute_r5_inclusion_criterion(dossier)
    assert result["value"] == "pre_cube_evidence_sufficient"
    assert result["track"] == 2


def test_b944_track_2_no_evidence_deferred():
    """B944: Track 2 + no 9b evidence -> deferred."""
    from backtest.diagnostics.r5_inclusion_criterion import compute_r5_inclusion_criterion
    dossier = {
        "sections": {
            "section_09_r4_cube_metrics": {"track": 2},
            "section_20_pre_cube_evidence_9b": {"has_pre_cube_evidence": False},
        }
    }
    result = compute_r5_inclusion_criterion(dossier)
    assert result["value"] == "deferred"


def test_b944_section_9_missing_returns_deferred():
    """B944: no Section 9 -> deferred (cannot determine track)."""
    from backtest.diagnostics.r5_inclusion_criterion import compute_r5_inclusion_criterion
    dossier = {"sections": {}}
    result = compute_r5_inclusion_criterion(dossier)
    assert result["value"] == "deferred"
    assert result["track"] is None


def test_b944_set_for_dossier_round_trip():
    """B944 setter persists criterion + detail in dossier JSON."""
    from scripts.dossier_build import init_dossier, DOSSIERS_DIR
    from backtest.diagnostics.section_09_r4_cube_metrics import populate_section_09_for_dossier
    from backtest.diagnostics.section_09b_pre_cube_evidence import populate_section_09b_for_dossier
    from backtest.diagnostics.section_r4_passthrough import populate_r4_passthrough_sections_for_dossier
    from backtest.diagnostics.r5_inclusion_criterion import set_r5_inclusion_criterion_for_dossier

    test_strategy = "donchian_10_breakout"  # in R4
    dossier_path = init_dossier(test_strategy, overwrite=True)
    populate_section_09_for_dossier(test_strategy, dossier_path)
    populate_section_09b_for_dossier(test_strategy, dossier_path)
    populate_r4_passthrough_sections_for_dossier(test_strategy, dossier_path)
    criterion = set_r5_inclusion_criterion_for_dossier(dossier_path)

    with open(dossier_path) as f:
        dossier = json.load(f)
    assert dossier["r5_inclusion_criterion"] in {
        "r4_metrics_passed", "pre_cube_evidence_sufficient", "deferred"
    }
    assert "r5_inclusion_criterion_detail" in dossier
