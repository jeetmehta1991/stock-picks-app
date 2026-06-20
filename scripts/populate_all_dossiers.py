"""B942 (2026-06-20): Phase P1 batch 4 commit 1 - Stream E full-roster population.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.2 + Council 48 batch 4 commit 1 +
# Outsider validation-at-scale mandate per owner directive 2026-06-20 Option A.

PURPOSE
-------
Populate dossiers for ALL 219 strategies with currently-built sections:
- Section 6 (B937 STATE/EVENT classification)
- Section 9 (B935 R4 cube metrics TWO-TRACK)
- Section 9b (B936 pre-cube evidence)

This is the Stream E validation-at-scale that Council 48 deemed mandatory
BEFORE adding more extractors. Surfaces drift / coverage gaps / schema
issues that B934 self-test on KNOWN-BUG canaries cannot catch.

USAGE
-----
    python scripts/populate_all_dossiers.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

logger = logging.getLogger(__name__)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    from scripts.dossier_build import list_strategies_for_dossier, DOSSIERS_DIR
    from backtest.diagnostics.section_06_producer_state_event import populate_section_06_for_dossier
    from backtest.diagnostics.section_09_r4_cube_metrics import populate_section_09_for_dossier
    from backtest.diagnostics.section_09b_pre_cube_evidence import populate_section_09b_for_dossier
    # B943 + B944 additions:
    from backtest.diagnostics.section_r4_passthrough import populate_r4_passthrough_sections_for_dossier
    from backtest.diagnostics.r5_inclusion_criterion import set_r5_inclusion_criterion_for_dossier

    strategies = list_strategies_for_dossier()
    logger.info("Populating sections 6 / 9 / 9b / 10 / 11 / 12 / 18 + r5_inclusion_criterion for %d strategies...", len(strategies))

    from collections import Counter
    stats = {
        "total": len(strategies),
        "section_6_populated": 0,
        "section_6_errors": 0,
        "section_9_populated": 0,
        "section_9_errors": 0,
        "section_9b_populated": 0,
        "section_9b_errors": 0,
        "r4_passthrough_populated": 0,
        "r4_passthrough_errors": 0,
        "criterion_set": 0,
        "criterion_errors": 0,
        "criterion_distribution": Counter(),
        "drift_findings": [],
    }

    for i, strat in enumerate(strategies):
        dossier_path = DOSSIERS_DIR / strat / "dossier.json"
        if not dossier_path.exists():
            stats["drift_findings"].append(f"missing dossier: {strat}")
            continue
        try:
            populate_section_06_for_dossier(strat, dossier_path)
            stats["section_6_populated"] += 1
        except Exception as e:
            stats["section_6_errors"] += 1
            stats["drift_findings"].append(f"section_6:{strat}: {type(e).__name__}: {e}")
        try:
            populate_section_09_for_dossier(strat, dossier_path)
            stats["section_9_populated"] += 1
        except Exception as e:
            stats["section_9_errors"] += 1
            stats["drift_findings"].append(f"section_9:{strat}: {type(e).__name__}: {e}")
        try:
            populate_section_09b_for_dossier(strat, dossier_path)
            stats["section_9b_populated"] += 1
        except Exception as e:
            stats["section_9b_errors"] += 1
            stats["drift_findings"].append(f"section_9b:{strat}: {type(e).__name__}: {e}")
        # B943: R4 pass-through bundle
        try:
            populate_r4_passthrough_sections_for_dossier(strat, dossier_path)
            stats["r4_passthrough_populated"] += 1
        except Exception as e:
            stats["r4_passthrough_errors"] += 1
            stats["drift_findings"].append(f"r4_passthrough:{strat}: {type(e).__name__}: {e}")
        # B944: r5_inclusion_criterion setter (must run AFTER all dependency sections)
        try:
            criterion = set_r5_inclusion_criterion_for_dossier(dossier_path)
            stats["criterion_set"] += 1
            stats["criterion_distribution"][criterion["value"]] += 1
        except Exception as e:
            stats["criterion_errors"] += 1
            stats["drift_findings"].append(f"criterion:{strat}: {type(e).__name__}: {e}")

        if (i + 1) % 50 == 0:
            logger.info("Progress: %d/%d (%.1f%%)", i + 1, len(strategies),
                        100.0 * (i + 1) / len(strategies))

    logger.info("Population COMPLETE:")
    logger.info("  Section 6:        %d populated / %d errors", stats["section_6_populated"], stats["section_6_errors"])
    logger.info("  Section 9:        %d populated / %d errors", stats["section_9_populated"], stats["section_9_errors"])
    logger.info("  Section 9b:       %d populated / %d errors", stats["section_9b_populated"], stats["section_9b_errors"])
    logger.info("  Sections 10/11/12/18: %d populated / %d errors", stats["r4_passthrough_populated"], stats["r4_passthrough_errors"])
    logger.info("  r5_inclusion_criterion: %d set / %d errors", stats["criterion_set"], stats["criterion_errors"])
    logger.info("  CRITERION DISTRIBUTION:")
    for criterion, count in stats["criterion_distribution"].most_common():
        logger.info("    %s: %d (%.1f%%)", criterion, count, 100.0 * count / stats["total"])
    if stats["drift_findings"]:
        logger.warning("Drift findings (%d):", len(stats["drift_findings"]))
        for finding in stats["drift_findings"][:20]:
            logger.warning("  %s", finding)
        if len(stats["drift_findings"]) > 20:
            logger.warning("  ... and %d more", len(stats["drift_findings"]) - 20)
    return 0 if all(stats[k] == 0 for k in ("section_6_errors", "section_9_errors", "section_9b_errors")) else 1


if __name__ == "__main__":
    sys.exit(main())
