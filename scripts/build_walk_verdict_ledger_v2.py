"""B950 (2026-06-20): Phase P1 batch 10 - extended walk-verdict ledger v2.

# Source: Council 54 UNANIMOUS option-epsilon verdict per owner directive
# 2026-06-20 (i)+(iii) combined ledger refinement.

PURPOSE
-------
Extend B948 walk_verdict_ledger.json with:

(A) PARSER COVERAGE (iii):
    A.1: Section-header pattern allows OPTIONAL hyphen between letter+number
         (catches `### T1.` TREND format alongside existing `### BR-1.`)
    A.2: NEW table-row pattern for cluster docs lacking section headers
         (catches PIVOT + SMART_MONEY)

(B) VERDICT-BEARING REQUIREMENT (i):
    B.1: Scan walk-section body (post-header until next header) for keywords
    B.2: Classify keywords as strong / medium per Council 54 First Principles
    B.3: Add 'verdict_strength' field: 'strong' | 'medium' | 'walked_only'

Output schema (extended):
{
  "strategy": str, "cluster_id": str, "batch_refs": [], "walk_positions": [],
  "context": str, "verdict": "walked",
  "confidence": "high",
  "verdict_strength": "strong" | "medium" | "walked_only",
  "verdict_keywords_strong": [], "verdict_keywords_medium": [],
  "source": str,
  "source_method": "section_header_hyphen" | "section_header_no_hyphen" | "table_row",
}

NO mutation of B948 ledger; produces v2 alongside.
"""
from __future__ import annotations

import json
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

logger = logging.getLogger(__name__)

STAGE_4_DOCS_GLOB = "STAGE_4_*CLUSTER_WALKS.md"

# A.1: Section header pattern WITH OPTIONAL hyphen (extends B948)
WALK_HEADER_PATTERN_V2 = re.compile(
    r"^###\s+(?P<cluster_id>[A-Z]+-?\d+[a-z]?)\.\s+`(?P<strategy>strat_[a-zA-Z0-9_]+)`(?:\s*\((?P<context>[^)]*)\))?",
    re.MULTILINE,
)

# A.2: Table-row pattern (NEW); handles BOTH formats:
#   PIVOT  format: `| **P5** | W10 \`camarilla_r3_breakout\` | ...`  (strategy
#                  in next cell after ID; NO strat_ prefix on strategy name)
#   SMART  format: `| **SM-4** \`strat_ma_target_long\` | ...`        (strategy
#                  in SAME cell as ID; WITH strat_ prefix on strategy name)
TABLE_ROW_PATTERN = re.compile(
    r"^\|\s*\*\*(?P<cluster_id>[A-Z]+-?\d+[a-z]?)\*\*[^`\n]*?`(?P<strategy>(?:strat_)?[a-z][a-z0-9_]+)`",
    re.MULTILINE,
)
# After table-row regex match, validate strategy against ALL_STRATEGIES set
# to avoid false positives from generic backticked words in body text.

# Verdict keyword vocabulary per Council 54
STRONG_KEYWORDS = ("SHIPPED", "DELETED", "VERIFIED", "DELETE candidate")
MEDIUM_KEYWORDS = ("RECOMMENDED", "loosen", "tighten", "swap", "kept", "keep")

# Batch ref patterns (same as B948)
BATCH_REFS_PATTERN = re.compile(r"\bB(?:atch\s+)?(\d{3,4})\b")
S4B_REFS_PATTERN = re.compile(r"\bS4-B(\d{3,4})\b")
W_REFS_PATTERN = re.compile(r"\bW(\d{1,2})\b")


def _scan_walk_section_body(doc_text: str, header_match_end: int) -> tuple[list[str], list[str]]:
    """B Scan walk-section body (post-header until next '### ' or '\\| \\*\\*[A-Z]') for keywords."""
    next_header = re.search(r"\n###\s+|\n\|\s*\*\*[A-Z]", doc_text[header_match_end:])
    if next_header:
        body = doc_text[header_match_end:header_match_end + next_header.start()]
    else:
        body = doc_text[header_match_end:header_match_end + 5000]
    strong = []
    medium = []
    for kw in STRONG_KEYWORDS:
        if kw in body:
            strong.append(kw)
    for kw in MEDIUM_KEYWORDS:
        target = body.lower() if kw.islower() else body
        if kw in target:
            medium.append(kw)
    return sorted(set(strong)), sorted(set(medium))


def _classify_verdict_strength(strong: list[str], medium: list[str]) -> str:
    """Council 54 First Principles: >=1 strong OR >=2 medium = STRONG; else medium/walked."""
    if strong:
        return "strong"
    if len(medium) >= 2:
        return "medium"
    return "walked_only"


def _extract_batch_refs(context: str) -> tuple[list[str], list[str]]:
    batch_refs = set()
    for bm in BATCH_REFS_PATTERN.finditer(context):
        batch_refs.add(f"B{bm.group(1)}")
    for s4 in S4B_REFS_PATTERN.finditer(context):
        batch_refs.add(f"S4-B{s4.group(1)}")
    walk_positions = set()
    for w in W_REFS_PATTERN.finditer(context):
        walk_positions.add(f"W{w.group(1)}")
    return sorted(batch_refs), sorted(walk_positions)


def parse_walk_doc_v2(doc_path: Path) -> list[dict[str, Any]]:
    """Extract walk entries via BOTH section-header AND table-row patterns."""
    if not doc_path.exists():
        return []
    text = doc_path.read_text(encoding="utf-8", errors="ignore")
    entries = []
    seen_strategies_in_doc = set()

    # A.1: Section-header pattern
    for m in WALK_HEADER_PATTERN_V2.finditer(text):
        strategy = m.group("strategy")
        strategy_key = strategy[len("strat_"):] if strategy.startswith("strat_") else strategy
        cluster_id = m.group("cluster_id")
        context = (m.group("context") or "").strip()
        batch_refs, walk_positions = _extract_batch_refs(context)
        strong_kw, medium_kw = _scan_walk_section_body(text, m.end())
        verdict_strength = _classify_verdict_strength(strong_kw, medium_kw)
        source_method = "section_header_hyphen" if "-" in cluster_id else "section_header_no_hyphen"
        entries.append({
            "strategy": strategy_key,
            "cluster_id": cluster_id,
            "batch_refs": batch_refs,
            "walk_positions": walk_positions,
            "context": context,
            "verdict": "walked",
            "confidence": "high",
            "verdict_strength": verdict_strength,
            "verdict_keywords_strong": strong_kw,
            "verdict_keywords_medium": medium_kw,
            "source": doc_path.name,
            "source_method": source_method,
        })
        seen_strategies_in_doc.add(strategy_key)

    # A.2: Table-row pattern (dedup against section-header + validate against ALL_STRATEGIES)
    from backtest.signals.screener import ALL_STRATEGIES
    all_strategy_names = set(ALL_STRATEGIES.keys())
    for m in TABLE_ROW_PATTERN.finditer(text):
        strategy = m.group("strategy")
        strategy_key = strategy[len("strat_"):] if strategy.startswith("strat_") else strategy
        # Validate against canonical roster to reject false-positive backticked words
        if strategy_key not in all_strategy_names:
            continue
        if strategy_key in seen_strategies_in_doc:
            continue
        cluster_id = m.group("cluster_id")
        strong_kw, medium_kw = _scan_walk_section_body(text, m.end())
        verdict_strength = _classify_verdict_strength(strong_kw, medium_kw)
        entries.append({
            "strategy": strategy_key,
            "cluster_id": cluster_id,
            "batch_refs": [],
            "walk_positions": [],
            "context": "",
            "verdict": "walked",
            "confidence": "high",
            "verdict_strength": verdict_strength,
            "verdict_keywords_strong": strong_kw,
            "verdict_keywords_medium": medium_kw,
            "source": doc_path.name,
            "source_method": "table_row",
        })
        seen_strategies_in_doc.add(strategy_key)

    return entries


def build_ledger_v2() -> dict[str, Any]:
    docs = sorted(REPO.glob(STAGE_4_DOCS_GLOB))
    logger.info("Parsing %d STAGE_4_*CLUSTER_WALKS.md docs (v2)...", len(docs))
    ledger: dict[str, list[dict]] = defaultdict(list)
    for d in docs:
        entries = parse_walk_doc_v2(d)
        for entry in entries:
            ledger[entry["strategy"]].append(entry)
        n_section = sum(1 for e in entries if "section_header" in e["source_method"])
        n_table = sum(1 for e in entries if e["source_method"] == "table_row")
        logger.info("  %s: %d (%d section + %d table)", d.name, len(entries), n_section, n_table)
    return dict(ledger)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ledger = build_ledger_v2()
    out_path = REPO / "output_audit" / "walk_verdict_ledger_v2.json"

    # Summary stats
    n_strong = sum(1 for sl in ledger.values() if any(e["verdict_strength"] == "strong" for e in sl))
    n_medium = sum(1 for sl in ledger.values() if any(e["verdict_strength"] == "medium" for e in sl)
                   and not any(e["verdict_strength"] == "strong" for e in sl))
    n_walked_only = len(ledger) - n_strong - n_medium

    with open(out_path, "w") as f:
        json.dump({
            "schema_version": "2.0",
            "batch": "B950",
            "construction_per_council": "54",
            "n_strategies_with_walks": len(ledger),
            "n_with_strong_verdict_strength": n_strong,
            "n_with_medium_verdict_strength_only": n_medium,
            "n_walked_only": n_walked_only,
            "ledger": ledger,
        }, f, indent=2, default=str)
    logger.info("Ledger v2 COMPLETE: %d strategies", len(ledger))
    logger.info("  strong verdict-strength: %d", n_strong)
    logger.info("  medium verdict-strength: %d", n_medium)
    logger.info("  walked-only: %d", n_walked_only)
    logger.info("Output: %s", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
