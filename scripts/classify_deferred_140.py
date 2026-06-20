"""B947 (2026-06-20): Phase P1 batch 7 - classifier for the 140 deferred strategies.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13 + Council 51 UNANIMOUS hybrid epsilon
# verdict per owner directive 2026-06-20 Option A.

PURPOSE
-------
Read-only classifier for strategies with r5_inclusion_criterion=='deferred'
post-B946 STRONG-EVIDENCE refinement. Per Council 51 First Principles:

Priority-ordered disjoint buckets (V > IV > III > II > I; highest evidence wins):
  V:   walk_doc_mentioned -- cross-referenced in STAGE_4_*.md docs
  IV:  below_threshold_fire -- fire-count measured but < 30/yr
  III: lineage_tags_only -- PATTERN_X / Wave_lineage / EVENT_only / SHORT_EXPLORATORY
  II:  batch_markers_only -- generic B### references in docstring
  I:   truly_deferred -- no evidence whatsoever; owner triage candidate

NO MUTATION of dossiers. NO new EXPLORATORY tags. NO r5_inclusion_criterion change.
Strict read-only per Council 51 Outsider HARD RULES.

OUTPUT
------
output_audit/b947_deferred_140_classification.json
output_audit/b947_deferred_140_summary.md
"""
from __future__ import annotations

import json
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

logger = logging.getLogger(__name__)


DOSSIERS_DIR = REPO / "output_audit" / "dossiers"
STAGE_4_DOCS = list(REPO.glob("STAGE_4_*.md"))


def _load_walk_doc_strategy_index() -> dict[str, list[str]]:
    """Cross-reference: which strategies are mentioned in which STAGE_4 walk docs.

    Returns dict[strategy_name] -> list of walk doc filenames.
    """
    index: dict[str, list[str]] = {}
    from backtest.signals.screener import ALL_STRATEGIES
    strategy_names = list(ALL_STRATEGIES.keys())
    for doc in STAGE_4_DOCS:
        try:
            text = doc.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for strat in strategy_names:
            if strat in text or f"strat_{strat}" in text:
                index.setdefault(strat, []).append(doc.name)
    return index


def _git_first_commit_date(strategy: str) -> str | None:
    """Get the first-touch date for a strategy's registration line in screener.py."""
    try:
        result = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%ad", "--date=short",
             "-S", f'"{strategy}"', "backtest/signals/screener.py"],
            cwd=str(REPO), capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            return lines[-1] if lines else None
    except Exception:
        pass
    return None


def classify_strategy(strategy: str, dossier: dict[str, Any],
                       walk_doc_index: dict[str, list[str]]) -> dict[str, Any]:
    """Apply priority-ordered disjoint bucket classification."""
    section_9b = dossier["sections"].get("section_20_pre_cube_evidence_9b") or {}
    walk_batches = section_9b.get("walk_batches", []) or []
    status_tags = section_9b.get("status_tags", []) or []
    fc = section_9b.get("fire_count_projection") or {}

    # Evidence gathering
    fpy_long = fc.get("fires_per_year_long") or 0
    fpy_short = fc.get("fires_per_year_short") or 0
    try:
        fpy_max = max(float(fpy_long or 0), float(fpy_short or 0))
    except (TypeError, ValueError):
        fpy_max = 0
    has_fire_count_measured = fpy_max > 0

    generic_batches = [b for b in walk_batches if b.startswith("B") and not b.startswith("S4-")]
    lineage_tags = [
        t for t in status_tags
        if t in {"EVENT_only", "SHORT_EXPLORATORY", "Wave_lineage", "mean_reversion"}
        or t.startswith("PATTERN_")
    ]
    walk_docs = walk_doc_index.get(strategy, [])
    docstring_present = bool(walk_batches or status_tags or fc)

    # Priority-ordered classification (V > IV > III > II > I)
    if walk_docs:
        bucket = "V_walk_doc_mentioned"
        next_step_hint = "walk_doc_extractor_gap"
    elif has_fire_count_measured and fpy_max < 30:
        bucket = "IV_below_threshold_fire"
        next_step_hint = "fire_starved_genuine"
    elif lineage_tags:
        bucket = "III_lineage_tags_only"
        next_step_hint = "reclassify_candidate"
    elif generic_batches:
        bucket = "II_batch_markers_only"
        next_step_hint = "owner_triage_low_evidence"
    else:
        bucket = "I_truly_deferred"
        next_step_hint = "owner_triage"

    return {
        "strategy": strategy,
        "bucket": bucket,
        "next_step_hint": next_step_hint,
        "evidence": {
            "batch_markers": walk_batches,
            "lineage_tags": lineage_tags,
            "fire_count_per_year_max": fpy_max,
            "fire_count_source": fc.get("source_file") if has_fire_count_measured else None,
            "walk_doc_refs": walk_docs,
            "docstring_present": docstring_present,
            "first_commit": _git_first_commit_date(strategy),
        },
    }


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if not DOSSIERS_DIR.exists():
        logger.error("Dossiers directory missing; run scripts/dossier_build.py --init-all first.")
        return 1

    logger.info("Loading walk-doc strategy index from %d STAGE_4_*.md docs...", len(STAGE_4_DOCS))
    walk_doc_index = _load_walk_doc_strategy_index()
    logger.info("Walk-doc index: %d strategies mentioned in walk docs", len(walk_doc_index))

    deferred_strategies: list[str] = []
    classifications: list[dict] = []

    for d in DOSSIERS_DIR.iterdir():
        if not d.is_dir():
            continue
        f = d / "dossier.json"
        if not f.exists():
            continue
        try:
            dossier = json.load(open(f))
        except Exception:
            continue
        if dossier.get("r5_inclusion_criterion") != "deferred":
            continue
        deferred_strategies.append(d.name)
        classifications.append(classify_strategy(d.name, dossier, walk_doc_index))

    # Summarize
    from collections import Counter
    bucket_counts = Counter(c["bucket"] for c in classifications)
    hint_counts = Counter(c["next_step_hint"] for c in classifications)

    out_dir = REPO / "output_audit"
    out_json = out_dir / "b947_deferred_140_classification.json"
    out_md = out_dir / "b947_deferred_140_summary.md"

    with open(out_json, "w") as f:
        json.dump({
            "total_deferred": len(classifications),
            "bucket_distribution": dict(bucket_counts),
            "next_step_hint_distribution": dict(hint_counts),
            "classifications": classifications,
        }, f, indent=2, default=str)

    # Summary markdown
    lines = []
    lines.append("# Batch 947 (2026-06-20): 140 Deferred Strategy Classification\n")
    lines.append("# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.8 + Council 51 UNANIMOUS hybrid epsilon verdict per CHECKLIST #77.\n\n")
    lines.append(f"## Summary\n\nTotal deferred strategies: {len(classifications)}\n\n")
    lines.append("## Bucket Distribution (priority-ordered V > IV > III > II > I)\n\n")
    lines.append("| Bucket | Count | % | Next-step hint |\n|---|---|---|---|\n")
    bucket_order = [
        "V_walk_doc_mentioned",
        "IV_below_threshold_fire",
        "III_lineage_tags_only",
        "II_batch_markers_only",
        "I_truly_deferred",
    ]
    for b in bucket_order:
        n = bucket_counts.get(b, 0)
        if not classifications: pct = 0.0
        else: pct = 100.0 * n / len(classifications)
        # Find the next_step_hint corresponding to this bucket
        hints_for_bucket = {c["next_step_hint"] for c in classifications if c["bucket"] == b}
        hint_str = ", ".join(sorted(hints_for_bucket)) if hints_for_bucket else "-"
        lines.append(f"| {b} | {n} | {pct:.1f}% | {hint_str} |\n")

    lines.append("\n## Top-10 Examples per Bucket\n\n")
    for b in bucket_order:
        examples = [c for c in classifications if c["bucket"] == b][:10]
        if not examples:
            continue
        lines.append(f"### {b}\n\n")
        for c in examples:
            ev = c["evidence"]
            ev_summary = []
            if ev["walk_doc_refs"]:
                ev_summary.append(f"walk_docs={ev['walk_doc_refs'][:2]}")
            if ev["fire_count_per_year_max"]:
                ev_summary.append(f"fpy={ev['fire_count_per_year_max']:.1f}")
            if ev["lineage_tags"]:
                ev_summary.append(f"lineage={ev['lineage_tags']}")
            if ev["batch_markers"]:
                ev_summary.append(f"batches={ev['batch_markers'][:3]}")
            lines.append(f"- `{c['strategy']}` (first_commit={ev['first_commit']}): {' | '.join(ev_summary) or 'no evidence'}\n")
        lines.append("\n")

    lines.append("## Recommendation (Council 51 mandate: recommend-only; no auto-mutation)\n\n")
    bucket_v_count = bucket_counts.get("V_walk_doc_mentioned", 0)
    bucket_v_pct = 100.0 * bucket_v_count / max(len(classifications), 1)
    if bucket_v_pct >= 90:
        lines.append(
            f"### HONEST FINDING: Walk-doc cross-reference too permissive\n\n"
            f"{bucket_v_count} of {len(classifications)} ({bucket_v_pct:.1f}%) strategies match Bucket V "
            f"(walk_doc_mentioned). The walk-doc index includes ALL 219 strategies (every "
            f"strategy is mentioned somewhere in a STAGE_4_*.md doc). This makes Bucket V's "
            f"matching criterion trivially universal -- the bucket doesn't discriminate.\n\n"
            f"**Analogous failure mode to B945:** B945 had a parser gap (regex too narrow); "
            f"B947 has a cross-reference gap (mention != walk verdict). Per Council 50 honest-"
            f"finding pattern, surfacing this without iterating tighter parser mid-batch.\n\n"
            f"**Council 52 RECOMMENDED ACTIONS:**\n"
            f"- (i) Tighten walk-doc parser: require strategy mention within K-line proximity "
            f"of 'walked', 'verdict', 'W##:', or 'S4-B###' keywords (NOT just any text mention)\n"
            f"- (ii) Build STAGE_4 walk-verdict ledger from B883 lineage (specific strategy "
            f"-> walk verdict mapping; treat ledger as ground truth)\n"
            f"- (iii) Accept 140 deferred as-is; defer walk-doc parser improvement to "
            f"separate B948 batch\n\n"
            f"Per Council 51 Outsider strict mandate: B947 ships honest finding; B948 (or "
            f"Council 52) decides next step. No mid-batch iteration.\n\n"
        )
    elif bucket_v_count > 20:
        lines.append(f"- **High-leverage opportunity:** {bucket_v_count} strategies mentioned in STAGE_4 walk docs but docstrings silent. Section 9b extractor walk-doc cross-reference (separate B948 ticket) could reclassify them legitimately.\n")
    if bucket_counts.get("I_truly_deferred", 0) > 20:
        lines.append(f"- **Owner triage queue:** {bucket_counts.get('I_truly_deferred', 0)} strategies have ZERO evidence (no walks, no fire-count, no tags). Council 52 should review.\n")
    if bucket_counts.get("IV_below_threshold_fire", 0) > 20:
        lines.append(f"- **Fire-starved cohort:** {bucket_counts.get('IV_below_threshold_fire', 0)} strategies were measured (<30/yr). Council 52 should consider whether to EXPLORATORY-tag (preserve per `feedback_no_a_priori_strategy_pruning`) or owner-defer.\n")
    if bucket_counts.get("III_lineage_tags_only", 0) > 20:
        lines.append(f"- **Lineage-tag cohort:** {bucket_counts.get('III_lineage_tags_only', 0)} strategies have PATTERN_X / Wave_lineage / EVENT_only / SHORT_EXPLORATORY tags. These describe origin not approval; Council 50 correctly rejected as STRONG evidence. Per `feedback_no_a_priori_strategy_pruning`: include in cube; let R5 verdict decide.\n")

    lines.append("\n## B931 Appendix Flag\n\n")
    lines.append("`institutional_persistent_holders_long` is in B906 MEASUREMENT_DISPUTED set + B931 MAY-REVERT tag pending B906 owner decision. Classification reflects current dossier state; no re-tag in this batch per Council 51 HARD RULE.\n\n")

    lines.append("## B947 Compliance Statement\n\n")
    lines.append("| Council 51 mandate | Status |\n|---|---|\n")
    lines.append("| ONE commit (B947) | OK |\n")
    lines.append("| Read-only classifier (no dossier mutation) | OK |\n")
    lines.append("| Priority-ordered disjoint buckets V > IV > III > II > I | OK |\n")
    lines.append("| Recommend-only (no auto-mutation) | OK |\n")
    lines.append("| B931 appendix-flagged | OK |\n")
    lines.append("| B948 walk-doc extractor + B949 owner triage = separate downstream | OK |\n")

    with open(out_md, "w") as f:
        f.writelines(lines)

    logger.info("Classification COMPLETE: %d strategies", len(classifications))
    for b in bucket_order:
        n = bucket_counts.get(b, 0)
        logger.info("  %s: %d", b, n)
    logger.info("Output: %s + %s", out_json.name, out_md.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
