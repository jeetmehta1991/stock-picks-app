"""Cube methodology hardening (Batch 266).

Regression coverage for COMPREHENSIVE_REVIEW_2026_05_20.md Section 3
findings - exit_strategy_best.csv was inflating earnings_blackout to
~80% WR / +100% mean PnL / 913-day holds because most trades defaulted
to "no_earnings_known" and rode the 2022-2026 bull market to end-of-data.

Hardening (in `run_exit_comparison`):
  1. Added `actual_fire_rate` column - fraction of trades where the exit
     method's intended trigger actually fired (vs defaulted to a non-fire
     reason like end_of_data / no_earnings_known / max_days).
  2. `recommended=True` now requires composite_score top-rank AND
     avg_hold_days <= 250 AND actual_fire_rate >= 0.5.
  3. NON_FIRE_EXIT_REASONS is the canonical set of fallback reasons that
     do NOT count as a real exit-method trigger.
"""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from backtest.engine.exit_strategies import (
    CUBE_MAX_AVG_HOLD_DAYS,
    CUBE_MIN_FIRE_RATE,
    NON_FIRE_EXIT_REASONS,
    run_exit_comparison,
)


def _build_trade_setup(n_bars: int = 100, start: str = "2023-01-03",
                       slope: float = 1.0, ticker: str = "TEST"):
    """Build a single synthetic trade setup with an uptrend (long entry profits)."""
    idx = pd.bdate_range(start=start, periods=n_bars)
    close = 100.0 + np.arange(n_bars) * slope
    df = pd.DataFrame({
        "open":  close - 0.1,
        "high":  close + 0.5,
        "low":   close - 0.5,
        "close": close,
        "volume": 1_000_000,
    }, index=idx)
    return {
        "ticker":      ticker,
        "entry_date":  idx[0].date(),
        "entry_price": float(close[0]),
        "direction":   "long",
        "atr":         1.0,
        "df":          df,
        "signals":     {"ticker": ticker, "strategy_name": "test_strategy",
                         "category": "momentum"},
    }


def test_non_fire_reasons_set_is_canonical():
    """The fallback reasons we mark as non-fire must include all known
    'method didn't trigger' branches in exit_strategies.py."""
    expected_subset = {
        "no_data",
        "end_of_data",
        "max_days",
        "no_earnings_known",
        "no_upcoming_earnings",
        "earnings_tolerant_skip",
    }
    assert expected_subset.issubset(NON_FIRE_EXIT_REASONS), (
        f"NON_FIRE_EXIT_REASONS missing canonical fallbacks: "
        f"{expected_subset - NON_FIRE_EXIT_REASONS}"
    )


def test_actual_fire_rate_column_present():
    """run_exit_comparison must emit actual_fire_rate per (strategy x exit)."""
    trades = [_build_trade_setup() for _ in range(6)]
    summary, _detail = run_exit_comparison("test_strategy", trades)
    assert not summary.empty
    assert "actual_fire_rate" in summary.columns
    assert summary["actual_fire_rate"].between(0.0, 1.0).all()


def test_per_trade_detail_carries_exit_reason():
    """trade_detail_df must expose exit_reason so downstream filters work."""
    trades = [_build_trade_setup() for _ in range(6)]
    _summary, detail = run_exit_comparison("test_strategy", trades)
    assert not detail.empty
    assert "exit_reason" in detail.columns


def test_recommended_rejects_long_hold_artifact():
    """A row with avg_hold_days > 250 must NOT be recommended even if its
    composite_score is the highest. This dethrones the earnings_blackout
    long-hold artifact identified in the 2026-05-20 review."""
    # Build long uptrend so trailing exits fire mid-trade but earnings_blackout
    # (no calendar data) rides all 400 bars to end_of_data.
    trades = [_build_trade_setup(n_bars=400, slope=2.0) for _ in range(8)]
    summary, _ = run_exit_comparison("test_strategy", trades)
    # Sanity: at least one non-firing exit went long-hold.
    long_hold_rows = summary[summary["avg_hold_days"] > CUBE_MAX_AVG_HOLD_DAYS]
    if long_hold_rows.empty:
        pytest.skip("Fixture didn't produce a long-hold row")
    # Any long-hold row must not be flagged as recommended.
    assert not long_hold_rows["recommended"].any(), (
        f"Long-hold rows incorrectly recommended: "
        f"{long_hold_rows[['exit_method', 'avg_hold_days', 'recommended']]}"
    )


def test_recommended_rejects_low_fire_rate():
    """A row with actual_fire_rate < 0.5 must NOT be recommended."""
    trades = [_build_trade_setup(n_bars=400, slope=2.0) for _ in range(8)]
    summary, _ = run_exit_comparison("test_strategy", trades)
    low_fire = summary[summary["actual_fire_rate"] < CUBE_MIN_FIRE_RATE]
    if low_fire.empty:
        pytest.skip("Fixture didn't produce a low-fire-rate row")
    assert not low_fire["recommended"].any(), (
        f"Low-fire-rate rows incorrectly recommended: "
        f"{low_fire[['exit_method', 'actual_fire_rate', 'recommended']]}"
    )


def test_recommended_at_most_one_row():
    """At most one row per (strategy x set of exits) should be recommended."""
    trades = [_build_trade_setup() for _ in range(6)]
    summary, _ = run_exit_comparison("test_strategy", trades)
    assert summary["recommended"].sum() <= 1


def test_recommended_falls_back_to_next_best_qualifying_row():
    """If the top-composite row fails guardrails, recommended should fall
    to the next-best qualifying row (not just leave nothing recommended
    when a qualifying row exists)."""
    # trailing_pct family should fire reliably on an uptrend fixture.
    trades = [_build_trade_setup(n_bars=80, slope=0.5) for _ in range(8)]
    summary, _ = run_exit_comparison("test_strategy", trades)
    qualifying = summary[
        (summary["avg_hold_days"] <= CUBE_MAX_AVG_HOLD_DAYS)
        & (summary["actual_fire_rate"] >= CUBE_MIN_FIRE_RATE)
    ]
    if qualifying.empty:
        pytest.skip("Fixture didn't produce a qualifying row")
    assert summary["recommended"].sum() == 1, (
        "Expected exactly one recommended row when at least one qualifies"
    )
    recommended_row = summary[summary["recommended"]].iloc[0]
    assert recommended_row["avg_hold_days"] <= CUBE_MAX_AVG_HOLD_DAYS
    assert recommended_row["actual_fire_rate"] >= CUBE_MIN_FIRE_RATE
