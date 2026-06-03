"""Batch 568 (2026-06-03) - Stage 4 step 3 of 4 per
PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md.

Pre-approval cross-sweep per workflow line 343 +
`feedback_audit_recommendations_against_existing_directives` memory.

For each Awaiting row in approvals.json:
  1. Search a curated doc set for mentions of the row's strategy
  2. Apply class-specific contradiction rules
  3. Populate the row's `conflicts: []` field with structured findings
  4. Save back to approvals.json (preserves status + history + everything
     else; only `conflicts` field is rewritten)

Severity ladder:
  blocker    - must be addressed before owner can Approve (e.g., a DEC
               that explicitly pins the parameter the proposal would change)
  warning    - probably worth owner attention (e.g., LEARNINGS entry about
               this strategy area, prior BUG cross-ref)
  info       - mention found, contextual only (e.g., strategy listed in
               CLAUDE.md fork-architecture line)

Doc set scanned:
  - CLAUDE.md
  - PROJECT_PLAN.md
  - DETAILED_PROJECT_PLAN.md
  - LEARNINGS.md
  - AUDIT.md  (lazy: only first 100KB to avoid full historical narrative
               grep cost; per L143 history is in archive/)
  - PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md (workflow self-reference)
  - memory/*.md (user memory)

Class-specific rules:
  Class 1 STRATEGY_EXIT_OVERRIDE:
    - If backtest/config.py::STRATEGY_EXIT_OVERRIDE already pins this
      strategy -> blocker (conflicts with existing pin)
    - If 5-gate verdict is FAIL -> warning (deploying a 5-gate-FAIL
      exit override would contradict workflow line 535-543 5-gate
      validity criteria - owner can override but should know)
  Class 3 COMPOUND_RESTRUCTURE:
    - Info-only: surface CLAUDE.md / LEARNINGS mentions of the strategy
  Class 4 SIZING_TIER_REMAP:
    - If proposed_tier is LOW (skip) and agg_sharpe > 0.7 -> warning
      (would skip a strategy that's borderline PASS per CLAUDE.md
      per-regime threshold)
    - If proposed_tier is EXCEPTIONAL and agg_sharpe < 1.5 -> warning
  Class 5 STRATEGY_REGIME_AFFINITY: skipped (auto-Deferred per workflow
    line 337; owner re-surfaces at 1B-alpha transition)
  Class 6 ROSTER_DEPRECATION:
    - Always cross-check `project_no_apriori_strategy_pruning` memory:
      empirical-only gate -> info ref. The B566 extractor already gated
      to PLZL bucket (workflow line 335), so this is consistency check.

Usage:
  python scripts/preflight_cross_sweep.py \
    --approvals C:/tmp/r4_optimization_candidates/approvals.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

DOC_SET = [
    REPO / "CLAUDE.md",
    REPO / "PROJECT_PLAN.md",
    REPO / "DETAILED_PROJECT_PLAN.md",
    REPO / "LEARNINGS.md",
    REPO / "PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md",
]
MEMORY_DIR = (
    Path.home() / ".claude" / "projects"
    / "c--Users-jeetm-Github-stock-picks-app" / "memory"
)
AUDIT_MD = REPO / "AUDIT.md"

# Class 4 sizing thresholds (per CLAUDE.md passing criteria table)
SHARPE_PER_REGIME_MIN = 0.7
SHARPE_OVERALL_MIN = 1.0
SHARPE_EXCEPTIONAL_FLOOR = 1.5


def _load_docs() -> dict:
    """Returns {filename: text} for the curated doc set."""
    out = {}
    for p in DOC_SET:
        if p.exists():
            try:
                out[p.name] = p.read_text(encoding="utf-8")
            except Exception:
                pass
    if MEMORY_DIR.exists():
        for mp in sorted(MEMORY_DIR.glob("*.md")):
            try:
                out[f"memory/{mp.name}"] = mp.read_text(encoding="utf-8")
            except Exception:
                pass
    if AUDIT_MD.exists():
        try:
            # Lazy read: first 100KB only
            with AUDIT_MD.open("r", encoding="utf-8") as f:
                out["AUDIT.md"] = f.read(100_000)
        except Exception:
            pass
    return out


def _strategy_mentions(strategy: str, docs: dict) -> list:
    """For a strategy name, find mentions across the doc set with 1-line
    context. Empty list if no mentions."""
    hits = []
    pattern = re.compile(re.escape(strategy), re.IGNORECASE)
    for name, text in docs.items():
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if pattern.search(line):
                hits.append({
                    "source": name,
                    "line_no": i + 1,
                    "snippet": line.strip()[:300],
                })
                if len(hits) >= 20:
                    return hits
    return hits


def _load_existing_overrides() -> set:
    """Read backtest/config.py and find strategy names in
    STRATEGY_EXIT_OVERRIDE / STRATEGIES_DISABLED_MISSING_PRODUCER /
    DEPRECATED_STRATEGIES. Used for Class 1 / Class 6 conflict checks."""
    cfg = REPO / "backtest" / "config.py"
    if not cfg.exists():
        return set()
    try:
        text = cfg.read_text(encoding="utf-8")
    except Exception:
        return set()
    # Find any "strategy_name" string that looks like a strategy key
    # NOTE: heuristic - looks for strings near STRATEGY_EXIT_OVERRIDE dict
    m = re.search(
        r"STRATEGY_EXIT_OVERRIDE\s*[:=]\s*\{([^}]*)\}",
        text, re.DOTALL,
    )
    if not m:
        return set()
    return set(re.findall(r"['\"]([a-z][a-z0-9_]+)['\"]", m.group(1)))


def _conflicts_for_row(row: dict, docs: dict,
                      existing_overrides: set,
                      no_apriori_principle_text: str) -> list:
    """Apply class-specific rules and return a list of conflict dicts."""
    conflicts = []
    cls = row["change_class"]
    strat = row["strategy"]
    struct = row.get("structured") or {}
    metrics = row.get("rationale_metrics") or {}

    if cls == 1:
        # Existing override pin?
        if strat in existing_overrides:
            conflicts.append({
                "rule": "existing_override",
                "severity": "blocker",
                "source": "backtest/config.py::STRATEGY_EXIT_OVERRIDE",
                "evidence": f"'{strat}' already has an exit override pin",
                "advice": "Owner must reconcile new proposal with the "
                          "existing pin before Approve",
            })
        # 5-gate FAIL warning
        if struct.get("five_gate_verdict") == "FAIL":
            conflicts.append({
                "rule": "five_gate_fail",
                "severity": "warning",
                "source": "workflow line 535-543",
                "evidence": (
                    f"proposed exit `{struct.get('proposed_exit_method')}` "
                    f"5-gate verdict = FAIL (Sharpe "
                    f"{struct.get('cell_sharpe')}, n={struct.get('cell_n')})"
                ),
                "advice": "Cell did not meet 5-gate validity criteria "
                          "(n>=30 + p<0.05 Bonferroni + PSR>=0.95 + t>=3.4 "
                          "+ R:R>=2.0). Approving anyway means deploying a "
                          "cell that failed canonical validity gates.",
            })

    elif cls == 4:
        proposed = struct.get("proposed_tier", "")
        sharpe = struct.get("agg_sharpe") or 0
        try:
            sharpe = float(sharpe)
        except (TypeError, ValueError):
            sharpe = 0
        if "LOW" in proposed and sharpe >= SHARPE_PER_REGIME_MIN:
            conflicts.append({
                "rule": "low_skip_with_passing_sharpe",
                "severity": "warning",
                "source": "CLAUDE.md passing criteria #10",
                "evidence": (
                    f"proposed LOW (skip) but agg_sharpe = {sharpe} "
                    f">= per-regime minimum {SHARPE_PER_REGIME_MIN}"
                ),
                "advice": "Skipping a strategy with Sharpe at or above the "
                          "per-regime PASS threshold may be overly conservative. "
                          "Owner may prefer MEDIUM-HIGH tier with empirical "
                          "verification at R5.",
            })
        if "EXCEPTIONAL" in proposed and sharpe < SHARPE_EXCEPTIONAL_FLOOR:
            conflicts.append({
                "rule": "exceptional_below_floor",
                "severity": "warning",
                "source": "CLAUDE.md sizing tier table",
                "evidence": (
                    f"proposed EXCEPTIONAL (5pct sizing) but agg_sharpe "
                    f"= {sharpe} < EXCEPTIONAL floor {SHARPE_EXCEPTIONAL_FLOOR}"
                ),
                "advice": "EXCEPTIONAL tier is reserved for highest-conviction "
                          "cells per CLAUDE.md sizing table.",
            })

    elif cls == 5:
        # auto-Deferred; no conflict to surface (revisited at 1B-alpha)
        pass

    elif cls == 6:
        # Empirical-only gate per workflow line 335 +
        # `project_no_apriori_strategy_pruning`. The B566 extractor
        # gated to PLZL bucket already - this is a consistency check.
        if no_apriori_principle_text:
            conflicts.append({
                "rule": "no_apriori_principle",
                "severity": "info",
                "source": "memory/project_no_apriori_strategy_pruning.md",
                "evidence": "Empirical-only deprecation principle in force; "
                            "PLZL bucket gating satisfies the empirical gate.",
                "advice": "Owner should verify that the producer is genuinely "
                          "broken (i.e., not a missing-data issue fixable by "
                          "the B556-pattern SMC fix or B561-pattern data "
                          "expansion) before flipping to Approved.",
            })

    # Doc mentions (info-level) for ALL classes
    mentions = _strategy_mentions(strat, docs)
    for m in mentions[:10]:  # cap per row to avoid bloat
        # Filter to "interesting" mentions (DEC- / BUG- / locked /
        # preserve / do not change / RESOLVED / deprecat)
        text = m["snippet"].lower()
        is_interesting = any(
            kw in text for kw in [
                "dec-", "bug-", "locked", "preserve",
                "do not change", "resolved", "deprecat", "disable",
                "override", "regime affinity", "strategy_regime_affinity",
                "strategy_exit_override",
            ]
        )
        if is_interesting:
            conflicts.append({
                "rule": "doc_mention",
                "severity": "info",
                "source": m["source"],
                "evidence": f"L{m['line_no']}: {m['snippet']}",
                "advice": "Cross-check this prior reference before Approve.",
            })

    return conflicts


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--approvals", required=True,
                   help="Path to approvals.json from B567")
    args = p.parse_args()

    apath = Path(args.approvals)
    if not apath.exists():
        print(f"ERROR: approvals.json not found: {apath}", file=sys.stderr)
        return 1

    payload = json.loads(apath.read_text(encoding="utf-8"))
    rows = payload["approvals"]

    print(f"Loading doc set for cross-sweep...")
    docs = _load_docs()
    print(f"  docs scanned: {len(docs)}")

    existing_overrides = _load_existing_overrides()
    print(f"  existing STRATEGY_EXIT_OVERRIDE keys: {len(existing_overrides)}")

    no_apriori = docs.get("memory/project_no_apriori_strategy_pruning.md", "")

    severity_counts = {"blocker": 0, "warning": 0, "info": 0}
    rows_with_conflicts = 0
    for r in rows:
        # Only sweep rows still in Awaiting / Deferred; Approved/Rejected
        # don't need fresh sweep (decision already taken)
        if r["status"] not in ("Awaiting", "Deferred"):
            continue
        cs = _conflicts_for_row(r, docs, existing_overrides, no_apriori)
        r["conflicts"] = cs
        if cs:
            rows_with_conflicts += 1
            for c in cs:
                severity_counts[c["severity"]] = severity_counts.get(c["severity"], 0) + 1

    payload["last_cross_sweep_at"] = datetime.now(timezone.utc).isoformat()
    payload["cross_sweep_summary"] = {
        "rows_with_conflicts": rows_with_conflicts,
        "rows_total": len(rows),
        "severity_counts": severity_counts,
    }
    apath.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Cross-sweep complete. {rows_with_conflicts}/{len(rows)} rows have conflicts.")
    print(f"Severity counts: {severity_counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
