"""News sentiment feature extraction from Polygon news + lightweight
rule-based fallback scorer.

Batch 230 (2026-05-18 owner-approved deferred-items implementation; safe
to build in parallel with Batch 225 final rerun - no engine mutation).

Source: Lopez-Lira-Tang 2023 SSRN "Can ChatGPT Forecast Stock Price
Movements?" - LLM-derived news sentiment documented Sharpe ~3.0 on a
long-short news-sentiment portfolio 2021-2022. Replications in 2024
landed at Sharpe 0.8-1.2 (still positive but the 3.0 number doesn't
reproduce cleanly).

This module exposes news sentiment as a FEATURE (not a standalone
strategy) feeding into:
  - the meta-labeler (Batch 214/228) as an additional feature column
  - higher-conviction event-driven strategies as a confluence gate

Data sources (preferred order):
  1. Polygon news 'sentiment' field if populated (positive/negative/neutral)
  2. Polygon news 'insights_json' if populated (per-ticker insights)
  3. Rule-based fallback: lightweight positive/negative word counts in
     title + description text

LLM-based scoring (FinBERT) is a future prefetch task; this module
reads pre-computed scores when available + falls back to rule-based.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd


_NEWS_DIR = Path(__file__).parent.parent.parent / "data_prefetch" / "polygon" / "news"

# Lightweight finance-domain sentiment lexicons. Not as accurate as
# FinBERT but reproducible and offline. Loughran-McDonald 2011 JF
# financial dictionary subset.
POSITIVE_WORDS = frozenset({
    "beat", "beats", "exceeded", "surpasses", "surpassed", "outperform",
    "upgrade", "upgraded", "raised", "raises", "strong", "stronger",
    "growth", "growing", "expansion", "expand", "expanded", "boost",
    "boosts", "boosted", "rally", "rallies", "rallied", "surge", "surges",
    "surged", "soar", "soars", "soared", "jump", "jumps", "jumped",
    "gain", "gains", "gained", "rise", "rises", "rose", "climb", "climbs",
    "climbed", "advance", "advances", "advanced", "positive", "profit",
    "profitable", "profitability", "record", "milestone", "breakthrough",
    "innovation", "leadership", "leader", "winning", "won", "wins",
    "approval", "approved", "successful", "success", "exceed", "exceeds",
    "exceeding", "premium", "robust", "solid", "improved", "improvement",
    "improving", "improves", "above", "ahead", "bullish",
})

NEGATIVE_WORDS = frozenset({
    "miss", "missed", "misses", "missing", "underperform", "underperforms",
    "underperformed", "downgrade", "downgraded", "cut", "cuts", "slashed",
    "weak", "weakness", "decline", "declines", "declined", "fall", "falls",
    "fell", "drop", "drops", "dropped", "plunge", "plunges", "plunged",
    "tumble", "tumbles", "tumbled", "slump", "slumps", "slumped",
    "loss", "losses", "lost", "deficit", "shortfall", "negative",
    "downgrade", "warning", "warns", "warned", "concern", "concerns",
    "concerning", "worry", "worried", "worries", "risk", "risks",
    "risky", "bankruptcy", "bankrupt", "default", "defaults",
    "lawsuit", "investigation", "investigated", "scandal", "fraud",
    "missed", "below", "behind", "lag", "lags", "lagged", "bearish",
    "delay", "delays", "delayed", "postpone", "postponed", "halt",
    "halted", "suspension", "suspended", "layoff", "layoffs", "cuts",
})


def _rule_based_sentiment(text: str) -> float:
    """Lightweight rule-based sentiment scorer using Loughran-McDonald
    finance lexicon subset. Returns score in [-1, 1] (negative = bearish,
    positive = bullish, 0 = neutral)."""
    if not text or not isinstance(text, str):
        return 0.0
    words = text.lower().split()
    n_pos = sum(1 for w in words if w.strip(".,!?;:'\"()[]{}") in POSITIVE_WORDS)
    n_neg = sum(1 for w in words if w.strip(".,!?;:'\"()[]{}") in NEGATIVE_WORDS)
    total = n_pos + n_neg
    if total == 0:
        return 0.0
    return (n_pos - n_neg) / total


def _polygon_sentiment_to_score(s: str) -> Optional[float]:
    """Map Polygon's 'sentiment' string to [-1, 0, 1]."""
    if not isinstance(s, str):
        return None
    s_lower = s.lower().strip()
    if s_lower in ("positive", "bullish"):
        return 1.0
    if s_lower in ("negative", "bearish"):
        return -1.0
    if s_lower in ("neutral",):
        return 0.0
    return None


def compute_news_sentiment_signals(
    ticker: str,
    as_of: date,
    lookback_days: int = 7,
) -> dict:
    """Compute news-sentiment features for a ticker as-of a date.

    Reads `data_prefetch/polygon/news/{TICKER}.parquet`, filters to
    articles published in the last `lookback_days` calendar days, and
    aggregates sentiment using:
      - Polygon's `sentiment` field when populated (Polygon provider score)
      - Fallback rule-based scorer on title + description text

    Returns dict with optional keys:
      - news_count_7d:           int (count of articles in window)
      - news_sentiment_score:    float in [-1, 1] (mean across articles)
      - news_bullish_pct:        float in [0, 1] (fraction positive)
      - news_bearish_pct:        float in [0, 1] (fraction negative)
      - news_uses_polygon_score: bool (True if any article had Polygon
                                  sentiment populated)

    Returns empty dict on data miss / no recent articles (consumer's
    .get() fallback to default 0).
    """
    safe_ticker = ticker.replace(".", "-")
    path = _NEWS_DIR / f"{safe_ticker}.parquet"
    if not path.exists():
        return {}
    try:
        df = pd.read_parquet(path)
    except Exception:
        return {}
    if df.empty or "published_utc" not in df.columns:
        return {}
    try:
        df["published_dt"] = pd.to_datetime(df["published_utc"], errors="coerce")
        df = df.dropna(subset=["published_dt"])
        df["published_date"] = df["published_dt"].dt.date
    except Exception:
        return {}
    cutoff = as_of - timedelta(days=lookback_days)
    sub = df[(df["published_date"] >= cutoff) & (df["published_date"] <= as_of)]
    if sub.empty:
        return {"news_count_7d": 0, "news_sentiment_score": 0.0,
                "news_bullish_pct": 0.0, "news_bearish_pct": 0.0,
                "news_uses_polygon_score": False}
    scores = []
    uses_polygon = False
    for _, row in sub.iterrows():
        # Prefer Polygon-supplied sentiment when present
        p_score = _polygon_sentiment_to_score(row.get("sentiment"))
        if p_score is not None:
            scores.append(p_score)
            uses_polygon = True
            continue
        # Fall back to rule-based on title + description
        title = row.get("title", "") or ""
        desc  = row.get("description", "") or ""
        text  = f"{title}. {desc}"
        scores.append(_rule_based_sentiment(text))
    n = len(scores)
    if n == 0:
        return {"news_count_7d": 0, "news_sentiment_score": 0.0,
                "news_bullish_pct": 0.0, "news_bearish_pct": 0.0,
                "news_uses_polygon_score": False}
    avg = sum(scores) / n
    n_pos = sum(1 for s in scores if s > 0)
    n_neg = sum(1 for s in scores if s < 0)
    return {
        "news_count_7d":           int(n),
        "news_sentiment_score":    round(float(avg), 4),
        "news_bullish_pct":        round(n_pos / n, 4),
        "news_bearish_pct":        round(n_neg / n, 4),
        "news_uses_polygon_score": bool(uses_polygon),
    }
