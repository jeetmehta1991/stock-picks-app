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


def test_b944_b946_track_1_failing_with_strong_evidence_fallback():
    """B944+B946: Track 1 + passes_all=False but Section 9b STRONG evidence -> pre_cube_evidence_sufficient.

    B946 Council 50 refinement: requires STRONG evidence (S4-walk OR
    fire-count>=30 OR owner-approved status tag). Bare has_pre_cube_evidence=True
    no longer sufficient.
    """
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
            # B946: STRONG evidence required - use S4-B walk marker
            "section_20_pre_cube_evidence_9b": {
                "walk_batches": ["S4-B754"],
                "fire_count_projection": None,
                "status_tags": [],
                "has_pre_cube_evidence": True,
            },
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


def test_b944_b946_track_2_with_strong_evidence_returns_pre_cube_sufficient():
    """B944+B946: Track 2 (post-R4) + STRONG 9b evidence -> pre_cube_evidence_sufficient.

    B946 Council 50: STRONG evidence required (S4-walk OR fire-count>=30 OR
    owner-approved status tag). Plain has_pre_cube_evidence=True with only
    lineage tags is no longer sufficient.
    """
    from backtest.diagnostics.r5_inclusion_criterion import compute_r5_inclusion_criterion
    # Use fire-count >=30/yr as STRONG evidence
    dossier = {
        "sections": {
            "section_09_r4_cube_metrics": {"track": 2},
            "section_20_pre_cube_evidence_9b": {
                "walk_batches": [],
                "fire_count_projection": {"fires_per_year_long": 50.0, "fires_per_year_short": 0},
                "status_tags": [],
                "has_pre_cube_evidence": True,
            },
        }
    }
    result = compute_r5_inclusion_criterion(dossier)
    assert result["value"] == "pre_cube_evidence_sufficient"
    assert result["track"] == 2


def test_b946_track_2_with_only_lineage_tags_returns_deferred():
    """B946 Council 50: Track 2 with ONLY lineage tags (PATTERN_X / Wave_lineage)
    is INSUFFICIENT; returns deferred."""
    from backtest.diagnostics.r5_inclusion_criterion import compute_r5_inclusion_criterion
    dossier = {
        "sections": {
            "section_09_r4_cube_metrics": {"track": 2},
            "section_20_pre_cube_evidence_9b": {
                "walk_batches": ["B583"],  # generic B### rejected
                "fire_count_projection": {"fires_per_year_long": 5.0},  # < 30 threshold
                "status_tags": ["PATTERN_AA", "Wave_lineage"],  # lineage only
                "has_pre_cube_evidence": True,
            },
        }
    }
    result = compute_r5_inclusion_criterion(dossier)
    assert result["value"] == "deferred"


def test_b946_fire_count_threshold_30_per_year():
    """B946 Council 50: fire-count threshold exactly 30/yr per direction."""
    from backtest.diagnostics.r5_inclusion_criterion import _has_strong_evidence
    # Above threshold
    section_9b_pass = {
        "walk_batches": [], "status_tags": [],
        "fire_count_projection": {"fires_per_year_long": 30.0, "fires_per_year_short": 0},
    }
    passes, _ = _has_strong_evidence(section_9b_pass)
    assert passes is True
    # Below threshold
    section_9b_fail = {
        "walk_batches": [], "status_tags": [],
        "fire_count_projection": {"fires_per_year_long": 29.9, "fires_per_year_short": 0},
    }
    passes, _ = _has_strong_evidence(section_9b_fail)
    assert passes is False


def test_b946_s4_walk_marker_accepted_generic_batch_rejected():
    """B946 Council 50: S4-B and W## walk markers are STRONG; generic B### is NOT."""
    from backtest.diagnostics.r5_inclusion_criterion import _has_strong_evidence
    # S4 marker STRONG
    sb_s4 = {"walk_batches": ["S4-B754"], "status_tags": [], "fire_count_projection": None}
    passes, breakdown = _has_strong_evidence(sb_s4)
    assert passes is True
    assert "S4-B754" in breakdown["strong_walk_markers"]
    # W## marker STRONG
    sb_w = {"walk_batches": ["W5"], "status_tags": [], "fire_count_projection": None}
    passes, _ = _has_strong_evidence(sb_w)
    assert passes is True
    # Generic B### NOT STRONG
    sb_b = {"walk_batches": ["B583", "B600"], "status_tags": [], "fire_count_projection": None}
    passes, _ = _has_strong_evidence(sb_b)
    assert passes is False


def test_b946_strong_status_tags_accepted():
    """B946 Council 50: each STRONG status tag triggers evidence pass."""
    from backtest.diagnostics.r5_inclusion_criterion import _has_strong_evidence, STRONG_STATUS_TAGS
    for tag in STRONG_STATUS_TAGS:
        sb = {"walk_batches": [], "fire_count_projection": None, "status_tags": [tag]}
        passes, _ = _has_strong_evidence(sb)
        assert passes is True, f"STRONG tag {tag!r} should pass evidence check"


def test_b946_lineage_only_tags_rejected():
    """B946 Council 50: lineage tags alone are INSUFFICIENT."""
    from backtest.diagnostics.r5_inclusion_criterion import _has_strong_evidence
    sb = {
        "walk_batches": [], "fire_count_projection": None,
        "status_tags": ["PATTERN_AA", "PATTERN_W", "Wave_lineage", "EVENT_only", "SHORT_EXPLORATORY"],
    }
    passes, breakdown = _has_strong_evidence(sb)
    assert passes is False
    assert len(breakdown["rejected_lineage_tags"]) >= 4


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
