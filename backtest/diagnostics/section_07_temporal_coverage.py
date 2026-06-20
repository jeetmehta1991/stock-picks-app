"""B952 (2026-06-20): Phase P1 batch 12 - Section 7 temporal coverage probe extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 7 + Council 56 UNANIMOUS
# 4/4 verdict per owner directive 2026-06-20 'Continue council this' +
# Outsider pre-build check (B660 JSON schema verified before extractor design).

PURPOSE
-------
Highest decision-aid column for owner Stage 4 walks: surfaces strategies
that LOOK valid statically (gates present, regime tagged, signals exist)
but EMPIRICALLY fire below the min_trades=30/yr floor per CLAUDE.md
criterion #9.

Consumes existing B660 measured fire-count JSON
(output_audit/fire_count_measured_b660_full_universe.json).

PRE-BUILD CHECK (Outsider Council 56 mandate, executed before coding):
  B660 JSON has CUMULATIVE measures over 2020-2026 (calendar_year_span=6.41)
  NOT per-year breakdown. Schema confirms:
    - measured_fires_per_calendar_year_*_sampled (cumulative div by span)
    - projected_fires_per_calendar_year_*_full_t1a (cumulative scaled)
    - first_fire_date / last_fire_date
    - calendar_year_span = 6.41
    - verdict = FAIL_FIRE_STARVED | PASS_CUBE | ...
  Section 7 ships TOTAL + FAIL_FIRE_STARVED flag HONESTLY.
  Per-year columns require B660-rerun with per-year aggregation; queued
  separately as future ticket.

Output schema:
{
  "verdict": "FAIL_FIRE_STARVED" | "PASS_CUBE" | "MIXED" | "UNKNOWN",
  "n_fires_long_total": int,
  "n_fires_short_total": int,
  "n_fires_avoid_total": int,
  "fires_per_year_long": float | None,
  "fires_per_year_short": float | None,
  "fires_per_year_total": float | None,
  "calendar_year_span": float,
  "first_fire_date": str | None,
  "last_fire_date": str | None,
  "min_trades_floor": 30,
  "passes_min_trades_floor_long": bool,
  "passes_min_trades_floor_short": bool,
  "passes_min_trades_floor_either": bool,
  "source": "B660_full_universe_2026-05-31",
  "method": "static_from_b660_measured_json",
  "limitation": str (HONEST about per-year-breakdown unavailability)
}
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent.parent
B660_PATH = REPO / "output_audit" / "fire_count_measured_b660_full_universe.json"

MIN_TRADES_FLOOR = 30  # CLAUDE.md criterion #9 per-regime power floor


@lru_cache(maxsize=1)
def _load_b660_index() -> dict[str, dict[str, Any]]:
    """Load B660 results indexed by strategy name."""
    if not B660_PATH.exists():
        logger.warning("B660 fire-count JSON not found at %s", B660_PATH)
        return {}
    try:
        with open(B660_PATH) as f:
            data = json.load(f)
        results = data.get("results", [])
        index = {r.get("strategy"): r for r in results if r.get("strategy")}
        return index
    except Exception as e:
        logger.error("Cannot load B660 JSON: %s", e)
        return {}


def extract_section_07_for_strategy(strategy: str) -> dict[str, Any]:
    """Extract Section 7 temporal_coverage_probe data for a single strategy.

    Returns dict for Section 7 dossier slot. method='static_from_b660_measured_json';
    honest about per-year breakdown unavailability per Outsider Council 56 mandate.
    """
    index = _load_b660_index()
    row = index.get(strategy)
    if row is None:
        return {
            "verdict": "UNKNOWN",
            "n_fires_long_total": None,
            "n_fires_short_total": None,
            "n_fires_avoid_total": None,
            "fires_per_year_long": None,
            "fires_per_year_short": None,
            "fires_per_year_total": None,
            "calendar_year_span": None,
            "first_fire_date": None,
            "last_fire_date": None,
            "min_trades_floor": MIN_TRADES_FLOOR,
            "passes_min_trades_floor_long": False,
            "passes_min_trades_floor_short": False,
            "passes_min_trades_floor_either": False,
            "source": "B660_full_universe_2026-05-31",
            "method": "static_from_b660_measured_json",
            "limitation": (
                "Strategy not present in B660 results (post-B660 addition OR "
                "B660 run pre-dates strategy registration). Re-run "
                "measure_fire_count.py --full to populate."
            ),
        }
    fpy_long = row.get("projected_fires_per_calendar_year_long_full_t1a")
    fpy_short = row.get("projected_fires_per_calendar_year_short_full_t1a")
    fpy_total = row.get("projected_fires_per_calendar_year_total_full_t1a")
    passes_long = (fpy_long or 0) >= MIN_TRADES_FLOOR
    passes_short = (fpy_short or 0) >= MIN_TRADES_FLOOR
    return {
        "verdict": row.get("projected_verdict_full_t1a") or row.get("verdict") or "UNKNOWN",
        "n_fires_long_total": row.get("n_fires_long"),
        "n_fires_short_total": row.get("n_fires_short"),
        "n_fires_avoid_total": row.get("n_fires_avoid"),
        "fires_per_year_long": fpy_long,
        "fires_per_year_short": fpy_short,
        "fires_per_year_total": fpy_total,
        "calendar_year_span": row.get("calendar_year_span"),
        "first_fire_date": row.get("first_fire_date"),
        "last_fire_date": row.get("last_fire_date"),
        "min_trades_floor": MIN_TRADES_FLOOR,
        "passes_min_trades_floor_long": passes_long,
        "passes_min_trades_floor_short": passes_short,
        "passes_min_trades_floor_either": passes_long or passes_short,
        "source": "B660_full_universe_2026-05-31",
        "method": "static_from_b660_measured_json",
        "limitation": (
            "B660 measured CUMULATIVE 2020-2026 (calendar_year_span=6.41). "
            "Per-year breakdown columns (fire_count_2020, _2021, ...) are NOT "
            "available; B660 reports cumulative totals + projection. Future "
            "B660-rerun with per-year aggregation queued as separate ticket."
        ),
    }


def populate_section_07_for_dossier(strategy: str, dossier_path: Path) -> None:
    """Populate Section 7 temporal_coverage_probe slot in dossier.json."""
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_payload = extract_section_07_for_strategy(strategy)
    sections = dossier.setdefault("sections", {})
    sections["section_07_temporal_coverage_probe"] = section_payload
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
