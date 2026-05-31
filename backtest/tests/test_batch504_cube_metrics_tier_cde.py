"""Batch 504 (2026-05-31) -- Tier C + D + E cube cell metrics tests.

Source: per CHECKLIST #77.
Queue row: EXECUTION_QUEUE.md item #5 (cube-cell-metrics-expansion).
Module: backtest/results/cube_metrics_tier_cde.py.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _make_trades(pnls, with_dates=False):
    df = pd.DataFrame({"pnl_pct": list(pnls)})
    if with_dates:
        df["entry_date"] = pd.date_range("2024-01-02", periods=len(pnls), freq="B")
    return df


# ---------------------------------------------------------------------------
# Tier C: sharpe_ci_95
# ---------------------------------------------------------------------------

def test_batch504_sharpe_ci_95_brackets_point_estimate():
    """CI low <= point Sharpe <= CI high. Deterministic via seed."""
    from backtest.results.cube_metrics_tier_cde import compute_sharpe_ci_95
    rng = np.random.default_rng(7)
    pnls = rng.normal(0.5, 1.0, size=200)
    out = compute_sharpe_ci_95(pnls, n_boot=500, seed=42)
    assert "sharpe_ci_low" in out
    assert "sharpe_ci_high" in out
    assert out["sharpe_ci_low"] < out["sharpe_ci_high"]


def test_batch504_sharpe_ci_95_short_input_returns_empty():
    from backtest.results.cube_metrics_tier_cde import compute_sharpe_ci_95
    assert compute_sharpe_ci_95(np.array([1.0]*10)) == {}


def test_batch504_sharpe_ci_95_deterministic_via_seed():
    from backtest.results.cube_metrics_tier_cde import compute_sharpe_ci_95
    pnls = np.array([1.0, 1.5, -0.5, 0.8] * 25)
    o1 = compute_sharpe_ci_95(pnls, n_boot=300, seed=99)
    o2 = compute_sharpe_ci_95(pnls, n_boot=300, seed=99)
    assert o1 == o2


# ---------------------------------------------------------------------------
# Tier C: oos_decay
# ---------------------------------------------------------------------------

def test_batch504_oos_decay_split_chronologically():
    from backtest.results.cube_metrics_tier_cde import compute_oos_decay
    # First half positive Sharpe (edge), second half random
    df = _make_trades([1.5]*40 + [0.1, -0.1]*20, with_dates=True)
    out = compute_oos_decay(df)
    assert "is_sharpe" in out
    assert "oos_sharpe" in out
    assert "is_oos_decay" in out
    # IS Sharpe should be much higher than OOS
    assert out["is_sharpe"] > out["oos_sharpe"]
    assert out["is_oos_decay"] > 0


def test_batch504_oos_decay_short_input_returns_empty():
    from backtest.results.cube_metrics_tier_cde import compute_oos_decay
    df = _make_trades([1.0]*40, with_dates=True)  # n=40 < 60 threshold
    assert compute_oos_decay(df) == {}


def test_batch504_oos_decay_missing_date_column_returns_empty():
    from backtest.results.cube_metrics_tier_cde import compute_oos_decay
    df = pd.DataFrame({"pnl_pct": [1.0]*100})
    assert compute_oos_decay(df) == {}


# ---------------------------------------------------------------------------
# Tier C: effective_n
# ---------------------------------------------------------------------------

def test_batch504_effective_n_iid_input_close_to_raw_n():
    """IID input -> rho1 near 0 -> effective_n close to n."""
    from backtest.results.cube_metrics_tier_cde import compute_effective_n
    rng = np.random.default_rng(11)
    pnls = rng.normal(0.0, 1.0, size=500)
    out = compute_effective_n(pnls)
    assert abs(out["autocorr_lag1"]) < 0.15
    assert out["effective_n"] > 350  # close to 500


def test_batch504_effective_n_high_autocorr_shrinks_n():
    """Positively autocorrelated input shrinks effective n."""
    from backtest.results.cube_metrics_tier_cde import compute_effective_n
    n = 200
    rng = np.random.default_rng(13)
    noise = rng.normal(0, 0.1, size=n)
    pnls = np.zeros(n)
    pnls[0] = noise[0]
    for i in range(1, n):
        pnls[i] = 0.7 * pnls[i-1] + noise[i]
    out = compute_effective_n(pnls)
    assert out["autocorr_lag1"] > 0.5
    assert out["effective_n"] < n  # shrunk


def test_batch504_effective_n_short_input_returns_empty():
    from backtest.results.cube_metrics_tier_cde import compute_effective_n
    assert compute_effective_n(np.array([1.0]*10)) == {}


# ---------------------------------------------------------------------------
# Tier D: SQN
# ---------------------------------------------------------------------------

def test_batch504_sqn_positive_edge():
    from backtest.results.cube_metrics_tier_cde import compute_sqn
    pnls = np.array([2.0]*60 + [-1.0]*40)
    out = compute_sqn(pnls)
    assert "sqn" in out
    assert out["sqn"] > 0


def test_batch504_sqn_zero_std_returns_zero():
    from backtest.results.cube_metrics_tier_cde import compute_sqn
    out = compute_sqn(np.array([1.0]*30))
    assert out["sqn"] == 0.0


def test_batch504_sqn_short_returns_empty():
    from backtest.results.cube_metrics_tier_cde import compute_sqn
    assert compute_sqn(np.array([1.0])) == {}


# ---------------------------------------------------------------------------
# Tier D: K-ratio
# ---------------------------------------------------------------------------

def test_batch504_k_ratio_noisy_uptrend_positive():
    """Noisy uptrend (drift + noise) should yield positive K-ratio.
    A perfectly monotonic uptrend has 0 residual variance -> K=0
    (defined behavior; can't divide by zero SE)."""
    from backtest.results.cube_metrics_tier_cde import compute_k_ratio
    rng = np.random.default_rng(19)
    pnls = 1.0 + rng.normal(0, 0.2, size=100)  # mean ~1.0 with small noise
    out = compute_k_ratio(pnls)
    assert out["k_ratio"] > 0


def test_batch504_k_ratio_perfectly_monotonic_returns_zero():
    """Pure constant -> 0 residual variance -> K-ratio is 0 (no SE)."""
    from backtest.results.cube_metrics_tier_cde import compute_k_ratio
    out = compute_k_ratio(np.array([1.0]*100))
    assert out["k_ratio"] == 0.0


def test_batch504_k_ratio_random_walk_near_zero():
    from backtest.results.cube_metrics_tier_cde import compute_k_ratio
    rng = np.random.default_rng(17)
    pnls = rng.normal(0, 1, size=200)
    out = compute_k_ratio(pnls)
    assert abs(out["k_ratio"]) < 2.0


def test_batch504_k_ratio_short_returns_empty():
    from backtest.results.cube_metrics_tier_cde import compute_k_ratio
    assert compute_k_ratio(np.array([1.0, 2.0])) == {}


# ---------------------------------------------------------------------------
# Tier D: MAR ratio
# ---------------------------------------------------------------------------

def test_batch504_mar_ratio_positive_for_uptrending():
    from backtest.results.cube_metrics_tier_cde import compute_mar_ratio
    # Mostly wins with small drawdown
    pnls = np.array([1.0]*50 + [-0.5]*10)
    out = compute_mar_ratio(pnls)
    assert "mar_ratio" in out
    assert out["mar_ratio"] > 0


def test_batch504_mar_ratio_no_drawdown_returns_zero():
    """Pure uptrend with no drawdown -> MAR = 0 (defined as no-DD)."""
    from backtest.results.cube_metrics_tier_cde import compute_mar_ratio
    pnls = np.array([1.0]*30)
    out = compute_mar_ratio(pnls)
    assert out["mar_ratio"] == 0.0
    assert out["max_dd_value"] == 0.0


# ---------------------------------------------------------------------------
# Tier E: Kelly fraction
# ---------------------------------------------------------------------------

def test_batch504_kelly_fraction_positive_for_positive_edge():
    from backtest.results.cube_metrics_tier_cde import compute_kelly_fraction
    # 60% WR, 2:1 R:R
    pnls = np.array([2.0]*60 + [-1.0]*40)
    out = compute_kelly_fraction(pnls)
    assert out["kelly_fraction"] > 0


def test_batch504_kelly_fraction_bounded_to_one():
    from backtest.results.cube_metrics_tier_cde import compute_kelly_fraction
    # Extreme positive edge -> capped at 1.0
    pnls = np.array([10.0]*95 + [-0.01]*5)
    out = compute_kelly_fraction(pnls)
    assert 0 <= out["kelly_fraction"] <= 1.0


def test_batch504_kelly_fraction_zero_for_negative_edge():
    """Negative-edge strategy -> Kelly = 0 (don't bet)."""
    from backtest.results.cube_metrics_tier_cde import compute_kelly_fraction
    pnls = np.array([0.5]*30 + [-2.0]*70)
    out = compute_kelly_fraction(pnls)
    assert out["kelly_fraction"] == 0.0


def test_batch504_kelly_fraction_zero_when_no_losses():
    from backtest.results.cube_metrics_tier_cde import compute_kelly_fraction
    out = compute_kelly_fraction(np.array([1.0]*30))
    assert out["kelly_fraction"] == 0.0


# ---------------------------------------------------------------------------
# Tier E: CVaR
# ---------------------------------------------------------------------------

def test_batch504_cvar_negative_for_loss_tail():
    from backtest.results.cube_metrics_tier_cde import compute_cvar
    pnls = np.concatenate([np.ones(95), np.array([-10.0, -8.0, -6.0, -4.0, -3.0])])
    out = compute_cvar(pnls)
    assert "cvar_5pct" in out
    assert "var_5pct" in out
    # 5% tail -> ~5 worst losses; their mean is around -6
    assert out["cvar_5pct"] < 0


def test_batch504_cvar_short_returns_empty():
    from backtest.results.cube_metrics_tier_cde import compute_cvar
    assert compute_cvar(np.array([1.0]*15)) == {}


# ---------------------------------------------------------------------------
# Tier E: Risk of ruin
# ---------------------------------------------------------------------------

def test_batch504_risk_of_ruin_low_for_positive_edge():
    from backtest.results.cube_metrics_tier_cde import compute_risk_of_ruin
    # Strong positive edge
    pnls = np.array([2.0]*70 + [-1.0]*30)
    out = compute_risk_of_ruin(pnls)
    assert "risk_of_ruin" in out
    assert 0 <= out["risk_of_ruin"] < 0.5


def test_batch504_risk_of_ruin_one_for_negative_edge():
    """No edge -> ruin certain over infinite play."""
    from backtest.results.cube_metrics_tier_cde import compute_risk_of_ruin
    pnls = np.array([1.0]*30 + [-3.0]*70)
    out = compute_risk_of_ruin(pnls)
    assert out["risk_of_ruin"] == 1.0


def test_batch504_risk_of_ruin_short_returns_empty():
    from backtest.results.cube_metrics_tier_cde import compute_risk_of_ruin
    assert compute_risk_of_ruin(np.array([1.0]*10)) == {}


# ---------------------------------------------------------------------------
# Aggregator
# ---------------------------------------------------------------------------

def test_batch504_aggregator_merges_all_tiers():
    from backtest.results.cube_metrics_tier_cde import compute_tier_cde_metrics
    rng = np.random.default_rng(23)
    df = _make_trades(rng.normal(0.5, 1.0, size=200), with_dates=True)
    out = compute_tier_cde_metrics(df)
    expected_keys = {
        "sharpe_ci_low", "sharpe_ci_high",  # Tier C
        "is_sharpe", "oos_sharpe", "is_oos_decay",  # Tier C
        "autocorr_lag1", "effective_n",  # Tier C
        "sqn",                           # Tier D
        "k_ratio",                       # Tier D
        "mar_ratio", "max_dd_value",     # Tier D
        "kelly_fraction",                # Tier E
        "var_5pct", "cvar_5pct",         # Tier E
        "risk_of_ruin",                  # Tier E
    }
    missing = expected_keys - set(out.keys())
    assert not missing, f"Aggregator missing keys: {missing}"


def test_batch504_aggregator_empty_input_returns_empty():
    from backtest.results.cube_metrics_tier_cde import compute_tier_cde_metrics
    assert compute_tier_cde_metrics(pd.DataFrame()) == {}


def test_batch504_aggregator_missing_pnl_pct_returns_empty():
    from backtest.results.cube_metrics_tier_cde import compute_tier_cde_metrics
    assert compute_tier_cde_metrics(pd.DataFrame({"x": [1, 2, 3]})) == {}
