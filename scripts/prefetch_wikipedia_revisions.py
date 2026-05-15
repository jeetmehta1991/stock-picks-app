"""
scripts/prefetch_wikipedia_revisions.py - Wikipedia article revision history.

Source of truth: API_ENDPOINT_INVENTORY.md section 19 (Wikipedia Pageviews),
row tagged "Article revision history -- NEW - content-volatility proxy (P2)".

Per owner directive 2026-05-15 "prefetch everything irrespective of use".

We re-use the article title mapping already established by data_prefetch/
wikipedia/<TICKER>.parquet (article column). For each ticker, fetch the
most recent rvlimit=500 revisions and cache per-ticker.

Endpoint: https://en.wikipedia.org/w/api.php
  ?action=query&prop=revisions&titles=<title>&rvlimit=500
  &rvprop=timestamp|user|comment|size|sha1&format=json

Wikipedia REST is unauthenticated free. Politeness: 0.5s between calls
+ User-Agent identifying our project per Wikimedia API etiquette.

Output: data_prefetch/wikipedia_revisions/<TICKER>.parquet
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
import requests

CACHE = Path("data_prefetch/wikipedia_revisions")
CACHE.mkdir(parents=True, exist_ok=True)
PAGEVIEWS_DIR = Path("data_prefetch/wikipedia")
RATE_LIMIT_SLEEP = 0.5
TIMEOUT = 30
HEADERS = {"User-Agent": "stock-picks-app/0.1 (research; github.com/jeetmehta1991/stock-picks-app)"}


def article_for_ticker(ticker: str) -> str | None:
    """Read the ticker's pageviews parquet to recover the Wikipedia article title."""
    p = PAGEVIEWS_DIR / f"{ticker}.parquet"
    if not p.exists():
        return None
    df = pd.read_parquet(p, columns=["article"])
    if df.empty:
        return None
    return df["article"].iloc[0]


def fetch_revisions(title: str) -> list[dict]:
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvlimit": 500,
        "rvprop": "timestamp|user|comment|size|sha1",
        "format": "json",
        "formatversion": 2,
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", [])
    if not pages:
        return []
    revs = pages[0].get("revisions") or []
    return [{**rev, "article": title} for rev in revs]


def main() -> int:
    # Use the same ticker list as the pageviews cache
    tickers = sorted([p.stem for p in PAGEVIEWS_DIR.glob("*.parquet")])
    print(f"Wikipedia revisions for {len(tickers)} tickers")
    ok = empty = err = skip = 0
    for i, t in enumerate(tickers, 1):
        out_path = CACHE / f"{t}.parquet"
        if out_path.exists():
            skip += 1
            continue
        title = article_for_ticker(t)
        if not title:
            empty += 1
            pd.DataFrame().to_parquet(out_path, compression="snappy", index=False)
            continue
        try:
            revs = fetch_revisions(title)
        except Exception as e:
            err += 1
            if i % 25 == 0:
                print(f"  [{i}/{len(tickers)}] {t} ERR: {e}")
            time.sleep(RATE_LIMIT_SLEEP)
            continue
        if not revs:
            empty += 1
        else:
            ok += 1
        df = pd.DataFrame(revs)
        df.to_parquet(out_path, compression="snappy", index=False)
        if i % 50 == 0:
            print(f"  {i}/{len(tickers)} ok={ok} empty={empty} err={err} skip={skip}")
        time.sleep(RATE_LIMIT_SLEEP)

    print(f"DONE  ok={ok} empty={empty} err={err} skip={skip}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
