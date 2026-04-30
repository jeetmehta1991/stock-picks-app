"""
data/smart_money.py — Smart money + analyst consensus data.

Sources:
  - Quiver Quantitative free tier: congressional, insider, 13F, analyst revisions
  - yfinance: analyst consensus, price targets, EPS estimates (no key required)
  - SEC EDGAR: Form 4, 13D/13G
  - OpenInsider: insider trades

All functions enforce point-in-time data (as_of parameter).
QUIVER_API_KEY env var required for Quiver data — gracefully skips if absent.
yfinance analyst data requires no API key.
"""

import os
import time
import logging
import requests
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

QUIVER_KEY  = os.environ.get("QUIVER_API_KEY", "")
QUIVER_BASE = "https://api.quiverquant.com/beta"
_DELAY      = 1.5

# Pre-fetch cache directory — populated by scripts/prefetch_quiver.py
PREFETCH_DIR = Path(__file__).parent / "cache" / "quiver"


def _load_prefetch(dataset: str, ticker: str) -> Optional[pd.DataFrame]:
    """Load pre-fetched Quiver data from Parquet cache. Returns None if not cached."""
    path = PREFETCH_DIR / dataset / f"{ticker.replace('-','_')}.parquet"
    if not path.exists():
        return None
    try:
        df = pd.read_parquet(path)
        return df if not df.empty else pd.DataFrame()
    except Exception as exc:
        logger.debug("prefetch load %s/%s: %s", dataset, ticker, exc)
        return None


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
# ANALYST CONSENSUS — yfinance primary, no API key required
# ─────────────────────────────────────────────────────────────────────────────

def get_analyst_data(ticker: str, as_of: date) -> dict:
    """
    Fetch analyst consensus, price targets, EPS estimates, and recent revisions.

    IMPORTANT — LIVE-ONLY DATA WARNING:
    Fields from yfinance t.info (recommendationMean, targetMeanPrice, eps estimates)
    always return CURRENT values, not historical values as-of the backtest date.
    These fields are used for site card display only — they do NOT affect confidence
    tier calculations, strategy pass/fail criteria, or backtest metrics.
    Point-in-time enforcement applies to recommendations history and upgrades/downgrades
    only (filtered by as_of date below).

    Returns dict with:
      consensus          — Strong Buy / Buy / Hold / Sell / Strong Sell
      buy_count          — number of Buy + Strong Buy ratings
      hold_count         — number of Hold ratings
      sell_count         — number of Sell + Strong Sell ratings
      total_analysts     — total analysts covering
      buy_pct            — % of analysts with Buy/Strong Buy
      target_mean        — average price target
      target_high        — highest price target
      target_low         — lowest price target
      target_upside_pct  — % upside from current price to mean target
      eps_estimate_next_q — EPS consensus estimate next quarter
      eps_estimate_next_y — EPS consensus estimate next year
      recent_upgrades    — upgrades in last 30 days (from Quiver if available)
      recent_downgrades  — downgrades in last 30 days
      revision_direction — "up" / "down" / "flat"
      signal             — "strong_buy" / "buy" / "hold" / "sell" / "unknown"
    """
    result = {
        "consensus": "unknown", "buy_count": 0, "hold_count": 0,
        "sell_count": 0, "total_analysts": 0, "buy_pct": 0.0,
        "target_mean": None, "target_high": None, "target_low": None,
        "target_upside_pct": None, "eps_estimate_next_q": None,
        "eps_estimate_next_y": None, "recent_upgrades": 0,
        "recent_downgrades": 0, "revision_direction": "flat",
        "signal": "unknown",
    }
    try:
        t    = yf.Ticker(ticker)
        info = t.info

        # Consensus label
        rec_mean = info.get("recommendationMean")   # 1=Strong Buy, 5=Strong Sell
        rec_key  = info.get("recommendationKey", "").lower()
        result["consensus"] = {
            "strong_buy": "Strong Buy", "buy": "Buy",
            "hold": "Hold", "sell": "Sell", "strong_sell": "Strong Sell",
        }.get(rec_key, rec_key.replace("_"," ").title() if rec_key else "Unknown")

        # Analyst counts
        n = info.get("numberOfAnalystOpinions", 0) or 0
        result["total_analysts"] = n

        # Price targets
        cur  = info.get("currentPrice") or info.get("regularMarketPrice")
        mean = info.get("targetMeanPrice")
        high = info.get("targetHighPrice")
        low  = info.get("targetLowPrice")
        result["target_mean"] = round(mean, 2) if mean else None
        result["target_high"] = round(high, 2) if high else None
        result["target_low"]  = round(low,  2) if low  else None
        if mean and cur and cur > 0:
            result["target_upside_pct"] = round((mean - cur) / cur * 100, 2)

        # EPS estimates
        try:
            earnings = t.earnings_estimate
            if earnings is not None and not earnings.empty:
                if "0q" in earnings.index:
                    result["eps_estimate_next_q"] = earnings.loc["0q", "Avg"] \
                        if "Avg" in earnings.columns else None
                if "0y" in earnings.index:
                    result["eps_estimate_next_y"] = earnings.loc["0y", "Avg"] \
                        if "Avg" in earnings.columns else None
        except Exception:
            pass

        # Recommendations history — parse buy/hold/sell counts and recent changes
        try:
            recs = t.recommendations
            if recs is not None and not recs.empty:
                # Point-in-time: only use recommendations on or before as_of
                recs.index = pd.to_datetime(recs.index).tz_localize(None)
                recs = recs[recs.index.date <= as_of]
                if not recs.empty:
                    # Count latest snapshot
                    latest = recs.iloc[-1]
                    sb = int(latest.get("strongBuy", 0) or 0)
                    b  = int(latest.get("buy",       0) or 0)
                    h  = int(latest.get("hold",      0) or 0)
                    s  = int(latest.get("sell",      0) or 0)
                    ss = int(latest.get("strongSell",0) or 0)
                    total = sb + b + h + s + ss
                    result["buy_count"]      = sb + b
                    result["hold_count"]     = h
                    result["sell_count"]     = s + ss
                    result["total_analysts"] = total
                    result["buy_pct"]        = round((sb+b)/total*100, 1) if total else 0
        except Exception:
            pass

        # Recent upgrades/downgrades (last 30 days)
        try:
            upgrades = t.upgrades_downgrades
            if upgrades is not None and not upgrades.empty:
                upgrades.index = pd.to_datetime(upgrades.index).tz_localize(None)
                window_start   = pd.Timestamp(as_of - timedelta(days=30))
                recent = upgrades[
                    (upgrades.index >= window_start) &
                    (upgrades.index.date <= as_of)
                ]
                if not recent.empty and "Action" in recent.columns:
                    result["recent_upgrades"]   = int((recent["Action"].str.lower() == "up").sum())
                    result["recent_downgrades"]  = int((recent["Action"].str.lower() == "down").sum())
                    ups   = result["recent_upgrades"]
                    downs = result["recent_downgrades"]
                    result["revision_direction"] = (
                        "up"   if ups > downs else
                        "down" if downs > ups else "flat"
                    )
        except Exception:
            pass

        # Quiver analyst revisions enhancement (if key available)
        if QUIVER_KEY:
            quiver_revs = _quiver_get(f"historical/analystestimates/{ticker}")
            if quiver_revs:
                time.sleep(_DELAY)
                df_q = pd.DataFrame(quiver_revs)
                if not df_q.empty and "Date" in df_q.columns:
                    df_q["Date"] = pd.to_datetime(df_q["Date"]).dt.date
                    recent_q = df_q[
                        (df_q["Date"] >= as_of - timedelta(days=30)) &
                        (df_q["Date"] <= as_of)
                    ]
                    if not recent_q.empty:
                        # Quiver provides direction field
                        if "Direction" in recent_q.columns:
                            ups   = (recent_q["Direction"].str.lower() == "up").sum()
                            downs = (recent_q["Direction"].str.lower() == "down").sum()
                            result["recent_upgrades"]   = max(result["recent_upgrades"],   int(ups))
                            result["recent_downgrades"] = max(result["recent_downgrades"], int(downs))
                            if ups > downs:
                                result["revision_direction"] = "up"
                            elif downs > ups:
                                result["revision_direction"] = "down"

        # Derive signal
        buy_pct = result["buy_pct"]
        rev     = result["revision_direction"]
        ups_cnt = result["recent_upgrades"]
        if buy_pct >= 70 and rev == "up" and ups_cnt >= 2:
            result["signal"] = "strong_buy"
        elif buy_pct >= 60 and rev in ("up", "flat"):
            result["signal"] = "buy"
        elif buy_pct < 40 or rev == "down":
            result["signal"] = "sell"
        elif result["total_analysts"] > 0:
            result["signal"] = "hold"

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
    data = _get_quiver_data("insider", f"historical/insidertrading/{ticker}", ticker)
    if not data:
        return {"signal": "none", "buy_count": 0, "sell_count": 0}
    try:
        df = pd.DataFrame(data)
        if df.empty:
            return {"signal": "none", "buy_count": 0, "sell_count": 0}
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
    data = _get_quiver_data("institutional", f"historical/institutionalholdings/{ticker}", ticker)
    if not data:
        return {"signal": "none"}
    try:
        df = pd.DataFrame(data)
        if df.empty:
            return {"signal": "none"}
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
