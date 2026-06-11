# Source: B709 EMPIRICAL-RESTORE per CHECKLIST #77
"""B709 pin tests: EV-3 + EV-4 restoration after B682 deletion.

Background:
  B682 (2026-06-10) deleted strat_pead_long_high_yoy_growth_only (EV-3) +
  strat_pead_short_negative_yoy_growth (EV-4) citing "Pattern W deterministic
  strict subset" of EV-1/EV-2.

  B702 (2026-06-11) adversarial review flagged the rationale as logically
  incomplete (subset on YoY VALUES != subset of FIRE EVENTS).

  B709 (2026-06-12) empirically measured phi correlation = 0.297 on 29 T1a
  tickers, 2020-2026, 5-day-stride probes. 70% of EV-3 fires are a
  population EV-1 misses entirely. Verdict: REVERT B682.

  Owner approved revert 2026-06-12.

These pins lock in that:
  1. Both strategy functions exist + are callable
  2. Both are registered in ALL_STRATEGIES
  3. Both fire correctly on their respective signal-dict inputs
"""
from __future__ import annotations

import importlib


def test_b709_pin1_strategy_functions_importable():
    """EV-3 + EV-4 must be importable from screener after revert."""
    from backtest.signals.screener import (
        strat_pead_long_high_yoy_growth_only,
        strat_pead_short_negative_yoy_growth,
    )
    assert callable(strat_pead_long_high_yoy_growth_only)
    assert callable(strat_pead_short_negative_yoy_growth)


def test_b709_pin2_all_strategies_registry_contains_both():
    """EV-3 + EV-4 must appear in ALL_STRATEGIES dict by their registry keys."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "pead_long_high_yoy_growth_only" in ALL_STRATEGIES, (
        "EV-3 key 'pead_long_high_yoy_growth_only' missing from ALL_STRATEGIES "
        "-- B682 deletion not fully reverted in registry."
    )
    assert "pead_short_negative_yoy_growth" in ALL_STRATEGIES, (
        "EV-4 key 'pead_short_negative_yoy_growth' missing from ALL_STRATEGIES "
        "-- B682 deletion not fully reverted in registry."
    )


def test_b709_pin3_ev3_fires_on_yoy_high_with_window_open():
    """EV-3 fires when within_pead_window=True AND yoy_surprise_high=True."""
    from backtest.signals.screener import strat_pead_long_high_yoy_growth_only
    sigs = {
        "within_pead_window":         True,
        "yoy_surprise_high":          True,
        "earnings_eps_yoy_growth":    0.07,
        "yoy_surprise_threshold_long": 0.05,
    }
    out = strat_pead_long_high_yoy_growth_only(sigs)
    assert out["fires"] is True, f"Expected fires=True; got {out}"
    assert out["direction"] == "long"


def test_b709_pin4_ev3_does_not_fire_without_window():
    """EV-3 must require within_pead_window=True."""
    from backtest.signals.screener import strat_pead_long_high_yoy_growth_only
    sigs = {
        "within_pead_window":   False,
        "yoy_surprise_high":    True,
        "earnings_eps_yoy_growth": 0.07,
    }
    out = strat_pead_long_high_yoy_growth_only(sigs)
    assert out["fires"] is False


def test_b709_pin5_ev3_does_not_fire_without_yoy_high():
    """EV-3 must require yoy_surprise_high=True."""
    from backtest.signals.screener import strat_pead_long_high_yoy_growth_only
    sigs = {
        "within_pead_window":   True,
        "yoy_surprise_high":    False,
        "earnings_eps_yoy_growth": 0.02,
    }
    out = strat_pead_long_high_yoy_growth_only(sigs)
    assert out["fires"] is False


def test_b709_pin6_ev4_fires_on_yoy_negative_with_window_open():
    """EV-4 fires when within_pead_window=True AND yoy_surprise_negative=True."""
    from backtest.signals.screener import strat_pead_short_negative_yoy_growth
    sigs = {
        "within_pead_window":         True,
        "yoy_surprise_negative":      True,
        "earnings_eps_yoy_growth":    -0.07,
        "yoy_surprise_threshold_short": -0.05,
    }
    out = strat_pead_short_negative_yoy_growth(sigs)
    assert out["fires"] is True, f"Expected fires=True; got {out}"
    assert out["direction"] == "short"


def test_b709_pin7_ev4_does_not_fire_without_yoy_negative():
    """EV-4 must require yoy_surprise_negative=True."""
    from backtest.signals.screener import strat_pead_short_negative_yoy_growth
    sigs = {
        "within_pead_window":     True,
        "yoy_surprise_negative":  False,
        "earnings_eps_yoy_growth": -0.02,
    }
    out = strat_pead_short_negative_yoy_growth(sigs)
    assert out["fires"] is False


def test_b709_pin8_strategy_roster_count_increased_by_two():
    """ALL_STRATEGIES dict should be 220 post-restore (was 218 pre-B709).

    Note: this is a soft assertion -- other concurrent strategy additions
    could shift the count. We just require >= 220 since B709 added 2.
    """
    from backtest.signals.screener import ALL_STRATEGIES
    n = len(ALL_STRATEGIES)
    assert n >= 220, (
        f"Expected ALL_STRATEGIES >= 220 post-B709 restore; got {n}. "
        f"Either B709 restore is incomplete or another concurrent deletion "
        f"shifted the count."
    )
