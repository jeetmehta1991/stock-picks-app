"""scripts/parse_aaii_sentiment.py - parse AAII extended sentiment xls.

Pass 53 v8h+1 owner-supplied 2026-05-08: AAII Sentiment Survey extended file
(downloaded manually from aaii.com via authenticated browser session, since
direct API returns 403 from this network).

Source: data_prefetch/aaii/sentiment (2).xls
Output: data_prefetch/aaii/weekly_sentiment.parquet (REPLACES the 5-col
        version with the 13-col extended schema)

Extended schema vs prior 5-col:
    Existing  : date, bullish, neutral, bearish, bull_bear_spread
    Extended  : + bullish_8wk_ma, bullish_long_term_avg,
                  bullish_long_term_avg_plus_1stdev,
                  bullish_long_term_avg_minus_1stdev,
                  spy_weekly_high, spy_weekly_low, spy_weekly_close, total

Run: python scripts/parse_aaii_sentiment.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "data_prefetch" / "aaii" / "sentiment (2).xls"
OUT = REPO_ROOT / "data_prefetch" / "aaii" / "weekly_sentiment.parquet"


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: {SRC} not found")
        return 1

    raw = pd.read_excel(SRC, sheet_name="SENTIMENT", header=None, engine="xlrd")

    # The header row is at index 3 (0-indexed) per inspection.
    # Data rows start at index 4 (one blank row at index 4 actually; data at 5+).
    header_cols = [
        "date", "bullish", "neutral", "bearish", "total",
        "bullish_8wk_ma", "bull_bear_spread",
        "bullish_long_term_avg",
        "bullish_long_term_avg_plus_1stdev",
        "bullish_long_term_avg_minus_1stdev",
        "spy_weekly_high", "spy_weekly_low", "spy_weekly_close",
    ]
    df = raw.iloc[5:, : len(header_cols)].copy()
    df.columns = header_cols
    df = df.dropna(subset=["date"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).reset_index(drop=True)

    for col in header_cols[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.to_parquet(OUT, index=False)
    print(f"Wrote {OUT.relative_to(REPO_ROOT)}")
    print(f"  rows: {len(df)}")
    print(f"  date range: {df['date'].min().date()} -> {df['date'].max().date()}")
    print(f"  columns: {list(df.columns)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
