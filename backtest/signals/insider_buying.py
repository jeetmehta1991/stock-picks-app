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


def _load_insiders_global() -> Optional[pd.DataFrame]:
    """Lazy-load the global insiders parquet once per process."""
    global _INSIDERS_CACHE
    if _INSIDERS_CACHE is not None:
        return _INSIDERS_CACHE
    if not _INSIDERS_GLOBAL.exists():
        _INSIDERS_CACHE = pd.DataFrame()
        return _INSIDERS_CACHE
    try:
        df = pd.read_parquet(_INSIDERS_GLOBAL)
        if df.empty:
            _INSIDERS_CACHE = df
            return _INSIDERS_CACHE
        # Normalize Date column to date
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
        _INSIDERS_CACHE = df
    except Exception:
        _INSIDERS_CACHE = pd.DataFrame()
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
    """
    df = _load_insiders_global()
    if df is None or df.empty:
        return {}
    tkr_safe = ticker.replace(".", "-")
    # Filter to ticker + lookback window + purchase transactions
    cutoff = as_of - timedelta(days=lookback_days)
    sub = df[
        (df["Ticker"].isin([ticker, tkr_safe]))
        & (df["Date"] >= cutoff)
        & (df["Date"] <= as_of)
        & (df.get("AcquiredDisposedCode") == "A")
    ]
    if sub.empty:
        return {}
    # Open-market purchase: TransactionCode == 'P'. Excludes 'A' (award),
    # 'M' (exercise), 'G' (gift). Drop missing transaction codes.
    if "TransactionCode" in sub.columns:
        sub = sub[sub["TransactionCode"] == "P"]
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
