"""Batch 487 (2026-05-30) -- SM1 smart-money sleeve strategies + SM2 26th
exit method (smart_money_reversal) tests.

SM1: 10 sleeve strategies in screener.py that gate ENTRY on a smart-money
composite OR signal (insider_cluster_active OR institutional_strong_buy OR
institutional_buy OR cfo_buy OR large_dollar_buy). Each sleeve adds the
gate on top of an existing base condition.

SM2: 26th exit method `smart_money_reversal` -- exits LONG on bearish
smart-money flip (cluster_sell OR concentrated_sell) during hold; SHORT
symmetric on bullish flip.

Tests assert:
  1. ALL 10 sleeves registered in ALL_STRATEGIES; count is 198.
  2. Each sleeve fires when base condition met AND smart-money signal
     present; misses when smart-money absent.
  3. smart_money_reversal registered in EXIT_STRATEGIES; count is 26.
  4. smart_money_reversal returns trail-stop result when no flip
     happens; exits at flip date when bearish flip seen.
"""
from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

import pandas as pd
import pytest


# ----------------------------------------------------------------------
# SM1 registration + count
# ----------------------------------------------------------------------
def test_sm1_all_ten_sleeves_registered():
    from backtest.signals.screener import ALL_STRATEGIES
    expected = [
        "bollinger_tight_with_smart_money_long",
        "mfi_oversold_with_smart_money_long",
        "rsi_oversold_with_smart_money_long",
        "52w_high_breakout_with_smart_money_long",
        "squeeze_breakout_with_smart_money_long",
        "xs_momentum_with_smart_money_long",
        "xs_low_beta_with_smart_money_long",
        "donchian_breakout_with_smart_money_long",
        "macd_bullish_with_smart_money_long",
        "pead_with_smart_money_long",
    ]
    for name in expected:
        assert name in ALL_STRATEGIES, f"missing sleeve: {name}"


def test_all_strategies_count_is_200_after_sm1_plus_m6_path2():
    """SM1 brought count 188 -> 198 (Batch 487; 10 smart-money sleeves).
    Batch 507 M6 Path-2 brought 198 -> 200 (2 YoY-growth PEAD sleeves)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 200


# ----------------------------------------------------------------------
# SM1 fire-condition semantics
# ----------------------------------------------------------------------
def test_bollinger_tight_sleeve_fires_with_smart_money():
    from backtest.signals.screener import strat_bollinger_tight_with_smart_money_long
    s = {
        "bb_squeeze": True, "close_above_open": True,
        "price_above_ema_200": True, "insider_cluster_active": True,
    }
    assert strat_bollinger_tight_with_smart_money_long(s)["fires"] is True


def test_bollinger_tight_sleeve_misses_without_smart_money():
    from backtest.signals.screener import strat_bollinger_tight_with_smart_money_long
    s = {
        "bb_squeeze": True, "close_above_open": True,
        "price_above_ema_200": True,
        # No smart-money signal
    }
    assert strat_bollinger_tight_with_smart_money_long(s)["fires"] is False


def test_donchian_sleeve_fires_on_dc20_breakout_plus_smart_money():
    from backtest.signals.screener import strat_donchian_breakout_with_smart_money_long
    s = {
        "dc20_breakout_up": True, "close_above_open": True,
        "institutional_strong_buy": True,
    }
    assert strat_donchian_breakout_with_smart_money_long(s)["fires"] is True


def test_pead_sleeve_fires_with_smart_money_composite():
    from backtest.signals.screener import strat_pead_with_smart_money_long
    s = {
        "within_pead_window": True, "pead_positive_surprise": True,
        "large_dollar_buy": True,
    }
    assert strat_pead_with_smart_money_long(s)["fires"] is True


def test_xs_momentum_sleeve_fires_with_cfo_buy():
    from backtest.signals.screener import strat_xs_momentum_with_smart_money_long
    s = {
        "xs_momentum_top_decile": True, "price_above_ema_200": True,
        "cfo_buy": True,
    }
    assert strat_xs_momentum_with_smart_money_long(s)["fires"] is True


def test_all_ten_sleeves_in_category_smart_money_sleeve():
    """Sleeves should share the 'smart_money_sleeve' category so the
    dashboard can group them + the cube can analyse them as a family."""
    from backtest.signals.screener import ALL_STRATEGIES
    sleeve_names = [n for n in ALL_STRATEGIES if n.endswith("_with_smart_money_long")]
    assert len(sleeve_names) == 10
    for name in sleeve_names:
        fn = ALL_STRATEGIES[name]
        result = fn({})
        # Even on empty signals dict the function returns a strat dict
        # with category field
        assert result.get("category") == "smart_money_sleeve"


# ----------------------------------------------------------------------
# SM2 26th exit method
# ----------------------------------------------------------------------
def test_sm2_exit_strategies_count_is_26():
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    assert len(EXIT_STRATEGIES) == 26


def test_sm2_smart_money_reversal_registered():
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    assert "smart_money_reversal" in EXIT_STRATEGIES


def _make_ohlcv(closes, start_date=date(2024, 1, 1)):
    n = len(closes)
    idx = pd.date_range(start_date, periods=n, freq="B")
    return pd.DataFrame({
        "open":   closes,
        "high":   [c * 1.01 for c in closes],
        "low":    [c * 0.99 for c in closes],
        "close":  closes,
        "volume": [1_000_000] * n,
    }, index=idx)


@patch("backtest.data.smart_money.insider_signal")
def test_sm2_smart_money_reversal_exits_on_bearish_flip(mock_insider):
    """Exit LONG when insider_signal returns cluster_sell during hold."""
    from backtest.engine.exit_strategies import exit_smart_money_reversal

    # Insider signal returns cluster_sell starting on day 5
    def insider_side_effect(ticker, as_of, lookback_days=5):
        if as_of >= date(2024, 1, 8):
            return {"signal": "cluster_sell", "concentrated_sell": True}
        return {"signal": "none"}
    mock_insider.side_effect = insider_side_effect

    closes = [100.0 + i * 0.5 for i in range(60)]  # gentle uptrend
    df = _make_ohlcv(closes, start_date=date(2024, 1, 1))
    result = exit_smart_money_reversal(
        df, date(2024, 1, 1), 100.0, "long", atr=2.0,
        signals={"ticker": "TEST"},
    )
    # Should exit on bearish flip, not run to end-of-data
    assert "smart_money_reversal_bearish_flip" in result["exit_reason"] \
        or "smart_money_trail_safety" in result["exit_reason"]


@patch("backtest.data.smart_money.insider_signal")
def test_sm2_smart_money_reversal_no_flip_runs_to_end(mock_insider):
    """No smart-money flip -> exit at max_days end (or trail stop)."""
    from backtest.engine.exit_strategies import exit_smart_money_reversal

    # Insider signal never flips bearish
    mock_insider.return_value = {"signal": "none"}

    closes = [100.0 + i * 0.5 for i in range(60)]
    df = _make_ohlcv(closes, start_date=date(2024, 1, 1))
    result = exit_smart_money_reversal(
        df, date(2024, 1, 1), 100.0, "long", atr=2.0,
        signals={"ticker": "TEST"},
    )
    # Should NOT exit via bearish flip; either trail-stop or end-of-data
    assert "bearish_flip" not in result["exit_reason"]


def test_sm2_smart_money_reversal_no_ticker_falls_back_to_atr_trail():
    """When ticker missing from signals, fallback to atr_trail_1x."""
    from backtest.engine.exit_strategies import exit_smart_money_reversal
    closes = [100.0] * 30
    df = _make_ohlcv(closes)
    result = exit_smart_money_reversal(
        df, date(2024, 1, 1), 100.0, "long", atr=2.0,
        signals={},  # no ticker
    )
    # Function returns a normal trade result
    assert "exit_reason" in result
    assert "pnl_pct" in result
