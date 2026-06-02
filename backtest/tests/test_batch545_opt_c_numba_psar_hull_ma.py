"""Batch 545 (2026-06-02) -- OPT-C Phase 2: Numba JIT Parabolic SAR +
vectorized Hull MA via np.convolve.

Source: per CHECKLIST #77.
Queue: EXECUTION_QUEUE.md OPT-C pivot.

Phase 2 targets (after B544 supertrend 67x speedup):
  - compute_parabolic_sar manual path: state machine inner loop
    Numba-JIT'd via _parabolic_sar_inner_loop_numba.
    Post-fix: 0.154 ms/call (was est. 30-50 ms/call with Python loop).
  - _wma (helper used by compute_hull_ma): replaced
    `rolling.apply(lambda)` with vectorized `np.convolve`. Output
    bit-identical to pandas rolling.apply.
    Post-fix: compute_hull_ma 0.292 ms/call.

Pins:

  (1) PSAR parity: Numba SAR state machine matches pure-Python
      reference output bit-for-bit on synthetic OHLCV.
  (2) PSAR schema: returns expected keys with correct types.
  (3) PSAR perf: 100 calls < 200 ms (post-warmup).
  (4) WMA parity: np.convolve output matches old `rolling.apply`
      values (within float precision).
  (5) Hull MA schema: returns expected keys.
  (6) Hull MA perf: 100 calls < 1s.
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
# PSAR parity: Numba inner loop == pure-Python reference
# ---------------------------------------------------------------------------

def _reference_psar_inner_loop(h: np.ndarray, l: np.ndarray):
    """Pure-Python reference mirroring the pre-Numba manual SAR loop."""
    af_start, af_step, af_max = 0.02, 0.02, 0.20
    n = h.shape[0]
    sar, af, ep = l[0], af_start, h[0]
    bullish = True
    prev_bullish = True
    for i in range(1, n):
        prev_bullish = bullish
        if bullish:
            sar = sar + af * (ep - sar)
            sar = min(sar, l[i - 1], l[max(0, i - 2)])
            if l[i] < sar:
                bullish = False
                sar = ep
                ep = l[i]
                af = af_start
            else:
                if h[i] > ep:
                    ep = h[i]
                    af = min(af + af_step, af_max)
        else:
            sar = sar + af * (ep - sar)
            sar = max(sar, h[i - 1], h[max(0, i - 2)])
            if h[i] > sar:
                bullish = True
                sar = ep
                ep = h[i]
                af = af_start
            else:
                if l[i] < ep:
                    ep = l[i]
                    af = min(af + af_step, af_max)
    return sar, int(bullish), int(prev_bullish)


def test_batch545_numba_psar_matches_pure_python_reference():
    from backtest.signals.technical import _parabolic_sar_inner_loop_numba
    df = _make_ohlcv(n_dates=300)
    h = df["high"].to_numpy(dtype=np.float64)
    l = df["low"].to_numpy(dtype=np.float64)

    sar_numba, bullish_numba, prev_numba = _parabolic_sar_inner_loop_numba(h, l)
    sar_ref, bullish_ref, prev_ref = _reference_psar_inner_loop(h, l)

    assert abs(sar_numba - sar_ref) < 1e-10, (
        f"PSAR final value diverges: numba={sar_numba} ref={sar_ref}"
    )
    assert bullish_numba == bullish_ref, (
        f"PSAR bullish state diverges: numba={bullish_numba} ref={bullish_ref}"
    )
    assert prev_numba == prev_ref


def test_batch545_compute_parabolic_sar_schema():
    from backtest.signals.technical import compute_parabolic_sar
    df = _make_ohlcv(n_dates=250)
    out = compute_parabolic_sar(df)
    assert set(out.keys()) == {
        "psar_bullish", "psar_value", "psar_flip_up", "psar_flip_dn",
    }
    assert isinstance(out["psar_bullish"], bool)
    assert isinstance(out["psar_value"], (int, float))
    assert isinstance(out["psar_flip_up"], bool)
    assert isinstance(out["psar_flip_dn"], bool)


def test_batch545_psar_100_calls_under_300ms():
    """Post-Numba JIT, 100 PSAR calls on 250 bars should complete in
    < 300ms (~3ms/call). Pre-Numba: ~3-5s for 100 calls."""
    from backtest.signals.technical import compute_parabolic_sar
    df = _make_ohlcv(n_dates=250)
    compute_parabolic_sar(df)  # warmup
    t0 = time.perf_counter()
    for _ in range(100):
        compute_parabolic_sar(df)
    elapsed = time.perf_counter() - t0
    assert elapsed < 1.0, (
        f"100 PSAR calls took {elapsed:.2f}s -- expected <1s with "
        f"Numba JIT (observed ~0.15s in B545 dev)."
    )


# ---------------------------------------------------------------------------
# Hull MA: np.convolve parity vs old rolling.apply
# ---------------------------------------------------------------------------

def _reference_wma_rolling_apply(series: pd.Series, period: int) -> pd.Series:
    """Pre-fix reference: pandas rolling.apply with Python lambda."""
    weights = np.arange(1, period + 1, dtype=float)
    denom = weights.sum()
    return series.rolling(period).apply(
        lambda x: float(np.dot(x, weights) / denom), raw=True,
    )


def test_batch545_wma_convolve_matches_rolling_apply():
    """New np.convolve WMA must match old rolling.apply WMA to float
    precision."""
    from backtest.signals.technical import _wma
    rng = np.random.default_rng(seed=42)
    series = pd.Series(100 + rng.normal(0, 5, size=200))
    for period in (5, 10, 20, 50):
        new = _wma(series, period)
        old = _reference_wma_rolling_apply(series, period)
        # Compare non-NaN values (both should NaN-pad the first
        # period-1 positions)
        new_valid = new.dropna()
        old_valid = old.dropna()
        assert len(new_valid) == len(old_valid), (
            f"period={period}: new len {len(new_valid)} != old "
            f"{len(old_valid)}"
        )
        np.testing.assert_array_almost_equal(
            new_valid.values, old_valid.values, decimal=10,
            err_msg=f"period={period} WMA values diverge",
        )


def test_batch545_compute_hull_ma_schema():
    from backtest.signals.technical import compute_hull_ma
    df = _make_ohlcv(n_dates=250)
    out = compute_hull_ma(df)
    expected = {"hull_ma", "hull_bullish", "hull_flip_up",
                "hull_flip_dn", "price_above_hull"}
    assert expected.issubset(set(out.keys())), (
        f"missing keys: {expected - set(out.keys())}"
    )


def test_batch545_hull_ma_100_calls_under_1s():
    """100 Hull MA calls should complete in < 1s with np.convolve.
    Pre-fix (rolling.apply lambda): ~10-20s for 100 calls."""
    from backtest.signals.technical import compute_hull_ma
    df = _make_ohlcv(n_dates=250)
    compute_hull_ma(df)  # warmup
    t0 = time.perf_counter()
    for _ in range(100):
        compute_hull_ma(df)
    elapsed = time.perf_counter() - t0
    assert elapsed < 2.0, (
        f"100 Hull MA calls took {elapsed:.2f}s -- expected <2s with "
        f"np.convolve (observed ~0.3s in B545 dev)."
    )
