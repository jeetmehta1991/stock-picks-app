#!/usr/bin/env python
"""The VERBATIM text that motivated each gate, plus the STATE it occurred in.

B1760. The owner asked why `scan_miss_capture_complete` was never tested against
the sentence that prompted it. The answer is that my probe strings were BUILT
FROM my own marker list:

    markers  = ("i was wrong", ..., "owner caught", ...)
    probes   = ("i was wrong about that", "owner caught it", ...)

**The test was circular.** It proved the list matches itself. Every gate this
session was validated the same way - invented strings seeded from the code under
test - which is why five of them passed their proofs and still missed the real
thing.

B1761 (the retroactive sweep). The first corpus stored a bare SENTENCE, and four
gates then looked silent. **Only one was actually broken.** The other three are
HYBRID gates that need the surrounding block and/or the repo state the incident
occurred in, and a fragment starves them into a correct no-op:

    scan_response_gates      needs tree_changed=False  (claim vs repo state)
    scan_false_skill_status  needs the "SKILLS INVOKED:" header AND injected=True
    scan_prose_only_rule     needs docs_touched / code_touched

**An incident is not a sentence. It is the text AS THE GATE SEES IT, plus the
state it saw.** Storing less manufactures FALSE FAILURES, which is the exact
mirror of the circular probes that manufactured false passes - both are a
harness reporting on itself instead of on the gate.

Entries are `(text, must_fire, state)`. Adding a gate means adding its incident
here; a gate with no entry is unproven regardless of how many probes pass.

HAND-RUN-ONLY as a script; consumed by `test_b1760_gates_fire_on_real_incidents`
and by `scripts/sweep_gate_incidents.py`.
"""
from __future__ import annotations

# gate name -> (verbatim text from the incident, must_fire, state kwargs)
#
# Every entry is REAL TEXT from this session's transcript. Where a gate's
# incident produced several sentences, the one chosen is the one that appeared
# in the response the owner reacted to.
INCIDENTS: dict[str, tuple[str, bool, dict]] = {
    "scan_miss_capture_complete": (
        "So a checklist item with no mechanism is enforced solely by my "
        "remembering to consult it - which is the failure itself.",
        True,
        {"observed": {"LEARNINGS.md entry": False}},
    ),
    "scan_response_gates": (
        "I am not shipping it. Reverting.",
        True,
        {"tree_changed": False},
    ),
    "scan_uncosted_probe": (
        "Split the next_pivot_target rows by exit_reason and compute rho "
        "separately for each. Offline on cached cubes, seconds.",
        True,
        {},
    ),
    "scan_false_skill_status": (
        "SKILLS INVOKED:\n"
        "execution-discipline - ALWAYS-ON (12-bullet hook summary; full skill "
        "not invoked this turn)",
        True,
        {"injected": True},
    ),
    "scan_uninspected_constant": (
        "MIN_N = 30 is the floor, so 70pct of the grid sits below it.",
        True,
        {"tool_text": "{}"},
    ),
    "scan_prose_only_rule": (
        "Remediation: #201 needs a provenance half. Not built.",
        True,
        {"docs_touched": True, "code_touched": False},
    ),
    "scan_retroactive_sweep": (
        "Fixed by stemming the verbs. This class is now closed.",
        True,
        {},
    ),
    "scan_compliance_is_content": (
        "CHECKLIST compliance statement: all items applied and satisfied.",
        True,
        {},
    ),
    "scan_ungated_addition": (
        "L516 + L517, CHECKLIST #240 + #241, SKILL section, 8 queue rows.",
        True,
        {"added_rules": ["240", "241"]},
    ),
    "scan_shell_substitution": (
        "",
        True,
        {"tool_text": 'git commit -q -m "RISK: a blanket Bash(*) runs '
                      'destructive commands (`git reset --hard`, `rm -rf`) '
                      'without a prompt."'},
    ),
    # B1767: a REGRESSION incident. Not every gate is motivated by something it
    # MISSED - this one blocked a clean turn because "free" matched inside
    # "freely". The words that motivated the fix are words it must NOT fire on,
    # so must_fire is False. A corpus that only stores misses cannot pin the
    # false-positive half of a gate's behaviour.
    "scan_unmeasured_quantity": (
        "the status column carries status OR priority OR a headline, "
        "chosen freely per row.",
        False,
        {},
    ),
    "scan_queue_vocabulary": (
        "",
        True,
        {"rows": ["| **S6-B1757c** | **ANSWERED** | - | a defect filed as an "
                  "answer, with no mechanism |"]},
    ),
    "scan_queue_not_updated": (
        "an ordinary turn report that records no queue row and declares nothing",
        True,
        {"rows": []},
    ),
    # NEGATIVE control - ordinary reporting prose that must NOT trip anything.
    # Note it is a bare sentence, so gates that legitimately require RESPONSE
    # STRUCTURE (a SKILLS block, a compliance block) are excluded by the sweep
    # rather than counted as false positives.
    "_negative_control": (
        "Wave 1 completed at 2026-05-05 with both cubes written and the "
        "monitor reporting free RAM above the floor throughout.",
        False,
        {},
    ),
}


# B1762c: state that NEUTRALISES a gate's non-text inputs for the negative
# control. The control asks "does ordinary prose trip this gate?" - so a gate
# that also reads the live repo must be told there is nothing there, or it
# answers a different question and reports a false positive.
#
# This is L517 again in the opposite direction: the control run must supply the
# state that isolates TEXT, exactly as the incident run supplies the state the
# incident had. A harness that gets either wrong reports on itself.
NEUTRAL: dict[str, dict] = {
    # B1769: the per-turn gate fires on ABSENCE, so the neutral state for a
    # text-only control must supply a row - otherwise the control measures the
    # gate doing its job and reports it as a false positive.
    "scan_queue_not_updated": {"rows": ["| **S6-X** | **DONE** | - | x |"]},
    "scan_queue_vocabulary": {"rows": []},
    "scan_ungated_addition": {"added_rules": []},
    "scan_shell_substitution": {"tool_text": ""},
}


def main() -> int:
    print(f"gate incident corpus: {len(INCIDENTS) - 1} gates + 1 negative control")
    for name, (text, fires, state) in INCIDENTS.items():
        print(f"  {'FIRE' if fires else 'QUIET':<5} {name}  state={state or '{}'}")
        print(f"          {text[:88]!r}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
