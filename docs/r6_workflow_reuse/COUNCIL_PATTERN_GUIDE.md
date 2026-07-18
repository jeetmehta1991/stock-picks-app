<!-- Source: per CHECKLIST #77 canonical-source; Council 287 B1234 2026-07-07 doc-sync sweep -->

<!-- COUNCIL 278-287 SYNC BANNER (B1234 2026-07-07) - READ FIRST -->
> **Sync status:** Body may contain refs stale as of 2026-06-27 or earlier. Canonical current state (B1231):
> - `len(ALL_STRATEGIES) = 219` (post-B1189 DELETE dxy_headwind); `STRATEGIES_DISABLED_MISSING_PRODUCER = set()`
> - Test count: 880 passed, 2 skipped on test_unit + test_integration
> - CHECKLIST items #1-#158, LEARNINGS through L209, latest batch B1310
> - Councils 278-287: 40 strategies loosened + 11 silent misses remediated + 25+ producer coverage audits + historical timeline finding + 2 critical bugs FIXED via graceful degradation
> - Stage 4 walks: ARCHIVED to `archive/2026-07-07-stage-4-walks-complete/`
> - Sprint 5 tickets: 3 queued (S5-B1214 HIGH / S5-B1216 MED post-B1230 correction / S5-B1212 MED)
> - Comprehensive coverage report: `output_audit/PRODUCER_COVERAGE_COMPREHENSIVE_REPORT.md`

---

# Source: Sub-Charlie B1052 R5-to-R6 reuse documentation (commit pending)

# Council Pattern Guide - R6 Onboarding

**Purpose:** Codify the 4-advisor council pattern that drove 143+ councils across R5 batches B979–B1051, so R6 owners and Claude agents can adopt it from turn 1.

**Cross-links:**
- `R5_WORKFLOW.md` (Sub-Alpha Doc A: phase/process overview)
- `HONEST_FINDING_PIVOT_PATTERN.md` (Doc E, this folder): the safety net that catches a council that gets it wrong
- Pending sibling docs: phase-ladder guide (Sub-Bravo Doc B), AWS launch guide (Sub-Bravo Doc C), governance & checklist guide (Sub-Alpha Doc F)
- `feedback_mandatory_council_per_turn` + `feedback_council_enumerate_plus_recommend` (memory rules)
- `CHECKLIST.md` items #110 (mandatory council per turn) and #115 (enumerate + recommend)

---

## 1. What the Council Pattern Is

Before any non-trivial recommendation, Claude briefs a 4-advisor council:

| Lens | Question it must answer |
| --- | --- |
| **Contrarian** | What's the strongest case AGAINST the leading option? What could make it look obvious-in-hindsight wrong? |
| **Executor** | What is the lowest-risk path that actually ships value this turn? What is the smallest reversible move? |
| **First Principles** | If we forgot all prior batches/memory rules and re-derived from the goal, what would we do? Are we paying for sunk cost? |
| **Outsider** | What would a fresh quant or SRE see that this thread of context is blind to? What's the meta-pattern? |

The council emits a **verdict** that includes BOTH an **enumeration of options** AND a **recommended final choice**. Per CHECKLIST #115, enumeration alone is not a council; recommendation alone is not a council. Both are required.

The pattern is a structural alternative to adversarial-review-on-demand: instead of waiting for the owner to catch a mistake, the council pre-stages 4 contradictory perspectives that surface the mistake first.

---

## 2. Why R5 Required This Pattern

R5 batches B979–B1051 ran 143 councils numbered 79 through 145. The session opened with a recurring 4-miss pattern in a single day (turn-1 missed a deletion, turn-2 missed a count drift, turn-3 missed a stale banner, turn-4 missed a wired-vs-armed gap). The owner correction 2026-06-19 codified `feedback_mandatory_council_per_turn`.

The pattern materially prevented downstream costs:

- **B1018 -> Council 107:** designed a 4-phase pre-R5 ladder ($0.40 -> $1.20 -> $3 -> R5). Without the council, R5 would have launched on stale universe -> $5–10 wasted.
- **B1028 -> Councils 119/120/121:** R5 launched at $1.20–2.70 budget; meta-bug surfaced ("monitor not armed") was caught only because Council 126 (B1032) was forced before the cleanup, not because the bug was obvious.
- **B1044 -> Council 139:** Option-8 HYBRID structural fix for design-vs-armed recurrence. Pure-procedure rules had failed three times; Council 139's first-principles lens drove the producer-consumer registry + schema-contract test framework - the actual durable fix.

In all three cases, the council's enumerate-plus-recommend output was the artifact that the owner reviewed and approved. Without it, owner sign-off would have been a yes/no with no audit trail.

---

## 3. When to Council (Hard Rule)

**MUST council before:**

- Any code recommendation that modifies engine, screener, exit manager, dashboard, or producer paths
- Any AWS launch decision (instance launch, AZ failover, spot-vs-on-demand, ladder phase advance)
- Any threshold or parameter change (gate values, regime affinity, position sizing tiers)
- Any phase scope decision (R5 launch, ladder phase advance, smoke-vs-full, full pyramid vs focused)
- Any framework or sub-system proposal (registry, schema contract, lint rule, new exit method)
- Any sub-decision logging (DEC-NNN entry, INV-NNN open, EXECUTION_QUEUE ticket triage)
- Any honest-finding pivot disposition (see `HONEST_FINDING_PIVOT_PATTERN.md`)

**MUST NOT council for:**

- Pure logging actions (already-approved decision -> AUDIT.md entry)
- Git operations on already-approved commits (git add / commit / push of pre-approved diff)
- Simple acknowledgments ("Yes", "Confirmed", "Acknowledged" with no proposal)
- Tooling calls inside a council (don't recurse)

When in doubt, council. The cost is ~200 words; the cost of skipping is whatever bug the council would have caught (B1028 was $2 sunk + 1h 38m wall-clock).

---

## 4. How to Council (Brief Format)

A council brief is ~200–400 words across the following sections. The brief is part of the agent message, not a separate file.

```
COUNCIL <N> BRIEF
Context (~150 words): what changed, what's at stake, what's the asymmetric risk.
Options (3-8 enumerated):
  Option-1: <short title>. Pros: ... Cons: ...
  Option-2: ...
  ...
Lenses (4 required):
  CONTRARIAN: <strongest objection>
  EXECUTOR: <lowest-risk shipping path>
  FIRST PRINCIPLES: <fresh-derivation view>
  OUTSIDER: <meta-pattern>
Memory rules referenced: <feedback_*.md>, <CHECKLIST #N>
VERDICT: 4/4 RECOMMEND Option-X <one-line justification>
```

**Format requirements per CHECKLIST #115:**

- Explicit `ENUMERATE` list (>=3 options; >=5 for high-impact decisions)
- Explicit `RECOMMEND` line with the chosen option label
- Each lens speaks in its own paragraph, not a synthesized blob
- Memory-rule citations are mandatory when a rule applies (silent skip is non-compliant)
- Owner-rule compliance footer at end of message (CHECKLIST #45)

**Notation in commit messages:**

`Council <N> Option-<X> <descriptor>` - e.g., `Council 143 Option-3+4 LAUNCH-WITH-FAILOVER-AZ + EVIDENCE-PERSISTENCE`. The council number, option label, and descriptor MUST appear in the commit subject line so AUDIT.md cross-references resolve cleanly.

---

## 5. Who Councils

Two valid configurations:

**Sub-agent council (preferred for high-impact decisions):** spawn 4 separate Agent calls (or one Agent call that internally runs 4 lenses with isolation) with a fresh context per lens. This satisfies CHECKLIST #126 evidence-artifact rule: the sub-agent's response is the linked evidence. Used for B1042 (4 audit sub-agents), B1045 (3 parallel sub-agents), B1046 (3 sub-agents).

**Claude-direct council (acceptable for simple decisions):** Claude writes all 4 lenses inline in the agent message. Used for ~70% of B979–B1051 councils where the decision was small-scope (single file, no AWS cost, no schema change). Faster but lacks the isolation guarantee of a fresh sub-agent.

**Decision rule:** if a wrong recommendation would cost more than $1 of AWS time or more than 30 minutes of follow-up rework, use sub-agent council. Otherwise, Claude-direct is acceptable.

---

## 6. Session Statistics R5 (B979–B1051)

- **143 councils** numbered 79 through 145 (some council numbers are sub-numbered, e.g., 119+120+121 for B1028, 137+138 for B1043)
- **29 honest-finding pivots** surfaced cumulative this session (see `HONEST_FINDING_PIVOT_PATTERN.md`)
- **0 council-skips** caught by owner after the `feedback_mandatory_council_per_turn` codification

The council pattern is the single highest-leverage piece of R5 procedural infrastructure. R6 should adopt it from turn 1.

---

## 7. Example Councils (R5 Reference Set)

**Council 138 (B1043, "fix scope decision"):** Owner-mandated adversarial review of monitor. 3 parallel sub-agent audits returned. Council 138 enumerated 5 fix-scope options; recommended Option-3 STAGED-FIX-+-SMOKE. 13 BLOCKERS fixed same turn, all pyramid-tested. Pyramid 905+2 GREEN. Avoided design-vs-armed recurrence at the structural level.

**Council 142 (B1047, "retrospective engine-armed audit"):** After Phase C v2 smoke PASS but before Phase D launch, council 142 ran a retrospective check: were all 16 engine-armed claims actually OPERATIONALLY-VERIFIED per CHECKLIST #126? Verdict: 13/16 clean, 2 CONFIRMED-WITH-CAVEAT, 1 RESOLVED. Sub-agent caught HONEST-FINDING PIVOT #28: Phase C v2.5b PASS cited as evidence but not persisted. Fix shipped same batch via new artifact `output_audit/phase_c_v2_5b_smoke_pass_2026_06_28.txt`.

**Council 143 (B1048, "Phase D launch"):** 4/4 RECOMMEND Option-3+4 LAUNCH-WITH-FAILOVER-AZ + EVIDENCE-ARTIFACT-PERSISTENCE. Council enumerated AZ-handling options across us-east-1a/b/c, dispositioned the failover order, and persisted a `phase_d_r5_launch_evidence_2026_06_28.json` artifact pre-launch per CHECKLIST #126. Phase D launched on us-east-1b after us-east-1a returned InsufficientInstanceCapacity. Council 143's failover-AZ option was the load-bearing decision.

**Council 144 (B1050, "PIVOT-#29-class adversarial scan"):** After B1049 pivot #29 (PHASE_DIR unbound at preflight), Council 144 enumerated whether other Class-A-through-F patterns existed in `launch_r5_master_4y_v2.sh`. 7-bug audit returned; 4 real fixes shipped via B1050+B1051; 5 new pyramid tests written. The PIVOT-#29-class adversarial scan was itself a council-mandated artifact.

---

## 8. R6 Onboarding - How to Use This in R6

**Turn 1:** Read this doc. Read `HONEST_FINDING_PIVOT_PATTERN.md`. Read `CHECKLIST.md` items #110 and #115.

**Turn 2:** Council the first material R6 decision (e.g., universe-refresh approach, Phase 1B agent selection). Use a 4-lens brief. Document the verdict in the commit message.

**Turn 3:** Council whatever surfaces. Even if it feels redundant. The pattern only works when applied repeatedly; one-shot councils produce one-shot insights.

By turn 5 the pattern is muscle memory. By turn 20 the owner is no longer the safety net for design-vs-armed misses.

---

## 9. Anti-Patterns (Do Not Do These)

- **Skipping the council on "obvious" decisions.** B1028 was "obvious" - the meta-bug cost $2 + 1h 38m. Nothing about a multi-million-cell backtest is obvious.
- **Recommending without enumerating.** Pre-CHECKLIST-#115 sessions had 6+ recommendations stated without options. Owner caught all 6. Enumerate.
- **Enumerating without recommending.** Council 69 (pre-B969) shipped enumeration-only; owner had to compose the recommendation. Council 70 over-corrected to recommendation-only. CHECKLIST #115 codified BOTH.
- **Sub-bullet councils (1-lens "councils") that don't actually adopt 4 perspectives.** A council that doesn't have a Contrarian lens isn't a council. Write the objection even if it feels weak.
- **Forgetting to cite memory rules.** Memory rules are how prior-session learnings propagate. Silent skipping resets the project's institutional memory.

---

## 10. Owner-Rule Compliance Footer Template

End every council-driven message with:

```
OWNER-RULE COMPLIANCE:
  Council <N> BEFORE recommendation
  Council <N> enumerate+recommend (<M> options + Option-<X> RECOMMEND)
  CHECKLIST #25/#45/#67/#94/#105/#110/#112/#114/#115/#121-#127 as applicable
  feedback_mandatory_council_per_turn
  feedback_council_enumerate_plus_recommend
  <other feedback_*.md as cited>
```

This footer is the per-turn compliance gate. It is auditable by grep and serves as the owner's review surface.

---

**End of Council Pattern Guide.**
