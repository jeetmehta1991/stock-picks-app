"""Tier 2 performance benchmarks for vendored smartmoneyconcepts library.

Per DEC-508 + CHECKLIST #71 Tier 2 mandate (performance sub-category).
Complements test_smartmoneyconcepts_integration.py's wall-time budget tests
with focused micro-benchmarks: per-primitive calls/sec, scaling vs bar count,
memory footprint, repeatability + composite pipeline throughput. Phase 1B-alpha
target: ~1937 tickers x full pipeline must fit comfortably within laptop
parallelization (4-8 cores) over a single overnight window.

Sub-categories:
  1. Calls-per-second throughput on canonical 1300-bar frame
  2. Bar-count scaling (linear vs quadratic)
  3. Repeatability variance across N runs (warmup + steady-state)
  4. Memory footprint (rough - using output frame size)
  5. Universe-wide extrapolation gating

Run: pytest backtest/tests/test_smartmoneyconcepts_performance.py -v
"""
from __future__ import annotations

import os
os.environ.setdefault("SMC_CREDIT", "0")

import gc
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from smartmoneyconcepts import smc

REPO = Path(__file__).resolve().parents[2]
OHLCV_DIR = REPO / "backtest" / "data" / "cache" / "ohlcv"


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def load_real_or_skip(ticker: str) -> pd.DataFrame:
    p = OHLCV_DIR / f"{ticker}.parquet"
    if not p.is_file():
        pytest.skip(f"{ticker} not cached")
    df = pd.read_parquet(p)
    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
        except Exception:
            pytest.skip(f"{ticker} index not date-coercible")
    return df


def synthetic_ohlcv(n: int, seed: int = 42, vol: float = 0.015) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    returns = rng.normal(0.0003, vol, n)
    prices = 100 * np.exp(np.cumsum(returns))
    daily_vol = np.abs(rng.normal(0, vol * 0.7, n))
    high = prices * (1 + daily_vol)
    low = prices * (1 - daily_vol)
    open_ = prices * (1 + rng.normal(0, vol * 0.3, n))
    close = prices * (1 + rng.normal(0, vol * 0.3, n))
    high = np.maximum(high, np.maximum(open_, close))
    low = np.minimum(low, np.minimum(open_, close))
    df = pd.DataFrame({
        "open": open_, "high": high, "low": low, "close": close,
        "volume": rng.uniform(1e6, 1e7, n),
    }, index=pd.date_range("2021-01-01", periods=n, freq="B"))
    df.index.name = "date"
    return df


def _time_call(fn, *args, n_runs: int = 1, **kwargs) -> float:
    """Return mean elapsed seconds over n_runs."""
    timings = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        fn(*args, **kwargs)
        timings.append(time.perf_counter() - t0)
    return float(np.mean(timings))


def _bench(fn, *args, n_runs: int = 5, **kwargs) -> dict:
    """Return mean / min / max / std elapsed seconds."""
    gc.collect()
    timings = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        fn(*args, **kwargs)
        timings.append(time.perf_counter() - t0)
    arr = np.array(timings)
    return {
        "mean": float(arr.mean()),
        "min": float(arr.min()),
        "max": float(arr.max()),
        "std": float(arr.std()),
        "n": n_runs,
    }


# Targets - chosen to allow Phase 1B-alpha full-universe sweep in <8h sequential
# (parallel 4x brings it under 2h). Headroom is generous; if these tighten
# materially under refactoring, surface as a finding.
THROUGHPUT_MIN_CALLS_PER_SEC = {
    "fvg": 1.0,                  # >=1 call/sec on 1300-bar frame
    "swing_highs_lows": 1.0,
    "bos_choch": 1.0,
    "ob": 1.0,
    "liquidity": 1.0,
    "previous_high_low": 1.0,
    "retracements": 1.0,
}

PER_PRIMITIVE_SEC_BUDGET = 1.0
REPEATABILITY_CV_MAX = 1.0  # std/mean of timings <= 1.0 (loose - accounts for cold-cache + Windows)


# =============================================================================
# 1. CALLS-PER-SECOND THROUGHPUT
# =============================================================================


def test_throughput_fvg_synthetic_1300_bars():
    """smc.fvg on 1300 synthetic bars should sustain >=1 call/sec."""
    df = synthetic_ohlcv(1300, seed=42)
    bench = _bench(smc.fvg, df, n_runs=3)
    cps = 1.0 / bench["mean"] if bench["mean"] > 0 else float("inf")
    assert cps >= THROUGHPUT_MIN_CALLS_PER_SEC["fvg"], (
        f"fvg throughput {cps:.2f} calls/sec < target {THROUGHPUT_MIN_CALLS_PER_SEC['fvg']} "
        f"(mean={bench['mean']:.3f}s, runs={bench['n']})"
    )


def test_throughput_swing_synthetic_1300_bars():
    df = synthetic_ohlcv(1300, seed=42)
    bench = _bench(smc.swing_highs_lows, df, n_runs=3, swing_length=50)
    cps = 1.0 / bench["mean"] if bench["mean"] > 0 else float("inf")
    assert cps >= THROUGHPUT_MIN_CALLS_PER_SEC["swing_highs_lows"], (
        f"swing_highs_lows throughput {cps:.2f} calls/sec, mean={bench['mean']:.3f}s"
    )


def test_throughput_bos_choch_synthetic_1300_bars():
    df = synthetic_ohlcv(1300, seed=42)
    sw = smc.swing_highs_lows(df, swing_length=50)
    bench = _bench(smc.bos_choch, df, sw, n_runs=3)
    cps = 1.0 / bench["mean"] if bench["mean"] > 0 else float("inf")
    assert cps >= THROUGHPUT_MIN_CALLS_PER_SEC["bos_choch"], (
        f"bos_choch throughput {cps:.2f} calls/sec, mean={bench['mean']:.3f}s"
    )


def test_throughput_ob_synthetic_1300_bars():
    df = synthetic_ohlcv(1300, seed=42)
    sw = smc.swing_highs_lows(df, swing_length=50)
    bench = _bench(smc.ob, df, sw, n_runs=3)
    cps = 1.0 / bench["mean"] if bench["mean"] > 0 else float("inf")
    assert cps >= THROUGHPUT_MIN_CALLS_PER_SEC["ob"], (
        f"ob throughput {cps:.2f} calls/sec, mean={bench['mean']:.3f}s"
    )


def test_throughput_liquidity_synthetic_1300_bars():
    df = synthetic_ohlcv(1300, seed=42)
    sw = smc.swing_highs_lows(df, swing_length=50)
    bench = _bench(smc.liquidity, df, sw, n_runs=3)
    cps = 1.0 / bench["mean"] if bench["mean"] > 0 else float("inf")
    assert cps >= THROUGHPUT_MIN_CALLS_PER_SEC["liquidity"], (
        f"liquidity throughput {cps:.2f} calls/sec, mean={bench['mean']:.3f}s"
    )


def test_throughput_previous_high_low_synthetic_1300_bars():
    df = synthetic_ohlcv(1300, seed=42)
    bench = _bench(smc.previous_high_low, df, "1D", n_runs=3)
    cps = 1.0 / bench["mean"] if bench["mean"] > 0 else float("inf")
    assert cps >= THROUGHPUT_MIN_CALLS_PER_SEC["previous_high_low"], (
        f"previous_high_low throughput {cps:.2f} calls/sec, mean={bench['mean']:.3f}s"
    )


def test_throughput_retracements_synthetic_1300_bars():
    df = synthetic_ohlcv(1300, seed=42)
    sw = smc.swing_highs_lows(df, swing_length=50)
    bench = _bench(smc.retracements, df, sw, n_runs=3)
    cps = 1.0 / bench["mean"] if bench["mean"] > 0 else float("inf")
    assert cps >= THROUGHPUT_MIN_CALLS_PER_SEC["retracements"], (
        f"retracements throughput {cps:.2f} calls/sec, mean={bench['mean']:.3f}s"
    )


# =============================================================================
# 2. BAR-COUNT SCALING (LINEAR vs QUADRATIC)
# =============================================================================


def test_fvg_scales_subquadratically_with_bars():
    """fvg(N=2000) / fvg(N=500) should be <16x (i.e., < O(N^2) - ideally near 4x)."""
    df_small = synthetic_ohlcv(500, seed=42)
    df_large = synthetic_ohlcv(2000, seed=42)
    t_small = _time_call(smc.fvg, df_small, n_runs=3)
    t_large = _time_call(smc.fvg, df_large, n_runs=3)
    if t_small <= 0:
        pytest.skip("micro-timings too noisy")
    ratio = t_large / t_small
    # 4x bars -> ideally 4x time (linear); reject if >16x (quadratic).
    assert ratio < 16, (
        f"fvg scaling ratio (2000/500 bars) = {ratio:.1f}x - "
        f"appears quadratic (t_small={t_small:.3f}s, t_large={t_large:.3f}s)"
    )


def test_swing_scales_subquadratically_with_bars():
    df_small = synthetic_ohlcv(500, seed=42)
    df_large = synthetic_ohlcv(2000, seed=42)
    t_small = _time_call(smc.swing_highs_lows, df_small, n_runs=3, swing_length=50)
    t_large = _time_call(smc.swing_highs_lows, df_large, n_runs=3, swing_length=50)
    if t_small <= 0:
        pytest.skip("micro-timings too noisy")
    ratio = t_large / t_small
    assert ratio < 16, (
        f"swing scaling ratio (2000/500 bars) = {ratio:.1f}x - appears quadratic"
    )


def test_bos_choch_scales_subquadratically_with_bars():
    df_small = synthetic_ohlcv(500, seed=42)
    df_large = synthetic_ohlcv(2000, seed=42)
    sw_small = smc.swing_highs_lows(df_small, swing_length=50)
    sw_large = smc.swing_highs_lows(df_large, swing_length=50)
    t_small = _time_call(smc.bos_choch, df_small, sw_small, n_runs=3)
    t_large = _time_call(smc.bos_choch, df_large, sw_large, n_runs=3)
    if t_small <= 0:
        pytest.skip("micro-timings too noisy")
    ratio = t_large / t_small
    assert ratio < 25, (
        f"bos_choch scaling ratio (2000/500 bars) = {ratio:.1f}x - looser bound since "
        f"swing-pair iteration is Nxk"
    )


# =============================================================================
# 3. REPEATABILITY VARIANCE
# =============================================================================


def test_fvg_repeatability_variance_bounded():
    """Across 10 runs, fvg timing CV (std/mean) should be bounded."""
    df = synthetic_ohlcv(1000, seed=42)
    bench = _bench(smc.fvg, df, n_runs=10)
    cv = bench["std"] / bench["mean"] if bench["mean"] > 0 else 0
    assert cv < REPEATABILITY_CV_MAX, (
        f"fvg timing CV {cv:.2f} > {REPEATABILITY_CV_MAX} - unstable runtime "
        f"(mean={bench['mean']:.3f}s std={bench['std']:.3f}s)"
    )


def test_swing_repeatability_variance_bounded():
    df = synthetic_ohlcv(1000, seed=42)
    bench = _bench(smc.swing_highs_lows, df, n_runs=10, swing_length=50)
    cv = bench["std"] / bench["mean"] if bench["mean"] > 0 else 0
    assert cv < REPEATABILITY_CV_MAX, (
        f"swing_highs_lows timing CV {cv:.2f} > {REPEATABILITY_CV_MAX}"
    )


def test_fvg_warmup_then_steady_state():
    """Warmup run should be <=5x slower than steady-state - no degenerate
    cold-cache spike (some warmup is expected on Windows)."""
    df = synthetic_ohlcv(1000, seed=42)
    cold = _time_call(smc.fvg, df, n_runs=1)
    warm = _time_call(smc.fvg, df, n_runs=5)
    if warm <= 0:
        pytest.skip("micro-timings too noisy")
    ratio = cold / warm
    assert ratio < 5.0, (
        f"Cold-vs-warm ratio {ratio:.1f}x exceeds 5x - possible JIT / lazy-import overhead "
        f"(cold={cold:.3f}s warm={warm:.3f}s)"
    )


# =============================================================================
# 4. MEMORY FOOTPRINT (rough - output frame size)
# =============================================================================


def test_fvg_output_memory_reasonable():
    """Output frame should be O(N) bars x ~4 columns x 8 bytes. For 1300 bars
    that's ~40 KB. Reject >1 MB as pathological."""
    df = synthetic_ohlcv(1300, seed=42)
    res = smc.fvg(df)
    mem_bytes = res.memory_usage(deep=True).sum()
    mem_mb = mem_bytes / 1_048_576
    assert mem_mb < 1.0, f"fvg output memory {mem_mb:.2f} MB > 1 MB for 1300 bars"


def test_full_pipeline_output_memory_reasonable():
    """Full pipeline output (7 frames) should be <10 MB for a 1300-bar input."""
    df = synthetic_ohlcv(1300, seed=42)
    sw = smc.swing_highs_lows(df, swing_length=50)
    frames = {
        "fvg": smc.fvg(df),
        "swings": sw,
        "bos_choch": smc.bos_choch(df, sw),
        "ob": smc.ob(df, sw),
        "liquidity": smc.liquidity(df, sw),
        "previous_high_low": smc.previous_high_low(df, "1D"),
        "retracements": smc.retracements(df, sw),
    }
    total_bytes = sum(f.memory_usage(deep=True).sum() for f in frames.values())
    total_mb = total_bytes / 1_048_576
    assert total_mb < 10.0, (
        f"Full pipeline output memory {total_mb:.2f} MB > 10 MB for 1300 bars - "
        f"unexpected memory bloat"
    )


# =============================================================================
# 5. UNIVERSE-WIDE EXTRAPOLATION GATING
# =============================================================================


def test_phase1b_universe_sequential_budget():
    """1937 tickers x full pipeline @ measured throughput should fit <10 h sequential
    (parallel 4x brings it under 3 h on laptop). Soft Phase 1B-alpha budget."""
    df = synthetic_ohlcv(1300, seed=42)
    sw = smc.swing_highs_lows(df, swing_length=50)

    def _pipeline(df, sw):
        smc.fvg(df)
        smc.bos_choch(df, sw)
        smc.ob(df, sw)
        smc.liquidity(df, sw)
        smc.previous_high_low(df, "1D")
        smc.retracements(df, sw)

    elapsed = _time_call(_pipeline, df, sw, n_runs=3)
    sequential_hours = 1937 * elapsed / 3600
    assert sequential_hours < 10, (
        f"Phase 1B-alpha sequential pipeline estimate: {sequential_hours:.2f} h "
        f"(per-ticker = {elapsed:.3f} s x 1937 tickers). Exceeds 10 h soft budget."
    )


def test_real_aapl_full_pipeline_budget():
    """End-to-end on a real cached frame should complete inside per-primitive budget."""
    df = load_real_or_skip("AAPL")
    if len(df) < 200:
        pytest.skip("AAPL too short")

    def _pipeline(df):
        sw = smc.swing_highs_lows(df, swing_length=20)
        smc.fvg(df)
        smc.bos_choch(df, sw)
        smc.ob(df, sw)
        smc.liquidity(df, sw)
        smc.retracements(df, sw)

    elapsed = _time_call(_pipeline, df, n_runs=2)
    assert elapsed < PER_PRIMITIVE_SEC_BUDGET * 7, (
        f"AAPL full pipeline {elapsed:.3f}s exceeds {PER_PRIMITIVE_SEC_BUDGET*7:.1f}s soft budget"
    )


def test_throughput_aggregate_real_tickers():
    """Across MSFT/TSLA/ABNB/NVDA, FVG must sustain >=0.5 calls/sec mean."""
    timings = []
    for ticker in ["MSFT", "TSLA", "ABNB", "NVDA"]:
        try:
            df = load_real_or_skip(ticker)
        except pytest.skip.Exception:
            continue
        if len(df) < 500:
            continue
        timings.append(_time_call(smc.fvg, df, n_runs=2))
    if not timings:
        pytest.skip("no real tickers available")
    mean_elapsed = float(np.mean(timings))
    cps = 1.0 / mean_elapsed if mean_elapsed > 0 else float("inf")
    assert cps >= 0.5, (
        f"Aggregate FVG throughput {cps:.2f} calls/sec across "
        f"{len(timings)} tickers < 0.5 target"
    )


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
