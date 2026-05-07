"""
data/sentiment.py — Sentiment signal data fetchers.

Sources (all free, no API key required):
  - AAII Investor Sentiment Survey: weekly bullish/bearish readings
  - CNN Fear & Greed Index: daily composite 0-100
  - COT (Commitment of Traders): CFTC weekly — commercial vs speculative positioning

All functions enforce point-in-time data (as_of parameter).

AAII data: loaded from backtest/data/aaii_sentiment.csv — full weekly history 2020-2024.
  Downloaded from aaii.com/sentimentsurvey/sent_results and committed to repo.
  Update annually by downloading fresh XLS from AAII and running the parser.

CNN Fear & Greed: loaded from backtest/data/cnn_fear_greed.csv — daily history 2020-2024.
  Downloaded from CNN unofficial API and committed to repo.
"""

import logging
import requests
import io
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# AAII SENTIMENT SURVEY
# Weekly reading — published every Thursday.
# Extreme bearishness (>50% bears) = contrarian buy signal.
# Extreme bullishness (>50% bulls) = contrarian sell warning.
#
# Loaded from aaii_sentiment.csv — full 2020-2026 weekly history (325 readings).
# ---------------------------------------------------------------------------

_AAII_DF: Optional[pd.DataFrame] = None


def _load_aaii() -> pd.DataFrame:
    """Load AAII weekly sentiment.

    Pass 53 Day-9 v8c G2 fix (L146 wiring): Sprint 0A canonical path
    ``data_prefetch/aaii/weekly_sentiment.parquet`` is preferred (auto-refreshed
    via GH Actions); legacy CSV ``backtest/data/aaii_sentiment.csv`` is fallback
    for backwards-compat. Schemas match exactly: date / bullish / neutral /
    bearish / bull_bear_spread.
    """
    global _AAII_DF
    if _AAII_DF is not None:
        return _AAII_DF
    repo_root = Path(__file__).parent.parent.parent
    parquet_path = repo_root / "data_prefetch" / "aaii" / "weekly_sentiment.parquet"
    csv_path = DATA_DIR / "aaii_sentiment.csv"
    df = None
    if parquet_path.exists():
        try:
            df = pd.read_parquet(parquet_path)
            df["date"] = pd.to_datetime(df["date"])
            logger.info("AAII: loaded %d weekly readings from Sprint 0A parquet",
                        len(df))
        except Exception as exc:
            logger.warning("AAII parquet read failed (%s); falling back to CSV", exc)
            df = None
    if df is None and csv_path.exists():
        df = pd.read_csv(csv_path, parse_dates=["date"])
        logger.info("AAII: loaded %d weekly readings from legacy CSV", len(df))
    if df is None:
        logger.warning("AAII not found at parquet OR CSV — using empty dataset")
        _AAII_DF = pd.DataFrame(columns=["survey_date","bullish_pct",
                                          "bearish_pct","neutral_pct"])
        return _AAII_DF
    df = df.rename(columns={"date": "survey_date", "bullish": "bullish_pct",
                             "bearish": "bearish_pct", "neutral": "neutral_pct"})
    _AAII_DF = df.sort_values("survey_date").reset_index(drop=True)
    return _AAII_DF


def get_aaii_sentiment(as_of: date) -> dict:
    """
    Return most recent AAII sentiment reading on or before `as_of`.
    Returns dict: survey_date, bullish_pct, bearish_pct, neutral_pct, signal
    """
    df = _load_aaii()
    available = df[df["survey_date"] <= pd.Timestamp(as_of)]
    if available.empty:
        return {"signal": "unknown", "bullish_pct": None, "bearish_pct": None}

    row = available.iloc[-1]
    bull = row["bullish_pct"]
    bear = row["bearish_pct"]

    # Contrarian signals
    if bear > 55:
        signal = "extreme_fear_contrarian_buy"
    elif bear > 45:
        signal = "high_bearishness_bullish"
    elif bull > 55:
        signal = "extreme_greed_contrarian_sell"
    elif bull > 45:
        signal = "elevated_bullishness_neutral"
    else:
        signal = "neutral"

    return {
        "survey_date":  row["survey_date"],
        "bullish_pct":  bull,
        "bearish_pct":  bear,
        "neutral_pct":  row["neutral_pct"],
        "signal":       signal,
    }


# ---------------------------------------------------------------------------
# CNN FEAR & GREED INDEX
# 0 = Extreme Fear (buy), 100 = Extreme Greed (sell warning)
# Source: CNN Markets — live scraping for Stage 3+; sampled data for backtest.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# CNN FEAR & GREED INDEX
# 0 = Extreme Fear (buy), 100 = Extreme Greed (sell warning)
# Loaded from cnn_fear_greed.csv — 1,630 daily readings 2020-2026.
# Built from CNN archives and interpolated between key readings.
# For Stage 3+ live trading: scrape CNN directly.
# ---------------------------------------------------------------------------

_CNN_DF: Optional[pd.DataFrame] = None


def _load_cnn() -> pd.DataFrame:
    """Load CNN Fear & Greed daily readings.

    Pass 53 Day-9 v8c G3 review (L146): Sprint 0A canonical path
    ``data_prefetch/cnn_fg/daily.parquet`` only has ~253 rows (~1 year, 2025-05+)
    because CNN's API has limited history. Legacy CSV
    ``backtest/data/cnn_fear_greed.csv`` has 1630 daily readings (2020-2026)
    built from CNN archives + interpolation, providing complete backtest history.
    Reads CSV (canonical for backtest), then merges any newer parquet rows.
    """
    global _CNN_DF
    if _CNN_DF is not None:
        return _CNN_DF
    repo_root = Path(__file__).parent.parent.parent
    parquet_path = repo_root / "data_prefetch" / "cnn_fg" / "daily.parquet"
    csv_path = DATA_DIR / "cnn_fear_greed.csv"

    df_csv = None
    if csv_path.exists():
        df_csv = pd.read_csv(csv_path, parse_dates=["date"])
        df_csv = df_csv.rename(columns={"date": "reading_date"})

    df_parquet = None
    if parquet_path.exists():
        try:
            tmp = pd.read_parquet(parquet_path)
            if "date" in tmp.columns:
                tmp["reading_date"] = pd.to_datetime(tmp["date"])
            tmp = tmp.rename(columns={"rating": "label"})
            df_parquet = tmp[["reading_date", "score", "label"]].copy()
        except Exception as exc:
            logger.debug("CNN parquet read skipped (%s); using CSV only", exc)

    if df_csv is not None and df_parquet is not None:
        # CSV has full history; parquet has any newer rows
        max_csv = df_csv["reading_date"].max()
        newer = df_parquet[df_parquet["reading_date"] > max_csv]
        merged = pd.concat([df_csv, newer], ignore_index=True)
        _CNN_DF = merged.sort_values("reading_date").reset_index(drop=True)
        logger.info("CNN F&G: %d CSV + %d newer parquet rows = %d total",
                    len(df_csv), len(newer), len(_CNN_DF))
    elif df_csv is not None:
        _CNN_DF = df_csv.sort_values("reading_date").reset_index(drop=True)
        logger.info("CNN F&G: loaded %d daily readings from legacy CSV", len(_CNN_DF))
    elif df_parquet is not None:
        _CNN_DF = df_parquet.sort_values("reading_date").reset_index(drop=True)
        logger.info("CNN F&G: loaded %d daily readings from Sprint 0A parquet "
                    "(legacy CSV missing — limited history)", len(_CNN_DF))
    else:
        logger.warning("CNN F&G not found at parquet OR CSV — using empty dataset")
        _CNN_DF = pd.DataFrame(columns=["reading_date","score","label"])
    return _CNN_DF


def get_fear_and_greed(as_of: date) -> dict:
    """
    Return most recent CNN Fear & Greed reading on or before `as_of`.
    Returns dict: reading_date, score (0-100), label, signal
    """
    df = _load_cnn()
    available = df[df["reading_date"] <= pd.Timestamp(as_of)]
    if available.empty:
        return {"signal": "unknown", "score": None}

    row = available.iloc[-1]
    score = row["score"]

    if score <= 20:
        signal = "extreme_fear_buy"
    elif score <= 35:
        signal = "fear_lean_buy"
    elif score >= 80:
        signal = "extreme_greed_sell_warning"
    elif score >= 65:
        signal = "greed_caution"
    else:
        signal = "neutral"

    return {
        "reading_date": row["reading_date"],
        "score":        score,
        "label":        row["label"],
        "signal":       signal,
    }


# ---------------------------------------------------------------------------
# COT — COMMITMENT OF TRADERS
# CFTC.gov — weekly, released every Friday for prior Tuesday positioning.
# Commercial hedgers = smart money. Speculators (large non-commercials) often
# wrong at extremes. Extreme commercial long + speculator short = buy signal.
#
# For backtesting: we track S&P 500 E-mini futures (CME Code 13874+)
# as a proxy for broad market sentiment positioning.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Pass 53 Batch 13 sub-tasks 4 + 5 (DEC-507 wiring matrix Row 5 closure)
# Reads from data_prefetch/ paths (Sprint 0A Batches 7/8/9 v2/12-a prefetched).
# ---------------------------------------------------------------------------

_REPO_ROOT_SENT = Path(__file__).parent.parent.parent
PREFETCH_CNN_COMPONENTS_DIR = _REPO_ROOT_SENT / "data_prefetch" / "cnn_fg" / "components"
PREFETCH_APEWISDOM = _REPO_ROOT_SENT / "data_prefetch" / "apewisdom" / "global.parquet"
PREFETCH_WIKIPEDIA_DIR = _REPO_ROOT_SENT / "data_prefetch" / "wikipedia"
PREFETCH_CFTC_COT = _REPO_ROOT_SENT / "data_prefetch" / "cftc" / "cot_emini_sp500.parquet"

CNN_COMPONENT_NAMES = [
    "junk_bond_demand",
    "put_call_options",
    "market_momentum_sp500",
    "stock_price_breadth",
    "safe_haven_demand",
    "market_volatility_vix",
    "stock_price_strength",
]


def get_cnn_components(as_of: date) -> dict:
    """Return CNN Fear & Greed 7 sub-components at as_of (Pass 53 Batch 7).

    Returns dict {component_name: {"score": float, "rating": str, "date": ...}}
    Component score 0-100 (low = fear, high = greed).
    """
    out = {}
    for comp in CNN_COMPONENT_NAMES:
        path = PREFETCH_CNN_COMPONENTS_DIR / f"{comp}.parquet"
        if not path.exists():
            out[comp] = {"score": None, "rating": "unknown"}
            continue
        try:
            df = pd.read_parquet(path)
            if df.empty or "date" not in df.columns or "score" not in df.columns:
                out[comp] = {"score": None, "rating": "unknown"}
                continue
            df["date"] = pd.to_datetime(df["date"]).dt.date
            df = df[df["date"] <= as_of]
            if df.empty:
                out[comp] = {"score": None, "rating": "unknown"}
                continue
            row = df.iloc[-1]
            out[comp] = {
                "score": float(row["score"]),
                "rating": str(row.get("rating", "")),
                "date": str(row["date"]),
            }
        except Exception as exc:
            logger.debug("get_cnn_components(%s): %s", comp, exc)
            out[comp] = {"score": None, "rating": "unknown"}
    return out


def get_apewisdom_mentions(ticker: str) -> dict:
    """Apewisdom WSB+r/stocks ticker mentions (Pass 53 Batch 12-a).

    Returns dict with mentions / mentions_24h / rank / sentiment for ticker;
    returns {"signal": "no_data"} if not in latest snapshot.
    """
    if not PREFETCH_APEWISDOM.exists():
        return {"signal": "no_data"}
    try:
        df = pd.read_parquet(PREFETCH_APEWISDOM)
        if df.empty or "ticker" not in df.columns:
            return {"signal": "no_data"}
        match = df[df["ticker"].astype(str).str.upper() == ticker.upper()]
        if match.empty:
            return {"signal": "no_mentions", "mentions": 0}
        row = match.iloc[0]
        return {
            "signal": "tracked",
            "mentions": int(row.get("mentions", 0) or 0),
            "mentions_24h": int(row.get("mentions_24h", 0) or 0),
            "rank": int(row.get("rank", 999) or 999),
            "sentiment": float(row.get("sentiment", 0) or 0),
        }
    except Exception as exc:
        logger.debug("get_apewisdom_mentions(%s): %s", ticker, exc)
        return {"signal": "no_data"}


def get_wikipedia_pageviews(ticker: str, as_of: date, lookback_days: int = 7) -> dict:
    """Wikipedia pageviews for ticker over lookback window (Pass 53 Batch 12-a).

    Returns dict with views_total / views_avg / signal (above_avg/normal/below_avg
    relative to 90-day baseline).
    """
    safe_ticker = ticker.replace("-", "_").replace(".", "_")
    path = PREFETCH_WIKIPEDIA_DIR / f"{safe_ticker}.parquet"
    if not path.exists():
        return {"signal": "no_data"}
    try:
        df = pd.read_parquet(path)
        if df.empty or "date" not in df.columns or "views" not in df.columns:
            return {"signal": "no_data"}
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df = df[df["date"] <= as_of]
        if df.empty:
            return {"signal": "no_data"}
        # Recent window
        window_start = as_of - timedelta(days=lookback_days)
        recent = df[df["date"] >= window_start]
        if recent.empty:
            return {"signal": "no_data"}
        recent_avg = float(recent["views"].mean())
        # 90-day baseline (excluding recent window)
        baseline_start = as_of - timedelta(days=90)
        baseline = df[(df["date"] >= baseline_start) & (df["date"] < window_start)]
        baseline_avg = float(baseline["views"].mean()) if not baseline.empty else recent_avg
        ratio = recent_avg / baseline_avg if baseline_avg > 0 else 1.0
        # Classification
        if ratio > 2.0:
            signal = "spike_high_attention"
        elif ratio > 1.3:
            signal = "above_avg"
        elif ratio < 0.7:
            signal = "below_avg"
        else:
            signal = "normal"
        return {
            "signal": signal,
            "views_recent_avg": recent_avg,
            "views_baseline_avg": baseline_avg,
            "ratio": ratio,
        }
    except Exception as exc:
        logger.debug("get_wikipedia_pageviews(%s): %s", ticker, exc)
        return {"signal": "no_data"}


def get_cot_report(as_of: date) -> dict:
    """
    COT (Commitment of Traders) positioning.
    Pass 53 Batch 13 sub-task 5 (RESOLVED-IMPLEMENTED 2026-05-06):
    Reads CFTC TFF E-mini S&P 500 weekly positioning from
    data_prefetch/cftc/cot_emini_sp500.parquet (Sprint 0A Batch 8 prefetched
    1,293 weekly reports 2006-06 to 2026-04).

    Commercial hedgers = smart money; speculators often wrong at extremes.
    Returns commercial net positioning + signal classification.
    """
    if not PREFETCH_CFTC_COT.exists():
        return {"signal": "not_available", "commercial_net": None}
    try:
        df = pd.read_parquet(PREFETCH_CFTC_COT)
        if df.empty or "report_date" not in df.columns:
            return {"signal": "not_available", "commercial_net": None}
        df["report_date"] = pd.to_datetime(df["report_date"]).dt.date
        df = df[df["report_date"] <= as_of]
        if df.empty:
            return {"signal": "not_available", "commercial_net": None}
        latest = df.iloc[-1]
        # CFTC TFF schema:
        # asset_mgr_positions_long, asset_mgr_positions_short
        # dealer_positions_long_all, dealer_positions_short_all (commercial)
        try:
            dealer_long = float(latest.get("dealer_positions_long_all", 0) or 0)
            dealer_short = float(latest.get("dealer_positions_short_all", 0) or 0)
            comm_net = dealer_long - dealer_short
            asset_mgr_long = float(latest.get("asset_mgr_positions_long", 0) or 0)
            asset_mgr_short = float(latest.get("asset_mgr_positions_short", 0) or 0)
            spec_net = asset_mgr_long - asset_mgr_short
        except Exception:
            return {"signal": "parse_error", "commercial_net": None}
        # 26-week (6mo) percentile of comm_net for extreme detection
        history = df.tail(26)
        try:
            comm_history = history.apply(
                lambda r: float(r.get("dealer_positions_long_all", 0) or 0)
                          - float(r.get("dealer_positions_short_all", 0) or 0),
                axis=1)
            pct = (comm_history < comm_net).sum() / max(len(comm_history), 1)
        except Exception:
            pct = 0.5
        if pct > 0.85:
            signal = "extreme_commercial_long_buy"  # contrarian buy
        elif pct < 0.15:
            signal = "extreme_commercial_short_sell"  # contrarian sell
        else:
            signal = "normal"
        return {
            "signal": signal,
            "commercial_net": comm_net,
            "speculator_net": spec_net,
            "report_date": str(latest["report_date"]),
            "history_percentile": pct,
        }
    except Exception as exc:
        logger.debug("get_cot_report(%s): %s", as_of, exc)
        return {"signal": "not_available", "commercial_net": None}


# ---------------------------------------------------------------------------
# COMBINED SENTIMENT SNAPSHOT
# ---------------------------------------------------------------------------

def sentiment_snapshot(as_of: date, ticker: Optional[str] = None) -> dict:
    """
    Return combined sentiment context dict for `as_of`.
    Used by the Sentiment Agent as its primary input.

    Pass 53 Batch 13 sub-tasks 4 + 5 expansion (DEC-507 Row 5 closure):
    Adds CNN F&G 7 sub-components, CFTC COT (real data), and ticker-specific
    Apewisdom + Wikipedia signals.

    `ticker` parameter optional — when provided, ticker-specific signals
    (Apewisdom mentions, Wikipedia pageviews) are included; when None, only
    market-wide sentiment signals are returned.

    Returns: aaii, fear_greed, fg_components, cot, apewisdom (if ticker),
    wikipedia (if ticker), sentiment_score (-5 to +5).
    """
    aaii = get_aaii_sentiment(as_of)
    fg = get_fear_and_greed(as_of)
    fg_components = get_cnn_components(as_of)
    cot = get_cot_report(as_of)

    score = 0

    # AAII scoring (contrarian)
    aaii_sig = aaii.get("signal", "neutral")
    if "extreme_fear" in aaii_sig:   score += 3
    elif "high_bearishness" in aaii_sig: score += 2
    elif "extreme_greed" in aaii_sig:  score -= 2
    elif "elevated_bullishness" in aaii_sig: score -= 1

    # Fear & Greed composite scoring (contrarian)
    fg_sig = fg.get("signal", "neutral")
    if fg_sig == "extreme_fear_buy":     score += 3
    elif fg_sig == "fear_lean_buy":       score += 1
    elif fg_sig == "extreme_greed_sell_warning": score -= 2
    elif fg_sig == "greed_caution":       score -= 1

    # CFTC COT scoring (Pass 53 Batch 13 sub-task 5)
    cot_sig = cot.get("signal", "not_available")
    if cot_sig == "extreme_commercial_long_buy":  score += 1
    elif cot_sig == "extreme_commercial_short_sell": score -= 1

    # Ticker-specific signals (when ticker provided)
    apewisdom = None
    wikipedia = None
    if ticker:
        apewisdom = get_apewisdom_mentions(ticker)
        wikipedia = get_wikipedia_pageviews(ticker, as_of)
        # Apewisdom rank (lower = more mentions)
        ape_sig = apewisdom.get("signal", "no_data")
        if ape_sig == "tracked" and apewisdom.get("rank", 999) <= 50:
            # Top-50 meme stock — signal mixed (could be retail buy or pump-and-dump)
            score += 0  # neutral; presence is information, direction is not
        # Wikipedia pageviews spike — high attention often precedes movement
        wiki_sig = wikipedia.get("signal", "no_data")
        if wiki_sig == "spike_high_attention":
            score += 0  # neutral; signal value depends on direction context

    return {
        "aaii":             aaii,
        "fear_greed":       fg,
        "fg_components":    fg_components,
        "cot":              cot,
        "apewisdom":        apewisdom,
        "wikipedia":        wikipedia,
        "sentiment_score":  max(-5, min(5, score)),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Pass 53 Day-9 v8c Wave D — L146 G8 pytrends search-attention accessor
# ─────────────────────────────────────────────────────────────────────────────
PREFETCH_PYTRENDS_DIR = _REPO_ROOT_SENT / "data_prefetch" / "pytrends"


def get_search_attention(ticker: str, as_of: date,
                          lookback_days: int = 30) -> dict:
    """Return Google Trends search-volume signal for `ticker` (PIT).

    Source: data_prefetch/pytrends/<TICKER>.parquet
    Schema: ticker / date / search_volume_index (0-100) / query_label

    Search Volume Index (SVI) is normalized 0-100 by Google Trends; spike
    in SVI is a retail-attention proxy (which can foreshadow vol/momentum
    in single-name names but is noisy).

    Returns dict with avg SVI in window + latest SVI + trend direction.
    """
    safe = ticker.replace(".", "-")
    path = PREFETCH_PYTRENDS_DIR / f"{safe}.parquet"
    default = {"avg_svi": None, "latest_svi": None,
               "trend": "unknown", "rows_in_window": 0,
               "as_of": str(as_of)}
    if not path.exists():
        return default
    try:
        df = pd.read_parquet(path)
        if df.empty or "date" not in df.columns:
            return default
        df["date"] = pd.to_datetime(df["date"])
        cutoff = pd.Timestamp(as_of)
        window_start = cutoff - pd.Timedelta(days=lookback_days)
        window = df[(df["date"] >= window_start) & (df["date"] <= cutoff)]
        if window.empty:
            return default
        avg_svi = float(window["search_volume_index"].mean())
        latest_svi = float(window["search_volume_index"].iloc[-1])
        # Crude trend: latest vs window avg
        if latest_svi > avg_svi * 1.2:
            trend = "rising"
        elif latest_svi < avg_svi * 0.8:
            trend = "falling"
        else:
            trend = "flat"
        return {
            "avg_svi":         avg_svi,
            "latest_svi":      latest_svi,
            "trend":           trend,
            "rows_in_window":  int(len(window)),
            "as_of":           str(as_of),
        }
    except Exception as exc:
        logger.debug("get_search_attention(%s): %s", ticker, exc)
        return default
