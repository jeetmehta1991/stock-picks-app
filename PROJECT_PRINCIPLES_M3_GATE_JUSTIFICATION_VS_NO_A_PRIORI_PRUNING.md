<!-- Source: per CHECKLIST #77 canonical-source; Council 287 B1233 2026-07-07 doc-sync sweep -->

<!-- 🟢 COUNCIL 278-287 SYNC BANNER (B1233 2026-07-07) — READ FIRST BEFORE THIS DOC -->
> **Doc-sync status:** This document may contain references stale as of 2026-06-27 or earlier. The current state below overrides any stale references in the body until the next full-rewrite.
>
> **Current canonical values (as of 2026-07-07 B1231):**
> - `len(ALL_STRATEGIES) = 219` (was 220 pre-B1189 DELETE of dxy_headwind_multinational_short; was 221 pre-B874)
> - `STRATEGIES_DISABLED_MISSING_PRODUCER = set()` (was `{dxy_headwind_multinational_short}` pre-B1189)
> - Active strategies for Phase 1A-β cube: 219; cube cells 219×26 = 5,694
> - Test count: **858 passed, 2 skipped** on `test_unit.py + test_integration.py`
> - **CHECKLIST items:** #1–#157 (added #151-#157 in Councils 279-285)
> - **LEARNINGS lessons:** through L202 (added L197-L202 in Councils 279-285)
> - **Latest batch:** B1231 (Council 285)
>
> **Recent Council 278-287 milestones (chronological):**
> - Council 278 (B1188-B1204): 40 SKIP strategies loosened per CSV recommendations
> - Council 279 (B1205-B1210): 11 silent misses remediated + L197 + CHECKLIST #151-#153
> - Council 280 (B1211-B1213): News coverage refined (84.2%) + CHECKLIST #154 codified
> - Council 281 (B1214-B1216): short_interest_pct producer bug + institutional 30% gap surfaced
> - Council 282 (B1217-B1219): Cross-audit 192 strategies + CHECKLIST #155
> - Council 283 (B1220-B1223): 5 more producer audits + comprehensive report
> - Council 284 (B1224-B1228): All 25+ producers audited + historical 2020-2023 spot-check + L201 + CHECKLIST #156
> - Council 285 (B1229-B1231): 2 critical bugs FIXED with graceful degradation + L202 + CHECKLIST #157
> - Council 287 (B1232-B1236 in progress): Stage 4 walks archived + doc-sync sweep
>
> **Stage 4 walks: ARCHIVED 2026-07-07 to `archive/2026-07-07-stage-4-walks-complete/`** (Council 121+ 2026-06-27 owner-approved completion). Any `STAGE_4_*.md` reference in this doc now points to archived location.
>
> **Producer coverage (all 25+ producers audited Councils 280-284):**
> - news_sentiment 84.2% / short_interest_dtc 97.7% / **short_interest_pct 0%** (bug; graceful-degradation fix in B1229) / pead 85% / insider 18.8% (event-rarity) / **institutional_signal 85%** (B1230 corrected from B1216's 30% misattribution) / congressional 67.7% / sec_edgar 97.7% / search_volume 99.2% / index_rebalance 10.5% (event) / earnings_yoy 78.9% / cot_positioning 100% / cross_asset 100% (5 fns) / calendar_effects 100% / macro_events 100% / OHLCV-derived (chart_patterns/technical/dec513/multi_timeframe/cross_sectional/ict_producers/volume_profile/smc_ict/pairs_trading) all 100% (bounded by ~84% OHLCV cache)
> - **Critical historical finding (B1227):** news_sentiment 0% in 2020; short_interest_dtc 0% in 2020; institutional 0% in 2020-2021. Backtest interpretation must annotate producer coverage TIMELINE.
>
> **Sprint 5 tickets queued (post-Council 285 priorities):**
> - S5-B1214-SHARES-OUTSTANDING (HIGH; 1 strategy; 1d) - remove B1229 fallback when data ships
> - S5-B1216-INSTITUTIONAL-13F (MED after B1230 correction; 1 strategy; 1-2d) - expand T1a persistence file
> - S5-B1212-SECONDARY-NEWS (MED; 6 strategies; 2d) - Finnhub/AlphaVantage fallback
>
> **Comprehensive coverage report:** `output_audit/PRODUCER_COVERAGE_COMPREHENSIVE_REPORT.md`

---

# M3 Project-Principles Memo: Gate-Justification Soft-Discipline vs No-A-Priori-Pruning

# per CHECKLIST #77 + #94 + #107
# Source: B769 council inline-council Reviewer 4 + chairman M3 unanimous-missed
# Source: backtest tickets #60 (gate-justification soft-discipline) + #61 (this memo)
# per memory: feedback_no_a_priori_strategy_pruning.md + project_no_apriori_strategy_pruning.md

## Purpose

Resolve the tension surfaced in B769 council Reviewer 4 + chairman M3: **codifying "gates need conditional-return evidence" before cube runs IS itself an a-priori-pruning rule**, which conflicts with the project's standing `feedback_no_a_priori_strategy_pruning.md` directive and the cube-authoritative principle.

This memo precedes ticket #60 (gate-justification soft-discipline codification) per B769 chairman tier order. The principle is correct; the codification mechanism needs the right shape to NOT become an a-priori filter on strategy registration.

## The conflict in concrete terms

**Pro-principle (B358 lesson + Reviewer 1):**
> "Gates must be justified by conditional-return evidence, not by 'trend confirmation sounds good'. A gate that 'feels' like prudent trend-confirmation can actively destroy a factor strategy's edge by mis-timing it against the regime where the factor actually pays."

The B358 case study: removing a 200-EMA bull-regime gate from `xs_low_beta_long` because cell-audit data showed -6.22% loss in neutral regime when the gate let it fire. **Evidence-based gate removal is correct.**

**Anti-mechanism (Reviewer 4 + the project's standing rule):**
> "Codifying 'gates need conditional-return evidence' before cube runs is itself a meta-gate that could prune strategies before they reach the cube."

The project's standing `feedback_no_a_priori_strategy_pruning.md`: "no a-priori strategy pruning — empirical validation over literature filtering... A strategy may be re-pruned only with empirical evidence from a completed run."

**The tension:** if we require "conditional-return evidence" BEFORE allowing a gate addition, we're implicitly requiring that evidence exist. For new strategies, that evidence doesn't yet exist (cube hasn't run). So either:
(a) No new gates can be added (impossible — kills strategy design),
(b) Some gates get added without pre-cube evidence (then the principle is unenforced), or
(c) The principle applies only POST-cube, not pre-cube (then it's not really a CHECKLIST item).

## Resolution: distinguish 3 scenarios

The principle applies differently in three concrete scenarios. The CHECKLIST codification should be scoped to scenarios 2 + 3, NOT scenario 1.

### Scenario 1 -- NEW STRATEGY DESIGN (Class 7 NEW + initial wiring)

When creating a new strategy or wiring its initial gates, **conditional-return evidence DOES NOT YET EXIST**. The cube hasn't seen this strategy. Requiring such evidence would block all new strategy creation -- which the chairman did NOT recommend and the council did NOT intend.

**Resolution:** New strategies are NOT subject to pre-cube gate-justification CHECKLIST. They must satisfy minimum-gate hygiene (each gate has a stated PURPOSE in the docstring + cites literature or rationale), but conditional-return evidence is GATED to cube outputs, not pre-cube.

The B271 family-bug regime-affinity audit + the B608/B609 silent-gap defaults sweep + the B632 positive-symmetric signals additions are all examples of post-cube + post-discovery refinements -- they do NOT block new-strategy creation.

### Scenario 2 -- GATE-ADDITION TO EXISTING STRATEGY (post-walk modifications)

When modifying an existing strategy (e.g., adding a trend gate, tightening a threshold, swapping a STATE for an EVENT signal), the strategy HAS prior data (B660 measurement + any cube run). **Conditional-return evidence CAN be required for these modifications.**

**Resolution:** Apply gate-justification soft-discipline ONLY to existing-strategy modifications. The pre-flight question becomes: "What conditional-return hypothesis does this gate addition imply? What's the post-modification fire-count projection? What's the validation plan?" Without those answers, the modification doesn't ship.

The B358 EMA-gate removal exemplifies this: cell-audit data showed -6.22% loss in neutral regime -> evidence-driven gate REMOVAL. Same template applies to gate-addition.

### Scenario 3 -- GATE-REMOVAL ON EVIDENCE OF HARM

When evidence emerges that an existing gate is harming a strategy (per-regime negative-EV measurement, autocorrelation-driven false positives, fire-starvation due to AND-stack collinearity), **the principle says REMOVE THE GATE** -- not defend it on "feels prudent" grounds.

**Resolution:** This scenario is mandatory NOT optional. It's the inverse of scenario 2. The CHECKLIST item: gate-keeping requires evidence of help, not evidence of absence-of-harm.

Cases the project has already handled this way:
- B358 200-EMA gate removed from xs_low_beta_long (cell-audit evidence of regime-mistiming)
- B654 W8 cpr_narrow tightened from 0.15 to 0.05 (extreme NO-OP at 87% True)
- B655 T10 supertrend redundancy fix (99.19% True extreme NO-OP)
- B663 default-True silent-gap sweep (200-EMA gate inadvertently auto-passing)
- B741 redundancy diagnostic deletes per fire-bar correlation evidence
- B722 Pattern W deterministic-duplicate deletions per identical-gates evidence

## The CHECKLIST codification (scoped soft-discipline)

The CHECKLIST item -- as per ticket #60 -- should read approximately:

> **CHECKLIST #108 (PROPOSED) -- Gate-modification justification (POST-walk; NOT pre-registration).** Every turn that ADDS, REMOVES, or REPLACES a gate on an EXISTING strategy must surface:
> (a) **Conditional-return hypothesis** (what regime/scenario does this gate help/hurt?)
> (b) **Fire-count projection** (post-modification fires/year per regime; flag if below min_trades=30)
> (c) **Validation plan** (what cube cell / regime-conditional measurement confirms the hypothesis post-cube?)
> (d) **Literature or empirical precedent cited** (Bulkowski / Nison / B358 / B658 etc.)
>
> **NOT REQUIRED FOR:** Class 7 NEW strategy initial wiring (no prior empirical history); urgent silent-gap fixes (Pattern F default-True bugs); producer-side fixes (NaN handling, lookback init); pure mechanical refactors (variable rename, function-signature change).

This is the soft-discipline shape. It:
- Applies to gate MODIFICATIONS on EXISTING strategies (Scenario 2 + 3)
- Does NOT apply to new strategy registration (Scenario 1; consistent with `feedback_no_a_priori_strategy_pruning`)
- Requires evidence FORWARD-LOOKING (hypothesis + validation plan), not evidence BACKWARD-LOOKING (literature only)
- Allows urgent fixes without ceremony (silent-gap + producer-side; matches B663 + B774 precedents)

## What this DOES and DOES NOT change

**This memo does NOT change:**
- `feedback_no_a_priori_strategy_pruning.md` standing rule. Strategies are still NOT pruned a-priori. The DEPRECATED_STRATEGIES set stays empty pending cube verdicts.
- The cube-authoritative principle. Final PASS/FAIL on a strategy is determined by cube measurement, not pre-cube design.
- Class 7 NEW wiring. New strategies still ship same-turn per `feedback_wire_new_strategies_on_the_spot.md`.

**This memo DOES change:**
- Gate modifications on EXISTING strategies (Scenarios 2 + 3) now require pre-flight justification per the proposed CHECKLIST #108. Both gate-additions AND gate-removals require evidence -- removing a gate "because the cluster walk said so" is not enough without evidence of harm.
- The interpretation of B358 generalizes: the same template (cell-audit evidence -> gate-removal) is the documented path for all gate modifications, not just the B-29 walk.
- Council Reviewer 1's "all factor strategies need the B358 template applied" becomes operationalizable.

## Why the council got this almost-right-but-not-quite

External council F2 asserted: "Codify into CHECKLIST: gates must be justified by conditional-return evidence, not by 'trend confirmation sounds good'."

Reviewer 4 critique: "codifying 'gates need conditional-return evidence' before cube runs is itself a meta-gate that could prune strategies before they reach the cube."

**Both are correct in different scopes.** The council was right about the principle. Reviewer 4 was right about the mechanism. The resolution is to scope the principle to gate MODIFICATIONS (which have prior empirical context) rather than to new-strategy gate REGISTRATIONS (which don't).

Reviewer 4's blanket rejection would over-block legitimate gate-audit work (B358 / B654 / B655 / B722 are all good precedents). The council's blanket codification would under-block the Scenario 1 case where new strategies need fresh design freedom.

The 3-scenario resolution above honors both concerns.

## Unblocking ticket #60

Per B769 chairman tier order: #61 M3 memo precedes #60 gate-justification soft-discipline codification. With this memo shipped (B776), ticket #60 is UNBLOCKED. The #60 implementation should:
1. Add the proposed CHECKLIST #108 text (or owner-preferred variant) to `CHECKLIST.md`
2. Reference this memo in #108 for scoping clarification
3. Add a per-turn pre-flight format template for gate-modification work
4. Update the relevant memory files (`feedback_no_a_priori_strategy_pruning.md`) with a cross-reference to scoped-soft-discipline distinction

## Compliance with existing rules

- `feedback_no_a_priori_strategy_pruning.md` -- COMPATIBLE: this memo explicitly excludes new strategy registration from the soft-discipline; existing strategies' gate modifications were already subject to evidence-based decisions (B358 etc.)
- `feedback_minimum_fire_count_gate_before_cube.md` -- REINFORCED: the proposed CHECKLIST #108(b) makes fire-count projection a per-turn requirement for gate modifications
- `feedback_narrow_scope_blast_radius.md` + `feedback_local_changes_default_global_needs_approval.md` -- ALIGNED: per-strategy gate modifications are LOCAL-scope by default; this memo doesn't expand that
- `feedback_wire_new_strategies_on_the_spot.md` -- PRESERVED: Class 7 NEW wiring stays same-turn, no pre-flight ceremony added
- `feedback_data_consumption_audit_must_apply_checklist_44b.md` -- COMPLEMENTARY: data-consumption audit and gate-justification are different audit classes; this memo doesn't override #44(b)

## Memo status

This memo SUPERSEDES the council's blanket F2 framing. Owner can either:
(a) Adopt this memo's 3-scenario scoping + proceed with #60 CHECKLIST codification per the proposed #108 text
(b) Reject this memo + revert to council's blanket framing (with #60 adjusted to broader scope)
(c) Adopt with modification (specify which scenarios trigger pre-flight)

Default (per B769 chairman): (a) -- proceed with #60 codification per this memo's scoping.

## CHECKLIST + memory compliance

- CHECKLIST #44(b) -- N/A (not a data-consumption audit)
- CHECKLIST #67 -- doc-sync (memo authored + queue annotation same turn)
- CHECKLIST #77 -- canonical-source headers
- CHECKLIST #94 -- queue-mandatory-per-turn
- CHECKLIST #105 -- N/A (not a producer/strategy walk)
- CHECKLIST #106 -- N/A
- CHECKLIST #107 -- findings-vs-tickets reconciliation (this memo IS the #61 finding shipped)
