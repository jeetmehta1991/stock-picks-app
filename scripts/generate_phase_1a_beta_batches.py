"""
scripts/generate_phase_1a_beta_batches.py
Generate 25 ticker batch splits for parallel Phase 1A-beta runs.

Per owner directive 2026-05-22 Batch 305: re-split from 5x388 to 25x78
after Batch 304 owner-reported runtime failures. Original 5-batch design
(Batch 181 2026-05-15) blew the GitHub-hosted runner 6-hour job cap on
every run.

Sizing rationale (Stage D empirical extrapolation):
  Stage D measured pace = ~0.22 sec/ticker/sim-day on same-class runner.
  For 1044 sim-days (2022-05-01..2026-04-30) at 78 tkrs:
    78 * 1044 * 0.22 = ~17,900 sec = ~5 hours per batch.
  Compare to prior 5x388 design which projected ~25h per batch.

  GitHub-hosted runners cap individual jobs at 6 hours. 25x78 leaves
  ~1h headroom under that cap. timeout-minutes set to 350 in workflow.

  GH free-tier private-repo concurrency = 20 jobs. Matrix runs 20 in
  wave 1 + 5 in wave 2 -> ~10h total wall clock.

Stratified split: each batch gets proportional representation from each
resolved_tier so a partial run still has tier coverage. Within tier,
preserve alphabetical order for reproducibility.

Usage:
    python scripts/generate_phase_1a_beta_batches.py

Outputs:
    scripts/batch_splits_phase_1a_beta.json  — 25 lists of tickers
    Prints exact run commands for each batch.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
CSV = REPO / "Backtesting universe" / "Master Universe_Deduplicated_All Tiers_May 2026.csv"
OUT_JSON = REPO / "scripts" / "batch_splits_phase_1a_beta.json"

N_BATCHES = 25


def main() -> int:
    if not CSV.exists():
        print(f"ERROR: {CSV} not found")
        return 1
    df = pd.read_csv(CSV, comment="#")
    if "Symbol" not in df.columns or "resolved_tier" not in df.columns:
        print(f"ERROR: missing Symbol or resolved_tier column")
        return 1
    df["Symbol"] = df["Symbol"].astype(str).str.upper().str.strip()
    df = df.drop_duplicates(subset=["Symbol"]).sort_values(["resolved_tier", "Symbol"])

    print(f"Master Universe: {len(df)} unique tickers")
    print("Tier distribution:")
    for tier, count in df["resolved_tier"].value_counts().items():
        print(f"  {tier:8s} {count:>5}")

    # Stratified split: round-robin within each tier so each batch gets
    # proportional tier representation. Within tier we preserve sorted order.
    batches: list[list[str]] = [[] for _ in range(N_BATCHES)]
    for tier, tier_df in df.groupby("resolved_tier", sort=True):
        for i, sym in enumerate(tier_df["Symbol"].tolist()):
            batches[i % N_BATCHES].append(sym)

    # Sanity checks: no overlap, no missing
    all_t = [t for b in batches for t in b]
    assert len(all_t) == len(df), f"Count mismatch: {len(all_t)} vs {len(df)}"
    assert len(set(all_t)) == len(all_t), "Duplicate detected"

    OUT_JSON.write_text(
        json.dumps({f"batch_{i+1}": b for i, b in enumerate(batches)}, indent=2),
        encoding="utf-8",
    )

    print(f"\n[OK] Split written to {OUT_JSON.relative_to(REPO)}\n")
    for i, batch in enumerate(batches, 1):
        # Per-batch tier breakdown
        tier_counts = df[df["Symbol"].isin(batch)]["resolved_tier"].value_counts().to_dict()
        tier_str = " ".join(f"{k}={v}" for k, v in sorted(tier_counts.items()))
        print(f"  Batch {i}: {len(batch):>4} tickers  ({tier_str})")

    print("\n" + "=" * 70)
    print("LAUNCH COMMANDS (run 5 in parallel as background jobs)")
    print("=" * 70)
    for i, batch in enumerate(batches, 1):
        tickers_csv = ",".join(batch[:5]) + (",..." if len(batch) > 5 else "")
        print(f"\n# Batch {i}: {len(batch)} tickers ({tickers_csv})")
        print(f"python backtest/run_phase1a.py --phase 1a-beta --no-agents --no-git \\")
        print(f"  --tickers \"$(python -c 'import json; print(\",\".join(json.load(open(\\\"scripts/batch_splits_phase_1a_beta.json\\\"))[\"batch_{i}\"]))')\" \\")
        print(f"  --output-dir output_phase_1a_beta_batch{i}")

    print("\n# After all 5 finish, merge:")
    print(f"python scripts/merge_batch_outputs.py --input-dirs " +
          " ".join(f"output_phase_1a_beta_batch{i}" for i in range(1, N_BATCHES + 1)) +
          " --output-dir output_phase_1a_beta_final")
    return 0


if __name__ == "__main__":
    sys.exit(main())
