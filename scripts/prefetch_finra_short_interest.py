#!/usr/bin/env python3
"""Batch 513 (2026-05-31) -- P15 FINRA biweekly short-interest fetcher.

Source: per CHECKLIST #77 + owner directive 2026-05-31 (P15 option =
"I'll provide the FINRA URL"; web-search found the canonical URL).
Queue row: EXECUTION_QUEUE.md item P15.

FINRA publishes biweekly short-interest reports at:
  https://cdn.finra.org/equity/otcmarket/biweekly/shrtYYYYMMDD.csv

Despite the "otcmarket" path component, the CSV covers BOTH NYSE/NASDAQ
exchange-listed names AND OTC names (verified Batch 513 web-fetch: AAPL,
MSFT and others are present alongside OTC tickers).

Schema (pipe-delimited despite the .csv extension):
  accountingYearMonthNumber|symbolCode|issueName|issuerServicesGroupExchangeCode
  |marketClassCode|currentShortPositionQuantity|previousShortPositionQuantity
  |stockSplitFlag|averageDailyVolumeQuantity|daysToCoverQuantity|revisionFlag
  |changePercent|changePreviousNumber|settlementDate

Important caveat per FINRA: prior to June 2021 the data is OTC-only;
post-2021-06 it includes exchange-listed names. Backtest cube
spans 2022-2026 so all snapshots fall in the post-2021-06 window.

Cadence: bi-weekly, settlement dates around the 15th and end of month
(e.g. 2026-04-15, 2026-04-30, 2026-05-15, etc.).

Output: `data_prefetch/finra/short_interest/<TICKER>.parquet` --
per-ticker history with columns (settlement_date, short_interest,
shares_outstanding, avg_daily_volume) matching the schema expected
by `backtest/signals/short_interest.py::compute_short_interest_signals`.

USAGE (operator-run after owner approval):

  # Pilot: just the most recent settlement
  python scripts/prefetch_finra_short_interest.py --pilot

  # Full historical pull (2021-06 to today, ~110 biweekly snapshots):
  python scripts/prefetch_finra_short_interest.py --full

  # Specific date:
  python scripts/prefetch_finra_short_interest.py --date 2026-04-30
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Optional
import urllib.error
import urllib.request

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# FINRA URL pattern (verified Batch 513 web-fetch)
FINRA_URL_PATTERN = (
    "https://cdn.finra.org/equity/otcmarket/biweekly/shrt{yyyymmdd}.csv"
)

# FINRA does NOT require a custom User-Agent (unlike SEC EDGAR), but a
# polite identifying UA reduces friction with their CDN throttle.
USER_AGENT = "Stock Picks Research jeetmehta1991@gmail.com"

# Polite throttle (FINRA CDN tolerates higher rates than SEC; 1/sec is
# conservative for the ~110 biweekly snapshots in 5 years).
RATE_LIMIT_SLEEP_SEC = 1.0

# Schema (FINRA's pipe-delimited columns)
FINRA_RAW_COLS = (
    "accountingYearMonthNumber", "symbolCode", "issueName",
    "issuerServicesGroupExchangeCode", "marketClassCode",
    "currentShortPositionQuantity", "previousShortPositionQuantity",
    "stockSplitFlag", "averageDailyVolumeQuantity",
    "daysToCoverQuantity", "revisionFlag", "changePercent",
    "changePreviousNumber", "settlementDate",
)

OUTPUT_DIR = REPO / "data_prefetch" / "finra" / "short_interest"


def biweekly_dates(start: date = date(2021, 6, 15),
                    end: Optional[date] = None) -> list[date]:
    """Generate biweekly settlement dates (15th + end-of-month) from
    start to end (inclusive). FINRA's published cadence."""
    if end is None:
        end = date.today()
    dates: list[date] = []
    y, m = start.year, start.month
    while True:
        # 15th of month
        d15 = date(y, m, 15)
        if d15 >= start and d15 <= end:
            dates.append(d15)
        # End of month
        if m == 12:
            ey, em = y + 1, 1
        else:
            ey, em = y, m + 1
        eom = date(ey, em, 1) - timedelta(days=1)
        if eom >= start and eom <= end:
            dates.append(eom)
        # Advance month
        if (y, m) >= (end.year, end.month):
            break
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1
    return sorted(dates)


def _fetch_csv(url: str, timeout: int = 60) -> Optional[bytes]:
    """Fetch a FINRA short-interest CSV. Returns bytes or None on error."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return None


def parse_finra_csv(raw_bytes: bytes) -> pd.DataFrame:
    """Parse the pipe-delimited FINRA short-interest CSV bytes into a
    normalized DataFrame with the schema expected by
    `compute_short_interest_signals`:
        settlement_date / short_interest / shares_outstanding (NaN --
        FINRA doesn't publish it; producer tolerates missing column) /
        avg_daily_volume / symbolCode (ticker passthrough).
    """
    import io
    df = pd.read_csv(io.BytesIO(raw_bytes), sep="|", dtype=str,
                       low_memory=False)
    # Coerce numerics
    out = pd.DataFrame()
    out["ticker"] = df["symbolCode"].str.upper().str.strip()
    out["settlement_date"] = pd.to_datetime(
        df["settlementDate"], errors="coerce"
    ).dt.date
    out["short_interest"] = pd.to_numeric(
        df["currentShortPositionQuantity"], errors="coerce"
    )
    out["avg_daily_volume"] = pd.to_numeric(
        df["averageDailyVolumeQuantity"], errors="coerce"
    )
    # shares_outstanding NOT in FINRA feed -- producer treats as missing
    # and computes only days_to_cover (which IS publishable from this data).
    out["shares_outstanding"] = pd.NA
    return out.dropna(subset=["settlement_date", "short_interest"])


def fetch_one_settlement(settlement_dt: date,
                          dry_run: bool = True) -> Optional[pd.DataFrame]:
    """Fetch + parse one biweekly settlement snapshot. None on error."""
    yyyymmdd = settlement_dt.strftime("%Y%m%d")
    url = FINRA_URL_PATTERN.format(yyyymmdd=yyyymmdd)
    if dry_run:
        print(f"[DRY-RUN] would fetch {url}")
        return None
    raw = _fetch_csv(url)
    if raw is None:
        print(f"[FAIL]    {url}")
        return None
    try:
        df = parse_finra_csv(raw)
        print(f"[OK]      {url} -> {len(df)} ticker rows")
        return df
    except Exception as exc:
        print(f"[PARSE-ERR] {url}: {exc}")
        return None


def repartition_by_ticker(snapshot_dfs: list[pd.DataFrame],
                            output_dir: Path = OUTPUT_DIR) -> dict:
    """Concat all snapshots, group by ticker, write per-ticker parquets.

    Returns manifest dict {ticker: n_snapshots}.
    """
    if not snapshot_dfs:
        return {}
    all_df = pd.concat(snapshot_dfs, ignore_index=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict = {}
    for ticker, sub in all_df.groupby("ticker", sort=False):
        sub = sub.sort_values("settlement_date").drop_duplicates(
            subset=["settlement_date"], keep="last"
        ).reset_index(drop=True)
        safe = str(ticker).replace(".", "-").upper()
        out_path = output_dir / f"{safe}.parquet"
        # Schema expected by compute_short_interest_signals:
        sub_out = sub[[
            "settlement_date", "short_interest",
            "shares_outstanding", "avg_daily_volume",
        ]]
        sub_out.to_parquet(out_path, index=False)
        manifest[ticker] = len(sub_out)
    return manifest


def run_pilot(dry_run: bool = True) -> list[pd.DataFrame]:
    """Pilot: fetch just the most recent settlement (one CSV ~2MB)."""
    today = date.today()
    # Most recent biweekly: prior settlement date
    candidates = biweekly_dates(start=today - timedelta(days=20), end=today)
    if not candidates:
        print("no biweekly dates in last 20 days")
        return []
    snap = fetch_one_settlement(candidates[-1], dry_run=dry_run)
    return [snap] if snap is not None else []


def run_full(dry_run: bool = True) -> list[pd.DataFrame]:
    """Full pull: 2021-06-15 to today (~110 snapshots)."""
    dates = biweekly_dates()
    print(f"Full pull: {len(dates)} biweekly snapshots from "
          f"{dates[0]} to {dates[-1]}")
    snaps = []
    for d in dates:
        s = fetch_one_settlement(d, dry_run=dry_run)
        if s is not None:
            snaps.append(s)
        if not dry_run:
            time.sleep(RATE_LIMIT_SLEEP_SEC)
    return snaps


def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--pilot", action="store_true",
                     help="Fetch most recent settlement only (one CSV)")
    mode.add_argument("--full", action="store_true",
                     help="Full historical pull from 2021-06 to today")
    mode.add_argument("--date", type=str,
                     help="Specific YYYY-MM-DD settlement date")
    p.add_argument("--dry-run", action="store_true", default=False,
                   help="Print URLs without fetching")
    args = p.parse_args()
    print(f"FINRA short-interest prefetch ({'DRY' if args.dry_run else 'LIVE'})")
    print(f"URL pattern: {FINRA_URL_PATTERN}")
    print()
    if args.pilot:
        snaps = run_pilot(args.dry_run)
    elif args.full:
        snaps = run_full(args.dry_run)
    else:
        dt = date.fromisoformat(args.date)
        s = fetch_one_settlement(dt, dry_run=args.dry_run)
        snaps = [s] if s is not None else []
    print()
    if args.dry_run or not snaps:
        print("(dry-run or no snapshots fetched; no parquet writes)")
        return
    print(f"\n[REPARTITION] {len(snaps)} snapshots -> per-ticker parquets...")
    manifest = repartition_by_ticker(snaps)
    print(f"Wrote {len(manifest)} ticker parquets to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
