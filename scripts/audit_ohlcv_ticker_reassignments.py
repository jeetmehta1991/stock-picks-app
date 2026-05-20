"""scripts/audit_ohlcv_ticker_reassignments.py - Batch 276 audit.

Scans every OHLCV parquet for sudden price jumps that indicate ticker
reassignment (a different company using the same ticker symbol in a
different time period). The META case (Meta Materials -> Meta Platforms
on 2022-06-09) caused a -1219% loss in Stage B smoke before being caught
manually; this audit finds the rest before they cost backtest validity.

Detection method:
  For each parquet, sort by date and compute day-over-day close ratio.
  Flag any single-day ratio > 5x or < 0.2x as a candidate reassignment.
  Normal stock splits typically produce ratios in [0.1, 0.5] (forward
  split 2:1, 3:1, 4:1, ...) or [2, 5] (reverse split). Beyond that
  range strongly suggests a different security.

Per CLAUDE.md - this is an audit / read-only investigation; produces a
report. Does NOT modify any parquets. The owner reviews the report and
decides which to fix (case-by-case, since each reassignment has its own
correct boundary date).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

# Common stock-split ratios. Anything outside this range is suspicious.
SPLIT_FORWARD_MIN = 0.05   # 20:1 forward (rare but possible)
SPLIT_REVERSE_MAX = 20.0   # 1:20 reverse (rare but possible)

# Run from repo root
REPO = Path(__file__).resolve().parent.parent

# Primary cache (production-canonical per Sprint 0A); MASTER source of truth.
PRIMARY_CACHE = REPO / "data_prefetch" / "polygon" / "ohlcv_daily"


def scan_parquet(path: Path) -> list[dict]:
    """Scan one parquet for day-over-day close-ratio anomalies.
    Returns list of anomaly dicts (empty if clean)."""
    try:
        df = pd.read_parquet(path)
    except Exception as exc:
        return [{"path": str(path.relative_to(REPO)), "error": f"read_fail: {exc}"}]
    if df.empty or "close" not in df.columns:
        return []
    # Normalize date col
    if "date" in df.columns:
        df["dt"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        try:
            df["dt"] = pd.to_datetime(df.index)
        except Exception:
            return []
    df = df.dropna(subset=["dt"]).sort_values("dt").reset_index(drop=True)
    if len(df) < 2:
        return []
    # Day-over-day close ratio
    df["close_ratio"] = df["close"] / df["close"].shift(1)
    anomalies = df[
        (df["close_ratio"] > SPLIT_REVERSE_MAX)
        | (df["close_ratio"] < SPLIT_FORWARD_MIN)
    ]
    if anomalies.empty:
        return []
    ticker = path.stem
    out = []
    for _, row in anomalies.iterrows():
        out.append({
            "ticker": ticker,
            "date": row["dt"].strftime("%Y-%m-%d"),
            "prior_close": round(float(df.iloc[max(0, row.name-1)]["close"]), 2),
            "this_close": round(float(row["close"]), 2),
            "ratio": round(float(row["close_ratio"]), 2),
            "direction": "UP" if row["close_ratio"] > 1 else "DOWN",
            "magnitude_pct": round(abs(row["close_ratio"] - 1) * 100, 0),
        })
    return out


def main():
    print("=" * 70)
    print("Batch 276: OHLCV ticker-reassignment audit")
    print(f"  Scanning: {PRIMARY_CACHE}")
    print(f"  Detection: day-over-day close ratio > {SPLIT_REVERSE_MAX}x "
          f"or < {SPLIT_FORWARD_MIN}x")
    print("=" * 70)

    if not PRIMARY_CACHE.exists():
        print(f"ERROR: cache dir not found: {PRIMARY_CACHE}")
        sys.exit(1)

    parquets = sorted(PRIMARY_CACHE.glob("*.parquet"))
    print(f"\nFound {len(parquets)} ticker parquets to scan.\n")

    all_anomalies = []
    for i, path in enumerate(parquets):
        anomalies = scan_parquet(path)
        if anomalies:
            all_anomalies.extend(anomalies)
        if (i + 1) % 200 == 0:
            print(f"  Scanned {i+1}/{len(parquets)} parquets; "
                  f"{len(all_anomalies)} anomalies so far")

    print(f"\nScanned {len(parquets)} parquets. "
          f"Found {len(all_anomalies)} suspect events.")
    print()
    if not all_anomalies:
        print("CLEAN: no ticker-reassignment candidates detected.")
        return

    # Group by ticker
    by_ticker: dict = {}
    for a in all_anomalies:
        by_ticker.setdefault(a["ticker"], []).append(a)

    # Sort tickers by max-magnitude event
    sorted_tickers = sorted(
        by_ticker.keys(),
        key=lambda t: max(abs(e["ratio"] - 1) for e in by_ticker[t]),
        reverse=True,
    )

    print("=" * 70)
    print(f"SUSPECTS - {len(by_ticker)} unique tickers with anomalies:")
    print("=" * 70)
    for tkr in sorted_tickers:
        events = by_ticker[tkr]
        events_sorted = sorted(events,
                                key=lambda e: abs(e["ratio"] - 1),
                                reverse=True)
        print(f"\n  {tkr} ({len(events)} events):")
        for e in events_sorted[:3]:   # top 3 most extreme per ticker
            print(f"    {e['date']}: close ${e['prior_close']:>9.2f} -> ${e['this_close']:>9.2f} "
                  f"ratio={e['ratio']:>6.2f} ({e['direction']} {e['magnitude_pct']:.0f}%)")

    # Write JSON report
    report_path = REPO / "TICKER_REASSIGNMENT_AUDIT_2026_05_20.json"
    report = {
        "scan_date": "2026-05-20",
        "scanned_parquets": len(parquets),
        "tickers_with_anomalies": len(by_ticker),
        "total_anomaly_events": len(all_anomalies),
        "detection_thresholds": {
            "forward_split_floor": SPLIT_FORWARD_MIN,
            "reverse_split_ceiling": SPLIT_REVERSE_MAX,
        },
        "by_ticker": by_ticker,
    }
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nFull report -> {report_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
