"""Tests for cube_populator.py (Batch 243 / DEC-422 + DEC-426)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtest.results.cube_populator import (
    compute_cell_metrics,
    evaluate_cell_criteria,
    extract_winners,
    populate_cube,
)


def _make_trades(strategy, exit_method, regime, pnls, tickers=None):
    n = len(pnls)
    return pd.DataFrame({
        "strategy":    [strategy] * n,
        "exit_method": [exit_method] * n,
        "regime":      [regime] * n,
        "pnl_pct":     pnls,
        "ticker":      tickers or ["AAPL"] * n,
    })


def test_populate_cube_empty_returns_empty():
    out = populate_cube(pd.DataFrame())
    assert out.empty


def test_populate_cube_missing_columns_raises():
    bad_df = pd.DataFrame({"strategy": ["rsi"], "pnl_pct": [0.5]})
    with pytest.raises(ValueError):
        populate_cube(bad_df)


def test_compute_cell_metrics_basic():
    pnls = [1.0, -0.5, 2.0, 1.5, -1.0, 0.5, 1.0, 2.0, -0.5, 1.5,
            1.0, 0.5, 1.5, 2.0, 1.0, -1.0, 0.5, 2.5, 1.0, 0.5,
            1.5, 1.0, 0.5, 2.0, 1.5, -0.5, 1.0, 1.5, 2.0, 1.0,
            0.5, 1.5]
    trades = _make_trades("rsi", "atr_trail_1x", "bull", pnls)
    metrics = compute_cell_metrics(trades)
    assert metrics["n_trades"] == len(pnls)
    assert metrics["win_rate"] > 0.5
    assert metrics["expected_value"] > 0
    assert metrics["profit_factor"] > 1.0


def test_evaluate_cell_criteria_p3_on_insufficient_trades():
    metrics = {"n_trades": 10}
    v = evaluate_cell_criteria(metrics, regime="bull")
    assert v["priority"] == "P3"
    assert v["fail_reason"] == "insufficient_trades"


def test_evaluate_cell_criteria_high_vol_regime_relaxation():
    metrics = {
        "n_trades":       40,
        "win_rate":       0.52,
        "profit_factor":  1.3,
        "expected_value": 0.8,
        "win_loss_ratio": 1.2,
        "max_dd":         0.22,
        "total_roi":      30.0,
        "sharpe":         0.8,
        "t_stat":         3.5,
        "bonferroni_p":   0.04,
        "psr":            0.96,
        "rr_ratio":       2.0,
    }
    v_crisis = evaluate_cell_criteria(metrics, regime="crisis")
    v_bull = evaluate_cell_criteria(metrics, regime="bull")
    assert v_crisis["checks"]["win_rate"]
    assert not v_bull["checks"]["win_rate"]


def test_evaluate_cell_criteria_p1_when_all_pass():
    metrics = {
        "n_trades":       100,
        "win_rate":       0.60,
        "profit_factor":  2.0,
        "expected_value": 1.0,
        "win_loss_ratio": 1.5,
        "max_dd":         0.10,
        "total_roi":      100.0,
        "sharpe":         1.2,
        "t_stat":         5.0,
        "bonferroni_p":   0.001,
        "psr":            0.99,
        "rr_ratio":       2.5,
    }
    v = evaluate_cell_criteria(metrics, regime="bull")
    assert v["priority"] == "P1"
    assert v["all_criteria_pass"]
    assert v["five_gate_pass"]


def test_populate_cube_yields_dataframe_with_combo_id():
    pnls = list(np.random.RandomState(7).normal(loc=0.5, scale=2.0, size=50))
    trades = _make_trades("rsi", "atr_trail_1x", "bull", pnls)
    cube = populate_cube(trades)
    assert not cube.empty
    assert "combo_id" in cube.columns
    assert "priority" in cube.columns
    assert cube["combo_id"].iloc[0] == "rsi__atr_trail_1x__bull"


def test_populate_cube_multiple_cells_sorted_by_priority():
    pnls_winner = list(np.random.RandomState(7).normal(loc=1.0, scale=1.0, size=100))
    pnls_loser = list(np.random.RandomState(7).normal(loc=-0.5, scale=1.5, size=50))
    t1 = _make_trades("rsi", "atr_trail_1x", "bull", pnls_winner)
    t2 = _make_trades("mfi", "fixed_stop", "bear", pnls_loser)
    cube = populate_cube(pd.concat([t1, t2], ignore_index=True))
    assert len(cube) == 2
    priority_order = {"P1": 0, "P2": 1, "P3": 2}
    p0 = priority_order.get(cube["priority"].iloc[0], 99)
    p1 = priority_order.get(cube["priority"].iloc[1], 99)
    assert p0 <= p1


def test_extract_winners_p1_only_returns_dataframe():
    pnls = list(np.random.RandomState(7).normal(loc=2.0, scale=0.5, size=100))
    trades = _make_trades("strat_winner", "atr_trail_1x", "bull", pnls)
    cube = populate_cube(trades)
    winners = extract_winners(cube, priority_filter=("P1",))
    assert isinstance(winners, pd.DataFrame)


def test_populate_cube_regime_at_entry_column_normalized():
    df = pd.DataFrame({
        "strategy":         ["rsi"] * 30,
        "exit_method":      ["atr_trail_1x"] * 30,
        "regime_at_entry":  ["bull"] * 30,
        "pnl_pct":          [1.0] * 30,
        "ticker":           ["AAPL"] * 30,
    })
    cube = populate_cube(df)
    assert not cube.empty
    assert cube["regime"].iloc[0] == "bull"


def test_populate_cube_combo_id_format():
    pnls = [1.0] * 30
    trades = _make_trades("mfi_oversold", "trailing_stop", "neutral", pnls)
    cube = populate_cube(trades)
    assert cube["combo_id"].iloc[0] == "mfi_oversold__trailing_stop__neutral"


def test_populate_cube_no_ticker_column_safe():
    pnls = [1.0] * 30
    df = pd.DataFrame({
        "strategy":    ["rsi"] * 30,
        "exit_method": ["atr"] * 30,
        "regime":      ["bull"] * 30,
        "pnl_pct":     pnls,
    })
    cube = populate_cube(df)
    assert not cube.empty
    assert cube["tickers_fired"].iloc[0] == []
