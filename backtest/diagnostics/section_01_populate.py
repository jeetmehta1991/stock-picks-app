"""B951 Section 1 populate helper.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 1 + Council 55 verdict.
"""
from __future__ import annotations

import json
from pathlib import Path

from .section_01_wiring_trace import extract_section_01_for_strategy


def populate_section_01_for_dossier(strategy: str, dossier_path: Path) -> None:
    """Populate Section 1 wiring_trace_coverage slot in dossier.json."""
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_payload = extract_section_01_for_strategy(strategy)
    sections = dossier.setdefault("sections", {})
    sections["section_01_wiring_trace_coverage"] = section_payload
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
