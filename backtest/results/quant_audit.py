"""DEC-246 — Quant finance correctness audit (Pass 53 build per DEC-594 same-commit).

Validates Sharpe annualization, max drawdown computation, vol periodicity per
quant-finance canonical formulas. Catches off-by-sqrt-252 errors, intra-day
vs daily-bar ambiguity, and incorrect cumulative-vs-daily DD computation.

Per DEC-578 7-gate Phase 1B-α verdict: Sharpe (Gate 4) and DD (Gate 5) must
be computed correctly. This audit catches errors at codification time rather
than after Phase 1B-α run.

Status: PARTIAL-SPEC-ONLY → RESOLVED-DECIDED post artifact landing per DEC-594.
"""

from __future__ import annotations

from typing import Dict, Sequence

import numpy as np


TRADING_DAYS_PER_YEAR = 252
TRADING_DAYS_PER_MONTH = 21


def annualized_sharpe(
    returns: Sequence[float],
    periodicity: str = "daily",
    rf_annual: float = 0.0,
) -> float:
    """Annualized Sharpe ratio with explicit periodicity.

    Args:
        returns: per-period returns (decimal; e.g., 0.01 for 1%).
        periodicity: 'daily' / 'monthly' / 'annual'.
        rf_annual: annual risk-free rate (default 0).

    Returns:
        Annualized Sharpe scalar.

    Per DEC-246: this function is the canonical Sharpe — no other module should
    re-implement annualization. Common bugs caught:
      - sqrt(252) vs sqrt(12) — periodicity confusion
      - rf subtracted in wrong period
      - std with ddof=0 (population) vs ddof=1 (sample)
    """
    arr = np.asarray(returns, dtype=float)
    if len(arr) < 2:
        return 0.0

    periods_per_year = {
        "daily": TRADING_DAYS_PER_YEAR,
        "monthly": 12,
        "annual": 1,
    }.get(periodicity)
    if periods_per_year is None:
        raise ValueError(f"Unknown periodicity '{periodicity}'; expected daily/monthly/annual")

    rf_per_period = rf_annual / periods_per_year
    excess = arr - rf_per_period

    mean = excess.mean()
    std = excess.std(ddof=1)
    if std < 1e-12 or not np.isfinite(std):
        return 0.0

    return mean / std * np.sqrt(periods_per_year)


def max_drawdown(equity_curve: Sequence[float]) -> Dict[str, float]:
    """Maximum drawdown from peak equity.

    Args:
        equity_curve: cumulative equity values (length T; e.g., portfolio value over time).

    Returns:
        {
          "max_drawdown_pct": -0.X (negative; e.g., -0.20 for -20%),
          "peak_idx": index of peak preceding max DD,
          "trough_idx": index of trough at max DD,
          "duration_periods": trough_idx - peak_idx,
        }

    Per DEC-246: DD is computed on EQUITY CURVE (cumulative), not daily returns.
    Common bug: applying max() to daily returns and treating as DD — produces
    daily worst-loss, not peak-to-trough drawdown.
    """
    eq = np.asarray(equity_curve, dtype=float)
    if len(eq) < 2:
        return {"max_drawdown_pct": 0.0, "peak_idx": 0, "trough_idx": 0, "duration_periods": 0}

    running_max = np.maximum.accumulate(eq)
    drawdown = (eq - running_max) / running_max  # negative values
    trough_idx = int(np.argmin(drawdown))
    max_dd = float(drawdown[trough_idx])
    # Find peak preceding trough
    peak_idx = int(np.argmax(eq[: trough_idx + 1])) if trough_idx > 0 else 0

    return {
        "max_drawdown_pct": max_dd,
        "peak_idx": peak_idx,
        "trough_idx": trough_idx,
        "duration_periods": trough_idx - peak_idx,
    }


def annualized_vol(
    returns: Sequence[float],
    periodicity: str = "daily",
) -> float:
    """Annualized volatility (std × sqrt(periods/year))."""
    arr = np.asarray(returns, dtype=float)
    if len(arr) < 2:
        return 0.0
    periods_per_year = {
        "daily": TRADING_DAYS_PER_YEAR,
        "monthly": 12,
        "annual": 1,
    }.get(periodicity)
    if periods_per_year is None:
        raise ValueError(f"Unknown periodicity '{periodicity}'")
    std = arr.std(ddof=1)
    if not np.isfinite(std):
        return 0.0
    return float(std * np.sqrt(periods_per_year))


def audit_metric_consistency(
    returns: Sequence[float],
    sharpe_reported: float,
    vol_reported: float,
    max_dd_reported: float,
    equity_curve: Sequence[float] | None = None,
    tolerance_pct: float = 0.05,
) -> Dict[str, str]:
    """Validate reported metrics against canonical computation.

    Returns dict {metric: status} where status ∈ {"OK", "MISMATCH"}.

    Use case: Phase 1B-α verdict reports per-cell metrics; this audit re-derives
    each from raw trade returns and flags mismatches > tolerance_pct.
    """
    findings: Dict[str, str] = {}

    canonical_sharpe = annualized_sharpe(returns)
    if abs(canonical_sharpe - sharpe_reported) > tolerance_pct:
        findings["sharpe"] = (
            f"MISMATCH: reported={sharpe_reported:.4f} canonical={canonical_sharpe:.4f}"
        )
    else:
        findings["sharpe"] = "OK"

    canonical_vol = annualized_vol(returns)
    if abs(canonical_vol - vol_reported) > tolerance_pct:
        findings["vol"] = (
            f"MISMATCH: reported={vol_reported:.4f} canonical={canonical_vol:.4f}"
        )
    else:
        findings["vol"] = "OK"

    if equity_curve is not None:
        canonical_dd = max_drawdown(equity_curve)["max_drawdown_pct"]
        if abs(canonical_dd - max_dd_reported) > tolerance_pct:
            findings["max_drawdown"] = (
                f"MISMATCH: reported={max_dd_reported:.4f} canonical={canonical_dd:.4f}"
            )
        else:
            findings["max_drawdown"] = "OK"

    return findings
