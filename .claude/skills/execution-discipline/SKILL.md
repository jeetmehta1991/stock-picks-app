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
7. **"I don't know" and "this failed" are always compliant answers.**
   Reporting a failed test, an interrupted run, or an unresolved question
   accurately is success; dressing it up is the violation.

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

## Phase 5 — MISS-CAPTURE FEEDBACK LOOP (whenever a miss is found)

A "miss" = any error, silent skip, stale claim, wrong count, missed scope item,
or owner correction — found by you, the owner, or an audit. Same turn, no
deferral:

1. **LEARNINGS.md entry** (next L-number): what happened, root cause, the
   generalized rule, and the detection signal that would have caught it earlier.
2. **CHECKLIST.md addition** ONLY if the miss is a NEW failure class not
   covered by existing items — and it must pass the ANTI-AUDIT-THEATER GUARD
   (CHECKLIST #136): demonstrate the new item would have retroactively caught
   the last 3 relevant PIVOTs/misses, or it is theater and gets rejected.
   If an existing item should have caught it, the miss is a COMPLIANCE failure —
   record that in the L-entry instead of adding a redundant item.
3. **Memory write** if the lesson is a standing owner-behavior rule
   (a `feedback_*` file + `MEMORY.md` pointer).
4. **Fix or ticket** — the miss itself is either remediated this turn or gets
   an EXECUTION_QUEUE ticket with priority. Never "acknowledged" without one
   of the two.
5. Owner corrections are ALWAYS misses (the system failed to self-catch).
   Six owner catches in Pass 52 is the canonical anti-pattern.

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
