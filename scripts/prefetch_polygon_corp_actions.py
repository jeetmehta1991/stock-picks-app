"""
scripts/prefetch_polygon_corp_actions.py — Pre-fetch Polygon splits + dividends for Sprint 1 universe.

Per DEC-441 + DEC-302 (raw OHLCV + adjusted-on-demand requires corp actions cache).

Splits cache: backtest/data/cache/polygon/splits/all_splits.parquet (single file — paginated all)
Dividends cache: backtest/data/cache/polygon/dividends/all_dividends.parquet (single file — paginated all)

Polygon /v3/reference/splits and /v3/reference/dividends are universe-wide endpoints
(no per-ticker filter needed); paginate to get all events in our 5y window.

Run from laptop:
  python scripts/prefetch_polygon_corp_actions.py
  python scripts/prefetch_polygon_corp_actions.py --tickers AAPL MSFT GOOGL  # filter for test

Estimated wall time: ~5-10 minutes (paginated; thousands of records).
"""

import os
import sys
import time
import argparse
import requests
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

POLYGON_KEY = os.environ.get("POLYGON_API_KEY", "")
if not POLYGON_KEY:
    print("ERROR: POLYGON_API_KEY not set")
    sys.exit(1)

BASE_URL = "https://api.polygon.io"
# Pass 53 Day-9 v8h: canonical Sprint 0A path per L146 wiring matrix.
SPLITS_DIR = Path("data_prefetch/polygon/splits")
DIVIDENDS_DIR = Path("data_prefetch/polygon/dividends")

# 5y window per DEC-482
END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=5 * 365 + 30)

TIMEOUT = 60


def fetch_paginated(endpoint: str, params: dict, max_pages: int = 1000) -> list:
    """Paginate through Polygon endpoint until next_url is None.

    Pass 53 fix: max_pages raised from 100 -> 1000 (default). Polygon Stocks Starter has
    unlimited rate; 1000 pages * 1000 records/page = 1M records ceiling — well beyond
    realistic global dividends/splits data volume (~200-500k dividends total in 5y window).
    """
    url = f"{BASE_URL}{endpoint}"
    all_results = []
    page = 0
    while True:
        page += 1
        try:
            r = requests.get(url, params=params, timeout=TIMEOUT)
        except requests.RequestException as e:
            print(f"    Page {page} failed: {e}")
            break
        if r.status_code != 200:
            print(f"    Page {page} HTTP {r.status_code}: {r.text[:200]}")
            break
        data = r.json()
        results = data.get("results", []) or []
        all_results.extend(results)
        next_url = data.get("next_url")
        if not next_url:
            break
        url = next_url
        params = {"apiKey": POLYGON_KEY}
        if page >= max_pages:
            print(f"    WARNING: hit max_pages={max_pages} at {len(all_results)} records — increase --max-pages if more data expected")
            break
        if page % 50 == 0:
            print(f"    Page {page}: cumulative {len(all_results)} records")
        time.sleep(0.05)
    return all_results


def fetch_per_ticker(endpoint: str, base_params: dict, tickers: list, max_pages: int = 50) -> list:
    """Per-ticker loop for endpoints where ticker.in= is silently ignored by Polygon
    (verified Pass 53 for /v3/reference/dividends and /v3/reference/splits).

    Issues one query per ticker with ticker=X (single-ticker filter DOES work).
    Concatenates results. Suitable for small ticker lists (test mode).
    """
    all_results = []
    for i, t in enumerate(tickers, 1):
        params = dict(base_params)
        params["ticker"] = t.upper()
        print(f"    [{i}/{len(tickers)}] {t.upper()}")
        results = fetch_paginated(endpoint, params, max_pages=max_pages)
        all_results.extend(results)
    return all_results


def main():
    ap = argparse.ArgumentParser(description="Polygon corp actions prefetch")
    ap.add_argument("--tickers", nargs="+", default=None,
                    help="Filter to specific tickers (universe-wide if omitted). For testing.")
    ap.add_argument("--test-suffix", type=str, default=None,
                    help="Append suffix to output filenames (e.g., '_test') for test runs.")
    ap.add_argument("--max-pages", type=int, default=1000,
                    help="Max pages per global query (default 1000 = 1M records ceiling).")
    args = ap.parse_args()

    print(f"=== Polygon Corporate Actions Prefetch ===")
    print(f"Window: {START_DATE} to {END_DATE} (~5 years)")
    if args.tickers:
        print(f"Filter: {args.tickers} (per-ticker loop — Polygon ticker.in= broken for these endpoints, Pass 53 verified)")
    print()

    splits_params = {
        "apiKey": POLYGON_KEY,
        "execution_date.gte": str(START_DATE),
        "execution_date.lte": str(END_DATE),
        "limit": 1000,
        "order": "asc",
        "sort": "execution_date",
    }
    divs_params = {
        "apiKey": POLYGON_KEY,
        "ex_dividend_date.gte": str(START_DATE),
        "ex_dividend_date.lte": str(END_DATE),
        "limit": 1000,
        "order": "asc",
        "sort": "ex_dividend_date",
    }

    suffix = args.test_suffix or ""

    # SPLITS
    print("[1/2] Fetching splits...")
    SPLITS_DIR.mkdir(parents=True, exist_ok=True)
    if args.tickers:
        splits = fetch_per_ticker("/v3/reference/splits", splits_params, args.tickers, max_pages=50)
    else:
        splits = fetch_paginated("/v3/reference/splits", splits_params, max_pages=args.max_pages)
    if splits:
        df_splits = pd.DataFrame(splits)
        out_path = SPLITS_DIR / f"all_splits{suffix}.parquet"
        df_splits.to_parquet(out_path, compression="snappy", index=False)
        print(f"  Splits: {len(df_splits)} records -> {out_path}")
    else:
        print(f"  WARNING: no splits returned (filter={args.tickers if args.tickers else 'none'})")

    # DIVIDENDS
    print("\n[2/2] Fetching dividends...")
    DIVIDENDS_DIR.mkdir(parents=True, exist_ok=True)
    if args.tickers:
        divs = fetch_per_ticker("/v3/reference/dividends", divs_params, args.tickers, max_pages=50)
    else:
        divs = fetch_paginated("/v3/reference/dividends", divs_params, max_pages=args.max_pages)
    if divs:
        df_divs = pd.DataFrame(divs)
        out_path = DIVIDENDS_DIR / f"all_dividends{suffix}.parquet"
        df_divs.to_parquet(out_path, compression="snappy", index=False)
        print(f"  Dividends: {len(df_divs)} records -> {out_path}")
    else:
        print(f"  WARNING: no dividends returned (filter={args.tickers if args.tickers else 'none'})")

    print()
    print("Next: python scripts/prefetch_polygon_news.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
