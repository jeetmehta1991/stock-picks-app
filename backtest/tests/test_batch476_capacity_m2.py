"""Batch 476 (2026-05-29) -- M2 capacity analysis tests."""
from __future__ import annotations

import pandas as pd
import pytest

from backtest.results.capacity_analysis import (
    CAPACITY_ADV_THRESHOLD,
    compute_cell_capacity,
    compute_cell_capacity_from_trade_log,
)


# ----------------------------------------------------------------------
# Scalar API
# ----------------------------------------------------------------------
def test_empty_returns_zero_dict():
    m = compute_cell_capacity([], [])
    assert m["n"] == 0
    assert m["capacity_concern_flag"] is False


def test_size_pct_below_threshold_does_not_flag():
    # Position $1000, ADV $10M -> 0.0001 == 0.01 pct, well below 0.1 pct
    m = compute_cell_capacity([10_000_000] * 5, [1_000] * 5)
    assert m["median_size_pct_of_adv"] == pytest.approx(0.0001, abs=1e-7)
    assert m["capacity_concern_flag"] is False


def test_size_pct_above_threshold_flags():
    # Position $50_000, ADV $10M -> 0.005 (0.5 pct), above 0.1 pct
    m = compute_cell_capacity([10_000_000] * 5, [50_000] * 5)
    assert m["median_size_pct_of_adv"] > CAPACITY_ADV_THRESHOLD
    assert m["capacity_concern_flag"] is True


def test_max_ratio_captures_worst_case():
    advs = [10_000_000] * 4 + [1_000_000]   # one tiny-ADV outlier
    poss = [1_000] * 4 + [50_000]           # outlier position $50k vs $1M ADV
    m = compute_cell_capacity(advs, poss)
    # Median position/adv = 1000/10M = 0.0001 -> below flag
    assert m["capacity_concern_flag"] is False
    # Max ratio = 50000/1000000 = 0.05 (5 pct) -- captured as max
    assert m["max_size_pct_of_adv"] == pytest.approx(0.05, abs=1e-4)


def test_zero_adv_rows_dropped():
    advs = [0.0, 10_000_000.0]
    poss = [1000.0, 1000.0]
    m = compute_cell_capacity(advs, poss)
    # Only the second row counts -> n=1
    assert m["n"] == 1
    assert m["median_adv_at_entry"] == 10_000_000.0


# ----------------------------------------------------------------------
# DataFrame API
# ----------------------------------------------------------------------
def test_from_trade_log_empty_returns_schema_columns():
    out = compute_cell_capacity_from_trade_log(pd.DataFrame())
    assert out.empty
    for c in ("strategy", "exit_method", "regime",
              "n", "median_adv_at_entry", "median_position_dollars",
              "median_size_pct_of_adv", "max_size_pct_of_adv",
              "capacity_concern_flag"):
        assert c in out.columns


def test_from_trade_log_missing_cols_raises():
    df = pd.DataFrame({"strategy": ["a"], "exit_method": ["x"],
                       "regime": ["bull"], "pnl_pct": [1.0]})
    with pytest.raises(ValueError, match="missing"):
        compute_cell_capacity_from_trade_log(df)


def test_from_trade_log_flags_concentrated_cell():
    df = pd.DataFrame({
        "strategy":         ["high_imp"] * 5 + ["low_imp"] * 5,
        "exit_method":      ["x"] * 10,
        "regime":           ["bull"] * 10,
        "adv_at_entry":     [1_000_000.0] * 5 + [10_000_000.0] * 5,
        "position_dollars": [50_000.0] * 5 + [1_000.0] * 5,
        "pnl_pct":          [1.0] * 10,
    })
    out = compute_cell_capacity_from_trade_log(df)
    hi = out[out["strategy"] == "high_imp"].iloc[0]
    lo = out[out["strategy"] == "low_imp"].iloc[0]
    assert bool(hi["capacity_concern_flag"]) is True
    assert bool(lo["capacity_concern_flag"]) is False
