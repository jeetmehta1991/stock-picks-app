"""DEC-509 strategy correlation cluster gate + DEC-513 #4 correlation matrix
regression tests (Pass 53 Day-9 v8g).

Spec source: TRADING_RULES_AND_INFORMATION.md §2A.10 + AUDIT.md §"Pass 53 Q2".

Pre-Phase-1B-α gate: pairwise return correlation; cluster at ρ > 0.7;
clusters ≥ 3 members retain highest-Sharpe representative; flag rest as
redundant_variant.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _build_returns(seed=0):
    """Build 5 synthetic strategies: A/B/D highly correlated, C/E independent."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-02", periods=252, freq="B")
    ret_A = pd.Series(rng.normal(0.001, 0.01, 252), index=idx)
    ret_B = ret_A + rng.normal(0, 0.002, 252)  # ~0.98 corr to A
    ret_C = pd.Series(rng.normal(0.001, 0.01, 252), index=idx)
    ret_D = ret_A * 0.9 + rng.normal(0, 0.001, 252)  # ~0.99 corr
    ret_E = pd.Series(rng.normal(0.0005, 0.012, 252), index=idx)
    return {"A": ret_A, "B": ret_B, "C": ret_C, "D": ret_D, "E": ret_E}


# ---------------------------------------------------------------------------
# DEC-513 #4 — correlation matrix
# ---------------------------------------------------------------------------
def test_dec513_4_corr_matrix_returns_dataframe():
    from backtest.engine.correlation_cluster import compute_correlation_matrix
    returns = _build_returns()
    corr = compute_correlation_matrix(returns)
    assert isinstance(corr, pd.DataFrame)
    assert corr.shape == (5, 5)
    # Diagonal = 1.0
    for i in range(5):
        assert corr.iat[i, i] == pytest.approx(1.0, abs=1e-6)


def test_dec513_4_corr_matrix_high_corr_pair():
    from backtest.engine.correlation_cluster import compute_correlation_matrix
    returns = _build_returns()
    corr = compute_correlation_matrix(returns)
    # A and B are correlated by construction
    assert corr.loc["A", "B"] > 0.9
    assert corr.loc["A", "D"] > 0.9


def test_dec513_4_corr_matrix_independent_pair_low():
    from backtest.engine.correlation_cluster import compute_correlation_matrix
    returns = _build_returns()
    corr = compute_correlation_matrix(returns)
    # C and E are independent of A
    assert abs(corr.loc["A", "C"]) < 0.5
    assert abs(corr.loc["A", "E"]) < 0.5


def test_dec513_4_corr_matrix_empty_input_returns_empty():
    from backtest.engine.correlation_cluster import compute_correlation_matrix
    out = compute_correlation_matrix({})
    assert out.empty


def test_dec513_4_corr_matrix_single_strategy_self_corr():
    from backtest.engine.correlation_cluster import compute_correlation_matrix
    idx = pd.date_range("2023-01-02", periods=100, freq="B")
    one = {"A": pd.Series(np.random.randn(100), index=idx)}
    out = compute_correlation_matrix(one)
    assert out.shape == (1, 1)
    assert out.iat[0, 0] == 1.0


# ---------------------------------------------------------------------------
# DEC-509 — cluster_strategies
# ---------------------------------------------------------------------------
def test_dec509_clusters_high_corr_into_one():
    from backtest.engine.correlation_cluster import (
        compute_correlation_matrix, cluster_strategies,
    )
    returns = _build_returns()
    corr = compute_correlation_matrix(returns)
    clusters = cluster_strategies(corr, threshold=0.7)
    # A/B/D should cluster together; C and E should be singletons
    cluster_set = [set(c) for c in clusters]
    assert {"A", "B", "D"} in cluster_set
    assert {"C"} in cluster_set or {"E"} in cluster_set


def test_dec509_threshold_zero_clusters_everything():
    from backtest.engine.correlation_cluster import cluster_strategies
    # Build a 3x3 corr matrix with all values 0.5
    df = pd.DataFrame(
        [[1.0, 0.5, 0.5], [0.5, 1.0, 0.5], [0.5, 0.5, 1.0]],
        index=list("ABC"), columns=list("ABC"),
    )
    clusters = cluster_strategies(df, threshold=0.0)
    # threshold 0 with positive correlations → all in one cluster
    assert len(clusters) == 1
    assert set(clusters[0]) == {"A", "B", "C"}


def test_dec509_threshold_one_no_clusters():
    from backtest.engine.correlation_cluster import cluster_strategies
    df = pd.DataFrame(
        [[1.0, 0.99, 0.99], [0.99, 1.0, 0.99], [0.99, 0.99, 1.0]],
        index=list("ABC"), columns=list("ABC"),
    )
    clusters = cluster_strategies(df, threshold=1.0)
    # threshold > all off-diagonal → 3 singletons
    assert len(clusters) == 3


def test_dec509_empty_corr_returns_empty():
    from backtest.engine.correlation_cluster import cluster_strategies
    assert cluster_strategies(pd.DataFrame()) == []


# ---------------------------------------------------------------------------
# DEC-509 — flag_redundant_variants
# ---------------------------------------------------------------------------
def test_dec509_flag_redundant_variants_basic():
    from backtest.engine.correlation_cluster import flag_redundant_variants
    returns = _build_returns()
    df = flag_redundant_variants(returns, threshold=0.7, min_cluster_size=3)
    assert {"strategy", "correlation_cluster_id", "is_primary",
             "is_redundant_variant", "sharpe"}.issubset(df.columns)
    # Cluster A/B/D has 3 members → 1 primary + 2 redundant
    cluster_abd = df[df["strategy"].isin(["A", "B", "D"])]
    assert cluster_abd["is_primary"].sum() == 1
    assert cluster_abd["is_redundant_variant"].sum() == 2


def test_dec509_primary_is_highest_sharpe():
    from backtest.engine.correlation_cluster import flag_redundant_variants
    returns = _build_returns()
    df = flag_redundant_variants(returns, threshold=0.7, min_cluster_size=3)
    cluster_abd = df[df["strategy"].isin(["A", "B", "D"])]
    primary_row = cluster_abd[cluster_abd["is_primary"]].iloc[0]
    redundants = cluster_abd[cluster_abd["is_redundant_variant"]]
    # Primary has highest Sharpe in cluster
    for _, r in redundants.iterrows():
        assert primary_row["sharpe"] >= r["sharpe"]


def test_dec509_singletons_marked_primary():
    from backtest.engine.correlation_cluster import flag_redundant_variants
    returns = _build_returns()
    df = flag_redundant_variants(returns, threshold=0.7, min_cluster_size=3)
    # C and E should be primary singletons (cluster_size=1)
    for s in ["C", "E"]:
        row = df[df["strategy"] == s].iloc[0]
        assert row["is_primary"] is True or row["is_primary"] == True
        assert row["is_redundant_variant"] is False or row["is_redundant_variant"] == False
        assert row["cluster_size"] == 1


def test_dec509_min_cluster_size_2_flags_pair():
    """With min_cluster_size=2, even pairs flag redundant variants."""
    from backtest.engine.correlation_cluster import flag_redundant_variants
    rng = np.random.default_rng(0)
    idx = pd.date_range("2023-01-02", periods=200, freq="B")
    a = pd.Series(rng.normal(0.001, 0.01, 200), index=idx)
    b = a + rng.normal(0, 0.001, 200)  # very high corr
    returns = {"A": a, "B": b}
    df = flag_redundant_variants(returns, threshold=0.7, min_cluster_size=2)
    assert df["is_redundant_variant"].sum() == 1


def test_dec509_explicit_sharpes_override():
    """If `sharpes` arg is provided, it controls primary selection."""
    from backtest.engine.correlation_cluster import flag_redundant_variants
    returns = _build_returns()
    # Pretend D has the highest Sharpe
    sharpes = {"A": 0.5, "B": 0.5, "C": 1.0, "D": 99.0, "E": 0.5}
    df = flag_redundant_variants(returns, sharpes=sharpes, threshold=0.7,
                                   min_cluster_size=3)
    cluster_abd = df[df["strategy"].isin(["A", "B", "D"])]
    primary = cluster_abd[cluster_abd["is_primary"]].iloc[0]
    assert primary["strategy"] == "D"


# ---------------------------------------------------------------------------
# Convenience: build_returns_from_trade_log
# ---------------------------------------------------------------------------
def test_build_returns_from_trade_log():
    from backtest.engine.correlation_cluster import build_returns_from_trade_log
    df = pd.DataFrame({
        "strategy":  ["A", "A", "B", "B", "A"],
        "exit_date": ["2023-01-03", "2023-01-04", "2023-01-03",
                       "2023-01-05", "2023-01-04"],
        "pnl_pct":   [1.0, 2.0, -1.0, 3.0, 0.5],
    })
    out = build_returns_from_trade_log(df)
    assert "A" in out and "B" in out
    # A had 2 trades on 2023-01-04 (2.0 + 0.5 = 2.5)
    assert out["A"].loc[pd.Timestamp("2023-01-04")] == 2.5
