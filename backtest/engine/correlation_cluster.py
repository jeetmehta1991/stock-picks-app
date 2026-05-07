"""DEC-509 strategy correlation cluster gate (Pass 53 Day-9 v8g).

Spec source: TRADING_RULES_AND_INFORMATION.md / AUDIT.md §"Pass 53 Q2 — DEC-509".

Pre-Phase-1B-α gate: pairwise return correlation on 1y in-sample; cluster at
ρ > 0.7; clusters with >3 members retain highest-Sharpe representative + flag
rest as "redundant variants" with `correlation_cluster_id` field. Redundant
variants run in backtest but are excluded from Phase 1B-α verdict.

Implements DEC-509 + DEC-513 #4 correlation matrix module together — they
share the `compute_correlation_matrix()` primitive.

Public API:
  compute_correlation_matrix(returns_by_strategy, lookback=252) → DataFrame N×N
  cluster_strategies(corr_df, threshold=0.7) → list of clusters
  flag_redundant_variants(strategy_returns, sharpes, threshold=0.7)
      → DataFrame with columns [strategy, correlation_cluster_id,
        is_primary, is_redundant_variant]
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# DEC-513 #4 — Correlation matrix module
# ---------------------------------------------------------------------------
def compute_correlation_matrix(
    returns_by_strategy: Dict[str, pd.Series],
    lookback: int = 252,
) -> pd.DataFrame:
    """Pairwise return correlation matrix across strategies.

    Args:
        returns_by_strategy: dict mapping strategy_name -> pd.Series of
            daily returns (DatetimeIndex preferred but not required).
        lookback: most-recent N return observations to use per strategy.

    Returns:
        N×N DataFrame of pairwise Pearson correlations. NaN for pairs with
        insufficient overlap. Diagonal is 1.0.
    """
    if not returns_by_strategy:
        return pd.DataFrame()
    # Truncate each series to lookback most recent observations
    truncated = {
        name: ser.dropna().tail(lookback)
        for name, ser in returns_by_strategy.items()
    }
    # Stack into DataFrame aligning on index
    df = pd.DataFrame(truncated)
    if df.empty or df.shape[1] < 2:
        # Edge case: only 1 strategy → 1×1 self-correlation = 1.0
        if df.shape[1] == 1:
            return pd.DataFrame(
                [[1.0]],
                index=df.columns, columns=df.columns,
            )
        return pd.DataFrame()
    return df.corr(method="pearson", min_periods=max(20, lookback // 4))


# ---------------------------------------------------------------------------
# DEC-509 — Cluster strategies by correlation
# ---------------------------------------------------------------------------
def cluster_strategies(
    corr_df: pd.DataFrame,
    threshold: float = 0.7,
) -> List[List[str]]:
    """Single-link clustering: any pair with corr > threshold joins same cluster.

    Args:
        corr_df: N×N correlation DataFrame (output of
            compute_correlation_matrix).
        threshold: correlation threshold for clustering (default 0.7 per spec).

    Returns:
        List of clusters; each cluster is a list of strategy names. Singletons
        appear as 1-element lists.
    """
    if corr_df is None or corr_df.empty:
        return []
    n = corr_df.shape[0]
    strategies = list(corr_df.columns)
    # Union-find for clustering
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[ry] = rx

    for i in range(n):
        for j in range(i + 1, n):
            val = corr_df.iat[i, j]
            if pd.notna(val) and val > threshold:
                union(i, j)

    # Group by root
    groups: Dict[int, List[str]] = {}
    for i, s in enumerate(strategies):
        r = find(i)
        groups.setdefault(r, []).append(s)
    return list(groups.values())


# ---------------------------------------------------------------------------
# DEC-509 — Flag redundant variants
# ---------------------------------------------------------------------------
def flag_redundant_variants(
    returns_by_strategy: Dict[str, pd.Series],
    sharpes: Optional[Dict[str, float]] = None,
    threshold: float = 0.7,
    min_cluster_size: int = 3,
) -> pd.DataFrame:
    """Apply DEC-509 cluster-gate logic to a set of strategies.

    For each cluster with >= min_cluster_size members, retain the
    highest-Sharpe member as ``primary`` and flag the rest as
    ``redundant_variant``. Smaller clusters keep all members as primary.

    Args:
        returns_by_strategy: strategy_name -> daily returns Series.
        sharpes: optional pre-computed per-strategy Sharpe ratios. If None,
            computes annualized Sharpe per strategy in the lookback window.
        threshold: correlation threshold (default 0.7).
        min_cluster_size: clusters smaller than this keep all members
            (default 3 per spec).

    Returns:
        DataFrame with columns:
          strategy, correlation_cluster_id (int), cluster_size,
          is_primary (bool), is_redundant_variant (bool), sharpe (float)
    """
    if not returns_by_strategy:
        return pd.DataFrame(columns=[
            "strategy", "correlation_cluster_id", "cluster_size",
            "is_primary", "is_redundant_variant", "sharpe",
        ])

    # Compute Sharpes if not provided
    if sharpes is None:
        sharpes = {}
        for name, ser in returns_by_strategy.items():
            r = ser.dropna()
            if len(r) < 20:
                sharpes[name] = float("nan")
                continue
            mean = r.mean()
            std = r.std()
            sharpes[name] = float(mean / std * np.sqrt(252)) if std > 0 else 0.0

    # Compute correlation matrix
    corr = compute_correlation_matrix(returns_by_strategy)
    if corr.empty:
        return pd.DataFrame([
            {"strategy": name, "correlation_cluster_id": i, "cluster_size": 1,
             "is_primary": True, "is_redundant_variant": False,
             "sharpe": sharpes.get(name, float("nan"))}
            for i, name in enumerate(returns_by_strategy.keys())
        ])

    # Cluster
    clusters = cluster_strategies(corr, threshold=threshold)

    rows = []
    for cluster_id, members in enumerate(clusters):
        size = len(members)
        if size < min_cluster_size:
            # Singleton or small cluster → all members are primary
            for s in members:
                rows.append({
                    "strategy": s,
                    "correlation_cluster_id": cluster_id,
                    "cluster_size": size,
                    "is_primary": True,
                    "is_redundant_variant": False,
                    "sharpe": sharpes.get(s, float("nan")),
                })
        else:
            # Multi-member cluster: pick highest-Sharpe as primary
            sorted_members = sorted(
                members,
                key=lambda s: sharpes.get(s, float("-inf")),
                reverse=True,
            )
            primary = sorted_members[0]
            for s in sorted_members:
                rows.append({
                    "strategy": s,
                    "correlation_cluster_id": cluster_id,
                    "cluster_size": size,
                    "is_primary": s == primary,
                    "is_redundant_variant": s != primary,
                    "sharpe": sharpes.get(s, float("nan")),
                })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Convenience: build per-strategy returns from a trade_log DataFrame
# ---------------------------------------------------------------------------
def build_returns_from_trade_log(
    df_trades: pd.DataFrame,
    pnl_col: str = "pnl_pct",
    strategy_col: str = "strategy",
    date_col: str = "exit_date",
) -> Dict[str, pd.Series]:
    """Convert a trade_log DataFrame into per-strategy daily-return Series.

    Aggregates per-strategy by exit_date (sum of pnl_pct on each exit day).
    Used as input to compute_correlation_matrix / flag_redundant_variants.
    """
    if df_trades is None or df_trades.empty:
        return {}
    df = df_trades.copy()
    if date_col not in df.columns:
        return {}
    df[date_col] = pd.to_datetime(df[date_col])
    out: Dict[str, pd.Series] = {}
    for strat, group in df.groupby(strategy_col):
        ser = group.groupby(date_col)[pnl_col].sum()
        out[str(strat)] = ser.sort_index()
    return out
