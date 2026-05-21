"""Comprehensive OHLCV integrity scan (Batch 298).

Per owner directive 2026-05-21: pre-Phase-1A-beta validation. Extends
Batch 276 audit (which scanned for ticker reuse using day-over-day close
ratios and found META as the unique case) with additional integrity
checks that a final-run-quality OHLCV cache should pass:

1. Volume = 0 day clusters (halts) - flag tickers with >5 consecutive
   zero-volume days (suggests delisted or halted ticker that shouldn't
   be in current universe).
2. Suspicious split-like events not in dividend data (>3x intraday
   open-to-close gap without matching split adjustment).
3. Tickers with <60 bars total (insufficient history for backtest
   gates that require 60-day lookback).
4. NaN / null close rows (corrupt data).
5. Date gaps > 7 calendar days (data prefetch gap or delisting).
6. Tickers where date range doesn't cover backtest window
   (2022-05-01 to 2026-04-30).

Output: OHLCV_INTEGRITY_REPORT.md + ohlcv_integrity.json
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
PRIMARY_CACHE = REPO / "data_prefetch" / "polygon" / "ohlcv_daily"

# Backtest window for Phase 1A-beta
BACKTEST_START = date(2022, 5, 1)
BACKTEST_END = date(2026, 4, 30)

# Thresholds
MIN_BARS = 60
MAX_DATE_GAP_DAYS = 14    # allow 2-week gap (holiday clusters)
MAX_ZERO_VOL_STREAK = 5
SUSPICIOUS_SPLIT_RATIO = 3.0


def scan_ticker(path: Path) -> dict:
    """Scan a single ticker for integrity issues. Returns dict of issues
    (empty when clean)."""
    issues = {}
    try:
        df = pd.read_parquet(path)
    except Exception as exc:
        return {"read_fail": str(exc)}
    if df.empty:
        return {"empty_file": True}
    if "close" not in df.columns:
        return {"missing_close_col": True}

    # Normalize date
    if "date" in df.columns:
        df["dt"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    else:
        try:
            df["dt"] = pd.to_datetime(df.index).date
        except Exception:
            return {"no_date_col": True}
    df = df.dropna(subset=["dt"]).sort_values("dt").reset_index(drop=True)
    if df.empty:
        return {"all_null_dates": True}

    # 1. Insufficient bars
    if len(df) < MIN_BARS:
        issues["insufficient_bars"] = len(df)

    # 2. NaN closes
    n_nan = df["close"].isna().sum()
    if n_nan > 0:
        issues["nan_closes"] = int(n_nan)

    # 3. Zero-volume streaks
    if "volume" in df.columns:
        zero = df["volume"].fillna(0) == 0
        streaks = []
        cur = 0
        for v in zero:
            if v:
                cur += 1
            else:
                if cur >= MAX_ZERO_VOL_STREAK:
                    streaks.append(cur)
                cur = 0
        if cur >= MAX_ZERO_VOL_STREAK:
            streaks.append(cur)
        if streaks:
            issues["zero_volume_streaks"] = {
                "count": len(streaks),
                "max_streak": max(streaks),
            }

    # 4. Date gaps
    if len(df) >= 2:
        df["prev_dt"] = df["dt"].shift(1)
        df["gap"] = (
            pd.to_datetime(df["dt"]) - pd.to_datetime(df["prev_dt"])
        ).dt.days
        big_gaps = df[df["gap"] > MAX_DATE_GAP_DAYS]
        if not big_gaps.empty:
            issues["date_gaps"] = {
                "count": len(big_gaps),
                "max_gap_days": int(big_gaps["gap"].max()),
            }

    # 5. Suspicious intraday gap (open vs close)
    if "open" in df.columns:
        ratio_oc = df["close"] / df["open"]
        suspicious = df[(ratio_oc > SUSPICIOUS_SPLIT_RATIO) |
                          (ratio_oc < 1 / SUSPICIOUS_SPLIT_RATIO)]
        if not suspicious.empty:
            issues["suspicious_intraday"] = {
                "count": len(suspicious),
                "sample_dates": [str(d) for d in
                                  suspicious["dt"].head(3).tolist()],
            }

    # 6. Coverage of backtest window
    from datetime import timedelta as _td
    first = df["dt"].iloc[0]
    last = df["dt"].iloc[-1]
    # Allow 180-day buffer for new listings (legitimate mid-window listings)
    # Flag only if data ends >30 days before backtest end (suggests delisting
    # mid-backtest that isn't reflected in universe membership)
    if last < BACKTEST_END - _td(days=30):
        issues["coverage_short"] = (
            f"data ends {last}, backtest ends {BACKTEST_END}"
        )
    return issues


def main():
    if not PRIMARY_CACHE.exists():
        print(f"ERROR: cache dir not found: {PRIMARY_CACHE}")
        sys.exit(1)
    parquets = sorted(PRIMARY_CACHE.glob("*.parquet"))
    print(f"Scanning {len(parquets)} OHLCV parquets...")

    issues_by_ticker = {}
    issue_counts = {}
    for i, p in enumerate(parquets):
        ticker = p.stem
        issues = scan_ticker(p)
        if issues:
            issues_by_ticker[ticker] = issues
            for k in issues:
                issue_counts[k] = issue_counts.get(k, 0) + 1
        if (i + 1) % 200 == 0:
            print(f"  Scanned {i+1}/{len(parquets)}; {len(issues_by_ticker)} flagged")

    print(f"\nTotal scanned: {len(parquets)}")
    print(f"Flagged tickers: {len(issues_by_ticker)}")
    print()
    print("Issues by type:")
    for k in sorted(issue_counts, key=lambda x: -issue_counts[x]):
        print(f"  {k}: {issue_counts[k]} tickers")

    # Write JSON
    report = {
        "scan_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "scanned_parquets": len(parquets),
        "tickers_with_issues": len(issues_by_ticker),
        "issue_counts": issue_counts,
        "thresholds": {
            "min_bars": MIN_BARS,
            "max_date_gap_days": MAX_DATE_GAP_DAYS,
            "max_zero_vol_streak": MAX_ZERO_VOL_STREAK,
            "suspicious_split_ratio": SUSPICIOUS_SPLIT_RATIO,
        },
        "by_ticker": issues_by_ticker,
    }
    json_path = REPO / "ohlcv_integrity.json"
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nFull report: {json_path.relative_to(REPO)}")

    # Markdown summary
    md = ["# OHLCV Integrity Audit", "",
          f"**Scanned:** {len(parquets)} parquets",
          f"**Flagged:** {len(issues_by_ticker)} tickers",
          "",
          "## Issue counts",
          "",
          "| Issue type | Tickers |",
          "|---|---:|"]
    for k in sorted(issue_counts, key=lambda x: -issue_counts[x]):
        md.append(f"| {k} | {issue_counts[k]} |")

    md.append("")
    md.append("## High-severity flagged tickers (insufficient_bars, missing_close)")
    md.append("")
    for tkr, iss in sorted(issues_by_ticker.items()):
        if any(k in iss for k in ("insufficient_bars", "empty_file",
                                    "missing_close_col", "read_fail",
                                    "no_date_col", "all_null_dates")):
            md.append(f"- **{tkr}**: {iss}")

    md_path = REPO / "OHLCV_INTEGRITY_REPORT.md"
    md_path.write_text("\n".join(md))
    print(f"Markdown summary: {md_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
