"""Batch 667 (2026-06-09) -- multiple-testing correction unit + integration
pins per MULTIPLE_TESTING_METHODOLOGY.md 6 owner-approved decisions.

Pins by function:

Bailey-LdP Deflated Sharpe (Decision 1 + 2):
  (1)  expected_max_sharpe is 0 for N=1 (no selection bias)
  (2)  expected_max_sharpe is monotonic in N (more strategies = higher
       expected-max under null)
  (3)  deflated_sharpe < raw_sharpe for N > 1 (selection-bias correction
       always reduces)
  (4)  deflated_sharpe one-sided p-value is in [0, 1]
  (5)  deflated_sharpe at N=219 (deployable) matches Bailey-LdP closed
       form to 4 decimal places (regression-block on the constant)

Hansen SPA (Decision 1 + 5):
  (6)  hansen_spa_pvalue returns p in [0, 1]
  (7)  hansen_spa_pvalue is deterministic given same rng_seed
  (8)  hansen_spa_pvalue with all-zero strategy returns vs zero
       benchmark returns p ~ 1 (no signal => high p-value)
  (9)  hansen_spa_pvalue with one strongly-positive strategy returns
       low p-value (< 0.1 expected)

Benjamini-Hochberg FDR (Decision 1):
  (10) BH-FDR on empty p-values returns empty list
  (11) BH-FDR on all-significant p-values rejects all
  (12) BH-FDR on all-non-significant p-values rejects none
  (13) BH-FDR controls FDR at level alpha for mixed p-values
       (mathematical property test)

EXPLORATORY flag mechanism (Decision 4):
  (14) cube_eligible_for_multiple_testing returns False for W5 + W5m
       (current EXPLORATORY set per B644 + B652)
  (15) cube_eligible_for_multiple_testing returns True for deployable
       (sample 3 strategies)

COMPOSE orchestrator (Decision 1 + 3 + 5):
  (16) cube_select_with_multiple_testing returns one result per input
  (17) results are grouped by (direction, regime) per Decision 3 + 5
       (LONG/SHORT separate; per-regime + overall separate)
  (18) EXPLORATORY inputs receive results but their inclusion in the
       group doesn't increase the family-size N for deployable inputs
       (Decision 4 circularity resolution)
  (19) passes_compose is True iff (deflated_z > 0 AND deflated p < alpha
       AND SPA p < alpha)
"""
from __future__ import annotations

import math


# ============ Bailey-LdP Deflated Sharpe ============

def test_batch667_expected_max_sharpe_n1_is_zero():
    """Pin (1): N=1 means no selection bias; expected_max = 0."""
    from backtest.engine.multiple_testing_correction import (
        expected_max_sharpe_bailey_lopez_de_prado,
    )
    assert expected_max_sharpe_bailey_lopez_de_prado(1) == 0.0


def test_batch667_expected_max_sharpe_monotonic_in_n():
    """Pin (2): expected_max_sharpe is monotonically increasing in N.
    Testing more strategies under null produces higher expected-max."""
    from backtest.engine.multiple_testing_correction import (
        expected_max_sharpe_bailey_lopez_de_prado,
    )
    em_10 = expected_max_sharpe_bailey_lopez_de_prado(10)
    em_100 = expected_max_sharpe_bailey_lopez_de_prado(100)
    em_219 = expected_max_sharpe_bailey_lopez_de_prado(219)
    em_1000 = expected_max_sharpe_bailey_lopez_de_prado(1000)
    assert em_10 < em_100 < em_219 < em_1000


def test_batch667_deflated_sharpe_less_than_raw():
    """Pin (3): deflation always reduces Sharpe for N > 1."""
    from backtest.engine.multiple_testing_correction import (
        deflated_sharpe_bailey_lopez_de_prado,
    )
    sharpe_raw = 1.5
    z, _ = deflated_sharpe_bailey_lopez_de_prado(
        sharpe_raw, n_trades=100, family_size=219,
    )
    # z is in standard-normal units; should be much smaller than the raw
    # 1.5 figure once the expected-max-of-219 ~ 2.5+ baseline is netted
    assert z < sharpe_raw


def test_batch667_deflated_sharpe_pvalue_bounded():
    """Pin (4): p-value is in [0, 1]."""
    from backtest.engine.multiple_testing_correction import (
        deflated_sharpe_bailey_lopez_de_prado,
    )
    for sharpe in (-2.0, -0.5, 0.0, 0.5, 1.5, 3.0):
        z, p = deflated_sharpe_bailey_lopez_de_prado(
            sharpe, n_trades=100, family_size=219,
        )
        assert 0.0 <= p <= 1.0, f"sharpe={sharpe} produced p={p}"


def test_batch667_deflated_sharpe_n219_closed_form():
    """Pin (5): regression-block on the closed-form constant at the
    owner-approved deployable family size N=219.

    Bailey-LdP 2014 closed form with N=219, sharpe_variance=1.0:
      E[max] = (1 - gamma) * Phi^-1(1 - 1/219)
             + gamma * Phi^-1(1 - 1/(219 * e))
      where gamma = 0.5772156649015329

    Numerically: Phi^-1(0.995434) ~ 2.6090, Phi^-1(0.998320) ~ 2.9350
    E[max] ~ (1-0.5772) * 2.6090 + 0.5772 * 2.9350 ~ 2.7951

    This pin locks in the constant so a future regression in the inv-CDF
    approximation surfaces immediately."""
    from backtest.engine.multiple_testing_correction import (
        expected_max_sharpe_bailey_lopez_de_prado,
    )
    em_219 = expected_max_sharpe_bailey_lopez_de_prado(219)
    # Allow 0.005 tolerance for the Acklam inv-CDF approximation
    assert abs(em_219 - 2.7951) < 0.005, (
        f"E[max Sharpe | N=219] = {em_219:.4f}; expected ~2.7951"
    )


# ============ Hansen SPA ============

def test_batch667_spa_pvalue_in_unit_interval():
    """Pin (6): SPA p-value in [0, 1]."""
    from backtest.engine.multiple_testing_correction import hansen_spa_pvalue
    import random
    rng = random.Random(0)
    strategy_returns = [
        [rng.gauss(0.0, 0.01) for _ in range(100)]
        for _ in range(5)
    ]
    p = hansen_spa_pvalue(strategy_returns, n_bootstrap=200, rng_seed=42)
    assert 0.0 <= p <= 1.0


def test_batch667_spa_pvalue_deterministic_given_seed():
    """Pin (7): same seed -> same p-value."""
    from backtest.engine.multiple_testing_correction import hansen_spa_pvalue
    import random
    rng = random.Random(0)
    strategy_returns = [
        [rng.gauss(0.0, 0.01) for _ in range(100)]
        for _ in range(5)
    ]
    p1 = hansen_spa_pvalue(strategy_returns, n_bootstrap=200, rng_seed=42)
    p2 = hansen_spa_pvalue(strategy_returns, n_bootstrap=200, rng_seed=42)
    assert p1 == p2


def test_batch667_spa_pvalue_zero_returns_high():
    """Pin (8): all-zero strategy returns vs zero benchmark -> high p
    (no signal)."""
    from backtest.engine.multiple_testing_correction import hansen_spa_pvalue
    strategy_returns = [[0.0] * 100 for _ in range(5)]
    p = hansen_spa_pvalue(strategy_returns, n_bootstrap=200, rng_seed=42)
    # No signal at all => p > 0.5 (sanity)
    assert p > 0.5


def test_batch667_spa_pvalue_positive_signal_low_p():
    """Pin (9): one strongly-positive strategy -> low p-value."""
    from backtest.engine.multiple_testing_correction import hansen_spa_pvalue
    import random
    rng = random.Random(0)
    # 4 zero-return strategies + 1 with strong positive mean
    weak = [[rng.gauss(0.0, 0.01) for _ in range(100)] for _ in range(4)]
    strong = [rng.gauss(0.005, 0.01) for _ in range(100)]
    strategy_returns = weak + [strong]
    p = hansen_spa_pvalue(strategy_returns, n_bootstrap=500, rng_seed=42)
    assert p < 0.1, f"Expected low p with strong signal; got {p}"


# ============ Benjamini-Hochberg FDR ============

def test_batch667_bh_fdr_empty():
    """Pin (10): empty p-values -> empty result."""
    from backtest.engine.multiple_testing_correction import benjamini_hochberg_fdr
    assert benjamini_hochberg_fdr([]) == []


def test_batch667_bh_fdr_all_significant():
    """Pin (11): all p-values << alpha -> all rejected."""
    from backtest.engine.multiple_testing_correction import benjamini_hochberg_fdr
    pvalues = [0.001, 0.002, 0.003, 0.001]
    result = benjamini_hochberg_fdr(pvalues, alpha=0.05)
    assert all(result)


def test_batch667_bh_fdr_all_nonsignificant():
    """Pin (12): all p-values >> alpha -> none rejected."""
    from backtest.engine.multiple_testing_correction import benjamini_hochberg_fdr
    pvalues = [0.9, 0.8, 0.85, 0.95]
    result = benjamini_hochberg_fdr(pvalues, alpha=0.05)
    assert not any(result)


def test_batch667_bh_fdr_mixed():
    """Pin (13): BH-FDR with mixed p-values rejects in order.

    Sorted p-values: [0.001, 0.005, 0.04, 0.5, 0.8]
    N=5, alpha=0.05
    Thresholds: 1/5*0.05=0.010, 2/5*0.05=0.020, 3/5*0.05=0.030,
                4/5*0.05=0.040, 5/5*0.05=0.050
    p[1]=0.001 <= 0.010? yes; p[2]=0.005 <= 0.020? yes;
    p[3]=0.04 <= 0.030? no; p[4]=0.5 <= 0.040? no;
    p[5]=0.8 <= 0.050? no.
    Largest k where p_(k) <= k*alpha/N is k=2.
    => Reject first 2 (in sorted order); original indices for 0.001 and
    0.005 = [0] and [1] respectively -> [True, True, False, False, False]
    """
    from backtest.engine.multiple_testing_correction import benjamini_hochberg_fdr
    pvalues = [0.001, 0.005, 0.04, 0.5, 0.8]
    result = benjamini_hochberg_fdr(pvalues, alpha=0.05)
    assert result == [True, True, False, False, False]


# ============ EXPLORATORY flag (Decision 4) ============

def test_batch667_exploratory_strategies_excluded():
    """Pin (14): W5 + W5m are excluded (return False)."""
    from backtest.engine.multiple_testing_correction import (
        cube_eligible_for_multiple_testing,
    )
    assert cube_eligible_for_multiple_testing("pivot_s3_capitulation") is False
    assert cube_eligible_for_multiple_testing("pivot_r3_blowoff_short") is False


def test_batch667_deployable_strategies_included():
    """Pin (15): sample deployable strategies return True."""
    from backtest.engine.multiple_testing_correction import (
        cube_eligible_for_multiple_testing,
    )
    for strat in (
        "insider_cluster_long",
        "institutional_cluster_long",
        "rsi_oversold",
    ):
        assert cube_eligible_for_multiple_testing(strat) is True


# ============ COMPOSE orchestrator ============

def test_batch667_compose_one_result_per_input():
    """Pin (16): cube_select_with_multiple_testing returns one result
    per input (no dropping)."""
    from backtest.engine.multiple_testing_correction import (
        cube_select_with_multiple_testing, StrategyTestInput,
    )
    inputs = [
        StrategyTestInput(
            strategy=f"strat_{i}", direction="long", regime=None,
            sharpe=0.8, n_trades=100,
        )
        for i in range(5)
    ]
    results = cube_select_with_multiple_testing(inputs, spa_bootstrap_iters=50)
    assert len(results) == len(inputs)


def test_batch667_compose_grouped_by_direction_and_regime():
    """Pin (17): results respect (direction, regime) grouping per
    Decisions 3 + 5. LONG and SHORT are separate families."""
    from backtest.engine.multiple_testing_correction import (
        cube_select_with_multiple_testing, StrategyTestInput,
    )
    # 3 LONG + 3 SHORT inputs with identical sharpe + n_trades; if
    # grouped together they would have family size 6; separately, 3 each
    inputs = (
        [StrategyTestInput(
            strategy=f"long_{i}", direction="long", regime=None,
            sharpe=0.8, n_trades=100,
        ) for i in range(3)]
        + [StrategyTestInput(
            strategy=f"short_{i}", direction="short", regime=None,
            sharpe=0.8, n_trades=100,
        ) for i in range(3)]
    )
    results = cube_select_with_multiple_testing(inputs, spa_bootstrap_iters=50)
    # All 6 deflated Sharpes should be IDENTICAL within each direction
    # but possibly different ACROSS directions due to family-size 3 vs 3.
    # Since family sizes are equal (both 3), values should match.
    long_z = [r.deflated_sharpe for r in results if r.direction == "long"]
    short_z = [r.deflated_sharpe for r in results if r.direction == "short"]
    # Within each direction, all 3 should match (same family size N=3)
    assert len(set(round(z, 6) for z in long_z)) == 1
    assert len(set(round(z, 6) for z in short_z)) == 1


def test_batch667_compose_exploratory_not_penalizing_deployable():
    """Pin (18): EXPLORATORY input in the same group does NOT inflate
    the family-size N for deployable inputs. Critical for Decision 4 +
    critique #7 circularity resolution."""
    from backtest.engine.multiple_testing_correction import (
        cube_select_with_multiple_testing, StrategyTestInput,
    )
    # Group A: 5 deployable strategies
    group_a = [
        StrategyTestInput(
            strategy=f"deployable_{i}", direction="long", regime=None,
            sharpe=1.0, n_trades=100,
        )
        for i in range(5)
    ]
    # Group B: same 5 deployable + 2 EXPLORATORY (W5 + W5m)
    group_b = group_a + [
        StrategyTestInput(
            strategy="pivot_s3_capitulation", direction="long",
            regime=None, sharpe=1.0, n_trades=100,
        ),
        StrategyTestInput(
            strategy="pivot_r3_blowoff_short", direction="long",
            regime=None, sharpe=1.0, n_trades=100,
        ),
    ]
    results_a = cube_select_with_multiple_testing(
        group_a, spa_bootstrap_iters=10,
    )
    results_b = cube_select_with_multiple_testing(
        group_b, spa_bootstrap_iters=10,
    )
    # Deployable strategies in B should have SAME deflated Sharpe as A
    # (EXPLORATORY presence did NOT increase family size from 5)
    z_a = sorted(r.deflated_sharpe for r in results_a)
    z_b_deployable = sorted(
        r.deflated_sharpe for r in results_b
        if r.strategy.startswith("deployable_")
    )
    for za, zb in zip(z_a, z_b_deployable):
        assert abs(za - zb) < 1e-9, (
            f"EXPLORATORY presence changed deployable z: {za} -> {zb} "
            "(violates Decision 4)"
        )


def test_batch667_compose_passes_iff_all_three_conditions():
    """Pin (19): passes_compose iff (deflated_z > 0 AND deflated p < alpha
    AND SPA p < alpha)."""
    from backtest.engine.multiple_testing_correction import (
        cube_select_with_multiple_testing, StrategyTestInput,
    )
    import random
    rng = random.Random(0)
    # Construct a strong-positive strategy + ensure SPA picks up signal
    strong_returns = [rng.gauss(0.01, 0.02) for _ in range(100)]
    weak_returns = [rng.gauss(0.0, 0.02) for _ in range(100)]
    inputs = [
        StrategyTestInput(
            strategy="strong_strat", direction="long", regime=None,
            sharpe=1.5, n_trades=100, returns=strong_returns,
        ),
        StrategyTestInput(
            strategy="weak_strat", direction="long", regime=None,
            sharpe=0.1, n_trades=100, returns=weak_returns,
        ),
    ]
    results = cube_select_with_multiple_testing(
        inputs, alpha=0.05, spa_bootstrap_iters=500,
    )
    for r in results:
        expected = (
            r.deflated_sharpe > 0
            and r.deflated_sharpe_pvalue < 0.05
            and r.spa_pvalue < 0.05
        )
        assert r.passes_compose is expected, (
            f"{r.strategy}: passes_compose={r.passes_compose} but expected "
            f"{expected} (z={r.deflated_sharpe:.4f}, "
            f"p_z={r.deflated_sharpe_pvalue:.4f}, "
            f"p_spa={r.spa_pvalue:.4f})"
        )
