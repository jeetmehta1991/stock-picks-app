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
    # B1887: VERBATIM from the B1856 monitor prompt. It greps for the fire
    # count using the ticker-FILE size, 200, while the screener reports
    # against the PIT-ACTIVE universe, 185. It would have reported "no fires"
    # every 11 minutes on a run that fired on 29 of 29 screen-days, and its
    # own decision rule would then have confirmed a launch blocker backwards.
    "scan_monitor_pattern_unverified": (
        "awk '/^2026-08-21 2[0-9]:/' backtest_v2.log | grep -oE "
        '"[0-9]+/200 passed" | sort | uniq -c | tail -5 - any non-zero N/200 '
        "means the approved window FIRES at 200 tickers and the blocker clears",
        True,
        {"blobs": ["grep -oE \"[0-9]+/200 passed\" backtest_v2.log - any "
                   "non-zero N/200 means the window fires and the blocker "
                   "clears"]},
    ),
    # B1879: VERBATIM from b1845_timing.py, the script whose three arms all
    # fired ZERO and produced a NEUTRAL verdict I nearly published. The launch
    # line named no interpreter, so it ran under the SYSTEM python: 2 of 33
    # producers kept, 0 trades. `sys.executable` on the identical config keeps
    # 3 of 33 and fires 10.
    "scan_bare_python_launch": (
        'p = subprocess.run(cmd, cwd=R, env=env, capture_output=True) with '
        'cmd = ["python", "backtest/run_phase1a.py", "--tickers-file", '
        '"output_audit/_t10.txt", "--screen-pool-workers", "0"]',
        True,
        {"cmds": ['subprocess.run(["python", "backtest/run_phase1a.py", '
                  '"--tickers-file", "output_audit/_t10.txt"])']},
    ),
    # B1865: VERBATIM from this session - the monitor prompt armed for the
    # B1849 causal test. It promises a periodic unconditional report and has
    # no stall clause at all, so it could report a hung run as healthy, which
    # is what three ticks did at B1555.
    "scan_monitor_without_stall_check": (
        "PERIODIC UNCONDITIONAL RUN REPORT - B1849 causal test. Report EVERY "
        "time this fires. Do not withhold the report because nothing changed. "
        "Silence is correct only when nothing is running.",
        True,
        {"blobs": ["PERIODIC UNCONDITIONAL RUN REPORT - B1849 causal test. "
                   "Report EVERY time this fires. Do not withhold the report "
                   "because nothing changed. Silence is correct only when "
                   "nothing is running."]},
    ),
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
    "scan_unverified_count": (
        "317 tickets created in the last 48h, 271 already closed.",
        True,
        {"tool_text": "{}"},
    ),
    "scan_partial_distribution": (
        "388 closed 149 done 96 open - 261 of 649 are not verified closed",
        True,
        {},
    ),
    "scan_partial_read": (
        "Batch 1 of 20 hand-verified - 2 complete, 17 open. On batch 1's rate "
        "roughly 12 more of the 138 will prove complete.",
        True,
        {"tool_text": "sed -n '1,20p' allrows.txt | head -35"},
    ),
    "scan_row_vs_ticket": (
        "OPEN rows read end to end : 214. still OPEN 64, EXECUTED 140.",
        True,
        {"tool_text": "python b1795_apply.py EXECUTION_QUEUE.md"},
    ),
    # S6-B1705e: RECONSTRUCTED, not verbatim - the original wording was not
    # kept, which is the same gap S6-B1761c records for three other gates. The
    # SHAPE is exact and comes from the retraction row (S6-B1705g): a Sharpe
    # figure quoted as measured that came from `rng.normal(1, 3, 30)`.
    # B1910 (S6-B1909c) - the incident, near-verbatim: a duplicate-exit
    # collapse reported as undocumented because the CODE COMMENT beside it
    # names only the other two. LEARNINGS carries it THREE times, at 100.0pct
    # over n=7,319. Nothing required the grep that caught it.
    "scan_novelty_claim_without_search": (
        "atr_trail_mae_conditional == atr_trail_1x is an undocumented third "
        "collapse, absent from the B1593 list",
        True,
        {},
    ),
    # B1924 - VERBATIM, recovered from L411: "my repeated `Get-Process
    # python | Stop-Process -Force` sweeps this turn". That command wedged the
    # Windows WMI service and blocked every pandas import on the box, pyramid
    # included. S6-B1865a exempted this gate for want of the verbatim text;
    # the lesson had preserved it.
    "scan_bulk_process_kill": (
        "Get-Process python | Stop-Process -Force",
        True,
        {"cmds": ["Get-Process python | Stop-Process -Force"]},
    ),
    # B1924 - DERIVED, and labelled so. L407 records the defect (a launch that
    # never named --screen-pool-workers ran SEQUENTIAL on a 12-core box; pool=10
    # measured 1.53x) but quotes no command. This is the REAL b1576 invocation
    # with the flag removed. **A derived fixture labelled as derived is evidence
    # about the gate; the same fixture labelled as an incident is what
    # S6-B1865a correctly refused to write.**
    "scan_launch_missing_pool_workers": (
        "DERIVED FIXTURE (not verbatim): the real b1576 launch, flag removed",
        True,
        {"blobs": ["PYTHONPATH=. python backtest/run_phase1a.py "
                   "--tickers-file output_audit/_sweep_100.txt --phase 1a-beta "
                   "--cube-isolation --no-agents --no-news --no-git "
                   "--no-walk-forward --start 2024-05-05 --end 2026-05-05 "
                   "--max-run-hours 6.0 --output-dir output_cfg1"]},
    ),
    "scan_synthetic_provenance": (
        "The boundary probe measured n=29 -> None and n=30 -> a Sharpe of "
        "2.422, so the floor is real.",
        True,
        {"tool_text": "pnl = rng.normal(1, 3, 30)"},
    ),
    # B1803: the incident is the ABSENCE the directive was issued about - a
    # turn report that ends without any ticket count. Verbatim from the turn
    # before the directive: a full compliance block, no ledger state anywhere.
    "scan_ticket_counts_missing": (
        "Pyramid 1004 passed / 3 skipped. Commit f9cd80c2c, pushed. "
        "CHECKLIST compliance - #234 all four Phase-5 members satisfied.",
        True,
        {},
    ),
    # S6-B1761c / B1809. VERBATIM from B1806, this session: the gate reported
    # "3 of 3 required member(s) NOT satisfied" on a response that listed all
    # three skills. The block sat at the TOP and the phrase appeared again in
    # prose below, so the LAST-occurrence window opened past it. must_fire is
    # FALSE - these are the words it must NOT fire on.
    "scan_skill_block_incomplete": (
        "**SKILLS INVOKED** - `execution-discipline` **ALWAYS-ON** - "
        "`fable-mode` **FULLY LOADED** - `llm-council` **NOT-TRIGGERED**\n\n"
        "`#274` - every turn reports ticket counts by group, same standing as "
        "SKILLS INVOKED.",
        False,
        {},
    ),
    # S6-B1761c / B1809. RECONSTRUCTED - S6-B1740a records the incident but not
    # the sentence: "B1739 built two gates, edited three docs and committed
    # without invoking Skill(execution-discipline). Disclosed in the response
    # but NOT ticketed until the new gate blocked the turn." Two finding
    # markers, zero queue rows.
    "scan_findings_vs_tickets": (
        "The retroactive sweep is not built. The tripwire table has no "
        "enforcement and that is a defect I am carrying forward.",
        True,
        {"rows": 0},
    ),
    # S6-B1761c / B1809. VERBATIM tail of a real turn report that ended with no
    # confirmation block - the shape the B1726 owner directive was issued about.
    "scan_missing_skill_confirmation": (
        "Pyramid 1004 passed / 3 skipped. Commit f9cd80c2c, pushed. "
        "CHECKLIST compliance - #234 all four Phase-5 members satisfied.",
        True,
        {},
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


# B1805: ONE INCIDENT PROVES ONE PATH.
#
# `scan_response_gates` carried an incident, an injectable seam, and passed the
# #240 sweep on every run - on the single sentence "Reverting.". Its stem is the
# one that does NOT end in `e`, so the naive `stem + "ing"` expansion happened to
# produce the right form for exactly that verb. **Deleting, removing, disabling,
# restoring and wiring were all unmatched and nothing could see it.**
#
# So a gate whose markers are GENERATED needs an incident per generation branch,
# not one per gate. These are additional (text, must_fire, state) cases checked
# alongside the primary entry. Kept in a separate dict deliberately: INCIDENTS
# stays a 3-tuple per gate, so the six existing consumers are untouched.
# B1916 (S6-B1865a / S6-B1761b): gates that take POSITIONAL arguments.
#
# `INCIDENTS` assumes one calling convention - fn(entries, **state) - so a gate
# with a different signature could not be expressed in it, and "cannot be
# expressed here" was recorded in test_b1762's EXEMPT dict as **"no seam"**.
#
# MEASURED: `scan_postfix_recheck` and `scan_orphan_rule` are PURE FUNCTIONS OF
# PLAIN ARGUMENTS - the most testable shape in the file. Calling them directly
# fires them, and flipping one argument silences them. The obstacle was the
# vocabulary, not the gates: **a corpus that cannot express a case makes it
# invisible rather than absent.**
#
# name -> (args, should_fire, what the case is)
PURE_INCIDENTS: dict[str, list[tuple[tuple, bool, str]]] = {
    # B1930: a gate taking ONLY `entries` is drivable by CONSTRUCTING entries.
    # B1925 and B1927 both did exactly that in their pins without noticing it
    # dissolved this gate's "no seam" exemption.
    "scan_unverified_cause": [
        (([{"type": "assistant", "message": {"content": [
            {"type": "text",
             "text": "The probable cause is the pool teardown wedging on "
                     "exit."}]}}],), True,
         "B1335 rule 3 - a CAUSE stated with no proof language anywhere in "
         "the turn. DERIVED causal claims must be worded 'hypothesis'."),
        (([{"type": "assistant", "message": {"content": [
            {"type": "text",
             "text": "The probable cause is the pool teardown; MEASURED by "
                     "rerunning it, exit code 127."}]}}],), False,
         "the same claim WITH proof language - must go quiet, or the gate "
         "punishes the evidence it asks for"),
    ],
    "scan_orphan_rule": [
        (("\n### L900\n\nA generalised rule: always verify X before Y.\n",
          "", "", ["L900"]), True,
         "L464/#197 - an L-entry stating a RULE, referenced in neither "
         "CHECKLIST nor the skill. A rule recorded only in LEARNINGS is a "
         "story, not a gate."),
        (("\n### L900\n\nA generalised rule: always verify X before Y.\n",
          "see L900", "", ["L900"]), False,
         "anchored in CHECKLIST - must go quiet, or the gate would punish "
         "the very anchoring it asks for"),
        (("\n### L901\n\nThis is a **record-of-fact** measurement only.\n",
          "", "", ["L901"]), False,
         "B1626 explicit opt-out - an entry that records a measurement rather "
         "than a rule"),
    ],
    "scan_postfix_recheck": [
        (("B1: fixed the thing", ["scripts/verify_turn_compliance.py"]), True,
         "L467/#196 - a FIX commit touching no downstream artifact and no "
         "queue entry. The roster relabel was reverted by the next "
         "regeneration because the fix belonged in the GENERATOR."),
        (("B1: fixed the thing",
          ["scripts/verify_turn_compliance.py", "EXECUTION_QUEUE.md"]), False,
         "the queue entry IS the disclosure the gate asks for - must go quiet"),
    ],
}


EXTRA_INCIDENTS: dict[str, list[tuple[str, bool, dict]]] = {
    "scan_bulk_process_kill": [
        # a TARGETED kill is the correct form and must stay quiet - the defect
        # is killing every python on the box, not stopping a known process
        ("targeted", False, {"cmds": ["Stop-Process -Id 12345 -Force"]}),
        ("read-only", False, {"cmds": ["Get-Process python"]}),
    ],
    "scan_launch_missing_pool_workers": [
        # the same launch WITH the flag - must go quiet, or the gate would
        # punish the compliance it asks for
        ("flag present", False,
         {"blobs": ["PYTHONPATH=. python backtest/run_phase1a.py "
                    "--tickers-file output_audit/_sweep_100.txt "
                    "--screen-pool-workers 0 --output-dir output_cfg1"]}),
    ],
    "scan_novelty_claim_without_search": [
        # the SAME finding made properly - the search is named in-clause
        ("grepped LEARNINGS.md and EXECUTION_QUEUE and the collapse is "
         "undocumented, 0 matches", False, {}),
        # the RETRACTION must not fire. Self-reference has hit this file ~13
        # times, so the escape is built in rather than bolted on afterwards.
        ("I called it undocumented and LEARNINGS already carries it three "
         "times", False, {}),
        # a clause-scoped check: a grep named in a DIFFERENT sentence must
        # NOT cover a bare claim made here
        ("I grepped the ledger earlier. This one is undocumented", True, {}),
    ],
    "scan_skill_block_incomplete": [
        # the must-FIRE half: a block naming only two of the three
        ("**SKILLS INVOKED** - `execution-discipline` **ALWAYS-ON** - "
         "`fable-mode` **FULLY LOADED**", True, {}),
    ],
    "scan_findings_vs_tickets": [
        # same findings, but ticketed - must be QUIET
        ("The retroactive sweep is not built. The tripwire table has no "
         "enforcement and that is a defect I am carrying forward.",
         False, {"rows": 2}),
    ],
    "scan_missing_skill_confirmation": [
        # the block present - must be QUIET
        ("SKILLS INVOKED - execution-discipline ALWAYS-ON. Pyramid green.",
         False, {}),
    ],
    "scan_response_gates": [
        # the E-STEM PROGRESSIVE branch - silently unmatched before B1804
        ("I am deleting the stale output directory now.", True,
         {"tree_changed": False, "queue_touched": True}),
        # and the substring branch: this must NOT fire (S6-B1798b)
        ("The behaviour is undocumented, so I read the source instead.", False,
         {"tree_changed": False, "queue_touched": True}),
    ],
}


def all_incidents(name: str) -> list[tuple[str, bool, dict]]:
    """Primary incident plus every extra branch recorded for `name`."""
    out = []
    if name in INCIDENTS:
        out.append(INCIDENTS[name])
    out.extend(EXTRA_INCIDENTS.get(name, []))
    return out


# B1762c: state that NEUTRALISES a gate's non-text inputs for the negative
# control. The control asks "does ordinary prose trip this gate?" - so a gate
# that also reads the live repo must be told there is nothing there, or it
# answers a different question and reports a false positive.
#
# This is L517 again in the opposite direction: the control run must supply the
# state that isolates TEXT, exactly as the incident run supplies the state the
# incident had. A harness that gets either wrong reports on itself.
NEUTRAL: dict[str, dict] = {
    # B1778: this gate reads TOOL text for proof-of-computation, so the
    # control must supply a computing call or it measures the gate
    # doing its job.
    "scan_unverified_count": {"tool_text": "execution_queue value_counts"},
    # B1769: the per-turn gate fires on ABSENCE, so the neutral state for a
    # text-only control must supply a row - otherwise the control measures the
    # gate doing its job and reports it as a false positive.
    "scan_queue_not_updated": {"rows": ["| **S6-X** | **DONE** | - | x |"]},
    "scan_queue_vocabulary": {"rows": []},
    # B1771: this gate reads LIVE git state (docs vs code touched). The
    # control asks "does ordinary prose trip it?", so the repo state must
    # be neutralised or the control measures the working tree instead of
    # the text - L517, third time this exact shape has appeared.
    "scan_prose_only_rule": {"docs_touched": False, "code_touched": False},
    "scan_ungated_addition": {"added_rules": []},
    "scan_shell_substitution": {"tool_text": ""},
    # B1794: this gate reads TOOL text for truncation markers, so the
    # control must supply a clean tool call or it measures the gate working.
    "scan_partial_read": {"tool_text": ""},
    # B1795: reads TOOL text for the queue path; neutralise it for the
    # text-only control or it measures the gate working.
    "scan_row_vs_ticket": {"tool_text": ""},
    # reads TOOL text for a generator; neutralise for the text-only control
    "scan_synthetic_provenance": {"tool_text": ""},
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
