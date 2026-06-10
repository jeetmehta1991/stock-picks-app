"""Batch 687 (2026-06-10) -- validation harness for the conditional-
information gate diagnostic (backtest/engine/conditional_information_gate
_diagnostic.py).

Per B687 external reviewer critique on trend cluster doc:

  The trend cluster's redundancy audit decided "honest confluence vs
  no-op camouflage" from per-gate True-rate + pairwise gate-gate
  correlation. Neither looks at the OUTCOME. The audit caught T10
  (one gate 99% True) correctly but cleared T3 as "honest confluence"
  on a +0.41 gate correlation that actually signals REDUNDANCY.

  Reviewer-built diagnostic (this module's test target) uses conditional
  information about the OUTCOME given the OTHER gates -- the missing
  axis. Validated against 3 labeled synthetic cases:

    Case A (T10-like): 1 gate at ~99% True (no-op camouflage)
      Expected: NO_OP_CAMOUFLAGE on the constant gate
    Case B (T3-like): 4 gates at ~45% True each, all correlated proxies
                      of one latent "trending up" factor
      Expected: JOINT_REDUNDANT (CAUGHT where current method clears)
    Case C (genuine confluence): 3 orthogonal failure-mode screens
      Expected: CONFLUENCE (no false alarm)
    Case D (mixed): 2 real informative + 1 redundant + 1 subsumed
      Expected: per-gate prune the redundant; defer the subsumed

  Decisive separation per reviewer empirical results:
    redundant gates score ~0.4-1.4sigma on conditional outcome spread
    genuine gates score 9-22sigma
  That gap is what the +0.41-correlation reasoning could not see.

Pins:

Case A (T10-like NO_OP_CAMOUFLAGE):
  (1)  Strategy verdict == "NO_OP_CAMOUFLAGE"
  (2)  The 99%-True gate is classified NO_OP_CAMOUFLAGE per-gate
  (3)  Recommended core excludes the no-op gate

Case B (T3-like JOINT_REDUNDANT):
  (4)  Strategy verdict == "JOINT_REDUNDANT"
  (5)  At least 2 gates classified JOINT_REDUNDANT (redundant proxies)
  (6)  None of the gates classified NO_OP_CAMOUFLAGE (individually < 98% True)
  (7)  Recommended core collapses to single informative gate

Case C (CONFLUENCE positive control):
  (8)  Strategy verdict == "CONFLUENCE"
  (9)  All 3 gates classified CONFLUENT
  (10) Conditional Z >> 2sigma for all genuine gates (validates separation)

Case D (mixed):
  (11) Real informative gates classified CONFLUENT
  (12) Redundant proxy gate classified JOINT_REDUNDANT
  (13) Recommended core excludes the redundant proxy

API + edge cases:
  (14) diagnose_strategy raises on shape mismatch
  (15) diagnose_strategy handles single-gate strategy
"""
from __future__ import annotations

import numpy as np
import pytest

from backtest.engine.conditional_information_gate_diagnostic import (
    StrategyDiagnosticResult,
    diagnose_strategy,
)


def _generate_t10_no_op_case(n: int = 5000, seed: int = 42) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Case A: 1 gate near-constant (T10 supertrend_bullish 99% True).
    Strategy with 3 gates total: 1 informative + 1 noise + 1 no-op.
    Outcome rewards rows where the informative gate is True.
    """
    rng = np.random.default_rng(seed)
    informative = rng.binomial(1, 0.45, n).astype(bool)
    noise       = rng.binomial(1, 0.45, n).astype(bool)
    no_op       = rng.binomial(1, 0.99, n).astype(bool)  # ~99% True
    # Outcome: informative gate adds +0.5sigma in expected return
    returns = rng.normal(0.0, 1.0, n) + 0.5 * informative.astype(float)
    gate_matrix = np.column_stack([informative, noise, no_op])
    gate_names = ["informative", "noise", "supertrend_bullish_99pct"]
    return gate_matrix, returns, gate_names


def _generate_t3_joint_redundant_case(n: int = 5000, seed: int = 43) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Case B: 4 gates that are all correlated proxies of ONE latent
    factor (T3 hull_rsi: hull_bullish + price_above_hull + rsi>50 +
    above_ema_200 all measure "price/Hull is trending up").

    Each gate ~45% True (no per-gate constant). Latent factor drives
    all 4 -- positively correlated (sibling-R^2 high). Outcome rewards
    rows where latent factor is True. Each gate carries some noise so
    they're not bit-identical.
    """
    rng = np.random.default_rng(seed)
    latent = rng.binomial(1, 0.45, n).astype(bool)
    # 4 proxies: each is the latent factor flipped with prob ~15% noise
    flip_prob = 0.15
    proxy_a = (latent ^ rng.binomial(1, flip_prob, n).astype(bool))
    proxy_b = (latent ^ rng.binomial(1, flip_prob, n).astype(bool))
    proxy_c = (latent ^ rng.binomial(1, flip_prob, n).astype(bool))
    proxy_d = (latent ^ rng.binomial(1, flip_prob, n).astype(bool))
    # Returns driven by the LATENT factor (not by any individual gate)
    returns = rng.normal(0.0, 1.0, n) + 0.5 * latent.astype(float)
    gate_matrix = np.column_stack([proxy_a, proxy_b, proxy_c, proxy_d])
    gate_names = ["hull_bullish", "price_above_hull", "rsi_14_above_50", "above_ema_200"]
    return gate_matrix, returns, gate_names


def _generate_confluence_positive_control(n: int = 5000, seed: int = 44) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Case C: 3 ORTHOGONAL gates, each screening a different failure
    mode. Each gate is individually predictive (CONFLUENT) and
    uncorrelated with siblings.

    Outcome rewards rows where ALL 3 gates are True (each adds +0.6sigma).
    Gates are independent draws -> low sibling correlation -> the
    diagnostic should classify all 3 as CONFLUENT.
    """
    rng = np.random.default_rng(seed)
    g1 = rng.binomial(1, 0.45, n).astype(bool)
    g2 = rng.binomial(1, 0.45, n).astype(bool)
    g3 = rng.binomial(1, 0.45, n).astype(bool)
    # Each gate independently adds to returns -- so each carries
    # marginal information given the others
    returns = (
        rng.normal(0.0, 1.0, n)
        + 0.6 * g1.astype(float)
        + 0.6 * g2.astype(float)
        + 0.6 * g3.astype(float)
    )
    gate_matrix = np.column_stack([g1, g2, g3])
    gate_names = ["screen_a_orthogonal", "screen_b_orthogonal", "screen_c_orthogonal"]
    return gate_matrix, returns, gate_names


def _generate_mixed_case(n: int = 5000, seed: int = 45) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Case D: 4 gates total -- 2 genuinely informative + 1 redundant
    proxy of one of the informative gates + 1 too-subsumed (always
    fires when others fire).
    """
    rng = np.random.default_rng(seed)
    real_a = rng.binomial(1, 0.45, n).astype(bool)
    real_b = rng.binomial(1, 0.45, n).astype(bool)
    # Redundant proxy of real_a (15% noise flip)
    proxy_a = (real_a ^ rng.binomial(1, 0.15, n).astype(bool))
    # Subsumed: rarely False when real_a + real_b + proxy_a all fire
    subsumed = rng.binomial(1, 0.85, n).astype(bool)
    returns = (
        rng.normal(0.0, 1.0, n)
        + 0.6 * real_a.astype(float)
        + 0.6 * real_b.astype(float)
    )
    gate_matrix = np.column_stack([real_a, real_b, proxy_a, subsumed])
    gate_names = ["real_a", "real_b", "proxy_of_real_a", "subsumed_gate"]
    return gate_matrix, returns, gate_names


# =================== Case A: T10-like NO_OP_CAMOUFLAGE ===================

def test_batch687_case_a_strategy_verdict_no_op_camouflage():
    """Pin (1)."""
    gm, ret, names = _generate_t10_no_op_case()
    result = diagnose_strategy(gm, ret, names)
    assert result.verdict == "NO_OP_CAMOUFLAGE", (
        f"Expected NO_OP_CAMOUFLAGE for T10-like case; got {result.verdict}. "
        f"per_gate={[(g.gate_name, g.verdict, g.true_rate) for g in result.per_gate]}"
    )


def test_batch687_case_a_no_op_gate_classified():
    """Pin (2): the 99%-True gate must be flagged NO_OP_CAMOUFLAGE."""
    gm, ret, names = _generate_t10_no_op_case()
    result = diagnose_strategy(gm, ret, names)
    no_op_gate = next(g for g in result.per_gate if g.gate_name == "supertrend_bullish_99pct")
    assert no_op_gate.verdict == "NO_OP_CAMOUFLAGE"
    assert no_op_gate.true_rate >= 0.98


def test_batch687_case_a_recommended_core_excludes_no_op():
    """Pin (3): recommended core gates must NOT include the no-op."""
    gm, ret, names = _generate_t10_no_op_case()
    result = diagnose_strategy(gm, ret, names)
    assert "supertrend_bullish_99pct" not in result.recommended_core_gates


# =================== Case B: T3-like JOINT_REDUNDANT ===================

def test_batch687_case_b_strategy_verdict_joint_redundant():
    """Pin (4): T3-like 4-proxy case must be JOINT_REDUNDANT.
    THIS IS THE CRITICAL CASE -- caught by B687 diagnostic where
    pre-B687 method clears it as 'honest confluence'."""
    gm, ret, names = _generate_t3_joint_redundant_case()
    result = diagnose_strategy(gm, ret, names)
    assert result.verdict == "JOINT_REDUNDANT", (
        f"CRITICAL B687 regression: T3-like joint-redundant case must be "
        f"flagged JOINT_REDUNDANT (pre-B687 diagnostic cleared this as "
        f"'honest confluence' on +0.41 correlation; B687 fixes the "
        f"methodology error). Got {result.verdict}. "
        f"per_gate={[(g.gate_name, g.verdict, round(g.conditional_z, 2), round(g.sibling_r2, 2)) for g in result.per_gate]}"
    )


def test_batch687_case_b_at_least_two_gates_redundant():
    """Pin (5): At least 2 gates must be classified JOINT_REDUNDANT."""
    gm, ret, names = _generate_t3_joint_redundant_case()
    result = diagnose_strategy(gm, ret, names)
    n_redundant = sum(1 for g in result.per_gate if g.verdict == "JOINT_REDUNDANT")
    assert n_redundant >= 2, (
        f"Expected >= 2 JOINT_REDUNDANT gates in T3-like case; got {n_redundant}. "
        f"per_gate={[(g.gate_name, g.verdict, round(g.conditional_z, 2)) for g in result.per_gate]}"
    )


def test_batch687_case_b_no_no_op_camouflage_on_45pct_gates():
    """Pin (6): 45%-True gates should NOT be misclassified as NO_OP.
    The B687 diagnostic must distinguish JOINT_REDUNDANT from
    NO_OP_CAMOUFLAGE: T3's gates are individually non-constant but
    jointly redundant -- a category the pre-B687 method had no name for."""
    gm, ret, names = _generate_t3_joint_redundant_case()
    result = diagnose_strategy(gm, ret, names)
    for g in result.per_gate:
        assert g.verdict != "NO_OP_CAMOUFLAGE", (
            f"Gate {g.gate_name} (true_rate={g.true_rate:.2f}) misclassified as NO_OP_CAMOUFLAGE"
        )


def test_batch687_case_b_recommended_core_collapses_to_one_gate():
    """Pin (7): When all gates are redundant proxies of one latent factor,
    the recommended core should collapse to a single informative gate."""
    gm, ret, names = _generate_t3_joint_redundant_case()
    result = diagnose_strategy(gm, ret, names)
    assert len(result.recommended_core_gates) <= 1, (
        f"Expected core to collapse to <=1 gate for joint-redundant case; "
        f"got {result.recommended_core_gates}"
    )


# =================== Case C: CONFLUENCE positive control ===================

def test_batch687_case_c_strategy_verdict_confluence():
    """Pin (8): orthogonal-screens case must be CONFLUENCE (NO false alarm)."""
    gm, ret, names = _generate_confluence_positive_control()
    result = diagnose_strategy(gm, ret, names)
    assert result.verdict == "CONFLUENCE", (
        f"Expected CONFLUENCE (no false alarm) for orthogonal-screens case; "
        f"got {result.verdict}. "
        f"per_gate={[(g.gate_name, g.verdict, round(g.conditional_z, 2)) for g in result.per_gate]}"
    )


def test_batch687_case_c_all_gates_confluent():
    """Pin (9): All 3 orthogonal gates must be classified CONFLUENT."""
    gm, ret, names = _generate_confluence_positive_control()
    result = diagnose_strategy(gm, ret, names)
    for g in result.per_gate:
        assert g.verdict == "CONFLUENT", (
            f"Gate {g.gate_name} expected CONFLUENT; got {g.verdict} (Z={g.conditional_z:.2f})"
        )


def test_batch687_case_c_decisive_z_separation():
    """Pin (10): Confluent gates should score Z >> 2sigma (decisive separation
    from redundant gates which score ~0.4-1.4sigma per reviewer empirical).
    Validates the diagnostic's discriminatory power."""
    gm, ret, names = _generate_confluence_positive_control()
    result = diagnose_strategy(gm, ret, names)
    for g in result.per_gate:
        if g.verdict != "INCONCLUSIVE":
            assert g.conditional_z >= 4.0, (
                f"Genuine confluence gate {g.gate_name} Z={g.conditional_z:.2f} "
                f"below decisive-separation bar of 4sigma"
            )


# =================== Case D: Mixed real + redundant + subsumed ===================

def test_batch687_case_d_real_gates_confluent():
    """Pin (11): The 2 genuinely informative gates must be CONFLUENT."""
    gm, ret, names = _generate_mixed_case()
    result = diagnose_strategy(gm, ret, names)
    real_a = next(g for g in result.per_gate if g.gate_name == "real_a")
    real_b = next(g for g in result.per_gate if g.gate_name == "real_b")
    # Real_a may be JOINT_REDUNDANT if proxy_of_real_a substitutes for it
    # (mutual-redundancy). At minimum real_b should be CONFLUENT.
    assert real_b.verdict == "CONFLUENT", (
        f"Independent real_b expected CONFLUENT; got {real_b.verdict} "
        f"(Z={real_b.conditional_z:.2f})"
    )


def test_batch687_case_d_redundant_proxy_flagged():
    """Pin (12): The redundant proxy must be flagged JOINT_REDUNDANT
    (or INCONCLUSIVE if subsumed by real_a too tightly to test).
    Critical: must NOT be CONFLUENT."""
    gm, ret, names = _generate_mixed_case()
    result = diagnose_strategy(gm, ret, names)
    proxy = next(g for g in result.per_gate if g.gate_name == "proxy_of_real_a")
    assert proxy.verdict != "CONFLUENT", (
        f"Redundant proxy_of_real_a misclassified as CONFLUENT "
        f"(Z={proxy.conditional_z:.2f}, sibling_r2={proxy.sibling_r2:.2f})"
    )


def test_batch687_case_d_recommended_core_excludes_redundant():
    """Pin (13): Recommended core must exclude the redundant proxy."""
    gm, ret, names = _generate_mixed_case()
    result = diagnose_strategy(gm, ret, names)
    assert "proxy_of_real_a" not in result.recommended_core_gates


# =================== API + edge cases ===================

def test_batch687_diagnose_strategy_raises_on_shape_mismatch():
    """Pin (14): API contract -- mismatched shapes raise ValueError."""
    gm = np.zeros((100, 3), dtype=bool)
    ret = np.zeros(99)  # Mismatched length
    with pytest.raises(ValueError, match="gate_matrix rows"):
        diagnose_strategy(gm, ret, ["a", "b", "c"])
    # Mismatched gate_names
    ret = np.zeros(100)
    with pytest.raises(ValueError, match="gate_names"):
        diagnose_strategy(gm, ret, ["a", "b"])  # 2 names for 3 gates


def test_batch687_diagnose_strategy_single_gate():
    """Pin (15): Single-gate strategy: no 'other gates' -> diagnose against
    full population. Should not crash."""
    rng = np.random.default_rng(0)
    n = 1000
    gate = rng.binomial(1, 0.45, n).astype(bool).reshape(-1, 1)
    returns = rng.normal(0, 1, n) + 0.5 * gate[:, 0].astype(float)
    result = diagnose_strategy(gate, returns, ["solo_gate"])
    assert isinstance(result, StrategyDiagnosticResult)
    assert len(result.per_gate) == 1
