"""
data/smart_money.py — Smart money + analyst consensus data.

Sources (Pass 53 DEC-497 NO-LIVE-API + DEC-503 second test pyramid application
2026-05-05; D4 owner-approved yfinance total cut runtime):
  - Quiver Quantitative paid (Trader tier per DEC-450):
      * congressional — historical/congresstrading/{ticker} (per-ticker, works in tier)
      * insider — live/insidertrading bulk feed (BUG-272 fix; historical/insidertrading 404s)
      * 13F — live/sec13f bulk feed (BUG-273 fix; historical/institutionalholdings 404s)
      * lobbying / govcontracts — per-ticker (works)
  - Polygon Stocks Starter (DEC-441/444):
      * EPS estimates / financials -> data_prefetch/polygon/financials/<TICKER>.parquet
        (Sprint 0A Batch 4 populates; pre-Batch-4 returns "not_available")
  - SEC EDGAR via edgartools (DEC-456 + R1 owner-approved Pass 53):
      * Form 4 (insider direct), 8-K (material events), 13D/G (5%+ activists)
      * Sprint 0A Batch 11 prefetches; reads from data_prefetch/sec_edgar/...
  - News sentiment: legacy AV+Finnhub paths retained until Batch 13 migration
    to data_prefetch/polygon/news/.

All functions enforce point-in-time data (as_of parameter).
QUIVER_API_KEY env var: live smoke tests only; runtime backtest reads from
cache/quiver/ + data_prefetch/ exclusively (NO LIVE API — DEC-497 HARD CUT).
yfinance: REMOVED runtime per DEC-497 + D4 owner-approved 2026-05-05.
"""

import os
import time
import logging
import requests
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

QUIVER_KEY  = os.environ.get("QUIVER_API_KEY", "")
QUIVER_BASE = "https://api.quiverquant.com/beta"
_DELAY      = 1.5

# Pre-fetch cache directory — populated by scripts/prefetch_quiver.py
# Sprint 0A.8 (Batch 13) will migrate to data_prefetch/quiver/. Until then,
# legacy path retained for backwards compatibility.
PREFETCH_DIR = Path(__file__).parent / "cache" / "quiver"

# Module-level bulk-feed cache (loaded once per process; thread-safe via GIL)
# BUG-272/273 Pass 53 fix: Quiver Trader tier exposes Live <dataset> as paginated
# bulk feeds (no per-ticker endpoint), so cache is single global.parquet per dataset
# and we filter by Ticker column at read time.
_BULK_CACHE: dict[str, Optional[pd.DataFrame]] = {}


def _load_prefetch(dataset: str, ticker: str) -> Optional[pd.DataFrame]:
    """Load pre-fetched Quiver data from Parquet cache. Returns None if not cached.

    Per-ticker pattern. Used for endpoints with per-ticker variants
    (congresstrading, lobbying, govcontracts, offexchange, topshareholders, etc.).
    """
    path = PREFETCH_DIR / dataset / f"{ticker.replace('-','_')}.parquet"
    if not path.exists():
        return None
    try:
        df = pd.read_parquet(path)
        return df if not df.empty else pd.DataFrame()
    except Exception as exc:
        logger.debug("prefetch load %s/%s: %s", dataset, ticker, exc)
        return None


def _load_quiver_bulk(dataset: str) -> pd.DataFrame:
    """Load Quiver bulk-feed parquet from cache/quiver/<dataset>/global.parquet.

    BUG-272/273 Pass 53 (DEC-503 second test pyramid application):
    Migration from per-ticker live API calls to bulk-feed cache reads.

    Quiver Trader-tier exposes these as paginated bulk feeds without per-ticker
    endpoints — Sprint 0A.5 prefetch (Batch 10) populates the bulk parquet;
    runtime reads filter the bulk DataFrame by `Ticker` column.

    Returns empty DataFrame if file missing (graceful degradation pre-prefetch).
    Cached per-process via _BULK_CACHE module global.

    Used by insider_signal (`live/insidertrading`) + institutional_signal
    (`live/sec13f`) per BUG-272/BUG-273 silent-gap fix.
    """
    if dataset in _BULK_CACHE:
        cached = _BULK_CACHE[dataset]
        return cached if cached is not None else pd.DataFrame()
    path = PREFETCH_DIR / dataset / "global.parquet"
    if not path.exists():
        logger.debug(
            "Quiver bulk feed not yet prefetched (Sprint 0A.5/Batch 10 will populate): %s", path
        )
        _BULK_CACHE[dataset] = None
        return pd.DataFrame()
    try:
        df = pd.read_parquet(path)
        _BULK_CACHE[dataset] = df
        logger.info("Loaded Quiver bulk feed %s: %d rows", dataset, len(df))
        return df
    except Exception as exc:
        logger.warning("Quiver bulk feed load failed for %s: %s", dataset, exc)
        _BULK_CACHE[dataset] = None
        return pd.DataFrame()


def _filter_bulk_by_ticker(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Filter a Quiver bulk DataFrame by Ticker column (case-insensitive)."""
    if df.empty or "Ticker" not in df.columns:
        return df
    return df[df["Ticker"].astype(str).str.upper() == ticker.upper()].copy()


def _reset_bulk_cache_for_tests():
    """Test-only helper: reset module-level bulk cache so tests don't leak state."""
    _BULK_CACHE.clear()


def _quiver_get(endpoint: str) -> Optional[list]:
    if not QUIVER_KEY:
        return None
    try:
        resp = requests.get(
            f"{QUIVER_BASE}/{endpoint}",
            headers={"Authorization": f"Token {QUIVER_KEY}"},
            timeout=20,
        )
        if resp.status_code == 429:
            time.sleep(60)
            return None
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        logger.debug("Quiver %s: %s", endpoint, exc)
        return None


def _get_quiver_data(dataset: str, endpoint_path: str, ticker: str) -> Optional[list]:
    """
    Load Quiver data — tries pre-fetch cache first, falls back to live API.
    Pre-fetch cache is populated by scripts/prefetch_quiver.py.
    """
    cached = _load_prefetch(dataset, ticker)
    if cached is not None:
        logger.debug("Prefetch cache hit: %s/%s (%d rows)", dataset, ticker, len(cached))
        return cached.to_dict("records") if not cached.empty else []
    # Cache miss — return empty (do NOT fallback to live API during backtest)
    # Live API fallback would exhaust rate limits and violate point-in-time.
    # Run scripts/prefetch_quiver.py to populate cache before Phase 1B.
    logger.debug("Prefetch cache miss: %s/%s — returning empty (pre-fetch required)", dataset, ticker)
    return []


# ─────────────────────────────────────────────────────────────────────────────
# ANALYST CONSENSUS
# BUG-271 Pass 53 (DEC-503 second test pyramid application):
#   REMOVED Quiver `historical/analystestimates` branch — endpoint NOT in Trader
#   tier per Pass 53 dashboard inventory + smoke test 2026-05-05 (404).
#   REMOVED yfinance branches per DEC-497 NO-LIVE-API HARD CUT (D4 owner approval
#   2026-05-05).
#   Function now reads from data_prefetch/polygon/financials/{ticker}.parquet
#   (populated by Sprint 0A Batch 4). Pre-Batch-4: returns "not_available"
#   gracefully. Polygon Stocks Starter financials endpoint covers EPS estimates
#   only — analyst consensus + recommendation count + price target fields will
#   remain "not_available" until/unless an analyst-consensus subscription is
#   added in Phase 1B/1C (FMP per DEC-461 candidate).
# ─────────────────────────────────────────────────────────────────────────────

# data_prefetch root for NO-LIVE-API reads (DEC-497)
_REPO_ROOT = Path(__file__).parent.parent.parent
PREFETCH_POLYGON_FINANCIALS_DIR = _REPO_ROOT / "data_prefetch" / "polygon" / "financials"


def get_analyst_data(ticker: str, as_of: date) -> dict:
    """
    Fetch analyst consensus, price targets, EPS estimates, and recent revisions
    from data_prefetch/polygon/financials/ (populated by Sprint 0A Batch 4).

    Returns dict with default `signal="not_available"` if cache miss (graceful
    pre-prefetch state). When Batch 4 populates cache, EPS estimates fields
    populated; analyst-consensus fields (buy/hold/sell counts, price targets)
    remain "not_available" until FMP/equivalent subscribed (DEC-461 candidate).

    BUG-271 + DEC-497 + D4 owner-approved Pass 53: NO yfinance + NO Quiver
    historical/analystestimates (both removed; endpoint 404 / yfinance-cut).

    Returns dict with:
      consensus, buy_count, hold_count, sell_count, total_analysts, buy_pct,
      target_mean, target_high, target_low, target_upside_pct,
      eps_estimate_next_q, eps_estimate_next_y, recent_upgrades,
      recent_downgrades, revision_direction, signal.
    """
    result = {
        "consensus": "unknown", "buy_count": 0, "hold_count": 0,
        "sell_count": 0, "total_analysts": 0, "buy_pct": 0.0,
        "target_mean": None, "target_high": None, "target_low": None,
        "target_upside_pct": None, "eps_estimate_next_q": None,
        "eps_estimate_next_y": None, "recent_upgrades": 0,
        "recent_downgrades": 0, "revision_direction": "flat",
        "signal": "not_available",
    }
    safe_ticker = ticker.replace("-", "_").replace(".", "_")
    path = PREFETCH_POLYGON_FINANCIALS_DIR / f"{safe_ticker}.parquet"
    if not path.exists():
        # Pre-Batch-4 graceful state — no Polygon financials prefetch yet.
        # signal="not_available" surfaces as no-input to agents (Fundamental Agent
        # treats as missing data, doesn't fall back to stale yfinance per DEC-497).
        return result

    try:
        df = pd.read_parquet(path)
        if df.empty:
            return result
        # Schema TBD post-Batch-4. Polygon /vX/reference/financials returns
        # standardized GAAP statements; EPS estimates are NOT included (those
        # come from analyst consensus providers). Filter PIT by filing_date <= as_of.
        if "filing_date" in df.columns:
            df["filing_date"] = pd.to_datetime(df["filing_date"]).dt.date
            df = df[df["filing_date"] <= as_of]
        if df.empty:
            return result
        # Per-filing fundamentals available — defer field-level extraction to
        # Batch 13 NO-LIVE-API refactor when full schema is locked. For Batch 1
        # signal value: presence of any post-PIT row → "available_unparsed",
        # consumed by Fundamental Agent as raw context (no derived signal).
        result["signal"] = "available_unparsed"
        return result
    except Exception as exc:
        logger.debug("get_analyst_data(%s): %s", ticker, exc)
        return result


def analyst_bullets(analyst: dict, current_price: Optional[float] = None) -> list:
    """
    Generate bullet points for the site card analyst section.
    Returns list of plain-English strings.
    """
    bullets = []
    n     = analyst.get("total_analysts", 0)
    cons  = analyst.get("consensus", "Unknown")
    b_pct = analyst.get("buy_pct", 0)
    b_cnt = analyst.get("buy_count", 0)
    h_cnt = analyst.get("hold_count", 0)
    s_cnt = analyst.get("sell_count", 0)

    if n > 0:
        bullets.append(
            f"Analyst consensus: {cons} — {b_cnt} Buy / {h_cnt} Hold / {s_cnt} Sell "
            f"({n} analysts covering)"
        )

    tgt = analyst.get("target_mean")
    upside = analyst.get("target_upside_pct")
    if tgt:
        upside_str = f" — {upside:+.1f}% from current" if upside is not None else ""
        bullets.append(f"Average price target: ${tgt:.2f}{upside_str}")

    tgt_h = analyst.get("target_high")
    tgt_l = analyst.get("target_low")
    if tgt_h and tgt_l:
        bullets.append(f"Target range: ${tgt_l:.2f} – ${tgt_h:.2f}")

    eps_q = analyst.get("eps_estimate_next_q")
    if eps_q is not None:
        bullets.append(f"EPS estimate next quarter: ${eps_q:.2f} (consensus)")

    ups   = analyst.get("recent_upgrades", 0)
    downs = analyst.get("recent_downgrades", 0)
    rev   = analyst.get("revision_direction", "flat")
    if ups > 0 or downs > 0:
        if rev == "up":
            bullets.append(
                f"{ups} upgrade{'s' if ups != 1 else ''} in last 30 days — "
                f"positive estimate momentum"
            )
        elif rev == "down":
            bullets.append(
                f"⚠️  {downs} downgrade{'s' if downs != 1 else ''} in last 30 days — "
                f"negative estimate momentum"
            )
        else:
            bullets.append(f"Mixed revisions: {ups} up / {downs} down in last 30 days")

    if not bullets:
        bullets.append("Analyst data unavailable for this instrument")

    return bullets


# ─────────────────────────────────────────────────────────────────────────────
# CONGRESSIONAL TRADES
# ─────────────────────────────────────────────────────────────────────────────

def congressional_signal(ticker: str, as_of: date, lookback_days: int = 45) -> dict:
    data = _get_quiver_data("congressional", f"historical/congresstrading/{ticker}", ticker)
    if not data:
        return {"signal": "none", "buy_count": 0, "sell_count": 0}
    try:
        df = pd.DataFrame(data)
        if df.empty:
            return {"signal": "none", "buy_count": 0, "sell_count": 0}

        # DEC-324 fix (Pass 51): use BOTH disclosure_date (PIT availability)
        # AND transaction_date (age-weighting). STOCK Act gives members up
        # to 45 days to disclose; a trade DISCLOSED 5 days ago might have
        # been TRANSACTED 40 days ago. Smart-money signal value comes from
        # when they ACTUALLY POSITIONED, not when paperwork landed.
        # Previously age-weighted by disclosure date, mis-weighting late filings.
        df["disclosure_date"] = pd.to_datetime(
            df.get("ReportDate", df.get("Date", df.get("date", "")))
        ).dt.date
        # Transaction date — fall back to disclosure_date if not present (some
        # Quiver records have only one). Schema field tested: "TransactionDate".
        if "TransactionDate" in df.columns:
            df["transaction_date"] = pd.to_datetime(df["TransactionDate"]).dt.date
        elif "transactionDate" in df.columns:
            df["transaction_date"] = pd.to_datetime(df["transactionDate"]).dt.date
        else:
            # Fallback: disclosure_date as proxy when transaction_date missing
            df["transaction_date"] = df["disclosure_date"]

        # PIT filter: only trades where DISCLOSURE was on/before as_of are visible
        df = df[df["disclosure_date"] <= as_of]

        # Age-weight by TRANSACTION date (when they actually traded)
        window_start = as_of - timedelta(days=lookback_days)
        recent = df[df["transaction_date"] >= window_start].copy()
        # Age-weight: <30 days = full, 30-60 days = 0.5x, >60 days = excluded
        recent["age_days"] = (pd.Timestamp(as_of) - pd.to_datetime(recent["transaction_date"])).dt.days
        recent["weight"]   = recent["age_days"].apply(
            lambda d: 1.0 if d < 30 else 0.5 if d < 60 else 0.0)
        recent = recent[recent["weight"] > 0]  # exclude >60 days

        buys   = recent[recent.get("Transaction","transaction").str.contains(
            "Purchase|Buy", case=False, na=False)]
        sells  = recent[recent.get("Transaction","transaction").str.contains(
            "Sale|Sell", case=False, na=False)]
        senate_buys  = buys[buys.get("Chamber","chamber").str.lower() == "senate"]
        cluster_buy  = buys.get("Representative","representative").nunique() >= 3
        signal = "none"
        if len(sells) > len(buys) and len(sells) >= 2:
            signal = "sell"
        elif len(senate_buys) >= 2 or cluster_buy:
            signal = "strong_buy"
        elif len(buys) >= 1:
            signal = "buy"
        return {"signal": signal, "buy_count": len(buys), "sell_count": len(sells),
                "senate_buys": len(senate_buys), "cluster_buy": cluster_buy}
    except Exception as exc:
        logger.debug("congressional_signal(%s): %s", ticker, exc)
        return {"signal": "none", "buy_count": 0, "sell_count": 0}


# ─────────────────────────────────────────────────────────────────────────────
# INSIDER TRADES
# ─────────────────────────────────────────────────────────────────────────────

def insider_signal(ticker: str, as_of: date, lookback_days: int = 30) -> dict:
    """Insider trading signal from Quiver `live/insidertrading` bulk feed.

    BUG-272 Pass 53 fix (DEC-503 second test pyramid application):
    Migrated from `historical/insidertrading/{ticker}` (404 — NOT IN TRADER TIER)
    to `live/insidertrading` paginated bulk feed (no per-ticker endpoint exists).
    Bulk feed cached as cache/quiver/insidertrading/global.parquet; runtime filters
    by Ticker column. Sprint 0A.5 Batch 10 prefetches the bulk file.
    """
    bulk = _load_quiver_bulk("insidertrading")
    df = _filter_bulk_by_ticker(bulk, ticker)
    if df.empty:
        return {"signal": "none", "buy_count": 0, "sell_count": 0}
    try:
        df["filing_date"] = pd.to_datetime(
            df.get("Date", df.get("date", ""))).dt.date
        df = df[df["filing_date"] <= as_of]
        # Exclude non-discretionary
        tx_col = "Transaction" if "Transaction" in df else "transaction"
        df = df[~df[tx_col].str.contains(
            "Option|Exercise|10b5-1|Gift|Transfer", case=False, na=False)]
        window_start = as_of - timedelta(days=lookback_days)
        recent = df[df["filing_date"] >= window_start]
        buys   = recent[recent[tx_col].str.contains(
            "Purchase|Buy|Acquisition", case=False, na=False)]
        sells  = recent[recent[tx_col].str.contains(
            "Sale|Sell", case=False, na=False)]
        role_col = "InsiderTitle" if "InsiderTitle" in df else "insiderTitle"
        ceo_buy  = buys[role_col].str.contains("CEO|Chief Executive", case=False, na=False).any() \
                   if role_col in buys else False
        cluster  = buys.get("InsiderName", buys.get("insiderName",
                   pd.Series())).nunique() >= 3
        signal   = "none"
        if sells.get("InsiderName", sells.get("insiderName",
                     pd.Series())).nunique() >= 3:
            signal = "cluster_sell"
        elif ceo_buy and cluster:
            signal = "strong_buy"
        elif ceo_buy or cluster:
            signal = "buy"
        elif len(buys) >= 1:
            signal = "weak_buy"
        return {"signal": signal, "buy_count": len(buys), "sell_count": len(sells),
                "ceo_buy": ceo_buy, "cluster_buy": cluster}
    except Exception as exc:
        logger.debug("insider_signal(%s): %s", ticker, exc)
        return {"signal": "none", "buy_count": 0, "sell_count": 0}


# ─────────────────────────────────────────────────────────────────────────────
# INSTITUTIONAL (13F)
# ─────────────────────────────────────────────────────────────────────────────

def institutional_signal(ticker: str, as_of: date) -> dict:
    """13F institutional holdings signal from Quiver `live/sec13f` bulk feed.

    BUG-273 Pass 53 fix (DEC-503 second test pyramid application):
    Migrated from `historical/institutionalholdings/{ticker}` (404 — NOT IN TRADER
    TIER) to `live/sec13f` paginated bulk feed (no per-ticker endpoint exists).
    Bulk feed cached as cache/quiver/sec13f/global.parquet; runtime filters by
    Ticker column. Sprint 0A.5 Batch 10 prefetches the bulk file.
    """
    bulk = _load_quiver_bulk("sec13f")
    df = _filter_bulk_by_ticker(bulk, ticker)
    if df.empty:
        return {"signal": "none"}
    try:
        df["quarter_end"]    = pd.to_datetime(
            df.get("Date", df.get("date", ""))).dt.date
        df["available_after"] = df["quarter_end"].apply(
            lambda d: d + timedelta(days=45) if d else None)
        df = df[df["available_after"] <= as_of]
        if df.empty:
            return {"signal": "none"}
        latest_q = df["quarter_end"].max()
        latest   = df[df["quarter_end"] == latest_q]
        sc = "SharesChange" if "SharesChange" in df else "sharesChange"
        sh = "Shares" if "Shares" in df else "shares"
        df[sc] = pd.to_numeric(df.get(sc, 0), errors="coerce").fillna(0)
        df[sh] = pd.to_numeric(df.get(sh, 0), errors="coerce").fillna(0)
        new_pos   = (latest[sc] == latest[sh]).sum()
        increased = (latest[sc] > 0).sum()
        decreased = (latest[sc] < 0).sum()
        signal = "none"
        if new_pos >= 3 or (new_pos >= 1 and increased >= 2):
            signal = "strong_buy"
        elif new_pos >= 1 or increased >= 2:
            signal = "buy"
        elif decreased > increased:
            signal = "negative"
        return {"signal": signal, "new_positions": int(new_pos),
                "increased": int(increased), "decreased": int(decreased)}
    except Exception as exc:
        logger.debug("institutional_signal(%s): %s", ticker, exc)
        return {"signal": "none"}


# ─────────────────────────────────────────────────────────────────────────────
# COMPOSITE SMART MONEY SCORE
# ─────────────────────────────────────────────────────────────────────────────

def smart_money_score(
    ticker: str, as_of: date,
    cong: Optional[dict] = None,
    ins:  Optional[dict] = None,
    inst: Optional[dict] = None,
) -> dict:
    """
    Compute composite smart money score and return all keys expected by:
    - backtest engine: composite_signal, score, congressional_signal,
                       insider_signal, institutional_signal
    - agent pipeline: congressional_sig, insider_sig, institutional_sig,
                      smart_money_composite
    """
    if cong is None: cong = congressional_signal(ticker, as_of)
    if ins  is None: ins  = insider_signal(ticker, as_of)
    if inst is None: inst = institutional_signal(ticker, as_of)

    cs   = cong.get("signal", "none")
    iss  = ins.get("signal", "none")
    ints = inst.get("signal", "none")

    if cs == "sell" and iss == "cluster_sell":
        composite = "congressional_sell+insider_cluster_sell"
        score = -5
    else:
        score = 0
        if cs  == "strong_buy":   score += 4
        elif cs == "buy":          score += 2
        elif cs == "sell":         score -= 3
        if iss == "strong_buy":   score += 4
        elif iss == "buy":         score += 2
        elif iss == "weak_buy":    score += 1
        elif iss == "cluster_sell": score -= 3
        if ints == "strong_buy":  score += 2
        elif ints == "buy":        score += 1
        elif ints == "negative":   score -= 1

        if score >= 6:    composite = "congressional+insider_cluster"
        elif score >= 4:  composite = "congressional_or_insider"
        elif score >= 2:  composite = "any_buy"
        elif score >= 1:  composite = "weak_buy"
        elif score <= -4: composite = "congressional_sell+insider_cluster_sell"
        elif score < 0:   composite = "negative"
        else:             composite = "none"

    return {
        # Tier assignment keys (backtest engine)
        "composite_signal":      composite,
        "score":                 score,
        "congressional_signal":  cs,
        "insider_signal":        iss,
        "institutional_signal":  ints,
        # Agent pipeline keys
        "congressional_sig":     cong,
        "insider_sig":           ins,
        "institutional_sig":     inst,
        "smart_money_composite": {"composite": composite, "score": score},
        # Detail breakdown
        "details": {"congressional": cs, "insider": iss, "institutional": ints},
    }


# ─────────────────────────────────────────────────────────────────────────────
# ALPHA VANTAGE / FINNHUB NEWS SENTIMENT
# Read from pre-fetched cache (scripts/prefetch_alphavantage_news.py +
# scripts/prefetch_finnhub_news.py). Falls back to neutral if no cache.
# ─────────────────────────────────────────────────────────────────────────────
#
# BUG-217 fix (Pass 48): previous implementation looked at `prefetch/news/`
# with `{ticker}_{year}.parquet` files and a `sentiment_score` column — none
# of which exist. Actual data is in `cache/av_news/` and `cache/finnhub_news/`
# as `{ticker}.parquet` with columns `sentiment_mean` / `sentiment_weighted` /
# `article_count`. This caused get_news_sentiment to return neutral for every
# ticker for every date, silently dropping the prefetched news data.

AV_NEWS_DIR = Path(__file__).parent / "cache" / "av_news"
FH_NEWS_DIR = Path(__file__).parent / "cache" / "finnhub_news"


def get_news_sentiment(ticker: str, as_of: date, lookback_days: int = 7) -> dict:
    """
    Return news sentiment for ticker in the lookback window before as_of.
    Reads from pre-fetched Alpha Vantage cache first, falls back to Finnhub.

    Returns dict:
        sentiment_score: float (-1 to 1), positive = bullish news
        article_count: int — number of articles in window
        signal: bullish | bearish | neutral
        source: alphavantage | finnhub | none
    """
    safe_ticker = ticker.replace("-", "_").replace(".", "_")
    result = {"sentiment_score": 0.0, "article_count": 0,
              "signal": "neutral", "source": "none"}

    for cache_dir, source in [(AV_NEWS_DIR, "alphavantage"),
                               (FH_NEWS_DIR, "finnhub")]:
        path = cache_dir / f"{safe_ticker}.parquet"
        if not path.exists():
            continue
        try:
            df = pd.read_parquet(path)
            if df.empty or "date" not in df.columns:
                continue

            df["date"] = pd.to_datetime(df["date"])
            window_start = pd.Timestamp(as_of - timedelta(days=lookback_days))
            window_end   = pd.Timestamp(as_of)
            window = df[(df["date"] >= window_start) & (df["date"] <= window_end)]

            if window.empty:
                continue

            # Prefer relevance-weighted sentiment when available (AV);
            # fall back to mean sentiment otherwise.
            if "sentiment_weighted" in window.columns:
                avg_score = float(window["sentiment_weighted"].mean())
            elif "sentiment_mean" in window.columns:
                avg_score = float(window["sentiment_mean"].mean())
            elif "sentiment_score" in window.columns:
                # legacy schema fallback
                avg_score = float(window["sentiment_score"].mean())
            else:
                continue

            article_count = (int(window["article_count"].sum())
                             if "article_count" in window.columns
                             else len(window))

            if avg_score >= 0.15:
                signal = "bullish"
            elif avg_score <= -0.15:
                signal = "bearish"
            else:
                signal = "neutral"

            return {
                "sentiment_score": round(avg_score, 3),
                "article_count":   article_count,
                "signal":          signal,
                "source":          source,
            }
        except Exception as exc:
            logger.debug("get_news_sentiment(%s,%s): %s", ticker, source, exc)
            continue

    return result


def get_gov_contracts(ticker: str, as_of: date, lookback_days: int = 365) -> dict:
    """
    Return government contract activity for ticker in lookback window.
    Reads from pre-fetched Quiver gov_contracts cache.
    Point-in-time enforced via Date column.

    Returns dict:
        total_amount: float — total contract value in window
        contract_count: int
        recent_win: bool — contract won in last 90 days
        trend: growing | stable | declining
        signal: bullish | neutral | no_data
    """
    result = {"total_amount": 0.0, "contract_count": 0,
              "recent_win": False, "trend": "stable", "signal": "no_data"}
    df = _load_prefetch("gov_contracts", ticker)
    if df is None or df.empty:
        return result
    try:
        date_col = next((c for c in df.columns if "date" in c.lower()), None)
        if not date_col:
            return result
        df[date_col] = pd.to_datetime(df[date_col])
        window = df[df[date_col] <= pd.Timestamp(as_of)]
        recent = window[window[date_col] >= pd.Timestamp(as_of) - pd.Timedelta(days=lookback_days)]
        if recent.empty:
            return result
        amount_col = next((c for c in df.columns if "amount" in c.lower()), None)
        total = float(recent[amount_col].sum()) if amount_col else 0.0
        recent_90 = window[window[date_col] >= pd.Timestamp(as_of) - pd.Timedelta(days=90)]
        older = window[
            (window[date_col] >= pd.Timestamp(as_of) - pd.Timedelta(days=365)) &
            (window[date_col] < pd.Timestamp(as_of) - pd.Timedelta(days=90))
        ]
        trend = "growing" if len(recent_90) > len(older) / 3 else "stable"
        return {
            "total_amount": round(total, 2),
            "contract_count": len(recent),
            "recent_win": len(recent_90) > 0,
            "trend": trend,
            "signal": "bullish" if total > 0 else "neutral",
        }
    except Exception as exc:
        logger.debug("get_gov_contracts(%s): %s", ticker, exc)
        return result


def get_lobbying(ticker: str, as_of: date, lookback_days: int = 365) -> dict:
    """
    Return lobbying spend activity for ticker.
    Reads from pre-fetched Quiver lobbying cache.

    Returns dict:
        total_spend: float — total lobbying spend in window
        filing_count: int
        issues: list — lobbying issue areas
        signal: high_spend | moderate | low | no_data
    """
    result = {"total_spend": 0.0, "filing_count": 0,
              "issues": [], "signal": "no_data"}
    df = _load_prefetch("lobbying", ticker)
    if df is None or df.empty:
        return result
    try:
        date_col = next((c for c in df.columns if "date" in c.lower()), None)
        if not date_col:
            return result
        df[date_col] = pd.to_datetime(df[date_col])
        window = df[
            (df[date_col] <= pd.Timestamp(as_of)) &
            (df[date_col] >= pd.Timestamp(as_of) - pd.Timedelta(days=lookback_days))
        ]
        if window.empty:
            return result
        amount_col = next((c for c in df.columns if "amount" in c.lower()), None)
        total = float(window[amount_col].sum()) if amount_col else 0.0
        issue_col = next((c for c in df.columns if "issue" in c.lower()), None)
        issues = list(window[issue_col].dropna().unique()[:5]) if issue_col else []
        signal = "high_spend" if total > 1_000_000 else "moderate" if total > 100_000 else "low"
        return {
            "total_spend": round(total, 2),
            "filing_count": len(window),
            "issues": issues,
            "signal": signal,
        }
    except Exception as exc:
        logger.debug("get_lobbying(%s): %s", ticker, exc)
        return result


def get_congressional_detail(ticker: str, as_of: date, top_n: int = 3) -> list:
    """
    Return top N most recent congressional trades with full detail.
    Used by Sentiment Agent for richer context vs composite signal only.
    Point-in-time enforced: only trades disclosed before as_of with 45-day lag.

    Returns list of dicts with: representative, transaction, amount_range,
    transaction_date, party, house
    """
    df = _load_prefetch("congressional", ticker)
    if df is None or df.empty:
        return []
    try:
        df["TransactionDate"] = pd.to_datetime(df["TransactionDate"], errors="coerce")
        df["ReportDate"] = pd.to_datetime(df.get("ReportDate", df["TransactionDate"]),
                                           errors="coerce")
        cutoff = pd.Timestamp(as_of) - pd.Timedelta(days=45)
        available = df[df["ReportDate"] <= cutoff].copy()
        if available.empty:
            return []
        available = available.sort_values("TransactionDate", ascending=False)
        top = available.head(top_n)
        return [
            {
                "representative": row.get("Representative", "Unknown"),
                "party": row.get("Party", ""),
                "house": row.get("House", ""),
                "transaction": row.get("Transaction", ""),
                "amount_range": row.get("Range", row.get("Amount", "")),
                "transaction_date": str(row.get("TransactionDate", ""))[:10],
                "days_ago": (pd.Timestamp(as_of) - row.get("TransactionDate",
                             pd.Timestamp(as_of))).days,
            }
            for _, row in top.iterrows()
        ]
    except Exception as exc:
        logger.debug("get_congressional_detail(%s): %s", ticker, exc)
        return []
