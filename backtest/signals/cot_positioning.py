"""Batch 472 (2026-05-29) -- P11 CFTC COT macro-positioning producer.

Reads weekly Commitments of Traders reports per instrument
(`data_prefetch/cftc/cot_<series>.parquet`) and emits per-as_of net
positioning percentile signals over a 3-year (156-week) rolling window.

The CFTC publishes these reports weekly (Tuesday positions, Friday release).
Each report describes how multiple trader categories (commercials,
managed-money, dealers, etc.) are positioned in the futures market.
Extreme net positioning -- commercials very long or very short relative
to history -- is a contrarian / mean-reversion signal in many academic
studies (e.g. Hong-Yogo 2012 "What Does Futures Market Interest Tell Us
About the Macroeconomy and Asset Prices?").

Source data layout (verified 2026-05-29 per CHECKLIST #99):
  cols include: report_date_as_yyyy_mm_dd, prod_merc_positions_long,
                prod_merc_positions_short, m_money_positions_long_all,
                m_money_positions_short_all, open_interest_all,
                report_date (Timestamp)
  coverage: ~1038 weekly observations per series (~20y)

Signals emitted PER series (universe-wide, ticker-agnostic):
  cot_<series>_commercials_net_pct  -- (net long - net short) as a fraction of
                                       open interest at as_of
  cot_<series>_commercials_pctile_3y -- percentile of current net positioning
                                        within trailing 156 weekly snapshots
                                        (0..1, 0 = lowest 3y, 1 = highest 3y)
  cot_<series>_mmoney_pctile_3y    -- managed-money equivalent (where the
                                        column exists -- not all instruments
                                        have a managed-money breakdown).

Where <series> maps to one of:
  sp500   (cot_emini_sp500.parquet)
  ndx     (cot_emini_nasdaq100.parquet)
  rut     (cot_emini_russell2k.parquet)
  dow     (cot_emini_dow.parquet)
  dxy     (cot_dxy_dollar_idx.parquet)
  gold    (cot_gold.parquet)
  copper  (cot_copper.parquet)

A single `get_all_cot_signals(as_of)` call returns the merged dict for
universe-wide signal injection in the screener (these are macro overlays,
identical for every ticker on a given as_of date).
"""
from __future__ import annotations

from datetime import date
from functools import lru_cache
from pathlib import Path

import pandas as pd


_COT_DIR = Path(__file__).parent.parent.parent / "data_prefetch" / "cftc"


SERIES_FILE_MAP = {
    "sp500":  "cot_emini_sp500.parquet",
    "ndx":    "cot_emini_nasdaq100.parquet",
    "rut":    "cot_emini_russell2k.parquet",
    "dow":    "cot_emini_dow.parquet",
    "dxy":    "cot_dxy_dollar_idx.parquet",
    "gold":   "cot_gold.parquet",
    "copper": "cot_copper.parquet",
}


@lru_cache(maxsize=16)
def _load_cot_series(filename: str) -> pd.DataFrame:
    """Load + cache one COT instrument file."""
    path = _COT_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()
    if df.empty:
        return df
    # Normalize a date column: prefer report_date (Timestamp), fall back to parsing the string
    if "report_date" in df.columns:
        df = df.copy()
        df["report_date"] = pd.to_datetime(df["report_date"], errors="coerce")
    elif "report_date_as_yyyy_mm_dd" in df.columns:
        df = df.copy()
        df["report_date"] = pd.to_datetime(
            df["report_date_as_yyyy_mm_dd"], errors="coerce")
    else:
        return pd.DataFrame()
    df = df.dropna(subset=["report_date"])
    df["d"] = df["report_date"].dt.date
    return df.sort_values("d")


def _commercials_columns(df: pd.DataFrame) -> tuple[str | None, str | None]:
    """Resolve commercial long/short columns; some instrument schemas use
    dealer_* (financial-instrument format) instead of prod_merc_* (commodity
    format). Returns (long_col, short_col) or (None, None) if neither
    convention is present."""
    if "prod_merc_positions_long" in df.columns \
            and "prod_merc_positions_short" in df.columns:
        return "prod_merc_positions_long", "prod_merc_positions_short"
    if "dealer_positions_long_all" in df.columns \
            and "dealer_positions_short_all" in df.columns:
        return "dealer_positions_long_all", "dealer_positions_short_all"
    return None, None


def _mmoney_columns(df: pd.DataFrame) -> tuple[str | None, str | None]:
    """Resolve managed-money long/short columns (commodity format) or
    leveraged-money (financial format)."""
    if "m_money_positions_long_all" in df.columns \
            and "m_money_positions_short_all" in df.columns:
        return "m_money_positions_long_all", "m_money_positions_short_all"
    if "lev_money_positions_long" in df.columns \
            and "lev_money_positions_short" in df.columns:
        return "lev_money_positions_long", "lev_money_positions_short"
    return None, None


def compute_cot_series_signals(series: str, as_of: date) -> dict:
    """Compute COT signals for one instrument as-of a date.

    Returns dict with keys (where available):
      cot_<series>_commercials_net_pct
      cot_<series>_commercials_pctile_3y
      cot_<series>_mmoney_pctile_3y
    """
    if series not in SERIES_FILE_MAP:
        return {}
    df = _load_cot_series(SERIES_FILE_MAP[series])
    if df.empty:
        return {}
    pit = df[df["d"] <= as_of]
    if pit.empty:
        return {}
    out: dict = {}
    long_c, short_c = _commercials_columns(pit)
    if long_c and short_c and "open_interest_all" in pit.columns:
        net = (pd.to_numeric(pit[long_c], errors="coerce")
               - pd.to_numeric(pit[short_c], errors="coerce"))
        oi = pd.to_numeric(pit["open_interest_all"], errors="coerce")
        net_pct = (net / oi).where(oi > 0)
        cur = float(net_pct.iloc[-1]) if not net_pct.empty \
            and not pd.isna(net_pct.iloc[-1]) else None
        if cur is not None:
            out[f"cot_{series}_commercials_net_pct"] = round(cur, 4)
            tail156 = net_pct.tail(156).dropna()
            if len(tail156) >= 20:
                pctile = float((tail156 <= cur).mean())
                out[f"cot_{series}_commercials_pctile_3y"] = round(pctile, 4)
    long_m, short_m = _mmoney_columns(pit)
    if long_m and short_m and "open_interest_all" in pit.columns:
        netm = (pd.to_numeric(pit[long_m], errors="coerce")
                - pd.to_numeric(pit[short_m], errors="coerce"))
        oi = pd.to_numeric(pit["open_interest_all"], errors="coerce")
        netm_pct = (netm / oi).where(oi > 0)
        curm = float(netm_pct.iloc[-1]) if not netm_pct.empty \
            and not pd.isna(netm_pct.iloc[-1]) else None
        if curm is not None:
            tail156 = netm_pct.tail(156).dropna()
            if len(tail156) >= 20:
                pctile_m = float((tail156 <= curm).mean())
                out[f"cot_{series}_mmoney_pctile_3y"] = round(pctile_m, 4)
    return out


def get_all_cot_signals(as_of: date) -> dict:
    """Universe-wide COT positioning signals -- identical for every ticker on
    a given as_of date. Merge per-series outputs into a single dict for
    injection into the screener pipeline."""
    out: dict = {}
    for series in SERIES_FILE_MAP:
        try:
            out.update(compute_cot_series_signals(series, as_of))
        except Exception:
            continue
    return out
