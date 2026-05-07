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
from pathlib import Path
from typing import Optional

import requests
import pandas as pd
# yfinance removed from runtime per DEC-497 D4 (Pass 53 Batch 13 sub-task 6 2026-05-06).
# VIX + DXY now read exclusively from cache/ohlcv/ (Polygon-prefetched).

logger = logging.getLogger(__name__)

FRED_KEY  = os.environ.get("FRED_API_KEY", "")
FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
# DEC-301 fix (Pass 50): ALFRED archival endpoint for vintage (PIT-correct) data.
# Without this, FRED returns latest revised values, leaking future revisions into past dates.
ALFRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
MACRO_CACHE = Path(__file__).parent / "cache" / "macro"

SERIES_MAP = {
    "T10Y2Y":   "yield_curve",
    "FEDFUNDS": "fed_funds",
    "UNRATE":   "unemployment",
    "CPIAUCSL": "cpi",
    "T10YIE":   "inflation_exp",
    "DGS10":    "treasury_10y",
    "BAA10Y":   "corp_spread",
}

_MACRO_COMBINED: Optional[pd.DataFrame] = None


def _load_macro_combined() -> Optional[pd.DataFrame]:
    """Load pre-fetched combined macro Parquet — fastest path."""
    global _MACRO_COMBINED
    if _MACRO_COMBINED is not None:
        return _MACRO_COMBINED
    path = MACRO_CACHE / "macro_combined.parquet"
    if path.exists():
        _MACRO_COMBINED = pd.read_parquet(path)
        _MACRO_COMBINED["date"] = pd.to_datetime(_MACRO_COMBINED["date"])
        logger.info("Macro: loaded pre-fetched combined cache (%d rows)", len(_MACRO_COMBINED))
    return _MACRO_COMBINED


def _fred_series(series_id: str, start: date, end: date,
                  as_of: Optional[date] = None) -> pd.Series:
    """
    Fetch FRED time series with optional vintage-aware (ALFRED) query.

    DEC-301 fix (Pass 50): when `as_of` is provided, calls FRED with
    `realtime_end=as_of` so the returned series contains the data values
    that were KNOWN on as_of, not the latest revised values. Eliminates
    revision look-ahead bias for backtest macro features (UNRATE/CPI/GDP
    are routinely revised 6+ months after first publication).

    Without as_of: returns latest revised values (legacy behavior, only
    safe for forward-looking analysis or non-revised series).
    """
    # Try pre-fetched Parquet cache first (which uses latest revisions —
    # correct for FORWARD analysis but NOT PIT-correct for backtest).
    # Cache is bypassed when as_of provided to ensure vintage path.
    name = SERIES_MAP.get(series_id)
    if name and as_of is None:
        combined = _load_macro_combined()
        if combined is not None and name in combined.columns:
            mask = (combined["date"] >= pd.Timestamp(start)) & \
                   (combined["date"] <= pd.Timestamp(end))
            s = combined.loc[mask, ["date", name]].set_index("date")[name]
            s.name = series_id
            return s

    if FRED_KEY:
        try:
            params = {
                "series_id": series_id,
                "observation_start": start.isoformat(),
                "observation_end": end.isoformat(),
                "api_key": FRED_KEY,
                "file_type": "json",
            }
            # DEC-301: when as_of provided, use ALFRED vintage parameters
            if as_of is not None:
                params["realtime_end"] = as_of.isoformat()
                # realtime_start defaults to series start; realtime_end caps the
                # vintage so we get values KNOWN on as_of.
                logger.debug("FRED %s: fetching vintage values as of %s", series_id, as_of)
            resp = requests.get(ALFRED_BASE, params=params, timeout=20)
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
    # DEC-301 fix (Pass 50): pass as_of to _fred_series for vintage values
    raw = _fred_series("T10Y2Y", start, effective_end, as_of=as_of)
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


# VIX and DXY pre-loaded at module level from OHLCV cache — avoids live calls during backtest
_VIX_CACHE: Optional[pd.DataFrame] = None
_DXY_CACHE: Optional[pd.DataFrame] = None
# DEC-302 fix (Pass 50): track which symbol is being used so downstream can warn
# Pass 53 Day-9 v8 BUG-VIX-PROXY: 'FRED:VIXCLS' is the new canonical priority
_VIX_SOURCE: Optional[str] = None  # 'FRED:VIXCLS' (canonical) | '^VIX' | 'VXX' (proxy — degraded)
_DXY_SOURCE: Optional[str] = None  # 'DX-Y.NYB' (canonical) or 'UUP' (proxy)


def _load_vix_from_fred() -> Optional[pd.DataFrame]:
    """Load VIX from FRED VIXCLS prefetch (Pass 53 Day-9 v8 BUG-VIX-PROXY fix).

    Prefers ``data_prefetch/fred/observations/VIXCLS.parquet`` (Sprint 0A canonical
    L146 wiring path) over ``backtest/data/cache/macro/vix.parquet`` (legacy path).
    Returns DataFrame with DatetimeIndex + 'vix' column or None on miss.
    """
    from pathlib import Path
    candidates = [
        Path("data_prefetch/fred/observations/VIXCLS.parquet"),
        Path("backtest/data/cache/macro/vix.parquet"),
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            df = pd.read_parquet(path)
            if "date" not in df.columns or "value" not in df.columns:
                continue
            df = df.rename(columns={"value": "vix"})
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date").sort_index()
            return df[["vix"]]
        except Exception as exc:
            logger.warning("FRED VIX load failed at %s: %s", path, exc)
            continue
    return None


def _load_vix_from_ohlcv_cache() -> Optional[pd.DataFrame]:
    """
    Load VIX from pre-fetched OHLCV Parquet cache. No live calls.

    DEC-302 fix (Pass 50): prefers actual ^VIX (volatility index, the canonical
    source) over VXX (futures-tracking ETF with severe contango decay — diverges
    from VIX after ~1 day). VXX is kept as fallback so existing caches still
    work, but emits a WARNING when used so users know regime classification
    quality is degraded. Run scripts/prefetch_macro.py in Codespaces to
    populate ^VIX into cache.
    """
    global _VIX_CACHE, _VIX_SOURCE
    if _VIX_CACHE is not None:
        return _VIX_CACHE
    from backtest.data.cache import get_ohlcv_bulk as cached_ohlcv_bulk
    from datetime import date as _date
    # Try canonical source FIRST (note ordering reversal vs old code)
    candidates = [("^VIX", False), ("VXX", True)]
    for symbol, is_proxy in candidates:
        result = cached_ohlcv_bulk([symbol], start=_date(2020,1,1), end=_date(2026,12,31))
        if symbol in result and not result[symbol].empty:
            df = result[symbol][["close"]].rename(columns={"close": "vix"})
            _VIX_CACHE = df
            _VIX_SOURCE = symbol
            if is_proxy:
                logger.warning(
                    "VIX loader using PROXY %s — material tracking error vs ^VIX "
                    "(VXX has contango decay, diverges from VIX after ~1 day). "
                    "Run scripts/prefetch_macro.py in Codespaces to populate ^VIX. "
                    "Regime classification may be degraded.",
                    symbol,
                )
            else:
                logger.info("VIX loaded from canonical ^VIX: %d rows", len(df))
            return _VIX_CACHE
    return None


def _load_dxy_from_ohlcv_cache() -> Optional[pd.DataFrame]:
    """
    Load DXY from pre-fetched OHLCV Parquet cache.

    DEC-302 fix (Pass 50): prefers actual DX-Y.NYB (US Dollar Index) over
    UUP (ETF proxy with different basket weighting). UUP retained as
    fallback with WARNING. Run scripts/prefetch_macro.py in Codespaces.
    """
    global _DXY_CACHE, _DXY_SOURCE
    if _DXY_CACHE is not None:
        return _DXY_CACHE
    from backtest.data.cache import get_ohlcv_bulk as cached_ohlcv_bulk
    from datetime import date as _date
    candidates = [("DX-Y.NYB", False), ("UUP", True)]
    for symbol, is_proxy in candidates:
        result = cached_ohlcv_bulk([symbol], start=_date(2020,1,1), end=_date(2026,12,31))
        if symbol in result and not result[symbol].empty:
            df = result[symbol][["close"]].rename(columns={"close": "dxy"})
            _DXY_CACHE = df
            _DXY_SOURCE = symbol
            if is_proxy:
                logger.warning(
                    "DXY loader using PROXY %s — different basket weighting than DX-Y.NYB. "
                    "Run scripts/prefetch_macro.py in Codespaces to populate DX-Y.NYB. "
                    "DXY trend classification may be degraded.",
                    symbol,
                )
            else:
                logger.info("DXY loaded from canonical DX-Y.NYB: %d rows", len(df))
            return _DXY_CACHE
    return None


def get_vix_data_source() -> Optional[str]:
    """Return the symbol used for current VIX data ('^VIX' canonical or 'VXX' proxy)."""
    _load_vix_from_ohlcv_cache()
    return _VIX_SOURCE


def get_dxy_data_source() -> Optional[str]:
    """Return the symbol used for current DXY data ('DX-Y.NYB' canonical or 'UUP' proxy)."""
    _load_dxy_from_ohlcv_cache()
    return _DXY_SOURCE


def get_vix(start: date, end: date, as_of: Optional[date] = None) -> pd.DataFrame:
    """Return VIX data.

    Source priority (Pass 53 Day-9 v8 BUG-VIX-PROXY fix — Options A+B+C+D):
      1. FRED VIXCLS (canonical, point-in-time, no proxy distortion) — Option C
      2. ^VIX OHLCV cache (canonical via Codespaces yfinance prefetch) — Option A
      3. VXX OHLCV cache (proxy — Option B band-aid: classifier ignores level,
         uses 30-day return-volatility instead because VXX *price* is on a
         different numeric scale than VIX *index points*)
      4. Empty DataFrame + LOUD warning — Option D fail-loud
    """
    global _VIX_SOURCE
    effective_end = min(end, as_of) if as_of else end

    # 1. FRED VIXCLS — canonical
    fred = _load_vix_from_fred()
    if fred is not None and not fred.empty:
        _VIX_SOURCE = "FRED:VIXCLS"
        mask = (fred.index.date >= start) & (fred.index.date <= effective_end)
        sliced = fred[mask]
        if not sliced.empty:
            return sliced

    # 2. ^VIX OHLCV cache (canonical via yfinance prefetch)
    cached = _load_vix_from_ohlcv_cache()
    if cached is not None:
        mask = (cached.index.date >= start) & (cached.index.date <= effective_end)
        sliced = cached[mask]
        if not sliced.empty and _VIX_SOURCE == "^VIX":
            return sliced
        if not sliced.empty and _VIX_SOURCE == "VXX":
            # Don't return raw VXX — caller must handle scale per Option B.
            # Annotate so vix_regime() can take the proxy path.
            sliced = sliced.copy()
            sliced.attrs["scale"] = "VXX_PRICE_NOT_VIX_POINTS"
            return sliced

    # 4. Fail-loud — Option D
    logger.warning(
        "BUG-VIX-PROXY guard: no canonical VIX source available "
        "(checked FRED:VIXCLS, ^VIX OHLCV cache). VXX proxy disabled because "
        "its price level is not on the VIX-index scale. Run scripts/prefetch_macro.py "
        "to populate VIXCLS. Regime classification will return 'unknown'."
    )
    return pd.DataFrame()


def vix_regime(as_of: date, lookback_days: int = 5) -> str:
    start = as_of - timedelta(days=lookback_days + 10)
    df = get_vix(start, as_of, as_of=as_of)
    if df.empty:
        return "unknown"

    # Pass 53 Day-9 v8 BUG-VIX-PROXY Option B safeguard:
    # If the only available source is VXX (proxy), DO NOT use the dollar price
    # against VIX-index thresholds. Estimate vol-regime from VXX 30-day realized
    # vol of returns instead — different numeric scale, but ordinally aligned
    # with crisis/calm. Mark as 'unknown' if not enough history.
    if df.attrs.get("scale") == "VXX_PRICE_NOT_VIX_POINTS":
        if len(df) < 30:
            return "unknown"
        rets = df["vix"].pct_change().dropna().tail(30)
        if rets.empty:
            return "unknown"
        annualized_vol_pct = float(rets.std() * (252 ** 0.5) * 100)
        # Empirical mapping: VXX 30-day annualized return-vol of ~80% ~= VIX 25
        # (proxy — band-aid only; replace by FRED VIXCLS as soon as available).
        if annualized_vol_pct < 50:
            return "low"
        if annualized_vol_pct < 90:
            return "normal"
        if annualized_vol_pct < 130:
            return "elevated"
        return "crisis"

    v = float(df["vix"].iloc[-1])
    if v < 15:   return "low"
    if v < 25:   return "normal"
    if v < 35:   return "elevated"
    return "crisis"


def get_dxy(start: date, end: date, as_of: Optional[date] = None) -> pd.DataFrame:
    """Return DXY data — reads from OHLCV cache first (UUP proxy), falls back to yfinance."""
    effective_end = min(end, as_of) if as_of else end

    cached = _load_dxy_from_ohlcv_cache()
    if cached is not None:
        mask = (cached.index.date >= start) & (cached.index.date <= effective_end)
        return cached[mask]

    # Pass 53 Batch 13 sub-task 6 (DEC-497 D4 yfinance HARD CUT 2026-05-06):
    # No live API fallback. Cache miss → empty DataFrame.
    logger.debug("DXY cache miss; DEC-497 HARD CUT — no live yfinance fallback")
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


# DEC-304 fix (Pass 50): economic calendar migrated from hardcoded Python lists
# to JSON file (backtest/data/economic_calendar.json) for easier annual refresh.
# Hardcoded lists were ending March 2026 with no auto-warning past coverage.
# JSON loader provides: CPI_DATES, NFP_DATES, FOMC_DATES, _metadata.
# Run scripts/refresh_event_calendar.py to extend coverage.

ECONOMIC_CALENDAR_FILE = Path(__file__).parent / "economic_calendar.json"


def _load_economic_calendar() -> dict:
    """
    Load CPI/NFP/FOMC dates from JSON file. Returns dict with date lists
    (parsed to date objects) plus _metadata dict documenting source URLs
    and refresh instructions.

    DEC-304: replaces previously-hardcoded Python lists. JSON file is the
    single source; hardcoded fallback exists only if file missing (would
    indicate a packaging bug, not normal operation).
    """
    import json
    if not ECONOMIC_CALENDAR_FILE.exists():
        logger.error(
            "ECONOMIC CALENDAR FILE MISSING [DEC-304]: %s not found. "
            "is_near_high_impact_event will return no-events for all dates. "
            "Repository may be corrupt — restore from git or commit calendar JSON.",
            ECONOMIC_CALENDAR_FILE,
        )
        return {"CPI_DATES": [], "NFP_DATES": [], "FOMC_DATES": [],
                "_metadata": {"sources": {}, "schema_version": 0,
                              "error": "calendar file missing"}}
    raw = json.loads(ECONOMIC_CALENDAR_FILE.read_text())
    return {
        "CPI_DATES":  [date.fromisoformat(s) for s in raw.get("CPI_DATES",  [])],
        "NFP_DATES":  [date.fromisoformat(s) for s in raw.get("NFP_DATES",  [])],
        "FOMC_DATES": [date.fromisoformat(s) for s in raw.get("FOMC_DATES", [])],
        "_metadata":  raw.get("_metadata", {}),
    }


# Module-level constants populated from JSON at import time.
# These names preserved for backward compatibility with existing callers.
_calendar_data = _load_economic_calendar()
CPI_DATES  = _calendar_data["CPI_DATES"]
NFP_DATES  = _calendar_data["NFP_DATES"]
FOMC_DATES = _calendar_data["FOMC_DATES"]

ALL_HIGH_IMPACT = sorted(set(CPI_DATES + NFP_DATES + FOMC_DATES))
LAST_HARDCODED_EVENT = ALL_HIGH_IMPACT[-1] if ALL_HIGH_IMPACT else None

# DEC-304 fix (Pass 50): track whether we've already warned about calendar
# staleness so we don't spam logs (one warn per process is enough).
_CALENDAR_STALENESS_WARNED = False


def _check_calendar_coverage(as_of: date) -> None:
    """
    Warn if as_of is at or past the last hardcoded high-impact event date —
    means we have NO event filtering for forward dates and would silently
    treat all upcoming days as 'no events near'.

    DEC-304: hardcoded calendars end ~March 2026. Without this check the
    system silently degrades to no-event-filtering as time advances past
    the hardcoded end-date. Run scripts/refresh_event_calendar.py to extend.
    """
    global _CALENDAR_STALENESS_WARNED
    if _CALENDAR_STALENESS_WARNED or LAST_HARDCODED_EVENT is None:
        return
    days_remaining = (LAST_HARDCODED_EVENT - as_of).days
    if days_remaining <= 30:
        logger.warning(
            "CALENDAR STALENESS [DEC-304]: hardcoded event calendar ends %s "
            "(%d days from as_of=%s). Beyond this date, is_near_high_impact_event "
            "returns 'no events' silently. Run scripts/refresh_event_calendar.py "
            "or extend CPI_DATES/NFP_DATES/FOMC_DATES in macro.py.",
            LAST_HARDCODED_EVENT, days_remaining, as_of,
        )
        _CALENDAR_STALENESS_WARNED = True


def is_near_high_impact_event(as_of: date, window_days: int = 2) -> dict:
    _check_calendar_coverage(as_of)
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


# Pass 53 Batch 13 sub-task 3 (Wiring matrix Row 4 closure per DEC-507/L146/CHECKLIST #70):
# 5 high-priority FRED series wired into macro_snapshot composite per DEC-407+448 expansion.
# data_prefetch/fred/observations/{series_id}.parquet (Sprint 0A Batch 6 prefetched 50/52 series).

_REPO_ROOT_MACRO = Path(__file__).parent.parent.parent
PREFETCH_FRED_DIR = _REPO_ROOT_MACRO / "data_prefetch" / "fred" / "observations"


def _fred_value_at(series_id: str, as_of: date) -> Optional[float]:
    """Latest FRED observation value at-or-before `as_of` from prefetch cache.

    Returns None if cache miss or no observations on/before as_of.
    """
    path = PREFETCH_FRED_DIR / f"{series_id}.parquet"
    if not path.exists():
        return None
    try:
        df = pd.read_parquet(path)
        if df.empty or "date" not in df.columns or "value" not in df.columns:
            return None
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df = df[df["date"] <= as_of]
        if df.empty:
            return None
        return float(df.iloc[-1]["value"])
    except Exception as exc:
        logger.debug("_fred_value_at(%s, %s): %s", series_id, as_of, exc)
        return None


def hy_oas_signal(as_of: date) -> dict:
    """High-yield OAS regime classification (credit cycle leading indicator).

    BAMLH0A0HYM2 = ICE BofA US High Yield Index Option-Adjusted Spread (% over Treasury).
    Crisis signal when >8.0 (e.g., 2008 = 18%, 2020 COVID = 11%, 2022 = 6%).
    """
    val = _fred_value_at("BAMLH0A0HYM2", as_of)
    if val is None:
        return {"signal": "unknown", "value": None, "score": 0}
    if val < 3.0:
        return {"signal": "healthy_credit", "value": val, "score": 1}
    elif val < 6.0:
        return {"signal": "normal", "value": val, "score": 0}
    elif val < 8.0:
        return {"signal": "elevated", "value": val, "score": -1}
    else:
        return {"signal": "crisis", "value": val, "score": -2}


def financial_stress_signal(as_of: date) -> dict:
    """St Louis Fed financial stress index regime.

    STLFSI4: 0 = average historical stress; >0 = above-normal; <0 = below-normal.
    Crisis signal when >+3 (e.g., 2008 = 5+, 2020 = 5+).
    """
    val = _fred_value_at("STLFSI4", as_of)
    if val is None:
        return {"signal": "unknown", "value": None, "score": 0}
    if val < -1.0:
        return {"signal": "below_normal", "value": val, "score": 1}
    elif val < 1.0:
        return {"signal": "normal", "value": val, "score": 0}
    elif val < 3.0:
        return {"signal": "elevated", "value": val, "score": -1}
    else:
        return {"signal": "crisis", "value": val, "score": -2}


def recession_probability_signal(as_of: date) -> dict:
    """Smoothed recession probability (RECPROUSM156N).

    Values: 0-100% probability of US recession current month.
    >50% = high recession risk; >75% = imminent.
    """
    val = _fred_value_at("RECPROUSM156N", as_of)
    if val is None:
        return {"signal": "unknown", "value": None, "score": 0}
    if val < 20:
        return {"signal": "healthy", "value": val, "score": 1}
    elif val < 40:
        return {"signal": "elevated_risk", "value": val, "score": 0}
    elif val < 60:
        return {"signal": "high_risk", "value": val, "score": -1}
    else:
        return {"signal": "imminent_recession", "value": val, "score": -2}


def jobless_claims_signal(as_of: date) -> dict:
    """Initial jobless claims (ICSA) — high-frequency labor leading indicator.

    Weekly published. Recession trigger commonly cited as sustained >300K.
    """
    val = _fred_value_at("ICSA", as_of)
    if val is None:
        return {"signal": "unknown", "value": None, "score": 0}
    if val < 250_000:
        return {"signal": "strong", "value": val, "score": 1}
    elif val < 350_000:
        return {"signal": "normal", "value": val, "score": 0}
    elif val < 450_000:
        return {"signal": "weakening", "value": val, "score": -1}
    else:
        return {"signal": "recession_indicator", "value": val, "score": -2}


def fed_balance_sheet_signal(as_of: date, lookback_days: int = 90) -> dict:
    """Fed balance sheet trajectory (WALCL) — QE vs QT direction.

    Compares current value to ~90 days ago; growing = QE (bullish liquidity);
    shrinking = QT (bearish liquidity).
    """
    val_now = _fred_value_at("WALCL", as_of)
    val_past = _fred_value_at("WALCL", as_of - timedelta(days=lookback_days))
    if val_now is None or val_past is None or val_past == 0:
        return {"signal": "unknown", "value": val_now, "score": 0,
                "delta_pct": None}
    delta_pct = (val_now - val_past) / val_past * 100
    if delta_pct > 1.0:
        return {"signal": "expansion_qe", "value": val_now, "score": 1,
                "delta_pct": delta_pct}
    elif delta_pct < -1.0:
        return {"signal": "contraction_qt", "value": val_now, "score": -1,
                "delta_pct": delta_pct}
    else:
        return {"signal": "stable", "value": val_now, "score": 0,
                "delta_pct": delta_pct}


def macro_snapshot(as_of: date) -> dict:
    """Composite macro context snapshot.

    Pass 53 Batch 13 sub-task 3 expansion (DEC-507 wiring matrix Row 4):
    Adds HY OAS / STLFSI4 / Recession Prob / ICSA / WALCL signals to
    pre-existing yield curve / VIX / DXY / event-calendar composite.
    """
    from backtest.config import BACKTEST_START
    yc  = yield_curve_regime(as_of)
    vr  = vix_regime(as_of)
    dxy = dxy_trend(as_of)
    ec  = is_near_high_impact_event(as_of)
    vix_df = get_vix(as_of - timedelta(days=5), as_of, as_of=as_of)
    vix_val = float(vix_df["vix"].iloc[-1]) if not vix_df.empty else None
    # Existing signals (legacy scoring)
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
    # Pass 53 Batch 13 expansion: 5 high-priority FRED signals
    hy = hy_oas_signal(as_of)
    fs = financial_stress_signal(as_of)
    rp = recession_probability_signal(as_of)
    jc = jobless_claims_signal(as_of)
    bs = fed_balance_sheet_signal(as_of)
    score += hy["score"] + fs["score"] + rp["score"] + jc["score"] + bs["score"]
    return {
        # Existing fields
        "yield_curve_regime":     yc,
        "vix_regime":             vr,
        "vix_value":              vix_val,
        "dxy_trend":              dxy,
        "near_high_impact_event": ec["blocked"],
        "event_type":             ec.get("nearest_event_type"),
        "event_days_away":        ec.get("days_away"),
        # NEW Pass 53 Batch 13 expansion
        "hy_oas":                hy,
        "financial_stress":      fs,
        "recession_probability": rp,
        "jobless_claims":        jc,
        "fed_balance_sheet":     bs,
        # Composite
        "macro_score":            score,
    }
