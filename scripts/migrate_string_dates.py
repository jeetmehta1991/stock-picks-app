"""scripts/migrate_string_dates.py - convert string-date columns to datetime64.

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08; Tier H22 P3 (INV-033 fix).

Walks all parquet files in data_prefetch/ + backtest/data/cache/, finds
columns named like dates (date / Date / time / TransactionDate /
snapshot_date / report_date / fileDate / ReportDate / etc.) that are
stored as strings, and re-writes them as datetime64.

Idempotent: skips files where the date columns are already datetime.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

DATE_COLUMN_NAMES = {
    "date", "Date", "time", "Time",
    "TransactionDate", "ReportDate", "report_date",
    "snapshot_date", "fileDate", "filed", "Uploaded",
    "last_modified", "filing_date", "filed_date",
    "ex_dividend_date", "pay_date", "record_date", "declaration_date",
    "execution_date", "ipo_date", "announced_date", "last_updated",
    "period_start", "period_end",
}

CACHE_ROOTS = [
    Path("data_prefetch"),
    Path("backtest/data/cache"),
]


def migrate_file(parq: Path) -> tuple[int, list[str]]:
    """Return (cols_migrated, new_column_types) tuple."""
    try:
        df = pd.read_parquet(parq)
    except Exception:
        return 0, []
    if df.empty:
        return 0, []
    migrated = []
    for col in df.columns:
        if col not in DATE_COLUMN_NAMES:
            continue
        if df[col].dtype == "object":
            try:
                converted = pd.to_datetime(df[col], errors="coerce")
                if converted.notna().any():
                    df[col] = converted
                    migrated.append(col)
            except Exception:
                pass
    if migrated:
        try:
            df.to_parquet(parq, index=False)
        except Exception as e:
            print(f"  [WARN] {parq}: write failed {e}")
            return 0, []
    return len(migrated), migrated


def main() -> int:
    total_files = 0
    total_migrated = 0
    total_cols = 0
    for root in CACHE_ROOTS:
        if not root.exists():
            continue
        for parq in root.rglob("*.parquet"):
            total_files += 1
            n, _cols = migrate_file(parq)
            if n > 0:
                total_migrated += 1
                total_cols += n
        print(f"{root}: {total_files} parquets scanned; {total_migrated} migrated")
    print(f"\nMigration complete: {total_migrated} files updated, {total_cols} column conversions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
