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

def _fred_series(series_id: str, start: date, end: date) -> pd.Series:
    if FRED_KEY:
        try:
            resp = requests.get(
                FRED_BASE,
                params={"series_id": series_id, "observation_start": start.isoformat(),
                        "observation_end": end.isoformat(), "api_key": FRED_KEY,
                        "file_type": "json"},
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

    # CSV fallback — reads column names dynamically, does not assume 'DATE'
    try:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        raw = pd.read_csv(io.StringIO(resp.text))
        if len(raw.columns) < 2:
            logger.error("FRED CSV for %s has unexpected format", series_id)
            return pd.Series(dtype=float)
        date_col  = raw.columns[0]
        value_col = raw.columns[1]
        raw[date_col] = pd.to_datetime(raw[date_col], errors="coerce")
        raw = raw.dropna(subset=[date_col])
        raw = raw[raw[date_col] >= pd.Timestamp(start)]
        raw = raw[raw[date_col] <= pd.Timestamp(end)]
        raw = raw[raw[value_col].astype(str) != "."]
        s = pd.to_numeric(raw[value_col], errors="coerce").dropna()
        s.index = pd.to_datetime(raw[date_col].values[:len(s)])
        return s
    except Exception as exc:
        logger.error("FRED CSV fallback failed for %s: %s", series_id, exc)
        return pd.Series(dtype=float)


def get_yield_curve(start: date, end: date, as_of: Optional[date] = None) -> pd.DataFrame:
    effective_end = min(end, as_of) if as_of else end
    raw = _fred_series("T10Y2Y", start, effective_end)
    if raw.empty:
        return pd.DataFrame()
    df = raw.rename("spread_10y_2y").to_frame()
    df["inverted"] = df["spread_10y_2y"] < 0
    return df


def yield_curve_regime(as_of: date, lookback_days: int = 30) -> str:
    start = as_of - timedelta(days=lookback_days + 5)
    df = get_yield_curve(start, as_of, as_of=as_of)
    if df.empty:
        return "unknown"
    avg = df["spread_10y_2y"].mean()
    if avg < -0.1:   return "inverted"
    if avg < 0.5:    return "flat"
    return "normal"


def get_vix(start: date, end: date, as_of: Optional[date] = None) -> pd.DataFrame:
    effective_end = min(end, as_of) if as_of else end
    try:
        df = yf.download("^VIX", start=start.isoformat(),
                         end=(effective_end + timedelta(days=1)).isoformat(),
                         auto_adjust=True, progress=False)
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index).tz_localize(None)
        result = df[["Close"]].rename(columns={"Close": "vix"})
        return result[result.index.date <= effective_end]
    except Exception as exc:
        logger.error("get_vix: %s", exc)
        return pd.DataFrame()


def vix_regime(as_of: date, lookback_days: int = 5) -> str:
    start = as_of - timedelta(days=lookback_days + 10)
    df = get_vix(start, as_of, as_of=as_of)
    if df.empty:
        return "unknown"
    v = float(df["vix"].iloc[-1])
    if v < 15:   return "low"
    if v < 25:   return "normal"
    if v < 35:   return "elevated"
    return "crisis"


def get_dxy(start: date, end: date, as_of: Optional[date] = None) -> pd.DataFrame:
    effective_end = min(end, as_of) if as_of else end
    try:
        df = yf.download("DX-Y.NYB", start=start.isoformat(),
                         end=(effective_end + timedelta(days=1)).isoformat(),
                         auto_adjust=True, progress=False)
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index).tz_localize(None)
        result = df[["Close"]].rename(columns={"Close": "dxy"})
        return result[result.index.date <= effective_end]
    except Exception as exc:
        logger.error("get_dxy: %s", exc)
        return pd.DataFrame()


def dxy_trend(as_of: date, lookback_days: int = 20) -> str:
    start = as_of - timedelta(days=lookback_days + 10)
    df = get_dxy(start, as_of, as_of=as_of)
    if len(df) < 10:
        return "unknown"
    pct = (float(df["dxy"].iloc[-1]) - float(df["dxy"].iloc[0])) / float(df["dxy"].iloc[0]) * 100
    if pct > 1.5:    return "rising"
    if pct < -1.5:   return "falling"
    return "flat"


# Economic calendar — CPI, NFP, FOMC dates 2022-2024
CPI_DATES = [
    date(2022,1,12),date(2022,2,10),date(2022,3,10),date(2022,4,12),
    date(2022,5,11),date(2022,6,10),date(2022,7,13),date(2022,8,10),
    date(2022,9,13),date(2022,10,13),date(2022,11,10),date(2022,12,13),
    date(2023,1,12),date(2023,2,14),date(2023,3,14),date(2023,4,12),
    date(2023,5,10),date(2023,6,13),date(2023,7,12),date(2023,8,10),
    date(2023,9,13),date(2023,10,12),date(2023,11,14),date(2023,12,12),
    date(2024,1,11),date(2024,2,13),date(2024,3,12),date(2024,4,10),
    date(2024,5,15),date(2024,6,12),date(2024,7,11),date(2024,8,14),
    date(2024,9,11),date(2024,10,10),date(2024,11,13),date(2024,12,11),
]
NFP_DATES = [
    date(2022,1,7),date(2022,2,4),date(2022,3,4),date(2022,4,1),
    date(2022,5,6),date(2022,6,3),date(2022,7,8),date(2022,8,5),
    date(2022,9,2),date(2022,10,7),date(2022,11,4),date(2022,12,2),
    date(2023,1,6),date(2023,2,3),date(2023,3,10),date(2023,4,7),
    date(2023,5,5),date(2023,6,2),date(2023,7,7),date(2023,8,4),
    date(2023,9,1),date(2023,10,6),date(2023,11,3),date(2023,12,8),
    date(2024,1,5),date(2024,2,2),date(2024,3,8),date(2024,4,5),
    date(2024,5,3),date(2024,6,7),date(2024,7,5),date(2024,8,2),
    date(2024,9,6),date(2024,10,4),date(2024,11,1),date(2024,12,6),
]
FOMC_DATES = [
    date(2022,1,26),date(2022,3,16),date(2022,5,4),date(2022,6,15),
    date(2022,7,27),date(2022,9,21),date(2022,11,2),date(2022,12,14),
    date(2023,2,1),date(2023,3,22),date(2023,5,3),date(2023,6,14),
    date(2023,7,26),date(2023,9,20),date(2023,11,1),date(2023,12,13),
    date(2024,1,31),date(2024,3,20),date(2024,5,1),date(2024,6,12),
    date(2024,7,31),date(2024,9,18),date(2024,11,7),date(2024,12,18),
]
ALL_HIGH_IMPACT = sorted(set(CPI_DATES + NFP_DATES + FOMC_DATES))


def is_near_high_impact_event(as_of: date, window_days: int = 2) -> dict:
    ws = as_of - timedelta(days=window_days)
    we = as_of + timedelta(days=window_days)
    blocked = []
    for ed in ALL_HIGH_IMPACT:
        if ws <= ed <= we:
            et = "CPI" if ed in CPI_DATES else "NFP" if ed in NFP_DATES else "FOMC"
            blocked.append({"event_type": et, "event_date": ed,
                            "days_away": (ed - as_of).days})
    if not blocked:
        return {"blocked": False, "nearest_event_type": None,
                "nearest_event_date": None, "days_away": None}
    nearest = min(blocked, key=lambda x: abs(x["days_away"]))
    return {"blocked": True, "nearest_event_type": nearest["event_type"],
            "nearest_event_date": nearest["event_date"],
            "days_away": nearest["days_away"]}


def macro_snapshot(as_of: date) -> dict:
    from backtest.config import BACKTEST_START
    yc  = yield_curve_regime(as_of)
    vr  = vix_regime(as_of)
    dxy = dxy_trend(as_of)
    ec  = is_near_high_impact_event(as_of)
    vix_df = get_vix(as_of - timedelta(days=5), as_of, as_of=as_of)
    vix_val = float(vix_df["vix"].iloc[-1]) if not vix_df.empty else None
    score = 0
    if yc == "normal":    score += 2
    elif yc == "inverted": score -= 2
    if vr == "low":       score += 2
    elif vr == "normal":   score += 1
    elif vr == "elevated": score -= 1
    elif vr == "crisis":   score -= 3
    if dxy == "falling":  score += 1
    elif dxy == "rising":  score -= 1
    if ec["blocked"]:     score -= 2
    return {
        "yield_curve_regime":     yc,
        "vix_regime":             vr,
        "vix_value":              vix_val,
        "dxy_trend":              dxy,
        "near_high_impact_event": ec["blocked"],
        "event_type":             ec.get("nearest_event_type"),
        "event_days_away":        ec.get("days_away"),
        "macro_score":            score,
    }
