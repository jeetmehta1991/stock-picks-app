"""Batch 573 (2026-06-04) -- Loosen near() tolerance 0.3pct/0.5pct -> 1.5pct
per Stage 4 Class 2 ENTRY_GATE_LOOSEN owner directive 2026-06-04:
"I think the criteria needs to be broadened to 1.5pct vs 1pct currently
for doji". Owner chose 1.5pct from the B571 Class 2 sweep grid
[0.5, 1.0, 1.5, 2.0pct].

Affects 14 strategies that consume the near_s/near_r/at_key_fib flags:
  bullish_engulfing_support, camarilla_rsi_obv,
  camarilla_rsi_obv_short, camarilla_s3_bounce,
  doji_at_resistance_short, doji_at_support, mfi_oversold,
  pivot_fib_confluence, pivot_s1_bounce, pivot_s2_bounce,
  pivot_s3_capitulation, prev_day_low_bounce, shooting_star_short,
  williams_stoch_dual

Pins:

  (1) Pivot near() tolerance is now 0.015 (not 0.003)
  (2) Fib near() tolerance is now 0.015 (not 0.005)
  (3) At 1.0pct away from S1, near_s1 = True (was False at 0.3pct
      tolerance - widened band catches it)
  (4) At 0.2pct away from S1, near_s1 = True (was True at 0.3pct -
      no regression for very-close prices)
  (5) At 1.6pct away from S1, near_s1 = False (outside the new band -
      tolerance is not unbounded)
  (6) doji_at_support fires on the same wider band (downstream effect)
  (7) doji_at_resistance_short fires on the same wider band
"""
from __future__ import annotations

import pandas as pd
import numpy as np


def _mk_ohlcv(today_close, prev_high=100, prev_low=95, prev_close=98,
              prev_open=97):
    """Build a 2-bar OHLCV df where today closes at `today_close` and
    yesterday provides the pivot inputs."""
    dates = pd.date_range("2024-01-01", periods=2)
    df = pd.DataFrame({
        "open":  [prev_open, today_close - 0.1],
        "high":  [prev_high, today_close + 0.1],
        "low":   [prev_low,  today_close - 0.1],
        "close": [prev_close, today_close],
        "volume": [1_000_000, 1_000_000],
    }, index=dates)
    return df


def test_batch573_pivot_near_tolerance_is_1_5pct():
    """Pin (1) + (3) + (4) + (5)."""
    from backtest.signals.technical import compute_pivots
    # Standard pivot: P = (H+L+C)/3 = (100+95+98)/3 = 97.667
    # S1 = 2P - H = 95.334
    s1 = 2 * (100 + 95 + 98) / 3 - 100
    # 1.0pct away from S1: should fire near_s1 (within 1.5pct band)
    df = _mk_ohlcv(today_close=s1 * 1.010)
    p = compute_pivots(df)
    assert p["near_s1"] == True, (
        f"Pin (3): close at S1+1.0pct ({s1*1.010:.3f} vs S1={s1:.3f}) "
        f"should be near_s1 under 1.5pct tolerance"
    )
    # 0.2pct away: still fires (no regression)
    df = _mk_ohlcv(today_close=s1 * 1.002)
    p = compute_pivots(df)
    assert p["near_s1"] == True, "Pin (4): close at S1+0.2pct still near"
    # 1.6pct away: must NOT fire (outside band)
    df = _mk_ohlcv(today_close=s1 * 1.016)
    p = compute_pivots(df)
    assert p["near_s1"] == False, (
        f"Pin (5): close at S1+1.6pct should NOT be near_s1 - tolerance "
        f"is bounded at 1.5pct"
    )


def test_batch573_fib_near_tolerance_is_1_5pct():
    """Pin (2): Fib near() also at 1.5pct."""
    from backtest.signals.technical import compute_fibonacci
    # Build a 50-bar OHLCV with a clear swing (sh - sl)
    n = 50
    dates = pd.date_range("2024-01-01", periods=n)
    highs = np.linspace(50, 110, n)
    lows  = np.linspace(40, 100, n)
    closes = (highs + lows) / 2
    df = pd.DataFrame({
        "open":  closes, "high": highs, "low": lows, "close": closes,
        "volume": [1_000_000] * n,
    }, index=dates)
    sh, sl = highs.max(), lows.min()
    # fib_500 = (sh + sl) / 2 = (110 + 40) / 2 = 75
    fib_500 = sh - 0.500 * (sh - sl)
    # Adjust today's close to be 1.0pct away from fib_500
    df.iloc[-1, df.columns.get_loc("close")] = fib_500 * 1.010
    fb = compute_fibonacci(df)
    assert fb["near_fib_500"] == True, (
        f"close at fib_500+1.0pct should be near_fib_500 under 1.5pct"
    )
    # 1.6pct away: not near
    df.iloc[-1, df.columns.get_loc("close")] = fib_500 * 1.016
    fb = compute_fibonacci(df)
    assert fb["near_fib_500"] == False


def test_batch573_doji_at_support_downstream():
    """Pin (6): doji_at_support fires when a synthetic signal dict
    shows near_s1=True (the widened band would produce this). No
    regression on the strategy's predicate logic."""
    from backtest.signals.screener import strat_doji_at_support
    s = {"doji": True, "near_s1": True, "vol_spike_15x": True}
    out = strat_doji_at_support(s)
    assert out["fires"] == True


def test_batch573_doji_at_resistance_downstream():
    """Pin (7): inverse strategy from B572 still fires correctly with
    the wider tolerance feeding near_r1."""
    from backtest.signals.screener import strat_doji_at_resistance_short
    s = {"doji": True, "near_r1": True, "vol_spike_15x": True}
    out = strat_doji_at_resistance_short(s)
    assert out["fires"] == True


def test_batch573_near_constant_is_0_015_in_source():
    """Pin (1) + (2) source-level check: technical.py contains the
    0.015 literal (not 0.003 / 0.005). Regression guard against
    accidental revert."""
    from pathlib import Path
    src = (Path(__file__).resolve().parents[2]
           / "backtest" / "signals" / "technical.py"
           ).read_text(encoding="utf-8")
    # Two near() definitions, both at 0.015
    assert src.count("< 0.015") >= 2, (
        f"expected at least 2 occurrences of '< 0.015' in technical.py; "
        f"got {src.count('< 0.015')}"
    )
    # Old constants must NOT be present anymore in active near() lines
    # (they may appear elsewhere if 0.003/0.005 is used for other math)
    # Check that the specific patterns 'lvl) < 0.003' / 'lvl) < 0.005'
    # are absent (these were the near() lambda bodies)
    assert "lvl) < 0.003" not in src, (
        "stale 0.003 near() tolerance still present in technical.py"
    )
    assert "lvl) < 0.005" not in src, (
        "stale 0.005 near() tolerance still present in technical.py"
    )
