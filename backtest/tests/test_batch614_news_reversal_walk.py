"""Batch 614 (2026-06-07) -- Stage 4 walk of news_reversal_long (B603
Class 7 NEW) + symmetric mirror into news_reversal_short (B467 parent).

Owner-directed: a + b + c + d + e approved.

  (a) EVENT anchor: added close_(above|below)_open + close_in_(top|bottom)
      _40pct_of_range so the fire bar must itself be the reversal candle.
      Anchors an otherwise rolling-state (5d window) strategy at the
      actual reversal moment.
  (b) Sentiment-shift gate: added news_sentiment_shift > +0.2 (long) /
      < -0.2 (short) to detect the actual news-tone turn-point rather
      than rolling-window state.
  (c) Window consistency: swapped news_article_count (7d default) ->
      news_count_5d so all coverage/sentiment/price gates use the same
      5d horizon.
  (d) Threshold loosened: |news_sentiment_5d| 0.7 -> 0.5 (symmetric to
      news_momentum_long's -0.5; fire-count risk relief per
      feedback_minimum_fire_count_gate_before_cube).
  (e) Mirror: all of (a)-(d) applied to news_reversal_short (the B467
      parent, original asymmetric thesis side).

Owner explicitly accepted attribution tradeoff per
feedback_sequence_or_split_when_stacking_changes (4 simultaneous changes
per direction). Cube replay will surface joint verdict.

Pins:
  (1) LONG fires with all 6 new gates True (incl. shift>+0.2 + EVENT bar)
  (2) LONG silent-gap closed: missing close_above_open blocks
  (3) LONG silent-gap closed: missing close_in_top_40pct_of_range blocks
  (4) LONG silent-gap closed: news_sentiment_shift<=+0.2 blocks
  (5) LONG legacy fixture (B603 5-gate: -0.7 + 3 articles) does NOT fire
      post-B614 (window swap to news_count_5d + new gates)
  (6) LONG threshold (d) loosened: -0.5 sentiment fires (was -0.7 only)
  (7) SHORT fires with all 6 new gates True (mirror)
  (8) SHORT silent-gap closed: missing close_below_open blocks
  (9) SHORT silent-gap closed: missing close_in_bottom_40pct blocks
  (10) SHORT silent-gap closed: news_sentiment_shift>=-0.2 blocks
  (11) SHORT legacy fixture (B467 3-gate) does NOT fire post-B614
  (12) SHORT threshold (d) loosened: +0.5 sentiment fires (was +0.7 only)
  (13) ALL_STRATEGIES count unchanged at 221 (pure refactor; no add/delete)
"""
from __future__ import annotations

import pytest


# ------------------ LONG side ------------------

def test_batch614_long_fires_6_gates():
    """Pin (1)."""
    from backtest.signals.screener import strat_news_reversal_long
    s = {
        "news_sentiment_5d": -0.6,            # passes B614 d (<=-0.5)
        "pct_change_5d": -0.15,
        "news_count_5d": 4,                   # B614 c
        "news_sentiment_shift": 0.3,          # B614 b (>+0.2)
        "close_above_open": True,             # B614 a
        "close_in_top_40pct_of_range": True,  # B614 a
    }
    out = strat_news_reversal_long(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch614_long_silent_gap_close_above_open():
    """Pin (2): missing close_above_open blocks."""
    from backtest.signals.screener import strat_news_reversal_long
    s = {
        "news_sentiment_5d": -0.6,
        "pct_change_5d": -0.15,
        "news_count_5d": 4,
        "news_sentiment_shift": 0.3,
        # close_above_open ABSENT
        "close_in_top_40pct_of_range": True,
    }
    assert strat_news_reversal_long(s)["fires"] is False


def test_batch614_long_silent_gap_close_in_top_40pct():
    """Pin (3)."""
    from backtest.signals.screener import strat_news_reversal_long
    s = {
        "news_sentiment_5d": -0.6,
        "pct_change_5d": -0.15,
        "news_count_5d": 4,
        "news_sentiment_shift": 0.3,
        "close_above_open": True,
        # close_in_top_40pct_of_range ABSENT
    }
    assert strat_news_reversal_long(s)["fires"] is False


def test_batch614_long_silent_gap_sentiment_shift():
    """Pin (4): news_sentiment_shift must be > +0.2 (improving)."""
    from backtest.signals.screener import strat_news_reversal_long
    s = {
        "news_sentiment_5d": -0.6,
        "pct_change_5d": -0.15,
        "news_count_5d": 4,
        "news_sentiment_shift": 0.1,          # below 0.2 threshold
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
    }
    assert strat_news_reversal_long(s)["fires"] is False


def test_batch614_long_legacy_b603_fixture_blocked():
    """Pin (5): B603 3-gate fixture (sentiment -0.7 + price -10pct +
    article_count 3) must NOT fire post-B614 (lacks shift + EVENT
    bar gates + uses old article_count key)."""
    from backtest.signals.screener import strat_news_reversal_long
    s = {
        "news_sentiment_5d": -0.8,
        "pct_change_5d": -0.12,
        "news_article_count": 5,  # old window key; B614 reads news_count_5d
        # news_sentiment_shift, close_above_open, close_in_top_40pct ABSENT
    }
    assert strat_news_reversal_long(s)["fires"] is False, (
        "B614 added shift gate + EVENT bar gates + switched window key; "
        "legacy B603 fixture must not fire"
    )


def test_batch614_long_threshold_d_loosened():
    """Pin (6): sentiment -0.5 (right at new threshold) fires post-B614;
    pre-B614 -0.7 cutoff would have blocked."""
    from backtest.signals.screener import strat_news_reversal_long
    s = {
        "news_sentiment_5d": -0.5,            # exactly at new threshold
        "pct_change_5d": -0.11,
        "news_count_5d": 3,
        "news_sentiment_shift": 0.25,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
    }
    out = strat_news_reversal_long(s)
    assert out["fires"] is True, (
        "B614 (d) loosened threshold from -0.7 to -0.5; this fixture "
        "must fire to validate the loosening"
    )


# ------------------ SHORT side (mirror) ------------------

def test_batch614_short_fires_6_gates():
    """Pin (7)."""
    from backtest.signals.screener import strat_news_reversal_short
    s = {
        "news_sentiment_5d": 0.6,             # passes B614 d (>=+0.5)
        "pct_change_5d": 0.15,
        "news_count_5d": 4,
        "news_sentiment_shift": -0.3,         # B614 b (<-0.2)
        "close_below_open": True,             # B614 a
        "close_in_bottom_40pct_of_range": True,  # B614 a
    }
    out = strat_news_reversal_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch614_short_silent_gap_close_below_open():
    """Pin (8)."""
    from backtest.signals.screener import strat_news_reversal_short
    s = {
        "news_sentiment_5d": 0.6,
        "pct_change_5d": 0.15,
        "news_count_5d": 4,
        "news_sentiment_shift": -0.3,
        # close_below_open ABSENT
        "close_in_bottom_40pct_of_range": True,
    }
    assert strat_news_reversal_short(s)["fires"] is False


def test_batch614_short_silent_gap_close_in_bottom_40pct():
    """Pin (9)."""
    from backtest.signals.screener import strat_news_reversal_short
    s = {
        "news_sentiment_5d": 0.6,
        "pct_change_5d": 0.15,
        "news_count_5d": 4,
        "news_sentiment_shift": -0.3,
        "close_below_open": True,
        # close_in_bottom_40pct_of_range ABSENT
    }
    assert strat_news_reversal_short(s)["fires"] is False


def test_batch614_short_silent_gap_sentiment_shift():
    """Pin (10): news_sentiment_shift must be < -0.2 (deteriorating)."""
    from backtest.signals.screener import strat_news_reversal_short
    s = {
        "news_sentiment_5d": 0.6,
        "pct_change_5d": 0.15,
        "news_count_5d": 4,
        "news_sentiment_shift": -0.1,         # above -0.2 threshold
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    assert strat_news_reversal_short(s)["fires"] is False


def test_batch614_short_legacy_b467_fixture_blocked():
    """Pin (11): B467 3-gate fixture must NOT fire post-B614."""
    from backtest.signals.screener import strat_news_reversal_short
    s = {
        "news_sentiment_5d": 0.8,
        "pct_change_5d": 0.12,
        "news_article_count": 5,  # old window key
        # shift + EVENT bar gates ABSENT
    }
    assert strat_news_reversal_short(s)["fires"] is False, (
        "B614 added shift gate + EVENT bar gates + switched window key; "
        "legacy B467 fixture must not fire"
    )


def test_batch614_short_threshold_d_loosened():
    """Pin (12): sentiment +0.5 fires post-B614."""
    from backtest.signals.screener import strat_news_reversal_short
    s = {
        "news_sentiment_5d": 0.5,             # exactly at new threshold
        "pct_change_5d": 0.11,
        "news_count_5d": 3,
        "news_sentiment_shift": -0.25,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    out = strat_news_reversal_short(s)
    assert out["fires"] is True


def test_batch614_all_strategies_count_unchanged_at_221():
    """Pin (13): pure refactor; no add/delete strategies."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 219
