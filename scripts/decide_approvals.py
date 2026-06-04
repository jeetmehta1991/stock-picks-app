"""Batch 570 (2026-06-04) - Stage 4 owner-decision tool.

Flips the status of one or more candidates in approvals.json from
Awaiting -> Approved | Rejected | Deferred. Preserves audit trail
per workflow lines 344-345 by appending a history entry on every
status change.

Selectors (one required):
  --candidate-ids   comma-separated candidate_id list (most precise)
  --strategies      comma-separated strategy name list (all classes)
  --change-class    integer 1..6 (all rows of that class)
  --status-from     filter to rows currently in this status (combinable
                    with --change-class)

Mutators:
  --to-status  REQUIRED  one of Approved | Rejected | Deferred | Awaiting
  --by         REQUIRED  owner identifier (e.g. "owner_jeet")
  --rationale  REQUIRED  free-text reason (~1 sentence; goes to history)
  --dependency optional  for Deferred only - identifier of the unblock
                         signal (e.g. "smc_choch_path_audit")

Safety:
  --dry-run    show what would change; do not write
  --force      allow re-flipping rows already at the target status (no-op
               otherwise); allow Approved -> Rejected mid-flight (per
               workflow line 345 - rationale required)

Usage example (B570 the 7 Class-6 PLZL deferrals):
  python scripts/decide_approvals.py \
    --approvals C:/tmp/r4_optimization_candidates/approvals.json \
    --change-class 6 --status-from Awaiting \
    --to-status Deferred \
    --by owner_jeet --dependency producer_audit_per_strategy \
    --rationale "Defer pending per-strategy producer audit per \
project_no_apriori_strategy_pruning + workflow line 343 sweep advice; \
all 7 candidates are recent additions (May 17-31 2026) with known \
producer-fix precedent (B556/B559/B561)"
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


VALID_STATUSES = {"Approved", "Rejected", "Deferred", "Awaiting"}


def select_rows(rows: list, args) -> list:
    """Return rows that match the selector flags (intersection)."""
    out = list(rows)
    if args.candidate_ids:
        ids = {x.strip() for x in args.candidate_ids.split(",") if x.strip()}
        out = [r for r in out if r["candidate_id"] in ids]
    if args.strategies:
        strats = {x.strip() for x in args.strategies.split(",") if x.strip()}
        out = [r for r in out if r["strategy"] in strats]
    if args.change_class is not None:
        out = [r for r in out if r["change_class"] == args.change_class]
    if args.status_from:
        out = [r for r in out if r["status"] == args.status_from]
    return out


def apply_decision(rows: list, args) -> tuple[int, int, list]:
    """Apply the to-status flip to rows + write history entries.
    Returns (n_changed, n_noop, log_lines)."""
    now = datetime.now(timezone.utc).isoformat()
    changed, noop = 0, 0
    log = []
    for r in rows:
        old = r["status"]
        if old == args.to_status and not args.force:
            noop += 1
            log.append(f"  noop: {r['candidate_id']} already {old}")
            continue
        # Workflow line 345: Approved -> Rejected mid-flight requires
        # rationale (which we always require), force=True to acknowledge
        if old == "Approved" and args.to_status == "Rejected" and not args.force:
            log.append(
                f"  SKIP {r['candidate_id']}: Approved -> Rejected "
                f"requires --force (per workflow line 345)"
            )
            continue
        r["history"].append({
            "ts":         now,
            "from_status": old,
            "to_status":   args.to_status,
            "by":          args.by,
            "rationale":   args.rationale,
        })
        r["status"] = args.to_status
        r["status_set_at"] = now
        r["status_set_by"] = args.by
        r["rationale"] = args.rationale
        if args.to_status == "Deferred" and args.dependency:
            r["dependency"] = args.dependency
        elif args.to_status != "Deferred":
            # Clear dependency on non-Deferred flips
            r["dependency"] = ""
        changed += 1
        log.append(
            f"  {r['candidate_id']} {r['strategy']:<40} "
            f"{old:<9} -> {args.to_status:<9}"
        )
    return changed, noop, log


def recompute_summary(rows: list) -> dict:
    """Recompute summary.by_status + by_class after flips."""
    summary = {
        "total": len(rows),
        "by_class": {},
        "by_status": {k: 0 for k in VALID_STATUSES},
    }
    for r in rows:
        summary["by_status"][r["status"]] = summary["by_status"].get(r["status"], 0) + 1
        cls = str(r["change_class"])
        summary["by_class"][cls] = summary["by_class"].get(cls, 0) + 1
    return summary


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--approvals", required=True, help="approvals.json path")
    p.add_argument("--candidate-ids", default="",
                   help="comma-separated candidate_id list")
    p.add_argument("--strategies", default="",
                   help="comma-separated strategy name list")
    p.add_argument("--change-class", type=int, default=None,
                   help="change_class 1..6")
    p.add_argument("--status-from", default="",
                   help="filter to rows currently in this status")
    p.add_argument("--to-status", required=True, choices=sorted(VALID_STATUSES))
    p.add_argument("--by", required=True, help="owner identifier")
    p.add_argument("--rationale", required=True, help="free-text reason")
    p.add_argument("--dependency", default="",
                   help="for Deferred only - unblock signal id")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    apath = Path(args.approvals)
    if not apath.exists():
        print(f"ERROR: approvals.json not found: {apath}", file=sys.stderr)
        return 1
    data = json.loads(apath.read_text(encoding="utf-8"))
    rows = data["approvals"]

    selected = select_rows(rows, args)
    print(f"Selected {len(selected)} row(s):")
    if not selected:
        print("  (none matched selector flags)")
        return 0

    changed, noop, log = apply_decision(selected, args)
    for line in log[:50]:  # cap log
        print(line)
    if len(log) > 50:
        print(f"  ... and {len(log) - 50} more")
    print(f"\nResult: {changed} changed, {noop} noop")

    if args.dry_run:
        print("\nDRY RUN - approvals.json not written.")
        return 0

    # Recompute summary + write
    data["summary"] = recompute_summary(rows)
    data["last_decision_at"] = datetime.now(timezone.utc).isoformat()
    apath.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"\nWrote {apath}")
    print(f"Summary now: {data['summary']['by_status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
