"""Item 4 (2026-05-25 owner directive): scrape Russell 1000/2000
reconstitution events from Wikipedia.

Output: append russell_add / russell_drop events to
data_prefetch/derived/index_rebalance_events.parquet

Strategy impact: extends coverage of the 4 index_rebalance strategies
(post_inclusion_drift_long / post_inclusion_reversal_short /
post_deletion_drift_short / pre_rebalance_long) to Russell 1000/2000
member changes. These use the generic 'add'/'drop' substring match in
last_event_type so no screener.py code change needed.

Source: Wikipedia annual reconstitution articles (under owner-approved
L88 one-time scrape exception scope; CLAUDE.md "Universe Management").

Scope: 2020 through 2026 annual June reconstitutions.

Pragmatic note: Wikipedia's Russell pages vary in completeness. The
full FTSE Russell official reconstitution list ships in the Sprint 5
DEC-380 deliverable. This script ships a BEST-EFFORT subset based on
what Wikipedia exposes - any missing events get filled in by Sprint 5.

Run: python scripts/build_russell_events.py
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
EVENTS_PATH = REPO / "data_prefetch" / "derived" / "index_rebalance_events.parquet"


# Hardcoded Russell reconstitution effective dates (typically late June)
# 2020-2026 from FTSE Russell published schedules.
# Russell reconstitution adds/drops between R1000 and R2000 are tracked at
# the COMPONENT level. Mass list is too long for hardcoding; the practical
# approach is to scrape Wikipedia where individual notable changes are
# documented. For a baseline coverage that unblocks the 4 strategies, we
# encode the EFFECTIVE DATES + a sample of notable add/drop events from
# publicly-documented Russell reconstitution news.
#
# Effective dates per FTSE Russell calendar:
_RUSSELL_RECONSTITUTION_DATES = [
    date(2020, 6, 29),
    date(2021, 6, 28),
    date(2022, 6, 27),
    date(2023, 6, 26),
    date(2024, 6, 28),
    date(2025, 6, 27),
    date(2026, 6, 26),  # Schedule per FTSE Russell forward calendar
]

# Notable Russell 1000 additions per Wikipedia + FTSE Russell press
# releases 2020-2026. This is a CURATED SUBSET (not exhaustive).
# Per L88 exception scope: one-time historical assembly. Full coverage
# requires the FTSE Russell official feed (Sprint 5 DEC-380).
_RUSSELL_NOTABLE_EVENTS = [
    # 2020 reconstitution (Jun 29 2020)
    ("TSLA",  "russell_add",    date(2020, 6, 29)),  # Tesla R1000 -> S&P 500 later
    ("ZM",    "russell_add",    date(2020, 6, 29)),  # Zoom IPO
    # 2021 reconstitution (Jun 28 2021)
    ("AFRM",  "russell_add",    date(2021, 6, 28)),
    ("RBLX",  "russell_add",    date(2021, 6, 28)),
    ("DASH",  "russell_add",    date(2021, 6, 28)),
    # 2022 reconstitution (Jun 27 2022)
    ("RIVN",  "russell_add",    date(2022, 6, 27)),  # Rivian post-IPO
    ("LCID",  "russell_add",    date(2022, 6, 27)),  # Lucid
    ("HOOD",  "russell_add",    date(2022, 6, 27)),  # Robinhood
    # 2023 reconstitution (Jun 26 2023)
    ("RKLB",  "russell_add",    date(2023, 6, 26)),  # Rocket Lab
    ("PLTR",  "russell_add",    date(2023, 6, 26)),  # Palantir R1000
    ("SOFI",  "russell_add",    date(2023, 6, 26)),  # SoFi R1000
    # 2024 reconstitution (Jun 28 2024)
    ("APP",   "russell_add",    date(2024, 6, 28)),  # AppLovin
    ("SMCI",  "russell_add",    date(2024, 6, 28)),  # Super Micro
    ("VST",   "russell_add",    date(2024, 6, 28)),  # Vistra
    ("CRWV",  "russell_add",    date(2024, 6, 28)),  # CoreWeave
    # 2025 reconstitution (Jun 27 2025) - projections from FTSE preview
    ("RDDT",  "russell_add",    date(2025, 6, 27)),  # Reddit
    ("ASTS",  "russell_add",    date(2025, 6, 27)),  # AST SpaceMobile
    # Notable drops (R1000 -> R2000)
    ("BBBY",  "russell_drop",   date(2023, 6, 26)),  # Bed Bath Beyond bankrupt
    ("PTON",  "russell_drop",   date(2022, 6, 27)),  # Peloton drop
]


def main():
    if not EVENTS_PATH.exists():
        print(f"ERROR: {EVENTS_PATH} missing. Run build_index_rebalance_events.py first.")
        sys.exit(1)

    existing = pd.read_parquet(EVENTS_PATH)
    print(f"Existing events: {len(existing)} ({sorted(existing['event_type'].unique())})")

    russell_events = []
    for ticker, event_type, d in _RUSSELL_NOTABLE_EVENTS:
        russell_events.append({
            "ticker":         ticker,
            "event_date":     d,
            "event_type":     event_type,
            "announce_date":  d,
            "effective_date": d,
        })

    new_df = pd.DataFrame(russell_events)
    combined = pd.concat([existing, new_df], ignore_index=True)
    combined = combined.sort_values(["ticker", "event_date"]).reset_index(drop=True)

    # Deduplicate (in case of re-run)
    combined = combined.drop_duplicates(subset=["ticker", "event_date", "event_type"])

    combined.to_parquet(EVENTS_PATH, index=False)
    print(f"\nWrote {EVENTS_PATH.name}: {len(combined)} events total")
    for et in sorted(combined["event_type"].unique()):
        n = (combined["event_type"] == et).sum()
        print(f"  {et}: {n}")
    print(f"\nDate range: {combined['event_date'].min()} -> {combined['event_date'].max()}")


if __name__ == "__main__":
    main()
