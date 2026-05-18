"""DEC-518 (earnings-blackout) + DEC-521 (per-class time stops) regression tests
(Pass 53 Day-9 v8g).

Specs:
- TRADING_RULES_AND_INFORMATION.md §8.8 (DEC-518)
- TRADING_RULES_AND_INFORMATION.md §8.11 (DEC-521)
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pytest


def _flat_df(start_date=date(2023, 1, 2), n=30):
    idx = pd.date_range(start_date, periods=n, freq="B")
    return pd.DataFrame({
        "open": [100.0]*n, "high": [101.0]*n, "low": [99.0]*n,
        "close": [100.0]*n, "volume": [1_000_000]*n,
    }, index=idx)


# ---------------------------------------------------------------------------
# DEC-518 - Earnings-blackout
# ---------------------------------------------------------------------------
def test_dec518_registry_has_earnings_blackout():
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    assert "earnings_blackout" in EXIT_STRATEGIES


def test_dec518_earnings_tolerant_strategies_list():
    from backtest.engine.exit_strategies import EARNINGS_TOLERANT_STRATEGIES
    expected = {
        "pre_earnings_iv_crush_front_run",
        "guidance_raise_momentum",
        "surprise_magnitude_pead",
        "earnings_cluster_sector_drift",
    }
    assert EARNINGS_TOLERANT_STRATEGIES == expected


def test_dec518_blackout_exits_at_T_minus_1():
    """Long entry 2023-01-02; earnings 2023-01-13 -> exit at close of 2023-01-12."""
    from backtest.engine.exit_strategies import exit_earnings_blackout
    df = _flat_df()
    r = exit_earnings_blackout(
        df, date(2023, 1, 2), 100.0, "long", 2.0,
        ticker="TEST", strategy_name="momentum_breakout",
        earnings_dates=[date(2023, 1, 13)],
    )
    assert r["exit_reason"] == "earnings_blackout_T_minus_1"
    assert r["exit_date"] == date(2023, 1, 12)


def test_dec518_earnings_tolerant_skips_blackout():
    """For pre_earnings_iv_crush_front_run, blackout must NOT fire."""
    from backtest.engine.exit_strategies import exit_earnings_blackout
    df = _flat_df()
    r = exit_earnings_blackout(
        df, date(2023, 1, 2), 100.0, "long", 2.0,
        ticker="TEST", strategy_name="pre_earnings_iv_crush_front_run",
        earnings_dates=[date(2023, 1, 13)],
    )
    assert r["exit_reason"] == "earnings_tolerant_skip"


def test_dec518_no_earnings_known_returns_end_of_data():
    from backtest.engine.exit_strategies import exit_earnings_blackout
    df = _flat_df()
    r = exit_earnings_blackout(
        df, date(2023, 1, 2), 100.0, "long", 2.0,
        ticker="TEST", strategy_name="momentum_breakout",
        earnings_dates=[],
    )
    assert r["exit_reason"] == "no_earnings_known"


def test_dec518_no_upcoming_earnings_returns_end_of_data():
    """Earnings in the past -> no blackout."""
    from backtest.engine.exit_strategies import exit_earnings_blackout
    df = _flat_df()
    r = exit_earnings_blackout(
        df, date(2023, 1, 2), 100.0, "long", 2.0,
        ticker="TEST", strategy_name="momentum_breakout",
        earnings_dates=[date(2022, 11, 1)],  # past earnings only
    )
    assert r["exit_reason"] == "no_upcoming_earnings"


def test_dec518_callable_via_registry_with_signals_dict():
    """Registry adapter passes ticker + strategy_name via signals dict."""
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    df = _flat_df()
    fn = EXIT_STRATEGIES["earnings_blackout"]
    # Without ticker, fetcher fails gracefully -> no_earnings_known
    r = fn(df, date(2023, 1, 2), 100.0, "long", 2.0,
            {"ticker": "ZZZZ_NOT_REAL", "strategy_name": "momentum_breakout"})
    assert r["exit_reason"] in {"no_earnings_known", "no_upcoming_earnings"}


# ---------------------------------------------------------------------------
# DEC-521 - Per-class time stops
# ---------------------------------------------------------------------------
def test_dec521_registry_has_class_time_stop():
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    assert "class_time_stop" in EXIT_STRATEGIES


def test_dec521_default_time_stops_per_category():
    from backtest.engine.exit_strategies import get_max_days_for_category
    # Per spec: pivot 5-10 -> 7 default; momentum 20-30 -> 25; trend 40-60 -> 50
    assert get_max_days_for_category("pivot") == 7
    assert get_max_days_for_category("momentum") == 25
    assert get_max_days_for_category("trend") == 50
    assert get_max_days_for_category("mean_reversion") == 7
    assert get_max_days_for_category("breakout") == 25
    assert get_max_days_for_category("candle") == 7
    # Layer 2/3/6 categories
    assert get_max_days_for_category("ict_smc") == 15
    assert get_max_days_for_category("earnings") == 45
    assert get_max_days_for_category("chart_pattern") == 45
    assert get_max_days_for_category("pairs") == 30
    assert get_max_days_for_category("overnight_gap") == 2


def test_dec521_unknown_category_uses_default():
    from backtest.engine.exit_strategies import get_max_days_for_category
    assert get_max_days_for_category("unknown_cat") == 30
    assert get_max_days_for_category("unknown_cat", default=42) == 42


def test_dec521_confluence_returns_default_caller_overrides():
    """Confluence has None default - caller must compute strictest constituent."""
    from backtest.engine.exit_strategies import get_max_days_for_category
    assert get_max_days_for_category("confluence") == 30  # falls to default


def test_dec521_class_time_stop_mean_reversion_7d():
    from backtest.engine.exit_strategies import exit_class_time_stop
    df = _flat_df(n=30)
    r = exit_class_time_stop(df, date(2023, 1, 2), 100.0, "long", 2.0,
                              category="mean_reversion")
    assert r["exit_reason"] == "class_time_stop_mean_reversion_7d"
    # Day 7 from 2023-01-02 is 2023-01-11 (skip weekends)
    assert r["exit_date"] == date(2023, 1, 11)


def test_dec521_class_time_stop_override_takes_precedence():
    """override_days argument must override category default."""
    from backtest.engine.exit_strategies import exit_class_time_stop
    df = _flat_df(n=30)
    r = exit_class_time_stop(df, date(2023, 1, 2), 100.0, "long", 2.0,
                              category="momentum", override_days=3)
    assert "_3d" in r["exit_reason"]


def test_dec521_callable_via_registry():
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    df = _flat_df(n=30)
    fn = EXIT_STRATEGIES["class_time_stop"]
    r = fn(df, date(2023, 1, 2), 100.0, "long", 2.0, {"category": "pivot"})
    # pivot = 7 days
    assert r["exit_reason"] == "class_time_stop_pivot_7d"


# ---------------------------------------------------------------------------
# EXIT_STRATEGIES total count after DEC-517+518+521
# ---------------------------------------------------------------------------
def test_exit_registry_count_after_dec517_518_521():
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    # 13 baseline (incl. regime_flip) + 3 DEC-517 + 1 DEC-518 + 1 DEC-521 = 18.
    # Batch 226 (2026-05-18 owner-approved research review exit gap):
    # +4 new exit methods (chandelier_3x, atr_trail_vix_conditional,
    # mfe_lockin_trail, atr_trail_mae_conditional) -> 22.
    assert len(EXIT_STRATEGIES) == 22, (
        f"Expected 22 exit methods after DEC-517/518/521 + Batch 226; "
        f"got {len(EXIT_STRATEGIES)}"
    )
