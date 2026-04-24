"""
scripts/prefetch_finnhub_news.py — Pre-fetch Finnhub news sentiment per ticker.

Downloads company news and computes daily sentiment score.
Free tier: 60 calls/minute, ~1 year lookback per call.
Strategy: fetch in annual batches (2022, 2023, 2024) per ticker.

Run from laptop (Codespaces may block Finnhub):
  python scripts/prefetch_finnhub_news.py

Progress saved every 50 tickers — safe to interrupt and resume.
"""

import os
import sys
import time
import json
import requests
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
from backtest.data.universe import get_sp500_constituents, ETFS_FULL

FINNHUB_KEY = os.environ.get("FINNHUB_API_KEY", "")
if not FINNHUB_KEY:
    print("ERROR: FINNHUB_API_KEY not set")
    sys.exit(1)

CACHE_DIR = Path("backtest/data/cache/finnhub_news")
CHECKPOINT_FILE = Path("backtest/data/cache/finnhub_news_checkpoint.json")
RATE_LIMIT_SLEEP = 1.1   # 60 calls/min = 1 per second, use 1.1 for safety
COMMIT_EVERY = 50

# Annual batches — free tier handles ~1 year per call
BATCHES = [
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
]


def fetch_news(ticker: str, from_date: str, to_date: str) -> list:
    url = (
        f"https://finnhub.io/api/v1/company-news"
        f"?symbol={ticker}&from={from_date}&to={to_date}"
        f"&token={FINNHUB_KEY}"
    )
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                return r.json() if r.text.strip() else []
            elif r.status_code == 429:
                print(f"  Rate limited — waiting 60s")
                time.sleep(60)
            else:
                return []
        except Exception as e:
            print(f"  Error (attempt {attempt+1}): {e}")
            time.sleep(10)
    return []


def score_sentiment(headline: str, summary: str) -> float:
    """Simple keyword sentiment scorer — returns -1 (negative) to +1 (positive)."""
    text = f"{headline} {summary}".lower()
    positive = ["beat", "exceed", "strong", "growth", "record", "surge",
                "upgrade", "outperform", "buy", "bullish", "profit", "gain",
                "positive", "raised", "above", "better"]
    negative = ["miss", "below", "weak", "decline", "loss", "cut", "downgrade",
                "underperform", "sell", "bearish", "negative", "warning",
                "concern", "risk", "fall", "drop", "lower", "lawsuit", "fraud"]
    pos = sum(1 for w in positive if w in text)
    neg = sum(1 for w in negative if w in text)
    total = pos + neg
    if total == 0:
        return 0.0
    return (pos - neg) / total


def process_ticker(ticker: str) -> pd.DataFrame:
    """Fetch news for all batches and compute daily sentiment."""
    all_articles = []
    for from_date, to_date in BATCHES:
        articles = fetch_news(ticker, from_date, to_date)
        all_articles.extend(articles)
        time.sleep(RATE_LIMIT_SLEEP)

    if not all_articles:
        return pd.DataFrame()

    rows = []
    for a in all_articles:
        ts = a.get("datetime", 0)
        if not ts:
            continue
        dt = pd.Timestamp(ts, unit="s").date()
        score = score_sentiment(a.get("headline",""), a.get("summary",""))
        rows.append({"date": dt, "sentiment": score, "headline": a.get("headline","")[:100]})

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])

    # Aggregate to daily: mean sentiment + article count
    daily = df.groupby("date").agg(
        sentiment_mean=("sentiment", "mean"),
        article_count=("sentiment", "count")
    ).reset_index()
    return daily


def load_checkpoint() -> list:
    if CHECKPOINT_FILE.exists():
        return json.loads(CHECKPOINT_FILE.read_text())
    return []


def save_checkpoint(done: list):
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(json.dumps(done))


def git_commit(message: str):
    import subprocess
    subprocess.run(["git", "add", "backtest/data/cache/finnhub_news/",
                    "backtest/data/cache/finnhub_news_checkpoint.json"],
                   capture_output=True)
    subprocess.run(["git", "commit", "-m", message], capture_output=True)
    subprocess.run(["git", "push", "origin", "main"], capture_output=True)


def main():
    sp500 = get_sp500_constituents(500)
    universe = list(dict.fromkeys(sp500 + ETFS_FULL))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    done = load_checkpoint()
    remaining = [t for t in universe if t not in done]

    print(f"Finnhub news pre-fetch")
    print(f"Universe: {len(universe)} | Done: {len(done)} | Remaining: {len(remaining)}")
    print(f"Batches: {BATCHES}")
    print()

    batch_count = 0
    for i, ticker in enumerate(remaining):
        df = process_ticker(ticker)
        out_file = CACHE_DIR / f"{ticker.replace('-','_')}.parquet"
        if df.empty:
            pd.DataFrame().to_parquet(out_file)
        else:
            df.to_parquet(out_file, index=False)

        done.append(ticker)
        save_checkpoint(done)
        batch_count += 1

        n = len(df) if not df.empty else 0
        print(f"  [{i+1}/{len(remaining)}] {ticker}: {n} daily sentiment rows")

        if batch_count % COMMIT_EVERY == 0:
            print(f"\n  Committing batch of {COMMIT_EVERY}...")
            git_commit(f"Finnhub news pre-fetch: batch {batch_count//COMMIT_EVERY}")
            print(f"  Committed.\n")

    git_commit(f"Finnhub news pre-fetch: complete ({len(universe)} tickers)")
    print("\nFinnhub news pre-fetch complete.")


if __name__ == "__main__":
    main()
