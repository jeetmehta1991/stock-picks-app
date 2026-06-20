"""B943 (2026-06-20): pyramid tests for R4 pass-through bundle (sections 10/11/12/18).

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 + Council 48 batch 4 commit 2.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


# --- Section 10 cost-sensitivity ----

def test_b943_section_10_post_r4_returns_track_2_sentinel():
    """B943 Section 10: post-R4 strategy returns TRACK 2 sentinel."""
    from backtest.diagnostics.section_r4_passthrough import extract_section_10_cost_sensitivity
    result = extract_section_10_cost_sensitivity("_nonexistent_post_r4_canary")
    assert result["r4_status"] == "post_r4_addition"
    assert result["value"] is None
    assert result["evidence_source"] == "section_9b"


def test_b943_section_10_in_r4_returns_ratio():
    """B943 Section 10: in-R4 strategy returns cost-sensitivity ratio."""
    from backtest.diagnostics.section_r4_passthrough import extract_section_10_cost_sensitivity
    result = extract_section_10_cost_sensitivity("donchian_10_breakout")
    assert result["r4_status"] == "in_r4_cube"
    # If non-zero sharpe_at_0bps, value is computed
    if result.get("value") is not None:
        assert "sharpe_at_0bps" in result
        assert "passes_dec_612_gate" in result


# --- Section 11 Chow break ---

def test_b943_section_11_post_r4_returns_track_2_sentinel():
    """B943 Section 11: post-R4 strategy returns TRACK 2 sentinel."""
    from backtest.diagnostics.section_r4_passthrough import extract_section_11_chow_break_point
    result = extract_section_11_chow_break_point("_nonexistent_post_r4_canary")
    assert result["r4_status"] == "post_r4_addition"


def test_b943_section_11_in_r4_has_passes_gate_field():
    """B943 Section 11: in-R4 returns passes_dec_613_gate field."""
    from backtest.diagnostics.section_r4_passthrough import extract_section_11_chow_break_point
    result = extract_section_11_chow_break_point("donchian_10_breakout")
    assert result["r4_status"] == "in_r4_cube"
    assert "passes_dec_613_gate" in result


# --- Section 12 ADF ---

def test_b943_section_12_post_r4_returns_track_2_sentinel():
    """B943 Section 12: post-R4 strategy returns TRACK 2 sentinel."""
    from backtest.diagnostics.section_r4_passthrough import extract_section_12_adf
    result = extract_section_12_adf("_nonexistent_post_r4_canary")
    assert result["r4_status"] == "post_r4_addition"


def test_b943_section_12_mean_rev_strategy_marked():
    """B943 Section 12: mean-rev strategy flagged is_mean_reversion_strategy=True."""
    from backtest.diagnostics.section_r4_passthrough import extract_section_12_adf
    # mfi_oversold is in MEAN_REVERSION_STRATEGIES per CLAUDE.md
    result = extract_section_12_adf("mfi_oversold")
    if result["r4_status"] == "in_r4_cube":
        assert result["is_mean_reversion_strategy"] is True


# --- Section 18 per-regime Sharpe dispersion ---

def test_b943_section_18_post_r4_returns_track_2_sentinel():
    """B943 Section 18: post-R4 strategy returns TRACK 2 sentinel."""
    from backtest.diagnostics.section_r4_passthrough import extract_section_18_per_regime_sharpe_dispersion
    result = extract_section_18_per_regime_sharpe_dispersion("_nonexistent_post_r4_canary")
    assert result["r4_status"] == "post_r4_addition"


def test_b943_section_18_in_r4_returns_dispersion_or_reason():
    """B943 Section 18: in-R4 returns dispersion value OR reason for missing."""
    from backtest.diagnostics.section_r4_passthrough import extract_section_18_per_regime_sharpe_dispersion
    result = extract_section_18_per_regime_sharpe_dispersion("donchian_10_breakout")
    assert result["r4_status"] == "in_r4_cube"
    # Either value populated OR reason explains why
    assert "value" in result


# --- Round-trip populate ---

def test_b943_populate_all_4_sections_round_trip():
    """B943 populate-then-read: all 4 sections persist in JSON."""
    from scripts.dossier_build import init_dossier, DOSSIERS_DIR
    from backtest.diagnostics.section_r4_passthrough import populate_r4_passthrough_sections_for_dossier

    test_strategy = "_test_b943_r4_passthrough_canary"
    try:
        dossier_path = init_dossier(test_strategy, overwrite=True)
        populate_r4_passthrough_sections_for_dossier(test_strategy, dossier_path)
        with open(dossier_path) as f:
            dossier = json.load(f)
        # All 4 sections populated (with TRACK 2 sentinels since canary not in R4)
        for key in [
            "section_10_cost_sensitivity_ratio",
            "section_11_chow_break_point",
            "section_12_adf_p_value",
            "section_18_per_regime_sharpe_dispersion",
        ]:
            assert dossier["sections"][key] is not None, f"{key} not populated"
            assert dossier["sections"][key]["r4_status"] == "post_r4_addition"
    finally:
        test_dir = DOSSIERS_DIR / test_strategy
        if test_dir.exists():
            for child in test_dir.iterdir():
                child.unlink()
            test_dir.rmdir()
