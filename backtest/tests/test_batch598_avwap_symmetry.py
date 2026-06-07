"""Batch 598 (2026-06-05) -- AVWAP anchor timeframe asymmetry fix per
owner directive 2026-06-05.

B597 left volume_spike_breakout with a timeframe asymmetry: LONG used
above_avwap_50low (50-day anchor), SHORT used above_avwap_20high
(20-day anchor). compute_vwap producer only emitted {252low, 50low,
20high} - no symmetric 20-day anchor pair was available.

B598 fix:
  (1) Producer: added avwap_20low to compute_vwap (additive; existing
      consumers of avwap_50low / 20high / 252low unchanged).
  (2) Strategy: switched strat_volume_spike_breakout LONG from
      above_avwap_50low -> above_avwap_20low. Both directions now use
      20-day anchors matching the DC20 breakout window.

Pins:
  (1) avwap_20low signal emitted by compute_vwap
  (2) above_avwap_20low emitted (close > avwap_20low)
  (3) pct_from_avwap_20low emitted
  (4) Existing above_avwap_50low / 20high / 252low still emitted
      (additive change confirmed)
  (5) strat_volume_spike_breakout LONG now requires above_avwap_20low
      (not 50low)
  (6) Legacy above_avwap_50low alone does NOT fire LONG post-B598
  (7) SHORT side unchanged (still uses above_avwap_20high)
"""
from __future__ import annotations

import numpy as np
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


def test_batch598_avwap_20low_signal_emitted():
    """Pin (1)+(2)+(3): producer emits avwap_20low + above_avwap_20low
    + pct_from_avwap_20low."""
    from backtest.signals.technical import compute_vwap
    # 30 bars: anchor at the swing low (index 5 - lowest low)
    closes = list(np.linspace(100, 105, 25)) + [106.0] * 5
    highs  = [c + 0.5 for c in closes]
    lows   = [c - 0.5 for c in closes]
    lows[5] = 95.0  # explicit swing low within last 20 bars
    df = _build_df(closes, highs, lows)
    out = compute_vwap(df)
    assert "avwap_20low" in out
    assert "above_avwap_20low" in out
    assert "pct_from_avwap_20low" in out
    assert out["avwap_20low"] > 0


def test_batch598_existing_avwap_signals_preserved():
    """Pin (4): additive change - {252low, 50low, 20high} still emitted.
    Fixture engineered to ensure each anchor falls within its window
    (not at the very last bar) so the AVWAP cumulative-from-anchor has
    at least 2 bars to compute over."""
    from backtest.signals.technical import compute_vwap
    n = 260
    closes = list(np.linspace(100, 110, n))
    highs  = [c + 0.5 for c in closes]
    lows   = [c - 0.5 for c in closes]
    # Inject anchors inside each window (not at the last bar):
    #   20-day window (last 20 bars: indices n-20..n-1)
    #     swing-high mid-window (index n-10)
    #     swing-low at index n-15
    highs[n - 10] = 120.0
    lows[n - 15]  = 90.0
    #   50-day swing-low at n-30 (within last 50 bars, not last)
    lows[n - 30] = 85.0
    #   252-day swing-low at n-200
    lows[n - 200] = 70.0
    df = _build_df(closes, highs, lows)
    out = compute_vwap(df)
    for key in ("avwap_252low", "avwap_50low", "avwap_20high", "avwap_20low",
                "above_avwap_252low", "above_avwap_50low",
                "above_avwap_20high", "above_avwap_20low"):
        assert key in out, f"existing/new signal {key} must be emitted"


def test_batch598_strategy_long_consumes_20low_not_50low():
    """Pin (5): LONG fires with above_avwap_20low; was 50low pre-B598."""
    from backtest.signals.screener import strat_volume_spike_breakout
    s = {
        "dc20_breakout_up": True,
        "vol_spike_15x": True,
        "above_avwap_20low": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
    }
    out = strat_volume_spike_breakout(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch598_strategy_long_legacy_50low_alone_blocked():
    """Pin (6): above_avwap_50low alone (without 20low) does NOT fire."""
    from backtest.signals.screener import strat_volume_spike_breakout
    s = {
        "dc20_breakout_up": True,
        "vol_spike_15x": True,
        "above_avwap_50low": True,   # legacy signal True
        "above_avwap_20low": False,  # but new signal False
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
    }
    assert strat_volume_spike_breakout(s)["fires"] is False, (
        "B598 swapped to 20low; legacy 50low alone must not fire"
    )


def test_batch598_strategy_short_still_uses_20high():
    """Pin (7): SHORT side still uses 20-day swing-high AVWAP anchor.
    B612 refactor: SHORT now consumes POSITIVE below_avwap_20high
    (symmetric to above_avwap_20low on LONG side) instead of the
    inverted `not s.get("above_avwap_20high")` pattern. 20-high anchor
    preserved."""
    from backtest.signals.screener import strat_volume_spike_breakout
    s = {
        "dc20_breakout_dn": True,
        "vol_spike_15x": True,
        "below_avwap_20high": True,  # B612 refactor: positive symmetric signal
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    out = strat_volume_spike_breakout(s)
    assert out["fires"] is True and out["direction"] == "short"
