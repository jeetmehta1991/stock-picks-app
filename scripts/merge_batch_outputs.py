"""
scripts/merge_batch_outputs.py
Merge 5 parallel batch output directories into one final Phase 1B result.

IMPORTANT: Strategy-level metrics are RE-COMPUTED on the combined trade log.
           Never average metrics across batches — statistically incorrect.

Usage:
    python scripts/merge_batch_outputs.py --input-dirs output_1b_batch1 output_1b_batch2 \
        output_1b_batch3 output_1b_batch4 output_1b_batch5 --output-dir output_1b_final

Validation checks run automatically after merge.
"""
import sys
import json
import argparse
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def merge_csv(dirs: list, filename: str) -> pd.DataFrame:
    """Concatenate a CSV file across all batch directories."""
    dfs = []
    for d in dirs:
        f = Path(d) / filename
        if f.exists():
            try:
                df = pd.read_csv(f)
                df["_batch_source"] = d
                dfs.append(df)
            except Exception as e:
                print(f"  [WARN]  Could not read {f}: {e}")
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


def validate_merge(trade_log: pd.DataFrame, input_dirs: list) -> list[str]:
    """Run validation checks on merged output."""
    issues = []

    # Check total trade count
    expected_min = len(input_dirs) * 1   # at least 1 trade per batch (test runs may have few)
    if len(trade_log) < expected_min:
        issues.append(f"Low trade count: {len(trade_log)} (expected >= {expected_min})")

    # Check no duplicate trades (same ticker + entry_date + strategy)
    if len(trade_log) > 0 and all(c in trade_log.columns for c in ["ticker","entry_date","strategy"]):
        dupes = trade_log.duplicated(subset=["ticker","entry_date","strategy"]).sum()
        if dupes > 0:
            issues.append(f"Duplicate trades: {dupes} - ticker+date+strategy not unique")

    # Check all batches contributed
    if "_batch_source" in trade_log.columns:
        sources = trade_log["_batch_source"].nunique()
        if sources < len(input_dirs):
            issues.append(f"Only {sources}/{len(input_dirs)} batches contributed trades")

    # Check required columns present
    required = ["ticker","entry_date","exit_date","pnl_pct","win",
                "confidence_tier","preliminary_tier","strategy","sector"]
    missing = [c for c in required if c not in trade_log.columns]
    if missing:
        issues.append(f"Missing columns: {missing}")

    # Check no NaN in critical columns
    for col in ["pnl_pct","win","hold_days"]:
        if col in trade_log.columns and trade_log[col].isna().any():
            issues.append(f"NaN values in {col}")

    return issues


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-dirs", nargs="+", required=True)
    p.add_argument("--output-dir", required=True)
    args = p.parse_args()

    input_dirs = args.input_dirs
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"MERGING {len(input_dirs)} BATCH OUTPUTS -> {output_dir}")
    print(f"{'='*60}\n")

    # -- 0. Verify all batches completed --
    print("Verifying all batch directories exist and have trade logs...")
    missing_dirs = []
    empty_dirs   = []
    for d in input_dirs:
        trade_log_path = Path(d) / "trade_log.csv"
        if not Path(d).exists():
            missing_dirs.append(d)
        elif not trade_log_path.exists():
            # Check for checkpoint as fallback
            checkpoint = Path(d) / "trade_log_checkpoint.csv"
            if checkpoint.exists():
                print(f"  [WARN]  {d}: no trade_log.csv but checkpoint exists - batch may have crashed")
                empty_dirs.append(d)
            else:
                empty_dirs.append(d)
        else:
            import pandas as _pd2
            df_check = _pd2.read_csv(trade_log_path)
            print(f"  [OK] {d}: {len(df_check)} trades")

    if missing_dirs:
        print(f"[FAIL] ABORT: {len(missing_dirs)} batch directories not found: {missing_dirs}")
        print("   Ensure all batches completed before merging.")
        sys.exit(1)
    if empty_dirs:
        print(f"[WARN]  WARNING: {len(empty_dirs)} batches have no trade_log.csv: {empty_dirs}")
        response = input("Continue merge with partial batches? (yes/no): ").strip().lower()
        if response != "yes":
            print("Merge aborted.")
            sys.exit(1)

    # -- 1. Merge trade log --
    print("Merging trade_log.csv...")
    trade_log = merge_csv(input_dirs, "trade_log.csv")
    if trade_log.empty:
        print("[FAIL] No trade logs found - check input directories")
        sys.exit(1)
    # Remove batch source column before saving
    trade_log_clean = trade_log.drop(columns=["_batch_source"], errors="ignore")
    trade_log_clean.to_csv(output_dir / "trade_log.csv", index=False)
    print(f"  [OK] {len(trade_log_clean)} total trades from {len(input_dirs)} batches")

    # -- 2. Re-compute strategy metrics on combined trade log --
    # Batch 201 (Issue-1 fix): prior imports referenced run_walk_forward and
    # run_bonferroni from backtest.results.metrics where they DO NOT exist
    # (run_walk_forward lives in backtest.engine.improvements;
    # run_bonferroni was never defined - the bonferroni helper is
    # bonferroni_adjusted_threshold in improvements). The bad top-level
    # import made the whole try-block fail before compute_all_metrics ever
    # ran, forcing every merge to fall back to concat of batch results
    # (statistically wrong - 5 strategies appearing in 5 batches would each
    # surface 5 times with batch-local averages, not 1 row with combined
    # metrics). Phase 1A-beta merge surfaced this. Fix: only import what
    # actually exists at module top; walk-forward retains its inner import
    # from improvements.
    print("\nRe-computing strategy metrics on combined trade log...")
    try:
        from backtest.results.metrics import compute_all_metrics
        # compute_all_metrics returns a single DataFrame
        metrics_df = compute_all_metrics(trade_log_clean)
        metrics_df.to_csv(output_dir / "backtest_results.csv", index=False)
        print(f"  [OK] {len(metrics_df)} strategies evaluated")

        # Walk-forward on combined log (needs full universe to reach 100+ IS trades)
        try:
            from backtest.engine.improvements import run_walk_forward, walk_forward_to_df
            wf = run_walk_forward(trade_log_clean)
            wf_df = walk_forward_to_df(wf)
            wf_df.to_csv(output_dir / "walk_forward_validation.csv", index=False)
            summary = wf.get("summary", {})
            print(f"  [OK] Walk-forward: {summary.get('robust',0)} ROBUST / "
                  f"{summary.get('total',0)} strategies")
        except Exception as wf_e:
            print(f"  [WARN]  Walk-forward failed: {wf_e}")

    except Exception as e:
        print(f"  [WARN]  Metrics re-computation failed: {e}")
        print("  Falling back to concat of batch results...")
        raw_metrics = merge_csv(input_dirs, "backtest_results.csv")
        raw_metrics.drop(columns=["_batch_source"], errors="ignore").to_csv(
            output_dir / "backtest_results.csv", index=False)

    # -- 3. Merge other output files (concat only) --
    for filename in ["skipped_trades.csv", "sector_concentration.csv",
                     "agent_performance.csv", "tier_adjustment_analysis.csv",
                     "circuit_breaker_log.csv"]:
        df = merge_csv(input_dirs, filename)
        if not df.empty:
            df.drop(columns=["_batch_source"], errors="ignore").to_csv(
                output_dir / filename, index=False)
            print(f"  [OK] {filename}: {len(df)} rows")

    # -- 4. Re-compute portfolio summary --
    # Batch 201 (Issue-2 fix): the 5 batches ran as 5 INDEPENDENT portfolios
    # each at 100% capital allocation. Concat of trade logs preserves the
    # batch-local position_size_pct values, so max_portfolio_heat_pct
    # computed on the concat'd log measures "sum of all 5 batches' open
    # heats", which is the wrong semantic for the merged-portfolio
    # interpretation. Phase 1A-beta merge reported 417% heat - clearly an
    # artifact (a real single portfolio cannot exceed 100% heat without
    # leverage). Correction: emit BOTH semantics in the JSON:
    #   - max_portfolio_heat_pct           = unified-portfolio (scaled by 1/N)
    #   - max_portfolio_heat_pct_concat    = original concat'd value
    # This preserves auditability AND gives downstream consumers
    # (dashboards, reports) a sensible default. Same applies to
    # avg_position_size_pct.
    try:
        from backtest.results.metrics import compute_portfolio_summary
        n_batches = max(len(input_dirs), 1)
        port = compute_portfolio_summary(trade_log_clean)
        # Preserve concat-semantics value, then rescale for unified portfolio
        concat_heat = port.get("max_portfolio_heat_pct", 0)
        concat_avg_size = port.get("avg_position_size_pct", 0)
        port["max_portfolio_heat_pct_concat"] = concat_heat
        port["avg_position_size_pct_concat"]  = concat_avg_size
        port["max_portfolio_heat_pct"]        = round(concat_heat / n_batches, 1)
        port["avg_position_size_pct"]         = round(concat_avg_size / n_batches, 2)
        port["n_batches_merged"]              = n_batches
        port["heat_semantics_note"]           = (
            f"max_portfolio_heat_pct rescaled by 1/{n_batches} from concat "
            "value to approximate unified-portfolio heat (each batch ran at "
            "100% capital allocation; merged represents 1 portfolio holding "
            "the union of trades sized against combined capital). Use "
            "max_portfolio_heat_pct_concat for raw concat aggregate."
        )
        (output_dir / "portfolio_summary.json").write_text(json.dumps(port, indent=2))
        print(f"\n  [OK] Portfolio return: {port.get('portfolio_return_pct',0):.1f}%")
        print(f"  [OK] Max heat (unified): {port['max_portfolio_heat_pct']:.1f}%  "
              f"(concat: {concat_heat:.1f}% / {n_batches} batches)")
    except Exception as e:
        print(f"  [WARN]  Portfolio summary failed: {e}")

    # -- 5. Validation --
    print(f"\n{'='*60}")
    print("VALIDATION")
    print(f"{'='*60}")
    issues = validate_merge(trade_log, input_dirs)
    if issues:
        print(f"[FAIL] {len(issues)} issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("[OK] All validation checks passed")

    # -- 6. Summary --
    print(f"\n{'='*60}")
    print("MERGE SUMMARY")
    print(f"{'='*60}")
    print(f"Total trades:     {len(trade_log_clean)}")
    if "strategy" in trade_log_clean.columns:
        print(f"Unique strategies: {trade_log_clean['strategy'].nunique()}")
    if "ticker" in trade_log_clean.columns:
        print(f"Unique tickers:    {trade_log_clean['ticker'].nunique()}")
    if "win" in trade_log_clean.columns:
        wr = trade_log_clean["win"].mean()
        print(f"Overall win rate:  {wr:.1%}")
    print(f"\nOutput: {output_dir}/")
    print("\n[WARN]  NEXT STEP: git add + commit all batch outputs and merged result")
    print("   NEVER run git reset --hard without checking git status first")


if __name__ == "__main__":
    main()
