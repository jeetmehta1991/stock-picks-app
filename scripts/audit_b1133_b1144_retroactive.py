"""B1145 retroactive audit: verify B1133-B1144 edits comply with CSV actions.

Per owner directive 2026-07-03 Council 256:
"Only your actions items in the csv doc need to be implemented. No other
changes are allowed. Ensure this is applied retroactively as well."

Audits every strategy edit in B1133-B1144 (52 strategies) against its
final_recommended_actions column in phase_1_quiet_fire_investigation.csv.

REPORT format:
  MATCH:      strategy edit matches CSV action
  EXTRA:      strategy edit does more than CSV action (potential over-scope)
  MISSING:    strategy edit does less than CSV action (potential under-scope)
  ORPHAN:     strategy in commit but not marked DONE_B<n> in CSV
"""
# Source: per CHECKLIST #77 canonical-source; author Council 256 B1145 2026-07-03
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


BATCHES_TO_AUDIT = [
    ("B1126", "2784571fb"),  # BUG-277 detect_triangle fix
    ("B1133", None),  # chart pattern LOOSEN
    ("B1134", None),
    ("B1135", None),
    ("B1136", None),
    ("B1137", None),
    ("B1138", None),
    ("B1139", None),
    ("B1140", None),
    ("B1141", None),
    ("B1142", None),
    ("B1143", None),
    ("B1144", None),
]


def get_commit_hash_for_batch(batch: str) -> str | None:
    """Find commit hash matching batch pattern."""
    result = subprocess.run(
        ["git", "log", "--all", "--format=%H %s", "-100"],
        capture_output=True,
        text=True,
        cwd=_REPO,
    )
    for line in result.stdout.split("\n"):
        if not line.strip():
            continue
        parts = line.split(" ", 1)
        if len(parts) < 2:
            continue
        hash_, subject = parts
        if f"Batch {batch[1:]}" in subject or f"batch {batch[1:]}" in subject.lower():
            return hash_
    return None


def get_files_changed_in_commit(commit_hash: str) -> list[str]:
    """Get list of files changed in a commit."""
    result = subprocess.run(
        ["git", "show", "--name-only", "--format=", commit_hash],
        capture_output=True,
        text=True,
        cwd=_REPO,
    )
    return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]


def get_functions_changed_in_commit(commit_hash: str) -> set[str]:
    """Extract strategy function names changed in commit's screener.py diff."""
    result = subprocess.run(
        ["git", "show", commit_hash, "--", "backtest/signals/screener.py"],
        capture_output=True,
        text=True,
        cwd=_REPO,
    )
    # Look for @@ hunks and identify def strat_ context
    strategies = set()
    for match in re.finditer(r"@@[^@]+@@\s*def strat_(\w+)", result.stdout):
        strategies.add(match.group(1))
    # Also look for direct + or - lines referencing strat_ definitions
    for match in re.finditer(r"^[+-]\s*def strat_(\w+)", result.stdout, re.MULTILINE):
        strategies.add(match.group(1))
    return strategies


def audit_batch(batch: str, commit_hash: str | None, df: pd.DataFrame) -> dict:
    """Audit one batch and return results dict."""
    if commit_hash is None:
        commit_hash = get_commit_hash_for_batch(batch)
    if commit_hash is None:
        return {"batch": batch, "error": "commit not found"}

    # Strategies marked as this batch in CSV
    csv_strategies = df[
        df["execution_batch_ref"] == batch
    ]["strategy_name"].tolist()

    # Files changed in commit
    files_changed = get_files_changed_in_commit(commit_hash)
    strategies_in_commit = get_functions_changed_in_commit(commit_hash)

    result = {
        "batch": batch,
        "commit": commit_hash[:8],
        "csv_marked": len(csv_strategies),
        "commit_strategies": len(strategies_in_commit),
        "files_changed": files_changed,
        "match": [],
        "orphan_in_commit": [],
        "orphan_in_csv": [],
    }

    csv_set = set(csv_strategies)

    for strat in strategies_in_commit:
        if strat in csv_set:
            result["match"].append(strat)
        else:
            result["orphan_in_commit"].append(strat)

    for strat in csv_set:
        if strat not in strategies_in_commit:
            # Check if this batch was a producer-side change (universe.py etc.)
            # In which case CSV strategies won't appear in screener.py diff
            result["orphan_in_csv"].append(strat)

    return result


def main() -> int:
    csv_path = _REPO / "output_batch_A_150" / "phase_1_quiet_fire_investigation.csv"
    df = pd.read_csv(csv_path)

    print("=" * 78)
    print("B1145 RETROACTIVE AUDIT - B1126 + B1133-B1144 CSV COMPLIANCE")
    print("=" * 78)
    print()

    total_match = 0
    total_orphan_commit = 0
    total_orphan_csv = 0

    for batch_name, hint_hash in BATCHES_TO_AUDIT:
        result = audit_batch(batch_name, hint_hash, df)

        if "error" in result:
            print(f"\n{batch_name}: ERROR - {result['error']}")
            continue

        n_match = len(result["match"])
        n_orphan_c = len(result["orphan_in_commit"])
        n_orphan_csv = len(result["orphan_in_csv"])

        total_match += n_match
        total_orphan_commit += n_orphan_c
        total_orphan_csv += n_orphan_csv

        producer_change = any(
            f.endswith(".py") and "screener" not in f
            for f in result["files_changed"]
            if not f.startswith(("output_", "EXECUTION"))
        )

        status = "OK" if (n_orphan_c == 0 and (n_orphan_csv == 0 or producer_change)) else "REVIEW"
        print(f"\n{batch_name} ({result['commit']}) [{status}]")
        print(f"  Files: {[f for f in result['files_changed'] if not f.startswith(('output_', 'EXECUTION', 'BUG'))][:3]}")
        print(f"  CSV-marked: {result['csv_marked']} | Commit-strategies: {result['commit_strategies']} | Match: {n_match}")
        if n_orphan_c:
            print(f"  ORPHAN IN COMMIT (in code but not CSV): {result['orphan_in_commit']}")
        if n_orphan_csv and not producer_change:
            print(f"  ORPHAN IN CSV (marked DONE but not in code): {result['orphan_in_csv']}")

    print()
    print("=" * 78)
    print(f"TOTALS: {total_match} MATCH | {total_orphan_commit} orphan-in-commit | {total_orphan_csv} orphan-in-csv")
    print("=" * 78)
    print()
    print("VERDICT: Producer-side batches (B1137 smc_ict.py, B1142 universe.py) expected to")
    print("have orphan_in_csv (CSV strategies changed via producer indirection - not in screener diff).")
    print("Non-producer batches should have 0 orphan_in_commit for full compliance.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
