"""Batch 592 (2026-06-05) -- Strong-breakout filter for donchian_10_breakout
per owner answer (i) closing B591 deferred (e) item.

Owner directive answer (i) "Strong-breakout requirement":
  Today's close must clear the prior 10-day high by at least 0.5 * ATR(14)
  (long) or break the prior 10-day low by at least 0.5 * ATR(14) (short)
  to count as a real breakout. Filters trivial closes-just-above-level
  pseudo-breakouts that lack momentum behind them.

Scope per feedback_narrow_scope_blast_radius: applied to
strat_donchian_10_breakout (dual) ONLY. The new tight-long variant
strat_donchian_breakout_long was NOT updated this batch - flagged
in B592 end-of-turn summary for owner clarification.

Pins:
  (1) dc10_strong_breakout_up fires when close clears prior_high by
      >= 0.5 * ATR(14)
  (2) dc10_strong_breakout_up DOES NOT fire when close is just above
      prior_high (< 0.5 ATR clearance) - the trivial-breakout filter
  (3) dc10_strong_breakout_dn mirror
  (4) End-to-end via compute_donchian on synthetic OHLCV
"""
from __future__ import annotations

import pandas as pd
import pytest


def _build_df(closes, highs, lows, opens=None, volumes=None):
    n = len(closes)
    if opens is None: opens = closes[:]
    if volumes is None: volumes = [1_000_000] * n
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    }, index=pd.date_range("2024-01-01", periods=n))


def test_batch592_strong_breakout_up_fires_on_clear_break():
    """Pin (1): close clears prior_high_10 by >= 0.5 * ATR(14)."""
    from backtest.signals.technical import compute_donchian
    # 20 pre-bars with wide range: high-low = 4, prior_high_10 ~ 104.
    # ATR(14) ~ 4. 0.5 * ATR ~ 2. Strong-breakout requires close >= 106.
    # Today close 108 clears comfortably.
    pre_closes = [100.0] * 19
    pre_highs  = [104.0] * 19
    pre_lows   = [100.0] * 19
    closes = pre_closes + [108.0]
    highs  = pre_highs  + [109.0]
    lows   = pre_lows   + [104.0]
    df = _build_df(closes, highs, lows)
    out = compute_donchian(df)
    # prior_high_10 should be 104 (max of last 10 prior highs)
    assert out["dc10_strong_breakout_up"] == True, (
        f"close 108 vs prior_high 104 should pass strong-breakout; "
        f"signals={ {k:v for k,v in out.items() if 'dc10' in k} }"
    )


def test_batch592_strong_breakout_up_blocks_trivial_break():
    """Pin (2): close just above prior_high (< 0.5 ATR clearance) blocked."""
    from backtest.signals.technical import compute_donchian
    # Same pre-window: prior_high ~ 104, ATR ~ 4, 0.5*ATR ~ 2.
    # Strong-breakout requires close >= 106. Today close = 104.5
    # (above prior_high but only by 0.5 - much less than 0.5*ATR=2).
    pre_closes = [100.0] * 19
    pre_highs  = [104.0] * 19
    pre_lows   = [100.0] * 19
    closes = pre_closes + [104.5]
    highs  = pre_highs  + [105.0]
    lows   = pre_lows   + [104.0]
    df = _build_df(closes, highs, lows)
    out = compute_donchian(df)
    # dc10_breakout_up_1pct should still fire (close 104.5 > 104*0.99=102.96)
    assert out["dc10_breakout_up_1pct"] == True
    # But strong-breakout filter should BLOCK
    assert out["dc10_strong_breakout_up"] == False, (
        f"close 104.5 (only 0.5 above prior_high 104, less than "
        f"0.5*ATR) should fail strong-breakout filter"
    )


def test_batch592_strong_breakout_dn_mirror():
    """Pin (3): mirror for breakdown."""
    from backtest.signals.technical import compute_donchian
    # 20 pre-bars: prior_low_10 ~ 100, ATR ~ 4, 0.5*ATR ~ 2.
    # Strong-breakdown requires close <= 98. Today close = 95 (clears).
    pre_closes = [104.0] * 19
    pre_highs  = [108.0] * 19
    pre_lows   = [100.0] * 19
    closes = pre_closes + [95.0]
    highs  = pre_highs  + [100.0]
    lows   = pre_lows   + [94.0]
    df = _build_df(closes, highs, lows)
    out = compute_donchian(df)
    assert out["dc10_strong_breakout_dn"] == True


def test_batch592_full_pipeline_donchian_10_breakout():
    """Pin (4): end-to-end through compute_donchian + compute_volume to
    strat_donchian_10_breakout. Synthetic AMD-style strong breakout."""
    from backtest.signals.technical import compute_donchian, compute_volume
    from backtest.signals.screener import strat_donchian_10_breakout
    import numpy as np
    n = 30
    cl = list(np.linspace(100, 105, n - 1)) + [110.0]
    hi = list(np.linspace(101, 106, n - 1)) + [110.5]
    lo = list(np.linspace( 99, 104, n - 1)) + [108.0]
    vol = [1_000_000] * (n - 1) + [2_500_000]
    df = _build_df(cl, hi, lo, volumes=vol)
    # Override today's open to make today bullish (close > open)
    df.iloc[-1, df.columns.get_loc("open")] = 108.5
    dc_out = compute_donchian(df)
    vol_out = compute_volume(df)
    signals = {**dc_out, **vol_out,
               "macd_12_26_9_bullish": True,
               "close_above_open": True}
    out = strat_donchian_10_breakout(signals)
    assert out.get("fires") == True and out.get("direction") == "long", (
        f"Strong breakout (close 110 vs prior_high ~105.8, ATR ~2) should "
        f"fire post-B592; dc10_strong_breakout_up="
        f"{dc_out.get('dc10_strong_breakout_up')}; out={out}"
    )
