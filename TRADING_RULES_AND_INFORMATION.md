# TRADING_RULES_AND_INFORMATION

**2026-05-15 Day 9+ Batch 178 status:** No rule/threshold changes this session — only inventory + dashboards + Wikipedia revisions prefetch. Canonical thresholds + criteria remain authoritative per §2A signals, §10.8 smart money composite, §13.12 API inventory cross-ref. Live coverage view: https://jeetmehta1991.github.io/stock-picks-app/dashboard_sprint0a/

> **B1029 FRESHNESS NOTE (2026-06-27 doc-sync per owner-mandated comprehensive sweep):** **LIVE COUNTS post-B1010:** **220 registered / 217 active / 12 EXPLORATORY / 3 DISABLED**. **CRITICAL POLICY UPDATE — B982/B983 BH-FDR HARD GATE + PSR companion gate** (Council 85/86 owner-approved 2026-06-21): Decision-1 outcome in MULTIPLE_TESTING_METHODOLOGY.md SUPERSEDED. AUTO-FAIL screens per CLAUDE.md `Passing Criteria` table: #1 cost-sensitivity (sharpe_at_20bps/sharpe_at_0bps ≥ 0.5; B890 DEC-612), #2 Chow break-point (p ≥ 0.05 OR post-break Sharpe ≥ 0.3; B890 DEC-613), #3 ADF stationarity (mean-rev strategies only; B890 DEC-614). R5 LAUNCHED 2026-06-27 B1028 on AWS i-0940a53c75d049381 (Master 1929 ops × 4y 2022-05-05 → 2026-05-05).
>
> **B897 ANCHOR (2026-06-18):** MAY-26-era counts at lines 341, 671, 1213, 1240 ("186 / 185 active" / "199 planned target") preserved for historical lineage; canonical current state in CLAUDE.md banner + CANONICAL_FACTS.md F-002.

**Document role:** Canonical home for all trading rules, thresholds, criteria, benchmarks, and parameters across all 5 stages of the project. ENGINEERING_REGISTER references this document instead of duplicating thresholds inline.

**Created:** Pass 52 turn 128
**Last updated:** Pass 52 turn 131 (surgical update — DEC-042 SUPERSEDED_BY_DEC-459 Option C Hybrid Architecture; Custom Toolkit (DEC-462-468) + LangGraph state augmentation cross-references added per TRADINGAGENTS_DATA_AUDIT.md)
**Companion canonical doc:** PROJECT_PLAN.md (project overview entry point)
**Companion data audit doc:** TRADINGAGENTS_DATA_AUDIT.md (per-agent data input requirements; gap analysis; Custom Toolkit + LangGraph state augmentation specs)
**Single Source of Truth:** This document holds canonical thresholds; if any specialized register or code differs, this document wins.

**Per owner directive #3:** Detail level is exhaustive — all information present, no abbreviation for brevity.

---

## TABLE OF CONTENTS

**Part A — Stage-by-Stage Benchmarks**
1. Stage Transition Criteria
2. Phase-by-Phase Acceptance Criteria
2A. Signal Universe Catalogue (Pass 53 NEW — comprehensive 6-category reference)

**Part B — Strategy-Level Rules**
3. Strategy Validity Gates (5-Gate Filter)
4. Strategy Decay Detection
5. Strategy Tiers and Position Sizing
6. Per-Ticker Risk Controls

**Part C — Agent Gate Rules**
7. AgentGateConfig

**Part D — Exit Methodology**
8. Exit Methods
9. Circuit Breakers

**Part E — Regime Rules**
10. Regime Classification
11. Regime-Conditional Strategy Behavior

**Part F — Data Integrity Rules**
12. PIT (Point-in-Time) Correctness
13. Cache Rules

**Part G — Cost Modeling Rules**
14. Trading Costs
15. Canadian-Resident Specifics

**Part H — Statistical Methodology Rules**
16. Walk-Forward Validation
17. Performance Metrics
18. A/B Testing Framework

**Part I — Event Handling Rules**
19. Event-Calendar Suppression
20. Corporate Actions

**Part J — Phase 1B-α Dimensional Cube**
21. Cube Dimensions
22. Cube Verdict Framework

**Part K — REVISIT_AFTER_BACKTEST Tags (DEDICATED SECTION)**
23. Empirical Tuning Items

---

# PART A — STAGE-BY-STAGE BENCHMARKS

## 1. Stage Transition Criteria

### 1.1 Stage 1 → Stage 2

**Status:** COMPLETE

**Criterion:** Smoke test passing — `fetch_stocks.py` runs daily via GitHub Actions cron at 06:00 UTC and successfully updates `index.html` with US top gainers + TSX quotes.

### 1.2 Stage 2 → Stage 3 (Phase 1B-α Verdict Gate per DEC-269)

**Quantitative gates (ALL required):**

| Metric | Threshold | Source |
|---|---|---|
| **Sharpe ratio (OOS)** | ≥ 1.0 | DEC-269 |
| **Maximum Drawdown** | ≤ 25% | DEC-269 |
| **Win Rate** | Per category (DEC-083 TIERED min trades) | DEC-269 |
| **A/B clear** | full-agents > rules-only by ≥ 0.2 net Sharpe | DEC-131 + DEC-210 |
| **Agent-vs-rules divergence** | < 20% | DEC-269 |

**Methodology gates:**
- Phase 1B-α run complete with 5-gate validity filter applied (DEC-426)
- Per-strategy verdicts available in dimensional cube (DEC-422)
- Live decision lookup table populated (DEC-429)
- Owner reviews Phase 1B-α dashboard outputs and approves Stage 3 transition

**Statistical gates (per DEC-426):**
- Strategies must pass 5-Gate validity filter (see §3) to enter Stage 3 candidate roster
- Insufficient sample strategies marked `INSUFFICIENT_SAMPLE` per DEC-426; not promoted
- R:R hard reject (< 2.0) per DEC-353 must clear

### 1.3 Stage 3 → Stage 4 (Paper Trading Proof per DEC-269)

**Quantitative gates (ALL required):**

| Metric | Threshold | Source |
|---|---|---|
| **Paper trading duration** | ≥ 3 months | DEC-028 |
| **Sharpe (paper)** | ≥ 1.0 | DEC-269 |
| **Max DD (paper)** | ≤ 25% | DEC-269 |
| **Paper-vs-backtest agreement** | Bayesian posterior consistent (DEC-268) | DEC-268 |
| **Paper mirrors live algo** | 100% (paper trades match what live algo would have done) | DEC-198 |

**Operational gates:**
- CPA consultation complete on Canadian tax classification (DEC-270, DEC-035)
- Daily loss limits framework defined (DEC-034)
- Multi-vendor data fallback chain ready (DEC-160)
- Remote kill switch (email-based STOP) operational (DEC-139)
- Norbert's Gambit operational for CAD→USD funding (DEC-255)
- IBKR market data subscriptions active (~$10-30/mo per DEC-271)

### 1.4 Stage 4 → Stage 5 (Full Automation)

**Operational gates:**
- Stage 4 small-scale stable for ≥ 6 months
- Cloud hosting migration complete (AWS/GCP per DEC-272)
- Disaster recovery plan operational (DEC-273)
- All Stage 5 monitoring infrastructure operational
- Owner reviews and approves full automation transition

---

## 2. Phase-by-Phase Acceptance Criteria

### 2.1 Phase 0.A — Polygon Foundation (Sprint 0A)

**Effort target:** ~20.5-26.5 engineering days
**Time-boxed first deliverable:** 1-2 weeks for "S&P 500 OHLCV cache populated + first PIT loader test passing"

**Acceptance criteria:**
- [ ] Polygon Stocks Starter $29/mo subscription active (owner action prerequisite per DEC-441)
- [ ] S&P 500 universe (482 tickers) OHLCV fully cached with raw OHLCV (auto_adjust=False per DEC-298)
- [ ] PointInTimeLoader implementation passes freezegun-based regression tests (DEC-040 + DEC-050)
- [ ] FRED 9+ macro series prefetched (DEC-407+448)
- [ ] AAII sentiment refresh script operational (DEC-319/390)
- [ ] CNN F&G refresh script operational (DEC-320/391) with `(value, last_published_date, age_days)` tuple format
- [ ] Cache eviction policy operational with prefetched-preserved invariant (DEC-225)
- [ ] Cache size monitoring at 80% disk threshold (DEC-227)
- [ ] Cache filelock fail-fast operational (DEC-328)
- [ ] Multi-process safe globals operational (DEC-329)
- [ ] Zero-volume preservation with `is_halted` flag (DEC-310)
- [ ] Ticker collision handling for BRK-B/BRK.B and similar (DEC-309)
- [ ] NYSE calendar via pandas_market_calendars (DEC-235)
- [ ] requirements.txt audit complete with pinned versions (DEC-275)
- [ ] Cross-asset macro prefetch (VIX/DXY/GLD/oil/sector ETFs/TLT/HYG/SHY) per DEC-118

**Test signals (representative):**
- `loader.fetch(ticker='AAPL', as_of='2024-01-15')` returns rows with date ≤ 2024-01-15 only (DEC-040 + DEC-050 freezegun test)
- `cache.evict()` does NOT remove prefetched FRED rows (DEC-225 invariant test)
- Synthetic ticker BRK.B and BRK-B resolve to canonical ticker ID (DEC-309)
- Synthetic zero-volume day on 2020-03-09 preserved with `is_halted=True` flag (DEC-310)

**Dashboards (Pass 53):** Prefetch Coverage Report (Tier 1, ~0.5d Sprint 0A) — auto-emitted post-prefetch HTML showing ticker × source × hit-rate matrix; verifies S&P 500 coverage ≥ 95%. Adaptation of `backtest_report.html` static HTML pattern; no new DEC. See DETAILED_PROJECT_PLAN.md Part 2.5.

### 2.2 Phase 0.B — Portfolio Class (Sprint 3)

**Effort target:** ~8-11 engineering days
**Critical priority:** Resolves BUG-095 CRITICAL OPEN

**Acceptance criteria:**
- [ ] Portfolio class implementation operational; portfolio-level state tracked atomically
- [ ] DEC-070 (portfolio aggregation logic) RESOLVED-IMPLEMENTED
- [ ] DEC-076 (portfolio cash management) RESOLVED-IMPLEMENTED
- [ ] DEC-091 (portfolio P&L computation) RESOLVED-IMPLEMENTED
- [ ] BUG-095 closed
- [ ] Portfolio-level position aggregation passes integration test
- [ ] Portfolio cash invariant (cash + position values = total NAV) passes property-based test (DEC-437)

**Dashboards (Pass 53):** N/A — Portfolio class is consumed by downstream dashboards (DEC-199/200/201, DEC-476 spec); no own dashboard at this phase. Verification via integration test signals. See DETAILED_PROJECT_PLAN.md Part 2.5.

### 2.3 Phase 0.C — Engine Bug Fixes Tier A (Sprint 2)

**Effort target:** ~25.5-30.5 engineering days

**Acceptance criteria:** All 14 critical engine bugs from Tier A resolved with regression tests:
- [ ] DEC-293 close_trade NameError on early close
- [ ] DEC-294 ClosedTrade dataclass dedup
- [ ] DEC-295/296/297 (additional Tier A engine fixes)
- [ ] DEC-305 PIT guard RAISE not WARN
- [ ] DEC-306 cache write atomicity
- [ ] DEC-311 trailing-stop ATR refresh
- [ ] DEC-312 entry signal day timing
- [ ] DEC-314 circuit breakers Levels 3+4 implementation
- [ ] DEC-315 sequential circuit breaker check
- [ ] DEC-327 short-borrow cost duplication fix
- [ ] DEC-338 exit_hybrid_50pct max_days inconsistency
- [ ] DEC-340 (additional Tier A fix)

**Dashboards (Pass 53):** N/A — bug fixes verified via CI test signals + sprint demo. No analytical dashboard at this phase. See DETAILED_PROJECT_PLAN.md Part 2.5.

### 2.4 Phase 0.D — ICT/SMC Fork Integration

**Effort target:** Distributed across Sprints 1, 4, 8

**Acceptance criteria:**
- [ ] smartmoneyconcepts library forked + verified operational (DEC-045)
- [ ] FVG (Fair Value Gap) detection operational
- [ ] BOS (Break of Structure) detection operational
- [ ] CHoCH (Change of Character) detection operational
- [ ] Order blocks detection operational
- [ ] Liquidity sweep detection operational
- [ ] swing_highs_lows primitive shared across strategies (DEC-345)
- [ ] Layer 2 strategies in STRATEGY_REGISTER operational

**Dashboards (Pass 53):** ICT/SMC primitive verification folded into DEC-200 ICT/SMC Audit dashboard at Phase 1A-α (no separate Phase 0.D dashboard per Pass 53 owner direction). See DETAILED_PROJECT_PLAN.md Part 2.5.

### 2.5 Phase 0.E — Catch-Mechanism Defense + Architecture Hygiene (Sprint 6)

**Effort target:** ~62.25-76.75 engineering days (largest sprint absolute)

**Acceptance criteria:**
- [ ] 5-layer catch-mechanism defense operational (DEC-417/436/437/438/439)
- [ ] 90% test coverage achieved (DEC-098)
- [ ] mypy --strict CI gate operational (DEC-170)
- [ ] sphinx documentation auto-generated (DEC-171)
- [ ] All numerical constants extracted to typed config (DEC-172, joint DEC-229 pydantic)
- [ ] ruff + black + isort + mypy pre-commit + CI gates (DEC-173)
- [ ] Cold-start CI workflow operational <30min (DEC-138)
- [ ] Determinism test byte-identical regression operational (DEC-232)
- [ ] python-json-logger structured logging operational (DEC-230)
- [ ] Daily data quality monitoring operational (DEC-233)
- [ ] Per-ticker stop-out cooldown 5d operational (DEC-018)
- [ ] FX exposure tracking metric operational (DEC-134 Stage 2 portion)
- [ ] Per-ticker max-loss cap rolling 30d operational (DEC-135)
- [ ] Portfolio rebalancing threshold-based operational (DEC-136)
- [ ] Memory profiling + 4GB cap operational (DEC-179)
- [ ] LRU memoization on hot signal paths (DEC-183)
- [ ] Random seed in backtest output (DEC-177)
- [ ] Dependency injection sandbox-prototype on 1-2 modules (DEC-251 HARD-REVERSIBILITY)

**Dashboards (Pass 53):** N/A — pyramid coverage tracked in ENGINEERING_REGISTER per Pass 53 (Sprint 6 owns DEC-437/438/439 framework build); test infrastructure IS the verification at this phase. See DETAILED_PROJECT_PLAN.md Part 2.5.

### 2.6 Phase 1A — Rules-Based + Smart Money Baseline (Sprint 6.5)

**Effort target:** ~6-8 engineering days

**Acceptance criteria:**
- [ ] Rules-based screener executes full 199 strategy classes (per F-002 post Pass 53 expansion: Layer 1 110 + Layer 2A 12 + 2B 4 + 2C 5 + Layer 3A 20 + 3B 21 + Layer 6 27) roster on full universe (per DEC-477 Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv + DEC-483 R1000 + NDX expansion)
- [ ] Smart money signals operational (DEC-124 confluence + DEC-332 weights + DEC-450 Quiver paid endpoints)
- [ ] `--no-agents` flag preserved from Phase 1A v3 archive — no TradingAgents.propagate calls
- [ ] Trade outcome log produced for full universe per DEC-189 schema; baseline trades tagged `arm=A_rules_only`
- [ ] Walk-forward folds executed per DEC-482 (expanding window 2y+ train + 6mo OOS × 5 folds within Polygon Stocks Starter 5y window)
- [ ] Liquidity floor applied per DEC-366 + tier-specific ADV thresholds
- [ ] Per-ticker risk gates enforced (DEC-018 cooldown + DEC-135 max-loss cap)
- [ ] Trade outcomes ready as input to Phase 1A-α cube populator

**Dashboards (Pass 53):** **Phase 1A Trade Summary Dashboard** (Tier 2, ~2-3d Sprint 6.5) — Streamlit port of legacy `analysis_dashboard_1a.html` 9-tab structure: per-strategy ranking / regime heatmap / MAE-MFE distribution / equity curve / walk-forward / smart money lift / sector breakdown / skipped trades / circuit breaker log. Adaptation of DEC-199 family (no new DEC). Precedes the cube layer at 1A-α. See DETAILED_PROJECT_PLAN.md Part 2.5.

### 2.7 Phase 1A-α — Rules-Only Dimensional Cube + Dashboards (Sprint 6.5-7)

**Effort target:** ~10-14 engineering days

**Acceptance criteria:**
- [ ] Dimensional cube infrastructure built (cube populator + 5-Gate verdict per DEC-426 + verdict.parquet)
- [ ] Cube populated from Phase 1A trade outcomes ONLY (single arm — rules-only)
- [ ] 5-Gate filter applied per DEC-426 + DEC-469/470 PROPOSED (FDR replacing Bonferroni; hierarchical 3-level)
- [ ] Per-cell verdicts (PASS/FAIL_RR/INSUFFICIENT_SAMPLE/FAIL_STAT) computed from rules-only data
- [ ] Cube Explorer dashboard operational with rules-only filter (DEC-199 — Phase 1A-α view)
- [ ] ICT/SMC Audit dashboard operational on rules-only signals (DEC-200)
- [ ] Live decision lookup table v1 populated from rules-only PASS cells (DEC-429 — pre-agent baseline)
- [ ] Owner reviews 1A-α verdict; rules-only Sharpe ≥ 0.7 OOS gate (else evaluate whether Phase 1B agent overlay is justified)
- [ ] Cube methodology validated at this scale before $300 budget commits in Phase 1B-α

### 2.8 Phase 1A-β — Production-Scale Validation Run (Sprint 7 Day 1)

**Effort target:** ~3-5 engineering days + ~6-8h compute wall time

**Acceptance criteria:**
- [ ] Full universe scale test (~1015 tickers per DEC-483) WITHOUT agents; pipeline integrity validated
- [ ] No PIT regression detected (freezegun verifies)
- [ ] No multi-process race conditions (filelock + cache integrity passes)
- [ ] Memory ceiling not exceeded (cube populate handles full universe scale)
- [ ] Walk-forward folds remain non-contaminated (no train→OOS data leakage)
- [ ] Cache hygiene metrics within thresholds (DEC-243 disk monitor + DEC-244 LRU exemption)
- [ ] Engine output schema validated against DEC-189 reflection log spec
- [ ] Owner reviews 1A-β output before authorizing Phase 1B-α $300 budget commit
- [ ] Catches infrastructure failures at zero API spend; cost of catching here = ~6-8h wall vs $300 + 37-40h re-run if caught mid-1B-α

**Dashboards (Pass 53):** REUSE — DEC-199 + DEC-200 with β-arm filter; no new dashboard at this phase. See DETAILED_PROJECT_PLAN.md Part 2.5.

### 2.9 Phase 1B — Statistical Methodology + A/B (Sprint 7)

**Effort target:** ~76-85 engineering days (largest sprint by total effort)

**Entry criteria:** Phase 1A + 1A-α + 1A-β complete with rules-only Sharpe ≥ 0.7 OOS (else owner reviews whether agent overlay justified at all).

**Acceptance criteria:**
- [ ] Walk-forward validation operational per DEC-482 (expanding window 2y+/6mo OOS × 5 folds within 5y Polygon Stocks Starter window)
- [ ] Deflated Sharpe / PSR computation operational (DEC-110)
- [ ] Stationarity tests operational (ADF + rolling Sharpe + Chow per DEC-111)
- [ ] Distribution analysis operational (DEC-242)
- [ ] A/B testing framework operational with 3 arms per DEC-473 PROPOSED (rules-only / full-with-veto / no-Risk)
- [ ] AgentGateConfig spec implemented per §7 (DEC-481 PROPOSED Option C2; supersedes DEC-459 turn 133)
- [ ] Custom toolkits operational per TRADINGAGENTS_DATA_AUDIT.md Part D (DEC-462-468 Pattern 2)
- [ ] OurAgentState schema + LangGraph injection points operational (DEC-467)
- [ ] LangGraph state augmentation per TRADINGAGENTS_DATA_AUDIT.md Part E (smart_money_signal / regime_context / portfolio_context / event_proximity / sector_context / short_interest_signal / historical_outcomes)
- [ ] Regime methodology operational (DEC-106-108, DEC-149-151)
- [ ] vs-SPY comparison in all reports (DEC-155)
- [ ] Agent overlay decisions logged for candidates that passed Phase 1A baseline gates

**Dashboards (Pass 53):** **Phase 1B Trade Summary Dashboard** (Tier 2, ~2-3d Sprint 7) — Streamlit port of legacy `analysis_dashboard_1b.html` 9-tab structure including agent analysis tab (per-arm Sharpe / DD / win rate / debate transcripts where DEC-189 logging operational). Adaptation of DEC-199 family (no new DEC). Precedes the 1B-α cube view. See DETAILED_PROJECT_PLAN.md Part 2.5.

### 2.10 Phase 1B-α — Combined Dimensional Cube + Dashboards (Sprint 7-8)

**Effort target:** ~28-38 engineering days

**Note:** Cube infrastructure (populator + 5-Gate verdict) was BUILT in Phase 1A-α; Phase 1B-α REUSES infrastructure and EXTENDS with agent arms.

**Acceptance criteria:**
- [ ] Cube populated with all 3 arms (rules-only from Phase 1A + full-with-veto + no-Risk from Phase 1B agent overlay)
- [ ] 17+ cube dimensions operational (revised to 8 core per DEC-471 PROPOSED)
- [ ] 5-gate validity filter operational across all arms (DEC-426)
- [ ] Per-cell per-arm verdicts computed (DEC-426)
- [ ] A/B comparison operational with block-bootstrap CIs per DEC-472 PROPOSED
- [ ] Live decision lookup table v2 updated with full 3-arm verdict (DEC-429)
- [ ] Agent overlay analysis dashboard operational (DEC-201)
- [ ] Stage 2 verdict (Phase 1B-α) per DEC-269: Sharpe ≥ 1.0 OOS, max DD ≤ 25%, win rate ≥ 50%, A/B clear
- [ ] Owner reviews dashboards; Stage 2 → Stage 3 GO/NO-GO decision

### 2.11 Phase 1C+ — Strategy Categories Expansion (Sprint 8)

**Effort target:** ~37-55 engineering days

**Acceptance criteria:**
- [ ] 8 chart pattern strategies operational (DEC-355-362)
- [ ] BUG-111 architectural choice resolved (Option A shared retest primitive recommended)
- [ ] 25 existing breakout strategies retest variants integrated (per BUG-111 resolution)
- [ ] 3 strategies from Layer 3B (DEC-368/370/371) operational
- [ ] Multi-timeframe non-ICT extension (DEC-350)
- [ ] 13F price-level mapping (DEC-352)
- [ ] 9 new exit methods (DEC-067 phases A+B = DEC-432/433) — planned target; live `len(EXIT_STRATEGIES)`=25 Pass 53
- [ ] AEP breaker (DEC-435)
- [ ] Total strategy roster ~109-119 strategies operational (historical planned target; live `len(ALL_STRATEGIES)`=186 registered / 185 active Pass 53 Batch 372)

**Dashboards (Pass 53):** REUSE — DEC-199/200/201 with new strategy roster populating cube; no new dashboard at this phase. See DETAILED_PROJECT_PLAN.md Part 2.5.

---

## 2A. Signal Universe Catalogue (Pass 53 NEW)

This section catalogues ALL signals consumed by strategies, agents, and the screener. Grouped by 6 canonical categories matching the project's signal architecture. Source-of-truth code references provided per category for engineering verification. Total active signal fields in Stage 2 backtest: **~265-275** (validates the "274 signal fields" reference in CLAUDE.md repo structure docstring).

### 2A.1 Category 1 — Technical Indicators (~220 fields)

**Source-of-truth:** [backtest/signals/technical.py:858-892](backtest/signals/technical.py) — `compute_all_signals(df)` aggregates 26 sub-functions.

**Computation:** PIT-correct from cached OHLCV; df sliced to `as_of` date by fetcher before signal computation.

#### 2A.1.1 Pivots & Price Levels
- `compute_pivots(df)` — daily / weekly / monthly pivots (R1/R2/R3 + S1/S2/S3); Camarilla; Woodie's
- `compute_fibonacci(df, lookback=50)` — 23.6 / 38.2 / 50 / 61.8 / 78.6% retracements + extensions
- `compute_vwap(df)` — VWAP + 1σ / 2σ deviation bands
- Previous Day High / Low / Close (from raw OHLCV — no compute fn needed)

#### 2A.1.2 Momentum
- `compute_rsi(df)` — RSI(9 / 14 / 21)
- `compute_stochrsi(df, period=14)` — Stochastic RSI
- `compute_stochastic(df)` — Stochastic Fast/Slow (%K, %D)
- `compute_macd(df)` — MACD(12,26,9) + MACD(8,21,5) variants; histogram + signal line cross
- `compute_ppo(df, fast=12, slow=26, sig=9)` — Percent Price Oscillator
- `compute_williams_r(df, period=14)` — Williams %R
- `compute_roc(df, period=12)` — Rate of Change
- `compute_awesome_oscillator(df)` — Awesome Oscillator (Bill Williams)
- `compute_ultimate_oscillator(df)` — Ultimate Oscillator (Larry Williams)

#### 2A.1.3 Trend
- `compute_ema_sma(df)` — EMA & SMA crossovers (9/21 + 20/50 + 50/200) + EMA distance percentages
- `compute_dema_tema(df, period=20)` — Double + Triple Exponential Moving Average
- `compute_adx(df, period=14)` — ADX strength + DI+/DI-
- `compute_parabolic_sar(df)` — PSAR with acceleration factor
- `compute_ichimoku(df)` — Ichimoku Cloud full 5 lines (Tenkan, Kijun, Senkou A, Senkou B, Chikou)
- `compute_supertrend(df, period=7, mult=3.0)` — Supertrend
- `compute_hull_ma(df, period=20)` — Hull Moving Average

#### 2A.1.4 Volatility / Bands
- `compute_bollinger(df)` — Bollinger Bands variants: (20, 2σ) + (20, 1.5σ) + (10, 2σ); %B + bandwidth
- `compute_keltner(df, period=20, mult=2.0)` — Keltner Channels
- `compute_donchian(df)` — Donchian Channels (period 20 high / low)
- `compute_atr_levels(df, period=14)` — ATR + ATR-stop levels
- `compute_squeeze(df)` — Bollinger inside Keltner squeeze indicator (LazyBear)

#### 2A.1.5 Volume
- `compute_volume(df)` — OBV + A/D Line + Chaikin Money Flow + MFI + Force Index + volume spikes (2× / 3× avg) + VWAP deviation

#### 2A.1.6 Candle Patterns
- `compute_candles(df)` — engulfing, pin bars, hammer, shooting star, doji, morning star, evening star, inside bar, outside bar, harami

### 2A.2 Category 2 — Smart Money Signals

**Source-of-truth:** [backtest/data/smart_money.py:470-529](backtest/data/smart_money.py) — `smart_money_score(ticker, as_of, ...)` composite.

**Per-source raw signals** (full per-source rules: see §10.8):
- **Congressional trades** — Quiver `/historical/congresstrading/{ticker}` (DEC-450 paid). 45-day lookback, age-weighted by transaction date (<30d=1.0× / 30-60d=0.5× / >60d excluded). PIT via STOCK Act 45-day disclosure lag (DEC-324 fix Pass 51).
- **Insider trades** — Quiver `/historical/insidertrading/{ticker}`. 30-day lookback. EXCLUDES non-discretionary: Option / Exercise / 10b5-1 / Gift / Transfer.
- **Institutional / 13F** — Quiver `/historical/institutionalholdings/{ticker}`. Latest available quarter; SEC 45-day filing deadline lag (DEC-325).

**Composite formula** (canonical — see §10.8 for full detail):
- Veto case: `cong=sell AND ins=cluster_sell` → score = -5 (overrides additive math)
- Otherwise additive per source × signal-strength matrix (congressional `+4/+2/-3`, insider `+4/+2/+1/-3`, institutional `+2/+1/-1`)
- Composite labels by score: ≥6 / ≥4 / ≥2 / ≥1 / 0 / <0 / ≤-4
- 90-day decay half-life per DEC-123 (REVISIT_AFTER_BACKTEST §23.1 #15)
- Tunable post-Phase-1B-α per DEC-072

**Adjacent signals (NOT in composite — see §10.9):**
- **News sentiment** — Polygon news (PRIMARY post-Sprint-4 per DEC-440) replacing AV/Finnhub legacy (DEC-454/455). 7-day window. `score ≥ 0.15` → bullish; `≤ -0.15` → bearish.
- **Government contracts** — Quiver prefetch `cache/quiver/gov_contracts/`. 365-day window. `total_amount > 0` → bullish; `recent_win` if last 90 days.
- **Lobbying** — Quiver prefetch `cache/quiver/lobbying/`. 365-day spend. `>$1M` → high_spend; `>$100k` → moderate.
- **Analyst data** — yfinance + Quiver `/historical/analystestimates/{ticker}`. **LIVE-ONLY warning per DEC-299/443** for `Ticker.info` fields (recommendationMean / targetMeanPrice / EPS estimates) — display-only, do NOT affect tier or pass/fail. PIT enforced on `recommendations` history + `upgrades_downgrades` window.

### 2A.3 Category 3 — Options Intelligence (Stage 3+ scope)

**Status:** Stage 3+ live trading scope — NOT consumed in Stage 2 backtest.

**Sources (planned):**
- Put/Call ratio (CBOE free)
- IV rank (for earnings strategy selection — Stage 4+ option strategies per DEC-035 future scope)
- Implied volatility skew

**Stage 2 deferral rationale:** Phase 1A v3 archive validated rules + smart money baseline at 67 instruments without options data. Adding options-driven signals belongs to Stage 3+ when paper trading begins live options strategies.

### 2A.4 Category 4 — Macro Filters

**Source-of-truth:** [backtest/data/macro.py](backtest/data/macro.py) + FRED/ALFRED endpoints (per §13.12 + DEC-301/407+448).

- **Yield curve** — 2yr/10yr Treasury spread (FRED series `DGS2` + `DGS10`); inversion flag
- **VIX** — 20-day realised volatility + classification thresholds (real-time per regime classifier §10); also used in regime hysteresis per DEC-317 (5-day SMA, ≥40 enter / <35 exit)
- **DXY** — US Dollar Index (UUP ETF proxy from OHLCV cache — direct DXY from yfinance/Polygon when available)
- **Economic calendar** — CPI / NFP / FOMC dates per DEC-348 event suppression (BLS `news_release/cpi.htm` + `empsit.htm` + Fed `ne-meetings.json`)
- **Fed rate direction** — Federal Funds rate level + change YoY (FRED `FEDFUNDS`)
- **Cross-asset macro (per DEC-118):** GLD (gold), USO (oil), TLT / HYG / SHY / IEF (bonds), GDX (gold miners), EEM / EFA (international) — sector & cross-asset breadth signals
- **Live breadth (Stage 3+ per DEC-447):** PCT_ABOVE_50EMA, PCT_ABOVE_200EMA, new high / low ratio (computed daily from cached OHLCV in Stage 3 live)

### 2A.5 Category 5 — Sentiment Signals

**Source-of-truth:** [backtest/data/sentiment.py](backtest/data/sentiment.py).

- **AAII Sentiment Survey** — weekly bullish / bearish / neutral percentages. Source: `aaii.com/sentimentsurvey/sent_results` manual CSV download committed to repo. Pub-lag 1 day per DEC-389. Auto-refresh per DEC-390 (GH Actions).
- **CNN Fear & Greed Index** — daily index 0-100 (scrape). Thresholds 20 / 35 / 65 / 80 per DEC-333. Last-published date with `age_days` per DEC-391.
- **COT Report (CFTC)** — weekly Commitments of Traders report (`cftc.gov/MarketReports/CommitmentsofTraders/`). Macro signal per DEC-407+448.

### 2A.6 Category 6 — Company / Fundamental Signals

**Source-of-truth:** [backtest/data/smart_money.py:88-253](backtest/data/smart_money.py) (analyst data) + Polygon Stocks Starter `/v3/reference/financials` (DEC-256 / DEC-257) + SEC EDGAR direct parsing (DEC-484 Sprint 4).

- **Analyst consensus** — recommendation mean (1-5 scale), price target (mean / high / low) + upside %, EPS estimates (next quarter / next year). **LIVE-ONLY warning per DEC-299/443** for yfinance `Ticker.info` — display-only on site card, NOT affecting confidence tier or pass/fail.
- **Analyst rating revisions** — upgrades / downgrades 30-day window (yfinance `upgrades_downgrades` PIT-filtered + Quiver `analystestimates`)
- **Earnings calendar** — report dates from Polygon Stocks Starter (DEC-256); `days_to_earnings` per DEC-013-revised (sizing context, NOT block — Phase 1B)
- **Buybacks** — SEC EDGAR 10-Q / 10-K share-count delta (Sprint 4 DEC-484 SEC EDGAR fundamentals replaces FMP per Pass 53)
- **Dividend changes** — Polygon `/v3/reference/dividends` — yield, growth rate, special dividends
- **Fundamentals (Phase 1B)** — income / balance sheet / cashflow per DEC-484 (SEC EDGAR direct parsing); operating margin, debt/equity, FCF, ROIC, EBITDA margin, etc. Full set TBD per Sprint 4 SEC EDGAR delivery.

### 2A.7 Category 7 — Universe-level signals (NEW Pass 53 owner-approved 2026-05-06; DEC-511)

**Architectural distinction:** Categories 1-6 above are **per-ticker** signals (compute on a single ticker's df, return per-ticker values). Category 7 is **universe-level** signals (compute across the entire universe at a given as-of date, return per-(ticker, date) ranks/scores OR universe-wide aggregates). Different harness, different cache key, different PIT discipline.

**Why a new category:** Layer 6A cross-sectional strategies (8 classes; IDs 172-179 per [STRATEGY_ROSTER_FULL.md](STRATEGY_ROSTER_FULL.md) Layer 6A) + Layer 6E breadth strategies (4 classes; IDs 189-192) are **structurally unimplementable** without a separate harness. Per-ticker `compute_all_signals(df)` cannot answer "where does AAPL rank in the universe today?" — that requires reading the entire universe at as-of T.

#### Category 7 modules

| # | Module | Function signature | Output shape | Cache key | Update cadence |
|---|---|---|---|---|---|
| 7.1 | **Cross-sectional rank** | `compute_cross_sectional_ranks(universe, as_of) → pd.DataFrame` | rows = tickers in PIT-active universe at as_of; cols = `mom_12_1_pct, ret_1m_pct, idio_vol_30d_pct, realized_vol_60d_pct, beta_252d_pct, dollar_volume_20d_pct, quality_composite_pct, factor_score_pct` (all 0-100 percentile ranks within universe) | (as_of_date) | Daily — recomputed at end-of-day for next-day strategies |
| 7.2 | **Breadth indicators** | `compute_breadth_indicators(universe, as_of) → dict` | `{percent_above_50sma, percent_above_200sma, advance_decline_line, ad_ratio_10d, mcclellan_oscillator, mcclellan_summation, zweig_thrust_active, percent_at_20d_highs, percent_at_20d_lows, new_52w_highs_count, new_52w_lows_count}` | (as_of_date) | Daily |
| 7.3 | **Correlation matrix** | `compute_correlation_matrix(universe, lookback=60, as_of) → pd.DataFrame` | N×N pairwise return correlations (lookback-day window ending at as_of); used by DEC-509 strategy correlation cluster + Layer 3B Pairs/Stat Arb (DEC-367) + portfolio-level position-correlation gates | (as_of_date, lookback) | Weekly recompute (correlations are slow-moving) |
| 7.4 | **Factor exposures** | `compute_factor_exposures(universe, as_of, factors=[market, size, value, quality, momentum]) → pd.DataFrame` | rows = tickers; cols = factor loadings via rolling regression on factor returns (FF3 + momentum + quality proxies) | (as_of_date) | Weekly — factor loadings drift slowly |
| 7.5 | **Sector relative strength** | `compute_sector_rs(universe, as_of, lookback=63) → pd.DataFrame` | rows = sectors (per F-005 18-classifier sector taxonomy DEC-499); cols = 1m/3m/6m/12m return vs SPY; ranks across sectors | (as_of_date, lookback) | Daily |

#### PIT discipline (universe-level)

**Universe-as-of-date semantics:** All Category 7 functions read the **as-of-date PIT-active universe** (per F-005 5-bucket DEC-477/483/494/495/103/104 + DEC-504 multi-tier precedence), NOT today's universe. A ticker that was in T1a on 2023-06-30 but delisted by 2026-05-06 must appear in 2023-06-30 cross-sectional ranks; today's universe is irrelevant.

**Lookahead trap (CRITICAL):** Cross-sectional momentum/vol/beta computations need the ticker's price history **up to as_of**, not full history. Implementation must filter ticker price series to `df[df.index <= as_of]` before any rank computation. Otherwise you leak future returns into the rank calculation.

**Cache invalidation:** Universe-level signal cache keys are `(as_of_date, signal_module, [optional lookback])`. Recompute when:
- Underlying ticker prices revise (rare; Polygon-revision audit pending DEC-512)
- Universe membership changes (T1a/T1c monthly refresh per DEC-374)
- Module logic changes (versioned via hash)

#### Output schema standardization

Category 7 outputs use a strict signal contract:
```
{
  "value": float,         # raw value (e.g. -0.05 for -5% momentum)
  "normalized_score": float,  # 0-100 percentile rank within universe
  "regime_tag": str,      # current F-006 regime
  "as_of": date,          # PIT date
  "age_days": int,        # 0 for daily-recomputed
  "source": str,          # module name
  "pit_safe": bool,       # always True for Category 7
}
```

This contract is recommended for Categories 1-6 too (per signal-universe review architectural callout); rolling adoption.

#### Source code paths (Sprint pre-Phase-1A implementation)

- 7.1: `backtest/signals/universe_ranks.py` (NEW)
- 7.2: `backtest/signals/breadth.py` (NEW)
- 7.3: `backtest/engine/correlation_matrix.py` (NEW; consumed by DEC-509 cluster + portfolio gate)
- 7.4: `backtest/signals/factor_exposures.py` (NEW)
- 7.5: `backtest/signals/sector_rs.py` (NEW)

**All NEW for Sprint pre-Phase-1A.** Aggregator: `compute_universe_signals(universe, as_of)` returns merged dict of all 5 modules.

#### Strategies blocked on Category 7

| Strategy | Blocked-by | Layer |
|---|---|---|
| `xs_momentum_12_1` (172) | 7.1 | 6A |
| `xs_short_term_reversal` (173) | 7.1 | 6A |
| `xs_residual_momentum` (174) | 7.1 + 7.4 | 6A |
| `xs_idiosyncratic_vol` (175) | 7.1 + 7.4 | 6A |
| `xs_quality_minus_junk` (176) | 7.1 + 7.4 (+ Sprint 4 fundamentals) | 6A |
| `xs_betting_against_beta` (177) | 7.1 + 7.4 | 6A |
| `xs_dual_momentum_absolute_gate` (178) | 7.1 + 7.5 | 6A |
| `xs_stock_vs_sector_rs` (179) | 7.5 | 6A |
| `breadth_thrust_zweig` (189) | 7.2 | 6E |
| `new_highs_lows_divergence` (190) | 7.2 | 6E |
| `mcclellan_extreme` (191) | 7.2 | 6E |
| `percent_above_50sma_extreme` (192) | 7.2 | 6E |
| `pair_trade_z_score` (108) | 7.3 | 3B |
| `cointegrated_basket_revert` (109) | 7.3 | 3B |
| `sector_pair_momentum` (110) | 7.5 | 3B |
| `etf_basket_arb` (111) | 7.3 | 3B |
| All DEC-509 cluster analysis | 7.3 | methodology gate |

**16 strategies + 1 methodology gate** are gated on Category 7. **Sprint pre-Phase-1A blocker.**

### 2A.8 Signal Universe Totals (post Pass 53 Q1+Q2+Q3)

| Category | Count | Status |
|---|---|---|
| 1. Technical Indicators | ~220 | ✅ ACTIVE Stage 2 (DEC-298 raw OHLCV cache) |
| 2. Smart Money composite + adjacents | ~10 composite/raw labels | ✅ ACTIVE Stage 2 (DEC-450 Quiver paid) |
| 3. Options Intelligence | ~5 planned | ⏸ Stage 3+ scope (DEC-506 deferred subscription) |
| 4. Macro Filters | ~17 (15 + VIX3M + VVIX per DEC-513) | ✅ ACTIVE Stage 2 (DEC-301/407+448); +2 PENDING DEC-513 |
| 5. Sentiment Signals | ~5 | ✅ ACTIVE Stage 2 (DEC-389/390/391/333/407+448) |
| 6. Company / Fundamental Signals | ~15 (full set Sprint 4) | ⏸ PARTIAL Stage 2 — full Sprint 4 DEC-484 |
| **7. Universe-level signals (NEW DEC-511)** | **~25-30 fields across 5 modules** | 🔴 NOT STARTED — Sprint pre-Phase-1A blocker per DEC-511 |
| **+ DEC-513 P1 signal additions** | **+10 fields** (realized vol 3 horizons; beta 3 windows; overnight/intraday split 2; gap classification 5) | 🔴 NOT STARTED — Sprint pre-Phase-1A per DEC-513 |

**Total active in Stage 2 backtest (current state):** ~270-280 signal fields. **Total post Sprint pre-Phase-1A (Category 7 + DEC-513 additions):** ~315-325 signal fields. Stage 3+ adds Category 3 options + completes Category 6 fundamentals → ~340+.

### 2A.8 Cross-References

- **Smart money composite formula (canonical):** §10.8
- **Smart money adjacent signals (canonical):** §10.9
- **API endpoint inventory per source:** §13.12
- **Regime classification using macro signals:** §10
- **Strategy roster consumption of signals:** STRATEGY_REGISTER.md + STRATEGY_ROSTER_FULL.md (Pass 53 expansion to 199 strategies per DEC-509/510)
- **Cube dimensions consuming signals as filters:** §21 (revised per DEC-569 5 primary + 12 drilldown post Pass 53 R7-09)
- **PIT enforcement for all signals:** §12 (DEC-305 RAISE not WARNING)
- **Signal-cleanup decisions:** DEC-453 (OpenBB), DEC-454 (Alpha Vantage), DEC-455 (Finnhub) — Sprint 4 deprecation cleanup; DEC-440 (Polygon news replaces AV+Finnhub); DEC-484 (SEC EDGAR replaces FMP for fundamentals)

### 2A.9 Pass 53 Doc-Reconciliation Cross-Refs (DEC-588 — NEW Day-6 propagation)

Per DEC-588 doc-reconciliation pass (Pass 53 Day 6-7 of 9-day window) executed 2026-05-07: signal-universe-related Pass 53 DECs are codified canonically at §23.x and cross-referenced into this section for top-to-bottom readability.

- **DEC-509 — Layer 1.I 38 short-side strategies for buy-the-dip-sell-the-rip symmetry:** strategy roster expanded to 199 classes (was 134); short-side strategies consume same Category 1 technical signals as long-side counterparts (mirror logic). See STRATEGY_ROSTER_FULL.md Layer 1.I 134-171.
- **DEC-510 — Layer 5 regime-eligibility flag schema overlay:** strategies tag which regime(s) they're eligible to fire in (calm/neutral/volatile/crisis); flag consumes regime classification from §10. See STRATEGY_ROSTER_FULL.md Layer 5.
- **DEC-511 — Category 7 universe-level signals (NEW):** ~25-30 fields across 5 modules (cross_sectional_ranks / breadth_indicators / correlation_matrix / factor_exposures / sector_rs). Sprint pre-Phase-1A blocker. See §2A.7 above for full inventory.
- **DEC-512 — Sentiment-extension fields (DEC-511 sub-decision):** AAII bullish_minus_bearish_30d_zscore + cnn_fg_score + cnn_fg_components + Apewisdom mention deltas + pytrends search-volume zscore. Stage-2 forward-only Apewisdom per DEC-592.
- **DEC-513 — Macro-extension fields (P1):** realized_vol (3 horizons: 5d/21d/63d), beta (3 windows: 60d/120d/250d), overnight/intraday return split (2 fields), gap classification (5 levels: -3σ/-2σ/-1σ/+1σ/+2σ/+3σ). Adds 10 fields to Category 4. See §2A.4.

**Source code paths (engineering verification):**
- Category 1: `backtest/signals/technical.py` (26 fns aggregated by `compute_all_signals()`)
- Category 2: `backtest/data/smart_money.py:470-529` (composite); `:317-374` (congressional); `:381-421` (insider); `:428-463` (institutional); `:549-705` (adjacent: news, gov_contracts, lobbying); `:88-253` (analyst)
- Category 4: `backtest/data/macro.py`
- Category 5: `backtest/data/sentiment.py`
- Category 6: distributed across `smart_money.py:88-253` (analyst) + `fetcher.py` (yfinance fundamentals — DEPRECATED per DEC-443) + Sprint 4 SEC EDGAR build
- Category 7 (NEW DEC-511): `backtest/signals/universe_ranks.py` + `breadth.py` + `factor_exposures.py` + `sector_rs.py` + `backtest/engine/correlation_matrix.py` (all NEW Sprint pre-Phase-1A)

### 2A.9 DEC-512 — PIT-fundamentals filing-date audit (Pre-Phase-1A blocker; Pass 53 Q2 owner-approved 2026-05-06)

**Trigger:** External AI 2026-05-06 review identified that fundamentals data has a TWO-DATE pattern: `filing_date` (when SEC publicly knew the data) vs `period_of_report_date` (the period the data describes). Backtests that join fundamentals on `period_of_report_date` leak future information — at as_of=2024-03-31, you can't use Q1-2024 numbers that will only be filed on 2024-05-15.

**This is the #1 source of fundamentals lookahead bias** in real-world backtests.

#### Audit checklist (pre-Phase-1A blocker)

| # | Audit item | Verification method | Status |
|---|---|---|---|
| 1 | Polygon financials cache uses `filing_date` (not `period_of_report_date`) for backtest as-of cutoff | Inspect `data_prefetch/polygon/financials/{TICKER}.parquet` schema; verify `filing_date` column populated; verify consumer code (Sprint 4 parser) joins on `filing_date <= as_of` | 🔴 PENDING |
| 2 | SEC EDGAR Form 4 cache (Sprint 4 parser) preserves both `transactionDate` AND `filing_date` (4-day SEC window) | Inspect `data_prefetch/sec_edgar/4/{TICKER}.parquet`; consumer joins on `filing_date <= as_of` for material-event-driven strategies; `transactionDate <= as_of` for insider-action-driven strategies | 🔴 PENDING |
| 3 | SEC EDGAR 8-K cache uses `filing_date` for material-event timing | Same pattern | 🔴 PENDING |
| 4 | SEC EDGAR SC 13D/G uses `filing_date` (not the holding date in the form) | Same pattern | 🔴 PENDING |
| 5 | Polygon earnings dates: announced-future earnings dates available historically as-of-prior-date | Test: `query_earnings_dates(ticker='AAPL', as_of='2023-09-15')` returns the 2023-Q4 earnings date IF announced before 2023-09-15. Currently UNKNOWN behavior. | 🔴 PENDING — critical for any pre-earnings strategy |
| 6 | Quiver insiders cache `Date` (transaction) vs Form 4 `filing_date`: confirm Quiver returns transaction dates and consumer adds 1-4 day lag for filing window per DEC-318 N+1 | Inspect Quiver insiders global.parquet; compare to SEC EDGAR Form 4 for same insider/ticker/date | 🔴 PENDING |
| 7 | Universal `signal_age_days` field populated per category | Schema audit; rollout per DEC-513 | 🔴 PENDING |

#### Targeted fix scope (post-audit)

If audit reveals lookahead bias:
- **Code fix in consumer modules** (`smart_money.py`, `macro.py`, `sentiment.py`, `fetcher.py`) — change join keys from `period_of_report_date` to `filing_date`
- **Add `signal_age_days` field universally** — every signal output includes it
- **Add `pit_safe: bool` flag** — strategies can require `pit_safe=True` to gate

**Effort:** ~1 day audit (item 1-7 verification) + ~1-2 days targeted code fixes (depends on findings).

**Phase 1A cannot run** until audit complete + bugs fixed. Per DEC-512.

### 2A.10 DEC-513 — P1 signal universe additions (Pre-Phase-1A; Pass 53 Q3 owner-approved 2026-05-06)

**Trigger:** External AI 2026-05-06 review identified 7 P1 (high-priority) signal additions that unblock Layer 6 strategies. Owner-approved.

#### Additions

| # | Signal | Category | Function | Output | Strategies unblocked |
|---|---|---|---|---|---|
| 1 | **Realized vol** (3 horizons) | §2A.1.4 ext. | `compute_realized_vol(df) → {realized_vol_10d, realized_vol_20d, realized_vol_60d}` (annualized stddev of daily returns) | 3 fields per ticker | 6B realized_vol_regime_short (182); BAB 6.6; idio-vol 6.4; vol-targeting position sizing |
| 2 | **Rolling beta** (3 windows) | §2A.1.4 ext. | `compute_betas(df, benchmarks=[SPY, sector_ETF]) → {beta_60d, beta_120d, beta_252d, sector_beta_60d, sector_beta_120d, sector_beta_252d}` | 6 fields per ticker | 6A.3 residual momentum; 6A.6 BAB; market-neutral DEC-141/142 |
| 3 | **Factor exposures** (FF3 + momentum + quality proxies) | §2A.7.4 (Cat 7) | `compute_factor_exposures(universe, as_of)` — rolling regression on factor returns | 5 fields per (ticker, as_of) | 6A.3 residual momentum; 6A.5 quality-minus-junk; 6A.6 BAB |
| 4 | **Correlation matrix module** | §2A.7.3 (Cat 7) | `compute_correlation_matrix(universe, lookback=60, as_of)` — pairwise return correlations | N×N matrix | DEC-509 cluster analysis; 3B Pairs/Stat Arb (4 strategies); portfolio-level position-correlation gates |
| 5 | **Overnight / intraday split** | §2A.1.7 NEW | `compute_overnight_intraday_split(df) → {overnight_return, intraday_return, overnight_intraday_ratio_20d}` | 3 fields per ticker | 6C overnight_only_long (183); overnight_drift_after_strong_close (186) |
| 6 | **Gap classification** | §2A.1.8 NEW | `compute_gaps(df) → {gap_size_pct, gap_size_bucket [small/medium/large], gap_filled_T1, gap_filled_T3, gap_filled_T5}` | 5 fields per ticker | 6C gap_fade_small (184); gap_and_go_large (185); gap_fill_reversal (187) |
| 7 | **VIX3M + VVIX** in macro feed | §2A.4 ext. | Add VIX3M (3-month VIX) + VVIX (vol of VIX) series to FRED 50 prefetch (or CBOE direct if FRED unavailable); add `vix_term_structure_ratio = VIX/VIX3M` derived signal | 3 fields universe-wide | 6B vix_term_contango_long (180); vix_backwardation_short (181) |
| 8 | **52-week distance continuous** | §2A.1.1 ext. | `compute_extremes(df) → {dist_from_52w_high_pct, dist_from_52w_low_pct, dist_from_20d_high_pct, dist_from_20d_low_pct, dist_from_252d_high_atr, ...}` | ~8 fields per ticker | Multiple Layer 1+6 strategies use 52w-distance implicitly today |
| 9 | **FINRA short interest %** | §2A.6 ext. (free FINRA bi-monthly) | New `data_prefetch/finra/short_interest/` cache + `compute_short_interest(ticker)` | `{short_interest_pct, days_to_cover, si_change_30d}` | 6D `insider_cluster_sell_short` (188); future Ortex squeeze prep |
| 10 | **Universal `signal_age_days` field** | All 7 categories | Schema additive; every signal output gets `age_days: int` populated | 0 new fields; metadata field on existing | Strategy harness can age-weight or reject stale data uniformly |

#### Implementation effort

- Signals 1-2 + 5-6 + 8: **~1-2 days each in `technical.py`** (mechanical compute additions)
- Signals 3-4: **~3-5 days** (depends on Category 7 architecture per DEC-511)
- Signal 7: **~1 day** (CBOE feed extension to macro.py FRED 50-series)
- Signal 9: **~2 days** (FINRA prefetch + parser)
- Signal 10: **~1-2 days** (schema additive across all signal modules)

**Total: ~12-18 days engineering work.** Sprint pre-Phase-1A. Blocks Phase 1A run.

#### Cross-references

- DEC-511 (Category 7 architectural prerequisite for items 3-4)
- DEC-512 (PIT-fundamentals audit — affects signal contract item 10)
- DEC-509 (correlation cluster — depends on item 4)
- DEC-505 (4-fold walk-forward — interacts with all per-ticker signals)
- F-003 + F-009 (signal universe + passing criteria affected)
- Layer 6A (8 strategies) + 6B (3) + 6C (5) + 6D (1) + 6E (4) + 3B Pairs (4) + DEC-509 — all gated on DEC-513 implementation

---

# PART B — STRATEGY-LEVEL RULES

## 3. Strategy Validity Gates (5-Gate Filter per DEC-426)

A strategy is **VALID** if and only if it passes ALL 5 gates per dimensional cube cell:

### 3.1 Gate 1: Sample Size (n ≥ 30 trades per cell)

**Rule:** A strategy must have **at least 30 trades** within a given dimensional cube cell to be evaluated.

**If n < 30:** Cell verdict = `INSUFFICIENT_SAMPLE`; strategy not eligible for promotion to Stage 3 candidate roster from this cell.

**Source:** DEC-426

### 3.2 Gate 2: Statistical Significance (p < 0.05 Bonferroni-corrected) — REVISED per DEC-582 Pass 53 owner-approved 2026-05-06

**Rule:** Strategy returns must be statistically significant at p < 0.05 **after Bonferroni correction** for multiple testing.

**Bonferroni correction factor (DEC-582 RESOLUTION):** Number of strategies tested **only** (per F-002 = 199 RESOLVED-DECIDED + IMPLEMENTED). **NOT strategies × cube cells.** Cube-cell-level multi-testing handled separately via FDR (Benjamini-Hochberg) at the per-strategy level — see DEC-470 PROPOSED for hierarchical correction.

**Resolution of double-counting concern (Pass 53 adversarial review):** Gate 4 (t-stat ≥ 3.4) and Gate 2 (Bonferroni p < 0.05) appeared to double-count multi-testing correction. They do NOT — Gate 2 corrects for cross-strategy multi-testing (planned target 199 strategies; live `len(ALL_STRATEGIES)`=186 Pass 53); Gate 4 corrects for cross-cell-within-strategy multi-testing (planned target ~17 cube dims; live exit_methods=25 per F-004). Each gate addresses a different correction layer; both required for valid inference.

**Why not 199 × cube_cells:** With ~10¹⁴ cells per §21, naive Bonferroni → α/10¹⁴ → t-stat ~7 → no real strategy passes. Hierarchical correction (DEC-470) controls family-wise error within strategy, then Bonferroni across strategies — statistically defensible AND tractable.

**Per DEC-018 (historical):** Original code hardcoded Bonferroni factor to 60 (BUG-18); now must equal `len(ALL_STRATEGIES)` = 199.

**Source:** DEC-080 + DEC-400 + DEC-426 + DEC-582 (Pass 53 BUG fix) + DEC-470 PROPOSED (hierarchical FDR for cube-cells)

### 3.3 Gate 3: Probabilistic Sharpe Ratio (PSR ≥ 0.95)

**Rule:** **Deflated Sharpe Ratio (PSR) ≥ 0.95** required.

**Methodology:** PSR adjusts Sharpe ratio for skewness and kurtosis of the return distribution. Strategies with non-normal distributions (high kurtosis or negative skew) need higher raw Sharpe to clear PSR ≥ 0.95.

**Source:** DEC-110, DEC-426

### 3.4 Gate 4: t-statistic (t ≥ 3.4)

**Rule:** Strategy mean-return t-statistic must be **≥ 3.4** (post-Bonferroni-equivalent threshold).

**Why 3.4 (not 1.96):** Adjusted for multiple testing across cube cells; stricter than naive 95% confidence threshold.

**Source:** DEC-426

### 3.5 Gate 5: Risk-Reward Ratio (R:R ≥ 2.0) — HARD REJECT

**Rule:** Average **Risk-Reward (R:R) ratio ≥ 2.0** required. **HARD REJECT below 2.0.**

**Methodology:** R:R = average win / average loss (in absolute terms). Strategies with R:R < 2.0 are categorically rejected regardless of other gate performance.

**Why hard reject:** Owner directive Pass 52: "2R to be minimum"; strategies relying on win-rate edge without R:R discipline have insufficient margin of safety.

**Cell verdict if R:R < 2.0:** `FAIL_RR` (distinct from PASS or INSUFFICIENT_SAMPLE per DEC-426).

**Source:** DEC-353, DEC-426

### 3.6 Insufficient Sample Handling

**If Gate 1 fails (n < 30):**
- Cell verdict: `INSUFFICIENT_SAMPLE`
- Strategy not promoted from this cell
- Insufficient-sample cells aggregate across cube — if too many, strategy may be promoted from other cells if those pass

**Per DEC-426:** Verdict tri-state is `PASS` / `FAIL_RR` / `INSUFFICIENT_SAMPLE`. (FAIL_RR is enum value distinct from generic FAIL — emphasizes the R:R hard-reject as separate failure mode.)

---

## 4. Strategy Decay Detection

### 4.1 Rolling 6-Month Sharpe Decay Flag (per DEC-249)

**Rule:** Track rolling 6-month Sharpe ratio per strategy. If rolling Sharpe drops by **>50%** from baseline, flag `STRATEGY_DECAY_WARNING`.

**Methodology:**
- Baseline = Sharpe at strategy promotion to live trading
- Rolling 6-month window
- Trigger threshold: `current_6mo_sharpe < baseline_sharpe × 0.5`

**Action on flag:** Trigger DEC-214 quarterly re-validation early (don't wait for next quarter); A/B re-test against rules-only baseline.

**Source:** DEC-249

### 4.2 Edge Decay Assumption (per DEC-250)

**Rule:** Apply **20% Sharpe haircut default** to backtest Sharpe to estimate live performance.

**Rationale:** Crowding effect — strategies that work in backtest get crowded by other traders; live performance is typically 15-25% below backtest. 20% is mid-range default.

**REVISIT_AFTER_BACKTEST:** Tunable empirically post-Phase-1B-α once paper trading data exists.

**Implementation:** Backtest reports both `gross_sharpe` and `decayed_sharpe = gross_sharpe × (1 - decay_pct)`; `decay_pct` configurable per strategy.

**Source:** DEC-250

### 4.3 Quarterly Re-Validation (per DEC-214)

**Rule:** Every strategy re-validated quarterly against rules-only baseline.

**Trigger:** End of each quarter OR strategy decay flag fires (DEC-249).

**Methodology:** Rerun strategy on most recent quarter data; compare metrics vs baseline; if degradation > threshold, demote tier or retire.

**Source:** DEC-214

### 4.4 Strategy Retirement Criteria

**Retire strategy if:**
- 2 consecutive quarterly re-validations show degradation
- Rolling 6-month Sharpe < 0.5 (absolute floor)
- A/B test fails to clear DEC-131 ≥0.2 net Sharpe gate

**Source:** Inferred from DEC-249 + DEC-214 + DEC-131

---

## 5. Strategy Tiers and Position Sizing

### 5.1 3-Tier System (per DEC-021)

| Tier | Position Size | Trigger Condition |
|---|---|---|
| **HIGH** | 5% of portfolio | PM confidence ≥ 0.8 (DEC-459) |
| **MEDIUM** | 3% of portfolio | gate_score 0.65 - 0.8 |
| **LOW** | 1.5% of portfolio | gate_score 0.5 - 0.65 |

**Below 0.5 gate_score:** No entry (REJECT).

**Tier assignment logic:** Per AgentGateConfig (§7) — gate_score determines tier; tier determines size multiplier.

**Source:** DEC-021

### 5.2 Tier Mapping from PM Confidence (per DEC-459 — supersedes DEC-042)

```
if gate_score >= 0.8 and Risk approves and Bull/Bear align:
    tier = HIGH
    position_size = 5% × portfolio_value
elif 0.65 <= gate_score < 0.8 and Risk approves and Bull/Bear align:
    tier = MEDIUM
    position_size = 3% × portfolio_value
elif 0.5 <= gate_score < 0.65 and Risk approves and Bull/Bear align:
    tier = LOW
    position_size = 1.5% × portfolio_value
else:
    REJECT (no position)
```

**REVISIT_AFTER_BACKTEST:** Tier thresholds (0.5/0.65/0.8) tunable empirically.

**Source:** DEC-459 (Pass 52 turn 129; supersedes DEC-042 turn 121 closure)

### 5.3 Fractional Kelly Position Sizing (per DEC-086 — Phased Rollout)

**Rule:** Kelly criterion sizing as parallel arm:

```
kelly_fraction = (win_rate × avg_win - loss_rate × avg_loss) / avg_win
fractional_kelly = 0.25 × kelly_fraction  # quarter-Kelly default
```

**Quarter-Kelly:** Reduces variance vs full Kelly; widely adopted in practitioner literature.

**Phased rollout:**
- Phase A: Tiered baseline (DEC-021 default; current canonical)
- Phase B parallel: Add Fractional Kelly arm
- Phase C parallel: Add Vol-targeted arm
- Verdict post-Phase-1B-α: which sizing methodology has best Sharpe per regime

**Source:** DEC-086

### 5.4 Vol-Targeted Position Sizing (per DEC-087)

**Rule:** Each position scaled to target same per-position vol contribution:

```
position_size_vol_targeted = (target_per_position_vol / asset_vol_252d) × portfolio_value
```

**Default target per-position vol:** 1% per day (configurable).

**Source:** DEC-087

### 5.5 Portfolio Vol Target (per DEC-088)

**Rule:** Total portfolio vol targets **15% annualized**.

**Methodology:**
- Compute portfolio realized vol (rolling 21-day)
- If realized vol > 17% annualized: reduce all positions by `15/realized_vol` ratio
- If realized vol < 13% annualized: increase positions toward target (capped by per-position limits)

**REVISIT_AFTER_BACKTEST:** 15% target tunable empirically.

**Source:** DEC-088

---

## 6. Per-Ticker Risk Controls

### 6.1 Stop-Out Cooldown (per DEC-018)

**Rule:** After a stop-out on a ticker, **5 trading days** before re-entry allowed on that ticker.

**Implementation:**
```
if last_trade_was_stop_out(ticker, lookback=5d):
    skip_entry(ticker)
```

**Rationale:** Prevents whipsaw re-entry after volatile move triggers stop.

**Source:** DEC-018

### 6.2 Per-Ticker Cumulative Max-Loss Cap (per DEC-135 + DEC-584 BUG FIX 2026-05-06)

**Rule:** **Default cap: -10% rolling 30-day per ticker.** If breached, halt that ticker for 30-day cooldown.

**Implementation (CORRECTED per DEC-584 — Pass 53 adversarial review found math bug):**
```
ticker_30d_pnl = cumulative_pnl(ticker, lookback=30d)
ticker_capital_allocated = sum_of_position_sizes_for_ticker_in_30d
if ticker_30d_pnl <= -0.10 × ticker_capital_allocated:
    halt_ticker(ticker, cooldown=30d)
```

**Prior (incorrect) version compared `ticker_30d_pnl` to `-0.10 × initial_portfolio`** — for a 5% position to lose 10% of portfolio meant losing 200% of itself, mathematically impossible. Corrected to compare against ticker-level capital allocated.

**REVISIT_AFTER_BACKTEST:** -10% threshold tunable empirically.

**Source:** DEC-135

### 6.3 Liquidity Filter (per DEC-321 + DEC-366 + DEC-019)

**Tier-specific floors:**

| Tier | Liquidity Floor (ADV) | Source |
|---|---|---|
| **Tier 1** | $10M ADV | DEC-366 |
| **Tier 2** | $5M ADV | DEC-366 |
| **Tier 3** | $5M ADV | DEC-366 |
| **Russell 1000 add** | $3M ADV | DEC-366 |

**Timing (per DEC-019):**
- Apply at entry: standard pre-entry filter
- Re-validate at exit only if liquidity drops materially (>50% from entry-day ADV)

**Fail-closed (per DEC-321):** If liquidity data unavailable, REJECT entry (don't fail-open).

**Source:** DEC-019, DEC-321, DEC-366

### 6.4 Position Concentration

**Per project memory + DEC-090 REJECTED:** No sector caps; concentration accepted.

**Per DEC-133 REJECTED:** No max gross/net exposure caps; concentration accepted.

**Implication:** Per-ticker risk controls (DEC-018/135) are the primary risk barrier; portfolio-level caps are not used.

**REVISIT_DURING_STAGE_3:** If max DD exceeds owner tolerance during paper trading, exposure caps may be revisited (DEC-133 recorded for re-evaluation).

---

# PART C — AGENT GATE RULES

## 7. AgentGateConfig (per DEC-459 Option C Hybrid Architecture — supersedes DEC-042)

**Status:** RESOLVED-DECIDED Pass 52 turn 129 (DEC-042 SUPERSEDED_BY_DEC-459)
**Origin:** Pass 52 turn 128 owner accountability question identified that DEC-042 turn 121 spec referenced agents (Bull/Bear/Risk/ChartAnalyst as parallel voters) that did not match actual TradingAgents architecture (sequential debate-and-synthesize through Portfolio Manager). Specifically: ChartAnalyst is NOT in 11-agent roster; framework produces ONE structured Pydantic decision from Portfolio Manager, not parallel votes.
**Resolution:** DEC-459 Option C Hybrid Architecture — TradingAgents Portfolio Manager native confidence as primary signal + separate Risk veto layer + Research Manager synthesis-level alignment check.

### 7.1 Architecture Overview

**Primary signal:** TradingAgents Portfolio Manager native structured Pydantic decision per `propagate()`:
```python
{
    decision: BUY | HOLD | SELL,
    confidence: float,  # 0.0 to 1.0
    rationale: str,
    structured_fields: {...}
}
```

PM confidence consumed directly as primary gate signal — **NOT re-aggregated** from intermediate agent scores. The TradingAgents framework already performs synthesis through Research Manager (Bull/Bear debate) + Portfolio Manager (Risk debate); re-aggregating these would duplicate work and lose debate richness.

**Source:** DEC-459

### 7.2 Risk Veto Layer

**Rule:** Separate Risk veto evaluated AFTER PM confidence threshold passed.

**Implementation (DEC-459 implementation option 7a recommended):** Extract Risk debate confidence from LangGraph state via state hook. Alternative options 7b (separate Risk Manager call) and 7c (collapse to pure PM-native) deferred to Sprint 7 implementation start.

```
EXTRACT s_risk from LangGraph state (Risk debate confidence aggregate)
IF s_risk < 0.5: REJECT (Risk veto fires regardless of PM confidence)
```

**Continuous-score testing extensively (DEC-459 carrying DEC-042 turn 121 directive #3 forward):**
- A/B framework includes parallel arms:
  - **Arm B (default):** PM confidence + Risk veto layer (binary)
  - **Arm C (no-Risk):** Risk veto disabled; collapses to Option B Pure-PM-native
  - **Continuous-Risk variant:** Risk weighted into PM confidence by extending OurAgentState with `s_risk_weighted` field; tests whether continuous outperforms binary
- Empirical Sharpe delta determines production architecture
- REVISIT_AFTER_BACKTEST tag: continuous-Risk vs binary-veto

**Source:** DEC-459 (carrying DEC-042 turn 121 directive #3 forward)

### 7.3 PM Confidence Threshold

**Rule:** PM confidence ≥ 0.5 required to enter trade pre-Risk-veto.

```
IF PM.decision == HOLD: REJECT
IF PM.confidence < 0.5: REJECT
```

**REVISIT_AFTER_BACKTEST:** 0.5 threshold tunable empirically.

**Source:** DEC-459

### 7.4 Bull-vs-Bear Alignment via Research Manager (Synthesis-Level)

**Rule:** Bull and Bear alignment check applied at debate-level via Research Manager synthesis (NOT raw parallel voting).

**Operationalization:**
```
EXTRACT RM_confidence from LangGraph state (Research Manager output)
EXTRACT RM_direction from Research Manager output

IF RM_confidence < 0.5: REJECT (debate contested; no clear consensus)
IF RM_direction does NOT match PM.decision direction: REJECT (misaligned)
```

**Why synthesis-level not raw votes:** Research Manager already synthesizes Bull/Bear debate through `max_debate_rounds` iterations. Raw Bull/Bear voting (DEC-042 spec) double-counted what RM already produces. Owner directive turn 121 #5 (must align) carried forward but applied at correct architectural layer.

**Source:** DEC-459 (carrying DEC-042 turn 121 directive #5 forward, adapted)

### 7.5 Tier Mapping from PM Confidence (per DEC-459 + DEC-021 3-tier)

| PM confidence | Tier | Position Size |
|---|---|---|
| ≥ 0.8 | HIGH | 5% per DEC-021 |
| 0.65 - 0.8 | MEDIUM | 3% |
| 0.5 - 0.65 | LOW | 1.5% |
| < 0.5 | — | REJECT |

**REVISIT_AFTER_BACKTEST:** All tier threshold cuts tunable.

**Source:** DEC-459 + DEC-021

### 7.6 Override

**Stage 2 (backtest):** Deterministic; no override (reproducibility requirement).

**Stage 3+ (paper / live):** Owner manual override via dashboard.

**Source:** DEC-459 (carrying DEC-042 turn 121 directive #6 forward)

### 7.7 Complete Gate Logic — Sequential Checks

```
INPUT: TradingAgents propagate() output

CHECK 1 — Decision direction
  IF PM.decision == HOLD → REJECT
  IF PM.decision == BUY: long candidate
  IF PM.decision == SELL: short candidate

CHECK 2 — PM confidence threshold (§7.3)
  IF PM.confidence < 0.5 → REJECT
  ELSE proceed

CHECK 3 — Risk veto layer (§7.2)
  EXTRACT s_risk from LangGraph state
  IF s_risk < 0.5 → REJECT (Risk veto)

CHECK 4 — Bull/Bear alignment via Research Manager (§7.4)
  EXTRACT RM_confidence from LangGraph state
  EXTRACT RM_direction from Research Manager output
  IF RM_confidence < 0.5 → REJECT (debate contested)
  IF RM_direction != PM.decision direction → REJECT (misaligned)

CHECK 5 — Tier assignment (§7.5)
  IF PM.confidence ≥ 0.8 → HIGH tier (5% position)
  ELIF 0.65 ≤ PM.confidence < 0.8 → MEDIUM tier (3% position)
  ELIF 0.5 ≤ PM.confidence < 0.65 → LOW tier (1.5% position)

ENTRY APPROVED at assigned tier
```

### 7.8 A/B Framework Arms

The A/B testing framework (DEC-205-216) tests AgentGateConfig variants per DEC-459:

| Arm | Description |
|---|---|
| **A — rules-only** | No agent gate; pure rules-based decisions |
| **B — full-agents-with-veto** | PM confidence + Risk veto + RM alignment (default config) |
| **C — no-Risk** | Risk veto disabled (collapses to Option B Pure-PM-native) |
| **D — no-Bull-Bear-align** | Research Manager alignment check disabled |
| **E — ablation per DEC-211** | Per-phase weight variations on intermediate scores; NARROW SCOPE (~$120 vs $13,800 naive) |

**Source:** DEC-205-216 + DEC-459 + DEC-211

### 7.9 Custom Toolkit + State Augmentation Dependencies

Per TRADINGAGENTS_DATA_AUDIT.md Part D + Part E (Pass 52 turn 130 — DEC-462 through DEC-468):

**Custom toolkits required (Pattern 2 implementation):**
- OurTechnicalToolkit (DEC-462) — Market Analyst tool set
- OurFundamentalsToolkit (DEC-463) — Fundamentals Analyst tool set
- OurNewsToolkit (DEC-464) — News Analyst tool set
- OurTraderToolkit (DEC-465 — NEW class) — Trader tool set; HARD DEPENDENCY on Sprint 3 Portfolio class (BUG-095)
- OurRiskToolkit (DEC-466 — NEW class) — Risk Debaters tool set; HARD DEPENDENCY on Sprint 3 + DEC-189 reflection log

**LangGraph state augmentation required (DEC-467):**
- 7 new state fields injected at Phase 1/2/3 entry points:
  - `smart_money_signal` (DEC-124 confluence)
  - `regime_context` (DEC-106 + crisis flags)
  - `portfolio_context` (Sprint 3 Portfolio class)
  - `event_proximity` (DEC-348 event suppression)
  - `sector_context` (DEC-151 sector regime)
  - `short_interest_signal` (Ortex per DEC-468)
  - `historical_outcomes` (DEC-189 reflection log)

**Without these:** AgentGateConfig operates on degraded data; PM confidence reflects shallow input; Stage 2 A/B verdict invalid (per L139 / CHECKLIST #60 — data dependency verification).

**Source:** DEC-462 through DEC-468 (TRADINGAGENTS_DATA_AUDIT.md Part D + E)

### 7.10 Test Signals

- (a) AgentGateConfig dataclass typed (PM confidence 0.0-1.0 invariant)
- (b) Synthetic `PM(BUY, conf=0.85) + RM(align long, conf=0.7) + Risk(conf=0.6)` → HIGH-tier 5% entry
- (c) Synthetic `PM(BUY, conf=0.85) + Risk(conf=0.4)` → Risk veto → REJECT regardless of PM confidence
- (d) Synthetic `PM(BUY, conf=0.7) + RM(contested, conf=0.4)` → align fail → REJECT
- (e) Synthetic `PM(HOLD)` → REJECT (decision direction)
- (f) DEC-216 A/B orchestrator passes config per arm: full-with-veto = default; no-Risk = veto disabled; no-align = alignment disabled
- (g) Continuous-Risk vs binary-veto A/B arm produces measurable Sharpe delta documenting which is empirically better
- (h) LangGraph state extraction unit tests verify Risk debate confidence + Research Manager confidence reachable from PM decision output

### 7.11 Effort and Sprint

**Effort:** Sprint 7 ~2-3 days (revised from DEC-042 ~1-2d; +1d delta)
- Config dataclass 0.5d
- LangGraph state extraction (Risk debate + Research Manager confidence) 1d
- DEC-216 A/B orchestrator integration 0.5d
- Risk continuous-score test infrastructure 0.5d

**Plus:** Custom toolkit work (DEC-462-468) ~19-22.5d adds to Sprint 7 total.

**Sprint 7 total effort impact:** 77-86d → 96-108.5d (+19-22.5d, ~25-28% increase per TRADINGAGENTS_DATA_AUDIT.md).

**Source:** DEC-459 + DEC-462-468

---

# PART D — EXIT METHODOLOGY

## 8. Exit Methods (per DEC-067)

### 8.1 25 Exit Methods (live `len(EXIT_STRATEGIES)` 2026-05-25; 17 was the pre-Batches-282-285 planned-target enumeration)

**Live 25 methods (2026-05-25 Batch 360):** atr_trail_1x, atr_trail_2x, atr_trail_mae_conditional, atr_trail_vix_conditional, break_even_at_1r, breakeven_plus_trail, chandelier_3x, class_time_stop, earnings_blackout, fixed_4r_2r, hybrid_50pct_target, ma_exit_ema9, mfe_lockin_trail, multi_tier_partial, next_pivot_target, r_multiple_2r, r_multiple_3r, regime_flip, reverse_signal, smc_mitigation_zone, time_stop_10d, time_stop_20d, trailing_10pct, trailing_15pct, trailing_5pct. Canonical SSOT: `backtest/engine/exit_strategies.py::EXIT_STRATEGIES`. Pinned by `test_unit.py::test_batch357_doc_count_drift_exit_methods`.

**9 Baseline (pre-Pass-52):**
1. Fixed % stop-loss
2. Fixed % take-profit
3. Trailing stop (% based)
4. Time-based exit (max days held)
5. ATR-based stop-loss
6. ATR-based trailing stop
7. Hybrid (50% at target, trail rest)
8. Volatility breakout exit
9. Signal-reversal exit

**8 New (Pass 52 — DEC-067 phases A+B = DEC-432/433):**

Phase A (DEC-432) — 3 new indicators:
10. Chandelier exit (3 × ATR off rolling high)
11. Parabolic SAR (PSAR)
12. SuperTrend (ATR-based regime indicator)

Phase B (DEC-433) — 6 new exit methods (1 dropped from initial 9):
13. Volatility-spike-aware ATR exit
14. Multi-timeframe momentum exit
15. Volume-spike exit
16. Volatility regime change exit
17. Time-decay accelerated exit

**Source:** DEC-067, DEC-432, DEC-433

### 8.2 R:R 2:1 Minimum (HARD REJECT per DEC-353)

**Rule:** **Average R:R ≥ 2.0 required.** Strategies (or exit methods producing strategies) with R:R < 2.0 categorically rejected per Gate 5 (§3.5).

**Implication for exits:** Exit method's expected R:R must be ≥ 2.0 across calibration runs.

**Source:** DEC-353

### 8.3 Per-Exit-Method Slippage (per DEC-122)

**Rule:** Different exits have different slippage:

| Exit Type | Slippage Multiplier (vs base) |
|---|---|
| Limit order | 1.0× (base) |
| Stop-market | 1.5× |
| Market-on-close | 2.0× (worst) |
| Trailing stop | 1.5× (similar to stop-market) |

**Source:** DEC-122 + DEC-092 base slippage

### 8.4 Time-of-Day Slippage Multiplier (per DEC-280)

**Rule:** Slippage varies by time of day:

| Time Window | Multiplier |
|---|---|
| Open (9:30-10:00 ET) | 1.5× |
| Mid-day (10:00-15:00 ET) | 1.0× (base) |
| Close (15:00-16:00 ET) | 1.3× |

**Source:** DEC-280

### 8.5 Trailing Stop ATR Refresh (per DEC-311)

**Rule:** ATR for trailing stop recalculated daily (not stale entry-day ATR).

**Source:** DEC-311

### 8.6 Hybrid 50% Exit Max Days (per DEC-338)

**Rule:** `exit_hybrid_50pct` strategy `max_days` parameter must align with documentation; was inconsistent in original code.

**Source:** DEC-338

### 8.7 R-Multiple Exits + Break-Even Moves (DEC-517 — Pass 53 owner-approved 2026-05-06 Q2 P1)

**Trigger:** External AI 2026-05-06 review — DEC-067 has %-based and ATR-based exits but no R-multiple. With R:R ≥ 2.0 hard floor (DEC-353), exits SHOULD be parameterized in R (multiples of initial risk). A 5% target on a 1% stop = 5R; a 5% target on a 4% stop = 1.25R — same %, completely different trades.

**New exit methods (added to DEC-067 17 → 19 + scale-out variants per DEC-523):**

| # | Method | Logic |
|---|---|---|
| 18 | `exit_r_multiple_2r` | Take profit at 2× initial risk (entry_price ± 2 × stop_distance) |
| 19 | `exit_r_multiple_3r` | Take profit at 3× initial risk |
| 20 | `exit_break_even_at_1r` | Move stop to entry (break-even) at +1R unrealized; continue trail per primary exit |

**Combined behaviors:**
- BE+0.5R cushion: at +2R, move stop to +0.5R (locks 0.5R minimum gain)
- BE+1R cushion: at +3R, move stop to +1R (locks 1R minimum gain)

**Source:** DEC-517

### 8.8 Earnings-Blackout Exit (DEC-518 — Pass 53 owner-approved 2026-05-06 Q2 P1)

**Trigger:** DEC-013 (earnings_tolerant) sizes positions around earnings but doesn't hard-exit non-earnings strategies. Almost all systematic swing systems have "flat by T-1 before earnings" rule.

**Rule:** For strategies NOT tagged `earnings_tolerant: True` (DEC-013 list — PEAD, earnings-momentum), force exit at close of T-1 (1 trading day before scheduled earnings) regardless of P&L.

**Earnings calendar source:** Polygon Stocks Starter earnings dates (per DEC-256; subject to DEC-512 PIT-fundamentals filing-date audit).

**Affected strategies:** All Layer 1-6 strategies EXCEPT explicitly earnings-tolerant: ~190 of 199 strategy classes affected (planned target; live 186 Pass 53).

**Override:** Layer 2B Earnings Momentum strategies (4 classes — `pre_earnings_iv_crush_front_run`, `guidance_raise_momentum`, `surprise_magnitude_pead`, `earnings_cluster_sector_drift`) are EARNINGS-NATIVE; blackout does not apply.

**Source:** DEC-518

### 8.9 Strategy-to-Exit Mapping (DEC-519 — Pass 53 owner-approved 2026-05-06 Q2 P1)

**Decision:** Every position has **multiple exits competing** (first-to-trigger wins), NOT one exit per strategy.

**Default exit stack per position:**
1. **Stop** (one of: `atr_trail_1x` per CLAUDE.md primary, `fixed_pct`, `chandelier`, etc. — strategy-specific)
2. **Profit target** (one of: `exit_r_multiple_2r` default, or strategy-specific %)
3. **Time stop** (per-strategy-class default per DEC-521)
4. **Signal-reversal** (per DEC-520 precise definition)
5. **Earnings-blackout** (per DEC-518) for non-earnings-tolerant strategies
6. **Regime-flip** (per DEC-516) when regime exits the strategy's `regime_eligible` set
7. **Sector/market overlay** (per DEC-525, P2 backlog)

**First-to-trigger wins:** the position closes at the first exit's fill price; subsequent triggers ignored.

**Reporting:** Per-(strategy × exit_method) cell in DEC-422 dimensional cube records which exit method fired for each trade.

**Source:** DEC-519

### 8.10 Signal-Reversal Exit Precise Definition (DEC-520 — Pass 53 owner-approved 2026-05-06 Q2 P1)

**Trigger:** DEC-067 method 9 lists "Signal-reversal exit" but doesn't define which signal reverses. With 199 strategies (planned target; live 186 Pass 53), this needs precise per-strategy meaning.

**Rule:** Exit when the entry-condition logic is no longer true (NOT when an opposite-direction signal fires).

**Examples:**
- `rsi_oversold` (entry: RSI(14) < 30 long): exit when RSI(14) > 50 (re-cross neutral midline; NOT when RSI > 70)
- `macd_crossover` (entry: MACD bullish cross): exit when MACD bearish cross (entry-condition inverted)
- `golden_cross_50_200` (entry: 50 SMA crosses above 200 SMA): exit when 50 SMA crosses below 200 SMA
- `pivot_s1_bounce` (entry: bounce at S1 support): exit when price closes below S1 (support broken)

**Implementation:** each strategy class registers an `exit_when()` predicate alongside its `entry_when()` predicate. Symmetric pair.

**Source:** DEC-520

### 8.11 Per-Strategy-Class Time Stops (DEC-521 — Pass 53 owner-approved 2026-05-06 Q2 P1)

**Trigger:** External AI flagged that one global `max_days` parameter is wrong for a multi-strategy system.

**Rule:** Default time stops per Layer 1 category (configurable per-strategy override):

| Strategy class | Default `max_days` | Rationale |
|---|---|---|
| Pivot (1.A) | 5-10 days | Intraday-anchored; mean-reverts within days |
| Momentum (1.B) | 20-30 days | Trending continuation horizon |
| Trend (1.C) | 40-60 days | Major trend continuation |
| Mean Reversion (1.D) | 5-10 days | Quick reversion expected; chop kills |
| Breakout (1.E) | 20-30 days | Breakout follow-through |
| Candle (1.F) | 5-10 days | Reversal patterns play out quickly |
| Confluence (1.G) | strictest of constituents | inherited |
| Layer 2A ICT/SMC | 10-20 days | Pattern-driven horizon |
| Layer 2B Earnings | 30-60 days | PEAD horizon |
| Layer 2C Calendar | per-strategy (Sell-in-May 6 months; Santa rally 1 week; etc.) | calendar-specific |
| Layer 3A Chart patterns | 30-60 days | Pattern measured-move horizon |
| Layer 3B Pairs | 20-40 days | Convergence horizon |
| Layer 3B Cross-Asset | 40-60 days | Cross-asset trend horizon |
| Layer 6A Cross-sectional | 21-30 days (rebalance cadence) | Monthly rebalance default |
| Layer 6B Vol regime | 5-15 days | Vol regimes shift quickly |
| Layer 6C Overnight/gap | 1-3 days | T+1 close-to-open or gap-fill window |
| Layer 6D Insider | 30-90 days | Insider signal persistence |
| Layer 6E Breadth | 20-40 days | Breadth thrust → bull-leg horizon |
| Layer 6F Drift | 30-60 days | Post-event drift window |
| Layer 6G Microstructure | 5-15 days | Setup-driven short horizon |

**Source:** DEC-521

### 8.12 Trailing-Stop ATR Floor (DEC-522 — Pass 53 owner-approved 2026-05-06 Q3 P2 backlog)

**Trigger:** External AI flagged "ATR collapse trap" — when realized vol crashes mid-trade, daily-refreshed ATR shrinks, trailing stop tightens aggressively, position stops out at noise.

**Rule:** Daily ATR refresh (per DEC-311) uses `max(current_atr, 0.7 × entry_day_atr)` — floor prevents trail-tightening on vol collapse.

**Source:** DEC-522 — P2 backlog spec; implementation in `backtest/engine/exit_strategies.py` ~0.25 day.

### 8.13 Scale-Out Curves Beyond 50/50 (DEC-523 — Pass 53 owner-approved 2026-05-06 Q3 P2 backlog)

**Trigger:** DEC-067 hybrid is single 50/50 split. Real scale-out is a curve.

**Rule (proposed, P2 backlog):** Add general scale-out framework. Default profile: 1/3 at 1R + 1/3 at 2R + 1/3 trail (chandelier/ATR).

**Source:** DEC-523 — P2 backlog; ~1 day implementation.

### 8.14 News / 8-K-Driven Exit (DEC-524 — Pass 53 owner-approved 2026-05-06 Q3 P2 backlog)

**Trigger:** Polygon news + SEC EDGAR 8-K already cached (Pass 53 Batch 3 + Batch 11). Exit on adverse idiosyncratic news (downgrade, guidance cut, SEC filing concern).

**Rule (proposed, P2 backlog):** Exit position on:
- Polygon news article tagged negative-sentiment (per `insights` field) within 1 trading day
- SEC EDGAR 8-K filed with material event (Item 2.02, 4.01, 4.02, etc.) within 1 trading day

**Source:** DEC-524 — P2 backlog; ~1-2 days post-Sprint 4 SEC EDGAR parser.

### 8.15 Sector/Market Exit Overlay (DEC-525 — Pass 53 owner-approved 2026-05-06 Q3 P2 backlog)

**Trigger:** Top-down kill switch separate from 5-level circuit breakers (which are P&L-triggered, not market-state-triggered).

**Rule (proposed, P2 backlog):** Exit longs if SPY breaks 50-SMA on closing basis; exit shorts if SPY breaks above 50-SMA. Sector ETF analog: exit sector positions if sector ETF (XLF/XLK/etc.) breaks 50-SMA against position direction.

**Source:** DEC-525 — P2 backlog; ~0.5 day.

### 8.16 Pattern-Target Exit for Layer 3A (DEC-526 — Pass 53 owner-approved 2026-05-06 Q3 P2 backlog)

**Trigger:** Layer 3A chart-pattern strategies (20 classes — DEC-355-362) lack textbook measured-move targets.

**Rule (proposed, P2 backlog):**
- **Measured-move target:** height of pattern projected from breakout point (e.g., for double-top, the depth of the trough below the second peak; for cup & handle, the cup depth)
- **Fibonacci extensions:** 1.272 / 1.618 / 2.618 of the swing as alternate target levels

**Per-pattern target table:** to be specified during DEC-526 implementation.

**Source:** DEC-526 — P2 backlog; ~1 day.

### 8.17 MAE/MFE Empirical Exit Calibration (DEC-527 — Pass 53 owner-approved 2026-05-06 Q3 P2 backlog)

**Trigger:** DEC-422 cube already captures MAE (Maximum Adverse Excursion) + MFE (Maximum Favorable Excursion) per cell. Best-practice: train exits on the in-sample MAE/MFE distributions per strategy.

**Rule (proposed, P2 backlog; Phase 1B-α work):** For each strategy class, after Phase 1A-α in-sample run:
- Compute MFE distribution; set TP at the 90th-percentile MFE achieved by winners
- Compute MAE distribution; set stop at the 5th-percentile MAE that didn't recover to a profit

**Source:** DEC-527 — P2 backlog; Phase 1B-α work ~2-3 days.

---

### 8.18 Backlog (P3-P4) — DEC-528 through DEC-538

| DEC | Topic | Effort |
|---|---|---|
| DEC-528 | Volatility-target position exit (vol_realized > 1.5× vol_entry over 5 bars) | ~0.5d |
| DEC-529 | Correlation-spike portfolio breaker (Level 8; depends on DEC-511 §7.3 correlation matrix) | ~1d |
| DEC-530 | Profit-protect ratchet stops (step-function: BE at 1R / lock 1R at 2R / lock 2R at 3R) | ~0.5d |
| DEC-531 | DD-from-peak per-trade exit (give back ≤30% of unrealized profit) | ~0.5d |
| DEC-532 | Time-stop + profit conditional (T+10 if not in profit; T+20 if in profit) | ~0.5d |
| DEC-533 | Adverse-selection slippage on stops (vol-conditional multiplier on stop-market fills in fast moves) | ~0.5d |
| DEC-534 | Long/short asymmetry: borrow recall exit + dividend liability + forced-buy-in modeling | ~1d |
| DEC-535 | Exit-as-function-of-signal-quality (high-confluence fires get wider stops + longer time horizons) | ~1d |
| DEC-536 | Underspecification fixes (vol-breakout direction / volume-spike direction filter / multi-TF / time-decay / chandelier 22d / SuperTrend dual-use) — single doc cleanup | ~0.5d |
| DEC-537 | Hybrid 50% scale-out fraction tunable in Phase 1B-α (calibration via DEC-072 sweep methodology) | post-Phase-1B-α |
| DEC-538 | Liquidity-conditional slippage refinement (per-name ADV vs tier-based DEC-095) | post-Phase-1B-α |

All DEC-528-538 are RESOLVED-DECIDED at backlog level (Pass 53 owner-approved 2026-05-06 Q3); implementation deferred to post-Phase-1B-α or as Sprint priorities allow.

---

## 9. Circuit Breakers

### 9.1 Levels 1-6 (per DEC-314 + DEC-315 + DEC-515 Pass 53 + DEC-586 priority fix)

| Level | Trigger | Action |
|---|---|---|
| **Level 1** | Single-day -1% portfolio | Soft pause: halve position sizes 1 day |
| **Level 2** | Single-day -2% portfolio | Soft pause: halve position sizes 2 days |
| **Level 3** | Intraday -7% from open | Intraday halt (NYSE Rule 80B trigger 1) |
| **Level 4** | Intraday -13% from open | Extended halt (NYSE Rule 80B trigger 2) |
| **Level 5** | Intraday -20% from open | Market halt (NYSE Rule 80B trigger 3) |
| **Level 6** (DEC-515 Pass 53 NEW) | Portfolio DD-from-rolling-peak ≥X% | Halt all new entries until peak recovers Y%; symmetric to Layer 5 entry gating + DEC-516 regime-flip exit |

**Priority order (DEC-586 Pass 53 fix; sequential check per DEC-315):** Level 6 → Level 5 → Level 4 → Level 3 → Level 2 → Level 1 (most-severe first; supersession).

**Documentation note (per DEC-126 + DEC-314 + DEC-515 Pass 53):** Levels 3-4 + Level 6 were documented but NOT implemented in original code; implementation Sprint 2 (Phase 0.C) per DEC-314 + Pass 53 R7-10 §5.1 16-bug list.

**Source:** DEC-314, DEC-315, DEC-515 (Pass 53 Level 6 add), DEC-586 (Pass 53 priority fix), DEC-587 (regime-block reconciliation §11.1)

### 9.2 Sequential Check (per DEC-315)

**Rule:** Circuit breakers checked one-at-a-time, NOT all simultaneously.

**Per DEC-315:** "If Level 1 + Level 5 both fire same day, Level 5 takes precedence and supersedes Level 1." Sequential evaluation prevents conflicting actions.

**Source:** DEC-315

### 9.3 Recovery Rules with Cooldown + Hysteresis (per DEC-127)

**Rule:** After circuit breaker fires, recovery rules apply:

| Level | Cooldown | Hysteresis (return-to-normal threshold) |
|---|---|---|
| Level 1-2 | 1-2 days | Portfolio +0.5% (recovery confirmed) |
| Level 3 | Same day reopen if NYSE reopens | Position sizes still halved 1 day post |
| Level 4-5 | Next session | Position sizes halved 3 days post |

**Source:** DEC-127

### 9.4 Dispersion-Conditional Breaker (per DEC-128)

**Rule:** Trigger circuit breaker if cross-sectional dispersion exceeds **3σ** (3 standard deviations from rolling mean).

**Methodology:** Compute daily cross-sectional dispersion (std dev of daily returns across portfolio); rolling 30-day baseline; if today's dispersion > baseline + 3σ, fire dispersion breaker.

**Action:** Soft pause similar to Level 1.

**Source:** DEC-128

### 9.5 Time-Resolution Limits (per DEC-126)

**Documentation note:** Circuit breakers operate at **end-of-day resolution** in Stage 2 backtest (no intraday data); Stage 3+ paper trading enables intraday circuit breakers.

**Source:** DEC-126 (documents limitation)

### 9.6 Level 6 — Drawdown-from-Peak Portfolio Breaker (DEC-515 — Pass 53 owner-approved 2026-05-06 Q1 P0; CRITICAL gap)

**Trigger:** External AI 2026-05-06 review identified that Levels 1-5 (DEC-314/315) all fire on single-day or intraday-from-open. None fire on cumulative drawdown from equity peak. **Slow grind-down drawdowns kill portfolios more often than single-day shocks** — biggest risk-management gap.

**Rule (Level 6 — NEW):**

| Sub-level | Trigger (DD from peak) | Action |
|---|---|---|
| **6a** | -10% from running 252-day equity peak | Halve position sizes for 5 trading days; new entries skipped |
| **6b** | -20% from running 252-day equity peak | Flat all positions over next 5 trading days; new entries blocked |
| **6c** | -30% from running 252-day equity peak | HARD STOP — flat all positions immediately; backtest run flagged for owner review (production-mode equivalent: alert + manual unlock) |

**Recovery:** Position-sizing returns to normal once equity recovers to within -5% of prior peak (hysteresis gap matching DEC-127 pattern).

**Implementation:** ~0.5 day in `backtest/engine/circuit_breakers.py`. Computes rolling 252-day max equity; checks DD% on each trading day's close.

**Interaction with Levels 1-5 (CORRECTED per DEC-586 Pass 53 owner-approved 2026-05-06):** Sequential evaluation per DEC-315. **Priority resolution:**
- Levels 1-2 (intraday-from-open soft pause) and Level 6 (DD-from-peak) are NOT mutually exclusive — both can fire same day; **most restrictive action wins** (between them)
- Levels 3-5 (intraday hard halt per NYSE Rule 80B) take **absolute precedence** over Levels 1-2 and Level 6 sub-levels 6a/6b — market is halted; nothing else matters
- Level 6c HARD STOP and Levels 3-5 conflict resolution: **whichever fires first** (Level 5 typically same-bar; Level 6c needs end-of-day evaluation in Stage 2 per DEC-126); in live Stage 4+, simultaneous → most restrictive (Level 6c flat-all wins, since Levels 3-5 only halt trading temporarily)

**Schmitt-trigger gap:** Level 6 recovery hysteresis loosened from "-5% from peak" to **"-10% from peak"** to avoid trapping portfolio at -25% DD for years (per adversarial review). Recovery: equity must rise from current to within -10% of running 252-day peak.

**Source:** DEC-515

### 9.7 Recovery vs New Entries (DEC-127 clarification per Pass 53 owner-approved 2026-05-06 Q1 P0)

**Trigger:** External AI flagged DEC-127 cooldown rules don't specify whether new entries are taken at half-size or skipped during cooldown.

**Rule (clarification):** During cooldown periods (Levels 1-2 + 6a):
- **New entries SKIPPED** (cleaner cooldown semantics; matches most prop systems)
- Existing positions managed normally (stops + targets active)
- Existing positions sized at the half-size scaler from Level fire

During hard halts (Levels 3-5 + 6b/6c):
- **New entries BLOCKED**
- Existing positions either halted (intraday Levels 3-5) or unwound (Level 6b/6c)

**Source:** DEC-127 clarification — same DEC, additive specification.

---

## 11. Backtest Fill Methodology (DEC-514 — Pass 53 owner-approved 2026-05-06 Q1 P0; CRITICAL pre-Phase-1A bug fix)

**Trigger:** External AI 2026-05-06 review identified that EOD-bar backtests have a **silent bug** when overnight gaps blow past stop levels. Without explicit fill methodology, backtests assume stop-price fill in all cases — understates downside in earnings-gap scenarios. **#1 silent backtest bug pre-Phase-1A.**

### 11.1 Long-position stop-loss fill rules

**Setup:** Long position at entry_price; stop_price below; bar OHLC = (open, high, low, close).

| Bar pattern | Fill rule |
|---|---|
| `low > stop_price` | NO FILL — stop not triggered this bar |
| `low ≤ stop_price ≤ open` | Fill at `stop_price` (intraday triggered; assume no slippage past stop in normal moves) |
| `open < stop_price` (gap-down through stop) | **Fill at `open`** (gap-through-stop case; you cannot fill at the stop you set above the open) |
| `low ≤ stop_price` AND vol-of-day > 1.5× ATR | Fill at `stop_price - slippage_bps × adverse_selection_multiplier` (per DEC-533 P3 backlog, future) |

### 11.2 Long-position take-profit fill rules

| Bar pattern | Fill rule |
|---|---|
| `high < target_price` | NO FILL |
| `high ≥ target_price ≥ open` | Fill at `target_price` |
| `open > target_price` (gap-up through target) | Fill at `open` (favorable gap; received better than target) |

### 11.3 Short-position symmetric rules

Short stop = stop above entry; short target = target below entry. Mirror the above rules.

### 11.4 Fill priority within bar

When multiple exits could trigger same bar (stop AND target both within range), assume **stop fires first** (conservative; understates winners). Implementation choice for this asymmetry:
- Stage 2 backtest: stop-first (conservative)
- Stage 3 paper: actual order routing decides
- Document the asymmetry; revisit if Stage-2-vs-Stage-3 verdicts diverge materially

### 11.5 Partial-fill modeling

**Stage 2:** Full fill at trigger price assumed. For S&P 500 + ETFs at typical position sizes (5%/4%/3% portfolio), this is ~accurate.

**Stage 3+:** Partial-fill modeling becomes relevant for larger universes / smaller-cap names. Documented as future scope.

### 11.6 Implementation site

`backtest/engine/exit_manager.py` — fill methodology applied at each bar's close-of-day evaluation. ~0.5-1 day implementation.

**Phase 1A cannot run cleanly until DEC-514 implemented** — without it, every overnight gap-down position's downside is silently understated.

**Source:** DEC-514

---

# PART E — REGIME RULES

## 10. Regime Classification

### 10.1 8+ Inputs (per DEC-106)

| Input | Source | Role |
|---|---|---|
| **VIX** | FRED VIXCLS | Volatility level |
| **Yield curve (T10Y2Y)** | FRED T10Y2Y | Recession leading indicator |
| **HY spread (BAA10Y)** | FRED BAA10Y | Credit stress |
| **ICSA jobless** | FRED ICSA | Labor market |
| **Breadth** | NYSE A/D ratio | Internal market health |
| **Sector dispersion** | Std dev of sector returns | Cross-sectional health |
| **AAII** | Refresh script (DEC-319) | Retail sentiment |
| **CNN Fear & Greed** | Refresh script (DEC-320) | Composite sentiment |

**Source:** DEC-106

### 10.2 Regime Probability vs Hard Label (per DEC-107)

**Rule:** Regime emitted as **probability distribution** over regime classes, NOT hard label.

**Regime classes:** Bull / Bull-Pause / Neutral / Bear-Pause / Bear / Crisis

**Output format:**
```
{
    "Bull": 0.45,
    "Bull-Pause": 0.30,
    "Neutral": 0.15,
    "Bear-Pause": 0.05,
    "Bear": 0.04,
    "Crisis": 0.01
}
```

Strategies consume regime probability vector (not hard label).

**Source:** DEC-107

### 10.3 EMA Smoothing (Not HMM) (per DEC-108)

**Rule:** Regime probabilities smoothed via **Exponential Moving Average** (NOT Hidden Markov Model).

**Methodology:**
```
regime_prob_smoothed[t] = α × regime_prob_raw[t] + (1-α) × regime_prob_smoothed[t-1]
α = 0.1  # ~10-day half-life
```

**Why not HMM:** HMM more complex, more parameters, harder to interpret; EMA simpler and produces similar smoothing. DEC-247 stats/ML implementation review verified EMA correctness.

**Source:** DEC-108

### 10.4 Regime Transition Probability Matrix (per DEC-149)

**Rule:** Track regime transition probabilities (Bull→Bull, Bull→Bear, etc.).

**Methodology:** Estimated from historical regime sequences via maximum likelihood. Used for forward-looking regime expectation.

**Source:** DEC-149

### 10.5 Multi-Asset Extension (12+ inputs) (per DEC-150)

**Expansion to 12+ inputs adds:**
- **Credit:** HY spread (already), IG spread
- **Commodity:** DBA, GSCI
- **Currency:** DXY

**Source:** DEC-150

### 10.6 Sector-Level Regime (per DEC-151)

**Rule:** Per-sector regime computed independently of market-level.

**Example (2022):** XLK (Tech) = bear, XLE (Energy) = bull, XLF (Financials) = neutral.

**Source:** DEC-151

### 10.7 Regime Hysteresis VIX SMA (per DEC-317 + DEC-559 Pass 53 P0 standardization)

**Rule:** Regime transitions require VIX to cross threshold AND stay there for SMA window. **Standardized to 5-day SMA per DEC-559 Pass 53 P0 (was inconsistent: §2A.4 said 5d / prior §10.7 said 21d — DEC-559 promoted P3→P0 to resolve contradiction).**

**Methodology:** Prevents single-day VIX spike from triggering regime change. 5-day SMA chosen for responsiveness to fast regime shifts (2020-03 COVID, 2022 inflation) while still filtering noise.

**Source:** DEC-317 (parent), DEC-559 (Pass 53 standardization to 5d).

### 10.7.A Pass 53 DEC-588 doc-reconciliation cross-refs (regime methodology)

Pass 53 review-cycle adds substantial regime methodology codified at §10.10-10.21. For top-to-bottom readability:

- **DEC-539** (§10.10) — Regime training/labeling mechanism (CRITICAL P0)
- **DEC-540** (§10.11) — Regime probability consumption pattern (CRITICAL P0)
- **DEC-541** (§10.12) — Regime classifier validation methodology (P0)
- **DEC-542** (§10.13) — Collapse 6 → 4 regime classes (P0)
- **DEC-543** (§10.14) — Stage 2 vs Stage 3+ regime-input parity (P0)
- **DEC-544** (§10.15) — Asymmetric EMA smoothing (P1)
- **DEC-545** (§10.16) — EMA + transition-matrix integration (P1)
- **DEC-546** (§10.17) — Schmitt-trigger on regime binarization + min-duration (P1)
- **DEC-547+** (§10.18-10.21) — additional regime methodology DECs
- **DEC-583** (§16.2 walk-forward 2018-2021 truncation fix) — walk-forward train window truncated to 2021-05+ since Polygon Stocks Starter cache starts 2021-05 per DEC-505
- **DEC-587** (§11.1 regime-block reconciliation) — circuit breaker + regime-eligibility coordination
- **DEC-559** (this section) — VIX hysteresis 5d standardization

All DECs RESOLVED-DECIDED at Pass 53 owner approval 2026-05-06; codified inline below.

### 10.8 Smart Money Composite Score (per DEC-124 + DEC-332 + DEC-450)

**Per-source signal labels:**

| Source | Lookback | PIT enforcement | Signal logic |
|---|---|---|---|
| **Congressional** (Quiver `/historical/congresstrading/{ticker}`) | 45 days, age-weighted by *transaction* date: <30d=1.0× / 30-60d=0.5× / >60d excluded | STOCK Act 45-day disclosure lag — filter to `disclosure_date ≤ as_of` (per DEC-324 fix Pass 51 — age-weight by transaction date, PIT-filter by disclosure date) | `sells > buys & sells ≥ 2` → `sell`; `senate_buys ≥ 2` OR `cluster_buy (≥3 unique representatives)` → `strong_buy`; `buys ≥ 1` → `buy`; else `none` |
| **Insider** (Quiver `/historical/insidertrading/{ticker}`) | 30 days | `filing_date ≤ as_of`. EXCLUDES non-discretionary transactions: Option / Exercise / 10b5-1 / Gift / Transfer | `unique_sell_insiders ≥ 3` → `cluster_sell`; `CEO_buy & cluster (≥3 unique buyers)` → `strong_buy`; `CEO_buy OR cluster` → `buy`; `buys ≥ 1` → `weak_buy`; else `none` |
| **Institutional / 13F** (Quiver `/historical/institutionalholdings/{ticker}`) | latest available quarter | `available_after = quarter_end + 45 days` (SEC filing deadline per DEC-325) ≤ as_of | `new_pos ≥ 3` OR `(new_pos ≥ 1 & increased ≥ 2)` → `strong_buy`; `new_pos ≥ 1` OR `increased ≥ 2` → `buy`; `decreased > increased` → `negative`; else `none` |

**Composite scoring (additive with one veto):**

VETO CASE — `congressional == sell` AND `insider == cluster_sell` → `score = -5`, composite = `congressional_sell+insider_cluster_sell` (skips additive math entirely).

OTHERWISE additive per source:

| Source | strong_buy | buy | weak_buy | sell | cluster_sell | negative |
|---|---|---|---|---|---|---|
| Congressional | +4 | +2 | — | -3 | — | — |
| Insider | +4 | +2 | +1 | — | -3 | — |
| Institutional | +2 | +1 | — | — | — | -1 |

**Composite label by score:**

| Score | Label |
|---|---|
| ≥ 6 | `congressional+insider_cluster` |
| ≥ 4 | `congressional_or_insider` |
| ≥ 2 | `any_buy` |
| ≥ 1 | `weak_buy` |
| 0 | `none` |
| < 0 | `negative` |
| ≤ -4 | `congressional_sell+insider_cluster_sell` |

**Decay weighting:** smart money signals decay with 90-day half-life per DEC-123 (REVISIT_AFTER_BACKTEST tag in §23.1 #15).

**Tunability:** weights are tagged tunable post-Phase-1B-α per DEC-072. Treat current values as baseline pending empirical tuning per §23 methodology.

**Source:** DEC-124 (cross-source confluence); DEC-332 (composite weights — RESOLVED-DECIDED Pass 48, body completed Pass 53 with the current numeric values per B1); DEC-450 (Quiver paid endpoints); DEC-123 (90-day decay half-life); DEC-072 (smart money scope = congressional + insider + 13F; WSB separate); DEC-073 (hand-roll composites, not Quiver pre-built); DEC-324 (PIT fix: disclosure-date filter, transaction-date age-weight); DEC-325 (13F filing-date PIT lag).

**Implementation:** `backtest/data/smart_money.py:470-529` (composite); `:317-374` (congressional); `:381-421` (insider); `:428-463` (institutional).

### 10.9 Smart Money-Adjacent Signals

These signals are computed alongside the smart money composite but are NOT included in the composite score. Each produces its own signal label consumed by agents and screener separately.

| Signal | Source | Endpoint / cache | Lookback | Signal logic |
|---|---|---|---|---|
| **News sentiment** | Polygon news (PRIMARY post-Sprint-4 per DEC-440) | `/v2/reference/news?ticker=...` | 7 days | `score ≥ 0.15` → bullish; `≤ -0.15` → bearish; else neutral. **Migration note Pass 53:** current code at `smart_money.py:545-615` reads from `cache/av_news/{ticker}.parquet` then falls back to `cache/finnhub_news/{ticker}.parquet`; Sprint 4 (DEC-454/455 deprecation cleanup) replaces both with the Polygon news endpoint. Code path lags this spec until Sprint 4. |
| **Government contracts** | Quiver prefetch | `cache/quiver/gov_contracts/{ticker}.parquet` | 365 days | `total_amount > 0` → bullish; `recent_win` flag if any win in last 90 days; trend = growing/stable. |
| **Lobbying** | Quiver prefetch | `cache/quiver/lobbying/{ticker}.parquet` | 365 days | `total_spend > $1M` → high_spend; `> $100k` → moderate; else low. |
| **Analyst data** | yfinance `Ticker.info` + `recommendations` + `upgrades_downgrades` + Quiver `/historical/analystestimates/{ticker}` | live yfinance + Quiver API | 30 days for upgrades/downgrades window | **LIVE-ONLY WARNING per DEC-299/443:** `recommendationMean`, `targetMeanPrice`, EPS estimates always return CURRENT not as-of values — used for site card display ONLY; do NOT affect tier or pass/fail criteria. PIT enforced on `recommendations` history and upgrades/downgrades window only. |

**Source:** DEC-450 (Quiver paid: gov_contracts + lobbying); DEC-299/443 (yfinance .info LIVE-ONLY warning); DEC-440 (news endpoint).

**Implementation:** `backtest/data/smart_money.py:618-705` (gov_contracts + lobbying); `:549-615` (news); `:88-253` (analyst).

---

### 10.10 Regime training/labeling mechanism (DEC-539 — Pass 53 owner-approved 2026-05-06 Q1 P0; CRITICAL)

**Trigger:** External AI 2026-05-06 review identified that DEC-107 spec doesn't define how the 6 regime classes (now 4 per DEC-542) are operationally labeled. The classifier's quality depends entirely on this.

**Resolution:** Hand-labeled historical periods + threshold-rule cross-validation.

**Labeling protocol:**
1. **Reviewer:** owner + Claude jointly review SPY price action + VIX + macro context per quarter for 2010-2026 (~16 years × 4 quarters = 64 labeling sessions; ~5-10 min each)
2. **Per-day labels:** each trading day gets one of 4 regime labels (Bull / Neutral / Bear / Crisis) based on:
   - SPY return regime (trailing 60-day return + slope of 200-SMA)
   - VIX regime (level + 20-day SMA + percentile in trailing 252-day distribution)
   - Macro context (recession flag from FRED RECPROUSM156N, financial-stress STLFSI4)
   - Crisis: VIX > 40 sustained ≥3 days OR -10% drawdown in 5 trading days OR explicit market-stress event (Mar 2020, Aug 2024 yen unwind)
3. **Stable label periods:** ≥ 5 trading days minimum (matches DEC-546 min-duration constraint)
4. **Cross-validation:** 70% in-sample / 30% out-of-sample split chronologically (no leakage); regime classifier trained on in-sample, tested on out-of-sample
5. **Versioning:** labels stored as `data_prefetch/regime_labels/labels_v1.parquet` with reviewer + timestamp + criteria hash

**Effort:** ~2-3 days labeling + ~1 day cross-validation infrastructure. Pre-Phase-1A.

**Source:** DEC-539

### 10.11 Regime probability consumption pattern (DEC-540 — Pass 53 owner-approved 2026-05-06 Q1 P0; CRITICAL)

**Trigger:** External AI identified inconsistency — DEC-107 says strategies consume probability vector; Layer 5 (this Pass Q1) uses hard regime tags. **Reconcile.**

**Resolution:** Two-stage consumption:
1. Classifier (DEC-107) outputs probability vector `{P(Bull), P(Neutral), P(Bear), P(Crisis)}` summing to 1
2. **Binarization layer (DEC-546 Schmitt-trigger)** converts vector to hard regime tag
3. Layer 5 strategies consume the **binarized hard tag** (not the raw probability vector)

**Per-strategy consumption rule:**
```
strategy fires only if:
  current_binarized_regime ∈ strategy.regime_eligible
  AND P(current_binarized_regime) > 0.5  (confidence floor)
```

**Crisis-override** per CLAUDE.md preserved: longs allowed at 50% size when binarized_regime=crisis, regardless of strategy's `regime_eligible` set.

**Source:** DEC-540

### 10.12 Regime classifier validation methodology (DEC-541 — Pass 53 owner-approved 2026-05-06 Q1 P0)

**Trigger:** External AI identified that we don't know if the 8-input EMA-smoothed classifier beats a simple SPY-200SMA-sign baseline. Common failure mode: sophisticated classifier that's actually just a slow SPY indicator.

**Validation protocol (pre-Phase-1A):**

1. **Baseline classifier:** SPY-200SMA-sign (3-class: long-trend = SPY > 200 SMA + slope up; neutral = SPY ≈ 200 SMA OR slope flat; short-trend = SPY < 200 SMA + slope down)
2. **Test classifier:** 8-input EMA-smoothed (DEC-106/107/108) post DEC-542 4-class collapse
3. **Test metrics on out-of-sample 30% of DEC-539 labels:**
   - **Regime-conditional Sharpe:** forward 20-day SPY return given regime label; should differ across regimes (Bull > Neutral > Bear)
   - **Regime persistence:** % of days in same regime as prior day (target: >85% — too low = thrashing; too high = stale)
   - **Regime accuracy:** classifier label vs hand-labeled ground truth (target: >75% on 4-class problem)
4. **Decision criterion:** 8-input must beat baseline on **at least 2 of 3 metrics with p < 0.05** (paired permutation test)
5. **If 8-input fails:** simplify to 4-input or 3-input subset; retest

**Effort:** ~1-2 days validation infrastructure + cross-validation runs. Pre-Phase-1A.

**Source:** DEC-541

### 10.13 Collapse 6 → 4 regime classes (DEC-542 — Pass 53 owner-approved 2026-05-06 Q1 P0)

**Trigger:** External AI identified that 6 classes (Bull / Bull-Pause / Neutral / Bear-Pause / Bear / Crisis) is statistically over-specified for ~6,300 trading days of data. Crisis is overwhelmingly rare (~100-200 days total in 25 years); statistical estimation of Crisis transitions is nearly impossible.

**Resolution:** Collapse to **4 regimes matching F-006 classifier**: `{Bull, Neutral, Bear, Crisis}`.

**Mapping from 6 → 4:**
- Bull-Pause → Neutral (trend losing momentum is statistically indistinguishable from neutral with our data)
- Bear-Pause → Neutral (mirror)

**Rationale:**
- 6,300 days / 4 classes = 1,575/class average (vs 1,050 for 6-class)
- Crisis stays at ~100-200 days (rare; expected)
- Bull / Neutral / Bear bear class boundaries are now wider — easier to fit reliable transitions

**Source:** DEC-542

### 10.14 Stage 2 vs Stage 3+ regime-input parity (DEC-543 — Pass 53 owner-approved 2026-05-06 Q1 P0)

**Trigger:** Per DEC-447, Stage 3+ adds richer breadth inputs (PCT_ABOVE_50/200EMA, new high/low ratio). External AI identified that backtest-calibrated strategy parameters wouldn't transfer to live if the regime classifier itself differs across stages.

**Resolution:** **Option A — Freeze inputs at Stage 2 set** (8 inputs per DEC-106; 12+ per DEC-150 multi-asset).

- Stage 3+ live richer breadth (DEC-447) used for **monitoring only**, NOT regime calibration
- Strategy parameters calibrated on Stage 2 regime classifier remain valid in Stage 3+
- Trade-off: Stage 3+ doesn't get to use the better breadth signals in regime classification — accepted to preserve calibration validity

**Alternative considered (rejected):** Option B re-validate all backtest-derived strategy parameters when Stage 3+ richer breadth comes online — too expensive; high risk of validity loss

**Source:** DEC-543

### 10.15 Asymmetric EMA smoothing (DEC-544 — Pass 53 owner-approved 2026-05-06 Q2 P1)

**Trigger:** External AI identified that single α=0.1 EMA (10-day half-life) is suboptimal for risk management — fast regime changes (Mar 2020, Aug 2024 yen unwind) detect Bear/Crisis well after losses.

**Resolution:** Per-direction α with fast-in / slow-out asymmetry:

| Transition | α | Half-life | Rationale |
|---|---|---|---|
| → Bear or Crisis | **0.20** | 5 days | Catch downside fast — risk management priority |
| → Recovery (Bear → Neutral or Neutral → Bull) | **0.05** | 20 days | Confirm recovery before re-risking |
| → Neutral or → Bull (non-recovery) | 0.10 | 10 days | Default symmetric smoothing |

**Implementation:** EMA function checks current vs prior regime; selects α from per-transition table. ~0.5 day in `backtest/engine/regime_filter.py`.

**Source:** DEC-544

### 10.16 EMA + transition-matrix integration (DEC-545 — Pass 53 owner-approved 2026-05-06 Q2 P1)

**Trigger:** External AI identified that DEC-108 EMA and DEC-149 transition matrix are decoupled — two unrelated mechanisms doing related work.

**Resolution:** Transition matrix posterior-updates EMA output via Bayesian update.

**Formula:**
```
P_EMA(regime) = EMA-smoothed regime probability (DEC-108 + DEC-544 asymmetric)
P_transition(regime | prior_regime) = DEC-149 transition matrix
P_final(regime) = P_EMA(regime) × P_transition(regime | prior_regime)
P_final normalized to sum to 1 across regimes
```

This integrates both mechanisms: EMA captures input-driven regime probability; transition matrix encodes regime persistence (regimes don't randomly flip; prior-regime conditional matters).

**Source:** DEC-545

### 10.17 Schmitt-trigger on regime binarization + min-duration (DEC-546 — Pass 53 owner-approved 2026-05-06 Q2 P1)

**Trigger:** External AI identified that no Schmitt threshold exists on regime probability binarization; regime probability hovering at 0.5 will flap. Min-duration constraint also missing.

**Resolution:**

| Rule | Threshold |
|---|---|
| **Enter regime X** | P(X) > 0.6 |
| **Stay in regime X** | P(X) > 0.4 (Schmitt gap; prevents flapping at 0.5) |
| **Exit regime X** | P(X) < 0.4 |
| **Min-duration in regime** | ≥ 5 trading days (regardless of probability — prevents thrashing on noise) |
| **Crisis-override** | Crisis can flip ON within 1 day if VIX > 50 (catastrophic event) — bypasses min-duration |

**Source:** DEC-546

### 10.18 Smart money veto symmetry (DEC-547 — Pass 53 owner-approved 2026-05-06 Q2 P1)

**Trigger:** External AI identified that current veto is asymmetric (cluster_sell vetoes to -5; no equivalent buy boost).

**Resolution:** Symmetric veto.

| Combined source signal | Score |
|---|---|
| cong=strong_buy AND ins=strong_buy AND inst=accumulate | **+5 (NEW symmetric to -5)** |
| cong=sell AND ins=cluster_sell | -5 (existing) |

**Note:** External AI suggested "sells more informative than buys" rationale (Lakonishok-Lee 2001) as alternative — owner-rejected; symmetry chosen for cleanliness. If empirical results in Phase 1B-α suggest sell-asymmetry has edge, revisit via DEC.

**Source:** DEC-547

### 10.19 Sector regime distinct from market regime (DEC-548 — Pass 53 owner-approved 2026-05-06 Q2 P1)

**Trigger:** External AI identified that DEC-151 sector-level regime claims independence from market-level but doesn't specify what inputs the sector regime uses. If same macro inputs as market regime, every sector has identical regime — defeats the purpose.

**Resolution:** Two-level hierarchy.

**Level 1 — Market regime** (existing): 8-input macro classifier per DEC-106/107/108/542
- Outputs: `{Bull, Neutral, Bear, Crisis}` (4-class)

**Level 2 — Sector regime** (NEW per DEC-548): per-sector deviation from market
- Inputs (sector-specific):
  - Sector ETF 60-day return (vs SPY)
  - Sector ETF 20-day realized vol (per DEC-513 #1)
  - Sector breadth (% stocks in sector above 50-SMA)
  - Sector dispersion (intra-sector return std-dev with direction per DEC-554)
  - Sector beta to SPY (252-day rolling per DEC-513 #2)
- Outputs: `{Bull, Neutral, Bear}` (3-class — Crisis is market-wide only)
- Cross-sectional consistency: sector regime is a **deviation from market regime**, not an independent classifier — XLK can't be in Bull when SPY is in Crisis

**Source:** DEC-548

### 10.20 Smart money composite + adjacent — additional DECs (P2-P4 backlog)

| DEC | Title | Effort |
|---|---|---|
| DEC-549 | Cluster_buy/cluster_sell threshold symmetry — tighten cluster_sell to require officer-level seller (mirrors cluster_buy CEO requirement) | ~0.5d |
| DEC-550 | Smart money signal normalization — gov contracts → % of revenue; lobbying → YoY change vs baseline; news sentiment → per-ticker rolling z-score | ~1d |
| DEC-551 | Regime × smart money interaction — explicit composition rule (independent inputs to position sizing; NOT veto) | ~0.5d |
| DEC-552 | Regime-conditional smart money weighting — Phase 1B-α tunable: insider buying in bear regime weighted higher than bull regime (private-info-offsets-bearishness rationale) | ~1-2d Phase 1B-α |
| DEC-553 | Equity-bond correlation as regime input (rolling 60-day SPY-TLT correlation) | ~0.5d |
| DEC-554 | Sector dispersion direction (pair std-dev with median sector return sign or skew) — disambiguates rotation-bull vs breakdown-bear | ~0.5d |
| DEC-555 | CFTC COT promotion to regime input (currently sentiment-only; should also be regime input given dealer positioning is regime-relevant) | ~0.5d |
| DEC-556 | Smart money tunability extension to structure (additive vs multiplicative vs Bayesian vs ML-ensemble) — Layer-1 architectural decision separate from weights | post-Phase-1B-α |
| DEC-557 | "Decreased > increased" stability fix — minimum count threshold (decreased ≥ 3, decreased > increased + N) | ~0.25d |
| DEC-558 | "new_pos ≥ 3" universe-normalization — % of trackable institutions opening new positions, OR new positions vs trailing average for that ticker | ~0.5d |
| DEC-559 | VIX SMA threshold reconciliation — 5-day vs 21-day SMA across docs; standardize | ~0.25d |
| DEC-560 | Score tier boundaries documented in source-mix terms (≥6 = strong_buy + 1 buy across sources; ≥4 = single strong_buy or two buys) | ~0.25d |
| DEC-561 | ICE BofA HY OAS (BAMLH0A0HYM2) preferred over BAA10Y for crisis sensitivity (we have both in FRED 50-series; use BAMLH0A0HYM2 as primary) | ~0.25d |
| DEC-562 | TED/SOFR-OIS / repo / dollar-funding stress as crisis-tail signals (free via NY Fed) | ~1d |
| DEC-563 | Senate-vs-House priority documentation + citation (Pelosi-style trades, committee access — defensible heuristic) | ~0.25d |
| DEC-564 | NAAIM exposure index as positioning input (weekly, free) | ~0.5d |
| DEC-565 | Commodity term structure (oil contango/backwardation, gold/silver ratio) | ~0.5d |

All DEC-549-565 are RESOLVED-DECIDED at backlog level (Pass 53 owner-approved 2026-05-06 Q3); implementation post-Phase-1B-α or as Sprint priorities allow.

### 10.21 Adversarial-review DECs — DEC-559 promoted + DEC-566-588 (Pass 53 Q1+Q2+Q3 owner-approved 2026-05-06)

**Trigger:** External-AI adversarial review of TRADING_RULES_AND_INFORMATION.md identified ~12 real bugs + ~25 critical gaps. Owner approved P0+P1+DEC-588 batch (Q4 DEC-581 endogeneity protection NOT in this approval).

#### Q1 P0 — Pre-Phase-1A blockers (10 DECs; 9 inline-fixed above; DEC-588 spec below)

| DEC | Resolution location |
|---|---|
| **DEC-559** | VIX hysteresis 5d vs 21d reconciliation — **standardize on 5-day SMA ≥40 enter / <35 exit** (matches §2A.4); §10.7 21-day reference deprecated. Inline edit pending §10.7. |
| **DEC-566** | "What happens on failure" branches — every gate gets explicit failure action: (a) abandon (strategy promoted to RETIRED status); (b) retry with different parameters (Phase 1A-α RETRY_ONCE); (c) fallback (default rule-only); (d) owner-review (manual intervention required). Per-gate table TBD; DEC-566 spec to be drafted in §1+§2 next pass. |
| **DEC-569** | Cube primary vs drilldown dimensions — **Primary (cell verdict applies):** (1) Strategy, (2) Regime, (3) Sector, (4) Direction, (5) Exit method = 5 dims. **Drilldown (post-hoc analysis only; no verdict):** remaining 12 dims. Resolves §21 vs §3.1 sample-size inconsistency. |
| **DEC-582** | Bonferroni × t-stat double-counting fix → §3.2 inline-edited above (correction at strategy level only; cube-cells via FDR per DEC-470 PROPOSED) |
| **DEC-583** | Walk-forward 2018-2021 OHLCV source → §16.2 inline-edited above (truncate to 2021-05+; 4y train acceptable) |
| **DEC-584** | §6.2 max-loss cap math fix → §6.2 inline-edited above (`× ticker_capital_allocated` not `× initial_portfolio`) |
| **DEC-585** | Strategy count 119 → 199 + exit count 17 → 20 doc reconciliation → multiple §s inline-edited via global replace |
| **DEC-586** | §9.6 vs §9.2 circuit breaker priority resolution → §9.6 inline-edited above; recovery hysteresis loosened to -10% |
| **DEC-587** | §11.1 vs Layer 5 regime-block reconciliation → §11.1 inline-edited above (direction is unconstrained; strategy CHOICE is constrained) |
| **DEC-588** | TRADING_RULES doc-reconciliation pass propagating DEC-509 through DEC-565 into all affected §s. Scope: ~3-5 days targeted edits across §1, §2, §3, §5, §7, §8, §9, §10, §11, §12, §13, §14, §16, §17, §18, §21, §22. Track via separate sprint task; DEC-588 declares INTENT this turn; full propagation done in subsequent commit(s). |

#### Q2 P1 — High-leverage adds (13 DECs)

| DEC | Title | Effort |
|---|---|---|
| DEC-567 | PM confidence calibration check (Brier-score + reliability diagram pre-Phase-1B production gate) | ~1d |
| DEC-568 | Walk-forward fold aggregation methodology (pooled-trade Sharpe + bootstrap CI per fold; NOT mean-of-fold-Sharpes) | ~1d |
| DEC-570 | Event-suppression calendar extension (NFP, PPI, ISM, Treasury auctions, ECB/BoJ/PBoC) | ~0.5d |
| DEC-571 | Corporate-action exit handling extension (M&A bid period; bankruptcy/Ch11; reverse splits; going-private) | ~1d |
| DEC-572 | Universal cache freshness-policy table (Polygon news intraday; Quiver insiders 4-day filing window; AAII Thursdays; CNN F&G daily) | ~0.5d |
| DEC-573 | Slippage floor + half-spread modeling (correct §14.2 size_factor=0 baseline gap; add explicit spread cost) | ~1d |
| DEC-574 | Borrow rate model (Ortex when subscribed per DEC-506; conservative default 30bps easy / 5% hard until subscribed) | ~0.5d |
| DEC-575 | Performance-metrics correctness pass (rf_daily DTB3 not FEDFUNDS; Sortino MAR-anchored not zero; L-moments skew/kurtosis estimators) | ~1-2d |
| DEC-576 | Promote DEC-512 PIT-fundamentals audit close to hard checklist gate in §2.6 Phase 1A acceptance | ~0.25d |
| DEC-577 | Unify `gate_score` vs `PM confidence` terminology (deprecate `gate_score` post-DEC-459) | ~0.25d |
| DEC-578 | F-009 7th gate — absolute mean-return-per-trade-net-of-cost floor (extends DEC-510 6-gate; pairs with R:R 2.0 floor; closes "5R:R 12% win-rate gameable" loophole) | ~0.5d |
| DEC-579 | MAE/MFE cross-validated percentiles (step-down from 90th to 75th to leave OOS noise headroom; protects against in-sample overfit) | ~0.5d |
| DEC-580 | Vol-targeting vs tier-sizing precedence rule (tier-size sets MAX; vol-target scales DOWN if vol > target) | ~0.25d |

All Q2 P1 DECs RESOLVED-DECIDED at spec level Pass 53; implementation Sprint pre-Phase-1A.

#### Q4 NOT IN THIS APPROVAL (DEC-581 — tuning methodology + endogeneity-loop protection)

Owner did not include Q4 in "Q1 Q2 Q3 A" approval. **DEC-581 remains PROPOSED** awaiting separate owner approval — the deepest critique from the adversarial review (28 REVISIT_AFTER_BACKTEST items create endogeneity loop where post-backtest decisions are conditioned on backtest results which were conditioned on different decisions). Re-offered at end of next response.

---

## 11. Regime-Conditional Strategy Behavior

### 11.1 Crisis-Flag Handling (replaces hard regime direction blocks)

**Per project memory:** Original system had hard regime direction blocks (e.g., long-only blocked in Bear regime). **REMOVED for direction (long+short philosophy per Pass 53 owner directive "buy the dip and sell the rip" — no direction-based regime block).**

**RECONCILIATION with Layer 5 per DEC-587 Pass 53 owner-approved 2026-05-06 (adversarial review fix):** Layer 5 regime-eligibility flags (DEC-516/540) are NOT direction blocks — they are STRATEGY-eligibility gates per category. RSI-oversold-long is gated on `[neutral]` regime not because long is blocked in Bear, but because RSI-oversold mean-reversion logic doesn't have edge in Bear regimes. **Direction is unconstrained by regime; strategy CHOICE is constrained by regime.** No contradiction with §11.1 once distinction is made. Crisis-override (longs at 50% size) preserves direction freedom across all regimes.

**Replacement:** Crisis flagging — strategies respect `crisis_flag` (computed from regime probability per DEC-107) but no hard blocks.

**Implication:** Strategies can fire in any regime; crisis_flag is informational input, not gate.

**Source:** Project memory + DEC-262/317

### 11.2 Regime Probability Gating per Strategy

**Rule:** Per-strategy regime sensitivity:
- Some strategies require `Bull regime probability > 0.5` for entry
- Some strategies require `Bear regime probability > 0.5` for short entry
- Some strategies are regime-agnostic

**Configuration:** Per-strategy `regime_filter` field in STRATEGY_REGISTER (joint DEC-100 + DEC-422 cube dimension).

### 11.3 Regime-Conditional Candidate Cap (per DEC-262)

**Rule:** Maximum candidates per regime:

| Regime | Max Candidates |
|---|---|
| Bull / Bull-Pause | 20 candidates/day |
| Neutral | 15 candidates/day |
| Bear-Pause / Bear / Crisis | 10 candidates/day |

**REVISIT_AFTER_BACKTEST:** Caps tunable empirically.

**Source:** DEC-262

### 11.4 Regime Hysteresis (per DEC-317)

See §10.7 above.

---

# PART F — DATA INTEGRITY RULES

## 12. PIT (Point-in-Time) Correctness

### 12.1 Definition

**PIT correctness:** `loader.fetch(as_of=D)` returns rows with `date ≤ D` only. No row with `date > D` may appear in result set.

**Why critical:** Lookahead bias is the most common cause of inflated backtest results that fail in live trading.

### 12.2 PIT Guard: RAISE not WARNING (per DEC-305)

**Rule:** Any row with `date > as_of` in fetcher output triggers **EXCEPTION** (not log warning).

**Implementation:**
```python
def fetch(as_of):
    rows = fetcher.get(as_of)
    for row in rows:
        if row.date > as_of:
            raise PITViolationError(f"Row date {row.date} exceeds as_of {as_of}")
    return rows
```

**Source:** DEC-305

### 12.3 yfinance .info CURRENT not as_of (per DEC-299/443)

**Caveat:** yfinance `Ticker.info` returns CURRENT data (not historical as-of). Use only when CURRENT semantics are appropriate; warn explicitly when used.

**Per DEC-443:** absorbed BUG-218; Sprint 4 implementation includes warnings + as_of-aware fallback where possible.

**Source:** DEC-299, DEC-443

### 12.4 ALFRED Archival FRED for Vintage Data (per DEC-301)

**Rule:** For PIT-correct macro data (vintage as_of), use **ALFRED** (Archival FRED) not standard FRED.

**Why:** FRED data is revised over time (e.g., GDP estimates revised quarterly); current FRED query for historical date returns CURRENT value of that date's data. ALFRED returns the value as published originally.

**Source:** DEC-301

### 12.5 PIT Regression Tests via freezegun (per DEC-050)

**Rule:** Every PIT-loader function tested with `freezegun.freeze_time(D)`; verifies fetch behavior with frozen system time.

**Test pattern:**
```python
@freeze_time("2024-01-15")
def test_loader_pit():
    result = loader.fetch(ticker='AAPL', as_of='2024-01-15')
    assert all(r.date <= datetime(2024, 1, 15) for r in result)
```

**Source:** DEC-050

---

## 13. Cache Rules

### 13.1 Schema Versioning (per DEC-330)

**Rule:** Cache schemas have explicit version field; schema migration on version bump.

**Versions:**
- v1: Original Stage 1 cache
- v2: Pass 52 raw OHLCV (DEC-298)
- v3+: Future migrations as needed

**Source:** DEC-330

### 13.2 Cache Stores RAW OHLCV (per DEC-298)

**Rule:** yfinance `auto_adjust=False`; cache stores **raw OHLCV + corp actions**; recompute adjusted-on-demand by as_of date.

**Why:** Adjusted OHLCV in cache is forward-looking (adjustments include future splits/dividends). Raw OHLCV is PIT-correct; adjustments computed at query time using corp_actions table filtered by as_of.

**Sprint sequencing:** Sprint 4 implementation early; DEC-377 + DEC-411 wait.

**Source:** DEC-298

### 13.3 Eviction Policy — Prefetched Preserved (per DEC-225)

**Rule:** Cache eviction never evicts **prefetched** rows (FRED, AAII, CNN F&G, sector ETFs, macro).

**Why:** Prefetched data is expensive to re-fetch; on-demand OHLCV cheap to refetch. Eviction prioritizes least-recently-used OHLCV first.

**Source:** DEC-225

### 13.4 Size Monitoring 80% Disk Threshold (per DEC-227)

**Rule:** When cache size reaches **80% of disk allocation**, log warning + trigger eviction of LRU OHLCV rows (preserving prefetched per §13.3).

**Source:** DEC-227

### 13.5 Filelock Fail-Fast (per DEC-328)

**Rule:** Cache writes acquire filelock; if lock unavailable >5sec timeout → fail-fast (raise exception, don't block forever).

**Source:** DEC-328

### 13.6 Multi-Process Safe Globals (per DEC-329)

**Rule:** Cache globals safe under multiprocessing; no race conditions on shared cache state.

**Implementation:** Per-process cache instance; coordinate via filesystem locks (DEC-328) and atomic writes.

**Source:** DEC-329

### 13.7 Zero-Volume Day Preservation (per DEC-310)

**Rule:** Zero-volume trading days preserved in cache with `is_halted=True` flag (don't drop).

**Why:** Halted days are real data; dropping creates bias and confuses calendar logic.

**Source:** DEC-310

### 13.8 Ticker Collision (per DEC-309)

**Rule:** Tickers like BRK-B / BRK.B (different symbol formats) resolved to canonical ticker ID.

**Implementation:** Symbol normalization layer that maps all formats → canonical (e.g., BRK.B canonical, BRK-B alias).

**Source:** DEC-309

### 13.9 NYSE Calendar (pandas_market_calendars per DEC-235)

**Rule:** Use `pandas_market_calendars.get_calendar('NYSE')` for trading day arithmetic.

**Why:** Holidays, half-days, special closures correctly handled. Don't roll your own calendar.

**Source:** DEC-235

### 13.10 Cache Freshness (per DEC-260)

**Rule:** Cache row has `last_validated_timestamp`; staleness threshold per data source:
- OHLCV: 1 day
- FRED macro: 7 days
- 13F filings: 90 days

**Source:** DEC-260

### 13.11 File-Level Checksum (per DEC-117)

**Rule:** Cache files have file-level checksum (SHA256) to detect corruption.

**Source:** DEC-117

### 13.12 API Endpoint Inventory

Comprehensive inventory of external endpoints consumed by the system. PIT lag = how stale the data is when first available (e.g., 13F filings have a 45-day SEC filing deadline). Status reflects post-Pass-53 deprecation cleanup direction (Sprint 4 DEC-453/454/455).

**Sprint 0A scope (DEC-497 RESOLVED-DECIDED Pass 53 owner directive 2026-05-05):** ALL endpoints from ALL planned APIs are prefetched for ALL universe tickers within testing date range 2020-01-01 → today. NO LIVE API CALLS in Stage 2 backtest (HARD CUT — owner Q8). yfinance permitted for one-time setup only.

**Eight APIs in Sprint 0A scope:**
1. **Polygon Stocks Starter** ($29/mo, DEC-441) — 16+ endpoints: aggregates daily/grouped, reference tickers/events/financials, news, splits, dividends, indicators (SMA/EMA/RSI/MACD), NBBO quotes selective per DEC-446
2. **FRED + ALFRED** (free) — ~52 series across 14 categories (yield curve, inflation, employment, GDP, credit spreads, money supply, industrial activity, housing, consumer, FX, commodities, volatility VIXCLS replaces yfinance ^VIX, financial conditions, recession indicators) — owner-confirmed full 52 Pass 53
3. **Quiver Trader tier** (DEC-450) — 11+ endpoints confirmed via probing: congresstrading, senatetrading, housetrading, govcontracts, lobbying, offexchange, politicalbeta, wallstreetbets, insiders bulk, twitter, politicalbeta live (owner-side dashboard list pending for full inventory)
4. **AAII** (free) — single CSV (5 fields: bullish/neutral/bearish/spread/MA8)
5. **CNN Fear & Greed** (free) — composite + 7 sub-components (owner-approved Pass 53)
6. **CFTC COT** (free) — IN scope per Pass 53 owner approval; weekly futures-only + disaggregated + financial futures + combined
7. **SEC EDGAR** (free, DEC-484/456) — structured data only via `edgartools`: 10-K/10-Q financials + Form 4 + 13F + 8-K events
8. **yfinance** — DEPRECATED from runtime; one-time setup OK for sector backfill of tickers Polygon doesn't cover (per Pass 53 owner Q1 approval)

**Folder structure:** `data_prefetch/<api_name>/<endpoint>/...` — Parquet for OHLCV+news+nested per DEC-491 exception; CSV for universe lists + flat row data per DEC-499 18-classifier sector normalization.

**Status legend:**
- `PRIMARY` — canonical source post-Sprint-4
- `FALLBACK` — used only if primary unavailable
- `DEPRECATED` — scheduled for removal per Sprint 4 cleanup
- `PREFETCH-ONLY` — no live calls in backtest; populated by `scripts/prefetch_*.py`
- `MANUAL` — static file or scheduled refresh script (no live API in run loop)
- `PLANNED` — not yet implemented; sub-decision approved
- `DISPLAY-ONLY` — site card / dashboard use only; does NOT affect tier or pass/fail

| Domain | Source | Endpoint / mechanism | PIT lag | Auth | Status | DECs |
|---|---|---|---|---|---|---|
| OHLCV daily | Polygon Stocks Starter | `https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{from}/{to}` | None | API key | PRIMARY | DEC-441/478/479 |
| OHLCV daily (legacy) | yfinance | `Ticker(symbol).history(period=...)` | None | None | FALLBACK | DEC-442 (demoted) |
| OHLCV intraday | Polygon Stocks Starter | `/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/...` | None | API key | PRIMARY | DEC-446 |
| Earnings (PIT) | Polygon Stocks Starter | `/v3/reference/financials?ticker=...` | report_date filing | API key | PRIMARY | DEC-256 |
| Earnings (current) | yfinance | `Ticker.earnings_dates`, `Ticker.earnings` | LIVE-ONLY | None | DEPRECATED for backtest (replaced by Polygon DEC-256) | DEC-443 (BUG-218) |
| Fundamentals (PIT) | Polygon Stocks Starter | `/v3/reference/financials` (income/balance/cashflow) | filing date | API key | PRIMARY (Phase 1B per DEC-484); SEC EDGAR replaces if Polygon insufficient | DEC-257/484 |
| Fundamentals (current) | yfinance | `Ticker.info`, `Ticker.financials`, `.balance_sheet`, `.cashflow` | LIVE-ONLY | None | DEPRECATED for backtest tier/pass-fail; OK for display | DEC-299/443 |
| Analyst consensus | yfinance | `Ticker.info` `recommendationMean` / `targetMeanPrice` / EPS estimates | LIVE-ONLY | None | DISPLAY-ONLY (does NOT affect tier or pass/fail) | DEC-299/443 |
| Analyst recommendations history (PIT) | yfinance | `Ticker.recommendations`, `Ticker.upgrades_downgrades` | None (date-filtered) | None | ACTIVE (PIT-correct via `as_of` filter) | — |
| Analyst revisions | Quiver | `https://api.quiverquant.com/beta/historical/analystestimates/{ticker}` | per-row Date | API key | ACTIVE (paid per DEC-450) | DEC-450 |
| Congressional trades | Quiver | `/beta/historical/congresstrading/{ticker}` | STOCK Act 45-day disclosure | API key | ACTIVE (paid per DEC-450) | DEC-124/324/450 |
| Insider trades | Quiver | `/beta/historical/insidertrading/{ticker}` | filing date | API key | ACTIVE (paid per DEC-450) | DEC-124/125/450 |
| 13F institutional | Quiver | `/beta/historical/institutionalholdings/{ticker}` | quarter_end + 45 days | API key | ACTIVE (paid per DEC-450) | DEC-124/325/450 |
| Government contracts | Quiver prefetch | `cache/quiver/gov_contracts/{ticker}.parquet` (script: `scripts/prefetch_quiver.py`) | per-row Date | n/a (cached) | PREFETCH-ONLY (paid per DEC-450) | DEC-450 / BUG-284 |
| Lobbying | Quiver prefetch | `cache/quiver/lobbying/{ticker}.parquet` | per-row Date | n/a (cached) | PREFETCH-ONLY (paid per DEC-450) | DEC-450 |
| News (per ticker) | Polygon Stocks Starter | `/v2/reference/news?ticker=...` | None | API key | PRIMARY (post-Sprint-4 — replaces AV+Finnhub per DEC-440/454/455) | DEC-440 |
| Macro / FRED | FRED | `https://api.stlouisfed.org/fred/series/observations?series_id=...` | publication date varies | API key | ACTIVE | DEC-407+448 |
| Macro / ALFRED (vintage) | FRED | same base + `realtime_start` / `realtime_end` params | true PIT vintage | API key | ACTIVE (PIT-correct per DEC-301) | DEC-301 |
| AAII sentiment survey | AAII | manual CSV from `aaii.com/sentimentsurvey/sent_results` (committed to repo) | weekly publication; pub-lag 1 day per DEC-389 | none | MANUAL (refreshed via GH Actions per DEC-390) | DEC-389/390 |
| CNN Fear & Greed | CNN | scrape (last-published with `age_days` per DEC-391) | last published | none | ACTIVE | DEC-391 |
| SEC EDGAR — fundamentals | SEC | `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` | 10-K/10-Q filing date | none | PLANNED Sprint 4 (replaces Polygon if insufficient) | DEC-484 |
| SEC EDGAR — Form 4 / 13D/13G | SEC | EDGAR full-text search | filing date | none | PLANNED (OpenInsider mentioned in code docstring but unused) | DEC-125 |
| SEC EDGAR — spinoffs (Form 10-12B) | SEC | EDGAR Form 10-12B query | filing date | none | PLANNED Sprint 5 | DEC-378-380 |
| NASDAQ symbol diff (spinoffs) | NASDAQ | scraped symbol listing | daily | none | PLANNED Sprint 5 | DEC-378 |
| Polygon corporate actions | Polygon Stocks Starter | `/v3/reference/dividends`, `/v3/reference/splits` | event date | API key | ACTIVE | DEC-380 |
| S&P 500 reference (universe Tier 1a) | slickcharts.com | scrape `https://www.slickcharts.com/sp500` (laptop-only) | quarterly refresh | none | MANUAL (laptop-only refresh per `scripts/refresh_sp500_universe.py`; quarterly cadence per CHECKLIST #19) | L88/DEC-477 |
| Russell 1000 reconstitution (Tier 1b) | FTSE Russell | annual reconstitution data | year-grain | none | MANUAL (Tier 1b per DEC-483) | DEC-483 |
| NASDAQ 100 reconstitution (Tier 1c) | Nasdaq | annual reconstitution | year-grain | none | MANUAL (Tier 1c per DEC-483) | DEC-483 |
| BLS CPI schedule | BLS | `https://www.bls.gov/schedule/news_release/cpi.htm` | future-dated calendar | none | ACTIVE (event suppression per DEC-348) | DEC-348 |
| BLS employment schedule | BLS | `https://www.bls.gov/schedule/news_release/empsit.htm` | future-dated calendar | none | ACTIVE | DEC-348 |
| Federal Reserve meetings | Fed | `https://www.federalreserve.gov/json/ne-meetings.json` | future-dated calendar | none | ACTIVE | DEC-348 |
| CFTC Commitments of Traders | CFTC | `https://www.cftc.gov/MarketReports/CommitmentsofTraders/` | weekly publication | none | ACTIVE (macro signal per DEC-407+448) | DEC-407+448 |
| Ortex short interest | Ortex (planned) | TBD | filing date | API key (TBD) | PLANNED Sprint 7 | DEC-468 |

**Cross-references:**
- Cache rules per source: §13.1-13.11 above
- PIT enforcement (DEC-305 RAISE not WARNING): §12.2
- Source priority hierarchy for events: §19.3
- Smart money signal computation using these endpoints: §10.8 / §10.9
- Per-source rate limits + quotas: tracked separately in `API_AUDIT.md`

**Source:** DEC-441/478/479 (Polygon Starter); DEC-442-444 (yfinance demotion); DEC-450 (Quiver paid); DEC-301/407/448 (FRED+ALFRED); DEC-453-455 (deprecation cleanup Sprint 4); DEC-389-391 (sentiment); DEC-348/349 (events); DEC-477/483 (universe); DEC-484 (SEC EDGAR); L88 (no Wikipedia).

---

# PART G — COST MODELING RULES

## 14. Trading Costs

### 14.1 IBKR Tiered Commission (per DEC-252)

**Rule:** IBKR Tiered commission schedule:

| Component | Rate |
|---|---|
| **Per share** | $0.0035 |
| **Minimum per trade** | $0.35 |
| **Maximum per trade** | 1.0% of trade value |
| **Plus** | Exchange fees (varies by venue) |

**Implementation:**
```python
def ibkr_tiered_commission(shares, trade_value):
    raw = shares × 0.0035
    capped = max(0.35, min(raw, 0.01 × trade_value))
    return capped + exchange_fees
```

**Source:** DEC-252

### 14.2 Slippage Model (per DEC-092)

**Rule:** Slippage as function of `(size_pct_ADV, vol)`:

```python
def slippage_bps(size_pct_ADV, vol_252d):
    base = 5  # bps
    size_factor = (size_pct_ADV / 0.01) ** 1.5  # nonlinear
    vol_factor = max(1.0, vol_252d / 0.20)
    return base × size_factor × vol_factor
```

**Source:** DEC-092

### 14.3 Time-of-Day Slippage Multiplier (per DEC-280)

See §8.4 above.

### 14.4 Per-Exit-Method Slippage (per DEC-122)

See §8.3 above.

### 14.5 Slippage Threshold ATR/price > 3% (per DEC-344)

**Rule:** If ATR/price > 3% on entry day, apply **2.0× slippage multiplier** (high-vol regime).

**REVISIT_AFTER_BACKTEST:** 3% threshold tunable empirically.

**Source:** DEC-344

### 14.6 Borrow Cost (per DEC-399)

**Rule:** Single consolidated module: `backtest.engine.costs.calculate_borrow_cost`.

**Why:** BUG-06 + BUG-21 + BUG-327 all involved scattered borrow cost code with double-counting bugs. Sprint 2 consolidates to single source of truth.

**Source:** DEC-399

### 14.7 Routing — TSX vs US (per DEC-253)

**Rule:** Route order to TSX-CAD if interlisted AND order ≤$50K AND ≥100K vol. Else route US-NYSE.

**Why:** TSX has lower commission for small trades and CAD-denominated; cost-optimal for Canadian-resident owner.

**Implementation:**
```python
def route(symbol, value_usd, daily_volume):
    if is_interlisted_tsx(symbol) and value_usd <= 50000 and daily_volume >= 100000:
        return 'TSX-CAD'
    return 'US-NYSE'
```

**Source:** DEC-253

---

## 15. Canadian-Resident Specifics

### 15.1 ETF Substitution Defaults (per DEC-254)

**Rule:** Canadian-resident default ETF substitutions (unhedged):

| US ETF | Canadian Substitute | Hedge Status |
|---|---|---|
| SPY | XUU | Unhedged |
| QQQ | XQQ | Unhedged |
| IWM | XSU | Unhedged |
| VTI | VUN | Unhedged |
| VEA | XEF | Unhedged |
| VWO | XEC | Unhedged |

**Why unhedged default:** Owner accepts FX exposure (DEC-134); hedged versions have higher MERs and tracking error.

**Source:** DEC-254

### 15.2 Norbert's Gambit (Stage 4+ per DEC-255)

**Rule:** USD funding via Norbert's Gambit at funding events only:

**Methodology:**
1. Buy DLR.TO on TSX (CAD)
2. Journal to DLR.U.TO (USD-denominated)
3. Sell DLR.U.TO for USD

**Why:** ~5-10 bps cost vs 150-200 bps on bank FX conversion.

**When:** Funding events only (not per-trade); typically at quarterly portfolio rebalances or capital top-ups.

**Stage:** Stage 4+ live trading.

**Source:** DEC-255

### 15.3 USD/CAD FX Exposure Tracking (per DEC-134)

**Stage 2 portion (Sprint 6, ~1d):** Track FX exposure metric per backtest:
```python
fx_exposure_pct = portfolio_usd_value_cad / total_portfolio_value_cad
```

**Stage 4+ portion (deferred):** Hedge implementation (joint DEC-255 Norbert Gambit).

**Source:** DEC-134

### 15.4 Tax Classification (Stage 4+ per DEC-035 + DEC-270)

**Rule:** Canadian tax classification of trading activity (capital gains vs business income) determined by CPA consultation pre-Stage-4.

**Why critical:** Business-income classification has significantly different tax treatment vs capital gains (50% inclusion). Frequent trading + algorithmic decision-making may trigger business-income classification.

**Stage:** Stage 4 entry prerequisite.

**Source:** DEC-035, DEC-270

---

# PART H — STATISTICAL METHODOLOGY RULES

## 16. Walk-Forward Validation (per DEC-109)

### 16.1 Rolling 5-Year Train / 1-Year Test

**Rule:** Walk-forward validation with rolling 5-year IS (in-sample) train, 1-year OOS (out-of-sample) test.

**Schedule:**
| Train Period | Test Period |
|---|---|
| 2018-01-01 to 2022-12-31 | 2023-01-01 to 2023-12-31 |
| 2019-01-01 to 2023-12-31 | 2024-01-01 to 2024-12-31 |
| 2020-01-01 to 2024-12-31 | 2025-01-01 to 2025-12-31 |
| ... | ... |

### 16.2 Cache Extends to 2018-01-01 (per DEC-109 Option B) — REVISED per DEC-583 Pass 53 owner-approved 2026-05-06

**Pass 53 BUG FIX:** Polygon Stocks Starter prefetch starts ~May 2021 (5y rolling cap per DEC-505). yfinance deprecated per DEC-497 NO-LIVE-API HARD CUT. Prior spec said "Cache extends to 2018-01-01 (DEC-109 Option B)" but **2018-2021 OHLCV source was undocumented**. Walk-forward as previously specified is impossible.

**DEC-583 RESOLUTION (Option A — RECOMMENDED + DEFAULT):** Truncate walk-forward train window to **Polygon-prefetched data only (2021-05 → 2026-05).** Walk-forward schedule revised:
- Train: 2021-05 → 2025-04 (~4y)
- OOS Test: 2025-05 → 2026-05 (1y; current rolling)
- Hold-out: 2026-06+ (forward, never-tuned)

**Trade-off accepted:** Less train data than original 5-year baseline (4y vs 5y). Mitigation: DEC-505 4-fold walk-forward gives multiple test estimates.

**Alternative considered (Option B, REJECTED):** One-time Polygon paid backfill to 2018 (~$200-500 estimated; still requires Polygon API). Rejected — 4y vs 5y train is acceptable; no need for paid backfill.

**Affected:** §16.1 schedule + DEC-505 4-fold walk-forward + all Phase 1A acceptance gates referencing pre-2021 OHLCV.

**Rule:** Cache start date 2018-01-01 (not 2020-01-01 default).

**Why:** Provides 2 OOS folds (2023, 2024) — academically defensible.

**Implementation gate:** DEC-411 (Phase A 2018 cache extension) waits for DEC-298 implementation.

### 16.3 4-5 OOS Folds 2018-2025

**Result:** 4-5 walk-forward OOS folds available with 2018 baseline.

### 16.4 Hold-Out Final Test Period (per DEC-152)

**Rule:** Reserve final 1 year as **never-tuned hold-out** for ultimate validation.

**Source:** DEC-152

### 16.5 Stage 3+ Extension Decisions

- **DEC-266 DEFERRED_TO_STAGE_3:** Extend to 2010 for crisis coverage (joint DEC-298 PIT cache rebuild gate)
- **DEC-158 DEFERRED_TO_STAGE_3:** Extend to 2008-2024 for full 2008 GFC coverage

---

## 17. Performance Metrics

### 17.1 Sharpe Ratio (per DEC-081 Phase A canonicalization)

**Rule:** Single canonical Sharpe formula:
```
sharpe_annualized = (mean_daily_return - rf_daily) / std_daily_return × sqrt(252)
```

**Risk-free rate (rf):** Use FEDFUNDS rate (per DEC-081).

**Source:** DEC-081

### 17.2 Sortino Ratio (per DEC-081 Phase B)

**Rule:** Sortino uses downside deviation only:
```
sortino_annualized = (mean_daily_return - rf_daily) / std_negative_daily_return × sqrt(252)
```

**Source:** DEC-081

### 17.3 Deflated Sharpe / PSR (per DEC-110)

**Rule:** PSR (Probabilistic Sharpe Ratio) from López de Prado:
```
PSR(SR_target) = Φ((SR_observed - SR_target) × sqrt((n - 1) / (1 - γ3 × SR_observed + ((γ4 - 1) / 4) × SR_observed^2)))
```

Where:
- `γ3` = skewness of returns
- `γ4` = kurtosis of returns
- `n` = number of observations

**Used in §3.3 Gate 3 (PSR ≥ 0.95).**

**Source:** DEC-110

### 17.4 Sample Size Requirements (per DEC-083 TIERED)

**Rule:** Minimum trades per tier for Sharpe stability:

| Tier | Min trades |
|---|---|
| HIGH | 100+ trades |
| MEDIUM | 50-100 trades |
| LOW | 30-50 trades |

**Source:** DEC-083

### 17.5 Stationarity Tests (per DEC-111)

**Tests applied to strategy returns:**
1. **ADF (Augmented Dickey-Fuller):** Rejects non-stationarity hypothesis (p < 0.05)
2. **Rolling Sharpe:** 6-month rolling Sharpe stability
3. **Chow test:** Structural break detection

**Source:** DEC-111

### 17.6 Distribution Analysis (per DEC-242)

**Metrics computed:**
- Skewness (γ3)
- Kurtosis (γ4)
- Maximum single-trade gain/loss
- Distribution histogram
- Q-Q plot vs normal

**Source:** DEC-242

### 17.7 vs-SPY Comparison (per DEC-155)

**Rule:** All backtest reports include vs-SPY metrics:
- **Alpha:** Strategy return - SPY return
- **Information Ratio:** Alpha / std(strategy_return - SPY_return)
- **Tracking Error:** std(strategy_return - SPY_return)

**Source:** DEC-155

### 17.8 Net Sharpe Contribution (per DEC-210)

**Rule:** Agent value-add measured as `net_sharpe = gross_lift - annualized_agent_cost`.

**Where:**
- `gross_lift` = Sharpe(full-agents) - Sharpe(rules-only)
- `annualized_agent_cost` = total agent API cost per year / portfolio value

**Source:** DEC-210

---

## 18. A/B Testing Framework (per DEC-205-216)

### 18.1 4-Arm Design

| Arm | Description |
|---|---|
| **rules-only** | No agent gate; pure rules-based decisions |
| **full-agents** | Default AgentGateConfig (§7) |
| **no-Risk** | Risk gate disabled |
| **no-Bull-Bear** | Bull/Bear alignment requirement disabled |

**Plus:** Continuous-Risk arm per DEC-459 (carrying DEC-042 turn 121 directive #3 forward) — 5th arm — total 5 arms.

**Source:** DEC-205-206

### 18.2 Paired Design

**Rule:** Every trade evaluated by every arm; same input data, different gating logic.

**Why:** Isolates agent-gate effect from market timing; reduces variance vs unpaired.

**Source:** DEC-205

### 18.3 Pre-Commit Minimum Sample (per DEC-207)

**Rule:** Minimum **300 paired trades** before A/B verdict committed.

**Why:** Below 300 trades, Sharpe estimates have high variance; verdicts unreliable.

**Source:** DEC-207

### 18.4 Multi-Metric Comparison (per DEC-208)

**Metrics compared per arm:**
- Sharpe ratio
- Sortino ratio
- Maximum drawdown
- Win rate
- Profit factor (PF)
- Conditional Value-at-Risk (CVaR)
- Cost (commissions + slippage + agent API costs)

**Source:** DEC-208

### 18.5 Per-Regime Verdicts (per DEC-209)

**Rule:** A/B verdicts computed **per regime** (not just overall).

**Why:** Agents may add value in some regimes (e.g., high-volatility) but not others.

**Output:** Per-regime A/B verdict matrix.

**Source:** DEC-209

### 18.6 Net Sharpe Contribution (per DEC-210)

See §17.8 above.

### 18.7 Agent Value-Add Gate (per DEC-131 — Two-Gate Refinement)

**Rule:** Agent value-add requires BOTH gates:
1. **Net Sharpe gate:** `net_sharpe(full-agents) - net_sharpe(rules-only) ≥ 0.2`
2. **Relative gate:** `(net_sharpe(full-agents) - net_sharpe(rules-only)) / abs(net_sharpe(rules-only)) ≥ 10%`

**Why two gates:** Absolute 0.2 alone could clear when rules-only is mediocre (e.g., 0.5→0.7 is +0.2 but only 40% of rules); relative gate ensures meaningful improvement.

**Source:** DEC-131 (Pass 52 turn 67 owner-approved)

### 18.8 Per-Agent Ablation (per DEC-211)

**Rule:** Drop each agent one at a time; measure Sharpe delta vs full-agents.

**Scope:** **Option A NARROW SCOPE** — sample-bounded top-20% strategies × ~5K trades per ablation arm. Cost ~$120 vs $13,800 naive full ablation.

**When:** Post-Phase-1B-α.

**Source:** DEC-211

### 18.9 Three-Case Pairing (per DEC-420)

**Rule:** A/B framework supports three pairing cases:
- **Case 1:** Same trade fired by all arms (trivial — direct comparison)
- **Case 2:** Trade fired by some arms but not others (gating differential)
- **Case 3:** Trade fired by no arms (informational — both gates worked)

**Source:** DEC-420 (joint DEC-131 implementation)

---

# PART I — EVENT HANDLING RULES

## 19. Event-Calendar Suppression (per DEC-348)

### 19.1 Trigger Events

| Event Type | Source |
|---|---|
| **FOMC meeting** | FRED FOMC calendar |
| **Earnings announcement** | Polygon earnings endpoint |
| **CPI release** | FRED CPI calendar |
| **GDP release** | FRED GDP calendar (lower priority) |

**Source:** DEC-256, DEC-348, DEC-407+448

### 19.2 Suppression Window (asymmetric per DEC-349)

**Rule:** Suppression window asymmetric: **pre=1 day, post=3 days**.

**Why asymmetric:**
- Pre-event: Some signals are valid right up to event (limited blackout)
- Post-event: Volatility persists 2-3 days post-announcement; entries unreliable

**REVISIT_AFTER_BACKTEST:** Window sizes (1/3) tunable empirically.

**Source:** DEC-349

### 19.3 Event Source Priority (per DEC-348 + DEC-407+448)

**Priority:**
1. Polygon earnings (Stocks Starter $29/mo subscription provides this)
2. FRED FOMC + CPI calendars
3. yfinance earnings_dates (deprecating per DEC-013/444)

**Source:** DEC-348, DEC-407+448

---

## 20. Corporate Actions (per DEC-146)

### 20.1 Splits (per DEC-146)

**Rule:** Price-series adjustment using corp_actions table; cache stores raw + adjustments computed at query time per as_of (DEC-298).

### 20.2 Dividends (per DEC-146)

**Rule:** Track ex-dates; total return calculation includes dividends; price-only return excludes.

### 20.3 Spinoffs (per DEC-378-380)

**Rule:** SEC EDGAR Form 10-12B scrape for spinoff feed; auto-add spinoff ticker to Tier 2 universe.

**Sources:** DEC-378 (universe inclusion), DEC-379 (SEC EDGAR scrape), DEC-380 (Polygon corp actions integration)

### 20.4 Renames (per DEC-234)

**Rule:** CUSIP/ISIN persistence — same security tracked across ticker renames (e.g., FB → META).

**Source:** DEC-234

### 20.5 Delistings (per DEC-147)

**Rule:** Delisted tickers preserved in universe at historical dates pre-delisting.

**Why:** Backtest universe at any historical date includes tickers active then but later delisted (avoid survivorship bias).

**Joint:** DEC-303 Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv + DEC-052 CC0 dataset.

**Test signal:** Lehman Brothers 2008 backtest has LEH ticker available pre-delisting; absence post-Sep 2008.

**Source:** DEC-147

---

# PART J — PHASE 1B-α DIMENSIONAL CUBE

## 21. Cube Dimensions (17+ per DEC-422)

### 21.1 Core Dimensions

1. **Strategy** (199 strategy classes (per F-002 post Pass 53 expansion: Layer 1 110 + Layer 2A 12 + 2B 4 + 2C 5 + Layer 3A 20 + 3B 21 + Layer 6 27) classes)
2. **Regime** (Bull/Bull-Pause/Neutral/Bear-Pause/Bear/Crisis — 6 levels)
3. **Sector** (11 GICS sectors)
4. **Market cap band** (mega/large/mid/small)
5. **Volatility band** (low/medium/high realized vol)
6. **Momentum band** (low/mid/high momentum percentile)
7. **Liquidity band** (low/medium/high ADV)
8. **Time period** (per OOS fold — 2023, 2024, 2025)

### 21.2 Additional Dimensions

9. **Trigger type** (catalyst/technical/stat-arb per DEC-174)
10. **Exit method** (20 exit methods per §8 post-DEC-517 R-multiple additions; was 17 pre-Pass-53)
11. **Position size tier** (HIGH/MED/LOW)
12. **Day of week** (Mon/Tue/Wed/Thu/Fri)
13. **Time of day** (open/mid/close)
14. **Earnings proximity** (pre-1d / post-3d / clear)
15. **FOMC proximity** (pre-1d / post-3d / clear)
16. **CPI proximity** (pre-1d / post-3d / clear)
17. **A/B arm** (rules / full-agents / no-Risk / no-Bull-Bear / continuous-Risk)

**Source:** DEC-422 + DEC-100 (categorical breakdowns) + DEC-144 (cross-tab)

### 21.3 Cube Schema

Output: per-cell row with dimension values + verdict (PASS/FAIL_RR/INSUFFICIENT_SAMPLE) + metrics (Sharpe/DD/n/p/PSR/t/R:R) + cost-adjusted Sharpe + MAE/MFE + skew/kurtosis + ROI.

**Source:** DEC-422 (Pass 52 schema correction with ROI, R:R, profit factor, expectancy, drawdown, MAE/MFE, cost-adjusted Sharpe + FAIL_RR enum + 5-gate filter)

---

## 22. Cube Verdict Framework (per DEC-426)

### 22.1 5-Gate Validity Filter

See §3 above (canonical detail there).

### 22.2 Verdict Classes

| Verdict | Trigger |
|---|---|
| **PASS** | All 5 gates pass |
| **FAIL_RR** | Gate 5 fails (R:R < 2.0) — distinct from generic FAIL |
| **INSUFFICIENT_SAMPLE** | Gate 1 fails (n < 30) |
| **FAIL** (generic) | Any other gate failure |

**Source:** DEC-426

### 22.3 Live Decision Lookup Table (per DEC-429)

**Rule:** Cube produces live decision lookup table consumed by paper/live trading:
```
key: (strategy, regime, sector, market_cap, vol, momentum, liquidity)
value: verdict, position_size_modifier, confidence_tier, expected_R:R, expected_Sharpe
```

**Live trading flow:** Look up cell verdict at trade-decision time; if PASS, enter at tier; else REJECT.

**Source:** DEC-429

---

# PART K — REVISIT_AFTER_BACKTEST TAGS (DEDICATED SECTION)

## 23. Empirical Tuning Items

Per owner directive #8 — dedicated section listing all empirical-tune items in one place. Aggregated from across the canonical document.

### 23.1 List of REVISIT_AFTER_BACKTEST Tagged Items

| # | Item | Default | Section | Decision |
|---|---|---|---|---|
| 1 | **Per-ticker max-loss cap** | -10% rolling 30-day | §6.2 | DEC-135 |
| 2 | **Edge decay percentage** | 20% Sharpe haircut | §4.2 | DEC-250 |
| 3 | **PM confidence threshold** | 0.5 (entry pre-Risk-veto) | §7.3 | DEC-459 (supersedes DEC-042) |
| 4 | **Tier thresholds (PM confidence)** | 0.5 / 0.65 / 0.8 | §7.5 | DEC-459 (supersedes DEC-042) |
| 5 | **Risk veto threshold** | 0.5 (binary current default) | §7.2 | DEC-459 (supersedes DEC-042) |
| 6 | **Continuous-Risk vs binary-veto** | Binary veto current default | §7.2 | DEC-459 (carries DEC-042 turn 121 directive #3) |
| 6a | **Research Manager alignment check on/off** | On default; A/B arm tests off | §7.4 | DEC-459 |
| 7 | **Slippage threshold ATR/price** | 3% (triggers 2.0× multiplier) | §14.5 | DEC-344 |
| 8 | **Event window pre/post** | pre=1, post=3 days | §19.2 | DEC-349 |
| 9 | **Regime candidate cap (Bull)** | 20 candidates/day | §11.3 | DEC-262 |
| 10 | **Regime candidate cap (Neutral)** | 15 candidates/day | §11.3 | DEC-262 |
| 11 | **Regime candidate cap (Bear/Crisis)** | 10 candidates/day | §11.3 | DEC-262 |
| 12 | **Portfolio vol target** | 15% annualized | §5.5 | DEC-088 |
| 13 | **Per-position vol target** | 1% per day | §5.4 | DEC-087 |
| 14 | **Fractional Kelly fraction** | 0.25 (quarter-Kelly) | §5.3 | DEC-086 |
| 15 | **Smart money decay half-life** | 90 days | §8.2 (PROJECT_PLAN) | DEC-123 |
| 16 | **Bonferroni correction factor** | Current strategy count (~72-119) | §3.2 | DEC-080+400 |
| 17 | **EMA smoothing alpha** | α = 0.1 (~10-day half-life) | §10.3 | DEC-108 |
| 18 | **Cache freshness OHLCV** | 1 day | §13.10 | DEC-260 |
| 19 | **Cache freshness FRED** | 7 days | §13.10 | DEC-260 |
| 20 | **Cache freshness 13F** | 90 days | §13.10 | DEC-260 |
| 21 | **Cache size monitoring threshold** | 80% disk | §13.4 | DEC-227 |
| 22 | **Filelock timeout** | 5 seconds | §13.5 | DEC-328 |
| 23 | **Stop-out cooldown** | 5 trading days | §6.1 | DEC-018 |
| 24 | **Strategy decay flag threshold** | >50% Sharpe drop | §4.1 | DEC-249 |
| 25 | **Rolling Sharpe window** | 6 months | §4.1 + §17.5 | DEC-249, DEC-111 |
| 26 | **Memory cap** | 4 GB | §2.5 (this doc) | DEC-179 |
| 27 | **Cold-start CI target** | <30 minutes | §2.5 | DEC-138 |
| 28 | **Test coverage target** | 90% | §21.2 (PROJECT_PLAN) | DEC-098 |

### 23.2 Tuning Methodology

**For each REVISIT_AFTER_BACKTEST item:**

1. **Pre-tuning state (current):** Documented above with default value
2. **Tuning trigger:** Phase 1B-α run complete; empirical evidence available
3. **Tuning approach:**
   - Sweep parameter across reasonable range
   - Measure metric impact (Sharpe / max DD / win rate)
   - Select parameter value optimizing primary metric (typically Sharpe)
   - Validate on held-out OOS fold (per DEC-152 hold-out)
4. **Approval:** Owner reviews tuning results; explicit approval before parameter change
5. **Documentation:** Update this section §23 with tuned value + rationale + date

### 23.3 Tuning Cadence

**Phase 1B-α (initial tuning):** Tune all items post-empirical-evidence; baseline values updated based on Phase 1B-α outputs. **GOVERNED BY DEC-581 endogeneity-loop protection (§23.4 below).**

**Quarterly re-tune (Stage 3+):** Per DEC-214 quarterly re-validation, REVISIT_AFTER_BACKTEST items re-evaluated; demote/retire strategies showing decay (DEC-249).

**Stage 4+ ongoing:** Live trading data feeds into tuning loop; quarterly cadence continues.

### 23.4 DEC-581 — Tuning methodology + endogeneity-loop protection (Pass 53 owner-approved 2026-05-06 Q4)

**Trigger:** External-AI adversarial review identified the deepest critique — 28 REVISIT_AFTER_BACKTEST items + 11 P2/P3 backlog + multiple PROPOSED-not-RESOLVED references create an **endogeneity loop**: post-backtest decisions are conditioned on backtest results which were conditioned on different decisions. Tuning Bonferroni factor (§23.1 #16) affects strategy selection; strategy selection affects walk-forward results; walk-forward results condition Bonferroni tuning. Without protection, tuning becomes circular noise-mining.

**Resolution:** Two-class reclassification + hold-out fold protection + multi-test correction at tuning level + audit trail.

#### Class A vs Class B endogeneity classification

Every REVISIT item is classified:

- **Class A (no strategy-selection feedback):** Tuning the parameter does NOT change which strategies pass Phase 1B-α gates. Examples: cache freshness, filelock timeout, memory cap. Safe to tune on full backtest data.
- **Class B (strategy-selection feedback):** Tuning the parameter DOES change which strategies pass. Examples: Bonferroni factor, R:R floor, smart money composite weights, decay half-life. Requires hold-out fold + single-shot tuning.

**Reclassification table (28 REVISIT items + new):**

| # | Item | Class | Hold-out required |
|---|---|---|---|
| 1 | Per-ticker max-loss cap (-10%) | A | No (operational threshold; doesn't gate) |
| 2 | Edge decay percentage (20%) | A | No |
| 3 | PM confidence threshold (0.5) | **B** | YES — gates strategy promotion to live |
| 4 | Tier thresholds (0.5/0.65/0.8) | **B** | YES — affects which trades execute |
| 5 | Risk veto threshold (0.5) | **B** | YES |
| 6 | Continuous-Risk vs binary-veto | **B** | YES — fundamental architecture choice |
| 6a | RM alignment check on/off | **B** | YES — A/B verdict directly |
| 7 | Slippage threshold ATR/price (3%) | A | No (cost model adjustment; doesn't reorder strategies materially) |
| 8 | Event window pre/post (1/3) | A | No |
| 9-11 | Regime candidate caps (20/15/10) | **B** | YES — affects which trades execute |
| 12 | Portfolio vol target (15%) | A | No (sizing scalar) |
| 13 | Per-position vol target (1%) | A | No |
| 14 | Fractional Kelly (0.25) | A | No |
| 15 | Smart money decay half-life (90d) | **B** | YES — composite drives strategy fires |
| 16 | Bonferroni correction factor | **B** | YES — directly affects gate-passing |
| 17 | EMA smoothing alpha (0.1) | **B** | YES — regime classifier output drives Layer 5 eligibility |
| 18-20 | Cache freshness | A | No |
| 21 | Cache size monitoring threshold | A | No |
| 22 | Filelock timeout | A | No |
| 23 | Stop-out cooldown (5d) | A | No (operational; doesn't gate selection) |
| 24 | Strategy decay flag threshold (>50%) | **B** | YES — drives retirement |
| 25 | Rolling Sharpe window (6mo) | A | No |
| 26 | Memory cap (4 GB) | A | No |
| 27 | Cold-start CI target | A | No |
| 28 | Test coverage target | A | No |
| 29 (NEW) | F-009 7th gate threshold (5bps DEC-578) | **B** | YES |
| 30 (NEW) | DSR threshold (0.95 DEC-510) | **B** | YES |
| 31 (NEW) | Asymmetric EMA alpha values (DEC-544) | **B** | YES |
| 32 (NEW) | Schmitt-trigger thresholds (0.6/0.4 DEC-546) | **B** | YES |
| 33 (NEW) | Smart money composite weights (+4/+2/-3) | **B** | YES |
| 34 (NEW) | Sentiment thresholds (CNN F&G 20/35/65/80) | **B** | YES |

**Class B count: 14 of 34 = ~41% of REVISIT items affect strategy selection.**

#### Hold-out fold protection

**Total available hold-out folds: 3** (per DEC-152 hold-out methodology).

**Allocation rule:**
- **Fold 1:** Top-level Sharpe / R:R / win-rate gate validation (cross-strategy)
- **Fold 2:** Class B parameter tuning (single-shot; consumes one fold per Class B parameter group)
- **Fold 3:** Final pre-promotion validation (never tuned; final out-of-sample test before Stage 3)

**Constraint:** With 14 Class B parameters and 1 hold-out fold for tuning, **must group Class B parameters into ≤14 single-shot groups** OR defer some to post-Phase-1B-α (using Stage 3 paper trading data as hold-out for the deferred set).

**Recommended grouping (12 single-shot tuning experiments):**
1. PM confidence threshold + tier thresholds + Risk veto threshold (3 → 1 joint experiment; agent-gate cluster)
2. Continuous-Risk vs binary-veto + RM alignment on/off (2 → 1 A/B test)
3. Regime candidate caps (3 → 1 joint experiment)
4. Smart money decay half-life + composite weights (2 → 1 joint experiment)
5. Bonferroni factor (alone; depends on strategy count)
6. EMA smoothing + Schmitt thresholds + asymmetric alpha (4 → 1 regime-classifier experiment)
7. Strategy decay threshold (alone; quarterly cadence)
8. F-009 7th gate threshold (alone; cost-model-dependent)
9. DSR threshold (alone; statistical methodology)
10. Sentiment thresholds (CNN F&G 4 levels → 1 joint experiment)
11. Reserved (deferred to Stage 3 paper if needed)
12. Reserved

**14 → 10 grouped experiments fits in 1 hold-out fold without contamination.**

#### Multi-comparison correction at tuning level

**Tuning-experiment Bonferroni:** With 10 grouped tuning experiments + 28 REVISIT items + 11 backlog ≈ 40-50 tuning trials, naive α/N → α/50 ≈ 0.001 → t-stat ~3.3 effect-size required.

**Effect-size floor (alongside statistical):**
- **Sharpe move ≥ 0.05 absolute** to count as a valid tuning improvement (1× standard error of Sharpe estimate at n=250 daily returns)
- Tuning moves below 0.05 Sharpe rejected as noise; baseline retained

**Iteration cap per parameter sweep:** Max 20 iterations (e.g., 20 candidate values for a continuous threshold). Prevents fine-grained p-hacking.

#### Joint vs marginal tuning rule

**Default: marginal** (one parameter at a time; preserves interpretability).

**Joint allowed only if:**
- Parameters interact via documented dependency (e.g., asymmetric EMA fast-in / slow-out alphas affect each other through transition matrix)
- Joint tuning has Bonferroni correction across joint dimension (α/n_combinations)
- Effect-size floor still applies post-correction

**Recommended grouping (above) uses joint tuning only where interaction is documented.**

#### Tuning audit trail

Every Class B tuning experiment produces:
```
tuning_audit/<item_id>_<date>.json
{
  "item_id": "DEC-080-Bonferroni-factor",
  "class": "B",
  "tuner": "owner / Claude / joint",
  "tune_date": "2026-XX-XX",
  "data_used": "walk-forward fold 2018-2024 in-sample + 2025 hold-out fold 2",
  "alternatives_tried": [N=10, N=72, N=199, N=199*17],
  "selected_value": "N=199",
  "selected_rationale": "DEC-582 cross-strategy multi-testing; cube-cells via FDR DEC-470",
  "effect_size_sharpe_delta": 0.08,
  "effect_size_pass": true (≥0.05 floor),
  "hold_out_fold_consumed": 2,
  "stat_significance_p": 0.012 (post-Bonferroni-tuning correction),
  "owner_approved": true,
  "approval_date": "2026-XX-XX"
}
```

Audit trail prevents post-hoc rationalization + enables reproducibility.

#### Endogeneity-cycle prevention

**Sequence rule:** Class B parameters tuned ONCE per Phase 1B-α run; results frozen. **No iterative re-tuning** within a single run.

**Iterative re-tuning across phase boundaries:** Allowed at quarterly re-validation (DEC-214) cadence ONLY. Each re-tune consumes a fresh data window (next quarter's trades).

**Post-tune strategy selection re-run:** Required ONLY if a Class B parameter materially shifts (Sharpe Δ ≥0.05). Otherwise prior selection holds. Prevents loop where each tune triggers full re-selection.

#### Implementation

- `backtest/engine/tuning_methodology.py` (NEW) — implements Class A/B classification + hold-out allocation + tuning audit trail
- `tuning_audit/` directory (NEW) — JSON file per Class B tuning experiment
- DEC-470 PROPOSED hierarchical FDR + this DEC-581 — joint statistical-correctness layer for Phase 1B-α verdict

**Effort:** ~2-3 days spec-implementation + ongoing per-tuning effort.

**Source:** DEC-581 (Pass 53 Q4 owner-approved 2026-05-06 — adversarial review codification of deepest critique)

---

### 23.4 Tuning Result Documentation Format

When tuning completes, document inline:

```
**Item N (Default):**  X (pre-Phase-1B-α)
**Item N (Tuned, post-Phase-1B-α):** Y
**Tuning rationale:** [empirical evidence summary]
**Owner approved:** Pass NN turn MM
**Re-tune cadence:** Quarterly per DEC-214
```

### 23.5 Cross-Reference Convention

Each item in §23.1 has:
- **Location in this document** (§ reference)
- **Source decision** (DEC-NNN)
- **Default value** (current pre-tune)

When tuned, ENGINEERING_REGISTER and AUDIT.md narrative entries cross-reference §23 of this document for canonical updated values.

---

### 23.6 Audit-Iteration Ceiling (DEC-589 — Pass 53 owner-approved 2026-05-06)

**Decision:** Pass 53 review-cycle CLOSED after 7 external-AI adversarial reviews + ~155 findings + ~80 DECs codified. No additional audit cycles permitted before Phase 1A implementation begins.

**Rationale (per Pass 53 owner Q2 = A approval):**

7 review-takes have been completed across Pass 53:
1. Strategy roster (Layer 1.I + Layer 6 expansion to 199 strategies — planned target; live 186 Pass 53)
2. Signal universe (Category 7 universe-level signals; ~270-280 → ~315-325 fields)
3. Exit-risk methodology (DEC-517-538 + 17 exit methods — planned target; live 25 Pass 53)
4. Regime methodology (DEC-539-565 4-regime collapse + training/labeling protocol)
5. Adversarial TRADING_RULES (DEC-566-580 cross-section + 7-gate Phase 1B-α verdict promotion)
6. Adversarial Q4 endogeneity (DEC-581 5-component endogeneity-loop protection)
7. Adversarial DETAILED_PROJECT_PLAN (CC-1 through CC-7 strategic risks; 10 P0 doc-drift bugs)

Marginal utility of additional review cycles approached zero. Adversarial reviews 5-7 began surfacing audit-process risks (CC-2 audit-cycle non-convergence; CC-3 decision-to-code ratio of ∞:0). Continued auditing without implementation creates structural risk per CC-4 planning-paralysis pattern.

**Boundary conditions (when ceiling can be relaxed):**

The audit-iteration ceiling is suspended ONLY when one of these triggers fires:
1. **Phase 1A empirical findings invalidate codified DEC** — if running code produces results that contradict a codified DEC's claimed effect, that specific DEC re-opens for revision (not the broader audit cycle).
2. **Phase 1B-α 7-gate Phase 1B-α verdict produces zero PASS cells** — Stage 2 has failed and the entire methodology stack re-opens per Part 13.3.
3. **Live data source breaks** — if a Sprint 0A prefetched data source (Polygon/Quiver/FRED/AAII/CNN F&G/CFTC/SEC EDGAR/Apewisdom/pytrends) becomes unavailable or schema changes, that specific data DEC re-opens.
4. **Owner explicit directive** — owner can re-open audit at any time. The ceiling is operational discipline, not a contract.

**What this rule blocks:**

- ❌ "8th external-AI review of [doc X]" — explicitly disallowed before Phase 1A implementation begins.
- ❌ "Re-audit [DEC-N] for completeness" — disallowed unless DEC actually fails empirical test.
- ❌ "Pass 54 audit-only sprint" — disallowed; Pass 54 must contain code execution.
- ❌ "Revisit [methodology Y] one more time" — disallowed unless boundary-condition trigger fires.

**What this rule does NOT block:**

- ✅ Inline P0 doc-drift fixes during implementation (e.g., R7-01 through R7-10 applied 2026-05-06)
- ✅ DEC drafting that arises from running-code findings
- ✅ Owner-directed scope expansions
- ✅ Pre-flight CHECKLIST verification before each recommendation (CHECKLIST #45 + Pass 52 mandate)

**Cross-references:**
- AUDIT.md Pass 53 review-cycle FINAL narrative (closure entry)
- AUDIT_BACKLOG.md (master registry of ~155 findings + ~80 DECs)
- AUDIT_INDEX.md DEC-589 entry
- DEC-590 (§23.7 below — Phase 1A implementation begin date 2026-05-15)

**Status:** RESOLVED-DECIDED Pass 53 owner Q2 approval 2026-05-06.

---

### 23.7 Implementation Begin Date (DEC-590 — Pass 53 owner-approved 2026-05-06)

**Decision:** Phase 1A implementation begins **2026-05-15** (9 days from Pass 53 review-cycle closure 2026-05-06). No further auditing permitted in the 9-day pre-implementation window EXCEPT inline P0 doc-drift fixes that arise from current-pass cleanup.

**Rationale (per Pass 53 owner Q3 = A approval):**

Owner-approved date provides:
- 9 days for codebase setup, alignment-test convergence, and `data_prefetch/` cache validation
- Time-box on document reconciliation (DEC-588 propagates Pass 53 decisions across TRADING_RULES sections)
- Hard deadline preventing audit-iteration drift (CC-2 risk mitigation)
- Owner calendar alignment (start of work week post-2026-05-15)

**Pre-implementation 9-day window allowed work (2026-05-06 to 2026-05-14):**

| Day | Allowed work | Disallowed work |
|---|---|---|
| 1-2 (May 6-7) | P0 doc-drift fixes (R7-01 through R7-10) + DEC-589/DEC-590 codification + AUDIT.md narrative + AUDIT_INDEX.md updates + alignment tests | New external-AI reviews; new audit cycles |
| 3-5 (May 8-10) | Sprint 0A pytrends bg restart cycles + Polygon news/indicators/financials/events/NBBO prefetch extension + 16 BATCH 14 smoke/demo test convergence | New methodology debates |
| 6-7 (May 11-12) | DEC-588 doc-reconciliation pass (~3-5 days propagating DEC-509-565 across TRADING_RULES sections) + universe-build validation (614+161+27+347+1923 = 2872 rows / 1937 unique) | Strategy roster expansion (locked at 199 per F-002) |
| 8-9 (May 13-14) | Phase 1A v3 archive 67-instrument-equivalent subset re-run prep + DEC-507 wiring matrix verification (5 toolkits × N agents × M data sources × verified status) + DEC-508 Tier 1-4 testing matrix prep | Last-minute scope additions |
| 10 (May 15) | **Phase 1A implementation BEGINS** — owner-gated start | — |

**Phase 1A scope at start (May 15):**

Per CANONICAL_FACTS F-001 + DETAILED_PROJECT_PLAN.md §3.6-3.10 + DEC-505 4-fold walk-forward:

1. Sprint 1A-α — Rules-only baseline cube (no agents) — `--no-agents` flag, 4 OOS folds, full universe, all 199 strategies (planned target; live 186 Pass 53)
2. Owner gate at 1A-α — rules-only Sharpe ≥ 0.7 OOS before $300 1B-α budget commits
3. Sprint 1A-β — Full-scale dry-run on 1937-unique-ticker universe with `--no-agents --dry-run`
4. Owner gate at 1A-β — pipeline integrity verified before Phase 1B-α agent overlay

**Slippage tolerance:** ±2 business days only. If implementation cannot start by 2026-05-19, owner reviews root cause + reapproves new date.

**Cross-references:**
- DEC-589 (§23.6 above — audit-iteration ceiling)
- AUDIT_BACKLOG.md implementation roadmap Week 1-5+
- DETAILED_PROJECT_PLAN.md §3.6-3.10 (Phase 1A sub-phase definitions)
- DEC-505 (4-fold walk-forward replacing 6-fold per Pass 53 R7-06)
- DEC-507 (Agent toolkit wiring matrix HARD RULE)
- DEC-508 + CHECKLIST #71 (4-tier external library fork integration mandate)

**Status:** RESOLVED-DECIDED Pass 53 owner Q3 approval 2026-05-06.

---

### 23.8 Data-Integrity Test Layer Mandatory (DEC-591 — Pass 53 owner-approved 2026-05-06 evening)

**Decision:** Data-integrity test layer (DEC-503 test type #7 — "schema validation, PIT semantics, completeness gates") is mandatory before Phase 1A start. PASS-gate codified as CHECKLIST #72 (HARD RULE).

**Rationale (per L148):** Pass 53 prefetch audit 2026-05-06 surfaced 5 of 5 CRITICAL findings + 7 HIGH findings, all of which existed in cache for weeks/months without detection. DEC-503 specified 9 test types but only code-test layers (1-6) were implemented; data-integrity layer (7) was specified-but-not-built. Same silent-gap pattern as L145/L146/L147 but on the VERIFICATION axis (test layer specified but never built).

**Test suite scope (`backtest/tests/test_data_integrity.py`):**

7 tests scanning the live cache (not mocked fixtures), each mapping to a pyramid-gap pattern:

| Test | Asserts | Catches |
|---|---|---|
| 1 | All OHLCV files share single schema | C1 schema split |
| 2 | All OHLCV last_bar ≥ as_of − 7 days OR ticker-delisted | C2 stale files |
| 3 | Required tickers present (VIX/VIXCLS, SPY, sector ETFs XLB-XLY+XLC) | C3 + M6 |
| 4 | Numeric columns have numeric dtype (CFTC, FRED, financials) | C4 |
| 5 | TIER_PARAMS dict populated for T1a/T1c/T1ETF/T2/T3 with all 5 keys | C5 |
| 6 | Cross-source ticker coverage ≥75% of universe (per source) | H5 Quiver legacy |
| 7 | Cumulative-snapshot sources have multi-day history (Apewisdom, AAII, CNN F&G, etc.) | H3 Apewisdom |

**Gate behavior:**

- Test suite runs as part of `pytest backtest/tests/` standard regression
- Failed test BLOCKS phase entry, BLOCKS DEC RESOLVED-IMPLEMENTED marking, BLOCKS commit-with-skip-tests
- Suite extends as new data sources added (one new test per source per gap pattern)

**CHECKLIST #72 (NEW HARD RULE Pass 53 2026-05-06 evening):**

> Data-integrity test scan of cache MUST run + pass before any DEC marks RESOLVED-IMPLEMENTED OR before any phase entry. The 7-test minimum scan is mandatory; new data sources extend the suite. No code push that touches prefetched data is compliant without running this suite.

**Implementation:** ~1d engineering within Day 1-2 of DEC-590 9-day window.

**Cross-references:**
- L148 (parent lesson — test pyramid layered failure mode)
- DEC-503 (test pyramid HARD RULE; data-integrity layer was specified there but unimplemented)
- DEC-590 (9-day window provides time for implementation pre-Phase-1A)
- CHECKLIST #69 (test pyramid before every code push) + #72 (this DEC)
- Pass 53 prefetch audit 2026-05-06 (5 CRITICAL + 7 HIGH findings)

**Status:** RESOLVED-DECIDED Pass 53 owner approval 2026-05-06 ("Approve ALL your recs on the rest").

---

### 23.9 Apewisdom Cumulative Daily Prefetcher (DEC-592 — Pass 53 owner-approved 2026-05-06 evening Q-followup b)

**Decision:** Apewisdom (free WSB/r/stocks ticker-mention sentiment) prefetched via cumulative daily-snapshot architecture, not point-in-time queries. Owner directive 2026-05-06 (Q-followup b = "umulative daily prefetcher") supersedes prior scope-out alternative.

**Problem:** Apewisdom API returns top trending tickers for the CURRENT day only — no historical query. Pass 53 prior prefetch only persisted 1 day (2026-05-05; 1110 rows in `data_prefetch/apewisdom/global.parquet`). Per DEC-502, history needs 2021-present coverage. Single-day cache provides zero historical signal.

**Solution architecture:**

1. **Daily prefetcher** (`scripts/prefetch_apewisdom_daily.py`) runs once per day (GitHub Actions cron `0 9 * * *` UTC; matches AAII Thursday refresh pattern)
2. **Append-only schema:** new daily snapshot APPENDED to `data_prefetch/apewisdom/global.parquet`; never overwrites
3. **Schema:** `[rank, ticker, name, mentions, upvotes, rank_24h_ago, mentions_24h_ago, snapshot_date]` — `snapshot_date` is the partition key
4. **Forward-only history:** 2026-05-05 (current snapshot) onward; no Stage-2 retroactive backfill (Apewisdom doesn't expose historical API)
5. **Stage-2 implication:** Apewisdom signal becomes available DURING Phase 1A run (accumulates daily); not retrospective for 2022-05 → 2026-05 backtest window
6. **Use within Phase 1A:** Out-of-cache forward-only signal — strategies that depend on Apewisdom only fire from 2026-05-05 onward; PIT loader returns "not_available" for any as_of < 2026-05-05
7. **Use post-Phase-1A:** Stage 3 papertrading + Stage 4 live use Apewisdom as accumulating signal; relevance grows over time

**Why cumulative-daily not scope-out:**

- Owner explicit choice b = cumulative daily prefetcher
- Apewisdom is free; ongoing cost = $0
- Even forward-only signal has Stage 3+ value
- Pattern reuse: same architecture works for any "current snapshot" API (e.g., CNN F&G already uses similar daily-cumulative pattern)

**Implementation:**

- Day 3-5 of DEC-590 9-day window (May 8-10)
- New script: `scripts/prefetch_apewisdom_daily.py` (~30 lines)
- New GitHub Actions workflow: `.github/workflows/refresh_apewisdom.yml` (cron daily)
- Loader update in `backtest/data/sentiment.py` to filter cumulative parquet by `snapshot_date <= as_of`
- Data-integrity test #7 covers this (cumulative snapshot multi-day history assertion)

**Cross-references:**
- DEC-502 (Quiver + Apewisdom + pytrends supplement parent)
- DEC-591 (data-integrity test #7 catches single-day failure)
- L148 (test pyramid gap; this DEC's #7 implementation closes the gap)
- AAII / CNN F&G similar daily-accumulate pattern (precedent)

**Status:** RESOLVED-DECIDED Pass 53 owner approval 2026-05-06 evening.

---

### 23.10 Wikipedia Pageviews Authorized as Alt-Data Signal (DEC-593 — Pass 53 owner-approved 2026-05-06 evening Q-followup c)

**Decision:** Wikipedia pageviews via Wikimedia REST API (https://wikimedia.org/api/rest_v1/metrics/pageviews/) authorized as alternative-data signal for the Stage 2 backtest universe. Owner directive 2026-05-06 (Q-followup c = "authorize new") supersedes prior unauthorized accumulation.

**Scope clarification (HARD-RULE distinction):**

CLAUDE.md HARD RULE "NEVER use Wikipedia" applies to:
- ❌ `pd.read_html('https://en.wikipedia.org/wiki/...')` for S&P 500 / NDX constituent membership scraping (L88)
- ❌ Wikipedia tables as ground-truth source for universe construction (use S&P DJI press releases / FTSE Russell / Nasdaq IR instead)

This DEC authorizes:
- ✅ Wikipedia PAGEVIEWS via Wikimedia REST API as ATTENTION-PROXY alt-data signal (used by quant funds for retail attention)
- ✅ Per-ticker daily pageview count for the company's primary Wikipedia article
- ✅ Cached at `data_prefetch/wikipedia/{TICKER}.parquet` with schema `[date, views, article]`

**Distinction:** "Wikipedia pageviews" (this DEC; alt-data signal) is fundamentally different from "Wikipedia table scraping" (HARD RULE-banned; structured-data scraping). Pageviews are timeseries observations from a STABLE REST API; tables are HTML scraping subject to formatting drift.

**Current cache state (audited 2026-05-06):**

- 1,414 / 1,937 tickers cached (73% coverage)
- Date range: 2021-04-06 → 2026-05-04 (5+ years; matches DEC-505 backtest window)
- Schema: `[date, views, article]` (article = canonical Wikipedia article title; usually company name)

**Use within strategies:**

- Layer 6 universe-level signals (Pass 53 STRATEGY_ROSTER_FULL Layer 6) include attention-proxy signals
- DEC-511 / DEC-513 sentiment universe extensions can consume pageviews
- Sentiment Agent toolkit (DEC-466 OurSentimentToolkit) may consume pageviews as confirmation signal alongside Apewisdom + pytrends

**Coverage extension (Day 3-5):**

- Re-prefetch the 523 missing tickers (likely T2/T3 newer listings) to bring coverage to 100%
- Verify schema consistency via DEC-591 test suite
- Add data-integrity test for cumulative pageview history (≥30d minimum per ticker)

**Why not Apewisdom-only:**

- Wikipedia pageviews exist 2008-present (deep historical); Apewisdom only 2026-05-05 onward forward
- For Stage 2 backtest 2022-05 → 2026-05, Wikipedia pageviews provide RETROSPECTIVE attention signal that Apewisdom cannot
- Complementary: Wikipedia = sustained-attention proxy (encyclopedia); Apewisdom = burst-attention proxy (forum mentions); pytrends = search-attention proxy (Google)

**Cross-references:**
- DEC-502 (alt-data sentiment supplement parent)
- DEC-505 (5y backtest window; Wikipedia coverage matches)
- DEC-591 (data-integrity test #7 covers cumulative history assertion)
- L88 (no Wikipedia HARD RULE — preserved for table-scraping; pageviews carve-out)
- Pass 53 prefetch audit H4 (this DEC closes the unauthorized-accumulation flag)

**Status:** RESOLVED-DECIDED Pass 53 owner approval 2026-05-06 evening.

---

### 23.11 Test-Artifact Same-Commit HARD RULE (DEC-594 — Pass 53 owner-approved 2026-05-06 late evening)

**Decision:** Every DEC that specifies a test layer / validation gate / acceptance criterion / pass criterion MUST include the executable test code (Python, pytest, CI workflow, gate script) in the SAME commit as the DEC text. A DEC cannot mark RESOLVED-DECIDED if any specified test/gate is "to be implemented later." If implementation requires multi-day work, the DEC marks PARTIAL-SPEC-ONLY until the executable artifact lands; only then does it advance to RESOLVED-DECIDED.

**Codified as CHECKLIST #73 + this DEC.**

**Rationale (per L148 + L149 NEW):**

The DEC-503 layer-7 failure is structural, not procedural. DEC-503 marked RESOLVED-DECIDED Pass 52 turn 132 with "Data integrity — schema validation, PIT semantics, completeness gates" in spec. The executable test was never written in that commit. Six weeks of prefetch work shipped under the framing of "comprehensive test pyramid" while layer 7 didn't exist. Pass 53 prefetch audit 2026-05-06 surfaced 5 CRITICAL + 7 HIGH findings that layer 7 would have caught at codification time.

Same pattern caused:
- L86 Pass 26: $50 lost on 6-agent design when actual was 11-agent (no agent-count test before run)
- L95: $100 lost on bug discovered mid-run (no end-to-end smoke before scaled run)
- $300 Phase 1B failed run: insufficient pre-flight validation
- 7 Pass 53 audit cycles: each cycle found gaps that an executable test would have caught

**Trigger words for DEC-594 enforcement:**

DEC pre-flight CHECKLIST #1 review must scan DEC body for: `test`, `validate`, `verify`, `verified`, `gate`, `acceptance criterion`, `pass criterion`, `must pass`, `before X`, `before phase entry`, `before commit`, `before run`. If any present, the DEC body must reference the corresponding executable artifact (file path) and the artifact must exist in the same commit.

**Status taxonomy (extended):**

- `RESOLVED-DECIDED` — spec final, executable artifact present
- `RESOLVED-IMPLEMENTED` — spec + artifact + integration tests + production usage demonstrated
- `PARTIAL-SPEC-ONLY` (NEW) — spec final, executable artifact PENDING; DEC blocked from advancing to RESOLVED-DECIDED until artifact lands
- `PROPOSED` — spec draft awaiting owner approval
- `DEFERRED` — out-of-scope for current stage; revisit at named gate

**Retroactive audit (Day 2-3 of DEC-590 9-day window):**

Scan all 351 existing DECs in [AUDIT_INDEX.md](AUDIT_INDEX.md) for spec-without-build patterns. Each finding gets demoted to PARTIAL-SPEC-ONLY status (or remediated by building the executable artifact in same commit).

**Implementation:**

- New CHECKLIST item #73 (gate executable tests) — codified same commit as this DEC
- New gate test file [backtest/tests/test_gates.py](backtest/tests/test_gates.py) — phase entry/exit gates as pytest functions
- Retroactive audit script [scripts/audit_decs_for_artifacts.py](scripts/audit_decs_for_artifacts.py) — automated scan
- Reviewer (Claude in pre-flight CHECKLIST #1) MUST flag non-compliant DEC drafts BEFORE codification

**Cross-references:**

- L148 (test pyramid layered failure mode — parent lesson for spec-without-build pattern)
- L149 NEW (this turn — codification of "every DEC with test/gate spec must include executable artifact in same commit")
- L86 ($50 lost; same pattern on agent count axis)
- L95 ($100 lost; same pattern on end-to-end smoke axis)
- DEC-503 (test pyramid HARD RULE; this DEC enforces the artifact-not-just-spec layer)
- DEC-591 (data-integrity test layer — first DEC compliant with #594 since artifact landed same-commit)
- CHECKLIST #72 (data-integrity HARD RULE) + #73 (gate executable HARD RULE)

**Status:** RESOLVED-DECIDED Pass 53 owner approval 2026-05-06 late evening ("approve all").

---

### 23.12 Stage / Phase / Sub-phase Gate Executable Tests (DEC-595 — Pass 53 owner-approved 2026-05-06 late evening)

**Decision:** Every transition between stages, phases, sprints, or sub-phases MUST have an executable gate test in [backtest/tests/test_gates.py](backtest/tests/test_gates.py) that asserts the entry/exit criteria. No transition without preceding gate test PASS.

**Gates required (initial set; extends as new transitions defined):**

| # | Gate | Asserts | Triggers |
|---|---|---|---|
| 1 | `test_gate_pre_phase_1a_entry` | 7-test data-integrity (DEC-591) + universe build verified + smoke run on 5 tickers + DEC-505 4-fold config valid | Before May 15 Phase 1A start (DEC-590) |
| 2 | `test_gate_post_phase_1a_alpha` | rules-only Sharpe ≥ 0.7 OOS verified per [PROJECT_PLAN](PROJECT_PLAN.md) §3.6-3.10 | Before $300 1B-α budget commit |
| 3 | `test_gate_pre_phase_1b_alpha_run` | DEC-507 wiring matrix all ✅ + DEC-508 Tier 1-3 fork tests pass + budget tracker armed + Anthropic API rate headroom verified | Before Phase 1B-α run (Sprint 9) |
| 4 | `test_gate_post_phase_1b_alpha_verdict` | DEC-578 7-gate Phase 1B-α verdict has ≥1 PASS cell + DSR validated + walk-forward 4 OOS folds complete (DEC-505) | Before Stage 3 entry |
| 5 | `test_gate_pre_stage_3_entry` | Phase 1B-α verdict produced + paper-trading infrastructure ready + 3-month duration plan (DEC-028) | Before Stage 2 → 3 transition |
| 6 | `test_gate_pre_stage_4_entry` | 3-month paper-trading audit pass + email approval pipeline operational + capital pre-funded | Before Stage 3 → 4 transition |

**Gate behavior:**

- Each gate is a `pytest` function asserting executable conditions (boolean checks on cache state, file existence, metric thresholds)
- Failed gate BLOCKS transition; surfaces actionable error message
- Gate test file is part of standard pytest regression
- New transitions defined → new gate added in same commit (per DEC-594)

**Implementation:**

`backtest/tests/test_gates.py` initial scaffold lands same-commit as this DEC (per DEC-594 enforcement). Gates 1-6 created with current asserts; #1 PASSES today (data-integrity 7/7); #2-#6 are PENDING until corresponding work completes (will assert SkipException with reason until criteria available).

**Cross-references:**

- DEC-594 (parent rule mandating same-commit artifact)
- CHECKLIST #73 (this DEC's HARD RULE codification)
- DEC-590 (Phase 1A May 15 begin date; gate #1 must PASS first)
- DEC-505 (4-fold walk-forward; assertions in gate #2/#4)
- DEC-507/508 (wiring matrix + fork integration; gate #3)
- DEC-578 (7-gate Phase 1B-α verdict; gate #4)
- DEC-028 (Stage 3 paper duration; gate #5)
- L148/L149 (lessons motivating the rule)

**Status:** RESOLVED-DECIDED Pass 53 owner approval 2026-05-06 late evening.

---

### 23.13 Standing Approvals + Per-Turn Push (DEC-596 — Pass 53 owner directive 2026-05-06 late evening)

**Decision:** Owner grants blanket standing approval for routine bash execution and mandates per-turn git push to `main`, contingent on Claude maintaining careful + thorough verification discipline (test pyramid, pre-flight CHECKLIST, data-integrity scan, gate tests). **Pre-approval scope is bash + push ONLY — ALL decisions still require explicit owner approval per CLAUDE.md.**

**Owner directives (verbatim):**

1. *"i approve all bash runs. Dont ask me over and over again in the turn. make this the standard practice going ahead. As long as your are careful and thorough and integrate testing and checks, no need for repeated approvals. Also push to git/main every turn."* (2026-05-06 late evening)
2. *"All decisions will still need to be approved by me."* (2026-05-06 late evening clarification — narrows pre-approval to bash + push only; reaffirms CLAUDE.md "All decisions need explicit owner approval before implementation" HARD RULE)

**Standing approval scope (PRE-APPROVED — no per-turn Q&A required) — BASH + PUSH ONLY, no decisions:**

| Operation | Status |
|---|---|
| File reads (Read, Grep, Glob) | ✅ Pre-approved |
| pytest execution | ✅ Pre-approved |
| Script execution (Python data-inspection / cache scans / prefetch utilities) | ✅ Pre-approved |
| Git status / log / diff / show | ✅ Pre-approved |
| Routine commits + pushes to `main` | ✅ Pre-approved (push every turn standard practice) |
| Background bg cycle restarts (pytrends auto-continue, etc.) | ✅ Pre-approved |
| Data-integrity scans + cache audits | ✅ Pre-approved |
| Building executable test artifacts per DEC-594 — **only when implementing already-approved DEC; NOT for designing new methodology** | ✅ Pre-approved (within already-approved scope) |

**Operations STILL requiring explicit owner approval (preserved) — ALL DECISIONS, not just methodology:**

| Operation | Why approval still required |
|---|---|
| **ALL decisions** (per 2026-05-06 owner clarification) | CLAUDE.md HARD RULE — "All decisions need explicit owner approval before implementation. No exceptions." Includes scope decisions, triage decisions, build vs annotate vs demote choices, recommendation selection, prioritization, etc. |
| **API spend that ramps cost** | L86 ($50) + L95 ($100) + $300 Phase 1B failed run lessons; CHECKLIST #13/22/23/29 small-batch → review → approve → scale protocol unchanged |
| **Methodology / strategy / threshold / parameter changes** | CLAUDE.md HARD RULE — "Never change rules, filters, thresholds, or parameters without approval" |
| **Destructive git operations** (`reset --hard`, force push, etc.) | CLAUDE.md HARD RULE; L49 + L77 prior data-loss incidents |
| **CLAUDE.md modifications** | CHECKLIST #6 — exact before/after diff + explicit written approval required |
| **Phase transitions** (Stage 2 → 3, Phase 1A → 1B-α, etc.) | DEC-595 + CHECKLIST #73 — preceding gate test PASS required |
| **DEC drafting / status changes / scope expansions** | All decisions per owner 2026-05-06 clarification |
| **CLAUDE.md hooks / settings** | Owner-controlled; tooling configuration |

**The line in plain English:** Pre-approval covers EXECUTING already-approved work (running tests, reading files, committing, pushing). It does NOT cover DECIDING what to do next, what scope to expand, what to build vs defer, what status to assign. Decisions always go through owner.

**Verification discipline (preserved; non-negotiable per standing-approval contract):**

- Pre-flight CHECKLIST runs before every recommendation per Pass 52 mandate
- Test pyramid runs before every code push per DEC-503 + CHECKLIST #69
- Data-integrity 7/7 PASS per DEC-591 + CHECKLIST #72
- Gate tests PASS before phase transitions per DEC-595 + CHECKLIST #73
- DEC-594 same-commit artifact rule — no DEC marks RESOLVED-DECIDED without artifact in same commit

**Per-turn push protocol:**

- Every turn that produces meaningful changes ends with `git commit + git push origin main`
- Commit message follows existing convention (subject + body + Co-Authored-By: Claude line)
- Multiple logical changes in one turn → one commit (atomic per turn) OR multiple commits if logically separable; both acceptable
- Push cadence supersedes prior CLAUDE.md "meaningful checkpoints only" guidance
- If a turn produces NO meaningful changes (e.g., status check / question answered), no commit needed
- PAT lifecycle (CLAUDE.md Push & PAT Pattern) preserved — owner re-pastes PAT per session

**Implicit conditions (revocation triggers):**

- If Claude is careless (e.g., destructive op without check, methodology change without approval, $-cost ramp without batch-review), standing approval is revocable
- The standing approval is a TRUST contract; verification discipline is the consideration

**Codification:**

- This DEC (TRADING_RULES §23.13)
- AUDIT_INDEX entry DEC-596
- Auto-memory `feedback_standing_approvals.md` (persistent across conversations)
- AUDIT.md narrative entry 2026-05-06 evening

**Cross-references:**

- CLAUDE.md "All API runs costing money" rule (preserved; still applies for COSTLY API ramps)
- CLAUDE.md "All decisions need explicit owner approval before implementation" (preserved for METHODOLOGY/strategy/threshold)
- CHECKLIST #1 (owner approval for new recommendations — still required pre-flight)
- CHECKLIST #6 (CLAUDE.md modifications — still require diff approval)
- CHECKLIST #13/22/23/29 (small-batch → review → approve → scale for API ramps)
- DEC-594/595 + CHECKLIST #73 (verification discipline; consideration in TRUST contract)
- L86 + L95 ($150 prior losses; reasons for preserving API approval rule)

**Status:** RESOLVED-DECIDED Pass 53 owner approval 2026-05-06 late evening.

---

# DOCUMENT METADATA

**Created:** Pass 52 turn 128 (post-Pass-52 closure, pre-Sprint-1 setup phase)
**Status:** Canonical for trading rules, thresholds, criteria, benchmarks across all 5 stages
**Refresh trigger:** Any threshold change requires Owner approval per CHECKLIST #51 + atomic update to this document per CHECKLIST #58
**Companion:** PROJECT_PLAN.md (project entry point); ENGINEERING_REGISTER.md (sprint roadmap); AUDIT.md (decision detail); BUG_REGISTER.md (bug-decision cross-reference)

**Total threshold items documented:** 28 REVISIT_AFTER_BACKTEST tags + ~50 fixed thresholds across 23 sections (+ §23.6 DEC-589 audit-iteration ceiling + §23.7 DEC-590 Phase 1A implementation begin date 2026-05-15 per Pass 53 review-cycle closure).

---

*End of TRADING_RULES_AND_INFORMATION.md*
*Per CHECKLIST #25 (highly detailed per owner directive #3); #43 (cross-references verified to source decisions); #51 (owner-approved structure executed); #57 (use-case mapping per section); #58 (canonical home for thresholds; ENGINEERING_REGISTER cross-references this document instead of duplicating).*

---

## Pass 53 Sprint 0A data sources update (2026-05-05)

### Stage 2 NO-LIVE-API HARD CUT (DEC-497)

Stage 2 backtest reads from `data_prefetch/<api_name>/<endpoint>/...` only. NO live API calls during backtest. yfinance permitted for one-time SETUP only (e.g., universe-build T3 sector backfill); not in runtime hot path. Affected modules (refactored Sprint 0A.8): `backtest/data/{fetcher,macro,sentiment,smart_money}.py`.

### Sprint 0A confirmed data sources (8 APIs)

| API | Subscription | Cost | Sub-phase | Status |
|---|---|---|---|---|
| Polygon Stocks Starter | Owner subscribed | $29/mo | 0A.1 + 0A.9 | OHLCV done; EXTENSION pending |
| FRED + ALFRED | Free | $0 | 0A.2 | Curating to ~15-20 series |
| AAII | Free | $0 | 0A.3 | Pending |
| CNN F&G (composite + 7 sub-components) | Free | $0 | 0A.3 | Pending — 7 sub-components Pass 53 expansion |
| CFTC COT (CME E-mini S&P 500) | Free | $0 | 0A.4 | Pending — wires existing stub |
| Quiver Trader 8 endpoint groups (DEC-502) | Owner subscribed | $50-100/mo | 0A.5 | Pending — silent-gap fix first |
| SEC EDGAR via edgartools (Form 4, 8-K, 10-Q/K) | Free | $0 | 0A.6 | Pending |
| Apewisdom + pytrends (free social sentiment) | Free | $0 | 0A.7 | Pending — DEC-502 supplement |

### Polygon ticker events integration (DEC-500 owner directive 2026-05-05)

`https://api.polygon.io/vX/reference/tickers/{ticker}/events` (Reference Data, included in Stocks Starter).

Event types: ticker_change, ticker_split, name_change, listing_change, exchange_change, delisting, new_listing.

Cache: `data_prefetch/polygon/events/{ticker}.parquet`.

Feeds all 11 active TradingAgents per DEC-057 + DETAILED_PROJECT_PLAN.md §2.6 (Market / Fundamentals / News Analysts + Bull / Bear Researchers + Research Manager + Trader + Aggressive / Conservative / Neutral Risk Debaters + Portfolio Manager) + T2 SCREENER per DEC-380. Note: prior wording "all 6 TradingAgents" reflected the conceptual-role simplification before TradingAgents Pattern 2 integration; correct enumeration is 11+ active LLM nodes per L94/Pass 26.

### Polygon Options NOT upgraded (DEC-501 owner directive 2026-05-05)

Owner Q1=C declined Stocks Starter upgrade; Polygon Options is separate subscription. Stage-2 Risk Agent operates on ATR (backward-looking) only. Stage-3 / Phase 1C revisit.

### Critical silent-gap bugs (BUG-271/272/273; smart_money silent-gap)

3 endpoints in current code 404 against Trader subscription. `smart_money_score` composite computing on 1-of-3 inputs. Fix scheduled next turn with full DEC-503 test pyramid.

### CHECKLIST additions Pass 53

- **#67 / #67.b** — per-turn doc sync (decoupled from pending runs); DEC-498
- **#68** — smoke→demo→full execution protocol for multi-call API operations
- **#69** — comprehensive test pyramid before every code push (DEC-503 HARD RULE)

**Cross-references:** AUDIT_INDEX.md DEC-497-503; AUDIT.md Pass 53 narrative; BUG_REGISTER.md BUG-271/272/273; DETAILED_PROJECT_PLAN.md Part 2.6 + §3.16; THEME_X53_SEQUENCING.md Sprint 0A.0-0A.10; API_AUDIT.md Pass 53 endpoint inventory.
