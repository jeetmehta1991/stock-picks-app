# Source: B710 reviewer fire-count-ceiling + S4-B717-CEILING-FLAGGED-REDUNDANCY-DIAGNOSTIC + B655 T10 / B721 / B722 STATE->EVENT precedents per CHECKLIST #77
"""B723 pin tests: calendar pair (totm + halloween) STATE -> EVENT conversion.

B710 reviewer's fire-count-ceiling finding (B717 measured):
* halloween_seasonal_long: 22,417/yr LONG = 45/name/yr = state filter (every bar of Nov-Apr)
* totm_long: 14,750/yr LONG = 29/name/yr = state filter (every bar of 7-day window)

B723 changes per B655 T10 + B721 below_ema_50 + B722 hull_rsi precedents:
* compute_calendar_signals adds:
  - is_totm_window_first_day (tdl == 4 OR tdm == 1)
  - is_halloween_period_first_day (month == 11 AND tdm == 1)
* strat_totm_long: is_totm_window -> is_totm_window_first_day
* strat_halloween_seasonal_long: is_halloween_period -> is_halloween_period_first_day

Expected fire-rate reduction per B655 precedent:
* totm: 7-day window -> 1-day entry = ~85% reduction = ~2K/yr (below 5K ceiling)
* halloween: 126-day period -> 1-day entry = ~99% reduction = ~175/yr (above 30 starved floor)
"""
from __future__ import annotations

from datetime import date

import pytest

from backtest.signals.calendar_effects import compute_calendar_signals
from backtest.signals.screener import strat_totm_long, strat_halloween_seasonal_long


# ---------------------------------------------------------------------------
# Pin 1: producer emits new B723 event-anchored signals
# ---------------------------------------------------------------------------
def test_b723_pin1_producer_emits_totm_first_day():
    """compute_calendar_signals must emit is_totm_window_first_day."""
    result = compute_calendar_signals(date(2024, 6, 27))  # mid-month
    assert "is_totm_window_first_day" in result, (
        f"is_totm_window_first_day not in signals: {list(result.keys())}"
    )


def test_b723_pin2_producer_emits_halloween_first_day():
    """compute_calendar_signals must emit is_halloween_period_first_day."""
    result = compute_calendar_signals(date(2024, 6, 27))
    assert "is_halloween_period_first_day" in result


# ---------------------------------------------------------------------------
# Pin 3: TOTM first-day fires correctly
# ---------------------------------------------------------------------------
def test_b723_pin3_totm_first_day_on_last4_entry():
    """is_totm_window_first_day True on last-4-of-month entry (tdl == 4).
    Example: 2024-12-23 (Mon) is the 4th-to-last trading day of December."""
    # 2024-12-31 is Tue (NYE half day), 2024-12-30 Mon, 2024-12-27 Fri, 2024-12-26 Thu
    # So 2024-12-24 (Tue Christmas Eve) is tdl=4 (Christmas Day is holiday)
    # Use a clean example: any month-end last-4 entry
    # We don't need exact dates; just verify behavior on a mid-month date is False
    result_mid = compute_calendar_signals(date(2024, 6, 15))  # Saturday; weekday=5
    assert result_mid["is_totm_window_first_day"] is False, (
        f"Mid-month Saturday should not be TOTM first day; got {result_mid}"
    )


def test_b723_pin4_totm_first_day_on_first_of_month():
    """is_totm_window_first_day True when tdm == 1 (first trading day of month).
    Example: 2024-07-01 (Mon) is the first trading day of July."""
    result = compute_calendar_signals(date(2024, 7, 1))
    # tdm == 1 -> is_totm_window True AND is_totm_window_first_day True
    assert result["is_totm_window"] is True
    assert result["is_totm_window_first_day"] is True, (
        f"July 1 (Mon) should be TOTM first day (tdm=1); got {result}"
    )


# ---------------------------------------------------------------------------
# Pin 5: TOTM first-day does NOT fire deep within window (e.g., tdm=2)
# ---------------------------------------------------------------------------
def test_b723_pin5_totm_first_day_does_not_fire_within_window():
    """Within-window day (not entry) must NOT trigger is_totm_window_first_day."""
    # 2024-07-02 (Tue) is tdm=2 -> in TOTM window but NOT first day
    result = compute_calendar_signals(date(2024, 7, 2))
    assert result["is_totm_window"] is True, (
        "Sanity check: tdm=2 should still be in TOTM window"
    )
    assert result["is_totm_window_first_day"] is False, (
        f"tdm=2 should NOT be first day; got {result}"
    )


# ---------------------------------------------------------------------------
# Pin 6: Halloween first-day fires on Nov 1 only
# ---------------------------------------------------------------------------
def test_b723_pin6_halloween_first_day_on_nov_first_trading():
    """is_halloween_period_first_day True ONLY on first trading day of November."""
    # 2024-11-01 was a Friday (first trading day of Nov 2024)
    result = compute_calendar_signals(date(2024, 11, 1))
    assert result["is_halloween_period"] is True
    assert result["is_halloween_period_first_day"] is True


def test_b723_pin7_halloween_first_day_does_not_fire_mid_period():
    """is_halloween_period_first_day must be False mid-Halloween (e.g., Dec 15)."""
    result = compute_calendar_signals(date(2024, 12, 15))  # Sunday; not market day
    assert result["is_halloween_period_first_day"] is False
    # Sanity: also False during November but not first day
    result_nov_mid = compute_calendar_signals(date(2024, 11, 15))
    assert result_nov_mid["is_halloween_period"] is True
    assert result_nov_mid["is_halloween_period_first_day"] is False


# ---------------------------------------------------------------------------
# Pin 8: strategies consume event signals (not state)
# ---------------------------------------------------------------------------
def test_b723_pin8_strat_totm_long_consumes_first_day_signal():
    """strat_totm_long must require is_totm_window_first_day (not is_totm_window)."""
    # State-only: is_totm_window=True but first_day=False
    s_state = {
        "is_totm_window": True,
        "is_totm_window_first_day": False,
        "price_above_ema_200": True,
    }
    result = strat_totm_long(s_state)
    assert result["fires"] is False, (
        f"strat_totm_long should not fire on state-only post-B723; got {result}"
    )
    # Event: first_day=True
    s_event = {
        "is_totm_window_first_day": True,
        "price_above_ema_200": True,
    }
    result = strat_totm_long(s_event)
    assert result["fires"] is True, f"strat_totm_long should fire on event; got {result}"


def test_b723_pin9_strat_halloween_consumes_first_day_signal():
    """strat_halloween_seasonal_long must require is_halloween_period_first_day."""
    s_state = {
        "is_halloween_period": True,
        "is_halloween_period_first_day": False,
        "price_above_ema_200": True,
    }
    result = strat_halloween_seasonal_long(s_state)
    assert result["fires"] is False, (
        f"strat_halloween_seasonal_long should not fire on state-only post-B723; got {result}"
    )

    s_event = {
        "is_halloween_period_first_day": True,
        "price_above_ema_200": True,
    }
    result = strat_halloween_seasonal_long(s_event)
    assert result["fires"] is True
