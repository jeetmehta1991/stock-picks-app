"""
scripts/prefetch_alphavantage_news.py — Pre-fetch Alpha Vantage News & Sentiment.

Replaces Finnhub news pre-fetch. Alpha Vantage provides:
- Full historical news back to 2022 (confirmed)
- AI-powered sentiment scores per article (not keyword-based)
- Per-ticker filtering with date ranges
- Free tier: 25 calls/minute, 500/day
- Already used in Stage 1 — no new account needed

Download structure: per ticker, annual batches (2022, 2023, 2024, 2025, 2026)
Output: Parquet per ticker with daily aggregated sentiment

Run from GitHub Actions (use ALPHAVANTAGE_API_KEY secret):
  Batch 1: tickers 1-127
  Batch 2: tickers 128-254
  Batch 3: tickers 255-381
  Batch 4: tickers 382-509
"""

import os
import sys
import time
import json
import argparse
import requests
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from backtest.data.universe import get_sp500_constituents, ETFS_FULL

AV_KEY = os.environ.get("ALPHAVANTAGE_API_KEY", "")
if not AV_KEY:
    print("ERROR: ALPHAVANTAGE_API_KEY not set")
    sys.exit(1)

CACHE_DIR    = Path("backtest/data/cache/av_news")
CHECKPOINT_F = Path("backtest/data/cache/av_news_checkpoint.json")
COMMIT_EVERY = 25       # commit every 25 tickers — smaller batches for reliability
RATE_SLEEP   = 13.0     # 25 calls/min = 1 per 2.4s — use 13s for safety (5/min)

# Annual date ranges to fetch
ANNUAL_BATCHES = [
    ("20220101T0000", "20221231T2359"),
    ("20230101T0000", "20231231T2359"),
    ("20240101T0000", "20241231T2359"),
    ("20250101T0000", "20251231T2359"),
    ("20260101T0000", "20260331T2359"),
]

SENTIMENT_LABEL_SCORE = {
    "Bullish":          1.0,
    "Somewhat-Bullish": 0.5,
    "Neutral":          0.0,
    "Somewhat-Bearish": -0.5,
    "Bearish":         -1.0,
}


def fetch_news(ticker: str, time_from: str, time_to: str) -> list:
    """Fetch news articles from Alpha Vantage for a ticker and date range."""
    url = "https://www.alphavantage.co/query"
    params = {
        "function":  "NEWS_SENTIMENT",
        "tickers":   ticker,
        "time_from": time_from,
        "time_to":   time_to,
        "limit":     1000,
        "apikey":    AV_KEY,
    }
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, timeout=20)
            if r.status_code == 200:
                data = r.json()
                if "Information" in data:
                    # Rate limit hit
                    print(f"  Rate limit — waiting 60s")
                    time.sleep(60)
                    continue
                return data.get("feed", [])
            else:
                print(f"  HTTP {r.status_code} — retrying")
                time.sleep(15)
        except Exception as e:
            print(f"  Error (attempt {attempt+1}): {e}")
            time.sleep(15)
    return []


def process_ticker(ticker: str) -> pd.DataFrame:
    """Fetch all years of news for ticker and aggregate to daily sentiment."""
    all_rows = []

    for time_from, time_to in ANNUAL_BATCHES:
        articles = fetch_news(ticker, time_from, time_to)
        year = time_from[:4]
        print(f"    {year}: {len(articles)} articles", end=" | ")

        for article in articles:
            # Use Alpha Vantage AI sentiment score directly
            overall_score = article.get("overall_sentiment_score", 0.0)
            overall_label = article.get("overall_sentiment_label", "Neutral")

            # Also get ticker-specific sentiment if available
            ticker_sentiment = 0.0
            for ts in article.get("ticker_sentiment", []):
                if ts.get("ticker") == ticker:
                    ticker_sentiment = float(ts.get("ticker_sentiment_score", overall_score))
                    break

            # Parse timestamp
            time_published = article.get("time_published", "")
            if not time_published:
                continue
            try:
                dt = pd.to_datetime(time_published, format="%Y%m%dT%H%M%S")
            except Exception:
                continue

            all_rows.append({
                "date":             dt.date(),
                "overall_score":    float(overall_score or 0),
                "ticker_score":     float(ticker_sentiment or overall_score or 0),
                "label":            overall_label,
                "relevance_score":  float(article.get("relevance_score", 0) or 0),
            })

        time.sleep(RATE_SLEEP)

    print()
    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df["date"] = pd.to_datetime(df["date"])

    # Weight by relevance score — more relevant articles count more
    df["weighted_score"] = df["ticker_score"] * df["relevance_score"].clip(0, 1)

    # Aggregate to daily
    daily = df.groupby("date").agg(
        sentiment_mean   = ("ticker_score", "mean"),
        sentiment_weighted = ("weighted_score", "sum"),
        article_count    = ("ticker_score", "count"),
        bullish_count    = ("label", lambda x: (x.isin(["Bullish","Somewhat-Bullish"])).sum()),
        bearish_count    = ("label", lambda x: (x.isin(["Bearish","Somewhat-Bearish"])).sum()),
        max_relevance    = ("relevance_score", "max"),
    ).reset_index()

    daily["sentiment_direction"] = daily.apply(
        lambda r: "bullish" if r.bullish_count > r.bearish_count
                  else "bearish" if r.bearish_count > r.bullish_count
                  else "neutral", axis=1
    )

    return daily


def load_checkpoint(batch: int = 0) -> list:
    key = f"batch_{batch}" if batch > 0 else "all"
    if CHECKPOINT_F.exists():
        try:
            data = json.loads(CHECKPOINT_F.read_text())
            if isinstance(data, dict):
                return data.get(key, [])
        except Exception:
            pass
    return []


def save_checkpoint(done: list, batch: int = 0):
    key = f"batch_{batch}" if batch > 0 else "all"
    existing = {}
    if CHECKPOINT_F.exists():
        try:
            existing = json.loads(CHECKPOINT_F.read_text())
            if not isinstance(existing, dict):
                existing = {}
        except Exception:
            pass
    existing[key] = done
    CHECKPOINT_F.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_F.write_text(json.dumps(existing))


def git_commit(message: str):
    import subprocess
    subprocess.run(["git", "add",
                    "backtest/data/cache/av_news/",
                    "backtest/data/cache/av_news_checkpoint.json"],
                   capture_output=True)
    result = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True)
    if "nothing to commit" in result.stdout:
        return
    subprocess.run(["git", "pull", "--rebase", "origin", "main"], capture_output=True)
    subprocess.run(["git", "push", "origin", "main"], capture_output=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=0,
                        help="Batch 1-4 for GitHub Actions (0=all)")
    args = parser.parse_args()

    sp500   = get_sp500_constituents(500)
    universe = list(dict.fromkeys(sp500 + ETFS_FULL))

    if args.batch > 0:
        batch_size = len(universe) // 4 + 1
        start = (args.batch - 1) * batch_size
        end   = min(args.batch * batch_size, len(universe))
        universe = universe[start:end]
        print(f"Batch {args.batch}/4: tickers {start+1}-{end} ({len(universe)} tickers)")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    done      = load_checkpoint(args.batch)
    remaining = [t for t in universe if t not in done]

    print(f"Alpha Vantage News pre-fetch")
    print(f"Universe: {len(universe)} | Done: {len(done)} | Remaining: {len(remaining)}")
    print(f"Years: {[b[0][:4] for b in ANNUAL_BATCHES]}")
    print(f"Rate: {RATE_SLEEP}s between calls (~5/min, safe for 25/min limit)")
    print()

    batch_count = 0
    for i, ticker in enumerate(remaining):
        print(f"[{i+1}/{len(remaining)}] {ticker}:")
        df = process_ticker(ticker)

        out_file = CACHE_DIR / f"{ticker.replace('-','_').replace('.','_')}.parquet"
        if df.empty:
            pd.DataFrame().to_parquet(out_file)
        else:
            df.to_parquet(out_file, index=False)

        done.append(ticker)
        save_checkpoint(done, args.batch)
        batch_count += 1

        n = len(df) if not df.empty else 0
        print(f"  → {n} daily rows saved")

        if batch_count % COMMIT_EVERY == 0:
            print(f"\n  Committing batch of {COMMIT_EVERY}...")
            git_commit(f"AV news batch {args.batch}: {batch_count} tickers done")
            print(f"  Committed.\n")

    git_commit(f"AV news batch {args.batch}: complete ({len(universe)} tickers)")
    print(f"\nDone. {len(done)} tickers complete.")


if __name__ == "__main__":
    main()
