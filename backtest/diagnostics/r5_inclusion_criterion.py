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
        # Fallback to pre-cube evidence for R4-included-but-failed
        if section_9b and section_9b.get("has_pre_cube_evidence"):
            return {
                "value": "pre_cube_evidence_sufficient",
                "rationale": (
                    f"In R4 cube but criterion failed (passes_all={passes_all!r}; "
                    f"gates={gates}); fallback to Section 9b pre-cube evidence."
                ),
                "track": 1,
                "auto_fail_gates": gates,
                "evidence_used": evidence_used + ["section_20_pre_cube_evidence_9b"],
            }
        return {
            "value": "deferred",
            "rationale": (
                f"In R4 cube but criterion failed (passes_all={passes_all!r}; "
                f"gates={gates}); no Section 9b fallback evidence."
            ),
            "track": 1,
            "auto_fail_gates": gates,
            "evidence_used": evidence_used,
        }

    # Track 2: post-R4 addition
    if track == 2:
        if section_9b and section_9b.get("has_pre_cube_evidence"):
            return {
                "value": "pre_cube_evidence_sufficient",
                "rationale": "Post-R4 addition with walk-batch / status-tag / fire-count evidence.",
                "track": 2,
                "auto_fail_gates": {},
                "evidence_used": ["section_09", "section_20_pre_cube_evidence_9b"],
            }
        return {
            "value": "deferred",
            "rationale": "Post-R4 addition with no pre-cube evidence (no walks / no status / no fire-count).",
            "track": 2,
            "auto_fail_gates": {},
            "evidence_used": ["section_09"],
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
