# TRADING_RULES_AND_INFORMATION

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
- [ ] Rules-based screener executes full ~109-119 strategy roster on full universe (per DEC-477 Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv + DEC-483 R1000 + NDX expansion)
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
- [ ] 9 new exit methods (DEC-067 phases A+B = DEC-432/433)
- [ ] AEP breaker (DEC-435)
- [ ] Total strategy roster ~109-119 strategies operational

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
- **Strategy roster consumption of signals:** STRATEGY_REGISTER.md
- **Cube dimensions consuming signals as filters:** §21
- **PIT enforcement for all signals:** §12 (DEC-305 RAISE not WARNING)
- **Signal-cleanup decisions:** DEC-453 (OpenBB), DEC-454 (Alpha Vantage), DEC-455 (Finnhub) — Sprint 4 deprecation cleanup; DEC-440 (Polygon news replaces AV+Finnhub); DEC-484 (SEC EDGAR replaces FMP for fundamentals)

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

### 3.2 Gate 2: Statistical Significance (p < 0.05 Bonferroni-corrected)

**Rule:** Strategy returns must be statistically significant at p < 0.05 **after Bonferroni correction** for multiple testing.

**Bonferroni correction factor:** Number of strategies × number of cells tested. Per DEC-080+400, correction is applied within cube methodology.

**Per DEC-018:** Bonferroni correction factor was hardcoded to 60 in original code (BUG-18) — must be 72 (or current strategy count); fixed via DEC-400.

**Source:** DEC-080, DEC-400, DEC-426

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

### 6.2 Per-Ticker Cumulative Max-Loss Cap (per DEC-135)

**Rule:** **Default cap: -10% rolling 30-day per ticker.** If breached, halt that ticker for 30-day cooldown.

**Implementation:**
```
ticker_30d_pnl = cumulative_pnl(ticker, lookback=30d)
if ticker_30d_pnl <= -0.10 × initial_portfolio:
    halt_ticker(ticker, cooldown=30d)
```

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

### 8.1 17 Exit Methods

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

---

## 9. Circuit Breakers

### 9.1 Levels 1-5 (per DEC-314 + DEC-315)

| Level | Trigger | Action |
|---|---|---|
| **Level 1** | Single-day -1% portfolio | Soft pause: halve position sizes 1 day |
| **Level 2** | Single-day -2% portfolio | Soft pause: halve position sizes 2 days |
| **Level 3** | Intraday -7% from open | Intraday halt (NYSE Rule 80B trigger 1) |
| **Level 4** | Intraday -13% from open | Extended halt (NYSE Rule 80B trigger 2) |
| **Level 5** | Intraday -20% from open | Market halt (NYSE Rule 80B trigger 3) |

**Documentation note (per DEC-126 + DEC-314):** Levels 3-4 were documented but NOT implemented in original code; implementation Sprint 2 per DEC-314.

**Source:** DEC-314, DEC-315

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

### 10.7 Regime Hysteresis VIX SMA (per DEC-317)

**Rule:** Regime transitions require VIX to cross threshold AND stay there for SMA window (e.g., VIX 21-day SMA, not single-day spike).

**Methodology:** Prevents single-day VIX spike from triggering regime change.

**Source:** DEC-317

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

## 11. Regime-Conditional Strategy Behavior

### 11.1 Crisis-Flag Handling (replaces hard regime direction blocks)

**Per project memory:** Original system had hard regime direction blocks (e.g., long-only blocked in Bear regime). **REMOVED.**

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

### 16.2 Cache Extends to 2018-01-01 (per DEC-109 Option B)

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

1. **Strategy** (~109-119 strategy classes)
2. **Regime** (Bull/Bull-Pause/Neutral/Bear-Pause/Bear/Crisis — 6 levels)
3. **Sector** (11 GICS sectors)
4. **Market cap band** (mega/large/mid/small)
5. **Volatility band** (low/medium/high realized vol)
6. **Momentum band** (low/mid/high momentum percentile)
7. **Liquidity band** (low/medium/high ADV)
8. **Time period** (per OOS fold — 2023, 2024, 2025)

### 21.2 Additional Dimensions

9. **Trigger type** (catalyst/technical/stat-arb per DEC-174)
10. **Exit method** (17 exit methods per §8)
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

**Phase 1B-α (initial tuning):** Tune all items post-empirical-evidence; baseline values updated based on Phase 1B-α outputs.

**Quarterly re-tune (Stage 3+):** Per DEC-214 quarterly re-validation, REVISIT_AFTER_BACKTEST items re-evaluated; demote/retire strategies showing decay (DEC-249).

**Stage 4+ ongoing:** Live trading data feeds into tuning loop; quarterly cadence continues.

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

# DOCUMENT METADATA

**Created:** Pass 52 turn 128 (post-Pass-52 closure, pre-Sprint-1 setup phase)
**Status:** Canonical for trading rules, thresholds, criteria, benchmarks across all 5 stages
**Refresh trigger:** Any threshold change requires Owner approval per CHECKLIST #51 + atomic update to this document per CHECKLIST #58
**Companion:** PROJECT_PLAN.md (project entry point); ENGINEERING_REGISTER.md (sprint roadmap); AUDIT.md (decision detail); BUG_REGISTER.md (bug-decision cross-reference)

**Total threshold items documented:** 28 REVISIT_AFTER_BACKTEST tags + ~50 fixed thresholds across 23 sections.

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
