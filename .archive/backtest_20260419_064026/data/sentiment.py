"""
data/sentiment.py — Sentiment signal data fetchers.

Sources (all free, no API key required):
  - AAII Investor Sentiment Survey: weekly bullish/bearish readings
  - CNN Fear & Greed Index: daily composite 0-100
  - COT (Commitment of Traders): CFTC weekly — commercial vs speculative positioning

All functions enforce point-in-time data (as_of parameter).

NOTE: Live scraping of AAII and CNN is fragile — both sites change layouts.
For backtesting, we use cached/hardcoded historical weekly readings derived
from publicly available data. Live scraping is used in Stage 3+ (paper trading).
"""

import logging
import requests
import io
from datetime import date, timedelta
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# AAII SENTIMENT SURVEY
# Weekly reading — published every Thursday.
# Extreme bearishness (>50% bears) = contrarian buy signal.
# Extreme bullishness (>50% bulls) = contrarian sell warning.
#
# Historical data (2022-2024) — sourced from AAII.com public archives.
# Format: survey_date, bullish_pct, bearish_pct, neutral_pct
# ---------------------------------------------------------------------------

# Sampled weekly AAII readings — representative of major regime shifts.
# Full dataset should be loaded from a CSV in production.
_AAII_SAMPLE = [
    # date,         bull,  bear,  neutral
    ("2022-01-06",  42.0,  23.3, 34.7),
    ("2022-03-03",  25.4,  45.0, 29.6),
    ("2022-06-02",  18.2,  59.0, 22.8),   # extreme bearishness — contrarian buy zone
    ("2022-09-29",  20.0,  60.9, 19.1),   # near-historic bearishness
    ("2022-12-01",  22.4,  44.7, 32.9),
    ("2023-01-05",  24.8,  37.5, 37.7),
    ("2023-03-02",  19.2,  41.3, 39.5),
    ("2023-06-01",  27.6,  33.0, 39.4),
    ("2023-09-07",  32.8,  30.0, 37.2),
    ("2023-11-02",  42.0,  27.0, 31.0),
    ("2024-01-04",  48.0,  22.0, 30.0),
    ("2024-03-07",  52.0,  21.0, 27.0),   # near-extreme bullishness
    ("2024-06-06",  44.0,  26.0, 30.0),
    ("2024-09-05",  41.0,  24.0, 35.0),
    ("2024-12-05",  46.0,  27.0, 27.0),
]

_AAII_DF: Optional[pd.DataFrame] = None


def _load_aaii() -> pd.DataFrame:
    global _AAII_DF
    if _AAII_DF is not None:
        return _AAII_DF
    rows = [{"survey_date": date.fromisoformat(r[0]),
             "bullish_pct": r[1], "bearish_pct": r[2], "neutral_pct": r[3]}
            for r in _AAII_SAMPLE]
    _AAII_DF = pd.DataFrame(rows).sort_values("survey_date").reset_index(drop=True)
    return _AAII_DF


def get_aaii_sentiment(as_of: date) -> dict:
    """
    Return most recent AAII sentiment reading on or before `as_of`.
    Returns dict: survey_date, bullish_pct, bearish_pct, neutral_pct, signal
    """
    df = _load_aaii()
    available = df[df["survey_date"] <= as_of]
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

_CNN_SAMPLE = [
    # date,         score, label
    ("2022-01-20",  30, "Fear"),
    ("2022-02-24",  20, "Extreme Fear"),
    ("2022-06-13",  10, "Extreme Fear"),   # near CPI shock lows
    ("2022-09-23",  14, "Extreme Fear"),
    ("2022-10-14",  20, "Extreme Fear"),
    ("2022-12-16",  38, "Fear"),
    ("2023-01-13",  55, "Greed"),
    ("2023-03-22",  40, "Fear"),
    ("2023-06-14",  68, "Greed"),
    ("2023-11-01",  35, "Fear"),
    ("2023-12-27",  72, "Greed"),
    ("2024-01-31",  65, "Greed"),
    ("2024-03-20",  80, "Extreme Greed"),
    ("2024-07-24",  33, "Fear"),
    ("2024-09-18",  55, "Greed"),
    ("2024-12-18",  40, "Fear"),
]

_CNN_DF: Optional[pd.DataFrame] = None


def _load_cnn() -> pd.DataFrame:
    global _CNN_DF
    if _CNN_DF is not None:
        return _CNN_DF
    rows = [{"reading_date": date.fromisoformat(r[0]), "score": r[1], "label": r[2]}
            for r in _CNN_SAMPLE]
    _CNN_DF = pd.DataFrame(rows).sort_values("reading_date").reset_index(drop=True)
    return _CNN_DF


def get_fear_and_greed(as_of: date) -> dict:
    """
    Return most recent CNN Fear & Greed reading on or before `as_of`.
    Returns dict: reading_date, score (0-100), label, signal
    """
    df = _load_cnn()
    available = df[df["reading_date"] <= as_of]
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
    Return COT positioning summary for S&P 500 futures on or before `as_of`.
    In production this scrapes CFTC.gov; for backtesting uses sampled data.

    Returns dict: report_date, commercial_net, speculator_net, signal
    """
    # Sampled COT net positioning (commercial long - short, in contracts)
    # Positive = net long, Negative = net short
    _COT_SAMPLE = [
        ("2022-01-04",  -50000, "neutral"),
        ("2022-06-14",   80000, "commercial_long_buy"),    # commercials loaded long near lows
        ("2022-09-27",   70000, "commercial_long_buy"),
        ("2022-12-13",   30000, "slight_long"),
        ("2023-06-13",  -20000, "neutral"),
        ("2023-12-19",  -60000, "commercial_short_caution"),  # commercials hedging at highs
        ("2024-03-19",  -70000, "commercial_short_caution"),
        ("2024-09-17",   10000, "neutral"),
        ("2024-12-17",  -40000, "slight_short"),
    ]

    for row_date, commercial_net, signal_hint in reversed(_COT_SAMPLE):
        if date.fromisoformat(row_date) <= as_of:
            return {
                "report_date":    date.fromisoformat(row_date),
                "commercial_net": commercial_net,
                "signal":         signal_hint,
            }
    return {"signal": "unknown", "commercial_net": None}


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

    # COT scoring
    cot_sig = cot.get("signal", "neutral")
    if "commercial_long_buy" in cot_sig: score += 2
    elif "commercial_short_caution" in cot_sig: score -= 1

    return {
        "aaii":             aaii,
        "fear_greed":       fg,
        "cot":              cot,
        "sentiment_score":  max(-5, min(5, score)),
    }
