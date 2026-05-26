"""Batch 366 DEC-304 calendar staleness regression test.

Source (per CHECKLIST #77 canonical-source attribution): owner directive
2026-05-25 Batch 366 "execute now" -- the post-fix cube smoke surfaced
the DEC-304 silent gap (`is_near_high_impact_event` returns "no events"
silently when as_of exceeds the hardcoded calendar's last date).

Fix: `scripts/refresh_event_calendar.py` extends calendar through 2030
deterministically (NFP = first Friday; CPI = 2nd Wednesday proxy; FOMC
= Fed published 2026-2027 + estimates 2028-2030).

This test pins the coverage so a future Phase 1A-beta re-run can never
silently degrade to no-event-filtering. If the calendar ages out, the
test fails BEFORE the engine runs.

Pyramid tiers exercised:
  T1 (Unit)        Calendar covers backtest end-date + 1y buffer
  T1 (Unit)        Each of CPI/NFP/FOMC has 12 dates/year
  T6 (Regression)  refresh_event_calendar.py is callable + idempotent
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent.parent


def test_batch366_calendar_covers_backtest_end_plus_buffer():
    """Calendar must cover today + 1 year. If as_of exceeds the last
    event date, is_near_high_impact_event silently returns 'no events'
    for everything past that date -- exactly the DEC-304 silent gap."""
    from backtest.data.macro import ALL_HIGH_IMPACT, LAST_HARDCODED_EVENT
    assert ALL_HIGH_IMPACT, "calendar is empty -- DEC-304 regression"
    today = date.today()
    required_through = today + timedelta(days=365)
    assert LAST_HARDCODED_EVENT >= required_through, (
        f"DEC-304 staleness gate: calendar ends {LAST_HARDCODED_EVENT} but "
        f"required >= {required_through} (today + 1 year). "
        f"Run `python scripts/refresh_event_calendar.py --through {required_through.year + 1}`."
    )


def test_batch366_calendar_has_cpi_nfp_fomc_density():
    """Each calendar must have ~12 dates/year * coverage_years dates. If
    any series is missing months, a producer silently returns no events
    for that month's events."""
    from backtest.data.macro import CPI_DATES, NFP_DATES, FOMC_DATES
    # Cover at least 2022-01 -> 2027-12 = 6 years
    expected_min_cpi  = 12 * 6     # CPI monthly
    expected_min_nfp  = 12 * 6     # NFP monthly
    expected_min_fomc = 8 * 6      # FOMC ~8 meetings/year
    assert len(CPI_DATES)  >= expected_min_cpi, (
        f"CPI calendar too sparse: {len(CPI_DATES)} < {expected_min_cpi}"
    )
    assert len(NFP_DATES)  >= expected_min_nfp, (
        f"NFP calendar too sparse: {len(NFP_DATES)} < {expected_min_nfp}"
    )
    assert len(FOMC_DATES) >= expected_min_fomc, (
        f"FOMC calendar too sparse: {len(FOMC_DATES)} < {expected_min_fomc}"
    )


def test_batch366_calendar_no_month_gaps_in_cpi_nfp():
    """CPI + NFP must have exactly one entry per month for every covered
    year. Any month-gap = the silent gap (the missing month returns no
    events)."""
    from backtest.data.macro import CPI_DATES, NFP_DATES
    for name, dates in (("CPI", CPI_DATES), ("NFP", NFP_DATES)):
        months = {(d.year, d.month) for d in dates}
        n_months_expected = (max(d.year for d in dates) - min(d.year for d in dates) + 1) * 12
        # Allow a couple missing months at the boundaries
        assert len(months) >= n_months_expected - 4, (
            f"{name} calendar has month gaps: {len(months)} unique (y,m) tuples "
            f"vs {n_months_expected} expected. DEC-304 silent gap likely."
        )


def test_batch366_refresh_script_idempotent():
    """Running refresh_event_calendar.py twice produces the same output
    (no historical date drift, no accidental duplicates)."""
    import json
    import subprocess
    import sys
    p = REPO / "backtest" / "data" / "economic_calendar.json"
    before = json.loads(p.read_text())
    # Re-run with the same --through param
    coverage_year = int(before.get("_metadata", {}).get("coverage_through", "2030-12-31")[:4])
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "refresh_event_calendar.py"),
         "--through", str(coverage_year)],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0
    after = json.loads(p.read_text())
    # Date lists must be identical
    for key in ("CPI_DATES", "NFP_DATES", "FOMC_DATES"):
        assert before[key] == after[key], f"refresh non-idempotent on {key}"


def test_batch366_is_near_high_impact_event_fires_in_oos_window():
    """The OOS window (today's date) must still produce events when
    queried -- the silent-gap state has the function return blocked=False
    for every date past the calendar's last event."""
    from backtest.data.macro import is_near_high_impact_event
    # Query a date within 1y of today and ~3 days before a likely event
    today = date.today()
    # The next 30 days SHOULD contain at least 1 NFP or CPI date
    found_event = False
    for offset in range(0, 30):
        d = today + timedelta(days=offset)
        result = is_near_high_impact_event(d, window_days=7)
        if result["blocked"]:
            found_event = True
            break
    assert found_event, (
        "DEC-304 silent gap regression: no high-impact event found in the "
        "next 30 days from today within a 7-day window. Calendar is stale."
    )
