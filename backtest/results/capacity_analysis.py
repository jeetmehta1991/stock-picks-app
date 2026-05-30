"""Batch 476 (2026-05-29) -- M2 capacity analysis per cell.

A cell with Sharpe 1.0 backtested on tiny positions may not survive when
deployed at meaningful AUM. This module computes per-cell capacity flags
so the verdict pipeline can surface "Sharpe N is real but capacity is
$X" caveats.

Inputs (per trade row in the cube trade_log):
  - adv_at_entry      :  avg-daily-dollar-volume at entry (cached or
                         derived as close * volume mean over trailing 20d)
  - position_dollars  :  position notional at entry (capital * size_pct)

Outputs (per cell -- aggregated):
  median_adv_at_entry         -- median ADV across cell's trades
  median_position_dollars     -- median position dollar size across trades
  median_size_pct_of_adv      -- median(position_dollars / adv_at_entry)
  max_size_pct_of_adv         -- max(...) -- captures worst-case impact
  capacity_concern_flag       -- median > 0.001 (0.1pct of ADV; slippage
                                 risk rises sharply past this threshold per
                                 Almgren-Chriss 2001 implementation-shortfall
                                 model)

Future consumer: cube populator -- annotate per-cell metrics with the
capacity flag; dashboard surface a "capacity-fragile" filter.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd


# Threshold below which the strategy is considered execution-feasible without
# meaningful slippage. Almgren-Chriss 2001 + practitioner heuristics agree
# that crossing 0.1 percent of ADV per fill begins to bite spread + impact.
CAPACITY_ADV_THRESHOLD = 0.001


def compute_cell_capacity(
    adv_at_entry: Sequence[float],
    position_dollars: Sequence[float],
) -> dict:
    """Compute capacity metrics for one cell from two equal-length series.

    Returns dict with keys median_adv_at_entry, median_position_dollars,
    median_size_pct_of_adv, max_size_pct_of_adv, capacity_concern_flag.

    Empty input returns zeros.
    """
    adv = np.asarray(list(adv_at_entry), dtype=float)
    pos = np.asarray(list(position_dollars), dtype=float)
    if adv.size == 0 or pos.size == 0 or adv.size != pos.size:
        return {
            "n": 0,
            "median_adv_at_entry":      0.0,
            "median_position_dollars":  0.0,
            "median_size_pct_of_adv":   0.0,
            "max_size_pct_of_adv":      0.0,
            "capacity_concern_flag":    False,
        }
    # Drop rows with non-positive ADV (division undefined)
    mask = adv > 0
    if not mask.any():
        return {
            "n": int(adv.size),
            "median_adv_at_entry":      0.0,
            "median_position_dollars":  float(np.median(pos)),
            "median_size_pct_of_adv":   0.0,
            "max_size_pct_of_adv":      0.0,
            "capacity_concern_flag":    False,
        }
    adv_m = adv[mask]
    pos_m = pos[mask]
    ratios = pos_m / adv_m
    med_ratio = float(np.median(ratios))
    return {
        "n":                          int(mask.sum()),
        "median_adv_at_entry":        float(np.median(adv_m)),
        "median_position_dollars":    float(np.median(pos_m)),
        "median_size_pct_of_adv":     round(med_ratio, 6),
        "max_size_pct_of_adv":        round(float(np.max(ratios)), 6),
        "capacity_concern_flag":      bool(med_ratio > CAPACITY_ADV_THRESHOLD),
    }


def compute_cell_capacity_from_trade_log(
    trade_log: pd.DataFrame,
    group_cols: Sequence[str] = ("strategy", "exit_method", "regime"),
    adv_col: str = "adv_at_entry",
    pos_col: str = "position_dollars",
) -> pd.DataFrame:
    """Per-cell capacity metrics from a trade-log DataFrame.

    Empty input returns empty DataFrame with schema columns. Missing the
    required cols raises ValueError so the caller surfaces the gap rather
    than silently emitting all-zeros.
    """
    EMPTY_COLS = list(group_cols) + [
        "n", "median_adv_at_entry", "median_position_dollars",
        "median_size_pct_of_adv", "max_size_pct_of_adv",
        "capacity_concern_flag",
    ]
    if trade_log is None or trade_log.empty:
        return pd.DataFrame(columns=EMPTY_COLS)
    missing = [c for c in list(group_cols) + [adv_col, pos_col]
               if c not in trade_log.columns]
    if missing:
        raise ValueError(
            f"compute_cell_capacity_from_trade_log: trade_log missing {missing}"
        )
    rows = []
    for keys, sub in trade_log.groupby(list(group_cols), sort=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        m = compute_cell_capacity(
            sub[adv_col].astype(float).values,
            sub[pos_col].astype(float).values,
        )
        rows.append({**dict(zip(group_cols, keys)), **m})
    return pd.DataFrame(rows)
