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
_PATENTMOMENTUM_PATH = (
    Path(__file__).parent.parent.parent / "data_prefetch"
    / "quiver" / "patentmomentum" / "global.parquet"
)
_OFFEXCHANGE_DIR = (
    Path(__file__).parent.parent.parent / "data_prefetch"
    / "quiver" / "offexchange"
)
_CORPORATEDONORS_PATH = (
    Path(__file__).parent.parent.parent / "data_prefetch"
    / "quiver" / "corporatedonors" / "global.parquet"
)

# Module-level cache for the global parquets (patentmomentum 5.8M rows,
# corporatedonors 25K rows). Cache on first read so per-ticker producer
# calls don't re-read multi-MB files inside the screener inner loop.
# Batch 534 (2026-06-01) update: also pre-INDEX by ticker -- profile
# showed `df[df["ticker"]==tkr]` scanning 5.8M rows per call took 240ms
# (the worst per-call hotspot). Pre-grouping into a dict-of-DataFrames
# at cache-load time turns per-call lookup into O(1).
_PATENT_DF_CACHE: pd.DataFrame | None = None
_PATENT_BY_TICKER: dict[str, pd.DataFrame] | None = None
# Strong reference to the DataFrame the index was built from. Used for
# identity comparison so monkeypatched caches in tests trigger rebuild.
# (id() comparison can suffer object-reuse after GC; storing a ref to
# the DataFrame itself is reliable.)
_PATENT_INDEXED_FROM: pd.DataFrame | None = None
_DONORS_DF_CACHE: pd.DataFrame | None = None
_DONORS_BY_TICKER: dict[str, pd.DataFrame] | None = None
_DONORS_INDEXED_FROM: pd.DataFrame | None = None

# Batch 535 (2026-06-01, OPT-A producer caching sweep): per-ticker file
# caches for the remaining 4 per-ticker producers. Each first call reads
# disk; subsequent calls return cached DataFrame (zero IO). Empty
# DataFrame cached on miss so non-existent ticker files don't repeat
# Path.exists() stat per call. Memory bounded: ~1937 tickers x ~50KB
# each x 4 producers = ~388MB max -- fits 32GB c7a.4xlarge easily.
_HOUSETRADING_BY_TICKER: dict[str, pd.DataFrame] = {}
_GOV_CONTRACTS_BY_TICKER: dict[str, pd.DataFrame] = {}
_LOBBYING_BY_TICKER: dict[str, pd.DataFrame] = {}
_OFFEXCHANGE_BY_TICKER: dict[str, pd.DataFrame] = {}


def _load_ticker_parquet(
    cache: dict[str, pd.DataFrame],
    base_dir: Path,
    ticker: str,
) -> pd.DataFrame:
    """Batch 535 OPT-A: generic per-ticker file cache lookup.

    First call reads the parquet from `base_dir/<safe_ticker>.parquet`
    + caches it (empty DataFrame on miss). Subsequent calls return the
    cached DataFrame directly. Profile-driven (B534 found pre-cache
    240ms/call; post-cache 7ms/call).
    """
    safe_ticker = ticker.replace(".", "-").upper()
    cached = cache.get(safe_ticker)
    if cached is not None:
        return cached
    path = base_dir / f"{safe_ticker}.parquet"
    if not path.exists():
        # Try non-uppered variant for backward compat with existing data
        alt_path = base_dir / f"{ticker.replace('.', '-')}.parquet"
        if alt_path.exists():
            path = alt_path
        else:
            cache[safe_ticker] = pd.DataFrame()
            return cache[safe_ticker]
    try:
        df = pd.read_parquet(path)
        cache[safe_ticker] = df
        return df
    except Exception:
        cache[safe_ticker] = pd.DataFrame()
        return cache[safe_ticker]


def _load_patent_global() -> pd.DataFrame | None:
    global _PATENT_DF_CACHE
    if _PATENT_DF_CACHE is None:
        if not _PATENTMOMENTUM_PATH.exists():
            return None
        try:
            _PATENT_DF_CACHE = pd.read_parquet(_PATENTMOMENTUM_PATH)
        except Exception:
            return None
    return _PATENT_DF_CACHE


def _patent_for_ticker(ticker: str) -> pd.DataFrame | None:
    """Batch 534 (2026-06-01): O(1) per-ticker lookup against pre-indexed
    cache (vs prior O(5.8M-row scan) per call).

    Index is invalidated when the underlying `_PATENT_DF_CACHE` is
    replaced (identity change) so monkeypatching in tests works
    correctly.
    """
    global _PATENT_BY_TICKER, _PATENT_INDEXED_FROM
    df = _load_patent_global()
    if df is None:
        return None
    if _PATENT_BY_TICKER is None or _PATENT_INDEXED_FROM is not df:
        # First call OR underlying cache was replaced -- rebuild index.
        if df.empty or "ticker" not in df.columns:
            _PATENT_BY_TICKER = {}
            _PATENT_INDEXED_FROM = df
            return None
        try:
            tmp = df.copy()
            tmp["_TKR"] = tmp["ticker"].astype(str).str.upper()
            _PATENT_BY_TICKER = {
                k: v.drop(columns=["_TKR"])
                for k, v in tmp.groupby("_TKR", sort=False)
            }
            _PATENT_INDEXED_FROM = df
        except Exception:
            _PATENT_BY_TICKER = {}
            _PATENT_INDEXED_FROM = df
            return None
    return _PATENT_BY_TICKER.get(ticker.upper())


def _load_donors_global() -> pd.DataFrame | None:
    global _DONORS_DF_CACHE
    if _DONORS_DF_CACHE is None:
        if not _CORPORATEDONORS_PATH.exists():
            return None
        try:
            _DONORS_DF_CACHE = pd.read_parquet(_CORPORATEDONORS_PATH)
        except Exception:
            return None
    return _DONORS_DF_CACHE


def _donors_for_ticker(ticker: str) -> pd.DataFrame | None:
    """Batch 534 (2026-06-01): O(1) per-ticker lookup against pre-indexed
    donor cache. Invalidates index on cache identity change."""
    global _DONORS_BY_TICKER, _DONORS_INDEXED_FROM
    df = _load_donors_global()
    if df is None:
        return None
    if _DONORS_BY_TICKER is None or _DONORS_INDEXED_FROM is not df:
        if df.empty or "Ticker" not in df.columns:
            _DONORS_BY_TICKER = {}
            _DONORS_INDEXED_FROM = df
            return None
        try:
            tmp = df.copy()
            tmp["_TKR"] = tmp["Ticker"].astype(str).str.upper()
            _DONORS_BY_TICKER = {
                k: v.drop(columns=["_TKR"])
                for k, v in tmp.groupby("_TKR", sort=False)
            }
            _DONORS_INDEXED_FROM = df
        except Exception:
            _DONORS_BY_TICKER = {}
            _DONORS_INDEXED_FROM = df
            return None
    return _DONORS_BY_TICKER.get(ticker.upper())


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
    # B535 OPT-A: cached per-ticker lookup (was per-call disk read).
    df = _load_ticker_parquet(_HOUSETRADING_BY_TICKER,
                                _HOUSETRADING_DIR, ticker)
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
    # B535 OPT-A: cached per-ticker lookup.
    df = _load_ticker_parquet(_GOV_CONTRACTS_BY_TICKER,
                                _GOV_CONTRACTS_DIR, ticker)
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
    # B535 OPT-A: cached per-ticker lookup.
    df = _load_ticker_parquet(_LOBBYING_BY_TICKER,
                                _LOBBYING_DIR, ticker)
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


def compute_patentmomentum_signals(
    ticker: str,
    as_of: date,
    lookback_days: int = 90,
) -> dict:
    """Batch 528 (2026-05-31, P16 completion) -- patent-activity
    momentum signals from Quiver patentmomentum global feed.

    Source: `data_prefetch/quiver/patentmomentum/global.parquet`
    (cols: ticker, date, momentum). 5.8M rows across ~all listed
    tickers since 2010-ish.

    Returns dict with:
      patent_momentum_recent      -- latest momentum reading <= as_of
      patent_momentum_90d_avg     -- trailing 90-day mean
      patent_momentum_above_avg   -- bool: recent > 90d_avg

    Academic backing: Hirshleifer-Hsu-Li 2013 RFS -- innovation
    intensity predicts equity returns. Quiver's `momentum` is a
    derived measure (USPTO grant + citation flow) normalized per
    sector; magnitudes are relative, not dollar-denominated.
    """
    # Batch 534 (2026-06-01) perf fix: was scanning 5.8M-row global
    # DataFrame on every call (240ms/call hotspot per profile). Now O(1)
    # dict lookup against pre-indexed cache.
    sub = _patent_for_ticker(ticker)
    if sub is None or sub.empty:
        return {}
    if "date" not in sub.columns or "momentum" not in sub.columns:
        return {}
    try:
        sub = sub.copy()
        sub["d"] = pd.to_datetime(sub["date"], errors="coerce").dt.date
        sub["momentum"] = pd.to_numeric(sub["momentum"], errors="coerce")
        sub = sub.dropna(subset=["d", "momentum"])
        sub = sub[sub["d"] <= as_of].sort_values("d")
    except Exception:
        return {}
    if sub.empty:
        return {}
    recent = float(sub.iloc[-1]["momentum"])
    window_start = as_of - timedelta(days=lookback_days)
    window = sub[sub["d"] >= window_start]
    if window.empty:
        avg = recent
    else:
        avg = float(window["momentum"].mean())
    return {
        "patent_momentum_recent":     round(recent, 4),
        "patent_momentum_90d_avg":    round(avg, 4),
        "patent_momentum_above_avg":  bool(recent > avg),
    }


def compute_offexchange_signals(
    ticker: str,
    as_of: date,
    lookback_days: int = 30,
) -> dict:
    """Batch 528 (2026-05-31, P16 completion) -- off-exchange / OTC
    dark-pool activity signals.

    Source: `data_prefetch/quiver/offexchange/<TICKER>.parquet`
    (cols: Ticker, Date, OTC_Short, OTC_Total, DPI).
    OTC_Short = volume executed in dark pools that was short.
    OTC_Total = total dark-pool volume.
    DPI = Dark Pool Index (proportion of dark trading).

    Returns dict with:
      otc_short_ratio_recent     -- latest OTC_Short / OTC_Total
      otc_volume_recent          -- latest OTC_Total
      dpi_recent                 -- latest DPI value
      dpi_30d_avg                -- trailing 30-day DPI mean
      dpi_elevated               -- bool: DPI > 30d_avg

    Academic backing: Comerton-Forde-Putnins 2015 JFE -- elevated
    dark-pool activity predicts short-horizon price discovery
    distortions. High institutional dark trading often precedes
    public-market moves.
    """
    # B535 OPT-A: cached per-ticker lookup.
    df = _load_ticker_parquet(_OFFEXCHANGE_BY_TICKER,
                                _OFFEXCHANGE_DIR, ticker)
    if df.empty or "Date" not in df.columns:
        return {}
    try:
        df = df.copy()
        df["d"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
        df = df.dropna(subset=["d"])
        df = df[df["d"] <= as_of].sort_values("d")
    except Exception:
        return {}
    if df.empty:
        return {}
    last = df.iloc[-1]
    out: dict = {}
    if "OTC_Short" in df.columns and "OTC_Total" in df.columns:
        total = float(last.get("OTC_Total", 0) or 0)
        short = float(last.get("OTC_Short", 0) or 0)
        out["otc_short_ratio_recent"] = round(short / total, 4) \
            if total > 0 else 0.0
        out["otc_volume_recent"]      = round(total, 2)
    if "DPI" in df.columns:
        dpi_recent = float(last.get("DPI", 0) or 0)
        window_start = as_of - timedelta(days=lookback_days)
        window = df[df["d"] >= window_start]
        dpi_avg = float(window["DPI"].mean()) if not window.empty \
            else dpi_recent
        out["dpi_recent"]   = round(dpi_recent, 4)
        out["dpi_30d_avg"]  = round(dpi_avg, 4)
        out["dpi_elevated"] = bool(dpi_recent > dpi_avg)
    return out


def compute_corporatedonors_signals(
    ticker: str,
    as_of: date,
    lookback_days: int = 365,
) -> dict:
    """Batch 528 (2026-05-31, P16 completion) -- corporate PAC
    donation signals from Quiver corporatedonors global feed.

    Source: `data_prefetch/quiver/corporatedonors/global.parquet`
    (cols: BioGuideID, CandidateName, CompanyCMTENM,
    TransactionDate, TransactionAmount, Ticker, CommitteeName, Cycle).

    Returns dict with:
      corp_donations_1y           -- sum of TransactionAmount over 365d
      corp_donations_count_1y     -- count of donations over 365d
      corp_donations_unique_pacs  -- distinct CommitteeName count

    Academic backing: Akey 2015 RFS -- companies that contribute to
    eventual winners realize regulatory-favorable outcomes. Donation
    volume is a noisy proxy for political-favor exposure; combine
    with lobbying for higher SNR.
    """
    # Batch 534 (2026-06-01) perf fix: O(1) dict lookup vs prior O(N)
    # row scan.
    sub = _donors_for_ticker(ticker)
    if sub is None or sub.empty:
        return {}
    if "TransactionDate" not in sub.columns \
            or "TransactionAmount" not in sub.columns:
        return {}
    try:
        sub = sub.copy()
        sub["d"] = pd.to_datetime(sub["TransactionDate"],
                                    errors="coerce").dt.date
        sub["amt"] = pd.to_numeric(sub["TransactionAmount"],
                                     errors="coerce").fillna(0)
        sub = sub.dropna(subset=["d"])
        window_start = as_of - timedelta(days=lookback_days)
        sub = sub[(sub["d"] <= as_of) & (sub["d"] >= window_start)]
    except Exception:
        return {}
    if sub.empty:
        return {}
    out: dict = {
        "corp_donations_1y":       round(float(sub["amt"].sum()), 2),
        "corp_donations_count_1y": int(len(sub)),
    }
    if "CommitteeName" in sub.columns:
        out["corp_donations_unique_pacs"] = int(sub["CommitteeName"].nunique())
    return out
