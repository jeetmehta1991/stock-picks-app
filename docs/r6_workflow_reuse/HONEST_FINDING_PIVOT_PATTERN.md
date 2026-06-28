# Source: Sub-Charlie B1052 R5-to-R6 reuse documentation (commit pending)

# Honest-Finding Pivot Pattern - R6 Onboarding

**Purpose:** Codify the "honest-finding pivot" pattern that surfaced 29 times across R5 batches B979–B1051, so R6 owners and Claude agents inherit the primary safety net against design-vs-armed drift, stale-banner claims, and pattern-match-without-verification.

**Cross-links:**
- `COUNCIL_PATTERN_GUIDE.md` (Doc D, this folder): the structural pattern that surfaces pivots before they ship
- `R5_WORKFLOW.md` (Sub-Alpha Doc A): the phases the pivots live inside
- Pending sibling docs: phase-ladder guide (Sub-Bravo Doc B), AWS launch guide (Sub-Bravo Doc C), governance & checklist guide (Sub-Alpha Doc F)
- `feedback_audit_recommendations_against_existing_directives` (memory rule - primary mandate)
- `feedback_designed_vs_verified_requires_evidence_artifact` (memory rule - B1044 closing pattern)
- `CHECKLIST.md` items #110, #115, #126, #127

---

## 1. What an Honest-Finding Pivot Is

A **pivot** is a numbered, public retraction. When Claude's prior claim, recommendation, banner status, or design assertion is found to be wrong - by the owner, by a sub-agent, by an empirical check, or by a test run - Claude does NOT silently update. Instead:

1. Number the pivot (`#NN`, cumulative across the session)
2. State explicitly what was WRONG vs what is NOW TRUE
3. Identify honest root cause (not a sanitized "context evolved" framing)
4. Ship a fix (code + test) or document the constraint that prevents fixing
5. Preferably: pyramid test catches the class of error going forward

The pivot is logged in the commit message, in LEARNINGS.md when load-bearing, and in CLAUDE.md banner when the misclaim was banner-visible. The session running count is part of the commit message.

---

## 2. Why R5 Required This Pattern

The pattern was codified after a recurring failure mode: Claude would state a status ("X is wired", "Y is RESOLVED", "Z monitor is armed") that was true at the design level but false at the operational level. The owner caught these. Repeatedly. Then explicitly fatigued: "I don't want to keep demanding adversarial reviews" (owner directive 2026-06-28, B1044).

`feedback_audit_recommendations_against_existing_directives` (codified post Pass 53) made silent over-claims a hard rule violation. `feedback_designed_vs_verified_requires_evidence_artifact` (codified B1044) escalated the rule by requiring linked evidence artifacts (schema-contract test PASS, AWS smoke sentinel, end-to-end output) before any WIRED/ARMED/INTEGRATED claim could be stated.

The honest-finding pivot is the structural alternative to adversarial-review-on-demand. The pivot count itself is a session-quality metric: a session with 0 pivots is suspicious (every claim was right?); a session with too many pivots without test back-stops is also suspicious (each fix should reduce class-recurrence probability).

R5 ran 29 pivots across 71 batches. The class-recurrence count tracks the pattern's fade-out: design-vs-armed appeared 3 times in 24 hours (B1028, mid-morning, B1042) before B1044's structural fix made the class catch-able by pyramid.

---

## 3. When to Surface a Pivot (Hard Rule)

**AUTO-pivot when:**

- Owner catches a wrong claim ("the monitor is armed, why is it flagged?" -> AUTO-pivot #18)
- Sub-agent's audit contradicts your prior claim (Sub-A Council 137 caught B1042 design-vs-armed -> AUTO-pivot #25)
- Empirical check reveals a claim was over-promised (banner says X% RESOLVED, pyramid says Y < X -> AUTO-pivot)
- A pyramid test fails on something previously labeled RESOLVED-IMPLEMENTED -> AUTO-pivot
- A banner / EXECUTION_QUEUE row is shown stale by a fresh grep -> AUTO-pivot (Council 76 banner-verification precedent)
- The "evidence" cited for a claim turns out to not exist or not persist (B1047 #28 v2.5b smoke PASS unpersisted)

**NEVER hide a pivot:**

- Do not rename the bug to a feature
- Do not defer the pivot to a "later batch" while continuing to cite the wrong claim
- Do not bundle a pivot inside a non-pivot batch's commit message footer (give it its own clearly numbered call-out)
- Do not roll back the number to avoid breaking session-count optics

---

## 4. How to Surface a Pivot

In the commit message subject line:
```
Batch <NNNN> (date): <descriptor> HONEST-FINDING PIVOT #<count> <one-line>
```

In the commit body:
```
HONEST-FINDING PIVOT #<count>:
  WHAT WAS CLAIMED: <verbatim or paraphrase>
  WHAT IS NOW TRUE: <verbatim>
  HONEST ROOT CAUSE: <not "context evolved"; the actual mechanism>
  HOW IT WAS SURFACED: <owner question / sub-agent / pyramid / grep>
  FIX: <code + test diff summary>
  CLASS PROTECTION: <pyramid test added that catches the class>
```

Cite the relevant memory rules. Update the cumulative count in the commit footer:
```
POST-B<NNNN>: <X> batches, <Y> councils, <Z> honest-finding pivots.
```

---

## 5. R5 Session Pivot Log (29 Pivots, B979–B1051)

The owner mandate is "be brutally honest" about all 29 pivots. Below is the best reconstruction from commit messages + LEARNINGS.md + sub-agent outputs. **Pivots #1–#11 are reconstructed from `LEARNINGS.md` and CLAUDE.md banner narrative**; they originated in pre-session and early-session work and may not align 1:1 with the count chain re-derived from B1042 onward. A gap-acknowledgment is documented at the end of this section.

| # | Batch | What was claimed | What is now true | Surfaced by | Fix shipped |
| --- | --- | --- | --- | --- | --- |
| #1-#11 | pre-R5 / early session | Various banner-status claims (RESOLVED-IMPLEMENTED on items where engine wiring was design-only; wired=grep heuristic mis-classifications) | See `VERIFICATION_MATRIX.md` which replaced the grep-found heuristic. Owner correction `feedback_wired_means_engine_consumed` codified pattern. | Owner audit + pyramid test additions | `scripts/build_verification_matrix.py` + dashboard regen |
| #12 | B1000 | CLAUDE.md banner line 4 said POST-B993; line 14 cited pyramid 2026-05-15 1882/14/5/0; line 17 items (iii) and (vi) missing RESOLVED markers | POST-B999 updates needed; pyramid is 861+2 on focused test_unit+test_integration; items (iii)+(vi) RESOLVED-VIA-B987 + B982 | Council 100 Option-H C stale-banner audit | Banner patched same batch; 12-of-22 session batches were honest-finding-pivot closures by this point |
| #13 | walk-1 Sub-B B985 | Section 1 wiring-trace helper flagged 6 BB sub-signals as MISSING | All 6 BB sub-signals ALREADY EMITTED by `technical.py::compute_bollinger` via `str(period).replace('.','')` loop; Section 1 helper had a FormattedValue rejection bug | Pre-flight source-verification (`grep compute_bollinger`) per Council 89 | Helper extended to handle `ast.Call` inside FormattedValue (`_try_resolve_str_method_chain`); 1 new test pin |
| #14 | B1014 | B1010 `strat_insider_cluster_concentrated_sell_short` PASSING focused pyramid | Full 13-tier pyramid (3 days 19h `bbtd18s8b`) caught missing `_short_borrow_trap_active()` gate per B740/B741 lint enforcement; focused subset didn't exercise it | Full pyramid completion | Gate retrofitted same batch; `signals_used` list updated; LEARNINGS L168 codified per-strategy gate audit at wire time; CHECKLIST #118 |
| #15 | B1022 | "R5 launch approved" appeared to literally mean "skip ladder; launch R5 directly" | Asymmetric-risk analysis showed Reading-2 LADDER-PRE-APPROVED honored both this directive AND prior B1018 4-phase ladder approval; literal reading would violate L86/L95 and 7 prior reinforcements | Council 113 4/4 Contrarian + Outsider lens | Pivot documented; Q1-a `aws configure` credential pattern surfaced; ladder preserved |
| #16 | B1026 | Council 116 RECOMMENDED Option-B CASCADING for autoladder | Cascading required `batch395-instance-role` IAM profile with `ec2:RunInstances` - dependency unverifiable in real-time without burning AWS quota | Pre-execute verification step | Pivoted to Option-A SINGLE-LARGE-INSTANCE (simpler-is-safer); LEARNINGS L165 codified the verify-Council-prerequisites pattern |
| #17 | B1026/B1028 lineage | "1930 tickers in S3 = the universe scope" | S3 `aws s3 ls` count is OPERATIONAL CARDINALITY, not project-scope authority; PROJECT_PLAN line 193 specifies Master Dedup 1937 (5-tier per DEC-504) as scope | Owner question "what universe?" | Master 1929 ops intersection derived; 8 Master-only delisted-M&A documented; `feedback_aws_artifact_count_not_proxy_for_project_scope` codified |
| #18 | B1028 | Council 107/110/113-117 chain assumed T1a 503 as launch scope | PROJECT_PLAN line 193 authoritatively says Master 1937 (5-tier DEC-504); banner T1a references in CLAUDE.md are illustrative STATUS INDICATORS, not scope authority | Owner question "don't we need Master?" | Universe re-derived to 1929 (Master 1937 ∩ S3 OHLCV); `feedback_banner_is_status_not_scope_authority` codified; `feedback_readiness_audit_must_verify_universe_scope` (3-way reconciliation rule) added |
| #19 | B1028 in-flight | "B1019 Monitor package designed -> monitor armed" | Monitor was DESIGNED but NOT operationally wrapped around engine in user-data; engine ran via `python -m backtest.run_phase1a` DIRECTLY; once Phase 1 RUNNING sentinel emitted, system went BLIND 1h 38m | Owner question "if monitor is armed, why is it flagged?" + B1028 HALT-TERMINATED | `feedback_monitor_design_vs_operational_gap` codified + CHECKLIST #121 MONITOR-ARMED-IN-USER-DATA pre-launch grep |
| #20 | B1028 ladder | "pandas-ta installed via pip -> dependency satisfied" | `pandas-ta` install failed silently via `\|\| true`; engine ran with missing dep; Python 3.13 incompat | B1032 12-bug catalog post-mortem | `feedback_silent_failure_pairing_rule` codified + CHECKLIST #122 `\|\| true` paired-success-check |
| #21 | B1028 ladder timing | Phase 1 estimated 30 min; cascade approval assumed timing held | Phase 1 ran 1h 38m+ vs 30-min estimate; cascade timing-assumption failed; engine progress emit absent | B1028 wall-clock review | `feedback_phase_ladder_timing_validation` codified + CHECKLIST #123 PHASE-LADDER-TIMING-VALIDATION smoke <=15 min mandate |
| #22 | B1028 lineage AWS sizing | Initial Phase D user-data sized as fits-in-16KB | 12740 raw / 16988 base64 exceeded 16 KB AWS user-data limit AFTER base64 expansion (33%) | First-attempt launch reject | `feedback_aws_user_data_size_preflight` codified + CHECKLIST #116; S3-externalization fallback for >12 KB raw |
| #23 | B1021 monitor lifecycle | Monitor armed via Monitor tool pre-launch | Monitor tool timeout expired 1 hour later before B1024 instance launched; monitor must arm AT event boundary not pre-launch | B1021 -> B1024 instance gap | `feedback_monitor_arm_at_event_not_pre_launch` + CHECKLIST #117 |
| #24 | B1042 | "Layer 1+2 engine_state.json emit + B1019 monitor wire SHIPPED" | Schema mismatch between engine emit and monitor read; PID captured via `tee` was wrong PID; 13 BLOCKERS in adversarial review | Council 137 Sub-A 9 BLOCK + 14 WARN + 21 NIT adversarial audit (owner-mandated) | B1043 13-blocker staged fix + 14 new tests; pyramid 905+2 GREEN |
| #25 | B1043 | (Same class as #19 + #24) Layer-1+2 design vs SCHEMA-LEVEL armed | Third recurrence of `feedback_monitor_design_vs_operational_gap` in 24 hours | Owner-mandated comprehensive adversarial review | Council 138 STAGED-FIX-+-SMOKE; Sub-B holdout_guard wired; Sub-C MAX_MIN raised |
| #26 | B1044 META | Procedural rules (CHECKLIST #121 monitor-armed grep) sufficient to prevent design-vs-armed | CHECKLIST #121 grep matched LOOSE PROXIES (sync_loop, phase_watchdog) while actual B1019 invocation was just a COMMENT; the check ITSELF was design-vs-armed | Council 139 first-principles lens | Council 139 Option-8 HYBRID STRUCTURAL FIX: producer-consumer registry (`docs/PRODUCER_CONSUMER_PAIRS.md`) + schema-contract tests (`test_schema_contracts.py`) + two-tier status discipline (DESIGNED-NOT-VERIFIED default; OPERATIONALLY-VERIFIED requires evidence) + `feedback_designed_vs_verified_requires_evidence_artifact` + CHECKLIST #126 |
| #27 | B1045 | B1043 Sub-B `holdout_guard` wire at engine entry was correctly scoped | Phase C v2.5 smoke FAILED 1 second after RUNNING with `HoldoutViolationError`; holdout_guard was OVER-AGGRESSIVE - designed to protect AGENT TRAINING from OOS peek, but Phase 1A-β backtest IS the legitimate OOS evaluation | AWS smoke (CHECKLIST #127 validating itself at $0.49) | `run_phase1a.py` switched to `HoldoutUnlock` context manager with explicit reason `phase_1a_beta_backtest_evaluation_per_design`; preserves enforcement for rogue callers |
| #28 | B1047 | Phase C v2.5b smoke PASS cited as evidence in Council 142 retrospective | v2.5b PASS was MEDIUM gap: cited but NOT PERSISTED; no evidence artifact existed on disk | Council 142 sub-agent caught the gap | NEW `output_audit/phase_c_v2_5b_smoke_pass_2026_06_28.txt` artifact persisted same batch; CHECKLIST #126 evidence-artifact requirement reinforced |
| #29 | B1049 | Phase D B1048 preflight invocation expected to run | `PHASE_DIR` variable was set ONLY INSIDE `run_phase()` function which hadn't been called yet at preflight; under `set -uxo pipefail`, unbound var errored -> `\|\|` fallback fired `B1019_PREFLIGHT_FAIL` sentinel + shutdown; preflight Python script NEVER RAN on AWS | B1048 HALT sentinel chain (~$0.50 detected at smoke gate per CHECKLIST #127) | `scripts/launch_r5_master_4y_v2.sh` preflight invocation replaced `${PHASE_DIR}/...` with literal `output_phase_1/...` + `mkdir -p` before invocation; 3 new tests (`test_b1049_launch_script_var_scope.py`) scan for `PHASE_DIR` references outside `run_phase()` and assert literal-path pattern |

**Gap acknowledgment (per Sub-Charlie directive):** The numbered series begins at #12 in commit message references. Pivots #1–#11 are referenced cumulatively in commit messages and CLAUDE.md banner but were not numbered in commits when they happened - they were back-counted when Council 100 (B1000) introduced the running tally. Treating them as opaque early-session honest-finding events is more accurate than fabricating per-pivot descriptions. The pivot pattern matured during the session itself; the numbering scheme stabilized only at B1000 onward.

---

## 6. R6 Onboarding - How to Use This in R6

**Turn 1:** Read this doc. Read `COUNCIL_PATTERN_GUIDE.md`. Read `LEARNINGS.md` L165–L176 (the pivot-class learnings).

**Turn 2:** Initialize a session pivot counter at #0. Any retraction in R6 gets #1, #2, #3...

**Turn 3:** When the first pivot fires, write its commit message in the exact format from Section 4. Cite the memory rule. Add a pyramid test if the class is catch-able.

**Standing rules from turn 1 onward:**

- Do not state a WIRED / ARMED / INTEGRATED / RESOLVED claim without a linked evidence artifact per CHECKLIST #126
- Do not cite a banner status without re-deriving it that turn (Council 76 banner-verification precedent)
- Do not cite a previously-passing test as evidence without re-running the relevant tier (focused pyramid is NOT a substitute for the 13-tier pyramid on lint-class tests; see #14)
- Do not assume that a procedural rule will catch the class; assume the rule has the same design-vs-armed problem and look for the structural fix (#26 lesson)

**R6 success criterion:** if R6 ends with 0–3 pivots, the session was either trivial or hiding pivots. If R6 ends with 30+ pivots, the structural fixes aren't catching their classes. The healthy range is roughly 5–15 pivots in a multi-batch R6, each one paired with a pyramid test that catches the class going forward.

---

## 7. Anti-Patterns (Do Not Do These)

- **Hiding pivots in compliance footers.** A pivot deserves its own numbered call-out in the commit subject and body. Burying "(also caught a small issue with X)" in the OWNER-RULE-COMPLIANCE block silently strips the audit trail.
- **Renaming bugs to features.** "The engine ran without monitoring for 1h 38m" is a pivot. "The engine ran in low-overhead autonomous mode" is the same fact dressed up to dodge the pivot.
- **Defending a wrong claim.** When the owner says "X is wrong", pivot. Do not re-argue the original claim by citing context that the owner already knows. Re-arguing is the pattern `feedback_audit_recommendations_against_existing_directives` was codified to prevent.
- **Numbered-rollback.** Do not adjust the pivot count downward when retrospectively merging two pivots into one. The cumulative count is a session-quality metric; rolling back hides the recurrence rate.
- **Pivot without test.** Every pivot whose class is catch-able by pyramid MUST add the test. B1014/B1043/B1044/B1049 each shipped tests. A pivot without a class-test means the class will recur.
- **Class blindness.** When two pivots fire in close succession on similar mechanisms (e.g., #19 + #24 + #25 = three design-vs-armed instances in 24 hours), the next council MUST treat it as a class problem and look for the structural fix (B1044 Council 139 Option-8). Not doing this is what owner fatigue is.

---

## 8. The Honest-Finding Pivot as Project Safety Net

The council pattern (Doc D) catches mistakes BEFORE they ship. The honest-finding pivot catches mistakes that slipped past the council. Together they form a two-stage filter:

```
Recommendation -> Council -> Ship -> [empirical check / owner / sub-agent / pyramid] -> Pivot if wrong
                  ^                                                                       |
                  |                                                                       |
                  +-- Memory rule + CHECKLIST item added per pivot class <-----------------+
                       (next session inherits the class-catch via the council brief)
```

R6 inherits 29 R5 pivot classes via this folder + LEARNINGS.md + memory rules. If R6 introduces 0 new pivot classes, the project has reached a stable design-vs-armed-free state. If R6 introduces 1–3 new classes that themselves become pyramid-catch-able, the meta-system is working. If R6 introduces more than 5 new classes without structural fix, the council-pivot loop needs revision and a Council 139-equivalent first-principles re-design is warranted.

---

**End of Honest-Finding Pivot Pattern Guide.**
