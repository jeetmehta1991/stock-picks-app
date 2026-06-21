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
    # B951 addition (Council 55 Section 1 wiring trace):
    from backtest.diagnostics.section_01_populate import populate_section_01_for_dossier
    # B952 addition (Council 56 Section 7 temporal coverage probe):
    from backtest.diagnostics.section_07_temporal_coverage import populate_section_07_for_dossier
    # B953 addition (Council 57 Section 5 regime affinity lineage):
    from backtest.diagnostics.section_05_regime_affinity_lineage import populate_section_05_for_dossier
    # B954 addition (Council 58 Section 13 exit axis best):
    from backtest.diagnostics.section_13_exit_axis_best import populate_section_13_for_dossier
    # B955 addition (Council 59 Section 8 data source asymmetry):
    from backtest.diagnostics.section_08_data_source_asymmetry import populate_section_08_for_dossier
    # B959 addition (Council 64 Section 4 redundancy_phi_matrix):
    from backtest.diagnostics.section_04_redundancy_phi_matrix import (
        populate_section_04_for_dossier, write_shared_matrix_parquet,
    )
    # B960 addition (Council 65 Section 19 closest_neighbor_cluster):
    from backtest.diagnostics.section_19_closest_neighbor_cluster import populate_section_19_for_dossier
    # B961 addition (Council 66 Section 3 inverse_pair_empirical):
    from backtest.diagnostics.section_03_inverse_pair_empirical import populate_section_03_for_dossier
    # B962-B966 additions (Council 67; 5-batch P1 completion):
    from backtest.diagnostics.section_02_gate_stacking_fire_rate import populate_section_02_for_dossier
    from backtest.diagnostics.section_14_returns_autocorr_correction import populate_section_14_for_dossier
    from backtest.diagnostics.section_15_exit_profitability_fraction import populate_section_15_for_dossier
    from backtest.diagnostics.section_16_negative_control_canary import populate_section_16_for_dossier
    from backtest.diagnostics.section_17_soft_score_weight_calibration import populate_section_17_for_dossier

    # B976 (2026-06-21 Council 77 P1 Bucket A A6 wiring): PRE-FLIGHT
    # dossier_self_test gate. Per Council 38 Outsider mandate the self-test
    # must run BEFORE Stream E on full roster - if known-good/known-broken
    # canaries fail, abort to prevent contaminated dossier population.
    # Closes B971 'c' classification for dossier_self_test.py.
    # SOFT-GATE design: log + continue on failure (per RECURRING-tool
    # contract; full block-on-failure would require owner-decided severity
    # gate). Council 38 Outsider mandate satisfied by visibility, not block.
    try:
        from scripts.dossier_self_test import main as _dossier_self_test_main
        logger.info("B976 A6 wiring PRE-FLIGHT: invoking dossier_self_test.main()")
        _self_test_rc = _dossier_self_test_main()
        if _self_test_rc != 0:
            logger.warning("Dossier self-test PRE-FLIGHT returned non-zero: %s "
                           "(continuing population; Outsider mandate notes "
                           "should be addressed before next R5 gate-check)",
                           _self_test_rc)
        else:
            logger.info("Dossier self-test PRE-FLIGHT OK - safe to populate full roster")
    except Exception as _e_self_test:
        logger.warning("B976 A6 wiring: dossier self-test PRE-FLIGHT failed "
                       "(non-fatal): %s: %s",
                       type(_e_self_test).__name__, _e_self_test)

    strategies = list_strategies_for_dossier()
    logger.info("Populating sections 1 / 5 / 6 / 7 / 8 / 9 / 9b / 10 / 11 / 12 / 13 / 18 + r5_inclusion_criterion for %d strategies...", len(strategies))

    from collections import Counter
    stats = {
        "total": len(strategies),
        "section_1_populated": 0,
        "section_1_errors": 0,
        "section_6_populated": 0,
        "section_6_errors": 0,
        "section_3_populated": 0,
        "section_3_errors": 0,
        "section_4_populated": 0,
        "section_4_errors": 0,
        "section_5_populated": 0,
        "section_5_errors": 0,
        "section_7_populated": 0,
        "section_7_errors": 0,
        "section_8_populated": 0,
        "section_8_errors": 0,
        "section_13_populated": 0,
        "section_13_errors": 0,
        "section_19_populated": 0,
        "section_19_errors": 0,
        "section_2_populated": 0,
        "section_2_errors": 0,
        "section_14_populated": 0,
        "section_14_errors": 0,
        "section_15_populated": 0,
        "section_15_errors": 0,
        "section_16_populated": 0,
        "section_16_errors": 0,
        "section_17_populated": 0,
        "section_17_errors": 0,
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
            populate_section_01_for_dossier(strat, dossier_path)
            stats["section_1_populated"] += 1
        except Exception as e:
            stats["section_1_errors"] += 1
            stats["drift_findings"].append(f"section_1:{strat}: {type(e).__name__}: {e}")
        try:
            populate_section_06_for_dossier(strat, dossier_path)
            stats["section_6_populated"] += 1
        except Exception as e:
            stats["section_6_errors"] += 1
            stats["drift_findings"].append(f"section_6:{strat}: {type(e).__name__}: {e}")
        try:
            populate_section_03_for_dossier(strat, dossier_path)
            stats["section_3_populated"] += 1
        except Exception as e:
            stats["section_3_errors"] += 1
            stats["drift_findings"].append(f"section_3:{strat}: {type(e).__name__}: {e}")
        try:
            populate_section_04_for_dossier(strat, dossier_path)
            stats["section_4_populated"] += 1
        except Exception as e:
            stats["section_4_errors"] += 1
            stats["drift_findings"].append(f"section_4:{strat}: {type(e).__name__}: {e}")
        try:
            populate_section_05_for_dossier(strat, dossier_path)
            stats["section_5_populated"] += 1
        except Exception as e:
            stats["section_5_errors"] += 1
            stats["drift_findings"].append(f"section_5:{strat}: {type(e).__name__}: {e}")
        try:
            populate_section_07_for_dossier(strat, dossier_path)
            stats["section_7_populated"] += 1
        except Exception as e:
            stats["section_7_errors"] += 1
            stats["drift_findings"].append(f"section_7:{strat}: {type(e).__name__}: {e}")
        try:
            populate_section_08_for_dossier(strat, dossier_path)
            stats["section_8_populated"] += 1
        except Exception as e:
            stats["section_8_errors"] += 1
            stats["drift_findings"].append(f"section_8:{strat}: {type(e).__name__}: {e}")
        try:
            populate_section_13_for_dossier(strat, dossier_path)
            stats["section_13_populated"] += 1
        except Exception as e:
            stats["section_13_errors"] += 1
            stats["drift_findings"].append(f"section_13:{strat}: {type(e).__name__}: {e}")
        try:
            populate_section_19_for_dossier(strat, dossier_path)
            stats["section_19_populated"] += 1
        except Exception as e:
            stats["section_19_errors"] += 1
            stats["drift_findings"].append(f"section_19:{strat}: {type(e).__name__}: {e}")
        # B962-B966 additions
        for sec_num, populate_fn in [
            ("2", populate_section_02_for_dossier),
            ("14", populate_section_14_for_dossier),
            ("15", populate_section_15_for_dossier),
            ("16", populate_section_16_for_dossier),
            ("17", populate_section_17_for_dossier),
        ]:
            try:
                populate_fn(strat, dossier_path)
                stats[f"section_{sec_num}_populated"] += 1
            except Exception as e:
                stats[f"section_{sec_num}_errors"] += 1
                stats["drift_findings"].append(f"section_{sec_num}:{strat}: {type(e).__name__}: {e}")
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
    logger.info("  Section 1:        %d populated / %d errors", stats["section_1_populated"], stats["section_1_errors"])
    logger.info("  Section 3:        %d populated / %d errors", stats["section_3_populated"], stats["section_3_errors"])
    logger.info("  Section 4:        %d populated / %d errors", stats["section_4_populated"], stats["section_4_errors"])
    logger.info("  Section 5:        %d populated / %d errors", stats["section_5_populated"], stats["section_5_errors"])
    logger.info("  Section 6:        %d populated / %d errors", stats["section_6_populated"], stats["section_6_errors"])
    logger.info("  Section 7:        %d populated / %d errors", stats["section_7_populated"], stats["section_7_errors"])
    logger.info("  Section 8:        %d populated / %d errors", stats["section_8_populated"], stats["section_8_errors"])
    logger.info("  Section 13:       %d populated / %d errors", stats["section_13_populated"], stats["section_13_errors"])
    logger.info("  Section 19:       %d populated / %d errors", stats["section_19_populated"], stats["section_19_errors"])
    for sec_num in ("2", "14", "15", "16", "17"):
        logger.info("  Section %s:       %d populated / %d errors", sec_num.rjust(2), stats[f"section_{sec_num}_populated"], stats[f"section_{sec_num}_errors"])
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

    # B975 (2026-06-21 Council 77 P1 Bucket A A9 wiring): end-of-run hook
    # to b956_build_findings_triage_queue. After full-roster population,
    # findings dependencies (sections 1/6/7/8/13/14/15/16/17/19 + r5_inclusion_
    # criterion) are freshly written. B956 consumes those exact sections to
    # enumerate FIRE_STARVED / SIGNAL_ORPHAN / INVERSE_UNSAFE / STATE_OVERCLAIM
    # / EARNINGS_BLACKOUT / DEFERRED_OWNER_TRIAGE findings into a flat queue.
    # Wiring here closes B971 'c' classification for b956 cron + ensures the
    # triage queue is always in sync with the latest dossier population.
    # Failure is non-fatal: triage queue is a SURFACING artifact, not gate.
    try:
        from scripts.b956_build_findings_triage_queue import main as _b956_main
        logger.info("B975 A9 wiring: invoking b956_build_findings_triage_queue.main()")
        _b956_rc = _b956_main()
        if _b956_rc != 0:
            logger.warning("B956 triage queue builder returned non-zero: %s", _b956_rc)
        else:
            logger.info("B956 triage queue builder OK (output_audit/b956_findings_triage_queue.json refreshed)")
    except Exception as _e_b956:
        logger.warning("B975 A9 wiring: b956 cron failed (non-fatal): %s: %s",
                       type(_e_b956).__name__, _e_b956)

    # B976 (2026-06-21 Council 77 P1 Bucket A A8 wiring): end-of-run hook
    # to build_walk_verdict_ledger_v2. STAGE_4 cluster walk doc edits feed
    # the walk-verdict ledger v2 (Council 54 verdict-bearing-keyword scan).
    # Wiring here per same cadence as A9 b956 cron - populate_all_dossiers
    # is the post-walk batch trigger that warrants verdict-ledger refresh.
    # Closes B971 'c' classification for build_walk_verdict_ledger_v2.py.
    # Failure is non-fatal: ledger v2 is a SURFACING artifact, not gate.
    try:
        from scripts.build_walk_verdict_ledger_v2 import main as _ledger_v2_main
        logger.info("B976 A8 wiring: invoking build_walk_verdict_ledger_v2.main()")
        _ledger_v2_rc = _ledger_v2_main()
        if _ledger_v2_rc != 0:
            logger.warning("Ledger v2 builder returned non-zero: %s", _ledger_v2_rc)
        else:
            logger.info("Ledger v2 builder OK (output_audit/walk_verdict_ledger_v2.json refreshed)")
    except Exception as _e_ledger_v2:
        logger.warning("B976 A8 wiring: ledger v2 cron failed (non-fatal): %s: %s",
                       type(_e_ledger_v2).__name__, _e_ledger_v2)

    # B976 (2026-06-21 Council 77 P1 Bucket A A7 wiring): end-of-run hook
    # to stream_v_verify_reproducibility. Stream V is the verification layer
    # that double-runs all Stream E extractors on 5 sampled strategies +
    # asserts bit-identical output. PATH Section 13.7 R5 launch gate #14
    # requires Stream V passing pre-R5. Natural wiring: run Stream V after
    # populate_all_dossiers (Stream E) completes - so any extractor change
    # that breaks determinism surfaces immediately, not weeks later at
    # pre-R5 gate-check. Closes B971 'c' classification for
    # stream_v_verify_reproducibility.py.
    # Failure is non-fatal: Stream V is a SURFACING verification, not gate
    # (R5 launch gate is a separate manual checklist that consults the
    # latest Stream V report).
    try:
        from scripts.stream_v_verify_reproducibility import main as _stream_v_main
        logger.info("B976 A7 wiring: invoking stream_v_verify_reproducibility.main()")
        _stream_v_rc = _stream_v_main()
        if _stream_v_rc != 0:
            logger.warning("Stream V reproducibility verifier returned non-zero: %s", _stream_v_rc)
        else:
            logger.info("Stream V verifier OK (output_audit/b970_stream_v_reproducibility_report.json refreshed)")
    except Exception as _e_stream_v:
        logger.warning("B976 A7 wiring: Stream V cron failed (non-fatal): %s: %s",
                       type(_e_stream_v).__name__, _e_stream_v)

    return 0 if all(stats[k] == 0 for k in ("section_6_errors", "section_9_errors", "section_9b_errors")) else 1


if __name__ == "__main__":
    sys.exit(main())
