"""B561 follow-on (2026-06-02): one-time fetch of FLT (FleetCor) OHLCV for
sector_history.csv 2023-03-17 row pair restoration.

FLT was renamed to CPAY on 2024-03-25. Polygon retains historical FLT data
under the FLT ticker (pre-rename). Without this prefetch, FLT.parquet is
absent and the FLT row of the 2023-03-17 GICS reclassification (IT ->
Financials cohort) cannot be added to sector_history.csv.

Per CLAUDE.md DEC-497 NO-LIVE-API HARD CUT, runtime engine cannot hit
Polygon. This script is one-time SETUP only -- runs on laptop, writes
parquet to disk, exits. Never invoked by the backtest hot path.

Usage:
  python scripts/fetch_flt_one_time_b561.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).parent.parent
load_dotenv(REPO_ROOT / ".env")

POLYGON_KEY = os.environ.get("POLYGON_API_KEY", "")
if not POLYGON_KEY:
    print("ERROR: POLYGON_API_KEY not set in environment or .env")
    sys.exit(1)

# Match the existing data_prefetch OHLCV window. CPAY parquet starts
# 2024-03-25 so FLT covers up to 2024-03-22 (last trading day under FLT).
START = "2021-05-08"
END = "2024-03-25"

url = f"https://api.polygon.io/v2/aggs/ticker/FLT/range/1/day/{START}/{END}"
r = requests.get(
    url,
    params={
        "apiKey": POLYGON_KEY,
        "adjusted": "true",
        "sort": "asc",
        "limit": 50000,
    },
    timeout=30,
)
if r.status_code != 200:
    print(f"FAIL HTTP {r.status_code}: {r.text[:200]}")
    sys.exit(1)
data = r.json()
results = data.get("results", []) or []
print(f"Fetched {len(results)} rows for FLT {START} -> {END}")
if not results:
    print(
        "EMPTY response. Polygon may have remapped FLT history to the "
        "post-rename CPAY ticker entirely. In that case, the only path "
        "to restore the FLT sector_history row is to query CPAY for the "
        "pre-2024-03-25 window and rename the ticker column to FLT."
    )
    sys.exit(0)

df = pd.DataFrame(results)
df["date"] = pd.to_datetime(df["t"], unit="ms").dt.date
df = df.rename(
    columns={
        "o": "open",
        "h": "high",
        "l": "low",
        "c": "close",
        "v": "volume",
        "vw": "vwap",
        "n": "transactions",
    }
)
df["ticker"] = "FLT"
df = df[
    [
        "ticker",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "vwap",
        "transactions",
    ]
]
df = df.sort_values("date").reset_index(drop=True)
# Coerce dtypes to match CPAY / other existing OHLCV parquets
df["ticker"] = df["ticker"].astype("string")
df["volume"] = df["volume"].astype("float64")
df["transactions"] = df["transactions"].astype("int64")

print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Schema dtypes: {df.dtypes.to_dict()}")

out = REPO_ROOT / "data_prefetch" / "polygon" / "ohlcv_daily" / "FLT.parquet"
out.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(out, index=False)
print(f"WROTE {out} ({len(df)} rows, {out.stat().st_size:,} bytes)")
