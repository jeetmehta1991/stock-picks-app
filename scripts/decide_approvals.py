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

# Per-workflow Stage 4 6-class set + B571 Class 7 extension. Class 7
# NEW_STRATEGY captures owner-surfaced new-strategy candidates that the
# optimizer can't propose (it can only operate on existing roster rows).
# Surfaced via the per-strategy deep-dive protocol per
# feedback_per_strategy_deep_dive_stage4 memory.
VALID_CLASSES = {1, 2, 3, 4, 5, 6, 7}
CLASS_NAMES = {
    1: "STRATEGY_EXIT_OVERRIDE",
    2: "ENTRY_GATE_LOOSEN",
    3: "COMPOUND_RESTRUCTURE",
    4: "SIZING_TIER_REMAP",
    5: "STRATEGY_REGIME_AFFINITY",
    6: "ROSTER_DEPRECATION",
    7: "NEW_STRATEGY",
}
CONFIG_TOUCH = {
    1: "backtest/config.py::STRATEGY_EXIT_OVERRIDE",
    2: "backtest/signals/screener.py::strat_<name> predicate",
    3: "backtest/signals/screener.py::strat_<name> compound restructure",
    4: "backtest/config.py sizing tier dict",
    5: "backtest/config.py::STRATEGY_REGIME_AFFINITY",
    6: "backtest/config.py::DEPRECATED_STRATEGIES",
    7: "backtest/signals/screener.py new strat_<name> + ALL_STRATEGIES",
}


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


def add_owner_row(data: dict, args) -> dict:
    """B571: append an owner-surfaced candidate row to approvals.json.

    Use case: the per-strategy deep-dive surfaces Class 2 ENTRY_GATE_LOOSEN
    candidates (e.g., loosen news_sentiment_shift threshold 0.4 -> 0.2)
    or Class 7 NEW_STRATEGY candidates (e.g., write missing
    strat_news_sentiment_shift_short) that the B566 extractor couldn't
    derive from optimizer outputs.

    The new row carries dimension_source='owner_added' so it's
    distinguishable from optimizer-extracted rows in audit + dashboard."""
    import hashlib
    now = datetime.now(timezone.utc).isoformat()
    h = hashlib.sha1(
        f"{args.add_strategy}|{args.add_class}|{args.add_detail}".encode("utf-8")
    ).hexdigest()[:12]
    cid = f"r4-owner-{h}"
    new_row = {
        "candidate_id":       cid,
        "strategy":           args.add_strategy,
        "change_class":       args.add_class,
        "change_class_name":  CLASS_NAMES.get(args.add_class, "UNKNOWN"),
        "change_detail":      args.add_detail,
        "dimension_source":   "owner_added",
        "structured":         json.loads(args.add_structured) if args.add_structured else {},
        "rationale_metrics":  {},
        "config_touch_point": CONFIG_TOUCH.get(args.add_class, ""),
        "status":             args.to_status,
        "status_set_at":      now,
        "status_set_by":      args.by,
        "rationale":          args.rationale,
        "dependency":         args.dependency,
        "conflicts":          [],
        "history":            [{
            "ts":          now,
            "from_status": "Awaiting",
            "to_status":   args.to_status,
            "by":          args.by,
            "rationale":   args.rationale,
        }] if args.to_status != "Awaiting" else [],
    }
    data["approvals"].append(new_row)
    return new_row


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
                   help="change_class 1..7 (Class 7 = NEW_STRATEGY per B571)")
    p.add_argument("--status-from", default="",
                   help="filter to rows currently in this status")
    # B571: --add-row mode for owner-surfaced candidates
    p.add_argument("--add-row", action="store_true",
                   help="Append a new owner-surfaced row instead of "
                        "flipping existing rows. Requires --add-strategy / "
                        "--add-class / --add-detail.")
    p.add_argument("--add-strategy", default="",
                   help="strategy name for --add-row")
    p.add_argument("--add-class", type=int, default=None,
                   help="change class for --add-row (1..7)")
    p.add_argument("--add-detail", default="",
                   help="change_detail string for --add-row")
    p.add_argument("--add-structured", default="",
                   help="JSON dict literal for structured field on --add-row")
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

    # B571 --add-row mode: append a new owner-surfaced row + bypass
    # selector/flip path
    if args.add_row:
        if not (args.add_strategy and args.add_class and args.add_detail):
            print("ERROR: --add-row requires --add-strategy + --add-class + "
                  "--add-detail", file=sys.stderr)
            return 1
        if args.add_class not in VALID_CLASSES:
            print(f"ERROR: --add-class {args.add_class} not in "
                  f"{sorted(VALID_CLASSES)}", file=sys.stderr)
            return 1
        new_row = add_owner_row(data, args)
        print(f"Added owner row: {new_row['candidate_id']} "
              f"{new_row['strategy']} class={new_row['change_class']} "
              f"status={new_row['status']}")
        if args.dry_run:
            print("\nDRY RUN - approvals.json not written.")
            return 0
        data["summary"] = recompute_summary(data["approvals"])
        data["last_decision_at"] = datetime.now(timezone.utc).isoformat()
        apath.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"\nWrote {apath}")
        print(f"Summary now: {data['summary']['by_status']}")
        return 0

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
