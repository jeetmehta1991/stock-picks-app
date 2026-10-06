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
# S6-B3139at (owner ruling 2026-10-06, packet row 19 're-fetch'): the seven
# series backtest/signals/cot_positioning.py reads are fetched by CFTC
# CONTRACT CODE - stable across renames, one contract per file. The name
# filters below matched the MICRO contracts for ndx and rut (the standard
# E-minis are named "NASDAQ MINI" and "RUSSELL E-MINI") and mixed the micro
# into sp500 and gold. Codes confirmed against CFTC's API at B3139q-r47
# (each 404 weekly reports 2019-01-08..2026-09-29).
CONTRACT_CODES = {
    "emini_sp500": "13874A",      # E-MINI S&P 500
    "emini_nasdaq100": "209742",  # NASDAQ MINI (the E-mini Nasdaq-100)
    "emini_russell2k": "239742",  # RUSSELL E-MINI (Russell 2000)
    "emini_dow": "124603",        # DJIA x $5
    "dxy_dollar_idx": "098662",   # USD INDEX
    "gold": "088691",             # GOLD (COMEX)
    "copper": "085692",           # COPPER- #1
    # The remaining slugs, read by backtest/data/sentiment.py get_cftc_cot.
    # Each code is the primary contract already in the file; eur_usd, jpy_usd,
    # silver and ust_bond had cross-rates, micros or the ultra bond mixed in.
    "vix_futures": "1170E1",      # VIX FUTURES
    "treasury_10y": "043602",     # UST 10Y NOTE
    "treasury_5y": "044601",      # UST 5Y NOTE
    "treasury_2y": "042601",      # UST 2Y NOTE
    "ust_bond": "020601",         # UST BOND (the ultra bond has its own file)
    "ultra_treasury": "020604",   # ULTRA UST BOND
    "fed_funds_30d": "045601",    # FED FUNDS
    "eur_usd": "099741",          # EURO FX
    "jpy_usd": "097741",          # JAPANESE YEN
    "wti_crude": "067411",        # CRUDE OIL, LIGHT SWEET-WTI
    "silver": "084691",           # SILVER
    "natural_gas": "023651",      # NAT GAS NYME
}

CONTRACTS = [
    # -- Equity indices (TFF) --
    ("emini_sp500",     DATASET_TFF, "E-MINI S&P 500"),
    ("emini_nasdaq100", DATASET_TFF, "E-MINI NASDAQ-100"),
    ("emini_russell2k", DATASET_TFF, "E-MINI RUSSELL 2000"),
    ("emini_dow",       DATASET_TFF, "E-MINI DJIA (X $5)"),
    ("vix_futures",     DATASET_TFF, "VIX FUTURES"),
    # -- Rates (TFF) -- INV-011 fix 2026-05-07: actual CFTC contract names
    ("treasury_10y",    DATASET_TFF, "UST 10Y NOTE"),
    ("treasury_5y",     DATASET_TFF, "UST 5Y NOTE"),
    ("treasury_2y",     DATASET_TFF, "UST 2Y NOTE"),
    ("ust_bond",        DATASET_TFF, "UST BOND"),
    ("ultra_treasury",  DATASET_TFF, "ULTRA UST BOND"),
    ("fed_funds_30d",   DATASET_TFF, "FED FUNDS"),
    ("emini_dow",       DATASET_TFF, "DJIA x $5"),
    # -- Currencies (TFF) --
    ("dxy_dollar_idx",  DATASET_TFF, "USD INDEX"),
    ("eur_usd",         DATASET_TFF, "EURO FX"),
    ("jpy_usd",         DATASET_TFF, "JAPANESE YEN"),
    # -- Commodities (DCOT) --
    ("wti_crude",       DATASET_DCOT, "CRUDE OIL, LIGHT SWEET-WTI"),
    ("gold",            DATASET_DCOT, "GOLD"),
    ("silver",          DATASET_DCOT, "SILVER"),
    ("natural_gas",     DATASET_DCOT, "NAT GAS NYME"),
    ("copper",          DATASET_DCOT, "COPPER- #1"),
]


def fetch_contract(dataset: str, contract_filter: str,
                    limit_per_page: int = 50000, code: str | None = None) -> pd.DataFrame:
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
            "$where": (f"cftc_contract_market_code = '{code}'" if code else
                       f"upper(contract_market_name) like '%{contract_filter.upper()}%'"),
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
    # Pass 53 Day-9 v8h fix (caught by test_data_integrity_4_numeric_dtype_cftc_fred):
    # CFTC Socrata API returns numeric columns as JSON strings. Coerce to numeric
    # so downstream arithmetic (rolling means, position changes, etc.) works.
    numeric_keywords = (
        "positions", "open_interest", "traders", "pct_of", "conc_",
        "change_in", "spread",
    )
    for col in df.columns:
        if any(kw in col.lower() for kw in numeric_keywords):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def main():
    print(f"Fetching {len(CONTRACTS)} CFTC contracts to {OUT_DIR}/")
    print()
    success_count = 0
    fail_count = 0
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    done = set()
    for slug, dataset, contract_filter in CONTRACTS:
        if (only is not None and slug not in only) or slug in done:
            continue
        done.add(slug)
        out_path = OUT_DIR / f"cot_{slug}.parquet"
        try:
            code = CONTRACT_CODES.get(slug)
            df = fetch_contract(dataset, contract_filter, code=code)
            if code and not df.empty:
                # S6-B3139at: one contract, one row per report date - fail closed
                codes = set(df["cftc_contract_market_code"].astype(str))
                if codes != {code}:
                    raise ValueError(f"{slug}: codes {sorted(codes)} != {{{code}}}")
                if df["report_date"].duplicated().any():
                    raise ValueError(f"{slug}: repeated report dates")
            if df.empty:
                print(f"  [SKIP] {slug} ({contract_filter}): no rows returned "
                      f"- check filter")
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
