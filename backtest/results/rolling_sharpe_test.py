"""DEC-415 — Rolling 1-year Sharpe deviation test (Pass 53 build per DEC-594).

Per DEC-111 Phase B: compute Sharpe over 252-day rolling windows; flag strategies
with high deviation across windows (unstable edge).

Phase 1B-α 7-gate verdict (DEC-578) Gate 7 = rolling Sharpe stability.

Status: PARTIAL-SPEC-ONLY → RESOLVED-DECIDED post artifact landing per DEC-594.
"""

from __future__ import annotations

from typing import Dict, Sequence

import numpy as np
import pandas as pd


WINDOW_DAYS = 252  # 1 trading year


def rolling_sharpe(
    returns: Sequence[float],
    window: int = WINDOW_DAYS,
) -> pd.Series:
    """Rolling annualized Sharpe over `window`-day windows.

    Args:
        returns: daily-bar returns (length T).
        window: rolling window size in days (default 252 = 1 year).

    Returns:
        pandas Series of length T-window+1 with rolling annualized Sharpe values.
        Index is the END date of each window (rightmost).
    """
    s = pd.Series(returns, dtype=float)
    if len(s) < window + 1:
        return pd.Series(dtype=float)

    mean = s.rolling(window=window).mean()
    std = s.rolling(window=window).std(ddof=1)
    # Drop windows with zero std (returns NaN); drop windows below `window`-size (also NaN)
    sharpe = (mean / std) * np.sqrt(252)
    sharpe = sharpe.where(std > 1e-12, np.nan)
    return sharpe.dropna().reset_index(drop=True)


def rolling_sharpe_stability(
    returns: Sequence[float],
    window: int = WINDOW_DAYS,
    deviation_threshold: float = 0.5,
) -> Dict[str, float]:
    """Stability metrics for rolling 1-year Sharpe.

    Args:
        returns: daily-bar returns.
        window: rolling window (default 252).
        deviation_threshold: max acceptable std-dev of rolling Sharpe across windows.

    Returns:
        {
          "rolling_sharpe_mean": float,
          "rolling_sharpe_std": float,
          "rolling_sharpe_min": float,
          "rolling_sharpe_max": float,
          "windows_below_zero": int (count of windows with Sharpe < 0),
          "stability_verdict": "STABLE" | "UNSTABLE",
        }

    Per DEC-415: stability = std(rolling_sharpe) ≤ deviation_threshold.
    Strategies with std > threshold are flagged for further review (possible
    regime-dependence) but NOT auto-rejected.
    """
    rs = rolling_sharpe(returns, window=window)
    if rs.empty:
        return {
            "rolling_sharpe_mean": 0.0,
            "rolling_sharpe_std": 0.0,
            "rolling_sharpe_min": 0.0,
            "rolling_sharpe_max": 0.0,
            "windows_below_zero": 0,
            "stability_verdict": "INSUFFICIENT_DATA",
        }

    mean = float(rs.mean())
    std = float(rs.std(ddof=1)) if len(rs) >= 2 else 0.0
    min_v = float(rs.min())
    max_v = float(rs.max())
    below_zero = int((rs < 0).sum())
    verdict = "STABLE" if std <= deviation_threshold else "UNSTABLE"

    return {
        "rolling_sharpe_mean": mean,
        "rolling_sharpe_std": std,
        "rolling_sharpe_min": min_v,
        "rolling_sharpe_max": max_v,
        "windows_below_zero": below_zero,
        "stability_verdict": verdict,
    }
