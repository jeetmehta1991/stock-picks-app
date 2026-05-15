"""
scripts/prefetch_polygon_prev_related.py — Polygon /prev + /related-companies.

Source of truth: API_ENDPOINT_INVENTORY.md section 1 (Polygon Stocks Starter),
rows tagged "NEW - daily previous-close capture" + "NEW - peer-companies signal".

Per owner directive 2026-05-15 ("prefetch everything"), this batch fetches:
  - /v2/aggs/ticker/{t}/prev      -> data_prefetch/polygon/prev/{TICKER}.parquet
  - /v1/related-companies/{t}     -> data_prefetch/polygon/related_companies/{TICKER}.parquet

Reads Master Universe Deduplicated CSV (1937 tickers).
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

POLYGON_KEY = os.environ.get("POLYGON_API_KEY", "")
if not POLYGON_KEY:
    print("ERROR: POLYGON_API_KEY not set")
    sys.exit(1)

BASE = "https://api.polygon.io"
PREV_DIR = Path("data_prefetch/polygon/prev")
RELATED_DIR = Path("data_prefetch/polygon/related_companies")
PREV_DIR.mkdir(parents=True, exist_ok=True)
RELATED_DIR.mkdir(parents=True, exist_ok=True)
UNIVERSE_CSV = Path("Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv")
RATE_LIMIT_SLEEP = 0.05
TIMEOUT = 30


def _polygon_ticker(t: str) -> str:
    if "-" in t:
        prefix, _, suffix = t.rpartition("-")
        if len(suffix) == 1 and suffix.isalpha():
            return f"{prefix}.{suffix}"
    return t


def load_universe() -> list[str]:
    if not UNIVERSE_CSV.exists():
        raise SystemExit(f"missing universe: {UNIVERSE_CSV}")
    df = pd.read_csv(UNIVERSE_CSV, comment="#")
    col = "Symbol" if "Symbol" in df.columns else df.columns[0]
    return sorted(df[col].dropna().astype(str).unique().tolist())


def fetch_prev(ticker: str) -> dict | None:
    api_t = _polygon_ticker(ticker)
    try:
        r = requests.get(f"{BASE}/v2/aggs/ticker/{api_t}/prev",
                         params={"apiKey": POLYGON_KEY}, timeout=TIMEOUT)
        if r.status_code != 200:
            return None
        d = r.json()
        results = d.get("results") or []
        if not results:
            return None
        row = results[0]
        return {"ticker": ticker, **row}
    except Exception:
        return None


def fetch_related(ticker: str) -> list[dict] | None:
    api_t = _polygon_ticker(ticker)
    try:
        r = requests.get(f"{BASE}/v1/related-companies/{api_t}",
                         params={"apiKey": POLYGON_KEY}, timeout=TIMEOUT)
        if r.status_code != 200:
            return None
        d = r.json()
        results = d.get("results") or []
        return [{"ticker": ticker, "related_ticker": x.get("ticker")} for x in results]
    except Exception:
        return None


def main() -> int:
    tickers = load_universe()
    print(f"Polygon /prev + /related-companies for {len(tickers)} tickers")
    prev_ok = related_ok = 0
    prev_skip = related_skip = 0
    for i, t in enumerate(tickers, 1):
        # /prev
        p_path = PREV_DIR / f"{t}.parquet"
        if not p_path.exists():
            row = fetch_prev(t)
            if row:
                pd.DataFrame([row]).to_parquet(p_path, compression="snappy", index=False)
                prev_ok += 1
            time.sleep(RATE_LIMIT_SLEEP)
        else:
            prev_skip += 1

        # /related-companies
        r_path = RELATED_DIR / f"{t}.parquet"
        if not r_path.exists():
            rows = fetch_related(t)
            if rows is not None:
                pd.DataFrame(rows).to_parquet(r_path, compression="snappy", index=False)
                related_ok += 1
            time.sleep(RATE_LIMIT_SLEEP)
        else:
            related_skip += 1

        if i % 100 == 0:
            print(f"  {i}/{len(tickers)}  prev: {prev_ok} new + {prev_skip} skip  related: {related_ok} new + {related_skip} skip")

    print(f"DONE  prev: {prev_ok} new / {prev_skip} skip  related: {related_ok} new / {related_skip} skip")
    return 0


if __name__ == "__main__":
    sys.exit(main())
