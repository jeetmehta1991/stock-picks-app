"""Batch 686 (2026-06-10) -- owner-approved inverted cup-and-handle Class 7
NEW + producer methodology work; deferred from B685 + scoped + executed
in B686 per owner directive 'execute now'.

Owner approval 2026-06-10: 'Inverted cup-and-handle deferred - needs
producer-side methodology work (inverted cup detection criteria + handle
detection on inverted topology); separate batch when owner ready to scope.
execute now'

Components shipped:

  1. detect_inverted_cup_and_handle NEW producer in chart_patterns.py
     (symmetric bearish mirror of detect_cup_and_handle):
     - left_rim_low (min of lows in first 25%) replaces left_rim (max highs)
     - right_rim_low (min of lows in last 25%) replaces right_rim
     - cup_high (max close in middle 50%) replaces cup_low (min close)
     - rim_low = min(rim_lows) replaces rim = max(rim_highs)
     - cup_height_pct = (cup_high - rim_low) / rim_low [10-35%]
     - handle_bounce_pct = (handle_high - handle_low) / handle_low [<15%]
     - breakdown_level = handle_low (SHORT-entry trigger)

  2. strat_inverted_cup_and_handle_short Class 7 NEW in screener.py
     (Bulkowski 2005 'rounded top with handle' / 'dump and pop'):
     5-gate symmetric to CP-1 cup_and_handle_long (post-B685 Pattern A
     WAVE 2 swept design): inverted_cup_handle_detected + below_ema_200
     + vol_spike_2x + below_ema_50 + rsi_14>30

  3. ALL_STRATEGIES registry entry 'inverted_cup_and_handle_short'

  4. compute_all_chart_patterns aggregator updated to invoke the new
     producer (defensive try/except).

  5. B671 borrow-trap gate applies (SHORT direction via _strat).

Strategy count impact: 221 -> 222 (+1 Class 7 NEW).
Active: 221 (222 registered - 1 disabled dxy_headwind).

Pins:

Producer methodology (4):
  (1)  detect_inverted_cup_and_handle importable from chart_patterns
  (2)  producer returns {} on insufficient history (None / empty / <120 bars)
  (3)  producer rejects (returns False) when cup_height outside [10%, 35%]
  (4)  producer rejects when rim_diff > 5%

Strategy wiring (3):
  (5)  strat_inverted_cup_and_handle_short importable + callable
  (6)  'inverted_cup_and_handle_short' in ALL_STRATEGIES
  (7)  ALL_STRATEGIES count == 222 (was 221 post-B685; +1 B686 Class 7 NEW)

Fire-logic (4):
  (8)  Fires SHORT on all 5 gates True
  (9)  Does NOT fire when below_ema_200 missing (B630 default-False fail-safe)
  (10) Does NOT fire when vol_spike_2x missing (volume confirmation required)
  (11) Does NOT fire on rsi_14<=30 (oversold; symmetric to CP-1 not-overbought)

Aggregator integration (1):
  (12) compute_all_chart_patterns invokes detect_inverted_cup_and_handle
       (returns dict containing inverted_cup_handle_detected key when
       sufficient data; producer-additive merge)
"""
from __future__ import annotations

import pandas as pd
import numpy as np


# ============ Producer methodology (4 pins) ============

def test_batch686_detect_inverted_cup_and_handle_importable():
    """Pin (1)."""
    from backtest.signals.chart_patterns import detect_inverted_cup_and_handle
    assert callable(detect_inverted_cup_and_handle)


def test_batch686_producer_insufficient_history_returns_empty():
    """Pin (2): defensive on None / empty / too-few-bars (<120)."""
    from backtest.signals.chart_patterns import detect_inverted_cup_and_handle
    assert detect_inverted_cup_and_handle(None) == {}
    assert detect_inverted_cup_and_handle(pd.DataFrame()) == {}
    # 50 bars insufficient for 120-bar lookback
    df = pd.DataFrame({
        "open": [100.0] * 50, "high": [101.0] * 50,
        "low": [99.0] * 50, "close": [100.0] * 50,
    })
    assert detect_inverted_cup_and_handle(df) == {}


def test_batch686_producer_rejects_cup_height_outside_range():
    """Pin (3): cup_height must be in [10%, 35%] band."""
    from backtest.signals.chart_patterns import detect_inverted_cup_and_handle
    # Flat data - cup_height = 0% - REJECTED
    df_flat = pd.DataFrame({
        "open":  [100.0] * 130, "high":  [100.5] * 130,
        "low":   [99.5]  * 130, "close": [100.0] * 130,
    })
    out = detect_inverted_cup_and_handle(df_flat)
    # Flat low/close means rim_low ~= cup_high, cup_height ~= 0 <10% -> REJECTED
    assert out.get("inverted_cup_handle_detected") is False


def test_batch686_producer_rejects_asymmetric_rims():
    """Pin (4): rim_diff must be <5% of rim_low for symmetric rims."""
    from backtest.signals.chart_patterns import detect_inverted_cup_and_handle
    n = 130
    # Asymmetric rims: left at 90, right at 100, rim_diff=10% (>5pct threshold)
    lows = np.concatenate([
        np.full(n // 4, 90.0),                       # left rim low = 90
        np.linspace(95.0, 100.0, n // 2),            # middle (peak area)
        np.full(n - n // 4 - n // 2, 100.0),         # right rim low = 100
    ])
    highs = lows + 1.0
    closes = lows + 0.5
    # Ensure peak in middle
    closes[n // 4:3 * n // 4] = np.linspace(110.0, 110.0, n // 2)
    df = pd.DataFrame({
        "open": closes, "high": highs,
        "low": lows, "close": closes,
    })
    out = detect_inverted_cup_and_handle(df)
    assert out.get("inverted_cup_handle_detected") is False, (
        "B686: producer should reject when left rim_low + right rim_low differ by > 5%"
    )


# ============ Strategy wiring (3 pins) ============

def test_batch686_strat_inverted_cup_and_handle_short_importable():
    """Pin (5)."""
    from backtest.signals.screener import strat_inverted_cup_and_handle_short
    assert callable(strat_inverted_cup_and_handle_short)


def test_batch686_inverted_cup_and_handle_short_in_registry():
    """Pin (6)."""
    from backtest.signals.screener import ALL_STRATEGIES, strat_inverted_cup_and_handle_short
    assert ALL_STRATEGIES.get("inverted_cup_and_handle_short") is strat_inverted_cup_and_handle_short


def test_batch686_all_strategies_count_222():
    """Pin (7): 221 post-B685 + 1 B686 Class 7 NEW = 222."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 222, (
        f"B686 strategy count drift: expected 222 (221 post-B685 + 1 NEW); "
        f"got {len(ALL_STRATEGIES)}"
    )


# ============ Fire-logic (4 pins) ============

def test_batch686_fires_on_all_5_gates_true():
    """Pin (8): canonical SHORT fire when all 5 gates True."""
    from backtest.signals.screener import strat_inverted_cup_and_handle_short
    s = {
        "inverted_cup_handle_detected": True,
        "below_ema_200":                True,
        "vol_spike_2x":                 True,
        "below_ema_50":                 True,
        "rsi_14":                       50.0,  # > 30
    }
    out = strat_inverted_cup_and_handle_short(s)
    assert out["fires"] is True
    assert out["direction"] == "short"


def test_batch686_no_fire_without_below_ema_200():
    """Pin (9): B630 producer-additive default-False fail-safe; missing key -> no fire."""
    from backtest.signals.screener import strat_inverted_cup_and_handle_short
    s = {
        "inverted_cup_handle_detected": True,
        # below_ema_200 ABSENT (default False)
        "vol_spike_2x":                 True,
        "below_ema_50":                 True,
        "rsi_14":                       50.0,
    }
    out = strat_inverted_cup_and_handle_short(s)
    assert out["fires"] is False, (
        "B686 regression: SHORT fired without below_ema_200 (silent gap)"
    )


def test_batch686_no_fire_without_vol_spike_2x():
    """Pin (10): symmetric to CP-1 B278 forensic-fix; volume confirmation required."""
    from backtest.signals.screener import strat_inverted_cup_and_handle_short
    s = {
        "inverted_cup_handle_detected": True,
        "below_ema_200":                True,
        # vol_spike_2x ABSENT
        "below_ema_50":                 True,
        "rsi_14":                       50.0,
    }
    assert strat_inverted_cup_and_handle_short(s)["fires"] is False


def test_batch686_no_fire_when_rsi_at_or_below_30():
    """Pin (11): rsi_14 > 30 strict-inequality; default-50 fail-safe (50>30 True).
    But explicit rsi <= 30 -> no fire (oversold; symmetric to CP-1's not-overbought)."""
    from backtest.signals.screener import strat_inverted_cup_and_handle_short
    # rsi=30 (at boundary - strict > so no fire)
    s = {
        "inverted_cup_handle_detected": True,
        "below_ema_200":                True,
        "vol_spike_2x":                 True,
        "below_ema_50":                 True,
        "rsi_14":                       30.0,
    }
    assert strat_inverted_cup_and_handle_short(s)["fires"] is False
    # rsi=25 (oversold) - no fire
    s["rsi_14"] = 25.0
    assert strat_inverted_cup_and_handle_short(s)["fires"] is False


# ============ Aggregator integration (1 pin) ============

def test_batch686_aggregator_invokes_inverted_cup_producer():
    """Pin (12): compute_all_chart_patterns includes detect_inverted_cup_and_handle."""
    from backtest.signals.chart_patterns import compute_all_chart_patterns
    # Build a 130-bar synthetic DataFrame (enough for 120-bar lookback)
    n = 130
    np.random.seed(42)
    closes = 100.0 + np.cumsum(np.random.normal(0, 0.5, n))
    df = pd.DataFrame({
        "open":  closes,
        "high":  closes + 0.5,
        "low":   closes - 0.5,
        "close": closes,
    })
    out = compute_all_chart_patterns(df)
    # Detection may be False on random data, but the KEY must be present
    # (producer was invoked + emitted the key as part of its dict).
    assert "inverted_cup_handle_detected" in out, (
        "B686: aggregator must invoke detect_inverted_cup_and_handle"
    )
