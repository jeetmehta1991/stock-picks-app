"""B966 (2026-06-20): pyramid tests for Section 17 soft_score_weight_calibration.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 17 + DEC #1 + Council 67
# verdict per owner directive 2026-06-20 autonomous mandate per CHECKLIST #77.
"""
from __future__ import annotations

import json


def test_b966_section_17_extractor_importable():
    """B966 contract: module importable + functions exposed."""
    from backtest.diagnostics import section_17_soft_score_weight_calibration as mod
    assert hasattr(mod, "extract_section_17_for_strategy")
    assert hasattr(mod, "populate_section_17_for_dossier")
    assert hasattr(mod, "DEC_1_WEIGHTS")


def test_b966_dec_1_weights_match_path_canonical():
    """B966: DEC #1 weights match PATH Section 13.4: 0.35/0.30/0.23/0.12."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import DEC_1_WEIGHTS
    assert DEC_1_WEIGHTS["sharpe"] == 0.35
    assert DEC_1_WEIGHTS["calmar"] == 0.30
    assert DEC_1_WEIGHTS["profit_factor"] == 0.23
    assert DEC_1_WEIGHTS["fourth_ingredient_unspecified"] == 0.12


def test_b966_dec_1_weights_sum_to_1():
    """B966: DEC #1 weights sum to 1.0 exactly."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import (
        DEC_1_WEIGHTS, _weights_sum,
    )
    assert abs(_weights_sum() - 1.0) < 1e-6
    assert abs(sum(DEC_1_WEIGHTS.values()) - 1.0) < 1e-6


def test_b966_placeholder_flag_machine_readable():
    """B966 Contrarian hardening: placeholder=True + do_not_use_for_winner_selection=True."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import extract_section_17_for_strategy
    result = extract_section_17_for_strategy("any_strategy")
    assert result["placeholder"] is True
    assert result["do_not_use_for_winner_selection"] is True


def test_b966_calibration_status_pre_r5():
    """B966: pre-R5 calibration_status string is explicit."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import extract_section_17_for_strategy
    result = extract_section_17_for_strategy("any_strategy")
    assert result["calibration_status"] == "pre_r5_static_weights_pending_null_calibration"
    assert result["calibration_method_pending"] == "null_distribution_variance_inverse"


def test_b966_fourth_ingredient_status_documented():
    """B966: 4th ingredient is documented as unspecified pending owner decision."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import extract_section_17_for_strategy
    result = extract_section_17_for_strategy("any_strategy")
    assert result["fourth_ingredient_status"] == "unspecified_per_DEC_1_pending_owner_decision"
    assert isinstance(result["fourth_ingredient_candidates"], list)
    assert len(result["fourth_ingredient_candidates"]) > 0
    # All candidates from canonical CLAUDE.md metrics
    expected = {"sortino", "win_rate", "psr", "expectancy"}
    assert set(result["fourth_ingredient_candidates"]) == expected


def test_b966_calibration_dependency_links_to_section_16():
    """B966: calibration_dependency points to Section 16 (null injection)."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import extract_section_17_for_strategy
    result = extract_section_17_for_strategy("any_strategy")
    assert result["calibration_dependency"] == "section_16_negative_control_canary"


def test_b966_payload_identical_across_strategies():
    """B966: Section 17 is framework-level; payload identical for any strategy name."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import extract_section_17_for_strategy
    r1 = extract_section_17_for_strategy("rsi_oversold_long")
    r2 = extract_section_17_for_strategy("smc_bos_continuation")
    r3 = extract_section_17_for_strategy("null_random_long_p05")
    # All three return identical payloads (framework-level state)
    assert r1 == r2 == r3


def test_b966_phase_1c_revisit_method_bayesian():
    """B966: phase_1c_revisit_method is bayesian_posterior per PATH."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import extract_section_17_for_strategy
    result = extract_section_17_for_strategy("any_strategy")
    assert result["phase_1c_revisit_method"] == "bayesian_posterior"


def test_b966_schema_keys_complete():
    """B966: extract returns expected schema keys."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import extract_section_17_for_strategy
    result = extract_section_17_for_strategy("any_strategy")
    expected_keys = {
        "weights", "weights_sum", "weight_source", "placeholder",
        "do_not_use_for_winner_selection", "calibration_method_pending",
        "calibration_status", "fourth_ingredient_status",
        "fourth_ingredient_candidates", "calibration_dependency",
        "phase_1c_revisit_method", "method", "source", "limitation",
        "memory_rule_reference",
    }
    assert set(result.keys()) == expected_keys


def test_b966_populate_writes_to_dossier(tmp_path):
    """B966: populate_section_17_for_dossier writes section slot."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import populate_section_17_for_dossier
    dossier_path = tmp_path / "dossier.json"
    dossier_path.write_text(json.dumps({"strategy": "any", "sections": {}}))
    populate_section_17_for_dossier("any", dossier_path)
    with open(dossier_path) as f:
        dossier = json.load(f)
    assert "section_17_soft_score_weight_calibration" in dossier["sections"]


def test_b966_weight_source_attribution_to_dec_1():
    """B966: weight_source attributes back to DEC #1 PATH Section 13.4."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import extract_section_17_for_strategy
    result = extract_section_17_for_strategy("any_strategy")
    assert "DEC #1" in result["weight_source"]
    assert "Section 13.4" in result["weight_source"]
