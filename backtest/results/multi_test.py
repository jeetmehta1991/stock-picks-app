"""DEC-401 — Holm-Bonferroni step-down multi-comparison correction (Pass 53 build per DEC-594).

Less conservative than vanilla Bonferroni when test statistics are correlated
(common in cube cells with shared underlying trades). Per DEC-080 Phase B:
add Holm-Bonferroni step-down option as alternative to Bonferroni for the
Phase 1B-α 7-gate verdict (Gate 2 cross-strategy + Gate 4 cross-cell-within-strategy).

Per DEC-582 Pass 53: Gate 2 and Gate 4 use distinct correction scopes;
Holm-Bonferroni applies to BOTH.

Status: PARTIAL-SPEC-ONLY → RESOLVED-DECIDED post artifact landing per DEC-594.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

import numpy as np


def holm_bonferroni(
    pvalues: Sequence[float],
    alpha: float = 0.05,
) -> Tuple[List[bool], List[float]]:
    """Holm-Bonferroni step-down correction.

    Args:
        pvalues: raw p-values from independent tests (length m).
        alpha: family-wise error rate (FWER) target.

    Returns:
        rejected: list[bool] — True if H_i rejected at FWER ≤ alpha
        adjusted: list[float] — Holm-adjusted p-values (capped at 1.0)

    Algorithm (Holm 1979):
        1. Sort p-values ascending: p_(1) ≤ p_(2) ≤ ... ≤ p_(m)
        2. For i = 1..m: if p_(i) ≤ alpha / (m - i + 1), reject H_(i)
                        else stop (cannot reject H_(i) or any later)
        3. Adjusted p-values: max running cumulative max of (m - i + 1) * p_(i),
           ensuring monotonicity.

    Less conservative than Bonferroni: vanilla Bonferroni divides alpha by m
    for ALL tests; Holm divides by (m - i + 1) for the i-th smallest, which
    relaxes the threshold for less-significant tests after most-significant
    are already accepted.
    """
    m = len(pvalues)
    if m == 0:
        return [], []

    pvals = np.asarray(pvalues, dtype=float)
    if np.any((pvals < 0) | (pvals > 1)):
        raise ValueError("p-values must be in [0, 1]")

    order = np.argsort(pvals)
    sorted_pvals = pvals[order]
    adjusted_sorted = np.zeros(m)

    running_max = 0.0
    for i in range(m):
        # Holm factor: m - i (since i is 0-indexed, m - i = m - i for the i-th smallest)
        adj = sorted_pvals[i] * (m - i)
        running_max = max(running_max, adj)
        adjusted_sorted[i] = min(running_max, 1.0)

    # Unsort back to original order
    adjusted = np.zeros(m)
    adjusted[order] = adjusted_sorted

    rejected = (adjusted <= alpha).tolist()
    return rejected, adjusted.tolist()


def bonferroni(
    pvalues: Sequence[float],
    alpha: float = 0.05,
) -> Tuple[List[bool], List[float]]:
    """Vanilla Bonferroni correction for comparison/baseline (DEC-080 parent).

    Args:
        pvalues: raw p-values (length m).
        alpha: FWER target.

    Returns:
        rejected: list[bool]
        adjusted: list[float] — adjusted p-values = min(p * m, 1.0)

    Always more conservative than Holm-Bonferroni; rejects fewer hypotheses.
    """
    m = len(pvalues)
    if m == 0:
        return [], []
    pvals = np.asarray(pvalues, dtype=float)
    if np.any((pvals < 0) | (pvals > 1)):
        raise ValueError("p-values must be in [0, 1]")
    adjusted = np.minimum(pvals * m, 1.0)
    rejected = (adjusted <= alpha).tolist()
    return rejected, adjusted.tolist()
