"""B950 PRE-BUILD AUDIT (2026-06-20): scan 75 D-only entries for verdict keywords.

# Source: Council 54 UNANIMOUS option-epsilon mandate per CHECKLIST #77 +
# Contrarian counter-pressure: 'scan 75 D-only entries for verdict keywords
# FIRST. If <20 have explicit verdicts, the ledger format itself lacks verdict
# capture - fix ledger schema upstream. If >50 have verdicts, (B) is safe.'

PURPOSE
-------
Verify (B) verdict-bearing requirement WON'T accidentally drop legitimate walks.
If >50 of 75 D-only entries have keyword evidence in cluster docs, ship (B).
If <20 have evidence, ABORT (B); skip to (A) parser-only path.
20-50 range: ship instrumented per Council 54 ship-conditional.
"""
from __future__ import annotations

import json
import logging
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

logger = logging.getLogger(__name__)

STRONG_KEYWORDS = ("SHIPPED", "DELETED", "VERIFIED", "DELETE candidate")
MEDIUM_KEYWORDS = ("RECOMMENDED", "loosen", "tighten", "swap", "kept", "keep")
ALL_KEYWORDS = STRONG_KEYWORDS + MEDIUM_KEYWORDS


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    b949_path = REPO / "output_audit" / "b949_evidence_source_buckets.json"
    with open(b949_path) as f:
        b949 = json.load(f)
    d_only_strategies = [
        r["strategy"] for r in b949["sufficient_records"]
        if r["source_combination_key"] == "D"
    ]
    logger.info("D-only strategies to audit: %d", len(d_only_strategies))

    # Load all STAGE_4_*.md content into memory once
    docs = list(REPO.glob("STAGE_4_*.md"))
    doc_text = {d.name: d.read_text(encoding="utf-8", errors="ignore") for d in docs}

    # For each D-only strategy, check keyword presence in any doc that mentions it
    audit_results = []
    strong_count = 0
    medium_count = 0
    none_count = 0
    for strat in d_only_strategies:
        # Find docs mentioning this strategy
        mentioning_docs = [name for name, txt in doc_text.items()
                            if (strat in txt or f"strat_{strat}" in txt)]
        # For each mentioning doc, find context around the strategy mention
        # and scan for verdict keywords within +/- 800 chars
        strong_hits = set()
        medium_hits = set()
        for doc_name in mentioning_docs:
            txt = doc_text[doc_name]
            for needle in (strat, f"strat_{strat}"):
                for m in re.finditer(re.escape(needle), txt):
                    window_start = max(0, m.start() - 400)
                    window_end = min(len(txt), m.end() + 400)
                    window = txt[window_start:window_end]
                    for kw in STRONG_KEYWORDS:
                        if kw in window:
                            strong_hits.add(kw)
                    for kw in MEDIUM_KEYWORDS:
                        if kw in window.lower() if kw.islower() else kw in window:
                            medium_hits.add(kw)
        has_strong = bool(strong_hits)
        has_2_medium = len(medium_hits) >= 2
        has_evidence = has_strong or has_2_medium
        if has_strong:
            strong_count += 1
        elif has_2_medium:
            medium_count += 1
        else:
            none_count += 1
        audit_results.append({
            "strategy": strat,
            "mentioning_docs_count": len(mentioning_docs),
            "strong_keywords_found": sorted(strong_hits),
            "medium_keywords_found": sorted(medium_hits),
            "has_evidence_for_b": has_evidence,
        })

    with_evidence = strong_count + medium_count
    pct_with_evidence = 100.0 * with_evidence / max(len(d_only_strategies), 1)

    # Council 54 thresholds
    if with_evidence < 20:
        verdict = "ABORT_B"
    elif with_evidence > 50:
        verdict = "SAFE_TO_SHIP_B"
    else:
        verdict = "SHIP_INSTRUMENTED"

    out_path = REPO / "output_audit" / "b950_pre_build_audit_d_only.json"
    with open(out_path, "w") as f:
        json.dump({
            "schema_version": "1.0",
            "batch": "B950_pre_build",
            "council_verdict": "54_UNANIMOUS_option_epsilon",
            "n_d_only_strategies": len(d_only_strategies),
            "n_with_strong_keyword": strong_count,
            "n_with_2_medium_keywords": medium_count,
            "n_no_evidence": none_count,
            "n_with_evidence_total": with_evidence,
            "pct_with_evidence": pct_with_evidence,
            "council_54_abort_threshold_lt": 20,
            "council_54_safe_threshold_gt": 50,
            "verdict": verdict,
            "audit_results": audit_results,
        }, f, indent=2, default=str)

    logger.info("AUDIT COMPLETE:")
    logger.info("  N strong-keyword: %d", strong_count)
    logger.info("  N >=2-medium-keyword: %d", medium_count)
    logger.info("  N no evidence: %d", none_count)
    logger.info("  Total with evidence: %d (%.1f%%)", with_evidence, pct_with_evidence)
    logger.info("  COUNCIL 54 VERDICT: %s", verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
