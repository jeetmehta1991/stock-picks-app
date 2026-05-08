"""scripts/prefetch_quiver_new_endpoints.py - probe-discovered Quiver endpoints.

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08.

Endpoints discovered by `scripts/probe_api_catalog.py` to be working at our
Trader plan tier but NOT previously prefetched:
  /historical/senatetrading/{ticker}  -> Senator-only feed
  /historical/housetrading/{ticker}   -> House-only feed
  /historical/spacs/{ticker}          -> SPAC mention timeline

Output:
  data_prefetch/quiver/senatetrading/{ticker}.parquet
  data_prefetch/quiver/housetrading/{ticker}.parquet
  data_prefetch/quiver/spacs/{ticker}.parquet

Run: python scripts/prefetch_quiver_new_endpoints.py
     --batch-size 100 --commit-every 100
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

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

QUIVER_KEY = os.environ.get("QUIVER_API_KEY", "")
if not QUIVER_KEY:
    print("ERROR: QUIVER_API_KEY not set")
    sys.exit(1)

BASE = "https://api.quiverquant.com/beta"
HEADERS = {"Authorization": f"Token {QUIVER_KEY}"}
RATE_LIMIT_SLEEP = 1.2
TIMEOUT = 15

CACHE_ROOT = Path("data_prefetch/quiver")
CHECKPOINT_FILE = Path("data_prefetch/quiver/_new_endpoints_checkpoint.json")

ENDPOINTS = {
    "senatetrading": "historical/senatetrading",
    "housetrading":  "historical/housetrading",
    "spacs":         "historical/spacs",
}


def fetch_endpoint(endpoint: str, ticker: str) -> list:
    url = f"{BASE}/{endpoint}/{ticker}"
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    if r.status_code == 200:
        return r.json() if r.text.strip() else []
    if r.status_code == 404:
        return []  # ticker not covered for this endpoint
    if r.status_code == 429:
        time.sleep(60)
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json() if r.text.strip() else []
    return None  # other error


def save_records(records: list, key: str, ticker: str) -> None:
    out_dir = CACHE_ROOT / key
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{ticker.replace('-', '_')}.parquet"
    if not records:
        pd.DataFrame().to_parquet(out)
        return
    df = pd.DataFrame(records)
    # Date typing if column present
    for col in ("Date", "TransactionDate", "ReportDate"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    df.to_parquet(out, index=False)


def load_checkpoint() -> dict:
    if CHECKPOINT_FILE.exists():
        return json.loads(CHECKPOINT_FILE.read_text())
    return {k: [] for k in ENDPOINTS}


def save_checkpoint(cp: dict) -> None:
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(json.dumps(cp))


def git_commit(message: str) -> None:
    import subprocess
    subprocess.run(["git", "add", str(CACHE_ROOT)], capture_output=True)
    result = subprocess.run(["git", "commit", "-m", message],
                            capture_output=True, text=True)
    if "nothing to commit" in result.stdout:
        return
    subprocess.run(["git", "pull", "--rebase", "origin", "main"], capture_output=True, text=True)
    subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="+", default=None,
                    help="Explicit tickers (smoke / demo)")
    ap.add_argument("--batch-size", type=int, default=100)
    ap.add_argument("--no-git", action="store_true")
    args = ap.parse_args()

    if args.tickers:
        tickers = sorted(t.upper() for t in args.tickers)
    else:
        master_csv = Path("Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv")
        df_uni = pd.read_csv(master_csv, comment="#")
        tickers = sorted(df_uni["Symbol"].dropna().str.strip().str.upper().unique())

    print(f"=== Quiver new-endpoints prefetch ({len(ENDPOINTS)} endpoints x {len(tickers)} tickers) ===")
    cp = load_checkpoint()

    for key, path in ENDPOINTS.items():
        done = set(cp.get(key, []))
        remaining = [t for t in tickers if t not in done]
        print(f"\n--- {key} --- {len(remaining)} remaining / {len(tickers)} total")
        batch_count = 0
        for i, ticker in enumerate(remaining, 1):
            print(f"  [{i}/{len(remaining)}] {ticker} ... ", end="", flush=True)
            try:
                records = fetch_endpoint(path, ticker)
                if records is None:
                    print("ERROR")
                    continue
                save_records(records, key, ticker)
                cp[key].append(ticker)
                save_checkpoint(cp)
                batch_count += 1
                n = len(records) if isinstance(records, list) else 0
                print(f"OK {n}")

                if not args.no_git and batch_count % args.batch_size == 0:
                    git_commit(f"Quiver new-endpoints: {key} batch {batch_count // args.batch_size}")
            except Exception as e:
                print(f"ERROR {e}")
            time.sleep(RATE_LIMIT_SLEEP)

        if not args.no_git and batch_count > 0:
            git_commit(f"Quiver new-endpoints: {key} final ({batch_count} fetched)")
        print(f"  {key} done: {len(cp[key])}")

    print("\nQuiver new-endpoints prefetch complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
