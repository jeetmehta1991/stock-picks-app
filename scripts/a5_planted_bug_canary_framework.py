# Source: PATH Section 13.7 R5 Launch Gate #15 (Planted-bug canary) + Council 104 Option-6 Phase 1 A5 per CHECKLIST #77.
"""B1011 A5 - Planted-bug canary framework.

# Source: Council 39 5-advisor bug-catching panel synthesis + Council 104
# Option-6 MULTI-BATCH-PHASE-A-FIRST Phase 1 A5 per owner directive
# 2026-06-22 "Approved. Update execution queue in each turn once tickets
# are resolved. Council this. Proceed."

PURPOSE
-------
PATH Section 13.7 R5 Launch Gate #15: "Planted-bug canary caught by walk
methodology (Council 39 - owner injects bug Claude-blind; if walk
doesn't catch it, walk methodology is theater)."

This framework provides the harness for owner to inject a synthetic
bug into a strategy or producer + verify the walk methodology catches
it before R5 launches.

PROTOCOL (owner-facing)
-----------------------

1. **Owner chooses bug type** from `BUG_CATALOG` below. Each bug type
   has known walk-detection mechanism.

2. **Owner runs `inject_bug.py --bug-type <X> --target <strategy>`**
   to apply bug. Claude is BLIND to which bug owner chose.

3. **Owner runs walk methodology** (Stage 4 walk script) on bugged
   strategy.

4. **Walk methodology must surface bug in walk-output disposition**:
   - If walk surfaces bug → canary PASS; methodology is sound
   - If walk does NOT surface bug → canary FAIL; methodology is theater

5. **Owner runs `revert_bug.py`** to restore original state.

6. **Owner records verdict** in `output_audit/a5_planted_bug_canary_log.json`:
   {"date": "...", "bug_type": "X", "target": "...", "walk_caught_bug": true/false}

BUG CATALOG (Council 39 5-advisor synthesis)
--------------------------------------------

Bug-type 1: SILENT-LOOKAHEAD
  Modify producer to read 1-bar-future data (e.g., df["close"].shift(-1))
  Walk should catch: section_07 temporal coverage + CHECKLIST #44(b)
  investigate-why

Bug-type 2: SIGNAL-ORPHAN
  Modify strategy to consume signal NOT produced by any producer
  Walk should catch: section_01 wiring trace (producer index miss)

Bug-type 3: FIRE-COUNT-DRIFT
  Loosen gate to fire 10x more than baseline
  Walk should catch: section_07 fire-count projection drift

Bug-type 4: INVERSE-UNSAFE
  Add mechanical SHORT mirror with data-source asymmetric base
  (e.g., 13F-based SHORT)
  Walk should catch: section_06 EVENT-vs-STATE + B611 asymmetry

Bug-type 5: REGIME-AFFINITY-DRIFT
  Modify STRATEGY_REGIME_AFFINITY entry to claim regime that
  doesn't match strategy logic
  Walk should catch: section_05 regime affinity lineage cross-ref

PROTECTION (CHECKLIST #114 STOP CONDITIONS)
-------------------------------------------

- Bug injection is REVERSIBLE (git revert path)
- Test pyramid must pass post-injection (catches mechanical bugs)
- Owner countersigns canary verdict before R5 launch
- A5 framework is INFRASTRUCTURE; owner-controlled execution gate

USAGE (PROTOTYPE; owner refines per actual injection)
-----------------------------------------------------

    # Owner-side:
    python scripts/a5_planted_bug_canary_framework.py --list-bugs
    python scripts/a5_planted_bug_canary_framework.py --inject \
        --bug-type silent-lookahead --target compute_smc_signals

    # Claude runs walk:
    python scripts/run_stage_4_walk.py compute_smc_signals

    # Owner verifies + reverts:
    python scripts/a5_planted_bug_canary_framework.py --revert
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent

BUG_CATALOG: dict[str, dict[str, Any]] = {
    "silent-lookahead": {
        "description": "Modify producer to read 1-bar-future data",
        "detection_mechanism": "section_07 temporal coverage + CHECKLIST #44(b) investigate-why",
        "example_target_files": ["backtest/signals/smc_ict.py", "backtest/signals/technical.py"],
        "example_diff_template": "df['signal'] = df['close'].shift(-1) > df['close']  # 1-bar lookahead",
    },
    "signal-orphan": {
        "description": "Modify strategy to consume signal NOT produced by any producer",
        "detection_mechanism": "section_01 wiring trace (producer index miss)",
        "example_target_files": ["backtest/signals/screener.py"],
        "example_diff_template": "s.get('definitely_orphan_signal_xyz', False)",
    },
    "fire-count-drift": {
        "description": "Loosen gate to fire 10x more than baseline",
        "detection_mechanism": "section_07 fire-count projection drift",
        "example_target_files": ["backtest/signals/screener.py"],
        "example_diff_template": "remove a gate condition (AND -> True default)",
    },
    "inverse-unsafe": {
        "description": "Add mechanical SHORT mirror with data-source asymmetric base",
        "detection_mechanism": "section_06 EVENT-vs-STATE + B611 asymmetry check",
        "example_target_files": ["backtest/signals/screener.py"],
        "example_diff_template": "def strat_<long_name>_short(s): ... # 13F-based SHORT (forbidden per SEC)",
    },
    "regime-affinity-drift": {
        "description": "Modify STRATEGY_REGIME_AFFINITY entry to claim regime mismatch",
        "detection_mechanism": "section_05 regime affinity lineage cross-ref",
        "example_target_files": ["backtest/engine/regime_selector.py"],
        "example_diff_template": "STRATEGY_REGIME_AFFINITY['<momentum_strat>'] = {'crisis'}  # wrong; momentum is bull/neutral",
    },
}


def list_bugs() -> int:
    print("PLANTED-BUG CANARY CATALOG (Council 39 5-advisor synthesis)")
    print("=" * 70)
    for bug_id, spec in BUG_CATALOG.items():
        print(f"\nBug-type: {bug_id}")
        print(f"  Description: {spec['description']}")
        print(f"  Detection mechanism: {spec['detection_mechanism']}")
        print(f"  Example targets: {spec['example_target_files']}")
    return 0


def inject_bug(bug_type: str, target: str) -> int:
    """STUB - owner refines per actual injection.

    This framework provides the catalog + protocol. The actual injection
    is owner-controlled to preserve Claude-blind discipline (per Council
    39 gate #15).
    """
    if bug_type not in BUG_CATALOG:
        print(f"ERROR: unknown bug-type '{bug_type}'; see --list-bugs")
        return 1
    spec = BUG_CATALOG[bug_type]
    print(f"INJECTION INSTRUCTIONS for bug-type '{bug_type}':")
    print(f"  Target: {target}")
    print(f"  Description: {spec['description']}")
    print(f"  Detection mechanism walk should catch: {spec['detection_mechanism']}")
    print(f"  Example diff template: {spec['example_diff_template']}")
    print("")
    print("OWNER ACTION REQUIRED:")
    print("  1. Apply the diff template (or owner-crafted equivalent) to target file")
    print("  2. Run pyramid (test_unit + test_integration) - should still pass")
    print("  3. Run Stage 4 walk script on target strategy")
    print("  4. Verify walk-output disposition catches the bug")
    print("  5. Record verdict in output_audit/a5_planted_bug_canary_log.json")
    print("  6. Run revert_bug + verify clean state")
    return 0


def revert_bug() -> int:
    """STUB - owner reverts via git or manual edit."""
    print("REVERT INSTRUCTIONS:")
    print("  Owner reverts via: git diff <bug-target-file>")
    print("  Then: git checkout -- <bug-target-file>")
    print("  Or manual undo of injected diff")
    print("  Verify pyramid GREEN post-revert")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="A5 Planted-bug canary framework")
    parser.add_argument("--list-bugs", action="store_true", help="List bug catalog")
    parser.add_argument("--inject", action="store_true", help="Inject bug (owner-controlled)")
    parser.add_argument("--revert", action="store_true", help="Revert injected bug")
    parser.add_argument("--bug-type", type=str, help="Bug type to inject")
    parser.add_argument("--target", type=str, help="Target file/strategy")
    args = parser.parse_args()

    if args.list_bugs:
        return list_bugs()
    if args.inject:
        if not args.bug_type or not args.target:
            print("ERROR: --inject requires --bug-type + --target")
            return 1
        return inject_bug(args.bug_type, args.target)
    if args.revert:
        return revert_bug()
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
