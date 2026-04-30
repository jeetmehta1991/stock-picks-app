# AUDIT_INDEX.md — Decision and Bug Registry
**Last regenerated:** April 2026 (post-Pass 51)

---

## Decision Registry

**Total: 346 decision entries**

| Status | Count |
|---|---|
| RESOLVED | 71 |
| PARTIAL | 5 |
| SUPERSEDED | 7 |
| PENDING | 263 |

### All Decisions Table

| ID | Title | Status | Theme | Pass Intro | Pass Resolved |
|---|---|---|---|---|---|
| **DECISION-001** | Quiver subscription cancellation timing | RESOLVED | Phase 0 / Architecture | Pass 19 | 19 |
| **DECISION-002** | Polygon News evaluation | RESOLVED | Phase 0 / Architecture | Pass 19 | 19 |
| **DECISION-003** | Phase 0 inclusion in PROJECT_PLAN | RESOLVED | Phase 0 / Architecture | Pass 19 | 19 |
| **DECISION-004** | Phase 0.A scope | RESOLVED | Phase 0 / Architecture | Pass 19 | 19 |
| **DECISION-005** | Strategy count target — 130 strategies + OpenBB+Polygon fundamentals | RESOLVED | Phase 0 / Architecture | Pass 19 | 19 |
| **DECISION-006** | Strategy families to defer to Phase 1F | RESOLVED | Phase 0 / Architecture | Pass 19 | 19 |
| **DECISION-007** | Phase 0 timeline (7-12 months path to live) | RESOLVED | Phase 0 / Architecture | Pass 19 | 19 |
| **DECISION-008** | Decision Agent action field integration (BUG-113) | PARTIAL | Phase 0 / Architecture | Pass 19 | 24 |
| **DECISION-009** | Position size modifier integration (BUG-118) | PARTIAL | Phase 0 / Architecture | Pass 19 | 24 |
| **DECISION-010** | Risk Agent trade_blocked semantics (BUG-116) | PARTIAL | Phase 0 / Architecture | Pass 19 | 24 |
| **DECISION-011** | Bull/Bear debate winner integration (BUG-119) | PARTIAL | Phase 0 / Architecture | Pass 19 | 24 |
| **DECISION-012** | Recommended exit integration (BUG-117) | PARTIAL | Phase 0 / Architecture | Pass 19 | 24 |
| **DECISION-013** | earnings_tolerant strategy attribute (REVISED) | RESOLVED | Architectural - Migration / Stage 3+ | Pass ? | 24 |
| **DECISION-014** | Phase 1B passing criteria adjustments | PENDING | Phase 1B Methodology | Pass 19 | - |
| **DECISION-015** | Strategy correlation analysis methodology | PENDING | Phase 1B Methodology | Pass 19 | - |
| **DECISION-016** | Threshold calibration scope (BUG-130) | PENDING | Phase 1B Methodology | Pass 19 | - |
| **DECISION-017** | Earnings proximity hard filter (BUG-131) — superseded by 013-revised | SUPERSEDED | SUPERSEDED | Pass 19 | 38 |
| **DECISION-018** | Cooldown after stop-out (BUG-133) | PENDING | Risk Management (Group C) | Pass 19 | - |
| **DECISION-019** | Liquidity filter timing (BUG-135) | PENDING | Risk Management (Group C) | Pass 19 | - |
| **DECISION-020** | News API selection (depends on 002 eval results) | PENDING | Process / Infrastructure (Group F) | Pass 19 | - |
| **DECISION-021** | Tier system simplification | PENDING | Strategy / Regime Adaptation (Group D) | Pass 19 | - |
| **DECISION-022** | Drawdown-aware position sizing (BUG-170) | PENDING | Risk Management (Group C) | Pass 19 | - |
| **DECISION-023** | Vol-targeted position sizing (BUG-168) | PENDING | Risk Management (Group C) | Pass 19 | - |
| **DECISION-024** | Correlation-adjusted concentration limits (BUG-169) | PENDING | Risk Management (Group C) | Pass 19 | - |
| **DECISION-025** | Regime-conditional strategy weighting (BUG-175) | PENDING | Strategy / Regime Adaptation (Group D) | Pass 19 | - |
| **DECISION-026** | Walk-forward parameter re-optimization (BUG-172) | PENDING | Strategy / Regime Adaptation (Group D) | Pass 19 | - |
| **DECISION-027** | Online learning / feedback loop (BUG-173) | PENDING | Strategy / Regime Adaptation (Group D) | Pass 19 | - |
| **DECISION-028** | Stage 3 paper trading duration — Stage 3 paper trading duration: 3 months | RESOLVED | Live Trading Operational (Group E) | Pass 19 | 43 |
| **DECISION-029** | Stage 4 starting capital — SPLIT into 029-A/B/C | RESOLVED | Live Trading Operational (Group E) | Pass 19 | 43 |
| **DECISION-029-A** | Paper trading notional 1: $5K CAD (small-account drag realism) | RESOLVED | Paper Trading Setup | Pass 43 | 43 |
| **DECISION-029-B** | Paper trading notional 2: $50K CAD (target AUM scale) | RESOLVED | Paper Trading Setup | Pass 43 | 43 |
| **DECISION-029-C** | Real-money starting capital — DEFERRED until post-paper-trading evaluation | PENDING | Live Trading Operational (Group E) | Pass 43 | - |
| **DECISION-030** | Wikipedia data alternative (BUG-185) — superseded by 052+L88 | SUPERSEDED | SUPERSEDED | Pass 19 | 38 |
| **DECISION-031** | Codespace/Cloud workflow vs local — Codespace through Phase 0, migrate to cloud before Sta | RESOLVED | Process / Infrastructure (Group F) | Pass 19 | 43 |
| **DECISION-032** | IBKR vs Alpaca for paper trading — superseded by 054 | SUPERSEDED | SUPERSEDED | Pass 19 | 38 |
| **DECISION-033** | Email approval system — REPLACED with email notifications + summaries (no approval gateway | RESOLVED | Live Trading Operational (Group E) | Pass 19 | 43 |
| **DECISION-034** | Daily loss limits for live trading | PENDING | Live Trading Operational (Group E) | Pass 19 | - |
| **DECISION-035** | Tax classification approach (Canadian) — Defer until CPA consultation before Stage 4 — kee | PENDING | Live Trading Operational (Group E) | Pass 19 | - |
| **DECISION-036** | Audit document maintenance going forward — Audit doc maintenance: trigger-only, not period | RESOLVED | Process / Infrastructure (Group F) | Pass 19 | 43 |
| **DECISION-037** | Characterization-test-first approach (Phase A) | PENDING | Phase 0 Sub-Scope (Group G) | Pass 20 | - |
| **DECISION-038** | Layered execution with iteration budgets | PENDING | Phase 0 Sub-Scope (Group G) | Pass 20 | - |
| **DECISION-039** | Phase 0 parallelization (deferred) | RESOLVED | Phase 0 / Architecture | Pass 22 | 22 |
| **DECISION-040** | PointInTimeLoader structural framework | RESOLVED | Phase 0 / Architecture | Pass 22 | 22 |
| **DECISION-041** | No Phase 0 compression | RESOLVED | Phase 0 / Architecture | Pass 23 | 23 |
| **DECISION-042** | AgentGateConfig spec (PARTIAL — needs revision) | RESOLVED | Phase 0 / Architecture | Pass 25 | 25 |
| **DECISION-043** | Retune framework | PENDING | Process / Infrastructure (Group F) | Pass 25 | - |
| **DECISION-044** | Phase 0.D scope — superseded by 045 | SUPERSEDED | SUPERSEDED | Pass 26 | 38 |
| **DECISION-045** | Adopt fork-existing strategy across Phase 0 | RESOLVED | Phase 0 / Architecture | Pass 27 | 27 |
| **DECISION-046** | Drop CVD from Phase 0 | RESOLVED | Phase 0 / Architecture | Pass 27 | 27 |
| **DECISION-047** | QuantStats for performance analytics | RESOLVED | Phase 0 / Architecture | Pass 28 | 33 |
| **DECISION-048** | Streamlit for Stage 3+ dashboard | RESOLVED | Phase 0 / Architecture | Pass 28 | 33 |
| **DECISION-049** | ib_async for IBKR integration | RESOLVED | Phase 0 / Architecture | Pass 28 | 33 |
| **DECISION-050** | freezegun for PIT regression tests | RESOLVED | Phase 0 / Architecture | Pass 28 | 29 |
| **DECISION-051** | Staged TradingAgents adoption (REVISED-3) | RESOLVED | Phase 0 / Architecture | Pass 28 | 33 |
| **DECISION-052** | Fork S&P 500 historical dataset (CC0) | RESOLVED | Phase 0 / Architecture | Pass 28 | 28 |
| **DECISION-053** | Defer Streamlit timing | RESOLVED | Phase 0 / Architecture | Pass 29 | 33 |
| **DECISION-054** | IBKR for both paper and live | RESOLVED | Phase 0 / Architecture | Pass 29 | 33 |
| **DECISION-055** | Cost-optimized TradingAgents config | RESOLVED | Phase 0 / Architecture | Pass 31 | 33 |
| **DECISION-056** | Skip TradingAgents CLI | RESOLVED | Phase 0 / Architecture | Pass 31 | 33 |
| **DECISION-057** | Disable Social Analyst | RESOLVED | Phase 0 / Architecture | Pass 31 | 33 |
| **DECISION-058** | GPT-5.4-mini for backtest, Anthropic for live (REVISED) | RESOLVED | Phase 0 / Architecture | Pass 32 | 33 |
| **DECISION-059** | $300 hard cap on Stage 2 backtest | RESOLVED | Phase 0 / Architecture | Pass 32 | 33 |
| **DECISION-060** | Smoke test gating before Stage 2 scale | RESOLVED | Phase 0 / Architecture | Pass 35 | 36 |
| **DECISION-061** | Tier mapping — Option 1 (their 5-tier → our adjustment) | RESOLVED | TradingAgents Architecture | Pass 38 | 38 |
| **DECISION-062** | Output schema translation: TradingAgents 5-tier → position_size_modifier | PENDING | TradingAgents Architecture | Pass 38 | - |
| **DECISION-063** | Universe refresh automation | PENDING | Batch X1 — Data + Universe | Pass 39 | - |
| **DECISION-064** | Phase 0.A prefetch checklist | PENDING | Batch X1 — Data + Universe | Pass 39 | - |
| **DECISION-065** | Validate stored data quality before Phase 1B-α | PENDING | Batch X1 — Data + Universe | Pass 39 | - |
| **DECISION-066** | Granularity standard for all backtest outputs | PENDING | Batch X8 — Granularity + Breakdowns | Pass 39 | - |
| **DECISION-067** | Add 9 missing exit methods | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 39 | - |
| **DECISION-068** | Bootstrap CI + pairwise significance for exit comparison | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 39 | - |
| **DECISION-069** | Per-regime exit selection | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 39 | - |
| **DECISION-070** | Portfolio-level exit logic | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 39 | - |
| **DECISION-071** | Smart money refinement (officer roles, 10b5-1 filter, etc.) | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-072** | Separate WSB from smart money | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-073** | Adopt Quiver pre-built composites | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-074** | Polygon block trades / dark pool eval | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-075** | Adverse-excursion-from-peak breaker | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 39 | - |
| **DECISION-076** | Factor exposure breaker | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 39 | - |
| **DECISION-077** | Portfolio drawdown breaker | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 39 | - |
| **DECISION-078** | Stop-out cluster breaker | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 39 | - |
| **DECISION-079** | Reconcile Level 2 earnings gap with earnings_tolerant | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 39 | - |
| **DECISION-080** | t-stat + Bonferroni | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
| **DECISION-081** | Sharpe + Sortino + transaction cost sensitivity | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
| **DECISION-082** | Stress-test pass requirements (2008/2020/2022) | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
| **DECISION-083** | Min trades floor 300 independent positions | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
| **DECISION-084** | Audit flag at 70% win rate — Audit flag threshold lowered to 65% win rate (more aggressive | RESOLVED | Batch X4 — Statistical Methodology | Pass 39 | 43 |
| **DECISION-085** | Define macro correlation precisely | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
| **DECISION-086** | Fractional Kelly position sizing | PENDING | Batch X5 — Risk Management Extension | Pass 39 | - |
| **DECISION-087** | Vol-targeted sizing per-position (closes 023) | PENDING | Batch X5 — Risk Management Extension | Pass 39 | - |
| **DECISION-088** | Portfolio vol target 15% | PENDING | Batch X5 — Risk Management Extension | Pass 39 | - |
| **DECISION-089** | Max correlation cap between positions | PENDING | Batch X5 — Risk Management Extension | Pass 39 | - |
| **DECISION-090** | Max sector exposure cap | PENDING | Batch X5 — Risk Management Extension | Pass 39 | - |
| **DECISION-091** | Drawdown re-sizing | PENDING | Batch X5 — Risk Management Extension | Pass 39 | - |
| **DECISION-092** | Slippage model = f(size%ADV, vol) | PENDING | Batch X5 — Risk Management Extension | Pass 39 | - |
| **DECISION-093** | Migrate live to AWS/GCP/DO before Stage 4 | PENDING | Batch X3 — Architecture | Pass 39 | - |
| **DECISION-094** | Secrets manager | PENDING | Batch X3 — Architecture | Pass 39 | - |
| **DECISION-095** | Monitoring + alerting | PENDING | Batch X3 — Architecture | Pass 39 | - |
| **DECISION-096** | Backtest reproducibility (code + data + config hash) | PENDING | Batch X3 — Architecture | Pass 39 | - |
| **DECISION-097** | Reconciliation job (daily position vs broker) | PENDING | Batch X3 — Architecture | Pass 39 | - |
| **DECISION-098** | Test coverage 70% before Stage 3 | PENDING | Batch X3 — Architecture | Pass 39 | - |
| **DECISION-099** | 11 missing strategy categories (Pairs, Calendar, Cross-Asset, Index Rebalance, etc.) | PENDING | Batch X1 — Data + Universe | Pass 39 | - |
| **DECISION-100** | 17+ categorical breakdown variables | PENDING | Batch X8 — Granularity + Breakdowns | Pass 39 | - |
| **DECISION-101** | Earnings strategies post-Phase 0.A | PENDING | Batch X1 — Data + Universe | Pass 39 | - |
| **DECISION-102** | Market-Level / Correlation-Factor strategies | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-103** | Auto-populate Tier 2 universe (spinoffs, IPOs, $5B+) | PENDING | Batch X1 — Data + Universe | Pass 39 | - |
| **DECISION-104** | Auto-populate Tier 3 momentum watchlist | PENDING | Batch X1 — Data + Universe | Pass 39 | - |
| **DECISION-105** | Spinoff detector | PENDING | Batch X1 — Data + Universe | Pass 39 | - |
| **DECISION-106** | Regime inputs 2 → 8+ | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-107** | Regime probability (not hard label) | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-108** | Regime persistence model (HMM or smoothing) | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-109** | Rolling 5yr/1yr walk-forward | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
| **DECISION-110** | Deflated Sharpe (Bailey et al.) | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
| **DECISION-111** | Stationarity / structural break tests | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
| **DECISION-112** | Disaster recovery plan + incident runbook | PENDING | Batch X3 — Architecture | Pass 39 | - |
| **DECISION-113** | Trade journal + research log + failure log | PENDING | Batch X3 — Architecture | Pass 39 | - |
| **DECISION-114** | Live-vs-backtest divergence monitoring | PENDING | Batch X3 — Architecture | Pass 39 | - |
| **DECISION-115** | Tail hedging consideration — Tail hedging skipped at small AUM, revisit at $100K+ | SUPERSEDED | Batch X5 — Risk Management Extension | Pass 39 | 43 |
| **DECISION-116** | Cash management protocol (idle cash to SGOV/T-bills) — Cash management: manual idle-to-SGO | RESOLVED | Batch X5 — Risk Management Extension | Pass 39 | 43 |
| **DECISION-117** | Add file-level checksum + last-validated timestamp to cache | PENDING | Batch X9 — Data integrity | Pass 40 | - |
| **DECISION-118** | Prefetch full cross-asset macro (VIX direct, DXY, GLD, oil, sector ETFs, TLT, HYG, SHY) | PENDING | Batch X9 — Data integrity | Pass 40 | - |
| **DECISION-119** | Per-trade explainability dict (primary_signal, dominant_multiplier, agent_tier_delta) | PENDING | Batch X10 — Trade explainability | Pass 40 | - |
| **DECISION-120** | Automatic loss attribution report — top 10 losing trades per strategy with full context | PENDING | Batch X10 — Trade explainability | Pass 40 | - |
| **DECISION-121** | Exit comparison report includes side-by-side exit dates/prices | PENDING | Batch X11 — Exit comparison | Pass 40 | - |
| **DECISION-122** | Per-exit-method slippage modeling | PENDING | Batch X11 — Exit comparison | Pass 40 | - |
| **DECISION-123** | Apply exponential decay to smart money signal weights | PENDING | Batch X12 — Smart money refinement | Pass 40 | - |
| **DECISION-124** | Cross-source smart money clusters (insider+congressional+13F confluence) | PENDING | Batch X12 — Smart money refinement | Pass 40 | - |
| **DECISION-125** | Add Form 144 prefetch (proposed sales — leading indicator) | PENDING | Batch X12 — Smart money refinement | Pass 40 | - |
| **DECISION-126** | Document time-resolution limitations of circuit breakers — Document time-resolution limits | RESOLVED | Batch X13 — Circuit breakers extension | Pass 40 | 43 |
| **DECISION-127** | Define recovery rules from each circuit breaker level (cooldown, hysteresis) | PENDING | Batch X13 — Circuit breakers extension | Pass 40 | - |
| **DECISION-128** | Dispersion-conditional circuit breaker | PENDING | Batch X13 — Circuit breakers extension | Pass 40 | - |
| **DECISION-129** | Live-vs-backtest Sharpe equivalence criterion (within 0.3 to pass Stage 3) | PENDING | Batch X14 — Validation criteria | Pass 40 | - |
| **DECISION-130** | Capacity stress test (5x capital, Sharpe drop <0.3) | PENDING | Batch X14 — Validation criteria | Pass 40 | - |
| **DECISION-131** | Agent value-add minimum (Sharpe improvement >=0.2 over rules-only) | PENDING | Batch X14 — Validation criteria | Pass 40 | - |
| **DECISION-132** | Annual Sharpe variance < 0.5 stability requirement | PENDING | Batch X14 — Validation criteria | Pass 40 | - |
| **DECISION-133** | Max gross long/short/net exposure caps | PENDING | Batch X15 — Risk management deeper | Pass 40 | - |
| **DECISION-134** | USD/CAD currency exposure tracking + optional FX hedge | PENDING | Batch X15 — Risk management deeper | Pass 40 | - |
| **DECISION-135** | Per-ticker cumulative max-loss cap (rolling 30-day) | PENDING | Batch X15 — Risk management deeper | Pass 40 | - |
| **DECISION-136** | Portfolio rebalancing frequency policy | PENDING | Batch X15 — Risk management deeper | Pass 40 | - |
| **DECISION-137** | Backtest output schema versioning + migration path | PENDING | Batch X16 — Architecture extension | Pass 40 | - |
| **DECISION-138** | Cold-start CI test (fresh container in <30 min) | PENDING | Batch X16 — Architecture extension | Pass 40 | - |
| **DECISION-139** | Remote kill switch (email-based STOP) | PENDING | Batch X16 — Architecture extension | Pass 40 | - |
| **DECISION-140** | Structured JSON logging standard | PENDING | Batch X16 — Architecture extension | Pass 40 | - |
| **DECISION-141** | Sector-neutral hedge overlay (long position + short sector ETF) | PENDING | Batch X17 — Strategy extensions | Pass 40 | - |
| **DECISION-142** | Optional market-neutral construction (long stock + short SPY at beta) | PENDING | Batch X17 — Strategy extensions | Pass 40 | - |
| **DECISION-143** | IPO/lockup/secondary offering systematic framework | PENDING | Batch X17 — Strategy extensions | Pass 40 | - |
| **DECISION-144** | Stock-vs-sector momentum delta as breakdown variable | PENDING | Batch X17 — Strategy extensions | Pass 40 | - |
| **DECISION-145** | IV delta vs historical pre-earnings pattern as signal | PENDING | Batch X17 — Strategy extensions | Pass 40 | - |
| **DECISION-146** | Corporate actions handler (split/dividend/spinoff/rename) | PENDING | Batch X18 — Universe management | Pass 40 | - |
| **DECISION-147** | Delisting registry + survivorship bias correction | PENDING | Batch X18 — Universe management | Pass 40 | - |
| **DECISION-148** | Stock-specific adaptive momentum lookback (vol-adjusted) | PENDING | Batch X18 — Universe management | Pass 40 | - |
| **DECISION-149** | Regime transition probability matrix | PENDING | Batch X19 — Regime extensions | Pass 40 | - |
| **DECISION-150** | Multi-asset regime detection (equity+credit+commodity+currency) | PENDING | Batch X19 — Regime extensions | Pass 40 | - |
| **DECISION-151** | Sector-level regime classification | PENDING | Batch X19 — Regime extensions | Pass 40 | - |
| **DECISION-152** | Hold-out final test period (never touched during audits) | PENDING | Batch X20 — IS/OOS extensions | Pass 40 | - |
| **DECISION-153** | Regime-stratified train/test splits | PENDING | Batch X20 — IS/OOS extensions | Pass 40 | - |
| **DECISION-154** | Market structure change tracker (quarterly) — Informal note in audit when market changes n | SUPERSEDED | Batch X21 — Benchmarking | Pass 40 | 43 |
| **DECISION-155** | vs-SPY comparison in all backtest reports | PENDING | Batch X21 — Benchmarking | Pass 40 | - |
| **DECISION-156** | Commit message references explicit CHECKLIST items followed — Commit messages reference CH | RESOLVED | Batch X22 — Process discipline | Pass 40 | 43 |
| **DECISION-157** | Synthetic broker outage testing during Stage 3 (chaos engineering) | PENDING | Batch X23 — Edge case handling | Pass 40 | - |
| **DECISION-158** | Extend backtest period to 2008-2024 (16 years for crisis coverage) | PENDING | Batch X23 — Edge case handling | Pass 40 | - |
| **DECISION-159** | Regulatory event handler (SEC/DOJ investigations, sanctions) | PENDING | Batch X23 — Edge case handling | Pass 40 | - |
| **DECISION-160** | Multi-vendor fallback chain per data source | PENDING | Batch X23 — Edge case handling | Pass 40 | - |
| **DECISION-161** | Decision dependency graph (DAG) | PENDING | Batch X24 — Decision management | Pass 41 | - |
| **DECISION-162** | Per-decision time-to-approve estimate + owner-approval-budget tracking | RESOLVED | Batch X24 — Decision management | Pass 41 | 42 |
| **DECISION-163** | Implementation cost estimate per pending decision | PENDING | Batch X24 — Decision management | Pass 41 | - |
| **DECISION-164** | Pairwise tradeoff matrix between decision batches (impact vs cost) | RESOLVED | Batch X24 — Decision management | Pass 41 | 42 |
| **DECISION-165** | Solo PR review checklist before merge to main — Skip — solo dev project, CHECKLIST already | SUPERSEDED | Batch X25 — Process workflow | Pass 41 | 43 |
| **DECISION-166** | HANDOFF.md template specification — HANDOFF template — build when activated by owner | PENDING | Batch X25 — Process workflow | Pass 41 | - |
| **DECISION-167** | Retrospective cadence (every N audit passes) — Retrospective cadence: every 10 audit passe | RESOLVED | Batch X25 — Process workflow | Pass 41 | 43 |
| **DECISION-168** | Incident postmortem template — Incident postmortem template — build at first incident | PENDING | Batch X25 — Process workflow | Pass 41 | - |
| **DECISION-169** | Owner skills gap audit (statistical, SRE, tax, etc.) — Owner self-assesses skills gap (not | PENDING | Batch X26 — Skills | Pass 41 | - |
| **DECISION-170** | Type hints + mypy in CI | PENDING | Batch X27 — Code quality | Pass 41 | - |
| **DECISION-171** | Docstring standard + sphinx documentation | PENDING | Batch X27 — Code quality | Pass 41 | - |
| **DECISION-172** | All numerical constants extracted to config | PENDING | Batch X27 — Code quality | Pass 41 | - |
| **DECISION-173** | Adopt ruff + black + isort + mypy as CI gates | PENDING | Batch X27 — Code quality | Pass 41 | - |
| **DECISION-174** | Strategy classification by trigger type (catalyst/technical/stat-arb) | PENDING | Batch X28 — Strategy meta | Pass 41 | - |
| **DECISION-175** | Signal persistence weighting (consecutive-day signals) | PENDING | Batch X28 — Strategy meta | Pass 41 | - |
| **DECISION-176** | Meta-strategies (boolean AND/OR combinations of base strategies) | PENDING | Batch X28 — Strategy meta | Pass 41 | - |
| **DECISION-177** | Explicit random seed in every backtest run output (reproducibility test) | PENDING | Batch X29 — Reproducibility | Pass 41 | - |
| **DECISION-178** | Signal lookup performance benchmark + caching strategy | PENDING | Batch X29 — Reproducibility | Pass 41 | - |
| **DECISION-179** | Memory profiling per backtest run + memory cap enforcement | PENDING | Batch X29 — Reproducibility | Pass 41 | - |
| **DECISION-180** | Pre-market and open-of-day operational checklist | PENDING | Batch X30 — Live trading ops | Pass 41 | - |
| **DECISION-181** | End-of-day reconciliation report (positions/P&L/agents/regime) | PENDING | Batch X30 — Live trading ops | Pass 41 | - |
| **DECISION-182** | Weekly auto-generated performance review | PENDING | Batch X30 — Live trading ops | Pass 41 | - |
| **DECISION-183** | Memoization layer for signal computation (LRU cache) | PENDING | Batch X31 — Performance optimization | Pass 41 | - |
| **DECISION-184** | Parallel backtest execution for Stage 1 baseline | PENDING | Batch X31 — Performance optimization | Pass 41 | - |
| **DECISION-185** | Incremental backtest updates for daily data refresh | PENDING | Batch X31 — Performance optimization | Pass 41 | - |
| **DECISION-187** | Two-property web architecture: public recommendations site + private analytics dashboard | RESOLVED | Website Architecture | Pass 43 | 43 |
| **DECISION-188** | Public site card-based layout with track record header (Sections A/B: Today + Yesterday) | RESOLVED | Website Architecture | Pass 43 | 43 |
| **DECISION-189** | Trade rationale 10-point depth standard (trigger/strategy/setup/smart-money/macro/agent/ri | RESOLVED | Website Architecture | Pass 43 | 43 |
| **DECISION-190** | Mobile-first design priority for both sites | RESOLVED | Website Architecture | Pass 43 | 43 |
| **DECISION-191** | Publish timing: pre-market 7-8am ET (tomorrow trades) + post-close 4pm ET (results) | RESOLVED | Website Architecture | Pass 43 | 43 |
| **DECISION-192** | Site shows actual paper trades with slippage, not theoretical recommendations | RESOLVED | Website Architecture | Pass 43 | 43 |
| **DECISION-193** | Open positions displayed on results page with mark-to-market unrealized P&L | RESOLVED | Website Architecture | Pass 43 | 43 |
| **DECISION-194** | Push alert events: stops, circuit breakers, halts, daily P&L breach (-2%/-5%), backtest-pa | RESOLVED | Notifications | Pass 43 | 43 |
| **DECISION-195** | Telegram bot for push alerts (vs SMS — free, richer formatting) | RESOLVED | Notifications | Pass 43 | 43 |
| **DECISION-196** | No authentication on paper-trading analytics dashboard; revisit before live trading | RESOLVED | Website Architecture | Pass 43 | 43 |
| **DECISION-197** | Hosting: Vercel for both web properties (free tier, mobile-optimized); backend on Codespac | RESOLVED | Website Architecture | Pass 43 | 43 |
| **DECISION-198** | Paper trading mirrors live algo exactly — same logic, sizing, risk rules, exits, breakers  | RESOLVED | Project Axioms | Pass 43 | 43 |
| **DECISION-199** | Dashboard 1 detailed spec (Phase 1B-α backtest analysis) | PENDING | Dashboard Specifications | Pass 44 | - |
| **DECISION-200** | Dashboard 2 detailed spec (Phase 0.D ICT/SMC signal audit) | PENDING | Dashboard Specifications | Pass 44 | - |
| **DECISION-201** | Dashboard 3 detailed spec (Stage 2 agent overlay analysis) | PENDING | Dashboard Specifications | Pass 44 | - |
| **DECISION-202** | Dashboard 4 detailed spec (Stage 3 paper trading analytics) | PENDING | Dashboard Specifications | Pass 44 | - |
| **DECISION-203** | Dashboard 5 detailed spec (Stage 4 live trading analytics) | PENDING | Dashboard Specifications | Pass 44 | - |
| **DECISION-204** | Dashboard 6 detailed spec (cross-phase comparison waterfall) | PENDING | Dashboard Specifications | Pass 44 | - |
| **DECISION-205** | A/B test arm design — minimum 4 arms (rules, full-agents, no-Risk, no-Bull-Bear) | PENDING | Batch X32 — Agent A/B Testing | Pass 45 | - |
| **DECISION-206** | Paired A/B design — every trade evaluated by every arm in parallel | PENDING | Batch X32 — Agent A/B Testing | Pass 45 | - |
| **DECISION-207** | Pre-commit minimum sample size per arm (300 paired trades) before declaring winner | PENDING | Batch X32 — Agent A/B Testing | Pass 45 | - |
| **DECISION-208** | Multi-metric A/B comparison (Sharpe + Sortino + DD + win rate + PF + CVaR + cost) | PENDING | Batch X32 — Agent A/B Testing | Pass 45 | - |
| **DECISION-209** | Per-regime A/B verdicts — agents pass/fail separately per regime | PENDING | Batch X32 — Agent A/B Testing | Pass 45 | - |
| **DECISION-210** | Net Sharpe contribution accounting (gross lift minus annualized agent cost) | PENDING | Batch X32 — Agent A/B Testing | Pass 45 | - |
| **DECISION-211** | Per-agent ablation studies (drop each agent one at a time) | PENDING | Batch X32 — Agent A/B Testing | Pass 45 | - |
| **DECISION-212** | Agent-disagreement decomposition (Bull vs Bear, Risk override) — testable hypotheses | PENDING | Batch X32 — Agent A/B Testing | Pass 45 | - |
| **DECISION-213** | Both-rationales storage (rules-only AND agent rationale stored every trade) | PENDING | Batch X32 — Agent A/B Testing | Pass 45 | - |
| **DECISION-214** | Quarterly re-validation of agent A/B test (model drift / cost drift) | PENDING | Batch X32 — Agent A/B Testing | Pass 45 | - |
| **DECISION-215** | A/B test result registry (structured artifacts versioned in repo) | PENDING | Batch X32 — Agent A/B Testing | Pass 45 | - |
| **DECISION-216** | A/B test orchestrator code module (parallel arms with deterministic seeds) | PENDING | Batch X32 — Agent A/B Testing | Pass 45 | - |
| **DECISION-217** | Audit and remove dead code (engine.py vs engine/backtest.py duplication etc.) | PENDING | Batch X33 — Architecture Hygiene | Pass 45 | - |
| **DECISION-218** | Documentation audit — role of EXPLANATION/PROGRESS/UNIVERSAL_LEARNINGS, README content | PENDING | Batch X33 — Architecture Hygiene | Pass 45 | - |
| **DECISION-219** | GitHub Actions audit — security, schedule, failure alerting, idempotency | PENDING | Batch X33 — Architecture Hygiene | Pass 45 | - |
| **DECISION-220** | Audit sync_from_claude.yml — disable if it bypasses owner approval | PENDING | Batch X33 — Architecture Hygiene | Pass 45 | - |
| **DECISION-221** | Test coverage measurement (pytest --cov) + CI gate | PENDING | Batch X34 — Test + Cache Infrastructure | Pass 45 | - |
| **DECISION-222** | Test naming and structure audit; regression tests for top-20 critical bugs | PENDING | Batch X34 — Test + Cache Infrastructure | Pass 45 | - |
| **DECISION-223** | CI gate — PR cannot merge to main without all tests passing | PENDING | Batch X34 — Test + Cache Infrastructure | Pass 45 | - |
| **DECISION-224** | Cache concurrency audit (filelock under concurrent access) | PENDING | Batch X34 — Test + Cache Infrastructure | Pass 45 | - |
| **DECISION-225** | Cache eviction policy (preserve prefetched, evict only computed) | PENDING | Batch X34 — Test + Cache Infrastructure | Pass 45 | - |
| **DECISION-226** | Cache schema versioning (every parquet has schema_version metadata) | PENDING | Batch X34 — Test + Cache Infrastructure | Pass 45 | - |
| **DECISION-227** | Cache size monitoring + alerting (cache_size_gb metric, 80% disk alert) | PENDING | Batch X34 — Test + Cache Infrastructure | Pass 45 | - |
| **DECISION-228** | Fetcher reliability audit (retry/rate-limit/idempotency per API) | PENDING | Batch X35 — Reliability + Determinism | Pass 45 | - |
| **DECISION-229** | Config management upgrade (pydantic + env overrides + change log) | PENDING | Batch X35 — Reliability + Determinism | Pass 45 | - |
| **DECISION-230** | Logging audit + standard (structured JSON, rotation, level standardization) | PENDING | Batch X35 — Reliability + Determinism | Pass 45 | - |
| **DECISION-231** | Audit all except Exception patterns; ensure WARNING+ logging with context | PENDING | Batch X35 — Reliability + Determinism | Pass 45 | - |
| **DECISION-232** | Determinism test (run identical backtest twice, diff outputs) | PENDING | Batch X35 — Reliability + Determinism | Pass 45 | - |
| **DECISION-233** | Daily data quality monitoring (per-ticker NaN/missing/anomaly detection) | PENDING | Batch X36 — Data Quality + Trading Mechanics | Pass 45 | - |
| **DECISION-234** | Ticker lifecycle event handler (CUSIP/ISIN tracking across renames/mergers) | PENDING | Batch X36 — Data Quality + Trading Mechanics | Pass 45 | - |
| **DECISION-235** | Time/calendar handling spec (NYSE calendar, holidays, DST, half-days) | PENDING | Batch X36 — Data Quality + Trading Mechanics | Pass 45 | - |
| **DECISION-236** | Position sizing precision rules (round to broker minimum increment) | PENDING | Batch X36 — Data Quality + Trading Mechanics | Pass 45 | - |
| **DECISION-237** | Order type policy (when MOO vs limit vs stop vs stop-limit) | PENDING | Batch X36 — Data Quality + Trading Mechanics | Pass 45 | - |
| **DECISION-238** | Pre/after-hours policy (recommendation: NO extended hours) | PENDING | Batch X36 — Data Quality + Trading Mechanics | Pass 45 | - |
| **DECISION-239** | Multi-account architecture (TFSA/RRSP/Margin future-proofing) | PENDING | Batch X36 — Data Quality + Trading Mechanics | Pass 45 | - |
| **DECISION-240** | Alert tuning — configurable thresholds per event + rate tracking | PENDING | Batch X36 — Data Quality + Trading Mechanics | Pass 45 | - |
| **DECISION-241** | Time-in-market metric (% in any position, % long, % short, % cash) | PENDING | Batch X36 — Data Quality + Trading Mechanics | Pass 45 | - |
| **DECISION-242** | Distribution analysis (skewness, kurtosis, max single-trade contribution) | PENDING | Batch X36 — Data Quality + Trading Mechanics | Pass 45 | - |
| **DECISION-243** | Owner Approval Queue file (pending decisions waiting on owner reply, by age) | PENDING | Batch X37 — Process / Owner Experience | Pass 45 | - |
| **DECISION-244** | SESSION_START.md — Claude reads first in any new session for fast onboarding | PENDING | Batch X37 — Process / Owner Experience | Pass 45 | - |
| **DECISION-245** | Owner experience retrospective (periodic check-in on workflow productivity) | PENDING | Batch X37 — Process / Owner Experience | Pass 45 | - |
| **DECISION-246** | Quant finance correctness audit (Sharpe annualization, DD computation, vol periodicity) | PENDING | Batch X38 — Knowledge Gaps | Pass 45 | - |
| **DECISION-247** | Stats/ML implementation review (HMM, deflated Sharpe, Kelly — validate against known resul | PENDING | Batch X38 — Knowledge Gaps | Pass 45 | - |
| **DECISION-248** | Owner pre-commitment doc (rules owner commits to before losses) | PENDING | Batch X38 — Knowledge Gaps | Pass 45 | - |
| **DECISION-249** | Strategy decay metric (rolling 6mo Sharpe per strategy; flag >50% drop) | PENDING | Batch X39 — Strategy Decay + Code Quality | Pass 45 | - |
| **DECISION-250** | Edge decay assumption (discount backtest Sharpe by expected crowding %) | PENDING | Batch X39 — Strategy Decay + Code Quality | Pass 45 | - |
| **DECISION-251** | Dependency injection audit (refactor for testability with mocks) | PENDING | Batch X39 — Strategy Decay + Code Quality | Pass 45 | - |
| **DECISION-252** | Explicit commission model in backtest using real IBKR pricing tables (Tiered + Fixed, with | PENDING | Batch X40 — Cost Modeling Accuracy | Pass 46 | - |
| **DECISION-253** | Routing decision for interlisted securities: evaluate TSX-CAD vs US-NYSE per trade based o | PENDING | Batch X40 — Cost Modeling Accuracy | Pass 46 | - |
| **DECISION-254** | ETF substitution for index strategies: SPY/QQQ/IWM trades evaluate TSX-CAD equivalents (XS | PENDING | Batch X40 — Cost Modeling Accuracy | Pass 46 | - |
| **DECISION-255** | Norbert's Gambit at funding: use DLR.TO/DLR.U.TO for CAD->USD conversion when capital move | PENDING | Batch X40 — Cost Modeling Accuracy | Pass 46 | - |
| **DECISION-256** | Earnings calendar prefetch (datetime + EPS surprise data) per ticker per quarter | PENDING | Batch X41 — Phase 0.A Data Prefetch Gaps | Pass 47 | - |
| **DECISION-257** | Quarterly fundamentals prefetch — explicit field/source/PIT inventory | PENDING | Batch X41 — Phase 0.A Data Prefetch Gaps | Pass 47 | - |
| **DECISION-258** | Options chain snapshot cache (OI + IV + put-call ratio) per ticker per day | PENDING | Batch X41 — Phase 0.A Data Prefetch Gaps | Pass 47 | - |
| **DECISION-259** | ICT/SMC signal pre-computation cache (FVG/BOS/CHoCH/order blocks) | PENDING | Batch X41 — Phase 0.A Data Prefetch Gaps | Pass 47 | - |
| **DECISION-260** | Cache freshness assertion — refuse to backtest beyond cache end-date per ticker | PENDING | Batch X41 — Phase 0.A Data Prefetch Gaps | Pass 47 | - |
| **DECISION-261** | ICT/SMC PIT rules — minimum lag from pattern completion to actionable signal | PENDING | Batch X41 — Phase 0.A Data Prefetch Gaps | Pass 47 | - |
| **DECISION-262** | 10-candidate-cap rationale — keep, raise, or make conditional | PENDING | Batch X42 — Phase 1B-α Stress | Pass 47 | - |
| **DECISION-263** | Burst-day stress test — re-run high-volatility days, verify no silent drops | PENDING | Batch X42 — Phase 1B-α Stress | Pass 47 | - |
| **DECISION-264** | Walk-forward window count — given current data, ensure adequate OOS testing | PENDING | Batch X42 — Phase 1B-α Stress | Pass 47 | - |
| **DECISION-265** | Smoke test power analysis — minimum candidates for ENTER/SKIP statistical distinguishabili | PENDING | Batch X42 — Phase 1B-α Stress | Pass 47 | - |
| **DECISION-266** | Data history extension — push backtest start from 2020 to 2010 for proper walk-forward + h | PENDING | Batch X43 — Data History | Pass 47 | - |
| **DECISION-267** | Trade event store schema — fields per trade + storage format (SQLite paper, Postgres live) | PENDING | Batch X44 — Paper Trading Infrastructure | Pass 47 | - |
| **DECISION-268** | Paper-vs-backtest comparison methodology — Bayesian posterior over Sharpe | PENDING | Batch X44 — Paper Trading Infrastructure | Pass 47 | - |
| **DECISION-269** | Stage 4 entry criteria — explicit numeric gates (Sharpe/DD/win-rate/A-B-clear/divergence) | PENDING | Batch X45 — Stage 4 Live | Pass 47 | - |
| **DECISION-270** | Pre-Stage-4 CPA consultation — formal opinion on trading business classification | PENDING | Batch X45 — Stage 4 Live | Pass 47 | - |
| **DECISION-271** | Real-time data feed cost — explicit Stage 4+ line item (IBKR market data subs) | PENDING | Batch X45 — Stage 4 Live | Pass 47 | - |
| **DECISION-272** | Stage 4 hosting migration plan — target platform, deployment, monitoring, secrets, cost | PENDING | Batch X46 — Stage 5 Operational | Pass 47 | - |
| **DECISION-273** | Disaster recovery plan — broker-side stops, heartbeat monitoring, manual override | PENDING | Batch X46 — Stage 5 Operational | Pass 47 | - |
| **DECISION-274** | sync_from_claude.yml conflict policy — fail on conflict instead of silent --strategy=their | PENDING | Batch X47 — Code Defects | Pass 47 | - |
| **DECISION-275** | requirements.txt audit + completeness (openai/tradingagents/fredapi missing) | PENDING | Batch X47 — Code Defects | Pass 47 | - |
| **DECISION-276** | OMS layer or use IBKR algos? Integrate IBKR TWAP/VWAP rather than rolling own | PENDING | Batch X48 — Professional Benchmark Gaps | Pass 47 | - |
| **DECISION-277** | Per-strategy promotion workflow — each of 72 strategies has independent stage | PENDING | Batch X48 — Professional Benchmark Gaps | Pass 47 | - |
| **DECISION-278** | Internal trade journal schema — chart snapshot, agent transcripts, signal raw values, regi | PENDING | Batch X48 — Professional Benchmark Gaps | Pass 47 | - |
| **DECISION-279** | P&L decomposition — separate (signal/timing/exit/sizing/agent) contributions | PENDING | Batch X48 — Professional Benchmark Gaps | Pass 47 | - |
| **DECISION-280** | Time-of-day slippage adjustment — first/last 30 min higher slippage | PENDING | Batch X48 — Professional Benchmark Gaps | Pass 47 | - |
| **DECISION-281** | Tax data architecture — design now, populate from Day 1 of paper trading | PENDING | Batch X49 — Thin Areas Surfaced | Pass 47 | - |
| **DECISION-282** | Notification cascade — Telegram primary, Email fallback, SMS for critical breaker events | PENDING | Batch X49 — Thin Areas Surfaced | Pass 47 | - |
| **DECISION-283** | Backtest output schema — explicit columns/types/nullability/post-conditions, versioned | PENDING | Batch X49 — Thin Areas Surfaced | Pass 47 | - |
| **DECISION-284** | Borderline strategy handling — explicit policy at threshold edge cases | PENDING | Batch X49 — Thin Areas Surfaced | Pass 47 | - |
| **DECISION-285** | Mid-hold agent re-evaluation — does live agent re-rate open positions? | PENDING | Batch X49 — Thin Areas Surfaced | Pass 47 | - |
| **DECISION-286** | Wealthsimple replication tracking — log owner-placed manual trades, compute exec-quality v | PENDING | Batch X49 — Thin Areas Surfaced | Pass 47 | - |
| **DECISION-287** | Public site failure handling + freshness signal (last-updated timestamp prominent) | PENDING | Batch X49 — Thin Areas Surfaced | Pass 47 | - |
| **DECISION-288** | Legal review of public site — registration check, disclaimer, liability terms BEFORE publi | PENDING | Batch X49 — Thin Areas Surfaced | Pass 47 | - |
| **DECISION-289** | Owner-absent contingency — backup contact, POA, vacation-mode auto-flatten | PENDING | Batch X49 — Thin Areas Surfaced | Pass 47 | - |
| **DECISION-290** | Dropped strategy re-evaluation cadence (every 6 months re-test, re-admit if Sharpe restore | PENDING | Batch X49 — Thin Areas Surfaced | Pass 47 | - |
| **DECISION-291** | Triage-based bulk approval — owner approves entire impact-ratio band in single message | PENDING | Batch X50 — Process Improvements | Pass 47 | - |
| **DECISION-292** | Decision→CHECKLIST migration audit (quarterly, RESOLVED decisions to process rules) | PENDING | Batch X50 — Process Improvements | Pass 47 | - |
| **DECISION-293** | Fix close_trade `days` NameError — confirmed runtime crash via execution. Reorder `pnl = _ | RESOLVED | Batch X51 — CRITICAL Runtime Bugs | Pass 48 | 49 |
| **DECISION-294** | Remove duplicate ClosedTrade dataclass definition in exit_manager.py — pick canonical, del | RESOLVED | Batch X51 — CRITICAL Runtime Bugs | Pass 48 | 49 |
| **DECISION-295** | Reconcile SHORT_BORROW_COST_PER_DAY units — 0.005 ambiguous (per-day decimal vs per-day pe | RESOLVED | Batch X51 — CRITICAL Runtime Bugs | Pass 48 | 50 |
| **DECISION-296** | Fix test_e2e fixture — engine fixture undefined, 7 of 8 e2e tests ERROR at setup | RESOLVED | Batch X51 — CRITICAL Runtime Bugs | Pass 48 | 49 |
| **DECISION-297** | Add unit test for close_trade — would have caught the days bug; same for any function in c | RESOLVED | Batch X51 — CRITICAL Runtime Bugs | Pass 48 | 49 |
| **DECISION-298** | Cache stores adjusted-close (auto_adjust=True) which changes over time as splits/dividends | PENDING | Batch X52 — CRITICAL PIT Correctness | Pass 48 | - |
| **DECISION-299** | yfinance fetch_info returns CURRENT sector/mkt_cap/IPO date regardless of as_of — full his | PENDING | Batch X52 — CRITICAL PIT Correctness | Pass 48 | - |
| **DECISION-300** | yfinance earnings_dates and analyst data return CURRENT values not as-of — replace with PI | PENDING | Batch X52 — CRITICAL PIT Correctness | Pass 48 | - |
| **DECISION-301** | FRED data revisions completely unhandled — switch to ALFRED (archival FRED) for vintage da | RESOLVED | Batch X52 — CRITICAL PIT Correctness | Pass 48 | 50 |
| **DECISION-302** | VXX used as VIX proxy + UUP used as DXY proxy — quantify tracking error or replace with ac | RESOLVED | Batch X52 — CRITICAL PIT Correctness | Pass 48 | 50 |
| **DECISION-303** | S&P 500 constituent list is current membership applied retroactively — survivorship bias;  | PENDING | Batch X52 — CRITICAL PIT Correctness | Pass 48 | - |
| **DECISION-304** | CPI/NFP/FOMC dates hardcoded through March 2026 only — auto-extend from FRED FOMC + BLS sc | RESOLVED | Batch X52 — CRITICAL PIT Correctness | Pass 48 | 50 |
| **DECISION-305** | PIT guard `_assert_no_lookahead` logs WARNING but doesn't RAISE — switch to RAISE in backt | RESOLVED | Batch X52 — CRITICAL PIT Correctness | Pass 48 | 50 |
| **DECISION-306** | get_news_sentiment path mismatch — code reads /prefetch/news/ but data lives in /cache/fin | RESOLVED | Batch X52 — CRITICAL PIT Correctness | Pass 48 | 49 |
| **DECISION-307** | Cache get_ohlcv front-extension missing — only fetches missing TAIL; if user requests star | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-308** | Cache get_ohlcv_bulk requires >=20 trading days — silently rejects valid cache for shorter | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-309** | Cache ticker collision: BRK-B and (hypothetical) BRK.B both map to BRK_B.parquet — silent  | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | 51 |
| **DECISION-310** | Cache writes zero-volume days dropped silently (df[volume>0]) — halted/suspended stocks in | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-311** | Trailing-stop ATR exits use ENTRY-time ATR throughout hold period — should refresh daily;  | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | 51 |
| **DECISION-312** | exit_hybrid_50pct has max_days=252 but 11 other exits don't — comparison metrics not apple | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | 51 |
| **DECISION-313** | update_trailing_stop ignores intraday HIGH — stop only updates at close above prior best;  | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-314** | Circuit breakers levels 3 and 4 (intraday halt, market halt) documented but NOT implemente | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-315** | Circuit breakers checked one-at-a-time — if Level 1 + Level 5 both fire same day, Level 5  | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | 51 |
| **DECISION-316** | Regime classifier returns 'neutral' default on missing VIX — should refuse to trade with n | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | 51 |
| **DECISION-317** | VIX hard thresholds (40/30/20) flip regime on single print — needs MA smoothing | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-318** | AAII pub-lag treatment missing — survey data marked available on survey-Wed, actually publ | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-319** | AAII auto-refresh missing — committed CSV will go stale, no refresh script in /scripts or  | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-320** | CNN F&G CSV interpolated between key readings — fabricated values used as PIT signal | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-321** | Liquidity filter market-cap check skips silently if data missing — fail-open instead of fa | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-322** | Market cap from yfinance.info CURRENT not historical — backtesting 2020 trades uses 2026 m | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-323** | Sector reclassifications retro-applied — Meta moved from Comms to Tech; 2020 backtests use | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-324** | Congressional weight by disclosure_date not transaction_date — smart-money signal weighted | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | 51 |
| **DECISION-325** | Institutional 13F PIT assumes universal on-time filing — late filers (some big funds) invi | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-326** | Walk-forward windows hardcoded calendar dates — no rolling logic per DEC-109; stale after  | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-327** | Short-borrow cost duplicated across improvements.py + exit_manager.py with different units | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-328** | Cache filelock fallback writes silently if lock unavailable — concurrent writes can corrup | PENDING | Batch X54 — Medium-Severity Improvements | Pass 48 | - |
| **DECISION-329** | Module-level global caches (VIX, DXY, AAII, CNN F&G) not multi-process safe | PENDING | Batch X54 — Medium-Severity Improvements | Pass 48 | - |
| **DECISION-330** | Cache schema not versioned — schema changes silently mix old + new parquet | PENDING | Batch X54 — Medium-Severity Improvements | Pass 48 | - |
| **DECISION-331** | ETF list fragmented (ETFS in config.py 17 items, ETFS_FULL in universe.py 25 items, ETF_TI | PENDING | Batch X54 — Medium-Severity Improvements | Pass 48 | - |
| **DECISION-332** | Smart money composite scoring weights (4/2/-3 etc) hardcoded magic — move to config with d | PENDING | Batch X54 — Medium-Severity Improvements | Pass 48 | - |
| **DECISION-333** | Sentiment thresholds (AAII 55/45, CNN F&G 20/35/65/80) don't match CNN's published bands | PENDING | Batch X54 — Medium-Severity Improvements | Pass 48 | - |
| **DECISION-334** | composite_score uses win_rate as ROI proxy — replace with actual ROI | PENDING | Batch X54 — Medium-Severity Improvements | Pass 48 | - |
| **DECISION-335** | composite_score weights (40/30/30) hardcoded — make configurable | PENDING | Batch X54 — Medium-Severity Improvements | Pass 48 | - |
| **DECISION-336** | info_cache.json never refreshed — stale market caps persist project-lifetime | PENDING | Batch X54 — Medium-Severity Improvements | Pass 48 | - |
| **DECISION-337** | update_trailing_stop ignores intraday extremes for stop placement; fix to track highs and  | PENDING | Batch X54 — Medium-Severity Improvements | Pass 48 | - |
| **DECISION-338** | Conversion logic (short→long in bull regime) creates label only; no actual long opened — d | PENDING | Batch X54 — Medium-Severity Improvements | Pass 48 | - |
| **DECISION-339** | pnl_dollar hardcoded $10K notional — wrong for $5K paper / $50K next stage / $1K live | PENDING | Batch X54 — Medium-Severity Improvements | Pass 48 | - |
| **DECISION-340** | get_correlation_matrix silently drops tickers with <20 history — variable corr-matrix memb | PENDING | Batch X54 — Medium-Severity Improvements | Pass 48 | - |
| **DECISION-341** | universe.py docstring claims Wikipedia fetch but code uses static CSV — fix docstring or i | PENDING | Batch X55 — Documentation Sync | Pass 48 | - |
| **DECISION-342** | Test pass-rate mis-reported — only 38 of 46 tests run cleanly (7 e2e errors); update repor | PENDING | Batch X55 — Documentation Sync | Pass 48 | - |
| **DECISION-343** | Pandas-ta deprecation warning on pandas 4.0 — plan replacement (TA-Lib alternative) | PENDING | Batch X55 — Documentation Sync | Pass 48 | - |
| **DECISION-344** | Slippage threshold ATR/price > 3% likely too high — most S&P large caps never trigger | PENDING | Batch X55 — Documentation Sync | Pass 48 | - |

---

### Pending Decisions by Theme

**Batch X1 — Data + Universe** (8):

- **DECISION-063**: Universe refresh automation
- **DECISION-064**: Phase 0.A prefetch checklist
- **DECISION-065**: Validate stored data quality before Phase 1B-α
- **DECISION-099**: 11 missing strategy categories (Pairs, Calendar, Cross-Asset, Index Rebalance, etc.)
- **DECISION-101**: Earnings strategies post-Phase 0.A
- **DECISION-103**: Auto-populate Tier 2 universe (spinoffs, IPOs, $5B+)
- **DECISION-104**: Auto-populate Tier 3 momentum watchlist
- **DECISION-105**: Spinoff detector

**Batch X10 — Trade explainability** (2):

- **DECISION-119**: Per-trade explainability dict (primary_signal, dominant_multiplier, agent_tier_delta)
- **DECISION-120**: Automatic loss attribution report — top 10 losing trades per strategy with full context

**Batch X11 — Exit comparison** (2):

- **DECISION-121**: Exit comparison report includes side-by-side exit dates/prices
- **DECISION-122**: Per-exit-method slippage modeling

**Batch X12 — Smart money refinement** (3):

- **DECISION-123**: Apply exponential decay to smart money signal weights
- **DECISION-124**: Cross-source smart money clusters (insider+congressional+13F confluence)
- **DECISION-125**: Add Form 144 prefetch (proposed sales — leading indicator)

**Batch X13 — Circuit breakers extension** (2):

- **DECISION-127**: Define recovery rules from each circuit breaker level (cooldown, hysteresis)
- **DECISION-128**: Dispersion-conditional circuit breaker

**Batch X14 — Validation criteria** (4):

- **DECISION-129**: Live-vs-backtest Sharpe equivalence criterion (within 0.3 to pass Stage 3)
- **DECISION-130**: Capacity stress test (5x capital, Sharpe drop <0.3)
- **DECISION-131**: Agent value-add minimum (Sharpe improvement >=0.2 over rules-only)
- **DECISION-132**: Annual Sharpe variance < 0.5 stability requirement

**Batch X15 — Risk management deeper** (4):

- **DECISION-133**: Max gross long/short/net exposure caps
- **DECISION-134**: USD/CAD currency exposure tracking + optional FX hedge
- **DECISION-135**: Per-ticker cumulative max-loss cap (rolling 30-day)
- **DECISION-136**: Portfolio rebalancing frequency policy

**Batch X16 — Architecture extension** (4):

- **DECISION-137**: Backtest output schema versioning + migration path
- **DECISION-138**: Cold-start CI test (fresh container in <30 min)
- **DECISION-139**: Remote kill switch (email-based STOP)
- **DECISION-140**: Structured JSON logging standard

**Batch X17 — Strategy extensions** (5):

- **DECISION-141**: Sector-neutral hedge overlay (long position + short sector ETF)
- **DECISION-142**: Optional market-neutral construction (long stock + short SPY at beta)
- **DECISION-143**: IPO/lockup/secondary offering systematic framework
- **DECISION-144**: Stock-vs-sector momentum delta as breakdown variable
- **DECISION-145**: IV delta vs historical pre-earnings pattern as signal

**Batch X18 — Universe management** (3):

- **DECISION-146**: Corporate actions handler (split/dividend/spinoff/rename)
- **DECISION-147**: Delisting registry + survivorship bias correction
- **DECISION-148**: Stock-specific adaptive momentum lookback (vol-adjusted)

**Batch X19 — Regime extensions** (3):

- **DECISION-149**: Regime transition probability matrix
- **DECISION-150**: Multi-asset regime detection (equity+credit+commodity+currency)
- **DECISION-151**: Sector-level regime classification

**Batch X20 — IS/OOS extensions** (2):

- **DECISION-152**: Hold-out final test period (never touched during audits)
- **DECISION-153**: Regime-stratified train/test splits

**Batch X21 — Benchmarking** (1):

- **DECISION-155**: vs-SPY comparison in all backtest reports

**Batch X23 — Edge case handling** (4):

- **DECISION-157**: Synthetic broker outage testing during Stage 3 (chaos engineering)
- **DECISION-158**: Extend backtest period to 2008-2024 (16 years for crisis coverage)
- **DECISION-159**: Regulatory event handler (SEC/DOJ investigations, sanctions)
- **DECISION-160**: Multi-vendor fallback chain per data source

**Batch X24 — Decision management** (2):

- **DECISION-161**: Decision dependency graph (DAG)
- **DECISION-163**: Implementation cost estimate per pending decision

**Batch X25 — Process workflow** (2):

- **DECISION-166**: HANDOFF.md template specification — HANDOFF template — build when activated by owner
- **DECISION-168**: Incident postmortem template — Incident postmortem template — build at first incident

**Batch X26 — Skills** (1):

- **DECISION-169**: Owner skills gap audit (statistical, SRE, tax, etc.) — Owner self-assesses skills gap (not for Claude to audit)

**Batch X27 — Code quality** (4):

- **DECISION-170**: Type hints + mypy in CI
- **DECISION-171**: Docstring standard + sphinx documentation
- **DECISION-172**: All numerical constants extracted to config
- **DECISION-173**: Adopt ruff + black + isort + mypy as CI gates

**Batch X28 — Strategy meta** (3):

- **DECISION-174**: Strategy classification by trigger type (catalyst/technical/stat-arb)
- **DECISION-175**: Signal persistence weighting (consecutive-day signals)
- **DECISION-176**: Meta-strategies (boolean AND/OR combinations of base strategies)

**Batch X29 — Reproducibility** (3):

- **DECISION-177**: Explicit random seed in every backtest run output (reproducibility test)
- **DECISION-178**: Signal lookup performance benchmark + caching strategy
- **DECISION-179**: Memory profiling per backtest run + memory cap enforcement

**Batch X3 — Architecture** (9):

- **DECISION-093**: Migrate live to AWS/GCP/DO before Stage 4
- **DECISION-094**: Secrets manager
- **DECISION-095**: Monitoring + alerting
- **DECISION-096**: Backtest reproducibility (code + data + config hash)
- **DECISION-097**: Reconciliation job (daily position vs broker)
- **DECISION-098**: Test coverage 70% before Stage 3
- **DECISION-112**: Disaster recovery plan + incident runbook
- **DECISION-113**: Trade journal + research log + failure log
- **DECISION-114**: Live-vs-backtest divergence monitoring

**Batch X30 — Live trading ops** (3):

- **DECISION-180**: Pre-market and open-of-day operational checklist
- **DECISION-181**: End-of-day reconciliation report (positions/P&L/agents/regime)
- **DECISION-182**: Weekly auto-generated performance review

**Batch X31 — Performance optimization** (3):

- **DECISION-183**: Memoization layer for signal computation (LRU cache)
- **DECISION-184**: Parallel backtest execution for Stage 1 baseline
- **DECISION-185**: Incremental backtest updates for daily data refresh

**Batch X32 — Agent A/B Testing** (12):

- **DECISION-205**: A/B test arm design — minimum 4 arms (rules, full-agents, no-Risk, no-Bull-Bear)
- **DECISION-206**: Paired A/B design — every trade evaluated by every arm in parallel
- **DECISION-207**: Pre-commit minimum sample size per arm (300 paired trades) before declaring winner
- **DECISION-208**: Multi-metric A/B comparison (Sharpe + Sortino + DD + win rate + PF + CVaR + cost)
- **DECISION-209**: Per-regime A/B verdicts — agents pass/fail separately per regime
- **DECISION-210**: Net Sharpe contribution accounting (gross lift minus annualized agent cost)
- **DECISION-211**: Per-agent ablation studies (drop each agent one at a time)
- **DECISION-212**: Agent-disagreement decomposition (Bull vs Bear, Risk override) — testable hypotheses
- **DECISION-213**: Both-rationales storage (rules-only AND agent rationale stored every trade)
- **DECISION-214**: Quarterly re-validation of agent A/B test (model drift / cost drift)
- **DECISION-215**: A/B test result registry (structured artifacts versioned in repo)
- **DECISION-216**: A/B test orchestrator code module (parallel arms with deterministic seeds)

**Batch X33 — Architecture Hygiene** (4):

- **DECISION-217**: Audit and remove dead code (engine.py vs engine/backtest.py duplication etc.)
- **DECISION-218**: Documentation audit — role of EXPLANATION/PROGRESS/UNIVERSAL_LEARNINGS, README content
- **DECISION-219**: GitHub Actions audit — security, schedule, failure alerting, idempotency
- **DECISION-220**: Audit sync_from_claude.yml — disable if it bypasses owner approval

**Batch X34 — Test + Cache Infrastructure** (7):

- **DECISION-221**: Test coverage measurement (pytest --cov) + CI gate
- **DECISION-222**: Test naming and structure audit; regression tests for top-20 critical bugs
- **DECISION-223**: CI gate — PR cannot merge to main without all tests passing
- **DECISION-224**: Cache concurrency audit (filelock under concurrent access)
- **DECISION-225**: Cache eviction policy (preserve prefetched, evict only computed)
- **DECISION-226**: Cache schema versioning (every parquet has schema_version metadata)
- **DECISION-227**: Cache size monitoring + alerting (cache_size_gb metric, 80% disk alert)

**Batch X35 — Reliability + Determinism** (5):

- **DECISION-228**: Fetcher reliability audit (retry/rate-limit/idempotency per API)
- **DECISION-229**: Config management upgrade (pydantic + env overrides + change log)
- **DECISION-230**: Logging audit + standard (structured JSON, rotation, level standardization)
- **DECISION-231**: Audit all except Exception patterns; ensure WARNING+ logging with context
- **DECISION-232**: Determinism test (run identical backtest twice, diff outputs)

**Batch X36 — Data Quality + Trading Mechanics** (10):

- **DECISION-233**: Daily data quality monitoring (per-ticker NaN/missing/anomaly detection)
- **DECISION-234**: Ticker lifecycle event handler (CUSIP/ISIN tracking across renames/mergers)
- **DECISION-235**: Time/calendar handling spec (NYSE calendar, holidays, DST, half-days)
- **DECISION-236**: Position sizing precision rules (round to broker minimum increment)
- **DECISION-237**: Order type policy (when MOO vs limit vs stop vs stop-limit)
- **DECISION-238**: Pre/after-hours policy (recommendation: NO extended hours)
- **DECISION-239**: Multi-account architecture (TFSA/RRSP/Margin future-proofing)
- **DECISION-240**: Alert tuning — configurable thresholds per event + rate tracking
- **DECISION-241**: Time-in-market metric (% in any position, % long, % short, % cash)
- **DECISION-242**: Distribution analysis (skewness, kurtosis, max single-trade contribution)

**Batch X37 — Process / Owner Experience** (3):

- **DECISION-243**: Owner Approval Queue file (pending decisions waiting on owner reply, by age)
- **DECISION-244**: SESSION_START.md — Claude reads first in any new session for fast onboarding
- **DECISION-245**: Owner experience retrospective (periodic check-in on workflow productivity)

**Batch X38 — Knowledge Gaps** (3):

- **DECISION-246**: Quant finance correctness audit (Sharpe annualization, DD computation, vol periodicity)
- **DECISION-247**: Stats/ML implementation review (HMM, deflated Sharpe, Kelly — validate against known results)
- **DECISION-248**: Owner pre-commitment doc (rules owner commits to before losses)

**Batch X39 — Strategy Decay + Code Quality** (3):

- **DECISION-249**: Strategy decay metric (rolling 6mo Sharpe per strategy; flag >50% drop)
- **DECISION-250**: Edge decay assumption (discount backtest Sharpe by expected crowding %)
- **DECISION-251**: Dependency injection audit (refactor for testability with mocks)

**Batch X4 — Statistical Methodology** (8):

- **DECISION-080**: t-stat + Bonferroni
- **DECISION-081**: Sharpe + Sortino + transaction cost sensitivity
- **DECISION-082**: Stress-test pass requirements (2008/2020/2022)
- **DECISION-083**: Min trades floor 300 independent positions
- **DECISION-085**: Define macro correlation precisely
- **DECISION-109**: Rolling 5yr/1yr walk-forward
- **DECISION-110**: Deflated Sharpe (Bailey et al.)
- **DECISION-111**: Stationarity / structural break tests

**Batch X40 — Cost Modeling Accuracy** (4):

- **DECISION-252**: Explicit commission model in backtest using real IBKR pricing tables (Tiered + Fixed, with 1% / 0.5% caps, third-party fees) — not flat per-share
- **DECISION-253**: Routing decision for interlisted securities: evaluate TSX-CAD vs US-NYSE per trade based on commission cap + FX cost + liquidity + tax treatment
- **DECISION-254**: ETF substitution for index strategies: SPY/QQQ/IWM trades evaluate TSX-CAD equivalents (XSP/XQQ/XSU, VFV unhedged, etc.) on hedging-cost vs FX-cost vs commission-cap basis
- **DECISION-255**: Norbert's Gambit at funding: use DLR.TO/DLR.U.TO for CAD->USD conversion when capital moved to IBKR; document one-time savings; not per-trade relevant

**Batch X41 — Phase 0.A Data Prefetch Gaps** (6):

- **DECISION-256**: Earnings calendar prefetch (datetime + EPS surprise data) per ticker per quarter
- **DECISION-257**: Quarterly fundamentals prefetch — explicit field/source/PIT inventory
- **DECISION-258**: Options chain snapshot cache (OI + IV + put-call ratio) per ticker per day
- **DECISION-259**: ICT/SMC signal pre-computation cache (FVG/BOS/CHoCH/order blocks)
- **DECISION-260**: Cache freshness assertion — refuse to backtest beyond cache end-date per ticker
- **DECISION-261**: ICT/SMC PIT rules — minimum lag from pattern completion to actionable signal

**Batch X42 — Phase 1B-α Stress** (4):

- **DECISION-262**: 10-candidate-cap rationale — keep, raise, or make conditional
- **DECISION-263**: Burst-day stress test — re-run high-volatility days, verify no silent drops
- **DECISION-264**: Walk-forward window count — given current data, ensure adequate OOS testing
- **DECISION-265**: Smoke test power analysis — minimum candidates for ENTER/SKIP statistical distinguishability

**Batch X43 — Data History** (1):

- **DECISION-266**: Data history extension — push backtest start from 2020 to 2010 for proper walk-forward + hold-out

**Batch X44 — Paper Trading Infrastructure** (2):

- **DECISION-267**: Trade event store schema — fields per trade + storage format (SQLite paper, Postgres live)
- **DECISION-268**: Paper-vs-backtest comparison methodology — Bayesian posterior over Sharpe

**Batch X45 — Stage 4 Live** (3):

- **DECISION-269**: Stage 4 entry criteria — explicit numeric gates (Sharpe/DD/win-rate/A-B-clear/divergence)
- **DECISION-270**: Pre-Stage-4 CPA consultation — formal opinion on trading business classification
- **DECISION-271**: Real-time data feed cost — explicit Stage 4+ line item (IBKR market data subs)

**Batch X46 — Stage 5 Operational** (2):

- **DECISION-272**: Stage 4 hosting migration plan — target platform, deployment, monitoring, secrets, cost
- **DECISION-273**: Disaster recovery plan — broker-side stops, heartbeat monitoring, manual override

**Batch X47 — Code Defects** (2):

- **DECISION-274**: sync_from_claude.yml conflict policy — fail on conflict instead of silent --strategy=theirs
- **DECISION-275**: requirements.txt audit + completeness (openai/tradingagents/fredapi missing)

**Batch X48 — Professional Benchmark Gaps** (5):

- **DECISION-276**: OMS layer or use IBKR algos? Integrate IBKR TWAP/VWAP rather than rolling own
- **DECISION-277**: Per-strategy promotion workflow — each of 72 strategies has independent stage
- **DECISION-278**: Internal trade journal schema — chart snapshot, agent transcripts, signal raw values, regime inputs
- **DECISION-279**: P&L decomposition — separate (signal/timing/exit/sizing/agent) contributions
- **DECISION-280**: Time-of-day slippage adjustment — first/last 30 min higher slippage

**Batch X49 — Thin Areas Surfaced** (10):

- **DECISION-281**: Tax data architecture — design now, populate from Day 1 of paper trading
- **DECISION-282**: Notification cascade — Telegram primary, Email fallback, SMS for critical breaker events
- **DECISION-283**: Backtest output schema — explicit columns/types/nullability/post-conditions, versioned
- **DECISION-284**: Borderline strategy handling — explicit policy at threshold edge cases
- **DECISION-285**: Mid-hold agent re-evaluation — does live agent re-rate open positions?
- **DECISION-286**: Wealthsimple replication tracking — log owner-placed manual trades, compute exec-quality vs system
- **DECISION-287**: Public site failure handling + freshness signal (last-updated timestamp prominent)
- **DECISION-288**: Legal review of public site — registration check, disclaimer, liability terms BEFORE publish
- **DECISION-289**: Owner-absent contingency — backup contact, POA, vacation-mode auto-flatten
- **DECISION-290**: Dropped strategy re-evaluation cadence (every 6 months re-test, re-admit if Sharpe restored)

**Batch X5 — Risk Management Extension** (7):

- **DECISION-086**: Fractional Kelly position sizing
- **DECISION-087**: Vol-targeted sizing per-position (closes 023)
- **DECISION-088**: Portfolio vol target 15%
- **DECISION-089**: Max correlation cap between positions
- **DECISION-090**: Max sector exposure cap
- **DECISION-091**: Drawdown re-sizing
- **DECISION-092**: Slippage model = f(size%ADV, vol)

**Batch X50 — Process Improvements** (2):

- **DECISION-291**: Triage-based bulk approval — owner approves entire impact-ratio band in single message
- **DECISION-292**: Decision→CHECKLIST migration audit (quarterly, RESOLVED decisions to process rules)

**Batch X52 — CRITICAL PIT Correctness** (4):

- **DECISION-298**: Cache stores adjusted-close (auto_adjust=True) which changes over time as splits/dividends accrue — store raw OHLCV + corp actions; recompute adjusted on demand
- **DECISION-299**: yfinance fetch_info returns CURRENT sector/mkt_cap/IPO date regardless of as_of — full historical company info source needed (Polygon Reference)
- **DECISION-300**: yfinance earnings_dates and analyst data return CURRENT values not as-of — replace with PIT source or remove from PIT-claiming functions
- **DECISION-303**: S&P 500 constituent list is current membership applied retroactively — survivorship bias; need historical PIT membership data

**Batch X53 — High-Impact Engine Bugs** (15):

- **DECISION-307**: Cache get_ohlcv front-extension missing — only fetches missing TAIL; if user requests start before cached_start, cache is overwritten with shorter range
- **DECISION-308**: Cache get_ohlcv_bulk requires >=20 trading days — silently rejects valid cache for shorter-window queries
- **DECISION-310**: Cache writes zero-volume days dropped silently (df[volume>0]) — halted/suspended stocks invisible vs not-trading
- **DECISION-313**: update_trailing_stop ignores intraday HIGH — stop only updates at close above prior best; misses highs
- **DECISION-314**: Circuit breakers levels 3 and 4 (intraday halt, market halt) documented but NOT implemented
- **DECISION-317**: VIX hard thresholds (40/30/20) flip regime on single print — needs MA smoothing
- **DECISION-318**: AAII pub-lag treatment missing — survey data marked available on survey-Wed, actually published Thursday
- **DECISION-319**: AAII auto-refresh missing — committed CSV will go stale, no refresh script in /scripts or workflows
- **DECISION-320**: CNN F&G CSV interpolated between key readings — fabricated values used as PIT signal
- **DECISION-321**: Liquidity filter market-cap check skips silently if data missing — fail-open instead of fail-closed
- **DECISION-322**: Market cap from yfinance.info CURRENT not historical — backtesting 2020 trades uses 2026 mkt cap
- **DECISION-323**: Sector reclassifications retro-applied — Meta moved from Comms to Tech; 2020 backtests use current sector
- **DECISION-325**: Institutional 13F PIT assumes universal on-time filing — late filers (some big funds) invisible
- **DECISION-326**: Walk-forward windows hardcoded calendar dates — no rolling logic per DEC-109; stale after June 2026
- **DECISION-327**: Short-borrow cost duplicated across improvements.py + exit_manager.py with different units — pick single source

**Batch X54 — Medium-Severity Improvements** (13):

- **DECISION-328**: Cache filelock fallback writes silently if lock unavailable — concurrent writes can corrupt
- **DECISION-329**: Module-level global caches (VIX, DXY, AAII, CNN F&G) not multi-process safe
- **DECISION-330**: Cache schema not versioned — schema changes silently mix old + new parquet
- **DECISION-331**: ETF list fragmented (ETFS in config.py 17 items, ETFS_FULL in universe.py 25 items, ETF_TICKERS in improvements.py 27 items) — single source
- **DECISION-332**: Smart money composite scoring weights (4/2/-3 etc) hardcoded magic — move to config with documentation
- **DECISION-333**: Sentiment thresholds (AAII 55/45, CNN F&G 20/35/65/80) don't match CNN's published bands
- **DECISION-334**: composite_score uses win_rate as ROI proxy — replace with actual ROI
- **DECISION-335**: composite_score weights (40/30/30) hardcoded — make configurable
- **DECISION-336**: info_cache.json never refreshed — stale market caps persist project-lifetime
- **DECISION-337**: update_trailing_stop ignores intraday extremes for stop placement; fix to track highs and lows
- **DECISION-338**: Conversion logic (short→long in bull regime) creates label only; no actual long opened — document or implement
- **DECISION-339**: pnl_dollar hardcoded $10K notional — wrong for $5K paper / $50K next stage / $1K live
- **DECISION-340**: get_correlation_matrix silently drops tickers with <20 history — variable corr-matrix membership

**Batch X55 — Documentation Sync** (4):

- **DECISION-341**: universe.py docstring claims Wikipedia fetch but code uses static CSV — fix docstring or implement
- **DECISION-342**: Test pass-rate mis-reported — only 38 of 46 tests run cleanly (7 e2e errors); update reporting
- **DECISION-343**: Pandas-ta deprecation warning on pandas 4.0 — plan replacement (TA-Lib alternative)
- **DECISION-344**: Slippage threshold ATR/price > 3% likely too high — most S&P large caps never trigger

**Batch X6 — Exits + Circuit Breakers** (9):

- **DECISION-067**: Add 9 missing exit methods
- **DECISION-068**: Bootstrap CI + pairwise significance for exit comparison
- **DECISION-069**: Per-regime exit selection
- **DECISION-070**: Portfolio-level exit logic
- **DECISION-075**: Adverse-excursion-from-peak breaker
- **DECISION-076**: Factor exposure breaker
- **DECISION-077**: Portfolio drawdown breaker
- **DECISION-078**: Stop-out cluster breaker
- **DECISION-079**: Reconcile Level 2 earnings gap with earnings_tolerant

**Batch X7 — Smart Money + Regimes** (8):

- **DECISION-071**: Smart money refinement (officer roles, 10b5-1 filter, etc.)
- **DECISION-072**: Separate WSB from smart money
- **DECISION-073**: Adopt Quiver pre-built composites
- **DECISION-074**: Polygon block trades / dark pool eval
- **DECISION-102**: Market-Level / Correlation-Factor strategies
- **DECISION-106**: Regime inputs 2 → 8+
- **DECISION-107**: Regime probability (not hard label)
- **DECISION-108**: Regime persistence model (HMM or smoothing)

**Batch X8 — Granularity + Breakdowns** (2):

- **DECISION-066**: Granularity standard for all backtest outputs
- **DECISION-100**: 17+ categorical breakdown variables

**Batch X9 — Data integrity** (2):

- **DECISION-117**: Add file-level checksum + last-validated timestamp to cache
- **DECISION-118**: Prefetch full cross-asset macro (VIX direct, DXY, GLD, oil, sector ETFs, TLT, HYG, SHY)

**Dashboard Specifications** (6):

- **DECISION-199**: Dashboard 1 detailed spec (Phase 1B-α backtest analysis)
- **DECISION-200**: Dashboard 2 detailed spec (Phase 0.D ICT/SMC signal audit)
- **DECISION-201**: Dashboard 3 detailed spec (Stage 2 agent overlay analysis)
- **DECISION-202**: Dashboard 4 detailed spec (Stage 3 paper trading analytics)
- **DECISION-203**: Dashboard 5 detailed spec (Stage 4 live trading analytics)
- **DECISION-204**: Dashboard 6 detailed spec (cross-phase comparison waterfall)

**Live Trading Operational (Group E)** (3):

- **DECISION-029-C**: Real-money starting capital — DEFERRED until post-paper-trading evaluation
- **DECISION-034**: Daily loss limits for live trading
- **DECISION-035**: Tax classification approach (Canadian) — Defer until CPA consultation before Stage 4 — keep PENDING but flagged for later

**Phase 0 Sub-Scope (Group G)** (2):

- **DECISION-037**: Characterization-test-first approach (Phase A)
- **DECISION-038**: Layered execution with iteration budgets

**Phase 1B Methodology** (3):

- **DECISION-014**: Phase 1B passing criteria adjustments
- **DECISION-015**: Strategy correlation analysis methodology
- **DECISION-016**: Threshold calibration scope (BUG-130)

**Process / Infrastructure (Group F)** (2):

- **DECISION-020**: News API selection (depends on 002 eval results)
- **DECISION-043**: Retune framework

**Risk Management (Group C)** (5):

- **DECISION-018**: Cooldown after stop-out (BUG-133)
- **DECISION-019**: Liquidity filter timing (BUG-135)
- **DECISION-022**: Drawdown-aware position sizing (BUG-170)
- **DECISION-023**: Vol-targeted position sizing (BUG-168)
- **DECISION-024**: Correlation-adjusted concentration limits (BUG-169)

**Strategy / Regime Adaptation (Group D)** (4):

- **DECISION-021**: Tier system simplification
- **DECISION-025**: Regime-conditional strategy weighting (BUG-175)
- **DECISION-026**: Walk-forward parameter re-optimization (BUG-172)
- **DECISION-027**: Online learning / feedback loop (BUG-173)

**TradingAgents Architecture** (1):

- **DECISION-062**: Output schema translation: TradingAgents 5-tier → position_size_modifier

---
## Bug Registry

**Total: 269 unique bug IDs.**

| Status | Count |
|---|---|
| RESOLVED | 15 |
| OPEN | 254 |


### Open Bugs by Severity

| Severity | Count |
|---|---|
| CRITICAL | 19 |
| HIGH | 52 |
| MEDIUM | 67 |
| LOW | 21 |
| UNKNOWN | 24 |
| INLINE-ONLY | 71 |

### All Bugs Table

| ID | Title | Severity | Status | Pass Intro |
|---|---|---|---|---|
| **BUG-026** | CRITICAL — VIX proxy is VXX price (223–461), not actual VIX (18–36) — all regime | CRITICAL | OPEN | - |
| **BUG-027** | CRITICAL — `regime_confidence()` function built but never called — dead code | CRITICAL | OPEN | - |
| **BUG-057** | MEDIUM — Integration tests missing 15 critical scenarios — 5 bugs would have bee | CRITICAL | OPEN | - |
| **BUG-063** | MEDIUM — Email approval system has 6 critical design gaps not addressed in PROJE | CRITICAL | OPEN | - |
| **BUG-068** | MEDIUM — CLAUDE.md missing 5 critical recent decisions | CRITICAL | OPEN | - |
| **BUG-078** | CRITICAL — Trailing stop lookahead bias: stop updated using today's close BEFORE | CRITICAL | OPEN | - |
| **BUG-093** | CRITICAL — No execution layer exists; PROJECT_PLAN describes it conceptually onl | CRITICAL | OPEN | - |
| **BUG-094** | CRITICAL — Stage 3 paper trading cannot actually run as designed | CRITICAL | OPEN | - |
| **BUG-095** | CRITICAL — No portfolio-level state; every trade evaluated independently | CRITICAL | OPEN | - |
| **BUG-101** | CRITICAL — 88.1% of trades are overlapping re-entries on the same ticker — backt | CRITICAL | OPEN | - |
| **BUG-102** | CRITICAL — 3.5× same-day duplicate inflation: 9,921 unique decisions logged as 3 | CRITICAL | OPEN | - |
| **BUG-103** | CRITICAL — Smart money data prefetched for 7 categories × 509 tickers but never  | CRITICAL | OPEN | - |
| **BUG-184** | CRITICAL — Insider data prefetch stops 2024-12-31; 13-month gap before backtest  | CRITICAL | OPEN | Pass 18 |
| **BUG-185** | CRITICAL — Wikipedia views prefetch failed entirely; all 509 files empty | CRITICAL | OPEN | Pass 18 |
| **BUG-191** | CRITICAL — No prefetch validation gate before cache-dependent code runs | CRITICAL | OPEN | Pass 18 |
| **BUG-200** | CRITICAL — Risk Agent context expansion required (Section B) | CRITICAL | OPEN | Pass 25 |
| **BUG-214** | close_trade NameError: 'days' used before assignment — confirmed via execution;  | CRITICAL | RESOLVED | Pass 48 |
| **BUG-215** | Duplicate ClosedTrade dataclass at lines 73 + 128 of exit_manager.py — second si | CRITICAL | RESOLVED | Pass 48 |
| **BUG-216** | test_e2e fixture undefined — 7 of 8 e2e tests ERROR at setup; engine fixture mis | CRITICAL | RESOLVED | Pass 48 |
| **BUG-217** | get_news_sentiment path mismatch — reads /prefetch/news/ but data lives in /cach | CRITICAL | RESOLVED | Pass 48 |
| **BUG-218** | yfinance fetch_info returns CURRENT analyst data not as_of — sector/mkt_cap/IPO/ | CRITICAL | OPEN | Pass 48 |
| **BUG-219** | Cache stores adjusted-close which silently shifts as new corp actions accrue — h | CRITICAL | OPEN | Pass 48 |
| **BUG-220** | FRED data revisions unhandled — current API returns latest revised values not vi | CRITICAL | RESOLVED | Pass 48 |
| **BUG-221** | VXX used as ^VIX proxy + UUP as DXY proxy — neither tracks underlying accurately | CRITICAL | RESOLVED | Pass 48 |
| **BUG-222** | S&P 500 constituents are CURRENT membership applied to all backtest dates — surv | CRITICAL | OPEN | Pass 48 |
| **BUG-223** | CPI/NFP/FOMC dates hardcoded through March 2026 only — live trading after that h | CRITICAL | RESOLVED | Pass 48 |
| **BUG-224** | PIT guard `_assert_no_lookahead` logs WARNING not RAISE — leakage swallowed in p | CRITICAL | RESOLVED | Pass 48 |
| **BUG-225** | Regime classifier returns 'neutral' on missing VIX silently — should refuse to t | CRITICAL | RESOLVED | Pass 48 |
| **BUG-028** | HIGH — RSI computation uses simple rolling mean instead of Wilder exponential sm | HIGH | OPEN | - |
| **BUG-029** | HIGH — Open trades at backtest end silently discarded — upward bias in all metri | HIGH | OPEN | - |
| **BUG-030** | HIGH — VIX tightening in crisis contradicts own documentation | HIGH | OPEN | - |
| **BUG-031** | HIGH — Walk-forward OOS minimum of 30 trades is statistically insufficient | HIGH | OPEN | - |
| **BUG-032** | HIGH — Profit factor minimum 1.2 too low; literature requires 1.5 minimum | HIGH | OPEN | - |
| **BUG-033** | HIGH — Sharpe ratio not required as passing criterion; computed but ignored | HIGH | OPEN | - |
| **BUG-034** | HIGH — Mean reversion strategies run in all regimes — literature shows they fail | HIGH | OPEN | - |
| **BUG-051** | HIGH — All 5 agents receive wrong or zero price context due to BUG-10 compoundin | HIGH | OPEN | - |
| **BUG-052** | HIGH — Risk Agent's VIX floor behavior now fully explained by BUG-26 | HIGH | OPEN | - |
| **BUG-053** | HIGH — Finnhub news cache: all 509 files are empty — Sentiment Agent has no news | HIGH | OPEN | - |
| **BUG-060** | HIGH — Short entry zone validation rejects favourable gap-down — understates sho | HIGH | OPEN | - |
| **BUG-061** | HIGH — Backtest allows multiple concurrent positions in same ticker across conse | HIGH | OPEN | - |
| **BUG-062** | HIGH — Phase 1D cannot run — 2020 OHLCV data not cached, DATA_LOAD_START=2021 | HIGH | OPEN | - |
| **BUG-072** | HIGH — `validate_phase1b_data.py` passes all checks but misses 6 blockers — fals | HIGH | OPEN | - |
| **BUG-073** | HIGH — `prepopulate_cache_index.py` writes incompatible format — causes cache mi | HIGH | OPEN | - |
| **BUG-074** | HIGH — BUG-14 worse than documented: XLE also missing from `run_full.sh` — 5 tic | HIGH | OPEN | - |
| **BUG-079** | HIGH — Stop fills assumed at the stop price; gap-through is not modelled (slippa | HIGH | OPEN | - |
| **BUG-080** | HIGH — Exit slippage never applied; only entry slippage charged. Round-trip slip | HIGH | OPEN | - |
| **BUG-081** | HIGH — `SHORT_BORROW_COST_PER_DAY = 0.005` is 2.5× the documented intent | HIGH | RESOLVED | - |
| **BUG-082** | HIGH — Slippage and transaction-cost double-charging — total cost 2× literature  | HIGH | OPEN | - |
| **BUG-083** | HIGH — `get_congressional_detail()` filters with INVERTED point-in-time logic | HIGH | OPEN | - |
| **BUG-096** | HIGH — No benchmark comparison (SPY buy-and-hold) | HIGH | OPEN | - |
| **BUG-097** | HIGH — No infrastructure-as-code; manual VPS setup | HIGH | OPEN | - |
| **BUG-098** | HIGH — No monitoring or alerting | HIGH | OPEN | - |
| **BUG-104** | HIGH — Position sizing rules from config never applied to PnL — backtest assumes | HIGH | OPEN | - |
| **BUG-105** | HIGH — Agent downgrade cascade: 99.9% of trades downgraded by exactly 1 tier — a | HIGH | OPEN | - |
| **BUG-106** | HIGH — Perfect stop fills in trade log: every trailing-stop exit fills at exactl | HIGH | OPEN | - |
| **BUG-109** | HIGH — yfinance auto_adjust causes data drift; backtest results not reproducible | HIGH | OPEN | Pass 12 |
| **BUG-110** | HIGH — Entry gap filter not enforced; trades opened despite exceeding ATR limit | HIGH | OPEN | Pass 12 |
| **BUG-113** | HIGH — Agent action/sizing/exit recommendations ignored by engine | HIGH | OPEN | Pass 14 |
| **BUG-178** | HIGH — Earnings dates fetched live during backtest, no prefetch path | HIGH | OPEN | Pass 17 |
| **BUG-179** | HIGH — yfinance .info fetched live during backtest universe load | HIGH | OPEN | Pass 17 |
| **BUG-180** | HIGH — VIX not explicitly prefetched; VXX used as proxy is cause of BUG-26 | HIGH | OPEN | Pass 17 |
| **BUG-186** | HIGH — 29 institutional 13F files empty including major tickers (AAPL, ABBV, AMZ | HIGH | OPEN | Pass 18 |
| **BUG-187** | HIGH — WSB mentions prefetch stops 2025-02-21; 14-month gap | HIGH | OPEN | Pass 18 |
| **BUG-205** | TRANSACTION_COSTS understates 3x at small notional (no IBKR cap modeling) | HIGH | OPEN | Pass 47 |
| **BUG-206** | Cache stale-data silent use (402 tickers end 2024-12-31, no warning) | HIGH | OPEN | Pass 47 |
| **BUG-210** | agents/pipeline.py silent downgrade on API failure (5 sites) | HIGH | OPEN | Pass 47 |
| **BUG-212** | sync_from_claude.yml --strategy=theirs silently overrides owner edits on conflic | HIGH | OPEN | Pass 47 |
| **BUG-226** | Cache get_ohlcv front-extension missing; if requested start before cached_start, | HIGH | OPEN | Pass 48 |
| **BUG-227** | Cache bulk fetch >=20 trading days threshold — silently rejects valid cache for  | HIGH | OPEN | Pass 48 |
| **BUG-228** | Cache ticker collision: BRK-B and BRK.B both → BRK_B.parquet | HIGH | RESOLVED | Pass 48 |
| **BUG-229** | Cache zero-volume days dropped silently — halted/suspended stocks invisible | HIGH | OPEN | Pass 48 |
| **BUG-230** | Trailing-stop ATR exits use ENTRY-time ATR throughout hold — should refresh dail | HIGH | RESOLVED | Pass 48 |
| **BUG-231** | exit_hybrid_50pct max_days=252 but other 11 exits don't have max — comparison no | HIGH | RESOLVED | Pass 48 |
| **BUG-232** | update_trailing_stop ignores intraday HIGH — only updates at close above prior b | HIGH | OPEN | Pass 48 |
| **BUG-233** | Circuit breakers level 3 + 4 documented but not implemented | HIGH | OPEN | Pass 48 |
| **BUG-234** | VIX hard thresholds flip regime on single print — no MA smoothing | HIGH | OPEN | Pass 48 |
| **BUG-235** | AAII pub-lag not respected — Wed survey marked tradeable Wed instead of Thu | HIGH | OPEN | Pass 48 |
| **BUG-236** | AAII auto-refresh missing — committed CSV will go stale | HIGH | OPEN | Pass 48 |
| **BUG-237** | CNN F&G CSV interpolated between key readings — fabricated PIT signal | HIGH | OPEN | Pass 48 |
| **BUG-238** | Liquidity filter market-cap fail-open — missing data passes filter | HIGH | OPEN | Pass 48 |
| **BUG-239** | Sector reclassifications retro-applied — current sector for old trades | HIGH | OPEN | Pass 48 |
| **BUG-240** | Congressional signal weighted by disclosure_date not transaction_date | HIGH | RESOLVED | Pass 48 |
| **BUG-241** | Institutional 13F PIT assumes on-time filing — late filers invisible | HIGH | OPEN | Pass 48 |
| **BUG-242** | Short borrow cost duplicated across improvements.py and exit_manager.py with dif | HIGH | RESOLVED | Pass 48 |
| **BUG-243** | Walk-forward windows hardcoded calendar dates — stale after June 2026 | HIGH | OPEN | Pass 48 |
| **BUG-244** | close_trade circuit breaker exits skip MAE/MFE update on day of exit (passes 0.0 | HIGH | OPEN | Pass 48 |
| **BUG-035** | MEDIUM — Decision Agent default fallback has invalid `action` value | MEDIUM | OPEN | - |
| **BUG-036** | MEDIUM — Regime-aware strategy weighting not implemented | MEDIUM | OPEN | - |
| **BUG-037** | MEDIUM — Survivorship bias haircut methodology is arbitrary | MEDIUM | OPEN | - |
| **BUG-038** | MEDIUM — No minimum Sharpe in Bonferroni correction | MEDIUM | OPEN | - |
| **BUG-039** | MEDIUM — `regime_confidence()` compares VIX-based regime with SPY-trend regime i | MEDIUM | OPEN | - |
| **BUG-040** | MEDIUM — Short stop distance same as long (10%) — asymmetric risk not accounted  | MEDIUM | OPEN | - |
| **BUG-041** | MEDIUM — `min_market_cap_m = 100` too low; admits stocks with poor institutional | MEDIUM | OPEN | - |
| **BUG-045** | MEDIUM — FX currency risk not modelled | MEDIUM | OPEN | - |
| **BUG-046** | MEDIUM — `fetch_info_bulk` info cache uses current market_cap, not historical | MEDIUM | OPEN | - |
| **BUG-047** | MEDIUM — VXX in universe creates self-referencing regime paradox | MEDIUM | OPEN | - |
| **BUG-048** | MEDIUM — Sector `Volatility` and `Emerging Markets` not in sector criteria profi | MEDIUM | OPEN | - |
| **BUG-054** | MEDIUM — Hull Moving Average uses simple rolling mean instead of WMA — signal ti | MEDIUM | OPEN | - |
| **BUG-055** | MEDIUM — PSAR flip detection uses approximation that may fire on wrong day | MEDIUM | OPEN | - |
| **BUG-056** | MEDIUM — Phase 1C base score can exceed [0, 100] — Decision Agent adjustment not | MEDIUM | OPEN | - |
| **BUG-064** | MEDIUM — Phase 1C prerequisites not documented — Unusual Whales and Ortex integr | MEDIUM | OPEN | - |
| **BUG-065** | MEDIUM — Strategy retirement rule statistically invalid at realistic live trade  | MEDIUM | OPEN | - |
| **BUG-066** | MEDIUM — PROJECT_PLAN mentions "60 strategies" 11 times — 9 of 12 new short stra | MEDIUM | OPEN | - |
| **BUG-067** | MEDIUM — Alpaca paper trading (Stage 3) does not match IBKR live trading (Stage  | MEDIUM | OPEN | - |
| **BUG-075** | MEDIUM — `max_drawdown` computed on unsorted PnL series — results depend on exit | MEDIUM | OPEN | - |
| **BUG-076** | MEDIUM — Agent cache fully contaminated: all runs for same ticker+date+phase sha | MEDIUM | OPEN | - |
| **BUG-077** | MEDIUM — Candidate ranking by `strategy_count` inflated by `avoid` entries — top | MEDIUM | OPEN | - |
| **BUG-084** | MEDIUM — IS/OOS walk-forward boundary leakage on multi-day swing trades | MEDIUM | OPEN | - |
| **BUG-085** | MEDIUM — `regime_at_entry` includes the regime label but no transition tracking | MEDIUM | OPEN | - |
| **BUG-086** | MEDIUM — FRED CPI lookahead bias of ~10 days | MEDIUM | OPEN | - |
| **BUG-087** | MEDIUM — No data quality validation on ingestion | MEDIUM | OPEN | - |
| **BUG-088** | MEDIUM — No signal versioning; cache invalidation incomplete | MEDIUM | OPEN | - |
| **BUG-089** | MEDIUM — Flat signal dict (220 fields) lacks type safety | MEDIUM | OPEN | - |
| **BUG-090** | MEDIUM — No state checkpointing for crashes/restarts | MEDIUM | OPEN | - |
| **BUG-091** | MEDIUM — No determinism control | MEDIUM | OPEN | - |
| **BUG-099** | MEDIUM — No secret management; API keys in environment variables | MEDIUM | OPEN | - |
| **BUG-100** | MEDIUM — No kill switch; manual intervention required to stop trading | MEDIUM | OPEN | - |
| **BUG-107** | MEDIUM — Silent exception swallowing: `except Exception: pass` masks checkpoint  | MEDIUM | OPEN | - |
| **BUG-108** | MEDIUM — Agent context built with `.get(key, default)` masks missing data; agent | MEDIUM | OPEN | - |
| **BUG-111** | MEDIUM — No break-and-retest variants of breakout strategies | MEDIUM | OPEN | Pass 13 |
| **BUG-181** | MEDIUM — Finnhub news prefetch silently produces empty files | MEDIUM | OPEN | Pass 17 |
| **BUG-182** | MEDIUM — Agent cache invalidated by every code change with no versioning gate | MEDIUM | OPEN | Pass 17 |
| **BUG-188** | MEDIUM — Defense tickers (NOC, TXT) have empty gov_contracts data | MEDIUM | OPEN | Pass 18 |
| **BUG-189** | MEDIUM — Ticker symbol mapping issue: BF-B, BRK-B variants empty | MEDIUM | OPEN | Pass 18 |
| **BUG-190** | MEDIUM — Quiver endpoints not in prefetch (Senate, Twitter, Off-Exchange, App Do | MEDIUM | OPEN | Pass 18 |
| **BUG-199** | MEDIUM — No gate firing rate observability | MEDIUM | OPEN | Pass 24 |
| **BUG-201** | MEDIUM — Strategy `earnings_tolerant` attribute missing | MEDIUM | OPEN | Pass 25 |
| **BUG-202** | MEDIUM — No earnings-momentum strategies implemented | MEDIUM | OPEN | Pass 25 |
| **BUG-203** | MEDIUM — No A/B testing infrastructure for agent gates | MEDIUM | OPEN | Pass 25 |
| **BUG-207** | Type hint coverage 0% in screener.py + engine/backtest.py (blocks mypy) | MEDIUM | OPEN | Pass 47 |
| **BUG-208** | Docstring coverage near zero in engine/backtest.py (4 of all functions) | MEDIUM | OPEN | Pass 47 |
| **BUG-209** | 81 except Exception blocks; some swallow real errors | MEDIUM | OPEN | Pass 47 |
| **BUG-211** | Cache concurrency unverified — prefetch + validate may collide | MEDIUM | OPEN | Pass 47 |
| **BUG-213** | requirements.txt missing openai, tradingagents, fredapi (incomplete) | MEDIUM | OPEN | Pass 47 |
| **BUG-245** | Cache filelock fallback silently overwrites — concurrent corruption risk | MEDIUM | OPEN | Pass 48 |
| **BUG-246** | Module globals (VIX, DXY, AAII, CNN F&G) not multi-process safe | MEDIUM | OPEN | Pass 48 |
| **BUG-247** | Cache schema not versioned | MEDIUM | OPEN | Pass 48 |
| **BUG-248** | ETF list fragmented across 3 files with different memberships | MEDIUM | OPEN | Pass 48 |
| **BUG-249** | Smart money scoring weights hardcoded — no config | MEDIUM | OPEN | Pass 48 |
| **BUG-250** | Sentiment thresholds don't match CNN published bands | MEDIUM | OPEN | Pass 48 |
| **BUG-251** | composite_score uses win_rate as ROI proxy — incorrect | MEDIUM | OPEN | Pass 48 |
| **BUG-252** | composite_score weights 40/30/30 hardcoded | MEDIUM | OPEN | Pass 48 |
| **BUG-253** | info_cache.json never refreshed — stale data persists | MEDIUM | OPEN | Pass 48 |
| **BUG-254** | Conversion logic creates label only; no actual long opened | MEDIUM | OPEN | Pass 48 |
| **BUG-255** | pnl_dollar hardcoded $10K notional | MEDIUM | OPEN | Pass 48 |
| **BUG-256** | get_correlation_matrix silently drops short-history tickers | MEDIUM | OPEN | Pass 48 |
| **BUG-257** | get_gov_contracts trend math compares mismatched window sizes | MEDIUM | OPEN | Pass 48 |
| **BUG-258** | ATR fallback magic number 2% in exit strategies | MEDIUM | OPEN | Pass 48 |
| **BUG-259** | exit_time_stop mis-labels exit as time_stop_10d when actually end-of-data at day | MEDIUM | OPEN | Pass 48 |
| **BUG-260** | exit_fixed_target uses STOP-FIRST priority — both stop+target same day uses stop | MEDIUM | OPEN | Pass 48 |
| **BUG-261** | Pandas4 deprecation warning on pandas-ta — needs replacement plan | MEDIUM | OPEN | Pass 48 |
| **BUG-262** | apply_slippage threshold ATR/price > 3% rarely triggered for typical stocks | MEDIUM | OPEN | Pass 48 |
| **BUG-263** | Slippage applied at apply_transaction_costs separate from _pnl borrow — short tr | MEDIUM | OPEN | Pass 48 |
| **BUG-009** | `below_cam_s3` signal key does not exist | LOW | OPEN | - |
| **BUG-042** | LOW — `LILLY` appears as ticker in `run_full.sh` but should be `LLY` | LOW | OPEN | - |
| **BUG-043** | LOW — Missing Calmar ratio minimum in passing criteria | LOW | OPEN | - |
| **BUG-044** | LOW — Test suite has no test for `close_trade()` or `_process_day()` | LOW | OPEN | - |
| **BUG-049** | LOW — FX risk not mentioned in EXPLANATION.md or PROJECT_PLAN.md | LOW | OPEN | - |
| **BUG-050** | LOW — `position_staleness_pct=1%` in live rules has no backtest equivalent | LOW | OPEN | - |
| **BUG-058** | LOW — StochRSI cross-up fires in mid-range, not just oversold zone | LOW | OPEN | - |
| **BUG-059** | LOW — CPR top/bottom labels are reversed vs industry convention | LOW | OPEN | - |
| **BUG-069** | LOW — Infrastructure design: GitHub Actions vs VPS ambiguity | LOW | OPEN | - |
| **BUG-070** | LOW — No database schema designed for Stage 3 PostgreSQL | LOW | OPEN | - |
| **BUG-071** | LOW — IBKR API session management not designed | LOW | OPEN | - |
| **BUG-092** | LOW — No streaming progress / metrics during run | LOW | OPEN | - |
| **BUG-112** | LOW — No ICT/SMC concepts implemented | LOW | OPEN | Pass 13 |
| **BUG-183** | LOW — No prefetch validation step | LOW | OPEN | Pass 17 |
| **BUG-204** | engine.py dead code shipping in repo (426 lines, no current import) | LOW | OPEN | Pass 47 |
| **BUG-264** | universe.py docstring claims Wikipedia fetch but uses static CSV | LOW | OPEN | Pass 48 |
| **BUG-265** | yfinance auto_adjust=True hardcoded; no raw price option | LOW | OPEN | Pass 48 |
| **BUG-266** | delay_sec 0.3 magic number undocumented | LOW | OPEN | Pass 48 |
| **BUG-267** | Test e2e takes 4.5 min for 1 passing test — too slow for smoke | LOW | OPEN | Pass 48 |
| **BUG-268** | ETF sector labels hardcoded — new ETFs default to Unknown | LOW | OPEN | Pass 48 |
| **BUG-269** | Quiver _DELAY constant unused — live API never called in backtest | LOW | OPEN | Pass 48 |
| **BUG-001** | `crisis_flag` used before definition → NameError crash | UNKNOWN | OPEN | - |
| **BUG-002** | `days` variable used before definition → UnboundLocalError on every trade close | UNKNOWN | OPEN | - |
| **BUG-003** | `ClosedTrade` dataclass defined twice — dead code, maintenance risk | UNKNOWN | OPEN | - |
| **BUG-004** | `avoid` direction falls into `triggered_short` bucket — inflates confidence tier | UNKNOWN | OPEN | - |
| **BUG-005** | `strategies_triggered` key mismatch — agent cache is always wrong | UNKNOWN | OPEN | - |
| **BUG-006** | Double borrow cost on short trades | UNKNOWN | OPEN | - |
| **BUG-007** | API key guard blocks no-agent Phase 1B run | UNKNOWN | OPEN | - |
| **BUG-008** | `ema_50_200_bullish` signal key does not exist | UNKNOWN | OPEN | - |
| **BUG-010** | Agent signal keys wrong — agents always see `False` for key price context | UNKNOWN | OPEN | - |
| **BUG-011** | `williams_r` short default fires incorrectly | UNKNOWN | OPEN | - |
| **BUG-012** | Deduplication order bias — shorts never fire when long strategy fires first | UNKNOWN | OPEN | - |
| **BUG-013** | `days_to_next_earnings` makes ~106,000 live yfinance calls during backtest | UNKNOWN | OPEN | - |
| **BUG-014** | AAPL, CVS, JPM, NVDA missing from `run_full.sh` batch ticker lists | UNKNOWN | OPEN | - |
| **BUG-015** | `max_drawdown` uses `cumsum()` instead of compounded equity curve | UNKNOWN | OPEN | - |
| **BUG-016** | `PASSING_CRITERIA min_trades = 100` contradicts all documentation | UNKNOWN | OPEN | - |
| **BUG-017** | `run_commit.sh` full mode hangs on interactive `input()` in merge script | UNKNOWN | OPEN | - |
| **BUG-018** | Bonferroni correction hardcoded to 60 strategies, should be 72 | UNKNOWN | OPEN | - |
| **BUG-019** | OHLCV cache incomplete — 402 of 495 tickers only cover to 2024-12-31 | UNKNOWN | OPEN | - |
| **BUG-020** | Regime thresholds inconsistent between PROJECT_PLAN and config.py | UNKNOWN | OPEN | - |
| **BUG-021** | `exit_strategies.py` own `_pnl` has no borrow cost — short comparison optimistic | UNKNOWN | OPEN | - |
| **BUG-022** | `run_phase1a.py` header prints "60 strategies" | UNKNOWN | OPEN | - |
| **BUG-023** | `screener.py` docstring says "60 strategies across 7 categories" | UNKNOWN | OPEN | - |
| **BUG-024** | CHECKLIST item 13c says "review ALL agent outputs" — not applicable for no-agent | UNKNOWN | OPEN | - |
| **BUG-025** | `run_tests.sh` does not pass `--no-agents` flag | UNKNOWN | OPEN | - |
| **BUG-114** | through BUG-123) for the agent integration gaps identified above. Each is HIGH o | INLINE-ONLY | OPEN | - |
| **BUG-115** | **BUG-115 · HIGH — Validation methodology cannot attribute success/failure clean | INLINE-ONLY | OPEN | - |
| **BUG-116** | \| HIGH \| Risk Agent `trade_blocked` boolean ignored by engine \| | INLINE-ONLY | OPEN | - |
| **BUG-117** | \| HIGH \| Decision Agent `recommended_exit` ignored; exit strategy hardcoded \| | INLINE-ONLY | OPEN | - |
| **BUG-118** | \| HIGH \| Decision Agent `position_size_modifier` ignored; sizing not different | INLINE-ONLY | OPEN | - |
| **BUG-119** | \| HIGH \| Bull/Bear Debate winner ignored; high-conviction bear debate doesn't  | INLINE-ONLY | OPEN | - |
| **BUG-120** | \| HIGH \| Fundamental Agent `avoid_earnings` ignored; earnings proximity doesn' | INLINE-ONLY | OPEN | - |
| **BUG-121** | \| MEDIUM \| Sentiment Agent `contrarian_signal` extreme_avoid ignored \| | INLINE-ONLY | OPEN | - |
| **BUG-122** | \| MEDIUM \| Risk Agent `risk_score` ignored as gate (only factors into final_sc | INLINE-ONLY | OPEN | - |
| **BUG-123** | ) for the agent integration gaps identified above. Each is HIGH or MEDIUM severi | INLINE-ONLY | OPEN | - |
| **BUG-124** | \| MEDIUM \| Technical Agent `entry_quality` weak/moderate/strong ignored as fil | INLINE-ONLY | OPEN | - |
| **BUG-125** | \| MEDIUM \| Technical Agent `sector_alignment` negative ignored for breakouts \ | INLINE-ONLY | OPEN | - |
| **BUG-126** | \| MEDIUM \| Debate `price_positioning` weak entry / strong entry ignored \| | INLINE-ONLY | OPEN | - |
| **BUG-127** | \| LOW \| Decision Agent `portfolio_note` concentration warnings text-only \| | INLINE-ONLY | OPEN | - |
| **BUG-128** | \| MEDIUM \| No correlation analysis between strategies; correlated firings coun | INLINE-ONLY | OPEN | - |
| **BUG-129** | \| MEDIUM \| No regime-conditional parameter tuning (RSI 30/70 fixed across regi | INLINE-ONLY | OPEN | - |
| **BUG-130** | \| MEDIUM \| No threshold calibration; all thresholds (RSI, MACD, Bollinger, siz | INLINE-ONLY | OPEN | - |
| **BUG-131** | \| MEDIUM \| No earnings proximity filter; trades open within 0-3 days of earnin | INLINE-ONLY | OPEN | - |
| **BUG-132** | \| MEDIUM \| No FOMC/CPI day filter; new entries on high-impact days \| | INLINE-ONLY | OPEN | - |
| **BUG-133** | \| MEDIUM \| No cross-day cooldown after stop-out; can re-enter same ticker next | INLINE-ONLY | OPEN | - |
| **BUG-134** | \| MEDIUM \| No correlation-aware concentration filter; 10 high-beta tech longs  | INLINE-ONLY | OPEN | - |
| **BUG-135** | \| MEDIUM \| Liquidity filter runs at universe load only, not at entry time; sta | INLINE-ONLY | OPEN | - |
| **BUG-136** | \| MEDIUM \| No bid-ask spread filter; backtest assumes zero spread \| | INLINE-ONLY | OPEN | - |
| **BUG-137** | \| LOW \| Agent context lacks historical analogues — no "last 5 times this strat | INLINE-ONLY | OPEN | - |
| **BUG-138** | \| LOW \| Agent context lacks news headlines as text — sentiment is number only, | INLINE-ONLY | OPEN | - |
| **BUG-139** | to BUG-150) | INLINE-ONLY | OPEN | - |
| **BUG-140** | MEDIUM** — No Quality strategy family (ROE, accruals, low debt) | INLINE-ONLY | OPEN | - |
| **BUG-141** | HIGH** — No Volatility-based strategies (vol-targeting, vol carry) | INLINE-ONLY | OPEN | - |
| **BUG-142** | HIGH** — No Event-driven strategies (PEAD, M&A arb, index inclusion) | INLINE-ONLY | OPEN | - |
| **BUG-143** | MEDIUM** — No Macro/Cross-asset strategies | INLINE-ONLY | OPEN | - |
| **BUG-144** | HIGH** — Smart-money signals are binary gates, not continuous strategy inputs | INLINE-ONLY | OPEN | - |
| **BUG-145** | HIGH** — No ICT/SMC strategy family (8 core concepts, 16 derived strategies) | INLINE-ONLY | OPEN | - |
| **BUG-146** | HIGH** — No Volume Profile / VPVR strategies | INLINE-ONLY | OPEN | - |
| **BUG-147** | MEDIUM** — No Anchored VWAP strategies | INLINE-ONLY | OPEN | - |
| **BUG-148** | MEDIUM** — No Sentiment/Narrative rule strategies (only agent-mediated) | INLINE-ONLY | OPEN | - |
| **BUG-149** | MEDIUM** — No Calendar/Seasonal strategies (FOMC, January, sell-in-May) | INLINE-ONLY | OPEN | - |
| **BUG-150** | ) | INLINE-ONLY | OPEN | - |
| **BUG-151** | to BUG-159) | INLINE-ONLY | OPEN | - |
| **BUG-152** | HIGH** — Volume Profile (POC, VAH, VAL, HVN, LVN) not computed | INLINE-ONLY | OPEN | - |
| **BUG-153** | MEDIUM** — Cumulative Volume Delta (CVD) not computed | INLINE-ONLY | OPEN | - |
| **BUG-154** | HIGH** — Relative Strength vs sector and SPY not computed (planned for 1C, recom | INLINE-ONLY | OPEN | - |
| **BUG-155** | MEDIUM** — Per-ticker volatility regime not computed | INLINE-ONLY | OPEN | - |
| **BUG-156** | HIGH** — Post-Earnings Announcement Drift (PEAD) tracking absent | INLINE-ONLY | OPEN | - |
| **BUG-157** | MEDIUM** — News headlines not passed to agents as text (only sentiment number) | INLINE-ONLY | OPEN | - |
| **BUG-158** | LOW** — Implied volatility / Volatility Risk Premium signals absent (Phase 1C+) | INLINE-ONLY | OPEN | - |
| **BUG-159** | ) | INLINE-ONLY | OPEN | - |
| **BUG-160** | to BUG-167) | INLINE-ONLY | OPEN | - |
| **BUG-161** | HIGH** — Fair Value Gap (FVG) detection absent | INLINE-ONLY | OPEN | - |
| **BUG-162** | HIGH** — Liquidity Sweep / Stop Hunt detection absent | INLINE-ONLY | OPEN | - |
| **BUG-163** | MEDIUM** — Displacement filter absent (used as quality filter for OB/FVG) | INLINE-ONLY | OPEN | - |
| **BUG-164** | MEDIUM** — Breaker Block detection absent | INLINE-ONLY | OPEN | - |
| **BUG-165** | MEDIUM** — Premium/Discount zones not computed | INLINE-ONLY | OPEN | - |
| **BUG-166** | MEDIUM** — Optimal Trade Entry (OTE) Fibonacci zone not computed | INLINE-ONLY | OPEN | - |
| **BUG-167** | ) | INLINE-ONLY | OPEN | - |
| **BUG-168** | to BUG-177) | INLINE-ONLY | OPEN | - |
| **BUG-169** | HIGH** — No correlation-adjusted concentration limits | INLINE-ONLY | OPEN | - |
| **BUG-170** | MEDIUM** — No drawdown-aware position sizing | INLINE-ONLY | OPEN | - |
| **BUG-171** | MEDIUM** — No risk parity allocation across strategies | INLINE-ONLY | OPEN | - |
| **BUG-172** | MEDIUM** — No walk-forward parameter optimization (all params static) | INLINE-ONLY | OPEN | - |
| **BUG-173** | MEDIUM** — No online learning / feedback loop from live performance | INLINE-ONLY | OPEN | - |
| **BUG-174** | LOW** — No execution algorithm sophistication (acceptable at $10K scale) | INLINE-ONLY | OPEN | - |
| **BUG-175** | HIGH** — No regime-conditional strategy weighting (smooth mixture) | INLINE-ONLY | OPEN | - |
| **BUG-176** | MEDIUM** — No ML enhancement layer (acceptable; agents are intended substitute) | INLINE-ONLY | OPEN | - |
| **BUG-177** | ) | INLINE-ONLY | OPEN | - |
| **BUG-192** | ) | INLINE-ONLY | OPEN | - |
| **BUG-193** | NEW) | INLINE-ONLY | OPEN | - |
| **BUG-194** | NEW) | INLINE-ONLY | OPEN | - |
| **BUG-195** | NEW) | INLINE-ONLY | OPEN | - |
| **BUG-196** | NEW) | INLINE-ONLY | OPEN | - |
| **BUG-197** | NEW) | INLINE-ONLY | OPEN | - |
| **BUG-198** | (NEW) · CRITICAL — No structural PIT data loader; each data source uses ad-hoc P | INLINE-ONLY | OPEN | - |

---
*Regenerated April 2026 after Pass 51.*