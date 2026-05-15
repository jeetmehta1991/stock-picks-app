"""
scripts/prefetch_polygon_grouped_daily.py - Polygon grouped daily aggs.

Source of truth: API_ENDPOINT_INVENTORY.md section 1 row tagged "NEW - daily
snapshot capture for liquidity ranking". Per owner directive 2026-05-15
"prefetch everything irrespective of use", we fetch every trading day's
market-wide snapshot for the backtest window.

Endpoint: /v2/aggs/grouped/locale/us/market/stocks/{YYYY-MM-DD}
Returns: all US stocks active on that day (ticker, o, h, l, c, v, vw, n).

Output: data_prefetch/polygon/grouped_daily/{YYYY-MM-DD}.parquet
Date range: 2020-01-01 to 2026-04-15 (matches backtest cache window).
Skips weekends. Polygon returns empty results on US market holidays;
empty days written as empty parquet (audit signal).
"""
from __future__ import annotations

import os
import sys
import time
from datetime import date, timedelta
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

BASE = "https://api.polygon.io"
CACHE = Path("data_prefetch/polygon/grouped_daily")
CACHE.mkdir(parents=True, exist_ok=True)
START = date(2020, 1, 1)
END = date(2026, 4, 15)
RATE_LIMIT_SLEEP = 0.05
TIMEOUT = 60


def fetch_grouped(d: date) -> list[dict] | None:
    url = f"{BASE}/v2/aggs/grouped/locale/us/market/stocks/{d.isoformat()}"
    try:
        r = requests.get(url, params={"apiKey": POLYGON_KEY, "adjusted": "true"},
                         timeout=TIMEOUT)
    except Exception as e:
        print(f"  {d}: network error {e}")
        return None
    if r.status_code != 200:
        return None
    return r.json().get("results", []) or []


def main() -> int:
    print(f"Polygon grouped daily aggs -> {CACHE}")
    print(f"  range: {START} to {END}")

    cur = START
    fetched = 0
    skipped = 0
    empty = 0
    error = 0
    while cur <= END:
        if cur.weekday() >= 5:  # skip Sat/Sun
            cur += timedelta(days=1)
            continue
        path = CACHE / f"{cur.isoformat()}.parquet"
        if path.exists():
            skipped += 1
            cur += timedelta(days=1)
            continue
        rows = fetch_grouped(cur)
        if rows is None:
            error += 1
            cur += timedelta(days=1)
            time.sleep(RATE_LIMIT_SLEEP)
            continue
        if rows:
            df = pd.DataFrame(rows)
            df["date"] = cur.isoformat()
            df.to_parquet(path, compression="snappy", index=False)
            fetched += 1
        else:
            pd.DataFrame().to_parquet(path, compression="snappy", index=False)
            empty += 1
        if (fetched + empty) % 50 == 0:
            print(f"  {cur}  fetched={fetched} empty={empty} skipped={skipped} error={error}")
        cur += timedelta(days=1)
        time.sleep(RATE_LIMIT_SLEEP)

    print(f"DONE  fetched={fetched} empty={empty} skipped={skipped} error={error}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
