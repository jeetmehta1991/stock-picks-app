"""Batch 475 (2026-05-29) -- M1 inter-strategy correlation matrix.

For a trade log spanning N strategies, computes pairwise correlation of
entry-day firing series. Two strategies that fire on identical days are
NOT independent signals -- their cube confluence count is inflated. The
resulting matrix lets the verdict pipeline / dashboard surface redundant
strategy pairs.

OUTPUT:
  compute_strategy_correlation_matrix(trade_log)
    -> pd.DataFrame N x N of pairwise correlations of per-strategy daily
       entry-count series (entry_date -> count of entries per strategy).
       Diagonal = 1.0, off-diagonal = pearson r.

  cluster_correlated_strategies(corr_matrix, threshold=0.8)
    -> list[set[str]] : connected components of the graph where edges
       are pairs with |corr| >= threshold. Each component is a cluster
       of mutually-redundant strategies.

UPSTREAM consumer (follow-on; not wired in this batch):
  `_assign_confidence_tier` in backtest/engine/backtest.py should compute
  `effective_strategy_count` = number of distinct CLUSTERS firing on a
  given ticker-day, not raw `strategy_count`. M9 in the execution queue
  tracks this wiring.
"""
from __future__ import annotations

from typing import Sequence

import pandas as pd


def compute_strategy_correlation_matrix(
    trade_log: pd.DataFrame,
    entry_date_col: str = "entry_date",
    strategy_col: str = "strategy",
) -> pd.DataFrame:
    """Pairwise correlation of per-strategy daily entry-count series.

    Returns N x N DataFrame indexed by strategy name with Pearson r as
    values. Empty input returns empty DataFrame. Strategies with zero
    variance (constant firing rate) get NaN in their off-diagonal cells.
    """
    if trade_log is None or trade_log.empty:
        return pd.DataFrame()
    if entry_date_col not in trade_log.columns \
            or strategy_col not in trade_log.columns:
        raise ValueError(
            f"trade_log missing required cols: "
            f"{entry_date_col!r} or {strategy_col!r}"
        )
    df = trade_log[[entry_date_col, strategy_col]].copy()
    df["_d"] = pd.to_datetime(df[entry_date_col], errors="coerce")
    df = df.dropna(subset=["_d"])
    if df.empty:
        return pd.DataFrame()
    # Per-strategy daily entry count
    grouped = df.groupby([strategy_col, "_d"]).size().rename("n").reset_index()
    pivot = grouped.pivot(index="_d", columns=strategy_col, values="n").fillna(0)
    # Pearson on the daily entry-count columns.
    return pivot.corr(method="pearson")


def cluster_correlated_strategies(
    corr_matrix: pd.DataFrame,
    threshold: float = 0.8,
) -> list[set[str]]:
    """Group strategies into clusters where every pair within the cluster
    has |correlation| >= threshold (transitive connection).

    Implements union-find on the upper-triangle of the matrix. Returns a
    list of sets; singletons (strategies with no correlated neighbour)
    appear as 1-element sets.
    """
    if corr_matrix is None or corr_matrix.empty:
        return []
    names = list(corr_matrix.columns)
    parent: dict[str, str] = {n: n for n in names}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i, a in enumerate(names):
        for b in names[i + 1:]:
            val = corr_matrix.loc[a, b]
            if pd.isna(val):
                continue
            if abs(float(val)) >= threshold:
                union(a, b)

    clusters: dict[str, set[str]] = {}
    for n in names:
        root = find(n)
        clusters.setdefault(root, set()).add(n)
    return list(clusters.values())


def redundant_strategy_pairs(
    corr_matrix: pd.DataFrame,
    threshold: float = 0.8,
) -> list[tuple[str, str, float]]:
    """List strategy pairs whose |correlation| meets `threshold`. Useful
    for dashboard reporting + roster-pruning recommendations."""
    if corr_matrix is None or corr_matrix.empty:
        return []
    names = list(corr_matrix.columns)
    out: list[tuple[str, str, float]] = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            val = corr_matrix.loc[a, b]
            if pd.isna(val):
                continue
            if abs(float(val)) >= threshold:
                out.append((a, b, float(val)))
    # Sort by |corr| desc for dashboard readability
    out.sort(key=lambda t: -abs(t[2]))
    return out
