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
    """B601 redesigned squeeze_setup_long to a 3-layer 8-gate composite
    (positioning L1 + catalyst L2 + confirmation L3). B622 fixture-
    drift repair: extend fixture with all post-B601 gates so the
    original B519 SI-threshold pin still validates the threshold
    semantically (high SI + supporting catalyst + confirmation
    triggers the strategy)."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = {
        "short_interest_pct": 0.25,           # B519 original SI gate
        "days_to_cover": 9.0,                  # B601 L1b
        "institutional_buy": True,             # B601 L1c (OR composite)
        "news_sentiment_shift": 0.5,           # B601 L2 catalyst
        "above_avwap_20low": True,             # B601 L3 (B205/B598)
        "vol_spike_15x": True,                 # B601 L3
        "close_above_open": True,              # B589/B601 L3
        "close_in_top_40pct_of_range": True,   # B589/B601 L3
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
    """SI == 20% exactly -> fires (>= comparison).
    B622 fixture-drift repair (post-B601 8-gate): extend fixture with
    L1+L2+L3 confirmation gates so the SI threshold-edge is isolated."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = {
        "short_interest_pct": 0.20,            # threshold edge
        "days_to_cover": 9.0,                  # B601 L1b
        "institutional_buy": True,             # B601 L1c
        "news_sentiment_shift": 0.5,           # B601 L2
        "above_avwap_20low": True,             # B601 L3
        "vol_spike_15x": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
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
    """B824 UPDATED + B825 docstring-clarified: B671 Q6 owner-approved
    tightening 5.0 -> 8.0. The strategy now fires only at dtc > 8.0
    (was > 5.0 in original B519). Test fixture dtc 7.5 -> 10.0 above
    new threshold. Function name `_above_5_dtc` is a SEMANTIC DRIFT
    artifact -- kept as-is to preserve test-ID stability across CI
    history; the threshold is actually 8.0 per B671 Q6 owner directive.
    Test verifies "fires when above current threshold (8.0)" not the
    historical 5.0 number embedded in function name."""
    from backtest.signals.screener import strat_short_borrow_trap_avoid
    s = {"days_to_cover": 10.0}  # B824: above new 8.0 threshold
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
    # B622 floor-pin (converted from ==): subsequent batches added more.
    assert len(ALL_STRATEGIES) >= 204


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
