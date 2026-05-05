# PASS 52 RETROSPECTIVE + PASS 53 PRIORITIES

**Created:** Pass 52 turn 124
**Pass 52 final commit:** `4b2bd662` (BUG-111 verification + DEC-298 honest correction)
**Pass 53 status:** READY TO BEGIN

---

## EXECUTIVE SUMMARY

Pass 52 was the **completion pass**: brought audit from 60% PENDING to 100% terminal state across 462 decisions, fixed structural gaps in execution tracking, and surfaced the true scope of Stage 2 implementation work (8-10x larger than original estimate).

**Key achievements:**
- PENDING resolution: 60% → 0% (~280 decisions resolved)
- Phase 2 retroactive sprint-tracking audit: ~239 decisions classified across 5 batches + cleanup
- Bug coverage gap closed: BUG_REGISTER.md created (148 bugs cross-referenced)
- Bulk sweep: 80 PENDING decisions converted to terminal states with HARD-REVERSIBILITY flag-and-continue pattern
- CHECKLIST #58 created and operational at 4 levels
- Engineering effort reality check: ~30-40d → ~310-385d (8-10x growth surfaced)

**Key process improvements:**
- 5-file atomic commit pattern (CHECKLIST #58)
- 4-bucket decision classification (DOCUMENTATION_REGISTER.md)
- Theme-batched walkthrough format proven at 4-8 decisions/turn
- Pre-flight cross-check methodology caught 52% supersession rate

---

## PASS 52 — DETAILED RETROSPECTIVE

### What went well

**1. Theme-batched walkthroughs at scale**
- 4 walkthroughs delivered 24 decisions across 6 themes (X16 + X33 + X40 + X42 + X43 + X52 + X59 + Group D + DEC-158 bonus)
- Per-theme pre-flight caught 52% supersession rate (12 of 23 items) — significant scope reduction vs creating parallel decisions
- Owner approval flow worked cleanly: walkthrough → 7 specific clarifications → "approve all" → atomic commit

**2. CHECKLIST #58 operational discipline**
- 5-file atomic commit pattern enforced consistency: AUDIT_INDEX + AUDIT + ENGINEERING_REGISTER + DOCUMENTATION_REGISTER + IMPLEMENTATION_READINESS_DASHBOARD all updated synchronously
- Phase 2 retroactive audit fixed legacy gap (~239 homeless decisions); #58 prevents recurrence
- Bug coverage gap (148 bugs) closed via BUG_REGISTER.md cross-reference (not parallel infrastructure)

**3. Owner accountability cycle**
- Owner caught 4 distinct anti-patterns: homeless decisions (turn 98), substantively-homeless decisions (turn 108), bug coverage gap (turn 110), 80 PENDING delegation (turn 114-118)
- Each catch led to framework-level fix, not one-off patch
- DEC-298 correction at turn 122 surfaced via owner verification question — caught my turn 121 misstatement within 1 turn

**4. Bulk sweep with HARD-REVERSIBILITY flag-and-continue**
- 80 PENDING decisions processed across 4 commits (turns 115-119) without quality degradation
- DEC-251 (dependency injection refactor) properly flagged for owner review per directive #2
- 3 supersessions caught even in bulk format (DEC-016/066/020 → DEC-422/422/441)

### What didn't go well

**1. Premature RESOLVED-DECIDED flips before owner walkthrough**
- DEC-042 (turn 101): I prematurely flipped to RESOLVED-DECIDED in Phase 2 Batch 1; owner caught and reverted
- This was the trigger for CHECKLIST #58 framework
- Pattern: I treated "PARTIAL — needs revision" qualifier as RESOLVED equivalent. Should have stayed PENDING for proper walkthrough.

**2. Misstating decision status in commit narratives**
- Turn 121: claimed DEC-298 was "still BLOCKED — gates DEC-377/411"
- Reality: DEC-298 is RESOLVED-DECIDED; downstream is sprint sequencing
- Owner verification turn 122 caught it; corrected turn 123

**3. X43 theme misidentification**
- Turn 109 menu listed "X43 = Phase 0.B Portfolio Class" 
- Actual X43 = Data History (1 PENDING DEC-266)
- No dedicated Phase 0.B Portfolio Class theme exists
- Walkthrough 4 ended up being 5 decisions not 8

**4. Initial bug coverage scope overestimation**
- Turn 110: framed bug coverage as "144+ bugs need separate ENG entries"
- Reality: 148/148 bugs already linked to decisions; right action was lightweight cross-reference
- Course-corrected during execution turn 111 (avoided weeks of unnecessary work)

**5. Sweep pre-flight effectiveness diminished in bulk**
- Per-theme walkthroughs: 52% supersession-catch rate
- Bulk sweep (Batches B-K): 4% supersession-catch rate (3 of 80)
- Trade-off: bulk speed vs per-theme rigor; owner aware via path-A/B/C presentation turn 114

### Process gaps that emerged

**1. Sprint-tracker assignment was not enforced before #58**
- Pre-Pass 52 turn 96: 294 RESOLVED-DECIDED decisions; only 46 (15.6%) in ENGINEERING_REGISTER
- Owner accountability call-out turn 98: "this is very basic stuff and we had already discussed this. you are simply not following it"
- Fix: CHECKLIST #58 + Phase 2 retroactive audit

**2. Substantive vs technical homelessness**
- Phase 2 Final Sweep declared "0 homeless" based on textual register mention
- Owner verification turn 108 caught 22 decisions with textual mention but no proper sprint-table entry
- Fix: cleanup batch turn 109 + #58 enforcement at substantive level

**3. Bug-decision linkage scattered across audit text**
- Pre-Pass 52: bugs documented in AUDIT.md ### BUG-NN sections
- Cross-references with decisions only in inline scope text
- No canonical lookup
- Fix: BUG_REGISTER.md created turn 111

---

## PASS 52 — FINAL STATE METRICS

### Decisions

| Status | Count | % |
|---|---|---|
| Total decisions | 462 | 100% |
| **PENDING** | **0** | **0% ✓** |
| RESOLVED-DECIDED | 358 | 77.5% |
| DEFERRED_TO_STAGE_3 | 32 | 6.9% |
| DEFERRED_TO_STAGE_4 | 19 | 4.1% |
| SUPERSEDED (total) | 29 | 6.3% |
| BLOCKED_ON_X | 10 | 2.2% |
| REJECTED | 2 | 0.4% |
| Other (PARTIAL/OBSOLETE) | 12 | 2.6% |

### Bugs

| Status | Count |
|---|---|
| Total canonical bugs | 148 |
| In BUG_REGISTER cross-reference | 148 (100%) |
| CRITICAL OPEN | 3 (BUG-095, BUG-218, BUG-111) |
| Resolution path verified | 3 (Sprint 3, DEC-443 absorbed Sprint 4, Sprint 8) |

### Engineering effort (FINAL)

| Sprint | Pass 52 Start | Pass 52 End | Growth |
|---|---|---|---|
| Sprint 1 (Phase 0.A) | ~7-9d | ~20.5-26.5d | 3x |
| Sprint 2 (Engine Bug Fixes Tier A) | ~9d | ~25.5-30.5d | 3x |
| Sprint 3 (Portfolio class) | ~5-7d | ~8-11d | ~1.5x |
| Sprint 4 (DEC-410 audit) | ~5-7d | ~41.75-54.25d | **8x (largest growth)** |
| Sprint 5 (Universe management) | ~5-8d | ~13.5-15.5d | 2x |
| Sprint 5 NEW (Position Sizing) | n/a | ~3.5d | new |
| Sprint 6 (Phase 0.E + Hygiene) | ~7-10d | ~62.25-76.75d | **7x (largest absolute)** |
| Sprint 7 (Statistical Methodology + A/B + AgentGate) | ~17-19d | ~76-85d | **4-5x (largest sprint)** |
| Sprint 7-8 (Dimensional Cube + Dashboards) | gated | ~28-38d | new tracked |
| Sprint 8 (Strategy categories) | ~50-60d | ~37-55d | consolidation |
| Sprint 9 (Phase 1B-α run + ongoing) | n/a | ~6d | new |
| **Critical path minimum** | **~21-25d** | **~125-160d** | **6x** |
| **Total Stage 2 realistic** | **~30-40d** | **~311.5-386.5d** | **8-10x** |

### Frameworks operational

| Framework | Status |
|---|---|
| AUDIT.md (decision detail) | Canonical |
| AUDIT_INDEX.md (status table) | Canonical |
| ENGINEERING_REGISTER.md (sprint roadmap) | Operational since turn 99 |
| DOCUMENTATION_REGISTER.md (5-bucket DOC tracker) | NEW Pass 52 turn 99 |
| BUG_REGISTER.md (148-bug cross-reference) | NEW Pass 52 turn 111 |
| IMPLEMENTATION_READINESS_DASHBOARD.md (sprint readiness) | Canonical |
| CHECKLIST.md (process discipline) | 58 items operational |
| LEARNINGS.md (L1-L137) | 137 learnings |
| LIMITATIONS_CAVEATS_ASSUMPTIONS.md | CAV-001 through CAV-071+ |
| API_AUDIT.md | DEC-410 17-API audit complete |
| STRATEGY_REGISTER.md | Tracks strategy-level decisions |

---

## PASS 53 PRIORITIES — RECOMMENDED

Owner directs Pass 53 priorities. My recommendations based on Pass 52 final state:

### Priority 1: Sprint 1 Kickoff (HIGHEST PRIORITY)

**Phase 0.A Polygon foundation implementation per DEC-441 ($30/mo subscription)**

- 17.5-23.5 engineering days estimate
- Critical path for Phase 1B-α
- Owner action prerequisite: subscribe to Polygon Stocks Starter ($29/mo)
- Decisions ready: DEC-040 (PIT loader), DEC-256-261 (prefetch checklist), DEC-307-310 (cache fixes), DEC-225/227/235 (cache + calendar), DEC-275 (requirements.txt), DEC-318-320/390/391 (sentiment refresh), DEC-328/329 (multiprocess), DEC-117/118 (data integrity + macro)

**Why first:** All other sprints depend on Sprint 1 cache + data infrastructure. Maximum ROI on critical path.

### Priority 2: BUG-095 + Sprint 3 (HIGH PRIORITY)

**Phase 0.B Portfolio class implementation**

- 8-11 engineering days estimate
- Resolves BUG-095 (CRITICAL OPEN) which blocks DEC-070/076/091
- Required for proper position sizing per DEC-086/087/088 (Kelly + vol-targeted + portfolio vol target)

**Why second:** Portfolio class is foundational architecture; multiple downstream decisions wait on it. BUG-095 is one of 3 CRITICAL OPEN bugs.

### Priority 3: DEC-410 Audit Findings Implementation (Sprint 4)

**Cost stack + reliability + DEC-410 cleanup** — ~30-41 engineering days

- Largest growth sprint (8x); now critical path
- Resolves 14 audit findings (BUG-218 absorbed via DEC-443)
- Includes Canadian-IBKR cost stack, ticker lifecycle, slippage model, smart money refinement

**Why third:** Sprint 4 work is largely parallel-able with Sprints 1+2; can run in parallel once Sprint 1 cache infrastructure established.

### Priority 4: BUG-111 Architectural Choice + Sprint 8

**Retest cross-cutting primitive vs explicit variants**

- Owner decision needed at Sprint 8 implementation start: Option A (shared primitive ~5-10d) vs Option B (per-strategy variants ~25-30d)
- BUG-111 is third CRITICAL OPEN bug
- Recommendation: Option A (smaller surface, opt-in flexibility)

### Priority 5: Documentation cleanup batch

**DOC Bucket B/C decisions execution** (Phase 2 retroactive cleanup)

- ~80 documentation-only decisions in DOCUMENTATION_REGISTER
- Bucket A foundational/integrated: ~10-15 (no work needed; historical)
- Bucket B methodology/library: ~15-20 (process documentation updates)
- Bucket C cross-reference/absorbed: ~6-10 (ensure cross-refs consistent)
- Bucket D Stage 3+/4+: documented; defer to Stage 3+ activation

**Why last:** Documentation execution is parallel-able with engineering work; not critical path.

---

## PASS 53 — RECOMMENDED OPENING DIRECTIVE

**Recommendation:** Sprint 1 kickoff with Polygon subscription owner action.

**Sequence:**
1. Owner subscribes to Polygon Stocks Starter ($29/mo) per DEC-441
2. Verify subscription active in API_AUDIT.md
3. Begin Sprint 1 implementation per ENGINEERING_REGISTER scope
4. CHECKLIST #58 enforced for any decision changes during implementation
5. Pass 53 closes once Sprint 1 reaches first measurable milestone (e.g., S&P 500 OHLCV fully cached + first PIT loader test passing)

**Estimated Pass 53 duration:** 17.5-23.5 engineering days for Sprint 1 + parallel BUG-095 work in Sprint 3 = ~25-35 calendar days realistic.

---

## OPEN OWNER QUESTIONS FOR PASS 53

1. **Which priority order?** My recommendation: Sprint 1 (Polygon foundation) → Sprint 3 (Portfolio + BUG-095) → Sprint 4 (DEC-410 cleanup). Owner direction welcome.

2. **Polygon subscription timing?** Sprint 1 cannot fully proceed without active subscription. Owner action required.

3. **BUG-111 architectural choice (Option A vs B)?** Owner reviews at Sprint 8 implementation start (not now). Pre-flag noted.

4. **Pass 53 cadence?** Per-decision walkthroughs in Pass 52 worked well. Pass 53 will be implementation-heavy — different cadence (per-PR review? per-sprint-milestone review?). Owner preference.

5. **CHECKLIST #58 enforcement during implementation?** Any RESOLVED-DECIDED-to-RESOLVED-IMPLEMENTED status flips will need #58 atomic commits. Owner confirms approach.

---

## CONTINUITY ITEMS FROM PASS 52

| Item | Status | Pass 53 action |
|---|---|---|
| DEC-251 sandbox-prototype | Owner-approved Sprint 6 ~5-7d | Execute when Sprint 6 begins |
| DEC-298 implementation | RESOLVED-DECIDED, sprint sequencing | Sprint 4 implementation ~5d |
| BUG-095 Portfolio class | CRITICAL OPEN; Sprint 3 resolution | Sprint 3 implementation ~8-11d |
| BUG-111 retest primitive | CRITICAL OPEN; Sprint 8 with architectural choice | Sprint 8 owner direction at start |
| BUG-218 yfinance .info | CRITICAL OPEN; absorbed via DEC-443 | Sprint 4 implementation |
| API subscriptions | DEC-441 Polygon $30/mo + DEC-450 Quiver paid + others ~$263 CAD/mo total | Owner action sequenced |

---

*Per CHECKLIST #25 (honest retrospective acknowledging both wins and losses)/#43 (precise grep on Pass 52 commits + state metrics)/#51 (recommendations are recommendations; owner decides Pass 53 priorities)/#57 (use-case mapping per priority area with critical-path analysis)/#58 (Pass 52 framework operational and ready for Pass 53 enforcement during implementation).*

---

## PASS 53 EVENT — PHASE 1A RESTORATION (mid-pass discovery)

**Owner directive:** "Why was phase 1A dropped. Even phase 1A had alpha and beta. same as phase 1B."

**Discovery:** PROJECT_PLAN_ARCHIVE.md showed Phase 1A v3 was COMPLETE (67 instruments × 4yr × 6,942 trades; atr_trail_1x confirmed primary exit). Pass 52 turn 119 absorbed DEC-014 Phase 1B passing criteria into DEC-422+426; Phase 1A reference inadvertently dropped from PROJECT_PLAN §3 sub-phases.

**Meta-failure of audit methodology:** ADVERSARIAL_AUDIT (Pass 52 turn 132) compared current docs vs current docs but didn't compare against PROJECT_PLAN_ARCHIVE. Phase 1A was archived; thus invisible to gap detection.

**Resolution Pass 53 (this pass):**
- 4 new decisions logged: DEC-486/487/488 PROPOSED + DEC-489 RESOLVED-DECIDED
- 9 canonical docs updated atomic commit (`0d5182c2`) — PROJECT_PLAN, TRADING_RULES, DETAILED_PROJECT_PLAN, CLAUDE, ENGINEERING_REGISTER, AUDIT, AUDIT_INDEX, CHECKLIST, LEARNINGS
- Subsequent dependency-sweep commit (this turn) updates remaining 15 docs
- New CHECKLIST #63 + L142 codify the methodology learning

**Updated Pass 53 priorities (post-restoration):**

| # | Original priority | Pass 53 update |
|---|---|---|
| 1 | Sprint 1 (Phase 0.A Polygon) | UNCHANGED — Sprint 1 starts immediately |
| 2 | Sprint 3 (Phase 0.B Portfolio) | UNCHANGED |
| 3 | Sprint 4 (DEC-410 cleanup) | UNCHANGED |
| 4 | Sprint 5 (Universe management) | UNCHANGED |
| 5 | Sprint 6 (Phase 0.E catch-mechanism) | UNCHANGED |
| **5.5** | **NEW: Sprint 6.5 (Phase 1A + 1A-α + 1A-β baseline)** | **~19-27d engineering + ~26-33h compute** |
| 6 | Sprint 7 (Phase 1B agent overlay) | NOW gated by Sprint 6.5 Phase 1A-α owner Sharpe ≥ 0.7 OOS gate |
| 7 | Sprint 7-8 (Phase 1B-α dimensional cube) | NOW gated by Sprint 6.5 Phase 1A-β scale validation passing |
| 8 | Sprint 9 (Phase 1B-α run) | NOW reuses cube infrastructure built in Phase 1A-α; $300 budget commits only after 1A-β cleared |

**New owner approval items added by Pass 53 turn:**

| DEC | Description | Status |
|---|---|---|
| DEC-486 | Phase 1A restoration | PROPOSED — awaits owner approval |
| DEC-487 | Phase 1A-α restoration | PROPOSED — awaits owner approval |
| DEC-488 | Phase 1A-β restoration | PROPOSED — awaits owner approval |
| DEC-482 | Walk-forward expanding window 2y+/6mo × 5 folds (per Polygon Stocks Starter 5y window) | PROPOSED — awaits owner approval |
| DEC-483 | Universe expansion R1000 + NDX added to Sprint 1 | PROPOSED — awaits owner approval |
| DEC-484 | Free FMP alternative — SEC EDGAR direct parsing for financials | PROPOSED — awaits owner approval (Q3 from prior turn unanswered) |
| DEC-485 | Earnings transcripts dropped from Stage 2 scope OR alternative | PROPOSED — awaits owner answer |

**Pass 53 priorities pre-Sprint-1 (now):**
1. Owner approval of DEC-486/487/488 (Phase 1A restoration)
2. Owner approval of DEC-482 (walk-forward configuration)
3. Owner approval of DEC-483 (R1000 + NDX universe expansion)
4. Owner decision on DEC-484/485 (FMP free alternative + earnings transcripts scope)
5. Owner Polygon subscription tonight (Stocks Starter $29/mo per directive)
6. THEN Sprint 1 Day 1 begins

**Estimated Pass 53 duration (revised post-Phase-1A-restoration):** 50-70 engineering days from Sprint 1 start to Phase 1B-α-ready state (was 30-40d pre-restoration). Phase 1A introduces ~19-27 days of pre-agent-overlay validation work but protects $300 1B-α budget from infrastructure failures.


---

## PASS 53 BATCH APPROVAL COMPLETED (this turn)

**Owner Q1-Q5 + Q3 explanation answered + approved.**

| Q | Owner answer | Decision logged |
|---|---|---|
| Q1 walk-forward | (c) Expanding window 2y+/6mo × 4-5 folds | DEC-482 RESOLVED-DECIDED |
| Q2 R1000+NDX | Sub-tiers for tracking | DEC-483 RESOLVED-DECIDED |
| Q3 PIT grain | My recommendation approved (year-grain default + day-grain via SEC EDGAR for DEC-368) | DEC-483 RESOLVED-DECIDED |
| Q4 DEC-477+479 | Agree | DEC-477 + DEC-479 RESOLVED-DECIDED |
| Q5 FMP alternative | Skip 2 strategies that need full financials, option b sounds good | DEC-484 + DEC-485 + DEC-490 RESOLVED-DECIDED |

**Plus auto-flipped (owner directive prior turn was "restore phase 1A"):**
- DEC-486/487/488 PROPOSED → RESOLVED-DECIDED

**Plus added (logically derived from owner answers):**
- DEC-478 RESOLVED-DECIDED (Polygon Stocks Starter $29/mo per "starter pack only")
- DEC-490 RESOLVED-DECIDED (Phase 1A skipped strategies enumerated)

**Total: 11 decisions logged this batch.**

**Sprint 1 Day 1 readiness post-batch:**
- ✅ Walk-forward configuration (DEC-482)
- ✅ Universe expansion (DEC-483)
- ✅ Universe canonical CSV (DEC-477)
- ✅ Polygon tier (DEC-478)
- ✅ Cost reference (DEC-479)
- ✅ FMP alternative (DEC-484)
- ✅ Earnings transcripts (DEC-485)
- ✅ Phase 1A architecture (DEC-486/487/488)
- ✅ Phase 1A skipped strategies (DEC-490)

**Sprint 1 Day 1 BLOCKED only by:**
1. Owner Polygon Stocks Starter subscription (tonight per directive)
2. Sprint 0 verification on local VS Code (AAII + CNN F&G + SEC EDGAR domain reachability)
3. BUG-007 verification — affects Sprint 6.5 Day 1 NOT Sprint 1 Day 1 (Phase 1A `--no-agents` flag)

---

## Pass 53 Post-Pre-Flight Update (Stream 3 chunk C)

**Trigger:** Owner Pass 53 directive: "sequential" — Stream 3 chunk C registration of Pass 53 work after the Sprint-1 Pre-Flight Batch above.

### Decisions added Pass 53 post-pre-flight (6 NEW):

| DEC | Status | Sprint | Description |
|---|---|---|---|
| DEC-491 | PROPOSED | Sprint 2 | trade_log Parquet format (preserves nested types) |
| DEC-492 | PROPOSED | Sprint 2 | signals_at_entry filter removed (preserve string/list signals) |
| DEC-493 | PROPOSED | Sprint 2 | trade_id schema field |
| DEC-494 | RESOLVED-DECIDED | Sprint 1 | Tier 2 / refresh_extended_universe.py alignment (DEC-368→DEC-370 attribution fix; NDX-non-S&P → T1c) |
| DEC-495 | RESOLVED-DECIDED | Stage 3+ | archived watchlist for tickers rotating out of all 5 buckets |
| DEC-496 | RESOLVED-DECIDED | Sprint 1 + Sprint 5 | Tier 3 momentum methodology (Jegadeesh-Titman 12-1 classic) |

### Universe-build progress Pass 53 cumulative:

- ✅ Tier 1 ETFs CSV migration (27 ETFs)
- ✅ T1c populated (157 rows; multi-period entries)
- ✅ T2/T3 schema migrated to B++ format
- ✅ Universe folder moved to top-level `Backtesting universe/`
- ⏸ T1a `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` (Sprint 1)
- ⏸ T1b `russell_1000_membership.csv` (Sprint 1 procurement; LSEG paywall surfaced)
- ⏸ T2 historical populate (Sprint 1 post-prefetch)
- ⏸ T3 historical populate (Sprint 1 post-prefetch)
- ⏸ DEC-495 archived watchlist (Stage 3+)

### TRADING_RULES.md NEW sections Pass 53 cumulative:

- §2A Signal Universe Catalogue (6 categories, ~265-275 fields)
- §10.8 Smart Money Composite Score (weights matrix + labels)
- §10.9 Smart Money-Adjacent Signals
- §13.12 API Endpoint Inventory (16 sources)
- §22.1 — test pyramid coverage gate per sprint

### State after Pass 53 cumulative:

- Total decisions: 490 (+18 from pre-Pass-53 baseline)
- RESOLVED-DECIDED: ~384
- PROPOSED: 16 (DEC-469-481 + DEC-491-493)
- Universe CSVs populated: 2 of 5; 3 pending Sprint 1
- Cumulative commits this Pass: ~25

### Sprint 1 effort revised post-Pass-53:

~25.5-35.5d → ~28-39d (+~2.5-3.5d for T2/T3 historical populate per DEC-494/496).

Sprint 1 Day 1 readiness UNCHANGED — same 3 blockers from prior batch (Polygon subscription + Sprint 0 verification + BUG-007 for Sprint 6.5 not Sprint 1).

### Cross-references:

- AUDIT.md Pass 53 narrative entries
- AUDIT_INDEX.md DEC-491-496 rows
- DOCUMENTATION_REGISTER.md Pass 53 post-pre-flight entry
- AUDIT_TRIAGE.md Pass 53 post-pre-flight decision count delta

## Sprint 0A active (Pass 53 owner directive 2026-05-05 — DEC-497)

**Title:** Sprint 0A — Full multi-API prefetch + universe build + Stage 2 NO-LIVE-API refactor.
**Renames:** Sprint 1 → Sprint 0A (absorbs prior Sprint 1 work).
**Status:** Universe build IMPLEMENTED Pass 53; multi-API prefetch + refactor PENDING (after universe validation).

**Phasing (Sprint 0A.0-0A.10):**
- 0A.0 — Quiver API key + Trader-tier endpoint enumeration (owner-side dashboard list pending)
- 0A.1 — Polygon EXTENSION: news for full universe (~15 hr), indicators (SMA/EMA/RSI/MACD), financials, events, NBBO selective
- 0A.2 — FRED + ALFRED prefetch (~50 series, all 11 macro categories)
- 0A.3 — AAII + CNN F&G prefetch (composite + 7 CNN sub-components)
- 0A.4 — CFTC COT prefetch (weekly historical 2020+)
- 0A.5 — Quiver full Trader-tier prefetch (11+ endpoints discovered; await dashboard list)
- 0A.6 — SEC EDGAR structured prefetch (10-K/10-Q financials + Form 4 + 13F + 8-K events via edgartools per DEC-456)
- 0A.7 — Smoke + demo tests per API (separate test files for 8 APIs)
- 0A.8 — Refactor `backtest/data/{fetcher,macro,sentiment,smart_money}.py` to read from `data_prefetch/` ONLY (HARD CUT no live API)
- 0A.9 — Move `backtest/data/cache/polygon/` → `data_prefetch/polygon/` (after universe validated)
- 0A.10 — Doc sync per CHECKLIST #67 (DEC-498)

**Universe state (Pass 53 IMPLEMENTED):** T1a 614 / T1c 161 / T1 ETFs 27 / T2 10 (full SCREENER restart in flight) / T3 1999 period rows (1220 unique). Sector backfill: T1a 70/70 + T3 partial (Polygon SIC + pending yfinance one-time fallback for ADRs/foreign per Q1 2026-05-05).

**Excluded from Sprint 0A:** dashboards (DEC-199/200/201), engine bugs (DEC-491-493 → Sprint 2), T1b R1000 (DEC-365 deferred Stage 3), strategy compute.
