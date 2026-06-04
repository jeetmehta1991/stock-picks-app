"""Batch 590 (2026-06-04) -- pullback producer redesign + false-breakout
filters per owner directives 2026-06-04.

B590a (redesign): single internally-consistent 30-bar window for BOTH
  (a) breakout detection AND (b) year_high_pre30 reference.
  year_high_pre30 = max HIGH over 252 days ending 30 bars ago (STABLE -
  does not drift as new highs print during breakout itself, fixing B586
  flaw).
  Retest tolerance widened 1% -> 3% per owner directive.

B590b (false-breakout filters per owner directive):
  - Time filter: at least 3 candles must form between first breakout bar
    and today before validating retest.
  - ATR band filter: today's close must be within 1*ATR(14) of
    year_high_pre30 (LONG) / year_low_pre30 (SHORT). Closes more than
    1 ATR outside the band represent a failed retest, not a pullback.

Pins:
  (1) near_52w_high_retest_long requires 7 conditions (5 from B590a + 2
      from B590b)
  (2) Time filter blocks fires when breakout is too recent (< 3 candles
      between breakout and today)
  (3) ATR-band filter blocks fires when today's close is more than 1
      ATR below year_high_pre30
  (4) Short-side mirror filters work symmetrically
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


def _make_pullback_long_fixture(n_bars_between_breakout_and_today=29,
                                today_close=100.5):
    """Build 283-bar synthetic that fires near_52w_high_retest_long.

    Pre-window (252 bars): close=99, high=100, low=98 -> year_high_pre30=100.
    Breakout-window (30 bars): bar 252 = breakout (close 102, high 102.5);
      remaining 29 bars = pullback (close 100.5).
    Today: close=today_close, high=close+0.5, low=close-0.5, open=close-0.5.
    """
    pre   = [99.0]  * 252
    pre_h = [100.0] * 252
    pre_l = [98.0]  * 252
    # First (oldest) breakout bar at index 0 of breakout-window, then
    # 29 pullback bars. So breakout happened 30 bars before today.
    breakout = [102.0] + [100.5] * 29
    breakout_h = [102.5] + [101.0] * 29
    breakout_l = [100.5] + [100.0] * 29
    closes = pre + breakout + [today_close]
    highs  = pre_h + breakout_h + [today_close + 0.5]
    lows   = pre_l + breakout_l + [today_close - 0.5]
    n = len(closes)
    opens = closes[:-1] + [today_close - 0.5]
    vol = [1_000_000] * (n - 1) + [600_000]
    return _build_df(closes, highs, lows, opens=opens, volumes=vol)


def test_batch590_pullback_long_fires_under_redesign():
    """Pin (1): all 7 gates satisfied -> fires."""
    from backtest.signals.technical import compute_volume
    df = _make_pullback_long_fixture()
    out = compute_volume(df)
    assert out.get("near_52w_high_retest_long") == True


def test_batch590_time_filter_blocks_recent_breakout():
    """Pin (2): breakout bar < 3 candles before today -> filter blocks."""
    from backtest.signals.technical import compute_volume
    # Pre 252 + 29 pullback bars + breakout AT bar 281 + today
    # i.e. breakout is at position -2 (1 bar before today) -> only 1 candle
    # between breakout and today -> < 3 -> filter blocks.
    pre   = [99.0]  * 252
    pre_h = [100.0] * 252
    pre_l = [98.0]  * 252
    # 29 quiet pullback bars FIRST (no breakouts), then breakout at end of window
    quiet = [99.0] * 29
    quiet_h = [99.5] * 29
    quiet_l = [98.5] * 29
    breakout = [102.0]  # breakout at bar 281 (1 bar before today)
    breakout_h = [102.5]
    breakout_l = [100.5]
    today_c = [100.5]
    today_h = [101.0]
    today_l = [100.0]
    closes = pre + quiet + breakout + today_c
    highs  = pre_h + quiet_h + breakout_h + today_h
    lows   = pre_l + quiet_l + breakout_l + today_l
    n = len(closes)
    opens = closes[:-1] + [100.0]
    vol = [1_000_000] * (n - 1) + [600_000]
    df = _build_df(closes, highs, lows, opens=opens, volumes=vol)
    out = compute_volume(df)
    # Breakout exists + within 3pct + below peak, but time filter fails
    assert out.get("near_52w_high_retest_long") == False, (
        "Time filter should block fire when breakout is < 3 candles old"
    )


def test_batch590_atr_band_filter_blocks_far_close():
    """Pin (3): today's close more than 1 ATR below year_high_pre30 -> blocked."""
    from backtest.signals.technical import compute_volume
    # Build fixture where retest tolerance (3%) would normally pass but
    # ATR band fails. Construct high ATR pre-window then today close
    # 4 below year_high_pre30, with ATR much smaller than that.
    # Actually simpler: pre window VERY quiet (TR ~ 0) -> ATR ~ 0 ->
    # ATR band degenerates (filter passes trivially when ATR=0).
    # Alternative: use a small-ATR fixture and put today's close just
    # outside ATR but within 3pct. Pre: high-low=0.5 -> ATR ~ 0.5. Today
    # close = 99.0, year_high_pre30=100 -> diff = 1.0 > 0.5 -> blocks.
    # But within 3pct still passes (1/100 = 1% <= 3%).
    pre_c = [99.5] * 252
    pre_h = [99.75] * 252
    pre_l = [99.25] * 252  # narrow range -> small ATR
    # Pre-window max high = 99.75; we need year_high_pre30 = 99.75 here.
    # Breakout: bars 252..281 with closes > 99.75. Use close=101.
    breakout = [101.0] + [100.0] * 29
    breakout_h = [101.5] + [100.5] * 29
    breakout_l = [100.5] + [99.5] * 29
    # Today: close = 98.5 (1.25 below year_high_pre30=99.75 -> 1.25% < 3% pass
    # but far outside small ATR band).
    today_c = [98.5]
    today_h = [99.0]
    today_l = [98.0]
    closes = pre_c + breakout + today_c
    highs  = pre_h + breakout_h + today_h
    lows   = pre_l + breakout_l + today_l
    n = len(closes)
    opens = closes[:-1] + [98.0]  # bullish (close 98.5 > open 98.0)
    vol = [1_000_000] * (n - 1) + [600_000]
    df = _build_df(closes, highs, lows, opens=opens, volumes=vol)
    out = compute_volume(df)
    # ATR band filter must block this fire
    assert out.get("near_52w_high_retest_long") == False, (
        f"ATR-band filter should block when close is >1 ATR below "
        f"year_high_pre30; year_high={out.get('year_high')}"
    )


def test_batch590_pullback_short_fires_under_redesign():
    """Pin (4): mirror - synthetic that fires near_52w_low_retest_short."""
    from backtest.signals.technical import compute_volume
    # Mirror of long fixture: high=51, low=49, close=50 baseline ->
    # year_low_pre30 = 49 (lowest LOW in pre-window).
    pre_c = [51.0] * 252
    pre_h = [52.0] * 252
    pre_l = [50.0] * 252  # year_low_pre30 = 50
    # Breakdown at bar 252: close 48 (< 50). Then 29 pullback bars at 49.5
    breakdown = [48.0] + [49.5] * 29
    breakdown_h = [49.0] + [50.0] * 29
    breakdown_l = [47.5] + [49.0] * 29
    # Today: close=49.5 (within 3% of 50, above breakdown trough)
    today_c = [49.5]
    today_h = [50.0]
    today_l = [49.0]
    closes = pre_c + breakdown + today_c
    highs  = pre_h + breakdown_h + today_h
    lows   = pre_l + breakdown_l + today_l
    n = len(closes)
    opens = closes[:-1] + [50.0]  # bearish today (close 49.5 < open 50.0)
    vol = [1_000_000] * (n - 1) + [600_000]
    df = _build_df(closes, highs, lows, opens=opens, volumes=vol)
    out = compute_volume(df)
    assert out.get("near_52w_low_retest_short") == True, (
        f"Mirror should fire under B590; year_low={out.get('year_low')} "
        f"close={closes[-1]} vol_ratio={out.get('vol_ratio_20d')}"
    )
