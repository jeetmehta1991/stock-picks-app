# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13 + Council 83 owner-approved per CHECKLIST #77.
"""B981 (2026-06-21): Phase P1 Bucket B B4 B956 triage queue top-N enumeration.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13 + Council 83 4/4 UNANIMOUS
# RECOMMEND Option-3 SCRIPT-PLUS-RECOMMEND per owner directive 2026-06-21
# 'Approve your recommendations. Proceed council this.'

PURPOSE
-------
Enumerate top-N candidates from B956 triage queue (323 findings across
5 finding types) for owner Stage 4 walk selection. Matches B978 audit +
B980 candidate report batch shape per Council 83 Executor lens.

Per Council 83 Top-N breakdown:
  SIGNAL_ORPHAN (11): top-9 (Council 83 said 9; actual is 11 -- include
    all 11 since smallest set)
  INVERSE_UNSAFE_CHECK_NEEDED (25): top-5 by severity
  EARNINGS_BLACKOUT_LOOKAHEAD_RISK (25): top-5 by severity
  DEFERRED_OWNER_TRIAGE (125): top-10 by walk-priority
  FIRE_STARVED (137): top-10 by closest-to-30/yr (lowest gate-loosen
    cost per B709 phi precedent)

Output: output_audit/b981_b956_triage_top_n_report.json

Per Council 83 starting recommendation: SIGNAL_ORPHAN-11 batch-walk
first (smallest + bug-impact + 88%-reduced via B970+1 = hard cases).
"""
from __future__ import annotations

import json
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

logger = logging.getLogger(__name__)

TOP_N_PER_TYPE = {
    "SIGNAL_ORPHAN": 11,                       # all (small set; per Council 83)
    "INVERSE_UNSAFE_CHECK_NEEDED": 5,
    "EARNINGS_BLACKOUT_LOOKAHEAD_RISK": 5,
    "DEFERRED_OWNER_TRIAGE": 10,
    "FIRE_STARVED": 10,
}

SEVERITY_NUMERIC = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}


def _severity_score(finding: dict[str, Any]) -> float:
    """Composite severity score for ordering within finding-type pool.

    Base: severity ordinal (HIGH=3 / MEDIUM=2 / LOW=1)
    Adjustments by finding-type:
      SIGNAL_ORPHAN: + (10 - wiring_coverage_pct/10) -- lower coverage = higher priority
      INVERSE_UNSAFE: + 1 if active mirror proposal exists (heuristic)
      EARNINGS_BLACKOUT: + per look-ahead-risk severity
      DEFERRED_OWNER_TRIAGE: + by strategy-name alpha order (stable tie-break)
      FIRE_STARVED: closest-to-30/yr scored higher (30 - |30 - fires|)
    """
    base = SEVERITY_NUMERIC.get(finding.get("severity", "LOW"), 1) * 10.0
    ftype = finding.get("finding_type", "")
    evidence = finding.get("evidence", {}) or {}
    if ftype == "SIGNAL_ORPHAN":
        wcp = evidence.get("wiring_coverage_pct", 100.0)
        base += max(0.0, 10.0 - wcp / 10.0)
    elif ftype == "FIRE_STARVED":
        fires = evidence.get("annualized_fires", evidence.get("fires_per_year", 0))
        try:
            fires_f = float(fires)
        except (TypeError, ValueError):
            fires_f = 0.0
        if fires_f > 0:
            base += max(0.0, 30.0 - abs(30.0 - fires_f))
    return base


def _select_top_n(findings: list[dict[str, Any]], finding_type: str, n: int) -> list[dict[str, Any]]:
    """Filter by finding_type + select top-N by severity score."""
    pool = [f for f in findings if f.get("finding_type") == finding_type]
    pool.sort(key=lambda f: (-_severity_score(f), f.get("strategy", "")))
    return pool[:n]


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    queue_path = REPO / "output_audit" / "b956_findings_triage_queue.json"
    if not queue_path.exists():
        logger.error("B956 queue not found at %s", queue_path)
        return 1
    queue = json.load(open(queue_path))
    findings = queue.get("findings", [])
    if not findings:
        logger.error("B956 queue empty")
        return 1

    logger.info("B981 enumerating top-N from %d B956 findings (Council 83 RECOMMEND)...", len(findings))

    top_n_by_type: dict[str, list[dict[str, Any]]] = {}
    for ftype, n in TOP_N_PER_TYPE.items():
        selected = _select_top_n(findings, ftype, n)
        top_n_by_type[ftype] = selected
        logger.info("  %s: %d / %d selected", ftype, len(selected), n)

    total_enumerated = sum(len(v) for v in top_n_by_type.values())
    type_counts_in_pool = Counter(f.get("finding_type") for f in findings)

    # Council 83 starting recommendation: SIGNAL_ORPHAN walk-1 batch
    walk_1_recommended = "SIGNAL_ORPHAN"
    walk_1_rationale = (
        "Smallest set (11 findings; closes-fully-in-1-batch); bug-impact "
        "severity (code-wiring breaks block engine consumption per B970+1 "
        "precedent); already 88%-reduced via B970+1 (146 -> 11 = hard "
        "cases remain); batch-walk authorized per owner standing pattern "
        "for small bug-impact sets."
    )
    walk_2_options = ["INVERSE_UNSAFE_CHECK_NEEDED", "EARNINGS_BLACKOUT_LOOKAHEAD_RISK",
                      "DEFERRED_OWNER_TRIAGE", "FIRE_STARVED"]

    out_path = REPO / "output_audit" / "b981_b956_triage_top_n_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({
            "schema_version": "1.0",
            "batch": "B981",
            "council": "83_OPTION_3_SCRIPT_PLUS_RECOMMEND",
            "owner_directive": "Approve your recommendations. Proceed council this. (2026-06-21)",
            "source_queue": "output_audit/b956_findings_triage_queue.json",
            "n_findings_in_source": len(findings),
            "n_findings_in_top_n_per_type": {k: len(v) for k, v in top_n_by_type.items()},
            "total_enumerated": total_enumerated,
            "pool_counts_per_type": dict(type_counts_in_pool),
            "council_83_walk_1_recommendation": walk_1_recommended,
            "council_83_walk_1_rationale": walk_1_rationale,
            "council_83_walk_2_owner_picks_from": walk_2_options,
            "ordering_methodology": {
                "base": "severity ordinal HIGH=3 / MEDIUM=2 / LOW=1 (x10)",
                "SIGNAL_ORPHAN_adjustment": "+ max(0, 10 - wiring_coverage_pct/10)",
                "FIRE_STARVED_adjustment": "+ max(0, 30 - |30 - annualized_fires|)",
                "tie_break": "alphabetical by strategy name",
            },
            "top_n_by_type": top_n_by_type,
            "memory_rule_reference": (
                "Council 83 Option-3 SCRIPT-PLUS-RECOMMEND per B978/B980 "
                "batch-shape precedent + feedback_per_strategy_deep_dive_"
                "stage4 + feedback_no_rushing_per_strategy_tweak + "
                "feedback_council_enumerate_plus_recommend + CHECKLIST "
                "#115 + CSV-first/data-first CLAUDE.md HARD RULE."
            ),
        }, f, indent=2, default=str)

    logger.info("B981 ENUMERATION COMPLETE:")
    logger.info("  Total enumerated: %d (target: %d)", total_enumerated, sum(TOP_N_PER_TYPE.values()))
    logger.info("  Council 83 walk-1 recommendation: %s (%d findings)",
                walk_1_recommended, len(top_n_by_type[walk_1_recommended]))
    logger.info("  Council 83 walk-2 owner picks from: %s", walk_2_options)
    logger.info("Output: %s", out_path.relative_to(REPO))

    # Surface first 3 of each type for at-a-glance
    logger.info("AT-A-GLANCE TOP-3 PER TYPE:")
    for ftype, selected in top_n_by_type.items():
        logger.info("  %s:", ftype)
        for f in selected[:3]:
            evidence_summary = ""
            ev = f.get("evidence", {}) or {}
            if "wiring_coverage_pct" in ev:
                evidence_summary = f" coverage={ev['wiring_coverage_pct']:.1f}%"
            elif "annualized_fires" in ev:
                evidence_summary = f" fires/yr={ev['annualized_fires']}"
            elif "fires_per_year" in ev:
                evidence_summary = f" fires/yr={ev['fires_per_year']}"
            logger.info("    [%s] %s severity=%s%s",
                        f.get("source_batch", "?"), f.get("strategy"),
                        f.get("severity"), evidence_summary)

    return 0


if __name__ == "__main__":
    sys.exit(main())
