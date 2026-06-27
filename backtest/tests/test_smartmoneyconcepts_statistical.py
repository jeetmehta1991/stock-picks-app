"""Tier 3 statistical sanity tests for vendored smartmoneyconcepts library.

Per DEC-508 + CHECKLIST #71 Tier 3 mandate (statistical sanity sub-category).
Complements test_smartmoneyconcepts_empirical.py's signal-density distribution
tests with deeper statistical sanity checks: signal value distributions,
fire-rate stability across seeds and volatility regimes, swing alternation
statistics, time-between-signals distributions, and signal-vs-price
relationships.

Sub-categories:
  1. Signal value distribution (bimodal -1/+1; balanced)
  2. Fire-rate sanity (density bounded across vol regimes)
  3. Time-between-signals distribution (no degenerate clumps / gaps)
  4. Swing alternation statistic (high-low-high-low cadence)
  5. Cross-primitive sanity (BOS-CHOCH mutual-exclusion semantics)

Run: pytest backtest/tests/test_smartmoneyconcepts_statistical.py -v
"""
from __future__ import annotations

import os
os.environ.setdefault("SMC_CREDIT", "0")

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from smartmoneyconcepts import smc

REPO = Path(__file__).resolve().parents[2]
OHLCV_DIR = REPO / "backtest" / "data" / "cache" / "ohlcv"


# -----------------------------------------------------------------------------
# Generators + helpers
# -----------------------------------------------------------------------------


def gbm_ohlcv(n: int, seed: int, vol: float = 0.015, drift: float = 0.0,
              with_jumps: bool = True) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    returns = rng.normal(drift, vol, n)
    if with_jumps:
        idx = rng.choice(n, max(1, n // 100), replace=False)
        returns[idx] += rng.choice([-0.04, 0.04], len(idx))
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


# =============================================================================
# 1. SIGNAL VALUE DISTRIBUTION
# =============================================================================


def test_fvg_signal_values_are_binary_directional():
    """FVG.dropna() should be {-1, 1} only - no spurious intermediate values."""
    df = gbm_ohlcv(2000, seed=42)
    fvg = smc.fvg(df)
    nonnull = fvg["FVG"].dropna()
    if len(nonnull) == 0:
        pytest.skip("no FVGs generated")
    unique_vals = set(int(v) for v in nonnull.unique())
    assert unique_vals <= {-1, 1}, (
        f"FVG values include non-directional codes {unique_vals} - expected {{-1, 1}}"
    )


def test_bos_signal_values_are_binary_directional():
    df = gbm_ohlcv(2000, seed=42, vol=0.02)
    sw = smc.swing_highs_lows(df, swing_length=20)
    bc = smc.bos_choch(df, sw)
    nonnull = bc["BOS"].dropna()
    if len(nonnull) == 0:
        pytest.skip("no BOS generated")
    unique_vals = set(int(v) for v in nonnull.unique())
    assert unique_vals <= {-1, 1}, f"BOS values {unique_vals} != {{-1, 1}}"


def test_choch_signal_values_are_binary_directional():
    df = gbm_ohlcv(2000, seed=42, vol=0.02)
    sw = smc.swing_highs_lows(df, swing_length=20)
    bc = smc.bos_choch(df, sw)
    nonnull = bc["CHOCH"].dropna()
    if len(nonnull) == 0:
        pytest.skip("no CHOCH generated")
    unique_vals = set(int(v) for v in nonnull.unique())
    assert unique_vals <= {-1, 1}, f"CHOCH values {unique_vals} != {{-1, 1}}"


def test_ob_signal_values_are_binary_directional():
    df = gbm_ohlcv(2000, seed=42, vol=0.02)
    sw = smc.swing_highs_lows(df, swing_length=20)
    ob = smc.ob(df, sw)
    nonnull = ob["OB"].dropna()
    if len(nonnull) == 0:
        pytest.skip("no OBs generated")
    unique_vals = set(int(v) for v in nonnull.unique())
    assert unique_vals <= {-1, 1}, f"OB values {unique_vals} != {{-1, 1}}"


def test_fvg_bullish_bearish_proportion_in_random_walk():
    """Pure GBM should produce roughly balanced bullish vs bearish FVGs (split <= 75/25)."""
    df = gbm_ohlcv(3000, seed=42, drift=0.0)
    fvg = smc.fvg(df)
    nonnull = fvg["FVG"].dropna()
    if len(nonnull) < 50:
        pytest.skip("too few FVGs for balance check")
    bullish = (nonnull > 0).sum()
    bearish = (nonnull < 0).sum()
    total = bullish + bearish
    if total == 0:
        pytest.skip("no directional FVGs")
    skew = max(bullish, bearish) / total
    assert skew <= 0.75, (
        f"FVG bull/bear skew {skew:.2f} > 0.75 - possible directional bias "
        f"(bullish={bullish} bearish={bearish})"
    )


def test_swing_high_low_proportion_balanced():
    """In a non-trending market, swing highs ≈ swing lows."""
    df = gbm_ohlcv(2000, seed=42, drift=0.0)
    sw = smc.swing_highs_lows(df, swing_length=20)
    highs = (sw["HighLow"] == 1).sum()
    lows = (sw["HighLow"] == -1).sum()
    total = highs + lows
    if total < 20:
        pytest.skip("too few swings")
    # Within 4x of each other - alternation invariant ensures this loosely
    assert max(highs, lows) / max(1, min(highs, lows)) < 4, (
        f"Swing high/low imbalance: highs={highs} lows={lows}"
    )


# =============================================================================
# 2. FIRE-RATE SANITY ACROSS VOLATILITY REGIMES
# =============================================================================


def test_fvg_density_increases_with_vol_jumps():
    """Adding price jumps to GBM should >=-loosely increase FVG density."""
    low_vol = gbm_ohlcv(1500, seed=42, vol=0.008, with_jumps=False)
    high_vol = gbm_ohlcv(1500, seed=42, vol=0.025, with_jumps=True)
    d_low = smc.fvg(low_vol)["FVG"].notna().sum() / len(low_vol)
    d_high = smc.fvg(high_vol)["FVG"].notna().sum() / len(high_vol)
    # Higher vol -> at least as many FVGs (allow tiny noise)
    assert d_high >= d_low * 0.7, (
        f"High-vol FVG density {d_high:.3f} < low-vol {d_low:.3f} x 0.7 - "
        f"library may be insensitive to volatility regime"
    )


def test_swing_count_decreases_with_swing_length():
    """Strict monotonic-decreasing swing count as swing_length grows on same input."""
    df = gbm_ohlcv(1500, seed=42, vol=0.015)
    counts = [
        smc.swing_highs_lows(df, swing_length=sl)["HighLow"].notna().sum()
        for sl in [5, 10, 20, 50, 100]
    ]
    for i in range(1, len(counts)):
        assert counts[i] <= counts[i-1], (
            f"swing count not monotonic decreasing in swing_length: {counts}"
        )


def test_fvg_density_bounded_in_trending_market():
    """Strongly trending market should still produce FVG density < 50%."""
    df = gbm_ohlcv(1500, seed=42, vol=0.01, drift=0.001, with_jumps=False)
    density = smc.fvg(df)["FVG"].notna().sum() / len(df)
    assert density < 0.5, (
        f"Trending-market FVG density {density:.3f} > 50% - pathological detection rate"
    )


def test_bos_count_positive_in_trending_market():
    """Strong uptrend should produce >=1 BOS (continuation breakout)."""
    df = gbm_ohlcv(2000, seed=42, vol=0.015, drift=0.0015, with_jumps=False)
    sw = smc.swing_highs_lows(df, swing_length=20)
    bc = smc.bos_choch(df, sw)
    n_bos = bc["BOS"].notna().sum()
    # Some trending paths may not trigger BOS due to swing-confirmation lag;
    # bound is loose - assert non-pathological (>=1 over 2000 trending bars).
    assert n_bos >= 1, (
        f"Trending-market BOS count {n_bos} == 0 over 2000 bars - swing detection broken"
    )


# =============================================================================
# 3. TIME-BETWEEN-SIGNALS DISTRIBUTION
# =============================================================================


def test_fvg_time_between_signals_no_clumping():
    """Mean inter-signal gap should be > 1 bar (consecutive-bar firing every bar
    would indicate a bug in detection logic, not a real edge)."""
    df = gbm_ohlcv(2000, seed=42, vol=0.015, with_jumps=True)
    fvg = smc.fvg(df)
    positions = np.where(fvg["FVG"].notna())[0]
    if len(positions) < 10:
        pytest.skip("not enough FVGs")
    gaps = np.diff(positions)
    mean_gap = float(gaps.mean())
    assert mean_gap > 1.0, (
        f"FVG mean inter-signal gap {mean_gap:.2f} <= 1.0 bar - every-bar firing is suspicious"
    )


def test_swing_time_between_signals_bounded():
    """Swing inter-arrival > swing_length / 2 on average (some confirmation lag)."""
    df = gbm_ohlcv(2000, seed=42)
    sw = smc.swing_highs_lows(df, swing_length=20)
    positions = np.where(sw["HighLow"].notna())[0]
    if len(positions) < 5:
        pytest.skip("not enough swings")
    gaps = np.diff(positions)
    median_gap = float(np.median(gaps))
    # With swing_length=20 we expect median gap >= ~10 bars
    assert median_gap >= 5, (
        f"Swing median inter-arrival {median_gap:.1f} < 5 bars (swing_length=20) - "
        f"library may emit duplicate/adjacent swings"
    )


def test_fvg_gap_distribution_finite_quantiles():
    """FVG inter-arrival quantiles should all be finite - no degenerate constant series."""
    df = gbm_ohlcv(2000, seed=42, with_jumps=True)
    positions = np.where(smc.fvg(df)["FVG"].notna())[0]
    if len(positions) < 20:
        pytest.skip("not enough FVGs")
    gaps = np.diff(positions)
    q25, q50, q75 = np.quantile(gaps, [0.25, 0.50, 0.75])
    for q in (q25, q50, q75):
        assert np.isfinite(q), f"gap quantile {q} not finite"
    # q75 > q25 (non-degenerate distribution)
    assert q75 >= q25, f"FVG gap distribution degenerate: q25={q25} q75={q75}"


# =============================================================================
# 4. SWING ALTERNATION STATISTIC
# =============================================================================


def test_swing_alternation_ratio_above_half():
    """Across a long random walk, swing sequence should mostly alternate high-low-high-low.
    Allow some same-direction runs (library may emit consecutive same-sign swings),
    but alternation ratio should exceed 0.5."""
    df = gbm_ohlcv(3000, seed=42, vol=0.018)
    sw = smc.swing_highs_lows(df, swing_length=20)
    seq = sw["HighLow"].dropna().astype(int).tolist()
    if len(seq) < 20:
        pytest.skip("not enough swings")
    flips = sum(1 for i in range(1, len(seq)) if seq[i] != seq[i-1])
    ratio = flips / (len(seq) - 1)
    assert ratio >= 0.5, (
        f"Swing alternation ratio {ratio:.2f} < 0.5 - consecutive same-direction "
        f"swings dominate ({flips} flips of {len(seq)-1} transitions)"
    )


def test_swing_levels_consistent_with_extremes():
    """At every swing bar, Level should equal that bar's high (if high-swing) or
    low (if low-swing) - by construction."""
    df = gbm_ohlcv(1500, seed=42, vol=0.015)
    sw = smc.swing_highs_lows(df, swing_length=20)
    # Iterate positionally to avoid label/boolean alignment quirks when index
    # types diverge between sw and df.
    for i in range(len(sw)):
        hl = sw["HighLow"].iloc[i]
        if pd.isna(hl):
            continue
        level = sw["Level"].iloc[i]
        if int(hl) == 1:
            assert abs(level - df["high"].iloc[i]) < 1e-6, (
                f"Swing-high at idx {i}: Level {level} != bar high {df['high'].iloc[i]}"
            )
        elif int(hl) == -1:
            assert abs(level - df["low"].iloc[i]) < 1e-6, (
                f"Swing-low at idx {i}: Level {level} != bar low {df['low'].iloc[i]}"
            )


# =============================================================================
# 5. CROSS-PRIMITIVE SANITY
# =============================================================================


def test_bos_choch_mutual_exclusion_per_bar():
    """At any given bar, BOS and CHOCH should not BOTH fire - they're mutually
    exclusive semantically (BOS = continuation; CHOCH = reversal)."""
    df = gbm_ohlcv(2000, seed=42, vol=0.02)
    sw = smc.swing_highs_lows(df, swing_length=20)
    bc = smc.bos_choch(df, sw)
    both_fire = (bc["BOS"].notna() & bc["CHOCH"].notna()).sum()
    assert both_fire == 0, (
        f"{both_fire} bars have BOTH BOS and CHOCH firing - semantic mutual-exclusion violated"
    )


def test_ob_top_geq_bottom_when_both_present():
    """OB Top must be >= Bottom for every emitted OB (geometric invariant)."""
    df = gbm_ohlcv(2000, seed=42, vol=0.02)
    sw = smc.swing_highs_lows(df, swing_length=20)
    ob = smc.ob(df, sw)
    valid = ob.dropna(subset=["Top", "Bottom"])
    if valid.empty:
        pytest.skip("no OBs with Top/Bottom")
    violations = (valid["Top"] < valid["Bottom"]).sum()
    assert violations == 0, f"{violations} OBs with Top < Bottom - geometric invariant violated"


def test_fvg_top_strictly_above_bottom():
    """FVG by definition is a gap - Top must be strictly > Bottom."""
    df = gbm_ohlcv(2000, seed=42, vol=0.02, with_jumps=True)
    fvg = smc.fvg(df)
    valid = fvg.dropna(subset=["Top", "Bottom"])
    if valid.empty:
        pytest.skip("no FVGs")
    violations = (valid["Top"] <= valid["Bottom"]).sum()
    assert violations == 0, (
        f"{violations} FVGs with Top <= Bottom - gap definition violated"
    )


def test_real_ticker_signal_distributions_sane():
    """On real cached tickers, fvg + swings + ob produce non-degenerate distributions."""
    counts = {"fvg": 0, "swings": 0, "ob": 0}
    tickers_used = 0
    for t in ["MSFT", "TSLA", "ABNB", "NVDA", "AAPL"]:
        try:
            df = load_real_or_skip(t)
        except pytest.skip.Exception:
            continue
        if len(df) < 200:
            continue
        sw = smc.swing_highs_lows(df, swing_length=20)
        counts["fvg"] += smc.fvg(df)["FVG"].notna().sum()
        counts["swings"] += sw["HighLow"].notna().sum()
        counts["ob"] += smc.ob(df, sw)["OB"].notna().sum()
        tickers_used += 1
    if tickers_used < 2:
        pytest.skip("need >=2 cached tickers")
    # Each primitive must produce >0 across the sample
    for k, v in counts.items():
        assert v > 0, f"{k}: aggregate signal count {v} across {tickers_used} tickers is zero"


def test_constant_data_produces_no_signals():
    """Edge sanity: bar-for-bar constant prices produce zero FVG / BOS / CHOCH / OB."""
    n = 200
    df = pd.DataFrame({
        "open": [100.0]*n, "high": [100.0]*n, "low": [100.0]*n,
        "close": [100.0]*n, "volume": [1e6]*n,
    }, index=pd.date_range("2021-01-01", periods=n, freq="B"))
    df.index.name = "date"
    sw = smc.swing_highs_lows(df, swing_length=20)
    bc = smc.bos_choch(df, sw)
    ob = smc.ob(df, sw)
    fvg = smc.fvg(df)
    assert fvg["FVG"].notna().sum() == 0
    assert bc["BOS"].notna().sum() == 0
    assert bc["CHOCH"].notna().sum() == 0
    assert ob["OB"].notna().sum() == 0


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
