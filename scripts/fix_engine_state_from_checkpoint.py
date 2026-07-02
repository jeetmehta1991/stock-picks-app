#!/usr/bin/env python
"""Batch 1094-A I4 helper (2026-07-02): auto-correct engine_state.json from CSV.

When engine self-kills (wall-time guard, OOM, spot interrupt), the final
checkpoint may write trades to trade_log_checkpoint.csv AFTER the last
engine_state.json update. This creates a mismatch where state.json's
simulated_day and trades_so_far LAG the CSV's actual content.

Naive resume then re-simulates already-done days -> duplicate trades.

Batch A recovery (2026-07-02) hit this exact issue: state.json said
simulated_day=704 / trades_so_far=4943 but CSV had 5081 trades through
2025-02-05 (day 719). Manual fix was applied.

This script automates that fix for the watchdog auto-resume path.

Logic:
  1. Read trade_log_checkpoint.csv; get max entry_date + max exit_date
  2. Determine trading-day index for max exit_date (or one before if
     ambiguous)
  3. Read state.json
  4. If CSV row count > state.json trades_so_far, update state.json:
       - simulated_day = derived from CSV max_exit
       - trades_so_far = CSV row count
       - sim_date      = CSV max_exit
       - status        = "resume_pending"
       - recovery_note  = automated-fix log
     Backup original to state.json.pre_autofix_YYYYMMDD_HHMMSS
  5. Print summary + exit code (0 = no fix needed, 1 = fix applied, 2 = error)

Usage:
  python scripts/fix_engine_state_from_checkpoint.py \
      --batch-dir output_batch_B_1787 \
      [--start-date 2022-05-05]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


def trading_days_between(start_date_str: str, end_date_str: str) -> int:
    """Approximate trading-day count between two dates using pandas
    business-day calendar (excludes weekends; does NOT exclude US holidays,
    so overcounts by ~10/year but is monotonic + close enough for resume-
    boundary determination)."""
    start = pd.Timestamp(start_date_str)
    end = pd.Timestamp(end_date_str)
    return len(pd.bdate_range(start, end)) - 1  # 0-indexed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-dir", required=True, help="Output directory of the batch (contains engine_state.json + trade_log_checkpoint.csv)")
    parser.add_argument("--start-date", default="2022-05-05", help="Phase window start date (for trading-day calc)")
    parser.add_argument("--dry-run", action="store_true", help="Report drift + intended fix without writing")
    args = parser.parse_args()

    batch_dir = Path(args.batch_dir)
    state_path = batch_dir / "engine_state.json"
    csv_path = batch_dir / "trade_log_checkpoint.csv"

    if not state_path.exists():
        print(f"ERROR: {state_path} not found")
        return 2
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found")
        return 2

    state = json.loads(state_path.read_text())
    df = pd.read_csv(csv_path)

    if len(df) == 0:
        print("INFO: CSV empty; no fix possible")
        return 0

    csv_rows = len(df)
    csv_max_entry = df["entry_date"].max() if "entry_date" in df.columns else None
    csv_max_exit = df["exit_date"].max() if "exit_date" in df.columns else csv_max_entry

    state_sim_day = int(state.get("simulated_day", 0))
    state_trades = int(state.get("trades_so_far", 0))

    print(f"State: simulated_day={state_sim_day} trades_so_far={state_trades} sim_date={state.get('sim_date')}")
    print(f"CSV:   rows={csv_rows} max_entry={csv_max_entry} max_exit={csv_max_exit}")

    if csv_rows <= state_trades:
        print("OK: no drift; state.json matches CSV")
        return 0

    # Derive corrected sim_day from CSV max_exit
    corrected_sim_day = trading_days_between(args.start_date, csv_max_exit)
    corrected_sim_date = csv_max_exit

    print(f"DRIFT: CSV has {csv_rows - state_trades} more trades than state.json accounts for")
    print(f"CORRECTION: simulated_day {state_sim_day} -> {corrected_sim_day}; trades_so_far {state_trades} -> {csv_rows}; sim_date -> {corrected_sim_date}")

    if args.dry_run:
        print("DRY-RUN: no changes written")
        return 1

    # Backup
    backup_ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = state_path.with_suffix(f".json.pre_autofix_{backup_ts}")
    shutil.copyfile(state_path, backup_path)
    print(f"Backup: {backup_path}")

    # Update
    state["simulated_day"] = corrected_sim_day
    state["sim_day_index"] = corrected_sim_day
    state["trades_so_far"] = csv_rows
    state["cells_completed"] = csv_rows
    state["sim_date"] = corrected_sim_date
    state["status"] = "resume_pending"
    state["timestamp"] = datetime.utcnow().isoformat() + "Z"
    prior_note = state.get("recovery_note", "")
    state["recovery_note"] = (
        f"AUTO-FIX by fix_engine_state_from_checkpoint.py at {backup_ts}Z: "
        f"drift detected (CSV rows {csv_rows} > state trades {state_trades}); "
        f"simulated_day corrected {state_sim_day} -> {corrected_sim_day} to match "
        f"CSV max_exit={csv_max_exit}. Backup: {backup_path.name}."
        + (f" Prior note: {prior_note}" if prior_note else "")
    )

    state_path.write_text(json.dumps(state, indent=2) + "\n")
    print(f"WROTE: {state_path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
