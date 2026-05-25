"""Batch 325 (2026-05-25): build index_rebalance_events.parquet from
existing universe CSVs.

Unblocks 4 quiet strategies:
  - post_inclusion_drift_long (Petajisto 2011)
  - post_inclusion_reversal_short (Beneish-Whaley 1996)
  - post_deletion_drift_short (Chen-Noronha-Singal 2004)
  - pre_rebalance_long (Cai-Houge 2008)

Source: Tier 1A B++ CSV (DEC-477) which already has added_date /
removed_date per row from the owner-approved one-time Wikipedia scrape
exception (L88 exception scope, see CLAUDE.md). This script reshapes
those columns into the schema expected by index_rebalance._load_events.

Schema (per backtest/signals/index_rebalance.py):
  ticker          str
  event_date      date
  event_type      str   (s&p_add | s&p_drop | russell_add | russell_drop | ndx_add | ndx_drop)
  announce_date   date  (= event_date when actual announce date unknown)
  effective_date  date  (= event_date - same source as announce_date)

For Stage 2 scope, we emit S&P 500 events from the T1a CSV. Russell +
Nasdaq-100 events deferred to Sprint 5 (DEC-380 Polygon corp-actions
ingestion). NDX historical events available from T1c CSV but lower
priority - the S&P add/drop signal carries most of the documented alpha.

Usage:
  python scripts/build_index_rebalance_events.py
  -> writes data_prefetch/derived/index_rebalance_events.parquet
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
T1A_CSV = REPO / "Backtesting universe" / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"
T1C_CSV = REPO / "Backtesting universe" / "Tier 1C Universe_NASDAQ-100 Tickers_Jan 2020 to May 2026.csv"
OUT_PATH = REPO / "data_prefetch" / "derived" / "index_rebalance_events.parquet"


def _extract_events_from_b_plus_csv(csv_path: Path, add_type: str, drop_type: str) -> list:
    """Generic B++ schema (Symbol, added_date, removed_date) -> event rows.
    Same logic for T1a (S&P 500) and T1c (NDX) per their shared schema."""
    if not csv_path.exists():
        return []
    df = pd.read_csv(csv_path, comment="#")
    required = ["Symbol", "added_date", "removed_date"]
    if not all(c in df.columns for c in required):
        return []
    events = []
    for _, row in df.iterrows():
        sym = row["Symbol"]
        added = row.get("added_date")
        removed = row.get("removed_date")
        if pd.notna(added):
            d = pd.to_datetime(added, errors="coerce").date()
            if pd.notna(d) and str(d) != "NaT":
                events.append({
                    "ticker":         sym,
                    "event_date":     d,
                    "event_type":     add_type,
                    "announce_date":  d,
                    "effective_date": d,
                })
        if pd.notna(removed):
            d = pd.to_datetime(removed, errors="coerce").date()
            if pd.notna(d) and str(d) != "NaT":
                events.append({
                    "ticker":         sym,
                    "event_date":     d,
                    "event_type":     drop_type,
                    "announce_date":  d,
                    "effective_date": d,
                })
    return events


def main():
    all_events = []

    # S&P 500 events from T1a B++ CSV (owner-approved one-time Wikipedia
    # scrape per L88 exception scope; CLAUDE.md universe management).
    sp_events = _extract_events_from_b_plus_csv(T1A_CSV, "s&p_add", "s&p_drop")
    all_events.extend(sp_events)
    print(f"S&P 500: {len(sp_events)} events from {T1A_CSV.name}")

    # Batch 341 (2026-05-25 owner directive "Execute B C12" item B#4):
    # NDX events from T1c B++ CSV. Same scrape exception scope - the
    # added_date / removed_date columns in T1c capture historical NDX
    # add/drop events 2020-2026. Cai-Houge 2008 + index-rebalance
    # literature: NDX events have similar drift signatures to S&P 500.
    ndx_events = _extract_events_from_b_plus_csv(T1C_CSV, "ndx_add", "ndx_drop")
    all_events.extend(ndx_events)
    print(f"NDX:     {len(ndx_events)} events from {T1C_CSV.name}")

    # Russell 1000 / 2000 reconstitution: Sprint 5 (DEC-380) deliverable
    # for Polygon corp-actions / FTSE Russell API integration. Not in
    # Batch 341 scope - the public Russell membership CSV doesn't ship
    # in this repo and the owner-approved Wikipedia-exception scope per
    # L88 is for index assembly only, not for ongoing reconstitution
    # capture. Russell reconstitution events will be added via Sprint 5
    # FTSE Russell official source per DEC-380.
    print(f"Russell: 0 events (deferred to Sprint 5 / DEC-380 FTSE feed)")

    if not all_events:
        print("ERROR: no events extracted from any source")
        sys.exit(1)
    out_df = pd.DataFrame(all_events).sort_values(["ticker", "event_date"]).reset_index(drop=True)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_parquet(OUT_PATH, index=False)
    print(f"\nWrote {OUT_PATH.relative_to(REPO)} ({len(out_df)} events total)")
    for et in sorted(out_df["event_type"].unique()):
        n = (out_df["event_type"] == et).sum()
        print(f"  {et}: {n}")
    print(f"  date range: {out_df['event_date'].min()} -> {out_df['event_date'].max()}")


if __name__ == "__main__":
    main()
