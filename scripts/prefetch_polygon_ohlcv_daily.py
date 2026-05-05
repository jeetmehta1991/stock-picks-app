"""
scripts/prefetch_polygon_ohlcv_daily.py — Pre-fetch Polygon daily OHLCV for Sprint 1 universe.

Per DEC-441 (Polygon Stocks Starter $29/mo) + DEC-256/440 + DEC-482 (5y window May 2021 → May 2026).

Hybrid Path A scope (Pass 53 turn — universe build deferred to tomorrow):
  - Universe: backtest/data/sp500_tickers.csv (484 current-state S&P 500)
  - Cache output: backtest/data/cache/polygon/ohlcv_daily/{TICKER}.parquet
  - Date range: ~5 years backward from today (per DEC-482 Polygon Stocks Starter window)
  - Adjusted=true (per Polygon default; DEC-302 raw OHLCV stored separately if needed Stage 2 walk-back)

Run from laptop:
  python scripts/prefetch_polygon_ohlcv_daily.py
  python scripts/prefetch_polygon_ohlcv_daily.py --limit-tickers 5    # small-scale test
  python scripts/prefetch_polygon_ohlcv_daily.py --tickers AAPL MSFT  # explicit list

Estimated wall time: ~30-60 minutes for 484 tickers (Stocks Starter unlimited rate).

Progress: checkpoint saved every 50 tickers; safe to interrupt and resume.
"""

import os
import sys
import time
import json
import argparse
import requests
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

POLYGON_KEY = os.environ.get("POLYGON_API_KEY", "")
if not POLYGON_KEY:
    print("ERROR: POLYGON_API_KEY not set in environment or .env file")
    sys.exit(1)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# --- Config ---
BASE_URL = "https://api.polygon.io"
CACHE_DIR = Path("backtest/data/cache/polygon/ohlcv_daily")
CHECKPOINT_FILE = Path("backtest/data/cache/polygon/_checkpoint_ohlcv.json")
UNIVERSE_CSV = Path("Backtesting universe/sp500_tickers.csv")

# 5-year window per DEC-482 (Polygon Stocks Starter limit)
END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=5 * 365 + 30)  # 5y + 30d buffer

RATE_LIMIT_SLEEP = 0.05  # Polygon Stocks Starter: unlimited; small sleep for politeness
TIMEOUT = 60
COMMIT_EVERY = 50  # checkpoint every N tickers


def load_universe() -> list[str]:
    """Load tickers from canonical CSV."""
    if not UNIVERSE_CSV.exists():
        print(f"ERROR: Universe CSV not found: {UNIVERSE_CSV}")
        sys.exit(1)
    df = pd.read_csv(UNIVERSE_CSV)
    if "Symbol" not in df.columns:
        print(f"ERROR: Universe CSV missing 'Symbol' column. Got: {list(df.columns)}")
        sys.exit(1)
    tickers = df["Symbol"].dropna().str.strip().str.upper().unique().tolist()
    return sorted(tickers)


def load_checkpoint() -> set:
    """Return set of tickers already prefetched."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f:
            return set(json.load(f).get("completed", []))
    return set()


def save_checkpoint(completed: set):
    """Persist checkpoint."""
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"completed": sorted(completed), "last_updated": str(date.today())}, f, indent=2)


def fetch_ticker_ohlcv(ticker: str) -> pd.DataFrame:
    """Fetch daily aggregates for one ticker, full window. Handles pagination."""
    url = f"{BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{START_DATE}/{END_DATE}"
    params = {
        "apiKey": POLYGON_KEY,
        "adjusted": "true",
        "sort": "asc",
        "limit": 50000,  # max per page; covers 5y daily easily
    }
    all_results = []
    page_count = 0
    while True:
        page_count += 1
        try:
            r = requests.get(url, params=params, timeout=TIMEOUT)
        except requests.RequestException as e:
            print(f"    {ticker} fetch failed: {e}")
            return pd.DataFrame()
        if r.status_code != 200:
            print(f"    {ticker} HTTP {r.status_code}: {r.text[:200]}")
            return pd.DataFrame()
        data = r.json()
        results = data.get("results", []) or []
        all_results.extend(results)

        # Pagination: Polygon returns next_url if more pages
        next_url = data.get("next_url")
        if not next_url:
            break
        url = next_url
        params = {"apiKey": POLYGON_KEY}  # next_url has its own params
        if page_count > 10:
            print(f"    {ticker} aborting: >10 pages (unexpected for daily 5y)")
            break

    if not all_results:
        return pd.DataFrame()

    df = pd.DataFrame(all_results)
    # Polygon fields: t (ms timestamp), o, h, l, c, v, vw, n
    df["date"] = pd.to_datetime(df["t"], unit="ms").dt.date
    df = df.rename(columns={
        "o": "open", "h": "high", "l": "low", "c": "close",
        "v": "volume", "vw": "vwap", "n": "transactions"
    })
    df["ticker"] = ticker
    df = df[["ticker", "date", "open", "high", "low", "close", "volume", "vwap", "transactions"]]
    df = df.sort_values("date").reset_index(drop=True)
    return df


def main():
    ap = argparse.ArgumentParser(description="Polygon daily OHLCV prefetch")
    ap.add_argument("--limit-tickers", type=int, default=None,
                    help="Only fetch first N tickers (alphabetical). For testing.")
    ap.add_argument("--tickers", nargs="+", default=None,
                    help="Explicit ticker list (overrides universe CSV). For testing.")
    args = ap.parse_args()

    print(f"=== Polygon Daily OHLCV Prefetch ===")
    print(f"Universe: {UNIVERSE_CSV}")
    print(f"Window:   {START_DATE} to {END_DATE} (~5 years)")
    print(f"Output:   {CACHE_DIR}/")
    if args.tickers:
        print(f"Mode:     EXPLICIT TICKERS ({len(args.tickers)}: {args.tickers})")
    elif args.limit_tickers:
        print(f"Mode:     LIMITED ({args.limit_tickers} tickers — TEST RUN)")
    else:
        print(f"Mode:     FULL UNIVERSE")
    print()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if args.tickers:
        tickers = sorted(t.upper() for t in args.tickers)
    else:
        tickers = load_universe()
        if args.limit_tickers:
            tickers = tickers[:args.limit_tickers]

    completed = load_checkpoint()
    todo = [t for t in tickers if t not in completed]

    print(f"Total tickers: {len(tickers)}")
    print(f"Already done:  {len(completed) if not args.tickers else 'N/A (explicit list)'}")
    print(f"To fetch:      {len(todo)}")
    print()

    if not todo:
        print("✅ All tickers already cached.")
        return 0

    failures = []
    success_count = 0
    start_ts = time.time()

    for i, ticker in enumerate(todo, 1):
        elapsed = time.time() - start_ts
        rate = i / elapsed if elapsed > 0 else 0
        eta = (len(todo) - i) / rate if rate > 0 else 0
        print(f"[{i}/{len(todo)}] {ticker} ... ", end="", flush=True)

        df = fetch_ticker_ohlcv(ticker)

        if df.empty:
            print("(no data)")
            failures.append(ticker)
            continue

        # Write to parquet (snappy compression, partitioned by ticker)
        out_path = CACHE_DIR / f"{ticker}.parquet"
        df.to_parquet(out_path, compression="snappy", index=False)

        rows = len(df)
        size_kb = out_path.stat().st_size / 1024
        print(f"{rows} rows, {size_kb:.1f} KB (rate: {rate:.1f} t/s, ETA: {eta/60:.1f}min)")

        completed.add(ticker)
        success_count += 1

        if success_count % COMMIT_EVERY == 0:
            save_checkpoint(completed)
            print(f"  -- checkpoint saved ({len(completed)}/{len(tickers)}) --")

        time.sleep(RATE_LIMIT_SLEEP)

    save_checkpoint(completed)

    elapsed = time.time() - start_ts
    print()
    print("=== Prefetch Complete ===")
    print(f"Total tickers fetched: {success_count}")
    print(f"Failures: {len(failures)}")
    if failures:
        print(f"  Failed tickers: {failures[:20]}{'...' if len(failures) > 20 else ''}")
    print(f"Wall time: {elapsed/60:.1f} min")
    print(f"Cache size: {sum(p.stat().st_size for p in CACHE_DIR.glob('*.parquet'))/(1024**2):.1f} MB")
    print()
    print("Next: python scripts/prefetch_polygon_reference.py")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
