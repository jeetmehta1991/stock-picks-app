"""Batch 368: Multi-batch parallel launcher for Phase 1A-beta cube run.

Source (per CHECKLIST #77 canonical-source attribution): owner directive
2026-05-25 ("proceed") after Batch 367 pre-launch validation suite all
6 phases green on Hetzner. Targets ~6.6h wall time on Hetzner CPX62 via
3-batch parallel partition of the 1937-ticker universe.

Per Stage 2 HARD CUT NO-LIVE-API + DEC-503 13-tier pyramid rules, this
ONLY orchestrates — actual backtest engine invocations go through
`python -m backtest.run_phase1a` with the Batch 322 process pool wiring.

Architecture:
  - Partition Master Dedup universe (~1937 tickers) into N batches
  - Each batch runs as own tmux session: `phase1a_bN`
  - Pool workers per batch = (16 cores / N batches), capped at 6
  - Output dirs: `output_phase_1a_beta_cube_b1/`, `_b2/`, `_b3/`
  - Post-run: scripts/merge_batch_outputs.py concatenates trade_log +
    trade_exit_detail and re-aggregates cube slices

Usage on Hetzner:
  python scripts/launch_phase_1a_beta_multibatch.py \
      --start 2022-05-05 --end 2026-05-05 \
      --batches 3 --pool-workers 5 \
      --output-prefix output_phase_1a_beta_cube \
      --launch

  Without --launch, it prints the tmux commands and partition counts
  without actually launching (dry-run for owner review).

Pre-flight:
  1. Run `scripts/pre_launch_validation.py` first; only proceed if PASS.
  2. Verify Hetzner Quiver prefetch sync (Batches 363 fix).
  3. Verify tmux sessions phase1a_b* don't already exist.

Post-run merge:
  python scripts/merge_batch_outputs.py \
      --input-dirs output_phase_1a_beta_cube_b1 output_phase_1a_beta_cube_b2 \
                   output_phase_1a_beta_cube_b3 \
      --output-dir output_phase_1a_beta_cube_merged
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MASTER_DEDUP = REPO / "Backtesting universe" / "Master Universe_Deduplicated_All Tiers_May 2026.csv"


def load_universe() -> list[str]:
    """Load all unique tickers from the Master Dedup CSV.

    File schema: header comment lines + CSV with Symbol column.
    """
    tickers = []
    with MASTER_DEDUP.open("r", encoding="utf-8") as f:
        # Skip leading comment lines
        lines = [line for line in f if not line.startswith("#")]
    reader = csv.DictReader(lines)
    for row in reader:
        symbol = row.get("Symbol", "").strip()
        if symbol and symbol not in tickers:
            tickers.append(symbol)
    return tickers


def partition(tickers: list[str], n: int) -> list[list[str]]:
    """Split tickers into n balanced partitions, preserving order so the
    same ticker always lands in the same batch (deterministic re-runs)."""
    chunk = (len(tickers) + n - 1) // n
    return [tickers[i:i + chunk] for i in range(0, len(tickers), chunk)]


def build_tmux_command(
    batch_id: int, tickers: list[str], start: str, end: str,
    pool_workers: int, output_dir: str,
) -> str:
    """Build the single-line tmux new-session command for one batch."""
    tickers_arg = ",".join(tickers)
    log_file = f"{output_dir}/run.log"
    inner_cmd = (
        f".venv/bin/python -m backtest.run_phase1a "
        f"--phase 1a-beta "
        f"--start {start} --end {end} "
        f"--tickers '{tickers_arg}' "
        f"--screen-pool-workers {pool_workers} "
        f"--no-git "
        f"--output-dir {output_dir} "
        f"2>&1 | tee {log_file}"
    )
    session = f"phase1a_b{batch_id}"
    return f"tmux new-session -d -s {session} -c ~/stock-picks-app '{inner_cmd}'"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2022-05-05")
    ap.add_argument("--end",   default="2026-05-05")
    ap.add_argument("--batches", type=int, default=3,
                    help="Number of parallel partitions")
    ap.add_argument("--pool-workers", type=int, default=5,
                    help="screen-pool workers per batch")
    ap.add_argument("--output-prefix", default="output_phase_1a_beta_cube")
    ap.add_argument("--launch", action="store_true",
                    help="Actually launch (default: dry-run prints)")
    args = ap.parse_args()

    tickers = load_universe()
    print(f"Master Dedup universe: {len(tickers)} unique tickers")
    parts = partition(tickers, args.batches)
    for i, p in enumerate(parts, 1):
        print(f"  Batch {i}: {len(p)} tickers ({p[0]!r} -> {p[-1]!r})")

    print()
    total_active_procs = args.batches + (args.batches * args.pool_workers)
    print(f"Plan: {args.batches} parallel batches x {args.pool_workers} pool workers each")
    print(f"      = {total_active_procs} active processes on Hetzner (16 cores)")
    print(f"Output dirs: {args.output_prefix}_b1/ ... _b{args.batches}/")
    print()

    commands = []
    for i, batch_tickers in enumerate(parts, 1):
        out_dir = f"{args.output_prefix}_b{i}"
        # Ensure output dir exists before tmux launches
        cmd_mkdir = f"mkdir -p {out_dir}"
        cmd_tmux = build_tmux_command(
            batch_id=i, tickers=batch_tickers,
            start=args.start, end=args.end,
            pool_workers=args.pool_workers,
            output_dir=out_dir,
        )
        commands.append((cmd_mkdir, cmd_tmux))

    if not args.launch:
        print("--- DRY RUN (use --launch to actually start) ---")
        for cmd_mkdir, cmd_tmux in commands:
            print(cmd_mkdir)
            print(cmd_tmux)
            print()
        return 0

    # Launch
    print("--- LAUNCHING ---")
    for cmd_mkdir, cmd_tmux in commands:
        for cmd in (cmd_mkdir, cmd_tmux):
            print(f"$ {cmd[:120]}{'...' if len(cmd) > 120 else ''}")
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if r.returncode != 0:
                print(f"FAILED: {r.stderr}")
                return 1
    print()
    print("All batches launched. Monitor via:")
    print(f"  tmux list-sessions")
    print(f"  tmux attach -t phase1a_b1")
    print(f"  tail -f {args.output_prefix}_b1/run.log")
    return 0


if __name__ == "__main__":
    sys.exit(main())
