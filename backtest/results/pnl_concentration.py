"""Batch 474 (2026-05-29) -- M11 PnL concentration metrics per cell.

Detects cells whose Sharpe is driven by 1-2 outsized trades vs cells with
broadly distributed wins. A cell with Sharpe 1.5 might be a fragile
single-trade outlier (HHI -> 100%) or a robust broad winner (HHI -> 0).
This module exposes the distinction so the cube verdict pipeline can
flag concentration risk.

Outputs per cell:
  pnl_concentration_top1_pct  -- fraction of total absolute pnl in the
                                  single largest trade [0..1].
  pnl_concentration_top5_pct  -- fraction of total absolute pnl in the
                                  top 5 largest absolute trades [0..1].
  pnl_hhi                     -- Herfindahl-Hirschman Index on
                                  abs-pnl share-of-total. 1/n on a perfectly
                                  uniform distribution, 1.0 if one trade
                                  carries all the pnl.

Future consumer: cube populator (`backtest.results.cube_populator.
compute_cell_metrics`) -- merge these keys into the per-cell metrics dict
so the 5-Gate verdict can incorporate concentration as a soft gate
(e.g., reject cells with top1>50 percent as overfit).
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd


def compute_pnl_concentration(pnls: Sequence[float]) -> dict:
    """Compute concentration metrics for a 1-D iterable of per-trade pnls.

    Empty input returns zeros for all metrics + n=0. Single-trade input
    returns top1=1.0 + top5=1.0 + HHI=1.0 (entirely concentrated).
    """
    arr = np.asarray(list(pnls), dtype=float)
    n = int(arr.size)
    if n == 0:
        return {
            "n":                          0,
            "pnl_concentration_top1_pct": 0.0,
            "pnl_concentration_top5_pct": 0.0,
            "pnl_hhi":                    0.0,
        }
    abs_pnl = np.abs(arr)
    total = float(abs_pnl.sum())
    if total <= 0:
        return {
            "n":                          n,
            "pnl_concentration_top1_pct": 0.0,
            "pnl_concentration_top5_pct": 0.0,
            "pnl_hhi":                    0.0,
        }
    shares = abs_pnl / total
    sorted_shares = np.sort(shares)[::-1]  # descending
    top1 = float(sorted_shares[0])
    top5 = float(sorted_shares[:5].sum())
    hhi = float(np.sum(shares ** 2))
    return {
        "n":                          n,
        "pnl_concentration_top1_pct": round(top1, 6),
        "pnl_concentration_top5_pct": round(top5, 6),
        "pnl_hhi":                    round(hhi, 6),
    }


def compute_pnl_concentration_from_trade_log(
    trade_log: pd.DataFrame,
    group_cols: Sequence[str] = ("strategy", "exit_method", "regime"),
    pnl_col: str = "pnl_pct",
) -> pd.DataFrame:
    """Apply `compute_pnl_concentration` per (group_cols) cell of a trade
    log DataFrame. Returns one row per cell with the 4 metric columns +
    the group keys.

    Empty input returns empty DataFrame with the metric column schema.
    """
    EMPTY_COLS = list(group_cols) + [
        "n", "pnl_concentration_top1_pct",
        "pnl_concentration_top5_pct", "pnl_hhi",
    ]
    if trade_log is None or trade_log.empty:
        return pd.DataFrame(columns=EMPTY_COLS)
    missing = [c for c in group_cols if c not in trade_log.columns]
    if missing:
        raise ValueError(
            f"compute_pnl_concentration_from_trade_log: trade_log missing "
            f"group cols {missing}"
        )
    if pnl_col not in trade_log.columns:
        raise ValueError(
            f"compute_pnl_concentration_from_trade_log: missing pnl_col "
            f"{pnl_col!r}"
        )
    rows = []
    for keys, sub in trade_log.groupby(list(group_cols), sort=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        m = compute_pnl_concentration(sub[pnl_col].astype(float).values)
        rows.append({**dict(zip(group_cols, keys)), **m})
    return pd.DataFrame(rows)
