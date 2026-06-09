"""Batch 643 (2026-06-09) -- W5 strat_pivot_s3_capitulation redesign per
owner directive option C from B640 walk bundle external-AI audit +
B641 fire-count measurement FAIL_FIRE_STARVED finding.

PRE-B643: strat_pivot_s3_capitulation fired SAME bar as the three
capitulation conditions (near_s3 + rsi<30 + vol_spike_2x). Pure
knife-catch by construction; measured 14.7/yr universe-wide.

POST-B643 (this batch): DECOUPLES detection from entry.
  (1) NEW producer `compute_capitulation_lookback` in technical.py
      emits `recent_capitulation_at_s3` = True when the capitulation
      conditions held on ANY of the last 5 bars (inclusive of today).
  (2) Strategy fires LONG when `recent_capitulation_at_s3` AND
      a reversal trigger today: bullish_engulfing OR hammer OR
      above_prev_high (key reversal bar).

Class 7 NEW mirror `strat_pivot_r3_blowoff_short` deferred pending
W5 fire-count + edge validation post-B643.

Pins:
  (1)  compute_capitulation_lookback importable + signature
  (2)  returns {} on insufficient history (<200 bars)
  (3)  emits recent_capitulation_at_s3 + capitulation_lookback_window
  (4)  recent_capitulation_at_s3 = True when capitulation event
       happened on bar -1 (today)
  (5)  recent_capitulation_at_s3 = True when capitulation event
       happened 3 bars ago (within 5-bar window)
  (6)  recent_capitulation_at_s3 = False when capitulation event
       happened 6 bars ago (outside 5-bar window)
  (7)  recent_capitulation_at_s3 = False on a normal price series
       (no capitulation conditions ever met)
  (8)  strategy fires when recent_capitulation_at_s3 AND
       bullish_engulfing
  (9)  strategy fires when recent_capitulation_at_s3 AND hammer
  (10) strategy fires when recent_capitulation_at_s3 AND
       above_prev_high
  (11) strategy DOES NOT fire when recent_capitulation_at_s3 but no
       reversal trigger today (closes the knife-catch pattern)
  (12) strategy DOES NOT fire on the pre-B643 conditions
       (rsi<30 + vol_spike_2x same bar without reversal trigger)
  (13) strategy DOES NOT fire when no recent capitulation but
       reversal trigger fires today (need BOTH gates)
  (14) producer registered in compute_all_signals output
  (15) registry: pivot_s3_capitulation present, strategy callable
  (16) regime affinity unchanged ({neutral, bear, crisis})
  (17) total strategy count unchanged at 221
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _make_normal_series(n: int = 220) -> pd.DataFrame:
    """Quiet uptrend with no capitulation conditions."""
    close = np.linspace(100.0, 110.0, n)
    high = close + 0.5
    low = close - 0.5
    open_ = close.copy()
    volume = np.full(n, 1e6)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=pd.date_range("2020-01-01", periods=n, freq="D"),
    )


def _inject_capitulation_at_bar(df: pd.DataFrame, bar_offset_from_end: int) -> pd.DataFrame:
    """Modify the dataframe so the bar at index (len-1-offset) satisfies
    all three pre-B643 capitulation conditions: near pivot S3 (computed
    from prev-bar HLC) + RSI<30 + volume spike >= 2x. We do this by:
      - Driving close down sharply for ~20 bars BEFORE the capitulation
        bar (so RSI<30)
      - Making the capitulation bar's close coincide with prev-bar S3
      - Spiking the capitulation bar's volume (>= 2.5x of avg of bars
        before it)
    """
    df = df.copy()
    cap_idx = len(df) - 1 - bar_offset_from_end
    # Decline last 20-ish bars to push RSI < 30
    decline_start = max(cap_idx - 20, 0)
    for i in range(decline_start, cap_idx + 1):
        # Steep descent into the capitulation bar
        progress = (i - decline_start) / max(cap_idx - decline_start, 1)
        df.iloc[i, df.columns.get_loc("close")] = 110.0 - progress * 40.0
        df.iloc[i, df.columns.get_loc("high")] = df.iloc[i]["close"] + 0.3
        df.iloc[i, df.columns.get_loc("low")] = df.iloc[i]["close"] - 0.3
        df.iloc[i, df.columns.get_loc("open")] = df.iloc[i]["close"] + 0.1
    # Capitulation bar: place close at prev-bar S3
    if cap_idx >= 1:
        prev = df.iloc[cap_idx - 1]
        h, l, c = prev["high"], prev["low"], prev["close"]
        pivot = (h + l + c) / 3
        s3 = l - 2 * (h - pivot)
        # Set capitulation-bar close very close to S3 (within 0.1%)
        df.iloc[cap_idx, df.columns.get_loc("close")] = float(s3)
        df.iloc[cap_idx, df.columns.get_loc("low")] = float(s3) - 0.5
        df.iloc[cap_idx, df.columns.get_loc("high")] = float(s3) + 1.0
        # Volume spike
        avg_vol_recent = float(df["volume"].iloc[max(cap_idx - 20, 0):cap_idx].mean())
        df.iloc[cap_idx, df.columns.get_loc("volume")] = avg_vol_recent * 4.0
    return df


# =================== Producer pins ===================

def test_batch643_producer_importable():
    """Pin (1)."""
    from backtest.signals.technical import compute_capitulation_lookback
    assert callable(compute_capitulation_lookback)


def test_batch643_producer_returns_empty_on_short_history():
    """Pin (2)."""
    from backtest.signals.technical import compute_capitulation_lookback
    df = _make_normal_series(n=50)  # < 200 bars
    out = compute_capitulation_lookback(df)
    assert out == {}


def test_batch643_producer_emits_keys():
    """Pin (3)."""
    from backtest.signals.technical import compute_capitulation_lookback
    df = _make_normal_series(n=220)
    out = compute_capitulation_lookback(df)
    assert "recent_capitulation_at_s3" in out
    assert "capitulation_lookback_window" in out
    assert out["capitulation_lookback_window"] == 5


def test_batch643_recent_capitulation_true_when_bar_is_today():
    """Pin (4): capitulation event on today's bar -> True."""
    from backtest.signals.technical import compute_capitulation_lookback
    df = _inject_capitulation_at_bar(_make_normal_series(220), bar_offset_from_end=0)
    out = compute_capitulation_lookback(df)
    assert out["recent_capitulation_at_s3"] is True


def test_batch643_recent_capitulation_true_within_5_bar_window():
    """Pin (5): capitulation event 3 bars ago -> True."""
    from backtest.signals.technical import compute_capitulation_lookback
    df = _inject_capitulation_at_bar(_make_normal_series(220), bar_offset_from_end=3)
    out = compute_capitulation_lookback(df)
    assert out["recent_capitulation_at_s3"] is True


def test_batch643_recent_capitulation_false_outside_window():
    """Pin (6): capitulation event 6 bars ago -> outside 5-bar window
    -> False."""
    from backtest.signals.technical import compute_capitulation_lookback
    df = _inject_capitulation_at_bar(_make_normal_series(220), bar_offset_from_end=6)
    out = compute_capitulation_lookback(df)
    assert out["recent_capitulation_at_s3"] is False


def test_batch643_recent_capitulation_false_on_normal_series():
    """Pin (7): quiet uptrend with no capitulation -> False."""
    from backtest.signals.technical import compute_capitulation_lookback
    df = _make_normal_series(220)
    out = compute_capitulation_lookback(df)
    assert out["recent_capitulation_at_s3"] is False


# =================== Strategy pins ===================

def test_batch643_strategy_fires_with_bullish_engulfing():
    """Pin (8): recent_capitulation + bullish_engulfing + vol_below_avg
    (B650) -> fires LONG."""
    from backtest.signals.screener import strat_pivot_s3_capitulation
    s = {"recent_capitulation_at_s3": True, "vol_below_avg": True,
         "bullish_engulfing": True}
    out = strat_pivot_s3_capitulation(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch643_strategy_fires_with_hammer():
    """Pin (9)."""
    from backtest.signals.screener import strat_pivot_s3_capitulation
    s = {"recent_capitulation_at_s3": True, "vol_below_avg": True,
         "hammer": True}
    out = strat_pivot_s3_capitulation(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch643_strategy_fires_with_above_prev_high():
    """Pin (10)."""
    from backtest.signals.screener import strat_pivot_s3_capitulation
    s = {"recent_capitulation_at_s3": True, "vol_below_avg": True,
         "above_prev_high": True}
    out = strat_pivot_s3_capitulation(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch650_strategy_blocked_without_vol_below_avg():
    """B650: Wyckoff Spring requires LOW-volume Test bar. Without
    vol_below_avg, the dead-cat-bounce on heavy distribution volume
    is NOT a valid Spring -- strategy must NOT fire."""
    from backtest.signals.screener import strat_pivot_s3_capitulation
    s = {"recent_capitulation_at_s3": True, "bullish_engulfing": True,
         "hammer": True, "above_prev_high": True}
    # All reversal triggers True but vol_below_avg missing -> no fire
    assert strat_pivot_s3_capitulation(s)["fires"] is False


def test_batch643_strategy_blocked_without_reversal_trigger():
    """Pin (11): the redesign's core property -- recent capitulation
    alone is NOT enough to fire; need a reversal trigger today.
    Closes the knife-catch pattern."""
    from backtest.signals.screener import strat_pivot_s3_capitulation
    s = {"recent_capitulation_at_s3": True}
    # No bullish_engulfing, hammer, above_prev_high
    assert strat_pivot_s3_capitulation(s)["fires"] is False


def test_batch643_strategy_blocked_on_pre_b643_conditions_alone():
    """Pin (12): the old gates (rsi<30 + vol_spike_2x) alone no longer
    fire -- only recent_capitulation_at_s3 + reversal_trigger does."""
    from backtest.signals.screener import strat_pivot_s3_capitulation
    s = {"near_s3": True, "rsi_14": 25, "vol_spike_2x": True}
    # Old gates set but no recent_capitulation_at_s3 (different key)
    assert strat_pivot_s3_capitulation(s)["fires"] is False


def test_batch643_strategy_blocked_without_recent_capitulation():
    """Pin (13): a reversal-trigger candle WITHOUT a recent capitulation
    event does NOT fire (need BOTH gates -- avoid false positives on
    routine reversal candles in non-stressed markets)."""
    from backtest.signals.screener import strat_pivot_s3_capitulation
    s = {"bullish_engulfing": True, "hammer": True, "above_prev_high": True}
    # No recent_capitulation_at_s3
    assert strat_pivot_s3_capitulation(s)["fires"] is False


# =================== Wire-in + registry pins ===================

def test_batch643_producer_wired_in_compute_all_signals():
    """Pin (14)."""
    from backtest.signals.technical import compute_all_signals
    df = _make_normal_series(220)
    sig = compute_all_signals(df)
    assert "recent_capitulation_at_s3" in sig
    assert "capitulation_lookback_window" in sig


def test_batch643_strategy_registered_and_callable():
    """Pin (15)."""
    from backtest.signals.screener import ALL_STRATEGIES, strat_pivot_s3_capitulation
    assert "pivot_s3_capitulation" in ALL_STRATEGIES
    assert ALL_STRATEGIES["pivot_s3_capitulation"] is strat_pivot_s3_capitulation
    assert callable(strat_pivot_s3_capitulation)


def test_batch651_regime_affinity_expanded_all_regimes():
    """Pin (16): B651 expanded {neutral, bear, crisis} -> all regimes
    to fix the regime-transition blocking issue (B643 redesign buys
    the turn up to 5 days later -- regime may have transitioned by
    then; permissive entry preserves fires across the transition)."""
    from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY
    assert STRATEGY_REGIME_AFFINITY.get("pivot_s3_capitulation") == {
        "bull", "neutral", "bear", "crisis",
    }


def test_batch643_total_strategy_count():
    """Pin (17): B645 added W5 mirror -> 222."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 222
