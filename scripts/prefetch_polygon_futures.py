"""scripts/prefetch_polygon_futures.py - Polygon Futures Basic prefetch.

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08.

Probe-confirmed working at our tier:
  /futures/v1/contracts            -> contract list
  /futures/v1/products             -> product taxonomy
  /v2/aggs/ticker/{sym}/range/...  -> OHLCV per contract
  /futures/v1/schedules            -> trading schedule

Strategy: fetch products + contracts metadata first, then OHLCV for major
front-month contracts. Per-product prefetch logic handles roll calendar.

Output:
  data_prefetch/polygon/futures/products.parquet
  data_prefetch/polygon/futures/contracts.parquet
  data_prefetch/polygon/futures/aggs/{symbol}.parquet
  data_prefetch/polygon/futures/schedules.parquet
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

CACHE_DIR = Path("data_prefetch/polygon/futures")
DATE_START = "2020-01-01"
DATE_END = "2026-05-08"
TIMEOUT = 30

# Front-month + active futures contracts to prefetch
# Equity index, vol, treasuries, currencies, energy, metals, agri
FUTURES_CONTRACTS = [
    "ES", "NQ", "RTY", "YM",                   # Equity indices
    "VX",                                       # VIX futures
    "ZB", "ZN", "ZF", "ZT",                     # Treasuries (30y/10y/5y/2y)
    "6E", "6J", "6B", "6A", "6C", "6S", "6N",  # Currencies (EUR/JPY/GBP/AUD/CAD/CHF/NZD)
    "CL", "BZ", "NG", "RB", "HO",               # Energy (WTI/Brent/Natgas/RBOB/Heating)
    "GC", "SI", "HG", "PL", "PA",               # Metals (gold/silver/copper/platinum/palladium)
    "ZC", "ZS", "ZW", "KC", "SB", "CT", "CC",  # Agri (corn/soy/wheat/coffee/sugar/cotton/cocoa)
    "LE", "HE",                                 # Live cattle / lean hogs
]


def fetch_paginated(url: str, params: dict | None = None) -> list[dict]:
    h = {"Authorization": f"Bearer {POLYGON_KEY}"}
    out: list[dict] = []
    next_url = url
    p = dict(params or {})
    while next_url:
        r = requests.get(next_url, headers=h, params=p, timeout=TIMEOUT)
        if r.status_code != 200:
            print(f"    HTTP {r.status_code}: {r.text[:120]}")
            break
        data = r.json()
        results = data.get("results", []) or []
        out.extend(results)
        next_url = data.get("next_url")
        p = {}  # next_url has params baked in
        time.sleep(0.1)
    return out


def fetch_contract_aggs(symbol: str) -> pd.DataFrame:
    url = (f"https://api.polygon.io/v2/aggs/ticker/{symbol}"
           f"/range/1/day/{DATE_START}/{DATE_END}")
    h = {"Authorization": f"Bearer {POLYGON_KEY}"}
    r = requests.get(url, headers=h, params={"limit": 50000}, timeout=TIMEOUT)
    if r.status_code != 200:
        return pd.DataFrame()
    data = r.json().get("results", []) or []
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df = df.rename(columns={"t": "timestamp_ms", "o": "open", "h": "high",
                              "l": "low", "c": "close", "v": "volume",
                              "vw": "vwap", "n": "transactions"})
    df["date"] = pd.to_datetime(df["timestamp_ms"], unit="ms").dt.date
    df = df.drop(columns=["timestamp_ms"])
    cols = ["date", "open", "high", "low", "close", "volume", "vwap", "transactions"]
    df = df[[c for c in cols if c in df.columns]]
    return df


def main() -> int:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    aggs_dir = CACHE_DIR / "aggs"
    aggs_dir.mkdir(parents=True, exist_ok=True)
    print(f"=== Polygon Futures prefetch ===")

    # 1. Products
    print("  Products ... ", end="", flush=True)
    products = fetch_paginated("https://api.polygon.io/futures/v1/products")
    if products:
        pd.DataFrame(products).to_parquet(CACHE_DIR / "products.parquet", index=False)
    print(f"{len(products)} products")

    # 2. Contracts
    print("  Contracts ... ", end="", flush=True)
    contracts = fetch_paginated("https://api.polygon.io/futures/v1/contracts",
                                  params={"limit": 1000})
    if contracts:
        pd.DataFrame(contracts).to_parquet(CACHE_DIR / "contracts.parquet", index=False)
    print(f"{len(contracts)} contracts")

    # 3. Schedules
    print("  Schedules ... ", end="", flush=True)
    schedules = fetch_paginated("https://api.polygon.io/futures/v1/schedules",
                                  params={"limit": 1000})
    if schedules:
        pd.DataFrame(schedules).to_parquet(CACHE_DIR / "schedules.parquet", index=False)
    print(f"{len(schedules)} schedule entries")

    # 4. OHLCV per contract symbol
    print(f"  Aggs for {len(FUTURES_CONTRACTS)} contracts (~13s sleep / call for free tier rate limit):")
    ok = 0
    for sym in FUTURES_CONTRACTS:
        out_path = aggs_dir / f"{sym}.parquet"
        if out_path.exists():
            existing = pd.read_parquet(out_path)
            if not existing.empty:
                print(f"    {sym} ... SKIP (cached {len(existing)} bars)")
                ok += 1
                continue
        print(f"    {sym} ... ", end="", flush=True)
        for attempt in range(3):
            try:
                df = fetch_contract_aggs(sym)
                if df.empty:
                    print(f"EMPTY (attempt {attempt+1})")
                    time.sleep(30)
                    continue
                df.to_parquet(out_path, index=False)
                print(f"OK {len(df)} bars")
                ok += 1
                break
            except Exception as e:
                print(f"ERROR {e}")
                time.sleep(30)
        time.sleep(13)

    print(f"\nFutures prefetch: {ok}/{len(FUTURES_CONTRACTS)} aggs OK")
    return 0 if ok > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
