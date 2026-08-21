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
        # B1814b: RUN and SKIPPED are reported SEPARATELY. "9 of 9
        # dispositioned" counted a SKIPPED step toward completion, which is
        # right for the gate's contract and wrong for the question a reader
        # actually asks - "did the analysis RUN?". MEASURED when the owner
        # asked: 4 of 36 step-instances across the sweep configs were SKIPPED,
        # all of them step 6, and nothing in this output said so.
        total_skipped = 0
        for c in cubes:
            e = ledger.get(c, {})
            ran = sum(1 for s in STEPS if e.get(s, {}).get("status") == "DONE")
            skipped = [s for s in STEPS
                       if e.get(s, {}).get("status") in ("SKIPPED", "N/A")]
            total_skipped += len(skipped)
            done = ran + len(skipped)
            mark = "COMPLETE" if done == len(STEPS) else "INCOMPLETE"
            tail = f"  [{len(skipped)} SKIPPED: {', '.join(skipped)}]" if skipped else ""
            print(f"  {mark:10} {c}: {ran} of {len(STEPS)} RUN{tail}")
        print(f"\n  {len(cubes)} cubes | {len(incomplete)} incomplete | "
              f"{total_skipped} step(s) SKIPPED with a reason")
        if total_skipped:
            print("  NOTE: a SKIPPED step satisfies this gate by design - the "
                  "runbook accepts SKIPPED-with-a-reason. It did NOT run.")

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

def zero_output_runs(root=None) -> list[str]:
    """Runs that COMPLETED and produced nothing (B1855 / L566).

    The signature of a silently-pruned run, confirmed causally at S6-B1849a:
    demand pruning kept 2 of 33 producers, the screener passed 0/10 on every
    one of 249 days, and the run exited 0 with no error. Same window with
    `DEMAND_PRUNING=0` produced 20 trades and 75 files.

    This is deliberately INDEPENDENT of the post-config ledger. `#223` accepts
    `N/A`, and I dispositioned four probe dirs `N/A` myself for a reason I
    still think correct - which removed the only check positioned to see
    `trades=0`. A detector that a waiver can switch off is not a detector.

    Returns dir names, never raises: a broken probe must not break a caller.
    """
    import json as _json
    import pathlib as _p

    base = _p.Path(root) if root else ROOT
    out = []
    for d in sorted(base.glob("output_*")):
        st = d / "engine_state.json"
        if not st.is_file():
            continue
        try:
            js = _json.loads(st.read_text(encoding="utf-8"))
        except Exception:
            continue
        if js.get("status") != "complete":
            continue                      # still running is not empty
        trades = js.get("trades_so_far")
        if trades is None:
            continue                      # older schema: cannot judge
        if trades == 0 and not (d / "trade_log.csv").is_file():
            out.append(d.name)
    return out
