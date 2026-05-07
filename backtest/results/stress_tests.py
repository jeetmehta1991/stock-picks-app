"""DEC-405 — Stress test suite (DEC-082 implementation; Pass 53 build per DEC-594).

Filter trades to specific historical stress regimes and compute per-stress
metrics. Per DEC-082 spec: 2022 full-year stress (rate hikes + tech drawdown);
Pass 53 extends to 2020-Q1 COVID + 2018-Q4 selloff per DEC-405.

Phase 1B-α 7-gate verdict (DEC-578) Gate 5 = stress-test pass per regime.

Status: PARTIAL-SPEC-ONLY → RESOLVED-DECIDED post artifact landing per DEC-594.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Sequence

import pandas as pd


# Stress windows per DEC-405 + DEC-082 spec
STRESS_WINDOWS = {
    "2018Q4_selloff": (date(2018, 10, 1), date(2018, 12, 31)),
    "2020Q1_covid": (date(2020, 2, 1), date(2020, 4, 30)),
    "2022_full_year": (date(2022, 1, 1), date(2022, 12, 31)),
    "2022Q4_inflation": (date(2022, 9, 1), date(2022, 12, 31)),
}


def filter_trades_to_window(
    trades_df: pd.DataFrame,
    window_start: date,
    window_end: date,
    date_col: str = "entry_date",
) -> pd.DataFrame:
    """Filter trade log to a specific date window.

    Args:
        trades_df: trade log with at least `date_col`.
        window_start, window_end: inclusive date bounds.
        date_col: name of date column (default 'entry_date').

    Returns:
        Subset DataFrame with trades whose date_col ∈ [window_start, window_end].
    """
    if date_col not in trades_df.columns:
        raise KeyError(f"trades_df missing column '{date_col}'")
    s = pd.to_datetime(trades_df[date_col])
    mask = (s.dt.date >= window_start) & (s.dt.date <= window_end)
    return trades_df.loc[mask].copy()


def per_stress_metrics(
    trades_df: pd.DataFrame,
    pnl_col: str = "pnl_pct",
    date_col: str = "entry_date",
) -> Dict[str, Dict[str, float]]:
    """Compute per-stress-window metrics for a trade log.

    Args:
        trades_df: trade log with pnl_pct + date_col.
        pnl_col: column with per-trade P&L percent (e.g., 0.05 for +5%).
        date_col: entry date column.

    Returns:
        {
          stress_name: {
            "n_trades": int,
            "win_rate": float,
            "mean_pnl_pct": float,
            "total_pnl_pct": float,
            "verdict": "PASS" | "FAIL" | "INSUFFICIENT_SAMPLE",
          }
        }

    Per DEC-405 acceptance:
      - PASS = total_pnl_pct ≥ -10% AND win_rate ≥ 0.40 within stress window
      - FAIL = total_pnl_pct < -10% OR win_rate < 0.40
      - INSUFFICIENT_SAMPLE = n_trades < 20
    """
    results: Dict[str, Dict[str, float]] = {}

    for stress_name, (start, end) in STRESS_WINDOWS.items():
        subset = filter_trades_to_window(trades_df, start, end, date_col=date_col)
        n = len(subset)
        if n < 20:
            results[stress_name] = {
                "n_trades": n,
                "win_rate": 0.0,
                "mean_pnl_pct": 0.0,
                "total_pnl_pct": 0.0,
                "verdict": "INSUFFICIENT_SAMPLE",
            }
            continue

        wins = (subset[pnl_col] > 0).sum()
        win_rate = wins / n
        mean_pnl = float(subset[pnl_col].mean())
        total_pnl = float(subset[pnl_col].sum())

        if total_pnl >= -0.10 and win_rate >= 0.40:
            verdict = "PASS"
        else:
            verdict = "FAIL"

        results[stress_name] = {
            "n_trades": int(n),
            "win_rate": float(win_rate),
            "mean_pnl_pct": mean_pnl,
            "total_pnl_pct": total_pnl,
            "verdict": verdict,
        }

    return results


def stress_summary(per_stress: Dict[str, Dict[str, float]]) -> Dict[str, int]:
    """Aggregate verdict counts across stress windows."""
    summary = {"PASS": 0, "FAIL": 0, "INSUFFICIENT_SAMPLE": 0}
    for stress_name, metrics in per_stress.items():
        v = metrics.get("verdict", "INSUFFICIENT_SAMPLE")
        summary[v] = summary.get(v, 0) + 1
    return summary
