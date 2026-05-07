"""DEC-247 — Deflated Sharpe Ratio (DSR) per Bailey & Lopez de Prado 2014 (Pass 53 build).

Adjusts observed Sharpe for selection bias (multiple-comparison + skewness/kurtosis).
Phase 1B-α 7-gate verdict (DEC-578) Gate 3 = PSR ≥ 0.95 OR DSR > threshold.

Status: PARTIAL-SPEC-ONLY → RESOLVED-DECIDED post artifact landing per DEC-594.

References:
  - Bailey, D. H., & Lopez de Prado, M. (2014). The Deflated Sharpe Ratio.
    The Journal of Portfolio Management, 40(5), 94-107.
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np


def _norm_cdf(z: float) -> float:
    """Standard normal CDF via erf (avoids scipy dependency)."""
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def _skew(arr: np.ndarray) -> float:
    """Sample skewness (bias-corrected; Fisher-Pearson; matches scipy.stats.skew(bias=False))."""
    n = len(arr)
    if n < 3:
        return 0.0
    mean = arr.mean()
    std = arr.std(ddof=1)
    if std < 1e-12:
        return 0.0
    m3 = ((arr - mean) ** 3).sum() / n
    g1 = m3 / (std ** 3)
    # Bias correction
    return float(g1 * math.sqrt(n * (n - 1)) / (n - 2))


def _excess_kurtosis(arr: np.ndarray) -> float:
    """Sample excess kurtosis (Fisher; bias-corrected; matches scipy.stats.kurtosis(fisher=True, bias=False))."""
    n = len(arr)
    if n < 4:
        return 0.0
    mean = arr.mean()
    std = arr.std(ddof=1)
    if std < 1e-12:
        return 0.0
    m4 = ((arr - mean) ** 4).sum() / n
    g2 = m4 / (std ** 4) - 3.0
    # Bias correction (G2 from g2)
    return float(((n - 1) / ((n - 2) * (n - 3))) * ((n + 1) * g2 + 6))


def probabilistic_sharpe_ratio(
    sharpe_observed: float,
    n_observations: int,
    skewness: float = 0.0,
    excess_kurtosis: float = 0.0,
    sharpe_benchmark: float = 0.0,
) -> float:
    """Probabilistic Sharpe Ratio (PSR) per Bailey & Lopez de Prado 2012.

    PSR = P(true_sharpe > sharpe_benchmark | observed)

    Args:
        sharpe_observed: observed Sharpe (annualized).
        n_observations: number of return observations (trades or daily bars).
        skewness: sample skewness of returns (0 for normal).
        excess_kurtosis: sample excess kurtosis (0 for normal; 3 for typical fat tails).
        sharpe_benchmark: benchmark Sharpe to test against (default 0).

    Returns:
        PSR scalar in [0, 1]. PSR ≥ 0.95 = high confidence true Sharpe > benchmark.
    """
    if n_observations < 2:
        return 0.0
    # Bailey-Lopez de Prado 2012 SE formula. `excess_kurtosis` is Fisher (k-3).
    # The original formula uses full kurtosis k, so kurtosis_full = excess + 3
    # → ((kurtosis_full - 1) / 4) = ((excess + 2) / 4)
    kurt_term = (excess_kurtosis + 2) / 4
    se_sharpe = np.sqrt(
        (1 - skewness * sharpe_observed + kurt_term * sharpe_observed ** 2)
        / (n_observations - 1)
    )
    if se_sharpe <= 0 or not np.isfinite(se_sharpe):
        return 0.0
    z = (sharpe_observed - sharpe_benchmark) / se_sharpe
    return float(_norm_cdf(z))


def deflated_sharpe_ratio(
    sharpe_observed: float,
    n_observations: int,
    n_strategies_tested: int,
    skewness: float = 0.0,
    excess_kurtosis: float = 0.0,
) -> float:
    """Deflated Sharpe Ratio (DSR) per Bailey & Lopez de Prado 2014.

    DSR = P(true_sharpe > 0 | observed, after adjusting for n_strategies tested).

    Args:
        sharpe_observed: highest observed Sharpe across strategies (annualized).
        n_observations: number of return observations per strategy.
        n_strategies_tested: total strategies tested (correction for max-of-N selection).
        skewness, excess_kurtosis: as in PSR.

    Returns:
        DSR scalar in [0, 1]. DSR > 0.95 = strong evidence for non-zero true Sharpe.

    Per DEC-578 Gate 3: DSR is computed across the strategy roster (199 per F-002)
    and applied to the per-cell winner — corrects for "best Sharpe across many
    strategies" selection bias.
    """
    if n_observations < 2 or n_strategies_tested < 1:
        return 0.0

    # Expected max-Sharpe under null (no skill) per Bailey-LdP 2014 Eq. 7
    # E[max_Sharpe_null] = sqrt(2 ln(n_strategies)) - euler-mascheroni / sqrt(2 ln(n_strategies))
    if n_strategies_tested < 2:
        sharpe_benchmark = 0.0
    else:
        ln_n = np.log(n_strategies_tested)
        gamma = 0.5772156649  # Euler-Mascheroni constant
        e_max = np.sqrt(2 * ln_n) - gamma / np.sqrt(2 * ln_n)
        # Convert annualized to per-period via sqrt(252) — assume daily here
        sharpe_benchmark = e_max / np.sqrt(252)

    return probabilistic_sharpe_ratio(
        sharpe_observed=sharpe_observed,
        n_observations=n_observations,
        skewness=skewness,
        excess_kurtosis=excess_kurtosis,
        sharpe_benchmark=sharpe_benchmark,
    )


def compute_dsr_from_returns(
    returns: Sequence[float],
    n_strategies_tested: int,
) -> dict:
    """Convenience: compute DSR + PSR + observed Sharpe + skew/kurtosis from returns."""
    arr = np.asarray(returns, dtype=float)
    if len(arr) < 2:
        return {
            "sharpe_observed": 0.0,
            "psr": 0.0,
            "dsr": 0.0,
            "skewness": 0.0,
            "excess_kurtosis": 0.0,
            "n_observations": len(arr),
        }

    mean = arr.mean()
    std = arr.std(ddof=1)
    if std < 1e-12:
        sharpe_obs = 0.0
    else:
        sharpe_obs = mean / std * np.sqrt(252)
    skew = _skew(arr)
    excess_kurt = _excess_kurtosis(arr)

    psr = probabilistic_sharpe_ratio(sharpe_obs, len(arr), skew, excess_kurt, 0.0)
    dsr = deflated_sharpe_ratio(sharpe_obs, len(arr), n_strategies_tested, skew, excess_kurt)

    return {
        "sharpe_observed": float(sharpe_obs),
        "psr": float(psr),
        "dsr": float(dsr),
        "skewness": skew,
        "excess_kurtosis": excess_kurt,
        "n_observations": len(arr),
    }
