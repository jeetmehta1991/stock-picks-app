# AUDIT_TRIAGE.md — Pending Decision Prioritization
**Last regenerated:** April 2026 (post-Pass 45, after Batch 1 approvals committed)
**Decisions covered:** 186 PENDING (matches AUDIT_INDEX.md)

**How to read:**
- **Impact (1-10):** how much each moves the needle on quality, risk, or unblocking work
- **Eng (days):** rough engineer-days to implement including tests
- **Review (min):** owner time to read context, weigh tradeoffs, decide
- **🔴 = Phase 0.A blocker**
- **Ratio:** Impact / max(Eng, 0.5). Higher = better leverage

**Caveat:** scores are best-effort. Owner judgment overrides.

---

## Top 30 by Impact/Cost Ratio (Approve First)

| Rank | Decision | Title | Impact | Eng | Review | 🔴 | Ratio | Rationale |
|---|---|---|---|---|---|---|---|---|
| 1 | **DECISION-152** | Hold-out final test period (never touched during a | 9 | 0 | 10 | 🔴 | 18.0 | Hold-out test period (no eng cost) |
| 2 | **DECISION-207** | Pre-commit minimum sample size per arm (300 paired | 9 | 0 | 15 | 🔴 | 18.0 | Pre-commit minimum sample size (300) |
| 3 | **DECISION-248** | Owner pre-commitment doc (rules owner commits to b | 6 | 0 | 30 |   | 12.0 | Owner pre-commitment doc |
| 4 | **DECISION-205** | A/B test arm design — minimum 4 arms (rules, full- | 10 | 1 | 15 | 🔴 | 10.0 | A/B test arm design - minimum 4 arms (gates Stage  |
| 5 | **DECISION-169** | Owner skills gap audit (statistical, SRE, tax, etc | 5 | 0 | 30 |   | 10.0 | Owner skills gap audit |
| 6 | **DECISION-029-C** | Real-money starting capital — DEFERRED until post- | 5 | 0 | 10 |   | 10.0 | Real-money starting capital - defer |
| 7 | **DECISION-238** | Pre/after-hours policy (recommendation: NO extende | 5 | 0 | 5 |   | 10.0 | Pre/after-hours policy |
| 8 | **DECISION-080** | t-stat + Bonferroni | 9 | 1 | 15 | 🔴 | 9.0 | t-stat + Bonferroni |
| 9 | **DECISION-131** | Agent value-add minimum (Sharpe improvement >=0.2  | 9 | 1 | 10 | 🔴 | 9.0 | Agent value-add minimum |
| 10 | **DECISION-206** | Paired A/B design — every trade evaluated by every | 9 | 1 | 10 | 🔴 | 9.0 | Paired A/B design |
| 11 | **DECISION-014** | Phase 1B passing criteria adjustments | 8 | 1 | 20 | 🔴 | 8.0 | Phase 1B passing criteria |
| 12 | **DECISION-073** | Adopt Quiver pre-built composites | 8 | 1 | 10 | 🔴 | 8.0 | Adopt Quiver pre-built composites |
| 13 | **DECISION-077** | Portfolio drawdown breaker | 8 | 1 | 10 |   | 8.0 | Portfolio drawdown breaker |
| 14 | **DECISION-082** | Stress-test pass requirements (2008/2020/2022) | 8 | 1 | 10 |   | 8.0 | Stress-test pass requirements |
| 15 | **DECISION-094** | Secrets manager | 8 | 1 | 10 |   | 8.0 | Secrets manager |
| 16 | **DECISION-129** | Live-vs-backtest Sharpe equivalence criterion (wit | 8 | 1 | 10 |   | 8.0 | Live-vs-backtest Sharpe equivalence |
| 17 | **DECISION-163** | Implementation cost estimate per pending decision | 8 | 1 | 30 | 🔴 | 8.0 | Implementation cost estimates |
| 18 | **DECISION-177** | Explicit random seed in every backtest run output  | 8 | 1 | 10 | 🔴 | 8.0 | Random seeds + reproducibility |
| 19 | **DECISION-210** | Net Sharpe contribution accounting (gross lift min | 8 | 1 | 10 | 🔴 | 8.0 | Net Sharpe contribution accounting |
| 20 | **DECISION-223** | CI gate — PR cannot merge to main without all test | 8 | 1 | 5 |   | 8.0 | CI gate - PR must pass tests |
| 21 | **DECISION-232** | Determinism test (run identical backtest twice, di | 8 | 1 | 10 | 🔴 | 8.0 | Determinism test |
| 22 | **DECISION-244** | SESSION_START.md — Claude reads first in any new s | 8 | 1 | 10 |   | 8.0 | SESSION_START.md |
| 23 | **DECISION-035** | Tax classification approach (Canadian) — Defer unt | 4 | 0 | 30 |   | 8.0 | Tax classification - needs CPA |
| 24 | **DECISION-245** | Owner experience retrospective (periodic check-in  | 4 | 0 | 30 |   | 8.0 | Owner experience retrospective |
| 25 | **DECISION-034** | Daily loss limits for live trading | 7 | 1 | 15 |   | 7.0 | Daily loss limits |
| 26 | **DECISION-038** | Layered execution with iteration budgets | 7 | 1 | 15 | 🔴 | 7.0 | Layered execution budgets |
| 27 | **DECISION-079** | Reconcile Level 2 earnings gap with earnings_toler | 7 | 1 | 10 | 🔴 | 7.0 | Reconcile L2 earnings gap |
| 28 | **DECISION-083** | Min trades floor 300 independent positions | 7 | 1 | 10 | 🔴 | 7.0 | Min trades floor 300 |
| 29 | **DECISION-090** | Max sector exposure cap | 7 | 1 | 10 |   | 7.0 | Max sector exposure cap |
| 30 | **DECISION-153** | Regime-stratified train/test splits | 7 | 1 | 10 | 🔴 | 7.0 | Regime-stratified train/test |

---

## All 186 Pending — Sorted by Ratio

| Decision | Title | Impact | Eng | Review | 🔴 | Ratio |
|---|---|---|---|---|---|---|
| **DECISION-152** | Hold-out final test period (never touched during audits) | 9 | 0 | 10 | 🔴 | 18.0 |
| **DECISION-207** | Pre-commit minimum sample size per arm (300 paired trades) b | 9 | 0 | 15 | 🔴 | 18.0 |
| **DECISION-248** | Owner pre-commitment doc (rules owner commits to before loss | 6 | 0 | 30 |   | 12.0 |
| **DECISION-205** | A/B test arm design — minimum 4 arms (rules, full-agents, no | 10 | 1 | 15 | 🔴 | 10.0 |
| **DECISION-169** | Owner skills gap audit (statistical, SRE, tax, etc.) — Owner | 5 | 0 | 30 |   | 10.0 |
| **DECISION-029-C** | Real-money starting capital — DEFERRED until post-paper-trad | 5 | 0 | 10 |   | 10.0 |
| **DECISION-238** | Pre/after-hours policy (recommendation: NO extended hours) | 5 | 0 | 5 |   | 10.0 |
| **DECISION-080** | t-stat + Bonferroni | 9 | 1 | 15 | 🔴 | 9.0 |
| **DECISION-131** | Agent value-add minimum (Sharpe improvement >=0.2 over rules | 9 | 1 | 10 | 🔴 | 9.0 |
| **DECISION-206** | Paired A/B design — every trade evaluated by every arm in pa | 9 | 1 | 10 | 🔴 | 9.0 |
| **DECISION-014** | Phase 1B passing criteria adjustments | 8 | 1 | 20 | 🔴 | 8.0 |
| **DECISION-073** | Adopt Quiver pre-built composites | 8 | 1 | 10 | 🔴 | 8.0 |
| **DECISION-077** | Portfolio drawdown breaker | 8 | 1 | 10 |   | 8.0 |
| **DECISION-082** | Stress-test pass requirements (2008/2020/2022) | 8 | 1 | 10 |   | 8.0 |
| **DECISION-094** | Secrets manager | 8 | 1 | 10 |   | 8.0 |
| **DECISION-129** | Live-vs-backtest Sharpe equivalence criterion (within 0.3 to | 8 | 1 | 10 |   | 8.0 |
| **DECISION-163** | Implementation cost estimate per pending decision | 8 | 1 | 30 | 🔴 | 8.0 |
| **DECISION-177** | Explicit random seed in every backtest run output (reproduci | 8 | 1 | 10 | 🔴 | 8.0 |
| **DECISION-210** | Net Sharpe contribution accounting (gross lift minus annuali | 8 | 1 | 10 | 🔴 | 8.0 |
| **DECISION-223** | CI gate — PR cannot merge to main without all tests passing | 8 | 1 | 5 |   | 8.0 |
| **DECISION-232** | Determinism test (run identical backtest twice, diff outputs | 8 | 1 | 10 | 🔴 | 8.0 |
| **DECISION-244** | SESSION_START.md — Claude reads first in any new session for | 8 | 1 | 10 |   | 8.0 |
| **DECISION-035** | Tax classification approach (Canadian) — Defer until CPA con | 4 | 0 | 30 |   | 8.0 |
| **DECISION-245** | Owner experience retrospective (periodic check-in on workflo | 4 | 0 | 30 |   | 8.0 |
| **DECISION-034** | Daily loss limits for live trading | 7 | 1 | 15 |   | 7.0 |
| **DECISION-038** | Layered execution with iteration budgets | 7 | 1 | 15 | 🔴 | 7.0 |
| **DECISION-079** | Reconcile Level 2 earnings gap with earnings_tolerant | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-083** | Min trades floor 300 independent positions | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-090** | Max sector exposure cap | 7 | 1 | 10 |   | 7.0 |
| **DECISION-153** | Regime-stratified train/test splits | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-155** | vs-SPY comparison in all backtest reports | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-158** | Extend backtest period to 2008-2024 (16 years for crisis cov | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-173** | Adopt ruff + black + isort + mypy as CI gates | 7 | 1 | 10 |   | 7.0 |
| **DECISION-180** | Pre-market and open-of-day operational checklist | 7 | 1 | 10 |   | 7.0 |
| **DECISION-220** | Audit sync_from_claude.yml — disable if it bypasses owner ap | 7 | 1 | 5 |   | 7.0 |
| **DECISION-221** | Test coverage measurement (pytest --cov) + CI gate | 7 | 1 | 5 |   | 7.0 |
| **DECISION-235** | Time/calendar handling spec (NYSE calendar, holidays, DST, h | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-243** | Owner Approval Queue file (pending decisions waiting on owne | 7 | 1 | 10 |   | 7.0 |
| **DECISION-075** | Adverse-excursion-from-peak breaker | 6 | 1 | 10 |   | 6.0 |
| **DECISION-085** | Define macro correlation precisely | 6 | 1 | 10 | 🔴 | 6.0 |
| **DECISION-113** | Trade journal + research log + failure log | 6 | 1 | 10 |   | 6.0 |
| **DECISION-123** | Apply exponential decay to smart money signal weights | 6 | 1 | 10 |   | 6.0 |
| **DECISION-132** | Annual Sharpe variance < 0.5 stability requirement | 6 | 1 | 10 |   | 6.0 |
| **DECISION-172** | All numerical constants extracted to config | 6 | 1 | 10 |   | 6.0 |
| **DECISION-237** | Order type policy (when MOO vs limit vs stop vs stop-limit) | 6 | 1 | 10 |   | 6.0 |
| **DECISION-242** | Distribution analysis (skewness, kurtosis, max single-trade  | 6 | 1 | 10 |   | 6.0 |
| **DECISION-250** | Edge decay assumption (discount backtest Sharpe by expected  | 6 | 1 | 10 |   | 6.0 |
| **DECISION-072** | Separate WSB from smart money | 5 | 1 | 10 |   | 5.0 |
| **DECISION-105** | Spinoff detector | 5 | 1 | 5 |   | 5.0 |
| **DECISION-121** | Exit comparison report includes side-by-side exit dates/pric | 5 | 1 | 10 |   | 5.0 |
| **DECISION-127** | Define recovery rules from each circuit breaker level (coold | 5 | 1 | 10 |   | 5.0 |
| **DECISION-136** | Portfolio rebalancing frequency policy | 5 | 1 | 10 |   | 5.0 |
| **DECISION-166** | HANDOFF.md template specification — HANDOFF template — build | 5 | 1 | 15 |   | 5.0 |
| **DECISION-214** | Quarterly re-validation of agent A/B test (model drift / cos | 5 | 1 | 10 |   | 5.0 |
| **DECISION-225** | Cache eviction policy (preserve prefetched, evict only compu | 5 | 1 | 10 |   | 5.0 |
| **DECISION-227** | Cache size monitoring + alerting (cache_size_gb metric, 80%  | 5 | 1 | 10 |   | 5.0 |
| **DECISION-236** | Position sizing precision rules (round to broker minimum inc | 5 | 1 | 10 |   | 5.0 |
| **DECISION-241** | Time-in-market metric (% in any position, % long, % short, % | 5 | 1 | 10 |   | 5.0 |
| **DECISION-062** | Output schema translation: TradingAgents 5-tier → position_s | 9 | 2 | 20 | 🔴 | 4.5 |
| **DECISION-063** | Universe refresh automation | 9 | 2 | 10 | 🔴 | 4.5 |
| **DECISION-081** | Sharpe + Sortino + transaction cost sensitivity | 9 | 2 | 15 | 🔴 | 4.5 |
| **DECISION-208** | Multi-metric A/B comparison (Sharpe + Sortino + DD + win rat | 9 | 2 | 20 | 🔴 | 4.5 |
| **DECISION-037** | Characterization-test-first approach (Phase A) | 8 | 2 | 15 | 🔴 | 4.0 |
| **DECISION-088** | Portfolio vol target 15% | 8 | 2 | 15 |   | 4.0 |
| **DECISION-091** | Drawdown re-sizing | 8 | 2 | 15 |   | 4.0 |
| **DECISION-096** | Backtest reproducibility (code + data + config hash) | 8 | 2 | 10 | 🔴 | 4.0 |
| **DECISION-110** | Deflated Sharpe (Bailey et al.) | 8 | 2 | 15 | 🔴 | 4.0 |
| **DECISION-139** | Remote kill switch (email-based STOP) | 8 | 2 | 10 |   | 4.0 |
| **DECISION-209** | Per-regime A/B verdicts — agents pass/fail separately per re | 8 | 2 | 15 | 🔴 | 4.0 |
| **DECISION-213** | Both-rationales storage (rules-only AND agent rationale stor | 8 | 2 | 10 | 🔴 | 4.0 |
| **DECISION-168** | Incident postmortem template — Incident postmortem template  | 4 | 1 | 10 |   | 4.0 |
| **DECISION-218** | Documentation audit — role of EXPLANATION/PROGRESS/UNIVERSAL | 4 | 1 | 10 |   | 4.0 |
| **DECISION-016** | Threshold calibration scope (BUG-130) | 7 | 2 | 15 | 🔴 | 3.5 |
| **DECISION-019** | Liquidity filter timing (BUG-135) | 7 | 2 | 15 |   | 3.5 |
| **DECISION-022** | Drawdown-aware position sizing (BUG-170) | 7 | 2 | 15 |   | 3.5 |
| **DECISION-068** | Bootstrap CI + pairwise significance for exit comparison | 7 | 2 | 10 | 🔴 | 3.5 |
| **DECISION-069** | Per-regime exit selection | 7 | 2 | 15 |   | 3.5 |
| **DECISION-076** | Factor exposure breaker | 7 | 2 | 15 |   | 3.5 |
| **DECISION-089** | Max correlation cap between positions | 7 | 2 | 15 |   | 3.5 |
| **DECISION-097** | Reconciliation job (daily position vs broker) | 7 | 2 | 10 |   | 3.5 |
| **DECISION-103** | Auto-populate Tier 2 universe (spinoffs, IPOs, $5B+) | 7 | 2 | 10 |   | 3.5 |
| **DECISION-119** | Per-trade explainability dict (primary_signal, dominant_mult | 7 | 2 | 15 |   | 3.5 |
| **DECISION-120** | Automatic loss attribution report — top 10 losing trades per | 7 | 2 | 10 |   | 3.5 |
| **DECISION-130** | Capacity stress test (5x capital, Sharpe drop <0.3) | 7 | 2 | 10 |   | 3.5 |
| **DECISION-133** | Max gross long/short/net exposure caps | 7 | 2 | 15 |   | 3.5 |
| **DECISION-181** | End-of-day reconciliation report (positions/P&L/agents/regim | 7 | 2 | 15 |   | 3.5 |
| **DECISION-182** | Weekly auto-generated performance review | 7 | 2 | 10 |   | 3.5 |
| **DECISION-183** | Memoization layer for signal computation (LRU cache) | 7 | 2 | 15 |   | 3.5 |
| **DECISION-224** | Cache concurrency audit (filelock under concurrent access) | 7 | 2 | 15 |   | 3.5 |
| **DECISION-249** | Strategy decay metric (rolling 6mo Sharpe per strategy; flag | 7 | 2 | 15 |   | 3.5 |
| **DECISION-065** | Validate stored data quality before Phase 1B-α | 9 | 3 | 15 | 🔴 | 3.0 |
| **DECISION-086** | Fractional Kelly position sizing | 9 | 3 | 20 |   | 3.0 |
| **DECISION-087** | Vol-targeted sizing per-position (closes 023) | 9 | 3 | 15 |   | 3.0 |
| **DECISION-018** | Cooldown after stop-out (BUG-133) | 6 | 2 | 15 |   | 3.0 |
| **DECISION-043** | Retune framework | 6 | 2 | 15 |   | 3.0 |
| **DECISION-074** | Polygon block trades / dark pool eval | 6 | 2 | 15 |   | 3.0 |
| **DECISION-078** | Stop-out cluster breaker | 6 | 2 | 15 |   | 3.0 |
| **DECISION-112** | Disaster recovery plan + incident runbook | 6 | 2 | 15 |   | 3.0 |
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
| **DECISION-215** | A/B test result registry (structured artifacts versioned in  | 6 | 2 | 10 |   | 3.0 |
| **DECISION-219** | GitHub Actions audit — security, schedule, failure alerting, | 6 | 2 | 10 |   | 3.0 |
| **DECISION-226** | Cache schema versioning (every parquet has schema_version me | 6 | 2 | 10 |   | 3.0 |
| **DECISION-230** | Logging audit + standard (structured JSON, rotation, level s | 6 | 2 | 10 |   | 3.0 |
| **DECISION-020** | News API selection (depends on 002 eval results) | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-023** | Vol-targeted position sizing (BUG-168) | 8 | 3 | 20 |   | 2.7 |
| **DECISION-066** | Granularity standard for all backtest outputs | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-070** | Portfolio-level exit logic | 8 | 3 | 15 |   | 2.7 |
| **DECISION-101** | Earnings strategies post-Phase 0.A | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-109** | Rolling 5yr/1yr walk-forward | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-114** | Live-vs-backtest divergence monitoring | 8 | 3 | 15 |   | 2.7 |
| **DECISION-118** | Prefetch full cross-asset macro (VIX direct, DXY, GLD, oil,  | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-124** | Cross-source smart money clusters (insider+congressional+13F | 8 | 3 | 15 |   | 2.7 |
| **DECISION-146** | Corporate actions handler (split/dividend/spinoff/rename) | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-201** | Dashboard 3 detailed spec (Stage 2 agent overlay analysis) | 8 | 3 | 15 |   | 2.7 |
| **DECISION-202** | Dashboard 4 detailed spec (Stage 3 paper trading analytics) | 8 | 3 | 15 |   | 2.7 |
| **DECISION-246** | Quant finance correctness audit (Sharpe annualization, DD co | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-021** | Tier system simplification | 5 | 2 | 20 |   | 2.5 |
| **DECISION-117** | Add file-level checksum + last-validated timestamp to cache | 5 | 2 | 10 |   | 2.5 |
| **DECISION-125** | Add Form 144 prefetch (proposed sales — leading indicator) | 5 | 2 | 10 |   | 2.5 |
| **DECISION-138** | Cold-start CI test (fresh container in <30 min) | 5 | 2 | 10 |   | 2.5 |
| **DECISION-161** | Decision dependency graph (DAG) | 5 | 2 | 15 |   | 2.5 |
| **DECISION-231** | Audit all except Exception patterns; ensure WARNING+ logging | 5 | 2 | 10 |   | 2.5 |
| **DECISION-240** | Alert tuning — configurable thresholds per event + rate trac | 5 | 2 | 10 |   | 2.5 |
| **DECISION-095** | Monitoring + alerting | 7 | 3 | 15 |   | 2.3 |
| **DECISION-107** | Regime probability (not hard label) | 7 | 3 | 15 |   | 2.3 |
| **DECISION-111** | Stationarity / structural break tests | 7 | 3 | 15 |   | 2.3 |
| **DECISION-134** | USD/CAD currency exposure tracking + optional FX hedge | 7 | 3 | 20 |   | 2.3 |
| **DECISION-147** | Delisting registry + survivorship bias correction | 7 | 3 | 10 |   | 2.3 |
| **DECISION-199** | Dashboard 1 detailed spec (Phase 1B-α backtest analysis) | 7 | 3 | 15 |   | 2.3 |
| **DECISION-203** | Dashboard 5 detailed spec (Stage 4 live trading analytics) | 7 | 3 | 15 |   | 2.3 |
| **DECISION-212** | Agent-disagreement decomposition (Bull vs Bear, Risk overrid | 7 | 3 | 15 |   | 2.3 |
| **DECISION-233** | Daily data quality monitoring (per-ticker NaN/missing/anomal | 7 | 3 | 15 |   | 2.3 |
| **DECISION-247** | Stats/ML implementation review (HMM, deflated Sharpe, Kelly  | 7 | 3 | 15 |   | 2.3 |
| **DECISION-064** | Phase 0.A prefetch checklist | 10 | 5 | 30 | 🔴 | 2.0 |
| **DECISION-071** | Smart money refinement (officer roles, 10b5-1 filter, etc.) | 8 | 4 | 20 |   | 2.0 |
| **DECISION-092** | Slippage model = f(size%ADV, vol) | 8 | 4 | 15 |   | 2.0 |
| **DECISION-100** | 17+ categorical breakdown variables | 8 | 4 | 20 | 🔴 | 2.0 |
| **DECISION-106** | Regime inputs 2 → 8+ | 8 | 4 | 20 |   | 2.0 |
| **DECISION-184** | Parallel backtest execution for Stage 1 baseline | 8 | 4 | 15 |   | 2.0 |
| **DECISION-211** | Per-agent ablation studies (drop each agent one at a time) | 8 | 4 | 20 |   | 2.0 |
| **DECISION-015** | Strategy correlation analysis methodology | 6 | 3 | 20 |   | 2.0 |
| **DECISION-024** | Correlation-adjusted concentration limits (BUG-169) | 6 | 3 | 20 |   | 2.0 |
| **DECISION-104** | Auto-populate Tier 3 momentum watchlist | 6 | 3 | 10 |   | 2.0 |
| **DECISION-128** | Dispersion-conditional circuit breaker | 6 | 3 | 15 |   | 2.0 |
| **DECISION-149** | Regime transition probability matrix | 6 | 3 | 15 |   | 2.0 |
| **DECISION-151** | Sector-level regime classification | 6 | 3 | 15 |   | 2.0 |
| **DECISION-178** | Signal lookup performance benchmark + caching strategy | 6 | 3 | 15 |   | 2.0 |
| **DECISION-217** | Audit and remove dead code (engine.py vs engine/backtest.py  | 6 | 3 | 15 |   | 2.0 |
| **DECISION-229** | Config management upgrade (pydantic + env overrides + change | 6 | 3 | 15 |   | 2.0 |
| **DECISION-171** | Docstring standard + sphinx documentation | 4 | 2 | 10 |   | 2.0 |
| **DECISION-239** | Multi-account architecture (TFSA/RRSP/Margin future-proofing | 4 | 2 | 15 |   | 2.0 |
| **DECISION-025** | Regime-conditional strategy weighting (BUG-175) | 7 | 4 | 20 |   | 1.8 |
| **DECISION-067** | Add 9 missing exit methods | 7 | 4 | 15 |   | 1.8 |
| **DECISION-108** | Regime persistence model (HMM or smoothing) | 7 | 4 | 15 |   | 1.8 |
| **DECISION-150** | Multi-asset regime detection (equity+credit+commodity+curren | 7 | 4 | 20 |   | 1.8 |
| **DECISION-176** | Meta-strategies (boolean AND/OR combinations of base strateg | 7 | 4 | 20 |   | 1.8 |
| **DECISION-216** | A/B test orchestrator code module (parallel arms with determ | 7 | 4 | 20 | 🔴 | 1.8 |
| **DECISION-228** | Fetcher reliability audit (retry/rate-limit/idempotency per  | 7 | 4 | 20 |   | 1.8 |
| **DECISION-026** | Walk-forward parameter re-optimization (BUG-172) | 5 | 3 | 15 |   | 1.7 |
| **DECISION-142** | Optional market-neutral construction (long stock + short SPY | 5 | 3 | 20 |   | 1.7 |
| **DECISION-148** | Stock-specific adaptive momentum lookback (vol-adjusted) | 5 | 3 | 15 |   | 1.7 |
| **DECISION-157** | Synthetic broker outage testing during Stage 3 (chaos engine | 5 | 3 | 15 |   | 1.7 |
| **DECISION-159** | Regulatory event handler (SEC/DOJ investigations, sanctions) | 5 | 3 | 20 |   | 1.7 |
| **DECISION-200** | Dashboard 2 detailed spec (Phase 0.D ICT/SMC signal audit) | 5 | 3 | 15 |   | 1.7 |
| **DECISION-204** | Dashboard 6 detailed spec (cross-phase comparison waterfall) | 5 | 3 | 15 |   | 1.7 |
| **DECISION-093** | Migrate live to AWS/GCP/DO before Stage 4 | 8 | 5 | 20 |   | 1.6 |
| **DECISION-141** | Sector-neutral hedge overlay (long position + short sector E | 6 | 4 | 20 |   | 1.5 |
| **DECISION-143** | IPO/lockup/secondary offering systematic framework | 6 | 4 | 20 |   | 1.5 |
| **DECISION-234** | Ticker lifecycle event handler (CUSIP/ISIN tracking across r | 6 | 4 | 20 |   | 1.5 |
| **DECISION-251** | Dependency injection audit (refactor for testability with mo | 6 | 4 | 20 |   | 1.5 |
| **DECISION-098** | Test coverage 70% before Stage 3 | 7 | 5 | 15 | 🔴 | 1.4 |
| **DECISION-222** | Test naming and structure audit; regression tests for top-20 | 7 | 5 | 15 |   | 1.4 |
| **DECISION-102** | Market-Level / Correlation-Factor strategies | 8 | 6 | 30 |   | 1.3 |
| **DECISION-145** | IV delta vs historical pre-earnings pattern as signal | 5 | 4 | 20 |   | 1.2 |
| **DECISION-185** | Incremental backtest updates for daily data refresh | 5 | 4 | 15 |   | 1.2 |
| **DECISION-099** | 11 missing strategy categories (Pairs, Calendar, Cross-Asset | 7 | 8 | 20 |   | 0.9 |
| **DECISION-027** | Online learning / feedback loop (BUG-173) | 3 | 5 | 15 |   | 0.6 |

---

## Phase 0.A Blockers (Critical Path)

| Decision | Title | Impact | Eng | Why blocking |
|---|---|---|---|---|
| **DECISION-205** | A/B test arm design — minimum 4 arms (rules, full- | 10 | 1 | A/B test arm design - minimum 4 arms (gates Stage 2) |
| **DECISION-064** | Phase 0.A prefetch checklist | 10 | 5 | Phase 0.A prefetch checklist (BLOCKING) |
| **DECISION-152** | Hold-out final test period (never touched during a | 9 | 0 | Hold-out test period (no eng cost) |
| **DECISION-207** | Pre-commit minimum sample size per arm (300 paired | 9 | 0 | Pre-commit minimum sample size (300) |
| **DECISION-080** | t-stat + Bonferroni | 9 | 1 | t-stat + Bonferroni |
| **DECISION-131** | Agent value-add minimum (Sharpe improvement >=0.2  | 9 | 1 | Agent value-add minimum |
| **DECISION-206** | Paired A/B design — every trade evaluated by every | 9 | 1 | Paired A/B design |
| **DECISION-062** | Output schema translation: TradingAgents 5-tier →  | 9 | 2 | TradingAgents output schema |
| **DECISION-063** | Universe refresh automation | 9 | 2 | Universe refresh automation |
| **DECISION-081** | Sharpe + Sortino + transaction cost sensitivity | 9 | 2 | Sharpe + Sortino + cost sensitivity |
| **DECISION-208** | Multi-metric A/B comparison (Sharpe + Sortino + DD | 9 | 2 | Multi-metric A/B comparison |
| **DECISION-065** | Validate stored data quality before Phase 1B-α | 9 | 3 | Validate stored data quality |
| **DECISION-014** | Phase 1B passing criteria adjustments | 8 | 1 | Phase 1B passing criteria |
| **DECISION-073** | Adopt Quiver pre-built composites | 8 | 1 | Adopt Quiver pre-built composites |
| **DECISION-163** | Implementation cost estimate per pending decision | 8 | 1 | Implementation cost estimates |
| **DECISION-177** | Explicit random seed in every backtest run output  | 8 | 1 | Random seeds + reproducibility |
| **DECISION-210** | Net Sharpe contribution accounting (gross lift min | 8 | 1 | Net Sharpe contribution accounting |
| **DECISION-232** | Determinism test (run identical backtest twice, di | 8 | 1 | Determinism test |
| **DECISION-037** | Characterization-test-first approach (Phase A) | 8 | 2 | Characterization tests-first |
| **DECISION-096** | Backtest reproducibility (code + data + config has | 8 | 2 | Backtest reproducibility hashing |
| **DECISION-110** | Deflated Sharpe (Bailey et al.) | 8 | 2 | Deflated Sharpe |
| **DECISION-209** | Per-regime A/B verdicts — agents pass/fail separat | 8 | 2 | Per-regime A/B verdicts |
| **DECISION-213** | Both-rationales storage (rules-only AND agent rati | 8 | 2 | Both-rationales storage |
| **DECISION-020** | News API selection (depends on 002 eval results) | 8 | 3 | News API choice |
| **DECISION-066** | Granularity standard for all backtest outputs | 8 | 3 | Granularity standard |
| **DECISION-101** | Earnings strategies post-Phase 0.A | 8 | 3 | Earnings strategies post-Phase-0.A |
| **DECISION-109** | Rolling 5yr/1yr walk-forward | 8 | 3 | Rolling 5yr/1yr walk-forward |
| **DECISION-118** | Prefetch full cross-asset macro (VIX direct, DXY,  | 8 | 3 | Cross-asset macro prefetch |
| **DECISION-146** | Corporate actions handler (split/dividend/spinoff/ | 8 | 3 | Corporate actions handler |
| **DECISION-246** | Quant finance correctness audit (Sharpe annualizat | 8 | 3 | Quant finance correctness audit |
| **DECISION-100** | 17+ categorical breakdown variables | 8 | 4 | 17+ categorical breakdowns |
| **DECISION-038** | Layered execution with iteration budgets | 7 | 1 | Layered execution budgets |
| **DECISION-079** | Reconcile Level 2 earnings gap with earnings_toler | 7 | 1 | Reconcile L2 earnings gap |
| **DECISION-083** | Min trades floor 300 independent positions | 7 | 1 | Min trades floor 300 |
| **DECISION-153** | Regime-stratified train/test splits | 7 | 1 | Regime-stratified train/test |
| **DECISION-155** | vs-SPY comparison in all backtest reports | 7 | 1 | vs-SPY comparison in reports |
| **DECISION-158** | Extend backtest period to 2008-2024 (16 years for  | 7 | 1 | Extend backtest to 2008-2024 |
| **DECISION-235** | Time/calendar handling spec (NYSE calendar, holida | 7 | 1 | Time/calendar handling spec |
| **DECISION-016** | Threshold calibration scope (BUG-130) | 7 | 2 | Threshold calibration scope |
| **DECISION-068** | Bootstrap CI + pairwise significance for exit comp | 7 | 2 | Bootstrap CI for exits |
| **DECISION-216** | A/B test orchestrator code module (parallel arms w | 7 | 4 | A/B test orchestrator code module |
| **DECISION-098** | Test coverage 70% before Stage 3 | 7 | 5 | Test coverage 70% |
| **DECISION-085** | Define macro correlation precisely | 6 | 1 | Define macro correlation precisely |

**Phase 0.A blocker totals:** 43 decisions, ~82 eng-days.

---

## Zero-Cost Approvals (No Engineering — Owner Just Decides)

| Decision | Title | Impact | Review Min |
|---|---|---|---|
| **DECISION-152** | Hold-out final test period (never touched during audits) | 9 | 10 |
| **DECISION-207** | Pre-commit minimum sample size per arm (300 paired trades) b | 9 | 15 |
| **DECISION-248** | Owner pre-commitment doc (rules owner commits to before loss | 6 | 30 |
| **DECISION-169** | Owner skills gap audit (statistical, SRE, tax, etc.) — Owner | 5 | 30 |
| **DECISION-029-C** | Real-money starting capital — DEFERRED until post-paper-trad | 5 | 10 |
| **DECISION-238** | Pre/after-hours policy (recommendation: NO extended hours) | 5 | 5 |
| **DECISION-035** | Tax classification approach (Canadian) — Defer until CPA con | 4 | 30 |
| **DECISION-245** | Owner experience retrospective (periodic check-in on workflo | 4 | 30 |

---

## Summary Statistics

- Total pending: **186**
- Phase 0.A blockers: **43** (~82 eng-days)
- Zero-engineering-cost: **8**
- Total engineering days if ALL approved: **~409** (~82 weeks)
- Total owner review time if ALL: **~2630 minutes** (~43.8 hours)

*Regenerated April 2026 — sweeps PAUSED per owner. Decisions surfaced for chat approval.*