"""B953 (2026-06-20): Phase P1 batch 13 - Section 5 regime_affinity_lineage extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 5 + Council 57 UNANIMOUS
# 4/4 verdict per owner directive 2026-06-20 'Continue council this' +
# memory rule feedback_regime_selector_lineage_grep_before_delete (B663).

PURPOSE
-------
Section 5 = anti-iteration value for the 127 deferred owner walks.

Per memory rule `feedback_regime_selector_lineage_grep_before_delete`:
  'Grep regime_selector.py lineage BEFORE proposing regime affinity deletes.'
  B663 lesson: B663 SM-1 walk F3 proposed delete of insider_cluster_long
  regime entries citing CMP 2012 literature, but B263 lineage at lines
  261-264 documented Phase 1A-alpha empirical override (36 crisis trades
  at 22% WR). Pre-flight grep would have caught it.

Section 5 makes that mandatory grep ONE-CLICK per strategy in the dossier.

PRE-BUILD CHECK (Council 57 Executor mandate, executed before coding):
  git log --follow regime_selector.py: 29 commits (substantive history)
  STRATEGY_REGIME_AFFINITY at line 107
  Inline batch lineage comments: B252/B253/B254/B293/B316a/B370/B418 found
  Multi-batch edits per strategy: confirmed (e.g., pairs_mean_reversion_long
  has B253 + B418 lineage)
  Section 5 build APPROVED per pre-build check.

OUTPUT SCHEMA per strategy:
{
  "current_regimes": [list of regimes] | None (if no entry = allow-all),
  "has_explicit_entry": bool,
  "lineage_comment_block": str (comment lines preceding the dict entry),
  "batch_refs": [list of B### / S4-B### / DEC-###],
  "regime_selector_line_number": int,
  "method": "ast_parse_regime_selector_py",
  "source": "backtest/engine/regime_selector.py",
  "anti_iteration_mandate": "feedback_regime_selector_lineage_grep_before_delete (B663)",
}
"""
from __future__ import annotations

import ast
import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent.parent
REGIME_SELECTOR_PATH = REPO / "backtest" / "engine" / "regime_selector.py"

# Batch / S4-B / DEC reference patterns
BATCH_REFS_PATTERN = re.compile(r"\bB(?:atch\s+)?(\d{3,4})\b")
S4B_REFS_PATTERN = re.compile(r"\bS4-B(\d{3,4})\b")
DEC_REFS_PATTERN = re.compile(r"\bDEC-(\d{3,4})\b")


@lru_cache(maxsize=1)
def _parse_regime_selector_strategy_index() -> dict[str, dict[str, Any]]:
    """Parse regime_selector.py AST + inline comment context.

    Returns {strategy: {regimes, line_no, leading_comments}}
    """
    if not REGIME_SELECTOR_PATH.exists():
        return {}
    source = REGIME_SELECTOR_PATH.read_text(encoding="utf-8", errors="ignore")
    source_lines = source.splitlines()
    try:
        tree = ast.parse(source)
    except Exception as e:
        logger.error("Cannot parse regime_selector.py: %s", e)
        return {}

    # Find the STRATEGY_REGIME_AFFINITY assignment
    affinity_dict_node = None
    for node in ast.walk(tree):
        if (isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
                and node.target.id == "STRATEGY_REGIME_AFFINITY"):
            affinity_dict_node = node.value
            break
        if (isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "STRATEGY_REGIME_AFFINITY"):
            affinity_dict_node = node.value
            break
    if affinity_dict_node is None or not isinstance(affinity_dict_node, ast.Dict):
        logger.warning("STRATEGY_REGIME_AFFINITY dict not found")
        return {}

    index: dict[str, dict[str, Any]] = {}
    for k_node, v_node in zip(affinity_dict_node.keys, affinity_dict_node.values):
        if not isinstance(k_node, ast.Constant) or not isinstance(k_node.value, str):
            continue
        strategy = k_node.value
        line_no = k_node.lineno
        # Extract regime set values
        regimes: list[str] = []
        if isinstance(v_node, ast.Set):
            for elt in v_node.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    regimes.append(elt.value)
        regimes.sort()
        # Extract leading comment block: scan upward from line_no-1 until a
        # non-comment / non-blank line (or another dict entry)
        leading_comments: list[str] = []
        i = line_no - 2  # 0-indexed; line above the strategy key
        while i >= 0:
            line = source_lines[i].rstrip()
            stripped = line.lstrip()
            if stripped.startswith("#"):
                leading_comments.append(stripped[1:].lstrip())
                i -= 1
                continue
            if not stripped:
                # Allow ONE blank line; further blank stops scan
                if leading_comments:
                    break
                i -= 1
                continue
            break
        leading_comments.reverse()
        comment_block = "\n".join(leading_comments)
        # Extract batch refs from comment block
        batch_refs = set()
        for m in BATCH_REFS_PATTERN.finditer(comment_block):
            batch_refs.add(f"B{m.group(1)}")
        for m in S4B_REFS_PATTERN.finditer(comment_block):
            batch_refs.add(f"S4-B{m.group(1)}")
        for m in DEC_REFS_PATTERN.finditer(comment_block):
            batch_refs.add(f"DEC-{m.group(1)}")
        index[strategy] = {
            "regimes": regimes,
            "line_no": line_no,
            "leading_comments": comment_block,
            "batch_refs": sorted(batch_refs),
        }
    return index


def extract_section_05_for_strategy(strategy: str) -> dict[str, Any]:
    """Extract Section 5 regime_affinity_lineage for a single strategy.

    Returns dict for Section 5 dossier slot.
    """
    index = _parse_regime_selector_strategy_index()
    entry = index.get(strategy)
    if entry is None:
        return {
            "current_regimes": None,
            "has_explicit_entry": False,
            "lineage_comment_block": "",
            "batch_refs": [],
            "regime_selector_line_number": None,
            "method": "ast_parse_regime_selector_py",
            "source": "backtest/engine/regime_selector.py",
            "anti_iteration_mandate": (
                "feedback_regime_selector_lineage_grep_before_delete (B663): "
                "Strategy not in STRATEGY_REGIME_AFFINITY dict -> defaults to "
                "ALLOW-ALL regimes. No lineage to grep; regime decisions are "
                "implicit."
            ),
        }
    return {
        "current_regimes": entry["regimes"],
        "has_explicit_entry": True,
        "lineage_comment_block": entry["leading_comments"],
        "batch_refs": entry["batch_refs"],
        "regime_selector_line_number": entry["line_no"],
        "method": "ast_parse_regime_selector_py",
        "source": "backtest/engine/regime_selector.py",
        "anti_iteration_mandate": (
            "feedback_regime_selector_lineage_grep_before_delete (B663): "
            "READ lineage_comment_block + batch_refs BEFORE proposing any "
            "regime affinity change. Multiple batches may have codified "
            "this entry; deletion without checking lineage caused B663 lapse."
        ),
    }


def populate_section_05_for_dossier(strategy: str, dossier_path: Path) -> None:
    """Populate Section 5 regime_affinity_lineage slot in dossier.json."""
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_payload = extract_section_05_for_strategy(strategy)
    sections = dossier.setdefault("sections", {})
    sections["section_05_regime_affinity_lineage"] = section_payload
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
