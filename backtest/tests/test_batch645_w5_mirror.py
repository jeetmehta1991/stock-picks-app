"""Batch 645 (2026-06-09) -- Class 7 NEW strat_pivot_r3_blowoff_short
wired per owner directive (a) from B643+B644 W5 follow-on. Symmetric
mirror of B643-redesigned strat_pivot_s3_capitulation.

Per feedback_long_short_inverse_audit + feedback_wire_new_strategies
_on_the_spot. EXPECTANCY ASYMMETRY explicitly acknowledged per
feedback_structural_symmetry_not_economic_symmetry; both LONG and
SHORT marked EXPLORATORY pending Stage 5 cube validation.

Same 2-gate structure as W5:
  (1) recent_blowoff_at_r3 -- 5-bar lookback OR-composite of
      (near_r3 + rsi>70 + vol_spike_2x)
  (2) reversal-trigger today -- bearish_engulfing OR shooting_star
      OR below_prev_low

Pins:
  (1)  compute_blowoff_lookback importable + callable
  (2)  returns {} on insufficient history (<200 bars)
  (3)  emits recent_blowoff_at_r3 + blowoff_lookback_window keys
  (4)  recent_blowoff_at_r3 True when blowoff happened today
  (5)  recent_blowoff_at_r3 True within 5-bar window
  (6)  recent_blowoff_at_r3 False outside 5-bar window (6 bars ago)
  (7)  recent_blowoff_at_r3 False on normal price series
  (8)  strategy fires SHORT on recent_blowoff_at_r3 + bearish_engulfing
  (9)  strategy fires SHORT on recent_blowoff_at_r3 + shooting_star
  (10) strategy fires SHORT on recent_blowoff_at_r3 + below_prev_low
  (11) strategy DOES NOT fire on recent_blowoff_at_r3 alone (no reversal)
  (12) strategy DOES NOT fire on reversal-trigger alone (no blowoff)
  (13) producer registered in compute_all_signals output
  (14) strategy registered + callable in ALL_STRATEGIES
  (15) Strategy uses B291 SHORT default {bear, crisis, neutral} (no
       explicit regime entry)
  (16) Total strategy count 221 -> 222
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _make_normal_series(n: int = 220) -> pd.DataFrame:
    """Quiet uptrend; no blowoff conditions."""
    close = np.linspace(100.0, 110.0, n)
    high = close + 0.5
    low = close - 0.5
    open_ = close.copy()
    volume = np.full(n, 1e6)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=pd.date_range("2020-01-01", periods=n, freq="D"),
    )


def _inject_blowoff_at_bar(df: pd.DataFrame, bar_offset_from_end: int) -> pd.DataFrame:
    """Modify df so the bar at index (len-1-offset) satisfies all three
    blowoff conditions: near pivot R3 (computed from prev-bar HLC) +
    RSI>70 + volume spike >= 2x. Mirror of capitulation injection."""
    df = df.copy()
    blow_idx = len(df) - 1 - bar_offset_from_end
    # Run-up last 20 bars to push RSI > 70
    runup_start = max(blow_idx - 20, 0)
    for i in range(runup_start, blow_idx + 1):
        progress = (i - runup_start) / max(blow_idx - runup_start, 1)
        df.iloc[i, df.columns.get_loc("close")] = 100.0 + progress * 40.0
        df.iloc[i, df.columns.get_loc("high")] = df.iloc[i]["close"] + 0.3
        df.iloc[i, df.columns.get_loc("low")] = df.iloc[i]["close"] - 0.3
        df.iloc[i, df.columns.get_loc("open")] = df.iloc[i]["close"] - 0.1
    # Blowoff bar: place close at prev-bar R3
    if blow_idx >= 1:
        prev = df.iloc[blow_idx - 1]
        h, l, c = prev["high"], prev["low"], prev["close"]
        pivot = (h + l + c) / 3
        r3 = h + 2 * (pivot - l)
        df.iloc[blow_idx, df.columns.get_loc("close")] = float(r3)
        df.iloc[blow_idx, df.columns.get_loc("high")] = float(r3) + 0.5
        df.iloc[blow_idx, df.columns.get_loc("low")] = float(r3) - 1.0
        avg_vol_recent = float(df["volume"].iloc[max(blow_idx - 20, 0):blow_idx].mean())
        df.iloc[blow_idx, df.columns.get_loc("volume")] = avg_vol_recent * 4.0
    return df


# =================== Producer pins ===================

def test_batch645_producer_importable():
    """Pin (1)."""
    from backtest.signals.technical import compute_blowoff_lookback
    assert callable(compute_blowoff_lookback)


def test_batch645_producer_empty_on_short_history():
    """Pin (2)."""
    from backtest.signals.technical import compute_blowoff_lookback
    df = _make_normal_series(n=50)
    assert compute_blowoff_lookback(df) == {}


def test_batch645_producer_emits_keys():
    """Pin (3)."""
    from backtest.signals.technical import compute_blowoff_lookback
    out = compute_blowoff_lookback(_make_normal_series(220))
    assert "recent_blowoff_at_r3" in out
    assert "blowoff_lookback_window" in out
    assert out["blowoff_lookback_window"] == 5


def test_batch645_recent_blowoff_true_today():
    """Pin (4)."""
    from backtest.signals.technical import compute_blowoff_lookback
    df = _inject_blowoff_at_bar(_make_normal_series(220), bar_offset_from_end=0)
    assert compute_blowoff_lookback(df)["recent_blowoff_at_r3"] is True


def test_batch645_recent_blowoff_true_within_window():
    """Pin (5): 3 bars ago -> within 5-bar window."""
    from backtest.signals.technical import compute_blowoff_lookback
    df = _inject_blowoff_at_bar(_make_normal_series(220), bar_offset_from_end=3)
    assert compute_blowoff_lookback(df)["recent_blowoff_at_r3"] is True


def test_batch645_recent_blowoff_false_outside_window():
    """Pin (6): 6 bars ago -> outside 5-bar window."""
    from backtest.signals.technical import compute_blowoff_lookback
    df = _inject_blowoff_at_bar(_make_normal_series(220), bar_offset_from_end=6)
    assert compute_blowoff_lookback(df)["recent_blowoff_at_r3"] is False


def test_batch645_recent_blowoff_false_normal_series():
    """Pin (7)."""
    from backtest.signals.technical import compute_blowoff_lookback
    assert compute_blowoff_lookback(_make_normal_series(220))["recent_blowoff_at_r3"] is False


# =================== Strategy pins ===================

def test_batch645_strategy_fires_with_bearish_engulfing():
    """Pin (8). B659 update: added vol_below_avg AND-gate to W5m
    (Wyckoff Upthrust-Test); fixture extended."""
    from backtest.signals.screener import strat_pivot_r3_blowoff_short
    s = {
        "recent_blowoff_at_r3": True,
        "vol_below_avg": True,  # B659 W5m vol gate
        "bearish_engulfing": True,
    }
    out = strat_pivot_r3_blowoff_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch645_strategy_fires_with_shooting_star():
    """Pin (9). B659 fixture update."""
    from backtest.signals.screener import strat_pivot_r3_blowoff_short
    s = {
        "recent_blowoff_at_r3": True,
        "vol_below_avg": True,  # B659 W5m vol gate
        "shooting_star": True,
    }
    out = strat_pivot_r3_blowoff_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch645_strategy_fires_with_below_prev_low():
    """Pin (10). B659 fixture update."""
    from backtest.signals.screener import strat_pivot_r3_blowoff_short
    s = {
        "recent_blowoff_at_r3": True,
        "vol_below_avg": True,  # B659 W5m vol gate
        "below_prev_low": True,
    }
    out = strat_pivot_r3_blowoff_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch645_strategy_blocked_without_reversal():
    """Pin (11): blowoff window alone -> no fire (closes the spike-fade
    pattern symmetric to W5's knife-catch closure)."""
    from backtest.signals.screener import strat_pivot_r3_blowoff_short
    s = {"recent_blowoff_at_r3": True}
    assert strat_pivot_r3_blowoff_short(s)["fires"] is False


def test_batch645_strategy_blocked_without_blowoff():
    """Pin (12): reversal-trigger alone (no recent blowoff event) -> no
    fire. Avoids false positives on routine bearish candles."""
    from backtest.signals.screener import strat_pivot_r3_blowoff_short
    s = {"bearish_engulfing": True, "shooting_star": True, "below_prev_low": True}
    assert strat_pivot_r3_blowoff_short(s)["fires"] is False


# =================== Wire-in + registry pins ===================

def test_batch645_producer_in_compute_all_signals():
    """Pin (13)."""
    from backtest.signals.technical import compute_all_signals
    sig = compute_all_signals(_make_normal_series(220))
    assert "recent_blowoff_at_r3" in sig
    assert "blowoff_lookback_window" in sig


def test_batch645_strategy_registered_and_callable():
    """Pin (14)."""
    from backtest.signals.screener import ALL_STRATEGIES, strat_pivot_r3_blowoff_short
    assert "pivot_r3_blowoff_short" in ALL_STRATEGIES
    assert ALL_STRATEGIES["pivot_r3_blowoff_short"] is strat_pivot_r3_blowoff_short


def test_batch645_b291_short_default_applies():
    """Pin (15): no explicit regime entry; B291 direction-aware default
    SHORT -> {bear, crisis, neutral}; not in {bull}."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    assert "pivot_r3_blowoff_short" not in STRATEGY_REGIME_AFFINITY
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime(
            "pivot_r3_blowoff_short", r, direction="short"
        ) is True
    assert should_strategy_fire_in_regime(
        "pivot_r3_blowoff_short", "bull", direction="short"
    ) is False


def test_batch645_total_strategy_count_222():
    """Pin (16) B823 UPDATED: +1 Class 7 NEW; 221 -> 222 post-B645.
    Trajectory: B682-4 + B685+3 + B686+1 + B709+2 - B722-3 = 221 current."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 221
