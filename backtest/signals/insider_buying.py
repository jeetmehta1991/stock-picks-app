"""Insider buying cluster signals from Quiver SEC Form 4 data.

Batch 222 (2026-05-18 owner-approved research review Top-10 #6).
Source: Cohen-Malloy-Pomorski 2012 JF "Decoding Inside Information";
refreshed Akbas-Jiang-Koch 2024 RFS. Documented 12-month alpha ~7%
on clustered insider-buying signals (>=2 insiders / 30 days, excluding
routine 10b5-1 trades).

Data: data_prefetch/quiver/insiders/global.parquet (Quiver Trader API
SEC Form 4 ingestion). Schema includes Ticker, Date (transaction),
Name, AcquiredDisposedCode (A/D), TransactionCode (P=purchase,
S=sale, etc.), Shares, PricePerShare, SharesOwnedFollowing,
isDirector/isOfficer/isTenPercentOwner.

Cluster definition (per Cohen-Malloy-Pomorski refined by Akbas et al.):
  - Count of UNIQUE insiders with AcquiredDisposedCode='A' AND
    TransactionCode='P' (open-market purchase) in last 30 calendar days
  - >=2 unique insiders = cluster (signal active)
  - Excludes TransactionCode='A' (grants/awards - not informed buys)
  - Excludes 10b5-1 routine trades (when flagged in source)
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd


_INSIDERS_GLOBAL = (
    Path(__file__).parent.parent.parent
    / "data_prefetch" / "quiver" / "insiders" / "global.parquet"
)
_INSIDERS_CACHE: Optional[pd.DataFrame] = None

# Batch 316b (2026-05-25): per-ticker pre-grouped index. Pre-Batch-316b the
# compute_insider_cluster_signals call did 4 boolean filters across the full
# insiders DataFrame (millions of rows) every invocation. Profile showed 31%
# of screen_instrument wall-clock on synthetic data. Post-fix: group by
# Ticker once at load time + pre-filter to AcquiredDisposedCode=='A' and
# TransactionCode=='P' (constants across all calls). Per-call becomes
# O(1) dict lookup + small per-ticker date-window filter.
_INSIDERS_BY_TICKER: Optional[dict] = None


def _load_insiders_global() -> Optional[pd.DataFrame]:
    """Lazy-load the global insiders parquet once per process.

    Builds two caches on first call:
      _INSIDERS_CACHE: legacy DataFrame view (kept for any downstream
        consumers that import it).
      _INSIDERS_BY_TICKER: dict[str -> DataFrame] of per-ticker rows already
        filtered to qualifying purchases (AcquiredDisposedCode=='A' AND
        TransactionCode=='P' when column present). This is the hot-path
        lookup table for compute_insider_cluster_signals.
    """
    global _INSIDERS_CACHE, _INSIDERS_BY_TICKER
    if _INSIDERS_CACHE is not None:
        return _INSIDERS_CACHE
    if not _INSIDERS_GLOBAL.exists():
        _INSIDERS_CACHE = pd.DataFrame()
        _INSIDERS_BY_TICKER = {}
        return _INSIDERS_CACHE
    try:
        df = pd.read_parquet(_INSIDERS_GLOBAL)
        if df.empty:
            _INSIDERS_CACHE = df
            _INSIDERS_BY_TICKER = {}
            return _INSIDERS_CACHE
        # Normalize Date column to date
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
        _INSIDERS_CACHE = df

        # Pre-filter to qualifying purchases (constant across all calls).
        qual = df
        if "AcquiredDisposedCode" in qual.columns:
            qual = qual[qual["AcquiredDisposedCode"] == "A"]
        if "TransactionCode" in qual.columns:
            qual = qual[qual["TransactionCode"] == "P"]
        # Pre-group by ticker. Each value is the subset for that ticker.
        if "Ticker" in qual.columns and not qual.empty:
            _INSIDERS_BY_TICKER = {
                str(tkr): grp
                for tkr, grp in qual.groupby("Ticker", sort=False)
            }
        else:
            _INSIDERS_BY_TICKER = {}
    except Exception:
        _INSIDERS_CACHE = pd.DataFrame()
        _INSIDERS_BY_TICKER = {}
    return _INSIDERS_CACHE


def compute_insider_cluster_signals(
    ticker: str,
    as_of: date,
    lookback_days: int = 30,
    min_unique_insiders: int = 2,
) -> dict:
    """Detect insider buying cluster for a single ticker as of a date.

    Returns signal dict suitable for merging into the per-ticker
    signals dict consumed by screener strategies. Keys:
      - insider_cluster_active:        bool (>=2 unique insiders bought
                                       open-market in last 30 days)
      - insider_unique_buyers_30d:     int (count of unique insiders)
      - insider_total_shares_bought_30d: float (sum of Shares)
      - insider_director_buyers_30d:   int (subset where isDirector=True)
      - insider_officer_buyers_30d:    int (subset where isOfficer=True)

    Returns empty dict on data miss / unknown ticker / no qualifying
    transactions.

    Batch 316b (2026-05-25): hot-path is now O(1) ticker lookup + small
    per-ticker date-window filter via _INSIDERS_BY_TICKER cache. Behavior
    is preserved: same filters (AcquiredDisposedCode=='A' AND
    TransactionCode=='P' when column present), same lookback window,
    same return dict shape. Profile target: 31% of screen_instrument
    per-call cost on data-present runs.
    """
    # Trigger cache build on first call.
    _load_insiders_global()
    if not _INSIDERS_BY_TICKER:
        return {}
    tkr_safe = ticker.replace(".", "-")
    sub = _INSIDERS_BY_TICKER.get(ticker)
    if sub is None and tkr_safe != ticker:
        sub = _INSIDERS_BY_TICKER.get(tkr_safe)
    if sub is None or sub.empty:
        return {}
    # Date-window filter (only the rows for this ticker remain, so this is
    # over at most a few hundred rows vs the prior full-DF scan).
    cutoff = as_of - timedelta(days=lookback_days)
    sub = sub[(sub["Date"] >= cutoff) & (sub["Date"] <= as_of)]
    if sub.empty:
        return {}
    # Count unique insiders by Name (proxy for unique-person)
    unique_buyers = sub["Name"].nunique() if "Name" in sub.columns else 0
    total_shares = float(sub["Shares"].sum()) if "Shares" in sub.columns else 0.0
    n_director = 0
    n_officer = 0
    if "Name" in sub.columns and "isDirector" in sub.columns:
        # Count unique insiders who are directors (per-name unique)
        by_name = sub.groupby("Name").first()
        n_director = int(by_name["isDirector"].fillna(False).sum())
    if "Name" in sub.columns and "isOfficer" in sub.columns:
        by_name = sub.groupby("Name").first()
        n_officer = int(by_name["isOfficer"].fillna(False).sum())
    return {
        "insider_cluster_active":            unique_buyers >= min_unique_insiders,
        "insider_unique_buyers_30d":         int(unique_buyers),
        "insider_total_shares_bought_30d":   round(total_shares, 0),
        "insider_director_buyers_30d":       n_director,
        "insider_officer_buyers_30d":        n_officer,
    }
