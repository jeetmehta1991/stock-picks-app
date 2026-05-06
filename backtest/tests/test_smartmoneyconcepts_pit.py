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


# ─────────────────────────────────────────────────────────────────────────────
# PIT regression for the remaining 6 primitives
# Same pattern: compute on truncated vs full-then-sliced; safe window =
# bars at least swing_length BEFORE cutoff so swings are confirmed.
# ─────────────────────────────────────────────────────────────────────────────


def _pit_compare(col_truncated: pd.Series, col_full_sliced: pd.Series) -> list[tuple]:
    """Return list of (idx, val_t, val_f) violations between truncated and full-sliced."""
    violations = []
    for i in range(len(col_truncated)):
        v_t = col_truncated.iloc[i]
        v_f = col_full_sliced.iloc[i]
        if pd.isna(v_t) and pd.isna(v_f):
            continue
        if pd.isna(v_t) != pd.isna(v_f):
            violations.append((i, v_t, v_f))
        elif not pd.isna(v_t) and v_t != v_f:
            violations.append((i, v_t, v_f))
    return violations


def test_bos_choch_pit_correctness():
    """🔴 BOS/CHOCH at bar D (in safe window) must be identical truncated vs full."""
    full = synthetic_ohlcv_5y(seed=42)
    n = len(full)
    cutoff = n // 2
    swing_length = 50

    sw_t = smc.swing_highs_lows(full.iloc[: cutoff + 1], swing_length=swing_length)
    sw_f = smc.swing_highs_lows(full, swing_length=swing_length)
    bc_t = smc.bos_choch(full.iloc[: cutoff + 1], sw_t)
    bc_f = smc.bos_choch(full, sw_f).iloc[: cutoff + 1]

    safe_end = cutoff - swing_length
    if safe_end <= 0:
        pytest.skip("safe window too small")

    for col in ("BOS", "CHOCH"):
        viols = _pit_compare(bc_t[col].iloc[:safe_end], bc_f[col].iloc[:safe_end])
        assert not viols, f"BOS/CHOCH PIT violation in {col}: first 3 = {viols[:3]}"


def test_ob_pit_correctness():
    """🔴 OB signals in safe window must be identical truncated vs full."""
    full = synthetic_ohlcv_5y(seed=42)
    cutoff = len(full) // 2
    swing_length = 50
    sw_t = smc.swing_highs_lows(full.iloc[: cutoff + 1], swing_length=swing_length)
    sw_f = smc.swing_highs_lows(full, swing_length=swing_length)
    ob_t = smc.ob(full.iloc[: cutoff + 1], sw_t)
    ob_f = smc.ob(full, sw_f).iloc[: cutoff + 1]

    safe_end = cutoff - swing_length
    if safe_end <= 0:
        pytest.skip("safe window too small")
    viols = _pit_compare(ob_t["OB"].iloc[:safe_end], ob_f["OB"].iloc[:safe_end])
    assert not viols, f"OB PIT violation: first 3 = {viols[:3]}"


def test_liquidity_pit_correctness():
    """🔴 Liquidity signals in safe window must be identical truncated vs full."""
    full = synthetic_ohlcv_5y(seed=42)
    cutoff = len(full) // 2
    swing_length = 50
    sw_t = smc.swing_highs_lows(full.iloc[: cutoff + 1], swing_length=swing_length)
    sw_f = smc.swing_highs_lows(full, swing_length=swing_length)
    liq_t = smc.liquidity(full.iloc[: cutoff + 1], sw_t)
    liq_f = smc.liquidity(full, sw_f).iloc[: cutoff + 1]

    safe_end = cutoff - swing_length
    if safe_end <= 0:
        pytest.skip("safe window too small")
    viols = _pit_compare(liq_t["Liquidity"].iloc[:safe_end], liq_f["Liquidity"].iloc[:safe_end])
    assert not viols, f"Liquidity PIT violation: first 3 = {viols[:3]}"


@pytest.mark.xfail(
    reason="🔴 PHASE-A FINDING (DEC-508): smc.retracements has lookahead — "
    "Direction signal at bar D differs depending on whether bars D+1..D+N exist. "
    "Library establishes 'direction' retroactively when a new swing confirms. "
    "CONSUMER MITIGATION REQUIRED before Phase 1B uses this signal: lag by ≥1 swing "
    "(typically swing_length bars) OR use Direction only at bars where the next swing "
    "is already detected. Tracked under DEC-508 Phase A risk register.",
    strict=True,
)
def test_retracements_pit_correctness():
    """🔴 Retracements Direction in safe window — KNOWN to fail (lookahead in library)."""
    full = synthetic_ohlcv_5y(seed=42)
    cutoff = len(full) // 2
    swing_length = 50
    sw_t = smc.swing_highs_lows(full.iloc[: cutoff + 1], swing_length=swing_length)
    sw_f = smc.swing_highs_lows(full, swing_length=swing_length)
    ret_t = smc.retracements(full.iloc[: cutoff + 1], sw_t)
    ret_f = smc.retracements(full, sw_f).iloc[: cutoff + 1]

    safe_end = cutoff - swing_length
    if safe_end <= 0:
        pytest.skip("safe window too small")
    viols = _pit_compare(ret_t["Direction"].iloc[:safe_end], ret_f["Direction"].iloc[:safe_end])
    assert not viols, f"Retracements Direction PIT violation: first 3 = {viols[:3]}"


def test_previous_high_low_pit_correctness():
    """🔴 PreviousHigh/Low at bar D must reflect only data ≤ D (no peeking)."""
    full = synthetic_ohlcv_5y(seed=42)
    cutoff = len(full) // 2
    res_t = smc.previous_high_low(full.iloc[: cutoff + 1], "1D")
    res_f = smc.previous_high_low(full, "1D").iloc[: cutoff + 1]

    for col in ("PreviousHigh", "PreviousLow"):
        viols = _pit_compare(res_t[col], res_f[col])
        assert not viols, f"previous_high_low PIT violation in {col}: first 3 = {viols[:3]}"


@pytest.mark.xfail(
    reason="🔴 PHASE-A FINDING (DEC-508): FVG signal is placed on the MIDDLE bar of "
    "a 3-bar pattern, but it cannot be confirmed until bar 3 arrives. So at as_of=199 "
    "with 200 bars, the FVG at bar 199 is invisible; at as_of=200 with 201 bars it "
    "becomes visible. This is a 1-bar lookahead from the consumer perspective. "
    "CONSUMER MITIGATION REQUIRED: shift FVG signals by +1 bar before strategies "
    "consume them (or read FVG at as_of-1 instead of as_of). Tracked under DEC-508 "
    "Phase A + DEC-261 N+1 lag rule.",
    strict=True,
)
def test_fvg_growing_dataframe_appending_preserves_prior_signals():
    """Append a new bar to a 200-bar DF — KNOWN to fail (FVG mid-bar placement is +1-lookahead)."""
    full = synthetic_ohlcv_5y(seed=42)
    base = full.iloc[:200]
    extended = full.iloc[:201]
    fvg_base = smc.fvg(base)
    fvg_ext = smc.fvg(extended).iloc[:200]
    viols = _pit_compare(fvg_base["FVG"], fvg_ext["FVG"])
    assert not viols, f"Appending bar changed prior FVG signals: first 3 = {viols[:3]}"


def test_swing_growing_dataframe_safe_window_invariant():
    """Append 100 bars: swing signals far before the boundary must be unchanged."""
    full = synthetic_ohlcv_5y(seed=42)
    base = full.iloc[:300]
    extended = full.iloc[:400]
    swing_length = 50
    sw_base = smc.swing_highs_lows(base, swing_length=swing_length)
    sw_ext = smc.swing_highs_lows(extended, swing_length=swing_length).iloc[:300]
    safe_end = 300 - swing_length
    viols = _pit_compare(sw_base["HighLow"].iloc[:safe_end], sw_ext["HighLow"].iloc[:safe_end])
    assert not viols, f"Extending DF changed prior swing signals: first 3 = {viols[:3]}"


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
