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

import functools
from datetime import date
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

_SI_CACHE_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "data_prefetch" / "finra" / "short_interest"
)

_REPO_SI = Path(__file__).resolve().parent.parent.parent
# S6-B3139bn (owner ruling 2026-10-06, packet row 26 'publish'): FINRA
# publishes a settlement's figures 7 NYSE trading days after the settlement
# date - 28 of 28 rows on FINRA's published schedule fit
# (output_audit/b3139bj_short_interest_publication_lag.json). A settlement is
# usable from its publication date, never from the settlement date.
_PUBLICATION_SCHEDULE_CSV = _REPO_SI / "data_prefetch" / "finra" / "publication_schedule.csv"
PUBLICATION_LAG_TRADING_DAYS = 7
# S6-B3139bd (owner ruling 2026-10-06, packet row 22 'source-dated'): the
# share count short_interest_pct divides by is the dei cover-page count FILED
# on or before the settlement (scripts/build_dei_shares_store.py).
_DEI_SHARES_PATH = _REPO_SI / "data_prefetch" / "sec_xbrl" / "dei_shares_outstanding.parquet"


@functools.lru_cache(maxsize=1)
def _nyse_days() -> pd.DatetimeIndex:
    import pandas_market_calendars as mcal
    return pd.DatetimeIndex(mcal.get_calendar("NYSE").valid_days("2010-01-01", "2030-12-31")
                            .tz_localize(None))


@functools.lru_cache(maxsize=1)
def _publication_schedule() -> dict:
    if not _PUBLICATION_SCHEDULE_CSV.exists():
        return {}
    s = pd.read_csv(_PUBLICATION_SCHEDULE_CSV)
    return {date.fromisoformat(a): date.fromisoformat(b)
            for a, b in zip(s["settlement_date"], s["publication_date"])}


def finra_dissemination_date(settlement: date) -> date:
    """The date a settlement's short interest became public: FINRA's listed
    publication date where the schedule carries it, else settlement + 7 NYSE
    trading days (a settlement on a non-trading day counts from the prior
    trading day, as the schedule does)."""
    listed = _publication_schedule().get(settlement)
    if listed is not None:
        return listed
    days = _nyse_days()
    i = int(np.searchsorted(days.values, np.datetime64(pd.Timestamp(settlement))))
    k = PUBLICATION_LAG_TRADING_DAYS
    if i < len(days) and days[i].date() == settlement:
        return days[i + k].date()
    return days[i + k - 1].date()


@functools.lru_cache(maxsize=1)
def _dei_store() -> dict:
    if not _DEI_SHARES_PATH.exists():
        return {}
    df = pd.read_parquet(_DEI_SHARES_PATH, columns=["ticker", "end", "filed", "val"])
    df["end"] = pd.to_datetime(df["end"]).dt.date
    df["filed"] = pd.to_datetime(df["filed"]).dt.date
    df = df[df["val"] > 0].sort_values(["ticker", "end", "filed"])
    return {t: g.reset_index(drop=True) for t, g in df.groupby("ticker")}


def dated_shares_outstanding(ticker: str, settlement: date) -> Optional[float]:
    """The cover-page share count a reader could have seen at `settlement`:
    among dei facts FILED on or before it, the one with the latest as-of
    date. None when the ticker has no such fact (excluded, never imputed)."""
    g = _dei_store().get(ticker.replace(".", "-").upper())
    if g is None:
        return None
    k = g[g["filed"] <= settlement]
    if k.empty:
        return None
    return float(k.iloc[-1]["val"])

# B1240 (2026-07-07 Council 290 S5-B1214 fix):
# FINRA cache has shares_outstanding = NULL for all rows (upstream data gap).
# Finnhub profile2 has shareOutstanding field with 95.5% Batch A coverage +
# 95-102% accuracy vs authoritative sources (per B1239 investigation).
# Use as fallback when FINRA row's shares_outstanding is missing.
_FINNHUB_PROFILE2_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "data_prefetch" / "finnhub" / "profile2"
)

_FINNHUB_SHARES_CACHE: dict[str, Optional[float]] = {}


def _load_shares_outstanding_from_finnhub(ticker: str) -> Optional[float]:
    """B1240 (Council 290 S5-B1214): return shares_outstanding for a ticker
    from Finnhub profile2 cache. Returns None on data miss.

    Finnhub profile2 has `shareOutstanding` field expressed in MILLIONS of
    shares. This helper multiplies by 1e6 to return raw share count.

    Validation (B1239): 95-102% accuracy vs SEC-authoritative shares_outstanding
    for AAPL/MSFT/GOOG/NVDA/AMZN/META; some deviation on high-turnover names
    (TSLA 117%, GME 147%) but sufficient for the >= 20% threshold check in
    strat_squeeze_setup_long.
    """
    if ticker in _FINNHUB_SHARES_CACHE:
        return _FINNHUB_SHARES_CACHE[ticker]
    path = _FINNHUB_PROFILE2_DIR / f"{ticker}.parquet"
    if not path.exists():
        _FINNHUB_SHARES_CACHE[ticker] = None
        return None
    try:
        df = pd.read_parquet(path)
        if df.empty:
            _FINNHUB_SHARES_CACHE[ticker] = None
            return None
        so_millions = df.iloc[0].get("shareOutstanding")
        if so_millions is None or so_millions <= 0:
            _FINNHUB_SHARES_CACHE[ticker] = None
            return None
        raw_shares = float(so_millions) * 1_000_000
        _FINNHUB_SHARES_CACHE[ticker] = raw_shares
        return raw_shares
    except Exception:
        _FINNHUB_SHARES_CACHE[ticker] = None
        return None

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
    df = _with_dissemination(df.sort_values("settlement_date").reset_index(drop=True))
    _SI_BY_TICKER[safe_ticker] = df
    return df


def _with_dissemination(df: pd.DataFrame) -> pd.DataFrame:
    """S6-B3139bn: the publication date beside every settlement - read from
    the file when the prefetcher wrote it, derived by the one rule otherwise."""
    if "dissemination_date" in df.columns:
        df = df.copy()
        df["dissemination_date"] = pd.to_datetime(df["dissemination_date"]).dt.date
        return df
    return df.assign(dissemination_date=[finra_dissemination_date(d) for d in df["settlement_date"]])


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
    if "dissemination_date" not in src.columns:
        src = _with_dissemination(src)
    # S6-B3139bn: a settlement is usable from its PUBLICATION date
    past = src[src["dissemination_date"] <= as_of]
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
    # S6-B3139bd (owner ruling 2026-10-06, packet row 22): the denominator is
    # a count DATED at the settlement - FINRA's own field (100 pct NULL as of
    # B1214) or the dei cover-page count filed on or before the settlement.
    # The undated Finnhub profile2 count (B1240) is no longer consulted: it is
    # TODAY's count and flipped 258 of 711 same-order-band gate decisions
    # (output_audit/b3139d_short_interest_pit_measure.json). No dated count ->
    # no short_interest_pct (excluded from the share-dependent layer).
    if so > 0:
        out["short_interest_shares_outstanding_source"] = "finra"
    else:
        dated = dated_shares_outstanding(ticker, most_recent["settlement_date"])
        if dated:
            so = dated
            out["short_interest_shares_outstanding_source"] = "sec_dei_dated"
        else:
            out["short_interest_shares_outstanding_source"] = "none_dated"
    if so > 0:
        out["short_interest_pct"] = round(si / so, 6)
    if adv > 0:
        out["days_to_cover"] = round(si / adv, 4)
    return out


__all__ = [
    "EXPECTED_COLS",
    "compute_short_interest_signals",
]
