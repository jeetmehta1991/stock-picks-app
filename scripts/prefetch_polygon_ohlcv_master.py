"""
scripts/prefetch_polygon_ohlcv_master.py - Polygon daily OHLCV prefetch for the 1937-ticker Master Dedup universe.

H1 RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10 (DEC-609; owner-approved Option B).
Distinct from prefetch_polygon_ohlcv_daily.py (S&P 500 only, legacy `backtest/data/cache/polygon/ohlcv_daily/`).

Scope:
  - Universe: Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv (1937 unique tickers)
  - Output:   data_prefetch/polygon/ohlcv_daily/<TICKER>.parquet  (canonical Sprint 0A path per DEC-497 architecture)
  - Schema:   ticker, date, open, high, low, close, volume, vwap, transactions  (9 cols)
  - Window:   ~5 years backward (Polygon Stocks Starter rolling window per DEC-482)
  - Adjusted: true (split + dividend-adjusted)

Smoke -> demo -> full protocol per CHECKLIST #68:
  python scripts/prefetch_polygon_ohlcv_master.py --tickers AAPL MSFT NVDA GOOGL TSLA   # smoke (5)
  python scripts/prefetch_polygon_ohlcv_master.py --limit-tickers 50                     # demo (50)
  python scripts/prefetch_polygon_ohlcv_master.py                                         # full (1937)

Estimated wallclock: ~60-90 min for full 1937 (Polygon Stocks Starter unlimited rate; bottleneck is per-call latency + write).
Checkpoint saved every 50 tickers; safe to interrupt and resume.

NO-LIVE-API note: this script is a prefetch utility (lives in scripts/), not runtime code.
DEC-497 HARD CUT applies only to backtest/data/, signals/, engine/, results/ - prefetch
scripts are explicitly the home for live API calls.
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

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

POLYGON_KEY = os.environ.get("POLYGON_API_KEY", "")
if not POLYGON_KEY:
    print("ERROR: POLYGON_API_KEY not set in environment or .env file")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "https://api.polygon.io"
CACHE_DIR = Path("data_prefetch/polygon/ohlcv_daily")
CHECKPOINT_FILE = Path("data_prefetch/polygon/_checkpoint_ohlcv_master.json")
UNIVERSE_CSV = Path("Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv")

END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=5 * 365 + 30)

RATE_LIMIT_SLEEP = 0.05
TIMEOUT = 60
COMMIT_EVERY = 50


def load_universe() -> list[str]:
    if not UNIVERSE_CSV.exists():
        print(f"ERROR: Universe CSV not found: {UNIVERSE_CSV}")
        sys.exit(1)
    df = pd.read_csv(UNIVERSE_CSV, comment="#")
    if "Symbol" not in df.columns:
        print(f"ERROR: Universe CSV missing 'Symbol' column. Got: {list(df.columns)}")
        sys.exit(1)
    tickers = df["Symbol"].dropna().str.strip().str.upper().unique().tolist()
    return sorted(tickers)


def load_checkpoint() -> set:
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f:
            return set(json.load(f).get("completed", []))
    return set()


def save_checkpoint(completed: set):
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"completed": sorted(completed), "last_updated": str(date.today())}, f, indent=2)


def _polygon_ticker(ticker: str) -> str:
    """Convert dash-format dual-class (BRK-B) to dot-format used by Polygon (BRK.B)."""
    if "-" in ticker:
        prefix, _, suffix = ticker.rpartition("-")
        if len(suffix) == 1 and suffix.isalpha():
            return f"{prefix}.{suffix}"
    return ticker


def fetch_ticker_ohlcv(ticker: str) -> pd.DataFrame:
    api_ticker = _polygon_ticker(ticker)
    url = f"{BASE_URL}/v2/aggs/ticker/{api_ticker}/range/1/day/{START_DATE}/{END_DATE}"
    params = {
        "apiKey": POLYGON_KEY,
        "adjusted": "true",
        "sort": "asc",
        "limit": 50000,
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

        next_url = data.get("next_url")
        if not next_url:
            break
        url = next_url
        params = {"apiKey": POLYGON_KEY}
        if page_count > 10:
            print(f"    {ticker} aborting: >10 pages (unexpected for daily 5y)")
            break

    if not all_results:
        return pd.DataFrame()

    df = pd.DataFrame(all_results)
    df["date"] = pd.to_datetime(df["t"], unit="ms").dt.date
    df = df.rename(columns={
        "o": "open", "h": "high", "l": "low", "c": "close",
        "v": "volume", "vw": "vwap", "n": "transactions",
    })
    df["ticker"] = ticker
    df = df[["ticker", "date", "open", "high", "low", "close", "volume", "vwap", "transactions"]]
    df = df.sort_values("date").reset_index(drop=True)
    return df


def main():
    ap = argparse.ArgumentParser(description="Polygon Master Dedup OHLCV prefetch (1937 tickers, vwap+transactions, canonical Sprint 0A path)")
    ap.add_argument("--limit-tickers", type=int, default=None,
                    help="Only fetch first N tickers (alphabetical). For testing.")
    ap.add_argument("--tickers", nargs="+", default=None,
                    help="Explicit ticker list (overrides universe CSV). For smoke.")
    args = ap.parse_args()

    print(f"=== Polygon Master Dedup OHLCV Prefetch (H1 / DEC-609) ===")
    print(f"Universe: {UNIVERSE_CSV}")
    print(f"Output:   {CACHE_DIR}/")
    print(f"Window:   {START_DATE} to {END_DATE} (~5y rolling per Polygon Stocks Starter)")
    if args.tickers:
        print(f"Mode:     EXPLICIT ({len(args.tickers)}: {args.tickers})")
    elif args.limit_tickers:
        print(f"Mode:     LIMITED ({args.limit_tickers} tickers - DEMO)")
    else:
        print(f"Mode:     FULL UNIVERSE (1937 tickers)")
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
        print("[OK] All tickers already cached.")
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
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
