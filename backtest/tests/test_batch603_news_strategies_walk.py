"""Batch 603 (2026-06-05) -- Stage 4 walk of news_momentum_long +
inverse audit additions per owner directives 2026-06-05.

Owner directives applied (answers a + b + c + f + g + h + i; j dropped
as contradictory):
  (a) Added close_above_open + close_in_top_40pct_of_range to
      news_momentum_long (B589-family standardization).
  (b) Added vol_above_avg to news_momentum_long (volume conviction).
  (c) Added above_avwap_20low to news_momentum_long (B597/B598/B601
      AVWAP family).
  (f) Preserved dc20_breakout_up in news_momentum_long (A/B test
      baseline; SMC twin will be built post-walks).
  (g) Added Class 7 NEW strat_news_momentum_short - symmetric inverse
      (negative-news-confirmed breakdown).
  (h) Added Class 7 NEW strat_news_reversal_long - symmetric inverse
      of news_reversal_short (fade negative-news overreaction).
  (i) Regime affinity: Batch 291 direction-aware default.

Pins:
  (1) news_momentum_long 7-gate fixture fires LONG
  (2) news_momentum_long legacy 3-gate fixture (post-B603) blocked
  (3) news_momentum_short 7-gate fixture fires SHORT
  (4) news_momentum_short symmetric to long (sentiment sign + DC dir +
      bar dir + close-in-bottom + AVWAP-below mirror)
  (5) news_reversal_long 3-gate fixture fires LONG
  (6) news_reversal_long symmetric to news_reversal_short (sentiment
      sign + pct_change sign mirror)
  (7) Regime defaults: long={bull, neutral}; short={bear, crisis, neutral}
  (8) ALL_STRATEGIES count = 219 (+2 from B603)
"""
from __future__ import annotations

import pytest


def test_batch603_news_momentum_long_7_gates_fires():
    """Pin (1)."""
    from backtest.signals.screener import strat_news_momentum_long
    s = {
        "news_sentiment_5d": 0.6,
        "news_volume_zscore_5d": 2.0,
        "dc20_breakout_up": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
        "vol_above_avg": True,
        "above_avwap_20low": True,
    }
    out = strat_news_momentum_long(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch603_news_momentum_long_legacy_3_gate_blocked():
    """Pin (2): legacy fixture (sentiment + zscore + dc20_breakout_up only)
    does NOT fire post-B603 due to 4 new required gates."""
    from backtest.signals.screener import strat_news_momentum_long
    s = {
        "news_sentiment_5d": 0.6,
        "news_volume_zscore_5d": 2.0,
        "dc20_breakout_up": True,
    }
    assert strat_news_momentum_long(s)["fires"] is False


def test_batch603_news_momentum_short_7_gates_fires():
    """Pin (3): symmetric inverse fires on negative-news-confirmed breakdown."""
    from backtest.signals.screener import strat_news_momentum_short
    s = {
        "news_sentiment_5d": -0.6,
        "news_volume_zscore_5d": 2.0,
        "dc20_breakout_dn": True,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "vol_above_avg": True,
        "above_avwap_20high": False,  # below the 20d swing-high AVWAP
    }
    out = strat_news_momentum_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch603_news_momentum_short_symmetric_with_long():
    """Pin (4): inverse fixture with mirrored signs should fire symmetrically.
    LONG signs:   sent>=0.5 / dc20_up / close_above_open / top_40pct / above_avwap_20low
    SHORT signs:  sent<=-0.5 / dc20_dn / close_below_open / bottom_40pct / NOT above_avwap_20high
    Both should fire."""
    from backtest.signals.screener import (
        strat_news_momentum_long, strat_news_momentum_short
    )
    # LONG side
    long_s = {
        "news_sentiment_5d": 0.5,
        "news_volume_zscore_5d": 1.5,
        "dc20_breakout_up": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
        "vol_above_avg": True,
        "above_avwap_20low": True,
    }
    # SHORT mirror
    short_s = {
        "news_sentiment_5d": -0.5,
        "news_volume_zscore_5d": 1.5,
        "dc20_breakout_dn": True,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "vol_above_avg": True,
        "above_avwap_20high": False,
    }
    assert strat_news_momentum_long(long_s)["fires"] is True
    assert strat_news_momentum_short(short_s)["fires"] is True


def test_batch603_news_momentum_short_sentiment_sign_required():
    """Pin (4b): positive sentiment on the SHORT-side fixture must NOT fire."""
    from backtest.signals.screener import strat_news_momentum_short
    s = {
        "news_sentiment_5d": 0.6,  # POSITIVE - wrong for SHORT
        "news_volume_zscore_5d": 2.0,
        "dc20_breakout_dn": True,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "vol_above_avg": True,
        "above_avwap_20high": False,
    }
    assert strat_news_momentum_short(s)["fires"] is False


def test_batch603_news_reversal_long_3_gates_fires():
    """Pin (5)."""
    from backtest.signals.screener import strat_news_reversal_long
    s = {
        "news_sentiment_5d": -0.8,
        "pct_change_5d": -0.12,
        "news_article_count": 5,
    }
    out = strat_news_reversal_long(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch603_news_reversal_long_symmetric_with_short():
    """Pin (6): mirror sign assertion - news_reversal_short fires on
    +0.7 / +0.10; news_reversal_long should fire on -0.7 / -0.10."""
    from backtest.signals.screener import (
        strat_news_reversal_short, strat_news_reversal_long
    )
    short_s = {
        "news_sentiment_5d": 0.7,
        "pct_change_5d": 0.11,
        "news_article_count": 3,
    }
    long_s = {
        "news_sentiment_5d": -0.7,
        "pct_change_5d": -0.11,
        "news_article_count": 3,
    }
    assert strat_news_reversal_short(short_s)["fires"] is True
    assert strat_news_reversal_long(long_s)["fires"] is True


def test_batch603_news_reversal_long_blocks_weak_negative_sentiment():
    """Pin (6b): sentiment -0.5 (weaker than the -0.7 threshold) must NOT fire."""
    from backtest.signals.screener import strat_news_reversal_long
    s = {
        "news_sentiment_5d": -0.5,    # not strong enough
        "pct_change_5d": -0.15,
        "news_article_count": 5,
    }
    assert strat_news_reversal_long(s)["fires"] is False


def test_batch603_news_reversal_long_blocks_small_down_move():
    """Pin (6c): pct_change -0.05 (smaller than -0.10) must NOT fire."""
    from backtest.signals.screener import strat_news_reversal_long
    s = {
        "news_sentiment_5d": -0.8,
        "pct_change_5d": -0.05,       # smaller than -0.10
        "news_article_count": 5,
    }
    assert strat_news_reversal_long(s)["fires"] is False


def test_batch603_regime_default_news_momentum_short_bear_crisis_neutral():
    """Pin (7) SHORT side: direction-aware default."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    assert "news_momentum_short" not in STRATEGY_REGIME_AFFINITY
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime(
            "news_momentum_short", r, direction="short"
        ) is True
    assert should_strategy_fire_in_regime(
        "news_momentum_short", "bull", direction="short"
    ) is False


def test_batch603_regime_default_news_reversal_long_bull_neutral():
    """Pin (7) LONG side."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    assert "news_reversal_long" not in STRATEGY_REGIME_AFFINITY
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime(
            "news_reversal_long", r, direction="long"
        ) is True
    for r in ["bear", "crisis"]:
        assert should_strategy_fire_in_regime(
            "news_reversal_long", r, direction="long"
        ) is False


def test_batch603_all_strategies_count_after_b603():
    """Pin (8): +2 strategies from B603 g+h."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 219, (
        f"Expected 219 post-B603 (+2 news inverses); got {len(ALL_STRATEGIES)}"
    )
