#!/usr/bin/env python
"""S6-B3155d: the last NYSE session whose daily bar can no longer change.

WHY. Polygon's daily aggregates endpoint /v2/aggs/ticker/{T}/range/1/day/
{start}/{end} INCLUDES {end}. A fetch whose window ends `date.today()` and
runs while that day's session is open writes a PARTIAL bar - low volume, a
mid-session price as the close - and nothing downstream can tell it from a
full one. MEASURED (S6-B3155a, B3139q-r69n): 479 engine-cache bars for
2026-05-05 were partial sessions, confirmed against a third source; the
engine prices every mark and exit from that cache.

THE RULE. A daily bar for trading day D is complete once US trading for D
has ended: the post-market closes at 20:00 America/New_York, the latest a
trade can print to D's consolidated bar. So the last completed session at a
moment `now` is the latest NYSE trading day D with now >= D 20:00 ET. The
calendar is the engine's own (backtest.engine.improvements), the same one
scripts/preleg_bar_audit.py uses.

Every script that fetches daily bars with an end date taken from the clock
uses `last_completed_session()` (pinned by test_b3155d). yfinance's `end` is
EXCLUSIVE (measured: end=2026-05-06 returned bars through 2026-05-05), so a
yf.download ending today already stops at the last closed session.
"""
from __future__ import annotations

import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SESSION_FINAL_ET = time(20, 0)      # US post-market close: no later print reaches the bar


def last_completed_session(now: datetime | None = None) -> date:
    """The latest NYSE trading day whose daily bar can no longer change at
    `now` (aware datetime; default: the current moment)."""
    from zoneinfo import ZoneInfo

    from backtest.engine.improvements import get_nyse_calendar_helper, is_nyse_trading_day
    et = ZoneInfo("America/New_York")
    now = (now or datetime.now(tz=et)).astimezone(et)
    cal = get_nyse_calendar_helper()
    day = now.date()
    if now.time() < SESSION_FINAL_ET:
        day -= timedelta(days=1)
    for _ in range(15):                 # fail closed rather than walk back without bound
        if is_nyse_trading_day(day, calendar=cal):
            return day
        day -= timedelta(days=1)
    raise RuntimeError(f"no NYSE trading day in the 15 days before {now.date()} - "
                       "refusing to guess a fetch window end")
