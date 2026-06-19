"""B917 (2026-06-19): RESCUE-AND-RETEST per owner directive (g).

# Source: owner directive 2026-06-19 'g' RESCUE-AND-RETEST + B916 6-probe findings +
# `feedback_data_consumption_audit_must_apply_checklist_44b` (#106 #44(b) probes).

Step 1: Coverage map - for each T1a active ticker, % B913-window dates
        where institutional_signal returns non-'none'.

Step 2: Stratified BROAD sample selection (NOT alphabetic-first).
        Picks high-coverage + medium-coverage + low-coverage tickers to
        characterize population.

Step 3: Re-run B913 micropilot on broad sample (via measure_fire_count.py
        invocation handled separately to leverage existing infra).

Discriminates:
- Coverage-gap-confounded (0 fires on alphabetic-first; non-zero on broad)
- Gate-stacking-confirmed (still 0 fires on broad-coverage sample)
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import pandas as pd

from backtest.data.smart_money import institutional_signal


def load_t1a_active(as_of: date) -> list[str]:
    """Load T1a tickers active as of given date (no removed_date OR removed_date > as_of)."""
    csv = REPO / "Backtesting universe" / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"
    df = pd.read_csv(csv, comment="#")
    df["added_date"] = pd.to_datetime(df["added_date"], errors="coerce").dt.date
    df["removed_date"] = pd.to_datetime(df["removed_date"], errors="coerce").dt.date
    mask = (df["added_date"].isna() | (df["added_date"] <= as_of)) & (
        df["removed_date"].isna() | (df["removed_date"] > as_of)
    )
    return sorted(df.loc[mask, "Symbol"].unique().tolist())


def coverage_map(tickers: list[str], window_start: date, window_end: date,
                  sample_freq_days: int = 7) -> dict[str, dict]:
    """For each ticker, count institutional_signal non-none rate in window."""
    out = {}
    for ticker in tickers:
        d = window_start
        total = 0
        non_none = 0
        new_pos_ge_3_count = 0
        while d <= window_end:
            total += 1
            sig = institutional_signal(ticker, d) or {}
            if sig.get("signal", "none") != "none":
                non_none += 1
            new_pos = int(sig.get("new_positions", 0) or 0)
            if new_pos >= 3:
                new_pos_ge_3_count += 1
            d += timedelta(days=sample_freq_days)
        out[ticker] = {
            "total_samples": total,
            "non_none_samples": non_none,
            "pct_non_none": round(100 * non_none / total, 1) if total else 0.0,
            "new_pos_ge_3_samples": new_pos_ge_3_count,
            "pct_new_pos_ge_3": round(100 * new_pos_ge_3_count / total, 1) if total else 0.0,
        }
    return out


def stratified_sample(coverage: dict[str, dict], n_high: int, n_mid: int,
                      n_low: int) -> dict[str, list[str]]:
    """Sort by pct_non_none + pick stratified sample."""
    sorted_t = sorted(coverage.items(), key=lambda kv: kv[1]["pct_non_none"], reverse=True)
    # Categorize
    high = [t for t, c in sorted_t if c["pct_non_none"] >= 80]
    mid = [t for t, c in sorted_t if 30 <= c["pct_non_none"] < 80]
    low = [t for t, c in sorted_t if c["pct_non_none"] < 30]

    # Stratify (deterministic: take first N of each)
    return {
        "high_coverage_>=80pct": high[:n_high],
        "mid_coverage_30_80pct": mid[:n_mid],
        "low_coverage_<30pct": low[:n_low],
        "high_coverage_total": len(high),
        "mid_coverage_total": len(mid),
        "low_coverage_total": len(low),
    }


def main() -> int:
    window_start = date(2024, 9, 1)
    window_end = date(2024, 12, 31)
    sample_as_of = date(2024, 11, 1)  # mid-window PIT-active check

    print(f"B917 RESCUE-AND-RETEST coverage map")
    print(f"Window: {window_start} -> {window_end}")
    print()

    print("Step 1a: Loading T1a active universe...")
    tickers = load_t1a_active(sample_as_of)
    print(f"  T1a active as of {sample_as_of}: {len(tickers)} tickers")
    print()

    print("Step 1b: Computing coverage map (this takes a few minutes)...")
    coverage = coverage_map(tickers, window_start, window_end, sample_freq_days=14)

    # Summary stats
    pcts = [c["pct_non_none"] for c in coverage.values()]
    pcts_sorted = sorted(pcts, reverse=True)
    n = len(pcts)
    summary = {
        "ticker_count": n,
        "mean_coverage_pct": round(sum(pcts) / n, 1) if n else 0,
        "median_coverage_pct": pcts_sorted[n // 2] if n else 0,
        "p25_coverage_pct": pcts_sorted[(3 * n) // 4] if n else 0,
        "p75_coverage_pct": pcts_sorted[n // 4] if n else 0,
        "count_high_coverage_>=80pct": sum(1 for p in pcts if p >= 80),
        "count_mid_coverage_30_80pct": sum(1 for p in pcts if 30 <= p < 80),
        "count_low_coverage_<30pct": sum(1 for p in pcts if p < 30),
        "count_zero_coverage": sum(1 for p in pcts if p == 0),
    }
    print(f"\nCoverage summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print()
    print("Step 2: Stratified BROAD sample selection...")
    sample = stratified_sample(coverage, n_high=5, n_mid=3, n_low=2)
    selected = (sample["high_coverage_>=80pct"] + sample["mid_coverage_30_80pct"]
                + sample["low_coverage_<30pct"])
    print(f"  Stratified sample (10 tickers):")
    print(f"    HIGH coverage (>=80%): {sample['high_coverage_>=80pct']}")
    print(f"    MID coverage (30-80%): {sample['mid_coverage_30_80pct']}")
    print(f"    LOW coverage (<30%): {sample['low_coverage_<30pct']}")
    print()
    print(f"  Per-ticker coverage detail:")
    for t in selected:
        c = coverage[t]
        print(f"    {t:6s} non-none={c['pct_non_none']:5.1f}% / "
              f"new_pos>=3={c['pct_new_pos_ge_3']:5.1f}% "
              f"({c['non_none_samples']}/{c['total_samples']} samples)")
    print()
    print("Step 3 launch command (for next batch):")
    print(f"  python scripts/measure_fire_count.py \\\n"
          f"    --strategies institutional_high_conviction_long "
          f"institutional_recent_init_momentum_long "
          f"institutional_recent_init_volume_long \\\n"
          f"    --tickers {' '.join(selected)} \\\n"
          f"    --start {window_start} --end {window_end} \\\n"
          f"    --output output_audit/b917_arch1_broad_sample_micropilot.json")

    # Save full result
    out = {
        "step": "B917 Step 1+2 coverage map + stratified sample",
        "window": [str(window_start), str(window_end)],
        "summary": summary,
        "stratified_sample": sample,
        "selected_sample": selected,
        "coverage": coverage,
    }
    out_path = REPO / "output_audit" / "b917_coverage_map_rescue_retest.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
