# Source: B700 reviewer CP-2 Phase-3 spec + B710 W1 strong-close + S4-B717 ceiling routing per CHECKLIST #77
"""B730 pin tests: strat_double_bottom_long ceiling fix per queued S4-B700-CP-2 reviewer-spec.

B710 reviewer's fire-count-ceiling finding (B717 measured):
* double_bottom_long: 7,510/yr LONG = state-flag rate

B700 reviewer CP-2 Phase-3 spec implemented in B730:
* Strong-close confirmation (close_in_top_40pct_of_range) -- B710 W1 anti-fakeout
* Volume confirmation (vol_spike_15x) -- Bulkowski 2005 conditional WR stats

Deferred per `feedback_no_rushing_per_strategy_tweak`:
* ATR-clearance margin sweep (needs chart_patterns.py producer changes)
* Second-bottom symmetry tolerance parameter (needs chart_patterns.py)
"""
from __future__ import annotations

from backtest.signals.screener import strat_double_bottom_long


def test_b730_pin1_requires_strong_close():
    """Strategy must require close_in_top_40pct_of_range (B710 W1 pattern)."""
    s_no_strong = {
        "double_bottom_detected": True,
        "price_above_ema_200": True,
        "close_in_top_40pct_of_range": False,
        "vol_spike_15x": True,
    }
    result = strat_double_bottom_long(s_no_strong)
    assert result["fires"] is False, (
        f"Should not fire without strong-close post-B730; got {result}"
    )


def test_b730_pin2_requires_vol_spike_15x():
    """Strategy must require vol_spike_15x (Bulkowski neckline-break volume)."""
    s_no_vol = {
        "double_bottom_detected": True,
        "price_above_ema_200": True,
        "close_in_top_40pct_of_range": True,
        "vol_spike_15x": False,
    }
    result = strat_double_bottom_long(s_no_vol)
    assert result["fires"] is False, (
        f"Should not fire without vol_spike_15x post-B730; got {result}"
    )


def test_b730_pin3_fires_with_all_4_gates():
    """All 4 gates True -> fires."""
    s_all = {
        "double_bottom_detected": True,
        "price_above_ema_200": True,
        "close_in_top_40pct_of_range": True,
        "vol_spike_15x": True,
    }
    result = strat_double_bottom_long(s_all)
    assert result["fires"] is True
    assert result["direction"] == "long"


def test_b730_pin4_signals_used_declares_new_gates():
    """signals_used must declare the 2 B730 gates."""
    s = {
        "double_bottom_detected": True,
        "price_above_ema_200": True,
        "close_in_top_40pct_of_range": True,
        "vol_spike_15x": True,
    }
    result = strat_double_bottom_long(s)
    assert "close_in_top_40pct_of_range" in result["signals_used"]
    assert "vol_spike_15x" in result["signals_used"]


def test_b730_pin5_pattern_detection_still_required():
    """double_bottom_detected gate still required (didn't break the core pattern)."""
    s_no_pattern = {
        "double_bottom_detected": False,
        "price_above_ema_200": True,
        "close_in_top_40pct_of_range": True,
        "vol_spike_15x": True,
    }
    result = strat_double_bottom_long(s_no_pattern)
    assert result["fires"] is False
