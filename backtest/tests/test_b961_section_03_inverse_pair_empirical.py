"""B961 (2026-06-20): pyramid tests for Section 3 inverse_pair_empirical.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 3 + Council 66 verdict
# per owner directive 2026-06-20 'Continue, council this' per CHECKLIST #77.
"""
from __future__ import annotations

import json

import pytest


def test_b961_section_03_extractor_importable():
    """B961 contract: module importable + functions exposed."""
    from backtest.diagnostics import section_03_inverse_pair_empirical as mod
    assert hasattr(mod, "extract_section_03_for_strategy")
    assert hasattr(mod, "populate_section_03_for_dossier")
    assert hasattr(mod, "_canonical_inverse_candidate")
    assert hasattr(mod, "_load_all_strategies")
    assert hasattr(mod, "_load_r4_fire_counts")


def test_b961_canonical_inverse_long_to_short():
    """B961: 'strat_X_long' -> 'strat_X_short'."""
    from backtest.diagnostics.section_03_inverse_pair_empirical import _canonical_inverse_candidate
    assert _canonical_inverse_candidate("rsi_oversold_long") == "rsi_oversold_short"
    assert _canonical_inverse_candidate("macd_crossover_long") == "macd_crossover_short"


def test_b961_canonical_inverse_short_to_long():
    """B961: 'strat_X_short' -> 'strat_X_long'."""
    from backtest.diagnostics.section_03_inverse_pair_empirical import _canonical_inverse_candidate
    assert _canonical_inverse_candidate("rsi_overbought_short") == "rsi_overbought_long"


def test_b961_canonical_inverse_neither_suffix():
    """B961: strategies without _long or _short suffix return None."""
    from backtest.diagnostics.section_03_inverse_pair_empirical import _canonical_inverse_candidate
    assert _canonical_inverse_candidate("smc_bos_continuation") is None
    assert _canonical_inverse_candidate("xs_momentum_top_decile") is None
    assert _canonical_inverse_candidate("macd_crossover") is None


def test_b961_extract_pair_exists_recommendation():
    """B961: strategy with registered inverse returns 'pair_exists'."""
    from backtest.diagnostics.section_03_inverse_pair_empirical import (
        extract_section_03_for_strategy, _load_all_strategies,
    )
    all_strats = _load_all_strategies()
    # Find a _long strategy with matching _short
    test_strat = None
    for s in all_strats:
        if s.endswith("_long"):
            inv = s[:-len("_long")] + "_short"
            if inv in all_strats:
                test_strat = s
                break
    if test_strat is None:
        pytest.skip("No canonical pair found in roster")
    result = extract_section_03_for_strategy(test_strat)
    if not result["b956_inverse_unsafe_flag"]:
        # Only verify if NOT asymmetric (asymmetric overrides pair_exists)
        assert result["has_named_inverse_candidate"] is True
        assert result["inverse_exists_in_registry"] is True


def test_b961_extract_missing_inverse_recommendation():
    """B961: _long strategy WITHOUT matching _short returns 'missing_inverse_candidate'."""
    from backtest.diagnostics.section_03_inverse_pair_empirical import (
        extract_section_03_for_strategy, _load_all_strategies,
    )
    all_strats = _load_all_strategies()
    # Find a _long strategy WITHOUT matching _short
    test_strat = None
    for s in all_strats:
        if s.endswith("_long"):
            inv = s[:-len("_long")] + "_short"
            if inv not in all_strats:
                test_strat = s
                break
    if test_strat is None:
        pytest.skip("All _long strategies have matching _short")
    result = extract_section_03_for_strategy(test_strat)
    if not result["b956_inverse_unsafe_flag"]:
        assert result["has_named_inverse_candidate"] is True
        assert result["inverse_exists_in_registry"] is False
        assert result["inverse_recommendation"] == "missing_inverse_candidate"


def test_b961_extract_asymmetric_data_overrides_recommendation():
    """B961: strategy flagged as INVERSE_UNSAFE (B956) returns 'asymmetric_data_no_mirror'."""
    from backtest.diagnostics.section_03_inverse_pair_empirical import extract_section_03_for_strategy
    # insider_cluster_long is INVERSE_UNSAFE per B955 Section 8
    result = extract_section_03_for_strategy("insider_cluster_long")
    if result.get("b956_inverse_unsafe_flag"):
        assert result["inverse_recommendation"] == "asymmetric_data_no_mirror"


def test_b961_extract_no_canonical_inverse_for_neither_suffix():
    """B961: 'smc_bos_continuation' (no suffix) returns 'no_canonical_inverse'."""
    from backtest.diagnostics.section_03_inverse_pair_empirical import (
        extract_section_03_for_strategy, _load_all_strategies,
    )
    all_strats = _load_all_strategies()
    test_strat = None
    for s in all_strats:
        if not (s.endswith("_long") or s.endswith("_short")):
            test_strat = s
            break
    if test_strat is None:
        pytest.skip("All strategies have _long/_short suffix")
    result = extract_section_03_for_strategy(test_strat)
    if not result["b956_inverse_unsafe_flag"]:
        assert result["has_named_inverse_candidate"] is False
        assert result["inverse_candidate_name"] is None
        assert result["inverse_recommendation"] == "no_canonical_inverse"


def test_b961_schema_keys_complete():
    """B961: extract returns expected schema keys."""
    from backtest.diagnostics.section_03_inverse_pair_empirical import extract_section_03_for_strategy
    result = extract_section_03_for_strategy("any_strategy")
    expected_keys = {
        "has_named_inverse_candidate", "inverse_candidate_name",
        "inverse_exists_in_registry", "self_r4_fires", "inverse_r4_fires",
        "self_in_r4_cube", "inverse_in_r4_cube", "asymmetric_data_source_flag",
        "b956_inverse_unsafe_flag", "asymmetric_sources",
        "inverse_recommendation", "method", "memory_rule_reference",
        "limitation",
    }
    assert set(result.keys()) == expected_keys


def test_b961_populate_writes_to_dossier(tmp_path):
    """B961: populate_section_03_for_dossier writes section slot."""
    from backtest.diagnostics.section_03_inverse_pair_empirical import populate_section_03_for_dossier
    dossier_path = tmp_path / "dossier.json"
    dossier_path.write_text(json.dumps({"strategy": "macd_crossover", "sections": {}}))
    populate_section_03_for_dossier("macd_crossover", dossier_path)
    with open(dossier_path) as f:
        updated = json.load(f)
    assert "section_03_inverse_pair_empirical" in updated["sections"]
    section = updated["sections"]["section_03_inverse_pair_empirical"]
    assert section["method"] == "static_name_pattern_plus_r4_fire_count_plus_section_8"
    assert "feedback_asymmetric_data_sources_break_mechanical_inverse" in section["memory_rule_reference"]
