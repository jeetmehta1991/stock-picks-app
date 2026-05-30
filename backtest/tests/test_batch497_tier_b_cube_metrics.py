"""Batch 497 (2026-05-31) -- Item 5 Tier B cube cell metrics tests.

Source: per CHECKLIST #77.
Queue row: EXECUTION_QUEUE.md item 5 Tier B.
Module:    backtest/results/cube_metrics_tier_b.py.

Each test runs a slice on a synthetic trade_log DataFrame so the
output is deterministic. Source columns mirror writer.py 46-col
schema verified against output_batch395_final/trade_log.csv as of
Batch 497.
"""
from __future__ import annotations

import pandas as pd
import pytest


def _make_trades(n_wins, n_losses, **col_overrides):
    """Build a trade_log DataFrame with n_wins=1 win rows + n_losses=0
    loss rows. col_overrides lets each test inject per-row column values.
    """
    rows = [{"win": 1, "pnl_pct": 1.5} for _ in range(n_wins)]
    rows += [{"win": 0, "pnl_pct": -1.0} for _ in range(n_losses)]
    df = pd.DataFrame(rows)
    for col, values in col_overrides.items():
        if not hasattr(values, "__len__"):
            values = [values] * len(df)
        assert len(values) == len(df), (
            f"col_override {col!r} length {len(values)} != df rows "
            f"{len(df)}"
        )
        df[col] = values
    return df


# ---------------------------------------------------------------------------
# Smart-money slice (criterion 7 from CLAUDE.md PASSING_CRITERIA)
# ---------------------------------------------------------------------------

def test_batch497_smart_money_slice_positive_lift():
    """10 wins + 10 losses; 10 of the wins have smart_money_score > 0
    and 10 of the losses have score <= 0 -> wr_lift = 1.0 - 0.0 = 1.0."""
    from backtest.results.cube_metrics_tier_b import compute_smart_money_slice
    df = _make_trades(
        n_wins=10, n_losses=10,
        smart_money_score=[1.0]*10 + [0.0]*10,
    )
    out = compute_smart_money_slice(df)
    assert out["n_with_smart_money"] == 10
    assert out["n_without_smart_money"] == 10
    assert out["wr_with_smart_money"] == pytest.approx(1.0, abs=1e-4)
    assert out["wr_without_smart_money"] == pytest.approx(0.0, abs=1e-4)
    assert out["wr_lift_smart_money"] == pytest.approx(1.0, abs=1e-4)


def test_batch497_smart_money_slice_no_lift():
    """Uniform smart_money_score distribution -> wr_lift near 0."""
    from backtest.results.cube_metrics_tier_b import compute_smart_money_slice
    df = _make_trades(
        n_wins=10, n_losses=10,
        smart_money_score=[1.0, 0.0] * 10,
    )
    out = compute_smart_money_slice(df)
    # Equal split -> both WRs are 0.5; lift = 0
    assert out["wr_lift_smart_money"] == pytest.approx(0.0, abs=1e-4)


def test_batch497_smart_money_slice_missing_column_returns_empty():
    from backtest.results.cube_metrics_tier_b import compute_smart_money_slice
    df = _make_trades(n_wins=5, n_losses=5)
    out = compute_smart_money_slice(df)
    assert out == {}


def test_batch497_smart_money_slice_empty_df_returns_empty():
    from backtest.results.cube_metrics_tier_b import compute_smart_money_slice
    out = compute_smart_money_slice(pd.DataFrame())
    assert out == {}


# ---------------------------------------------------------------------------
# Days-to-earnings bucketing
# ---------------------------------------------------------------------------

def test_batch497_days_to_earnings_buckets_correctly():
    """Each band must capture the right slice."""
    from backtest.results.cube_metrics_tier_b import compute_days_to_earnings_slice
    df = _make_trades(
        n_wins=10, n_losses=10,
        days_to_earnings=[3]*5 + [10]*5 + [30]*5 + [60]*5,
    )
    out = compute_days_to_earnings_slice(df)
    bands = out["wr_by_days_to_earnings_band"]
    assert "0_to_5d" in bands
    assert "6_to_15d" in bands
    assert "16_to_45d" in bands
    assert "over_45d" in bands
    # 5 wins in the first 5 rows (0_to_5d band) -> WR=1.0
    assert bands["0_to_5d"]["wr"] == pytest.approx(1.0, abs=1e-4)
    assert bands["0_to_5d"]["n"] == 5


def test_batch497_days_to_earnings_post_earnings_band():
    from backtest.results.cube_metrics_tier_b import compute_days_to_earnings_slice
    df = _make_trades(
        n_wins=3, n_losses=2,
        days_to_earnings=[-5, -10, -2, -1, -7],
    )
    out = compute_days_to_earnings_slice(df)
    bands = out["wr_by_days_to_earnings_band"]
    assert "post_earnings" in bands
    assert bands["post_earnings"]["n"] == 5


def test_batch497_days_to_earnings_unknown_band():
    """NaN days_to_earnings -> 'unknown' band."""
    from backtest.results.cube_metrics_tier_b import compute_days_to_earnings_slice
    df = _make_trades(
        n_wins=2, n_losses=2,
        days_to_earnings=[float("nan")] * 4,
    )
    out = compute_days_to_earnings_slice(df)
    bands = out["wr_by_days_to_earnings_band"]
    assert "unknown" in bands
    assert bands["unknown"]["n"] == 4


# ---------------------------------------------------------------------------
# Generic group-by slices
# ---------------------------------------------------------------------------

def test_batch497_confidence_tier_slice():
    from backtest.results.cube_metrics_tier_b import compute_confidence_tier_slice
    df = _make_trades(
        n_wins=10, n_losses=10,
        confidence_tier=["HIGH"]*10 + ["LOW"]*10,
    )
    out = compute_confidence_tier_slice(df)
    tiers = out["wr_by_confidence_tier"]
    assert "HIGH" in tiers
    assert "LOW" in tiers
    assert tiers["HIGH"]["wr"] == pytest.approx(1.0, abs=1e-4)
    assert tiers["LOW"]["wr"] == pytest.approx(0.0, abs=1e-4)


def test_batch497_regime_slice():
    from backtest.results.cube_metrics_tier_b import compute_regime_slice
    df = _make_trades(
        n_wins=12, n_losses=8,
        regime=["bull"]*6 + ["bear"]*6 + ["bull"]*4 + ["bear"]*4,
    )
    out = compute_regime_slice(df)
    regimes = out["wr_by_regime"]
    assert "bull" in regimes
    assert "bear" in regimes


def test_batch497_min_group_size_skips_small_groups():
    """Groups with fewer than 5 trades are dropped."""
    from backtest.results.cube_metrics_tier_b import compute_confidence_tier_slice
    df = _make_trades(
        n_wins=10, n_losses=10,
        confidence_tier=["HIGH"]*18 + ["LOW"]*2,  # LOW has only 2
    )
    out = compute_confidence_tier_slice(df)
    tiers = out["wr_by_confidence_tier"]
    assert "HIGH" in tiers
    assert "LOW" not in tiers


def test_batch497_circuit_breaker_slice():
    from backtest.results.cube_metrics_tier_b import compute_circuit_breaker_slice
    df = _make_trades(
        n_wins=10, n_losses=10,
        circuit_breaker_level=[0]*10 + [2]*10,
    )
    out = compute_circuit_breaker_slice(df)
    levels = out["wr_by_circuit_breaker_level"]
    assert "0" in levels
    assert "2" in levels


def test_batch497_sector_slice():
    from backtest.results.cube_metrics_tier_b import compute_sector_slice
    df = _make_trades(
        n_wins=10, n_losses=10,
        sector=["Tech"]*10 + ["Energy"]*10,
    )
    out = compute_sector_slice(df)
    sectors = out["wr_by_sector"]
    assert "Tech" in sectors
    assert "Energy" in sectors


# ---------------------------------------------------------------------------
# Macro score bucketing
# ---------------------------------------------------------------------------

def test_batch497_macro_score_buckets():
    from backtest.results.cube_metrics_tier_b import compute_macro_score_slice
    df = _make_trades(
        n_wins=15, n_losses=15,
        macro_score=[-1]*10 + [0]*10 + [1]*10,
    )
    out = compute_macro_score_slice(df)
    bands = out["wr_by_macro_score_band"]
    assert "negative" in bands
    assert "neutral" in bands
    assert "positive" in bands


# ---------------------------------------------------------------------------
# Top-level aggregator
# ---------------------------------------------------------------------------

def test_batch497_aggregator_merges_all_slices():
    from backtest.results.cube_metrics_tier_b import compute_tier_b_metrics
    df = _make_trades(
        n_wins=10, n_losses=10,
        smart_money_score=[1.0]*10 + [0.0]*10,
        days_to_earnings=[3, 10, 30, 60, 80] * 4,
        confidence_tier=["HIGH"]*10 + ["MEDIUM"]*10,
        regime=["bull"]*10 + ["bear"]*10,
        macro_score=[1]*5 + [-1]*5 + [0]*5 + [1]*5,
    )
    out = compute_tier_b_metrics(df)
    # All slices present
    assert "wr_lift_smart_money" in out
    assert "wr_by_days_to_earnings_band" in out
    assert "wr_by_confidence_tier" in out
    assert "wr_by_regime" in out
    assert "wr_by_macro_score_band" in out


def test_batch497_aggregator_empty_df_returns_empty():
    from backtest.results.cube_metrics_tier_b import compute_tier_b_metrics
    assert compute_tier_b_metrics(pd.DataFrame()) == {}


def test_batch497_aggregator_partial_columns_degrades_gracefully():
    """If only some columns present, only those slices emit."""
    from backtest.results.cube_metrics_tier_b import compute_tier_b_metrics
    df = _make_trades(
        n_wins=10, n_losses=10,
        regime=["bull"]*10 + ["bear"]*10,
    )
    out = compute_tier_b_metrics(df)
    # Only regime slice should fire
    assert "wr_by_regime" in out
    assert "wr_lift_smart_money" not in out
    assert "wr_by_days_to_earnings_band" not in out
