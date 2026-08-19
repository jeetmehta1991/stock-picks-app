#!/usr/bin/env python
"""Every completed cube must carry a COMPLETE post-config ledger. Mechanically.

B1699, owner catch. The runbook has said since it was written:

    MANDATORY POST-CONFIG ANALYSIS (owner directive - run after EVERY config,
    unprompted). "Skipping a step is a silent miss."

I ran 1-2 steps per turn and waited to be asked for the rest, four times. When
the owner pointed at it I VERIFIED the text was already there and wrote a ticket
saying it "needs mechanical enforcement like #221, not another sentence."

**That ticket was itself another sentence.** Ticketing the need for a gate is not
building the gate - the same deferral, one level up, which is exactly what the
GENERALIZATION MANDATE forbids.

And the reason no existing hook caught it: `verify_turn_compliance.py` has TEN
gates and every one of them checks how work is REPORTED or COMMITTED - verdict
denominators, orphan rules, unverified claims, artifact drift, the compliance
marker. **Not one checks whether mandatory work RAN.** A turn could skip the
entire post-config sequence and every gate would pass, because each gate audits
the description of the work rather than its existence.

This closes that hole. For every cube that finished, a ledger entry must exist
with all NINE steps dispositioned. Silence is not a disposition; SKIPPED with a
reason is. The gate blocks the turn otherwise.

Exit 0 = every completed cube has a complete ledger.
Exit 2 = a cube exists with steps neither DONE nor explicitly SKIPPED.
Exit 3 = the ledger is unreadable (fail CLOSED).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEDGER = ROOT / "output_audit" / "postconfig_ledger.json"

# The nine steps the runbook mandates, in order.
STEPS = [
    "1_cube_sanity",
    "2_grade_with_config_params",
    "3_outlier_discrepancy_sweep",
    "4_three_leg_spot_check",
    "5_adversarial_lens_review",
    "6_post_fix_recheck",
    "6b_equivalence_class_check",
    "7_implement_in_engine",
    "8_verdict_with_denominators",
]
TERMINAL = {"DONE", "SKIPPED", "N/A"}


def completed_cubes() -> list[str]:
    """A cube that exists is a config that finished and owes a ledger entry."""
    out = []
    for d in sorted(ROOT.glob("output_*")):
        if (d / "trade_exit_detail.csv").exists():
            out.append(d.name)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--only", help="check just this config name")
    a = ap.parse_args()

    if LEDGER.exists():
        try:
            ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"FAIL-CLOSED: ledger unreadable: {exc!r}")
            return 3
    else:
        ledger = {}

    cubes = completed_cubes()
    if a.only:
        cubes = [c for c in cubes if c == a.only]

    incomplete = []
    for c in cubes:
        entry = ledger.get(c, {})
        missing = [s for s in STEPS if entry.get(s, {}).get("status") not in TERMINAL]
        if missing:
            incomplete.append((c, missing))

    if not a.quiet:
        print("=== POST-CONFIG LEDGER (B1699) ===")
        for c in cubes:
            e = ledger.get(c, {})
            done = sum(1 for s in STEPS if e.get(s, {}).get("status") in TERMINAL)
            mark = "COMPLETE" if done == len(STEPS) else "INCOMPLETE"
            print(f"  {mark:10} {c}: {done} of {len(STEPS)} steps dispositioned")
        print(f"\n  {len(cubes)} cubes | {len(incomplete)} incomplete")

    if incomplete:
        print("\nBLOCK: a finished cube owes a complete post-config ledger. "
              "The runbook calls skipping a step a silent miss, so a step with no "
              "entry is not 'pending' - it is missing. Record DONE with evidence, "
              "or SKIPPED with a reason.")
        for c, missing in incomplete:
            print(f"  {c}: {', '.join(missing)}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
