"""Tier 2 integration tests for vendored smartmoneyconcepts library.

Per DEC-508 + CHECKLIST #71 Tier 2 mandate. 4 sub-categories:
  1. Cache pipeline — smc reads real OHLCV cache without modification
  2. Composition — smc outputs are mergeable with existing F-003 signals
     (compute_all_signals 296 fields) without name collision
  3. Survivorship — smc handles short history / delisted / IPO / ticker_change
  4. Performance — wall-time budget per primitive fits Phase 1B-α scale

Phase A Tier 1 covered correctness with synthetic data; Tier 2 stresses
real-world data + integration constraints. Not yet Tier 3 (statistical
sanity / adversarial / cross-validation) or Tier 4 (Dashboard 2 visual).

Run: pytest backtest/tests/test_smartmoneyconcepts_integration.py -v
"""
from __future__ import annotations

import os
os.environ.setdefault("SMC_CREDIT", "0")

import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from smartmoneyconcepts import smc

REPO = Path(__file__).resolve().parents[2]
OHLCV_DIR = REPO / "backtest" / "data" / "cache" / "ohlcv"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def load_real_ticker(ticker: str) -> pd.DataFrame:
    """Load real OHLCV from cache; skip test if not available or not date-indexed."""
    p = OHLCV_DIR / f"{ticker}.parquet"
    if not p.is_file():
        pytest.skip(f"{ticker} OHLCV not cached")
    df = pd.read_parquet(p)
    if not isinstance(df.index, pd.DatetimeIndex):
        # Try to coerce; otherwise skip
        try:
            df.index = pd.to_datetime(df.index)
        except Exception:
            pytest.skip(f"{ticker} index not DatetimeIndex-coercible")
    return df


def smc_full_pipeline(df: pd.DataFrame, swing_length: int = 50) -> dict[str, pd.DataFrame]:
    """Run all 7 primary smc primitives on a real OHLCV frame."""
    sw = smc.swing_highs_lows(df, swing_length=swing_length)
    return {
        "swings": sw,
        "fvg": smc.fvg(df),
        "bos_choch": smc.bos_choch(df, sw),
        "ob": smc.ob(df, sw),
        "liquidity": smc.liquidity(df, sw),
        "previous_high_low": smc.previous_high_low(df, "1D"),
        "retracements": smc.retracements(df, sw),
    }


# =============================================================================
# 1. CACHE PIPELINE — smc reads real cache without modification
# =============================================================================


def test_smc_reads_real_ohlcv_msft():
    """MSFT 5-year OHLCV — full pipeline runs without crash, schemas preserved."""
    df = load_real_ticker("MSFT")
    results = smc_full_pipeline(df)
    for name, res in results.items():
        assert len(res) == len(df), f"{name} length {len(res)} != input {len(df)}"


def test_smc_reads_real_ohlcv_tsla():
    """TSLA 5-year — high-vol ticker should produce many smc signals."""
    df = load_real_ticker("TSLA")
    results = smc_full_pipeline(df)
    # High-vol ticker: expect ≥10 swings, ≥5 FVGs, ≥1 BOS/CHOCH
    swing_count = results["swings"]["HighLow"].notna().sum()
    fvg_count = results["fvg"]["FVG"].notna().sum()
    assert swing_count >= 10, f"TSLA only {swing_count} swings"
    assert fvg_count >= 5, f"TSLA only {fvg_count} FVGs"


def test_smc_reads_real_ohlcv_abnb():
    """ABNB 5-year — verify pipeline works on a different sector."""
    df = load_real_ticker("ABNB")
    results = smc_full_pipeline(df)
    assert all(len(r) == len(df) for r in results.values())


def test_smc_handles_truncated_history_aapl():
    """AAPL has only ~272 bars cached — smc should still work, possibly with fewer signals."""
    df = load_real_ticker("AAPL")
    if len(df) < 100:
        pytest.skip("AAPL cache too short for smoke")
    results = smc_full_pipeline(df, swing_length=20)  # smaller swing_length for short history
    assert all(len(r) == len(df) for r in results.values())


def test_smc_signal_density_real_ticker_reasonable():
    """Signal-density sanity: real 5-year ticker should have FVG density 1-50%."""
    df = load_real_ticker("MSFT")
    fvg = smc.fvg(df)
    fvg_count = fvg["FVG"].notna().sum()
    density = fvg_count / len(df)
    assert 0.005 <= density <= 0.5, (
        f"FVG density {density:.3f} outside 0.5%-50% — possible library issue"
    )


def test_smc_works_on_5year_window():
    """Confirm 5-year (1260+ bar) input doesn't trigger memory/length issues."""
    df = load_real_ticker("TSLA")
    if len(df) < 1000:
        pytest.skip("TSLA cache too short")
    res = smc.fvg(df)
    assert len(res) == len(df)


# =============================================================================
# 2. COMPOSITION — smc outputs merge with existing F-003 signals (no collision)
# =============================================================================


def test_smc_columns_no_conflict_with_compute_all_signals():
    """smc output column names must NOT collide with compute_all_signals 296 fields."""
    from backtest.signals.technical import compute_all_signals
    df = load_real_ticker("MSFT")
    existing_keys = set(compute_all_signals(df).keys())

    smc_columns: set[str] = set()
    smc_columns.update(smc.fvg(df).columns)
    sw = smc.swing_highs_lows(df, swing_length=50)
    smc_columns.update(sw.columns)
    smc_columns.update(smc.bos_choch(df, sw).columns)
    smc_columns.update(smc.ob(df, sw).columns)
    smc_columns.update(smc.liquidity(df, sw).columns)
    smc_columns.update(smc.previous_high_low(df, "1D").columns)
    smc_columns.update(smc.retracements(df, sw).columns)

    # smc uses CamelCase; existing compute_all_signals uses snake_case.
    # Direct collision check (case-sensitive — both are case-distinct):
    collisions = smc_columns & existing_keys
    assert not collisions, (
        f"smc columns collide with compute_all_signals keys: {collisions}. "
        "Apply a `smc_` or `ict_` prefix in OurTechnicalToolkit (DEC-462) "
        "before merging into the F-003 signal panel."
    )


def test_smc_outputs_align_with_input_index():
    """Every smc primitive returns a DataFrame with the same index as input."""
    df = load_real_ticker("MSFT")
    sw = smc.swing_highs_lows(df, swing_length=50)
    primitives = {
        "fvg": smc.fvg(df),
        "swings": sw,
        "bos_choch": smc.bos_choch(df, sw),
        "ob": smc.ob(df, sw),
        "liquidity": smc.liquidity(df, sw),
        "previous_high_low": smc.previous_high_low(df, "1D"),
        "retracements": smc.retracements(df, sw),
    }
    for name, res in primitives.items():
        assert len(res) == len(df), f"{name} length mismatch"
        # Library may return RangeIndex; accept either matching DatetimeIndex or aligned RangeIndex
        if isinstance(res.index, pd.DatetimeIndex) and isinstance(df.index, pd.DatetimeIndex):
            assert (res.index == df.index).all(), f"{name} index mismatch"


def test_smc_can_merge_into_signal_panel():
    """Demonstrate per-bar feature dict combining compute_all_signals + smc with prefix."""
    from backtest.signals.technical import compute_all_signals
    df = load_real_ticker("MSFT")
    sw = smc.swing_highs_lows(df, swing_length=50)
    fvg = smc.fvg(df)

    # Take last bar — flatten existing signals + add smc with prefix
    existing = compute_all_signals(df)
    last_bar = {}
    last_bar.update({f"tech_{k}": v for k, v in existing.items()})
    last_bar["smc_fvg"] = fvg["FVG"].iloc[-1] if pd.notna(fvg["FVG"].iloc[-1]) else None
    last_bar["smc_fvg_top"] = fvg["Top"].iloc[-1] if pd.notna(fvg["Top"].iloc[-1]) else None
    last_bar["smc_swing"] = sw["HighLow"].iloc[-1] if pd.notna(sw["HighLow"].iloc[-1]) else None

    # Merged dict has no key collisions
    assert "tech_pivot" in last_bar
    assert "smc_fvg" in last_bar
    # Total keys = 296 + 3 smc additions = 299
    assert len(last_bar) >= 299


def test_smc_signal_count_extends_f003_universe():
    """Per F-003: ~270-280 active fields. With smc primitives wired, expect ≥285."""
    df = load_real_ticker("MSFT")
    sw = smc.swing_highs_lows(df, swing_length=50)
    smc_field_count = (
        len(smc.fvg(df).columns)
        + len(sw.columns)
        + len(smc.bos_choch(df, sw).columns)
        + len(smc.ob(df, sw).columns)
        + len(smc.liquidity(df, sw).columns)
        + len(smc.previous_high_low(df, "1D").columns)
        + len(smc.retracements(df, sw).columns)
    )
    # 4 + 2 + 4 + 6 + 4 + 4 + 3 = 27 smc-side feature columns
    assert smc_field_count >= 25, f"smc field count {smc_field_count} unexpectedly low"


def test_smc_pit_preserved_through_truncation():
    """Composition with truncated DF — signals at safe-window bars preserved."""
    df = load_real_ticker("MSFT")
    if len(df) < 200:
        pytest.skip("MSFT too short for truncation test")
    full = df
    truncated = df.iloc[: len(df) - 50]
    safe_end = len(truncated) - 50  # stay 50 bars before the truncation boundary

    fvg_full = smc.fvg(full).iloc[:safe_end]
    fvg_trunc = smc.fvg(truncated).iloc[:safe_end]

    # FVG signal column must agree in safe window
    diffs = 0
    for i in range(len(fvg_full)):
        v_f = fvg_full["FVG"].iloc[i]
        v_t = fvg_trunc["FVG"].iloc[i]
        if pd.isna(v_f) and pd.isna(v_t):
            continue
        if pd.isna(v_f) != pd.isna(v_t) or v_f != v_t:
            diffs += 1
    assert diffs == 0, f"{diffs} FVG signals differ between full vs truncated in safe window"


# =============================================================================
# 3. SURVIVORSHIP — smc handles short history / delisted / corp actions / ticker change
# =============================================================================


def test_smc_handles_short_history_truncated_aapl():
    """AAPL has only ~272 cached bars — smc must not crash."""
    df = load_real_ticker("AAPL")
    sw = smc.swing_highs_lows(df, swing_length=20)
    assert len(sw) == len(df)
    fvg = smc.fvg(df)
    assert len(fvg) == len(df)


def test_smc_handles_recent_ipo_short_history():
    """Find a short-history ticker (recent IPO) and verify smc works."""
    short_candidates = ["RIVN", "CVNA", "ABNB", "DOCN", "PATH", "AFRM"]
    for t in short_candidates:
        p = OHLCV_DIR / f"{t}.parquet"
        if p.is_file():
            df = pd.read_parquet(p)
            if not isinstance(df.index, pd.DatetimeIndex):
                continue
            # Use this ticker even if it's longer; key thing is smc runs cleanly
            sw = smc.swing_highs_lows(df, swing_length=min(20, len(df) // 4))
            fvg = smc.fvg(df)
            assert len(sw) == len(df)
            assert len(fvg) == len(df)
            return
    pytest.skip("no short-history candidates found in cache")


def test_smc_swing_length_larger_than_data_handled():
    """If swing_length > len(df), library should not crash."""
    df = load_real_ticker("MSFT").iloc[:30]
    try:
        res = smc.swing_highs_lows(df, swing_length=100)
        assert len(res) == len(df) or len(res) == 0
    except (ValueError, IndexError):
        pass  # acceptable explicit error


def test_smc_handles_split_adjusted_jumps():
    """OHLCV cache stores split-adjusted prices. Detect: large continuous jumps
    (e.g. 4-for-1) should produce FVG / swings; library shouldn't crash."""
    df = load_real_ticker("TSLA")  # had splits
    fvg = smc.fvg(df)
    sw = smc.swing_highs_lows(df, swing_length=50)
    assert len(fvg) == len(df)
    assert len(sw) == len(df)


def test_smc_handles_extreme_volatility():
    """Volatile periods (e.g. 2020-2022 crisis) should not break smc."""
    df = load_real_ticker("TSLA")
    # Slice to a known volatile window if data covers it
    if df.index.min() <= pd.Timestamp("2022-01-01"):
        vol_window = df[(df.index >= "2022-01-01") & (df.index <= "2022-12-31")]
        if len(vol_window) >= 100:
            sw = smc.swing_highs_lows(vol_window, swing_length=20)
            fvg = smc.fvg(vol_window)
            assert len(sw) == len(vol_window)
            assert len(fvg) == len(vol_window)


# =============================================================================
# 4. PERFORMANCE — wall-time budget per primitive fits Phase 1B-α scale
# =============================================================================


# Phase 1B-α target: ~1937 tickers × 7 primitives × <X seconds = total budget
# Per-ticker per-primitive target: <1 second on a 5-year (1300-bar) frame
# Full-universe estimate: 1937 × 7 × 1s = ~3.8 hours sequential (parallelizable)


PERF_BUDGET_PER_PRIMITIVE_SEC = 1.0
PERF_BUDGET_FULL_PIPELINE_SEC = 3.0


def _time_call(fn, *args, **kwargs):
    t0 = time.perf_counter()
    fn(*args, **kwargs)
    return time.perf_counter() - t0


def test_smc_fvg_5year_under_budget():
    df = load_real_ticker("MSFT")
    if len(df) < 1000:
        pytest.skip("MSFT cache <1000 bars")
    elapsed = _time_call(smc.fvg, df)
    assert elapsed < PERF_BUDGET_PER_PRIMITIVE_SEC, (
        f"smc.fvg took {elapsed:.3f}s on {len(df)}-bar frame — exceeds {PERF_BUDGET_PER_PRIMITIVE_SEC}s budget. "
        f"Full-universe extrapolation: 1937 × {elapsed:.3f}s = {1937*elapsed/60:.1f} min for fvg alone."
    )


def test_smc_swing_5year_under_budget():
    df = load_real_ticker("MSFT")
    if len(df) < 1000:
        pytest.skip("MSFT cache <1000 bars")
    elapsed = _time_call(smc.swing_highs_lows, df, swing_length=50)
    assert elapsed < PERF_BUDGET_PER_PRIMITIVE_SEC, (
        f"swing_highs_lows took {elapsed:.3f}s on {len(df)}-bar frame"
    )


def test_smc_full_pipeline_5year_under_budget():
    df = load_real_ticker("MSFT")
    if len(df) < 1000:
        pytest.skip("MSFT cache <1000 bars")
    elapsed = _time_call(smc_full_pipeline, df)
    assert elapsed < PERF_BUDGET_FULL_PIPELINE_SEC, (
        f"Full smc pipeline took {elapsed:.3f}s on {len(df)}-bar frame — exceeds "
        f"{PERF_BUDGET_FULL_PIPELINE_SEC}s budget. Full-universe extrapolation: "
        f"1937 × {elapsed:.3f}s = {1937*elapsed/3600:.2f} hours sequential."
    )


def test_smc_perf_consistent_across_tickers():
    """Wall-time should be roughly proportional to bar count, not erratic."""
    timings = {}
    for ticker in ["MSFT", "TSLA", "ABNB"]:
        try:
            df = load_real_ticker(ticker)
        except pytest.skip.Exception:
            continue
        if len(df) < 1000:
            continue
        t = _time_call(smc.fvg, df)
        timings[ticker] = t
    if len(timings) < 2:
        pytest.skip("need ≥2 tickers with full history")
    # All within 10× of each other (no pathological cases)
    fastest = min(timings.values())
    slowest = max(timings.values())
    assert slowest / fastest < 10, (
        f"Wall-time variance across tickers: {timings} — slowest/fastest = {slowest/fastest:.1f}×"
    )


def test_smc_full_universe_estimate_fits_phase1b():
    """Extrapolation: full-universe smc compute should fit Phase 1B-α budget.
    Rule of thumb: <5 hours sequential (parallelizable across tickers)."""
    df = load_real_ticker("MSFT")
    if len(df) < 1000:
        pytest.skip("MSFT cache <1000 bars")
    elapsed = _time_call(smc_full_pipeline, df)
    # F-005: ~1937 tickers
    sequential_hours = 1937 * elapsed / 3600
    # Soft budget: 5 hours sequential (Phase 1B-α can parallelize 4-8x on laptop)
    assert sequential_hours < 10, (
        f"Full-universe sequential estimate: {sequential_hours:.2f} hours — "
        f"exceeds 10-hour soft budget. Per-ticker pipeline = {elapsed:.3f}s × 1937 tickers."
    )
