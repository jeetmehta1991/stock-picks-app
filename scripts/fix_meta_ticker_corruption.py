"""scripts/fix_meta_ticker_corruption.py - Batch 275 META data fix.

The META ticker was assigned to Meta Materials Inc from 2021-06-30 to
2022-06-08. From 2022-06-09 onward, the ticker was reassigned to Meta
Platforms (formerly Facebook, ticker FB). Polygon's META.parquet stitches
both companies' prices into one continuous series:
  - Before 2022-06-09: Meta Materials ($14-15 range)
  - On    2022-06-09: discontinuity (close $14.91 -> $184.00)
  - After 2022-06-09: Meta Platforms ($150+ range)

This caused a -1,219% loss on a single trade in the Stage B smoke
(cpr_narrow_momentum_short META 2022-01-04 -> 2022-06-09) because the
entry was logged at $14.77 (Meta Materials price) and exit at $194
(Meta Platforms price).

Fix (owner-approved option C, 2026-05-20):
Refetch META from Polygon with start date 2022-06-09. This drops the
Meta Materials portion of the series. Pre-2022-06-09 backtest trades on
META will then return no OHLCV - the screener will skip the ticker on
those days, which is correct (Facebook traded under FB ticker then).

Applies the fix to all 3 cache locations:
  - data_prefetch/polygon/ohlcv_daily/META.parquet
  - backtest/data/cache/polygon/ohlcv_daily/META.parquet
  - backtest/data/cache/ohlcv/META.parquet
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

POLYGON_KEY = os.environ.get("POLYGON_API_KEY", "")
if not POLYGON_KEY:
    print("ERROR: POLYGON_API_KEY not set")
    sys.exit(1)

# Meta Platforms (formerly FB) acquired the META ticker on 2022-06-09.
META_PLATFORMS_START = date(2022, 6, 9)
END_DATE = date.today()

TARGETS = [
    Path("data_prefetch/polygon/ohlcv_daily/META.parquet"),
    Path("backtest/data/cache/polygon/ohlcv_daily/META.parquet"),
    Path("backtest/data/cache/ohlcv/META.parquet"),
]


def fetch_meta_polygon(start: date, end: date) -> pd.DataFrame:
    """Fetch META daily aggregates from Polygon for [start, end]."""
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/META/range/1/day/"
        f"{start.isoformat()}/{end.isoformat()}"
        f"?adjusted=true&sort=asc&limit=50000&apiKey={POLYGON_KEY}"
    )
    print(f"  GET {url.replace(POLYGON_KEY, '<KEY>')}")
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    payload = r.json()
    results = payload.get("results", [])
    if not results:
        raise RuntimeError(f"No results from Polygon for META {start}-{end}")
    df = pd.DataFrame(results)
    # Polygon returns: {t: timestamp_ms, o, h, l, c, v, vw, n}
    df["dt"] = pd.to_datetime(df["t"], unit="ms")
    df["date"] = df["dt"].dt.strftime("%Y-%m-%d")
    df["ticker"] = "META"
    df = df.rename(columns={
        "o": "open", "h": "high", "l": "low", "c": "close",
        "v": "volume", "vw": "vwap", "n": "transactions",
    })
    cols = ["ticker", "date", "open", "high", "low", "close",
            "volume", "vwap", "transactions"]
    return df[cols].copy()


def backup(path: Path) -> Path:
    """Backup existing parquet to .meta_materials_backup."""
    if not path.exists():
        return path
    bak = path.with_suffix(".parquet.meta_materials_backup")
    shutil.copy2(path, bak)
    return bak


def main():
    print("=" * 70)
    print("Batch 275: META ticker corruption fix")
    print(f"  Refetching META from Polygon for {META_PLATFORMS_START} to {END_DATE}")
    print("=" * 70)

    # Step 1: sanity check - read one existing file to confirm corruption
    sample_path = TARGETS[0]
    if sample_path.exists():
        sample = pd.read_parquet(sample_path)
        sample["dt"] = pd.to_datetime(sample["date"])
        pre = sample[sample["dt"] < pd.Timestamp(META_PLATFORMS_START)]
        post = sample[sample["dt"] >= pd.Timestamp(META_PLATFORMS_START)]
        print(f"\nCurrent {sample_path}:")
        print(f"  Total rows: {len(sample)}")
        print(f"  Pre-2022-06-09 (Meta Materials corruption): {len(pre)} rows")
        print(f"  Post-2022-06-09 (Meta Platforms valid): {len(post)} rows")
        if not pre.empty:
            print(f"  Pre-rename close range: ${pre['close'].min():.2f} - ${pre['close'].max():.2f}")
        if not post.empty:
            print(f"  Post-rename close range: ${post['close'].min():.2f} - ${post['close'].max():.2f}")

    # Step 2: fetch fresh META post-rename data
    print(f"\nFetching META from Polygon...")
    fresh = fetch_meta_polygon(META_PLATFORMS_START, END_DATE)
    print(f"  Got {len(fresh)} rows; close range: "
          f"${fresh['close'].min():.2f} - ${fresh['close'].max():.2f}")
    print(f"  Date range: {fresh['date'].iloc[0]} to {fresh['date'].iloc[-1]}")

    # Step 3: write to all target locations (with backup)
    for path in TARGETS:
        if not path.parent.exists():
            print(f"  Skipping {path} (parent dir missing)")
            continue
        bak = backup(path) if path.exists() else None
        if bak:
            print(f"\n  {path}: backup -> {bak.name}")
        else:
            print(f"\n  {path}: creating new (no existing file)")
        # Match the column schema of the original file if it existed
        if path.exists():
            existing = pd.read_parquet(path)
            existing_cols = list(existing.columns)
            out = fresh.copy()
            for col in existing_cols:
                if col not in out.columns:
                    out[col] = None
            out = out[existing_cols]
        else:
            out = fresh
        out.to_parquet(path, index=False)
        print(f"  Wrote {path} - {len(out)} rows")

    print()
    print("=" * 70)
    print("Done. META.parquet now has Meta Platforms data only (>= 2022-06-09).")
    print("Pre-2022-06-09 META queries will return empty -> screener skips.")
    print("=" * 70)


if __name__ == "__main__":
    main()
