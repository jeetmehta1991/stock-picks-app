"""scripts/prefetch_cftc_extended.py - 5 missing CFTC datasets (Tier H18).

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08; Tier H18 P2.

Extends existing prefetch_cftc_cot.py (Disagg combined kh3c-gbw2 + TFF
futures-only gpe5-46if) with the 5 missing public Socrata datasets:

  Legacy Futures Only        : 6dca-aqww
  Legacy Combined            : jun7-fc8e
  Disaggregated Futures Only : 72hh-3qpy
  TFF Combined               : yw9f-hn96
  Supplemental CIT           : 4zgm-a668

Same ~19 contracts as prefetch_cftc_cot.py; output namespaced per dataset
to avoid clobber: data_prefetch/cftc/{dataset_label}/{contract_label}.parquet
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
import requests


CFTC_BASE = "https://publicreporting.cftc.gov/resource"

DATASETS = {
    "legacy_futures":   ("6dca-aqww", "Legacy Futures Only"),
    "legacy_combined":  ("jun7-fc8e", "Legacy Combined"),
    "disagg_futures":   ("72hh-3qpy", "Disaggregated Futures Only"),
    "tff_combined":     ("yw9f-hn96", "TFF Combined"),
    "supp_cit":         ("4zgm-a668", "Supplemental CIT"),
}

# Reuse same contract names as the original CFTC script
CONTRACTS = [
    ("emini_sp500",     "E-MINI S&P 500"),
    ("emini_nasdaq100", "E-MINI NASDAQ-100"),
    ("emini_russell2k", "E-MINI RUSSELL 2000"),
    ("vix_futures",     "VIX FUTURES"),
    ("treasury_10y",    "UST 10Y NOTE"),
    ("treasury_5y",     "UST 5Y NOTE"),
    ("treasury_2y",     "UST 2Y NOTE"),
    ("ust_bond",        "UST BOND"),
    ("ultra_treasury",  "ULTRA UST BOND"),
    ("fed_funds_30d",   "FED FUNDS"),
    ("dxy_dollar_idx",  "USD INDEX"),
    ("eur_usd",         "EURO FX"),
    ("jpy_usd",         "JAPANESE YEN"),
    ("wti_crude",       "CRUDE OIL, LIGHT SWEET-WTI"),
    ("gold",            "GOLD"),
    ("silver",          "SILVER"),
    ("natural_gas",     "NAT GAS NYME"),
    ("copper",          "COPPER- #1"),
]


def fetch_contract(dataset_id: str, contract_filter: str,
                    limit: int = 50000) -> pd.DataFrame:
    rows = []
    offset = 0
    while True:
        url = f"{CFTC_BASE}/{dataset_id}.json"
        params = {
            "$where": f"upper(contract_market_name) like '%{contract_filter.upper()}%'",
            "$limit": limit,
            "$offset": offset,
        }
        try:
            r = requests.get(url, params=params, timeout=30)
        except Exception as e:
            print(f"    error: {e}")
            break
        if r.status_code != 200:
            print(f"    HTTP {r.status_code}")
            break
        page = r.json()
        if not page:
            break
        rows.extend(page)
        if len(page) < limit:
            break
        offset += limit
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if "report_date_as_yyyy_mm_dd" in df.columns:
        df["report_date"] = pd.to_datetime(
            df["report_date_as_yyyy_mm_dd"], errors="coerce"
        )
    # Numeric coercion for known-numeric column patterns (per INV-011 fix)
    numeric_keywords = ("positions", "open_interest", "traders", "pct_of",
                         "conc_", "change_in", "spread")
    for col in df.columns:
        if any(kw in col.lower() for kw in numeric_keywords):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def main() -> int:
    base = Path("data_prefetch/cftc")
    base.mkdir(parents=True, exist_ok=True)
    print(f"=== CFTC extended prefetch ({len(DATASETS)} datasets x {len(CONTRACTS)} contracts) ===")
    total_ok = 0
    for ds_label, (ds_id, ds_name) in DATASETS.items():
        out_dir = base / ds_label
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n--- {ds_label} ({ds_id} = {ds_name}) ---")
        for slug, contract_name in CONTRACTS:
            print(f"  {slug} ({contract_name}) ... ", end="", flush=True)
            try:
                df = fetch_contract(ds_id, contract_name)
                if df.empty:
                    print("EMPTY")
                    continue
                out = out_dir / f"cot_{slug}.parquet"
                df.to_parquet(out, index=False)
                print(f"OK {len(df)} rows")
                total_ok += 1
            except Exception as e:
                print(f"ERROR {e}")
            time.sleep(0.5)
    print(f"\nCFTC extended prefetch: {total_ok} contract-dataset pairs OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
