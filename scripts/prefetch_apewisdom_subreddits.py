"""scripts/prefetch_apewisdom_subreddits.py - subreddit-specific Apewisdom feeds.

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08; Tier H19 P2.

Probe-confirmed: /api/v1.0/filter/{filter} accepts subreddit names as
filter values. Currently we fetch only 'all-stocks'. Adding 4 specific
subreddit feeds: wallstreetbets, stocks, investing, options.

Output: data_prefetch/apewisdom/{subreddit}.parquet (snapshot at fetch time;
forward-only accumulation if cron'd)
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd
import requests

URL_BASE = "https://apewisdom.io/api/v1.0/filter"
TIMEOUT = 30
MAX_RANK = 1110

SUBREDDITS = ["wallstreetbets", "stocks", "investing", "options",
               "stockmarket", "CryptoCurrency", "Bitcoin", "SatoshiStreetBets"]


def fetch_subreddit(name: str) -> pd.DataFrame:
    rows = []
    page = 1
    while True:
        url = f"{URL_BASE}/{name}/page/{page}"
        try:
            r = requests.get(url, timeout=TIMEOUT)
        except Exception as e:
            print(f"    page {page} error: {e}")
            break
        if r.status_code != 200:
            break
        data = r.json()
        results = data.get("results", []) or []
        if not results:
            break
        rows.extend(results)
        if len(rows) >= MAX_RANK:
            break
        page += 1
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["snapshot_date"] = str(date.today())
    return df


def main() -> int:
    out_dir = Path("data_prefetch/apewisdom/subreddits")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"=== Apewisdom subreddit-specific prefetch ({len(SUBREDDITS)} feeds) ===")
    ok = 0
    for sub in SUBREDDITS:
        print(f"  {sub} ... ", end="", flush=True)
        try:
            df = fetch_subreddit(sub)
            if df.empty:
                print("EMPTY")
                continue
            out = out_dir / f"{sub.lower()}.parquet"
            df.to_parquet(out, index=False)
            print(f"OK {len(df)} rows")
            ok += 1
        except Exception as e:
            print(f"ERROR {e}")
    print(f"\nApewisdom subreddit prefetch: {ok}/{len(SUBREDDITS)} OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
