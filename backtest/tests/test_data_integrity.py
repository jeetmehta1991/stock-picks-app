"""Data-integrity test layer (DEC-591 / CHECKLIST #72 / L148).

Implements DEC-503 test pyramid type #7 - schema validation, PIT semantics,
completeness gates - by scanning the LIVE cache (not mocked fixtures).

7 minimum tests; suite extends as new data sources are added.

PASS-gate: required before any DEC marks RESOLVED-IMPLEMENTED OR phase entry.
"""

import io
import os
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OHLCV_DIR = REPO_ROOT / "backtest" / "data" / "cache" / "ohlcv"
PREFETCH_DIR = REPO_ROOT / "data_prefetch"
UNIVERSE_CSV = (
    REPO_ROOT
    / "Backtesting universe"
    / "Master Universe_Deduplicated_All Tiers_May 2026.csv"
)

REQUIRED_TICKERS = {
    "SPY",          # broad-market benchmark
    "VIXY",         # volatility ETF (acceptable VIX proxy)
    "XLB", "XLE", "XLF", "XLI", "XLK",
    "XLP", "XLRE", "XLU", "XLV", "XLY",
    "XLC",          # Communication Services (post-2018)
}

VIX_PROXIES = {"VIXCLS", "^VIX", "VIX", "VIXY", "VXX"}

CUMULATIVE_SNAPSHOT_SOURCES = {
    # source -> (path, min_unique_dates required)
    # Apewisdom relaxed per DEC-592 (forward-only accumulator; historical API not available)
    "apewisdom": (PREFETCH_DIR / "apewisdom" / "global.parquet", 1),
    "aaii": (PREFETCH_DIR / "aaii" / "weekly_sentiment.parquet", 30),
    "cnn_fg": (PREFETCH_DIR / "cnn_fg" / "daily.parquet", 30),
}

CROSS_SOURCE_COVERAGE_TARGETS = {
    "ohlcv":            (OHLCV_DIR, 0.99),
    "polygon_news":     (PREFETCH_DIR / "polygon" / "news", 0.95),
    "polygon_events":   (PREFETCH_DIR / "polygon" / "events", 0.85),
    "polygon_financials": (PREFETCH_DIR / "polygon" / "financials", 0.85),
    "sec_edgar_4":      (PREFETCH_DIR / "sec_edgar" / "4", 0.75),
    "sec_edgar_8K":     (PREFETCH_DIR / "sec_edgar" / "8_K", 0.75),
}

TIER_PARAM_KEYS = {
    "min_avg_dollar_volume_usd",  # was C5 expectation "liquidity_floor_adv" - corrected post-Pass-53 audit
    "min_history_days",
    "min_market_cap_m",
    "position_size_tier",
    "refresh_cadence",
}

TIERS_REQUIRED = {"T1a", "T1c", "T1ETF", "T2", "T3"}


def _load_universe():
    if not UNIVERSE_CSV.exists():
        pytest.skip(f"Master Dedup CSV missing at {UNIVERSE_CSV}")
    text = "".join(
        line for line in UNIVERSE_CSV.read_text(encoding="utf-8").splitlines(keepends=True)
        if not line.startswith("#")
    )
    df = pd.read_csv(io.StringIO(text))
    return set(df["Symbol"].dropna().astype(str).str.upper())


def _load_active_tickers():
    """Subset of universe that is currently_active in any tier (Master Dedup col)."""
    if not UNIVERSE_CSV.exists():
        return set()
    text = "".join(
        line for line in UNIVERSE_CSV.read_text(encoding="utf-8").splitlines(keepends=True)
        if not line.startswith("#")
    )
    df = pd.read_csv(io.StringIO(text))
    active = df[df["currently_active"].astype(str).str.lower() == "true"]
    return set(active["Symbol"].dropna().astype(str).str.upper())


def _list_parquet(d):
    if not d.exists():
        return set()
    return {f[:-8] for f in os.listdir(d) if f.endswith(".parquet")}


# ---------------------------------------------------------------------------
# Test 1: OHLCV schema consistency (catches Pass 53 C1)
# ---------------------------------------------------------------------------
def test_data_integrity_1_ohlcv_schema_consistency():
    """All OHLCV files must share single schema (RangeIndex + date col OR DatetimeIndex)."""
    if not OHLCV_DIR.exists():
        pytest.skip("OHLCV cache missing")
    schema_a = []  # DatetimeIndex, no date col
    schema_b = []  # RangeIndex, has date col
    sample = sorted(os.listdir(OHLCV_DIR))  # full scan
    for f in sample:
        if not f.endswith(".parquet"):
            continue
        try:
            df = pd.read_parquet(OHLCV_DIR / f)
        except Exception as e:
            pytest.fail(f"OHLCV file {f} failed to parse: {e}")
        has_date_col = "date" in df.columns
        is_dt_index = isinstance(df.index, pd.DatetimeIndex)
        if has_date_col and not is_dt_index:
            schema_b.append(f)
        elif is_dt_index and not has_date_col:
            schema_a.append(f)
        else:
            pytest.fail(
                f"OHLCV file {f} has unexpected schema: "
                f"has_date_col={has_date_col}, is_dt_index={is_dt_index}, "
                f"cols={list(df.columns)}"
            )
    assert not (schema_a and schema_b), (
        f"OHLCV schema split detected (Pass 53 C1): "
        f"{len(schema_a)} files Schema-A (DatetimeIndex, no date col) + "
        f"{len(schema_b)} files Schema-B (RangeIndex + date col). "
        f"Sample Schema-A: {schema_a[:3]}; Sample Schema-B: {schema_b[:3]}"
    )


# ---------------------------------------------------------------------------
# Test 2: OHLCV freshness (catches Pass 53 C2)
# ---------------------------------------------------------------------------
def test_data_integrity_2_ohlcv_freshness():
    """All OHLCV last_bar must be >= today - 35 days (workdays + weekend +
    prefetch-cadence buffer).

    Delisted tickers (currently_active=False in Master Dedup) are exempt - their
    last_bar is correctly frozen at the delist date.

    Batch 228 (housekeeping 2026-05-18 owner-approved): cutoff extended
    14 -> 21 days to accommodate Polygon prefetch cadence for thinly-traded
    T2/T3 tier tickers.

    Batch 423 (housekeeping 2026-05-28 owner-approved): cutoff extended
    21 -> 35 days. Per CLAUDE.md HARD CUT "Stage 2 backtest is NO-LIVE-API;
    prefetch refreshes happen on owner-driven cadence not per-day", the
    21-day window was tighter than the realistic owner-driven cadence.
    Triggered by 924 ACTIVE-ticker .parquet files with last_bar=2026-05-05
    (Phase 1A-beta backtest end window) when CI ran on 2026-05-28
    (23 days later, 2 days past the prior 21-day cutoff). Causing the
    Test Pyramid Tier 3 (Data integrity) to red on every push from
    Batch 412 onwards (~12 consecutive CI failures noticed by owner
    2026-05-28).
    """
    if not OHLCV_DIR.exists():
        pytest.skip("OHLCV cache missing")
    cutoff = pd.Timestamp.today() - pd.Timedelta(days=35)
    active_tickers = _load_active_tickers()
    stale = []
    files = sorted(os.listdir(OHLCV_DIR))
    for f in files:
        if not f.endswith(".parquet"):
            continue
        ticker = f[:-8].upper()
        # Normalize ticker conventions for active-set lookup
        ticker_norm = ticker.replace("_", ".").replace("-", ".")
        if ticker not in active_tickers and ticker_norm not in active_tickers:
            continue  # delisted; exempt from freshness check
        try:
            df = pd.read_parquet(OHLCV_DIR / f)
            if "date" in df.columns:
                last = pd.to_datetime(df["date"]).max()
            else:
                last = df.index.max()
            if last < cutoff:
                stale.append((f, str(last.date()) if hasattr(last, "date") else str(last)))
        except Exception:
            pass
    assert not stale, (
        f"OHLCV stale files detected for ACTIVE tickers (Pass 53 C2): "
        f"{len(stale)} files with last_bar < {cutoff.date()}. "
        f"Examples: {stale[:5]}"
    )


# ---------------------------------------------------------------------------
# Test 3: Required tickers present (catches Pass 53 C3 + M6)
# ---------------------------------------------------------------------------
def test_data_integrity_3_required_tickers_present():
    """VIX proxy + SPY + 11 sector ETFs (XLB-XLY + XLC) must be in OHLCV cache OR FRED."""
    ohlcv = _list_parquet(OHLCV_DIR)
    fred = _list_parquet(PREFETCH_DIR / "fred" / "observations")

    # VIX: present if any proxy is in OHLCV or VIXCLS in FRED
    vix_present = bool(VIX_PROXIES & (ohlcv | fred))
    assert vix_present, (
        f"VIX missing entirely (Pass 53 C3) - none of {VIX_PROXIES} found in "
        f"OHLCV cache or FRED."
    )

    # Required tickers in OHLCV
    missing_in_ohlcv = (REQUIRED_TICKERS - VIX_PROXIES) - ohlcv
    assert not missing_in_ohlcv, (
        f"Required tickers missing from OHLCV (Pass 53 C3 + M6): "
        f"{sorted(missing_in_ohlcv)}"
    )


# ---------------------------------------------------------------------------
# Test 4: Numeric dtype on CFTC + FRED (catches Pass 53 C4)
# ---------------------------------------------------------------------------
def test_data_integrity_4_numeric_dtype_cftc_fred():
    """CFTC + FRED numeric columns must be numeric dtype (not string)."""
    cftc = PREFETCH_DIR / "cftc" / "cot_emini_sp500.parquet"
    if not cftc.exists():
        pytest.skip(f"CFTC cache missing at {cftc}")
    df_cftc = pd.read_parquet(cftc)

    cftc_numeric_cols = [
        "open_interest_all",
        "lev_money_positions_long",
        "lev_money_positions_short",
        "asset_mgr_positions_long",
        "asset_mgr_positions_short",
    ]
    bad = [
        c for c in cftc_numeric_cols
        if c in df_cftc.columns and not pd.api.types.is_numeric_dtype(df_cftc[c])
    ]
    assert not bad, (
        f"CFTC numeric columns have non-numeric dtype (Pass 53 C4): {bad}. "
        f"Column-level arithmetic (mean/sum/rolling) will fail."
    )

    # FRED 'value' col must be numeric
    fred_dir = PREFETCH_DIR / "fred" / "observations"
    if fred_dir.exists():
        sample = sorted(os.listdir(fred_dir))[:5]
        for f in sample:
            df = pd.read_parquet(fred_dir / f)
            if "value" in df.columns:
                assert pd.api.types.is_numeric_dtype(df["value"]), (
                    f"FRED {f} 'value' column non-numeric: {df['value'].dtype}"
                )


# ---------------------------------------------------------------------------
# Test 5: TIER_PARAMS dict populated (catches Pass 53 C5)
# ---------------------------------------------------------------------------
def test_data_integrity_5_tier_params_populated():
    """TIER_PARAMS dict must be populated for all 5 tiers with all required keys."""
    from backtest.data import universe

    # Check all 5 tiers have entries
    if not hasattr(universe, "TIER_PARAMS"):
        pytest.fail(
            "universe.TIER_PARAMS not exported (Pass 53 C5) - DEC-504 implementation incomplete."
        )

    tier_params = universe.TIER_PARAMS
    missing_tiers = TIERS_REQUIRED - set(tier_params.keys())
    assert not missing_tiers, (
        f"TIER_PARAMS missing tiers (Pass 53 C5): {missing_tiers}"
    )

    # Each tier must have all required keys
    for tier in TIERS_REQUIRED:
        params = tier_params[tier]
        missing_keys = TIER_PARAM_KEYS - set(params.keys())
        assert not missing_keys, (
            f"TIER_PARAMS[{tier}] missing keys (Pass 53 C5): {missing_keys}. "
            f"Got: {list(params.keys())}"
        )
        # No None values
        none_keys = [k for k, v in params.items() if v is None]
        assert not none_keys, (
            f"TIER_PARAMS[{tier}] has None for keys: {none_keys}"
        )


# ---------------------------------------------------------------------------
# Test 6: Cross-source ticker coverage (catches Pass 53 H5)
# ---------------------------------------------------------------------------
def test_data_integrity_6_cross_source_ticker_coverage():
    """Each prefetch source must cover ≥X% of universe per CROSS_SOURCE_COVERAGE_TARGETS."""
    universe = _load_universe()
    failures = []
    for source, (path, target_pct) in CROSS_SOURCE_COVERAGE_TARGETS.items():
        cached = _list_parquet(path)
        # Normalize ticker conventions: '.' / '-' / '_' equivalent
        cached_norm = {t.replace(".", "_").replace("-", "_") for t in cached}
        universe_norm = {t.replace(".", "_").replace("-", "_") for t in universe}
        coverage = len(universe_norm & cached_norm) / len(universe_norm) if universe_norm else 0
        if coverage < target_pct:
            failures.append((source, f"{100*coverage:.1f}%", f">={100*target_pct:.0f}%"))
    assert not failures, (
        f"Cross-source coverage below target (Pass 53 H5): "
        f"{[(s, got, want) for s, got, want in failures]}"
    )


# ---------------------------------------------------------------------------
# Test 7: Cumulative-snapshot history (catches Pass 53 H3 Apewisdom)
# ---------------------------------------------------------------------------
def test_data_integrity_7_cumulative_snapshot_history():
    """Sources that accumulate daily must meet per-source minimum distinct dates.

    Apewisdom is relaxed to ≥1 (DEC-592 forward-only accumulator; historical API
    unavailable). AAII / CNN F&G require ≥30 days (have multi-year history).
    """
    failures = []
    for source, (path, min_unique_dates) in CUMULATIVE_SNAPSHOT_SOURCES.items():
        if not path.exists():
            failures.append((source, "MISSING", min_unique_dates))
            continue
        df = pd.read_parquet(path)
        date_col = None
        for cand in ("snapshot_date", "date", "report_date"):
            if cand in df.columns:
                date_col = cand
                break
        if date_col is None:
            failures.append((source, "NO_DATE_COL", min_unique_dates))
            continue
        unique_dates = pd.to_datetime(df[date_col]).dt.date.nunique()
        if unique_dates < min_unique_dates:
            failures.append((source, str(unique_dates), min_unique_dates))
    assert not failures, (
        f"Cumulative-snapshot sources have insufficient history (Pass 53 H3): "
        f"{[(s, got, f'>={want}') for s, got, want in failures]}"
    )
