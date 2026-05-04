# PROJECT_PLAN — Stock Picks & Automated Trading System

**Document role:** Canonical project entry point. References specialized registers; doesn't duplicate them. Single source for project understanding from "what is this" to "what's next."

**Last refreshed:** Pass 52 turn 127 (post-Pass-52 closure)
**Supersedes:** Previous PROJECT_PLAN.md content (now historical via git history)
**Companion canonical doc:** TRADING_RULES_AND_INFORMATION.md (rules/thresholds detail)
**Historical reference:** PROJECT_PLAN_ARCHIVE.md (pre-April-2026)

---

## TABLE OF CONTENTS

**Part A — Project Overview**
1. Vision and Objective
2. Five-Stage Roadmap

**Part B — Current Stage: Stage 2 Strategy Validation**
3. Stage 2 Sub-Phases
4. Sprint Roadmap Index
5. Stage 2 Success Criteria

**Part C — Architecture**
6. Universe Architecture (Three Tiers)
7. Strategy Universe Index
8. Signal Universe
9. Agent Architecture (TradingAgents Framework)
10. Data Sources by Stage

**Part D — Rules & Thresholds**
11. Trading Rules Reference
12. Risk Management Philosophy
13. PIT Correctness — Non-Negotiable

**Part E — Current State & Decisions**
14. Current Status (Pass 52 Closure)
15. Audit Index
16. Engineering Register
17. Documentation Register
18. Bug Register
19. Implementation Readiness
20. Limitations / Caveats / Assumptions

**Part F — Testing & Execution**
21. Testing Strategy
22. Sprint Execution Plan
23. CHECKLIST Process
24. Learnings

**Part G — Reference**
25. Tech Stack Summary
26. Cost Summary
27. Workflow — Making Changes
28. Glossary
29. Document Map
30. Pass Retrospectives Reference

---

# PART A — PROJECT OVERVIEW

## 1. Vision and Objective

### 1.1 What this project is

A comprehensive algorithmic trading platform for **swing trading US equities** with the primary goal of **high-return performance**. The system combines rules-based strategies with selective AI agent overlay (TradingAgents framework), evaluates strategies across a **dimensional verdict cube** (regime × sector × market-cap × volatility × etc.), and progresses through five stages from proof-of-concept to fully automated live trading.

GitHub: `jeetmehta1991/stock-picks-app`

### 1.2 Risk philosophy

**Medium-high risk tolerance** — explicitly accepts drawdowns in pursuit of higher ROI. Owner buys dips during volatile and crisis markets.

Concentration is **accepted** (not penalized):
- No sector caps (DEC-090 REJECTED)
- No max gross/net exposure caps (DEC-133 REJECTED)
- No hard regime direction blocks (replaced with crisis-flag system)

Currency exposure is **accepted**:
- Default unhedged on Canadian ETF substitutions (DEC-254)
- USD/CAD FX exposure tracking only (DEC-134); hedge implementation Stage 4+

Detail: see TRADING_RULES_AND_INFORMATION.md §4 (Risk Management Rules).

### 1.3 Owner profile

- Canadian resident
- IBKR (Interactive Brokers) account holder
- Personal Windows laptop + GitHub Codespace ("vigilant system") for development
- VS Code + Claude Code for browsing
- Codespace terminal for execution
- Approval cadence: explicit per-decision approval required (Option C verification gate)

### 1.4 Out of scope

**Explicitly excluded from current project:**
- **Intraday trading** (separate future project)
- **High-frequency trading** (HFT)
- **Market making**
- **Options strategies as primary signal** (used as supplementary signal only — DEC-145 deferred-implementation)
- **Crypto** (US equities only)

---

## 2. Five-Stage Roadmap

### 2.1 Stage Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Stage 1   │ Stage 2          │ Stage 3        │ Stage 4   │ Stage 5     │
│ Proof of  │ Strategy         │ Paper Trading  │ Live —    │ Full        │
│ Concept   │ Validation       │ (3 months)     │ Small     │ Automation  │
│           │                  │                │ Scale     │             │
│ COMPLETE  │ CURRENT (Pass 53)│ planning       │ planning  │ planning    │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Stage 1: Proof of Concept (COMPLETE)

**Status:** COMPLETE
**Deliverable:** `fetch_stocks.py` Python script fetching US top gainers + TSX quotes via Alpha Vantage; outputs dark-themed `index.html` updated daily via GitHub Actions cron (06:00 UTC).
**Lessons:** Wikipedia scraping unreliable in Codespace network allowlist; static committed CSV files preferred for reference data.

### 2.3 Stage 2: Strategy Validation (CURRENT — Pass 53 implementation)

**Status:** Implementation phase begins Pass 53
**Goal:** Empirically validate strategy roster across dimensional verdict cube
**Effort:** ~310-385 engineering days realistic; ~125-160 days minimum critical path

**Sub-phases:** see §3
**Sprint roadmap:** see §4
**Success criteria:** see §5

### 2.4 Stage 3: Paper Trading

**Status:** Planning
**Duration:** 3 months minimum (DEC-028)
**Trigger:** Stage 2 → Stage 3 transition criteria met (see §5.3)
**Activities:** Paper trades mirror live algo exactly (DEC-198); SQLite trade event store (DEC-267); end-of-day reconciliation reports (DEC-181); weekly auto-generated performance reviews (DEC-182).

### 2.5 Stage 4: Live Trading — Small Scale

**Status:** Planning
**Trigger:** Stage 3 paper trading proves profitable per numeric gates (DEC-269)
**Prerequisites:**
- CPA consultation on Canadian tax classification (DEC-270, DEC-035)
- IBKR market data subscriptions (~$10-30/mo per DEC-271)
- Cloud hosting migration (DEC-272 — AWS/GCP target; Codespace not production-grade)
- Disaster recovery plan (DEC-273)
- Daily loss limits (DEC-034)
- Multi-vendor data fallback (DEC-160)
- Remote kill switch via email (DEC-139)
- Norbert's Gambit operational for CAD→USD funding (DEC-255)

### 2.6 Stage 5: Full Automation

**Status:** Planning
**Activities:** Stage 4 deliverables operating autonomously; full API stack (~$263 CAD/mo per project memory).

### 2.7 Stage Transition Gates

Detail in TRADING_RULES_AND_INFORMATION.md §1 (Stage Transition Criteria).

Summary:
- **Stage 1 → 2:** smoke test passing (COMPLETE)
- **Stage 2 → 3:** Phase 1B-α verdict gate (Sharpe ≥ 1.0 OOS, max DD ≤ 25%, A/B clear, divergence < 20%)
- **Stage 3 → 4:** 3-month paper trading + numeric gates met + CPA consultation complete
- **Stage 4 → 5:** Stage 4 small-scale stable for ≥ 6 months; full automation infrastructure operational

---

# PART B — CURRENT STAGE: STAGE 2 STRATEGY VALIDATION

## 3. Stage 2 Sub-Phases

### 3.1 Phase 0.A — Polygon Foundation (Sprint 1)

**Effort:** ~20.5-26.5 engineering days
**Deliverable:** S&P 500 OHLCV cache populated (PIT-correct via DEC-298 raw OHLCV + DEC-040 PointInTimeLoader); FRED expansion data prefetched; sentiment data refresh scripts operational; cache infrastructure (eviction, monitoring, multi-process safety) operational.
**Decisions in scope:** DEC-040, DEC-256-261, DEC-225/227/235, DEC-275, DEC-300/304/307-310, DEC-117/118, DEC-318-320/390-391, DEC-328-329, DEC-382-383

**Owner action prerequisite:** Subscribe to **Polygon Stocks Starter $30/mo per DEC-441** before Sprint 1 can fully proceed.

### 3.2 Phase 0.B — Portfolio Class (Sprint 3)

**Effort:** ~8-11 engineering days
**Deliverable:** Resolves **BUG-095 CRITICAL OPEN** (no Portfolio class). Implements proper portfolio-level position management; unblocks DEC-070/076/091.
**Decisions in scope:** DEC-070/076/091 (BLOCKED_ON_BUG-095), DEC-277, DEC-339

### 3.3 Phase 0.C — Engine Bug Fixes Tier A (Sprint 2)

**Effort:** ~25.5-30.5 engineering days
**Deliverable:** 14 critical engine bug fixes (close_trade NameError, duplicate ClosedTrade dataclass, circuit breakers Level 3+4, exit_hybrid_50pct max_days inconsistency, etc.).
**Decisions in scope:** DEC-293-297, DEC-305-306, DEC-311-312, DEC-314-315, DEC-327, DEC-338, DEC-340

### 3.4 Phase 0.D — ICT/SMC Fork Integration

**Effort:** Distributed across Sprints 1, 4, 8
**Deliverable:** smartmoneyconcepts library fork verified operational; ICT/SMC strategies (FVG, BOS, CHoCH, order blocks) integrated; Layer 2 strategy roster expansion per STRATEGY_REGISTER.md.
**Decisions in scope:** DEC-045, DEC-259, DEC-345, DEC-352, DEC-355-362

### 3.5 Phase 0.E — Catch-Mechanism Defense + Architecture Hygiene (Sprint 6)

**Effort:** ~62.25-76.75 engineering days (largest sprint absolute)
**Deliverable:** 5-layer catch-mechanism defense (DEC-417/436/437/438/439); A/B testing foundation (DEC-205/206); 9 architecture hygiene improvements (DEC-217/218/219/220 from X33 + DEC-222/229/230/231/232/233/241); risk controls (DEC-018/134/135/136); CI infrastructure (DEC-138/170/171/172/173/177/178/179/183).

### 3.6 Phase 1B — Statistical Methodology + A/B (Sprint 7)

**Effort:** ~76-85 engineering days (largest sprint by total effort)
**Deliverable:** Walk-forward validation (DEC-109); Deflated Sharpe / PSR (DEC-110); stationarity tests (DEC-111); A/B testing operational (DEC-205-216); regime methodology (DEC-106-108, DEC-149-151); AgentGateConfig spec (DEC-042) — see TRADING_RULES_AND_INFORMATION.md §7.

### 3.7 Phase 1B-α — Dimensional Cube + Dashboards (Sprint 7-8)

**Effort:** ~28-38 engineering days
**Deliverable:** Dimensional verdict cube infrastructure (DEC-422 phases 1-7 = DEC-425-431); 3-dashboard suite (DEC-199 cube explorer + DEC-200 ICT/SMC audit + DEC-201 agent overlay analysis); 5-gate validity filter operational (DEC-426).

### 3.8 Phase 1C+ — Strategy Categories Expansion (Sprint 8)

**Effort:** ~37-55 engineering days
**Deliverable:** 8 chart pattern strategies (DEC-355-362); 3 Calendar/Index Rebalance/Within-category strategies (DEC-368/370/371); existing breakout strategies retest variants (BUG-111 architectural choice — Option A shared primitive recommended); multi-timeframe non-ICT extension (DEC-350); 13F price-level mapping (DEC-352); 9 new exit methods (DEC-067 phases A+B = DEC-432/433); AEP breaker (DEC-435).

---

## 4. Sprint Roadmap Index

**Canonical:** see ENGINEERING_REGISTER.md for sprint slot details with test signals + effort.

### 4.1 Sprint Dependency Graph

```
Sprint 1 (Phase 0.A Foundation) ──┬──► Sprint 4 (DEC-410 Audit Findings)
                                  ├──► Sprint 5 (Universe Management)
                                  └──► Sprint 5 NEW (Position Sizing)
Sprint 2 (Engine Bug Fixes Tier A) [parallel-able after Sprint 1 cache established]
Sprint 3 (Portfolio Class) ───────► Resolves BUG-095; sequential after Sprint 2
Sprint 6 (Phase 0.E + Hygiene) ───► CI infrastructure; parallel-able from Day 1
Sprint 7 (Statistical Methodology + A/B) ──► Critical path; gates Phase 1B-α
Sprint 7-8 (Dimensional Cube + Dashboards) ─► Phase 1B-α verdict infrastructure
Sprint 8 (Strategy Categories) ────► Parallel-able; not critical path
Sprint 9 (Phase 1B-α run + ongoing) ► Final critical-path gate
```

### 4.2 Sprint Table

| Sprint | Name | Effort | Critical path? | Pass 52 final |
|---|---|---|---|---|
| 1 | Phase 0.A Polygon Foundation | ~20.5-26.5d | Yes | scoped |
| 2 | Engine Bug Fixes Tier A | ~25.5-30.5d | Yes | scoped |
| 3 | Phase 0.B Portfolio Class | ~8-11d | Yes (BUG-095) | scoped |
| 4 | DEC-410 Audit Findings | ~41.75-54.25d | Yes | scoped |
| 5 | Universe Management | ~13.5-15.5d | Partial | scoped |
| 5 NEW | Position Sizing | ~3.5d | No (parallel) | scoped |
| 6 | Phase 0.E + Hygiene | ~62.25-76.75d | Partial | scoped |
| 7 | Statistical Methodology + A/B | ~76-85d | Yes | scoped |
| 7-8 | Phase 1B-α Cube + Dashboards | ~28-38d | Yes | scoped |
| 8 | Strategy Categories | ~37-55d | No | scoped |
| 9 | Phase 1B-α run + ongoing | ~6d | Yes | scoped |
| **Total Stage 2** | | **~311.5-386.5d realistic** | | |
| **Critical path minimum** | | **~125-160d** | | |

### 4.3 Critical Path

Sprint 1 → Sprint 3 (BUG-095 unblock) → Sprint 4 (audit cleanup) → Sprint 7 (statistical) → Sprint 7-8 (cube) → Sprint 9 (Phase 1B-α run)

### 4.4 Parallel-able Sprints

- Sprint 2 + Sprint 4 (after Sprint 1 cache established)
- Sprint 5 + Sprint 5 NEW
- Sprint 6 hygiene + CI infrastructure (Day 1)
- Sprint 8 (off critical path)

### 4.5 Sprint Sequencing Reference

→ ENGINEERING_REGISTER.md (canonical sprint detail with test signals + effort estimates per decision)

---

## 5. Stage 2 Success Criteria

### 5.1 Quantitative Gates (per DEC-269)

Stage 2 → Stage 3 transition requires:
- **Sharpe ≥ 1.0** OOS (out-of-sample)
- **Max DD ≤ 25%**
- **Win Rate** threshold per category (DEC-083 TIERED min trades)
- **A/B clear** — full-agents > rules-only by ≥ 0.2 net Sharpe per DEC-131
- **Divergence < 20%** — agent-vs-rules disagreement bounded

### 5.2 Phase-Specific Milestones

Detail in TRADING_RULES_AND_INFORMATION.md §2 (Phase-by-Phase Acceptance Criteria).

Summary:
- **Phase 0.A milestone:** S&P 500 OHLCV fully cached + first PIT loader test passing (Sprint 1 first deliverable; **time-boxed 1-2 weeks**)
- **Phase 0.B milestone:** Portfolio class operational; BUG-095 closed
- **Phase 0.E milestone:** 5-layer catch-mechanism defense operational; 90% test coverage achieved (DEC-098)
- **Phase 1B milestone:** A/B framework operational; statistical methodology tests pass
- **Phase 1B-α milestone:** Dimensional cube produces verdicts per DEC-422; 3-dashboard suite operational

### 5.3 Stage 2 → Stage 3 Transition Criteria

All quantitative gates (§5.1) PLUS:
- Phase 1B-α run complete with 5-gate validity filter applied (DEC-426)
- Per-strategy verdicts available in dimensional cube
- Live decision lookup table populated (DEC-429)
- Owner reviews Phase 1B-α dashboard outputs and approves Stage 3 transition

---

# PART C — ARCHITECTURE

## 6. Universe Architecture (Three Tiers)

### 6.1 Tier 1: S&P 500 + Selected ETFs

**Composition:** 482 S&P 500 constituents (per static committed CSV, since Wikipedia scraping unreliable in Codespace) + selected sector/macro ETFs (per DEC-118 cross-asset macro: VIX, DXY, GLD, oil, sector ETFs, TLT, HYG, SHY).
**Liquidity floor:** $10M ADV (per DEC-366)
**History requirement:** 250 trading days
**Universe:** ~509 tickers

### 6.2 Tier 2: Spinoffs / IPOs (high-cap, short-history)

**Composition:** Recent spinoffs (per DEC-378-380 SEC EDGAR scrape) + recent IPOs (per DEC-103/373/374 Tier 2 universe automation)
**Liquidity floor:** $5M ADV
**Market cap minimum:** $2B
**History requirement:** 20 days minimum (with `LIMITED_HISTORY` flag respected by strategies)
**Universe size:** Variable; ~10-30 tickers active at any time

### 6.3 Tier 3: Momentum Top-100 Watchlist

**Composition:** Top 100 momentum-screen tickers refreshed monthly (per DEC-104/375/376/377)
**Liquidity floor:** $5M ADV
**Market cap minimum:** $300M
**History requirement:** 60 days
**Refresh:** Monthly via `.github/workflows/refresh_momentum_watchlist.yml`

### 6.4 Universe Management

→ ENGINEERING_REGISTER.md Sprint 5 (DEC-303/331/364-380)

---

## 7. Strategy Universe Index

**Canonical:** STRATEGY_REGISTER.md

### 7.1 Strategy Taxonomy (4 layers)

- **Layer 1:** Baseline 60-strategy roster (7 categories; pre-Pass-52)
- **Layer 2:** Phase 0.D Additions (ICT/SMC, Earnings Momentum, Calendar) — DEC-045/259/345
- **Layer 3:** Pass 52 RESOLVED-DECIDED Additions
  - Layer 3A: Chart Pattern Strategies (DEC-355-362, 8 strategies, X55 closure)
  - Layer 3B: Strategy Categories (DEC-367-371, 5 strategies, X1 Block 2 closure)
- **Layer 4:** Sub-decisions and additive strategies (DEC-432/433/435 from DEC-067/075)

### 7.2 Total Strategy Count

**Roster total:** ~109-119 strategy classes when full Layer 1+2+3+4 implemented (varies by implementation order in Sprint 8).

### 7.3 Detail

→ STRATEGY_REGISTER.md (canonical roster + sourcing + counting convention notes)

---

## 8. Signal Universe

**~220 fields per instrument per day** at full Stage 2 scope.

### 8.1 Technical Signals

Standard TA: moving averages, RSI, MACD, Bollinger Bands, ATR, ADX, etc.; ICT/SMC primitives (FVG, BOS, CHoCH, order blocks per DEC-045/259/345); chart patterns (DEC-355-362).

### 8.2 Smart Money Signals

- **Insider trading** (Form 4 actual sales, Form 144 proposed sales per DEC-125)
- **Congressional disclosures** (Quiver paid endpoint per DEC-450)
- **13F institutional holdings** (Quiver paid + DEC-325 PIT filing_date)
- **Cross-source clusters** (insider+congressional+13F confluence per DEC-124)
- **Exponential decay weighting** (90-day half-life default per DEC-123)
- **Smart money composite** weights configurable (DEC-332)

### 8.3 Macro Signals

**FRED expansion** to 9+ series (DEC-085 + DEC-407+448):
- VIX, DGS10, T10Y2Y, FEDFUNDS, UNRATE, CPIAUCSL, T10YIE, BAA10Y, DXY

**Regime classifier 8+ inputs** (DEC-106): VIX + yield curve + HY spread + ICSA jobless + breadth + sector dispersion + AAII + CNN F&G; expanded to 12+ multi-asset (DEC-150) + sector-level regime (DEC-151).

### 8.4 Sentiment Signals

- **AAII** Bull/Bear sentiment (refresh script DEC-319/390)
- **CNN Fear & Greed** (no interpolation; tuple `(value, last_published_date, age_days)` per DEC-320/391)
- **Reddit/social** via news sentiment

### 8.5 Detail

→ ENGINEERING_REGISTER.md decisions DEC-118/106/107/123/124/125/319/320/332/333

---

## 9. Agent Architecture (TradingAgents Framework)

### 9.1 11 Agents per propagate()

**12 minus dropped Social Analyst** (DEC-057 — disabled per cost optimization).

Active agents include Bull Researcher, Bear Researcher, News Analyst, Fundamentals Analyst, ChartAnalyst, Risk Manager, Trade Decision Aggregator, plus 4 supporting agents.

### 9.2 LLM Provider Strategy (per DEC-058)

- **Backtest (Stage 2):** GPT-5.4-mini (cost-optimized; ~$300 hard cap per DEC-059)
- **Live (Stage 3+):** Anthropic Claude
- **Skip TradingAgents CLI** (DEC-056)
- **Cost-optimized config** (DEC-055)

### 9.3 AgentGateConfig Spec

**Canonical detail:** TRADING_RULES_AND_INFORMATION.md §7 (AgentGateConfig).

Summary (per DEC-042 RESOLVED Pass 52 turn 121):
- **Approval rule:** WEIGHTED CONTINUOUS-SCORE (`gate_score = w_bull*s_bull + w_bear*s_bear + w_risk*s_risk + w_chart*s_chart`); default weights 0.25 each (REVISIT_AFTER_BACKTEST)
- **Risk veto:** `s_risk ≥ 0.5` hard gate
- **Bull/Bear must align:** both > 0.5 for long; both < 0.5 for short
- **Tier mapping:** HIGH ≥0.8 (5%) / MED 0.65-0.8 (3%) / LOW 0.5-0.65 (1.5%)
- **Override:** Stage 2 deterministic; Stage 3+ owner manual

### 9.4 A/B Framework (per DEC-205-216)

**4-arm design** (rules / full-agents / no-Risk / no-Bull-Bear); paired design (every trade by every arm); pre-commit minimum 300 paired trades per DEC-207; multi-metric comparison (Sharpe + Sortino + DD + win rate + PF + CVaR + cost) per DEC-208.

Detail: TRADING_RULES_AND_INFORMATION.md §18.

### 9.5 Agent Ablation Studies

→ DEC-211 Sprint 9 (post-Phase-1B-α; Option A NARROW SCOPE; sample-bounded top-20% strategies × ~5K trades; ~$120 vs $13,800 naive)

---

## 10. Data Sources by Stage

**Canonical:** API_AUDIT.md (DEC-410 17-API audit, 4 tiers, 4 batches)

### 10.1 Stage 1 (current — deprecating)

- Alpha Vantage (DEC-455 deprecation timeline; supersession by Polygon per DEC-440/441)

### 10.2 Stage 2 (Pass 53 implementation)

- **Polygon Stocks Starter** — $30/mo (DEC-441) **[Owner action prerequisite for Sprint 1]**
- **FRED** — free; expanded to 9+ series (DEC-407+448)
- **ALFRED** — archival FRED for vintage data PIT (DEC-301)
- **Quiver Quantitative paid** — ALL endpoints (DEC-450; Insider Trading, Congressional, 13F, House/Senate, etc.)
- **smartmoneyconcepts** library fork (DEC-045)
- **yfinance** — limited use; deprecating live calls (DEC-013, DEC-444 absorbed)
- **AAII** — sentiment refresh (DEC-319)
- **CNN Fear & Greed** — sentiment refresh (DEC-320)
- **Pandas Market Calendars** (DEC-235)

### 10.3 Stage 3 (planning)

- All Stage 2 sources +
- **IBKR paper trading data** (real-time + historical via paper account)
- **SEC EDGAR Form 10-12B** (DEC-379 — spinoff feed)

### 10.4 Stage 4+ (planning)

- All Stage 3 sources +
- **IBKR market data subscriptions** (~$10-30/mo per DEC-271)
- **Polygon real-time WebSocket** (if needed; current Stocks Starter is delayed)
- Multi-vendor fallback chain (DEC-160 deferred Stage 4)

### 10.5 Detail

→ API_AUDIT.md (canonical data source matrix with 17 APIs across 4 tiers)

---

# PART D — RULES & THRESHOLDS

## 11. Trading Rules Reference

**All trading rules, thresholds, criteria, and benchmarks live in TRADING_RULES_AND_INFORMATION.md (canonical).**

This section provides high-level orientation; for implementation thresholds and decision parameters, refer to TRADING_RULES_AND_INFORMATION.md sections directly.

### Quick Reference Index

| Topic | TRADING_RULES Section |
|---|---|
| Stage transition criteria | §1 |
| Phase-by-phase acceptance criteria | §2 |
| Strategy validity gates (5-Gate per DEC-426) | §3 |
| Strategy decay detection | §4 |
| Strategy tiers + position sizing | §5 |
| Per-ticker risk controls | §6 |
| AgentGateConfig | §7 |
| Exit methodology | §8 |
| Circuit breakers | §9 |
| Regime classification | §10 |
| Regime-conditional behavior | §11 |
| PIT correctness | §12 |
| Cache rules | §13 |
| Trading costs | §14 |
| Canadian-resident specifics | §15 |
| Walk-forward validation | §16 |
| Performance metrics | §17 |
| A/B testing framework | §18 |
| Event-calendar suppression | §19 |
| Corporate actions | §20 |
| Phase 1B-α dimensional cube | §21 |
| Cube verdict framework | §22 |
| REVISIT_AFTER_BACKTEST tags | §23 |

---

## 12. Risk Management Philosophy

### 12.1 Medium-High Risk Profile

**Owner accepts:** drawdowns, concentration, FX exposure, single-name concentration, sector concentration.

**Owner does not accept:** lookahead bias, premature decisions, untested production code, silent failures.

**Implication for design:** Risk controls focus on **operational risks** (PIT correctness, test coverage, deterministic behavior) not portfolio-construction risks (sector caps, exposure caps).

### 12.2 Position Sizing Methodology

**3-Tier system** (DEC-021): HIGH 5% / MED 3% / LOW 1.5%

**Phased rollout** of advanced sizing:
- Phase A: Tiered baseline (DEC-021 default)
- Phase B parallel: Fractional Kelly (DEC-086)
- Phase C parallel: Vol-targeted per-position (DEC-087)
- Portfolio vol target: 15% annualized (DEC-088)

Detail: TRADING_RULES_AND_INFORMATION.md §5

### 12.3 Circuit Breakers

**Levels 1-5** (DEC-314/315):
- Level 1-2: Soft pauses (single-day extreme moves)
- Level 3-4: Intraday halts (DEC-314 implementation pending)
- Level 5: Market halt (sequential check per DEC-315)

**Recovery rules** with cooldown + hysteresis (DEC-127); dispersion-conditional breaker (DEC-128).

Detail: TRADING_RULES_AND_INFORMATION.md §9

### 12.4 Per-Ticker Controls

- **Stop-out cooldown:** 5 trading days post-stop (DEC-018) — prevents whipsaw re-entry
- **Cumulative max-loss cap:** -10% rolling 30-day per ticker (DEC-135) — REVISIT_AFTER_BACKTEST
- **Liquidity filter:** tier-specific floors fail-closed (DEC-321/366)

Detail: TRADING_RULES_AND_INFORMATION.md §6

### 12.5 Detail

→ TRADING_RULES_AND_INFORMATION.md §4 (Risk Management Rules), §5 (Position Sizing), §6 (Per-Ticker Controls), §9 (Circuit Breakers)

---

## 13. PIT Correctness — Non-Negotiable

### 13.1 Why PIT Matters

**Lookahead bias** (using future information in historical backtest) inflates results dramatically and produces strategies that fail in live trading. PIT discipline ensures `loader.fetch(as_of=D)` returns rows with `date ≤ D` only.

### 13.2 PIT Loader Architecture

**DEC-040:** PointInTimeLoader structural framework — Sprint 1 foundation. Consumed by all PIT-aware fetchers.

**Test signal:** freezegun-based `loader.fetch(as_of=D)` returns rows with date ≤ D; rejects rows with date > D.

### 13.3 Cache Stores Raw OHLCV

**DEC-298 RESOLVED-DECIDED:** switch yfinance `auto_adjust=False`; store raw OHLCV + corp actions; recompute adjusted-on-demand by as_of date.

**Sprint sequencing:** DEC-298 implementation early Sprint 4; DEC-377 (Tier 3 historical backfill) and DEC-411 (DEC-109 Phase A 2018 cache extension) wait for DEC-298 implementation.

### 13.4 PIT Guard

**DEC-305:** PIT guard RAISE not WARNING — any row with date > as_of date triggers exception, not silent log message.

**Detail:** TRADING_RULES_AND_INFORMATION.md §12 (PIT Correctness Rules), §13 (Cache Rules)

---

# PART E — CURRENT STATE & DECISIONS

## 14. Current Status (Pass 52 Closure)

### 14.1 Pass 52 Achievements Summary

- PENDING resolution: 60% → 0% (~280 decisions resolved)
- Phase 2 retroactive sprint-tracking audit (~226 classified)
- Bug coverage gap closed (148 bugs in BUG_REGISTER cross-reference)
- Bulk sweep (80 PENDING converted to terminal states)
- CHECKLIST #58 operational at 4 levels (technical homelessness, substantive homelessness, bug coverage, status-flip discipline)
- Engineering effort reality check: ~30-40d → ~311.5-386.5d (8-10x scope expansion surfaced)

### 14.2 Pass 53 Status: Pre-Sprint-1 Setup

**Pre-execution risk planning** in progress (Pass 52 turn 125+).

**10 pre-Sprint-1 actions identified** (Pass 52 turn 125):
1. Bug status audit (148 bugs → FIXED_IN_CODE / OPEN_PENDING / WONTFIX)
2. Bring forward Sprint 6 quality gates to Sprint 1 Day 1 (DEC-138/170/172/173/177/229/232/233)
3. Define Minimum Viable Backtest (MVB)
4. Write Sprint 1 acceptance criteria
5. Set up branch protection + PR review flow
6. Test-first discipline doc
7. Time-box Sprint 1 first deliverable
8. Sprint plan with bug-fix work as visible line items
9. Pre-commit hook installed locally
10. Define RESOLVED-IMPLEMENTED criteria per decision

**Pre-Sprint-1 setup effort:** ~9-11 engineering days

### 14.3 Audit State

**462 decisions / 0 PENDING / 100% terminal**

| Status | Count |
|---|---|
| RESOLVED-DECIDED | 358 |
| DEFERRED_TO_STAGE_3 | 32 |
| DEFERRED_TO_STAGE_4 | 19 |
| SUPERSEDED (total) | 29 |
| BLOCKED_ON_X | 10 |
| REJECTED | 2 |
| Other (PARTIAL/OBSOLETE) | 12 |

### 14.4 Detail

→ PASS_53_PRIORITIES.md (Pass 52 retrospective + Pass 53 priorities)

---

## 15. Audit Index

**Canonical:** AUDIT.md (~25,000 lines of decision detail) + AUDIT_INDEX.md (status table for 462 decisions)

### 15.1 Decision Tracking Framework

Each decision has substantive scope text, status (RESOLVED-DECIDED, DEFERRED, SUPERSEDED, BLOCKED, REJECTED, etc.), joint references (other decisions consumed by or consuming this one), test signals (for engineering decisions), effort estimate (for engineering decisions), and sprint slot (per CHECKLIST #58).

### 15.2 Audit Coverage

**462 decisions / 0 PENDING / 100% terminal state**

### 15.3 Detail

→ AUDIT_INDEX.md (canonical status table)

---

## 16. Engineering Register

**Canonical:** ENGINEERING_REGISTER.md (~226 ENG decisions tracked across 11 sprints)

### 16.1 Engineering Decisions Tracked

~226 RESOLVED-DECIDED engineering decisions distributed across Sprints 1-9 + 5 NEW + 7-8 cross-sprint.

### 16.2 Sprint Slots

Each sprint slot has decision ID + description, test signals (verifiable acceptance criteria), effort estimate (engineering days), and joint references to dependent decisions.

### 16.3 Detail

→ ENGINEERING_REGISTER.md (canonical sprint roadmap)

---

## 17. Documentation Register

**Canonical:** DOCUMENTATION_REGISTER.md (~80 DOC decisions tracked across 5 buckets)

### 17.1 Documentation Decisions Tracked

5-bucket classification:
- **Bucket A:** Foundational / Already-Integrated (no separate execution work)
- **Bucket B:** Methodology / Library Choices
- **Bucket C:** Cross-Reference / Absorbed (work tracked via parent or joint decision)
- **Bucket D:** Stage 3+/4+ Operational (defer to that stage)
- **Bucket E:** To Be Classified (currently empty)

### 17.2 Execution Plan

**Phase 1 (post-walkthrough):** Documentation register cleanup pass — execute all documentation-only items in order. Trigger: post-Pass-52 closure (NOW available).

**Phase 2 (parallel with engineering):** Per-bucket execution.

### 17.3 Detail

→ DOCUMENTATION_REGISTER.md (canonical 5-bucket DOC tracker)

---

## 18. Bug Register

**Canonical:** BUG_REGISTER.md (148 bugs cross-referenced with resolving decisions)

### 18.1 Bug Coverage

148 canonical bugs in AUDIT.md (### BUG-NN sections); 100% linked to decisions in AUDIT_INDEX.md.

**4-bucket classification:**
- **Bucket 1 (Open-linked):** Resolution decision exists with sprint slot
- **Bucket 2 (Open-unlinked):** None found — all bugs linked
- **Bucket 3 (Resolved):** Already fixed in code; historical record
- **Bucket 4 (Deferred / WONTFIX):** Documented in DOCUMENTATION_REGISTER

### 18.2 CRITICAL OPEN Bugs (3)

- **BUG-095** (no Portfolio class) → resolution Sprint 3 Phase 0.B (~8-11d); blocks DEC-070/076/091
- **BUG-218** (yfinance .info CURRENT not as_of) → resolution DEC-443 absorbed Sprint 4
- **BUG-111** (no break-and-retest variants of breakout strategies) → resolution Sprint 8 via DEC-355-362; **architectural choice flagged** (Option A shared retest primitive ~5-10d vs Option B per-strategy variants ~25-30d)

### 18.3 Detail

→ BUG_REGISTER.md (canonical bug-decision cross-reference)

---

## 19. Implementation Readiness

**Canonical:** IMPLEMENTATION_READINESS_DASHBOARD.md (sprint readiness gates + effort estimates)

### 19.1 Sprint Readiness Gates

Each sprint has effort estimate (current), decisions in scope (count), critical path classification (yes/no/partial), and pre-Sprint-1 dependencies.

### 19.2 Effort Reality Check

- **Total Stage 2 realistic:** ~311.5-386.5 engineering days
- **Critical path minimum:** ~125-160 engineering days
- **8-10x scope expansion** vs original ~30-40d Pass 52 starting estimate
- Hidden in homeless + substantively-homeless decisions: ~280-345 days surfaced via Phase 2 retroactive audit

### 19.3 Detail

→ IMPLEMENTATION_READINESS_DASHBOARD.md (canonical sprint readiness)

---

## 20. Limitations / Caveats / Assumptions

**Canonical:** LIMITATIONS_CAVEATS_ASSUMPTIONS.md (CAV-001 through CAV-071+)

### 20.1 Caveat Categories

- Section 1: Data quality and PIT correctness
- Section 2: Methodology and statistical caveats
- Section 3: Cascade-broken signal pipelines (Stage 5/5.5 findings)
- Section 4: Data source caveats
- Section 5+: Additional Pass-specific caveats

### 20.2 Detail

→ LIMITATIONS_CAVEATS_ASSUMPTIONS.md (canonical)

---

# PART F — TESTING & EXECUTION

## 21. Testing Strategy

### 21.1 Test Pyramid

**5 test layers** (DEC-417/436-439):
- **Unit tests:** Per-function correctness (~70% of test count)
- **Integration tests:** Cross-module behavior (~20%)
- **Characterization tests:** Golden-master snapshots (DEC-438)
- **Property-based tests:** Hypothesis library on invariants (DEC-437)
- **Differential tests:** Two independent implementations on high-stakes computations (DEC-439)

### 21.2 Coverage Target

**90%** per DEC-098 (owner override from 70% baseline).

### 21.3 Multi-Layer Defense (5-Layer Catch-Mechanism per DEC-417/436-439)

- **Layer 1:** Pre-flight checklist
- **Layer 2:** CI/CD regression pipeline (DEC-436)
- **Layer 3:** Property-based testing (DEC-437)
- **Layer 4:** Golden-master tests (DEC-438)
- **Layer 5:** Differential testing (DEC-439)
- **Plus:** DEC-417 (test-run audit gate; approval-vs-implementation gap)

### 21.4 PIT Regression Tests via freezegun (DEC-050)

Every PIT-loader function tested with frozen time; verifies `loader.fetch(as_of=D)` returns rows with `date ≤ D` only.

### 21.5 Test Infrastructure

→ ENGINEERING_REGISTER.md Sprint 6 (DEC-098/138/170/177/178/179/183/222/229/230/231/232/417/436-439)

---

## 22. Sprint Execution Plan

### 22.1 Per-Sprint Workflow

**PR-based, branch-protected, CI-gated:**
1. Feature branch created from `main`
2. Test written first (failing test linked to decision)
3. Code change implementing decision per ENGINEERING_REGISTER scope
4. Pre-commit hook runs locally (ruff + black + isort + mypy + pytest)
5. PR opened; CI runs cold-start (DEC-138) + regression (DEC-436) + property (DEC-437) tests
6. Owner reviews PR before merge
7. Merge to `main`; CHECKLIST #58 atomic commit pattern enforced
8. Status flip RESOLVED-DECIDED → RESOLVED-IMPLEMENTED with verification commit

### 22.2 Acceptance Criteria Template per Sprint

For each sprint deliverable:
- [ ] All decisions in sprint scope have RESOLVED-IMPLEMENTED status
- [ ] All test signals from ENGINEERING_REGISTER pass
- [ ] Coverage ≥ 90% on changed modules (DEC-098)
- [ ] Mypy --strict passes (DEC-170)
- [ ] Cold-start CI passes (DEC-138)
- [ ] Determinism test byte-identical pass (DEC-232)
- [ ] Owner reviews and approves sprint completion

### 22.3 RESOLVED-DECIDED → RESOLVED-IMPLEMENTED Transition

Per CHECKLIST #58 spirit applied to implementation:
- **RESOLVED-DECIDED:** Decision approved with sprint slot + test signals + effort
- **RESOLVED-IMPLEMENTED:** Code merged + tests pass + coverage met + owner-verified

**Status flip requires:** PR merged to main + CI green + linked test signals demonstrably passing.

### 22.4 Implementation Cadence

**Pass 53 cadence options (owner direction needed):**
- Per-PR review (owner reviews every PR before merge)
- Per-sprint-milestone review (owner reviews at sprint completion)
- Hybrid (per-PR for HARD-REVERSIBILITY work; per-milestone for routine)

---

## 23. CHECKLIST Process

**Canonical:** CHECKLIST.md (58 process discipline items)

### 23.1 Latest CHECKLIST Items

- **#58:** Sprint-tracker assignment as RESOLVED-DECIDED commit requirement (Pass 52 L137)
- **#57:** Use-case mapping discipline (Pass 52 L136 — this-system vs generic-template)
- **#56:** Focus-phase scope filter (Pass 52 L135 — forward-looking deferral discipline)
- **#55:** Phase scope check (Pass 52 L134 — architectural framing gate)
- **#54:** Test-run audit gate (Pass 52 L133 — CRITICAL process gate)
- **#53:** Grounded-recommendation format mandatory (Pass 52)
- **#52:** Ambiguous owner directives default to lower-impact action (Pass 52 L131)
- **#51:** Do not infer approval beyond owner's explicit statement (Pass 52)

### 23.2 #58 Operational

**Every RESOLVED-DECIDED status flip MUST include sprint-tracker assignment in the SAME commit:**
- AUDIT_INDEX.md (status flip)
- AUDIT.md (narrative)
- ENGINEERING_REGISTER.md (sprint slot if engineering work)
- DOCUMENTATION_REGISTER.md (bucket if doc-only)
- IMPLEMENTATION_READINESS_DASHBOARD.md (sprint readiness if scope changed)
- BUG_REGISTER.md (if bugs touched — 6th file when applicable)

### 23.3 Detail

→ CHECKLIST.md (canonical 58-item process discipline)

---

## 24. Learnings

**Canonical:** LEARNINGS.md (L1-L137)

### 24.1 Process Learnings

137 learnings documented across all Passes; latest:
- **L137:** Sprint-tracker assignment discipline (triggered CHECKLIST #58)
- **L136:** Use-case mapping (triggered CHECKLIST #57)
- **L135:** Focus-phase scope filter (triggered CHECKLIST #56)
- **L134:** Phase scope check (triggered CHECKLIST #55)
- **L133:** Test-run audit gate (triggered CHECKLIST #54)

### 24.2 Detail

→ LEARNINGS.md (canonical L1-L137)

---

# PART G — REFERENCE

## 25. Tech Stack Summary

### 25.1 Languages and Runtime

- **Python 3.11+** (primary)
- **JavaScript/TypeScript** (Stage 3+ web dashboards via Vercel)

### 25.2 Data and Storage

- **Parquet** via pyarrow (primary cache format)
- **SQLite** (Stage 3 paper trade event store per DEC-267)
- **Postgres** (Stage 4+ live trade event store per DEC-267)
- **GitHub Actions** (CI/CD + scheduled jobs)
- **Codespace** (Stage 0-3 development; production migration Stage 4 per DEC-272)

### 25.3 Libraries (key)

- **yfinance** (limited use; deprecating live calls per DEC-013/DEC-444)
- **polygon-api-client** (Sprint 1 onwards; DEC-441)
- **fredapi** (DEC-407+448)
- **smartmoneyconcepts** (forked per DEC-045)
- **ib_async** (IBKR integration per DEC-049)
- **freezegun** (PIT regression tests per DEC-050)
- **hypothesis** (property-based testing per DEC-437)
- **vulture** (dead code detection per DEC-217)
- **pydantic** (typed config per DEC-229)
- **python-json-logger** (structured logging per DEC-230)
- **pandas_market_calendars** (NYSE calendar per DEC-235)
- **pytest** + **pytest-benchmark** (testing + perf benchmarks)
- **ruff + black + isort + mypy** (CI gates per DEC-173)
- **memory_profiler** (DEC-179)
- **streamlit** (Stage 3+ dashboards per DEC-048)
- **QuantStats** (performance analytics per DEC-047)

### 25.4 LLM Providers

- **OpenAI GPT-5.4-mini** (Stage 2 backtest per DEC-058)
- **Anthropic Claude** (Stage 3+ live per DEC-058)
- **TradingAgents framework** (DEC-051 phased adoption)

---

## 26. Cost Summary

### 26.1 One-Time Costs

- **Stage 2 backtest agent costs:** ~$300 hard cap (DEC-059)
- **Per-agent ablation:** ~$120 (DEC-211 Option A NARROW SCOPE)
- **Polygon initial cache fetch:** included in $30/mo subscription
- **CPA consultation:** Pre-Stage-4 (DEC-270 — variable cost)

### 26.2 Monthly Recurring (Stage 2 + Stage 3)

| Service | Cost (USD) |
|---|---|
| Polygon Stocks Starter | $30/mo (DEC-441) |
| Quiver Quantitative paid (ALL endpoints) | ~$50-100/mo (DEC-450) |
| Finnhub | (TBD per DEC-410) |
| Unusual Whales | (TBD) |
| Ortex | (TBD) |
| OpenAI API | ~$30-60/mo (Stage 2 backtest agents) |
| Anthropic API | (Stage 3+ only) |
| Vercel | $0 (free tier) |

**Estimated Stage 2 + Stage 3 monthly:** ~$110-220/mo

### 26.3 Stage 4+ Additions

| Service | Cost (USD) |
|---|---|
| IBKR market data subscriptions | ~$10-30/mo (DEC-271) |
| AWS/GCP hosting | ~$30-100/mo (DEC-272) |
| Anthropic API (live agents) | ~$60-120/mo |

**Estimated Stage 4+ monthly:** ~$210-470/mo (~$263 CAD/mo per project memory baseline)

### 26.4 Tools/Libraries

- **All open-source or built-in:** $0/mo
- **GitHub** (free tier): $0/mo

---

## 27. Workflow — Making Changes

### 27.1 Branches

- **`main`:** canonical; PR-only merges (Stage 2+); sync_from_claude.yml manual workflow per DEC-220
- **`claude-updates`:** Claude session work; merged to main via owner-triggered sync_from_claude.yml workflow

### 27.2 sync_from_claude.yml Workflow (per DEC-220)

**Owner-controlled** (workflow_dispatch only; manual trigger from GitHub Actions UI; mandatory description input).

**Improvements per DEC-220 Sprint 6:**
- Header comment documenting governance model
- Replace `--strategy-option=theirs` with `--no-ff` to prevent silent overwrite of owner-edits to main

### 27.3 Daily Updater (Stage 1 legacy)

`update_stocks.yml` cron job runs at 06:00 UTC; commits `index.html` updates. Will phase out as Stage 2+ infrastructure replaces.

### 27.4 Push Pattern

Per CLAUDE.md: Option 3 cached `~/.git-credentials` (chmod 600); required rebase pattern when daily updater commits collide.

---

## 28. Glossary

| Term | Definition |
|---|---|
| Stage | One of 5 project phases (1: Proof of Concept; 2: Strategy Validation; 3: Paper Trading; 4: Live Small Scale; 5: Full Automation) |
| Phase | Sub-phase within a Stage (e.g., Phase 0.A = Polygon Foundation within Stage 2) |
| Sprint | Engineering execution unit (Sprint 1, 2, ...) within a Phase |
| Pass | Audit/decision-making session (Pass 1 to Pass 52+) |
| PIT | Point-in-Time correctness — using as-of-date data, not current data |
| Cube | Dimensional verdict cube (Phase 1B-α, DEC-422; 17+ dimensions) |
| 5-Gate | Strategy validity filter (n≥30, p<0.05, PSR≥0.95, t≥3.4, R:R≥2.0 per DEC-426) |
| Tier | Strategy confidence tier (HIGH/MED/LOW per DEC-021 3-tier system) |
| Arm | A/B test arm (rules / full-agents / no-Risk / no-Bull-Bear per DEC-205) |
| R:R | Risk-Reward ratio (DEC-353 hard reject if R:R < 2.0) |
| REVISIT_AFTER_BACKTEST | Tag indicating empirical tuning needed post-Phase-1B-α |
| CHECKLIST #58 | Process discipline: sprint-tracker assignment in same commit as RESOLVED-DECIDED status flip |
| Option C verification gate | Owner pre-approves exact commit content before push |

---

## 29. Document Map

### 29.1 Canonical Documents

| Document | Role |
|---|---|
| **PROJECT_PLAN.md** (this) | Project entry point; references all registers |
| **TRADING_RULES_AND_INFORMATION.md** | Canonical rules/thresholds detail |
| **AUDIT.md** | Decision narrative detail (~25K lines) |
| **AUDIT_INDEX.md** | Decision status table (462 decisions) |
| **ENGINEERING_REGISTER.md** | Engineering sprint roadmap (~226 ENG decisions) |
| **DOCUMENTATION_REGISTER.md** | Documentation-only decisions (5 buckets, ~80 DOC decisions) |
| **BUG_REGISTER.md** | Bug-decision cross-reference (148 bugs) |
| **IMPLEMENTATION_READINESS_DASHBOARD.md** | Sprint readiness + effort estimates |
| **STRATEGY_REGISTER.md** | Strategy roster (4 layers, ~109-119 strategies) |
| **API_AUDIT.md** | Data source audit (17 APIs across 4 tiers) |
| **LIMITATIONS_CAVEATS_ASSUMPTIONS.md** | Caveats CAV-001 through CAV-071+ |
| **CHECKLIST.md** | Process discipline (58 items) |
| **LEARNINGS.md** | Process learnings (L1-L137) |

### 29.2 Reference Documents

| Document | Role |
|---|---|
| **PROJECT_PLAN_ARCHIVE.md** | Pre-April-2026 historical reference |
| **PASS_53_PRIORITIES.md** | Pass 52 retrospective + Pass 53 priorities |
| **CLAUDE.md** | Claude session context (Push pattern, governance, etc.) |
| **README.md** | Public-facing entry (Stage 1 legacy) |

---

## 30. Pass Retrospectives Reference

### 30.1 Pass 53 Priorities

→ PASS_53_PRIORITIES.md (Pass 52 closure + Pass 53 priorities)

### 30.2 Historical Archive

→ PROJECT_PLAN_ARCHIVE.md (pre-April-2026 reference)

### 30.3 Pass 52 Achievements

Documented in AUDIT.md (turn 124 closure narrative + retrospective).

---

*End of PROJECT_PLAN.md (refreshed Pass 52 turn 127)*
*Per CHECKLIST #25 (honest about scope and references vs duplication); #43 (existing-document inventory); #51 (owner-approved structure executed); #57 (use-case mapping per section); #58 (Single Source of Truth principle — references registers, doesn't duplicate them).*
