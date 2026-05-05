"""
scripts/refresh_sp500_universe.py
Refresh backtest/data/Current Snapshot_SP500 Tickers_May 2026.csv with current S&P 500 constituents.

MUST RUN ON LAPTOP (unrestricted network). NOT for Codespaces.
Source: slickcharts.com — free, stable, no auth, updated same day as S&P announcements.
Fallback: manual CSV edit from https://www.spglobal.com/spdji/en/indices/equity/sp-500/#news-research

Usage:
    python scripts/refresh_sp500_universe.py            # review diff only
    python scripts/refresh_sp500_universe.py --write    # write and stage for commit

After running:
    git diff backtest/data/Current Snapshot_SP500 Tickers_May 2026.csv            # review changes
    git add backtest/data/Current Snapshot_SP500 Tickers_May 2026.csv
    git commit -m "Universe refresh: quarterly S&P 500 update YYYY-MM-DD"
    git push origin main

Run quarterly (January, April, July, October) — add to calendar.
NEVER run from Codespaces — network is restricted to specific allowlisted domains (L88).
"""
import sys
import argparse
import time
from datetime import date
from pathlib import Path

import pandas as pd

# ── Config ─────────────────────────────────────────────────────────────────
CSV_PATH  = Path(__file__).parent.parent / "Backtesting universe" / "Current Snapshot_SP500 Tickers_May 2026.csv"
SLICK_URL = "https://www.slickcharts.com/sp500"

# ETF sector labels for any ETF that makes it into the list by mistake
ETF_SECTORS = {
    "SPY": "Broad Market ETF", "QQQ": "Technology ETF", "IWM": "Small Cap ETF",
}

# Known S&P 500 sector mapping for common stocks (supplement to yfinance)
SECTOR_OVERRIDES = {
    "SNDK": "Information Technology",
    "GEV":  "Industrials",
    "VST":  "Utilities",
    "SMCI": "Information Technology",
    "GDDY": "Information Technology",
    "ERIE": "Financials",
}


def fetch_from_slickcharts() -> pd.DataFrame:
    """
    Fetch S&P 500 constituent list from slickcharts.com.
    Returns DataFrame with columns: Symbol, Company, Weight (%)
    Works on unrestricted networks. Stable since 2015+.
    """
    headers = {"User-Agent": "Mozilla/5.0 (compatible; research-tool/1.0)"}
    print(f"Fetching S&P 500 from {SLICK_URL}...")
    tables = pd.read_html(SLICK_URL, attrs={"class": "table"}, storage_options={"User-Agent": headers["User-Agent"]})
    df = tables[0]
    print(f"  Raw table: {len(df)} rows, columns: {df.columns.tolist()}")

    # Normalise column names — slickcharts uses '#', 'Company', 'Symbol', 'Weight'
    df.columns = [c.strip() for c in df.columns]
    if "Symbol" not in df.columns:
        # Try alternate column names
        rename_map = {}
        for col in df.columns:
            if "symbol" in col.lower() or "ticker" in col.lower():
                rename_map[col] = "Symbol"
            elif "company" in col.lower() or "name" in col.lower():
                rename_map[col] = "Company"
        df = df.rename(columns=rename_map)

    # Clean tickers — replace '.' with '-' (BRK.B → BRK-B)
    df["Symbol"] = df["Symbol"].str.strip().str.replace(".", "-", regex=False)
    df = df[df["Symbol"].str.match(r"^[A-Z\-]{1,6}$", na=False)]  # valid ticker chars only
    return df[["Symbol", "Company"]].drop_duplicates(subset=["Symbol"])


def get_sector_from_yfinance(ticker: str) -> str:
    """Fetch sector for a single ticker from yfinance. Used for new additions only."""
    if ticker in SECTOR_OVERRIDES:
        return SECTOR_OVERRIDES[ticker]
    try:
        import yfinance as yf
        info = yf.Ticker(ticker).info
        sector = info.get("sector", "Unknown")
        return sector if sector else "Unknown"
    except Exception:
        return "Unknown"


def main():
    p = argparse.ArgumentParser(description="Refresh S&P 500 universe CSV")
    p.add_argument("--write", action="store_true", help="Write updated CSV (default: dry run)")
    p.add_argument("--add", nargs="+", metavar="TICKER",
                   help="Force-add tickers (e.g. spinoffs) even if not in slickcharts")
    p.add_argument("--remove", nargs="+", metavar="TICKER",
                   help="Force-remove tickers (confirmed removals)")
    args = p.parse_args()

    # ── 1. Load current CSV ───────────────────────────────────────────────
    if not CSV_PATH.exists():
        print(f"ERROR: {CSV_PATH} not found")
        sys.exit(1)
    current_df = pd.read_csv(CSV_PATH, comment='#')
    # Pass 53 schema standardization — ensure B++ columns present (added_date/removed_date)
    if "added_date" not in current_df.columns:
        current_df["added_date"] = ""
    if "removed_date" not in current_df.columns:
        current_df["removed_date"] = ""
    current_tickers = set(current_df["Symbol"].tolist())
    print(f"\nCurrent CSV: {len(current_tickers)} tickers (last updated: check git log)")

    # ── 2. Fetch new list ─────────────────────────────────────────────────
    try:
        new_df = fetch_from_slickcharts()
    except Exception as e:
        print(f"\nERROR fetching from slickcharts: {e}")
        print("Fallback options:")
        print("  1. Check https://www.spglobal.com/spdji/en/indices/equity/sp-500/#news-research")
        print("  2. Use --add/--remove flags to apply known changes manually")
        print("  3. Check Quiver Quantitative for S&P 500 membership data")
        sys.exit(1)

    new_tickers = set(new_df["Symbol"].tolist())

    # ── 3. Compute diff ───────────────────────────────────────────────────
    additions = new_tickers - current_tickers
    removals  = current_tickers - new_tickers

    # Apply forced overrides
    if args.add:
        for t in args.add:
            additions.add(t.upper())
            print(f"  Force-adding: {t.upper()}")
    if args.remove:
        for t in args.remove:
            removals.add(t.upper())
            print(f"  Force-removing: {t.upper()}")

    print(f"\n{'='*60}")
    print(f"DIFF vs current CSV")
    print(f"{'='*60}")
    if additions:
        print(f"\n✅ ADDITIONS ({len(additions)}):")
        for t in sorted(additions):
            company = new_df[new_df["Symbol"] == t]["Company"].values
            name = company[0] if len(company) > 0 else "(manual add)"
            print(f"   + {t:8s}  {name}")
    else:
        print("\n  No additions detected")

    if removals:
        print(f"\n❌ REMOVALS ({len(removals)}):")
        for t in sorted(removals):
            row = current_df[current_df["Symbol"] == t]
            name = row["Company"].values[0] if len(row) > 0 else "?"
            sector = row["Sector"].values[0] if "Sector" in row.columns and len(row) > 0 else "?"
            print(f"   - {t:8s}  {name}  [{sector}]")
    else:
        print("\n  No removals detected")

    if not additions and not removals:
        print("\n✅ Universe is current — no changes needed")
        return

    # ── 4. Build updated DataFrame ────────────────────────────────────────
    # Start from current, apply removals
    updated_df = current_df[~current_df["Symbol"].isin(removals)].copy()

    # Fetch sectors for new additions
    if additions and args.write:
        print(f"\nFetching sectors for {len(additions)} new tickers (yfinance)...")
        today_iso = date.today().isoformat()
        new_rows = []
        for i, ticker in enumerate(sorted(additions)):
            sector = get_sector_from_yfinance(ticker)
            company_row = new_df[new_df["Symbol"] == ticker]
            company = company_row["Company"].values[0] if len(company_row) > 0 else ticker
            # Pass 53 B++ schema: set added_date for new entries; removed_date NULL until removed
            new_rows.append({
                "Symbol": ticker,
                "Company": company,
                "Sector": sector,
                "added_date": today_iso,
                "removed_date": "",
            })
            print(f"  {ticker}: {sector}")
            if i < len(additions) - 1:
                time.sleep(0.5)
        updated_df = pd.concat([updated_df, pd.DataFrame(new_rows)], ignore_index=True)
    elif additions:
        # Dry run — show what would be added
        print(f"\n  (dry run — sectors not fetched; use --write to fetch and apply)")

    # ── 5. Write or report ────────────────────────────────────────────────
    if args.write:
        updated_df = updated_df.sort_values("Symbol").reset_index(drop=True)
        # Pass 53 B++ schema — enforce canonical column order on output
        b_plus_plus_cols = ["Symbol", "Company", "Sector", "added_date", "removed_date"]
        extra_cols = [c for c in updated_df.columns if c not in b_plus_plus_cols]
        updated_df = updated_df[b_plus_plus_cols + extra_cols]
        updated_df.to_csv(CSV_PATH, index=False)
        print(f"\n✅ Written: {CSV_PATH}")
        print(f"   {len(current_tickers)} → {len(updated_df)} tickers")
        print(f"\nNext steps:")
        print(f"  git diff backtest/data/Current Snapshot_SP500 Tickers_May 2026.csv   # review")
        print(f"  git add backtest/data/Current Snapshot_SP500 Tickers_May 2026.csv")
        print(f"  git commit -m 'Universe refresh: Q{(date.today().month-1)//3+1} {date.today().year} S&P 500 update'")
        print(f"  git push origin main")
    else:
        print(f"\n  Dry run complete. Use --write to apply changes.")
        print(f"  Or use --add/--remove for manual overrides without slickcharts.")


if __name__ == "__main__":
    main()
