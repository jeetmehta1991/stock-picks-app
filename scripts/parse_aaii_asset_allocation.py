"""scripts/parse_aaii_asset_allocation.py - parse AAII Asset Allocation Survey xls.

Pass 53 v8h+1 owner-approved 2026-05-09: AAII Asset Allocation Survey
(monthly stocks/bonds/cash %; separate from the weekly Sentiment survey).

Source: data_prefetch/aaii/asset.xls (manual download from AAII member portal;
direct fetch returns 403 from this network).
Output: data_prefetch/aaii/asset_allocation_survey.parquet

Schema (11 columns):
  date                      - month-end snapshot date
  stock_funds_pct           - allocation to stock mutual funds / ETFs
  stocks_pct                - allocation to individual stocks
  bond_funds_pct            - allocation to bond mutual funds / ETFs
  bonds_pct                 - allocation to individual bonds
  cash_pct                  - allocation to cash / money-market
  total                     - sum (~1.000; sanity check)
  stocks_combined_pct       - stock_funds + stocks
  bonds_combined_pct        - bond_funds + bonds
  cash_combined_pct         - cash (mirror)
  response_rate             - survey response count

Use case (DEC-501 follow-on / Phase 1A regime input):
  Asset allocation survey is a contrarian indicator - retail-investor
  stocks_combined extreme high = late-cycle warning; extreme low = bottom
  signal. Long-term average ~62% stocks; >75% = euphoric, <50% = panic.

Run: python scripts/parse_aaii_asset_allocation.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "data_prefetch" / "aaii" / "asset.xls"
OUT = REPO_ROOT / "data_prefetch" / "aaii" / "asset_allocation_survey.parquet"


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: {SRC} not found")
        return 1

    raw = pd.read_excel(SRC, sheet_name="AAII Asset Allocation Survey",
                          header=None, engine="xlrd")

    # Header row at index 2 (per inspection); data rows from index 3 onward.
    # Column layout:
    #   0  date
    #   1  Stock Funds
    #   2  Stocks
    #   3  Bond Funds
    #   4  Bonds
    #   5  Cash
    #   6  Total
    #   8  Stocks combined
    #   9  Bonds combined
    #   10 Cash combined
    #   12 Response Rate
    column_map = {
        0:  "date",
        1:  "stock_funds_pct",
        2:  "stocks_pct",
        3:  "bond_funds_pct",
        4:  "bonds_pct",
        5:  "cash_pct",
        6:  "total",
        8:  "stocks_combined_pct",
        9:  "bonds_combined_pct",
        10: "cash_combined_pct",
        12: "response_rate",
    }
    df = raw.iloc[3:, list(column_map.keys())].copy()
    df.columns = list(column_map.values())
    df = df.dropna(subset=["date"])

    # Mixed date formats:
    #  - Most rows: Excel datetime (parse cleanly)
    #  - Recent rows (2024-2026): text labels like "Oct '24:" / "Apr' 26"
    #  - Footer/legend rows: text labels like "Average" / "**Beginning..."
    import re as _re
    _MONTHS = {"jan":1, "feb":2, "mar":3, "apr":4, "may":5, "jun":6, "june":6,
               "jul":7, "july":7, "aug":8, "sep":9, "sept":9, "oct":10, "nov":11, "dec":12}

    def _coerce_date(v):
        if isinstance(v, pd.Timestamp):
            return v
        if isinstance(v, str):
            s = v.strip().rstrip(":").strip()
            # Try AAII text label format like "Oct '24" / "Apr' 26"
            m = _re.match(r"^([A-Za-z]+)\s*'?\s*(\d{2,4})$", s)
            if m:
                month_name = m.group(1).lower()[:4]
                yr = int(m.group(2))
                if yr < 100:
                    yr += 2000  # AAII xls 2-digit years are 21st century
                if month_name in _MONTHS:
                    # Use 1st of month as the snapshot date convention
                    return pd.Timestamp(year=yr, month=_MONTHS[month_name], day=1)
            # Standard date formats fallback
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"):
                try:
                    return pd.to_datetime(s, format=fmt, errors="raise")
                except (ValueError, TypeError):
                    continue
        try:
            return pd.to_datetime(v, errors="coerce")
        except Exception:
            return pd.NaT

    df["date"] = df["date"].apply(_coerce_date)
    df = df.dropna(subset=["date"]).reset_index(drop=True)
    # Filter implausible early dates (parser miscoercion produces year=0001)
    df = df[df["date"] >= pd.Timestamp("1985-01-01")].reset_index(drop=True)

    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows where all 3 main allocation cells are NaN (pre-survey)
    df = df.dropna(subset=["stocks_combined_pct", "bonds_combined_pct",
                            "cash_combined_pct"], how="all").reset_index(drop=True)

    df.to_parquet(OUT, index=False)
    print(f"Wrote {OUT.relative_to(REPO_ROOT)}")
    print(f"  rows: {len(df)}")
    print(f"  date range: {df['date'].min().date()} -> {df['date'].max().date()}")
    print(f"  columns: {list(df.columns)}")
    if len(df) > 0:
        latest = df.iloc[-1]
        print(f"  latest: stocks={latest['stocks_combined_pct']:.1%}  "
              f"bonds={latest['bonds_combined_pct']:.1%}  "
              f"cash={latest['cash_combined_pct']:.1%}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
