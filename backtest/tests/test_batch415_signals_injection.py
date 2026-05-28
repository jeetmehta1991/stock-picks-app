"""Batch 415 (2026-05-28 owner-approved): regression test for the
signals-dict enrichment in run_exit_comparison.

Before Batch 415, run_exit_comparison passed t.get("signals", {}) directly
to each exit_fn. The trade dict (from _pool_cube_replay_worker) did NOT
include ticker / strategy_name / category in its signals dict, so:
  - exit_earnings_blackout extracted ticker="" via lambda
    `(s or {}).get("ticker", "")`, called fetch_earnings_dates(""), got [],
    returned no_earnings_known for 100% of trades.
  - exit_class_time_stop extracted category="momentum" default for ALL
    strategies regardless of actual layer.
  - These showed up as fire_rate=0.000 cells in the post-cube optimizer
    output, silently failing the Stage 4 review (Batch 414 dropped 12 of
    22 candidate STRATEGY_EXIT_OVERRIDE entries because of this).

This batch fixes the gap. Tests assert that the enriched signals dict
arrives at each exit_fn with ticker, strategy_name, and category set.
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from backtest.engine.exit_strategies import run_exit_comparison


# Capture what the exit_fn receives via a spy lambda
class _SignalsSpy:
    def __init__(self):
        self.captured = []

    def __call__(self, df, entry_date, entry_price, direction, atr, signals):
        # Capture the signals dict for assertion later
        self.captured.append(dict(signals))
        # Return a valid _base_result-shaped dict
        return {
            "exit_price":  entry_price,
            "exit_date":   df.index[-1].date(),
            "exit_reason": "test_spy",
            "pnl_pct":     0.0,
            "win":         False,
            "hold_days":   1,
        }


def _make_synth_df(n_bars=10, base=100.0):
    closes = np.array([base + i * 0.1 for i in range(n_bars)])
    opens  = closes.copy()
    highs  = closes + 0.5
    lows   = closes - 0.5
    idx = pd.bdate_range(start="2024-01-02", periods=n_bars)
    return pd.DataFrame({
        "open":   opens, "high": highs, "low": lows,
        "close":  closes, "volume": [1_000_000] * n_bars,
    }, index=idx)


def _patch_one_exit_strategy(monkeypatch, name, spy):
    """Replace one entry of EXIT_STRATEGIES with the spy callable so we can
    capture what the cube-replay loop hands the exit_fn."""
    from backtest.engine import exit_strategies as mod
    new_dict = dict(mod.EXIT_STRATEGIES)
    new_dict[name] = lambda df, ed, ep, d, a, s: spy(df, ed, ep, d, a, s)
    monkeypatch.setattr(mod, "EXIT_STRATEGIES", new_dict)


def test_batch415_signals_dict_carries_ticker(monkeypatch):
    """Cube-replay must inject ticker into the signals dict reaching exit_fn."""
    spy = _SignalsSpy()
    _patch_one_exit_strategy(monkeypatch, "atr_trail_1x", spy)

    df = _make_synth_df()
    trades = [{
        "df":          df,
        "ticker":      "AAPL",
        "entry_date":  date(2024, 1, 2),
        "entry_price": 100.0,
        "direction":   "long",
        "atr":         1.0,
        "signals":     {"some_signal_key": True},
        "category":    "momentum",
    } for _ in range(6)]  # >=5 trades so run_exit_comparison emits the row

    run_exit_comparison("test_strategy_x", trades)

    assert len(spy.captured) >= 6, (
        f"spy was called {len(spy.captured)} times; expected >=6")
    for capt in spy.captured:
        assert capt.get("ticker") == "AAPL", (
            f"signals dict missing ticker; got {capt!r}")


def test_batch415_signals_dict_carries_strategy_name(monkeypatch):
    """Cube-replay must inject strategy_name into the signals dict."""
    spy = _SignalsSpy()
    _patch_one_exit_strategy(monkeypatch, "atr_trail_1x", spy)

    df = _make_synth_df()
    trades = [{
        "df":          df,
        "ticker":      "MSFT",
        "entry_date":  date(2024, 1, 2),
        "entry_price": 100.0,
        "direction":   "long",
        "atr":         1.0,
        "signals":     {},
        "category":    "trend",
    } for _ in range(6)]

    run_exit_comparison("ichimoku_tk_cross", trades)

    for capt in spy.captured:
        assert capt.get("strategy_name") == "ichimoku_tk_cross", (
            f"signals dict missing strategy_name; got {capt!r}")


def test_batch415_signals_dict_carries_category(monkeypatch):
    """Cube-replay must inject category (from trade dict OR signals dict
    OR 'momentum' fallback) into the signals dict."""
    spy = _SignalsSpy()
    _patch_one_exit_strategy(monkeypatch, "atr_trail_1x", spy)

    df = _make_synth_df()
    trades_explicit_category = [{
        "df":          df,
        "ticker":      "TSLA",
        "entry_date":  date(2024, 1, 2),
        "entry_price": 100.0,
        "direction":   "long",
        "atr":         1.0,
        "signals":     {},
        "category":    "mean_reversion",
    } for _ in range(6)]

    run_exit_comparison("rsi_oversold", trades_explicit_category)
    for capt in spy.captured:
        assert capt.get("category") == "mean_reversion", (
            f"signals dict missing category='mean_reversion'; got {capt!r}")


def test_batch415_signals_dict_category_fallback_to_momentum(monkeypatch):
    """If neither trade-dict nor signals-dict has category, falls back to
    'momentum' (matches scalar exit_class_time_stop's default)."""
    spy = _SignalsSpy()
    _patch_one_exit_strategy(monkeypatch, "atr_trail_1x", spy)

    df = _make_synth_df()
    trades_no_category = [{
        "df":          df,
        "ticker":      "NVDA",
        "entry_date":  date(2024, 1, 2),
        "entry_price": 100.0,
        "direction":   "long",
        "atr":         1.0,
        "signals":     {},
        # NO "category" key
    } for _ in range(6)]

    run_exit_comparison("some_unknown_strategy", trades_no_category)
    for capt in spy.captured:
        assert capt.get("category") == "momentum", (
            f"signals dict category fallback wrong; got {capt!r}")


def test_batch415_pre_existing_signals_preserved(monkeypatch):
    """Enrichment must not clobber pre-existing keys in the trade's
    signals dict (e.g., r1 / pivot levels used by next_pivot_target)."""
    spy = _SignalsSpy()
    _patch_one_exit_strategy(monkeypatch, "atr_trail_1x", spy)

    df = _make_synth_df()
    trades = [{
        "df":          df,
        "ticker":      "AMD",
        "entry_date":  date(2024, 1, 2),
        "entry_price": 100.0,
        "direction":   "long",
        "atr":         1.0,
        "signals":     {
            "r1":       105.0,
            "r2":       110.0,
            "s1":        95.0,
            "vix_band_low": True,
        },
        "category":    "breakout",
    } for _ in range(6)]

    run_exit_comparison("pivot_r1_breakout", trades)
    for capt in spy.captured:
        # New enrichment keys present
        assert capt.get("ticker") == "AMD"
        assert capt.get("strategy_name") == "pivot_r1_breakout"
        assert capt.get("category") == "breakout"
        # Pre-existing keys preserved
        assert capt.get("r1") == 105.0
        assert capt.get("r2") == 110.0
        assert capt.get("s1") == 95.0
        assert capt.get("vix_band_low") is True
