"""Tests for per-exit conditional analyzer (Pass 53 Day-9-evening v2).

Owner reframe: NOT universal-best-exit; instead "for each exit, where does it
dominate?" Per-exit conditional sweet-spot analysis.

Per DEC-594 same-commit: tests land with artifact + writer wiring.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtest.results.exit_conditional_analyzer import (
    DEFAULT_CONDITION_DIMS,
    compute_multi_dim_cube,
    compute_pairwise_dominance,
    find_sweet_spots,
)


def _make_synthetic_detail(
    n_trades_per_combo: int = 20,
    exit_methods: tuple = ("trailing_atr", "fixed_3r", "signal_reversal"),
    regimes: tuple = ("calm", "volatile"),
    sectors: tuple = ("Information Technology", "Energy"),
    cap_bands: tuple = ("large_10_200B",),
    vol_bands: tuple = ("low_lt_15",),
    hold_bands: tuple = ("medium_4_10d",),
) -> pd.DataFrame:
    """Synthetic trade_exit_detail with known per-(exit, regime) edges."""
    rng = np.random.default_rng(0)
    rows = []
    # Per design: trailing_atr wins in volatile; fixed_3r wins in calm
    for exit_m in exit_methods:
        for regime in regimes:
            for sector in sectors:
                for cap in cap_bands:
                    for vol in vol_bands:
                        for hold in hold_bands:
                            # Synthesize per-(exit, regime) edge
                            if exit_m == "trailing_atr" and regime == "volatile":
                                mean_pnl = 0.04
                            elif exit_m == "fixed_3r" and regime == "calm":
                                mean_pnl = 0.04
                            else:
                                mean_pnl = 0.01  # baseline
                            for _ in range(n_trades_per_combo):
                                pnl = rng.normal(mean_pnl, 0.02)
                                rows.append({
                                    "exit_method": exit_m,
                                    "strategy": "test_strat",
                                    "regime_at_entry": regime,
                                    "sector": sector,
                                    "cap_band": cap,
                                    "vol_band": vol,
                                    "hold_duration_band": hold,
                                    "pnl_pct": pnl,
                                    "win": pnl > 0,
                                })
    return pd.DataFrame(rows)


def test_multi_dim_cube_returns_long_form():
    df = _make_synthetic_detail()
    cube = compute_multi_dim_cube(df, dims=DEFAULT_CONDITION_DIMS)
    assert not cube.empty
    # Column structure: exit_method + 5 dims + 4 metrics
    expected_cols = ["exit_method", "regime_at_entry", "sector",
                      "cap_band", "vol_band", "hold_duration_band",
                      "n", "win_rate", "avg_pnl_pct", "total_pnl_pct", "sharpe_proxy"]
    for c in expected_cols:
        assert c in cube.columns, f"Missing: {c}"


def test_multi_dim_cube_drops_undersampled_cells():
    df = _make_synthetic_detail(n_trades_per_combo=2)  # below MIN_TRADES_PER_CELL=5
    cube = compute_multi_dim_cube(df, dims=DEFAULT_CONDITION_DIMS, min_trades_per_cell=5)
    assert cube.empty


def test_multi_dim_cube_raises_on_missing_dim():
    df = pd.DataFrame({"exit_method": ["a"], "pnl_pct": [0.01], "win": [True]})
    with pytest.raises(KeyError):
        compute_multi_dim_cube(df, dims=("regime_at_entry",))


def test_sweet_spots_finds_per_exit_winners():
    """Per-exit top-K sweet spots — synthetic data has trailing_atr winning in
    volatile regime and fixed_3r winning in calm regime."""
    df = _make_synthetic_detail()
    cube = compute_multi_dim_cube(df, dims=DEFAULT_CONDITION_DIMS)
    spots = find_sweet_spots(cube, dims=DEFAULT_CONDITION_DIMS, top_k=5)
    assert not spots.empty
    # trailing_atr should appear with regime=volatile
    trailing_atr_spots = spots[spots["exit_method"] == "trailing_atr"]
    assert "volatile" in trailing_atr_spots["regime_at_entry"].values, \
        "trailing_atr should sweet-spot in volatile regime"
    # fixed_3r should appear with regime=calm
    fixed_3r_spots = spots[spots["exit_method"] == "fixed_3r"]
    assert "calm" in fixed_3r_spots["regime_at_entry"].values, \
        "fixed_3r should sweet-spot in calm regime"


def test_sweet_spots_columns_present():
    df = _make_synthetic_detail()
    cube = compute_multi_dim_cube(df, dims=DEFAULT_CONDITION_DIMS)
    spots = find_sweet_spots(cube, dims=DEFAULT_CONDITION_DIMS)
    expected = ["exit_method", "regime_at_entry", "total_pnl_pct",
                "runner_up_method", "edge_over_runner_up", "n"]
    for c in expected:
        assert c in spots.columns, f"Missing: {c}"


def test_sweet_spots_handles_empty_cube():
    spots = find_sweet_spots(pd.DataFrame(), dims=DEFAULT_CONDITION_DIMS)
    assert spots.empty


def test_pairwise_dominance_basic():
    df = _make_synthetic_detail()
    cube = compute_multi_dim_cube(df, dims=DEFAULT_CONDITION_DIMS)
    dom = compute_pairwise_dominance(cube, dims=DEFAULT_CONDITION_DIMS)
    assert not dom.empty
    assert "exit_a" in dom.columns
    assert "exit_b" in dom.columns
    assert "edge" in dom.columns
    assert "dominates" in dom.columns


def test_pairwise_dominance_synthetic_edge():
    """trailing_atr should dominate fixed_3r in volatile regime cells."""
    df = _make_synthetic_detail()
    cube = compute_multi_dim_cube(df, dims=DEFAULT_CONDITION_DIMS)
    dom = compute_pairwise_dominance(cube, dims=DEFAULT_CONDITION_DIMS,
                                      edge_threshold=0.05)
    # Find any row where trailing_atr beats fixed_3r in volatile regime
    volatile_pairs = dom[
        (dom["regime_at_entry"] == "volatile")
        & (((dom["exit_a"] == "trailing_atr") & (dom["exit_b"] == "fixed_3r"))
           | ((dom["exit_a"] == "fixed_3r") & (dom["exit_b"] == "trailing_atr")))
    ]
    if not volatile_pairs.empty:
        # If trailing_atr is exit_a, edge should be positive (a > b);
        # if trailing_atr is exit_b, edge should be negative
        for _, row in volatile_pairs.iterrows():
            if row["exit_a"] == "trailing_atr":
                assert row["edge"] > 0, "trailing_atr should beat fixed_3r in volatile"
            else:
                assert row["edge"] < 0, "fixed_3r should lose to trailing_atr in volatile"


def test_empty_input_returns_empty():
    cube = compute_multi_dim_cube(pd.DataFrame(), dims=DEFAULT_CONDITION_DIMS)
    assert cube.empty
    spots = find_sweet_spots(cube, dims=DEFAULT_CONDITION_DIMS)
    assert spots.empty
    dom = compute_pairwise_dominance(cube, dims=DEFAULT_CONDITION_DIMS)
    assert dom.empty
