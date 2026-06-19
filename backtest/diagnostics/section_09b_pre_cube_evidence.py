"""B936 (2026-06-19): Section 9b TWO-TRACK pre-cube evidence extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 9b (B934 Council 45 owner-A
# addition) + Council 46 batch 2 commit 1 per owner directive 2026-06-19 Option A.

PURPOSE
-------
Section 9b is the LOAD-BEARING counterpart to Section 9 TWO-TRACK. For
post-R4 additions (~117 strategies that lack R4 cube metrics), Section 9b
carries the pre-cube evidence that justifies their inclusion in R5:

  - fire_count_projection:    From B660/B907 fire-count measurements
                              (when available in output_audit/*)
  - walk_batches:             B883 Stage 4 walk ledger references
                              (from git log + screener.py docstring
                              batch markers)
  - status_tags:              EXPLORATORY / DORMANT / MEASUREMENT_DISPUTED
                              from backtest/config.py sets
                              + inline EXPLORATORY docstring scrape
  - attribution_narrative:    Synthesized narrative per PATH 13.7 gate #7

For Section 9 TRACK 1 (R4-included strategies), Section 9b STILL populates
where status_tags / walks exist; both sections are independent. The dossier's
r5_inclusion_criterion combines Section 9 + 9b verdicts.
"""
from __future__ import annotations

import inspect
import json
import logging
import re
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


REPO = Path(__file__).resolve().parent.parent.parent


def _extract_status_tags_from_screener_docstring(strategy: str) -> list[str]:
    """Scan strategy function docstring for inline status markers.

    Common patterns documented across batches (per CLAUDE.md):
    - 'EXPLORATORY' (B644 / B652 / B873 etc.)
    - 'DORMANT' (Phase 1B-alpha reserved)
    - 'MEAN-REV' / 'mean-reversion' (canonical)
    - 'B748d-protected' / 'walk-back protected'
    - 'MAY-REVERT' (B931 institutional_persistence pattern)
    """
    try:
        from backtest.signals.screener import ALL_STRATEGIES
    except Exception:
        return []
    fn = ALL_STRATEGIES.get(strategy)
    if fn is None:
        return []
    doc = inspect.getdoc(fn) or ""
    tags = []
    if re.search(r"\bEXPLORATORY\b", doc):
        tags.append("EXPLORATORY")
    if re.search(r"\bDORMANT\b", doc):
        tags.append("DORMANT")
    if re.search(r"B748d|walk[- ]back[- ]protected", doc, re.IGNORECASE):
        tags.append("B748d_walk_back_protected")
    if re.search(r"MAY[- ]REVERT", doc):
        tags.append("MAY_REVERT")
    if re.search(r"mean[- ]rev(ersion)?", doc, re.IGNORECASE):
        tags.append("mean_reversion")
    return tags


def _config_status_tags(strategy: str) -> list[str]:
    """Cross-reference strategy against canonical backtest/config.py status sets."""
    tags = []
    try:
        from backtest.config import (
            MEASUREMENT_DISPUTED,
            MEAN_REVERSION_STRATEGIES,
            STRATEGIES_DISABLED_MISSING_PRODUCER,
        )
    except Exception:
        return []
    if strategy in MEASUREMENT_DISPUTED:
        tags.append("MEASUREMENT_DISPUTED")
    if strategy in MEAN_REVERSION_STRATEGIES:
        tags.append("MEAN_REVERSION_STRATEGIES")
    if strategy in STRATEGIES_DISABLED_MISSING_PRODUCER:
        tags.append("DISABLED_MISSING_PRODUCER")
    return tags


def _scrape_walk_batches_from_docstring(strategy: str) -> list[str]:
    """Extract batch references from strategy docstring (e.g., 'B685', 'B907').

    Per B883 Stage 4 walk ledger pattern: walk batches are documented inline
    in strategy docstrings (Batch NNN: ... lineage entries).
    """
    try:
        from backtest.signals.screener import ALL_STRATEGIES
    except Exception:
        return []
    fn = ALL_STRATEGIES.get(strategy)
    if fn is None:
        return []
    doc = inspect.getdoc(fn) or ""
    # Match "Batch NNN" / "B###" / "Wave N" patterns
    batch_refs = set()
    for m in re.finditer(r"\bB(?:atch\s+)?(\d{3,4})\b", doc):
        batch_refs.add(f"B{m.group(1)}")
    return sorted(batch_refs)


def _fire_count_projection(strategy: str) -> Optional[dict]:
    """Search output_audit/ for B660/B907 fire-count projections for this strategy.

    Returns dict with fires_per_year + source_file or None if not found.
    Lightweight scan; first match returned.
    """
    audit_dir = REPO / "output_audit"
    if not audit_dir.exists():
        return None
    # Scan B660 / B907 / b922 / b926 fire-count JSON outputs
    candidate_patterns = ["b660*.json", "b907*.json", "b922*.json", "b926*.json", "b919*.json"]
    for pat in candidate_patterns:
        for f in audit_dir.glob(pat):
            try:
                with open(f) as fh:
                    data = json.load(fh)
            except Exception:
                continue
            # Common schemas: {strategies: {strat: {fires_per_year_long: X}}}
            results = data.get("results") or data.get("strategies") or []
            if isinstance(results, list):
                for entry in results:
                    if entry.get("strategy") == strategy:
                        return {
                            "source_file": f.name,
                            "fires_per_year_long": entry.get("fires_per_year_long"),
                            "fires_per_year_short": entry.get("fires_per_year_short"),
                            "verdict": entry.get("verdict_220") or entry.get("verdict"),
                        }
            elif isinstance(results, dict) and strategy in results:
                entry = results[strategy]
                return {
                    "source_file": f.name,
                    "fires_per_year_long": entry.get("fires_per_year_long"),
                    "fires_per_year_short": entry.get("fires_per_year_short"),
                    "verdict": entry.get("verdict_220") or entry.get("verdict"),
                }
    return None


def extract_section_09b(strategy: str) -> dict[str, Any]:
    """Extract Section 9b pre-cube evidence for a strategy.

    Returns Council 45 schema:
        {
          "fire_count_projection": {<from B660/B907>} | None,
          "walk_batches": [<B### references>],
          "status_tags": [<EXPLORATORY/DORMANT/DISPUTED/...>],
          "attribution_narrative": "<synthesized>",
          "has_pre_cube_evidence": bool,
        }
    """
    fire_count = _fire_count_projection(strategy)
    walk_batches = _scrape_walk_batches_from_docstring(strategy)
    config_tags = _config_status_tags(strategy)
    doc_tags = _extract_status_tags_from_screener_docstring(strategy)
    status_tags = sorted(set(config_tags + doc_tags))

    # Synthesize attribution narrative
    narrative_parts = []
    if fire_count:
        fpy = fire_count.get("fires_per_year_long") or fire_count.get("fires_per_year_short") or 0
        narrative_parts.append(
            f"Fire-count projection: {fpy:.1f}/yr per {fire_count['source_file']}"
        )
    if walk_batches:
        narrative_parts.append(f"Stage 4 walk references: {', '.join(walk_batches[:5])}")
    if status_tags:
        narrative_parts.append(f"Status: {', '.join(status_tags)}")
    if not narrative_parts:
        narrative_parts.append(
            "NO pre-cube evidence found. Strategy lacks fire-count projection, walk-batch "
            "references in docstring, AND status tags. r5_inclusion_criterion candidate: 'deferred'."
        )
    narrative = " | ".join(narrative_parts)

    has_evidence = bool(fire_count) or bool(walk_batches) or bool(status_tags)

    return {
        "fire_count_projection": fire_count,
        "walk_batches": walk_batches,
        "status_tags": status_tags,
        "attribution_narrative": narrative,
        "has_pre_cube_evidence": has_evidence,
    }


def populate_section_09b_for_dossier(strategy: str, dossier_path: Path) -> Path:
    """Read dossier.json, set Section 9b (key: section_20_pre_cube_evidence_9b), write back."""
    if not dossier_path.exists():
        raise FileNotFoundError(f"Dossier not initialized: {dossier_path}")
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_value = extract_section_09b(strategy)
    dossier["sections"]["section_20_pre_cube_evidence_9b"] = section_value
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
    logger.debug(
        "Populated Section 9b for %s: %d tags, %d walks, fire_count=%s",
        strategy, len(section_value["status_tags"]),
        len(section_value["walk_batches"]),
        bool(section_value["fire_count_projection"]),
    )
    return dossier_path
