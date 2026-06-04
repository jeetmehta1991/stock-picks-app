"""Batch 576 (2026-06-04) - Backfill QUIET_NO_CANDIDATES rows in
approvals.json for strategies in ALL_STRATEGIES that don't currently
have any Stage 4 candidate row.

Per owner directive 2026-06-04: "We have 355 strategies in stage 4
approvals, while the strategy roster doc showws 205, why this drift?
Shouldnt both be the same? This is the drift you should be addressing
proactively."

The drift: ALL_STRATEGIES has 205 strategies but approvals.json only
has rows for 124 unique strategies. The 81 missing are strategies
that didn't fire in R4 so the optimizer didn't extract a candidate.
Owner has no Stage 4 visibility on them.

Fix: emit a placeholder row for each missing strategy with:
  change_class:    0  (special: not an actionable change class)
  change_class_name: "QUIET_NO_CANDIDATES"
  dimension_source: "drift_backfill_b576"
  status:          "Awaiting"
  change_detail:   "Strategy registered but did not fire in R4; no
                    optimizer candidate emitted. Investigate producer
                    health / compound restrictiveness on next R-iteration."

This makes the per-strategy Stage 4 status visible for ALL registered
strategies, closing the drift.

Usage:
  python scripts/backfill_quiet_strategies.py \
    --approvals C:/tmp/r4_optimization_candidates/approvals.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

CHANGE_CLASS_QUIET = 0
CHANGE_CLASS_NAME = "QUIET_NO_CANDIDATES"
CHANGE_DETAIL_TEMPLATE = (
    "Strategy `{name}` registered in ALL_STRATEGIES but did not fire in R4 "
    "(no optimizer candidate emitted). Surfaced for Stage 4 visibility per "
    "owner directive 2026-06-04 drift correction. Investigate producer "
    "health (B556/B559/B561 patterns) or compound restrictiveness; results "
    "feed next R-iteration."
)
CONFIG_TOUCH = (
    "n/a (no Stage 5 code change implied; this row exists only for "
    "Stage 4 visibility on quiet strategies)"
)


def _cid(strategy: str) -> str:
    h = hashlib.sha1(
        f"{strategy}|{CHANGE_CLASS_QUIET}|quiet_no_candidates".encode("utf-8")
    ).hexdigest()[:12]
    return f"r4-quiet-{h}"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--approvals", required=True)
    args = p.parse_args()

    apath = Path(args.approvals)
    if not apath.exists():
        print(f"ERROR: approvals.json not found: {apath}", file=sys.stderr)
        return 1

    data = json.loads(apath.read_text(encoding="utf-8"))
    rows = data["approvals"]
    existing_strategies = {r["strategy"] for r in rows}

    from backtest.signals.screener import ALL_STRATEGIES
    all_names = set(ALL_STRATEGIES.keys())
    missing = sorted(all_names - existing_strategies)

    print(f"ALL_STRATEGIES total:        {len(all_names)}")
    print(f"Strategies in approvals:     {len(existing_strategies)}")
    print(f"Missing (quiet, no rows):    {len(missing)}")
    if not missing:
        print("No drift to close. Done.")
        return 0

    now = datetime.now(timezone.utc).isoformat()
    for name in missing:
        new_row = {
            "candidate_id":       _cid(name),
            "strategy":           name,
            "change_class":       CHANGE_CLASS_QUIET,
            "change_class_name":  CHANGE_CLASS_NAME,
            "change_detail":      CHANGE_DETAIL_TEMPLATE.format(name=name),
            "dimension_source":   "drift_backfill_b576",
            "structured":         {
                "drift_close": True,
                "investigation_paths": [
                    "producer_health_check",
                    "compound_predicate_audit",
                    "fire_rate_per_signal_clause",
                ],
            },
            "rationale_metrics":  {"n_trades": 0, "fires": 0},
            "config_touch_point": CONFIG_TOUCH,
            "status":             "Awaiting",
            "status_set_at":      now,
            "status_set_by":      "system_drift_backfill",
            "rationale":          "",
            "dependency":         "",
            "conflicts":          [],
            "history":            [],
        }
        rows.append(new_row)

    # Recompute summary
    from collections import Counter
    summary = {
        "total": len(rows),
        "by_class": dict(Counter(str(r["change_class"]) for r in rows)),
        "by_status": dict(Counter(r["status"] for r in rows)),
    }
    for k in ("Awaiting", "Approved", "Rejected", "Deferred", "Implemented"):
        summary["by_status"].setdefault(k, 0)
    data["summary"] = summary
    data["last_decision_at"] = now
    apath.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"Backfilled {len(missing)} QUIET_NO_CANDIDATES rows.")
    print(f"Summary now: {summary['by_status']}")
    print(f"Total rows:  {summary['total']}")
    # Drift-close check:
    unique_now = {r["strategy"] for r in rows}
    ghosts = unique_now - all_names
    print(f"Unique strategies in approvals: {len(unique_now)} "
          f"(vs ALL_STRATEGIES {len(all_names)})")
    if ghosts:
        # Ghosts are LEGITIMATE in two cases:
        # 1. Strategies registered via non-ALL_STRATEGIES paths
        #    (e.g. lead_lag_sector_rotation -> screen_lead_lag_sector()
        #    at screener.py:4096; called from screen_universe).
        # 2. Class 7 NEW_STRATEGY Approved candidates awaiting wiring
        #    (e.g. news_sentiment_shift_short B571 Approved).
        # Report them but don't fail.
        print(f"Ghost strategies (in approvals, not in ALL_STRATEGIES): {len(ghosts)}")
        for g in sorted(ghosts):
            g_rows = [r for r in rows if r["strategy"] == g]
            classes = sorted({r["change_class"] for r in g_rows})
            sources = sorted({r["dimension_source"] for r in g_rows})
            print(f"  {g}: classes={classes} sources={sources}")
    assert (unique_now & all_names) == all_names, (
        f"Drift incomplete: {len(all_names - unique_now)} ALL_STRATEGIES "
        f"strategies still have no approvals row"
    )
    print("DRIFT CLOSED for ALL_STRATEGIES (every registered strategy "
          "now has at least one row).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
