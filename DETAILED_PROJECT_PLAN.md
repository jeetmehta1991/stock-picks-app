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
- §2.4 Strategy roster (4 layers, ~109-119 strategies)
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

**Part 8 — Phase 1B: Statistical Methodology + A/B + Custom Toolkits**
(15 sections)

**Part 9 — Phase 1B-α: Dimensional Cube + Dashboards**
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
- Personal Windows laptop + GitHub Codespace ("vigilant system") for development
- VS Code + Claude Code for browsing and code review
- Codespace terminal for Python execution
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
- Static committed CSV of S&P 500 constituents (482 tickers — Wikipedia scraping was blocked by Codespace network allowlist; CSV was the workaround)

**Key lessons preserved into Stage 2 architecture:**
1. Wikipedia scraping is unreliable in Codespace (network allowlist blocks); use static committed reference data or paid APIs
2. GitHub Actions cron + commit pattern works for low-frequency data refresh
3. `index.html` rendering proves the front-end → back-end → data pipeline works end-to-end (small but real)
4. Alpha Vantage was sufficient for proof-of-concept but is being demoted in Stage 2 (Polygon replaces it per DEC-441/455)

**Why Stage 1 isn't being refactored:** It works, it's stable, and the daily updater commits to `index.html` are a known noise factor in `git pull --rebase` flow. Stage 2 builds alongside, not replacing.

## §1.3 Stage 2: Strategy Validation (CURRENT)

**Status:** Pass 53 begins implementation. Pass 52 closed audit (462 → 472 decisions, 0 PENDING). Pass 52 turn 132 surfaced 167 documentation gaps + 10 Stage 2 effectiveness blockers via adversarial review. Pass 52 turn 133 began critical-gap resolution (FDR replacing Bonferroni, cube dimensionality reduction, paired A/B elimination, Portfolio class API spec, TradingAgents v0.2.4 schema verification, Polygon tier reconsideration).

**Goal:** Empirically validate the strategy roster across a dimensional verdict cube using walk-forward validation + A/B testing of agent overlay vs rules-only. Produce per-cell verdicts (PASS/FAIL/INSUFFICIENT_SAMPLE) that feed a live decision lookup table for Stage 3.

**Effort:** ~310-385 engineering days realistic; ~125-160 days minimum critical path.

**Sub-phases (covered in Parts 3-12):**

| Phase | Part | Sprint | Effort |
|---|---|---|---|
| 0.A — Polygon Foundation | Part 3 | Sprint 1 | ~20.5-26.5d |
| 0.B — Portfolio Class | Part 4 | Sprint 3 | ~8-11d |
| 0.C — Engine Bug Fixes Tier A | Part 5 | Sprint 2 | ~25.5-30.5d |
| 0.D — ICT/SMC Fork Integration | Part 6 | Sprints 1/4/8 | distributed |
| 0.E — Catch-Mechanism + Hygiene | Part 7 | Sprint 6 | ~62.25-76.75d |
| 1B — Statistical + A/B + Toolkits | Part 8 | Sprint 7 | ~96-108.5d (post-DEC-462-468) |
| 1B-α — Cube + Dashboards | Part 9 | Sprint 7-8 | ~28-38d |
| 1C+ — Strategy Categories | Part 10 | Sprint 8 | ~37-55d |
| (Sprint 4 — DEC-410 audit) | Part 11 | Sprint 4 | ~41.75-54.25d |
| (Sprint 5 — Universe Mgmt) | Part 12 | Sprint 5 | ~13.5-15.5d |
| 1B-α run + ongoing | end of Part 9 | Sprint 9 | ~6d (orchestration; compute ~37-40h wall) |

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
- Cloud hosting migration complete (DEC-272) — Codespace is dev only, not production
- Disaster recovery plan in place (DEC-273) — backup, restoration, runbook
- IBKR market data subscriptions active (~$10-30/mo per DEC-271) — real-time bid/ask required
- Polygon Stocks Advanced (or equivalent) for real-time data — if continuing Polygon (per DEC-478 PROPOSED tier upgrade)

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
- Full API stack operational (~$263 CAD/mo baseline per project memory; revised to $93-200+/mo per DEC-478 PROPOSED tier choice)

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

**Cube definition (revised per DEC-471 PROPOSED — reduced from 17+ dims to 8 core dims):**

| # | Dimension | Levels | Why it matters |
|---|---|---|---|
| 1 | Strategy | 119 (Layer 1+2+3+4 from STRATEGY_REGISTER) | The thing being tested |
| 2 | Market regime | 4 (calm/neutral/volatile/crisis per DEC-106) | Strategies that work calm may fail volatile |
| 3 | Sector | 11 GICS | Tech vs Energy vs Financials may have different signal-to-noise |
| 4 | Market cap band | 3 (mega/large/mid) | Mid-caps less efficient; large more efficient |
| 5 | Vol band | 3 (low/medium/high VIX) | Vol regime affects mean-reversion vs trend |
| 6 | Hold period band | 3 (short ≤3d / medium 4-10d / long ≥11d) | Different exit dynamics |
| 7 | Universe tier | 3 (Tier 1 S&P 500 / Tier 2 spinoffs/IPOs / Tier 3 momentum) | Liquidity and efficiency differ |
| 8 | Smart money signal present | 2 (yes/no per DEC-124 confluence) | Smart money should add edge |

**Cell count:** 119 × 4 × 11 × 3 × 3 × 3 × 3 × 2 = 254,016 maximum cells.

**Expected populated cells:** ~20-30% (50K-75K) — many cells will be empty because trades simply don't occur in some combinations (e.g., a mid-cap technology calm-regime short-hold smart-money-no scenario may never trigger any of 119 strategies).

**Why we reduced from 17+ to 8:** Original cube design (TRADING_RULES §21.1) had 17+ dimensions. Adversarial Pass 4 (GAP 130) showed: 119 strategies × 65K cells × 30 trades min × 6 OOS folds = 1.4 BILLION trades required. Universe provides 720K ticker-days. Math impossible. Reduction to 8 core dims with eliminated dimensions becoming TRADE-LEVEL METADATA (recorded in DEC-189 trade outcome log) brings the math back to feasibility.

**Eliminated dimensions (now trade metadata, not faceted):**
- Momentum band — recorded per trade, queryable but not a cube axis
- Liquidity band — used as pre-trade filter (DEC-321/366), not faceted
- Entry trigger type — recorded
- Exit method — recorded (17 methods per DEC-067)
- News event present — recorded
- Earnings proximity — already a filter via DEC-348 event suppression
- ICT/SMC signal type — per-strategy attribute

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

## §2.3 Universe architecture (3 tiers)

The universe defines the trading population — which tickers are even eligible to be traded. 3 tiers exist because liquidity, history, and efficiency differ enough to warrant different rules.

**Tier 1 — S&P 500 + Selected ETFs (~509 tickers):**
- Composition: S&P 500 constituents per `historical_membership.csv` (DEC-303 — PIT-correct historical membership; supersedes static 482-ticker CSV per DEC-477 PROPOSED) + selected sector/macro ETFs (per DEC-118: VIX, DXY, GLD, oil, sector ETFs, TLT, HYG, SHY)
- Liquidity floor: $10M ADV (per DEC-366)
- History requirement: 250 trading days
- Why this tier: most-liquid US equities; highest signal-to-noise for technical strategies

**Tier 2 — Spinoffs / IPOs (variable, ~10-30 tickers active):**
- Composition: recent spinoffs (per DEC-378/379/380 — SEC EDGAR Form 10-12B scrape) + recent IPOs (per DEC-103/373/374)
- Liquidity floor: $5M ADV
- Market cap minimum: $2B
- History requirement: 20 days minimum (with `LIMITED_HISTORY` flag respected by strategies that need longer history)
- Why this tier: spinoffs and IPOs often have inefficient pricing; specific strategies target this

**Tier 3 — Momentum Top-100 Watchlist:**
- Composition: top 100 momentum-screen tickers refreshed monthly (per DEC-104/375/376/377)
- Liquidity floor: $5M ADV
- Market cap minimum: $300M
- History requirement: 60 days
- Refresh: monthly via `.github/workflows/refresh_momentum_watchlist.yml`
- Why this tier: momentum strategies need a candidate pool that updates with regime; static lists go stale

**Universe build pipeline (Sprint 5, Part 12):** Each tier has a build function that runs at backtest start (or daily in live) producing a list of tickers eligible for that tier on that as_of date. PIT-correctness applies — at as_of=2020-06-15, Tier 1 should reflect S&P 500 membership AS OF that date, not current.

## §2.4 Strategy roster (4 layers, ~109-119 strategies)

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

**Layer 4 — Sub-decisions and additive (DEC-432/433/435 from DEC-067/075):**
- 9 new exit method variants (DEC-432/433 — chandelier, psar, supertrend, volatility_regime, volume_climax, rsi_extreme, partial_scaleout, kelly_target, macro_event)
- AEP breaker strategy (DEC-435)

**Total strategy roster:** ~109-119 strategy classes when Layer 1+2+3+4 fully implemented.

**BUG-111 architectural choice (deferred):** Existing 25 breakout strategies in `screener.py` may need break-and-retest variants. Option A (shared retest primitive ~5-10d) recommended over Option B (per-strategy variants ~25-30d). Decision deferred to Sprint 8 implementation start (Part 10).

**STRATEGY_REGISTER.md is the canonical roster** — when this plan adds/changes strategies, that doc is updated atomically.

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

Stage 2 requires the following data sources. Polygon tier choice (Stocks Starter $29/mo vs Developer $79/mo vs Advanced $199/mo) is open per DEC-478 PROPOSED. My recommendation Pass 52 turn 133: Stocks Developer $79/mo + FMP $14-50/mo = $93-129/mo total.

**Confirmed sources:**

| Source | Purpose | Cost | Status |
|---|---|---|---|
| **Polygon Stocks (tier TBD per DEC-478)** | OHLCV, reference data, news, technical indicators, corporate actions | $29-199/mo | Subscription pending owner direction |
| **FMP (Financial Modeling Prep)** | PIT financials, earnings transcripts, analyst consensus estimates | $14-50/mo | NEW addition pending DEC-461 + DEC-478 |
| **FRED + ALFRED** | Macro data (rates, jobless, CPI, etc.); ALFRED for vintage PIT | Free | Stage 2 use confirmed |
| **Quiver Quantitative paid** | Insider trading (Form 4+144), congressional, 13F, analyst rating changes, government contracts | ~$50-100/mo | Confirmed paid (DEC-450) |
| **Ortex** | Short interest | TBD (in plan; not yet wired) | DEC-468 wires it Sprint 7 |
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
RULES-BASED SCREEN — fires 109-119 strategies on Tier 1/2/3 universe
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
- 6 OOS folds total (DEC-109): ~30-50 hours wall time
- Cube + verdict + dashboards: ~15 hours additional
- Total Phase 1B-α run: ~37-40 hours wall time (per Sprint 9 compute estimate Part 9 §9.7)

**Codespace 8-core machine sufficient** with parallel folds; no cloud migration needed for Stage 2 (cloud begins Stage 4 per DEC-272).

---

# PART 3 — PHASE 0.A: POLYGON FOUNDATION (Sprint 1)

## §3.1 What — concrete deliverable in plain English

Phase 0.A produces the **data foundation** for Stage 2 backtest. By the end of Sprint 1, the backtest engine can pull point-in-time-correct OHLCV data, corporate actions, reference data (sector, market cap, GICS classification), and macro/sentiment data for any S&P 500 ticker on any historical date back to the start of the cache window — without lookahead bias, with proper survivorship correction, and with deterministic cache behavior.

Concrete deliverables:

1. **Polygon API integration** — `backtest/data/polygon_client.py` wrapping Polygon REST API for: OHLCV daily aggregates, OHLCV minute aggregates, reference data, corporate actions (splits/dividends), news endpoint, technical indicators endpoint. API key stored in environment variable; rate limiting respected; failures retry with exponential backoff per DEC-260.

2. **`PointInTimeLoader` base class (DEC-040)** — `backtest/data/pit_loader.py` abstract class that all PIT-aware fetchers inherit from. Defines `fetch(ticker, as_of_date, **kwargs)` contract: returns data WHERE all rows have `published_date ≤ as_of_date`. Includes edge case handlers: weekend `as_of` (returns last trading day's data), pre-IPO `as_of` (returns empty + warning), post-delist `as_of` (returns up to delisting), partial cache (re-fetch missing range; fail-fast per DEC-260).

3. **OHLCV cache layer** — `backtest/data/cache_ohlcv.py` Parquet cache for raw OHLCV with `auto_adjust=False` semantics (DEC-298). Adjusted-on-demand recomputation by `as_of` date using corporate actions table — meaning if today is 2024-06-15 and we ask for AAPL price on 2020-06-15 with as_of=2020-06-15, we recompute the adjustment factors using only splits/dividends that occurred BEFORE 2020-06-15.

4. **Polygon S&P 500 prefetch** — bulk download of OHLCV for all 509 Tier 1 tickers (S&P 500 constituents per `historical_membership.csv` + selected sector/macro ETFs) for the cache window (depth depends on DEC-478 tier choice — Stocks Starter $29 = 5yr; Developer $79 = 10yr; Advanced $199 = 20yr).

5. **Cache hygiene infrastructure (DEC-329)** — disk usage monitoring (warn at 80% / hard fail at 95% per DEC-243), filelock for multi-process safety (DEC-431, 5s timeout), cache eviction policy distinguishing prefetched vs dynamically-fetched files (DEC-244 — prefetched files marked with metadata file `.prefetch.lock` for LRU exemption).

6. **FRED expansion to 9+ series (DEC-407+448)** — `backtest/data/fred_client.py` fetches VIX, DGS10 (10y treasury), T10Y2Y (yield curve), FEDFUNDS, UNRATE, CPIAUCSL, T10YIE (breakeven inflation), BAA10Y (HY spread proxy), DXY. ALFRED used for vintage PIT correction.

7. **AAII + CNN F&G refresh scripts** — `.github/workflows/refresh_aaii.yml` and `.github/workflows/refresh_cnn_fg.yml` cron jobs (weekly Thursday for AAII; daily for CNN F&G with 1-day lag respected per DEC-320). Output committed to `data/sentiment/aaii.parquet` and `data/sentiment/cnn_fg.parquet`. Codespace network allowlist verified working for AAII/CNN F&G domains pre-commit (per Sprint 0 action).

8. **Polygon reference replacing yfinance.info (DEC-443)** — sector classification, market cap, exchange, listing dates pulled from Polygon Reference Data endpoint instead of yfinance.info (which has no as_of date support and BUG-218 returns CURRENT not as_of).

9. **Polygon earnings cache (DEC-256, replacing yfinance per DEC-444)** — `backtest/data/polygon_earnings.py` fetches historical earnings dates + EPS actuals + estimates. Cache key: ticker + earnings_date. PIT-aware via filing_date.

10. **Cache freshness rules implemented (DEC-260)** — OHLCV cache stale threshold 1 day; sentiment 7 days; fundamentals 90 days. Stale cache → re-fetch (not silent staleness).

## §3.2 Why — how this advances Stage 2 toward verdict

The verdict cube (Part 2 §2.2) cannot be populated without trade outcomes. Trade outcomes cannot be computed without prices. Prices must be PIT-correct or the entire backtest is contaminated by lookahead bias. Therefore: **no Phase 0.A foundation = no valid Stage 2 verdict.**

Specific dependencies that justify Phase 0.A as Sprint 1:

- **Sprint 2 (engine bug fixes Tier A)** operates on cache produced by Sprint 1; if cache schema changes mid-Sprint-2, fixes refer to obsolete schema. Phase 0.A defines schema first.
- **Sprint 3 (Portfolio class)** queries OHLCV for current market values via `update_market_values(prices, as_of)`. Needs cache layer.
- **Sprint 5 (universe management)** builds Tier 2/3 universes which depend on `historical_membership.csv` PIT correctness — established in Sprint 1.
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
- DEC-303 + 477 PROPOSED — `historical_membership.csv` canonical S&P 500 (deprecates 482-CSV static)

## §3.4 When — sequence, blockers, parallel-ability

**Sequence within Sprint 1 (Week 1):**

| Day | Task | Blocker resolved by Day |
|---|---|---|
| 1 | Polygon API key set up + smoke test (1 ticker, 1 month) | Sprint 0 owner action |
| 2 | `PointInTimeLoader` base class + tests (no fetcher yet, just contract) | Day 1 |
| 3 | `polygon_client.py` — get_aggs + reference + corp actions | Day 1 |
| 4 | `cache_ohlcv.py` Parquet cache + filelock | Day 3 |
| 5 | Cache hygiene + disk monitor + LRU exemption | Day 4 |
| 6-7 | S&P 500 bulk prefetch + verification | Day 5 |
| 8 | FRED + ALFRED 9+ series cache | parallel with prefetch |
| 9 | AAII + CNN F&G refresh scripts + workflow | parallel; verify Codespace allowlist |
| 10 | Polygon earnings cache | Day 6 |
| 11 | Polygon reference replacing yfinance.info | Day 6 |
| 12-14 | Edge case tests (weekend/holiday/pre-IPO/post-delist/partial cache) | Day 5 |
| 15-20 | Integration tests + freezegun PIT verification + bug fixes | Days 6-14 |

**Total: ~20 working days** (Sprint 1 baseline; +1 day if owner approves DEC-478 Polygon Stocks Developer requiring re-fetch with deeper history).

**Parallel-ability:**
- Sprint 1 ↔ Sprint 2 (engine bug fixes): **parallel** — Sprint 2 fixes operate on existing engine code, not on Sprint 1's new cache layer; coordination only at integration test (end of Sprint 2)
- Sprint 1 ↔ Sprint 4 (DEC-410 audit findings): partially parallel — Sprint 4 includes DEC-442 (yfinance demotion) which depends on Sprint 1's polygon_client; so Sprint 4 starts mid-Sprint-1
- Sprint 1 ↔ Sprint 3 (Portfolio class): **sequential** — Sprint 3 needs Sprint 1's PriceLoader; Sprint 3 starts after Sprint 1 Day 5

**Blockers (must resolve before Sprint 1 starts):**
1. Owner subscribes to Polygon (Sprint 0 action; tier per DEC-478 PROPOSED owner decision)
2. DEC-460 verification: does Polygon Stocks Starter cover PIT fundamentals? (Pre-Sprint-1 verification; result Pass 52 turn 133 = NEGATIVE)
3. DEC-461 conditional FMP subscription (now MANDATORY per DEC-460 verification negative)
4. Universe definition resolved: 482-CSV vs `historical_membership.csv` (DEC-477 PROPOSED owner approval)

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
- [ ] `historical_membership.csv` canonicalized; static 482-CSV deprecated with deprecation warning
- [ ] Sprint 1 PR merged to main; CI green; integration tests pass; cache integrity verified post-merge

## §3.6 Risks — what could go wrong specifically

**Risk R-1: Polygon rate limiting unexpected**
- Polygon Stocks Starter+ advertises "unlimited API calls" but rate-related throttles may exist for specific endpoints (e.g., bulk historical fetches)
- Mitigation: implement exponential backoff + 429-aware retry per DEC-260; verify rate behavior on Day 1 smoke test
- If hit during prefetch: spread bulk fetch across multiple sessions, throttle to ~5 req/s

**Risk R-2: Polygon historical depth shorter than expected**
- Stocks Starter = 5 years per polygon.io/pricing verification
- 5 years from May 2026 = May 2021 onwards; insufficient for DEC-109 walk-forward 5-year-train pre-2021 OOS folds
- Mitigation: DEC-478 PROPOSED owner decision to upgrade to Stocks Developer ($79/mo, 10 years) covering 2016-2026 for OOS folds 2021-2026
- If owner declines upgrade: walk-forward train window must reduce; this is a Sprint 7 architectural change

**Risk R-3: AAII or CNN F&G domains blocked by Codespace allowlist**
- Stage 1 lesson: Wikipedia was blocked
- Mitigation: Sprint 0 Day 1 verification — `curl https://www.aaii.com/...` and `https://production.dataviz.cnn.io/...` from Codespace; if fails, network settings update needed
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
- Quiver: not Sprint 1 (Sprint 4 onward)

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
| 303 | historical_membership.csv (PIT S&P 500 membership) | RESOLVED-DECIDED |
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
| 477 PROPOSED | historical_membership.csv canonical; deprecate 482-CSV | Awaits owner approval |
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

- "Reproduce Pass 32 hand-validated AAPL 2020 backtest using Sprint 1 cache; results match within 0.5% per DEC-218 numerical tolerance" — owner-witnessed demo

## §3.10 Data dependencies — what feeds in, where it comes from, what's downstream

**Inputs to Phase 0.A:**

| Input | Source | Sprint 0 verification |
|---|---|---|
| Polygon API key | Owner subscription | Required Day 1 |
| FRED API key | Free signup | Required Day 8 |
| `historical_membership.csv` | DEC-303 SEC filings + Wayback Machine archive | Pre-existing; verify in Sprint 0 |
| AAII URL accessible | https://www.aaii.com/sentimentsurvey | Sprint 0 verify in Codespace allowlist |
| CNN F&G URL accessible | https://production.dataviz.cnn.io/index/fearandgreed/graphdata | Sprint 0 verify |
| Owner-confirmed cache directory path | `/workspaces/stock-picks-app/data/cache/` | None |
| Codespace disk available | ≥ 32GB free | Sprint 0 verify (Stocks Starter 5-year cache ≈ 8-12GB) |

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
- [ ] Day 9: AAII + CNN F&G refresh scripts; verify Codespace allowlist
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
- [ ] Day 20: merge to main; ENGINEERING_REGISTER Sprint 1 → RESOLVED-IMPLEMENTED

## §3.12 Open issues — gaps from ADVERSARIAL_AUDIT relevant to this phase

From `ADVERSARIAL_AUDIT_PASS_52_TURN_132.md`, gaps directly affecting Phase 0.A:

- **GAP 1:** Polygon subscription timing — when does owner subscribe relative to other Sprint 0 actions?
  - Resolution: Sprint 0 Day 1 prerequisite; if owner delays, Sprint 1 Day 1 blocked
- **GAP 2:** API key procedure — storage, testing, what-if-down
  - Resolution: env var (`POLYGON_API_KEY`); smoke test Day 1; failover N/A in Sprint 1 (multi-vendor fallback Stage 4 per DEC-160)
- **GAP 13:** PIT loader class skeleton not specified
  - Resolution: §3.3 component diagram + §3.5 done criteria specifies ABC contract
- **GAP 14 (CRITICAL):** PIT loader edge cases not documented
  - Resolution: §3.1 deliverable #2 explicitly lists 5 edge cases (weekend/pre-IPO/post-delist/partial-cache); §3.5 done criteria gates them
- **GAP 15 (CRITICAL):** Two universes (482 vs `historical_membership.csv`)
  - Resolution: DEC-477 PROPOSED — `historical_membership.csv` canonical; static 482-CSV deprecated. Sprint 1 Day 19 deprecation warning added.
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
  - Resolution: DEC-478 PROPOSED owner decision; if Stocks Developer chosen, 10-year coverage 2016+

## §3.13 Decision history — what changed and why

**Pre-Pass-52 (legacy):**
- DEC-298 Pass ~30 — adopted `auto_adjust=False` to enable PIT-correct adjusted-on-demand
- DEC-040 Pass ~25 — established PointInTimeLoader as foundational pattern
- DEC-118 Pass ~28 — Tier 1 includes selected ETFs alongside S&P 500

**Pass 52 turn 130 (TradingAgents data audit):**
- DEC-460 — verify Polygon Stocks Starter covers PIT fundamentals (RESULT: NEGATIVE per turn 133 verification)
- DEC-461 — subscribe FMP if Polygon insufficient (RESULT: now MANDATORY)

**Pass 52 turn 133 (critical gaps resolution):**
- DEC-477 PROPOSED — `historical_membership.csv` canonical; supersedes static 482-CSV
- DEC-478 PROPOSED — Polygon tier upgrade decision pending owner approval (recommend Stocks Developer $79/mo + FMP $14-50/mo)
- DEC-479 PROPOSED — DEC-441 cost correction $30 → $29

**Why these supersession patterns:**
- Original assumption (Stocks Starter sufficient) was unverified — adversarial review (Pass 52 turn 132) caught the gap; verification (turn 133) confirmed insufficiency
- Pattern: assume nothing about external data sources; verify against actual API documentation; budget for higher tiers if needed

## §3.14 File / module structure

```
backtest/
├── data/
│   ├── __init__.py
│   ├── polygon_client.py            ★ NEW Sprint 1
│   ├── pit_loader.py                ★ NEW Sprint 1 (ABC base)
│   ├── cache_ohlcv.py               ★ NEW Sprint 1
│   ├── cache_monitor.py             ★ NEW Sprint 1 (disk + filelock)
│   ├── corporate_actions.py         ★ NEW Sprint 1
│   ├── fred_client.py               ★ NEW Sprint 1
│   ├── polygon_earnings.py          ★ NEW Sprint 1 (replaces yfinance_earnings)
│   ├── polygon_reference.py         ★ NEW Sprint 1 (replaces yfinance_info)
│   └── refresh/
│       ├── refresh_aaii.py          ★ NEW Sprint 1
│       └── refresh_cnn_fg.py        ★ NEW Sprint 1
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
    └── historical_membership.csv    ★ canonical (DEC-303 + DEC-477 PROPOSED)

.github/workflows/
├── refresh_aaii.yml                 ★ NEW Sprint 1
└── refresh_cnn_fg.yml               ★ NEW Sprint 1

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
- **Sprint 1 (Phase 0.A) must be complete** — Portfolio queries OHLCV via PriceLoader for `update_market_values`
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
- 60-day return correlation × N existing positions × M candidate tickers per day → O(N×M) computations per day × 250 days × 6 OOS folds
- Mitigation: cache correlation matrix per `as_of_date`; recompute incrementally only when positions change
- If still slow: parallel computation across positions using NumPy vectorization

**Risk R-4: Decimal arithmetic edge cases**
- `Decimal` for all money fields per DEC-218 0.5% tolerance — but Python `Decimal` arithmetic with floats can produce subtle errors (`Decimal('0.1') + 0.1` raises TypeError; mixing types breaks)
- Mitigation: explicit `Decimal()` conversion at every API boundary; lint rule prohibits mixing `Decimal` with `float` in same expression

**Risk R-5: Drawdown computation drift vs QuantStats**
- QuantStats has a specific drawdown algorithm; our computation must match within 0.1%
- Mitigation: §4.5 done criteria explicitly tests against QuantStats; if drift, debug to convergence before merge

**Risk R-6: Event log size at scale**
- 6 OOS folds × thousands of trades per fold = potentially 50K-500K event log entries; in-memory might exceed RAM
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

Phase 0.C produces **a stable backtest engine** by fixing 14 critical engine bugs that have accumulated through pre-Pass-52 development. These bugs cause anything from incorrect P&L on closed trades (missing exit method implementations) to silent test failures (NameError in close_trade) to circuit breakers that don't fire correctly. Without Sprint 2, the engine is unreliable; cube populated by an unreliable engine produces invalid verdict.

Concrete deliverables — the 14 critical engine bugs (per ADVERSARIAL_AUDIT GAP 26 enumeration):

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

Plus minor adjustments and dependency cleanups bundled with these fixes per BUG_REGISTER tier-A bugs.

## §5.2 Why — how this advances Stage 2 toward verdict

The engine is the executor that turns strategy signals into trades. If the engine has bugs, the trades it produces are wrong, the cube cells are populated with wrong outcomes, and the verdict is invalid no matter how good the data foundation (Sprint 1) or Portfolio class (Sprint 3) is.

Specifically:

- **Bug 1-3 (close_trade / ClosedTrade / exit_hybrid_50pct):** Closed trade records had inconsistent fields → cube cell population wrong → metrics wrong.
- **Bug 4 (trailing stop ATR refresh):** Trailing stops too tight or too loose → exit prices systematically biased → returns biased.
- **Bug 5-7 (circuit breakers Level 3/4/sequence):** During market stress periods (a meaningful fraction of OOS folds), backtest doesn't apply correct halt behavior → over-trading during 2008/2020/2022 stress → returns biased.
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
| 14-18 | Integration tests + acceptance reproduction |
| 19-20 | PR review + merge |

**Total: ~25.5-30.5d realistic** (some bugs more involved than 1d; e.g., circuit breaker Level 3/4 may take 2-3d each given 4-level orchestration logic).

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
- [ ] Day 4-6: Bugs 5/6/7 (circuit breakers)
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

**Sprint 1 (Day 8-10):**
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
│   ├── primitives.py          ★ NEW Sprint 1 (wraps smartmoneyconcepts library)
│   ├── multi_timeframe.py     ★ NEW Sprint 8 (combines 1D + 1H primitives)
│   ├── cache_smc.py           ★ NEW Sprint 1 (Parquet cache for primitives)
│   └── strategies/
│       ├── __init__.py
│       ├── fvg_fill.py        ★ NEW Sprint 8
│       ├── bos_direction.py   ★ NEW Sprint 8
│       ├── choch_reversal.py  ★ NEW Sprint 8
│       └── ob_zone_bounce.py  ★ NEW Sprint 8

vendor/
└── smartmoneyconcepts/        ★ Forked Sprint 1 (separate repo: jeetmehta1991/smartmoneyconcepts)
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

**Sprint 1 (Days 8-10):**
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

By Sprint 6 entry, the engine has been touched by 5 sprints of changes (Sprint 1 cache, Sprint 2 bug fixes, Sprint 3 Portfolio class, Sprint 4 audit findings, Sprint 5 universe management). Without catch-mechanism layers:

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
3. `backtest/statistics/walk_forward.py` — 5-year train / 1-year OOS / 6 folds per DEC-109
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
- Sprint 1 (cache layer)
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
- DEC-478 PROPOSED — Polygon tier upgrade decision (FMP availability for OurFundamentalsToolkit)
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
- 254K cells × 17+ metrics × 6 OOS folds → high memory; may exceed Codespace limits
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
- Sprint 1 cache + Sprint 4 financials (FMP) + Sprint 5 universe + Sprint 3 Portfolio
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

# PART 9 — PHASE 1B-α: DIMENSIONAL CUBE + DASHBOARDS (Sprint 7-8)

## §9.1 What — concrete deliverable in plain English

Phase 1B-α is the **Stage 2 verdict run plus owner-facing dashboards**. By end of this phase:

- The 8-dim cube (revised per DEC-471 PROPOSED from 17+ to 8 core dims, eliminated dims become trade-level metadata) is fully populated from walk-forward backtest trades across 6 OOS folds covering 2018-2026 (depth depends on Polygon tier per DEC-478)
- All cells have 5-Gate filter applied (DEC-426); each cell tagged PASS / FAIL_RR / INSUFFICIENT_SAMPLE / FAIL_STAT
- A/B framework verdict produced (3 arms compared via block bootstrap CIs per DEC-472 PROPOSED)
- 3 owner-facing dashboards rendered (DEC-199 Cube Explorer, DEC-200 ICT/SMC Audit, DEC-201 Agent Overlay Analysis) — interactive HTML or Streamlit
- Live decision lookup table generated from PASS cells (DEC-429)
- Stage 2 → 3 transition documentation auto-generated for owner review

This is the moment Stage 2 produces its actual deliverable: a populated cube + dashboards + verdict.

Concrete deliverables:

1. **Cube populator integration** (Sprint 7 already built; Sprint 7-8 transition runs at scale)
2. **Sprint 9 — full backtest run** — execute walk-forward across 6 OOS folds; 119 strategies × 509 Tier 1 + variable Tier 2/3; estimated wall time 37-40 hours
3. **Cube full population** — every trade attributed to its 8-dim cell; per-cell metrics computed
4. **5-Gate filter execution** — per-cell verdict assignment
5. **Live decision lookup table** — PASS cells rendered as queryable table for Stage 3
6. **A/B verdict** — block bootstrap CIs across 3 arms; per-regime comparison
7. **DEC-199 Cube Explorer dashboard** — owner can drill down: select strategy → regime → sector → cap → vol → tier → smart-money; see per-cell metrics
8. **DEC-200 ICT/SMC Audit dashboard** — focused review of SMC strategies; FVG/BOS/CHoCH/OB hit-rate by regime
9. **DEC-201 Agent Overlay Analysis dashboard** — A/B comparison visualizations: Arm Sharpe distributions, per-arm trade outcomes, agent reasoning logs (sampled), Risk veto frequency, Trader cross-check downgrade frequency
10. **Stage 2 → 3 transition packet** — auto-generated markdown summarizing: Stage 2 numeric gates met/missed, A/B verdict (justify agent overlay or not), top-N PASS strategies, cube coverage stats, recommendations

## §9.2 Why — how this advances Stage 2 toward verdict

Phase 1B-α IS the Stage 2 verdict. Without it:

- **No cube populated** → no validity assessment per strategy/regime/cell
- **No live decision lookup table** → Stage 3 paper trading has no rules to execute
- **No A/B verdict** → no answer to "should we deploy agent overlay or not?"
- **No dashboards** → owner can't review and approve Stage 2 → 3 transition

This is the moment the project either succeeds or fails Stage 2.

## §9.3 How — components, data flow, dependencies

**Component diagram:**

```
backtest/
├── runner/
│   ├── phase_1b_alpha.py          ★ NEW Sprint 9 (orchestrator)
│   ├── walk_forward_runner.py     ★ NEW Sprint 9 (per-fold execution)
│   └── parallel_fold_pool.py      ★ NEW Sprint 9 (multi-process fold pool)
├── cube/
│   ├── populator.py               (Sprint 7 deliverable)
│   ├── verdict.py                 (Sprint 7 deliverable)
│   └── live_decision_lookup.py    (Sprint 7 deliverable)
└── dashboards/
    ├── cube_explorer.py           ★ NEW (DEC-199) — Streamlit or interactive HTML
    ├── ict_smc_audit.py            ★ NEW (DEC-200)
    └── agent_overlay_analysis.py   ★ NEW (DEC-201)

reports/
├── stage_2_verdict_packet.md       ★ NEW Sprint 9 — auto-generated
├── stage_2_transition_decision.md  ★ NEW Sprint 9 — owner approval template
└── stage_2_dashboards/             ★ NEW Sprint 9 — exported HTML dashboards
```

**Data flow during Phase 1B-α run:**

```
Phase 1B-α orchestrator started
        │
        ▼
For each of 6 OOS folds (2018-19, 2019-20, 2020-21, 2021-22, 2022-23, 2023-24+):
        │
        ▼ launch fold worker process (parallelized)
        │
        ▼ Within fold:
        │   For each trading day in OOS year:
        │       Engine runs daily scan
        │       Strategies fire candidates
        │       Per-ticker risk gates applied
        │       Selective agent overlay (Sprint 7 toolkits + DEC-481 Option C2)
        │       A/B 3-arm split
        │       Per-arm Portfolio executes trades
        │       Trade outcomes logged with cube cell coordinates
        │
        ▼ End of fold:
        │   Trade outcomes streamed to fold's Parquet
        │
        ▼
All folds complete; orchestrator aggregates
        │
        ▼
cube/populator.py groups all trades by 8-dim cell
        │
        ▼
Per-cell metrics suite computed (sharpe, sortino, ROI, win rate, etc. per DEC-422)
        │
        ▼
verdict.py applies 5-Gate filter:
        - Gate 1: n ≥ 30 → INSUFFICIENT_SAMPLE if not
        - Gate 2: FDR q < 0.10 (hierarchical, DEC-470) → FAIL_STAT if not
        - Gate 3: PSR ≥ 0.95 → FAIL_STAT if not
        - Gate 4: t-stat ≥ 3.4 → FAIL_STAT if not
        - Gate 5: R:R ≥ 2.0 → FAIL_RR if not
        Verdict tagged
        │
        ▼
PASS cells extracted → live_decision_lookup.py table
        │
        ▼
A/B comparison: ab/comparison.py runs block bootstrap CIs
        Per-regime comparisons: each arm's Sharpe distribution per regime
        Per-strategy comparisons: each arm's per-strategy outcomes
        Aggregate verdict: Arm B (full) Sharpe vs Arm A (rules-only) Sharpe
        DEC-131 thresholds applied: ≥ 0.2 absolute OR ≥ 0.15 relative
        │
        ▼
Dashboards generate from cube + A/B output:
        DEC-199 Cube Explorer: drill-down filterable view
        DEC-200 ICT/SMC Audit: SMC strategy focus
        DEC-201 Agent Overlay: A/B visualization + agent reasoning samples
        │
        ▼
stage_2_verdict_packet.md auto-generated:
        Summary stats: total trades, total cells, PASS / FAIL_RR / INSUFF / FAIL_STAT counts
        Top-N PASS strategies with Sharpe / DD / R:R
        A/B verdict per regime
        Stage 2 numeric gates: pass/fail per DEC-269
        Recommendations: deploy / iterate / reject
        │
        ▼
Owner reviews; approves Stage 2 → 3 OR requests further iteration
```

**Dependencies:**
- Sprints 1-7 complete
- DEC-478 PROPOSED Polygon tier decided (cache depth determines OOS fold range)
- DEC-481 PROPOSED AgentGateConfig Option C2 approved
- DEC-469-475, 480 PROPOSED — methodology decisions approved

**Library dependencies:**
- All Sprint 7 deps
- `streamlit` or `plotly`+`dash` for dashboards
- `quantstats` for tear sheet generation in dashboards
- `multiprocessing` or `dask` for parallel fold execution

## §9.4 When

**Sequence within Phase 1B-α (Sprint 7-8 boundary; Sprint 9 actually runs it):**

| Day | Task |
|---|---|
| 1 | Phase 1B-α dry run setup: 1 fold, 10 candidates, end-to-end smoke |
| 2-3 | Resolve dry-run issues; tune parallelism + memory |
| 4 | DEC-199 Cube Explorer dashboard — first iteration |
| 5 | DEC-200 ICT/SMC Audit dashboard |
| 6 | DEC-201 Agent Overlay Analysis dashboard |
| 7-8 | Dashboard iteration based on owner feedback (small dry run) |
| 9 | Pre-flight check: Sprint 7 + 8 deliverables green; cache populated; budget tracker reset |
| 10 | **Phase 1B-α full run launch** |
| 10-12 | Wall time: 37-40 hours across 6 folds (parallel = 6-8h wall, serial = 40h+) |
| 13 | Cube populate + verdict + A/B comparison |
| 14 | Dashboard generation; live decision lookup table |
| 15 | stage_2_verdict_packet.md auto-gen + owner review session |

**Total: ~15 days from dry-run to verdict packet.**

**Compute estimate (per ADVERSARIAL_AUDIT B6 resolution):**
- 6 folds × 250 days × 509 Tier 1 + variable Tier 2/3 ≈ 800K ticker-days
- Strategy fires + risk gates + agent overlay (selective): est. ~5-8h wall per fold serial
- 6 folds parallel on 8-core machine: ~6-10h wall total
- Cube populate + verdict + dashboards: additional ~6-8h
- **Total: ~12-18h wall time on Codespace 8-core; budget 24h with safety margin**

(Earlier 37-40h estimate was for Stocks Starter 5yr cache; Stocks Developer 10yr cache = more historical data but still manageable parallelism.)

**Blockers:**
- Sprint 7 PR merged
- Sprint 8 strategy categories complete (all 109-119 strategies fire in run)
- Cache fully populated (Sprint 1 prefetch)
- 13 PROPOSED DECs approved (DEC-469 through DEC-481)
- Owner $300 API budget release

**Parallel-ability:**
- Phase 1B-α run is sequential and resource-intensive
- During the run, no other development should consume Codespace compute

## §9.5 Done criteria

- [ ] Phase 1B-α dry run smoke test successful (1 fold, 10 candidates)
- [ ] Full Phase 1B-α run completes without crashes
- [ ] All 6 OOS folds produce trade outcomes (no fold left with empty Parquet)
- [ ] Cube fully populated; cell count > 0 across all 8 dimensions
- [ ] Per-cell metrics suite computed for all populated cells
- [ ] 5-Gate filter applied; verdict tagged on every cell
- [ ] PASS cells > 0 (cube didn't reject everything)
- [ ] Live decision lookup table populated; queryable
- [ ] A/B comparison produced; per-regime verdicts assigned
- [ ] DEC-199, 200, 201 dashboards rendered and viewable
- [ ] stage_2_verdict_packet.md generated with all required sections
- [ ] Owner reviews dashboards + packet; approves OR rejects Stage 2 → 3 transition
- [ ] If approved: live decision lookup table committed; transition documentation merged
- [ ] If rejected: gap analysis produced; iteration plan drafted

## §9.6 Risks

**Risk R-1: Compute exceeds estimate**
- 6 folds × 800K ticker-days could surprise with longer-than-expected per-trade computation if agents called too often
- Mitigation: budget tracker enforces $300 cap (DEC-059); selective agent overlay (top candidates only); fold parallelism throttled if memory pressure

**Risk R-2: Cube too sparse**
- 254K cells × 30-trade-min sample × 6 folds requires substantial trade volume; if reality is < expected, INSUFFICIENT_SAMPLE rate dominates
- Mitigation: DEC-471 PROPOSED already reduced from 17+ to 8 dims; if still sparse, accept some cells suspended; iterate

**Risk R-3: A/B verdict inconclusive**
- Block bootstrap CIs may overlap if sample insufficient
- Mitigation: per-regime verdicts may be stronger than aggregate; document inconclusive verdicts as data, not failure

**Risk R-4: Dashboard rendering slow**
- Streamlit / Plotly with 250K-cell cube + thousands of trades = slow render
- Mitigation: data aggregation upstream; cube_explorer caches summaries; drill-down lazy-loads

**Risk R-5: Verdict invalidates Stage 2 entirely**
- Sharpe < 1.0, max DD > 25%, win rate < 50%, A/B null, PASS cells < threshold → Stage 2 fails
- Mitigation: §9.10 Open issues addresses what-if; Part 13.3 covers Stage 2 fail recovery
- Owner decides: iterate (more strategies, different methodology) OR pause project

**Risk R-6: Owner rejects dashboards as confusing**
- Dashboards may not match owner intuition; redesign needed
- Mitigation: dry-run at small scale (Days 4-8); incorporate feedback before full run

**Risk R-7: Live decision lookup table format friction with Stage 3**
- Stage 3 paper trading must consume the table; format must be operational
- Mitigation: Stage 3 design starts at end of Phase 1B-α run; table format reviewed in transition packet

## §9.7 Cost

**Engineering effort:** ~15d for orchestration + dashboards + verdict packet (Sprint 9)
**Compute cost (one-time Phase 1B-α run):**
- Codespace 8-core hours: ~12-18h wall time included in Codespace subscription
- Anthropic API for agent calls during run: $75-225 per DEC-472 PROPOSED corrected estimate; under $300 cap (DEC-059)
- Total compute: ~$75-225

**Subscription costs already-paid (Sprint 1-7):**
- Polygon $29-79/mo
- FMP $14-50/mo
- Quiver $50-100/mo
- Ortex $50-100/mo
- Total: $143-329/mo (revised per DEC-478)

## §9.8 Decisions in scope

| DEC | Title |
|---|---|
| 029 | Stage 2 → 3 transition criteria |
| 109 | Walk-forward 5y/1y/6 folds |
| 131 | A/B Sharpe ≥ 0.2 absolute or ≥ 0.15 relative |
| 199 | Cube Explorer dashboard |
| 200 | ICT/SMC Audit dashboard |
| 201 | Agent Overlay Analysis dashboard |
| 269 | Stage 2 numeric gates (Sharpe/DD/win rate/divergence/A/B) |
| 422 | Cube 17+ dimensions (revised to 8 per DEC-471) |
| 426 | 5-Gate verdict filter |
| 429 | Live decision lookup |
| 469-475 PROPOSED | Statistical + A/B methodology corrections |

## §9.9 Test approach

**Pre-run dry test:**
- 1 fold × 10 candidates × 3 arms × 1 strategy class
- Verify end-to-end pipeline succeeds before launching full run

**Run monitoring:**
- Real-time progress dashboard: folds completed, trades executed, API spend
- Auto-halt if API spend > $290 (10% safety margin under $300 cap)

**Post-run validation:**
- Cube cell count sanity check (> 0 PASS cells; not all INSUFFICIENT)
- Sample-trace 5 PASS cells; manually verify trade outcomes match cell metrics
- Differential check: rules-only arm vs Sprint 7 unit test expected output

**Acceptance:**
- Owner reviews packet + 3 dashboards; declares Stage 2 → 3 GO or NO-GO

## §9.10 Data dependencies

**Inputs:** All Sprint 1-8 deliverables
**Outputs:**
- Populated cube (Parquet)
- Live decision lookup table (Parquet + JSON for Stage 3 consumption)
- 3 dashboard HTML/Streamlit apps
- stage_2_verdict_packet.md
- DEC-189 reflection log entries (final populated)

**Downstream consumer:** Stage 3 paper trading

## §9.11 Operational checklist

(See §9.4 day-by-day.)

## §9.12 Open issues — gaps from ADVERSARIAL_AUDIT

- **GAP B6 (CRITICAL — Blocker):** Cube cell sparsity / compute cost — RESOLVED via DEC-471 PROPOSED 8-dim reduction + compute estimate
- **GAP 168:** Phase 1B-α budget owner-controlled — addressed via DEC-059 $300 cap + budget tracker auto-halt
- **GAP 169:** Dashboard format unspecified — §9.3 specifies Streamlit or interactive HTML; flexibility per owner preference

**What if Stage 2 fails:**
- Per Part 13.3 (Stage 2 → 3 if rejected): owner reviews packet; gap analysis identifies which strategies/regimes failed; iteration plan drafted
- Iterate options: (a) more strategies, (b) different statistical methodology, (c) different agent prompts, (d) different cube dimensions, (e) more historical data (Polygon tier upgrade)
- Owner approves iteration scope; new Phase 1B-α planned

## §9.13 Decision history

- DEC-199-201 (Pass ~30): dashboard cluster
- DEC-269 (Pass ~35): Stage 2 numeric gates
- DEC-422-429 (Pass ~42): cube + verdict + lookup cluster
- DEC-469-475 PROPOSED (Pass 52 turn 133): methodology corrections

## §9.14 File / module structure

(See §9.3 component diagram.)

## §9.15 Example walkthrough

**Scenario:** Phase 1B-α run completes. Owner opens DEC-199 Cube Explorer.

**Step 1:** Dashboard loads showing summary:
```
Cube cells populated: 47,328 of 254,016 max (18.6%)
PASS: 312
FAIL_RR: 1,245
INSUFFICIENT_SAMPLE: 38,907
FAIL_STAT: 6,864
```

**Step 2:** Owner clicks "Drill down by strategy" → selects "ICT_FVG_Long_Tier1":
- Cells where this strategy fires: 142
- PASS: 23
- INSUFFICIENT: 87
- FAIL_RR: 18
- FAIL_STAT: 14

**Step 3:** Owner filters PASS cells by regime → "volatile":
- 11 PASS cells in volatile regime
- Best cell (Tech / mega / high-vol / smart-money-yes / Tier 1): Sharpe 1.8, R:R 2.4, win rate 62%, n=47

**Step 4:** Owner switches to DEC-201 Agent Overlay Analysis:
```
Aggregate A/B verdict:
  Arm A (Rules-only): Sharpe 1.05 ± 0.18 (95% CI)
  Arm B (Full-with-veto): Sharpe 1.32 ± 0.21 (95% CI)
  Arm C (No-Risk): Sharpe 1.18 ± 0.20 (95% CI)
  
Sharpe delta B - A = +0.27 (CI [0.09, 0.45]) — passes DEC-131 ≥ 0.2 absolute
Risk veto fired 18% of candidates; downstream Sharpe impact +0.14
Trader cross-check downgraded 12% from HIGH→MEDIUM; no Sharpe impact (neutral)
```

**Step 5:** stage_2_verdict_packet.md states:
> Stage 2 numeric gates: PASS (Sharpe 1.32 > 1.0; DD -18% < 25%; win rate 56% > 50%; A/B clear +0.27)
> 
> Recommendation: Stage 2 → 3 transition APPROVED contingent on owner review of 312 PASS cells.
> 
> Top-N PASS strategies (by aggregate Sharpe):
> 1. ICT_FVG_Long_Tier1 — Sharpe 1.65
> 2. RSI_Mean_Reversion_30_70 — Sharpe 1.48
> 3. Earnings_Drift_Post — Sharpe 1.42
> ...

**Step 6:** Owner approves Stage 2 → 3 transition. Live decision lookup table merged. Stage 3 paper trading planning begins.

**Without Phase 1B-α:** No cube, no verdict, no dashboards, no go/no-go decision. Stage 2 has no terminal output.

---

# PART 10 — PHASE 1C+: STRATEGY CATEGORIES EXPANSION (Sprint 8)

## §10.1 What — concrete deliverable in plain English

Phase 1C+ produces the **strategy roster expansion** that takes the strategy count from baseline 60 (Layer 1) up to ~109-119 (Layer 1+2+3+4). This sprint runs in parallel with Sprint 7 toolkit work; deliverables enter the cube via the Phase 1B-α run (Part 9).

Concrete deliverables:

**Layer 3A — 8 chart-pattern strategies (DEC-355-362):**
1. **DEC-355 — Head and Shoulders** (top + bottom; bearish + bullish reversal)
2. **DEC-356 — Double Top / Double Bottom**
3. **DEC-357 — Triple Top / Triple Bottom**
4. **DEC-358 — Ascending Triangle / Descending Triangle / Symmetrical Triangle**
5. **DEC-359 — Cup and Handle**
6. **DEC-360 — Flag and Pennant**
7. **DEC-361 — Wedge (Rising / Falling)**
8. **DEC-362 — Channel (Ascending / Descending / Horizontal)**

Each has:
- Detection algorithm (pattern recognition on OHLCV; uses `smartmoneyconcepts` + custom pattern detection)
- Entry trigger (e.g., breakout above neckline for H&S, with volume confirmation)
- Stop placement (e.g., below right shoulder for H&S top)
- Target (e.g., measured move from pattern height)
- Confidence score (0-1; pattern quality)

**Layer 3B — 5 strategy categories (DEC-367-371):**
9. **DEC-367 — Calendar Effects** (turn-of-month, day-of-week, FOMC week, post-CPI release)
10. **DEC-368 — Index Rebalance** (S&P 500 add/drop trades; Russell rebalance; per DEC-377)
11. **DEC-369 — Within-Category Momentum** (best-in-sector momentum; long sector leader, short laggard)
12. **DEC-370 — Earnings Quality Surprise** (large EPS surprise + analyst estimate revision; per DEC-256/444 Polygon earnings)
13. **DEC-371 — Insider Cluster Trade** (top-N insiders all buying within 30d; per DEC-450 Quiver paid)

**Layer 4 — Exit method variants (DEC-432/433):**
14-22. **9 new exit method variants:**
- chandelier (DEC-432) — trailing ATR-based on highest high
- psar (DEC-433) — Parabolic SAR exit
- supertrend (DEC-433) — supertrend trailing
- volatility_regime (DEC-433) — exit when vol regime changes
- volume_climax (DEC-433) — exit on extreme volume bar
- rsi_extreme (DEC-433) — exit on RSI > 80 long, RSI < 20 short
- partial_scaleout (DEC-433) — sell partial at 1R, hold rest to higher target
- kelly_target (DEC-433) — exit at Kelly-criterion-derived target
- macro_event (DEC-433) — exit before known macro event (FOMC/NFP)

**Layer 4 — AEP breaker (DEC-435):**
23. **AEP breaker strategy** — Aggregate Equity Position breaker; if portfolio drawdown crosses threshold, all-positions exit

**Plus BUG-111 architectural decision (deferred from Pass 52):**
- 25 existing breakout strategies in `screener.py` may want break-and-retest variants
- Option A — shared retest primitive (~5-10d) recommended
- Option B — per-strategy variants (~25-30d)
- Decision deferred to Sprint 8 implementation start

## §10.2 Why — how this advances Stage 2 toward verdict

Strategy roster expansion is what gives the cube **breadth of signals to test**. Without Layer 3+4:
- Only 60 strategies in cube → cube under-explores signal space
- Chart pattern strategies absent → pattern-based traders' signals not represented
- Calendar / index-rebalance / earnings-quality / insider-cluster strategies absent → category-specific edges untested
- Exit method variants absent → exit dynamics unexplored; some strategies may have asymmetric edge based on exit
- AEP breaker absent → aggregate risk control untested at portfolio level

Adversarial GAP 130 noted: 119 strategies × cube = math feasibility (post-DEC-471 reduction). Without 119 strategies, cube is sparse and verdict is shallow.

## §10.3 How — components, data flow, dependencies

**Component diagram:**

```
backtest/
├── strategies/
│   ├── chart_patterns/                  ★ NEW Sprint 8 (DEC-355-362)
│   │   ├── head_and_shoulders.py
│   │   ├── double_top_bottom.py
│   │   ├── triple_top_bottom.py
│   │   ├── triangles.py
│   │   ├── cup_and_handle.py
│   │   ├── flag_pennant.py
│   │   ├── wedge.py
│   │   └── channel.py
│   ├── categories/                       ★ NEW Sprint 8 (DEC-367-371)
│   │   ├── calendar_effects.py
│   │   ├── index_rebalance.py
│   │   ├── within_category_momentum.py
│   │   ├── earnings_quality_surprise.py
│   │   └── insider_cluster_trade.py
│   ├── ict_smc/                          (Phase 0.D Sprint 1 + here Sprint 8)
│   │   ├── fvg_fill.py
│   │   ├── bos_direction.py
│   │   ├── choch_reversal.py
│   │   └── ob_zone_bounce.py
│   ├── breakout_with_retest/             ★ NEW Sprint 8 (BUG-111 Option A)
│   │   ├── retest_primitive.py
│   │   └── (existing 25 breakouts adopt primitive)
│   └── aep_breaker.py                    ★ NEW Sprint 8 (DEC-435)

backtest/engine/exit_methods/             ⊠ Sprint 8 EXTENDED (DEC-432/433)
├── chandelier.py                         ★ NEW
├── psar.py                               ★ NEW
├── supertrend.py                         ★ NEW
├── volatility_regime.py                  ★ NEW
├── volume_climax.py                      ★ NEW (also in Sprint 2 Bug 12)
├── rsi_extreme.py                        ★ NEW (also in Sprint 2 Bug 14)
├── partial_scaleout.py                   ★ NEW
├── kelly_target.py                       ★ NEW
└── macro_event.py                        ★ NEW
```

**Data flow:**

```
OHLCV cache (Sprint 1) + corp actions
        │
        ▼
chart_pattern detection algorithms (Layer 3A)
        - Compute swing highs/lows
        - Detect H&S formation
        - Score pattern quality
        │
        ▼ Pattern detected on AAPL 2022-06-15
        │
        ▼
Strategy `Head_and_Shoulders_Top_Tier1` fires → ENTRY SHORT signal
        │
        ▼
Layer 3B categories also produce candidates (calendar / index rebalance / earnings / insider cluster)
        │
        ▼
All candidates feed into engine; risk gates + agent overlay (selective) + A/B
        │
        ▼
Trade outcomes recorded with cube cell coordinates including exit method (Layer 4 variants tested)
        │
        ▼
Cube populates with broader signal coverage
```

**Dependencies:**
- Sprint 1 (OHLCV + reference + corp actions)
- Sprint 4 (Quiver paid, FMP financials, Polygon earnings)
- Phase 0.D (smartmoneyconcepts library) for SMC strategies
- Sprint 2 (engine bug fixes — exit methods variants 12, 14 already added in Sprint 2; here Sprint 8 adds the rest)

**Library dependencies:**
- `pandas-ta` (Bollinger / RSI / etc.)
- `scipy.signal` (peak finding for swing high/low detection)
- `smartmoneyconcepts` (forked Phase 0.D)

## §10.4 When

**Sequence within Sprint 8 (~37-55d):**

| Week | Focus |
|---|---|
| Week 1 | BUG-111 architectural decision; pick Option A (shared retest primitive) |
| Week 1 | Build retest primitive; refactor 25 existing breakouts to use it |
| Week 2-3 | Layer 3A: 8 chart pattern strategies (3-5d each; parallel-able) |
| Week 4 | Layer 3B: calendar effects + index rebalance |
| Week 5 | Layer 3B: within-category momentum + earnings quality + insider cluster |
| Week 6 | Layer 4: 7 exit method variants (chandelier, psar, supertrend, volatility_regime, partial_scaleout, kelly_target, macro_event) |
| Week 7 | Layer 4: AEP breaker (DEC-435) |
| Week 8 | Multi-timeframe SMC strategies (Phase 0.D Sprint 8 component) |
| Week 9-10 | Integration tests + acceptance + PR review |

**Total: ~37-55d realistic.**

**Parallel-ability:**
- Sprint 8 ↔ Sprint 7: **parallel** — Sprint 8 strategies are independent of Sprint 7 toolkit work
- Sprint 8 ↔ Phase 1B-α run: **sequential** — Sprint 8 must complete before Phase 1B-α can include these strategies in cube

## §10.5 Done criteria

- [ ] BUG-111 decision made; Option A implemented (or B if owner chooses)
- [ ] All 25 breakouts use shared retest primitive (Option A) OR have own variants (Option B)
- [ ] All 8 chart pattern strategies implemented; pattern detection unit-tested with synthetic + real examples
- [ ] All 5 strategy categories implemented; can fire on Tier 1/2/3 universe
- [ ] All 9 exit method variants available; strategies that reference them execute correctly
- [ ] AEP breaker implemented; threshold parameter (e.g., portfolio DD -15%) triggers all-position exit
- [ ] 4 SMC strategies implemented (FVG fill, BOS direction, CHoCH reversal, OB zone bounce)
- [ ] Multi-timeframe regime confirmation per DEC-345 operational
- [ ] Strategy roster count = 109-119 (depends on retest primitive adoption — Option A counts breakouts as 25 with retest primitive variant; Option B counts as 50)
- [ ] STRATEGY_REGISTER.md updated with all new strategies
- [ ] CI green; integration tests pass

## §10.6 Risks

**Risk R-1: Pattern detection false positives**
- H&S detection on small swings → too many candidates → noise
- Mitigation: minimum swing size threshold; pattern quality scoring; manual validation on 5-10 examples per pattern

**Risk R-2: BUG-111 architectural choice wrong**
- Owner might prefer Option B (per-strategy variants) for testing flexibility; Option A simpler
- Mitigation: DEC TBD owner decision Sprint 8 Week 1; documented analysis of trade-offs

**Risk R-3: Calendar effects spurious in walk-forward**
- Calendar strategies often have small Sharpe; walk-forward may not validate
- Mitigation: accept that some Layer 3B strategies may FAIL_STAT; document rather than retire pre-emptively

**Risk R-4: Index rebalance dates need historical accuracy**
- DEC-377 requires PIT-correct S&P/Russell rebalance dates
- Mitigation: source from public archives (Wikipedia / S&P press releases); manually validate sample

**Risk R-5: Insider cluster strategy data freshness**
- DEC-450 Quiver paid endpoint; Form 4 filings can be late
- Mitigation: use filing_date not transaction_date for PIT correctness; document lag in LIMITATIONS_CAVEATS_ASSUMPTIONS.md

**Risk R-6: AEP breaker over-trades**
- Threshold tuning (-15% portfolio DD) may trigger too often or too rarely
- Mitigation: Phase 1B-α verdict tests multiple thresholds; owner approves final per backtest

**Risk R-7: Multi-timeframe strategy compute cost**
- Daily + hourly + minute timeframes per ticker per day → high compute
- Mitigation: cache intermediate timeframe aggregates; precompute multi-TF regime at Sprint 8 setup

## §10.7 Cost

**Engineering effort:** ~37-55d
**Subscription cost:** $0 incremental (uses Sprint 1-4 data sources)

## §10.8 Decisions in scope

| DEC | Title |
|---|---|
| 067 | 17 exit methods canonical |
| 075 | Exit classification (signal vs time) |
| 256 | Polygon earnings cache |
| 332 | Smart money composite |
| 345 | Multi-timeframe regime confirmation |
| 348 | Event suppression asymmetric |
| 355-362 | 8 chart pattern strategies |
| 367-371 | 5 strategy categories |
| 377 | Index rebalance PIT historical dates |
| 432 | Exit method variants additive |
| 433 | 9 new exit method variant set |
| 435 | AEP breaker strategy |
| 444 | Polygon earnings replacing yfinance |
| 450 | Quiver paid endpoint expansion |
| BUG-111 | Break-and-retest architecture (Option A or B) |

## §10.9 Test approach

- Unit tests per pattern detection algorithm (synthetic OHLCV + real examples)
- Integration tests: each strategy fires on Tier 1 universe; produces expected candidate count
- Acceptance: owner reviews 3-5 candidates per pattern manually; confirms detection quality

## §10.10 Data dependencies

**Inputs:** Sprint 1 OHLCV + Sprint 4 Quiver/FMP/Polygon earnings + Phase 0.D SMC primitives
**Outputs:** Strategy roster expansion → Phase 1B-α cube broader signal coverage

## §10.11 Operational checklist

(See §10.4 week-by-week.)

## §10.12 Open issues — gaps from ADVERSARIAL_AUDIT

- **GAP 56-58:** Sprint 8 strategy variant counts unclear (60 baseline → 109-119)
  - Resolution: §10.1 enumerates explicit additions; total reconciled
- **GAP 81:** BUG-111 break-and-retest unresolved
  - Resolution: §10.4 Week 1 explicit decision point; recommendation Option A
- **GAP 152, 153:** Pattern detection libraries / algorithms specified
  - Resolution: §10.3 component diagram + scipy.signal + smartmoneyconcepts integration

## §10.13 Decision history

- DEC-067 (Pass ~25): 17 exit methods baseline canonical
- DEC-345 (Pass ~38): multi-timeframe regime
- DEC-355-362 (Pass ~42): 8 chart patterns
- DEC-367-371 (Pass ~45): 5 categories
- DEC-432-435 (Pass 51): exit variants + AEP
- BUG-111 (Pass 52 logged; Sprint 8 resolves)

## §10.14 File / module structure

(See §10.3 component diagram.)

## §10.15 Example walkthrough

**Scenario:** AAPL on 2022-08-15 forms a Head & Shoulders Top pattern.

**Step 1:** `head_and_shoulders.py` runs on AAPL daily OHLCV:
- Identifies left shoulder (peak 2022-06-12, $148)
- Identifies head (peak 2022-07-08, $159)
- Identifies right shoulder (peak 2022-08-10, $151)
- Identifies neckline (low 2022-06-25, $137 + low 2022-07-22, $138; trendline)
- Pattern quality score: 0.78 (good symmetry, volume profile decreasing through pattern)
- Confirmation trigger: close below neckline ~$135

**Step 2:** 2022-08-18, AAPL closes at $133 → confirms breakdown:
- Strategy `Head_and_Shoulders_Top_Tier1` fires SHORT signal at $133
- Stop: above right shoulder $151
- Target: measured move = head - neckline = $159 - $137 = $22 → target $135 - $22 = $113

**Step 3:** Engine + agent overlay process (per Part 8 walkthrough):
- Risk gates clear
- Agent overlay (Sprint 7): Market Analyst notes pattern via OurTechnicalToolkit.get_chart_pattern()
- Bull/Bear debate factors pattern + earnings calendar + macro context
- PM final rating: Underweight → SHORT entry candidate, MEDIUM tier
- DEC-481 Option C2 gate: PM Underweight → REJECT for long; SHORT entry MEDIUM tier (3% short sizing)

**Step 4:** SHORT executed at $133, 100 shares. Borrow cost daily accrual.

**Step 5:** 2022-09-30, AAPL at $115 — partial target. Trade closes via `partial_scaleout` exit method (Layer 4 variant): 50 shares @ $115, hold 50 shares to lower target.

**Step 6:** 2022-10-15, AAPL at $113 — full target. Remaining 50 shares closed.

**Step 7:** ClosedTrade logged with cube cell coordinates:
```
strategy='Head_and_Shoulders_Top_Tier1'
regime='volatile' (high VIX)
sector='Technology'
cap_band='mega'
vol_band='high'
hold_band='long' (60 days)
tier=1
smart_money_signal=False
```

**Step 8:** Cube cell `(H&S_Top_Tier1, volatile, Tech, mega, high, long, T1, no_SM)` populated; aggregates 23 trades; per-cell metrics computed.

**Step 9:** 5-Gate filter: n=23 < 30 → INSUFFICIENT_SAMPLE → cell suspended pending more trades.

**Without Sprint 8:** Strategy `Head_and_Shoulders_Top_Tier1` doesn't exist → no signal → no trade → cell empty → cube under-populated.

---

# PART 11 — SPRINT 4: DEC-410 API AUDIT FINDINGS (Parallel)

## §11.1 What — concrete deliverable in plain English

Sprint 4 is **the cleanup sprint for the data layer** based on findings from DEC-410 API audit (17-API comprehensive review conducted Pass 51). The audit identified ~15 specific issues with our data sources — yfinance unreliability, missing Polygon adoption, conditional FMP need, Quiver paid endpoint expansion, Finnhub/OpenBB/AV deprecation candidates. Sprint 4 resolves these findings.

This sprint runs **in parallel with Sprint 3** (Portfolio class) starting Week 2-3 of overall implementation timeline. It's a "cleanup" sprint — no new strategies or methodology; just data layer hygiene to prepare for Sprint 7 toolkit work.

Concrete deliverables (15 sub-decisions per ENGINEERING_REGISTER):

1. **DEC-441 verification** — confirm Polygon Stocks Starter cost = $29 (not $30 originally stated); update DEC-479 PROPOSED to reflect; this depends on DEC-478 PROPOSED tier choice
2. **DEC-442 — yfinance demoted to fallback** — yfinance is removed from production paths; only used for fallback comparisons; deprecation warnings added; removed entirely from Sprint 7 toolkit work
3. **DEC-443 — Polygon reference data replaces yfinance.info** — sector / market cap / exchange / listing dates fetched from Polygon Reference; resolves BUG-218 (yfinance.info returns CURRENT not as_of)
4. **DEC-444 — Polygon earnings replaces yfinance earnings** — earnings dates + EPS actuals + estimates from Polygon (cached per Sprint 1 deliverable); yfinance earnings deprecated
5. **DEC-445 — Polygon news replaces Finnhub** — news endpoint from Polygon; Finnhub deprecated per DEC-440
6. **DEC-446 — Polygon technical indicators replace pandas-ta for selected indicators** — Polygon offers RSI/MACD/SMA via API; use Polygon for Tier 1 universe; pandas-ta for Tier 2/3 (cost optimization)
7. **DEC-447 — Polygon options data evaluation** — DEC-145 deferred-implementation; Sprint 4 evaluates Polygon options API; document findings
8. **DEC-448 — FRED expansion to 9+ series** — already in Sprint 1 deliverables; here Sprint 4 confirms ALFRED PIT validation across all 9 series
9. **DEC-449 — FRED expansion fully wired into agent toolkits** — Sprint 4 verifies FRED data flows into OurFundamentalsToolkit / OurNewsToolkit (Sprint 7) macro signals
10. **DEC-450 — Quiver paid endpoint expansion (insider, congressional, 13F)** — full subscription ~$50-100/mo; all paid endpoints prefetched; gov_contracts date filter validated
11. **DEC-451 — Quiver retail flow / wallstreet bets (free) decommissioned** — free Quiver endpoints unreliable; rely on paid only
12. **DEC-453 — Finnhub fully decommissioned** — remove all Finnhub code paths; deprecation warnings; CI lint blocks new imports
13. **DEC-454 — OpenBB fully decommissioned** — same as Finnhub; OpenBB removed
14. **DEC-455 — Alpha Vantage fully decommissioned** — Stage 1 legacy; Sprint 4 removes all production code paths; CI lint blocks new imports
15. **DEC-456 — TradingView library removed** — never adopted; cleanup
16. **DEC-461 (NEW; conditional)** — FMP subscription becomes MANDATORY (DEC-460 verification negative confirmed Pass 52 turn 133)
17. **DEC-468 — Ortex wired** — confirmed in Sprint 7 explicitly; Sprint 4 prepares the data path

(15 sub-decisions per ENGINEERING_REGISTER count of "DEC-442/443/444/445/446/447/448/449/450/451/453/454/455/456 + DEC-441 verification" = 15.)

## §11.2 Why — how this advances Stage 2 toward verdict

Sprint 4 doesn't add new strategies or methodology; it **cleans up the data layer so Sprint 7 toolkit work doesn't accumulate technical debt**. Specifically:

- **Sprint 7 toolkit OurFundamentalsToolkit (DEC-463)** — needs FMP for transcripts + analyst estimates + financials (Polygon Stocks Starter shortfall confirmed). Without DEC-461 FMP subscription, OurFundamentalsToolkit is degraded
- **Sprint 7 toolkit OurNewsToolkit (DEC-464)** — needs Polygon news (DEC-445) replacing Finnhub
- **Sprint 7 toolkit OurTechnicalToolkit (DEC-462)** — needs Polygon technical indicators or pandas-ta (DEC-446)
- **Phase 1B-α run** — needs all data sources cached, deprecated APIs removed, deterministic data layer
- **PIT correctness** — yfinance.info CURRENT-only contaminated multiple downstream queries; DEC-443 closes this contamination vector

Sprint 4 is a precondition for Sprint 7 effectiveness.

## §11.3 How — components, data flow, dependencies

**Component-level changes:**

```
backtest/data/
├── polygon_news.py            ★ NEW Sprint 4 (DEC-445)
├── polygon_technicals.py      ★ NEW Sprint 4 (DEC-446) — for Tier 1
├── polygon_options.py         ★ NEW Sprint 4 (DEC-447) — evaluation only
├── fmp_client.py              ★ NEW Sprint 4 (DEC-461 mandatory)
├── fmp_financials.py          ★ NEW Sprint 4 (PIT-correct fundamentals)
├── fmp_transcripts.py         ★ NEW Sprint 4 (earnings call transcripts)
├── fmp_analyst_estimates.py   ★ NEW Sprint 4
├── quiver_paid_client.py      ⊠ EXTEND Sprint 4 (DEC-450)
├── _legacy/                    ⊠ Sprint 4 SCAFFOLD
│   ├── yfinance_info.py        (replaced by polygon_reference.py)
│   ├── yfinance_earnings.py    (replaced by polygon_earnings.py)
│   ├── finnhub_news.py         (replaced by polygon_news.py)
│   ├── openbb_*.py             (decommissioned)
│   ├── alpha_vantage_*.py      (decommissioned)
│   └── tradingview_*.py        (decommissioned)

requirements.txt               ⊠ UPDATED Sprint 4
    - yfinance>=...             # demoted but retained for fallback
    + financial-modeling-prep
    + (Polygon already in)
    - finnhub-python              # REMOVED
    - openbb                      # REMOVED
    - alpha-vantage              # REMOVED

.github/workflows/lint.yml      ⊠ UPDATED Sprint 4 — block import of decommissioned libs
```

**Data flow during a Sprint 7+ toolkit query (example — fundamentals):**

```
OurFundamentalsToolkit.get_financials("AAPL", "2022-06-15")
        │
        ▼
fmp_financials.fetch_financial_statements("AAPL", as_of="2022-06-15")
        │
        ▼ checks cache_fundamentals.parquet
        │
        ├── HIT → return rows where filing_date ≤ "2022-06-15"
        │
        └── MISS → fmp_client.get_income_statement(...)
                  fmp_client.get_balance_sheet(...)
                  fmp_client.get_cash_flow(...)
                  → cache, return PIT-sliced
```

**Dependencies:**
- Sprint 1 substantially complete (Polygon foundation)
- Sprint 3 mid-point (Portfolio class for context if needed; not strict)
- DEC-478 PROPOSED Polygon tier choice
- DEC-461 PROPOSED FMP subscription
- DEC-468 Ortex wiring path

## §11.4 When

**Sequence within Sprint 4 (~41.75-54.25d, parallel with Sprints 3+5+6):**

| Week | Focus |
|---|---|
| Week 1 | DEC-461 FMP subscription + smoke test; FMP financials cache |
| Week 1-2 | DEC-450 Quiver paid endpoint expansion + cache extension |
| Week 2 | DEC-443 Polygon reference replacing yfinance.info wired into engine |
| Week 2-3 | DEC-444 Polygon earnings replacing yfinance earnings |
| Week 3 | DEC-445 Polygon news replacing Finnhub |
| Week 4 | DEC-446 Polygon technical indicators (Tier 1) + pandas-ta (Tier 2/3) |
| Week 4 | DEC-447 Polygon options evaluation; document findings |
| Week 5 | DEC-441 verification + DEC-479 cost correction documentation |
| Week 5 | DEC-448/449 FRED expansion + ALFRED PIT validation |
| Week 6 | DEC-451 Quiver free decommission + DEC-468 Ortex wiring |
| Week 6-7 | DEC-453/454/455/456 — Finnhub/OpenBB/AV/TradingView decommissioning + lint blocks |
| Week 7 | yfinance demotion to fallback (DEC-442) |
| Week 8 | Integration tests + acceptance + PR review |

**Total: ~41.75-54.25d realistic.**

**Parallel-ability:**
- Sprint 4 ↔ Sprint 1: **partial parallel** — Sprint 4 uses Sprint 1's Polygon foundation; can start Week 2 of Sprint 1
- Sprint 4 ↔ Sprint 3: **parallel** — Sprint 3 builds Portfolio; Sprint 4 builds data layer; orthogonal
- Sprint 4 ↔ Sprint 5/6: **parallel** — independent concerns

**Blockers:**
- DEC-478 PROPOSED Polygon tier choice (impacts which Polygon endpoints available)
- DEC-461 PROPOSED FMP subscription (impacts OurFundamentalsToolkit)
- Sprint 1 substantially complete (Polygon foundation)

## §11.5 Done criteria

- [ ] FMP subscription active; smoke test successful; financials + transcripts + analyst estimates cached
- [ ] Polygon reference data replaces yfinance.info; CI tests verify sector/cap/exchange come from Polygon (BUG-218 closed)
- [ ] Polygon earnings cached; yfinance earnings deprecated; deprecation warning fires on import
- [ ] Polygon news replaces Finnhub; news available for all Tier 1 tickers
- [ ] Polygon technical indicators wired for Tier 1; pandas-ta for Tier 2/3
- [ ] Polygon options evaluation document complete; recommend implementation or defer
- [ ] DEC-441 cost reconciled; DEC-479 PROPOSED merged
- [ ] FRED 9+ series cached; ALFRED PIT validated for all series
- [ ] Quiver paid expansion: insider + congressional + 13F + analyst rating changes + government contracts all cached
- [ ] Quiver free endpoints decommissioned
- [ ] Ortex API wired; short interest cached for Tier 1 tickers
- [ ] Finnhub / OpenBB / Alpha Vantage / TradingView code paths removed
- [ ] Lint rules block new imports of decommissioned libraries
- [ ] yfinance demoted to fallback only; not used in production paths
- [ ] All BUG_REGISTER bugs related to data layer closed
- [ ] Sprint 4 PR merged; CI green

## §11.6 Risks

**Risk R-1: FMP subscription cost overrun**
- $14-50/mo per FMP tier; if upgrade needed for endpoints, overrun
- Mitigation: Sprint 4 Week 1 verifies tier; budget $50/mo conservative

**Risk R-2: Polygon news endpoint quality lower than Finnhub**
- News API quality varies; Finnhub may be better in some respects
- Mitigation: cross-reference 5-10 examples; if Polygon insufficient, defer Finnhub decommission to Sprint 7 with rationale

**Risk R-3: yfinance fallback paths trigger silently**
- Code might silently fall back to yfinance; contamination risk
- Mitigation: lint enforces explicit import; CI blocks new yfinance.info / yfinance.earnings imports; deprecation warnings on existing paths

**Risk R-4: Ortex API contract surprises**
- Untested in production
- Mitigation: smoke test Week 6; if API issues, defer Ortex to Sprint 7 Week 14 explicitly

**Risk R-5: Quiver paid endpoint rate limits**
- Paid tier rate limits TBD
- Mitigation: smoke test Week 1; throttle ingest if rate limits enforce

**Risk R-6: Polygon options data depth varies by tier**
- Stocks Starter may not include options; Stocks Developer may
- Mitigation: DEC-447 evaluation explicitly tests at chosen tier; document findings; defer implementation if insufficient

## §11.7 Cost

**Engineering effort:** ~41.75-54.25d
**Subscription cost:**
- FMP $14-50/mo (DEC-461 mandatory now)
- Polygon (Sprint 1 already counted)
- Quiver paid expansion $50-100/mo (already DEC-450 Sprint 1 baseline)
- Ortex $50-100/mo (DEC-468 Sprint 7 baseline)

**Sprint 4 incremental monthly subscriptions: $14-50/mo (FMP).**

## §11.8 Decisions in scope

| DEC | Title | Status |
|---|---|---|
| 410 | API audit (17-API comprehensive) parent decision | RESOLVED-DECIDED |
| 440 | Finnhub decommission scoping | RESOLVED-DECIDED |
| 441 | Polygon Stocks Starter $29 baseline | RESOLVED-DECIDED |
| 442 | yfinance demoted to fallback | RESOLVED-DECIDED |
| 443 | Polygon reference replaces yfinance.info | RESOLVED-DECIDED |
| 444 | Polygon earnings replaces yfinance earnings | RESOLVED-DECIDED |
| 445 | Polygon news replaces Finnhub | RESOLVED-DECIDED |
| 446 | Polygon technical indicators (Tier 1) | RESOLVED-DECIDED |
| 447 | Polygon options evaluation | RESOLVED-DECIDED |
| 448 | FRED 9+ series expansion | RESOLVED-DECIDED |
| 449 | FRED + ALFRED PIT validation | RESOLVED-DECIDED |
| 450 | Quiver paid endpoint expansion | RESOLVED-DECIDED |
| 451 | Quiver free decommissioned | RESOLVED-DECIDED |
| 453 | Finnhub fully decommissioned | RESOLVED-DECIDED |
| 454 | OpenBB fully decommissioned | RESOLVED-DECIDED |
| 455 | Alpha Vantage fully decommissioned | RESOLVED-DECIDED |
| 456 | TradingView removed | RESOLVED-DECIDED |
| 461 | FMP MANDATORY (per DEC-460 negative) | RESOLVED-DECIDED conditional |
| 468 | Ortex wired | RESOLVED-DECIDED |
| 478 PROPOSED | Polygon tier upgrade decision | Awaits owner approval |
| 479 PROPOSED | DEC-441 cost correction $30→$29 | Awaits owner approval |

## §11.9 Test approach

- Unit tests: each new client (FMP, Polygon news, Polygon technicals, Polygon options eval, Ortex)
- Integration: data flows from each source to cache to query layer
- PIT regression: same as_of date returns same data regardless of system time
- Lint: enforces decommission

**Acceptance:** Sprint 4 PR review; verify lint rules + CI tests pass; manual spot-check on 5 Tier 1 tickers across all data sources

## §11.10 Data dependencies

**Inputs:** Sprint 1 Polygon foundation
**Outputs:** Cleaned data layer for Sprint 7 toolkit work; Sprint 8 strategy categories that depend on FMP/Polygon earnings

## §11.11 Operational checklist

(See §11.4 week-by-week.)

## §11.12 Open issues — gaps from ADVERSARIAL_AUDIT

- **GAP 9:** Quiver paid scope (which endpoints)
  - Resolution: §11.1 deliverable #10 — insider + congressional + 13F + analyst rating changes + government contracts
- **GAP 10:** Quiver paid rate limits unverified
  - Resolution: Sprint 4 Week 1 smoke test explicitly verifies
- **GAP 11:** Ortex specific endpoints used unspecified
  - Resolution: short interest + days to cover + borrow cost; Sprint 4 Week 6 smoke test verifies
- **GAP 12:** Ortex API quirks
  - Resolution: §11.6 R-4 — smoke test; if quirks, defer to Sprint 7

## §11.13 Decision history

- DEC-410 (Pass 51): API audit parent decision; identified 17 APIs across project
- DEC-440-456 (Pass 51): individual decommissioning + replacement decisions
- DEC-460-461 (Pass 52 turn 130): conditional FMP subscription
- Pass 52 turn 133: DEC-460 verification negative confirmed; DEC-461 NOW MANDATORY

## §11.14 File / module structure

(See §11.3 component diagram.)

## §11.15 Example walkthrough

**Scenario:** Sprint 7 builds OurFundamentalsToolkit; method `get_recent_earnings_call_transcript("AAPL", "2022-06-15")` is called.

**Without Sprint 4 (no FMP):**
- yfinance has no transcripts
- Polygon Stocks Starter has no transcripts
- Toolkit method returns empty / error → agent reasoning degraded → Phase 1B-α A/B comparison less informative

**With Sprint 4 (FMP subscribed per DEC-461):**
- `fmp_transcripts.fetch_transcript("AAPL", quarter="Q1_2022", filing_date_le="2022-06-15")` returns transcript
- Toolkit method returns transcript text → Fundamentals Analyst incorporates into reasoning → agent overlay value-add increased

**Similarly DEC-443 (Polygon reference replacing yfinance.info):**

**Without Sprint 4:**
- yfinance.info on AAPL returns CURRENT sector "Technology"
- 2022-06-15 query: yfinance.info has no as_of capability → returns CURRENT sector
- BUG-218 contamination: portfolio sector concentration computed on CURRENT sector → wrong if any reclassification happened post-2022-06-15

**With Sprint 4:**
- polygon_reference.get_sector("AAPL", as_of="2022-06-15") returns sector AS OF 2022-06-15
- BUG-218 closed; sector concentration computed correctly

**Sprint 4 isn't glamorous but is essential for Stage 2 verdict integrity.**

---

# PART 12 — SPRINT 5: UNIVERSE MANAGEMENT (Parallel)

## §12.1 What — concrete deliverable in plain English

Sprint 5 produces the **3-tier universe construction logic** that determines which tickers are eligible to trade on any given date in the backtest (and later, in live). This is the build pipeline behind the universe architecture described in Part 2 §2.3.

This sprint runs in parallel with Sprints 3+4+6 because universe management is orthogonal to data layer cleanup, Portfolio class, and engine work.

Concrete deliverables:

**Tier 1 — S&P 500 + Selected ETFs build pipeline:**
1. **`universe/tier_1_sp500.py`** — daily build using `historical_membership.csv` (per DEC-303 + DEC-477 PROPOSED canonical) + selected ETFs (DEC-118: VIX, DXY, GLD, oil, sector ETFs, TLT, HYG, SHY)
2. **PIT correctness** — at as_of=2020-06-15, Tier 1 = S&P 500 membership AS OF 2020-06-15; not current; resolves ADVERSARIAL_AUDIT GAP 36 (Russell 1000 inconsistency, GAP B9)
3. **Liquidity floor enforcement** — $10M ADV minimum; tickers below floor flagged but kept in universe with reduced sizing per DEC-321/366
4. **History requirement enforcement** — 250-day minimum history; new IPOs to S&P 500 wait period before Tier 1 eligibility

**Tier 2 — Spinoffs / IPOs build pipeline:**
5. **`universe/tier_2_spinoffs.py`** — SEC EDGAR scrape for Form 10-12B filings (per DEC-378-380); detects spinoffs from parent company; tracks spinoff event dates
6. **`universe/tier_2_ipos.py`** — recent IPOs identified via Polygon listings (or alternative source); cap minimum $2B; history minimum 20 trading days
7. **`LIMITED_HISTORY` flag** — strategies that need long history check this flag and skip; strategies designed for short-history (e.g., post-IPO drift, post-spinoff opportunity) explicitly opt-in
8. **Refresh frequency** — daily refresh; new spinoffs/IPOs added; aged out (>2 years post-spinoff event) graduate to Tier 1 if S&P 500 member

**Tier 3 — Momentum Top-100 build pipeline:**
9. **`universe/tier_3_momentum.py`** — monthly refresh on the 1st trading day; ranks all universe candidates by 6-month total return + relative strength; selects top 100; subject to liquidity floor + market cap floor
10. **`.github/workflows/refresh_momentum_watchlist.yml`** — cron monthly first-trading-day; commits updated `data/universe/tier_3_momentum.csv`
11. **PIT correctness** — refresh date is recorded; at backtest as_of, use Tier 3 list AS OF that date (not current)

**Universe orchestration:**
12. **`universe/universe_builder.py`** — single entry point; given as_of_date, returns dict `{tier_1: [...], tier_2: [...], tier_3: [...]}`; backtest engine uses this for daily scan
13. **Universe diff tracking** — daily log of universe additions / removals with reasons; supports Phase 1B-α verdict context (which tickers entered/exited cube during run)
14. **Russell 1000 reconciliation per ADVERSARIAL GAP B9** — explicit decision: Stage 2 universe = S&P 500 only (Tier 1) per DEC-477 PROPOSED; Russell 1000 mention from prior docs deprecated; if owner wants Russell 1000 expansion, that's a Stage 2 scope expansion per Part 13 owner review

## §12.2 Why — how this advances Stage 2 toward verdict

Universe management determines **which trades are even possible** in the backtest. Without Sprint 5:

- Tier 1 is just a static list (the 482-ticker CSV) → not PIT-correct → tickers in S&P 500 today but not in 2020 are mistakenly included; tickers removed from S&P 500 in 2022 mistakenly excluded from 2020 trades → cube populated on wrong universe → verdict invalid
- Tier 2 doesn't exist → spinoff/IPO strategies have no candidates → cube under-populated for those signal classes
- Tier 3 doesn't refresh → momentum strategies operate on stale candidate pool → verdict missing real momentum dynamics
- Survivorship bias contamination — including only currently-extant tickers → backtest looks better than reality

Sprint 5 ensures the cube is populated with PIT-correct universe, which is foundational to Stage 2 verdict validity.

## §12.3 How — components, data flow, dependencies

**Component diagram:**

```
backtest/
├── universe/
│   ├── __init__.py
│   ├── universe_builder.py            ★ NEW Sprint 5 (orchestrator)
│   ├── tier_1_sp500.py                ★ NEW Sprint 5
│   ├── tier_2_spinoffs.py             ★ NEW Sprint 5
│   ├── tier_2_ipos.py                 ★ NEW Sprint 5
│   ├── tier_3_momentum.py             ★ NEW Sprint 5
│   ├── liquidity_floor.py             ★ NEW Sprint 5 (DEC-366)
│   ├── history_requirement.py         ★ NEW Sprint 5
│   └── universe_diff.py                ★ NEW Sprint 5

data/universe/
├── historical_membership.csv          (Sprint 1 deliverable; canonical per DEC-477)
├── selected_etfs.csv                   ★ NEW Sprint 5
├── tier_2_spinoffs.parquet             ★ NEW Sprint 5 (refreshed daily)
├── tier_2_ipos.parquet                 ★ NEW Sprint 5 (refreshed daily)
└── tier_3_momentum.parquet             ★ NEW Sprint 5 (refreshed monthly)

.github/workflows/
├── refresh_tier_2_spinoffs.yml         ★ NEW Sprint 5 (daily cron)
├── refresh_tier_2_ipos.yml             ★ NEW Sprint 5 (daily cron)
└── refresh_momentum_watchlist.yml      ★ NEW Sprint 5 (monthly cron)
```

**Data flow at backtest start:**

```
Engine: "I need universe for as_of=2022-06-15"
        │
        ▼
universe_builder.build(as_of_date=2022-06-15)
        │
        ├── tier_1_sp500.build(as_of_date)
        │       reads historical_membership.csv
        │       filters to members at as_of_date
        │       adds selected_etfs.csv (DEC-118)
        │       liquidity_floor.apply($10M ADV)
        │       history_requirement.apply(250 days)
        │       returns ~509 tickers
        │
        ├── tier_2_spinoffs.build(as_of_date)
        │       reads tier_2_spinoffs.parquet (filed_date ≤ as_of)
        │       filters to within 2-year spinoff window
        │       liquidity_floor.apply($5M ADV)
        │       returns variable count
        │
        ├── tier_2_ipos.build(as_of_date)
        │       reads tier_2_ipos.parquet (ipo_date ≤ as_of)
        │       filters to within 1-year IPO window + cap ≥ $2B + history ≥ 20d
        │       returns variable count
        │
        └── tier_3_momentum.build(as_of_date)
                reads tier_3_momentum.parquet
                finds most-recent monthly refresh ≤ as_of_date
                returns top 100 from that month
        │
        ▼
returns {tier_1: [...], tier_2: [...], tier_3: [...]}
        │
        ▼
Engine fires strategies on each tier (strategies declare which tier they target)
```

**Dependencies:**
- Sprint 1: `historical_membership.csv` canonicalized; OHLCV cache for liquidity computation
- Sprint 4 (mid-point): SEC EDGAR scrape capability tested; Polygon listings endpoint operational
- DEC-477 PROPOSED — historical_membership.csv canonical
- DEC-104/375-377 — momentum top-100 specs

**Library dependencies:**
- `requests` + `lxml` (SEC EDGAR scraping)
- `pandas`, `numpy` (computation)
- Polygon listings endpoint via existing client

## §12.4 When

**Sequence within Sprint 5 (~13.5-15.5d, parallel with Sprints 3+4+6):**

| Day | Task |
|---|---|
| 1 | universe_builder.py orchestrator + tier_1_sp500.py |
| 2 | liquidity_floor.py + history_requirement.py |
| 3 | selected_etfs.csv definition + integration |
| 4 | tier_2_spinoffs.py + SEC EDGAR scrape pilot |
| 5 | tier_2_ipos.py + Polygon listings integration |
| 6-7 | tier_3_momentum.py + monthly refresh logic |
| 8 | Refresh workflows (3 GitHub Actions cron jobs) |
| 9 | universe_diff.py tracking |
| 10 | Russell 1000 reconciliation documentation per GAP B9 |
| 11-12 | Integration tests + PIT correctness verification |
| 13-14 | Sprint 5 PR review + merge |

**Total: ~13.5-15.5d realistic.**

**Parallel-ability:**
- Sprint 5 ↔ Sprint 3: parallel
- Sprint 5 ↔ Sprint 4: parallel (slightly dependent on Sprint 4 Polygon listings)
- Sprint 5 ↔ Sprint 6: parallel

**Blockers:**
- Sprint 1 historical_membership.csv canonicalized (DEC-477 PROPOSED approval)
- DEC-378-380 SEC EDGAR scrape feasibility verified (likely fine; SEC EDGAR is public)

## §12.5 Done criteria

- [ ] universe_builder.py returns dict for any as_of date in cache window
- [ ] Tier 1 returns ~509 tickers for current as_of; varies historically per S&P 500 membership
- [ ] Tier 2 spinoffs daily refresh produces sensible candidate count (typically 5-30 active spinoffs)
- [ ] Tier 2 IPOs daily refresh produces sensible candidate count (typically 5-20 active IPOs)
- [ ] Tier 3 momentum monthly refresh produces 100 tickers each refresh
- [ ] PIT correctness: as_of=2020-06-15 returns S&P 500 membership AS OF 2020-06-15 (not current)
- [ ] Liquidity floor enforced: tickers below $10M ADV (Tier 1) / $5M ADV (Tier 2/3) flagged
- [ ] History requirement enforced: tickers with < 250 days history excluded from Tier 1 (or 20 days for IPOs in Tier 2 with LIMITED_HISTORY flag)
- [ ] Russell 1000 reconciliation documented; Stage 2 scope = S&P 500 + selected ETFs (Tier 1) confirmed
- [ ] Universe diff log committed daily; supports Phase 1B-α verdict context
- [ ] 3 refresh workflows running successfully in GitHub Actions
- [ ] Sprint 5 PR merged; CI green; PIT regression tests pass

## §12.6 Risks

**Risk R-1: SEC EDGAR scrape unreliable in Codespace**
- Allowlist may block SEC EDGAR (Wikipedia precedent)
- Mitigation: Sprint 5 Day 4 pilot test; if blocked, owner approves allowlist update OR scrape locally on Windows laptop and commit

**Risk R-2: Form 10-12B parsing complex**
- SEC filings have nested XBRL; parsing requires care
- Mitigation: existing libraries (sec-edgar-downloader, edgar) handle parsing; budget extra day if custom parsing

**Risk R-3: Tier 3 momentum refresh on stale data**
- Monthly refresh first-trading-day; if cron fails, stale list used
- Mitigation: cron failure alerts; manual refresh trigger; freshness check at as_of build

**Risk R-4: historical_membership.csv coverage gaps**
- DEC-303 csv may have gaps for certain dates (especially pre-2010)
- Mitigation: validation pass during Sprint 5; flag gaps; document in LIMITATIONS

**Risk R-5: IPO date PIT correctness**
- Polygon listings endpoint may not have historical IPO date with as_of context
- Mitigation: SEC EDGAR S-1 filing date is canonical IPO date; cross-reference

**Risk R-6: Selected ETFs PIT correctness**
- Some ETFs were created within cache window (e.g., XLY came in 1998, well before; but some sector ETFs are newer)
- Mitigation: each ETF has earliest_date; tier_1 filters to ETFs that exist at as_of

## §12.7 Cost

**Engineering effort:** ~13.5-15.5d
**Subscription cost:** $0 incremental (uses Sprint 1 + 4 data sources)

## §12.8 Decisions in scope

| DEC | Title |
|---|---|
| 103 | IPO universe ≥$2B + 20-day-min history |
| 104 | Momentum top-100 watchlist refresh monthly |
| 118 | Tier 1 includes selected ETFs |
| 303 | historical_membership.csv (PIT S&P 500) |
| 321 | Liquidity filter fail-closed |
| 366 | Liquidity floor $10M Tier 1 / $5M Tier 2/3 |
| 375 | Tier 3 refresh script |
| 376 | Tier 3 refresh workflow |
| 377 | Index rebalance PIT historical dates |
| 378 | Tier 2 spinoffs SEC EDGAR scrape |
| 379 | SEC EDGAR Form 10-12B detection |
| 380 | Spinoff event date tracking |
| 477 PROPOSED | historical_membership.csv canonical | Awaits owner approval |
| GAP B9 (resolution) | Russell 1000 reconciliation — Stage 2 = S&P 500 only |

## §12.9 Test approach

- Unit tests: each tier builder; PIT correctness via freezegun; liquidity / history floor enforcement
- Integration: universe_builder returns expected counts for known historical dates
- Acceptance: owner spot-checks 5 historical dates; confirms Tier 1 membership matches S&P 500 archive

## §12.10 Data dependencies

**Inputs:** Sprint 1 historical_membership.csv + OHLCV; SEC EDGAR + Polygon listings
**Outputs:** Universe dict per as_of → consumed by Phase 1B-α run

## §12.11 Operational checklist

(See §12.4 day-by-day.)

## §12.12 Open issues — gaps from ADVERSARIAL_AUDIT

- **GAP B9 (CRITICAL — Blocker):** Russell 1000 / universe definition inconsistent
  - Resolution: §12.1 deliverable #14 — Stage 2 = S&P 500 + selected ETFs (Tier 1) per DEC-477 PROPOSED; Russell 1000 expansion deferred to potential Stage 2 scope expansion via owner review
- **GAP 36:** historical_membership.csv vs static 482-CSV
  - Resolution: §12.1 deliverable #1 — DEC-477 PROPOSED canonicalizes historical_membership.csv; static deprecated
- **GAP 154-156:** Spinoff / IPO detection sources unspecified
  - Resolution: §12.3 component diagram — SEC EDGAR Form 10-12B + Polygon listings + S-1 filings
- **GAP 157:** Tier 3 momentum refresh failure handling
  - Resolution: §12.6 R-3 — alerts + manual fallback + freshness check

## §12.13 Decision history

- DEC-103/104 (Pass ~25): Tier 2/3 universe specs
- DEC-303 (Pass ~30): historical_membership.csv approach
- DEC-321/366 (Pass ~35): liquidity filter
- DEC-375-380 (Pass ~42): Tier 2/3 refresh + spinoffs SEC EDGAR
- DEC-477 PROPOSED (Pass 52 turn 133): canonicalization of historical_membership.csv

## §12.14 File / module structure

(See §12.3 component diagram.)

## §12.15 Example walkthrough

**Scenario:** Backtest fold 2020 starts. Engine needs universe for 2020-06-15.

**Step 1:** `universe_builder.build(as_of_date='2020-06-15')` called.

**Step 2:** Tier 1:
- `tier_1_sp500.build('2020-06-15')` reads historical_membership.csv
- Filters to S&P 500 members AS OF 2020-06-15 → 505 tickers (including TSLA which was added later 2020-12-21 — TSLA NOT in this universe yet)
- Adds selected ETFs that exist at 2020-06-15 → +12 ETFs
- Applies liquidity floor $10M ADV using Sprint 1 OHLCV → drops 0 (all S&P 500 + ETFs liquid)
- Applies history floor 250 days → drops 0
- Returns 517 tickers

**Step 3:** Tier 2:
- `tier_2_spinoffs.build('2020-06-15')` reads tier_2_spinoffs.parquet
- Filters: spinoff_date within 2 years of 2020-06-15 (i.e., spinoffs from 2018-06-15 onwards)
- Returns ~15 active spinoff candidates (e.g., ADT spinoff from State Industries, MGM spinoff from MGM Mirage, etc.)
- Liquidity floor $5M; history flag LIMITED_HISTORY for those <250 days

- `tier_2_ipos.build('2020-06-15')` reads tier_2_ipos.parquet
- Filters: IPO within 1 year of 2020-06-15 (IPOs since 2019-06-15) + cap ≥ $2B + history ≥ 20d
- Returns ~12 IPOs (e.g., Uber Q2 2019 IPO, Lyft 2019, etc.)

**Step 4:** Tier 3:
- `tier_3_momentum.build('2020-06-15')` reads tier_3_momentum.parquet
- Finds most-recent monthly refresh ≤ 2020-06-15 → 2020-06-01 refresh
- Returns 100 tickers from 2020-06-01 momentum top-100
- (TSLA in this list since pre-S&P-500 inclusion, momentum top-100 captured high-momentum names)

**Step 5:** universe_builder returns:
```python
{
    'tier_1': [517 tickers],
    'tier_2': [27 tickers (15 spinoffs + 12 IPOs)],
    'tier_3': [100 tickers]
}
```

**Step 6:** Engine fires strategies:
- Tier-1-only strategies (e.g., RSI_Mean_Reversion_30_70) iterate over 517 tickers
- Tier-2-only strategies (e.g., Post_Spinoff_Momentum) iterate over 27 tickers
- Tier-3-only strategies (e.g., Momentum_Top_N_Trend) iterate over 100 tickers
- Multi-tier strategies (e.g., Earnings_Drift_Post) iterate over union (excluding ETFs)

**Step 7:** Universe diff log records:
- Today's tier_1 count: 517
- Today's tier_2 count: 27
- Today's tier_3 count: 100
- Additions from yesterday: ABC Corp (new Tier 2 IPO; price first available)
- Removals from yesterday: XYZ Inc (failed liquidity floor due to volume drop)

**Without Sprint 5:**
- Static 482-CSV used for Tier 1 → TSLA included in 2020-06-15 (wrong; TSLA not in S&P 500 until Dec 2020) → contaminates trades
- Tier 2 doesn't exist → spinoff/IPO strategies have no candidates → cube empty for those cells
- Tier 3 doesn't refresh → momentum strategies operate on stale or current list → not PIT
- Cube under-populated AND contaminated → verdict invalid

---

