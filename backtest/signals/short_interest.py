"""Batch 494 (2026-05-30) -- P15 FINRA short-interest producer (scaffold).

Source: per CHECKLIST #77 (test extensively) and CHECKLIST #99 (schema-
verify before producer ships).
Queue row: EXECUTION_QUEUE.md item P15.

State as of 2026-05-30: data NOT prefetched. The expected cache path
`data_prefetch/finra/short_interest/<TICKER>.parquet` does not exist.
This module emits {} for all callers until the prefetch lands.

Why ship the scaffold now:
  - Wiring (screener-level call site) can land separately from data
    arrival; bundling the two has historically caused integration debt
    (DEC-507 wiring matrix). Producer + tests ship now; prefetch +
    strategy variants ship when owner approves the data source.
  - Tests use mock dataframes to validate the math + emit shape.
  - When data arrives, no producer-side change is needed -- only the
    fetcher script writes the parquet, and ALL_STRATEGIES gets the new
    sleeve names appended.

Producer outputs (per ticker at as_of):
  short_interest_pct       : SI / shares_outstanding (0..1)
  days_to_cover            : SI / avg_daily_volume_20d (days)
  short_interest_observations: count of biweekly snapshots used

Academic backing: Cohen-Diether-Malloy 2007 "Supply and Demand Shifts
in the Shorting Market" -- short-interest changes predict negative
abnormal returns; days-to-cover is a robust squeeze-risk filter.

NEW STRATEGIES (deferred to follow-on batch when data lands):
  squeeze_setup_long          : SI >= 20% + bullish breakout (long)
  short_borrow_trap_avoid     : DTC > 5 -> reject for short strategies
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

_SI_CACHE_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "data_prefetch" / "finra" / "short_interest"
)

# Schema of the expected per-ticker parquet (when prefetch lands):
#   settlement_date   : YYYY-MM-DD biweekly settlement date
#   short_interest    : float  -- shares short on that date
#   shares_outstanding: float  -- total shares outstanding
#   avg_daily_volume  : float  -- 20-day ADV at settlement_date
EXPECTED_COLS = ("settlement_date", "short_interest",
                 "shares_outstanding", "avg_daily_volume")

# Batch 535 OPT-A: per-ticker in-memory cache (first call fills, subsequent
# calls O(1) lookup -- no disk IO). 1926 universe-active tickers x ~5KB
# each = ~10MB max.
_SI_BY_TICKER: dict[str, pd.DataFrame] = {}


def _load_ticker_si(ticker: str) -> pd.DataFrame:
    """Load the cached per-ticker FINRA short-interest history.

    Returns empty DataFrame on cache miss or schema mismatch (graceful
    empty per L86: never raise from producer; let strategies degrade
    quietly when source data is absent).

    Batch 535 OPT-A: in-memory cache by safe_ticker; first call reads
    disk, subsequent calls return cached DataFrame.
    """
    safe_ticker = ticker.replace(".", "-").upper()
    cached = _SI_BY_TICKER.get(safe_ticker)
    if cached is not None:
        return cached
    path = _SI_CACHE_DIR / f"{safe_ticker}.parquet"
    empty = pd.DataFrame(columns=list(EXPECTED_COLS))
    if not path.exists():
        _SI_BY_TICKER[safe_ticker] = empty
        return empty
    try:
        df = pd.read_parquet(path)
    except Exception:
        _SI_BY_TICKER[safe_ticker] = empty
        return empty
    missing = [c for c in EXPECTED_COLS if c not in df.columns]
    if missing:
        _SI_BY_TICKER[safe_ticker] = empty
        return empty
    df = df.copy()
    df["settlement_date"] = pd.to_datetime(df["settlement_date"]).dt.date
    df = df.sort_values("settlement_date").reset_index(drop=True)
    _SI_BY_TICKER[safe_ticker] = df
    return df


def compute_short_interest_signals(
    ticker: str,
    as_of: date,
    df: Optional[pd.DataFrame] = None,
) -> dict:
    """Compute short-interest signals for a ticker as-of a date.

    Returns dict (empty on cache-miss / no observations <= as_of):
      short_interest_pct                 : float in [0, 1]
      days_to_cover                      : float (days)
      short_interest_observations        : int (>=1)
      short_interest_settlement_date     : date of latest snapshot used

    Args:
      ticker: equity symbol
      as_of:  PIT date; only snapshots with settlement_date <= as_of
              are eligible
      df:     optional injected DataFrame (testing); skips disk load

    No-data behavior: returns {} so downstream strategies degrade
    quietly. This is the same convention as compute_pead_signals.
    """
    src = df if df is not None else _load_ticker_si(ticker)
    if src is None or src.empty:
        return {}
    past = src[src["settlement_date"] <= as_of]
    if past.empty:
        return {}
    most_recent = past.iloc[-1]
    si = float(most_recent.get("short_interest") or 0.0)
    so = float(most_recent.get("shares_outstanding") or 0.0)
    adv = float(most_recent.get("avg_daily_volume") or 0.0)
    out: dict = {
        "short_interest_observations": int(len(past)),
        "short_interest_settlement_date": most_recent["settlement_date"],
    }
    if so > 0:
        out["short_interest_pct"] = round(si / so, 6)
    if adv > 0:
        out["days_to_cover"] = round(si / adv, 4)
    return out


__all__ = [
    "EXPECTED_COLS",
    "compute_short_interest_signals",
]
