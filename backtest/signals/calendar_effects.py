"""Calendar / Seasonal effects — Track A batch 231 parallel-safe module.

Batch 231 (2026-05-18 owner-approved deferred-items implementation;
parallel-safe with Batch 225 final rerun). Addresses DEC-368 Calendar/
Seasonal strategies (previously SUPERSEDED-BY-DEC-099 umbrella).

Documented calendar effects in equity literature:

1. Turn-of-the-Month (TOTM)
   Source: Ariel 1987 *Journal of Business* "A Monthly Effect in Stock
   Returns"; Lakonishok-Smidt 1988 *RFS* "Are Seasonal Anomalies Real?"
   Mechanism: equity returns concentrate in the last 4 trading days of
   month + first 3 trading days of next month (T-4 to T+3 window).
   Documented Sharpe ~1.0 on the TOTM window 1928-1986; replicated
   McConnell-Xu 2008 *FAJ* post-publication (Sharpe attenuated to ~0.6
   but statistically significant).

2. Pre-Holiday effect
   Source: Lakonishok-Smidt 1988 *RFS*. Equity returns on days
   preceding US market holidays are systematically higher than average.
   Replicated Ariel 1990 *JoF*. Documented 5-10x daily-mean abnormal
   return on the pre-holiday day.

3. January effect (small-cap subset)
   Source: Rozeff-Kinney 1976 *JoF* "Capital Market Seasonality: The
   Case of Stock Returns". Small-cap stocks outperform large-cap in
   January; post-1990 effect attenuated for liquid names but persists
   in micro-caps + recent IPOs (Easterday-Sen-Stephan 2009 *Journal of
   Financial Economics*).

4. Sell-in-May / Halloween indicator
   Source: Bouman-Jacobsen 2002 *American Economic Review* "The
   Halloween Indicator". Equity returns concentrate Nov-Apr ("winter")
   vs May-Oct ("summer"); winter premium 4-5% annualized in US 1970-
   1998. Replicated Andrade-Chhaochharia-Fuerst 2013 *JFE*.

5. Monday weakness (Day-of-Week effect)
   Source: Cross 1973 *FAJ* "The Behavior of Stock Prices on Fridays
   and Mondays"; French 1980 *JFE*. Monday returns historically lower
   than other weekdays; mostly arbitraged away post-1990 (Connolly
   1989 *JFQA*); minor residual remains in small-cap (Brusa-Liu-Schulman
   2003 *JBF*).

This module computes per-date calendar features + emits signal flags
for the strategies in screener.py. Strategy registration is deferred
to post-Batch-225 follow-on batch.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

import pandas as pd


# US market holidays 2020-2030 (subset; expand as needed).
# Per NYSE calendar; partial-trading days (e.g. day after Thanksgiving)
# are NOT in this list since the effect studies use full closures.
_US_MARKET_HOLIDAYS = frozenset({
    # 2022
    date(2022, 1, 17), date(2022, 2, 21), date(2022, 4, 15),
    date(2022, 5, 30), date(2022, 6, 20), date(2022, 7, 4),
    date(2022, 9, 5), date(2022, 11, 24), date(2022, 12, 26),
    # 2023
    date(2023, 1, 2), date(2023, 1, 16), date(2023, 2, 20),
    date(2023, 4, 7), date(2023, 5, 29), date(2023, 6, 19),
    date(2023, 7, 4), date(2023, 9, 4), date(2023, 11, 23),
    date(2023, 12, 25),
    # 2024
    date(2024, 1, 1), date(2024, 1, 15), date(2024, 2, 19),
    date(2024, 3, 29), date(2024, 5, 27), date(2024, 6, 19),
    date(2024, 7, 4), date(2024, 9, 2), date(2024, 11, 28),
    date(2024, 12, 25),
    # 2025
    date(2025, 1, 1), date(2025, 1, 20), date(2025, 2, 17),
    date(2025, 4, 18), date(2025, 5, 26), date(2025, 6, 19),
    date(2025, 7, 4), date(2025, 9, 1), date(2025, 11, 27),
    date(2025, 12, 25),
    # 2026
    date(2026, 1, 1), date(2026, 1, 19), date(2026, 2, 16),
    date(2026, 4, 3), date(2026, 5, 25), date(2026, 6, 19),
    date(2026, 7, 3), date(2026, 9, 7), date(2026, 11, 26),
    date(2026, 12, 25),
})


def _next_business_day(d: date) -> date:
    """Next non-weekend non-holiday business day."""
    d2 = d + timedelta(days=1)
    while d2.weekday() >= 5 or d2 in _US_MARKET_HOLIDAYS:
        d2 += timedelta(days=1)
    return d2


def _is_business_day(d: date) -> bool:
    return d.weekday() < 5 and d not in _US_MARKET_HOLIDAYS


def _trading_day_of_month(d: date) -> int:
    """Return 1-indexed trading day of the month (1 = first trading day)."""
    first = date(d.year, d.month, 1)
    day = first
    counter = 0
    while day <= d:
        if _is_business_day(day):
            counter += 1
        day += timedelta(days=1)
    return counter


def _trading_days_left_in_month(d: date) -> int:
    """Number of remaining trading days in month including today."""
    if d.month == 12:
        next_month_first = date(d.year + 1, 1, 1)
    else:
        next_month_first = date(d.year, d.month + 1, 1)
    counter = 0
    cur = d
    while cur < next_month_first:
        if _is_business_day(cur):
            counter += 1
        cur += timedelta(days=1)
    return counter


def _days_to_next_holiday(d: date, max_lookahead: int = 30) -> Optional[int]:
    """Calendar days until next US market holiday (None if none in window)."""
    for delta in range(1, max_lookahead + 1):
        cand = d + timedelta(days=delta)
        if cand in _US_MARKET_HOLIDAYS:
            return delta
    return None


def compute_calendar_signals(as_of: date) -> dict:
    """Compute calendar / seasonal signals for a given trading date.

    Returns dict (universe-wide; same for all tickers on a given day):
      - dow:                          int 0-4 (Mon=0)
      - is_monday:                    bool
      - is_friday:                    bool
      - trading_day_of_month:         int (1-indexed)
      - trading_days_left_in_month:   int (incl today)
      - is_totm_window:               bool (Ariel 1987 last-4 + first-3
                                       Trading-Of-The-Month window)
      - is_january:                   bool
      - is_pre_holiday:               bool (next biz day is US holiday)
      - is_halloween_period:          bool (Nov-Apr per Bouman-Jacobsen)
      - is_summer_period:             bool (May-Oct)
      - days_to_next_holiday:         int (calendar; None if >30 days)
    """
    if as_of is None:
        return {}
    out: dict = {}
    dow = as_of.weekday()
    out["dow"] = dow
    out["is_monday"] = dow == 0
    out["is_friday"] = dow == 4
    tdm = _trading_day_of_month(as_of)
    tdl = _trading_days_left_in_month(as_of)
    out["trading_day_of_month"] = tdm
    out["trading_days_left_in_month"] = tdl
    # TOTM window: last 4 trading days of month OR first 3 of next month
    out["is_totm_window"] = bool((tdl <= 4) or (tdm <= 3))
    out["is_january"] = (as_of.month == 1)
    # Pre-holiday: next CALENDAR day (after weekend gap) is a US market
    # holiday. _next_business_day skips holidays by design and would
    # always evaluate False here; walk forward through weekend until
    # hitting a non-weekend day, then check if that day is a holiday.
    pre = as_of + timedelta(days=1)
    while pre.weekday() >= 5 and pre not in _US_MARKET_HOLIDAYS:
        pre += timedelta(days=1)
    out["is_pre_holiday"] = pre in _US_MARKET_HOLIDAYS
    out["days_to_next_holiday"] = _days_to_next_holiday(as_of)
    # Halloween / Sell-in-May
    out["is_halloween_period"] = as_of.month in (11, 12, 1, 2, 3, 4)
    out["is_summer_period"] = as_of.month in (5, 6, 7, 8, 9, 10)
    return out
