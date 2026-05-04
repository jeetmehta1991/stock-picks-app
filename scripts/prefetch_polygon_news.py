"""
scripts/prefetch_polygon_news.py — Pre-fetch Polygon news for Sprint 1 universe.

Per DEC-440 (Polygon news supersedes Finnhub) + DEC-453 (Finnhub deprecated).

Cache: backtest/data/cache/polygon/news/{TICKER}.parquet
Each row: published_utc, ticker, title, description, article_url, publisher, sentiment, insights

Run from laptop:
  python scripts/prefetch_polygon_news.py

Estimated wall time: ~3-5 hours for 484 tickers (news endpoint paginates heavily).

Progress: checkpoint saved every 25 tickers.
"""

import os
import sys
import time
import json
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

sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "https://api.polygon.io"
CACHE_DIR = Path("backtest/data/cache/polygon/news")
CHECKPOINT_FILE = Path("backtest/data/cache/polygon/_checkpoint_news.json")
UNIVERSE_CSV = Path("backtest/data/sp500_tickers.csv")

# 5y window per DEC-482
END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=5 * 365 + 30)

RATE_LIMIT_SLEEP = 0.05
TIMEOUT = 60
COMMIT_EVERY = 25
MAX_PAGES_PER_TICKER = 50  # safety cap; 50 × 1000 = 50k articles per ticker max


def load_universe() -> list[str]:
    df = pd.read_csv(UNIVERSE_CSV)
    return sorted(df["Symbol"].dropna().str.strip().str.upper().unique().tolist())


def load_checkpoint() -> set:
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f:
            return set(json.load(f).get("completed", []))
    return set()


def save_checkpoint(completed: set):
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"completed": sorted(completed), "last_updated": str(date.today())}, f, indent=2)


def fetch_news_for_ticker(ticker: str) -> pd.DataFrame:
    """Fetch all news for ticker in our 5y window, paginated."""
    url = f"{BASE_URL}/v2/reference/news"
    params = {
        "apiKey": POLYGON_KEY,
        "ticker": ticker,
        "published_utc.gte": str(START_DATE),
        "published_utc.lte": str(END_DATE),
        "limit": 1000,
        "order": "asc",
        "sort": "published_utc",
    }
    all_articles = []
    page = 0
    while True:
        page += 1
        try:
            r = requests.get(url, params=params, timeout=TIMEOUT)
        except requests.RequestException as e:
            print(f" page {page} failed: {e}", end="")
            break
        if r.status_code != 200:
            print(f" HTTP {r.status_code}", end="")
            break
        data = r.json()
        articles = data.get("results", []) or []
        all_articles.extend(articles)
        next_url = data.get("next_url")
        if not next_url:
            break
        url = next_url
        params = {"apiKey": POLYGON_KEY}
        if page >= MAX_PAGES_PER_TICKER:
            print(f" capped@{MAX_PAGES_PER_TICKER}p", end="")
            break
        time.sleep(RATE_LIMIT_SLEEP)

    if not all_articles:
        return pd.DataFrame()

    # Flatten to columns we care about
    rows = []
    for a in all_articles:
        # Extract this ticker's per-ticker insight if present
        insights = a.get("insights", []) or []
        ticker_insight = next((i for i in insights if i.get("ticker") == ticker), {})
        rows.append({
            "ticker": ticker,
            "id": a.get("id"),
            "published_utc": a.get("published_utc"),
            "title": a.get("title"),
            "description": a.get("description"),
            "article_url": a.get("article_url"),
            "amp_url": a.get("amp_url"),
            "publisher_name": (a.get("publisher") or {}).get("name"),
            "publisher_homepage_url": (a.get("publisher") or {}).get("homepage_url"),
            "sentiment": ticker_insight.get("sentiment"),  # positive / negative / neutral
            "sentiment_reasoning": ticker_insight.get("sentiment_reasoning"),
            "all_tickers": ",".join(a.get("tickers", []) or []),
        })

    df = pd.DataFrame(rows)
    df["published_utc"] = pd.to_datetime(df["published_utc"], errors="coerce", utc=True)
    df = df.sort_values("published_utc").reset_index(drop=True)
    return df


def main():
    print(f"=== Polygon News Prefetch ===")
    print(f"Window: {START_DATE} to {END_DATE}")
    print(f"Output: {CACHE_DIR}/")
    print()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tickers = load_universe()
    completed = load_checkpoint()
    todo = [t for t in tickers if t not in completed]

    print(f"Total: {len(tickers)} | Done: {len(completed)} | Todo: {len(todo)}")
    print()

    if not todo:
        print("✅ All news already cached.")
        return 0

    failures = []
    success = 0
    start_ts = time.time()

    for i, ticker in enumerate(todo, 1):
        print(f"[{i}/{len(todo)}] {ticker} ", end="", flush=True)
        df = fetch_news_for_ticker(ticker)
        if df.empty:
            print("(0 articles)")
            # Even 0 articles is a success — just no news for this ticker
            completed.add(ticker)
            continue
        out_path = CACHE_DIR / f"{ticker}.parquet"
        df.to_parquet(out_path, compression="snappy", index=False)
        print(f"{len(df)} articles, {out_path.stat().st_size/1024:.1f} KB")
        completed.add(ticker)
        success += 1

        if success % COMMIT_EVERY == 0:
            save_checkpoint(completed)
            elapsed = time.time() - start_ts
            rate = i / elapsed
            eta = (len(todo) - i) / rate
            print(f"  -- checkpoint ({len(completed)}/{len(tickers)}) | rate {rate:.2f} t/s | ETA {eta/60:.1f}min --")

        time.sleep(RATE_LIMIT_SLEEP)

    save_checkpoint(completed)
    elapsed = time.time() - start_ts
    total_size = sum(p.stat().st_size for p in CACHE_DIR.glob("*.parquet")) / (1024**2)
    print()
    print(f"News prefetch: {success} tickers with articles in {elapsed/60:.1f} min")
    print(f"Cache size: {total_size:.1f} MB")
    print(f"Failures: {failures[:20] if failures else 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
