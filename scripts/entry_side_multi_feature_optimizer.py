#!/usr/bin/env python3
"""Batch 521 (2026-05-31) -- entry-side MULTI-FEATURE threshold optimizer.

Source: per CHECKLIST #77 + EXECUTION_QUEUE.md #9 1a-alpha-gate fallback +
DET1-unblock note "what else can be done while P17a runs" (autonomous
batch series).
Queue rows: #9 1a-alpha-gate-decision-r3 (entry-side optimization);
extends Batch 501 (`entry_side_threshold_optimizer.py`).

Purpose: Batch 501 scored SINGLE-feature entry filters (e.g.
`macro_neutral`) and produced a per-strategy ranked candidate list.
This script extends that to PAIRWISE combinations
(e.g. `macro_neutral + sm_score_le_0`) and surfaces combinations where
the joint filter beats either single-feature filter alone. The use case
is owner-decision input for R4 cube spec -- multi-feature gates may
unlock strategies that single filters can't get above the 1A-alpha
Sharpe>=0.7 bar.

Method:

  for each strategy in BATCH_414_STRATEGIES:
    baseline_sharpe = sharpe(strategy trades)
    for each ordered pair (feature_A, feature_B) with A != B:
      for each (bucket_A, bucket_B):
        joint_mask = bucket_A_mask AND bucket_B_mask
        if n_post_filter >= MIN_N:
          compute joint_sharpe, joint_wr, joint_pnl
          lift_vs_baseline = joint_sharpe - baseline_sharpe
          lift_vs_single_A = joint_sharpe - sharpe(bucket_A_mask only)
          lift_vs_single_B = joint_sharpe - sharpe(bucket_B_mask only)
          incremental_lift = min(lift_vs_single_A, lift_vs_single_B)
        emit row

Output ranking: incremental_lift (joint MUST beat BOTH single-feature
filters to be interesting; if one single-feature already gives the
same lift, the pair adds nothing).

NO re-run required. Pure post-processing on existing trade_log.csv.
"""
from __future__ import annotations

import argparse
from itertools import combinations
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parent.parent

# Same 9 strategies as Batch 501 (the 1A-alpha gate-lock candidates)
BATCH_414_STRATEGIES = (
    "bollinger_tight", "xs_momentum_top_decile", "cmf_flip",
    "monthly_bias_momentum_long", "xs_quality_top_quintile_long",
    "pead_long", "pairs_mean_reversion_long", "adx_initiation",
    "xs_low_beta_long",
)


def _sharpe_approx(pnls: np.ndarray) -> float:
    """Per-trade Sharpe approximation (consistent w/ Batch 501)."""
    if len(pnls) < 2:
        return 0.0
    s = float(pnls.std(ddof=1))
    if s == 0:
        return 0.0
    return float(pnls.mean() / s * np.sqrt(252))


def _feature_buckets():
    """Identical bucket definitions to Batch 501 so single-vs-pair
    comparisons stay apples-to-apples."""
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


def _per_strategy_baseline(trades: pd.DataFrame) -> dict:
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


def _single_bucket_stats(sub: pd.DataFrame, mask) -> dict | None:
    filt = sub[mask]
    if len(filt) < 2:
        return None
    pnls = filt["pnl_pct"].astype(float).values
    return {
        "n":      int(len(filt)),
        "wr":     float((filt["win"] > 0).mean()),
        "pnl":    float(pnls.mean()),
        "sharpe": _sharpe_approx(pnls),
    }


def optimize_pairwise(
    trades: pd.DataFrame,
    strategies: Iterable[str] = BATCH_414_STRATEGIES,
    min_n_post_filter: int = 30,
) -> pd.DataFrame:
    """Score pairwise (feature_A_bucket, feature_B_bucket) joints.

    Output is ranked by `incremental_lift`: joint Sharpe MUST exceed
    BOTH single-feature Sharpes to make the cell appear with a
    positive incremental_lift -- that's the criterion for owner-pick
    as a multi-feature R4 gate.
    """
    baselines = _per_strategy_baseline(trades)
    bucket_specs = _feature_buckets()
    rows = []
    features = sorted(bucket_specs.keys())

    for strat in strategies:
        sub = trades[trades["strategy"] == strat]
        if sub.empty or strat not in baselines:
            continue
        base = baselines[strat]
        # Pre-compute single-bucket masks + stats so the pair loop can
        # reuse them
        bucket_index: dict[str, dict] = {}
        for feat, buckets in bucket_specs.items():
            if feat not in sub.columns:
                continue
            for label, mask_fn in buckets:
                try:
                    mask = mask_fn(sub)
                except Exception:
                    continue
                stats = _single_bucket_stats(sub, mask)
                if stats is None:
                    continue
                bucket_index[f"{feat}::{label}"] = {
                    "feat":   feat,
                    "label":  label,
                    "mask":   mask,
                    **stats,
                }

        # Iterate unordered pairs (A, B) where A.feature < B.feature
        # (avoid double-counting; never combine 2 buckets of same feature)
        keys = list(bucket_index.keys())
        for k_a, k_b in combinations(keys, 2):
            a, b = bucket_index[k_a], bucket_index[k_b]
            if a["feat"] == b["feat"]:
                continue
            joint = sub[a["mask"] & b["mask"]]
            if len(joint) < min_n_post_filter:
                continue
            pnls = joint["pnl_pct"].astype(float).values
            j_sharpe = _sharpe_approx(pnls)
            j_wr     = float((joint["win"] > 0).mean())
            j_pnl    = float(pnls.mean())
            lift_vs_baseline   = j_sharpe - base["sharpe_baseline"]
            lift_vs_single_a   = j_sharpe - a["sharpe"]
            lift_vs_single_b   = j_sharpe - b["sharpe"]
            incremental_lift   = min(lift_vs_single_a, lift_vs_single_b)
            rows.append({
                "strategy":             strat,
                "feature_a":            a["feat"],
                "bucket_a":             a["label"],
                "feature_b":            b["feat"],
                "bucket_b":             b["label"],
                "n_joint":              int(len(joint)),
                "n_single_a":           a["n"],
                "n_single_b":           b["n"],
                "n_baseline":           base["n_baseline"],
                "wr_baseline":          round(base["wr_baseline"], 4),
                "wr_joint":             round(j_wr, 4),
                "pnl_baseline":         round(base["pnl_baseline"], 4),
                "pnl_joint":            round(j_pnl, 4),
                "sharpe_baseline":      round(base["sharpe_baseline"], 4),
                "sharpe_single_a":      round(a["sharpe"], 4),
                "sharpe_single_b":      round(b["sharpe"], 4),
                "sharpe_joint":         round(j_sharpe, 4),
                "lift_vs_baseline":     round(lift_vs_baseline, 4),
                "lift_vs_single_a":     round(lift_vs_single_a, 4),
                "lift_vs_single_b":     round(lift_vs_single_b, 4),
                "incremental_lift":     round(incremental_lift, 4),
                "wr_lift_pp":           round((j_wr - base["wr_baseline"]) * 100, 2),
            })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.sort_values("incremental_lift", ascending=False).reset_index(drop=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--trade-log", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--min-n", type=int, default=30,
                   help="minimum joint-filtered-trade count to keep a row")
    p.add_argument("--strategies", nargs="*", default=None,
                   help="strategies to score (default = 9 Batch-414 candidates)")
    p.add_argument("--top-n", type=int, default=20,
                   help="rows printed to stdout (full CSV always written)")
    args = p.parse_args()

    if not args.trade_log.exists():
        raise FileNotFoundError(args.trade_log)
    trades = pd.read_csv(args.trade_log, low_memory=False)
    strategies = args.strategies or BATCH_414_STRATEGIES
    df = optimize_pairwise(trades, strategies, args.min_n)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"wrote {args.output} -- {len(df)} (strategy, feature_a, feature_b) rows")
    if not df.empty:
        print(f"\nTop {args.top_n} incremental-lift pairs (joint beats BOTH singles):")
        cols = ["strategy", "feature_a", "bucket_a", "feature_b", "bucket_b",
                "n_joint", "sharpe_baseline", "sharpe_single_a",
                "sharpe_single_b", "sharpe_joint", "incremental_lift"]
        print(df.head(args.top_n)[cols].to_string(index=False))


if __name__ == "__main__":
    main()
