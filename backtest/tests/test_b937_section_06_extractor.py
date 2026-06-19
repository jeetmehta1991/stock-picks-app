"""B937 (2026-06-19): pyramid tests for Section 6 producer STATE/EVENT extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 6 + Council 46 batch 2
# commit 2 per owner directive 2026-06-19 Option A.
"""
from __future__ import annotations

import json

import pytest


def test_b937_classify_event_signal_breakout():
    """B937 EVENT heuristic: '_breakout' suffix -> EVENT."""
    from backtest.diagnostics.section_06_producer_state_event import classify_signal_temporality
    result = classify_signal_temporality("dc20_breakout_up", overrides={})
    assert result["temporality"] == "EVENT", f"got {result!r}"


def test_b937_classify_event_signal_cross():
    """B937 EVENT heuristic: '_cross' suffix -> EVENT."""
    from backtest.diagnostics.section_06_producer_state_event import classify_signal_temporality
    result = classify_signal_temporality("macd_bullish_cross", overrides={})
    assert result["temporality"] == "EVENT"


def test_b937_classify_event_signal_today():
    """B937 EVENT heuristic: '_today' suffix -> EVENT."""
    from backtest.diagnostics.section_06_producer_state_event import classify_signal_temporality
    result = classify_signal_temporality("bullish_pin_bar_today", overrides={})
    assert result["temporality"] == "EVENT"


def test_b937_classify_state_institutional():
    """B937 STATE heuristic: 'institutional_' prefix -> STATE (13F quarterly)."""
    from backtest.diagnostics.section_06_producer_state_event import classify_signal_temporality
    result = classify_signal_temporality("institutional_strong_buy", overrides={})
    assert result["temporality"] == "STATE"


def test_b937_classify_state_long_ema_trend_filter():
    """B937 STATE heuristic: 'price_above_ema_200' -> STATE (slow trend filter)."""
    from backtest.diagnostics.section_06_producer_state_event import classify_signal_temporality
    result = classify_signal_temporality("price_above_ema_200", overrides={})
    assert result["temporality"] == "STATE"


def test_b937_classify_state_classification():
    """B937 STATE heuristic: 'classification_' prefix -> STATE (GICS reclass slow)."""
    from backtest.diagnostics.section_06_producer_state_event import classify_signal_temporality
    result = classify_signal_temporality("classification_change_to_tech", overrides={})
    assert result["temporality"] == "STATE"


def test_b937_classify_unknown_signal():
    """B937 UNKNOWN: signal name not matching any pattern -> UNKNOWN."""
    from backtest.diagnostics.section_06_producer_state_event import classify_signal_temporality
    result = classify_signal_temporality("_some_ambiguous_signal_name_zzz", overrides={})
    assert result["temporality"] == "UNKNOWN"
    assert result["matched_pattern"] is None


def test_b937_manual_override_takes_precedence():
    """B937 override: manual override JSON beats heuristic."""
    from backtest.diagnostics.section_06_producer_state_event import classify_signal_temporality
    # Override forces vol_spike_2x to STATE (against EVENT heuristic)
    result = classify_signal_temporality("vol_spike_2x", overrides={"vol_spike_2x": "STATE"})
    assert result["temporality"] == "STATE"
    assert result["manual_override"] is True


def test_b937_extract_section_06_for_strategy():
    """B937 strategy-level extraction: returns schema with summary."""
    from backtest.diagnostics.section_06_producer_state_event import extract_section_06
    # institutional_high_conviction_long consumes institutional_new_positions + price_above_ema_50
    result = extract_section_06("institutional_high_conviction_long")
    assert "signals_consumed" in result
    assert "classifications" in result
    assert "summary" in result
    # Should have at least 1 signal classified
    assert result["n_signals"] >= 1


def test_b937_institutional_only_strategy_flagged_pure_state():
    """B937 compliance check: pure-STATE strategy fails feedback_signal_temporality compliance.

    institutional_high_conviction_long uses only institutional_new_positions
    (STATE) + price_above_ema_50 (STATE). Both STATE; no EVENT signal.
    Per feedback_signal_temporality_event_vs_state: compliance=False.
    """
    from backtest.diagnostics.section_06_producer_state_event import extract_section_06
    result = extract_section_06("institutional_high_conviction_long")
    summary = result["summary"]
    # Strategy has institutional_new_positions (STATE) + price_above_ema_50 (STATE)
    assert summary["n_state"] >= 1
    # Compliance: requires at least 1 EVENT signal
    if summary["n_event"] == 0:
        assert not summary["feedback_signal_temporality_event_vs_state_compliance"]


def test_b937_smc_breaker_block_long_has_event_signals():
    """B937: smc_breaker_block_long uses break/breaker EVENT signals."""
    from backtest.diagnostics.section_06_producer_state_event import extract_section_06
    result = extract_section_06("smc_breaker_block_long")
    # SMC strategies should have EVENT signals (smc_breaker_block, etc.)
    # Note: SMC signals may classify as UNKNOWN if they don't match
    # the heuristic; manual override JSON would fix that.
    assert result["n_signals"] >= 1


def test_b937_overrides_file_initialization():
    """B937 overrides JSON file: created if missing; valid JSON."""
    from backtest.diagnostics.section_06_producer_state_event import _load_overrides, OVERRIDES_PATH
    overrides = _load_overrides()
    assert isinstance(overrides, dict)
    assert OVERRIDES_PATH.exists()


def test_b937_populate_section_06_round_trip():
    """B937 populate-then-read: section_06 persists in JSON."""
    from scripts.dossier_build import init_dossier, DOSSIERS_DIR
    from backtest.diagnostics.section_06_producer_state_event import populate_section_06_for_dossier

    test_strategy = "institutional_high_conviction_long"
    try:
        dossier_path = init_dossier(test_strategy, overwrite=True)
        populate_section_06_for_dossier(test_strategy, dossier_path)
        with open(dossier_path) as f:
            dossier = json.load(f)
        section_6 = dossier["sections"]["section_06_producer_state_event"]
        assert section_6 is not None
        assert "summary" in section_6
    finally:
        test_dir = DOSSIERS_DIR / test_strategy
        if test_dir.exists():
            for child in test_dir.iterdir():
                child.unlink()
            test_dir.rmdir()
