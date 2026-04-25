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
    global _AAII_DF
    if _AAII_DF is not None:
        return _AAII_DF
    csv_path = DATA_DIR / "aaii_sentiment.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path, parse_dates=["date"])
        df = df.rename(columns={"date": "survey_date", "bullish": "bullish_pct",
                                 "bearish": "bearish_pct", "neutral": "neutral_pct"})
        _AAII_DF = df.sort_values("survey_date").reset_index(drop=True)
        logger.info("AAII: loaded %d weekly readings from CSV", len(_AAII_DF))
    else:
        logger.warning("AAII CSV not found — using empty dataset")
        _AAII_DF = pd.DataFrame(columns=["survey_date","bullish_pct","bearish_pct","neutral_pct"])
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
    global _CNN_DF
    if _CNN_DF is not None:
        return _CNN_DF
    csv_path = DATA_DIR / "cnn_fear_greed.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path, parse_dates=["date"])
        df = df.rename(columns={"date": "reading_date"})
        _CNN_DF = df.sort_values("reading_date").reset_index(drop=True)
        logger.info("CNN F&G: loaded %d daily readings from CSV", len(_CNN_DF))
    else:
        logger.warning("CNN F&G CSV not found — using empty dataset")
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

def get_cot_report(as_of: date) -> dict:
    """
    COT (Commitment of Traders) positioning.
    REMOVED: previous implementation used 9 fabricated hardcoded sample points.
    Real CFTC COT data: https://www.cftc.gov/MarketReports/CommitmentsofTraders/
    Phase 1C+: integrate real CFTC COT via their free weekly data files.
    Returns neutral — does not influence sentiment score.
    """
    return {"signal": "not_available", "commercial_net": None}


# ---------------------------------------------------------------------------
# COMBINED SENTIMENT SNAPSHOT
# ---------------------------------------------------------------------------

def sentiment_snapshot(as_of: date) -> dict:
    """
    Return combined sentiment context dict for `as_of`.
    Used by the Sentiment Agent as its primary input.

    Returns: aaii, fear_greed, cot, sentiment_score (-5 to +5)
    """
    aaii       = get_aaii_sentiment(as_of)
    fg         = get_fear_and_greed(as_of)
    cot        = get_cot_report(as_of)

    score = 0

    # AAII scoring (contrarian)
    aaii_sig = aaii.get("signal", "neutral")
    if "extreme_fear" in aaii_sig:   score += 3
    elif "high_bearishness" in aaii_sig: score += 2
    elif "extreme_greed" in aaii_sig:  score -= 2
    elif "elevated_bullishness" in aaii_sig: score -= 1

    # Fear & Greed scoring (contrarian)
    fg_sig = fg.get("signal", "neutral")
    if fg_sig == "extreme_fear_buy":     score += 3
    elif fg_sig == "fear_lean_buy":       score += 1
    elif fg_sig == "extreme_greed_sell_warning": score -= 2
    elif fg_sig == "greed_caution":       score -= 1

    # COT — not available (removed fabricated data)
    # Will be re-enabled in Phase 1C with real CFTC data

    return {
        "aaii":             aaii,
        "fear_greed":       fg,
        "cot":              cot,
        "sentiment_score":  max(-5, min(5, score)),
    }
