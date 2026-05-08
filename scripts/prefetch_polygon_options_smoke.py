"""scripts/prefetch_polygon_options_smoke.py - Tier H10 smoke (Pass 53 v8h+1).

Fetches /v3/reference/options/contracts for a few sample underlyings to:
  (1) verify endpoint accessible at Basic plan tier
  (2) measure: contracts per underlying, response time, payload size
  (3) estimate storage for full 1937-ticker rollout before owner approves scale

Output:
  data_prefetch/polygon/options_chains/{underlying}.parquet  (smoke set only)
  prints summary table to stdout

Run: python scripts/prefetch_polygon_options_smoke.py
     python scripts/prefetch_polygon_options_smoke.py --tickers AAPL TSLA SPY
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests


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

BASE = "https://api.polygon.io"
TIMEOUT = 20
RATE_LIMIT_SLEEP = 0.6  # Polygon Stocks Starter = unlimited; conservative throttle

CACHE_ROOT = Path("data_prefetch/polygon/options_chains")
CACHE_ROOT.mkdir(parents=True, exist_ok=True)


def fetch_options_chain(underlying: str, max_pages: int = 10) -> tuple[list, float, int]:
    """Returns (contracts_list, elapsed_sec, http_calls)."""
    url = f"{BASE}/v3/reference/options/contracts"
    params = {
        "underlying_ticker": underlying,
        "expired": "false",
        "limit": 1000,
        "apiKey": POLYGON_KEY,
    }
    contracts: list = []
    pages = 0
    t0 = time.time()
    next_url: str | None = None
    while pages < max_pages:
        if next_url:
            r = requests.get(next_url + f"&apiKey={POLYGON_KEY}", timeout=TIMEOUT)
        else:
            r = requests.get(url, params=params, timeout=TIMEOUT)
        pages += 1
        if r.status_code == 401:
            return ([], time.time() - t0, pages)  # auth failure
        if r.status_code == 403:
            return ([], time.time() - t0, pages)  # tier-gated
        if r.status_code == 429:
            time.sleep(60)
            continue
        if r.status_code != 200:
            break
        body = r.json()
        results = body.get("results") or []
        contracts.extend(results)
        next_url = body.get("next_url")
        if not next_url:
            break
        time.sleep(RATE_LIMIT_SLEEP)
    return (contracts, time.time() - t0, pages)


def save(contracts: list, underlying: str) -> int:
    out = CACHE_ROOT / f"{underlying}.parquet"
    if not contracts:
        pd.DataFrame().to_parquet(out)
        return 0
    df = pd.DataFrame(contracts)
    if "expiration_date" in df.columns:
        df["expiration_date"] = pd.to_datetime(df["expiration_date"], errors="coerce")
    df.to_parquet(out, index=False)
    return out.stat().st_size


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="+", default=["AAPL", "TSLA", "SPY", "QQQ", "MSFT"],
                    help="Smoke set (default 5 high-liquidity)")
    args = ap.parse_args()

    print(f"=== Polygon Options Basic smoke ({len(args.tickers)} underlyings) ===")
    rows = []
    total_contracts = 0
    total_bytes = 0
    total_secs = 0.0
    for t in args.tickers:
        print(f"  {t} ... ", end="", flush=True)
        contracts, elapsed, pages = fetch_options_chain(t)
        n = len(contracts)
        bytes_written = save(contracts, t)
        rows.append({
            "ticker": t,
            "contracts": n,
            "pages": pages,
            "elapsed_sec": round(elapsed, 2),
            "bytes": bytes_written,
        })
        total_contracts += n
        total_bytes += bytes_written
        total_secs += elapsed
        print(f"contracts={n} pages={pages} elapsed={elapsed:.1f}s bytes={bytes_written}")
        time.sleep(RATE_LIMIT_SLEEP)

    print()
    print(f"Smoke totals: contracts={total_contracts}  bytes={total_bytes:,}  secs={total_secs:.1f}")
    if args.tickers:
        avg_contracts = total_contracts / len(args.tickers)
        avg_bytes = total_bytes / len(args.tickers)
        avg_secs = total_secs / len(args.tickers)
        # Project to 1937 universe
        proj_contracts = avg_contracts * 1937
        proj_bytes = avg_bytes * 1937
        proj_secs = avg_secs * 1937
        print(f"Per-ticker avg: contracts={avg_contracts:.0f}  bytes={avg_bytes:,.0f}  secs={avg_secs:.1f}")
        print(f"Projected 1937-ticker full rollout (chain reference only):")
        print(f"  contracts: {proj_contracts:,.0f}")
        print(f"  storage:   {proj_bytes / 1e6:.1f} MB")
        print(f"  duration:  {proj_secs / 60:.1f} min ({proj_secs / 3600:.2f} h)")
        print()
        print(f"Per-contract OHLCV (endpoint 2) NOT FETCHED in smoke - that is the")
        print(f"big-storage layer. Owner approval required before scaling endpoint 2.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
