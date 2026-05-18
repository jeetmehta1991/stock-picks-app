"""HRP correlation-adjusted sizing + per-strategy half-Kelly fraction.

Batch 212 (2026-05-17 owner-approved research review). Implements two
risk-management additions from the Top-5 research recommendations:

1. Hierarchical Risk Parity (Lopez de Prado 2016, *Journal of Portfolio
   Management* 42(4)). Documented +31.3% out-of-sample Sharpe vs
   classical CLA on 1,292-stock US equity backtest. Clusters strategies
   by correlation, then allocates inversely with cluster variance via
   recursive bisection. Replaces flat tier sizing with correlation-aware
   weighting so highly-correlated strategies share a sizing budget
   rather than compounding exposure.

2. Half-Kelly per-strategy (MacLean, Ziemba, Blazenko 1992 *Mathematical
   Finance*). Half-Kelly = 75% of full-Kelly growth at 50% of volatility.
   Kelly fraction f* = (b*p - q) / b where p = win rate, q = 1-p,
   b = avg_win / avg_loss. Half-Kelly applies f* / 2 with clamping to
   prevent extreme positions.

Both functions compose multiplicatively with the existing tier sizing
stack (TIER_POSITION_SIZE_PCT * DD-band * portfolio_vol_target *
per_position_vol_target * VIX_pct from Batch 203). HRP weight scales
within a cluster; Kelly scales within a strategy.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def half_kelly_fraction(
    win_rate: Optional[float],
    avg_win: Optional[float],
    avg_loss: Optional[float],
    min_trades: int = 30,
    n_trades: Optional[int] = None,
    min_mult: float = 0.25,
    max_mult: float = 1.0,
) -> float:
    """Compute half-Kelly sizing multiplier from rolling strategy stats.

    Kelly fraction f* = (b*p - q) / b
      p = win rate (probability of win)
      q = 1 - p
      b = avg_win / abs(avg_loss) (W:L ratio)

    Half-Kelly = f* / 2 (MacLean-Ziemba-Blazenko 1992: 75% of full-Kelly
    growth at 50% of volatility - the canonical practical Kelly fraction).

    Returns multiplier in [min_mult, max_mult]. Returns max_mult=1.0
    (no-op) when:
      - insufficient sample (n_trades < min_trades)
      - inputs missing / non-numeric
      - avg_loss is zero or NaN

    This is INTENTIONALLY no-op-on-insufficient-data so the strategy
    can build a rolling sample before Kelly takes over - rather than
    defaulting to min_mult (which would discriminate against new
    strategies). Owner-facing dashboards can show the per-strategy
    Kelly evolution.

    Args:
      win_rate:   p in Kelly formula, 0..1
      avg_win:    average winning trade PnL (decimal or %; sign-agnostic
                  as long as avg_loss uses same units)
      avg_loss:   average losing trade PnL (negative value or absolute)
      min_trades: minimum sample size before Kelly applies (default 30)
      n_trades:   rolling sample size; None = treat as sufficient
      min_mult:   floor on Kelly multiplier (prevents 0-sizing on edge cases)
      max_mult:   ceiling on Kelly multiplier (prevents Kelly leverage)
    """
    if (
        win_rate is None
        or avg_win is None
        or avg_loss is None
    ):
        return max_mult
    if n_trades is not None and n_trades < min_trades:
        return max_mult
    if avg_loss == 0 or np.isnan(avg_loss):
        return max_mult
    p = float(win_rate)
    q = 1.0 - p
    b = float(avg_win) / abs(float(avg_loss))
    if b <= 0:
        return max_mult
    kelly = (b * p - q) / b
    half_kelly = kelly / 2.0
    return float(max(min_mult, min(max_mult, round(half_kelly, 4))))


def per_strategy_kelly_from_trade_log(
    trade_log: pd.DataFrame,
    strategy: str,
    lookback_days: int = 252,
    as_of: Optional[pd.Timestamp] = None,
    pnl_col: str = "pnl_pct",
    win_col: str = "win",
    entry_col: str = "entry_date",
) -> float:
    """Compute half-Kelly multiplier for a strategy from rolling trade log.

    Used at trade-open time (or batched ahead of a day's screen) to
    derive a strategy-specific sizing multiplier from its trailing
    lookback_days window.

    Returns 1.0 (no-op) when trade_log empty / strategy absent / sample
    too small (handled by half_kelly_fraction's min_trades gate).
    """
    if trade_log is None or trade_log.empty or strategy not in trade_log.get("strategy", pd.Series()).values:
        return 1.0
    df = trade_log[trade_log["strategy"] == strategy].copy()
    if as_of is not None and entry_col in df.columns:
        df = df[pd.to_datetime(df[entry_col]) <= as_of]
        # Limit to lookback window
        window_start = pd.to_datetime(as_of) - pd.Timedelta(days=lookback_days)
        df = df[pd.to_datetime(df[entry_col]) >= window_start]
    n = len(df)
    if n < 30:
        return 1.0
    if win_col not in df.columns or pnl_col not in df.columns:
        return 1.0
    win_rate = float(df[win_col].mean())
    winners = df[df[win_col] == True][pnl_col]
    losers = df[df[win_col] == False][pnl_col]
    avg_win = float(winners.mean()) if len(winners) > 0 else None
    avg_loss = float(losers.mean()) if len(losers) > 0 else None
    if avg_win is None or avg_loss is None:
        return 1.0
    return half_kelly_fraction(win_rate, avg_win, avg_loss, n_trades=n)


def _correlation_distance(corr: pd.DataFrame) -> pd.DataFrame:
    """Convert correlation matrix to distance matrix used by HRP.

    Lopez de Prado distance: d_ij = sqrt(0.5 * (1 - corr_ij)). Perfectly
    correlated -> distance 0; perfectly anti-correlated -> 1.
    """
    return ((1 - corr) / 2.0).pow(0.5)


def _inverse_variance_weights(cov: pd.DataFrame) -> pd.Series:
    """Inverse-variance weights within a cluster. Cluster equivalent of
    Markowitz minimum-variance for the cluster's covariance submatrix.
    """
    ivp = 1.0 / np.diag(cov.values)
    ivp = ivp / ivp.sum()
    return pd.Series(ivp, index=cov.columns)


def per_strategy_hrp_weight_from_trade_log(
    trade_log: pd.DataFrame,
    strategy: str,
    as_of: Optional[pd.Timestamp] = None,
    lookback_days: int = 252,
    entry_col: str = "entry_date",
    pnl_col: str = "pnl_pct",
    strategy_col: str = "strategy",
    min_strategies: int = 3,
    min_obs: int = 30,
    min_mult: float = 0.25,
    max_mult: float = 2.0,
) -> float:
    """Compute the per-strategy HRP-relative sizing multiplier.

    Batch 219 (HRP wiring 2026-05-18 owner-approved). Builds the
    per-strategy daily returns matrix from a closed-trades log, runs
    hrp_cluster_weights, and returns a tilt multiplier relative to the
    equal-weight baseline (1/N).

    Returned multiplier semantics:
      - hrp_weight = HRP's allocation to this strategy (sum-to-1.0)
      - relative   = hrp_weight * N_strategies (compared to equal-weight)
      - multiplier = clamp(relative, [min_mult, max_mult])

    A multiplier of 1.0 means HRP gives this strategy exactly its
    equal-weight share. >1.0 = HRP wants more; <1.0 = HRP wants less.
    Bounded [0.25, 2.0] to prevent over-tilt on noisy short samples.

    Returns 1.0 (no-op) when:
      - trade log empty or strategy absent
      - fewer than min_strategies distinct strategies (HRP undefined)
      - fewer than min_obs return observations
      - HRP computation fails (defensive fallback)
    """
    if trade_log is None or trade_log.empty:
        return 1.0
    if strategy_col not in trade_log.columns or strategy not in trade_log[strategy_col].values:
        return 1.0
    df = trade_log.copy()
    if as_of is not None and entry_col in df.columns:
        df = df[pd.to_datetime(df[entry_col]) <= as_of]
        window_start = pd.to_datetime(as_of) - pd.Timedelta(days=lookback_days)
        df = df[pd.to_datetime(df[entry_col]) >= window_start]
    if df.empty:
        return 1.0
    if entry_col not in df.columns or pnl_col not in df.columns:
        return 1.0
    # Aggregate per-strategy daily returns
    df["__d__"] = pd.to_datetime(df[entry_col]).dt.normalize()
    grouped = (
        df.groupby(["__d__", strategy_col])[pnl_col]
        .sum()
        .unstack(fill_value=0.0)
    )
    if grouped.empty:
        return 1.0
    n_strategies = grouped.shape[1]
    if n_strategies < min_strategies:
        return 1.0
    if len(grouped) < min_obs:
        return 1.0
    if strategy not in grouped.columns:
        return 1.0
    try:
        weights = hrp_cluster_weights(grouped, min_obs=min_obs)
    except Exception:
        return 1.0
    if weights is None or weights.empty or strategy not in weights.index:
        return 1.0
    hrp_w = float(weights[strategy])
    if hrp_w <= 0:
        return 1.0
    equal_w = 1.0 / n_strategies
    if equal_w <= 0:
        return 1.0
    relative = hrp_w / equal_w
    return float(max(min_mult, min(max_mult, round(relative, 4))))


def hrp_cluster_weights(
    returns_df: pd.DataFrame,
    min_obs: int = 30,
) -> pd.Series:
    """Compute HRP weights for a returns matrix.

    Lopez de Prado 2016 algorithm:
      1. Compute correlation matrix
      2. Compute distance matrix (sqrt((1-corr)/2))
      3. Single-linkage hierarchical clustering
      4. Quasi-diagonalize (reorder so similar series are adjacent)
      5. Recursive bisection: split clusters in half, allocate inversely
         to cluster variance
      6. Return final per-asset weights

    Returns equal-weight Series when:
      - returns_df has fewer than min_obs rows
      - returns_df is empty or single-column
      - any computation fails (defensive fallback to equal-weight)

    Args:
      returns_df: DataFrame indexed by date, columns = asset/strategy
                  names, values = period returns
      min_obs:    minimum number of return observations before HRP
                  applies (else equal-weight fallback)
    """
    if returns_df is None or returns_df.empty:
        return pd.Series(dtype=float)
    cols = list(returns_df.columns)
    n = len(cols)
    if n == 0:
        return pd.Series(dtype=float)
    eq = pd.Series([1.0 / n] * n, index=cols)
    if n == 1:
        return eq
    if len(returns_df) < min_obs:
        return eq
    try:
        from scipy.cluster.hierarchy import linkage
        from scipy.spatial.distance import squareform
        corr = returns_df.corr()
        # Replace NaN correlations with 0 (uncorrelated default)
        corr = corr.fillna(0.0)
        # Symmetrize numerically just in case
        corr = (corr + corr.T) / 2.0
        # Ensure diagonal exactly 1.0
        np.fill_diagonal(corr.values, 1.0)
        dist = _correlation_distance(corr)
        # Convert to condensed distance form for scipy.linkage
        try:
            condensed = squareform(dist.values, checks=False)
        except Exception:
            return eq
        link = linkage(condensed, method="single")
        # Quasi-diagonalization via linkage matrix
        def _get_quasi_diag(lnk):
            lnk = lnk.astype(int)
            sort_ix = pd.Series([lnk[-1, 0], lnk[-1, 1]])
            num_items = lnk[-1, 3]
            while sort_ix.max() >= num_items:
                sort_ix.index = range(0, sort_ix.shape[0] * 2, 2)
                df0 = sort_ix[sort_ix >= num_items]
                i = df0.index
                j = df0.values - num_items
                sort_ix[i] = lnk[j, 0]
                df0 = pd.Series(lnk[j, 1], index=i + 1)
                sort_ix = pd.concat([sort_ix, df0])
                sort_ix = sort_ix.sort_index()
                sort_ix.index = range(sort_ix.shape[0])
            return sort_ix.tolist()
        sort_ix_pos = _get_quasi_diag(link)
        ordered_cols = [cols[i] for i in sort_ix_pos]
        cov = returns_df.cov()
        # Recursive bisection
        weights = pd.Series([1.0] * n, index=ordered_cols)
        clusters = [ordered_cols]
        while clusters:
            new_clusters = []
            for cluster in clusters:
                if len(cluster) <= 1:
                    continue
                mid = len(cluster) // 2
                left = cluster[:mid]
                right = cluster[mid:]
                # Variance of each sub-cluster via inverse-variance weights
                def cluster_var(sub):
                    sub_cov = cov.loc[sub, sub]
                    w = _inverse_variance_weights(sub_cov)
                    return float(np.dot(np.dot(w.values, sub_cov.values), w.values))
                var_left = cluster_var(left)
                var_right = cluster_var(right)
                if var_left + var_right == 0:
                    alpha = 0.5
                else:
                    alpha = 1.0 - var_left / (var_left + var_right)
                for t in left:
                    weights[t] *= alpha
                for t in right:
                    weights[t] *= 1.0 - alpha
                new_clusters.extend([left, right])
            clusters = new_clusters
        # Normalize
        weights = weights / weights.sum()
        return weights.reindex(cols).fillna(1.0 / n)
    except Exception:
        return eq
