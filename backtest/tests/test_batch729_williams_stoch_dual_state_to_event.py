# Source: B655 T10 + B721 + B722 STATE->EVENT precedents + S4-B717 ceiling routing per CHECKLIST #77
"""B729 pin tests: strat_williams_stoch_dual STATE -> EVENT conversion.

B710 reviewer's fire-count-ceiling finding (B717 measured):
* williams_stoch_dual: 4,091 LONG + 6,587 SHORT per year (SHORT above ceiling)

B729 changes:
* LONG: stoch_oversold (STATE) -> stoch_bullish_cross (EVENT)
* SHORT: stoch_overbought (STATE) -> stoch_bearish_cross (EVENT)
* Williams %R + pivot proximity gates unchanged

Pattern: B655 T10 STATE -> EVENT applied symmetrically.
"""
from __future__ import annotations

from backtest.signals.screener import strat_williams_stoch_dual


def test_b729_pin1_long_consumes_stoch_bullish_cross():
    """LONG branch must consume stoch_bullish_cross, not stoch_oversold."""
    # STATE-only (oversold True but no cross) -> should not fire
    s_state = {
        "williams_r_oversold": True,
        "stoch_oversold": True,
        "stoch_bullish_cross": False,
        "near_s1": True,
    }
    result = strat_williams_stoch_dual(s_state)
    assert result["fires"] is False, (
        f"Should not fire on STATE-only post-B729; got {result}"
    )

    # EVENT cross True -> should fire
    s_event = {
        "williams_r_oversold": True,
        "stoch_bullish_cross": True,
        "near_s1": True,
    }
    result = strat_williams_stoch_dual(s_event)
    assert result["fires"] is True
    assert result["direction"] == "long"


def test_b729_pin2_short_consumes_stoch_bearish_cross():
    """SHORT branch must consume stoch_bearish_cross, not stoch_overbought."""
    s_state = {
        "williams_r": -10,
        "stoch_overbought": True,
        "stoch_bearish_cross": False,
        "near_r1": True,
        "days_to_cover": 2.0,
    }
    result = strat_williams_stoch_dual(s_state)
    assert result["fires"] is False, (
        f"Should not fire on STATE-only post-B729; got {result}"
    )

    s_event = {
        "williams_r": -10,
        "stoch_bearish_cross": True,
        "near_r1": True,
        "days_to_cover": 2.0,
    }
    result = strat_williams_stoch_dual(s_event)
    assert result["fires"] is True
    assert result["direction"] == "short"


def test_b729_pin3_signals_used_declares_event_signals():
    """signals_used must declare cross events, not oversold/overbought."""
    s_long = {
        "williams_r_oversold": True,
        "stoch_bullish_cross": True,
        "near_s1": True,
    }
    r = strat_williams_stoch_dual(s_long)
    assert "stoch_bullish_cross" in r["signals_used"]


def test_b729_pin4_pivot_gate_still_required():
    """Pivot proximity gate (near_s1/s2/cam_s3 for LONG) still required."""
    s_no_pivot = {
        "williams_r_oversold": True,
        "stoch_bullish_cross": True,
        # No pivot proximity
    }
    result = strat_williams_stoch_dual(s_no_pivot)
    assert result["fires"] is False
