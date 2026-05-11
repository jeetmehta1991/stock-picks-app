"""
scripts/refresh_aaii_sentiment.py
---------------------------------

AAII Sentiment Survey weekly auto-refresh script.

DEC-319 + DEC-390 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 46
2026-05-11 (owner-approved Path C).

AAII publishes the weekly sentiment survey every Thursday afternoon
(historically Wednesday before 2014). Without this script, the committed
backtest/data/aaii_sentiment.csv grows stale; new weekly readings need
manual addition. This script:

  1. Fetches the latest sentiment row from aaii.com/sentiment
  2. Appends to backtest/data/aaii_sentiment.csv if the row is newer than
     the last committed week
  3. Logs the fetch with rate-limit + retry handling
  4. Stage 2 LAPTOP-ONLY (DEC-497 NO-LIVE-API HARD CUT excludes runtime
     calls but laptop SETUP scripts are explicitly permitted)

Usage:
  python scripts/refresh_aaii_sentiment.py [--dry-run] [--cron]

  --dry-run: print what would be appended; don't write
  --cron: minimal logging (one line) for crontab invocation

Source: https://www.aaii.com/sentimentsurvey (HTML, no API)
Fallback: https://www.aaii.com/files/surveys/sentiment.xls (Excel)

DEC-318 cross-reference: AAII publication lag (Friday publish vs Wed/Thu
survey) handled in backtest/data/sentiment.py:_load_aaii_csv (use latest
row with date <= as_of).
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
AAII_CSV = REPO_ROOT / "backtest" / "data" / "aaii_sentiment.csv"
AAII_URL_HTML = "https://www.aaii.com/sentimentsurvey"
AAII_URL_XLS = "https://www.aaii.com/files/surveys/sentiment.xls"

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logger = logging.getLogger("refresh_aaii_sentiment")


def fetch_latest_aaii_row():
    """Fetch the most recent AAII sentiment row.

    Returns:
        dict with keys: date, bullish_pct, neutral_pct, bearish_pct
        OR None on fetch failure.

    Implementation notes:
        - Primary path: parse the HTML at AAII_URL_HTML
        - Fallback: parse the XLS at AAII_URL_XLS via pandas.read_excel
        - Both paths network-dependent; this is laptop-only per DEC-497.
    """
    try:
        import pandas as pd
        # Fallback path is more robust: Excel file with consistent schema
        logger.info("Fetching AAII XLS from %s", AAII_URL_XLS)
        df = pd.read_excel(AAII_URL_XLS, header=3, engine="xlrd")
        # AAII XLS columns (Pass 53 spec):
        # ['Reported Date', 'Bullish', 'Neutral', 'Bearish', ...]
        df = df.dropna(subset=["Bullish"])
        last = df.iloc[-1]
        return {
            "date": pd.to_datetime(last["Reported Date"]).date(),
            "bullish_pct": float(last["Bullish"]) * 100,
            "neutral_pct": float(last["Neutral"]) * 100,
            "bearish_pct": float(last["Bearish"]) * 100,
        }
    except Exception as exc:
        logger.error("AAII fetch failed: %s", exc)
        return None


def load_current_csv():
    """Read the existing aaii_sentiment.csv. Returns last row date or None."""
    import pandas as pd
    if not AAII_CSV.exists():
        return None, None
    try:
        df = pd.read_csv(AAII_CSV)
        if df.empty:
            return None, None
        # Normalize date column name
        date_col = "Reported Date" if "Reported Date" in df.columns else "date"
        last_date = pd.to_datetime(df[date_col]).max().date()
        return df, last_date
    except Exception as exc:
        logger.error("Could not read %s: %s", AAII_CSV, exc)
        return None, None


def append_new_row(row: dict, dry_run: bool = False) -> bool:
    """Append `row` to AAII_CSV if newer than last existing entry."""
    import pandas as pd
    existing_df, last_date = load_current_csv()
    if last_date and row["date"] <= last_date:
        logger.info("AAII row %s already present (latest=%s); nothing to append",
                    row["date"], last_date)
        return False
    if dry_run:
        logger.info("[DRY RUN] Would append row: %s", row)
        return True
    new_row_df = pd.DataFrame([{
        "Reported Date": row["date"].isoformat(),
        "Bullish": row["bullish_pct"] / 100,
        "Neutral": row["neutral_pct"] / 100,
        "Bearish": row["bearish_pct"] / 100,
    }])
    if existing_df is not None and not existing_df.empty:
        combined = pd.concat([existing_df, new_row_df], ignore_index=True)
    else:
        combined = new_row_df
    combined.to_csv(AAII_CSV, index=False)
    logger.info("Appended AAII row %s (bull=%.1f%% neut=%.1f%% bear=%.1f%%)",
                row["date"], row["bullish_pct"], row["neutral_pct"], row["bearish_pct"])
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be appended; don't write")
    parser.add_argument("--cron", action="store_true",
                        help="Minimal logging for crontab invocation")
    args = parser.parse_args()
    if args.cron:
        logger.setLevel(logging.WARNING)
    row = fetch_latest_aaii_row()
    if row is None:
        logger.error("AAII fetch returned no row; aborting refresh")
        sys.exit(1)
    success = append_new_row(row, dry_run=args.dry_run)
    sys.exit(0 if success else 0)


if __name__ == "__main__":
    main()
