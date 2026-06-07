"""Batch 616 (2026-06-07) -- systematic LOW-priority `not s.get(...)`
refactor sweep per CHECKLIST #105 a-j + feedback_never_use_NOT_s_get
_pattern + B612 producer-additive grep extension.

Owner-directed: Option (A) approved -- all 6 swaps across 5 strategies +
2 additive producer signals + strict-less-than convention.

Refactor table:
  1. strat_52wl_break_retest_short:
       not s.get(price_above_ema_200, True)  -> below_ema_200 (B609)
       not s.get(above_avwap_20high,  True)  -> below_avwap_20high (B612)
  2. strat_flag_bear_retest_short:
       not s.get(price_above_ema_200, True)  -> below_ema_200 (B609)
  3. strat_news_momentum_short:
       not s.get(above_avwap_20high,  True)  -> below_avwap_20high (B612)
  4. strat_turtle_soup_long:
       not s.get(below_prev_low,      True)  -> above_prev_low (B616 NEW)
  5. strat_turtle_soup_short:
       not s.get(above_prev_high,     True)  -> below_prev_high (B616 NEW)

Producer additions (technical.py:139):
  above_prev_low  = today > L  (strict-less-than convention; symmetric
                                to existing above_prev_high)
  below_prev_high = today < H  (symmetric to existing below_prev_low)

Per CHECKLIST #105 j producer-additive grep: only turtle_soup strategies
reference these new keys (as label strings, not .get() keys); no
conflicting consumers; no silent-gap risk.

Behavior preservation: pre-B616 `not s.get(..., True)` evaluated to
`today_close <= boundary` (inclusive equality). Post-B616 strict signal
evaluates to `today_close < boundary`. Empirically rare at-tick equality
difference; matches existing producer strict-greater-than convention.

Pins:
  (1) producer emits above_prev_low + below_prev_high keys
  (2) producer above_prev_low: today > L (strict)
  (3) producer below_prev_high: today < H (strict)
  (4) 52wl_break_retest_short fires with positive signals (below_ema_200
      + below_avwap_20high)
  (5) 52wl_break_retest_short silent-gap closed: missing below_ema_200
      key blocks (pre-B616 would have auto-passed via `not s.get(...,
      True)`)
  (6) 52wl_break_retest_short silent-gap closed: missing
      below_avwap_20high key blocks
  (7) flag_bear_retest_short fires with below_ema_200
  (8) flag_bear_retest_short silent-gap closed: missing below_ema_200
  (9) news_momentum_short fires with below_avwap_20high
  (10) news_momentum_short silent-gap closed: missing below_avwap_20high
  (11) turtle_soup_long fires with above_prev_low
  (12) turtle_soup_long silent-gap closed: missing above_prev_low
  (13) turtle_soup_short fires with below_prev_high
  (14) turtle_soup_short silent-gap closed: missing below_prev_high
  (15) ALL_STRATEGIES count unchanged at 222 (pure refactor + producer
       additive; no add/delete)
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


# ------------------ Producer pins ------------------

def test_batch616_producer_emits_new_keys():
    """Pin (1)."""
    from backtest.signals.technical import compute_pivots
    closes = [100.0, 101.0, 102.0, 101.5, 103.0]
    highs  = [100.5, 101.5, 102.5, 102.0, 103.5]
    lows   = [ 99.5, 100.5, 101.5, 101.0, 102.5]
    df = _build_df(closes, highs, lows)
    out = compute_pivots(df)
    assert "above_prev_low" in out, "B616 producer must emit above_prev_low"
    assert "below_prev_high" in out, "B616 producer must emit below_prev_high"


def test_batch616_producer_above_prev_low_strict():
    """Pin (2): today > L."""
    from backtest.signals.technical import compute_pivots
    # Today close (104) > prev_low (101) -> True
    df_true = _build_df(
        closes=[100.0, 101.0, 102.0, 101.5, 104.0],
        highs =[100.5, 101.5, 102.5, 102.0, 104.5],
        lows  =[ 99.5, 100.5, 101.5, 101.0, 103.5],
    )
    assert bool(compute_pivots(df_true)["above_prev_low"]) is True

    # Today close (100) < prev_low (101) -> False
    df_false = _build_df(
        closes=[100.0, 101.0, 102.0, 101.5, 100.0],
        highs =[100.5, 101.5, 102.5, 102.0, 100.5],
        lows  =[ 99.5, 100.5, 101.5, 101.0,  99.5],
    )
    assert bool(compute_pivots(df_false)["above_prev_low"]) is False


def test_batch616_producer_below_prev_high_strict():
    """Pin (3): today < H."""
    from backtest.signals.technical import compute_pivots
    # Today close (101) < prev_high (102.5) -> True
    df_true = _build_df(
        closes=[100.0, 101.0, 102.0, 102.5, 101.0],
        highs =[100.5, 101.5, 102.5, 103.0, 101.5],
        lows  =[ 99.5, 100.5, 101.5, 102.0, 100.5],
    )
    assert bool(compute_pivots(df_true)["below_prev_high"]) is True

    # Today close (104) > prev_high (102.5) -> False
    df_false = _build_df(
        closes=[100.0, 101.0, 102.0, 102.5, 104.0],
        highs =[100.5, 101.5, 102.5, 103.0, 104.5],
        lows  =[ 99.5, 100.5, 101.5, 102.0, 103.5],
    )
    assert bool(compute_pivots(df_false)["below_prev_high"]) is False


# ------------------ strat_52wl_break_retest_short ------------------

def test_batch616_52wl_break_retest_short_fires_positive_signals():
    """Pin (4)."""
    from backtest.signals.screener import strat_52wl_break_retest_short
    s = {
        "year_low_break_retest_short": True,
        "near_52w_low": True,
        "below_ema_200": True,           # B616 positive
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "vol_below_avg": True,
        "below_avwap_20high": True,      # B616 positive
    }
    out = strat_52wl_break_retest_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch616_52wl_break_retest_short_silent_gap_below_ema_200():
    """Pin (5): missing below_ema_200 key blocks (pre-B616 auto-passed)."""
    from backtest.signals.screener import strat_52wl_break_retest_short
    s = {
        "year_low_break_retest_short": True,
        "near_52w_low": True,
        # below_ema_200 ABSENT
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "vol_below_avg": True,
        "below_avwap_20high": True,
    }
    assert strat_52wl_break_retest_short(s)["fires"] is False


def test_batch616_52wl_break_retest_short_silent_gap_below_avwap_20high():
    """Pin (6)."""
    from backtest.signals.screener import strat_52wl_break_retest_short
    s = {
        "year_low_break_retest_short": True,
        "near_52w_low": True,
        "below_ema_200": True,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "vol_below_avg": True,
        # below_avwap_20high ABSENT
    }
    assert strat_52wl_break_retest_short(s)["fires"] is False


# ------------------ strat_flag_bear_retest_short ------------------

def test_batch616_flag_bear_retest_short_fires_positive():
    """Pin (7)."""
    from backtest.signals.screener import strat_flag_bear_retest_short
    s = {
        "flag_bear_break_retest_short": True,
        "below_ema_200": True,           # B616 positive
        "close_below_open": True,
        "vol_below_avg": True,
    }
    out = strat_flag_bear_retest_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch616_flag_bear_retest_short_silent_gap_closed():
    """Pin (8)."""
    from backtest.signals.screener import strat_flag_bear_retest_short
    s = {
        "flag_bear_break_retest_short": True,
        # below_ema_200 ABSENT
        "close_below_open": True,
        "vol_below_avg": True,
    }
    assert strat_flag_bear_retest_short(s)["fires"] is False


# ------------------ strat_news_momentum_short ------------------

def test_batch616_news_momentum_short_fires_positive():
    """Pin (9)."""
    from backtest.signals.screener import strat_news_momentum_short
    s = {
        "news_sentiment_5d": -0.7,
        "news_volume_zscore_5d": 2.0,
        "dc20_breakout_dn": True,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "vol_above_avg": True,
        "below_avwap_20high": True,      # B616 positive
    }
    out = strat_news_momentum_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch616_news_momentum_short_silent_gap_closed():
    """Pin (10)."""
    from backtest.signals.screener import strat_news_momentum_short
    s = {
        "news_sentiment_5d": -0.7,
        "news_volume_zscore_5d": 2.0,
        "dc20_breakout_dn": True,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "vol_above_avg": True,
        # below_avwap_20high ABSENT
    }
    assert strat_news_momentum_short(s)["fires"] is False


# ------------------ strat_turtle_soup_long ------------------

def test_batch616_turtle_soup_long_fires_positive():
    """Pin (11)."""
    from backtest.signals.screener import strat_turtle_soup_long
    s = {
        "smc_liquidity_swept_dn": True,
        "above_prev_low": True,          # B616 NEW positive
        "close_above_open": True,
    }
    out = strat_turtle_soup_long(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch616_turtle_soup_long_silent_gap_closed():
    """Pin (12): missing above_prev_low blocks (pre-B616 fixture lacking
    `below_prev_low` would have auto-passed `not s.get(below_prev_low,
    True)`)."""
    from backtest.signals.screener import strat_turtle_soup_long
    s = {
        "smc_liquidity_swept_dn": True,
        # above_prev_low ABSENT
        "close_above_open": True,
    }
    assert strat_turtle_soup_long(s)["fires"] is False


# ------------------ strat_turtle_soup_short ------------------

def test_batch616_turtle_soup_short_fires_positive():
    """Pin (13)."""
    from backtest.signals.screener import strat_turtle_soup_short
    s = {
        "smc_liquidity_swept_up": True,
        "below_prev_high": True,         # B616 NEW positive
        "close_below_open": True,
    }
    out = strat_turtle_soup_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch616_turtle_soup_short_silent_gap_closed():
    """Pin (14)."""
    from backtest.signals.screener import strat_turtle_soup_short
    s = {
        "smc_liquidity_swept_up": True,
        # below_prev_high ABSENT
        "close_below_open": True,
    }
    assert strat_turtle_soup_short(s)["fires"] is False


# ------------------ Registry pin ------------------

def test_batch616_all_strategies_count_unchanged_at_222():
    """Pin (15): pure refactor + additive producer; no add/delete."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 222
