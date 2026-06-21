"""B982 (2026-06-21): Phase P1 Bucket B B3 - BH-FDR promoted from sanity-check to gate.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13 + Council 85 Option-3
# owner-approved 2026-06-21 'Approve your recommendations. Proceed
# council this.'

Verifies B982 Council 85 Option-3 implementation:
  - passes_compose now requires bh_fdr_significant = True
  - Strategies failing BH-FDR fail passes_compose even if deflated +
    SPA pass
  - Discrepancy flag (bh_fdr_significant field) still exists as audit
    trail per pre-B982 invariant
  - Backward compat: pre-B982 behavior was (deflated > 0 AND deflated_p
    < alpha AND spa_p < alpha) WITHOUT bh_fdr_significant; post-B982
    adds the BH-FDR conjunct.
"""
from __future__ import annotations

import math

from backtest.engine.multiple_testing_correction import (
    StrategyTestInput,
    StrategyTestResult,
    cube_select_with_multiple_testing,
)


def _make_input(
    strategy: str,
    direction: str = "long",
    regime: str = "overall",
    sharpe: float = 0.5,
    n_trades: int = 200,
) -> StrategyTestInput:
    """Build StrategyTestInput per actual schema (sharpe + n_trades + returns)."""
    return StrategyTestInput(
        strategy=strategy,
        direction=direction,
        regime=regime,
        sharpe=sharpe,
        n_trades=n_trades,
        returns=None,
    )


def test_b982_bh_fdr_now_part_of_passes_compose():
    """B982: passes_compose composition includes bh_fdr_significant as conjunct."""
    inputs = [
        _make_input(f"strat_{i}", sharpe=0.6 + 0.05 * i, n_trades=300)
        for i in range(20)
    ]
    results = cube_select_with_multiple_testing(inputs, alpha=0.05)
    for r in results:
        # passes_compose must NOT be True if bh_fdr_significant is False
        if not r.bh_fdr_significant:
            assert r.passes_compose is False, (
                f"B982 invariant: strategy {r.strategy} bh_fdr_significant=False "
                f"but passes_compose=True (BH-FDR should be hard gate)"
            )
        # passes_compose can be True only when ALL 4 conjuncts pass
        if r.passes_compose:
            assert r.deflated_sharpe > 0
            assert r.deflated_sharpe_pvalue < 0.05
            assert r.spa_pvalue < 0.05
            assert r.bh_fdr_significant is True


def test_b982_bh_fdr_audit_trail_preserved():
    """B982: bh_fdr_significant field still exists as audit trail per pre-B982."""
    inputs = [_make_input(f"strat_{i}", sharpe=0.5 + 0.02 * i, n_trades=200) for i in range(10)]
    results = cube_select_with_multiple_testing(inputs, alpha=0.05)
    for r in results:
        # Audit trail invariant: field must exist + be boolean
        assert hasattr(r, "bh_fdr_significant"), (
            f"B982 invariant: bh_fdr_significant field missing on {r.strategy}"
        )
        assert isinstance(r.bh_fdr_significant, bool)


def test_b982_discrepancy_case_now_fails_gate():
    """B982: regression test for the case Council 85 cited as the motivation.

    Pre-B982: a strategy could pass deflated-Sharpe + SPA but fail BH-FDR
    and still get passes_compose=True (discrepancy flag was sanity-check
    only). Post-B982: such a case must get passes_compose=False.
    """
    # Craft a borderline pool where some strategies pass deflated but fail BH-FDR
    inputs = [
        _make_input(f"borderline_{i}", sharpe=0.45 + 0.01 * i, n_trades=150)
        for i in range(30)
    ]
    results = cube_select_with_multiple_testing(inputs, alpha=0.05)
    # Find at least one result where bh_fdr_significant=False AND deflated_p<alpha
    # (if any exist, they must NOT pass_compose per B982)
    discrepancy_cases = [
        r for r in results
        if not r.bh_fdr_significant
        and r.deflated_sharpe > 0
        and r.deflated_sharpe_pvalue < 0.05
    ]
    for r in discrepancy_cases:
        assert r.passes_compose is False, (
            f"B982 regression: strategy {r.strategy} is a discrepancy case "
            f"(deflated passes but BH-FDR fails); passes_compose must be False post-B982"
        )


def test_b982_module_docstring_mentions_b982_amendment():
    """B982: module docstring must document the B667 D1 amendment per CHECKLIST #67."""
    from backtest.engine import multiple_testing_correction as mtc
    assert mtc.__doc__ is not None
    assert "B982" in mtc.__doc__, "B982 amendment must be in module docstring"
    assert "BH-FDR" in mtc.__doc__
    assert "HARD GATE" in mtc.__doc__ or "hard gate" in mtc.__doc__.lower()
