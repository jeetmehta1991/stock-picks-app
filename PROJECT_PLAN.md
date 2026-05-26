# Stock Picks & Automated Trading System — PROJECT_PLAN

**Version:** Pass 53 Day 9+ Batch 178 (refreshed 2026-05-15 launch day)
**Status:** Phase 0A complete → Phase 1A launch day. 0 strict blockers. 1882 tests passing / 0 failed. 3 live dashboards on GitHub Pages. Matrix stable 731 (no oscillation).
**Supersedes:** PROJECT_PLAN_v1_outdated.md (April 2026 version, marked outdated post-Pass-52)
**Historical archive:** PROJECT_PLAN_ARCHIVE.md (pre-April-2026 reference)
**Companion:** TRADING_RULES_AND_INFORMATION.md (canonical thresholds + criteria reference)
**Live dashboards:** https://jeetmehta1991.github.io/stock-picks-app/

---

## Document Purpose

This is the **canonical entry point** for understanding the project. It provides project overview, stage objectives, current status, sprint sequencing, and references to specialized registers. Detailed rules and thresholds live in TRADING_RULES_AND_INFORMATION.md (canonical home); decision detail lives in AUDIT.md + AUDIT_INDEX.md; sprint roadmap detail lives in ENGINEERING_REGISTER.md; bug detail lives in BUG_REGISTER.md.

**Do not duplicate content from registers here.** Link to them. This document explains *what the project is*; specialized registers explain *how each piece works*.

---

# PART A — PROJECT OVERVIEW

## 1. Vision and Objective

### 1.1 What this project is

A comprehensive algorithmic trading platform for **swing trading US equities** (and selected Canadian-listed equivalents). The system spans data ingestion, strategy generation, multi-agent verdict layering, statistical validation, and automated execution. Primary goal: high-return performance with medium-high risk tolerance, explicitly accepting drawdowns in pursuit of higher ROI.

### 1.2 Risk philosophy

Per Pass 52 owner-confirmed precedent (DEC-090 REJECTED, DEC-133 REJECTED, DEC-254 unhedged-default):

- **Medium-high risk** — drawdowns explicitly accepted in pursuit of higher ROI
- **Concentration over hard caps** — sector caps, exposure caps rejected; stock-level diversification preferred over sector-level diversification
- **FX exposure accepted** — Canadian-resident with USD trading; default unhedged ETFs (XUU over XSP)
- **Buy-the-dip philosophy** — volatile and crisis markets are entry opportunities, not avoidance triggers
- **Crisis flagging over hard regime blocks** — replaces direction-based regime exclusion

### 1.3 Owner profile

- Canadian resident (Ontario)
- IBKR (Interactive Brokers) Tiered commission account
- Swing trading horizon (multi-day to multi-week holds)
- Personal Windows laptop + VS Code + Claude Code (Pass 53 update — was: GitHub Codespace "vigilant system"; owner switched to local VS Code) for development
- Approval cycle: explicit owner approval per decision via Option C verification gate

### 1.4 Out of scope (explicit)

- **Intraday trading** — separate future project; current scope is swing trading only
- **HFT (high-frequency trading)** — not part of architecture
- **Market making** — not part of architecture
- **Options trading directly** — options data consumed as signal (DEC-258, DEC-145) but not traded directly in current scope
- **International markets** — US equities + interlisted Canadian equivalents only

---

## 2. Five-Stage Roadmap

### 2.1 Stage Map

| Stage | Name | Status | Effort Target |
|---|---|---|---|
| **Stage 1** | Proof of Concept (US gainers + TSX quotes daily HTML) | COMPLETE | done |
| **Stage 2** | Strategy Validation (current pass implementation) | CURRENT — Pass 53 pre-Sprint-1 | ~310-385d realistic |
| **Stage 3** | Paper Trading | Planning | TBD |
| **Stage 4** | Live Trading — Small Scale | Planning | TBD |
| **Stage 5** | Full Automation | Planning | TBD |

### 2.2 Stage 1: Proof of Concept (COMPLETE)

**Deliverable:** Daily-updated dark-themed `index.html` showing US top gainers + TSX quotes.
**Components:** Python `fetch_stocks.py` script + Alpha Vantage API + GitHub Actions cron (06:00 UTC daily).
**Status:** Operational since project inception; daily updates continue.
**Future:** Alpha Vantage to be deprecated per DEC-440 / DEC-455 (replaced by Polygon Stocks Starter per DEC-441).

### 2.3 Stage 2: Strategy Validation (CURRENT)

**Deliverable:** Validated strategy roster with statistical confidence; A/B-tested agent overlay; Phase 1B-α dimensional cube verdict matrix.

**Sub-phases:** See Section 3 (Stage 2 Sub-Phases) below.

**Critical path:** Sprint 0A (Phase 0.A) → Sprint 2 (Engine Bug Fixes) → Sprint 3 (Portfolio Class) → Sprint 7 (Statistical Methodology) → Sprint 7-8 (Phase 1B-α Run).

**Stage 2 success criteria:** See Section 5 + TRADING_RULES_AND_INFORMATION.md Section 1.2.

### 2.4 Stage 3: Paper Trading (planning)

**Deliverable:** 3 months of paper trading mirroring live algo exactly (DEC-198), proving strategy stability beyond backtest.

**Entry criteria (per DEC-028):** Stage 2 statistical validation complete; A/B framework verdicts established; dashboards operational.

**Components:** SQLite trade event store (DEC-267); paper-vs-backtest Bayesian comparison (DEC-268); EOD reconciliation reports (DEC-181); weekly performance reviews (DEC-182).

**Stage 3 → Stage 4 numeric gates:** See TRADING_RULES_AND_INFORMATION.md Section 1.3 (DEC-269).

### 2.5 Stage 4: Live Trading — Small Scale (planning)

**Deliverable:** Small-capital live trading via IBKR (DEC-054 + DEC-049 ib_async).

**Entry prerequisites:**
- Stage 3 paper trading proves profitable
- CPA consultation completed (DEC-270)
- Tax classification confirmed (DEC-035)
- Cloud infrastructure migrated from Codespace (DEC-031, DEC-272)
- Disaster recovery operational (DEC-273)
- Real-time data feed activated (DEC-271)
- Production-grade Stage 4 cluster: secrets manager (DEC-094), monitoring/alerting (DEC-095), kill switch (DEC-139), daily loss limits (DEC-034)

**Capital:** Per DEC-029 (split 029-A/B/C; specifics TBD).

### 2.6 Stage 5: Full Automation (planning)

**Deliverable:** Full automation operational at scale.

**Components:** Hosting at scale (DEC-272); operational runbooks (DEC-180); ongoing performance reviews (DEC-182); strategy decay monitoring (DEC-249); quarterly re-validation (DEC-214).

### 2.7 Stage Transition Gates

Detailed numeric gates per stage live in **TRADING_RULES_AND_INFORMATION.md Section 1**.

---

# PART B — CURRENT STAGE: STAGE 2 STRATEGY VALIDATION

## 3. Stage 2 Sub-Phases

Stage 2 is the largest scope phase. Decomposed into sub-phases corresponding to engineering sprints.

### 3.1 Phase 0.A — Polygon Foundation (Sprint 1)

**Owner action prerequisite:** Subscribe to Polygon Stocks Starter $29/mo per DEC-441/478/479 (Pass 53 RESOLVED-DECIDED — cost corrected from $30, tier confirmed as Stocks Starter).

**Scope:** Build PIT-correct foundational data infrastructure on Polygon (replacing Alpha Vantage). PIT loader (DEC-040), cache fixes (DEC-307-310), prefetch checklist (DEC-256-261), NYSE calendar (DEC-235), data integrity (DEC-117-118), sentiment refresh (DEC-318-320 + DEC-390-391), multiprocess safety (DEC-328-329).

**Effort:** ~20.5-26.5 engineering days post-Phase-2-cleanup-batch.

**Detail:** ENGINEERING_REGISTER.md → Sprint 0A.

### 3.2 Phase 0.B — Portfolio Class (Sprint 3)

**Resolves CRITICAL OPEN bug:** BUG-095 (no Portfolio class blocks DEC-070/076/091).

**Scope:** Build Portfolio class as foundational architecture for position sizing, risk management, and multi-strategy coordination. Per-strategy promotion workflow (DEC-277), dynamic notional sizing (DEC-339).

**Effort:** ~8-11 engineering days.

**Detail:** ENGINEERING_REGISTER.md → Sprint 3.

### 3.3 Phase 0.C — Engine Bug Fixes Tier A (Sprint 2)

**Scope:** Resolve 14 Tier A engine bug-fix decisions surfaced during Pass 52: close_trade NameError (DEC-293), duplicate ClosedTrade (DEC-294), borrow cost reconciliation (DEC-295/327/399), test fixture (DEC-296/297), PIT guard RAISE (DEC-305), get_news_sentiment path (DEC-306), trailing-stop ATR (DEC-311/313), exit_hybrid max_days (DEC-312), circuit breakers L3+4 (DEC-314/315), conversion logic (DEC-338), correlation matrix (DEC-340).

**Effort:** ~25.5-30.5 engineering days.

**Detail:** ENGINEERING_REGISTER.md → Sprint 2.

### 3.4 Phase 0.D — ICT/SMC Fork Integration

**Scope:** Fork-existing strategy adoption (DEC-045) — integrate `smartmoneyconcepts` library. ICT/SMC pre-cache (DEC-259), timeframe scope (DEC-345), Multi-TF non-ICT (DEC-350).

**Effort:** Tracked across Sprints 1 + 8.

### 3.5 Phase 0.E — Catch-Mechanism Defense + Architecture Hygiene (Sprint 6)

**Scope:** 5-Layer Catch-Mechanism Defense (DEC-417/436/437/438/439) + Architecture Hygiene (DEC-217/218/219/220) + A/B foundation (DEC-205/206) + Test/Cache/Data Quality cluster (DEC-222/229-235/241) + Risk Management decisions (DEC-018/135/136) + Code Quality (DEC-170-173/177-179/183) + DEC-251 dependency injection sandbox-prototype.

**Effort:** ~62.25-76.75 engineering days (largest absolute sprint after Sprint 7).

**Detail:** ENGINEERING_REGISTER.md → Sprint 6.

### 3.6 Phase 1A — Rules-Based + Smart Money Baseline (Sprint 6.5)

**Scope:** Rules-only execution layer running the full strategy roster on the full universe with smart money signals, NO agent overlay (`--no-agents` flag preserved from Phase 1A v3 archive). Produces baseline trade outcomes that feed A/B Arm A (rules-only) downstream. Smart money signals (DEC-124 confluence + DEC-332 weights + DEC-450 Quiver paid endpoints) are part of rules-based screening, not agents.

**Why this phase exists:** Original Phase 1A (PROJECT_PLAN_ARCHIVE) ran rules-only on 67 instruments × 4 years validating pipeline cleanliness + confirming `atr_trail_1x` as primary exit (20/29 strategy comparisons). Phase 1A in this restored framing extends that pattern: rules + smart money baseline must be validated BEFORE agent overlay layer is added in Phase 1B. Skipping this phase would mean A/B Arm A has no independently-validated baseline.

**Effort:** ~6-8 engineering days (most infrastructure already exists from prior Phase 1A v3 work; this is re-execution on new Sprint 0A cache + DEC-477 universe + Sprint 5 tier definitions).

**Detail:** ENGINEERING_REGISTER.md → Sprint 6.5 (NEW).

### 3.7 Phase 1A-α — Rules-Only Dimensional Cube + Dashboards (Sprint 6.5-7)

**Scope:** Cube populator + 5-Gate verdict + Dashboard 1 (Cube Explorer DEC-199 — rules-only view) + Dashboard 2 (ICT/SMC Audit DEC-200) consuming Phase 1A trade outcomes ONLY (no agent arms). Identifies which strategies pass without agents — establishes the pre-agent baseline verdict per strategy × regime × cell. Mirrors Phase 1B-α structure but applied to single-arm rules-only data.

**Why separate from 1B-α:** Allows owner to evaluate rules-only verdict BEFORE committing $300 budget for full agent-overlay run (Phase 1B-α). If rules-only baseline is weak (Sharpe < 0.7 OOS, no PASS cells), agent overlay justification drops sharply — possibly avoid running 1B at all.

**Effort:** ~10-14 engineering days (cube infrastructure built here; Phase 1B-α reuses).

**Detail:** ENGINEERING_REGISTER.md → Sprint 6.5-7.

### 3.8 Phase 1A-β — Exhaustive Search: Find Winners (Sprint 7 Day 1+)

**Scope (Pass 53 Day 9+ 2026-05-19 architecture clarification per owner Q):** Exhaustive backtest across ALL strategies × ALL tickers × FULL timeframe. Universe = 1937 (Master Dedup 5-tier per DEC-504). Strategies = ~180 (Layer 1 baseline 60 + T1.1-T1.5 16 + Phase 1C+ ~80-100). Timeframe = 2022-05-05 → 2026-05-05 (4y).

**Primary output:** Per-(strategy × exit-method × regime) winner identification. The 9-criteria gate (per PROJECT_PLAN §3.5) determines which combinations show edge at scale. This winner list directly feeds Phase 1B-α agent overlay scope.

**Why exhaustive (not pre-filtered):** Pre-filtering would require knowing which strategies work at full universe — that's the question Phase 1A-β answers. Sub-sampling (e.g., T1a only) would miss strategies whose edge is concentrated in T2/T3 small-caps. Owner directive 2026-05-19: test all, then narrow.

**Secondary outputs:** Pipeline integrity verification (cache corruption, PIT regression, multi-process race conditions, memory ceiling, walk-forward fold contamination); refreshed cube + dashboards.

**Effort:** ~3-5 engineering days + ~5-7 days compute wall time at 5-batch parallel (1937 × 180 × 4y is heavier than original 1015 × 60 × 4y baseline).

**Detail:** ENGINEERING_REGISTER.md → Sprint 7 Day 1. [STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md](STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md) canonical post-Phase-1A-α build plan.

### 3.9 Phase 1B — Statistical Methodology + A/B (Sprint 7)

**Scope:** Statistical methodology cluster (DEC-080-085 phases + DEC-107-111 + DEC-144/152/153/155) + A/B operational (DEC-207-216 + DEC-242) + Distribution analysis + AgentGateConfig (DEC-459 Option C Hybrid; supersedes DEC-042) + Custom Toolkit + LangGraph state augmentation (DEC-462-468 per TRADINGAGENTS_DATA_AUDIT.md) + Performance metrics canonicalization + Regime classifier improvements.

**Entry criteria:** Phase 1A + 1A-α complete with non-trivial PASS cell count; rules-only baseline Sharpe ≥ 0.7 OOS (else owner reviews whether agent overlay justified).

**Effort:** ~76-85 engineering days (LARGEST sprint).

**Detail:** ENGINEERING_REGISTER.md → Sprint 7.

### 3.10 Phase 1B-α — Agents on Winners + Combined Cube (Sprint 7-8)

**Scope (Pass 53 Day 9+ 2026-05-19 architecture clarification per owner Q):** DEC-422 Phase 1B-α dimensional cube infrastructure (DEC-425/427/428/429/431) + Dashboard 3 spec (DEC-201 — agent overlay analysis) + parallel backtest execution (DEC-184) + per-trade explainability (DEC-119) + loss attribution (DEC-120) + 17+ categorical breakdown variables (DEC-100/144) + TradingAgents 5-tier→size (DEC-062).

**WINNERS-ONLY APPLICATION (canonical per owner directive 2026-05-19):** Phase 1B-α does NOT run agents over the full universe. It applies the 11-agent pipeline ONLY to winning (strategy × exit-method × regime) combinations identified by Phase 1A-β verdict. This determines whether agents OPTIMIZE ROI of already-validated baseline strategies. A/B comparison framework (DEC-131/207-216/242) operates on the same winners subset.

**Why winners-only:** Running agents over full universe ($300 estimate) would waste resources testing agents on strategies that haven't proven baseline edge. Instead, baseline edge is established in Phase 1A-β (exhaustive search); Phase 1B-α tests the orthogonal question "do agents add value to already-winning combos."

**Budget:** $300 ceiling pre-approved (per owner 2026-05-19). Actual cost typically ~$50-150 because winning combinations are a subset of the full screening firehose (~20-40% of strategy roster passes 9-criteria gate at scale).

**Note:** Cube infrastructure (populator + 5-Gate verdict logic) was built in Phase 1A-α; Phase 1B-α reuses and extends with agent arms.

**Effort:** ~28-38 engineering days.

**Detail:** ENGINEERING_REGISTER.md → Sprint 7-8. [STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md](STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md) canonical post-Phase-1A-α build plan.

### 3.11 Phase 1C+ — Strategy Categories Expansion (Sprint 8)

**Scope:** Strategy roster additions: chart pattern strategies (DEC-355-362) + DEC-067 9 exit methods (planned target; live `len(EXIT_STRATEGIES)`=25 Pass 53) + DEC-075 AEP + DEC-368 Calendar/Seasonal + DEC-370 Index Rebalance + DEC-371 within-category gaps + DEC-352 13F price-level + DEC-174 strategy classification + DEC-175 signal persistence + DEC-076-079 (deferred sub-decisions per Pass 52 #56 scope filter) + multi-TF (DEC-350) + ICT/SMC (DEC-345).

**Effort:** ~37-55 engineering days (parallel-able; not critical path).

**Detail:** ENGINEERING_REGISTER.md → Sprint 8.

---



## Sprint 0A note (Pass 53 owner directive 2026-05-05; DEC-497)

Sprint 1 has been **renamed → Sprint 0A** with materially expanded scope:
- **Multi-API prefetch** — all 8 planned APIs (Polygon, Quiver Trader, FRED, ALFRED, AAII, CNN F&G, CFTC COT, SEC EDGAR), not Polygon-only
- **Universe build absorbed** — Pass 53 IMPLEMENTED (614 T1a + 161 T1c + 27 ETFs + T2/T3 SCREENERs)
- **Stage 2 NO-LIVE-API refactor** — backtest reads from `data_prefetch/` only; HARD CUT (owner directive Q8)
- **Smoke + demo tests per API** — 16 test files (8 smoke + 8 demo), separate per API per owner directive
- **18-classifier sector normalization** (DEC-499) — GICS-11 + Fixed Income/Commodities/Volatility/Broad Market/International/Emerging Markets/Small Cap

Phasing: Sprint 0A.0-0A.10 (see ENGINEERING_REGISTER for sub-phase detail). Effort: ~6-10 days code + ~25 hours prefetch wall time. Excluded: dashboards (DEC-199/200/201 → Sprint 9), engine bugs (DEC-491-493 → Sprint 2), T1b R1000 (deferred Stage 3 per DEC-365), strategy compute.

## 4. Sprint Roadmap Index

**Canonical detail:** ENGINEERING_REGISTER.md (~226 ENG decisions tracked across 9 sprints + sub-sprint blocks).

### 4.1 Sprint dependency graph

```
                Phase 0.A Multi-API Prefetch (Sprint 0A)
                            |
            +---------------+---------------+
            |               |               |
    Engine Bugs A      Portfolio Class    DEC-410 Audit
    (Sprint 2)         (Sprint 3)         (Sprint 4)
            |               |               |
            +---------------+---------------+
                            |
                Universe Mgmt (Sprint 5)
                            |
                Phase 0.E + Hygiene (Sprint 6)
                            |
            Statistical Methodology + A/B (Sprint 7)
                            |
                Phase 1B-α Run (Sprint 7-8 + Sprint 9)

  Strategy Categories (Sprint 8) — parallel, not critical path
```

### 4.2 Sprint Table

| Sprint | Name | Effort (post-Phase-2) | Critical Path? |
|---|---|---|---|
| Sprint 0A | Phase 0.A Multi-API Prefetch + Polygon Foundation | ~20.5-26.5d | YES |
| Sprint 2 | Engine Bug Fixes Tier A | ~25.5-30.5d | YES |
| Sprint 3 | Phase 0.B Portfolio Class | ~8-11d | YES (BUG-095) |
| Sprint 4 | DEC-410 Audit Findings | ~41.75-54.25d | YES (largest growth) |
| Sprint 5 | Universe Management | ~13.5-15.5d | YES |
| Sprint 5 NEW | Position Sizing | ~3.5d | parallel |
| Sprint 6 | Phase 0.E + Hygiene | ~62.25-76.75d | YES |
| Sprint 7 | Statistical Methodology + A/B + AgentGate | ~76-85d | YES (largest) |
| Sprint 7-8 | Phase 1B-α Dimensional Cube + Dashboards | ~28-38d | YES |
| Sprint 8 | Strategy Categories | ~37-55d | parallel |
| Sprint 9 | Phase 1B-α Run + ongoing | ~6d | YES (phase gate) |

### 4.3 Critical path

Sprint 0A → Sprint 3 (BUG-095) → Sprint 7 (statistical methodology) → Sprint 7-8 (Phase 1B-α verdict). Total critical path: **~125-160 engineering days minimum**.

### 4.4 Parallel-able sprints

Sprints 4, 6 partially parallel with Sprints 1-3 once foundations established. Sprint 5 partially parallel after Sprint 0A. Sprint 8 fully parallel after Sprint 0A.

### 4.5 Detail

ENGINEERING_REGISTER.md is canonical for sprint-by-sprint decisions, test signals, effort breakdowns. IMPLEMENTATION_READINESS_DASHBOARD.md is canonical for sprint readiness gates.

### 4.6 Dashboard coverage across phases (Pass 53)

Stage 2 dashboard coverage spans all 11 phases per [DETAILED_PROJECT_PLAN.md Part 2.5](DETAILED_PROJECT_PLAN.md). Three tiers:
- **Tier 1 (engineering verification):** Phase 0.A Prefetch Coverage Report (NEW Sprint 0A, ~0.5d). Phases 0.B/0.C/0.E marked N/A — verification via CI test signals + sprint demo.
- **Tier 2 (analytical baseline):** Phase 1A Trade Summary Dashboard (NEW Sprint 6.5, ~2-3d) + Phase 1B Trade Summary Dashboard (NEW Sprint 7, ~2-3d). Both Streamlit ports of legacy `analysis_dashboard_1a/1b.html` 9-tab archive — adaptations of DEC-199 family (no new DECs).
- **Tier 3 (cube + verdict):** DEC-199 Cube Explorer + DEC-200 ICT/SMC Audit (Phase 1A-α + 1B-α + reused 1A-β + 1C+) + DEC-201 Agent Overlay Analysis (Phase 1B-α only).

Phase 0.D ICT/SMC primitive verification folded into DEC-200. Total NEW dashboard effort: ~5-7 engineering days. See [TRADING_RULES.md §2.1-§2.11](TRADING_RULES_AND_INFORMATION.md) for per-phase dashboard callouts.

---

## 5. Stage 2 Success Criteria

### 5.1 Quantitative gates (Phase 1B-α verdict per DEC-269)

Stage 2 → Stage 3 transition requires:
- **Sharpe ≥ 1.0** out-of-sample (per DEC-269)
- **Max DD ≤ 25%**
- **Win Rate threshold per category** (DEC-083 TIERED min trades floor)
- **A/B clear** — full-agents arm > rules-only arm by ≥ 0.2 net Sharpe (per DEC-131)
- **Divergence < 20%** rules-vs-agents
- **5-Gate validity passed** (DEC-426): n ≥ 30, p < 0.05 Bonferroni-corrected, PSR ≥ 0.95, t-stat ≥ 3.4, R:R ≥ 2.0

Detail: TRADING_RULES_AND_INFORMATION.md Section 1.2 + Section 3.

### 5.2 Phase-specific milestones

Per phase acceptance criteria documented per sprint in ENGINEERING_REGISTER.md.

### 5.3 Stage 2 → Stage 3 transition

Owner reviews Phase 1B-α dimensional cube verdicts (DEC-422). If majority of strategies pass 5-gate validity AND A/B framework shows agent value-add, transition approved.

---

# PART C — ARCHITECTURE

## 6. Universe Architecture (Three Tiers)

Reference: STRATEGY_REGISTER.md + ENGINEERING_REGISTER.md decisions DEC-303/331/364-380.

### 6.1 Tier 1: S&P 500 + Selected ETFs

- **Source:** S&P 500 Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv per DEC-303 (CC0 dataset DEC-052)
- **Liquidity floor:** $10M ADV per DEC-366
- **History minimum:** 250 trading days
- **Primary backtest universe**

### 6.2 Tier 2: Spinoffs/IPOs (high-cap, short-history)

- **Source:** SEC EDGAR Form 10-12B feed (DEC-379) + Polygon corporate actions (DEC-380)
- **Liquidity floor:** $5M ADV
- **Market cap minimum:** $2B
- **History minimum:** 20 days (`LIMITED_HISTORY` flag respected)
- **Auto-population:** DEC-372/373/374 phased

### 6.3 Tier 3: Momentum top-100 watchlist

- **Source:** Auto-populated via DEC-104 + DEC-364/375/376/377
- **Liquidity floor:** $5M ADV
- **Market cap minimum:** $300M
- **History minimum:** 60 days
- **Refresh:** Monthly via GitHub Actions (DEC-376)

### 6.4 Universe management

ETF list reconciliation (DEC-331), `--validate` mode (DEC-373), delisting registry + survivorship correction (DEC-147), corporate actions handler (DEC-146).

Detail: ENGINEERING_REGISTER.md Sprint 5 + STRATEGY_REGISTER.md.

---

## 7. Strategy Universe Index

**Canonical home:** STRATEGY_REGISTER.md.

### 7.1 Strategy taxonomy (4 layers)

| Layer | Description | Count |
|---|---|---|
| Layer 1 | Baseline roster (60 strategy classes per archived PROJECT_PLAN section 6 = baseline; live `len(ALL_STRATEGIES)`=186 includes later layers Pass 53) | 60 |
| Layer 2 | Phase 0.D additions (ICT/SMC + Earnings Momentum + Calendar) | TBD |
| Layer 3 | Pass 52 RESOLVED-DECIDED additions (chart patterns DEC-355-362 + categories DEC-367-371) | 13 |
| Layer 4 | PENDING strategy-additive sub-decisions (DEC-141/142/143/145/176 per STRATEGY_REGISTER.md Layer 4) | ~5-6 |

### 7.2 Total strategy count

Approximately **~108-118 classes** post-Phase-1C (per BUG-111 resolution Sprint 8 + DEC-355-362 chart patterns + DEC-368/370/371 category additions + Layer 4 pending). Exit methods (DEC-067) are tracked separately — see DETAILED_PROJECT_PLAN.md §2.4.5 and TRADING_RULES.md §8. The AEP breaker (DEC-435) is a portfolio guard, not a strategy — see TRADING_RULES.md §9.

### 7.3 Detail

STRATEGY_REGISTER.md is canonical.

### 7.4 Layer 1 — 60-strategy enumeration (RESTORED Pass 53 inline per Q2 owner directive)

*(Restored from PROJECT_PLAN_ARCHIVE.md / Pass 44 commit `bb6335d6`. Eliminated by Pass 52 turn 128 REFRESH; owner Q2 Pass 53 2026-05-05: "Restore inline".)*

| Category | Count | Examples |
|---|---|---|
| **Momentum / Trend** | 12 | 50/200 SMA cross, breakout from base, sector momentum rotation, MACD bull cross + above 200 EMA + ADX>25, Donchian 20 breakout, MA stack 9/21/50, prior swing-high breakout, Hull MA flip up, Supertrend flip up + price above 200 EMA, ROC + RSI midline, Aroon Up cross, sector RS rotation |
| **Mean Reversion** | 10 | Oversold bounce, RSI divergence, Bollinger reversion (lower band touch + RSI<30), Keltner channel mid-band test, mean-reversion-after-gap, MFI oversold + price >200 EMA, z-score >2 reversion, gap-fill, Stochastic K cross above 20, support-zone bounce |
| **Smart Money** | 8 | Congressional cluster buy (DEC-124 confluence), insider CEO+cluster buy, 13F accumulation Q-over-Q, gov contracts + congressional buy, insider buy + low-IV setup, 13F new initiator, congressional pre-earnings, insider Form 4 + analyst upgrade |
| **Volatility** | 7 | VIX spike fade, IV crush + post-earnings drift, vol contraction breakout, low-vol pullback to MA, BBW expansion + breakout direction, ATR rank low + breakout, vol-targeting overlay |
| **Fundamental** | 8 | Earnings momentum (post-EPS beat drift), analyst upgrade clusters, buyback announcements, dividend hike, EPS estimate revision up, revenue surprise, margin expansion, capex cut + buyback |
| **Macro / Regime** | 6 | Yield-curve normalization trades, crisis dip-buying (regime=crisis_CRISIS_FLAG longs at 50% size), sector rotation (defensive→cyclical), USD weakness + commodities, Fed pivot trades, bond-stock correlation breakdown |
| **Event-Driven** | 9 | Spinoffs (DEC-103 cap >$5B + 90d history), M&A arbitrage, post-IPO drift (>$10B IPO + 90d), earnings PEAD, FDA approval drift, S&P 500 inclusion drift, index-rebalance front-run, dividend ex-date arb, secondary offering drift |

**Strategy attributes (Layer 1):**
- **`earnings_tolerant`** (DEC-013 REVISED): PEAD and earnings-momentum strategies ignore earnings proximity. Others reduce size 0.75× within 7 days, 0.5× within 3 days
- **Confidence tier:** 5% / 4% / 3% / 1.5% / 0.75% position size based on signal quality (per DEC-021)
- **CVD-dependent strategies dropped** per DEC-046 (daily OHLCV cannot produce real Cumulative Volume Delta)

**Layer 2-4 detail:** see STRATEGY_REGISTER.md per-layer enumeration. Layer 2 ICT/SMC strategies use `smartmoneyconcepts` library fork per DEC-045. Layer 3 chart patterns DEC-355-362. Layer 3B categories DEC-367-371. Layer 4 PENDING DEC-141/142/143/145.

---

## 8. Signal Universe (~220 fields per instrument per day)

Reference: ENGINEERING_REGISTER.md decisions DEC-118/106/107/etc.

### 8.1 Technical signals (~80 fields)

- OHLCV + derived (returns, ATR, RSI, MACD, MA, momentum, volatility bands)
- Multi-timeframe (Daily + Weekly per DEC-345; extension via DEC-350)
- ICT/SMC concepts (FVG, BOS, CHoCH, order blocks, liquidity grabs) per DEC-259
- Chart pattern primitives (swing highs/lows; retest detection per BUG-111 Sprint 8)
- Indicators (chandelier, PSAR, supertrend, volume climax, RSI extreme) per DEC-432

### 8.2 Smart money signals (~50 fields)

- Insider trading (Form 4 actual + Form 144 proposed) per DEC-125
- Congressional disclosure (Quiver paid endpoints) per DEC-450 + DEC-324
- 13F institutional (filing_date PIT) per DEC-325 + DEC-352
- Cross-source clusters (3+ source confluence) per DEC-124
- Exponential decay weights (90-day half-life default REVISIT) per DEC-123
- Composite weights configurable per DEC-332
- Hand-rolled (NOT Quiver pre-built) per DEC-073

### 8.3 Macro signals (~40 fields)

- FRED expansion (9 series: VIX, DGS10, T10Y2Y, FEDFUNDS, UNRATE, CPIAUCSL, T10YIE, BAA10Y, DXY) per DEC-085 + DEC-407+448
- ALFRED archival FRED for vintage data per DEC-301
- Cross-asset (HY spread, IG spread, DBA, GSCI, sector ETFs, TLT, HYG, SHY) per DEC-118
- CPI/NFP/FOMC dates auto-extend per DEC-304
- Regime classifier 8+ inputs per DEC-106 (extended to 12+ multi-asset per DEC-150)

### 8.4 Sentiment signals (~30 fields)

- AAII pub-lag N+1 trading day shift per DEC-318
- AAII auto-refresh weekly script per DEC-319 + DEC-390
- CNN F&G no interpolation; (value, last_published, age_days) tuple per DEC-320 + DEC-391
- WSB separated from smart money per DEC-072
- News sentiment (Polygon news endpoint per DEC-441)

### 8.5 Other signals (~20 fields)

- Event flags (FOMC / earnings / CPI suppression per DEC-348/349)
- Liquidity metrics (ADV, fail-closed per DEC-321)
- Sector rotation (per DEC-323 + DEC-151)
- Borrow cost (consolidated per DEC-399)

Detail: ENGINEERING_REGISTER.md per-decision specifications.

---

## 9. Agent Architecture (TradingAgents Framework)

Reference: TRADING_RULES_AND_INFORMATION.md Section 7 (canonical AgentGateConfig spec).

### 9.1 11 agents per propagate()

Per DEC-051 staged adoption + DEC-057 (Social Analyst disabled). 11 agents from TradingAgents framework consumed per trade-decision propagate().

### 9.2 LLM provider strategy

Per DEC-058: GPT-5.4-mini for backtest (cost-optimized; DEC-055), Anthropic for live (Stage 4+ when correctness premium > cost). Skip TradingAgents CLI per DEC-056.

### 9.3 AgentGateConfig spec

**Canonical detail:** TRADING_RULES_AND_INFORMATION.md Section 7.

Summary: OPTION C HYBRID ARCHITECTURE per DEC-459 (supersedes DEC-042 turn 121 spec; DEC-459 Pass 52 turn 129):
- Primary signal: TradingAgents Portfolio Manager native confidence consumed directly (NOT re-aggregated)
- Risk veto layer: separate `s_risk ≥ 0.5` hard gate via LangGraph state extraction
- Bull/Bear alignment: Research Manager synthesis-level check (RM confidence ≥ 0.5 AND direction matches PM)
- Tier mapping from PM confidence: HIGH ≥0.8 (5%), MED 0.65-0.8 (3%), LOW 0.5-0.65 (1.5%) per DEC-021
- Custom toolkit + LangGraph state augmentation required (DEC-462-468 per TRADINGAGENTS_DATA_AUDIT.md)

### 9.4 A/B framework (5 arms per DEC-459)

Per DEC-205-216 cluster + DEC-459:
- Arm A: Rules-only (no agents)
- Arm B: Full-agents-with-veto (default AgentGateConfig per DEC-459)
- Arm C: No-Risk (Risk veto disabled — collapses to pure PM-native)
- Arm D: No-Bull-Bear-align (Research Manager alignment check disabled)
- Arm E: Ablation per DEC-211 (per-phase weight variations)

Tested across 17+ dimensions per DEC-422 cube; pre-commit min sample 300 paired trades per DEC-207; per-regime verdicts per DEC-209.

### 9.5 Agent ablation studies

Per DEC-211 (Option A NARROW SCOPE): 7-arm runs ONLY post-Phase 1B-α 4-arm completion; sample-bounded top-20% strategies × ~5K trades. Cost ~$120 one-time + ~$30-60/month.

Detail: TRADING_RULES_AND_INFORMATION.md Section 18.

---

## 10. Data Sources by Stage

**Canonical detail:** API_AUDIT.md (DEC-410 17-API audit complete).

### 10.1 Stage 1 (current)

- **Alpha Vantage:** US gainers + TSX quotes (deprecating per DEC-440 / DEC-455)

### 10.2 Stage 2

- **Polygon Stocks Starter $29/mo** (per DEC-441) — replaces Alpha Vantage
- **FRED + ALFRED** (free tier; archival via ALFRED per DEC-301)
- **Quiver Quantitative** (paid tier ALL endpoints per DEC-450)
- **Finnhub** (free + selected paid)
- **yfinance** (deprecating per DEC-444 — earnings via Polygon DEC-256; .info via Polygon reference DEC-447)

### 10.3 Stage 3

- All Stage 2 sources +
- **IBKR paper trading** (real-time data feed per DEC-054 + DEC-049 ib_async)

### 10.4 Stage 4+

- All Stage 3 sources +
- **IBKR market data subscriptions** (~$10-30/month per DEC-271)

### 10.5 Cost summary

Full Stage 5 stack: ~$263 CAD/month (per project memory).

Detail: API_AUDIT.md per-API specification with use-case mapping.

---

# PART D — RULES & THRESHOLDS

## 11.B Confidence Tiers, Position Sizing, Tier Adjustment (RESTORED Pass 53 inline per Q2)

*(Restored from PROJECT_PLAN_ARCHIVE.md / Pass 44 commit `bb6335d6`. Eliminated by Pass 52 turn 128 REFRESH; owner Q2 Pass 53 2026-05-05: "Restore inline".)*

### 11.B.1 Stage 1 (rule-based preliminary tier)

Based on signal counts and smart money:

| Tier | Triggers | Position size |
|---|---|---|
| EXCEPTIONAL | 3+ strategies fire AND congressional cluster buy AND insider cluster buy | 5% of capital |
| VERY HIGH | 2+ strategies fire AND 1+ smart money signal | 4% |
| HIGH | 2+ strategies fire OR 1 strategy + smart money | 3% |
| MEDIUM-HIGH | 1 strategy fire + supporting context | 1.5% |
| MEDIUM | 1 strategy fire alone | 0.75-1% (Stage 3+ only) |
| LOW / AVOID | Below minimum or contradicted | watch-only |

### 11.B.2 Stage 2 (TradingAgents 5-tier overlay) — DEC-061 Option 1 / DEC-481 Option C2 Hybrid

TradingAgents Portfolio Manager outputs Buy/Overweight/Hold/Underweight/Sell. Maps to tier adjustment:
- **Buy** → upgrade preliminary tier by 1 level
- **Overweight** → priority flag within tier (stay in tier, prioritize for execution)
- **Hold** → no change
- **Underweight** → downgrade preliminary tier by 1 level
- **Sell** → downgrade to AVOID (do not trade)

AVOID tier never upgrades regardless of agent rating.

DEC-481 Option C2 Hybrid (PROPOSED Pass 52 turn 133) supersedes DEC-459 Option C — TradingAgents v0.2.4 uses 5-tier rating, not numeric confidence; SignalProcessor reads rating from rendered markdown via deterministic heuristic.

### 11.B.3 Position size multiplier stack

```
position_size = base × tier_multiplier × earnings_modifier × vol_targeted × drawdown_modifier
```

- `tier_multiplier`: 5% / 4% / 3% / 1.5% / 0.75% / 0 per table above
- `earnings_modifier`: 1.0 if earnings_tolerant=True; else 0.75× within 7d / 0.5× within 3d
- `vol_targeted`: pending DEC-023 (inverse-ATR sizing)
- `drawdown_modifier`: pending DEC-022 (step function at -5/-10/-15%)

Floor: combined multiplier < 0.10% → skip as `below_minimum_size`.

**Canonical thresholds:** TRADING_RULES_AND_INFORMATION.md (this section is summary; thresholds may be revised there post-backtest per REVISIT_AFTER_BACKTEST tags).

---

## 11.D Backtest window + walk-forward methodology (DEC-505 Pass 53 owner directive 2026-05-05)

**Owner directive:** "Remove backtest windows for these 16 months. Why would it make sense to use these windows for testing if we have no data for these. Develop testing windows within the 5 year data we already have."

### Locked Stage 2 backtest window

| Constant | Value | Purpose |
|---|---|---|
| `DATA_LOAD_START` | 2021-05-05 | Warmup window start (Polygon Stocks Starter cache start; 252-day indicator computation begins here) |
| `BACKTEST_START` | 2022-05-05 | First tradeable date (post 1y warmup; signals fire from this date forward) |
| `BACKTEST_END` | 2026-05-05 | Polygon cache end (locked) |

**Total window:** 5.0 years (1y warmup + 4y tradeable).

### Walk-forward folds (DEC-505 supersedes DEC-109's 6-fold spec)

| Fold | OOS test window | Rationale |
|---|---|---|
| Fold 1 | 2022-05-05 → 2023-05-05 | Post-warmup; first OOS test |
| Fold 2 | 2023-05-05 → 2024-05-05 | |
| Fold 3 | 2024-05-05 → 2025-05-05 | |
| Fold 4 | 2025-05-05 → 2026-05-05 | Most recent year |

DEC-109 (6 folds × 1y) required 6+ years of data; Polygon delivers 5y; owner declined Stocks Developer/Advanced upgrade per DEC-501 spirit ("No upgrade. Lets stick to what we have"). Reduced to 4 folds + 1y warmup = full 5y utilization.

### Sample-size floor preserved (L99)

L99 + DEC-269 require ≥143 independent positions per strategy. With 4 OOS folds × ~100-200 trades/strategy/year ≈ 400-800 per-strategy trades — comfortably above floor.

### Per-fold compute (revised from DEC-109 estimate)

- Per fold: ~509 T1 + variable T2/T3 ≈ 5-8 hr wall time
- Total Phase 1B-α run: 4 folds × 5-8 hr = **20-32 hr** (was 30-50 hr for 6 folds; ~33% reduction)

### Code references

- `backtest/config.py`:
  - `BACKTEST_START = date(2022, 5, 5)`
  - `BACKTEST_END = date(2026, 5, 5)`
  - `DATA_LOAD_START = date(2021, 5, 5)`
  - `WALK_FORWARD_FOLDS = [(2022-05-05, 2023-05-05), (2023-05-05, 2024-05-05), (2024-05-05, 2025-05-05), (2025-05-05, 2026-05-05)]`

### Joint decisions

- DEC-505 (this rule) — supersedes DEC-109 6-fold spec
- DEC-269 — numeric gates unchanged (Sharpe / DD / win rate are relative to backtest, not absolute time)
- DEC-478 — Polygon tier (owner declined upgrade)
- DEC-501 — superseded Pass 53 by DEC-506 (Polygon Options Stage 2 IN-SCOPE; subscription deferred to point-of-need per owner directive 2026-05-05)
- L99 — sample-size floor preserved

---

## 11.C Stage 2 → Stage 3 Validation Gates (RESTORED Pass 53 inline per Q2)

*(Restored from PROJECT_PLAN_ARCHIVE.md / Pass 44 §11. Eliminated by Pass 52 turn 128 REFRESH; owner Q2 Pass 53 2026-05-05: "Restore inline".)*

Stage 2 must pass these gates before Stage 3 paper trading:

| # | Gate | Threshold | Source |
|---|---|---|---|
| 1 | **Edge over baseline** | Stage 2 (full agents) Sharpe ≥ rules-only Sharpe + 0.2 absolute OR 0.15 relative | DEC-131 |
| 2 | **Per-strategy minimum** | ≥500 trades AND ≥143 independent positions per L99 (3.5× row inflation correction) | L99 |
| 3 | **Regime breakdown** | Per-regime PASS in ≥1 of 4 regimes (calm/neutral/volatile/crisis per DEC-106); not universal-pass required | DEC-209 |
| 4 | **Drawdown bounded** | Max drawdown ≤ 25% across full backtest | DEC-269 |
| 5 | **Walk-forward consistency** | Out-of-sample Sharpe within 0.5 of in-sample | DEC-109 |
| 6 | **Transaction costs honest** | Costs computed at actual broker spread + slippage per DEC-040 PIT loader | DEC-040, DEC-092/122/280 |
| 7 | **No look-ahead** | PIT regression tests via freezegun pass; DEC-305 PIT guard RAISE not WARN | DEC-040, DEC-305, DEC-417 |
| 8 | **Agent score calibration** | Distribution of Portfolio Manager 5-tier output roughly normal (not all Hold, not all extremes) | DEC-481 |
| 9 | **5-Gate cube validity** | n≥30 + FDR q<0.10 + PSR≥0.95 + t≥3.4 + RR≥2.0 per DEC-426 | DEC-426 + DEC-469/470 |
| 10 | **A/B Sharpe delta CI** | Block-bootstrap CI on Sharpe delta excludes zero per DEC-472 PROPOSED | DEC-472 |
| 11 | **Stage 3 dashboard prerequisites (NEW Pass 53 §32)** | Public site live + Dashboard 4 operational + Telegram bot + email alerts active | §32, DEC-187, DEC-202 |

Detailed gate logic in DETAILED_PROJECT_PLAN.md Part 13 §13.1.

---

## 11. Trading Rules Reference

**All trading rules, thresholds, criteria, and benchmarks are canonical in TRADING_RULES_AND_INFORMATION.md.**

This document does not duplicate them. Sections in TRADING_RULES_AND_INFORMATION.md:
- Stage transition criteria (Section 1)
- Phase acceptance criteria (Section 2)
- Strategy validity gates (Section 3)
- Strategy decay detection (Section 4)
- Position sizing (Section 5)
- Per-ticker risk controls (Section 6)
- AgentGateConfig (Section 7)
- Exit methodology (Section 8)
- Circuit breakers (Section 9)
- Regime rules (Sections 10-11)
- PIT correctness (Section 12)
- Cache rules (Section 13)
- Cost modeling (Sections 14-15)
- Statistical methodology (Sections 16-18)
- Event handling (Sections 19-20)
- Phase 1B-α dimensional cube (Sections 21-22)
- REVISIT_AFTER_BACKTEST aggregation (Section 23)

---

## 12. Risk Management Philosophy

Detail: TRADING_RULES_AND_INFORMATION.md Sections 5-6, 9.

Summary: medium-high risk profile with concentration accepted; position sizing via DEC-021 3-tier (5%/3%/1.5%) augmented by Kelly + vol-targeted parallel computation (DEC-086/087); portfolio vol target 15% (DEC-088); circuit breakers Levels 1-5 with recovery rules (DEC-127/128/314/315); per-ticker controls (5-day stop-out cooldown DEC-018, -10% rolling 30d max-loss cap DEC-135).

---

## 13. PIT Correctness — Non-Negotiable

Detail: TRADING_RULES_AND_INFORMATION.md Section 12.

Summary: All historical data lookups must return values as-of-date, not current. PIT loader (DEC-040), cache stores raw OHLCV (DEC-298), freezegun PIT regression tests (DEC-050), PIT guard RAISE not WARNING (DEC-305). yfinance .info CURRENT-not-as-of cluster resolved via Polygon reference (DEC-443/447).

---

# PART E — CURRENT STATE & DECISIONS

## 14. Current Status (Pass 52 Closure)

### 14.1 Pass 52 achievements summary

- PENDING resolution: 60% → 0% (~280 decisions resolved)
- Phase 2 retroactive sprint-tracking audit (~226 classified)
- BUG_REGISTER.md created (148 bugs cross-referenced)
- Bulk sweep (80 PENDING converted)
- CHECKLIST #58 operational at 4 levels
- Engineering effort reality check: ~30-40d → ~310-385d (8-10x growth)

### 14.2 Pass 53 status

**Pre-Sprint-1 setup phase.** Per PASS_53_PRIORITIES.md, owner is reviewing pre-execution risk plan before authorizing Sprint 1 kickoff. Polygon subscription owner action pending.

### 14.3 Audit state

- Total decisions: 462
- PENDING: 0
- RESOLVED-DECIDED: 358
- Audit at 100% terminal state

### 14.4 Detail

PASS_53_PRIORITIES.md is canonical for Pass 53 priorities + retrospective.

---

## 15. Audit Index

**Canonical:** AUDIT.md (decision detail) + AUDIT_INDEX.md (status table).

| Status | Count |
|---|---|
| Total | 462 |
| PENDING | 0 |
| RESOLVED-DECIDED | 358 |
| DEFERRED_TO_STAGE_3 | 32 |
| DEFERRED_TO_STAGE_4 | 19 |
| SUPERSEDED (any) | 29 |
| BLOCKED_ON_X | 10 |
| REJECTED | 2 |
| Other (PARTIAL/OBSOLETE) | 12 |

Detail: AUDIT_INDEX.md.

---

## 16. Engineering Register

**Canonical:** ENGINEERING_REGISTER.md.

~226 ENG decisions tracked across 9 sprints with sprint slots, test signals, and effort estimates. Per CHECKLIST #58, every RESOLVED-DECIDED engineering decision has a sprint slot.

---

## 17. Documentation Register

**Canonical:** DOCUMENTATION_REGISTER.md.

~80-100 DOC decisions tracked across 5 buckets:
- Bucket A: Foundational/Integrated (no execution work)
- Bucket B: Methodology/Library choices
- Bucket C: Cross-Reference/Absorbed
- Bucket D: Stage 3+/4+ Operational deferred
- Bucket E: To Be Classified

---

## 18. Bug Register

**Canonical:** BUG_REGISTER.md.

148 canonical bugs cataloged with cross-references to resolving decisions.

**3 CRITICAL OPEN bugs:**
- **BUG-095** (no Portfolio class) → Sprint 3 resolves
- **BUG-218** (yfinance .info CURRENT) → DEC-443 absorbed Sprint 4
- **BUG-111** (no break-and-retest variants) → Sprint 8 with architectural choice flagged

---

## 19. Implementation Readiness

**Canonical:** IMPLEMENTATION_READINESS_DASHBOARD.md.

- Total Stage 2 effort: ~310-385 engineering days realistic
- Critical path: ~125-160 engineering days minimum
- 8-10x scope expansion vs original Pass 52 starting estimate

---

## 20. Limitations / Caveats / Assumptions

**Canonical:** LIMITATIONS_CAVEATS_ASSUMPTIONS.md.

CAV-001 through CAV-071+ documenting all known limitations, caveats, and assumptions. Per CHECKLIST #49 + #50, caveats are tracked separately from decisions and inline-referenced in PROJECT_PLAN as relevant.

---

# PART F — TESTING & EXECUTION

## 21. Testing Strategy

### 21.1 Test pyramid

- **Unit tests:** function/class isolation (~70% of test suite)
- **Integration tests:** module-to-module interactions (~20% of test suite)
- **Characterization / golden-master tests:** capture known-good behaviors per DEC-438 (~5% of test suite)
- **Property-based tests:** invariant verification via `hypothesis` per DEC-437 (~3% of test suite)
- **Differential tests:** cross-implementation validation per DEC-439 (~2% of test suite, highest-stakes only)

### 21.2 Coverage target

**90% coverage** target per DEC-098 (owner override Pass 52 turn 58 from 70%).

### 21.3 Multi-layer defense

5-Layer Catch-Mechanism Defense per DEC-417/436/437/438/439:
- Layer 1: Pre-flight checklist (existing)
- Layer 2: CI/CD regression pipeline (DEC-436)
- Layer 3: Property-based testing via hypothesis (DEC-437)
- Layer 4: Characterization / golden-master tests (DEC-438)
- Layer 5: Differential testing (DEC-439)
- Plus: DEC-417 audit gate

### 21.4 PIT regression tests

All PIT-loader functions tested via `freezegun` (DEC-050). `loader.fetch(as_of=D)` must return rows with date ≤ D only; rows with date > D must RAISE (not warn) per DEC-305.

### 21.5 Test infrastructure

ENGINEERING_REGISTER.md Sprint 6 captures full test infrastructure scope.

---

## 22. Sprint Execution Plan

### 22.1 Per-sprint workflow

- **PR-based development:** branch protection on main; all changes via PR
- **CI gates:** ruff + black + isort + mypy + pytest must pass before merge (per DEC-173)
- **Cold-start CI test:** weekly + on dependency changes (per DEC-138)
- **Test-first discipline:** failing test linked to decision before code change
- **Test pyramid coverage:** each sprint's acceptance criteria enumerates which pyramid layers (per §21.1) it touches and asserts test signals at the matching layer
- **Owner PR review:** per-PR review before merge (not retroactively post-push)

### 22.2 Acceptance criteria template per sprint

Each sprint defines explicit acceptance criteria in ENGINEERING_REGISTER.md. Examples:
- Sprint 1: "S&P 500 OHLCV fully cached + first PIT loader test passing"
- Sprint 3: "Portfolio class instantiable; positions tracked across multi-strategy entries"
- Sprint 7: "5-gate validity filter operational; A/B framework produces per-cell verdicts"

### 22.3 RESOLVED-DECIDED → RESOLVED-IMPLEMENTED transition

Per CHECKLIST #58: every RESOLVED-DECIDED with implementation work must have:
1. Sprint slot in ENGINEERING_REGISTER (or DOCUMENTATION_REGISTER bucket if doc-only)
2. Test signals defined
3. Effort estimate

When implementation completes:
1. Tests pass for all defined test signals
2. Code review approved
3. Status flips RESOLVED-DECIDED → RESOLVED-IMPLEMENTED in AUDIT_INDEX
4. AUDIT.md narrative documents implementation
5. ENGINEERING_REGISTER updated (move from "in-progress" to "implemented")

### 22.4 Implementation cadence

Per Pass 53 pre-Sprint-1 setup: cadence TBD per owner direction (per-PR review vs per-sprint-milestone review).

---

## 23. CHECKLIST Process

**Canonical:** CHECKLIST.md.

58 process discipline items operational. Most-recent additions (Pass 52):
- #58: Sprint-tracker assignment as RESOLVED-DECIDED commit requirement
- #57: Use-case mapping discipline (this-system vs generic-template)
- #56: Focus-phase scope filter (forward-looking deferral discipline)
- #55: Phase scope check (architectural framing gate)
- #54: Test-run audit gate (CRITICAL process gate)
- #53: Grounded-recommendation format mandatory
- #52: Ambiguous owner directives default to lower-impact action
- #51: Do not infer approval beyond owner's explicit statement

Detail: CHECKLIST.md.

---

## 24. Learnings — Key Lessons Driving This Plan (RESTORED Pass 53 inline per Q2)

**Canonical:** LEARNINGS.md (1-145 entries).

*(Q2 owner directive Pass 53 2026-05-05: restore inline. Pass 52 turn 128 REFRESH had compressed this to a pointer.)*

### 24.1 Process / discipline learnings (CHECKLIST source)

| # | Lesson | Codified in CHECKLIST |
|---|---|---|
| L86 | Cost-controlled API runs (small batch → owner approval → scale) | #13/#22/#23/#29 |
| L88 | Wikipedia is unreliable as a runtime data source — static CSV pattern is correct | Universe management |
| L89 | New spinoff >$5B → add to T2 immediately, don't wait for S&P 500 inclusion (SNDK 9-month lag) | DEC-103 |
| L94 | Process discipline standing rule | #30/#31/#32 (Pass 44) |
| L99 | Row inflation correction 3.5× — per-strategy minimum 143 independent positions | Stage 2 → 3 gate #2 |
| L103 | Read library source before recommending | Fork-first architecture HARD RULE |
| L106-L108 | (multiple process learnings) | #30/#31/#32 |
| L133-L137 | (Pass 52 learnings) | #54-#58 |
| L143 | Don't-rewrite-history (immutable historical AUDIT.md narratives) | #67 exclusions |
| L144 | Roster category-boundary integrity | #65 |
| L145 | Silent-gap pattern (working endpoint validates wrong assumption) | #69 (test pyramid mandate; DEC-503) |

### 24.2 Architectural learnings driving design

- **PIT correctness is non-negotiable** (L143 + DEC-040 + DEC-305) — every fetcher accepts `as_of`, RAISES on look-ahead, freezegun-tested
- **Survivorship bias prevention** (DEC-303 PIT membership + DEC-477/483/494 B++ schema) — universe loaders filter by `(added_date <= as_of) AND (removed_date IS NULL OR removed_date > as_of)`
- **NO LIVE API HARD CUT** Stage 2 (DEC-497 + D4 owner directive 2026-05-05) — backtest reads from `data_prefetch/` only; yfinance removed runtime
- **Smart-money signals are CONTINUOUS, not binary** (BUG-144) — agents consume confidence-weighted scores, not just gates
- **Agent overlay must DEMONSTRATE edge** (DEC-131 ≥0.2 Sharpe delta) — A/B tested every Phase, retired if degrades
- **Strategy decay re-validation quarterly** (DEC-214) — strategy passing Stage 2 may fail in live; re-run periodically
- **Test pyramid before every code push** (DEC-503 Pass 53; CHECKLIST #69) — silent-gap discovery (BUG-271/272/273) showed limited testing missed 3-of-4 endpoint failures

### 24.3 Operational learnings

- **Email > Telegram for trade approvals** (DEC-194 evolved Pass 43) — but Telegram for real-time alerts (free + richer than SMS)
- **Owner approves all decisions explicitly** (CLAUDE.md HARD RULE) — no autonomous strategy/threshold changes
- **Cost-controlled API discipline** (CHECKLIST #13/#22/#23/#29) — small test → manual review → owner approval → scale; past mistakes (L86/L95) cost $150
- **Per-turn doc sync** (CHECKLIST #67/#67.b Pass 53) — every turn with meaningful changes commits docs same turn; decoupled from pending operations

### 24.4 Recent Pass 53 learnings

- **L143 / L144 / L145** codified Pass 53 (silent-gap discovery, roster integrity, test pyramid mandate)
- **CHECKLIST #67/#68/#69** added Pass 53 (per-turn doc sync, smoke→demo→full protocol, test pyramid before push)
- **DEC-497 to DEC-504** Pass 53 architectural decisions (Sprint 0A scope, Polygon ticker events, Quiver expansion, test pyramid HARD RULE, T3-over-T1 precedence)

Full detail: LEARNINGS.md L1-L145.

---

# PART G — REFERENCE

## 25. Tech Stack Summary

| Layer | Tool / Library | Notes |
|---|---|---|
| Language | Python 3.11+ | |
| Data persistence | Parquet via pyarrow | Cache layer per DEC-260+ |
| Workflow orchestration | GitHub Actions | + sync_from_claude.yml owner-controlled (DEC-220) |
| Dev environment | VS Code on Windows laptop + Claude Code (Pass 53 update — was: GitHub Codespace "vigilant system") | Owner uses Windows laptop |
| Backend (Stage 4+) | TBD cloud platform per DEC-272 | |
| Web hosting | Vercel for public + private dashboard per DEC-197 | Mobile-first per DEC-190 |
| Backtest framework | Custom `backtest/` module | engine.py being audited per DEC-217 |
| Strategy framework | `screener.py` + STRATEGY_REGISTER.md | |
| Statistical | scipy + numpy + custom metrics.py | + hypothesis (DEC-437) + freezegun (DEC-050) |
| Broker integration (Stage 4+) | IBKR via ib_async per DEC-049/054 | |
| Agent framework | TradingAgents per DEC-051 staged | + GPT-5.4-mini per DEC-058 |
| Type checking | mypy strict per DEC-170 | + ruff/black/isort per DEC-173 |
| Testing | pytest + hypothesis + freezegun + pytest-benchmark | |
| Documentation | sphinx with Google-style docstrings per DEC-171 | |
| Logging | python-json-logger per DEC-230 | |
| Configuration | pydantic typed config per DEC-229 | |

---

## 26. Cost Summary

### 26.1 One-time costs

- Polygon Stocks Starter activation: $0 (subscription only)
- Quiver paid tier activation: $0 (subscription only)
- Tools/libraries: $0 (open-source)

### 26.2 Monthly recurring (Stage 2 → Stage 5)

| Item | Cost (CAD/mo approx) | Stage |
|---|---|---|
| Polygon Stocks Starter | $30 USD ≈ $40 CAD | Stage 2+ (DEC-441) |
| Quiver Quantitative paid | TBD per DEC-450 | Stage 2+ |
| LLM agent costs (Stage 2 backtest) | ~$120 one-time + ~$30-60/mo | Stage 2 (DEC-211) |
| LLM agent costs (Stage 4+ live) | TBD per DEC-058 | Stage 4+ |
| IBKR market data subs | ~$10-30 USD ≈ $15-40 CAD | Stage 4+ (DEC-271) |
| Cloud hosting (Stage 4+) | TBD per DEC-272 | Stage 4+ |
| **Full Stage 5 stack** | **~$263 CAD/mo** | per project memory |

### 26.3 Per-stage cost progression

- Stage 1: $0 (Alpha Vantage free + GitHub Actions free)
- Stage 2: ~$70-100 CAD/mo (Polygon + Quiver)
- Stage 3: ~$100-150 CAD/mo (+ paper trading data)
- Stage 4: ~$200-263 CAD/mo (+ market data + cloud)
- Stage 5: ~$263 CAD/mo full stack

---

## 27. Workflow — Making Changes

### 27.1 GitHub repository

`jeetmehta1991/stock-picks-app`

### 27.2 Branches

- `main` — production canonical state; protected
- `claude-updates` — Claude session changes; merged to main via owner-controlled `sync_from_claude.yml` workflow per DEC-220

### 27.3 sync_from_claude.yml governance (per DEC-220 inspection turn 95)

- Workflow trigger: `workflow_dispatch` only (manual, owner-triggered from GitHub Actions UI)
- Mandatory `description` input parameter (audit trail)
- Validates imports post-merge
- **NOT scheduled, NOT auto-run**
- Owner Option C verification gate intact at architectural level

### 27.4 Owner approval cycle (Option C verification gate)

Per CHECKLIST #51:
- Claude proposes recommendations
- Owner explicitly approves before status flips or commits
- Claude does not infer approval beyond owner's explicit statement

### 27.5 PAT pattern (per CLAUDE.md)

Option 3 cached `~/.git-credentials` (chmod 600) for git operations from sandbox.

---

## 28. Glossary

| Term | Definition |
|---|---|
| **PIT** | Point-in-Time — historical data lookup as-of a specific date, not current value |
| **Look-ahead bias** | Using future information in backtest decisions; PIT prevents this |
| **PSR** | Probabilistic Sharpe Ratio — Bailey-Lopez de Prado deflated Sharpe |
| **Sharpe** | Risk-adjusted return: `mean(returns) / std(returns) × sqrt(252)` for daily |
| **DD** | Drawdown — peak-to-trough decline in equity curve |
| **OOS** | Out-of-sample — validation data not used in training |
| **A/B** | Comparative testing of agent overlay variants |
| **TIER** | Confidence tier (HIGH/MEDIUM/LOW per DEC-021 3-tier) |
| **Walk-forward** | Rolling train/test methodology per DEC-505 (1y warmup + 4 OOS × 1y; supersedes DEC-109 5y/1y/6-fold) |
| **Cube** | Phase 1B-α dimensional cube per DEC-422 (17+ dimensions) |
| **5-gate** | DEC-426 validity filter (n/p/PSR/t/R:R) |
| **Crisis flag** | Replaces hard regime direction blocks; identifies extreme conditions |
| **REVISIT_AFTER_BACKTEST** | Tag indicating threshold/value needs empirical tuning post-Phase-1B-α |

---

## 29. Document Map

This project's documentation lives across multiple specialized files. The map:

### Entry point
- **PROJECT_PLAN.md** (this file) — canonical project entry point

### Canonical references
- **TRADING_RULES_AND_INFORMATION.md** — all rules/thresholds/criteria (HIGHLY DETAILED)
- **AUDIT.md** + **AUDIT_INDEX.md** — decision detail + status table
- **ENGINEERING_REGISTER.md** — sprint roadmap + ENG decisions
- **DOCUMENTATION_REGISTER.md** — DOC decisions (5 buckets)
- **BUG_REGISTER.md** — 148 bugs + decision linkages
- **STRATEGY_REGISTER.md** — strategy taxonomy + per-strategy detail
- **API_AUDIT.md** — DEC-410 17-API utilization audit
- **IMPLEMENTATION_READINESS_DASHBOARD.md** — sprint readiness gates
- **LIMITATIONS_CAVEATS_ASSUMPTIONS.md** — CAV-001 through CAV-071+
- **CHECKLIST.md** — 58 process discipline items
- **LEARNINGS.md** — L1-L137 process learnings

### Pass-specific
- **PASS_53_PRIORITIES.md** — Pass 52 retrospective + Pass 53 priorities
- **HANDOFF_PASS52.md** — Pass 52 session handoff (historical)
- **THEME_X53_SEQUENCING.md** — Pass 52 theme sequencing (historical)

### Historical
- **PROJECT_PLAN_v1_outdated.md** — pre-Pass-53 PROJECT_PLAN (April 2026)
- **PROJECT_PLAN_ARCHIVE.md** — pre-April-2026 reference
- **EXPLANATION.md** — early project explanation (historical)
- **AUDIT_TRIAGE.md** — Pass 52 audit triage (historical)

### Operational
- **CLAUDE.md** — Claude session context guide
- **README.md** — repository entry
- **PROGRESS.md** — high-level progress tracker

---

## 30. Pass Retrospectives Reference

### 30.1 PASS_53_PRIORITIES.md

Comprehensive Pass 52 retrospective + Pass 53 priorities. Created Pass 52 turn 124 closure.

### 30.2 Historical archive

PROJECT_PLAN_ARCHIVE.md contains the pre-April-2026 PROJECT_PLAN reference, useful for understanding the project's evolution.

---

*This document is canonical for project overview. All section detail lives in specialized registers per the Document Map (Section 29). Per CHECKLIST #58 + Single Source of Truth principle.*

---

## 31. Pass 53 Sprint 0A status snapshot (2026-05-05)

### 31.1 Active sprint

**Sprint 0A** (Pass 53 owner-renamed from Sprint 1 per DEC-497) — Multi-API Prefetch + Universe Build + Stage 2 NO-LIVE-API Refactor.

### 31.2 Sub-phase status (Sprint 0A.0 - 0A.10)

| Sub-phase | Deliverable | Status |
|---|---|---|
| 0A.0 | Universe build (5 tiers + sector normalization + Master dedup) | ✅ IMPLEMENTED 2026-05-05 |
| 0A.1 | Polygon EXTENSION (news/financials/events/NBBO daily-close) | ⏸ Pending owner gate |
| 0A.2 | FRED + ALFRED 52-series (curating ~15-20) | ⏸ Pending |
| 0A.3 | AAII + CNN F&G (composite + 7 sub-components) | ⏸ Pending |
| 0A.4 | CFTC COT prefetch | ⏸ Pending |
| 0A.5 | Quiver Trader 8 endpoint groups + silent-gap fix (BUG-271/272/273) | ⏸ Pending — silent-gap fix first |
| 0A.6 | SEC EDGAR structured (Form 4, 8-K, 10-Q/K via edgartools) | ⏸ Pending |
| 0A.7 | Apewisdom + pytrends (free social sentiment supplement; DEC-502) | ⏸ Pending |
| 0A.8 | NO-LIVE-API HARD CUT refactor (`fetcher/macro/sentiment/smart_money.py`) | ⏸ Pending |
| 0A.9 | Polygon ticker events integration (DEC-500) | ⏸ Pending |
| 0A.10 | Smoke + demo + full tests per API + full test pyramid (DEC-503) | ⏸ Pending |

### 31.3 New DECs Pass 53 (497-503)

- **DEC-497** — Sprint 0A scope expansion + NO-LIVE-API HARD CUT (RESOLVED-DECIDED)
- **DEC-498** — Per-turn doc sync rule (CHECKLIST #67 + #67.b codified)
- **DEC-499** — 18-classifier sector taxonomy (GICS-11 + 7 ETF asset classes)
- **DEC-500** — Polygon ticker events integration as agent context (RESOLVED-DECIDED)
- **DEC-501** — superseded by DEC-506 Pass 53 owner correction 2026-05-05 (Polygon Options Stage 2 IN-SCOPE; subscription buy-on-demand at sprint entry)
- **DEC-506** — Polygon Options + Ortex confirmed Stage 2 in-scope; subscriptions deferred to point-of-need; corrects DEC-501 + DEC-468 timing
- **DEC-507** — Agent toolkit wiring matrix HARD RULE (CHECKLIST #70 + L146)
- **DEC-502** — Quiver Trader-tier 8 endpoint groups + Apewisdom + pytrends supplement
- **DEC-503** — Comprehensive test pyramid before every code push (HARD RULE; CHECKLIST #69)
- **DEC-504** — T3-over-T1 multi-tier precedence resolver (RESOLVED-IMPLEMENTED 2026-05-05; FIRST DEC-503 test pyramid application)

### 31.4 Critical bugs surfaced Pass 53 (BUG-271/272/273)

`backtest/data/smart_money.py` has 3 silent gaps — Quiver endpoints returning HTTP 404 against Trader-tier subscription, silently zeroing insider + institutional + analyst-revisions inputs of the smart_money composite. Logged to BUG_REGISTER.md. Fix scheduled next turn with full DEC-503 test pyramid.

### 31.5 Universe build (Sprint 0A.0) deliverables

5-tier B++ schema universe:
- T1a S&P 500 historical: 614 rows (Jan 2020 → May 2026)
- T1c NASDAQ-100: 161 rows (101 active + 60 historical)
- T1 ETFs: 27 (DEC-118)
- T2 Spinoffs/IPOs: 347 (297 SCREENER + 50 graduated-name backfill per BUG-274 Option B owner-approved 2026-05-05; 0 blank sectors post BUG-275 fix)
- T3 Momentum: 1923 period rows (1924 - 1 NULL Symbol post BUG-276 fix); 1220 unique tickers
- Master Dedup: 1,937 unique tickers with `resolved_tier` column per DEC-504 (T3=993, T1a=501, T2=282, T1c=134, T1ETF=27)
- DEC-504 T3-over-T1 precedence rule RESOLVED-IMPLEMENTED Pass 53; scope (a)-(e) all approved
- T3 Momentum Top-100: 1924 rows (after leveraged-ETF blocklist fix)
- Master Universe Deduplicated: 1,775 unique tickers with full dimensional metadata

### 31.6 Reading guide

Full Sprint 0A detail in **DETAILED_PROJECT_PLAN.md Part 2.6 (Sprint-Sequenced Index) + Part 3 §3.16-§3.17 (expanded scope)**. Cross-document navigation in DETAILED_PROJECT_PLAN.md Part 18.

---

## 32. Website Architecture & Phase-Specific Analytics Dashboards

*(RESTORED Pass 53 owner directive 2026-05-05 — eliminated by Pass 52 turn 128 PROJECT_PLAN REFRESH (commit `4d514c2a`); preserved in PROJECT_PLAN_ARCHIVE.md §21. Owner: "the website creation has been completely removed? Why? That is still a key deliverable in stage 3. Can not be removed!" Restoring Section 21 from Pass 44 (commit `bb6335d6`) with Pass 53 minor updates.)*

### 32.1 Two-Property Web Architecture (per DECISION-187)

The system has two distinct web properties, not one:

**Property 1 — Public Recommendations Site** (mobile-first, no auth, end-of-day refresh)
- Today's trade recommendations with full 10-point rationale
- Yesterday's recommendation results (success/failure with mark-to-market on still-open positions)
- Track record header: rolling 30/90/all-time recommendation win rate, avg gain, avg loss, profit factor
- URL: TBD public domain

**Property 2 — Private Analytics Dashboards** (multiple dashboards, no auth during paper trading per DEC-196, revisit before live)
- Phase-specific dashboards (one per phase — see §32.5)
- All deeply linked, accessed via internal URLs
- URL: TBD internal subdomain

### 32.2 Trade Flow: Algo → Execution → Notification → Display

```
[Backtest / Paper / Live Algo Engine]
              │
              ▼
   Generates trade decisions
              │
              ▼
[Autonomous Execution] ←─── (no human approval gate per DEC-033 changed)
              │
              ▼
   Trades placed (paper or live broker via IBKR)
              │
              ▼
   Fills + slippage recorded
              │
        ┌─────┴─────┐
        ▼           ▼
[Notification    [Database]
   Layer]            │
   - Telegram    [Public Site] ← end-of-day refresh
   - Email       [Private Dashboards] ← real-time/on-demand
   - Push           │
        │        Owner monitors via mobile
   Owner alerts:
   stops, breakers,
   halts, P&L breach,
   divergence, data
   feed failures
        │
   Owner may manually
   replicate trades in
   Wealthsimple (out of system)
```

### 32.3 Public Recommendations Site — Spec (per DEC-187 to 198)

**Layout: Mobile-first card-based, two main sections.**

**Section A — Today's / Tomorrow's Recommendations**
- Card per recommendation
- Card collapsed view (default on mobile): ticker, direction, tier, entry, stop, target, hold range, strategy name, top 3 signals
- Card expanded view (tap to expand): full 10-point rationale per DEC-189

**Section B — Yesterday's Results**
- Card per recommendation made yesterday
- Status badges: closed-positive ✅ / closed-negative ❌ / still-open with mark-to-market 🔄
- Closed cards show: entry, exit, hold days, exit reason, P&L
- Open cards show: entry, current, unrealized P&L, days held so far
- Original rationale expandable

**Header — Track Record**
- Rolling win rate (30d / 90d / all)
- Avg gain on winners / avg loss on losers
- Profit factor
- Total recommendations

**10-Point Trade Rationale (DEC-189) per recommendation:**
1. **Trigger** — exact signal values (RSI=28, not "oversold")
2. **Strategy** — name + one-line description
3. **Setup** — chart pattern / context
4. **Smart money context** — insider/congressional/13F flags with names
5. **Macro/regime fit** — why this trade fits current regime
6. **Agent reasoning** — Bull case, Bear case, who won
7. **Risk assessment** — gap risk, earnings proximity, sector weakness
8. **Similar historical trades** — "won 14 of 22 in similar setups"
9. **Position sizing rationale** — why this tier
10. **Exit plan** — stop, target, time stop, abort conditions

**Publish timing (DEC-191):**
- Pre-market 7-8am ET: tomorrow's recommendations published
- Post-close 4pm ET: today's results updated, status badges set

**DEC-192:** Site shows actual paper trades with real slippage, not theoretical recommendations. Track record reflects what actually happened including fills.

### 32.4 Push Notification Layer (DEC-194, DEC-195)

**Bot:** Telegram (free, richer formatting than SMS, separate from phone SMS).

**6 alert events:**
1. Stop-out fired on any open position
2. Circuit breaker triggered (any of 5 levels per CIRCUIT_BREAKERS config)
3. Position halted intraday
4. Daily P&L breach (-2% warning, -5% critical)
5. Backtest-vs-paper divergence > threshold (paper Sharpe drops 0.5 below backtest, per DEC-114)
6. Data feed failure (any vendor)

**NOT alerting on:** earnings beats/misses (too noisy across many open positions).

**Email summary (twice daily):**
- Pre-market 7am ET: tomorrow's planned trades + overnight news + regime classification
- Post-close 4:30pm ET: today's executed trades + day P&L + open positions + tomorrow's preview

### 32.5 Phase-Specific Analytics Dashboards (6 dashboards)

Each phase produces different output shapes and answers different questions. One dashboard each:

**Dashboard 1 — Phase 1B-α Backtest Analysis** (DEC-199; Pass 52 turn 79 RESOLVED-DECIDED with 5-section spec)

Sections: Cube Explorer (2D heatmap / 3D scatter / per-cell drill-down per DEC-430) | Per-strategy verdict cards (PASS/FAIL_RR/FAIL_CONFIDENCE/FAIL_DRAWDOWN/INSUFFICIENT_SAMPLE per DEC-426 + 5-gate validity n>=30/p<0.05/PSR>=0.95/t>=3.4/RR>=2.0) | Regime breakdown (verdict-by-regime per DEC-209) | A/B comparison (rules vs full-agents net Sharpe per DEC-205-216 + DEC-210) | Live decision lookup (state-vector input → recommended strategy/exit/confidence per DEC-429). Filter sliders all dimensions; drill-downs to per-cell trades with DEC-189 10-point rationale.

**Dashboard 2 — Phase 0.D ICT/SMC Signal Audit** (DEC-200; Pass 52 turn 79 RESOLVED-DECIDED with 5-section spec)

Sections: Signal visualization (FVG/BOS/CHoCH/order blocks overlay on candlestick per DEC-259/261 PIT N+1 lag) | Signal frequency stats (per-ticker per-month counts; flag anomalies) | Synthetic test cases (smartmoneyconcepts test suite verification) | PIT validation (confirm N+1 lag rule applied) | Library version manifest (pinned smartmoneyconcepts version + fork commit hash per DEC-045).

**Dashboard 3 — Stage 2 Path B Agent Overlay Analysis** (DEC-201; Pass 52 turn 79 RESOLVED-DECIDED with 6-section spec)

Sections: A/B summary (4-arm net Sharpe table per DEC-205-210) | Agent disagreement events (trades tagged AGENT_DISAGREEMENT_BULL_BEAR per DEC-212 + outcome) | Per-agent ablation (DEC-211 narrow scope — marginal Sharpe per agent on top-20% strategies × 5K sample, post-Phase-1B-α) | Both-rationales comparison (DEC-213 — rules_rationale + agent_rationale side-by-side) | Cost accounting (Net Sharpe = Gross Lift − Annualized Cost per DEC-210; alert if approaching DEC-131 0.2 net threshold) | Quarterly re-validation status (DEC-214; ALERT_AGENT_DECAY).

**Dashboard 4 — Stage 3 Paper Trading Analytics** (DEC-202 PROMOTED FROM DEFERRED Pass 53 owner directive 2026-05-05 — full spec below)

Sections (PROMOTED Pass 53 to ACTIVE; spec drafted now for Stage 3 entry preparation):
- **§4.1 Status bar** — last update timestamp / paper-account balance / open positions count / today's P&L / today's order count
- **§4.2 Equity curves** — $5K vs $50K vs SPY (per DEC-029-A/B); zoom 30d/90d/YTD/all
- **§4.3 Drawdown chart** — peak-to-trough with circuit-breaker overlay (CIRCUIT_BREAKERS L1-L5 markers)
- **§4.4 Per-strategy P&L attribution** — P&L breakdown across strategies (sortable by net contribution)
- **§4.5 Per-regime breakdown** — calm/neutral/volatile/crisis per DEC-106 + win rate / Sharpe / count
- **§4.6 Trade journal** — full trade list with 10-point rationale per DEC-189; searchable + filterable; expandable cards per trade
- **§4.7 Backtest-vs-paper divergence tracker** — paper Sharpe vs backtest projection; flag when >0.5σ deviation per DEC-114
- **§4.8 KPIs panel** — Sharpe / win rate / profit factor / max DD / vs-SPY (rolling 30d / 90d / all-time per DEC-155)
- **§4.9 Circuit breaker status** — current state of L1-L5 breakers + last-fired log
- **§4.10 System health panel** — data feed freshness (Polygon / Quiver / FRED / etc); broker connection (IBKR paper); kill switch armed/fired
- **§4.11 Push alert log** — 6 alert events history (stops / breakers / halts / P&L breach / divergence / data feed) with timestamps + ack status
- Filters: notional ($5K/$50K), date range, strategy, regime, exit method
- Effort: ~5-7d (Streamlit; reuses Dashboard 1 Cube infrastructure for verdict lookup)
- Pass 53 RESOLVED-DECIDED (promoted from DEFERRED_TO_STAGE_3); Stage 3 entry prerequisite

**Dashboard 5 — Stage 4 Live Trading Analytics** (DEC-203 PROMOTED FROM DEFERRED Pass 53 owner directive 2026-05-05 — full spec below)

Sections (PROMOTED Pass 53 to ACTIVE; mirrors Dashboard 4 + real-money concerns):
- **All Dashboard 4 sections** plus:
- **§5.1 Real cash position + USD/CAD exposure** (DEC-134) — CAD home base; USD position with FX rate; running CAD-equivalent P&L
- **§5.2 Tax event log** (DEC-035, DEC-270) — realized gains/losses per Canadian CRA classification; T5008 tracking; unrealized year-end estimate
- **§5.3 Capital protection metrics** — running drawdown vs limits / vol vs target / factor exposure caps / sector concentration
- **§5.4 Reconciliation status** (DEC-097) — broker statement reconciliation; discrepancy log
- **§5.5 Order routing performance** — fill quality vs NBBO; slippage actual vs DEC-092/122/280 estimate; venue breakdown
- **§5.6 Regulatory event flags** (DEC-159) — short-sale rule (Reg SHO); pattern day trader status; circuit breaker triggered events
- **§5.7 Optional: Wealthsimple replication tracking log** — owner manually replicates in Wealthsimple per personal preference; this dashboard tracks that replication
- Filters: account ($10K-50K initial / scaled), date range, strategy, regime
- Effort: ~3-4d incremental over Dashboard 4 (re-uses §4 sections + adds §5.1-§5.7)
- Pass 53 RESOLVED-DECIDED (promoted from DEFERRED_TO_STAGE_4); Stage 4 entry prerequisite

**Dashboard 6 — Cross-Phase Comparison** (DEC-204 PROMOTED FROM DEFERRED Pass 53 owner directive 2026-05-05 — full spec below)

Sections (PROMOTED Pass 53 to ACTIVE; master "is it working" view):
- **§6.1 Sharpe waterfall** — Backtest → Stage 2 (1B-α) → Stage 3 (Paper) → Stage 4 (Live) Sharpe per DEC-129; expected vs actual at each phase boundary
- **§6.2 Win rate degradation waterfall** — backtest → paper → live; expected win-rate decline given DEC-114 threshold
- **§6.3 Slippage attribution per phase** — modeled vs realized slippage per DEC-092/122/280
- **§6.4 Strategy mortality** — which strategies passed/failed each phase (PASS at backtest → PASS at paper → PASS at live); strategy retirement log per DEC-249/214/043
- **§6.5 Cost stack** — commission + slippage + agent fees + infrastructure + data subscription per trade across phases
- **§6.6 Decision ledger** — when each strategy was promoted/demoted; full audit trail per DEC-249
- Filters: strategy subset, date range, phase scope
- Effort: ~3-4d (Streamlit; sources from Dashboard 4 + Dashboard 5 underlying parquet trades)
- Pass 53 RESOLVED-DECIDED (promoted from DEFERRED_TO_STAGE_3); useful from Stage 3 onwards (need ≥30d paper trading for first meaningful waterfall)

### 32.6 Tech Stack & Hosting (Hybrid per owner approval)

**Public site (Property 1):** Next.js + Vercel
- Mobile-first, SSR/SSG-optimized
- Custom domain (TBD)
- Free tier sufficient for paper trading phase
- SEO and polish required for public-facing

**Private dashboards (Property 2, all 6):** Streamlit (per DEC-048 approved)
- Python-native, fast iteration
- One Streamlit app per dashboard, deep-linked
- Hosted via Streamlit Cloud free tier or self-hosted alongside backend
- Single-user friendly; revisit if multi-user need emerges

**Backend / Algo engine:** Local VS Code (Pass 53 update; was Codespace pre-Pass-53) through paper trading per DEC-031, migrate to AWS/GCP/DO before Stage 4 per DEC-093.

**Database:** Existing Parquet cache + new transactional store for trades/results. SQLite during paper (DEC-267); Postgres for live trading.

### 32.7 Build Sequence Aligned to Phase Milestones

Dashboards don't all need to exist on Day 1. Built in lockstep with phase progression:

| Phase | Dashboards Required | Why |
|---|---|---|
| **Sprint 6.5 (Phase 1A baseline)** | Phase 1A Trade Summary Dashboard (NEW Pass 53 §2.5.3 — Streamlit port of legacy 9-tab) | Pre-cube analytical layer |
| **Sprint 7 (Phase 1A-α + 1B + 1B-α)** | Dashboard 1 + Dashboard 2 + Dashboard 3 + Phase 1B Trade Summary Dashboard (NEW) | Cube + ICT/SMC + agent + statistical analysis |
| **Sprint 9 (1B-α run)** | Dashboard 1 + 2 + 3 fully operational | Required to interpret results and pass/fail strategies + Stage 2 verdict gate |
| **Stage 3 entry (paper trading)** | **Public Site (Property 1) + Dashboard 4** | CRITICAL — paper trading goes live + owner monitors via mobile + push alerts |
| **Stage 4 entry (live)** | Public Site live + Dashboard 4 + Dashboard 5 + Dashboard 6 | Real money requires complete monitoring stack |
| **Stage 5** | All 6 dashboards stable + monitoring automation | Owner shifts to monitor role per Part 16 |

### 32.8 Decisions in scope (DEC-187 to DEC-204; preserved AUDIT_INDEX)

| DEC | Title | Status |
|---|---|---|
| 187 | Two-property web architecture | RESOLVED-DECIDED Pass 43 |
| 188 | Public site card-based layout | RESOLVED-DECIDED Pass 43 |
| 189 | Trade rationale 10-point depth standard | RESOLVED-DECIDED Pass 43 |
| 190 | Mobile-first design priority | RESOLVED-DECIDED Pass 43 |
| 191 | Publish timing (pre-market 7-8am ET / post-close 4pm ET) | RESOLVED-DECIDED Pass 43 |
| 192 | Site shows actual paper trades with slippage | RESOLVED-DECIDED Pass 43 |
| 194 | Push alert events (6 events) | RESOLVED-DECIDED Pass 43 |
| 195 | Telegram bot | RESOLVED-DECIDED Pass 43 |
| 196 | No auth on paper-trading dashboard; revisit live | RESOLVED-DECIDED Pass 43 |
| 198 | Paper trading mirrors live algo exactly | RESOLVED-DECIDED Pass 43 |
| 199 | Dashboard 1 (Phase 1B-α backtest analysis) | RESOLVED-DECIDED Pass 52 turn 79 (5-section spec) |
| 200 | Dashboard 2 (Phase 0.D ICT/SMC audit) | RESOLVED-DECIDED Pass 52 turn 79 (5-section spec) |
| 201 | Dashboard 3 (Stage 2 agent analysis) | RESOLVED-DECIDED Pass 52 turn 79 (6-section spec) |
| **202** | **Dashboard 4 (Stage 3 paper trading)** | **PROMOTED Pass 53 from DEFERRED to RESOLVED-DECIDED** (11-section spec §32.5) |
| **203** | **Dashboard 5 (Stage 4 live trading)** | **PROMOTED Pass 53 from DEFERRED to RESOLVED-DECIDED** (mirrors §4 + 7 §5 sections) |
| **204** | **Dashboard 6 (Cross-phase comparison)** | **PROMOTED Pass 53 from DEFERRED to RESOLVED-DECIDED** (6-section waterfall) |

### 32.9 Cost Summary update (Stage 3+ hosting)

**Stage 3 monthly recurring (paper trading, ~3 months):**
- Vercel free tier (Property 1 public site): $0/mo
- Streamlit Cloud free tier (Property 2 dashboards 1-4): $0/mo
- Telegram bot: $0/mo
- Email infrastructure (transactional, e.g., AWS SES or owner-Gmail): ~$0-5/mo
- Stage 3 hosting total: ~$0-5/mo

**Stage 4 monthly recurring (live trading + hosting upgrade):**
- Vercel Pro (custom domain SSL, more bandwidth): ~$20/mo
- Streamlit Cloud Teams (multi-dashboard concurrent + private auth): ~$25/mo (or self-host on cloud at ~$10-30/mo)
- IBKR market data subscriptions: ~$10-30/mo per DEC-271
- Stage 4 hosting + market data: ~$55-85/mo
