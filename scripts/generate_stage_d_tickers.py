"""Stage D 150-ticker stratified sampler (Batch 300).

Source: per CHECKLIST #77 canonical-source attribution. Reads from
'Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv'
(canonical PIT universe, Pass 53 DEC-504). Restricts to tickers with
cached Polygon OHLCV at data_prefetch/polygon/ohlcv_daily/.

Purpose: intermediate validation between Stage C smoke (10 tkr x 4y) and
Phase 1A-beta (1937 tkr x 4y). Stratified sample preserves Phase 1A-beta
tier ratios so regression detection is representative.

Tier proportions (Master Dedup 1937 tkrs):
  T3:    993/1937 = 51.3%  ->  77 tkrs
  T1a:   501/1937 = 25.9%  ->  39 tkrs
  T2:    282/1937 = 14.6%  ->  22 tkrs
  T1c:   134/1937 =  6.9%  ->  10 tkrs
  T1ETF:  27/1937 =  1.4%  ->   2 tkrs
  Total:                       150 tkrs

Random seed 42 for reproducibility. SPY auto-included in backtest engine
per Batch 290 fix; no need to force into sample.

Output: scripts/stage_d_tickers.txt (one ticker per line, alphabetized).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
MASTER_CSV = REPO / "Backtesting universe" / \
    "Master Universe_Deduplicated_All Tiers_May 2026.csv"
OHLCV_DIR = REPO / "data_prefetch" / "polygon" / "ohlcv_daily"
OUT_PATH = REPO / "scripts" / "stage_d_tickers.txt"

TIER_QUOTAS = {
    "T3": 77,
    "T1a": 39,
    "T2": 22,
    "T1c": 10,
    "T1ETF": 2,
}
SEED = 42


def main():
    df = pd.read_csv(MASTER_CSV, comment="#")
    cached = {p.stem for p in OHLCV_DIR.glob("*.parquet")}
    df = df[df["Symbol"].isin(cached)].copy()

    picks = []
    for tier, n in TIER_QUOTAS.items():
        pool = df[df["resolved_tier"] == tier]
        if len(pool) < n:
            print(f"WARN tier {tier}: only {len(pool)} available, requested {n}")
            n = len(pool)
        sampled = pool.sample(n=n, random_state=SEED)
        picks.append(sampled)
        print(f"{tier}: {n} sampled from pool of {len(pool)}")

    out = pd.concat(picks).sort_values("Symbol")
    tickers = out["Symbol"].tolist()
    OUT_PATH.write_text("\n".join(tickers) + "\n")

    print(f"\nTotal: {len(tickers)}")
    print(f"Wrote: {OUT_PATH.relative_to(REPO)}")
    print(f"\nComma-joined (for --tickers arg):")
    print(",".join(tickers))


if __name__ == "__main__":
    main()
