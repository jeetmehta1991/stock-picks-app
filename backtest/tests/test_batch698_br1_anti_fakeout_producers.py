"""B698 regression-guard tests for the two new anti-fakeout producer
signals added to compute_volume + wired into strat_52w_high_breakout.

Owner-approved 2026-06-11 per output_audit/b693_sweeps/b693_sweeps_report.md:
  - Sweep 3: break-clearance margin (ATR-scaled) at 0.5-0.8x ATR plateau
    gives test FT 0.358 vs base 0.313 (+4.5pp OOS lift). Anti-fakeout #1.
  - Sweep 6 (immediate-reclaim filter): test FT 0.375 vs base 0.311
    (+6.4pp OOS lift, keeps 75% of fires). Anti-fakeout #4.

New producer signals (in compute_volume of technical.py):
  - break_52w_high_clearance_atr_05: True when close > prior_252_max + 0.5*ATR(14)
  - break_52w_high_confirmed_today: True when yesterday's close broke the
    52w high AND today's close still holds above that same level

BR-1 wiring (in screener.py strat_52w_high_breakout):
  - Score-of-2-of-5 across (vol_spike_17x, close_above_open,
    close_in_top_40pct_of_range, break_52w_high_clearance_atr_05,
    break_52w_high_confirmed_today)
  - Requires break_52w_high as the EVENT trigger
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtest.signals.technical import compute_volume
from backtest.signals.screener import strat_52w_high_breakout


def _make_df_with_pattern(closes: list[float], highs: list[float] | None = None,
                           lows: list[float] | None = None) -> pd.DataFrame:
    """Build a minimal OHLCV df. By default high=close, low=close-1.0 (so
    ATR is non-zero from the high-low range). Caller can override highs
    and lows to control 52w-high precisely."""
    n = len(closes)
    dates = pd.date_range("2020-01-02", periods=n, freq="B")
    h_list = highs if highs is not None else list(closes)
    l_list = lows if lows is not None else [c - 1.0 for c in closes]
    df = pd.DataFrame({
        "open": closes,
        "high": h_list,
        "low": l_list,
        "close": closes,
        "volume": [1_000_000] * n,
    }, index=dates)
    return df


# ---------------------------------------------------------------------------
# Pin 1: clearance_atr_05 producer signal is emitted
# ---------------------------------------------------------------------------
def test_b698_pin1_clearance_atr_05_emitted_in_signals_dict():
    """compute_volume must emit break_52w_high_clearance_atr_05 in the
    signals dict whenever there's enough history."""
    closes = [100 + i * 0.1 for i in range(300)]
    df = _make_df_with_pattern(closes)
    sigs = compute_volume(df)
    assert "break_52w_high_clearance_atr_05" in sigs
    # numpy bool_ is acceptable (np.False_ / np.True_)
    v = sigs["break_52w_high_clearance_atr_05"]
    assert isinstance(v, (bool, np.bool_))


# ---------------------------------------------------------------------------
# Pin 2: confirmed_today producer signal is emitted
# ---------------------------------------------------------------------------
def test_b698_pin2_confirmed_today_emitted_in_signals_dict():
    closes = [100 + i * 0.1 for i in range(300)]
    df = _make_df_with_pattern(closes)
    sigs = compute_volume(df)
    assert "break_52w_high_confirmed_today" in sigs
    v = sigs["break_52w_high_confirmed_today"]
    assert isinstance(v, (bool, np.bool_))


# ---------------------------------------------------------------------------
# Pin 3: atr_14 also emitted (used by the clearance signal)
# ---------------------------------------------------------------------------
def test_b698_pin3_atr_14_emitted_with_finite_value():
    closes = [100 + i * 0.05 for i in range(300)]
    df = _make_df_with_pattern(closes)
    sigs = compute_volume(df)
    assert "atr_14" in sigs
    assert sigs["atr_14"] is not None
    assert sigs["atr_14"] > 0


# ---------------------------------------------------------------------------
# Pin 4: clearance margin returns True when close clears by >= 0.5x ATR
# ---------------------------------------------------------------------------
def test_b698_pin4_clearance_True_when_close_clears_by_half_atr():
    """Pattern: 260 flat bars at 100, then 40 random-walk bars, then a
    big breakout that clears by 2x ATR. The clearance margin signal
    should fire True."""
    np.random.seed(0)
    closes = [100.0] * 260
    for _ in range(40):
        closes.append(closes[-1] + np.random.uniform(-0.5, 0.5))
    closes.append(max(closes) + 10.0)  # massive breakout
    # high=close, low=close-1.0 keeps high consistent
    df = _make_df_with_pattern(closes)
    sigs = compute_volume(df)
    assert sigs["break_52w_high"] is True or sigs["break_52w_high"] == True
    assert sigs["break_52w_high_clearance_atr_05"] is True or sigs["break_52w_high_clearance_atr_05"] == True


# ---------------------------------------------------------------------------
# Pin 5: clearance margin returns False on a 1-tick poke
# ---------------------------------------------------------------------------
def test_b698_pin5_clearance_False_on_one_tick_poke():
    np.random.seed(1)
    closes = [100.0] * 260
    for _ in range(40):
        closes.append(closes[-1] + np.random.uniform(-0.5, 0.5))
    # Tiny 1-tick break (much less than 0.5x ATR, which on this fixture
    # is ~1.0 from the 1-pt high-low range; so 0.5*ATR ~= 0.5)
    closes.append(max(closes) + 0.01)
    df = _make_df_with_pattern(closes)
    sigs = compute_volume(df)
    # break_52w_high should be True (close > prior max close = prior max high
    # since high=close in this fixture)
    assert sigs["break_52w_high"] is True or sigs["break_52w_high"] == True
    # But clearance should be False (didn't clear by 0.5x ATR)
    assert sigs["break_52w_high_clearance_atr_05"] is False or sigs["break_52w_high_clearance_atr_05"] == False


# ---------------------------------------------------------------------------
# Pin 6: confirmed_today True when yesterday broke + today still above
# ---------------------------------------------------------------------------
def test_b698_pin6_confirmed_True_when_yesterday_broke_today_holds():
    np.random.seed(2)
    closes = [100.0] * 260
    for _ in range(40):
        closes.append(closes[-1] + np.random.uniform(-0.5, 0.5))
    prev_high = max(closes)
    # Yesterday: breakout above prev_high
    closes.append(prev_high + 2.0)
    # Today: still above the broken level
    closes.append(prev_high + 1.5)
    df = _make_df_with_pattern(closes)
    sigs = compute_volume(df)
    assert sigs["break_52w_high_confirmed_today"] is True


# ---------------------------------------------------------------------------
# Pin 7: confirmed_today False when reclaim happens (today drops below level)
# ---------------------------------------------------------------------------
def test_b698_pin7_confirmed_False_when_today_reclaims():
    np.random.seed(3)
    closes = [100.0] * 260
    for _ in range(40):
        closes.append(closes[-1] + np.random.uniform(-0.5, 0.5))
    prev_high = max(closes)
    # Yesterday: broke up
    closes.append(prev_high + 2.0)
    # Today: dropped back below the broken level (reclaim = fakeout)
    closes.append(prev_high - 1.0)
    df = _make_df_with_pattern(closes)
    sigs = compute_volume(df)
    assert sigs["break_52w_high_confirmed_today"] is False


# ---------------------------------------------------------------------------
# Pin 8: BR-1 wires the 2 new signals into its 2-of-5 score
# ---------------------------------------------------------------------------
def test_b698_pin8_br1_uses_new_anti_fakeout_signals_in_score():
    """When all 3 original confirmations are False but BOTH new
    anti-fakeout signals are True, BR-1 fires (2-of-5 score met by the
    new signals alone)."""
    sig = {
        "break_52w_high": True,
        "vol_spike_17x": False,
        "close_above_open": False,
        "close_in_top_40pct_of_range": False,
        "break_52w_high_clearance_atr_05": True,
        "break_52w_high_confirmed_today": True,
    }
    r = strat_52w_high_breakout(sig)
    assert r["fires"] is True, "BR-1 must fire when 2 of 5 score (new signals alone)"


# ---------------------------------------------------------------------------
# Pin 9: BR-1 1-of-5 score does NOT fire
# ---------------------------------------------------------------------------
def test_b698_pin9_br1_1_of_5_does_not_fire():
    sig = {
        "break_52w_high": True,
        "break_52w_high_clearance_atr_05": True,  # 1 of 5
    }
    r = strat_52w_high_breakout(sig)
    assert r["fires"] is False


# ---------------------------------------------------------------------------
# Pin 10: BR-1 mixed 2-of-5 score (1 old + 1 new) fires
# ---------------------------------------------------------------------------
def test_b698_pin10_br1_mixed_2_of_5_score_fires():
    sig = {
        "break_52w_high": True,
        "vol_spike_17x": True,
        "break_52w_high_confirmed_today": True,
    }
    r = strat_52w_high_breakout(sig)
    assert r["fires"] is True


# ---------------------------------------------------------------------------
# Pin 11: signals_used metadata advertises the 2 new signals
# ---------------------------------------------------------------------------
def test_b698_pin11_signals_used_advertises_new_signals():
    r = strat_52w_high_breakout({"break_52w_high": True, "vol_spike_17x": True,
                                  "close_above_open": True})
    used = r.get("signals_used", [])
    assert "break_52w_high_clearance_atr_05" in used
    assert "break_52w_high_confirmed_today" in used
