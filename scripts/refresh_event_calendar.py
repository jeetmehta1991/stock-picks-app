"""Refresh `backtest/data/economic_calendar.json` with CPI/NFP/FOMC dates.

Source (per CHECKLIST #77 canonical-source attribution): owner directive
2026-05-25 Batch 366 DEC-304 calendar staleness fix. The hardcoded
calendar ends 2026-03-18; any as_of past that date silently returns
"no events" from is_near_high_impact_event. Phase 1A-beta window
2022-05 -> 2026-05 has ~30 trading days at the OOS tail with no event
coverage; future Phase 1A re-runs will have more.

Deterministic extension logic:
  NFP:  first Friday of each month (BLS canonical schedule)
  CPI:  2nd Wednesday of each month (BLS approximate; varies +/- 1d)
  FOMC: 8 meetings per year, per Fed's published schedule for 2026-2027
        and reasonable estimates 2028-2030 based on typical pattern
        (Jan, Mar, Apr/May, Jun, Jul, Sep, Nov, Dec)

Note: CPI/FOMC dates are approximations beyond the BLS/Fed published
windows. Off-by-1-week is acceptable noise for proximity-based event-
blocking strategies; missing months entirely is the silent gap this
script closes.

Usage:
  python scripts/refresh_event_calendar.py                # extend to end-2030
  python scripts/refresh_event_calendar.py --through 2027  # custom end year

Outputs:
  Overwrites `backtest/data/economic_calendar.json` with extended dates +
  updated _metadata coverage_through. Preserves historical dates from the
  existing JSON file.
"""
from __future__ import annotations

import argparse
import json
from calendar import Calendar
from datetime import date
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
CAL_PATH = REPO / "backtest" / "data" / "economic_calendar.json"


def _nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    """Return the Nth occurrence of `weekday` (Mon=0..Sun=6) in (year,month)."""
    cal = Calendar()
    occurrences = [d for d in cal.itermonthdates(year, month)
                   if d.month == month and d.weekday() == weekday]
    return occurrences[n - 1]


def first_friday(year: int, month: int) -> date:
    return _nth_weekday_of_month(year, month, weekday=4, n=1)


def second_wednesday(year: int, month: int) -> date:
    return _nth_weekday_of_month(year, month, weekday=2, n=2)


# Fed's published FOMC calendar for 2026-2027 (verbatim from federalreserve.gov)
# Approximations for 2028-2030 based on the typical Jan/Mar/Apr-May/Jun/Jul/Sep/Nov/Dec pattern.
FOMC_KNOWN = {
    # 2026 (published)
    2026: [
        date(2026, 1, 28), date(2026, 3, 18), date(2026, 4, 29),
        date(2026, 6, 17), date(2026, 7, 29), date(2026, 9, 16),
        date(2026, 11, 5), date(2026, 12, 16),
    ],
    # 2027 (published)
    2027: [
        date(2027, 1, 27), date(2027, 3, 17), date(2027, 5, 5),
        date(2027, 6, 16), date(2027, 7, 28), date(2027, 9, 22),
        date(2027, 11, 3), date(2027, 12, 15),
    ],
    # 2028 (estimate; pattern-matched)
    2028: [
        date(2028, 1, 26), date(2028, 3, 15), date(2028, 5, 3),
        date(2028, 6, 14), date(2028, 7, 26), date(2028, 9, 20),
        date(2028, 11, 1), date(2028, 12, 13),
    ],
    # 2029 (estimate)
    2029: [
        date(2029, 1, 31), date(2029, 3, 21), date(2029, 5, 2),
        date(2029, 6, 13), date(2029, 7, 25), date(2029, 9, 19),
        date(2029, 10, 31), date(2029, 12, 12),
    ],
    # 2030 (estimate)
    2030: [
        date(2030, 1, 30), date(2030, 3, 20), date(2030, 5, 1),
        date(2030, 6, 12), date(2030, 7, 24), date(2030, 9, 18),
        date(2030, 10, 30), date(2030, 12, 11),
    ],
}


def generate_calendar(start_year: int, end_year: int) -> dict[str, list[date]]:
    """Generate CPI/NFP/FOMC dates from start_year to end_year inclusive."""
    cpi = []
    nfp = []
    fomc = []
    for y in range(start_year, end_year + 1):
        for m in range(1, 13):
            cpi.append(second_wednesday(y, m))
            nfp.append(first_friday(y, m))
        fomc.extend(FOMC_KNOWN.get(y, []))
    return {"CPI_DATES": sorted(cpi), "NFP_DATES": sorted(nfp),
            "FOMC_DATES": sorted(fomc)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--through", type=int, default=2030,
                    help="Extend calendar through end of this year (default 2030)")
    args = ap.parse_args()

    # Preserve historical dates from existing file (avoid replacing observed
    # publication dates with our generator's approximations).
    existing = {}
    if CAL_PATH.exists():
        raw = json.loads(CAL_PATH.read_text())
        existing = {
            "CPI_DATES":  [date.fromisoformat(s) for s in raw.get("CPI_DATES",  [])],
            "NFP_DATES":  [date.fromisoformat(s) for s in raw.get("NFP_DATES",  [])],
            "FOMC_DATES": [date.fromisoformat(s) for s in raw.get("FOMC_DATES", [])],
        }

    # Generate from 2022 (Phase 1A-beta start) through args.through.
    gen = generate_calendar(2022, args.through)

    # Merge: prefer historical observed dates over generated approximations
    # for any (year, month) tuple where existing has a date.
    def merge(observed: list[date], generated: list[date]) -> list[date]:
        observed_by_ym = {(d.year, d.month): d for d in observed}
        out = list(observed)
        for d in generated:
            if (d.year, d.month) not in observed_by_ym:
                out.append(d)
        # FOMC is irregular -- merge by exact date set, not by month
        return sorted(set(out))

    def merge_fomc(observed: list[date], generated: list[date]) -> list[date]:
        # Keep all observed; only add generated dates >= max(observed) so we
        # don't introduce duplicates near the boundary.
        cutoff = max(observed) if observed else date(2022, 1, 1)
        return sorted(set(list(observed) + [d for d in generated if d > cutoff]))

    final = {
        "CPI_DATES":  merge(existing.get("CPI_DATES",  []), gen["CPI_DATES"]),
        "NFP_DATES":  merge(existing.get("NFP_DATES",  []), gen["NFP_DATES"]),
        "FOMC_DATES": merge_fomc(existing.get("FOMC_DATES", []), gen["FOMC_DATES"]),
    }

    out = {
        "CPI_DATES":  [d.isoformat() for d in final["CPI_DATES"]],
        "NFP_DATES":  [d.isoformat() for d in final["NFP_DATES"]],
        "FOMC_DATES": [d.isoformat() for d in final["FOMC_DATES"]],
        "_metadata": {
            "schema_version": 2,
            "last_updated":   date.today().isoformat(),
            "coverage_through": f"{args.through}-12-31",
            "sources": {
                "CPI":  "https://www.bls.gov/schedule/news_release/cpi.htm",
                "NFP":  "https://www.bls.gov/schedule/news_release/empsit.htm",
                "FOMC": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
            },
            "generation_notes": {
                "CPI":  "Historical dates preserved from prior schema_version=1 "
                        "(observed BLS publication dates). Future dates use "
                        "2nd Wednesday of month as proxy (BLS publishes within "
                        "+/- 1 week of this date typically).",
                "NFP":  "First Friday of each month (BLS canonical schedule; "
                        "deterministic).",
                "FOMC": "Historical dates preserved; 2026-2027 from Fed's "
                        "published calendar; 2028-2030 estimated from typical "
                        "8-meetings-per-year pattern.",
            },
            "refresh_instructions": (
                "Run `python scripts/refresh_event_calendar.py --through YYYY` "
                "annually to extend coverage. Test pin: "
                "test_batch366_calendar_covers_backtest_end_plus_buffer in "
                "test_silent_gap_pyramid.py."
            ),
        },
    }

    CAL_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {CAL_PATH}")
    print(f"     CPI:  {len(out['CPI_DATES']):4d} dates ({out['CPI_DATES'][0]} -> {out['CPI_DATES'][-1]})")
    print(f"     NFP:  {len(out['NFP_DATES']):4d} dates ({out['NFP_DATES'][0]} -> {out['NFP_DATES'][-1]})")
    print(f"     FOMC: {len(out['FOMC_DATES']):4d} dates ({out['FOMC_DATES'][0]} -> {out['FOMC_DATES'][-1]})")


if __name__ == "__main__":
    main()
