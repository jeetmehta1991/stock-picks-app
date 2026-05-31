#!/usr/bin/env python3
"""Batch 501 (2026-05-31) -- entry-side threshold optimizer (Dim A).

Source: per CHECKLIST #77 + owner directive 2026-05-31 ("loop back to
entry-side optimization since 1A-alpha gate LOCKED at OOS Sharpe 0.406
< 0.7").
Queue rows: EXECUTION_QUEUE.md items #9 1a-alpha-gate-decision-r3
fallback (entry-side optimization) + indirectly unblocks R4 cube.

Purpose: WITHOUT re-running the cube, identify entry-time filters that
would have improved OOS Sharpe for the 9 Batch-414 candidate
strategies (the ones that LOCK 1A-alpha today at max OOS Sharpe
0.406). The output is a per-strategy ranked list of single-feature
threshold filters where applying the filter retroactively to the
existing trade log would have raised that strategy's effective OOS
Sharpe.

Features scanned (all readable from output_batch395_final/trade_log.csv):
  smart_money_score      (>0 / <=0)
  macro_score            (negative / neutral / positive)
  sentiment_score        (negative / neutral / positive)
  confidence_tier        (per-tier)
  regime                 (per regime)
  days_to_earnings       (bucketed)
  circuit_breaker_level  (per level)

For each strategy x feature x threshold/bucket combo, compute:
  - n_filtered     : trades surviving filter
  - filtered_wr    : win rate post-filter
  - filtered_pnl   : average pnl_pct post-filter
  - filtered_sharpe: per-trade approximation
  - lift           : (filtered_sharpe - baseline_sharpe)

Output a ranked CSV `output_batch395_final/entry_threshold_candidates.csv`
sorted by lift. Owner uses this to pick which thresholds to wire into
the R4 cube spec OR to add to STRATEGY_EXIT_OVERRIDE entries.

NO re-run required. Pure post-processing on existing trade_log.csv.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parent.parent

# Strategies whose entry-side thresholds drive the 1A-alpha gate
BATCH_414_STRATEGIES = (
    "bollinger_tight", "xs_momentum_top_decile", "cmf_flip",
    "monthly_bias_momentum_long", "xs_quality_top_quintile_long",
    "pead_long", "pairs_mean_reversion_long", "adx_initiation",
    "xs_low_beta_long",
)


def _sharpe_approx(pnls: np.ndarray) -> float:
    """Per-trade Sharpe approximation: mean / std * sqrt(252 / avg_hold).

    Caller passes pre-filtered pnl_pct values. Hold-days adjustment is
    intentionally omitted -- this is a RANKING metric not an absolute
    Sharpe (consistent across strategies for relative comparison).
    """
    if len(pnls) < 2:
        return 0.0
    s = float(pnls.std(ddof=1))
    if s == 0:
        return 0.0
    return float(pnls.mean() / s * np.sqrt(252))


def _baseline_per_strategy(trades: pd.DataFrame) -> dict:
    """Compute baseline (no-filter) stats per strategy."""
    out: dict = {}
    for strat, sub in trades.groupby("strategy"):
        pnls = sub["pnl_pct"].astype(float).values
        out[strat] = {
            "n_baseline":      int(len(sub)),
            "wr_baseline":     float((sub["win"] > 0).mean()),
            "pnl_baseline":    float(pnls.mean()),
            "sharpe_baseline": _sharpe_approx(pnls),
        }
    return out


def _feature_buckets():
    """Per-feature bucket definitions. Each yields (label, mask_fn)."""
    return {
        "smart_money_score": [
            ("sm_score_gt_0", lambda df: pd.to_numeric(
                df["smart_money_score"], errors="coerce") > 0),
            ("sm_score_le_0", lambda df: pd.to_numeric(
                df["smart_money_score"], errors="coerce") <= 0),
        ],
        "macro_score": [
            ("macro_negative",  lambda df: pd.to_numeric(df["macro_score"],
                                                          errors="coerce") < 0),
            ("macro_neutral",   lambda df: pd.to_numeric(df["macro_score"],
                                                          errors="coerce") == 0),
            ("macro_positive",  lambda df: pd.to_numeric(df["macro_score"],
                                                          errors="coerce") > 0),
        ],
        "sentiment_score": [
            ("sentiment_negative", lambda df: pd.to_numeric(
                df["sentiment_score"], errors="coerce") < 0),
            ("sentiment_neutral",  lambda df: pd.to_numeric(
                df["sentiment_score"], errors="coerce") == 0),
            ("sentiment_positive", lambda df: pd.to_numeric(
                df["sentiment_score"], errors="coerce") > 0),
        ],
        "confidence_tier": [
            (f"tier_{t}", (lambda df, _t=t: df["confidence_tier"] == _t))
            for t in ("LOW", "MEDIUM", "MEDIUM-HIGH", "HIGH",
                      "VERY HIGH", "EXCEPTIONAL")
        ],
        "regime": [
            ("regime_bull",    lambda df: df["regime"] == "bull"),
            ("regime_neutral", lambda df: df["regime"] == "neutral"),
            ("regime_bear",    lambda df: df["regime"] == "bear"),
            ("regime_crisis",  lambda df: df["regime"].astype(str)
                                                 .str.contains("crisis", na=False)),
        ],
        "days_to_earnings": [
            ("days_to_earn_0_5",   lambda df: (pd.to_numeric(
                df["days_to_earnings"], errors="coerce") >= 0) & (
                pd.to_numeric(df["days_to_earnings"], errors="coerce") <= 5)),
            ("days_to_earn_6_15",  lambda df: (pd.to_numeric(
                df["days_to_earnings"], errors="coerce") > 5) & (
                pd.to_numeric(df["days_to_earnings"], errors="coerce") <= 15)),
            ("days_to_earn_over_15", lambda df: pd.to_numeric(
                df["days_to_earnings"], errors="coerce") > 15),
        ],
    }


def optimize_entry_thresholds(
    trades: pd.DataFrame,
    strategies: Iterable[str] = BATCH_414_STRATEGIES,
    min_n_post_filter: int = 30,
) -> pd.DataFrame:
    """Compute per (strategy, feature_bucket) lift over baseline.

    Returns a DataFrame ranked by lift (filtered_sharpe - sharpe_baseline)
    descending. Buckets with fewer than `min_n_post_filter` filtered
    trades are dropped.
    """
    baselines = _baseline_per_strategy(trades)
    buckets = _feature_buckets()
    rows = []
    for strat in strategies:
        sub = trades[trades["strategy"] == strat]
        if sub.empty or strat not in baselines:
            continue
        base = baselines[strat]
        for feature, bucket_list in buckets.items():
            if feature not in sub.columns:
                continue
            for label, mask_fn in bucket_list:
                try:
                    mask = mask_fn(sub)
                except Exception:
                    continue
                filt = sub[mask]
                if len(filt) < min_n_post_filter:
                    continue
                pnls = filt["pnl_pct"].astype(float).values
                f_sharpe = _sharpe_approx(pnls)
                f_wr = float((filt["win"] > 0).mean())
                f_pnl = float(pnls.mean())
                rows.append({
                    "strategy":         strat,
                    "feature":          feature,
                    "bucket":           label,
                    "n_filtered":       int(len(filt)),
                    "n_baseline":       base["n_baseline"],
                    "wr_baseline":      round(base["wr_baseline"], 4),
                    "wr_filtered":      round(f_wr, 4),
                    "pnl_baseline":     round(base["pnl_baseline"], 4),
                    "pnl_filtered":     round(f_pnl, 4),
                    "sharpe_baseline":  round(base["sharpe_baseline"], 4),
                    "sharpe_filtered":  round(f_sharpe, 4),
                    "lift":             round(f_sharpe - base["sharpe_baseline"], 4),
                    "wr_lift_pp":       round((f_wr - base["wr_baseline"]) * 100, 2),
                })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.sort_values("lift", ascending=False).reset_index(drop=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--trade-log", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--min-n", type=int, default=30,
                   help="minimum filtered-trade count to keep a bucket")
    p.add_argument("--strategies", nargs="*", default=None,
                   help="strategies to score (default = 9 Batch-414 candidates)")
    args = p.parse_args()

    if not args.trade_log.exists():
        raise FileNotFoundError(args.trade_log)
    trades = pd.read_csv(args.trade_log, low_memory=False)
    strategies = args.strategies or BATCH_414_STRATEGIES
    df = optimize_entry_thresholds(trades, strategies, args.min_n)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"wrote {args.output} -- {len(df)} (strategy, feature, bucket) rows")
    if not df.empty:
        # Print top 20 positive-lift candidates
        print("\nTop 20 lift candidates:")
        cols = ["strategy", "feature", "bucket", "n_filtered",
                "sharpe_baseline", "sharpe_filtered", "lift", "wr_lift_pp"]
        print(df.head(20)[cols].to_string(index=False))


if __name__ == "__main__":
    main()
