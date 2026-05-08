"""scripts/prefetch_polygon_indices.py - Polygon Indices Basic prefetch.

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08 (after Indices Basic activation).

Probe-confirmed accessible at our tier (5 indices):
  I:NDX, I:MID, I:SML, I:NYA, I:COMP

Probe-blocked at our tier (403 — likely CBOE/S&P licensing gate):
  I:VIX, I:SPX, I:DJI, I:RUT, I:VIX9D, I:VIX3M, I:VVIX, I:OEX
  Workaround: FRED VIXCLS / VXVCLS already cached for VIX/VIX3M.

Output: data_prefetch/polygon/indices/{symbol}.parquet
Schema: date (datetime), open, high, low, close, volume, vwap, transactions

Run: python scripts/prefetch_polygon_indices.py
"""

from __future__ import annotations

import os
import sys
import time
import requests
import pandas as pd
from pathlib import Path
from datetime import date

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

CACHE_DIR = Path("data_prefetch/polygon/indices")
DATE_START = "2020-01-01"
DATE_END = "2026-05-08"
RATE_LIMIT_SLEEP = 0.1
TIMEOUT = 30

# Probe-confirmed working at our tier
WORKING_INDICES = ["I:NDX", "I:MID", "I:SML", "I:NYA", "I:COMP"]

# Probe-confirmed 403 - included for re-probe if owner upgrades tier later
BLOCKED_INDICES = ["I:VIX", "I:SPX", "I:DJI", "I:RUT", "I:VIX9D",
                    "I:VIX3M", "I:VVIX", "I:OEX"]


def fetch_index_aggs(symbol: str) -> pd.DataFrame:
    """Fetch daily OHLCV for an index symbol over full date range."""
    url = (f"https://api.polygon.io/v2/aggs/ticker/{symbol}"
           f"/range/1/day/{DATE_START}/{DATE_END}")
    h = {"Authorization": f"Bearer {POLYGON_KEY}"}
    r = requests.get(url, headers=h, params={"limit": 50000}, timeout=TIMEOUT)
    if r.status_code != 200:
        print(f"  [WARN] {symbol}: HTTP {r.status_code} - {r.text[:80]}")
        return pd.DataFrame()
    data = r.json().get("results", []) or []
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    # Polygon aggregate keys: t (timestamp ms), o, h, l, c, v, vw, n
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
    print(f"=== Polygon Indices prefetch ===")
    print(f"Working indices ({len(WORKING_INDICES)}): {WORKING_INDICES}")
    print(f"Blocked indices ({len(BLOCKED_INDICES)}): {BLOCKED_INDICES}")
    print(f"Date range: {DATE_START} to {DATE_END}")
    print(f"Output: {CACHE_DIR}")
    print()

    ok = 0
    failed = []
    for sym in WORKING_INDICES:
        print(f"  Fetching {sym} ... ", end="", flush=True)
        try:
            df = fetch_index_aggs(sym)
            if df.empty:
                print("EMPTY")
                failed.append(sym)
                continue
            out = CACHE_DIR / f"{sym.replace(':', '_')}.parquet"
            df.to_parquet(out, index=False)
            print(f"OK {len(df)} bars -> {out.name}")
            ok += 1
        except Exception as e:
            print(f"ERROR {e}")
            failed.append(sym)
        time.sleep(RATE_LIMIT_SLEEP)

    # Also try blocked ones (capture 403 for record)
    print("\n  Re-probing blocked indices (for record)...")
    for sym in BLOCKED_INDICES:
        try:
            df = fetch_index_aggs(sym)
            if not df.empty:
                # Surprise - now accessible!
                out = CACHE_DIR / f"{sym.replace(':', '_')}.parquet"
                df.to_parquet(out, index=False)
                print(f"  [INFO] {sym} now ACCESSIBLE - {len(df)} bars saved")
                ok += 1
        except Exception:
            pass
        time.sleep(RATE_LIMIT_SLEEP)

    print(f"\nIndices prefetch: {ok}/{len(WORKING_INDICES) + len(BLOCKED_INDICES)} succeeded")
    if failed:
        print(f"Failed: {failed}")
    return 0 if ok > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
