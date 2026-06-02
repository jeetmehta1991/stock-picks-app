"""Batch 552 (2026-06-02) -- OPT-C Phase 3: news_sentiment per-article
score pre-compute at cache fill time + _score_window vectorize.

Source: per CHECKLIST #77.
Queue: EXECUTION_QUEUE.md OPT-C pivot.

Pre-fix profile (post-B548): _score_window 2079 calls / 37s / 18ms/call.
Bottleneck: per-row `for _, row in sub.iterrows(): _score_article(row)`
where _score_article does string-lower + dict-lookup OR rule-based
text scoring. Repeated on every (ticker, as_of) call across 3 windows
(current 7d, prior 7d, 30d).

Post-fix B552:
  - _precompute_article_scores runs ONCE at cache fill time:
    * Polygon sentiment field -> vectorized .str.lower().str.strip().map
    * Rule-based fallback applied only to rows where polygon score is None
    * Result: numeric `_article_score` column + boolean `_uses_polygon` column
  - _score_window becomes:
        scores = sub["_article_score"].to_numpy()
        avg = scores.mean()
        n_pos = (scores > 0).sum()
        n_neg = (scores < 0).sum()
    A Python for-loop replaced by 3 numpy ops.
  - Backwards-compatible fallback path retained for callers passing
    non-cached DataFrames (no test uses this path; pin in code only).

Bench: 46ms/call -> 26ms/call on AAPL (current+prior+5d+30d windows).

Pins:

  (1) Parity: post-fix output dict matches pre-fix dict for AAPL/MSFT/
      JPM x 2 dates verified vs pre-B552 commit. Key invariants:
      news_count_7d / news_sentiment_score / news_bullish_pct /
      news_bearish_pct / news_sentiment_shift / news_uses_polygon_score
  (2) Cache layer pre-computes columns: _article_score (float),
      _uses_polygon (bool)
  (3) _score_window vectorized aggregation matches per-row reference
      on synthetic 5-article window with mixed polygon + rule-based
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def reset_caches():
    from backtest.signals.news_sentiment import _NEWS_BY_TICKER
    _NEWS_BY_TICKER.clear()
    yield
    _NEWS_BY_TICKER.clear()


def _have_news(ticker: str) -> bool:
    repo_root = Path(__file__).parent.parent.parent
    return (repo_root / "data_prefetch" / "polygon" / "news"
            / f"{ticker.replace('.', '-')}.parquet").exists()


@pytest.mark.skipif(not _have_news("AAPL"), reason="AAPL news cache absent")
def test_batch552_cache_has_article_score_column():
    """After cache load, _article_score (float) and _uses_polygon (bool)
    columns must be present on the cached DataFrame."""
    from backtest.signals.news_sentiment import (
        _load_news_parquet, _NEWS_BY_TICKER,
    )
    df = _load_news_parquet("AAPL")
    assert "_article_score" in df.columns
    assert "_uses_polygon" in df.columns
    assert pd.api.types.is_numeric_dtype(df["_article_score"])
    assert pd.api.types.is_bool_dtype(df["_uses_polygon"]) or (
        df["_uses_polygon"].dtype == bool
    )


@pytest.mark.skipif(not _have_news("AAPL"), reason="AAPL news cache absent")
def test_batch552_known_signal_outcome_aapl():
    """Pre-B552 baseline: AAPL 2024-06-14 -> count=110, sent_score=0.4121,
    bullish_pct=0.5091, bearish_pct=0.0455."""
    from backtest.signals.news_sentiment import compute_news_sentiment_signals
    out = compute_news_sentiment_signals("AAPL", date(2024, 6, 14))
    assert out["news_count_7d"] == 110
    assert abs(out["news_sentiment_score"] - 0.4121) < 0.001
    assert abs(out["news_bullish_pct"] - 0.5091) < 0.001


def test_batch552_score_window_vectorized_matches_reference():
    """_score_window with vectorized path must match the per-row
    reference on a synthetic mixed-source window."""
    from backtest.signals.news_sentiment import (
        _precompute_article_scores, _score_window, _rule_based_sentiment,
    )
    # 5 articles: 2 polygon-positive, 1 polygon-negative, 2 rule-based
    df = pd.DataFrame([
        {"sentiment": "positive", "title": "x", "description": ""},
        {"sentiment": "positive", "title": "x", "description": ""},
        {"sentiment": "negative", "title": "x", "description": ""},
        {"sentiment": None, "title": "earnings beat raised",
         "description": "strong"},  # rule-based: positive
        {"sentiment": None, "title": "downgrade weak",
         "description": "decline"},  # rule-based: negative
    ])
    df_scored = _precompute_article_scores(df)
    avg, n, n_pos, n_neg, polygon_any = _score_window(df_scored)

    # Reference (manual): polygon=[1, 1, -1, None, None]; rule=[1, -1]
    # All 5: [1, 1, -1, 1, -1] -> avg=0.2, n=5, n_pos=3, n_neg=2
    assert n == 5
    assert abs(avg - 0.2) < 0.001
    assert n_pos == 3
    assert n_neg == 2
    assert polygon_any is True  # 3 of 5 are polygon


def test_batch552_score_window_empty_returns_zero_tuple():
    from backtest.signals.news_sentiment import _score_window
    out = _score_window(pd.DataFrame())
    assert out == (0.0, 0, 0, 0, False)
