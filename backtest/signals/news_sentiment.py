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

import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


# B832 (2026-06-16) PATTERN BB SPOF SENTINEL state.
# Per S4-B750-PATTERN-BB-NEWS-SENTIMENT-VENDOR-SPOF-SENTINEL: Polygon news
# is a single-point-of-failure for ~6 news-sentiment-consuming strategies
# (news_momentum_long / news_reversal_short / news_sentiment_shift_long
# etc). If the vendor goes silent (parquets stale OR sentiment field all
# zero OR rule-based fallback active for too long) those strategies fire
# on stale/degenerate signal without operator awareness.
#
# Sentinel pattern: track per-process call counts + degenerate-emission
# counts; once thresholds breached, log a WARNING once-per-process
# (rate-limited via _SPOF_WARNED flag). Mirrors B416 silent-producer
# logging pattern.
_SPOF_CALL_COUNT = 0
_SPOF_EMPTY_RETURNS = 0       # data file missing OR empty parquet
_SPOF_ZERO_SCORE_RETURNS = 0  # cur_n>0 but all scores rounded to 0.0
_SPOF_RULE_FALLBACK_ONLY = 0  # cur_n>0 but news_uses_polygon_score=False
_SPOF_WARNED = {"empty": False, "zero_score": False, "rule_only": False}
_SPOF_THRESHOLDS = {
    "empty": 50,         # 50 consecutive empty returns -> vendor cache exhausted
    "zero_score": 30,    # 30 zero-score returns -> sentiment field degraded
    "rule_only": 100,    # 100 rule-only returns -> Polygon sentiment field absent
}


def _spof_record(outcome: str) -> None:
    """B832 PATTERN BB: record one news-sentiment producer call + emit
    rate-limited WARNING if SPOF threshold breached. Called once per
    compute_news_sentiment_signals invocation."""
    global _SPOF_CALL_COUNT, _SPOF_EMPTY_RETURNS, _SPOF_ZERO_SCORE_RETURNS, _SPOF_RULE_FALLBACK_ONLY
    _SPOF_CALL_COUNT += 1
    if outcome == "empty":
        _SPOF_EMPTY_RETURNS += 1
        if _SPOF_EMPTY_RETURNS >= _SPOF_THRESHOLDS["empty"] and not _SPOF_WARNED["empty"]:
            logger.warning(
                "B832 SPOF SENTINEL: news_sentiment producer returned EMPTY "
                "for %d consecutive calls -- Polygon news parquet cache "
                "likely exhausted OR all ticker files missing. News-sentiment "
                "strategies firing on stale signal. Check data_prefetch/polygon/news/",
                _SPOF_EMPTY_RETURNS,
            )
            _SPOF_WARNED["empty"] = True
    elif outcome == "zero_score":
        _SPOF_ZERO_SCORE_RETURNS += 1
        if _SPOF_ZERO_SCORE_RETURNS >= _SPOF_THRESHOLDS["zero_score"] and not _SPOF_WARNED["zero_score"]:
            logger.warning(
                "B832 SPOF SENTINEL: news_sentiment producer emitted "
                "zero-score for %d returns despite article-count>0 -- Polygon "
                "sentiment field may be all-null OR rule-based scorer degraded. "
                "News-sentiment strategies firing on degenerate signal.",
                _SPOF_ZERO_SCORE_RETURNS,
            )
            _SPOF_WARNED["zero_score"] = True
    elif outcome == "rule_only":
        _SPOF_RULE_FALLBACK_ONLY += 1
        if _SPOF_RULE_FALLBACK_ONLY >= _SPOF_THRESHOLDS["rule_only"] and not _SPOF_WARNED["rule_only"]:
            logger.warning(
                "B832 SPOF SENTINEL: news_sentiment producer emitted Polygon-"
                "sentiment-absent (rule-fallback only) for %d returns -- "
                "Polygon vendor sentiment field may be silently dropped. "
                "Rule-based fallback active; FinBERT/LLM-based scoring not yet "
                "deployed. Validate Polygon news API contract.",
                _SPOF_RULE_FALLBACK_ONLY,
            )
            _SPOF_WARNED["rule_only"] = True


_NEWS_DIR = Path(__file__).parent.parent.parent / "data_prefetch" / "polygon" / "news"

# B1243 (2026-07-07 Council 291 Sprint 5 S5-B1212):
# Finnhub company_news secondary source for tickers with zero Polygon coverage.
# B1211 audit found 21 zero-coverage tickers in Polygon; B1242 investigation
# verified 21/21 have Finnhub data (48-246 articles per ticker).
_FINNHUB_NEWS_DIR = Path(__file__).parent.parent.parent / "data_prefetch" / "finnhub" / "company_news"

# Batch 535 OPT-A: per-ticker news parquet cache. Polygon news prefetch
# has ~1926 tickers; each parquet ~50-500KB; max ~1GB if all loaded.
_NEWS_BY_TICKER: dict[str, pd.DataFrame] = {}
_FINNHUB_NEWS_BY_TICKER: dict[str, pd.DataFrame] = {}


def _load_finnhub_news_parquet(ticker: str) -> pd.DataFrame:
    """B1243 (Council 291 S5-B1212): return Finnhub company_news normalized
    to Polygon news schema.

    Finnhub schema: {headline, summary, datetime (unix), category, source, url}
    Polygon schema: {title, description, published_utc, sentiment, ...}

    Normalization:
      - headline -> title
      - summary -> description
      - datetime (unix ts) -> published_utc (ISO string) + published_dt
      - No 'sentiment' field (Finnhub doesn't emit one) -> rule-based scorer used

    Returns empty DataFrame on data miss.
    """
    safe_ticker = ticker.replace(".", "-")
    cached = _FINNHUB_NEWS_BY_TICKER.get(safe_ticker)
    if cached is not None:
        return cached
    path = _FINNHUB_NEWS_DIR / f"{safe_ticker}.parquet"
    if not path.exists():
        _FINNHUB_NEWS_BY_TICKER[safe_ticker] = pd.DataFrame()
        return _FINNHUB_NEWS_BY_TICKER[safe_ticker]
    try:
        df = pd.read_parquet(path)
        if df.empty:
            _FINNHUB_NEWS_BY_TICKER[safe_ticker] = pd.DataFrame()
            return _FINNHUB_NEWS_BY_TICKER[safe_ticker]
        # Normalize to Polygon schema
        df = df.copy()
        df["title"] = df.get("headline", "")
        df["description"] = df.get("summary", "")
        # datetime is unix timestamp; convert to pandas datetime
        df["published_dt"] = pd.to_datetime(df["datetime"], unit="s", errors="coerce")
        df = df.dropna(subset=["published_dt"])
        df["published_date"] = df["published_dt"].dt.date
        df["published_utc"] = df["published_dt"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        # No sentiment field - rule-based scorer will be used
        df["sentiment"] = None
        # Pre-score articles (same as Polygon path)
        df = _precompute_article_scores(df)
        _FINNHUB_NEWS_BY_TICKER[safe_ticker] = df
        return df
    except Exception:
        _FINNHUB_NEWS_BY_TICKER[safe_ticker] = pd.DataFrame()
        return _FINNHUB_NEWS_BY_TICKER[safe_ticker]


def _precompute_article_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Batch 552 OPT-C: pre-compute per-article _article_score + _uses_polygon
    columns once at cache fill time. _score_window then becomes a vectorized
    aggregation (mean / >0 count / <0 count) over numeric columns instead of
    a Python for-loop over .iterrows() calling _score_article per row.

    Score derivation matches _score_article semantics exactly:
      - Polygon `sentiment` field, when populated, maps positive/bullish=+1,
        negative/bearish=-1, neutral=0 via _polygon_sentiment_to_score
      - Otherwise fall back to _rule_based_sentiment on title + ". " + description
    """
    if df.empty:
        return df
    n = len(df)
    sentiment_raw = df["sentiment"] if "sentiment" in df.columns else pd.Series(
        [None] * n, index=df.index
    )

    # Vectorize the Polygon-sentiment mapping: lowercase + strip
    sentiment_str = sentiment_raw.where(
        sentiment_raw.apply(lambda x: isinstance(x, str)), other=None,
    )
    sentiment_lower = sentiment_str.str.lower().str.strip()
    polygon_map = {
        "positive": 1.0, "bullish": 1.0,
        "negative": -1.0, "bearish": -1.0,
        "neutral": 0.0,
    }
    polygon_scores = sentiment_lower.map(polygon_map)
    uses_polygon = polygon_scores.notna()

    # Rule-based fallback for non-Polygon rows
    title = df["title"] if "title" in df.columns else pd.Series([""] * n, index=df.index)
    desc = df["description"] if "description" in df.columns else pd.Series([""] * n, index=df.index)
    combined = title.fillna("").astype(str) + ". " + desc.fillna("").astype(str)
    # _rule_based_sentiment is cheap-ish but still Python; only apply on
    # the fallback rows. Most articles in Polygon news have sentiment
    # populated so the fallback subset is small.
    rule_scores = combined[~uses_polygon].apply(_rule_based_sentiment)
    # Merge: polygon scores where present, rule-based where not
    final = polygon_scores.fillna(0.0).astype(float)
    if not rule_scores.empty:
        final.loc[~uses_polygon] = rule_scores
    df = df.copy()
    df["_article_score"] = final
    df["_uses_polygon"] = uses_polygon
    return df


def _load_news_parquet(ticker: str) -> pd.DataFrame:
    """B535 OPT-A cached per-ticker news lookup.

    B545 OPT-C update: pre-compute published_date + published_dt at
    cache load time (one-shot pd.to_datetime + .dt.date). Pre-OPT-C
    the producer re-did this conversion on every call (~30-40ms each
    for typical news cache size). Cache now serves the converted
    DataFrame ready for boolean date filters.

    Batch 552 OPT-C: also pre-compute _article_score + _uses_polygon
    so _score_window aggregates a numeric column (sum / count >0 /
    count <0) instead of looping per-row.
    """
    safe_ticker = ticker.replace(".", "-")
    cached = _NEWS_BY_TICKER.get(safe_ticker)
    if cached is not None:
        return cached
    path = _NEWS_DIR / f"{safe_ticker}.parquet"
    if not path.exists():
        _NEWS_BY_TICKER[safe_ticker] = pd.DataFrame()
        return _NEWS_BY_TICKER[safe_ticker]
    try:
        df = pd.read_parquet(path)
        # B545 OPT-C: do the date conversion ONCE at cache fill.
        if not df.empty and "published_utc" in df.columns:
            df = df.copy()
            df["published_dt"] = pd.to_datetime(df["published_utc"],
                                                  errors="coerce")
            df = df.dropna(subset=["published_dt"])
            df["published_date"] = df["published_dt"].dt.date
            # B552 OPT-C: pre-score articles
            df = _precompute_article_scores(df)
        _NEWS_BY_TICKER[safe_ticker] = df
        return df
    except Exception:
        _NEWS_BY_TICKER[safe_ticker] = pd.DataFrame()
        return _NEWS_BY_TICKER[safe_ticker]

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


def _score_article(row) -> tuple:
    """Score one article row. Returns (score, used_polygon).
    Polygon sentiment preferred; rule-based fallback on title+description."""
    p_score = _polygon_sentiment_to_score(row.get("sentiment"))
    if p_score is not None:
        return p_score, True
    title = row.get("title", "") or ""
    desc  = row.get("description", "") or ""
    return _rule_based_sentiment(f"{title}. {desc}"), False


def _score_window(sub: pd.DataFrame) -> tuple:
    """Score every article in a window. Returns (mean, n, n_pos, n_neg,
    used_polygon_any). Empty window returns (0.0, 0, 0, 0, False).

    Batch 552 OPT-C: vectorized aggregation over pre-computed
    `_article_score` + `_uses_polygon` columns (populated by
    _precompute_article_scores at cache load time). Pre-fix used a
    Python for-loop over .iterrows() calling _score_article per row.
    """
    n = len(sub)
    if n == 0:
        return 0.0, 0, 0, 0, False
    if "_article_score" in sub.columns:
        scores = sub["_article_score"].to_numpy()
        avg = float(scores.mean())
        n_pos = int((scores > 0).sum())
        n_neg = int((scores < 0).sum())
        uses_polygon = bool(sub["_uses_polygon"].any()) if "_uses_polygon" in sub.columns else False
        return avg, n, n_pos, n_neg, uses_polygon
    # Fallback path (cache layer pre-B552 or upstream callers passing
    # non-cached DataFrames): preserve original semantics via per-row
    # _score_article.
    scores = []
    uses_polygon = False
    for _, row in sub.iterrows():
        s, used_p = _score_article(row)
        scores.append(s)
        if used_p:
            uses_polygon = True
    n_list = len(scores)
    if n_list == 0:
        return 0.0, 0, 0, 0, False
    avg = sum(scores) / n_list
    n_pos = sum(1 for s in scores if s > 0)
    n_neg = sum(1 for s in scores if s < 0)
    return avg, n_list, n_pos, n_neg, uses_polygon


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
      - news_count_7d / news_article_count:  int (article count in current
                                               window; aliased so
                                               strat_news_sentiment_long
                                               and strat_news_sentiment_shift_long
                                               can read either name).
      - news_sentiment_score / news_sentiment_mean: float in [-1, 1] (mean
                                               across articles; aliased for
                                               back-compat + strategy consumers).
      - news_bullish_pct / news_bearish_pct: float in [0, 1]
      - news_sentiment_shift:    float in [-2, 2] (current-window mean minus
                                  prior-window mean of same size; positive =
                                  sentiment improving vs prior period;
                                  0.0 when prior window is empty).
      - news_prior_article_count: int (count in prior window; helps
                                   interpret shift confidence).
      - news_uses_polygon_score: bool (True if any current-window article
                                  had Polygon sentiment populated).

    Batch 267 (2026-05-20 owner-approved Path B): emits aliased keys
    (news_article_count / news_sentiment_mean) so the news sentiment
    strategies can read them, and computes news_sentiment_shift (delta vs
    prior `lookback_days` window) so strat_news_sentiment_shift_long can
    fire. Prior keys (news_count_7d / news_sentiment_score) preserved for
    back-compat with existing trade_log artifacts.

    Returns empty dict on data miss (consumer's .get() fallback to 0).
    """
    # B535 OPT-A: cached per-ticker lookup (was per-call disk read).
    # B545 OPT-C: date conversion pre-computed at cache fill; producer
    # now just consumes published_date column directly.
    df = _load_news_parquet(ticker)
    # B1243 (2026-07-07 Council 291 S5-B1212): Finnhub fallback for tickers
    # with zero Polygon news coverage. B1211 audit found 21 zero-coverage tickers
    # in Batch A; B1242 verified 21/21 have Finnhub company_news data (48-246
    # articles per ticker; range 2025-2026). Fallback strategy:
    # (1) Load Polygon news file
    # (2) If entirely empty OR current 7-day window has 0 articles, try Finnhub
    # (3) If Finnhub has articles in the same 7-day window, use Finnhub
    news_source = "polygon" if not df.empty and "published_date" in df.columns else "empty"
    if df.empty or "published_date" not in df.columns:
        df = _load_finnhub_news_parquet(ticker)
        if df.empty or "published_date" not in df.columns:
            _spof_record("empty")  # B832 SPOF SENTINEL: vendor cache exhausted
            return {}
        news_source = "finnhub_fallback"

    # Current window: [as_of - lookback_days, as_of]
    cur_start = as_of - timedelta(days=lookback_days)
    cur = df[(df["published_date"] >= cur_start) & (df["published_date"] <= as_of)]
    # B1243: If Polygon window empty, try Finnhub for the same window
    if news_source == "polygon" and cur.empty:
        finnhub_df = _load_finnhub_news_parquet(ticker)
        if not finnhub_df.empty and "published_date" in finnhub_df.columns:
            finnhub_cur = finnhub_df[
                (finnhub_df["published_date"] >= cur_start)
                & (finnhub_df["published_date"] <= as_of)
            ]
            if not finnhub_cur.empty:
                # Finnhub has articles in this window - use it as fallback source
                df = finnhub_df
                cur = finnhub_cur
                news_source = "finnhub_fallback"

    # Prior window: [as_of - 2*lookback_days, as_of - lookback_days)
    prior_start = as_of - timedelta(days=2 * lookback_days)
    prior_end   = as_of - timedelta(days=lookback_days)
    prior = df[(df["published_date"] >= prior_start) & (df["published_date"] < prior_end)]

    cur_avg, cur_n, n_pos, n_neg, uses_polygon = _score_window(cur)
    prior_avg, prior_n, _p_pos, _p_neg, _p_polygon = _score_window(prior)

    # Batch 467 (P10): add fixed-window 5d / 30d sentiment + 5d volume z-score
    # for strat_news_momentum_long + strat_news_reversal_short. Independent
    # of `lookback_days` so the same producer feeds both shift-detector
    # strategies (lookback-driven) and momentum/reversal strategies
    # (fixed-window). Tetlock 2007 / Da-Engelberg-Gao 2011 use ~5d windows;
    # 30d baseline is the canonical news-volume baseline window.
    five_start = as_of - timedelta(days=5)
    thirty_start = as_of - timedelta(days=30)
    five_d = df[(df["published_date"] >= five_start)
                & (df["published_date"] <= as_of)]
    thirty_d = df[(df["published_date"] >= thirty_start)
                  & (df["published_date"] <= as_of)]

    # Recency-weighted mean within 5d window: weight = 1 - age/5 (linear).
    # Equivalent to volume-weighted with weight ~ recency since multiple
    # articles per day count as multiple recent-bucket observations.
    def _recency_weighted_mean(sub: pd.DataFrame) -> float:
        if sub.empty:
            return 0.0
        s_scores = []
        weights = []
        for _, row in sub.iterrows():
            sc, _ = _score_article(row)
            age = (as_of - row["published_date"]).days
            w = max(0.0, 1.0 - (age / 5.0))
            if w <= 0:
                continue
            s_scores.append(sc)
            weights.append(w)
        if not weights:
            return 0.0
        total_w = sum(weights)
        return sum(s * w for s, w in zip(s_scores, weights)) / total_w \
            if total_w > 0 else 0.0

    sentiment_5d = _recency_weighted_mean(five_d)
    avg_30d, _n30, _, _, _ = _score_window(thirty_d)

    # Volume z-score: count_5d vs trailing 30-day daily-count distribution
    # (exclude the last 5 days from baseline so the z-score is "5d count
    # relative to its own prior 25 days"). Cohen-Frazzini-Malloy news-
    # volume papers use a similar normalisation.
    baseline_end = as_of - timedelta(days=5)
    baseline_start = as_of - timedelta(days=30)
    baseline = df[(df["published_date"] >= baseline_start)
                  & (df["published_date"] < baseline_end)]
    count_5d = int(len(five_d))
    # Per-day counts in baseline:
    if baseline.empty:
        vol_zscore_5d = 0.0
    else:
        daily = baseline.groupby("published_date").size()
        # Reindex to fill missing days as 0:
        full_idx = pd.date_range(baseline_start, baseline_end - timedelta(days=1),
                                  freq="D").date
        daily = daily.reindex(full_idx, fill_value=0)
        mu = float(daily.mean())
        sd = float(daily.std(ddof=1)) if len(daily) > 1 else 0.0
        # Compare count_5d (5-day total) to expected 5 * mu with std
        # sqrt(5)*sd (variance of independent daily counts).
        expected = 5.0 * mu
        sd_5 = (5 ** 0.5) * sd
        vol_zscore_5d = ((count_5d - expected) / sd_5) if sd_5 > 0 else 0.0

    if cur_n == 0:
        _spof_record("empty")  # B832 SPOF SENTINEL: no current-window articles
        return {"news_count_7d": 0, "news_article_count": 0,
                "news_sentiment_score": 0.0, "news_sentiment_mean": 0.0,
                "news_bullish_pct": 0.0, "news_bearish_pct": 0.0,
                "news_sentiment_shift": 0.0,
                "news_prior_article_count": int(prior_n),
                "news_uses_polygon_score": False,
                "news_sentiment_5d": round(float(sentiment_5d), 4),
                "news_sentiment_30d": round(float(avg_30d), 4),
                "news_volume_zscore_5d": round(float(vol_zscore_5d), 4),
                "news_count_5d": count_5d}

    # Shift only meaningful when prior window has articles to compare against.
    shift = (cur_avg - prior_avg) if prior_n > 0 else 0.0

    avg_r = round(float(cur_avg), 4)

    # B832 SPOF SENTINEL: degenerate emission detection. cur_n>0 here.
    if avg_r == 0.0 and n_pos == 0 and n_neg == 0:
        _spof_record("zero_score")  # articles present but all neutral
    elif not uses_polygon:
        _spof_record("rule_only")   # rule-based fallback active (no Polygon sentiment field)

    return {
        "news_count_7d":             int(cur_n),
        "news_article_count":        int(cur_n),
        "news_sentiment_score":      avg_r,
        "news_sentiment_mean":       avg_r,
        "news_bullish_pct":          round(n_pos / cur_n, 4),
        "news_bearish_pct":          round(n_neg / cur_n, 4),
        "news_sentiment_shift":      round(float(shift), 4),
        "news_prior_article_count":  int(prior_n),
        "news_uses_polygon_score":   bool(uses_polygon),
        # Batch 467 (P10) additions
        "news_sentiment_5d":         round(float(sentiment_5d), 4),
        "news_sentiment_30d":        round(float(avg_30d), 4),
        "news_volume_zscore_5d":     round(float(vol_zscore_5d), 4),
        "news_count_5d":             count_5d,
        # B1243 (Council 291 S5-B1212): diagnostic - which source populated this signal
        "news_source":               news_source,
    }
