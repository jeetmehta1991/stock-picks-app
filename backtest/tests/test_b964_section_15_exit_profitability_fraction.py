"""B964 (2026-06-20): pyramid tests for Section 15 exit_profitability_fraction.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 15 + Council 67 verdict
# per owner directive 2026-06-20 autonomous mandate per CHECKLIST #77.
"""
from __future__ import annotations

import json

import pytest


def test_b964_section_15_extractor_importable():
    """B964 contract: module importable + functions exposed."""
    from backtest.diagnostics import section_15_exit_profitability_fraction as mod
    assert hasattr(mod, "extract_section_15_for_strategy")
    assert hasattr(mod, "populate_section_15_for_dossier")
    assert hasattr(mod, "_sharpe_proxy")
    assert hasattr(mod, "_load_r4_trade_log_by_strategy_exit")


def test_b964_r4_trade_log_loads_grouped():
    """B964: R4 trade_log loads grouped by strategy/exit + has >50 strategies."""
    from backtest.diagnostics.section_15_exit_profitability_fraction import _load_r4_trade_log_by_strategy_exit
    grouped = _load_r4_trade_log_by_strategy_exit()
    assert len(grouped) > 50, f"Expected >50 strategies in R4 trade_log, got {len(grouped)}"


def test_b964_sharpe_proxy_small_sample_returns_none():
    """B964: Sharpe proxy on n<5 returns None."""
    from backtest.diagnostics.section_15_exit_profitability_fraction import _sharpe_proxy
    assert _sharpe_proxy([]) is None
    assert _sharpe_proxy([0.01, 0.02]) is None  # n=2 < 5


def test_b964_sharpe_proxy_zero_std_returns_none():
    """B964: Sharpe proxy when std=0 returns None (degenerate)."""
    from backtest.diagnostics.section_15_exit_profitability_fraction import _sharpe_proxy
    assert _sharpe_proxy([1.0, 1.0, 1.0, 1.0, 1.0]) is None


def test_b964_sharpe_proxy_positive_returns_positive_sharpe():
    """B964: Sharpe proxy on positive-mean returns is positive."""
    from backtest.diagnostics.section_15_exit_profitability_fraction import _sharpe_proxy
    sharpe = _sharpe_proxy([0.5, 0.3, 0.4, 0.6, 0.2, 0.5, 0.3])
    assert sharpe is not None
    assert sharpe > 0


def test_b964_extract_strategy_in_r4_returns_populated():
    """B964: a strategy in R4 trade_log returns populated per_exit_sharpe."""
    from backtest.diagnostics.section_15_exit_profitability_fraction import (
        extract_section_15_for_strategy,
        _load_r4_trade_log_by_strategy_exit,
    )
    grouped = _load_r4_trade_log_by_strategy_exit()
    # Find strategy with >=2 exit_reasons each having >=5 trades
    test_strat = None
    for s, exits in grouped.items():
        big_cells = [e for e, p in exits.items() if len(p) >= 5]
        if len(big_cells) >= 2:
            test_strat = s
            break
    if test_strat is None:
        pytest.skip("No multi-exit strategy with >=5 trades per cell in R4")
    result = extract_section_15_for_strategy(test_strat)
    assert result["in_r4_trade_log"] is True
    assert result["exits_measured"] >= 1
    assert result["exits_total"] == 26
    assert isinstance(result["per_exit_sharpe"], dict)


def test_b964_extract_unknown_strategy_returns_not_measured():
    """B964: unknown strategy returns exit_profitability_check='not_measured'."""
    from backtest.diagnostics.section_15_exit_profitability_fraction import extract_section_15_for_strategy
    result = extract_section_15_for_strategy("nonexistent_strategy_xyz_789")
    assert result["in_r4_trade_log"] is False
    assert result["exit_profitability_check"] == "not_measured"
    assert result["exits_measured"] == 0
    assert result["warn_partial_denominator"] is True


def test_b964_warn_partial_denominator_when_measured_less_than_total():
    """B964: warn_partial_denominator=True when exits_measured < 26."""
    from backtest.diagnostics.section_15_exit_profitability_fraction import (
        extract_section_15_for_strategy,
        _load_r4_trade_log_by_strategy_exit,
    )
    grouped = _load_r4_trade_log_by_strategy_exit()
    test_strat = next(iter(grouped.keys()))
    result = extract_section_15_for_strategy(test_strat)
    if result["exits_measured"] < 26:
        assert result["warn_partial_denominator"] is True
        assert result["fraction_basis"] == "partial_per_strategy"


def test_b964_fraction_per_total_uses_26_denominator():
    """B964: fraction_positive_per_total uses 26 denominator per PATH canonical."""
    from backtest.diagnostics.section_15_exit_profitability_fraction import (
        extract_section_15_for_strategy,
        _load_r4_trade_log_by_strategy_exit,
        EXITS_TOTAL,
    )
    assert EXITS_TOTAL == 26
    grouped = _load_r4_trade_log_by_strategy_exit()
    test_strat = next(iter(grouped.keys()))
    result = extract_section_15_for_strategy(test_strat)
    if result["fraction_positive_per_total"] is not None:
        expected = round(result["exits_with_positive_sharpe"] / 26, 4)
        assert abs(result["fraction_positive_per_total"] - expected) < 1e-6


def test_b964_threshold_floor_is_0_4_per_path():
    """B964: FRACTION_POSITIVE_FLOOR = 0.4 per PATH Section 13.3 row 15."""
    from backtest.diagnostics.section_15_exit_profitability_fraction import FRACTION_POSITIVE_FLOOR
    assert FRACTION_POSITIVE_FLOOR == 0.4


def test_b964_schema_keys_complete():
    """B964: extract returns expected schema keys."""
    from backtest.diagnostics.section_15_exit_profitability_fraction import extract_section_15_for_strategy
    result = extract_section_15_for_strategy("any_strategy")
    expected_keys = {
        "in_r4_trade_log", "exits_measured", "exits_total",
        "exits_with_positive_sharpe", "fraction_positive_per_measured",
        "fraction_positive_per_total", "per_exit_sharpe",
        "exit_profitability_check", "fraction_basis",
        "warn_partial_denominator", "method", "source", "limitation",
        "memory_rule_reference",
    }
    assert set(result.keys()) == expected_keys


def test_b964_populate_writes_to_dossier(tmp_path):
    """B964: populate_section_15_for_dossier writes section slot."""
    from backtest.diagnostics.section_15_exit_profitability_fraction import populate_section_15_for_dossier
    dossier_path = tmp_path / "dossier.json"
    dossier_path.write_text(json.dumps({"strategy": "any", "sections": {}}))
    populate_section_15_for_dossier("any", dossier_path)
    with open(dossier_path) as f:
        dossier = json.load(f)
    assert "section_15_exit_profitability_fraction" in dossier["sections"]
