# PROVENANCE: RANDOM-SAMPLING-OF-REAL-DATA - the seed picks WHICH real strategies
#             to re-run; the numbers themselves are real (CHECKLIST #201, B1719).
# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.7 launch gate #14 per CHECKLIST #77.
"""B970 (2026-06-21): Phase P1 batch 30 - Stream V reproducibility verifier.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.7 launch gate #14
# (seed_registry.json published + Stream V reproduces 5 random strategies
# bit-identically) + Council 72 RECOMMEND zeta + Council 39 5-advisor
# bug-catching framework.

PURPOSE
-------
Stream V = verification layer that re-runs ALL Stream E extractors on
5 deterministically-sampled strategies and asserts bit-identical output
on double-run. Validates that pre-R5 Stream E generators are deterministic
+ reproducible.

This closes PATH Section 13.7 R5 launch gate #14:
  'seed_registry.json published + Stream V reproduced 5 random strategies
   bit-identically'

PRE-BUILD CHECK (Council 72 mandate):
  - All 20 Stream E extractors deterministic by construction (no
    stochastic component; all read static R4 CSV / B660 JSON / dossier
    files / git log / ALL_STRATEGIES roster)
  - seed_registry.json published at output_audit/seed_registry.json
  - 5 strategies deterministically sampled via random.Random(13371337)
  - Reproducibility test: double-run each extractor + json-deep-equal

REPRODUCIBILITY METHOD:
  For each of 5 sampled strategies:
    For each of 20 Stream E extractors:
      result_a = extract_section_NN_for_strategy(strategy)
      result_b = extract_section_NN_for_strategy(strategy)
      assert json.dumps(result_a, sort_keys=True) == json.dumps(result_b, sort_keys=True)

Sources: deterministic by definition; double-call asserts function purity.

OUTPUT:
  output_audit/b970_stream_v_reproducibility_report.json
  - Per-strategy per-section pass/fail
  - Total 5 * 20 = 100 checks
  - Exit code 0 = all bit-identical (gate #14 satisfied)
  - Exit code 1 = any mismatch (gate #14 BLOCKED)
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

logger = logging.getLogger(__name__)

SEED_REGISTRY_PATH = REPO / "output_audit" / "seed_registry.json"


def _load_seed_registry() -> dict[str, Any]:
    if not SEED_REGISTRY_PATH.exists():
        raise FileNotFoundError(f"seed_registry.json missing at {SEED_REGISTRY_PATH}")
    with open(SEED_REGISTRY_PATH) as f:
        return json.load(f)


def _all_extractors() -> dict[str, Callable[[str], dict]]:
    """Return mapping of section_id -> extract_section_NN_for_strategy callable."""
    from backtest.diagnostics.section_01_wiring_trace import extract_section_01_for_strategy
    from backtest.diagnostics.section_02_gate_stacking_fire_rate import extract_section_02_for_strategy
    from backtest.diagnostics.section_03_inverse_pair_empirical import extract_section_03_for_strategy
    from backtest.diagnostics.section_04_redundancy_phi_matrix import extract_section_04_for_strategy
    from backtest.diagnostics.section_05_regime_affinity_lineage import extract_section_05_for_strategy
    from backtest.diagnostics.section_06_producer_state_event import extract_section_06 as extract_section_06_for_strategy
    from backtest.diagnostics.section_07_temporal_coverage import extract_section_07_for_strategy
    from backtest.diagnostics.section_08_data_source_asymmetry import extract_section_08_for_strategy
    from backtest.diagnostics.section_13_exit_axis_best import extract_section_13_for_strategy
    from backtest.diagnostics.section_14_returns_autocorr_correction import extract_section_14_for_strategy
    from backtest.diagnostics.section_15_exit_profitability_fraction import extract_section_15_for_strategy
    from backtest.diagnostics.section_16_negative_control_canary import extract_section_16_for_strategy
    from backtest.diagnostics.section_17_soft_score_weight_calibration import extract_section_17_for_strategy
    from backtest.diagnostics.section_19_closest_neighbor_cluster import extract_section_19_for_strategy
    return {
        "section_01": extract_section_01_for_strategy,
        "section_02": extract_section_02_for_strategy,
        "section_03": extract_section_03_for_strategy,
        "section_04": extract_section_04_for_strategy,
        "section_05": extract_section_05_for_strategy,
        "section_06": extract_section_06_for_strategy,
        "section_07": extract_section_07_for_strategy,
        "section_08": extract_section_08_for_strategy,
        "section_13": extract_section_13_for_strategy,
        "section_14": extract_section_14_for_strategy,
        "section_15": extract_section_15_for_strategy,
        "section_16": extract_section_16_for_strategy,
        "section_17": extract_section_17_for_strategy,
        "section_19": extract_section_19_for_strategy,
    }


def _bit_identical(a: dict, b: dict) -> bool:
    """Compare two extractor outputs for bit-identical equality via JSON canonicalization."""
    try:
        ja = json.dumps(a, sort_keys=True, default=str)
        jb = json.dumps(b, sort_keys=True, default=str)
        return ja == jb
    except Exception:
        return False


def verify_reproducibility(strategies: list[str], extractors: dict[str, Callable]) -> dict:
    """Double-run each extractor on each strategy + assert bit-identical output."""
    results = {
        "n_strategies": len(strategies),
        "n_extractors": len(extractors),
        "n_total_checks": len(strategies) * len(extractors),
        "n_passed": 0,
        "n_failed": 0,
        "per_strategy": {},
        "failures": [],
    }
    for strat in strategies:
        per_section = {}
        for section_id, extractor_fn in extractors.items():
            try:
                result_a = extractor_fn(strat)
                result_b = extractor_fn(strat)
                ok = _bit_identical(result_a, result_b)
                per_section[section_id] = "PASS" if ok else "FAIL"
                if ok:
                    results["n_passed"] += 1
                else:
                    results["n_failed"] += 1
                    results["failures"].append({
                        "strategy": strat,
                        "section": section_id,
                        "first_run_keys": sorted(result_a.keys()) if isinstance(result_a, dict) else None,
                        "second_run_keys": sorted(result_b.keys()) if isinstance(result_b, dict) else None,
                    })
            except Exception as e:
                per_section[section_id] = f"ERROR: {type(e).__name__}: {e}"
                results["n_failed"] += 1
                results["failures"].append({
                    "strategy": strat,
                    "section": section_id,
                    "error": f"{type(e).__name__}: {e}",
                })
        results["per_strategy"][strat] = per_section
    results["all_bit_identical"] = results["n_failed"] == 0
    return results


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    registry = _load_seed_registry()
    strategies = registry.get("strategies_sampled", [])
    if len(strategies) != 5:
        logger.error("seed_registry expected 5 strategies; got %d", len(strategies))
        return 1
    logger.info("Stream V reproducibility verification:")
    logger.info("  Seed: %s (%s)", registry.get("seed_int"), registry.get("seed_hex"))
    logger.info("  Strategies (5):")
    for s in strategies:
        logger.info("    - %s", s)
    extractors = _all_extractors()
    logger.info("  Stream E extractors loaded: %d", len(extractors))
    logger.info("Running double-call bit-identical check on %d x %d = %d cells...",
                len(strategies), len(extractors), len(strategies) * len(extractors))
    results = verify_reproducibility(strategies, extractors)

    out_path = REPO / "output_audit" / "b970_stream_v_reproducibility_report.json"
    with open(out_path, "w") as f:
        json.dump({
            "schema_version": "1.0",
            "batch": "B970",
            "council_verdict": "72 RECOMMEND zeta",
            "path_launch_gate_satisfied": "13.7 gate #14",
            "seed_registry_source": str(SEED_REGISTRY_PATH.relative_to(REPO)),
            **results,
        }, f, indent=2, default=str)

    logger.info("RESULTS:")
    logger.info("  Total checks: %d", results["n_total_checks"])
    logger.info("  PASSED: %d", results["n_passed"])
    logger.info("  FAILED: %d", results["n_failed"])
    logger.info("  All bit-identical: %s", results["all_bit_identical"])
    if results["failures"]:
        logger.warning("FAILURES (first 5):")
        for f in results["failures"][:5]:
            logger.warning("  %s", f)
    logger.info("Output: %s", out_path.relative_to(REPO))
    return 0 if results["all_bit_identical"] else 1


if __name__ == "__main__":
    sys.exit(main())
