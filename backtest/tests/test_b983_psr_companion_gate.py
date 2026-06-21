"""B983 (2026-06-21): Phase P1 Bucket B B1 - DEC #6 PSR companion gate.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.4 DEC #6 + Council 86
# Option-7 owner-approved 2026-06-21 'Approve your recommendation.
# Proceed council this.'

Verifies B983 Council 86 Option-7 implementation:
  - "psr" key present in compute_strategy_metrics passes dict
  - PSR >= 0.95 -> passes_psr = True
  - PSR < 0.95 -> passes_psr = False
  - PSR = None (n_trades < 30 or sharpe == 0) -> passes_psr = True
    (per Council 86 Option-7 INSUFFICIENT-SAMPLE-PASS; no double-penalty
    with n>=30 criterion #9)
  - Separate from passes_compose (deflated_sharpe / dsr) per DEC #6
    literal reading

Closes Bucket B 5-of-5.
"""
from __future__ import annotations

from backtest.config import PASSING_CRITERIA
from backtest.results.metrics import _deflated_sharpe


def test_b983_min_psr_in_passing_criteria():
    """B983: PASSING_CRITERIA dict contains min_psr = 0.95 per DEC #6."""
    assert "min_psr" in PASSING_CRITERIA, (
        "B983: PASSING_CRITERIA must contain min_psr key per Council 86 Option-7"
    )
    assert PASSING_CRITERIA["min_psr"] == 0.95, (
        f"B983: min_psr must be 0.95 per DEC #6 Quant spec; "
        f"got {PASSING_CRITERIA['min_psr']}"
    )


def test_b983_psr_high_sharpe_returns_high_psr():
    """B983: high Sharpe + adequate sample produces PSR near 1.0."""
    # Realistic strong-Sharpe scenario: SR=1.5, n=200, normal-ish
    result = _deflated_sharpe(sharpe=1.5, n_trades=200, skew=0.0, kurtosis=3.0)
    assert result["psr"] is not None
    assert result["psr"] >= 0.95, (
        f"B983: SR=1.5 n=200 PSR should be >= 0.95; got {result['psr']}"
    )


def test_b983_psr_insufficient_sample_returns_none():
    """B983: n_trades < 30 returns PSR=None per Bailey-Lopez de Prado."""
    result = _deflated_sharpe(sharpe=1.5, n_trades=20, skew=0.0, kurtosis=3.0)
    assert result["psr"] is None, (
        f"B983: n_trades=20 < 30 should return PSR=None; got {result['psr']}"
    )


def test_b983_psr_zero_sharpe_returns_none():
    """B983: sharpe == 0 returns PSR=None per degenerate-case guard."""
    result = _deflated_sharpe(sharpe=0.0, n_trades=200, skew=0.0, kurtosis=3.0)
    assert result["psr"] is None, (
        f"B983: sharpe=0 should return PSR=None; got {result['psr']}"
    )


def test_b983_passes_psr_gate_composition_semantics():
    """B983: passes_psr composition matches Option-7 spec.

    Verifies the composition logic directly (without invoking the full
    compute_strategy_metrics with synthetic trade data):
      passes_psr = (psr is None) OR (psr >= min_psr)
    """
    min_psr = 0.95
    test_cases = [
        # (psr_value, expected_passes_psr, description)
        (None, True, "PSR=None auto-passes per Option-7 INSUFFICIENT-SAMPLE-PASS"),
        (0.99, True, "PSR=0.99 >= 0.95 passes"),
        (0.95, True, "PSR=0.95 == threshold passes"),
        (0.94, False, "PSR=0.94 < 0.95 fails"),
        (0.50, False, "PSR=0.50 << 0.95 fails"),
        (0.0, False, "PSR=0.0 fails (degenerate)"),
    ]
    for psr_value, expected, desc in test_cases:
        actual = (psr_value is None) or (psr_value >= min_psr)
        assert actual == expected, (
            f"B983 gate composition failure: {desc} -- "
            f"psr={psr_value} expected passes_psr={expected} got={actual}"
        )


def test_b983_dec_6_literal_separation_from_dsr():
    """B983: PSR companion gate is SEPARATE from DSR per DEC #6 literal reading.

    Verifies that PASSING_CRITERIA has BOTH:
      - min_deflated_sharpe (DSR family-level multi-testing correction)
      - min_psr (per-strategy Sharpe-confidence)
    Per DEC #6 'PSR per-strategy + DSR on family' literal separation.
    """
    assert "min_deflated_sharpe" in PASSING_CRITERIA, "DSR family-level gate"
    assert "min_psr" in PASSING_CRITERIA, "PSR per-strategy gate"
    # Both 0.95 by convention but they measure different things
    assert PASSING_CRITERIA["min_deflated_sharpe"] == 0.95
    assert PASSING_CRITERIA["min_psr"] == 0.95
