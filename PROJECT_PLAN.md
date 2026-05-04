# Stock Picks & Automated Trading System — PROJECT_PLAN

**Version:** Pass 52 closure (refreshed Pass 53 turn 126)
**Status:** Pass 52 audit 100% terminal (462/462 decisions in terminal states); Pass 53 pre-Sprint-1 setup
**Supersedes:** PROJECT_PLAN_v1_outdated.md (April 2026 version, marked outdated post-Pass-52)
**Historical archive:** PROJECT_PLAN_ARCHIVE.md (pre-April-2026 reference)
**Companion:** TRADING_RULES_AND_INFORMATION.md (canonical thresholds + criteria reference)

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
- Personal Windows laptop + VS Code + Claude Code + GitHub Codespace ("vigilant system") for development
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

**Critical path:** Sprint 1 (Phase 0.A) → Sprint 2 (Engine Bug Fixes) → Sprint 3 (Portfolio Class) → Sprint 7 (Statistical Methodology) → Sprint 7-8 (Phase 1B-α Run).

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

**Owner action prerequisite:** Subscribe to Polygon Stocks Starter $30/mo per DEC-441.

**Scope:** Build PIT-correct foundational data infrastructure on Polygon (replacing Alpha Vantage). PIT loader (DEC-040), cache fixes (DEC-307-310), prefetch checklist (DEC-256-261), NYSE calendar (DEC-235), data integrity (DEC-117-118), sentiment refresh (DEC-318-320 + DEC-390-391), multiprocess safety (DEC-328-329).

**Effort:** ~20.5-26.5 engineering days post-Phase-2-cleanup-batch.

**Detail:** ENGINEERING_REGISTER.md → Sprint 1.

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

**Effort:** ~6-8 engineering days (most infrastructure already exists from prior Phase 1A v3 work; this is re-execution on new Sprint 1 cache + DEC-477 universe + Sprint 5 tier definitions).

**Detail:** ENGINEERING_REGISTER.md → Sprint 6.5 (NEW).

### 3.7 Phase 1A-α — Rules-Only Dimensional Cube + Dashboards (Sprint 6.5-7)

**Scope:** Cube populator + 5-Gate verdict + Dashboard 1 (Cube Explorer DEC-199 — rules-only view) + Dashboard 2 (ICT/SMC Audit DEC-200) consuming Phase 1A trade outcomes ONLY (no agent arms). Identifies which strategies pass without agents — establishes the pre-agent baseline verdict per strategy × regime × cell. Mirrors Phase 1B-α structure but applied to single-arm rules-only data.

**Why separate from 1B-α:** Allows owner to evaluate rules-only verdict BEFORE committing $300 budget for full agent-overlay run (Phase 1B-α). If rules-only baseline is weak (Sharpe < 0.7 OOS, no PASS cells), agent overlay justification drops sharply — possibly avoid running 1B at all.

**Effort:** ~10-14 engineering days (cube infrastructure built here; Phase 1B-α reuses).

**Detail:** ENGINEERING_REGISTER.md → Sprint 6.5-7.

### 3.8 Phase 1A-β — Production-Scale Validation Run (Sprint 7 Day 1)

**Scope:** Pre-cube validation run on full universe (~1015 tickers per DEC-483 PROPOSED) without agents. Verifies pipeline integrity at scale BEFORE Phase 1B-α $300 cube run. Catches: cache corruption, PIT regression, multi-process race conditions, memory ceiling issues, walk-forward fold contamination. Inherits Phase 1B-α infrastructure but runs in dry-run mode (no agent API spend).

**Why this phase exists:** Phase 1A-α validates rules-only cube methodology on prior cache scope; Phase 1A-β validates that same methodology survives full universe scale. Catching infrastructure failures here costs ~6-8 hours wall time; catching them mid-Phase-1B-α costs $300 + 37-40h re-run.

**Effort:** ~3-5 engineering days + ~6-8h compute wall time.

**Detail:** ENGINEERING_REGISTER.md → Sprint 7 Day 1.

### 3.9 Phase 1B — Statistical Methodology + A/B (Sprint 7)

**Scope:** Statistical methodology cluster (DEC-080-085 phases + DEC-107-111 + DEC-144/152/153/155) + A/B operational (DEC-207-216 + DEC-242) + Distribution analysis + AgentGateConfig (DEC-459 Option C Hybrid; supersedes DEC-042) + Custom Toolkit + LangGraph state augmentation (DEC-462-468 per TRADINGAGENTS_DATA_AUDIT.md) + Performance metrics canonicalization + Regime classifier improvements.

**Entry criteria:** Phase 1A + 1A-α complete with non-trivial PASS cell count; rules-only baseline Sharpe ≥ 0.7 OOS (else owner reviews whether agent overlay justified).

**Effort:** ~76-85 engineering days (LARGEST sprint).

**Detail:** ENGINEERING_REGISTER.md → Sprint 7.

### 3.10 Phase 1B-α — Combined Dimensional Cube + Dashboards (Sprint 7-8)

**Scope:** DEC-422 Phase 1B-α dimensional cube infrastructure (DEC-425/427/428/429/431) + Dashboard 3 spec (DEC-201 — agent overlay analysis) + parallel backtest execution (DEC-184) + per-trade explainability (DEC-119) + loss attribution (DEC-120) + 17+ categorical breakdown variables (DEC-100/144) + TradingAgents 5-tier→size (DEC-062). Combines Phase 1A baseline + Phase 1B agent-overlay arms (full-with-veto, no-Risk) into single 3-arm cube.

**Note:** Cube infrastructure (populator + 5-Gate verdict logic) was built in Phase 1A-α; Phase 1B-α reuses and extends with agent arms.

**Effort:** ~28-38 engineering days.

**Detail:** ENGINEERING_REGISTER.md → Sprint 7-8.

### 3.11 Phase 1C+ — Strategy Categories Expansion (Sprint 8)

**Scope:** Strategy roster additions: chart pattern strategies (DEC-355-362) + DEC-067 9 exit methods + DEC-075 AEP + DEC-368 Calendar/Seasonal + DEC-370 Index Rebalance + DEC-371 within-category gaps + DEC-352 13F price-level + DEC-174 strategy classification + DEC-175 signal persistence + DEC-076-079 (deferred sub-decisions per Pass 52 #56 scope filter) + multi-TF (DEC-350) + ICT/SMC (DEC-345).

**Effort:** ~37-55 engineering days (parallel-able; not critical path).

**Detail:** ENGINEERING_REGISTER.md → Sprint 8.

---

## 4. Sprint Roadmap Index

**Canonical detail:** ENGINEERING_REGISTER.md (~226 ENG decisions tracked across 9 sprints + sub-sprint blocks).

### 4.1 Sprint dependency graph

```
                Phase 0.A Polygon Foundation (Sprint 1)
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
| Sprint 1 | Phase 0.A Polygon Foundation | ~20.5-26.5d | YES |
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

Sprint 1 → Sprint 3 (BUG-095) → Sprint 7 (statistical methodology) → Sprint 7-8 (Phase 1B-α verdict). Total critical path: **~125-160 engineering days minimum**.

### 4.4 Parallel-able sprints

Sprints 4, 6 partially parallel with Sprints 1-3 once foundations established. Sprint 5 partially parallel after Sprint 1. Sprint 8 fully parallel after Sprint 1.

### 4.5 Detail

ENGINEERING_REGISTER.md is canonical for sprint-by-sprint decisions, test signals, effort breakdowns. IMPLEMENTATION_READINESS_DASHBOARD.md is canonical for sprint readiness gates.

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

- **Source:** S&P 500 historical_membership.csv per DEC-303 (CC0 dataset DEC-052)
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
| Layer 1 | Baseline roster (60 strategy classes per archived PROJECT_PLAN section 6) | 60 |
| Layer 2 | Phase 0.D additions (ICT/SMC + Earnings Momentum + Calendar) | TBD |
| Layer 3 | Pass 52 RESOLVED-DECIDED additions (chart patterns DEC-355-362 + categories DEC-367-371) | 13 |
| Layer 4 | Strategy-additive sub-decisions tracked | TBD |

### 7.2 Total strategy count

Approximately **~109-119 classes** post-Phase-1C (per BUG-111 resolution Sprint 8 + DEC-067 9 exit methods + DEC-355-362 chart patterns + DEC-368/370/371 category additions).

### 7.3 Detail

STRATEGY_REGISTER.md is canonical.

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

- **Polygon Stocks Starter $30/mo** (per DEC-441) — replaces Alpha Vantage
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

## 24. Learnings

**Canonical:** LEARNINGS.md.

L1-L137 process learnings documented across project lifecycle. Key Pass 52 learnings:
- L137 → CHECKLIST #58 (sprint-tracker discipline)
- L136 → CHECKLIST #57 (use-case mapping)
- L135 → CHECKLIST #56 (focus-phase scope filter)
- L134 → CHECKLIST #55 (phase scope check)
- L133 → CHECKLIST #54 (test-run audit gate)

Detail: LEARNINGS.md.

---

# PART G — REFERENCE

## 25. Tech Stack Summary

| Layer | Tool / Library | Notes |
|---|---|---|
| Language | Python 3.11+ | |
| Data persistence | Parquet via pyarrow | Cache layer per DEC-260+ |
| Workflow orchestration | GitHub Actions | + sync_from_claude.yml owner-controlled (DEC-220) |
| Dev environment | GitHub Codespaces ("vigilant system") + VS Code + Claude Code | Owner uses Windows laptop |
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
| **Walk-forward** | Rolling train/test methodology per DEC-109 (5yr/1yr) |
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
