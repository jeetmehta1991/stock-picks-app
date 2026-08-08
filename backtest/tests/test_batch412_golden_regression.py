"""Batch 412 (2026-05-28 owner-approved): cube-level golden regression test.

Drives ``run_exit_comparison`` end-to-end with the same trade fixture twice -
once with ``USE_VECTORIZED_EXITS=False`` (scalar baseline) and once with
``USE_VECTORIZED_EXITS=True`` (vectorized fast path) - and asserts the
resulting ``trade_detail_df`` rows are byte-identical for the 9 Tier 1
exit methods that get dispatched to the vectorized path.

This is the gate that protects production from drift if a future change to
either path accidentally diverges them. Per Batch 412 commit policy, the
feature flag CANNOT be flipped to ON in any production run until this test
passes.
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from backtest.engine import exit_strategies as exit_mod
from backtest.engine.exit_strategies import (
    EXIT_STRATEGIES,
    run_exit_comparison,
)
from backtest.engine.exit_strategies_vectorized import (
    EXIT_STRATEGIES_VECTORIZED,
)


TIER_1_METHODS = set(EXIT_STRATEGIES_VECTORIZED.keys())


# ---------------------------------------------------------------------------
# Fixture: synthetic 8-ticker x 60-bar universe with 5 staggered trades.
# Mix of trending, mean-reverting, gap-down patterns so multiple exit
# methods get exercised.
# ---------------------------------------------------------------------------

def _bdays(start, n):
    return pd.bdate_range(start=start, periods=n)


def _ticker_df(seed, n=80):
    """Reproducible OHLCV with mixed regimes."""
    rng = np.random.default_rng(seed)
    drift = rng.uniform(-0.0015, 0.0030)
    closes = 100.0 * np.cumprod(1.0 + drift + rng.normal(0, 0.012, n))
    intraday_range = closes * 0.012
    highs = closes + intraday_range * rng.uniform(0.3, 1.0, n)
    lows  = closes - intraday_range * rng.uniform(0.3, 1.0, n)
    opens = closes + rng.normal(0, intraday_range * 0.5)
    opens = np.clip(opens, lows, highs)
    idx = _bdays(date(2024, 1, 2), n)
    return pd.DataFrame({
        "open":   opens,
        "high":   highs,
        "low":    lows,
        "close":  closes,
        "volume": np.full(n, 1_000_000),
    }, index=idx)


def _build_trades_data():
    """8 tickers x 1-2 trades each. Entry on bar 10; signals include category."""
    trades = []
    for seed in range(1, 9):
        df = _ticker_df(seed, n=80)
        for trade_offset in (10, 25):
            entry_idx = trade_offset
            entry_date = df.index[entry_idx].date()
            entry_price = float(df["close"].iloc[entry_idx])
            direction = "long" if seed % 2 == 0 else "short"
            atr = entry_price * 0.015
            trades.append({
                "ticker":      f"T{seed}",
                "entry_date":  entry_date,
                "entry_price": entry_price,
                "direction":   direction,
                "atr":         atr,
                "signals":     {"category": "momentum"},
                "df":          df,
            })
    return trades


# ---------------------------------------------------------------------------
# Golden regression: scalar vs vectorized trade_detail_df byte-equal on
# Tier 1 methods.
# ---------------------------------------------------------------------------

def _run_cube(use_vectorized: bool):
    exit_mod.USE_VECTORIZED_EXITS = use_vectorized
    trades_data = _build_trades_data()
    _summary_df, detail_df = run_exit_comparison("golden_synthetic",
                                                 trades_data)
    return detail_df


def test_golden_trade_detail_byte_equal_tier_1():
    scalar_detail = _run_cube(use_vectorized=False)
    vec_detail = _run_cube(use_vectorized=True)

    # Filter to Tier 1 methods only - scalar/vec rows for non-Tier-1 methods
    # are identical (same scalar fn).
    scalar_t1 = scalar_detail[
        scalar_detail["exit_method"].isin(TIER_1_METHODS)
    ].reset_index(drop=True).sort_values(
        ["ticker", "entry_date", "exit_method"]
    ).reset_index(drop=True)
    vec_t1 = vec_detail[
        vec_detail["exit_method"].isin(TIER_1_METHODS)
    ].reset_index(drop=True).sort_values(
        ["ticker", "entry_date", "exit_method"]
    ).reset_index(drop=True)

    # Same number of rows
    assert len(scalar_t1) == len(vec_t1), (
        f"Row count drift: scalar={len(scalar_t1)} vec={len(vec_t1)}")

    # Same set of (ticker, entry_date, exit_method) tuples
    scalar_keys = set(zip(scalar_t1["ticker"], scalar_t1["entry_date"],
                           scalar_t1["exit_method"]))
    vec_keys = set(zip(vec_t1["ticker"], vec_t1["entry_date"],
                        vec_t1["exit_method"]))
    assert scalar_keys == vec_keys, (
        f"Key set drift: only_scalar={scalar_keys - vec_keys} "
        f"only_vec={vec_keys - scalar_keys}")

    # Per-row byte-equal on the value columns
    cols = ["pnl_pct", "win", "hold_days", "exit_price", "exit_date",
            "exit_reason"]
    for col in cols:
        if col == "exit_date":
            # Both stored as str(date) per run_exit_comparison
            mismatches = (scalar_t1[col].astype(str) !=
                          vec_t1[col].astype(str))
        else:
            mismatches = (scalar_t1[col] != vec_t1[col])
        if mismatches.any():
            offenders = scalar_t1.loc[mismatches, [
                "ticker", "entry_date", "exit_method"]].assign(
                scalar_val=scalar_t1.loc[mismatches, col].values,
                vec_val=vec_t1.loc[mismatches, col].values,
            )
            pytest.fail(
                f"Tier 1 cube regression drift on '{col}':\n{offenders}")


def test_golden_summary_byte_equal_tier_1():
    """Aggregate per-strategy summary row (win_rate / profit_factor /
    composite_score) must be byte-equal for Tier 1 exit methods."""
    exit_mod.USE_VECTORIZED_EXITS = False
    trades_data = _build_trades_data()
    scalar_summary, _ = run_exit_comparison("golden_synthetic", trades_data)
    scalar_summary = scalar_summary.set_index("exit_method")

    exit_mod.USE_VECTORIZED_EXITS = True
    trades_data = _build_trades_data()
    vec_summary, _ = run_exit_comparison("golden_synthetic", trades_data)
    vec_summary = vec_summary.set_index("exit_method")

    for method in TIER_1_METHODS:
        if method not in scalar_summary.index:
            # Method may have < 5 trades after dispatch -> skipped per
            # run_exit_comparison contract. Skip symmetrically.
            assert method not in vec_summary.index, (
                f"{method}: scalar skipped (n<5) but vec present")
            continue
        assert method in vec_summary.index, (
            f"{method}: vec skipped but scalar present")
        for col in ["trades", "win_rate", "profit_factor", "avg_pnl_pct",
                    "total_roi_pct", "max_drawdown_pct", "avg_hold_days",
                    "actual_fire_rate", "composite_score"]:
            assert scalar_summary.loc[method, col] == vec_summary.loc[
                method, col], (
                f"{method}.{col} drift: scalar="
                f"{scalar_summary.loc[method, col]} "
                f"vec={vec_summary.loc[method, col]}")


def test_flag_default_off_at_module_import():
    """Hard guarantee that importing the engine never silently flips the
    feature flag - any production run must opt-in via the CLI flag."""
    # B1485 (S6-B1481a): was importlib.reload(exit_mod). backtest.py imports FUNCTIONS
    # from exit_strategies BY VALUE (_pool_cube_replay_worker, run_exit_comparison), so a
    # reload rebinds them while the engine keeps the old objects - the same hazard that
    # made two GATE tests order-dependent (L330). The assertion wants the ON-DISK default,
    # which disk_value() reads without touching the live process.
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).resolve().parent))
    from config_disk import disk_value
    _es = _Path(__file__).resolve().parents[1] / "engine" / "exit_strategies.py"
    assert disk_value("USE_VECTORIZED_EXITS", _es) is False, (
        "USE_VECTORIZED_EXITS must default to False at import time so "
        "in-flight runs and next-default runs are unaffected by Batch 412.")
