---
name: execution-discipline
description: MANDATORY turn protocol for the stock-picks-app repo — applies UNPROMPTED at the START of every working turn (any turn that produces a recommendation, code change, audit, review, or doc update) per owner directive 2026-07-07; the owner never needs to mention it. Enforces CHECKLIST pre-flight, no-silent-miss disposition ledger, test pyramid on every code change, LEARNINGS feedback loop on every miss, deep code-verified audits, and the absolute anti-fabrication truth standard. Also invocable as /execution-discipline.
---

# Execution Discipline — stock-picks-app Turn Protocol

This skill codifies the execution discipline this project converged on across
1200+ batches, 290+ councils, 49 PIVOTs, 157 CHECKLIST items, and 204 LEARNINGS.
It exists because the same failure classes recurred: silent misses, surface-level
audits, skipped pyramids, deferred doc-sweeps, and lessons written but not re-read.

**Run every phase below, in order, every working turn. Phases are gates, not
suggestions. A skipped phase makes the turn non-compliant.**

## Standing activation (owner directive 2026-07-07 — Council 292/293)

- This skill applies **UNPROMPTED**. The owner never needs to type
  `/execution-discipline` or mention compliance. If a turn produces work
  and this protocol was not applied, the turn is non-compliant — record it
  as a miss (Phase 5) the moment it is noticed.
- The Truth & Evidence Standard below is **cross-cutting and absolute**: it
  binds every phase, every sentence, every number in every response.

## GENERALIZATION MANDATE (owner directive 2026-07-18 — Council 341, HARD)

Two mandatory requirements, owner-set after L207→L208→L209 (a silent
calendar fallback was fixed as a one-off "install the package" instead of
generalized to a pre-run parity gate; the under-generalization directly
caused the chunk-1 cross-environment defect days later):

1. **NO UNDER-GENERALIZATION.** When a defect is found, fix the CLASS, not
   the instance. Before shipping any fix, state the failure class it
   belongs to and confirm the fix closes the class (or add the gate/test
   that does). A patch that leaves siblings of the same class open is
   non-compliant.
2. **NO ONE-OFF FIXES WITHOUT OWNER APPROVAL.** A deliberately narrow /
   instance-only fix is allowed ONLY with explicit owner sign-off. Absent
   that, generalize. When proposing any fix, explicitly say whether it is
   class-level or one-off; if one-off, STOP and get approval before shipping.

These bind every code change, audit remediation, and Phase 5 miss-capture.
The test: "what else breaks the same way, and does this fix cover it?" —
answered in-response, every fix.

---

## TRUTH & EVIDENCE STANDARD (cross-cutting — absolute, zero tolerance)

Fabrication, false claims, invented numbers, and overstated status are
**entirely prohibited**. This is the highest-priority rule in this skill —
it wins over speed, over completeness, over looking finished.

1. **Every factual claim carries an evidence class**, and only these four exist:
   - `EXECUTED` — a command/test/probe run THIS turn, with its actual output.
   - `READ` — a file read THIS turn, citable as `file:line`.
   - `DERIVED` — arithmetic/logic from EXECUTED or READ inputs, shown explicitly.
   - `UNVERIFIED` — anything else (memory, prior-session recall, sub-agent
     report, extrapolation, expectation). Must be LABELED as such in the
     response. An UNVERIFIED claim stated as fact is a fabrication.
2. **Sub-agent and tool-summary outputs are UNVERIFIED until independently
   spot-checked** (PIVOT #41: a sub-agent fabricated results that were
   relayed as fact and had to be retracted). Verify at least one concrete
   artifact from any sub-agent report before repeating its conclusions.
3. **Numbers are never estimated silently.** A count, coverage %, test total,
   or fire rate appears in a response only if re-derived THIS turn by running
   code, or explicitly marked as stale-with-source ("84.2% per B1211").
4. **Status vocabulary is earned, not chosen:**
   - `DONE` / `SHIPPED` — requires pyramid GREEN + commit hash in the same message.
   - `VERIFIED` / `WIRED` / `ARMED` — requires a linked evidence artifact
     (CHECKLIST #124), never a code-presence grep.
   - `FIXED` — requires the pin test that reproduces the bug, passing.
   - Anything not yet earned is `IN-PROGRESS`, `ATTEMPTED`, or `UNVERIFIED`.
5. **Predictions are framed as predictions.** "Should", "expected", "likely"
   claims must be visually separated from observed facts — never mixed into
   a results table.
6. **On discovering any false claim (own or inherited): retract immediately
   and visibly** in the next message — state what was claimed, what is
   actually true, and the evidence. Then Phase 5 (L-entry). A quiet
   correction is a second fabrication.
8. **VERDICT SCOPE (CHECKLIST #182, B1504).** The four evidence classes tag a
   claim's PROVENANCE, not its SCOPE - so an EXECUTED claim can still be false
   by reaching further than what was measured. Before stating any verdict about
   an object (strategy, producer, module, dataset), enumerate that object's FULL
   parameter/dimension space and mark each entry TESTED / UNTESTED. **The verdict
   sentence must name its denominator** - "0 of 20 combinations across 2 of 6
   producers", never "it fails". MECHANICALLY ENFORCED: the Stop hook
   (`scan_verdict_denominators` in `scripts/verify_turn_compliance.py`) blocks a
   turn whose response uses verdict language with no "N of M" in the same block.
   *Lineage:* B1502 shipped "cannot clear the Sharpe bar" on 2 of 6 producers;
   B1500 shipped "16 of 41 strategies have nothing to tighten" having enumerated
   only gate expressions, never producers. Note this is distinct from the scope-of-
   ACTION rule (L361, widening what you DO without approval) - this covers
   scope-of-CONCLUSION.

7. **"I don't know" and "this failed" are always compliant answers.**
   Reporting a failed test, an interrupted run, or an unresolved question
   accurately is success; dressing it up is the violation.

---

## B1335 HARD RULES — PRE-SPEND / MECHANISM-EXISTENCE / RCA-TAGGING (owner-approved 2026-07-20, Council 365)

Derived from the B1334 fresh-eyes review of the chunk-1/chunk-2 waste and the
batch-1 traps. Each rule retroactively catches >=2 real past misses (#136).

1. **PRE-SPEND OBSOLESCENCE GATE.** Before any cost-bearing or multi-hour run:
   write a `run_manifest.json` pinning **code SHA, isolation mode, calendar,
   universe/ticker list, budget projection**; then answer in writing *"what
   could make this run obsolete?"* — every enumerated risk gets a mechanical
   gate or an explicit owner acceptance. Changing any pinned field mid-sequence
   restarts the sequence. `scripts/prelaunch_gate.py` implements this check.
   **B1704 CORRECTION - it is HAND-RUN, not launcher-wired.** This text claimed
   "launcher-wired; refuses launch without a passing manifest"; an audit of every
   gate in `scripts/` found it has **ZERO automatic callers**, so nothing refuses
   anything - the launch path is a direct `run_phase1a.py` invocation that never
   consults it. **Run it explicitly before any cost-bearing launch and paste the
   exit code.** A capability asserted in the enforcement layer's own description
   and contradicted by grep is the MECHANISM-EXISTENCE RULE failing against
   itself (L499 / CHECKLIST #224).
   *Retroactive:* chunk 1 (isolation undecided, calendar unpinned), chunk 2
   (stale SHA), chunk-9 cross-arm (three enumerable confounds) — all blocked.

2. **MECHANISM-EXISTENCE RULE.** Any flag, script, gate, or capability cited
   in a plan or promised to the owner carries EXECUTED evidence it exists
   (`--help` output, grep of the flag, a test run) — or is explicitly labeled
   **PROPOSED-NOT-BUILT**. A plan referencing an unverified mechanism is a
   Truth-Standard violation *at the plan level*.
   *Retroactive:* the promised-but-nonexistent `--expect-sha` (B1333/B1334);
   the "monitor armed" code-presence claims (B1028 class).

3. **RCA EVIDENCE-TAGGING.** Every causal claim in an owner-facing RCA is
   tagged with its evidence class (EXECUTED / READ / DERIVED / UNVERIFIED).
   DERIVED or UNVERIFIED causal claims must be worded **"hypothesis"**, never
   "root cause". Any counter or metric used as RCA evidence requires its
   **measurement point verified first** (what pipeline stage does it count?).
   *Retroactive:* "all 140 fire-bars were red candles" (B1333 — counter was
   pre-confirmation, default-permissive gate); "calendar contaminates ~25pct"
   (L209).

4. **FRESH-EYES REVIEW CADENCE (standing).** Before every batch-size
   escalation (or every ~10 batches of a sequence), an adversarial review of
   the accumulated work runs with fresh eyes — a different model or a cold
   pass that re-derives claims from code/data rather than summaries. The
   B1334 review (model-switch) caught 3 defects the author missed; this
   cadence is the Tier-3 compliance mechanism for judgment-tier failures.

---

## MECHANICAL ENFORCEMENT LAYER (B1254-B1257 — the gates that make phases 3 and 6 physically binding)

Owner-approved 2026-07-08. These run WITHOUT invocation; know they exist so
you work WITH them, not against them:

| Gate | Where it fires | What it blocks |
|---|---|---|
| C6 pyramid stamp | every `git commit` staging `*.py` (pre-commit hook) | commit without a fresh GREEN full pyramid (`.pyramid_stamp` written only by a both-tiers pytest session) |
| C7 banned-pattern diff scan | every commit | ADDED lines with `not s.get(`, default-True strategy gates, relative `data_prefetch` paths, unlogged `except: pass` (waiver: same-line `# preflight-allow: <rule>`) |
| C8 queue-entry gate | every commit | commits not staging EXECUTION_QUEUE.md (escape: `GIT_QUEUE_EXEMPT=1`, logged to `.queue_exempt_log`) |
| C9 doc→queue cross-check | every commit | `output_audit/*.md` referencing ticket IDs absent from the queue |
| #182 verdict-denominator | every turn-end (Stop hook) | a response stating a verdict with no "N of M" denominator naming the tested scope (B1504) |
| Gate B Stop hook | every turn-end (`.claude/settings.json` hooks.Stop → `scripts/verify_turn_compliance.py`) | ending a turn with modified TRACKED files uncommitted (escape: one-shot `.stop_exempt`, logged) |

- **Fresh clones** (AWS instances, new machines): git-hook shims do NOT
  travel with clones — run `bash scripts/install_git_hooks.sh` (or `.bat`)
  once after `git clone`, per AWS_LAUNCH_PLAYBOOK Gate 5. The Stop hook and
  preflight script are committed and need no install.
- **Manual dry-runs:** `python scripts/preflight.py --staged` (commit gates)
  and `python scripts/verify_turn_compliance.py` (turn gate).
- The gates cover the mechanically-checkable rules. Phases below remain
  authoritative for the JUDGMENT surface (truth standard, audit depth,
  recommendation quality) — the Pass 52 class of miss that no script catches.
- Every escape-hatch use is logged and therefore auditable; using one is a
  disclosure, not a workaround.

## Phase 0 — RECALL (before any analysis or recommendation)

1. **Read `CHECKLIST.md`** (or confirm it is already in context this session).
   Current range: #1-#157 and growing. The checklist is the accumulated immune
   system — every item exists because its absence caused a real failure.
2. **Read the LEARNINGS relevant to this turn's task type.** Grep `LEARNINGS.md`
   for keywords matching the task (e.g. `producer`, `coverage`, `pyramid`,
   `doc-sync`, `fire-count`). Do not rely on memory of what the lessons say —
   re-read the actual entries. Minimum: read the 5 most recent L-entries at
   session start (they encode the freshest failure modes).
3. **Check memory directory pointers** (`MEMORY.md` feedback_* entries) for
   standing owner rules that apply — e.g. `feedback_no_auto_launch_batch_b`,
   `feedback_pyramid_no_exceptions`, `feedback_mandatory_council_per_turn`.
4. **State the scope ledger** (Phase 1) before doing any work.

## Phase 1 — SCOPE LEDGER (the no-silent-miss mechanism)

At turn start, enumerate EVERY item in scope as an explicit ledger:

```
SCOPE LEDGER (turn N):
  1. <item> — [status at turn end: DONE | DEFERRED(ticket-ID) | N/A(reason) | BLOCKED(owner-input)]
  2. <item> — ...
```

Rules:
- Every item the user's directive touches gets a row. If the directive says
  "all X", enumerate X by RUNNING CODE or grepping — never estimate the list.
- At end of turn, every row must carry a terminal disposition. **A row with no
  disposition is a silent miss — the exact failure class this ledger exists
  to prevent** (B1119: 22 batches of silent doc-sync suspension; Council 236's
  46-strategy ledger is the positive template).
- DEFERRED requires a ticket in `EXECUTION_QUEUE.md` written THIS turn, not a
  promise. "Documented but not remediated" items must be flagged in the
  end-of-turn summary under an explicit **"ACKNOWLEDGED-NOT-REMEDIATED"**
  heading so the owner sees them — burying them in prose is a silent miss.
- Counts must reconcile: items-in x = DONE + DEFERRED + N/A + BLOCKED. State
  the arithmetic explicitly.

## Phase 2 — PRE-FLIGHT (before EVERY recommendation)

Per the Pass 52 standing rule in `CLAUDE.md`:
- Apply CHECKLIST.md as a visible pre-flight block BEFORE stating each
  recommendation — each applicable item marked ✅ / ⚠ / 🔴 with one-line
  evidence (grep output, count re-derived from code, cross-reference).
- Items not applicable: mark N/A **with reason**. Silent skipping = the
  pattern-match-without-verification failure that caused 6 consecutive
  DEC-422 lapses.
- Any 🔴 → HALT. Report the failure; do not state the recommendation.
- Council-style enumerate + recommend (`feedback_council_enumerate_plus_recommend`,
  CHECKLIST #115): list options, then recommend one with reasoning.
- Owner approval gates: ALL rule/threshold/parameter changes, ALL paid API
  runs (small test → review → approval → scale), Batch B launch
  (`feedback_no_auto_launch_batch_b` — explicit typed instruction only).

## Phase 3 — EXECUTE with the TEST PYRAMID GATE

Applies to EVERY code change (feature / fix / refactor / schema / data-source
migration) and EVERY commit — **no doc/data carve-outs**
(`feedback_pyramid_no_exceptions`; CHECKLIST #69 / DEC-503):

1. Run the pyramid BEFORE commit:
   `python -m pytest backtest/tests/test_unit.py backtest/tests/test_integration.py -q`
   Current baseline: 861 passed + 2 skipped (grows over time — any decrease
   from prior baseline without an approved deletion is a 🔴).
2. Pyramid runs PER ADDRESSAL, not bundled across fixes
   (`feedback_pyramid_per_addressal`). Never launch parallel pyramid runs
   (`feedback_no_parallel_pyramid_runs`).
3. Every fix ships with a PIN TEST that would have caught the bug it fixes
   (writer-reader schema contracts especially —
   `feedback_writer_reader_schema_contract_pin_test`, PIVOT #37).
4. Batch cap: ≤3 substantive fixes per batch (Council 201). Larger sets split
   into sequenced batches, each with its own pyramid.
5. Validate by RUNNING code, never by reading it (CHECKLIST #14, #15). Counts
   cited in docs are re-derived from code at cite time
   (`feedback_doc_count_drift_must_be_test_pinned`), e.g.:
   `python -c "from backtest.signals.screener import ALL_STRATEGIES; print(len(ALL_STRATEGIES))"`

## Phase 4 — AUDIT DEPTH STANDARD (for any audit / review / verification task)

Surface-level = non-compliant. Every audit must satisfy ALL of:

1. **Code-verified, not doc-verified.** Every claim about system behavior is
   backed by an executed probe (runtime call, pytest, or script run) — not a
   grep for code presence. "Wired" means engine-consumed on a real call path
   (`feedback_wired_means_engine_consumed`; the `wired=yes` grep heuristic
   produced ~150 false-positive RESOLVED claims).
2. **Both artifact classes checked:** the codebase AND all non-archive docs.
   An audit that reads only docs (or only code) is half an audit.
3. **Happy-path artifacts inspected**, not just HALT-path logic
   (CHECKLIST #128 — B1019's 0-byte monitor.log passed review because only
   failure branches were read).
4. **Representative sampling** for coverage claims: ≥25 tickers, ≥4 dates
   spanning ≥12 months (CHECKLIST #154), and trace the ACTUAL consumer path
   through multi-function producers (CHECKLIST #157 / L202).
5. **Evidence artifact required** for any WIRED / ARMED / VERIFIED status —
   a linked file or command output, not an assertion (CHECKLIST #124).
6. **Default-empty returns investigated**, never assumed benign
   (CHECKLIST #106 / #44(b)); temporal coverage checked across the full
   backtest window, not one date (CHECKLIST #156 / L201).
7. **Line-by-line ticket extraction** when reviewing feedback or prior turns:
   every sentence becomes a candidate ticket BEFORE synthesis
   (`feedback_line_by_line_ticket_extraction_before_synthesis`).

## ANCHOR-THE-RULE RULE (B1597 - L464, CHECKLIST #197, mechanically enforced)

**A rule recorded only in LEARNINGS is a story, not a gate.**

MEASURED across one session: 24 L-entries stated a generalised rule and **18 were
referenced in NEITHER CHECKLIST nor this skill - a 75pct orphan rate.**

Writing the L-entry FEELS like closing the loop: the insight is captured, the prose
is good, the commit is green. **But capture is not enforcement.** LEARNINGS is read
when someone goes looking; CHECKLIST and this skill are read every turn. An
unanchored rule gets rediscovered by repeating the failure that produced it.

**Every L-entry stating a generalised rule MUST, in the same turn, be anchored by a
NEW CHECKLIST item citing the L-number, or an explicit citation of an EXISTING item
that already covers it.**

*The confirming pattern:* every rule that HELD had a script behind it (#182, #185/#186,
#187, #188, #189). Every rule that decayed was prose. **Placement is not filing - it
decides whether a rule is enforced, consulted, or merely archived.**

Enforced by `scan_orphan_rule()` in `scripts/verify_turn_compliance.py`.

## POST-FIX RE-CHECK RULE (B1595 - L462, CHECKLIST #196)

**A fix can invalidate a conclusion the defect itself left intact.** While the bug
stood the numbers were self-consistent; correcting it breaks that consistency for
anything already shipped.

After ANY defect fix, before moving on: **enumerate the SHIPPED conclusions that
depended on the old behaviour by GREPPING for them, MEASURE the overlap, and
ticket each for re-derivation** or state why it survives. The instinct after a fix
is to move on; the obligation is to re-check what was already decided.

*Lineage:* B1593's `regime_flip` fix landed on one of only two ROBUST Phase 1B
roster cells, whose numbers were `time_stop_20d`'s all along.

## TEST-EVERY-QUANTITY RULE (B1605 - L470, CHECKLIST #201, mechanically enforced)

**Owner directive 2026-08-16: when making any quantitative claim, you are required
to TEST it.**

The NO-UNTESTED-CAUSE rule below covers CAUSES. It does not cover NUMBERS - and a
number drives a decision at least as directly. *"Costs nothing - same runtime"* was
stated about a 3-year window against a 2-year baseline. It cost **50pct more**
(5.00 h vs 3.33 h per config; ~50 h vs ~33 h for the sweep), and **the arithmetic
was one multiplication** against a runtime spec the owner had set deliberately.

**The recurring shape is substituting a RATE for a TOTAL.** Per-sim-day cost was
identical either way - true - but there were 1.5x as many days. Same class as a
per-call ratio quoted as a wall-clock saving (L432), a spot RAM reading quoted as a
ceiling (three times), a cold JIT timing quoted as steady state. **The rate is the
number already in front of you, which is exactly why it gets substituted.**

**Before ANY claim of the form "costs nothing / free / same / negligible / roughly
the same / about Nx": do the arithmetic and SHOW it.** If you cannot compute it,
say the quantity is UNMEASURED - and ticket it as `UNKNOWN - RCA NEEDED` if it
matters. Never assert a magnitude you have not calculated.

Enforced by `scan_unmeasured_quantity()` in `scripts/verify_turn_compliance.py`.

## NO-UNTESTED-CAUSE RULE (B1587 - L455, HARD, mechanically enforced)

**A hypothesis presented as a finding is a fabrication.** The Truth Standard already
said "word DERIVED/UNVERIFIED causal claims as hypothesis, never root cause"
(B1335 rule 3). **It did not help**, because labelling is a formatting act and the
reader still receives a cause.

**The failure it did not prevent (L455):** a 4pct residual in a grading run was
explained as *"probable cause is the `i < 250` warmup guard"*, written into the
response AND the queue. It was **wrong** - the affected rows sat at bars
799-1158 - and **one command disproved it**. The hypothesis was cheaper to TEST
than to write.

**The rule is therefore not about labelling. It is about ORDER:**

1. **If a cause can be tested with a command you already know how to run, RUN IT
   before naming the cause.** Not after, not "next turn".
2. **If it cannot be tested cheaply, say the cause is UNKNOWN - and TICKET it**
   as `UNKNOWN - RCA NEEDED` (owner directive 2026-08-16). "I don't know why"
   is a compliant answer ONLY when paired with a ticket; unticketed, it turns an
   open question into a closed one - the investigation stops and nothing records
   that it must resume. Naming a plausible mechanism instead is not an option.
3. **Never let a hypothesis enter a durable artifact** - queue ticket, LEARNINGS
   entry, doc, commit message - without EXECUTED evidence beside it. Durable
   artifacts are read later by people who will not re-derive your confidence.
4. **A wrong cause is worse than no cause**: it closes the investigation. L455's
   hypothesis would have sent the next reader to the warmup guard, which was
   fine, while the real explanation (a swept `close_mitigation` variant behaving
   exactly as designed) went unexamined.

**Mechanically enforced:** `scan_unverified_cause()` in
`scripts/verify_turn_compliance.py` blocks turn-end when cause language
("probable cause", "likely because", "I suspect", "most likely", ...) appears
with no evidence language ("EXECUTED", "confirmed by", "I ran", "probe",
"ruled out") anywhere in the same turn. Windowed to the current turn.

## SPEC-vs-IMPLEMENTATION RULE (B1608 - L471, CHECKLIST #202)

**Every verification habit in this skill checks code against REALITY - does it run,
does it reproduce, is the artifact the right one. NONE of them checks code against
INTENT.** That gap has its own failure, and it is invisible to all of them.

`tighten_breaker_block.py` applied all six admission gates and emitted PASS/FAIL,
while the plan specifies STEP 1 produces **"ranked combinations"** and STEP 2
produces **"gate verdicts"**. So **"0 PASS across 400 combinations" was reported as
a Step-1 result when Step 1 can never produce a PASS.** No artifact was wrong. No
data was wrong. The ARTIFACT-PROVENANCE RULE below could not have caught it,
because nothing was wrong with any artifact - the CODE had drifted from the DESIGN,
and nothing in the repo compares those two.

**Before reporting what any component produced:**

1. **Read what its phase is SPECIFIED to produce** - in the plan document, not from
   memory or from earlier in the conversation.
2. **If the output shape does not match the spec, that is a DEFECT** in the code or
   in the plan. Say which. **Do not report the number** - a result of the wrong
   KIND is not a good or bad result, it is a category error.
3. **When a design was decided earlier, RE-READ the decision.** Reconstructing it
   from conversation produces a worse version: this drifted across ~20 turns, with
   the window and universe re-argued from scratch while the plan already held the
   answer. This is CONFIRM-BEFORE-REPLICATING applied to a SPECIFICATION rather
   than a template.

**The tell:** if you find yourself explaining why a result is surprising, check
first that it is the right SHAPE of result. "0 PASS" was surprising because it was
answering a question the phase was never asked.

## ARTIFACT-PROVENANCE RULE (B1572 — L445, HARD, mechanically enforced)

**"Use the artifact, not the roster" is only half a rule. It does not say use the
RIGHT artifact.**

A universe was taken from `output_audit/r5_universe_381.txt` because a doc rule
said to derive from the baseline artifact. That file came from
`output_r5_rung4_chunk1` — an ABANDONED, alphabetically-partitioned chunk run.
**380 of its 381 tickers start with A, B or C.** The real baseline,
`output_r5_merged_1_7`, has 544 tickers, 25pct A-C, and contains MSFT / NVDA /
GOOGL / META / TSLA — none of which were in the 381. Overlap: 133. The file held
248 tickers the baseline never ran. Every downstream artifact inherited it
silently, because 381-vs-544 is not a discrepancy a filename reveals.

**Before ANY artifact becomes an input to analysis or a run:**

1. **Open it and characterise its CONTENTS** — never infer scope from its name,
   its size, or the doc that pointed at it. A filename is a claim by its author.
2. **Reconcile it against the artifact everything else uses.** If two consumers
   of "the same" baseline see different counts, one of them is on a different
   artifact. Ask which, before proceeding.
3. **For any ticker/entity universe, run the mechanical check:**
   ```
   python scripts/verify_universe_artifact.py <file> --compare-cube <baseline_cube.csv>
   ```
   It fails on alphabetical skew, mega-cap absence, narrow letter coverage, and
   provenance mismatch — the four ways this class presents. Retroactively it
   flags the 381 on ALL FOUR (CHECKLIST #136 satisfied).
4. **A deliberately narrow input is fine — say so IN WRITING** in the doc that
   consumes it. Unstated narrowness is the defect; stated narrowness is a scope.

**Generalised beyond universes:** the same trap applies to any cube, roster,
cache, or results file selected by name. **"Which artifact, and does its coverage
match what I am claiming?" is a question with an executable answer — so execute
it rather than reasoning about it.**

## Phase 5 — MISS-CAPTURE FEEDBACK LOOP (whenever a miss is found)

A "miss" = any error, silent skip, stale claim, wrong count, missed scope item,
or owner correction — found by you, the owner, or an audit. Same turn, no
deferral.

**A MISS INCLUDES HOW A QUESTION WAS ANSWERED, NOT ONLY WHAT WAS BUILT (B1722 /
L503 / CHECKLIST #228).** Asked what had been done about a specific root cause, I
listed nine enforcement hooks. Every one existed and worked — and every one
caught a SYMPTOM, not the cause. The response was **fully true and completely
off-target**, which is what makes this class dangerous: no evidence check catches
it. Every number was measured, every artifact real, so the Truth Standard, the
pyramid and all ten turn-gates pass a response like that. **The defect is the
MAPPING from question to answer, not the content.**

- **Before answering, restate the question in your own words**, then check the
  answer against the restatement — not against the work you happen to have done.
  If the response would be equally true had the question been different, it is
  not an answer to this question.
- **Answer each part of a multi-part request explicitly.** "Learnings, checklist
  and skill" is three deliverables; producing two and reporting completion is the
  same substitution one level down. Enumerate the parts, then map each to what
  landed.

**AND: ACKNOWLEDGING A MISS IN PROSE IS NOT RECORDING IT.** I wrote *"my last
response wasn't clear because it wasn't true of it"* and moved straight on to
building — no L-entry, no checklist item, no ticket, until the owner asked why.
The acknowledgement felt like the accounting. It is the same shape as naming a
defect class and fixing only instances (L499). **The sentence admitting a miss is
the TRIGGER for steps 1-4 below, never a substitute for them.**

**The skill is the third artifact and it kept being the one dropped.** Between
B1704 and B1722 every miss produced a LEARNINGS entry and a CHECKLIST item and
left this file untouched. When a lesson is about the TURN PROTOCOL itself, it
belongs here — CHECKLIST is the pre-action gate list, LEARNINGS is the incident
record, and this file is what actually gets read at the start of every turn.

1. **LEARNINGS.md entry** (next L-number): what happened, root cause, the
   generalized rule, and the detection signal that would have caught it earlier.
2. **CHECKLIST.md addition.** (B1447: the #136 retroactive-coverage REQUIREMENT
   is REMOVED by owner directive — an item is no longer rejected for failing to
   show it would have caught 2 of the last 3 PIVOTs. State what it would and
   would not have caught; that is a reporting obligation, not a gate. A novel
   failure class has no prior instances by definition.)
   If an existing item should have caught the miss, that is a COMPLIANCE failure
   and belongs in the L-entry — but see the ratchet warning: when three or more
   L-entries accumulate with NO checklist addition, re-examine them AS A BATCH.
   Between 2026-07-23 and 2026-08-04 that ratchet produced 8 L-entries and 0
   checklist items over ~90 batches (L271); four were genuinely new classes.
3. **Memory write** if the lesson is a standing owner-behavior rule
   (a `feedback_*` file + `MEMORY.md` pointer).
4. **Fix or ticket** — the miss itself is either remediated this turn or gets
   an EXECUTION_QUEUE ticket with priority. Never "acknowledged" without one
   of the two.
5. Owner corrections are ALWAYS misses (the system failed to self-catch).
   Six owner catches in Pass 52 is the canonical anti-pattern.

## LOAD-THE-SKILL RULE (B1728/B1729 — L504, CHECKLIST #229, mechanically enforced)

**The hook injects 12 bullets. This file is 644 lines. Invoking it delivers all 644.**

I reported the gap as a structural limit and offered the owner a workaround. It was an un-run tool
call — the copy I was reasoning from had been truncated by COMPACTION, not by design.

**Any turn that touches the repo invokes `Skill(execution-discipline)` first.** The 632 lines the
summary omits are not filler: `#182` verdict-scope, POST-FIX RE-CHECK, B1446
no-arbitrary-decisions, the TRIPWIRE TABLE and ANCHOR-THE-RULE — **all violated in the session
where only the summary was loaded.**

Enforced by `scan_discipline_not_loaded()` in `scripts/verify_turn_compliance.py`.

**And the general form (#229): before calling anything a limitation, run the cheapest probe that
separates a LIMIT from an OMISSION.** A mechanism that explains your own repeated failures is the
one to distrust most — it is the story you have a motive to believe.

## Phase 6 — END-OF-TURN SWEEP (CHECKLIST #67 — HARD RULE, no exceptions)

1. **Doc-sync sweep**: every forward-looking non-archive doc touched by this
   turn's changes is updated AND COMMITTED this turn
   (`feedback_per_turn_doc_sweep_no_exceptions`). Doc commits are DECOUPLED
   from in-flight long-running jobs (#67.b). CSV-analysis-only and
   investigation-only turns STILL require the sweep (B1119 lesson).
2. **EXECUTION_QUEUE.md updated every turn — the queue is the ANCHOR**
   (CHECKLIST #94 — `feedback_execution_queue_mandatory_per_turn`;
   owner directive 2026-07-08):
   - Every turn gets a batch entry, including analysis-only and
     parallel-track turns.
   - **Parallel-track rule:** any detour from queued work (a review, an
     owner question, an incident) must (a) ticket its own findings into
     the queue THIS turn, and (b) end by restating where the queue stands
     — what was interrupted and what resumes next. Work that leaves the
     queue and never returns is a silent miss.
   - Findings without tickets don't exist: a bug/gap/idea mentioned in a
     doc or chat but absent from the queue is a silent miss (the B1248
     review's 9 findings were initially doc-only — the trigger for this
     rule).
   - **"Finding" means ALL of (B1251 lesson — the lenient reading caused
     5 gaps):** bugs, recommendations/levers, new-strategy candidates,
     structural decisions awaiting owner input, disclosed-partial audit
     scopes, and open owner questions. A doc's own "priority queue"
     section is NOT a queue substitute.
   - **Mechanical cross-check, not memory:** any turn that produces a
     deliverable doc ends with an executed doc→queue cross-check (grep
     the doc's finding IDs / lever numbers / decision items against
     EXECUTION_QUEUE.md; every non-matched item gets a ticket or an
     explicit N/A). Prose rules without an executable verifier decay —
     the only no-silent-miss catches that have worked were programmatic
     (219/219 coverage script, B1251 grep cross-check).
   - **New-rule retroactive sweep:** when a discipline rule is added or
     tightened mid-stream, the same turn re-scans the last 3 batches'
     outputs against it (mirror of CHECKLIST #136's retroactive spirit).
     B1249 added the queue-anchor rule without re-scanning B1248 — that
     omission was the gap.
3. **Scope ledger closed**: restate the Phase 1 ledger with final dispositions
   and the reconciliation arithmetic.
4. **Compliance statement** (CHECKLIST #45): enumerate which checklist items
   applied and were satisfied. Post-hoc statement does NOT replace Phase 2
   pre-flight.
5. **Commit + push** per standing approval (`feedback_standing_approvals`),
   pyramid GREEN first. Batch-numbered commit message with council reference.
6. **Language discipline**: never claim "comprehensive audit",
   "OPERATIONALLY-VERIFIED", "last instance of this bug class", or
   "this time is different" (retired per Council 197). Use numeric status
   only: "shipped + monitoring", "N of M dispositioned".

---

## B1446 HARD RULES - NO-ARBITRARY-DECISIONS / ROUTED-WORK-TICKETS (owner-directed 2026-08-04)

Owner, verbatim: **"No arbitrary decisions. That's an absolute red flag."** and
**"routed work plan becomes trackable tickets - that's a genuine gap."**

1. **NO ARBITRARY DECISIONS (CHECKLIST #165).** Whenever code or analysis CHOOSES among
   candidates - which duplicate survives, which exit is canonical, which threshold, which
   sample, which tie-break - the criterion is stated inline AND justified on a measured
   basis, or explicitly labelled `ARBITRARY-PENDING-JUSTIFICATION` **in the same message
   that publishes any number derived from it**, with a ticket to replace it. Convenience
   defaults (first match, largest N, alphabetical, insertion order) ARE arbitrary until
   argued. Publishing a number from an unjustified rule without the label is a
   Truth-Standard violation: the number carries authority the method does not.
   *Lineage:* B1444 chose de-dup survivors by largest trade set while the canonical
   pipeline uses eigenvalue effective-N; six strategies were nearly decommissioned on it.

2. **ROUTED WORK BECOMES TICKETS (CHECKLIST #164).** Any artifact or turn that ENUMERATES
   FUTURE WORK produces EXECUTION_QUEUE tickets with an S6-xxx ID, the ITEM NAMES inlined,
   and a disposition. Prose counts are a record, not a ticket - not greppable per item,
   not closeable individually. The per-turn cross-check greps the artifact's routing KEYS
   **and item NAMES**, not its filename.
   *Lineage:* B1410 routed 177 strategies and recorded only bucket counts; invisible ~30
   batches until the owner asked.

3. **ZERO-HIT GREPS PROVE NOTHING UNTIL THE PATTERN IS VALIDATED (CHECKLIST #166).** Before
   reporting an absence, prove the pattern CAN match - run it against a known-present
   instance or invert it. "0 hits" from an unvalidated pattern is UNVERIFIED, never
   "it is not there".
   *Lineage:* B1444 grepped `"LOOSEN / STARVED"` against a file writing `LOOSEN/STARVED`;
   the false absence was reported to the owner, written to LEARNINGS and committed.

4. **REJECTION ON DIRECTION MUST REDIRECT (CHECKLIST #167).** A router rejecting a candidate
   for being the WRONG KIND of change re-routes it to the opposite queue; it never
   `continue`s the item out of the pipeline.

5. **MISS-CAPTURE IS TWO FILES, NOT ONE.** Phase 5 requires a LEARNINGS entry AND a
   CHECKLIST evaluation. Classifying every miss as "compliance failure, no new item" is
   itself a drift pattern: between B1263 and B1445 the session wrote L263-L270 (8 entries)
   and ZERO checklist items, with CHECKLIST untouched for 12 days. If three or more
   L-entries accumulate without a checklist item, that is a signal the anti-theater guard
   (#136) is being over-applied - re-examine them as a batch.

## TRIPWIRE TABLE — recurring mistake classes and their pre-action checks

Before acting, scan this table. If the action matches a row, run the tripwire
check FIRST. Each row is a real failure that recurred until its check existed.

| If you are about to... | Tripwire check | Lineage |
|---|---|---|
| Cite any count (strategies, tests, docs, coverage) | Re-derive it by running code THIS turn | ~150 false RESOLVED; `feedback_doc_count_drift_must_be_test_pinned` |
| Relay a sub-agent's finding | Independently verify ≥1 concrete artifact from it | PIVOT #41 fabrication |
| Claim something is "wired" / "consumed" / "integrated" | Runtime probe on the actual call path, not grep | `feedback_wired_means_engine_consumed` |
| Claim a monitor/job is armed or running | `Get-Process` (Windows truth) + evidence artifact; check existing PIDs before launching | CHECKLIST #121/#124; `feedback_powershell_authoritative_for_windows_process_truth` |
| Declare an audit/review complete | Did you check the HAPPY-PATH output artifacts (not just failure branches)? Both code AND docs? | CHECKLIST #128 (B1019 0-byte monitor.log) |
| Interpret a signal/field name | Verify semantics in producer source (vol_spike_15x = 1.5x, NOT 15x) | `feedback_vol_spike_naming_convention` |
| Check producer coverage | Trace the ACTUAL consumer path + check the actually-emitted key (days_to_cover vs short_interest_pct slip) | CHECKLIST #157 / L202 |
| Add a gate/threshold change | Owner approval? Prior-deletion reconcile (grep git log)? Blast radius local? | CHECKLIST (k); `feedback_narrow_scope_blast_radius` |
| Write `\|\| true` or swallow an exception | Pair with an explicit success-check | CHECKLIST #122 |
| Change a writer OR a reader of shared schema | Pin test on the writer-reader contract | PIVOT #37; `feedback_writer_reader_schema_contract_pin_test` |
| Bundle >3 fixes into one batch | STOP — split into sequenced batches | Council 201 (44 PIVOTs/session) |
| Launch anything long-running / costly | Small test → manual review → owner approval → scale; resume infra armed; NEVER auto-launch Batch B | L86/L95 ($150 lost); `feedback_no_auto_launch_batch_b` |
| Add a new audit layer / checklist item after a miss | #136 anti-theater guard: would it have caught the last 3 misses retroactively? | Council 197 "eight layers is the smell" |
| Run `git reset --hard` or any destructive git op | `git status` FIRST, always | L49, L77 (data destroyed twice) |
| Defer doc updates because "the turn was only analysis" | No — CSV/investigation-only turns still sweep | B1119 (22 batches silent suspension) |
| Treat CLAUDE.md banner as scope authority | Scope lives in PROJECT_PLAN.md + DEC-NNN | `feedback_banner_is_status_not_scope_authority` |
| Declare partial success on a data/pre-warm fix | Verify the EXACT names/keys landed (phantom-name check) | PIVOT #34 |
| Choose among candidates (dup survivor, canonical exit, threshold, sample) | State + justify the criterion, or label ARBITRARY-PENDING-JUSTIFICATION + ticket | CHECKLIST #165; B1444 largest-trade-set de-dup |
| Report that something is ABSENT from a search | Validate the pattern can match (run it on a known-present instance) first | CHECKLIST #166; B1444 false "no B1410 section" |
| Produce a routing table / candidate list / "remaining N" | File S6-xxx tickets with item NAMES inlined, not prose counts | CHECKLIST #164; B1410 177 strategies |
| Reject a candidate for being the wrong KIND of change | Re-route to the opposite queue; never `continue` it out | CHECKLIST #167; 10 strategies dropped |
| Skip pyramid because "docs only" | No carve-outs — pyramid every commit | `feedback_pyramid_no_exceptions` |

## Quick-reference: the five commitments

| # | Commitment | Enforced by |
|---|---|---|
| 1 | CHECKLIST adhered to every turn; grown on new failure classes | Phase 0 + 2 + 5.2 (with #136 anti-theater guard) |
| 2 | LEARNINGS updated on every miss AND re-read before work | Phase 0.2 + Phase 5.1 |
| 3 | No silent misses | Phase 1 scope ledger + reconciliation arithmetic + ACKNOWLEDGED-NOT-REMEDIATED heading |
| 4 | Test pyramid on every code change/commit | Phase 3 (no carve-outs, per-addressal, pin tests) |
| 5 | Deep audits: code-verified + all docs, never surface | Phase 4 (7-point depth standard) |
| 6 | Zero fabrication / false claims | Truth & Evidence Standard (4 evidence classes; earned status vocabulary; visible retraction) |
| 7 | Compliance without prompting | Standing activation section (unprompted, every turn; non-application = a Phase 5 miss) |
| 8 | Queue is the anchor — every turn, every finding, every detour returns | Phase 6.2 (per-turn entry; parallel-track return rule; findings-without-tickets don't exist) |

## Failure modes this skill exists to prevent (lineage)

- **B1119**: 22 batches with zero doc-sync — Phase 6 makes the sweep per-turn unconditional.
- **PIVOT #41**: sub-agent fabrication — Phase 4.5 evidence artifacts.
- **~150 false RESOLVED claims** from `wired=yes` grep — Phase 4.1 code-verified.
- **Pass 52 six consecutive owner catches** — Phase 2 pre-flight before, not after.
- **Council 197 "eight layers is the smell"** — Phase 5.2 anti-theater guard: fix compliance, don't stack redundant checklist items.
- **"Silent misses acknowledged (documented but not remediated)"** — Phase 1 DEFERRED-requires-ticket + Phase 5.4.
