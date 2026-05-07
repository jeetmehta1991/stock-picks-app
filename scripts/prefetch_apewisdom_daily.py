"""
scripts/prefetch_apewisdom_daily.py — Cumulative daily Apewisdom prefetcher (DEC-592 Pass 53).

Apewisdom API returns top trending tickers for the CURRENT day only — no historical
query. This prefetcher runs once per day (cron-driven) and APPENDS the current
snapshot to data_prefetch/apewisdom/global.parquet (forward-only accumulation).

Per DEC-592 (Pass 53 owner-approved 2026-05-06 evening Q-followup b):
  - Append-only: never overwrites existing rows
  - Schema: [rank, ticker, name, mentions, upvotes, rank_24h_ago,
            mentions_24h_ago, snapshot_date]
  - snapshot_date partition key
  - Forward-only history; 2026-05-05 onward (no Stage-2 retroactive backfill;
    Apewisdom doesn't expose historical API)

Run modes:
  python scripts/prefetch_apewisdom_daily.py            # cron: append today
  python scripts/prefetch_apewisdom_daily.py --dry-run  # validation; no write

GitHub Actions: .github/workflows/refresh_apewisdom.yml runs daily at 09:00 UTC.
"""

import argparse
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import requests

CACHE = Path("data_prefetch/apewisdom/global.parquet")
URL = "https://apewisdom.io/api/v1.0/filter/all-stocks"
TIMEOUT = 30
MAX_RANK = 1110  # Apewisdom returns up to ~1110 trending tickers


def fetch_apewisdom_snapshot() -> pd.DataFrame:
    """Fetch current Apewisdom top-trending snapshot. Returns flat DataFrame."""
    rows = []
    page = 1
    while True:
        try:
            r = requests.get(f"{URL}/page/{page}", timeout=TIMEOUT)
        except requests.RequestException as e:
            print(f"  Page {page} fetch failed: {e}")
            break
        if r.status_code != 200:
            print(f"  Page {page} HTTP {r.status_code}")
            break
        data = r.json()
        page_results = data.get("results", []) or []
        if not page_results:
            break
        rows.extend(page_results)
        # Apewisdom paginates ~50/page; stop when we have >= MAX_RANK
        if len(rows) >= MAX_RANK or len(page_results) < 50:
            break
        page += 1
        if page > 25:  # safety
            break

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    expected_cols = ["rank", "ticker", "name", "mentions", "upvotes",
                     "rank_24h_ago", "mentions_24h_ago"]
    for c in expected_cols:
        if c not in df.columns:
            df[c] = None
    df = df[expected_cols].copy()
    df["snapshot_date"] = str(date.today())

    # Coerce numeric cols
    for c in ("rank", "mentions", "upvotes", "rank_24h_ago"):
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    df["mentions_24h_ago"] = pd.to_numeric(df["mentions_24h_ago"], errors="coerce")

    return df


def append_snapshot(df_new: pd.DataFrame, dry_run: bool = False) -> int:
    """Append snapshot to cumulative parquet; idempotent (skips if today already cached)."""
    today_str = str(date.today())

    if CACHE.exists():
        existing = pd.read_parquet(CACHE)
        if "snapshot_date" in existing.columns:
            already = (existing["snapshot_date"].astype(str) == today_str).any()
            if already:
                print(f"  Snapshot for {today_str} already cached; skipping append.")
                return 0
        merged = pd.concat([existing, df_new], ignore_index=True)
    else:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        merged = df_new

    if dry_run:
        print(f"  DRY-RUN: would append {len(df_new)} rows for {today_str}; "
              f"merged total = {len(merged)}")
        return len(df_new)

    merged.to_parquet(CACHE, index=False)
    print(f"  Appended {len(df_new)} rows for {today_str}; merged total = {len(merged)}")
    return len(df_new)


def main():
    ap = argparse.ArgumentParser(description="Apewisdom cumulative daily prefetcher")
    ap.add_argument("--dry-run", action="store_true", help="Fetch + validate, no write")
    args = ap.parse_args()

    print(f"=== Apewisdom Daily Prefetcher ({date.today()}) ===")
    df = fetch_apewisdom_snapshot()
    if df.empty:
        print("ERROR: snapshot empty (API rate-limit or down)")
        sys.exit(1)
    print(f"  Fetched {len(df)} rows; top: rank={df.iloc[0]['rank']} "
          f"ticker={df.iloc[0]['ticker']} mentions={df.iloc[0]['mentions']}")

    appended = append_snapshot(df, dry_run=args.dry_run)
    print(f"  Done. Appended: {appended}")


if __name__ == "__main__":
    main()
