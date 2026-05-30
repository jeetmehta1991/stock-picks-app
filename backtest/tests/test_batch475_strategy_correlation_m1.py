"""Batch 475 (2026-05-29) -- M1 inter-strategy correlation matrix tests."""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from backtest.results.strategy_correlation import (
    cluster_correlated_strategies,
    compute_strategy_correlation_matrix,
    redundant_strategy_pairs,
)


def _make_trade_log(rows):
    """rows is iterable of (strategy, entry_date)."""
    return pd.DataFrame([
        {"strategy": s, "entry_date": pd.Timestamp(d), "pnl_pct": 1.0,
         "ticker": "T", "exit_method": "x"}
        for s, d in rows
    ])


def test_empty_trade_log_returns_empty_matrix():
    out = compute_strategy_correlation_matrix(pd.DataFrame())
    assert out.empty


def test_missing_required_cols_raises():
    df = pd.DataFrame({"strategy": ["a"], "pnl_pct": [1.0]})
    with pytest.raises(ValueError):
        compute_strategy_correlation_matrix(df)


def test_two_perfectly_aligned_strategies_correlate_1():
    """Strategy A and B fire with identical daily counts -> corr ~= 1.0.
    Counts must VARY across days, otherwise the series is constant and
    corr is undefined."""
    dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(30)]
    rng = np.random.RandomState(0)
    rows = []
    for d in dates:
        n = int(rng.choice([0, 1, 2, 3]))
        for _ in range(n):
            rows.append(("A", d))
            rows.append(("B", d))
    out = compute_strategy_correlation_matrix(_make_trade_log(rows))
    assert "A" in out.columns and "B" in out.columns
    assert out.loc["A", "B"] == pytest.approx(1.0, abs=1e-6)


def test_anti_aligned_strategies_correlate_negative():
    """A fires on odd days, B on even days -> negative corr."""
    rows = []
    for i in range(40):
        d = date(2024, 1, 1) + timedelta(days=i)
        if i % 2 == 0:
            rows.append(("A", d))
        else:
            rows.append(("B", d))
    out = compute_strategy_correlation_matrix(_make_trade_log(rows))
    # Strategies that never fire on the same day -> negative correlation
    assert out.loc["A", "B"] < 0


def test_diagonal_is_one():
    # Variable daily counts so the series has non-zero variance
    rng = np.random.RandomState(0)
    rows = []
    for i in range(1, 31):
        d = date(2024, 1, 1) + timedelta(days=i)
        for _ in range(int(rng.choice([1, 2, 3]))):
            rows.append(("A", d))
    out = compute_strategy_correlation_matrix(_make_trade_log(rows))
    assert out.loc["A", "A"] == pytest.approx(1.0, abs=1e-6)


# ---------------------------------------------------------------------
# clustering
# ---------------------------------------------------------------------
def test_cluster_empty_matrix_returns_empty_list():
    assert cluster_correlated_strategies(pd.DataFrame()) == []


def test_cluster_isolates_correlated_pairs():
    rng = np.random.RandomState(0)
    n = 100
    # A and B fire identically with VARYING daily counts (non-constant
    # series). C and D fire on different patterns.
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    rows = []
    for d in dates:
        # A and B identical (will correlate ~1.0)
        cnt_ab = int(rng.choice([0, 1, 2, 3]))
        for _ in range(cnt_ab):
            rows.append(("A", d.date()))
            rows.append(("B", d.date()))
        # C random independent
        cnt_c = int(rng.choice([0, 1, 2]))
        for _ in range(cnt_c):
            rows.append(("C", d.date()))
        # D random independent
        cnt_d = int(rng.choice([0, 1, 4]))
        for _ in range(cnt_d):
            rows.append(("D", d.date()))
    df = _make_trade_log(rows)
    corr = compute_strategy_correlation_matrix(df)
    clusters = cluster_correlated_strategies(corr, threshold=0.8)
    # A + B should be in one cluster
    ab_cluster = next((c for c in clusters if "A" in c), None)
    assert ab_cluster is not None
    assert "B" in ab_cluster


def test_redundant_strategy_pairs_filters_by_threshold():
    rng = np.random.RandomState(0)
    rows = []
    dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(50)]
    for d in dates:
        # X and Y vary in lock step
        cnt = int(rng.choice([0, 1, 2, 3]))
        for _ in range(cnt):
            rows.append(("X", d))
            rows.append(("Y", d))
        # Z fires independently (random + isolated days)
        if rng.rand() < 0.3:
            rows.append(("Z", d))
    corr = compute_strategy_correlation_matrix(_make_trade_log(rows))
    pairs = redundant_strategy_pairs(corr, threshold=0.95)
    assert any({a, b} == {"X", "Y"} for a, b, _ in pairs)
    # Z should not pair with X or Y at 0.95 threshold (independent randomness)
    assert not any({"Z"} <= set([a, b]) for a, b, _ in pairs)
