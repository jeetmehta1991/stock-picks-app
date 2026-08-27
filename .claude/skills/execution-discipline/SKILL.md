---
name: execution-discipline
description: MANDATORY turn protocol for the stock-picks-app repo — applies UNPROMPTED at the START of every working turn (any turn that produces a recommendation, code change, audit, review, or doc update - **AND every turn that ANSWERS A QUESTION, per B2134/L634: a factual answer matched none of those five, so Phase 6.2's findings-need-tickets rule was unreachable by this very predicate on the turn type that generates findings most cheaply**) per owner directive 2026-07-07; the owner never needs to mention it. Enforces CHECKLIST pre-flight, no-silent-miss disposition ledger, test pyramid on every code change, LEARNINGS feedback loop on every miss, deep code-verified audits, and the absolute anti-fabrication truth standard. Also invocable as /execution-discipline.
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

**Mechanically enforced** by the B1744 auto-injection hook and scan_discipline_not_loaded (a substantive turn without the full skill in context is blocked).

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

8b. **RECOVERY CADENCE IS A COVERAGE CLAIM (L644/B2175).** Any long-running
   process's checkpoint/heartbeat cadence implies a LARGEST WINDOW a hard death
   can lose - state it as a number (min of every trigger: sim-day gates AND
   timers), never as a frequency. sw10 died at 19 minutes with a day-50 gate
   and a 30-minute timer both unfired: the window was real, enumerable from
   two constants, and nobody had multiplied them out. The manifest's
   obsolescence risks is where the number lives.

9. **CAPABILITY CLAIMS ARE CLAIMS (B1731 / L505 / CHECKLIST #230).** Every
   example above is about DATA - counts, coverage, fire rates. **Claims about
   the SYSTEM ITSELF slip past**: what a tool can load, what a format permits,
   what a budget allows. They feel like background rather than findings.
   *MEASURED:* I would never publish a cell count unrun; I published *"the skill
   loads as 12 of 644 lines"* having run nothing, and built an owner-facing
   trade-off on it. Invoking it delivers all 644. **Run the probe that settles a
   capability, or label it UNVERIFIED - the four evidence classes apply
   unchanged.**

   **THIRD SHAPE (B2179 / L645): the OBJECTION.** A case-against carries the same
   evidence burden as a recommendation. *"The cheaper alternative was never costed"*
   is itself an uncosted claim about that alternative's cost — the asserted-consequence
   shape wearing a critic's coat (L622 was the same shape from the advocate's side).
   MEASURED: the mandated Contrarian objection claimed a signals-shifted MCPT variant
   died uncosted; one file-open showed no cube carries a signal series, so the variant
   re-runs the engine per permutation and the refusal it attacked was correct. Cost an
   objection before filing it, or file it as a QUESTION.

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

   c2) **RECOVERY - "one command", "just resume", "rollback is trivial." (L646,
   third instance of the class)** A recovery estimate is a capability claim
   about the CONFIG the recovery command reads - and unlike other effort
   claims, acting on a wrong one can DESTROY the state it describes: the
   "one-command" sw30 resume pointed at a spec with resume=False, which would
   have restarted day 0 over a day-57 checkpoint. **Open the config the
   recovery would read and verify it points where the prose says, BEFORE
   quoting the recovery as cheap.**

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
   universe/ticker list, budget projection** (the wall-clock projection field exists because
   a manifest shipped without one - L333); then answer in writing *"what
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

4. **A GUARD MUST NOT SHARE THE CONTROL FLOW IT GUARDS (L637/B2143).** A limit
   evaluated at the top of a loop bounds ITERATIONS, not wall-clock — and those
   differ exactly when one iteration goes pathological, which is the case the
   limit exists for. MEASURED: a 2.5h cap ran to 2.9h with no kill and no warn,
   while the code was correct and the clock was set before the loop; the process
   simply never returned to a day boundary. Same failure, three ways, in one run:
   the cap could not fire, the first checkpoint was gated at sim-day 50 so
   nothing was recoverable, and the monitor plus its cron were session-scoped and
   died with the session, leaving a healthy process computing blind for 2h34m.
   **Every safety mechanism depended on the watched thing reaching a point where
   it could be observed.** So: a wall-clock cap needs a watchdog outside the
   guarded flow (thread, supervisor, or signal); a long run writes a heartbeat
   from its FIRST iteration, never from a milestone; and the durable channel is a
   file any session can read, never a session-held pipe. **B2144 SWEEP: this is
   not one guard's bug.** The engine has SEVEN loop-gated writers - milestone
   telemetry, the progress log, a 50-day site, three paired checkpoint writers,
   and the wall-time cap - and ALL SEVEN sit inside the day loop, so NOTHING in
   the runtime path reaches disk independently of it. Even a 30-minute
   time-trigger, added precisely so progress would survive, is evaluated once per
   simulated day and so is a 30-minute save only while days are short. When you
   find a guard sharing its subject's control flow, sweep for its siblings before
   fixing it: the fix is one supervisor outside the loop, not seven patches.

5. **AFTER ONE FAILED EXACT-MATCH EDIT, CHANGE ROUTE (L638/B2145).** A patch
   whose content is settled can still cost four attempts to land. MEASURED in one
   session: a shell heredoc collapsed regex escapes TWICE, then the Edit tool
   refused the identical text THREE times because the file is CRLF while the Read
   view renders LF. It landed only as a scratchpad script that located the target
   by its `def` line and replaced a LINE RANGE. So: never pass backslash-bearing
   code through a heredoc; after ONE failed exact match, stop matching and address
   by anchor plus line range from a script file; and in source-scanning helpers
   prefer explicit substring checks to regex alternations — the alternation in
   that same patch matched 7 sites in a direct probe and 3 from inside the test.
   **When the transport keeps failing, the content is not the problem — stop
   re-sending it and change how it travels.**

6. **A NUMBER INSIDE AN OPEN TICKET DECAYS SILENTLY (L639/B2153).** A ticket's
   STATUS and its MEASUREMENT rot at different rates. MEASURED: a row recorded
   "4 manifest fields read by no gate"; the true count was 2, because two had
   been wired by later batches and nothing told the row. Its status was still
   correct - the work is genuinely unfinished - so no staleness check fired,
   while its number stayed quotable and wrong by 2x. Same shape as a retirement
   requested on evidence four batches out of date. **When a sweep touches a class
   an existing ticket quantifies, re-measure and correct that ticket in the same
   close** - a count inside an open ticket carries a response's evidence burden.
   Detection is JUDGMENT-ONLY: no scan distinguishes a stale count from a current
   one without re-running the measurement it summarises.

7. **CLOSING HALF A TICKET NEEDS A NEW ID (L640/B2154).** The ledger holds ONE
   state per ticket by last-row-wins, so appending a non-terminal row for the
   remainder REOPENS a terminal id and makes every derived count unsound. This
   happened TWICE in one session, the second time two batches after I wrote the
   rule - because instance 1 was filed only as a queue row, where the next
   occurrence cannot see it. **Close the id and open a NEW id for the remainder
   in the same append**, and before appending any non-terminal row check whether
   that id is already terminal (`scripts/queue_state.py`, one call). The reused
   id will FEEL like continuity - same subject, same thread - and terminality is
   invisible at the moment of typing. Pin: test_b1795_queue_counts_are_per_ticket.

8. **SILENCE IS NEVER EVIDENCE OF WORK IN PROGRESS (L641/B2158).** A record
   that logs an ENDING only on the success path says nothing about the endings
   that matter. MEASURED: a launcher writes its completion line after the
   engine returns, so a killed run leaves a log SHAPE-IDENTICAL to a live one -
   2 of 8 real logs were in that state, both from kills, neither able to say
   so. A kill signal skips every write path the writer could use, so the fix is
   never a better writer: **make the READER authoritative and one-directional**
   - absence of a completion record reads as DEAD unless a live process proves
   otherwise. Ask of any status surface: *if this job died right now, would this
   artifact look different?* Pin:
   test_b2158_a_log_without_an_ending_is_dead_not_running.

9. **A GUARD MUST FAIL CLOSED ON THE ABSENT INPUT (L642/B2159).** A check
   conditioned on the presence of the thing it guards is not defensive - it
   converts UNDECLARED into APPROVED. MEASURED, on a check I had shipped that
   same day: `if cap is not None and cap > LIMIT: refuse` meant a manifest
   that simply omitted the field skipped the check, so an owner HARD CAP went
   unenforced against exactly the manifests least likely to declare a bound.
   Write `if X is None: refuse` BEFORE `if X > limit: refuse`. **The absent
   case is not the safe case; it is the case the guard exists for.**
   And a check nobody has watched FAIL is indistinguishable from a check that
   does not exist: keep a known-bad corpus proving each check fires with a
   reason naming the defect, plus a reachability assertion that every defined
   check is reached from the entry point - this session shipped one wired to
   call ITSELF, which ran zero times and was caught by reading, not by a test.
   Pins: test_b2159_known_bad_manifests_are_each_refused,
   test_b2159_every_gate_check_is_reachable.

10. **A SWEEP MUST CLASSIFY, NOT COUNT (L643/B2161).** "N instances of the
    bad pattern" invites a mass edit; "N instances, M of which mean a bound"
    is a finding. MEASURED: after fixing a cap check that approved every
    manifest omitting the field, the same pattern swept across the safety path
    returned SEVEN instances - and all seven were correct. One was an advisory
    that must never block; six read optional DATA where absence means the
    feature is unavailable. **Burning the pattern down on sight would have
    'fixed' seven correct call sites and changed engine behaviour.** The
    discriminator: absence of a BOUND (cap, quota, required declaration) must
    REFUSE, absence of a FEATURE must SKIP. Read every instance and report the
    population WITH its classification - the sweep's value is often proving the
    blast radius is one, not seven. Pairs with rule 6: a number without its
    per-instance reading is not yet evidence.

11. **A NEW DETECTOR'S FIRST NUMBER IS A HYPOTHESIS (L644/B2162).** The
    output of a measuring instrument is itself a measurement and carries the
    same evidence burden. MEASURED: minutes after writing that a sweep must
    classify rather than count, I quoted a keyword matcher's 68-row split,
    then hand-read 5 of the rows it flagged and found 5 misclassifications -
    **and the error ran in the direction that made my new rule look
    necessary.** A detector built for a class is not exempt from that class.
    Before quoting a NEW scan's headline, hand-read a sample of what it
    flagged and report the sample error rate beside the count; if the sample
    disagrees, keep the script and drop the figure. Nothing in the workflow
    re-checks a number that confirms the thing you just built - that is why
    this one is JUDGMENT-ONLY and cannot be scanned for.

12. **A DETECTOR SHRINKS THE POPULATION; THE READING STATES THE RESULT
    (L644 addendum/B2165).** Quoting a screening tool's raw count as the
    finding is how a filter gets mistaken for a measurement. MEASURED: a
    regex flagged 14 live tickets as "quoting a count"; hand-reading all 14
    gave a precision near 9 of 14 - the misses were a DATE fragment, an
    owner-item number, a CHECKLIST reference and two process IDs, none of
    which a digit matcher can tell from a measurement. **The same reading
    found a real stale figure the count alone would never have surfaced.**
    So: report what you READ, cite the detector only as the thing that made
    the reading affordable - here, 1,391 tickets narrowed to 14 in a minute.

13. **A COPY IS A FRESH SHIPMENT OF OLD CODE (L645/B2167).** Copying an
    existing block preserves its defects with the same fidelity as its
    behaviour, and the consistency rationale (same dict, one schema) actively
    suppresses the question of whether the source block is correct. MEASURED:
    a kill-path emitter faithfully copied the periodic emitter - including a
    phantom getattr name never assigned anywhere - so every state file ever
    written recorded open_trades: 0, and M6 measured a constant. The pins
    missed it because NO FIXTURE HELD A NON-ZERO OPEN COUNT: a field that is
    always 0 passes every test whose fixture also has 0 of the thing. So:
    audit a copied block's attribute references against the class as part of
    the copy, and pin an emitter with at least one fixture holding a NON-ZERO
    value of each asserted field. Pins: test_b2167 (phantom names banned
    engine-wide), test_b2148 (fixture now carries a real open trade).

14. **FRESH-EYES REVIEW CADENCE (standing).** Before every batch-size
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
| C7 banned-pattern diff scan | every commit | ADDED lines with `not s.get(`, default-True strategy gates, relative `data_prefetch` paths (waiver: same-line `# preflight-allow: <rule>`). **B2128 CORRECTION: this row claimed `except: pass` too - it never did.** C7 has exactly three patterns, and a line-scan cannot see the multi-line form; silent excepts are now held by the AST ratchet `test_b2128_silent_except_pass_is_a_shrinking_set` (frozen at 134, shrink-only). `#224` inside the enforcement table itself. |
| C8 queue-entry gate | every commit | commits not staging EXECUTION_QUEUE.md (escape: `GIT_QUEUE_EXEMPT=1`, logged to `.queue_exempt_log`) |
| C9 doc→queue cross-check | every commit | `output_audit/*.md` referencing ticket IDs absent from the queue |
| #182 verdict-denominator | every turn-end (Stop hook) | a response stating a verdict with no "N of M" denominator naming the tested scope (B1504) |
| Gate B Stop hook | every turn-end (`.claude/settings.json` hooks.Stop → `scripts/verify_turn_compliance.py`) | ending a turn with modified TRACKED files uncommitted (escape: one-shot `.stop_exempt`, logged) |

- **Fresh clones** (AWS instances, new machines): git-hook shims do NOT
  travel with clones — run `bash scripts/install_git_hooks.sh` (or `.bat`)
  once after `git clone`, per AWS_LAUNCH_PLAYBOOK Gate 5. The Stop hook and
  preflight script are committed and need no install.
- **Manual dry-runs:** `python scripts/preflight.py --staged` (commit gates)
  and, for the turn gate, **`TURN_GATE_TRANSCRIPT=<transcript.jsonl> python
  scripts/verify_turn_compliance.py`**. **B1843 - the bare command HANGS.** It
  reads stdin, which only the Stop hook populates, so standalone it blocks
  forever (measured: 300s and 60s, zero bytes out). **And `</dev/null` is a
  trap** - it exits 0 while the script prints *"0 transcript entries loaded ...
  this is NOT evidence of compliance"*. **A dry-run that returns clean because
  it read nothing is worse than no dry-run.** With the env var set it returns
  every violation at once, in seconds, over a 128k-line transcript.
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

JUDGMENT-ONLY: whether the checklists and learnings were actually READ is unobservable to any scan; the compensating mechanism is the B1744 auto-injection (this file arrives in context every turn) plus the anchor rules that keep lessons in the loaded files.

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
- **DEPTH-FIRST ORDERING (B2056 - S6-B1763e, L519's rank-by-depth half):** among
  EXECUTABLE items, the deepest/highest-priority ledger row is worked FIRST -
  P0 before P1 before P2, decision-gated skips excepted. "Two shallow gates
  shipped while the item explaining both was deferred" is the failure; at end
  of turn the shallow-first ordering is automatic unless forced. JUDGMENT-ONLY
  for detection (executability is a judgment no scan can read); durability
  pinned by test_b2056_depth_first_rule_is_in_the_skill.

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
- **NEVER RESOLVE AN ADVICE-VS-INSTRUCTION CONFLICT SILENTLY - IN EITHER
  DIRECTION (B2133 / L633, owner-corrected 2026-08-24).** I applied 5 council
  dispositions directly; 2 were scope cuts against a standing "execute all open
  tickets", and I said nothing - the owner had to ask why 3 tickets were
  untouched. **The error was the SILENCE, not the disagreement.** Owner,
  verbatim: *"if i am very much wrong, its yours and councils job to correct
  me"* - so silently COMPLYING with an instruction you believe is mistaken is
  the same defect wearing the opposite coat, and is equally forbidden. **When
  advice and instruction conflict: state the conflict, give the reasoning and a
  recommendation, and proceed as instructed unless the owner rules otherwise.**
  Disagreement is owed out loud; the decision stays the owner's.
- Owner approval gates: ALL rule/threshold/parameter changes, ALL paid API
  runs (small test → review → approval → scale), Batch B launch
  (`feedback_no_auto_launch_batch_b` — explicit typed instruction only).

**Mechanically enforced** in part by scan_compliance_is_content (#238: the compliance statement must cite items with per-item status); the per-recommendation pre-flight ordering itself is JUDGMENT-ONLY - no scan can see whether verification happened BEFORE a recommendation was drafted.

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

**Mechanically enforced** by the C6 pyramid stamp in scripts/preflight.py (a *.py commit without a fresh green .pyramid_stamp is blocked - it fired on this very program at B2025).

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
   (CHECKLIST #106 / #44(b)). **EXTENSION (B2137 / L637): a field empty for
   100pct of a population is a READER bug until proven otherwise.** A funnel
   column rendered `-` for every config across four runs and two grader
   generations; I ticketed it as an artifact limitation and an advisor predicted
   fresh artifacts would fix it. Both wrong - it read `admit`, present only on
   carried ranking rows, while the values sat as top-level keys on every result
   row. **Open ONE row and look for the value under another name or another
   level before writing "not recorded" into a ticket** - and note that the
   honest-rendering rule (an unmeasured value shows `-`, never `0`) is exactly
   what let this look like good reporting for as long as it survived; temporal coverage checked across the full
   backtest window, not one date (CHECKLIST #156 / L201).
7. **Line-by-line ticket extraction** when reviewing feedback or prior turns:
   every sentence becomes a candidate ticket BEFORE synthesis
   (`feedback_line_by_line_ticket_extraction_before_synthesis`).

JUDGMENT-ONLY: audit depth (happy-path artifacts opened, representative sampling, consumer paths traced) is a property of how work was done, not of the text that reports it; the evidence-artifact requirements (#124) and the executed-check vocabularies are the gateable slices and are gated where they appear.

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

**PROVENANCE HALF (S6-B1705e / B1801): COMPUTED FROM WHAT?**

**`#201` asks whether a quantity was computed, never what FROM.** `2.422` came from
`rng.normal(1, 3, 30)` in my own probe and satisfied it completely - *"measured"* was true of the
arithmetic and false of the meaning.

- **Label a figure from `rng`/`random`/a hand-made fixture `SYNTHETIC` where you quote it** - not in
  a footnote, not in the method. Enforced by `scan_synthetic_provenance`; **the escape is one word.**
- **A synthetic probe can still produce a real finding.** That probe's boundary result (n=29 -> None,
  n=30 -> a value) was genuine. **Separate the STRUCTURE a fixture demonstrates from the VALUE it
  produces** - the first can be evidence, the second almost never is.
- **Prefer a deterministic fixture when the test is about behaviour.** If no number is quoted, no
  provenance question arises.

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

**EXTENSION (B2019 - L617): a verdict about WHY a population is EMPTY is a causal claim.**
"0 carried because the universe lacks power" shipped into a committed ledger while every
excluded row carried holdout_n=0 from a filter clause - the disproof was ONE row read.
Before naming a power/sample cause for an empty result set, READ the excluded rows' fields;
an all-None column across a whole verdict population means CHECK THE FILTER CLAUSE first.
Mechanism: the existing scan_unverified_cause class - the phrasing carried no cause-marker,
the L509 marker-stem limit, already recorded.

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

JUDGMENT-ONLY for detection: no scan compares code output-shape to the PLAN's specified deliverable (the drift lives between two documents' meanings). The values-vs-claims halves that ARE derivable got mechanisms: verify_describing_artifacts.py record-vs-code checks plus the B2054 status-prose anchor gate.

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
6. **LAND ALL FIVE MEMBERS IN ONE COMMIT (B2129 / L630).** LEARNINGS + the
   CHECKLIST citation + the queue row + the fix + the mechanism/pin go in a
   SINGLE commit, not across successive closes. **MEASURED: splitting them
   produced a 20-close gate storm** - each close touched LEARNINGS without
   SKILL.md, or SKILL.md without a pin, so the Phase-5 gates alternated and
   every retry re-emitted the mandatory blocks to the owner, who asked why the
   same table kept printing. **The remediation's SHAPE is what reaches the
   owner, not its content.** One commit, all members, then close once.
   **AND WHEN THE ARTIFACT EDITED IS THIS FILE, "all members" INCLUDES THE PIN
   (B2130 / L630 addendum).** The commit that added THIS member shipped two new
   skill rules with no test - `#231` - because the mechanism member reads as
   being about the FIX, and a rule added to the skill IS the fix. A skill edit
   and its `test_b2123` fragment go in the same commit, always.
   **AND IN THE SAME SCRIPTED CALL (B2132 / L632 addendum).** "Same commit" was
   not enough - the split recurred THREE times in one day (B2129c, B2130b,
   B2132d), each time with this rule already written. Staging the doc edit and
   the pin edit in ONE python call makes them inseparable by construction; a
   habit that depends on remembering, after three failures, is not a habit.

## LOAD-THE-SKILL RULE (B1728/B1729 — L504, CHECKLIST #229, mechanically enforced)

**The hook injects 12 bullets. This file is 644 lines. Invoking it delivers all 644.**

I reported the gap as a structural limit and offered the owner a workaround. It was an un-run tool
call — the copy I was reasoning from had been truncated by COMPACTION, not by design.

**Any turn that touches the repo invokes `Skill(execution-discipline)` first.** The 632 lines the
summary omits are not filler: `#182` verdict-scope, POST-FIX RE-CHECK, B1446
no-arbitrary-decisions, the TRIPWIRE TABLE and ANCHOR-THE-RULE — **all violated in the session
where only the summary was loaded.**

Enforced by `scan_discipline_not_loaded()` in `scripts/verify_turn_compliance.py`.

**A skill is triggered when it is the OBJECT of the request, not only when it is the method
(L624/B2124).** "Update fable mode" triggers fable-mode; editing, reviewing or reasoning ABOUT a
skill is the strongest case for loading it, because the loaded file is independent evidence the
edit landed. "It was the subject, not the method" is not an exemption.

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

**B2129 / L628 — THE UNADDRESSED CLAIM CAN ARRIVE THROUGH A QUEUE ROW, NOT ONLY A DOC EDIT.**
I promoted a rule into this file and recorded it in a ticket row naming no pin. `#231`'s own
check PASSED (the pin landed in the same batch), while the ROW still claimed a rule with no
address - `#264`, caught a close later. **Pin the promotion in the same batch AND name the pin
in the row.** `test_b2123` asserts the clause survives, so a promotion is checkable, not asserted.

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

**EXTENSION (B1797 / L548) - `JUDGMENT-ONLY` IS TWO QUESTIONS, AND THE SECOND IS USUALLY YES:**

| question | for B1797 |
|---|---|
| can the CLASS be DETECTED? | **no** - no scan tells a RULE from an EXAMPLE of one |
| can the FIX be kept from VANISHING? | **yes** - assert it is still in the docs |

**Reaching for `JUDGMENT-ONLY` reads as honest, and it is - about detection. It is also where the
thinking usually stops.** A rule written into a doc can be dropped from that doc later, which is the
same disappearance in slow motion, and THAT is mechanisable even when detection is not.

- **So `JUDGMENT-ONLY` is never the whole answer until the durability question has been asked out
  loud.** State it as *"no DETECTION mechanism; durability pinned by `<test>`"* whenever both halves
  apply - the two are different claims and collapsing them overstates the first.
- **Pin the DIAGNOSTIC, not just the rule.** `test_b1797_matcher_rung_rule_is_in_the_durable_docs`
  asserts the three rungs AND *"disjoint vocabulary"* survive in both files. **Without the
  diagnostic the table is trivia** - the usable part is *two domains, one claim, no shared root.*
- **Prove the pin can fail (`#226`).** Deleting the diagnostic from `CHECKLIST.md` must fail the
  test. A presence-assertion that passes against a gutted file is the inert-gate defect in a new
  costume.

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

## A FIGURE YOU REPEAT IS RE-DERIVED, NOT CARRIED (B1827 - L559, CHECKLIST #256 ext)

**MEASURED: I told the owner the `#201` gate had produced "roughly six false positives" across
several turns. It is 5 mechanical false positives and 2 SUBSTANTIVE catches** - it has never been
wrong about the concern.

- **Check which way the error points.** *"Six false positives"* supported the conclusion I had
  already stated - *do not patch this again*. The correct figure supports the opposite. **An error
  that argues for what you already decided is the one you are least likely to re-derive.**
- **`#256` covers a ticket's number; this covers a number you keep SAYING.** Nobody re-checks a
  figure that has already been said out loud - that is exactly how it survives.
- **A RECORDED DEFECT HAS AN EXPIRY, AND THE LEDGER NEVER SHOWS IT (B2139 / L638).** I quoted a
  recorded exit defect three times in one session from the LEDGER TEXT; a later batch had fixed
  it, and the owner reasonably ordered the exit retired. **An append-log entry is evidence about
  ITS OWN DATE and nothing later** - both the defect and its fix are true entries. Before
  repeating a recorded defect as a LIVE fact, re-derive it (here: one per-cube measurement showed
  42 real flips where the record said zero), and when summarising historical step results say
  which findings have since been closed.
- **A deterministic fixture does not FEEL synthetic.** `rng` announces itself; `pd.Series([1.0,
  2.0, 3.0])` looks like data. Choosing determinism to dodge the provenance question is what made
  those numbers feel earned (B1801's rule, violated two batches after I wrote it).

## AN ARTIFACT MUST CARRY THE KEY IT WAS RANKED ON (B1820 - L558, CHECKLIST #277)

**MEASURED: `step1_ranking` emitted the HOLDOUT Sharpe as its first field and omitted `is_sharpe`,
the key it ranks on** - so the artifact showed exactly what the leak B1718 fixed would have
produced. **Real separation, unverifiable from its own output.** Load-bearing: `m = 41` versus
`m = 820` turned on that field.

- **Emit the ordering key FIRST, beside the value it is not.** A measurement kept for information is
  fine; a measurement sitting where the ranking key belongs is misleading.
- **The test: could a reader tell this artifact from one the BUG produced?** If not, it is not
  evidence, however correct the code.
- **Same shape as a vacuous test.** My AST check for this class walked `ast.Assign` while the
  declaration was `ast.AnnAssign`, so it examined nothing and passed - **a test with no content and
  a report with no content fail identically, and neither is visible from the result.** Only running
  the failure case separates them.

**Mechanically enforced** by test_b1820_step1_ranking_emits_its_ranking_key.

## AN ASSERTED CONSEQUENCE IS A CLAIM - COMPUTE IT (B1833 - L560, CHECKLIST #278)

**MEASURED: both retractions in one turn were consequences asserted without computing.**
*"Re-running wave 1 would not fix it"* needed a `git log`; *"the lever costs ~2x runtime"* needed
`100 x 2 = 200 x 1`. **Each took under a minute once attempted, and neither was attempted** - a
consequence feels like reasoning rather than a claim.

- **A consequence carries a measurement's evidence burden.** *"X follows from Y"* is a claim about
  X, and Y being verified does not verify it.
- **Check which way it points.** Both errors favoured the position I already held. `#256`-ext covers
  a figure you REPEAT; this covers one asserted for the FIRST time, which no rule reached.
- **Retroactive: four asserted consequences, four wrong** - the re-run advice, the ~2x runtime, the
  plan's *"enforced mechanically ... a file path"* that never existed, and B1775's assumed join.

## RUN THE TURN GATE YOURSELF; THE STOP HOOK IS THE BACKSTOP (B1842 - L563)

**MEASURED: three Stop-hook blocks in a row at one turn close** - no compliance
statement, then the statement present but ALL-CAPS against a case-sensitive
matcher, then two OPEN rows with no `_reason:_`. **Each close fixed only what the
gate had just named.**

- **Run `TURN_GATE_TRANSCRIPT=<transcript.jsonl> python
  scripts/verify_turn_compliance.py`** - it returns all violations at once.
  Running it once before ending replaces three round trips with one.
- **B2129 / L628 - AFTER THE FIRST BLOCK, RUNNING IT YOURSELF IS MANDATORY, NOT
  ADVISORY.** This bullet said "run it" and named no trigger, so I fixed one
  named violation per close **twelve consecutive times**. Every blocked close is
  a NEW turn-end that must re-emit the SKILLS INVOKED line and the six-class
  ticket table, so the owner saw a zero-delta table twelve times and asked why.
  **The retry loop, not the work, is what reaches the owner.** One self-run over
  a 21MB transcript returned the whole list in seconds. Trigger: any turn that
  shipped code, or any turn already blocked once.
- **B1843: the BARE command hangs** (reads stdin, which only the hook fills) and
  **`</dev/null` exits 0 having read nothing**. L563 cited the bare form before
  anyone ran it - **a lesson recommending an unrun mechanism, inside the entry
  about mechanisms existing but not running.**
- **The mechanism existing is not the mechanism running** - same shape as
  `require_each`, which had existed for batches before I used it.
- **Compliance failure against `#45` and `#247`, not a new class.** A fifth rule
  restating four that were ignored is `#136` theater.

## A REVIEW'S EXISTENCE MATRIX CANNOT SEE CONTENT DEFECTS (B1992 - L614, CHECKLIST #276b/#281)

**The owner-directed review of 26 addressal commits: every promised artifact
existed - 24/24 pins, 11/11 L-entries, every mechanism present - and the two
real misses were CONTENT, both the reviewer's own:**

- **A pin case passing through the WRONG BRANCH** (trigger-absence instead of
  the escape it claims to prove). A hedge inside an assert message - *"wait,
  it must also..."* - is a finding you noticed and filed nowhere.
- **13 new citations of an item proved undefined in the same session.** A
  number-frozen ratchet is not shrink-only if frozen members can be cited
  indefinitely - freeze the per-file COUNTS, and measure the baseline LAST,
  after every edit of the batch (the freeze's own message quotes the number).
- **The L-entry batch re-exam (B1446 rule 5) is a separate question from
  per-instance citations** - ten of eleven were covered; the eleventh became
  `#281`.

**A gate's trigger must never match the compliance it demands (B1996 - L616,
CHECKLIST #246):** a bare `#23` substring in a trigger list armed the sweep
gate on every mandated compliance block citing the miss-capture and
retroactive-sweep items - four consecutive treadmill firings. (Numbers in
L616; this bullet avoids them because the citation count-freeze on anchor
docs is itself one of this arc's mechanisms, and it just fired here.) Before adding any trigger, ask: *would a fully
compliant turn's REQUIRED closing statement contain this string?* If yes, the
trigger is wrong. Enforced by
`test_b1996_citing_an_item_does_not_arm_the_sweep_gate`.

**And two second-order rules from applying the fixes (B1993 - L615):** a
detector over a corpus you also write must not assume the corpus's formatting
discipline - the append-log's odd backticks flipped a whole-file strip's
parity, so scrub PER LINE (`#275`); and a count-freeze whose home is inside
its own measurement taxes every edit of the mechanism - scope freezes to the
DOCS where anchors live, never to the machinery quoting the incidents (L586's
costly-in-the-wrong-place sibling). **And a failed edit must BLOCK its commit** - chain
edit-then-commit with `&&`, never as sibling commands; a sibling chain
proceeded past a failed assertion and produced a commit message claiming an
edit that never landed (B1993d, JUDGMENT-ONLY: no scan reads shell chaining;
the `999e23d` retraction is the precedent; second instance L623/B2122 - a
zero-hit VERIFICATION grep sibling-chained before its dependent commit, so a
false claim shipped: the rule covers checks, not only edits, and a
presence-grep must assert its match count to be able to fail; **THIRD instance
L629/B2129** - an anchor assert failed and the newline-separated commit shipped
a row claiming a skill edit that never landed, hours after I authored this very
rule. **The trigger is the FAILURE MODE, not the tool**: any step whose failure
would invalidate a LATER step is joined to it with `&&`. I chain when thinking
about commits, and twice now the failing step was an EDIT or a CHECK. Prefer one
edit per shell call when its success is load-bearing for a commit message).

**Mechanically enforced** by the corrected B1986 case, the per-file citation
count-freeze in `test_b1971_no_new_dangling_checklist_citation`, and `#281`'s
`test_b1974_generated_artifact_is_not_older_than_its_generator`.

## GATE EVIDENCE HAS THREE AXES: PROVENANCE, WINDOW, KIND (B1987 - L612, CHECKLIST #262)

**The 8-gate conversion arc (B1967-B1986) closed, and its shape is the
lesson.** "The right evidence" decomposes into three separate questions, each
learned on ONE gate and then found missing in siblings:

- **PROVENANCE** - ran vs typed (`_executed_tool_text`; Write/Edit content is
  authored, a heredoc body is data).
- **WINDOW** - turn vs session-since-compaction (`_turn_entries`;
  `_skill_context_text` for anything that STRADDLES the boundary).
- **KIND** - command vs read vs skill-context (`_inspecting_tool_text`; a
  Read's file_path is opening, a shell command is executing).

**Ask all three before wiring any new gate's evidence.** The axes only stopped
regressing when the TRUNK owned them - and the closure is pinned, because the
natural way to write gate nine is the older, shorter `_tool_text` name.

**Mechanically enforced** by `test_b1987_no_gate_reads_raw_tool_text` (zero
raw call sites, shrink-only at zero).

## EACH GATE'S QUESTION NAMES ITS OWN WINDOW (B1983 - L610, CHECKLIST #196)

**B1980's turn-scoping was right for the collectors and wrong for one
consumer.** A `Skill` invocation STRADDLES the turn boundary by construction -
the tool call lands, then the skill body arrives as a USER-role message, which
resets the slice - so the discipline gate fired on the turn FOLLOWING every
successful load.

- **A post-fix re-check that enumerates call sites is not done**: ask, per
  consumer, what WINDOW its question needs. "Did this turn sample a source?"
  is turn-scoped; "is the skill in context?" is session-since-last-compaction.
- **Both wrong windows fail differently**: session-wide missed the compaction
  drop (the original incident); turn-wide misses every load.
- **Prove a re-windowed gate in both failure directions AND on the live
  transcript** - the constructed cases show the boundary; only the live run
  shows the gate is quiet on genuine compliance.

**Mechanically enforced** by
`test_b1983_skill_gate_window_is_session_since_compaction`.

## A TURN GATE READS THIS TURN - ON EVERY COLLECTOR (B1980 - L609, CHECKLIST #262)

**`scan_partial_read` fired two turns running, both false: the verdict came
from this turn's final block, the truncation evidence from 122 `head -` lines
across the session's whole history.** The turn-scoping rule (B1742) was
learned on the response collector and never carried to the tool collectors.

- **Evidence and claim must share a scope.** A gate pairing this turn's words
  with last month's commands is comparing two different turns.
- **`tool_result` entries are typed "user" but are not the user** - a turn
  boundary drawn there resets at every tool call.
- **Debug against the live artifact, not a mental model.** Two turns of
  plausible-cause guessing each found A defect; one run against the real
  transcript found THE defect.

**Mechanically enforced** by `test_b1980_tool_evidence_is_scoped_to_the_turn`.

## A NEW HELPER STARTS WITHOUT ITS SIBLINGS' LESSONS (B1979 - L608, CHECKLIST #262)

**`scan_partial_read`, freshly converted to executed-text, fired on the very
turn that shipped the conversion** - the commit message quoted a `sed` line-
range inside a heredoc, and a heredoc body is DATA the command carries, not a
command that ran. The scrub for exactly this existed **twice in the same
file** (B1880, B1925 - "the sibling of B1880's"); the helper was built later
and inherited neither.

- **A `#237` sweep covers the sites that exist when it runs.** The next site
  re-introduces the defect - nothing carries a lesson into code that does not
  exist yet.
- **Move the lesson to the trunk the first time a second leaf needs it**: fix
  shared scrubs in the shared helper, never per-consumer.
- When a gate fires on the turn that shipped it, check for a scrub its
  siblings have and it lacks, before doubting the conversion.

**Mechanically enforced** by `test_b1979_heredoc_bodies_are_data_not_commands`
(both directions, both converted consumers).

## RUN THE CONTROL BEFORE THE EDIT (B1974 - L607, CHECKLIST #226)

**Regenerating `PHASE_1B_ROSTER.md` after a fix showed a changed funnel. The
change was not mine** - stashing the edit and re-running produced the SAME new
output from the OLD code. The committed doc had been stale for **7 commits to
its own generator.**

- **A single post-change run cannot separate your diff from drift already
  there** - and it reads exactly as though it can. Capture the baseline by
  RUNNING the old code, not by trusting the committed artifact.
- **A generated artifact older than its generator is stale, full stop.** No
  judgement about whether the change "should" have mattered.
- **The headline hides it.** The roster's 2-cell conclusion was unchanged;
  only intermediate rows were wrong. A stale artifact keeps the SHAPE of a
  measurement while being a memory.
- Prove output-preservation by **regeneration and diff**, not by arguing from
  a frequency measurement - though measure first, so you know what to expect.

**Mechanically enforced** by
`test_b1974_generated_artifact_is_not_older_than_its_generator` (compares
commit timestamps; re-runs nothing, because regenerating reads 4.9M rows).

## A GATE CAN BE RIGHT AND NAME THE WRONG CAUSE (B1973 - L606, CHECKLIST #275)

**The gate said a row carried NO reason. It carried one.** My first words were
"the gate is misfiring" - it was not. The row was missing its terminating `|`,
so the extractor found no right delimiter and reported *no reason*.

- **When a gate fires on work you believe is correct, the reading order is:
  reproduce, then locate, then judge.** "The gate is wrong" is a conclusion,
  not an opening.
- **A gate that misnames its cause spends its own credibility** - the next
  true fire reads as the same false alarm.
- **The real defect was underneath**: the pattern stopped at the first `**`, so
  a reason that emphasised early was truncated and failed a length test.
  **Same reason, opposite verdict, decided by emphasis position.**
- **`#275` three times in one file in three batches.** Every regex reading a
  formatted document is a candidate - each was written by someone who could
  see the formatting they had in mind.
- **Two writers for one artifact, one of them lossy**: 5 malformed rows all
  came from the Python path, none from the heredoc path.

**Mechanically enforced** by `test_b1973_reason_verdict_is_invariant_to_emphasis`
and `test_b1973_every_ticket_row_closes_its_cell`.

## A TICKET NAMES A SITE; THE CLASS SPANS FILES (B1972 - L605, CHECKLIST #201)

**`S6-B1825c` named one line. The file had three. The codebase had 28 across
11 files** - including `backtest/results/writer.py` and
`build_phase_1b_roster.py`, which produces the owner-facing roster.

- **`x or default` cannot tell "no value" from "the value 0".** Two opposite
  failures: `sharpe or 0.0` reports an UNMEASURABLE Sharpe as a MEASURED zero;
  `sharpe or -9` ranks a Sharpe of EXACTLY 0.0 worst, so **the exit that broke
  even loses to every exit that lost money.**
- **Work the CLASS, not the ticket's wording.** A copy-pasted pattern spreads
  by FILE; the ticket was written inside one, and the class is not.
- **0 live instances is not "no bug".** A latent trap is the one that fires on
  data nobody has seen yet - a cube on a new universe is exactly that.
- **Strip docstrings before counting.** The naive sweep returned 40, including
  `Returns 1.0 or 1.5.` from prose; `source_text.code_only` cut it to 25.

**Mechanically enforced** by `test_b1972_zero_is_a_value_not_an_absence`, which
asserts the ORDERING (0.0 outranks a loser; absent still sorts last) rather
than describing it.

## A CITED RULE MAY NOT EXIST - CHECK THE ADDRESS (B1971 - L604, CHECKLIST #201)

**Seven CHECKLIST items are cited 94 times across LEARNINGS, the queue, this
skill and the gate script, and not one is defined:** `#187`-`#192` and `#237`.
The turn gate prints `RETROACTIVE SWEEP MISSING (B1757 / #237)` every turn -
and the sweep it demanded is what found `#237` does not exist.

- **A citation is a claim with an ADDRESS**, and the address is checkable
  independently of the claim (L595). Citing it is not the rule running (`#235`).
- **B1945 built this for L-numbers and stopped.** The CHECKLIST sibling was
  three lines away. Ask what OTHER namespace has the same defect.
- **Measure the measuring tool first.** My extractor read only `### #N` and
  reported 30 contiguous missing items, because `#185` is `**#185 ...**` bold
  inline - the `#275` formatting defect, inside the audit of it.
- **A contiguous run of missing items is a measurement smell**, not a finding.

**Mechanically enforced** by `test_b1971_no_new_dangling_checklist_citation`
(shrink-only ratchet + `#279` reverse check + a run-length guard against the
extractor defect that produced the first wrong answer).

## WHAT A PARSER REJECTS IS THE SET NOBODY AUDITS (B1969 - L603, CHECKLIST #275/#279)

**The queue's row regex required the ticket id to be BOLD.** `queue_state.py`
and every other reader agreed on that - **and 48 real tickets sit in an older
schema with an unbolded id, so nothing has ever counted them.** Every total
reported from that counter excluded them silently; the true population is
**1,245, not 1,197**, and those rows have no state column, so their OPEN-ness is
**UNKNOWN, not zero.**

- **A reject pile is invisible by construction.** A non-matching row produces
  no row, no error and no count - it produces a total that looks complete.
- **Consistency across readers made it WORSE.** All five agreed, so no
  cross-check could disagree, and the agreement read as corroboration.
- **Ask what a parser DROPS, not only what it takes** (`#279`, both
  directions). Never let a gate depend on formatting (`#275`).
- **Disclose, do not admit.** Widening the regex would INVENT a state those
  rows do not have. `unparsed()` names all 48 under a SCOPE line.

**And when you fix it, sweep the CLASS - the site you were chasing is rarely
the worst one (B1970).** B1969 fixed the one gate whose false positive was in
front of me; the `#237` sweep then found **the row COLLECTOR had the same bold
requirement** - and every row-reading gate draws its input from it, so dropping
the asterisks bypassed the whole row-gate layer at once. **Fixing the site you
happened to be chasing is availability, not a sweep.**

- Sweep by SEARCH (`grep -nF '\*\*'` found all 5 sites), never by recall.
- Fix the FEEDER before the consumers - a defect in the collector is every
  downstream gate's defect simultaneously.
- **A site deliberately left unchanged gets a comment AND a pin** - an
  undocumented survivor of a class sweep is indistinguishable from one that
  was missed. (Extends `#279`, which requires both directions for exclusion
  REGISTERS, to the survivors of a code sweep. Named search: the phrase has
  one occurrence in LEARNINGS - L603's own B1970 amendment - so this rule is
  new there, not duplicated.)

**Mechanically enforced** by `queue_state.unparsed()` and the bold-independent
own-id scrub, pinned by `test_b1969_gate_does_not_require_bold`,
`test_b1969_counter_discloses_what_it_cannot_parse`,
`test_b1970_row_collector_does_not_require_bold` and
`test_b1970_vocabulary_scan_stays_bold_on_purpose` (the pinned survivor).

## AN EVIDENCE VOCABULARY'S MISSING KIND IS INVISIBLE (B1968 - L602, CHECKLIST #162)

**Two lists of *what counts as proof* were each missing an obvious kind, and
each was found only when the gate refused CORRECT work.** `COUNT_PROOF` omitted
`queue_state` - the canonical counter, which the already-listed
`audit_ticket_staleness` imports. `MEMBER_EVIDENCE` omitted gate names, so a row
naming eight `scan_*` members failed the rule it satisfied.

- **Neither ever failed a test.** A missing kind produces no error - it produces
  **a turn that did the right thing and was told it did not.**
- **The cheap response is to reach for a token the list accepts** rather than
  the tool that answers the question. B1722's bypass, via a false NEGATIVE.
- **The fix is not a longer list.** Where the recognised thing has an OPEN set
  of kinds, **test the STRUCTURE** - two or more distinct identifiers IS an
  enumeration, and the test need not know the type.
- **9 evidence vocabularies exist here; 2 have been bitten.**

**Mechanically enforced** by the structural enumeration test in
`scan_count_without_members`, pinned by
`test_b1969_member_detection_is_structural`.

## A COUNT IS NOT A SET (B1965 - L601, CHECKLIST #280)

**A row said *"3 ROWS: their batch changed code but added no durable
definition"* and named none of the 3.** Its partition was complete - 148 = 7 +
138 + 3 - and only the 7 promoted rows are identifiable, because promotion
changed their state. **MEASURED: 13 of 62 OPEN rows state a count; 7 name no
member.**

- **The row reads as actionable and is not.** The only thing to do with it is
  measure again, and L600 says that yields a different set under the same name.
- **An anonymous count is not WRONG, it is UNUSABLE.** Re-checking never
  recovers which 3.
- **Distinguish from a STALE count:** stale is wrong and re-deriving fixes it;
  anonymous is right and re-deriving replaces it.
- **Name a member id, or the query.** *46 of 60, per `queue_state`* is complete.

**Mechanically enforced** by `scan_count_without_members` on rows added this
turn.

## TWO NUMBERS FOR ONE NAME - DIFF THE DEFINITIONS, NOT THE ARITHMETIC (B1963 - L600, CHECKLIST #271)

**`#271` surfaced SIX times in one session and every instance had correct
arithmetic:** a row is not a ticket, a BATCH is not a ticket, a LIVE ticket is
not an OPEN one, a call SITE is not a mention, a row's STATE is not a ticket's,
and *"carrying a count"* meaning two different things - **98 of 105 against 88
of 106, both mine, one batch.**

- **The arithmetic is never the fault**, which is why the class survives
  `#256`'s re-derivation rule: re-running confirms BOTH numbers and resolves
  nothing. **Re-deriving is the right instinct aimed one level too low.**
- **A wrong sum is loud. A right sum over the wrong set passes every check there
  is**, and the only evidence is a second figure that disagrees.
- **When two figures for one quantity differ, ask which SET each counted** - read
  the two definitions side by side. It gets skipped because both arrive verified.
- **Prefer citing the set with its total** (`#260`).

**Mechanically enforced** by `scan_row_vs_ticket` and `#260`'s
`scan_partial_distribution`, which is what caught the sixth instance.

## THE GATES OVER YOUR OWN REPORTING ARE THE LEAST VERIFIED (B1954 - L599, CHECKLIST #226)

**Two consecutive conversions caught defects in what I WRITE, not in what the
code does.** One gate had been passing while the required block was absent -
**102 of 3,519 reports carried one, 2.9pct.** The next says my block's status is
FALSE: `ALWAYS-ON` is stale when the skill was auto-injected, and the honest
status is **FULLY LOADED (auto-injected)**.

- **A gate over CODE is exercised by every code change** - it fires, someone
  investigates, it gets fixed.
- **A gate over REPORTING is exercised every turn and independently checked by
  nobody**, because *its subject is the same text that would report its
  failure.*
- **A blind reporting gate produces exactly the transcript of a working one:**
  compliant-looking prose and no alarm.
- **So the layer asserting you are compliant has the least verification in the
  system.** Read those gates first.

**Mechanically enforced** by `scan_missing_skill_confirmation` and
`scan_false_skill_status`, both routed through `_response_text` with
`keep_code=True` and both carrying corpus incidents.

## A GATE READING THE WRONG WINDOW DOES NOT FAIL LOUDLY - IT PASSES (B1952 - L598, CHECKLIST #226)

**Routing one gate through `_response_text` made it fire on the very next
turn.** It had been reading a wider window, finding its marker somewhere in it,
and passing while the required block was absent. **MEASURED: 3,519 substantive
reports this session, 102 with a SKILLS INVOKED block - 2.9pct - against 1,134
with a CHECKLIST compliance statement.**

- **COMPLIANCE FAILURE against owner directive B1726**, whose own reason is the
  diagnosis: *silence cannot distinguish "not triggered" from "triggered and
  skipped".*
- **A gate reading too NARROW a window fires on compliant turns and gets fixed
  within a batch.** A gate reading too WIDE returns clean, and the only signal
  is an alarm that was never going to sound.
- **Whenever a check has a permissive direction, that is where the rot is** -
  L596's asymmetry, one level up, and the direction nobody is prompted to test.

**Mechanically enforced** by the `S6-B1783b` conversion backlog, pinned at 5 by
`count_text_readers`: each remaining raw reader is a gate whose window has
never been proven.

## AN ENUMERATION PATTERN ENCODES THE EXAMPLES IN FRONT OF YOU (B1950 - L597, CHECKLIST #162)

**Four times in one session a probe ran clean, returned a plausible number, and
enumerated the wrong set:** occurrences counted where the claim was about
functions (4 vs 2); a corpus dict omitted; `^### L` matched while the file also
uses `## L` (89 of 502 missed); gate escapes enumerated by one syntactic shape
(6 of at least 9, **missing three fixed in the two preceding batches**).

- **The tell is identical.** Each regex was written while reading one example,
  and it inherited every accident of that example.
- **Worse than an unmeasured guess** - it arrives with the authority of having
  been run, and **the quantity is right while only the POPULATION is short**, so
  nothing in the output says so.
- **Control from OUTSIDE the sample that produced the pattern:** name a member
  you know exists and did not look at, then assert the enumeration finds it.
- **Prefer a STRUCTURAL bound to a syntactic one** - the escapes were
  unenumerable by regex and perfectly bounded by *every text-reading gate*.

**Mechanically enforced** where it can be: `count_text_readers` is the single
definition both the measurement and the pin call (L593).

## THE ESCAPE IS THE SIDE THAT LETS A TURN THROUGH (B1948 - L596, CHECKLIST #226)

**A gate granted its exemption to a `PROSE-ONLY` shown as an EXAMPLE inside a
code fence.** B1738's convention - vocabulary in backticks is a MENTION, not a
USE - had been applied to every gate TRIGGER in the file and to **no gate's
ESCAPE.**

- **MEASURED across three escape vocabularies:** `PROSE-ONLY` fixed at B1947,
  `SYNTHETIC` already routed, **`record-of-fact` vulnerable** until B1948.
- **The asymmetry is not accidental.** A trigger that fires wrongly is LOUD - it
  blocks a turn and someone investigates. **An escape that clears wrongly is
  silent, and the turn simply proceeds.**
- **A trigger false positive costs a re-word. An escape false positive costs
  the rule.**

**Mechanically enforced** by `test_b1948_escape_markers_obey_mention_vs_use`,
which holds both gates' fixes in place.

## A CITATION IS A CLAIM WITH AN ADDRESS (B1945 - L595, CHECKLIST #201)

**`L611` does not exist.** I ran `grep -n` on LEARNINGS.md, read
`611:A finding only counts as...`, and recorded it as a lesson number. **The
text is at LINE 611, inside `L126`** - and the mis-citation reached ticket rows,
a `CHECKLIST #279` amendment, and a section of THIS FILE, loaded every turn.

- **`#201` asks a FIGURE to name its source. Nothing asked whether a named
  source EXISTS.** The address is checkable independently of the claim.
- **Nothing was decided on a false premise** - the rule was real and correctly
  applied. **The damage is that a reader following the citation finds nothing**,
  and that reader is most likely you, next session.
- **A label is not a record.** `L594` was cited in two ticket rows and a turn
  report before the entry was written.
- **Grep output carries line numbers that look like identifiers.** So do row
  indices, commit-position counters, and `enumerate` output.

**Mechanically enforced** by `test_b1945_no_new_dangling_learnings_citation`:
the dangling sets are frozen and shrink-only, scanned with code spans stripped
so a row DOCUMENTING a mis-citation can still name it.

## A FIRE-ONLY CORPUS NEVER PROVES A GATE CAN STAY QUIET (B1944 - L594, CHECKLIST #226)

**A gate demanded proof of a count and did not recognise `queue_state`, the
script that produces every count in these reports.** Nobody noticed because its
corpus was fire-only: one case, must-fire, nothing asserting a compliant turn
passes. **MEASURED: 20 of 41 gates are fire-only.**

- **A must-FIRE case proves the gate catches the defect. Only a must-QUIET case
  proves it does not punish the compliant turn.**
- **B1722 named the consequence for false POSITIVES - a gate that cries wolf
  gets bypassed. This is the mirror**, and it is harder to see: **a false
  negative looks like a working gate to everyone except the person doing it
  right**, whose cheapest response is to reach for whatever token the gate
  accepts.
- **A proof-vocabulary that omits the canonical tool teaches the workaround.**

**Mechanically enforced** by `FIRE_ONLY_LEGACY` in
`test_b1944_fire_only_corpus_is_a_shrinking_set` - frozen at 20, shrink-only,
and moved to 19 in the batch that created it.

## PIN THE CODE THAT MEASURED IT, NOT A FRESH IMPLEMENTATION (B1938 - L593, CHECKLIST #271)

**L592 says count the sites and pin the count. I did both and they disagreed:**
the measurement split on `def scan_` and counted FUNCTIONS (2); the pin used
`re.findall` and counted OCCURRENCES (4).

- **Both are correct counts of different things.** `#271`'s fourth face - a row
  is not a ticket, a batch is not a ticket, a LIVE ticket is not an OPEN one,
  **a call site is not a mention** - and I wrote B1929 about this class then did
  it again in a pin.
- **`#226`'s ONE PATTERN clause too:** two implementations of one count,
  minutes apart, diverging immediately. **The rewrite was the easy version, the
  one a regex reaches for.**
- **The pin is what survives.** The measurement scrolls away; the assertion runs
  forever. **A pin counting a different set than its claim passes while the
  claim rots.**
- **Put the measuring code IN the pin, or derive both from one function.**

## THE UNIT OF THE CHANGE WAS SMALLER THAN THE UNIT OF THE DEFECT (B1936 - L592, CHECKLIST #226)

**One edit wrote two files. `safe_write_py` - which parses before writing -
guarded one of them.** The other got a SyntaxError, stopped importing, and 8
tests failed at collection. The guard was already imported, used three lines
earlier.

- **Four instances this session, every one surfaced by a gate firing on
  legitimate work:** B1904 word-bounded both sides on evidence for one; B1905
  B1820 fixed the JSON and not the table rendering it; B1925 B1880's heredoc
  strip in one launch detector and not its sibling; B1936 the guard on one file
  of two.
- **Each fix was CORRECT where it landed.** Nothing in the act of fixing asks
  how many sites the fix governs.
- **Count the sites and PIN the count.** B1925's pin asserts its strip
  expression appears at least TWICE - that assertion is the remedy.
- **FIFTH INSTANCE, AT FULL PRICE (B2092 - L620):** B2043 grew a task payload
  to a 3-tuple, fixed the pool worker, pinned through the replay path - and
  BOTH non-pool consumers kept 2-tuple unpacks. The first run to traverse
  the sequential branch completed its entire 3-hour day loop and crashed at
  save with the cube unwritten. **A payload's arity is a contract with every
  consumer, and a pin through one path proves one path.** The durable form
  of count-and-pin here is STRUCTURAL: test_b2092 walks the AST and asserts
  the append arity equals EVERY for-unpack arity, so a future consumer
  inherits the check unwritten.

## AN EXEMPTION'S REASON IS A CLAIM ABOUT CODE (B1934 - L591, CHECKLIST #279)

**A gate-exemption register went 15 -> 6 in one session and NOT ONE removal was
because the work got done.** Every one was the register wrong about itself: 3
stale, 3 excused as *"no seam"* while drivable, 2 as *"undocumented trigger"*
while importable, 2 as unseamed **while a passing test in the same repo drove
them.**

- **`#279` says a register DECAYS. This one was never right.** The disproof of
  four of five reasons was **already committed** when each reason was written.
- **`require_each` proves an entry HAS a reason, never that the reason is
  TRUE** - and the two are indistinguishable in review.
- **Before writing "cannot be tested / no seam / not available", CALL IT.**
  `#222` applied to an exclusion instead of a threshold.
- **EXTENSION (B2072 - L619): "decision-gated" / "needs owner approval" is such
  a reason.** Verify the item against the approval-requiring classes
  (rule/threshold/parameter changes, paid runs, launches, strategy changes)
  before presenting it as blocked on the owner - an offline analysis on cached
  artifacts belongs to none of them, and B2067 halted a whole goal partly on
  that mislabel. JUDGMENT-ONLY: no scan classifies gatedness; anchored at
  `#279`'s L619 extension, durability via the anchor-doc citation freeze.

## A DOCSTRING IS DOCUMENTATION; THE MARKER LIST IS THE PROGRAM (B1931 - L590, CHECKLIST #222)

**Two gates needed corpus incidents. I read their docstrings, guessed
triggering text, neither fired - and I filed a ticket saying their trigger
vocabulary was undocumented.** It was importable the whole time; one `print()`
closed the question.

- **The guesses were not near misses.** *"COMPLETE and handles every shape"* for
  a gate matching *"cannot clear"*; third-person *"the gate failed"* for one
  requiring first-person acknowledgment - **a distinction that gate's own
  docstring states.**
- **COMPLIANCE FAILURE against `#222`**, written about a THRESHOLD and
  identical for a TRIGGER. L588's shape, two batches after L588.
- **The cost was the TICKET, not the guess.** A failed probe became a filed
  claim about the codebase that a later reader would take as established.
- **A non-firing probe is evidence about the PROBE until the trigger has been
  read.**

## AN OUTCOME DIFFERENCE IS NOT EVIDENCE ABOUT CONTENT (B1921 - L589, CHECKLIST #275)

**`EXIT=127 CUBE_ROWS=ABSENT` on one run, `EXIT=0` with 8,581 and 10,921 rows on
the next. That reads as a fix. `diff` on the two driver scripts returns TWO
LINES, both log paths** - same wrapper, and `nohup|setsid|disown|detach` appear
zero times in either. **The later run succeeded because nothing killed it.**

- **The mirror of the confound lesson, not a repeat.** There the cause was one
  of several changes; **here NOTHING changed and the difference was real
  anyway**, so the inference *something was fixed* had no candidate and would
  have been invented.
- **Two runs of the same script are two samples from an environment**, not a
  controlled comparison. Kills, memory pressure, other load - none of it
  appears in the outputs and all of it moves them.
- **An artifact difference licenses a claim about artifacts; an outcome
  difference licenses nothing until the inputs are diffed.** One command.

**Mechanically enforced** as a durability pin in
`test_b1914_l585_l586_rules_and_their_disposition_survive`; the attribution
judgment itself is not mechanisable.

## A CONTROL MUST TAKE THE SAME PATH AS THE CLAIM (B1918 - L588, CHECKLIST #276b)

**Before emptying a 26-entry grandfather list I ran `#226`: inject a synthetic
ungated section, confirm the classifier flags it. It passed. It proved
nothing.** The claim was *"the existing 26 are stale"*; the control asked *"can
it see a NEW one?"* - and the existing sections were classified by a path the
injected one never touched.

- **`#276b` is exactly this rule** and I did not reach for it, because it was
  written about an injection seam in a GATE and I was running a manual probe.
- **Second time in three batches.** L585 was a compliance failure against
  `#162`, which I had filed under RCA because the item was written after one.
- **A rule's ANCHOR is not its SCOPE.** The retroactive line records where an
  item came FROM and reads like where it APPLIES.
- **Say both paths out loud before trusting a control.** One sentence -
  *"the injected section is not in the literal; the existing ones are"* - would
  have shown it.

**Mechanically enforced** for the register half by the redundancy assertion in
`test_b1762_every_scan_gate_has_a_corpus_entry` and the both-direction
assertions in `test_b1860_skill_additions_are_gated`; the control-path half is
judgment.

## AN EXCLUSION REGISTER DECAYS IN THE SAFE-LOOKING DIRECTION (B1916 - L587, CHECKLIST #279)

**A gate-exemption dict carried three entries excused as "incident text not
preserved" while all three had incidents. The reverse check found them the
first time it ran.**

- **A stale exemption never fails anything.** The work runs, the tests pass,
  and the register claims a gap that already closed - **the recorded state
  drifts PESSIMISTIC while everything stays green**, which is why it survives.
- **Both assertions, always: nothing uncovered, AND nothing excused that no
  longer needs it.** The first half usually exists; the second usually does not.
- **The excuse can be wrong on the day it is written.** Two gates were excused
  as *"no seam"* and are PURE FUNCTIONS - the corpus could not EXPRESS a
  positional signature, and that limit was recorded as a property of the gates.
- **Same decay in `STRATEGIES_DISABLED_*`:** B1035 reversed two disablements
  after probes found the producers alive; B1494 reverted six more.

**Mechanically enforced** by the redundancy assertion in
`test_b1762_every_scan_gate_has_a_corpus_entry`.

## A METRIC THAT COUNTS THE WRONG THING ARRIVES PRE-ARMOURED (B1912 - L585, CHECKLIST #162)

**Deciding whether to add a rule to a gate, I measured "11 of 41 firings, 27pct"
and wrote it into the comment justifying the change. The real effect is four.**
My probe counted quote marks within a character WINDOW of the clause -
**proximity is not containment** - so it was closer to measuring "is this a
report" than "is this a quotation".

- **An unmeasured number can be challenged on sight. A number that was
  genuinely computed, from real data, by a script that ran clean, cannot.**
- **COMPLIANCE FAILURE against `#162`** - the counter-semantics trap. I had
  filed `#162` under RCA because it was written after one. **It is a
  MEASUREMENT rule, and a gate-design probe is a measurement.**
- **Name the quantity, then prove the probe computes THAT quantity** - ideally
  by making the change and re-measuring, the before/after discipline B1872 used
  and this batch skipped.

**PROSE-ONLY, and here is why no gate is possible.** This rule is a claim about
CORRESPONDENCE between a name and a computation. My probe ran clean, on real
data, and returned a number; what was wrong is that *"quote marks within 40
characters of the clause"* is not *"the clause is a quotation"* - a difference
only a reader who knows the intent can see. **No text scan evaluates whether a
computation means what its author called it**, and a presence-pin asserting
this section still exists would be enforcement theatre, which `#136` rejects.

**The gateable slice already exists and is `#201`** - a figure must name its
source - and it passed here, because the figure DID name its source. **That is
precisely the limit worth knowing: `#201` proves a number came from somewhere,
never that the somewhere measured the right thing.**

## A GATE WITH A CHILLING EFFECT ON THE RECORD IS WORSE THAN THE GAP IT CLOSES (B1912 - L586, CHECKLIST #136)

**An unsourced claim in `LEARNINGS.md` escaped the novelty gate, which reads the
response. The obvious fix - scan the newest L-entry - was built, and it fails on
that entry itself**, because an entry recording an incident must narrate the
wrong claim to correct it.

- **Every future lesson about a novelty miss would trip the same pin.** The
  cheapest response becomes wording around the gate, or not writing it.
- **This project's error-correction loop runs through that file.** A mechanism
  that taxes the loop it protects is a net negative even when the gap is real.
- **Before gating an artifact, ask what behaviour the gate makes cheapest. If
  the cheapest response is to write less down, do not ship it.**
- `#136` has a sibling: **an addition can fail not by being useless but by
  being COSTLY IN THE WRONG PLACE.**

## A CLAIM OF NOVELTY NEEDS THE SAME VERIFICATION AS A NUMBER (B1910 - L584, CHECKLIST #201)

**I reported a duplicate-exit collapse as an "undocumented third collapse"
because the code comment beside it names only the other two. LEARNINGS carries
it three times, at 100.0pct over n=7,319.** It never reached the owner because
I happened to grep first. **Nothing required that grep.**

- **"Not in the code comment" is not "not documented."** A local artifact's
  omission is evidence about that artifact, never about the corpus.
- **CORRECTED B1911: the RULE existed, the MECHANISM did not.** `CHECKLIST
  #26` covers it and **L520 says so**; **L126** is exact - *"a finding only
  counts as no prior art when ALL FOUR sources confirm absence"*. **I treated
  ONE source, a code comment, as sufficient.** COMPLIANCE FAILURE against
  `#26`, not a new class.
- **Check ALL the sources, not the nearest one.** `#201`/`#222`/`#256` are
  rules WITH gates; `#26` was a rule enforced by remembering it.
- **Name the search or say the prior art exists.** MEASURED on 5,098 real
  report texts: the gate fires on 0.7pct.
- **SEARCH THE CLASS, NOT THE CONSEQUENCE (B2135 / L635).** I searched whether a
  config set was contaminated (the data in front of me) and never whether the
  SHAPE had been recorded before (the corpus) - so I called two findings new
  while my own ticket cited `L558` for one and the other was a documented
  renderer behaving as designed. **The consequence search is about your data;
  only the CLASS search establishes novelty.** When prior art exists, the honest
  form is *"the instance is new, the class is known, see <entry>"* - and often
  the real novelty is SCOPE (a whole config set, not one field).
- **Build the retraction escape FROM THE START.** Self-reference has hit this
  file ~13 times, always by bolting it on after the gate blocked its own
  incident report.

## A FIGURE IN A CODE COMMENT IS AN ASSERTION, NOT A MEASUREMENT (B1908 - L583, CHECKLIST #201)

**I twice quoted a Spearman of -0.779/-0.865 as measured and used it to argue a
result was "the expected shape". It lives in a comment.** I never ran it. The
turn gate caught it - a COMPLIANCE FAILURE against `#201`, not a gap in it.

- **`#201` asks a figure to NAME its source. It does not ask whether that
  source is itself evidence.** `.py` is a valid source token, so naming the
  file clears the gate - MEASURED.
- **A `.py` is evidence for a READ claim** ("the constant is 1.0") **and not
  for an EXECUTED one** ("it measured 4.92 ms"). The gate cannot tell them
  apart, and which verbs separate them is a POLICY CALL, not a guess.
- **A number read from a comment is READ-class evidence that the comment says
  it.** Quote it as an assertion with its author, or re-measure it.
- **ASSERT THE ANCHOR BEFORE YOU REPLACE IT (B2128 / L627 addendum).** Every
  scripted edit asserts its anchor matches exactly once BEFORE writing. This is
  what makes a wrong anchor harmless: reconstructing a file's wording from
  memory instead of reading it is a substitution you will make, and the assert
  turns it into a failed edit at authoring time rather than a silent no-op or a
  mangled file. MEASURED in one session: 9 scripted edits, all asserted, one
  anchor wrong, zero bad edits shipped. Sibling of the `&&` chaining rule
  (B1993d) - both convert a silent wrong outcome into a loud stop.
- **EXTENSION (B2128 / L627) - NAME THE FILE YOU READ IT IN, NOT THE FILE THAT
  OUGHT TO HOLD IT.** Re-wording a figure to satisfy this very rule, I sourced
  it to the script that exists BECAUSE of the incident it describes; a grep of
  that file returns ZERO hits, and the figure actually came from a turn-gate
  message read minutes earlier. **Grep the named file for the figure before
  naming it** - an attribution is a claim with an address (L595), and
  plausibility is not evidence. Gate text, prior-turn blocks and your own
  earlier prose are sources that must be named as themselves.
- **A measurement on a SELECTED subset does not refute one on the population** -
  range restriction attenuates correlation; -0.382 on an is_sharpe-selected
  top-10 is consistent with -0.779 on all 300.

## A TRANSFORM ON AN ASSERTION'S HAYSTACK CAN TURN IT GREEN AND VACUOUS (B1906 - L582, CHECKLIST #226)

**A pin said a renderer must not print `float("nan")`. It fired on the COMMENT
explaining the fix** - ~11th instance of a gate matching its own documentation,
because a source-text grep cannot tell prose from code.

**The fix then had the worse bug.** The comment-stripper REBUILT the source as
`" ".join(tokens)`, so `_measured.fmt` became `_measured . fmt`.

- **A `not in` assertion whose haystack has been mangled PASSES** - silently,
  for the wrong reason. Every assertion built on that strip would have been
  vacuous and green.
- **Blank in place; never rebuild.** Overwrite dropped ranges with spaces so
  offsets, layout and dotted names stay byte-identical.
- **Pair every `not in` with an `in`** proving the haystack still holds what it
  should. That `#226` line is what caught this, one run after being written.

## A CONTAMINATED RESULT THAT LOOKS GOOD IS THE LEAST INFORMATIVE ONE (B2136 - L636, CHECKLIST #201)

**MEASURED: four config runs were ranked on the HOLDOUT. The two whose holdout numbers cleared
the noise floor (+0.607, +0.439) are the two whose honest in-sample numbers are worst (-0.140,
+0.259). 0 of 4 clear the floor once re-graded in-sample.**

- **Peeking is a BEST-CASE procedure** - it hands the search the answer sheet. A run that peeked
  and still FAILED is strong evidence there is nothing there, and nearly free. A run that peeked
  and WON has told you almost nothing, because winning is what peeking manufactures.
- **The instinct is to protect the winners and discard the failures. Reverse it.** Say which
  results are the contaminated ones OUT LOUD before re-deriving, or you will keep whichever
  version flatters them.
- **Re-grading fixes the ARTIFACT, not the leak.** The holdout stays spent for that object until
  the boundary is re-cut; re-derived rankings are CANDIDATES, never verdicts.
- **The renderer that exposes a contamination can carry it.** Ours ranked `best` on the holdout
  key even for honestly-graded inputs. Apply the L558 test to VIEWS, not only artifacts: could a
  reader tell this output from one the bug produced?

## A RANKING IS A CLAIM ABOUT ORDER, AND ONE ROW CAN INVERT IT (B1902 - L581, CHECKLIST #201)

**MEASURED: a harvester ranked 192 strategies by mean pnl and put one first at
+944.752pct. THREE rows of 547 produce that number** - SBNY at $0.001 entry
after the bank failed. That cell's median is +0.399pct, and the whole top-five
was artifact.

- **0.083pct of rows carried `|pnl_pct| > 100` and 141 strategies touched one.**
  Tiny contamination, total distortion - an OUTLIER signature, not a bias.
- **A mean answers "what happened on average"; a ranking answers "which is
  best".** Order is discontinuous, so one value moves a strategy from last to
  first where a mean would only shift.
- **Never rank on a statistic one observation can dominate, and show the robust
  statistic beside the fragile one.**

## A MISSING MEASUREMENT AND A MEASURED ZERO ARE DIFFERENT FACTS (B1899 - L580, CHECKLIST #201)

**MEASURED: a renderer crashed on `None`, I fixed it to print `n/a` and wrote
the rule down - and broke it in a DIFFERENT renderer one batch later**, printing
`0` for a value the artifact does not record.

- **The crash was the lucky one.** It stopped. **The `0` rendered cleanly into a
  table meant for quoting**, and was caught only because I ran the renderer on
  real artifacts rather than a fixture.
- **`None` = not measured, renders `-`. A real `0` renders `0`** - a measured
  zero IS evidence and must not hide behind the same token as an absence.
- **A rule in a comment carries nothing** (L536). The carrier is
  `scripts/measured.py`.

## A CORPUS WRITTEN FOR HUMANS BREAKS TOOLS OVER IT (B1895 - L579, CHECKLIST #226)

**MEASURED: four attempts to index the ledger, three failed, each returning a
PLAUSIBLE NUMBER** - 530 "contradictions" that were the stamp every row
carries, then 146 from a second stamp layer, then `GATES`/`OWNER`/`LEDGER`
matched as identifiers because the ledger is written in emphatic ALL-CAPS.

- **Both defeats are self-inflicted and both are good choices for a reader.**
  The provenance stamp and the bold-caps emphasis each help a human and each
  break a tool.
- **A probe returning ZERO is obviously broken. A probe returning a NUMBER is
  only obviously broken if you check what it counted.**
- **Demand structure the prose cannot fake** - an identifier must carry an
  underscore or a `.py`; emphasis cannot satisfy that.
- **Record failed probes where the next attempt starts** -
  `scripts/queue_crossref.py` carries all three in its docstring.

## A GUARD'S PROMISE IS ONLY AS WIDE AS ITS DETECTOR (B1893 - L578, CHECKLIST #226)

**MEASURED: a pin whose docstring says the set "cannot GROW" tested two of the
three ways a gate reads assistant text.** Two gates using the third sat outside
it for batches, and a new gate in that style would have grown the set silently.

- **Not a broken gate.** L561 is a gate gone SILENT; this one works perfectly on
  the shapes it tests. **The defect is the gap between docstring and coverage**,
  and only the docstring is load-bearing for a reader.
- **The tell was two of my own tickets disagreeing** - one said 13, one said 14.
  **A disagreement between your own rows is free evidence one is wrong**, and it
  went unread because each was written in a different batch.
- **When a guard's docstring makes a universal claim, enumerate the ways the
  thing it guards can occur and check the detector covers each.**

## A TICKET'S NUMBERS ARE AS PERISHABLE AS A RESPONSE'S (B1890 - L577, CHECKLIST #256)

**MEASURED: a row carried "14 gates with no seam" for batches; the world said
9.** It was correct when written and went stale while staying open.

- **`#256` covers a figure you REPEAT.** It has no reach into a figure sitting
  in a ticket, which is read as a PREMISE - **and a premise is what nobody
  re-derives.** 100 of 109 live tickets carry a number.
- **Re-derive before working a row**, not after. Mechanism:
  `python scripts/audit_ticket_staleness.py`, now 9 claim shapes.
- **A prober that cannot measure must print `n/a`, never a placeholder digit** -
  a fake number looks like a measurement, which is the failure it exists to catch.

## VERIFYING A MONITOR'S PLUMBING IS NOT VERIFYING ITS PERCEPTION (B1886 - L576, mechanically enforced)

**MEASURED: a launch-turn gate confirmed the cron's state-file path matched the
runner's output, and passed. The monitor was blind anyway** - its grep used
`/200` while the screener reports against the PIT-ACTIVE 185, so it would have
said "no fires" every 11 minutes on a run firing on 29 of 29 screen-days.

- **The gate asked "is it pointed at the right file?"** - checkable, cheap, and
  not the question whose failure was live.
- **A monitor's wrong grep is SCHEDULED.** It reports the same false silence
  every interval, and **repetition reads as corroboration when the mechanism is
  shared.**
- **When a monitor searches, its pattern needs a POSITIVE CONTROL** - a real
  line it must match - before the monitor is trusted to report silence.
  Enforced by `scan_monitor_pattern_unverified`; helper is `grep_control.py`.

## A LITERAL'S VALUE DEPENDS ON THE PATH IT TRAVELLED (B1884 - L575, CHECKLIST #226)

**MEASURED: I verified a fixture was invalid Python in a bash heredoc, embedded
it in a `pytest.raises` arm, and the arm failed DID NOT RAISE** - the literal,
as it exists in the file, parses.

- **The two strings looked identical and were not.** Heredoc copy: bash -> tool
  layer -> Python. File copy: disk -> parser. `\\` collapses on one and
  survives on the other.
- **Read the literal back out of the TARGET file with `ast`.** That settled in
  one command what two heredoc probes got wrong.
- **This mangling corrupted a BELIEF, not a file** - no file check catches it,
  because the file was written exactly as intended.
- **When a fixture's VALUE carries the meaning of a test, verify it where it
  lives, not where you drafted it.**

## BEING RIGHT ABOUT THE CONTENT IS NOT BEING RIGHT ABOUT THE CLAIM (B1882 - L574, CHECKLIST #226)

**MEASURED: a gate blocked three consecutive turns. I checked the match, found
genuine executed code, declared the gate correct - and the command had run
2026-05-15, three months earlier, at transcript line 471 of 130,622.**

- **The gate's claim was "THIS TURN ran X", not "X exists somewhere."** I
  verified the half that was true.
- **Root cause was the shared helper:** `_executed_text` said *this turn* in its
  docstring and iterated the whole session. **130,655 entries in the file, 46 in
  the turn.**
- **The cheap unasked question was "WHICH LINE?"** One grep ended a three-turn
  block.
- **When a gate fires on something you believe correct, verify the SCOPE of its
  claim, not only the content of its match.**

## A RUN ON THE WRONG INTERPRETER DOES NOT CRASH (B1878 - L573, mechanically enforced)

**MEASURED: I told the owner, as CAUSALLY CONFIRMED, that demand pruning
silently zeroed runs. It does not** - venv python gives 10 trades with pruning
ON and 10 with it OFF. **The zero-fire arm had run through
`subprocess.run(["python", ...])`, which resolves to the SYSTEM interpreter.**

- **The wrong interpreter does not raise.** It imports the engine, runs every
  day, writes `engine_state.json`, exits 0, and produces an empty cube. Every
  liveness signal is green (L566).
- **A one-variable test is not "I changed one flag" - it is "one thing
  differs", and THE LAUNCH PATH IS A THING.** My two arms used different launch
  mechanisms and I never asked whether that could reach the result.
- **A launch names its interpreter.** `sys.executable`, never a bare `python`.
  Enforced by `scan_bare_python_launch`.

## A "STRICTER" RULE IS A DIFFERENT RULE FOR MEMBERS IT WAS NOT ABOUT (B1873 - L572, CHECKLIST #246)

**MEASURED: fixing 3 markers that matched their own negation, I word-bounded
whole marker lists. That is strictly stricter for a PLAIN WORD and WRONG for
`output_`** - `_` is a word character, and the marker exists to match
`output_cfg1`.

- **The lists are heterogeneous by construction** - plain words, prefixes,
  extensions and phrases in one tuple. **A uniform change to a heterogeneous
  collection is several different changes**, and only one had evidence.
- **Opposite of L567 and equally costly.** L567 is under-examining; this is
  over-applying a fix past the members it was derived from. Both read as
  diligence.
- **Before transforming a collection, ask whether its members are the same KIND
  of thing.** If not, each change needs its own evidence.

## AN AUDIT SCOPED TO OPEN ROWS CANNOT FIND A FALSE CLAIM IN A CLOSED ONE (B1871 - L571)

**MEASURED: a row marked EXECUTED claims the migration tagged every inferred
class. At the migration commit itself the tag appears ONCE - in the prose
describing it.** The tags were never written. **Two end-to-end passes ran after
that row and neither found it; both were scoped to rows still OPEN.**

- **A claim in an OPEN row is a promise. A claim in a CLOSED row is
  load-bearing** - other work is already built on it.
- **The cost of a false claim rises when it is marked done, and that is exactly
  when it stops being audited.**
- **When a verification pass enumerates its population, say whether CLOSED rows
  are in it** - and if they are not, say so out loud.
- **JUDGMENT-ONLY for detection** (arbitrary prose claims across 800 closed
  rows are not a scan); durability pinned by `test_b1871_false_claim_stays_flagged`.

## AUTHORING A RULE FEELS LIKE INSTALLING IT (B1869 - L570, CHECKLIST #226/#244)

**MEASURED: twice in one session I broke a rule I had just written or cited.**
I cited `S6-B1762f` - *require_each existed and I did not use it* - in the batch
where I did not use `require_each`. I wrote L567 - *a ticket names one guard;
the expression has two* - and two batches later fixed one delivery form and
left its sibling.

- **The rule was not forgotten. It was recalled, quoted, and not applied**, so
  "re-read the lesson" is not the remedy.
- **The gate caught both; I caught neither** - in a session where I was writing
  the rules in question.
- **When a turn CITES a rule, treat the citation as a checklist item, not as
  evidence of compliance.** Apply it to the edit in front of you before quoting
  it about the edit behind you.
- **JUDGMENT-ONLY for detection** (no scan can read internalisation); the
  durability half is pinned by `test_b1869_authored_then_violated_ledger`.

## A TEXT-SCANNING GATE TRIPS ON ITS OWN PROOF (B1867 - L569, CHECKLIST #246 ext)

**MEASURED: `scan_bulk_process_kill` blocked the very turn that shipped it**, on
my own probe `cmds=["Get-Process python | Stop-Process -Force"]` inside a
heredoc - while the only process actually killed went by verified PID.

- **Structural, not bad luck.** A gate that scans executed text is proven by
  fixtures containing exactly what it detects, written through the stream it
  reads. **Instance 10 of the self-reference family.**
- **Give it a fixture-exclusion in the SAME batch**, or it blocks its author
  first. A heredoc body is data handed to an interpreter.
- **Assert the opposite arm too:** a real kill BESIDE a heredoc must still
  fire, or you have traded a false positive for a false negative.

## AN EMPTY SEARCH RESULT PROVES NOTHING UNTIL THE PATTERN IS PROVEN (B1862 - L568, CHECKLIST #226 ext)

**MEASURED: I watched a 200-ticker run for fires with `[0-9]+/200 passed`, got
nothing, and reported "still in warmup" TWICE.** The denominator is the
PIT-ACTIVE **185**, not the file's 200 - the run was firing on all 29
screen-days, **and the monitor carried the same pattern**, so it would have
reported "no fires" unattended and confirmed a launch blocker backwards.

- **An empty result is indistinguishable from a wrong pattern.** Before
  concluding absence, make the pattern match a KNOWN POSITIVE from the real data.
- **Mechanism: `scripts/grep_control.py`** - `search_with_control` RAISES
  instead of returning `[]` when the pattern fails its control.
- **What caught it was reading a raw log line**, not the derived view. A grep is
  a claim about the data's shape.

## A TICKET NAMES ONE GUARD; THE EXPRESSION HAS TWO (B1859 - L567, CHECKLIST #226 ext)

**MEASURED: a ticket reported one defect in `(?<!\d)[.;](?!\d)`. I fixed the
guard it named and shipped a regex whose OTHER guard was also broken, and
older** - it refused to split a sentence ending in a decimal, so a figure
inherited a source from the next sentence. Deleting it fixed both.

- **A ticket describes the symptom someone NOTICED.** A compound predicate has
  as many failure modes as it has terms.
- **Evaluate every term against a case table BEFORE editing, and put the table
  in the commit.** Mine showed the first fix still failing 1 of 6.
- **Not a compliance failure** - the `#226` fail arm caught it. The lesson is
  about where to look, not about a skipped step.

## EVERY CHECK PASSED AND THE RUN DID NOTHING (B1854 - L566, CHECKLIST #223)

**MEASURED: a three-arm probe returned 890.7 / 890.6 / 890.6 seconds and the
verdict NEUTRAL - the answer I expected. All three arms did no work**
(`0/10 passed` on 751 days, `trades=0`, 1 output file instead of 74).

- **The validation validated the wrong layer.** Exit codes, windows,
  `universe_size`, checkpoints, CPU, working set - **all true, none of them asks
  whether the run DID anything.**
- **The tell was in the numbers first:** three different workloads within 0.1s,
  and a fitted model saying neither tickers nor years matter. **An idle engine
  produces very clean arithmetic.**
- **Naming a gate N/A switches it off.** `#223` step 1 is `cube_sanity` - the
  one check that opens the cube. I waived it for all four probe dirs with a
  reason I still think correct. **When you waive a gate, name what the waiver
  stops detecting.**

## CHECKING THE VALUE IS NOT READING THE CODE (B1852 - L565, CHECKLIST #222)

**MEASURED: I recommended raising `DEMAND_PRUNING_WARMUP` from a runbook table
without opening the module. The table was CORRECT** - the default really is 25.
**Reading it overturned the recommendation anyway:** the module records that
warmup now counts DISTINCT SIM-DAYS, so every arm sharing a start date observed
the same 25 warmup days - and warmup length therefore cannot explain the split I
was proposing to fix with it.

- **A constant you have not read carries its neighbourhood unread too** - the
  comment above it, the bug already fixed in it, the units it counts.
- **The number can be accurate while the recommendation resting on it is
  nonsense**, and verifying the number would not catch that.
- `#222`'s recorded rationale is doc-drift; **this is the stronger form**, and
  the existing `scan_uninspected_constant` caught it with no new gate needed.

## A MECHANICAL DIRECTIVE TAKES DO-IT OR ASK, NOT AN EXPLANATION (B1850 - L564, #185)

**MEASURED: four long jobs launched, zero monitors armed - and I did not forget.
I wrote down why it was unnecessary**, under a DISCLOSED heading, and the
reasoning was defensible. **The memory says mechanical, not "remember to
report":** a mechanical rule does not route through my judgement about whether
today is an exception.

- **Disclosing an exemption you granted yourself is still an exemption you
  granted yourself.** Writing it in the open makes it feel audited.
- **`.stop_exempt` is legitimate and this is not** - the difference is whether
  the escape exists in the system or only in my paragraph.
- **What it cost:** the run I judged not worth monitoring returned a clean
  NEUTRAL verdict from three arms that did no work. An hourly report naming
  `trades_so_far=0` would have caught it at the first fire.

## THE PROOF IS ITSELF A PROBE (B1840 - L562, CHECKLIST #226 ext)

**MEASURED: the fail-arm proof for the control-character gate was defeated by the control-character
bug it was testing.** The probe went through a heredoc, the escape collapsed, the file landed with a
real `0x08`, **the gate's OLD arm caught it and printed `1 failed`** - proof-shaped, with both new
arms unexercised.

- **Assert the probe's own inputs.** Fourth instance of L556; each of the four returned a flattering
  answer.
- **Assert WHICH message fires, not the exit status.** `1 failed` named a different arm's line.
- **Every fail arm needs a must-NOT-fire case**, or a gate that fires on everything looks correct.
- **A gate that raises while building its offender message is silent on exactly its target case** -
  `n.lineno` on an `ast.Module`. Clean input never reaches that line, so the repo passes.

## A SILENT GATE AND A CORRECT ONE ARE THE SAME OBSERVATION (B1836 - L561, CHECKLIST #226 ext)

**MEASURED while replacing `#201`'s mechanism: three bugs, none visible on reading, two of which
made the gate SILENT** - a clause splitter that split `169.347` into `169` and `347`, and a decimal
matcher that refused a sentence-final number so the gate went quiet on its own incident's shape.

- **That is why the fail arm is not optional.** A gate broken into silence produces exactly the
  output of a working one. **Only running the case it should catch separates them.**
- **ONE PATTERN, ONE DEFINITION.** The third bug: the regex lived at two sites and I fixed one.
  **A duplicated pattern is a divergence waiting for someone to fix half of it** - three instances
  now (B1812, B1798, B1832).

## PROVE-IT-CAN-FAIL RULE (B1706 - L501, CHECKLIST #226, PROVEN)

**EXTENSION (B1802 - L551): WHEN THE NEGATIVE ARM FAILS, SUSPECT YOUR MODEL FIRST.**

**MEASURED: I read the CALLER and not the function.** The grader does `is_m = rc.in_sample(sub)`, so
I built the bypass arm against the call site - but `select_exit` slices `in_sample()` itself and its
docstring says so. **Bypassing the caller's filter bypassed nothing, and the arm failed.**

- **Only the negative arm makes you NAME where the mechanism is.** You cannot break what you cannot
  locate, so it tests your MODEL as much as the code. The positive arms are identical either way.
- **Re-read the function before changing the test.** Weakening an arm until it passes leaves
  something indistinguishable from never having written one - L550's instinct, new location.
- **A failing arm is a finding, not an obstacle.** This one produced a correction to an open ticket:
  `S6-B1705c`'s *"there is no enforcement"* is true of the ranking and false of the exit choice.

**A gate observed only PASSING has not been tested. It has been run.**

**AND ITS PRECONDITION BINDS THE OPERATION, NOT THE MODULE (B2132 / L632).** My drift gate
refused a launch whenever engine paths were dirty - correct for a real run, and it made the
test suite unrunnable during development, because dirty is what development LOOKS like. I had
scoped it to the SCRIPT, so every path inherited a precondition only one path needs. **Before
shipping a gate, enumerate the paths through its module and ask which the precondition is
actually about; a test seam is by definition not the guarded operation.** The tell was WHICH
tests broke - two unrelated launcher tests, never the gate's own - so **run the FULL suite
before believing a new gate is scoped right.**

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

## COUNT ENTITIES, NOT ROWS - AND NEVER WRITE A DEFAULT BRANCH (B1795 - L545/L546, #271/#272)

**MEASURED: `EXECUTION_QUEUE.md` is an APPEND LOG - 823 rows, 721 tickets.** Closing a ticket appends
a row instead of editing it, so 81 ids are duplicated and **57 are EXECUTED AND OPEN at once.** Every
queue count quoted this session was row-level while named ticket-level.

- **One reader.** `scripts/queue_state.py`, last row wins, per distinct id. `scan_row_vs_ticket`
  fires on a class count whose method names no dedup.
- **Assert the invariant the scheme rests on.** Last-row-wins holds only while no terminal row is
  followed by a non-terminal one. The pin test checks it; if it fails, EVERY derived count is wrong.
- **Exclusive labels are not exclusive assignment.** The six classes were made non-overlapping as
  vocabulary while 69 tickets sat in two of them - and the vocabulary fix was reported as the fix.
- **A classifier over a population has NO `else`.** An `else` promoted 140 tickets when 36 had been
  classified; 104 unread tickets were marked EXECUTED **by the script enforcing #270.** Name every
  member in exactly one list, assert `named == population`, and REFUSE TO WRITE on mismatch.
- **Where it happened matters.** Not in the analysis - in the ENFORCEMENT, for the second time
  (`S6-B1780d` is the first, and was already open when the `else` was written).

## NAMING AN ENFORCER IS NOT BEING ENFORCED - CHECK IT COVERS THE SCOPE (B1796 - L547, #273)

**`#242` requires every rule added here to NAME the function or test that enforces it. Nothing
checked that the named mechanism COVERS the scope the rule declares.**

**MEASURED: `#270` declares *"tickets, documents, or CODE"* and its gate fired on 2 of 10 realistic
verdict sentences - both tickets, ZERO of eight for code and documents.** The bullet claiming
enforcement was written in the same turn as the gate that did not deliver it.

- **When a rule names N domains, its pin test carries a case per domain.** Not one example - one per
  declared domain, so the coverage claim is true by test rather than by assertion.
- **And fix it at the right rung** - see `#239`'s three-rung table. The domains failed here because
  the matcher enumerated one dialect; **matching the SHAPE covered all three at once.**
- **This is any-vs-each one level up.** `#234` asks whether every MEMBER of a rule was handled;
  this asks whether every DOMAIN of a rule is reachable by its enforcer.
- **The prose is the claim.** Writing *"Enforced by X"* is a factual assertion about X's behaviour
  and is subject to the Truth Standard like any other - **verify it or qualify it.**
- **Retroactive (`#136`):** `#270` (this instance); `#242` itself, which checks naming and not
  coverage; `#240`, where *"every gate carries a corpus entry"* was asserted while 17 of 25 had none.

## NO HALF MEASURES - READ IT END TO END (B1794 - L544, CHECKLIST #270)

**EXTENSION (B1807 - L554): truncation counts only where it is applied to the SOURCE.** Everything
after a `|` has already seen the whole input - `pytest -q | tail -3` trims OUTPUT, it does not
sample. **Third false positive from this gate; fix it rather than learn to ignore it. The
*"end to end"* escape is an ASSERTION, and using it to silence a false positive makes it a lie the
next time it matters.**

**OWNER DIRECTIVE: analyze anything - tickets, documents, or CODE - end to end. No half measures.**

**MEASURED: I read 20 of 141 rows and projected. Sample 10pct complete, population 72pct - wrong
SEVEN-FOLD.** The set was SORTED: planning rows first, measurement records after. **A contiguous
slice of a sorted list is not a sample.**

- **Read every member before stating a verdict over the set.** Enforced by `scan_partial_read`
  **across all three declared domains** - it fires on a population verdict beside truncation
  markers (`head -N`, `[:300]`, "batch 1 of") in the ticket dialect (*"all 138 are complete"*),
  the code dialect (*"no other call sites"*, *"all 47 gates have a seam"*) and the document
  dialect (*"no document outside archive/ still references it"*). **B1796: it originally covered
  only tickets - 2 of 10 cases, 0 of 8 for code and documents - while this bullet already claimed
  it was enforced.** One case per domain is pinned by
  `test_b1796_partial_read_covers_every_declared_domain`.
- **A forward-looking clause is an intention, not a verdict**, and the check is clause-scoped:
  planning in one clause does not excuse concluding in the next.
- **Say "end to end" only when it is true.** The gate treats that phrase as the assertion it is.
- **The contamination is not local.** The ground-truth corpus built from those 20 rows, and used to
  score four classifiers, was right about each row and wrong about the population.
- **Careful work on a subset reads exactly like careful work.** Every one of the 20 verdicts was
  correct. **The error was in generalising from a slice**, which care inside the slice cannot see.

## SCORE ON THE MINORITY CLASS, NOT ON ACCURACY (B1793 - L543, CHECKLIST #269)

**MEASURED: 17/20 = 85pct overall, 0/3 = 0pct on the classes that matter.** The classifier defaults
to the majority class, so **a constant function scores 85pct on this sample.**

- **85pct was the first number printed and the one I would have reported.** What exposed it was the
  SHAPE of the errors - three disagreements, every one a non-OPEN row.
- **Keep hand-read verdicts as labelled ground truth** with the phrase that decided each. **A
  classifier is unproven until it reproduces verdicts a human reached by reading** - `#240`'s corpus
  pattern moved from gates to classifiers.
- **Record a metric you cannot meet; do not enforce it.** A floor the classifier cannot reach
  invites loosening the labels to pass.

## A CLASSIFIER INHERITS YOUR MODEL OF THE DATA (B1792 - L542, CHECKLIST #268)

**MEASURED: hand-reading 20 rows gave 2 complete, 17 open work, 1 misclassified.** Four classifiers
had promoted 17-57 of that same population.

- **They failed on the PREMISE, not the pattern.** I had framed these as *analysis whose artifact
  was documentation*, so each hunted for a recorded result. **They are tasks with verbs** - "Run
  first", "Build the harvester", "Owner approval required" - written down and never started.
- **Hand-read a sample and state what the population IS before writing a classifier.** A wrong model
  of the data cannot be patched by refining the pattern.
- **A completed analysis row has a shape:** a finding plus its consequence, no verb pointing
  forward. **A definitive NEGATIVE is a completed result.**
- **Hand-reading finds what no checker looks for** - one row stated its own blocker and had sat as
  OPEN; every completeness checker was asking a different question.

**Mechanically enforced** by the kept hand-read corpus in scripts/hand_verified_rows.py (LABELS + RANDOM_SAMPLE_LABELS with reproduce_random_sample, B2022): a classifier is scored against verdicts a human reached by reading, never against its author's expectations.

## STOP AT THE SECOND FAILED HAND-CHECK (B1791 - L541, CHECKLIST #267)

**MEASURED: four classifiers, hand-checked samples failing 3-of-4 then 3-of-5.** The rule *two
failed attempts means the diagnosis is wrong* applied two attempts before I stopped.

- **The wrong assumption was that "nothing pending" is keyword-detectable.** The distinction is
  grammatical MOOD - *"I measured X"* vs *"measure X"* share every content word.
- **On the second failed hand-check, STOP and present the options** - hand-verify in batches,
  accept the population as OPEN, or have the owner accept a sampled error rate. **A fifth regex is
  momentum, not a plan.**
- **A verifier must strip its predecessor's annotations.** Rows now lead with ~430 characters of
  prior verdicts; the first classifier scored those. **Grading your own homework, worse each pass.**
- **What held: nothing was written.** Four wrong classifiers, zero corrupted rows - dry-run then
  hand-check before `--write`, every time.

JUDGMENT-ONLY: an iteration-stopping rule for the author's own debugging loop - no scan counts failed hand-checks. Durability: the incident and rule are anchored at #267.

## AN ANALYSIS ROW HAS NO CODE TO VERIFY (B1790 - L540, CHECKLIST #266)

**MEASURED: of 148 rows naming no artifact, 138 belong to batches whose commit touched NO CODE.**
Spot-checked: `B1512: engine timing COMPLETE (42.9 min)` changed three .md files and nothing else.
**A measurement turn's output is a number and a lesson.**

- **"EXECUTED means verified against code" is unsatisfiable BY CONSTRUCTION for analysis rows.**
  138 are permanently ineligible for the only terminal state that fits them - **a category error in
  the ledger, not a backlog.**
- **Do not pick a resolution silently.** DROPPED implies abandonment, OPEN-forever makes the queue
  useless, EXECUTED-on-docs reverses the ruling. **The six classes exist because states were being
  invented; choosing here without a ruling repeats that.**
- **Name a verdict to its evidence.** `CODE_LANDED_IN_BATCH` is not `VERIFIED` - a batch carries
  several rows, so it proves the batch produced durable code, not that THIS row's claim is it.
  **B1777's error was asking about the batch and answering about the row.**

JUDGMENT-ONLY: the category call (analysis-output vs build-claim) is semantic; the enforceable halves live in the six-class vocabulary gates (scan_queue_vocabulary) and the #264 build-claim checker, both cited in their own sections.

## PROMOTION NEEDS A BATCH-SPECIFIC ARTIFACT (B1788 - L539, CHECKLIST #265)

**A row earns EXECUTED only on a WIRED gate or a `test_bNNN` - artifacts tied to the batch that
claimed them.** Docs and file mentions do not count.

- **My first pass promoted 85 rows on LEARNINGS/CHECKLIST references** - the prose the owner's
  ruling explicitly excludes. **I encoded the instruction's shape while inverting its content.**
- **A file mention is not evidence.** `technical.py` predates most rows naming it. **Absence stays a
  strong negative; presence is not.** 39 -> 20 promotions on that alone.
- **MEASURED: 20 promoted, 148 still open, 145 of those naming nothing checkable.**
- **The burden of proof sits on PROMOTION** - "if anything to be done even potentially, keep them
  open". A row stays OPEN by default and must earn EXECUTED.

**Mechanically enforced** by scripts/verify_build_claims.py (LANDED requires the named artifact to exist) and the A1-ruling vocabulary gates.

## A BUILD CLAIM MUST NAME ITS ARTIFACT (B1787 - L538, CHECKLIST #264)

**MEASURED: of 134 build-claiming tickets in 48h - 54 LANDED, 0 MISSING, 79 NOT_CHECKABLE.**
Nothing is missing; **59pct simply cannot be verified because the ticket never names what it
built.** The limit is not the checking, it is that most claims are unfalsifiable as written.

- **Name the artifact**: a `scan_`/`check_` function, a `test_bNNN_`, or a file path. Then
  verification is one command.
- **A suspiciously clean result is a HARNESS BUG until proven otherwise.** Three false findings here
  before the real number: stripping `_` killed every snake_case name (0 LANDED / 17 false MISSING),
  a `scripts/`-only inventory made `backtest/` artifacts vanish, exact matching missed prefixes.
  **Fourth time this session a large finding collapsed on inspection.**
- **Adjacency asserts a relationship.** "92 awaiting verification" beside "96 work items" read as
  comparable; they are different sets, neither containing the other.
- **A marker set can be over-widened as easily as under-widened.** `MISS_MARKERS` stemmed 9 -> 116,
  of which 112 are generic topic nouns - so in a session about defects the gate fired on its own
  subject. Narrowing it then broke the corpus incident. **The corpus caught both ends.**

**Mechanically enforced** by scripts/verify_build_claims.py (the #264 checker, harness-fixed B2044, pin test_b2044_build_claim_test_citations_match_by_prefix).

## SIX MUTUALLY EXCLUSIVE LEDGER CLASSES (B1784 - L537, CHECKLIST #263)

**Owner ruling 2026-08-20.** `EXECUTED` / `DROPPED` / `BLOCKED` / `DEFERRED` / `OPEN` / `RUNNING`.
**There is no "finished but unverified" state** - a row is EXECUTED (verified against code and the
change log) or it is still work. A turn may never write EXECUTED.

- **I had reported SEVEN classes by unioning two rulings.** B1769 ruled six with DONE terminal;
  B1778 added CLOSED and **retired nothing**. Two overlapping terminal-ish states coexisted and I
  reported their union as a taxonomy. **A classification is a PARTITION, not a list of labels in
  use.**
- **When a ruling ADDS a class, name what it RETIRES.** An addition that retires nothing makes the
  partition quietly coarser - and the overlap survived two turns of counts reported off it.
- **228 rows moved DONE -> OPEN.** Never verified means never finished. **The number got worse
  because the definition got honest**; reporting that as a regression is the category-to-claim error
  again.

**Mechanically enforced** by scan_queue_vocabulary, the queue_state.py audit invariants (terminal-not-last), and the test_b1969 parser pins.

## A RESPONSE GATE MUST NOT ASSUME HOW THE RESPONSE IS FORMATTED (B1806 - L553, CHECKLIST #275)

**Two gates blocked a turn that had complied with both of them. Both defects were in the gates.**

- **POSITION: the block is wherever the MEMBERS are.** B1732 moved a locator from the FIRST header
  occurrence to the LAST and inherited the mirror bug; a later prose mention then opened the window
  PAST a complete block - **all three members listed, all three reported missing.**
  `_best_block_window` tries every occurrence and keeps the best. **A positional heuristic encodes a
  habit of formatting and inverts silently when the formatting changes.**
- **FENCING: a gate demanding a TABLE OF NUMBERS passes `keep_code=True`.** `_response_text` strips
  fences so documenting a defect cannot trip its own gate (B1781) - but a table belongs in a fence,
  and the counts gate reported 5 of 6 classes missing with all six on screen.
- **`keep_code` must skip the INLINE strip too - a fence IS backticks.** The first version guarded
  only the fenced regex and changed nothing. **Re-running caught it; reasoning would not have.**

## CARRY THE RULE, DO NOT RE-LEARN IT (B1783 - L536, CHECKLIST #262)

**MEASURED: of 15 text-reading gates, 13 had NEITHER of the two rules already learned for that
class** - B1738 (strip code spans; mention is not use) and B1742 (read only the final assistant
block). Each reached exactly the gate it was learned on, which is how B1781 fired on a LEARNINGS
entry that merely RECORDED a defect.

- **When you learn a rule, ask what will CARRY it to the next instance.** A shared helper, a
  primitive, or a test pinning the set. **Prose in LEARNINGS carries nothing.**
- **`_response_text()` is that carrier here**; every response-scanning gate uses it, pinned by
  `test_b1783_response_gates_inherit_text_scoping` so the unconverted set cannot grow.
- **Documenting a failure must not trip the gate for that failure**, or the lesson cannot be
  written down.
- **Five scales this session**: a stemmed marker list while twelve kept the defect (L515), a
  hardened trigger with a loose exemption (L528), an instance patched with its class left open
  (L519), a gate's scoping lesson not reaching the next gate (L536), and a ledger counting
  categories rather than members (L532). **Same shape every time.**

## PROVE A RESPONSE GATE ON A REALISTIC RESPONSE (B1780 - L535, CHECKLIST #261)

**MEASURED: the gate built to stop bad arithmetic blocked my next turn WITH bad arithmetic.** It
harvested class counts from every table in a long response, summed them into a number no sentence
claimed, and paired it with an unrelated `of 1937`.

- **`#240` governs a probe's CONTENT; this governs its SHAPE.** I tested five one-line cases and the
  incident genuinely was one line - **but a one-line probe cannot exercise a windowing bug.**
- **Prove every response-scanning gate on a multi-paragraph response** with several tables and
  unrelated numbers nearby. That is the environment it runs in.
- **A gate pairing two figures must require PROXIMITY** - otherwise it invents the relationship.
- **When the machinery starts reproducing the defect it was built to stop, the next gate is not the
  answer.** Three turns: a wrong count bred a gate, which missed the next wrong count, which bred a
  gate, whose first live act was a wrong count.

## SHOW EVERY CLASS OR CITE NO TOTAL (B1779 - L534, CHECKLIST #260)

**MEASURED: "388 CLOSED / 149 DONE / 96 OPEN ... 261 of 649" - three of SEVEN classes against a
seven-class total.** The owner caught it by adding: 388+149+96 = 633. **The figures were also wrong,
taken from the migration's TRANSITION counts rather than the ledger's state** (actual 390/153/95 of
662).

- **Report a breakdown in FULL, or cite no total** (`scan_partial_distribution`).
- **Say WHICH computation a number came from.** `scan_unverified_count` passed this, because a
  computation HAD run - it cannot know it was the wrong one.
- **Symbol-level verification of ticket claims produced ZERO findings**: 105 -> 33 after fixing my
  own index -> 0 on inspection, all parse artifacts. **A symbol beside a call site does not prove
  "X blocks Y" - only running it does.**
- **Twice in one turn a large number collapsed under inspection.** The problem is not that numbers
  are wrong; it is **reporting them before attacking them, and only attacking the ones I already
  doubt.**

## DONE IS SELF-REPORTED; CLOSED IS VERIFIED AGAINST CODE (B1778 - L533, CHECKLIST #258/#259)

**Owner ruling 2026-08-20.** `DONE` is no longer terminal - it means *reported finished,
unverified*. **`CLOSED` is written only by `promote_verified_closed.py`** from git evidence; a turn
may never write it. Ledger today: **388 CLOSED / 149 DONE / 96 OPEN - 261 of 649 not verified.**

- **A ledger count in a response must have been COMPUTED that turn** (`scan_unverified_count`).
  *"271 closed"* was 13. **~30 gates scan prose for markers; a number carries no marker.**
- **The check I skip is selected by whether I LIKE the result.** I ran the measure step and skipped
  the attack-your-own-answer step on a flattering number. No marker gate can fire on that.
- **Never write a regex through a bash heredoc.** `\b` becomes a literal backspace: it silently
  killed a gate AND `is_dual()` in the roster builder, whose B1454 fix was inert until repaired
  (now detects 60 duals). Third occurrence this session; a comment has recorded it since B1721b.
- **DROPPED is never promoted to CLOSED** - that manufactures completion for abandoned work.

## A DERIVED COUNT MUST NAME AND TEST ITS ASSUMPTION (B1777 - L532, CHECKLIST #257)

**MEASURED: I reported "271 closed in 48h"; the real figure is 13.** I computed
`created - open = closed`, which is valid only if every ticket starts open - **87pct are written as
DONE and never transition.**

- **State the assumption under any derived count, and test it.** One query over first-rows would
  have caught this before the owner did.
- **Count MEMBERS, not CATEGORIES.** "21 enforcement tickets" - **6 of them hold 62 work items**,
  one alone holds 22. A ticket is itself a category.
- **Verify DONE against git, not prose**: `scripts/audit_done_claims.py`. 66pct CODE_BACKED,
  26pct ANALYSIS_ONLY, 3.4pct UNSUPPORTED, **27 tickets on batches with no commit at all.**
- **Keep ANALYSIS_ONLY a separate verdict.** An analysis turn produces a number, not a diff.
  **Calling every doc-only DONE false is the same category-to-claim leap as the 271** - a council
  advisor read 87pct born-DONE as "87pct fabrication". It is not.

**Mechanically enforced** by scripts/audit_done_claims.py plus the per-ticket joined re-derivation in scripts/audit_ticket_staleness.py (B2055, pin test_b2055_staleness_join_rederives_ticket_claims).

## RE-DERIVE A TICKET'S NUMBER BEFORE WORKING IT (B1776 - L531, CHECKLIST #256)

**MEASURED: 6 of 21 open enforcement tickets described a world that no longer existed** - and none
was wrong when written. **60 of 69 open tickets carry a number**, and in the queue a past-tense
measurement reads exactly like a present fact.

- **Run `scripts/audit_ticket_staleness.py` before working or citing a ticket.** Three times now,
  re-derivation beat trusting: "11 unwired" -> 0, "64 markers" -> 67 with 17 inverting, and six at
  once here.
- **A stale number repeated in a response is a Truth-Standard violation with a paper trail that
  looks like evidence** - worse than no citation.
- **Do not report stale-ticket closures as progress.** Two of the six closed because work landed;
  four because the QUESTION changed shape. **Closing a stale framing is bookkeeping.**

## PRINT THE SAMPLE IDENTIFIER BEFORE JOINING TWO MEASUREMENTS (B1775 - L530, CHECKLIST #255)

**MEASURED: I explained a rho with a defect from a different dataset.** The persistence gap was real
in one cube; the rho came from another. **Both measurements were correct and careful. The join was
assumed** - I never asked which cube produced the numbers I was combining.

- **Print the sample identifier for each measurement before combining them** - row count, fire
  count, manifest hash. One line. **A shared subject is not a shared sample.**
- **Confirm on a SECOND dataset before writing the lesson.** The contradiction only appeared when
  the same check ran on wave 1. **A finding and the lesson written from it are the same evidence,
  not two.**
- **Retract the ATTRIBUTION without discarding the measurement.** The gap is still real; what failed
  was the link. Say which half survives.

JUDGMENT-ONLY: no scan knows which two measurements a sentence is joining; the rule is applied at write time, and #255 anchors it.

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

**Mechanically enforced** by the _WRITTEN_FIELDS strip in the tool-text collectors and the trunk pin test_b1987_no_gate_reads_raw_tool_text.

## HARDEN THE EXEMPTION, NOT JUST THE TRIGGER (B1773 - L528, CHECKLIST #253)

**EXTENSION (B1799 - L550): AN EXEMPTION KEYED ON INTENT IS KEYED ON NOTHING.**

**MEASURED: I shadowed `_read_entries` three batches after building the test that forbids it.** The
attractive fix was to exempt *"deliberate wrappers that alias the original"* - true of what I had
written, and **an opening any accidental shadow walks through by adding one alias line.**

- **Key an exemption on an OBSERVABLE property, never on why the author wrote it.** A test sees
  shape, never intent.
- **When your own gate blocks your own fix, change the FIX.** The restructure took one rename;
  weakening the check is faster and afterwards indistinguishable from never having had it.
- **If the gate is genuinely wrong, that is a separate finding** - its own evidence, its own turn,
  never a clause appended to the change it is blocking.

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
- **"Best of N" is only N if the N are distinct.** The selection-noise floor (0.369 then; re-measured 0.333 at B2009, and the family question answered by the picks themselves) was calibrated
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

**Mechanically enforced** by roster_core.measure_degraded_exits run per cube (#252) and the live flip-branch pin test_b2043_regime_flip_fires_on_a_real_flip_through_replay (B2043 closed the fallback itself).

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

**Mechanically enforced** since B1769: the owner ruled on 2026-08-19 (six classes, `_reason:_`
required on every non-terminal row) and `scan_queue_vocabulary` validates both, via `require_each`
with placeholder rejection. **This paragraph said "JUDGMENT-ONLY until the owner rules - attach the
mechanism when the ruling lands" for THREE DAYS after both had happened** (B1988): a standing
attach-later instruction has no owner once its trigger fires, which is `#279`'s decay arriving
through a TODO instead of a register. A JUDGMENT-ONLY that names a future un-blocker needs a
mechanism watching for the un-blocker - or the batch clearing the blocker sweeps for waivers
naming it (L613; anchored to `#279`, whose decay this is, arriving through a TODO instead of
a register).

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

## MENTION-vs-USE APPLIES TO TOOL TEXT, AND CHECK A TEXT'S SHAPE BEFORE REGEXING IT (B1812/B1813 - L556/L557)

**Writing a marker into a file is not running it.** MEASURED: `rng.normal` appeared 3 times in a
file a turn WROTE - a fixture and a lesson quoting the generator - and the gate read it as a
generator having run. **B1738's rule for the RESPONSE had no equivalent for TOOL text.**

- **The transcript carries the tool NAME, so the split is exact:** `Bash`/`PowerShell` `command` is
  EXECUTED; `Write`/`Edit` `content` is WRITTEN. Use `_executed_text` for any "did X RUN?" question.
- **In a codebase whose subject is its own enforcement, mention is the NORMAL case** - every lesson
  quotes the marker it is about and every pin test embeds its trigger.
- **And check a text's SHAPE before regexing it (L556).** Tool text is ONE line, so an unanchored
  `[^\n]*` ate the whole corpus after the first `[1/1]` inside a quoted string - 183 chars in,
  84 out, every tool-text gate blinded by the strip meant to stop one false positive. **A gate
  report is LINE-ANCHORED; an echo inside a JSON string is not.**
- **Assert the LOSSLESS case.** A strip is defined as much by what it must NOT remove; the version
  that shipped without that assertion is the one that broke.

**Mechanically enforced** by the shared heredoc/data strips in the executed-text collectors, pinned by test_b1979_heredoc_bodies_are_data_not_commands.

## A GATE'S OWN DIAGNOSTIC IS NOT EVIDENCE, AND A SEAM MUST TAKE THE LIVE PATH (B1811 - L555, #276)

**MEASURED: the only `rng.` in the transcript was the gate's OWN message**, which quotes
`rng.normal(1,3,30)` to explain itself. The Stop hook feeds it back and the next turn echoes it, so
**firing once seeds the next firing.** Third instance: B1732 (self-description shifted its own
window), B1738 (a response listing trigger words fired the gate), B1811.

- **Strip prior gate reports in the SHARED readers**, not per gate. B1738 guarded the RESPONSE and
  this arrived through TOOL text - a rule learned on one reader did not travel (L536).
- **Keep vivid diagnostics; strip the echo.** Quoting the trigger vocabulary is what makes a message
  useful AND self-triggering.
- **A seam that answers a different question than the live path proves nothing** - `#241`'s
  corollary. Ten call sites let an injected `tool_text` skip every scrub, so the first probe of the
  fix passed against a path production never takes. **Put the override INSIDE the helper.**

## PROVE GATES ON THE VERBATIM INCIDENT, AND GIVE THEM A SEAM (B1760/B1761 - L516/L517, CHECKLIST #240/#241)

**EXTENSION (B1805 - L552): ONE INCIDENT PROVES ONE PATH.**

**MEASURED: `scan_response_gates` passed the sweep every run on one sentence - *"Reverting."* -
while 5 of 12 tense variants went unmatched.** `revert` is the only one of its six verbs not ending
in `e`, so the naive `stem + "ing"` produced a real word for that verb and garbage for the rest.
**The single verb the incident used was the single verb the expansion handled correctly.**

- **Markers that are GENERATED need an incident per generation BRANCH** (`EXTRA_INCIDENTS`), not one
  per gate.
- **At least one branch must be must-be-QUIET.** A corpus of only must-fire entries cannot see a
  gate that fires on everything - and this one also tripped on *"undocumented"* and *"hardwired"*.
  **Too tight and too loose at once; one incident shows neither.**
- **The missing form was the PRESENT PARTICIPLE** - the tense you narrate an in-flight action in.
  The gate existed to catch narrated-but-unperformed actions and was blind to how narration is
  usually phrased.

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
- **EXTENSION (B1798 / L549) - starving is one face; there are three, and two showed up in a single
  turn:**

  | face | symptom | tell |
  |---|---|---|
  | starved state | false FAILURE | gate silent on text it should catch |
  | **empty input** | **false PASS that reads as a clean negative** | **`entries loaded: 0`** |
  | **over-supplied state** | **false PASS via a route you are not testing** | **both arms agree** |

  **An empty measurement renders identically to a negative result** - print the INPUT SIZE beside
  every marker list, one line, always. **And when both arms of a probe agree, suspect the probe
  before believing the result**: mine passed twice because the turn was editing the very files that
  satisfied the member under test.
- **A ticket describing a defect does not stop the defect (L549).** `S6-B1774e` named the raw-`in`
  matching class, stayed OPEN with a good reason, and the defect it predicted then blocked a turn.
  **Deferred-with-a-reason and unfixed are the same state from the defect's point of view** - when
  the class is live in machinery you rely on, deferring is a decision to accept the next incident.

## STEM EVERY MARKER LIST, AND SWEEP THEM ALL (B1759 - L515, CHECKLIST #239)

**MEASURED: `scan_miss_capture_complete` stayed QUIET on the words *"which is the failure
itself"*.** Zero of nine `MISS_MARKERS` matched while `fail` and `failure` were both present - so a
plainly-stated defect went unticketed as a miss.

**Third instance of the class L509 named.** L509 said *encode the stem*; I fixed
`NARRATION_MARKERS` and left twelve other lists in the identical shape, including the one guarding
miss-capture.

- **A marker list is a claim about how a class will be WORDED.** Stem the root; the conjugations
  come free. Enumerating remembered phrasings is guessing.
- **EXTENSION (B1796 / L548) - THREE RUNGS, AND ENUMERATION IS THE BOTTOM ONE:**

  | rung | covers | example |
  |---|---|---|
  | enumerate phrasings | only what you remembered | `promoted`, `stays open` |
  | stem the root (`#239`) | **conjugations** | `verif` -> verify / verified / verifying |
  | match the SHAPE (B1796) | **dialects - the same claim in another domain's words** | quantifier + state verb, or negative existential |

  **MEASURED: `scan_partial_read` held the ticket dialect and fired on 2 of 10 verdict sentences -
  0 of 8 for code and documents.** *"All 138 are complete"*, *"there are no other call sites"* and
  *"no document outside archive/ still references it"* are ONE claim in three vocabularies.
  **Stemming would not have helped - the words are unrelated.** Matching the grammatical shape
  covered all three at once: **11 of 11 fire, 0 of 7 false positives.**
- **Ask which rung a matcher is on before adding to it.** Reaching for more words is the reflex, and
  it is the bottom rung; **if two domains express the same claim with disjoint vocabulary, the
  matcher is on the wrong rung and no amount of adding fixes it.**
- **When a marker list is fixed, sweep EVERY other list in the same file that turn.** 18 lists, 13
  unstemmed - found only when the owner asked a fourth time.
- **WHEN A SWEEP FINDS EVERY INSTANCE CORRECT, THE FIX BELONGS UPSTREAM (B2140 / L638).** I swept
  a dated fact ("26 exits per entry") across the queue and the ledger: 6 occurrences, ALL
  legitimate historical records of pre-deprecation cubes. The instinct is to report "no siblings,
  nothing to do" and stop. **But something WAS wrong** - my present-tense SUMMARY of one of them,
  which is upstream of every record. A clean sweep does not mean a clean class; it relocates the
  defect from the artifacts to how they are QUOTED, and that is where the fix goes.
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

**Mechanically enforced** by scripts/gate_incident_corpus.py and test_b1762_every_scan_gate_has_a_corpus_entry.

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

## A REUSED NAME'S TERMINAL ARTIFACT SHADOWS THE LIVE RUN (B2193 - L649, CHECKLIST #283)

**MEASURED: the B2192 autonomous chain, on its first start, read sw50's wave
summary, found INCOMPLETE_MAX_LEGS, and correctly HALTed - while the live
resumed sw50 run was at sim day 110.** The summary was the KILLED parallel-era
attempt's; resume-in-place reuses the wave name to keep its checkpoint dir, so
the wave inherits every name-keyed artifact of the failed attempt, including
the exact file readers poll for its outcome.

- **A terminal artifact on disk at launch describes a PRIOR attempt by
  construction** - it is older than the RUN it claims to describe (#281's
  sibling: there the artifact was older than its GENERATOR). The launcher
  archives it - evidence preserved, path cleared - before any reader can act
  on it.
- **The fail-closed reader was CORRECT and still misled.** A reader about to
  act on a terminal verdict checks the artifact is younger than the run it
  describes (heartbeat comparison) - a verdict minutes older than a live
  heartbeat is the tell.
- **Scope, measured not assumed:** the repo has exactly ONE wave-summary
  writer (run_wave.py main()) and the archive guard runs in that same main()
  before it - so the guard covers 1 of 1 writer; other name-keyed sentinels
  (completion flags, verdict files) get the same check at their own launch
  sites when created.

**Mechanically enforced** by run_wave.py archive_stale_summary() at launch,
pinned by test_b2193_stale_wave_summary_is_archived_at_launch.

## A DIRECTIVE'S 'ALL' IS ENUMERATED FROM THE PLAN, NOT FROM THE ACTIVE SUBSET (B2197 - L650, compliance failure against #164)

**MEASURED: the standing all-configs directive was satisfied on the 5-config W-B band while
the plan's own factorial enumerated 35 engine configs; the 30 others were unticketed and the
owner had to ask.** When a directive quantifies over ALL of a class, run the enumeration the
plan already carries (the factorial's ENGINE RUNS line), ticket the full set, and let a
completed subset close its ticket - never the directive. JUDGMENT-ONLY for detection;
durability pinned by test_b2123.

## RUNNING AN ANALYSIS IS NOT DELIVERING IT (B2198 - L651, CHECKLIST #284)

**MEASURED: the mandatory post-config battery auto-ran on every landing - exit 0
three times, ledger steps DONE with evidence, grid written - and the owner asked
why they had never seen a result for any config.** Every report of mine verified
that it RAN (a boolean) and quoted one headline number; the analysis itself sat
in a JSON file nobody was reading.

- **A directive that an analysis runs per event is a directive about a DELIVERED
  analysis.** The artifact is the medium, not the deliverable.
- **"Did it run?" and "what did it say?" are different questions**, and the
  verification habit answers only the first - which reads as diligence while the
  reader learns nothing.
- **Ship the RENDERER with the runner, and have the runner invoke it at the
  moment it announces completion**, so delivery cannot depend on the reporter
  remembering. Sibling of L641 (silence is not evidence of work in progress):
  there the work was absent, here the work was real and the reporting was silent.

**Mechanically enforced** by scripts/postconfig_report.py invoked from
run_wave.py at arm completion, pinned by
test_b2198_battery_result_is_rendered_not_only_written.

## A LOCKED FORMAT BINDS THE WRITER, NOT THE QUOTER (B2199 - L652, CHECKLIST #285)

**MEASURED: Table C is locked at 12 columns across four batches; I retyped a
9-column version into chat three times**, dropping `P1-P6 bands tested` - the
column that separates a config which searched 18 parameter values from one that
searched 2 - until the owner asked whether the format was locked.

- **Retyping a locked artifact is a second, unreviewed renderer**, and its
  omissions look like editorial trimming rather than data loss.
- **Print it.** Ship the command that emits the locked form and quote that
  command's output: `scripts/show_table_c.py` for Table C.
- Sibling of L651: there the result never left disk; here it left disk lossily.
  **Both are the reporting layer undoing work the mechanism did correctly.**

**Mechanically enforced** by scripts/show_table_c.py, pinned by
test_b2199_table_c_is_printed_with_every_locked_column.

## A PIN ON THE CALLEE IS NOT A PIN ON THE WIRING (B2208 - L654, compliance failure vs #224)

**MEASURED: I inserted a print call AFTER a function's `return` - dead code. The file
parsed, the pyramid was green, the pin (which called the renderer directly) passed, and
the output never appeared for THREE landings until the owner asked.**

- Wiring a call into an existing function? **The pin must assert the call site is
  REACHABLE**, not merely that the callee works.
- Cheap general form: AST-walk the edited module asserting no statement follows a
  `return` in any function, plus assert the new call precedes that return.
- **"X now does Y" is a claim about the PROCESS, not the file.** Verify it by finding
  Y's output in the process's actual output, or label it UNVERIFIED.

## A STATUS IS NOT A FINDING (B2211 - L655, compliance failure vs #284)

**MEASURED: a report rendered 14 integrity checks, a 50-trade re-derivation and a
300-combination funnel as nine rows reading "DONE". The owner's verdict was
"absolutely horrible and inadequate. It just says done!"**

- **Print the MEASURED VALUE beside WHAT WOULD HAVE BEEN ALARMING.** A row the
  reader cannot disagree with carries no evidentiary weight, and DONE is
  undisagreeable.
- **Report the check set's FALSIFIABILITY.** 140 checks with 0 failures ever
  makes green WEAK evidence; say so rather than implying earned confidence.
- **Organise by how the numbers could be wrong**, not by pipeline step order -
  step names are the pipeline's structure, not the reader's decision structure.

**Mechanically enforced** by scripts/postconfig_doc.py, pinned by
test_b2211_single_doc_reports_findings_not_status (asserts values, alarm
conditions, and the ABSENCE of status-only rows).

## A HEARTBEAT WRITTEN BY A WATCHDOG PROVES THE WATCHDOG (B2212 - L656, compliance failure vs #121)

**MEASURED: a process pool died at 19:37:49Z and the monitor called the run "alive and
cruising" 51 minutes later off a 0.0-minute-old heartbeat.** The heartbeat came from a
supervisor DAEMON THREAD still writing a STALE progress counter.

- **Read a counter only the WORK can advance** (sim_day_index, rows written, cells done),
  and **diff it across two observations**. An unchanged counter beside a fresh timestamp
  IS the stall signature.
- File freshness proves the writer lives, never the worker.
- **Dead-pool confirmation in one minute:** two CPU samples ~45s apart of parent and two
  workers - frozen workers beside a parent at ~98% of one core - then grep the run's log
  for Traceback / AssertionError / BrokenPipe.
- The evidence is often already in your own prior reports; compare consecutive readings
  before trusting either.

## A NAME YOU COINED IS STILL AN UNVERIFIED CLAIM (B2213 - L657, compliance failure vs #222)

**MEASURED: I proposed a status value, then wrote it in later sentences as if the system
had it. Grep returned exit 1 - it does not exist.** The mechanism-existence rule's examples
are all things SOMEONE ELSE might have built, so it never fired on a name invented in the
same breath.

- **Label an invented identifier PROPOSED-NOT-BUILT at the moment of invention**, and keep
  the label on every later mention in the same response.
- **The absence is often the finding.** That no status value could express "censored trade
  population" is precisely why the measured drop count gated nothing.
- Mechanism: the #222 scan is the enforcement and it fires; telling a proposal from an
  assertion is JUDGMENT-ONLY, since no scan reads intent.

## KILLING BY NAME IS A MACHINE-WIDE ACTION (B2214 - L658, compliance failure vs L411)

**MEASURED: executing a restart, I ran `Get-Process python | Stop-Process -Force` twice.**
That force-kills every python on the box - pytest, other sessions, unrelated work. It was
survivable only because nothing else was running, and I cannot prove after the fact that
nothing else died.

- **Get the PID, VERIFY its command line, then `Stop-Process -Id`.** Never `-Name`, never a
  pipeline sweep.
- **An unidentified target is not a target** - if you cannot name what you are killing and
  why it is yours, stop.
- Use `scripts/kill_wave_tree.py --out-dir <dir>` (dry-run by default, refuses without the
  wave's heartbeat).
- These rules bind hardest **while executing an owner instruction under time pressure**,
  which is precisely when they get skipped.

## A DISCLOSURE DIES AT THE CALLER (B2215 - L659, compliance failure vs #284)

**MEASURED: a selector records three disclosures about how many candidates it truly ranked
over; the caller copies two unrelated keys and drops all three.** The committed artifact
therefore cannot answer "were all of them analysed?" - the exact question the disclosure
was built for.

- **When a producer emits a disclosure, check the CALLER carries it to the artifact.**
  Writing it is half the fix; the reporting boundary is where it dies.
- A field set on a returned dict is a **claim about what a reader will see** and needs the
  same executed check as any other claim.
- **Third instance of one class in a day** (L651 result never left disk, L655 status where a
  finding belonged, L659 disclosure dropped in transit): information the system
  deliberately produced not surviving the reporting boundary. Each was invisible until
  someone asked a question the artifact could not answer.

## WHEN A LANDING IS EXPECTED, READ THE DIRECTORY NOT THE LOG (B2218 - L660, recurrence of L498)

**MEASURED: the engine wrote its full output set at 00:50Z; the chain log still showed the
old LAUNCH line, and I told the owner "still running" for several turns.** The #223 gate
caught it in one turn - the mechanism worked, the reading did not.

- The **log is an event record written by the orchestrator at its own pace**; the
  **directory is the work's own output**. Between engine-finish and summary-write they
  disagree, and the log is the stale one.
- Sibling of L656: both are **reading a SECONDARY record and believing it about the PRIMARY
  work**.
- A documented lesson RECURRING is worse than a novel miss - search LEARNINGS before
  calling anything new.

## A FREEZE AS LONG AS THE QUEUE MAKES THE MONITOR UNFIXABLE (B2219 - L661, compliance failure vs #121)

**MEASURED: the stall watchdog was deferred because the supervisor is engine code and a wave
was running. 21 configs x 2h means the moratorium's length EQUALS the queue's length** - the
monitor could not be fixed until after the run it protects. I called that correct sequencing
for several turns.

- **When a freeze blocks a fix, ask which SIDE of the boundary the fix needs to live on.**
  Detection almost never needs to live inside the thing detected.
- The frozen component usually already PUBLISHES what a reader needs; diff it from outside.
- Sweep the other freeze-deferred tickets for the same question - some are genuine, some are
  self-sealing, and only reading them apart tells you which.

## STATE THE READING THAT COSTS YOU MOST, FIRST (B2220 - L662)

**MEASURED: asked why a ticket count had not fallen, I was about to answer "the process
working" - a framing that grades the sweep on effort rather than on what it found.** The
truer accounting: I closed the cheapest ticket and opened the two that reach the owner's
results.

- **When reporting on your OWN work, lead with the reading that costs you most.**
- Mechanical test: **write the sentence a hostile reviewer would write**; if it is truer
  than yours, lead with theirs.
- A comfortable self-assessment buries the headline - here, that a degeneracy finding
  invalidates the denominator behind every multiple-testing correction.
- JUDGMENT-ONLY: no scan detects a self-serving frame. The Contrarian lens is the guard,
  which is why a council without one is not a council.

## CHECK THE EFFECT IN THE ROWS WITH ENOUGH DATA (B2226 - L663, compliance failure vs #115)

**MEASURED: three spans returned an identical top cell at the swing where samples were
THINNEST (12 fires), and I proposed a band change on it. The same three spans at the
well-sampled swing did NOT collapse.**

- **A degeneracy measured only where n is smallest is a SAMPLE-SIZE hypothesis wearing a
  parameter hypothesis's clothes.** Check the rows with enough data to show the effect.
- **Watch the metric too**: counting rows that agree on value AND count treats two starved
  cells as agreeing - agreement about nothing.
- **Write the objection BEFORE the recommendation.** Here it did not decorate the answer,
  it reversed it.

## A CONSTANT QUOTED FROM A TICKET IS UNVERIFIED (B2227a - L664, compliance failure vs #222)

**MEASURED: I quoted "the 3,223 MB floor at plan line 1391" from an EXECUTION_QUEUE row, computed
that a live 1.69 GB reading sat 46pct below it, and filed a P0.** Opening the file showed the
constant is at line 1397, and that its definition site carries an explicit **[GRAIN-STALE]**
marker: 3,223 MB was PER-WORKER from when one process was one config; at pool-10 per-process
peaks run ~1.0-1.2 GB. **1.69 GB was ABOVE the present-grain peak. The alarm was a unit
mismatch.** The number was real, the reading was real, the comparison was meaningless.

- **Secondary records preserve the DIGITS and drop the GRAIN, the CAVEAT and the LINE NUMBER** -
  exactly the payload that decides whether a comparison is valid. Read the constant at its
  definition site, or do not cite it.
- **Watch for sibling floors at other grains.** The same sweep found 0.333 is the PER-CELL
  yardstick while iid (0.088), entry-day block (0.2245) and SMC block (0.3115) floors exist
  beside it. Quoting the right number at the wrong grain is this failure's most common shape.
- **Third recurrence of one class** (L656 heartbeat-proves-the-watchdog, L660 read-the-directory-
  not-the-log, L664 read-the-file-not-the-ticket): **trusting a SECONDARY record about a PRIMARY
  fact.** L664 is the worst of the three - the primary file already carried the exact correction
  that would have stopped me.
- **The ordering is the lesson:** the half I asserted was wrong and the half I had not checked
  was right. Leading with the arithmetic you can compute, while skipping the probe that settles
  the question, is the shape to catch in yourself.

## Phase 6 — END-OF-TURN SWEEP (CHECKLIST #67 — HARD RULE, no exceptions)

**TICKET COUNTS BY GROUP - EVERY TURN (B1803 - CHECKLIST #274, owner directive 2026-08-21).**
*"Always provide a count of tickets by groups at the end of the turn. similar to skills invoked."*

- **All SIX classes with a number each** - EXECUTED / DROPPED / BLOCKED / DEFERRED / OPEN / RUNNING.
  A class named without a count reports nothing; a class omitted lets silence stand in for zero.
- **`python scripts/queue_state.py`, never a hand count** - per distinct ticket, last row wins. The
  ledger is an append log, so a row-level figure is wrong by an unbounded amount (`#271`).
- **Show the delta when anything moved.** A level repeated each turn hides that nothing changed.
- Enforced by `scan_ticket_counts_missing`.
- **B2039 (L618, CHECKLIST #282): the counts are a TABLE - six classes x (count, delta) -
  plus the turn's ticket OUTCOMES, and the skills block names FULLY INVOKED vs not.
  An owner FORMATTING directive is a SPEC with a gate, encoded the same turn - half-encoding
  passes as compliant until the owner asks why (six-number prose satisfied the old gate for
  two days). Mechanism: the `tabular with a delta column` require_each member of the same scan.

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
   **EXTENSION (B2128 / L625) - AN ALL-CLEAR IS THE SAME CLAIM AS A ZERO-HIT.** Auditing
   whether a declared thing is ENFORCED, my probe reported 17 of 17 manifest fields
   consumed - because its corpus included `run_wave`, the script that WRITES manifests, so
   every field name necessarily appeared. The corrected AST read-scan over CONSUMERS ONLY
   found 4 unread, one of them load-bearing. **An enforcement audit must exclude the
   artifact's PRODUCER and match a consumption SITE (an access, a call, a branch), never a
   name** - a grep answers "does this name appear", which is the question you are not
   asking. Validate by planting a known-unread member and confirming the probe reports it.
   The tell: a clean all-clear arriving one command after a real instance was found.
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
| Run a TIMING measurement (concurrency point, wall-clock A/B, ELAPSED comparison) | HOLD every CPU-heavy process - including your own pyramid - until the completion line; name the load risk in the manifest (JUDGMENT-ONLY detection; the manifest risk row + cadence hold clause are the mechanism) | B2095/L621 (the pyramid contaminated the N=3 trio; 2.93x became an upper bound and a rerun was owed) |
| Launch anything long-running / costly | Small test → manual review → owner approval → scale; resume infra armed; NEVER auto-launch Batch B | L86/L95 ($150 lost); `feedback_no_auto_launch_batch_b` |
| Launch the engine AT ALL - probe, smoke or wave | Verify the tickers file (`#187`) AND arm the cadence monitor (`#185`) IN THE LAUNCH TURN. **There is no duration exemption** - "too short to need a monitor" is a test the rules do not contain, and the probe judged too small ran 18 minutes against a 3-minute cap (B2128/L626). A run whose length depends on a cap you have not verified is unbounded by construction. | L626; MEASURED: 2 of 6 engine launches in one session were gated at launch time |
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

PROSE-ONLY: an INDEX of historical failures - each entry's enforcement lives with its own rule; gating the index would gate a table of contents.
