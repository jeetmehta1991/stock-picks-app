"""B1070 Block-4 (Council 182 audit closure 2026-06-29) — silent-strategy
list generator that filters against current ALL_STRATEGIES + baseline.

# Source: Sub-A finding (b1066/b1068/b1069 reports each manually flagged
# 4 NOT_REGISTERED strategies: hull_rsi_short B722-deleted, volume_spike
# _breakout_retest B682-deleted, camarilla_rsi_obv + _short B874-deleted)
# Stage E ITEM 1 marked this "no-op" but the underlying bug recurs at
# every future audit. This helper codifies the filter.
#
# Per `feedback_designed_vs_verified_requires_evidence_artifact` +
# CHECKLIST #124: claim of "no-op" required actual helper to prevent
# recurrence.

Usage from audit scripts:
    from scripts.b1070_silent_strategy_list_generator import (
        silent_strategies_filtered_against_roster,
    )
    silent = silent_strategies_filtered_against_roster(
        baseline_strategies=set_of_b660_strategies,
        fired_strategies=set_from_trade_log,
    )

Filter logic:
  1. baseline_strategies (set from B660 cube data; may include deleted)
  2. Intersect with current ALL_STRATEGIES (excludes deleted)
  3. Exclude DEPRECATED_STRATEGIES
  4. Exclude STRATEGIES_DISABLED_MISSING_PRODUCER
  5. Subtract fired_strategies (silent = expected but didn't fire)
  6. Return set of strategies that ARE in current active roster +
     in baseline + did NOT fire
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def silent_strategies_filtered_against_roster(
    baseline_strategies: set,
    fired_strategies: set,
    include_disabled: bool = False,
    include_deprecated: bool = False,
) -> set:
    """B1070 Block-4: identify silent strategies that ARE in current
    active roster + have baseline expectation but did not fire.

    Filters out deleted/disabled strategies that would otherwise show
    as false silent (e.g. hull_rsi_short deleted B722).

    Args:
        baseline_strategies: set of strategies with non-zero baseline
            expectation (typically from B660 cube data)
        fired_strategies: set of strategies that fired in the run
            (typically from trade_log.csv strategy column)
        include_disabled: include STRATEGIES_DISABLED_MISSING_PRODUCER
            in active set (default False)
        include_deprecated: include DEPRECATED_STRATEGIES in active set
            (default False)

    Returns:
        set of strategy names that are silent_with_expectation +
        in current active roster.
    """
    from backtest.signals.screener import ALL_STRATEGIES
    from backtest.config import (
        DEPRECATED_STRATEGIES, STRATEGIES_DISABLED_MISSING_PRODUCER,
    )

    active = set(ALL_STRATEGIES.keys())
    if not include_deprecated:
        active -= set(DEPRECATED_STRATEGIES)
    if not include_disabled:
        active -= set(STRATEGIES_DISABLED_MISSING_PRODUCER)

    # Silent = in baseline AND in active roster AND did not fire
    silent = (set(baseline_strategies) & active) - set(fired_strategies)
    return silent


def deleted_strategies_in_baseline(baseline_strategies: set) -> set:
    """Identify strategies that appear in baseline but were DELETED
    from current roster (e.g. hull_rsi_short B722). These are NOT
    silent bugs - they're stale baseline entries.

    Returns set of strategy names in baseline but not in ALL_STRATEGIES.
    """
    from backtest.signals.screener import ALL_STRATEGIES
    return set(baseline_strategies) - set(ALL_STRATEGIES.keys())


def silent_classification_report(
    baseline_strategies: set,
    fired_strategies: set,
) -> dict:
    """Comprehensive silent-strategy classification.

    Returns:
        dict with keys:
            silent_in_roster: set (true silents)
            deleted_from_roster: set (stale baseline)
            disabled_missing_producer: set (known-blocked)
            deprecated: set (intentionally disabled)
            never_in_baseline: set (no expectation)
    """
    from backtest.signals.screener import ALL_STRATEGIES
    from backtest.config import (
        DEPRECATED_STRATEGIES, STRATEGIES_DISABLED_MISSING_PRODUCER,
    )

    baseline = set(baseline_strategies)
    fired = set(fired_strategies)
    all_strats = set(ALL_STRATEGIES.keys())
    deprecated = set(DEPRECATED_STRATEGIES)
    disabled = set(STRATEGIES_DISABLED_MISSING_PRODUCER)
    active = all_strats - deprecated - disabled

    return {
        "silent_in_roster": (baseline & active) - fired,
        "deleted_from_roster": baseline - all_strats,
        "disabled_missing_producer": baseline & disabled,
        "deprecated": baseline & deprecated,
        "never_in_baseline": active - baseline - fired,
    }


if __name__ == "__main__":
    # CLI usage: pip-style smoke
    print("B1070 Block-4 silent-strategy generator self-test:")
    from backtest.signals.screener import ALL_STRATEGIES
    sample_baseline = {
        "hull_rsi_short",  # B722 deleted - should be in deleted_from_roster
        "52w_high_breakout",  # active - should be silent_in_roster (if not in fired)
        "dxy_headwind_multinational_short",  # disabled missing producer
    }
    sample_fired = {"morning_star"}
    report = silent_classification_report(sample_baseline, sample_fired)
    for k, v in report.items():
        print(f"  {k}: {sorted(v)[:5]}")
