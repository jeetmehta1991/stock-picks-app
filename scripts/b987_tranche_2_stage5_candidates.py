"""B987 (2026-06-21): Phase P1 Stage 5 Tranche 2 candidate re-extraction.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13 + Council 91 Option-6
# HYBRID owner-approved 2026-06-21 'Approve your recommendation. Proceed
# council this.'

PURPOSE
-------
Re-extract Stage 5 candidates from R4 optimizer output beyond Tranche 1
PASS-cell threshold. Tranche 1 captured Sharpe >= 0.30 PASS cells (15
total; #71-75 = 5 candidates per B834). Tranche 2 broadens to Sharpe
0.20-0.30 tier (lower-confidence cube cells; still cube-empirical).

CRITICAL PRE-FLIGHT FINDING:
  Tranche 1 #71+#72 ALREADY SHIPPED via B835 (verified via git log
  c340df6be + backtest/config.py:306,309). CLAUDE.md banner +
  EXECUTION_QUEUE B834 row stale. Council 91 brief based on stale
  banner; Tranche 1 actually 5-of-5 COMPLETE (B835 + B886).

Per Council 76 banner-verification precedent + Council 89/90 honest-
finding pivot: re-scope to Tranche 2 directly.

Method:
  - Walk output_optimization_candidates_R4_2026_06_16/ JSONs
  - For each strategy: collect cube cells with Sharpe in [0.20, 0.30)
    (Tranche 2 tier; below Tranche 1 0.30+ PASS threshold)
  - Filter by 5-gate PASS where possible (n>=30 + 4 other gates)
  - Exclude strategies ALREADY in STRATEGY_EXIT_OVERRIDE (Tranche 1 +
    legacy entries)
  - Output: output_audit/b987_tranche_2_stage5_candidates.json

Per Council 91 forecast: 5-15 candidates expected in this tier.
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

R4_OPTIMIZER_DIR = REPO / "output_optimization_candidates_R4_2026_06_16"
OUT_PATH = REPO / "output_audit" / "b987_tranche_2_stage5_candidates.json"

# Tranche 2 Sharpe band: between Tranche 1 cutoff (0.30) and lower
# minimum (0.20). Lower than 0.20 = too weak for Stage 5 confidence.
SHARPE_TRANCHE_2_MIN = 0.20
SHARPE_TRANCHE_2_MAX = 0.30


def _load_strategy_already_overridden() -> set[str]:
    """Strategies already in STRATEGY_EXIT_OVERRIDE (Tranche 1 + legacy)."""
    from backtest.config import STRATEGY_EXIT_OVERRIDE
    return set(STRATEGY_EXIT_OVERRIDE.keys())


def _extract_tranche_2_from_strategy_json(path: Path) -> list[dict[str, Any]]:
    """Walk strategy JSON; collect cells with Sharpe in [0.20, 0.30)."""
    try:
        data = json.load(open(path))
    except Exception as e:
        logger.warning("Failed to parse %s: %s", path.name, e)
        return []
    strategy_name = data.get("strategy") or path.stem
    candidates = []
    # B987 fix: R4 optimizer JSONs use dimension_d_exit.ranked list
    # (verified via pre-flight on adx_initiation.json).
    dim_d = data.get("dimension_d_exit", {})
    cells = dim_d.get("ranked", []) if isinstance(dim_d, dict) else []
    if not isinstance(cells, list):
        return []
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        sharpe = cell.get("sharpe") or cell.get("sharpe_ratio") or 0.0
        try:
            sharpe_f = float(sharpe)
        except (TypeError, ValueError):
            continue
        if not (SHARPE_TRANCHE_2_MIN <= sharpe_f < SHARPE_TRANCHE_2_MAX):
            continue
        # Pass gates if available
        n = cell.get("n") or cell.get("n_trades") or 0
        try:
            n_int = int(n)
        except (TypeError, ValueError):
            continue
        if n_int < 30:
            continue
        verdict = cell.get("verdict", "")
        five_gate = cell.get("five_gate_pass") or cell.get("passes_5_gate")
        exit_method = cell.get("exit_method") or cell.get("exit")
        if not exit_method:
            continue
        # B987: PSR lives in gates dict per R4 schema
        gates = cell.get("gates", {}) if isinstance(cell.get("gates"), dict) else {}
        psr_pass = gates.get("psr_>=_0.95") if gates else None
        candidates.append({
            "strategy": strategy_name,
            "exit_method": exit_method,
            "n": n_int,
            "sharpe": round(sharpe_f, 4),
            "pf": cell.get("profit_factor"),
            "wr": cell.get("win_rate"),
            "psr_pass": bool(psr_pass) if psr_pass is not None else None,
            "verdict": verdict,
            "five_gate_pass": bool(five_gate),
        })
    return candidates


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if not R4_OPTIMIZER_DIR.exists():
        logger.error("R4 optimizer dir missing: %s", R4_OPTIMIZER_DIR)
        return 1
    already_overridden = _load_strategy_already_overridden()
    logger.info("Already-overridden strategies (Tranche 1 + legacy): %d", len(already_overridden))
    all_candidates: list[dict[str, Any]] = []
    json_files = sorted(R4_OPTIMIZER_DIR.glob("*.json"))
    logger.info("Walking %d R4 optimizer JSONs...", len(json_files))
    for jf in json_files:
        cands = _extract_tranche_2_from_strategy_json(jf)
        all_candidates.extend(cands)

    # Filter: exclude already-overridden + dedupe by (strategy, exit_method) keeping best Sharpe
    filtered = [c for c in all_candidates if c["strategy"] not in already_overridden]
    by_strategy: dict[str, dict[str, Any]] = {}
    for c in filtered:
        existing = by_strategy.get(c["strategy"])
        if existing is None or c["sharpe"] > existing["sharpe"]:
            by_strategy[c["strategy"]] = c
    tranche_2 = sorted(by_strategy.values(), key=lambda x: -x["sharpe"])

    n_candidates = len(tranche_2)
    five_gate_pass = sum(1 for c in tranche_2 if c["five_gate_pass"])

    # Verdict
    if n_candidates >= 5:
        verdict = "TRANCHE_2_VIABLE"
        narrative = f"{n_candidates} candidates surfaced; >=5 batch threshold met."
    elif n_candidates >= 1:
        verdict = "TRANCHE_2_PARTIAL"
        narrative = f"{n_candidates} candidates; under >=5 threshold; combine with Tranche 3 or accept partial."
    else:
        verdict = "TRANCHE_2_EMPTY"
        narrative = "No Tranche 2 candidates in Sharpe 0.20-0.30 tier; Stage 5 backlog exhausted from R4 data."

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump({
            "schema_version": "1.0",
            "batch": "B987",
            "council": "91_OPTION_6_HYBRID + 92_TRANCHE_2",
            "owner_directive": "Approve your recommendation. Proceed council this. (2026-06-21)",
            "source_dir": str(R4_OPTIMIZER_DIR.relative_to(REPO)),
            "sharpe_band": [SHARPE_TRANCHE_2_MIN, SHARPE_TRANCHE_2_MAX],
            "n_strategies_total_scanned": len(json_files),
            "n_already_overridden_excluded": len(already_overridden),
            "n_candidates_raw_in_band": len(all_candidates),
            "n_candidates_post_filter": n_candidates,
            "n_five_gate_pass": five_gate_pass,
            "verdict": verdict,
            "narrative": narrative,
            "tranche_2_candidates": tranche_2,
            "honest_finding_pre_flight": (
                "Tranche 1 #71+#72 ALREADY SHIPPED via B835 (git log c340df6be + "
                "backtest/config.py:306+309). CLAUDE.md banner stale; Council 91 "
                "Option-6 'ship #71+#72' is moot. Tranche 2 launch proceeds per "
                "Council 91 path-forward portion."
            ),
            "memory_rule_reference": (
                "Council 76 banner-verification precedent + Council 89/90 honest-"
                "finding pivot + feedback_audit_recommendations_against_existing_"
                "directives + feedback_path_c_min_batch_size + project_no_apriori_"
                "strategy_pruning + DO-NOT-DELETE."
            ),
        }, f, indent=2, default=str)

    logger.info("B987 TRANCHE 2 RE-EXTRACTION COMPLETE:")
    logger.info("  Strategies scanned: %d", len(json_files))
    logger.info("  Already-overridden (Tranche 1 + legacy): %d", len(already_overridden))
    logger.info("  Candidates raw in Sharpe band: %d", len(all_candidates))
    logger.info("  Candidates post-filter (dedupe + exclude overridden): %d", n_candidates)
    logger.info("  Five-gate PASS: %d / %d", five_gate_pass, n_candidates)
    logger.info("  Verdict: %s", verdict)
    logger.info("  Narrative: %s", narrative)
    if tranche_2:
        logger.info("  Top-10 candidates by Sharpe:")
        for c in tranche_2[:10]:
            pf_str = f"{c['pf']:.2f}" if c.get('pf') is not None else "?"
            logger.info("    %-40s %-25s n=%d Sharpe=%.3f PF=%s 5GP=%s",
                        c["strategy"], c["exit_method"], c["n"], c["sharpe"],
                        pf_str, c.get("five_gate_pass"))
    logger.info("Output: %s", OUT_PATH.relative_to(REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
