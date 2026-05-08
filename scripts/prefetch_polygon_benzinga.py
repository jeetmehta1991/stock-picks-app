"""scripts/prefetch_polygon_benzinga.py - Polygon Benzinga partner data.

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08.

Probe-confirmed working at our tier (200 OK):
  /benzinga/v1/analyst-insights -> rating_action, insight, date, firm,
                                    price_target, rating, last_updated,
                                    company_name

Other Benzinga endpoints to probe + add: ratings, bulls-bears-say,
consensus, guidance, earnings, firm-details, news.

Output: data_prefetch/polygon/benzinga/{endpoint}/{ticker}.parquet
Commit every 100 tickers.

Run: python scripts/prefetch_polygon_benzinga.py
     --tickers AAPL MSFT (smoke)
     --batch-size 100
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

POLYGON_KEY = os.environ.get("POLYGON_API_KEY", "")
if not POLYGON_KEY:
    print("ERROR: POLYGON_API_KEY not set")
    sys.exit(1)

CACHE_ROOT = Path("data_prefetch/polygon/benzinga")
CHECKPOINT_FILE = Path("data_prefetch/polygon/benzinga/_checkpoint.json")
TIMEOUT = 30
RATE_LIMIT_SLEEP = 0.2

# Initial endpoint set - others to be probed/added incrementally
ENDPOINTS = {
    "analyst_insights": "https://api.polygon.io/benzinga/v1/analyst-insights",
    # Probe additional paths at run time
    "ratings": "https://api.polygon.io/benzinga/v1/ratings",
    "consensus": "https://api.polygon.io/benzinga/v1/consensus-ratings",
    "earnings": "https://api.polygon.io/benzinga/v1/earnings",
    "guidance": "https://api.polygon.io/benzinga/v1/guidance",
    "firm_details": "https://api.polygon.io/benzinga/v1/firms",
    "news": "https://api.polygon.io/benzinga/v1/news",
}


def fetch_paginated(url: str, ticker: str | None = None) -> list[dict]:
    h = {"Authorization": f"Bearer {POLYGON_KEY}"}
    out: list[dict] = []
    p = {"limit": 1000}
    if ticker:
        p["ticker"] = ticker
    next_url = url
    pass_params = p
    while next_url:
        r = requests.get(next_url, headers=h, params=pass_params, timeout=TIMEOUT)
        if r.status_code == 404:
            return None
        if r.status_code == 403:
            return "BLOCKED"
        if r.status_code != 200:
            print(f"    HTTP {r.status_code}: {r.text[:80]}")
            break
        data = r.json()
        results = data.get("results") or data.get("data") or []
        if isinstance(results, dict):
            results = [results]
        out.extend(results)
        next_url = data.get("next_url")
        pass_params = {}
        time.sleep(0.1)
        if len(out) >= 5000:  # safety cap per ticker
            break
    return out


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
    ap.add_argument("--tickers", nargs="+", default=None)
    ap.add_argument("--batch-size", type=int, default=100)
    ap.add_argument("--no-git", action="store_true")
    args = ap.parse_args()

    CACHE_ROOT.mkdir(parents=True, exist_ok=True)

    if args.tickers:
        tickers = sorted(t.upper() for t in args.tickers)
    else:
        master_csv = Path("Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv")
        df_uni = pd.read_csv(master_csv, comment="#")
        tickers = sorted(df_uni["Symbol"].dropna().str.strip().str.upper().unique())

    print(f"=== Polygon Benzinga prefetch ({len(ENDPOINTS)} endpoints x {len(tickers)} tickers) ===")

    # Probe each endpoint with first ticker to confirm tier access
    print("Probing endpoint access ...")
    probe_ticker = tickers[0]
    accessible: dict[str, bool] = {}
    for key, url in ENDPOINTS.items():
        result = fetch_paginated(url, ticker=probe_ticker)
        if result == "BLOCKED":
            accessible[key] = False
            print(f"  {key}: 403 BLOCKED")
        elif result is None:
            accessible[key] = False
            print(f"  {key}: 404 NOT FOUND (URL guess wrong)")
        else:
            accessible[key] = True
            print(f"  {key}: OK ({len(result)} sample records for {probe_ticker})")
        time.sleep(0.5)

    accessible_keys = [k for k, v in accessible.items() if v]
    print(f"\nAccessible endpoints: {accessible_keys}")
    if not accessible_keys:
        print("No accessible endpoints. Exiting.")
        return 1

    cp = load_checkpoint()

    for key in accessible_keys:
        url = ENDPOINTS[key]
        out_dir = CACHE_ROOT / key
        out_dir.mkdir(parents=True, exist_ok=True)
        done = set(cp.get(key, []))
        remaining = [t for t in tickers if t not in done]
        print(f"\n--- {key} --- {len(remaining)} remaining / {len(tickers)}")
        batch_count = 0
        for i, ticker in enumerate(remaining, 1):
            print(f"  [{i}/{len(remaining)}] {ticker} ... ", end="", flush=True)
            try:
                records = fetch_paginated(url, ticker=ticker)
                if records is None:
                    records = []
                if isinstance(records, str):
                    print("BLOCKED")
                    continue
                out = out_dir / f"{ticker.replace('-', '_')}.parquet"
                if records:
                    df = pd.DataFrame(records)
                    # Date typing
                    for col in ("date", "Date", "last_updated", "report_date"):
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors="coerce")
                    df.to_parquet(out, index=False)
                else:
                    pd.DataFrame().to_parquet(out)
                cp[key] = cp.get(key, [])
                cp[key].append(ticker)
                save_checkpoint(cp)
                batch_count += 1
                print(f"OK {len(records)}")
                if not args.no_git and batch_count % args.batch_size == 0:
                    git_commit(f"Polygon Benzinga: {key} batch {batch_count // args.batch_size}")
            except Exception as e:
                print(f"ERROR {e}")
            time.sleep(RATE_LIMIT_SLEEP)

        if not args.no_git and batch_count > 0:
            git_commit(f"Polygon Benzinga: {key} final ({batch_count} fetched)")
        print(f"  {key} done: {len(cp[key])}")

    print("\nBenzinga prefetch complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
