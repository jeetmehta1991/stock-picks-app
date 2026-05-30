"""Batch 478 (2026-05-29) -- M9 correlation-aware confluence count.

Wraps the M1 strategy-correlation matrix into a helper that converts
"raw strategy_count firing on a ticker-day" into "effective independent
strategy_count" by counting CLUSTERS rather than individual strategies.

A confluence of 5 strategies that all derive from the same underlying
pattern (e.g. five Donchian-style breakout variants) should count as 1
independent signal, not 5. This module supplies the conversion.

API:
  build_strategy_cluster_lookup(corr_matrix, threshold)
      Pre-compute a {strategy_name -> cluster_id} dict from a correlation
      matrix. Returns ({}, 0) on an empty matrix. Threshold defaults to
      0.8 -- pairs at or above this absolute correlation collapse into
      one cluster.

  effective_strategy_count(strategy_names, lookup)
      Given a list of strategies firing on a ticker-day + the precomputed
      cluster lookup, return the count of distinct cluster_ids. Strategies
      not in the lookup count as their own cluster (singletons).

The engine consumer (`backtest.engine.backtest._assign_confidence_tier`)
should call `effective_strategy_count(firing_strategies, _CLUSTER_LOOKUP)`
in place of `len(firing_strategies)` when computing the confidence tier.
The lookup is built once per backtest from the cube trade_log (M1 output).
"""
from __future__ import annotations

from typing import Iterable

import pandas as pd

from backtest.results.strategy_correlation import cluster_correlated_strategies


def build_strategy_cluster_lookup(
    corr_matrix: pd.DataFrame,
    threshold: float = 0.8,
) -> tuple[dict[str, int], int]:
    """Map each strategy in the correlation matrix to a cluster id.

    Returns (lookup_dict, n_clusters). Empty matrix -> ({}, 0).
    """
    if corr_matrix is None or corr_matrix.empty:
        return {}, 0
    clusters = cluster_correlated_strategies(corr_matrix, threshold=threshold)
    lookup: dict[str, int] = {}
    for cluster_id, members in enumerate(clusters):
        for strat in members:
            lookup[strat] = cluster_id
    return lookup, len(clusters)


def effective_strategy_count(
    firing_strategies: Iterable[str],
    cluster_lookup: dict[str, int],
) -> int:
    """Count distinct CLUSTERS firing.

    Strategies not in `cluster_lookup` are treated as their own singleton
    cluster (use their name as the id). This keeps un-clustered strategies
    contributing to the confluence count -- correct behaviour during the
    pre-M1-data warmup period.
    """
    seen: set = set()
    next_singleton_id = -1
    for s in firing_strategies:
        cid = cluster_lookup.get(s)
        if cid is None:
            # Singleton fallback: use string id namespaced to avoid clash
            seen.add(f"__singleton__{s}")
        else:
            seen.add(cid)
    return len(seen)
