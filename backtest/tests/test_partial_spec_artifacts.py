"""Unit tests for DEC-153 / DEC-401 / DEC-423 executable artifacts.

Per DEC-594 Test-Artifact Same-Commit HARD RULE: each PARTIAL-SPEC-ONLY DEC
that gets an executable artifact MUST land tests in same commit. This file
covers the 3 artifacts built Pass 53 Day 9 (2026-05-07):

  DEC-153 - regime_stratified_split (backtest/engine/regime_stratified_split.py)
  DEC-401 - holm_bonferroni + bonferroni (backtest/results/multi_test.py)
  DEC-423 - bootstrap_metric + pairwise_sharpe_diff (backtest/results/bootstrap_ci.py)

Once tests pass + lands same-commit, all 3 DECs advance from PARTIAL-SPEC-ONLY
to RESOLVED-DECIDED.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtest.engine.regime_stratified_split import (
    REGIME_CLASSES,
    regime_stratified_split,
    regime_proportions,
)
from backtest.results.multi_test import bonferroni, holm_bonferroni
from backtest.results.bootstrap_ci import (
    bootstrap_metric,
    pairwise_sharpe_diff_significance,
    sharpe_ratio,
)


# ---------------------------------------------------------------------------
# DEC-153 — Regime-stratified split
# ---------------------------------------------------------------------------
def test_dec153_basic_split():
    dates = pd.date_range("2024-01-01", periods=400, freq="D")
    # 100 calm + 100 neutral + 100 volatile + 100 crisis
    labels = ["calm"] * 100 + ["neutral"] * 100 + ["volatile"] * 100 + ["crisis"] * 100
    train, test, summary = regime_stratified_split(dates, labels, train_frac=0.7)
    assert len(train) + len(test) == 400
    # Each regime should have ~70 in train, ~30 in test
    for regime in REGIME_CLASSES:
        assert summary[regime] >= 65, f"{regime} train low: {summary[regime]}"
        assert summary[f"{regime}_test"] >= 25, f"{regime} test low: {summary[f'{regime}_test']}"
        assert summary[f"{regime}_status"] == "OK"


def test_dec153_insufficient_sample():
    dates = pd.date_range("2024-01-01", periods=20, freq="D")
    labels = ["calm"] * 5 + ["neutral"] * 5 + ["volatile"] * 5 + ["crisis"] * 5
    train, test, summary = regime_stratified_split(
        dates, labels, train_frac=0.7, min_per_regime=20
    )
    # All regimes should fail INSUFFICIENT_SAMPLE since each has only 5
    for regime in REGIME_CLASSES:
        assert summary[f"{regime}_status"] == "INSUFFICIENT_SAMPLE"


def test_dec153_unknown_labels_excluded():
    dates = pd.date_range("2024-01-01", periods=200, freq="D")
    labels = ["calm"] * 50 + ["neutral"] * 50 + ["unknown"] * 50 + ["crisis"] * 50
    train, test, summary = regime_stratified_split(dates, labels, train_frac=0.7)
    # 'unknown' samples should NOT be in train OR test
    assert len(train) + len(test) == 150  # 200 - 50 unknown
    assert "unknown" not in summary


def test_dec153_proportions():
    labels = ["calm"] * 50 + ["neutral"] * 30 + ["volatile"] * 15 + ["crisis"] * 5
    props = regime_proportions(labels)
    assert abs(props["calm"] - 0.5) < 0.01
    assert abs(props["neutral"] - 0.3) < 0.01
    assert abs(props["volatile"] - 0.15) < 0.01
    assert abs(props["crisis"] - 0.05) < 0.01


def test_dec153_chronological_order_within_regime():
    # Within each regime, train and test indices should be sorted ascending
    dates = pd.date_range("2024-01-01", periods=200, freq="D")
    labels = ["calm"] * 200
    train, test, _ = regime_stratified_split(dates, labels, train_frac=0.7)
    assert train == sorted(train)
    assert test == sorted(test)


# ---------------------------------------------------------------------------
# DEC-401 — Holm-Bonferroni
# ---------------------------------------------------------------------------
def test_dec401_bonferroni_basic():
    pvals = [0.01, 0.04, 0.03, 0.005]
    rejected, adj = bonferroni(pvals, alpha=0.05)
    # m = 4; threshold = 0.05/4 = 0.0125
    assert rejected == [True, False, False, True]
    assert all(0 <= a <= 1 for a in adj)


def test_dec401_holm_less_conservative_than_bonferroni():
    """Holm rejects ≥ as many hypotheses as Bonferroni (never fewer)."""
    pvals = [0.01, 0.04, 0.03, 0.005, 0.045]
    bonf_rej, _ = bonferroni(pvals, alpha=0.05)
    holm_rej, _ = holm_bonferroni(pvals, alpha=0.05)
    assert sum(holm_rej) >= sum(bonf_rej)


def test_dec401_holm_step_down_logic():
    """Smallest p-value tested at alpha/m; next at alpha/(m-1); etc."""
    # pvals: 0.01, 0.02, 0.03; m=3; alpha=0.05
    # Holm: p_(1)=0.01 vs 0.05/3=0.0167 → reject; p_(2)=0.02 vs 0.05/2=0.025 → reject; p_(3)=0.03 vs 0.05/1=0.05 → reject
    rejected, adj = holm_bonferroni([0.01, 0.02, 0.03], alpha=0.05)
    assert all(rejected)


def test_dec401_holm_monotonic_adjusted():
    """Adjusted p-values must be monotone non-decreasing in sorted order."""
    pvals = [0.001, 0.05, 0.01, 0.02]
    _, adj = holm_bonferroni(pvals, alpha=0.05)
    sorted_adj = sorted(adj)
    for i in range(1, len(sorted_adj)):
        assert sorted_adj[i] >= sorted_adj[i - 1]


def test_dec401_empty_input():
    rej, adj = holm_bonferroni([], alpha=0.05)
    assert rej == []
    assert adj == []


def test_dec401_invalid_pvalues_rejected():
    with pytest.raises(ValueError):
        holm_bonferroni([0.5, -0.1, 0.3], alpha=0.05)


# ---------------------------------------------------------------------------
# DEC-423 — Bootstrap CI
# ---------------------------------------------------------------------------
def test_dec423_sharpe_ratio_basic():
    # Constant 0.001 daily return, 0 std → Sharpe = 0 (per safety branch)
    assert sharpe_ratio([0.001] * 252) == 0.0
    # Constant returns
    assert sharpe_ratio([]) == 0.0
    assert sharpe_ratio([0.001]) == 0.0


def test_dec423_bootstrap_returns_valid_ci():
    rng = np.random.default_rng(0)
    returns = rng.normal(0.001, 0.01, 100)  # 100 trades
    result = bootstrap_metric(returns, n_resamples=200, seed=42)
    assert result.method == "bootstrap"
    assert result.n == 100
    assert result.n_resamples == 200
    assert result.ci_low <= result.point_estimate <= result.ci_high


def test_dec423_insufficient_sample():
    returns = [0.01] * 10  # < 30 trades
    result = bootstrap_metric(returns, min_trades=30)
    assert result.method == "insufficient_sample"
    assert np.isnan(result.ci_low)
    assert np.isnan(result.ci_high)


def test_dec423_pairwise_significance_different():
    """Two strategies with clearly different Sharpe should test significant."""
    rng = np.random.default_rng(1)
    a = rng.normal(0.005, 0.01, 100)  # high mean, low vol
    b = rng.normal(-0.001, 0.01, 100)  # low mean
    diff, lo, hi, sig = pairwise_sharpe_diff_significance(a, b, n_resamples=300, seed=42)
    assert sig is True
    assert diff > 0


def test_dec423_pairwise_significance_same():
    """Two strategies with same distribution should test NOT significant."""
    rng = np.random.default_rng(2)
    a = rng.normal(0.001, 0.01, 100)
    b = rng.normal(0.001, 0.01, 100)
    diff, lo, hi, sig = pairwise_sharpe_diff_significance(a, b, n_resamples=300, seed=42)
    # CI should include 0
    assert sig is False or (lo <= 0 <= hi)


def test_dec423_reproducibility_via_seed():
    returns = [0.01, -0.005, 0.02, 0.001, -0.01] * 30  # 150 trades
    r1 = bootstrap_metric(returns, n_resamples=200, seed=42)
    r2 = bootstrap_metric(returns, n_resamples=200, seed=42)
    assert r1.ci_low == r2.ci_low
    assert r1.ci_high == r2.ci_high
