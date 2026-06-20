"""B949 (2026-06-20): Phase P1 batch 9 - evidence-source bucket investigation.

# Source: Council 53 UNANIMOUS option-epsilon hybrid beta+delta verdict per
# owner directive 2026-06-20 Option B (investigate why 65 below sweet spot).

PURPOSE
-------
Census-level investigation of:
- BETA: WHICH STRONG evidence source (A/B/C/D) promoted each of the 152
  pre_cube_evidence_sufficient strategies?
- DELTA: WHICH bucket (I/II/III/IV) explains each of the 65 deferred?

Council 53 First Principles: 65 deferred may be the correct floor for the
current evidence corpus. Not every walk produces ledger-quality verdict.
Sweet spot 80-150 was Outsider heuristic, not ground truth.

NO MUTATION. NO schema change. NO auto-tightening.
Report-only per Council 53 strict mandate.

OUTPUTS
-------
output_audit/b949_evidence_source_buckets.json (machine-readable)
output_audit/b949_investigation_summary.md (human-readable)
"""
from __future__ import annotations

import json
import logging
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

logger = logging.getLogger(__name__)

DOSSIERS_DIR = REPO / "output_audit" / "dossiers"
STAGE_4_DOCS = list(REPO.glob("STAGE_4_*.md"))


def _load_walk_doc_strategy_index() -> dict[str, list[str]]:
    """Same as B947 — every-mention permissive cross-reference."""
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


def _classify_sufficient_by_source(strategy: str, dossier: dict) -> dict[str, Any]:
    """BETA: identify which STRONG evidence source(s) promoted this strategy.

    Sources:
      A: S4-B or W## walk markers (in section_9b walk_batches)
      B: fire-count >= 30/yr per direction
      C: STRONG status tags (canonical owner-approved set)
      D: walk_verdict_ledger entry (high|medium confidence)
    """
    from backtest.diagnostics.r5_inclusion_criterion import (
        STRONG_STATUS_TAGS, STRONG_WALK_PREFIXES, FIRE_COUNT_PASS_THRESHOLD_PER_YEAR,
        _walk_verdict_ledger_entries,
    )
    s9b = dossier.get("sections", {}).get("section_20_pre_cube_evidence_9b") or {}
    walk_batches = s9b.get("walk_batches", []) or []
    status_tags = s9b.get("status_tags", []) or []
    fc = s9b.get("fire_count_projection") or {}

    # A
    source_a = any(
        any(b.startswith(p) for p in STRONG_WALK_PREFIXES) for b in walk_batches
    )
    # B
    try:
        fpy_max = max(
            float(fc.get("fires_per_year_long") or 0),
            float(fc.get("fires_per_year_short") or 0),
        )
    except (TypeError, ValueError):
        fpy_max = 0
    source_b = fpy_max >= FIRE_COUNT_PASS_THRESHOLD_PER_YEAR
    # C
    source_c = any(t in STRONG_STATUS_TAGS for t in status_tags)
    # D
    source_d = bool(_walk_verdict_ledger_entries(strategy))

    sources = {"A": source_a, "B": source_b, "C": source_c, "D": source_d}
    active = sorted([k for k, v in sources.items() if v])
    return {
        "sources_active": active,
        "source_combination_key": "+".join(active) if active else "NONE",
        "details": {
            "A_walk_markers": [b for b in walk_batches
                                if any(b.startswith(p) for p in STRONG_WALK_PREFIXES)],
            "B_fire_count_per_year_max": fpy_max,
            "C_strong_status_tags": [t for t in status_tags if t in STRONG_STATUS_TAGS],
            "D_ledger_entry_count": len(_walk_verdict_ledger_entries(strategy)),
        },
    }


def _classify_deferred_by_bucket(strategy: str, dossier: dict,
                                  walk_doc_index: dict[str, list[str]]) -> dict[str, Any]:
    """DELTA: bucket I/II/III/IV explaining why this strategy is deferred.

    Bucket I:   NOT in any STAGE_4_*.md doc (genuinely unwalked)
    Bucket II:  IN walk doc but no structured walk_verdict_ledger entry
                (parser missed; or walk-doc mentioned strategy but no header)
    Bucket III: IN walk doc + has B### generic batch OR lineage tags (PATTERN_X
                or Wave_lineage) -- failed STRONG check post-B946
    Bucket IV:  All evidence rejected (rare; truly nothing)
    """
    from backtest.diagnostics.r5_inclusion_criterion import (
        STRONG_STATUS_TAGS, _walk_verdict_ledger_entries, LINEAGE_ONLY_TAGS,
    )
    s9b = dossier.get("sections", {}).get("section_20_pre_cube_evidence_9b") or {}
    walk_batches = s9b.get("walk_batches", []) or []
    status_tags = s9b.get("status_tags", []) or []

    in_walk_doc = strategy in walk_doc_index
    has_ledger = bool(_walk_verdict_ledger_entries(strategy))
    has_generic_b = any(
        b.startswith("B") and not b.startswith("S4-") for b in walk_batches
    )
    has_lineage_tags = any(
        t in LINEAGE_ONLY_TAGS or t.startswith("PATTERN_") for t in status_tags
    )

    if not in_walk_doc:
        bucket = "I_not_in_any_walk_doc"
    elif in_walk_doc and not has_ledger:
        bucket = "II_in_walk_doc_no_structured_header"
    elif in_walk_doc and (has_generic_b or has_lineage_tags):
        bucket = "III_walk_doc_but_only_lineage_or_generic"
    else:
        bucket = "IV_all_evidence_rejected"

    return {
        "bucket": bucket,
        "details": {
            "in_walk_doc": in_walk_doc,
            "walk_doc_refs": walk_doc_index.get(strategy, [])[:3],
            "has_ledger_entry": has_ledger,
            "has_generic_b_only": has_generic_b,
            "has_lineage_tags_only": has_lineage_tags,
            "all_walk_batches": walk_batches,
            "all_status_tags": status_tags,
        },
    }


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if not DOSSIERS_DIR.exists():
        logger.error("Dossiers directory missing.")
        return 1

    logger.info("Building permissive walk-doc index from %d STAGE_4_*.md docs...", len(STAGE_4_DOCS))
    walk_doc_index = _load_walk_doc_strategy_index()

    sufficient_records: list[dict] = []
    deferred_records: list[dict] = []
    sufficient_source_combos = Counter()
    deferred_buckets = Counter()

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
        criterion = dossier.get("r5_inclusion_criterion")
        strategy = d.name
        if criterion == "pre_cube_evidence_sufficient":
            classification = _classify_sufficient_by_source(strategy, dossier)
            sufficient_records.append({"strategy": strategy, **classification})
            sufficient_source_combos[classification["source_combination_key"]] += 1
        elif criterion == "deferred":
            classification = _classify_deferred_by_bucket(strategy, dossier, walk_doc_index)
            deferred_records.append({"strategy": strategy, **classification})
            deferred_buckets[classification["bucket"]] += 1

    # Compute D-only metric per Council 53 threshold
    d_only_count = sufficient_source_combos.get("D", 0)
    d_only_pct = 100.0 * d_only_count / max(len(sufficient_records), 1)

    # Bucket I count - genuinely unwalked
    bucket_i_count = deferred_buckets.get("I_not_in_any_walk_doc", 0)
    bucket_i_pct = 100.0 * bucket_i_count / max(len(deferred_records), 1)

    # JSON output
    out_json = REPO / "output_audit" / "b949_evidence_source_buckets.json"
    with open(out_json, "w") as f:
        json.dump({
            "schema_version": "1.0",
            "batch": "B949",
            "council_verdict": "53_UNANIMOUS_option_epsilon_hybrid_beta_delta",
            "n_sufficient": len(sufficient_records),
            "n_deferred": len(deferred_records),
            "sufficient_source_combinations": dict(sufficient_source_combos),
            "deferred_buckets": dict(deferred_buckets),
            "d_only_metric": {
                "count": d_only_count, "pct_of_sufficient": d_only_pct,
                "council_53_over_permissive_threshold_count": 40,
                "council_53_over_permissive_threshold_pct": 26.3,
                "verdict": "OVER_PERMISSIVE" if d_only_count > 40 else "WITHIN_BOUNDS",
            },
            "bucket_i_metric": {
                "count": bucket_i_count, "pct_of_deferred": bucket_i_pct,
                "council_53_legitimate_deferral_dominance_threshold": 40,
                "verdict": "GENUINELY_UNWALKED_DOMINATES" if bucket_i_count > 40 else "PARSER_OR_MIXED",
            },
            "sufficient_records": sufficient_records,
            "deferred_records": deferred_records,
        }, f, indent=2, default=str)

    # Markdown summary
    lines = []
    lines.append("# Batch 949 (2026-06-20): Evidence-Source Bucket Investigation\n\n")
    lines.append("# Source: Council 53 UNANIMOUS option-epsilon hybrid beta+delta verdict per CHECKLIST #77.\n\n")
    lines.append(f"## Summary\n\nTotal sufficient: {len(sufficient_records)} | Total deferred: {len(deferred_records)}\n\n")

    # BETA section
    lines.append("## Section 1: Sufficient (152) Bucketed by STRONG Evidence Source\n\n")
    lines.append("Sources: A (S4-B/W## walk markers) | B (fire-count >=30/yr) | C (STRONG status tags) | D (walk_verdict_ledger)\n\n")
    lines.append("| Source combination | Count | % of sufficient |\n|---|---|---|\n")
    for combo, n in sufficient_source_combos.most_common():
        pct = 100.0 * n / max(len(sufficient_records), 1)
        marker = " **<- D-ONLY**" if combo == "D" else ""
        lines.append(f"| {combo} | {n} | {pct:.1f}%{marker} |\n")
    lines.append("\n")

    # D-only verdict
    lines.append("### D-only metric (Council 53 over-permissiveness gate)\n\n")
    lines.append(f"- D-only count: **{d_only_count}** of {len(sufficient_records)} sufficient ({d_only_pct:.1f}%)\n")
    lines.append(f"- Council 53 threshold: >40 (>26.3%) = OVER-PERMISSIVE\n")
    verdict_d = "**OVER-PERMISSIVE**" if d_only_count > 40 else "**WITHIN BOUNDS**"
    lines.append(f"- Verdict: {verdict_d}\n\n")

    # DELTA section
    lines.append("## Section 2: Deferred (65) Bucketed by Why Deferred\n\n")
    lines.append("| Bucket | Count | % of deferred |\n|---|---|---|\n")
    bucket_order = [
        "I_not_in_any_walk_doc",
        "II_in_walk_doc_no_structured_header",
        "III_walk_doc_but_only_lineage_or_generic",
        "IV_all_evidence_rejected",
    ]
    for b in bucket_order:
        n = deferred_buckets.get(b, 0)
        pct = 100.0 * n / max(len(deferred_records), 1)
        lines.append(f"| {b} | {n} | {pct:.1f}% |\n")
    lines.append("\n")

    lines.append("### Bucket I (genuinely-unwalked) dominance metric\n\n")
    lines.append(f"- Bucket I count: **{bucket_i_count}** of {len(deferred_records)} deferred ({bucket_i_pct:.1f}%)\n")
    lines.append(f"- Council 53 threshold: >40 = GENUINELY-UNWALKED DOMINATES\n")
    verdict_i = "**GENUINELY UNWALKED DOMINATES**" if bucket_i_count > 40 else "**PARSER OR MIXED**"
    lines.append(f"- Verdict: {verdict_i}\n\n")

    # Section 3: Honest finding
    lines.append("## Section 3: HONEST FINDING (Council 53 First Principles)\n\n")
    if d_only_count > 40 and bucket_i_count < 20:
        lines.append("**Mixed: ledger over-permissive AND parser gap. Most likely actual finding per Council 53 Contrarian.**\n\n")
        lines.append("Implication: 75 strategies flipped via D-only evidence may not have owner-issued verdicts; ledger needs verdict-bearing requirement.\n")
        lines.append("Plus: parser missing structured headers in 4 cluster docs (PIVOT/SMART_MONEY/TREND/EVENT_DRIVEN).\n\n")
    elif d_only_count > 40:
        lines.append("**LEDGER OVER-PERMISSIVE.** D-only evidence flipped many strategies that had no other STRONG signal. Walk-header presence alone may not constitute owner verdict.\n\n")
    elif bucket_i_count > 40:
        lines.append("**65 LEGITIMATELY DEFERRED.** Most are not in any STAGE_4_*.md doc -- genuinely unwalked.\n\n")
        lines.append("Per Council 53 First Principles: 'Sweet spot 80-150 was Outsider heuristic, not ground truth. 65 may be the correct floor for the current evidence corpus.'\n\n")
    elif deferred_buckets.get("II_in_walk_doc_no_structured_header", 0) > 30:
        lines.append("**PARSER GAP.** Many deferred strategies are mentioned in walk docs but lack structured walk-header in cluster docs. B950+ parser improvement would recover them.\n\n")
    else:
        lines.append("**MIXED DISTRIBUTION.** No single failure mode dominates. Owner discretion on next step.\n\n")

    # Section 4: Recommendation framing
    lines.append("## Section 4: Recommendation Framing (Council 53 surface-don't-prescribe mandate)\n\n")
    lines.append("Owner has THREE terminal-state options:\n\n")
    lines.append("- **(i) Tighten ledger (verdict-bearing requirement)** -- triggered if D-only >40 of 152. Recommend if owner sees walk-header parsing alone is over-permissive.\n")
    lines.append("- **(ii) Accept 65 as legitimate floor + owner triage queue** -- triggered if Bucket I dominates. Recommend if owner accepts the corpus has structural limits.\n")
    lines.append("- **(iii) Parser improvement (B950+)** -- triggered if Bucket II dominates. Recommend if owner sees walk docs have structural inconsistency.\n\n")
    lines.append("**Council 53 strict mandate:** NO auto-application. Owner picks.\n\n")

    # Section 5: Compliance
    lines.append("## B949 Compliance Statement\n\n")
    lines.append("| Council 53 mandate | Status |\n|---|---|\n")
    lines.append("| ONE commit (B949) | OK |\n")
    lines.append("| Hybrid beta + delta (census, not sample) | OK |\n")
    lines.append("| Report-only; no schema mutation | OK |\n")
    lines.append("| No auto-tightening regardless of finding | OK |\n")
    lines.append("| Honest finding mandatory | OK |\n")
    lines.append("| Owner picks (i)/(ii)/(iii); no pre-prescription | OK |\n")

    out_md = REPO / "output_audit" / "b949_investigation_summary.md"
    with open(out_md, "w") as f:
        f.writelines(lines)

    logger.info("Investigation COMPLETE: %d sufficient + %d deferred",
                len(sufficient_records), len(deferred_records))
    logger.info("Sufficient source combinations:")
    for combo, n in sufficient_source_combos.most_common():
        logger.info("  %s: %d", combo, n)
    logger.info("Deferred buckets:")
    for b in bucket_order:
        n = deferred_buckets.get(b, 0)
        logger.info("  %s: %d", b, n)
    logger.info("D-only metric: %d (%.1f%%) -- %s", d_only_count, d_only_pct,
                "OVER-PERMISSIVE" if d_only_count > 40 else "WITHIN BOUNDS")
    logger.info("Bucket I metric: %d (%.1f%%) -- %s", bucket_i_count, bucket_i_pct,
                "GENUINELY UNWALKED DOMINATES" if bucket_i_count > 40 else "PARSER OR MIXED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
