"""B944 (2026-06-20): Phase P1 batch 4 commit 3 - r5_inclusion_criterion setter.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.8.1/13.8.2 + B934 Council 45
# r5_inclusion_criterion enum + Council 48 batch 4 commit 3 "highest leverage
# in entire Phase P1" verdict per owner directive 2026-06-20 Option A.

PURPOSE
-------
**THE LOAD-BEARING VERDICT BIT.** All 20 dossier sections exist to
produce ONE per-strategy verdict:

    r5_inclusion_criterion ∈ {
        "r4_metrics_passed",              # in R4 + passes PASSING_CRITERIA
        "pre_cube_evidence_sufficient",   # post-R4 + has walk/status/fire-count
        "deferred",                       # neither path qualifies
    }

Without this setter, every section is decorative. With it, the dossier
becomes load-bearing infrastructure.

DECISION TREE (Council 45 owner-approved design + Council 48 First
Principles "criterion-setter-first" framing):

  if section_9.track == 1 (in R4 cube):
      if section_9.metrics.passes_all == True
         AND section_10.passes_dec_612_gate == True
         AND section_11.passes_dec_613_gate == True
         AND section_12.passes_dec_614_gate == True:
          -> "r4_metrics_passed"
      else:
          if section_9b.has_pre_cube_evidence == True:
              -> "pre_cube_evidence_sufficient" (fallback path)
          else:
              -> "deferred"

  elif section_9.track == 2 (post-R4 addition):
      if section_9b.has_pre_cube_evidence == True:
          -> "pre_cube_evidence_sufficient"
      else:
          -> "deferred"

  else:
      -> "deferred"

NOTE: This is PRELIMINARY criterion. Sections 13-19 will refine it
post-B944. r4_metrics_passed gate is conservative; B890 AUTO-FAIL
gates ARE materialized via Sections 10/11/12 (B943) but other
canonical criteria (Sharpe/Sortino/Calmar/DSR per regime) are read
directly from R4 CSV via section_9.metrics.passes_all.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


VALID_CRITERIA = ("r4_metrics_passed", "pre_cube_evidence_sufficient", "deferred")


# B946 (2026-06-20) Council 50 STRONG-EVIDENCE refinement:
# Replace permissive 'has_pre_cube_evidence=True' check with strict evidence
# subset. Owner-approved status tags carry weight; lineage tags do not.
STRONG_STATUS_TAGS = frozenset({
    # From canonical backtest/config.py sets
    "MEASUREMENT_DISPUTED",
    "MEAN_REVERSION_STRATEGIES",
    "DISABLED_MISSING_PRODUCER",
    # From owner-approved docstring markers
    "EXPLORATORY",
    "DORMANT",
    "B748d_walk_back_protected",
    "MAY_REVERT",
})

# Lineage-only tags are descriptive, not owner-approval evidence.
# Explicitly REJECTED from STRONG_STATUS_TAGS per Council 50 verdict:
LINEAGE_ONLY_TAGS = frozenset({
    "EVENT_only",
    "SHORT_EXPLORATORY",
    "Wave_lineage",
    "mean_reversion",  # docstring scrape; canonical set membership is the proof
    # PATTERN_X tags (PATTERN_AA, PATTERN_W, etc.) handled via prefix check
})

# Stage 4 walk-ticket prefixes; B883 ledger-bearing per Council 10.
# Generic 'B###' rejected (could be any incidental commit).
STRONG_WALK_PREFIXES = ("S4-B", "W")

# CLAUDE.md criterion #9 per-regime min_trades; codified power floor.
FIRE_COUNT_PASS_THRESHOLD_PER_YEAR = 30.0


def _has_strong_evidence(section_9b: dict | None) -> tuple[bool, dict]:
    """Council 50 strict evidence check.

    Returns (passes_strong_check, evidence_breakdown).
    Evidence is STRONG if AT LEAST ONE OF:
      A. Walk batches include S4-B### or W## marker (Stage 4 walk ticket)
      B. Fire-count projection >= 30/yr per direction (long OR short)
      C. Status tags include any of STRONG_STATUS_TAGS

    PATTERN_X tags (PATTERN_AA, PATTERN_W, etc.) are LINEAGE-only and
    REJECTED. mean_reversion docstring tag is REJECTED in favor of
    canonical MEAN_REVERSION_STRATEGIES config set membership.
    """
    if not section_9b:
        return False, {"reason": "section_9b_missing"}
    # A. Stage 4 walk markers
    walks = section_9b.get("walk_batches", []) or []
    strong_walks = [w for w in walks if w.startswith(STRONG_WALK_PREFIXES)]
    # B. Fire-count threshold
    fc = section_9b.get("fire_count_projection")
    fpy_long = (fc or {}).get("fires_per_year_long") or 0
    fpy_short = (fc or {}).get("fires_per_year_short") or 0
    try:
        fpy_max = max(float(fpy_long or 0), float(fpy_short or 0))
    except (TypeError, ValueError):
        fpy_max = 0
    fire_pass = fpy_max >= FIRE_COUNT_PASS_THRESHOLD_PER_YEAR
    # C. Owner-approved status tags
    tags = section_9b.get("status_tags", []) or []
    strong_tags = [t for t in tags if t in STRONG_STATUS_TAGS]
    # PATTERN_X tags are lineage-only; explicitly do not count
    rejected_lineage = [
        t for t in tags
        if t in LINEAGE_ONLY_TAGS or t.startswith("PATTERN_")
    ]
    breakdown = {
        "strong_walk_markers": strong_walks,
        "fire_count_per_year_max": fpy_max,
        "fire_count_passes_threshold": fire_pass,
        "fire_count_threshold": FIRE_COUNT_PASS_THRESHOLD_PER_YEAR,
        "strong_status_tags": strong_tags,
        "rejected_lineage_tags": rejected_lineage,
        "passes_strong_check": bool(strong_walks) or fire_pass or bool(strong_tags),
    }
    return breakdown["passes_strong_check"], breakdown


def compute_r5_inclusion_criterion(dossier: dict[str, Any]) -> dict[str, Any]:
    """Compute r5_inclusion_criterion + rationale from populated sections.

    Returns:
        {
          "value": <one of VALID_CRITERIA>,
          "rationale": str,
          "track": 1 or 2 or None,
          "auto_fail_gates": {
              "dec_612_cost_sensitivity": bool|None,
              "dec_613_chow_break": bool|None,
              "dec_614_adf": bool|None,
          },
          "evidence_used": [...],
        }
    """
    sections = dossier.get("sections", {})
    section_9 = sections.get("section_09_r4_cube_metrics")
    section_9b = sections.get("section_20_pre_cube_evidence_9b")
    section_10 = sections.get("section_10_cost_sensitivity_ratio")
    section_11 = sections.get("section_11_chow_break_point")
    section_12 = sections.get("section_12_adf_p_value")

    if section_9 is None:
        return {
            "value": "deferred",
            "rationale": "Section 9 not populated; cannot determine R4 inclusion track.",
            "track": None,
            "auto_fail_gates": {},
            "evidence_used": [],
        }

    track = section_9.get("track")
    evidence_used = ["section_09"]

    # Track 1: in R4 cube
    if track == 1:
        metrics = section_9.get("metrics") or {}
        passes_all = metrics.get("passes_all")
        if isinstance(passes_all, str):
            passes_all = passes_all.strip().lower() == "true"
        elif not isinstance(passes_all, bool):
            passes_all = None

        # B890 AUTO-FAIL gates from B943 R4 pass-through
        dec612 = section_10.get("passes_dec_612_gate") if isinstance(section_10, dict) else None
        dec613 = section_11.get("passes_dec_613_gate") if isinstance(section_11, dict) else None
        dec614 = section_12.get("passes_dec_614_gate") if isinstance(section_12, dict) else None

        gates = {
            "dec_612_cost_sensitivity": dec612,
            "dec_613_chow_break": dec613,
            "dec_614_adf": dec614,
        }
        evidence_used.extend(["section_10", "section_11", "section_12"])

        # All gates must be True (None permitted as "data missing; conservative pass")
        gates_all_pass = all(
            v is None or v is True for v in (dec612, dec613, dec614)
        )

        if passes_all is True and gates_all_pass:
            return {
                "value": "r4_metrics_passed",
                "rationale": "In R4 cube + passes_all=True + all AUTO-FAIL gates clear (DEC-612/613/614).",
                "track": 1,
                "auto_fail_gates": gates,
                "evidence_used": evidence_used,
            }
        # B946 Council 50 STRONG-EVIDENCE fallback (replaces permissive
        # has_pre_cube_evidence check): require strict markers per Council 50
        strong_pass, evidence_breakdown = _has_strong_evidence(section_9b)
        if strong_pass:
            return {
                "value": "pre_cube_evidence_sufficient",
                "rationale": (
                    f"In R4 cube but criterion failed (passes_all={passes_all!r}; "
                    f"gates={gates}); fallback to Section 9b STRONG evidence per Council 50."
                ),
                "track": 1,
                "auto_fail_gates": gates,
                "evidence_used": evidence_used + ["section_20_pre_cube_evidence_9b"],
                "strong_evidence_breakdown": evidence_breakdown,
            }
        return {
            "value": "deferred",
            "rationale": (
                f"In R4 cube but criterion failed (passes_all={passes_all!r}; "
                f"gates={gates}); no STRONG evidence in Section 9b per Council 50."
            ),
            "track": 1,
            "auto_fail_gates": gates,
            "evidence_used": evidence_used,
            "strong_evidence_breakdown": evidence_breakdown,
        }

    # Track 2: post-R4 addition
    if track == 2:
        strong_pass, evidence_breakdown = _has_strong_evidence(section_9b)
        if strong_pass:
            return {
                "value": "pre_cube_evidence_sufficient",
                "rationale": "Post-R4 addition with STRONG evidence per Council 50 (S4-walk OR fire-count>=30 OR owner-approved status tag).",
                "track": 2,
                "auto_fail_gates": {},
                "evidence_used": ["section_09", "section_20_pre_cube_evidence_9b"],
                "strong_evidence_breakdown": evidence_breakdown,
            }
        return {
            "value": "deferred",
            "rationale": "Post-R4 addition without STRONG evidence per Council 50 (lineage tags + generic batch refs are insufficient).",
            "track": 2,
            "auto_fail_gates": {},
            "evidence_used": ["section_09"],
            "strong_evidence_breakdown": evidence_breakdown,
        }

    # Track 0 (CSV missing or unexpected)
    return {
        "value": "deferred",
        "rationale": f"Unexpected track={track!r}; treating as deferred.",
        "track": track,
        "auto_fail_gates": {},
        "evidence_used": evidence_used,
    }


def set_r5_inclusion_criterion_for_dossier(dossier_path: Path) -> dict[str, Any]:
    """Read dossier, compute criterion, write back. Returns the criterion dict."""
    if not dossier_path.exists():
        raise FileNotFoundError(f"Dossier not initialized: {dossier_path}")
    with open(dossier_path) as f:
        dossier = json.load(f)
    criterion = compute_r5_inclusion_criterion(dossier)
    # Set the dossier field (preserves nested structure under sections)
    dossier["r5_inclusion_criterion"] = criterion["value"]
    dossier["r5_inclusion_criterion_detail"] = criterion
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
    return criterion
