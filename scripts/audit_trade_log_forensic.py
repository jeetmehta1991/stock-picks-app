"""Comprehensive forensic audit of a trade_log CSV.

Source: per CHECKLIST #77 canonical-source attribution. Owner-directed
post-Batch-303 audit of Stage C v4 / Stage D v2 outputs covering five
dimensions:

  1. INPUTS WIRED & ROUTING - which signal/macro/smart-money columns are
     populated vs silently null (BUG-286 silent-gap pattern detector at
     the trade-log layer)
  2. STRATEGIES FIRING - distribution per strategy, regime, direction
  3. EXITS DISPATCHING - exit_reason distribution vs STRATEGY_EXIT_OVERRIDE
     configuration
  4. DATA CORRUPTION - impossible PnL (>500% or <-100%), negative holds,
     exit-before-entry, NaN in critical fields, META-pattern detector
  5. OUTCOMES LOGICAL - PnL distribution, win rate / mean by regime,
     hold-duration vs exit-method sanity

Usage:
  python scripts/audit_trade_log_forensic.py --input output_stage_d/trade_log_checkpoint.csv
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def section(title: str):
    print()
    print("=" * 78)
    print(f"  {title}")
    print("=" * 78)


def subsection(title: str):
    print()
    print(f"  --- {title} ---")


def audit(path: Path):
    if not path.exists():
        print(f"ERROR: {path} not found")
        sys.exit(1)
    df = pd.read_csv(path, low_memory=False)
    n = len(df)
    print(f"Loaded {n} trades from {path}")

    findings = {"OK": [], "WARN": [], "FAIL": []}

    # =========================================================================
    # SECTION 1 - INPUTS WIRED & ROUTING
    # =========================================================================
    section("1. INPUTS WIRED & ROUTING")

    expected_cols = [
        "ticker", "entry_date", "exit_date", "direction", "strategy",
        "category", "sector", "confidence_tier", "regime", "exit_reason",
        "entry_price", "exit_price", "initial_stop", "trailing_stop_at_exit",
        "pnl_pct", "pnl_dollar", "win", "hold_days",
        "max_adverse_excursion", "max_favourable_excursion",
        "signals_at_entry", "smart_money_score", "macro_score",
        "sentiment_score", "congressional_signal", "insider_signal",
        "institutional_signal", "aaii_signal", "cnn_fg_score",
    ]
    missing_cols = [c for c in expected_cols if c not in df.columns]
    if missing_cols:
        findings["FAIL"].append(f"Missing columns: {missing_cols}")
        print(f"  [FAIL] Missing required columns: {missing_cols}")
    else:
        findings["OK"].append("All 29 critical columns present")
        print(f"  [OK] All 29 critical trade-log columns present")

    subsection("Column population rates (silent-default detector)")
    consume_columns = {
        "regime":               "regime classifier wired (Batches 288-292)",
        "smart_money_score":    "smart_money signal aggregator",
        "congressional_signal": "Quiver congressional",
        "insider_signal":       "Quiver insider / SEC Form 4",
        "institutional_signal": "Quiver 13F (Batch 294 historical path)",
        "aaii_signal":          "AAII bearish/bullish",
        "cnn_fg_score":         "CNN Fear & Greed",
        "macro_score":          "macro composite",
        "sentiment_score":      "news/sentiment aggregator",
    }
    # Batch 365 Item 2 (owner-approved 2026-05-25): semantic-population check.
    # The pre-Batch-365 "populated" check used .notna() which counts default
    # sentinels (0 numeric, "none" string) as populated. Result: smart_money_
    # score=0 across 7,191 trades (Batch 363 silent gap) was reported as
    # "[OK] smart_money_score 100% populated" -- masking the silent gap for
    # all of Phase 1A. Semantic check below distinguishes "non-default" from
    # "any-value" so silent-default columns flag as [FAIL].
    DEFAULT_SENTINELS = {
        # numeric defaults (treat == 0 as un-fired)
        "smart_money_score": 0,
        "macro_score":       0,
        "sentiment_score":   0,
        "cnn_fg_score":      0,
        "aaii_signal":       0,
        # string defaults (treat == "none" as un-fired)
        "congressional_signal": "none",
        "insider_signal":       "none",
        "institutional_signal": "none",
    }

    for col, desc in consume_columns.items():
        if col not in df.columns:
            findings["WARN"].append(f"Column {col} missing")
            print(f"  [WARN] {col!s:25s} MISSING - {desc}")
            continue
        series = df[col]
        if series.dtype == object:
            distinct = series.astype(str).str.strip().unique()
            non_empty = series.astype(str).str.strip().replace("", np.nan)
            populated = non_empty.notna().sum()
        else:
            populated = series.notna().sum()
            distinct = pd.Series(series.dropna().unique())
        pct = 100.0 * populated / n
        # Semantic-non-default check
        sentinel = DEFAULT_SENTINELS.get(col)
        if sentinel is not None:
            if series.dtype == object:
                non_default = (series.astype(str).str.strip() != str(sentinel)).sum()
            else:
                # Numeric: any value with abs > tiny epsilon counts as non-default
                non_default = (pd.to_numeric(series, errors="coerce").fillna(0).abs() > 1e-9).sum()
            sem_pct = 100.0 * non_default / n
        else:
            sem_pct = pct  # No registered sentinel; semantic = literal

        # Gate semantic-non-default at 5% min for known signal columns
        sem_marker = "[OK]" if sem_pct >= 50 else ("[WARN]" if sem_pct >= 5 else "[FAIL]")
        sem_bucket = "OK" if sem_pct >= 50 else ("WARN" if sem_pct >= 5 else "FAIL")
        findings[sem_bucket].append(
            f"{col}: literal={pct:.0f}% populated / semantic={sem_pct:.1f}% non-default"
        )
        sample = ",".join([str(x)[:20] for x in distinct[:5]])
        sentinel_note = f" (default={sentinel!r})" if sentinel is not None else ""
        print(f"  {sem_marker:6s} {col!s:25s} literal={pct:5.1f}% / semantic={sem_pct:5.1f}% non-default{sentinel_note}  e.g. {sample}")

    subsection("Regime distribution (Batch 288/292 gate verification)")
    if "regime" in df.columns:
        regime_counts = df["regime"].value_counts(dropna=False)
        for r, c in regime_counts.items():
            print(f"  {r!s:25s} {c:5d}  ({100*c/n:5.1f}%)")
        if "bear" in regime_counts.index and regime_counts["bear"] > 0:
            findings["OK"].append(
                f"bear regime fired {regime_counts.get('bear', 0)} times (Batch 288 SPY-only gate working)"
            )
            print(f"  [OK] bear regime active - Batch 288/289 fix delivered")
        else:
            findings["FAIL"].append("bear regime never fired - Batch 288 fix may have regressed")
            print(f"  [FAIL] bear regime NEVER fired - Stage C v1 silent-bull regression returned")

    # =========================================================================
    # SECTION 2 - STRATEGIES FIRING
    # =========================================================================
    section("2. STRATEGIES FIRING")
    strat_counts = df["strategy"].value_counts()
    print(f"  Distinct strategies that fired: {len(strat_counts)}")
    print(f"  Total trades: {n}")
    print()
    print(f"  Top 10 by trade count:")
    for strat, count in strat_counts.head(10).items():
        pnl_mean = df[df["strategy"] == strat]["pnl_pct"].mean()
        print(f"    {strat!s:45s} {count:4d} trades   avg_pnl={pnl_mean:+.2f}%")
    print()
    print(f"  Bottom 5 by trade count:")
    for strat, count in strat_counts.tail(5).items():
        pnl_mean = df[df["strategy"] == strat]["pnl_pct"].mean()
        print(f"    {strat!s:45s} {count:4d} trades   avg_pnl={pnl_mean:+.2f}%")

    subsection("Direction split")
    dir_counts = df["direction"].value_counts()
    for d, c in dir_counts.items():
        print(f"    {d!s:10s} {c:5d}  ({100*c/n:5.1f}%)")

    subsection("Category distribution")
    if "category" in df.columns:
        cat_counts = df["category"].value_counts()
        for cat, c in cat_counts.head(10).items():
            cat_pnl = df[df["category"] == cat]["pnl_pct"].sum()
            print(f"    {cat!s:30s} {c:4d} trades   sum_pp={cat_pnl:+.1f}")

    # =========================================================================
    # SECTION 3 - EXITS DISPATCHING
    # =========================================================================
    section("3. EXITS DISPATCHING")
    exit_counts = df["exit_reason"].value_counts()
    print(f"  Distinct exit reasons: {len(exit_counts)}")
    print()
    for reason, count in exit_counts.items():
        sub = df[df["exit_reason"] == reason]
        wr = (sub["win"].astype(bool).sum() / len(sub)) * 100 if "win" in df.columns else float("nan")
        mean_pnl = sub["pnl_pct"].mean()
        mean_hold = sub["hold_days"].mean()
        print(f"    {reason!s:35s} n={count:4d}  WR={wr:5.1f}%  mean_pnl={mean_pnl:+.2f}%  mean_hold={mean_hold:5.1f}d")

    subsection("STRATEGY_EXIT_OVERRIDE compliance check")
    try:
        from backtest.config import STRATEGY_EXIT_OVERRIDE
        from backtest.engine.exit_strategies import EXIT_STRATEGIES
        valid_methods = set(EXIT_STRATEGIES.keys())
        # For each strategy with override, verify the actual exits used match
        mismatches = []
        for strat, cfg in STRATEGY_EXIT_OVERRIDE.items():
            if strat not in strat_counts.index:
                continue
            method = cfg.get("exit_method") if isinstance(cfg, dict) else cfg
            sub = df[df["strategy"] == strat]
            actual_exits = set(sub["exit_reason"].unique())
            # exit_reason isn't necessarily the same string as the method; just
            # report the distribution for owner inspection
            print(f"    {strat!s:35s} configured={method!s:30s} actual={list(actual_exits)[:3]}")
    except ImportError as e:
        print(f"    [SKIP] STRATEGY_EXIT_OVERRIDE import failed: {e}")

    # =========================================================================
    # SECTION 4 - DATA CORRUPTION
    # =========================================================================
    section("4. DATA CORRUPTION CHECKS")

    subsection("Impossible PnL (>500% gain or <-100% loss)")
    impossible_pnl = df[(df["pnl_pct"] > 500) | (df["pnl_pct"] < -100)]
    if not impossible_pnl.empty:
        findings["FAIL"].append(f"{len(impossible_pnl)} trades with impossible PnL")
        print(f"  [FAIL] {len(impossible_pnl)} trades have impossible PnL")
        print(impossible_pnl[["ticker","entry_date","strategy","direction","pnl_pct","hold_days"]].to_string(index=False))
    else:
        findings["OK"].append("No impossible PnL trades")
        print(f"  [OK] No impossible PnL (META-pattern detector clean)")

    subsection("Negative hold_days or zero")
    bad_hold = df[df["hold_days"] < 0]
    if not bad_hold.empty:
        findings["FAIL"].append(f"{len(bad_hold)} trades with negative hold_days")
        print(f"  [FAIL] {len(bad_hold)} trades with negative hold_days")
        print(bad_hold[["ticker","entry_date","exit_date","hold_days"]].head(5).to_string(index=False))
    else:
        findings["OK"].append("No negative hold_days")
        print(f"  [OK] No negative hold_days")

    zero_hold = df[df["hold_days"] == 0]
    if not zero_hold.empty:
        findings["WARN"].append(f"{len(zero_hold)} trades with hold_days=0 (same-day exit)")
        print(f"  [WARN] {len(zero_hold)} trades with hold_days=0 (same-day) - intraday signals or stop-out at entry")

    subsection("Exit date before entry date")
    df["entry_dt"] = pd.to_datetime(df["entry_date"], errors="coerce")
    df["exit_dt"] = pd.to_datetime(df["exit_date"], errors="coerce")
    bad_dates = df[df["exit_dt"] < df["entry_dt"]]
    if not bad_dates.empty:
        findings["FAIL"].append(f"{len(bad_dates)} trades with exit before entry")
        print(f"  [FAIL] {len(bad_dates)} trades with exit before entry")
    else:
        findings["OK"].append("All exits are after entries")
        print(f"  [OK] All exits after entries")

    subsection("NaN in critical fields")
    critical = ["ticker", "entry_date", "exit_date", "strategy", "direction",
                "regime", "exit_reason", "pnl_pct", "hold_days"]
    nan_summary = []
    for col in critical:
        if col not in df.columns:
            continue
        n_nan = df[col].isna().sum()
        if n_nan > 0:
            nan_summary.append((col, n_nan))
    if nan_summary:
        findings["FAIL"].append(f"NaN in critical fields: {nan_summary}")
        for col, n_nan in nan_summary:
            print(f"  [FAIL] {col}: {n_nan} NaN rows")
    else:
        findings["OK"].append("No NaN in critical fields")
        print(f"  [OK] No NaN in critical fields")

    subsection("Entry price vs initial stop sanity")
    if "initial_stop" in df.columns and "entry_price" in df.columns:
        # Long: stop should be < entry_price ; Short: stop > entry_price
        long_bad_stop = df[(df["direction"] == "long") &
                           (df["initial_stop"] >= df["entry_price"])]
        short_bad_stop = df[(df["direction"] == "short") &
                            (df["initial_stop"] <= df["entry_price"])]
        if not long_bad_stop.empty:
            findings["FAIL"].append(f"{len(long_bad_stop)} long trades with stop >= entry_price")
            print(f"  [FAIL] {len(long_bad_stop)} LONG trades with initial_stop >= entry_price")
        if not short_bad_stop.empty:
            findings["FAIL"].append(f"{len(short_bad_stop)} short trades with stop <= entry_price")
            print(f"  [FAIL] {len(short_bad_stop)} SHORT trades with initial_stop <= entry_price")
        if long_bad_stop.empty and short_bad_stop.empty:
            findings["OK"].append("All stops on correct side of entry price")
            print(f"  [OK] All stops on correct side of entry price")

    # =========================================================================
    # SECTION 5 - OUTCOMES LOGICAL
    # =========================================================================
    section("5. OUTCOMES LOGICAL")
    n_win = int(df["win"].astype(bool).sum()) if "win" in df.columns else 0
    wr = 100.0 * n_win / n
    mean_pnl = df["pnl_pct"].mean()
    sum_pp = df["pnl_pct"].sum()
    median_hold = df["hold_days"].median()
    p95_pnl = df["pnl_pct"].quantile(0.95)
    p05_pnl = df["pnl_pct"].quantile(0.05)
    print(f"  n_trades:    {n}")
    print(f"  wins:        {n_win}")
    print(f"  win rate:    {wr:5.1f}%")
    print(f"  mean PnL:    {mean_pnl:+.2f}%")
    print(f"  sum PnL pp:  {sum_pp:+.1f}")
    print(f"  median hold: {median_hold:.1f} days")
    print(f"  5th pct PnL: {p05_pnl:+.2f}%")
    print(f"  95th pct:    {p95_pnl:+.2f}%")
    print(f"  worst:       {df['pnl_pct'].min():+.2f}%")
    print(f"  best:        {df['pnl_pct'].max():+.2f}%")

    subsection("Per-regime breakdown")
    if "regime" in df.columns:
        for regime in df["regime"].dropna().unique():
            sub = df[df["regime"] == regime]
            r_n = len(sub)
            r_wr = 100.0 * sub["win"].astype(bool).sum() / r_n
            r_mean = sub["pnl_pct"].mean()
            r_sum = sub["pnl_pct"].sum()
            print(f"    {regime!s:25s} n={r_n:4d}  WR={r_wr:5.1f}%  mean={r_mean:+.2f}%  sum_pp={r_sum:+.1f}")

    subsection("Per-direction breakdown")
    for direction in df["direction"].dropna().unique():
        sub = df[df["direction"] == direction]
        d_n = len(sub)
        d_wr = 100.0 * sub["win"].astype(bool).sum() / d_n
        d_mean = sub["pnl_pct"].mean()
        d_sum = sub["pnl_pct"].sum()
        print(f"    {direction!s:10s} n={d_n:4d}  WR={d_wr:5.1f}%  mean={d_mean:+.2f}%  sum_pp={d_sum:+.1f}")

    subsection("Hold duration vs exit method sanity")
    if "exit_reason" in df.columns:
        for reason in df["exit_reason"].value_counts().head(8).index:
            sub = df[df["exit_reason"] == reason]
            hold_max = sub["hold_days"].max()
            hold_p95 = sub["hold_days"].quantile(0.95)
            hold_median = sub["hold_days"].median()
            note = ""
            # Sanity: class_time_stop should hold <60d; r_multiple_2r/3r could be longer
            if reason == "class_time_stop" and hold_max > 90:
                note = "  [WARN] class_time_stop hold > 90d - cap may not be enforced"
                findings["WARN"].append(f"class_time_stop hold > 90d ({hold_max})")
            if reason == "trailing_stop" and hold_median > 365:
                note = "  [WARN] trailing_stop median > 1y - may be tracking dead trade"
            print(f"    {reason!s:35s} median={hold_median:5.1f}d  p95={hold_p95:5.1f}d  max={hold_max:5.0f}d{note}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    section("AUDIT SUMMARY")
    print(f"  OK:   {len(findings['OK'])}")
    print(f"  WARN: {len(findings['WARN'])}")
    print(f"  FAIL: {len(findings['FAIL'])}")
    print()
    if findings["FAIL"]:
        print("  FAILURES:")
        for f in findings["FAIL"]:
            print(f"    - {f}")
    if findings["WARN"]:
        print("  WARNINGS:")
        for w in findings["WARN"]:
            print(f"    - {w}")

    return findings


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="trade_log.csv path")
    args = p.parse_args()
    audit(Path(args.input))


if __name__ == "__main__":
    main()
