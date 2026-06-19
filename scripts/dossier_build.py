"""B933 (2026-06-19): Phase P1 Stream E dossier_build.py skeleton.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.2 (Phase P1 Stream E) +
# Section 13.3 (19 dossier sections) + Council 44 batch 1 design per
# owner directive 2026-06-19 Option A.

PURPOSE
-------
Per-strategy diagnostic dossier builder. Each strategy gets a JSON file
at `output_audit/dossiers/<strategy>/dossier.json` with 19 sections.
Sections are populated by Stream E batches (one batch per section or
per related-section group).

Per Council 38 First Principles:
- Sections are independent; can be populated in any order
- Each section's value: either validated parquet path OR null if not-yet-computed
- Stream D (Decision) consumes dossiers in batches of 5 per owner
- Stream V (Verification) runs pyramid per Stream E generator

Per Council 44 batch 1 scope:
- Commit 1 (THIS FILE): skeleton + JSON schema + evidence_store init
- Commit 2: self-test harness with KNOWN-BUG canaries
- Commit 3: Section 9 (R4 cube metrics) extractor
- Commits 4-6+: progressive section coverage

USAGE
-----
    # Initialize empty dossier for a strategy
    python scripts/dossier_build.py --init --strategy strat_NAME

    # Populate a specific section (Section 9 implemented B935)
    python scripts/dossier_build.py --section 9 --strategy strat_NAME

    # Populate ALL sections (long-running; future batches)
    python scripts/dossier_build.py --all --strategy strat_NAME

    # Populate section across all 218 strategies (batched)
    python scripts/dossier_build.py --section 9 --all-strategies

EVIDENCE STORE
--------------
Content-addressed parquet store at `evidence_store/<hash>/<section>.parquet`
where hash = sha256(strategy_name + section_id + as_of_date + producer_git_sha).
Reproducibility load-bearing for DEC #4 (OOS seal protocol).

This module ships the SKELETON only; section extractors live in
`backtest/diagnostics/section_NN_*.py` (added per-batch).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

logger = logging.getLogger(__name__)


DOSSIERS_DIR = REPO / "output_audit" / "dossiers"
EVIDENCE_STORE_DIR = REPO / "evidence_store"


# 20 dossier sections per PATH Section 13.3 + Council 45 (B934) addition of
# Section 9b "pre_cube_evidence" addressing R4=102 vs roster=219 drift.
# Section 9b is logically paired with Section 9 but stored separately to
# preserve content-addressed evidence_store layout.
DOSSIER_SECTIONS = [
    (1,  "wiring_trace_coverage",      "Wiring trace via coverage.py mode (NOT grep)"),
    (2,  "gate_stacking_fire_rate",    "Per-gate fire-rate + gate-stacking diagnostic"),
    (3,  "inverse_pair_empirical",     "Empirical inverse-pair probe (NOT literature)"),
    (4,  "redundancy_phi_matrix",      "Pairwise trade-day Jaccard redundancy matrix"),
    (5,  "regime_affinity_lineage",    "Git-log lineage of regime affinity changes"),
    (6,  "producer_state_event",       "Producer source extract + STATE/EVENT classification"),
    (7,  "temporal_coverage_probe",    "Per-year-per-strategy fire count (not mean)"),
    (8,  "data_source_asymmetry",      "Data-source asymmetry tag (B611 13F long-only pattern)"),
    (9,  "r4_cube_metrics",            "R4 cube metrics (all regimes + bootstrap 90% CI); NULL for post-R4 additions"),
    (10, "cost_sensitivity_ratio",     "Cost-sensitivity ratio (DEC-612)"),
    (11, "chow_break_point",           "Chow break-point test (DEC-613)"),
    (12, "adf_p_value",                "ADF stationarity p-value (DEC-614 mean-rev only)"),
    (13, "exit_axis_best_26",          "Exit-axis best-26 vector + dispersion + median + p25"),
    (14, "returns_autocorr_correction","Returns autocorrelation correction (Lo 2002)"),
    (15, "exit_profitability_fraction","Exit profitability fraction (>=40% exits profitable)"),
    (16, "negative_control_canary",    "Negative-control canary status (5 null strategies)"),
    (17, "soft_score_weight_calibration","Soft-score weight calibration via null distribution"),
    (18, "per_regime_sharpe_dispersion","Per-regime Sharpe dispersion (Simpson's paradox guard)"),
    (19, "closest_neighbor_cluster",   "Closest-passing-neighbor + family + cluster_id"),
    # B934 Council 45 addition (owner-approved): pre-cube evidence for post-R4 strategies
    (20, "pre_cube_evidence_9b",       "Pre-cube evidence for post-R4 additions: B907/B660 fire-count + B883 walk batch + EXPLORATORY/DORMANT + attribution narrative"),
]


# B934 Council 45 (owner-approved): r5_inclusion_criterion enum.
R5_INCLUSION_CRITERIA = (
    "r4_metrics_passed",              # In R4 cube AND passed PASSING_CRITERIA
    "pre_cube_evidence_sufficient",   # Post-R4 with B907/B660 fire-count + Stage 4 walk + EXPLORATORY tag
    "deferred",                       # Owner-explicit defer to next cube cycle
)


def _empty_dossier_schema(strategy: str) -> dict[str, Any]:
    """Return a 20-section dossier with null values for not-yet-computed sections.

    B934 Council 45 (owner-approved): schema bumped from 19 to 20 sections to
    accommodate Section 9b (pre_cube_evidence) addressing R4=102 vs roster=219
    drift. r5_inclusion_criterion field added per Council 45 verdict.
    """
    return {
        "schema_version": "1.1",
        "schema_source": "PATH_TO_PHASE_1B_ALPHA.md Section 13.3 + B934 Council 45 (Section 9b + r5_inclusion_criterion)",
        "strategy": strategy,
        "dossier_build_batch": "B934",
        "phase": "P1",
        "r5_inclusion_criterion": None,  # one of R5_INCLUSION_CRITERIA after Section 9 + 9b populated
        "sections": {
            f"section_{n:02d}_{key}": None
            for n, key, _desc in DOSSIER_SECTIONS
        },
        "section_metadata": [
            {"id": n, "key": key, "description": desc}
            for n, key, desc in DOSSIER_SECTIONS
        ],
    }


def _compute_evidence_hash(
    strategy: str,
    section_key: str,
    as_of: date,
    producer_git_sha: str = "",
) -> str:
    """Content-addressed hash for evidence_store parquet locations.

    sha256(strategy_name | section_key | as_of_date | producer_git_sha)

    The producer_git_sha allows reproducibility tracking across code
    changes. When producer code mutates, hash changes -> old evidence
    preserved + new evidence built.
    """
    payload = f"{strategy}|{section_key}|{as_of.isoformat()}|{producer_git_sha}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def init_dossier(strategy: str, overwrite: bool = False) -> Path:
    """Initialize an empty 19-section dossier JSON for a strategy."""
    DOSSIERS_DIR.mkdir(parents=True, exist_ok=True)
    strat_dir = DOSSIERS_DIR / strategy
    strat_dir.mkdir(exist_ok=True)
    dossier_path = strat_dir / "dossier.json"
    if dossier_path.exists() and not overwrite:
        logger.info("Dossier already exists for %s (use --overwrite to replace)", strategy)
        return dossier_path
    schema = _empty_dossier_schema(strategy)
    with open(dossier_path, "w") as f:
        json.dump(schema, f, indent=2, default=str)
    logger.info("Initialized dossier: %s", dossier_path)
    return dossier_path


def init_evidence_store() -> Path:
    """Initialize evidence_store directory with version-pinned manifest."""
    EVIDENCE_STORE_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = EVIDENCE_STORE_DIR / "manifest.json"
    if not manifest_path.exists():
        manifest = {
            "schema_version": "1.0",
            "store_format": "content-addressed parquet",
            "hash_algorithm": "sha256",
            "hash_truncate_chars": 16,
            "hash_inputs": ["strategy_name", "section_key", "as_of_date", "producer_git_sha"],
            "created_batch": "B933",
            "phase": "P1",
            "dec_dependency": "DEC #4 OOS seal protocol (reproducibility load-bearing)",
        }
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        logger.info("Initialized evidence_store manifest: %s", manifest_path)
    return EVIDENCE_STORE_DIR


def list_strategies_for_dossier() -> list[str]:
    """List ALL_STRATEGIES from screener.py registry."""
    from backtest.signals.screener import ALL_STRATEGIES
    return sorted(ALL_STRATEGIES.keys())


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--init", action="store_true",
        help="Initialize empty dossier (--strategy required)",
    )
    parser.add_argument(
        "--init-all", action="store_true",
        help="Initialize empty dossier for ALL 218 strategies",
    )
    parser.add_argument(
        "--strategy", default=None,
        help="Single strategy name (registry key)",
    )
    parser.add_argument(
        "--all-strategies", action="store_true",
        help="Operate on ALL strategies",
    )
    parser.add_argument(
        "--section", type=int, default=None,
        help="Section ID 1-19 (per DOSSIER_SECTIONS) to populate",
    )
    parser.add_argument(
        "--all-sections", action="store_true",
        help="Populate ALL sections (long-running)",
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing dossiers (default skip)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Verbose logging",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    # Initialize evidence_store always (idempotent)
    init_evidence_store()

    if args.init_all:
        strategies = list_strategies_for_dossier()
        logger.info("Initializing dossiers for %d strategies...", len(strategies))
        for strat in strategies:
            init_dossier(strat, overwrite=args.overwrite)
        logger.info("DONE: %d dossiers initialized", len(strategies))
        return 0

    if args.init:
        if not args.strategy:
            logger.error("--init requires --strategy NAME")
            return 1
        init_dossier(args.strategy, overwrite=args.overwrite)
        return 0

    if args.section:
        # Section extractors land in subsequent batches; this commit ships
        # the skeleton + schema only.
        logger.error(
            "Section %d extractor not yet implemented (Council 44 batch 1 scope: skeleton + "
            "self-test + Section 9). Future batches add other section extractors per PATH 13.3.",
            args.section,
        )
        return 2

    logger.info("Usage: --init [--strategy NAME] OR --init-all OR --section N")
    return 0


if __name__ == "__main__":
    sys.exit(main())
