# AUDIT_TRIAGE.md — Pending Decision Prioritization
**Generated:** April 2026 (post-Pass 41)
**Decisions covered:** 147 PENDING (matches AUDIT_INDEX.md as of commit 6b095568)
**Source decisions:** DECISION-062, plus 014-038 (Group B/C/D/E/F/G), 063-116 (Pass 39 batches X1-X8), 117-160 (Pass 40), 161-185 (Pass 41)

**How to read this file:**
- **Impact (1-10):** my estimate of how much each decision moves the needle on system quality, risk reduction, or unblocking work
- **Eng Cost (days):** rough engineer-days to implement including tests
- **Review (min):** estimated time owner needs to read context, weigh tradeoffs, decide
- **Phase 0.A blocker:** YES means this needs to resolve before Phase 0.A implementation can start
- **Impact/Cost ratio:** higher = better leverage; sort by this for efficient prioritization

**Honest disclaimers:**
- These estimates are my best-effort, not measured. Owner sanity-checks.
- Eng days assume single-developer focused work, no context-switching cost.
- Review minutes assume owner has prior context (skim AUDIT.md section first).
- Impact ratings are subjective; owner judgment overrides.

---

## Top 30 Highest Impact/Cost Ratio (Approve First)

| Rank | Decision | Title | Impact | Eng Days | Review Min | Phase 0.A Blocker | Ratio | Rationale |
|---|---|---|---|---|---|---|---|---|
| 1 | **DECISION-152** | Hold-out final test period (never touched during a | 9 | 0 | 10 | 🔴 YES | 18.0 | Hold-out test period — critical for honesty, but cost is jus |
| 2 | **DECISION-084** | Audit flag at 70% win rate | 7 | 0 | 5 | 🔴 YES | 14.0 | Audit flag at 70% win rate — config change |
| 3 | **DECISION-164** | Pairwise tradeoff matrix between decision batches  | 10 | 1 | 30 | 🔴 YES | 10.0 | Impact-vs-cost matrix — TRIAGE TOOL (this output) |
| 4 | **DECISION-031** | Codespace/Cloud workflow vs local | 5 | 0 | 10 | no | 10.0 | Codespace vs local — current state works, formal decision de |
| 5 | **DECISION-028** | Stage 3 paper trading duration | 5 | 0 | 10 | no | 10.0 | Stage 3 paper duration — operational decision, no eng |
| 6 | **DECISION-029** | Stage 4 starting capital | 5 | 0 | 10 | no | 10.0 | Stage 4 starting capital — owner decision, no eng |
| 7 | **DECISION-156** | Commit message references explicit CHECKLIST items | 5 | 0 | 5 | no | 10.0 | Commit message CHECKLIST refs — process discipline |
| 8 | **DECISION-169** | Owner skills gap audit (statistical, SRE, tax, etc | 5 | 0 | 30 | no | 10.0 | Owner skills gap audit — owner-facing |
| 9 | **DECISION-080** | t-stat + Bonferroni | 9 | 1 | 15 | 🔴 YES | 9.0 | t-stat + Bonferroni — fundamental for Stage 1 results validi |
| 10 | **DECISION-131** | Agent value-add minimum (Sharpe improvement >=0.2  | 9 | 1 | 10 | 🔴 YES | 9.0 | Agent value-add minimum (closes Stage 2 question) — already  |
| 11 | **DECISION-014** | Phase 1B passing criteria adjustments | 8 | 1 | 20 | 🔴 YES | 8.0 | Phase 1B passing criteria — drives Stage 1 baseline pass/fai |
| 12 | **DECISION-094** | Secrets manager | 8 | 1 | 10 | no | 8.0 | Secrets manager — Stage 3+ requirement |
| 13 | **DECISION-082** | Stress-test pass requirements (2008/2020/2022) | 8 | 1 | 10 | no | 8.0 | Stress-test pass requirements — see DEC-158 for Black Swan e |
| 14 | **DECISION-077** | Portfolio drawdown breaker | 8 | 1 | 10 | no | 8.0 | Portfolio drawdown breaker — kill switch |
| 15 | **DECISION-073** | Adopt Quiver pre-built composites | 8 | 1 | 10 | 🔴 YES | 8.0 | Adopt Quiver pre-built composites — saves duplicate work |
| 16 | **DECISION-129** | Live-vs-backtest Sharpe equivalence criterion (wit | 8 | 1 | 10 | no | 8.0 | Live-vs-backtest Sharpe equivalence — Stage 3 gate |
| 17 | **DECISION-163** | Implementation cost estimate per pending decision | 8 | 1 | 30 | 🔴 YES | 8.0 | Implementation cost estimates — TRIAGE TOOL (this output) |
| 18 | **DECISION-177** | Explicit random seed in every backtest run output  | 8 | 1 | 10 | 🔴 YES | 8.0 | Random seeds + reproducibility test — easy, high-value |
| 19 | **DECISION-035** | Tax classification approach (Canadian) | 4 | 0 | 30 | no | 8.0 | Tax classification (Canadian) — needs CPA consult |
| 20 | **DECISION-126** | Document time-resolution limitations of circuit br | 4 | 0 | 5 | no | 8.0 | Document time-resolution limitations — documentation |
| 21 | **DECISION-165** | Solo PR review checklist before merge to main | 4 | 0 | 5 | no | 8.0 | Solo PR review checklist — discipline |
| 22 | **DECISION-167** | Retrospective cadence (every N audit passes) | 4 | 0 | 10 | no | 8.0 | Retrospective cadence — process |
| 23 | **DECISION-034** | Daily loss limits for live trading | 7 | 1 | 15 | no | 7.0 | Daily loss limits — protects real money in Stage 4 |
| 24 | **DECISION-038** | Layered execution with iteration budgets | 7 | 1 | 15 | 🔴 YES | 7.0 | Layered execution budgets — Phase 0 sequencing |
| 25 | **DECISION-083** | Min trades floor 300 independent positions | 7 | 1 | 10 | 🔴 YES | 7.0 | Min trades floor 300 independent — closes L99 row inflation  |
| 26 | **DECISION-090** | Max sector exposure cap | 7 | 1 | 10 | no | 7.0 | Max sector exposure cap — diversification |
| 27 | **DECISION-079** | Reconcile Level 2 earnings gap with earnings_toler | 7 | 1 | 10 | 🔴 YES | 7.0 | Reconcile L2 earnings gap with earnings_tolerant — fixes des |
| 28 | **DECISION-153** | Regime-stratified train/test splits | 7 | 1 | 10 | 🔴 YES | 7.0 | Regime-stratified train/test splits — methodology |
| 29 | **DECISION-155** | vs-SPY comparison in all backtest reports | 7 | 1 | 10 | 🔴 YES | 7.0 | vs-SPY comparison in all reports — easy, high-value |
| 30 | **DECISION-158** | Extend backtest period to 2008-2024 (16 years for  | 7 | 1 | 10 | 🔴 YES | 7.0 | Extend backtest to 2008-2024 — captures crisis periods, just |

---

## All 147 Pending Decisions — Sorted by Impact/Cost Ratio

| Decision | Title | Impact | Eng Days | Review Min | Phase 0.A Blocker | Ratio |
|---|---|---|---|---|---|---|
| **DECISION-152** | Hold-out final test period (never touched during audits) | 9 | 0 | 10 | 🔴 | 18.0 |
| **DECISION-084** | Audit flag at 70% win rate | 7 | 0 | 5 | 🔴 | 14.0 |
| **DECISION-164** | Pairwise tradeoff matrix between decision batches (impact vs | 10 | 1 | 30 | 🔴 | 10.0 |
| **DECISION-031** | Codespace/Cloud workflow vs local | 5 | 0 | 10 |   | 10.0 |
| **DECISION-028** | Stage 3 paper trading duration | 5 | 0 | 10 |   | 10.0 |
| **DECISION-029** | Stage 4 starting capital | 5 | 0 | 10 |   | 10.0 |
| **DECISION-156** | Commit message references explicit CHECKLIST items followed | 5 | 0 | 5 |   | 10.0 |
| **DECISION-169** | Owner skills gap audit (statistical, SRE, tax, etc.) | 5 | 0 | 30 |   | 10.0 |
| **DECISION-080** | t-stat + Bonferroni | 9 | 1 | 15 | 🔴 | 9.0 |
| **DECISION-131** | Agent value-add minimum (Sharpe improvement >=0.2 over rules | 9 | 1 | 10 | 🔴 | 9.0 |
| **DECISION-014** | Phase 1B passing criteria adjustments | 8 | 1 | 20 | 🔴 | 8.0 |
| **DECISION-094** | Secrets manager | 8 | 1 | 10 |   | 8.0 |
| **DECISION-082** | Stress-test pass requirements (2008/2020/2022) | 8 | 1 | 10 |   | 8.0 |
| **DECISION-077** | Portfolio drawdown breaker | 8 | 1 | 10 |   | 8.0 |
| **DECISION-073** | Adopt Quiver pre-built composites | 8 | 1 | 10 | 🔴 | 8.0 |
| **DECISION-129** | Live-vs-backtest Sharpe equivalence criterion (within 0.3 to | 8 | 1 | 10 |   | 8.0 |
| **DECISION-163** | Implementation cost estimate per pending decision | 8 | 1 | 30 | 🔴 | 8.0 |
| **DECISION-177** | Explicit random seed in every backtest run output (reproduci | 8 | 1 | 10 | 🔴 | 8.0 |
| **DECISION-035** | Tax classification approach (Canadian) | 4 | 0 | 30 |   | 8.0 |
| **DECISION-126** | Document time-resolution limitations of circuit breakers | 4 | 0 | 5 |   | 8.0 |
| **DECISION-165** | Solo PR review checklist before merge to main | 4 | 0 | 5 |   | 8.0 |
| **DECISION-167** | Retrospective cadence (every N audit passes) | 4 | 0 | 10 |   | 8.0 |
| **DECISION-034** | Daily loss limits for live trading | 7 | 1 | 15 |   | 7.0 |
| **DECISION-038** | Layered execution with iteration budgets | 7 | 1 | 15 | 🔴 | 7.0 |
| **DECISION-083** | Min trades floor 300 independent positions | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-090** | Max sector exposure cap | 7 | 1 | 10 |   | 7.0 |
| **DECISION-079** | Reconcile Level 2 earnings gap with earnings_tolerant | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-153** | Regime-stratified train/test splits | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-155** | vs-SPY comparison in all backtest reports | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-158** | Extend backtest period to 2008-2024 (16 years for crisis cov | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-173** | Adopt ruff + black + isort + mypy as CI gates | 7 | 1 | 10 |   | 7.0 |
| **DECISION-180** | Pre-market and open-of-day operational checklist | 7 | 1 | 10 |   | 7.0 |
| **DECISION-113** | Trade journal + research log + failure log | 6 | 1 | 10 |   | 6.0 |
| **DECISION-085** | Define macro correlation precisely | 6 | 1 | 10 | 🔴 | 6.0 |
| **DECISION-116** | Cash management protocol (idle cash to SGOV/T-bills) | 6 | 1 | 10 |   | 6.0 |
| **DECISION-075** | Adverse-excursion-from-peak breaker | 6 | 1 | 10 |   | 6.0 |
| **DECISION-123** | Apply exponential decay to smart money signal weights | 6 | 1 | 10 |   | 6.0 |
| **DECISION-132** | Annual Sharpe variance < 0.5 stability requirement | 6 | 1 | 10 |   | 6.0 |
| **DECISION-172** | All numerical constants extracted to config | 6 | 1 | 10 |   | 6.0 |
| **DECISION-162** | Per-decision time-to-approve estimate + owner-approval-budge | 10 | 2 | 30 | 🔴 | 5.0 |
| **DECISION-105** | Spinoff detector | 5 | 1 | 5 |   | 5.0 |
| **DECISION-072** | Separate WSB from smart money | 5 | 1 | 10 |   | 5.0 |
| **DECISION-121** | Exit comparison report includes side-by-side exit dates/pric | 5 | 1 | 10 |   | 5.0 |
| **DECISION-127** | Define recovery rules from each circuit breaker level (coold | 5 | 1 | 10 |   | 5.0 |
| **DECISION-136** | Portfolio rebalancing frequency policy | 5 | 1 | 10 |   | 5.0 |
| **DECISION-166** | HANDOFF.md template specification | 5 | 1 | 15 |   | 5.0 |
| **DECISION-062** | Output schema translation: TradingAgents 5-tier → position_s | 9 | 2 | 20 | 🔴 | 4.5 |
| **DECISION-063** | Universe refresh automation | 9 | 2 | 10 | 🔴 | 4.5 |
| **DECISION-081** | Sharpe + Sortino + transaction cost sensitivity | 9 | 2 | 15 | 🔴 | 4.5 |
| **DECISION-037** | Characterization-test-first approach (Phase A) | 8 | 2 | 15 | 🔴 | 4.0 |
| **DECISION-096** | Backtest reproducibility (code + data + config hash) | 8 | 2 | 10 | 🔴 | 4.0 |
| **DECISION-110** | Deflated Sharpe (Bailey et al.) | 8 | 2 | 15 | 🔴 | 4.0 |
| **DECISION-088** | Portfolio vol target 15% | 8 | 2 | 15 |   | 4.0 |
| **DECISION-091** | Drawdown re-sizing | 8 | 2 | 15 |   | 4.0 |
| **DECISION-139** | Remote kill switch (email-based STOP) | 8 | 2 | 10 |   | 4.0 |
| **DECISION-036** | Audit document maintenance going forward | 4 | 1 | 10 |   | 4.0 |
| **DECISION-154** | Market structure change tracker (quarterly) | 4 | 1 | 30 |   | 4.0 |
| **DECISION-168** | Incident postmortem template | 4 | 1 | 10 |   | 4.0 |
| **DECISION-016** | Threshold calibration scope (BUG-130) | 7 | 2 | 15 | 🔴 | 3.5 |
| **DECISION-019** | Liquidity filter timing (BUG-135) | 7 | 2 | 15 |   | 3.5 |
| **DECISION-022** | Drawdown-aware position sizing (BUG-170) | 7 | 2 | 15 |   | 3.5 |
| **DECISION-103** | Auto-populate Tier 2 universe (spinoffs, IPOs, $5B+) | 7 | 2 | 10 |   | 3.5 |
| **DECISION-097** | Reconciliation job (daily position vs broker) | 7 | 2 | 10 |   | 3.5 |
| **DECISION-089** | Max correlation cap between positions | 7 | 2 | 15 |   | 3.5 |
| **DECISION-068** | Bootstrap CI + pairwise significance for exit comparison | 7 | 2 | 10 | 🔴 | 3.5 |
| **DECISION-069** | Per-regime exit selection | 7 | 2 | 15 |   | 3.5 |
| **DECISION-076** | Factor exposure breaker | 7 | 2 | 15 |   | 3.5 |
| **DECISION-119** | Per-trade explainability dict (primary_signal, dominant_mult | 7 | 2 | 15 |   | 3.5 |
| **DECISION-120** | Automatic loss attribution report — top 10 losing trades per | 7 | 2 | 10 |   | 3.5 |
| **DECISION-130** | Capacity stress test (5x capital, Sharpe drop <0.3) | 7 | 2 | 10 |   | 3.5 |
| **DECISION-133** | Max gross long/short/net exposure caps | 7 | 2 | 15 |   | 3.5 |
| **DECISION-181** | End-of-day reconciliation report (positions/P&L/agents/regim | 7 | 2 | 15 |   | 3.5 |
| **DECISION-182** | Weekly auto-generated performance review | 7 | 2 | 10 |   | 3.5 |
| **DECISION-183** | Memoization layer for signal computation (LRU cache) | 7 | 2 | 15 |   | 3.5 |
| **DECISION-065** | Validate stored data quality before Phase 1B-α | 9 | 3 | 15 | 🔴 | 3.0 |
| **DECISION-086** | Fractional Kelly position sizing | 9 | 3 | 20 |   | 3.0 |
| **DECISION-087** | Vol-targeted sizing per-position (closes 023) | 9 | 3 | 15 |   | 3.0 |
| **DECISION-043** | Retune framework | 6 | 2 | 15 |   | 3.0 |
| **DECISION-018** | Cooldown after stop-out (BUG-133) | 6 | 2 | 15 |   | 3.0 |
| **DECISION-112** | Disaster recovery plan + incident runbook | 6 | 2 | 15 |   | 3.0 |
| **DECISION-115** | Tail hedging consideration | 6 | 2 | 20 |   | 3.0 |
| **DECISION-078** | Stop-out cluster breaker | 6 | 2 | 15 |   | 3.0 |
| **DECISION-074** | Polygon block trades / dark pool eval | 6 | 2 | 15 |   | 3.0 |
| **DECISION-122** | Per-exit-method slippage modeling | 6 | 2 | 10 |   | 3.0 |
| **DECISION-135** | Per-ticker cumulative max-loss cap (rolling 30-day) | 6 | 2 | 15 |   | 3.0 |
| **DECISION-137** | Backtest output schema versioning + migration path | 6 | 2 | 10 |   | 3.0 |
| **DECISION-140** | Structured JSON logging standard | 6 | 2 | 10 |   | 3.0 |
| **DECISION-144** | Stock-vs-sector momentum delta as breakdown variable | 6 | 2 | 10 |   | 3.0 |
| **DECISION-160** | Multi-vendor fallback chain per data source | 6 | 2 | 15 |   | 3.0 |
| **DECISION-170** | Type hints + mypy in CI | 6 | 2 | 15 |   | 3.0 |
| **DECISION-174** | Strategy classification by trigger type (catalyst/technical/ | 6 | 2 | 15 |   | 3.0 |
| **DECISION-175** | Signal persistence weighting (consecutive-day signals) | 6 | 2 | 15 |   | 3.0 |
| **DECISION-179** | Memory profiling per backtest run + memory cap enforcement | 6 | 2 | 10 |   | 3.0 |
| **DECISION-020** | News API selection (depends on 002 eval results) | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-023** | Vol-targeted position sizing (BUG-168) | 8 | 3 | 20 |   | 2.7 |
| **DECISION-101** | Earnings strategies post-Phase 0.A | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-114** | Live-vs-backtest divergence monitoring | 8 | 3 | 15 |   | 2.7 |
| **DECISION-109** | Rolling 5yr/1yr walk-forward | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-070** | Portfolio-level exit logic | 8 | 3 | 15 |   | 2.7 |
| **DECISION-066** | Granularity standard for all backtest outputs | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-118** | Prefetch full cross-asset macro (VIX direct, DXY, GLD, oil,  | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-124** | Cross-source smart money clusters (insider+congressional+13F | 8 | 3 | 15 |   | 2.7 |
| **DECISION-146** | Corporate actions handler (split/dividend/spinoff/rename) | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-021** | Tier system simplification | 5 | 2 | 20 |   | 2.5 |
| **DECISION-117** | Add file-level checksum + last-validated timestamp to cache | 5 | 2 | 10 |   | 2.5 |
| **DECISION-125** | Add Form 144 prefetch (proposed sales — leading indicator) | 5 | 2 | 10 |   | 2.5 |
| **DECISION-138** | Cold-start CI test (fresh container in <30 min) | 5 | 2 | 10 |   | 2.5 |
| **DECISION-161** | Decision dependency graph (DAG) | 5 | 2 | 15 |   | 2.5 |
| **DECISION-095** | Monitoring + alerting | 7 | 3 | 15 |   | 2.3 |
| **DECISION-111** | Stationarity / structural break tests | 7 | 3 | 15 |   | 2.3 |
| **DECISION-107** | Regime probability (not hard label) | 7 | 3 | 15 |   | 2.3 |
| **DECISION-134** | USD/CAD currency exposure tracking + optional FX hedge | 7 | 3 | 20 |   | 2.3 |
| **DECISION-147** | Delisting registry + survivorship bias correction | 7 | 3 | 10 |   | 2.3 |
| **DECISION-064** | Phase 0.A prefetch checklist | 10 | 5 | 30 | 🔴 | 2.0 |
| **DECISION-100** | 17+ categorical breakdown variables | 8 | 4 | 20 | 🔴 | 2.0 |
| **DECISION-092** | Slippage model = f(size%ADV, vol) | 8 | 4 | 15 |   | 2.0 |
| **DECISION-071** | Smart money refinement (officer roles, 10b5-1 filter, etc.) | 8 | 4 | 20 |   | 2.0 |
| **DECISION-106** | Regime inputs 2 → 8+ | 8 | 4 | 20 |   | 2.0 |
| **DECISION-184** | Parallel backtest execution for Stage 1 baseline | 8 | 4 | 15 |   | 2.0 |
| **DECISION-015** | Strategy correlation analysis methodology | 6 | 3 | 20 |   | 2.0 |
| **DECISION-024** | Correlation-adjusted concentration limits (BUG-169) | 6 | 3 | 20 |   | 2.0 |
| **DECISION-033** | Email approval system specifics | 6 | 3 | 15 |   | 2.0 |
| **DECISION-104** | Auto-populate Tier 3 momentum watchlist | 6 | 3 | 10 |   | 2.0 |
| **DECISION-128** | Dispersion-conditional circuit breaker | 6 | 3 | 15 |   | 2.0 |
| **DECISION-149** | Regime transition probability matrix | 6 | 3 | 15 |   | 2.0 |
| **DECISION-151** | Sector-level regime classification | 6 | 3 | 15 |   | 2.0 |
| **DECISION-178** | Signal lookup performance benchmark + caching strategy | 6 | 3 | 15 |   | 2.0 |
| **DECISION-171** | Docstring standard + sphinx documentation | 4 | 2 | 10 |   | 2.0 |
| **DECISION-025** | Regime-conditional strategy weighting (BUG-175) | 7 | 4 | 20 |   | 1.8 |
| **DECISION-067** | Add 9 missing exit methods | 7 | 4 | 15 |   | 1.8 |
| **DECISION-108** | Regime persistence model (HMM or smoothing) | 7 | 4 | 15 |   | 1.8 |
| **DECISION-150** | Multi-asset regime detection (equity+credit+commodity+curren | 7 | 4 | 20 |   | 1.8 |
| **DECISION-176** | Meta-strategies (boolean AND/OR combinations of base strateg | 7 | 4 | 20 |   | 1.8 |
| **DECISION-026** | Walk-forward parameter re-optimization (BUG-172) | 5 | 3 | 15 |   | 1.7 |
| **DECISION-142** | Optional market-neutral construction (long stock + short SPY | 5 | 3 | 20 |   | 1.7 |
| **DECISION-148** | Stock-specific adaptive momentum lookback (vol-adjusted) | 5 | 3 | 15 |   | 1.7 |
| **DECISION-157** | Synthetic broker outage testing during Stage 3 (chaos engine | 5 | 3 | 15 |   | 1.7 |
| **DECISION-159** | Regulatory event handler (SEC/DOJ investigations, sanctions) | 5 | 3 | 20 |   | 1.7 |
| **DECISION-093** | Migrate live to AWS/GCP/DO before Stage 4 | 8 | 5 | 20 |   | 1.6 |
| **DECISION-141** | Sector-neutral hedge overlay (long position + short sector E | 6 | 4 | 20 |   | 1.5 |
| **DECISION-143** | IPO/lockup/secondary offering systematic framework | 6 | 4 | 20 |   | 1.5 |
| **DECISION-098** | Test coverage 70% before Stage 3 | 7 | 5 | 15 | 🔴 | 1.4 |
| **DECISION-102** | Market-Level / Correlation-Factor strategies | 8 | 6 | 30 |   | 1.3 |
| **DECISION-145** | IV delta vs historical pre-earnings pattern as signal | 5 | 4 | 20 |   | 1.2 |
| **DECISION-185** | Incremental backtest updates for daily data refresh | 5 | 4 | 15 |   | 1.2 |
| **DECISION-099** | 11 missing strategy categories (Pairs, Calendar, Cross-Asset | 7 | 8 | 20 |   | 0.9 |
| **DECISION-027** | Online learning / feedback loop (BUG-173) | 3 | 5 | 15 |   | 0.6 |

---

## Phase 0.A Critical Path (Blockers Only)

These decisions block Phase 0.A implementation. Resolve these first to unblock the next milestone.

| Decision | Title | Impact | Eng Days | Why blocking |
|---|---|---|---|---|
| **DECISION-164** | Pairwise tradeoff matrix between decision batches  | 10 | 1 | Impact-vs-cost matrix — TRIAGE TOOL (this output) |
| **DECISION-162** | Per-decision time-to-approve estimate + owner-appr | 10 | 2 | Time-to-approve estimates — TRIAGE TOOL (this output) |
| **DECISION-064** | Phase 0.A prefetch checklist | 10 | 5 | Phase 0.A prefetch checklist — comprehensive scope |
| **DECISION-152** | Hold-out final test period (never touched during a | 9 | 0 | Hold-out test period — critical for honesty, but cost is jus |
| **DECISION-080** | t-stat + Bonferroni | 9 | 1 | t-stat + Bonferroni — fundamental for Stage 1 results validi |
| **DECISION-131** | Agent value-add minimum (Sharpe improvement >=0.2  | 9 | 1 | Agent value-add minimum (closes Stage 2 question) — already  |
| **DECISION-062** | Output schema translation: TradingAgents 5-tier →  | 9 | 2 | Output schema translation — required for TradingAgents integ |
| **DECISION-063** | Universe refresh automation | 9 | 2 | Universe refresh automation — without this universe goes sta |
| **DECISION-081** | Sharpe + Sortino + transaction cost sensitivity | 9 | 2 | Sharpe + Sortino + cost sensitivity — passing criteria upgra |
| **DECISION-065** | Validate stored data quality before Phase 1B-α | 9 | 3 | Validate stored data quality — fixes yield_curve schema bug  |
| **DECISION-014** | Phase 1B passing criteria adjustments | 8 | 1 | Phase 1B passing criteria — drives Stage 1 baseline pass/fai |
| **DECISION-073** | Adopt Quiver pre-built composites | 8 | 1 | Adopt Quiver pre-built composites — saves duplicate work |
| **DECISION-163** | Implementation cost estimate per pending decision | 8 | 1 | Implementation cost estimates — TRIAGE TOOL (this output) |
| **DECISION-177** | Explicit random seed in every backtest run output  | 8 | 1 | Random seeds + reproducibility test — easy, high-value |
| **DECISION-037** | Characterization-test-first approach (Phase A) | 8 | 2 | Characterization tests-first — gates Phase 0 implementation  |
| **DECISION-096** | Backtest reproducibility (code + data + config has | 8 | 2 | Backtest reproducibility (code+data+config hash) — applies t |
| **DECISION-110** | Deflated Sharpe (Bailey et al.) | 8 | 2 | Deflated Sharpe — multi-strategy testing rigor |
| **DECISION-020** | News API selection (depends on 002 eval results) | 8 | 3 | News API choice gates Phase 0.A News Analyst |
| **DECISION-101** | Earnings strategies post-Phase 0.A | 8 | 3 | Earnings strategies post-Phase 0.A — needs earnings data fir |
| **DECISION-109** | Rolling 5yr/1yr walk-forward | 8 | 3 | Rolling 5yr/1yr walk-forward — Stage 1 design |
| **DECISION-066** | Granularity standard for all backtest outputs | 8 | 3 | Granularity standard for backtest outputs — applies L106 |
| **DECISION-118** | Prefetch full cross-asset macro (VIX direct, DXY,  | 8 | 3 | Cross-asset macro prefetch — fills VIX/DXY/sector ETF gap |
| **DECISION-146** | Corporate actions handler (split/dividend/spinoff/ | 8 | 3 | Corporate actions handler — PIT correctness |
| **DECISION-100** | 17+ categorical breakdown variables | 8 | 4 | 17+ categorical breakdowns — needed for granular reporting |
| **DECISION-084** | Audit flag at 70% win rate | 7 | 0 | Audit flag at 70% win rate — config change |
| **DECISION-038** | Layered execution with iteration budgets | 7 | 1 | Layered execution budgets — Phase 0 sequencing |
| **DECISION-083** | Min trades floor 300 independent positions | 7 | 1 | Min trades floor 300 independent — closes L99 row inflation  |
| **DECISION-079** | Reconcile Level 2 earnings gap with earnings_toler | 7 | 1 | Reconcile L2 earnings gap with earnings_tolerant — fixes des |
| **DECISION-153** | Regime-stratified train/test splits | 7 | 1 | Regime-stratified train/test splits — methodology |
| **DECISION-155** | vs-SPY comparison in all backtest reports | 7 | 1 | vs-SPY comparison in all reports — easy, high-value |
| **DECISION-158** | Extend backtest period to 2008-2024 (16 years for  | 7 | 1 | Extend backtest to 2008-2024 — captures crisis periods, just |
| **DECISION-016** | Threshold calibration scope (BUG-130) | 7 | 2 | Threshold calibration scope — affects Stage 1 design |
| **DECISION-068** | Bootstrap CI + pairwise significance for exit comp | 7 | 2 | Bootstrap CI for exits — statistical rigor |
| **DECISION-098** | Test coverage 70% before Stage 3 | 7 | 5 | Test coverage 70% — gates Stage 3, but starts in Phase 0 |
| **DECISION-085** | Define macro correlation precisely | 6 | 1 | Define macro correlation precisely — closes ambiguity |

**Phase 0.A blocker totals:** 35 decisions, ~67 eng-days to implement.

---

## Zero-Cost Approvals (No Engineering Work — Owner Just Decides)

These decisions are pure judgment calls or documentation. No code work needed.

| Decision | Title | Impact | Review Min |
|---|---|---|---|
| **DECISION-152** | Hold-out final test period (never touched during audits) | 9 | 10 |
| **DECISION-084** | Audit flag at 70% win rate | 7 | 5 |
| **DECISION-031** | Codespace/Cloud workflow vs local | 5 | 10 |
| **DECISION-028** | Stage 3 paper trading duration | 5 | 10 |
| **DECISION-029** | Stage 4 starting capital | 5 | 10 |
| **DECISION-156** | Commit message references explicit CHECKLIST items followed | 5 | 5 |
| **DECISION-169** | Owner skills gap audit (statistical, SRE, tax, etc.) | 5 | 30 |
| **DECISION-035** | Tax classification approach (Canadian) | 4 | 30 |
| **DECISION-126** | Document time-resolution limitations of circuit breakers | 4 | 5 |
| **DECISION-165** | Solo PR review checklist before merge to main | 4 | 5 |
| **DECISION-167** | Retrospective cadence (every N audit passes) | 4 | 10 |

---

## Defer Candidates (Low Impact/Cost Ratio — Consider Postponing)

These have low leverage. Owner may rationally defer to focus on higher-leverage work.

| Decision | Title | Impact | Eng Days | Ratio |
|---|---|---|---|---|
| **DECISION-171** | Docstring standard + sphinx documentation | 4 | 2 | 2.0 |
| **DECISION-025** | Regime-conditional strategy weighting (BUG-175) | 7 | 4 | 1.8 |
| **DECISION-067** | Add 9 missing exit methods | 7 | 4 | 1.8 |
| **DECISION-108** | Regime persistence model (HMM or smoothing) | 7 | 4 | 1.8 |
| **DECISION-150** | Multi-asset regime detection (equity+credit+commodity+curren | 7 | 4 | 1.8 |
| **DECISION-176** | Meta-strategies (boolean AND/OR combinations of base strateg | 7 | 4 | 1.8 |
| **DECISION-026** | Walk-forward parameter re-optimization (BUG-172) | 5 | 3 | 1.7 |
| **DECISION-142** | Optional market-neutral construction (long stock + short SPY | 5 | 3 | 1.7 |
| **DECISION-148** | Stock-specific adaptive momentum lookback (vol-adjusted) | 5 | 3 | 1.7 |
| **DECISION-157** | Synthetic broker outage testing during Stage 3 (chaos engine | 5 | 3 | 1.7 |
| **DECISION-159** | Regulatory event handler (SEC/DOJ investigations, sanctions) | 5 | 3 | 1.7 |
| **DECISION-093** | Migrate live to AWS/GCP/DO before Stage 4 | 8 | 5 | 1.6 |
| **DECISION-141** | Sector-neutral hedge overlay (long position + short sector E | 6 | 4 | 1.5 |
| **DECISION-143** | IPO/lockup/secondary offering systematic framework | 6 | 4 | 1.5 |
| **DECISION-098** | Test coverage 70% before Stage 3 | 7 | 5 | 1.4 |
| **DECISION-102** | Market-Level / Correlation-Factor strategies | 8 | 6 | 1.3 |
| **DECISION-145** | IV delta vs historical pre-earnings pattern as signal | 5 | 4 | 1.2 |
| **DECISION-185** | Incremental backtest updates for daily data refresh | 5 | 4 | 1.2 |
| **DECISION-099** | 11 missing strategy categories (Pairs, Calendar, Cross-Asset | 7 | 8 | 0.9 |
| **DECISION-027** | Online learning / feedback loop (BUG-173) | 3 | 5 | 0.6 |

---

## Summary Statistics

- Total pending decisions analyzed: **147**
- Phase 0.A blockers: **35** (~67 eng-days)
- Zero-engineering-cost decisions: **11**
- Total engineering days if ALL approved: **316** days (~63 weeks at 5d/wk)
- Total owner review time if ALL reviewed individually: **2120 minutes** (~35.3 hours)

**Recommended approach:** Approve top-30 by impact/cost ratio first (~50 eng-days, ~6 hours owner review). Defer or reject remainder pending evidence they matter.

**Phase 0.A unblock path:** Resolve the ~25 Phase 0.A blockers first (~50 eng-days) to start prefetch + baseline backtest work.

*Generated April 2026 from /tmp/decision_catalog.json. Will become stale; regenerate when status changes.*