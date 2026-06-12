# Source: B710 W1 strong-close + S4-B717 ceiling routing per CHECKLIST #77
"""B728 pin tests: 3-strategy breakout retest batch adds strong-close gate.

B710 reviewer's fire-count-ceiling finding (B717 measured):
* dc20_break_retest: 6,379 LONG + 3,880 SHORT per year
* break_retest_volume: 6,532 LONG + 3,902 SHORT per year
* break_retest_confluence: 6,015 LONG + 3,693 SHORT per year

B728 changes (3 strategies; r1_break_retest already has strong-close from B606):
* dc20_break_retest: add close_in_top_40pct_of_range (LONG) + _bottom_40pct (SHORT)
* break_retest_volume: same additions
* break_retest_confluence: same additions

Pattern: B710 W1 strong-close anti-fakeout (existing close_above_open is ~50% True;
strong-close gate separates real-retest-hold from weak-bounce).
"""
from __future__ import annotations

from backtest.signals.screener import (
    strat_dc20_break_retest,
    strat_break_retest_volume,
    strat_break_retest_confluence,
)


def _make_long_signal_base():
    return {
        "resistance_break_retest": True,
        "vol_below_avg": True,
        "adx_trending": True,
        "obv_bullish": True,
        "macd_12_26_9_bullish": True,
        "price_above_ema_20": True,
        "price_above_ema_50": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,  # B728
    }


def _make_short_signal_base():
    return {
        "support_break_retest": True,
        "vol_below_avg": True,
        "adx_trending": True,
        "obv_bearish": True,
        "macd_12_26_9_bearish": True,
        "below_ema_20": True,
        "below_ema_50": True,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,  # B728
        "days_to_cover": 2.0,  # below B718a 5.0 borrow gate
    }


# ---------------------------------------------------------------------------
# dc20_break_retest
# ---------------------------------------------------------------------------
def test_b728_pin1_dc20_break_retest_requires_strong_close_long():
    s = _make_long_signal_base()
    # Without strong-close: should not fire
    s["close_in_top_40pct_of_range"] = False
    r = strat_dc20_break_retest(s)
    assert r["fires"] is False, f"Should not fire without strong-close LONG; got {r}"

    s["close_in_top_40pct_of_range"] = True
    r2 = strat_dc20_break_retest(s)
    assert r2["fires"] is True
    assert r2["direction"] == "long"


def test_b728_pin2_dc20_break_retest_requires_strong_close_short():
    s = _make_short_signal_base()
    s["close_in_bottom_40pct_of_range"] = False
    r = strat_dc20_break_retest(s)
    assert r["fires"] is False, f"Should not fire without strong-close SHORT; got {r}"

    s["close_in_bottom_40pct_of_range"] = True
    r2 = strat_dc20_break_retest(s)
    assert r2["fires"] is True
    assert r2["direction"] == "short"


# ---------------------------------------------------------------------------
# break_retest_volume
# ---------------------------------------------------------------------------
def test_b728_pin3_break_retest_volume_requires_strong_close():
    s = _make_long_signal_base()
    s["close_in_top_40pct_of_range"] = False
    assert strat_break_retest_volume(s)["fires"] is False

    s["close_in_top_40pct_of_range"] = True
    r = strat_break_retest_volume(s)
    assert r["fires"] is True
    assert r["direction"] == "long"


# ---------------------------------------------------------------------------
# break_retest_confluence
# ---------------------------------------------------------------------------
def test_b728_pin4_break_retest_confluence_requires_strong_close():
    s = _make_long_signal_base()
    s["close_in_top_40pct_of_range"] = False
    assert strat_break_retest_confluence(s)["fires"] is False

    s["close_in_top_40pct_of_range"] = True
    r = strat_break_retest_confluence(s)
    assert r["fires"] is True


# ---------------------------------------------------------------------------
# signals_used declarations
# ---------------------------------------------------------------------------
def test_b728_pin5_signals_used_declares_strong_close_gates():
    """All 3 B728-modified strategies declare close_in_top_40pct_of_range."""
    s = _make_long_signal_base()
    for fn in (strat_dc20_break_retest, strat_break_retest_volume, strat_break_retest_confluence):
        r = fn(s)
        assert "close_in_top_40pct_of_range" in r["signals_used"], (
            f"{fn.__name__} must declare close_in_top_40pct_of_range; got {r['signals_used']}"
        )
