"""B668 (2026-06-09) -- Stage-D cube replay path integration of the COMPOSE
multi-testing correction per MULTIPLE_TESTING_METHODOLOGY.md owner-
approved decisions (B667).

Wraps `cube_select_with_multiple_testing()` from
`backtest.engine.multiple_testing_correction` to operate on a trade-log
DataFrame (`df_trades`) + emit a per-(strategy, direction, regime) verdict
output `cube_compose_verdict.csv` alongside the existing DEC-578 7-gate
`verdict_cube.csv`.

ARCHITECTURE NOTE (B668 owner-approved): this module adds a PARALLEL
artifact alongside the existing 7-gate verdict; it does NOT replace
Gate 2 (Bonferroni) or Gate 3 (DSR) in the 7-gate path. Reviewer +
cube tooling can A/B compare the two verdict paths. Replacing 7-gate
Gate 2 + Gate 3 with the COMPOSE module is a future B-N decision
requiring explicit owner approval per
`feedback_local_changes_default_global_needs_approval` (would touch the
load-bearing 7-gate path used by ~5 test files).

Per-strategy mean returns + Sharpe + n_trades are aggregated from
`df_trades` grouped by (strategy, direction, regime); inputs are then
fed to `cube_select_with_multiple_testing()`. EXPLORATORY strategies
(W5 + W5m per `EXPLORATORY_STRATEGIES`) appear in the output with their
correction results but DO NOT raise the family-size N for deployable
strategies -- per Decision 4 (B667).
"""
from __future__ import annotations

import logging
from typing import Sequence

import numpy as np
import pandas as pd

from backtest.engine.multiple_testing_correction import (
    StrategyTestInput,
    StrategyTestResult,
    cube_select_with_multiple_testing,
)

logger = logging.getLogger(__name__)


def _sharpe_from_returns(returns: np.ndarray) -> float:
    """Sample Sharpe ratio (mean / std). Returns 0 on insufficient data."""
    if len(returns) < 2:
        return 0.0
    std = float(np.std(returns, ddof=1))
    if std <= 0:
        return 0.0
    return float(np.mean(returns) / std)


def _resolve_direction(group_df: pd.DataFrame) -> str:
    """Resolve direction from a group sub-frame. Falls back to 'long' if
    no direction column is present."""
    if "direction" not in group_df.columns:
        return "long"
    directions = group_df["direction"].dropna().unique().tolist()
    if not directions:
        return "long"
    if len(directions) == 1:
        return str(directions[0]).lower()
    # Mixed directions in a (strategy, regime) cell -- treat as 'dual'
    return "dual"


def compute_cube_compose_verdict(
    df_trades: pd.DataFrame,
    pnl_col: str = "pnl_pct",
    cell_id_cols: Sequence[str] = ("strategy", "regime_at_entry"),
    alpha: float = 0.05,
    spa_bootstrap_iters: int = 1000,
    include_overall: bool = True,
) -> pd.DataFrame:
    """Compute the COMPOSE multi-testing verdict for a trade log.

    Args:
        df_trades: trade-level DataFrame with at least `pnl_col` + a
            `strategy` column + optionally `regime_at_entry` + `direction`.
        pnl_col: column with per-trade return (decimal; e.g. 0.05 = +5%).
        cell_id_cols: dimensions defining a cell. Default
            ("strategy", "regime_at_entry") groups per-strategy per-regime.
        alpha: significance level (default 0.05).
        spa_bootstrap_iters: Hansen SPA bootstrap iterations (default 1000).
        include_overall: if True, also emit "overall" rows (regime=None
            aggregation per strategy + direction).

    Returns:
        DataFrame with one row per (strategy, direction, regime) cell.
        Columns:
          strategy, direction, regime, sharpe_raw, n_trades,
          deflated_sharpe, deflated_sharpe_pvalue, spa_pvalue,
          bh_fdr_significant, passes_compose
    """
    if df_trades.empty or "strategy" not in df_trades.columns:
        return pd.DataFrame()

    available_cols = [c for c in cell_id_cols if c in df_trades.columns]
    if not available_cols:
        return pd.DataFrame()

    # Build StrategyTestInput list. Per-regime first (if regime col present),
    # then overall (regime=None) appended if include_overall.
    inputs: list[StrategyTestInput] = []

    # Per-regime / per-cell aggregation
    for cell_keys, cell_df in df_trades.groupby(list(available_cols), dropna=False):
        if not isinstance(cell_keys, tuple):
            cell_keys = (cell_keys,)
        cell_dict = dict(zip(available_cols, cell_keys))
        strategy = str(cell_dict.get("strategy", ""))
        regime = cell_dict.get("regime_at_entry") or cell_dict.get("regime")
        if pd.isna(regime):
            regime = None
        elif regime is not None:
            regime = str(regime)

        returns = cell_df[pnl_col].dropna().astype(float).values
        if len(returns) < 2:
            continue

        direction = _resolve_direction(cell_df)
        inputs.append(StrategyTestInput(
            strategy=strategy,
            direction=direction,
            regime=regime,
            sharpe=_sharpe_from_returns(returns),
            n_trades=len(returns),
            returns=returns.tolist(),
        ))

    # Overall aggregation: per (strategy, direction) regardless of regime.
    # Skipped when no regime column is present in df_trades -- the per-cell
    # aggregation already produces regime=None rows in that case (which
    # are functionally the "overall" rows). Adding the overall loop here
    # would double-count strategies.
    has_regime_dim = (
        "regime_at_entry" in df_trades.columns
        or "regime" in df_trades.columns
    )
    if include_overall and has_regime_dim:
        for strategy_name, strat_df in df_trades.groupby("strategy", dropna=False):
            if pd.isna(strategy_name):
                continue
            returns = strat_df[pnl_col].dropna().astype(float).values
            if len(returns) < 2:
                continue
            direction = _resolve_direction(strat_df)
            inputs.append(StrategyTestInput(
                strategy=str(strategy_name),
                direction=direction,
                regime=None,  # overall sentinel
                sharpe=_sharpe_from_returns(returns),
                n_trades=len(returns),
                returns=returns.tolist(),
            ))

    if not inputs:
        return pd.DataFrame()

    results = cube_select_with_multiple_testing(
        inputs, alpha=alpha, spa_bootstrap_iters=spa_bootstrap_iters,
    )

    rows = []
    for r in results:
        rows.append({
            "strategy": r.strategy,
            "direction": r.direction,
            "regime": r.regime if r.regime is not None else "overall",
            "sharpe_raw": round(r.sharpe_raw, 4),
            "deflated_sharpe": round(r.deflated_sharpe, 4),
            "deflated_sharpe_pvalue": round(r.deflated_sharpe_pvalue, 6),
            "spa_pvalue": round(r.spa_pvalue, 6),
            "bh_fdr_significant": bool(r.bh_fdr_significant),
            "passes_compose": bool(r.passes_compose),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(
            ["regime", "direction", "strategy"]
        ).reset_index(drop=True)
    return df


def emit_cube_compose_verdict_csv(
    df_trades: pd.DataFrame,
    output_path,
    pnl_col: str = "pnl_pct",
    alpha: float = 0.05,
    spa_bootstrap_iters: int = 1000,
) -> dict:
    """Compute + write `cube_compose_verdict.csv`. Returns summary dict.

    Called from `backtest/results/writer.py` alongside the DEC-578
    `verdict_cube.csv` emission.
    """
    cell_id_cols = ["strategy"]
    if "regime_at_entry" in df_trades.columns:
        cell_id_cols.append("regime_at_entry")
    elif "regime" in df_trades.columns:
        cell_id_cols.append("regime")

    df_compose = compute_cube_compose_verdict(
        df_trades, pnl_col=pnl_col,
        cell_id_cols=cell_id_cols,
        alpha=alpha,
        spa_bootstrap_iters=spa_bootstrap_iters,
    )

    if df_compose.empty:
        return {
            "n_cells": 0, "n_passes": 0, "n_bh_significant": 0,
            "discrepancy_count": 0,
            "written": False,
        }

    df_compose.to_csv(output_path, index=False)
    n_cells = len(df_compose)
    n_passes = int(df_compose["passes_compose"].sum())
    n_bh = int(df_compose["bh_fdr_significant"].sum())
    # Discrepancy: BH says significant but COMPOSE says NOT pass (or vice versa)
    discrepancy_count = int(
        (df_compose["bh_fdr_significant"] != df_compose["passes_compose"]).sum()
    )
    return {
        "n_cells": n_cells,
        "n_passes": n_passes,
        "n_bh_significant": n_bh,
        "discrepancy_count": discrepancy_count,
        "written": True,
    }


__all__ = [
    "compute_cube_compose_verdict",
    "emit_cube_compose_verdict_csv",
]
