"""Local parallel orchestrator for Phase 1A-beta.

Source: per CHECKLIST #77 canonical-source attribution. Owner directive
2026-05-23 (Batch 306): after GH Actions run #2 had 16/25 batches hit
timeout, run Phase 1A-beta locally with controlled parallelism.

Reads scripts/batch_splits_phase_1a_beta.json (25 batches, ~78 tkrs).
For each batch, launches `python -m backtest.run_phase1a --phase 1a-beta
--no-agents --no-git ...` as a subprocess. Concurrency configurable via
--max-parallel. Skips batches that already have a complete output dir
(checks for trade_log.csv -- the final-write marker) so the run is
resumable.

After all 25 batches finish, runs merge + IS/OOS report.

Usage:
    # Run locally with 4 parallel workers, default 4y window:
    python scripts/run_phase_1a_beta_local.py --max-parallel 4

    # Run a single batch first to validate pipeline:
    python scripts/run_phase_1a_beta_local.py --only 1

    # Resume after interruption (skips batches with completed trade_log.csv):
    python scripts/run_phase_1a_beta_local.py --max-parallel 4

    # Custom date range (e.g., 2-year OOS-only window):
    python scripts/run_phase_1a_beta_local.py --start 2024-05-01 --end 2026-04-30 --max-parallel 4
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SPLITS_PATH = REPO / "scripts" / "batch_splits_phase_1a_beta.json"
LOG_DIR = REPO / "logs" / "phase_1a_beta_local"


def output_dir_for_batch(batch_id: int) -> Path:
    return REPO / f"output_phase_1a_beta_batch{batch_id}"


def is_batch_complete(batch_id: int) -> bool:
    """Returns True if the batch has finished writing its final trade_log.csv.
    Engine writes trade_log.csv as the very last step, so its presence is the
    'complete' marker. Checkpoint files exist mid-run; we look only for the
    final write."""
    out = output_dir_for_batch(batch_id)
    return (out / "trade_log.csv").exists()


def run_one_batch(args_tuple) -> dict:
    batch_id, tickers, start, end = args_tuple
    out_dir = output_dir_for_batch(batch_id)
    log_path = LOG_DIR / f"batch_{batch_id:02d}.log"
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    tickers_csv = ",".join(tickers)
    t0 = time.time()
    with open(log_path, "w", encoding="utf-8") as logf:
        cmd = [
            sys.executable, "-m", "backtest.run_phase1a",
            "--phase", "1a-beta",
            "--no-agents",
            "--no-git",
            "--tickers", tickers_csv,
            "--start", start,
            "--end", end,
            "--output-dir", str(out_dir),
        ]
        logf.write(f"# Batch {batch_id} | {len(tickers)} tickers | {start}..{end}\n")
        logf.write(f"# Cmd: {' '.join(cmd[:6])} ...\n\n")
        logf.flush()
        proc = subprocess.Popen(
            cmd, cwd=str(REPO), stdout=logf, stderr=subprocess.STDOUT,
        )
        rc = proc.wait()
    elapsed = time.time() - t0
    ok = is_batch_complete(batch_id)
    return {
        "batch_id": batch_id,
        "rc": rc,
        "elapsed_sec": int(elapsed),
        "complete": ok,
        "log": str(log_path),
        "output_dir": str(out_dir),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--max-parallel", type=int, default=4,
                   help="Concurrent batch processes (default 4; tune for RAM)")
    p.add_argument("--start", default="2022-05-01")
    p.add_argument("--end", default="2026-04-30")
    p.add_argument("--only", type=int, default=None,
                   help="Run a single batch ID (1-25) for validation")
    p.add_argument("--exclude", type=str, default="",
                   help="Comma-separated batch IDs to skip (e.g. 1,3,9 for GH successes)")
    p.add_argument("--force", action="store_true",
                   help="Re-run even if trade_log.csv already exists for a batch")
    p.add_argument("--skip-merge", action="store_true",
                   help="Skip the final merge + IS/OOS step")
    args = p.parse_args()

    if not SPLITS_PATH.exists():
        print(f"ERROR: {SPLITS_PATH} missing. Run scripts/generate_phase_1a_beta_batches.py first.")
        return 1
    splits = json.loads(SPLITS_PATH.read_text())

    # Determine which batches to run
    exclude_ids = set()
    if args.exclude:
        exclude_ids = {int(x.strip()) for x in args.exclude.split(",") if x.strip()}
    if args.only is not None:
        batch_ids = [args.only]
    else:
        batch_ids = list(range(1, len(splits) + 1))
    batch_ids = [b for b in batch_ids if b not in exclude_ids]

    # Skip already-complete batches unless --force
    to_run = []
    already_done = []
    for b in batch_ids:
        if not args.force and is_batch_complete(b):
            already_done.append(b)
        else:
            to_run.append(b)

    print(f"Phase 1A-beta local orchestrator")
    print(f"  splits file:  {SPLITS_PATH.relative_to(REPO)}")
    print(f"  total batches in splits: {len(splits)}")
    print(f"  excluded:      {sorted(exclude_ids) if exclude_ids else 'none'}")
    print(f"  already done:  {sorted(already_done) if already_done else 'none'}")
    print(f"  to run now:    {to_run}")
    print(f"  max parallel:  {args.max_parallel}")
    print(f"  window:        {args.start} -> {args.end}")
    print()

    if not to_run:
        print("Nothing to do. All requested batches already have trade_log.csv.")
        return _run_merge_and_report(splits, batch_ids, args)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  per-batch logs at: {LOG_DIR.relative_to(REPO)}/")
    print(f"  estimated runtime: ~{5 * (len(to_run) / max(args.max_parallel,1)):.1f}h "
          f"(assumes ~5h per batch; verify after first wave)")
    print()

    tasks = []
    for b in to_run:
        key = f"batch_{b}"
        if key not in splits:
            print(f"WARN: {key} not in splits; skipping")
            continue
        tickers = splits[key]
        tasks.append((b, tickers, args.start, args.end))

    print(f"Launching {len(tasks)} batch processes (max {args.max_parallel} concurrent)...")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=args.max_parallel) as pool:
        futures = {pool.submit(run_one_batch, t): t[0] for t in tasks}
        for fut in as_completed(futures):
            bid = futures[fut]
            try:
                res = fut.result()
                results.append(res)
                tag = "OK " if res["complete"] else "FAIL"
                print(f"  [{tag}] batch {bid:2d}  elapsed={res['elapsed_sec']//60}m"
                      f"  rc={res['rc']}  log={Path(res['log']).name}")
            except Exception as exc:
                print(f"  [EXC]  batch {bid:2d}  exception={exc}")

    elapsed_total = time.time() - t0
    print()
    print(f"Local run complete in {elapsed_total/3600:.1f}h. "
          f"{sum(1 for r in results if r['complete'])}/{len(results)} successful.")
    print()

    if args.only is not None or args.skip_merge:
        print("Skipping merge (per --only or --skip-merge).")
        return 0

    return _run_merge_and_report(splits, batch_ids, args)


def _run_merge_and_report(splits, batch_ids, args) -> int:
    # Identify output dirs that exist + are complete
    complete_dirs = []
    incomplete = []
    for b in batch_ids:
        if is_batch_complete(b):
            complete_dirs.append(str(output_dir_for_batch(b)))
        else:
            incomplete.append(b)

    if not complete_dirs:
        print("ERROR: no complete batch output dirs found - nothing to merge.")
        return 1

    print(f"Merging {len(complete_dirs)} complete batches (skipping {len(incomplete)} incomplete: {incomplete})...")
    merged_dir = REPO / "output_phase_1a_beta_merged_local"
    merged_dir.mkdir(exist_ok=True)
    cmd = [
        sys.executable, "scripts/merge_batch_outputs.py",
        "--input-dirs", *complete_dirs,
        "--output-dir", str(merged_dir),
    ]
    print("  cmd:", " ".join(cmd[:4] + ["..."] + cmd[-2:]))
    rc = subprocess.call(cmd, cwd=str(REPO))
    if rc != 0:
        print(f"ERROR: merge returned rc={rc}")
        return rc

    print(f"\nMerged output: {merged_dir.relative_to(REPO)}/")

    # IS/OOS report (Batch 297)
    is_oos_cmd = [
        sys.executable, "scripts/phase_1a_beta_is_oos_report.py",
        "--output-dir", str(merged_dir),
    ]
    print("\nRunning IS/OOS report...")
    rc = subprocess.call(is_oos_cmd, cwd=str(REPO))
    if rc != 0:
        print(f"WARN: IS/OOS report returned rc={rc}")

    # Forensic audit
    audit_cmd = [
        sys.executable, "scripts/audit_trade_log_forensic.py",
        "--input", str(merged_dir / "trade_log.csv"),
    ]
    print("\nRunning forensic audit...")
    subprocess.call(audit_cmd, cwd=str(REPO))

    print("\n[OK] Phase 1A-beta local run complete.")
    print(f"     Merged output:  {merged_dir.relative_to(REPO)}/")
    print(f"     IS/OOS report:  {merged_dir.relative_to(REPO)}/IS_OOS_REPORT.md")
    print(f"     Trade log:      {merged_dir.relative_to(REPO)}/trade_log.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
