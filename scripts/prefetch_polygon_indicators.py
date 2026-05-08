"""scripts/prefetch_polygon_indicators.py - precomputed indicators (Tier H6).

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08; Tier H6 P2.

Probe-confirmed: /v1/indicators/{sma|ema|rsi|macd}/{ticker} returns Polygon's
own precomputed values. Useful as a sanity-check vs our locally computed
indicators (signals/technical.py) and as alternate source.

Output: data_prefetch/polygon/indicators/{indicator}/{ticker}.parquet

Stocks Starter unlimited rate; small commit-every-100 batches.
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

CACHE_ROOT = Path("data_prefetch/polygon/indicators")
CHECKPOINT_FILE = CACHE_ROOT / "_checkpoint.json"
TIMEOUT = 30
RATE_LIMIT_SLEEP = 0.05

RESERVED_WIN = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}


def safe_filename_stem(ticker: str) -> str:
    safe = str(ticker).replace("-", "_")
    if safe.upper() in RESERVED_WIN:
        safe = safe + "_"
    return safe


# Indicators to fetch with default windows
INDICATORS = [
    ("sma_50", "sma", {"window": 50}),
    ("sma_200", "sma", {"window": 200}),
    ("ema_20", "ema", {"window": 20}),
    ("ema_50", "ema", {"window": 50}),
    ("rsi_14", "rsi", {"window": 14}),
    ("macd", "macd", {"short_window": 12, "long_window": 26, "signal_window": 9}),
]


def fetch_indicator(ticker: str, indicator: str, params: dict) -> pd.DataFrame:
    api_t = ticker
    if "-" in ticker and ticker.split("-")[-1].isalpha() and len(ticker.split("-")[-1]) == 1:
        api_t = ticker.replace("-", ".")
    url = f"https://api.polygon.io/v1/indicators/{indicator}/{api_t}"
    h = {"Authorization": f"Bearer {POLYGON_KEY}"}
    p = {
        "timestamp.gte": "2020-01-01",
        "timespan": "day",
        "series_type": "close",
        "limit": 5000,
        **params,
    }
    r = requests.get(url, headers=h, params=p, timeout=TIMEOUT)
    if r.status_code != 200:
        return pd.DataFrame()
    data = r.json().get("results", {}) or {}
    values = data.get("values", []) or []
    if not values:
        return pd.DataFrame()
    df = pd.DataFrame(values)
    if "timestamp" in df.columns:
        df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date
        df = df.drop(columns=["timestamp"])
    return df


def load_checkpoint() -> dict:
    if CHECKPOINT_FILE.exists():
        try:
            return json.loads(CHECKPOINT_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_checkpoint(cp: dict) -> None:
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(json.dumps(cp))


def git_commit_paths(message: str, paths: list[str]) -> None:
    import subprocess
    for p in paths:
        subprocess.run(["git", "add", "--", p], capture_output=True)
    result = subprocess.run(["git", "commit", "-m", message] + ["--"] + paths,
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
        master = Path("Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv")
        df_uni = pd.read_csv(master, comment="#")
        tickers = sorted(df_uni["Symbol"].dropna().str.strip().str.upper().unique())

    cp = load_checkpoint()
    print(f"=== Polygon indicators prefetch ({len(INDICATORS)} indicators x {len(tickers)} tickers) ===")

    for label, kind, params in INDICATORS:
        out_dir = CACHE_ROOT / label
        out_dir.mkdir(parents=True, exist_ok=True)
        done = set(cp.get(label, []))
        remaining = [t for t in tickers if t not in done]
        print(f"\n--- {label} --- {len(remaining)} remaining / {len(tickers)}")
        batch_count = 0
        for i, ticker in enumerate(remaining, 1):
            if i % 100 == 0:
                print(f"  [{i}/{len(remaining)}] {ticker}")
            try:
                df = fetch_indicator(ticker, kind, params)
                out = out_dir / f"{safe_filename_stem(ticker)}.parquet"
                if df.empty:
                    pd.DataFrame().to_parquet(out)
                else:
                    df.to_parquet(out, index=False)
                cp.setdefault(label, []).append(ticker)
                save_checkpoint(cp)
                batch_count += 1
                if not args.no_git and batch_count % args.batch_size == 0:
                    git_commit_paths(
                        f"Polygon indicators: {label} batch {batch_count // args.batch_size}",
                        [str(out_dir), str(CHECKPOINT_FILE)],
                    )
            except Exception:
                pass
            time.sleep(RATE_LIMIT_SLEEP)

        if not args.no_git and batch_count > 0:
            git_commit_paths(f"Polygon indicators: {label} final ({batch_count})",
                              [str(out_dir), str(CHECKPOINT_FILE)])
        print(f"  {label} done: {len(cp.get(label, []))}")

    print("\nIndicators prefetch complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
