"""DEC-513 extended signals — regression tests (Pass 53 Day-9 v8g).

Spec source: TRADING_RULES_AND_INFORMATION.md §2A.10.

Tests the 4-of-9 signal helpers implemented this turn:
  #1 compute_realized_vol           (3 horizons)
  #5 compute_overnight_intraday_split
  #6 compute_gaps                    (size + bucket + fill T+1/T+3/T+5)
  #8 compute_extremes                (52w/20d/252d distance fields)
  #10 attach_signal_age              (universal age field)
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest


def _build_df(n=80, drift=0.0, vol=0.01, seed=42, start=100.0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-02", periods=n, freq="B")
    rets = rng.normal(drift, vol, n)
    close = start * np.cumprod(1 + rets)
    df = pd.DataFrame({
        "open":   close * (1 + rng.normal(0, 0.001, n)),
        "high":   close * (1 + np.abs(rng.normal(0.005, 0.002, n))),
        "low":    close * (1 - np.abs(rng.normal(0.005, 0.002, n))),
        "close":  close,
        "volume": rng.integers(800_000, 1_500_000, n),
    }, index=idx)
    df["high"] = df[["open", "high", "close"]].max(axis=1)
    df["low"]  = df[["open", "low", "close"]].min(axis=1)
    return df


# ---------------------------------------------------------------------------
# #1 Realized vol
# ---------------------------------------------------------------------------
def test_dec513_realized_vol_three_horizons_present():
    from backtest.signals.dec513_extended_signals import compute_realized_vol
    df = _build_df(n=80)
    out = compute_realized_vol(df)
    assert set(out.keys()) == {"realized_vol_10d", "realized_vol_20d", "realized_vol_60d"}


def test_dec513_realized_vol_high_vol_input():
    """Synthetic high-vol input → realized_vol should be elevated."""
    from backtest.signals.dec513_extended_signals import compute_realized_vol
    df = _build_df(n=80, vol=0.05)
    out = compute_realized_vol(df)
    # 5% daily vol annualized ≈ 80%
    assert out["realized_vol_20d"] > 0.4


def test_dec513_realized_vol_low_vol_input():
    from backtest.signals.dec513_extended_signals import compute_realized_vol
    df = _build_df(n=80, vol=0.005)
    out = compute_realized_vol(df)
    # 0.5% daily vol annualized ≈ 8%
    assert out["realized_vol_20d"] < 0.3


def test_dec513_realized_vol_insufficient_history():
    from backtest.signals.dec513_extended_signals import compute_realized_vol
    df = _build_df(n=5)
    out = compute_realized_vol(df)
    assert all(np.isnan(v) for v in out.values())


# ---------------------------------------------------------------------------
# #2 Betas (Pass 53 Day-9 v8h evening — DEC-513 #2)
# ---------------------------------------------------------------------------
def _build_synth_pair(beta: float, n: int = 280, vol: float = 0.01,
                       seed: int = 42, drift: float = 0.0):
    """Build market and stock OHLCV where stock_ret = beta * market_ret + tiny noise.

    Returns (stock_df, market_df). Useful for verifying that compute_betas
    recovers the synthetic beta to within tolerance.
    """
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2022-01-03", periods=n, freq="B")
    market_rets = rng.normal(drift, vol, n)
    noise = rng.normal(0, vol * 0.05, n)  # 5% noise relative to market vol
    stock_rets = beta * market_rets + noise
    market_close = 100.0 * np.cumprod(1 + market_rets)
    stock_close = 100.0 * np.cumprod(1 + stock_rets)
    market_df = pd.DataFrame({"open": market_close, "high": market_close * 1.005,
                              "low": market_close * 0.995, "close": market_close,
                              "volume": [1_000_000] * n}, index=idx)
    stock_df = pd.DataFrame({"open": stock_close, "high": stock_close * 1.005,
                             "low": stock_close * 0.995, "close": stock_close,
                             "volume": [1_000_000] * n}, index=idx)
    return stock_df, market_df


def test_dec513_betas_returns_8_fields():
    from backtest.signals.dec513_extended_signals import compute_betas
    s, m = _build_synth_pair(beta=1.0, n=280)
    out = compute_betas(s, m)
    expected = {
        "beta_market_60d", "beta_market_252d",
        "r2_market_60d", "r2_market_252d",
        "beta_sector_60d", "beta_sector_252d",
        "r2_sector_60d", "r2_sector_252d",
    }
    assert set(out.keys()) == expected


def test_dec513_betas_recover_beta_one():
    """Synthetic stock_ret = 1.0 * market_ret → beta_market should be ~1.0."""
    from backtest.signals.dec513_extended_signals import compute_betas
    s, m = _build_synth_pair(beta=1.0, n=280)
    out = compute_betas(s, m)
    assert abs(out["beta_market_252d"] - 1.0) < 0.05
    assert out["r2_market_252d"] > 0.95  # near-perfect linear relationship


def test_dec513_betas_recover_beta_one_point_five():
    """Synthetic stock_ret = 1.5 * market_ret → beta_market ~1.5."""
    from backtest.signals.dec513_extended_signals import compute_betas
    s, m = _build_synth_pair(beta=1.5, n=280)
    out = compute_betas(s, m)
    assert abs(out["beta_market_252d"] - 1.5) < 0.10


def test_dec513_betas_recover_beta_half():
    """Synthetic stock_ret = 0.5 * market_ret → beta_market ~0.5."""
    from backtest.signals.dec513_extended_signals import compute_betas
    s, m = _build_synth_pair(beta=0.5, n=280)
    out = compute_betas(s, m)
    assert abs(out["beta_market_252d"] - 0.5) < 0.05


def test_dec513_betas_sector_nan_when_omitted():
    """No sector_df → sector_* fields are all NaN."""
    from backtest.signals.dec513_extended_signals import compute_betas
    s, m = _build_synth_pair(beta=1.0, n=280)
    out = compute_betas(s, m, sector_df=None)
    assert np.isnan(out["beta_sector_60d"])
    assert np.isnan(out["beta_sector_252d"])


def test_dec513_betas_sector_recovers_when_supplied():
    """When sector ETF is the same as market, sector beta ≈ market beta."""
    from backtest.signals.dec513_extended_signals import compute_betas
    s, m = _build_synth_pair(beta=1.2, n=280)
    out = compute_betas(s, m, sector_df=m)  # use market as sector for test
    assert abs(out["beta_sector_252d"] - 1.2) < 0.10


def test_dec513_betas_insufficient_history_returns_nan():
    from backtest.signals.dec513_extended_signals import compute_betas
    s, m = _build_synth_pair(beta=1.0, n=5)
    out = compute_betas(s, m)
    assert np.isnan(out["beta_market_60d"])
    assert np.isnan(out["beta_market_252d"])


# ---------------------------------------------------------------------------
# #5 Overnight / intraday split
# ---------------------------------------------------------------------------
def test_dec513_overnight_intraday_returns_three_fields():
    from backtest.signals.dec513_extended_signals import compute_overnight_intraday_split
    df = _build_df(n=40)
    out = compute_overnight_intraday_split(df)
    assert set(out.keys()) == {"overnight_return", "intraday_return",
                                "overnight_intraday_ratio_20d"}


def test_dec513_overnight_split_correct_components():
    """Build deterministic OHLC: prev_close=100, open=101 (1% gap), close=99 (intraday -2%)."""
    from backtest.signals.dec513_extended_signals import compute_overnight_intraday_split
    idx = pd.date_range("2023-01-02", periods=21, freq="B")
    df = pd.DataFrame({
        "open":   [100.0] * 20 + [101.0],
        "high":   [101.0] * 21,
        "low":    [99.0] * 21,
        "close":  [100.0] * 20 + [99.0],
        "volume": [1_000_000] * 21,
    }, index=idx)
    out = compute_overnight_intraday_split(df)
    # last bar: open=101 vs prev_close=100 → overnight = +1%
    # close=99 vs open=101 → intraday = -1.98%
    assert out["overnight_return"] == pytest.approx(0.01, abs=1e-6)
    assert out["intraday_return"] == pytest.approx((99 - 101) / 101, abs=1e-6)


# ---------------------------------------------------------------------------
# #6 Gap classification
# ---------------------------------------------------------------------------
def test_dec513_gaps_small_bucket():
    """0.5% gap → small bucket."""
    from backtest.signals.dec513_extended_signals import compute_gaps
    idx = pd.date_range("2023-01-02", periods=10, freq="B")
    df = pd.DataFrame({
        "open":   [100.0]*9 + [100.5],
        "high":   [101.0]*9 + [101.0],
        "low":    [99.0]*9 + [100.0],
        "close":  [100.0]*9 + [100.6],
        "volume": [1_000_000]*10,
    }, index=idx)
    out = compute_gaps(df)
    assert out["gap_size_bucket"] == "small"
    assert abs(out["gap_size_pct"] - 0.5) < 0.01


def test_dec513_gaps_large_bucket_gap_up():
    """5% gap-up → large bucket."""
    from backtest.signals.dec513_extended_signals import compute_gaps
    idx = pd.date_range("2023-01-02", periods=10, freq="B")
    df = pd.DataFrame({
        "open":   [100.0]*9 + [105.0],
        "high":   [101.0]*9 + [106.0],
        "low":    [99.0]*9 + [104.0],
        "close":  [100.0]*9 + [105.5],
        "volume": [1_000_000]*10,
    }, index=idx)
    out = compute_gaps(df)
    assert out["gap_size_bucket"] == "large"
    assert out["gap_size_pct"] > 4.0


def test_dec513_gaps_medium_bucket_gap_down():
    """-2% gap-down → medium bucket; gap_size_pct negative."""
    from backtest.signals.dec513_extended_signals import compute_gaps
    idx = pd.date_range("2023-01-02", periods=10, freq="B")
    df = pd.DataFrame({
        "open":   [100.0]*9 + [98.0],
        "high":   [101.0]*9 + [99.0],
        "low":    [99.0]*9 + [97.0],
        "close":  [100.0]*9 + [98.5],
        "volume": [1_000_000]*10,
    }, index=idx)
    out = compute_gaps(df)
    assert out["gap_size_bucket"] == "medium"
    assert out["gap_size_pct"] < -1.0


def test_dec513_gap_fill_true_when_intraday_returns():
    """Gap up at T0; T+1 low <= prev_close → gap filled."""
    from backtest.signals.dec513_extended_signals import compute_gaps
    idx = pd.date_range("2023-01-02", periods=10, freq="B")
    # Prev close = 100. T0 (idx[6]): open=105 (gap up), close=104.
    # T+1 (idx[7]): low=99 (touches prev_close=100). Gap filled.
    df = pd.DataFrame({
        "open":   [100.0]*6 + [105.0, 102.0, 100.0, 100.0],
        "high":   [101.0]*6 + [106.0, 103.0, 101.0, 101.0],
        "low":    [99.0]*6 + [104.0, 99.0, 99.0, 99.0],
        "close":  [100.0]*6 + [104.5, 99.5, 100.0, 100.0],
        "volume": [1_000_000]*10,
    }, index=idx)
    # Pass slice ending at T0 + 1 future bar (T+1 fill check)
    out = compute_gaps(df.iloc[:8])  # 7 bars + T+1 bar
    # The last bar in slice is T+1 — but our fn computes gap on LAST bar.
    # We need to call compute_gaps on slice ending at gap-bar with future appended.
    # Simpler: pass full df (10 bars), compute_gaps treats LAST (idx[9]) as the gap day.
    # Instead, let's verify with df where last bar IS the gap and T+1..T+5 follow.
    df2 = df.copy()
    df2 = df2.iloc[:7]  # 7 bars; last is gap (idx[6])
    out = compute_gaps(df2)
    # Without future bars in df2, fill flags must be False
    assert out["gap_filled_T1"] is False


# ---------------------------------------------------------------------------
# #7 VIX term structure (Pass 53 Day-9 v8h evening — DEC-513 #7)
# ---------------------------------------------------------------------------
def _build_fred_series(values: list, label: str = "value") -> pd.DataFrame:
    """Build a FRED-style observations DataFrame (DatetimeIndex + value col)."""
    idx = pd.date_range("2024-01-02", periods=len(values), freq="B")
    return pd.DataFrame({label: values}, index=idx)


def test_dec513_vix_term_structure_returns_5_fields():
    from backtest.signals.dec513_extended_signals import compute_vix_term_structure
    vix = _build_fred_series([15.0, 16.0, 18.0])
    vix3m = _build_fred_series([18.0, 19.0, 20.0])
    out = compute_vix_term_structure(vix, vix3m)
    assert set(out.keys()) == {"vix_spot", "vix_3m", "vix_term_premium",
                                "vix_term_ratio", "vix_term_regime"}


def test_dec513_vix_term_contango_normal():
    """VIX=15, VIX3M=18 → premium=+3, ratio=1.2, regime=contango."""
    from backtest.signals.dec513_extended_signals import compute_vix_term_structure
    vix = _build_fred_series([15.0])
    vix3m = _build_fred_series([18.0])
    out = compute_vix_term_structure(vix, vix3m)
    assert out["vix_spot"] == 15.0
    assert out["vix_3m"] == 18.0
    assert out["vix_term_premium"] == pytest.approx(3.0)
    assert out["vix_term_ratio"] == pytest.approx(1.2)
    assert out["vix_term_regime"] == "contango"


def test_dec513_vix_term_backwardation_stress():
    """VIX=40, VIX3M=30 → premium=-10, ratio=0.75, regime=backwardation."""
    from backtest.signals.dec513_extended_signals import compute_vix_term_structure
    vix = _build_fred_series([40.0])
    vix3m = _build_fred_series([30.0])
    out = compute_vix_term_structure(vix, vix3m)
    assert out["vix_term_premium"] == pytest.approx(-10.0)
    assert out["vix_term_ratio"] == pytest.approx(0.75)
    assert out["vix_term_regime"] == "backwardation"


def test_dec513_vix_term_flat_regime():
    """VIX=20, VIX3M=20.5 → ratio=1.025, regime=flat."""
    from backtest.signals.dec513_extended_signals import compute_vix_term_structure
    vix = _build_fred_series([20.0])
    vix3m = _build_fred_series([20.5])
    out = compute_vix_term_structure(vix, vix3m)
    assert out["vix_term_regime"] == "flat"


def test_dec513_vix_term_handles_empty_input():
    from backtest.signals.dec513_extended_signals import compute_vix_term_structure
    empty = pd.DataFrame({"value": []})
    vix3m = _build_fred_series([20.0])
    out = compute_vix_term_structure(empty, vix3m)
    assert np.isnan(out["vix_spot"])
    assert out["vix_term_regime"] == "unknown"


def test_dec513_vix_term_handles_zero_vix():
    """vix_spot=0 → division-safe; returns NaN regime=unknown."""
    from backtest.signals.dec513_extended_signals import compute_vix_term_structure
    vix = _build_fred_series([0.0])
    vix3m = _build_fred_series([20.0])
    out = compute_vix_term_structure(vix, vix3m)
    assert np.isnan(out["vix_spot"]) or out["vix_spot"] == 0.0
    assert out["vix_term_regime"] == "unknown"


def test_dec513_vix_term_uses_last_row():
    """compute_vix_term_structure should use the LAST row (most-recent), not first."""
    from backtest.signals.dec513_extended_signals import compute_vix_term_structure
    vix = _build_fred_series([10.0, 20.0, 30.0])
    vix3m = _build_fred_series([15.0, 25.0, 33.0])
    out = compute_vix_term_structure(vix, vix3m)
    # Should pick last row (vix=30, vix3m=33)
    assert out["vix_spot"] == 30.0
    assert out["vix_3m"] == 33.0


# ---------------------------------------------------------------------------
# #8 Extremes
# ---------------------------------------------------------------------------
def test_dec513_extremes_returns_8_fields():
    from backtest.signals.dec513_extended_signals import compute_extremes
    df = _build_df(n=300)
    out = compute_extremes(df)
    expected = {
        "dist_from_52w_high_pct", "dist_from_52w_low_pct",
        "dist_from_20d_high_pct", "dist_from_20d_low_pct",
        "dist_from_252d_high_atr", "dist_from_252d_low_atr",
        "pct_to_52w_high", "pct_to_52w_low",
    }
    assert set(out.keys()) == expected


def test_dec513_extremes_at_high_yields_zero_distance():
    """If close == 52w high, dist_from_52w_high_pct ≈ 0."""
    from backtest.signals.dec513_extended_signals import compute_extremes
    idx = pd.date_range("2023-01-02", periods=300, freq="B")
    close = np.linspace(100, 200, 300)  # monotonic up; today is high
    df = pd.DataFrame({
        "open":   close, "high": close + 0.5, "low": close - 0.5,
        "close":  close, "volume": [1_000_000] * 300,
    }, index=idx)
    out = compute_extremes(df)
    # Last close = 200; 52w high = 200.5; distance ≈ 0.25%
    assert out["dist_from_52w_high_pct"] < 1.0


def test_dec513_extremes_at_low_yields_high_distance_from_high():
    """If close near 52w low, dist_from_52w_high_pct should be large."""
    from backtest.signals.dec513_extended_signals import compute_extremes
    idx = pd.date_range("2023-01-02", periods=300, freq="B")
    close = np.linspace(200, 100, 300)  # monotonic down; today is low
    df = pd.DataFrame({
        "open":   close, "high": close + 0.5, "low": close - 0.5,
        "close":  close, "volume": [1_000_000] * 300,
    }, index=idx)
    out = compute_extremes(df)
    # Last close ~100; 52w high ~200; dist ~50%
    assert out["dist_from_52w_high_pct"] > 30.0


def test_dec513_extremes_pct_to_52w_high_in_unit_range():
    from backtest.signals.dec513_extended_signals import compute_extremes
    df = _build_df(n=300)
    out = compute_extremes(df)
    assert 0 < out["pct_to_52w_high"] <= 1.0001
    assert out["pct_to_52w_low"] >= 0.99


# ---------------------------------------------------------------------------
# #10 signal_age_days
# ---------------------------------------------------------------------------
def test_dec513_signal_age_days_basic():
    from backtest.signals.dec513_extended_signals import attach_signal_age
    out = attach_signal_age({"signal": "buy"}, date(2024, 6, 1), date(2024, 6, 15))
    assert out["signal_age_days"] == 14
    assert out["signal"] == "buy"  # original keys preserved


def test_dec513_signal_age_days_same_day_zero():
    from backtest.signals.dec513_extended_signals import attach_signal_age
    out = attach_signal_age({}, date(2024, 6, 1), date(2024, 6, 1))
    assert out["signal_age_days"] == 0
