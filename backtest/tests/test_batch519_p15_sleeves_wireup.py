"""Batch 519 (2026-05-31) -- P15 sleeve strategies + producer wire-in.

Source: per CHECKLIST #77 + owner directive 2026-05-31 ("execute other
pending tasks") which approves the P15 queue's stated "next step":
register squeeze_setup_long + short_borrow_trap_avoid in ALL_STRATEGIES
+ wire compute_short_interest_signals into screener.

Tests:
  1. Both sleeve functions importable + correctly classified
  2. squeeze_setup_long fires when high SI + DC20 breakout + volume
  3. short_borrow_trap_avoid fires as `avoid` direction when DTC > 5
  4. ALL_STRATEGIES count = 202 (was 200 pre-519)
  5. Producer wired into screen_instrument signals dict
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Sleeve fire semantics
# ---------------------------------------------------------------------------

def test_batch519_squeeze_setup_long_fires_on_high_si_plus_breakout():
    from backtest.signals.screener import strat_squeeze_setup_long
    s = {
        "short_interest_pct": 0.25,  # 25% SI -- well above 20% threshold
        "dc20_breakout_up": True,
        "vol_above_avg": True,
    }
    r = strat_squeeze_setup_long(s)
    assert r["fires"] is True
    assert r["direction"] == "long"
    assert r["category"] == "smart_money_sleeve"


def test_batch519_squeeze_setup_long_misses_low_si():
    """SI < 20% -> no fire even if breakout + volume."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = {
        "short_interest_pct": 0.10,  # 10% SI -- below threshold
        "dc20_breakout_up": True,
        "vol_above_avg": True,
    }
    assert strat_squeeze_setup_long(s)["fires"] is False


def test_batch519_squeeze_setup_long_misses_without_breakout():
    """High SI but no DC20 breakout -> no fire."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = {
        "short_interest_pct": 0.25,
        "dc20_breakout_up": False,
        "vol_above_avg": True,
    }
    assert strat_squeeze_setup_long(s)["fires"] is False


def test_batch519_squeeze_setup_long_misses_without_volume():
    """High SI + breakout but volume not confirming -> no fire."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = {
        "short_interest_pct": 0.25,
        "dc20_breakout_up": True,
        "vol_above_avg": False,
    }
    assert strat_squeeze_setup_long(s)["fires"] is False


def test_batch519_squeeze_threshold_boundary_at_20_pct():
    """SI == 20% exactly -> fires (>= comparison)."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = {
        "short_interest_pct": 0.20,
        "dc20_breakout_up": True,
        "vol_above_avg": True,
    }
    assert strat_squeeze_setup_long(s)["fires"] is True


def test_batch519_squeeze_handles_missing_si_signal_gracefully():
    """When short_interest_pct missing (ticker not in FINRA cache),
    SI defaults to 0 -> no fire."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = {"dc20_breakout_up": True, "vol_above_avg": True}
    assert strat_squeeze_setup_long(s)["fires"] is False


# ---------------------------------------------------------------------------
# Short-borrow-trap-avoid
# ---------------------------------------------------------------------------

def test_batch519_short_borrow_trap_avoid_fires_above_5_dtc():
    """Days-to-cover > 5 -> fires `avoid` direction."""
    from backtest.signals.screener import strat_short_borrow_trap_avoid
    s = {"days_to_cover": 7.5}
    r = strat_short_borrow_trap_avoid(s)
    assert r["fires"] is True
    assert r["direction"] == "avoid"
    assert r["category"] == "smart_money_sleeve"


def test_batch519_short_borrow_trap_avoid_boundary_at_5_dtc():
    """DTC == 5 -> no fire (strict >)."""
    from backtest.signals.screener import strat_short_borrow_trap_avoid
    s = {"days_to_cover": 5.0}
    assert strat_short_borrow_trap_avoid(s)["fires"] is False


def test_batch519_short_borrow_trap_avoid_below_threshold():
    """DTC = 3 -> no fire."""
    from backtest.signals.screener import strat_short_borrow_trap_avoid
    assert strat_short_borrow_trap_avoid({"days_to_cover": 3.0})["fires"] is False


def test_batch519_short_borrow_trap_avoid_missing_dtc_no_fire():
    """When days_to_cover missing (no FINRA cache for ticker), default
    0 -> no fire."""
    from backtest.signals.screener import strat_short_borrow_trap_avoid
    assert strat_short_borrow_trap_avoid({})["fires"] is False


# ---------------------------------------------------------------------------
# Registration in ALL_STRATEGIES
# ---------------------------------------------------------------------------

def test_batch519_squeeze_setup_long_registered():
    from backtest.signals.screener import ALL_STRATEGIES
    assert "squeeze_setup_long" in ALL_STRATEGIES


def test_batch519_short_borrow_trap_avoid_registered():
    from backtest.signals.screener import ALL_STRATEGIES
    assert "short_borrow_trap_avoid" in ALL_STRATEGIES


def test_batch519_all_strategies_count_is_204_post_p17():
    """SM1 188->198 (Batch 487) + M6 198->200 (Batch 507) + P15
    200->202 (Batch 519) + P17 202->204 (Batch 531)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 204


# ---------------------------------------------------------------------------
# Producer wired into screener.screen_instrument
# ---------------------------------------------------------------------------

def test_batch519_short_interest_producer_wired_in_screener():
    """Pin the wire-in in backtest/signals/screener.py."""
    from pathlib import Path
    src = (
        Path(__file__).resolve().parent.parent / "signals" / "screener.py"
    ).read_text(encoding="utf-8")
    assert "from backtest.signals.short_interest import compute_short_interest_signals" in src
    assert "compute_short_interest_signals(ticker, as_of)" in src
    # Silent-failure logger wraps the producer call
    assert '_log_silent_producer_failure("short_interest", _e)' in src
