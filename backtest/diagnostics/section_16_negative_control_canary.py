# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 16 per CHECKLIST #77.
"""B965 (2026-06-20): Phase P1 batch 25 - Section 16 negative_control_canary.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 16 + Council 67 4/4 verdict
# per owner directive 2026-06-20 'Continue council this. Continue without
# stopping till all sections in P1 are done.' per CHECKLIST #77.

PURPOSE
-------
Section 16 = Negative-control canary status per PATH Section 13.3 row 16:
  '5 null strategies injected pre-Stream-E; framework must identify them;
   if not, framework miscalibrated.'

For each strategy in the dossier:
  - If strategy is one of the 5 null canaries: report canary_status (whether
    framework currently identifies it as null via Section 2/14/15 gates).
  - If strategy is NOT a null canary: report dependency on canary verdict
    (framework-calibration prerequisite).

PRE-BUILD CHECK (Council 67 Executor + Contrarian hardening, executed):
  scripts/inject_null_strategies.py: BUILT B965 same turn (RUNNABLE; 5
    concrete null specs; NULL_STRATEGY_REGISTRY exposed).
  NULL_STRATEGY_NAMES tuple: ('null_random_long_p05', 'null_shuffled_signal_long',
    'null_lagged_self_long', 'null_pure_noise_gauss', 'null_coin_flip_daily').
  Null strategies NOT YET in R5 trade_log (R5 cube not launched; pre-R5 status).
  Section 2 (B962) / Section 14 (B963) / Section 15 (B964) extractors all
    handle 'not_measured' gracefully -> Section 16 can compose calibration
    verdict once R5 trade_log lands.
  Contrarian hardening: this is NOT a schema-only IOU; the inject script is
    a runnable artifact today. Section 16 ships the framework-side aggregator.
  Build APPROVED.

METHODOLOGY:
  1. Look up strategy in NULL_STRATEGY_NAMES.
  2. If null canary:
     - Pull Section 2/14/15 verdicts from cached extractors.
     - canary_correctly_identified = any gate returned 'failed' status.
     - Pre-R5: 'pending_r5_cube_launch' (no R5 trade_log yet).
  3. If real strategy:
     - canary_status = composite of all 5 canary identifications.
     - framework_calibrated = (5/5 nulls correctly identified as failed).
  4. Report calibration verdict + per-canary breakdown.

OUTPUT SCHEMA per strategy:
{
  "is_null_canary": bool,
  "null_strategy_name": str | None,                   # if is_null_canary
  "canary_correctly_identified": bool | None,         # if is_null_canary
  "canary_failed_gates": list[str],                   # if is_null_canary
  "n_null_canaries_total": 5,                         # always 5 per design
  "n_null_canaries_identified": int | None,           # pre-R5: 0; post-R5: 0-5
  "framework_calibrated": bool | None,                # pre-R5: None
  "canary_status_overall": str,                       # pre-R5/passed/failed
  "null_strategy_names": list[str],                   # canonical 5
  "injection_script": str,                            # path to inject script
  "method": "static_canary_protocol_pre_r5",
  "source": "scripts/inject_null_strategies.py + B962/B963/B964 extractors",
  "limitation": str,
  "memory_rule_reference": str,
}
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent.parent
INJECTION_SCRIPT = REPO / "scripts" / "inject_null_strategies.py"


def _get_null_strategy_names() -> tuple[str, ...]:
    """Pull canonical 5 null strategy names from inject script."""
    try:
        # Defer import to avoid hard dependency at module load time
        from scripts.inject_null_strategies import NULL_STRATEGY_NAMES
        return NULL_STRATEGY_NAMES
    except Exception as e:
        logger.warning("Cannot import NULL_STRATEGY_NAMES from inject script: %s", e)
        # Fallback to hardcoded canonical names (must match inject script)
        return (
            "null_random_long_p05",
            "null_shuffled_signal_long",
            "null_lagged_self_long",
            "null_pure_noise_gauss",
            "null_coin_flip_daily",
        )


def _check_canary_identified(strategy: str) -> tuple[bool, list[str]]:
    """For a null canary strategy, check if framework gates identify it as failed.

    Returns (is_identified, list_of_failed_gates). Pulls Section 2/14/15 verdicts.
    Pre-R5: all gates return 'not_measured' -> not_identified.
    """
    failed_gates: list[str] = []
    try:
        from backtest.diagnostics.section_02_gate_stacking_fire_rate import extract_section_02_for_strategy
        s2 = extract_section_02_for_strategy(strategy)
        if s2.get("gate_stacking_check") == "failed":
            failed_gates.append("section_02_gate_stacking_fire_rate")
    except Exception as e:
        logger.warning("Section 2 lookup failed for %s: %s", strategy, e)
    try:
        from backtest.diagnostics.section_14_returns_autocorr_correction import extract_section_14_for_strategy
        s14 = extract_section_14_for_strategy(strategy)
        if s14.get("corrected_sharpe_overall_re_pass") is False:
            failed_gates.append("section_14_returns_autocorr_correction")
    except Exception as e:
        logger.warning("Section 14 lookup failed for %s: %s", strategy, e)
    try:
        from backtest.diagnostics.section_15_exit_profitability_fraction import extract_section_15_for_strategy
        s15 = extract_section_15_for_strategy(strategy)
        if s15.get("exit_profitability_check") == "failed":
            failed_gates.append("section_15_exit_profitability_fraction")
    except Exception as e:
        logger.warning("Section 15 lookup failed for %s: %s", strategy, e)
    return (len(failed_gates) > 0, failed_gates)


def extract_section_16_for_strategy(strategy: str) -> dict[str, Any]:
    """Extract Section 16 negative_control_canary for a single strategy.

    method='static_canary_protocol_pre_r5'.
    """
    null_names = _get_null_strategy_names()
    is_null = strategy in null_names

    n_total = len(null_names)

    if is_null:
        identified, failed_gates = _check_canary_identified(strategy)
        return {
            "is_null_canary": True,
            "null_strategy_name": strategy,
            "canary_correctly_identified": identified,
            "canary_failed_gates": failed_gates,
            "n_null_canaries_total": n_total,
            "n_null_canaries_identified": None,  # only meaningful at aggregate level
            "framework_calibrated": None,         # only meaningful at aggregate level
            "canary_status_overall": (
                "passed" if identified
                else "pending_r5_cube_launch"
            ),
            "null_strategy_names": list(null_names),
            "injection_script": str(INJECTION_SCRIPT.relative_to(REPO)),
            "method": "static_canary_protocol_pre_r5",
            "source": "scripts/inject_null_strategies.py + B962/B963/B964 extractors",
            "limitation": (
                "Pre-R5: null strategies are REGISTERED-READY via "
                "scripts/inject_null_strategies.py (5 concrete specs; runnable "
                "today via `python -m scripts.inject_null_strategies "
                "--verify-registration`) but NOT YET in R5 trade_log. Section 2/"
                "14/15 verdicts return 'not_measured' pre-R5. Post-R5: gates "
                "should classify the null as 'failed' on >=1 axis; if not, "
                "framework is over-permissive (Type 1 error)."
            ),
            "memory_rule_reference": (
                "Council 67 Contrarian hardening (B965): protocol stub must be "
                "ACTIONABLE not theater. inject_null_strategies.py is RUNNABLE "
                "today with 5 concrete null specs (Bernoulli p=0.05/0.5, "
                "shuffled signal, lagged self, pure-noise Gaussian). "
                "feedback_no_write_only_md_files: this file is consumed by "
                "Section 16 extractor + R5 ALL_STRATEGIES injection."
            ),
        }

    # Real strategy: report on aggregate canary status
    # Pre-R5: framework_calibrated = None (cannot evaluate without R5 trade_log
    # on null strategies). Post-R5: count how many of the 5 nulls were
    # correctly classified as failed.
    n_identified: int | None = None
    framework_calibrated: bool | None = None
    canary_status_overall = "pending_r5_cube_launch"
    aggregate_failed_gates: dict[str, list[str]] = {}

    # Best-effort aggregate check pre-R5 (will all return False without R5 data)
    try:
        n_identified = 0
        for null_name in null_names:
            ident, gates = _check_canary_identified(null_name)
            if ident:
                n_identified += 1
            aggregate_failed_gates[null_name] = gates
        if n_identified == n_total:
            framework_calibrated = True
            canary_status_overall = "framework_calibrated"
        elif n_identified > 0:
            framework_calibrated = False
            canary_status_overall = (
                f"framework_partially_calibrated_{n_identified}_of_{n_total}"
            )
        else:
            framework_calibrated = None
            canary_status_overall = "pending_r5_cube_launch"
    except Exception as e:
        logger.warning("Aggregate canary check failed: %s", e)

    return {
        "is_null_canary": False,
        "null_strategy_name": None,
        "canary_correctly_identified": None,
        "canary_failed_gates": [],
        "n_null_canaries_total": n_total,
        "n_null_canaries_identified": n_identified,
        "framework_calibrated": framework_calibrated,
        "canary_status_overall": canary_status_overall,
        "null_strategy_names": list(null_names),
        "injection_script": str(INJECTION_SCRIPT.relative_to(REPO)),
        "method": "static_canary_protocol_pre_r5",
        "source": "scripts/inject_null_strategies.py + B962/B963/B964 extractors",
        "limitation": (
            "Pre-R5: framework_calibrated is None for ALL real strategies "
            "until R5 cube runs the 5 null canaries. Post-R5, all 219 "
            "strategy dossiers see the SAME aggregate calibration verdict "
            "(framework-wide, not per-strategy). Per-strategy field is_null"
            "_canary distinguishes the 5 nulls themselves from the 219 reals. "
            "Injection script scripts/inject_null_strategies.py is runnable "
            "today; integration with ALL_STRATEGIES is deferred to owner-"
            "decision pre-R5 launch (avoid contaminating R4/in-flight runs)."
        ),
        "memory_rule_reference": (
            "Council 67 Contrarian + Council 60 honest framing (B965): ship "
            "actionable injection artifact + extractor pre-R5; framework_"
            "calibrated verdict resolves post-R5 cube + inject. "
            "feedback_no_write_only_md_files."
        ),
    }


def populate_section_16_for_dossier(strategy: str, dossier_path: Path) -> None:
    """Populate Section 16 negative_control_canary slot in dossier.json."""
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_payload = extract_section_16_for_strategy(strategy)
    sections = dossier.setdefault("sections", {})
    sections["section_16_negative_control_canary"] = section_payload
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
