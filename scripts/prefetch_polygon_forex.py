"""scripts/prefetch_polygon_forex.py - Polygon Forex Basic prefetch.

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08.

Probe-confirmed working at our tier:
  /v2/aggs/ticker/C:{PAIR}/range/1/day/...   (OHLCV per pair)
  /v3/reference/tickers?market=fx           (pair list)

Probe-blocked: /v1/conversion (requires higher tier)

Pairs prefetched (DXY components + risk-on/off + EM):
  EURUSD, USDJPY, GBPUSD, USDCAD, USDCHF, AUDUSD, NZDUSD, USDCNY,
  USDMXN, USDINR, USDKRW, USDBRL

Output: data_prefetch/polygon/forex/{pair}.parquet
Schema: date, open, high, low, close, volume, vwap, transactions
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

CACHE_DIR = Path("data_prefetch/polygon/forex")
DATE_START = "2020-01-01"
DATE_END = "2026-05-08"
TIMEOUT = 30

PAIRS = [
    "EURUSD", "USDJPY", "GBPUSD", "USDCAD", "USDCHF", "AUDUSD",
    "NZDUSD", "USDCNY", "USDMXN", "USDINR", "USDKRW", "USDBRL",
]


def fetch_pair(pair: str) -> pd.DataFrame:
    sym = f"C:{pair}"
    url = (f"https://api.polygon.io/v2/aggs/ticker/{sym}"
           f"/range/1/day/{DATE_START}/{DATE_END}")
    h = {"Authorization": f"Bearer {POLYGON_KEY}"}
    r = requests.get(url, headers=h, params={"limit": 50000}, timeout=TIMEOUT)
    if r.status_code != 200:
        print(f"  [WARN] {pair}: HTTP {r.status_code}")
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
    print(f"=== Polygon Forex prefetch ({len(PAIRS)} pairs) ===")
    print("Rate limit: free Forex Basic = ~5 calls/min, sleeping 13s between calls")
    ok = 0
    for pair in PAIRS:
        # Skip if already cached (resume support)
        out_path = CACHE_DIR / f"{pair}.parquet"
        if out_path.exists():
            existing = pd.read_parquet(out_path)
            if not existing.empty:
                print(f"  {pair} ... SKIP (cached {len(existing)} bars)")
                ok += 1
                continue
        print(f"  {pair} ... ", end="", flush=True)
        # Retry on 429
        for attempt in range(3):
            try:
                df = fetch_pair(pair)
                if df.empty:
                    print(f"EMPTY (attempt {attempt+1})")
                    time.sleep(30)  # rate-limit cooldown
                    continue
                df.to_parquet(out_path, index=False)
                print(f"OK {len(df)} bars")
                ok += 1
                break
            except Exception as e:
                print(f"ERROR {e}")
                time.sleep(30)
        time.sleep(13)  # 5 calls/min ceiling
    print(f"\nForex prefetch: {ok}/{len(PAIRS)} succeeded")
    return 0 if ok > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
