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
                print(f"  ⚠️  Could not read {f}: {e}")
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


def validate_merge(trade_log: pd.DataFrame, input_dirs: list) -> list[str]:
    """Run validation checks on merged output."""
    issues = []

    # Check total trade count
    expected_min = len(input_dirs) * 10  # at least 10 trades per batch
    if len(trade_log) < expected_min:
        issues.append(f"Low trade count: {len(trade_log)} (expected ≥ {expected_min})")

    # Check no duplicate trades (same ticker + entry_date + strategy)
    if len(trade_log) > 0 and all(c in trade_log.columns for c in ["ticker","entry_date","strategy"]):
        dupes = trade_log.duplicated(subset=["ticker","entry_date","strategy"]).sum()
        if dupes > 0:
            issues.append(f"Duplicate trades: {dupes} — ticker+date+strategy not unique")

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
    print(f"MERGING {len(input_dirs)} BATCH OUTPUTS → {output_dir}")
    print(f"{'='*60}\n")

    # ── 1. Merge trade log ──
    print("Merging trade_log.csv...")
    trade_log = merge_csv(input_dirs, "trade_log.csv")
    if trade_log.empty:
        print("❌ No trade logs found — check input directories")
        sys.exit(1)
    # Remove batch source column before saving
    trade_log_clean = trade_log.drop(columns=["_batch_source"], errors="ignore")
    trade_log_clean.to_csv(output_dir / "trade_log.csv", index=False)
    print(f"  ✅ {len(trade_log_clean)} total trades from {len(input_dirs)} batches")

    # ── 2. Re-compute strategy metrics on combined trade log ──
    print("\nRe-computing strategy metrics on combined trade log...")
    try:
        from backtest.results.metrics import compute_all_metrics
        metrics_df, wf_df, bonf_df = compute_all_metrics(trade_log_clean)
        metrics_df.to_csv(output_dir / "backtest_results.csv", index=False)
        if wf_df is not None and not wf_df.empty:
            wf_df.to_csv(output_dir / "walk_forward_validation.csv", index=False)
        if bonf_df is not None and not bonf_df.empty:
            bonf_df.to_csv(output_dir / "bonferroni_correction.csv", index=False)
        print(f"  ✅ {len(metrics_df)} strategies evaluated")
    except Exception as e:
        print(f"  ⚠️  Metrics re-computation failed: {e}")
        print("  Falling back to concat of batch results...")
        raw_metrics = merge_csv(input_dirs, "backtest_results.csv")
        raw_metrics.drop(columns=["_batch_source"], errors="ignore").to_csv(
            output_dir / "backtest_results.csv", index=False)

    # ── 3. Merge other output files (concat only) ──
    for filename in ["skipped_trades.csv", "sector_concentration.csv",
                     "agent_performance.csv", "tier_adjustment_analysis.csv",
                     "circuit_breaker_log.csv"]:
        df = merge_csv(input_dirs, filename)
        if not df.empty:
            df.drop(columns=["_batch_source"], errors="ignore").to_csv(
                output_dir / filename, index=False)
            print(f"  ✅ {filename}: {len(df)} rows")

    # ── 4. Re-compute portfolio summary ──
    try:
        from backtest.results.metrics import compute_portfolio_summary
        port = compute_portfolio_summary(trade_log_clean)
        (output_dir / "portfolio_summary.json").write_text(json.dumps(port, indent=2))
        print(f"\n  ✅ Portfolio return: {port.get('portfolio_return_pct',0):.1f}%")
        print(f"  ✅ Max portfolio heat: {port.get('max_portfolio_heat_pct',0):.1f}%")
    except Exception as e:
        print(f"  ⚠️  Portfolio summary failed: {e}")

    # ── 5. Validation ──
    print(f"\n{'='*60}")
    print("VALIDATION")
    print(f"{'='*60}")
    issues = validate_merge(trade_log, input_dirs)
    if issues:
        print(f"❌ {len(issues)} issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ All validation checks passed")

    # ── 6. Summary ──
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
    print("\n⚠️  NEXT STEP: git add + commit all batch outputs and merged result")
    print("   NEVER run git reset --hard without checking git status first")


if __name__ == "__main__":
    main()
