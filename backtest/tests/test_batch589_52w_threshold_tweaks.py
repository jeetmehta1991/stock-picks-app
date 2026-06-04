"""Batch 589 (2026-06-04) -- 52w pair threshold tweaks per owner
directives in Stage 4 walk turn:
  1. 52w_high_breakout + inverse: add close_above_open +
     close_in_top_40pct_of_range (close_below_open +
     close_in_bottom_40pct_of_range for inverse)
  2. 52w_high_breakout_with_smart_money_long + mirror:
     vol_above_avg -> vol_spike_12x (>=1.2x);
     near_52w_high -> near_52w_high_95pct (95pct of prior 252d high);
     mirror uses near_52w_low_105pct.

Plus saved feedback_no_rushing_per_strategy_tweak memory + Q1 fix
flipping Class 0 Awaiting rows to Implemented for walked strategies.

Pins:

  (1) vol_spike_12x emitted by compute_volume when ratio >= 1.2
  (2) close_in_top_40pct_of_range emitted when close is in top 40% of bar
  (3) close_in_bottom_40pct_of_range mirror
  (4) near_52w_high_95pct emitted (95pct of prior 252d high)
  (5) near_52w_low_105pct mirror
  (6) strat_52w_high_breakout requires all 5 conditions (B589 added 2)
  (7) strat_52w_low_breakdown requires all 5 conditions (mirror)
  (8) strat_52w_high_breakout_with_smart_money_long uses _95pct + _12x
  (9) strat_52w_low_breakdown_with_smart_money_short mirror uses _105pct + _12x
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest


APPROVALS = Path("C:/tmp/r4_optimization_candidates/approvals.json")


def _build_df(closes, highs, lows, opens=None, volumes=None):
    n = len(closes)
    if opens is None: opens = closes[:]
    if volumes is None: volumes = [1_000_000] * n
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    }, index=pd.date_range("2024-01-01", periods=n))


def test_batch589_vol_spike_12x_emitted():
    """Pin (1). ratio >= 1.2 fires; <1.2 does not."""
    from backtest.signals.technical import compute_volume
    n = 25
    closes = [100.0] * n
    highs  = [101.0] * n
    lows   = [99.0] * n
    # Need today_vol s.t. ratio >= 1.2:
    #   ratio = today_v / mean(last 20 incl today)
    #   1.4M today: avg = (19*1M + 1.4M)/20 = 1.02M; ratio = 1.4/1.02 = 1.37 (> 1.2)
    df = _build_df(closes, highs, lows, volumes=[1_000_000]*(n-1) + [1_400_000])
    out = compute_volume(df)
    assert out["vol_spike_12x"] == True
    # Quiet day -> ratio = 1.0 -> not >= 1.2
    df2 = _build_df(closes, highs, lows, volumes=[1_000_000]*n)
    out2 = compute_volume(df2)
    assert out2["vol_spike_12x"] == False


def test_batch589_close_in_top_40pct_of_range():
    """Pin (2): close in top 40% of bar range. (high-close)/(high-low) <= 0.4."""
    from backtest.signals.technical import compute_volume
    n = 25
    # Today: high=110, low=100, close=108 -> (110-108)/(110-100) = 0.2 (in top 20%, qualifies)
    closes = [100.0] * (n - 1) + [108.0]
    highs  = [100.0] * (n - 1) + [110.0]
    lows   = [100.0] * (n - 1) + [100.0]
    df = _build_df(closes, highs, lows)
    out = compute_volume(df)
    assert out["close_in_top_40pct_of_range"] == True
    # Close at midpoint: high=110, low=100, close=104 -> (110-104)/10 = 0.6 (in bottom 40%)
    closes2 = [100.0] * (n - 1) + [104.0]
    highs2  = [100.0] * (n - 1) + [110.0]
    lows2   = [100.0] * (n - 1) + [100.0]
    df2 = _build_df(closes2, highs2, lows2)
    out2 = compute_volume(df2)
    assert out2["close_in_top_40pct_of_range"] == False


def test_batch589_close_in_bottom_40pct_of_range():
    """Pin (3): mirror."""
    from backtest.signals.technical import compute_volume
    n = 25
    # Today: high=110, low=100, close=102 -> (102-100)/10 = 0.2 (in bottom 20%)
    df = _build_df([100.0]*(n-1)+[102.0], [100.0]*(n-1)+[110.0], [100.0]*(n-1)+[100.0])
    out = compute_volume(df)
    assert out["close_in_bottom_40pct_of_range"] == True


def test_batch589_near_52w_high_95pct():
    """Pin (4): 95pct tolerance for smart_money sleeve."""
    from backtest.signals.technical import compute_volume
    # Build 254 bars; prior_year_high (252d window excluding today) needs to compute.
    # Last 253 bars at high=100; today close 95.0 = exactly 95% of 100.
    import numpy as np
    n = 254
    closes = list(np.linspace(80, 99, n - 1)) + [95.0]
    highs  = list(np.linspace(81, 100, n - 1)) + [99.0]  # prior max high = 100
    lows   = list(np.linspace(79, 98, n - 1)) + [94.0]
    df = _build_df(closes, highs, lows)
    out = compute_volume(df)
    # year_high should be 100 (prior 252d max)
    # near_52w_high_95pct = close >= 100 * 0.95 = 95.0
    assert out["near_52w_high_95pct"] == True
    # But near_52w_high (98%) should NOT fire: 95 < 98
    assert out["near_52w_high"] == False


def test_batch589_near_52w_low_105pct():
    """Pin (5): mirror."""
    from backtest.signals.technical import compute_volume
    import numpy as np
    n = 254
    # prior 252d min low = 50; today close = 52.5 = exactly 105% of 50
    closes = list(np.linspace(80, 60, n - 1)) + [52.5]
    highs  = list(np.linspace(81, 61, n - 1)) + [53.0]
    lows   = list(np.linspace(79, 51, n - 1)) + [52.0]  # prior min low ~50
    # Adjust to make prior_year_low exactly 50
    lows[100] = 50.0
    df = _build_df(closes, highs, lows)
    out = compute_volume(df)
    # year_low should be 50; close 52.5 <= 50*1.05 = 52.5 -> True
    assert out["near_52w_low_105pct"] == True


def test_batch589_strat_52w_high_breakout_requires_5():
    """Pin (6): all 5 conditions required (B589 added 2)."""
    from backtest.signals.screener import strat_52w_high_breakout
    # All True -> fires
    s_all = {"break_52w_high": True, "vol_spike_17x": True,
             "sector_outperforming_spy": True, "close_above_open": True,
             "close_in_top_40pct_of_range": True}
    assert strat_52w_high_breakout(s_all)["fires"] == True
    # Missing close_above_open -> no fire
    s_no_co = dict(s_all); s_no_co["close_above_open"] = False
    assert strat_52w_high_breakout(s_no_co)["fires"] == False
    # Missing top_40 -> no fire
    s_no_top = dict(s_all); s_no_top["close_in_top_40pct_of_range"] = False
    assert strat_52w_high_breakout(s_no_top)["fires"] == False


def test_batch589_strat_52w_low_breakdown_requires_5():
    """Pin (7) mirror."""
    from backtest.signals.screener import strat_52w_low_breakdown
    s_all = {"break_52w_low": True, "vol_spike_17x": True,
             "sector_underperforming_spy": True, "close_below_open": True,
             "close_in_bottom_40pct_of_range": True}
    assert strat_52w_low_breakdown(s_all)["fires"] == True
    s_no_bot = dict(s_all); s_no_bot["close_in_bottom_40pct_of_range"] = False
    assert strat_52w_low_breakdown(s_no_bot)["fires"] == False


def test_batch589_strat_52w_high_smart_money_new_gates():
    """Pin (8): _95pct + _12x replaced 98pct + above_avg."""
    from backtest.signals.screener import strat_52w_high_breakout_with_smart_money_long
    s = {"near_52w_high_95pct": True, "close_above_open": True,
         "vol_spike_12x": True, "institutional_buy": True}
    assert strat_52w_high_breakout_with_smart_money_long(s)["fires"] == True
    # Legacy near_52w_high alone should NOT fire (we use _95pct now)
    s_legacy = {"near_52w_high": True, "close_above_open": True,
                "vol_above_avg": True, "institutional_buy": True}
    assert strat_52w_high_breakout_with_smart_money_long(s_legacy)["fires"] == False


def test_batch589_strat_52w_low_smart_money_mirror():
    """Pin (9): mirror of pin 8."""
    from backtest.signals.screener import strat_52w_low_breakdown_with_smart_money_short
    s = {"near_52w_low_105pct": True, "close_below_open": True,
         "vol_spike_12x": True, "cluster_sell": True}
    assert strat_52w_low_breakdown_with_smart_money_short(s)["fires"] == True


def test_batch589_class_0_awaiting_flipped_to_implemented():
    """Q1 fix: walked strategies' Class 0 Awaiting rows now show
    Implemented in approvals.json."""
    if not APPROVALS.exists():
        pytest.skip("approvals.json absent")
    data = json.loads(APPROVALS.read_text(encoding="utf-8"))
    reviewed = data.get("s4_reviewed_strategies", {})
    # Pick a known-walked strategy with Class 0 row
    target = "52w_high_breakout"
    if target not in reviewed:
        pytest.skip(f"{target} not in s4_reviewed_strategies (test stale)")
    class_0_rows = [r for r in data["approvals"]
                    if r["strategy"] == target and r["change_class"] == 0]
    if not class_0_rows:
        pytest.skip(f"{target} has no Class 0 row to check")
    # After B589 flip, the Class 0 row should be Implemented (not Awaiting)
    assert class_0_rows[0]["status"] == "Implemented", (
        f"{target} Class 0 row should be Implemented post-B589 Q1 fix; "
        f"got {class_0_rows[0]['status']}"
    )
