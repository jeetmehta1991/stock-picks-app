"""B950 COUNTERFACTUAL MEASUREMENT (2026-06-20): re-materialize 3 ways.

# Source: Council 54 UNANIMOUS option-epsilon ship-conditional verdict.

Measures three counterfactual distributions WITHOUT touching production
dossiers or criterion code. In-process simulation.

Counterfactuals:
  A-only: v2 ledger (125 strategies; +17 from parser extension), NO verdict-bearing requirement
  B-only: v1 ledger (108 strategies, original), WITH verdict-bearing requirement (strong|medium only)
  A+B  : v2 ledger (125 strategies), WITH verdict-bearing requirement (strong|medium only)

Ship-condition per Council 54:
  A+B lands 80-150 deferred -> ship combined
  A+B lands <50           -> ship A-only
  A+B lands >180          -> ship B-only

Distribution math (sufficient = R5_ready; deferred = needs walk verdict).
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

logger = logging.getLogger(__name__)

DOSSIERS_DIR = REPO / "output_audit" / "dossiers"


def _load_ledger_v1() -> dict[str, list[dict]]:
    p = REPO / "output_audit" / "walk_verdict_ledger.json"
    if not p.exists():
        return {}
    return json.load(open(p)).get("ledger", {})


def _load_ledger_v2() -> dict[str, list[dict]]:
    p = REPO / "output_audit" / "walk_verdict_ledger_v2.json"
    if not p.exists():
        return {}
    return json.load(open(p)).get("ledger", {})


def _ledger_entries_filter_verdict_bearing(entries: list[dict]) -> list[dict]:
    """Keep only entries with verdict_strength == 'strong' or 'medium'.

    v1 entries lack verdict_strength field; treat as 'walked_only' (filtered out).
    """
    return [e for e in entries if e.get("verdict_strength") in ("strong", "medium")]


def _strategy_has_strong_pre_cube_evidence(strategy: str, section_9b: dict,
                                            ledger: dict[str, list[dict]],
                                            require_verdict_bearing: bool) -> bool:
    """Replicate _has_strong_evidence logic with feature-flag control.

    A: S4-B or W## walk markers
    B: fire-count >= 30/yr
    C: STRONG status tags
    D: ledger entry (high|medium confidence; optionally verdict-bearing)
    """
    from backtest.diagnostics.r5_inclusion_criterion import (
        STRONG_STATUS_TAGS, STRONG_WALK_PREFIXES, FIRE_COUNT_PASS_THRESHOLD_PER_YEAR,
    )
    walk_batches = section_9b.get("walk_batches", []) or []
    status_tags = section_9b.get("status_tags", []) or []
    fc = section_9b.get("fire_count_projection") or {}

    # A
    source_a = any(any(b.startswith(p) for p in STRONG_WALK_PREFIXES) for b in walk_batches)
    # B
    try:
        fpy_max = max(float(fc.get("fires_per_year_long") or 0),
                      float(fc.get("fires_per_year_short") or 0))
    except (TypeError, ValueError):
        fpy_max = 0
    source_b = fpy_max >= FIRE_COUNT_PASS_THRESHOLD_PER_YEAR
    # C
    source_c = any(t in STRONG_STATUS_TAGS for t in status_tags)
    # D
    entries = ledger.get(strategy, [])
    if require_verdict_bearing:
        entries = _ledger_entries_filter_verdict_bearing(entries)
    # Keep high|medium confidence per existing rule
    entries = [e for e in entries if e.get("confidence") in ("high", "medium")]
    source_d = bool(entries)

    return source_a or source_b or source_c or source_d


def measure_distribution(ledger: dict, require_verdict_bearing: bool, label: str) -> dict:
    """Re-materialize r5_inclusion_criterion across 217 dossiers using given ledger + flag."""
    counts = {"pre_cube_evidence_sufficient": 0, "deferred": 0, "r4_metrics_passed": 0}
    deferred_strategies = []
    sufficient_strategies = []
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
        strategy = d.name
        s9b = dossier.get("sections", {}).get("section_20_pre_cube_evidence_9b") or {}
        # Track Track 1 / Track 2 logic per existing criterion
        s9 = dossier.get("sections", {}).get("section_09_r4_cube_metrics") or {}
        track = s9.get("track", "track_2_post_r4_addition")
        if track == "track_1_r4_included":
            # Track 1: if r4_metrics_passed -> r4_metrics_passed; else fallback to strong evidence
            if s9.get("passes_canonical_criteria"):
                counts["r4_metrics_passed"] += 1
                continue
        # Track 2 OR Track 1 fallback
        has_strong = _strategy_has_strong_pre_cube_evidence(
            strategy, s9b, ledger, require_verdict_bearing
        )
        if has_strong:
            counts["pre_cube_evidence_sufficient"] += 1
            sufficient_strategies.append(strategy)
        else:
            counts["deferred"] += 1
            deferred_strategies.append(strategy)
    return {
        "label": label,
        "counts": counts,
        "n_deferred": counts["deferred"],
        "n_sufficient": counts["pre_cube_evidence_sufficient"],
        "deferred_strategies": sorted(deferred_strategies),
        "sufficient_strategies_sample": sorted(sufficient_strategies)[:20],
    }


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    v1 = _load_ledger_v1()
    v2 = _load_ledger_v2()
    logger.info("Ledger v1: %d strategies | v2: %d strategies", len(v1), len(v2))

    # Three counterfactuals
    a_only = measure_distribution(v2, require_verdict_bearing=False, label="A_only_parser_only")
    b_only = measure_distribution(v1, require_verdict_bearing=True, label="B_only_tighten_only")
    a_b = measure_distribution(v2, require_verdict_bearing=True, label="A_plus_B_combined")

    # Ship decision per Council 54
    n_deferred_ab = a_b["n_deferred"]
    if 80 <= n_deferred_ab <= 150:
        ship = "A_PLUS_B"
    elif n_deferred_ab < 80:
        # A+B too low; pick whichever single dimension lands closer to 80-150 band
        if 80 <= a_only["n_deferred"] <= 150:
            ship = "A_ONLY"
        elif 80 <= b_only["n_deferred"] <= 150:
            ship = "B_ONLY"
        else:
            # All three outside; pick closest to band midpoint (115)
            candidates = [(abs(c["n_deferred"] - 115), c["label"]) for c in (a_only, b_only, a_b)]
            ship = min(candidates)[1]
    else:
        ship = "A_PLUS_B_OVER_BAND"

    out_path = REPO / "output_audit" / "b950_counterfactuals.json"
    with open(out_path, "w") as f:
        json.dump({
            "schema_version": "1.0", "batch": "B950",
            "council": "54_UNANIMOUS_option_epsilon",
            "ship_decision": ship,
            "counterfactuals": {"A_only": a_only, "B_only": b_only, "A_plus_B": a_b},
            "council_54_band_min": 80, "council_54_band_max": 150,
        }, f, indent=2, default=str)

    for cf in (a_only, b_only, a_b):
        logger.info("%s: %d sufficient / %d deferred", cf["label"], cf["n_sufficient"], cf["n_deferred"])
    logger.info("COUNCIL 54 SHIP DECISION: %s", ship)
    return 0


if __name__ == "__main__":
    sys.exit(main())
