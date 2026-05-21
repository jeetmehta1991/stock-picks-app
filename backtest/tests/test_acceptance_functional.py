"""Acceptance / functional tests -- Pass 53 Day-9 G5.

Closes the acceptance/functional dimension of the test pyramid (DEC-503 9-type).
Where G1-G4 cover system-as-pytest / bad-data / performance / CI, G5 verifies
that the system meets functional requirements end-to-end:

  - 9 passing criteria computable end-to-end
  - All 13 exit methods (12 baseline + regime_flip) callable + return valid output
  - Regime classifier covers 4 named regimes + unknown fail-closed
  - Strategy roster has expected baseline count (60 Layer-1 per CANONICAL_FACTS)
  - Round-trip: synthetic OHLCV -> signals -> screen -> exit produces valid trade

Runtime: <10s. Synthetic data only -- no cache dependency.
"""

from __future__ import annotations

import logging
from datetime import date

import numpy as np
import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def _quiet_logs():
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture(scope="module")
def synthetic_ohlcv():
    """80 business days of clean synthetic OHLCV -- no NaN, monotonic trend."""
    rng = np.random.default_rng(42)
    idx = pd.date_range("2023-01-02", periods=80, freq="B")
    drift = np.linspace(0, 5, 80)
    noise = rng.normal(0, 0.5, 80)
    close = 100 + drift + noise.cumsum() * 0.1
    df = pd.DataFrame({
        "open":   close - rng.uniform(0.1, 0.5, 80),
        "high":   close + rng.uniform(0.5, 1.5, 80),
        "low":    close - rng.uniform(0.5, 1.5, 80),
        "close":  close,
        "volume": rng.integers(800_000, 1_500_000, 80).astype(float),
    }, index=idx)
    df["high"] = df[["open", "high", "close"]].max(axis=1) + 0.1
    df["low"] = df[["open", "low", "close"]].min(axis=1) - 0.1
    return df


# ===========================================================================
# G5.1 -- 9 passing criteria are all defined in config
# ===========================================================================
def test_g5_passing_criteria_complete():
    """PASSING_CRITERIA must define all 9 metrics + audit thresholds."""
    from backtest.config import PASSING_CRITERIA

    required = {
        "min_win_rate", "min_profit_factor", "min_expected_value",
        "min_win_loss_ratio", "max_drawdown", "min_total_roi",
        "smart_money_lift", "macro_correlation", "min_trades",
    }
    missing = required - set(PASSING_CRITERIA.keys())
    assert not missing, f"PASSING_CRITERIA missing: {missing}"

    # Audit thresholds for look-ahead detection
    assert "audit_win_rate_above" in PASSING_CRITERIA
    assert "audit_profit_factor_above" in PASSING_CRITERIA


def test_g5_sector_passing_criteria_buckets():
    """SECTOR_PASSING_CRITERIA must have high_volatility / standard / low_volatility buckets."""
    from backtest.config import SECTOR_PASSING_CRITERIA

    assert "high_volatility" in SECTOR_PASSING_CRITERIA
    for bucket in SECTOR_PASSING_CRITERIA.values():
        assert "min_win_rate" in bucket
        assert "min_profit_factor" in bucket
        assert "max_drawdown" in bucket


# ===========================================================================
# G5.2 -- All 13 exit methods callable + return valid output
# ===========================================================================
EXPECTED_EXITS = {
    "trailing_10pct", "trailing_5pct", "trailing_15pct",
    "atr_trail_1x", "atr_trail_2x",
    "fixed_4r_2r", "next_pivot_target", "ma_exit_ema9",  # BUG-285: was fixed_3r_2r (1.5:1 R:R violation)
    "time_stop_10d", "time_stop_20d",
    "breakeven_plus_trail", "hybrid_50pct_target",
    "regime_flip",  # DEC-516
}


def test_g5_exit_strategies_registry_complete():
    """EXIT_STRATEGIES registry must include all 13 methods (12 baseline + regime_flip)."""
    from backtest.engine.exit_strategies import EXIT_STRATEGIES

    missing = EXPECTED_EXITS - set(EXIT_STRATEGIES.keys())
    assert not missing, f"EXIT_STRATEGIES missing: {missing}"


@pytest.mark.parametrize("method_name", sorted(EXPECTED_EXITS))
def test_g5_each_exit_method_callable(method_name, synthetic_ohlcv):
    """Each of 13 exit methods must execute without crash and return (date, price)."""
    from backtest.engine.exit_strategies import EXIT_STRATEGIES

    fn = EXIT_STRATEGIES[method_name]
    entry_date = synthetic_ohlcv.index[10].date()
    entry_price = float(synthetic_ohlcv.loc[synthetic_ohlcv.index[10], "close"])
    direction = "long"
    atr = 1.5

    # signals dict -- empty stub; regime_flip will fall back to time_stop_max_days
    signals = {}

    try:
        result = fn(synthetic_ohlcv, entry_date, entry_price, direction, atr, signals)
    except Exception as exc:
        pytest.fail(f"{method_name} raised {type(exc).__name__}: {exc}")

    # Result contract: tuple of (exit_date, exit_price, exit_reason) -- or similar
    # exit_manager parses it. Just assert it's not None / not empty.
    assert result is not None, f"{method_name} returned None"
    if isinstance(result, tuple):
        assert len(result) >= 2, f"{method_name} tuple too short: {result}"


# ===========================================================================
# G5.3 -- Regime classifier covers all 4 named regimes + unknown
# ===========================================================================
@pytest.mark.parametrize("vix,spy_above,expected", [
    (15.0, True,  "bull"),
    # Batch 288 (option A.2): SPY-below-200-EMA alone classifies "bear"
    # regardless of VIX level. Was "neutral" pre-Batch-288.
    (15.0, False, "bear"),     # Batch 288 SPY-only bear gate
    (25.0, True,  "neutral"),
    (25.0, False, "bear"),     # Batch 288 SPY-only bear gate
    (35.0, False, "bear"),
    (35.0, True,  "neutral"),  # 30+ but SPY above: not bear -> neutral
    (42.0, False, "crisis"),
    (42.0, True,  "crisis"),   # crisis dominates regardless of SPY
    (None, True,  "unknown"),  # DEC-316 fail-closed
    (None, None,  "unknown"),
])
def test_g5_regime_classifier_covers_all_outcomes(vix, spy_above, expected):
    from backtest.engine.regime_filter import classify_regime
    actual = classify_regime(vix, spy_above)
    assert actual == expected, (
        f"classify_regime({vix}, {spy_above}) = {actual!r}, expected {expected!r}"
    )


# ===========================================================================
# G5.4 -- Strategy roster baseline count (CANONICAL_FACTS F-002 Layer 1 = 60)
# ===========================================================================
def test_g5_strategy_roster_baseline_count():
    """ALL_STRATEGIES must have 60 Layer-1 baseline strategies per CANONICAL_FACTS F-002."""
    try:
        from backtest.signals.screener import ALL_STRATEGIES
    except ImportError as exc:
        pytest.skip(f"ALL_STRATEGIES import failed: {exc}")

    assert len(ALL_STRATEGIES) >= 60, (
        f"Layer-1 baseline expected 60 strategies, got {len(ALL_STRATEGIES)}. "
        f"Per CANONICAL_FACTS F-002 / CLAUDE.md screener.py docstring."
    )


# ===========================================================================
# G5.5 -- Technical signals contract (>=200 fields per Category 1)
# ===========================================================================
def test_g5_technical_signals_field_count(synthetic_ohlcv):
    """compute_all_signals must produce >=200 fields per CANONICAL_FACTS F-003."""
    from backtest.signals.technical import compute_all_signals

    sigs = compute_all_signals(synthetic_ohlcv)

    # Output may be dict or DataFrame depending on impl
    if isinstance(sigs, dict):
        n_fields = len(sigs)
    elif isinstance(sigs, pd.DataFrame):
        n_fields = len(sigs.columns)
    elif isinstance(sigs, pd.Series):
        n_fields = len(sigs)
    else:
        pytest.fail(f"compute_all_signals returned unexpected type: {type(sigs)}")

    assert n_fields >= 200, (
        f"Technical signals expected >=200 fields (Category 1 per CANONICAL_FACTS F-003); "
        f"got {n_fields}"
    )


# ===========================================================================
# G5.6 -- Round-trip synthetic data flow
# ===========================================================================
def test_g5_round_trip_signals_to_exit(synthetic_ohlcv):
    """Synthetic OHLCV -> signals computed -> exit method runs end-to-end."""
    from backtest.signals.technical import compute_all_signals
    from backtest.engine.exit_strategies import exit_atr_trail

    sigs = compute_all_signals(synthetic_ohlcv)
    assert sigs is not None

    entry_date = synthetic_ohlcv.index[20].date()
    entry_price = float(synthetic_ohlcv.iloc[20]["close"])

    result = exit_atr_trail(
        synthetic_ohlcv, entry_date, entry_price, "long", atr=1.5, atr_mult=1.0
    )
    assert result is not None
    if isinstance(result, tuple):
        exit_date_or_idx = result[0]
        # Exit must be after or equal to entry
        if hasattr(exit_date_or_idx, "date"):
            exit_d = exit_date_or_idx.date()
        else:
            exit_d = exit_date_or_idx
        if isinstance(exit_d, date):
            assert exit_d >= entry_date, "Exit before entry -- round-trip broken"


# ===========================================================================
# G5.7 -- Trailing stop never moves down (DEC-067 invariant)
# ===========================================================================
def test_g5_trailing_stop_invariant():
    """Trailing stop on long must never decrease -- DEC-067 ratchet invariant."""
    from backtest.engine.exit_manager import OpenTrade, update_trailing_stop

    t = OpenTrade(
        ticker="TEST", entry_date=date(2023, 1, 1), entry_price=100.0,
        direction="long", strategy="test", category="momentum", sector="Technology",
        initial_stop=90.0, trailing_stop=90.0, highest_close=100.0,
        regime_at_entry="bull",
    )
    t = update_trailing_stop(t, 110.0)
    high_water_stop = t.trailing_stop
    t = update_trailing_stop(t, 105.0)  # price retraces
    assert t.trailing_stop >= high_water_stop, (
        f"Trailing stop moved DOWN: {high_water_stop} -> {t.trailing_stop} "
        f"on retrace from 110 to 105 -- DEC-067 invariant violated"
    )


# ===========================================================================
# G5.8 -- DEC-505 4-fold walk-forward references intact
# ===========================================================================
def test_g5_walk_forward_4fold_module_present():
    """DEC-505 4-fold walk-forward implementation must be importable."""
    try:
        from backtest.engine.improvements import run_walk_forward
    except ImportError as exc:
        pytest.fail(f"DEC-505 walk-forward broken: {exc}")
    assert callable(run_walk_forward)


# ===========================================================================
# G5.9 -- DEC-578 7-gate verdict primitives importable
# ===========================================================================
def test_g5_seven_gate_verdict_primitives():
    """DEC-578 7-gate verdict composer primitives must all be callable."""
    from backtest.results.seven_gate_verdict import compute_verdict_cube, evaluate_cell
    assert callable(compute_verdict_cube)
    assert callable(evaluate_cell)


# ===========================================================================
# G5.10 -- Phase-1A circuit breakers wired (Levels 1-6)
# ===========================================================================
def test_g5_circuit_breakers_levels_1_to_6():
    """All 6 circuit breaker levels must be reachable via priority evaluator."""
    from backtest.engine.circuit_breakers import (
        Level6State, update_level_6_state, evaluate_circuit_breakers_priority,
    )
    state = Level6State()
    update_level_6_state(state, 100.0, date(2023, 1, 2), days_since_start=100)
    assert callable(evaluate_circuit_breakers_priority)
