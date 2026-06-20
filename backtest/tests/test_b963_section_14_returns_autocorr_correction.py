"""B963 (2026-06-20): pyramid tests for Section 14 returns_autocorr_correction.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 14 + Council 67 verdict
# per owner directive 2026-06-20 autonomous mandate per CHECKLIST #77.
"""
from __future__ import annotations

import json

import numpy as np
import pytest


def test_b963_section_14_extractor_importable():
    """B963 contract: module importable + functions exposed."""
    from backtest.diagnostics import section_14_returns_autocorr_correction as mod
    assert hasattr(mod, "extract_section_14_for_strategy")
    assert hasattr(mod, "populate_section_14_for_dossier")
    assert hasattr(mod, "_compute_lo_2002_correction")
    assert hasattr(mod, "_load_r4_trade_log_grouped")


def test_b963_r4_trade_log_loads():
    """B963: R4 trade_log loads + has > 50 strategies."""
    from backtest.diagnostics.section_14_returns_autocorr_correction import _load_r4_trade_log_grouped
    grouped = _load_r4_trade_log_grouped()
    assert len(grouped) > 50, f"Expected >50 strategies in R4 trade_log, got {len(grouped)}"


def test_b963_lo_correction_small_sample_returns_nulls():
    """B963: Lo correction on n<30 returns None values (insufficient sample)."""
    from backtest.diagnostics.section_14_returns_autocorr_correction import _compute_lo_2002_correction
    result = _compute_lo_2002_correction([0.01, -0.005, 0.003])  # n=3
    assert result["n_trades"] == 3
    assert result["raw_sharpe"] is None
    assert result["rho1"] is None
    assert result["effective_n"] is None
    assert result["corrected_sharpe"] is None


def test_b963_lo_correction_iid_returns_rho1_near_zero():
    """B963: IID Gaussian returns produce rho1 close to 0; corrected ~= raw."""
    from backtest.diagnostics.section_14_returns_autocorr_correction import _compute_lo_2002_correction
    np.random.seed(42)
    pnls = np.random.randn(500).tolist()
    result = _compute_lo_2002_correction(pnls)
    assert result["n_trades"] == 500
    assert result["rho1"] is not None
    # IID should produce |rho1| small
    assert abs(result["rho1"]) < 0.15, f"IID rho1={result['rho1']} too large"
    # Effective_n close to actual n
    assert abs(result["effective_n"] - 500) < 200, f"effective_n={result['effective_n']} far from 500"


def test_b963_lo_correction_positive_autocorr_reduces_effective_n():
    """B963: AR(1) positive autocorrelation reduces n_eff vs n."""
    from backtest.diagnostics.section_14_returns_autocorr_correction import _compute_lo_2002_correction
    np.random.seed(123)
    # Generate AR(1) with rho=0.5
    n = 500
    eps = np.random.randn(n)
    pnls = np.zeros(n)
    for i in range(1, n):
        pnls[i] = 0.5 * pnls[i - 1] + eps[i]
    result = _compute_lo_2002_correction(pnls.tolist())
    assert result["rho1"] > 0.3, f"AR(1) rho=0.5 measured rho1={result['rho1']}"
    # Lo formula: n_eff = n * (1 - 0.5) / (1 + 0.5) = n / 3
    # Allow generous tolerance for sample variation
    assert result["effective_n"] < 400, f"effective_n={result['effective_n']} should be << 500"


def test_b963_extract_strategy_in_r4_returns_populated():
    """B963: a strategy in R4 trade_log returns populated per-regime + overall."""
    from backtest.diagnostics.section_14_returns_autocorr_correction import (
        extract_section_14_for_strategy,
        _load_r4_trade_log_grouped,
    )
    grouped = _load_r4_trade_log_grouped()
    test_strat = None
    for s, regimes in grouped.items():
        total = sum(len(v) for v in regimes.values())
        if total >= 30:
            test_strat = s
            break
    if test_strat is None:
        pytest.skip("No strategy with >=30 trades in R4 trade_log")
    result = extract_section_14_for_strategy(test_strat)
    assert result["in_r4_trade_log"] is True
    assert result["n_trades_total"] >= 30
    assert result["raw_sharpe_overall"] is not None
    assert result["corrected_sharpe_overall"] is not None
    assert isinstance(result["per_regime"], dict)


def test_b963_extract_unknown_strategy_returns_not_in_r4():
    """B963: unknown strategy returns in_r4_trade_log=False."""
    from backtest.diagnostics.section_14_returns_autocorr_correction import extract_section_14_for_strategy
    result = extract_section_14_for_strategy("nonexistent_strategy_xyz_456")
    assert result["in_r4_trade_log"] is False
    assert result["n_trades_total"] == 0
    assert result["corrected_sharpe_overall"] is None


def test_b963_re_pass_thresholds_match_claude_md():
    """B963: re-pass thresholds are 1.0 overall + 0.7 per-regime per CLAUDE.md."""
    from backtest.diagnostics.section_14_returns_autocorr_correction import (
        SHARPE_OVERALL_PASS, SHARPE_PER_REGIME_PASS,
    )
    assert SHARPE_OVERALL_PASS == 1.0
    assert SHARPE_PER_REGIME_PASS == 0.7


def test_b963_schema_keys_complete():
    """B963: extract returns expected schema keys."""
    from backtest.diagnostics.section_14_returns_autocorr_correction import extract_section_14_for_strategy
    result = extract_section_14_for_strategy("any_strategy")
    expected_keys = {
        "in_r4_trade_log", "n_trades_total", "raw_sharpe_overall",
        "rho1_overall", "effective_n_overall", "corrected_sharpe_overall",
        "corrected_sharpe_overall_re_pass", "per_regime",
        "sharpe_inflation_pct_overall", "method", "source", "limitation",
        "memory_rule_reference",
    }
    assert set(result.keys()) == expected_keys


def test_b963_populate_writes_to_dossier(tmp_path):
    """B963: populate_section_14_for_dossier writes section slot."""
    from backtest.diagnostics.section_14_returns_autocorr_correction import populate_section_14_for_dossier
    dossier_path = tmp_path / "dossier.json"
    dossier_path.write_text(json.dumps({"strategy": "any", "sections": {}}))
    populate_section_14_for_dossier("any", dossier_path)
    with open(dossier_path) as f:
        dossier = json.load(f)
    assert "section_14_returns_autocorr_correction" in dossier["sections"]


def test_b963_per_regime_re_pass_flag_consistent():
    """B963: per-regime corrected_sharpe_re_pass flag matches the >= 0.7 threshold."""
    from backtest.diagnostics.section_14_returns_autocorr_correction import (
        extract_section_14_for_strategy,
        _load_r4_trade_log_grouped,
        SHARPE_PER_REGIME_PASS,
    )
    grouped = _load_r4_trade_log_grouped()
    test_strat = None
    for s, regimes in grouped.items():
        if any(len(v) >= 30 for v in regimes.values()):
            test_strat = s
            break
    if test_strat is None:
        pytest.skip("No strategy with regime n>=30 in R4")
    result = extract_section_14_for_strategy(test_strat)
    for regime, cell in result["per_regime"].items():
        if cell["corrected_sharpe"] is not None:
            expected_pass = cell["corrected_sharpe"] >= SHARPE_PER_REGIME_PASS
            assert cell["corrected_sharpe_re_pass"] == expected_pass, (
                f"regime={regime} corrected={cell['corrected_sharpe']} "
                f"re_pass={cell['corrected_sharpe_re_pass']} != expected={expected_pass}"
            )
