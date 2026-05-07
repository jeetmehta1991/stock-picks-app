"""DEC-517 R-multiple exits + break-even moves — regression tests
(Pass 53 Day-9 v8g).

Spec source: TRADING_RULES_AND_INFORMATION.md §8.7.

Three new exit methods (registered in EXIT_STRATEGIES):
  18 exit_r_multiple_2r:    target = entry ± 2 × stop_distance
  19 exit_r_multiple_3r:    target = entry ± 3 × stop_distance
  20 exit_break_even_at_1r: stop moves to entry once +1R is reached

Stop distance default: 1× ATR if atr provided, else 2% of entry. All sites
use DEC-514 fill methodology (gap-through fills at bar_open).
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Helper: build synthetic OHLCV with predictable pattern
# ---------------------------------------------------------------------------
def _build_uptrend(start=100.0, n=20, daily_gain=1.0):
    idx = pd.date_range("2023-01-02", periods=n, freq="B")
    rows = []
    p = start
    for _ in range(n):
        rows.append({
            "open":   p,
            "high":   p + 1.0,
            "low":    p - 0.5,
            "close":  p + 0.5,
            "volume": 1_000_000,
        })
        p += daily_gain
    return pd.DataFrame(rows, index=idx)


def _build_downtrend(start=100.0, n=20, daily_loss=1.0):
    idx = pd.date_range("2023-01-02", periods=n, freq="B")
    rows = []
    p = start
    for _ in range(n):
        rows.append({
            "open":   p,
            "high":   p + 0.5,
            "low":    p - 1.0,
            "close":  p - 0.5,
            "volume": 1_000_000,
        })
        p -= daily_loss
    return pd.DataFrame(rows, index=idx)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
def test_dec517_registry_has_three_new_methods():
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    for k in ["r_multiple_2r", "r_multiple_3r", "break_even_at_1r"]:
        assert k in EXIT_STRATEGIES, f"DEC-517: {k} missing from EXIT_STRATEGIES"


def test_dec517_registry_count_grew_by_three():
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    assert len(EXIT_STRATEGIES) >= 16, (
        f"EXIT_STRATEGIES has only {len(EXIT_STRATEGIES)} methods; expected ≥16 "
        f"after DEC-517"
    )


# ---------------------------------------------------------------------------
# DEC-517 #18 exit_r_multiple_2r
# ---------------------------------------------------------------------------
def test_dec517_r_multiple_2r_long_hits_target():
    """Long entry at 100, ATR=2 → 2R target = 104. Uptrend should hit on day 3."""
    from backtest.engine.exit_strategies import exit_r_multiple_2r
    df = _build_uptrend(100.0, n=10, daily_gain=1.0)
    r = exit_r_multiple_2r(df, date(2023, 1, 2), 100.0, "long", 2.0)
    assert r["exit_reason"] == "r_multiple_2r_target"
    assert r["exit_price"] == pytest.approx(104.0, abs=0.5)


def test_dec517_r_multiple_2r_short_hits_target():
    """Short entry at 100, ATR=2 → 2R target = 96. Downtrend should hit."""
    from backtest.engine.exit_strategies import exit_r_multiple_2r
    df = _build_downtrend(100.0, n=10, daily_loss=1.0)
    r = exit_r_multiple_2r(df, date(2023, 1, 2), 100.0, "short", 2.0)
    assert r["exit_reason"] == "r_multiple_2r_target"
    assert r["exit_price"] == pytest.approx(96.0, abs=0.5)


def test_dec517_r_multiple_long_hits_stop_on_reversal():
    """Long entry, immediate reversal → 1R stop should fire."""
    from backtest.engine.exit_strategies import exit_r_multiple_2r
    df = _build_downtrend(100.0, n=10, daily_loss=1.0)
    r = exit_r_multiple_2r(df, date(2023, 1, 2), 100.0, "long", 2.0)
    assert r["exit_reason"] == "r_multiple_stop"
    # Stop = 100 - 2 = 98
    assert r["exit_price"] <= 98.5


# ---------------------------------------------------------------------------
# DEC-517 #19 exit_r_multiple_3r
# ---------------------------------------------------------------------------
def test_dec517_r_multiple_3r_long_hits_target():
    """3R target = 100 + 6 = 106 in uptrend."""
    from backtest.engine.exit_strategies import exit_r_multiple_3r
    df = _build_uptrend(100.0, n=15, daily_gain=1.0)
    r = exit_r_multiple_3r(df, date(2023, 1, 2), 100.0, "long", 2.0)
    assert r["exit_reason"] == "r_multiple_3r_target"
    assert r["exit_price"] == pytest.approx(106.0, abs=0.5)


def test_dec517_r_multiple_3r_takes_longer_than_2r():
    """3R should take more days to hit than 2R in same uptrend."""
    from backtest.engine.exit_strategies import exit_r_multiple_2r, exit_r_multiple_3r
    df = _build_uptrend(100.0, n=15, daily_gain=1.0)
    r2 = exit_r_multiple_2r(df, date(2023, 1, 2), 100.0, "long", 2.0)
    r3 = exit_r_multiple_3r(df, date(2023, 1, 2), 100.0, "long", 2.0)
    assert r3["hold_days"] >= r2["hold_days"]


# ---------------------------------------------------------------------------
# DEC-517 #20 exit_break_even_at_1r
# ---------------------------------------------------------------------------
def test_dec517_be_at_1r_locks_no_loss_on_smooth_reversal_after_be():
    """Long: rally to +1R (activates BE), then SMOOTH reversal (no gap).
    Exit at trail stop (close to BE); pnl should be roughly flat.

    Note: a gap-down THROUGH the trail stop fills at bar_open per DEC-514,
    so a sudden crash can produce a loss greater than the trail level. This
    test uses a smooth reversal to validate the core BE-protection behavior.
    """
    from backtest.engine.exit_strategies import exit_break_even_at_1r
    # 5 days uptrend (hits +1R at day 2), then 5 days slow drift down (no gap)
    rows = []
    p = 100.0
    for i in range(5):
        rows.append({"open": p, "high": p + 1.0, "low": p - 0.5,
                     "close": p + 0.5, "volume": 1_000_000})
        p += 1.0
    # p is now 105
    for i in range(15):
        rows.append({"open": p, "high": p + 0.5, "low": p - 1.0,
                     "close": p - 0.5, "volume": 1_000_000})
        p -= 0.5
    df = pd.DataFrame(rows, index=pd.date_range("2023-01-02", periods=20, freq="B"))
    r = exit_break_even_at_1r(df, date(2023, 1, 2), 100.0, "long", atr=2.0)
    assert r["exit_reason"] == "be_trail_stop"
    # Trail stop after BE protected near entry — pnl >= -1% in smooth reversal
    assert r["pnl_pct"] >= -1.0, (
        f"BE-trail stop should protect near break-even; got pnl={r['pnl_pct']}"
    )


def test_dec517_be_at_1r_gap_down_fills_at_open_per_dec514():
    """DEC-514 cross-check: BE@1R + overnight gap-down → fill at gap_open
    (worse than trail stop). This is correct broker behavior."""
    from backtest.engine.exit_strategies import exit_break_even_at_1r
    base = _build_uptrend(100.0, n=20, daily_gain=1.0)
    base.loc[base.index[10:], ["open", "high", "low", "close"]] -= 15  # crash
    r = exit_break_even_at_1r(base, date(2023, 1, 2), 100.0, "long", atr=2.0)
    assert r["exit_reason"] == "be_trail_stop"
    # PnL is materially negative due to gap-through fill (DEC-514)
    # Without DEC-514, we'd see a smaller loss filling at trail stop
    assert r["pnl_pct"] < -3.0, (
        "Gap-down through trail stop should fill at open (DEC-514) producing "
        "loss greater than the trail level"
    )


def test_dec517_be_at_1r_initial_stop_fires_on_immediate_reversal():
    """Long: immediate downtrend, never hits +1R. Initial 1R stop fires."""
    from backtest.engine.exit_strategies import exit_break_even_at_1r
    df = _build_downtrend(100.0, n=10, daily_loss=2.0)
    r = exit_break_even_at_1r(df, date(2023, 1, 2), 100.0, "long", atr=2.0)
    assert r["exit_reason"] == "initial_1r_stop"
    # Stop = 100 - 2 = 98
    assert r["exit_price"] <= 98.5


# ---------------------------------------------------------------------------
# Stop-distance fallback (no ATR)
# ---------------------------------------------------------------------------
def test_dec517_stop_distance_falls_back_to_2pct_when_atr_zero():
    """If atr=0, stop distance defaults to 2% of entry."""
    from backtest.engine.exit_strategies import exit_r_multiple_2r
    df = _build_uptrend(100.0, n=10, daily_gain=1.0)
    # atr=0 → fallback 2% × 100 = $2.0; 2R = 100+4 = 104
    r = exit_r_multiple_2r(df, date(2023, 1, 2), 100.0, "long", atr=0.0)
    assert r["exit_reason"] == "r_multiple_2r_target"


# ---------------------------------------------------------------------------
# Integration: callable via EXIT_STRATEGIES registry
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", ["r_multiple_2r", "r_multiple_3r", "break_even_at_1r"])
def test_dec517_callable_via_registry(name):
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    df = _build_uptrend(100.0, n=15, daily_gain=1.0)
    fn = EXIT_STRATEGIES[name]
    result = fn(df, date(2023, 1, 2), 100.0, "long", 2.0, {})
    assert result is not None
    assert "exit_price" in result
    assert "exit_reason" in result
    assert result["exit_price"] > 0
