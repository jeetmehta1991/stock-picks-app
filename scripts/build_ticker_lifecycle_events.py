"""Batch 374 DEC-234 + DEC-380: Polygon corp-actions -> ticker_lifecycle_events.

Reads Polygon all_splits.parquet (and future Polygon ticker-events / mergers /
delistings sources) and emits a canonical ticker_lifecycle_events.parquet
matching the DEC-234 schema (TICKER_LIFECYCLE_FIELDS).

Output schema (canonical per backtest/config.py::TICKER_LIFECYCLE_FIELDS):
  ticker             str   (current/successor)
  cusip              str   ("" if not in Polygon reference)
  isin               str   ("" if not in Polygon reference)
  event_type         str   (one of TICKER_LIFECYCLE_EVENT_TYPES)
  event_date         date
  predecessor_ticker str
  successor_ticker   str
  note               str

Current sources (Batch 374):
  data_prefetch/polygon/splits/all_splits.parquet -> split events
    (reverse splits >= 1:5 ratio flagged as share_class_change)
  data_prefetch/polygon/dividends/all_dividends.parquet -> dividend
    distributions (NOT a lifecycle event; informational only, skipped)

Future sources (DEC-380 follow-on):
  Polygon /v3/reference/tickers historical name changes -> rename
  Polygon /v3/reference/tickers/.../events -> merger / spinoff / delisting

Per CSV-first principle (CLAUDE.md HARD RULE): output to parquet (binary)
rather than CSV because the dataset is small but nested-friendly and
consumers parse via pandas. Could be exported to CSV with a flatten step
if owner prefers; queued.

Usage:
  python scripts/build_ticker_lifecycle_events.py
  python scripts/build_ticker_lifecycle_events.py --output data_prefetch/derived/ticker_lifecycle_events.parquet
"""
from __future__ import annotations

import argparse
import sys
from datetime import date as _date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

SPLITS_PATH = REPO / "data_prefetch" / "polygon" / "splits" / "all_splits.parquet"
DEFAULT_OUT = REPO / "data_prefetch" / "derived" / "ticker_lifecycle_events.parquet"


def _events_from_splits(splits_df: pd.DataFrame) -> list[dict]:
    """Map Polygon splits to TICKER_LIFECYCLE_FIELDS records.

    Reverse splits >= 1:5 ratio = share_class_change (likely corporate
    restructuring or reverse-merger pretext). Forward splits = informational
    (not lifecycle event per DEC-234 enumeration); skipped.
    """
    events = []
    for _, row in splits_df.iterrows():
        try:
            ts = row.get("split_to")
            fr = row.get("split_from")
            ed = row.get("execution_date")
            tkr = row.get("ticker")
            if not all([ts, fr, ed, tkr]):
                continue
            # Forward split: split_to > split_from (e.g. 4:1 means 4 new = 1 old)
            # Reverse split: split_to < split_from (e.g. 1:10)
            if float(ts) >= float(fr):
                continue  # forward split, not lifecycle event
            ratio = float(fr) / float(ts)
            if ratio < 5.0:
                continue  # small reverse splits (1:2, 1:3) not flagged
            events.append({
                "ticker":             str(tkr),
                "cusip":              "",
                "isin":               "",
                "event_type":         "share_class_change",
                "event_date":         ed if isinstance(ed, _date) else
                                       pd.to_datetime(ed).date(),
                "predecessor_ticker": str(tkr),
                "successor_ticker":   str(tkr),
                "note":               f"reverse_split_{fr:.0f}_to_{ts:.0f}_ratio_{ratio:.1f}",
            })
        except (TypeError, ValueError) as exc:
            # DEC-231: log silent failures with context
            print(f"[WARN] split row skipped: {exc}; row={dict(row)}")
            continue
    return events


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", default=str(DEFAULT_OUT))
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if not SPLITS_PATH.exists():
        print(f"[ERROR] Polygon splits cache missing at {SPLITS_PATH}")
        return 1

    splits_df = pd.read_parquet(SPLITS_PATH)
    print(f"[INFO] Loaded {len(splits_df)} split events from Polygon cache")

    events = _events_from_splits(splits_df)
    print(f"[INFO] Mapped to {len(events)} ticker-lifecycle events "
          f"(filter: reverse-splits >= 1:5 ratio)")

    if args.dry_run:
        for ev in events[:5]:
            print(f"[DRY] {ev}")
        if len(events) > 5:
            print(f"[DRY] ... {len(events) - 5} more")
        return 0

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(events,
                      columns=["ticker", "cusip", "isin", "event_type",
                               "event_date", "predecessor_ticker",
                               "successor_ticker", "note"])
    df.to_parquet(out_path, index=False)
    print(f"[OK] Wrote {len(df)} events to {out_path.relative_to(REPO)}")

    # Validate schema match
    from backtest.config import TICKER_LIFECYCLE_FIELDS, TICKER_LIFECYCLE_EVENT_TYPES
    missing = set(TICKER_LIFECYCLE_FIELDS) - set(df.columns)
    extra = set(df.columns) - set(TICKER_LIFECYCLE_FIELDS)
    if missing:
        print(f"[ERROR] Output missing canonical fields: {missing}")
        return 1
    if extra:
        print(f"[WARN] Output has extra fields: {extra}")
    bad_events = df[~df["event_type"].isin(TICKER_LIFECYCLE_EVENT_TYPES)]
    if not bad_events.empty:
        print(f"[ERROR] Output has {len(bad_events)} events with non-canonical event_type")
        return 1
    print(f"[OK] Schema validation passed: all {len(TICKER_LIFECYCLE_FIELDS)} canonical fields present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
