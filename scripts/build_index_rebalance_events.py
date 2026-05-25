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
OUT_PATH = REPO / "data_prefetch" / "derived" / "index_rebalance_events.parquet"


def main():
    if not T1A_CSV.exists():
        print(f"ERROR: {T1A_CSV} missing")
        sys.exit(1)
    df = pd.read_csv(T1A_CSV, comment="#")
    # Schema: Symbol, Company, Sector, added_date, removed_date
    required = ["Symbol", "added_date", "removed_date"]
    for col in required:
        if col not in df.columns:
            print(f"ERROR: T1a CSV missing required column {col!r}")
            sys.exit(1)
    events = []
    for _, row in df.iterrows():
        sym = row["Symbol"]
        added = row.get("added_date")
        removed = row.get("removed_date")
        # Skip rows with no usable event dates (pre-2020 baseline membership)
        if pd.notna(added):
            d = pd.to_datetime(added, errors="coerce").date()
            if pd.notna(d) and str(d) != "NaT":
                events.append({
                    "ticker":         sym,
                    "event_date":     d,
                    "event_type":     "s&p_add",
                    "announce_date":  d,
                    "effective_date": d,
                })
        if pd.notna(removed):
            d = pd.to_datetime(removed, errors="coerce").date()
            if pd.notna(d) and str(d) != "NaT":
                events.append({
                    "ticker":         sym,
                    "event_date":     d,
                    "event_type":     "s&p_drop",
                    "announce_date":  d,
                    "effective_date": d,
                })
    if not events:
        print("ERROR: no events extracted from T1a CSV")
        sys.exit(1)
    out_df = pd.DataFrame(events).sort_values(["ticker", "event_date"]).reset_index(drop=True)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_parquet(OUT_PATH, index=False)
    print(f"Wrote {OUT_PATH.relative_to(REPO)} ({len(out_df)} events)")
    print(f"  s&p_add:  {(out_df['event_type'] == 's&p_add').sum()}")
    print(f"  s&p_drop: {(out_df['event_type'] == 's&p_drop').sum()}")
    print(f"  date range: {out_df['event_date'].min()} -> {out_df['event_date'].max()}")


if __name__ == "__main__":
    main()
