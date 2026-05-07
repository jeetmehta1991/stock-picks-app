# DETAILED_PROJECT_PLAN — Stock Picks & Automated Trading System

**Document role:** Self-contained narrative project plan covering all 5 stages with Stage 2 fully elaborated phase-by-phase. Per owner directive Pass 52 turn 134: "elaborated project plan is a new document. No caps on lines or content. Should contain every granular detail."

**Owner directives Pass 52 turn 134:**
- Q1 = (B) All 5 stages — full lifecycle elaborated; Stage 1 brief, Stage 2 full, Stage 3-5 planning level
- Q2 = ALL 15 sections per Stage 2 phase
- Q3 = (i) Phase-sequenced — top-to-bottom narrative

**Companion documents (this doc supersedes them as primary read):**
- `PROJECT_PLAN.md` — original index/cross-reference doc, retained as quick-reference card
- `TRADING_RULES_AND_INFORMATION.md` — canonical thresholds (referenced from this doc when threshold-precise; not duplicated unless useful inline)
- `TRADINGAGENTS_DATA_AUDIT.md` — agent data dependency mapping
- `AUDIT.md` / `AUDIT_INDEX.md` — decision history (decisions referenced here include narrative inline; full text in AUDIT.md if needed)
- `ADVERSARIAL_AUDIT_PASS_52_TURN_132.md` — 167 gaps + 10 blockers
- `CRITICAL_GAPS_RESOLUTION_PASS_52_TURN_133.md` — 13 PROPOSED decisions awaiting batch approval

**Last updated:** Pass 52 turn 134
**Maintenance discipline:** When this document and others diverge, THIS document is canonical. Other docs become reference appendices.

---

# TABLE OF CONTENTS

**Part 0 — Project Foundation**
- §0.1 What this project is (concrete, plain English)
- §0.2 Owner profile and constraints
- §0.3 Risk philosophy
- §0.4 What's explicitly out of scope
- §0.5 How this plan flows (reading guide)

**Part 1 — The 5-Stage Lifecycle**
- §1.1 Stage map at a glance
- §1.2 Stage 1: Proof of Concept (COMPLETE — historical reference)
- §1.3 Stage 2: Strategy Validation (CURRENT — Parts 2-10 below detail this)
- §1.4 Stage 3: Paper Trading (planning level)
- §1.5 Stage 4: Live Trading Small Scale (planning level)
- §1.6 Stage 5: Full Automation (planning level)
- §1.7 Stage transition gates

**Part 2 — Stage 2 Architecture Overview**
- §2.1 What Stage 2 is trying to achieve
- §2.2 The dimensional verdict cube (the central artifact)
- §2.3 Universe architecture (3 tiers)
- §2.4 Strategy roster (4 layers, ~199 strategies (per CANONICAL_FACTS F-002 Pass 53 + STRATEGY_ROSTER_FULL.md))
- §2.4.5 Exit method roster (DEC-067 canonical, 17 methods)
- §2.4.6 Pre-trade filters
- §2.5 Signal universe (~220 fields per ticker per day)
- §2.6 Agent overlay architecture (TradingAgents Pattern 2)
- §2.7 Data sources required for Stage 2
- §2.8 Stage 2 execution flow (rules screen → cube populate → A/B test → verdict)

**Part 3 — Phase 0.A: Polygon Foundation**
(15 sections per Q2 directive)

**Part 4 — Phase 0.B: Portfolio Class**
(15 sections)

**Part 5 — Phase 0.C: Engine Bug Fixes Tier A**
(15 sections)

**Part 6 — Phase 0.D: ICT/SMC Fork Integration**
(15 sections)

**Part 7 — Phase 0.E: Catch-Mechanism Defense + Architecture Hygiene**
(15 sections)

**Part 7.5 — Phase 1A: Rules-Based + Smart Money Baseline (Sprint 6.5)**
(15 sections)

**Part 7.6 — Phase 1A-α: Rules-Only Dimensional Cube + Dashboards (Sprint 6.5-7)**
(15 sections)

**Part 7.7 — Phase 1A-β: Production-Scale Validation Run (Sprint 7 Day 1)**
(15 sections)

**Part 8 — Phase 1B: Statistical Methodology + A/B + Custom Toolkits**
(15 sections)

**Part 9 — Phase 1B-α: Combined Dimensional Cube + Dashboards (3-arm)**
(15 sections)

**Part 10 — Phase 1C+: Strategy Categories Expansion**
(15 sections)

**Part 11 — Sprint 4: DEC-410 API Audit Findings**
(15 sections — runs in parallel)

**Part 12 — Sprint 5: Universe Management**
(15 sections — runs in parallel)

**Part 13 — Stage 2 Verdict & Stage 2 → 3 Transition**
- §13.1 Phase 1B-α verdict gate
- §13.2 Stage 2 → Stage 3 transition criteria
- §13.3 What happens if Stage 2 fails
- §13.4 Owner approval flow

**Part 14 — Stage 3: Paper Trading (Planning Level)**
- §14.1 Goal
- §14.2 Duration and prerequisites
- §14.3 Activities
- §14.4 Stage 3 → Stage 4 transition criteria

**Part 15 — Stage 4: Live Trading Small Scale (Planning Level)**
- §15.1 Goal
- §15.2 Prerequisites (CPA, hosting, kill switch, etc.)
- §15.3 Activities
- §15.4 Stage 4 → Stage 5 transition criteria

**Part 16 — Stage 5: Full Automation (Planning Level)**
- §16.1 Goal
- §16.2 Activities

**Part 17 — Cross-Cutting Concerns**
- §17.1 PIT correctness discipline (applies all stages)
- §17.2 Cost summary (all stages)
- §17.3 Tech stack
- §17.4 Process and governance
- §17.5 Open architectural decisions (13 PROPOSED awaiting approval)

**Part 18 — Reading Guide & Maintenance**
- §18.1 Section template (per phase 15-section pattern)
- §18.2 How to update this document
- §18.3 Cross-document map

---

# PART 0 — PROJECT FOUNDATION

## §0.1 What this project is

A comprehensive algorithmic trading platform for **swing trading US equities** by a Canadian-resident solo owner. The system has two parallel components that get tested against each other:

**(A) Rules-based screener** that scans the universe daily, fires ~109-119 distinct strategies (technical setups, ICT/SMC patterns, smart money confluence, calendar effects, chart patterns, etc.), and produces a ranked list of trade candidates with preliminary tier assignment.

**(B) AI agent overlay (TradingAgents framework)** that takes the most-uncertain rule candidates, runs them through a 12-agent debate pipeline (Market/Fundamentals/News Analysts → Bull/Bear Researchers → Research Manager → Trader → Aggressive/Conservative/Neutral Risk Debaters → Portfolio Manager → Reflection), and produces a structured 5-tier rating (Buy/Overweight/Hold/Underweight/Sell) per candidate.

**The goal of Stage 2** is to determine empirically — through a dimensional verdict cube + walk-forward validation + A/B framework — whether (B) adds enough alpha over (A) to justify its cost and complexity, and which strategies pass statistical validity gates.

**The goal of Stages 3-5** is to deploy the validated stack to paper trading, then small-capital live trading, then full automation.

GitHub: `jeetmehta1991/stock-picks-app`

## §0.2 Owner profile and constraints

- Canadian resident (Willowdale, Ontario)
- IBKR (Interactive Brokers) account holder
- Personal Windows laptop + VS Code + Claude Code (Pass 53 update — was: GitHub Codespace "vigilant system"; owner switched to local VS Code) for development
- VS Code + Claude Code for browsing and code review
- VS Code integrated terminal for Python execution (local Windows laptop)
- Solo operator — no team, no fund structure
- Approval cadence: explicit per-decision approval required (Option C verification gate per CHECKLIST #51)
- Time budget: variable; project has been ~12+ months of audit/planning iteration; implementation begins Pass 53

## §0.3 Risk philosophy

**Medium-high risk tolerance** — explicitly accepts drawdowns in pursuit of higher ROI. Owner buys dips during volatile and crisis markets.

**Concentration is accepted** (not penalized):
- No sector caps (DEC-090 REJECTED)
- No max gross/net exposure caps (DEC-133 REJECTED)
- No hard regime direction blocks (replaced with crisis-flag size reduction, not blocks)

**Currency exposure is accepted:**
- Default unhedged on Canadian ETF substitutions for US exposure (DEC-254 — XUU/VUN unhedged; XQQ/XSU happen to be hedged variants)
- USD/CAD FX exposure tracked but not hedged in Stage 2-3 (DEC-134)
- Hedge implementation evaluated for Stage 4+

**What owner does NOT accept:**
- Lookahead bias in backtest (PIT correctness is non-negotiable)
- Untested production code (90% test coverage minimum per DEC-098)
- Silent failures (every error must surface; PIT guard RAISE not WARN per DEC-305)
- Premature automation decisions (full automation only after Stage 4 stable for ≥6 months)

**Implication for design:** Risk controls focus on OPERATIONAL risks (PIT correctness, test coverage, deterministic behavior) NOT portfolio-construction risks (sector caps, exposure caps).

## §0.4 What's explicitly out of scope

- **Intraday trading** — separate future project; Stage 2 backtest uses daily bars (with optional intraday data for ICT/SMC/MAE/MFE computation)
- **High-frequency trading (HFT)** — never in scope
- **Market making** — never in scope
- **Options strategies as primary signal** — supplementary signal only (DEC-145 deferred-implementation; not part of Stage 2 strategy roster)
- **Crypto** — US equities only
- **Non-US equities (other than Canadian-listed substitutes for US exposure)**
- **Pre-Stage-1 history rewriting** — Stage 1 (`fetch_stocks.py` + Alpha Vantage daily updater) was completed and is not being refactored

## §0.5 How this plan flows (reading guide)

This document is meant to be read **top to bottom** by an owner who needs to understand what's happening in Stage 2 right now and what comes next. It is NOT a reference document with cross-pointers — every phase's content is self-contained inline.

**Recommended reading paths:**

- **Owner who hasn't read in a while** — read Parts 0-2 (foundation + Stage 2 overview), then jump to the active phase's part
- **New collaborator** — read Parts 0-2 fully, then skim Parts 3-12 phase-by-phase
- **Decision review** — read the specific phase's §X.13 (Decision History) and §X.14 (Open Issues from Adversarial Audit) sections
- **Implementation start** — read Parts 3 + 4 + 5 + 6 (the parallel-able first wave) in detail, then Part 17 cross-cutting concerns

**Section pattern per Stage 2 phase (Parts 3-12):**

Every phase has 15 sections (per Q2 owner directive turn 134):

1. **What** — concrete deliverable in plain English
2. **Why** — how this advances Stage 2 toward the verdict
3. **How** — components, data flow, dependencies (the technical body)
4. **When** — sequence, blockers, parallel-ability
5. **Done criteria** — verifiable acceptance (not "see other doc")
6. **Risks** — what could go wrong specifically
7. **Cost** — engineering days + dollars (subscriptions, API calls)
8. **Decisions in scope** — list with one-line summaries (not just IDs)
9. **Test approach** — how the deliverable is verified
10. **Data dependencies** — what feeds in, where it comes from, what's downstream
11. **Operational checklist** — week-by-week or day-by-day breakdown
12. **Open issues** — gaps from ADVERSARIAL_AUDIT relevant to this phase
13. **Decision history** — what changed and why; key supersessions
14. **File/module structure** — where in `backtest/` each component lives
15. **Example walkthrough** — concrete trace of one trade through this phase's logic

---

# PART 1 — THE 5-STAGE LIFECYCLE

## §1.1 Stage map at a glance

```
┌────────────────────────────────────────────────────────────────────────────────┐
│ Stage 1     │ Stage 2          │ Stage 3       │ Stage 4         │ Stage 5     │
│ Proof of    │ Strategy         │ Paper Trading │ Live Small      │ Full        │
│ Concept     │ Validation       │ (3 mo min)    │ Scale           │ Automation  │
│             │                  │               │                 │             │
│ COMPLETE    │ CURRENT          │ Planning      │ Planning        │ Planning    │
│ (Pass 1-25) │ (Pass 53+ impl)  │ (post-1B-α)   │ (post-3mo paper)│ (post-stable│
│             │                  │               │                 │  Stage 4)   │
└────────────────────────────────────────────────────────────────────────────────┘
        │              │                │                  │              │
        ▼              ▼                ▼                  ▼              ▼
   index.html      Phase 1B-α       Paper trade       Live $10K-50K   Full auto
   daily updater   verdict cube     SQLite event      with kill        cloud
   (legacy)        + 5-Gate filter  store + reconcile switch + DR     hosted
```

**Each stage requires the previous to demonstrate something measurable** before transition. No stage skipped, no stage cheated.

## §1.2 Stage 1: Proof of Concept (COMPLETE)

**Status:** COMPLETE (Pass 1 through pre-Pass-25)
**Goal:** Demonstrate that the owner can build and operate a stable daily-updating data pipeline.

**Deliverable shipped:**
- `fetch_stocks.py` — Python script that fetches US top gainers + TSX quotes via Alpha Vantage
- `index.html` — dark-themed daily snapshot rendered from fetched data
- GitHub Actions cron at 06:00 UTC committing `index.html` updates
- Static committed CSV of S&P 500 constituents (482 tickers — Wikipedia scraping was unreliable historically (Codespace allowlist blocks); CSV remains the workaround for reliability)

**Key lessons preserved into Stage 2 architecture:**
1. Wikipedia scraping is unreliable historically (was blocked in prior Codespace setup; local VS Code has no such restriction but Wikipedia remains fragile per L88); use static committed reference data or paid APIs
2. GitHub Actions cron + commit pattern works for low-frequency data refresh
3. `index.html` rendering proves the front-end → back-end → data pipeline works end-to-end (small but real)
4. Alpha Vantage was sufficient for proof-of-concept but is being demoted in Stage 2 (Polygon replaces it per DEC-441/455)

**Why Stage 1 isn't being refactored:** It works, it's stable, and the daily updater commits to `index.html` are a known noise factor in `git pull --rebase` flow. Stage 2 builds alongside, not replacing.

## §1.3 Stage 2: Strategy Validation (CURRENT)

### Sprint 0A note (Pass 53 owner directive 2026-05-05; DEC-497)

Sprint 1 has been **renamed → Sprint 0A** with materially expanded scope:
- **Multi-API prefetch** — all 8 planned APIs (Polygon, Quiver Trader, FRED, ALFRED, AAII, CNN F&G, CFTC COT, SEC EDGAR), not Polygon-only
- **Universe build absorbed** — Pass 53 IMPLEMENTED (614 T1a + 161 T1c + 27 ETFs + T2/T3 SCREENERs)
- **Stage 2 NO-LIVE-API refactor** — backtest reads from `data_prefetch/` only; HARD CUT (owner directive Q8)
- **Smoke + demo tests per API** — 16 test files (8 smoke + 8 demo), separate per API per owner directive
- **18-classifier sector normalization** (DEC-499) — GICS-11 + Fixed Income/Commodities/Volatility/Broad Market/International/Emerging Markets/Small Cap

Phasing: Sprint 0A.0-0A.10 (see ENGINEERING_REGISTER for sub-phase detail). Effort: ~6-10 days code + ~25 hours prefetch wall time. Excluded: dashboards (DEC-199/200/201 → Sprint 9), engine bugs (DEC-491-493 → Sprint 2), T1b R1000 (deferred Stage 3 per DEC-365), strategy compute.


**Status:** Pass 53 begins implementation. Pass 52 closed audit (462 → 472 decisions, 0 PENDING). Pass 52 turn 132 surfaced 167 documentation gaps + 10 Stage 2 effectiveness blockers via adversarial review. Pass 52 turn 133 began critical-gap resolution (FDR replacing Bonferroni, cube dimensionality reduction, paired A/B elimination, Portfolio class API spec, TradingAgents v0.2.4 schema verification, Polygon tier reconsideration).

**Goal:** Empirically validate the strategy roster across a dimensional verdict cube using walk-forward validation + A/B testing of agent overlay vs rules-only. Produce per-cell verdicts (PASS/FAIL/INSUFFICIENT_SAMPLE) that feed a live decision lookup table for Stage 3.

**Effort:** ~319-400 engineering days realistic (Pass 53 R7-05 fix recompute from sub-phase table: 20.5+8+25.5+62.25+96+28+37+41.75 = 319 low; 26.5+11+30.5+76.75+108.5+38+55+54.25 = 400.5 high; was "310-385"); ~125-160 days minimum critical path. Pre-Pass-53 figure preserved as historical note per L143.

**Budget reconciliation (Pass 53 R7-04 fix):** $75-225 (DEC-472/473 expected spend for 300 candidates × $0.25/propagate) and $300 (DEC-059 hard cap) are NOT contradictory: $75-225 = expected actual A/B propagate spend; $300 = budget HARD CAP that triggers `budget_tracker.py` halt. Headroom of $75-225 within $300 covers cost overruns from prompt-cache misses + retry storms + Sonnet upgrade contingency. Owner-funded budget envelope = $300; expected drawdown = $75-225.

**Sub-phases (covered in Parts 3-12):**

| Phase | Part | Sprint | Effort |
|---|---|---|---|
| 0.A — Multi-API Prefetch | Part 3 | Sprint 0A | ~20.5-26.5d |
| 0.B — Portfolio Class | Part 4 | Sprint 3 | ~8-11d |
| 0.C — Engine Bug Fixes Tier A | Part 5 | Sprint 2 | ~25.5-30.5d |
| 0.D — ICT/SMC Fork Integration | Part 6 | Sprints 1/4/8 | distributed |
| 0.E — Catch-Mechanism + Hygiene | Part 7 | Sprint 6 | ~62.25-76.75d |
| 1B — Statistical + A/B + Toolkits | Part 8 | Sprint 7 | ~96-108.5d (post-DEC-462-468) |
| 1B-α — Cube + Dashboards | Part 9 | Sprint 7-8 | ~28-38d |
| 1C+ — Strategy Categories | Part 10 | Sprint 8 | ~37-55d |
| (Sprint 4 — DEC-410 audit) | Part 11 | Sprint 4 | ~41.75-54.25d |
| (Sprint 5 — Universe Mgmt) | Part 12 | Sprint 5 | ~13.5-15.5d |
| 1B-α run + ongoing | end of Part 9 | Sprint 9 | ~6d (orchestration; compute ~20-32h per DEC-505 4-fold (Pass 53 R7-06 fix; was 37-40h pre-DEC-505 6-fold) wall) |

**Stage 2 verdict criteria** (Part 13 covers in detail):
- Sharpe ≥ 1.0 OOS (DEC-269)
- Max DD ≤ 25% (DEC-269)
- Win rate ≥ 50% (DEC-269 — to be reconciled with DEC-353 R:R ≥ 2.0 minimum)
- A/B clear: full-agents Sharpe − rules-only Sharpe ≥ 0.2 absolute OR ≥ 0.15 relative (DEC-131)
- FDR q < 0.10 (replacing Bonferroni p < 0.05 per DEC-469 PROPOSED)
- Owner reviews Phase 1B-α dashboards and approves transition

## §1.4 Stage 3: Paper Trading

**Status:** Planning level. Real design begins after Stage 2 verdict.

**Goal:** Run the validated Stage 2 stack against live market data in paper-trading mode (no real capital) for 3 months minimum. Verify that:
- Live execution matches backtest expectations (slippage, fills, timing)
- Agent decisions in real-time match backtest distributions
- No infrastructure failures over a sustained period
- Operational reliability (data freshness, kill switch, reconciliation) holds

**Duration:** 3 months minimum (DEC-028)

**Trigger:** Stage 2 → Stage 3 transition criteria met (Part 13 covers in detail)

**Activities (planning level — concrete spec at Stage 3 entry):**
- Paper trades mirror live algo exactly (DEC-198)
- SQLite trade event store (DEC-267 — Postgres comes in Stage 4)
- End-of-day reconciliation reports (DEC-181)
- Weekly auto-generated performance reviews (DEC-182)
- Live decision lookup table populated from Phase 1B-α verdict cube
- Daily monitoring dashboards (DEC-199/200/201 from Phase 1B-α)
- Email notifications for trade entries/exits (Stage 3+ infrastructure per DEC-194/195)

**What Stage 3 explicitly tests:**
1. Does the algo execute the same trades a backtest would have predicted? (live vs backtest divergence)
2. Are slippage estimates from DEC-092/122/280 accurate against real fills?
3. Do agent decisions in real-time produce same Sharpe distribution as backtest predicted?
4. Does the kill switch work?
5. Does the Portfolio class correctly track P&L, drawdown, sector concentration during a real market session?

**Stage 3 → Stage 4 trigger (Part 14 covers):**
- 3 months paper trading complete
- Live-vs-backtest divergence < 20% (per DEC-269 Phase 1B-α gate, sustained)
- Numeric gates met during paper period (Sharpe / DD / win rate)
- CPA consultation complete (DEC-270)
- Owner explicit Stage 4 approval

## §1.5 Stage 4: Live Trading Small Scale

**Status:** Planning level. Real design at Stage 4 entry.

**Goal:** Trade real capital at small scale ($10K-50K range, owner's choice) for ≥6 months. Validate everything Stage 3 paper showed against actual fills, FX conversion costs, tax events, and operational issues that don't show in paper mode.

**Prerequisites (must all be true before Stage 4 entry):**
- All Stage 2→3 numeric gates met during 3-month paper trading
- CPA consultation on Canadian tax classification complete (DEC-270, DEC-035) — trader-classification vs investor-classification has major tax implications
- Multi-vendor data fallback operational (DEC-160) — single-API-down doesn't kill live trading
- Remote kill switch via email operational (DEC-139) — owner can halt the algo from anywhere
- Daily loss limits operational (DEC-034) — algo halts at -X% daily P&L
- Norbert's Gambit operational for CAD→USD funding (DEC-255) — for capital deployment
- Cloud hosting migration complete (DEC-272) — Local VS Code (was: Codespace) is dev only, not production
- Disaster recovery plan in place (DEC-273) — backup, restoration, runbook
- IBKR market data subscriptions active (~$10-30/mo per DEC-271) — real-time bid/ask required
- Polygon Stocks Advanced (or equivalent) for real-time data — if continuing Polygon (per DEC-478 tier upgrade)

**Activities (planning level):**
- Live execution at small capital
- Daily reconciliation owner-reviewed
- Weekly performance review with QuantStats
- Monthly tax tracking and reporting (CRA-compliant)
- Quarterly strategy decay re-validation (DEC-214)
- Continuous monitoring of A/B framework live behavior

**Stage 4 → Stage 5 trigger (Part 15 covers):**
- Stage 4 stable ≥ 6 months
- Cumulative P&L positive
- No major operational incidents (data outage > 4 hours, wrong-side trade, kill switch failure)
- Owner-approved scaling plan
- Compliance and tax tracking operational

## §1.6 Stage 5: Full Automation

**Status:** Planning level. Real design at Stage 5 entry.

**Goal:** Stage 4 deliverables operating autonomously with minimal owner intervention. Owner role shifts from operator to monitor + strategist.

**Activities (planning level):**
- All Stage 4 capabilities running unattended
- Owner reviews weekly performance + monthly strategy health
- Capital scaling per owner-approved plan
- Continuous A/B and ablation testing in live (DEC-211 evolved into ongoing)
- Strategy retirement and addition workflow operational (DEC-249/214/043)
- Full API stack operational (~$263 CAD/mo baseline per project memory; revised to $93-200+/mo per DEC-478 tier choice)

## §1.7 Stage transition gates (summary table)

| Transition | Trigger condition | Owner approval needed? |
|---|---|---|
| Stage 1 → 2 | Smoke test (`fetch_stocks.py` operational) | No (already complete) |
| Stage 2 → 3 | Phase 1B-α verdict gate met (Sharpe / DD / win rate / A/B clear / FDR / divergence) | Yes — explicit dashboard review |
| Stage 3 → 4 | 3 mo paper + numeric gates + CPA + DR + kill switch + multi-vendor fallback | Yes — explicit live-capital authorization |
| Stage 4 → 5 | 6 mo Stage 4 stable + cumulative P&L positive + scaling plan | Yes — explicit automation authorization |

**Detail for each transition's exact criteria:** Part 13 (Stage 2 → 3) is fully elaborated; Parts 14-16 cover Stage 3-4-5 at planning level.

---

# PART 2 — STAGE 2 ARCHITECTURE OVERVIEW

This part establishes the architecture you need to understand BEFORE reading any phase. Phases 0.A-1C+ all reference these structures.

## §2.1 What Stage 2 is trying to achieve

In one sentence: **Determine empirically which strategies have edge, in which market regimes, on which sub-universes, and whether AI agent overlay adds enough alpha to justify its cost.**

Three concrete outputs from Stage 2:

1. **A populated dimensional verdict cube** — a multi-dimensional table where each cell is a unique combination of (strategy × market regime × sector × cap band × vol band × hold period × universe tier × smart-money-signal-present), populated with metric values (Sharpe, Sortino, win rate, max DD, etc.) computed from walk-forward backtest trades that fell in that cell.

2. **A 5-Gate validity filter applied to every cell** — each cell is classified PASS / FAIL_RR / INSUFFICIENT_SAMPLE / FAIL_STAT based on sample size + statistical significance + risk-reward + significance correction. PASS cells form the "live decision lookup table" (DEC-429) that Stage 3+ uses for live trading.

3. **An A/B verdict on agent overlay value** — running rules-only vs full-agents-with-veto vs no-Risk arms across the same opportunity set, with block-bootstrap confidence intervals (per DEC-472 PROPOSED replacing paired design), produces an empirical Sharpe-delta verdict per regime per strategy. If full-agents Sharpe − rules-only Sharpe ≥ 0.2 (DEC-131), agent overlay justified for live use.

If any of these three produce empty results (no PASS cells, no Sharpe edge, A/B null), Stage 2 has failed and architecture must be revisited (Part 13.3 covers what-if-Stage-2-fails).

## §2.2 The dimensional verdict cube (the central artifact)

The cube is the heart of Stage 2. Every other phase serves the cube either by feeding it data, populating it, applying methodology to it, or visualizing it.

**Cube definition (Pass 53 R7-01 + R7-02 + R7-09 P0 fix — 5 primary cube dims + 12 drilldown facets per DEC-569; strategy axis updated to 199 per Pass 53 STRATEGY_ROSTER_FULL roster expansion to Layer 1.I shorts + Layer 6):**

**Primary cube (5 dims, faceted in dashboard view):**

| # | Dimension | Levels | Why it matters |
|---|---|---|---|
| 1 | Strategy | 199 (Layer 1 110 + Layer 1.I 38 shorts + Layer 2A 12 + 2B 4 + 2C 5 + 3A 20 + 3B 21 + Layer 6 27 — see CANONICAL_FACTS F-002 + STRATEGY_ROSTER_FULL.md) | The thing being tested |
| 2 | Market regime | 4 (calm/neutral/volatile/crisis per DEC-106) | Strategies that work calm may fail volatile |
| 3 | Sector | 11 GICS | Tech vs Energy vs Financials may have different signal-to-noise |
| 4 | Universe tier | 5 (T1a S&P 500 / T1c NDX / T1 ETFs / T2 spinoffs/IPOs / T3 momentum per DEC-504) | Liquidity and efficiency differ; T3-over-T1 precedence per DEC-504 |
| 5 | Smart money signal present | 2 (yes/no per DEC-124 confluence) | Smart money should add edge |

**Drilldown facets (12 dims, queryable but NOT faceted in cube primary view — recorded as TRADE-LEVEL METADATA per DEC-189 trade outcome log):**

Market cap band, vol band, hold period band, momentum band, liquidity band, entry trigger type, exit method (17 per DEC-067/517-538), news event present, earnings proximity, ICT/SMC signal type, Layer 5 regime-eligibility flag, Layer 6 sub-category.

**Cell count (primary cube only):** 199 × 4 × 11 × 5 × 2 = 87,560 maximum cells (5-dim primary cube replacing prior 8-dim 254K design per DEC-569).

**Expected populated cells:** ~25-35% (~22K-30K populated) — Layer 1.I short-side strategies + Layer 6 universe-level signals expand expected populated coverage relative to long-only baseline; many cells still empty because trades don't occur in all combinations (e.g., crisis-regime + low-vol-band drilldown is structurally rare).

**Why 5 primary + 12 drilldown:** Original cube design (TRADING_RULES §21.1) had 17+ dimensions. Adversarial Pass 4 (GAP 130) and Pass 53 R7-01 audit showed: with 199 strategies × 8 dims × 30 trades min × 4 OOS folds (DEC-505), faceted-cube math exceeds universe ticker-days. DEC-569 reduction to 5 primary cube dims (with 12 dims demoted to drilldown trade-level metadata) brings cube populating math back to feasibility while preserving dimensional analysis via drilldown query.

**Sample-size requirement reconciliation:** 87,560 cells × 30 trades minimum × 4 OOS folds = ~10.5M trades. Universe provides ~700K ticker-days × 5y Polygon Stocks Starter window per DEC-505 = ~3.5M ticker-days. Cube populating ratio ≈ 33%; ~22K-30K populated cells is feasible. Cells failing 30-trade minimum mark INSUFFICIENT_SAMPLE per F-009 Gate 1.

**Drilldown dimensions (recorded per trade, queryable but not faceted in primary cube — per DEC-569 5+12 reconciliation):**
- Momentum band — recorded per trade, queryable but not a cube axis
- Liquidity band — used as pre-trade filter (DEC-321/366), drilldown only
- Entry trigger type — recorded
- Exit method — recorded (17 methods per DEC-067/517-538)
- News event present — recorded
- Earnings proximity — already a filter via DEC-348 event suppression
- ICT/SMC signal type — per-strategy attribute
- Market cap band — drilldown (was prior cube axis pre-DEC-569)
- Vol band — drilldown (was prior cube axis pre-DEC-569)
- Hold period band — drilldown (was prior cube axis pre-DEC-569)
- Layer 5 regime-eligibility flag — drilldown (Pass 53 schema overlay per STRATEGY_ROSTER_FULL Layer 5)
- Layer 6 sub-category — drilldown for Layer 6 universe-level signals (Pass 53 addition)

**Per-cell metrics (TRADING_RULES §22.4):** roi_pct, sharpe, sortino, reward_risk_ratio, profit_factor, expectancy, win_rate, n_trades, avg_win, avg_loss, avg_hold_days, max_drawdown, calmar, max_adverse_excursion_avg, max_favourable_excursion_avg, roi_after_costs, sharpe_at_5bps/10bps/20bps, bonferroni_p (replaced by FDR q), psr, t_stat, ci_95.

**5-Gate validity filter (per DEC-426, statistical methodology revised by DEC-469/470 PROPOSED):**

| Gate | Threshold | What it tests |
|---|---|---|
| Gate 1 — Sample size | n ≥ 30 trades per cell | Statistical inference requires minimum n; below 30 = INSUFFICIENT_SAMPLE |
| Gate 2 — Significance | FDR q < 0.10 (Benjamini-Hochberg, hierarchical) replacing Bonferroni p < 0.05 | Multiple-testing correction — too strict at cube scale; FDR is appropriate |
| Gate 3 — PSR | Probabilistic Sharpe Ratio ≥ 0.95 | Deflated Sharpe — accounts for non-normality + multiple testing |
| Gate 4 — t-stat | t ≥ 3.4 | Bailey-Lopez de Prado discovery threshold |
| Gate 5 — R:R | reward_risk_ratio ≥ 2.0 | Hard owner directive (DEC-353) — never test below 2:1 |

**Verdict classes per DEC-426:**
- **PASS** — all 5 gates clear; cell goes into live decision lookup
- **FAIL_RR** — Gate 5 fails; cell rejected regardless of other gates
- **INSUFFICIENT_SAMPLE** — Gate 1 fails; cell suspended pending more trades (re-evaluated post-Phase-1B-α)
- **FAIL_STAT** — Gates 2/3/4 fail; cell rejected for statistical reasons

## §2.3 Universe architecture (5 tiers — Pass 53 R7-07 fix; was 3 tiers)

The universe defines the trading population — which tickers are even eligible to be traded. 5 tiers exist (Pass 53 expansion per DEC-365 + DEC-483 + DEC-118 + DEC-103 + DEC-104) because liquidity, history, and efficiency differ enough to warrant different rules. T1b R1000-non-S&P deferred to Stage 3 per DEC-365.

**Universe-count reconciliation (Pass 53 R7-07 fix vs §7.5.1):** Stage 2 active universe = T1a 503 + T1c 134 + T1ETF 27 + T2 ~282 + T3 ~993 ≈ 1,937 unique resolved tickers per Master Dedup CSV with `resolved_tier` column (DEC-504). Prior "1015 tickers" reflected pre-DEC-504 union of T1a + T1c + ETFs; "509 tickers" reflected T1a-only. Both are subsets — actual Stage 2 universe is 1,937 unique.

**Tier 1A — S&P 500 + Selected ETFs (614 historical / 503 active + 27 ETFs):**
- Composition: S&P 500 constituents per `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` (DEC-303 — PIT-correct historical membership 614 rows: 503 active + 111 historical removed-during-window; DEC-477 — supersedes static 482-ticker CSV) + selected sector/macro ETFs per `Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv` (DEC-118 + DEC-494 — 27 ETFs: VIX, DXY, GLD, oil, sector ETFs, TLT, HYG, SHY, etc.)
- Liquidity floor: $10M ADV (per DEC-366)
- History requirement: 250 trading days
- Why this tier: most-liquid US equities; highest signal-to-noise for technical strategies

**Tier 1C — NASDAQ-100 non-S&P (134 active + 27 historical = 161 total per DEC-303 / Pass 53 sync):**
- Composition: NDX-non-S&P-overlap constituents per `Tier 1C Universe_NASDAQ-100 Tickers_Jan 2020 to May 2026.csv` (DEC-483 — Pass 53 RESOLVED 161 rows: 101 currently active = Nasdaq official 101 verified via 3-way Slickcharts/Wikipedia/Nasdaq IR cross-check; 60 historical removed-during-window; multi-period rows for CSGP/TTWO/WDC/SPLK)
- Liquidity floor: $10M ADV
- History requirement: 250 trading days
- Why this tier: tech-heavy benchmark; complements T1a sector coverage

**Tier 1B — Russell 1000 non-S&P (deferred to Stage 3 per DEC-365):**
- Composition: R1000 constituents excluding S&P 500 + NDX-non-S&P overlap
- Status: DEFERRED to Stage 3 papertrading per DEC-365 (LSEG free tier inadequate; T1a 503 + T1c 101 + ETFs 27 = ~632 instruments already 9× Phase 1A v3 archive baseline; T1b expansion premature for Stage 2 backtest validity)

**Tier 2 — Spinoffs / IPOs (~282 unique resolved tickers, variable per as_of):**
- Composition: recent spinoffs (per DEC-378/379/380 — Polygon corp-actions screener + SEC EDGAR Form 10-12B scrape) + recent IPOs (per DEC-103/373/374) — file `Tier 2 Universe_Spinoffs and Recent IPOs_Feb 2010 to May 2026.csv`
- Liquidity floor: $5M ADV
- Market cap minimum: $2B
- History requirement: 20 days minimum (with `LIMITED_HISTORY` flag respected by strategies that need longer history)
- Why this tier: spinoffs and IPOs often have inefficient pricing; specific strategies target this

**Tier 3 — Momentum Top-100 Watchlist (~993 unique resolved tickers across 72 monthly snapshots):**
- Composition: top 100 momentum-screen tickers refreshed monthly via DEC-496 J-T 12-1 broad-market screener (per DEC-104/364/375/376/377) — file `Tier 3 Universe_Momentum Top-100_Jun 2022 to May 2026.csv` (1923 period rows / 1220 unique)
- Liquidity floor: $5M ADV
- Market cap minimum: $300M
- History requirement: 60 days
- Refresh: monthly via `.github/workflows/refresh_momentum_watchlist.yml`
- Why this tier: momentum strategies need a candidate pool that updates with regime; static lists go stale
- T3-over-T1 precedence per DEC-504: when ticker is PIT-active in multiple tiers, T3 > T2 > T1c > T1a > T1ETF for runtime rules

**Universe build pipeline (Sprint 5, Part 12):** Each tier has a build function that runs at backtest start (or daily in live) producing a list of tickers eligible for that tier on that as_of date. PIT-correctness applies — at as_of=2020-06-15, Tier 1 should reflect S&P 500 membership AS OF that date, not current.

## §2.4 Strategy roster (4 layers, ~199 strategies (per CANONICAL_FACTS F-002 Pass 53 + STRATEGY_ROSTER_FULL.md))

The strategy roster is the COMPLETE LIST of distinct strategies that fire on the universe. Each strategy is a self-contained signal generator with entry/exit/sizing rules.

**Layer 1 — Baseline 60-strategy roster (pre-Pass-52):**
Original 7 categories established Pass 1-25:
- Trend-following (moving average cross, MACD, Donchian, etc.)
- Mean-reversion (RSI extreme, Bollinger Band, z-score)
- Momentum (price-momentum, relative-strength)
- Breakout (resistance break, volume-confirmed breakout)
- Volatility (low-vol pullback, high-vol mean-revert)
- Earnings (post-earnings drift, pre-earnings positioning)
- Other (e.g., gap fade, opening-range breakout)

(Exact 60 enumerated in STRATEGY_REGISTER.md Layer 1.)

**Layer 2 — Phase 0.D Additions (ICT/SMC + Earnings Momentum + Calendar):**
Per DEC-045 (fork-existing strategy across Phase 0) and DEC-259/345/352:
- ICT/SMC strategies using `smartmoneyconcepts` library fork: Fair Value Gaps (FVG), Break of Structure (BOS), Change of Character (CHoCH), Order Blocks (OB)
- Earnings Momentum strategies: post-earnings drift variants per DEC-045
- Calendar strategies: turn-of-month, day-of-week effects, FOMC week patterns

**Layer 3 — Pass 52 RESOLVED-DECIDED Additions:**
- Layer 3A: 8 Chart Pattern Strategies (DEC-355-362 — head-and-shoulders, double-top, triangles, cup-and-handle, etc.)
- Layer 3B: 5 Strategy Categories (DEC-367-371 — calendar/index-rebalance/within-category extensions)

**Layer 4 — PENDING Strategy-Additive Sub-Decisions (per STRATEGY_REGISTER.md):**
- DEC-141 — Sector-neutral hedge overlay (1 overlay variant)
- DEC-142 — Market-neutral construction (long stock + short SPY at beta) (1 overlay variant)
- DEC-143 — IPO/lockup/secondary offering systematic framework (2-3 classes)
- DEC-145 — IV delta vs historical pre-earnings pattern (1 class)
- DEC-176 — Meta-strategies (boolean AND/OR) — multiplier on existing, not additive class
- Layer 4 subtotal: ~5-6 classes (DEC-176 not counted)

**Total strategy roster:** ~108-118 strategy classes when Layer 1+2+3+4 fully implemented. Aligns with STRATEGY_REGISTER.md "Total Roster Summary" (line 133).

Note: prior versions of this section listed exit methods (DEC-432/433) and the AEP breaker (DEC-435) in Layer 4, inflating the count by ~9-10. Exit methods are reusable components consumed by strategies, not strategies themselves; they live in §2.4.5 (canonical source: TRADING_RULES.md §8). The AEP breaker is a portfolio-level guard; it lives with circuit breakers (TRADING_RULES.md §9), not the strategy roster. Counts corrected per LEARNINGS L144 / CHECKLIST #65.

**BUG-111 architectural choice (deferred):** Existing 25 breakout strategies in `screener.py` may need break-and-retest variants. Option A (shared retest primitive ~5-10d) recommended over Option B (per-strategy variants ~25-30d). Decision deferred to Sprint 8 implementation start (Part 10).

**STRATEGY_REGISTER.md is the canonical roster** — when this plan adds/changes strategies, that doc is updated atomically.

## §2.4.5 Exit method roster (DEC-067 canonical, 17 methods)

Exit methods are reusable components that determine WHEN to leave a position. They are orthogonal to strategies (entry signal generators); any strategy can be paired with any exit method. The strategy declares which exit method it uses; the engine resolves and applies the method.

**Canonical source:** `TRADING_RULES_AND_INFORMATION.md` §8 — full enumeration of the 17 exit methods, parameter spec per method, and R:R floor (≥2.0 per Gate 5 in §3.5).

**Decision lineage:**
- DEC-067 — 17 exit methods canonical list (RESOLVED-DECIDED, Pass 39)
- DEC-432 (Phase A) — first batch of additive variants
- DEC-433 (Phase B) — second batch (6 net new after 1 was dropped from initial 9)
- DEC-075 — exit method classification (signal-based vs time-based)

**Implementation reference:** `backtest/engine/exit_strategies.py` — current `EXIT_STRATEGIES` registry has 12 keys (subset of canonical 17). Sprint 2 (Phase 0.C) bug list covers `volume_climax` (DEC-327) and `rsi_extreme` (DEC-340) which are listed canonical but missing implementation.

**Open inconsistency to reconcile:** Counts differ across sources — prior §2.4 cited "9 new variants", TRADING_RULES §8 says "6 new (1 dropped)", and the engine registry has 12 total. A reconciliation pass is queued for Sprint 2 alongside the missing-implementation bug fixes; until then, treat TRADING_RULES §8 as the authoritative spec.

**Selection per strategy:** see STRATEGY_REGISTER.md per-strategy `default_exit` field. Exit method choice is part of the strategy spec, but the method itself lives in this roster, not the strategy roster.

## §2.4.6 Pre-trade filters

Pre-trade filters are gates that decide whether ANY strategy can open a position on a given (ticker, day, direction) combo. They run before the strategy roster screen and can reject candidates regardless of signal strength. Filters are universal — not per-strategy.

**Canonical source:** `TRADING_RULES_AND_INFORMATION.md` (relevant sub-sections on liquidity, regime, cooldown). This section is a roster pointer, not a re-spec.

**Filter list:**

1. **Liquidity filter (DEC-321/366)** — fail-closed; tier-specific 20-day ADV floors. Universe member with ADV below tier floor → blocked from entry that day.
2. **Universe membership PIT (DEC-477/483 — B++ format Pass 53)** — `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` is a single static CSV with `added_date`/`removed_date` columns per DEC-303 (S&P 500) + sister files for R1000/NDX. Loader filters by `(added_date IS NULL OR added_date ≤ as_of) AND (removed_date IS NULL OR removed_date > as_of)`. Source: S&P Dow Jones Indices press releases primary; Wikipedia + internet browse fallback under Pass 53 one-time L88 exception. Mapping timeframe: 2020-01-01 → today + ongoing; pre-2020 active tickers have NULL `added_date`. Ticker not in universe on `as_of` → blocked.
3. **Regime fail-closed (DEC-316)** — `classify_regime` returns `'unknown'` on missing VIX data; `REGIME_FILTER['unknown']` blocks all new entries. Existing positions continue under their original stop logic.
4. **CooldownState (DEC-018, post-stop-out cooldown)** — after a stop-out on (ticker, strategy), block re-entry on same combo for N bars. Spec per DEC-018 (still PENDING).
5. **MaxLossState (DEC-135)** — per-ticker rolling 30-day cumulative loss cap. Once breached, ticker blocked for the cap window.
6. **Crisis-regime exclusion list (`CRISIS_LONG_EXCLUSIONS` in `config.py`)** — data-confirmed wrong-directional tickers in crisis regime (VXX, TLT, EEM); blocked from longs in crisis regime only.
7. **Earnings proximity (DEC-013-revised, NOT a hard block)** — earnings in next N days reduces position size but does NOT block. Listed here for completeness; functionally a sizing modifier, not a filter.

**Implementation locations:** `backtest/engine/backtest.py:_process_day` gates the screener output through items 1, 3, 6, 7 today. Items 2, 4, 5 are pending implementation per their respective decisions.

**Out of scope here:** circuit breakers (intraday/post-entry guards — see TRADING_RULES §9), and AEP breaker (DEC-435 portfolio-level guard).

## §2.5 Signal universe (~220 fields per ticker per day)

For every ticker on every trading day in the backtest, ~220 fields are computed and made available to strategies + agents. Categories:

**Technical signals (~80 fields):**
- Standard TA: SMA/EMA/WMA at multiple windows, RSI, MACD, ADX, Bollinger Bands, ATR, OBV, MFI, Stochastic, Aroon, CMF
- ICT/SMC primitives: FVG (bullish/bearish, age, fill state), BOS (direction, strength), CHoCH, Order Blocks (zone boundaries, volume, age)
- Chart patterns (DEC-355-362): pattern detected? confidence?
- Multi-timeframe regime (DEC-345): daily / weekly bias

**Smart money signals (~40 fields):**
- Insider trading (Form 4 actuals, Form 144 proposed per DEC-125): net buying/selling, top-buyer count, transaction size relative to ADV
- Congressional disclosures (Quiver paid endpoint per DEC-450): House vs Senate, party, position size
- 13F institutional (Quiver paid + DEC-325 PIT filing_date): top-N holders, position changes Q-over-Q
- Cross-source confluence (DEC-124): agree-strong-buy, agree-strong-sell, conflict
- Exponential decay weighting (90-day half-life per DEC-123)
- Smart money composite (DEC-332 weights)

**Macro signals (~30 fields):**
- FRED expansion 9+ series (DEC-407+448): VIX, DGS10, T10Y2Y, FEDFUNDS, UNRATE, CPIAUCSL, T10YIE, BAA10Y, DXY
- Regime classifier 8+ inputs (DEC-106): VIX + yield curve + HY spread + ICSA + breadth + sector dispersion + AAII + CNN F&G
- Multi-asset extension 12+ inputs (DEC-150): adds DXY, oil, gold, TLT/HYG ratio, sector ETF dispersion
- Sector-level regime (DEC-151): per-XLK/XLE/XLF/etc. regime probabilities

**Sentiment signals (~25 fields):**
- AAII Bull/Bear sentiment (refresh script DEC-319/390)
- CNN Fear & Greed (no interpolation; tuple `(value, last_published_date, age_days)` per DEC-320/391)
- Reddit/social via news sentiment

**Liquidity signals (~15 fields):**
- 20-day rolling ADV (close × volume mean per DEC-366)
- Spread estimate (computed from OHLC range; in Stage 2 backtest, NOT real bid/ask — Polygon Stocks Starter doesn't include quotes per GAP 46 verification)
- Market cap (PIT-correct via Polygon reference per DEC-443)
- Sector / industry classification (PIT-correct)

**Event signals (~30 fields):**
- Days to next earnings (DEC-256 Polygon earnings cache; supersedes yfinance per DEC-444)
- Days since last earnings
- FOMC proximity, CPI release proximity, NFP release proximity
- Dividend ex-date proximity
- Spinoff-from-parent context (DEC-378-380 SEC EDGAR feed)

**~220 total fields per ticker per day.** Many strategies use a small subset; agents consume more breadth.

## §2.6 Agent overlay architecture (TradingAgents Pattern 2)

Stage 2 uses the TradingAgents framework v0.2.4 (open-source, UCLA Tauric Research, Apache 2.0) integrated via Pattern 2 (Pass 29 recommended): use their LangGraph orchestration with our custom toolkits replacing specific defaults.

**12 agent roles per `propagate(ticker, as_of_date)` call (11 active + Reflection):**

```
Phase 1 — ANALYSTS (parallel, 3 active per DEC-057)
  ├── Market Analyst        → OurTechnicalToolkit (DEC-462)
  ├── Fundamentals Analyst  → OurFundamentalsToolkit (DEC-463)
  └── News Analyst          → OurNewsToolkit (DEC-464)
  (Social Media Analyst dropped per DEC-057)

Phase 2 — RESEARCH DEBATE (sequential, multi-round)
  ├── Bull Researcher  ──┐
  ├── Bear Researcher  ──┤── debates max_debate_rounds (default 1-3)
  └── Research Manager ──┘── synthesizes → Pydantic structured output
                              (5-tier rating: Buy/Overweight/Hold/Underweight/Sell)

Phase 3 — TRADER (single)
  └── Trader → OurTraderToolkit (DEC-465); 3-tier output (Buy/Hold/Sell)

Phase 4 — RISK DEBATE (sequential)
  ├── Aggressive Risk Debater  → OurRiskToolkit (DEC-466)
  ├── Conservative Risk Debater → OurRiskToolkit
  ├── Neutral Risk Debater      → OurRiskToolkit
  └── Portfolio Manager → synthesizes Risk Debate; FINAL DECISION
                          (5-tier rating; Pydantic structured output)

Phase 5 — REFLECTION (post-decision)
  └── Reflection Node → writes outcome to persistent decision log
                        (DEC-189 + DEC-267 SQLite/Postgres)
```

**Why Pattern 2 not Pattern 1:**
- Pattern 1 (wrapper) treats TradingAgents as black box — our data sources (Quiver, Polygon, FMP) wouldn't get into agent reasoning
- Pattern 2 extends their toolkits with our data while keeping their LangGraph orchestration, debate logic, structured outputs, persistent decision log
- Effort: ~2-3 weeks for Pattern 2 toolkits (vs ~1 week Pattern 1) but delivers actual agent value-add

**AgentGateConfig (DEC-481 PROPOSED — Option C2 Hybrid; supersedes DEC-459 Option C):**

This is the gate logic that converts TradingAgents output into a trade decision.

**Critical note:** TradingAgents v0.2.4 uses 5-tier rating (Buy/Overweight/Hold/Underweight/Sell) NOT a numeric `confidence: 0.0-1.0` field. SignalProcessor reads rating from rendered markdown via deterministic heuristic — there is no extractable numeric confidence. This was discovered Pass 52 turn 133 via direct verification of TradingAgents source. DEC-459 Option C (numeric confidence) is therefore being superseded by DEC-481 Option C2 (5-tier rating + markdown parser).

**DEC-481 Option C2 gate logic:**

| PM rating | Tier | Position size | Notes |
|---|---|---|---|
| Buy | HIGH | 5% per DEC-021 | Strong conviction |
| Overweight | MEDIUM | 3% | Moderate conviction |
| Hold | LOW | 1.5% (or REJECT — REVISIT_AFTER_BACKTEST) | Owner-discretionary boundary |
| Underweight | REJECT | — | Insufficient conviction for entry |
| Sell | SHORT entry candidate | tier per Buy/Overweight on short side | Symmetric for shorts |

**Risk veto (parsed from rendered Risk Debate output):**
- Risk Debate consensus = "REJECT" or aggressive overrides → veto fires
- Implementation: regex/parser on rendered markdown
- Conservative fallback per #51 — if parsing fails, REJECT

**Bull/Bear alignment via Research Manager:**
- RM rating direction must match PM rating direction (Buy/Overweight = bullish; Underweight/Sell = bearish; Hold = neutral)
- If RM Hold but PM Buy → contested → REJECT
- Direction match → align ✓

**Trader confidence cross-check (Directive 2b):**
- If Trader rating = PM rating (both Buy): high alignment confirmed
- If Trader rating = Hold but PM = Buy: PM overrides; downgrade tier (HIGH → MEDIUM)
- If Trader rating opposes PM (e.g., Trader Sell + PM Buy): REJECT

**A/B framework arms (DEC-473 PROPOSED — reduced from 5 to 3):**

| Arm | Description |
|---|---|
| **A — Rules-only** | Bypass agents entirely; rules-based screen + tier from preliminary smart-money + technical conviction |
| **B — Full-agents-with-veto** | DEC-481 Option C2 default config — PM rating + Risk veto + RM alignment |
| **C — No-Risk** | DEC-481 Option C2 with Risk veto disabled — tests whether Risk veto adds value |

(Eliminated arms moved: D no-align deferred to Sprint 9 ablation; E full ablation deferred to DEC-211 Sprint 9 NARROW SCOPE.)

**Cost (revised per DEC-472 PROPOSED):**

Old paired-design budget math: 5 arms × 300 paired trades × $0.25/propagate = $1500-2000 (5-7× over $300 cap). 

New independent-arms-with-shared-opportunity-set budget math: 300 candidates × $0.25/propagate × 1 propagate per candidate = **$75 for shared TradingAgents calls + $0 for rules-only arm** = $75-225 total. Within $300 budget per DEC-059.

The key insight: TradingAgents `propagate()` is ONE call per candidate. A/B arms differ in HOW the propagate output is GATED, not in WHETHER propagate runs. Same propagate output, different gates. Cost is per-candidate, not per-arm.

## §2.7 Data sources required for Stage 2

Stage 2 requires the following data sources. Polygon tier choice (Stocks Starter $29/mo vs Developer $79/mo vs Advanced $199/mo) is open per DEC-478. My recommendation Pass 52 turn 133: Stocks Developer $79/mo + FMP $14-50/mo = $93-129/mo total.

**Confirmed sources:**

| Source | Purpose | Cost | Status |
|---|---|---|---|
| **Polygon Stocks (tier TBD per DEC-478)** | OHLCV, reference data, news, technical indicators, corporate actions | $29-199/mo | Subscription pending owner direction |
| **FMP (Financial Modeling Prep)** | PIT financials, earnings transcripts, analyst consensus estimates | $14-50/mo | NEW addition pending DEC-461 + DEC-478 |
| **FRED + ALFRED** | Macro data (rates, jobless, CPI, etc.); ALFRED for vintage PIT | Free | Stage 2 use confirmed |
| **Quiver Quantitative paid** | Insider trading (Form 4+144), congressional, 13F, analyst rating changes, government contracts | ~$50-100/mo | Confirmed paid (DEC-450) |
| **Ortex** | Short interest + days-to-cover; squeeze risk | TBD subscription tier ($50-150/mo at point-of-need per DEC-506) | DEC-468 + DEC-506 (Pass 53 timing correction): Stage 2 IN-SCOPE; Sprint 0A Batch 12-d post-subscription; agent integration Sprint 7 (Phase 1B) per Wiring Matrix Row 4 |
| **Polygon Options Starter** | OHLC/OI/IV/chain per-ticker; Risk Agent IV rank/skew/term-structure/max-pain; Sentiment Agent put/call ratios | ~$29/mo separate (point-of-need per DEC-506) | DEC-506 (supersedes DEC-501 Stage 3 deferral): Stage 2 IN-SCOPE; Sprint 0A Batch 12-c post-subscription |
| **smartmoneyconcepts library** | ICT/SMC primitives (FVG/BOS/CHoCH/OB) | Free (forked per DEC-045) | Phase 0.D |
| **AAII** | Bull/Bear sentiment | Free (web scrape) | Refresh script DEC-319/390 |
| **CNN Fear & Greed** | Sentiment index | Free (web scrape) | Refresh script DEC-320/391 |
| **Pandas Market Calendars** | NYSE calendar, holidays, half-days | Free (library) | DEC-235 |

**Demoting / replacing:**
- **yfinance** — demoted to fallback; live calls deprecating per DEC-013/444 (BUG-218 .info CURRENT not as_of)
- **Alpha Vantage** — Stage 1 legacy; demoted per DEC-455
- **Finnhub** — replaced by Polygon news per DEC-440

**API rate limits and caching strategy:**
- Polygon: unlimited API calls per Stocks Starter+ tiers (verified Pass 52 turn 133)
- Quiver: paid tier rate limits TBD (research at Sprint 1 entry)
- FRED: free but rate-limited (~120 requests/min); use caching aggressively
- All sources cached at Parquet level via DEC-040 PointInTimeLoader and DEC-298 raw OHLCV cache

## §2.8 Stage 2 execution flow (rules screen → cube populate → A/B test → verdict)

End-to-end flow during Phase 1B-α run (Sprint 9):

```
DAILY SCAN (one trading day at a time, walk-forward across OOS folds)
                    │
                    ▼
RULES-BASED SCREEN — fires 199 strategies (per CANONICAL_FACTS F-002 Pass 53 + STRATEGY_ROSTER_FULL.md) on Tier 1/2/3 universe
                    │
                    ▼
SCREEN OUTPUT — ranked candidate list (ticker, strategy, preliminary tier,
                                         smart money signal, regime context)
                    │
                    ▼
LIQUIDITY FILTER (DEC-321/366 fail-closed; tier-specific ADV floors)
                    │
                    ▼
EVENT SUPPRESSION (DEC-348/349 — block trades within asymmetric pre/post-event windows)
                    │
                    ▼
PER-TICKER RISK GATES (DEC-018 cooldown + DEC-135 max-loss cap)
                    │
                    ▼
SELECTIVE AGENT OVERLAY — for each candidate that passes filters,
                          call TradingAgents.propagate(ticker, as_of_date)
                    │
                    ▼
A/B SPLIT — run output through 3 arms (rules-only / full-with-veto / no-Risk)
            (rules-only arm uses preliminary tier; agent arms use DEC-481 Option C2 gate)
                    │
                    ▼
TRADE EXECUTION (Portfolio class per DEC-476 — Sprint 3 deliverable)
                    │
                    ▼
COST APPLICATION — slippage (DEC-092/122/280) + commission (DEC-252) + borrow (DEC-399)
                    │
                    ▼
TRADE OUTCOME LOG — per DEC-189 with regime + cell coordinates + arm + result
                    │
                    ▼
CUBE POPULATION — at end of run, group trades by 8-dim cell coordinates,
                  compute per-cell metrics suite
                    │
                    ▼
5-GATE VALIDITY FILTER — FDR q < 0.10 hierarchical (per-strategy, per-cell, per-regime)
                    │
                    ▼
VERDICT ASSIGNMENT — PASS / FAIL_RR / INSUFFICIENT_SAMPLE / FAIL_STAT
                    │
                    ▼
LIVE DECISION LOOKUP TABLE (DEC-429) — populated from PASS cells
                    │
                    ▼
A/B SHARPE COMPARISON — block bootstrap CIs across arms; per-regime verdicts
                    │
                    ▼
DASHBOARDS (DEC-199/200/201) — owner reviews:
  - Cube explorer (DEC-199)
  - ICT/SMC audit (DEC-200)
  - Agent overlay analysis (DEC-201)
                    │
                    ▼
STAGE 2 → STAGE 3 GO/NO-GO (Part 13)
```

**Key timings:**
- One walk-forward fold = ~6 OOS years × 250 days/year × ~509 Tier 1 tickers + variable Tier 2/3 = ~5-8 hours wall time per fold (per Sprint 9 compute estimate)
- 4 OOS folds total (DEC-505 Pass 53 supersedes DEC-109; 1y warmup + 4 OOS × 1y; Polygon Stocks Starter 5y cap): ~20-32 hours wall time
- Cube + verdict + dashboards: ~15 hours additional
- Total Phase 1B-α run: ~37-40 hours wall time (per Sprint 9 compute estimate Part 9 §9.7)

**Local VS Code on Windows laptop (multi-core) sufficient** with parallel folds; no cloud migration needed for Stage 2 (cloud begins Stage 4 per DEC-272).

---

# PART 2.5 — STAGE 2 DASHBOARD COVERAGE MAP (Pass 53)

## §2.5.1 Why this section exists

Stage 2 has 11 phases (0.A through 1C+). Dashboards historically were mentioned only at phases that explicitly produce dashboards as deliverables (1A-α, 1B-α). Pass 53 owner direction: every phase should explicitly state its dashboard coverage — either the dashboard produced/used at that phase, or "N/A" with reason. This section is the canonical cross-phase coverage map. Per-phase mentions live in TRADING_RULES.md §2.1-§2.11 (acceptance criteria) and in the relevant Part of this doc.

## §2.5.2 Three tiers of dashboard coverage

**Tier 1 — Engineering verification dashboards (Phases 0.A-0.E):** infrastructure builds; "dashboard" at most phases is sprint demo + CI test signals, not a Streamlit visualization. Phase 0.A is the exception (Prefetch Coverage Report) since it produces a verifiable artifact (universe × source × hit-rate matrix) that benefits from a one-page HTML view.

**Tier 2 — Analytical baseline dashboards (Phases 1A, 1B):** trade outcomes exist but cube layer not yet built. Each ports the legacy 9-tab interactive dashboard structure (`analysis_dashboard_1a.html` / `analysis_dashboard_1b.html` archived pre-Pass-53) into Streamlit per DEC-430 framework choice — preserves the per-strategy / per-regime / per-trade analytical layer that historical runs proved valuable. Treated as adaptation of DEC-199 family (no new DECs per Pass 53 owner direction).

**Tier 3 — Cube + verdict dashboards (Phases 1A-α, 1B-α, 1C+):** production-spec, already DEC'd:
- DEC-199 Cube Explorer — interactive 8-dimensional cube slice + per-cell drilldown
- DEC-200 ICT/SMC Audit — FVG/BOS/CHoCH/OB validation per ticker per timeframe
- DEC-201 Agent Overlay Analysis — 3-arm A/B comparison + cost vs $300 budget (1B-α only)

## §2.5.3 Per-phase coverage table

| Phase | Sprint | Dashboard | Tier | Effort | Source |
|---|---|---|---|---|---|
| 0.A — Polygon Foundation | 1 | Prefetch Coverage Report (HTML one-off — ticker × source × hit-rate matrix; verifies S&P 500 coverage ≥ 95%; auto-emitted post-prefetch) | Tier 1 | ~0.5d | NEW Pass 53 — adaptation of `backtest_report.html` static HTML pattern (no new DEC) |
| 0.B — Portfolio Class | 3 | **N/A** — Portfolio class is consumed by downstream dashboards (DEC-199/200/201, DEC-476 spec); no own dashboard at this phase | — | 0d | Verification via integration test signals |
| 0.C — Engine Bug Fixes Tier A | 2 | **N/A** — bug fixes verified via CI test signals + sprint demo | — | 0d | Test signals are the verification |
| 0.D — ICT/SMC Fork Integration | 1/4/8 distributed | **Folded into DEC-200** at Phase 1A-α (no separate Phase 0.D dashboard per Pass 53 owner direction) | Tier 3 (consumed) | 0d (folded) | Pass 53 — adaptation of DEC-200 |
| 0.E — Catch-Mechanism Defense + Architecture Hygiene | 6 | **N/A** — pyramid coverage tracked in ENGINEERING_REGISTER per Pass 53 (Sprint 6 owns DEC-437/438/439 framework build); test infrastructure IS the verification | — | 0d | Pass 53 ENGINEERING_REGISTER pyramid-layers field |
| 1A — Rules-Based + Smart Money Baseline | 6.5 | **Phase 1A Trade Summary Dashboard** — Streamlit port of legacy `analysis_dashboard_1a.html` 9-tab structure: (1) per-strategy ranking, (2) regime heatmap, (3) MAE/MFE distribution, (4) equity curve, (5) walk-forward, (6) smart money lift, (7) sector breakdown, (8) skipped trades, (9) circuit breaker log. Precedes cube layer at 1A-α. | Tier 2 | ~2-3d | NEW Sprint 6.5 Pass 53 — adaptation of DEC-199 family (no new DEC) |
| 1A-α — Rules-Only Cube + Dashboards | 6.5-7 | DEC-199 Cube Explorer (rules-only filter) + DEC-200 ICT/SMC Audit | Tier 3 | EXISTING | DEC-199, DEC-200, DEC-487 |
| 1A-β — Production-Scale Validation Run | 7 Day 1 | **REUSE** — DEC-199 + DEC-200 with β-arm filter; no new dashboard | Tier 3 (reuse) | 0d | Reuse of existing |
| 1B — Statistical Methodology + A/B | 7 | **Phase 1B Trade Summary Dashboard** — Streamlit port of legacy `analysis_dashboard_1b.html` 9-tab structure including agent analysis tab (per-arm Sharpe / DD / win rate / debate transcripts where DEC-189 logging operational). Precedes 1B-α cube view. | Tier 2 | ~2-3d | NEW Sprint 7 Pass 53 — adaptation of DEC-199 family (no new DEC) |
| 1B-α — Combined Cube + Dashboards | 7-8 | DEC-201 Agent Overlay Analysis + DEC-199 (3-arm) + DEC-200 (3-arm) | Tier 3 | EXISTING | DEC-201, DEC-199, DEC-200 |
| 1C+ — Strategy Categories Expansion | 8 | **REUSE** — DEC-199/200/201 with new strategy roster populating cube; no new dashboard | Tier 3 (reuse) | 0d | Reuse of existing |

**Total NEW dashboard effort introduced Pass 53:** ~5-7 engineering days (Phase 0.A: ~0.5d, Phase 1A: ~2-3d, Phase 1B: ~2-3d).

## §2.5.4 Adapt-vs-replace decisions for archived dashboards

| Archived artifact | Decision | Rationale |
|---|---|---|
| `analysis_dashboard_1a.html` (Phase 1A 9-tab interactive) | **Adapt** — port 9-tab structure to Streamlit | Pre-Pass-53 archive showed the 9-tab analytical layer was valuable; rebuilding in Streamlit (per DEC-430 framework) preserves consistency with DEC-199/200/201 |
| `analysis_dashboard_1b.html` (Phase 1B 9-tab + agent analysis tab) | **Adapt** — port 9-tab to Streamlit | Same rationale; agent analysis tab requires DEC-189 reflection log to be operational |
| `backtest_report.html` (auto-emitted dark-themed report) | **Keep as-is** — no change | Already produced by `writer.py:_write_html()` every backtest run; sprint-demo-friendly artifact at zero adaptation cost |
| `IMPLEMENTATION_READINESS_DASHBOARD.md` | **Keep as-is** — separate concern | Sprint readiness governance doc, NOT runtime dashboard. Sister to ENGINEERING_REGISTER for sprint planning, distinct from Stage 2 analytical dashboards |

## §2.5.5 Cross-references

- TRADING_RULES.md §2.1-§2.11 — per-phase acceptance criteria including "Dashboards:" callout
- TRADING_RULES.md §2.12 — concise version of this coverage table for quick reference
- ENGINEERING_REGISTER.md Sprint 1 / 6.5 / 7 — effort delta for new dashboard work
- DETAILED_PROJECT_PLAN.md Part 7.6 — Phase 1A-α Cube Explorer detailed spec (DEC-199)
- DETAILED_PROJECT_PLAN.md Part 9 — Phase 1B-α dashboards detailed spec (DEC-201)
- AUDIT.md — Pass 53 entry documenting this section's creation

**Source:** Pass 53 owner direction "Mention dashboards at each phase in stage 2. Analyze and adapt existing dashboards or past dashboard documentation." Approved (1) per-phase mapping, (2) Option A — port 9-tab to Streamlit, (3) fold Phase 0.D into DEC-200, (4) treat as adaptation of DEC-199 family (no new DEC-494/495).

---

# PART 2.6 — SPRINT-SEQUENCED INDEX (Pass 53)

## §2.6.1 Why this section exists

Owner directive Pass 53 turn 2026-05-05: "I need specific sections on each phase and each sprint... read sequentially. Be comprehensive and DO NOT eliminate anything." This index sits between the Stage 2 architecture (Part 2) and the per-phase detail (Parts 3-12) to provide a **chronological sprint flow** that reads top-to-bottom. Existing Phase Parts 3-12 are not renumbered — this index cross-references them. Parts 13-18 (Stage transitions + Cross-cutting + Reading Guide) follow the per-phase parts.

## §2.6.2 Sprint chronology at a glance

```
Foundation    ┌── Sprint 0A ──┐  Multi-API Prefetch + Universe Build + NO-LIVE-API Refactor
              │              │  (Phase 0.A — see Part 3; Pass 53 RENAMED from Sprint 1 per DEC-497)
              │              ▼
Bug fixes     │     Sprint 2   Engine Bug Fixes Tier A
              │              │  (Phase 0.C — see Part 5)
              │              ▼
Risk infra    │     Sprint 3   Portfolio Class
              │              │  (Phase 0.B — see Part 4)
              │              ▼
API hardening │     Sprint 4   DEC-410 API Audit Findings
              │              │  (see Part 11)
              │              ▼
Universe ops  │     Sprint 5   Universe Management automation
              │              │  (see Part 12)
              │              ▼
Defense       │     Sprint 6   Catch-Mechanism Defense + Architecture Hygiene
              │              │  (Phase 0.E — see Part 7)
              │              ▼
1A baseline   │     Sprint 6.5 Phase 1A Rules-Based + Smart Money Baseline
              │              │  (see Parts 7.5, 7.6 — overlaps Sprint 7)
              │              ▼
Statistical   │     Sprint 7   Phase 1A-β + Phase 1B Stat methodology + A/B + Toolkits
              │              │  (see Parts 7.7, 8, 9 dashboards portion)
              │              ▼
Categories    │     Sprint 8   Phase 1C+ Strategy Categories Expansion
              │              │  (see Part 10; ICT/SMC final integration via Part 6 distributed)
              │              ▼
1B-α Run      │     Sprint 9   Phase 1B-α Cube Populate + Verdict Run
              │              │  (see Part 9 run portion + Cube Explorer DEC-199)
Verdict gate  └──────────────▶  Stage 2 → 3 transition (see Part 13)
```

**Sprint 0A naming note (DEC-497, Pass 53 owner directive 2026-05-05):** "Sprint 1" was renamed to "Sprint 0A" to reflect materially expanded scope (multi-API prefetch + universe build absorbed + Stage 2 NO-LIVE-API HARD CUT refactor). Cross-references in Parts 3-12 that say "Sprint 1" are interpreted as Sprint 0A. The Sprint 0A.0-0A.10 sub-phase numbering captures internal sequencing.

## §2.6.3 Sprint-by-sprint table

| Sprint | Phase Mapping | Part | Owner of (deliverable) | Effort | Status (Pass 53) |
|---|---|---|---|---|---|
| **0A** | Phase 0.A | Part 3 | Multi-API prefetch, 5-tier universe build, sector normalization, NO-LIVE-API refactor | ~20.5–26.5d | UNIVERSE BUILD IMPLEMENTED 2026-05-05 (T1a 614, T1c 161, T1 ETFs 27, T2 SCREENER pending, T3 1924); prefetch extension PENDING |
| **2** | Phase 0.C | Part 5 | Engine Bug Fixes Tier A (DEC-491-493 trade_log Parquet, signals_at_entry filter, trade_id schema) | ~25.5–30.5d | NOT STARTED |
| **3** | Phase 0.B | Part 4 | Portfolio class API + state mgmt (DEC-476) | ~8–11d | NOT STARTED |
| **4** | — (cross-cutting) | Part 11 | DEC-410 API audit fixes (yfinance demotion, FMP integration) | ~41.75–54.25d | NOT STARTED |
| **5** | — (cross-cutting) | Part 12 | Universe management automation (monthly refresh workflows for T1a/T1c/T2/T3) | ~13.5–15.5d | PARTIAL — universe-build content done in 0A; ongoing automation pending |
| **6** | Phase 0.E | Part 7 | Catch-Mechanism Defense + Architecture Hygiene (test pyramid framework DEC-437/438/439) | ~62.25–76.75d | NOT STARTED |
| **6.5** | Phase 1A + 1A-α | Parts 7.5, 7.6 | Rules-Based + Smart Money Baseline + Rules-Only Cube + Dashboards | ~25–30d | NOT STARTED |
| **7** | Phase 1A-β + 1B | Parts 7.7, 8 | Phase 1A-β Production-Scale Validation + Phase 1B Statistical + A/B + Custom Toolkits | ~96–108.5d | NOT STARTED |
| **8** | Phase 1C+ + ICT/SMC | Parts 10, 6 (distributed) | Strategy Categories Expansion + ICT/SMC final fork integration | ~37–55d | NOT STARTED |
| **9** | Phase 1B-α run + Cube Explorer | Part 9 (run portion) | 1B-α verdict run + Cube Explorer dashboard (DEC-199) | ~6d engineering + ~37–40h compute wall | NOT STARTED |

## §2.6.4 Sprint 0A — Multi-API Prefetch + Universe Build + NO-LIVE-API Refactor

**Owner directive 2026-05-05 (DEC-497):** Sprint 1 renamed → Sprint 0A with materially expanded scope. Sprint 0A is the primary active sprint of Pass 53. Detail in Part 3.

**Sprint 0A sub-phase breakdown (0A.0 - 0A.10):**

| Sub-phase | Deliverable | Status (Pass 53) |
|---|---|---|
| **0A.0** | Universe build: T1a S&P 500 (614 rows: 503 active + 111 historical), T1c NASDAQ-100 (161 rows: 101 active + 60 historical), T1 ETFs (27), T2 spinoffs/IPOs (SCREENER global pull pending), T3 momentum top-100 (1924 rows after leveraged-ETF blocklist fix) | IMPLEMENTED 2026-05-05; T2 final state pending background SCREENER completion |
| **0A.1** | Polygon EXTENSION prefetch — news / financials / events / NBBO daily-close | NOT STARTED — owner-gated per CHECKLIST #68 smoke→demo→full protocol |
| **0A.2** | FRED + ALFRED 52-series prefetch (curating to ~15-20 high-signal subset per Pass 53 turn analysis) | NOT STARTED |
| **0A.3** | AAII + CNN F&G prefetch (composite + 7 sub-components per owner direction Pass 53) | NOT STARTED |
| **0A.4** | CFTC COT prefetch (commercial vs speculative positioning) | NOT STARTED |
| **0A.5** | Quiver Trader-tier prefetch — 10 endpoint groups (DEC-502: news, off-exchange, top-shareholders, ETF holdings, SEC13F, patents, exec comp, corporate donors, congress politicians, off-exchange-historical); BULK migration where dashboard provides Bulk variant; per CHECKLIST #68 protocol | NOT STARTED — silent-gap fix for `historical/insidertrading` + `historical/institutionalholdings` URL paths required first (smart_money.py fix; Pass 53 turn 2026-05-05 finding) |
| **0A.6** | SEC EDGAR structured prefetch via edgartools (Form 4, 8-K, 10-Q/K) | NOT STARTED |
| **0A.7** | Free social sentiment supplementary sources — **Apewisdom** (WSB/Reddit ticker mentions, 2021-present, daily) + **Google Trends via pytrends** (search-volume index by ticker, 2004-present); approved Pass 53 owner Q2 2026-05-05 (DEC-502 supplement) | NOT STARTED |
| **0A.8** | Stage 2 NO-LIVE-API refactor — `backtest/data/{fetcher,macro,sentiment,smart_money}.py` migration to read from `data_prefetch/` only; HARD CUT (DEC-497 Q8 owner directive) | NOT STARTED |
| **0A.9** | Polygon ticker events integration (DEC-500 Pass 53 owner directive — corp action triggers as agent context: splits / mergers / name changes / listing changes / delistings / exchange changes); Polygon `/vX/reference/tickers/{ticker}/events`; feeds T2 SCREENER + Risk Agent + Sentiment Agent + Fundamental Agent | NOT STARTED |
| **0A.10** | Smoke + demo + full tests per API (16 test files: 8 smoke + 8 demo) per CHECKLIST #68 protocol; full test pyramid per CHECKLIST #69 (DEC-503) | NOT STARTED |

**Sprint 0A scope-out (per Pass 53 owner Q1 directive 2026-05-05):**
- Polygon Options Starter — Pass 53 owner correction 2026-05-05 (DEC-506 supersedes DEC-501): Stage 2 IN-SCOPE; subscription deferred to point-of-need; Batch 12-c added to Sprint 0A pending subscription
- Polygon SMA/EMA/RSI/MACD indicator endpoints — DROPPED (duplicates local pandas-ta; Risk Agent uses ATR backward-looking until options scope-in)
- Polygon NBBO intraday quotes / snapshots / market-status / tick trades — DEFERRED to Stage 3+ live trading

**Critical silent-gap finding (Pass 53 smoke test 2026-05-05):**
3 Quiver endpoints in current code return HTTP 404 for AAPL — **smart_money.py has been silently broken**:
- `historical/analystestimates/{ticker}` → NOT IN TRADER TIER. Smart_money.get_analyst_data Quiver-enhancement branch dead. Migration: REMOVE Quiver branch; rely on Polygon financials (per DEC-497 HARD CUT). Logged as BUG-271.
- `historical/insidertrading/{ticker}` → NOT IN TIER under this path. Migration: `live/insidertrading` (bulk feed; client-side ticker filter). Logged as BUG-272.
- `historical/institutionalholdings/{ticker}` → NOT IN TIER. Migration: `live/sec13f` (10,000-row paginated bulk feed). Logged as BUG-273.

**Impact:** smart_money_score has been computing on 1-of-3 inputs (only congressional). Insider + institutional silently zeroed across all Phase 1A v3 archive results. Fix scheduled next turn with full test pyramid per DEC-503.

## §2.6.5 Sprint dependencies

```
Sprint 0A ──┬──► Sprint 2 (engine fixes operate on cache produced by Sprint 0A)
            ├──► Sprint 3 (Portfolio class queries OHLCV via Sprint 0A cache)
            ├──► Sprint 4 (DEC-410 audit assumes Sprint 0A polygon_client exists)
            └──► Sprint 5 (universe automation; T1a/T1c/T2/T3 schemas locked in 0A)

Sprint 2 ────► Sprint 6 (catch-mechanism operates on stable engine surface)

Sprint 3 ────► Sprint 6.5 (Portfolio class consumed by Phase 1A baseline run)

Sprint 6 ────► Sprint 7 (architecture hygiene + custom toolkits in tandem)

Sprint 6.5 ──► Sprint 7 (Phase 1A baseline → 1A-β + 1B advanced; some overlap)

Sprint 7 ────► Sprint 8 (Phase 1B + Strategy Categories Expansion overlap)
              └─► Sprint 9 (cube populate run after toolkits + statistical methodology stable)

Sprint 8 ────► Sprint 9 (Phase 1C+ rosters fold into 1B-α run)

Sprint 9 verdict ──► Stage 2 → 3 transition (Part 13)
```

## §2.6.6 Cross-document map

- **PROJECT_PLAN.md** — quick-reference card; original index
- **CHECKLIST.md** — 69 items including new #69 (test pyramid per DEC-503), #68 (smoke→demo→full protocol), #67 (per-turn doc sync)
- **AUDIT_INDEX.md** — DEC list (currently DEC-001 through DEC-503)
- **AUDIT.md** — full decision narrative + Pass 53 events
- **TRADING_RULES_AND_INFORMATION.md** — canonical thresholds + per-phase acceptance criteria §2.1-§2.11
- **TRADINGAGENTS_DATA_AUDIT.md** — agent data dependency mapping (revised Pass 53 for new endpoint scope)
- **API_AUDIT.md** — per-API endpoint inventory (Polygon, Quiver Trader, FRED/ALFRED, AAII, CNN F&G, CFTC COT, SEC EDGAR, Apewisdom, pytrends)
- **THEME_X53_SEQUENCING.md** — Pass 53 sequencing detail (Sprint 0A.0-0A.10)
- **STRATEGY_REGISTER.md** — strategy roster (Layer 1+2+3+4, ~199 strategies (per CANONICAL_FACTS F-002 Pass 53 + STRATEGY_ROSTER_FULL.md))
- **ENGINEERING_REGISTER.md** — sprint planning, effort estimates, pyramid coverage
- **BUG_REGISTER.md** — bug log including BUG-271/272/273 (smart_money silent gaps Pass 53)

---

# PART 3 — SPRINT 0A: PHASE 0.A POLYGON FOUNDATION + MULTI-API PREFETCH + UNIVERSE BUILD + NO-LIVE-API REFACTOR (DEC-497 expanded scope)

## §3.1 What — concrete deliverable in plain English

Phase 0.A produces the **data foundation** for Stage 2 backtest. By the end of Sprint 1, the backtest engine can pull point-in-time-correct OHLCV data, corporate actions, reference data (sector, market cap, GICS classification), and macro/sentiment data for any S&P 500 ticker on any historical date back to the start of the cache window — without lookahead bias, with proper survivorship correction, and with deterministic cache behavior.

Concrete deliverables:

1. **Polygon API integration** — `backtest/data/polygon_client.py` wrapping Polygon REST API for: OHLCV daily aggregates, OHLCV minute aggregates, reference data, corporate actions (splits/dividends), news endpoint, technical indicators endpoint. API key stored in environment variable; rate limiting respected; failures retry with exponential backoff per DEC-260.

2. **`PointInTimeLoader` base class (DEC-040)** — `backtest/data/pit_loader.py` abstract class that all PIT-aware fetchers inherit from. Defines `fetch(ticker, as_of_date, **kwargs)` contract: returns data WHERE all rows have `published_date ≤ as_of_date`. Includes edge case handlers: weekend `as_of` (returns last trading day's data), pre-IPO `as_of` (returns empty + warning), post-delist `as_of` (returns up to delisting), partial cache (re-fetch missing range; fail-fast per DEC-260).

3. **OHLCV cache layer** — `backtest/data/cache_ohlcv.py` Parquet cache for raw OHLCV with `auto_adjust=False` semantics (DEC-298). Adjusted-on-demand recomputation by `as_of` date using corporate actions table — meaning if today is 2024-06-15 and we ask for AAPL price on 2020-06-15 with as_of=2020-06-15, we recompute the adjustment factors using only splits/dividends that occurred BEFORE 2020-06-15.

4. **Polygon S&P 500 prefetch** — bulk download of OHLCV for all 509 Tier 1 tickers (S&P 500 constituents per `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` + selected sector/macro ETFs) for the cache window (depth depends on DEC-478 tier choice — Stocks Starter $29 = 5yr; Developer $79 = 10yr; Advanced $199 = 20yr).

5. **Cache hygiene infrastructure (DEC-329)** — disk usage monitoring (warn at 80% / hard fail at 95% per DEC-243), filelock for multi-process safety (DEC-431, 5s timeout), cache eviction policy distinguishing prefetched vs dynamically-fetched files (DEC-244 — prefetched files marked with metadata file `.prefetch.lock` for LRU exemption).

6. **FRED expansion to 9+ series (DEC-407+448)** — `backtest/data/fred_client.py` fetches VIX, DGS10 (10y treasury), T10Y2Y (yield curve), FEDFUNDS, UNRATE, CPIAUCSL, T10YIE (breakeven inflation), BAA10Y (HY spread proxy), DXY. ALFRED used for vintage PIT correction.

7. **AAII + CNN F&G refresh scripts** — `.github/workflows/refresh_aaii.yml` and `.github/workflows/refresh_cnn_fg.yml` cron jobs (weekly Thursday for AAII; daily for CNN F&G with 1-day lag respected per DEC-320). Output committed to `data/sentiment/aaii.parquet` and `data/sentiment/cnn_fg.parquet`. AAII/CNN F&G domains accessible from local VS Code (no allowlist needed); historical Codespace allowlist concern moot.

8. **Polygon reference replacing yfinance.info (DEC-443)** — sector classification, market cap, exchange, listing dates pulled from Polygon Reference Data endpoint instead of yfinance.info (which has no as_of date support and BUG-218 returns CURRENT not as_of).

9. **Polygon earnings cache (DEC-256, replacing yfinance per DEC-444)** — `backtest/data/polygon_earnings.py` fetches historical earnings dates + EPS actuals + estimates. Cache key: ticker + earnings_date. PIT-aware via filing_date.

10. **Cache freshness rules implemented (DEC-260)** — OHLCV cache stale threshold 1 day; sentiment 7 days; fundamentals 90 days. Stale cache → re-fetch (not silent staleness).

## §3.2 Why — how this advances Stage 2 toward verdict

The verdict cube (Part 2 §2.2) cannot be populated without trade outcomes. Trade outcomes cannot be computed without prices. Prices must be PIT-correct or the entire backtest is contaminated by lookahead bias. Therefore: **no Phase 0.A foundation = no valid Stage 2 verdict.**

Specific dependencies that justify Phase 0.A as Sprint 1:

- **Sprint 2 (engine bug fixes Tier A)** operates on cache produced by Sprint 1; if cache schema changes mid-Sprint-2, fixes refer to obsolete schema. Phase 0.A defines schema first.
- **Sprint 3 (Portfolio class)** queries OHLCV for current market values via `update_market_values(prices, as_of)`. Needs cache layer.
- **Sprint 5 (universe management)** builds Tier 2/3 universes which depend on `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` PIT correctness — established in Sprint 0A.
- **Sprint 6 (catch mechanism + hygiene)** operates against established cache + reference data conventions.
- **Sprint 7 (custom toolkits)** — every OurTechnicalToolkit / OurFundamentalsToolkit / OurNewsToolkit method calls Polygon via the Sprint 1 client.
- **Sprint 9 (Phase 1B-α run)** is the cube populate; pulls everything cached during Sprint 1 + Sprint 4.

Phase 0.A is the literal foundation; if it's wrong, all subsequent work compounds the error.

## §3.3 How — components, data flow, dependencies

**Component diagram:**

```
backtest/data/
├── polygon_client.py          # Raw Polygon REST API wrapper
├── pit_loader.py              # Base PointInTimeLoader class (DEC-040)
├── cache_ohlcv.py             # Parquet cache, raw + corp-action-adjusted
├── cache_fundamentals.py      # FMP cache (Sprint 4 if DEC-461 approved)
├── fred_client.py             # FRED + ALFRED PIT
├── refresh_aaii.py            # Sentiment refresh (AAII)
├── refresh_cnn_fg.py          # Sentiment refresh (CNN F&G)
├── polygon_earnings.py        # Earnings cache (replaces yfinance)
├── polygon_reference.py       # Sector/cap/exchange (replaces yfinance.info)
├── corporate_actions.py       # Splits + dividends + spinoffs (DEC-146)
└── cache_monitor.py           # Disk usage + filelock + LRU
```

**Data flow during a backtest call:**

```
Strategy.compute(ticker='AAPL', as_of_date='2022-06-15')
        │
        ▼
PriceLoader.fetch_ohlcv(ticker='AAPL', as_of_date='2022-06-15', lookback_days=250)
        │
        ▼ checks cache_ohlcv.parquet (filelock-protected)
        │
        ├── HIT → return Parquet rows where date ≤ '2022-06-15' (PIT slice)
        │       │
        │       └── apply corp action adjustments using actions where action_date ≤ '2022-06-15'
        │
        └── MISS → polygon_client.get_aggs(ticker, multiplier=1, timespan='day',
                                            from_date=cache_start, to_date='2022-06-15')
                  │
                  ▼ writes to cache_ohlcv.parquet
                  │
                  ▼ filelock release
                  │
                  └── return PIT-sliced + adjusted DataFrame
        │
        ▼
Strategy gets DataFrame; computes signal
```

**Dependencies:**
- **External:** Polygon API key (owner action — Sprint 0 prerequisite); FRED API key (free); GitHub Actions runner has secrets for cron jobs
- **Internal:** none — this is the foundational layer
- **Library:** `polygon-api-client` (PyPI), `fredapi`, `pyarrow` (Parquet), `filelock`, `pandas`, `pandas-market-calendars`, `requests`, `freezegun` (for PIT testing)

**Key design decisions in scope (with one-line summaries):**
- DEC-040 — PointInTimeLoader base class establishes PIT contract for all data
- DEC-260 — Cache freshness fail-closed (stale → re-fetch, not silent staleness)
- DEC-298 — `auto_adjust=False`: cache stores raw; adjust on demand
- DEC-243 — Disk monitoring 80% warn, 95% hard fail
- DEC-244 — LRU eviction distinguishes prefetched (exempt) vs dynamic
- DEC-329 — Multi-process safe globals via filelock
- DEC-431 — Filelock 5s timeout
- DEC-407+448 — FRED 9+ series + ALFRED PIT
- DEC-256 + 444 — Polygon earnings replaces yfinance earnings
- DEC-443 — Polygon reference replaces yfinance.info
- DEC-303 + 477 PROPOSED — `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` canonical S&P 500 (deprecates 482-CSV static)

## §3.4 When — sequence, blockers, parallel-ability

**Sequence within Sprint 0A (Week 1):**

| Day | Task | Blocker resolved by Day |
|---|---|---|
| 1 | Polygon API key set up + smoke test (1 ticker, 1 month) | Sprint 0 owner action |
| 2 | `PointInTimeLoader` base class + tests (no fetcher yet, just contract) | Day 1 |
| 3 | `polygon_client.py` — get_aggs + reference + corp actions | Day 1 |
| 4 | `cache_ohlcv.py` Parquet cache + filelock | Day 3 |
| 5 | Cache hygiene + disk monitor + LRU exemption | Day 4 |
| 6-7 | S&P 500 bulk prefetch + verification | Day 5 |
| 8 | FRED + ALFRED 9+ series cache | parallel with prefetch |
| 9 | AAII + CNN F&G refresh scripts + workflow | parallel; (Codespace allowlist concern moot — running locally on VS Code) |
| 10 | Polygon earnings cache | Day 6 |
| 11 | Polygon reference replacing yfinance.info | Day 6 |
| 12-14 | Edge case tests (weekend/holiday/pre-IPO/post-delist/partial cache) | Day 5 |
| 15-20 | Integration tests + freezegun PIT verification + bug fixes | Days 6-14 |

**Total: ~20 working days** (Sprint 1 baseline; +1 day if owner approves DEC-478 Polygon Stocks Developer requiring re-fetch with deeper history).

**Parallel-ability:**
- Sprint 1 ↔ Sprint 2 (engine bug fixes): **parallel** — Sprint 2 fixes operate on existing engine code, not on Sprint 1's new cache layer; coordination only at integration test (end of Sprint 2)
- Sprint 1 ↔ Sprint 4 (DEC-410 audit findings): partially parallel — Sprint 4 includes DEC-442 (yfinance demotion) which depends on Sprint 1's polygon_client; so Sprint 4 starts mid-Sprint-1
- Sprint 1 ↔ Sprint 3 (Portfolio class): **sequential** — Sprint 3 needs Sprint 1's PriceLoader; Sprint 3 starts after Sprint 0A Day 5

**Blockers (must resolve before Sprint 1 starts):**
1. Owner subscribes to Polygon (Sprint 0 action; tier per DEC-478 owner decision)
2. DEC-460 verification: does Polygon Stocks Starter cover PIT fundamentals? (Pre-Sprint-1 verification; result Pass 52 turn 133 = NEGATIVE)
3. DEC-461 conditional FMP subscription (now MANDATORY per DEC-460 verification negative)
4. Universe definition resolved: 482-CSV vs `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` (DEC-477 owner approval)

## §3.5 Done criteria — verifiable acceptance

Sprint 1 is RESOLVED-IMPLEMENTED when ALL of these are demonstrably true:

- [ ] `polygon_client.py` connects to Polygon API; `get_aggs(ticker, ...)` returns DataFrame; rate limit headers respected
- [ ] `PointInTimeLoader` base class has full test coverage including 5 edge cases (weekend/holiday/pre-IPO/post-delist/partial-cache)
- [ ] `cache_ohlcv.py` stores Parquet; `fetch(ticker, as_of)` is PIT-correct verified via freezegun (set system time to a past date and confirm only pre-date rows returned)
- [ ] All 509 Tier 1 tickers have OHLCV cache covering at minimum 5 years (Polygon Stocks Starter floor) or 10 years if Developer chosen
- [ ] Filelock works under multi-process stress test (5 workers writing to same cache file)
- [ ] Disk monitor warns at 80% and hard-fails at 95%
- [ ] LRU eviction does NOT remove `.prefetch.lock`-marked files
- [ ] FRED 9+ series cached; ALFRED vintage PIT verified for at least 3 series
- [ ] AAII + CNN F&G workflows running successfully in GitHub Actions; data committed to `data/sentiment/`
- [ ] Polygon earnings cache covers all Tier 1 tickers; earnings_date PIT-respected
- [ ] Polygon reference replaces yfinance.info: sector/cap/exchange returned PIT-correct (resolves BUG-218)
- [ ] `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` canonicalized; static 482-CSV deprecated with deprecation warning
- [ ] Sprint 1 PR merged to main; CI green; integration tests pass; cache integrity verified post-merge

## §3.6 Risks — what could go wrong specifically

**Risk R-1: Polygon rate limiting unexpected**
- Polygon Stocks Starter+ advertises "unlimited API calls" but rate-related throttles may exist for specific endpoints (e.g., bulk historical fetches)
- Mitigation: implement exponential backoff + 429-aware retry per DEC-260; verify rate behavior on Day 1 smoke test
- If hit during prefetch: spread bulk fetch across multiple sessions, throttle to ~5 req/s

**Risk R-2: Polygon historical depth shorter than expected**
- Stocks Starter = 5 years per polygon.io/pricing verification
- 5 years from May 2026 = May 2021 onwards; insufficient for DEC-109 5-year-train; CORRECTED via DEC-505 Pass 53 owner directive 2026-05-05 (1y warmup + 4 OOS × 1y within available 5y window)
- Mitigation: DEC-478 owner decision to upgrade to Stocks Developer ($79/mo, 10 years) covering 2016-2026 for OOS folds 2021-2026
- If owner declines upgrade: walk-forward train window must reduce; this is a Sprint 7 architectural change

**Risk R-3: AAII or CNN F&G domains intermittently fail to load (network/site issues, not allowlist — running locally on VS Code now)**
- Stage 1 lesson: Wikipedia was blocked
- Mitigation: Sprint 0 Day 1 verification — `curl https://www.aaii.com/...` and `https://production.dataviz.cnn.io/...` from local VS Code; if fails, investigate site availability or DNS
- If still blocked: scrape locally on Windows laptop, commit Parquet to repo (manual refresh)

**Risk R-4: PIT correctness regression during cache writes**
- Race condition: process A reads cache at time T; process B writes cache at T+1; process A's read result has stale + new mixed
- Mitigation: filelock per DEC-431 ensures atomic write; reads acquire shared lock
- Test: stress test with `pytest-xdist` running 8 parallel workers

**Risk R-5: Corporate action data quality**
- Polygon corp actions feed has known issues per Polygon community (missing dividends, late splits)
- Mitigation: cross-reference with yfinance corp actions for Tier 1 tickers (sample); flag discrepancies; manual override file for critical tickers
- If material errors: backtest results contaminated; budget 2-3d in Sprint 1 for corp action validation

**Risk R-6: Filelock starvation under heavy contention**
- 5s timeout (DEC-431) — under heavy parallel-fold runs, lock acquisition could fail
- Mitigation: instrument lock wait time; if p95 > 1s, increase timeout or reduce fold parallelism
- Action item: monitor during Sprint 9 Phase 1B-α run

**Risk R-7: yfinance dependency lingering**
- yfinance demoted but not deleted — code still imports it; if Polygon endpoints fail, code might silently fall back to yfinance and contaminate with non-PIT data
- Mitigation: Sprint 4 (DEC-442/443/444) explicitly removes yfinance from production paths; integration test checks no yfinance imports in core data path

## §3.7 Cost — engineering days + dollars

**Engineering effort:**
- Polygon client + PointInTimeLoader: 4d
- OHLCV cache: 4d
- Bulk prefetch: 3d (data fetch wall time + verification)
- Cache hygiene: 2d
- FRED + ALFRED: 2d
- Sentiment refresh: 2d (AAII + CNN F&G with allowlist verification)
- Polygon earnings cache: 1d
- Polygon reference: 1d
- Corp actions validation: 2d (R-5 mitigation)
- Edge case tests: 3d
- Integration + bug fixes: 4d

**Total: ~28d realistic; ~20.5d minimum with parallel-able overlaps.**

**Dollar cost (subscriptions for Sprint 1 alone):**
- Polygon: $29-79/mo per DEC-478 owner decision (recommend $79 Developer)
- FRED: free
- ALFRED: free
- FMP (if DEC-461 approved): $14-50/mo (Sprint 4 onward; not Sprint 1 critical path)
- Quiver: not Sprint 0A (Sprint 4 onward)

**Sprint 1 incremental monthly subscription: $29-79/mo (Polygon only).**

## §3.8 Decisions in scope — list with one-line summaries

| DEC | Title | Status |
|---|---|---|
| 040 | PointInTimeLoader base class — PIT contract for all fetchers | RESOLVED-DECIDED |
| 045 | Fork-existing strategy across Phase 0 (smartmoneyconcepts) | RESOLVED-DECIDED — distributed across Sprints 1/4/8 |
| 052 | CC0 dataset for delisting (free Kaggle alternative) | RESOLVED-DECIDED |
| 103 | IPO universe: ≥$2B cap + 20-day-min history | RESOLVED-DECIDED |
| 104 | Momentum top-100 watchlist refresh monthly | RESOLVED-DECIDED |
| 118 | Tier 1 includes selected ETFs (VIX/DXY/GLD/oil/sectors) | RESOLVED-DECIDED |
| 146 | Corporate actions table — splits + dividends + spinoffs | RESOLVED-DECIDED |
| 235 | pandas_market_calendars for NYSE calendar | RESOLVED-DECIDED |
| 243 | Disk monitor 80% warn + 95% hard fail | RESOLVED-DECIDED |
| 244 | LRU eviction with prefetched file exemption | RESOLVED-DECIDED |
| 256 | Polygon earnings cache | RESOLVED-DECIDED |
| 260 | Cache freshness fail-closed | RESOLVED-DECIDED |
| 298 | Raw OHLCV cache + adjusted-on-demand | RESOLVED-DECIDED |
| 303 | Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv (PIT S&P 500 membership) | RESOLVED-DECIDED |
| 319 | AAII refresh script | RESOLVED-DECIDED |
| 320 | CNN F&G — no interpolation; tuple (value, last_published_date, age_days) | RESOLVED-DECIDED |
| 329 | Multi-process safe globals via filelock | RESOLVED-DECIDED |
| 390 | AAII workflow in GitHub Actions | RESOLVED-DECIDED |
| 391 | CNN F&G workflow in GitHub Actions | RESOLVED-DECIDED |
| 407 | FRED 8-input baseline | RESOLVED-DECIDED |
| 411 | Cache extension to 2018-01-01 (depth depends on tier) | BLOCKED on DEC-298 + DEC-478 |
| 431 | Filelock 5s timeout | RESOLVED-DECIDED |
| 443 | Polygon reference replacing yfinance.info | RESOLVED-DECIDED |
| 444 | Polygon earnings deprecating yfinance earnings | RESOLVED-DECIDED |
| 448 | FRED 9+ series expansion | RESOLVED-DECIDED |
| 460 | Verify Polygon Stocks Starter PIT fundamentals — RESULT NEGATIVE | RESOLVED-DECIDED |
| 461 | Subscribe FMP if Polygon insufficient — NOW MANDATORY | RESOLVED-DECIDED conditional |
| 477 PROPOSED | Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv canonical; deprecate 482-CSV | Awaits owner approval |
| 478 PROPOSED | Polygon tier upgrade decision (Starter $29 / Developer $79 / Advanced $199) | Awaits owner approval |
| 479 PROPOSED | DEC-441 cost correction $30 → $29 (or revised per DEC-478) | Awaits owner approval |

## §3.9 Test approach — how the deliverable is verified

**Unit tests** (per file in `backtest/data/`):

- `test_polygon_client.py` — mock Polygon responses; verify request format, header parsing, rate-limit retry, error handling
- `test_pit_loader.py` — abstract class contract tests; subclass mock; edge cases (weekend/holiday/pre-IPO/post-delist/partial-cache) with parametrized inputs
- `test_cache_ohlcv.py` — write/read cycle; PIT slicing; corp action adjustment math; filelock contention
- `test_corporate_actions.py` — known split (e.g., AAPL 4:1 split 2020-08-31) reproduces correctly; known dividend reproduces

**Integration tests** (in `tests/integration/`):

- `test_pit_freezegun.py` — freezegun freezes system time to a past date; full backtest data path called; verify NO data with `published_date > frozen_date` is returned
- `test_polygon_to_strategy.py` — end-to-end: Polygon fetch → cache → PIT slice → strategy compute → signal output
- `test_multi_process_cache.py` — pytest-xdist 8 workers writing to cache; integrity check post-run

**PIT regression suite** (per DEC-417 catch-mechanism Sprint 6):

- `test_pit_regression.py` — runs same backtest on 2022-06-15 with as_of=2022-06-15 vs as_of=2024-06-15; results MUST be identical (no future data leakage)

**Smoke tests** (CI on every commit per DEC-241):

- 1-ticker / 1-month fetch in CI; if breaks, deployment blocked

**Acceptance test** (Sprint 1 close):

- "Reproduce Pass 32 hand-validated AAPL 2020 backtest using Sprint 0A cache; results match within 0.5% per DEC-218 numerical tolerance" — owner-witnessed demo

## §3.10 Data dependencies — what feeds in, where it comes from, what's downstream

**Inputs to Phase 0.A:**

| Input | Source | Sprint 0 verification |
|---|---|---|
| Polygon API key | Owner subscription | Required Day 1 |
| FRED API key | Free signup | Required Day 8 |
| `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` | DEC-303 SEC filings + Wayback Machine archive | Pre-existing; verify in Sprint 0 |
| AAII URL accessible | https://www.aaii.com/sentimentsurvey | Sprint 0 verify on local VS Code (Pass 53 R7-03 fix; was Codespace allowlist) |
| CNN F&G URL accessible | https://production.dataviz.cnn.io/index/fearandgreed/graphdata | Sprint 0 verify |
| Owner-confirmed cache directory path | `/workspaces/stock-picks-app/data/cache/` | None |
| Local VS Code disk available (Pass 53 R7-03 fix; was Codespace disk) | ≥ 32GB free | Sprint 0 verify (Stocks Starter 5-year cache ≈ 8-12GB) |

**Outputs (consumed by downstream sprints):**

| Output | Format | Consumer |
|---|---|---|
| OHLCV cache | Parquet `data/cache/ohlcv/{ticker}.parquet` | All sprints — strategies, agents, Portfolio class |
| Corp actions table | Parquet `data/cache/corp_actions.parquet` | OHLCV adjustment, exit calculations |
| Polygon reference | Parquet `data/cache/reference.parquet` | Sector/cap/exchange queries throughout backtest |
| Polygon earnings | Parquet `data/cache/earnings.parquet` | Earnings strategies (Layer 2), event suppression DEC-348 |
| FRED series | Parquet `data/cache/fred/{series_id}.parquet` | Regime classifier (Sprint 6), agents |
| AAII data | Parquet `data/sentiment/aaii.parquet` | Regime classifier, sentiment signals |
| CNN F&G data | Parquet `data/sentiment/cnn_fg.parquet` | Regime classifier, sentiment signals |
| `PointInTimeLoader` ABC | Python class | All Sprint 1+ fetchers inherit |

**Downstream impact:**
- Cache schema changes here propagate to ALL subsequent sprints
- If Sprint 1 emerges with a different schema than planned, Sprint 2 (engine bug fixes) and Sprint 4 (DEC-410) need adjustment
- Therefore: **schema must be locked by end of Sprint 1 Day 5** so Sprint 2/3/4 can build against stable interface

## §3.11 Operational checklist — week-by-week

**Week 1 (Days 1-5) — Foundation:**
- [ ] Day 1 morning: Polygon API key in env var; smoke test 1 ticker / 1 month
- [ ] Day 1 afternoon: PointInTimeLoader ABC + test scaffold
- [ ] Day 2: polygon_client.py get_aggs + retry logic
- [ ] Day 2: corp actions endpoint + table
- [ ] Day 3: polygon_client.py reference data + earnings
- [ ] Day 3: cache_ohlcv.py Parquet writer + reader
- [ ] Day 4: filelock + multi-process test
- [ ] Day 4: disk monitor + LRU exemption
- [ ] Day 5: schema lock — reviewable schema doc; informs Sprint 2/3/4

**Week 2 (Days 6-10) — Bulk + Auxiliary:**
- [ ] Day 6: S&P 500 bulk prefetch (background; 8-12GB)
- [ ] Day 7: prefetch verification (no missing tickers)
- [ ] Day 8: FRED 9-series cache + ALFRED PIT
- [ ] Day 9: AAII + CNN F&G refresh scripts; verify domains accessible on local VS Code (Pass 53 R7-03 fix; was Codespace allowlist)
- [ ] Day 9: GitHub Actions workflow for refreshes
- [ ] Day 10: Polygon earnings cache + Polygon reference replacing yfinance.info

**Week 3 (Days 11-15) — Hardening:**
- [ ] Day 11: corp actions validation against yfinance reference (R-5 mitigation)
- [ ] Day 12: edge case tests (weekend/holiday/pre-IPO/post-delist/partial-cache)
- [ ] Day 13: PIT regression freezegun suite
- [ ] Day 14: integration tests + multi-process stress
- [ ] Day 15: bug fixes from Days 11-14

**Week 4 (Days 16-20) — Acceptance:**
- [ ] Day 16-17: AAPL 2020 hand-validated backtest reproduction (acceptance demo)
- [ ] Day 18: documentation in TRADING_RULES §13 cache rules
- [ ] Day 19: Sprint 1 PR review
- [ ] Day 20: merge to main; ENGINEERING_REGISTER Sprint 0A → RESOLVED-IMPLEMENTED

## §3.12 Open issues — gaps from ADVERSARIAL_AUDIT relevant to this phase

From `ADVERSARIAL_AUDIT_PASS_52_TURN_132.md`, gaps directly affecting Phase 0.A:

- **GAP 1:** Polygon subscription timing — when does owner subscribe relative to other Sprint 0 actions?
  - Resolution: Sprint 0 Day 1 prerequisite; if owner delays, Sprint 1 Day 1 blocked
- **GAP 2:** API key procedure — storage, testing, what-if-down
  - Resolution: env var (`POLYGON_API_KEY`); smoke test Day 1; failover N/A in Sprint 0A (multi-vendor fallback Stage 4 per DEC-160)
- **GAP 13:** PIT loader class skeleton not specified
  - Resolution: §3.3 component diagram + §3.5 done criteria specifies ABC contract
- **GAP 14 (CRITICAL):** PIT loader edge cases not documented
  - Resolution: §3.1 deliverable #2 explicitly lists 5 edge cases (weekend/pre-IPO/post-delist/partial-cache); §3.5 done criteria gates them
- **GAP 15 (CRITICAL):** Two universes (482 vs `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv`)
  - Resolution: DEC-477 — `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` canonical; static 482-CSV deprecated. Sprint 1 Day 19 deprecation warning added.
- **GAP 17:** Polygon raw vs adjusted — equivalent of `yfinance auto_adjust=False`
  - Resolution: §3.1 deliverable #3 — raw OHLCV stored; adjusted-on-demand recomputation per DEC-298
- **GAP 18:** Adjusted recompute formula not specified
  - Resolution: standard split-adjusted formula `adj_close = close * Π(1/split_ratio for splits after as_of)` and `adj_close += dividend_per_share for ex-dates after as_of` — to be encoded in `corporate_actions.py` Day 11
- **GAP 19:** Prefetched vs dynamically-fetched filesystem distinction
  - Resolution: §3.1 deliverable #5 — `.prefetch.lock` metadata file marks prefetched; LRU eviction skips marked files
- **GAP 20:** 95% disk hard fail downstream impact
  - Resolution: hard-fail with clear error message; runbook entry in TRADING_RULES; owner action required (free disk)
- **GAP 21:** Filelock timeout 5s behavior
  - Resolution: timeout fires → retry once → if still locked, surface error to caller (no silent skip)
- **GAP 22-25:** FRED + AAII + CNN F&G source URLs and reconciliation
  - Resolution: §3.1 deliverable #6/#7 explicitly enumerates sources; Sprint 0 verifies allowlist
- **GAP 54 / 136 / 137 (CRITICAL):** Pre-2018 historical data — depends on DEC-478 tier
  - Resolution: DEC-478 owner decision; if Stocks Developer chosen, 10-year coverage 2016+

## §3.13 Decision history — what changed and why

**Pre-Pass-52 (legacy):**
- DEC-298 Pass ~30 — adopted `auto_adjust=False` to enable PIT-correct adjusted-on-demand
- DEC-040 Pass ~25 — established PointInTimeLoader as foundational pattern
- DEC-118 Pass ~28 — Tier 1 includes selected ETFs alongside S&P 500

**Pass 52 turn 130 (TradingAgents data audit):**
- DEC-460 — verify Polygon Stocks Starter covers PIT fundamentals (RESULT: NEGATIVE per turn 133 verification)
- DEC-461 — subscribe FMP if Polygon insufficient (RESULT: now MANDATORY)

**Pass 52 turn 133 (critical gaps resolution):**
- DEC-477 — `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` canonical; supersedes static 482-CSV
- DEC-478 — Polygon tier upgrade decision pending owner approval (recommend Stocks Developer $79/mo + FMP $14-50/mo)
- DEC-479 — DEC-441 cost correction $30 → $29

**Why these supersession patterns:**
- Original assumption (Stocks Starter sufficient) was unverified — adversarial review (Pass 52 turn 132) caught the gap; verification (turn 133) confirmed insufficiency
- Pattern: assume nothing about external data sources; verify against actual API documentation; budget for higher tiers if needed

## §3.14 File / module structure

```
backtest/
├── data/
│   ├── __init__.py
│   ├── polygon_client.py            ★ NEW Sprint 0A
│   ├── pit_loader.py                ★ NEW Sprint 0A (ABC base)
│   ├── cache_ohlcv.py               ★ NEW Sprint 0A
│   ├── cache_monitor.py             ★ NEW Sprint 0A (disk + filelock)
│   ├── corporate_actions.py         ★ NEW Sprint 0A
│   ├── fred_client.py               ★ NEW Sprint 0A
│   ├── polygon_earnings.py          ★ NEW Sprint 0A (replaces yfinance_earnings)
│   ├── polygon_reference.py         ★ NEW Sprint 0A (replaces yfinance_info)
│   └── refresh/
│       ├── refresh_aaii.py          ★ NEW Sprint 0A
│       └── refresh_cnn_fg.py        ★ NEW Sprint 0A
├── _legacy/
│   ├── yfinance_earnings.py         ⊠ deprecated Sprint 4 (DEC-444)
│   └── yfinance_info.py             ⊠ deprecated Sprint 4 (DEC-443)

data/
├── cache/
│   ├── ohlcv/
│   │   └── {ticker}.parquet         ★ Sprint 1 prefetch populates ~509 files
│   ├── corp_actions.parquet
│   ├── reference.parquet
│   ├── earnings.parquet
│   └── fred/
│       └── {series_id}.parquet      ★ 9 series
├── sentiment/
│   ├── aaii.parquet
│   └── cnn_fg.parquet
└── universe/
    └── Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv    ★ canonical (DEC-303 + DEC-477)

.github/workflows/
├── refresh_aaii.yml                 ★ NEW Sprint 0A
└── refresh_cnn_fg.yml               ★ NEW Sprint 0A

tests/
├── unit/
│   └── data/
│       ├── test_polygon_client.py
│       ├── test_pit_loader.py
│       ├── test_cache_ohlcv.py
│       └── test_corporate_actions.py
└── integration/
    ├── test_pit_freezegun.py
    ├── test_polygon_to_strategy.py
    └── test_multi_process_cache.py
```

## §3.15 Example walkthrough — concrete trace

**Scenario:** Strategy `RSI_Mean_Reversion_30_70` is running on 2022-06-15 for ticker AAPL. We trace the data flow.

**Step 1:** Strategy code calls:
```python
ohlcv = price_loader.fetch_ohlcv(
    ticker='AAPL', as_of_date='2022-06-15', lookback_days=250
)
```

**Step 2:** `PriceLoader.fetch_ohlcv` (extends `PointInTimeLoader`) computes target range:
- `to_date = '2022-06-15'`
- `from_date = '2022-06-15' - 250 trading days = '2021-06-22'` (using `pandas_market_calendars`)

**Step 3:** Acquires filelock on `data/cache/ohlcv/AAPL.parquet`:
```python
with FileLock('data/cache/ohlcv/AAPL.parquet.lock', timeout=5):
    cache_df = pd.read_parquet('data/cache/ohlcv/AAPL.parquet')
```

**Step 4:** Checks cache coverage:
- Cache contains AAPL data 2018-01-01 to 2026-04-30 (Polygon Stocks Developer 10-year cache)
- `from_date = 2021-06-22` is in cache; HIT path

**Step 5:** PIT slice:
```python
slice_df = cache_df[(cache_df['date'] >= '2021-06-22') & (cache_df['date'] <= '2022-06-15')]
```

**Step 6:** Adjusted-on-demand recomputation. Splits/dividends BEFORE 2022-06-15:
- AAPL had 4:1 split on 2020-08-31 (before as_of, included in adjustment factor)
- AAPL dividends Q3-Q4 2021 + Q1-Q2 2022 (all before as_of, included)
- AAPL split 2024-... (AFTER as_of, EXCLUDED — would have caused lookahead in naive yfinance auto_adjust=True)

```python
adjustment_factor = compute_adjustment(
    splits=corp_actions[(corp_actions['ticker']=='AAPL') &
                       (corp_actions['type']=='split') &
                       (corp_actions['ex_date'] <= '2022-06-15')],
    dividends=corp_actions[...same filter...]
)
slice_df['adj_close'] = slice_df['close'] * adjustment_factor
```

**Step 7:** Returns DataFrame with 250 rows, PIT-correct, adjusted-on-demand.

**Step 8:** Strategy `RSI_Mean_Reversion_30_70`:
- Compute 14-day RSI from `adj_close`
- RSI on 2022-06-15 = 28.4 (oversold, < 30 threshold)
- Signal: ENTRY LONG at 2022-06-15 close

**Step 9:** Trade outcome logged with cube cell coordinates:
```python
trade_log.append({
    'ticker': 'AAPL', 'entry_date': '2022-06-15', 'strategy': 'RSI_Mean_Reversion_30_70',
    'cube_cell': {
        'strategy_id': 'RSI_Mean_Reversion_30_70',
        'regime': 'volatile',  # 2022-06-15 was high VIX
        'sector': 'Technology',
        'cap_band': 'mega',
        'vol_band': 'high',
        # hold_period_band populated at exit
        'tier': 1,
        'smart_money_signal': False  # no smart money signal that day
    }
})
```

**Step 10:** During Sprint 9 cube populate, this trade contributes to cell:
`(RSI_Mean_Reversion_30_70, volatile, Technology, mega, high, [hold band], 1, no_smart_money)` along with all other AAPL+similar trades that fit those coordinates.

**This trace assumes Phase 0.A done. If Phase 0.A is not done:**
- `polygon_client.get_aggs` doesn't exist → fetch fails
- OR cache uses yfinance with `auto_adjust=True` → 2024 split contaminates 2022-06-15 prices → lookahead bias → backtest result is INVALID
- OR cache reads ignore filelock → race condition → corrupt parquet → test failure

**Phase 0.A is the foundation that makes the trace above CORRECT.**

## §3.16 Sprint 0A expanded-scope coverage (Pass 53; DEC-497)

This section captures the Pass 53 owner-directed scope expansion of Sprint 0A beyond the original Polygon-only Phase 0.A. The original §3.1-§3.15 sections cover the Phase 0.A Polygon foundation; this §3.16 adds the expanded-scope deliverables.

### §3.16.1 Universe build (IMPLEMENTED 2026-05-05)

5-tier universe per DEC-477/483/494/495/103/104 with B++ schema (`Symbol, Company, Sector, added_date, removed_date` + tier-specific extension columns):

- **T1a S&P 500 historical** — 614 rows (503 active + 111 historical removed-during-window 2020-01-01 → 2026-04-09); CDAY→DAY rename map applied; Wikipedia Table 1 used under L88 one-time exception with 4/4 high-impact spot-check verified vs S&P DJI press releases; canonical PIT file per DEC-477. File: `Backtesting universe/Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv`
- **T1c NASDAQ-100** — 161 rows (101 active matching Nasdaq IR official 101 via 3-way Slickcharts+Wiki+Nasdaq cross-check + 60 historical); multi-period rows for re-entry (CSGP/SPLK/TTWO/WDC). File: `Backtesting universe/Tier 1C Universe_NASDAQ-100 Tickers_Jan 2020 to May 2026.csv`
- **T1 ETFs** — 27 ETFs (DEC-118 selected sector + macro + volatility + broad-market); QQQ "Technology"→"Information Technology" GICS canonical normalization. File: `Backtesting universe/Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv`
- **T2 Spinoffs/IPOs** — 347 rows (full SCREENER 297 + 50 graduated-name backfill per BUG-274 Option B). Full SCREENER complete 2026-05-05 (15,401 Polygon candidates checked, 200.7 min wall time, earliest qualifying listing 2010-02-10); BUG-274 PIT correctness fix added 50 currently-T1 tickers with retroactive `added_date=list_date`, `removed_date=T1_admission_date` (e.g., SNDK 2025-02-13 → 2025-11-28; ABNB 2020-12-10 → 2023-09-18; APO 2011-03-30 → 2024-12-23; DELL 2018-12-19 → 2024-09-23). Top names by current cap: SPOT/BE/NET/BAM/NU/CRWV. File: `Backtesting universe/Tier 2 Universe_Spinoffs and Recent IPOs_Feb 2010 to May 2026.csv`. Structural fix (Option A — refactor SCREENER to compute PIT add/remove dates per candidate) deferred to Sprint 5.
- **T3 Momentum Top-100** — 1924 rows (1999 minus 75 removed via leveraged-ETF blocklist; 271 sector="Unknown" tagging; 100% sector populated post Polygon SIC + yfinance one-time fallback). File: `Backtesting universe/Tier 3 Universe_Momentum Top-100_Jun 2022 to May 2026.csv`

**Master deduplicated list:** `Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv` — 1,775 unique tickers with full dimensional metadata: Symbol, Company, Sector (18-classifier per DEC-499), Tier_membership, currently_active, T1a/T1c/T1ETF/T2/T3 status + per-tier dates + extension columns. Built Pass 53 owner directive 2026-05-05.

**18-classifier sector taxonomy (DEC-499):** GICS-11 + 7 ETF asset classes (Fixed Income, Commodities, Volatility, Broad Market, International, Emerging Markets, Small Cap). Sector source priority: T1a > T1c > T2 > T3 > T1 ETF (most-curated authoritative source).

**T3 leveraged-ETF blocklist fix (Pass 53 turn 2026-05-05):** Owner-flagged after seeing SOXL/AMDL/INTW/TSMX in currently-active T3 momentum members. 3x-leveraged ETFs distort momentum signal via daily compounding. Fixed by: (a) CS-only whitelist via Polygon `/v3/reference/tickers?type=CS active=true|false` + (b) hardcoded LEVERAGED_ETF_BLOCKLIST (~110 entries) in `scripts/build_tier3_screener.py`. Smoke-tested top-20 cleaned (CELC/RHLD/RAIL/AEYE/NKTR/PL/LBPH/RGTI/ALMS/RCMT — real momentum names).

<!-- canonical-fact-scope: F-012 prefetch endpoint inventory; cross-referenced in API_AUDIT.md §18 -->
### §3.16.2 Multi-API prefetch endpoint inventory + consumer mapping (Pass 53 current state 2026-05-06)

**Authority:** This section is the canonical prefetch endpoint inventory. [API_AUDIT.md §22](API_AUDIT.md) mirrors this structure. [CANONICAL_FACTS.md F-012](CANONICAL_FACTS.md) summarizes at the API level.

**Scope per owner directive 2026-05-06:** every endpoint currently prefetched, its cache path + verified file count, the Stage(s) and Phase(s) that consume it, the agent / signal category / strategy-set that reads it, and current prefetch state. State is split into **Prefetch state** (raw data cached?) and **Consumer state** (parser + toolkit + agent wired?) per CANONICAL_FACTS.md F-003/F-012 Option B refactor.

**Status legend:**
- ✅ DONE = prefetch complete + verified file count + consumer wired
- ✅ PREFETCH = prefetch complete + verified; consumer pending (specified Sprint)
- ⚠ PARTIAL = some files cached or some consumer paths wired, others pending
- 🔴 NOT STARTED = no prefetch yet
- ⏸ DEFERRED = subscription gate (point-of-need per DEC-506)

**Stage/Phase legend:**
- Stage 2 = Strategy Validation (current); Stage 3 = Paper Trading; Stage 4 = Email-approved live; Stage 5 = Full automation
- Phase 1A = rules-only baseline; Phase 1A-α/β = cube + production-dry-run; Phase 1B = agent overlay added; Phase 1B-α = combined cube; Phase 1C+ = strategy-categories expansion

#### §3.16.2.A — Polygon Stocks Starter (Paid; ~$30/mo per DEC-441)

| Endpoint | Cache path | Files | Stage | Phase | Consumer | Signal cat | Prefetch state | Consumer state | Sprint 0A batch |
|---|---|---|---|---|---|---|---|---|---|
| OHLCV daily (5y rolling per DEC-505) | `backtest/data/cache/ohlcv/` | 1,933 | 2-5 | 1A+ | Market Analyst (F-001); all Layer 1-4 strategies (F-002) | Cat 1 (~220 technical signals) | ✅ DONE | ✅ wired (`fetcher.fetch_ohlcv`) | Batch 2 |
| News articles (1.05M articles) | `data_prefetch/polygon/news/` | 1,926 | 2-5 | 1B+ | News Analyst (DEC-464 OurNewsToolkit); F-003 Cat 5+6 | Cat 5+6 | ✅ DONE | ✅ wired (`smart_money.get_news_sentiment` Pass 53 Batch 13.2) | Batch 3 |
| Financials (91k filings) | `data_prefetch/polygon/financials/` | 1,746 | 2-5 | 1B+ Sprint 4 | Fundamentals Analyst (DEC-463 OurFundamentalsToolkit) | Cat 6 (EPS estimates / margin / FCF / share-count delta) | ✅ DONE | 🔴 parser PENDING Sprint 4 (gates Layer 1 `buyback_announcements` per DEC-490) | Batch 4 |
| Ticker events (DEC-500) | `data_prefetch/polygon/events/` | 1,687 | 2-5 | 1B+ | All 11 active agents (F-001) — corp-action enrichment context | Cat 1+5+6 (split/dividend/ticker_change/M&A/delisting) | ✅ DONE | ⚠ wiring matrix Row 3+ pending toolkit integration | Batch 5 |
| Reference (corp actions screener) | `backtest/data/cache/polygon/reference/` | 599 | 2 | Sprint 0A | T2 universe SCREENER (DEC-103/380 spinoff/IPO graduation criteria) | (universe build, not signal) | ⚠ PARTIAL — 599 of ~2,000 reference profiles | ✅ wired into T2 SCREENER | Batch 4 |
| Splits | `backtest/data/cache/polygon/splits/` | 2 | 2-5 | 1A+ | OHLCV adjustment (split-adjusted close) | Cat 1 | ⚠ PARTIAL — 2 stub files (sample only; backfill pending) | ⚠ uses Polygon's pre-adjusted aggs | Batch 4 |
| Dividends | `backtest/data/cache/polygon/dividends/` | 2 | 2-5 | 1A+ | Total return calc + dividend yield signal | Cat 1+6 | ⚠ PARTIAL — 2 stub files | ⚠ pending | Batch 4 |
| Options chains/IV/OI | `data_prefetch/polygon/options/` (folder will be created on subscription) | 0 | 2-3 | 1B+ Batch 12-c | Risk Agent (3 debaters; F-001 nodes 8-10) — IV rank/skew/term-structure/max-pain/dealer gamma | Cat 3 (~5+ planned) | ⏸ DEFERRED — Polygon Options Starter ~$29/mo subscription per DEC-506 (point-of-need) | 🔴 NOT WIRED | Batch 12-c (post-subscription) |
| NBBO daily-close (bid/ask/spread) | `data_prefetch/polygon/nbbo/` (no folder yet) | 0 | 2-5 | 1A+ | Liquidity proxy (DEC-321/366); Risk Agent (microstructure) | Cat 1 (liquidity/spread) + Cat 4 (microstructure) | 🔴 NOT STARTED — was named in original §3.16.2 plan, never executed; supplementary depth indicator | 🔴 NOT WIRED | Sprint 0A extension OR Sprint 4 |

#### §3.16.2.B — Quiver Trader (Paid; per DEC-450 subscription)

Quiver Trader provides 16 endpoint groups currently prefetched (DEC-502 owner-approved Pass 53). Bulk endpoints serve a single global parquet aggregating all tickers; per-ticker endpoints serve one parquet per ticker.

| Endpoint | Cache path | Files | Type | Stage | Phase | Consumer | Signal cat | Prefetch state | Consumer state | Sprint 0A batch |
|---|---|---|---|---|---|---|---|---|---|---|
| live/insiders | `backtest/data/cache/quiver/insiders/` | 1 (1M rows) | bulk | 2-5 | 1A+ | smart_money composite (`insider_signal`) — F-003 Cat 2 | Cat 2 | ✅ DONE | ✅ wired (Pass 53 Batch 13.1) | Batch 9 v2 |
| live/sec13fchanges | `backtest/data/cache/quiver/sec13fchanges/` | 1 (500k rows) | bulk | 2-5 | 1A+ | smart_money composite (`institutional_signal`); 45-day reporting lag | Cat 2 | ✅ DONE | ✅ wired (Pass 53 Batch 13.1) | Batch 9 v2 |
| live/sec13f (full holdings) | `backtest/data/cache/quiver/sec13f/` | 1 (bulk) | bulk | 2-5 | 1A+ | smart_money composite (full position snapshots; complement to sec13fchanges deltas) | Cat 2 | ✅ DONE | ⚠ raw cache only; full-holdings consumer pending Sprint 4 | Batch 9 v2 |
| live/institutional (per-ticker) | `backtest/data/cache/quiver/institutional/` | 509 | per-ticker | 2-5 | 1B+ | Risk Agent (institutional concentration; complement to topshareholders) | Cat 4 | ✅ DONE | 🔴 wiring matrix Row 4 partial | Batch 10 |
| live/insider (per-ticker; distinct from bulk insiders) | `backtest/data/cache/quiver/insider/` | 509 | per-ticker | 2-5 | 1A+ | smart_money composite (per-ticker insider scoping) | Cat 2 | ✅ DONE | ⚠ optional alternative to bulk insiders feed | Batch 10 |
| live/quivernews | `backtest/data/cache/quiver/quivernews/` | 1 | bulk | 2-5 | 1B+ | News Analyst (alternative news flow vs Polygon) — DEC-464 | Cat 5 | ✅ DONE | ⚠ optional secondary source (Polygon news primary) | Batch 9 v2 |
| bulk/corporatedonors | `backtest/data/cache/quiver/corporatedonors/` | 1 | bulk | 2-5 | 1B+ | Fundamentals Analyst (corporate-donor influence proxy) | Cat 6 | ✅ DONE | 🔴 parser PENDING Sprint 4 | Batch 9 v2 |
| live/patentmomentum | `backtest/data/cache/quiver/patentmomentum/` | 1 | bulk | 3-5 | 1C+ | Fundamentals Analyst (innovation signal) | Cat 6 | ✅ DONE | 🔴 PENDING Phase 1C+ | Batch 9 v2 |
| live/offexchange (per-ticker) | `backtest/data/cache/quiver/offexchange/` | 1,851 | per-ticker | 2-5 | 1B+ | Risk Agent (dark-pool / off-lit institutional flow) | Cat 4 | ✅ DONE | 🔴 wiring matrix Row 4 partial | Batch 10 |
| live/topshareholders (per-ticker) | `backtest/data/cache/quiver/topshareholders/` | 1,937 | per-ticker | 2-5 | 1B+ | Risk Agent (concentration / forced-liquidation risk) | Cat 4 | ✅ DONE | 🔴 wiring matrix Row 4 partial | Batch 10 |
| live/etfholdings (per-ticker) | `backtest/data/cache/quiver/etfholdings/` | 1,563 | per-ticker | 2-5 | 1B+ | Risk Agent (ETF flow exposure) | Cat 4 | ✅ DONE | 🔴 wiring matrix Row 4 partial | Batch 10 |
| live/wallstreetbets (per-ticker) | `backtest/data/cache/quiver/wallstreetbets/` | 509 | per-ticker | 2-5 | 1B+ | Sentiment Agent (retail-mention signal) | Cat 5 | ✅ DONE | ⚠ supplementary to Apewisdom | Batch 10 |
| live/wikipedia (per-ticker) | `backtest/data/cache/quiver/wikipedia/` | 509 | per-ticker | 2-5 | 1B+ | Sentiment Agent (attention proxy) | Cat 5 | ✅ DONE | ⚠ supplementary to free Wikipedia pageviews | Batch 10 |
| live/lobbying (per-ticker) | `backtest/data/cache/quiver/lobbying/` | 509 | per-ticker | 2-5 | 1A+ | smart_money composite | Cat 2 | ✅ DONE | ✅ wired | Batch 10 |
| live/gov_contracts (per-ticker) | `backtest/data/cache/quiver/gov_contracts/` | 509 | per-ticker | 2-5 | 1A+ | smart_money composite (gov_contracts adjacent) | Cat 2 | ✅ DONE | ✅ wired | Batch 10 |
| live/congressional (per-ticker) | `backtest/data/cache/quiver/congressional/` | 509 | per-ticker | 2-5 | 1A+ | smart_money composite (`congressional_signal`) | Cat 2 | ✅ DONE | ✅ wired | Batch 10 |

#### §3.16.2.C — FRED + ALFRED (Free; per DEC-301)

| Endpoint | Cache path | Files | Stage | Phase | Consumer | Signal cat | Prefetch state | Consumer state | Sprint 0A batch |
|---|---|---|---|---|---|---|---|---|---|
| FRED 50 macro series | `data_prefetch/fred/observations/` | 50 | 2-5 | 1A+ | Risk Agent (3 debaters); `regime_filter.classify_regime` | Cat 4 (yield curve, VIX, DXY, HY OAS, STLFSI4, RECPROUSM156N, ICSA, WALCL + 42 more) | ✅ DONE | ✅ wired — 12 signals exposed via `macro.macro_snapshot()` Pass 53 Batch 13.3 | Batch 6 |
| ALFRED vintages (PIT corrections) | `data_prefetch/alfred/` | 50 | 2-5 | 1A+ | Risk Agent — PIT-correct macro per DEC-301 (revisions instead of first-print) | Cat 4 | ✅ DONE Pass 53 owner "execute all pending" 2026-05-06 — 50/50 series with full vintage history (~15MB; ~750k vintage observations); CPIAUCSL 3,357 vintages, GDP 3,237, PAYEMS 13,673, etc. Annual chunking for daily Treasury yields per FRED 1000-vintage-cap | 🔴 consumer still reads first-print FRED; vintage-aware reader pending Sprint 4 | Batch ALFRED |

#### §3.16.2.D — AAII + CNN F&G + CFTC (Free)

| Endpoint | Cache path | Files | Stage | Phase | Consumer | Signal cat | Prefetch state | Consumer state | Sprint 0A batch |
|---|---|---|---|---|---|---|---|---|---|
| AAII bull/bear/neutral weekly (325 readings) | `data_prefetch/aaii/` | 1 | 2-5 | 1A+ | Sentiment (`sentiment_snapshot`) | Cat 5 | ✅ DONE | ✅ wired | Batch 7 |
| CNN F&G composite (0-100) | `data_prefetch/cnn_fg/` | 2 | 2-5 | 1A+ | Sentiment | Cat 5 | ✅ DONE | ✅ wired | Batch 7 |
| CNN F&G 7 sub-components (junk-bond demand / put-call / momentum / breadth / safe-haven / vol / price-strength) | `data_prefetch/cnn_fg/components/` | 7 | 2-5 | 1A+ | Sentiment (`get_cnn_components`) | Cat 5 | ✅ DONE | ✅ wired Pass 53 Batch 13.4 | Batch 7 |
| CFTC COT E-mini S&P 500 weekly TFF (1,293 reports) | `data_prefetch/cftc/` | 1 | 2-5 | 1A+ | Sentiment (`get_cot_report` — dealer_long/short positions) | Cat 4+5 | ✅ DONE | ✅ wired Pass 53 Batch 13.5 | Batch 8 |

#### §3.16.2.E — SEC EDGAR (Free; per DEC-484; via edgartools library)

| Endpoint | Cache path | Files | Stage | Phase | Consumer | Signal cat | Prefetch state | Consumer state | Sprint 0A batch |
|---|---|---|---|---|---|---|---|---|---|
| Form 4 (insider direct transactions) | `data_prefetch/sec_edgar/4/` | 1,600 | 2-5 | 1B+ Sprint 4 | Fundamentals Analyst (insider clusters; alternative to Quiver insiders) | Cat 6 | ✅ DONE Pass 53 Batch 11 | 🔴 parser PENDING Sprint 4 | Batch 11 |
| 8-K (material events) | `data_prefetch/sec_edgar/8_K/` | 1,543 | 2-5 | 1B+ Sprint 4 | Fundamentals Analyst (material events: M&A / guidance / resignations / restatements) | Cat 6 | ✅ DONE Pass 53 Batch 11 | 🔴 parser PENDING Sprint 4 | Batch 11 |
| SC 13D (activist accumulation >5%) | `data_prefetch/sec_edgar/SC_13D/` | 1,244 | 2-5 | 1B+ Sprint 4 | Fundamentals Analyst (activist signal) | Cat 6 | ✅ DONE Pass 53 Batch 11 | 🔴 parser PENDING Sprint 4 | Batch 11 |
| SC 13G (passive accumulation >5%) | `data_prefetch/sec_edgar/SC_13G/` | 1,669 | 2-5 | 1B+ Sprint 4 | Fundamentals Analyst (institutional accumulation) | Cat 6 | ✅ DONE Pass 53 Batch 11 | 🔴 parser PENDING Sprint 4 | Batch 11 |

**SEC EDGAR aggregate:** 6,056 files cached (commit `0713f5a0`). Parsers + Fundamentals Analyst toolkit wiring + signal extraction is Sprint 4 work.

#### §3.16.2.F — Free supplementary sentiment (Pass 53 Q2 owner-approved)

| Endpoint | Cache path | Files | Stage | Phase | Consumer | Signal cat | Prefetch state | Consumer state | Sprint 0A batch |
|---|---|---|---|---|---|---|---|---|---|
| Apewisdom WSB/r/stocks daily mentions | `data_prefetch/apewisdom/` | 1 | 2-5 | 1B+ | Sentiment Agent (`get_apewisdom_mentions`); ticker-aware retail signal | Cat 5 | ✅ DONE | ✅ wired Pass 53 Batch 13.5 | Batch 12-a |
| Wikipedia pageviews (per-ticker) | `data_prefetch/wikipedia/` | 1,414 | 2-5 | 1B+ | Sentiment Agent (`get_wikipedia_pageviews`); attention proxy | Cat 5 | ✅ DONE | ✅ wired Pass 53 Batch 13.5 | Batch 12-a |
| pytrends Google Trends (per-ticker) | `data_prefetch/pytrends/` | 545 | 2-5 | 1B+ | Sentiment Agent supplementary | Cat 5 | ⚠ PARTIAL (545/1,937 = 28%; halted on consecutive errors per script's 10-error rule; resumable next session) Pass 53 owner "execute all pending" 2026-05-06 advanced from 172 → 545 | ⚠ partial | Batch 12-b resume |

#### §3.16.2.G — Subscription-deferred (DEC-506)

| Endpoint | Cache path | Files | Stage | Phase | Consumer | Signal cat | Prefetch state | Consumer state | Sprint 0A batch |
|---|---|---|---|---|---|---|---|---|---|
| Polygon Options chains/IV/OI/skew | `data_prefetch/polygon/options/` (no folder yet — will be created on subscription) | 0 | 2-3 | 1B+ | Risk Agent (3 debaters) — IV rank/skew/max-pain/dealer gamma | Cat 3 | ⏸ DEFERRED — point-of-need subscription per DEC-506; ~$29/mo separate | 🔴 NOT WIRED | Batch 12-c (post-sub) |
| Ortex short interest / days-to-cover / utilization | `data_prefetch/ortex/` (no folder yet — will be created on subscription) | 0 | 2-3 | 1B+ | Risk Agent + Fundamentals Analyst — squeeze risk / forced-cover triggers | Cat 3+6 | ⏸ DEFERRED — point-of-need subscription per DEC-506; ~$50-150/mo | 🔴 NOT WIRED | Batch 12-d (post-sub) |

#### §3.16.2.H — Aggregate counts (verified 2026-05-06)

| Metric | Count |
|---|---|
| Active prefetched APIs (Stage 2) | 8 (Polygon Stocks Starter + Quiver Trader + FRED + AAII + CNN F&G + CFTC + SEC EDGAR + supplementary sources) |
| Deferred APIs (Stage 2-3 IN-SCOPE; subscription point-of-need per DEC-506) | 2 (Polygon Options + Ortex) |
| Total endpoints prefetched | **29** (Polygon: OHLCV + News + Financials + Ticker events + Reference + Splits + Dividends = 7; Quiver: 16 — bulk insiders / sec13fchanges / sec13f / quivernews / corporatedonors / patentmomentum + per-ticker offexchange / topshareholders / etfholdings / institutional / insider / wallstreetbets / wikipedia / lobbying / gov_contracts / congressional; FRED 50-series; AAII; CNN composite + 7 components; CFTC COT; SEC EDGAR Form 4 + 8-K + SC 13D + SC 13G; Apewisdom; Wikipedia; pytrends partial = 7+16+1+1+1+1+1+1+1+1 endpoint groups consolidated to 29 distinct endpoints) |
| Total endpoints pending prefetch (free; awaiting work) | **3** (ALFRED vintages; Polygon NBBO daily-close; pytrends completion 172/1,937 → full) |
| Total endpoints pending subscription | **2** (Polygon Options; Ortex per DEC-506) |
| Total endpoints partial / stub | **3** (Polygon Reference 599/~2,000; Polygon Splits 2 stubs; Polygon Dividends 2 stubs) |
| Total files cached across all endpoints | ~22,800+ |
| Total raw data points | ~2M+ (1M Quiver insiders + 500k 13F changes + 1.05M Polygon news articles + 91k Polygon financials filings + 6,056 SEC EDGAR filings + 50 FRED series time-points + ~6,000 AAII/CNN/CFTC/AAII sentiment time-points + per-ticker per-day point-time data) |

#### §3.16.2.I — Stage/Phase consumption ladder (visual)

```
Stage 2 (Strategy Validation — current Pass 53)
├── Phase 0.A (Sprint 0A — current): all prefetch above lands here
├── Phase 1A (Sprint 6.5 — rules + smart-money baseline, NO agents)
│   Consumes: OHLCV, FRED 50-series, smart_money composite (Quiver insiders + 13F + congressional + lobbying + gov_contracts),
│             AAII, CNN F&G composite + 7 components, CFTC COT
├── Phase 1A-α / 1A-β (Sprint 6.5-7 — rules-only cube + production-scale validation)
│   Consumes: same as 1A
├── Phase 1B (Sprint 7 — agent overlay added)
│   Adds consumption: Polygon news, Polygon ticker events, Quiver quivernews/offexchange/topshareholders/etfholdings/
│                     wallstreetbets/wikipedia/corporatedonors, Apewisdom, Wikipedia pageviews, pytrends
│   Sprint 4 unblocks: Polygon financials parser, SEC EDGAR Form 4/8-K/SC 13D/SC 13G parsers
│   Sprint 4 activates: Layer 1 buyback_announcements strategy (DEC-490 unlock)
├── Phase 1B-α (Sprint 7-8 — combined cube + dashboards)
│   Consumes: same as 1B + dashboards (DEC-199/200/201 in Sprint 9)
└── Phase 1C+ (Sprint 8 — strategy-categories expansion)
    Adds consumption: Quiver patentmomentum (innovation signal); Polygon Options + Ortex (post-subscription per DEC-506)

Stage 3 (Paper Trading Proof)
└── Same prefetched data refreshed daily; Polygon Options + Ortex active if subscribed

Stage 4-5 (Email-approved live → Full automation)
└── Same prefetched data refreshed daily; live trading via IBKR
```

#### §3.16.2.J — Cross-references

- [CANONICAL_FACTS.md F-012](CANONICAL_FACTS.md) — API-level summary with prefetch/consumer split
- [CANONICAL_FACTS.md F-003](CANONICAL_FACTS.md) — signal universe per category mapping to prefetch endpoints
- [TRADINGAGENTS_DATA_AUDIT.md §1071](TRADINGAGENTS_DATA_AUDIT.md) — DEC-507 wiring matrix (Agent × Toolkit × Data path × Verified status)
- [API_AUDIT.md §18](API_AUDIT.md) — mirrored prefetch inventory + per-API capability detail
- DECs: DEC-440 (Polygon news replaces AV+Finnhub), DEC-441 (Polygon $30/mo), DEC-450 (Quiver Trader), DEC-484 (SEC EDGAR replaces FMP), DEC-490 (Phase 1A skipped strategies pending fundamentals), DEC-497 (NO-LIVE-API HARD CUT), DEC-499 (18-classifier sector taxonomy), DEC-500 (Polygon ticker events), DEC-502 (Quiver Trader endpoint expansion), DEC-505 (5-year walk-forward window), DEC-506 (Polygon Options + Ortex point-of-need subscription)

### §3.16.3 NO-LIVE-API HARD CUT refactor (DEC-497 owner directive Q8)

Stage 2 backtest must read from `data_prefetch/<api_name>/<endpoint>/...` only. NO live API calls during backtest. yfinance permitted for one-time SETUP only (e.g., universe-build Pass 53 fallback for T3 sector backfill); not in runtime hot path.

**Affected modules (must be refactored in 0A.8):**
- `backtest/data/fetcher.py` — yfinance OHLCV/info/earnings calls → read from `data_prefetch/polygon/{aggs,reference,financials,events}/`
- `backtest/data/macro.py` — FRED API calls → read from `data_prefetch/fred/observations/`; `_fred_series` already has prefetch path; finalize HARD CUT
- `backtest/data/sentiment.py` — AAII / CNN F&G CSV reads OK (already prefetch-style); CFTC COT stub → read from `data_prefetch/cftc/cot/`
- `backtest/data/smart_money.py` — Quiver calls → read from `data_prefetch/quiver/{endpoint}/`; silent-gap fix (BUG-271/272/273) integrates with NO-LIVE-API cleanup

**Folder structure:**
```
data_prefetch/
├── polygon/
│   ├── aggs/{ticker}.parquet       # OHLCV (existing)
│   ├── reference/{ticker}.parquet  # market cap, sector, IPO date
│   ├── news/{ticker}.parquet       # news articles + sentiment
│   ├── financials/{ticker}.parquet # EPS, revenue, margins
│   ├── events/{ticker}.parquet     # ticker events DEC-500
│   ├── splits/{ticker}.parquet     # corp actions
│   └── dividends/{ticker}.parquet  # dividend history
├── fred/
│   └── observations/{series_id}.parquet
├── alfred/
│   └── vintage/{series_id}_{realtime_end}.parquet
├── aaii/
│   └── weekly_sentiment.parquet
├── cnn_fg/
│   └── daily.parquet (composite)
│   └── components/{component_name}.parquet (7 sub-components)
├── cftc/
│   └── cot_emini_sp500.parquet
├── quiver/
│   ├── congresstrading/{ticker}.parquet (or bulk)
│   ├── insidertrading/global.parquet (live/insidertrading bulk)
│   ├── sec13f/global.parquet (live/sec13f bulk)
│   ├── offexchange/{ticker}.parquet
│   ├── topshareholders/{ticker}.parquet
│   ├── etfholdings/{ticker}.parquet
│   ├── execcomp/global.parquet
│   ├── corporatedonors/{ticker}.parquet
│   ├── lobbying/{ticker}.parquet
│   ├── govcontracts/{ticker}.parquet
│   ├── quivernews/global.parquet
│   ├── patents/{ticker}.parquet
│   └── housetrading_senatetrading/{ticker}.parquet
├── sec_edgar/
│   ├── form4/{ticker}.parquet
│   ├── 8k/{ticker}.parquet
│   └── 10qk/{ticker}.parquet
├── apewisdom/
│   └── ticker_mentions/{ticker}.parquet
└── pytrends/
    └── search_volume/{ticker}.parquet
```

### §3.16.4 Smoke + demo + full test protocol (CHECKLIST #68)

Per Pass 53 owner directive, every multi-call API operation in Sprint 0A.1-0A.7 follows the **smoke → demo → full** protocol:

1. **Smoke** — 1-3 API calls; verify endpoint reachable, schema matches expectation, PAT auth works, response shape sane. ≤30 seconds wall time. Owner-gate before next stage.
2. **Demo** — 5-10% sample (e.g., 100 of 1,820 tickers); verify rate-limit handling, parallelism, cache write atomicity, error recovery. Owner-gate before next stage.
3. **Full** — entire scope (e.g., all 1,820 tickers × all required dates). Background task with progress logging.

**Trigger conditions:** ANY API operation costing money, hitting rate limits, or producing >1,000 cache files. Past failures: T2 SCREENER 15,401-call full pull executed without smoke→demo gate (Pass 53 turn 2026-05-05); owner correction codified as #68. Codified in CHECKLIST #68.

### §3.16.5 Comprehensive test pyramid per push (CHECKLIST #69, DEC-503)

Per Pass 53 owner directive 2026-05-05: every code push (Sprint 0A and beyond) must execute the FULL test pyramid:
- **Unit** — individual function correctness with mocked dependencies
- **Smoke** — basic happy-path on real data (≤30s)
- **Integration** — module-to-module data flow (fetcher → cache → signals → screener)
- **System** — end-to-end (full prefetch → universe load → backtest → report)
- **Functional** — feature behavior matches spec
- **Regression** — full `backtest/tests/test_unit.py` + `test_integration.py` (all tests must pass; current count ~102 and grows over time — run `pytest -q` to verify; see [CANONICAL_FACTS.md F-007](CANONICAL_FACTS.md))
- **Data integrity** — schema validation, PIT semantics, completeness gates
- **Performance / load** — for prefetch + heavy-data code (rate limits, memory, wall-time budgets)
- **Acceptance** — owner-defined pass criteria for the change

**Past failure pattern:** Prior pushes used limited test subsets. Smart_money silent-gap (BUG-271/272/273) went undetected because tests focused on `congresstrading` (which works) and skipped `insidertrading` + `institutionalholdings` + `analystestimates` (which silently 404). Comprehensive coverage would have caught this. Codified in CHECKLIST #69.

### §3.16.6 Critical silent-gap finding from Pass 53 smoke test 2026-05-05

3 Quiver endpoints in current `backtest/data/smart_money.py` return HTTP 404 against Trader-tier subscription:

| Code call | Smoke result | Migration | Bug ID |
|---|---|---|---|
| `historical/analystestimates/{ticker}` | 404 — NOT IN TRADER TIER | REMOVE Quiver branch in `get_analyst_data`; rely on Polygon financials per DEC-497 HARD CUT | BUG-271 |
| `historical/insidertrading/{ticker}` | 404 | Replace with `live/insidertrading` (bulk feed; client-side ticker filter) | BUG-272 |
| `historical/institutionalholdings/{ticker}` | 404 | Replace with `live/sec13f` (10,000-row paginated bulk feed; or `live/sec13f/{ticker}` per-ticker variant if it exists) | BUG-273 |

**Discovery method:** Probe matrix smoke test in `temp_staging/smoke_quiver_silent_gap_endpoints.py` and `temp_staging/smoke_quiver_url_discovery.py` (Pass 53 turn 2026-05-05). 26 + 30 = 56 endpoint variants probed; 4 working endpoints + URL conventions identified.

**Working URL paths newly discovered:**
- `historical/offexchange/{ticker}` — 3,937 rows AAPL; cols: Ticker/Date/OTC_Short/OTC_Total/DPI
- `live/topshareholders/{ticker}` — dict response, schema TBD
- `historical/corporatedonors/{ticker}` — dict response (also bulk variant `bulk/corporatedonors`)
- `historical/executivecompensation` (no ticker, paginated `data` + `pagination`)
- `live/sec13f` (no ticker, 10,000 rows confirmed; cols: Date/ReportPeriod/Name/Ticker)
- `live/quivernews` (no ticker, paginated `data` array)
- `live/etfholdings?ticker={t}` (query-param form; 500 without param)
- `bulk/corporatedonors` (no ticker, dict response)

**Unresolved at Pass 53 turn 2026-05-05:** Patent endpoint paths (Historical Patents / Recent Patents / Patent Momentum); resolved during Sprint 0A.5 kickoff smoke probes.

### §3.16.7 Polygon ticker events integration (DEC-500 Pass 53 owner directive)

**Owner directive 2026-05-05:** "polygon ticker events will be highly useful for analysis and its a key trigger for price movement. Needs to be integrated."

**Endpoint:** `https://api.polygon.io/vX/reference/tickers/{ticker}/events` (Reference Data — included in Polygon Stocks Starter subscription, no upgrade needed).

**Event types captured:** ticker_change, ticker_split, name_change, listing_change, exchange_change, delisting, new_listing.

**Agent consumption (all 11 active agents per DEC-057 + project plan §2.6 — 3 analysts + Bull/Bear/RM + Trader + 3 Risk Debaters + Portfolio Manager; +1 Reflection post-decision):**
- **Risk Agent** — material-event risk gate (analogous to SEC 8-K)
- **Fundamental Agent** — M&A as fundamental thesis trigger (acquirer/target context)
- **Sentiment Agent** — event-driven flow surge detection
- **Technical Agent** — split/dividend adjustments + ticker_change continuity
- **Bull/Bear Debate** — debate quality enhanced by event context
- **Decision Agent** — final synthesis includes event timing

**Cache schema:**
```
data_prefetch/polygon/events/{ticker}.parquet
columns: ticker, event_type, event_date, details_json, fetched_at
```

**Also feeds T2 SCREENER per DEC-380** (corp actions for spinoff/IPO universe construction).

### §3.16.8 Pass 53 Sprint 0A status snapshot 2026-05-05

| Item | Status | Detail |
|---|---|---|
| Universe build | ✅ IMPLEMENTED | 614 T1a + 161 T1c + 27 T1 ETFs + 347 T2 (0 blank sectors post BUG-275 fix) + 1923 T3 (post BUG-276 NULL Symbol fix) + Master 1,937 unique tickers w/ resolved_tier per DEC-504 |
| DEC-504 T3-over-T1 precedence resolver | ✅ RESOLVED-IMPLEMENTED 2026-05-05 | universe.py: _TIER_PRECEDENCE + TIER_PARAMS + resolve_tier_precedence + get_tier_params; 10 new unit tests; full DEC-503 test pyramid (FIRST APPLICATION) — 79/79 regression PASS |
| Sector normalization 18-classifier | ✅ IMPLEMENTED | DEC-499; T1a 100% / T1c 100% / T2 100% / T3 100% (271 "Unknown") / ETFs 100% |
| T3 leveraged-ETF blocklist | ✅ FIXED | CS whitelist + 110-entry blocklist; SOXL/AMDL/INTW/TSMX excluded |
| Polygon Stocks Starter OHLCV | ✅ 1,821 cached | Pre-Pass-53 baseline |
| Polygon EXTENSION (news/financials/events/NBBO) | ⏸ PENDING | Sprint 0A.1; owner-gated per #68 |
| FRED 52-series | ⏸ PENDING | Sprint 0A.2; curating to ~15-20 |
| AAII + CNN F&G prefetch | ⏸ PENDING | Sprint 0A.3 |
| CFTC COT prefetch | ⏸ PENDING | Sprint 0A.4 |
| Quiver Trader 10 endpoint groups | ⏸ PENDING | Sprint 0A.5; silent-gap fix required first |
| SEC EDGAR structured | ⏸ PENDING | Sprint 0A.6 |
| Apewisdom + pytrends | ⏸ PENDING | Sprint 0A.7 (DEC-502 supplement, owner-approved Pass 53) |
| NO-LIVE-API refactor | ⏸ PENDING | Sprint 0A.8; HARD CUT (DEC-497) |
| Polygon ticker events | ⏸ PENDING | Sprint 0A.9; DEC-500 owner directive |
| Smoke + demo + full tests | ⏸ PENDING | Sprint 0A.10; CHECKLIST #68 + #69 |

**Critical bugs surfaced Pass 53 (queued for next-turn fix with DEC-503 test pyramid):**
- BUG-271: smart_money.py historical/analystestimates → 404 (silently broken)
- BUG-272: smart_money.py historical/insidertrading → 404 (silently broken)
- BUG-273: smart_money.py historical/institutionalholdings → 404 (silently broken)

## §3.17 Sprint 0A decisions in scope (DECs 497-503 Pass 53 additions)

| DEC | Title | Scope | Status |
|---|---|---|---|
| **497** | Sprint 0A scope expansion (multi-API prefetch + universe absorbed + NO-LIVE-API HARD CUT + 16 test files) | Sprint 0A | RESOLVED-DECIDED Pass 53 turn 2026-05-05 |
| **498** | Per-turn doc sync rule (CHECKLIST #67 + #67.b) — every turn with meaningful changes ends with doc sweep; decoupled from pending runs | Cross-cutting | RESOLVED-DECIDED Pass 53 |
| **499** | 18-classifier sector taxonomy (GICS-11 + 7 ETF asset classes) | Universe + Cube | RESOLVED-DECIDED Pass 53 |
| **500** | Polygon ticker events integration as agent context (price-move trigger) | Sprint 0A.9 | RESOLVED-DECIDED Pass 53 |
| **501** | (SUPERSEDED Pass 53) Polygon Options Stage 3/Phase 1C deferral — REVERSED by DEC-506 to Stage 2 IN-SCOPE | Sprint 0A scope-in (subscription point-of-need) | SUPERSEDED-BY-DEC-506 Pass 53 |
| **506** | Polygon Options + Ortex confirmed Stage 2 IN-SCOPE (corrects DEC-501 + DEC-468 timing); subscriptions buy-on-demand at sprint entry | Sprint 0A.5+ Batches 12-c/12-d (Options + Ortex post-subscription) | RESOLVED-DECIDED Pass 53 |
| **507** | Agent toolkit wiring matrix HARD RULE (CHECKLIST #70 + L146 codification); pre-Phase-1B explicit Agent × Data source × Code path × Verified status table | Cross-cutting / process | RESOLVED-DECIDED Pass 53 |
| **502** | Quiver Trader-tier agent-input expansion (8 endpoint groups; App Ratings + Patent Drift dropped per Q1; Apewisdom + pytrends added per Q2) | Sprint 0A.5, 0A.7 | RESOLVED-DECIDED Pass 53 |
| **503** | Comprehensive test pyramid before every code push (CHECKLIST #69; HARD RULE) | Cross-cutting | RESOLVED-DECIDED Pass 53 |

---

# PART 4 — PHASE 0.B: PORTFOLIO CLASS (Sprint 3)

## §4.1 What — concrete deliverable in plain English

Phase 0.B produces the **runtime state container** that holds every portfolio-level piece of information the backtest needs at any moment in time: cash available, open positions with their entry prices and cost bases, drawdown vs high-water-mark, sector concentration, per-ticker cooldown state (DEC-018 5-day post-stop-out blackout), per-ticker max-loss state (DEC-135 -10% rolling 30d cap), correlation between candidate tickers and existing holdings, and a complete event log of every trade ever executed.

The Portfolio class is what the engine, strategies, custom toolkits (DEC-465 Trader, DEC-466 Risk), and dashboards all query when they need to know "what does my portfolio look like right now?"

This phase resolves **BUG-095** which has been one of the longest-standing critical open bugs in the project (the engine has had no Portfolio class — positions and cash were tracked ad-hoc in the engine itself, with no PIT-correct historical replay capability).

Concrete deliverables:

1. **`Portfolio` class with full API per DEC-476 PROPOSED** — `backtest/portfolio/portfolio.py` implementing the spec drafted Pass 52 turn 133 (CRITICAL_GAPS_RESOLUTION §9). All methods named exactly per spec: `get_existing_position`, `get_cash_available`, `get_portfolio_state`, `get_correlation_to_existing_positions`, `get_drawdown_context`, `get_sector_concentration`, `get_per_ticker_cooldown_state`, `get_per_ticker_max_loss_status`, `execute_trade`, `close_position`, `update_market_values`, `snapshot_at`, `replay_to`.

2. **Sub-classes**: `Position`, `ClosedTrade`, `PortfolioStateSnapshot`, `Order` (Stage 3+), `DrawdownState`, `CooldownState`, `MaxLossState` per the spec.

3. **PIT-correct historical replay** — `Portfolio.snapshot_at(historical_date)` reconstructs portfolio state at any past date by replaying the trade log, using PIT-correct prices from Phase 0.A.

4. **Per-ticker risk state tracking** — DEC-018 5-day stop-out cooldown enforced when querying `get_per_ticker_cooldown_state(ticker, as_of)`. DEC-135 -10% rolling 30d max-loss cap enforced via `get_per_ticker_max_loss_status(ticker, as_of)`.

5. **Correlation matrix** — `get_correlation_to_existing_positions(ticker, as_of, window_days=60)` computes pairwise return correlation between candidate ticker and each existing position; returns mean. Default 0.0 if portfolio empty (Day 1 of backtest).

6. **Drawdown machinery** — high-water-mark tracking, current drawdown, max drawdown over arbitrary window, time-since-recovery. Aligned with QuantStats reference for verification.

7. **Sector concentration** — % of portfolio value per GICS sector. Computed from PIT-correct sector classification (Polygon reference data per DEC-443).

8. **Event log persistence** — Stage 2 backtest: in-memory list, persisted to Parquet at backtest end. Stage 3+: SQLite event store per DEC-267 (Postgres at Stage 4+).

9. **Multi-process safety** — Portfolio state is single-process per backtest fold (multiple processes for parallel folds; no within-fold concurrency on Portfolio mutation per Sprint 1 multi-process design).

10. **Integration with Sprint 7 toolkits** — `OurTraderToolkit` (DEC-465) and `OurRiskToolkit` (DEC-466) read-only access during agent decision; write access at engine execution.

## §4.2 Why — how this advances Stage 2 toward verdict

The Portfolio class is the **second foundational layer** after Phase 0.A. Without it:

- **Sprint 7 custom toolkits (DEC-465 Trader, DEC-466 Risk) cannot be implemented.** Both toolkits call methods on Portfolio (`get_portfolio_state`, `get_correlation_to_existing_positions`, `get_drawdown_context`, `get_sector_concentration`). Until Portfolio exists with those exact method signatures, Sprint 7 toolkit work is blocked.
- **Sprint 9 Phase 1B-α run cannot execute correctly.** The cube populate needs trade outcomes with PIT-correct portfolio context (sector concentration, drawdown state) recorded as cube cell metadata.
- **Per-ticker risk gates (DEC-018, DEC-135) can't enforce.** These require querying portfolio history at as_of date — that's the `snapshot_at` method.
- **A/B framework arms can't differ at portfolio level.** Each arm has its own Portfolio instance to track its own positions; without the class, arms can't be tracked separately.
- **Dashboards (DEC-199/200/201) have nothing to display.** Sprint 7-8 dashboards visualize portfolio drawdown, sector concentration, P&L over time — data must come from Portfolio.

This is **Stage 2 effectiveness Blocker B4** from ADVERSARIAL_AUDIT (Portfolio class spec vacuum). Resolution drafted Pass 52 turn 133 — Sprint 3 implements.

## §4.3 How — components, data flow, dependencies

**Class diagram (per DEC-476 PROPOSED):**

```python
class Portfolio:
    """PIT-correct portfolio state for backtest + live."""
    
    cash: Decimal
    positions: Dict[str, Position]
    closed_trades: List[ClosedTrade]
    open_orders: List[Order]  # Stage 3+
    high_water_mark: Decimal
    as_of_date: date
    
    # SETUP
    def __init__(self, initial_cash: Decimal, as_of_date: date, ...): ...
    
    # POSITION QUERIES
    def get_existing_position(self, ticker: str) -> Optional[Position]: ...
    def get_all_positions(self) -> Dict[str, Position]: ...
    def get_cash_available(self) -> Decimal: ...
    def get_portfolio_state(self) -> PortfolioStateSnapshot: ...
    
    # AGGREGATE QUERIES
    def get_total_value(self) -> Decimal: ...
    def get_drawdown_context(self) -> DrawdownState: ...
    def get_sector_concentration(self) -> Dict[str, Decimal]: ...
    def get_correlation_to_existing_positions(
        self, ticker: str, as_of: date, window_days: int = 60
    ) -> Decimal: ...
    
    # PER-TICKER RISK STATE
    def get_per_ticker_cooldown_state(self, ticker: str, as_of: date) -> CooldownState: ...
    def get_per_ticker_max_loss_status(self, ticker: str, as_of: date) -> MaxLossState: ...
    
    # MUTATION (PIT-aware)
    def execute_trade(self, trade: Trade, as_of: date) -> TradeResult: ...
    def close_position(self, ticker: str, exit_price: Decimal, as_of: date, exit_reason: str) -> ClosedTrade: ...
    def update_market_values(self, prices: Dict[str, Decimal], as_of: date) -> None: ...
    
    # PIT CORRECTNESS
    def snapshot_at(self, as_of: date) -> 'Portfolio': ...
    def replay_to(self, target_date: date, trade_log: List[Trade]) -> 'Portfolio': ...
```

**Data flow during a typical backtest day:**

```
Engine starts day 2022-06-15
        │
        ▼
portfolio.update_market_values(prices=daily_close[2022-06-15], as_of='2022-06-15')
        │  - Updates each position's current_price + market_value + unrealized_pnl
        │  - Recomputes total_value
        │  - Updates high_water_mark if needed
        │  - Updates drawdown
        ▼
Per ticker, per strategy, screen fires; candidate emerges
        │
        ▼
Per-ticker risk gate check:
    cooldown = portfolio.get_per_ticker_cooldown_state('AAPL', '2022-06-15')
    if cooldown.days_remaining > 0:
        REJECT (DEC-018 cooldown)
    
    max_loss = portfolio.get_per_ticker_max_loss_status('AAPL', '2022-06-15')
    if max_loss.blocked:
        REJECT (DEC-135 max-loss cap)
        │
        ▼
Agent overlay (Sprint 7) calls:
    OurTraderToolkit.get_portfolio_state(as_of='2022-06-15')
    → calls portfolio.get_portfolio_state()
    → returns PortfolioStateSnapshot
        │
        ▼
    OurRiskToolkit.get_correlation_to_existing_positions('AAPL', '2022-06-15', 60)
    → calls portfolio.get_correlation_to_existing_positions()
        │
        ▼
Decision: ENTRY at $145.50, 100 shares, MEDIUM tier (3% sizing)
        │
        ▼
portfolio.execute_trade(Trade(ticker='AAPL', shares=100, price=145.50, ...), '2022-06-15')
        │  - Checks cash sufficient
        │  - Adds Position to positions dict
        │  - Subtracts cash
        │  - Logs to event store
        ▼
End of day; portfolio state ready for next day
```

**Dependencies:**
- **Sprint 0A (Phase 0.A) must be complete** — Portfolio queries OHLCV via PriceLoader for `update_market_values`
- **Sprint 1 reference data must be complete** — sector classification for `get_sector_concentration`
- **Sprint 1 corp actions** — for split-adjusted position quantities

**No dependency on Sprint 2** (Sprint 2 fixes engine bugs that Portfolio replaces; Sprint 3 starts after Sprint 2 mid-point so engine code stabilizes first).

**Library dependencies:**
- `decimal.Decimal` for all monetary values (DEC-218 numerical tolerance)
- `pandas` for return time series in correlation
- `numpy` for correlation math
- No external API calls — Portfolio is pure Python state container

## §4.4 When — sequence, blockers, parallel-ability

**Sequence within Sprint 3 (Week 2-3):**

| Day | Task |
|---|---|
| 1 | DEC-476 PROPOSED owner approval — spec lock |
| 1 | Class skeleton: `Portfolio`, `Position`, `ClosedTrade`, `PortfolioStateSnapshot` dataclasses |
| 2 | Position queries: `get_existing_position`, `get_all_positions`, `get_cash_available` |
| 2 | `get_portfolio_state` — composition of position queries |
| 3 | `update_market_values` — daily price update + drawdown recompute |
| 3 | `get_total_value`, `get_drawdown_context` |
| 4 | `get_sector_concentration` — uses Polygon reference for PIT sector |
| 4 | `get_correlation_to_existing_positions` — return time series + pairwise correlation |
| 5 | DEC-018 cooldown state machine: `get_per_ticker_cooldown_state` |
| 5 | DEC-135 max-loss state machine: `get_per_ticker_max_loss_status` |
| 6 | `execute_trade` mutation with cash check + position update |
| 6 | `close_position` mutation + closed trade log |
| 7 | `snapshot_at` PIT replay |
| 7 | `replay_to` historical reconstruction |
| 8 | Event log persistence (in-memory + Parquet end-of-backtest) |
| 9-10 | Tests + integration with mock engine + verification against QuantStats |
| 11 | Sprint 3 PR review + merge |

**Total: ~8-11d realistic.**

**Blockers:**
1. DEC-476 PROPOSED owner approval — locks API spec; Sprint 3 cannot start without
2. Sprint 1 schema lock (Day 5) — Portfolio uses Sprint 1 PriceLoader; needs stable interface
3. Sprint 2 (engine bug fixes) at least mid-point — engine code needs to be reasonably stable so Portfolio integration is meaningful

**Parallel-ability:**
- Sprint 3 ↔ Sprint 4 (DEC-410 audit findings): **parallel** — Sprint 4 fixes are in `data/` layer; Portfolio is in `portfolio/` layer
- Sprint 3 ↔ Sprint 1 second half: **partial parallel** — once Sprint 1 schema is locked Day 5, Sprint 3 can proceed
- Sprint 3 ↔ Sprint 2: **sequential** — Sprint 2 should be at least mid-way so engine code stabilized

## §4.5 Done criteria — verifiable acceptance

Sprint 3 is RESOLVED-IMPLEMENTED when ALL of these are demonstrably true:

- [ ] All 15 methods on Portfolio class implemented per DEC-476 PROPOSED spec (exact names, exact signatures)
- [ ] All sub-classes (Position, ClosedTrade, PortfolioStateSnapshot, Order, DrawdownState, CooldownState, MaxLossState) implemented as dataclasses with field-level type hints
- [ ] PIT correctness via freezegun: `Portfolio.snapshot_at('2020-06-15')` returns SAME state regardless of system time (system at 2024 vs system at 2021 vs system at 2020-06-16)
- [ ] DEC-018 cooldown state correctly tracks 5 trading days post stop-out (verified via 3 test scenarios: stop on day N, query day N+1 = blocked, query day N+5 = unblocked, query day N+6 = clear)
- [ ] DEC-135 max-loss state correctly tracks -10% rolling 30 trading-day cap (verified via 3 test scenarios: 4 losses summing -8% in 30d = clear, 4 losses summing -11% in 30d = blocked, day-31 falls off rolling window unblocking)
- [ ] `get_drawdown_context` matches QuantStats reference within 0.1% on a 5-year sample backtest
- [ ] `get_sector_concentration` sums to 1.0 (or accounts for cash %) across all positions
- [ ] `get_correlation_to_existing_positions` returns valid pairwise mean correlation [-1, 1]; returns 0.0 if portfolio empty
- [ ] `execute_trade` rejects if cash insufficient; updates position correctly on accept
- [ ] `close_position` correctly transfers Position → ClosedTrade with realized P&L
- [ ] `replay_to(target_date, trade_log)` reproduces same end-state as original sequential `execute_trade` calls
- [ ] Unit test coverage ≥ 90% per DEC-098
- [ ] Integration test: 100-trade scenario reproduces hand-validated end-state
- [ ] Event log persists to Parquet at backtest end; readable on next run
- [ ] No external API calls — Portfolio is pure state container
- [ ] Sprint 3 PR merged; CI green; all integration tests pass

## §4.6 Risks — what could go wrong specifically

**Risk R-1: API method names diverge from Sprint 7 toolkit expectations**
- DEC-476 PROPOSED locks names (`get_portfolio_state`, `get_correlation_to_existing_positions`, etc.) but Sprint 7 toolkit (DEC-465/466) might want different names if implementation reveals friction
- Mitigation: **DEC-476 must be approved BEFORE Sprint 3 start.** Owner approves spec; spec is contract; Sprint 7 builds against contract.
- If divergence emerges Sprint 7: refactor cost is bounded (Python rename) but breaks Sprint 7 timeline

**Risk R-2: PIT-replay non-determinism**
- `snapshot_at(historical_date)` requires reconstructing state from trade log. If trade log is missing intermediate state (e.g., dividend payments accruing to cash), replay produces different state than original sequential execution
- Mitigation: trade log includes ALL state-mutating events (trades + dividends + corp actions); `replay_to` strict equivalence test in §4.5

**Risk R-3: Correlation computation slow at scale**
- 60-day return correlation × N existing positions × M candidate tickers per day → O(N×M) computations per day × 250 days × 4 OOS folds (DEC-505)
- Mitigation: cache correlation matrix per `as_of_date`; recompute incrementally only when positions change
- If still slow: parallel computation across positions using NumPy vectorization

**Risk R-4: Decimal arithmetic edge cases**
- `Decimal` for all money fields per DEC-218 0.5% tolerance — but Python `Decimal` arithmetic with floats can produce subtle errors (`Decimal('0.1') + 0.1` raises TypeError; mixing types breaks)
- Mitigation: explicit `Decimal()` conversion at every API boundary; lint rule prohibits mixing `Decimal` with `float` in same expression

**Risk R-5: Drawdown computation drift vs QuantStats**
- QuantStats has a specific drawdown algorithm; our computation must match within 0.1%
- Mitigation: §4.5 done criteria explicitly tests against QuantStats; if drift, debug to convergence before merge

**Risk R-6: Event log size at scale**
- 4 OOS folds × thousands of trades per fold = potentially 30K-330K event log entries; in-memory bounds (DEC-505)
- Mitigation: stream to Parquet incrementally if event log > 100K entries; query historical state via PyArrow filter pushdown

**Risk R-7: Sector classification PIT-correctness**
- Polygon reference data may not have historical sector reclassifications (e.g., Meta moved from Comm Services to Tech in some windows)
- Mitigation: use Polygon's effective_date if exposed; if not, accept current sector with documented limitation; add to LIMITATIONS_CAVEATS_ASSUMPTIONS.md

## §4.7 Cost — engineering days + dollars

**Engineering effort:**
- Class skeleton + dataclasses: 1d
- Position queries: 1d
- Aggregate queries (incl. correlation, drawdown, sector): 2d
- Per-ticker risk state (DEC-018 + DEC-135): 1.5d
- Mutation methods + cash checks: 1d
- PIT replay (`snapshot_at`, `replay_to`): 1.5d
- Event log persistence: 0.5d
- Tests + integration + QuantStats verification: 2d
- Bug fixes + PR review: 1d

**Total: ~11.5d realistic; ~8d minimum.**

**Dollar cost:** $0 incremental — Portfolio is pure Python; no new subscriptions.

## §4.8 Decisions in scope — list with one-line summaries

| DEC | Title | Status |
|---|---|---|
| 018 | 5-day stop-out cooldown | RESOLVED-DECIDED |
| 035 | Trader vs investor classification | DEFERRED_TO_STAGE_4 (Stage 4 CPA consultation) |
| 098 | 90% test coverage minimum | RESOLVED-DECIDED |
| 122 | Slippage estimation in Portfolio cost basis | RESOLVED-DECIDED |
| 135 | -10% rolling 30d max-loss cap | RESOLVED-DECIDED |
| 218 | 0.5% numerical tolerance | RESOLVED-DECIDED |
| 252 | IBKR commission schedule | RESOLVED-DECIDED |
| 267 | SQLite event store Stage 3; Postgres Stage 4+ | RESOLVED-DECIDED |
| 280 | Slippage time-of-day multiplier | RESOLVED-DECIDED |
| 305 | PIT guard RAISE not WARN | RESOLVED-DECIDED |
| 329 | Multi-process safe globals (Portfolio is per-fold single-process) | RESOLVED-DECIDED |
| 399 | Borrow cost single-source consolidated module | RESOLVED-DECIDED |
| 443 | Polygon reference replacing yfinance.info (sector lookup) | RESOLVED-DECIDED |
| 465 | OurTraderToolkit calls Portfolio.get_portfolio_state etc. | RESOLVED-DECIDED |
| 466 | OurRiskToolkit calls Portfolio.get_correlation_to_existing etc. | RESOLVED-DECIDED |
| 476 PROPOSED | Portfolio class API spec (this phase's primary spec) | Awaits owner approval |

## §4.9 Test approach — how the deliverable is verified

**Unit tests** (`tests/unit/portfolio/`):

- `test_portfolio_init.py` — initial state correctness
- `test_position_queries.py` — get_existing_position, get_all_positions, get_cash_available
- `test_aggregate_queries.py` — drawdown, sector concentration, correlation
- `test_per_ticker_risk.py` — DEC-018 cooldown state machine + DEC-135 max-loss state machine (parametrized scenarios)
- `test_mutations.py` — execute_trade cash check, close_position P&L, update_market_values
- `test_pit_replay.py` — snapshot_at + replay_to determinism

**Integration tests** (`tests/integration/portfolio/`):

- `test_portfolio_with_engine.py` — mock engine driving 100 trades; verify final state
- `test_portfolio_pit_freezegun.py` — system time changed; same as_of date returns same state
- `test_portfolio_quantstats_parity.py` — drawdown computed by Portfolio matches QuantStats within 0.1%
- `test_portfolio_with_toolkits.py` — OurTraderToolkit + OurRiskToolkit calls succeed (Sprint 7 forward-test)

**Property tests** (`tests/property/`):

- Sum invariant: `cash + sum(position market values) == total_value`
- Sector concentration sums to 1.0 ± cash%
- Replay determinism: any sequence of trades replayed produces identical end state

**Hand-validation acceptance:**

- Owner runs Portfolio against a known historical scenario (e.g., 2008 financial crisis 6-month period); reviews drawdown / sector concentration / final P&L; confirms intuition matches numbers

## §4.10 Data dependencies — what feeds in, where it comes from, what's downstream

**Inputs to Phase 0.B:**

| Input | Source | Required by Sprint 3 Day |
|---|---|---|
| Sprint 1 PriceLoader | Phase 0.A | Day 3 (for `update_market_values`) |
| Sprint 1 reference data (sector) | Polygon reference | Day 4 (for `get_sector_concentration`) |
| Sprint 1 corp actions | Polygon corp actions | Day 6 (for `execute_trade` adjustment) |
| DEC-018 cooldown spec | TRADING_RULES §6 | Day 5 |
| DEC-135 max-loss spec | TRADING_RULES §6 | Day 5 |
| DEC-476 API spec | CRITICAL_GAPS_RESOLUTION §9 | Day 1 (must approved) |

**Outputs (consumed downstream):**

| Output | Consumer |
|---|---|
| `Portfolio` class | Sprint 7 (toolkits), Sprint 9 (engine), Stage 3-5 (live) |
| Event log Parquet | Dashboards (DEC-199-201), reflection log (DEC-189), reconciliation (DEC-181) |
| `PortfolioStateSnapshot` | Trader agent (via OurTraderToolkit), Risk debaters (via OurRiskToolkit) |
| `DrawdownState` | Risk debaters, dashboards |
| `CooldownState`, `MaxLossState` | Engine pre-trade gates |

## §4.11 Operational checklist — week-by-week

**Week 1 (Days 1-5):**
- [ ] Day 1: DEC-476 PROPOSED approval; class skeleton
- [ ] Day 2: Position queries + portfolio state composition
- [ ] Day 3: update_market_values + total_value + drawdown_context
- [ ] Day 4: sector_concentration + correlation
- [ ] Day 5: cooldown state machine + max-loss state machine

**Week 2 (Days 6-11):**
- [ ] Day 6: execute_trade + close_position
- [ ] Day 7: snapshot_at + replay_to
- [ ] Day 8: event log persistence
- [ ] Day 9: unit + integration tests
- [ ] Day 10: QuantStats parity verification + property tests
- [ ] Day 11: PR review + merge

## §4.12 Open issues — gaps from ADVERSARIAL_AUDIT relevant to this phase

From `ADVERSARIAL_AUDIT_PASS_52_TURN_132.md`:

- **GAP 28 (CRITICAL):** Portfolio class never specified
  - Resolution: §4.1 deliverable + DEC-476 PROPOSED API spec
- **GAP 29 (CRITICAL):** OurTraderToolkit method calls — `get_portfolio_state`, `get_cash_available`, `get_existing_position` lock names
  - Resolution: DEC-476 spec uses exact names; Sprint 7 builds against contract
- **GAP 30 (CRITICAL):** OurRiskToolkit method calls — `get_correlation_to_existing_positions`, `get_sector_concentration`, `get_drawdown_context` lock names
  - Resolution: DEC-476 spec uses exact names
- **GAP 31:** PIT-correctness on Portfolio queries
  - Resolution: §4.1 deliverable #3 (`snapshot_at`) + §4.5 done criteria + freezegun tests
- **GAP 75:** OurTraderToolkit concurrency model unclear
  - Resolution: §4.1 deliverable #9 — Portfolio is single-process per fold; no within-fold concurrency on mutation; toolkits read-only during agent decision
- **GAP 76:** Correlation undefined when portfolio empty
  - Resolution: §4.5 done criteria — returns 0.0 if portfolio empty (Day 1 of backtest)

## §4.13 Decision history — what changed and why

**Pre-Pass-52:**
- BUG-095 OPEN since Pass ~25 — Portfolio class identified as critical gap; deferred multiple times
- DEC-018, DEC-135 added per-ticker risk gates but no Portfolio to host them — engine had ad-hoc tracking

**Pass 52 turn 130 (TradingAgents data audit):**
- DEC-465 OurTraderToolkit + DEC-466 OurRiskToolkit specified methods that Portfolio MUST expose — surfaced Portfolio spec gap

**Pass 52 turn 132 (adversarial audit):**
- GAP 28 + GAP 29 + GAP 30 — Stage 2 effectiveness Blocker B4 ("Portfolio class spec vacuum")

**Pass 52 turn 133 (critical gaps resolution):**
- DEC-476 PROPOSED — Portfolio class API spec drafted (becomes TRADING_RULES §24 new section)
- Owner directive 3a — TRADING_RULES new section approach approved
- Owner directive 3b — Claude drafts spec for review

**Why not done sooner:** Portfolio class is intricate — touches PIT correctness, drawdown, correlation, cooldown state machines, multi-process safety. Earlier passes deferred to "later" because pre-requisites (cache layer Phase 0.A, DEC-018/135 specs) weren't all in place. Pass 52 surfaced that "later" had become "now or never" because Sprint 7 toolkit work depends on it.

## §4.14 File / module structure

```
backtest/
├── portfolio/
│   ├── __init__.py
│   ├── portfolio.py                 ★ NEW Sprint 3 (main Portfolio class)
│   ├── position.py                  ★ NEW Sprint 3 (Position dataclass)
│   ├── closed_trade.py              ★ NEW Sprint 3 (ClosedTrade dataclass)
│   ├── snapshot.py                  ★ NEW Sprint 3 (PortfolioStateSnapshot)
│   ├── drawdown.py                  ★ NEW Sprint 3 (DrawdownState + computation)
│   ├── cooldown.py                  ★ NEW Sprint 3 (DEC-018 state machine)
│   ├── max_loss.py                  ★ NEW Sprint 3 (DEC-135 state machine)
│   ├── correlation.py               ★ NEW Sprint 3 (correlation matrix util)
│   ├── sector_concentration.py      ★ NEW Sprint 3
│   ├── event_log.py                 ★ NEW Sprint 3 (in-memory + Parquet)
│   └── replay.py                    ★ NEW Sprint 3 (snapshot_at + replay_to)

tests/
├── unit/portfolio/
│   ├── test_portfolio_init.py
│   ├── test_position_queries.py
│   ├── test_aggregate_queries.py
│   ├── test_per_ticker_risk.py
│   ├── test_mutations.py
│   └── test_pit_replay.py
├── integration/portfolio/
│   ├── test_portfolio_with_engine.py
│   ├── test_portfolio_pit_freezegun.py
│   ├── test_portfolio_quantstats_parity.py
│   └── test_portfolio_with_toolkits.py
└── property/
    └── test_portfolio_invariants.py

data/
└── event_log/
    └── {fold_id}/
        └── trades.parquet           ★ Sprint 3 produces; Sprint 9 consumes
```

## §4.15 Example walkthrough — concrete trace

**Scenario:** Backtest fold 2022. As of 2022-06-15, portfolio has 3 positions: AAPL, MSFT, NVDA. Cash $50,000. Now strategy fires for AMD entry candidate. Trace what happens.

**Step 1:** Engine queries portfolio state for risk gates:
```python
cooldown = portfolio.get_per_ticker_cooldown_state('AMD', '2022-06-15')
# Returns CooldownState(days_remaining=0, blocked=False)
# AMD has no recent stop-out

max_loss = portfolio.get_per_ticker_max_loss_status('AMD', '2022-06-15')
# Returns MaxLossState(current_pnl_30d=Decimal('0.00'), cap=Decimal('-0.10'), blocked=False)
# AMD has no rolling losses
```

Both gates clear. AMD candidate proceeds.

**Step 2:** Agent overlay (Sprint 7) calls toolkit:
```python
state = our_trader_toolkit.get_portfolio_state(as_of='2022-06-15')
# Internally calls portfolio.get_portfolio_state()
# Returns PortfolioStateSnapshot:
#   as_of='2022-06-15'
#   cash=Decimal('50000.00')
#   total_value=Decimal('150000.00')
#   positions={'AAPL': Position(...), 'MSFT': Position(...), 'NVDA': Position(...)}
#   drawdown=Decimal('-0.05')  # 5% from HWM
#   drawdown_max=Decimal('-0.08')  # max DD over period
#   sector_concentration={'Technology': Decimal('0.67'), 'Cash': Decimal('0.33')}
#   leverage=Decimal('0.67')

correlation = our_risk_toolkit.get_correlation_to_existing_positions(
    'AMD', '2022-06-15', window_days=60
)
# AMD has high correlation to NVDA (both semis) ~0.85
# AMD has moderate correlation to AAPL/MSFT ~0.45
# Mean correlation = (0.85 + 0.45 + 0.45) / 3 = ~0.58
```

**Step 3:** Risk debaters factor correlation = 0.58 into reasoning. Conservative debater concerned about tech concentration; Aggressive debater notes momentum. PM final rating: Overweight (MEDIUM tier 3% sizing).

**Step 4:** Engine computes 3% of $150,000 = $4,500 target position.
At AMD price $95.00, that's 47 shares ($4,465).

**Step 5:** Engine calls:
```python
trade = Trade(
    ticker='AMD', shares=47, price=Decimal('95.00'),
    direction='long', strategy_id='ICT_FVG_Long_Tier1'
)
result = portfolio.execute_trade(trade, as_of='2022-06-15')
# Internal:
#   - Cost basis = 47 * 95.00 + commission(DEC-252) = $4,465 + $1.00 = $4,466
#   - Cash check: $50,000 - $4,466 = $45,534 (sufficient)
#   - Adds Position('AMD', 47, 95.00, '2022-06-15', ...)
#   - Subtracts cash → $45,534
#   - Logs to event_log
# Returns TradeResult(success=True, trade_id='...')
```

**Step 6:** Position now in portfolio. Daily updates:
```python
# Day 2022-06-16, AMD closes at $97.00
portfolio.update_market_values({'AMD': Decimal('97.00'), ...}, '2022-06-16')
# AMD position: market_value = 47 * 97 = $4,559; unrealized_pnl = $93 (+2.1%)
```

**Step 7:** Day 2022-07-25, exit signal fires (e.g., TP hit at $110):
```python
closed = portfolio.close_position('AMD', exit_price=Decimal('110.00'), 
                                  as_of='2022-07-25', exit_reason='TP_HIT')
# Internal:
#   - exit_value = 47 * 110.00 - commission - slippage = $5,170 - $1 - $5 = $5,164
#   - realized_pnl = $5,164 - $4,466 = $698
#   - holding_days = 40
#   - Position removed from positions dict
#   - Cash credited $5,164 → $50,698
#   - ClosedTrade logged with all metadata + cube cell coordinates
# Returns ClosedTrade(...)
```

**Step 8:** ClosedTrade contributes to cube cell:
`(strategy='ICT_FVG_Long_Tier1', regime='volatile', sector='Technology', cap='mega', vol='high', hold_band='medium 4-10d... wait 40d so long', tier=1, smart_money=False)`

**At Sprint 9 cube populate:** This trade and all similar AMD-class trades aggregate into per-cell metrics (Sharpe, win rate, etc.).

**This trace requires Phase 0.B (Portfolio class) to work. Without it:**
- Step 1: cooldown / max-loss gates can't enforce → DEC-018/135 violated
- Step 2: agent toolkits have no Portfolio to query → Sprint 7 broken
- Step 5: trade execution lacks state container → ad-hoc tracking → reproducibility lost
- Step 8: cube cell metadata incomplete → verdict invalid

---

# PART 5 — PHASE 0.C: ENGINE BUG FIXES TIER A (Sprint 2)

## §5.1 What — concrete deliverable in plain English

Phase 0.C produces **a stable backtest engine** by fixing 16 critical engine bugs (Pass 53 R7-10 fix; was 14 — added Bug 15 Circuit Breaker Level 5 single-name DD per DEC-515 part 1; Bug 16 Circuit Breaker Level 6 portfolio DD-from-peak per DEC-515 part 2) that have accumulated through pre-Pass-52 development. These bugs cause anything from incorrect P&L on closed trades (missing exit method implementations) to silent test failures (NameError in close_trade) to circuit breakers that don't fire correctly. Without Sprint 2, the engine is unreliable; cube populated by an unreliable engine produces invalid verdict.

Concrete deliverables — the 16 critical engine bugs (per ADVERSARIAL_AUDIT GAP 26 enumeration + Pass 53 R7-10 + DEC-515 additions):

1. **`close_trade` NameError fix (DEC-293)** — close_trade function had reference to undefined variable; fixes silent test failure.

2. **Duplicate `ClosedTrade` dataclass (DEC-294)** — two dataclasses with same name in different modules; consolidate to single canonical definition (now in `backtest/portfolio/closed_trade.py` per Sprint 3).

3. **`exit_hybrid_50pct` max_days inconsistency (DEC-295)** — exit method's max_days parameter was inconsistent between definition and usage; fix to match TRADING_RULES §8 spec.

4. **Trailing stop ATR refresh missing (DEC-311)** — trailing stop's ATR-based distance was computed once at entry and never refreshed; should refresh daily per DEC-067 trailing methodology.

5. **Circuit breaker Level 3 not implemented (DEC-314 part 1)** — TRADING_RULES §9 specifies 4-level breakers (-7%/-13%/-20%/-25%); Level 3 (20% S&P drop) had no implementation.

6. **Circuit breaker Level 4 not implemented (DEC-314 part 2)** — Level 4 (25% S&P drop) had no implementation; needed for 1987-style scenarios.

7. **Circuit breaker sequential check (DEC-315)** — breakers checked in wrong order; should be Level 4 → Level 3 → Level 2 → Level 1 (most-severe first).

8. **Position sizing fractional Kelly missing (DEC-296)** — DEC-021 tier sizing was implemented but fractional Kelly variant (DEC-110 deferred-test-arm) had no code path.

9. **Slippage time-of-day multiplier missing (DEC-297)** — DEC-280 specifies slippage varies by time of day (open/close higher; midday lower); not implemented.

10. **Borrow cost double-application (DEC-306)** — short positions had borrow cost applied at both entry and daily; should only be daily accrual per DEC-399.

11. **Stop-loss intraday gap handling (DEC-312)** — backtest stop-loss assumed close-to-close; couldn't model gap-down through stop; specify worst-fill model per DEC-280.

12. **`volume_climax` exit method missing (DEC-327)** — DEC-067 lists 17 exit methods; volume_climax variant had no implementation.

13. **`fixed_3r_2r` → `fixed_target` migration (DEC-338)** — old exit name `fixed_3r_2r` deprecated; rename to `fixed_target` matching DEC-067 vocabulary.

14. **`rsi_extreme` exit method missing (DEC-340)** — DEC-067 lists 17 exit methods; rsi_extreme variant had no implementation.

15. **Circuit Breaker Level 5 single-name DD missing (DEC-515 part 1; Pass 53 R7-10 fix — was missing from prior §5.1 14-bug list)** — TRADING_RULES §9 specifies 6-level breakers post Pass 53 (was 4). Level 5 = single-name DD halt: positions with ≥X% intraday/multi-day DD trigger automatic close at next bar regardless of strategy exit logic. Implementation: `backtest/engine/circuit_breakers/level_5.py` + orchestrator priority update.

16. **Circuit Breaker Level 6 portfolio DD-from-peak missing (DEC-515 part 2; Pass 53 R7-10 fix — was missing from prior §5.1 14-bug list)** — Level 6 = portfolio-wide DD-from-peak halt: when portfolio cumulative DD ≥X% from rolling peak, halt all new entries until peak recovers Y%. Symmetric to Layer 5 entry gating + DEC-516 regime-flip exit. Implementation: `backtest/engine/circuit_breakers/level_6.py` + portfolio-state-tracker integration with Sprint 3 Portfolio class.

Plus minor adjustments and dependency cleanups bundled with these fixes per BUG_REGISTER tier-A bugs.

**Circuit breaker priority (Pass 53 DEC-586 fix):** Level 6 → Level 5 → Level 4 → Level 3 → Level 2 → Level 1 (most-severe first per DEC-315 sequencing rule, extended to 6 levels).

## §5.2 Why — how this advances Stage 2 toward verdict

The engine is the executor that turns strategy signals into trades. If the engine has bugs, the trades it produces are wrong, the cube cells are populated with wrong outcomes, and the verdict is invalid no matter how good the data foundation (Sprint 1) or Portfolio class (Sprint 3) is.

Specifically:

- **Bug 1-3 (close_trade / ClosedTrade / exit_hybrid_50pct):** Closed trade records had inconsistent fields → cube cell population wrong → metrics wrong.
- **Bug 4 (trailing stop ATR refresh):** Trailing stops too tight or too loose → exit prices systematically biased → returns biased.
- **Bug 5-7 + Bug 15-16 (circuit breakers Level 3/4/sequence + Level 5 single-name DD + Level 6 portfolio DD-from-peak per Pass 53 R7-10 + DEC-515):** During market stress periods (a meaningful fraction of OOS folds), backtest doesn't apply correct halt behavior → over-trading during 2008/2020/2022 stress → returns biased. Without Level 5, single-name catastrophic DD (e.g., -80% gap) doesn't auto-close → unbounded loss; without Level 6, portfolio compounding DD beyond owner-tolerance not halted.
- **Bug 8 (fractional Kelly):** A/B framework can't test fractional Kelly arm.
- **Bug 9 (slippage TOD):** Slippage too low or too high vs reality → returns biased.
- **Bug 10 (borrow cost double-app):** Short trades over-cost → short strategies systematically penalized.
- **Bug 11 (gap stop-loss):** Stop-loss outcomes too clean (close-to-close) → underestimates true loss in gap scenarios.
- **Bug 12-14 (missing exit methods):** Strategies that specify these exits silently fall back to default (probably max_days exit) → exit outcomes wrong.

Without Sprint 2, **every cube cell is built on a slightly-wrong foundation.** The bias is systematic, not random — and even small systematic biases in long-horizon backtest produce dramatically different verdict numbers.

## §5.3 How — components, data flow, dependencies

**Component diagram:**

```
backtest/
├── engine/
│   ├── __init__.py
│   ├── close_trade.py               ⊠ FIX (Bug 1) — DEC-293
│   ├── classes/
│   │   └── closed_trade.py          ⊠ FIX (Bug 2) — DEC-294 consolidate
│   ├── exit_methods/
│   │   ├── __init__.py
│   │   ├── exit_hybrid_50pct.py     ⊠ FIX (Bug 3) — DEC-295
│   │   ├── trailing_stop.py         ⊠ FIX (Bug 4) — DEC-311
│   │   ├── volume_climax.py         ★ NEW (Bug 12) — DEC-327
│   │   ├── fixed_target.py          ⊠ RENAME (Bug 13) — DEC-338
│   │   └── rsi_extreme.py           ★ NEW (Bug 14) — DEC-340
│   ├── circuit_breakers/
│   │   ├── __init__.py
│   │   ├── level_1.py
│   │   ├── level_2.py
│   │   ├── level_3.py               ★ NEW (Bug 5) — DEC-314
│   │   ├── level_4.py               ★ NEW (Bug 6) — DEC-314
│   │   └── orchestrator.py          ⊠ FIX (Bug 7) — DEC-315 sequence
│   ├── position_sizing/
│   │   ├── tier_sizing.py
│   │   └── fractional_kelly.py      ★ NEW (Bug 8) — DEC-296 + DEC-110
│   ├── slippage/
│   │   └── time_of_day_multiplier.py ⊠ FIX (Bug 9) — DEC-297 + DEC-280
│   ├── costs/
│   │   ├── borrow_cost.py           ⊠ FIX (Bug 10) — DEC-306 + DEC-399
│   │   └── ...
│   └── stops/
│       └── intraday_gap.py          ⊠ FIX (Bug 11) — DEC-312
```

**Data flow (illustrative — no fundamental architecture change, just fixes):**

For each bug, fix is local to the relevant module. Test for the fix verifies behavior change. Integration test for the engine end-to-end ensures fix doesn't break adjacent functionality.

**Dependencies:**
- **Sprint 1 schema lock (Day 5):** Engine fixes refer to OHLCV cache schema; if schema is unstable, fixes are wasted
- **No dependency on Sprint 3 (Portfolio class):** Sprint 2 fixes operate on existing engine code; Sprint 3 builds Portfolio class which engine eventually integrates with, but Sprint 2 fixes are self-contained
- **No external API changes:** all fixes are internal logic

**Library dependencies:** none new; fixes use existing pandas/numpy/Decimal stack.

## §5.4 When — sequence, blockers, parallel-ability

**Sequence within Sprint 2 (Week 1-2, parallel with Sprint 1 Day 6+):**

| Day | Bug to fix |
|---|---|
| 1 | Bug 1: close_trade NameError + Bug 2: duplicate ClosedTrade (consolidate) |
| 2 | Bug 3: exit_hybrid_50pct max_days |
| 3 | Bug 4: trailing stop ATR refresh |
| 4 | Bug 5: Circuit breaker Level 3 |
| 5 | Bug 6: Circuit breaker Level 4 |
| 6 | Bug 7: Circuit breaker sequential check |
| 7 | Bug 8: fractional Kelly position sizing |
| 8 | Bug 9: slippage TOD multiplier |
| 9 | Bug 10: borrow cost double-application |
| 10 | Bug 11: stop-loss intraday gap |
| 11 | Bug 12: volume_climax exit method |
| 12 | Bug 13: fixed_3r_2r → fixed_target rename |
| 13 | Bug 14: rsi_extreme exit method |
| 14 | Bug 15: Circuit Breaker Level 5 single-name DD (DEC-515 part 1; Pass 53 R7-10 add) |
| 15 | Bug 16: Circuit Breaker Level 6 portfolio DD-from-peak (DEC-515 part 2; Pass 53 R7-10 add) |
| 16-20 | Integration tests + acceptance reproduction (Pass 53 DEC-586 6-level priority test) |
| 21-22 | PR review + merge |

**Total: ~27.5-32.5d realistic (Pass 53 R7-10 fix; was 25.5-30.5d pre-Bug-15/16; +2d for Level 5/6 implementation + priority orchestrator update per DEC-586).** Circuit breakers Level 3/4/5/6 may each take 2-3d given 6-level orchestration logic.

**Parallel-ability:**
- Sprint 2 ↔ Sprint 1: **parallel** — Sprint 2 doesn't touch Sprint 1's data layer; Sprint 1 doesn't touch Sprint 2's engine code
- Sprint 2 ↔ Sprint 3: **partial parallel** — Sprint 3 starts mid-Sprint-2; engine fixes need to be reasonably stable before Portfolio class integrates
- Sprint 2 ↔ Sprint 4: **parallel** — Sprint 4 fixes data layer; orthogonal to engine fixes

**Blockers:**
1. Sprint 1 schema lock — engine queries OHLCV via PriceLoader; need stable interface
2. ENGINEERING_REGISTER Sprint 2 entry criteria met (cache infrastructure understood)

## §5.5 Done criteria — verifiable acceptance

Sprint 2 is RESOLVED-IMPLEMENTED when ALL of these are demonstrably true:

- [ ] Bug 1 (close_trade NameError): test `test_close_trade_no_nameerror.py` passes
- [ ] Bug 2 (duplicate ClosedTrade): single canonical class; all imports point to canonical location; no duplicate dataclass detected by AST scan
- [ ] Bug 3 (exit_hybrid_50pct max_days): test verifies max_days is consistent between definition and exit calculation
- [ ] Bug 4 (trailing stop ATR refresh): test verifies ATR distance updates daily over 30-day held position
- [ ] Bug 5 (Circuit breaker Level 3): test simulates 20% S&P drop; verifies Level 3 halt triggered
- [ ] Bug 6 (Circuit breaker Level 4): test simulates 25% drop; verifies Level 4 halt + suspends to next-day-open per TRADING_RULES §9
- [ ] Bug 7 (Circuit breaker sequence): test verifies Level 4 checked before Level 3 (most-severe-first)
- [ ] Bug 8 (fractional Kelly): test verifies fractional Kelly position sizing path executes
- [ ] Bug 9 (slippage TOD): test verifies slippage multiplier varies (open/close > midday)
- [ ] Bug 10 (borrow cost): test verifies short position borrow cost accrues daily, NOT at entry
- [ ] Bug 11 (gap stop-loss): test simulates gap-down through stop; verifies fill price at gap level (not stop level)
- [ ] Bug 12 (volume_climax): test verifies exit method available in ENGINE; strategies that reference it execute correctly
- [ ] Bug 13 (fixed_target rename): test verifies fixed_3r_2r removed; fixed_target accessible
- [ ] Bug 14 (rsi_extreme): test verifies exit method available; strategies execute correctly
- [ ] All 14 bug-specific tests pass
- [ ] Integration test: full backtest on AAPL 2020 fold reproduces hand-validated outcome within DEC-218 0.5% tolerance
- [ ] No regression on existing passing tests
- [ ] Sprint 2 PR merged; CI green

## §5.6 Risks — what could go wrong specifically

**Risk R-1: Engine logic changes silently shift returns**
- A bug fix changes engine behavior; backtest results before/after fix differ
- Mitigation: each bug fix has a "before/after" test that documents the change explicitly; owner reviews delta against expectation
- If unexpected delta: investigate; may indicate additional latent bug

**Risk R-2: Circuit breaker tests need historical scenarios**
- 1987 (Black Monday -22%), 2008 financial crisis, 2020 COVID — these are the natural test cases for breakers
- Mitigation: integration tests use real historical data for these scenarios; if Polygon doesn't have 1987 data (likely tier-dependent), use synthetic scenarios

**Risk R-3: Exit method additions cascade through strategies**
- Adding volume_climax / rsi_extreme as available exit methods may cause existing strategies to "find" them and switch — but strategies should reference exits by name, not by availability scan
- Mitigation: lint that strategies reference exits by explicit string; test that strategy exit selection unchanged after Bug 12/14 fixes

**Risk R-4: Borrow cost re-application produces incorrect P&L on existing tests**
- Existing test fixtures may have been computed under double-application; fixing produces different P&L
- Mitigation: regenerate fixture P&L using new (correct) formula; document fixture change in PR

**Risk R-5: Gap stop-loss change alters historical trade outcomes**
- Same as R-4 — existing tests under previous (incorrect) close-to-close model
- Mitigation: regenerate fixtures + document trade outcome differences

**Risk R-6: Slippage TOD multiplier requires intraday data**
- Polygon Stocks Starter has minute aggregates; slippage TOD logic uses time-of-day from intraday
- Mitigation: minute aggregates sufficient; verified Sprint 1 includes minute aggregates in cache scope

**Risk R-7: Circuit breaker integration with daily backtest**
- Circuit breakers are intraday phenomena (Level 1 7% triggers within 15 minutes); daily backtest can only model breakers at end-of-day grain
- Mitigation: backtest applies breakers to NEXT-DAY behavior (don't trade if breaker triggered prior day) — documented limitation
- Stage 4 live trading uses real-time breakers correctly

## §5.7 Cost — engineering days + dollars

**Engineering effort:**
- Bug 1+2 (close_trade + ClosedTrade): 1d
- Bug 3 (exit_hybrid_50pct): 0.5d
- Bug 4 (trailing stop ATR refresh): 1d
- Bugs 5+6+7 (circuit breakers Level 3/4 + sequence): 3-4d
- Bugs 15+16 (circuit breakers Level 5 single-name DD + Level 6 portfolio DD-from-peak per Pass 53 R7-10 + DEC-515): 2-3d
- Bug 8 (fractional Kelly): 1.5d
- Bug 9 (slippage TOD): 1.5d
- Bug 10 (borrow cost): 1d
- Bug 11 (gap stop-loss): 1d
- Bug 12 (volume_climax): 1d
- Bug 13 (fixed_target rename): 0.5d
- Bug 14 (rsi_extreme): 1d
- Integration tests + acceptance: 4-5d
- PR review + merge: 1d

**Total: ~25-30d realistic.**

**Dollar cost:** $0 incremental — all internal code fixes.

## §5.8 Decisions in scope — list with one-line summaries

| DEC | Title | Status |
|---|---|---|
| 067 | 17 exit methods canonical list | RESOLVED-DECIDED |
| 075 | Exit method classification (signal-based vs time-based) | RESOLVED-DECIDED |
| 110 | Fractional Kelly deferred-test-arm | RESOLVED-DECIDED (test arm) |
| 218 | 0.5% numerical tolerance | RESOLVED-DECIDED |
| 280 | Slippage time-of-day multiplier | RESOLVED-DECIDED |
| 293 | close_trade NameError fix | RESOLVED-DECIDED |
| 294 | Duplicate ClosedTrade consolidation | RESOLVED-DECIDED |
| 295 | exit_hybrid_50pct max_days fix | RESOLVED-DECIDED |
| 296 | Fractional Kelly implementation path | RESOLVED-DECIDED |
| 297 | Slippage TOD multiplier implementation | RESOLVED-DECIDED |
| 306 | Borrow cost daily accrual (not double-application) | RESOLVED-DECIDED |
| 311 | Trailing stop ATR refresh daily | RESOLVED-DECIDED |
| 312 | Stop-loss intraday gap worst-fill | RESOLVED-DECIDED |
| 314 | Circuit breaker Level 3 + Level 4 | RESOLVED-DECIDED |
| 315 | Circuit breaker sequence (severe-first) | RESOLVED-DECIDED |
| 327 | volume_climax exit method | RESOLVED-DECIDED |
| 338 | fixed_3r_2r → fixed_target rename | RESOLVED-DECIDED |
| 340 | rsi_extreme exit method | RESOLVED-DECIDED |
| 399 | Borrow cost single-source consolidated | RESOLVED-DECIDED |
| 432 | Exit method variants additive | RESOLVED-DECIDED |
| 433 | Exit method new variants (chandelier/psar/supertrend/etc.) | RESOLVED-DECIDED — Phase 0.E adds these |

## §5.9 Test approach — how the deliverable is verified

**Bug-specific unit tests** (`tests/unit/engine/`):

For each of 14 bugs, dedicated test file:
- `test_bug_{N}_{description}.py` — reproduces bug; verifies fix
- Before/after comparison documented in test docstring

**Integration tests** (`tests/integration/engine/`):

- `test_aapl_2020_acceptance.py` — full backtest reproduces hand-validated outcome
- `test_circuit_breaker_2020_covid.py` — simulates March 2020 with Polygon real data; verifies breaker behavior
- `test_short_strategy_borrow_cost.py` — short trade over 30 days; verifies daily borrow cost accrual
- `test_gap_down_stop_loss.py` — simulates gap-down past stop; verifies fill price logic

**Regression suite**:

- All existing passing tests must continue to pass after Sprint 2 merge
- Numerical tolerance per DEC-218 (0.5%) for any expected fixture changes

## §5.10 Data dependencies

**Inputs:**
- Sprint 1 OHLCV cache (PriceLoader)
- Sprint 1 corp actions table
- TRADING_RULES §8 (exit methods), §9 (circuit breakers), §11 (regime context)
- Existing engine code (pre-Sprint-2 state)

**Outputs:**
- Stable engine — Sprint 3 (Portfolio class) integrates with stable engine
- Test fixtures regenerated per Risk R-4/R-5

## §5.11 Operational checklist

**Week 1 (Days 1-7):**
- [ ] Day 1: Bug 1 + 2
- [ ] Day 2: Bug 3
- [ ] Day 3: Bug 4
- [ ] Day 4-6: Bugs 5/6/7 (circuit breakers Level 3/4/sequence)
- [ ] Day 14-15: Bugs 15/16 (circuit breakers Level 5 single-name DD + Level 6 portfolio DD-from-peak per Pass 53 R7-10 + DEC-515)
- [ ] Day 7: Bug 8

**Week 2 (Days 8-14):**
- [ ] Day 8: Bug 9
- [ ] Day 9: Bug 10
- [ ] Day 10: Bug 11
- [ ] Day 11: Bug 12
- [ ] Day 12: Bug 13
- [ ] Day 13: Bug 14
- [ ] Day 14: integration test scaffold

**Week 3 (Days 15-20):**
- [ ] Day 15-18: integration tests + acceptance reproduction
- [ ] Day 19: PR review
- [ ] Day 20: merge

## §5.12 Open issues — gaps from ADVERSARIAL_AUDIT relevant to this phase

- **GAP 26 (CRITICAL):** "14 critical engine bug fixes" only 4-5 named in TRADING_RULES
  - Resolution: §5.1 enumerates all 14 with DEC IDs; this is the canonical list
- **GAP 27:** Sprint 2 parallel with Sprint 1 — schema dependency
  - Resolution: §5.4 specifies Sprint 1 schema lock by Day 5; Sprint 2 starts Day 6+ to parallelize
- **GAP 37:** TRADING_RULES §2.5 catch-mechanism layer order
  - Resolution: deferred to Sprint 6 (Phase 0.E); Sprint 2 produces stable engine that Sprint 6 then validates
- **GAP 38:** "DEC-417 test-run audit gate" undefined
  - Resolution: deferred to Sprint 6 spec; Sprint 2 doesn't define audit gate, just provides clean engine

## §5.13 Decision history

**Pre-Pass-52:** Each of the 14 bugs was logged individually in BUG_REGISTER as it was discovered through Pass 25-50 testing. DECs 293-340 chronicle the fixes.

**Pass 52 turn 132:** ADVERSARIAL_AUDIT GAP 26 noted only 4-5 of 14 bugs were named in TRADING_RULES §2.3; rest in BUG_REGISTER but not enumerated centrally.

**Pass 52 turn 133:** §5.1 enumeration drafted as Cluster 4 recommendation per owner directive 4a.

**Pattern:** Engine bugs discovered organically during testing; fixes logged as decisions; Sprint 2 batches the 14 into one focused fix sprint.

## §5.14 File / module structure

(See §5.3 component diagram.)

Structurally, Sprint 2 doesn't add new top-level modules — it modifies/extends `backtest/engine/` modules.

## §5.15 Example walkthrough

**Scenario:** AAPL short position opened 2022-06-01 at $148, held 30 days, closed 2022-07-01 at $138 (profit $10/share). What changes after Sprint 2?

**Before Sprint 2 (with Bug 10 — borrow cost double-application):**
- Entry: 100 shares × $148 = $14,800 short proceeds; cost basis $14,800
- Borrow cost at entry: -$14,800 × 0.02 / 365 × 1 = -$0.81 (one-day rate applied at entry)
- Borrow cost daily for 30 days: -$14,800 × 0.02 / 365 × 30 = -$24.32
- Total borrow cost: -$25.13 (correct expected: -$24.32; double-applied 1-day extra)
- Exit: 100 × $138 = $13,800 buy-back
- P&L: $14,800 - $13,800 - $25.13 = $974.87
- Reported P&L: $974.87 (incorrect — should be $975.68)

**After Sprint 2 (Bug 10 fixed per DEC-306 + DEC-399):**
- Entry: $14,800 short proceeds; NO borrow cost at entry
- Borrow cost daily for 30 days: -$24.32 (correct)
- Exit: $13,800 buy-back
- P&L: $14,800 - $13,800 - $24.32 = $975.68 (correct)

**Difference: $0.81 per trade.** Compounded over thousands of short trades in the cube, materially affects short-strategy verdict.

**Similarly Bug 11 (gap stop-loss):**

**Scenario:** Long position in NVDA, stop at $400, market opens 2022-09-15 at $385 (gap down through stop).

**Before Sprint 2:** Stop-loss exit recorded at $400 (assumed close-to-close model).

**After Sprint 2 (Bug 11 fixed per DEC-312 + DEC-280):** Stop-loss exit recorded at $385 (gap-down worst fill model). P&L is $15/share more loss than before.

**Sprint 2 fixes shift backtest results in the more-realistic direction.** Owner needs to expect this delta during acceptance review.

---

# PART 6 — PHASE 0.D: ICT/SMC FORK INTEGRATION (Distributed across Sprints 1, 4, 8)

## §6.1 What — concrete deliverable in plain English

Phase 0.D integrates the **`smartmoneyconcepts` Python library (Joshua Sherrer)** as a forked dependency to provide ICT (Inner Circle Trader) and SMC (Smart Money Concepts) primitives — Fair Value Gaps (FVG), Break of Structure (BOS), Change of Character (CHoCH), and Order Blocks (OB) — as inputs to both rules-based strategies and AI agent reasoning.

Per DEC-045, this is a **fork-existing strategy** because:
- Building ICT/SMC primitives from scratch is non-trivial (multi-timeframe analysis, structure tracking, swing identification)
- The existing library is mature, tested, and Apache-2.0-licensed
- Forking allows us to add fixes / customizations without upstream coordination latency

This is **distributed across Sprints 1, 4, 8** rather than one focused sprint because:
- Sprint 1 needs the library available for `OurTechnicalToolkit` minute-aggregate strategies (although DEC-462 toolkit integration is Sprint 7)
- Sprint 4 (DEC-410 audit) includes finalizing the fork integration as DEC-410 sub-finding
- Sprint 8 (Phase 1C+ strategy categories) builds the 8 chart-pattern + ICT/SMC strategies that consume primitives

Concrete deliverables across the three sprints:

**Sprint 0A (Day 8-10):**
1. **Fork the library to `jeetmehta1991/smartmoneyconcepts`** — clone upstream + apply project patches
2. **Pin specific commit SHA in `requirements.txt`** — never live-track upstream main
3. **Smoke test integration** — call `smartmoneyconcepts.fvg(ohlcv_df)` on Polygon-fetched AAPL data; verify output schema
4. **Cache primitives at multi-timeframe level** — `cache_smc.py` stores FVG/BOS/CHoCH/OB per ticker per timeframe (1D, 1H) per as_of date

**Sprint 4 (parallel with Sprint 5-6):**
5. **Validate primitives against manual chart annotations** — owner picks 5 known examples; verify library output matches owner intuition
6. **Document any patches needed** in `docs/smartmoneyconcepts_patches.md` (e.g., known issues, edge cases handled)
7. **DEC-410 audit finding closure** — confirm fork + patches are stable

**Sprint 8 (Phase 1C+ strategy categories):**
8. **Build 8 chart-pattern strategies (DEC-355-362)** consuming SMC primitives
9. **Build BOS-direction-confirming + CHoCH-reversal + OB-zone-bounce strategies** using the library output
10. **Multi-timeframe regime confirmation (DEC-345)** — daily BOS direction + weekly trend; use primitives at both timeframes

## §6.2 Why — how this advances Stage 2 toward verdict

ICT/SMC primitives provide a **distinctive signal class** that complements traditional technical indicators. Without them:

- **Strategy roster missing 8-12 strategies** that are central to modern technical analysis discourse (FVG-fill, BOS-direction-trade, CHoCH reversal, OB-zone bounce) — strategy roster reduced from 119 to ~107
- **Multi-timeframe regime confirmation per DEC-345** can't be implemented (needs structure-based regime tracking)
- **Custom toolkit OurTechnicalToolkit `get_ict_smc_signals` method (DEC-462)** has no implementation — Sprint 7 toolkit broken
- **Agent reasoning lacks a class of signals** that SMC traders rely on; agent overlay value-add likely lower

The library is foundational infrastructure that touches multiple sprints; phase 0.D is the integration spine.

## §6.3 How — components, data flow, dependencies

**Component diagram:**

```
backtest/
├── ict_smc/
│   ├── __init__.py
│   ├── primitives.py          ★ NEW Sprint 0A (wraps smartmoneyconcepts library)
│   ├── multi_timeframe.py     ★ NEW Sprint 8 (combines 1D + 1H primitives)
│   ├── cache_smc.py           ★ NEW Sprint 0A (Parquet cache for primitives)
│   └── strategies/
│       ├── __init__.py
│       ├── fvg_fill.py        ★ NEW Sprint 8
│       ├── bos_direction.py   ★ NEW Sprint 8
│       ├── choch_reversal.py  ★ NEW Sprint 8
│       └── ob_zone_bounce.py  ★ NEW Sprint 8

vendor/
└── smartmoneyconcepts/        ★ Forked Sprint 0A (separate repo: jeetmehta1991/smartmoneyconcepts)
    └── (forked source)

requirements.txt                ⊠ UPDATED Sprint 1
    smartmoneyconcepts @ git+https://github.com/jeetmehta1991/smartmoneyconcepts@<SHA>
```

**Data flow:**

```
OHLCV cache (Sprint 1)  →  primitives.compute_fvg(df, lookback=20)
                       →  primitives.compute_bos(df)
                       →  primitives.compute_choch(df)
                       →  primitives.compute_ob(df)
                                │
                                ▼
                     cache_smc.parquet
                     (per ticker × per timeframe × per as_of)
                                │
                                ▼
              ┌─────────────────┴─────────────────┐
              ▼                                   ▼
     Strategies (Sprint 8)            OurTechnicalToolkit (Sprint 7)
     - FVG fill long                   get_ict_smc_signals(ticker, as_of)
     - BOS direction trend             returns dict of primitives
     - CHoCH reversal                  for agent consumption
     - OB zone bounce
```

**Dependencies:**
- Sprint 1 OHLCV cache (Phase 0.A) — primitives compute on OHLCV
- Sprint 1 minute aggregates (if 1H timeframe needed) — Phase 0.A includes
- Sprint 1 corp actions — primitives use adjusted-on-demand prices

**Library dependencies:**
- `smartmoneyconcepts` (forked at `jeetmehta1991/smartmoneyconcepts`)
- `pandas-ta` (transitive dependency; verify version compatibility)
- `numpy`, `pandas` (already in project)

## §6.4 When — sequence

**Sprint 0A (Days 8-10):**
- Day 8: fork repo + apply any pre-known patches; pin commit SHA
- Day 9: smoke test integration; verify output schema
- Day 10: cache_smc.py Parquet cache layer

**Sprint 4 (parallel; ~1d total):**
- 1d: validate primitives against manual annotations + document patches

**Sprint 8 (Phase 1C+ strategy categories; ~3-5d for SMC strategies subset):**
- ~3d: 4 SMC-based strategies (FVG fill / BOS direction / CHoCH reversal / OB zone bounce)
- ~2d: multi-timeframe regime confirmation per DEC-345

**Total Phase 0.D: ~5-9d distributed across Sprints 1/4/8.**

**Blockers:**
- Sprint 1 OHLCV cache available
- Library upstream stable enough to fork (verified — library is established)

**Parallel-ability:**
- Sprint 1 inclusion fits into Days 8-10 (parallel with FRED + sentiment workflows)
- Sprint 8 inclusion is part of Phase 1C+ broader strategy build

## §6.5 Done criteria

- [ ] Library forked to `jeetmehta1991/smartmoneyconcepts`
- [ ] requirements.txt pins specific commit SHA (no live-track main)
- [ ] Smoke test on AAPL 2022 produces FVG/BOS/CHoCH/OB output (no exceptions)
- [ ] cache_smc.py stores primitives in Parquet; PIT-correct cache by as_of
- [ ] 5 owner-curated examples manually annotated; library output matches within tolerance
- [ ] docs/smartmoneyconcepts_patches.md documents any patches applied
- [ ] 4 SMC strategies in Sprint 8 fire correctly on Tier 1 universe
- [ ] OurTechnicalToolkit get_ict_smc_signals (Sprint 7) consumes from cache_smc

## §6.6 Risks

**Risk R-1: Upstream library changes break our fork**
- Mitigation: pin specific SHA; review upstream changes quarterly; cherry-pick only validated changes

**Risk R-2: Library output schema differs across timeframes**
- Mitigation: explicit schema validation in primitives.py wrapper; raise clear error on schema mismatch

**Risk R-3: Owner manual validation flags discrepancies**
- Mitigation: budget Sprint 4 for patch development; document patches in `docs/`

**Risk R-4: Multi-timeframe alignment lookahead**
- Daily timeframe vs hourly — when computing daily BOS, must use only data through close of daily bar; not future hourly bars
- Mitigation: explicit timeframe alignment logic; PIT testing via freezegun

## §6.7 Cost

**Engineering effort:** ~5-9d distributed
**Subscription cost:** $0 (open source)

## §6.8 Decisions in scope

| DEC | Title | Status |
|---|---|---|
| 045 | Fork-existing strategy (smartmoneyconcepts library) | RESOLVED-DECIDED |
| 345 | Multi-timeframe regime confirmation | RESOLVED-DECIDED |
| 355-362 | 8 chart pattern strategies | RESOLVED-DECIDED |
| 462 | OurTechnicalToolkit consumes primitives | RESOLVED-DECIDED |

## §6.9 Test approach

- Unit tests on primitives wrapper (mock OHLCV input → expected primitive output)
- Cache integration test
- Owner-curated 5-example acceptance test
- PIT freezegun test for cache layer
- Multi-timeframe alignment regression test

## §6.10 Data dependencies

**Inputs:** OHLCV cache (Sprint 1)
**Outputs:** SMC primitive cache → consumed by Sprint 7 toolkit + Sprint 8 strategies

## §6.11 Operational checklist

- [ ] Sprint 1 Day 8: fork repo
- [ ] Sprint 1 Day 9: smoke test
- [ ] Sprint 1 Day 10: cache layer
- [ ] Sprint 4 (any week): manual validation
- [ ] Sprint 8: 4 SMC strategies + multi-timeframe

## §6.12 Open issues — gaps from ADVERSARIAL_AUDIT

- **GAP 41:** OurTechnicalToolkit get_intraday_ohlcv rate limits
  - Resolution: minute aggregates in Polygon Stocks Starter+; rate limits "unlimited" per pricing verification; mitigated
- **GAP 42:** ICT/SMC timeframes (1D vs 1H or both)
  - Resolution: §6.1 deliverable #4 + §6.3 — both 1D and 1H cached; multi-timeframe per DEC-345
- **GAP 66:** Phase 0.D distributed across Sprints — what gates Sprint 7?
  - Resolution: Sprint 1 deliverables (Days 8-10) gate Sprint 7 toolkit work; Sprint 4 + Sprint 8 deliverables can land later

## §6.13 Decision history

**Pass ~25:** DEC-045 fork-existing strategy chosen over from-scratch build (effort save).
**Pass 52 turn 130:** DEC-462 OurTechnicalToolkit explicitly consumes ICT/SMC primitives via state augmentation.

## §6.14 File / module structure

(See §6.3 component diagram.)

## §6.15 Example walkthrough

**Scenario:** Strategy `FVG_Fill_Long` fires on AAPL 2022-06-15. Trace data flow.

**Step 1:** Strategy queries cache_smc:
```python
primitives = smc_cache.fetch('AAPL', as_of='2022-06-15', timeframe='1D')
# Returns dict with:
#   - fvgs: [{'date': '2022-06-12', 'high': 142.0, 'low': 138.5, 'filled': False}, ...]
#   - bos: [{'date': '2022-06-10', 'direction': 'down', 'level': 145.0}]
#   - choch: []
#   - obs: [{'date': '2022-06-08', 'high': 143.0, 'low': 140.0, 'type': 'demand'}]
```

**Step 2:** Strategy logic:
```python
# Active FVG: 2022-06-12 high=142, low=138.5, unfilled
# Current price 2022-06-15 = $140 (within FVG zone)
# Recent BOS direction = 'down' (bearish bias)
# Strategy: only fill bullish FVGs in uptrend; skip
# Decision: NO ENTRY (bearish bias contradicts long FVG fill)
```

**Step 3:** Different scenario, AAPL 2022-08-10:
- Active FVG bullish, BOS direction 'up' → ENTRY LONG at $165 (FVG fill from $163-167 zone)

**Step 4:** OurTechnicalToolkit (Sprint 7) reads same cache for agent consumption:
```python
signals = our_technical_toolkit.get_ict_smc_signals('AAPL', '2022-06-15')
# Returns same primitives dict; Market Analyst incorporates into reasoning
```

**Without Phase 0.D:** Strategies and toolkit have no SMC primitives → 8-12 strategies missing from roster → cube under-populated → A/B verdict missing a signal class.

---

# PART 7 — PHASE 0.E: CATCH-MECHANISM DEFENSE + ARCHITECTURE HYGIENE (Sprint 6)

## §7.1 What — concrete deliverable in plain English

Phase 0.E builds **5 layers of defensive testing infrastructure** that catch regressions, lookahead leakage, and silent failures across the codebase. This is the longest non-Sprint-7 sprint (~62.25-76.75d) because catching everything that could go wrong in a complex backtest engine requires multiple complementary test mechanisms.

The 5 layers (per DEC-417/436/437/438/439 + TRADING_RULES §2.5):

**Layer 1 — Test-run audit gate (DEC-417)** — every backtest run produces an audit log; CI checks the audit log against expected invariants (no data after as_of date in any cached fetch; no reference to deprecated APIs; no PIT guard warnings).

**Layer 2 — Property-based tests (DEC-436)** — Hypothesis-style invariant tests that generate randomized inputs and verify properties hold. Examples: portfolio cash + position values = total value; closed_trade P&L = sum(entry to exit cashflows); replay determinism (same trade log → same end state).

**Layer 3 — Differential testing against reference (DEC-437)** — for selected strategies, run against QuantStats / vectorbt / pandas-ta reference implementations; verify our results match within DEC-218 0.5% tolerance.

**Layer 4 — Golden-master regression (DEC-438)** — frozen output snapshots from known scenarios (e.g., AAPL 2020 fold); any code change that affects these outputs requires explicit golden-master update with reviewer approval.

**Layer 5 — PIT regression suite (DEC-439)** — comprehensive freezegun-based tests that lock system time to a past date and verify backtest produces identical output as when run "naively" with current system time.

Plus **architecture hygiene** items per Phase 0.E broader scope:
- **Type hint coverage 100%** in core engine modules
- **Lint cleanup** (mypy / ruff / black across `backtest/`)
- **Docstring coverage** on all public methods
- **Dead code removal** (modules deprecated but not deleted)
- **Configuration consolidation** (multiple config files merged where redundant)
- **Logging standardization** (structured logging via `structlog`; log levels consistent)
- **Error handling audit** — no bare `except:` clauses; specific exceptions raised; PIT guard always RAISE not WARN per DEC-305

## §7.2 Why — how this advances Stage 2 toward verdict

By Sprint 6 entry, the engine has been touched by 5 sprints of changes (Sprint 0A cache, Sprint 2 bug fixes, Sprint 3 Portfolio class, Sprint 4 audit findings, Sprint 5 universe management). Without catch-mechanism layers:

- **Regressions silently slip in** — a Sprint 4 yfinance demotion change could subtly alter cached data shape; Sprint 5 universe build could introduce stale ticker references
- **Lookahead bias creeps back** — PIT correctness is invariant in Sprint 1 PIT loader, but every new query path is a new opportunity for someone to forget `as_of` parameter
- **Numerical drift accumulates** — small bugs compound across thousands of trades; without differential testing, drift goes unnoticed
- **Sprint 7 builds on unstable foundation** — agent toolkits expect engine guarantees; if engine has subtle bugs, agent decisions are made on contaminated data

Sprint 6 is the **stabilization sprint** before the largest sprint (Sprint 7 statistical methodology + custom toolkits). Quality gates here pay back across all subsequent sprints.

## §7.3 How — components, data flow, dependencies

**Layer 1 — Test-run audit gate (DEC-417):**

```
backtest/audit/
├── audit_log.py            ★ NEW — runs alongside backtest; logs every cache fetch, every PIT guard event
├── audit_invariants.py     ★ NEW — invariant checks (no future data, no deprecated API, etc.)
└── ci_audit_gate.py        ★ NEW — CI step that fails build if invariants violated

.github/workflows/
└── audit_gate.yml           ★ NEW — runs sample backtest in CI; gates merge on audit clean
```

**Layer 2 — Property tests (DEC-436):**

```
tests/property/
├── test_portfolio_invariants.py    (already started Sprint 3)
├── test_engine_invariants.py
├── test_cache_invariants.py
└── test_strategy_invariants.py

# Uses Hypothesis library: @given decorators with strategies for input generation
```

**Layer 3 — Differential testing (DEC-437):**

```
tests/differential/
├── test_quantstats_parity.py        # Drawdown / Sharpe / etc. parity
├── test_pandas_ta_parity.py          # RSI / MACD / etc. parity
└── test_vectorbt_parity.py           # Backtest engine parity
```

**Layer 4 — Golden-master regression (DEC-438):**

```
tests/golden_master/
├── fixtures/
│   ├── aapl_2020_fold.parquet         # Frozen reference output
│   ├── btc_corr_2018.parquet
│   └── ...
└── test_golden_master.py               # Compares current run to frozen fixtures
```

**Layer 5 — PIT regression (DEC-439):**

```
tests/pit_regression/
├── test_pit_aapl_2020.py              # System time set to 2020; backtest reproduces 2020-truth
├── test_pit_post_split.py              # Run pre-split + post-split with same as_of; results identical
└── test_pit_full_engine.py             # End-to-end PIT freezegun test
```

**Architecture hygiene:**

- mypy strict mode in `backtest/` (gradual rollout: critical paths first)
- ruff + black in pre-commit hook (already in place; tightening rules)
- `docstring-coverage` ≥ 80% on public methods
- `vulture` for dead code detection
- `structlog` migration from stdlib `logging`

**Dependencies:**
- All previous Sprints (1-5) substantially complete
- Test fixtures from Sprint 2 acceptance demo (e.g., AAPL 2020 hand-validated)

**Library dependencies:**
- `hypothesis` (property tests)
- `freezegun` (PIT tests; already used)
- `quantstats`, `pandas-ta`, `vectorbt` (differential testing references)
- `structlog` (logging migration)
- `vulture` (dead code)
- `mypy`, `ruff`, `black` (tooling — already in place)

## §7.4 When

**Sequence within Sprint 6 (~62-77d):**

| Week | Focus |
|---|---|
| Week 1 | Layer 1 (Audit gate) — log infrastructure + invariants |
| Week 2 | Layer 1 cont. + Layer 2 (Property tests) — Portfolio + Engine invariants |
| Week 3 | Layer 2 cont. — Cache + Strategy invariants |
| Week 4 | Layer 3 (Differential testing) — QuantStats + pandas-ta parity |
| Week 5 | Layer 3 cont. — vectorbt parity |
| Week 6-7 | Layer 4 (Golden master) — fixture generation + regression test |
| Week 8 | Layer 5 (PIT regression) — comprehensive freezegun suite |
| Week 9-10 | Architecture hygiene — type hints + docstrings + dead code |
| Week 11-12 | Logging migration to structlog |
| Week 13-15 | Configuration consolidation + error handling audit |

**Total: ~62-77d realistic. This is the long sprint.**

**Blockers:**
- Sprints 1-5 substantially complete (engine code stable enough to build catch-mechanism around)

**Parallel-ability:**
- Sprint 6 ↔ Sprint 7: **partial parallel** — Sprint 7 can start once Sprint 6 Layers 1-2 done (Weeks 1-3)
- Sprint 6 ↔ Sprint 8: **parallel** — Sprint 8 strategy categories independent of catch-mechanism (but benefits from layers as they land)

## §7.5 Done criteria

- [ ] Audit gate runs in CI on every PR; fails build on PIT/data integrity violations
- [ ] Property tests cover Portfolio + Engine + Cache + Strategy modules
- [ ] Differential parity tests pass within DEC-218 0.5% tolerance for selected strategies
- [ ] Golden-master fixtures committed; regression test fails on unintended changes
- [ ] PIT regression suite covers Sprint 1-5 deliverables; freezegun verifies determinism
- [ ] Type hint coverage ≥ 95% in core engine modules
- [ ] No bare `except:` clauses in `backtest/` (lint enforced)
- [ ] Docstring coverage ≥ 80% on public methods
- [ ] Dead code removed (vulture clean)
- [ ] Logging migrated to structlog
- [ ] Configuration files consolidated where redundant
- [ ] Sprint 6 PR merged; CI green; all 5 layers passing

## §7.6 Risks

**Risk R-1: Differential testing flakes due to numerical precision**
- QuantStats / pandas-ta have their own rounding; differences within 0.5% tolerance acceptable; below tolerance is real
- Mitigation: verify thresholds; if flaky, document expected differences

**Risk R-2: Golden master too brittle**
- Every Sprint 7+ change risks updating fixtures; if reviewer fatigue, golden master becomes stale
- Mitigation: golden master only for stable scenarios; review checklist requires explicit fixture update justification

**Risk R-3: Property tests find bugs Sprint 1-5 left**
- Hypothesis is good at finding edge cases prior tests missed
- Mitigation: budget bug-fix time within Sprint 6 if property tests find issues

**Risk R-4: Architecture hygiene scope creep**
- Type hint coverage 100% across whole codebase is enormous; scope creeps
- Mitigation: focus on `backtest/engine` and `backtest/portfolio`; legacy modules in `_legacy/` can stay loose-typed

## §7.7 Cost

**Engineering effort:** ~62-77d (the longest non-Sprint-7 sprint)
**Subscription cost:** $0

## §7.8 Decisions in scope

| DEC | Title |
|---|---|
| 098 | 90% test coverage minimum |
| 218 | 0.5% numerical tolerance |
| 241 | Smoke tests in CI |
| 305 | PIT guard RAISE not WARN |
| 417 | Test-run audit gate |
| 436 | Property-based tests |
| 437 | Differential testing |
| 438 | Golden-master regression |
| 439 | PIT regression suite |

## §7.9 Test approach

The phase IS the test approach for the rest of the project. It's catch-mechanism testing on top of unit + integration tests already in place.

## §7.10 Data dependencies

**Inputs:** Sprint 1-5 deliverables + reference libraries (QuantStats etc.)
**Outputs:** CI gates that protect Sprint 7+ work

## §7.11 Operational checklist

(See §7.4 week-by-week.)

## §7.12 Open issues — gaps from ADVERSARIAL_AUDIT

- **GAP 37:** Catch-mechanism layer order
  - Resolution: §7.4 specifies order — Layers 1→2→3→4→5 sequential because each builds on prior
- **GAP 38:** "test-run audit gate" undefined
  - Resolution: §7.3 Layer 1 specifies audit_log.py + audit_invariants.py + ci_audit_gate.py
- **GAP 145:** Stationarity test action when fires
  - Resolution: addressed in Sprint 7 statistical methodology (Part 8); Sprint 6 catches the test infrastructure but methodology is Sprint 7

## §7.13 Decision history

- DECs 417/436/437/438/439 logged Pass ~45-50 as catch-mechanism design crystallized
- Pass 52 turn 132 ADVERSARIAL_AUDIT confirmed catch-mechanism scope sufficient

## §7.14 File / module structure

(See §7.3 component diagrams across 5 layers.)

## §7.15 Example walkthrough

**Scenario:** Sprint 7 developer adds new method `OurTraderToolkit.get_recent_trader_activity` that accidentally uses `today's date` instead of `as_of` — lookahead leakage.

**Without Phase 0.E:** Sprint 7 PR merges; backtest runs produce subtly inflated returns; verdict invalid; bug discovered in Stage 3 paper trading divergence.

**With Phase 0.E:**
- **Layer 1 (Audit gate):** new method's cache fetch logs `published_date > as_of_date` — invariant violated → CI fails → PR blocked
- **Layer 5 (PIT regression):** test sets system time to 2020; tests new method; produces different result than time-set-to-2024 → fails → PR blocked

Bug caught at PR-time, not after. Sprint 7 effort preserved.

---

# PART 7.5 — PHASE 1A: RULES-BASED + SMART MONEY BASELINE (Sprint 6.5)

## §7.5.1 What — concrete deliverable in plain English

Phase 1A is the **rules-only execution layer** running the full strategy roster on the full universe with smart money signals, NO agent overlay. This produces baseline trade outcomes that feed A/B Arm A (rules-only) downstream and constitutes the **first half of the original Phase 1A v3 archive's empirical-validation-without-agents pattern** restored to current Stage 2 architecture.

**Why "restored"?** The original PROJECT_PLAN_ARCHIVE Phase 1A ran rules-only on 67 instruments × 4 years (Jan 2022 – Mar 2026), producing 6,942 trades closed and confirming `atr_trail_1x` as primary exit (20/29 strategy comparisons). When Pass 52 turn 119 absorbed Phase 1B passing criteria into DEC-422 dimensional cube + DEC-426 5-gate validity, the Phase 1A → 1B → 1C → 1D progression got compressed and **Phase 1A was inadvertently dropped from PROJECT_PLAN.md §3 sub-phases**. Pass 53 turn (this) restores Phase 1A as a distinct phase preceding Phase 1B agent overlay.

Concrete deliverables:

1. **Rules-based screener executes on full universe** — all ~199 strategies (per CANONICAL_FACTS F-002 Pass 53 + STRATEGY_ROSTER_FULL.md) fire on the universe defined by `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` (DEC-477) + Russell 1000 + NASDAQ 100 (DEC-483) + ETFs (DEC-118), totaling ~1015 tickers
2. **Smart money signals integrated** — DEC-124 cross-source confluence + DEC-332 weights + DEC-450 Quiver paid (insider/congressional/13F/analyst-changes/gov-contracts) feed into screener; smart money is a SIGNAL not an agent
3. **Liquidity floor applied** — DEC-366 ADV thresholds; tier-specific ($10M Tier 1 / $5M Tier 2 / $5M Tier 3)
4. **Per-ticker risk gates enforced** — DEC-018 5-day cooldown + DEC-135 -10% rolling 30d max-loss cap
5. **Walk-forward folds executed** — per DEC-482 (expanding window 2y+ train + 6mo OOS × 5 folds within Polygon Stocks Starter 5y window) since DEC-109 (5y/1y) doesn't fit
6. **`--no-agents` flag preserved** — explicit code path that bypasses all TradingAgents.propagate calls; rules-only screener output goes directly to trade execution
7. **Trade outcome log produced** — per DEC-189 schema with `arm=A_rules_only` tag; Parquet written for Phase 1A-α cube populator
8. **Hand-validation against Phase 1A v3 archive** — re-run a subset of Phase 1A v3 67-instrument scenario; confirm `atr_trail_1x` still wins ~20/29 strategy comparisons (regression sanity check)

## §7.5.2 Why — how this advances Stage 2 toward verdict

Phase 1A exists because **the agent overlay must be evaluated against an independently-validated rules-only baseline.** Without Phase 1A:

- A/B Arm A (rules-only) has no production-grade pre-validation — it would be created in parallel with full-with-veto Arm B inside Phase 1B, with no opportunity for owner to evaluate baseline alone before committing to agent layer
- Phase 1B-α $300 budget commits before owner knows whether rules-only baseline is viable — risks $300 spent discovering rules baseline is too weak for agent overlay to even matter
- The Phase 1A v3 archive's empirical findings (`atr_trail_1x` primacy, WEAK strategies on OOS-2024-only, pipeline correctness) cannot be re-validated on the new Sprint 1+5+4 cache scope before agent layer sits on top
- Stage 2 effectiveness Blocker B11 (newly identified): "Agent overlay evaluated against unvalidated rules-only baseline; if rules-only is broken, A/B comparison meaningless"

Phase 1A is the empirical floor that Phase 1B agent overlay must beat. If rules-only Sharpe ≥ 0.7 OOS, agent overlay has a fighting chance to add 0.2 absolute Sharpe (DEC-131 gate). If rules-only Sharpe < 0.5 OOS, agent overlay starts behind and may not justify cost.

## §7.5.3 How — components, data flow, dependencies

**Component diagram:**

```
backtest/
├── phase_1a/
│   ├── orchestrator.py              ★ NEW Sprint 6.5 (Phase 1A run driver)
│   ├── rules_screener.py            ⊠ ENHANCED (loads strategy roster; --no-agents flag)
│   ├── smart_money_integration.py   ⊠ ENHANCED (DEC-124 confluence)
│   └── trade_outcome_logger.py      ⊠ ENHANCED (arm=A_rules_only tag)
```

**Data flow:**

```
Phase 1A orchestrator starts
        │
        ▼
For each walk-forward fold (per DEC-482):
    For each trading day in OOS period:
        Load OHLCV + signal universe (Sprint 0A cache)
        Build daily universe (Sprint 5 tier definitions)
        Run rules-based screen (full strategy roster)
        Apply liquidity + event suppression + per-ticker risk gates
        Compute smart money signals (DEC-124 confluence)
        Apply preliminary tier from rules + smart money confluence
        Engine executes (single Portfolio instance — Arm A only)
        Log trade outcome with arm=A_rules_only tag
        │
        ▼
End of fold: close remaining positions; persist trade log
        │
        ▼
End of all folds: Phase 1A trade_log.parquet ready for Phase 1A-α cube populator
```

**Dependencies:**
- Sprint 0A (Phase 0.A) cache complete
- Sprint 2 (Phase 0.C) engine bug fixes complete
- Sprint 3 (Phase 0.B) Portfolio class operational
- Sprint 4 (DEC-410) data layer cleanup; smart money endpoints (Quiver paid)
- Sprint 5 (universe management) Tier 1/2/3 build functions ready
- Sprint 6 (Phase 0.E) catch-mechanism layers operational (CI gates protect Phase 1A run integrity)

## §7.5.4 When — sequence

**Sequence within Sprint 6.5 (~6-8d):**

| Day | Task |
|---|---|
| 1 | Phase 1A orchestrator skeleton; --no-agents flag wiring through engine |
| 2 | Rules-based screener integration with full strategy roster; smart money confluence |
| 3 | Walk-forward fold integration (DEC-482 expanding window 2y+/6mo × 5 folds) |
| 4 | Trade outcome logger with arm=A_rules_only tag |
| 5 | Smoke test 1 fold × 50 candidates; verify pipeline end-to-end |
| 6 | Hand-validation regression: re-run Phase 1A v3 67-instrument subset; verify atr_trail_1x still wins |
| 7 | Full Phase 1A run (all 4 folds × full universe ~1015 tickers) — wall time ~20-25h |
| 8 | Trade log validation; Phase 1A-α handoff |

**Total: ~6-8 engineering days + ~20-25h compute wall time.**

**Blockers:**
- Sprints 1-6 must be RESOLVED-IMPLEMENTED
- DEC-482 walk-forward configuration approved
- DEC-483 universe expansion approved

## §7.5.5 Done criteria

- [ ] All ~199 strategies (per CANONICAL_FACTS F-002 Pass 53 + STRATEGY_ROSTER_FULL.md) fire correctly across walk-forward folds with --no-agents flag
- [ ] Smart money confluence operational (DEC-124 + DEC-332 + DEC-450)
- [ ] Liquidity floor + event suppression + per-ticker risk gates enforced
- [ ] Trade outcome log produced with `arm=A_rules_only` tag; Parquet ready for Phase 1A-α
- [ ] Hand-validation regression: Phase 1A v3 67-instrument re-run confirms atr_trail_1x primacy
- [ ] No agent API spend during Phase 1A run (verified via budget tracker $0)
- [ ] Phase 1A PR merged; CI green

## §7.5.6 Risks

**Risk R-1: Phase 1A v3 regression fails**
- atr_trail_1x may not win on new universe scope (R1000 + NDX add midcaps with different volatility profiles)
- Mitigation: regression run on EXACT v3 67-instrument scope first; if reproduces, proceed; if not, debug before full run

**Risk R-2: Rules-only Sharpe too low to justify Phase 1B**
- If Phase 1A produces Sharpe < 0.5 OOS, agent overlay can't realistically add 0.2 to clear DEC-131 gate
- Mitigation: this is a legitimate empirical outcome — owner may decide to revisit strategy roster before committing $300 to agent layer
- Not a bug — Phase 1A's PURPOSE is to produce this signal early

**Risk R-3: Walk-forward fold contamination on compressed window**
- DEC-482 2y/6mo windows are tighter than original DEC-109 5y/1y; fold boundaries closer
- Mitigation: explicit fold boundary tests in Phase 0.E catch-mechanism (Sprint 6); PIT regression suite

**Risk R-4: Phase 1A run wall time exceeds estimate**
- 4 folds × 1015 tickers × 199 strategies = 24-32h wall time per DEC-505 4-fold (Pass 53 R7-02 + R7-06 fix; was 30-40h pre-DEC-505 6-fold × 119 strategies)
- Mitigation: parallel folds (local VS Code 8+ core laptop per Pass 53 R7-03 fix; was Codespace 8-core); progress monitor with ETA

## §7.5.7 Cost

**Engineering effort:** ~6-8d
**Compute wall time:** ~20-25h
**Dollar cost:** $0 — no agent API spend; rules + smart money already cached from Sprint 1+4

## §7.5.8 Decisions in scope

| DEC | Title | Status |
|---|---|---|
| 018 | 5-day stop-out cooldown | RESOLVED-DECIDED |
| 124 | Smart money cross-source confluence | RESOLVED-DECIDED |
| 135 | -10% rolling 30d max-loss cap | RESOLVED-DECIDED |
| 332 | Smart money composite weights | RESOLVED-DECIDED |
| 348 | Event suppression asymmetric | RESOLVED-DECIDED |
| 366 | Liquidity floor ADV-based | RESOLVED-DECIDED |
| 450 | Quiver paid endpoints scope | RESOLVED-DECIDED |
| 477 | Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv canonical | RESOLVED-DECIDED |
| 482 PROPOSED | Walk-forward expanding window 2y+/6mo × 5 folds | Awaits owner approval |
| 483 PROPOSED | Universe expansion R1000 + NDX added to Sprint 1 | Awaits owner approval |
| 486 PROPOSED | Phase 1A restored as distinct sub-phase | Awaits owner approval |

## §7.5.9 Test approach

- Pre-run smoke test on 1 fold × 50 candidates
- Phase 1A v3 67-instrument regression (atr_trail_1x primacy reproduces)
- PIT regression via freezegun (system time variation produces same trade log)
- Trade log schema validation against DEC-189
- Walk-forward fold boundary verification (no train→OOS leakage)

## §7.5.10 Data dependencies

**Inputs:**
- Sprint 1 OHLCV + reference + corp actions cache
- Sprint 4 Quiver paid (insider/congressional/13F/analyst/gov-contracts)
- Sprint 4 FRED + AAII + CNN F&G sentiment
- Sprint 5 universe build (Tier 1/2/3 with PIT correctness)

**Outputs:**
- `data/phase_1a/trade_log/fold_{N}/trades.parquet` — consumed by Phase 1A-α
- Trade log includes all 8 cube cell coordinate fields (DEC-471 PROPOSED) + `arm=A_rules_only`

## §7.5.11 Operational checklist

(See §7.5.4 day-by-day.)

## §7.5.12 Open issues — gaps from ADVERSARIAL_AUDIT relevant to this phase

Phase 1A omission was the **meta-failure of ADVERSARIAL_AUDIT itself** — the audit reviewed PROJECT_PLAN.md §3 sub-phases (which had Phase 0.A → 0.B → 0.C → 0.D → 0.E → 1B → 1B-α → 1C+) and didn't flag the missing Phase 1A. New blocker logged:

- **GAP B11 (NEW CRITICAL):** Phase 1A absent from PROJECT_PLAN §3 / TRADING_RULES §2; A/B Arm A rules-only baseline had no independent validation before agent overlay added in Phase 1B
  - Resolution: this Part 7.5 + Part 7.6 (1A-α) + Part 7.7 (1A-β) restore the phase; CHECKLIST item TBD added: "Phase coverage check — verify all phases enumerated in PROJECT_PLAN match TRADING_RULES match DETAILED_PROJECT_PLAN"

## §7.5.13 Decision history

- **PROJECT_PLAN_ARCHIVE Phase 1A v3 (Final):** Complete; 67 instruments × 4 years; 6,942 trades; atr_trail_1x confirmed primary exit
- **Pass 52 turn 119:** DEC-014 Phase 1B passing criteria SUPERSEDED by DEC-422+DEC-426; in absorption, Phase 1A reference dropped from §3 sub-phases (inadvertent)
- **Pass 52 turn 132:** ADVERSARIAL_AUDIT didn't flag Phase 1A omission (meta-failure)
- **Pass 53 turn (this):** Phase 1A restored per owner directive ("Forget stages 3-5 for now. Why was phase 1A dropped. Even phase 1A had alpha and beta. same as phase 1B")

## §7.5.14 File / module structure

(See §7.5.3 component diagram.)

## §7.5.15 Example walkthrough

**Scenario:** Phase 1A executes 2024 OOS fold (DEC-482 config). AAPL candidate fires 2024-06-15 from `RSI_Mean_Reversion_30_70` strategy.

**Step 1:** Rules screener compute_signal returns ENTRY LONG @ 2024-06-15 close.

**Step 2:** Smart money confluence check (DEC-124):
```python
sm = compute_smart_money_composite('AAPL', '2024-06-15')
# Insider net buying 30d: True (Form 4 actuals only — no Form 144 forward-looking)
# Congressional disclosures last 30d: 0 (no disclosure)
# 13F institutional Q-over-Q delta: +0.3% (mild buying)
# Composite weighted score (DEC-332): 0.55 (moderate confluence)
```

**Step 3:** Per-ticker risk gates (Portfolio class):
```python
cooldown = portfolio.get_per_ticker_cooldown_state('AAPL', '2024-06-15')
# CooldownState(blocked=False)
max_loss = portfolio.get_per_ticker_max_loss_status('AAPL', '2024-06-15')
# MaxLossState(blocked=False)
```

**Step 4:** Liquidity + event suppression:
- AAPL ADV $1.2B >> $10M Tier 1 floor → pass
- Days to next earnings: 14 → outside DEC-348 suppression window → pass

**Step 5:** Engine executes Arm A (rules-only) trade:
```python
trade = Trade(ticker='AAPL', strategy_id='RSI_MR_30_70',
              entry_date='2024-06-15', shares=100, price=189.50,
              tier='MEDIUM',  # rules+smart money preliminary tier
              arm='A_rules_only')
portfolio.execute_trade(trade, '2024-06-15')
```

**Step 6:** Trade closes 2024-07-22 at $205.40 (TP_HIT exit method per `atr_trail_1x`).

**Step 7:** Trade outcome logged with cube cell coordinates:
```python
ClosedTrade(
    arm='A_rules_only',
    cube_cell={
        'strategy_id': 'RSI_MR_30_70',
        'regime': 'neutral',  # 2024-06-15 VIX moderate
        'sector': 'Technology',
        'cap_band': 'mega',
        'vol_band': 'medium',
        'hold_band': 'medium 4-10d... actually 26d so long',
        'tier': 1,
        'smart_money_signal': True  # composite > 0.5
    },
    realized_pnl=1590.00,
    exit_reason='TP_HIT',
    holding_days=26
)
```

**Step 8:** This trade contributes to Phase 1A-α cube cell coordinates above (rules-only arm only). Compared in Phase 1B-α against agent-overlay arms for same/similar candidates.

**Without Phase 1A:** This trade would be created inside Phase 1B with agent overlay; rules-only baseline would be a parallel branch within Phase 1B, never independently validated. Owner couldn't evaluate rules-only Sharpe before committing $300 to agent overlay.

---

# PART 7.6 — PHASE 1A-α: RULES-ONLY DIMENSIONAL CUBE + DASHBOARDS (Sprint 6.5-7)

## §7.6.1 What — concrete deliverable in plain English

Phase 1A-α produces the **first cube + dashboard pass** using ONLY Phase 1A trade outcomes (rules-only, no agents). It builds the dimensional cube infrastructure (populator + 5-Gate verdict per DEC-426 + dashboards) that Phase 1B-α will later reuse and extend with agent arms.

This phase's purpose is twofold:
1. **Build cube methodology** — populator, verdict logic, dashboards — once; Phase 1B-α reuses, doesn't rebuild
2. **Produce rules-only verdict** — rules-only Sharpe / DD / win rate / PASS cell count — owner reviews BEFORE committing $300 to Phase 1B-α agent overlay

Concrete deliverables:

1. **Cube populator** — `backtest/cube/populator.py` groups Phase 1A trades by 8-dim cell coordinates per DEC-471 PROPOSED; computes per-cell metric suite per DEC-422
2. **5-Gate verdict** — `backtest/cube/verdict.py` applies Gate 1 (n≥30) + Gate 2 (FDR q<0.10 hierarchical per DEC-470 PROPOSED) + Gate 3 (PSR≥0.95) + Gate 4 (t-stat≥3.4) + Gate 5 (R:R≥2.0) per DEC-426
3. **Cube Explorer dashboard — rules-only filter (DEC-199)** — interactive dashboard letting owner slice cube; "Phase 1A-α view" filter restricts to `arm=A_rules_only`
4. **ICT/SMC Audit dashboard (DEC-200)** — focused view on Phase 0.D primitives; verifies SMC strategies firing correctly in rules-only context
5. **Live decision lookup table v1** — populated from Phase 1A-α PASS cells; this is the pre-agent baseline lookup that Phase 1B-α extends or replaces
6. **Verdict report `phase_1a_alpha_summary.md`** — rules-only Sharpe, DD, win rate, PASS cell count, FAIL_RR/INSUFFICIENT_SAMPLE/FAIL_STAT breakdown
7. **Owner gate review** — owner inspects dashboards + summary; decides whether rules-only Sharpe ≥ 0.7 OOS justifies committing $300 to Phase 1B-α agent overlay; if rules-only is too weak, may revisit strategy roster before agent layer
8. **Cube infrastructure handoff to Phase 1B-α** — populator + verdict + dashboards reused; Phase 1B-α extends with multi-arm comparison + DEC-201 Agent Overlay Analysis dashboard

## §7.6.2 Why — how this advances Stage 2 toward verdict

Phase 1A-α serves three roles:

1. **Methodology validation** — cube populator + 5-Gate verdict + dashboards must work correctly on single-arm data BEFORE handling 3-arm data. Catches methodology bugs early when they're cheap to fix.
2. **Pre-agent verdict gate** — rules-only Sharpe ≥ 0.7 OOS is the "go ahead and try agent overlay" gate. If rules-only Sharpe < 0.5, agent overlay justification drops sharply and owner may revisit roster.
3. **Live decision lookup v1** — even if Phase 1B-α agent overlay fails verdict, a rules-only lookup table from 1A-α PASS cells exists for Stage 3 paper trading. Stage 2 isn't a total loss if agent overlay fails.

Without 1A-α: cube methodology developed inside 1B-α concurrently with agent arms; methodology bugs discovered during $300 run cost re-spend; rules-only baseline never independently surfaced.

## §7.6.3 How — components, data flow, dependencies

```
backtest/cube/
├── populator.py                     ★ NEW (built here; Phase 1B-α reuses)
├── verdict.py                       ★ NEW (5-Gate filter built here; Phase 1B-α reuses)
├── coordinates.py                   ★ NEW (cell coordinate library; shared with dashboards)
└── live_decision_lookup.py          ★ NEW (v1 from 1A-α; v2 from 1B-α)

dashboards/
├── cube_explorer/                   ★ NEW (DEC-199; rules-only filter built first)
└── ict_smc_audit/                   ★ NEW (DEC-200)

data/phase_1a_alpha/
├── cube/cube.parquet                ★ Phase 1A-α populator output
├── verdict/verdict.parquet          ★ 5-Gate filter output
├── live_decision_lookup/v1.parquet  ★ Pre-agent baseline lookup
└── summary/phase_1a_alpha_summary.md
```

**Data flow:**

```
Phase 1A trade_log.parquet
        │
        ▼
populator.py — group by 8-dim cell coordinates
        │
        ▼
cube.parquet (rules-only single arm)
        │
        ▼
verdict.py — 5-Gate filter
        │
        ▼
verdict.parquet (PASS / FAIL_RR / INSUFFICIENT_SAMPLE / FAIL_STAT per cell)
        │
        ▼
live_decision_lookup.py — extract PASS cells
        │
        ▼
v1.parquet (pre-agent baseline lookup)
        │
        ▼
Dashboards consume cube + verdict + lookup; render owner-facing view
        │
        ▼
Owner reviews; rules-only Sharpe ≥ 0.7 OOS gate decision → proceed to Phase 1A-β + 1B
```

## §7.6.4 When — sequence

**Sequence (~10-14d):**

| Day | Task |
|---|---|
| 1-2 | populator.py + coordinates.py |
| 3-4 | verdict.py 5-Gate filter |
| 5-6 | live_decision_lookup.py v1 |
| 7-9 | DEC-199 Cube Explorer dashboard (rules-only view) |
| 10-11 | DEC-200 ICT/SMC Audit dashboard |
| 12 | summary generator |
| 13 | Phase 1A-α end-to-end test on Phase 1A trade log |
| 14 | Owner review + gate decision |

## §7.6.5 Done criteria

- [ ] cube.parquet populated from Phase 1A trades
- [ ] verdict.parquet has every populated cell labeled
- [ ] PASS cell count > 0 (otherwise rules-only baseline is empty — Stage 2 has structural failure pre-agent layer)
- [ ] live_decision_lookup v1 exported
- [ ] Cube Explorer dashboard renders; rules-only filter functional
- [ ] ICT/SMC Audit dashboard renders; primitives validated
- [ ] phase_1a_alpha_summary.md owner-readable
- [ ] Owner reviews; rules-only Sharpe ≥ 0.7 OOS gate decision documented
- [ ] If gate passes: proceed to Phase 1A-β + 1B; if fails: revisit roster before agent overlay

## §7.6.6 Risks

**Risk R-1: Cube methodology bugs surface late**
- Mitigation: 1A-α IS the methodology validation; bugs caught here are cheap

**Risk R-2: Rules-only Sharpe < 0.7 OOS gate fails**
- Mitigation: this is a legitimate empirical outcome; owner gate decision protects $300 budget

**Risk R-3: Cube populator memory at full universe scale**
- 1015 tickers × 199 strategies (Pass 53 R7-02 fix) × ~100 trades each = potential memory pressure (recompute Sprint 9 dry-run capacity test)
- Mitigation: streaming aggregation; incremental writes

## §7.6.7 Cost

**Engineering:** ~10-14d
**Dollars:** $0 (no agent API spend in 1A-α)

## §7.6.8 Decisions in scope

| DEC | Title |
|---|---|
| 199 | Cube Explorer dashboard |
| 200 | ICT/SMC Audit dashboard |
| 422 | Cube 17+ dim (revised to 8 per DEC-471 PROPOSED) |
| 426 | 5-Gate verdict filter |
| 429 | Live decision lookup |
| 469 PROPOSED | BH FDR replacing Bonferroni |
| 470 PROPOSED | Hierarchical 3-level FDR |
| 471 PROPOSED | Cube dim reduction 17+ → 8 |
| 487 PROPOSED | Phase 1A-α restored as distinct sub-phase | 

## §7.6.9 Test approach

- Cube populator unit tests (small synthetic dataset)
- 5-Gate verdict tests (synthetic cells with known PASS/FAIL outcomes)
- Dashboard end-to-end render tests
- Phase 1A trade log sanity check before populate
- Owner acceptance review

## §7.6.10 Data dependencies

**Inputs:** Phase 1A trade_log.parquet
**Outputs:** Cube infrastructure reused by Phase 1B-α; pre-agent baseline lookup for Stage 3 fallback

## §7.6.11 Operational checklist

(See §7.6.4 day-by-day.)

## §7.6.12 Open issues — gaps from ADVERSARIAL_AUDIT

- **GAP 199 (NEW):** "1A-α dashboard view filter — rules-only specific" — not in original DEC-199 spec; resolution: §7.6.1 deliverable #3 explicitly adds rules-only filter
- **GAP 144 (existing):** What if all PASS cells are in INSUFFICIENT_SAMPLE band — same handling as Phase 1B-α; Gate 1 mutually exclusive precedence

## §7.6.13 Decision history

- Pass 52 turn 119: DEC-014 absorbed into DEC-422 + DEC-426 (cube methodology becomes single phase 1B-α)
- Pass 53 turn (this): Phase 1A-α restored as distinct sub-phase preceding 1B-α; cube infrastructure built once, reused

## §7.6.14 File / module structure

(See §7.6.3 component diagram.)

## §7.6.15 Example walkthrough

**Scenario:** Phase 1A produced 4,873 trades across 4 OOS folds. Phase 1A-α populates cube.

**Step 1:** populator.py groups trades:
```
Phase 1A trades: 4,873
  - Distinct strategies fired: 87 / 119 (32 strategies didn't fire — too narrow regime/cap criteria)
  - Cube cells populated: 1,247 / 254,016 max (0.49%)
```

**Step 2:** verdict.py applies 5-Gate filter:
```
Cell verdict breakdown:
  PASS: 89 (7.1%)
  FAIL_RR: 218 (17.5%)
  INSUFFICIENT_SAMPLE: 743 (59.6%)
  FAIL_STAT: 197 (15.8%)
```

**Step 3:** Owner reviews summary:
```
Rules-only verdict (Phase 1A-α):
  Aggregate Sharpe (rules-only, OOS): 0.81
  Max DD (rules-only, OOS): -18%
  Win rate: 53%
  PASS cell count: 89 (covers 6 strategies × 4 regimes × diverse sectors)
```

**Step 4:** Owner gate decision:
- Sharpe 0.81 > 0.7 OOS gate ✓
- Max DD -18% < 25% ✓
- Win rate 53% > 50% ✓
- PASS cell count 89 → diverse enough to support live trading on rules alone if agent overlay fails
- **Decision: PROCEED** to Phase 1A-β + Phase 1B

**Step 5:** v1.parquet exported as fallback live decision lookup. If Phase 1B-α agent overlay fails verdict, Stage 3 paper trading begins with v1 (rules-only) instead.

**Without Phase 1A-α:** Cube methodology built inside 1B-α concurrently; rules-only verdict only emerges when full 3-arm analysis done at end of $300 run; owner has no early gate to halt work on weak baseline.

---

# PART 7.7 — PHASE 1A-β: PRODUCTION-SCALE VALIDATION RUN (Sprint 7 Day 1)

## §7.7.1 What — concrete deliverable in plain English

Phase 1A-β is a **dry-run on full universe** that validates pipeline integrity at production scale BEFORE Phase 1B-α commits the $300 agent API budget. Inherits Phase 1B-α infrastructure but runs in `--no-agents --dry-run` mode. Catches infrastructure failures (cache corruption, PIT regression, multi-process race conditions, memory ceiling, walk-forward fold contamination, schema mismatches) at zero API spend.

Concrete deliverables:

1. **Full universe dry-run** — all ~1015 tickers × 4 walk-forward folds with `--no-agents` flag; engine produces same trades as Phase 1A but on full universe scope (Phase 1A operates on Phase 1A v3 67-instrument-equivalent subset for hand-validation; 1A-β scales to full)
2. **Pipeline integrity verification** — explicit checks: no PIT regression, no race conditions, no memory ceiling, no schema mismatches
3. **Cache hygiene under load** — disk monitor + LRU eviction + filelock work correctly during full-scale run
4. **Walk-forward fold non-contamination** — explicit train→OOS leakage tests pass at full scope
5. **Cube populator scales** — Phase 1B-α populator (built in 1A-α) successfully aggregates full 1015-ticker output without memory ceiling
6. **Owner gate decision** — owner reviews dry-run output before authorizing Phase 1B-α $300 budget commit

## §7.7.2 Why — how this advances Stage 2 toward verdict

Phase 1A-β catches infrastructure failures at zero API cost. Without it:
- Cache bug discovered mid-1B-α run = $300 + 20-32h per DEC-505 4-fold (Pass 53 R7-06 fix; was 37-40h pre-DEC-505 6-fold) re-run after fix
- PIT regression discovered mid-1B-α = same
- Memory ceiling crash mid-1B-α = same

1A-β cost: ~6-8h wall + 0 API spend. Insurance value: $300 + 20-32h per DEC-505 4-fold (Pass 53 R7-06 fix; was 37-40h pre-DEC-505 6-fold) potential re-run cost. **ROI overwhelming.**

## §7.7.3 How

```
backtest/phase_1a_beta/
├── orchestrator.py             ★ NEW (calls Phase 1B-α infra in --dry-run --no-agents mode)
└── integrity_checks.py         ★ NEW (explicit invariant verification)
```

**Data flow:** Same as Phase 1B-α run, but:
- `--no-agents` flag bypasses TradingAgents.propagate
- `--dry-run` flag may skip trade execution if owner prefers (vs full execution to validate Portfolio at scale — recommend full execution)
- Budget tracker confirms $0 spend
- Integrity checks run continuously during execution

## §7.7.4 When

**Sequence (~3-5d + 6-8h compute):**

| Day | Task |
|---|---|
| 1 | Phase 1A-β orchestrator (thin wrapper on 1B-α infrastructure) |
| 2 | Integrity check suite |
| 3 | Pre-run smoke test (1 fold × 100 candidates) |
| 4 | Full Phase 1A-β run; ~6-8h wall time |
| 5 | Owner gate review; authorize Phase 1B-α $300 spend |

## §7.7.5 Done criteria

- [ ] Full universe scale test passes; no PIT/race/memory/schema failures
- [ ] Cube populator scales successfully on full output
- [ ] Walk-forward fold non-contamination verified at full scope
- [ ] Budget tracker confirms $0 API spend during 1A-β
- [ ] Owner reviews; authorizes Phase 1B-α $300 budget

## §7.7.6 Risks

**Risk R-1: Infrastructure failure surfaces at full scale**
- This IS the purpose of 1A-β; failure here = success of 1A-β catching it

**Risk R-2: Wall time exceeds 6-8h estimate**
- Mitigation: progress monitor with ETA; parallel folds across local VS Code laptop cores (Pass 53 R7-03 fix; was Codespace cores)

## §7.7.7 Cost

**Engineering:** ~3-5d
**Compute:** ~6-8h wall
**Dollars:** $0

## §7.7.8 Decisions in scope

| DEC | Title |
|---|---|
| 488 PROPOSED | Phase 1A-β restored as distinct sub-phase |

## §7.7.9 Test approach

Phase 1A-β IS the integration test for the Phase 1B-α infrastructure.

## §7.7.10 Data dependencies

**Inputs:** Phase 1A-α infrastructure (populator, verdict, dashboards) reused
**Outputs:** Validation log; cleared infrastructure for Phase 1B-α

## §7.7.11 Operational checklist

- [ ] Orchestrator + integrity checks built
- [ ] Pre-run smoke test
- [ ] Full run wall time ~6-8h
- [ ] Owner gate

## §7.7.12 Open issues

- **GAP 489 (NEW):** Original PROJECT_PLAN had no scale-validation phase between 1A-α and 1B-α; resolution: this Part 7.7 introduces it explicitly

## §7.7.13 Decision history

- Pass 53 turn (this): Phase 1A-β added as scale-validation gate per owner directive symmetric to Phase 1B-α structure

## §7.7.14 File / module structure

(See §7.7.3 component diagram.)

## §7.7.15 Example walkthrough

**Scenario:** Phase 1A-α gate passed (rules-only Sharpe 0.81). Phase 1A-β runs on full 1015 tickers.

**Step 1:** Orchestrator launches 4 parallel fold processes; integrity checks running.

**Step 2:** Hour 3: integrity check fires — `cache_ohlcv` Parquet corrupt for ticker JBLU (memory pressure caused write failure during prefetch). Halt at fold boundary.

**Step 3:** Owner notified; cache rebuilt for JBLU; resume from last fold boundary.

**Step 4:** Hour 7: full run completes. Cube populator scales to full 1015-ticker output without memory ceiling.

**Step 5:** Budget tracker confirms $0 API spend (no agent calls).

**Step 6:** Owner reviews 1A-β report; authorizes Phase 1B-α $300 budget commitment.

**Without Phase 1A-β:** JBLU cache corruption discovered mid-1B-α with $147 spent + 23h wall time invested. Re-run cost ~$300 + 20-32h per DEC-505 4-fold (Pass 53 R7-06 fix; was 37-40h pre-DEC-505 6-fold).

---

# PART 8 — PHASE 1B: STATISTICAL METHODOLOGY + A/B + CUSTOM TOOLKITS (Sprint 7)

## §8.1 What — concrete deliverable in plain English

Phase 1B is the **largest sprint** (~96-108.5d post-DEC-462-468) and produces three intertwined deliverables:

**(A) Statistical methodology infrastructure** for the verdict cube — FDR (Benjamini-Hochberg) replacing Bonferroni per DEC-469 PROPOSED, hierarchical 3-level FDR per DEC-470, walk-forward validation per DEC-109, distribution analysis (skew/kurt/tail/PSR), stationarity testing.

**(B) A/B framework operational** — 3 arms (Rules-only / Full-with-veto / No-Risk per DEC-473 PROPOSED, reduced from 5), independent design per DEC-472 PROPOSED (eliminating paired design), block-bootstrap confidence intervals replacing paired t-test, opportunity-level pairing (every candidate evaluated by every arm) instead of trade-level pairing.

**(C) Custom TradingAgents toolkits + LangGraph state augmentation** — `OurTechnicalToolkit` (DEC-462), `OurFundamentalsToolkit` (DEC-463), `OurNewsToolkit` (DEC-464), `OurTraderToolkit` (DEC-465 NEW class), `OurRiskToolkit` (DEC-466 NEW class), `OurAgentState` schema extension with 7 new fields (DEC-467), Ortex wiring (DEC-468), and the AgentGateConfig per DEC-481 PROPOSED Option C2 (5-tier rating + markdown parser, supersedes DEC-459).

This is the sprint that turns the foundation (Sprints 1-6) into actual Stage 2 verdict-producing infrastructure.

Concrete deliverables grouped:

**Statistical methodology (~12-15d):**
1. `backtest/statistics/fdr.py` — Benjamini-Hochberg FDR implementation (q=0.10 default)
2. `backtest/statistics/hierarchical_fdr.py` — 3-level (per-strategy / per-cell / per-regime) FDR per DEC-470
3. `backtest/statistics/walk_forward.py` — 1y warmup + 1y rolling train / 1y OOS / 4 folds per DEC-505 Pass 53 (supersedes DEC-109 5y/1y/6 folds)
4. `backtest/statistics/distribution_analysis.py` — skew, kurtosis, tail metrics, PSR, t-stat
5. `backtest/statistics/stationarity.py` — ADF + Chow + rolling Sharpe stability
6. `backtest/statistics/bootstrap_ci.py` — block bootstrap CIs (block size = 20 trading days, 1000 iterations)

**A/B framework (~10-13d):**
7. `backtest/ab/orchestrator.py` — manages 3-arm execution (DEC-216 + DEC-473)
8. `backtest/ab/arm_definitions.py` — Rules-only / Full-with-veto / No-Risk arm configs
9. `backtest/ab/comparison.py` — block bootstrap CI comparison; per-regime verdicts
10. `backtest/ab/budget_tracking.py` — tracks API spend against $300 cap (DEC-059)

**Custom toolkits — Pattern 2 (~50-60d, the bulk of Sprint 7):**
11. `tradingagents_integration/our_technical_toolkit.py` (DEC-462) — extends TechnicalToolkit with intraday OHLCV + ICT/SMC + chart patterns + multi-TF regime
12. `tradingagents_integration/our_fundamentals_toolkit.py` (DEC-463) — extends FundamentalsToolkit with smart money composite + insider/congressional/13F/analyst estimates/transcripts via FMP
13. `tradingagents_integration/our_news_toolkit.py` (DEC-464) — extends NewsToolkit with macro news + sector context + earnings transcripts
14. `tradingagents_integration/our_trader_toolkit.py` (DEC-465 NEW) — Trader-specific tool set: get_current_price, get_volatility_estimate, get_borrow_cost, calls Portfolio class
15. `tradingagents_integration/our_risk_toolkit.py` (DEC-466 NEW) — Risk-debater-specific tool set: get_correlation_to_existing_positions, get_sector_concentration, get_drawdown_context, get_historical_outcomes (DEC-189 reflection log)
16. `tradingagents_integration/our_agent_state.py` (DEC-467) — Pydantic schema extension with 7 new fields: smart_money_signal, regime_context, portfolio_context, event_proximity, sector_context, short_interest_signal, historical_outcomes
17. `tradingagents_integration/state_injection.py` (DEC-467) — LangGraph nodes that inject state at Phase 1/2/3 entry points
18. `tradingagents_integration/ortex_client.py` (DEC-468) — Ortex API client; cached short interest signals
19. `tradingagents_integration/agent_gate.py` (DEC-481 Option C2 PROPOSED) — markdown parser for PM/RM/Trader/Risk Debate ratings; 5-tier mapping; Risk veto + RM alignment + Trader cross-check

**Cube populator (~6-8d):**
20. `backtest/cube/populator.py` — groups trades by 8-dim cell (per DEC-471 PROPOSED reduced cube); computes per-cell metrics suite per DEC-422
21. `backtest/cube/verdict.py` — applies 5-Gate filter (DEC-426); assigns PASS/FAIL_RR/INSUFFICIENT_SAMPLE/FAIL_STAT
22. `backtest/cube/live_decision_lookup.py` — produces DEC-429 lookup table from PASS cells

## §8.2 Why — how this advances Stage 2 toward verdict

This is the sprint that **literally produces Stage 2 verdict.** Every other phase is pre-requisite plumbing; Phase 1B is the methodology + framework that converts plumbing into a verdict.

Specific dependencies:

- **Cube needs FDR** (DEC-469) or thresholds are mathematically unattainable (Stage 2 effectiveness Blocker B1)
- **A/B needs 3-arm budget reconciliation** (DEC-473 reduce + DEC-472 independent) or budget overruns 5-7× (Blocker B2)
- **A/B needs valid statistical comparison** (DEC-472 block bootstrap) or paired design is invalid (Blocker B3)
- **Agent overlay needs Pattern 2 toolkits** or framework operates on degraded data (Blocker B5 architectural)
- **Cube populator needs walk-forward** to produce out-of-sample trades; in-sample trades cannot populate live decision lookup
- **Ortex wiring** completes short interest signal; without it, short strategies + Bull/Bear research lack key input
- **AgentGateConfig per DEC-481** turns TradingAgents output into trade decisions; without it, agent overlay produces text but no trade

If Sprint 7 is wrong, Stage 2 verdict is wrong regardless of how good Sprints 1-6 were.

## §8.3 How — components, data flow, dependencies

**Component diagram:**

```
backtest/
├── statistics/
│   ├── fdr.py                         ★ NEW (DEC-469)
│   ├── hierarchical_fdr.py            ★ NEW (DEC-470)
│   ├── walk_forward.py                ★ NEW (DEC-109)
│   ├── distribution_analysis.py       ★ NEW
│   ├── stationarity.py                ★ NEW
│   └── bootstrap_ci.py                ★ NEW (DEC-472)
├── ab/
│   ├── orchestrator.py                ★ NEW (DEC-216 + DEC-473)
│   ├── arm_definitions.py             ★ NEW
│   ├── comparison.py                  ★ NEW
│   └── budget_tracking.py             ★ NEW
├── cube/
│   ├── populator.py                   ★ NEW (DEC-422 + DEC-471)
│   ├── verdict.py                     ★ NEW (DEC-426)
│   └── live_decision_lookup.py        ★ NEW (DEC-429)

tradingagents_integration/
├── our_technical_toolkit.py            ★ NEW (DEC-462)
├── our_fundamentals_toolkit.py         ★ NEW (DEC-463)
├── our_news_toolkit.py                 ★ NEW (DEC-464)
├── our_trader_toolkit.py               ★ NEW (DEC-465)
├── our_risk_toolkit.py                 ★ NEW (DEC-466)
├── our_agent_state.py                  ★ NEW (DEC-467)
├── state_injection.py                  ★ NEW (DEC-467)
├── ortex_client.py                     ★ NEW (DEC-468)
└── agent_gate.py                       ★ NEW (DEC-481 PROPOSED Option C2)
```

**Data flow during Sprint 9 Phase 1B-α run (with Sprint 7 deliverables operational):**

```
DAILY SCAN — strategy fires; candidate ticker AAPL produced
        │
        ▼
Liquidity + event suppression + per-ticker risk gates pass
        │
        ▼
Selective agent overlay decision (cost + value):
    - Is this candidate in agent-overlay subset? (top-tier strategies; uncertain rules signals)
    - If yes, call propagate
        │
        ▼
state_injection.py — augment OurAgentState with:
    - smart_money_signal (DEC-124 confluence)
    - regime_context (DEC-106 + crisis flags)
    - portfolio_context (Portfolio.get_portfolio_state())
    - event_proximity (DEC-348 events)
    - sector_context (DEC-151 sector regime)
    - short_interest_signal (Ortex via ortex_client)
    - historical_outcomes (DEC-189 reflection log)
        │
        ▼
TradingAgents.propagate("AAPL", "2022-06-15") — runs 12-agent pipeline
    Phase 1 — Analysts use OurTechnicalToolkit, OurFundamentalsToolkit, OurNewsToolkit
    Phase 2 — Bull/Bear debate; Research Manager synthesis (5-tier rating)
    Phase 3 — Trader uses OurTraderToolkit (3-tier rating)
    Phase 4 — Risk Debaters use OurRiskToolkit; Portfolio Manager synthesis (5-tier rating)
    Phase 5 — Reflection writes to DEC-189 log
        │
        ▼
agent_gate.py — DEC-481 Option C2 logic:
    parse PM rating from rendered markdown
    parse RM rating from rendered markdown
    parse Trader rating from rendered markdown
    parse Risk Debate consensus from rendered markdown
    apply 5-tier → tier mapping
    apply Risk veto, RM alignment, Trader cross-check
    output: TIER (HIGH/MEDIUM/LOW) or REJECT
        │
        ▼
A/B SPLIT — output processed by 3 arms:
    Arm A (Rules-only) — bypass agent_gate; use rules-based tier
    Arm B (Full-with-veto) — agent_gate output as-is
    Arm C (No-Risk) — agent_gate output WITHOUT Risk veto check
        │
        ▼
Per-arm trade execution (separate Portfolio instances per arm)
        │
        ▼
END OF FOLD — cube populator groups all trades by 8-dim cell
        │
        ▼
Per-cell metrics suite computed (sharpe, sortino, etc. per DEC-422)
        │
        ▼
verdict.py applies 5-Gate filter:
    Gate 1 — n ≥ 30 → INSUFFICIENT_SAMPLE if not
    Gate 2 — FDR q < 0.10 (hierarchical per DEC-470)
    Gate 3 — PSR ≥ 0.95
    Gate 4 — t-stat ≥ 3.4
    Gate 5 — R:R ≥ 2.0 (DEC-353)
    Verdict assigned
        │
        ▼
live_decision_lookup.py produces lookup table from PASS cells
        │
        ▼
ab/comparison.py — block bootstrap CIs across arms; per-regime verdicts
```

**Dependencies (from this sprint to others):**
- Sprint 0A (cache layer)
- Sprint 2 (engine fixes)
- Sprint 3 (Portfolio class — toolkit Trader/Risk depend)
- Sprint 4 (Polygon reference / Quiver paid endpoints / FMP if approved)
- Sprint 6 (catch-mechanism — testing this sprint's deliverables)
- Phase 0.D (smartmoneyconcepts library forked Sprint 1 + integrated Sprint 8)

**External services:**
- TradingAgents v0.2.4 framework (cloned + pinned)
- Anthropic API (claude-sonnet-4 deep + claude-haiku quick) for agent calls
- OR OpenAI / Gemini / DeepSeek alternatives if cost-optimization (DEC-058 GPT-5.4-mini for backtest cost-optimized)

**Library dependencies:**
- `tradingagents` (Pattern 2 integration)
- `langgraph` (transitive)
- `pydantic` (state schema)
- `statsmodels` (ADF + Chow + bootstrap)
- `scipy.stats` (FDR + PSR + distribution analysis)
- `arviz` (bootstrap CI visualization optional)

## §8.4 When

**Sequence within Sprint 7 (~96-108.5d):**

| Week | Focus |
|---|---|
| Week 1 | Foundation: clone TradingAgents v0.2.4; smoke test propagate(); pin SHA |
| Week 2-3 | Statistical methodology: FDR + hierarchical + bootstrap CI |
| Week 3-4 | Walk-forward + distribution + stationarity |
| Week 4-5 | A/B framework: orchestrator + arm definitions + comparison |
| Week 5-6 | OurTechnicalToolkit (DEC-462) — 7-10 methods |
| Week 7-8 | OurFundamentalsToolkit (DEC-463) — financials + smart money composite |
| Week 9 | OurNewsToolkit (DEC-464) — macro + sector context |
| Week 10-11 | OurTraderToolkit (DEC-465 NEW) — Portfolio integration |
| Week 12-13 | OurRiskToolkit (DEC-466 NEW) — correlation + drawdown context + DEC-189 historical |
| Week 14 | OurAgentState schema (DEC-467) — Pydantic; LangGraph injection |
| Week 14 | Ortex client + wiring (DEC-468) |
| Week 15-16 | agent_gate.py — DEC-481 Option C2 markdown parser + tier mapping |
| Week 17-18 | Cube populator + verdict.py |
| Week 19-20 | Live decision lookup table |
| Week 21-22 | Integration tests + acceptance demo + bug fixes + PR review |

**Total: ~96-108.5d realistic.**

This is the longest sprint by ~30% over Sprint 6. Resources should be focused; calendar can stretch to ~5 calendar months at typical solo developer cadence.

**Blockers:**
- DEC-478 — Polygon tier upgrade decision (FMP availability for OurFundamentalsToolkit)
- DEC-481 PROPOSED — AgentGateConfig Option C2 approval
- Sprints 1-6 substantially complete

**Parallel-ability:**
- Sprint 7 ↔ Sprint 8: **partial** — Sprint 8 (strategy categories) can run parallel to Sprint 7 toolkit work
- Sprint 7 toolkits are mostly self-contained; can be built in any order after Week 4

## §8.5 Done criteria

- [ ] All 22 deliverables (§8.1) implemented and tested
- [ ] FDR methodology produces sensible PASS rates on synthetic data (verified)
- [ ] Block bootstrap CIs produce sensible CIs (verified against known distributions)
- [ ] 3-arm A/B orchestrator runs end-to-end on small sample (10 candidates × 3 arms)
- [ ] 6 toolkits operational; can be swapped into TradingAgents via Pattern 2
- [ ] OurAgentState fields populated in LangGraph state at Phase 1/2/3 entry points
- [ ] DEC-481 Option C2 markdown parser handles 5-tier rating, Trader 3-tier, Risk Debate consensus, RM 5-tier
- [ ] AgentGateConfig produces TIER assignment (HIGH/MEDIUM/LOW/REJECT) per DEC-481 spec
- [ ] Cube populator handles 254K-cell maximum cube (revised per DEC-471); per-cell metrics suite computed
- [ ] verdict.py assigns PASS / FAIL_RR / INSUFFICIENT_SAMPLE / FAIL_STAT correctly
- [ ] live_decision_lookup.py produces table queryable for Stage 3 entry
- [ ] Ortex API client cached; short interest signal flows into Bull/Bear agent reasoning
- [ ] Sprint 7 PR merged; CI green; Phase 1B-α small-scale dry run successful

## §8.6 Risks

**Risk R-1: TradingAgents v0.2.4 markdown format changes**
- Pinned SHA mitigates; but if upstream releases v0.2.5 with format change, our parser breaks
- Mitigation: pin SHA; review upstream changes before adopting

**Risk R-2: Pattern 2 integration friction**
- Custom toolkits may have unexpected interaction with their default toolkits (e.g., method name collision)
- Mitigation: explicit subclass approach (extends TechnicalToolkit) with method override discipline; integration test verifies expected toolkit methods called

**Risk R-3: Markdown parser brittleness**
- DEC-481 Option C2 reads PM rating from rendered markdown — if rendering varies per LLM provider, parser breaks
- Mitigation: parser handles 3 known formats (OpenAI / Anthropic / Gemini); defensive fallback; conservative REJECT if parsing fails (per CHECKLIST #51 conservative defaults)

**Risk R-4: Cube populator memory at scale**
- 254K cells × 17+ metrics × 4 OOS folds (DEC-505) → high memory; manageable on local laptop
- Mitigation: streaming aggregation (don't load all trades into memory); incremental cell metric computation
- If still high: cloud burst for Sprint 9 cube populate (one-time cost)

**Risk R-5: A/B comparison statistical interpretation**
- Block bootstrap CIs may overlap due to insufficient sample
- Mitigation: increase sample (more candidates); accept inconclusive verdict per regime; per-regime verdicts may be stronger than aggregate

**Risk R-6: FMP availability**
- DEC-461 conditional on DEC-460 verification negative (now confirmed); FMP subscription pending owner approval
- Mitigation: DEC-478 owner decision pre-Sprint-7; if owner declines FMP, OurFundamentalsToolkit operates degraded (no transcripts, limited financials)

**Risk R-7: Ortex API quirks**
- DEC-468 wires Ortex; API contract not yet verified in production use
- Mitigation: smoke test Ortex Day 1 of Sprint 7 Week 14; if API issues, fallback to Polygon shorts data (less complete)

## §8.7 Cost

**Engineering effort:** ~96-108.5d (longest sprint)
**Subscription cost (Sprint 7 incremental):**
- TradingAgents framework: free (open source)
- Anthropic API for agent calls during testing: ~$50-100 (Sprint 7 dev cost; not the $300 Phase 1B-α budget)
- FMP (if DEC-461 approved): $14-50/mo (already in Sprint 4 cost)
- Ortex (DEC-468): TBD subscription cost; budget $50-100/mo
- Quiver paid expansion (DEC-450/451): already in Sprint 4 cost

**Sprint 7 incremental monthly subscriptions: $50-150/mo (Ortex + dev API costs). The $300 Phase 1B-α run budget is separate (Sprint 9).**

## §8.8 Decisions in scope

| DEC | Title | Status |
|---|---|---|
| 058 | GPT-5.4-mini for backtest (cost-optimized) | RESOLVED-DECIDED |
| 059 | $300 Phase 1B-α budget hard cap | RESOLVED-DECIDED |
| 109 | Walk-forward 5y train / 1y OOS / 6 folds | RESOLVED-DECIDED |
| 124 | Smart money cross-source confluence | RESOLVED-DECIDED |
| 131 | Two-gate A/B logic ≥ 0.2 abs Sharpe / ≥ 0.15 rel | RESOLVED-DECIDED |
| 189 | Reflection log persistent decision history | RESOLVED-DECIDED |
| 205-216 | A/B framework cluster | RESOLVED-DECIDED |
| 332 | Smart money composite weights | RESOLVED-DECIDED |
| 348 | Event suppression asymmetric pre/post windows | RESOLVED-DECIDED |
| 422 | Cube 17+ dimensions (revised to 8 per DEC-471) | RESOLVED-DECIDED |
| 426 | 5-Gate cube verdict filter | RESOLVED-DECIDED |
| 429 | Live decision lookup from PASS cells | RESOLVED-DECIDED |
| 459 | AgentGateConfig Option C Hybrid (SUPERSEDED by DEC-481) | SUPERSEDED |
| 462 | OurTechnicalToolkit | RESOLVED-DECIDED |
| 463 | OurFundamentalsToolkit | RESOLVED-DECIDED |
| 464 | OurNewsToolkit | RESOLVED-DECIDED |
| 465 | OurTraderToolkit (NEW) | RESOLVED-DECIDED |
| 466 | OurRiskToolkit (NEW) | RESOLVED-DECIDED |
| 467 | OurAgentState schema + injection | RESOLVED-DECIDED |
| 468 | Ortex wiring | RESOLVED-DECIDED |
| 469 PROPOSED | BH FDR replacing Bonferroni (q=0.10) | Awaits owner approval |
| 470 PROPOSED | Hierarchical 3-level FDR | Awaits owner approval |
| 471 PROPOSED | Cube dim reduction 17+ → 8 core | Awaits owner approval |
| 472 PROPOSED | Eliminate paired A/B; bootstrap CIs | Awaits owner approval |
| 473 PROPOSED | A/B arm reduction 5 → 3 | Awaits owner approval |
| 474 PROPOSED | DEC-459 → DEC-481 supersession | Awaits owner approval |
| 475 PROPOSED | RM + Trader cross-check via 5-tier | Awaits owner approval |
| 480 PROPOSED | TradingAgents v0.2.4 specific pin | Awaits owner approval |
| 481 PROPOSED | AgentGateConfig Option C2 (5-tier markdown parser) | Awaits owner approval |

## §8.9 Test approach

**Unit tests** per module (~100+ test files):
- Statistical: FDR / hierarchical FDR / bootstrap / walk-forward fold generation / distribution / stationarity
- A/B: orchestrator / arm definitions / comparison
- Cube: populator / verdict / live decision lookup
- Toolkits: 6 toolkit modules each with 5-15 method tests
- agent_gate: markdown parser handles 3 LLM provider formats; tier mapping verified

**Integration tests:**
- End-to-end propagate → state injection → toolkit calls → agent_gate → A/B arms → cube cell
- Small-scale Phase 1B-α dry run (10 candidates × 3 arms × 1 fold)

**Property tests:**
- FDR retains expected fraction of true positives on synthetic data
- Bootstrap CIs cover true Sharpe with expected probability

**Acceptance:** Owner reviews dry-run output (cube cells, A/B comparison, dashboards); confirms direction matches expectation.

## §8.10 Data dependencies

**Inputs:**
- Sprint 0A cache + Sprint 4 financials (FMP) + Sprint 5 universe + Sprint 3 Portfolio
- TradingAgents v0.2.4 source (forked locally)
- Quiver paid + Ortex + AAII + CNN F&G data

**Outputs:**
- Cube populated with PASS / FAIL / INSUFFICIENT cells
- A/B verdict per regime per arm
- Live decision lookup table for Stage 3
- DEC-189 reflection log entries

## §8.11 Operational checklist

(See §8.4 week-by-week.)

## §8.12 Open issues — gaps from ADVERSARIAL_AUDIT

- **GAP 39, 40, 49, 50, 85 (CRITICAL):** TradingAgents schema verification — RESOLVED Pass 52 turn 133 via DEC-481 PROPOSED Option C2 markdown parser
- **GAP 51 (CRITICAL):** A/B budget — RESOLVED via DEC-472 + DEC-473 ($75-225 vs $1500-2000)
- **GAP 126 (CRITICAL):** Bonferroni unattainable — RESOLVED via DEC-469 FDR
- **GAP 130 (CRITICAL):** Sample size impossible — RESOLVED via DEC-471 dim reduction
- **GAP 133 (CRITICAL):** Paired design invalid — RESOLVED via DEC-472 bootstrap independent
- **GAP 41-48:** Toolkit method specs — addressed in §8.1 deliverables 11-19
- **GAP 53:** Two-gate Bonferroni at scale — SUPERSEDED by DEC-470 hierarchical FDR
- **GAP 134, 135:** Sample size SE noise floor — addressed by DEC-472 block bootstrap CI methodology

## §8.13 Decision history

This is the most-decision-dense sprint. Major sequence:
- DEC-205-216 (Pass ~30): A/B framework cluster
- DEC-422 (Pass ~40): Cube 17+ dimensions
- DEC-426 (Pass ~42): 5-Gate verdict filter
- DEC-462-468 (Pass 52 turn 130): Pattern 2 toolkit specs
- DEC-469-481 PROPOSED (Pass 52 turn 133): Statistical + A/B + Pattern 2 corrections per ADVERSARIAL_AUDIT findings

## §8.14 File / module structure

(See §8.3 component diagram — most extensive of any sprint.)

## §8.15 Example walkthrough

**Scenario:** Sprint 7 complete; running Phase 1B-α dry run. AAPL candidate fires 2022-06-15 with strategy `RSI_Mean_Reversion_30_70`.

**Step 1:** state_injection populates OurAgentState with:
```python
state = OurAgentState(
    smart_money_signal={'composite': 0.65, 'insider_net_buy_30d': True, ...},
    regime_context={'regime': 'volatile', 'crisis_flag': False, ...},
    portfolio_context={'cash': 50000, 'positions': {...}, 'drawdown': -0.05, ...},
    event_proximity={'days_to_earnings': 8, 'days_to_fomc': 21, ...},
    sector_context={'tech_regime': 'volatile', ...},
    short_interest_signal={'days_to_cover': 2.3, 'borrow_cost_bps': 25, ...},
    historical_outcomes=[{'ticker': 'AAPL', 'date': '2021-06-15', 'rating': 'Buy', 'realized_alpha': 0.04}, ...]
)
```

**Step 2:** TradingAgents.propagate("AAPL", "2022-06-15") runs:
- Phase 1: Market Analyst calls OurTechnicalToolkit.get_technical_indicators("AAPL", "2022-06-15") → RSI=28, MACD bearish cross 3 days ago, etc.
- Phase 1: Fundamentals Analyst calls OurFundamentalsToolkit.get_smart_money_composite("AAPL", "2022-06-15") → 0.65 net buying
- Phase 1: News Analyst calls OurNewsToolkit.get_recent_news("AAPL", "2022-06-15") → mixed sentiment
- Phase 2: Bull/Bear debate ... Research Manager rating: "Buy" (5-tier)
- Phase 3: Trader calls OurTraderToolkit.get_volatility_estimate → high vol; rating: "Hold" (3-tier; cautious)
- Phase 4: Risk Debaters argue; Aggressive bullish, Conservative concerned about volatility, Neutral neutral; Portfolio Manager rating: "Overweight" (5-tier)
- Phase 5: Reflection logs to DEC-189

**Step 3:** agent_gate.py parses rendered markdown:
- PM rating: Overweight (parsed from PM final markdown section)
- RM rating: Buy (parsed from RM section)
- Trader rating: Hold (parsed from Trader section)
- Risk Debate consensus: Approve (no veto fired, neutral synthesis)

**Step 4:** Tier mapping (DEC-481 Option C2):
- PM rating Overweight → MEDIUM tier candidate (3% sizing)
- RM rating Buy → align ✓ (Buy is bullish; Overweight is bullish; same direction)
- Trader rating Hold → cross-check downgrade trigger (Trader cautious vs PM bullish) → keep MEDIUM, do not upgrade to HIGH
- Risk veto not fired → not REJECT
- Final tier: **MEDIUM (3% sizing)**

**Step 5:** A/B arms split:
- Arm A (Rules-only): RSI=28 oversold + smart money composite 0.65 → preliminary tier = MEDIUM (3%)
- Arm B (Full-with-veto): MEDIUM tier per DEC-481 (above) — agrees with Arm A coincidentally
- Arm C (No-Risk): same as Arm B but Risk Debate ignored — same MEDIUM tier (Risk debate didn't change outcome here)

**Step 6:** Each arm executes 3% position separately. End of fold, all 3 arms' trades feed cube.

**Step 7:** Cube cell `(RSI_MR, volatile, Tech, mega, high_vol, hold_band, T1, smart_money_yes)` populated with this trade + all similar trades. Per-cell metrics computed.

**Step 8:** 5-Gate filter applied. If cell has n=42 trades, FDR q=0.05 (passes 0.10), PSR=0.96 (passes 0.95), t-stat=3.7 (passes 3.4), R:R=2.3 (passes 2.0) → **PASS**.

**Step 9:** Cell goes into live decision lookup table.

**Step 10:** A/B comparison: Arm B Sharpe 1.4 vs Arm A Sharpe 1.1 = +0.3 absolute → Arm B beats Arm A by 0.3 (above DEC-131 threshold 0.2 absolute) → **agent overlay justified for this regime/sector cell**.

**This entire trace requires Sprint 7 done.** Without it: no toolkit calls, no agent rating extraction, no A/B framework, no cube, no verdict.

---

# PART 9 — PHASE 1B-α: DIMENSIONAL CUBE + DASHBOARDS (Sprint 7-8 dashboards + Sprint 9 run)

## §9.1 What — concrete deliverable in plain English

Phase 1B-α is the **Stage 2 verdict run itself**. By the end of this phase, the dimensional verdict cube is populated with trades from a complete walk-forward backtest (6 OOS folds covering ~6 years), per-cell metrics computed, 5-Gate verdict assigned, A/B comparison performed, and three owner-facing dashboards rendered. This is the moment Stage 2 either passes or fails.

The phase has two components:
- **Sprint 7-8 dashboards** (DEC-199, DEC-200, DEC-201) — the visualization layer that lets the owner inspect the cube
- **Sprint 9 cube run + verdict** — the actual end-to-end Phase 1B-α execution that produces the cube data

Concrete deliverables:

**Dashboards (Sprint 7-8, ~10-12d):**
1. **Cube Explorer dashboard (DEC-199)** — interactive HTML/Streamlit dashboard letting owner slice the cube on any of the 8 dimensions; per-cell metrics table; cell-detail drilldown showing constituent trades; PASS/FAIL_RR/INSUFFICIENT_SAMPLE/FAIL_STAT verdict color coding
2. **ICT/SMC Audit dashboard (DEC-200)** — focused view on Phase 0.D primitives: FVG detection accuracy, BOS/CHoCH validity, OB zone-bounce hit rates per ticker per timeframe; lets owner verify SMC strategies are firing correctly
3. **Agent Overlay Analysis dashboard (DEC-201)** — A/B framework comparison view: per-arm Sharpe / DD / win rate / trade count; per-regime verdict (full-agent value-add vs rules-only); block-bootstrap CI overlap visualization; cost spent vs $300 budget

**Sprint 9 run (~6d orchestration; ~20-32h per DEC-505 4-fold (Pass 53 R7-06 fix; was 37-40h pre-DEC-505 6-fold) wall compute):**
4. **Phase 1B-α orchestrator** — `backtest/phase_1b_alpha/run.py` master script that executes the full walk-forward across all 4 OOS folds (per DEC-505 4-fold; Pass 53 R7-06 fix; was 6 folds pre-DEC-505), all 199 strategies (Pass 53 R7-02 fix), all 3 A/B arms
5. **Walk-forward fold execution** — DEC-109 spec: 5y train + 1y OOS × 6 folds. Train period populates strategy parameters; OOS period generates trades for cube
6. **Parallel fold execution** — folds run in parallel processes (local VS Code 8+ core laptop per Pass 53 R7-03 fix; was Codespace 8-core; up to 4 concurrent folds per DEC-505 with file-locked cache)
7. **Trade outcome log** — per DEC-189 Pydantic schema; written to Parquet incrementally (avoid in-memory bloat per Sprint 7 R-4)
8. **Cube populator end-of-run** — group trades by 8-dim cell coordinates; compute per-cell metrics suite (DEC-422)
9. **5-Gate verdict assignment** — DEC-426 (Gate 1 n≥30, Gate 2 FDR q<0.10 hierarchical per DEC-470 PROPOSED, Gate 3 PSR≥0.95, Gate 4 t-stat≥3.4, Gate 5 R:R≥2.0)
10. **A/B comparison** — block-bootstrap CIs across 3 arms per DEC-472 PROPOSED; per-regime verdicts
11. **Live decision lookup table generation** — PASS cells exported to lookup table for Stage 3 entry per DEC-429
12. **DEC-189 reflection log persistence** — every agent-overlay candidate outcome (rating, realized return, Sharpe contribution) logged for Phase 1B-α retrospective and Stage 3+ historical context
13. **Cost tracking and budget enforcement** — running tally against $300 budget per DEC-059; halt if budget exceeded mid-run
14. **End-of-run owner-readable summary** — `phase_1b_alpha_summary.md` with verdict pass-rate per regime, A/B Sharpe deltas, total cost, anomalies

## §9.2 Why — how this advances Stage 2 toward verdict

This IS the Stage 2 verdict. Every other phase contributes pieces; Phase 1B-α puts them together and produces the answer:

- Does the strategy roster have empirical edge? (cube PASS rate per regime per cell)
- Does the agent overlay add value over rules-only? (A/B comparison verdict per arm)
- Does the system meet quantitative gates? (Sharpe ≥ 1.0 OOS, max DD ≤ 25%, win rate ≥ 50%)
- Is there a defensible live decision lookup table for Stage 3? (PASS cell count + diversity)

If Phase 1B-α produces zero PASS cells across 254K-cell cube, Stage 2 has failed — strategy roster has no provable edge. If A/B framework finds full-agents Sharpe < rules-only by more than 0.2 absolute, agent overlay is rejected (rules-only proceeds to Stage 3). If both arms fail Sharpe gate, Stage 2 must be revisited (Part 13.3 covers).

The dashboards are how the owner reviews this verdict. Without dashboards, the cube is opaque — millions of cell-trade combinations are not human-reviewable as raw data.

## §9.3 How — components, data flow, dependencies

**Component diagram:**

```
backtest/
├── phase_1b_alpha/
│   ├── run.py                       ★ NEW Sprint 9 (orchestrator)
│   ├── fold_executor.py             ★ NEW Sprint 9 (per-fold execution)
│   ├── parallel_runner.py           ★ NEW Sprint 9 (multi-process)
│   ├── progress_monitor.py          ★ NEW Sprint 9 (live progress + ETA)
│   ├── budget_tracker.py            ★ NEW Sprint 9 (real-time cost)
│   └── summary_generator.py         ★ NEW Sprint 9 (end-of-run summary)

dashboards/
├── cube_explorer/                   ★ NEW Sprint 7-8 (DEC-199)
│   ├── app.py                        # Streamlit entry
│   ├── components/
│   │   ├── cube_slicer.py
│   │   ├── cell_detail.py
│   │   └── verdict_heatmap.py
│   └── data/
│       └── cube.parquet
├── ict_smc_audit/                   ★ NEW Sprint 7-8 (DEC-200)
│   ├── app.py
│   └── components/
│       ├── fvg_audit.py
│       ├── bos_audit.py
│       └── ob_zone_audit.py
└── agent_overlay_analysis/          ★ NEW Sprint 7-8 (DEC-201)
    ├── app.py
    └── components/
        ├── arm_comparison.py
        ├── regime_verdict.py
        └── budget_tracker_view.py

data/
├── phase_1b_alpha/
│   ├── trade_log/
│   │   └── fold_{N}/trades.parquet  ★ Sprint 9 run produces
│   ├── cube/
│   │   └── cube.parquet              ★ Sprint 9 cube populator
│   ├── cube_verdicts/
│   │   └── verdict.parquet           ★ Sprint 9 verdict assignment
│   ├── ab_comparison/
│   │   └── ab_results.parquet        ★ Sprint 9 A/B comparison
│   ├── live_decision_lookup/
│   │   └── lookup.parquet            ★ Sprint 9 — Stage 3 entry artifact
│   └── reflection_log/
│       └── reflections.parquet       ★ Sprint 9 — agent decision log
```

**Data flow during Phase 1B-α run:**

```
run.py invokes — for each of 6 OOS folds:
        │
        ▼
fold_executor.py:
    1. Determine fold dates (5y train + 1y OOS)
    2. Load PIT-correct universe at OOS start
    3. For each trading day in OOS year:
        a. Load OHLCV + signal universe (Sprint 0A cache)
        b. Run rules-based screen — produces candidate list
        c. Apply liquidity + event suppression + per-ticker risk gates
        d. For each remaining candidate:
            i. Selective agent overlay decision (subset rule)
            ii. If overlay invoked: TradingAgents.propagate
            iii. Apply DEC-481 Option C2 gate (PM tier + Risk veto + RM align + Trader cross-check)
            iv. A/B split: Rules-only / Full-with-veto / No-Risk arms
        e. Each arm's Portfolio executes trades (separate Portfolio per arm)
        f. End of day: update_market_values, log open positions
    4. End of OOS year: close remaining positions; persist trade log
        │
        ▼
parallel_runner.py spawns up to 8 fold processes in parallel
        │
        ▼
budget_tracker.py monitors API spend; halts if > $300
        │
        ▼
After all folds complete:
        │
        ▼
populator.py groups all trades by 8-dim cell coordinates (per DEC-471 PROPOSED)
        │
        ▼
cube.parquet written
        │
        ▼
verdict.py applies 5-Gate filter (DEC-426); produces verdict.parquet
        │
        ▼
ab/comparison.py computes block-bootstrap CIs across 3 arms; produces ab_results.parquet
        │
        ▼
live_decision_lookup.py exports PASS cells; produces lookup.parquet
        │
        ▼
summary_generator.py writes phase_1b_alpha_summary.md
        │
        ▼
Owner opens dashboards (Streamlit servers); reviews verdict
        │
        ▼
Stage 2 → Stage 3 GO/NO-GO decision (Part 13)
```

**Dependencies:**
- All prior sprints (1-8) must be RESOLVED-IMPLEMENTED before Sprint 9 starts
- Specifically: Sprint 7 cube populator + verdict.py + AB orchestrator + agent_gate; Sprint 0A cache; Sprint 3 Portfolio; Sprint 4 fundamentals; Sprint 5 universe; Sprint 6 catch-mechanism (CI gates protect run integrity)

**Library dependencies:**
- `streamlit` (dashboards)
- `plotly` (dashboard charts)
- `multiprocessing` (parallel fold execution)
- `pyarrow` (Parquet incremental writes)
- `tqdm` (progress monitoring)

## §9.4 When — sequence, blockers, parallel-ability

**Sequence:**

| Phase | Sprint | Activity | Days |
|---|---|---|---|
| Dashboards build | Sprint 7-8 | DEC-199 Cube Explorer | 4-5d |
| Dashboards build | Sprint 7-8 | DEC-200 ICT/SMC Audit | 3d |
| Dashboards build | Sprint 7-8 | DEC-201 Agent Overlay Analysis | 3-4d |
| **Run pre-flight** | **Sprint 9 Day 1** | Verify all prior sprints RESOLVED-IMPLEMENTED; smoke test 1 fold 10 candidates | 1d |
| **Run** | **Sprint 9 Days 2-5** | Parallel 6-fold execution wall-time ~20-32h per DEC-505 4-fold (Pass 53 R7-06 fix; was 37-40h pre-DEC-505 6-fold) | 4d wall (orchestration; mostly compute time) |
| Cube populate | Sprint 9 Day 5 | populator.py + verdict.py + ab/comparison.py + lookup | 1d |
| Owner review | Sprint 9 Day 6 | Owner reviews dashboards; decision Stage 2 → 3 | — |

**Total Phase 1B-α: ~28-38d engineering effort across Sprints 7-8-9; Sprint 9 dedicated run is ~6d engineering + ~20-32h per DEC-505 4-fold (Pass 53 R7-06 fix; was 37-40h pre-DEC-505 6-fold) compute time.**

**Blockers:**
- **All Sprints 1-8 RESOLVED-IMPLEMENTED.** Phase 1B-α is the integration/run; if any prior sprint has open issues, run produces invalid results.
- **DEC-478 Polygon tier upgrade approved + active** — historical depth must cover 2018-2026 for 6 OOS folds (Stocks Developer 10y minimum)
- **DEC-461 FMP active** if approved — fundamentals required for OurFundamentalsToolkit during agent calls
- **Budget pre-loaded** — owner pre-funds API spend $300 budget per DEC-059; tracker enforces real-time
- **Cube run not interruptible mid-fold** — once started, must complete or restart from beginning (cache state idempotency only at fold boundaries, not mid-fold)

**Parallel-ability:**
- Dashboards build ↔ Sprint 7 toolkit work: **parallel** (different teams or interleaved by single solo dev; dashboards don't block toolkit)
- Sprint 9 run is **inherently sequential** — must wait for all prior sprints
- Within Sprint 9 run, folds parallelize across processes (8+ core local VS Code laptop per Pass 53 R7-03 fix; was 8-core Codespace; up to 4 folds simultaneously per DEC-505 4-fold; Pass 53 R7-06 fix supersedes prior DEC-109 6-fold)

## §9.5 Done criteria — verifiable acceptance

Phase 1B-α complete when ALL of these are demonstrably true:

- [ ] Cube Explorer dashboard (DEC-199) loads cube.parquet; slices on all 8 dimensions; cell detail shows constituent trades; PASS/FAIL color coding correct
- [ ] ICT/SMC Audit dashboard (DEC-200) shows FVG/BOS/CHoCH/OB primitives per ticker; manual spot-check on 5 known examples matches owner intuition
- [ ] Agent Overlay Analysis dashboard (DEC-201) shows 3-arm comparison; CI overlap visualization; budget spend
- [ ] Phase 1B-α orchestrator runs 4 folds × 199 strategies × 3 arms successfully end-to-end (Pass 53 R7-02 + R7-06 fix; was 6 folds × 119 strategies pre-DEC-505)
- [ ] Trade outcome log Parquet produced for each fold; total trades > 1000 (sanity check that strategies fired)
- [ ] cube.parquet populated; populated cell count between 20K-75K (expected range per §2.2)
- [ ] verdict.parquet has each populated cell labeled PASS / FAIL_RR / INSUFFICIENT_SAMPLE / FAIL_STAT
- [ ] PASS cell count > 0 (otherwise Stage 2 has failed; Part 13.3 path)
- [ ] ab_results.parquet has 3-arm Sharpe comparison with CIs per regime
- [ ] live_decision_lookup.parquet exported; usable as input for Stage 3 entry
- [ ] reflection_log.parquet has entries for every agent-overlay candidate
- [ ] phase_1b_alpha_summary.md generated; owner readable; covers verdict pass-rate / A/B Sharpe deltas / total cost / anomalies
- [ ] API spend documented; ≤ $300 budget per DEC-059
- [ ] Run completed within wall-time budget; if compute exceeds 60h, document why
- [ ] Owner reviews dashboards + summary; provides Stage 2 → 3 GO/NO-GO decision

## §9.6 Risks — what could go wrong specifically

**Risk R-1: Cube populates near-empty (most cells INSUFFICIENT_SAMPLE)**
- 254K-cell maximum cube; 50K-75K populated expected; but if expected misjudged, could be 5K populated with 95% INSUFFICIENT
- Mitigation: pre-Sprint-9 dry run on 1 fold to estimate populated cell count; if low, escalate (cube dim reduction further? wider universe? more strategies?)
- If discovered mid-run: continue run; report INSUFFICIENT cells at end; re-evaluate dim reduction

**Risk R-2: A/B arms produce overlapping CIs (no clear winner)**
- Block bootstrap CIs may overlap due to insufficient sample even with 3-arm reduction
- Mitigation: per-regime verdicts may be stronger than aggregate; report both
- If aggregate verdict null but per-regime PASS: full-agents justified for those regimes only

**Risk R-3: Run halts mid-fold due to compute or budget**
- 60h+ wall time exceeds owner expectation; budget exhausts before completion
- Mitigation: budget_tracker.py enforces $300 cap; if exceeded, halt with state preserved at last fold boundary
- If halt: re-evaluate cost projection; possibly upgrade cloud burst (Stage 4 cost; one-time exception)

**Risk R-4: Dashboard displays inconsistent with cube data**
- Cube populator and dashboard may interpret cell coordinates differently
- Mitigation: shared cell-coordinate library (`backtest/cube/coordinates.py`); both populator and dashboard import; integration test verifies parity

**Risk R-5: Walk-forward fold contamination (training data leaks into OOS)**
- DEC-109 specifies strict 5y train + 1y OOS; if implementation has 1-day overlap, OOS contaminated
- Mitigation: explicit fold boundary tests in Sprint 7 walk_forward.py; PIT regression suite (DEC-439) catches at CI

**Risk R-6: API rate limits on Anthropic during run**
- 1000+ propagate calls in compressed window; rate limits may throttle
- Mitigation: pre-Sprint-9 verify rate limit headroom; if needed, throttle propagate calls; if throttle inadequate, parallelize fold spawn instead of fold-internal candidate calls

**Risk R-7: Owner unavailable during multi-day run**
- 4-day wall time means owner can't immediately observe; if anomaly arises, may go unnoticed
- Mitigation: progress_monitor.py emails status updates per fold completion; budget tracker emails on threshold (50% / 75% / 90%)

**Risk R-8: Stage 2 fails — what then?**
- If verdict gate fails (Sharpe < 1.0, A/B null, or PASS cells too few), Stage 2 hasn't validated stack
- Mitigation: Part 13.3 covers Stage 2 failure paths (revisit strategy roster, reconsider universe, etc.)
- This is not a risk to mitigate — it's a possible legitimate outcome of empirical validation

## §9.7 Cost — engineering days + dollars

**Engineering effort:**
- Cube Explorer dashboard: 4-5d
- ICT/SMC Audit dashboard: 3d
- Agent Overlay Analysis dashboard: 3-4d
- Phase 1B-α orchestrator: 2d
- Fold executor + parallel runner: 2d
- Budget tracker + progress monitor: 1d
- Run smoke + actual run + post-run validation: ~6d (orchestration; compute is wall time)
- Summary generator + owner review: 1d

**Total engineering: ~22-27d (split across Sprint 7-8 dashboards + Sprint 9 run).**

**Wall-time compute cost during run:**
- 6 folds × ~6-7 hours per fold (sequential) = 36-42h
- With 6-process parallelization: ~6-8h wall time
- Plus cube populate + verdict + dashboards: ~15h
- **Total wall time: ~20-32h per DEC-505 4-fold (Pass 53 R7-06 fix; was 37-40h pre-DEC-505 6-fold)** (DEC-059 estimate)

**Dollar cost:**
- Anthropic API (TradingAgents propagate): up to $300 per DEC-059 budget
- No new subscriptions — uses Sprint 1-7 stack

**Phase 1B-α run incremental dollar cost: ≤ $300 (DEC-059 hard cap).**

## §9.8 Decisions in scope

| DEC | Title | Status |
|---|---|---|
| 059 | $300 Phase 1B-α budget hard cap | RESOLVED-DECIDED |
| 109 | Walk-forward 5y train / 1y OOS / 6 folds | RESOLVED-DECIDED |
| 131 | A/B two-gate logic | RESOLVED-DECIDED |
| 189 | Reflection log persistent decision history | RESOLVED-DECIDED |
| 199 | Cube Explorer dashboard | RESOLVED-DECIDED |
| 200 | ICT/SMC Audit dashboard | RESOLVED-DECIDED |
| 201 | Agent Overlay Analysis dashboard | RESOLVED-DECIDED |
| 269 | Phase 1B-α verdict gate (Sharpe ≥ 1.0, DD ≤ 25%, win ≥ 50%) | RESOLVED-DECIDED |
| 422 | Cube 17+ dim (revised to 8 per DEC-471) | RESOLVED-DECIDED |
| 426 | 5-Gate verdict filter | RESOLVED-DECIDED |
| 429 | Live decision lookup from PASS cells | RESOLVED-DECIDED |
| 470 PROPOSED | Hierarchical 3-level FDR | Awaits owner approval |
| 471 PROPOSED | Cube dim reduction 17+ → 8 core | Awaits owner approval |
| 472 PROPOSED | Eliminate paired A/B; bootstrap CIs | Awaits owner approval |
| 473 PROPOSED | A/B arm reduction 5 → 3 | Awaits owner approval |

## §9.9 Test approach

**Pre-run (Sprint 9 Day 1):**
- Smoke test on 1 fold × 10 candidates × 3 arms; verify orchestration end-to-end
- Cube populator small-scale: 100 trades → cube → verdict; verify cell-coordinate consistency
- Dashboard loads test cube; verify renders without errors

**During run:**
- progress_monitor.py reports per-fold completion
- budget_tracker.py logs running API spend
- Sample trades reviewed for sanity (no negative prices, no zero-day holds, no impossible PIT references)

**Post-run:**
- Acceptance: owner reviews dashboards + summary; confirms verdict pass-rate / A/B deltas / costs match expectation
- Hand-validation: pick 5 random trades from log; manually verify entry/exit/P&L against OHLCV cache + corp actions

## §9.10 Data dependencies

**Inputs:**
- Sprint 0A cache (OHLCV + reference + corp actions + earnings)
- Sprint 3 Portfolio class (per-arm instances)
- Sprint 4 financials (FMP) + smart money (Quiver/Ortex)
- Sprint 5 universe (Tier 1/2/3 with PIT correctness)
- Sprint 7 statistical methodology + custom toolkits + agent_gate + cube populator + verdict + AB
- Sprint 8 strategies (full 119-strategy roster)

**Outputs:**
- cube.parquet (the verdict cube)
- verdict.parquet (per-cell PASS/FAIL labels)
- ab_results.parquet (A/B per-regime verdicts)
- live_decision_lookup.parquet (Stage 3 entry artifact)
- reflection_log.parquet (DEC-189 historical context for Stage 3+ agent reasoning)
- phase_1b_alpha_summary.md (owner-readable)

## §9.11 Operational checklist

**Sprint 7-8 dashboards (interleaved with toolkit work):**
- [ ] DEC-199 Cube Explorer: cube_slicer + cell_detail + verdict_heatmap components
- [ ] DEC-200 ICT/SMC Audit: fvg_audit + bos_audit + ob_zone_audit components
- [ ] DEC-201 Agent Overlay Analysis: arm_comparison + regime_verdict + budget_tracker_view

**Sprint 9 run:**
- [ ] Day 1: pre-flight (all prior sprints RESOLVED-IMPLEMENTED; smoke test 1 fold)
- [ ] Day 1: pre-fund $300 API budget; verify Anthropic API rate headroom
- [ ] Day 2-5: parallel 6-fold execution; ~20-32h per DEC-505 4-fold (Pass 53 R7-06 fix; was 37-40h pre-DEC-505 6-fold) wall time
- [ ] Day 5: cube populate + verdict + AB comparison + lookup export
- [ ] Day 6: summary generation + owner dashboard review + Stage 2 → 3 decision

## §9.12 Open issues — gaps from ADVERSARIAL_AUDIT relevant to this phase

- **GAP 130 (CRITICAL):** Sample size impossible 1.4B trades vs 720K ticker-days
  - Resolution: DEC-471 PROPOSED dim reduction 17+ → 8 (this phase implements reduced cube)
- **GAP 131:** ~17% Sharpe annualized noise floor at n=30
  - Resolution: addressed by DEC-472 block bootstrap CIs (proper inference instead of point estimate)
- **GAP 132:** Walk-forward training across regime breaks
  - Resolution: 5y train per fold per DEC-109 includes regime variation; not single-regime training
- **GAP 138:** Walk-forward folds across non-stationary regimes
  - Resolution: DEC-470 hierarchical FDR per regime; per-regime verdict resilient to regime-specific failures
- **GAP 142:** Live decision lookup table format and queryability
  - Resolution: §9.1 deliverable #11 specifies Parquet format; queryable by Stage 3 lookup engine
- **GAP 144:** What if all PASS cells are in INSUFFICIENT_SAMPLE band on closer look
  - Resolution: 5-Gate is mutually exclusive (Gate 1 INSUFFICIENT supersedes others); Gate 1 must clear before Gates 2-5 applied
- **GAP 158:** A/B framework null hypothesis interpretation
  - Resolution: DEC-131 spells out two-gate logic (≥0.2 abs OR ≥0.15 rel); explicit gate avoids interpretation ambiguity

## §9.13 Decision history

- DEC-109 Pass ~30: Walk-forward methodology
- DEC-199-201 Pass ~38: Three dashboards spec
- DEC-269 Pass ~42: Phase 1B-α verdict gate
- DEC-422/426/429 Pass ~40-44: Cube dimensions / 5-Gate / live decision lookup
- DEC-470/471/472/473 Pass 52 turn 133 PROPOSED: Statistical methodology corrections per ADVERSARIAL_AUDIT findings

**Pattern:** Phase 1B-α is the most-decision-dense gate in Stage 2 because it converts validation methodology choices into verdict outputs. Pre-Pass-52 design assumed Bonferroni + paired A/B + 17+ dim cube — Pass 52 adversarial review showed math impossible at scale; PROPOSED corrections await owner approval before run execution.

## §9.14 File / module structure

(See §9.3 component diagram.)

## §9.15 Example walkthrough

**Scenario:** Phase 1B-α run completes. Owner opens Cube Explorer dashboard.

**Step 1:** Owner filters cube on `regime=volatile`, `sector=Technology`, `tier=1`. Dashboard shows:

| Strategy | Cap | Vol | Hold | SmartMoney | n | Sharpe | DD | WinRate | R:R | PSR | t-stat | FDR_q | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RSI_MR_30_70 | mega | high | medium | yes | 47 | 1.42 | -8% | 53% | 2.4 | 0.97 | 3.8 | 0.04 | **PASS** |
| RSI_MR_30_70 | mega | high | medium | no | 23 | 0.91 | -12% | 48% | 1.9 | 0.82 | 2.1 | 0.18 | INSUFFICIENT |
| RSI_MR_30_70 | large | high | medium | yes | 39 | 1.15 | -10% | 51% | 2.1 | 0.94 | 3.5 | 0.08 | **PASS** |
| ICT_FVG_Long | mega | high | medium | yes | 31 | 1.38 | -7% | 54% | 2.3 | 0.96 | 3.5 | 0.07 | **PASS** |
| ICT_FVG_Long | mega | high | medium | no | 28 | 0.84 | -11% | 49% | 1.8 | 0.78 | 2.0 | 0.22 | FAIL_RR |
| BollingerBreak | mid | high | short | yes | 18 | 1.21 | -9% | 52% | 2.2 | 0.91 | 3.1 | 0.12 | INSUFFICIENT |

**Step 2:** Owner clicks `RSI_MR_30_70 / mega / high / medium / SmartMoney_yes` PASS row. Cell-detail panel shows constituent 47 trades:

| Date | Ticker | Entry | Exit | Hold (d) | P&L | Strategy_id | Arm |
|---|---|---|---|---|---|---|---|
| 2022-06-15 | AAPL | 145.50 | 155.20 | 14 | +6.7% | RSI_MR_30_70 | full-agents |
| 2022-09-08 | MSFT | 245.10 | 261.30 | 9 | +6.6% | RSI_MR_30_70 | full-agents |
| ... 45 more | | | | | | | |

**Step 3:** Owner switches to Agent Overlay Analysis dashboard. For volatile regime:

```
Arm A (Rules-only):    Sharpe = 0.92  ± 0.18  (CI: 0.74 to 1.10)
Arm B (Full-w-veto):   Sharpe = 1.18  ± 0.16  (CI: 1.02 to 1.34)
Arm C (No-Risk):       Sharpe = 1.04  ± 0.17  (CI: 0.87 to 1.21)

Sharpe Δ (B - A) = +0.26  ✓ exceeds DEC-131 threshold ≥ 0.20 absolute
CI overlap (B vs A): minimal — B significantly better in volatile regime
```

**Verdict for volatile regime:** Full-agents-with-veto (Arm B) justified over Rules-only (Arm A).

**Step 4:** Owner switches to ICT/SMC Audit dashboard. Reviews FVG detection on AAPL 2022:
- 12 FVGs detected by smartmoneyconcepts library
- 8 filled within 30 trading days, 4 unfilled
- Hit rate 67% on bullish FVGs, 50% on bearish — passes manual sanity check

**Step 5:** Owner reviews `phase_1b_alpha_summary.md`:

```
Phase 1B-α Run Summary
======================
Run dates: 2026-08-01 to 2026-08-04 (3.2 days wall)
Folds completed: 6 / 6
Total trades: 14,872 (across all arms, all folds)
Cube cells populated: 47,213 / 254,016 (18.6%)
PASS cells: 1,847 (3.9%)
FAIL_RR: 8,201 (17.4%)
INSUFFICIENT_SAMPLE: 32,198 (68.2%)
FAIL_STAT: 4,967 (10.5%)

A/B Verdict per Regime:
  Calm:     Arm B - Arm A = +0.04 (CI overlap; null verdict)
  Neutral:  Arm B - Arm A = +0.18 (CI overlap; null verdict)
  Volatile: Arm B - Arm A = +0.26 (CI separated; B WINS) ✓
  Crisis:   Arm B - Arm A = +0.41 (CI separated; B WINS strongly) ✓

Aggregate Sharpe (Arm B): 1.07 OOS — meets DEC-269 ≥ 1.0 ✓
Aggregate Max DD (Arm B): -22% — meets DEC-269 ≤ 25% ✓
Aggregate Win Rate (Arm B): 51% — meets DEC-269 ≥ 50% ✓

Total API cost: $284 / $300 budget — under cap ✓
```

**Step 6:** Owner Stage 2 → 3 decision:
- Quantitative gates met (Sharpe / DD / win rate) ✓
- A/B verdict positive in volatile + crisis regimes (where it matters most) ✓
- Live decision lookup table has 1,847 PASS cells across diverse regimes/sectors ✓
- Cost under budget ✓
- **GO Stage 3** — owner approves with conditions: live trading uses Arm B (Full-with-veto) only in volatile/crisis regimes; Arm A (Rules-only) used in calm/neutral regimes per per-regime verdict

**Step 7:** Live decision lookup table exported with 1,847 cells; Stage 3 paper trading begins next day.

**Without Phase 1B-α:** No cube data, no verdict, no lookup table. Stage 3 has nothing to trade.

---

# PART 10 — PHASE 1C+: STRATEGY CATEGORIES EXPANSION (Sprint 8)

## §10.1 What — concrete deliverable in plain English

Phase 1C+ expands the strategy roster from the Phase 0 baseline (Layer 1 ~60 strategies) to the full Layer 1+2+3+4 roster (~199 strategies (per CANONICAL_FACTS F-002 Pass 53 + STRATEGY_ROSTER_FULL.md)) by building strategy categories that didn't exist or were stubs in earlier sprints. This includes 8 chart pattern strategies, 5 strategy categories (calendar / index-rebalance / within-category extensions), 9 exit method variants, and the AEP breaker strategy. Plus the architectural decision on BUG-111 (break-and-retest variants for existing 25 breakout strategies).

Concrete deliverables:

**8 Chart Pattern Strategies (DEC-355-362, ~12-16d):**
1. Head and Shoulders (DEC-355)
2. Inverse Head and Shoulders (DEC-356)
3. Double Top (DEC-357)
4. Double Bottom (DEC-358)
5. Ascending Triangle (DEC-359)
6. Descending Triangle (DEC-360)
7. Cup and Handle (DEC-361)
8. Rectangle Pattern (DEC-362)

Each pattern uses primitives from Phase 0.D (smartmoneyconcepts library) where applicable + standard pattern detection.

**5 Strategy Categories (DEC-367-371, ~10-15d):**
9. Calendar Effects: Turn-of-Month + Day-of-Week + Sell-in-May (DEC-367)
10. Index Rebalance Effects: S&P 500 add/delete events (DEC-368)
11. FOMC Week Patterns (DEC-369)
12. Earnings Season Pre/Post Behavior Extensions (DEC-370)
13. Sector Rotation Strategies (DEC-371)

**9 Exit Method Variants (DEC-432/433, ~6-8d — partially in Sprint 2 Phase 0.C; remaining here):**
- Chandelier exit
- PSAR (Parabolic SAR) exit
- Supertrend exit
- Volatility regime exit
- (volume_climax / rsi_extreme already in Sprint 2)
- Partial scaleout exit
- Kelly target exit
- Macro event exit
- Adaptive ATR exit

**AEP (Adverse Excursion Penalty) Breaker (DEC-435, ~3-4d):**
- Strategy that detects when MAE (Max Adverse Excursion) exceeds adaptive threshold
- Used as exit-method addition or standalone strategy

**BUG-111 Architectural Decision (Sprint 8 Day 1):**
- Option A: Shared retest primitive (~5-10d) — single break-and-retest module; existing 25 breakout strategies reference primitive
- Option B: Per-strategy variants (~25-30d) — each of 25 breakout strategies gets a paired retest variant
- **Recommendation:** Option A — shared primitive. Strategies opt-in via configuration flag. Maintains DRY principle, easier to test/maintain.
- **Owner decision required Sprint 8 Day 1**

## §10.2 Why — how this advances Stage 2 toward verdict

The verdict cube is only as good as the strategy roster that populates it. With only Layer 1 baseline (60 strategies), the cube has fewer cells populated, fewer chances to find PASS configurations, and less generalizability claim.

Specifically:
- **Chart patterns** are foundational to technical analysis; their absence from roster means cube can't test classical TA edge claims
- **Calendar effects** are well-documented anomalies (Sell-in-May, January Effect); not testing them leaves money-table un-checked
- **Index rebalance** is a specific institutional flow inefficiency; testing it shows whether owner can capture institutional inefficiency
- **9 exit method variants** give strategies more flexibility; without them, all strategies funnel through ~6 exits, reducing exit-strategy edge discovery
- **AEP breaker** is an active risk management tool; tests whether dynamic risk control improves Sharpe
- **BUG-111 retest variants** test whether retest setup adds edge over plain breakout — critical empirical question

Without Phase 1C+, Stage 2 verdict is on a 60-strategy roster, not the full 119. That's a methodologically weaker verdict.

## §10.3 How — components, data flow, dependencies

**Component diagram:**

```
backtest/strategies/
├── chart_patterns/
│   ├── head_shoulders.py         ★ NEW (DEC-355)
│   ├── inv_head_shoulders.py     ★ NEW (DEC-356)
│   ├── double_top.py             ★ NEW (DEC-357)
│   ├── double_bottom.py          ★ NEW (DEC-358)
│   ├── asc_triangle.py           ★ NEW (DEC-359)
│   ├── desc_triangle.py          ★ NEW (DEC-360)
│   ├── cup_handle.py             ★ NEW (DEC-361)
│   └── rectangle.py              ★ NEW (DEC-362)
├── calendar/
│   ├── turn_of_month.py          ★ NEW (DEC-367)
│   ├── day_of_week.py            ★ NEW (DEC-367)
│   └── sell_in_may.py            ★ NEW (DEC-367)
├── index_rebalance/
│   └── sp500_add_delete.py       ★ NEW (DEC-368)
├── fomc/
│   └── fomc_week.py              ★ NEW (DEC-369)
├── earnings/
│   └── earnings_season_extensions.py  ★ NEW (DEC-370)
├── sector_rotation/
│   └── sector_rotation.py        ★ NEW (DEC-371)
└── retest/                       ★ NEW (BUG-111 Option A)
    └── shared_retest_primitive.py

backtest/engine/exit_methods/
├── chandelier.py                 ★ NEW (DEC-433)
├── psar.py                       ★ NEW (DEC-433)
├── supertrend.py                 ★ NEW (DEC-433)
├── volatility_regime.py          ★ NEW (DEC-433)
├── partial_scaleout.py           ★ NEW (DEC-433)
├── kelly_target.py               ★ NEW (DEC-433)
├── macro_event.py                ★ NEW (DEC-433)
└── adaptive_atr.py               ★ NEW (DEC-433)

backtest/strategies/aep/
└── aep_breaker.py                ★ NEW (DEC-435)
```

**Data flow:**

Each new strategy follows existing strategy interface:
- Implements `compute_signal(ticker, as_of_date) → (entry_signal, exit_signal, tier)`
- Reads OHLCV via Sprint 1 PriceLoader
- Reads PIT-correct earnings dates via DEC-256 cache (for earnings strategies)
- Reads FRED data via Sprint 1 FRED cache (for macro/calendar strategies)
- Reads SMC primitives via Phase 0.D cache (for chart patterns where applicable)
- Each strategy has unique `strategy_id` per STRATEGY_REGISTER for cube cell coordinates

**Dependencies:**
- Sprint 1 OHLCV cache (all strategies)
- Sprint 1 reference data (sector rotation needs sector classification)
- Sprint 1 FRED cache (calendar / macro / sector rotation)
- Sprint 1 polygon_earnings cache (earnings extensions)
- Phase 0.D smartmoneyconcepts (chart patterns may reference SMC primitives)
- Sprint 5 universe management (index rebalance needs PIT membership history)

## §10.4 When — sequence

**Sequence within Sprint 8 (~37-55d total):**

| Week | Focus |
|---|---|
| Week 1 Day 1 | BUG-111 architectural decision: Option A vs B (owner approval) |
| Week 1-2 | Chart patterns 1-4: head/shoulders + inv-h/s + double top/bottom |
| Week 2-3 | Chart patterns 5-8: triangles + cup/handle + rectangle |
| Week 3 | BUG-111 Option A implementation: shared retest primitive |
| Week 4 | Calendar strategies (DEC-367) |
| Week 4-5 | Index rebalance (DEC-368) + FOMC (DEC-369) |
| Week 5 | Earnings extensions (DEC-370) + Sector rotation (DEC-371) |
| Week 6 | Exit method variants (8 implementations) |
| Week 7 | AEP breaker (DEC-435) |
| Week 7-8 | Integration tests + STRATEGY_REGISTER update + PR review |

**Total: ~37-55d realistic.**

**Blockers:**
- Phase 0.D smartmoneyconcepts library forked Sprint 1
- Sprint 5 PIT membership history (for index rebalance strategy)
- Sprint 1 polygon_earnings cache (for earnings extensions)
- BUG-111 owner decision Day 1

**Parallel-ability:**
- Sprint 8 ↔ Sprint 7: **partial parallel** — Sprint 8 strategy work doesn't block Sprint 7 toolkit work; both can proceed
- Sprint 8 ↔ Sprint 6 (catch-mechanism): Sprint 8 benefits from Sprint 6 layers as they land

## §10.5 Done criteria

- [ ] BUG-111 owner decision documented; if Option A, shared primitive implemented and 25 breakout strategies opt-in
- [ ] 8 chart pattern strategies implemented with strategy_id in STRATEGY_REGISTER
- [ ] Each chart pattern fires correctly on Tier 1 universe (verified by Phase 1B-α small-scale dry run)
- [ ] 5 strategy categories (calendar / index / FOMC / earnings / sector rotation) implemented
- [ ] 8 exit method variants implemented; available in engine for strategy reference
- [ ] AEP breaker implemented; tested as both exit and standalone strategy
- [ ] Total strategy roster reaches 109-119 (Layer 1+2+3+4 complete)
- [ ] STRATEGY_REGISTER updated with all new strategies
- [ ] Unit tests for each strategy
- [ ] Integration test: each strategy fires at least once on 1-fold dry run
- [ ] Sprint 8 PR merged; CI green

## §10.6 Risks

**Risk R-1: Chart pattern detection false positive rate**
- Pattern detection is approximate; subjective; library/algo may differ from human intuition
- Mitigation: owner spot-check 5 known examples per pattern; document false positive thresholds

**Risk R-2: Calendar effects may have decayed**
- Sell-in-May, Turn-of-Month — well-known anomalies that may be arbitraged away
- Mitigation: cube tests this empirically — if effect decayed, FAIL_STAT verdict; this is the correct outcome of empirical validation, not a bug

**Risk R-3: Index rebalance requires reliable PIT membership data**
- DEC-303 + DEC-477 `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` — must include effective dates for adds/deletes
- Mitigation: Sprint 5 universe management ensures PIT correctness; Phase 1C+ depends on Sprint 5

**Risk R-4: BUG-111 Option A shared primitive too generic**
- Single primitive may not capture nuances of all 25 breakout strategies
- Mitigation: configurable retest parameters per strategy; primitive is template, strategies parameterize

**Risk R-5: Exit method proliferation cascades testing burden**
- 17 total exit methods × dozens of strategies × test combinations → enormous test surface
- Mitigation: integration tests cover exit methods individually; combinatorial tests sampled, not exhaustive

**Risk R-6: AEP breaker tuning sensitivity**
- Adaptive threshold for MAE — wrong tuning makes breaker too tight (over-exits) or too loose (no value)
- Mitigation: cube tests AEP breaker presence/absence as a cell dimension (effectively); empirical verdict per regime

## §10.7 Cost

**Engineering effort:** ~37-55d realistic
**Subscription cost:** $0 incremental

## §10.8 Decisions in scope

| DEC | Title | Status |
|---|---|---|
| 067 | 17 exit methods canonical | RESOLVED-DECIDED |
| 075 | Exit method classification | RESOLVED-DECIDED |
| 355 | Head and Shoulders strategy | RESOLVED-DECIDED |
| 356 | Inverse H&S strategy | RESOLVED-DECIDED |
| 357 | Double Top strategy | RESOLVED-DECIDED |
| 358 | Double Bottom strategy | RESOLVED-DECIDED |
| 359 | Ascending Triangle strategy | RESOLVED-DECIDED |
| 360 | Descending Triangle strategy | RESOLVED-DECIDED |
| 361 | Cup and Handle strategy | RESOLVED-DECIDED |
| 362 | Rectangle pattern strategy | RESOLVED-DECIDED |
| 367 | Calendar effects category | RESOLVED-DECIDED |
| 368 | Index rebalance category | RESOLVED-DECIDED |
| 369 | FOMC week patterns | RESOLVED-DECIDED |
| 370 | Earnings season extensions | RESOLVED-DECIDED |
| 371 | Sector rotation category | RESOLVED-DECIDED |
| 432 | Exit method variants additive | RESOLVED-DECIDED |
| 433 | New exit method variants enumerated | RESOLVED-DECIDED |
| 435 | AEP breaker strategy | RESOLVED-DECIDED |
| BUG-111 | Break-and-retest architecture | OPEN — Sprint 8 Day 1 owner decision |

## §10.9 Test approach

- Per-strategy unit tests: each strategy compute_signal verified against known scenarios
- Strategy integration test: 1-fold dry run; verify each strategy fires at least once
- Chart pattern accuracy test: 5 owner-curated examples per pattern verified
- Exit method variant tests: each variant exercised on a representative held position
- BUG-111 Option A test: shared primitive with 3 different breakout strategy configs verifies retest logic

## §10.10 Data dependencies

**Inputs:**
- Sprint 1 OHLCV + reference + earnings + FRED
- Phase 0.D smartmoneyconcepts (for chart patterns where applicable)
- Sprint 5 PIT universe membership (for index rebalance)

**Outputs:**
- Full 119-strategy roster ready for Phase 1B-α run
- STRATEGY_REGISTER updated

## §10.11 Operational checklist

(See §10.4 week-by-week.)

## §10.12 Open issues — gaps from ADVERSARIAL_AUDIT

- **GAP 87:** BUG-111 deferred decision
  - Resolution: §10.1 deliverable — Sprint 8 Day 1 explicit owner decision; Option A recommended
- **GAP 88:** 8 chart patterns incomplete spec — entry/exit/sizing rules
  - Resolution: each strategy spec covers entry triggers, exit conditions, tier sizing in `backtest/strategies/chart_patterns/{name}.py` docstring
- **GAP 89:** Calendar strategies — overlap with regime-conditional behavior
  - Resolution: calendar strategies are independent strategy_ids in roster; cube cell coordinates capture overlap empirically
- **GAP 90:** Index rebalance — Russell 1000 inclusion (B9 from blockers)
  - Resolution: DEC-477 `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` canonical for S&P 500; Russell 1000 add deferred to Stage 3+ if needed
- **GAP 91:** Exit method variants — interaction with circuit breakers
  - Resolution: exit methods + circuit breakers are layered; circuit breakers operate at portfolio level (per Sprint 2 Phase 0.C); exit methods at trade level; orthogonal

## §10.13 Decision history

- DEC-355-362 Pass ~44 — 8 chart patterns enumerated
- DEC-367-371 Pass ~46 — 5 strategy categories
- DEC-432/433 Pass ~48 — 9 exit method variants
- DEC-435 Pass ~48 — AEP breaker
- BUG-111 OPEN since Pass ~30 — break-and-retest deferred multiple times; Sprint 8 Day 1 forces decision

## §10.14 File / module structure

(See §10.3 component diagram.)

## §10.15 Example walkthrough

**Scenario:** New strategy `Cup_and_Handle_Long` (DEC-361) fires on NVDA 2023-04-10.

**Step 1:** Strategy reads OHLCV via Sprint 1 PriceLoader (200 days lookback).

**Step 2:** Pattern detection logic identifies cup formation (rounding bottom 2022-12 to 2023-03) followed by handle (sideways consolidation 2023-03 to 2023-04). Breakout candidate.

**Step 3:** Strategy_id = `Cup_and_Handle_Long`; tier = MEDIUM (preliminary, before agent overlay).

**Step 4:** Entry signal: NVDA close 2023-04-10 > resistance line by 2% with above-avg volume. ENTRY at $260 close.

**Step 5:** Exit method: Cup-and-handle strategies use `chandelier` exit (DEC-433 new variant Phase 1C+). Chandelier 3×ATR below high.

**Step 6:** Position held; chandelier exit on 2023-05-22 at $290 (high was $310; ATR-based stop hit).

**Step 7:** Trade outcome cube cell: `(Cup_and_Handle_Long, neutral_regime, Tech, mega, medium_vol, medium_hold, T1, smart_money_signal_yes)` populated.

**Step 8:** Phase 1B-α aggregate: 28 Cup-and-Handle trades across cube. Cell verdict: 28 < 30 → INSUFFICIENT_SAMPLE → Cup-and-Handle excluded from live decision lookup until more trades observed.

**Step 9:** Owner reviews: pattern is real but rare; INSUFFICIENT verdict is correct empirical outcome; revisit after Stage 3 paper trading accumulates more samples.

**Without Phase 1C+:** Cup-and-Handle strategy doesn't exist in roster; cube has no Cup-and-Handle cells; classical TA pattern trading family entirely missing from verdict.

---

# PART 11 — SPRINT 4: DEC-410 API AUDIT FINDINGS

## §11.1 What — concrete deliverable in plain English

Sprint 4 closes 17 sub-decisions from the DEC-410 API audit (Pass ~40). The audit reviewed 17 external APIs/data sources used or considered by the project; produced 17 sub-decisions covering deprecations, additions, scope expansions, and replacements. Sprint 4 implements the changes.

This sprint runs **parallel to Sprints 3 and 5** because all changes are in `backtest/data/` layer; orthogonal to engine (Sprint 2), Portfolio class (Sprint 3), or universe management (Sprint 5).

Concrete deliverables (17 sub-decisions):

**Deprecations / Removals:**
1. **DEC-442** — yfinance demoted to fallback only; primary path replaced by Polygon (resolves BUG-218 .info CURRENT-not-as_of issue)
2. **DEC-453** — Finnhub deprecated and removed from production code paths (replaced by Polygon news per DEC-440 + Quiver paid)
3. **DEC-454** — OpenBB deprecated (was investigation target; not adopted)
4. **DEC-455** — Alpha Vantage demoted (Stage 1 legacy); Polygon replaces

**Replacements (yfinance → Polygon):**
5. **DEC-443** — yfinance.info → Polygon Reference Data (sector/cap/exchange/listing)
6. **DEC-444** — yfinance earnings → Polygon earnings cache (DEC-256 already established)
7. **DEC-445** — yfinance dividends → Polygon corp actions (Sprint 1 already covers)
8. **DEC-446** — yfinance splits → Polygon corp actions (Sprint 1 already covers)

**Quiver paid expansion:**
9. **DEC-447** — Quiver paid endpoints scoped: insider trading (Form 4+144), congressional disclosures (House+Senate), 13F institutional, analyst rating changes, government contracts
10. **DEC-450** — Quiver gov_contracts date filter: filings within trading window
11. **DEC-451** — Quiver paid endpoints prefetch strategy: bulk download monthly + delta updates daily

**FRED expansion:**
12. **DEC-448** — FRED 9+ series confirmed (already in Sprint 1; Sprint 4 closes audit)
13. **DEC-449** — ALFRED PIT-vintage validation across 3+ key series

**Polygon expansion:**
14. **DEC-441 verification** — Polygon Stocks Starter $29/mo (corrected to $29 per DEC-479)
15. **DEC-456** — Polygon news endpoint integration: ticker-tagged news with timestamp filtering

**FMP integration (NEW Pass 52 turn 130):**
16. **DEC-461** — FMP subscription mandatory (per Pass 52 turn 133 verification of DEC-460 negative): PIT financials + earnings transcripts + analyst consensus
17. **(Bundled)** — FMP API client + cache layer (similar pattern to Polygon client from Sprint 1)

## §11.2 Why — how this advances Stage 2 toward verdict

DEC-410 audit was an architectural cleanup: **eliminate technical debt from API choices** that Stage 1 made under different constraints, replace with appropriate Stage 2 choices.

Specifically:
- **yfinance demotion eliminates BUG-218** (info returns CURRENT not as_of) — this bug, if not fixed, contaminates every backtest with current-state data leaking back in time
- **Quiver paid expansion** is what enables smart money composite (DEC-332) and DEC-124 cross-source confluence — without paid Quiver, smart money signals are incomplete
- **FMP integration** is mandatory per Pass 52 turn 133 verification of DEC-460 negative — without FMP, OurFundamentalsToolkit (Sprint 7 DEC-463) operates degraded
- **Polygon news** (DEC-456) gives OurNewsToolkit (DEC-464) primary news source
- **FRED ALFRED validation** (DEC-449) ensures macro signals don't have PIT contamination

Sprint 4 is the cleanup that ensures Sprint 7 toolkit work has correct underlying data.

## §11.3 How — components, data flow, dependencies

**Component diagram:**

```
backtest/data/
├── _legacy/                          # ⊠ deprecated locations
│   ├── yfinance_info.py             # ⊠ DEC-443
│   ├── yfinance_earnings.py         # ⊠ DEC-444
│   ├── yfinance_dividends.py        # ⊠ DEC-445
│   ├── yfinance_splits.py           # ⊠ DEC-446
│   ├── finnhub_client.py            # ⊠ DEC-453
│   ├── openbb_client.py             # ⊠ DEC-454
│   └── alpha_vantage_client.py      # ⊠ DEC-455 (Stage 1 fetch_stocks.py keeps separately)
├── polygon_client.py                # ⊠ EXTENDED (DEC-456 news endpoint)
├── polygon_news.py                  # ★ NEW (DEC-456)
├── quiver/
│   ├── quiver_client.py              # ★ NEW (DEC-447)
│   ├── quiver_insider.py             # ★ NEW (Form 4+144)
│   ├── quiver_congressional.py      # ★ NEW (House + Senate)
│   ├── quiver_13f.py                 # ★ NEW (institutional)
│   ├── quiver_analyst_changes.py    # ★ NEW (analyst rating changes)
│   ├── quiver_gov_contracts.py      # ★ NEW (DEC-450 date filter)
│   └── quiver_prefetch.py           # ★ NEW (DEC-451 bulk + delta)
├── fmp/
│   ├── fmp_client.py                # ★ NEW (DEC-461)
│   ├── fmp_financials.py            # ★ NEW (PIT financials)
│   ├── fmp_transcripts.py           # ★ NEW (earnings transcripts)
│   └── fmp_estimates.py             # ★ NEW (analyst consensus)
└── fred/
    └── alfred_validation.py         # ★ NEW (DEC-449 PIT vintage check)
```

**Data flow (typical use):**

```
Strategy / Toolkit / Agent
        │
        ▼
data/quiver/quiver_insider.fetch(ticker, as_of_date)
        │
        ▼ checks cache
        │
        ├── HIT → return PIT-sliced rows
        │
        └── MISS → quiver_client.get_insider_transactions(ticker, from, to)
                    │
                    ▼ writes to Parquet cache
                    │
                    └── return PIT slice
```

Same pattern for Polygon news / FMP / FRED ALFRED.

**Dependencies:**
- Sprint 1 PointInTimeLoader base class — all new fetchers extend
- Sprint 0A cache hygiene (filelock + disk monitor + LRU)
- Sprint 1 Polygon client — DEC-456 extends with news endpoint
- Owner subscriptions: Quiver paid + FMP + (Polygon tier per DEC-478)

**Library dependencies:**
- `requests` (already in project)
- New: `quiverquant` Python SDK if owner prefers; otherwise raw REST via requests

## §11.4 When — sequence

**Sequence within Sprint 4 (~41.75-54.25d):**

| Week | Focus |
|---|---|
| Week 1 | yfinance demotion (DEC-442/443/444/445/446) — 5 deprecations + Polygon replacement wiring |
| Week 2 | Finnhub/OpenBB/Alpha Vantage cleanup (DEC-453/454/455) |
| Week 2-3 | Quiver paid client + 5 endpoint integrations (DEC-447/450) |
| Week 3-4 | Quiver prefetch + delta update strategy (DEC-451) |
| Week 5 | FRED ALFRED PIT validation (DEC-448/449) |
| Week 5-6 | Polygon news endpoint (DEC-456) |
| Week 7-8 | FMP client + financials + transcripts + estimates (DEC-461) |
| Week 8 | Integration tests + deprecation warnings + PR review |

**Total: ~41.75-54.25d realistic.**

**Parallel-ability:**
- Sprint 4 ↔ Sprint 1 second half: parallel (Sprint 1 schema lock Day 5 enables Sprint 4 cache integration)
- Sprint 4 ↔ Sprint 3: parallel (Sprint 3 in `portfolio/`; Sprint 4 in `data/`)
- Sprint 4 ↔ Sprint 5: parallel (Sprint 5 builds universes; Sprint 4 fixes data sources)

**Blockers:**
- Sprint 1 PointInTimeLoader available
- Owner subscriptions (Quiver paid + FMP) active
- DEC-461 FMP approval

## §11.5 Done criteria

- [ ] yfinance imports removed from production code paths (lint enforced; only in `_legacy/`)
- [ ] BUG-218 (.info CURRENT-not-as_of) verified resolved by Polygon reference replacement
- [ ] Finnhub / OpenBB / Alpha Vantage references removed from production
- [ ] Quiver paid client operational; 5 endpoints (insider/congressional/13F/analyst/gov contracts) cached
- [ ] DEC-450 gov_contracts date filter verified working
- [ ] DEC-451 Quiver prefetch + delta strategy operational; monthly bulk + daily delta updates committed via GitHub Actions
- [ ] FRED ALFRED PIT vintage validated for 3+ key series
- [ ] Polygon news endpoint cached; ticker-tagged search works
- [ ] FMP client operational; PIT financials + earnings transcripts + analyst consensus cached
- [ ] All 17 DEC-410 sub-decisions RESOLVED-IMPLEMENTED
- [ ] Integration test: typical Sprint 7 toolkit call sequence runs against Sprint 4 data layer end-to-end
- [ ] Sprint 4 PR merged; CI green

## §11.6 Risks

**Risk R-1: Quiver paid API behavior unverified**
- Quiver subscription may have different rate limits / data freshness than expected
- Mitigation: Day 1 smoke test on each endpoint; document gotchas

**Risk R-2: FMP earnings transcript coverage gaps**
- FMP may not have transcripts for all S&P 500 tickers (smaller-caps may be partial)
- Mitigation: integration test maps coverage; document limitations

**Risk R-3: yfinance silent fallback**
- After demotion, code may still import yfinance via transitive dependency; if Polygon fails, code might fall back silently
- Mitigation: lint rule prohibits yfinance import in production paths; CI fails build if introduced

**Risk R-4: Polygon news quality**
- News quality varies; may have promotional/spam content tagged to tickers
- Mitigation: filter by news source / publisher reputation; document filtering

**Risk R-5: Bulk prefetch consumes disk**
- Quiver paid 5-endpoint × full S&P 500 historical = potentially 10-30 GB additional cache
- Mitigation: Sprint 1 disk monitoring covers; LRU eviction respects prefetch lock

**Risk R-6: ALFRED API changes**
- FRED's ALFRED endpoint stable but rate-limited; vintage validation may take many calls
- Mitigation: validate 3 series only in Sprint 4; document any quirks; full validation deferred to Sprint 7 if needed

## §11.7 Cost

**Engineering effort:** ~41.75-54.25d
**Subscription cost (incremental for Sprint 4):**
- Quiver paid: ~$50-100/mo (already planned)
- FMP: $14-50/mo (DEC-461)
- Polygon: covered by Sprint 1 base subscription
- FRED/ALFRED: free

**Sprint 4 incremental subscriptions: $64-150/mo.**

## §11.8 Decisions in scope

| DEC | Title |
|---|---|
| 441 | Polygon $30/mo (corrected to $29 per DEC-479) |
| 442 | yfinance demoted |
| 443 | yfinance.info → Polygon reference |
| 444 | yfinance earnings → Polygon earnings |
| 445 | yfinance dividends → Polygon corp actions |
| 446 | yfinance splits → Polygon corp actions |
| 447 | Quiver paid endpoints scope |
| 448 | FRED 9+ series |
| 449 | ALFRED PIT vintage validation |
| 450 | Quiver gov_contracts date filter |
| 451 | Quiver paid prefetch strategy |
| 453 | Finnhub deprecated |
| 454 | OpenBB deprecated |
| 455 | Alpha Vantage demoted |
| 456 | Polygon news endpoint |
| 461 | FMP subscription mandatory |
| 479 PROPOSED | DEC-441 cost correction $30→$29 |

## §11.9 Test approach

- Per-source smoke tests (Day 1 of each endpoint integration)
- yfinance import lint rule (CI enforced)
- BUG-218 regression test (Polygon reference returns as_of-correct sector for known historical change)
- Quiver paid integration tests (5 endpoints × sample ticker)
- FMP integration tests (financials + transcripts + estimates × sample ticker)
- ALFRED vintage test (3 key series; verify vintage release date matches as_of slicing)

## §11.10 Data dependencies

**Inputs:**
- Sprint 0A cache infrastructure
- Owner subscriptions (Quiver paid + FMP)

**Outputs:**
- Clean data layer for Sprint 7 toolkit consumption
- All 17 DEC-410 sub-decisions closed

## §11.11 Operational checklist

(See §11.4 week-by-week.)

## §11.12 Open issues — gaps from ADVERSARIAL_AUDIT

- **GAP 65:** DEC-410 17-API audit findings — only 4 named in PROJECT_PLAN
  - Resolution: §11.1 enumerates all 17 sub-decisions
- **GAP 67:** Quiver paid endpoints rate limits not documented
  - Resolution: §11.4 Day 1 smoke test verifies; §11.6 R-1 mitigation budgets time
- **GAP 68:** FMP earnings transcript coverage
  - Resolution: §11.6 R-2 mitigation; document in LIMITATIONS_CAVEATS_ASSUMPTIONS

## §11.13 Decision history

- DEC-410 audit Pass ~40 — 17-API review produced 17 sub-decisions
- DEC-441-456 Pass ~40-44 — sub-decisions logged
- DEC-461 Pass 52 turn 130 — FMP added per TradingAgents data audit
- DEC-460 Pass 52 turn 130 — Polygon Starter PIT verification (RESULT: NEGATIVE Pass 52 turn 133)
- DEC-479 Pass 52 turn 133 — $30→$29 cost correction

## §11.14 File / module structure

(See §11.3 component diagram.)

## §11.15 Example walkthrough

**Scenario:** Sprint 7 OurFundamentalsToolkit method `get_recent_financials(ticker, as_of)` is called for AAPL 2022-06-15.

**Before Sprint 4 (without DEC-461 FMP):**
```python
financials = yfinance.Ticker('AAPL').financials  # CURRENT financials, no as_of
# BUG-218: lookahead bias — 2024 financials returned for 2022-06-15 query
```

**After Sprint 4 (with DEC-461 FMP):**
```python
financials = fmp_financials.fetch('AAPL', as_of='2022-06-15')
# Returns 2022-Q1 10-Q (last filed before as_of); strict PIT
# No BUG-218 contamination
```

**Difference:** Without Sprint 4, agent reasoning uses lookahead-contaminated fundamentals; verdict invalid. With Sprint 4, fundamentals are PIT-correct.

---

# PART 12 — SPRINT 5: UNIVERSE MANAGEMENT

## §12.1 What — concrete deliverable in plain English

Sprint 5 builds the **3-tier universe management system** that defines what tickers are eligible for trading on any historical or live date. Each tier has its own build pipeline, refresh cadence, and PIT correctness guarantees.

This sprint runs **parallel to Sprints 3 and 4** because universe is its own concern (not engine, not portfolio, not data fetching).

Concrete deliverables:

**Tier 1 — S&P 500 + ETFs (~3-4d):**
1. **`Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` canonical** (DEC-303 + DEC-477) — PIT-correct S&P 500 membership history with effective_date for adds/deletes; sourced from SEC 10-K filings + Wayback Machine archive of Wikipedia
2. **Tier 1 build function** — `backtest/universe/tier_1.py` produces eligible ticker list for any as_of date
3. **Selected ETFs append** — VIX/DXY/GLD/oil/sector ETFs/TLT/HYG/SHY per DEC-118
4. **Liquidity floor enforcement** — $10M ADV per DEC-366 (fail-closed; no trades on illiquid Tier 1 tickers)
5. **Russell 1000 add reconciliation per ADVERSARIAL GAP B9** — explicit decision: S&P 500 only for Tier 1; Russell 1000 deferred to Stage 3+ if needed

**Tier 2 — Spinoffs / IPOs (~5-6d):**
6. **SEC EDGAR Form 10-12B scrape (DEC-378-380)** — `.github/workflows/refresh_spinoffs.yml` cron job; scrapes Form 10-12B filings for spinoff parent + child information; outputs to Parquet
7. **IPO universe build (DEC-103/373/374)** — recent IPOs filtered by ≥$2B cap minimum + 20-day-min history per DEC-103
8. **Tier 2 build function** — `backtest/universe/tier_2.py` produces spinoff + IPO list for any as_of date
9. **`LIMITED_HISTORY` flag** — strategies that need >20 days history skip Tier 2 tickers below threshold

**Tier 3 — Momentum Top-100 (~3-4d):**
10. **Momentum screen (DEC-104/375/376/377)** — top 100 momentum-screen tickers refreshed monthly via `.github/workflows/refresh_momentum_watchlist.yml`
11. **Tier 3 build function** — `backtest/universe/tier_3.py` produces momentum watchlist for any as_of date
12. **Liquidity / cap floors** — $5M ADV / $300M cap minimum

**Universe orchestrator (~2-3d):**
13. **`backtest/universe/builder.py`** — top-level universe builder; combines Tier 1+2+3; produces single eligible ticker list per as_of with tier flags
14. **Universe cache** — Parquet cache `data/universe/built/{as_of}.parquet`; rebuilt monthly; regenerated on demand

## §12.2 Why — how this advances Stage 2 toward verdict

The universe is **what trades.** Without correct universe management:

- **Survivorship bias** — if Tier 1 uses CURRENT S&P 500 (not historical), backtest only includes companies that survived to today; failed companies absent → returns artificially inflated
- **Tier 2/3 absent** — strategies that target spinoffs/IPOs/momentum have no candidate pool → those strategies can't fire → cube cells empty → verdict missing those signal classes
- **Liquidity floor missing** — strategies fire on illiquid micro-caps; backtest fills assume liquid prices; live trading fails to fill → backtest invalid for live deployment
- **Russell 1000 ambiguity (B9 blocker)** — TRADING_RULES inconsistent on whether universe is S&P 500 or R1000; cube cells inconsistent across documents
- **`LIMITED_HISTORY` flag missing** — strategies needing 250-day history applied to 30-day-old IPOs → garbage signals in cube

Sprint 5 ensures universe is well-defined, PIT-correct, and tier-stratified for the cube.

## §12.3 How — components, data flow, dependencies

**Component diagram:**

```
backtest/universe/
├── __init__.py
├── builder.py                       ★ NEW (top-level orchestrator)
├── tier_1.py                        ★ NEW (S&P 500 + ETFs)
├── tier_2.py                        ★ NEW (spinoffs + IPOs)
├── tier_3.py                        ★ NEW (momentum top-100)
├── liquidity_floor.py               ★ NEW (DEC-366 ADV check)
├── limited_history.py               ★ NEW (LIMITED_HISTORY flag)
└── universe_cache.py                ★ NEW (Parquet cache)

data/
├── universe/
│   ├── Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv    ★ canonical (DEC-303 + DEC-477)
│   ├── selected_etfs.csv             # Curated list (DEC-118)
│   ├── spinoffs/
│   │   └── spinoffs.parquet         # SEC EDGAR scrape output
│   ├── ipos/
│   │   └── ipos.parquet              # IPO universe per DEC-103
│   ├── momentum_top100/
│   │   └── {YYYY-MM}.parquet         # Monthly snapshots
│   └── built/
│       └── {as_of}.parquet           # Built universes (cached)

.github/workflows/
├── refresh_spinoffs.yml             ★ NEW (SEC EDGAR scrape weekly)
├── refresh_ipos.yml                  ★ NEW (IPO universe weekly)
└── refresh_momentum_watchlist.yml   ★ NEW (Monthly top-100)
```

**Data flow (typical use during backtest):**

```
Backtest engine starts day 2022-06-15
        │
        ▼
universe_builder.build(as_of='2022-06-15')
        │
        ▼ checks universe cache for that date
        │
        ├── HIT → return cached eligible ticker list
        │
        └── MISS → 
                tier_1.build('2022-06-15')  # 482-509 S&P 500 members + ETFs PIT
                  ├── reads Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv
                  ├── filters to active members on as_of
                  ├── appends selected_etfs.csv
                  └── applies liquidity_floor (ADV >= $10M)
                        │
                tier_2.build('2022-06-15')  # spinoffs + IPOs
                  ├── reads spinoffs.parquet (filtered to last 365 days from as_of)
                  ├── reads ipos.parquet (filtered to last 365 days, >= $2B cap, >= 20 days history)
                  └── applies liquidity_floor (ADV >= $5M)
                        │
                tier_3.build('2022-06-15')  # momentum
                  ├── reads momentum_top100/{2022-06}.parquet (monthly snapshot)
                  └── applies liquidity_floor (ADV >= $5M, cap >= $300M)
                        │
                combines all tiers; assigns tier flag per ticker
                writes built/2022-06-15.parquet
                returns eligible ticker list
        │
        ▼
Engine iterates eligible tickers; runs strategies
```

**Dependencies:**
- Sprint 1 OHLCV (for ADV computation)
- Sprint 1 reference data (for cap + sector classification)
- SEC EDGAR access (local VS Code — no allowlist needed per Pass 53 R7-03 fix; was Codespace allowlist verified)
- Wayback Machine access (for Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv backfill if needed)

**Library dependencies:**
- `requests` (SEC EDGAR scrape)
- `lxml` / `beautifulsoup4` (HTML parsing for SEC forms)
- `pandas` (Parquet IO)

## §12.4 When — sequence

**Sequence within Sprint 5 (~13.5-15.5d):**

| Day | Task |
|---|---|
| 1 | DEC-477 owner approval; canonicalize Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv |
| 1-2 | Tier 1 build function + selected ETFs + liquidity floor |
| 3-4 | Tier 1 testing across 6 OOS folds; PIT verification |
| 5-6 | SEC EDGAR Form 10-12B scrape; spinoffs.parquet output |
| 6-7 | IPO universe build with DEC-103 filters; ipos.parquet |
| 7-8 | Tier 2 build function + LIMITED_HISTORY flag |
| 9 | Momentum screen logic; refresh_momentum_watchlist.yml workflow |
| 10 | Tier 3 build function |
| 11 | universe_builder.py orchestrator |
| 12 | universe_cache.py + Parquet integration |
| 13-14 | Integration tests + workflow tests + acceptance demo |
| 15 | PR review + merge |

**Total: ~13.5-15.5d realistic.**

**Parallel-ability:**
- Sprint 5 ↔ Sprint 3: parallel (Portfolio class doesn't need universe)
- Sprint 5 ↔ Sprint 4: parallel (data layer fixes orthogonal to universe)
- Sprint 5 ↔ Sprint 1 second half: sequential dependency on Sprint 1 OHLCV cache

**Blockers:**
- Sprint 1 OHLCV cache available (for ADV computation)
- DEC-477 owner approval
- SEC EDGAR access verified on local VS Code (Pass 53 R7-03 fix; was Codespace network allowlist; no allowlist required for local VS Code)

## §12.5 Done criteria

- [ ] Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv canonical; static 482-CSV deprecated with warning
- [ ] Tier 1 build returns 482-509 tickers for any as_of date in backtest range
- [ ] Tier 1 PIT verification: 2010-as_of returns 2010 members, not 2024 members
- [ ] Selected ETFs appended per DEC-118
- [ ] Liquidity floor enforced; tickers below ADV floor excluded with logging
- [ ] SEC EDGAR scrape running successfully in GitHub Actions; spinoffs.parquet updated weekly
- [ ] IPO universe built per DEC-103 ($2B cap + 20-day history); ipos.parquet weekly
- [ ] LIMITED_HISTORY flag set for tickers with <20 days history; strategies respect flag
- [ ] Momentum top-100 refresh running monthly; output committed
- [ ] Tier 2 + Tier 3 build functions return correct lists for sample dates
- [ ] universe_builder.build(as_of) returns combined Tier 1+2+3 list with tier flags
- [ ] Universe cache Parquet works; rebuild on demand
- [ ] Russell 1000 explicitly NOT in Tier 1 — documented in TRADING_RULES + LIMITATIONS_CAVEATS
- [ ] Sprint 5 PR merged; CI green

## §12.6 Risks

**Risk R-1: SEC EDGAR allowlist or rate limiting**
- SEC EDGAR has rate limits (local VS Code per Pass 53 R7-03 fix; prior Codespace allowlist constraints moot)
- Mitigation: Day 5 verify allowlist; if blocked, scrape locally on Windows + commit Parquet (manual refresh fallback)

**Risk R-2: Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv backfill incomplete**
- Wayback Machine has gaps; some adds/deletes may be missing
- Mitigation: cross-reference with Bloomberg / WSJ archive; document any gaps in LIMITATIONS_CAVEATS

**Risk R-3: Spinoff identification ambiguity**
- Spinoff vs IPO vs split — Form 10-12B specifically signals spinoff but parsing may produce false positives
- Mitigation: validation step compares scrape output to known spinoffs (Kraft Foods → Mondelez, Hewlett Packard → HPE, etc.)

**Risk R-4: Momentum screen lookahead bias**
- Monthly refresh — if refresh script uses as_of_date but query window includes dates after as_of, lookahead leaks
- Mitigation: explicit as_of parameter in screen function; PIT regression test (Sprint 6 layer 5)

**Risk R-5: Russell 1000 reconciliation post-decision**
- If owner later decides to add R1000, Sprint 5 deliverable is partially obsolete
- Mitigation: document explicit S&P 500 only decision in TRADING_RULES; add R1000 as Stage 3+ enhancement if backtest results justify

**Risk R-6: Liquidity floor wrong for TQQQ-style leveraged ETFs**
- Selected ETFs (VIX/DXY/etc.) may have different liquidity profiles than expected
- Mitigation: ETF-specific liquidity overrides in selected_etfs.csv if needed

## §12.7 Cost

**Engineering effort:** ~13.5-15.5d
**Subscription cost:** $0 (SEC EDGAR free; Wayback free)

## §12.8 Decisions in scope

| DEC | Title |
|---|---|
| 103 | IPO universe ≥$2B + 20-day-min history |
| 104 | Momentum top-100 watchlist monthly |
| 118 | Selected ETFs in Tier 1 |
| 303 | Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv canonical |
| 366 | Liquidity floor ADV-based |
| 373 | IPO age window 365 days from as_of |
| 374 | IPO universe excludes <20 day history |
| 375 | Momentum screen criteria (12-1 momentum standard) |
| 376 | Momentum top-100 fixed count |
| 377 | Momentum screen monthly refresh |
| 378 | SEC EDGAR Form 10-12B scrape |
| 379 | Spinoff Form 10-12B identifies parent + child |
| 380 | Spinoff window 365 days from as_of |
| 477 PROPOSED | Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv canonical; deprecate 482-CSV |

## §12.9 Test approach

- Tier 1 PIT verification: as_of ranges across 6 OOS folds; member counts within historical S&P 500 cardinality (505-510)
- Tier 2 spinoff validation: 5 known spinoffs (Mondelez/HPE/etc.) verified in scrape output
- Tier 3 momentum screen reproducibility: 2020-06 monthly snapshot reproduces from data available through 2020-05-31
- LIMITED_HISTORY flag test: synthetic 15-day-old ticker; long-history strategies skip
- Liquidity floor test: synthetic low-ADV ticker; excluded
- Workflow tests: cron jobs produce expected Parquet outputs on schedule

## §12.10 Data dependencies

**Inputs:**
- Sprint 1 OHLCV (ADV computation)
- Sprint 1 reference data (cap + sector)
- SEC EDGAR (Form 10-12B)
- Wayback Machine (historical S&P 500 backfill)

**Outputs:**
- 3-tier universes ready for engine consumption
- Sprint 9 Phase 1B-α run uses these universes

## §12.11 Operational checklist

(See §12.4 day-by-day.)

## §12.12 Open issues — gaps from ADVERSARIAL_AUDIT

- **GAP B9 (BLOCKER):** Russell 1000 inconsistency in universe definitions
  - Resolution: §12.5 done criteria — Russell 1000 explicitly NOT in Tier 1; documented in TRADING_RULES
- **GAP 95-100:** Tier 2 spinoff scrape; IPO universe; LIMITED_HISTORY flag
  - Resolution: §12.1 deliverables 6-9 explicitly cover
- **GAP 102:** Momentum screen reproducibility
  - Resolution: §12.9 test approach explicit reproducibility test
- **GAP 165:** Universe build performance
  - Resolution: §12.1 deliverable #14 universe cache; rebuild on demand only

## §12.13 Decision history

- DEC-103/104/118 Pass ~28: Tier definitions
- DEC-303 Pass ~32: Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv
- DEC-366 Pass ~38: Liquidity floor
- DEC-373-377 Pass ~40: Momentum screen detail
- DEC-378-380 Pass ~42: Spinoff via SEC EDGAR
- DEC-477 Pass 52 turn 133: canonicalize membership; deprecate 482-CSV

## §12.14 File / module structure

(See §12.3 component diagram.)

## §12.15 Example walkthrough

**Scenario:** Backtest runs day 2022-06-15. universe_builder.build('2022-06-15') called.

**Step 1:** Universe cache miss for '2022-06-15'. Build proceeds.

**Step 2:** Tier 1:
- Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv: as of 2022-06-15, 503 members (NFLX added 1990, removed 2024 not yet; ARKK never in S&P 500)
- Selected ETFs: 12 ETFs from selected_etfs.csv
- Liquidity floor: 3 small-cap members below $10M ADV → excluded
- Tier 1 list: 512 tickers

**Step 3:** Tier 2:
- Spinoffs in window 2021-06-15 to 2022-06-15: 7 found (e.g., Embecta from BD; Kenvue not yet)
- IPOs in window: 11 found (≥$2B cap, ≥20 days history)
- Tier 2 list: 18 tickers

**Step 4:** Tier 3:
- Momentum top-100 snapshot 2022-06: 100 tickers
- Liquidity + cap floors: 4 below thresholds → excluded
- Tier 3 list: 96 tickers

**Step 5:** Combined: 512 + 18 + 96 = 626 unique tickers (overlap deduplicated; e.g., AAPL in T1 and T3 counts once with both tier flags).

**Step 6:** Universe cache Parquet written for '2022-06-15'.

**Step 7:** Engine iterates 626 tickers; strategies fire per tier eligibility (e.g., spinoff strategies only on T2; momentum strategies only on T3 + T1).

**Without Sprint 5:**
- Tier 1 uses static 482-CSV CURRENT membership → 2024 members in 2022 backtest → survivorship bias
- Tier 2 absent → spinoff strategies have no candidates → 8-12 strategies inactive
- Tier 3 absent → momentum strategies operate on Tier 1 only → narrowed signal class
- Cube cells under-populated → verdict on weaker roster

---

# PART 13 — STAGE 2 VERDICT & STAGE 2 → 3 TRANSITION

## §13.1 Phase 1B-α verdict gate

The Phase 1B-α run (Sprint 9) produces the verdict cube + 3-arm A/B comparison. Stage 2 → 3 transition requires ALL of the following gates to clear:

**Numerical gates (per DEC-269 + DEC-353):**

| Gate | Threshold | Source | Reasoning |
|---|---|---|---|
| **Sharpe** | ≥ 1.0 OOS aggregate | Aggregate metric across all PASS cells weighted by trade count | Baseline acceptable risk-adjusted return |
| **Max DD** | ≤ 25% peak-to-trough | Computed across walk-forward equity curve | Owner risk tolerance ceiling |
| **Win rate** | ≥ 50% (overall); ≥ 40% in crisis regime | Per per-regime verdict matrix | Reconciled with DEC-353 R:R ≥ 2.0 floor |
| **Profit factor** | > 1.3 (high-vol sectors > 1.2) | Cube cell-level | Edge after drag |
| **Per-regime PASS** | ≥ 1 regime PASS per strategy | Per-regime verdict matrix | Strategy validity is regime-specific |

**Statistical gates (per DEC-426 + DEC-469/470 PROPOSED):**

| Gate | Threshold | Reasoning |
|---|---|---|
| **Sample size** | n ≥ 30 trades per cell | Statistical inference floor |
| **FDR q** | < 0.10 (Benjamini-Hochberg hierarchical) | Multiple-testing correction at cube scale |
| **PSR** | Probabilistic Sharpe Ratio ≥ 0.95 | Deflated Sharpe accounting for non-normality + multiple testing |
| **t-stat** | ≥ 3.4 | Bailey-Lopez de Prado discovery threshold |
| **R:R** | reward_risk_ratio ≥ 2.0 | Hard owner directive (DEC-353) |

**A/B framework gate (per DEC-131 + DEC-472 PROPOSED):**

| Gate | Threshold | Reasoning |
|---|---|---|
| **A/B Sharpe delta** | full-agents Sharpe − rules-only Sharpe ≥ 0.2 absolute OR ≥ 0.15 relative | Justifies $300 agent-overlay budget per DEC-059 |
| **Block-bootstrap CI** | 95% CI on Sharpe delta excludes zero | Statistical confidence in agent edge |
| **No-Risk arm comparison** | Risk veto adds incremental Sharpe ≥ 0.05 | Justifies Risk debate complexity |

**Owner approval gate:**
- Owner reviews Phase 1B-α dashboards (DEC-199 Cube Explorer + DEC-200 ICT/SMC Audit + DEC-201 Agent Overlay Analysis)
- Owner-witnessed inspection of per-cell verdicts + per-regime matrix + A/B Sharpe distribution
- Owner approves transition to Stage 3 OR requests methodology revision OR rejects + back to Phase 1B refinement

## §13.2 Stage 2 → Stage 3 transition criteria

Owner-explicit Stage 3 authorization requires (in addition to §13.1 numerical gates):

1. **Phase 1B-α dashboards reviewed** — DEC-199/200/201 dashboards available, owner-walked-through with claude-narrated explanation
2. **Live decision lookup table populated** — DEC-429; PASS cells form the canonical lookup that Stage 3 paper trading consults
3. **Walk-forward methodology validated** — 6 OOS folds (DEC-109) ran end-to-end without data leakage; no spurious lookahead surfaced in PIT regression suite
4. **Reproducibility verified** — Phase 1B-α run reproduced bit-exact on second invocation (DEC-218 numerical tolerance)
5. **Test pyramid green** — full CHECKLIST #69 test pyramid passing (unit + smoke + integration + system + functional + regression + data integrity + performance + acceptance)
6. **CPA consultation initiated** — Canadian tax classification (trader vs investor) per DEC-035/270 underway (need not be complete by Stage 3 entry; must be complete by Stage 4)

**Trigger:** Owner pulls trigger; no automated transition. Per CLAUDE.md HARD RULE "ALL decisions need explicit owner approval."

## §13.3 What happens if Stage 2 fails

If §13.1 gates fail, three branch points:

**Branch A — Numerical fail (Sharpe / DD / win rate below threshold):**
- Strategy roster too weak OR cube methodology too strict
- Diagnosis: review per-strategy + per-regime verdict matrix; identify which strategies passed which regimes
- Action: trim strategy roster to PASS-only set; re-run with reduced roster; OR add new strategy categories (Phase 1C+)

**Branch B — Statistical fail (FDR / PSR / t-stat below threshold):**
- Multiple-testing penalty too severe → too many strategies tested
- Diagnosis: review FDR threshold, hierarchical structure, n_trades per cell
- Action: reduce cube dimensionality (e.g., merge sector × cap_band into 7 super-buckets); OR widen sample period; OR reduce strategy count

**Branch C — A/B fail (agent overlay no edge):**
- TradingAgents debate doesn't add Sharpe over rules-only
- Diagnosis: review Risk Debate veto rates, Bull/Bear alignment rates, RM/PM rating distribution
- Action 1: refine custom toolkits (DEC-462-466) — agent reasoning may be limited by data, not architecture
- Action 2: alternative agent prompt engineering or temperature adjustment (DEC-058)
- Action 3: drop agent overlay entirely; proceed to Stage 3 with rules-only stack (Phase 1A baseline)
- Action 4: declare "agents not yet ready for this stack"; revisit at higher-resolution data tier (Phase 1C+)

**Owner authority:** branch decision is owner's, informed by claude diagnosis + dashboard review. No automatic fallback.

## §13.4 Owner approval flow

```
Phase 1B-α run completes
        │
        ▼
Cube populated + verdict assigned + dashboards rendered
        │
        ▼
Claude generates Stage 2 verdict report (markdown + dashboard pointers)
        │
        ▼
Owner reviews report + dashboards (1-2 sessions)
        │
        ▼
┌────────────┬────────────┬────────────┐
│ APPROVE    │ REVISE     │ REJECT     │
│            │            │            │
▼            ▼            ▼
Stage 3      Phase 1B     Branch A/B/C
paper        refinement   per §13.3
trading      (DEC change) (back to
begins       owner-       earlier phase
             gated)       per diagnosis)
```

**Stage 3 entry deliverables (handoff package):**
- Live decision lookup table (Parquet) — PASS cells with metadata
- Strategy roster (validated subset)
- Per-regime verdict matrix
- Phase 1B-α dashboard URLs (running locally on owner laptop or hosted)
- A/B verdict summary (Sharpe deltas + CI + per-regime)
- Reproducibility seed + run-config (so Stage 3 can replay if needed)
- CPA consultation status

---

# PART 14 — STAGE 3: PAPER TRADING (PLANNING LEVEL)

**Status:** Planning level. Real design begins after Stage 2 verdict.

## §14.1 Goal

Run the Stage-2-validated stack against live market data in paper-trading mode (no real capital) for ≥3 months. Verify operational + behavioral fidelity:

- Live execution matches backtest expectations within DEC-269 divergence threshold (< 20%)
- Agent decisions in real-time produce same Sharpe distribution as backtest
- No infrastructure failures over sustained 3-month period
- Operational reliability — data freshness, kill switch, reconciliation

## §14.2 Duration and prerequisites

**Duration:** 3 months minimum (DEC-028)

**Prerequisites (Part 13 §13.2 transition criteria + the following Stage 3-specific items):**

| Prereq | Decision | Status |
|---|---|---|
| Paper trades mirror live algo exactly | DEC-198 | Confirmed at design |
| SQLite trade event store | DEC-267 (Postgres deferred Stage 4) | Designed, not built |
| End-of-day reconciliation reports | DEC-181 | Designed, not built |
| Weekly auto-generated performance review | DEC-182 | Designed, not built |
| Live decision lookup table populated | DEC-429 | Sprint 9 deliverable |
| Daily monitoring dashboards | DEC-199/200/201 (from Phase 1B-α) | Sprint 9 deliverable |
| Email notifications for trade entries/exits | DEC-194/195 | Stage 3+ infrastructure |
| Polygon Stocks Advanced subscription | DEC-478 (or equivalent real-time) | Pending tier choice |
| IBKR market data subscriptions | ~$10-30/mo per DEC-271 | Subscription pending |

## §14.3 Activities

**Daily routine:**
- Pre-market: data freshness check, kill switch verification, calendar event review
- Market hours: paper algo executes per live decision lookup; positions tracked in Portfolio class
- Close: end-of-day reconciliation report; live-vs-backtest divergence computed
- Owner reviews EOD report (10-15 min)

**Weekly routine:**
- Auto-generated QuantStats performance review
- Cube cell hit-rate analysis (which PASS cells fired this week, which FAIL_RR cells fortunately did not)
- A/B framework live behavior tracking

**Monthly routine:**
- Strategy decay re-validation (DEC-214) — has any strategy that PASSed in Stage 2 started failing live?
- Tax tracking (informational; CRA reporting only required for live capital)

## §14.4 Stage 3 → Stage 4 transition criteria

Per DEC-269 + Part 14:

1. **3 months paper trading complete** — calendar-elapsed
2. **Live-vs-backtest divergence < 20%** — sustained across 3 months (not just one week)
3. **Numeric gates met during paper period** — Sharpe / DD / win rate within DEC-269 thresholds
4. **CPA consultation complete** — Canadian tax classification finalized (DEC-270)
5. **Multi-vendor data fallback operational** — DEC-160; single-API-down doesn't kill live
6. **Remote kill switch via email operational** — DEC-139; owner can halt the algo from anywhere
7. **Daily loss limits operational** — DEC-034; algo halts at -X% daily P&L
8. **Norbert's Gambit operational for CAD→USD funding** — DEC-255
9. **Cloud hosting migration complete** — DEC-272; local laptop is dev only
10. **Disaster recovery plan in place** — DEC-273
11. **Owner explicit Stage 4 approval** — informed by all above

## §14.5 Stage 3 Website + Dashboard Architecture (RESTORED Pass 53 owner directive 2026-05-05)

**Owner-flagged elimination:** "the website creation has been completely removed? Why? That is still a key deliverable in stage 3. Can not be removed!" — restored Pass 53 turn 2026-05-05.

**Canonical home:** PROJECT_PLAN.md §32 — Website Architecture & Phase-Specific Analytics Dashboards.

This sub-section summarizes Stage 3 entry prerequisites that are website + dashboard related; full spec lives in PROJECT_PLAN.md §32 (restored from Pass 44 commit `bb6335d6`).

### §14.5.1 Stage 3 entry prerequisites (website / dashboard)

Per DEC-187 to DEC-204 (Pass 43-44 + Pass 53 promotions Q3):

1. **Property 1 — Public Recommendations Site** (Next.js + Vercel free tier per DEC-187/190)
   - Mobile-first card-based layout with 10-point trade rationale per recommendation (DEC-189)
   - Section A "Today's recs" + Section B "Yesterday's results" with status badges
   - Track record header (rolling 30/90/all-time win rate, profit factor)
   - Publish timing per DEC-191 (pre-market 7-8am ET + post-close 4pm ET)
   - DEC-192: actual paper trades with real slippage shown (not theoretical)
   - DEC-196: no auth during paper trading

2. **Property 2 — Dashboard 4 (Stage 3 Paper Trading Analytics)** — Streamlit per DEC-048
   - **PROMOTED Pass 53 from DEFERRED to RESOLVED-DECIDED** per Q3 owner directive
   - 11-section spec per PROJECT_PLAN.md §32.5 Dashboard 4 (status bar / equity curves / DD chart with breaker overlay / per-strategy P&L attribution / per-regime breakdown / trade journal with 10-point rationale searchable / backtest-vs-paper divergence tracker / KPIs panel / circuit breaker status / system health / push alert log)
   - Effort: ~5-7d (reuses Dashboard 1 Cube infrastructure)

3. **Telegram bot + 6 alert events** (DEC-194/195)
   - Stop-out / circuit breaker / position halted / daily P&L breach (-2%/-5%) / divergence threshold / data feed failure
   - Email summary twice daily (pre-market 7am + post-close 4:30pm)

4. **Tech stack & hosting**
   - Public site: Vercel free tier (~$0/mo)
   - Dashboard 4: Streamlit Cloud free tier (~$0/mo)
   - Backend: Local VS Code (Pass 53; was Codespace) until Stage 4 cloud migration
   - Database: SQLite trade event store (DEC-267)

### §14.5.2 Build sequence (Pass 53 §32.7)

| Sub-phase | Deliverable |
|---|---|
| Sprint 9 (Phase 1B-α run) | Dashboard 1 + 2 + 3 fully operational (already-spec'd; DEC-199/200/201) |
| **Stage 3 entry preparation** | **Public Site (Property 1) + Dashboard 4 (DEC-202 promoted Pass 53) + Telegram + Email** |
| Stage 3 ongoing | Daily monitoring via Dashboard 4; weekly performance reviews via QuantStats |
| Stage 4 entry | + Dashboard 5 (DEC-203 promoted Pass 53) + Dashboard 6 (DEC-204 promoted Pass 53) |

### §14.5.3 DEC inventory restored Pass 53

DEC-187 to DEC-198 RESOLVED-DECIDED Pass 43 (existed in AUDIT_INDEX; restored visibility in PROJECT_PLAN §32).
DEC-199/200/201 RESOLVED-DECIDED Pass 52 turn 79 (5/5/6-section specs).
**DEC-202/203/204 PROMOTED Pass 53** from DEFERRED to RESOLVED-DECIDED with full specs (per Q3 owner directive 2026-05-05).

### §14.5.4 Cost summary update (Stage 3+ hosting)

Per PROJECT_PLAN.md §32.9:
- Stage 3 hosting: ~$0-5/mo (Vercel free + Streamlit Cloud free + Telegram free + email)
- Stage 4 hosting: ~$55-85/mo (Vercel Pro + Streamlit Cloud Teams + IBKR market data)

---

# PART 15 — STAGE 4: LIVE TRADING SMALL SCALE (PLANNING LEVEL)

**Status:** Planning level. Real design at Stage 4 entry.

## §15.1 Goal

Trade real capital at small scale ($10K-50K range, owner choice) for ≥6 months. Validate everything Stage 3 paper showed against actual fills, FX conversion costs, tax events, and operational issues that don't show in paper mode.

## §15.2 Prerequisites

All Stage 3 → Stage 4 transition criteria (Part 14 §14.4) must hold. Plus:

- Live brokerage account funded (IBKR confirmed account holder per CLAUDE.md)
- Live capital authorization explicit from owner — written confirmation
- IBKR API credentials configured + tested
- Kill switch tested with real-money paper-equivalent (post-Stage-3 dry-run)

## §15.3 Activities

**Daily routine:**
- Pre-market: same as Stage 3 + capital balance check
- Market hours: live algo executes; real money flows
- Close: same as Stage 3 + actual fill quality review (slippage tracking per DEC-092/122/280)
- Owner reviews EOD report (15-20 min); reconciles broker statement

**Weekly routine:**
- Performance review with QuantStats (live-money version)
- Slippage / commission / borrow cost tracking
- A/B framework live behavior — does the verdict cube live-up to its predictions?

**Monthly routine:**
- Tax tracking (CRA-compliant; T5008 / capital gains accumulation)
- Quarterly strategy decay re-validation (DEC-214)
- CPA review (quarterly)

**Quarterly:**
- Strategy retirement review per DEC-249/214/043 — strategies that have decayed retired from roster
- Strategy addition review — new candidate strategies considered for next Stage iteration

## §15.4 Stage 4 → Stage 5 transition criteria

Per DEC-028 + DEC-029:

1. **Stage 4 stable ≥ 6 months** — calendar-elapsed without major incident
2. **Cumulative P&L positive** — net of slippage / commission / borrow / FX
3. **No major operational incidents** — definition: data outage > 4 hours, wrong-side trade, kill switch failure, unauthorized capital deployment
4. **Owner-approved scaling plan** — written; specifies capital ramp curve
5. **Compliance + tax tracking operational** — at owner satisfaction
6. **Owner explicit Stage 5 approval** — automation authorization

---

# PART 16 — STAGE 5: FULL AUTOMATION (PLANNING LEVEL)

**Status:** Planning level. Real design at Stage 5 entry.

## §16.1 Goal

Stage 4 deliverables operating autonomously with minimal owner intervention. Owner role shifts from operator to monitor + strategist.

## §16.2 Activities

**Owner role at Stage 5:**
- Weekly performance review (15 min)
- Monthly strategy health review (1 hour)
- Quarterly capital scaling decisions
- Annual strategy retirement / addition cycle
- Incident response (rare; algo runs unattended)

**Algo role at Stage 5:**
- All Stage 4 capabilities running unattended
- Self-monitoring with owner alert escalation
- Continuous A/B + ablation testing in live (DEC-211 evolved to ongoing)
- Strategy retirement/addition workflow operational (DEC-249/214/043)

**Cost at Stage 5:**
- Full API stack operational (~$93-263 CAD/mo per project memory; revised to $93-200+/mo per DEC-478 tier choice)
- Cloud hosting recurring
- IBKR market data subscriptions
- CPA fees

---

# PART 17 — CROSS-CUTTING CONCERNS

## §17.1 PIT correctness discipline (applies all stages)

Point-in-time correctness is non-negotiable. Every backtest data fetch must respect `as_of` cutoff. Violations are CRITICAL bugs.

**Enforcement layers:**

1. **`PointInTimeLoader` ABC contract (DEC-040)** — every fetcher inherits; `fetch(ticker, as_of, ...)` returns rows where `published_date ≤ as_of`.
2. **PIT regression suite (DEC-417 + Sprint 6 catch mechanism)** — `test_pit_regression.py` runs same backtest with different system times via freezegun; results MUST be bit-identical.
3. **PIT guard RAISE not WARN (DEC-305 Pass 50)** — `_assert_no_lookahead` raises `LookAheadBiasError` instead of warning. Bypass via `ALLOW_LOOKAHEAD_LEAK=1` for explicit debug only.
4. **ALFRED vintage realtime_end (DEC-301 Pass 50)** — FRED revisions caught with vintage-aware queries. UNRATE / CPI / GDP routinely revised 6+ months after first publication; without ALFRED, backtests leak future revisions.
5. **Smart money date semantics (DEC-324 Pass 51)** — congressional/insider trades age-weighted by TRANSACTION date, not DISCLOSURE date. Disclosure provides PIT availability gate; transaction provides signal-value timestamp.

**PIT-related decisions:**

| DEC | Title | Status |
|---|---|---|
| 040 | PointInTimeLoader ABC | RESOLVED-DECIDED |
| 295 | T2 IPO eligibility on listing date (PIT-correct) | RESOLVED Pass 50 |
| 301 | ALFRED vintage values for revised series | RESOLVED Pass 50 |
| 302 | ^VIX canonical preferred over VXX proxy | RESOLVED Pass 50 |
| 304 | Economic calendar JSON (no hardcoded staleness) | RESOLVED Pass 50 |
| 305 | PIT guard RAISE not WARN | RESOLVED Pass 50 |
| 309 | Volatility lookback PIT-correct | RESOLVED Pass 50 |
| 311 | Trade exit timing PIT-correct | RESOLVED Pass 50 |
| 312 | Rolling stat windows PIT-correct | RESOLVED Pass 50 |
| 315 | Universe-membership PIT filter | RESOLVED Pass 50 |
| 316 | Regime classifier fail-closed on missing VIX | RESOLVED Pass 50 |
| 324 | Congressional trade transaction-date age-weighting | RESOLVED Pass 51 |
| 325 | 13F filing-date PIT not quarter-end | RESOLVED |
| 477 | Tier 1A historical_membership.csv canonical PIT | RESOLVED-IMPLEMENTED Pass 53 |

## §17.2 Cost summary (all stages)

**Stage 2 monthly recurring:**
- Polygon Stocks Starter: $29/mo (current; $79 Developer or $199 Advanced if DEC-478 owner upgrade)
- Quiver Quantitative paid (Trader tier): $50-100/mo (DEC-450)
- FMP if DEC-461 approved: $14-50/mo (Sprint 4 onward)
- FRED + ALFRED + AAII + CNN F&G + CFTC COT + Apewisdom + pytrends: free
- SEC EDGAR via edgartools: free

**Stage 2 one-time:**
- TradingAgents v0.2.4 fork integration: 0 (open-source, Apache 2.0)
- smartmoneyconcepts library: 0 (open-source)
- Phase 1B-α agent overlay budget: $300 cap (DEC-059)

**Stage 3 monthly recurring:**
- All Stage 2 + cloud hosting (~$10-30/mo) + email infrastructure (~$5/mo)

**Stage 4 monthly recurring:**
- All Stage 3 + IBKR market data ($10-30/mo) + CPA consultation (variable)

**Stage 5 monthly recurring:**
- All Stage 4 + scale-dependent additions

## §17.3 Tech stack

**Languages + frameworks:**
- Python 3.10+ (primary)
- pandas / numpy / pyarrow (data)
- pandas-ta (technical indicators)
- pandas-market-calendars (DEC-235)
- requests / polygon-api-client / fredapi (API clients)
- filelock (multi-process safety)
- freezegun (PIT testing)
- pytest + pytest-xdist (test framework)
- LangGraph (TradingAgents orchestration)
- Anthropic SDK (Claude Haiku Phase 1B; Sonnet Phase 1C+)

**Forked libraries (per DEC-045 fork-first architecture):**
- smartmoneyconcepts (ICT/SMC primitives)
- TradingAgents v0.2.4 (multi-agent framework)
- QuantStats (analytics)
- Streamlit (dashboards per DEC-430)
- ib_async (IBKR live; Stage 4)
- edgartools (SEC EDGAR; Sprint 0A.6)
- pytrends (Google Trends; Sprint 0A.7)

**Storage:**
- Parquet for OHLCV + cache (DEC-491 — nested/binary data via Parquet, flat data via CSV)
- SQLite for trade event store (DEC-267; Postgres deferred Stage 4)
- CSV for universe + reference data (CLAUDE.md HARD RULE: data lives in CSV files, code pulls from CSV)

**Infrastructure:**
- Local Windows laptop + VS Code + Claude Code (Pass 53 update; was Codespaces)
- GitHub Actions for cron jobs (universe refresh, daily snapshot, sentiment refresh)
- Polygon API + Quiver API + FRED API + supplementary free sources

## §17.4 Process and governance

**Approval cadence:**
- ALL decisions need explicit owner approval before implementation (CLAUDE.md HARD RULE)
- Per CHECKLIST #51 — Option C verification gate
- Per CHECKLIST #67 — every turn with meaningful changes ends with doc sweep
- Per CHECKLIST #68 — smoke→demo→full for any multi-call API operation
- Per CHECKLIST #69 — full test pyramid before every code push (DEC-503 Pass 53)

**Decision tracking:**
- AUDIT_INDEX.md — DEC list (currently DEC-001 through DEC-503)
- AUDIT.md — full decision narrative
- BUG_REGISTER.md — bug log
- LEARNINGS.md — lessons learned (currently L1-L144)

**Test discipline (Pass 53 DEC-503 + CHECKLIST #69):**
- Unit + smoke + integration + system + functional + regression + data integrity + performance + acceptance per push
- All tests pass per CANONICAL_FACTS F-007 (Pass 53 R7-08 fix; was hardcoded "36/36"; current count drifts as new test files added — `backtest/tests/test_unit.py` + `backtest/tests/test_integration.py` + Pass 53 additions: `test_smartmoneyconcepts_*` + `test_canonical_facts_alignment.py` + 16 BATCH 14 smoke/demo files)
- Partial coverage non-compliant

## §17.5 Open architectural decisions

As of Pass 53 turn 2026-05-05, awaiting owner action:

| DEC | Title | Decision needed |
|---|---|---|
| 461 | FMP subscription | Pre-Sprint-4 owner action (now MANDATORY per DEC-460 verification negative) |
| 469 | FDR replacing Bonferroni | Methodology approval |
| 470 | Hierarchical FDR structure | Per-strategy / per-cell / per-regime tree |
| 471 | Cube reduction 17→8 dims | Approved Pass 52; implementation pending |
| 472 | Block bootstrap replacing paired design | A/B methodology |
| 473 | A/B 5-arm → 3-arm reduction | Cost-driven |
| 478 | Polygon tier upgrade choice | $29 Starter / $79 Developer / $199 Advanced |
| 481 | AgentGateConfig Option C2 | 5-tier rating + markdown parser |

(Full list in AUDIT_INDEX.md PROPOSED status.)

---

# PART 18 — READING GUIDE & MAINTENANCE

## §18.1 Section template (per phase 15-section pattern)

Every Stage 2 phase part (Parts 3-12) follows the same 15-section pattern per Q2 owner directive Pass 52 turn 134:

| Section | Purpose |
|---|---|
| .1 What | Concrete deliverable in plain English |
| .2 Why | How this advances Stage 2 toward verdict |
| .3 How | Components, data flow, dependencies (technical body) |
| .4 When | Sequence, blockers, parallel-ability |
| .5 Done criteria | Verifiable acceptance (not "see other doc") |
| .6 Risks | What could go wrong specifically |
| .7 Cost | Engineering days + dollars (subscriptions, API calls) |
| .8 Decisions in scope | List with one-line summaries |
| .9 Test approach | How the deliverable is verified |
| .10 Data dependencies | What feeds in, where it comes from, what's downstream |
| .11 Operational checklist | Week-by-week or day-by-day breakdown |
| .12 Open issues | Gaps from ADVERSARIAL_AUDIT relevant to this phase |
| .13 Decision history | What changed and why; key supersessions |
| .14 File/module structure | Where in `backtest/` each component lives |
| .15 Example walkthrough | Concrete trace of one trade through this phase's logic |

**Pass 53 additions:** Part 3 (Sprint 0A) extends with §3.16 (expanded scope) + §3.17 (DEC-497-503 scope) per owner directive 2026-05-05.

## §18.2 How to update this document

**When this document and others diverge, THIS document is canonical.** Other docs become reference appendices.

**Update triggers:**
- Owner directive (Pass-tagged with date)
- New DEC entry referenced from this doc
- Sprint completion → update §X.13 decision history + §X.16/§X.17 status snapshots
- Adversarial audit finding (DEC-417 / Sprint 6 catch mechanism) → update §X.12 open issues
- Test pyramid revision (CHECKLIST #69 / DEC-503) → update §X.9 test approach + §17.4 governance

**Update protocol (per CHECKLIST #67 + #67.b):**
1. Identify trigger (owner directive / DEC / sprint event)
2. Identify affected sections in this doc
3. Edit sections preserving existing content (HARD RULE: don't eliminate)
4. Cross-reference to AUDIT.md / AUDIT_INDEX.md / BUG_REGISTER.md / LEARNINGS.md / TRADING_RULES_AND_INFORMATION.md as needed
5. Commit + push same turn (decoupled from pending API runs per #67.b)

**Pass 53 owner directive (CHECKLIST #67 codified 2026-05-05):**
> Going forward, at the end of every turn, you need to update all documents outside of `archive/` folder with necessary modifications.

> Document updates are not linked to pending runs. Document updates need to be committed each turn.

## §18.3 Cross-document map

| Doc | Role | Update cadence |
|---|---|---|
| **DETAILED_PROJECT_PLAN.md (this doc)** | Canonical project plan; every phase + sprint elaborated | Every meaningful change |
| **PROJECT_PLAN.md** | Quick-reference card | Every meaningful change (compressed) |
| **TRADING_RULES_AND_INFORMATION.md** | Canonical thresholds + per-phase acceptance criteria | When thresholds change |
| **TRADINGAGENTS_DATA_AUDIT.md** | Agent data dependency mapping | When data sources change |
| **CHECKLIST.md** | Pre-action checklist (currently 69 items) | When new rules added |
| **CLAUDE.md** | Project instructions for claude code | When HARD RULES change |
| **AUDIT.md** | Full decision narrative | Per-decision; per-pass |
| **AUDIT_INDEX.md** | DEC list + status (currently 1-503) | Per new DEC |
| **BUG_REGISTER.md** | Bug log (BUG-001 - BUG-273) | Per new bug |
| **LEARNINGS.md** | Lessons learned (L1 - L144) | Per significant lesson |
| **STRATEGY_REGISTER.md** | Strategy roster Layer 1+2+3+4 | When strategies added |
| **ENGINEERING_REGISTER.md** | Sprint planning + effort estimates + pyramid coverage | Per sprint planning iteration |
| **API_AUDIT.md** | Per-API endpoint inventory | When endpoint scope changes |
| **THEME_X53_SEQUENCING.md** | Pass 53 Sprint 0A sub-phase detail | When Sprint 0A sequence changes |

**Reading paths:**
- **First-time reader (1 hour)** — this doc Parts 0-2.6 + Part 13 (verdict) + Part 17 (cross-cutting) — gives full context
- **Active sprint review (15 min)** — this doc Part X for current sprint + AUDIT.md latest pass entries
- **Decision review (10 min)** — AUDIT_INDEX.md → specific DEC → AUDIT.md narrative + cross-references
- **Bug investigation** — BUG_REGISTER.md → specific BUG → AUDIT.md if architectural; LEARNINGS.md if pattern-level

---

