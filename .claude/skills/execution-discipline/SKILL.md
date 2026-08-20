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

9. **CAPABILITY CLAIMS ARE CLAIMS (B1731 / L505 / CHECKLIST #230).** Every
   example above is about DATA - counts, coverage, fire rates. **Claims about
   the SYSTEM ITSELF slip past**: what a tool can load, what a format permits,
   what a budget allows. They feel like background rather than findings.
   *MEASURED:* I would never publish a cell count unrun; I published *"the skill
   loads as 12 of 644 lines"* having run nothing, and built an owner-facing
   trade-off on it. Invoking it delivers all 644. **Run the probe that settles a
   capability, or label it UNVERIFIED - the four evidence classes apply
   unchanged.**

   **EXTENSION (B1736 / L506): two more shapes, both of which slipped past the
   rule ABOVE because its examples were tools, formats and budgets.**

   a) **ARTIFACT SCHEMA - does the file hold the field you are about to use?**
      I specified a probe as *"split by `exit_reason` and compute rho separately"*
      against a grid JSON that is **one row per COMBINATION and has no
      `exit_reason` column at all**. The split lives in the per-trade CSV. **A
      claim about what an artifact CAN SUPPORT is a capability claim** - open it
      and check the columns before proposing work that depends on them.

   b) **COST - "seconds", "cheap", "one command", "offline".** I said *"offline
      on cached cubes, seconds"* for work that needed a per-trade re-grade at a
      different grain. **An effort estimate is a quantitative claim** and falls
      under the TEST-EVERY-QUANTITY rule, which its wording never suggested.

   **The rule's own diagnosis applies to itself**: *"a rule whose examples share
   one shape gets applied to that shape only."* Its three examples were all
   tools/formats/budgets, and the two shapes above went unrecognised for **four
   instances in one session**. **Before proposing any probe, name the ARTIFACT
   and the FIELD it needs, and say whether you have opened it.**

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

## PROSE-IS-NOT-SHIPPED RULE (B1739 — L507, CHECKLIST #231, mechanically enforced)

**Owner directive: prose alone will not suffice. A rule earns its place only when something
enforces it.**

Three consecutive rules shipped as prose and needed the owner to ask before the mechanism existed —
B1723, B1725, B1736. **Writing the prose FEELS like closing the loop**, which is why this keeps
recurring: it is L499's confession-is-not-remediation and L504's naming-a-class-is-not-closing-it,
one level up each time. **The artifact that RECORDS a rule keeps being mistaken for the artifact
that ENFORCES it.**

**Any turn editing this file or CHECKLIST.md also touches `verify_turn_compliance.py` or
`test_unit.py`** — or writes **PROSE-ONLY** with the reason no mechanism is possible.

**Companion, and the subtler half: a gate that checks a CATEGORY was touched does not check that
every MEMBER was handled.** `#225` fired only on an UNTOUCHED queue, so one ticket satisfied a turn
carrying several findings. **Whenever a rule says "each" or "every", the gate must COUNT, not merely
detect.**

Enforced by `scan_prose_only_rule()` and `scan_findings_vs_tickets()`.

## COMPLIANCE IS CONTENT, AND AN ANSWER CAN BE A DEFECT (B1758 - L514, CHECKLIST #238)

**`check_compliance_marker` asserted only that a compliance BLOCK exists** - never which items were
applied. A block naming nothing passed on every turn of an entire session, so **any checklist item
without its own mechanism was enforced solely by remembering to consult it.** That is the answer to
*"why didn't checklist membership prevent it?"* - **membership was never checked**.

- **The compliance statement cites at least two CHECKLIST items by number, with per-item status.**
  Enforced by `scan_compliance_is_content`.
- **A defect phrased as an ANSWER is still a defect.** This finding was ticketed **ANSWERED**, with
  no mechanism and no `JUDGMENT-ONLY` - violating `#236` one turn after `#236` was written.
  A question mark in the owner's sentence made it feel like an inquiry to satisfy rather than a
  finding to fix.
- **A gate's trigger vocabulary is narrower than its class until proven otherwise.** `#236`'s gate
  keys on MISS markers and missed a defect written as an answer - L509's marker-stem lesson
  recurring in a different gate. **Fixing one gate's vocabulary does not fix the others'.**

## PHASE 5 HAS A FIFTH MEMBER: THE MECHANISM (B1756 - L512/L513, CHECKLIST #236)

**The defect the owner found: a FULLY COMPLIANT Phase-5 remediation can leave its class entirely
unenforced.**

B1702 discovered built-but-not-wired, and touched **LEARNINGS, CHECKLIST, EXECUTION_QUEUE,
`test_unit.py` AND `verify_turn_compliance.py`**. It passed every rule we had. Its remediation was
**ten docstring labels**. The class stayed open, and the next day it produced
`scan_false_skill_status` - defined, proven 5/5, committed, never wired.

**Phase 5's four steps say LEARNINGS / CHECKLIST / memory / fix-or-ticket. None says "build the
mechanism that stops this CLASS."** "Fix" means fix the instance. `#231` does not close it either -
it checks that CODE MOVED, not that THIS class is now enforced, and B1702 moved code.

**So Phase 5 now has FIVE members, enforced through `require_each`:**

1. LEARNINGS entry
2. CHECKLIST item, or an explicit `compliance failure against item N`
3. EXECUTION_QUEUE ticket
4. Fix or ticket for the instance
5. **A MECHANISM FOR THE CLASS - a `scan_`, a pin test, or an explicit
   `JUDGMENT-ONLY: <why no mechanism is possible>`**

**And L512's evidence for why member 5 is not optional:** between the two `scan_skill_not_updated`
catches the **full skill was auto-injected every turn**, containing ANCHOR-THE-RULE, which says
exactly this. **The rule was in context, verbatim, and the behaviour did not change. A 14-line
scanner caught both.** That is the measurement, not the argument.

**Retroactive sweep is also unenforced** - the rule exists in Phase 6 and **no `scan_` has ever
checked it**, so it has run zero times autonomously this session. Every retroactive check happened
because the owner asked.

## CITING A RULE IS NOT THE RULE RUNNING (B1753 - L511, CHECKLIST #235)

**MEASURED: `#224` - *a gate nobody calls is not enforcement* - was a checklist paragraph plus ten
docstring banners for its ENTIRE LIFE.** No mechanism ever existed. It was cited by number,
repeatedly, as though citing were enforcing - **in the same turn an unwired gate shipped underneath
it**.

**A rule number in a response reads like evidence. It is not.** `#224`, `#226` and `#231` were each
cited while the failures they name kept recurring, because none had a mechanism until very late.

- **Before citing any CHECKLIST item as protection, name the function or test that enforces it - or
  say plainly that it is judgment-only.** An item with no named mechanism is a description of a
  failure, not a defence against one.
- **When asked to CONFIRM coverage, MEASURE it.** A 10-errors x 4-artifacts table took one command
  and found 9 of 10 complete with one real gap. *"Yes, all covered"* would have been wrong by one.
- **A zero-hit grep proves nothing until the pattern is validated (#166).** The claim "no such gate
  exists" was first made on a narrow regex; only the owner's challenge forced the broad search that
  actually settled it. The conclusion survived. The method did not.

## PROVE-IT-CAN-FAIL RULE (B1706 - L501, CHECKLIST #226, PROVEN)

**A gate observed only PASSING has not been tested. It has been run.**

`scan_untickcted_remediation` called `_entry_text`, which did not exist, over `_read_entries()`,
which returned zero entries - so the missing function was never reached, the gate returned `None`,
and I reported it working. **A check returning "clean" over an empty input is indistinguishable
from a check that works.**

- **Feed every new gate a case it MUST reject, and watch it reject.** Both directions, always.
- **Then count its occurrences in the file.** One occurrence is the definition alone - proven and
  never wired (B1747, instance 5 of any-vs-each).
- **#224 was PROSE plus docstring labels for its whole life** and could never have fired on the
  unwired gate underneath it. **The rule naming "presence is not enforcement" was itself
  present-but-not-enforced** until the B1751 pin test.

## ANY-VS-EACH PRIMITIVE (B1751 - L510, CHECKLIST #234, mechanically enforced)

**Five instances of one class, each patched alone, so the class stayed open:** `#225` fired on an
untouched queue; the per-skill gate accepted any Skill call; the runner stopped at the first
violation; Phase 5 counted queue rows only; and `scan_false_skill_status` was **defined and never
wired** - built, proven 5/5, committed, reported live, never run.

**`if category_touched: pass` is the natural way to write a check and it is wrong whenever the rule
says *each*.**

- **Any rule whose wording contains "each" or "every" goes through
  `require_each(rule, {member: satisfied})`.** It takes a dict so every member must be enumerated,
  and it names the MISSING members rather than degrading to "something is missing".
- **Count the occurrences of every gate's name.** One occurrence is the definition only - the gate
  has never run. One line, and it would have caught instance 5 two turns earlier.
- **Phase 5 is three artifacts**: LEARNINGS + CHECKLIST-or-explicit-citation + queue ticket.
  Enforced by `scan_miss_capture_complete`.

## INSPECTION EVIDENCE COMES FROM READS, NEVER FROM WRITES (B1774 - L529, CHECKLIST #254)

**MEASURED: writing any file exempted a turn from the uncosted-probe gate**, because `file_path` is
an evidence marker and every `Write`/`Edit` carries one. A narrower hole came first - a `Write`
whose CONTENT mentioned *grep* also satisfied it. **B1738 fixed mention-vs-use for responses and
left the tool side untouched.**

- **Drop mutating tool calls before matching evidence markers**, and verify both ways: a real read
  must still exempt; a write followed by a read must still exempt.
- **Do not call work manual until you have tested that it is.** I ticketed 24 sites as needing
  individual judgment; **the control flow classified all 16 mechanically** (`if <match>: return []`
  = exemption, `if not <match>: return []` = detection). **Asserting something cannot be automated,
  untested, is the same armchair claim as asserting a mechanism exists without checking.**
- **A tool built to find a defect can contain it.** My classifier's negation test was a flat
  `UnaryOp` check and misread a negation nested in a `BoolOp` - it would have sent me to harden the
  wrong side of that gate.
- **Check a flagged site before converting it.** One flag was purely "does not call `_affirms`" on
  a set intersection with no exposure. **The absence of a fix is not the presence of a defect.**

## HARDEN THE EXEMPTION, NOT JUST THE TRIGGER (B1773 - L528, CHECKLIST #253)

**A loose trigger over-fires and gets noticed. A loose EXEMPTION lets violations through silently
and never does.** B1767 word-bounded the trigger side and left the escape clause on raw `in`;
**17 markers collide with their own negation**, so a gate demanding proof was satisfied by a
sentence denying it.

- **Whenever a gate has an escape clause, the escape gets the STRICTER matcher.** `_affirms()`:
  whole word AND un-negated within its clause.
- **Word boundaries fix only half.** 5 cases are word-internal (*measured*/*unmeasured*); **12 are
  phrase-level (*never executed*) and boundaries cannot see them.**
- **Look both ways and clamp to the clause** - backward-only missed *"was NOT executed"*, and a flat
  window rejected a genuine affirmation because the previous sentence was negative.
- **Build probes FROM the live marker list.** Twice in one turn I tested with strings the code could
  not match - once the trigger never fired, once the phrases were absent from the list. **A test
  whose input cannot engage the code proves nothing and reads exactly like a pass.**

## MEASURE DEGRADED EXITS; A HAND-MAINTAINED LIST GOES STALE (B1772 - L527, CHECKLIST #252)

**MEASURED on 217,724 trades: 3 of 26 exits fire a reason unrelated to their own name**, 1 shows a
temporal identity step, and 10 pairs are outcome-duplicates - **`exits_effective ~ 16 of 26`.** The
runbook's hand-written caveat said `regime_flip` was a time stop *pre-B1593*; **it still is.**

- **Run `scripts/measure_degraded_exits.py <cube>` in every post-config pass.** A hand-maintained
  list of which exits are broken decays; a per-cube measurement does not.
- **"Best of N" is only N if the N are distinct.** The 0.369 selection-noise floor was calibrated
  for best-of-26 against a family that is really ~16.
- **When building a lens, flag MISMATCH rather than consistency**, and **match on stems** - exact
  tokens called `atr_trail_1x -> atr_trailing_stop` a mismatch because `trail != trailing`
  (**`#239`, inside a check written minutes after citing it**).
- **Substring containment is not word matching.** Third instance this session; raising a match
  THRESHOLD reduces such a defect without removing it.

## A SILENT FALLBACK MAKES ONE NAME INTO TWO EXITS (B1771 - L526, CHECKLIST #251)

**MEASURED: `next_pivot_target` was 100pct silent-fallback for ELEVEN QUARTERS** (5,050 trades)
because `signals_at_entry` was not persisted before 2025-02-06 - then ~20-40pct after. **The exit
has a different identity either side of that date**, which mechanically guarantees the IS/OOS rank
instability that looked like a statistical mystery.

- **Plot a fallback share BY PERIOD, never as one overall rate.** A step function inside the sample
  window invalidates every cross-period comparison built on it.
- **Ask what else reads the same field.** `exit_regime_flip` reads `signals_at_entry` too and fires
  `regime_flip_max_days_20` on **100pct of trades in both periods** - a `time_stop_20d` duplicate
  that never flips.
- **Check that remediation advice names a REAL mechanism.** B1748's error text says to select
  `fixed_target_3atr`; no such exit is registered. My cross-check against it matched an **empty
  set** and reported a meaningless agreement number.
- **A "0 of N" or "100pct of N" result is a SCHEMA question before it is a finding.**

## DECOMPOSE A POOLED CORRELATION WITHIN GROUPS (B1770 - L525, CHECKLIST #250)

**MEASURED: the `-0.8` IS/OOS inversion is TWO defects.** Holding the exit fixed moved rho from
`-0.865/-0.779` to a weighted `-0.342/-0.419` - about half was the exit selector fitting in-sample
noise. **The residual is concentrated in ONE exit** (`next_pivot_target`, `rho = -0.73`, the exit
all ten top-ranked combinations chose); other exits sit near zero or positive.

- **Split a surprising pooled statistic by every group label already in the rows, before theorising
  about it.** The `exit` column was in the same records the whole time.
- **The two readings have different owners:** a selection artifact is a METHODOLOGY defect; a single
  member inverting is a PROPERTY of that member. The pooled number alone would have sent the wrong
  remedy at half the problem.
- **JUDGMENT-ONLY** - no gate can know which columns are group labels for a given analysis.

## THE QUEUE HAS A CLOSED VOCABULARY, AND EVERY TURN UPDATES IT (B1769 - L524, CHECKLIST #249)

**Owner ruling 2026-08-19.** Classes: `DONE / DROPPED / BLOCKED / DEFERRED / OPEN / RUNNING`.
Priority is its own column (`P0/P1/P2`). **Every non-terminal class states WHY, and placeholders are
rejected** - `scan_queue_vocabulary` (via `require_each`, so each bad row is named) and
`scan_queue_not_updated`.

- **A seventh class is a ruling, not a convenience.** "Any text satisfies the slot" is how 132
  labels accumulated across 688 rows.
- **An empty turn is DECLARED, never invented:** `NO-QUEUE-CHANGE: <reason>`. A mandatory gate
  otherwise creates fabrication pressure on queue-free turns - the escape converts that into a
  recorded, greppable decision. **A disclosure, not a workaround.**
- **Measure before choosing a migration default.** The clean plan was to map every unclassifiable
  row to `DEFERRED`; **71.7pct of them record COMPLETED work**, so it would have manufactured ~134
  fake open items. **A migration that changes what the record MEANS is not lossless because git can
  revert the bytes.**
- **Report parser output as parser output.** I quoted "641 rows" twice; the file has **688** - the
  lower number came from a regex requiring bold labels, and it was load-bearing in a recommendation.

## CHECK THE RECORD CAN STORE THE DISTINCTION YOU DREW (B1766 - L522, CHECKLIST #247)

**When you explain your own behaviour with a distinction, verify the artifact meant to hold it has a
field for it.** MEASURED: having told the owner a ticket was filed *"with no reason attached"* and
recorded that as a lapse, the truth was **38 of 38** - the queue has no reason field and no
vocabulary separating **blocked / deprioritised / not-started**. **A confession about discipline was
really a missing column, and the confession is what stopped me looking.**

**JUDGMENT-ONLY for now**: the gate (validate status against a closed vocabulary) cannot exist until
the owner rules on the vocabulary (`S6-B1766c`). Attach the mechanism when the ruling lands.

## NAME THE CLASS AFTER THE MECHANISM, NOT THE INCIDENT (B1768 - L523, CHECKLIST #248)

**`#245` was written one batch ago and violated immediately.** It said *"commit message"*; the class
is **any double-quoted shell argument** - bash substitutes in all of them, and `git commit -m` was
merely where it first bit. Next batch the same defect arrived via `python -c "..."`.

- **The memorable part of a failure is rarely the general part.** `git reset --hard` was the
  CONSEQUENCE; double-quote substitution was the mechanism, and the mechanism is what generalises.
- **Content with punctuation goes through the Write tool into a file you then execute** - or a
  quoted heredoc. The widened `scan_shell_substitution` is a backstop for a habit that should not
  produce candidates.
- **State the luck:** this instance failed to parse so nothing ran; B1765's parsed, so it executed
  `git reset --hard`. **Nothing about my care differed between the two.**

## STEMS AND WHOLE WORDS NEED OPPOSITE MATCHERS (B1767 - L521, CHECKLIST #246)

**A cost gate blocked a clean turn because `QUANT_CLAIMS` held `"free"` and the response said
"chosen FREELY per row".** L515 said *encode the stem* - correct for `_MISS_STEMS`. **The opposite
defect is a whole word whose meaning changes inside another word**, and one matcher cannot serve
both. `STEM_LISTS` is the explicit register; everything else is word-bounded via `_marker_hits`.

- **Boundaries are necessary and NOT sufficient.** Word-bounded `"free"` still fires on "free RAM"
  and "free tier". **A marker whose bare form is ambiguous needs its CONTEXT in the marker.** The
  half-fix would have shipped as complete; the negative control is the only reason it did not.
- **A sweep yields CANDIDATES, not defects.** 64 markers match inside longer words; most are
  deliberate stems. Same lesson as the 13-of-16 grep one batch earlier.
- **A seamless gate cannot have its FALSE POSITIVES reproduced either.** Seams were argued for
  against gates that MISS. **The gate that misfires most needs to be askable** - so corpus entries
  may carry `must_fire=False` as REGRESSION entries.

## NEVER PUT A MESSAGE IN A DOUBLE-QUOTED SHELL ARGUMENT (B1765 - L520, CHECKLIST #245)

**THIS RAN.** A commit message written to WARN about destructive commands contained backticked
examples of them; bash substituted them and **`git reset --hard` executed**, clearing the index and
reverting unstaged tracked files. Third instance of the git-safety hard rule (L49, L77) and **the
first never typed as a command** - prose about a destructive command is indistinguishable from the
command inside double quotes.

- **`git commit -F -` with a quoted heredoc (`<<'MSG'`).** No substitution. Never `-m "..."` for
  anything that might contain a backtick or `$(`. Enforced by `scan_shell_substitution`.
- **The safe form was already the habit; nothing enforced it.** One deviation was enough.
- **Verify the ARTIFACT, not the exit code.** `preflight: checking 1 file(s)` was the tell, in
  output already scrolled past. **A green commit hash and a clean `git status` were both consistent
  with the damage** - `git show --stat` plus re-reading the on-disk file is what found it.

## AVAILABILITY IS NOT ADOPTION (B1763 - L519, CHECKLIST #244)

**MEASURED: `require_each` existed from B1751 and two fresh any-vs-each defects shipped in the two
turns after it.** A primitive nobody reaches for is a library, not a guardrail - **so the reach is
what gets gated, not the primitive.**

- **If a rule you write says "each" or "every", the check routes through `require_each`.** Enforced
  by `test_b1763_universal_rules_use_require_each`; exemptions carry reasons.
- **Gate on the message a check EMITS, not on its body.** Grepping bodies for `each` flags 13 of 16
  gates and is wrong - marker lists use `any()` correctly, because a detector *should* match any
  marker. **One grep result is not one finding**: the 6 real candidates carried three different
  dispositions.
- **A deferral carries its reason.** `S6-B1762f` read *"candidate for the next enforcement batch"* -
  no blocker, no cap cited. A ticket is where a decision is recorded, not a substitute for making
  one.
- **Rank by depth, not by closability.** Two shallow gates shipped while the item explaining both
  was deferred. **At end of turn that ordering is automatic unless it is forced.**

## EVERY RULE YOU ADD SHIPS WITH ITS OWN ENFORCER (B1762 - L518, CHECKLIST #242/#243)

**This is the standing requirement for additions to this file.** Adding a section here, or an item
to CHECKLIST.md, is not complete until that rule names the function or pin test that enforces it -
**in the same clause as its number** - or carries an explicit `JUDGMENT-ONLY` / `PROSE-ONLY` waiver
stating why no mechanism is possible.

**MEASURED, which is why this is a rule and not a preference:** the B1761 section asserts *"every
gate carries a corpus entry"* and **17 of 25 gates had none, with nothing failing.**

- **`#231`'s gate could not have caught it.** `scan_prose_only_rule` asks whether a CODE FILE was
  touched this turn; touching it for ANY reason silences it. **Any-vs-each at the FILE level - the
  unit of enforcement is the RULE, not the file.** Enforced now by `scan_ungated_addition`.
- **A test that iterates OVER a registry validates only what is in it.** `test_b1760` checked gates
  IN the corpus, never that a gate IS in it. Enforced now by
  `test_b1762_every_scan_gate_has_a_corpus_entry`, with exemptions carrying reasons.
- **Proximity is not attribution.** The first version of `scan_ungated_addition` matched a +/-220
  character window, so one mechanism mention satisfied every number in a short response. **Scope to
  the clause.**
- **Probe the HALF-satisfied case.** Both defects above surfaced from a pair where one member was
  enforced and one was not - the case a self-derived probe never constructs.

## PROVE GATES ON THE VERBATIM INCIDENT, AND GIVE THEM A SEAM (B1760/B1761 - L516/L517, CHECKLIST #240/#241)

**MEASURED: my gate probes were built from the marker list of the gate under test - the test proved
the list matches itself.** Five gates passed 4/4 and 5/5 proofs that way and stayed silent on the
exact words that caused them. **`#226` (prove it can fail) is necessary and NOT sufficient**: a
synthetic negative satisfies it while every positive stays self-derived.

**MEASURED across 38 gates: 27 cannot be asked anything** - no injectable text, so their pin tests
assert only `gate([]) == []`, which passes for a correct gate, an inverted gate, and a gate wired to
nothing. `scan_false_skill_status` was defined, proven 5/5, reported live, and had never run.

- **Every gate gets an entry in `scripts/gate_incident_corpus.py`** - the VERBATIM text from the
  turn the failure happened in, plus the STATE that turn was in. No entry = unproven.
- **Every new `scan_` gate takes injectable `text=` and its state.** A gate with no seam cannot be
  distinguished from a gate that does nothing.
- **A seam that is never exercised equals no seam.** `scan_uninspected_constant` accepted `text=`
  and ignored it in two places.
- **And the mirror: a harness that STARVES a gate of its incident's state manufactures false
  failures.** My first sweep called 4 gates broken; **3 were correct.** Before ticketing a gate as
  silent, give it the full text and state - **reporting on your own harness is the same defect in
  the opposite direction.**

## STEM EVERY MARKER LIST, AND SWEEP THEM ALL (B1759 - L515, CHECKLIST #239)

**MEASURED: `scan_miss_capture_complete` stayed QUIET on the words *"which is the failure
itself"*.** Zero of nine `MISS_MARKERS` matched while `fail` and `failure` were both present - so a
plainly-stated defect went unticketed as a miss.

**Third instance of the class L509 named.** L509 said *encode the stem*; I fixed
`NARRATION_MARKERS` and left twelve other lists in the identical shape, including the one guarding
miss-capture.

- **A marker list is a claim about how a class will be WORDED.** Stem the root; the conjugations
  come free. Enumerating remembered phrasings is guessing.
- **When a marker list is fixed, sweep EVERY other list in the same file that turn.** 18 lists, 13
  unstemmed - found only when the owner asked a fourth time.
- **A fix applied to the instance in front of you is not applied to the class. Stating a class is
  not sweeping it.**

## GATE-CONSTRUCTION RULES (B1748/B1749 - L509, CHECKLIST #233, PROVEN)

**Measured: the replay harness scored 1 of 8 on this session's own errors. The first miss was the
error the gate was written for.**

`NARRATION_MARKERS` held `"reverted"`. The incident said **`"Reverting."`** - and `"reverted"` is
not a substring of `"reverting"`.

- **Encode the STEM, not the conjugation.** A marker list written from the past tense of a
  remembered incident matches only that tense. `revert` + ed/ing/s/d, not `reverted`.
- **Test every marker gate on a PARAPHRASE of the incident, never its exact words.** The exact
  words are the one phrasing that will not recur; a gate passing only on its own lineage example is
  fitted to a single string.
- **Every gate takes an INJECTABLE input for its evidence source** (2nd instance with B1713/L501:
  `sys.stdin`, then `_assistant_text`). A check whose input can only arrive from live plumbing
  cannot be validated, and will be trusted on no evidence.
- **A gate suite is fitted to the errors that built it.** The catch-count says nothing about the
  next error class. Report it with that caveat attached, always.

## SILENT-FALLBACK RULE (B1744 - L508, CHECKLIST #232, PROVEN)

**A fallback that looks like success will be served forever.**

B1743 changed this hook to emit the full skill. It shipped green and did NOTHING for two sessions
including a restart. Proven cause: the hook writes to a **cp1252** stdout on Windows, this file
contains U+2192 / U+2264 / em-dashes, the write raised `UnicodeEncodeError` - and the
`except Exception:` added *"so a missing skill never blocks a turn"* served the 12-bullet summary
instead. **The safety net was the defect.**

- **Any `except` substituting a DEGRADED output must announce itself** - stderr log, or the output
  says it is degraded. This is CHECKLIST #122 at a larger scale.
- **Verify through the REAL invocation path** - its encoding, its stdin, its cwd. I tested with
  `input='{}'` through a UTF-8 pipe (716 lines) while the harness used a cp1252 console (9 lines).
  **Same script, opposite result.**

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
| Propose a probe / say work is "seconds", "cheap", "one command" | OPEN the artifact and name the FIELD it needs; an effort estimate is a quantitative claim | CHECKLIST #230 EXT (B1736 / L506); "split by exit_reason, offline, seconds" against a file with no such column |
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
