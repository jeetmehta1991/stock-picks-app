"""Conditional-information gate redundancy diagnostic.

Batch 687 (2026-06-10 owner-approved external reviewer fix to the
trend cluster's "honest confluence vs no-op camouflage" diagnostic).

PROBLEM (per B687 external reviewer critique on trend doc):
  The trend cluster's redundancy audit (T3 / T8 / T10 walks) decided
  "honest confluence vs no-op camouflage" from two quantities:
    1. per-gate True-rate (catches T10's 99.19%-True supertrend_bullish)
    2. pairwise gate-gate correlation
  Neither looks at the OUTCOME.

  T3 (hull_rsi) was cleared as "honest confluence" because:
    - all 5 gates 38-53% True (no near-constant)
    - hull_bullish x price_above_hull correlate +0.41

  But +0.41 between gates is a REDUNDANCY signature, not a confluence
  signature. Genuine confluence requires gates with low or negative
  correlation (orthogonal failure-mode screens). The audit measured
  positively-correlated STATE gates and labeled them confluence by
  assertion.

  Worse: T3's own Step 7 "deeper question" described an always-on
  STATE composite that "fires on EVERY bar that meets the 5 conditions
  ... could fire 100+ days in a row" -- and then the finding table
  cleared it.

  Same misclassification applies to T8 (ichimoku_cloud_breakout) and
  post-fix W8 (cpr_narrow_tight): jointly-redundant positively-
  correlated STATE gates that are individually non-constant.

FIX (this module):
  The discriminator is conditional information about the OUTCOME given
  the OTHER gates. For each gate g in a strategy's gate set G:
    1. Find rows where every OTHER gate in G fires (call this the
       "other-gates-fire" subpopulation).
    2. Within that subpopulation, split rows by gate g True (KEEP)
       vs False (REJECT).
    3. Compute Z = (mean_return(KEEP) - mean_return(REJECT)) /
                   (pooled_std * sqrt(1/n_keep + 1/n_reject))
    4. Classify:
         - NO_OP_CAMOUFLAGE if True-rate > 98% (gate is near-constant)
         - INCONCLUSIVE if either side has < min_n samples
         - CONFLUENT if Z >= z_hi (default 2.0)
         - JOINT_REDUNDANT otherwise (gate splits into two groups
           with same forward return -- carries no marginal outcome
           information given the other gates)

  Strategy-level verdict aggregates per-gate:
    - NO_OP_CAMOUFLAGE if any gate is NO_OP_CAMOUFLAGE
    - JOINT_REDUNDANT if 2+ gates are JOINT_REDUNDANT
    - CONFLUENCE if all classified gates are CONFLUENT
    - MIXED otherwise (reports redundant gates separately)

  Additionally for JOINT_REDUNDANT diagnosis: compute sibling-R^2 for
  each gate against the OR-combination of other gates. High R^2 (>0.6)
  reinforces the redundancy signal but is NOT required -- the
  conditional outcome spread IS the discriminator.

VALIDATION:
  This module is validated against labeled synthetic cases in
  test_batch687_conditional_information_diagnostic.py:
    T10-like: 1 gate at ~99% True + 1 informative gate -> NO_OP_CAMOUFLAGE
    T3-like: 4 gates at ~45% True, all correlated proxies of one latent
             trend factor -> JOINT_REDUNDANT (caught where the pre-B687
             diagnostic clears it)
    Genuine confluence: 3 orthogonal failure-mode screens -> CONFLUENCE
                        (no false alarm)
    Mixed: 2 real + 1 redundant + 1 subsumed -> reports per-gate

  Decisive separation: redundant gates score ~0.4-1.4σ on the
  conditional outcome spread; genuine gates score 9-22σ. That gap is
  what the +0.41-correlation reasoning could not see.

CAVEATS (load-bearing, not boilerplate):
  - Requires a forward-return panel that is cost-adjusted (C6),
    survivorship-corrected (C5), and PIT-clean. Until B660 lands +
    survivorship verdict ships + cost-aware cube replay populates,
    diagnostic outputs are PENDING-B660 exactly like the fire counts.
  - Significance bar (z_hi=2.0) should inherit whatever C2 multiple-
    testing correction is applied -- testing many gates across many
    strategies inflates false positives at the cluster level.
  - "Other gates fire" subpopulation requires sufficient overlap;
    INCONCLUSIVE verdicts are honest deferrals, not silent failures.

USAGE:
  >>> from backtest.engine.conditional_information_gate_diagnostic import diagnose_strategy
  >>> result = diagnose_strategy(gate_matrix, forward_returns,
  ...                             gate_names=["near_s1", "rsi_oversold", ...])
  >>> result.verdict  # CONFLUENCE | NO_OP_CAMOUFLAGE | JOINT_REDUNDANT | MIXED
  >>> result.recommended_core_gates  # subset to keep per redundancy pruning
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np


# Diagnostic thresholds (tunable per cluster + per-cube C2 correction).
TRUE_RATE_NO_OP = 0.98       # Per-gate True-rate above this = NO_OP_CAMOUFLAGE (T10 catch)
Z_HI            = 2.0        # Conditional outcome spread Z >= this = CONFLUENT
MIN_N           = 30         # Per-side minimum sample size; below this = INCONCLUSIVE
R2_HI           = 0.60       # Sibling-R^2 above this reinforces redundancy signal


@dataclass
class GateResult:
    """Per-gate diagnostic output."""
    gate_name: str
    true_rate: float           # Fraction of all rows where gate is True
    n_keep: int                # Rows where other-gates-fire AND this gate True
    n_reject: int              # Rows where other-gates-fire AND this gate False
    mean_keep: float           # Mean forward-return on KEEP rows
    mean_reject: float         # Mean forward-return on REJECT rows
    conditional_z: float       # Z-score of (mean_keep - mean_reject)
    sibling_r2: float          # Max R^2 vs OR of other gates (0 if single-gate)
    verdict: str               # CONFLUENT | NO_OP_CAMOUFLAGE | JOINT_REDUNDANT | INCONCLUSIVE


@dataclass
class StrategyDiagnosticResult:
    """Strategy-level aggregated diagnostic output."""
    verdict: str                            # CONFLUENCE | NO_OP_CAMOUFLAGE | JOINT_REDUNDANT | MIXED | INCONCLUSIVE
    per_gate: list[GateResult] = field(default_factory=list)
    recommended_core_gates: list[str] = field(default_factory=list)
    notes: str = ""


def _sibling_r2(gate_matrix: np.ndarray, gate_idx: int) -> float:
    """R^2 of gate_idx against OR of all other gates.

    OR-combination is a strict-but-reasonable approximation of "do the
    other gates collectively fire alongside this gate." Pairwise max
    R^2 with siblings is an alternative; we use OR-combination because
    it captures joint-redundancy where no single sibling fully predicts
    but the combination does.
    """
    n_gates = gate_matrix.shape[1]
    if n_gates < 2:
        return 0.0
    gate_col = gate_matrix[:, gate_idx].astype(float)
    other_mask = np.ones(n_gates, dtype=bool)
    other_mask[gate_idx] = False
    other_or = (gate_matrix[:, other_mask].astype(int).sum(axis=1) > 0).astype(float)
    # R^2 = (cov(g, other_or))^2 / (var(g) * var(other_or))
    var_g = float(np.var(gate_col))
    var_o = float(np.var(other_or))
    if var_g <= 0.0 or var_o <= 0.0:
        return 0.0
    cov = float(np.cov(gate_col, other_or, ddof=0)[0, 1])
    r2 = (cov * cov) / (var_g * var_o)
    return float(min(max(r2, 0.0), 1.0))


def diagnose_gate(
    gate_matrix: np.ndarray,
    forward_returns: np.ndarray,
    gate_idx: int,
    gate_names: Sequence[str],
    true_rate_no_op: float = TRUE_RATE_NO_OP,
    z_hi: float = Z_HI,
    min_n: int = MIN_N,
) -> GateResult:
    """Diagnose a single gate's conditional information.

    Args:
        gate_matrix: shape (n_rows, n_gates) boolean / 0-1 matrix
        forward_returns: shape (n_rows,) forward-return panel
        gate_idx: index of gate to diagnose
        gate_names: names for all gates (parallel to gate_matrix columns)
    """
    gate_col = gate_matrix[:, gate_idx].astype(bool)
    n_rows = len(forward_returns)
    true_rate = float(gate_col.sum()) / n_rows if n_rows > 0 else 0.0
    name = gate_names[gate_idx]

    # NO_OP_CAMOUFLAGE: gate near-constant (rule A from T10 catch)
    if true_rate >= true_rate_no_op:
        return GateResult(
            gate_name=name,
            true_rate=true_rate,
            n_keep=int(gate_col.sum()),
            n_reject=int((~gate_col).sum()),
            mean_keep=float(np.mean(forward_returns[gate_col])) if gate_col.any() else 0.0,
            mean_reject=float(np.mean(forward_returns[~gate_col])) if (~gate_col).any() else 0.0,
            conditional_z=0.0,
            sibling_r2=_sibling_r2(gate_matrix, gate_idx),
            verdict="NO_OP_CAMOUFLAGE",
        )

    # Other-gates-fire subpopulation
    n_gates = gate_matrix.shape[1]
    if n_gates == 1:
        # No "other gates" -- diagnose against full population
        other_fire = np.ones(n_rows, dtype=bool)
    else:
        other_mask = np.ones(n_gates, dtype=bool)
        other_mask[gate_idx] = False
        other_fire = gate_matrix[:, other_mask].astype(bool).all(axis=1)

    keep = other_fire & gate_col
    reject = other_fire & (~gate_col)
    n_keep = int(keep.sum())
    n_reject = int(reject.sum())

    if n_keep < min_n or n_reject < min_n:
        return GateResult(
            gate_name=name,
            true_rate=true_rate,
            n_keep=n_keep,
            n_reject=n_reject,
            mean_keep=float(np.mean(forward_returns[keep])) if n_keep > 0 else 0.0,
            mean_reject=float(np.mean(forward_returns[reject])) if n_reject > 0 else 0.0,
            conditional_z=0.0,
            sibling_r2=_sibling_r2(gate_matrix, gate_idx),
            verdict="INCONCLUSIVE",
        )

    # Conditional outcome spread Z-score
    rk = forward_returns[keep]
    rr = forward_returns[reject]
    mean_keep = float(np.mean(rk))
    mean_reject = float(np.mean(rr))
    var_keep = float(np.var(rk, ddof=1))
    var_reject = float(np.var(rr, ddof=1))
    se = float(np.sqrt(var_keep / n_keep + var_reject / n_reject))
    if se <= 0.0:
        z = 0.0
    else:
        z = (mean_keep - mean_reject) / se

    sib_r2 = _sibling_r2(gate_matrix, gate_idx)

    if z >= z_hi:
        verdict = "CONFLUENT"
    else:
        verdict = "JOINT_REDUNDANT"

    return GateResult(
        gate_name=name,
        true_rate=true_rate,
        n_keep=n_keep,
        n_reject=n_reject,
        mean_keep=mean_keep,
        mean_reject=mean_reject,
        conditional_z=float(z),
        sibling_r2=sib_r2,
        verdict=verdict,
    )


def diagnose_strategy(
    gate_matrix: np.ndarray,
    forward_returns: np.ndarray,
    gate_names: Sequence[str],
    true_rate_no_op: float = TRUE_RATE_NO_OP,
    z_hi: float = Z_HI,
    min_n: int = MIN_N,
) -> StrategyDiagnosticResult:
    """Diagnose a strategy's full gate set.

    Returns a StrategyDiagnosticResult with per-gate findings + a
    strategy-level verdict + recommended core gates (the CONFLUENT
    subset, with redundant gates pruned).

    Strategy-level verdict logic:
        NO_OP_CAMOUFLAGE if any gate is NO_OP_CAMOUFLAGE (T10 case)
        JOINT_REDUNDANT if 2+ gates are JOINT_REDUNDANT (T3 case)
        CONFLUENCE if all classified gates are CONFLUENT (genuine case)
        INCONCLUSIVE if all gates are INCONCLUSIVE
        MIXED otherwise

    Per the validation harness: even within an otherwise-CONFLUENT
    strategy, individual JOINT_REDUNDANT gates are surfaced in
    per_gate so the redundant ones can be pruned from the recommended
    core. The strategy-level CONFLUENCE label requires zero redundant
    gates by default but reporting catches mixed cases.
    """
    n_rows, n_gates = gate_matrix.shape
    if len(forward_returns) != n_rows:
        raise ValueError(
            f"gate_matrix rows ({n_rows}) must match forward_returns ({len(forward_returns)})"
        )
    if len(gate_names) != n_gates:
        raise ValueError(
            f"gate_names ({len(gate_names)}) must match gate_matrix columns ({n_gates})"
        )

    per_gate = [
        diagnose_gate(
            gate_matrix, forward_returns, i, gate_names,
            true_rate_no_op=true_rate_no_op, z_hi=z_hi, min_n=min_n,
        )
        for i in range(n_gates)
    ]

    # Strategy-level aggregation
    verdicts = [g.verdict for g in per_gate]
    n_no_op = sum(1 for v in verdicts if v == "NO_OP_CAMOUFLAGE")
    n_redundant = sum(1 for v in verdicts if v == "JOINT_REDUNDANT")
    n_confluent = sum(1 for v in verdicts if v == "CONFLUENT")
    n_inconclusive = sum(1 for v in verdicts if v == "INCONCLUSIVE")
    n_classified = n_confluent + n_redundant + n_no_op

    if n_no_op > 0:
        strategy_verdict = "NO_OP_CAMOUFLAGE"
    elif n_classified == 0 and n_inconclusive > 0:
        strategy_verdict = "INCONCLUSIVE"
    elif n_redundant >= 2:
        strategy_verdict = "JOINT_REDUNDANT"
    elif n_confluent == n_classified and n_classified > 0:
        strategy_verdict = "CONFLUENCE"
    else:
        strategy_verdict = "MIXED"

    # Recommended core: CONFLUENT gates only (prune redundant + no-op)
    recommended_core = [g.gate_name for g in per_gate if g.verdict == "CONFLUENT"]
    # If all gates were redundant or no-op, recommend the highest-information
    # gate as a single core (collapse to most-informative single gate)
    if not recommended_core and n_classified > 0:
        best = max(
            (g for g in per_gate if g.verdict != "INCONCLUSIVE"),
            key=lambda g: g.conditional_z,
            default=None,
        )
        if best is not None and best.verdict != "NO_OP_CAMOUFLAGE":
            recommended_core = [best.gate_name]

    notes = (
        f"n_gates={n_gates} | n_confluent={n_confluent} | "
        f"n_redundant={n_redundant} | n_no_op={n_no_op} | "
        f"n_inconclusive={n_inconclusive}"
    )

    return StrategyDiagnosticResult(
        verdict=strategy_verdict,
        per_gate=per_gate,
        recommended_core_gates=recommended_core,
        notes=notes,
    )
