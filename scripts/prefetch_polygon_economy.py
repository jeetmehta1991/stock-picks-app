"""scripts/prefetch_polygon_economy.py - Polygon Economy endpoints prefetch.

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08.

Probe-confirmed working (3 endpoints):
  /fed/v1/inflation              -> date, cpi
  /fed/v1/inflation-expectations -> date, model_1_year/5/10/30
  /fed/v1/treasury-yields        -> date, yield_1_year/5/10

Note: /fed/v1/labor was 404 in probe; not included.

Output: data_prefetch/polygon/economy/{endpoint}.parquet
"""

from __future__ import annotations

import os
import sys
import time
import requests
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def _load_env(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for line in path.read_text(errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()

POLYGON_KEY = os.environ.get("POLYGON_API_KEY", "")
if not POLYGON_KEY:
    print("ERROR: POLYGON_API_KEY not set")
    sys.exit(1)

CACHE_DIR = Path("data_prefetch/polygon/economy")
TIMEOUT = 30

ENDPOINTS = [
    ("inflation", "https://api.polygon.io/fed/v1/inflation"),
    ("inflation_expectations", "https://api.polygon.io/fed/v1/inflation-expectations"),
    ("treasury_yields", "https://api.polygon.io/fed/v1/treasury-yields"),
]


def fetch_paginated(url: str) -> list[dict]:
    """Polygon paginated endpoint - follow next_url cursor."""
    h = {"Authorization": f"Bearer {POLYGON_KEY}"}
    out: list[dict] = []
    next_url = url
    while next_url:
        r = requests.get(next_url, headers=h, params={"limit": 50000},
                         timeout=TIMEOUT)
        if r.status_code != 200:
            print(f"    HTTP {r.status_code}: {r.text[:120]}")
            break
        data = r.json()
        results = data.get("results", []) or []
        out.extend(results)
        next_url = data.get("next_url")
        time.sleep(0.1)
    return out


def main() -> int:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    print("=== Polygon Economy prefetch ===")
    print(f"Output: {CACHE_DIR}")
    print()
    ok = 0
    for label, url in ENDPOINTS:
        print(f"  Fetching {label} ... ", end="", flush=True)
        try:
            rows = fetch_paginated(url)
            if not rows:
                print("EMPTY")
                continue
            df = pd.DataFrame(rows)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
            out = CACHE_DIR / f"{label}.parquet"
            df.to_parquet(out, index=False)
            print(f"OK {len(df)} rows -> {out.name}")
            ok += 1
        except Exception as e:
            print(f"ERROR {e}")
    print(f"\nEconomy prefetch: {ok}/{len(ENDPOINTS)} succeeded")
    return 0 if ok > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
