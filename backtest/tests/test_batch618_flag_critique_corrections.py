"""Batch 618 (2026-06-07) -- 3rd external-AI critique corrections on B607
walk (flag_bull_retest_long) per CHECKLIST #105 (k)/(l)/(m)/(n) extensions
codified in B617.

Critique findings + B618 actions:

  #1 (breakout-occurred gate buried in helper logic):
      Producer DOES check broke = any(close > breakout_level) but the
      strategy docstring didn't surface it as first-class. B618 lifts
      the breakout-occurred condition into the docstring's "FIRST-CLASS
      REQUIREMENTS" enumeration with PIT-discipline note.

  #2 (lookahead/PIT risk - flag window + retest window overlap):
      FACTUALLY INCORRECT on the code - the producer uses
      df.iloc[:n - K] historical slice so flag_high is computed over a
      window strictly BEFORE the breakout/retest window. B618 adds
      regression test pinning the PIT discipline so a future refactor
      can't silently break it.

  #4 (bear flag economic symmetry):
      Per CHECKLIST #105 (m) codified in B617 - structural symmetry
      does NOT imply economic symmetry. B618 adds explicit note in
      strat_flag_bear_retest_short docstring; cube must validate the
      SHORT independently rather than assume LONG's hit-rate.

  #5 (~70% Bulkowski win-rate citation):
      Bulkowski stats are definition-sensitive. B618 adds caveat to
      child docstring: edge must be validated empirically by backtest,
      not assumed from textbook.

  #6 ("high-tight flag" mislabeling):
      detect_flag defaults are +10% pole / <5% flag - this is a
      STANDARD flag, NOT classic Weinstein high-tight (>=90% pole).
      B618 renames description text in strat_flag_bull_long.

  #8 (parent strat_flag_bull_long phantom-breakout - MOST IMPORTANT):
      Pre-B618 parent fired on flag_bull_detected + EMA-200, but
      flag_bull_detected fires the day the flag COMPLETES - the flag
      window INCLUDES today's bar, so today's close <= flag_high by
      construction. No breakout could have occurred yet. B618 fix:
      added flag_bull_broke (+ flag_bear_broke) producer signal that
      detects a flag K bars ago (K in 1..8) + verifies today's close
      strictly exceeds the historical flag_high. Parent rewired to
      use flag_bull_broke.

Pins:
  (1) producer emits flag_bull_broke + flag_bear_broke keys
  (2) PIT-discipline: flag_high is computed STRICTLY BEFORE the
      breakout window - no contamination by breakout-bar's own high
  (3) PIT-discipline: producer signal does NOT fire when today's close
      is exactly equal to flag_high (strict-greater-than)
  (4) flag_bull_broke fires when flag completed K bars ago + today's
      close > historical flag_high
  (5) flag_bull_broke does NOT fire when today's close <= historical
      flag_high (the phantom-breakout case B618 fixes)
  (6) flag_bear_broke mirrors flag_bull_broke
  (7) parent strat_flag_bull_long fires with flag_bull_broke (post-B618)
  (8) parent strat_flag_bull_long does NOT fire on flag_bull_detected
      alone (the phantom-breakout case pre-B618 fired but shouldn't have)
  (9) child strat_flag_bull_retest_long unchanged (B607 4-gate set
      preserved; B618 is docstring + parent fix only for the children)
  (10) child strat_flag_bear_retest_short unchanged
  (11) ALL_STRATEGIES count unchanged at 222 (B618 is pure refactor +
       additive producer + docstring; no strategy add/delete)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _build_df(closes, highs, lows, opens=None, volumes=None):
    n = len(closes)
    if opens is None:
        opens = closes[:]
    if volumes is None:
        volumes = [1_000_000] * n
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    }, index=pd.date_range("2024-01-01", periods=n))


def _build_bull_flag_with_breakout(K_bars_ago: int):
    """Construct OHLCV data with a clean bull flag that completed K bars
    ago and a current bar that has broken above the flag-high.

    Structure (left to right):
      - 5 prefix bars (settling)
      - 20-bar pole rising 100 -> 115 (>10pct move)
      - 10-bar flag consolidating between 113-115 (<5pct pullback)
      - K_bars_ago more bars trending up from 115 -> 120 (post-breakout)
    Today's close = 120, well above flag_high ~ 115. Should trigger
    flag_bull_broke at K_bars_ago.
    """
    closes = []
    highs = []
    lows = []
    # 5 prefix
    closes += [99.0, 99.5, 100.0, 100.0, 100.0]
    highs  += [c + 0.5 for c in closes[-5:]]
    lows   += [c - 0.5 for c in closes[-5:]]
    # 20-bar pole 100 -> 115
    for i in range(20):
        c = 100.0 + (15.0 * (i + 1) / 20)
        closes.append(c)
        highs.append(c + 0.4)
        lows.append(c - 0.4)
    # 10-bar flag: tight range 113-115 (~1.7pct pullback)
    flag_vals = [115.0, 114.5, 114.0, 113.8, 114.0, 114.2, 114.0, 113.9, 114.1, 114.2]
    for c in flag_vals:
        closes.append(c)
        highs.append(min(115.0, c + 0.4))
        lows.append(max(113.0, c - 0.4))
    # K_bars_ago post-flag bars trending up to 120
    for i in range(K_bars_ago):
        c = 115.0 + (5.0 * (i + 1) / max(K_bars_ago, 1))
        closes.append(c)
        highs.append(c + 0.4)
        lows.append(c - 0.4)
    return _build_df(closes, highs, lows)


def test_batch618_producer_emits_new_breakout_keys():
    """Pin (1)."""
    from backtest.signals.chart_patterns import compute_flag_break_retest_signals
    df = _build_bull_flag_with_breakout(K_bars_ago=2)
    out = compute_flag_break_retest_signals(df)
    assert "flag_bull_broke" in out, "B618 producer must emit flag_bull_broke"
    assert "flag_bear_broke" in out, "B618 producer must emit flag_bear_broke"


def test_batch618_pit_discipline_no_overlap():
    """Pin (2): PIT discipline regression test per critique #2.

    Hand-construct a case where the flag_high WOULD be contaminated by
    the breakout bar's high IF the producer's slicing were wrong. The
    producer must use df.iloc[:n - K] so the flag window excludes the
    breakout bar entirely.

    Construction: flag forms in bars [n-K-10, n-K), flat at ~114. Then
    bar n-K is a HUGE green candle with high = 130 (the breakout bar).
    If the producer's slicing leaks - including bar n-K in the flag
    window - flag_high would be 130 instead of ~115, and the broke
    check (close > flag_high) would FAIL for the modest current close
    at 120. If the slicing is correct, flag_high stays ~115 and
    flag_bull_broke fires correctly.
    """
    from backtest.signals.chart_patterns import compute_flag_break_retest_signals
    # 5 prefix + 20 pole + 10 flag + breakout (n-K) + 1 settling bar (today)
    closes = []
    highs = []
    lows = []
    # Prefix + pole
    closes += [99.0, 99.5, 100.0, 100.0, 100.0]
    highs  += [c + 0.5 for c in closes[-5:]]
    lows   += [c - 0.5 for c in closes[-5:]]
    for i in range(20):
        c = 100.0 + (15.0 * (i + 1) / 20)
        closes.append(c)
        highs.append(c + 0.4)
        lows.append(c - 0.4)
    # Flag (10 bars, tight near 114)
    for c_val in [115.0, 114.5, 114.0, 113.8, 114.0, 114.2, 114.0, 113.9, 114.1, 114.2]:
        closes.append(c_val)
        highs.append(min(115.0, c_val + 0.4))
        lows.append(max(113.0, c_val - 0.4))
    # BREAKOUT BAR with HUGE high (would contaminate if slicing wrong)
    closes.append(125.0)
    highs.append(130.0)        # <-- the contamination point
    lows.append(120.0)
    # Today's bar (n-1): close at 120, below the breakout bar's high
    # of 130 but above the legitimate flag_high of ~115
    closes.append(120.0)
    highs.append(121.0)
    lows.append(119.0)
    df = _build_df(closes, highs, lows)

    out = compute_flag_break_retest_signals(df)
    # If PIT discipline holds, flag_high ~ 115 (from the flag bars only)
    # and today's close 120 > 115 -> fires.
    # If slicing leaks, flag_high gets the 130 high -> 120 < 130 -> no fire.
    assert out["flag_bull_broke"] is True, (
        "B618 PIT-discipline regression: flag-detection slice must "
        "EXCLUDE the breakout bar (bar n-K). If this assertion fails, "
        "df.iloc[:n - K] slicing in compute_flag_break_retest_signals "
        "is leaking the breakout bar's high into flag_high."
    )


def test_batch618_strict_greater_than_breakout():
    """Pin (3): producer uses STRICTLY greater than (today_close >
    flag_high), not >=. At-equality case should NOT fire."""
    from backtest.signals.chart_patterns import compute_flag_break_retest_signals
    # Construct a case where today's close is EXACTLY at the historical
    # flag_high. Set today_close = 115.0 (the flag_high).
    closes = []
    highs = []
    lows = []
    closes += [99.0, 99.5, 100.0, 100.0, 100.0]
    highs  += [c + 0.5 for c in closes[-5:]]
    lows   += [c - 0.5 for c in closes[-5:]]
    for i in range(20):
        c = 100.0 + (15.0 * (i + 1) / 20)
        closes.append(c)
        highs.append(c + 0.4)
        lows.append(c - 0.4)
    # Flag with high exactly = 115
    for c_val in [115.0, 114.5, 114.0, 113.8, 114.0, 114.2, 114.0, 113.9, 114.1, 114.2]:
        closes.append(c_val)
        highs.append(min(115.0, c_val + 0.4))
        lows.append(max(113.0, c_val - 0.4))
    # Today's close == 115 (exact equality)
    closes.append(115.0)
    highs.append(115.4)
    lows.append(114.6)
    df = _build_df(closes, highs, lows)
    out = compute_flag_break_retest_signals(df)
    assert out["flag_bull_broke"] is False, (
        "B618 strict-greater-than convention: today's close == flag_high "
        "must NOT fire (not a breakout, just touching the level)"
    )


def test_batch618_flag_bull_broke_fires_on_clean_breakout():
    """Pin (4)."""
    from backtest.signals.chart_patterns import compute_flag_break_retest_signals
    df = _build_bull_flag_with_breakout(K_bars_ago=3)
    out = compute_flag_break_retest_signals(df)
    assert out["flag_bull_broke"] is True


def test_batch618_flag_bull_broke_blocked_when_close_below_flag_high():
    """Pin (5): phantom-breakout case - flag detected but today's close
    is still BELOW the historical flag_high. Must NOT fire."""
    from backtest.signals.chart_patterns import compute_flag_break_retest_signals
    # Construct flag + today's close still BELOW flag_high
    closes = []
    highs = []
    lows = []
    closes += [99.0, 99.5, 100.0, 100.0, 100.0]
    highs  += [c + 0.5 for c in closes[-5:]]
    lows   += [c - 0.5 for c in closes[-5:]]
    for i in range(20):
        c = 100.0 + (15.0 * (i + 1) / 20)
        closes.append(c)
        highs.append(c + 0.4)
        lows.append(c - 0.4)
    # Flag with high ~ 115
    for c_val in [115.0, 114.5, 114.0, 113.8, 114.0, 114.2, 114.0, 113.9, 114.1, 114.2]:
        closes.append(c_val)
        highs.append(min(115.0, c_val + 0.4))
        lows.append(max(113.0, c_val - 0.4))
    # Today's bar: close at 113 (BELOW flag_high) - phantom-breakout case
    closes.append(113.0)
    highs.append(113.5)
    lows.append(112.5)
    df = _build_df(closes, highs, lows)
    out = compute_flag_break_retest_signals(df)
    assert out["flag_bull_broke"] is False, (
        "B618 phantom-breakout fix: flag detected but today's close "
        "below flag_high must NOT fire (pre-B618 strat_flag_bull_long "
        "would have fired in this case via flag_bull_detected + EMA-200)"
    )


def test_batch618_flag_bear_broke_mirror():
    """Pin (6): bear flag mirror."""
    from backtest.signals.chart_patterns import compute_flag_break_retest_signals
    closes = []
    highs = []
    lows = []
    # Prefix high
    closes += [120.0, 120.0, 119.5, 120.0, 120.0]
    highs  += [c + 0.5 for c in closes[-5:]]
    lows   += [c - 0.5 for c in closes[-5:]]
    # Bear pole: 120 -> 105 (drop ~12.5pct)
    for i in range(20):
        c = 120.0 - (15.0 * (i + 1) / 20)
        closes.append(c)
        highs.append(c + 0.4)
        lows.append(c - 0.4)
    # Bear flag: tight range near 105-107 (~2pct pullback)
    for c_val in [105.0, 105.5, 106.0, 106.2, 106.0, 105.8, 106.0, 106.1, 105.9, 105.8]:
        closes.append(c_val)
        highs.append(min(107.0, c_val + 0.4))
        lows.append(max(105.0, c_val - 0.4))
    # 3 post-flag bars trending down to ~100 (below flag_low = 105)
    for c in [102.0, 101.0, 100.0]:
        closes.append(c)
        highs.append(c + 0.4)
        lows.append(c - 0.4)
    df = _build_df(closes, highs, lows)
    out = compute_flag_break_retest_signals(df)
    assert out["flag_bear_broke"] is True


def test_batch618_parent_strat_flag_bull_long_requires_broke_signal():
    """Pin (7): post-B618 parent fires when flag_bull_broke is True."""
    from backtest.signals.screener import strat_flag_bull_long
    s = {
        "flag_bull_broke": True,
        "price_above_ema_200": True,
    }
    out = strat_flag_bull_long(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch618_parent_phantom_breakout_no_fire():
    """Pin (8): KEY phantom-breakout pin - pre-B618 the parent fired
    on flag_bull_detected + EMA-200 with NO breakout verification.
    Post-B618 with only flag_bull_detected True (no flag_bull_broke),
    the strategy must NOT fire."""
    from backtest.signals.screener import strat_flag_bull_long
    s = {
        "flag_bull_detected": True,       # pre-B618 sufficient signal
        "price_above_ema_200": True,
        # flag_bull_broke ABSENT - phantom-breakout case
    }
    out = strat_flag_bull_long(s)
    assert out["fires"] is False, (
        "B618 phantom-breakout fix: strat_flag_bull_long must NOT fire "
        "on flag_bull_detected alone (today's close is still inside "
        "or below the flag by construction). Requires flag_bull_broke."
    )


def test_batch618_child_strat_flag_bull_retest_long_unchanged():
    """Pin (9): B618 is docstring + parent fix only; the retest child
    behavior is unchanged from B607."""
    from backtest.signals.screener import strat_flag_bull_retest_long
    s = {
        "flag_bull_break_retest_long": True,
        "price_above_ema_200": True,
        "close_above_open": True,
        "vol_below_avg": True,
    }
    out = strat_flag_bull_retest_long(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch618_child_strat_flag_bear_retest_short_unchanged():
    """Pin (10)."""
    from backtest.signals.screener import strat_flag_bear_retest_short
    s = {
        "flag_bear_break_retest_short": True,
        "below_ema_200": True,
        "close_below_open": True,
        "vol_below_avg": True,
    }
    out = strat_flag_bear_retest_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch618_all_strategies_count_unchanged_at_222():
    """Pin (11): B618 is pure refactor + additive producer + docstring;
    no strategy add/delete."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 222
