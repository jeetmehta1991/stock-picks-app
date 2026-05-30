"""Batch 478 (2026-05-29) -- M9 correlation-aware effective strategy count tests."""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from backtest.engine.correlation_aware_count import (
    build_strategy_cluster_lookup,
    effective_strategy_count,
)
from backtest.results.strategy_correlation import (
    compute_strategy_correlation_matrix,
)


def test_build_lookup_returns_empty_on_empty_matrix():
    lookup, n = build_strategy_cluster_lookup(pd.DataFrame())
    assert lookup == {}
    assert n == 0


def test_effective_count_singletons_count_as_own_clusters():
    lookup = {}
    count = effective_strategy_count(["A", "B", "C"], lookup)
    assert count == 3


def test_effective_count_collapses_clustered_strategies():
    lookup = {"A": 0, "B": 0, "C": 1}
    # A + B in same cluster -> 1; C alone -> 1; total 2
    assert effective_strategy_count(["A", "B", "C"], lookup) == 2


def test_effective_count_mixes_clustered_and_singleton():
    lookup = {"A": 0, "B": 0}
    # A + B -> 1 cluster; C unknown -> 1 singleton; total 2
    assert effective_strategy_count(["A", "B", "C"], lookup) == 2


def test_effective_count_dedupes_repeated_strategies():
    lookup = {"A": 0}
    assert effective_strategy_count(["A", "A", "A"], lookup) == 1


def test_end_to_end_correlation_to_effective_count():
    """Build a correlation matrix from synthetic trade log, then verify
    the effective-count helper collapses the correlated pair."""
    rng = np.random.RandomState(0)
    dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(30)]
    rows = []
    for d in dates:
        n_pair = int(rng.choice([0, 1, 2, 3]))
        for _ in range(n_pair):
            rows.append({"strategy": "redundant_a", "entry_date": pd.Timestamp(d)})
            rows.append({"strategy": "redundant_b", "entry_date": pd.Timestamp(d)})
        if rng.rand() < 0.4:
            rows.append({"strategy": "independent_c", "entry_date": pd.Timestamp(d)})
    df = pd.DataFrame(rows)
    corr = compute_strategy_correlation_matrix(df)
    lookup, n_clusters = build_strategy_cluster_lookup(corr, threshold=0.8)
    # redundant_a + redundant_b should be in the same cluster
    assert lookup.get("redundant_a") == lookup.get("redundant_b")
    # independent_c either in its own cluster (singleton) or absent
    cnt_raw = 3   # all three strategies firing
    cnt_eff = effective_strategy_count(
        ["redundant_a", "redundant_b", "independent_c"], lookup,
    )
    assert cnt_eff < cnt_raw, \
        f"effective count {cnt_eff} should be less than raw {cnt_raw}"
