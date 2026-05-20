"""Prefetch CNN Fear & Greed Index (Batch 259 - INV-021 orphan resolution).

Source: https://production.dataviz.cnn.io/index/fearandgreed/graphdata
(CNN's public dataviz API; no auth required; per CHECKLIST #77 canonical
source declaration).

Resolves INV-021 orphan cache: data_prefetch/cnn_fg/ was populated by some
prior mechanism but no canonical prefetch script existed. This script
authors the canonical fetch path so refresh becomes reproducible.

Cache:
  data_prefetch/cnn_fg/daily.parquet         - composite Fear & Greed score
                                                + rating (timestamp, score
                                                rating, date)
  data_prefetch/cnn_fg/daily_legacy.parquet  - extended history (older API
                                                schema preserved)
  data_prefetch/cnn_fg/components/<name>.parquet  - 7 sub-components
                                                (Market Momentum, Stock Price
                                                Strength, Put/Call, Junk Bond
                                                Demand, Market Volatility,
                                                Stock Price Breadth, Safe
                                                Haven Demand)

Usage:
  python scripts/prefetch_cnn_fg.py
  python scripts/prefetch_cnn_fg.py --output-dir custom/path/

Owner directive 2026-05-19: INV-021 orphan cleanup; codify canonical
prefetch + add to .github/workflows for periodic refresh.
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO / "data_prefetch" / "cnn_fg"

# CNN dataviz endpoint (verified accessible via probe 2026-05-20)
CNN_FG_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

# 7 sub-component keys per CNN's spec
SUB_COMPONENTS = [
    "market_momentum_sp500",
    "stock_price_strength",
    "stock_price_breadth",
    "put_call_options",
    "market_volatility_vix",
    "junk_bond_demand",
    "safe_haven_demand",
]


def fetch_cnn_fg(timeout: int = 30) -> dict:
    """Fetch raw JSON from CNN endpoint with retry."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; stock-picks-app/1.0)",
        "Accept": "application/json",
    }
    for attempt in range(3):
        try:
            r = requests.get(CNN_FG_URL, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as exc:
            if attempt == 2:
                raise
            print(f"[WARN] attempt {attempt + 1} failed ({exc}); retry in 5s")
            time.sleep(5)
    return {}


def parse_daily(data: dict) -> pd.DataFrame:
    """Parse the composite daily Fear & Greed score history."""
    fg = data.get("fear_and_greed_historical", {})
    items = fg.get("data", [])
    rows = []
    for item in items:
        ts = item.get("x")
        score = item.get("y")
        rating = item.get("rating")
        if ts is None or score is None:
            continue
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).date()
        rows.append({
            "timestamp": int(ts),
            "score":     float(score),
            "rating":    str(rating) if rating else "",
            "date":      str(dt),
        })
    return pd.DataFrame(rows)


def parse_component(data: dict, key: str) -> pd.DataFrame:
    """Parse a sub-component history (key in CNN response keys)."""
    comp = data.get(key, {})
    items = comp.get("data", [])
    rows = []
    for item in items:
        ts = item.get("x")
        score = item.get("y")
        rating = item.get("rating")
        if ts is None or score is None:
            continue
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).date()
        rows.append({
            "timestamp": int(ts),
            "score":     float(score),
            "rating":    str(rating) if rating else "",
            "date":      str(dt),
        })
    return pd.DataFrame(rows)


def main() -> int:
    p = argparse.ArgumentParser(description="Prefetch CNN Fear & Greed Index")
    p.add_argument("--output-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--dry-run", action="store_true",
                   help="Fetch + parse; don't write to disk")
    args = p.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Fetching CNN F&G from {CNN_FG_URL}")
    try:
        data = fetch_cnn_fg()
    except Exception as exc:
        print(f"[ERROR] fetch failed: {exc}")
        return 1

    daily_df = parse_daily(data)
    print(f"[INFO] Composite daily: {len(daily_df)} rows")

    components_dir = out_dir / "components"
    components_dir.mkdir(parents=True, exist_ok=True)
    comp_counts = {}
    for comp_key in SUB_COMPONENTS:
        df = parse_component(data, comp_key)
        comp_counts[comp_key] = len(df)
        if not args.dry_run and not df.empty:
            (components_dir / f"{comp_key}.parquet").write_text  # no-op; use to_parquet
            df.to_parquet(components_dir / f"{comp_key}.parquet", index=False)
    print(f"[INFO] Sub-components: {comp_counts}")

    if args.dry_run:
        print("[DRY RUN] Skipped writes")
        return 0

    if not daily_df.empty:
        daily_df.to_parquet(out_dir / "daily.parquet", index=False)
        print(f"[OK] wrote {out_dir.relative_to(REPO)}/daily.parquet ({len(daily_df)} rows)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
