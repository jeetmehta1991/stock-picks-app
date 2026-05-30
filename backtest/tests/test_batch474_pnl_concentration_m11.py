"""Batch 474 (2026-05-29) -- M11 PnL concentration metric tests."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtest.results.pnl_concentration import (
    compute_pnl_concentration,
    compute_pnl_concentration_from_trade_log,
)


# ---------------------------------------------------------------------
# Scalar API: compute_pnl_concentration
# ---------------------------------------------------------------------
def test_empty_input_returns_zero_metrics():
    m = compute_pnl_concentration([])
    assert m == {
        "n": 0,
        "pnl_concentration_top1_pct": 0.0,
        "pnl_concentration_top5_pct": 0.0,
        "pnl_hhi": 0.0,
    }


def test_single_trade_is_fully_concentrated():
    m = compute_pnl_concentration([5.0])
    assert m["n"] == 1
    assert m["pnl_concentration_top1_pct"] == 1.0
    assert m["pnl_concentration_top5_pct"] == 1.0
    assert m["pnl_hhi"] == 1.0


def test_uniform_distribution_minimum_hhi():
    pnls = [1.0] * 100
    m = compute_pnl_concentration(pnls)
    # top1 = 1/100 = 0.01; HHI = 1/100 = 0.01
    assert m["pnl_concentration_top1_pct"] == pytest.approx(0.01, abs=1e-6)
    assert m["pnl_hhi"] == pytest.approx(0.01, abs=1e-6)
    # top5 = 0.05
    assert m["pnl_concentration_top5_pct"] == pytest.approx(0.05, abs=1e-6)


def test_one_outsized_trade_dominates():
    pnls = [0.01] * 99 + [50.0]  # 50.0 dwarfs the 99 small ones
    m = compute_pnl_concentration(pnls)
    # top1 should be very close to 1.0
    assert m["pnl_concentration_top1_pct"] > 0.95
    assert m["pnl_hhi"] > 0.9


def test_absolute_value_used_for_concentration():
    """Negative pnls count toward concentration too -- a -100% loss is just
    as informative as a +100% gain for risk-concentration purposes."""
    pnls = [-50.0, 1.0, 1.0]
    m = compute_pnl_concentration(pnls)
    # top1 = 50 / 52 ~= 0.96
    assert m["pnl_concentration_top1_pct"] == pytest.approx(50 / 52, abs=1e-4)


def test_all_zeros_returns_zero_metrics_without_div_by_zero():
    m = compute_pnl_concentration([0.0, 0.0, 0.0])
    assert m["n"] == 3
    assert m["pnl_concentration_top1_pct"] == 0.0
    assert m["pnl_hhi"] == 0.0


# ---------------------------------------------------------------------
# DataFrame API: compute_pnl_concentration_from_trade_log
# ---------------------------------------------------------------------
def test_from_trade_log_empty_returns_empty_df_with_schema():
    out = compute_pnl_concentration_from_trade_log(pd.DataFrame())
    assert out.empty
    for c in ("strategy", "exit_method", "regime",
              "n", "pnl_concentration_top1_pct",
              "pnl_concentration_top5_pct", "pnl_hhi"):
        assert c in out.columns


def test_from_trade_log_missing_group_col_raises():
    df = pd.DataFrame({
        "strategy": ["A"], "pnl_pct": [1.0],
    })
    with pytest.raises(ValueError, match="missing group cols"):
        compute_pnl_concentration_from_trade_log(df)


def test_from_trade_log_missing_pnl_col_raises():
    df = pd.DataFrame({
        "strategy": ["A"], "exit_method": ["x"], "regime": ["bull"],
    })
    with pytest.raises(ValueError, match="missing pnl_col"):
        compute_pnl_concentration_from_trade_log(df)


def test_from_trade_log_groups_by_strategy_exit_regime():
    rng = np.random.RandomState(0)
    df = pd.DataFrame({
        "strategy":    ["A"] * 10 + ["B"] * 10,
        "exit_method": ["x"] * 10 + ["y"] * 10,
        "regime":      ["bull"] * 20,
        "pnl_pct":     list(rng.normal(0.5, 1.0, 20)),
    })
    out = compute_pnl_concentration_from_trade_log(df)
    assert len(out) == 2  # two (strat, exit, regime) cells
    assert set(out["strategy"]) == {"A", "B"}
    assert (out["n"] == 10).all()


def test_from_trade_log_outlier_cell_has_high_top1():
    # Cell A: one huge outlier. Cell B: balanced.
    df = pd.DataFrame({
        "strategy":    ["A"] * 10 + ["B"] * 10,
        "exit_method": ["x"] * 10 + ["x"] * 10,
        "regime":      ["bull"] * 20,
        "pnl_pct":     [0.01] * 9 + [100.0] + [1.0] * 10,
    })
    out = compute_pnl_concentration_from_trade_log(df)
    a = out[out["strategy"] == "A"].iloc[0]
    b = out[out["strategy"] == "B"].iloc[0]
    assert a["pnl_concentration_top1_pct"] > 0.95
    assert b["pnl_concentration_top1_pct"] == pytest.approx(0.10, abs=1e-4)
