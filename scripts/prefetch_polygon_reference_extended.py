"""scripts/prefetch_polygon_reference_extended.py - extended reference fields (Tier H4).

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08; Tier H4 P2.

Resolves INV-030 — Polygon reference cache was missing address, branding
(logo_url, icon_url), total_employees, phone_number, description,
composite_figi, share_class_figi, round_lot.

Re-fetches /v3/reference/tickers/{ticker} for full Master Universe with
extended field set.

Output: data_prefetch/polygon/reference_extended/{ticker}.parquet
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import date
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

OUT_DIR = Path("data_prefetch/polygon/reference_extended")
TIMEOUT = 30
RATE_LIMIT_SLEEP = 0.05

RESERVED_WIN = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}


def safe_filename_stem(ticker: str) -> str:
    safe = str(ticker).replace("-", "_")
    if safe.upper() in RESERVED_WIN:
        safe = safe + "_"
    return safe


def fetch_extended(ticker: str) -> dict | None:
    api_t = ticker.replace("-", ".") if "-" in ticker and ticker.split("-")[-1].isalpha() else ticker
    url = f"https://api.polygon.io/v3/reference/tickers/{api_t}"
    h = {"Authorization": f"Bearer {POLYGON_KEY}"}
    r = requests.get(url, headers=h, timeout=TIMEOUT)
    if r.status_code != 200:
        return None
    data = r.json().get("results") or {}
    if not data:
        return None
    # Capture ALL returned fields, including nested ones
    out = {
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
        # NEW extended fields (INV-030)
        "phone_number": data.get("phone_number"),
        "description": data.get("description"),
        "total_employees": data.get("total_employees"),
        "composite_figi": data.get("composite_figi"),
        "share_class_figi": data.get("share_class_figi"),
        "round_lot": data.get("round_lot"),
        "address_json": json.dumps(data.get("address", {})) if data.get("address") else None,
        "branding_json": json.dumps(data.get("branding", {})) if data.get("branding") else None,
        "fetched_at": str(date.today()),
    }
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    master = Path("Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv")
    df_uni = pd.read_csv(master, comment="#")
    tickers = sorted(df_uni["Symbol"].dropna().str.strip().str.upper().unique())

    # Resume support
    existing = {f.stem for f in OUT_DIR.glob("*.parquet")}
    remaining = [t for t in tickers if safe_filename_stem(t) not in existing]
    print(f"=== Polygon reference extended prefetch ===")
    print(f"Universe: {len(tickers)}; existing: {len(existing)}; remaining: {len(remaining)}")
    rows = []
    failed = []
    for i, t in enumerate(remaining, 1):
        if i % 100 == 0:
            print(f"  [{i}/{len(remaining)}] (running)")
        try:
            ref = fetch_extended(t)
            if not ref:
                failed.append(t)
                continue
            pd.DataFrame([ref]).to_parquet(
                OUT_DIR / f"{safe_filename_stem(t)}.parquet", index=False
            )
            rows.append(ref)
        except Exception as e:
            failed.append(t)
        time.sleep(RATE_LIMIT_SLEEP)
    if rows:
        # Combined index
        pd.DataFrame(rows).to_parquet(OUT_DIR / "_index.parquet", index=False)
    print(f"\nReference extended: {len(rows)} OK / {len(failed)} failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
