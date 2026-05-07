"""Per-exit conditional analysis (Pass 53 Day-9-evening 2026-05-07).

Owner directive: "We are not analyzing universal exit strategies. We are
looking for best exit strategies that work optimally under different set of
variables."

Re-framed from prior single-dim "best exit per dim" framing:

  WRONG (universal-best framing):
    For each (strategy, regime), what's the best exit?  →  picks a winner.

  RIGHT (per-exit conditional framing):
    For each exit method, under what conditions does it dominate?
      → characterize each exit by the variable-combinations where it wins.

Outputs:
  1) exit_method_multi_dim_cube.csv  — long-form aggregate with metrics per
     (exit_method × condition-combo). Condition-combo = (regime × sector ×
     cap_band × vol_band × hold_duration_band) by default; configurable.
  2) exit_sweet_spots.csv  — per-exit ranked list of conditions where THIS
     exit ranks #1 vs other exits (with edge-over-runner-up).
  3) exit_pairwise_dominance.csv  — for each (exit_A, exit_B, condition),
     does A beat B by ≥X% pnl with ≥N trades?

Per DEC-594 same-commit: artifact + tests + writer wiring all land together.
"""

from __future__ import annotations

from typing import List, Optional, Sequence

import numpy as np
import pandas as pd


# Default condition dimensions for multi-dim cube (5 dims; ~2,112 combos before
# filtering to populated cells). All from exit_context CONTEXT_COLUMN_NAMES.
DEFAULT_CONDITION_DIMS = (
    "regime_at_entry",
    "sector",
    "cap_band",
    "vol_band",
    "hold_duration_band",
)

# Metrics per cell
DEFAULT_METRICS = ("n", "win_rate", "avg_pnl_pct", "total_pnl_pct", "sharpe_proxy")

MIN_TRADES_PER_CELL = 5  # cells with fewer than this are dropped (insufficient sample)
SWEET_SPOT_MIN_TRADES = 10  # tighter threshold for sweet-spot ranking


def compute_multi_dim_cube(
    trade_exit_detail: pd.DataFrame,
    dims: Sequence[str] = DEFAULT_CONDITION_DIMS,
    min_trades_per_cell: int = MIN_TRADES_PER_CELL,
) -> pd.DataFrame:
    """Aggregate trade_exit_detail by (exit_method × dims-combo) → metrics.

    Long-form output: one row per (exit_method, dim_1=value, ..., dim_N=value).

    Args:
        trade_exit_detail: full counterfactual trade_exit_detail.csv data.
        dims: condition dimension column names from exit_context.
        min_trades_per_cell: drop cells with fewer trades (insufficient sample).

    Returns:
        DataFrame with columns: exit_method, *dims, n, win_rate, avg_pnl_pct,
        total_pnl_pct, sharpe_proxy.
    """
    if trade_exit_detail is None or trade_exit_detail.empty:
        return pd.DataFrame()

    # Verify dims present
    missing_dims = [d for d in dims if d not in trade_exit_detail.columns]
    if missing_dims:
        raise KeyError(f"trade_exit_detail missing dim columns: {missing_dims}")

    group_cols = ["exit_method", *dims]
    agg = (trade_exit_detail.groupby(group_cols, dropna=False)
                            .agg(
                                n=("pnl_pct", "size"),
                                win_rate=("win", "mean"),
                                avg_pnl_pct=("pnl_pct", "mean"),
                                total_pnl_pct=("pnl_pct", "sum"),
                                std_pnl_pct=("pnl_pct", "std"),
                            ).reset_index())

    # Sharpe-proxy = avg/std × sqrt(n) — rough cell-level metric (not annualized)
    agg["sharpe_proxy"] = np.where(
        (agg["std_pnl_pct"].fillna(0) > 1e-12) & (agg["n"] > 1),
        agg["avg_pnl_pct"] / agg["std_pnl_pct"] * np.sqrt(agg["n"]),
        0.0,
    )

    # Filter under-sampled cells
    agg = agg[agg["n"] >= min_trades_per_cell].copy()
    return agg.drop(columns=["std_pnl_pct"])


def find_sweet_spots(
    cube: pd.DataFrame,
    dims: Sequence[str] = DEFAULT_CONDITION_DIMS,
    primary_metric: str = "total_pnl_pct",
    top_k: int = 20,
    min_trades: int = SWEET_SPOT_MIN_TRADES,
) -> pd.DataFrame:
    """Per-exit top-K conditions where this exit dominates other exits.

    For each cell (dim-combo), rank exits by primary_metric. For each exit,
    collect cells where IT ranks #1 — these are its sweet spots.

    Args:
        cube: output of compute_multi_dim_cube.
        dims: condition dimensions used to define cells.
        primary_metric: metric to rank exits by within each cell.
        top_k: per-exit top-K cells to surface (sorted by edge over runner-up).
        min_trades: cells with fewer trades excluded.

    Returns:
        DataFrame with columns: exit_method, *dims, primary_metric_value,
        runner_up_method, runner_up_metric, edge_over_runner_up, n_trades, rank.
        Per exit_method, rows sorted by edge (descending).
    """
    if cube.empty:
        return pd.DataFrame()

    cube_filt = cube[cube["n"] >= min_trades].copy()
    if cube_filt.empty:
        return pd.DataFrame()

    # Rank exits within each cell by primary_metric (descending)
    cube_filt["rank_in_cell"] = cube_filt.groupby(list(dims))[primary_metric].rank(
        ascending=False, method="dense"
    )

    # Compute runner-up metric per cell (rank=2)
    cell_groups = cube_filt.groupby(list(dims))
    runner_up_data = cell_groups.apply(
        lambda g: pd.Series({
            "runner_up_method": (g.loc[g["rank_in_cell"] == 2, "exit_method"].iloc[0]
                                  if (g["rank_in_cell"] == 2).any() else None),
            "runner_up_metric": (g.loc[g["rank_in_cell"] == 2, primary_metric].iloc[0]
                                  if (g["rank_in_cell"] == 2).any() else None),
            "n_exits_in_cell": int(g["exit_method"].nunique()),
        }),
        include_groups=False,
    ).reset_index()

    # Filter to winners (rank=1) and join runner-up info
    winners = cube_filt[cube_filt["rank_in_cell"] == 1].merge(
        runner_up_data, on=list(dims), how="left"
    )

    winners["edge_over_runner_up"] = (
        winners[primary_metric] - winners["runner_up_metric"].fillna(0)
    )

    # For each exit method, take top-K by edge
    sweet_spots_rows = []
    for exit_name in winners["exit_method"].unique():
        exit_winners = winners[winners["exit_method"] == exit_name].copy()
        exit_winners = exit_winners.sort_values("edge_over_runner_up", ascending=False)
        sweet_spots_rows.append(exit_winners.head(top_k))

    if not sweet_spots_rows:
        return pd.DataFrame()

    result = pd.concat(sweet_spots_rows, ignore_index=True)
    # Final column ordering
    cols = (["exit_method"] + list(dims) +
            [primary_metric, "runner_up_method", "runner_up_metric",
             "edge_over_runner_up", "n", "n_exits_in_cell", "rank_in_cell"])
    cols = [c for c in cols if c in result.columns]
    return result[cols]


def compute_pairwise_dominance(
    cube: pd.DataFrame,
    dims: Sequence[str] = DEFAULT_CONDITION_DIMS,
    metric: str = "total_pnl_pct",
    edge_threshold: float = 0.01,
    min_trades: int = SWEET_SPOT_MIN_TRADES,
) -> pd.DataFrame:
    """For each (exit_A, exit_B, dim-combo), report whether A dominates B.

    Dominance = exit_A.metric - exit_B.metric ≥ edge_threshold
                AND both have ≥ min_trades.

    Returns long-form DataFrame: exit_a, exit_b, *dims, a_metric, b_metric,
    edge, dominates (bool), n_a, n_b.
    """
    if cube.empty:
        return pd.DataFrame()

    cube_filt = cube[cube["n"] >= min_trades].copy()
    if cube_filt.empty:
        return pd.DataFrame()

    # Self-join: pivot exit_method to columns within cell
    rows: List[dict] = []
    for cell_keys, cell in cube_filt.groupby(list(dims)):
        if not isinstance(cell_keys, tuple):
            cell_keys = (cell_keys,)
        exits_in_cell = cell["exit_method"].tolist()
        for i, ea in enumerate(exits_in_cell):
            for eb in exits_in_cell[i + 1:]:
                ra = cell[cell["exit_method"] == ea].iloc[0]
                rb = cell[cell["exit_method"] == eb].iloc[0]
                edge = float(ra[metric] - rb[metric])
                row = {
                    "exit_a": ea, "exit_b": eb,
                    **{dim: cell_keys[idx] for idx, dim in enumerate(dims)},
                    f"a_{metric}": float(ra[metric]),
                    f"b_{metric}": float(rb[metric]),
                    "edge": edge,
                    "dominates": edge >= edge_threshold,
                    "n_a": int(ra["n"]), "n_b": int(rb["n"]),
                }
                rows.append(row)

    return pd.DataFrame(rows) if rows else pd.DataFrame()
