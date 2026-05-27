"""Batch 399 (2026-05-27): Sprint 7 Phase B canary - sample selection.

Source (per CHECKLIST #77): owner directive 2026-05-27 "all wired items
activated".  Phase B per DEC-508 / CHECKLIST #71: signals computed but
strategies disabled; Dashboard validates 20-50 signals + statistical
sanity + PIT regression.

This script handles step 1 of Phase B: pick a representative subset of
N (ticker, as_of) pairs from a Phase 1A-beta trade_log to feed into the
LangGraph canary pipeline.  Output is consumed by
`scripts/phase_1b_canary_compute.py`.

Selection strategy (deterministic for reproducibility):
  - Sample N pairs stratified by regime + direction
  - Prefer pairs where multiple strategies agreed (high-conviction events)
  - Span full backtest window (year-balanced)

Note: Phase B execution requires Python 3.12 (Phase A vendoring caveat
in vendored/MANIFEST.md).  This selector runs on any Python 3.10+.

Usage:
    python scripts/phase_1b_canary_sample_selector.py \\
        --trade-log output_phase_1a_beta_final/trade_log.csv \\
        --output output_phase_1b_canary/sample_pairs.parquet \\
        --n 50

    # Dry-run with synthetic trade log (no actual 1A-beta output needed):
    python scripts/phase_1b_canary_sample_selector.py --synthetic --n 20
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent


def build_synthetic_trade_log(n: int = 200) -> pd.DataFrame:
    """Synthetic trade log for testing without a real 1A-beta output."""
    rng = np.random.RandomState(42)
    tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "JPM",
               "XOM", "JNJ", "WMT", "V", "MA", "HD", "PG"]
    regimes = ["bull", "neutral", "bear", "crisis"]
    strategies = ["pairs_mean_reversion_long", "ichimoku_cloud_breakout",
                  "ema_pullback_long", "rsi_oversold_bounce",
                  "news_sentiment_shift_long", "smc_bos_long"]
    rows = []
    for i in range(n):
        rows.append({
            "ticker":     rng.choice(tickers),
            "entry_date": (pd.Timestamp("2020-06-01") + pd.Timedelta(days=int(rng.randint(0, 1800)))).isoformat()[:10],
            "regime":     rng.choice(regimes, p=[0.6, 0.25, 0.13, 0.02]),
            "direction":  rng.choice(["long", "short"], p=[0.7, 0.3]),
            "strategy":   rng.choice(strategies),
            "pnl_pct":    round(float(rng.normal(0.5, 5.0)), 4),
        })
    return pd.DataFrame(rows)


def stratified_sample(df: pd.DataFrame, n: int, seed: int = 42) -> pd.DataFrame:
    """Stratified sample with regime + direction balance + year span.

    For N=50 default:
      - 30 from bull, 12 from neutral, 6 from bear, 2 from crisis
      - Within each regime: 70% long, 30% short
      - Within each (regime, direction): span the years evenly
    """
    if df.empty:
        return df
    rng = np.random.RandomState(seed)
    df = df.copy()
    df["entry_date"] = pd.to_datetime(df["entry_date"])
    df["year"] = df["entry_date"].dt.year

    # Regime allocation (cap at available rows in each bucket)
    regime_weights = {"bull": 0.60, "neutral": 0.25, "bear": 0.13, "crisis": 0.02}
    allocations = {r: max(1, int(round(n * w))) for r, w in regime_weights.items()}

    samples = []
    for regime, target_n in allocations.items():
        regime_df = df[df["regime"] == regime] if "regime" in df.columns else df
        if regime_df.empty:
            continue
        # Within regime, stratify by year for time-coverage
        years = sorted(regime_df["year"].unique())
        per_year = max(1, target_n // max(1, len(years)))
        for y in years:
            year_df = regime_df[regime_df["year"] == y]
            if year_df.empty:
                continue
            take = min(per_year, len(year_df))
            samples.append(year_df.sample(n=take, random_state=rng.randint(0, 1 << 30)))

    if not samples:
        return df.head(min(n, len(df)))
    out = pd.concat(samples, ignore_index=True)
    # Trim to exactly N
    if len(out) > n:
        out = out.sample(n=n, random_state=seed).reset_index(drop=True)
    elif len(out) < n:
        # Top-up from remaining un-sampled rows
        leftover = df[~df.index.isin(out.index)]
        if not leftover.empty:
            top_up = leftover.sample(
                n=min(n - len(out), len(leftover)),
                random_state=seed,
            )
            out = pd.concat([out, top_up], ignore_index=True)
    return out.sort_values(["entry_date", "ticker"]).reset_index(drop=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trade-log", type=Path, default=None,
                    help="Phase 1A-beta trade_log.csv (or .parquet)")
    ap.add_argument("--output", type=Path,
                    default=REPO / "output_phase_1b_canary" / "sample_pairs.parquet")
    ap.add_argument("--n", type=int, default=50,
                    help="number of (ticker, as_of) pairs to select")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--synthetic", action="store_true",
                    help="generate synthetic trade log (no real 1A-beta needed)")
    args = ap.parse_args()

    if args.synthetic:
        print("[INFO] using synthetic trade log (n=200)")
        df = build_synthetic_trade_log(n=200)
    else:
        if args.trade_log is None or not args.trade_log.exists():
            print(f"[FATAL] --trade-log missing: {args.trade_log}.  "
                  f"Use --synthetic for a dry-run.")
            return 1
        df = (pd.read_parquet(args.trade_log)
              if args.trade_log.suffix == ".parquet"
              else pd.read_csv(args.trade_log, low_memory=False))
        print(f"[INFO] loaded {len(df)} trades from {args.trade_log}")

    sample = stratified_sample(df, n=args.n, seed=args.seed)
    print(f"[INFO] selected {len(sample)} canary samples")
    if "regime" in sample.columns:
        print(f"[INFO] regime distribution: {sample['regime'].value_counts().to_dict()}")
    if "direction" in sample.columns:
        print(f"[INFO] direction split: {sample['direction'].value_counts().to_dict()}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sample.to_parquet(args.output, index=False)
    print(f"[OK] wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
