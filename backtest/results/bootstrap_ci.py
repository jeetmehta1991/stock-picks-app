"""DEC-423 — Per-cell bootstrap CI + pairwise significance (Pass 53 build per DEC-594).

Per DEC-068 expansion (DEC-422 cube): bootstrap operates at PER-CELL level
(not per-strategy). For each cell in dimensional cube:
  1. 1000-resample bootstrap on cell trades
  2. Compute Sharpe (or other metric) on each resample
  3. Empirical CI = (2.5 percentile, 97.5 percentile) → 95% CI

Pairwise significance: for two strategies in the same cell, bootstrap their
Sharpe difference + test 0 ∉ 95% CI.

Per DEC-582 Pass 53: this is the per-cell-within-strategy correction layer
(Gate 4 of 7-gate Phase 1B-α verdict). Pairwise comparisons within cube cell
get Bonferroni-corrected by total cell-pair count.

Per DEC-153: cells with n < 30 trades fall back to marginal-best per dimension
(no bootstrap).

Status: PARTIAL-SPEC-ONLY → RESOLVED-DECIDED post artifact landing per DEC-594.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np

DEFAULT_RESAMPLES = 1000
DEFAULT_CI_LEVEL = 0.95
MIN_TRADES_FOR_BOOTSTRAP = 30


@dataclass
class BootstrapResult:
    point_estimate: float
    ci_low: float
    ci_high: float
    n: int
    n_resamples: int
    method: str  # "bootstrap" or "fallback_marginal_best" or "insufficient_sample"


def sharpe_ratio(returns: Sequence[float]) -> float:
    """Annualized Sharpe assuming daily returns; rf = 0.

    Returns 0 for constant or near-constant return series (std below floating-
    point precision threshold) to avoid numerical-noise blowups.
    """
    arr = np.asarray(returns, dtype=float)
    if len(arr) < 2:
        return 0.0
    mean = arr.mean()
    std = arr.std(ddof=1)
    # Guard against numerical precision: 1e-12 floor catches both exact-0 and
    # constant-array float residue (e.g., np.std([0.001]*252, ddof=1) ≈ 1e-19).
    if std < 1e-12 or not np.isfinite(std):
        return 0.0
    return mean / std * np.sqrt(252)


def bootstrap_metric(
    trade_returns: Sequence[float],
    metric_fn: Callable[[Sequence[float]], float] = sharpe_ratio,
    n_resamples: int = DEFAULT_RESAMPLES,
    ci_level: float = DEFAULT_CI_LEVEL,
    min_trades: int = MIN_TRADES_FOR_BOOTSTRAP,
    seed: int = 42,
) -> BootstrapResult:
    """Bootstrap CI for a metric on trade returns.

    Args:
        trade_returns: per-trade return values (length n).
        metric_fn: callable(returns) → metric scalar; default = annualized Sharpe.
        n_resamples: bootstrap iterations.
        ci_level: confidence level (e.g., 0.95 for 95% CI).
        min_trades: minimum trades to run bootstrap; fewer → INSUFFICIENT_SAMPLE.
        seed: RNG seed for reproducibility.

    Returns:
        BootstrapResult with point_estimate, ci_low, ci_high, n, n_resamples, method.
    """
    arr = np.asarray(trade_returns, dtype=float)
    n = len(arr)

    if n < min_trades:
        # Insufficient sample → cannot bootstrap reliably
        point = metric_fn(arr) if n > 0 else 0.0
        return BootstrapResult(
            point_estimate=point,
            ci_low=float("nan"),
            ci_high=float("nan"),
            n=n,
            n_resamples=0,
            method="insufficient_sample",
        )

    rng = np.random.default_rng(seed)
    point = metric_fn(arr)
    samples = np.empty(n_resamples)
    for i in range(n_resamples):
        resample = rng.choice(arr, size=n, replace=True)
        samples[i] = metric_fn(resample)

    alpha = (1 - ci_level) / 2
    ci_low = float(np.quantile(samples, alpha))
    ci_high = float(np.quantile(samples, 1 - alpha))

    return BootstrapResult(
        point_estimate=float(point),
        ci_low=ci_low,
        ci_high=ci_high,
        n=n,
        n_resamples=n_resamples,
        method="bootstrap",
    )


def pairwise_sharpe_diff_significance(
    returns_a: Sequence[float],
    returns_b: Sequence[float],
    n_resamples: int = DEFAULT_RESAMPLES,
    ci_level: float = DEFAULT_CI_LEVEL,
    seed: int = 42,
) -> Tuple[float, float, float, bool]:
    """Pairwise bootstrap of Sharpe(A) - Sharpe(B); significant if 0 ∉ CI.

    Args:
        returns_a, returns_b: per-trade return arrays for two strategies in same cell.
        n_resamples: bootstrap iterations.
        ci_level: confidence level.
        seed: RNG seed.

    Returns:
        (point_diff, ci_low, ci_high, significant)
        significant = True iff CI excludes 0.
    """
    a = np.asarray(returns_a, dtype=float)
    b = np.asarray(returns_b, dtype=float)
    if len(a) < MIN_TRADES_FOR_BOOTSTRAP or len(b) < MIN_TRADES_FOR_BOOTSTRAP:
        point_diff = sharpe_ratio(a) - sharpe_ratio(b)
        return point_diff, float("nan"), float("nan"), False

    rng = np.random.default_rng(seed)
    diffs = np.empty(n_resamples)
    for i in range(n_resamples):
        ra = rng.choice(a, size=len(a), replace=True)
        rb = rng.choice(b, size=len(b), replace=True)
        diffs[i] = sharpe_ratio(ra) - sharpe_ratio(rb)

    alpha = (1 - ci_level) / 2
    ci_low = float(np.quantile(diffs, alpha))
    ci_high = float(np.quantile(diffs, 1 - alpha))
    point_diff = float(sharpe_ratio(a) - sharpe_ratio(b))
    significant = not (ci_low <= 0 <= ci_high)
    return point_diff, ci_low, ci_high, significant
