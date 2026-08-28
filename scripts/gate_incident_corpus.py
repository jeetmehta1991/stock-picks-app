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
    # B1931: VERDICT_PATTERNS is the trigger, not the docstring's prose.
    # "cannot clear" / "no combination passes" fire; a literal `N of M`
    # anywhere in the same text block clears them.
    "scan_verdict_denominators": [
        (([{"type": "assistant", "message": {"content": [
            {"type": "text",
             "text": "The config cannot clear the Sharpe gate at any "
                     "level."}]}}],), True,
         "a capability verdict with no scope - the reader cannot tell "
         "whether it failed everywhere or in one cell"),
        (([{"type": "assistant", "message": {"content": [
            {"type": "text",
             "text": "No combination passes in 0 of 400 "
                     "combinations."}]}}],), False,
         "same verdict WITH its denominator - must go quiet"),
    ],
    # B1931: MISS_PHRASES, not MISS_MARKERS. The docstring says it plainly -
    # "the owner pointing out an error is not the trigger; ACKNOWLEDGING it
    # is" - so the vocabulary is FIRST-PERSON.
    "scan_unrecorded_miss": [
        (([{"type": "assistant", "message": {"content": [
            {"type": "text",
             "text": "I was wrong about the schema - the artifacts carry "
                     "an older one."}]}}], False), True,
         "#194/L446 - a miss ACKNOWLEDGED with LEARNINGS.md untouched"),
        (([{"type": "assistant", "message": {"content": [
            {"type": "text",
             "text": "I was wrong about the schema - the artifacts carry "
                     "an older one."}]}}], True), False,
         "the same acknowledgment WITH the L-entry written - must go quiet"),
        (([{"type": "assistant", "message": {"content": [
            {"type": "text",
             "text": "The owner pointed out an error in the row."}]}}],
          False), False,
         "the OWNER naming an error is not the author acknowledging one - "
         "the distinction the docstring draws, pinned"),
    ],
    # B1934: both of these were driven by a working `entries` fixture in
    # B1925's and B1927's own pins, while the register still called them
    # unseamed. The fifth wrong reason it has carried.
    "scan_unverified_universe": [
        (([{"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {
                "command": "python backtest/run_phase1a.py --phase 1a-beta "
                           "--output-dir output_cfg1"}}]}}],), True,
         "#193/L445 - a config LAUNCHED with no verify_universe_artifact.py "
         "run in the same turn. Two configs once searched an abandoned A-C "
         "chunk for 3.3 h each because nobody looked at the ticker list."),
        (([{"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {
                "command": "python - <<'PY'\nbase = \"python "
                           "backtest/run_phase1a.py --output-dir "
                           "output_cfg1\"\nPY\n"}}]}}],), False,
         "B1925 - the same command QUOTED inside a heredoc body is data "
         "handed to an interpreter, not a launch that ran"),
        (([{"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {
                "command": "python backtest/run_phase1a.py --phase 1a-beta "
                           "--output-dir output_cfg1"}}]}},
           {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {
                "command": "python scripts/verify_universe_artifact.py "
                           "output_cfg1"}}]}}],), False,
         "the verification the gate asks for, run in the same turn"),
    ],
    "scan_unmonitored_launch": [
        (([{"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {
                "command": "nohup python backtest/run_phase1a.py "
                           "--output-dir output_cfg1 &"}}]}}],), True,
         "L420 - three long runs launched with no monitor, AFTER the rule "
         "forbidding it was written"),
        (([{"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "CronCreate", "input": {
                "cron": "0 * * * *",
                "prompt": "check and push; do not withhold the report"}}]}},
           {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {
                "command": "nohup python backtest/run_phase1a.py "
                           "--output-dir output_cfg1 &"}}]}}],), False,
         "an hourly UNCONDITIONAL arm in the same turn - both halves of "
         "L424, and the gate must not punish the compliance it demands"),
    ],
    # B1940: excused as unseamed and 3/3 drivable on STRUCTURAL_CLAIMS.
    # Sixth false reason this register has carried.
    "scan_unverified_structure": [
        (([{"type": "assistant", "message": {"content": [
            {"type": "text",
             "text": "The producer is wired into the engine."}]}}],), True,
         "#215/L489 - a claim about CODE STRUCTURE in a turn that never "
         "opened a file"),
        (([{"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Read",
             "input": {"file_path": "backtest/signals/screener.py"}}]}},
           {"type": "assistant", "message": {"content": [
            {"type": "text",
             "text": "The producer is wired into the engine."}]}}],), False,
         "the same claim after a Read - the gate must not punish the "
         "inspection it demands"),
        (([{"type": "assistant", "message": {"content": [
            {"type": "text",
             "text": "The run took 198 minutes."}]}}],), False,
         "a measurement, not a structural claim"),
    ],
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
    # ---- S6-B2263 batch 1 (B2291): must-QUIET cases for FIRE_ONLY_LEGACY gates.
    # A gate that refuses EVERYTHING satisfies every must-FIRE case ever written
    # for it (L686), so the accept-path is the only arm that proves the gate
    # DISCRIMINATES. Each case below is a VALID input the gate must let through,
    # written against that gate's own signature - the four take different state,
    # so no generic fixture exists and none is faked.
    # ---- S6-B2292 batch 2 (B2303): must-QUIET cases, six more gates.
    # Same rule as batch 1: written per-gate against each signature, because the
    # six take different state (text / rows / docs_touched+code_touched /
    # added_rules / tool_text). No generic fixture exists and none is faked.
    "scan_prose_only_rule": [
        # the compliant shape: a doc rule shipped WITH its mechanism in the same
        # turn. If this fired, the rule would be unsatisfiable - every doc edit
        # would be a violation regardless of whether a gate accompanied it.
        ("Remediation: #201 needs a provenance half. Shipped with its pin.", False,
         {"docs_touched": True, "code_touched": True}),
    ],
    "scan_queue_not_updated": [
        # a turn that DID record a queue row. The must-FIRE case passes rows=[];
        # quiet here is the whole point, otherwise every turn is non-compliant.
        ("a turn report that records its queue row", False,
         {"rows": ["| **S6-B2303** | **EXECUTED** | P2 | **batch 2** | shipped |"]}),
    ],
    "scan_ungated_addition": [
        # rules added WITH a named mechanism. The must-FIRE case lists rule
        # numbers with nothing enforcing them.
        ("L516 + L517, CHECKLIST #240 + #241, pinned by "
         "test_b1762_every_scan_gate_has_a_corpus_entry.", False,
         {"added_rules": []}),
    ],
    "scan_compliance_is_content": [
        # a compliance block that NAMES items and statuses, which is what #238
        # requires. The must-FIRE case is the content-free version.
        # B2303 CORRECTION: the first version of this case named three items
        # but carried ZERO status markers, so the gate correctly FIRED. #238
        # requires BOTH halves - items cited AND a per-item status - and I had
        # read only the first half of its own docstring. The gate was right.
        ("CHECKLIST compliance statement: #69 PYRAMID satisfied, green 1193/3; "
         "#258 LEDGER COUNT satisfied, executed this turn; #270 complete read "
         "done, 19 of 19 blocks.", False,
         {}),
    ],
    "scan_partial_distribution": [
        # a distribution whose parts are stated against a named total, rather
        # than a residual left implicit.
        ("Verdicts across all 4,200 cells: 3,094 BELOW_POWER_FLOOR, 1,091 "
         "NO_EXIT_SELECTABLE, 15 ZERO_FIRES - 4,200 of 4,200 accounted for.",
         False, {}),
    ],
    "scan_retroactive_sweep": [
        # a class closed WITH a sweep stated. The must-FIRE case declares a class
        # closed with no statement of what else was scanned.
        ("Fixed by stemming the verbs. Retroactive sweep: scanned all 6 sibling "
         "call sites, 1 shared the defect and is fixed, 5 were already correct.",
         False, {}),
    ],
    "scan_shell_substitution": [
        # the SAME shape as the must-FIRE incident with the substitution removed:
        # a commit message describing the danger in plain words. If this fires,
        # the gate is refusing all -c strings rather than live substitution.
        ("", False,
         {"tool_text": 'git commit -q -m "RISK: a blanket Bash(*) runs '
                       'destructive commands without a prompt."'}),
    ],
    "scan_bare_python_launch": [
        # the venv interpreter named EXPLICITLY - the compliant form the gate
        # exists to require. Firing here would make the rule unsatisfiable.
        ("launch names its interpreter", False,
         {"cmds": ['subprocess.run([str(VENV_PY), "backtest/run_phase1a.py", '
                   '"--tickers-file", "output_audit/_t10.txt"])']}),
    ],
    "scan_uninspected_constant": [
        # the must-FIRE incident's prose, but with a tool call that ACTUALLY
        # opened the constant. Quiet here is the whole point of #222: the rule
        # is "look before you cite", not "never cite".
        ("MIN_N = 30 is the floor, so 70pct of the grid sits below it.", False,
         {"tool_text": 'grep -n "MIN_N" backtest/config.py'}),
    ],
    "scan_queue_vocabulary": [
        # a terminal class from the closed vocabulary. The must-FIRE case uses
        # ANSWERED, which is off-vocabulary; EXECUTED is the sanctioned form.
        ("", False,
         {"rows": ["| **S6-B2291** | **EXECUTED** | P2 | **a row using a "
                   "sanctioned class** | shipped with its pyramid |"]}),
    ],

    # B2273/B2275 (L691): the FRESHNESS arm of the counts gate, added after it
    # caught its own author TWICE within three turns. The block below is
    # verbatim-shaped compliant output - six classes, a delta column, the
    # correct numbers - and it is a DEFECT because the counter never ran that
    # turn, so the figures were carried from the previous close. Presence and
    # format were always gated; freshness was not, and the two gates covering
    # this artifact left a seam neither was wrong about.
    "scan_ticket_counts_missing": [
        ("Ticket counts (scripts/queue_state.py, executed this turn):\n\n"
         "| Class | Count | Delta |\n|---|---|---|\n"
         "| EXECUTED | 1481 | 0 |\n| DROPPED | 24 | 0 |\n"
         "| BLOCKED | 5 | 0 |\n| DEFERRED | 11 | 0 |\n"
         "| OPEN | 14 | 0 |\n| RUNNING | 1 | 0 |\n",
         True, {"tool_text": "git status --porcelain"}),
        # the must-QUIET arm: the SAME block with the counter actually run.
        # Without it, a gate that refused every counts block would satisfy the
        # entry above and look correct (L594/L686).
        ("Ticket counts (scripts/queue_state.py, executed this turn):\n\n"
         "| Class | Count | Delta |\n|---|---|---|\n"
         "| EXECUTED | 1481 | 0 |\n| DROPPED | 24 | 0 |\n"
         "| BLOCKED | 5 | 0 |\n| DEFERRED | 11 | 0 |\n"
         "| OPEN | 14 | 0 |\n| RUNNING | 1 | 0 |\n",
         False, {"tool_text": "python scripts/queue_state.py"}),
    ],
    # B2005 (G2, owner-approved): the verbatim B1908 incident - a COMMENT's
    # number quoted as measured, cleared by `.py` in FIGURE_SOURCES.
    "scan_synthetic_provenance": [
        ("tighten_breaker_block.py states the measured spearman as -0.779 "
         "across the graded rows", True, {}),
        # the mandated compliant style stays QUIET: a run token is present
        ("the rho of -0.779 was measured by this turn's probe over "
         "b1715_leak_span21.json", False, {}),
    ],
    # B1965 - the incident VERBATIM: S6-B1790d states a count and names none
    # of the 3. Its batch's partition was 148 = 7 + 138 + 3 and only the 7
    # promoted rows are identifiable, because promotion changed their state.
    "scan_ticket_claim_without_pin": [
        # the verbatim S6-B1562a incident: EXECUTED, "A2 shipped", pyramid
        # green - and NOTHING checkable named. The B1788 review could only
        # mark such rows NOT_CHECKABLE forever.
        ("EXECUTED row claims shipped code, names no artifact", True,
         {"rows": ["| **S6-B1562a** | **EXECUTED** | - | **DONE** | A2 "
                   "shipped (DATA_LOAD_START 2021-05-05 -> 2021-05-06) PLUS "
                   "end-anchored coverage. 20-ticker run universe: 0/20 -> "
                   "18/20 cache hits. Pyramid 907/2 GREEN. L436. |"]}),
        ("a code row naming its pin must go quiet", False,
         {"rows": ["| **S6-B2033a** | **EXECUTED** | P1 | **B2075: THE SWEEP "
                   "LEG IS REQUIRED AGAIN (owner C12, pin "
                   "test_b2075_sweep_leg_is_required_again)** | gate fixed. |"]}),
        ("an EXECUTED analysis row with no code claim must go quiet", False,
         {"rows": ["| **S6-B2080x** | **EXECUTED** | P1 | **THE FLOOR "
                   "MEASURED - 0.2245 at the full pool** | bootstrap record. |"]}),
        ("an OPEN row with a code marker must go quiet - the rule binds "
         "EXECUTED only", False,
         {"rows": ["| **S6-B1779x** | **OPEN** | P2 | _reason:_ the fix will "
                   "be implemented next batch. |"]}),
    ],
    "scan_count_without_members": [
        ("| **S6-B1790d** | **OPEN** | P2 | **3 ROWS: their batch changed "
         "code but added no durable definition** |", True,
         {"rows": ["| **S6-B1790d** | **OPEN** | P2 | **3 ROWS: their batch "
                   "changed code but added no durable definition** |"]}),
        ("a row naming its members must go quiet", False,
         {"rows": ["| **S6-B1964f** | **OPEN** | P1 | **7 OPEN tickets state "
                   "a count: S6-B1589c, S6-B1636a, S6-B1788d** |"]}),
        ("a row naming the SELECTING QUERY must go quiet - the set is "
         "recoverable even without the ids", False,
         {"rows": ["| **S6-B1963c** | **EXECUTED** | P0 | **46 of 60 OPEN "
                   "tickets carry a count, per queue_state** |"]}),
        ("a row stating no count at all", False,
         {"rows": ["| **S6-B1900a** | **EXECUTED** | P0 | **the harvester "
                   "ranks on median now** |"]}),
        # B1968: a row naming GATE members must go quiet. MEMBER_EVIDENCE
        # listed only ticket ids and query tools, so this FIRED - the gate
        # counted "member" as "ticket id" because every instance in front of
        # me when #280 was built counted tickets (L597).
        ("a row naming GATE members, not ticket ids", False,
         {"rows": ["| **S6-B1967d** | **EXECUTED** | P0 | **10 gates read "
                   "tool text. 8 remain: scan_partial_read, "
                   "scan_row_vs_ticket, scan_uncosted_probe** |"]}),
    ],
    # B1944b: the must-QUIET case this gate never had - and the one that
    # would have caught B1943. `COUNT_PROOF` omitted `queue_state`, the
    # project's canonical counter, so the HONEST path was rejected while
    # `grep -c` passed. This case fails before that fix and passes after: a
    # regression test for the defect, not a decoration.
    "scan_unverified_count": [
        ("317 tickets created in the last 48h, 271 already closed.", False,
         {"tool_text": "python scripts/queue_state.py"}),
        # B1944b: the case TEXT is the gate's INPUT, not a label for it.
        # This first read "the same claim with an unrelated tool call
        # must STILL fire" - a description, carrying no count claim, so
        # the gate correctly stayed quiet and the case failed.
        ("317 tickets created in the last 48h, 271 already closed.", True,
         {"tool_text": "cat README.md"}),
    ],
    # B1936: L591 applied - CALL a gate before believing its exemption reason.
    # All four incidents are preserved VERBATIM in the gates' own docstrings,
    # which is exactly what "incident text not preserved" denied. These take
    # KWARGS, so they live here rather than in PURE_INCIDENTS; B1924b's
    # signature-aware call is what lets a gate with no `text` parameter run.
    #
    # The Skill blobs are SINGLE-quoted literals: they contain double quotes,
    # and B1936b produced a SyntaxError by interpolating one into a
    # double-quoted string.
    "scan_skill_not_updated": [
        ("B1723 - a LEARNINGS entry with SKILL.md left untouched. MEASURED: "
         "SKILL.md was touched 5 times (B1597-B1704) while LEARNINGS ran far "
         "ahead.", True,
         {"learnings_touched": True, "skill_touched": False}),
        ("both files touched - must go quiet", False,
         {"learnings_touched": True, "skill_touched": True}),
        ("no miss recorded at all - must go quiet", False,
         {"learnings_touched": False, "skill_touched": False}),
    ],
    "scan_discipline_not_loaded": [
        ("B1728, owner: 'I want the full 632 lines loaded each turn!' - a "
         "substantive turn that never loaded the skill", True,
         {"tool_text": "", "substantive": True}),
        ("the skill loaded - must go quiet", False,
         {"tool_text": "Skill execution-discipline", "substantive": True}),
        ("a non-substantive turn - must go quiet", False,
         {"tool_text": "", "substantive": False}),
    ],
    "scan_skill_not_invoked": [
        ("B1725, owner: 'Is the fable mode and council skills not being "
         "invoked if prompted? I am not seeing anything in turn.'", True,
         {"user_text": "please use fable mode here", "tool_text": ""}),
        ("a Skill tool_use blob present - must go quiet", False,
         {"user_text": "please use fable mode here",
          "tool_text": '{"name": "Skill", "input": {"skill": "fable-mode"}}'}),
        ("no trigger in the request - must go quiet", False,
         {"user_text": "just do the thing", "tool_text": ""}),
    ],
    "scan_skill_not_invoked_per_skill": [
        ("S6-B1729c - two skills triggered, ONE invoked. Invoking a DIFFERENT "
         "skill does not satisfy a trigger.", True,
         {"user_text": "fable mode and council this",
          "tool_text": '{"name": "Skill", "input": {"skill": "fable-mode"}}'}),
        ("both invoked - must go quiet", False,
         {"user_text": "fable mode and council this",
          "tool_text": '{"name": "Skill", "input": {"skill": "fable-mode"}} '
                       '{"name": "Skill", "input": {"skill": "llm-council"}}'}),
    ],
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
