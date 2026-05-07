"""scripts/prefetch_cftc_cot.py — Pre-fetch CFTC Commitments of Traders for major contracts.

Pass 53 Day-9 v8h Tier C3 (owner-approved 2026-05-07 "All tiers do it now"):
extends single-contract `cot_emini_sp500.parquet` with full coverage of major
financial + commodity contracts.

Sources (public Socrata datasets at data.cftc.gov, no auth required):
  - Traders in Financial Futures (TFF) Combined: dataset ``gpe5-46if`` (equity
    indices, rates, currencies; uses dealer/asset_mgr/lev_money breakdown)
  - Disaggregated COT (DCOT) Combined: dataset ``kh3c-gbw2`` (commodities;
    uses producer/swap_dealer/managed_money/other_reportable breakdown)

Outputs to ``data_prefetch/cftc/<safe_contract_name>.parquet``.

Run:
    python scripts/prefetch_cftc_cot.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
import requests


CFTC_BASE = "https://publicreporting.cftc.gov/resource"
DATASET_TFF = "gpe5-46if"   # Traders in Financial Futures - Combined
DATASET_DCOT = "kh3c-gbw2"  # Disaggregated COT - Combined

OUT_DIR = Path("data_prefetch/cftc")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Map of (label -> {dataset, contract_market_name_filter, slug_for_filename})
CONTRACTS = [
    # ── Equity indices (TFF) ──
    ("emini_sp500",     DATASET_TFF, "E-MINI S&P 500"),
    ("emini_nasdaq100", DATASET_TFF, "E-MINI NASDAQ-100"),
    ("emini_russell2k", DATASET_TFF, "E-MINI RUSSELL 2000"),
    ("emini_dow",       DATASET_TFF, "E-MINI DJIA (X $5)"),
    ("vix_futures",     DATASET_TFF, "VIX FUTURES"),
    # ── Rates (TFF) ──
    ("treasury_10y",    DATASET_TFF, "10-YEAR U.S. TREASURY NOTES"),
    ("treasury_5y",     DATASET_TFF, "5-YEAR U.S. TREASURY NOTES"),
    ("treasury_2y",     DATASET_TFF, "2-YEAR U.S. TREASURY NOTES"),
    ("ultra_treasury",  DATASET_TFF, "ULTRA U.S. TREASURY BONDS"),
    ("fed_funds_30d",   DATASET_TFF, "FED FUNDS"),
    # ── Currencies (TFF) ──
    ("dxy_dollar_idx",  DATASET_TFF, "USD INDEX"),
    ("eur_usd",         DATASET_TFF, "EURO FX"),
    ("jpy_usd",         DATASET_TFF, "JAPANESE YEN"),
    # ── Commodities (DCOT) ──
    ("wti_crude",       DATASET_DCOT, "CRUDE OIL, LIGHT SWEET-WTI"),
    ("gold",            DATASET_DCOT, "GOLD"),
    ("silver",          DATASET_DCOT, "SILVER"),
    ("natural_gas",     DATASET_DCOT, "NAT GAS NYME"),
    ("copper",          DATASET_DCOT, "COPPER- #1"),
]


def fetch_contract(dataset: str, contract_filter: str,
                    limit_per_page: int = 50000) -> pd.DataFrame:
    """Fetch all rows for a contract via Socrata API.

    Uses ``$where`` filter on contract_market_name (case-insensitive contains).
    Paginates via $offset. Public Socrata datasets allow up to 50k rows per
    request without auth.

    Pass 53 Day-9 v8h fix: use requests `params=` for proper URL encoding
    (handles & / # / spaces in contract names safely).
    """
    rows = []
    offset = 0
    while True:
        url = f"{CFTC_BASE}/{dataset}.json"
        params = {
            "$where": f"upper(contract_market_name) like '%{contract_filter.upper()}%'",
            "$limit": limit_per_page,
            "$offset": offset,
            "$order": "report_date_as_yyyy_mm_dd",
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        page = r.json()
        if not page:
            break
        rows.extend(page)
        if len(page) < limit_per_page:
            break
        offset += limit_per_page
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if "report_date_as_yyyy_mm_dd" in df.columns:
        df["report_date"] = pd.to_datetime(
            df["report_date_as_yyyy_mm_dd"], errors="coerce"
        ).dt.date
    return df


def main():
    print(f"Fetching {len(CONTRACTS)} CFTC contracts to {OUT_DIR}/")
    print()
    success_count = 0
    fail_count = 0
    for slug, dataset, contract_filter in CONTRACTS:
        out_path = OUT_DIR / f"cot_{slug}.parquet"
        try:
            df = fetch_contract(dataset, contract_filter)
            if df.empty:
                print(f"  [SKIP] {slug} ({contract_filter}): no rows returned "
                      f"— check filter")
                fail_count += 1
                continue
            df.to_parquet(out_path, index=False)
            print(f"  [OK] {slug} ({contract_filter}): {len(df)} rows -> "
                  f"{out_path.name}")
            success_count += 1
        except Exception as exc:
            print(f"  [FAIL] {slug} ({contract_filter}): {type(exc).__name__}: {exc}")
            fail_count += 1
        time.sleep(0.2)  # courtesy rate limit
    print()
    print(f"CFTC prefetch complete: {success_count} OK, {fail_count} failed.")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
