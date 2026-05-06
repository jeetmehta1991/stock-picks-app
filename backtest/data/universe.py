"""
data/universe.py — Instrument manager.

Handles:
  - Loading S&P 500 constituent list from committed static CSV (Current Snapshot_SP500 Tickers_May 2026.csv)
    The CSV is refreshed quarterly via slickcharts.com (or S&P press releases).
    See LEARNINGS L88: Wikipedia is unreliable as a runtime data source — the
    static CSV pattern is the correct approach.
  - Applying liquidity filters to reduce ~500 → ~380-420 tradeable names
  - Appending new instruments to existing universe without re-fetching
  - Sector breakdown for correlation analysis

Universe tiers:
  Phase 1A: SP50 + 17 ETFs = 67 instruments (hardcoded — pipeline validation)
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
import yfinance as yf

from backtest.config import SP50, ETFS, LIQUIDITY

logger = logging.getLogger(__name__)

# Universe CSVs moved to top-level "Backtesting universe/" folder (Pass 53 owner directive)
# for repo-wide visibility. Path resolves from backtest/data/universe.py → repo root.
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

    Per DEC-494 (Pass 53 owner-approved Sprint 1) — ETFs are now declared in
    a CSV file alongside T1a/T1b/T1c membership files for consistency.
    No leveraged ETFs included — volatility decay invalidates backtest results.

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


# Computed at module import time — preserves legacy `from universe import ETFS_FULL`
# callers. CSV-backed; update Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv to change the list.
ETFS_FULL = get_etfs_full()


def get_sp500_constituents(max_tickers: int | None = None) -> list[str]:
    """
    Load S&P 500 constituent list from the committed CSV file.

    Uses Backtesting universe/Current Snapshot_SP500 Tickers_May 2026.csv — a maintained static file
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
        # Remove duplicates by Symbol (defensive — file should already be unique by symbol)
        tickers = df["Symbol"].drop_duplicates().tolist()
        logger.info("Loaded %d S&P 500 constituents from Current Snapshot_SP500 Tickers_May 2026.csv", len(tickers))
        return tickers[:max_tickers] if max_tickers else tickers
    except Exception as exc:
        logger.error("Could not read Current Snapshot_SP500 Tickers_May 2026.csv: %s", exc)
        return []


# ── Pass 53 PIT loader (DEC-040 / DEC-477) ────────────────────────────────────
# B++ schema universe CSVs use `added_date` / `removed_date` columns; PIT filter
# resolves the active member set at any `as_of` date without survivorship bias.
#
# PIT FILTER: (added_date IS NULL OR added_date <= as_of)
#         AND (removed_date IS NULL OR removed_date > as_of)
#
# Multi-period rows (ticker re-entry — e.g., NDX WDC/CSGP/TTWO/SPLK) are
# handled via standard pandas OR semantics: each row is filtered independently;
# union of passing rows is the active set at `as_of`.

def _filter_pit(df: pd.DataFrame, as_of: date) -> pd.DataFrame:
    """
    Apply B++ PIT filter to a DataFrame with `added_date` and `removed_date` columns.
    Returns rows active at `as_of`.
    """
    if "added_date" not in df.columns or "removed_date" not in df.columns:
        # File predates B++ migration — treat all rows as active (current snapshot semantics)
        return df

    as_of_ts = pd.Timestamp(as_of)
    added = pd.to_datetime(df["added_date"], errors="coerce")
    removed = pd.to_datetime(df["removed_date"], errors="coerce")
    # NULL added_date → "in index prior to mapping window" → always passes left side
    # NULL removed_date → "currently active" → always passes right side
    left_ok = added.isna() | (added <= as_of_ts)
    right_ok = removed.isna() | (removed > as_of_ts)
    return df[left_ok & right_ok]


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
            logger.warning("T1a historical CSV missing — falling back to Current Snapshot_SP500 Tickers_May 2026.csv current snapshot")
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


def union_universe(as_of: date, include_etfs: bool = True) -> list[str]:
    """
    Union of all 5 universe buckets at `as_of` (DEC-040 cross-tier loader).

    Returns deduplicated ticker list combining:
      T1a (S&P 500 — historical_membership.csv PIT)
      T1c (NASDAQ 100 non-S&P — Tier 1C Universe_NASDAQ-100 Tickers_Jan 2020 to May 2026.csv PIT)
      T2  (spinoffs + recent IPOs — Tier 2 Universe_Spinoffs and Recent IPOs_Feb 2010 to May 2026.csv PIT)
      T3  (momentum top 100 non-T1 — Tier 3 Universe_Momentum Top-100_Jun 2022 to May 2026.csv PIT)
      ETFs (Tier 1 ETFs — Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv, always-active)

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
# DEC-504 Pass 53 owner directive 2026-05-05 — Multi-tier precedence resolver
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
#   (a) Liquidity floor — T3=$5M ADV, T2=$5M, T1c=$10M, T1a=$10M, T1ETF=N/A
#   (b) History minimum — T3=60d, T2=20d (with LIMITED_HISTORY flag), T1c=250d, T1a=250d
#   (c) Position sizing — tier-specific tier→size map (Master Dedup uses this)
#   (d) Strategy roster — tier-eligible strategies (e.g., spinoff strategies T2-only,
#       momentum strategies T3+T1)
#   (e) Refresh cadence — T3 monthly, T2 monthly, T1 quarterly (ops-level, not runtime)

# Tier precedence order — index 0 = highest precedence
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
        - resolve_tier_precedence('VST', 2024-06-01) → 'T3' (T3 wins)

      For as_of=2024-07-01:
        - T1a-active: True
        - T3-active: False (removed 2024-06-03)
        - resolve_tier_precedence('VST', 2024-07-01) → 'T1a'
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

        # Volume filter — 20-day average
        avg_vol = float(sliced["volume"].tail(20).mean())
        if avg_vol < min_avg_volume:
            failing[ticker] = f"avg_vol_{int(avg_vol):,}_below_{int(min_avg_volume):,}"
            continue

        # Market cap — skip check if data unavailable (rate limit graceful fallback)
        info = info_dict.get(ticker, {})
        mkt_cap_m = (info.get("market_cap") or 0) / 1_000_000
        if mkt_cap_m > 0 and mkt_cap_m < min_market_cap_m:
            failing[ticker] = f"mkt_cap_${mkt_cap_m:.0f}M_below_${min_market_cap_m:.0f}M"
            continue

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
    Load Tier 2 extended universe — spinoffs, large non-S&P stocks.
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
    Load Tier 3 momentum watchlist — top non-S&P momentum names.
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
      Tier 1 — S&P 500 (~500 tickers, quarterly refresh)
      Tier 2 — Extended: spinoffs, large non-S&P (~50-100 tickers, monthly refresh)
      Tier 3 — Momentum watchlist: top non-S&P momentum (~50 tickers, monthly refresh)
      ETFs   — Sector, bond, commodity, volatility ETFs (~25 tickers, static)
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


def fetch_info_bulk(
    tickers: list[str],
    delay: float = 0.2,
    cache_file: str = "data/cache/info_cache.json",
) -> dict[str, dict]:
    """
    Fetch company info (sector, market cap, IPO date) for all tickers.
    Uses a simple JSON cache to avoid re-fetching on every run.
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

    to_fetch = [t for t in tickers if t not in cached]
    if to_fetch:
        logger.info("Fetching info for %d new tickers...", len(to_fetch))

    for i, ticker in enumerate(to_fetch):
        if i > 0 and i % 20 == 0:
            time.sleep(2)
        try:
            info = yf.Ticker(ticker).info
            cached[ticker] = {
                "name":       info.get("longName", ticker),
                "sector":     info.get("sector", "Unknown"),
                "industry":   info.get("industry", "Unknown"),
                "market_cap": info.get("marketCap", 0) or 0,
                "exchange":   info.get("exchange", ""),
                "ipo_date":   info.get("firstTradeDateEpochUtc"),
            }
        except Exception as exc:
            cached[ticker] = {
                "name": ticker, "sector": "Unknown",
                "industry": "Unknown", "market_cap": 0,
                "exchange": "", "ipo_date": None,
            }
            logger.debug("fetch_info(%s): %s", ticker, exc)
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
