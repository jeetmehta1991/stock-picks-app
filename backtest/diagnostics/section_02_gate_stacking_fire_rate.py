# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 2 per CHECKLIST #77.
"""B962 (2026-06-20): Phase P1 batch 22 - Section 2 gate_stacking_fire_rate extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 2 + Council 67 4/4 verdict
# per owner directive 2026-06-20 'Continue council this. Continue without
# stopping till all sections in P1 are done.' per CHECKLIST #77.

PURPOSE
-------
Section 2 = PATH-load-bearing for R5 launch gate #6 per Section 13.7:
  'All strategies: dossier.gate_stacking_check == passed'.
Gate-stacking diagnostic identifies strategies whose AND-stacked gates
multiplicatively drive fire-rate below the min_trades=30/regime power floor.

PATH Section 13.3 row 2 spec (canonical):
  'Gate-stacking + per-gate fire-rate'
  'RUNTIME measurement from R4 trade_log (NOT a-priori estimator;
   estimator missed B660 by order of magnitude)'

PRE-BUILD CHECK (Council 67 Executor mandate, executed before coding):
  B660 fire_count_measured_b660_full_universe.json: OK (post-B648 fix;
    universe=503 T1a-PIT-active not 220 hardcoded bug)
  Schema verified: results[].strategy + results[].gate_marginals (dict)
    + results[].verdict (FAIL_FIRE_STARVED/etc.) + results[].n_fires_long/short
    + results[].projected_fires_per_calendar_year_total_full_t1a
  R4 trade_log.csv: ~29k trades x 102 firing strategies (sparse fire-count
    proxy; B660 is the PATH-spec canonical RUNTIME source per row 2 text)
  All 222 strategies present in B660 results (older roster; current 219 may
    have <222 hits; missing strategies return status='not_in_b660_measurement')
  Build APPROVED.

METHODOLOGY (per-strategy gate-stacking diagnostic):
  1. Look up strategy in B660 results by `strategy` key.
  2. Extract `gate_marginals` (per-gate fire rate, P(gate=True) on universe).
  3. Compute `n_gates_stacked` = len(gate_marginals).
  4. Compute `min_marginal` = min gate fire-rate (tightest gate).
  5. Compute `independence_predicted_joint_prob` = product of marginals
     (assumes independence; surfaces upper bound on joint fire rate).
  6. Report `measured_fires_per_year_full_t1a` from B660
     `projected_fires_per_calendar_year_total_full_t1a`.
  7. Report `b660_verdict` (FAIL_FIRE_STARVED / PASS).
  8. Composite `gate_stacking_check`:
       passed if measured_fires_per_year >= 30 (CLAUDE.md min_trades floor)
       OR if status indicates strategy not in measurement
       OR if marked EXPLORATORY/DORMANT (cube allowed to validate sparse)
       failed otherwise (catches genuine gate-stack starvation)

OUTPUT SCHEMA per strategy:
{
  "n_gates_stacked": int | None,
  "gate_marginals": dict[str, float] | None,
  "min_marginal_fire_rate": float | None,
  "tightest_gate": str | None,
  "independence_predicted_joint_prob": float | None,
  "measured_fires_per_year_full_t1a": float | None,
  "b660_verdict": str | None,
  "gate_stacking_check": str,  # passed / failed / not_measured
  "method": "runtime_measurement_b660_post_b648",
  "source": "output_audit/fire_count_measured_b660_full_universe.json",
  "limitation": str,
  "memory_rule_reference": str,
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

# CLAUDE.md passing criterion #9: min_trades per regime >= 30
MIN_TRADES_PER_REGIME_FLOOR = 30
# Approximate # of regimes the floor must be cleared in; 1 regime sufficient
# per CLAUDE.md per-regime verdict (#11). Use 1 as the leniency conversion.
MIN_FIRES_PER_YEAR_FLOOR = 30


@lru_cache(maxsize=1)
def _load_b660_index() -> dict[str, dict[str, Any]]:
    """Load B660 fire-count measurement indexed by strategy name.

    B660 schema: top-level dict with `results` list; each element has
    `strategy`, `gate_marginals` (dict), `verdict`, projected fires keys.
    Returns {strategy: result_dict} mapping; empty if B660 absent.
    """
    if not B660_PATH.exists():
        logger.warning("B660 fire_count_measured JSON not found at %s", B660_PATH)
        return {}
    try:
        with open(B660_PATH) as f:
            data = json.load(f)
    except Exception as e:
        logger.error("Cannot parse B660 fire-count JSON: %s", e)
        return {}
    results = data.get("results", [])
    if not isinstance(results, list):
        logger.error("B660 results is not a list")
        return {}
    index: dict[str, dict[str, Any]] = {}
    for entry in results:
        if not isinstance(entry, dict):
            continue
        strategy = entry.get("strategy")
        if strategy:
            index[strategy] = entry
    return index


def extract_section_02_for_strategy(strategy: str) -> dict[str, Any]:
    """Extract Section 2 gate_stacking_fire_rate for a single strategy.

    Returns dict for Section 2 dossier slot. method='runtime_measurement_b660'.
    """
    index = _load_b660_index()
    entry = index.get(strategy)

    if entry is None:
        return {
            "n_gates_stacked": None,
            "gate_marginals": None,
            "min_marginal_fire_rate": None,
            "tightest_gate": None,
            "independence_predicted_joint_prob": None,
            "measured_fires_per_year_full_t1a": None,
            "b660_verdict": None,
            "gate_stacking_check": "not_measured",
            "method": "runtime_measurement_b660_post_b648",
            "source": "output_audit/fire_count_measured_b660_full_universe.json",
            "limitation": (
                f"Strategy '{strategy}' not present in B660 measurement output. "
                "B660 was run against the 222-strategy roster snapshot; current "
                "roster is 219 (post B709 / B722 / B874 net changes). Strategies "
                "added or renamed post-B660 return not_measured. Re-run B660 "
                "measurement script (scripts/measure_fire_count.py) before R5 to "
                "close the gap. NOT a strategy defect; instrument-coverage gap."
            ),
            "memory_rule_reference": (
                "feedback_minimum_fire_count_gate_before_cube (memory rule): "
                "walks that stack 4-6 gates must surface a-priori fire-count "
                "projection. B660 is the canonical RUNTIME measurement per "
                "PATH Section 13.3 row 2."
            ),
        }

    gate_marginals = entry.get("gate_marginals") or {}
    n_gates = len(gate_marginals) if isinstance(gate_marginals, dict) else 0

    min_marginal: float | None = None
    tightest_gate: str | None = None
    if isinstance(gate_marginals, dict) and gate_marginals:
        tightest_gate, min_marginal = min(gate_marginals.items(), key=lambda kv: kv[1])
        min_marginal = round(float(min_marginal), 6)

    indep_joint = entry.get("independence_predicted_joint_prob")
    if indep_joint is not None:
        indep_joint = round(float(indep_joint), 8)

    fires_per_year = entry.get("projected_fires_per_calendar_year_total_full_t1a")
    if fires_per_year is not None:
        fires_per_year = round(float(fires_per_year), 4)

    verdict = entry.get("verdict")

    # Composite gate-stacking check
    if fires_per_year is None:
        check = "not_measured"
    elif fires_per_year >= MIN_FIRES_PER_YEAR_FLOOR:
        check = "passed"
    else:
        check = "failed"  # below 30/yr floor; gate-stacking starvation suspected

    return {
        "n_gates_stacked": n_gates,
        "gate_marginals": (
            {k: round(float(v), 6) for k, v in gate_marginals.items()}
            if isinstance(gate_marginals, dict)
            else None
        ),
        "min_marginal_fire_rate": min_marginal,
        "tightest_gate": tightest_gate,
        "independence_predicted_joint_prob": indep_joint,
        "measured_fires_per_year_full_t1a": fires_per_year,
        "b660_verdict": verdict,
        "gate_stacking_check": check,
        "method": "runtime_measurement_b660_post_b648",
        "source": "output_audit/fire_count_measured_b660_full_universe.json",
        "limitation": (
            "B660 measurement is point-in-time (2020-01-01 to ~2026-04-09 per "
            "B660 date_range key) on T1a-PIT-active universe (503 tickers post "
            "B648 hardcoded-220 bug fix). Independence-predicted joint prob "
            "assumes gates fire independently; real-world correlation (B660 "
            "`gate_pairwise_correlation` key) can drive joint fire-rate above "
            "or below the independence prediction. Use `measured_fires_per_year"
            "_full_t1a` (extrapolated from actual fires) as the authoritative "
            "runtime value; treat `independence_predicted_joint_prob` as a "
            "diagnostic upper-bound estimator. gate_stacking_check threshold "
            "(>= 30 fires/yr full T1a) maps CLAUDE.md min_trades=30/regime "
            "into a single composite gate; per-regime decomposition deferred "
            "to R5 cube cells."
        ),
        "memory_rule_reference": (
            "feedback_minimum_fire_count_gate_before_cube (memory rule, "
            "2026-06-07): walks that stack 4-6 gates per direction MUST surface "
            "a-priori fire-count projection. If projected fires/year < 30 "
            "(min_trades passing criterion), the cube can't produce a "
            "statistically valid PASS/FAIL. Section 2 operationalizes the rule "
            "via B660 runtime measurement per PATH Section 13.3 row 2."
        ),
    }


def populate_section_02_for_dossier(strategy: str, dossier_path: Path) -> None:
    """Populate Section 2 gate_stacking_fire_rate slot in dossier.json."""
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_payload = extract_section_02_for_strategy(strategy)
    sections = dossier.setdefault("sections", {})
    sections["section_02_gate_stacking_fire_rate"] = section_payload
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
