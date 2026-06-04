"""Batch 584 (2026-06-04) -- fix compute_donchian rolling-window
off-by-one bug (same pattern as B582 year_high).

Owner directive 2026-06-04 (option "Apply + also fix dc_new_high
consistency"): exclude today's bar from the rolling-N window for
breakout_up / breakout_dn / new_high signals so the comparison is
"today close/high vs PRIOR-N-day max/min".

ROOT CAUSE (pre-B584):
  upper = df["high"].rolling(10).max()
  result["dc10_breakout_up"] = close >= upper.iloc[-1] * 0.998
  upper.iloc[-1] = max of last 10 bars INCLUDING today's high.
  Since close <= today_high <= upper.iloc[-1], the gate effectively
  required close >= 99.8pct of today_high AND today_high == max-of-10.
  Same bug pattern as 52w_high (B582).

FIX:
  prior = df.iloc[:-1]
  upper_prior = prior["high"].tail(period).max()
  result["dc10_breakout_up"] = close >= upper_prior * 0.998
  result["dc10_new_high"] = today_high > upper_prior

AFFECTED STRATEGIES (6):
  donchian_10_breakout (dual), donchian_breakdown_short,
  volume_spike_breakout (dual), squeeze_setup_long,
  news_momentum_long, donchian_breakout_with_smart_money_long.

Pins:

  (1) dc10_breakout_up fires on AMD-style breakout (close 107 vs
      prior-10 max 105) -- was False pre-B584, True post-B584
  (2) dc20_breakout_up fires on equivalent 20-day case
  (3) dc10_breakout_dn fires on breakdown (mirror)
  (4) dc20_breakout_dn fires (mirror)
  (5) dc10_new_high fires when today's high exceeds prior-10 high
  (6) dc10_upper / _lower / _mid retain current-rolling values
      (display-only signals; INCLUDE today)
  (7) downstream strat_donchian_10_breakout fires given post-fix
      signals + macd_bullish + vol_above_avg
  (8) downstream strat_donchian_breakdown_short fires given post-fix
      signals
  (9) full pipeline: synthetic OHLCV ending in breakout day +
      compute_donchian + strategy returns fires=True
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


def test_batch584_dc10_breakout_up_fires_amd_style():
    """Pin (1): close 107 vs prior-10-day max 105 -> fires."""
    from backtest.signals.technical import compute_donchian
    # 11 bars: prior 10 bars in 100-105 high range, today close 107
    # with today's intraday high 108 (HIGHER than today's close)
    hi = [101, 102, 103, 104, 105, 104, 103, 102, 103, 104, 105, 108]
    lo = [ 98,  99, 100,  98, 100,  99,  98, 100, 101,  99, 100, 106]
    cl = [ 99, 100, 102, 101, 103, 102, 101, 101, 102, 101, 103, 107]
    df = _build_df(cl, hi, lo)
    out = compute_donchian(df)
    assert out["dc10_breakout_up"] == True, (
        f"close 107 vs prior-10-day max 105 should fire dc10_breakout_up; "
        f"dc10_upper (incl today) = {out.get('dc10_upper')}"
    )


def test_batch584_dc20_breakout_up():
    """Pin (2)."""
    from backtest.signals.technical import compute_donchian
    n = 22  # 20 prior + today + buffer
    cl = list(np.linspace(100, 105, n - 1)) + [110.0]
    hi = list(np.linspace(101, 106, n - 1)) + [111.0]
    lo = list(np.linspace( 99, 104, n - 1)) + [109.0]
    df = _build_df(cl, hi, lo)
    out = compute_donchian(df)
    assert out["dc20_breakout_up"] == True


def test_batch584_dc10_breakout_dn_fires():
    """Pin (3): close below prior-10-day low."""
    from backtest.signals.technical import compute_donchian
    hi = [101, 102, 103, 104, 105, 104, 103, 102, 103, 104, 105,  97]
    lo = [ 98,  99, 100,  98, 100,  99,  98, 100, 101,  99, 100,  93]
    cl = [ 99, 100, 102, 101, 103, 102, 101, 101, 102, 101, 103,  95]
    df = _build_df(cl, hi, lo)
    out = compute_donchian(df)
    assert out["dc10_breakout_dn"] == True


def test_batch584_dc20_breakout_dn():
    """Pin (4)."""
    from backtest.signals.technical import compute_donchian
    n = 22
    cl = list(np.linspace(105, 100, n - 1)) + [92.0]
    hi = list(np.linspace(106, 101, n - 1)) + [94.0]
    lo = list(np.linspace(104,  99, n - 1)) + [91.0]
    df = _build_df(cl, hi, lo)
    out = compute_donchian(df)
    assert out["dc20_breakout_dn"] == True


def test_batch584_dc10_new_high_expanding_channel():
    """Pin (5): today's high exceeds prior-10 max."""
    from backtest.signals.technical import compute_donchian
    hi = [101, 102, 103, 104, 105, 104, 103, 102, 103, 104, 105, 110]
    lo = [ 98,  99, 100,  98, 100,  99,  98, 100, 101,  99, 100, 108]
    cl = [ 99, 100, 102, 101, 103, 102, 101, 101, 102, 101, 103, 109]
    df = _build_df(cl, hi, lo)
    out = compute_donchian(df)
    assert out["dc10_new_high"] == True


def test_batch584_dc10_display_signals_include_today():
    """Pin (6): _upper / _lower / _mid display values retain
    current-rolling semantic (include today). Per B584 design choice."""
    from backtest.signals.technical import compute_donchian
    hi = [101, 102, 103, 104, 105, 104, 103, 102, 103, 104, 105, 108]
    lo = [ 98,  99, 100,  98, 100,  99,  98, 100, 101,  99, 100, 106]
    cl = [ 99, 100, 102, 101, 103, 102, 101, 101, 102, 101, 103, 107]
    df = _build_df(cl, hi, lo)
    out = compute_donchian(df)
    # dc10_upper INCLUDES today's high (108) - rolling-10 max ending today
    assert out["dc10_upper"] == 108.0
    # dc10_lower INCLUDES today's low - rolling-10 min ending today
    assert out["dc10_lower"] == 98.0


def test_batch584_donchian_10_breakout_downstream():
    """Pin (7): strat_donchian_10_breakout fires given post-fix signals.
    Batch 591 added (b) dc10_breakout_up_1pct + (c) close_above_open +
    (d) close_in_top_40pct_of_range gates; Batch 592 added (e)
    dc10_strong_breakout_up gate. Test updated for all 6."""
    from backtest.signals.screener import strat_donchian_10_breakout
    s = {
        "dc10_breakout_up_1pct": True,
        "vol_above_avg": True,
        "macd_12_26_9_bullish": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
        "dc10_strong_breakout_up": True,
    }
    out = strat_donchian_10_breakout(s)
    assert out.get("fires") == True, (
        f"donchian_10_breakout long should fire post-B592 with all 6 gates: {out}"
    )
    assert out.get("direction") == "long"


def test_batch584_donchian_breakdown_short_downstream():
    """Pin (8): strat_donchian_breakdown_short fires given post-fix signals.
    Batch 591 deleted this strategy; Batch 592 RESTORED it per owner
    correction 2026-06-05 (both tight-long AND tight-short variants
    coexist for symmetry)."""
    from backtest.signals.screener import strat_donchian_breakdown_short
    s = {
        "dc10_breakout_dn": True,
        "vol_spike_15x": True,
        "macd_12_26_9_bullish": False,
    }
    out = strat_donchian_breakdown_short(s)
    assert out["fires"] == True
    assert out["direction"] == "short"


def test_batch584_full_pipeline_amd_style():
    """Pin (9): full pipeline from synthetic OHLCV through
    compute_donchian + compute_volume to strat_donchian_10_breakout.
    Batch 591 added strong-close + bullish-bar gates - fixture updated
    so today's bar reflects them (open < close, close in top 40% of
    bar range)."""
    from backtest.signals.technical import compute_donchian, compute_volume
    from backtest.signals.screener import strat_donchian_10_breakout
    n = 30
    cl = list(np.linspace(100, 105, n - 1)) + [110.0]
    hi = list(np.linspace(101, 106, n - 1)) + [110.5]  # close 110 in top
                                                        # 40pct: (110.5-110)
                                                        # /(110.5-108)=0.2
    lo = list(np.linspace( 99, 104, n - 1)) + [108.0]
    # Volume spike on breakout day
    vol = [1_000_000] * (n - 1) + [2_500_000]
    # _build_df sets open=close by default - override today's open to
    # 108.5 so close (110) > open -> close_above_open True
    df = _build_df(cl, hi, lo, vol)
    df.iloc[-1, df.columns.get_loc("open")] = 108.5
    dc_out = compute_donchian(df)
    vol_out = compute_volume(df)
    # close_above_open is emitted from a separate producer
    # (compute_overnight_returns); inject directly since this test only
    # covers the donchian->volume->strategy path
    signals = {**dc_out, **vol_out,
               "macd_12_26_9_bullish": True,
               "close_above_open": True}
    out = strat_donchian_10_breakout(signals)
    assert out.get("fires") == True and out.get("direction") == "long", (
        f"AMD-style breakout end-to-end should fire donchian_10_breakout long "
        f"post-B591; dc10_breakout_up_1pct={dc_out.get('dc10_breakout_up_1pct')} "
        f"vol_above_avg={vol_out.get('vol_above_avg')} "
        f"close_above_open={vol_out.get('close_above_open')} "
        f"close_in_top_40pct_of_range={vol_out.get('close_in_top_40pct_of_range')} "
        f"out={out}"
    )
