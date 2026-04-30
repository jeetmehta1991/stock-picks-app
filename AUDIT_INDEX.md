# AUDIT_INDEX.md — Decision and Bug Registry
**Last regenerated:** April 2026 (post-Pass 46)

---

## Decision Registry

**Total: 257 decision entries**

| Status | Count |
|---|---|
| RESOLVED | 55 |
| PARTIAL | 5 |
| SUPERSEDED | 7 |
| PENDING | 190 |

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

**Batch X5 — Risk Management Extension** (7):

- **DECISION-086**: Fractional Kelly position sizing
- **DECISION-087**: Vol-targeted sizing per-position (closes 023)
- **DECISION-088**: Portfolio vol target 15%
- **DECISION-089**: Max correlation cap between positions
- **DECISION-090**: Max sector exposure cap
- **DECISION-091**: Drawdown re-sizing
- **DECISION-092**: Slippage model = f(size%ADV, vol)

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

**Total: 203 unique bug IDs.**

| Severity | Count |
|---|---|
| CRITICAL | 16 |
| HIGH | 35 |
| MEDIUM | 43 |
| LOW | 14 |
| UNKNOWN | 24 |
| INLINE-ONLY | 71 |

### All Bugs Table

| ID | Title | Severity | Pass Intro |
|---|---|---|---|
| **BUG-026** | CRITICAL — VIX proxy is VXX price (223–461), not actual VIX (18–36) — all regime | CRITICAL | - |
| **BUG-027** | CRITICAL — `regime_confidence()` function built but never called — dead code | CRITICAL | - |
| **BUG-057** | MEDIUM — Integration tests missing 15 critical scenarios — 5 bugs would have bee | CRITICAL | - |
| **BUG-063** | MEDIUM — Email approval system has 6 critical design gaps not addressed in PROJE | CRITICAL | - |
| **BUG-068** | MEDIUM — CLAUDE.md missing 5 critical recent decisions | CRITICAL | - |
| **BUG-078** | CRITICAL — Trailing stop lookahead bias: stop updated using today's close BEFORE | CRITICAL | - |
| **BUG-093** | CRITICAL — No execution layer exists; PROJECT_PLAN describes it conceptually onl | CRITICAL | - |
| **BUG-094** | CRITICAL — Stage 3 paper trading cannot actually run as designed | CRITICAL | - |
| **BUG-095** | CRITICAL — No portfolio-level state; every trade evaluated independently | CRITICAL | - |
| **BUG-101** | CRITICAL — 88.1% of trades are overlapping re-entries on the same ticker — backt | CRITICAL | - |
| **BUG-102** | CRITICAL — 3.5× same-day duplicate inflation: 9,921 unique decisions logged as 3 | CRITICAL | - |
| **BUG-103** | CRITICAL — Smart money data prefetched for 7 categories × 509 tickers but never  | CRITICAL | - |
| **BUG-184** | CRITICAL — Insider data prefetch stops 2024-12-31; 13-month gap before backtest  | CRITICAL | Pass 18 |
| **BUG-185** | CRITICAL — Wikipedia views prefetch failed entirely; all 509 files empty | CRITICAL | Pass 18 |
| **BUG-191** | CRITICAL — No prefetch validation gate before cache-dependent code runs | CRITICAL | Pass 18 |
| **BUG-200** | CRITICAL — Risk Agent context expansion required (Section B) | CRITICAL | Pass 25 |
| **BUG-028** | HIGH — RSI computation uses simple rolling mean instead of Wilder exponential sm | HIGH | - |
| **BUG-029** | HIGH — Open trades at backtest end silently discarded — upward bias in all metri | HIGH | - |
| **BUG-030** | HIGH — VIX tightening in crisis contradicts own documentation | HIGH | - |
| **BUG-031** | HIGH — Walk-forward OOS minimum of 30 trades is statistically insufficient | HIGH | - |
| **BUG-032** | HIGH — Profit factor minimum 1.2 too low; literature requires 1.5 minimum | HIGH | - |
| **BUG-033** | HIGH — Sharpe ratio not required as passing criterion; computed but ignored | HIGH | - |
| **BUG-034** | HIGH — Mean reversion strategies run in all regimes — literature shows they fail | HIGH | - |
| **BUG-051** | HIGH — All 5 agents receive wrong or zero price context due to BUG-10 compoundin | HIGH | - |
| **BUG-052** | HIGH — Risk Agent's VIX floor behavior now fully explained by BUG-26 | HIGH | - |
| **BUG-053** | HIGH — Finnhub news cache: all 509 files are empty — Sentiment Agent has no news | HIGH | - |
| **BUG-060** | HIGH — Short entry zone validation rejects favourable gap-down — understates sho | HIGH | - |
| **BUG-061** | HIGH — Backtest allows multiple concurrent positions in same ticker across conse | HIGH | - |
| **BUG-062** | HIGH — Phase 1D cannot run — 2020 OHLCV data not cached, DATA_LOAD_START=2021 | HIGH | - |
| **BUG-072** | HIGH — `validate_phase1b_data.py` passes all checks but misses 6 blockers — fals | HIGH | - |
| **BUG-073** | HIGH — `prepopulate_cache_index.py` writes incompatible format — causes cache mi | HIGH | - |
| **BUG-074** | HIGH — BUG-14 worse than documented: XLE also missing from `run_full.sh` — 5 tic | HIGH | - |
| **BUG-079** | HIGH — Stop fills assumed at the stop price; gap-through is not modelled (slippa | HIGH | - |
| **BUG-080** | HIGH — Exit slippage never applied; only entry slippage charged. Round-trip slip | HIGH | - |
| **BUG-081** | HIGH — `SHORT_BORROW_COST_PER_DAY = 0.005` is 2.5× the documented intent | HIGH | - |
| **BUG-082** | HIGH — Slippage and transaction-cost double-charging — total cost 2× literature  | HIGH | - |
| **BUG-083** | HIGH — `get_congressional_detail()` filters with INVERTED point-in-time logic | HIGH | - |
| **BUG-096** | HIGH — No benchmark comparison (SPY buy-and-hold) | HIGH | - |
| **BUG-097** | HIGH — No infrastructure-as-code; manual VPS setup | HIGH | - |
| **BUG-098** | HIGH — No monitoring or alerting | HIGH | - |
| **BUG-104** | HIGH — Position sizing rules from config never applied to PnL — backtest assumes | HIGH | - |
| **BUG-105** | HIGH — Agent downgrade cascade: 99.9% of trades downgraded by exactly 1 tier — a | HIGH | - |
| **BUG-106** | HIGH — Perfect stop fills in trade log: every trailing-stop exit fills at exactl | HIGH | - |
| **BUG-109** | HIGH — yfinance auto_adjust causes data drift; backtest results not reproducible | HIGH | Pass 12 |
| **BUG-110** | HIGH — Entry gap filter not enforced; trades opened despite exceeding ATR limit | HIGH | Pass 12 |
| **BUG-113** | HIGH — Agent action/sizing/exit recommendations ignored by engine | HIGH | Pass 14 |
| **BUG-178** | HIGH — Earnings dates fetched live during backtest, no prefetch path | HIGH | Pass 17 |
| **BUG-179** | HIGH — yfinance .info fetched live during backtest universe load | HIGH | Pass 17 |
| **BUG-180** | HIGH — VIX not explicitly prefetched; VXX used as proxy is cause of BUG-26 | HIGH | Pass 17 |
| **BUG-186** | HIGH — 29 institutional 13F files empty including major tickers (AAPL, ABBV, AMZ | HIGH | Pass 18 |
| **BUG-187** | HIGH — WSB mentions prefetch stops 2025-02-21; 14-month gap | HIGH | Pass 18 |
| **BUG-035** | MEDIUM — Decision Agent default fallback has invalid `action` value | MEDIUM | - |
| **BUG-036** | MEDIUM — Regime-aware strategy weighting not implemented | MEDIUM | - |
| **BUG-037** | MEDIUM — Survivorship bias haircut methodology is arbitrary | MEDIUM | - |
| **BUG-038** | MEDIUM — No minimum Sharpe in Bonferroni correction | MEDIUM | - |
| **BUG-039** | MEDIUM — `regime_confidence()` compares VIX-based regime with SPY-trend regime i | MEDIUM | - |
| **BUG-040** | MEDIUM — Short stop distance same as long (10%) — asymmetric risk not accounted  | MEDIUM | - |
| **BUG-041** | MEDIUM — `min_market_cap_m = 100` too low; admits stocks with poor institutional | MEDIUM | - |
| **BUG-045** | MEDIUM — FX currency risk not modelled | MEDIUM | - |
| **BUG-046** | MEDIUM — `fetch_info_bulk` info cache uses current market_cap, not historical | MEDIUM | - |
| **BUG-047** | MEDIUM — VXX in universe creates self-referencing regime paradox | MEDIUM | - |
| **BUG-048** | MEDIUM — Sector `Volatility` and `Emerging Markets` not in sector criteria profi | MEDIUM | - |
| **BUG-054** | MEDIUM — Hull Moving Average uses simple rolling mean instead of WMA — signal ti | MEDIUM | - |
| **BUG-055** | MEDIUM — PSAR flip detection uses approximation that may fire on wrong day | MEDIUM | - |
| **BUG-056** | MEDIUM — Phase 1C base score can exceed [0, 100] — Decision Agent adjustment not | MEDIUM | - |
| **BUG-064** | MEDIUM — Phase 1C prerequisites not documented — Unusual Whales and Ortex integr | MEDIUM | - |
| **BUG-065** | MEDIUM — Strategy retirement rule statistically invalid at realistic live trade  | MEDIUM | - |
| **BUG-066** | MEDIUM — PROJECT_PLAN mentions "60 strategies" 11 times — 9 of 12 new short stra | MEDIUM | - |
| **BUG-067** | MEDIUM — Alpaca paper trading (Stage 3) does not match IBKR live trading (Stage  | MEDIUM | - |
| **BUG-075** | MEDIUM — `max_drawdown` computed on unsorted PnL series — results depend on exit | MEDIUM | - |
| **BUG-076** | MEDIUM — Agent cache fully contaminated: all runs for same ticker+date+phase sha | MEDIUM | - |
| **BUG-077** | MEDIUM — Candidate ranking by `strategy_count` inflated by `avoid` entries — top | MEDIUM | - |
| **BUG-084** | MEDIUM — IS/OOS walk-forward boundary leakage on multi-day swing trades | MEDIUM | - |
| **BUG-085** | MEDIUM — `regime_at_entry` includes the regime label but no transition tracking | MEDIUM | - |
| **BUG-086** | MEDIUM — FRED CPI lookahead bias of ~10 days | MEDIUM | - |
| **BUG-087** | MEDIUM — No data quality validation on ingestion | MEDIUM | - |
| **BUG-088** | MEDIUM — No signal versioning; cache invalidation incomplete | MEDIUM | - |
| **BUG-089** | MEDIUM — Flat signal dict (220 fields) lacks type safety | MEDIUM | - |
| **BUG-090** | MEDIUM — No state checkpointing for crashes/restarts | MEDIUM | - |
| **BUG-091** | MEDIUM — No determinism control | MEDIUM | - |
| **BUG-099** | MEDIUM — No secret management; API keys in environment variables | MEDIUM | - |
| **BUG-100** | MEDIUM — No kill switch; manual intervention required to stop trading | MEDIUM | - |
| **BUG-107** | MEDIUM — Silent exception swallowing: `except Exception: pass` masks checkpoint  | MEDIUM | - |
| **BUG-108** | MEDIUM — Agent context built with `.get(key, default)` masks missing data; agent | MEDIUM | - |
| **BUG-111** | MEDIUM — No break-and-retest variants of breakout strategies | MEDIUM | Pass 13 |
| **BUG-181** | MEDIUM — Finnhub news prefetch silently produces empty files | MEDIUM | Pass 17 |
| **BUG-182** | MEDIUM — Agent cache invalidated by every code change with no versioning gate | MEDIUM | Pass 17 |
| **BUG-188** | MEDIUM — Defense tickers (NOC, TXT) have empty gov_contracts data | MEDIUM | Pass 18 |
| **BUG-189** | MEDIUM — Ticker symbol mapping issue: BF-B, BRK-B variants empty | MEDIUM | Pass 18 |
| **BUG-190** | MEDIUM — Quiver endpoints not in prefetch (Senate, Twitter, Off-Exchange, App Do | MEDIUM | Pass 18 |
| **BUG-199** | MEDIUM — No gate firing rate observability | MEDIUM | Pass 24 |
| **BUG-201** | MEDIUM — Strategy `earnings_tolerant` attribute missing | MEDIUM | Pass 25 |
| **BUG-202** | MEDIUM — No earnings-momentum strategies implemented | MEDIUM | Pass 25 |
| **BUG-203** | MEDIUM — No A/B testing infrastructure for agent gates | MEDIUM | Pass 25 |
| **BUG-009** | `below_cam_s3` signal key does not exist | LOW | - |
| **BUG-042** | LOW — `LILLY` appears as ticker in `run_full.sh` but should be `LLY` | LOW | - |
| **BUG-043** | LOW — Missing Calmar ratio minimum in passing criteria | LOW | - |
| **BUG-044** | LOW — Test suite has no test for `close_trade()` or `_process_day()` | LOW | - |
| **BUG-049** | LOW — FX risk not mentioned in EXPLANATION.md or PROJECT_PLAN.md | LOW | - |
| **BUG-050** | LOW — `position_staleness_pct=1%` in live rules has no backtest equivalent | LOW | - |
| **BUG-058** | LOW — StochRSI cross-up fires in mid-range, not just oversold zone | LOW | - |
| **BUG-059** | LOW — CPR top/bottom labels are reversed vs industry convention | LOW | - |
| **BUG-069** | LOW — Infrastructure design: GitHub Actions vs VPS ambiguity | LOW | - |
| **BUG-070** | LOW — No database schema designed for Stage 3 PostgreSQL | LOW | - |
| **BUG-071** | LOW — IBKR API session management not designed | LOW | - |
| **BUG-092** | LOW — No streaming progress / metrics during run | LOW | - |
| **BUG-112** | LOW — No ICT/SMC concepts implemented | LOW | Pass 13 |
| **BUG-183** | LOW — No prefetch validation step | LOW | Pass 17 |
| **BUG-001** | `crisis_flag` used before definition → NameError crash | UNKNOWN | - |
| **BUG-002** | `days` variable used before definition → UnboundLocalError on every trade close | UNKNOWN | - |
| **BUG-003** | `ClosedTrade` dataclass defined twice — dead code, maintenance risk | UNKNOWN | - |
| **BUG-004** | `avoid` direction falls into `triggered_short` bucket — inflates confidence tier | UNKNOWN | - |
| **BUG-005** | `strategies_triggered` key mismatch — agent cache is always wrong | UNKNOWN | - |
| **BUG-006** | Double borrow cost on short trades | UNKNOWN | - |
| **BUG-007** | API key guard blocks no-agent Phase 1B run | UNKNOWN | - |
| **BUG-008** | `ema_50_200_bullish` signal key does not exist | UNKNOWN | - |
| **BUG-010** | Agent signal keys wrong — agents always see `False` for key price context | UNKNOWN | - |
| **BUG-011** | `williams_r` short default fires incorrectly | UNKNOWN | - |
| **BUG-012** | Deduplication order bias — shorts never fire when long strategy fires first | UNKNOWN | - |
| **BUG-013** | `days_to_next_earnings` makes ~106,000 live yfinance calls during backtest | UNKNOWN | - |
| **BUG-014** | AAPL, CVS, JPM, NVDA missing from `run_full.sh` batch ticker lists | UNKNOWN | - |
| **BUG-015** | `max_drawdown` uses `cumsum()` instead of compounded equity curve | UNKNOWN | - |
| **BUG-016** | `PASSING_CRITERIA min_trades = 100` contradicts all documentation | UNKNOWN | - |
| **BUG-017** | `run_commit.sh` full mode hangs on interactive `input()` in merge script | UNKNOWN | - |
| **BUG-018** | Bonferroni correction hardcoded to 60 strategies, should be 72 | UNKNOWN | - |
| **BUG-019** | OHLCV cache incomplete — 402 of 495 tickers only cover to 2024-12-31 | UNKNOWN | - |
| **BUG-020** | Regime thresholds inconsistent between PROJECT_PLAN and config.py | UNKNOWN | - |
| **BUG-021** | `exit_strategies.py` own `_pnl` has no borrow cost — short comparison optimistic | UNKNOWN | - |
| **BUG-022** | `run_phase1a.py` header prints "60 strategies" | UNKNOWN | - |
| **BUG-023** | `screener.py` docstring says "60 strategies across 7 categories" | UNKNOWN | - |
| **BUG-024** | CHECKLIST item 13c says "review ALL agent outputs" — not applicable for no-agent | UNKNOWN | - |
| **BUG-025** | `run_tests.sh` does not pass `--no-agents` flag | UNKNOWN | - |
| **BUG-114** | through BUG-123) for the agent integration gaps identified above. Each is HIGH o | INLINE-ONLY | - |
| **BUG-115** | **BUG-115 · HIGH — Validation methodology cannot attribute success/failure clean | INLINE-ONLY | - |
| **BUG-116** | \| HIGH \| Risk Agent `trade_blocked` boolean ignored by engine \| | INLINE-ONLY | - |
| **BUG-117** | \| HIGH \| Decision Agent `recommended_exit` ignored; exit strategy hardcoded \| | INLINE-ONLY | - |
| **BUG-118** | \| HIGH \| Decision Agent `position_size_modifier` ignored; sizing not different | INLINE-ONLY | - |
| **BUG-119** | \| HIGH \| Bull/Bear Debate winner ignored; high-conviction bear debate doesn't  | INLINE-ONLY | - |
| **BUG-120** | \| HIGH \| Fundamental Agent `avoid_earnings` ignored; earnings proximity doesn' | INLINE-ONLY | - |
| **BUG-121** | \| MEDIUM \| Sentiment Agent `contrarian_signal` extreme_avoid ignored \| | INLINE-ONLY | - |
| **BUG-122** | \| MEDIUM \| Risk Agent `risk_score` ignored as gate (only factors into final_sc | INLINE-ONLY | - |
| **BUG-123** | ) for the agent integration gaps identified above. Each is HIGH or MEDIUM severi | INLINE-ONLY | - |
| **BUG-124** | \| MEDIUM \| Technical Agent `entry_quality` weak/moderate/strong ignored as fil | INLINE-ONLY | - |
| **BUG-125** | \| MEDIUM \| Technical Agent `sector_alignment` negative ignored for breakouts \ | INLINE-ONLY | - |
| **BUG-126** | \| MEDIUM \| Debate `price_positioning` weak entry / strong entry ignored \| | INLINE-ONLY | - |
| **BUG-127** | \| LOW \| Decision Agent `portfolio_note` concentration warnings text-only \| | INLINE-ONLY | - |
| **BUG-128** | \| MEDIUM \| No correlation analysis between strategies; correlated firings coun | INLINE-ONLY | - |
| **BUG-129** | \| MEDIUM \| No regime-conditional parameter tuning (RSI 30/70 fixed across regi | INLINE-ONLY | - |
| **BUG-130** | \| MEDIUM \| No threshold calibration; all thresholds (RSI, MACD, Bollinger, siz | INLINE-ONLY | - |
| **BUG-131** | \| MEDIUM \| No earnings proximity filter; trades open within 0-3 days of earnin | INLINE-ONLY | - |
| **BUG-132** | \| MEDIUM \| No FOMC/CPI day filter; new entries on high-impact days \| | INLINE-ONLY | - |
| **BUG-133** | \| MEDIUM \| No cross-day cooldown after stop-out; can re-enter same ticker next | INLINE-ONLY | - |
| **BUG-134** | \| MEDIUM \| No correlation-aware concentration filter; 10 high-beta tech longs  | INLINE-ONLY | - |
| **BUG-135** | \| MEDIUM \| Liquidity filter runs at universe load only, not at entry time; sta | INLINE-ONLY | - |
| **BUG-136** | \| MEDIUM \| No bid-ask spread filter; backtest assumes zero spread \| | INLINE-ONLY | - |
| **BUG-137** | \| LOW \| Agent context lacks historical analogues — no "last 5 times this strat | INLINE-ONLY | - |
| **BUG-138** | \| LOW \| Agent context lacks news headlines as text — sentiment is number only, | INLINE-ONLY | - |
| **BUG-139** | to BUG-150) | INLINE-ONLY | - |
| **BUG-140** | MEDIUM** — No Quality strategy family (ROE, accruals, low debt) | INLINE-ONLY | - |
| **BUG-141** | HIGH** — No Volatility-based strategies (vol-targeting, vol carry) | INLINE-ONLY | - |
| **BUG-142** | HIGH** — No Event-driven strategies (PEAD, M&A arb, index inclusion) | INLINE-ONLY | - |
| **BUG-143** | MEDIUM** — No Macro/Cross-asset strategies | INLINE-ONLY | - |
| **BUG-144** | HIGH** — Smart-money signals are binary gates, not continuous strategy inputs | INLINE-ONLY | - |
| **BUG-145** | HIGH** — No ICT/SMC strategy family (8 core concepts, 16 derived strategies) | INLINE-ONLY | - |
| **BUG-146** | HIGH** — No Volume Profile / VPVR strategies | INLINE-ONLY | - |
| **BUG-147** | MEDIUM** — No Anchored VWAP strategies | INLINE-ONLY | - |
| **BUG-148** | MEDIUM** — No Sentiment/Narrative rule strategies (only agent-mediated) | INLINE-ONLY | - |
| **BUG-149** | MEDIUM** — No Calendar/Seasonal strategies (FOMC, January, sell-in-May) | INLINE-ONLY | - |
| **BUG-150** | ) | INLINE-ONLY | - |
| **BUG-151** | to BUG-159) | INLINE-ONLY | - |
| **BUG-152** | HIGH** — Volume Profile (POC, VAH, VAL, HVN, LVN) not computed | INLINE-ONLY | - |
| **BUG-153** | MEDIUM** — Cumulative Volume Delta (CVD) not computed | INLINE-ONLY | - |
| **BUG-154** | HIGH** — Relative Strength vs sector and SPY not computed (planned for 1C, recom | INLINE-ONLY | - |
| **BUG-155** | MEDIUM** — Per-ticker volatility regime not computed | INLINE-ONLY | - |
| **BUG-156** | HIGH** — Post-Earnings Announcement Drift (PEAD) tracking absent | INLINE-ONLY | - |
| **BUG-157** | MEDIUM** — News headlines not passed to agents as text (only sentiment number) | INLINE-ONLY | - |
| **BUG-158** | LOW** — Implied volatility / Volatility Risk Premium signals absent (Phase 1C+) | INLINE-ONLY | - |
| **BUG-159** | ) | INLINE-ONLY | - |
| **BUG-160** | to BUG-167) | INLINE-ONLY | - |
| **BUG-161** | HIGH** — Fair Value Gap (FVG) detection absent | INLINE-ONLY | - |
| **BUG-162** | HIGH** — Liquidity Sweep / Stop Hunt detection absent | INLINE-ONLY | - |
| **BUG-163** | MEDIUM** — Displacement filter absent (used as quality filter for OB/FVG) | INLINE-ONLY | - |
| **BUG-164** | MEDIUM** — Breaker Block detection absent | INLINE-ONLY | - |
| **BUG-165** | MEDIUM** — Premium/Discount zones not computed | INLINE-ONLY | - |
| **BUG-166** | MEDIUM** — Optimal Trade Entry (OTE) Fibonacci zone not computed | INLINE-ONLY | - |
| **BUG-167** | ) | INLINE-ONLY | - |
| **BUG-168** | to BUG-177) | INLINE-ONLY | - |
| **BUG-169** | HIGH** — No correlation-adjusted concentration limits | INLINE-ONLY | - |
| **BUG-170** | MEDIUM** — No drawdown-aware position sizing | INLINE-ONLY | - |
| **BUG-171** | MEDIUM** — No risk parity allocation across strategies | INLINE-ONLY | - |
| **BUG-172** | MEDIUM** — No walk-forward parameter optimization (all params static) | INLINE-ONLY | - |
| **BUG-173** | MEDIUM** — No online learning / feedback loop from live performance | INLINE-ONLY | - |
| **BUG-174** | LOW** — No execution algorithm sophistication (acceptable at $10K scale) | INLINE-ONLY | - |
| **BUG-175** | HIGH** — No regime-conditional strategy weighting (smooth mixture) | INLINE-ONLY | - |
| **BUG-176** | MEDIUM** — No ML enhancement layer (acceptable; agents are intended substitute) | INLINE-ONLY | - |
| **BUG-177** | ) | INLINE-ONLY | - |
| **BUG-192** | ) | INLINE-ONLY | - |
| **BUG-193** | NEW) | INLINE-ONLY | - |
| **BUG-194** | NEW) | INLINE-ONLY | - |
| **BUG-195** | NEW) | INLINE-ONLY | - |
| **BUG-196** | NEW) | INLINE-ONLY | - |
| **BUG-197** | NEW) | INLINE-ONLY | - |
| **BUG-198** | (NEW) · CRITICAL — No structural PIT data loader; each data source uses ad-hoc P | INLINE-ONLY | - |

---
*Regenerated April 2026 after Pass 46.*