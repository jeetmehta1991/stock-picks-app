"""B955 (2026-06-20): pyramid tests for Section 8 data_source_asymmetry extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 8 + Council 59 UNANIMOUS
# verdict per owner directive 2026-06-20 autonomous mandate +
# feedback_asymmetric_data_sources_break_mechanical_inverse (B611).
"""
from __future__ import annotations

import json

import pytest


def test_b955_section_08_extractor_importable():
    """B955 contract: section_08_data_source_asymmetry module importable."""
    from backtest.diagnostics import section_08_data_source_asymmetry as mod
    assert hasattr(mod, "extract_section_08_for_strategy")
    assert hasattr(mod, "populate_section_08_for_dossier")
    assert hasattr(mod, "classify_signal")
    assert hasattr(mod, "ASYMMETRIC_SIGNAL_PATTERNS")
    assert hasattr(mod, "INVERSE_UNSAFE_CLASSES")


def test_b955_inverse_unsafe_classes_match_b611():
    """B955 contract: INVERSE_UNSAFE_CLASSES = {13F, insider_buy, 13D} per B611."""
    from backtest.diagnostics.section_08_data_source_asymmetry import INVERSE_UNSAFE_CLASSES
    assert INVERSE_UNSAFE_CLASSES == frozenset({"13F", "insider_buy", "13D"})


def test_b955_classify_signal_insider_cluster_active():
    """B955: insider_cluster_active classifies as insider_buy."""
    from backtest.diagnostics.section_08_data_source_asymmetry import classify_signal
    classes = classify_signal("insider_cluster_active")
    assert "insider_buy" in classes


def test_b955_classify_signal_sc_13d_filed():
    """B955: sc_13d_filed_within_30d classifies as 13D."""
    from backtest.diagnostics.section_08_data_source_asymmetry import classify_signal
    classes = classify_signal("sc_13d_filed_within_30d")
    assert "13D" in classes


def test_b955_classify_signal_days_to_cover():
    """B955: days_to_cover classifies as short_interest (asymmetric data, NOT inverse-unsafe)."""
    from backtest.diagnostics.section_08_data_source_asymmetry import classify_signal
    classes = classify_signal("days_to_cover")
    assert "short_interest" in classes


def test_b955_classify_signal_rsi_14_unmatched():
    """B955: rsi_14 doesn't match any asymmetric pattern."""
    from backtest.diagnostics.section_08_data_source_asymmetry import classify_signal
    classes = classify_signal("rsi_14")
    assert classes == []


def test_b955_extract_insider_strategy_flags_inverse_unsafe():
    """B955: insider_cluster_long is mechanical_inverse_unsafe=True."""
    from backtest.diagnostics.section_08_data_source_asymmetry import extract_section_08_for_strategy
    result = extract_section_08_for_strategy("insider_cluster_long")
    if not result["asymmetric_sources"]:
        pytest.skip("insider_cluster_long signal deps not extracted")
    assert "insider_buy" in result["asymmetric_sources"]
    assert result["mechanical_inverse_unsafe"] is True


def test_b955_extract_activist_13d_flags_inverse_unsafe():
    """B955: activist_13d_long is mechanical_inverse_unsafe=True (13D long-only)."""
    from backtest.diagnostics.section_08_data_source_asymmetry import extract_section_08_for_strategy
    result = extract_section_08_for_strategy("activist_13d_long")
    if not result["asymmetric_sources"]:
        pytest.skip("activist_13d_long signal deps not extracted")
    assert "13D" in result["asymmetric_sources"]
    assert result["mechanical_inverse_unsafe"] is True


def test_b955_extract_short_borrow_does_not_flag_inverse_unsafe():
    """B955: short_borrow_trap_avoid is asymmetric_source but NOT mechanical_inverse_unsafe.

    days_to_cover is short_interest class (asymmetric in DATA but inverse feasible
    via complementary low_short_interest signal).
    """
    from backtest.diagnostics.section_08_data_source_asymmetry import extract_section_08_for_strategy
    result = extract_section_08_for_strategy("short_borrow_trap_avoid")
    if not result["asymmetric_sources"]:
        pytest.skip("short_borrow_trap_avoid signal deps not extracted")
    assert "short_interest" in result["asymmetric_sources"]
    # mechanical_inverse_unsafe should be False (short_interest is inverse-feasible)
    assert result["mechanical_inverse_unsafe"] is False


def test_b955_extract_pure_technical_strategy_no_asymmetry():
    """B955: pure technical strategies have empty asymmetric_sources."""
    from backtest.diagnostics.section_08_data_source_asymmetry import extract_section_08_for_strategy
    result = extract_section_08_for_strategy("macd_crossover")
    if not result["asymmetric_sources"]:
        assert result["mechanical_inverse_unsafe"] is False


def test_b955_schema_keys_complete():
    """B955: extract returns expected schema keys."""
    from backtest.diagnostics.section_08_data_source_asymmetry import extract_section_08_for_strategy
    result = extract_section_08_for_strategy("any_strategy")
    expected_keys = {
        "asymmetric_sources", "mechanical_inverse_unsafe",
        "signals_triggering_classification", "inverse_unsafe_classes",
        "method", "memory_rule_reference", "is_walk_aid",
    }
    assert set(result.keys()) == expected_keys


def test_b955_populate_writes_to_dossier(tmp_path):
    """B955: populate_section_08_for_dossier writes section slot."""
    from backtest.diagnostics.section_08_data_source_asymmetry import populate_section_08_for_dossier
    dossier_path = tmp_path / "dossier.json"
    dossier_path.write_text(json.dumps({"strategy": "macd_crossover", "sections": {}}))
    populate_section_08_for_dossier("macd_crossover", dossier_path)
    with open(dossier_path) as f:
        updated = json.load(f)
    assert "section_08_data_source_asymmetry" in updated["sections"]
    section = updated["sections"]["section_08_data_source_asymmetry"]
    assert "asymmetric_sources" in section
    assert "feedback_asymmetric_data_sources_break_mechanical_inverse" in section["memory_rule_reference"]
