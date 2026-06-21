"""B966 (2026-06-20): pyramid tests for Section 17 soft_score_weight_calibration.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 17 + DEC #1 + Council 67
# verdict per owner directive 2026-06-20 autonomous mandate per CHECKLIST #77.
# B969 (2026-06-21) AMENDED for Council 70+71 DEFER + RENORMALIZE verdict:
# 3-ingredient 0.40/0.34/0.26 (4th post-R5 from null calibration).
"""
from __future__ import annotations

import json


def test_b966_section_17_extractor_importable():
    """B966 contract: module importable + functions exposed."""
    from backtest.diagnostics import section_17_soft_score_weight_calibration as mod
    assert hasattr(mod, "extract_section_17_for_strategy")
    assert hasattr(mod, "populate_section_17_for_dossier")
    assert hasattr(mod, "DEC_1_WEIGHTS")
    assert hasattr(mod, "OBSERVER_COLUMNS")


def test_b966_dec_1_weights_renormalized_3_ingredient_b969():
    """B966+B969: DEC #1 weights renormalized to 0.40/0.34/0.26 (3 ingredients).

    B969 Council 70+71 owner-approved 2026-06-21: DEFER + RENORMALIZE
    (4th ingredient post-R5 null calibration).
    """
    from backtest.diagnostics.section_17_soft_score_weight_calibration import DEC_1_WEIGHTS
    assert DEC_1_WEIGHTS["sharpe"] == 0.40
    assert DEC_1_WEIGHTS["calmar"] == 0.34
    assert DEC_1_WEIGHTS["profit_factor"] == 0.26
    # 4th ingredient slot REMOVED (was 0.12)
    assert "fourth_ingredient_unspecified" not in DEC_1_WEIGHTS
    # Exactly 3 ingredients
    assert len(DEC_1_WEIGHTS) == 3


def test_b966_dec_1_weights_sum_to_1():
    """B966: DEC #1 weights sum to 1.0 (within float precision)."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import (
        DEC_1_WEIGHTS, _weights_sum,
    )
    assert abs(_weights_sum() - 1.0) < 1e-6
    assert abs(sum(DEC_1_WEIGHTS.values()) - 1.0) < 1e-6


def test_b966_b969_no_placeholder_flag():
    """B969 amendment: placeholder=True + do_not_use flags REMOVED post-renormalization.

    The 3-ingredient renormalized weights ARE the canonical pre-R5 spec
    (not a placeholder); winner-selection can proceed using these 3 +
    DSR/cost-sens gates. Observer columns are separate from the
    weighted soft-score.
    """
    from backtest.diagnostics.section_17_soft_score_weight_calibration import extract_section_17_for_strategy
    result = extract_section_17_for_strategy("any_strategy")
    assert "placeholder" not in result
    assert "do_not_use_for_winner_selection" not in result
    assert result["n_ingredients"] == 3
    assert result["is_renormalized_from_4_ingredient_draft"] is True


def test_b966_b969_calibration_status_renormalized():
    """B969: calibration_status reflects 3-ingredient renormalized + post-R5 pending."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import extract_section_17_for_strategy
    result = extract_section_17_for_strategy("any_strategy")
    assert result["calibration_status"] == "3_ingredient_renormalized_post_r5_null_calibration_pending"
    assert result["calibration_method_pending"] == "null_distribution_variance_inverse"


def test_b966_b969_fourth_ingredient_deferred_status():
    """B969: 4th ingredient status documents deferral per Council 70+71."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import extract_section_17_for_strategy
    result = extract_section_17_for_strategy("any_strategy")
    assert "deferred_post_r5" in result["fourth_ingredient_status"]
    assert "council_70" in result["fourth_ingredient_status"].lower()


def test_b966_b969_observer_columns_emitted():
    """B969: 4 observer columns shipped for empirical 4th-ingredient comparison."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import (
        extract_section_17_for_strategy, OBSERVER_COLUMNS,
    )
    result = extract_section_17_for_strategy("any_strategy")
    expected_observers = {"sharpe_stability", "ulcer_index", "tail_ratio", "k_ratio"}
    assert set(OBSERVER_COLUMNS) == expected_observers
    assert set(result["fourth_ingredient_observer_columns"]) == expected_observers
    # Pre-R5: all observer values are None
    assert result["observer_column_status"] == "pending_r5_cube_launch"
    assert all(v is None for v in result["observer_column_values"].values())


def test_b966_b969_post_r5_ticket_documented():
    """B969: post-R5 calibration ticket explicitly named."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import extract_section_17_for_strategy
    result = extract_section_17_for_strategy("any_strategy")
    assert result["post_r5_ticket"] == "S5-NULL-CALIB-SOFT-SCORE-4TH-INGREDIENT"


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
    assert r1 == r2 == r3


def test_b966_phase_1c_revisit_method_bayesian():
    """B966: phase_1c_revisit_method is bayesian_posterior per PATH."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import extract_section_17_for_strategy
    result = extract_section_17_for_strategy("any_strategy")
    assert result["phase_1c_revisit_method"] == "bayesian_posterior"


def test_b966_b969_schema_keys_complete():
    """B966+B969: extract returns expected schema keys for renormalized 3-ingredient."""
    from backtest.diagnostics.section_17_soft_score_weight_calibration import extract_section_17_for_strategy
    result = extract_section_17_for_strategy("any_strategy")
    expected_keys = {
        "weights", "weights_sum", "weight_source",
        "n_ingredients", "is_renormalized_from_4_ingredient_draft",
        "calibration_method_pending", "calibration_status",
        "fourth_ingredient_status", "fourth_ingredient_observer_columns",
        "observer_column_status", "observer_column_values",
        "calibration_dependency", "post_r5_ticket",
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
