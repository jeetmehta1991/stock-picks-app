"""
scripts/prefetch_fred_metadata.py — FRED metadata endpoints (per CHECKLIST #77).

Source of truth: API_ENDPOINT_INVENTORY.md section 9 (FRED), rows tagged "NEW".
Per owner directive 2026-05-15 ("prefetch everything irrespective of use"),
this batch caches the metadata sidecar for every FRED series we already
prefetch under data_prefetch/fred/observations/, plus the static
category/release/source/tags catalog trees.

Endpoints covered (Batch 173 / Phase B2):
  Per-series (one row per series we have cached):
    /fred/series                     -> series.parquet
    /fred/series/categories          -> series_categories.parquet
    /fred/series/release             -> series_release.parquet
    /fred/series/tags                -> series_tags.parquet
    /fred/series/vintagedates        -> series_vintagedates.parquet
    /fred/series/updates             -> series_updates.parquet (global, daily)

  Static catalog (top-of-tree browse, cached once):
    /fred/category                   -> category_root.parquet
    /fred/category/children          -> category_children_<id>.parquet (root + 1-level)
    /fred/release                    -> releases.parquet (paginated all)
    /fred/source                     -> sources.parquet (paginated all)
    /fred/tags                       -> tags.parquet (paginated all)

Output: data_prefetch/fred/metadata/<name>.parquet
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

FRED_KEY = os.environ.get("FRED_API_KEY", "")
if not FRED_KEY:
    print("ERROR: FRED_API_KEY not set")
    sys.exit(1)

BASE = "https://api.stlouisfed.org/fred"
CACHE = Path("data_prefetch/fred/metadata")
CACHE.mkdir(parents=True, exist_ok=True)
OBS_DIR = Path("data_prefetch/fred/observations")
RATE_LIMIT_SLEEP = 0.5  # FRED rate limit: 120 req/min
TIMEOUT = 30


def fetch(path: str, params: dict | None = None) -> dict:
    p = dict(params or {})
    p["api_key"] = FRED_KEY
    p["file_type"] = "json"
    r = requests.get(f"{BASE}{path}", params=p, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def fetch_paginated(path: str, list_key: str, params: dict | None = None) -> list[dict]:
    out: list[dict] = []
    offset = 0
    limit = 1000
    while True:
        p = dict(params or {})
        p["limit"] = limit
        p["offset"] = offset
        data = fetch(path, p)
        rows = data.get(list_key, [])
        if not rows:
            break
        out.extend(rows)
        if len(rows) < limit:
            break
        offset += limit
        time.sleep(RATE_LIMIT_SLEEP)
    return out


def write(name: str, rows, note: str = "") -> int:
    path = CACHE / f"{name}.parquet"
    if not rows:
        df = pd.DataFrame()
    elif isinstance(rows, list):
        df = pd.DataFrame(rows)
    else:
        df = pd.DataFrame([rows])
    df.to_parquet(path, compression="snappy", index=False)
    print(f"  {name:40s} -> {len(df):>6} rows  {note}")
    return len(df)


def per_series_pull() -> dict[str, list[dict]]:
    """For each series in OBS_DIR, fetch its metadata + cats + release + tags + vintagedates."""
    if not OBS_DIR.exists():
        print("  WARN: no fred/observations dir; per-series metadata skipped")
        return {}
    series_ids = sorted([p.stem for p in OBS_DIR.glob("*.parquet")])
    print(f"  per-series metadata for {len(series_ids)} series ...")
    by_kind: dict[str, list[dict]] = {
        "series": [], "series_categories": [], "series_release": [],
        "series_tags": [], "series_vintagedates": [],
    }
    for i, sid in enumerate(series_ids, 1):
        try:
            d = fetch("/series", {"series_id": sid})
            for r in d.get("seriess", []):
                by_kind["series"].append(r)
            time.sleep(RATE_LIMIT_SLEEP)
            d = fetch("/series/categories", {"series_id": sid})
            for r in d.get("categories", []):
                by_kind["series_categories"].append({**r, "series_id": sid})
            time.sleep(RATE_LIMIT_SLEEP)
            d = fetch("/series/release", {"series_id": sid})
            for r in d.get("releases", []):
                by_kind["series_release"].append({**r, "series_id": sid})
            time.sleep(RATE_LIMIT_SLEEP)
            d = fetch("/series/tags", {"series_id": sid})
            for r in d.get("tags", []):
                by_kind["series_tags"].append({**r, "series_id": sid})
            time.sleep(RATE_LIMIT_SLEEP)
            d = fetch("/series/vintagedates", {"series_id": sid, "limit": 10000})
            for v in d.get("vintage_dates", []):
                by_kind["series_vintagedates"].append({"series_id": sid, "vintage_date": v})
            time.sleep(RATE_LIMIT_SLEEP)
        except requests.HTTPError as e:
            print(f"    {sid}: HTTP error {e}")
            continue
        if i % 10 == 0:
            print(f"    progress: {i}/{len(series_ids)}")
    return by_kind


def main() -> int:
    print(f"FRED metadata -> {CACHE}")

    # Per-series metadata
    by_kind = per_series_pull()
    for name, rows in by_kind.items():
        write(name, rows, f"per-series ({len(set(r.get('series_id') for r in rows if r.get('series_id')))} unique)")

    # Global / static catalogs
    print("  global static catalogs ...")
    try:
        write("series_updates",
              fetch("/series/updates", {"limit": 1000}).get("seriess", []),
              "recently updated series (last 24h-ish)")
    except Exception as e:
        print(f"    series_updates SKIPPED: {e}")

    try:
        write("category_root",
              fetch("/category", {"category_id": 0}).get("categories", []),
              "FRED root category")
    except Exception as e:
        print(f"    category_root SKIPPED: {e}")

    try:
        write("category_children_root",
              fetch("/category/children", {"category_id": 0}).get("categories", []),
              "root children")
    except Exception as e:
        print(f"    category_children SKIPPED: {e}")

    try:
        write("releases", fetch_paginated("/releases", "releases"),
              "all FRED releases")
    except Exception as e:
        print(f"    releases SKIPPED: {e}")

    try:
        write("sources", fetch_paginated("/sources", "sources"),
              "all FRED sources")
    except Exception as e:
        print(f"    sources SKIPPED: {e}")

    try:
        write("tags", fetch_paginated("/tags", "tags"),
              "all FRED tags")
    except Exception as e:
        print(f"    tags SKIPPED: {e}")

    print("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
