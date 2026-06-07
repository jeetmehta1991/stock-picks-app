"""Batch 467 (2026-05-29) -- P10 Polygon news sentiment producer + strategies.

Closes queue item P10 (`producer-polygon-news-sentiment`): wires the
prefetched Polygon news cache to the screener as 3 new signal keys plus
2 new strategies.

PRODUCER EXTENSIONS (backtest/signals/news_sentiment.py):
  news_sentiment_5d       -- recency-weighted 5d window mean
                              (weight = max(0, 1 - age/5); 0 if empty)
  news_sentiment_30d      -- equal-weighted 30d window mean
  news_volume_zscore_5d   -- z-score of last-5-day article count vs
                              trailing 25-day daily-count distribution
                              (so 5d count is compared to 25d baseline
                              of independent daily counts; z = (count_5d
                              - 5 * mu_daily) / (sqrt(5) * sd_daily))
  news_count_5d           -- raw 5d article count

NEW SIGNAL (backtest/signals/technical.py):
  compute_simple_returns(df) -> pct_change_5d / 10d / 20d as fractional
  returns. Registered in compute_all_signals() so every screener pass
  carries them.

NEW STRATEGIES (backtest/signals/screener.py):
  strat_news_momentum_long   -- sentiment_5d >= 0.5 AND vol_zscore_5d >= 1.5
                                 AND dc20_breakout_up
  strat_news_reversal_short  -- sentiment_5d >= 0.7 AND pct_change_5d > 0.10
                                 AND news_article_count >= 3

Both registered in ALL_STRATEGIES; not in DEPRECATED_STRATEGIES.

TESTS BELOW assert:
  1. Producer returns the 4 new keys when articles exist + when empty.
  2. Recency weight gives more weight to recent articles.
  3. Volume z-score is positive when 5d count > baseline mean * 5.
  4. compute_simple_returns emits pct_change_5d / 10d / 20d.
  5. compute_simple_returns returns {} on short history.
  6. compute_all_signals integrates compute_simple_returns.
  7. strat_news_momentum_long fires when all three gates hit.
  8. strat_news_momentum_long does NOT fire when any gate misses.
  9. strat_news_reversal_short fires when all three gates hit.
 10. strat_news_reversal_short does NOT fire when sentiment too low.
 11. Both new strategies are registered in ALL_STRATEGIES.
 12. The new strategy names are not in DEPRECATED_STRATEGIES.
"""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest


# ----------------------------------------------------------------------
# Producer tests
# ----------------------------------------------------------------------
def _make_news_df(rows):
    """rows is iterable of (published_utc_str, sentiment, title)."""
    return pd.DataFrame(
        [{"published_utc": ts, "sentiment": s, "title": t,
          "description": "", "ticker": "TEST"} for ts, s, t in rows]
    )


def test_producer_emits_new_keys_when_articles_present(tmp_path, monkeypatch):
    import backtest.signals.news_sentiment as ns
    rows = [
        (date.today() - timedelta(days=1), "positive", "beats expectations strong growth"),
        (date.today() - timedelta(days=2), "positive", "raised guidance surge"),
        (date.today() - timedelta(days=3), "positive", "upgraded rally"),
    ]
    df = _make_news_df([
        (pd.Timestamp(d, tz="UTC").isoformat(), s, t) for d, s, t in rows
    ])
    p = tmp_path / "TEST.parquet"
    df.to_parquet(p)
    monkeypatch.setattr(ns, "_NEWS_DIR", tmp_path)

    out = ns.compute_news_sentiment_signals("TEST", date.today())
    for k in ("news_sentiment_5d", "news_sentiment_30d",
              "news_volume_zscore_5d", "news_count_5d"):
        assert k in out, f"missing {k}"
    assert out["news_count_5d"] == 3
    assert out["news_sentiment_5d"] > 0  # positive articles


def test_producer_emits_zero_keys_when_window_empty(tmp_path, monkeypatch):
    import backtest.signals.news_sentiment as ns
    # Single old article well outside 7d window
    old = date.today() - timedelta(days=60)
    df = _make_news_df([(pd.Timestamp(old, tz="UTC").isoformat(),
                          "positive", "stale article")])
    p = tmp_path / "OLD.parquet"
    df.to_parquet(p)
    monkeypatch.setattr(ns, "_NEWS_DIR", tmp_path)

    out = ns.compute_news_sentiment_signals("OLD", date.today())
    # Empty current window path returns zero counts but still emits 5d keys
    assert out["news_count_5d"] == 0
    assert out["news_sentiment_5d"] == 0.0
    assert "news_volume_zscore_5d" in out


def test_producer_recency_weight_prefers_recent_articles(tmp_path, monkeypatch):
    import backtest.signals.news_sentiment as ns
    # Two articles: one strongly bullish today, one strongly bearish 5d ago.
    # Recency weight (1 - age/5) gives the bullish article ~weight 1.0 and the
    # bearish article ~weight 0.0 -> the 5d window mean should be positive.
    rows = [
        (date.today(), "positive", "rally surge gains exceeded"),
        (date.today() - timedelta(days=5), "negative", "decline plunge loss"),
    ]
    df = _make_news_df([
        (pd.Timestamp(d, tz="UTC").isoformat(), s, t) for d, s, t in rows
    ])
    p = tmp_path / "REC.parquet"
    df.to_parquet(p)
    monkeypatch.setattr(ns, "_NEWS_DIR", tmp_path)
    out = ns.compute_news_sentiment_signals("REC", date.today())
    assert out["news_sentiment_5d"] > 0, \
        "Recency weight should favor the recent bullish article over " \
        "the 5d-old bearish one"


def test_producer_volume_zscore_positive_on_spike(tmp_path, monkeypatch):
    import backtest.signals.news_sentiment as ns
    # Baseline: variable 0-2 articles/day over 25 trailing days (non-zero std)
    # Spike: 5 articles per day x 5 recent days = 25 articles in 5d window
    rng = np.random.RandomState(7)
    today = date.today()
    rows = []
    for k in range(6, 31):  # 25 baseline days
        n = int(rng.choice([0, 1, 2]))
        for _ in range(n):
            rows.append((today - timedelta(days=k), "neutral", "baseline article"))
    for k in range(5):
        for _ in range(5):
            rows.append((today - timedelta(days=k), "neutral", "spike article"))
    df = _make_news_df([
        (pd.Timestamp(d, tz="UTC").isoformat(), s, t) for d, s, t in rows
    ])
    p = tmp_path / "SPK.parquet"
    df.to_parquet(p)
    monkeypatch.setattr(ns, "_NEWS_DIR", tmp_path)
    out = ns.compute_news_sentiment_signals("SPK", today)
    assert out["news_count_5d"] == 25
    assert out["news_volume_zscore_5d"] > 1.5, \
        f"Expected z > 1.5 on a clear volume spike; got {out['news_volume_zscore_5d']}"


# ----------------------------------------------------------------------
# compute_simple_returns tests
# ----------------------------------------------------------------------
def _make_ohlcv(closes):
    n = len(closes)
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame({
        "open":   closes,
        "high":   [c * 1.01 for c in closes],
        "low":    [c * 0.99 for c in closes],
        "close":  closes,
        "volume": [1_000_000] * n,
    }, index=idx)


def test_compute_simple_returns_emits_5_10_20():
    from backtest.signals.technical import compute_simple_returns
    closes = list(np.linspace(100, 120, 30))  # +20% over 30 days
    df = _make_ohlcv(closes)
    out = compute_simple_returns(df)
    for k in ("pct_change_5d", "pct_change_10d", "pct_change_20d"):
        assert k in out
    # 5-day return on linear ramp: ~+3.6%
    assert 0.02 < out["pct_change_5d"] < 0.06
    # 20-day larger than 5-day on a linear ramp
    assert out["pct_change_20d"] > out["pct_change_5d"]


def test_compute_simple_returns_empty_on_short_history():
    from backtest.signals.technical import compute_simple_returns
    df = _make_ohlcv([100.0] * 5)  # too short
    out = compute_simple_returns(df)
    assert out == {}


def test_compute_all_signals_integrates_simple_returns():
    from backtest.signals.technical import compute_all_signals
    closes = list(np.linspace(100, 110, 50))
    df = _make_ohlcv(closes)
    out = compute_all_signals(df)
    assert "pct_change_5d" in out
    assert "pct_change_20d" in out


# ----------------------------------------------------------------------
# Strategy tests
# ----------------------------------------------------------------------
def test_strat_news_momentum_long_fires_on_full_confluence():
    from backtest.signals.screener import strat_news_momentum_long
    s = {
        "news_sentiment_5d": 0.6,
        "news_volume_zscore_5d": 2.0,
        "dc20_breakout_up": True,
        "close_above_open": True,
    }
    r = strat_news_momentum_long(s)
    assert r["fires"] is True
    assert r["direction"] == "long"


def test_strat_news_momentum_long_misses_when_no_breakout():
    from backtest.signals.screener import strat_news_momentum_long
    s = {
        "news_sentiment_5d": 0.8,
        "news_volume_zscore_5d": 3.0,
        "dc20_breakout_up": False,
    }
    r = strat_news_momentum_long(s)
    assert r["fires"] is False


def test_strat_news_reversal_short_fires_on_overreaction():
    """B614 update: fixture extended with B614 a+b+c gates so it still
    fires post-walk. Threshold 0.8 still passes new +0.5 floor (B614 d).
    Semantic pin preserved: overreaction triggers SHORT."""
    from backtest.signals.screener import strat_news_reversal_short
    s = {
        "news_sentiment_5d": 0.8,
        "pct_change_5d": 0.15,
        "news_count_5d": 5,                       # B614 (c) window-consistent
        "news_sentiment_shift": -0.3,             # B614 (b) tone deteriorating
        "close_below_open": True,                 # B614 (a) EVENT anchor
        "close_in_bottom_40pct_of_range": True,   # B614 (a)
    }
    r = strat_news_reversal_short(s)
    assert r["fires"] is True
    assert r["direction"] == "short"


def test_strat_news_reversal_short_misses_when_sentiment_too_low():
    """B614 update: sentiment 0.4 still blocks (below new 0.5 floor,
    B614 d loosened from 0.7). All other gates provided so this isolates
    the threshold test."""
    from backtest.signals.screener import strat_news_reversal_short
    s = {
        "news_sentiment_5d": 0.4,   # below 0.5 threshold (B614 d loosened)
        "pct_change_5d": 0.20,
        "news_count_5d": 10,
        "news_sentiment_shift": -0.3,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    r = strat_news_reversal_short(s)
    assert r["fires"] is False


def test_both_new_strategies_registered_in_ALL_STRATEGIES():
    from backtest.signals.screener import ALL_STRATEGIES
    assert "news_momentum_long" in ALL_STRATEGIES
    assert "news_reversal_short" in ALL_STRATEGIES


def test_new_strategies_not_in_DEPRECATED():
    from backtest.config import DEPRECATED_STRATEGIES
    assert "news_momentum_long" not in DEPRECATED_STRATEGIES
    assert "news_reversal_short" not in DEPRECATED_STRATEGIES
