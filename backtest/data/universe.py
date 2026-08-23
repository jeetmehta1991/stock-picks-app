"""
data/universe.py  -  Instrument manager.

Handles:
  - Loading S&P 500 constituent list from committed static CSV (Current Snapshot_SP500 Tickers_May 2026.csv)
    The CSV is refreshed quarterly via slickcharts.com (or S&P press releases).
    See LEARNINGS L88: Wikipedia is unreliable as a runtime data source  -  the
    static CSV pattern is the correct approach.
  - Applying liquidity filters to reduce ~500 -> ~380-420 tradeable names
  - Appending new instruments to existing universe without re-fetching
  - Sector breakdown for correlation analysis

Universe tiers:
  Phase 1A: SP50 + 17 ETFs = 67 instruments (hardcoded  -  pipeline validation)
  Phase 1B: Filtered S&P 500 + all ETFs = ~400 instruments (CSV-backed)
  Phase 1C: Passing strategies only, full universe

Resolves: DEC-341 (Pass 52), closes BUG-264.
"""

import logging
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
# yfinance removed from runtime per DEC-497 D4 (Pass 53 Batch 13 sub-task 6
# 2026-05-06). Sector + info now via canonical CSV (Master Dedup 18-classifier).

from backtest.config import SP50, ETFS, LIQUIDITY

logger = logging.getLogger(__name__)

# Universe CSVs moved to top-level "Backtesting universe/" folder (Pass 53 owner directive)
# for repo-wide visibility. Path resolves from backtest/data/universe.py -> repo root.
UNIVERSE_DIR = Path(__file__).parent.parent.parent / "Backtesting universe"

# Full ETF list for Phase 1B+
# Per DEC-494 / Pass 53 owner directive: ETFs migrated from hardcoded list to
# `backtest/data/Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv` (Item 4 (ii) CSV + code migration). Module-level
# ETFS_FULL is computed at import time from the CSV via get_etfs_full() so that
# legacy callers (universe.py functions, agents, tests) continue to work without
# refactor. CSV is the source of truth; updates flow through the CSV, not this
# module.

def get_etfs_full() -> list[str]:
    """
    Load Tier 1 ETF list from `backtest/data/Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv`.

    Per DEC-494 (Pass 53 owner-approved Sprint 1)  -  ETFs are now declared in
    a CSV file alongside T1a/T1b/T1c membership files for consistency.
    No leveraged ETFs included  -  volatility decay invalidates backtest results.

    Returns list of ticker symbols. Falls back to empty list on read failure
    (callers should treat empty as a catastrophic config error).
    """
    csv_path = UNIVERSE_DIR / "Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv"
    try:
        df = pd.read_csv(csv_path, comment='#')
        tickers = df["Symbol"].drop_duplicates().tolist()
        logger.info("Loaded %d Tier 1 ETFs from Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv", len(tickers))
        return tickers
    except Exception as exc:
        logger.error("Could not read Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv: %s", exc)
        return []


# Computed at module import time  -  preserves legacy `from universe import ETFS_FULL`
# callers. CSV-backed; update Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv to change the list.
ETFS_FULL = get_etfs_full()


def get_sp500_constituents(max_tickers: int | None = None) -> list[str]:
    """
    Load S&P 500 constituent list from the committed CSV file.

    Uses Backtesting universe/Current Snapshot_SP500 Tickers_May 2026.csv  -  a maintained static file
    (Pass 53 folder move). Synced to Wikipedia Table 0 ground truth (503).
    No network calls, no rate limiting, works in all environments.
    Update Current Snapshot_SP500 Tickers_May 2026.csv manually when index membership changes
    (typically 10-20 changes per year).

    Per Pass 53: actual S&P 500 has ~503 securities (500 companies + dual-class).
    Default `max_tickers=None` returns all members. Pass an explicit cap only
    for tests or constrained-universe scenarios.
    """
    csv_path = UNIVERSE_DIR / "Current Snapshot_SP500 Tickers_May 2026.csv"
    try:
        df = pd.read_csv(csv_path, comment='#')
        # Remove duplicates by Symbol (defensive  -  file should already be unique by symbol)
        tickers = df["Symbol"].drop_duplicates().tolist()
        logger.info("Loaded %d S&P 500 constituents from Current Snapshot_SP500 Tickers_May 2026.csv", len(tickers))
        return tickers[:max_tickers] if max_tickers else tickers
    except Exception as exc:
        logger.error("Could not read Current Snapshot_SP500 Tickers_May 2026.csv: %s", exc)
        return []


# -- Pass 53 PIT loader (DEC-040 / DEC-477) ------------------------------------
# B++ schema universe CSVs use `added_date` / `removed_date` columns; PIT filter
# resolves the active member set at any `as_of` date without survivorship bias.
#
# PIT FILTER: (added_date IS NULL OR added_date <= as_of)
#         AND (removed_date IS NULL OR removed_date > as_of)
#
# Multi-period rows (ticker re-entry  -  e.g., NDX WDC/CSGP/TTWO/SPLK) are
# handled via standard pandas OR semantics: each row is filtered independently;
# union of passing rows is the active set at `as_of`.

def _filter_pit(df: pd.DataFrame, as_of: date) -> pd.DataFrame:
    """
    Apply B++ PIT filter to a DataFrame with `added_date` and `removed_date` columns.
    Returns rows active at `as_of`.
    """
    if "added_date" not in df.columns or "removed_date" not in df.columns:
        # File predates B++ migration  -  treat all rows as active (current snapshot semantics)
        return df

    as_of_ts = pd.Timestamp(as_of)
    added = pd.to_datetime(df["added_date"], errors="coerce")
    removed = pd.to_datetime(df["removed_date"], errors="coerce")
    # B2058 (S6-B1250-UNIVERSE-METRICS-DEPTH): a NON-NULL date that COERCES
    # to NaT is garbage, and under the NULL-passes rule it silently became a
    # PERMANENT member - fail-open path resolution for data. Measured clean
    # on the real T1a file today (0 of 109 added / 0 of 111 removed), so
    # excluding garbage rows is a zero-live-change hardening; each exclusion
    # is logged (#122 pairing).
    # an empty/whitespace cell is the CSV's NULL convention (the DEC-477 pins
    # encode it as ""), NOT garbage - only a non-blank unparseable value is.
    def _nonblank(col):
        return df[col].notna() & (df[col].astype(str).str.strip() != "")
    garbage = (added.isna() & _nonblank("added_date")) | \
              (removed.isna() & _nonblank("removed_date"))
    if bool(garbage.any()):
        logger.warning(
            "PIT filter EXCLUDING %d row(s) with unparseable dates "
            "(fail-closed; a garbage date must not read as always-active): %s",
            int(garbage.sum()),
            df.loc[garbage, "Symbol"].tolist()[:5] if "Symbol" in df.columns
            else "<no Symbol col>")
    # NULL added_date -> "in index prior to mapping window" -> always passes left side
    # NULL removed_date -> "currently active" -> always passes right side
    # Boundary convention, MEASURED B2058 (AGN removed 2020-05-12): a ticker
    # is OUT on its removal date itself - `removed > as_of` matches the S&P
    # effective-prior-to-open convention.
    left_ok = added.isna() | (added <= as_of_ts)
    right_ok = removed.isna() | (removed > as_of_ts)
    return df[left_ok & right_ok & ~garbage]


def get_t1a_master_set() -> set:
    """BUG-222 RESOLVED-IMPLEMENTED Batch 117 2026-05-12 (owner-approved
    option B 2026-05-12): return the set of ALL tickers that have ever
    been in the T1a S&P 500 universe (current snapshot + historical
    members removed-during-window). Engine's `_build_liquid_universe`
    intersection logic uses this set to decide which tickers to
    PIT-filter against `get_sp500_constituents_pit(year_start)`. Tickers
    NOT in this set (T1 ETFs, T2 spinoffs/IPOs, T3 momentum names)
    bypass the PIT intersection and use OHLCV liquidity only.

    Returns empty set on CSV read failure so the engine falls back to
    no-PIT-filtering (current pre-Batch-117 behavior).
    """
    csv_path = UNIVERSE_DIR / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"
    if not csv_path.exists():
        legacy = UNIVERSE_DIR / "historical_membership.csv"
        if legacy.exists():
            csv_path = legacy
        else:
            logger.warning("BUG-222: T1a master CSV missing - returning empty set "
                           "(engine will skip PIT intersection)")
            return set()
    try:
        df = pd.read_csv(csv_path, comment='#')
        return set(df["Symbol"].drop_duplicates().tolist())
    except Exception as exc:
        logger.error("BUG-222: could not read T1a master CSV: %s", exc)
        return set()


def get_sp500_constituents_pit(as_of: date) -> list[str]:
    """
    PIT-correct S&P 500 constituents at `as_of` date (DEC-040 / DEC-477).

    Reads `Backtesting universe/historical_membership.csv` (B++ schema) and
    applies the PIT filter. Falls back to `Current Snapshot_SP500 Tickers_May 2026.csv` current snapshot
    if the historical file is missing.

    Pass 53 SCRAPE-COMPLETE: 614 rows from Wikipedia (124 events 2020-2026 +
    503 currently active). File renamed Pass 53 (commit pending) from
    `historical_membership.csv` to `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv`.
    """
    csv_path = UNIVERSE_DIR / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"
    # Backwards-compat fallback during transition
    if not csv_path.exists():
        legacy = UNIVERSE_DIR / "historical_membership.csv"
        if legacy.exists():
            csv_path = legacy
        else:
            logger.warning("T1a historical CSV missing  -  falling back to Current Snapshot_SP500 Tickers_May 2026.csv current snapshot")
            return get_sp500_constituents()
    try:
        df = pd.read_csv(csv_path, comment='#')
        active = _filter_pit(df, as_of)
        tickers = active["Symbol"].drop_duplicates().tolist()
        logger.info("PIT S&P 500 at %s: %d active members", as_of, len(tickers))
        return tickers
    except Exception as exc:
        logger.error("Could not read T1a historical CSV: %s", exc)
        return []


def get_ndx_constituents_pit(as_of: date) -> list[str]:
    """PIT-correct NASDAQ 100 (T1c) constituents at `as_of` (DEC-303 / DEC-483 T1c)."""
    csv_path = UNIVERSE_DIR / "Tier 1C Universe_NASDAQ-100 Tickers_Jan 2020 to May 2026.csv"
    if not csv_path.exists():
        return []
    try:
        df = pd.read_csv(csv_path, comment='#')
        active = _filter_pit(df, as_of)
        return active["Symbol"].drop_duplicates().tolist()
    except Exception as exc:
        logger.error("Could not read Tier 1C Universe_NASDAQ-100 Tickers_Jan 2020 to May 2026.csv: %s", exc)
        return []


def get_extended_universe_pit(as_of: date) -> list[str]:
    """PIT-correct Tier 2 (spinoffs + recent IPOs) constituents at `as_of` (DEC-103 / DEC-494)."""
    csv_path = UNIVERSE_DIR / "Tier 2 Universe_Spinoffs and Recent IPOs_Feb 2010 to May 2026.csv"
    if not csv_path.exists():
        return []
    try:
        df = pd.read_csv(csv_path, comment='#')
        if df.empty or "Symbol" not in df.columns:
            return []
        active = _filter_pit(df, as_of)
        return active["Symbol"].dropna().drop_duplicates().tolist()
    except Exception as exc:
        logger.error("Could not read Tier 2 Universe_Spinoffs and Recent IPOs_Feb 2010 to May 2026.csv: %s", exc)
        return []


def get_momentum_watchlist_pit(as_of: date) -> list[str]:
    """PIT-correct Tier 3 (momentum top 100 non-T1) constituents at `as_of` (DEC-104 / DEC-364 / DEC-496)."""
    csv_path = UNIVERSE_DIR / "Tier 3 Universe_Momentum Top-100_Jun 2022 to May 2026.csv"
    if not csv_path.exists():
        return []
    try:
        df = pd.read_csv(csv_path, comment='#')
        if df.empty or "Symbol" not in df.columns:
            return []
        active = _filter_pit(df, as_of)
        return active["Symbol"].dropna().drop_duplicates().tolist()
    except Exception as exc:
        logger.error("Could not read Tier 3 Universe_Momentum Top-100_Jun 2022 to May 2026.csv: %s", exc)
        return []


def get_master_universe() -> list[str]:
    """
    Return ALL ~1937 unique tickers from the Master Dedup CSV (DEC-504 / Pass 53).

    Reads `Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv`
    which contains the union of all 5 tiers (T1a + T1c + T1ETF + T2 + T3) with
    resolved_tier precedence applied. This is the Phase 1A-beta / 1B-alpha scope.

    Unlike `union_universe(as_of)` which returns PIT-active tickers for a single
    date, this returns EVERY ticker that was active in ANY tier at ANY point
    during the backtest window. The engine's existing PIT loaders handle per-day
    activation via `(added_date IS NULL OR added_date <= as_of) AND (removed_date
    IS NULL OR removed_date > as_of)` so passing the full set is safe.

    Phase 1A-beta (Batch 181 2026-05-15 owner-approved):
      - Replaces `config.UNIVERSE = SP50 + ETFS = 67 tickers` (legacy Phase 1A
        baseline scope) with the canonical 1937-ticker Master Dedup.
      - Test grid: 117 strategies x 1937 tickers x 17 exit methods ~ 3.85M cells.
      - Runtime estimate: 5-7 days single-threaded; 1-2 days with batch
        parallelization via scripts/generate_batch_splits.py.

    Source: per CHECKLIST #77 - canonical CSV path. CANONICAL_FACTS.md F-005.
    """
    csv_path = UNIVERSE_DIR / "Master Universe_Deduplicated_All Tiers_May 2026.csv"
    if not csv_path.exists():
        logger.error("Master Dedup CSV missing: %s", csv_path)
        return []
    try:
        df = pd.read_csv(csv_path, comment="#")
    except Exception as exc:
        logger.error("Master Dedup CSV read failed: %s", exc)
        return []
    col = "Symbol" if "Symbol" in df.columns else df.columns[0]
    tickers = sorted(df[col].dropna().astype(str).str.upper().str.strip().unique().tolist())
    logger.info("Master Universe (Phase 1A-beta scope): %d unique tickers loaded from %s",
                len(tickers), csv_path.name)
    return tickers


def union_universe(as_of: date, include_etfs: bool = True) -> list[str]:
    """
    Union of all 5 universe buckets at `as_of` (DEC-040 cross-tier loader).

    Returns deduplicated ticker list combining:
      T1a (S&P 500  -  historical_membership.csv PIT)
      T1c (NASDAQ 100 non-S&P  -  Tier 1C Universe_NASDAQ-100 Tickers_Jan 2020 to May 2026.csv PIT)
      T2  (spinoffs + recent IPOs  -  Tier 2 Universe_Spinoffs and Recent IPOs_Feb 2010 to May 2026.csv PIT)
      T3  (momentum top 100 non-T1  -  Tier 3 Universe_Momentum Top-100_Jun 2022 to May 2026.csv PIT)
      ETFs (Tier 1 ETFs  -  Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv, always-active)

    T1b (Russell 1000 non-S&P) deferred to Sprint 1 procurement (LSEG paywall).
    """
    members = set(get_sp500_constituents_pit(as_of))
    members |= set(get_ndx_constituents_pit(as_of))
    members |= set(get_extended_universe_pit(as_of))
    members |= set(get_momentum_watchlist_pit(as_of))
    if include_etfs:
        members |= set(get_etfs_full())
    return sorted(members)


# =============================================================================
# DEC-504 Pass 53 owner directive 2026-05-05  -  Multi-tier precedence resolver
# =============================================================================
# When a ticker is in multiple tiers PIT-active for the same date, T3 wins over
# T1 per owner directive: "If a ticker is in multiple tiers, rules of T3 should
# apply over T1." Generalized precedence (most-specific wins):
#
#   T3 (momentum) > T2 (spinoff/IPO) > T1c (NDX-non-SP) > T1a (S&P 500) > T1ETF
#
# Rationale: T3/T2 capture more-specific signal categories. If a ticker
# graduates into T1 from T3, the T3 momentum thesis is the more-recent + more-
# specific signal, so T3 rules apply (more permissive liquidity + history floors,
# T3 strategy roster, T3 position sizing).
#
# Scope of "rules apply" per Pass 53 owner Q1=Approve all:
#   (a) Liquidity floor  -  T3=$5M ADV, T2=$5M, T1c=$10M, T1a=$10M, T1ETF=N/A
#   (b) History minimum  -  T3=60d, T2=20d (with LIMITED_HISTORY flag), T1c=250d, T1a=250d
#   (c) Position sizing  -  tier-specific tier->size map (Master Dedup uses this)
#   (d) Strategy roster  -  tier-eligible strategies (e.g., spinoff strategies T2-only,
#       momentum strategies T3+T1)
#   (e) Refresh cadence  -  T3 monthly, T2 monthly, T1 quarterly (ops-level, not runtime)

# Tier precedence order  -  index 0 = highest precedence
_TIER_PRECEDENCE = ["T3", "T2", "T1c", "T1a", "T1ETF"]

# Tier-specific parameter dicts (DEC-504 owner-approved scope a-d)
TIER_PARAMS = {
    "T3": {
        "min_avg_dollar_volume_usd": 5_000_000,   # $5M ADV (DEC-321/366)
        "min_history_days": 60,
        "min_market_cap_m": 300,                  # $300M
        "position_size_tier": "T3",
        "refresh_cadence": "monthly",
    },
    "T2": {
        "min_avg_dollar_volume_usd": 5_000_000,
        "min_history_days": 20,                   # LIMITED_HISTORY-flagged strategies respect this
        "min_market_cap_m": 2_000,                # $2B (DEC-103)
        "position_size_tier": "T2",
        "refresh_cadence": "monthly",
    },
    "T1c": {
        "min_avg_dollar_volume_usd": 10_000_000,  # $10M ADV
        "min_history_days": 250,
        "min_market_cap_m": 100,                  # $100M
        "position_size_tier": "T1c",
        "refresh_cadence": "quarterly",
    },
    "T1a": {
        "min_avg_dollar_volume_usd": 10_000_000,
        "min_history_days": 250,
        "min_market_cap_m": 100,
        "position_size_tier": "T1a",
        "refresh_cadence": "quarterly",
    },
    "T1ETF": {
        "min_avg_dollar_volume_usd": 5_000_000,
        "min_history_days": 250,
        "min_market_cap_m": 0,                    # ETFs N/A
        "position_size_tier": "T1ETF",
        "refresh_cadence": "static",
    },
}


def _ticker_in_tier(ticker: str, tier: str, as_of: date) -> bool:
    """Return True if ticker is PIT-active in the named tier on `as_of`."""
    t = ticker.upper()
    if tier == "T3":
        return t in set(get_momentum_watchlist_pit(as_of))
    if tier == "T2":
        return t in set(get_extended_universe_pit(as_of))
    if tier == "T1c":
        return t in set(get_ndx_constituents_pit(as_of))
    if tier == "T1a":
        return t in set(get_sp500_constituents_pit(as_of))
    if tier == "T1ETF":
        return t in set(get_etfs_full())
    raise ValueError(f"Unknown tier: {tier}")


def resolve_tier_precedence(ticker: str, as_of: date) -> Optional[str]:
    """
    Return the most-specific PIT-active tier for `ticker` on `as_of`.

    Precedence order (DEC-504 Pass 53): T3 > T2 > T1c > T1a > T1ETF.
    Returns None if ticker not PIT-active in any tier on the given date.

    Example:
      VST joined S&P 500 on 2024-05-08 AND was T3 momentum top-100 with
      added_date=2024-05-01. For as_of=2024-06-01:
        - T1a-active: True
        - T3-active: True (removed 2024-06-03)
        - resolve_tier_precedence('VST', 2024-06-01) -> 'T3' (T3 wins)

      For as_of=2024-07-01:
        - T1a-active: True
        - T3-active: False (removed 2024-06-03)
        - resolve_tier_precedence('VST', 2024-07-01) -> 'T1a'
    """
    for tier in _TIER_PRECEDENCE:
        if _ticker_in_tier(ticker, tier, as_of):
            return tier
    return None


def get_tier_params(ticker: str, as_of: date) -> Optional[dict]:
    """
    Return the tier-specific parameter dict for `ticker` on `as_of` per DEC-504
    precedence resolution. Returns None if ticker not PIT-active in any tier.

    Use this in place of hardcoded T1/T2/T3 parameter lookups so multi-tier
    tickers get T3-over-T1 rules per owner directive.
    """
    tier = resolve_tier_precedence(ticker, as_of)
    if tier is None:
        return None
    return TIER_PARAMS[tier].copy()


def apply_liquidity_filter(
    tickers: list[str],
    ohlcv_dict: dict[str, pd.DataFrame],
    info_dict: dict[str, dict],
    as_of: date,
    min_price: float = None,
    min_avg_volume: float = None,
    min_market_cap_m: float = None,
) -> tuple[list[str], dict[str, str]]:
    """
    Apply liquidity filters to a list of tickers.
    Returns (passing_tickers, {ticker: fail_reason}).

    Uses config defaults if parameters not specified.
    """
    min_price        = min_price        or LIQUIDITY["min_price"]
    min_avg_volume   = min_avg_volume   or LIQUIDITY["min_avg_volume"]
    min_market_cap_m = min_market_cap_m or LIQUIDITY["min_market_cap_m"]

    passing = []
    failing = {}

    for ticker in tickers:
        df = ohlcv_dict.get(ticker)
        if df is None or df.empty:
            failing[ticker] = "no_price_data"
            continue

        # Slice to as_of
        sliced = df[df.index.date <= as_of]
        if len(sliced) < 20:
            failing[ticker] = "insufficient_history"
            continue

        # Price filter
        last_close = float(sliced["close"].iloc[-1])
        if last_close < min_price:
            failing[ticker] = f"price_${last_close:.2f}_below_${min_price}"
            continue

        # Volume filter  -  20-day average
        avg_vol = float(sliced["volume"].tail(20).mean())
        if avg_vol < min_avg_volume:
            failing[ticker] = f"avg_vol_{int(avg_vol):,}_below_{int(min_avg_volume):,}"
            continue

        # DEC-321 + DEC-392 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 43
        # 2026-05-11 (owner-approved Path C). Liquidity filter FAIL-CLOSED on
        # missing market_cap data. Previously skipped check silently when
        # data unavailable (rate-limit graceful fallback) which let illiquid
        # micro-caps slip through. Now: missing/zero market_cap fails the
        # filter EXCEPT for ETFs (min_market_cap_m == 0, intentional bypass).
        info = info_dict.get(ticker, {})
        mkt_cap_raw = info.get("market_cap") or 0
        mkt_cap_m = mkt_cap_raw / 1_000_000
        if min_market_cap_m > 0:
            # Fail-closed: missing or zero market cap rejects the ticker
            if mkt_cap_m <= 0:
                failing[ticker] = f"mkt_cap_missing_fail_closed_dec321"
                continue
            if mkt_cap_m < min_market_cap_m:
                failing[ticker] = f"mkt_cap_${mkt_cap_m:.0f}M_below_${min_market_cap_m:.0f}M"
                continue
        # ETFs: min_market_cap_m == 0 -> skip check entirely (intentional)

        passing.append(ticker)

    logger.info(
        "Liquidity filter: %d/%d passed (%.0f%% pass rate)",
        len(passing), len(tickers),
        len(passing) / len(tickers) * 100 if tickers else 0,
    )
    return passing, failing


def get_sector_map(tickers: list[str], info_dict: dict[str, dict] = None) -> dict[str, str]:
    """
    Return {ticker: sector} mapping.
    Reads from Current Snapshot_SP500 Tickers_May 2026.csv first (fast, no network).
    Falls back to info_dict if ticker not in CSV (e.g. ETFs).
    """
    csv_path = UNIVERSE_DIR / "Current Snapshot_SP500 Tickers_May 2026.csv"
    sector_map = {}

    # Load from CSV
    try:
        df = pd.read_csv(csv_path, comment='#')
        df = df.drop_duplicates(subset=["Symbol"])
        sector_map = dict(zip(df["Symbol"], df["Sector"]))
    except Exception:
        pass

    # ETF sector labels
    etf_sectors = {
        "SPY": "Broad Market", "QQQ": "Technology", "IWM": "Small Cap",
        "DIA": "Broad Market", "VTI": "Broad Market", "XLK": "Information Technology",
        "XLF": "Financials", "XLE": "Energy", "XLV": "Health Care",
        "XLI": "Industrials", "XLY": "Consumer Discretionary", "XLP": "Consumer Staples",
        "XLU": "Utilities", "XLB": "Materials", "XLRE": "Real Estate",
        "VXX": "Volatility", "TLT": "Fixed Income", "HYG": "Fixed Income",
        "LQD": "Fixed Income", "GLD": "Commodities", "SLV": "Commodities",
        "GDX": "Commodities", "USO": "Commodities", "EEM": "Emerging Markets",
        "EFA": "International",
    }
    sector_map.update(etf_sectors)

    # Fill remaining from info_dict if provided
    result = {}
    for t in tickers:
        if t in sector_map:
            result[t] = sector_map[t]
        elif info_dict and t in info_dict:
            result[t] = info_dict[t].get("sector", "Unknown")
        else:
            result[t] = "Unknown"
    return result


# DEC-323 + DEC-394 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 46
# 2026-05-11 (owner-approved Path C). PIT-correct sector lookup using
# Backtesting universe/sector_history.csv (major GICS reclassifications).
# Falls back to current-snapshot sector for tickers without historical
# reclassification entries.
#
# Major events covered (see CSV for full list):
# - 2018-09-24: META/GOOGL/GOOG (IT -> Comms), NFLX/DIS/CMCSA (CD -> Comms),
#   T/VZ (Telecom -> Comms, renamed Communication Services sector)
# - 2023-03-17: V/MA (IT -> Financials)
_SECTOR_HISTORY_CACHE: Optional[pd.DataFrame] = None


def _load_sector_history() -> pd.DataFrame:
    """Load sector_history.csv at module level. Cached after first call."""
    global _SECTOR_HISTORY_CACHE
    if _SECTOR_HISTORY_CACHE is not None:
        return _SECTOR_HISTORY_CACHE
    csv_path = UNIVERSE_DIR / "sector_history.csv"
    if not csv_path.exists():
        _SECTOR_HISTORY_CACHE = pd.DataFrame(columns=["Symbol", "Sector", "added_date", "removed_date"])
        return _SECTOR_HISTORY_CACHE
    try:
        df = pd.read_csv(csv_path, comment='#')
        # Ensure dates are pandas datetime (NaN for blank)
        df["added_date"] = pd.to_datetime(df["added_date"], errors="coerce")
        df["removed_date"] = pd.to_datetime(df["removed_date"], errors="coerce")
        _SECTOR_HISTORY_CACHE = df
    except Exception as exc:
        logger.warning("sector_history.csv read failed: %s", exc)
        _SECTOR_HISTORY_CACHE = pd.DataFrame(columns=["Symbol", "Sector", "added_date", "removed_date"])
    return _SECTOR_HISTORY_CACHE


def get_sector_pit(ticker: str, as_of: date, fallback: Optional[str] = None) -> str:
    """PIT-correct sector for `ticker` at `as_of` per DEC-323.

    Lookup priority:
      1. sector_history.csv entry where added_date <= as_of < (removed_date OR inf)
      2. Fallback to current-snapshot sector (caller-supplied or get_sector_map)
      3. "Unknown" if no source available

    Inputs:
      ticker: stock symbol
      as_of: date to resolve sector for
      fallback: optional current-snapshot sector (typically from get_sector_map);
                used when ticker has no historical entries

    Returns sector string.
    """
    df = _load_sector_history()
    if df.empty:
        return fallback or "Unknown"
    rows = df[df["Symbol"] == ticker]
    if rows.empty:
        return fallback or "Unknown"
    as_of_ts = pd.Timestamp(as_of)
    # PIT filter: added_date <= as_of AND (removed_date IS NULL OR removed_date > as_of)
    left_ok = rows["added_date"].isna() | (rows["added_date"] <= as_of_ts)
    right_ok = rows["removed_date"].isna() | (rows["removed_date"] > as_of_ts)
    active = rows[left_ok & right_ok]
    if active.empty:
        return fallback or "Unknown"
    # Most-recent-active wins (highest added_date among active rows)
    sorted_active = active.sort_values("added_date", na_position="first")
    return str(sorted_active.iloc[-1]["Sector"])


def get_classification_change_signals(
    ticker: str,
    as_of: date,
    lookback_days: int = 180,  # B1142: was 90 (Council 254 LOOSEN per Turn 9 - widened for structural rarity)
) -> dict:
    """Wave 3 (Batch 332): detect recent GICS classification changes for ticker.

    Reads sector_history.csv (DEC-323) — same source as get_sector_pit, but
    INSTEAD of returning the active sector, returns metadata about whether
    the ticker has experienced a sector reclassification within the
    `lookback_days` window leading up to `as_of`.

    Returns dict with keys (all keys absent when no qualifying change):
      classification_changed_recent:   bool
      days_since_classification_change: int (None if no change)
      new_sector:                       str (sector ticker moved INTO)
      prior_sector:                     str (sector ticker moved OUT OF)
      classification_change_to_tech:    bool (moved INTO IT / Comms / Health)
      classification_change_to_defensive: bool (moved INTO Materials /
                                          Utilities / Real Estate / Cons Staples)

    Literature: Chen-Chen 2010 (industry classification + price discovery),
    Brogaard-Heath-Saadi 2019 (industry classification + analyst forecasts).

    No-op (returns empty dict) when sector_history.csv missing OR ticker
    has no qualifying change row in the lookback window.
    """
    df = _load_sector_history()
    if df.empty:
        return {}
    rows = df[df["Symbol"] == ticker]
    if rows.empty:
        return {}
    as_of_ts = pd.Timestamp(as_of)
    cutoff = as_of_ts - pd.Timedelta(days=lookback_days)
    # Find rows where the ticker MOVED INTO a new sector recently:
    # added_date is in (cutoff, as_of] AND added_date is not NaT.
    moved_in = rows[
        rows["added_date"].notna()
        & (rows["added_date"] > cutoff)
        & (rows["added_date"] <= as_of_ts)
    ]
    if moved_in.empty:
        return {}
    # Most-recent move wins
    latest = moved_in.sort_values("added_date").iloc[-1]
    new_sec = str(latest["Sector"])
    change_ts = pd.Timestamp(latest["added_date"])
    days_since = int((as_of_ts - change_ts).days)
    # Prior sector: the row where this ticker was REMOVED on the same date
    # (the OUT-OF side of the reclassification).
    prior_rows = rows[
        rows["removed_date"].notna()
        & (rows["removed_date"] == change_ts)
    ]
    prior_sec = (
        str(prior_rows.iloc[0]["Sector"])
        if not prior_rows.empty
        else "Unknown"
    )
    # Sector buckets per GICS taxonomy
    growth_sectors = {"Information Technology", "Communication Services", "Health Care"}
    defensive_sectors = {"Materials", "Utilities", "Real Estate", "Consumer Staples"}
    return {
        "classification_changed_recent":      True,
        "days_since_classification_change":   days_since,
        "new_sector":                         new_sec,
        "prior_sector":                       prior_sec,
        "classification_change_to_tech":      new_sec in growth_sectors,
        "classification_change_to_defensive": new_sec in defensive_sectors,
        # Batch 335 (2026-05-25): symmetric from_tech flag for short strategies
        # firing on ticker moving OUT of a growth sector (e.g., V/MA 2023
        # IT -> Financials). Inverse-rating signal per Chen-Chen 2010.
        "classification_change_from_tech":    prior_sec in growth_sectors,
    }


def get_correlation_matrix(
    ohlcv_dict: dict[str, pd.DataFrame],
    as_of: date,
    lookback_days: int = 60,
) -> pd.DataFrame:
    """
    Compute return correlation matrix for all instruments.
    Used by correlation filter to prevent over-concentrated positions.
    """
    start = as_of - timedelta(days=lookback_days + 5)
    returns = {}
    for ticker, df in ohlcv_dict.items():
        sliced = df[(df.index.date >= start) & (df.index.date <= as_of)]
        if len(sliced) >= 20:
            returns[ticker] = sliced["close"].pct_change().dropna()

    if not returns:
        return pd.DataFrame()

    ret_df = pd.DataFrame(returns).dropna(how="all")
    return ret_df.corr()




def get_extended_universe() -> list[str]:
    """
    Load Tier 2 extended universe  -  spinoffs, large non-S&P stocks.
    Refreshed monthly via scripts/refresh_extended_universe.py (Stage 3+ only).
    Empty CSV = Tier 2 not yet populated (Phase 1B/1C/1D use Tier 1 only).
    """
    csv_path = UNIVERSE_DIR / "Tier 2 Universe_Spinoffs and Recent IPOs_Feb 2010 to May 2026.csv"
    try:
        df = pd.read_csv(csv_path, comment='#')
        if df.empty:
            return []
        tickers = df["Symbol"].drop_duplicates().tolist()
        logger.info("Loaded %d Tier 2 extended universe tickers", len(tickers))
        return tickers
    except Exception as exc:
        logger.debug("Tier 2 Universe_Spinoffs and Recent IPOs_Feb 2010 to May 2026.csv not found or empty: %s", exc)
        return []


def get_momentum_watchlist() -> list[str]:
    """
    Load Tier 3 momentum watchlist  -  top non-S&P momentum names.
    Refreshed monthly via scripts/build_momentum_watchlist.py (Stage 3+ only).
    For backtesting: fixed at run start (static, no look-ahead).
    For live: recomputed monthly, updated at month-end.
    Empty CSV = Tier 3 not yet populated.
    """
    csv_path = UNIVERSE_DIR / "Tier 3 Universe_Momentum Top-100_Jun 2022 to May 2026.csv"
    try:
        df = pd.read_csv(csv_path, comment='#')
        if df.empty:
            return []
        tickers = df["Symbol"].drop_duplicates().tolist()
        logger.info("Loaded %d Tier 3 momentum watchlist tickers", len(tickers))
        return tickers
    except Exception as exc:
        logger.debug("Tier 3 Universe_Momentum Top-100_Jun 2022 to May 2026.csv not found or empty: %s", exc)
        return []


def get_full_live_universe() -> list[str]:
    """
    Build full live universe for Stage 3+: Tier 1 + Tier 2 + Tier 3 + ETFs.
    For backtesting (Phase 1B/1C/1D): use build_phase1b_universe() instead.
    
    Universe tiers:
      Tier 1  -  S&P 500 (~500 tickers, quarterly refresh)
      Tier 2  -  Extended: spinoffs, large non-S&P (~50-100 tickers, monthly refresh)
      Tier 3  -  Momentum watchlist: top non-S&P momentum (~50 tickers, monthly refresh)
      ETFs    -  Sector, bond, commodity, volatility ETFs (~25 tickers, static)
    """
    tier1  = get_sp500_constituents(500)
    tier2  = get_extended_universe()
    tier3  = get_momentum_watchlist()
    etfs   = ETFS_FULL

    # Deduplicate, preserve tier priority order
    full = list(dict.fromkeys(tier1 + tier2 + tier3 + etfs))
    logger.info(
        "Full live universe: %d tickers (T1=%d T2=%d T3=%d ETF=%d)",
        len(full), len(tier1), len(tier2), len(tier3), len(etfs)
    )
    return full

def build_phase1b_universe(
    ohlcv_dict: dict[str, pd.DataFrame],
    info_dict:  dict[str, dict],
    as_of: date,
) -> tuple[list[str], dict[str, str]]:
    """
    Build the full Phase 1B universe: filtered S&P 500 + all ETFs.
    Returns (passing_tickers, fail_reasons).
    """
    sp500 = get_sp500_constituents(500)
    all_tickers = list(dict.fromkeys(sp500 + ETFS_FULL))  # deduplicated, order preserved
    return apply_liquidity_filter(all_tickers, ohlcv_dict, info_dict, as_of)


def _polygon_reference_lookup(ticker: str) -> dict:
    """Batch 301: read market_cap / list_date / sic_description / exchange
    from data_prefetch/polygon/reference/{TICKER}.parquet (canonical source
    per Sprint 0A Polygon reference prefetch).

    Returns empty dict if parquet missing or unreadable. Caller defaults the
    rest of the info_cache entry. Replaces the `market_cap: 0` placeholder
    that DEC-497 D4 left behind (2026-05-06) and which BUG-238 fail-closed
    (2026-05-12) silently weaponized into a 96.5% universe rejection.
    """
    from pathlib import Path as _P
    ref_path = (_P(__file__).resolve().parent.parent.parent
                / "data_prefetch" / "polygon" / "reference" / f"{ticker}.parquet")
    if not ref_path.exists():
        return {}
    try:
        rdf = pd.read_parquet(ref_path)
    except Exception:
        return {}
    if rdf.empty:
        return {}
    row = rdf.iloc[0]
    out = {}
    mc = row.get("market_cap")
    if mc is not None and not pd.isna(mc):
        out["market_cap"] = float(mc)
    ld = row.get("list_date")
    if ld is not None and not (isinstance(ld, float) and pd.isna(ld)):
        out["ipo_date"] = str(ld)
    sic = row.get("sic_description")
    if sic is not None and not (isinstance(sic, float) and pd.isna(sic)):
        out["industry"] = str(sic)
    exch = row.get("primary_exchange")
    if exch is not None and not (isinstance(exch, float) and pd.isna(exch)):
        out["exchange"] = str(exch)
    return out


def fetch_info_bulk(
    tickers: list[str],
    delay: float = 0.2,
    cache_file: str = "data/cache/info_cache.json",
) -> dict[str, dict]:
    """
    Fetch company info (sector, market cap, IPO date) for all tickers.
    Uses a simple JSON cache to avoid re-fetching on every run.

    Batch 301 (BUG-NEW 2026-05-21): wired to Polygon reference parquets at
    data_prefetch/polygon/reference/{TICKER}.parquet for market_cap /
    ipo_date / industry / exchange. Entries with market_cap<=0 are treated
    as stale and re-fetched (self-heals the 1871 zero-mcap entries left
    over by the DEC-497 D4 + BUG-238 silent-gap interaction).
    """
    import json
    from pathlib import Path

    cache_path = Path(cache_file)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing cache
    cached = {}
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text())
        except Exception:
            cached = {}

    # Batch 301: refetch stale (market_cap<=0) entries in addition to missing
    # tickers. The DEC-497 D4 transition left 1871 entries with mcap=0; this
    # filter heals them on the next fetch_info_bulk() call.
    def _needs_fetch(t: str) -> bool:
        if t not in cached:
            return True
        v = cached.get(t) or {}
        mc = v.get("market_cap", 0) or 0
        return mc <= 0
    to_fetch = [t for t in tickers if _needs_fetch(t)]
    if to_fetch:
        logger.info("Fetching info for %d tickers (incl. mcap=0 refetch)...", len(to_fetch))

    # Pass 53 Batch 13 sub-task 6 (DEC-497 D4 yfinance HARD CUT 2026-05-06):
    # yfinance.Ticker.info removed from runtime. Sector resolution via
    # canonical CSV at "Backtesting universe/Master Universe_Deduplicated_All
    # Tiers_May 2026.csv" (Pass 53 Master Dedup, 18-classifier sectors per
    # DEC-499). Batch 301 (2026-05-21) wires market_cap / list_date /
    # sic_description / primary_exchange from Polygon reference parquets.
    try:
        from backtest.data.universe import UNIVERSE_DIR  # type: ignore
    except ImportError:
        UNIVERSE_DIR = Path(__file__).parent.parent.parent / "Backtesting universe"
    master_path = UNIVERSE_DIR / "Master Universe_Deduplicated_All Tiers_May 2026.csv"
    master_lookup = {}
    if master_path.exists():
        try:
            text = ''.join(l for l in master_path.read_text(encoding='utf-8').splitlines(keepends=True) if not l.startswith('#'))
            import io as _io
            mdf = pd.read_csv(_io.StringIO(text))
            master_lookup = {
                str(r["Symbol"]).upper(): {
                    "name": r.get("Company", "") or "",
                    "sector": r.get("Sector", "Unknown") or "Unknown",
                }
                for _, r in mdf.iterrows()
            }
        except Exception as exc:
            logger.debug("fetch_info_bulk master lookup failed: %s", exc)

    for i, ticker in enumerate(to_fetch):
        m = master_lookup.get(ticker.upper(), {})
        # Batch 301: hydrate from Polygon reference; falls back to defaults
        # when the parquet is absent (delisted names beyond Polygon retention).
        ref = _polygon_reference_lookup(ticker)
        cached[ticker] = {
            "name":       m.get("name", ticker) or ticker,
            "sector":     m.get("sector", "Unknown"),
            "industry":   ref.get("industry", "Unknown"),
            "market_cap": ref.get("market_cap", 0),
            "exchange":   ref.get("exchange", ""),
            "ipo_date":   ref.get("ipo_date", None),
        }
        # Local parquet read is fast; the historical 0.2s delay was a
        # yfinance rate-limit guard. Keep delay opt-in only for very large
        # refetch sweeps (Phase 1A-beta full 1937 = ~6 min at 0.2s; skip).
        if delay > 0 and i % 100 == 99:
            time.sleep(delay)

    # Save updated cache
    try:
        # File lock prevents race conditions in parallel batch runs
        import filelock
        lock_path = str(cache_path) + ".lock"
        try:
            with filelock.FileLock(lock_path, timeout=30):
                # Re-read before writing to merge any updates from other batches
                existing = {}
                if cache_path.exists():
                    try:
                        existing = json.loads(cache_path.read_text())
                    except Exception:
                        existing = {}
                existing.update(cached)
                cache_path.write_text(json.dumps(existing, default=str, indent=2))
        except Exception:
            cache_path.write_text(json.dumps(cached, default=str, indent=2))
    except Exception as exc:
        logger.warning("Info cache write failed: %s", exc)

    return {t: cached.get(t, {"sector": "Unknown", "market_cap": 0}) for t in tickers}
