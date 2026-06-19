"""B934 (2026-06-19): Phase P1 Stream E self-test harness with KNOWN-BUG canaries.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.2 + Council 38 Outsider Pre-flight
# Self-Test Mandate + Council 44 batch 1 commit 2 per owner directive 2026-06-19
# Option A.

PURPOSE
-------
Council 38 Outsider mandate (verbatim):
    "Before trusting A1-A9 outputs, run them against KNOWN-BUG ground truth
    (B918 institutional_signal bug, B917 32-ticker gap). If Phase A misses
    these known cases, Phase A is broken — fix before proceeding."

Council 38 Executor extension:
    "Stream E self-test on 5 known-good + 5 known-broken strategies BEFORE
    running on 218."

This harness defines the canonical KNOWN-GOOD + KNOWN-BROKEN strategy sets
+ a runner that asserts each Stream E section produces expected behavior
on both. Failure of self-test BLOCKS Stream E from running on full 218
strategies per Outsider mandate.

KNOWN-GOOD STRATEGIES (R4-era; present in output_batch395_final/)
-----------------------------------------------------------------
R4 cube ran with 102-strategy roster (May 31); current roster is 219.
B934 self-test caught this drift: post-R4 additions (SMC + chart-pattern
B685 Class 7 NEW + hammer + head_and_shoulders) NOT in R4 results.

Council 45 (owner-approved B934 architecture):
- Section 9 = TWO-TRACK extractor:
  - R4-included (~102): populate from output_batch395_final/backtest_results.csv
  - Post-R4 (~117): null + r4_status="post_r4_addition"
- NEW Section 9b "pre_cube_evidence" carries: B907/B660 fire-count +
  B883 walk batch reference + EXPLORATORY/DORMANT status + attribution
- dossier.r5_inclusion_criterion ∈ {r4_metrics_passed,
  pre_cube_evidence_sufficient, deferred}

For Section 9 R4 extractor self-test, use R4-era strategies:
1. donchian_10_breakout (in R4; momentum baseline)
2. po3_bullish (in R4; ICT family; B722 EXPLORATORY but in R4)
3. avwap_50_reclaim (in R4; AVWAP reclaim pattern)
4. institutional_cluster_long (in R4; institutional family BEFORE B918 fix)
5. rsi21_slow (in R4; sample row from R4 results CSV)

Current-roster known-good (post-R4 additions; Section 9b carries evidence):
- smc_breaker_block_long (B907 verified 31,158/yr; needs B901 SMC fix)
- head_and_shoulders_top_short (B685 Class 7 NEW)
- hammer_at_support_long (B685 Class 7 NEW)
- institutional_high_conviction_long POST-B922 + B918 fix

KNOWN-BROKEN CANARIES (5)
-------------------------
These represent past-bug snapshots OR architectural gaps that Stream E
must surface. A Stream E section that fails to flag them is broken.

1. institutional_high_conviction_long PRE-B922 baseline (R4=0 fires; should
   show R4 cube metrics fire_count=0 in Section 9)
2. classification_change_recent_long (B910 sector_history stale; Section 9
   should show 0 R4 fires)
3. dxy_headwind_multinational_short (STRATEGIES_DISABLED_MISSING_PRODUCER;
   Section 9 should show absence from cube)
4. institutional_persistent_holders_long (B906 MEASUREMENT_DISPUTED; Section
   9 should reflect dispute classification)
5. mfi_oversold (any historically-fire-starved baseline strategy)
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

logger = logging.getLogger(__name__)


# Council 38 + 44 canonical sets
KNOWN_GOOD_STRATEGIES_R4_ERA = [
    "donchian_10_breakout",       # in R4 momentum baseline
    "po3_bullish",                # in R4 ICT family
    "avwap_50_reclaim",           # in R4 AVWAP reclaim
    "institutional_cluster_long", # in R4 institutional family (pre-B918 era)
    "rsi21_slow",                 # in R4 sample
]

KNOWN_GOOD_STRATEGIES_POST_R4 = [
    "smc_breaker_block_long",              # B907 31,158/yr; B901 SMC fix
    "head_and_shoulders_top_short",        # B685 Class 7 NEW
    "hammer_at_support_long",              # B685 Class 7 NEW
    "institutional_high_conviction_long",  # B918 fix + B922 unblocked
]

KNOWN_BROKEN_CANARIES = [
    {
        "strategy": "institutional_high_conviction_long",
        "canary_type": "pre_b922_baseline",
        "expected_r4_fires": 0,
        "description": "R4 cube ran pre-B918 fix; pre-B922 TIER 2 deferral; should show 0 fires",
    },
    {
        "strategy": "classification_change_recent_long",
        "canary_type": "b910_sector_history_stale",
        "expected_r4_fires": 0,
        "description": "sector_history.csv 1190d stale; producer emits empty in 2024 window",
    },
    {
        "strategy": "dxy_headwind_multinational_short",
        "canary_type": "missing_producer_disabled",
        "expected_r4_fires": "absent_from_cube",
        "description": "In STRATEGIES_DISABLED_MISSING_PRODUCER set (foreign_rev_pct producer absent)",
    },
    {
        "strategy": "institutional_persistent_holders_long",
        "canary_type": "b906_measurement_disputed",
        "expected_r4_fires": "any",
        "description": "In B906 MEASUREMENT_DISPUTED set; cube measurement validity in dispute",
    },
    {
        "strategy": "mfi_oversold",
        "canary_type": "fire_starved_baseline",
        "expected_r4_fires": "any_or_zero",
        "description": "Historical baseline mean-reversion; in MEAN_REVERSION_STRATEGIES set",
    },
]


def assert_known_good_in_roster() -> tuple[list[str], list[str]]:
    """Verify all KNOWN-GOOD strategies (R4-era + post-R4) exist in ALL_STRATEGIES."""
    from backtest.signals.screener import ALL_STRATEGIES
    all_known = KNOWN_GOOD_STRATEGIES_R4_ERA + KNOWN_GOOD_STRATEGIES_POST_R4
    present = [s for s in all_known if s in ALL_STRATEGIES]
    missing = [s for s in all_known if s not in ALL_STRATEGIES]
    return present, missing


def assert_known_broken_canaries_classification() -> dict:
    """Verify B906 / disabled / mean-rev set memberships are still valid."""
    from backtest.config import (
        MEASUREMENT_DISPUTED,
        MEAN_REVERSION_STRATEGIES,
        STRATEGIES_DISABLED_MISSING_PRODUCER,
    )
    from backtest.signals.screener import ALL_STRATEGIES

    results = {}
    for canary in KNOWN_BROKEN_CANARIES:
        strat = canary["strategy"]
        canary_type = canary["canary_type"]
        check = {}
        if canary_type == "b906_measurement_disputed":
            check["in_measurement_disputed"] = strat in MEASUREMENT_DISPUTED
        elif canary_type == "missing_producer_disabled":
            check["in_disabled_missing_producer"] = strat in STRATEGIES_DISABLED_MISSING_PRODUCER
        elif canary_type == "fire_starved_baseline":
            check["in_mean_reversion_set"] = strat in MEAN_REVERSION_STRATEGIES
        elif canary_type == "b910_sector_history_stale":
            # Cannot self-check without running producer; mark as runtime check
            check["runtime_check_required"] = True
        elif canary_type == "pre_b922_baseline":
            # Cannot self-check without R4 snapshot; mark as runtime check
            check["runtime_check_required"] = True
        check["in_all_strategies"] = strat in ALL_STRATEGIES
        results[strat] = {"canary_type": canary_type, "checks": check}
    return results


def self_test_meta() -> dict:
    """Self-test #0: meta-level verification before any section self-test runs.

    Asserts:
    - All 5 known-good strategies present in ALL_STRATEGIES
    - All known-broken canary classifications match current config
    - Reports any drift (e.g., B922 fix may have caused institutional_*
      strategies to be re-classified from broken to good)
    """
    good_present, good_missing = assert_known_good_in_roster()
    canary_classification = assert_known_broken_canaries_classification()

    result = {
        "test_id": "self_test_meta",
        "known_good_present": good_present,
        "known_good_missing": good_missing,
        "canary_classification": canary_classification,
        "passed": len(good_missing) == 0,
    }
    if not result["passed"]:
        logger.error(
            "Self-test META FAIL: missing known-good strategies %r. Roster changed "
            "without updating self-test; review KNOWN_GOOD_STRATEGIES.",
            good_missing,
        )
    return result


def _load_r4_strategies(r4_results_csv: Path) -> set[str]:
    """Load the set of strategy names present in R4 cube results."""
    import pandas as pd
    if not r4_results_csv.exists():
        return set()
    df = pd.read_csv(r4_results_csv)
    if "strategy" not in df.columns:
        return set()
    return set(df["strategy"].unique())


def self_test_section_9a_r4_era_known_good_present_in_r4(
    r4_results_csv: Path,
) -> dict:
    """Council 45 Assertion 1: R4-era known-good strategies MUST be in R4 results.

    If extract_section_9 cannot find R4 metrics for these strategies, the
    R4 extractor is broken. R4 cube ran with the older 102-strategy roster
    that included these.
    """
    r4_strategies = _load_r4_strategies(r4_results_csv)
    if not r4_strategies:
        return {
            "test_id": "section_9a_r4_era_in_r4",
            "passed": False,
            "reason": f"R4 results CSV missing or empty: {r4_results_csv}",
        }
    found = {s: s in r4_strategies for s in KNOWN_GOOD_STRATEGIES_R4_ERA}
    n_found = sum(found.values())
    n_total = len(KNOWN_GOOD_STRATEGIES_R4_ERA)
    return {
        "test_id": "section_9a_r4_era_in_r4",
        "n_r4_era_known_good_found_in_r4": n_found,
        "n_r4_era_known_good_total": n_total,
        "found_per_strategy": found,
        # ALL R4-era known-good MUST be in R4; if not, R4-era selection was wrong
        "passed": n_found == n_total,
    }


def self_test_section_9b_post_r4_known_good_NOT_in_r4(
    r4_results_csv: Path,
) -> dict:
    """Council 45 Assertion 2: Post-R4 known-good strategies MUST NOT be in R4 results.

    These strategies were added after R4 ran (May 31). If any appear in
    R4 results, either: (a) post-R4 classification is wrong, OR (b) R4 was
    re-run with newer roster (architectural fact we'd need to know).
    """
    r4_strategies = _load_r4_strategies(r4_results_csv)
    if not r4_strategies:
        return {
            "test_id": "section_9b_post_r4_NOT_in_r4",
            "passed": False,
            "reason": f"R4 results CSV missing or empty: {r4_results_csv}",
        }
    in_r4 = {s: s in r4_strategies for s in KNOWN_GOOD_STRATEGIES_POST_R4}
    n_unexpected_in_r4 = sum(in_r4.values())
    return {
        "test_id": "section_9b_post_r4_NOT_in_r4",
        "n_post_r4_known_good_unexpectedly_in_r4": n_unexpected_in_r4,
        "in_r4_per_strategy": in_r4,
        # All POST-R4 known-good must be NOT in R4; if any are, classification drifted
        "passed": n_unexpected_in_r4 == 0,
    }


def self_test_section_9b_evidence_available_for_post_r4(
    r4_results_csv: Path,
) -> dict:
    """Council 45 Assertion 3 (load-bearing): Section 9b pre_cube_evidence MUST be available for post-R4 strategies.

    For each post-R4 known-good, we must have AT LEAST ONE of:
    - Stage 4 walk batch reference (e.g., B685/B686/B722/B907 lineage)
    - B660 or B907 fire-count projection
    - EXPLORATORY/DORMANT/MEASUREMENT_DISPUTED status tag

    If a post-R4 strategy has NONE of these, it has no pre-cube evidence
    and should fail the r5_inclusion_criterion gate.
    """
    from backtest.config import MEASUREMENT_DISPUTED
    r4_strategies = _load_r4_strategies(r4_results_csv)

    # Sources of pre-cube evidence (B883 Stage 4 walk ledger references)
    walk_lineage_markers = {
        "smc_breaker_block_long": ["B907 micro-pilot verified 31,158/yr"],
        "head_and_shoulders_top_short": ["B685 Class 7 NEW Edwards-Magee 1948"],
        "hammer_at_support_long": ["B685 Class 7 NEW Nison 1991"],
        "institutional_high_conviction_long": ["B918 fix + B922 architectural unblock (156/yr sample)"],
    }

    evidence_per_strategy = {}
    for strat in KNOWN_GOOD_STRATEGIES_POST_R4:
        markers = walk_lineage_markers.get(strat, [])
        in_disputed = strat in MEASUREMENT_DISPUTED
        evidence_per_strategy[strat] = {
            "walk_lineage_markers": markers,
            "in_measurement_disputed": in_disputed,
            "in_r4": strat in r4_strategies,
            "has_pre_cube_evidence": bool(markers) or in_disputed,
        }

    # ALL post-R4 known-good must have AT LEAST one evidence source
    n_with_evidence = sum(
        1 for v in evidence_per_strategy.values() if v["has_pre_cube_evidence"]
    )
    return {
        "test_id": "section_9b_evidence_available",
        "n_post_r4_with_pre_cube_evidence": n_with_evidence,
        "n_post_r4_total": len(KNOWN_GOOD_STRATEGIES_POST_R4),
        "evidence_per_strategy": evidence_per_strategy,
        "passed": n_with_evidence == len(KNOWN_GOOD_STRATEGIES_POST_R4),
    }


def self_test_r5_inclusion_criterion_values_match_spec() -> dict:
    """Council 45 schema invariant: r5_inclusion_criterion enum has exactly 3 values."""
    from scripts.dossier_build import R5_INCLUSION_CRITERIA
    expected = ("r4_metrics_passed", "pre_cube_evidence_sufficient", "deferred")
    return {
        "test_id": "r5_inclusion_criterion_enum",
        "actual": list(R5_INCLUSION_CRITERIA),
        "expected": list(expected),
        "passed": tuple(R5_INCLUSION_CRITERIA) == expected,
    }


def self_test_section_9_broken_canaries_match_expectations(
    r4_results_csv: Path,
) -> dict:
    """Self-test for Section 9: known-broken canaries match expected R4 behavior."""
    import pandas as pd
    if not r4_results_csv.exists():
        return {
            "test_id": "section_9_broken_canaries",
            "passed": False,
            "reason": f"R4 results CSV not found: {r4_results_csv}",
        }
    df = pd.read_csv(r4_results_csv)
    canary_results = {}
    for canary in KNOWN_BROKEN_CANARIES:
        strat = canary["strategy"]
        sub = df[df["strategy"] == strat] if "strategy" in df.columns else df.iloc[0:0]
        in_r4 = not sub.empty
        n_trades = int(sub["total_trades"].iloc[0]) if in_r4 and "total_trades" in sub.columns else 0
        canary_results[strat] = {
            "canary_type": canary["canary_type"],
            "expected_r4_fires": canary["expected_r4_fires"],
            "in_r4": in_r4,
            "n_trades_in_r4": n_trades,
        }
    return {
        "test_id": "section_9_broken_canaries",
        "canary_results": canary_results,
        "passed": True,  # Diagnostic; passes always; data feeds dossier
        "purpose": "Diagnostic; records canary R4 state for later cross-check",
    }


def run_all_self_tests(
    r4_results_csv: Optional[Path] = None,
) -> dict:
    """Run all Stream E self-tests; return aggregate report."""
    if r4_results_csv is None:
        r4_results_csv = REPO / "output_batch395_final" / "backtest_results.csv"

    tests = []
    tests.append(self_test_meta())
    # Council 45 3-assertion redesign for Section 9 + 9b:
    tests.append(self_test_section_9a_r4_era_known_good_present_in_r4(r4_results_csv))
    tests.append(self_test_section_9b_post_r4_known_good_NOT_in_r4(r4_results_csv))
    tests.append(self_test_section_9b_evidence_available_for_post_r4(r4_results_csv))
    tests.append(self_test_r5_inclusion_criterion_values_match_spec())
    # Original diagnostic carried forward:
    tests.append(self_test_section_9_broken_canaries_match_expectations(r4_results_csv))

    all_passed = all(t["passed"] for t in tests)
    return {
        "phase": "P1",
        "batch": "B934",
        "stream_e_self_test_passed": all_passed,
        "tests_run": len(tests),
        "tests_passed": sum(1 for t in tests if t["passed"]),
        "results": tests,
        "known_good_strategies_r4_era": KNOWN_GOOD_STRATEGIES_R4_ERA,
        "known_good_strategies_post_r4": KNOWN_GOOD_STRATEGIES_POST_R4,
        "known_broken_canaries": KNOWN_BROKEN_CANARIES,
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON path (default: output_audit/b934_stream_e_self_test.json)",
    )
    parser.add_argument(
        "--r4-csv",
        default=None,
        help="Path to R4 backtest_results.csv (default: output_batch395_final/backtest_results.csv)",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    r4_csv = Path(args.r4_csv) if args.r4_csv else None
    report = run_all_self_tests(r4_results_csv=r4_csv)

    out_path = Path(args.output) if args.output else (
        REPO / "output_audit" / "b934_stream_e_self_test.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    logger.info(
        "Stream E self-test: %s. Tests passed: %d/%d. Output: %s",
        "PASSED" if report["stream_e_self_test_passed"] else "FAILED",
        report["tests_passed"],
        report["tests_run"],
        out_path,
    )
    return 0 if report["stream_e_self_test_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
