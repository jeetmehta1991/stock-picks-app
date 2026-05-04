"""
scripts/prefetch_polygon_reference.py — Pre-fetch Polygon ticker reference details.

Per DEC-441 + DEC-257 (fundamentals partial; consumed Phase 1B not Phase 1A):
  - Ticker name, market cap, sector/SIC, primary exchange
  - List date, delisting date (if applicable)
  - CIK number for SEC EDGAR cross-reference (DEC-484)
  - Currency (USD validation)

Cache: backtest/data/cache/polygon/reference/{TICKER}.parquet
Single combined index: backtest/data/cache/polygon/reference_index.parquet

Run from laptop:
  python scripts/prefetch_polygon_reference.py
  python scripts/prefetch_polygon_reference.py --limit-tickers 5    # test
  python scripts/prefetch_polygon_reference.py --tickers AAPL MSFT  # explicit list

Estimated wall time: ~5-10 minutes for 484 tickers.
"""

import os
import sys
import time
import json
import argparse
import requests
import pandas as pd
from pathlib import Path
from datetime import date

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

POLYGON_KEY = os.environ.get("POLYGON_API_KEY", "")
if not POLYGON_KEY:
    print("ERROR: POLYGON_API_KEY not set")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "https://api.polygon.io"
CACHE_DIR = Path("backtest/data/cache/polygon/reference")
INDEX_FILE = Path("backtest/data/cache/polygon/reference_index.parquet")
UNIVERSE_CSV = Path("backtest/data/sp500_tickers.csv")

RATE_LIMIT_SLEEP = 0.05
TIMEOUT = 30


def fetch_ticker_reference(ticker: str) -> dict:
    """Fetch /v3/reference/tickers/{ticker} — full reference detail."""
    url = f"{BASE_URL}/v3/reference/tickers/{ticker}"
    try:
        r = requests.get(url, params={"apiKey": POLYGON_KEY}, timeout=TIMEOUT)
    except requests.RequestException as e:
        return {"ticker": ticker, "error": str(e)}
    if r.status_code != 200:
        return {"ticker": ticker, "error": f"HTTP {r.status_code}"}
    data = r.json().get("results", {})
    if not data:
        return {"ticker": ticker, "error": "no results"}
    return {
        "ticker": ticker,
        "name": data.get("name"),
        "market_cap": data.get("market_cap"),
        "share_class_shares_outstanding": data.get("share_class_shares_outstanding"),
        "weighted_shares_outstanding": data.get("weighted_shares_outstanding"),
        "sic_code": data.get("sic_code"),
        "sic_description": data.get("sic_description"),
        "primary_exchange": data.get("primary_exchange"),
        "type": data.get("type"),
        "active": data.get("active"),
        "currency_name": data.get("currency_name"),
        "cik": data.get("cik"),
        "list_date": data.get("list_date"),
        "delisted_utc": data.get("delisted_utc"),
        "homepage_url": data.get("homepage_url"),
        "fetched_at": str(date.today()),
    }


def main():
    ap = argparse.ArgumentParser(description="Polygon reference prefetch")
    ap.add_argument("--limit-tickers", type=int, default=None,
                    help="Only fetch first N tickers. For testing.")
    ap.add_argument("--tickers", nargs="+", default=None,
                    help="Explicit ticker list. For testing.")
    args = ap.parse_args()

    print(f"=== Polygon Reference Prefetch ===")
    print(f"Universe: {UNIVERSE_CSV}")
    print(f"Output:   {CACHE_DIR}/ + {INDEX_FILE}")
    if args.tickers:
        print(f"Mode:     EXPLICIT TICKERS ({len(args.tickers)})")
    elif args.limit_tickers:
        print(f"Mode:     LIMITED ({args.limit_tickers} tickers — TEST RUN)")
    else:
        print(f"Mode:     FULL UNIVERSE")
    print()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if args.tickers:
        tickers = sorted(t.upper() for t in args.tickers)
    else:
        df_uni = pd.read_csv(UNIVERSE_CSV)
        tickers = sorted(df_uni["Symbol"].dropna().str.strip().str.upper().unique())
        if args.limit_tickers:
            tickers = tickers[:args.limit_tickers]
    print(f"Tickers: {len(tickers)}")

    rows = []
    failures = []
    start_ts = time.time()

    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] {ticker} ... ", end="", flush=True)
        ref = fetch_ticker_reference(ticker)
        if "error" in ref:
            print(f"ERROR: {ref['error']}")
            failures.append(ticker)
        else:
            # Write per-ticker file
            pd.DataFrame([ref]).to_parquet(CACHE_DIR / f"{ticker}.parquet", compression="snappy", index=False)
            rows.append(ref)
            print(f"OK ({ref.get('sic_description', 'n/a')[:40]})")
        time.sleep(RATE_LIMIT_SLEEP)

    if rows:
        # Write combined index file
        idx = pd.DataFrame(rows)
        INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        idx.to_parquet(INDEX_FILE, compression="snappy", index=False)
        print(f"\nWrote combined index: {INDEX_FILE} ({len(idx)} rows)")

    elapsed = time.time() - start_ts
    print()
    print(f"Reference prefetch: {len(rows)}/{len(tickers)} succeeded; {len(failures)} failed in {elapsed/60:.1f} min")
    if failures:
        print(f"Failed: {failures[:20]}")
    print()
    print("Next: python scripts/prefetch_polygon_corp_actions.py")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
