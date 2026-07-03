#!/usr/bin/env python
"""Council 239 (2026-07-03): Add execution_status + execution_batch_ref columns.

Two new columns for lifecycle tracking of final_recommended_actions:

execution_status values:
  PENDING             - default; no work started
  IN_PROGRESS_B<n>    - actively being addressed in batch n
  DONE_B<n>           - fully addressed and verified in batch n
  SKIPPED_<reason>    - explicit skip: SKIPPED_STRUCTURAL_RARE / SKIPPED_UNIVERSE_ONLY
  BLOCKED_<reason>    - blocked by upstream: BLOCKED_DATA_MISSING / BLOCKED_PRODUCER_BUG
  SUPERSEDED_B<n>     - recommendation was superseded by later analysis in batch n

execution_batch_ref: comma-separated batch numbers, e.g. 'B1121,B1126'.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


# Initial state overrides:
# 1. DISABLED_PENDING_DATA -> BLOCKED_DATA_MISSING
# 2. FIX_PRODUCER-primary + producer identified BROKEN -> BLOCKED_PRODUCER_BUG
BLOCKED_DATA_MISSING = {
    "post_deletion_drift_short",
    "post_inclusion_drift_long",
    "post_inclusion_reversal_short",
    "pre_rebalance_long",
}

BLOCKED_PRODUCER_BUG = {
    "triangle_ascending_long",
    "triangle_ascending_retest_long",
    "triangle_descending_short",
    "halloween_seasonal_long",
    "totm_long",
    "pre_holiday_long",
}


def _classify_initial_status(row: pd.Series) -> tuple[str, str]:
    """Return (execution_status, execution_batch_ref) tuple."""
    strat = row["strategy_name"]
    actions = str(row.get("final_recommended_actions", ""))

    if strat in BLOCKED_DATA_MISSING:
        return ("BLOCKED_DATA_MISSING", "")
    if strat in BLOCKED_PRODUCER_BUG:
        return ("BLOCKED_PRODUCER_BUG", "")
    if "DISABLED_PENDING_DATA" in actions:
        return ("BLOCKED_DATA_MISSING", "")

    return ("PENDING", "")


def main() -> int:
    csv_path = Path("output_batch_A_150/phase_1_quiet_fire_investigation.csv")
    df = pd.read_csv(csv_path)

    if "execution_status" not in df.columns:
        df["execution_status"] = ""
    if "execution_batch_ref" not in df.columns:
        df["execution_batch_ref"] = ""

    statuses = df.apply(_classify_initial_status, axis=1)
    df["execution_status"] = [s[0] for s in statuses]
    df["execution_batch_ref"] = [s[1] for s in statuses]

    df.to_csv(csv_path, index=False)

    print(f"Added execution_status + execution_batch_ref columns to {len(df)} rows.")
    print()
    print("INITIAL STATUS DISTRIBUTION:")
    for status in sorted(df["execution_status"].unique()):
        n = (df["execution_status"] == status).sum()
        print(f"  {status:30s}: {n:3d}")
    print()
    print("BLOCKED strategies (10 total):")
    blocked = df[df["execution_status"].str.startswith("BLOCKED")]
    for _, r in blocked.iterrows():
        print(
            f"  {r['strategy_name']:40s} status={r['execution_status']} "
            f"(n_fires={int(r['n_fires'])})"
        )
    print()
    print("COLUMNS NOW IN CSV:")
    for col in df.columns:
        print(f"  {col}")
    print(f"\nTotal columns: {len(df.columns)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
