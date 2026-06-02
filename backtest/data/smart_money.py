"""
data/smart_money.py  -  Smart money + analyst consensus data.

Sources (Pass 53 DEC-497 NO-LIVE-API + DEC-503 second test pyramid application
2026-05-05; D4 owner-approved yfinance total cut runtime):
  - Quiver Quantitative paid (Trader tier per DEC-450):
      * congressional  -  historical/congresstrading/{ticker} (per-ticker, works in tier)
      * insider  -  live/insidertrading bulk feed (BUG-272 fix; historical/insidertrading 404s)
      * 13F  -  live/sec13f bulk feed (BUG-273 fix; historical/institutionalholdings 404s)
      * lobbying / govcontracts  -  per-ticker (works)
  - Polygon Stocks Starter (DEC-441/444):
      * EPS estimates / financials -> data_prefetch/polygon/financials/<TICKER>.parquet
        (Sprint 0A Batch 4 populates; pre-Batch-4 returns "not_available")
  - SEC EDGAR via edgartools (DEC-456 + R1 owner-approved Pass 53):
      * Form 4 (insider direct), 8-K (material events), 13D/G (5%+ activists)
      * Sprint 0A Batch 11 prefetches; reads from data_prefetch/sec_edgar/...
  - News sentiment: legacy AV+Finnhub paths retained until Batch 13 migration
    to data_prefetch/polygon/news/.

All functions enforce point-in-time data (as_of parameter).
NO LIVE API CALLS in Stage 2 backtest (DEC-497 HARD CUT, owner-approved 2026-05-05;
fully implemented Sprint 0A.8 Pass 53 v8h+1 2026-05-10). Runtime backtest reads from
data_prefetch/quiver/ exclusively. Live Quiver API calls live exclusively in
scripts/prefetch_quiver*.py.
yfinance: REMOVED runtime per DEC-497 + D4 owner-approved 2026-05-05.
requests: REMOVED runtime per DEC-497 + Sprint 0A.8 (Pass 53 v8h+1 2026-05-10).
"""

import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Pre-fetch cache directory - populated by scripts/prefetch_quiver*.py.
# Pass 53 H5 fix 2026-05-06: migrated from backtest/data/cache/quiver/ to
# data_prefetch/quiver/ per Sprint 0A.8 + DEC-497 NO-LIVE-API HARD CUT.
PREFETCH_DIR = Path(__file__).parent.parent.parent / "data_prefetch" / "quiver"

# Module-level bulk-feed cache (loaded once per process; thread-safe via GIL)
# BUG-272/273 Pass 53 fix: Quiver Trader tier exposes Live <dataset> as paginated
# bulk feeds (no per-ticker endpoint), so cache is single global.parquet per dataset
# and we filter by Ticker column at read time.
_BULK_CACHE: dict[str, Optional[pd.DataFrame]] = {}


# Batch 535 OPT-A Phase 5: per-(dataset, ticker) prefetch cache.
# Profile showed congressional_signal + insider_signal calling
# _load_prefetch -> pd.read_parquet on every call. Cache eliminates
# repeat disk reads. Bounded memory: 1937 tickers x ~10 datasets x
# ~10KB each = ~190MB max.
_PREFETCH_CACHE: dict[tuple[str, str], Optional[pd.DataFrame]] = {}


def _load_prefetch(dataset: str, ticker: str) -> Optional[pd.DataFrame]:
    """Load pre-fetched Quiver data from Parquet cache. Returns None if not cached.

    Per-ticker pattern. Used for endpoints with per-ticker variants
    (congresstrading, lobbying, govcontracts, offexchange, topshareholders, etc.).

    Batch 535 OPT-A Phase 5: in-memory cache keyed by (dataset, ticker).
    First call reads disk; subsequent calls return cached DataFrame.
    """
    cache_key = (dataset, ticker.replace('-', '_'))
    if cache_key in _PREFETCH_CACHE:
        return _PREFETCH_CACHE[cache_key]
    path = PREFETCH_DIR / dataset / f"{ticker.replace('-','_')}.parquet"
    if not path.exists():
        _PREFETCH_CACHE[cache_key] = None
        return None
    try:
        df = pd.read_parquet(path)
        result = df if not df.empty else pd.DataFrame()
        _PREFETCH_CACHE[cache_key] = result
        return result
    except Exception as exc:
        logger.debug("prefetch load %s/%s: %s", dataset, ticker, exc)
        _PREFETCH_CACHE[cache_key] = None
        return None


def _load_quiver_bulk(dataset: str) -> pd.DataFrame:
    """Load Quiver bulk-feed parquet from cache/quiver/<dataset>/global.parquet.

    BUG-272/273 Pass 53 (DEC-503 second test pyramid application):
    Migration from per-ticker live API calls to bulk-feed cache reads.

    Quiver Trader-tier exposes these as paginated bulk feeds without per-ticker
    endpoints  -  Sprint 0A.5 prefetch (Batch 10) populates the bulk parquet;
    runtime reads filter the bulk DataFrame by `Ticker` column.

    Returns empty DataFrame if file missing (graceful degradation pre-prefetch).
    Cached per-process via _BULK_CACHE module global.

    Used by insider_signal (`live/insidertrading`) + institutional_signal
    (`live/sec13f`) per BUG-272/BUG-273 silent-gap fix.
    """
    if dataset in _BULK_CACHE:
        cached = _BULK_CACHE[dataset]
        return cached if cached is not None else pd.DataFrame()
    path = PREFETCH_DIR / dataset / "global.parquet"
    if not path.exists():
        logger.debug(
            "Quiver bulk feed not yet prefetched (Sprint 0A.5/Batch 10 will populate): %s", path
        )
        _BULK_CACHE[dataset] = None
        return pd.DataFrame()
    try:
        df = pd.read_parquet(path)
        _BULK_CACHE[dataset] = df
        logger.info("Loaded Quiver bulk feed %s: %d rows", dataset, len(df))
        return df
    except Exception as exc:
        logger.warning("Quiver bulk feed load failed for %s: %s", dataset, exc)
        _BULK_CACHE[dataset] = None
        return pd.DataFrame()


# Batch 535 OPT-A Phase 4: pre-index bulk DataFrames by ticker so
# `_filter_bulk_by_ticker` is O(1) dict lookup (vs O(N-row scan) per
# call). Profile showed _filter_bulk_by_ticker = 159s / 4326 calls =
# 37ms/call doing full-table scans. Insider trading + 13F bulk feeds
# can be 100K+ rows each.
# Structure: {dataset_name: (cached_df_ref, {ticker_upper: filtered_df})}
_BULK_INDEX: dict[str, tuple[pd.DataFrame, dict[str, pd.DataFrame]]] = {}


def _filter_bulk_by_ticker(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Filter a Quiver bulk DataFrame by Ticker column (case-insensitive).

    Batch 535 OPT-A Phase 4: pre-indexes by ticker on first call against
    a given df. Subsequent calls with same df return O(1) dict lookup.
    Cache invalidation: identity-check (`is`) on df vs cached df --
    different DataFrame triggers rebuild.
    """
    if df.empty or "Ticker" not in df.columns:
        return df
    # Use id() of df as the dataset key (DataFrames don't have a stable
    # name attribute; identity is the natural cache key here).
    # Note: if the global _BULK_CACHE replaces df with a new object,
    # the id may change and we'll rebuild -- which is what we want.
    df_id = id(df)
    key = f"__id_{df_id}"
    cached_pair = _BULK_INDEX.get(key)
    if cached_pair is None or cached_pair[0] is not df:
        # First call OR df changed -- build the index
        try:
            tmp = df.copy()
            tmp["_TKR"] = tmp["Ticker"].astype(str).str.upper()
            by_tkr = {
                k: v.drop(columns=["_TKR"]).copy()
                for k, v in tmp.groupby("_TKR", sort=False)
            }
            _BULK_INDEX[key] = (df, by_tkr)
        except Exception:
            return df[df["Ticker"].astype(str).str.upper() == ticker.upper()].copy()
    by_tkr = _BULK_INDEX[key][1]
    return by_tkr.get(ticker.upper(), df.iloc[0:0].copy())


def _reset_bulk_cache_for_tests():
    """Test-only helper: reset module-level bulk cache so tests don't leak state."""
    _BULK_CACHE.clear()


def _get_quiver_data(dataset: str, endpoint_path: str, ticker: str) -> Optional[list]:
    """
    Load Quiver data from prefetch cache only (NO LIVE API per DEC-497 HARD CUT).

    Pass 53 Sprint 0A.8 NO-LIVE-API enforcement (Pass 53 v8h+1 2026-05-10):
    Cache miss returns empty list. Run scripts/prefetch_quiver*.py to populate
    data_prefetch/quiver/{dataset}/{ticker}.parquet before backtest.

    The endpoint_path arg is retained for caller-API compatibility but is no
    longer used at runtime - it identifies which prefetch script populates
    the cache.
    """
    cached = _load_prefetch(dataset, ticker)
    if cached is not None:
        logger.debug("Prefetch cache hit: %s/%s (%d rows)", dataset, ticker, len(cached))
        return cached.to_dict("records") if not cached.empty else []
    # Cache miss - return empty (NO live API per DEC-497 HARD CUT).
    logger.debug(
        "Prefetch cache miss: %s/%s - returning empty (run prefetch_quiver*.py)",
        dataset, ticker,
    )
    return []


# -----------------------------------------------------------------------------
# ANALYST CONSENSUS
# BUG-271 Pass 53 (DEC-503 second test pyramid application):
#   REMOVED Quiver `historical/analystestimates` branch  -  endpoint NOT in Trader
#   tier per Pass 53 dashboard inventory + smoke test 2026-05-05 (404).
#   REMOVED yfinance branches per DEC-497 NO-LIVE-API HARD CUT (D4 owner approval
#   2026-05-05).
#   Function now reads from data_prefetch/polygon/financials/{ticker}.parquet
#   (populated by Sprint 0A Batch 4). Pre-Batch-4: returns "not_available"
#   gracefully. Polygon Stocks Starter financials endpoint covers EPS estimates
#   only  -  analyst consensus + recommendation count + price target fields will
#   remain "not_available" until/unless an analyst-consensus subscription is
#   added in Phase 1B/1C (FMP per DEC-461 candidate).
# -----------------------------------------------------------------------------

# data_prefetch root for NO-LIVE-API reads (DEC-497)
_REPO_ROOT = Path(__file__).parent.parent.parent
PREFETCH_POLYGON_FINANCIALS_DIR = _REPO_ROOT / "data_prefetch" / "polygon" / "financials"


def get_analyst_data(ticker: str, as_of: date) -> dict:
    """
    Fetch analyst consensus, price targets, EPS estimates, and recent revisions
    from data_prefetch/polygon/financials/ (populated by Sprint 0A Batch 4).

    Returns dict with default `signal="not_available"` if cache miss (graceful
    pre-prefetch state). When Batch 4 populates cache, EPS estimates fields
    populated; analyst-consensus fields (buy/hold/sell counts, price targets)
    remain "not_available" until FMP/equivalent subscribed (DEC-461 candidate).

    BUG-271 + DEC-497 + D4 owner-approved Pass 53: NO yfinance + NO Quiver
    historical/analystestimates (both removed; endpoint 404 / yfinance-cut).

    Returns dict with:
      consensus, buy_count, hold_count, sell_count, total_analysts, buy_pct,
      target_mean, target_high, target_low, target_upside_pct,
      eps_estimate_next_q, eps_estimate_next_y, recent_upgrades,
      recent_downgrades, revision_direction, signal.
    """
    result = {
        "consensus": "unknown", "buy_count": 0, "hold_count": 0,
        "sell_count": 0, "total_analysts": 0, "buy_pct": 0.0,
        "target_mean": None, "target_high": None, "target_low": None,
        "target_upside_pct": None, "eps_estimate_next_q": None,
        "eps_estimate_next_y": None, "recent_upgrades": 0,
        "recent_downgrades": 0, "revision_direction": "flat",
        "signal": "not_available",
    }
    safe_ticker = ticker.replace("-", "_").replace(".", "_")
    path = PREFETCH_POLYGON_FINANCIALS_DIR / f"{safe_ticker}.parquet"
    if not path.exists():
        # Pre-Batch-4 graceful state  -  no Polygon financials prefetch yet.
        # signal="not_available" surfaces as no-input to agents (Fundamental Agent
        # treats as missing data, doesn't fall back to stale yfinance per DEC-497).
        return result

    try:
        df = pd.read_parquet(path)
        if df.empty:
            return result
        # Schema TBD post-Batch-4. Polygon /vX/reference/financials returns
        # standardized GAAP statements; EPS estimates are NOT included (those
        # come from analyst consensus providers). Filter PIT by filing_date <= as_of.
        if "filing_date" in df.columns:
            df["filing_date"] = pd.to_datetime(df["filing_date"]).dt.date
            df = df[df["filing_date"] <= as_of]
        if df.empty:
            return result
        # Per-filing fundamentals available  -  defer field-level extraction to
        # Batch 13 NO-LIVE-API refactor when full schema is locked. For Batch 1
        # signal value: presence of any post-PIT row -> "available_unparsed",
        # consumed by Fundamental Agent as raw context (no derived signal).
        result["signal"] = "available_unparsed"
        return result
    except Exception as exc:
        logger.debug("get_analyst_data(%s): %s", ticker, exc)
        return result


def analyst_bullets(analyst: dict, current_price: Optional[float] = None) -> list:
    """
    Generate bullet points for the site card analyst section.
    Returns list of plain-English strings.
    """
    bullets = []
    n     = analyst.get("total_analysts", 0)
    cons  = analyst.get("consensus", "Unknown")
    b_pct = analyst.get("buy_pct", 0)
    b_cnt = analyst.get("buy_count", 0)
    h_cnt = analyst.get("hold_count", 0)
    s_cnt = analyst.get("sell_count", 0)

    if n > 0:
        bullets.append(
            f"Analyst consensus: {cons}  -  {b_cnt} Buy / {h_cnt} Hold / {s_cnt} Sell "
            f"({n} analysts covering)"
        )

    tgt = analyst.get("target_mean")
    upside = analyst.get("target_upside_pct")
    if tgt:
        upside_str = f"  -  {upside:+.1f}% from current" if upside is not None else ""
        bullets.append(f"Average price target: ${tgt:.2f}{upside_str}")

    tgt_h = analyst.get("target_high")
    tgt_l = analyst.get("target_low")
    if tgt_h and tgt_l:
        bullets.append(f"Target range: ${tgt_l:.2f} - ${tgt_h:.2f}")

    eps_q = analyst.get("eps_estimate_next_q")
    if eps_q is not None:
        bullets.append(f"EPS estimate next quarter: ${eps_q:.2f} (consensus)")

    ups   = analyst.get("recent_upgrades", 0)
    downs = analyst.get("recent_downgrades", 0)
    rev   = analyst.get("revision_direction", "flat")
    if ups > 0 or downs > 0:
        if rev == "up":
            bullets.append(
                f"{ups} upgrade{'s' if ups != 1 else ''} in last 30 days  -  "
                f"positive estimate momentum"
            )
        elif rev == "down":
            bullets.append(
                f"WARNING:  {downs} downgrade{'s' if downs != 1 else ''} in last 30 days  -  "
                f"negative estimate momentum"
            )
        else:
            bullets.append(f"Mixed revisions: {ups} up / {downs} down in last 30 days")

    if not bullets:
        bullets.append("Analyst data unavailable for this instrument")

    return bullets


# -----------------------------------------------------------------------------
# CONGRESSIONAL TRADES
# -----------------------------------------------------------------------------

# Batch 548 OPT-C: pre-processed congressional cache. _load_prefetch already
# caches the raw DataFrame; this layer additionally pre-converts disclosure_date
# / transaction_date columns ONCE per ticker (was per-call). Source-DataFrame
# identity check (`is`) handles cache invalidation. The as_of-dependent
# filtering still happens per call (cheap pandas boolean indexing).
_CONGRESS_PROCESSED_CACHE: dict[str, tuple] = {}


def _load_congressional_processed(ticker: str) -> Optional[pd.DataFrame]:
    """Return cached DataFrame with disclosure_date + transaction_date
    columns pre-computed as datetime64. Returns None when no data."""
    raw = _load_prefetch("congressional", ticker)
    if raw is None or raw.empty:
        return None
    cached = _CONGRESS_PROCESSED_CACHE.get(ticker)
    if cached is not None and cached[0] is raw:
        return cached[1]
    df = raw.copy()
    # ReportDate / Date / date fallback chain
    if "ReportDate" in df.columns:
        disc_src = df["ReportDate"]
    elif "Date" in df.columns:
        disc_src = df["Date"]
    elif "date" in df.columns:
        disc_src = df["date"]
    else:
        disc_src = pd.Series([""] * len(df), index=df.index)
    df["disclosure_dt"] = pd.to_datetime(disc_src, errors="coerce")
    if "TransactionDate" in df.columns:
        df["transaction_dt"] = pd.to_datetime(df["TransactionDate"], errors="coerce")
    elif "transactionDate" in df.columns:
        df["transaction_dt"] = pd.to_datetime(df["transactionDate"], errors="coerce")
    else:
        df["transaction_dt"] = df["disclosure_dt"]
    df = df.dropna(subset=["disclosure_dt"])
    _CONGRESS_PROCESSED_CACHE[ticker] = (raw, df)
    return df


# Batch 549 OPT-C: pre-processed institutional 13F cache. Mirrors B548
# congressional pattern. Raw cache lives in _PREFETCH_CACHE under key
# ("institutional_perticker", ticker); this layer adds report_period (date),
# report_period_ts (datetime64), available_after_ts (datetime64 + 45 days),
# Shares_num (numeric coerced) -- all ONCE per ticker. Source-identity
# invalidation.
_INSTITUTIONAL_PROCESSED_CACHE: dict[str, tuple] = {}


def _load_institutional_processed(ticker: str) -> Optional[pd.DataFrame]:
    """Return cached institutional 13F DataFrame with report_period_ts +
    available_after_ts + Shares_num pre-computed. None when no data."""
    cache_key = ("institutional_perticker", ticker)
    raw = _PREFETCH_CACHE.get(cache_key)
    if raw is None and cache_key not in _PREFETCH_CACHE:
        path = PREFETCH_DIR / "institutional" / f"{ticker}.parquet"
        if not path.exists():
            _PREFETCH_CACHE[cache_key] = None
            return None
        try:
            raw = pd.read_parquet(path)
            _PREFETCH_CACHE[cache_key] = raw
        except Exception:
            _PREFETCH_CACHE[cache_key] = None
            return None
    if raw is None or raw.empty:
        return None
    if not {"ReportPeriod", "Fund", "Shares"}.issubset(raw.columns):
        return None
    cached = _INSTITUTIONAL_PROCESSED_CACHE.get(ticker)
    if cached is not None and cached[0] is raw:
        return cached[1]
    df = raw.copy()
    df["report_period_ts"] = pd.to_datetime(df["ReportPeriod"], errors="coerce")
    df = df.dropna(subset=["report_period_ts"])
    if df.empty:
        _INSTITUTIONAL_PROCESSED_CACHE[ticker] = (raw, df)
        return df
    df["report_period"] = df["report_period_ts"].dt.date
    # Batch 549 OPT-C: vectorized timedelta add (was per-row Python lambda)
    df["available_after_ts"] = df["report_period_ts"] + pd.Timedelta(days=45)
    df["Shares_num"] = pd.to_numeric(df["Shares"], errors="coerce").fillna(0)
    _INSTITUTIONAL_PROCESSED_CACHE[ticker] = (raw, df)
    return df


def congressional_signal(ticker: str, as_of: date, lookback_days: int = 45) -> dict:
    df = _load_congressional_processed(ticker)
    if df is None or df.empty:
        return {"signal": "none", "buy_count": 0, "sell_count": 0}
    try:
        # DEC-324 fix (Pass 51) BUG-240: use BOTH disclosure_date (PIT availability)
        # AND transaction_date (age-weighting). STOCK Act gives members up
        # to 45 days to disclose; a trade DISCLOSED 5 days ago might have
        # been TRANSACTED 40 days ago. Smart-money signal value comes from
        # when they ACTUALLY POSITIONED, not when paperwork landed.
        # Previously age-weighted by disclosure date, mis-weighting late filings.
        # Batch 548 OPT-C: disclosure_dt + transaction_dt are pre-converted at
        # cache load; per-call work is only the as_of-dependent filters.
        as_of_ts = pd.Timestamp(as_of)
        window_start_ts = pd.Timestamp(as_of - timedelta(days=lookback_days))

        # PIT filter: only trades where DISCLOSURE was on/before as_of are visible
        df = df[df["disclosure_dt"] <= as_of_ts]

        # Age-weight by TRANSACTION date (when they actually traded)
        recent_mask = df["transaction_dt"] >= window_start_ts
        recent = df[recent_mask].copy()
        if recent.empty:
            return {"signal": "none", "buy_count": 0, "sell_count": 0,
                    "senate_buys": 0, "cluster_buy": False}
        # Age-weight: <30 days = full, 30-60 days = 0.5x, >60 days = excluded
        age_days_arr = (as_of_ts - recent["transaction_dt"]).dt.days.to_numpy()
        # Batch 548 OPT-C: np.where replaces per-element Python lambda
        weight_arr = np.where(
            age_days_arr < 30, 1.0,
            np.where(age_days_arr < 60, 0.5, 0.0),
        )
        recent["age_days"] = age_days_arr
        recent["weight"] = weight_arr
        recent = recent[recent["weight"] > 0]  # exclude >60 days

        buys   = recent[recent.get("Transaction","transaction").str.contains(
            "Purchase|Buy", case=False, na=False)]
        sells  = recent[recent.get("Transaction","transaction").str.contains(
            "Sale|Sell", case=False, na=False)]
        # BUG-273 fix 2026-05-13: actual Quiver column is "House" (values:
        # "Senate"/"Representatives"), not "Chamber". Using df.get("Chamber",...)
        # returned the string "chamber" (no column found) -> AttributeError on
        # .str.lower() -> silent exception -> always returned signal="none".
        house_col = "House" if "House" in buys.columns else "Chamber"
        senate_buys = (
            buys[buys[house_col].str.lower() == "senate"]
            if not buys.empty and house_col in buys.columns
            else buys.iloc[0:0]
        )
        cluster_buy  = buys["Representative"].nunique() >= 3 if not buys.empty else False
        signal = "none"
        if len(sells) > len(buys) and len(sells) >= 2:
            signal = "sell"
        elif len(senate_buys) >= 2 or cluster_buy:
            signal = "strong_buy"
        elif len(buys) >= 1:
            signal = "buy"
        return {"signal": signal, "buy_count": len(buys), "sell_count": len(sells),
                "senate_buys": len(senate_buys), "cluster_buy": cluster_buy}
    except Exception as exc:
        logger.debug("congressional_signal(%s): %s", ticker, exc)
        return {"signal": "none", "buy_count": 0, "sell_count": 0}


# -----------------------------------------------------------------------------
# INSIDER TRADES
# -----------------------------------------------------------------------------

def insider_signal(ticker: str, as_of: date, lookback_days: int = 30) -> dict:
    """Insider trading signal from Quiver `live/insiders` bulk feed.

    BUG-270 Pass 53 v8h+1 cross-reference (RESOLVED-IMPLEMENTED 2026-05-10):
    "insider_signal() column-name mismatch (100% silent failure)" was subsumed
    by the BUG-272 schema migration below. Rewriting the function to consume
    the live/insiders bulk feed (NOT the legacy insidertrading endpoint) fixed
    the column-name mismatch as a side effect of schema alignment. No
    independent BUG-270 fix needed; promotion verified via this docstring tag
    so dashboard wired-check can find the cross-reference.

    BUG-272 Pass 53 fix RESOLVED-IMPLEMENTED 2026-05-06 (Batch 13 schema alignment):
    Path: `cache/quiver/insiders/global.parquet` (NOT `insidertrading/`  -  actual
    Quiver Trader-tier endpoint is `live/insiders` per Pass 53 v2 smoke probe).

    Schema (per Quiver live/insiders):
      Ticker / Date / Name / AcquiredDisposedCode ('A' acquired, 'D' disposed)
      / TransactionCode ('P' open-mkt purchase, 'S' open-mkt sale, 'A' grant,
        'F' tax withhold, 'M' option exercise, 'J' other, 'G' gift, 'C' conversion,
        'L' small acquisition exempt) / Shares / PricePerShare / officerTitle /
      isDirector / isOfficer / isTenPercentOwner

    Signal logic:
      - Bullish: TransactionCode 'P' (open-market purchase, real money) or 'L'
        (small acquisition); CEO/officer purchases weighted higher
      - Bearish: TransactionCode 'S' (open-market sale)
      - Excluded as noise: 'A' (grant), 'F' (tax), 'M' (option exercise alone),
        'G' (gift), 'C' (conversion), 'J' (other; varies)

    Returns dict per existing schema for backward compatibility.
    """
    bulk = _load_quiver_bulk("insiders")
    df = _filter_bulk_by_ticker(bulk, ticker)
    if df.empty:
        return {"signal": "none", "buy_count": 0, "sell_count": 0}
    try:
        df = df.copy()
        # Pass 53 Day-9 v8f DEC-512 fix (BUG-INSIDER-PIT): use fileDate (SEC
        # filing date) for PIT cutoff, NOT Date (transaction date). Pre-fix
        # used Date which gave ~6-day lookahead  -  public didn't know about
        # the transaction until the SEC Form 4 was filed. Fall back to Date
        # only when fileDate is absent (defensive; should not happen with
        # current Quiver schema).
        if "fileDate" in df.columns:
            df["filing_date"] = pd.to_datetime(df["fileDate"], errors="coerce").dt.date
            # Drop rows where fileDate is unparseable rather than silently
            # falling back to Date (which would re-introduce the lookahead)
            df = df[df["filing_date"].notna()]
        else:
            df["filing_date"] = pd.to_datetime(df["Date"]).dt.date
        df = df[df["filing_date"] <= as_of]
        # Window
        window_start = as_of - timedelta(days=lookback_days)
        recent = df[df["filing_date"] >= window_start].copy()
        # Filter to meaningful transactions:
        # buys: TransactionCode in ('P', 'L')  -  open-market purchase (real money)
        # sells: TransactionCode == 'S'  -  open-market sale
        buy_codes = ("P", "L")
        sell_codes = ("S",)
        buys = recent[recent["TransactionCode"].isin(buy_codes)]
        sells = recent[recent["TransactionCode"].isin(sell_codes)]
        # CEO buy detection: officerTitle contains CEO/Chief Executive AND isOfficer
        if not buys.empty and "officerTitle" in buys.columns:
            ceo_titles = buys["officerTitle"].fillna("").astype(str)
            ceo_buy = bool(ceo_titles.str.contains(
                "CEO|Chief Executive", case=False, na=False).any())
            # Batch 469 (P14): CFO regex -- missing from prior signal.
            cfo_buy = bool(ceo_titles.str.contains(
                "CFO|Chief Financial", case=False, na=False).any())
        else:
            ceo_buy = False
            cfo_buy = False
        # Batch 469 (P14): director-only buy -- isDirector=True AND
        # isOfficer=False (Cohen-Malloy-Pomorski 2012 shows director-only
        # purchases are a distinct signal class from C-suite purchases).
        director_only_buy = False
        if (not buys.empty and "isDirector" in buys.columns
                and "isOfficer" in buys.columns):
            d = buys["isDirector"].fillna(False).astype(bool)
            o = buys["isOfficer"].fillna(False).astype(bool)
            director_only_buy = bool((d & ~o).any())
        # Batch 469 (P14): large-dollar-buy -- PricePerShare * Shares > $1M.
        # Captures conviction independent of role; complements CEO/CFO regex.
        large_dollar_buy = False
        if (not buys.empty and "PricePerShare" in buys.columns
                and "Shares" in buys.columns):
            pps = pd.to_numeric(buys["PricePerShare"], errors="coerce").fillna(0)
            shrs = pd.to_numeric(buys["Shares"], errors="coerce").fillna(0)
            dollars = (pps * shrs).abs()
            large_dollar_buy = bool((dollars > 1_000_000).any())
        # Batch 469 (P14): concentrated-sell -- sold-fraction
        # Shares / SharesOwnedFollowing > 50%. Captures liquidation events
        # vs. routine diversification trims.
        concentrated_sell = False
        if (not sells.empty and "Shares" in sells.columns
                and "SharesOwnedFollowing" in sells.columns):
            sold_s = pd.to_numeric(sells["Shares"], errors="coerce").fillna(0).abs()
            holding = pd.to_numeric(
                sells["SharesOwnedFollowing"], errors="coerce").fillna(0).abs()
            # Total holdings BEFORE the sale = remaining + sold.
            total_before = holding + sold_s
            with np.errstate(divide="ignore", invalid="ignore"):
                frac = sold_s.where(total_before > 0, 0) / total_before.where(
                    total_before > 0, 1)
            concentrated_sell = bool((frac > 0.50).any())
        # Cluster buy: 3+ unique insider names purchasing
        cluster_buy = buys["Name"].nunique() >= 3 if not buys.empty else False
        # Cluster sell: 3+ unique insider names selling
        cluster_sell = sells["Name"].nunique() >= 3 if not sells.empty else False
        # Composite signal
        signal = "none"
        if cluster_sell or concentrated_sell:
            signal = "cluster_sell" if cluster_sell else "concentrated_sell"
        elif ceo_buy and cluster_buy:
            signal = "strong_buy"
        elif ceo_buy or cfo_buy or large_dollar_buy or cluster_buy:
            signal = "buy"
        elif director_only_buy or len(buys) >= 1:
            signal = "weak_buy"
        return {
            "signal":             signal,
            "buy_count":          len(buys),
            "sell_count":         len(sells),
            "ceo_buy":            ceo_buy,
            "cfo_buy":            cfo_buy,
            "director_only_buy":  director_only_buy,
            "large_dollar_buy":   large_dollar_buy,
            "concentrated_sell":  concentrated_sell,
            "cluster_buy":        cluster_buy,
        }
    except Exception as exc:
        logger.debug("insider_signal(%s): %s", ticker, exc)
        return {"signal": "none", "buy_count": 0, "sell_count": 0}


# -----------------------------------------------------------------------------
# INSTITUTIONAL (13F)
# -----------------------------------------------------------------------------

def get_institutional_positions(ticker: str, as_of: date):
    """DEC-325 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 57 2026-05-11
    (owner-approved Path C 5-DEC bundle). PIT-correct institutional 13F
    lookup per Pass 52 spec: filter by actual `filing_date` from SEC
    when available (NOT the universal-on-time assumption of
    `quarter_end + 45 <= D` used in institutional_signal for legacy
    compat).

    Late filers (some big funds file 60-90 days after quarter end)
    become VISIBLE under filing_date filter — the universal-on-time
    assumption silently dropped them per DEC-325 / CAV-046.

    Falls back to ReportPeriod + 45 estimate when no filing_date column
    exists in the source data (sec13fchanges currently has only
    ReportPeriod; sec13f raw has fileDate). Caller-side decides whether
    fallback is acceptable.

    Inputs:
      ticker: ticker symbol
      as_of: PIT date

    Returns DataFrame (possibly empty) of institutional positions
    visible at as_of. Each row preserves the source columns
    (Fund, Change_Share, Change_Pct, Held, etc.).

    Joint with BUG-241 (late-filer visibility) + BUG-186 (PIT
    correctness) + DEC-396 sub-decision.
    """
    bulk = _load_quiver_bulk("sec13fchanges")
    df = _filter_bulk_by_ticker(bulk, ticker)
    if df is None or df.empty:
        return df
    df = df.copy()
    # Prefer actual filing_date when present
    if "filing_date" in df.columns:
        df["filing_date"] = pd.to_datetime(df["filing_date"], errors="coerce").dt.date
        return df[df["filing_date"].notna() & (df["filing_date"] <= as_of)]
    if "fileDate" in df.columns:
        df["filing_date"] = pd.to_datetime(df["fileDate"], errors="coerce").dt.date
        return df[df["filing_date"].notna() & (df["filing_date"] <= as_of)]
    # Fallback: ReportPeriod + 45 days (legacy assumption; caller warned)
    if "ReportPeriod" in df.columns:
        df["report_period"] = pd.to_datetime(df["ReportPeriod"], errors="coerce").dt.date
        df["available_after"] = df["report_period"].apply(
            lambda d: d + timedelta(days=45) if d else None)
        return df[df["available_after"].notna()
                  & (df["available_after"] <= as_of)]
    return df.iloc[0:0]  # no date column -> empty


def _institutional_signal_from_bulk(ticker: str, as_of: date) -> dict:
    """Bulk-feed signal source (recent ~12 months of precomputed deltas).
    Returns {"signal": "none"} when bulk doesn't cover the date.
    See institutional_signal() for full semantics."""
    bulk = _load_quiver_bulk("sec13fchanges")
    df = _filter_bulk_by_ticker(bulk, ticker)
    if df.empty:
        return {"signal": "none"}
    try:
        df = df.copy()
        df["report_period"] = pd.to_datetime(df["ReportPeriod"]).dt.date
        df["available_after"] = df["report_period"].apply(
            lambda d: d + timedelta(days=45) if d else None)
        df = df[df["available_after"] <= as_of]
        if df.empty:
            return {"signal": "none"}
        latest_q = df["report_period"].max()
        latest = df[df["report_period"] == latest_q].copy()
        latest["Change_Share"] = pd.to_numeric(
            latest.get("Change_Share", 0), errors="coerce").fillna(0)
        latest["Change_Pct"] = pd.to_numeric(
            latest.get("Change_Pct", 0), errors="coerce").fillna(0)
        new_pos = int((latest["Change_Pct"] == 1.0).sum())
        increased = int(((latest["Change_Share"] > 0) &
                          (latest["Change_Pct"] < 1.0)).sum())
        decreased = int((latest["Change_Share"] < 0).sum())
        signal = "none"
        if new_pos >= 3 or (new_pos >= 1 and increased >= 2):
            signal = "strong_buy"
        elif new_pos >= 1 or increased >= 2:
            signal = "buy"
        elif decreased > increased:
            signal = "negative"
        return {"signal": signal, "new_positions": new_pos,
                "increased": increased, "decreased": decreased,
                "source": "bulk"}
    except Exception as exc:
        logger.debug("_institutional_signal_from_bulk(%s): %s", ticker, exc)
        return {"signal": "none"}


def _institutional_signal_from_perticker_history(
    ticker: str, as_of: date,
) -> dict:
    """Batch 294 (2026-05-21 owner-approved F1): compute institutional_signal
    from per-ticker historical sec13f data when bulk doesn't cover as_of.
    Bulk feed (live/sec13fchanges) only has ~12 months recent data; this
    fallback uses data_prefetch/quiver/institutional/{TICKER}.parquet which
    has 18+ years of history (2006-2025).

    Computes the SAME deltas (new_position / increased / decreased) that the
    bulk feed precomputes, by diffing per-fund holdings across consecutive
    quarters. Same signal classification thresholds. PIT correctness via
    ReportPeriod + 45 days (DEC-325 fallback rule).

    Per-ticker schema: Date, ReportPeriod, Name, Ticker, Fund, Class, Value,
                       Shares, SH/PRN, Put/Call, Direction
    """
    # Batch 535 OPT-A Phase 5: cached per-ticker institutional history.
    # Was reading parquet on every call (2485 calls / 73s / 29ms each).
    # Batch 549 OPT-C: in-memory pre-processed cache stores DataFrame with
    # report_period_ts + available_after_ts + Shares_num pre-computed at
    # fill time. Per-call work reduces to as_of filter + groupby. Identity
    # check on raw cached source for invalidation.
    df = _load_institutional_processed(ticker)
    if df is None or df.empty:
        return {"signal": "none"}
    try:
        as_of_ts = pd.Timestamp(as_of)
        df = df[df["available_after_ts"] <= as_of_ts]
        if df.empty:
            return {"signal": "none"}
        quarters = sorted(df["report_period"].unique())
        if len(quarters) < 1:
            return {"signal": "none"}
        latest_q = quarters[-1]
        prior_q = quarters[-2] if len(quarters) >= 2 else None
        latest = df[df["report_period"] == latest_q]
        # Batch 549 OPT-C: Shares_num pre-converted in cache layer
        latest_by_fund = latest.groupby("Fund")["Shares_num"].sum()
        if prior_q is None:
            new_pos = int((latest_by_fund > 0).sum())
            return {
                "signal": "buy" if new_pos >= 10 else "none",
                "new_positions": new_pos, "increased": 0, "decreased": 0,
                "source": "perticker_no_prior",
            }
        prior = df[df["report_period"] == prior_q]
        prior_by_fund = prior.groupby("Fund")["Shares_num"].sum()
        # Batch 549 OPT-C: vectorize per-fund classification via outer-join
        # reindex (was Python for-loop over union of fund names).
        all_idx = latest_by_fund.index.union(prior_by_fund.index)
        cur_arr = latest_by_fund.reindex(all_idx, fill_value=0.0).to_numpy()
        prv_arr = prior_by_fund.reindex(all_idx, fill_value=0.0).to_numpy()
        new_pos = int(((prv_arr == 0) & (cur_arr > 0)).sum())
        increased = int(((prv_arr > 0) & (cur_arr > prv_arr)).sum())
        decreased = int((cur_arr < prv_arr).sum())
        signal = "none"
        if new_pos >= 3 or (new_pos >= 1 and increased >= 2):
            signal = "strong_buy"
        elif new_pos >= 1 or increased >= 2:
            signal = "buy"
        elif decreased > increased:
            signal = "negative"
        return {"signal": signal, "new_positions": new_pos,
                "increased": increased, "decreased": decreased,
                "source": "perticker_history"}
    except Exception as exc:
        logger.debug("_institutional_signal_from_perticker(%s): %s",
                     ticker, exc)
        return {"signal": "none"}


def institutional_signal(ticker: str, as_of: date) -> dict:
    """13F institutional holdings signal. Returns dict with `signal` in
    {"none", "buy", "strong_buy", "negative"} + diagnostic counts.

    Batch 294 (2026-05-21 owner-approved F1 per 13F integration investigation):
    Two-source resolution closes the historical-depth gap. The bulk feed
    (data_prefetch/quiver/sec13fchanges/global.parquet) is fast and precomputes
    deltas but only has ~12 months of recent data. The per-ticker historical
    cache (data_prefetch/quiver/institutional/{TICKER}.parquet) has 2006-2025
    full history but needs delta computation. Try bulk first (fast path),
    fall back to per-ticker when bulk has no data for the date.

    Result dict includes "source" key for diagnostics: "bulk",
    "perticker_history", "perticker_no_prior", or absent (none-from-bulk).

    PIT respect: 45-day reporting lag (DEC-325) applies to both sources.

    BUG-273 history: Pass 53 (2026-05-06) migrated from per-ticker to bulk
    feed for performance. The bulk feed has only ~12 months of history,
    silently dropping 17+ years of historical 13F coverage. 97% of T1a
    trades returned "none" because their as_of dates were older than the
    bulk feed window. Batch 294 restores historical depth via the
    per-ticker fallback while keeping bulk as the fast path for recent
    dates.

    Signal classification thresholds (preserved across sources):
      strong_buy: new_pos >= 3 OR (new_pos >= 1 AND increased >= 2)
      buy:        new_pos >= 1 OR increased >= 2
      negative:   decreased > increased
      none:       otherwise
    """
    bulk_result = _institutional_signal_from_bulk(ticker, as_of)
    if bulk_result.get("signal") != "none":
        return bulk_result
    return _institutional_signal_from_perticker_history(ticker, as_of)


# -----------------------------------------------------------------------------
# COMPOSITE SMART MONEY SCORE
# -----------------------------------------------------------------------------

def smart_money_score(
    ticker: str, as_of: date,
    cong: Optional[dict] = None,
    ins:  Optional[dict] = None,
    inst: Optional[dict] = None,
) -> dict:
    """
    Compute composite smart money score and return all keys expected by:
    - backtest engine: composite_signal, score, congressional_signal,
                       insider_signal, institutional_signal
    - agent pipeline: congressional_sig, insider_sig, institutional_sig,
                      smart_money_composite
    """
    if cong is None: cong = congressional_signal(ticker, as_of)
    if ins  is None: ins  = insider_signal(ticker, as_of)
    if inst is None: inst = institutional_signal(ticker, as_of)

    cs   = cong.get("signal", "none")
    iss  = ins.get("signal", "none")
    ints = inst.get("signal", "none")

    if cs == "sell" and iss == "cluster_sell":
        composite = "congressional_sell+insider_cluster_sell"
        score = -5
    else:
        score = 0
        if cs  == "strong_buy":   score += 4
        elif cs == "buy":          score += 2
        elif cs == "sell":         score -= 3
        if iss == "strong_buy":   score += 4
        elif iss == "buy":         score += 2
        elif iss == "weak_buy":    score += 1
        elif iss == "cluster_sell": score -= 3
        if ints == "strong_buy":  score += 2
        elif ints == "buy":        score += 1
        elif ints == "negative":   score -= 1

        if score >= 6:    composite = "congressional+insider_cluster"
        elif score >= 4:  composite = "congressional_or_insider"
        elif score >= 2:  composite = "any_buy"
        elif score >= 1:  composite = "weak_buy"
        elif score <= -4: composite = "congressional_sell+insider_cluster_sell"
        elif score < 0:   composite = "negative"
        else:             composite = "none"

    # Batch 531 (2026-05-31, P17e activation per owner directive "wire in
    # activate truly pending items"). +1 to score when SC 13G passive
    # filing landed in last 30 days (Vanguard/BlackRock crossing 5% =>
    # index reweighting + forced fund buying signal). Modifier is
    # composite-recompute-safe: re-evaluates composite from the new
    # score so downstream tier-assignment sees the boosted band.
    try:
        from backtest.signals.sec_edgar_modifiers import (
            smart_money_score_modifier_13g,
        )
        new_score = smart_money_score_modifier_13g(ticker, as_of, score)
        if new_score != score:
            score = new_score
            # Recompute composite band from new score to keep them
            # consistent for downstream consumers.
            if score >= 6:    composite = "congressional+insider_cluster"
            elif score >= 4:  composite = "congressional_or_insider"
            elif score >= 2:  composite = "any_buy"
            elif score >= 1:  composite = "weak_buy"
            elif score <= -4: composite = "congressional_sell+insider_cluster_sell"
            elif score < 0:   composite = "negative"
            else:             composite = "none"
    except Exception:
        pass

    return {
        # Tier assignment keys (backtest engine)
        "composite_signal":      composite,
        "score":                 score,
        "congressional_signal":  cs,
        "insider_signal":        iss,
        "institutional_signal":  ints,
        # Agent pipeline keys
        "congressional_sig":     cong,
        "insider_sig":           ins,
        "institutional_sig":     inst,
        "smart_money_composite": {"composite": composite, "score": score},
        # Detail breakdown
        "details": {"congressional": cs, "insider": iss, "institutional": ints},
    }


# -----------------------------------------------------------------------------
# NEWS SENTIMENT
# Pass 53 Batch 13 sub-task 2 (DEC-507 + L146 wiring matrix Row 2 closure):
# PRIMARY source = Polygon news (DEC-440) read from data_prefetch/polygon/news/
# {TICKER}.parquet (Sprint 0A Batch 3 prefetched 1.05M articles for 1,926
# tickers). Polygon news includes rich `insights` array with per-ticker
# `sentiment` ('positive'/'negative'/'neutral') + `sentiment_reasoning` text.
# LEGACY fallback: Alpha Vantage + Finnhub paths retained for backwards
# compatibility (BUG-217 Pass 48). Will be removed Sprint 0A.8 NO-LIVE-API
# refactor + Batch 14 test cleanup.
# -----------------------------------------------------------------------------

# data_prefetch path (Pass 53 Batch 3 + Batch 13 Row 2 closure)
PREFETCH_POLYGON_NEWS_DIR = _REPO_ROOT / "data_prefetch" / "polygon" / "news"

# Legacy paths (BUG-217 Pass 48; preserved during transition)
AV_NEWS_DIR = Path(__file__).parent / "cache" / "av_news"
FH_NEWS_DIR = Path(__file__).parent / "cache" / "finnhub_news"


# -----------------------------------------------------------------------------
# SEC EDGAR FILINGS  -  Pass 53 Day-9 v8c G7 closure (L146 wiring)
#
# Sprint 0A Batch 11 prefetched 6056 filings across 4 form types:
#   - Form 4    : insider transactions (per-ticker, ~1336 rows AAPL)
#   - 8-K       : material event disclosures (per-ticker, ~234 rows AAPL)
#   - SC 13D    : activist 5%+ holder filings (per-ticker, ~7 rows AAPL)
#   - SC 13G    : passive 5%+ holder filings (per-ticker, ~81 rows AAPL)
#
# Schema (uniform across form types):
#   ticker, cik, form, filing_date, accession_number, primary_doc
#
# Public accessors below; strategy-side wiring deferred to Phase 1B+ per
# CLAUDE.md (Layer-2 catalyst signal candidate).
# -----------------------------------------------------------------------------

PREFETCH_SEC_EDGAR_DIR = _REPO_ROOT / "data_prefetch" / "sec_edgar"

# EDGAR form-type -> subdirectory mapping. Form names with spaces become
# underscored on disk (e.g., "8-K" -> "8_K", "SC 13D" -> "SC_13D").
# Pass 53 Day-9 v8h Tier B1-B4 expansion: 10-K, 10-Q, DEF 14A, S-1, S-1/A,
# SC 13D/A, SC 13G/A added.
SEC_EDGAR_FORM_DIRS = {
    "4":        "4",
    "8-K":      "8_K",
    "SC 13D":   "SC_13D",
    "SC 13G":   "SC_13G",
    # Tier B1: annual + quarterly reports
    "10-K":     "10_K",
    "10-Q":     "10_Q",
    # Tier B2: proxy statements
    "DEF 14A":  "DEF_14A",
    # Tier B3: IPO registration + amendments
    "S-1":      "S_1",
    "S-1/A":    "S_1_A",
    # Tier B4: beneficial-ownership amendments
    "SC 13D/A": "SC_13D_A",
    "SC 13G/A": "SC_13G_A",
}


def _load_sec_filings(ticker: str, form: str) -> Optional[pd.DataFrame]:
    """Read prefetched SEC EDGAR filings parquet for one form type."""
    subdir = SEC_EDGAR_FORM_DIRS.get(form)
    if subdir is None:
        return None
    safe = ticker.replace(".", "-")
    path = PREFETCH_SEC_EDGAR_DIR / subdir / f"{safe}.parquet"
    if not path.exists():
        return None
    try:
        df = pd.read_parquet(path)
        if df.empty:
            return None
        df["filing_date"] = pd.to_datetime(df["filing_date"])
        return df
    except Exception as exc:
        logger.debug("SEC EDGAR %s/%s read failed: %s", subdir, ticker, exc)
        return None


def get_sec_filings(
    ticker: str,
    as_of: date,
    lookback_days: int = 30,
    form: str = "8-K",
) -> dict:
    """Return SEC filings of one form type for `ticker` filed within the
    `lookback_days` window ending at `as_of` (point-in-time).

    Args:
      ticker: stock ticker.
      as_of: cutoff date (PIT). Filings filed > as_of are excluded.
      lookback_days: window length (default 30 days).
      form: one of '4' / '8-K' / 'SC 13D' / 'SC 13G'.

    Returns:
      dict with keys:
        'count'        -  number of filings in window
        'most_recent'  -  datetime of most recent filing in window (or None)
        'days_since'   -  days since most recent filing (or None)
        'filings'      -  list of {filing_date, accession_number} dicts (<=25)
    """
    df = _load_sec_filings(ticker, form)
    if df is None or df.empty:
        return {"count": 0, "most_recent": None, "days_since": None,
                "filings": []}

    cutoff = pd.Timestamp(as_of)
    window_start = cutoff - pd.Timedelta(days=lookback_days)
    in_window = df[(df["filing_date"] <= cutoff) &
                   (df["filing_date"] >= window_start)]
    in_window = in_window.sort_values("filing_date", ascending=False)

    if in_window.empty:
        return {"count": 0, "most_recent": None, "days_since": None,
                "filings": []}

    most_recent = in_window["filing_date"].iloc[0]
    days_since = (cutoff - most_recent).days
    return {
        "count":       int(len(in_window)),
        "most_recent": most_recent,
        "days_since":  int(days_since),
        "filings":     in_window[["filing_date", "accession_number"]]
                          .head(25)
                          .to_dict(orient="records"),
    }


def sec_catalyst_signal(ticker: str, as_of: date) -> dict:
    """Composite catalyst-event signal from SEC EDGAR filings (PIT).

    Combines 4 form types into a single dict suitable for strategy/agent input.
    Heuristic scoring (Phase 1A baseline; weights revisitable Phase 1B):

      - 8-K filed <= 5 trading days       -> +1 score (recent material event)
      - SC 13D filed <= 30 days           -> +2 score (activist accumulation)
      - SC 13G filed <= 30 days           -> +1 score (passive accumulation)
      - Form 4 cluster >= 3 in 30 days    -> +/- depending on transaction code

    Returns dict with per-form `count` + `days_since` + composite `score`.
    """
    eight_k    = get_sec_filings(ticker, as_of, lookback_days=10, form="8-K")
    sc_13d     = get_sec_filings(ticker, as_of, lookback_days=30, form="SC 13D")
    sc_13g     = get_sec_filings(ticker, as_of, lookback_days=30, form="SC 13G")
    form_4     = get_sec_filings(ticker, as_of, lookback_days=30, form="4")

    score = 0
    if eight_k["count"] > 0 and (eight_k["days_since"] or 99) <= 5:
        score += 1
    if sc_13d["count"] > 0:
        score += 2
    if sc_13g["count"] > 0:
        score += 1

    return {
        "8k":         eight_k,
        "sc_13d":     sc_13d,
        "sc_13g":     sc_13g,
        "form_4":     form_4,
        "score":      score,
        "label":      ("activist_accumulation" if sc_13d["count"] > 0
                        else "recent_8k"        if score >= 1
                        else "no_recent_filings"),
    }


def _polygon_insights_to_score(insights, ticker: str) -> Optional[float]:
    """Extract per-ticker sentiment from Polygon news insights array.

    Polygon insights schema (per article, when present):
        [{'ticker': 'AAPL', 'sentiment': 'positive'|'negative'|'neutral',
          'sentiment_reasoning': '...'}, ...]

    Returns score in [-1, 1] for the matching ticker, or None if absent.
    Mapping: positive=+1.0, negative=-1.0, neutral=0.0.
    """
    if insights is None:
        return None
    try:
        # insights may be list, ndarray, or string-encoded list
        if isinstance(insights, str):
            return None  # serialized; skip
        for entry in insights:
            if not isinstance(entry, dict):
                continue
            if str(entry.get("ticker", "")).upper() == ticker.upper():
                sent = str(entry.get("sentiment", "")).lower()
                if sent == "positive":
                    return 1.0
                if sent == "negative":
                    return -1.0
                if sent == "neutral":
                    return 0.0
    except (TypeError, ValueError):
        pass
    return None


def get_news_sentiment(ticker: str, as_of: date, lookback_days: int = 7) -> dict:
    """
    Return news sentiment for ticker in the lookback window before as_of.

    PRIMARY (Pass 53 Batch 13 Row 2 closure): data_prefetch/polygon/news/
    LEGACY fallback: Alpha Vantage + Finnhub caches.

    Returns dict:
        sentiment_score: float (-1 to 1), positive = bullish news
        article_count: int  -  number of articles in window
        signal: bullish | bearish | neutral
        source: polygon | alphavantage | finnhub | none
    """
    safe_ticker = ticker.replace("-", "_").replace(".", "_")
    result = {"sentiment_score": 0.0, "article_count": 0,
              "signal": "neutral", "source": "none"}

    # === PRIMARY: Polygon news with per-ticker insights ===
    polygon_path = PREFETCH_POLYGON_NEWS_DIR / f"{safe_ticker}.parquet"
    if polygon_path.exists():
        try:
            df = pd.read_parquet(polygon_path)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                window_start = pd.Timestamp(as_of - timedelta(days=lookback_days))
                window_end = pd.Timestamp(as_of)
                window = df[(df["date"] >= window_start) & (df["date"] <= window_end)]
                if not window.empty:
                    # Extract per-ticker sentiment scores from insights
                    scores = []
                    for insights_val in window.get("insights", pd.Series()):
                        s = _polygon_insights_to_score(insights_val, ticker)
                        if s is not None:
                            scores.append(s)
                    article_count = len(window)
                    if scores:
                        avg_score = sum(scores) / len(scores)
                        if avg_score >= 0.15:
                            signal = "bullish"
                        elif avg_score <= -0.15:
                            signal = "bearish"
                        else:
                            signal = "neutral"
                        return {
                            "sentiment_score": round(avg_score, 3),
                            "article_count": article_count,
                            "scored_count": len(scores),  # NEW: # articles with insights
                            "signal": signal,
                            "source": "polygon",
                        }
                    # Articles in window but none had insights  -  still better than nothing
                    return {
                        "sentiment_score": 0.0,
                        "article_count": article_count,
                        "scored_count": 0,
                        "signal": "neutral",
                        "source": "polygon_no_insights",
                    }
        except Exception as exc:
            logger.debug("get_news_sentiment polygon path %s: %s", ticker, exc)

    # === LEGACY fallback (Alpha Vantage / Finnhub) ===
    for cache_dir, source in [(AV_NEWS_DIR, "alphavantage"),
                               (FH_NEWS_DIR, "finnhub")]:
        path = cache_dir / f"{safe_ticker}.parquet"
        if not path.exists():
            continue
        try:
            df = pd.read_parquet(path)
            if df.empty or "date" not in df.columns:
                continue

            df["date"] = pd.to_datetime(df["date"])
            window_start = pd.Timestamp(as_of - timedelta(days=lookback_days))
            window_end   = pd.Timestamp(as_of)
            window = df[(df["date"] >= window_start) & (df["date"] <= window_end)]

            if window.empty:
                continue

            if "sentiment_weighted" in window.columns:
                avg_score = float(window["sentiment_weighted"].mean())
            elif "sentiment_mean" in window.columns:
                avg_score = float(window["sentiment_mean"].mean())
            elif "sentiment_score" in window.columns:
                avg_score = float(window["sentiment_score"].mean())
            else:
                continue

            article_count = (int(window["article_count"].sum())
                             if "article_count" in window.columns
                             else len(window))

            if avg_score >= 0.15:
                signal = "bullish"
            elif avg_score <= -0.15:
                signal = "bearish"
            else:
                signal = "neutral"

            return {
                "sentiment_score": round(avg_score, 3),
                "article_count":   article_count,
                "signal":          signal,
                "source":          source,
            }
        except Exception as exc:
            logger.debug("get_news_sentiment(%s,%s): %s", ticker, source, exc)
            continue

    return result


def get_gov_contracts(ticker: str, as_of: date, lookback_days: int = 365) -> dict:
    """
    Return government contract activity for ticker in lookback window.
    Reads from pre-fetched Quiver gov_contracts cache.

    BUG-271 fix 2026-05-13: Quiver gov_contracts schema has Qtr (int 1-4) +
    Year (int), NOT a Date column. Prior code used date-column search -> always
    returned no_data (99.4% silent failure). Fix: reconstruct quarter-end date
    from Qtr+Year (Q1->Mar-31, Q2->Jun-30, Q3->Sep-30, Q4->Dec-31).
    Also: Amount column is str dtype -> pd.to_numeric() before sum().

    Returns dict:
        total_amount: float  -  total contract value in window
        contract_count: int
        recent_win: bool  -  contract won in last 90 days
        trend: growing | stable | declining
        signal: bullish | neutral | no_data
    """
    _QTR_MONTH = {1: 3, 2: 6, 3: 9, 4: 12}
    _QTR_DAY   = {1: 31, 2: 30, 3: 30, 4: 31}
    result = {"total_amount": 0.0, "contract_count": 0,
              "recent_win": False, "trend": "stable", "signal": "no_data"}
    df = _load_prefetch("gov_contracts", ticker)
    if df is None or df.empty:
        return result
    try:
        if "Qtr" in df.columns and "Year" in df.columns:
            from datetime import date as _date
            def _qtr_end(row):
                try:
                    return _date(int(row["Year"]), _QTR_MONTH[int(row["Qtr"])],
                                 _QTR_DAY[int(row["Qtr"])])
                except Exception:
                    return None
            df = df.copy()
            df["_qtr_date"] = df.apply(_qtr_end, axis=1)
            df = df[df["_qtr_date"].notna()]
            date_col = "_qtr_date"
        else:
            date_col = next((c for c in df.columns if "date" in c.lower()), None)
            if not date_col:
                return result
            df = df.copy()
            df[date_col] = pd.to_datetime(df[date_col]).dt.date
        window = df[df[date_col] <= as_of]
        recent = window[window[date_col] >= as_of - timedelta(days=lookback_days)]
        if recent.empty:
            return result
        amount_col = next((c for c in df.columns if "amount" in c.lower()), None)
        total = float(pd.to_numeric(recent[amount_col], errors="coerce").fillna(0).sum()) if amount_col else 0.0
        recent_90 = window[window[date_col] >= as_of - timedelta(days=90)]
        older = window[
            (window[date_col] >= as_of - timedelta(days=365)) &
            (window[date_col] < as_of - timedelta(days=90))
        ]
        trend = "growing" if len(recent_90) > len(older) / 3 else "stable"
        return {
            "total_amount": round(total, 2),
            "contract_count": len(recent),
            "recent_win": len(recent_90) > 0,
            "trend": trend,
            "signal": "bullish" if total > 0 else "neutral",
        }
    except Exception as exc:
        logger.debug("get_gov_contracts(%s): %s", ticker, exc)
        return result


def get_lobbying(ticker: str, as_of: date, lookback_days: int = 365) -> dict:
    """
    Return lobbying spend activity for ticker.
    Reads from pre-fetched Quiver lobbying cache.

    Returns dict:
        total_spend: float  -  total lobbying spend in window
        filing_count: int
        issues: list  -  lobbying issue areas
        signal: high_spend | moderate | low | no_data
    """
    result = {"total_spend": 0.0, "filing_count": 0,
              "issues": [], "signal": "no_data"}
    df = _load_prefetch("lobbying", ticker)
    if df is None or df.empty:
        return result
    try:
        date_col = next((c for c in df.columns if "date" in c.lower()), None)
        if not date_col:
            return result
        df[date_col] = pd.to_datetime(df[date_col])
        window = df[
            (df[date_col] <= pd.Timestamp(as_of)) &
            (df[date_col] >= pd.Timestamp(as_of) - pd.Timedelta(days=lookback_days))
        ]
        if window.empty:
            return result
        amount_col = next((c for c in df.columns if "amount" in c.lower()), None)
        # BUG-272 fix 2026-05-13: Quiver lobbying Amount dtype is str; .sum()
        # concatenated strings instead of adding numerics -> 98.8% silent failure.
        total = float(pd.to_numeric(window[amount_col], errors="coerce").fillna(0).sum()) if amount_col else 0.0
        issue_col = next((c for c in df.columns if "issue" in c.lower()), None)
        issues = list(window[issue_col].dropna().unique()[:5]) if issue_col else []
        signal = "high_spend" if total > 1_000_000 else "moderate" if total > 100_000 else "low"
        return {
            "total_spend": round(total, 2),
            "filing_count": len(window),
            "issues": issues,
            "signal": signal,
        }
    except Exception as exc:
        logger.debug("get_lobbying(%s): %s", ticker, exc)
        return result


def get_congressional_detail(ticker: str, as_of: date, top_n: int = 3) -> list:
    """
    Return top N most recent congressional trades with full detail.
    Used by Sentiment Agent for richer context vs composite signal only.
    Point-in-time enforced: include filings publicly available by as_of.

    BUG-83 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 18 2026-05-10
    (owner-approved Option A): removed erroneous 45-day delta subtraction.
    Quiver's `ReportDate` already reflects the upstream disclosure delay
    (ReportDate >= TransactionDate by the lag); subtracting another 45 days
    excluded the most recent (most actionable) filings from the agent's
    detail view, contradicting the composite signal in the same module.
    Restores consistency with `insider_signal` and composite congressional_sig.

    Returns list of dicts with: representative, transaction, amount_range,
    transaction_date, party, house
    """
    df = _load_prefetch("congressional", ticker)
    if df is None or df.empty:
        return []
    try:
        df["TransactionDate"] = pd.to_datetime(df["TransactionDate"], errors="coerce")
        df["ReportDate"] = pd.to_datetime(df.get("ReportDate", df["TransactionDate"]),
                                           errors="coerce")
        # BUG-83 fix: PIT semantics = ReportDate <= as_of (upstream disclosure
        # delay is already encoded in ReportDate). No additional 45-day delta.
        cutoff = pd.Timestamp(as_of)
        available = df[df["ReportDate"] <= cutoff].copy()
        if available.empty:
            return []
        available = available.sort_values("TransactionDate", ascending=False)
        top = available.head(top_n)
        return [
            {
                "representative": row.get("Representative", "Unknown"),
                "party": row.get("Party", ""),
                "house": row.get("House", ""),
                "transaction": row.get("Transaction", ""),
                "amount_range": row.get("Range", row.get("Amount", "")),
                "transaction_date": str(row.get("TransactionDate", ""))[:10],
                "days_ago": (pd.Timestamp(as_of) - row.get("TransactionDate",
                             pd.Timestamp(as_of))).days,
            }
            for _, row in top.iterrows()
        ]
    except Exception as exc:
        logger.debug("get_congressional_detail(%s): %s", ticker, exc)
        return []


# -----------------------------------------------------------------------------
# Pass 53 Day-9 v8c Wave C  -  L146 G12+G13+G14+G15 Quiver new-signal accessors
# -----------------------------------------------------------------------------
# Wires 4 previously-unconsumed Quiver datasets into thin accessor functions.
# Strategy-side wiring (smart_money composite, agent inputs) deferred to
# Phase 1B+ per CLAUDE.md (Layer-2 candidate signals).
#
# Each accessor reads from data_prefetch/quiver/<dataset>/<TICKER>.parquet
# (PIT-safe per Sprint 0A.8 NO-LIVE-API HARD CUT).


def get_etf_holdings(ticker: str) -> dict:
    """G12  -  Which ETFs hold this ticker, and at what weight?

    Source: data_prefetch/quiver/etfholdings/<TICKER>.parquet
    Schema: 'ETF Symbol' / 'Holding Name' / 'Holding Symbol' / '% of ETF' /
            'Value ($)'

    Returns dict with:
      etf_count         -  number of ETFs holding this ticker
      top_etf_weight    -  max % of any single ETF
      total_etf_value   -  sum of $ value across all ETF holdings
      top10             -  list of {etf_symbol, weight_pct, value_usd} top 10

    .. WARNING:: NO PIT DIMENSION
       Source data has no date column  -  this is a CURRENT snapshot of ETF
       inclusions, not a historical record. Using this in a backtest at
       as_of=2020 silently leaks future ETF inclusion changes. Phase 1A
       must NOT use this accessor for time-bounded decisions until source
       prefetch is extended with date dimension. Documented per Pass 53
       Day-9 v8g PIT audit (Batch 7).
    """
    df = _load_prefetch("etfholdings", ticker)
    default = {"etf_count": 0, "top_etf_weight": 0.0,
               "total_etf_value": 0.0, "top10": []}
    if df is None or df.empty:
        return default
    try:
        df_sorted = df.sort_values("% of ETF", ascending=False)
        top10 = [
            {
                "etf_symbol":  row["ETF Symbol"],
                "weight_pct":  float(row["% of ETF"]),
                "value_usd":   float(row["Value ($)"]),
            }
            for _, row in df_sorted.head(10).iterrows()
        ]
        return {
            "etf_count":       int(len(df)),
            "top_etf_weight":  float(df["% of ETF"].max()),
            "total_etf_value": float(df["Value ($)"].sum()),
            "top10":           top10,
        }
    except Exception as exc:
        logger.debug("get_etf_holdings(%s): %s", ticker, exc)
        return default


def get_offexchange_volume(ticker: str, as_of: date,
                            lookback_days: int = 5) -> dict:
    """G13  -  Dark-pool / off-exchange volume signal (PIT).

    Source: data_prefetch/quiver/offexchange/<TICKER>.parquet
    Schema: Ticker / Date / OTC_Short / OTC_Total / DPI

    DPI = Dark-Pool Index (off-exchange volume / total volume). Rising DPI
    can indicate institutional accumulation (or distribution) in dark venues.

    Returns dict with avg DPI in window, latest DPI, and short-vol ratio.
    """
    df = _load_prefetch("offexchange", ticker)
    default = {"avg_dpi": None, "latest_dpi": None, "short_ratio": None,
               "rows_in_window": 0, "as_of": str(as_of)}
    if df is None or df.empty or "Date" not in df.columns:
        return default
    try:
        df["Date"] = pd.to_datetime(df["Date"])
        cutoff = pd.Timestamp(as_of)
        window_start = cutoff - pd.Timedelta(days=lookback_days)
        window = df[(df["Date"] >= window_start) & (df["Date"] <= cutoff)]
        if window.empty:
            return default
        avg_dpi = float(window["DPI"].mean()) if "DPI" in window.columns else None
        latest_row = window.iloc[-1]
        latest_dpi = float(latest_row.get("DPI", 0)) if "DPI" in window.columns else None
        short_ratio = None
        if "OTC_Short" in window.columns and "OTC_Total" in window.columns:
            tot = float(latest_row.get("OTC_Total", 0))
            if tot > 0:
                short_ratio = float(latest_row.get("OTC_Short", 0)) / tot
        return {
            "avg_dpi":         avg_dpi,
            "latest_dpi":      latest_dpi,
            "short_ratio":     short_ratio,
            "rows_in_window":  int(len(window)),
            "as_of":           str(as_of),
        }
    except Exception as exc:
        logger.debug("get_offexchange_volume(%s): %s", ticker, exc)
        return default


def get_top_shareholders(ticker: str, top_n: int = 10) -> dict:
    """G14  -  Institutional ownership concentration signal.

    Source: data_prefetch/quiver/topshareholders/<TICKER>.parquet
    Schema: 1 row with 'ownership' (array of dicts) + 'ownership_options' arrays.
    Each dict: owner_name / owner_title / shares (or underlying_shares for options).

    Returns top-N institutional holders + total share count + concentration.

    .. WARNING:: NO PIT DIMENSION
       Source is a CURRENT shareholder snapshot, not historical. Using this
       in a backtest at past as_of silently leaks current ownership info.
       Phase 1A must NOT use this for time-bounded decisions until source
       is extended. Documented per Pass 53 Day-9 v8g PIT audit (Batch 7).
       Use ``institutional_signal()`` (sec13fchanges bulk; PIT-correct) for
       backtest-time concentration signals.
    """
    df = _load_prefetch("topshareholders", ticker)
    default = {"top_n_count": 0, "top_n_total_shares": 0,
               "top_holder_shares": 0, "top_holders": []}
    if df is None or df.empty or "ownership" not in df.columns:
        return default
    try:
        ownership_arr = df["ownership"].iloc[0]
        # ownership is a numpy array of dicts; cast to list of dicts
        if hasattr(ownership_arr, "tolist"):
            owners = list(ownership_arr.tolist())
        else:
            owners = list(ownership_arr) if ownership_arr is not None else []
        if not owners:
            return default
        # Sort by shares desc, take top_n
        owners_sorted = sorted(
            (o for o in owners if isinstance(o, dict)),
            key=lambda o: o.get("shares", 0) or 0, reverse=True
        )[:top_n]
        top_total = sum(o.get("shares", 0) or 0 for o in owners_sorted)
        top_holder_shares = owners_sorted[0].get("shares", 0) if owners_sorted else 0
        return {
            "top_n_count":         int(len(owners_sorted)),
            "top_n_total_shares":  int(top_total),
            "top_holder_shares":   int(top_holder_shares),
            "top_holders":         [
                {"name": o.get("owner_name", ""),
                 "title": o.get("owner_title", ""),
                 "shares": int(o.get("shares", 0) or 0)}
                for o in owners_sorted
            ],
        }
    except Exception as exc:
        logger.debug("get_top_shareholders(%s): %s", ticker, exc)
        return default


def get_wsb_attention(ticker: str, as_of: date,
                       lookback_days: int = 7) -> dict:
    """G15  -  Reddit r/wallstreetbets mention/sentiment signal (PIT).

    Source: data_prefetch/quiver/wallstreetbets/<TICKER>.parquet
    Schema: Date / Ticker / Mentions / Rank / Sentiment

    Returns aggregate mentions + avg sentiment + max rank in window.
    Caveat: WSB sentiment is noisy; useful as retail-attention proxy.
    """
    df = _load_prefetch("wallstreetbets", ticker)
    default = {"total_mentions": 0, "avg_sentiment": None,
               "best_rank": None, "rows_in_window": 0, "as_of": str(as_of)}
    if df is None or df.empty or "Date" not in df.columns:
        return default
    try:
        df["Date"] = pd.to_datetime(df["Date"])
        cutoff = pd.Timestamp(as_of)
        window_start = cutoff - pd.Timedelta(days=lookback_days)
        window = df[(df["Date"] >= window_start) & (df["Date"] <= cutoff)]
        if window.empty:
            return default
        total_mentions = int(window.get("Mentions", pd.Series([0])).sum())
        avg_sentiment = (float(window["Sentiment"].mean())
                          if "Sentiment" in window.columns else None)
        best_rank = (int(window["Rank"].min())
                      if "Rank" in window.columns and not window["Rank"].isna().all()
                      else None)
        return {
            "total_mentions":   total_mentions,
            "avg_sentiment":    avg_sentiment,
            "best_rank":        best_rank,
            "rows_in_window":   int(len(window)),
            "as_of":            str(as_of),
        }
    except Exception as exc:
        logger.debug("get_wsb_attention(%s): %s", ticker, exc)
        return default


# -----------------------------------------------------------------------------
# Pass 53 Day-9 v8c Wave D  -  L146 G10/G11/G16/G17 closures
# -----------------------------------------------------------------------------
# G10: insider per-ticker fast-path accessor (bulk remains canonical)
# G11: institutional per-ticker prefetch is INCOMPLETE (AAPL empty, ~18% empty);
#      bulk sec13fchanges is canonical. Document; do not delete data.
# G16: Quiver wikipedia mirror is empty (separate data_prefetch/wikipedia/ used).
#      Document; do not delete.
# G17: 4 micro-datasets  -  wire 3 with real data (patentmomentum / corporatedonors /
#      sec13f); skip quivernews (general headlines, not per-ticker; Polygon news
#      is the canonical news source already wired).


def get_insider_transactions_pertkr(ticker: str, as_of: date,
                                     lookback_days: int = 90) -> dict:
    """G10  -  Insider transactions for `ticker` from per-ticker prefetch (PIT).

    Source: data_prefetch/quiver/insider/<TICKER>.parquet (per-ticker fast path)
    Falls back to bulk insiders/global.parquet via _load_quiver_bulk if per-tkr
    file is missing. Bulk is canonical for completeness.

    Schema: Ticker / Date / Name / AcquiredDisposedCode (A=acquired/D=disposed) /
            TransactionCode / Shares / PricePerShare / SharesOwnedFollowing /
            officerTitle / isDirector / isOfficer / isTenPercentOwner

    Returns dict with buy/sell counts + cluster flag.
    """
    df = _load_prefetch("insider", ticker)
    if df is None or df.empty:
        # Fall back to bulk
        bulk = _load_quiver_bulk("insiders")
        if bulk.empty or "Ticker" not in bulk.columns:
            return {"buy_count": 0, "sell_count": 0, "cluster": False,
                    "rows_in_window": 0, "source": "none"}
        df = bulk[bulk["Ticker"] == ticker]
        source = "bulk"
    else:
        source = "per_ticker"
    if df.empty:
        return {"buy_count": 0, "sell_count": 0, "cluster": False,
                "rows_in_window": 0, "source": source}
    try:
        df = df.copy()
        # Pass 53 Day-9 v8f DEC-512 fix (BUG-INSIDER-PIT): PIT cutoff must use
        # fileDate (SEC filing) not Date (transaction). Public didn't know
        # about the transaction until the Form 4 was filed (~6 days lag).
        if "fileDate" in df.columns:
            df["pit_date"] = pd.to_datetime(df["fileDate"], errors="coerce")
            df = df[df["pit_date"].notna()]
        else:
            df["pit_date"] = pd.to_datetime(df["Date"], errors="coerce")
        cutoff = pd.Timestamp(as_of)
        window_start = cutoff - pd.Timedelta(days=lookback_days)
        win = df[(df["pit_date"] >= window_start) & (df["pit_date"] <= cutoff)]
        if win.empty:
            return {"buy_count": 0, "sell_count": 0, "cluster": False,
                    "rows_in_window": 0, "source": source}
        buys  = int((win["AcquiredDisposedCode"] == "A").sum())
        sells = int((win["AcquiredDisposedCode"] == "D").sum())
        return {
            "buy_count":      buys,
            "sell_count":     sells,
            "cluster":        buys >= 3 or sells >= 3,
            "rows_in_window": int(len(win)),
            "source":         source,
        }
    except Exception as exc:
        logger.debug("get_insider_transactions_pertkr(%s): %s", ticker, exc)
        return {"buy_count": 0, "sell_count": 0, "cluster": False,
                "rows_in_window": 0, "source": source}


def get_institutional_holdings_pertkr(ticker: str) -> dict:
    """G11  -  Institutional per-ticker prefetch (DOCUMENTED AS INCOMPLETE).

    Source: data_prefetch/quiver/institutional/<TICKER>.parquet
    Status: ~18% of per-ticker files empty (incl. AAPL). Bulk path
    `data_prefetch/quiver/sec13fchanges/global.parquet` (used by
    institutional_signal()) is the canonical source. This accessor exists
    so the per-ticker prefetch is reachable from code (closes L146 wiring
    gap) but is documented as fallback-only.

    Returns dict with row count + warning flag.
    """
    df = _load_prefetch("institutional", ticker)
    if df is None or df.empty:
        return {
            "row_count": 0,
            "is_complete": False,
            "warning": "Per-ticker institutional prefetch is empty for "
                       f"{ticker}; use institutional_signal() (bulk path) "
                       "or get_top_shareholders() instead.",
        }
    return {
        "row_count":   int(len(df)),
        "is_complete": True,
        "warning":     None,
    }


# G16: data_prefetch/quiver/wikipedia/ is empty for all 100 sampled tickers.
# The separate `data_prefetch/wikipedia/` (already consumed by sentiment.py
# via get_wikipedia_pageviews) is canonical. No accessor added  -  the empty
# Quiver mirror should be re-prefetched or removed (owner decision; data
# preservation rule keeps it for now).


def get_patent_momentum(ticker: str, as_of: date,
                        lookback_days: int = 90) -> dict:
    """G17a  -  Quiver patent-momentum signal (PIT).

    Source: data_prefetch/quiver/patentmomentum/global.parquet
    Schema: ticker / date / momentum (numeric)

    Returns latest patent-momentum value within lookback window.
    """
    bulk = _load_quiver_bulk("patentmomentum")
    if bulk.empty or "ticker" not in bulk.columns:
        return {"latest_momentum": None, "as_of": str(as_of), "found": False}
    try:
        df = bulk[bulk["ticker"] == ticker].copy()
        if df.empty:
            return {"latest_momentum": None, "as_of": str(as_of), "found": False}
        df["date"] = pd.to_datetime(df["date"])
        cutoff = pd.Timestamp(as_of)
        window_start = cutoff - pd.Timedelta(days=lookback_days)
        win = df[(df["date"] >= window_start) & (df["date"] <= cutoff)]
        if win.empty:
            return {"latest_momentum": None, "as_of": str(as_of), "found": False}
        latest = win.sort_values("date").iloc[-1]
        return {
            "latest_momentum": float(latest["momentum"]),
            "as_of":           str(as_of),
            "found":           True,
        }
    except Exception as exc:
        logger.debug("get_patent_momentum(%s): %s", ticker, exc)
        return {"latest_momentum": None, "as_of": str(as_of), "found": False}


def get_corporate_donations(ticker: str,
                              as_of: Optional[date] = None) -> dict:
    """G17b  -  Corporate PAC political donations summary (PIT, optional cutoff).

    Source: data_prefetch/quiver/corporatedonors/global.parquet
    Schema: BioGuideID / CandidateName / CompanyCMTENM / TransactionDate /
            TransactionAmount / Ticker / ...

    Pass 53 Day-9 v8g PIT-fix: now accepts optional ``as_of`` parameter.
    When provided, donations with TransactionDate > as_of are excluded
    (closes silent lookahead  -  donations made AFTER as_of weren't public yet).

    Returns total donation $ + recipient count for the company's PAC.
    """
    bulk = _load_quiver_bulk("corporatedonors")
    if bulk.empty or "Ticker" not in bulk.columns:
        return {"total_donations_usd": 0.0, "recipient_count": 0,
                "found": False}
    try:
        df = bulk[bulk["Ticker"] == ticker]
        if df.empty:
            return {"total_donations_usd": 0.0, "recipient_count": 0,
                    "found": False}
        # PIT cutoff per as_of
        if as_of is not None and "TransactionDate" in df.columns:
            df = df.copy()
            df["_td"] = pd.to_datetime(df["TransactionDate"], errors="coerce")
            cutoff = pd.Timestamp(as_of)
            df = df[df["_td"].notna() & (df["_td"] <= cutoff)]
            if df.empty:
                return {"total_donations_usd": 0.0, "recipient_count": 0,
                        "found": False}
        total = float(df["TransactionAmount"].sum())
        n = int(df["BioGuideID"].nunique())
        return {
            "total_donations_usd": total,
            "recipient_count":     n,
            "found":               True,
        }
    except Exception as exc:
        logger.debug("get_corporate_donations(%s): %s", ticker, exc)
        return {"total_donations_usd": 0.0, "recipient_count": 0,
                "found": False}


def get_sec13f_holdings(ticker: str, as_of: date) -> dict:
    """G17d  -  Full SEC 13F institutional holdings for `ticker` (PIT).

    Source: data_prefetch/quiver/sec13f/global.parquet (500K rows bulk).
    Schema: Date / ReportPeriod / Name / Ticker / Fund / Class / ...

    Complement to existing institutional_signal() which uses sec13fchanges
    (changes-only). This returns the most-recent absolute-holdings snapshot
    on or before as_of (filed within ~45 days of ReportPeriod).

    Returns dict with fund_count + total_value_held (when value column present).
    """
    bulk = _load_quiver_bulk("sec13f")
    if bulk.empty or "Ticker" not in bulk.columns:
        return {"fund_count": 0, "report_period": None, "found": False}
    try:
        df = bulk[bulk["Ticker"] == ticker].copy()
        if df.empty:
            return {"fund_count": 0, "report_period": None, "found": False}
        # Filter PIT: 13F filings appear ~45 days after ReportPeriod end
        df["Date"] = pd.to_datetime(df["Date"])
        cutoff = pd.Timestamp(as_of)
        df = df[df["Date"] <= cutoff]
        if df.empty:
            return {"fund_count": 0, "report_period": None, "found": False}
        df["ReportPeriod"] = pd.to_datetime(df["ReportPeriod"], errors="coerce")
        latest_rp = df["ReportPeriod"].max()
        latest_snap = df[df["ReportPeriod"] == latest_rp]
        return {
            "fund_count":    int(latest_snap["Fund"].nunique()),
            "report_period": str(latest_rp.date()) if pd.notna(latest_rp) else None,
            "found":         True,
        }
    except Exception as exc:
        logger.debug("get_sec13f_holdings(%s): %s", ticker, exc)
        return {"fund_count": 0, "report_period": None, "found": False}
