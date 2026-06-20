"""B948 (2026-06-20): Phase P1 batch 8 - STAGE_4 walk-verdict ledger builder.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13 + B883 lineage Council 10 verdict
# + Council 52 UNANIMOUS option-epsilon verdict per owner directive 2026-06-20
# Option B.

PURPOSE
-------
Build ground-truth ledger of strategy -> Stage 4 walk verdicts from
STAGE_4_*.md cluster walk docs. Replaces B947's permissive
"mentioned-in-doc" cross-reference with structured walk-header parsing.

Per Council 52 consensus:
- Option epsilon: minimal viable; lenient match + strict confidence
- Schema: strategy -> list of {batch, walk_position, verdict, confidence, source}
- Vocabulary: keep / loosen / tighten / swap / delete / Class7_NEW / EXPLORATORY / MAY_REVERT
- Sparse coverage acceptable
- Single commit; integrate into Section 9b _has_strong_evidence

PARSING STRATEGY
----------------
1. Per-strategy walk headers (HIGH confidence):
   Pattern: ^### \\w+-\\d+\\. `strat_NAME` (Batch ###...walked B###)
   Source: STAGE_4_BREAKOUT_CLUSTER_WALKS.md + similar structured cluster docs
   Count: ~56+ across structured docs

2. Batch reference within walk-section (MEDIUM confidence):
   Extracts B### markers from walk-header parenthetical
   Inferred verdict: 'walked' (binary)

3. Verdict inference (LOW confidence; logged but not credited):
   Scan walk-section body for verdict keywords
   Not used by _has_strong_evidence per Council 52
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

# Per-strategy walk header pattern
# Matches: "### BR-1. `strat_52w_high_breakout` (Batch 586+589, 52w family, walked B676)"
WALK_HEADER_PATTERN = re.compile(
    r"^###\s+(?P<cluster_id>[A-Z]+-\d+)\.\s+`(?P<strategy>strat_[a-zA-Z0-9_]+)`(?:\s*\((?P<context>[^)]*)\))?",
    re.MULTILINE,
)

# Batch reference in walk-header parenthetical
BATCH_REFS_PATTERN = re.compile(r"\bB(?:atch\s+)?(\d{3,4})\b")
S4B_REFS_PATTERN = re.compile(r"\bS4-B(\d{3,4})\b")
W_REFS_PATTERN = re.compile(r"\bW(\d{1,2})\b")

# Owner-approved verdict vocabulary (per Council 52 First Principles)
VERDICT_VOCAB = (
    "keep", "loosen", "tighten", "swap", "delete",
    "Class7_NEW", "EXPLORATORY", "MAY_REVERT", "walked",
)


def parse_walk_doc(doc_path: Path) -> list[dict[str, Any]]:
    """Extract per-strategy walk entries from a STAGE_4 cluster walk doc."""
    if not doc_path.exists():
        return []
    text = doc_path.read_text(encoding="utf-8", errors="ignore")
    entries = []
    for m in WALK_HEADER_PATTERN.finditer(text):
        strategy = m.group("strategy")
        # Strip "strat_" prefix for canonical ALL_STRATEGIES key
        if strategy.startswith("strat_"):
            strategy_key = strategy[len("strat_"):]
        else:
            strategy_key = strategy
        cluster_id = m.group("cluster_id")
        context = (m.group("context") or "").strip()
        # Extract batch references from context
        batch_refs = set()
        for bm in BATCH_REFS_PATTERN.finditer(context):
            batch_refs.add(f"B{bm.group(1)}")
        for s4 in S4B_REFS_PATTERN.finditer(context):
            batch_refs.add(f"S4-B{s4.group(1)}")
        walk_positions = set()
        for w in W_REFS_PATTERN.finditer(context):
            walk_positions.add(f"W{w.group(1)}")
        entries.append({
            "strategy": strategy_key,
            "cluster_id": cluster_id,
            "batch_refs": sorted(batch_refs),
            "walk_positions": sorted(walk_positions),
            "context": context,
            "verdict": "walked",  # binary baseline; per-strategy verdict inference deferred
            "confidence": "high",  # structured cluster-walk header
            "source": doc_path.name,
        })
    return entries


def build_walk_verdict_ledger() -> dict[str, Any]:
    """Build complete strategy -> walk-entries ledger."""
    docs = sorted(REPO.glob(STAGE_4_DOCS_GLOB))
    logger.info("Parsing %d STAGE_4_*CLUSTER_WALKS.md docs...", len(docs))
    ledger: dict[str, list[dict]] = defaultdict(list)
    for d in docs:
        entries = parse_walk_doc(d)
        for entry in entries:
            ledger[entry["strategy"]].append(entry)
        logger.info("  %s: %d walk entries", d.name, len(entries))
    return dict(ledger)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ledger = build_walk_verdict_ledger()
    out_path = REPO / "output_audit" / "walk_verdict_ledger.json"
    with open(out_path, "w") as f:
        json.dump({
            "schema_version": "1.0",
            "batch": "B948",
            "construction_per_council": "52",
            "n_strategies_with_walks": len(ledger),
            "ledger": ledger,
        }, f, indent=2, default=str)
    logger.info("Ledger COMPLETE: %d strategies with walk entries", len(ledger))
    logger.info("Output: %s", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
