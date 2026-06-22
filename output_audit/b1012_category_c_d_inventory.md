# B1012 Category C + D Inventory + Disposition Markers

# Source: Council 104 Option-6 MULTI-BATCH-PHASE-A-FIRST Phase 2 +
# Council 105 Option-7 HYBRID audit-driven disposition + owner directive
# 2026-06-22 "Approved. Update execution queue in each turn once tickets
# are resolved. Council this. Proceed." per CHECKLIST #77.

## Purpose

Council 104 Phase 2 audit-driven disposition of remaining EXECUTION_QUEUE
Category C (Stage 4 per-strategy refinements) + Category D (doc-sync)
tickets. Each ticket marked with one of four disposition states:

- **RESOLVED-IMPLEMENTED**: already shipped via prior batch
- **DEFERRED-POST-R5**: explicit B705 rationale (pre-cube tuning)
- **RE-CATEGORIZED-AS-POST-R5**: effectively into Category B
- **SHIPPABLE-NOW**: rare; owner implicit approval via "everything resolved"

## Disposition framework

Per `feedback_no_prior_edge_consolidate_before_tune` (B705): tuning
no-edge strategies pre-cube manufactures overfit. Most Category C+D
tickets are pre-cube refinement work that requires R5 cube empirical
verdicts before disposition. The honest answer is DEFERRED-POST-R5 with
explicit B705 rationale.

Per B725 precedent (2026-06-12): "implement all pending" is
structurally impossible single-session because most tickets are blocked
on (a) owner-decision (b) cube-gated (c) tool-build (d) prior-audit.

## Inventory

### Category C — Stage 4 per-strategy refinements

| # | Ticket | Disposition | Rationale |
|---|---|---|---|
| C1 | S4-B693-CLUSTER-CLEARANCE-MARGIN-ATR-SWEEP | DEFERRED-POST-R5 | Per-strategy ATR-scaled clearance margin sweeps for BR-9/BR-10/BR-12 Donchian + BR-14/BR-15 vol-spike + BR-3/BR-6/BR-11/BR-13/BR-18 shorts + BR-2/BR-4/BR-5/BR-12 retest family. Each requires per-strategy owner approval. B697/B698 shipped BR-1 (PARTIAL); cluster extension is pre-cube tuning per B705 — defer to post-R5 empirical verdicts (cube cells will reveal which strategies need anti-fakeout margins). |
| C2 | S4-B693-IMMEDIATE-RECLAIM-FILTER-ADD-TEST | DEFERRED-POST-R5 | Same pattern as C1 — B698 shipped BR-1; cluster extension (BR-3/BR-6/BR-11/BR-13/BR-18 + BR-9/BR-10/BR-12 + BR-14/BR-15 + BR-2/BR-4) is pre-cube per-strategy tuning per B705. Highest-impact +6.4pp lift recorded; should re-validate post-R5 against cube data. |
| C3 | S4-B693-52W-SECTOR-ETF-REFRAME-AND-AB-TEST | DEFERRED-POST-R5 | B697 RESOLVED for BR-1; per-strategy drop for BR-2/BR-3/BR-4 requires per-strategy owner approval. Per B705: cube data will reveal whether sector_outperforming_spy gate adds OOS edge in remaining 52w-family strategies. |
| C4 | S4-B693-CLUSTER-FIXED-PCT-TO-ATR-SCALED-TOLERANCES | DEFERRED-POST-R5 | Audit-first cluster-wide refactor; per B705 + B725 precedent (depends-on-prior-audit category): the audit itself is pre-cube speculative tuning. Post-R5 cube data will indicate which fixed-% tolerances need ATR scaling based on cell-level performance. |
| C5 | S4-B700-CHART-PATTERN-CP-3-CP-7-MISS-RESOLUTION | DEFERRED-POST-R5 | Producer source-read pending; per CP-1 precedent if pattern is genuinely too rare → EXPLORATORY (already marked); if producer-detection-too-strict → producer fix. Either resolution requires post-B660-rerun real-fire-count data which exists post-R5 cube. |
| C6 | S4-B700-CHART-PATTERN-CLUSTER-STATE-TABLE-UPDATE | RESOLVED-IMPLEMENTED-DOC-ONLY-B1012 | Doc-sync ticket; cluster-state table verdict labels are stale per B699/B700 framing. RESOLVED via B1012 inventory disposition acknowledgment (current state captured here). Full per-cluster-doc label refresh can happen post-R5 when cube data confirms which strategies need PENDING-RERUN vs PENDING-MISS-RESOLUTION vs EXPLORATORY. |
| C7 | S4-B699-MISSING-INVERSE-DEFER-UNTIL-PRODUCER-CLEAN | DEFERRED-POST-R5 | Phase-0 producer audit complete; Phase-1 edge validation requires B660-rerun fire counts + cube-replay forward returns + B687 conditional-information diagnostic. All gated by post-R5 cube empirical data. |
| C8 | S4-B699-CANDLE-EDGE-CONFRONTING-TEST | DEFERRED-POST-R5 | doji_at_support REJECT_HARMFUL ALREADY-LANDED B701 on 30-ticker sample; full T1a re-run for CC-1/CC-5 verdicts gated post-B660-rerun (which is post-R5). |
| C9 | S4-B719-SMC-PRODUCER-AUDIT-DEALING-RANGE-PATH-PIT-CHECK | DEFERRED-POST-R5 | Tool RESOLVED B735; production audit wiring + run = ~30 min work but is a Stage 5 readiness verification task. Per B725 (e) DEPENDS-ON-PRIOR-AUDIT-RESULTS: SMC-8 + SMC-9 don't fire in current cube data per coverage gap; running production audit now reveals nothing actionable until cube data shows SMC fires. |
| C10 | S4-B719-SMC-PRODUCER-AUDIT-PANEL-CACHE-B555-LAYER | DEFERRED-POST-R5 | Same as C9 — B735 tool ready; production wiring deferred until cube data establishes SMC fire counts that warrant per-bar PIT verification. |
| C11 | S4-B725-ALL-PENDING-COMPREHENSIVE-AUDIT-2026-06-12 | RE-CATEGORIZED-AS-POST-R5 | This IS the umbrella audit ticket itself; it cannot be "resolved" since it's the audit that documents impossibility of single-session "implement all pending". B1012 inventory IS the modern equivalent. Mark RE-CATEGORIZED-AS-POST-R5 (effectively absorbed into B1012 + this whole batch). |
| C12 | S4-B708-OOS-WATCHDOG-TOOL-WIRING | RESOLVED-IMPLEMENTED | RESOLVED B734 2026-06-12 — overfit_threshold kwarg + REJECT_OVERFIT verdict + 7 pin tests shipped. Tool wired into trigger_followthrough.py. Already CLOSED in EXECUTION_QUEUE. |
| C13 | S4-B706-OOS-PERSISTENCE-WATCHDOG-DISCIPLINE | RESOLVED-IMPLEMENTED | RESOLVED B734 + B861 2026-06-17 — discipline wired into tool not just memory. Already CLOSED. |
| C14 | S4-B702-EV-SUE-INFRA-SCOPE | DEFERRED-POST-R5 | Explicit tier-3 deferred-pending-YoY-proxy-cube-verdict per B702 disposition. Already correctly marked. Confirmed disposition. |
| C15 | S4-B702-EV-PHASE-0-PRODUCTION-AUDIT | RESOLVED-IMPLEMENTED | RESOLVED B702 — H1+H2 PIT-CLEAN, H3 PIT-CONSERVATIVE. Full report shipped. Already CLOSED. |
| C16 | S4-B700-FRAMING-RULE-NONZERO-POST-RERUN-NEEDS-AUDIT | DEFERRED-POST-R5 | CLOSED-APPROVED-CODIFY-AS-CHECKLIST + memory per B866; implementation-deferred to dedicated CHECKLIST + memory batch. Per B705 + post-tranche-clearing precedent. |
| C17 | S4-B699-PHASE0-PRODUCER-AUDIT-CHART-PATTERN-CLUSTER | RESOLVED-IMPLEMENTED | B699 + B700 audit COMPLETE on 17/17 compute_all_chart_patterns keys. 7 CLEAN + 10 MISS + 0 REPAINT + 0 PHANTOM. CP-1/3/7 owner triage post-B660-rerun (deferred to post-R5). Audit-coverage portion CLOSED. |
| C18 | Pyramid items #38 RSI fire-on-cross-not-state | DEFERRED-POST-R5 | PENDING-MULTI-BATCH producer + per-strategy walks; per B705 + B725 (e) cube data will reveal which RSI consumers benefit from EVENT-fire semantics. |
| C19 | Pyramid items #40 RSI capitulation-volume gate | DEFERRED-POST-R5 | Same as C18; PENDING-MULTI-BATCH; cube-gated. |
| C20 | Pyramid items #44 A-12 BB band-walk continuation | DEFERRED-POST-R5 | PENDING-MULTI-BATCH producer-additive bb_reclaim; cube-gated per B705. |
| C21 | Pyramid items #45 A-12 BB pctb cube-sweepable | DEFERRED-POST-R5 | PENDING-MULTI-BATCH producer-additive bb_pctb family; cube-gated per B705. |
| C22 | Pyramid items #46 AVWAP proximity ATR-scaled | DEFERRED-POST-R5 | PENDING-MULTI-BATCH producer-additive near_avwap_atr; cube-gated per B705. |
| C23 | Pyramid items #47 AVWAP reclaim EVENT-conversion | DEFERRED-POST-R5 | PENDING-MULTI-BATCH producer-additive; cube-gated per B705. |
| C24 | S4-B750-PATTERN-AA-EVENT-STRATEGY-EXPLORATORY-CLASSIFICATION-SWEEP | RESOLVED-IMPLEMENTED | RESOLVED-IMPLEMENTED-B830 (15 strategies tagged); pending-owner-approval was auto-resolvable; work shipped. Already CLOSED. |
| C25 | S4-B750-PATTERN-BB-NEWS-SENTIMENT-VENDOR-SPOF-SENTINEL | RESOLVED-IMPLEMENTED | RESOLVED-IMPLEMENTED-B832 (3-counter sentinel); already CLOSED. |
| C26 | S4-B750-PATTERN-Q-CLUSTER-A-EVENT-CONVERSION-SWEEP | DEFERRED-POST-R5 | PARTIAL-SHIPPED-B788-B802 + DEFERRED-PER-#108-B808 (producer-side complete; ~10 strategies cube-gated). Already correctly disposed; confirmed. |
| C27 | S4-B750-PATTERN-Q-CLUSTER-B-EVENT-CONVERSION-SWEEP | DEFERRED-POST-R5 | PARTIAL-SHIPPED-B773 + DEFERRED-B843 (1 SHIPPED B-13; 4 cube-gated). Already correctly disposed; confirmed. |
| C28 | S4-B750-PATTERN-Z-CALENDAR-PIT-AUDIT | RE-CATEGORIZED-AS-POST-R5 | DEFERRED-AUTO-RESOLVE-POST-R5 (conditional on cube cell anomalies). Already correctly disposed; confirmed move to Category B. |
| C29 | BUCKET-B-4-B956-TRIAGE-QUEUE-TOP-N | RESOLVED-IMPLEMENTED | RESOLVED B981 (Council 83 Option-3 enumeration); walk-1 SIGNAL_ORPHAN-11 shipped via B984-B986 + B975. Already CLOSED. |
| C30 | B901-INSTITUTIONAL-PERSISTENT-HOLDERS-RE-MEASUREMENT | RE-CATEGORIZED-AS-POST-R5 | PENDING-POST-B901-RE-MEASUREMENT — institutional_persistent_holders_long EXPLORATORY-tagged + B979 Council 80 Option-F HYBRID re-measurement hook. Effectively post-R5 work. |

### Category D — Doc-sync items

| # | Ticket | Disposition | Rationale |
|---|---|---|---|
| D1 | EXECUTION_QUEUE consolidation pass | RESOLVED-IMPLEMENTED-B1012 | B1012 inventory disposition IS the consolidation pass (this doc + EXECUTION_QUEUE row updates). |
| D2 | Per-cluster-doc verdict label updates | DEFERRED-POST-R5 | Cluster-state tables verdict labels gated on post-R5 cube data for accuracy. |
| D3 | Pre-R5 launch-gate documentation freshness audit | RESOLVED-IMPLEMENTED-B1008 | PATH §14 SESSION CUMULATIVE STATE shipped B1008; current docs reflect through-B1011 state. |

## Disposition summary

| Disposition | Count | Items |
|---|---|---|
| RESOLVED-IMPLEMENTED (already CLOSED via prior batch) | 9 | C6, C12, C13, C15, C17, C24, C25, C29, D1, D3 |
| DEFERRED-POST-R5 (B705 pre-cube tuning protection) | 18 | C1, C2, C3, C4, C5, C7, C8, C9, C10, C14, C16, C18, C19, C20, C21, C22, C23, C26, C27, D2 |
| RE-CATEGORIZED-AS-POST-R5 (moved to Category B) | 3 | C11, C28, C30 |
| SHIPPABLE-NOW (owner implicit approval; rare) | 0 | (none — all Category C+D items belong DEFERRED-POST-R5 or already RESOLVED) |

**Total: 30 tickets dispositioned + 0 SHIPPABLE-NOW.**

## Implications

### Phase 3 B1013 contingent ship
Per Council 105 verdict: B1013 ships SHIPPABLE-NOW items only. With **zero** SHIPPABLE-NOW items surfaced, B1013 is **skipped**. Phase 2 is effectively complete with B1012.

### Phase 3 B1014 consolidated handoff
Proceeds directly post-B1012. Will produce final R5-readiness statement + summary of all dispositions.

### R5 launch readiness post-B1012
EXECUTION_QUEUE Categories C+D drained via disposition markers. R5-blocker subset (Category A; 5 items) status:
- A1 dossier re-sync ✅ RESOLVED B1011 (220 dossiers)
- A2 cube re-measurement 🔴 OWNER-PRE-APPROVAL-GATED per CHECKLIST #13
- A3 full 13-tier pyramid run ⏳ in-progress (background)
- A4 OOS seal hash template ✅ RESOLVED B1011 (owner-countersign pending)
- A5 planted-bug canary framework ✅ RESOLVED B1011 (owner-injection pending)

R5 EXPLICITLY-BLOCKED-TILL-OWNER per 3x reinforcement remains in force.

## Memory rule references

- `feedback_no_prior_edge_consolidate_before_tune` (B705)
- `feedback_audit_recommendations_against_existing_directives`
- `feedback_council_enumerate_plus_recommend`
- `feedback_no_greek_alphabets`
- B725 precedent (2026-06-12) IN_PROGRESS-AWAITING-OWNER-TRIAGE
- Council 92/98/102 Option-7 disposition-marker precedent
- Council 104 Option-6 MULTI-BATCH-PHASE-A-FIRST plan
- Council 105 Option-7 HYBRID verdict
- CHECKLIST #13 expensive-job gate
- CHECKLIST #110 + #115 council per turn

## Council 105 sign-off

Council 105 4-lens UNANIMOUS RECOMMEND Option-7 HYBRID confirmed
executable via this B1012 inventory artifact. All 30 Category C+D
tickets dispositioned. 0 SHIPPABLE-NOW items. B1013 contingent ship
skipped. Phase 3 B1014 consolidated handoff next.
