"""Batch 582 (2026-06-04) -- fix `year_high` / `year_low` producer bug
that gated strat_52w_high_breakout to ~0 fires in R4 despite obvious
real-world breakouts (e.g. AMD breaking 52w high multiple times in
the backtest window).

Owner directive 2026-06-04 via Stage 4 audit of `52w_high_breakout`
QUIET status in STRATEGY_ROSTER.md:
  "This is logically a high incidence category. Why is this quiet.
   Some thing is seriously wrong. Lets start with this."

ROOT CAUSE: technical.py:1085 had
  year_high = df["high"].tail(252).max()
which INCLUDES today's intraday high. So `today_close >= year_high`
effectively required today_close == today_high == max-of-252d.
Extremely rare; explains R4 QUIET status.

FIX: exclude today's bar from the 252-day window:
  prior = df.iloc[:-1]
  year_high = prior["high"].tail(lookback).max()
Plus use strict `>` for break_* (per owner spec "Close > Highest High
(250 days)") rather than `>=`.

Pins:

  (1) year_high EXCLUDES today's bar (AMD-style scenario fires)
  (2) year_low EXCLUDES today's bar (mirror)
  (3) break_52w_high uses strict > comparison (close == year_high is
      NOT a break - it's a touch)
  (4) break_52w_low uses strict < comparison
  (5) near_52w_high still uses 98% threshold + >= (touching counts)
  (6) AMD-style scenario: close at 102 with prior_high=101 fires
      break_52w_high=True (was False with pre-B582 bug)
  (7) Edge case: close exactly equals prior_year_high -> break=False
      (strict greater than)
  (8) Edge case: short history (<= 1 bar) doesn't crash
  (9) Downstream: strat_52w_high_breakout fires on AMD-style scenario
      (was silent under pre-B582 bug)
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _build_df(closes, highs, lows, volumes=None):
    n = len(closes)
    if volumes is None:
        volumes = [1_000_000] * n
    return pd.DataFrame({
        "open":   closes,
        "high":   highs,
        "low":    lows,
        "close":  closes,
        "volume": volumes,
    }, index=pd.date_range("2024-01-01", periods=n))


def test_batch582_year_high_excludes_today():
    """Pin (1) + (6): AMD-style scenario - today close 102 breaks
    prior 252d high of 101."""
    from backtest.signals.technical import compute_volume as compute_indicators
    n = 252
    # First 251 bars: range 80-101 (prior high = 101)
    closes = list(np.linspace(80, 100, n - 1)) + [102.0]  # today close = 102
    highs  = list(np.linspace(81, 101, n - 1)) + [103.0]  # today intraday high = 103
    lows   = list(np.linspace(79,  99, n - 1)) + [101.0]
    df = _build_df(closes, highs, lows)
    out = compute_indicators(df)
    # year_high should be prior high = 101.0 (excludes today)
    assert out["year_high"] == 101.0, (
        f"year_high should exclude today's intraday high; got {out['year_high']}, "
        f"expected 101.0 (prior 251d max)"
    )
    # break_52w_high fires because 102 > 101 (close > prior year_high)
    assert out["break_52w_high"] == True, (
        f"break_52w_high should fire: today_close 102 > prior_year_high 101"
    )


def test_batch582_year_low_excludes_today():
    """Pin (2): mirror for year_low."""
    from backtest.signals.technical import compute_volume as compute_indicators
    n = 252
    closes = list(np.linspace(100, 80, n - 1)) + [78.0]  # today close = 78
    highs  = list(np.linspace(101, 81, n - 1)) + [79.0]
    lows   = list(np.linspace( 99, 79, n - 1)) + [77.0]
    df = _build_df(closes, highs, lows)
    out = compute_indicators(df)
    assert out["year_low"] == 79.0, (
        f"year_low should exclude today's intraday low; got {out['year_low']}, "
        f"expected 79.0"
    )
    assert out["break_52w_low"] == True


def test_batch582_break_52w_high_strict_gt():
    """Pin (3) + (7): close exactly equals prior year_high -> NOT a break."""
    from backtest.signals.technical import compute_volume as compute_indicators
    n = 252
    closes = list(np.linspace(80, 100, n - 1)) + [101.0]  # close EXACTLY at prior high
    highs  = list(np.linspace(81, 101, n - 1)) + [102.0]
    lows   = list(np.linspace(79,  99, n - 1)) + [100.0]
    df = _build_df(closes, highs, lows)
    out = compute_indicators(df)
    assert out["year_high"] == 101.0
    # Strict > -- equality is NOT a break, just a touch
    assert out["break_52w_high"] == False, (
        f"close == prior_year_high should NOT fire break_52w_high (strict >); "
        f"got {out['break_52w_high']}"
    )
    # But near_52w_high (>= 98%) should still fire (touching counts as near)
    assert out["near_52w_high"] == True


def test_batch582_break_52w_low_strict_lt():
    """Pin (4)."""
    from backtest.signals.technical import compute_volume as compute_indicators
    n = 252
    closes = list(np.linspace(100, 80, n - 1)) + [79.0]  # close = prior year_low
    highs  = list(np.linspace(101, 81, n - 1)) + [80.0]
    lows   = list(np.linspace( 99, 79, n - 1)) + [78.0]
    df = _build_df(closes, highs, lows)
    out = compute_indicators(df)
    assert out["year_low"] == 79.0
    # Strict <
    assert out["break_52w_low"] == False
    assert out["near_52w_low"] == True


def test_batch582_near_52w_high_threshold_98pct():
    """Pin (5): near = within 98pct of prior year_high; touching the
    high (==) is still 'near'."""
    from backtest.signals.technical import compute_volume as compute_indicators
    n = 252
    # close at 99 (98% of prior_high 101 = 98.98, so 99 > 98.98 -> near)
    closes = list(np.linspace(80, 100, n - 1)) + [99.0]
    highs  = list(np.linspace(81, 101, n - 1)) + [100.0]
    lows   = list(np.linspace(79,  99, n - 1)) + [98.0]
    df = _build_df(closes, highs, lows)
    out = compute_indicators(df)
    assert out["year_high"] == 101.0
    assert out["near_52w_high"] == True
    assert out["break_52w_high"] == False  # not over 101


def test_batch582_short_history_no_crash():
    """Pin (8): a 1-bar df shouldn't crash. compute_volume early-returns
    empty dict on insufficient history; absence of year_high in output
    is acceptable - the strategy will read it as falsy via dict.get()
    fallback."""
    from backtest.signals.technical import compute_volume as compute_indicators
    df = _build_df([100.0], [101.0], [99.0])
    out = compute_indicators(df)  # should not raise
    assert isinstance(out, dict)


def test_batch582_downstream_strat_52w_high_breakout_fires():
    """Pin (9): strat_52w_high_breakout fires given full post-B586
    confluence (break + vol >1.7x + sector outperforming SPY).
    B582 fixed the break_52w_high producer; B586 added sector filter."""
    from backtest.signals.screener import strat_52w_high_breakout
    # Inject the post-B586 signals (B586 added vol_spike_17x +
    # sector_outperforming_spy gates beyond B582 producer fix)
    s = {
        "break_52w_high": True,
        "vol_spike_17x": True,
        "sector_outperforming_spy": True,
        "year_high": 101.0,
    }
    out = strat_52w_high_breakout(s)
    assert out["fires"] == True
    assert out["direction"] == "long"


def test_batch582_amd_realistic_scenario_full_pipeline():
    """Pin (6) end-to-end: build a 252-day OHLCV simulating AMD breaking
    out, run compute_indicators, check that break_52w_high fires
    correctly (B582 producer fix verified).

    B586 update: strat_52w_high_breakout now ALSO requires
    vol_spike_17x + sector_outperforming_spy. This test verifies the
    PRODUCER (break_52w_high) is correct; the full strategy fires
    test was moved to B586 (which provides all required signals
    explicitly)."""
    from backtest.signals.technical import compute_volume as compute_indicators
    from backtest.signals.screener import strat_52w_high_breakout
    n = 252
    # 251 prior bars in 100-120 range, today close breaks to 125
    closes = list(np.linspace(100, 120, n - 1)) + [125.0]
    highs  = list(np.linspace(101, 121, n - 1)) + [126.0]
    lows   = list(np.linspace( 99, 119, n - 1)) + [124.0]
    # Volume spike on breakout day (3x to ensure ratio > 1.7)
    volumes = [1_000_000] * (n - 1) + [3_000_000]
    df = _build_df(closes, highs, lows, volumes)
    out = compute_indicators(df)
    assert out["break_52w_high"] == True, (
        f"AMD-style breakout should fire break_52w_high; close=125 vs "
        f"year_high={out['year_high']}"
    )
    # B586: strategy now ALSO requires sector_outperforming_spy.
    # Inject the post-B586 signals explicitly to verify the strategy
    # fires end-to-end given full confluence.
    s = dict(out)
    s["sector_outperforming_spy"] = True  # post-B586 producer (sector_strength.py)
    s_result = strat_52w_high_breakout(s)
    assert s_result["fires"] == True, (
        f"strat_52w_high_breakout should fire on AMD-style breakout + vol_spike_2x; "
        f"vol_ratio={out.get('vol_ratio_20d')}"
    )
