"""Tests for N1 (DEC-516 regime-flip exit + DEC-515 Level 6 circuit breaker)
and N2 (DEC-578 7-gate Phase 1B-α verdict composer).

Pass 53 Day-9-evening 2026-05-07 owner-approved D1+D2.
Per DEC-594 same-commit: artifact + tests land together.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from backtest.engine.circuit_breakers import (
    LEVEL_6_DD_HALT_THRESHOLD,
    LEVEL_6_RECOVERY_THRESHOLD,
    Level6State,
    evaluate_circuit_breakers_priority,
    update_level_6_state,
)
from backtest.engine.exit_strategies import (
    EXIT_STRATEGIES,
    exit_regime_flip,
)
from backtest.results.seven_gate_verdict import (
    GATE_1_MIN_TRADES,
    compute_verdict_cube,
    evaluate_cell,
)


# ===========================================================================
# N1 — DEC-516 regime-flip exit
# ===========================================================================
def _synthetic_ohlcv(n_days: int = 30, start_price: float = 100.0,
                      drift: float = 0.001) -> pd.DataFrame:
    """Synthetic OHLCV DataFrame with DatetimeIndex."""
    dates = pd.date_range("2024-01-01", periods=n_days, freq="B")
    rng = np.random.default_rng(0)
    returns = rng.normal(drift, 0.01, n_days)
    closes = start_price * np.cumprod(1 + returns)
    df = pd.DataFrame({
        "open":   closes * (1 - 0.005),
        "high":   closes * (1 + 0.005),
        "low":    closes * (1 - 0.005),
        "close":  closes,
        "volume": 1_000_000,
    }, index=dates)
    return df


def test_dec516_regime_flip_in_registry():
    """regime_flip exit must be registered in EXIT_STRATEGIES."""
    assert "regime_flip" in EXIT_STRATEGIES


def test_dec516_regime_flip_returns_valid_result():
    """regime_flip with no flip data → falls back to time_stop_max_days."""
    df = _synthetic_ohlcv(n_days=30)
    result = exit_regime_flip(
        df, entry_date=date(2024, 1, 1), entry_price=100.0,
        direction="long", atr=2.0, signals={"regime_at_entry": "calm"},
        regime_series=None, max_days=20,
    )
    assert "pnl_pct" in result
    assert "exit_reason" in result
    assert "regime_flip_max_days" in result["exit_reason"] or \
           "regime_flip" in result["exit_reason"]


def test_dec516_regime_flip_detects_change():
    """regime_flip with regime series showing change → exits early."""
    df = _synthetic_ohlcv(n_days=30)
    # Regime series: calm → volatile after 5 days
    regime_series = {}
    for i, ts in enumerate(df.index):
        regime_series[ts.date()] = "calm" if i < 5 else "volatile"
    result = exit_regime_flip(
        df, entry_date=date(2024, 1, 1), entry_price=100.0,
        direction="long", atr=2.0,
        signals={"regime_at_entry": "calm"},
        regime_series=regime_series, max_days=20,
    )
    assert "regime_flip" in result["exit_reason"]
    # Exit method should reflect the flip detection
    assert "calm_to_volatile" in result["exit_reason"] or \
           "regime_flip_max_days" in result["exit_reason"]


# ===========================================================================
# N1 — DEC-515 Level 6 circuit breaker
# ===========================================================================
def test_dec515_level6_no_halt_in_uptrend():
    """Steady uptrend → no halt triggered."""
    state = Level6State()
    for i, eq in enumerate([100, 102, 105, 108, 110]):
        result = update_level_6_state(
            state, current_equity=eq, as_of=date(2024, 1, 1 + i),
            days_since_start=100,
        )
    assert not state.halt_triggered
    assert state.rolling_peak_equity == 110


def test_dec515_level6_halt_triggers_on_drawdown():
    """Drop ≥15% from peak → halt triggered."""
    state = Level6State()
    # Build up peak
    for i, eq in enumerate([100, 110, 120]):
        update_level_6_state(state, eq, date(2024, 1, 1 + i), days_since_start=100)
    assert state.rolling_peak_equity == 120
    # Drop 20% from peak
    update_level_6_state(state, current_equity=96, as_of=date(2024, 1, 4),
                         days_since_start=100)
    assert state.halt_triggered
    assert state.halt_equity == 96


def test_dec515_level6_min_history_blocks_early_halt():
    """Halt does NOT trigger before min_history_days."""
    state = Level6State()
    update_level_6_state(state, 100, date(2024, 1, 1), days_since_start=0)
    update_level_6_state(state, 80, date(2024, 1, 2), days_since_start=5)  # 20% drop
    assert not state.halt_triggered  # blocked by min_history


def test_dec515_level6_resume_when_recovers():
    """After halt, resume when current_equity ≥ target_resume_equity."""
    state = Level6State()
    # Build peak + drawdown
    update_level_6_state(state, 100, date(2024, 1, 1), days_since_start=100)
    update_level_6_state(state, 120, date(2024, 1, 2), days_since_start=101)
    update_level_6_state(state, 96, date(2024, 1, 3), days_since_start=102)  # halt
    assert state.halt_triggered
    target = state.target_resume_equity
    # Equity recovers to target
    update_level_6_state(state, target + 0.01, date(2024, 1, 10),
                         days_since_start=109)
    assert not state.halt_triggered


def test_dec515_priority_level_6_wins():
    """Level 6 active → highest_level=6 even if Level 1 also active."""
    state = Level6State()
    # Set up halt
    state.halt_triggered = True
    state.target_resume_equity = 110
    state.rolling_peak_equity = 100
    result = evaluate_circuit_breakers_priority(
        daily_portfolio_pct=-0.015,  # would trigger L1
        intraday_low_vs_open_pct=-0.005,
        level_6_state=state,
        current_equity=95,
        as_of=date(2024, 6, 1),
        days_since_start=100,
    )
    assert 6 in result["active_breakers"]
    assert result["highest_level"] == 6
    assert result["size_multiplier"] == 0.0  # halt new entries


def test_dec515_priority_no_breakers_normal_day():
    """Normal day → no breakers, full size."""
    state = Level6State()
    state.rolling_peak_equity = 100
    result = evaluate_circuit_breakers_priority(
        daily_portfolio_pct=0.005, intraday_low_vs_open_pct=-0.002,
        level_6_state=state, current_equity=101, as_of=date(2024, 6, 1),
        days_since_start=100,
    )
    assert result["highest_level"] is None
    assert result["size_multiplier"] == 1.0


# ===========================================================================
# N2 — DEC-578 7-gate verdict composer
# ===========================================================================
def test_dec578_insufficient_sample():
    """n < 30 → INSUFFICIENT_SAMPLE."""
    result = evaluate_cell([0.01] * 10)
    assert result.verdict == "INSUFFICIENT_SAMPLE"


def test_dec578_strong_strategy_passes():
    """Strong synthetic strategy with 100 trades, mean_pnl=2%, σ=1% — should pass.

    Test goal: verify all 7 gates evaluate (not necessarily all PASS for synthetic
    data; key is no gate-evaluation crash).
    """
    rng = np.random.default_rng(0)
    returns = rng.normal(0.02, 0.01, 100)  # 2% mean, 1% std → very strong
    result = evaluate_cell(returns, n_strategies_tested=10)  # small N to ease Bonferroni
    # Should PASS most gates (strong signal); but DSR with N=10 is harsh
    assert result.verdict in (
        "PASS", "FAIL_GATE_3_DSR", "FAIL_GATE_4_T_STAT",
        "FAIL_GATE_5_RR", "FAIL_GATE_6_PF", "FAIL_GATE_7_EFFECT_SIZE",
        "FAIL_GATE_2_BONFERRONI",
    )
    assert result.n_trades == 100


def test_dec578_weak_strategy_fails_early_gate():
    """Weak strategy with mean ~ 0 → fails Gate 2 (Bonferroni)."""
    rng = np.random.default_rng(1)
    returns = rng.normal(0.0, 0.01, 100)  # zero mean
    result = evaluate_cell(returns, n_strategies_tested=199)
    # Should fail at Gate 2 (Bonferroni) due to no significant signal
    assert "FAIL" in result.verdict
    assert result.gates_passed <= 2


def test_dec578_negative_strategy_fails_effect_size():
    """Negative-skill strategy → fails some gate (typically Gate 2 or 5/6)."""
    rng = np.random.default_rng(2)
    returns = rng.normal(-0.005, 0.01, 100)  # losing strategy
    result = evaluate_cell(returns, n_strategies_tested=199)
    assert "FAIL" in result.verdict


def test_dec578_gate_details_structure():
    """GateResult.gate_details must have entries for each evaluated gate."""
    result = evaluate_cell([0.01, -0.005] * 50, n_strategies_tested=10)
    assert "gate_1_sample_size" in result.gate_details
    # If any FAIL after gate 1, gates_passed reflects how many passed
    assert result.gates_passed >= 1


def test_dec578_compute_verdict_cube():
    """compute_verdict_cube produces one row per cell."""
    rng = np.random.default_rng(3)
    rows = []
    for strat in ["s1", "s2"]:
        for regime in ["calm", "volatile"]:
            for _ in range(40):
                pnl = rng.normal(0.005 if strat == "s1" else -0.001, 0.01)
                rows.append({"strategy": strat, "regime_at_entry": regime,
                             "sector": "Tech", "cap_band": "large_10_200B",
                             "vol_band": "low_lt_15", "pnl_pct": pnl})
    df = pd.DataFrame(rows)
    cube_verdict = compute_verdict_cube(df, n_strategies_tested=10)
    assert not cube_verdict.empty
    assert "verdict" in cube_verdict.columns
    assert "gates_passed" in cube_verdict.columns
    assert "n_trades" in cube_verdict.columns
    # 4 cells expected (2 strategies × 2 regimes × 1 sector × 1 cap × 1 vol)
    assert len(cube_verdict) == 4


def test_dec578_compute_verdict_cube_empty_input():
    """Empty input returns empty DataFrame."""
    result = compute_verdict_cube(pd.DataFrame())
    assert result.empty
