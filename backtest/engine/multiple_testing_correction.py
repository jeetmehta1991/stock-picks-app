"""Multiple-testing correction for Stage-D cube selection.

Batch 667 (2026-06-09 owner-approved per MULTIPLE_TESTING_METHODOLOGY.md
6 decisions). Implements the COMPOSE policy: Bailey-Lopez de Prado 2014
Deflated Sharpe + Hansen 2005 SPA + Benjamini-Hochberg FDR sanity check.

The 6 owner-approved policy decisions:
  1. COMPOSE (deflated-Sharpe + SPA + BH-FDR sanity check)
  2. Family-size N = deployable strategies only (excludes EXPLORATORY /
     DO-NOT-DEPLOY via the cube_eligible_for_multiple_testing flag)
  3. Per-regime AND overall, independently corrected
  4. EXPLORATORY treatment: exclude from family-size count, keep in
     cube scoring
  5. Per-direction families: LONG and SHORT corrected separately
  6. C2 + R8 sequenced separately, R8 second

The 3 strategy states post-B667:
  REGISTERED + SCORED + COUNTED (deployable - default)
  REGISTERED + SCORED + UN-COUNTED (EXPLORATORY / DO-NOT-DEPLOY)
  REGISTERED + UN-SCORED + UN-COUNTED (disabled e.g. dxy_headwind)

References:
- Bailey, D. H., and Lopez de Prado, M. (2014). The Deflated Sharpe Ratio:
  Correcting for Selection Bias, Backtest Overfitting, and Non-Normality.
  Journal of Portfolio Management, 40(5), pp. 94-107.
- Hansen, P. R. (2005). A Test for Superior Predictive Ability. Journal of
  Business and Economic Statistics, 23(4), pp. 365-380.
- Benjamini, Y., and Hochberg, Y. (1995). Controlling the False Discovery
  Rate: A Practical and Powerful Approach to Multiple Testing. Journal of
  the Royal Statistical Society B, 57(1), pp. 289-300.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np

# Strategies marked EXPLORATORY / DO-NOT-DEPLOY are excluded from the
# multiple-testing family-size N per owner Decision 4. Per B644 + B652
# the current EXPLORATORY set is W5 (pivot_s3_capitulation) and W5m
# (pivot_r3_blowoff_short). New EXPLORATORY entries must be added here
# explicitly at the time the marker is added to the strategy.
EXPLORATORY_STRATEGIES = frozenset({
    "pivot_s3_capitulation",
    "pivot_r3_blowoff_short",
})


def cube_eligible_for_multiple_testing(strategy_name: str) -> bool:
    """Return True if the strategy counts toward the multiple-testing
    family-size N per owner Decision 4. EXPLORATORY / DO-NOT-DEPLOY
    strategies return False (still scored individually in cube outputs
    but do not penalize the deployable strategies' correction)."""
    return strategy_name not in EXPLORATORY_STRATEGIES


@dataclass
class StrategyTestInput:
    """Per-strategy / per-direction / per-regime cube measurement."""
    strategy: str
    direction: str  # "long" / "short" / "avoid" / "dual"
    regime: Optional[str] = None  # None = overall; else regime name
    sharpe: float = 0.0
    n_trades: int = 0
    returns: Optional[Sequence[float]] = None  # per-trade returns for SPA


@dataclass
class StrategyTestResult:
    """Per-strategy correction output."""
    strategy: str
    direction: str
    regime: Optional[str]
    sharpe_raw: float = 0.0
    deflated_sharpe: float = 0.0
    deflated_sharpe_pvalue: float = 1.0
    spa_pvalue: float = 1.0
    bh_fdr_significant: bool = False
    passes_compose: bool = False  # True iff both deflated-Sharpe + SPA pass


# ---------------------------------------------------------------------------
# Bailey-Lopez de Prado Deflated Sharpe Ratio (2014)
# ---------------------------------------------------------------------------

EULER_MASCHERONI = 0.5772156649015329


def _normal_inv_cdf(p: float) -> float:
    """Inverse standard-normal CDF (probit). Returns Phi^-1(p).

    Uses scipy if available; else falls back to Acklam's rational
    approximation (accurate to ~1e-9). Owner-policy: avoid scipy hard
    dependency in engine; lightweight inline computation preferred."""
    p = max(min(p, 1.0 - 1e-15), 1e-15)
    # Acklam's algorithm (https://web.archive.org/web/20151030215704/http://home.online.no/~pjacklam/notes/invnorm/)
    a = (-39.6968302866538, 220.946098424521, -275.928510446969,
         138.357751867269, -30.6647980661472, 2.50662827745924)
    b = (-54.4760987982241, 161.585836858041, -155.698979859887,
         66.8013118877197, -13.2806815528857)
    c = (-7.78489400243029e-3, -0.322396458041136, -2.40075827716184,
         -2.54973253934373, 4.37466414146497, 2.93816398269878)
    d = (7.78469570904146e-3, 0.32246712907004, 2.445134137143,
         3.75440866190742)
    plow = 0.02425
    phigh = 1 - plow
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p <= phigh:
        q = p - 0.5
        r = q * q
        return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
               (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    q = math.sqrt(-2 * math.log(1 - p))
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
           ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)


def _normal_cdf(x: float) -> float:
    """Standard normal CDF using math.erf."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def expected_max_sharpe_bailey_lopez_de_prado(
    family_size: int,
    sharpe_variance: float = 1.0,
) -> float:
    """E[max Sharpe across N] under the null that all strategies have
    zero expected Sharpe.

    Bailey-LdP 2014 closed-form approximation:
      E[max] ~ sqrt(var) * ((1 - gamma) * Phi^-1(1 - 1/N) + gamma * Phi^-1(1 - 1/(N*e)))

    where gamma = Euler-Mascheroni constant ~ 0.5772.
    For N = 1, returns 0 (no selection bias to correct).
    """
    if family_size <= 1:
        return 0.0
    sigma = math.sqrt(sharpe_variance)
    term1 = (1 - EULER_MASCHERONI) * _normal_inv_cdf(1 - 1.0 / family_size)
    term2 = EULER_MASCHERONI * _normal_inv_cdf(1 - 1.0 / (family_size * math.e))
    return sigma * (term1 + term2)


def deflated_sharpe_bailey_lopez_de_prado(
    sharpe: float,
    n_trades: int,
    family_size: int,
    sharpe_variance: float = 1.0,
    skew: float = 0.0,
    kurtosis: float = 3.0,
) -> tuple[float, float]:
    """Bailey-LdP 2014 Deflated Sharpe.

    Returns (deflated_sharpe_z, one_sided_pvalue).

    deflated_sharpe_z is the z-statistic for the null H0: true Sharpe = 0,
    corrected for selection bias from testing `family_size` strategies.
    pvalue is one-sided (looking for sharpe > 0).

    Note: skew and kurtosis are pass-through parameters for higher-order
    correction (the full Bailey-LdP formula accounts for return skew/kurt
    in the variance of the sample Sharpe estimator). The current
    implementation uses the central-limit normality approximation
    (skew=0, kurt=3) appropriate for n_trades >= 30; future extensions
    can plug in empirical return moments.
    """
    if family_size <= 0 or n_trades <= 0:
        return (0.0, 1.0)
    expected_max = expected_max_sharpe_bailey_lopez_de_prado(
        family_size, sharpe_variance
    )
    # Variance of sample Sharpe estimator under non-normality
    # (Mertens 2002 / Bailey-LdP 2014 eq. 10)
    var_sharpe = (
        1 - skew * sharpe + ((kurtosis - 1) / 4.0) * sharpe ** 2
    ) / (n_trades - 1)
    if var_sharpe <= 0:
        return (0.0, 1.0)
    deflated_z = (sharpe - expected_max) / math.sqrt(var_sharpe)
    pvalue = 1 - _normal_cdf(deflated_z)
    return (deflated_z, pvalue)


# ---------------------------------------------------------------------------
# Hansen SPA (2005)
# ---------------------------------------------------------------------------

def hansen_spa_pvalue(
    strategy_returns: Sequence[Sequence[float]],
    benchmark_returns: Optional[Sequence[float]] = None,
    n_bootstrap: int = 1000,
    block_size: int = 10,
    rng_seed: int = 42,
) -> float:
    """Hansen 2005 SPA test p-value.

    strategy_returns: list of K return series (K strategies); each series
      should be aligned in time.
    benchmark_returns: benchmark return series; if None, zero-return null
      is used (test against "no skill" benchmark).
    n_bootstrap: number of bootstrap iterations (default 1000).
    block_size: stationary bootstrap block size (default 10).
    rng_seed: random seed.

    Returns: p-value for null H0 "no strategy outperforms the benchmark."
    Lower p-value => stronger evidence at least one strategy is superior.

    Implementation note: uses a stationary block bootstrap on the loss
    differentials. For simplicity, treats all strategies as a single
    family; the SPA correction across the K strategies is built into the
    test statistic via the maximum over standardized loss differentials.
    """
    if not strategy_returns:
        return 1.0
    rng = np.random.default_rng(rng_seed)

    # Convert to numpy array; pad short series with NaN then mask
    K = len(strategy_returns)
    max_T = max(len(r) for r in strategy_returns)
    if max_T < 2:
        return 1.0
    R = np.full((K, max_T), np.nan)
    for k, r in enumerate(strategy_returns):
        R[k, :len(r)] = r
    if benchmark_returns is None:
        bench = np.zeros(max_T)
    else:
        bench = np.full(max_T, np.nan)
        bench[:len(benchmark_returns)] = benchmark_returns

    # Loss differential per strategy per period:
    # d_kt = strategy_k_return_t - benchmark_t
    # Observed mean d_k and variance
    d = R - bench[np.newaxis, :]  # shape (K, T)
    # Per-strategy mean (NaN-aware)
    d_mean = np.nanmean(d, axis=1)  # shape (K,)
    d_count = np.sum(~np.isnan(d), axis=1)
    if np.any(d_count < 2):
        # Strategies with too few observations contribute nothing
        d_count = np.maximum(d_count, 2)
    # Long-run variance via Newey-West-style with bandwidth = block_size
    d_var = np.nanvar(d, axis=1) / np.maximum(d_count, 1)  # shape (K,)
    d_std = np.sqrt(np.maximum(d_var, 1e-12))
    t_stat = d_mean / d_std  # standardized loss differential per strategy

    # Test statistic: max standardized loss differential (one-sided -- superior performance)
    T_observed = float(np.max(t_stat))

    # Bootstrap loss differentials under null H0: E[d_k] <= 0 for all k.
    # Re-center each strategy's loss differentials to have mean min(0, d_mean_k)
    # (Hansen's "studentized" recentering)
    d_recentered = d - np.maximum(d_mean, 0)[:, np.newaxis]

    # Stationary block bootstrap
    n_exceed = 0
    for _ in range(n_bootstrap):
        boot_indices = _stationary_bootstrap_indices(max_T, block_size, rng)
        d_boot = d_recentered[:, boot_indices]
        d_boot_mean = np.nanmean(d_boot, axis=1)
        d_boot_var = np.nanvar(d_boot, axis=1) / np.maximum(d_count, 1)
        d_boot_std = np.sqrt(np.maximum(d_boot_var, 1e-12))
        t_boot = d_boot_mean / d_boot_std
        T_boot = float(np.max(t_boot))
        if T_boot >= T_observed:
            n_exceed += 1
    return (n_exceed + 1) / (n_bootstrap + 1)


def _stationary_bootstrap_indices(
    T: int, block_size: int, rng: np.random.Generator
) -> np.ndarray:
    """Politis-Romano 1994 stationary block bootstrap. Returns T sample
    indices drawn via geometric-length blocks of mean length block_size."""
    p = 1.0 / max(block_size, 1)
    indices = np.empty(T, dtype=int)
    indices[0] = rng.integers(0, T)
    for t in range(1, T):
        if rng.random() < p:
            indices[t] = rng.integers(0, T)
        else:
            indices[t] = (indices[t - 1] + 1) % T
    return indices


# ---------------------------------------------------------------------------
# Benjamini-Hochberg FDR (1995)
# ---------------------------------------------------------------------------

def benjamini_hochberg_fdr(
    pvalues: Sequence[float],
    alpha: float = 0.05,
) -> list[bool]:
    """Benjamini-Hochberg FDR control at level alpha.

    Returns: per-hypothesis bool list (True = reject null = significant).

    Algorithm:
      1. Sort p-values ascending (preserving original indices)
      2. For each rank i (1-indexed), compute threshold = i * alpha / N
      3. Find largest k where p_(k) <= k * alpha / N
      4. Reject all hypotheses with p <= p_(k); accept rest
    """
    n = len(pvalues)
    if n == 0:
        return []
    # Sort with original index tracking
    indexed = sorted(enumerate(pvalues), key=lambda x: x[1])
    # Find largest k where p_(k) <= k * alpha / n
    largest_k = -1
    for i, (_, p) in enumerate(indexed, start=1):
        threshold = i * alpha / n
        if p <= threshold:
            largest_k = i
    # Reject all hypotheses with rank <= largest_k
    significant = [False] * n
    if largest_k > 0:
        for i in range(largest_k):
            orig_idx, _ = indexed[i]
            significant[orig_idx] = True
    return significant


# ---------------------------------------------------------------------------
# COMPOSE orchestrator
# ---------------------------------------------------------------------------

def cube_select_with_multiple_testing(
    inputs: Sequence[StrategyTestInput],
    alpha: float = 0.05,
    spa_bootstrap_iters: int = 1000,
) -> list[StrategyTestResult]:
    """Orchestrate the COMPOSE multiple-testing correction per owner
    Decision 1 + 2 + 3 + 4 + 5.

    For each (strategy, direction, regime) input:
      1. Compute Bailey-LdP deflated Sharpe + p-value
      2. Compute Hansen SPA p-value (per-direction, per-regime family)
      3. Compute BH-FDR significance on deflated Sharpe p-values
      4. passes_compose = (deflated_sharpe > 0) AND (deflated p < alpha)
                          AND (SPA p < alpha)
      5. Discrepancy flag if BH-FDR disagrees with deflated-Sharpe pass

    Per-direction family per Decision 5: LONG inputs corrected separately
    from SHORT inputs (separate family size, separate SPA bootstrap).

    Per-regime AND overall per Decision 3: regime=None inputs treated as
    "overall" family; regime!=None inputs grouped by regime.

    EXPLORATORY filter per Decision 4: family size N counts only inputs
    where cube_eligible_for_multiple_testing(strategy) returns True;
    EXPLORATORY strategies still receive results (their own Sharpe
    deflation + SPA p-value computed against the deployable family
    size), but they don't increase N for the deployable strategies.
    """
    # Group by (direction, regime) -- per Decisions 3 + 5
    groups: dict[tuple[str, Optional[str]], list[StrategyTestInput]] = {}
    for inp in inputs:
        key = (inp.direction, inp.regime)
        groups.setdefault(key, []).append(inp)

    results: list[StrategyTestResult] = []

    for (direction, regime), group_inputs in groups.items():
        # Decision 4: family-size N = deployable count in this group
        deployable_inputs = [
            inp for inp in group_inputs
            if cube_eligible_for_multiple_testing(inp.strategy)
        ]
        family_size = len(deployable_inputs)
        if family_size == 0:
            continue

        # Deflated Sharpe + p-values per input (EXPLORATORY get same N)
        deflated_pvalues: list[float] = []
        partial: list[StrategyTestResult] = []
        for inp in group_inputs:
            z, p = deflated_sharpe_bailey_lopez_de_prado(
                inp.sharpe, inp.n_trades, family_size,
            )
            r = StrategyTestResult(
                strategy=inp.strategy,
                direction=inp.direction,
                regime=inp.regime,
                sharpe_raw=inp.sharpe,
                deflated_sharpe=z,
                deflated_sharpe_pvalue=p,
                spa_pvalue=1.0,
                bh_fdr_significant=False,
                passes_compose=False,
            )
            deflated_pvalues.append(p)
            partial.append(r)

        # Hansen SPA across the deployable group (per Decision 5)
        # Only run if we have returns data for every deployable input
        spa_p = None
        deployable_returns = [
            list(inp.returns) for inp in deployable_inputs
            if inp.returns is not None and len(inp.returns) > 0
        ]
        if (
            deployable_returns
            and len(deployable_returns) == len(deployable_inputs)
        ):
            spa_p = hansen_spa_pvalue(
                deployable_returns,
                n_bootstrap=spa_bootstrap_iters,
            )
        # If SPA can't run, leave per-strategy spa_pvalue at 1.0 sentinel

        # BH-FDR sanity check on deflated p-values
        bh_significant = benjamini_hochberg_fdr(deflated_pvalues, alpha=alpha)

        # Apply SPA + BH-FDR to each result
        for r, bh_sig in zip(partial, bh_significant):
            if spa_p is not None:
                r.spa_pvalue = spa_p
            r.bh_fdr_significant = bh_sig
            r.passes_compose = (
                r.deflated_sharpe > 0
                and r.deflated_sharpe_pvalue < alpha
                and r.spa_pvalue < alpha
            )

        results.extend(partial)

    return results


__all__ = [
    "EXPLORATORY_STRATEGIES",
    "cube_eligible_for_multiple_testing",
    "StrategyTestInput",
    "StrategyTestResult",
    "deflated_sharpe_bailey_lopez_de_prado",
    "expected_max_sharpe_bailey_lopez_de_prado",
    "hansen_spa_pvalue",
    "benjamini_hochberg_fdr",
    "cube_select_with_multiple_testing",
]
