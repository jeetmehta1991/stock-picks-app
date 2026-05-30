"""Batch 473 (2026-05-29) -- P16 sub-items: housetrading + gov_contracts.

Two Quiver alt-data producers wired into a single module:

  1. compute_housetrading_signals  -- US House members' personal stock
     trades (Ziobrowski et al. 2004 / Belmont 2008 documents +6pp annual
     alpha on Congress-member trade-following). Emits per-ticker counts
     of recent buys vs sells from House members.

  2. compute_gov_contracts_signals -- federal contract awards per ticker
     (Hill-Kelly-Lockhart 2014 RFS variant; Cohen-Gurun-Malloy 2012
     documents alpha on government-spending-exposed equities). Emits
     last-quarter contract amount + 4-quarter rolling sum.

Both producers are SAFE-ADDITIVE: returning {} on data miss preserves
backward compat; consumers should s.get(...) with defaults.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd


_HOUSETRADING_DIR = (
    Path(__file__).parent.parent.parent / "data_prefetch"
    / "quiver" / "housetrading"
)
_GOV_CONTRACTS_DIR = (
    Path(__file__).parent.parent.parent / "data_prefetch"
    / "quiver" / "gov_contracts"
)
_LOBBYING_DIR = (
    Path(__file__).parent.parent.parent / "data_prefetch"
    / "quiver" / "lobbying"
)


def compute_housetrading_signals(
    ticker: str,
    as_of: date,
    lookback_days: int = 90,
) -> dict:
    """House-member trading signals over the last `lookback_days`.

    Returns dict with optional keys:
      house_buy_count_90d   -- distinct House members who PURCHASED in window
      house_sell_count_90d  -- distinct House members who SOLD in window
      house_net_buy_90d     -- buy_count - sell_count (>0 net buying)
      house_cluster_buy     -- bool: >=3 distinct buyers
      house_cluster_sell    -- bool: >=3 distinct sellers
    """
    safe_ticker = ticker.replace(".", "-")
    path = _HOUSETRADING_DIR / f"{safe_ticker}.parquet"
    if not path.exists():
        return {}
    try:
        df = pd.read_parquet(path)
    except Exception:
        return {}
    if df.empty or "Date" not in df.columns \
            or "Transaction" not in df.columns:
        return {}
    try:
        df = df.copy()
        df["d"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
        df = df.dropna(subset=["d"])
        df = df[df["d"] <= as_of]
        window_start = as_of - timedelta(days=lookback_days)
        recent = df[df["d"] >= window_start]
    except Exception:
        return {}
    if recent.empty:
        return {
            "house_buy_count_90d":  0, "house_sell_count_90d": 0,
            "house_net_buy_90d":    0,
            "house_cluster_buy":   False, "house_cluster_sell": False,
        }
    buys = recent[recent["Transaction"].str.lower() == "purchase"]
    sells = recent[recent["Transaction"].str.lower() == "sale"]
    buy_count = int(buys["Representative"].nunique()) \
        if "Representative" in buys.columns else int(len(buys))
    sell_count = int(sells["Representative"].nunique()) \
        if "Representative" in sells.columns else int(len(sells))
    return {
        "house_buy_count_90d":  buy_count,
        "house_sell_count_90d": sell_count,
        "house_net_buy_90d":    buy_count - sell_count,
        "house_cluster_buy":    buy_count >= 3,
        "house_cluster_sell":   sell_count >= 3,
    }


def compute_gov_contracts_signals(ticker: str, as_of: date) -> dict:
    """Federal contracts awarded to `ticker`. Emits:
      gov_contracts_last_qtr_amount   -- Most recent quarter's amount.
      gov_contracts_4q_sum            -- Sum of last 4 quarterly amounts.
      gov_contracts_qoq_growth        -- (last - prior) / prior; 0.0 if no
                                          prior. Captures rising/declining
                                          federal-spending exposure.

    Quiver gov_contracts cadence is QUARTERLY (Year + Qtr columns).
    """
    safe_ticker = ticker.replace(".", "-")
    path = _GOV_CONTRACTS_DIR / f"{safe_ticker}.parquet"
    if not path.exists():
        return {}
    try:
        df = pd.read_parquet(path)
    except Exception:
        return {}
    if df.empty:
        return {}
    if "Year" not in df.columns or "Qtr" not in df.columns \
            or "Amount" not in df.columns:
        return {}
    try:
        df = df.copy()
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
        df["Qtr"] = pd.to_numeric(df["Qtr"], errors="coerce")
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        df = df.dropna(subset=["Year", "Qtr"])
        # Quarter end-date proxy: PIT cutoff applied as
        # (year, quarter) <= (as_of.year, as_of.quarter).
        as_of_qtr = (as_of.month - 1) // 3 + 1
        df["qtr_key"] = df["Year"] * 10 + df["Qtr"]
        cutoff_key = as_of.year * 10 + as_of_qtr
        df = df[df["qtr_key"] <= cutoff_key].sort_values("qtr_key")
    except Exception:
        return {}
    if df.empty:
        return {}
    last_qtr_amt = float(df.iloc[-1]["Amount"])
    last_4 = df.tail(4)["Amount"].sum()
    if len(df) >= 2:
        prior = float(df.iloc[-2]["Amount"])
        qoq = ((last_qtr_amt - prior) / prior) if prior > 0 else 0.0
    else:
        qoq = 0.0
    return {
        "gov_contracts_last_qtr_amount": round(last_qtr_amt, 2),
        "gov_contracts_4q_sum":          round(float(last_4), 2),
        "gov_contracts_qoq_growth":      round(float(qoq), 4),
    }


def compute_lobbying_signals(
    ticker: str,
    as_of: date,
    lookback_days: int = 365,
) -> dict:
    """Federal lobbying spending signals over a trailing window.

    Source: Quiver `data_prefetch/quiver/lobbying/<TICKER>.parquet`
    (Date, Amount, Client, Issue, Specific_Issue, Registrant, Ticker).

    Returns dict with optional keys:
      lobbying_amount_1y      -- sum of Amount over trailing 365 days
      lobbying_amount_q       -- amount in trailing 90 days
      lobbying_amount_yoy     -- (1y window) vs (prior 1y window) growth fraction

    Hill-Kelly-Lockhart 2014 RFS documents +0.8 pp/month alpha on heavy
    lobbiers; cumulative spend serves as the heaviness proxy here.
    """
    safe_ticker = ticker.replace(".", "-")
    path = _LOBBYING_DIR / f"{safe_ticker}.parquet"
    if not path.exists():
        return {}
    try:
        df = pd.read_parquet(path)
    except Exception:
        return {}
    if df.empty or "Date" not in df.columns or "Amount" not in df.columns:
        return {}
    try:
        df = df.copy()
        df["d"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        df = df.dropna(subset=["d"])
        df = df[df["d"] <= as_of]
    except Exception:
        return {}
    if df.empty:
        return {}
    one_yr_start = as_of - timedelta(days=lookback_days)
    prior_yr_start = as_of - timedelta(days=2 * lookback_days)
    last_q_start = as_of - timedelta(days=90)
    cur = df[df["d"] >= one_yr_start]
    prior = df[(df["d"] >= prior_yr_start) & (df["d"] < one_yr_start)]
    cur_q = df[df["d"] >= last_q_start]
    cur_sum = float(cur["Amount"].sum())
    prior_sum = float(prior["Amount"].sum())
    q_sum = float(cur_q["Amount"].sum())
    yoy = ((cur_sum - prior_sum) / prior_sum) if prior_sum > 0 else 0.0
    return {
        "lobbying_amount_1y":  round(cur_sum, 2),
        "lobbying_amount_q":   round(q_sum, 2),
        "lobbying_amount_yoy": round(yoy, 4),
    }
