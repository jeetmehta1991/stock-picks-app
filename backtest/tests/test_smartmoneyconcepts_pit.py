"""
Tier 1 PIT correctness regression for vendored smartmoneyconcepts library.

🔴 CRITICAL category per DEC-508 + CHECKLIST #71 Phase A mandate.

Per DEC-261 N+1 lag rule: signal at bar D MUST be IDENTICAL whether computed at
as_of=D vs as_of=D+50. If the library uses future bars to compute signals,
this test will fail.

Run: pytest backtest/tests/test_smartmoneyconcepts_pit.py -v
"""
import os
os.environ.setdefault("SMC_CREDIT", "0")

from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import pytest

from smartmoneyconcepts import smc


def synthetic_ohlcv_5y(seed: int = 42) -> pd.DataFrame:
    """Generate 5 years of synthetic OHLCV (~1260 trading days) with realistic dynamics."""
    np.random.seed(seed)
    n = 1260
    dates = pd.date_range("2021-05-05", periods=n, freq="B")
    # Geometric Brownian motion + occasional jumps for FVG opportunities
    drift = 0.0003
    vol = 0.015
    returns = np.random.normal(drift, vol, n)
    # Add ~10 jumps (gap-creating) to ensure FVG patterns appear
    jump_indices = np.random.choice(n, 10, replace=False)
    returns[jump_indices] += np.random.choice([-0.04, 0.04], 10)
    prices = 100 * np.exp(np.cumsum(returns))

    daily_vol = np.abs(np.random.normal(0, 0.01, n))
    high = prices * (1 + daily_vol)
    low = prices * (1 - daily_vol)
    open_ = prices * (1 + np.random.normal(0, 0.005, n))
    close = prices * (1 + np.random.normal(0, 0.005, n))
    # Ensure high/low bounds
    high = np.maximum(high, np.maximum(open_, close))
    low = np.minimum(low, np.minimum(open_, close))

    df = pd.DataFrame({
        "open": open_, "high": high, "low": low, "close": close,
        "volume": np.random.uniform(1e6, 1e7, n),
    }, index=dates)
    df.index.name = "date"
    return df


# ─────────────────────────────────────────────────────────────────────────────
# PIT regression for FVG
# ─────────────────────────────────────────────────────────────────────────────

def test_fvg_pit_correctness_no_lookahead():
    """🔴 CRITICAL: FVG signal at bar D must be identical when computed at as_of=D
    vs as_of=D+50. If library uses future bars, this test fails — lookahead bias
    detected per DEC-261 N+1 lag rule.
    """
    full_df = synthetic_ohlcv_5y(seed=42)
    n = len(full_df)
    # Test cutoff: midpoint of synthetic period
    cutoff_idx = n // 2
    cutoff_date = full_df.index[cutoff_idx]

    # Compute FVG on TRUNCATED data (data through cutoff only)
    truncated = full_df.iloc[: cutoff_idx + 1]
    fvg_truncated = smc.fvg(truncated)

    # Compute FVG on FULL data, then slice to same cutoff window
    fvg_full = smc.fvg(full_df)
    fvg_full_sliced = fvg_full.iloc[: cutoff_idx + 1]

    # CRITICAL ASSERTION: signals at bars 0..cutoff_idx must be identical between
    # truncated computation and full-then-sliced computation
    fvg_col_t = fvg_truncated.iloc[:, 0]
    fvg_col_f = fvg_full_sliced.iloc[:, 0]

    # Compare element-by-element; both NaN values count as equal
    pit_violations = []
    for i in range(len(fvg_col_t)):
        v_t = fvg_col_t.iloc[i]
        v_f = fvg_col_f.iloc[i]
        if pd.isna(v_t) and pd.isna(v_f):
            continue
        if pd.isna(v_t) != pd.isna(v_f):
            pit_violations.append((i, v_t, v_f))
        elif not pd.isna(v_t) and v_t != v_f:
            pit_violations.append((i, v_t, v_f))

    assert len(pit_violations) == 0, \
        (f"🔴 PIT VIOLATION DETECTED: {len(pit_violations)} bars where FVG signal "
         f"differs between truncated vs full-then-sliced computation. "
         f"First 5 violations: {pit_violations[:5]}. "
         f"This indicates lookahead bias — library uses future bars beyond the "
         f"FVG bar to determine its signal value. Per DEC-261, fix or sandbox "
         f"the library before strategies consume FVG signals.")


def test_swing_highs_lows_pit_correctness():
    """🔴 PIT regression: swing_highs_lows requires lookahead by design (a swing
    high needs N bars after it to confirm). This test EXPECTS the library to
    eventually backfill new swings as data extends, but EXISTING swings (at
    bars far before cutoff) should NOT change.

    Important caveat: swings detected within `swing_length` bars before cutoff
    may not yet be confirmed; ignore those.
    """
    full_df = synthetic_ohlcv_5y(seed=42)
    n = len(full_df)
    cutoff_idx = n // 2
    swing_length = 50

    truncated = full_df.iloc[: cutoff_idx + 1]
    swings_truncated = smc.swing_highs_lows(truncated, swing_length=swing_length)
    swings_full_sliced = smc.swing_highs_lows(full_df, swing_length=swing_length).iloc[: cutoff_idx + 1]

    # Compare bars BEFORE the lookback window (bars 0 to cutoff - swing_length)
    safe_window_end = cutoff_idx - swing_length
    if safe_window_end <= 0:
        pytest.skip("Cutoff too early for safe window")

    col_t = swings_truncated.iloc[: safe_window_end, 0]
    col_f = swings_full_sliced.iloc[: safe_window_end, 0]

    pit_violations = []
    for i in range(len(col_t)):
        v_t = col_t.iloc[i]
        v_f = col_f.iloc[i]
        if pd.isna(v_t) and pd.isna(v_f):
            continue
        if pd.isna(v_t) != pd.isna(v_f) or (not pd.isna(v_t) and v_t != v_f):
            pit_violations.append((i, v_t, v_f))

    # In safe window (>swing_length before cutoff), values must agree
    assert len(pit_violations) == 0, \
        (f"🔴 PIT VIOLATION in swing_highs_lows safe window: {len(pit_violations)} "
         f"bars differ. swing_length={swing_length}, safe_window_end={safe_window_end}. "
         f"First 5: {pit_violations[:5]}. Library may use look-back beyond swing_length.")


# ─────────────────────────────────────────────────────────────────────────────
# Lookahead detection helper
# ─────────────────────────────────────────────────────────────────────────────

def test_pit_test_infrastructure_works():
    """Sanity: the PIT comparison utility correctly detects intentional lookahead."""
    full = synthetic_ohlcv_5y(seed=42)
    cutoff_idx = len(full) // 2

    # Construct adversarial case: signal that DOES use future data (last close)
    full_signal_future = pd.Series(
        [full["close"].iloc[-1]] * len(full), index=full.index
    )  # constant = last value (future-leaked)

    truncated_signal_future = pd.Series(
        [full.iloc[: cutoff_idx + 1]["close"].iloc[-1]] * (cutoff_idx + 1),
        index=full.index[: cutoff_idx + 1],
    )

    # Truncated and full-sliced WILL differ — sanity that our test infra catches this
    sliced = full_signal_future.iloc[: cutoff_idx + 1]
    assert not (sliced == truncated_signal_future).all(), \
        "Sanity check: future-leak signal should differ between truncated and full"


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
