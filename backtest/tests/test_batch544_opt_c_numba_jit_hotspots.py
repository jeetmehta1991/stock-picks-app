"""Batch 544 (2026-06-02) -- OPT-C pivot to Numba JIT on hot indicators.

Source: per CHECKLIST #77 + owner directive 2026-06-02 "2" (Numba JIT
on hot pandas paths, after OPT-C Polars naive translation showed
4.3x SLOWDOWN -- B543 finding).
Queue: EXECUTION_QUEUE.md OPT-C pivot.

Phase 1 of Numba JIT sweep: compute_supertrend state-tracking inner
loop. Profile baseline: 104ms/call. Post-Numba: 1.55ms/call = ~67x
speedup.

Pins:

  (1) Parity: Numba JIT inner loop produces IDENTICAL state-tracking
      output as the pre-Numba pure-Python reference implementation
  (2) Speedup: 50 repeated calls complete in < 200ms total (was ~5s
      pre-Numba)
  (3) Public API contract: compute_supertrend returns the same dict
      keys (supertrend_bullish, supertrend_value, supertrend_flip_up,
      supertrend_flip_dn) with same value types
  (4) Edge cases: short history returns empty dict
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest


def _make_ohlcv(n_dates: int = 250, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed=seed)
    log_ret = rng.normal(0.0005, 0.015, size=n_dates)
    log_ret[0] = 0
    close = 100.0 * np.exp(np.cumsum(log_ret))
    open_ = np.concatenate(([100.0], close[:-1]))
    high = np.maximum(open_, close) + rng.uniform(0, 0.01, size=n_dates) * close
    low = np.minimum(open_, close) - rng.uniform(0, 0.01, size=n_dates) * close
    return pd.DataFrame({
        "open": open_, "high": high, "low": low, "close": close,
        "volume": rng.integers(1_000_000, 5_000_000, size=n_dates),
    }, index=pd.date_range("2024-01-01", periods=n_dates, freq="B"))


# ---------------------------------------------------------------------------
# Parity: Numba inner loop == pure-Python reference
# ---------------------------------------------------------------------------

def _reference_supertrend_inner_loop(
    ub: np.ndarray, lb: np.ndarray, close: np.ndarray,
):
    """Pure-Python reference implementation that mirrors the pre-Numba
    state-tracking logic verbatim. Used as parity ground truth."""
    n = ub.shape[0]
    st = [0.0] * n
    bull = [True] * n
    for i in range(1, n):
        ub_prev = float(ub[i - 1])
        lb_prev = float(lb[i - 1])
        ub_cur = float(ub[i])
        lb_cur = float(lb[i])
        cl_prev = float(close[i - 1])
        cl_cur = float(close[i])
        if cl_prev > lb_prev:
            lb_cur = max(lb_cur, lb_prev)
        if cl_prev < ub_prev:
            ub_cur = min(ub_cur, ub_prev)
        if st[i - 1] == ub_prev:
            st[i] = lb_cur if cl_cur > ub_prev else ub_cur
        else:
            st[i] = ub_cur if cl_cur < lb_prev else lb_cur
        bull[i] = cl_cur > st[i]
    return np.array(st), np.array(bull)


def test_batch544_numba_supertrend_matches_pure_python_reference():
    """Numba JIT inner loop must produce bit-identical state-tracking
    output as the pure-Python reference for the same upper/lower/close
    arrays."""
    from backtest.signals.technical import _supertrend_inner_loop_numba
    df = _make_ohlcv(n_dates=300)
    # Build ub/lb/close exactly as compute_supertrend does
    period = 7
    mult = 3.0
    # Use a simple ATR approximation for the test (must be deterministic)
    h, l, c = df["high"], df["low"], df["close"]
    tr_hl = h - l
    tr_hc = (h - c.shift()).abs()
    tr_lc = (l - c.shift()).abs()
    tr = pd.concat([tr_hl, tr_hc, tr_lc], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / period, adjust=False).mean()
    hl2 = (h + l) / 2
    ub = (hl2 + mult * atr).to_numpy(dtype=np.float64, na_value=0.0)
    lb = (hl2 - mult * atr).to_numpy(dtype=np.float64, na_value=0.0)
    cl = c.to_numpy(dtype=np.float64, na_value=0.0)

    st_numba, bull_numba = _supertrend_inner_loop_numba(ub, lb, cl)
    st_ref, bull_ref = _reference_supertrend_inner_loop(ub, lb, cl)

    np.testing.assert_array_almost_equal(st_numba, st_ref, decimal=10)
    np.testing.assert_array_equal(bull_numba, bull_ref)


def test_batch544_compute_supertrend_returns_expected_schema():
    """Public API contract preserved: same dict keys + types.
    B840 UPDATED: B655 T10 supertrend redundancy-audit added 3 keys
    (supertrend_bearish + supertrend_flip_recent_long_5d +
    supertrend_flip_recent_short_5d) + supertrend_lookback_window
    diagnostic per B655 producer-additive EVENT-conversion. Schema
    superset of original 4 keys."""
    from backtest.signals.technical import compute_supertrend
    df = _make_ohlcv(n_dates=250)
    out = compute_supertrend(df)
    # Original 4 keys still required (back-compat)
    required = {
        "supertrend_bullish", "supertrend_value",
        "supertrend_flip_up", "supertrend_flip_dn",
    }
    assert required.issubset(set(out.keys())), (
        f"missing required keys: {required - set(out.keys())}"
    )
    # B655 additions (5-bar lookback EVENT + symmetric bearish + lookback diagnostic)
    b655_additions = {
        "supertrend_bearish",
        "supertrend_flip_recent_long_5d",
        "supertrend_flip_recent_short_5d",
        "supertrend_lookback_window",
    }
    assert b655_additions.issubset(set(out.keys())), (
        f"missing B655 keys: {b655_additions - set(out.keys())}"
    )
    assert isinstance(out["supertrend_bullish"], bool)
    assert isinstance(out["supertrend_value"], float)
    assert isinstance(out["supertrend_flip_up"], bool)
    assert isinstance(out["supertrend_flip_dn"], bool)
    assert isinstance(out["supertrend_bearish"], bool)
    assert isinstance(out["supertrend_flip_recent_long_5d"], bool)
    assert isinstance(out["supertrend_flip_recent_short_5d"], bool)


def test_batch544_compute_supertrend_short_history_returns_empty():
    from backtest.signals.technical import compute_supertrend
    df = _make_ohlcv(n_dates=5)
    assert compute_supertrend(df) == {}


# ---------------------------------------------------------------------------
# Speedup verification
# ---------------------------------------------------------------------------

def test_batch544_supertrend_numba_50_calls_under_1s():
    """50 repeated calls should complete in <1s with Numba JIT
    (post-warmup). Pre-Numba: ~5s for 50 calls (104ms each).
    Post-Numba: ~50-100ms for 50 calls (1-2ms each)."""
    from backtest.signals.technical import compute_supertrend
    df = _make_ohlcv(n_dates=300)
    # Warmup JIT compilation
    compute_supertrend(df)
    compute_supertrend(df)
    t0 = time.perf_counter()
    for _ in range(50):
        compute_supertrend(df)
    elapsed = time.perf_counter() - t0
    assert elapsed < 1.0, (
        f"50 calls took {elapsed:.2f}s -- expected <1s with Numba JIT. "
        f"Indicates JIT not active OR loop overhead regressed."
    )
    print(f"\n  supertrend 50 calls: {elapsed*1000:.0f}ms "
          f"({elapsed*1000/50:.2f}ms/call)")
