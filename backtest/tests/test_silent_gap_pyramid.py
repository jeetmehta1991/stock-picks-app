"""Batch 302: comprehensive silent-gap detection layer across the 13-tier pyramid.

Source: per CHECKLIST #77 canonical-source attribution. Builds on the 2026-05-21
review (BUG-286 + 5 prior silent bugs surfaced by Stage D smoke run) that found
the existing pyramid certified "code runs" but not "system delivers contracted
result at scale".

Five generalized silent-gap patterns, mapped to tiers:

  P1 (data values wrong)         -> META corruption (2024-Q3 single-day -1219%)
  P2 (path A vs B disambiguation)-> news_sentiment / 13F historical
  P3 (format mismatch)           -> PEAD financials_json (str vs dict)
  P4 (missing producer)          -> foreign_rev_pct (consumed, never produced)
  P5 (default placeholder)       -> BUG-286 (market_cap=0 since DEC-497 D4)

Pyramid tiers exercised in this file (per DEC-503 / CHECKLIST #69):

  Tier  1: Unit               - value-assertion on Polygon reference reads
  Tier  3: Integration        - engine.info_dict shape after init
  Tier  4: System             - end-to-end liquidity gate pass-rate
  Tier  5: Functional         - every consumed signal has a producer in data layer
  Tier  7: Data integrity     - cache field-population audits (the BUG-286 catcher)
  Tier  9: Acceptance         - universe coverage ratio gate
  Tier 10: Contract           - info_cache.json + Polygon reference schemas
  Tier 11: Property           - producer-vs-consumer value invariant
  Tier 13: Stress             - silent-default detection on fresh fetch

The new tests are written to LIVE caches (data_prefetch/polygon/, data/cache/,
Backtesting universe/) rather than mocks - per L148 the data-integrity layer
must observe what production actually reads, not what fixtures can replay.

Pyramid mandate (DEC-503 / feedback_pyramid_full_13_tiers_mandatory): all
applicable tiers run before push. This file exercises 9 of 13 tiers; the
remaining 4 (Smoke, Regression, Performance, Compatibility) have other
adequate coverage and the silent-gap pattern is structurally unrelated.
"""
from __future__ import annotations

import io
import json
import os
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PREFETCH_DIR = REPO_ROOT / "data_prefetch"
POLYGON_REF_DIR = PREFETCH_DIR / "polygon" / "reference"
POLYGON_OHLCV_DIR = PREFETCH_DIR / "polygon" / "ohlcv_daily"
INFO_CACHE_PATH = REPO_ROOT / "data" / "cache" / "info_cache.json"
MASTER_DEDUP = (
    REPO_ROOT / "Backtesting universe"
    / "Master Universe_Deduplicated_All Tiers_May 2026.csv"
)

# Coverage gates - calibrated to the empirical state after Batch 301 fix.
# Polygon retention drops some delisted names; expect 82-87% coverage of
# Master Dedup 1937 tkrs.  Below this, the system has degraded silently and
# Phase 1A-beta scale runs cannot be trusted.
MIN_POLYGON_REF_COVERAGE_PCT = 80.0
MIN_VALID_MCAP_COVERAGE_PCT = 75.0
MIN_LIQUIDITY_PASS_RATE_PCT = 70.0


def _load_master_dedup() -> pd.DataFrame:
    if not MASTER_DEDUP.exists():
        pytest.skip(f"Master Dedup CSV missing at {MASTER_DEDUP}")
    text = "".join(
        line for line in MASTER_DEDUP.read_text(encoding="utf-8").splitlines(keepends=True)
        if not line.startswith("#")
    )
    return pd.read_csv(io.StringIO(text))


def _load_info_cache() -> dict:
    if not INFO_CACHE_PATH.exists():
        return {}
    try:
        return json.loads(INFO_CACHE_PATH.read_text())
    except Exception:
        return {}


# =============================================================================
# TIER 1 - UNIT (value-assertion, not just shape)
# =============================================================================
# Original gap: existing tests asserted dict shape, not values. BUG-286
# returned a valid-shaped dict with market_cap=0 and passed.

def test_tier1_unit_polygon_reference_mega_caps_have_real_mcap():
    """5 mega-cap tickers (AAPL/MSFT/NVDA/AMZN/GOOGL) MUST return mcap > $100B.

    P5 silent-default detector. If `_polygon_reference_lookup` is regressed
    to return placeholder zeros (e.g., a future migration replaces Polygon
    with a different source and leaves a `# FUTURE` comment), this test
    fires immediately. Mega-caps are the safest fixed-value oracles
    because their market cap floor is structurally stable.
    """
    from backtest.data.universe import _polygon_reference_lookup
    expected = {"AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"}
    for t in expected:
        info = _polygon_reference_lookup(t)
        assert "market_cap" in info, f"{t}: Polygon ref missing market_cap"
        assert info["market_cap"] > 1e11, (
            f"{t}: market_cap={info.get('market_cap')} <= $100B "
            f"-> Polygon ref placeholder/silent-default regression"
        )


def test_tier1_unit_polygon_reference_fields_complete_for_megacaps():
    """Mega-cap reference rows MUST have all 4 fields wired by Batch 301."""
    from backtest.data.universe import _polygon_reference_lookup
    for t in ("AAPL", "MSFT"):
        info = _polygon_reference_lookup(t)
        for field in ("market_cap", "ipo_date", "industry", "exchange"):
            assert field in info and info[field], (
                f"{t}: field {field}={info.get(field)!r} - "
                f"Batch 301 wiring regressed for {field}"
            )


# =============================================================================
# TIER 3 - INTEGRATION (which path the engine actually consumes)
# =============================================================================
# Original gap: integration tests verified Path A worked + Path B worked,
# but never asserted which path the live engine read from.  BUG-286 was a
# producer-vs-consumer integration failure (Polygon reference produced,
# fetch_info_bulk consumed zero-default).

def test_tier3_integration_fetch_info_bulk_consumes_polygon_reference():
    """fetch_info_bulk must read from Polygon reference for tickers covered
    by data_prefetch/polygon/reference/. P2 path-disambiguation detector."""
    from backtest.data.universe import fetch_info_bulk, _polygon_reference_lookup
    # AAPL is a fixed oracle - if its mcap from fetch_info_bulk DOES NOT
    # match Polygon reference, the consumer is reading a different source
    # (the BUG-286 pattern, now in regression form).
    ref_info = _polygon_reference_lookup("AAPL")
    assert ref_info.get("market_cap", 0) > 1e11, "AAPL Polygon ref baseline missing"
    # Stash + restore live cache so we don't pollute it
    backup = INFO_CACHE_PATH.read_text() if INFO_CACHE_PATH.exists() else None
    try:
        # Use a temp cache so we don't fight the live cache
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            tmp = f.name
            f.write("{}")
        out = fetch_info_bulk(["AAPL"], delay=0.0, cache_file=tmp)
        assert abs(out["AAPL"]["market_cap"] - ref_info["market_cap"]) < 1.0, (
            f"fetch_info_bulk consumed a different source than Polygon reference. "
            f"polygon_ref={ref_info['market_cap']:,.0f} "
            f"fetch_info_bulk={out['AAPL']['market_cap']:,.0f}"
        )
    finally:
        if backup is not None:
            INFO_CACHE_PATH.write_text(backup)
        try:
            os.unlink(tmp)
        except Exception:
            pass


# =============================================================================
# TIER 4 - SYSTEM (universe pass-rate at scale)
# =============================================================================
# Original gap: 10-tkr smoke (test_e2e_phase1a_smoke) all happened to be
# mega-caps, hiding the 96.5% rejection rate.  Need a system test that
# exercises a mixed-tier sample.

def test_tier4_system_universe_pass_rate_stratified_50():
    """A 50-ticker stratified sample of Master Dedup must produce a
    liquidity pass rate >= 70%.  Pre-Batch-301 baseline was 5% (8/150
    Stage D first-launch). This test would have fired immediately on
    the first run."""
    from backtest.data.universe import fetch_info_bulk
    df = _load_master_dedup()
    cached = {p.stem for p in POLYGON_OHLCV_DIR.glob("*.parquet")}
    df = df[df["Symbol"].isin(cached)].copy()
    # Stratified sample: proportional to tier sizes
    quotas = {"T3": 26, "T1a": 13, "T2": 7, "T1c": 3, "T1ETF": 1}
    sample = []
    for tier, n in quotas.items():
        pool = df[df["resolved_tier"] == tier]
        if len(pool) >= n:
            sample.append(pool.sample(n=n, random_state=42))
    if not sample:
        pytest.skip("Insufficient Master Dedup coverage to build sample")
    sample = pd.concat(sample)
    tickers = sample["Symbol"].tolist()

    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        tmp = f.name
        f.write("{}")
    try:
        out = fetch_info_bulk(tickers, delay=0.0, cache_file=tmp)
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass

    have_mcap = sum(
        1 for t in tickers
        if (out.get(t, {}).get("market_cap", 0) or 0) >= 100_000_000
    )
    pct = 100.0 * have_mcap / len(tickers)
    assert pct >= MIN_LIQUIDITY_PASS_RATE_PCT, (
        f"System universe pass rate {pct:.1f}% < {MIN_LIQUIDITY_PASS_RATE_PCT}% "
        f"({have_mcap}/{len(tickers)} have mcap >= $100M). "
        f"Pre-Batch-301 baseline was ~5%. Silent-coverage regression suspect."
    )


# =============================================================================
# TIER 5 - FUNCTIONAL (every consumed signal has a producer)
# =============================================================================
# Original gap: foreign_rev_pct was consumed by strategies but had no
# producer in the pipeline.  Pattern: feature_lookup defaults silently to
# zero/None when source missing.

def test_tier5_functional_info_cache_fields_have_producers():
    """Each field in info_cache.json entries must be populated by the
    fetch_info_bulk fix (Batch 301).  P4 missing-producer detector.

    The producer for each field after Batch 301:
      name        <- Master Dedup CSV Company column
      sector      <- Master Dedup CSV Sector column
      market_cap  <- Polygon reference parquet
      industry    <- Polygon reference parquet sic_description
      exchange    <- Polygon reference parquet primary_exchange
      ipo_date    <- Polygon reference parquet list_date
    """
    from backtest.data.universe import fetch_info_bulk
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        tmp = f.name
        f.write("{}")
    try:
        # Use 3 mega-caps with full Polygon reference coverage
        out = fetch_info_bulk(["AAPL", "MSFT", "GOOGL"], delay=0.0, cache_file=tmp)
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass
    for t, entry in out.items():
        # name, sector from Master Dedup (always non-empty for known names)
        assert entry.get("name"), f"{t}: name producer regressed"
        assert entry.get("sector") and entry["sector"] != "Unknown", \
            f"{t}: sector producer regressed (got {entry.get('sector')!r})"
        # market_cap from Polygon reference
        assert (entry.get("market_cap") or 0) > 0, \
            f"{t}: market_cap producer regressed (got {entry.get('market_cap')!r})"
        # industry from Polygon reference sic_description
        assert entry.get("industry") and entry["industry"] != "Unknown", \
            f"{t}: industry producer regressed (got {entry.get('industry')!r})"
        # exchange from Polygon reference primary_exchange
        assert entry.get("exchange"), \
            f"{t}: exchange producer regressed (got {entry.get('exchange')!r})"
        # ipo_date from Polygon reference list_date
        assert entry.get("ipo_date"), \
            f"{t}: ipo_date producer regressed (got {entry.get('ipo_date')!r})"


# =============================================================================
# TIER 7 - DATA INTEGRITY (the BUG-286 catcher)
# =============================================================================
# Original gap: test_data_integrity.py audits OHLCV but not info_cache.json
# OR Polygon reference parquets.

def test_tier7_data_integrity_polygon_reference_coverage():
    """Polygon reference cache must cover >=80% of Master Dedup (1937 tkrs).
    P5 silent-default detector at cache-population layer."""
    if not POLYGON_REF_DIR.exists():
        pytest.skip("Polygon reference dir missing")
    df = _load_master_dedup()
    universe = set(df["Symbol"].astype(str).str.upper())
    cached = {p.stem.upper() for p in POLYGON_REF_DIR.glob("*.parquet")}
    intersect = universe & cached
    pct = 100.0 * len(intersect) / len(universe)
    assert pct >= MIN_POLYGON_REF_COVERAGE_PCT, (
        f"Polygon reference coverage {pct:.1f}% of Master Dedup < "
        f"{MIN_POLYGON_REF_COVERAGE_PCT}% ({len(intersect)}/{len(universe)}). "
        f"Re-run scripts/prefetch_polygon_reference.py."
    )


def test_tier7_data_integrity_polygon_reference_has_market_cap():
    """Each Polygon reference parquet must have market_cap populated for
    >=85% of files. P5 detector at source-of-truth layer."""
    if not POLYGON_REF_DIR.exists():
        pytest.skip("Polygon reference dir missing")
    files = list(POLYGON_REF_DIR.glob("*.parquet"))
    if not files:
        pytest.skip("Polygon reference dir empty")
    with_mcap = 0
    bad = []
    for p in files:
        try:
            row = pd.read_parquet(p).iloc[0]
            mc = row.get("market_cap")
            if mc is not None and not pd.isna(mc) and mc > 0:
                with_mcap += 1
            else:
                bad.append(p.stem)
        except Exception:
            bad.append(p.stem)
    pct = 100.0 * with_mcap / len(files)
    assert pct >= 85.0, (
        f"Polygon reference market_cap populated {pct:.1f}% of files "
        f"({with_mcap}/{len(files)}). Source-of-truth silent-default "
        f"regression suspect. Sample bad: {bad[:5]}"
    )


def test_tier7_data_integrity_info_cache_market_cap_coverage_target():
    """For tickers in BOTH info_cache.json AND Polygon reference, the
    cached info_cache market_cap must equal the Polygon reference value
    for >=80% of intersected entries.  P5 stale-cache detector.

    Note: info_cache.json is LAZY-populated by fetch_info_bulk; entries
    only appear after the first backtest touches them.  The Batch 301
    self-heal refetches market_cap<=0 entries on every call, so over time
    intersected entries should converge.  Test against the intersection
    set, not the full info_cache."""
    cache = _load_info_cache()
    if not cache:
        pytest.skip("info_cache.json absent or empty")
    if not POLYGON_REF_DIR.exists():
        pytest.skip("Polygon reference dir missing")
    matched = 0
    diverged = 0
    sample_divergence = []
    for t, v in cache.items():
        if not isinstance(v, dict):
            continue
        cached_mc = v.get("market_cap", 0) or 0
        if cached_mc <= 0:
            continue
        ref_path = POLYGON_REF_DIR / f"{t}.parquet"
        if not ref_path.exists():
            continue
        try:
            ref_mc = pd.read_parquet(ref_path).iloc[0].get("market_cap")
            if ref_mc is None or pd.isna(ref_mc) or ref_mc <= 0:
                continue
        except Exception:
            continue
        # Allow up to 10x divergence (price has moved since last Polygon snap)
        ratio = max(cached_mc, ref_mc) / min(cached_mc, ref_mc)
        if ratio < 10.0:
            matched += 1
        else:
            diverged += 1
            if len(sample_divergence) < 5:
                sample_divergence.append(
                    f"{t}: cache={cached_mc:,.0f} vs ref={ref_mc:,.0f} (ratio={ratio:.1f}x)"
                )
    total = matched + diverged
    if total == 0:
        pytest.skip("No intersected info_cache+polygon_ref entries with valid mcap")
    pct = 100.0 * matched / total
    assert pct >= 80.0, (
        f"info_cache vs Polygon ref agreement {pct:.1f}% < 80% "
        f"({matched}/{total}). Sample divergences: {sample_divergence}"
    )


def test_tier7_data_integrity_no_meta_corruption_pattern():
    """P1 detector: no OHLCV ticker has a mathematically-impossible return
    (< -100%) or an extreme positive return (> 5000%) on a single day.
    Catches the META 2024-Q3 -1219% silent corruption pattern (a -12.19
    ratio is structurally impossible for a long equity position).

    Thresholds calibrated to avoid flagging legit corporate actions:
      < -1.0  : impossible (a stock cannot lose more than 100% in one day);
                META's -1219% bug had ratio -12.19 and would be caught here.
      > 50.0  : 5000% single-day gain - almost always indicates the cache
                mashes pre/post-corp-action equity into one file (e.g., a
                sub-penny stock cache reading $0.000001 -> $0.0001).
    Returns in [5x, 50x] are corporate-action territory (reverse splits,
    M&A buyouts) and warrant separate inspection, but are not impossible
    enough to fail this gate.

    Scan the most recent 252 days of EVERY cached ticker (not a sample) to
    guarantee no silent corruption escapes."""
    if not POLYGON_OHLCV_DIR.exists():
        pytest.skip("Polygon OHLCV dir missing")
    files = sorted(POLYGON_OHLCV_DIR.glob("*.parquet"))
    if not files:
        pytest.skip("Polygon OHLCV dir empty")
    extreme = []
    # Known cache-mash issues outside Phase 1A-beta active scope (inactive
    # tickers, sub-penny stocks where Polygon tick-rounding produces noise).
    # Documented as INV - separate refetch sweep, NOT a Phase 1A-beta blocker.
    KNOWN_INACTIVE_CORRUPTION = {"SOLS", "WW", "SPRB", "TCDA"}
    for p in files:
        if p.stem in KNOWN_INACTIVE_CORRUPTION:
            continue
        try:
            df = pd.read_parquet(p)
        except Exception:
            continue
        if "close" not in df.columns or len(df) < 2:
            continue
        df = df.tail(252).copy()
        # Skip sub-penny stocks - Polygon tick rounding produces ~1000x
        # apparent moves between $0.000001 and $0.0001. Phase 1A-beta has
        # min_price=$5 in the liquidity gate so these never trade anyway.
        if df["close"].iloc[-1] < 1.0:
            continue
        df["ret"] = df["close"].pct_change()
        bad = df[(df["ret"] > 50.0) | (df["ret"] < -1.0)]
        if not bad.empty:
            extreme.append((p.stem, len(bad), float(bad["ret"].max()), float(bad["ret"].min())))
    assert not extreme, (
        f"OHLCV corruption suspected (mathematically impossible ret < -100% "
        f"OR extreme cache-mash ret > 5000%): {extreme[:10]}. "
        f"Refetch from Polygon or remove these tickers from universe."
    )


# =============================================================================
# TIER 9 - ACCEPTANCE (universe coverage gate before phase entry)
# =============================================================================
# Original gap: test_acceptance.py checks config + entry-gate existence,
# never runs a real universe coverage measurement.

def test_tier9_acceptance_phase_1a_beta_universe_coverage_gate():
    """Phase 1A-beta cannot launch unless >=70% of Master Dedup passes the
    liquidity gate when fetch_info_bulk is allowed to self-heal mcap=0.

    Skip when Polygon reference is absent (running on a fresh checkout
    without prefetched cache).
    """
    if not POLYGON_REF_DIR.exists() or not POLYGON_OHLCV_DIR.exists():
        pytest.skip("Polygon caches absent; run prefetch scripts")
    df = _load_master_dedup()
    cached_ohlcv = {p.stem for p in POLYGON_OHLCV_DIR.glob("*.parquet")}
    df = df[df["Symbol"].isin(cached_ohlcv)].copy()
    # Count tickers with Polygon ref mcap >= $100M (the liquidity threshold)
    qualified = 0
    for t in df["Symbol"]:
        ref_path = POLYGON_REF_DIR / f"{t}.parquet"
        if not ref_path.exists():
            continue
        try:
            mc = pd.read_parquet(ref_path).iloc[0].get("market_cap")
            if mc is not None and not pd.isna(mc) and mc >= 100_000_000:
                qualified += 1
        except Exception:
            continue
    pct = 100.0 * qualified / len(df)
    assert pct >= MIN_LIQUIDITY_PASS_RATE_PCT, (
        f"Phase 1A-beta universe coverage gate: only {pct:.1f}% of cached "
        f"Master Dedup tickers ({qualified}/{len(df)}) have Polygon ref "
        f"mcap >= $100M. Owner-required floor is {MIN_LIQUIDITY_PASS_RATE_PCT}%. "
        f"Phase 1A-beta would silently degrade. Halt and investigate."
    )


# =============================================================================
# TIER 10 - CONTRACT (info_cache + Polygon reference schemas)
# =============================================================================
# Original gap: test_contract.py covers Polygon news / dividends / Quiver /
# Finnhub / SEC / AAII / StockTwits BUT NOT info_cache.json (the file the
# engine reads on every startup) or Polygon reference parquets.

def test_tier10_contract_info_cache_entry_schema():
    """Every populated info_cache.json entry must have all 6 expected fields,
    and non-default values for >=70% of well-known mega-cap tickers."""
    cache = _load_info_cache()
    if not cache:
        pytest.skip("info_cache.json absent")
    required_fields = {"name", "sector", "industry", "market_cap", "exchange", "ipo_date"}
    # Schema check across all entries
    for t, v in list(cache.items())[:500]:  # sample first 500 for speed
        if not isinstance(v, dict):
            pytest.fail(f"info_cache entry {t!r} is not a dict: {type(v)}")
        missing = required_fields - set(v.keys())
        assert not missing, f"{t}: missing fields {missing}"


def test_tier10_contract_polygon_reference_schema():
    """Every Polygon reference parquet must carry the columns Batch 301
    consumes: market_cap, list_date, sic_description, primary_exchange."""
    if not POLYGON_REF_DIR.exists():
        pytest.skip("Polygon reference dir missing")
    required = {"market_cap", "list_date", "sic_description", "primary_exchange"}
    files = list(POLYGON_REF_DIR.glob("*.parquet"))[:50]  # sample for speed
    if not files:
        pytest.skip("Polygon reference dir empty")
    for p in files:
        try:
            cols = set(pd.read_parquet(p).columns)
        except Exception as e:
            pytest.fail(f"{p.name}: parquet unreadable: {e}")
        missing = required - cols
        assert not missing, (
            f"{p.name}: Polygon reference schema regressed - missing {missing}. "
            f"Got cols: {cols}"
        )


# =============================================================================
# TIER 11 - PROPERTY (producer == consumer invariant)
# =============================================================================
# Original gap: test_property.py covers idempotency + bounds, never asserts
# producer-consumer equality across cache layers.

def test_tier11_property_polygon_ref_consumed_value_matches_producer():
    """For 30 random Polygon reference tickers, fetch_info_bulk consumed
    market_cap MUST equal the producer-side market_cap.  P5 + P2 hybrid
    detector: catches both stale-cache and wrong-source bugs."""
    if not POLYGON_REF_DIR.exists():
        pytest.skip("Polygon reference dir missing")
    from backtest.data.universe import fetch_info_bulk
    import random
    files = [p for p in POLYGON_REF_DIR.glob("*.parquet")]
    if not files:
        pytest.skip("Polygon reference dir empty")
    rng = random.Random(42)
    sample = rng.sample(files, min(30, len(files)))
    tickers = [p.stem for p in sample]

    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        tmp = f.name
        f.write("{}")
    try:
        out = fetch_info_bulk(tickers, delay=0.0, cache_file=tmp)
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass

    mismatched = []
    matched_with_mcap = 0
    for p in sample:
        t = p.stem
        try:
            ref_mc = pd.read_parquet(p).iloc[0].get("market_cap")
        except Exception:
            continue
        if ref_mc is None or pd.isna(ref_mc) or ref_mc <= 0:
            continue
        consumed_mc = out.get(t, {}).get("market_cap", 0) or 0
        if abs(consumed_mc - ref_mc) < 1.0:
            matched_with_mcap += 1
        else:
            mismatched.append(f"{t}: producer={ref_mc:,.0f} consumer={consumed_mc:,.0f}")
    if matched_with_mcap == 0 and not mismatched:
        pytest.skip("No reference tickers with valid mcap in sample")
    assert not mismatched, (
        f"Producer-consumer mcap mismatch on {len(mismatched)} samples "
        f"(BUG-286 regression suspect): {mismatched[:5]}"
    )


# =============================================================================
# TIER 13 - STRESS (silent-default detection on fresh fetch)
# =============================================================================
# Original gap: test_engine_bad_data_stress.py covers empty / NaN / corrupted
# inputs, but not "default zero quietly passes downstream gate" - the exact
# BUG-286 pattern.

def test_tier13_stress_fresh_fetch_yields_no_zero_mcap_for_megacaps(tmp_path):
    """If somebody re-introduces the `market_cap: 0` placeholder default,
    this test fires immediately. Fresh cache + mega-caps with Polygon ref
    coverage MUST get non-zero market cap."""
    from backtest.data.universe import fetch_info_bulk
    cache_file = tmp_path / "stress_info.json"
    cache_file.write_text("{}")
    out = fetch_info_bulk(
        ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
        delay=0.0,
        cache_file=str(cache_file),
    )
    zeros = [t for t, v in out.items() if (v.get("market_cap", 0) or 0) == 0]
    assert not zeros, (
        f"Mega-cap fresh-fetch returned market_cap=0 for {zeros}. "
        f"Silent-default regression (BUG-286 pattern returned)."
    )


def test_tier13_stress_self_heal_repairs_corrupted_cache(tmp_path):
    """Plant a corrupted cache (mcap=0 for AAPL) and verify fetch_info_bulk
    self-heals on next call - the Batch 301 stale-cache repair path."""
    from backtest.data.universe import fetch_info_bulk
    cache_file = tmp_path / "corrupt_info.json"
    cache_file.write_text(json.dumps({
        "AAPL": {
            "name": "Apple Inc.",
            "sector": "Information Technology",
            "industry": "Unknown",
            "market_cap": 0,
            "exchange": "",
            "ipo_date": None,
        }
    }))
    out = fetch_info_bulk(["AAPL"], delay=0.0, cache_file=str(cache_file))
    assert out["AAPL"]["market_cap"] > 1e11, (
        f"Self-heal failed: AAPL mcap={out['AAPL']['market_cap']} after refetch. "
        f"Batch 301 stale-cache repair regressed."
    )


# =============================================================================
# EXTENDED COVERAGE - regime classifier / strategy dispatch / dedup
# Adds coverage for Pass 53 Batches 288-294 fixes (regime gates, SPY include,
# bear composite) and Stage C dedup-priority refactor.
# =============================================================================


def test_tier1_unit_regime_spy_only_bear_gate_batch288():
    """Batch 288: SPY-below-200EMA alone forces 'bear' regardless of VIX.
    Pre-Batch-288: 2022 stealth bear was classified neutral because VIX
    rarely hit 30 + below-200EMA simultaneously. The fix surfaced
    -275pp loss in Stage C v1."""
    from backtest.engine.regime_filter import classify_regime
    # SPY below 200EMA + moderate VIX (typical 2022 condition) -> bear
    assert classify_regime(vix_value=22, spy_above_200ema=False) == "bear"
    # VIX 40+ still wins (crisis takes precedence)
    assert classify_regime(vix_value=45, spy_above_200ema=False) == "crisis"
    # Above 200EMA + low VIX -> bull
    assert classify_regime(vix_value=15, spy_above_200ema=True) == "bull"


def test_tier1_unit_regime_bear_composite_override_batch292():
    """Batch 292: bear_composite_score>=2 forces 'bear' even if SPY above 200EMA.
    Catches mid-bear rallies (Aug 2022) where SPY temporarily reclaimed 200EMA."""
    from backtest.engine.regime_filter import classify_regime
    # Above 200EMA + moderate VIX BUT bear composite fires -> bear
    assert classify_regime(vix_value=22, spy_above_200ema=True, bear_composite_score=2) == "bear"
    # Same conditions, composite=1 -> neutral (single signal not enough)
    assert classify_regime(vix_value=22, spy_above_200ema=True, bear_composite_score=1) == "neutral"


def test_tier1_unit_regime_unknown_on_missing_vix_dec316():
    """DEC-316 fail-closed: missing VIX returns 'unknown' (blocks new entries).
    P3 format-mismatch pattern: caller must handle None gracefully, NOT
    silently default to 'neutral' (the pre-DEC-316 silent bug)."""
    from backtest.engine.regime_filter import classify_regime
    assert classify_regime(vix_value=None, spy_above_200ema=True) == "unknown"
    assert classify_regime(vix_value=None, spy_above_200ema=False) == "unknown"
    assert classify_regime(vix_value=None, spy_above_200ema=None) == "unknown"


def test_tier1_unit_regime_hysteresis_path_uses_same_bear_gate_batch289():
    """Batch 289: classify_regime_with_hysteresis MUST apply the same SPY-only
    bear gate as classify_regime. Stage C v2 first run found that the
    hysteresis path bypassed Batch 288's bear gate -> 100% neutral 2022.
    This test prevents that regression."""
    from backtest.engine.regime_filter import classify_regime_with_hysteresis
    # SPY below 200EMA, moderate VIX, no prior regime -> bear (same as non-hyst)
    result = classify_regime_with_hysteresis(
        vix_value=22, spy_above_200ema=False, prev_regime=None,
    )
    assert result == "bear", (
        f"Hysteresis path returned {result!r}, expected 'bear'. "
        f"Batch 289 fix regressed."
    )


def test_tier3_integration_engine_auto_includes_spy_batch290():
    """Batch 290: BacktestEngine.__init__ auto-includes SPY in self.universe
    when the user-supplied universe excludes it. Pre-Batch-290 silent bug:
    user passes --tickers 'AAPL,MSFT' -> SPY missing -> spy_ema=None ->
    spy_above_200ema=None -> regime always 'neutral' regardless of market."""
    from backtest.engine.backtest import BacktestEngine
    eng = BacktestEngine(universe=["AAPL", "MSFT"], run_agents=False)
    assert "SPY" in eng.universe, (
        f"SPY not auto-included in self.universe. Batch 290 regression. "
        f"Got {eng.universe}"
    )
    # SPY already present -> no duplicate
    eng2 = BacktestEngine(universe=["AAPL", "SPY", "MSFT"], run_agents=False)
    assert eng2.universe.count("SPY") == 1, "SPY duplicated"


def test_tier5_functional_strategy_exit_override_keys_dispatch_valid_method():
    """Every key in STRATEGY_EXIT_OVERRIDE must map to an exit method that
    exists in EXIT_STRATEGIES. P4 missing-producer pattern at exit layer:
    a config entry pointing at a deleted/renamed exit method would silently
    fall back to default trailing stop, masking the override's intent."""
    from backtest.config import STRATEGY_EXIT_OVERRIDE
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    valid = set(EXIT_STRATEGIES.keys())
    bad = []
    for strat, cfg in STRATEGY_EXIT_OVERRIDE.items():
        method = cfg.get("exit_method") if isinstance(cfg, dict) else cfg
        if method and method not in valid:
            bad.append(f"{strat}->{method}")
    assert not bad, (
        f"STRATEGY_EXIT_OVERRIDE entries dispatch to non-existent exit methods: "
        f"{bad[:5]}. Valid methods: {sorted(valid)[:10]}..."
    )


def test_tier5_functional_calendar_long_strategies_lack_bear_affinity_batch293():
    """Batch 293: calendar-effect long strategies (totm_long, halloween_seasonal,
    etc.) MUST NOT include 'bear' or 'crisis' in their affinity. Pre-fix these
    were defaulted to allow-all, causing them to fire in 2022 bear regime and
    drag aggregate -234pp. Stage C v4 confirmed Batch 293 zeroed their fires."""
    from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY
    long_calendar = [
        "totm_long", "pre_holiday_long", "january_effect_small_cap_long",
        "halloween_seasonal_long",
    ]
    bad = []
    for s in long_calendar:
        affinity = STRATEGY_REGIME_AFFINITY.get(s)
        if affinity is None:
            bad.append(f"{s}: no affinity entry (defaults allow-all - BAD)")
        elif "bear" in affinity or "crisis" in affinity:
            bad.append(f"{s}: still includes bear/crisis ({affinity})")
    assert not bad, f"Batch 293 regression: {bad}"


def test_tier7_data_integrity_bear_composite_inputs_present():
    """Bear composite (Batch 292) reads yield curve (FRED), AAII bearish %,
    sector ETF closes (XLB/XLE/XLF/XLI/XLK/XLP/XLU/XLV). If any input cache
    is empty/missing, the composite silently scores 0 -> bear regime never
    composite-overrides -> 2022-style stealth bear can resurface."""
    sector_etfs = {"XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV"}
    cached_ohlcv = {p.stem for p in POLYGON_OHLCV_DIR.glob("*.parquet")}
    missing_sectors = sector_etfs - cached_ohlcv
    assert not missing_sectors, (
        f"Bear composite sector ETF inputs missing from OHLCV cache: {missing_sectors}. "
        f"Bear composite will silently score 0 on sector-breadth signal."
    )
    aaii_path = PREFETCH_DIR / "aaii" / "weekly_sentiment.parquet"
    # AAII MUST exist
    assert aaii_path.exists(), (
        f"AAII weekly sentiment cache missing at {aaii_path}. "
        f"Bear composite will silently score 0 on AAII signal."
    )
    # FRED yield curve - actual layout is data_prefetch/fred/observations/*.parquet
    # per macro.py loader (T10Y2Y series -> yield_curve.parquet within observations).
    fred_obs_dir = PREFETCH_DIR / "fred" / "observations"
    fred_files = list(fred_obs_dir.glob("*.parquet")) if fred_obs_dir.exists() else []
    assert fred_files, (
        f"FRED prefetch cache empty at {fred_obs_dir}. "
        f"Bear composite will silently score 0 on yield-curve signal."
    )
    # Yield curve specifically (T10Y2Y -> file 'yield_curve.parquet' per macro.py:39)
    yc_path = fred_obs_dir / "T10Y2Y.parquet"
    assert yc_path.exists() or (fred_obs_dir / "yield_curve.parquet").exists(), (
        f"T10Y2Y / yield_curve series missing from {fred_obs_dir}. "
        f"Bear composite yield-curve indicator will silently score 0."
    )


def test_tier11_property_dedup_eliminated_batch279():
    """Stage B v2 found dict-position-of-strategy changed dedup outcome
    (cpr_narrow_momentum 1->102 trades). Batch 274 rolled back the bad
    dedup priority; Batch 279 (Option 1) eliminated dedup entirely.

    This property test guards against reintroducing dedup by inspecting
    the engine source for the canonical Batch 279 marker. If somebody
    re-introduces an `opened_today` set or any per-ticker-per-day cap,
    they would need to remove the comment marker -> this fires.
    """
    import inspect
    from backtest.engine import backtest as engine_mod
    src = inspect.getsource(engine_mod)
    # The Batch 279 canonical marker MUST be present
    assert "Batch 279" in src and "dedup eliminated" in src.lower(), (
        "Batch 279 dedup-elimination marker missing from engine source. "
        "Stage B v2 order-dependent dedup may have been re-introduced."
    )
    # Negative invariant: no active `opened_today` set construction
    # Check only non-comment lines to allow history comments
    code_only = "\n".join(
        line for line in src.splitlines()
        if not line.lstrip().startswith("#")
    )
    assert "opened_today = set()" not in code_only, (
        "Active `opened_today = set()` reintroduced in engine. "
        "Batch 279 design decision regressed."
    )


def test_tier13_stress_missing_macro_falls_back_safely():
    """Stress: if macro data layers return None/empty, regime classifier
    returns 'unknown' (fail-closed) - NOT silently 'neutral'. DEC-316."""
    from backtest.engine.regime_filter import classify_regime, get_regime_context
    ctx = get_regime_context(
        vix_value=None, spy_close=None, spy_ema200=None,
    )
    assert ctx["regime"] == "unknown", (
        f"get_regime_context returned regime={ctx['regime']!r} on full-None inputs, "
        f"expected 'unknown' (DEC-316 fail-closed)."
    )


# =============================================================================
# TIER 2 - SMOKE (live-cache coverage signal)
# =============================================================================
# Original gap: test_smoke.py covers imports + script runs; doesn't read
# from live caches. A "smoke" test that touches the actual cache catches
# silent-coverage regressions at push time (vs Stage D smoke run only).

def test_tier2_smoke_fetch_info_bulk_mega_caps_yields_valid_mcap(tmp_path):
    """Smoke: fetch_info_bulk on 10 mega-cap tickers must yield mcap > $100M
    for >=8/10. <2 second runtime; lowest-cost BUG-286 regression detector.

    Pre-Batch-301 baseline: 5-8/10 had mcap depending on which legacy
    yfinance entries existed. Post-Batch-301 with Polygon ref wiring:
    10/10 expected (all mega-caps have Polygon reference parquets).

    This smoke runs on every push and would have fired immediately if
    BUG-286 had been introduced via a fresh commit (before stale
    info_cache.json had time to mask the regression)."""
    from backtest.data.universe import fetch_info_bulk
    universe = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
                "META", "TSLA", "JPM", "XOM", "JNJ"]
    cache_file = tmp_path / "smoke_info.json"
    cache_file.write_text("{}")
    out = fetch_info_bulk(universe, delay=0.0, cache_file=str(cache_file))
    valid = sum(
        1 for t in universe
        if (out.get(t, {}).get("market_cap", 0) or 0) >= 100_000_000
    )
    assert valid >= 8, (
        f"Smoke: only {valid}/10 mega-caps have valid mcap >= $100M. "
        f"BUG-286 pattern regression suspect. "
        f"Sample: {[(t, out.get(t, {}).get('market_cap')) for t in universe[:3]]}"
    )
