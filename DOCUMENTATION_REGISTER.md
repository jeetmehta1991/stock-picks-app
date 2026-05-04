# DOCUMENTATION_REGISTER

**Purpose:** Per owner Pass 52 turn 98 directive — track all RESOLVED-DECIDED decisions that are documentation-only / cross-reference / no-engineering-work-required, scheduled for execution AFTER decision-walkthrough phase completes.

**Companion to:** ENGINEERING_REGISTER.md (engineering work) and IMPLEMENTATION_READINESS_DASHBOARD.md (sprint readiness gate).

**Established:** Pass 52 turn 99 (retroactive sprint-tracking audit fix)

---

## Categories

Documentation-only decisions fall into:

1. **Cross-reference / absorbed** — work tracked via parent or joint decision; this entry is a documentation pointer
2. **Foundational integrated** — early structural decisions (DEC-001 to DEC-010 era) already integrated into project structure; no separate execution needed
3. **Stage-deferred operational** — Stage 3+ or Stage 4+ scope; document now for future-stage execution
4. **Cross-reference enrichment** — adds context to existing decisions (e.g., supersession notes, joint references)
5. **Methodology decisions** — pure decision text, no implementation artifact (e.g., "use library X over Y")

## Execution Plan

**Phase 1 (current):** Decision-walkthrough — Pass 52 working through PENDING decisions
**Phase 2 (post-walkthrough):** Documentation-register cleanup pass — execute all documentation-only items in order
**Phase 3 (parallel with Phase 2):** Sprint engineering work per ENGINEERING_REGISTER

Phase 2 timing: trigger when PENDING decisions reach 0 or owner directs.

---

## DECISION INVENTORY

*To be populated by retroactive sprint-tracking audit (Pass 52 turn 99 onward). Initial population covers homeless RESOLVED-DECIDED decisions found across all of Pass 52.*

### Bucket A: Foundational / Already-Integrated (no separate execution work)

These decisions were structural/foundational early-pass decisions already integrated into project shape (CLAUDE.md, PROJECT_PLAN.md content, etc.). No documentation-cleanup work required.

| DEC | Description | Why no execution |
|---|---|---|
| DEC-001 | Quiver subscription cancellation timing | Operational; superseded by DEC-450 paid Quiver |
| DEC-002 | Polygon News evaluation | Superseded by DEC-440/441 Polygon subscription |
| DEC-003 | Phase 0 inclusion in PROJECT_PLAN | Structural — already in PROJECT_PLAN.md |
| DEC-004 | Phase 0.A scope | Structural — defines project structure |
| DEC-005 | Strategy count target — 130 strategies + OpenBB+Polygon fundamentals | Superseded by Layer 1-4 strategy roster (~109-119 classes) |
| DEC-006 | Strategy families to defer to Phase 1F | Structural deferral; superseded by current Phase 0/1B-α structure |
| DEC-007 | Phase 0 timeline (7-12 months path to live) | Aspirational target; tracking via sprint roadmap |
| DEC-039 | Phase 0 parallelization (deferred) | Structural deferral |
| DEC-041 | No Phase 0 compression | Structural |
| DEC-046 | Drop CVD from Phase 0 | Structural decision (negative scope) |

### Bucket B: Methodology / Library Choices (no incremental execution beyond making the choice)

These decisions choose a library or methodology. The "execution" is using the chosen tool when relevant code is written, captured in respective sprint slots.

| DEC | Description | Library/method | Already captured in |
|---|---|---|---|
| DEC-047 | QuantStats for performance analytics | QuantStats | (used during Phase 1B-α / Stage 3) |
| DEC-048 | Streamlit for Stage 3+ dashboard | Streamlit | DEC-430 Sprint 7-8 dashboard |
| DEC-049 | ib_async for IBKR integration | ib_async | Stage 4+ broker integration |
| DEC-050 | freezegun for PIT regression tests | freezegun | DEC-437/439 in Sprint 6 |
| DEC-052 | Fork S&P 500 historical dataset (CC0) | CC0 dataset | DEC-365/366 universe |
| DEC-054 | IBKR for both paper and live | IBKR | Stage 3+/Stage 4+ broker setup |
| DEC-055 | Cost-optimized TradingAgents config | config | DEC-051/058 agent setup |
| DEC-056 | Skip TradingAgents CLI | architectural | DEC-051 baseline |
| DEC-057 | Disable Social Analyst | architectural | DEC-051 baseline |
| DEC-058 | GPT-5.4-mini for backtest, Anthropic for live | model selection | Stage 2/3 agent infrastructure |
| DEC-061 | Tier mapping (Option 1) | mapping decision | absorbed into DEC-021 (3-tier simplification) |

### Bucket C: Cross-Reference / Absorbed (work tracked via parent or joint decision)

These decisions point to other decisions where the actual work lives. No separate execution.

| DEC | Description | Tracked via |
|---|---|---|
| DEC-015 | Strategy correlation methodology | Used by DEC-089 Sprint 5+ / DEC-458 |
| DEC-068 | Bootstrap CI + pairwise significance for exits | Expanded in DEC-423 → Sprint 7 statistical methodology |
| DEC-073 | Hand-roll smart money composites (NOT Quiver pre-built) | Decision only — guides DEC-450 Quiver consumer code |
| DEC-265 | Smoke test power analysis | Absorbed by DEC-080/400/083/110/413/426 → Sprint 7 |
| DEC-347 | Lagging-indicator dominance | Absorbed by DEC-071/072/389-391/106/107 → various sprints |
| DEC-126 | Document time-resolution limits of circuit breakers | Documentation in CAV-XXX |

### Bucket D: Stage 3+ / Stage 4+ Operational (defer to that stage)

These decisions are scoped to Stage 3 (paper trading) or Stage 4+ (live). Documented now for future-stage execution; NOT in current sprint roadmap.

| DEC | Description | Stage |
|---|---|---|
| DEC-028 | Stage 3 paper trading duration (3 months) | Stage 3 entry criterion |
| DEC-029 | Stage 4 starting capital (SPLIT into 029-A/B/C) | Stage 4 |
| DEC-031 | Codespace through Phase 0, migrate to cloud before Stage 4 | Stage 3→4 transition |
| DEC-051 | Staged TradingAgents adoption (REVISED-3) | Stage 2/3 phased |
| DEC-053 | Defer Streamlit timing | Stage 3+ |
| DEC-059 | $300 hard cap on Stage 2 backtest | Stage 2 budget guard |
| DEC-060 | Smoke test gating before Stage 2 scale | Stage 2 entry |
| DEC-255 | Norbert's Gambit at funding (DLR.TO/DLR.U.TO) | Stage 4+ operational |

### Bucket E: To Be Classified

(Populated as retroactive audit progresses. Decisions here need owner verification before bucket assignment.)

---

## Status Tracking

| Metric | Count |
|---|---|
| Decisions in DOCUMENTATION_REGISTER (this file) | TBD post-classification |
| Bucket A (foundational integrated) | ~10-15 |
| Bucket B (methodology/library) | ~11-15 |
| Bucket C (cross-reference/absorbed) | ~6-10 |
| Bucket D (stage 3+/4+ operational) | ~8-12 |
| Bucket E (TBC) | TBD |

---

## Next Actions (Phase 2 — post-walkthrough)

1. Verify each bucket assignment with owner
2. For Bucket D — confirm Stage 3/4 operational deferral vs needing Stage 2 documentation NOW
3. For unclear cases — owner approval required before final categorization
4. Final consolidation: documentation-only items execute in Phase 2 cleanup; engineering items execute per ENGINEERING_REGISTER sprints

---

*Per CHECKLIST #25 honest acknowledgment that retroactive audit was needed; per #51 owner-prompted execution-tracking; per #57 use-case mapping for each decision's correct register/bucket.*

---

## Phase 2 Batch 1 — 13 decisions classified (Pass 52 turn 101)

Owner Pass 52 turn 100: "Approve all"
Owner Pass 52 turn 101: "Dec 042 pending / Approve all"

### Bucket B additions (5 — methodology/library choices)

| DEC | Description | Decision/Methodology | Notes |
|---|---|---|---|
| DEC-013 | earnings_tolerant strategy attribute (REVISED) | Strategy attribute design | Consumed by strategy code in Sprint 8 |
| DEC-033 | Email approval system (REPLACED with notifications + summaries, no approval gateway) | Process architecture | Approval governance via Option C verification gate |
| DEC-036 | Audit doc maintenance (trigger-only, not periodic) | Process methodology | AUDIT.md update cadence |
| DEC-045 | Adopt fork-existing strategy across Phase 0 | Architecture choice | Library/code reuse vs greenfield |
| DEC-084 | Audit flag at 65% win rate (lowered from 70%) | Threshold setting | Triggers audit review when strategy hits threshold |

### Bucket C additions (8 — cross-reference / absorbed via children)

| DEC | Description | Tracked via |
|---|---|---|
| DEC-063 | Universe refresh automation | Children: DEC-372/373/374/375/376/377/378/379/380 |
| DEC-064 | Phase 0.A prefetch checklist | Children: DEC-256/257/258/259/260/261 |
| DEC-065 | Validate stored data quality before Phase 1B-α | Children: DEC-410/260/417 |
| DEC-099 | 11 missing strategy categories | Children: DEC-367/368/369/370/371 |
| DEC-101 | Earnings strategies post-Phase 0.A | Parent: DEC-256 (Polygon earnings calendar prefetch) |
| DEC-102 | Market-Level / Correlation-Factor strategies | Absorbed by: DEC-369 (Cross-Asset strategies) |
| DEC-103 | Auto-populate Tier 2 universe | Children: DEC-372/373/374 |
| DEC-104 | Auto-populate Tier 3 momentum watchlist | Children: DEC-364/375/376/377 |
| DEC-105 | Spinoff detector | Children: DEC-378/379/380 |

### Bucket D additions (1 — deferred-implementation)

| DEC | Description | Activation trigger |
|---|---|---|
| DEC-074 | Polygon block trades / dark pool eval (defer empirical evaluation to Phase 1B-α) | Triggered when DEC-446 calibration runs ~1d sample analysis + 0-2d adoption decision |

### Bucket E additions (0 this batch)

DEC-042 was tagged for Bucket E in Phase 2 Batch 1 walkthrough but owner directed flip-back to PENDING for proper future walkthrough. Not added to DOCUMENTATION_REGISTER.

---

## Phase 2 Status After Batch 1

| Metric | Count |
|---|---|
| Total RESOLVED-DECIDED | 298 (was 299; −1 DEC-042 flipped back) |
| In ENGINEERING_REGISTER | 46 + 15 (Batch 1 ENG additions) = 61 |
| In DOCUMENTATION_REGISTER | 0 + ~40 (Phase 1) + 13 (Batch 1) = ~53 |
| Truly homeless after Batch 1 | 187 − 30 (Batch 1) + 1 (DEC-042 flip back, removed from homeless) = 158 |

Phase 2 cadence: ~5 more batches to clear remaining 158 unclassified.


---

## Phase 2 Batch 2 — 30 decisions classified (Pass 52 turn 103)

Owner Pass 52 turn 102: Phase 2 Batch 2 walkthrough presented (7 specific clarifications)
Owner Pass 52 turn 103: "Approve all"

### Bucket B additions (7 — methodology/library/architecture choices)

| DEC | Description | Decision/Methodology | Notes |
|---|---|---|---|
| DEC-156 | Commit messages reference CHECKLIST items followed | Process methodology | Commit hygiene; per-commit traceability |
| DEC-162 | Per-decision time-to-approve estimate + owner-approval-budget tracking | Process methodology | Decision-making efficiency |
| DEC-164 | Pairwise tradeoff matrix between decision batches (impact vs cost) | Process methodology | Decision-making framework |
| DEC-167 | Retrospective cadence every 10 audit passes | Process methodology | Audit cadence |
| DEC-169 | Owner skills gap audit (statistical, SRE, tax, etc.) | Process methodology | Owner self-assessment |
| DEC-190 | Mobile-first design priority for both web sites | Architecture choice | Web design principle |
| DEC-197 | Hosting: Vercel for web (free tier mobile-optimized); Codespace/Docker for backend | Architecture choice | Platform selection |

### Bucket D additions (14 — Stage 3+/4+ deferred-implementation)

| DEC | Description | Stage / Activation Trigger |
|---|---|---|
| DEC-113 (Stage 3+ portion) | Trade journal for paper trades (Stage 2 research/failure log already in Sprint 6) | Stage 3 paper trading |
| DEC-116 | Cash management protocol (idle cash to SGOV/T-bills) | Stage 4+ live cash management |
| DEC-141 | Sector-neutral hedge overlay | Activation trigger: any strategy proposes sector-neutral preference |
| DEC-142 | Optional market-neutral construction | Activation trigger: any strategy proposes market-neutral preference |
| DEC-145 | IV pre-earnings delta signal | Joint with DEC-258 options chain activation |
| DEC-187 | Two-property web architecture (public site + private dashboard) | Stage 3+ web infrastructure |
| DEC-188 | Public site card-based layout with track record (Sections A/B) | Stage 3+ depends on DEC-187 |
| DEC-191 | Publish timing: pre-market 7-8am ET + post-close 4pm ET | Stage 3+ operational schedule |
| DEC-192 | Site shows actual paper trades with slippage (not theoretical) | Stage 3 paper trading principle |
| DEC-193 | Open positions displayed with mark-to-market unrealized P&L | Stage 3+ feature |
| DEC-194 | Push alert events: stops, breakers, halts, daily P&L breach (-2%/-5%) | Stage 3+ alerting (joint DEC-095 monitoring) |
| DEC-195 | Telegram bot for push alerts (vs SMS — free, richer formatting) | Stage 3+ alerting platform |
| DEC-196 | No authentication on paper dashboard; revisit before live | Stage 3 paper specific; revisit Stage 4 |
| DEC-198 | Paper trading mirrors live algo exactly (same logic/sizing/risk/exits) | Stage 3 paper trading principle |

### Bucket E additions (0 this batch)

---

## Phase 2 Status After Batch 2

| Metric | Count |
|---|---|
| Total RESOLVED-DECIDED | 298 (unchanged) |
| In ENGINEERING_REGISTER | 61 + 9 (Batch 2 ENG additions) = 70 |
| In DOCUMENTATION_REGISTER | ~53 + 21 (Batch 2 DOC additions, incl DEC-113 split) = ~74 |
| Truly homeless after Batch 2 | 158 − 30 = 128 |

Phase 2 cadence: ~4 more batches remaining at 30/turn.


---

## Phase 2 Batch 3 — 30 decisions classified (Pass 52 turn 105)

Owner Pass 52 turn 104: Phase 2 Batch 3 walkthrough presented (7 specific clarifications)
Owner Pass 52 turn 105: "Approve all"

### Bucket B additions (3 — methodology/architecture/process choices)

| DEC | Description | Decision/Methodology | Notes |
|---|---|---|---|
| DEC-238 | Pre/after-hours policy (NO extended hours) | Architecture choice | Stage 2/3 policy decision; revisit if Stage 4 strategy requires it |
| DEC-245 | Owner experience retrospective (periodic check-in on workflow productivity) | Process methodology | Owner self-assessment cadence |
| DEC-248 | Owner pre-commitment doc (rules owner commits to before losses) | Process methodology / owner self-discipline | Mental model document; reduces emotional decision-making during drawdowns |

### Bucket D additions (0 this batch)

All Bucket D candidates were either Sprint 9 (post-Phase-1B-α) or already in Bucket D from prior batches.

---

## Phase 2 Status After Batch 3

| Metric | Count |
|---|---|
| Total RESOLVED-DECIDED | 298 (unchanged) |
| In ENGINEERING_REGISTER | 70 + 27 (Batch 3 ENG additions) = 97 |
| In DOCUMENTATION_REGISTER | ~74 + 3 (Batch 3 DOC additions) = ~77 |
| Truly homeless after Batch 3 | 128 − 30 = 98 |

Phase 2 cadence: ~3 more batches at 30/turn cadence.


---

## Phase 2 Final Sweep — 3 decisions classified (Pass 52 turn 107)

Owner Pass 52 turn 106: "Approve all remaining batches in phase 2"
Owner Pass 52 turn 107: Final sweep across all 87 remaining homeless decisions

### Bucket C additions (2 — cross-reference / absorbed)

| DEC | Description | Tracked via |
|---|---|---|
| DEC-336 | info_cache.json never refreshed (stale market caps) | Likely SUPERSEDED_BY_DEC-443 (Polygon reference data covers sector + market_cap PIT, replacing yfinance .info) |
| DEC-343 | Pandas-ta deprecation warning on pandas 4.0 | Joint with DEC-445 (TA-Lib evaluation; wait until DEC-445 reveals whether Polygon technical indicators sufficient as replacement) |

### Bucket D additions (1 — Stage 3+ deferred-implementation)

| DEC | Description | Stage / Activation Trigger |
|---|---|---|
| DEC-287 | Public site failure handling + freshness signal (last-updated timestamp prominent) | Stage 3+ web infrastructure (joint DEC-187/192/193 web architecture cluster) |

---

## Phase 2 Status After Final Sweep

| Metric | Count |
|---|---|
| Total RESOLVED-DECIDED | 298 (unchanged) |
| In ENGINEERING_REGISTER | 97 + 84 (Final Sweep ENG additions) = **181** |
| In DOCUMENTATION_REGISTER | ~77 + 3 (Final Sweep DOC additions) = **~80** |
| Truly homeless after Final Sweep | **0** ✓ |

## PHASE 2 COMPLETE

All RESOLVED-DECIDED decisions now have execution tracker assignments. Per CHECKLIST #58 framework, every status flip requires sprint-tracker assignment in same commit; this was retroactively applied to all pre-CHECKLIST-#58 decisions.


---

## Walkthrough 4 Additions (Pass 52 turn 113)

Per CHECKLIST #58 — Bucket D additions for Walkthrough 4 deferred decisions.

### Bucket D additions (3 — Stage 3+/4+ deferred-implementation)

| DEC | Description | Stage / Activation Trigger |
|---|---|---|
| DEC-139 | Remote kill switch (email-based STOP) — production-grade live trading control plane | Stage 4+ live trading; joint DEC-094 secrets manager + DEC-095 monitoring/alerting cluster; ~1-2d when activated |
| DEC-158 | Extend backtest period to 2008-2024 (16 years for crisis coverage) — coordinated with DEC-266 | Stage 3 paper trading evaluation; gate via empirical Sharpe-stability evidence post-Phase-1B-α; joint cluster DEC-266/DEC-298; ~5-7d when activated |
| DEC-266 | Data history extension (2020 → 2010 for walk-forward + crisis coverage) | Stage 3 paper trading evaluation; same boundary question as DEC-158; activates jointly; ~5-7d when activated |


---

## Batch B (Risk Management) Additions (Pass 52 turn 115)

### Bucket D additions (1 — Stage 4+ deferred)
| DEC | Description | Activation Trigger |
|---|---|---|
| DEC-134 (Stage 4+ portion) | FX hedge implementation (Stage 2 tracking-only portion in Sprint 6) | Stage 4+ live trading; joint DEC-255 Norbert Gambit; ~2-3d |

### Rejected decisions (1)
- DEC-133 REJECTED + REVISIT_DURING_STAGE_3: Max gross long/short/net exposure caps. Same precedent as DEC-090 sector cap REJECTED (owner medium-high risk philosophy)


---

## Bulk Sweep Final (Batches D-K + DEC-251) Additions (Pass 52 turn 119)

### Bucket B additions (process methodology — 5)
- DEC-038 Layered execution with iteration budgets (process methodology, operational across Pass 52)
- DEC-161 Decision dependency graph (DAG) — graphviz visualization optional Sprint 9
- DEC-163 Implementation cost estimate per decision — Phase 2 retroactive audit pattern
- DEC-244 SESSION_START.md (already operational via CLAUDE.md)
- DEC-292 Decision→CHECKLIST migration (quarterly cadence)

### Bucket D additions (Stage 3+/4+ deferred — 13)
- DEC-034 Daily loss limits (Stage 4)
- DEC-035 Tax classification Canadian (Stage 4 + DEC-270 CPA)
- DEC-157 Synthetic broker outage chaos (Stage 3)
- DEC-160 Multi-vendor fallback chain (Stage 4)
- DEC-166 HANDOFF.md template (Stage 3 owner-activated)
- DEC-168 Incident postmortem template (Stage 3 first-incident)
- DEC-176 Meta-strategies (Stage 3 post-base-validation)
- DEC-180 Pre-market checklist (Stage 4 live ops)
- DEC-181 EOD reconciliation report (Stage 3 paper)
- DEC-182 Weekly performance review (Stage 3 paper)
- DEC-185 Incremental backtest updates (Stage 3 daily)
- DEC-267 Trade event store schema (Stage 3 SQLite, Stage 4 Postgres)
- DEC-268 Paper-vs-backtest Bayesian comparison (Stage 3)
- DEC-270 CPA consultation (Stage 4 owner action)
- DEC-271 Real-time data feed cost (Stage 4)
- DEC-272 Stage 4 hosting migration plan
- DEC-273 Disaster recovery plan (Stage 4)

### Bucket C additions (cross-reference / absorbed — 4)
- DEC-014 Phase 1B passing criteria (absorbed by DEC-422 + DEC-426) — **Pass 53 NOTE: this absorption inadvertently caused Phase 1A reference to drop from PROJECT_PLAN §3 sub-phases. Phase 1A restored via DEC-486/487/488 PROPOSED Pass 53; methodology learning DEC-489 RESOLVED-DECIDED + CHECKLIST #63 prevent recurrence.**
- DEC-037 Characterization-test-first Phase A (absorbed by DEC-438)
- DEC-100 17+ categorical breakdown variables (absorbed by DEC-422)
- DEC-417 Test-run audit gate (already in Sprint 6)
- DEC-420 DEC-131 implementation (absorbed by DEC-205-216 + DEC-211)

### Rejected (1 + DEC-133 from Batch B)
- DEC-133 Max gross long/short/net exposure caps — REJECTED per DEC-090 risk philosophy precedent


---

## Pass 53 Turn — Phase 1A Restoration Cross-Reference

**Trigger:** Owner Pass 53: "Why was phase 1A dropped. Even phase 1A had alpha and beta. same as phase 1B."

**4 new decisions added to canonical inventory:**

| DEC | Description | Bucket | Status |
|---|---|---|---|
| DEC-486 | Phase 1A restoration as distinct sub-phase (Sprint 6.5) | Cross-reference / new sprint scope | PROPOSED |
| DEC-487 | Phase 1A-α restoration as distinct sub-phase (Sprint 6.5-7) | Cross-reference / new sprint scope | PROPOSED |
| DEC-488 | Phase 1A-β restoration as distinct sub-phase (Sprint 7 Day 1) | Cross-reference / new sprint scope | PROPOSED |
| DEC-489 | Adversarial audit must include archive comparison | Methodology learning | RESOLVED-DECIDED |

**9 canonical docs updated by atomic Pass 53 turn commit (`0d5182c2`):**
1. PROJECT_PLAN.md
2. TRADING_RULES_AND_INFORMATION.md
3. DETAILED_PROJECT_PLAN.md
4. CLAUDE.md
5. ENGINEERING_REGISTER.md
6. AUDIT.md
7. AUDIT_INDEX.md
8. CHECKLIST.md
9. LEARNINGS.md

**Subsequent dependency-sweep commit (this turn) updates:**
- DOCUMENTATION_REGISTER.md (this entry)
- IMPLEMENTATION_READINESS_DASHBOARD.md (Sprint 6.5 readiness gate)
- PASS_53_PRIORITIES.md (Phase 1A work added to priorities)
- LIMITATIONS_CAVEATS_ASSUMPTIONS.md (Phase 1A scope caveats)
- HANDOFF_PASS52.md (closure note acknowledging Phase 1A omission caught Pass 53)
- STRATEGY_REGISTER.md (strategy fire scope per phase)
- BUG_REGISTER.md (Phase 1A scope notes)
- PROGRESS.md (progress tracker)
- README.md (top-level project description)
- EXPLANATION.md (project explanation)
- TRADINGAGENTS_DATA_AUDIT.md (toolkit phase scope)
- UNIVERSAL_LEARNINGS.md (Pass 53 learning)
- API_AUDIT.md (Sprint 4 dependencies)
- AUDIT_TRIAGE.md (decision triage update)
- THEME_X53_SEQUENCING.md (sequencing note)

**Total docs touched across both Pass 53 turn commits: 24 of 27 (3 historical-immutable docs untouched: PROJECT_PLAN_ARCHIVE.md, ADVERSARIAL_AUDIT_PASS_52_TURN_132.md, CRITICAL_GAPS_RESOLUTION_PASS_52_TURN_133.md).**

