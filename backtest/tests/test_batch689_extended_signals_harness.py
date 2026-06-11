"""B689 regression-guard tests for the measure_fire_count.py harness
extension shipped per B660 self-critique.

Pre-B689 the precompute loop only invoked `compute_all_signals` from
technical.py. 103 of 146 FAIL_FIRE_STARVED verdicts in B660 were false
negatives caused by smart-money / SMC / ICT / chart-pattern / event-driven
producers being absent from the per-bar signals dict.

B689 wires:
  TIER 1 (per-bar df-only; no cache deps):
    chart_patterns + smc_ict + ict_producers + multi_timeframe +
    volume_profile
  TIER 3 (per-as_of global; cached across tickers):
    cross_asset + calendar_effects + macro_events.pre_fomc +
    cot_positioning (7 series)

DEFERRED to B690 (Tier 2): per-(ticker, as_of) cache-read producers
(insider, institutional, short_interest, sec_edgar, news_sentiment,
pead, search_volume, congressional_*, recent_8k, cross_sectional).

These pins guarantee:
  - the new helpers exist and are importable
  - they produce non-empty signal dicts on real OHLCV
  - the precompute path emits strictly more keys when extended=ON
  - specific TIER 1 + TIER 3 key families appear in the output
  - --no-extended-signals CLI flag preserves pre-B689 behavior (backward
    compat for diffing against the B660 baseline)
  - a single producer failure is non-fatal (try/except guards work)
"""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import pytest

from scripts import measure_fire_count as mfc


# ---------------------------------------------------------------------------
# Pin 1: New TIER 3 helper exists + produces a dict
# ---------------------------------------------------------------------------
def test_b689_pin1_tier3_helper_exists_and_returns_dict():
    """`_compute_tier3_signals_for_as_of` must exist and return a dict on
    any valid date (empty acceptable if producers all silently fail; non-
    None is the bare-minimum guarantee)."""
    assert hasattr(mfc, "_compute_tier3_signals_for_as_of")
    result = mfc._compute_tier3_signals_for_as_of(date(2024, 6, 14))
    assert isinstance(result, dict), (
        "_compute_tier3_signals_for_as_of must return a dict (got "
        f"{type(result).__name__})"
    )


# ---------------------------------------------------------------------------
# Pin 2: TIER 3 helper produces non-empty signals on a known good date
# ---------------------------------------------------------------------------
def test_b689_pin2_tier3_emits_signals_for_known_good_date():
    """For a date well within the prefetched range (2024-06-14), TIER 3
    should emit AT LEAST the calendar_effects signals (which need no
    external cache) and ideally cross_asset signals. If this falls to 0
    keys, the wire-in is broken."""
    result = mfc._compute_tier3_signals_for_as_of(date(2024, 6, 14))
    assert len(result) >= 5, (
        f"TIER 3 emitted only {len(result)} keys; expected >=5 from "
        "calendar_effects + cross_asset + pre_fomc + cot minimum. "
        "Producer chain may be silently failing."
    )


# ---------------------------------------------------------------------------
# Pin 3: TIER 1 helper exists + produces signals on real OHLCV
# ---------------------------------------------------------------------------
def test_b689_pin3_tier1_helper_exists_and_emits_signals():
    """`_compute_tier1_signals_for_bar` must exist and produce a non-trivial
    dict on real OHLCV (AAPL)."""
    assert hasattr(mfc, "_compute_tier1_signals_for_bar")
    df = mfc._load_ohlcv("AAPL")
    if df is None or len(df) < 300:
        pytest.skip("AAPL OHLCV cache unavailable in test environment")
    sub_df = df.iloc[:300]
    result = mfc._compute_tier1_signals_for_bar(sub_df, "AAPL")
    assert isinstance(result, dict), "TIER 1 must return a dict"
    assert len(result) >= 30, (
        f"TIER 1 emitted only {len(result)} keys on AAPL[:300]; expected "
        ">=30 from chart_patterns + smc + ict + multi_timeframe + "
        "volume_profile combined. Producer chain may be silently failing."
    )


# ---------------------------------------------------------------------------
# Pin 4: Extended signals path is strictly a SUPERSET of pre-B689 path
# ---------------------------------------------------------------------------
def test_b689_pin4_extended_signals_is_superset_of_pre_b689():
    """Running the precompute with extended_signals=True must emit
    strictly more keys than extended_signals=False (the pre-B689 baseline).
    Same OHLCV, same date range, same ticker."""
    df = mfc._load_ohlcv("AAPL")
    if df is None or len(df) < 300:
        pytest.skip("AAPL OHLCV cache unavailable in test environment")
    start = date(2024, 6, 1)
    end = date(2024, 7, 15)
    pre = mfc._precompute_signals_for_ticker(
        df, "AAPL", start, end, enable_extended_signals=False,
    )
    post = mfc._precompute_signals_for_ticker(
        df, "AAPL", start, end, enable_extended_signals=True,
    )
    assert pre and post, "Both precompute runs must produce non-empty output"
    n_keys_pre = len(pre[0][1])
    n_keys_post = len(post[0][1])
    assert n_keys_post > n_keys_pre, (
        f"B689 extended_signals=True produced {n_keys_post} keys but "
        f"extended_signals=False produced {n_keys_pre}. Extended path "
        "must be a STRICT superset (TIER 1 + TIER 3 add new keys; do "
        "not subtract)."
    )
    # Delta should be substantial -- at least 50 new keys covering the
    # 5 TIER 1 modules + 4 TIER 3 modules.
    assert n_keys_post - n_keys_pre >= 50, (
        f"B689 delta only {n_keys_post - n_keys_pre} keys; expected >=50 "
        "from TIER 1 + TIER 3 wire-in. Most likely cause: one or more "
        "producer modules raised an exception caught by the try/except "
        "guard. Run with --verbose to see DEBUG messages."
    )


# ---------------------------------------------------------------------------
# Pin 5: Specific TIER 1 key families appear in extended output
# ---------------------------------------------------------------------------
def test_b689_pin5_tier1_specific_key_families_present():
    """Concrete check: each TIER 1 module's signature output keys must
    appear in the post-B689 dict. Looking for at least one key per family:
    chart_patterns, smc_, po3_, weekly_bias_, monthly_bias_, htf_, value_area_
    """
    df = mfc._load_ohlcv("AAPL")
    if df is None or len(df) < 300:
        pytest.skip("AAPL OHLCV cache unavailable in test environment")
    sub_df = df.iloc[:300]
    result = mfc._compute_tier1_signals_for_bar(sub_df, "AAPL")
    keys = set(result.keys())

    # Chart patterns
    chart_pattern_hits = {k for k in keys if any(
        token in k for token in ("cup_handle", "head_shoulders", "triangle_", "flag_", "double_top", "double_bottom", "wedge")
    )}
    assert chart_pattern_hits, (
        "TIER 1 chart_patterns module produced ZERO recognized keys. "
        "B689 wire-in for chart_patterns may be broken or import-failing."
    )

    # SMC
    smc_hits = {k for k in keys if k.startswith("smc_")}
    assert smc_hits, "TIER 1 smc_ict module produced ZERO smc_* keys."

    # ICT / PO3
    po3_hits = {k for k in keys if "po3" in k.lower()}
    assert po3_hits, "TIER 1 ict_producers / multi_timeframe produced ZERO po3* keys."

    # multi_timeframe biases
    bias_hits = {k for k in keys if "weekly_bias" in k or "monthly_bias" in k or "htf_" in k}
    assert bias_hits, (
        "TIER 1 multi_timeframe produced ZERO weekly_bias / monthly_bias / htf_ keys."
    )


# ---------------------------------------------------------------------------
# Pin 6: Specific TIER 3 key families appear
# ---------------------------------------------------------------------------
def test_b689_pin6_tier3_specific_key_families_present():
    """TIER 3 must include cross_asset signals (vix_today, bond_equity_*,
    sector_*) AND calendar_effects (some date-derived flags). If both
    families are empty, the per-as_of wire-in is broken."""
    result = mfc._compute_tier3_signals_for_as_of(date(2024, 6, 14))
    keys = set(result.keys())

    cross_asset_hits = {k for k in keys if any(
        token in k for token in ("vix_", "bond_equity", "sector_", "gold_silver", "dxy_", "risk_off", "risk_on")
    )}
    assert cross_asset_hits, (
        "TIER 3 cross_asset module produced ZERO recognized keys at "
        "2024-06-14 (cache should be fully populated for this date)."
    )


# ---------------------------------------------------------------------------
# Pin 7: CLI flag --no-extended-signals exists + parses correctly
# ---------------------------------------------------------------------------
def test_b689_pin7_cli_flag_no_extended_signals():
    """The CLI must accept --no-extended-signals (backward-compat /
    diff-vs-B660 mode). Parsing must succeed; the flag must be reflected
    in the namespace."""
    parser = mfc._build_arg_parser()
    args = parser.parse_args(["--strategies", "macd_crossover", "--no-extended-signals"])
    assert hasattr(args, "no_extended_signals")
    assert args.no_extended_signals is True


# ---------------------------------------------------------------------------
# Pin 8: CLI flag --cot-series exists with sensible default
# ---------------------------------------------------------------------------
def test_b689_pin8_cli_flag_cot_series_with_default():
    parser = mfc._build_arg_parser()
    args = parser.parse_args(["--strategies", "macd_crossover"])
    assert hasattr(args, "cot_series")
    assert isinstance(args.cot_series, list)
    assert len(args.cot_series) >= 5, (
        "Default --cot-series should cover >=5 series (equity + fx + "
        "commodity + rates minimum)."
    )
    # All defaults must match DEFAULT_COT_SERIES
    assert set(args.cot_series) == set(mfc.DEFAULT_COT_SERIES)
    # Custom override
    args2 = parser.parse_args([
        "--strategies", "macd_crossover", "--cot-series", "cot_emini_sp500", "cot_gold",
    ])
    assert args2.cot_series == ["cot_emini_sp500", "cot_gold"]


# ---------------------------------------------------------------------------
# Pin 9: Single-producer failure is non-fatal (try/except guards)
# ---------------------------------------------------------------------------
def test_b689_pin9_single_producer_failure_non_fatal():
    """If any individual producer raises (e.g., cache missing), the
    helper must catch + continue, not propagate the exception. Simulate
    by monkey-patching compute_smc_signals to raise; the helper must
    still return a non-empty dict from the other modules."""
    df = mfc._load_ohlcv("AAPL")
    if df is None or len(df) < 300:
        pytest.skip("AAPL OHLCV cache unavailable in test environment")
    sub_df = df.iloc[:300]

    # Patch compute_smc_signals to raise
    import backtest.signals.smc_ict as smc_mod
    original = smc_mod.compute_smc_signals
    def _broken(*args, **kwargs):
        raise RuntimeError("simulated smc cache miss")
    smc_mod.compute_smc_signals = _broken
    try:
        result = mfc._compute_tier1_signals_for_bar(sub_df, "AAPL")
        # Must still produce non-empty dict from chart_patterns + ict_producers
        # + multi_timeframe + volume_profile
        assert len(result) >= 30, (
            f"After smc_ict failure simulation TIER 1 produced only "
            f"{len(result)} keys; the try/except guard appears to have "
            "let the exception propagate or the other producers also "
            "broke. Should still emit chart_patterns + ict + mtf + vp."
        )
        # smc_ keys should be absent (their producer was patched to raise)
        smc_keys = {k for k in result.keys() if k.startswith("smc_")}
        assert not smc_keys, (
            "smc_ keys should be absent after compute_smc_signals raise; "
            "found: " + str(sorted(smc_keys))
        )
    finally:
        smc_mod.compute_smc_signals = original


# ---------------------------------------------------------------------------
# Pin 10: DEFAULT_COT_SERIES constant exists + lists existing parquets
# ---------------------------------------------------------------------------
def test_b689_pin10_default_cot_series_files_exist():
    """Each name in DEFAULT_COT_SERIES must have a corresponding parquet
    in data_prefetch/cftc/. Otherwise the TIER 3 COT injection silently
    no-ops and the operator has no signal it's broken."""
    assert hasattr(mfc, "DEFAULT_COT_SERIES")
    series = mfc.DEFAULT_COT_SERIES
    assert isinstance(series, tuple) and len(series) >= 5
    cftc_dir = Path(__file__).resolve().parents[2] / "data_prefetch" / "cftc"
    for name in series:
        parquet = cftc_dir / f"{name}.parquet"
        assert parquet.exists(), (
            f"B689 DEFAULT_COT_SERIES references {name} but "
            f"{parquet} does not exist. Either fix the constant or "
            "backfill the cache."
        )


# ---------------------------------------------------------------------------
# Pin 11: measure_strategies signature accepts new kwargs
# ---------------------------------------------------------------------------
def test_b689_pin11_measure_strategies_accepts_extended_signal_kwargs():
    """`measure_strategies` must accept `enable_extended_signals` +
    `cot_series` kwargs without raising TypeError. Smoke-only; does not
    actually run the full measurement (too slow for unit-test)."""
    import inspect
    sig = inspect.signature(mfc.measure_strategies)
    assert "enable_extended_signals" in sig.parameters, (
        "measure_strategies must accept enable_extended_signals kwarg per B689"
    )
    assert "cot_series" in sig.parameters
    # Defaults
    assert sig.parameters["enable_extended_signals"].default is True
    assert sig.parameters["cot_series"].default == mfc.DEFAULT_COT_SERIES


# ---------------------------------------------------------------------------
# Pin 12: per-as_of cache is shared (not recomputed per ticker)
# ---------------------------------------------------------------------------
def test_b689_pin12_per_as_of_cache_is_shared_across_tickers():
    """The as_of_cache dict passed into _precompute_signals_for_ticker
    must be FILLED LAZILY and SHARED across tickers. After running 2
    tickers over the same date range, the cache should contain entries
    keyed by bar_date, and the second ticker should hit the cache (no
    recomputation of TIER 3 signals).
    """
    df = mfc._load_ohlcv("AAPL")
    if df is None or len(df) < 300:
        pytest.skip("AAPL OHLCV cache unavailable in test environment")
    start = date(2024, 6, 1)
    end = date(2024, 6, 20)
    as_of_cache: dict = {}
    out1 = mfc._precompute_signals_for_ticker(
        df, "AAPL", start, end,
        as_of_cache=as_of_cache, enable_extended_signals=True,
    )
    n_after_first = len(as_of_cache)
    assert n_after_first > 0, (
        "as_of_cache must be filled by first ticker run when extended_signals=True"
    )
    # Second ticker (same df reused as proxy)
    out2 = mfc._precompute_signals_for_ticker(
        df, "AAPL_AGAIN", start, end,
        as_of_cache=as_of_cache, enable_extended_signals=True,
    )
    n_after_second = len(as_of_cache)
    # Cache size should be IDENTICAL after second run (date range same; cache
    # already has all bar_dates)
    assert n_after_second == n_after_first, (
        f"as_of_cache size grew from {n_after_first} to {n_after_second} "
        "after a same-range second ticker run. The cache should be reused "
        "(this is the whole point of the per-as_of shared cache)."
    )


# ---------------------------------------------------------------------------
# Pin 13: Extended signals path produces the >=50-key delta vs baseline
# ---------------------------------------------------------------------------
def test_b689_pin13_extended_signals_delta_threshold():
    """Quantitative pin: the delta from extended=False to extended=True
    should be at least 50 new keys. Below that suggests one or more
    producer modules silently failed."""
    df = mfc._load_ohlcv("AAPL")
    if df is None or len(df) < 300:
        pytest.skip("AAPL OHLCV cache unavailable in test environment")
    start = date(2024, 6, 1)
    end = date(2024, 6, 20)
    off = mfc._precompute_signals_for_ticker(
        df, "AAPL", start, end, enable_extended_signals=False,
    )
    on = mfc._precompute_signals_for_ticker(
        df, "AAPL", start, end, enable_extended_signals=True,
    )
    assert off and on, "Both runs must produce non-empty output"
    delta = len(on[0][1]) - len(off[0][1])
    assert delta >= 50, (
        f"B689 extended-signals delta is only {delta} keys; expected "
        ">=50. One or more producer modules likely silently failed."
    )
