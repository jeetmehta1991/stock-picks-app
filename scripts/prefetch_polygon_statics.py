"""
scripts/prefetch_polygon_statics.py — Polygon Stocks Starter small static lookups.

Source of truth (per CHECKLIST #77): API_ENDPOINT_INVENTORY.md table 1 (Polygon
Stocks Starter), tagged "NEW - small static, cache once". These are static
reference tables that change rarely; we fetch them once per release.

Endpoints (Batch 172 / Phase B1 - owner directive 2026-05-15 "prefetch
everything irrespective of use"):
  - /v3/reference/tickers/types         -> data_prefetch/polygon/static/tickers_types.parquet
  - /v3/reference/conditions            -> data_prefetch/polygon/static/conditions.parquet
  - /v3/reference/exchanges             -> data_prefetch/polygon/static/exchanges.parquet
  - /v1/marketstatus/upcoming           -> data_prefetch/polygon/static/marketstatus_upcoming.parquet
  - /v3/reference/tickers?market=indices -> data_prefetch/polygon/static/tickers_indices.parquet
  - /v3/reference/tickers?market=fx      -> data_prefetch/polygon/static/tickers_fx.parquet

Stage 3+ snapshots (one-time capture per owner directive):
  - /v1/marketstatus/now                -> data_prefetch/polygon/static/marketstatus_now.parquet
  - /v2/snapshot/locale/us/markets/stocks/tickers  -> .../snapshot_all.parquet
  - /v2/snapshot/locale/us/markets/stocks/{direction} (gainers/losers) -> .../snapshot_movers_*.parquet

Run from laptop:
  python scripts/prefetch_polygon_statics.py
"""
from __future__ import annotations

import os
import sys
import time
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
CACHE = Path("data_prefetch/polygon/static")
CACHE.mkdir(parents=True, exist_ok=True)
RATE_LIMIT_SLEEP = 0.05
TIMEOUT = 30


def fetch_json(url: str, params: dict | None = None) -> dict:
    p = dict(params or {})
    p["apiKey"] = POLYGON_KEY
    r = requests.get(url, params=p, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def fetch_paginated(url: str, params: dict | None = None) -> list[dict]:
    out: list[dict] = []
    next_url = url
    next_params = dict(params or {})
    pages = 0
    while next_url and pages < 200:
        data = fetch_json(next_url, next_params)
        rows = data.get("results") or data.get("tickers") or []
        if isinstance(rows, dict):
            rows = [rows]
        out.extend(rows)
        nu = data.get("next_url")
        if nu:
            next_url = nu
            next_params = {}
        else:
            next_url = None
        pages += 1
        time.sleep(RATE_LIMIT_SLEEP)
    return out


def write(name: str, rows: list[dict], note: str = "") -> int:
    path = CACHE / f"{name}.parquet"
    if not rows:
        df = pd.DataFrame()
    else:
        df = pd.DataFrame(rows)
    df.to_parquet(path, compression="snappy", index=False)
    print(f"  {name:35s} -> {len(df):>6} rows  {note}")
    return len(df)


def main() -> int:
    print(f"Polygon small statics -> {CACHE}")

    # Static tier-1 lookups
    write("tickers_types",
          fetch_json(f"{BASE}/v3/reference/tickers/types").get("results", []),
          "asset class/locale lookup")
    write("conditions",
          fetch_paginated(f"{BASE}/v3/reference/conditions", {"limit": 1000}),
          "trade/quote condition codes")
    write("exchanges",
          fetch_json(f"{BASE}/v3/reference/exchanges").get("results", []),
          "exchange MIC + acronym lookup")
    write("marketstatus_upcoming",
          fetch_json(f"{BASE}/v1/marketstatus/upcoming"),
          "upcoming market holidays")

    # Ticker-reference by market (paginated)
    write("tickers_indices",
          fetch_paginated(f"{BASE}/v3/reference/tickers",
                          {"market": "indices", "limit": 1000, "active": "true"}),
          "indices ticker catalog")
    write("tickers_fx",
          fetch_paginated(f"{BASE}/v3/reference/tickers",
                          {"market": "fx", "limit": 1000, "active": "true"}),
          "FX ticker catalog")

    # Stage 3+ daily snapshots - owner directive 2026-05-15 "prefetch everything"
    # captures one snapshot today (live data; serves as audit baseline).
    try:
        write("marketstatus_now",
              fetch_json(f"{BASE}/v1/marketstatus/now"),
              "live market status (1-time capture)")
    except Exception as e:
        print(f"  marketstatus_now -> SKIPPED: {e}")
    try:
        snap = fetch_json(f"{BASE}/v2/snapshot/locale/us/markets/stocks/tickers").get("tickers", [])
        write("snapshot_all", snap, "snapshot all (1-time)")
    except Exception as e:
        print(f"  snapshot_all -> SKIPPED: {e}")
    for direction in ("gainers", "losers"):
        try:
            rows = fetch_json(
                f"{BASE}/v2/snapshot/locale/us/markets/stocks/{direction}"
            ).get("tickers", [])
            write(f"snapshot_movers_{direction}", rows, f"top {direction} (1-time)")
        except Exception as e:
            print(f"  snapshot_movers_{direction} -> SKIPPED: {e}")

    print("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
