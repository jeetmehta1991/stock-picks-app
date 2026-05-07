"""Tests for exit_context.py — Tier 1-4 per-trade context for trade_exit_detail.

Pass 53 Day-9-evening 2026-05-07 owner directive: all 4 tiers tested in Phase 1A.
Per DEC-594 same-commit rule.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from backtest.engine.exit_context import (
    CONTEXT_COLUMN_NAMES,
    build_entry_context,
    _adv_bucket,
    _day_of_week_at_entry,
    _days_from_quarter_end,
    _derive_cap_band,
    _derive_vol_band,
    _entry_atr_ratio,
    _hold_duration_band,
    _hy_oas_band_at_entry,
    _mae_mfe_bucket,
    _regime_changed_during_hold,
    _smart_money_signal_present,
    _universe_tier,
    _win_loss_outcome,
)


# ---------------------------------------------------------------------------
# Tier 1
# ---------------------------------------------------------------------------
def test_t1_hold_duration_band():
    assert _hold_duration_band(0) == "short_le_3d"
    assert _hold_duration_band(3) == "short_le_3d"
    assert _hold_duration_band(7) == "medium_4_10d"
    assert _hold_duration_band(15) == "long_ge_11d"


def test_t1_win_loss_outcome():
    assert _win_loss_outcome(0.05) == "win"
    assert _win_loss_outcome(-0.02) == "loss"
    assert _win_loss_outcome(0) == "loss"  # 0 = no profit = loss-side


def test_t1_universe_tier_resolves():
    # Real ticker; should resolve to a known tier or 'unknown'
    tier = _universe_tier("AAPL", date(2024, 6, 1))
    assert tier in ("T1a", "T1c", "T1ETF", "T2", "T3", "unknown")


def test_t1_smart_money_signal_present_yes():
    sigs = {"smart_money_score": 0.8, "atr": 1.5}
    assert _smart_money_signal_present(sigs) == "yes"


def test_t1_smart_money_signal_present_no():
    sigs = {"atr": 1.5, "rsi": 30.0}
    assert _smart_money_signal_present(sigs) == "no"


def test_t1_cap_band_derives():
    assert _derive_cap_band(pd.Series({"market_cap": 250e9})) == "mega_ge_200B"
    assert _derive_cap_band(pd.Series({"market_cap": 50e9})) == "large_10_200B"
    assert _derive_cap_band(pd.Series({"market_cap": 5e9})) == "mid_2_10B"
    assert _derive_cap_band(pd.Series({"market_cap": 1e9})) == "small_lt_2B"
    assert _derive_cap_band(pd.Series({"market_cap": None})) == "unknown"


def test_t1_vol_band_from_vix():
    assert _derive_vol_band({"vix_value": 12}, atr=1.0, entry_price=100) == "low_lt_15"
    assert _derive_vol_band({"vix_value": 20}, atr=1.0, entry_price=100) == "mid_15_25"
    assert _derive_vol_band({"vix_value": 30}, atr=1.0, entry_price=100) == "high_25_40"
    assert _derive_vol_band({"vix_value": 45}, atr=1.0, entry_price=100) == "crisis_ge_40"


def test_t1_vol_band_atr_fallback():
    """No VIX in signals → falls back to ATR/price ratio."""
    assert _derive_vol_band({}, atr=0.5, entry_price=100) == "low_atr_lt_1pct"
    assert _derive_vol_band({}, atr=2.0, entry_price=100) == "mid_atr_1_2.5pct"
    assert _derive_vol_band({}, atr=4.0, entry_price=100) == "high_atr_2.5_5pct"
    assert _derive_vol_band({}, atr=8.0, entry_price=100) == "crisis_atr_ge_5pct"


# ---------------------------------------------------------------------------
# Tier 2
# ---------------------------------------------------------------------------
def test_t2_entry_atr_ratio():
    assert _entry_atr_ratio(2.0, 100.0) == 0.02
    assert _entry_atr_ratio(0.0, 0.0) == 0.0


def test_t2_mae_mfe_bucket():
    assert _mae_mfe_bucket(-0.01) == "q1_lt_2pct"
    assert _mae_mfe_bucket(-0.04) == "q2_2_5pct"
    assert _mae_mfe_bucket(-0.08) == "q3_5_10pct"
    assert _mae_mfe_bucket(-0.15) == "q4_ge_10pct"


def test_t2_regime_changed_during_hold():
    assert _regime_changed_during_hold("calm", "calm") == "no"
    assert _regime_changed_during_hold("calm", "volatile") == "yes"
    assert _regime_changed_during_hold("calm", "unknown") == "unknown"


# ---------------------------------------------------------------------------
# Tier 3
# ---------------------------------------------------------------------------
def test_t3_day_of_week_at_entry():
    assert _day_of_week_at_entry(date(2024, 6, 3)) == "mon"  # Monday
    assert _day_of_week_at_entry(date(2024, 6, 7)) == "fri"  # Friday


def test_t3_days_from_quarter_end():
    # 2024-06-15 → next quarter end is 2024-06-30 → 15 days
    assert _days_from_quarter_end(date(2024, 6, 15)) == 15
    # 2024-12-31 → same day = 0
    assert _days_from_quarter_end(date(2024, 12, 31)) == 0


# ---------------------------------------------------------------------------
# Tier 4
# ---------------------------------------------------------------------------
def test_t4_adv_bucket_no_data():
    assert _adv_bucket(None, date(2024, 6, 1)) == "no_data"
    assert _adv_bucket(pd.DataFrame(), date(2024, 6, 1)) == "no_data"


def test_t4_adv_bucket_computes():
    """Synthetic OHLCV → ADV bucket from close × volume."""
    dates = pd.date_range("2024-05-01", "2024-06-01", freq="B")
    df = pd.DataFrame({
        "date": dates,
        "open": 100, "high": 105, "low": 95, "close": 100, "volume": 100_000,
    })
    # close × volume = 100 × 100_000 = $10M ADV → "5_25M"
    assert _adv_bucket(df, date(2024, 6, 1)) == "5_25M"


def test_t4_hy_oas_returns_known_band_or_no_data():
    """HY OAS fetched from FRED prefetch — either 'no_data' (file missing) or a known band."""
    band = _hy_oas_band_at_entry(date(2024, 6, 1))
    assert band in (
        "compressed_lt_3", "normal_3_5", "wide_5_7", "stressed_ge_7",
        "no_data", "unknown",
    )


# ---------------------------------------------------------------------------
# Integration: build_entry_context returns all 25 columns
# ---------------------------------------------------------------------------
def test_context_returns_all_25_columns():
    """build_entry_context must populate all CONTEXT_COLUMN_NAMES."""
    row = pd.Series({
        "entry_price":               100.0,
        "regime":                    "neutral",
        "sector":                    "Information Technology",
        "confidence_tier":           "MEDIUM",
        "hold_days":                 5,
        "pnl_pct":                   0.03,
        "max_adverse_excursion":     -0.02,
        "max_favourable_excursion":  0.04,
        "exit_date":                 "2024-06-15",
        "market_cap":                50e9,
    })
    df_full = pd.DataFrame({
        "date": pd.date_range("2024-05-01", "2024-06-30", freq="B"),
        "open": 100, "high": 105, "low": 95, "close": 100, "volume": 1_000_000,
    })
    spy_df = df_full.copy()
    signals = {"vix_value": 18, "atr": 2.0, "smart_money_score": 0.7}
    ctx = build_entry_context(
        row=row, ticker="AAPL", entry_date=date(2024, 6, 10),
        df_full=df_full, spy_df=spy_df, signals=signals, atr=2.0,
    )
    # All 25 columns must be present
    for col in CONTEXT_COLUMN_NAMES:
        assert col in ctx, f"Missing context column: {col}"
    # Spot-check key fields
    assert ctx["regime_at_entry"] == "neutral"
    assert ctx["sector"] == "Information Technology"
    assert ctx["hold_duration_band"] == "medium_4_10d"
    assert ctx["win_loss_outcome"] == "win"
    assert ctx["smart_money_signal_present"] == "yes"
    assert ctx["vol_band"] == "mid_15_25"
    assert ctx["cap_band"] == "large_10_200B"
    assert ctx["day_of_week_at_entry"] == "mon"


def test_context_handles_missing_fields_gracefully():
    """build_entry_context must not raise on missing/None fields."""
    row = pd.Series({"entry_price": 100.0})
    df_full = pd.DataFrame({
        "date": pd.date_range("2024-05-01", "2024-06-30", freq="B"),
        "close": 100, "volume": 100_000,
    })
    ctx = build_entry_context(
        row=row, ticker="UNKNOWN_TICKER", entry_date=date(2024, 6, 1),
        df_full=df_full, spy_df=None, signals={}, atr=0.0,
    )
    # All 25 columns present; values may be 'unknown' but structure correct
    for col in CONTEXT_COLUMN_NAMES:
        assert col in ctx, f"Missing context column: {col}"
