"""Pin tests for scripts/validate_pattern_w_candidates.py per Batch 759 +
S4-B755-COUNCIL-PATTERN-W-DELETE-BUNDLE-A-8-A-19-A-21.

# Source: scripts/validate_pattern_w_candidates.py (B759 build)
# per CHECKLIST #77 + #106 (council chairman recommendation).

Locks in:
- COUNCIL_DELETE_CANDIDATES inventory (the 3 council-named Pattern W cases)
- Threshold constants (Jaccard 0.85, phi 0.70 per B709, min n=30)
- _classify_pair_verdict logic per all 4 verdict classes
- _lookup_pair alphabetical-ordering convention
- Additional Pattern W surfacing (Jaccard >= 0.85 not in council list)
- Pattern J consolidation surfacing (phi >= 0.70)
"""
from __future__ import annotations

import pandas as pd
import pytest

from scripts.validate_pattern_w_candidates import (
    COUNCIL_DELETE_CANDIDATES,
    JACCARD_THRESHOLD_DELETE,
    JACCARD_THRESHOLD_MARGINAL,
    PHI_THRESHOLD_CONSOLIDATION,
    MIN_N_FOR_VALIDATION,
    _classify_pair_verdict,
    _lookup_pair,
    surface_additional_pattern_w,
    surface_pattern_j_candidates,
    validate_council_candidates,
)


# ---------------------------------------------------------------------------
# Pin 1: COUNCIL_DELETE_CANDIDATES has exactly 3 entries per B755-COUNCIL
# ---------------------------------------------------------------------------
def test_pin1_council_candidates_count_is_3():
    assert len(COUNCIL_DELETE_CANDIDATES) == 3


# ---------------------------------------------------------------------------
# Pin 2: All 3 council candidates have required fields
# ---------------------------------------------------------------------------
def test_pin2_council_candidates_schema():
    for c in COUNCIL_DELETE_CANDIDATES:
        assert "candidate_strategy" in c
        assert "vs_strategy" in c
        assert "direction" in c
        assert "council_verdict" in c
        assert "council_basis" in c
        assert c["direction"] in ("long", "short")


# ---------------------------------------------------------------------------
# Pin 3: A-19 (camarilla_rsi_obv_short) is in council list (HIGHEST CONFIDENCE)
# ---------------------------------------------------------------------------
def test_pin3_a19_camarilla_in_council_candidates():
    names = [c["candidate_strategy"] for c in COUNCIL_DELETE_CANDIDATES]
    assert "camarilla_rsi_obv_short" in names
    for c in COUNCIL_DELETE_CANDIDATES:
        if c["candidate_strategy"] == "camarilla_rsi_obv_short":
            assert c["council_verdict"] == "HIGHEST_CONFIDENCE_DELETE"


# ---------------------------------------------------------------------------
# Pin 4: All 3 expected candidates present (A-8 / A-19 / A-21)
# ---------------------------------------------------------------------------
def test_pin4_all_three_council_candidates_present():
    names = {c["candidate_strategy"] for c in COUNCIL_DELETE_CANDIDATES}
    expected = {
        "stochrsi_overbought_short",   # A-8
        "camarilla_rsi_obv_short",     # A-19
        "cpr_narrow_momentum_short",   # A-21
    }
    assert names == expected


# ---------------------------------------------------------------------------
# Pin 5: Threshold constants per chairman recommendation
# ---------------------------------------------------------------------------
def test_pin5_threshold_constants():
    assert JACCARD_THRESHOLD_DELETE == 0.85
    assert JACCARD_THRESHOLD_MARGINAL == 0.50
    assert PHI_THRESHOLD_CONSOLIDATION == 0.70  # B709 PEAD-restore precedent
    assert MIN_N_FOR_VALIDATION == 30


# ---------------------------------------------------------------------------
# Pin 6: _classify_pair_verdict CONFIRMED at Jaccard >= 0.85
# ---------------------------------------------------------------------------
def test_pin6_classify_confirmed():
    assert _classify_pair_verdict(0.85, 0.99, 100, 100) == "CONFIRMED"
    assert _classify_pair_verdict(0.99, 0.99, 100, 100) == "CONFIRMED"


# ---------------------------------------------------------------------------
# Pin 7: _classify_pair_verdict MARGINAL between 0.50 and 0.85 Jaccard
# ---------------------------------------------------------------------------
def test_pin7_classify_marginal():
    assert _classify_pair_verdict(0.60, 0.50, 100, 100) == "MARGINAL"
    assert _classify_pair_verdict(0.84, 0.70, 100, 100) == "MARGINAL"


# ---------------------------------------------------------------------------
# Pin 8: _classify_pair_verdict REJECTED at Jaccard < 0.50
# ---------------------------------------------------------------------------
def test_pin8_classify_rejected():
    assert _classify_pair_verdict(0.40, 0.30, 100, 100) == "REJECTED"


# ---------------------------------------------------------------------------
# Pin 9: _classify_pair_verdict INSUFFICIENT_DATA when n < min threshold
# ---------------------------------------------------------------------------
def test_pin9_classify_insufficient_data():
    assert _classify_pair_verdict(0.99, 0.99, 25, 100) == "INSUFFICIENT_DATA"
    assert _classify_pair_verdict(0.99, 0.99, 100, 25) == "INSUFFICIENT_DATA"


# ---------------------------------------------------------------------------
# Pin 10: _lookup_pair uses alphabetical ordering on strategy_a, strategy_b
# (compute_pairwise_similarity emits sorted pairs only)
# ---------------------------------------------------------------------------
def test_pin10_lookup_pair_alphabetical_normalization():
    df = pd.DataFrame([
        {"strategy_a": "alpha", "strategy_b": "beta", "direction": "long",
         "n_a": 100, "n_b": 100, "n_both": 90, "jaccard": 0.90,
         "phi_correlation": 0.80},
    ])
    # Lookup as (beta, alpha) should work via alphabetical normalization
    result = _lookup_pair(df, "beta", "alpha", "long")
    assert result is not None
    assert result["strategy_a"] == "alpha"
    assert result["strategy_b"] == "beta"


# ---------------------------------------------------------------------------
# Pin 11: _lookup_pair returns None when pair not found
# ---------------------------------------------------------------------------
def test_pin11_lookup_pair_not_found():
    df = pd.DataFrame(columns=[
        "strategy_a", "strategy_b", "direction",
        "n_a", "n_b", "n_both", "jaccard", "phi_correlation",
    ])
    result = _lookup_pair(df, "x", "y", "long")
    assert result is None


# ---------------------------------------------------------------------------
# Pin 12: validate_council_candidates returns NOT_FOUND_IN_SIMILARITY_MATRIX
# when input is empty
# ---------------------------------------------------------------------------
def test_pin12_validate_council_empty_similarity():
    df = pd.DataFrame(columns=[
        "strategy_a", "strategy_b", "direction",
        "n_a", "n_b", "n_both", "jaccard", "phi_correlation",
    ])
    results = validate_council_candidates(df)
    assert len(results) == 3  # all 3 council candidates returned
    for r in results:
        assert r["empirical_verdict"] == "NOT_FOUND_IN_SIMILARITY_MATRIX"


# ---------------------------------------------------------------------------
# Pin 13: validate_council_candidates A-19 CONFIRMED when Jaccard >= 0.85
# (synthesizes the council's HIGHEST_CONFIDENCE finding)
# ---------------------------------------------------------------------------
def test_pin13_validate_a19_confirmed_at_high_jaccard():
    df = pd.DataFrame([
        {"strategy_a": "camarilla_rsi_obv", "strategy_b": "camarilla_rsi_obv_short",
         "direction": "short",
         "n_a": 100, "n_b": 100, "n_both": 95, "jaccard": 0.95,
         "phi_correlation": 0.92},
    ])
    results = validate_council_candidates(df)
    a19 = [r for r in results if r["candidate_strategy"] == "camarilla_rsi_obv_short"]
    assert len(a19) == 1
    assert a19[0]["empirical_verdict"] == "CONFIRMED"
    assert a19[0]["agreement_with_council"] == "AGREES"


# ---------------------------------------------------------------------------
# Pin 14: validate_council_candidates DISAGREES when empirical Jaccard < 0.50
# (this is the Contrarian's concern: gate-text IDENTICAL but empirically NOT
# overlapping = silent-no-op gate bug, NOT a duplicate)
# ---------------------------------------------------------------------------
def test_pin14_validate_disagrees_when_empirical_low():
    df = pd.DataFrame([
        {"strategy_a": "camarilla_rsi_obv", "strategy_b": "camarilla_rsi_obv_short",
         "direction": "short",
         "n_a": 100, "n_b": 100, "n_both": 30, "jaccard": 0.20,
         "phi_correlation": 0.18},
    ])
    results = validate_council_candidates(df)
    a19 = [r for r in results if r["candidate_strategy"] == "camarilla_rsi_obv_short"][0]
    assert a19["empirical_verdict"] == "REJECTED"
    assert a19["agreement_with_council"] == "DISAGREES"


# ---------------------------------------------------------------------------
# Pin 15: surface_additional_pattern_w finds Jaccard >= 0.85 pairs
# NOT in council list
# ---------------------------------------------------------------------------
def test_pin15_surface_additional_pattern_w_finds_new_duplicates():
    df = pd.DataFrame([
        {"strategy_a": "new_strat_a", "strategy_b": "new_strat_b",
         "direction": "long",
         "n_a": 100, "n_b": 100, "n_both": 92, "jaccard": 0.92,
         "phi_correlation": 0.85},
    ])
    council_keys = set()  # empty -- council didn't name this pair
    results = surface_additional_pattern_w(df, council_keys)
    assert len(results) == 1
    assert results[0]["strategy_a"] == "new_strat_a"
    assert results[0]["verdict"] == "DELETE_CANDIDATE_NEW"


# ---------------------------------------------------------------------------
# Pin 16: surface_additional_pattern_w SKIPS pairs already in council list
# ---------------------------------------------------------------------------
def test_pin16_surface_additional_skips_council_pairs():
    df = pd.DataFrame([
        {"strategy_a": "camarilla_rsi_obv", "strategy_b": "camarilla_rsi_obv_short",
         "direction": "short",
         "n_a": 100, "n_b": 100, "n_both": 95, "jaccard": 0.95,
         "phi_correlation": 0.92},
    ])
    council_keys = {tuple(sorted(["camarilla_rsi_obv", "camarilla_rsi_obv_short"])) + ("short",)}
    results = surface_additional_pattern_w(df, council_keys)
    assert len(results) == 0  # council-named pair excluded


# ---------------------------------------------------------------------------
# Pin 17: surface_pattern_j_candidates finds phi >= 0.70 pairs
# (B709 PEAD-restore threshold)
# ---------------------------------------------------------------------------
def test_pin17_surface_pattern_j_finds_consolidation():
    df = pd.DataFrame([
        {"strategy_a": "x", "strategy_b": "y", "direction": "long",
         "n_a": 100, "n_b": 100, "n_both": 60, "jaccard": 0.40,
         "phi_correlation": 0.75},
    ])
    results = surface_pattern_j_candidates(df)
    assert len(results) == 1
    assert results[0]["verdict"] == "CONSOLIDATION_CANDIDATE"


# ---------------------------------------------------------------------------
# Pin 18: surface_pattern_j_candidates excludes phi < 0.70
# ---------------------------------------------------------------------------
def test_pin18_surface_pattern_j_excludes_below_threshold():
    df = pd.DataFrame([
        {"strategy_a": "x", "strategy_b": "y", "direction": "long",
         "n_a": 100, "n_b": 100, "n_both": 20, "jaccard": 0.15,
         "phi_correlation": 0.45},
    ])
    results = surface_pattern_j_candidates(df)
    assert len(results) == 0


# ---------------------------------------------------------------------------
# Pin 19: surface_pattern_j_candidates sorts by phi descending
# (highest-correlation pairs surfaced first)
# ---------------------------------------------------------------------------
def test_pin19_surface_pattern_j_sorted_by_phi_desc():
    df = pd.DataFrame([
        {"strategy_a": "a", "strategy_b": "b", "direction": "long",
         "n_a": 100, "n_b": 100, "n_both": 50, "jaccard": 0.30,
         "phi_correlation": 0.72},
        {"strategy_a": "c", "strategy_b": "d", "direction": "long",
         "n_a": 100, "n_b": 100, "n_both": 70, "jaccard": 0.50,
         "phi_correlation": 0.95},
    ])
    results = surface_pattern_j_candidates(df)
    assert len(results) == 2
    # Higher phi first
    assert results[0]["phi"] == 0.95
    assert results[1]["phi"] == 0.72
