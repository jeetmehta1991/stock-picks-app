"""Tier 3 cross-validation tests for vendored smartmoneyconcepts library.

Per DEC-508 + CHECKLIST #71 Tier 3 mandate (cross-validation sub-category).
Validates signal consistency across ticker partitions, seed partitions,
date-window partitions, and parameter partitions. Complements PIT regression
(test_smartmoneyconcepts_pit.py) and statistical sanity
(test_smartmoneyconcepts_statistical.py) by ensuring that any individual
ticker / window / parameter slice does not produce wildly anomalous behavior.

Sub-categories:
  1. Ticker partition CV - across N real tickers, FVG density stable
  2. Date-window partition CV - across folds on the same ticker, density stable
  3. Seed partition CV - across N synthetic seeds, density bounded
  4. Parameter partition CV - across swing_length values, monotonic count
  5. Leave-one-out stability - removing one ticker doesn't shift aggregate
  6. K-fold walk-forward (DEC-505 4-fold pattern) - fold-density stable

Run: pytest backtest/tests/test_smartmoneyconcepts_xvalidation.py -v
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
# Helpers
# -----------------------------------------------------------------------------


def gbm_ohlcv(n: int, seed: int, vol: float = 0.015,
              with_jumps: bool = True) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    returns = rng.normal(0.0003, vol, n)
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


def _cv(arr: list | np.ndarray) -> float:
    """Coefficient of variation (std/mean). Returns 0 if mean==0."""
    a = np.asarray(arr, dtype=float)
    if a.size == 0 or a.mean() == 0:
        return 0.0
    return float(a.std() / a.mean())


def _safe_density(arr: pd.Series, n: int) -> float:
    return float(arr.notna().sum() / n) if n > 0 else 0.0


# Candidate cached real tickers (skip if cache missing)
CACHED_TICKERS = ["MSFT", "TSLA", "ABNB", "NVDA", "AAPL", "A", "AA"]


# =============================================================================
# 1. TICKER PARTITION CV - FVG DENSITY STABLE ACROSS REAL TICKERS
# =============================================================================


def test_fvg_density_cv_across_real_tickers():
    """Across cached real tickers, FVG density CV should be < 1.5 (bounded)."""
    densities = []
    for t in CACHED_TICKERS:
        try:
            df = load_real_or_skip(t)
        except pytest.skip.Exception:
            continue
        if len(df) < 200:
            continue
        densities.append(_safe_density(smc.fvg(df)["FVG"], len(df)))
    if len(densities) < 3:
        pytest.skip(f"need >=3 cached tickers, found {len(densities)}")
    cv = _cv(densities)
    assert cv < 1.5, (
        f"FVG density CV {cv:.2f} > 1.5 across {len(densities)} tickers (densities={densities})"
    )


def test_swing_density_cv_across_real_tickers():
    densities = []
    for t in CACHED_TICKERS:
        try:
            df = load_real_or_skip(t)
        except pytest.skip.Exception:
            continue
        if len(df) < 200:
            continue
        sw = smc.swing_highs_lows(df, swing_length=20)
        densities.append(_safe_density(sw["HighLow"], len(df)))
    if len(densities) < 3:
        pytest.skip("need >=3 tickers")
    cv = _cv(densities)
    assert cv < 1.5, (
        f"Swing density CV {cv:.2f} > 1.5 across {len(densities)} tickers"
    )


def test_bos_density_cv_across_real_tickers():
    densities = []
    for t in CACHED_TICKERS:
        try:
            df = load_real_or_skip(t)
        except pytest.skip.Exception:
            continue
        if len(df) < 200:
            continue
        sw = smc.swing_highs_lows(df, swing_length=20)
        bc = smc.bos_choch(df, sw)
        densities.append(_safe_density(bc["BOS"], len(df)))
    if len(densities) < 3:
        pytest.skip("need >=3 tickers")
    cv = _cv(densities)
    # BOS is sparser; allow wider CV (2.0)
    assert cv < 2.0, f"BOS density CV {cv:.2f} > 2.0 across {len(densities)} tickers"


def test_ticker_partition_all_nonzero_fvg_density():
    """No individual real ticker should produce zero FVGs (else suggests broken cache)."""
    zero_count = 0
    tested = 0
    for t in CACHED_TICKERS:
        try:
            df = load_real_or_skip(t)
        except pytest.skip.Exception:
            continue
        if len(df) < 500:
            continue
        tested += 1
        n = smc.fvg(df)["FVG"].notna().sum()
        if n == 0:
            zero_count += 1
    if tested < 3:
        pytest.skip("need >=3 tickers")
    # At most 1 of N tickers may produce zero FVGs (allows for true edge cases)
    assert zero_count <= 1, f"{zero_count} of {tested} tickers produced zero FVGs"


# =============================================================================
# 2. DATE-WINDOW PARTITION CV - SAME TICKER, DIFFERENT WINDOWS
# =============================================================================


def test_fvg_density_cv_across_date_windows():
    """Split synthetic 2000-bar fixture into 4 non-overlapping 500-bar windows;
    FVG density CV should be < 1.5."""
    full = gbm_ohlcv(2000, seed=42, vol=0.015, with_jumps=True)
    densities = []
    for i in range(4):
        window = full.iloc[i*500:(i+1)*500]
        densities.append(_safe_density(smc.fvg(window)["FVG"], len(window)))
    if all(d == 0 for d in densities):
        pytest.skip("zero FVGs across all windows - fixture issue")
    cv = _cv(densities)
    assert cv < 1.5, f"Date-window FVG density CV {cv:.2f} > 1.5, densities={densities}"


def test_swing_density_cv_across_date_windows():
    full = gbm_ohlcv(2000, seed=42, vol=0.015)
    densities = []
    for i in range(4):
        window = full.iloc[i*500:(i+1)*500]
        sw = smc.swing_highs_lows(window, swing_length=20)
        densities.append(_safe_density(sw["HighLow"], len(window)))
    if all(d == 0 for d in densities):
        pytest.skip("zero swings - fixture issue")
    cv = _cv(densities)
    assert cv < 1.0, f"Swing density CV {cv:.2f} > 1.0 across date-windows, {densities}"


def test_fvg_density_real_ticker_first_vs_last_half():
    """For a real ticker, FVG density in first half vs second half should be similar
    (no regime-bias signal)."""
    for t in ["MSFT", "TSLA"]:
        try:
            df = load_real_or_skip(t)
        except pytest.skip.Exception:
            continue
        if len(df) < 500:
            continue
        mid = len(df) // 2
        first = df.iloc[:mid]
        second = df.iloc[mid:]
        d1 = _safe_density(smc.fvg(first)["FVG"], len(first))
        d2 = _safe_density(smc.fvg(second)["FVG"], len(second))
        if d1 == 0 or d2 == 0:
            continue
        ratio = max(d1, d2) / min(d1, d2)
        assert ratio < 5.0, (
            f"{t} FVG density first/second half ratio {ratio:.2f} > 5x: d1={d1:.3f} d2={d2:.3f}"
        )
        return  # passed on one ticker is sufficient
    pytest.skip("no qualifying ticker")


# =============================================================================
# 3. SEED PARTITION CV - STABILITY ACROSS RNG SEEDS
# =============================================================================


def test_fvg_density_cv_across_seeds():
    """Across 8 different seeds, FVG density CV should be < 0.5 (tight)."""
    densities = []
    for seed in range(42, 50):
        df = gbm_ohlcv(1000, seed=seed, vol=0.015, with_jumps=True)
        densities.append(_safe_density(smc.fvg(df)["FVG"], len(df)))
    cv = _cv(densities)
    assert cv < 0.5, f"FVG density CV across seeds = {cv:.2f}, densities={densities}"


def test_swing_density_cv_across_seeds():
    densities = []
    for seed in range(42, 50):
        df = gbm_ohlcv(1000, seed=seed, vol=0.015)
        sw = smc.swing_highs_lows(df, swing_length=20)
        densities.append(_safe_density(sw["HighLow"], len(df)))
    cv = _cv(densities)
    assert cv < 0.5, f"Swing density CV across seeds = {cv:.2f}, densities={densities}"


def test_bos_density_cv_across_seeds():
    densities = []
    for seed in range(42, 50):
        df = gbm_ohlcv(1500, seed=seed, vol=0.02, with_jumps=True)
        sw = smc.swing_highs_lows(df, swing_length=20)
        bc = smc.bos_choch(df, sw)
        densities.append(_safe_density(bc["BOS"], len(df)))
    cv = _cv(densities)
    # BOS sparser -> looser bound
    assert cv < 1.0, f"BOS density CV across seeds = {cv:.2f}, densities={densities}"


def test_ob_density_cv_across_seeds():
    densities = []
    for seed in range(42, 50):
        df = gbm_ohlcv(1500, seed=seed, vol=0.018)
        sw = smc.swing_highs_lows(df, swing_length=20)
        ob = smc.ob(df, sw)
        densities.append(_safe_density(ob["OB"], len(df)))
    cv = _cv(densities)
    assert cv < 1.0, f"OB density CV across seeds = {cv:.2f}, densities={densities}"


def test_seed_partition_min_max_ratio_bounded():
    """Max/min FVG density across seeds < 5x (no pathological seed outlier)."""
    densities = []
    for seed in range(42, 50):
        df = gbm_ohlcv(1000, seed=seed, vol=0.015, with_jumps=True)
        densities.append(_safe_density(smc.fvg(df)["FVG"], len(df)))
    positives = [d for d in densities if d > 0]
    if len(positives) < 2:
        pytest.skip("not enough positive densities")
    ratio = max(positives) / min(positives)
    assert ratio < 5.0, f"FVG density max/min ratio {ratio:.1f}x too large: {densities}"


# =============================================================================
# 4. PARAMETER PARTITION CV - swing_length MONOTONIC + RANGE BOUNDED
# =============================================================================


def test_swing_length_monotonic_count():
    """Across swing_length=[5,10,20,50,100], swing count must monotonically decrease."""
    df = gbm_ohlcv(2000, seed=42, vol=0.015)
    counts = []
    for sl in [5, 10, 20, 50, 100]:
        n = smc.swing_highs_lows(df, swing_length=sl)["HighLow"].notna().sum()
        counts.append(n)
    for i in range(1, len(counts)):
        assert counts[i] <= counts[i-1], (
            f"swing count not monotonic decreasing across swing_length: {counts}"
        )


def test_liquidity_range_percent_monotonic_count():
    """Wider range_percent should produce >= liquidity zones (monotonic non-decreasing)."""
    df = gbm_ohlcv(1500, seed=42, vol=0.015)
    sw = smc.swing_highs_lows(df, swing_length=20)
    counts = []
    for rp in [0.001, 0.005, 0.01, 0.025, 0.05]:
        n = smc.liquidity(df, sw, range_percent=rp)["Liquidity"].notna().sum()
        counts.append(n)
    for i in range(1, len(counts)):
        assert counts[i] >= counts[i-1], (
            f"liquidity count not monotonic increasing across range_percent: {counts}"
        )


def test_fvg_join_consecutive_reduces_count():
    """join_consecutive=True must produce <= FVGs compared to join_consecutive=False."""
    df = gbm_ohlcv(2000, seed=42, vol=0.02, with_jumps=True)
    n_sep = smc.fvg(df, join_consecutive=False)["FVG"].notna().sum()
    n_joined = smc.fvg(df, join_consecutive=True)["FVG"].notna().sum()
    assert n_joined <= n_sep, (
        f"join_consecutive=True ({n_joined}) > join_consecutive=False ({n_sep})"
    )


# =============================================================================
# 5. LEAVE-ONE-OUT (LOO) STABILITY
# =============================================================================


def test_loo_aggregate_density_stable_across_seeds():
    """Leave-one-out across 8 synthetic seeds: removing one seed shouldn't shift
    aggregate FVG density by more than 2x."""
    seeds = list(range(42, 50))
    densities_by_seed = {}
    for seed in seeds:
        df = gbm_ohlcv(1000, seed=seed, vol=0.015, with_jumps=True)
        densities_by_seed[seed] = _safe_density(smc.fvg(df)["FVG"], len(df))
    if all(d == 0 for d in densities_by_seed.values()):
        pytest.skip("zero densities - fixture issue")

    full_mean = float(np.mean(list(densities_by_seed.values())))
    if full_mean == 0:
        pytest.skip("zero mean - fixture issue")

    for held_out in seeds:
        loo_vals = [d for s, d in densities_by_seed.items() if s != held_out]
        loo_mean = float(np.mean(loo_vals))
        ratio = max(full_mean, loo_mean) / max(min(full_mean, loo_mean), 1e-9)
        assert ratio < 2.0, (
            f"LOO held-out seed {held_out}: full={full_mean:.3f} loo={loo_mean:.3f} "
            f"ratio={ratio:.2f}x > 2x"
        )


def test_loo_ticker_aggregate_density_stable():
    """LOO across real cached tickers: removing one shouldn't shift aggregate by >3x."""
    densities = {}
    for t in CACHED_TICKERS:
        try:
            df = load_real_or_skip(t)
        except pytest.skip.Exception:
            continue
        if len(df) < 500:
            continue
        densities[t] = _safe_density(smc.fvg(df)["FVG"], len(df))
    if len(densities) < 3:
        pytest.skip("need >=3 tickers")
    full_mean = float(np.mean(list(densities.values())))
    if full_mean == 0:
        pytest.skip("zero mean")

    for held_out in densities:
        loo_vals = [d for t, d in densities.items() if t != held_out]
        loo_mean = float(np.mean(loo_vals))
        ratio = max(full_mean, loo_mean) / max(min(full_mean, loo_mean), 1e-9)
        # Real tickers are heterogeneous; allow up to 3x shift
        assert ratio < 3.0, (
            f"LOO held-out {held_out}: full={full_mean:.3f} loo={loo_mean:.3f} ratio={ratio:.2f}x"
        )


# =============================================================================
# 6. K-FOLD WALK-FORWARD (DEC-505)
# =============================================================================


def test_4fold_walk_forward_density_stable():
    """DEC-505 4-fold walk-forward: 4 successive 250-bar OOS windows on synthetic
    1300-bar fixture should produce density CV < 1.0."""
    full = gbm_ohlcv(1300, seed=42, vol=0.015, with_jumps=True)
    fold_size = 250
    densities = []
    for k in range(4):
        start = 50 + k * fold_size  # 50-bar warmup before first fold
        end = start + fold_size
        if end > len(full):
            break
        fold = full.iloc[start:end]
        densities.append(_safe_density(smc.fvg(fold)["FVG"], len(fold)))
    if len(densities) < 3:
        pytest.skip("need >=3 folds")
    cv = _cv(densities)
    assert cv < 1.0, f"4-fold walk-forward FVG density CV {cv:.2f} > 1.0, densities={densities}"


def test_4fold_walk_forward_swing_stable():
    full = gbm_ohlcv(1300, seed=42, vol=0.015)
    fold_size = 250
    densities = []
    for k in range(4):
        start = 50 + k * fold_size
        end = start + fold_size
        if end > len(full):
            break
        fold = full.iloc[start:end]
        sw = smc.swing_highs_lows(fold, swing_length=20)
        densities.append(_safe_density(sw["HighLow"], len(fold)))
    if len(densities) < 3:
        pytest.skip("need >=3 folds")
    cv = _cv(densities)
    assert cv < 1.0, f"4-fold walk-forward swing density CV {cv:.2f} > 1.0, {densities}"


def test_expanding_window_density_stable():
    """Expanding window (250->500->750->1000 bars from start) - FVG density should
    converge as data grows (CV across expansions < 1.0)."""
    full = gbm_ohlcv(1500, seed=42, vol=0.015, with_jumps=True)
    densities = []
    for end in [250, 500, 750, 1000]:
        window = full.iloc[:end]
        densities.append(_safe_density(smc.fvg(window)["FVG"], len(window)))
    if all(d == 0 for d in densities):
        pytest.skip("zero - fixture issue")
    cv = _cv(densities)
    assert cv < 1.0, (
        f"Expanding-window FVG density CV {cv:.2f} > 1.0 - density should converge: {densities}"
    )


def test_kfold_cross_ticker_density_pairwise_bounded():
    """Pairwise comparison across cached tickers: no pair should differ by >10x in
    FVG density (sanity bound for cross-ticker variance)."""
    densities = {}
    for t in CACHED_TICKERS:
        try:
            df = load_real_or_skip(t)
        except pytest.skip.Exception:
            continue
        if len(df) < 500:
            continue
        densities[t] = _safe_density(smc.fvg(df)["FVG"], len(df))
    positives = {k: v for k, v in densities.items() if v > 0}
    if len(positives) < 3:
        pytest.skip("need >=3 positive-density tickers")
    arr = list(positives.values())
    ratio = max(arr) / min(arr)
    assert ratio < 10.0, (
        f"Cross-ticker FVG density max/min ratio {ratio:.1f}x - outlier ticker present: {positives}"
    )


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
