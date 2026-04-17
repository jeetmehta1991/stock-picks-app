"""
data/macro.py — Macro and economic filter data.

Sources:
  - FRED API: yield curve (T10Y2Y), fed funds rate (FEDFUNDS)
  - yfinance: VIX (^VIX), DXY (DX-Y.NYB)
  - Hardcoded FOMC/CPI/NFP dates (free, from public calendars)

All functions enforce point-in-time data (as_of parameter).
FRED_API_KEY env var required for FRED. Falls back to CSV download if absent.
"""

import os
import logging
import io
from datetime import date, timedelta
from typing import Optional

import requests
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

FRED_KEY  = os.environ.get("FRED_API_KEY", "")
FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

# ---------------------------------------------------------------------------
# FRED HELPERS
# ---------------------------------------------------------------------------

def _fred_series(series_id: str, start: date, end: date) -> pd.Series:
    """
    Fetch a FRED time series. Uses API key if available; falls back to
    FRED's public CSV endpoint (no key needed).
    """
    if FRED_KEY:
        try:
            resp = requests.get(
                FRED_BASE,
                params={
                    "series_id":         series_id,
                    "observation_start": start.isoformat(),
                    "observation_end":   end.isoformat(),
                    "api_key":           FRED_KEY,
                    "file_type":         "json",
                },
                timeout=20,
            )
            resp.raise_for_status()
            obs = resp.json().get("observations", [])
            s = pd.Series(
                {o["date"]: float(o["value"]) for o in obs if o["value"] != "."},
                name=series_id,
            )
            s.index = pd.to_datetime(s.index)
            return s
        except Exception as exc:
            logger.warning("FRED API error for %s: %s — trying CSV fallback", series_id, exc)

    # CSV fallback (no API key required)
    try:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text), parse_dates=["DATE"])
        df = df[df["DATE"] >= pd.Timestamp(start)]
        df = df[df["DATE"] <= pd.Timestamp(end)]
        df = df[df[series_id] != "."]
        s = pd.to_numeric(df[series_id], errors="coerce").dropna()
        s.index = df["DATE"]
        return s
    except Exception as exc:
        logger.error("FRED CSV fallback failed for %s: %s", series_id, exc)
        return pd.Series(dtype=float)


# ---------------------------------------------------------------------------
# YIELD CURVE
# ---------------------------------------------------------------------------

def get_yield_curve(
    start: date,
    end: date,
    as_of: Optional[date] = None,
) -> pd.DataFrame:
    """
    Return daily 10Y-2Y Treasury spread (T10Y2Y) from FRED.
    Negative = inverted yield curve = risk-off / recession signal.

    as_of ceiling enforced: only rows on/before as_of returned.
    """
    effective_end = min(end, as_of) if as_of else end
    raw = _fred_series("T10Y2Y", start, effective_end)
    if raw.empty:
        return pd.DataFrame()
    df = raw.rename("spread_10y_2y").to_frame()
    df["inverted"] = df["spread_10y_2y"] < 0
    return df


def yield_curve_regime(as_of: date, lookback_days: int = 30) -> str:
    """
    Return yield curve regime at as_of:
      'inverted'  — spread consistently negative (risk-off)
      'flat'      — spread between -0.1 and +0.5
      'normal'    — spread > 0.5 (healthy risk-on)
      'unknown'   — data unavailable
    """
    start = as_of - timedelta(days=lookback_days + 5)
    df = get_yield_curve(start, as_of, as_of=as_of)
    if df.empty:
        return "unknown"
    recent = df.tail(lookback_days)
    avg_spread = recent["spread_10y_2y"].mean()
    if avg_spread < -0.1:
        return "inverted"
    if avg_spread < 0.5:
        return "flat"
    return "normal"


# ---------------------------------------------------------------------------
# VIX REGIME
# ---------------------------------------------------------------------------

def get_vix(
    start: date,
    end: date,
    as_of: Optional[date] = None,
) -> pd.DataFrame:
    """
    Return daily VIX close via yfinance.
    as_of ceiling enforced.
    """
    effective_end = min(end, as_of) if as_of else end
    try:
        df = yf.download(
            "^VIX",
            start=start.isoformat(),
            end=(effective_end + timedelta(days=1)).isoformat(),
            auto_adjust=True,
            progress=False,
        )
        if df.empty:
            return pd.DataFrame()
        # Handle MultiIndex columns from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index).tz_localize(None)
        result = df[["Close"]].rename(columns={"Close": "vix"})
        return result[result.index.date <= effective_end]  # type: ignore[attr-defined]
    except Exception as exc:
        logger.error("get_vix: %s", exc)
        return pd.DataFrame()


def vix_regime(as_of: date, lookback_days: int = 5) -> str:
    """
    Classify VIX regime at as_of.
    Returns: 'low' (<15), 'normal' (15-25), 'elevated' (25-35), 'crisis' (>35)
    """
    start = as_of - timedelta(days=lookback_days + 10)
    df = get_vix(start, as_of, as_of=as_of)
    if df.empty:
        return "unknown"
    current_vix = df["vix"].iloc[-1]
    if current_vix < 15:
        return "low"
    if current_vix < 25:
        return "normal"
    if current_vix < 35:
        return "elevated"
    return "crisis"


# ---------------------------------------------------------------------------
# DXY — US Dollar Index
# ---------------------------------------------------------------------------

def get_dxy(
    start: date,
    end: date,
    as_of: Optional[date] = None,
) -> pd.DataFrame:
    """
    Return daily DXY (US Dollar Index) close. Affects multinational and commodity stocks.
    as_of ceiling enforced.
    """
    effective_end = min(end, as_of) if as_of else end
    try:
        df = yf.download(
            "DX-Y.NYB",
            start=start.isoformat(),
            end=(effective_end + timedelta(days=1)).isoformat(),
            auto_adjust=True,
            progress=False,
        )
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index).tz_localize(None)
        result = df[["Close"]].rename(columns={"Close": "dxy"})
        return result[result.index.date <= effective_end]  # type: ignore[attr-defined]
    except Exception as exc:
        logger.error("get_dxy: %s", exc)
        return pd.DataFrame()


def dxy_trend(as_of: date, lookback_days: int = 20) -> str:
    """Return 'rising', 'falling', or 'flat' based on 20-day DXY trend."""
    start = as_of - timedelta(days=lookback_days + 10)
    df = get_dxy(start, as_of, as_of=as_of)
    if len(df) < 10:
        return "unknown"
    first = df["dxy"].iloc[0]
    last  = df["dxy"].iloc[-1]
    pct_change = (last - first) / first * 100
    if pct_change > 1.5:
        return "rising"
    if pct_change < -1.5:
        return "falling"
    return "flat"


# ---------------------------------------------------------------------------
# ECONOMIC CALENDAR — HIGH IMPACT EVENTS
# Strategy: avoid new swing entries in ±2 trading days around CPI, NFP, FOMC.
# Dates are hardcoded from public FOMC/BLS/CPI calendars — accurate to 2025.
# ---------------------------------------------------------------------------

# CPI release dates (Bureau of Labor Statistics)
CPI_DATES = [
    # 2022
    date(2022, 1, 12), date(2022, 2, 10), date(2022, 3, 10), date(2022, 4, 12),
    date(2022, 5, 11), date(2022, 6, 10), date(2022, 7, 13), date(2022, 8, 10),
    date(2022, 9, 13), date(2022, 10, 13), date(2022, 11, 10), date(2022, 12, 13),
    # 2023
    date(2023, 1, 12), date(2023, 2, 14), date(2023, 3, 14), date(2023, 4, 12),
    date(2023, 5, 10), date(2023, 6, 13), date(2023, 7, 12), date(2023, 8, 10),
    date(2023, 9, 13), date(2023, 10, 12), date(2023, 11, 14), date(2023, 12, 12),
    # 2024
    date(2024, 1, 11), date(2024, 2, 13), date(2024, 3, 12), date(2024, 4, 10),
    date(2024, 5, 15), date(2024, 6, 12), date(2024, 7, 11), date(2024, 8, 14),
    date(2024, 9, 11), date(2024, 10, 10), date(2024, 11, 13), date(2024, 12, 11),
]

# Non-Farm Payroll release dates (Bureau of Labor Statistics — first Friday of month)
NFP_DATES = [
    # 2022
    date(2022, 1, 7), date(2022, 2, 4), date(2022, 3, 4), date(2022, 4, 1),
    date(2022, 5, 6), date(2022, 6, 3), date(2022, 7, 8), date(2022, 8, 5),
    date(2022, 9, 2), date(2022, 10, 7), date(2022, 11, 4), date(2022, 12, 2),
    # 2023
    date(2023, 1, 6), date(2023, 2, 3), date(2023, 3, 10), date(2023, 4, 7),
    date(2023, 5, 5), date(2023, 6, 2), date(2023, 7, 7), date(2023, 8, 4),
    date(2023, 9, 1), date(2023, 10, 6), date(2023, 11, 3), date(2023, 12, 8),
    # 2024
    date(2024, 1, 5), date(2024, 2, 2), date(2024, 3, 8), date(2024, 4, 5),
    date(2024, 5, 3), date(2024, 6, 7), date(2024, 7, 5), date(2024, 8, 2),
    date(2024, 9, 6), date(2024, 10, 4), date(2024, 11, 1), date(2024, 12, 6),
]

# FOMC meeting decision dates
FOMC_DATES = [
    # 2022
    date(2022, 1, 26), date(2022, 3, 16), date(2022, 5, 4), date(2022, 6, 15),
    date(2022, 7, 27), date(2022, 9, 21), date(2022, 11, 2), date(2022, 12, 14),
    # 2023
    date(2023, 2, 1), date(2023, 3, 22), date(2023, 5, 3), date(2023, 6, 14),
    date(2023, 7, 26), date(2023, 9, 20), date(2023, 11, 1), date(2023, 12, 13),
    # 2024
    date(2024, 1, 31), date(2024, 3, 20), date(2024, 5, 1), date(2024, 6, 12),
    date(2024, 7, 31), date(2024, 9, 18), date(2024, 11, 7), date(2024, 12, 18),
]

ALL_HIGH_IMPACT = sorted(set(CPI_DATES + NFP_DATES + FOMC_DATES))


def is_near_high_impact_event(as_of: date, window_days: int = 2) -> dict:
    """
    Return whether `as_of` is within `window_days` of a CPI, NFP, or FOMC event.
    Per project plan: avoid new swing entries within ±2 trading days.

    Returns dict: blocked (bool), nearest_event_type, nearest_event_date, days_away
    """
    window_start = as_of - timedelta(days=window_days)
    window_end   = as_of + timedelta(days=window_days)

    blocked_events = []
    for event_date in ALL_HIGH_IMPACT:
        if window_start <= event_date <= window_end:
            event_type = (
                "CPI"  if event_date in CPI_DATES  else
                "NFP"  if event_date in NFP_DATES  else
                "FOMC"
            )
            days_away = (event_date - as_of).days
            blocked_events.append({
                "event_type": event_type,
                "event_date": event_date,
                "days_away":  days_away,
            })

    if not blocked_events:
        return {"blocked": False, "nearest_event_type": None,
                "nearest_event_date": None, "days_away": None}

    nearest = min(blocked_events, key=lambda x: abs(x["days_away"]))
    return {
        "blocked":             True,
        "nearest_event_type":  nearest["event_type"],
        "nearest_event_date":  nearest["event_date"],
        "days_away":           nearest["days_away"],
    }


# ---------------------------------------------------------------------------
# COMPLETE MACRO SNAPSHOT
# ---------------------------------------------------------------------------

def macro_snapshot(as_of: date) -> dict:
    """
    Return a complete macro context dict for `as_of`.
    Used by the Risk Agent as its primary input.

    Returns: yield_curve_regime, vix_regime, vix_value, dxy_trend,
             near_high_impact_event, event_type, macro_score
    """
    from backtest.config import BACKTEST_START

    yc_regime   = yield_curve_regime(as_of)
    vix_reg     = vix_regime(as_of)
    dxy_tr      = dxy_trend(as_of)
    econ_check  = is_near_high_impact_event(as_of)

    # Fetch current VIX value
    vix_df = get_vix(as_of - timedelta(days=5), as_of, as_of=as_of)
    vix_val = float(vix_df["vix"].iloc[-1]) if not vix_df.empty else None

    # Macro favourability score (-5 to +5)
    score = 0
    if yc_regime == "normal":  score += 2
    elif yc_regime == "flat":   score += 0
    elif yc_regime == "inverted": score -= 2

    if vix_reg == "low":       score += 2
    elif vix_reg == "normal":   score += 1
    elif vix_reg == "elevated": score -= 1
    elif vix_reg == "crisis":   score -= 3

    if dxy_tr == "falling": score += 1   # falling dollar = risk-on for US stocks
    elif dxy_tr == "rising": score -= 1

    if econ_check["blocked"]: score -= 2  # avoid entries near major events

    return {
        "yield_curve_regime":    yc_regime,
        "vix_regime":            vix_reg,
        "vix_value":             vix_val,
        "dxy_trend":             dxy_tr,
        "near_high_impact_event": econ_check["blocked"],
        "event_type":            econ_check.get("nearest_event_type"),
        "event_days_away":       econ_check.get("days_away"),
        "macro_score":           score,
    }
