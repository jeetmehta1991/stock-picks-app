"""Batch 567 (2026-06-03) - Stage 4 step 2 of 4 per
PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md.

Reads r4_proposed_changes.json (from B566 extractor) and writes
approvals.json - the persistent state file for Stage 4 per-change
owner decisions.

Schema (per workflow lines 641-645):
  {
    "version":      "r4",
    "generated_at": ISO timestamp,
    "source":       path to r4_proposed_changes.json,
    "summary":      { class breakdown + status totals },
    "approvals":    [
      {
        "candidate_id":      str   (copied from proposed_changes)
        "strategy":          str
        "change_class":      int   (1..6)
        "change_class_name": str
        "change_detail":     str
        "dimension_source":  str
        "structured":        dict
        "rationale_metrics": dict
        "config_touch_point":str
        "status":            "Awaiting" | "Approved" | "Rejected" | "Deferred"
        "status_set_at":     ISO timestamp
        "status_set_by":     "system_init" | owner-id later
        "rationale":         str   (empty for Awaiting; populated on flip)
        "dependency":        str   (Deferred: what unblocks it)
        "conflicts":         []    (populated at B568)
        "history":           [{ts, from_status, to_status, by, rationale}]
      },
      ...
    ]
  }

Workflow line 337 mandate: Class 5 STRATEGY_REGIME_AFFINITY rows
auto-DEFERRED until Phase 1B-alpha transition (Phase 1A-beta cubes
run with --no-regime-affinity so the affinity map can't be applied
inside the current cube; approval would have no operational effect
until 1B-alpha). All other classes default to "Awaiting" for owner
decision.

Usage:
  python scripts/init_approvals.py \
    --input  C:/tmp/r4_optimization_candidates/r4_proposed_changes.json \
    --output C:/tmp/r4_optimization_candidates/approvals.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


CLASS5_AUTO_DEFER_RATIONALE = (
    "Phase 1A-beta cubes run with --no-regime-affinity so STRATEGY_REGIME_AFFINITY "
    "approvals would have no operational effect until Phase 1B-alpha transition. "
    "Auto-deferred per PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md line 337. "
    "Will re-surface on Phase 1B-alpha entry."
)
CLASS5_DEPENDENCY = "phase_1b_alpha_transition"


def init_approvals(rows: list, source_path: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    approvals = []
    summary = {
        "total": len(rows),
        "by_class": {},
        "by_status": {"Awaiting": 0, "Approved": 0, "Rejected": 0, "Deferred": 0},
    }
    for r in rows:
        is_class5 = r["change_class"] == 5
        status = "Deferred" if is_class5 else "Awaiting"
        rationale = CLASS5_AUTO_DEFER_RATIONALE if is_class5 else ""
        dependency = CLASS5_DEPENDENCY if is_class5 else ""

        approvals.append({
            "candidate_id":       r["candidate_id"],
            "strategy":           r["strategy"],
            "change_class":       r["change_class"],
            "change_class_name":  r["change_class_name"],
            "change_detail":      r["change_detail"],
            "dimension_source":   r["dimension_source"],
            "structured":         r.get("structured", {}),
            "rationale_metrics":  r.get("rationale_metrics", {}),
            "config_touch_point": r["config_touch_point"],
            "status":             status,
            "status_set_at":      now,
            "status_set_by":      "system_init",
            "rationale":          rationale,
            "dependency":         dependency,
            "conflicts":          [],
            "history":            [],
        })
        cls_key = str(r["change_class"])
        summary["by_class"][cls_key] = summary["by_class"].get(cls_key, 0) + 1
        summary["by_status"][status] += 1

    return {
        "version":      "r4",
        "generated_at": now,
        "source":       source_path,
        "summary":      summary,
        "approvals":    approvals,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True,
                   help="Path to r4_proposed_changes.json from B566 extractor")
    p.add_argument("--output", required=True,
                   help="Path to write approvals.json")
    p.add_argument("--force", action="store_true",
                   help="Overwrite approvals.json if it exists. Default is "
                        "to refuse so existing owner decisions aren't clobbered.")
    args = p.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    if not in_path.exists():
        print(f"ERROR: input file not found: {in_path}", file=sys.stderr)
        return 1
    if out_path.exists() and not args.force:
        print(f"ERROR: {out_path} exists. Use --force to overwrite (will "
              f"clobber any in-flight owner decisions). Default-refuse is "
              f"per workflow line 344-345 audit-trail discipline.",
              file=sys.stderr)
        return 2

    rows = json.loads(in_path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        print(f"ERROR: input not a list (got {type(rows).__name__})",
              file=sys.stderr)
        return 1

    payload = init_approvals(rows, str(in_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    s = payload["summary"]
    print(f"Initialized approvals.json -> {out_path}")
    print(f"  total: {s['total']}")
    print(f"  by status:")
    for k in ("Awaiting", "Deferred", "Approved", "Rejected"):
        print(f"    {k}: {s['by_status'][k]}")
    print(f"  by class:")
    for k in sorted(s["by_class"].keys()):
        print(f"    Class {k}: {s['by_class'][k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
