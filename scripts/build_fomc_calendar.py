"""Batch 342 (2026-05-25 owner directive "Execute B C12" item B#5): build
FOMC calendar parquet from the public Federal Reserve published meeting
schedule.

Output: data_prefetch/fred/fomc_calendar.parquet

Unblocks:
 - strat_pre_fomc_long_sleeve (Lucca-Moench 2015 JF +50bps pre-FOMC drift)
 - strat_pre_fomc_quality_momentum_long (DEC-422 add-on)

Producer: backtest/signals/macro_events.py::_load_fomc_calendar reads
the parquet. Without the file, returns empty DataFrame -> the producer
yields no pre-FOMC keys -> the 2 strategies fire 0 trades.

Schema (consumed by backtest/signals/macro_events.py::_load_fomc_calendar):
  date             date    (announcement date; second day of each FOMC
                            meeting; what Lucca-Moench 2015 references
                            for the +50bps pre-FOMC drift window)
  announce_time    str     ("14:00 ET" canonical; informational)
  meeting_type     str     ("scheduled" | "emergency")

Source: Federal Reserve press releases, FOMC calendar page
https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
(public domain). Data hardcoded below from the Fed's 2020-2026
published schedule.

Owner-approved one-time data assembly under CLAUDE.md L88 exception
scope for ONE-TIME historical CSV inputs.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
OUT_PATH = REPO / "data_prefetch" / "fred" / "fomc_calendar.parquet"


# Federal Reserve FOMC meeting schedule 2020-2026.
# "meeting_date" = second day of each scheduled meeting (the announcement
# day; what Lucca-Moench 2015 references for the +50bps pre-FOMC drift
# window).
# Emergency meetings (March 2020 COVID rate cuts) flagged as meeting_type
# "emergency"; pre-FOMC long sleeve only fires before SCHEDULED meetings
# per the canonical Lucca-Moench methodology.
_FOMC_MEETINGS = [
    # 2020
    (date(2020, 1, 29),  "scheduled"),
    (date(2020, 3, 3),   "emergency"),  # 50bp emergency cut
    (date(2020, 3, 15),  "emergency"),  # 100bp emergency cut + ZLB
    (date(2020, 4, 29),  "scheduled"),
    (date(2020, 6, 10),  "scheduled"),
    (date(2020, 7, 29),  "scheduled"),
    (date(2020, 9, 16),  "scheduled"),
    (date(2020, 11, 5),  "scheduled"),
    (date(2020, 12, 16), "scheduled"),
    # 2021
    (date(2021, 1, 27),  "scheduled"),
    (date(2021, 3, 17),  "scheduled"),
    (date(2021, 4, 28),  "scheduled"),
    (date(2021, 6, 16),  "scheduled"),
    (date(2021, 7, 28),  "scheduled"),
    (date(2021, 9, 22),  "scheduled"),
    (date(2021, 11, 3),  "scheduled"),
    (date(2021, 12, 15), "scheduled"),
    # 2022
    (date(2022, 1, 26),  "scheduled"),
    (date(2022, 3, 16),  "scheduled"),
    (date(2022, 5, 4),   "scheduled"),
    (date(2022, 6, 15),  "scheduled"),
    (date(2022, 7, 27),  "scheduled"),
    (date(2022, 9, 21),  "scheduled"),
    (date(2022, 11, 2),  "scheduled"),
    (date(2022, 12, 14), "scheduled"),
    # 2023
    (date(2023, 2, 1),   "scheduled"),
    (date(2023, 3, 22),  "scheduled"),
    (date(2023, 5, 3),   "scheduled"),
    (date(2023, 6, 14),  "scheduled"),
    (date(2023, 7, 26),  "scheduled"),
    (date(2023, 9, 20),  "scheduled"),
    (date(2023, 11, 1),  "scheduled"),
    (date(2023, 12, 13), "scheduled"),
    # 2024
    (date(2024, 1, 31),  "scheduled"),
    (date(2024, 3, 20),  "scheduled"),
    (date(2024, 5, 1),   "scheduled"),
    (date(2024, 6, 12),  "scheduled"),
    (date(2024, 7, 31),  "scheduled"),
    (date(2024, 9, 18),  "scheduled"),
    (date(2024, 11, 7),  "scheduled"),
    (date(2024, 12, 18), "scheduled"),
    # 2025
    (date(2025, 1, 29),  "scheduled"),
    (date(2025, 3, 19),  "scheduled"),
    (date(2025, 5, 7),   "scheduled"),
    (date(2025, 6, 18),  "scheduled"),
    (date(2025, 7, 30),  "scheduled"),
    (date(2025, 9, 17),  "scheduled"),
    (date(2025, 10, 29), "scheduled"),
    (date(2025, 12, 10), "scheduled"),
    # 2026
    (date(2026, 1, 28),  "scheduled"),
    (date(2026, 3, 18),  "scheduled"),
    (date(2026, 4, 29),  "scheduled"),
    (date(2026, 6, 17),  "scheduled"),
    (date(2026, 7, 29),  "scheduled"),
    (date(2026, 9, 16),  "scheduled"),
    (date(2026, 11, 4),  "scheduled"),
    (date(2026, 12, 16), "scheduled"),
]


def main():
    rows = [
        {"date": d, "announce_time": "14:00 ET", "meeting_type": t}
        for d, t in _FOMC_MEETINGS
    ]
    df = pd.DataFrame(rows)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PATH, index=False)
    n_scheduled = (df["meeting_type"] == "scheduled").sum()
    n_emergency = (df["meeting_type"] == "emergency").sum()
    print(f"Wrote {OUT_PATH.relative_to(REPO)} ({len(df)} FOMC meetings)")
    print(f"  scheduled: {n_scheduled}")
    print(f"  emergency: {n_emergency}")
    print(f"  date range: {df['date'].min()} -> {df['date'].max()}")


if __name__ == "__main__":
    main()
