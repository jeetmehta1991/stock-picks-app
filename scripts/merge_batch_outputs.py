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
    p.add_argument("--allow-env-mismatch", action="store_true",
                   help="B1307 CHECKLIST #158: proceed despite env-parity "
                        "mismatch (owner override; logged)")
    p.add_argument("--yes", action="store_true",
                   help="Non-interactive: auto-accept partial-batch warnings. "
                        "Required for unattended Hetzner runs. (Stream A4)")
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
        if args.yes:
            print("--yes: auto-accepting partial-batch merge")
        else:
            response = input("Continue merge with partial batches? (yes/no): ").strip().lower()
            if response != "yes":
                print("Merge aborted.")
                sys.exit(1)

    # -- 0. B1307 (CHECKLIST #158): environment-fingerprint parity gate.
    # HALT the merge if any two chunks ran on incompatible grids/calendars
    # (the B1305 chunk-1 Mon-Fri-vs-NYSE defect). Fingerprints that are
    # absent (legacy chunks) warn but don't block; present-and-mismatched
    # blocks unless --allow-env-mismatch is set (owner override, logged).
    fps = []
    for d in input_dirs:
        fp_path = Path(d) / "env_fingerprint.json"
        if fp_path.exists():
            try:
                fps.append((d, json.loads(fp_path.read_text(encoding="utf-8"))))
            except Exception:
                pass
    if len(fps) >= 2:
        # B1332 (Council 362): use the SINGLE-SOURCE MERGE_CRITICAL (grid + cal
        # + smc_active + code_sha) instead of a hardcoded grid+cal tuple. The
        # adversarial review found the merge was NOT enforcing code_sha/smc_active
        # (B1329 added them to MERGE_CRITICAL but the merge had its own list) ->
        # batches at different code / SMC-state would have merged silently.
        try:
            from scripts.env_fingerprint import MERGE_CRITICAL as crit
        except Exception:
            crit = ("grid_total", "grid_hash", "calendar_backend",
                    "smc_active", "code_sha")
        base_d, base = fps[0]
        mm = [f"{d}:{k}={fp.get(k)} != {base_d}:{k}={base.get(k)}"
              for d, fp in fps[1:] for k in crit if fp.get(k) != base.get(k)]
        if mm:
            print("[FAIL] ENV-PARITY (CHECKLIST #158): chunks ran on "
                  "incompatible environments -- NOT mergeable:")
            for m in mm:
                print(f"   {m}")
            if not getattr(args, "allow_env_mismatch", False):
                print("   Re-run mismatched chunks on the correct grid, or "
                      "pass --allow-env-mismatch (owner override, logged).")
                sys.exit(1)
            print("   --allow-env-mismatch: proceeding despite mismatch (owner override)")
        else:
            print(f"[OK] env-parity: {len(fps)} chunks agree on {tuple(crit)}")
    elif fps:
        print(f"[WARN] env-parity: only {len(fps)}/{len(input_dirs)} chunks "
              "have fingerprints; cannot fully verify (CHECKLIST #158)")
    else:
        print("[WARN] env-parity: no env_fingerprint.json in any chunk "
              "(pre-#158 run); verify grids manually before trusting merge")

    # -- 1. Merge trade log --
    print("Merging trade_log.csv...")
    trade_log = merge_csv(input_dirs, "trade_log.csv")
    if trade_log.empty:
        print("[FAIL] No trade logs found - check input directories")
        sys.exit(1)
    # Remove batch source column before saving
    trade_log_clean = trade_log.drop(columns=["_batch_source"], errors="ignore")
    # B1299 (Council 333, S6-B1297-MERGE-FIXES fix-c): CROSS-BATCH DEDUP.
    # The engine auto-adds the benchmark (SPY) to every run's tradeable
    # universe, so every chunk trades SPY -> N-times duplication in the
    # merge (Gate 6 dry-run catch). Dedup on the trade identity key.
    _pre = len(trade_log_clean)
    if all(c in trade_log_clean.columns for c in ("ticker", "strategy", "entry_date")):
        trade_log_clean = trade_log_clean.drop_duplicates(
            subset=["ticker", "strategy", "entry_date"], keep="first")
    if _pre - len(trade_log_clean):
        print(f"  [OK] fix-c dedup: dropped {_pre - len(trade_log_clean)} "
              f"cross-batch duplicate trades (benchmark auto-inclusion class)")
    trade_log_clean.to_csv(output_dir / "trade_log.csv", index=False)
    print(f"  [OK] {len(trade_log_clean)} total trades from {len(input_dirs)} batches")
    # B1299 fix-a: merged CANONICAL parquet (DEC-491) via the FIX-3
    # serialization contract (nested cols as JSON strings; loads_signals
    # reads them back). Failure leaves the ENG-3-style marker.
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from backtest.util.signals_serde import dumps_signals, loads_signals
        _pq = trade_log_clean.copy()
        for _c in ("signals_at_entry", "context_bullets", "agent_reasoning"):
            if _c in _pq.columns:
                _pq[_c] = _pq[_c].apply(
                    lambda v: dumps_signals(loads_signals(v, v))
                    if isinstance(v, (str, dict, list)) else v)
        _pq.to_parquet(output_dir / "trade_log.parquet", index=False)
        print(f"  [OK] fix-a trade_log.parquet written ({len(_pq)} rows)")
    except Exception as _e_pq:
        print(f"  [FAIL] fix-a trade_log.parquet write failed: {_e_pq}")
        (output_dir / "trade_log.parquet.FAILED").write_text(str(_e_pq))

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

    # -- 3b. Batch 345 (D9 fix) 2026-05-25: exit cube post-merge.
    # Per-batch outputs include exit_by_<dim>.csv slices + exit_method_multi_dim_cube
    # + exit_sweet_spots + exit_pairwise_dominance, all DERIVED from
    # trade_exit_detail.csv. Concat of derived slices would produce N-times
    # duplicate (exit_method, dim_value) buckets - wrong semantics. Right fix:
    # concat the SOURCE trade_exit_detail across batches, then re-run the
    # aggregation logic from writer.py against the combined source.
    print("\nMerging exit cube outputs (D9 fix)...")
    try:
        ted = merge_csv(input_dirs, "trade_exit_detail.csv")
        if not ted.empty:
            ted_clean = ted.drop(columns=["_batch_source"], errors="ignore")
            # B1299 fix-c: same cross-batch dedup at detail grain.
            if all(c in ted_clean.columns for c in
                   ("ticker", "strategy", "entry_date", "exit_method")):
                _tp = len(ted_clean)
                ted_clean = ted_clean.drop_duplicates(
                    subset=["ticker", "strategy", "entry_date", "exit_method"],
                    keep="first")
                if _tp - len(ted_clean):
                    print(f"  [OK] fix-c detail dedup: dropped {_tp - len(ted_clean)} rows")
            ted_clean.to_csv(output_dir / "trade_exit_detail.csv", index=False)
            print(f"  [OK] trade_exit_detail.csv: {len(ted_clean)} rows merged")

            # B1299 fix-b: rebuild the ENGINE-SCHEMA per-(strategy x exit)
            # cube. Gate 6 caught a NAME COLLISION: this script previously
            # wrote a per-exit-method summary (26 rows) under
            # exit_strategy_comparison.csv, the filename the engine uses
            # for the per-cell cube (858 rows at 5 tickers) -- PIVOT #37
            # writer-reader class. The per-exit summary now writes to
            # exit_method_summary.csv; this block rebuilds the true cube.
            try:
                from backtest.engine.exit_strategies import (
                    composite_score, NON_FIRE_EXIT_REASONS,
                    CUBE_MAX_AVG_HOLD_DAYS, CUBE_MIN_FIRE_RATE)
                rows = []
                for (strat, exm), g in ted_clean.groupby(["strategy", "exit_method"]):
                    pnl = g["pnl_pct"].astype(float)
                    wins = pnl[pnl > 0].sum()
                    losses = abs(pnl[pnl <= 0].sum())
                    pf = round(wins / losses, 4) if losses > 0 else (999.0 if wins > 0 else 0.0)
                    g2 = g.sort_values("entry_date")
                    cum = g2["pnl_pct"].astype(float).cumsum()
                    mdd = round(float((cum - cum.cummax()).min()), 4) if len(cum) else 0.0
                    fired = (~g["exit_reason"].isin(NON_FIRE_EXIT_REASONS)).mean() if "exit_reason" in g.columns else 1.0
                    wr = round(float(g["win"].mean()), 4)
                    avg_pnl = round(float(pnl.mean()), 4)
                    avg_hold = round(float(g["hold_days"].mean()), 1) if "hold_days" in g.columns else 0.0
                    rows.append({
                        "strategy": strat, "exit_method": exm, "trades": len(g),
                        "win_rate": wr, "profit_factor": pf, "avg_pnl_pct": avg_pnl,
                        "total_roi_pct": round(float(pnl.sum()), 4),
                        "max_drawdown_pct": mdd, "avg_hold_days": avg_hold,
                        "actual_fire_rate": round(float(fired), 4),
                        "composite_score": composite_score(wr, pf, mdd, avg_pnl_pct=avg_pnl),
                        "recommended": False,
                    })
                cube_df = pd.DataFrame(rows)
                if not cube_df.empty:
                    # recommended = per-strategy max composite passing guardrails
                    ok = cube_df[(cube_df.avg_hold_days <= CUBE_MAX_AVG_HOLD_DAYS)
                                 & (cube_df.actual_fire_rate >= CUBE_MIN_FIRE_RATE)]
                    best_idx = ok.sort_values("composite_score", ascending=False
                                              ).groupby("strategy").head(1).index
                    cube_df.loc[best_idx, "recommended"] = True
                    cube_df.to_csv(output_dir / "exit_strategy_comparison.csv", index=False)
                    print(f"  [OK] fix-b exit_strategy_comparison.csv rebuilt in "
                          f"ENGINE schema: {len(cube_df)} strategy x exit cells")
            except Exception as e_cell:
                print(f"  [FAIL] fix-b engine-schema cube rebuild failed: {e_cell}")

            # 1D marginal aggregates per CONTEXT_COLUMN_NAMES dim
            try:
                from backtest.engine.exit_context import CONTEXT_COLUMN_NAMES
                n_dims_written = 0
                for dim in CONTEXT_COLUMN_NAMES:
                    if dim not in ted_clean.columns:
                        continue
                    try:
                        agg = (ted_clean.groupby(
                                    ["strategy", "exit_method", dim], dropna=False
                                ).agg(
                                    n=("pnl_pct", "size"),
                                    win_rate=("win", "mean"),
                                    avg_pnl_pct=("pnl_pct", "mean"),
                                    total_pnl_pct=("pnl_pct", "sum"),
                                ).reset_index())
                        agg.to_csv(output_dir / f"exit_by_{dim}.csv", index=False)
                        n_dims_written += 1
                    except Exception as e_dim:
                        print(f"  [WARN] exit_by_{dim} failed: {e_dim}")
                print(f"  [OK] exit_by_<dim>.csv: {n_dims_written} dim slices re-aggregated")
            except Exception as e_ctx:
                print(f"  [WARN] CONTEXT_COLUMN_NAMES import failed: {e_ctx}")

            # Multi-dim cube + sweet spots + pairwise dominance
            try:
                from backtest.results.exit_conditional_analyzer import (
                    compute_multi_dim_cube,
                    find_sweet_spots,
                    compute_pairwise_dominance,
                    DEFAULT_CONDITION_DIMS,
                )
                available_dims = [d for d in DEFAULT_CONDITION_DIMS
                                  if d in ted_clean.columns]
                cube = compute_multi_dim_cube(ted_clean, dims=available_dims)
                if not cube.empty:
                    cube.to_csv(output_dir / "exit_method_multi_dim_cube.csv", index=False)
                    print(f"  [OK] exit_method_multi_dim_cube.csv: {len(cube)} cells x {len(available_dims)} dims")
                    spots = find_sweet_spots(cube, dims=available_dims)
                    if not spots.empty:
                        spots.to_csv(output_dir / "exit_sweet_spots.csv", index=False)
                        print(f"  [OK] exit_sweet_spots.csv: {len(spots)} rows")
                    dom = compute_pairwise_dominance(cube, dims=available_dims)
                    if not dom.empty:
                        dom.to_csv(output_dir / "exit_pairwise_dominance.csv", index=False)
                        print(f"  [OK] exit_pairwise_dominance.csv: {len(dom)} rows")
            except Exception as e_cube:
                print(f"  [WARN] exit cube re-aggregation failed: {e_cube}")

            # exit_strategy_comparison (top-level per-exit-method summary)
            try:
                if {"exit_method", "pnl_pct", "win"}.issubset(ted_clean.columns):
                    comp = (ted_clean.groupby("exit_method").agg(
                        n=("pnl_pct", "size"),
                        win_rate=("win", "mean"),
                        avg_pnl_pct=("pnl_pct", "mean"),
                        total_pnl_pct=("pnl_pct", "sum"),
                        median_pnl_pct=("pnl_pct", "median"),
                    ).reset_index().sort_values("total_pnl_pct", ascending=False))
                    # B1299 fix-b: renamed from exit_strategy_comparison.csv
                    # (name collision with the engine's per-cell cube).
                    comp.to_csv(output_dir / "exit_method_summary.csv", index=False)
                    print(f"  [OK] exit_method_summary.csv: {len(comp)} exit methods")
                    # exit_strategy_best (per-strategy top exit by total_pnl)
                    best = (ted_clean.groupby(["strategy", "exit_method"]).agg(
                        total_pnl_pct=("pnl_pct", "sum"),
                        n=("pnl_pct", "size"),
                        win_rate=("win", "mean"),
                    ).reset_index())
                    best_per_strat = best.sort_values("total_pnl_pct", ascending=False).groupby("strategy").head(1)
                    best_per_strat.to_csv(output_dir / "exit_strategy_best.csv", index=False)
                    print(f"  [OK] exit_strategy_best.csv: {len(best_per_strat)} strategy x best-exit rows")
            except Exception as e_comp:
                print(f"  [WARN] exit_strategy_comparison failed: {e_comp}")
        else:
            print("  [SKIP] trade_exit_detail.csv missing in all batches; exit cube not merged")
    except Exception as e_ted:
        print(f"  [WARN] exit cube merge failed: {e_ted}")

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
    # B1299: validate the POST-dedup frame (pre-dedup duplicates are the
    # benchmark-auto-inclusion class fix-c removes by design).
    issues = validate_merge(trade_log_clean, input_dirs)
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
