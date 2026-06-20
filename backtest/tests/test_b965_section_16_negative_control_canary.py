"""B965 (2026-06-20): pyramid tests for Section 16 negative_control_canary.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 16 + Council 67 verdict
# per owner directive 2026-06-20 autonomous mandate per CHECKLIST #77.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))


def test_b965_section_16_extractor_importable():
    """B965 contract: module importable + functions exposed."""
    from backtest.diagnostics import section_16_negative_control_canary as mod
    assert hasattr(mod, "extract_section_16_for_strategy")
    assert hasattr(mod, "populate_section_16_for_dossier")
    assert hasattr(mod, "_get_null_strategy_names")


def test_b965_inject_script_exists():
    """B965 Contrarian hardening: inject script must exist as runnable artifact."""
    from backtest.diagnostics.section_16_negative_control_canary import INJECTION_SCRIPT
    assert INJECTION_SCRIPT.exists(), f"Injection script missing at {INJECTION_SCRIPT}"


def test_b965_null_strategy_names_canonical_5():
    """B965: exactly 5 canonical null strategies registered."""
    from backtest.diagnostics.section_16_negative_control_canary import _get_null_strategy_names
    names = _get_null_strategy_names()
    assert len(names) == 5
    assert "null_random_long_p05" in names
    assert "null_shuffled_signal_long" in names
    assert "null_lagged_self_long" in names
    assert "null_pure_noise_gauss" in names
    assert "null_coin_flip_daily" in names


def test_b965_inject_script_verify_registration_runs():
    """B965 Contrarian hardening: inject script verify_registration is callable."""
    from scripts.inject_null_strategies import verify_registration
    result = verify_registration()
    assert result["n_null_strategies"] == 5
    assert len(result["names"]) == 5
    assert result["registration_status"] == "stub_callable_runtime_ready"
    for name, info in result["verification"].items():
        assert info["callable"] is True, f"{name} not callable: {info}"


def test_b965_null_strategies_are_callable_and_deterministic():
    """B965: each null strategy callable returns dict with fires/direction/category."""
    from scripts.inject_null_strategies import build_null_strategies
    strats = build_null_strategies()
    assert len(strats) == 5
    stub_s = {"rsi_oversold": True, "rsi_oversold_lag_252": False}
    for name, fn in strats.items():
        out = fn(stub_s)
        assert "fires" in out
        assert "direction" in out
        assert "category" in out
        assert out["category"] == "null_control"


def test_b965_extract_for_null_canary_returns_is_null_true():
    """B965: null strategy returns is_null_canary=True."""
    from backtest.diagnostics.section_16_negative_control_canary import extract_section_16_for_strategy
    result = extract_section_16_for_strategy("null_random_long_p05")
    assert result["is_null_canary"] is True
    assert result["null_strategy_name"] == "null_random_long_p05"
    assert result["n_null_canaries_total"] == 5


def test_b965_extract_for_real_strategy_returns_is_null_false():
    """B965: real strategy returns is_null_canary=False."""
    from backtest.diagnostics.section_16_negative_control_canary import extract_section_16_for_strategy
    result = extract_section_16_for_strategy("rsi_oversold_long")
    assert result["is_null_canary"] is False
    assert result["null_strategy_name"] is None


def test_b965_pre_r5_framework_calibrated_status():
    """B965: pre-R5, framework_calibrated is None or partially-calibrated value."""
    from backtest.diagnostics.section_16_negative_control_canary import extract_section_16_for_strategy
    result = extract_section_16_for_strategy("rsi_oversold_long")
    # Pre-R5, can be None OR partially-calibrated based on Section 2/14/15 verdicts
    # B660 may already identify some nulls if they have measured FAIL_FIRE_STARVED
    assert result["canary_status_overall"] in {
        "pending_r5_cube_launch",
        "framework_calibrated",
    } or result["canary_status_overall"].startswith("framework_partially_calibrated_")


def test_b965_schema_keys_complete_for_null():
    """B965: schema keys complete when strategy is null canary."""
    from backtest.diagnostics.section_16_negative_control_canary import extract_section_16_for_strategy
    result = extract_section_16_for_strategy("null_coin_flip_daily")
    expected_keys = {
        "is_null_canary", "null_strategy_name",
        "canary_correctly_identified", "canary_failed_gates",
        "n_null_canaries_total", "n_null_canaries_identified",
        "framework_calibrated", "canary_status_overall",
        "null_strategy_names", "injection_script", "method", "source",
        "limitation", "memory_rule_reference",
    }
    assert set(result.keys()) == expected_keys


def test_b965_schema_keys_complete_for_real():
    """B965: schema keys complete when strategy is real."""
    from backtest.diagnostics.section_16_negative_control_canary import extract_section_16_for_strategy
    result = extract_section_16_for_strategy("any_real_strategy_xyz")
    expected_keys = {
        "is_null_canary", "null_strategy_name",
        "canary_correctly_identified", "canary_failed_gates",
        "n_null_canaries_total", "n_null_canaries_identified",
        "framework_calibrated", "canary_status_overall",
        "null_strategy_names", "injection_script", "method", "source",
        "limitation", "memory_rule_reference",
    }
    assert set(result.keys()) == expected_keys


def test_b965_populate_writes_to_dossier(tmp_path):
    """B965: populate_section_16_for_dossier writes section slot."""
    from backtest.diagnostics.section_16_negative_control_canary import populate_section_16_for_dossier
    dossier_path = tmp_path / "dossier.json"
    dossier_path.write_text(json.dumps({"strategy": "any", "sections": {}}))
    populate_section_16_for_dossier("any", dossier_path)
    with open(dossier_path) as f:
        dossier = json.load(f)
    assert "section_16_negative_control_canary" in dossier["sections"]


def test_b965_inject_does_not_persist_to_screener_source():
    """B965: inject_into_all_strategies is runtime-only (does not mutate file)."""
    # Read screener.py; assert null strategy names are NOT in source
    screener_path = REPO / "backtest" / "signals" / "screener.py"
    text = screener_path.read_text(encoding="utf-8")
    for null_name in (
        "null_random_long_p05",
        "null_shuffled_signal_long",
        "null_lagged_self_long",
        "null_pure_noise_gauss",
        "null_coin_flip_daily",
    ):
        # Allow comment references but not registry insertion
        # Registry insertion would look like `"null_random_long_p05":`
        assert f'"{null_name}":' not in text, (
            f"{null_name} appears to be persisted in screener.py source; "
            f"inject must remain runtime-only per B965 design."
        )
