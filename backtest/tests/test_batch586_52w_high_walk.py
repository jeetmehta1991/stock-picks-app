"""Batch 586 (2026-06-04) -- Stage 4 walk for 52w_high_breakout per
owner directive 2026-06-04. Four changes shipped:
  1. vol_spike_2x -> vol_spike_17x (owner picked >1.7x from 1.5-2 range)
  2. Add sector_outperforming_spy confluence filter (sector_strength.py)
  3. Add strat_52w_high_breakout_pullback_long (Class 7 NEW)
  4. Add strat_52w_low_breakdown_pullback_short (inverse per
     feedback_long_short_inverse_audit)
Plus trigger column plain-language enhancement in build_strategy_roster.

Pins:

  (1) vol_spike_17x signal emitted by compute_volume; True when
      ratio > 1.7
  (2) sector_strength producer returns sector_outperforming_spy bool
      for Information Technology sector (XLK vs SPY)
  (3) sector_strength producer returns empty dict for unknown sector
  (4) strat_52w_high_breakout fires ONLY when all 3 conditions true
  (5) strat_52w_high_breakout does NOT fire when sector
      underperforming (gate False)
  (6) strat_52w_high_breakout_pullback_long fires on
      near_52w_high_retest_long
  (7) strat_52w_low_breakdown_pullback_short fires on
      near_52w_low_retest_short
  (8) near_52w_high_retest_long signal emitted by compute_volume
      when pullback conditions met
  (9) ALL_STRATEGIES count = 215
  (10) build_strategy_roster trigger plain-language column populates
"""
from __future__ import annotations

import datetime
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


REPO = Path(__file__).resolve().parents[2]


def _build_df(closes, highs, lows, opens=None, volumes=None):
    n = len(closes)
    if opens is None: opens = closes[:]
    if volumes is None: volumes = [1_000_000] * n
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    }, index=pd.date_range("2024-01-01", periods=n))


def test_batch586_vol_spike_17x_emitted():
    """Pin (1). vol_ratio_20d = today_vol / mean(last 20 INCLUDING today).
    So to get ratio > 1.7, today_vol must significantly exceed the 20d
    mean which includes today itself. A today_vol = 3.0x baseline gives
    ratio ~= 3.0 / ((19 + 3) / 20) = 3.0 / 1.1 = 2.73 (well > 1.7)."""
    from backtest.signals.technical import compute_volume
    n = 25
    closes = [100.0] * n
    highs  = [101.0] * n
    lows   = [99.0] * n
    # Today volume 3x baseline -> ratio approx 2.73 -> > 1.7
    vol = [1_000_000] * (n - 1) + [3_000_000]
    df = _build_df(closes, highs, lows, volumes=vol)
    out = compute_volume(df)
    assert out["vol_spike_17x"] == True, (
        f"vol ratio = {out['vol_ratio_20d']} should fire vol_spike_17x (>1.7)"
    )
    # Quiet day: today_vol = baseline -> ratio = 1.0 -> NOT > 1.7
    vol2 = [1_000_000] * n
    df2 = _build_df(closes, highs, lows, volumes=vol2)
    out2 = compute_volume(df2)
    assert out2["vol_spike_17x"] == False


def test_batch586_sector_strength_it():
    """Pin (2): XLK vs SPY 20d return on a known historical date."""
    from backtest.signals.sector_strength import compute_sector_strength_signals
    out = compute_sector_strength_signals("Information Technology",
                                          datetime.date(2024, 6, 1))
    if not out:
        pytest.skip("XLK or SPY OHLCV parquet not present in this environment")
    assert "sector_outperforming_spy" in out
    assert "sector_etf_return_20d" in out
    assert "spy_return_20d" in out
    assert out["sector_etf_ticker"] == "XLK"


def test_batch586_sector_strength_unknown():
    """Pin (3): unknown sector -> empty dict."""
    from backtest.signals.sector_strength import compute_sector_strength_signals
    out = compute_sector_strength_signals("Unknown Sector XYZ",
                                          datetime.date(2024, 6, 1))
    assert out == {}


def test_batch586_strat_52w_high_breakout_post_b586():
    """Pin (4) + (5): all conditions required. B589 added 2 more gates
    (close_above_open + close_in_top_40pct_of_range)."""
    from backtest.signals.screener import strat_52w_high_breakout
    # All conditions True -> fires (B589 added 2 gates -> now 5 total)
    s_all = {"break_52w_high": True, "vol_spike_17x": True,
             "sector_outperforming_spy": True,
             "close_above_open": True, "close_in_top_40pct_of_range": True}
    assert strat_52w_high_breakout(s_all)["fires"] == True
    # Missing sector filter -> no fire
    s_no_sector = dict(s_all); s_no_sector["sector_outperforming_spy"] = False
    assert strat_52w_high_breakout(s_no_sector)["fires"] == False
    # Old vol_spike_2x alone (no _17x) -> no fire
    s_old = dict(s_all); s_old["vol_spike_17x"] = False
    s_old["vol_spike_2x"] = True
    assert strat_52w_high_breakout(s_old)["fires"] == False


def test_batch586_pullback_long_fires():
    """Pin (6)."""
    from backtest.signals.screener import strat_52w_high_breakout_pullback_long
    out = strat_52w_high_breakout_pullback_long({"near_52w_high_retest_long": True})
    assert out["fires"] == True
    assert out["direction"] == "long"


def test_batch586_pullback_short_fires():
    """Pin (7)."""
    from backtest.signals.screener import strat_52w_low_breakdown_pullback_short
    out = strat_52w_low_breakdown_pullback_short({"near_52w_low_retest_short": True})
    assert out["fires"] == True
    assert out["direction"] == "short"


def test_batch586_pullback_producer_signal_emitted():
    """Pin (8): synthetic data triggers near_52w_high_retest_long under
    B590-redesigned producer (single 30-bar window for both breakout
    detection AND year_high_pre30 reference + 3% tolerance per owner
    B590 directive).

    B590 producer windows:
      ref_window = df.iloc[-283:-31]  (252-bar window ending 30 bars
                                       before today; STABLE pre-breakout
                                       52w resistance)
      recent_closes = df.iloc[-31:-1] (last 30 bars before today;
                                       breakout-detection window)
      today = df.iloc[-1]

    Setup (total 283 bars):
      bars 0..251 (252 bars): close=99, HIGH=100, low=98
        -> year_high_pre30 = max(ref_window.high) = 100
      bars 252..281 (30 bars): breakout closes 102 / pullback 100.5
        -> recent_max_close = 102 > year_high_pre30 (100) ✓
      bar 282 (today): close=100.5, open=100, high=101, low=100
        -> within_3pct_high: |100.5 - 100|/100 = 0.5% <= 3% ✓
        -> today_below_peak: 100.5 < 102 * 0.99 = 100.98 ✓
        -> close_above_open: 100.5 > 100 ✓
        -> vol_below_avg: today vol < 20d avg ✓
    """
    from backtest.signals.technical import compute_volume
    pre   = [99.0]  * 252
    pre_h = [100.0] * 252
    pre_l = [98.0]  * 252
    # 30-bar breakout-detection window: bars 252..281
    # bar 252 = breakout day (close 102, exceeds 100); bars 253..281 = pullback
    breakout   = [102.0] + [100.5] * 29
    breakout_h = [102.5] + [101.0] * 29
    breakout_l = [100.5] + [100.0] * 29
    today_c = [100.5]
    today_h = [101.0]
    today_l = [100.0]
    closes = pre + breakout + today_c
    highs  = pre_h + breakout_h + today_h
    lows   = pre_l + breakout_l + today_l
    n = len(closes)
    assert n == 283, f"fixture must be 283 bars to engage year_high_pre30 window; got {n}"
    opens = closes[:-1] + [100.0]  # bullish today (close 100.5 > open 100.0)
    vol = [1_000_000] * (n - 1) + [600_000]  # below avg
    df = _build_df(closes, highs, lows, opens=opens, volumes=vol)
    out = compute_volume(df)
    assert out.get("near_52w_high_retest_long") == True, (
        f"Expected near_52w_high_retest_long=True post-B590; "
        f"year_high={out.get('year_high')} close={closes[-1]} "
        f"vol_ratio={out.get('vol_ratio_20d')}"
    )


def test_batch586_all_strategies_count_at_least_215():
    """Pin (9). B586 brought count to 215; later batches add more
    (B588 +1 52w_low_breakdown_with_smart_money_short mirror)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) >= 215


def test_batch586_builder_renders_plain_trigger():
    """Pin (10): regen STRATEGY_ROSTER.md and verify trigger plain-language
    is rendered for 52w_high_breakout."""
    rc = subprocess.run([sys.executable,
                         str(REPO / "scripts" / "build_strategy_roster.py")],
                        capture_output=True, text=True, timeout=60)
    assert rc.returncode == 0
    doc = (REPO / "STRATEGY_ROSTER.md").read_text(encoding="utf-8")
    # The plain-language column should contain "close > prior 252d high" for 52w_high_breakout
    import re
    m = re.search(r"`52w_high_breakout` \|[^\n]*", doc)
    assert m, "52w_high_breakout row missing"
    row = m.group(0)
    # Plain trigger column should reference the human-readable conditions.
    # B589 owner-directed expanded descriptions; phrasing changed.
    assert "prior 252 trading days" in row, (
        f"52w_high_breakout row missing '252 trading days' plain phrase; "
        f"row:\n{row[:400]}"
    )
    assert "sector SPDR ETF" in row or "outperforming" in row.lower(), (
        f"52w_high_breakout row missing sector strength plain phrase"
    )
