"""
scripts/prefetch_macro.py — Pre-fetch all FRED macro data for Phase 1B backtest.

Downloads and caches to Parquet:
  - T10Y2Y: 10-year minus 2-year yield curve spread
  - FEDFUNDS: Federal funds rate
  - UNRATE: Unemployment rate
  - CPIAUCSL: CPI inflation
  - T10YIE: 10-year inflation expectations
  - VIXCLS: VIX (also in OHLCV cache but useful as standalone)
  - DGS10: 10-year treasury yield
  - BAA10Y: Corporate bond spread (credit risk proxy)

Run from either laptop or Codespaces (FRED is allowed):
  python scripts/prefetch_macro.py
"""

import os
import sys
import requests
import pandas as pd
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env so FRED_API_KEY does not need manual export (Pass 53 Day-9 v8 BUG-VIX-PROXY fix)
def _load_env_file(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for line in path.read_text(errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env_file()

FRED_KEY = os.environ.get("FRED_API_KEY", "")
if not FRED_KEY:
    print("ERROR: FRED_API_KEY not set (looked in env + .env)")
    sys.exit(1)

CACHE_DIR = Path("backtest/data/cache/macro")
SPRINT_0A_DIR = Path("data_prefetch/fred/observations")  # canonical L146 wiring path
DATE_START = "2020-01-01"
DATE_END = "2026-12-31"

SERIES = {
    "yield_curve":    "T10Y2Y",    # 10Y-2Y spread - inversion = recession risk
    "fed_funds":      "FEDFUNDS",  # Fed funds rate
    "unemployment":   "UNRATE",    # Unemployment rate
    "cpi":            "CPIAUCSL",  # CPI inflation
    "inflation_exp":  "T10YIE",    # 10-year breakeven inflation
    "treasury_10y":   "DGS10",     # 10-year treasury yield
    "corp_spread":    "BAA10Y",    # Corporate bond spread
    "vix":            "VIXCLS",    # VIX volatility index (BUG-VIX-PROXY fix Pass 53 Day-9 v8)
    # Pass 53 Day-9 v8h Tier C additions (DEC-513 #7 + macro signals)
    "vix_3m":         "VXVCLS",    # 3-month VIX (term-structure ratio with VIX)
    "vvix":           "VVIXCLS",   # Vol of VIX (regime-shift indicator)
    "dxy":            "DTWEXBGS",  # Trade-weighted broad dollar index
    "ted_3m":         "TB3SMFFM",  # 3-month T-bill - fed funds (TED-style spread)
    "wti":            "DCOILWTICO",# WTI crude oil price
    "housing_starts": "HOUST",     # Housing starts
    "permits":        "PERMIT",    # Building permits
    "retail_sales":   "RSAFS",     # Retail sales
    "industrial_prod":"INDPRO",    # Industrial production index
    "consumer_sent":  "UMCSENT",   # U-Mich consumer sentiment
    "money_supply_m2":"M2SL",      # M2 money stock
    "pce_inflation":  "PCEPI",     # PCE price index (Fed's preferred inflation gauge)
    "gold_price":     "GOLDAMGBD228NLBM",  # London gold AM fix
    # Pass 53 Day-9 v8h+1 additions (broad-everything per owner directive 2026-05-08)
    # TIPS yields (real)
    "tips_5y":        "DFII5",
    "tips_10y":       "DFII10",
    "tips_30y":       "DFII30",
    "forward_inflation_5y5y": "T5YIFR",
    # Productivity
    "productivity":   "OPHNFB",
    "unit_labor_cost":"ULCNFB",
    # Yield curve points
    "treasury_3y":    "DGS3",
    "treasury_20y":   "DGS20",
    # Fed balance sheet detail
    "treasury_held":  "TREAST",
    # M1 money supply + monetary base
    "money_supply_m1":"M1SL",
    "monetary_base":  "BOGMBASE",
    # Sector employment
    "employ_construction": "USCONS",
    "employ_trade":   "USTRADE",
    "employ_mining":  "USMINE",
    "employ_info":    "USINFO",
    "employ_finance": "USFIRE",
    "employ_education":"USEHS",
    "employ_leisure": "USLAH",
    "employ_services":"USSERV",
    "employ_government":"USGOVT",
    # Housing additions
    "case_shiller":   "CSUSHPINSA",
    "median_sale_price":"MSPUS",
    # Manufacturing
    "new_orders_durable":"AMTMNO",
    # Consumer credit
    "consumer_credit":"TOTALSL",
    # FX exchange rates (FRED-tracked)
    "dex_us_eu":      "DEXUSEU",
    "dex_us_uk":      "DEXUSUK",
    "dex_jp_us":      "DEXJPUS",
    "dex_us_ca":      "DEXCAUS",
    "dex_us_ch":      "DEXSZUS",
    # Commodities
    "brent":          "DCOILBRENTEU",
    "gas_reg":        "GASREGW",
    # Foreign yields
    "germany_10y":    "IRLTLT01DEM156N",
    "uk_10y":         "IRLTLT01GBM156N",
    "japan_10y":      "IRLTLT01JPM156N",
}


def fetch_fred(series_id: str) -> pd.DataFrame:
    url = (
        f"https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}"
        f"&api_key={FRED_KEY}"
        f"&file_type=json"
        f"&observation_start={DATE_START}"
        f"&observation_end={DATE_END}"
    )
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    obs = data.get("observations", [])
    if not obs:
        return pd.DataFrame()
    df = pd.DataFrame(obs)[["date", "value"]]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])
    return df


def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    SPRINT_0A_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Fetching {len(SERIES)} FRED macro series: {DATE_START} to {DATE_END}")
    print()

    all_series = {}
    for name, series_id in SERIES.items():
        try:
            df = fetch_fred(series_id)
            # Legacy path
            out_file = CACHE_DIR / f"{name}.parquet"
            df.to_parquet(out_file, index=False)
            # Sprint 0A canonical path (DEC-440 / L146 wiring matrix)
            sprint_file = SPRINT_0A_DIR / f"{series_id}.parquet"
            df.to_parquet(sprint_file, index=False)
            all_series[name] = df
            print(f"  [OK] {name} ({series_id}): {len(df)} observations -> "
                  f"{out_file.name} + {sprint_file.name}")
        except Exception as e:
            print(f"  [FAIL] {name} ({series_id}): {e}")

    # Also save combined macro snapshot for fast lookup
    # Forward-fill to daily frequency
    all_dates = pd.date_range(DATE_START, DATE_END, freq="B")
    combined = pd.DataFrame(index=all_dates)
    for name, df in all_series.items():
        if not df.empty:
            s = df.set_index("date")["value"]
            combined[name] = s.reindex(all_dates).ffill()

    combined.index.name = "date"
    combined = combined.reset_index()
    combined.to_parquet(CACHE_DIR / "macro_combined.parquet", index=False)
    print(f"\n  [OK] Combined macro snapshot: {len(combined)} daily rows")

    print("\nMacro pre-fetch complete. Caller is responsible for git commit.")


if __name__ == "__main__":
    main()
