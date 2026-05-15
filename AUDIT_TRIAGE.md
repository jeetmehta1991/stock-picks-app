# AUDIT_TRIAGE.md — Pending Decision Prioritization

**2026-05-15 Batch 178 status:** This static triage file is largely superseded by the live dashboard at https://jeetmehta1991.github.io/stock-picks-app/dashboard_stage_2/ which shows real-time decision/bug/INV status with engine-consumption verification. Current state: 481 visible DECs (260 IMPLEMENTED / 136 DECIDED / 83 DEFERRED / 2 UNKNOWN) + 250 visible BUGs. Phase 1A launch unblocked.

**Last regenerated:** April 2026 (post-Pass 52 Round 1 complete + DEC-346 categorical matrix + DEC-347 lagging-indicator gap + DEC-348 event-calendar suppression logged)
**Decisions covered:** 251 PENDING (matches AUDIT_INDEX.md actual count, post-Pass-52 Round 1 + DEC-346 + DEC-347 + DEC-348 logged as new pending)

**How to read:**
- **Impact (1-10):** how much each moves the needle on quality, risk, or unblocking work
- **Eng (days):** rough engineer-days to implement including tests
- **Review (min):** owner time to read context, weigh tradeoffs, decide
- **🔴 = Phase 0.A blocker**
- **Ratio:** Impact / max(Eng, 0.5). Higher = better leverage

**Caveat:** scores are best-effort. Owner judgment overrides.

---

## Counts

| Metric | Count |
|---|---|
| Total pending | 251 |
| Phase 0.A blockers | 60 |
| Zero-eng-cost (only review time needed) | 2 |
| Impact >= 9 | 17 |
| Impact >= 8 (high) | 72 |
| Sum eng-days estimated | 594 |

---

## Top 30 by Impact/Cost Ratio (Approve First)

| Rank | Decision | Title | Impact | Eng | Review | 🔴 | Ratio | Theme |
|---|---|---|---|---|---|---|---|---|
| 2 | **DECISION-207** | Pre-commit minimum sample size per arm (300 paired trad | 9 | 0 | 15 | 🔴 | 18.0 | Batch X32 — Agent A/B Testing |
| 4 | **DECISION-291** | Triage-based bulk approval — owner approves entire impa | 8 | 0 | 10 |   | 16.0 | Batch X50 — Process Improvements |
| 5 | **DECISION-270** | Pre-Stage-4 CPA consultation — formal opinion on tradin | 7 | 0 | 10 |   | 14.0 | Batch X45 — Stage 4 Live |
| 7 | **DECISION-205** | A/B test arm design — minimum 4 arms (rules, full-agent | 10 | 1 | 15 | 🔴 | 10.0 | Batch X32 — Agent A/B Testing |
| 8 | **DECISION-029-C** | Real-money starting capital — DEFERRED until post-paper | 5 | 0 | 10 |   | 10.0 | Live Trading Operational (Group E) |
| 12 | **DECISION-080** | t-stat + Bonferroni | 9 | 1 | 15 | 🔴 | 9.0 | Batch X4 — Statistical Methodology |
| 13 | **DECISION-131** | Agent value-add minimum (Sharpe improvement >=0.2 over  | 9 | 1 | 10 | 🔴 | 9.0 | Batch X14 — Validation criteria |
| 14 | **DECISION-206** | Paired A/B design — every trade evaluated by every arm  | 9 | 1 | 10 | 🔴 | 9.0 | Batch X32 — Agent A/B Testing |
| 15 | **DECISION-014** | Phase 1B passing criteria adjustments | 8 | 1 | 20 | 🔴 | 8.0 | Phase 1B Methodology |
| 16 | **DECISION-073** | Adopt Quiver pre-built composites | 8 | 1 | 10 | 🔴 | 8.0 | Batch X7 — Smart Money + Regimes |
| 17 | **DECISION-077** | Portfolio drawdown breaker | 8 | 1 | 10 |   | 8.0 | Batch X6 — Exits + Circuit Breakers |
| 18 | **DECISION-082** | Stress-test pass requirements (2008/2020/2022) | 8 | 1 | 10 |   | 8.0 | Batch X4 — Statistical Methodology |
| 19 | **DECISION-094** | Secrets manager | 8 | 1 | 10 |   | 8.0 | Batch X3 — Architecture |
| 20 | **DECISION-129** | Live-vs-backtest Sharpe equivalence criterion (within 0 | 8 | 1 | 10 |   | 8.0 | Batch X14 — Validation criteria |
| 21 | **DECISION-163** | Implementation cost estimate per pending decision | 8 | 1 | 30 | 🔴 | 8.0 | Batch X24 — Decision management |
| 22 | **DECISION-177** | Explicit random seed in every backtest run output (repr | 8 | 1 | 10 | 🔴 | 8.0 | Batch X29 — Reproducibility |
| 23 | **DECISION-210** | Net Sharpe contribution accounting (gross lift minus an | 8 | 1 | 10 | 🔴 | 8.0 | Batch X32 — Agent A/B Testing |
| 24 | **DECISION-223** | CI gate — PR cannot merge to main without all tests pas | 8 | 1 | 5 |   | 8.0 | Batch X34 — Test + Cache Infrastructure |
| 25 | **DECISION-232** | Determinism test (run identical backtest twice, diff ou | 8 | 1 | 10 | 🔴 | 8.0 | Batch X35 — Reliability + Determinism |
| 26 | **DECISION-244** | SESSION_START.md — Claude reads first in any new sessio | 8 | 1 | 10 |   | 8.0 | Batch X37 — Process / Owner Experience |
| 27 | **DECISION-260** | Cache freshness assertion — refuse to backtest beyond c | 8 | 1 | 5 | 🔴 | 8.0 | Batch X41 — Phase 0.A Data Prefetch Gaps |
| 28 | **DECISION-269** | Stage 4 entry criteria — explicit numeric gates (Sharpe | 8 | 1 | 15 |   | 8.0 | Batch X45 — Stage 4 Live |
| 29 | **DECISION-295** | Reconcile SHORT_BORROW_COST_PER_DAY units — 0.005 ambig | 8 | 1 | 10 |   | 8.0 | Batch X51 — CRITICAL Runtime Bugs |
| 30 | **DECISION-305** | PIT guard `_assert_no_lookahead` logs WARNING but doesn | 8 | 1 | 5 | 🔴 | 8.0 | Batch X52 — CRITICAL PIT Correctness |

---

## CRITICAL-IMPACT BATCH (Impact >= 9) — for Path (b) Approval

This is the recommended next-batch for fix approval. Includes runtime correctness
(PIT bias, survivorship, FRED revisions) and statistical rigor (hold-out, A/B).

| Decision | Title | Impact | Eng | 🔴 | Theme | Why critical |
|---|---|---|---|---|---|---|
| **DECISION-080** | t-stat + Bonferroni | 9 | 1 | 🔴 | Batch X4 — Statistical Methodo | High system impact |
| **DECISION-131** | Agent value-add minimum (Sharpe improvement >=0.2  | 9 | 1 | 🔴 | Batch X14 — Validation criteri | High system impact |
| **DECISION-062** | Output schema translation: TradingAgents 5-tier →  | 9 | 2 | 🔴 | TradingAgents Architecture | High system impact |
| **DECISION-063** | Universe refresh automation | 9 | 2 | 🔴 | Batch X1 — Data + Universe | High system impact |
| **DECISION-081** | Sharpe + Sortino + transaction cost sensitivity | 9 | 2 | 🔴 | Batch X4 — Statistical Methodo | High system impact |
| **DECISION-065** | Validate stored data quality before Phase 1B-α | 9 | 3 | 🔴 | Batch X1 — Data + Universe | High system impact |
| **DECISION-086** | Fractional Kelly position sizing | 9 | 3 |   | Batch X5 — Risk Management Ext | High system impact |
| **DECISION-087** | Vol-targeted sizing per-position (closes 023) | 9 | 3 |   | Batch X5 — Risk Management Ext | High system impact |
| **DECISION-301** | FRED data revisions completely unhandled — switch  | 9 | 3 | 🔴 | Batch X52 — CRITICAL PIT Corre | PIT correctness blocks valid backtest |
| **DECISION-300** | yfinance earnings_dates and analyst data return CU | 9 | 4 | 🔴 | Batch X52 — CRITICAL PIT Corre | PIT correctness blocks valid backtest |
| **DECISION-064** | Phase 0.A prefetch checklist | 10 | 5 | 🔴 | Batch X1 — Data + Universe | High system impact |
| **DECISION-298** | Cache stores adjusted-close (auto_adjust=True) whi | 10 | 5 | 🔴 | Batch X52 — CRITICAL PIT Corre | PIT correctness blocks valid backtest |
| **DECISION-256** | Earnings calendar prefetch (datetime + EPS surpris | 9 | 5 | 🔴 | Batch X41 — Phase 0.A Data Pre | Phase 0.A data foundation |
| **DECISION-299** | yfinance fetch_info returns CURRENT sector/mkt_cap | 9 | 5 | 🔴 | Batch X52 — CRITICAL PIT Corre | PIT correctness blocks valid backtest |
| **DECISION-303** | S&P 500 constituent list is current membership app | 10 | 7 | 🔴 | Batch X52 — CRITICAL PIT Corre | PIT correctness blocks valid backtest |
| **DECISION-257** | Quarterly fundamentals prefetch — explicit field/s | 9 | 7 | 🔴 | Batch X41 — Phase 0.A Data Pre | PIT correctness blocks valid backtest |

**Total Impact-9+ items: 21 | Total eng-days: 62**

---

## Phase 0.A Blockers (must resolve before Phase 0.A starts)

| Decision | Title | Impact | Eng | Ratio |
|---|---|---|---|---|
| **DECISION-080** | t-stat + Bonferroni | 9 | 1 | 9.0 |
| **DECISION-131** | Agent value-add minimum (Sharpe improvement >=0.2 over rules | 9 | 1 | 9.0 |
| **DECISION-014** | Phase 1B passing criteria adjustments | 8 | 1 | 8.0 |
| **DECISION-073** | Adopt Quiver pre-built composites | 8 | 1 | 8.0 |
| **DECISION-163** | Implementation cost estimate per pending decision | 8 | 1 | 8.0 |
| **DECISION-177** | Explicit random seed in every backtest run output (reproduci | 8 | 1 | 8.0 |
| **DECISION-210** | Net Sharpe contribution accounting (gross lift minus annuali | 8 | 1 | 8.0 |
| **DECISION-232** | Determinism test (run identical backtest twice, diff outputs | 8 | 1 | 8.0 |
| **DECISION-260** | Cache freshness assertion — refuse to backtest beyond cache  | 8 | 1 | 8.0 |
| **DECISION-305** | PIT guard `_assert_no_lookahead` logs WARNING but doesn't RA | 8 | 1 | 8.0 |
| **DECISION-038** | Layered execution with iteration budgets | 7 | 1 | 7.0 |
| **DECISION-079** | Reconcile Level 2 earnings gap with earnings_tolerant | 7 | 1 | 7.0 |
| **DECISION-083** | Min trades floor 300 independent positions | 7 | 1 | 7.0 |
| **DECISION-153** | Regime-stratified train/test splits | 7 | 1 | 7.0 |
| **DECISION-155** | vs-SPY comparison in all backtest reports | 7 | 1 | 7.0 |
| **DECISION-158** | Extend backtest period to 2008-2024 (16 years for crisis cov | 7 | 1 | 7.0 |
| **DECISION-235** | Time/calendar handling spec (NYSE calendar, holidays, DST, h | 7 | 1 | 7.0 |
| **DECISION-264** | Walk-forward window count — given current data, ensure adequ | 7 | 1 | 7.0 |
| **DECISION-085** | Define macro correlation precisely | 6 | 1 | 6.0 |
| **DECISION-062** | Output schema translation: TradingAgents 5-tier → position_s | 9 | 2 | 4.5 |
| **DECISION-063** | Universe refresh automation | 9 | 2 | 4.5 |
| **DECISION-081** | Sharpe + Sortino + transaction cost sensitivity | 9 | 2 | 4.5 |
| **DECISION-037** | Characterization-test-first approach (Phase A) | 8 | 2 | 4.0 |
| **DECISION-096** | Backtest reproducibility (code + data + config hash) | 8 | 2 | 4.0 |
| **DECISION-110** | Deflated Sharpe (Bailey et al.) | 8 | 2 | 4.0 |
| **DECISION-213** | Both-rationales storage (rules-only AND agent rationale stor | 8 | 2 | 4.0 |
| **DECISION-252** | Explicit commission model in backtest using real IBKR pricin | 8 | 2 | 4.0 |
| **DECISION-283** | Backtest output schema — explicit columns/types/nullability/ | 8 | 2 | 4.0 |
| **DECISION-302** | VXX used as VIX proxy + UUP used as DXY proxy — quantify tra | 8 | 2 | 4.0 |
| **DECISION-304** | CPI/NFP/FOMC dates hardcoded through March 2026 only — auto- | 8 | 2 | 4.0 |
| **DECISION-016** | Threshold calibration scope (BUG-130) | 7 | 2 | 3.5 |
| **DECISION-068** | Bootstrap CI + pairwise significance for exit comparison | 7 | 2 | 3.5 |
| **DECISION-065** | Validate stored data quality before Phase 1B-α | 9 | 3 | 3.0 |
| **DECISION-301** | FRED data revisions completely unhandled — switch to ALFRED  | 9 | 3 | 3.0 |
| **DECISION-020** | News API selection (depends on 002 eval results) | 8 | 3 | 2.7 |
| **DECISION-066** | Granularity standard for all backtest outputs | 8 | 3 | 2.7 |
| **DECISION-101** | Earnings strategies post-Phase 0.A | 8 | 3 | 2.7 |
| **DECISION-109** | Rolling 5yr/1yr walk-forward | 8 | 3 | 2.7 |
| **DECISION-118** | Prefetch full cross-asset macro (VIX direct, DXY, GLD, oil,  | 8 | 3 | 2.7 |
| **DECISION-146** | Corporate actions handler (split/dividend/spinoff/rename) | 8 | 3 | 2.7 |
| **DECISION-246** | Quant finance correctness audit (Sharpe annualization, DD co | 8 | 3 | 2.7 |
| **DECISION-326** | Walk-forward windows hardcoded calendar dates — no rolling l | 7 | 3 | 2.3 |
| **DECISION-300** | yfinance earnings_dates and analyst data return CURRENT valu | 9 | 4 | 2.2 |
| **DECISION-064** | Phase 0.A prefetch checklist | 10 | 5 | 2.0 |
| **DECISION-298** | Cache stores adjusted-close (auto_adjust=True) which changes | 10 | 5 | 2.0 |
| **DECISION-100** | 17+ categorical breakdown variables | 8 | 4 | 2.0 |
| **DECISION-266** | Data history extension — push backtest start from 2020 to 20 | 8 | 4 | 2.0 |
| **DECISION-256** | Earnings calendar prefetch (datetime + EPS surprise data) pe | 9 | 5 | 1.8 |
| **DECISION-299** | yfinance fetch_info returns CURRENT sector/mkt_cap/IPO date  | 9 | 5 | 1.8 |
| **DECISION-216** | A/B test orchestrator code module (parallel arms with determ | 7 | 4 | 1.8 |
| **DECISION-303** | S&P 500 constituent list is current membership applied retro | 10 | 7 | 1.4 |
| **DECISION-098** | Test coverage 70% before Stage 3 | 7 | 5 | 1.4 |
| **DECISION-259** | ICT/SMC signal pre-computation cache (FVG/BOS/CHoCH/order bl | 8 | 6 | 1.3 |
| **DECISION-257** | Quarterly fundamentals prefetch — explicit field/source/PIT  | 9 | 7 | 1.3 |

**Total Phase 0.A blockers: 60 | Total eng-days: 142**

---

## Zero-Engineering-Cost (Approve in One Reading Session)

These need only owner review time, no implementation work. Easy wins.

| Decision | Title | Impact | Review (min) | Theme |
|---|---|---|---|---|
| **DECISION-270** | Pre-Stage-4 CPA consultation — formal opinion on tradin | 7 | 10 | Batch X45 — Stage 4 Live |
| **DECISION-035** | Tax classification approach (Canadian) — Defer until CP | 4 | 30 | Live Trading Operational (Grou |

**Total zero-eng items: 2 | Total review-min: 40** (post-Pass-52 Round 1 complete: only DEC-035 + DEC-270 remain, both owner-deferred this session as Canadian-tax pair).

---

## All 251 Pending — Sorted by Ratio

| Decision | Title | Impact | Eng | Review | 🔴 | Ratio |
|---|---|---|---|---|---|---|
| **DECISION-270** | Pre-Stage-4 CPA consultation — formal opinion on tradin | 7 | 0 | 10 |   | 14.0 |
| **DECISION-080** | t-stat + Bonferroni | 9 | 1 | 15 | 🔴 | 9.0 |
| **DECISION-131** | Agent value-add minimum (Sharpe improvement >=0.2 over  | 9 | 1 | 10 | 🔴 | 9.0 |
| **DECISION-014** | Phase 1B passing criteria adjustments | 8 | 1 | 20 | 🔴 | 8.0 |
| **DECISION-073** | Adopt Quiver pre-built composites | 8 | 1 | 10 | 🔴 | 8.0 |
| **DECISION-077** | Portfolio drawdown breaker | 8 | 1 | 10 |   | 8.0 |
| **DECISION-082** | Stress-test pass requirements (2008/2020/2022) | 8 | 1 | 10 |   | 8.0 |
| **DECISION-094** | Secrets manager | 8 | 1 | 10 |   | 8.0 |
| **DECISION-129** | Live-vs-backtest Sharpe equivalence criterion (within 0 | 8 | 1 | 10 |   | 8.0 |
| **DECISION-163** | Implementation cost estimate per pending decision | 8 | 1 | 30 | 🔴 | 8.0 |
| **DECISION-177** | Explicit random seed in every backtest run output (repr | 8 | 1 | 10 | 🔴 | 8.0 |
| **DECISION-210** | Net Sharpe contribution accounting (gross lift minus an | 8 | 1 | 10 | 🔴 | 8.0 |
| **DECISION-223** | CI gate — PR cannot merge to main without all tests pas | 8 | 1 | 5 |   | 8.0 |
| **DECISION-232** | Determinism test (run identical backtest twice, diff ou | 8 | 1 | 10 | 🔴 | 8.0 |
| **DECISION-244** | SESSION_START.md — Claude reads first in any new sessio | 8 | 1 | 10 |   | 8.0 |
| **DECISION-260** | Cache freshness assertion — refuse to backtest beyond c | 8 | 1 | 5 | 🔴 | 8.0 |
| **DECISION-269** | Stage 4 entry criteria — explicit numeric gates (Sharpe | 8 | 1 | 15 |   | 8.0 |
| **DECISION-295** | Reconcile SHORT_BORROW_COST_PER_DAY units — 0.005 ambig | 8 | 1 | 10 |   | 8.0 |
| **DECISION-305** | PIT guard `_assert_no_lookahead` logs WARNING but doesn | 8 | 1 | 5 | 🔴 | 8.0 |
| **DECISION-035** | Tax classification approach (Canadian) — Defer until CP | 4 | 0 | 30 |   | 8.0 |
| **DECISION-034** | Daily loss limits for live trading | 7 | 1 | 15 |   | 7.0 |
| **DECISION-038** | Layered execution with iteration budgets | 7 | 1 | 15 | 🔴 | 7.0 |
| **DECISION-079** | Reconcile Level 2 earnings gap with earnings_tolerant | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-083** | Min trades floor 300 independent positions | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-090** | Max sector exposure cap | 7 | 1 | 10 |   | 7.0 |
| **DECISION-153** | Regime-stratified train/test splits | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-155** | vs-SPY comparison in all backtest reports | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-158** | Extend backtest period to 2008-2024 (16 years for crisi | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-173** | Adopt ruff + black + isort + mypy as CI gates | 7 | 1 | 10 |   | 7.0 |
| **DECISION-180** | Pre-market and open-of-day operational checklist | 7 | 1 | 10 |   | 7.0 |
| **DECISION-220** | Audit sync_from_claude.yml — disable if it bypasses own | 7 | 1 | 5 |   | 7.0 |
| **DECISION-221** | Test coverage measurement (pytest --cov) + CI gate | 7 | 1 | 5 |   | 7.0 |
| **DECISION-235** | Time/calendar handling spec (NYSE calendar, holidays, D | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-243** | Owner Approval Queue file (pending decisions waiting on | 7 | 1 | 10 |   | 7.0 |
| **DECISION-264** | Walk-forward window count — given current data, ensure  | 7 | 1 | 10 | 🔴 | 7.0 |
| **DECISION-289** | Owner-absent contingency — backup contact, POA, vacatio | 7 | 1 | 15 |   | 7.0 |
| **DECISION-312** | exit_hybrid_50pct has max_days=252 but 11 other exits d | 7 | 1 | 5 |   | 7.0 |
| **DECISION-316** | Regime classifier returns 'neutral' default on missing  | 7 | 1 | 5 |   | 7.0 |
| **DECISION-075** | Adverse-excursion-from-peak breaker | 6 | 1 | 10 |   | 6.0 |
| **DECISION-085** | Define macro correlation precisely | 6 | 1 | 10 | 🔴 | 6.0 |
| **DECISION-113** | Trade journal + research log + failure log | 6 | 1 | 10 |   | 6.0 |
| **DECISION-123** | Apply exponential decay to smart money signal weights | 6 | 1 | 10 |   | 6.0 |
| **DECISION-132** | Annual Sharpe variance < 0.5 stability requirement | 6 | 1 | 10 |   | 6.0 |
| **DECISION-172** | All numerical constants extracted to config | 6 | 1 | 10 |   | 6.0 |
| **DECISION-237** | Order type policy (when MOO vs limit vs stop vs stop-li | 6 | 1 | 10 |   | 6.0 |
| **DECISION-242** | Distribution analysis (skewness, kurtosis, max single-t | 6 | 1 | 10 |   | 6.0 |
| **DECISION-250** | Edge decay assumption (discount backtest Sharpe by expe | 6 | 1 | 10 |   | 6.0 |
| **DECISION-271** | Real-time data feed cost — explicit Stage 4+ line item  | 6 | 1 | 10 |   | 6.0 |
| **DECISION-275** | requirements.txt audit + completeness (openai/tradingag | 6 | 1 | 5 |   | 6.0 |
| **DECISION-309** | Cache ticker collision: BRK-B and (hypothetical) BRK.B  | 6 | 1 | 5 |   | 6.0 |
| **DECISION-315** | Circuit breakers checked one-at-a-time — if Level 1 + L | 6 | 1 | 5 |   | 6.0 |
| **DECISION-323** | Sector reclassifications retro-applied — Meta moved fro | 6 | 1 | 5 |   | 6.0 |
| **DECISION-325** | Institutional 13F PIT assumes universal on-time filing  | 6 | 1 | 5 |   | 6.0 |
| **DECISION-327** | Short-borrow cost duplicated across improvements.py + e | 6 | 1 | 5 |   | 6.0 |
| **DECISION-072** | Separate WSB from smart money | 5 | 1 | 10 |   | 5.0 |
| **DECISION-105** | Spinoff detector | 5 | 1 | 5 |   | 5.0 |
| **DECISION-121** | Exit comparison report includes side-by-side exit dates | 5 | 1 | 10 |   | 5.0 |
| **DECISION-127** | Define recovery rules from each circuit breaker level ( | 5 | 1 | 10 |   | 5.0 |
| **DECISION-136** | Portfolio rebalancing frequency policy | 5 | 1 | 10 |   | 5.0 |
| **DECISION-166** | HANDOFF.md template specification — HANDOFF template —  | 5 | 1 | 15 |   | 5.0 |
| **DECISION-214** | Quarterly re-validation of agent A/B test (model drift  | 5 | 1 | 10 |   | 5.0 |
| **DECISION-225** | Cache eviction policy (preserve prefetched, evict only  | 5 | 1 | 10 |   | 5.0 |
| **DECISION-227** | Cache size monitoring + alerting (cache_size_gb metric, | 5 | 1 | 10 |   | 5.0 |
| **DECISION-236** | Position sizing precision rules (round to broker minimu | 5 | 1 | 10 |   | 5.0 |
| **DECISION-241** | Time-in-market metric (% in any position, % long, % sho | 5 | 1 | 10 |   | 5.0 |
| **DECISION-262** | 10-candidate-cap rationale — keep, raise, or make condi | 5 | 1 | 10 |   | 5.0 |
| **DECISION-274** | sync_from_claude.yml conflict policy — fail on conflict | 5 | 1 | 5 |   | 5.0 |
| **DECISION-280** | Time-of-day slippage adjustment — first/last 30 min hig | 5 | 1 | 10 |   | 5.0 |
| **DECISION-284** | Borderline strategy handling — explicit policy at thres | 5 | 1 | 10 |   | 5.0 |
| **DECISION-290** | Dropped strategy re-evaluation cadence (every 6 months  | 5 | 1 | 10 |   | 5.0 |
| **DECISION-292** | Decision→CHECKLIST migration audit (quarterly, RESOLVED | 5 | 1 | 10 |   | 5.0 |
| **DECISION-308** | Cache get_ohlcv_bulk requires >=20 trading days — silen | 5 | 1 | 5 |   | 5.0 |
| **DECISION-310** | Cache writes zero-volume days dropped silently (df[volu | 5 | 1 | 5 |   | 5.0 |
| **DECISION-318** | AAII pub-lag treatment missing — survey data marked ava | 5 | 1 | 5 |   | 5.0 |
| **DECISION-321** | Liquidity filter market-cap check skips silently if dat | 5 | 1 | 5 |   | 5.0 |
| **DECISION-328** | Cache filelock fallback writes silently if lock unavail | 5 | 1 | 5 |   | 5.0 |
| **DECISION-331** | ETF list fragmented (ETFS in config.py 17 items, ETFS_F | 5 | 1 | 5 |   | 5.0 |
| **DECISION-334** | composite_score uses win_rate as ROI proxy — replace wi | 5 | 1 | 5 |   | 5.0 |
| **DECISION-338** | Conversion logic (short→long in bull regime) creates la | 5 | 1 | 5 |   | 5.0 |
| **DECISION-062** | Output schema translation: TradingAgents 5-tier → posit | 9 | 2 | 20 | 🔴 | 4.5 |
| **DECISION-063** | Universe refresh automation | 9 | 2 | 10 | 🔴 | 4.5 |
| **DECISION-081** | Sharpe + Sortino + transaction cost sensitivity | 9 | 2 | 15 | 🔴 | 4.5 |
| **DECISION-037** | Characterization-test-first approach (Phase A) | 8 | 2 | 15 | 🔴 | 4.0 |
| **DECISION-088** | Portfolio vol target 15% | 8 | 2 | 15 |   | 4.0 |
| **DECISION-091** | Drawdown re-sizing | 8 | 2 | 15 |   | 4.0 |
| **DECISION-096** | Backtest reproducibility (code + data + config hash) | 8 | 2 | 10 | 🔴 | 4.0 |
| **DECISION-110** | Deflated Sharpe (Bailey et al.) | 8 | 2 | 15 | 🔴 | 4.0 |
| **DECISION-139** | Remote kill switch (email-based STOP) | 8 | 2 | 10 |   | 4.0 |
| **DECISION-213** | Both-rationales storage (rules-only AND agent rationale | 8 | 2 | 10 | 🔴 | 4.0 |
| **DECISION-252** | Explicit commission model in backtest using real IBKR p | 8 | 2 | 15 | 🔴 | 4.0 |
| **DECISION-283** | Backtest output schema — explicit columns/types/nullabi | 8 | 2 | 10 | 🔴 | 4.0 |
| **DECISION-302** | VXX used as VIX proxy + UUP used as DXY proxy — quantif | 8 | 2 | 10 | 🔴 | 4.0 |
| **DECISION-304** | CPI/NFP/FOMC dates hardcoded through March 2026 only —  | 8 | 2 | 10 | 🔴 | 4.0 |
| **DECISION-311** | Trailing-stop ATR exits use ENTRY-time ATR throughout h | 8 | 2 | 10 |   | 4.0 |
| **DECISION-168** | Incident postmortem template — Incident postmortem temp | 4 | 1 | 10 |   | 4.0 |
| **DECISION-218** | Documentation audit — role of EXPLANATION/PROGRESS/UNIV | 4 | 1 | 10 |   | 4.0 |
| **DECISION-332** | Smart money composite scoring weights (4/2/-3 etc) hard | 4 | 1 | 10 |   | 4.0 |
| **DECISION-333** | Sentiment thresholds (AAII 55/45, CNN F&G 20/35/65/80)  | 4 | 1 | 5 |   | 4.0 |
| **DECISION-335** | composite_score weights (40/30/30) hardcoded — make con | 4 | 1 | 10 |   | 4.0 |
| **DECISION-336** | info_cache.json never refreshed — stale market caps per | 4 | 1 | 5 |   | 4.0 |
| **DECISION-339** | pnl_dollar hardcoded $10K notional — wrong for $5K pape | 4 | 1 | 5 |   | 4.0 |
| **DECISION-340** | get_correlation_matrix silently drops tickers with <20  | 4 | 1 | 5 |   | 4.0 |
| **DECISION-344** | Slippage threshold ATR/price > 3% likely too high — mos | 4 | 1 | 5 |   | 4.0 |
| **DECISION-016** | Threshold calibration scope (BUG-130) | 7 | 2 | 15 | 🔴 | 3.5 |
| **DECISION-019** | Liquidity filter timing (BUG-135) | 7 | 2 | 15 |   | 3.5 |
| **DECISION-022** | Drawdown-aware position sizing (BUG-170) | 7 | 2 | 15 |   | 3.5 |
| **DECISION-068** | Bootstrap CI + pairwise significance for exit compariso | 7 | 2 | 10 | 🔴 | 3.5 |
| **DECISION-069** | Per-regime exit selection | 7 | 2 | 15 |   | 3.5 |
| **DECISION-076** | Factor exposure breaker | 7 | 2 | 15 |   | 3.5 |
| **DECISION-089** | Max correlation cap between positions | 7 | 2 | 15 |   | 3.5 |
| **DECISION-097** | Reconciliation job (daily position vs broker) | 7 | 2 | 10 |   | 3.5 |
| **DECISION-103** | Auto-populate Tier 2 universe (spinoffs, IPOs, $5B+) | 7 | 2 | 10 |   | 3.5 |
| **DECISION-119** | Per-trade explainability dict (primary_signal, dominant | 7 | 2 | 15 |   | 3.5 |
| **DECISION-120** | Automatic loss attribution report — top 10 losing trade | 7 | 2 | 10 |   | 3.5 |
| **DECISION-130** | Capacity stress test (5x capital, Sharpe drop <0.3) | 7 | 2 | 10 |   | 3.5 |
| **DECISION-133** | Max gross long/short/net exposure caps | 7 | 2 | 15 |   | 3.5 |
| **DECISION-181** | End-of-day reconciliation report (positions/P&L/agents/ | 7 | 2 | 15 |   | 3.5 |
| **DECISION-182** | Weekly auto-generated performance review | 7 | 2 | 10 |   | 3.5 |
| **DECISION-183** | Memoization layer for signal computation (LRU cache) | 7 | 2 | 15 |   | 3.5 |
| **DECISION-224** | Cache concurrency audit (filelock under concurrent acce | 7 | 2 | 15 |   | 3.5 |
| **DECISION-249** | Strategy decay metric (rolling 6mo Sharpe per strategy; | 7 | 2 | 15 |   | 3.5 |
| **DECISION-277** | Per-strategy promotion workflow — each of 72 strategies | 7 | 2 | 10 |   | 3.5 |
| **DECISION-307** | Cache get_ohlcv front-extension missing — only fetches  | 7 | 2 | 10 |   | 3.5 |
| **DECISION-313** | update_trailing_stop ignores intraday HIGH — stop only  | 7 | 2 | 10 |   | 3.5 |
| **DECISION-317** | VIX hard thresholds (40/30/20) flip regime on single pr | 7 | 2 | 10 |   | 3.5 |
| **DECISION-065** | Validate stored data quality before Phase 1B-α | 9 | 3 | 15 | 🔴 | 3.0 |
| **DECISION-086** | Fractional Kelly position sizing | 9 | 3 | 20 |   | 3.0 |
| **DECISION-087** | Vol-targeted sizing per-position (closes 023) | 9 | 3 | 15 |   | 3.0 |
| **DECISION-301** | FRED data revisions completely unhandled — switch to AL | 9 | 3 | 15 | 🔴 | 3.0 |
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
| **DECISION-174** | Strategy classification by trigger type (catalyst/techn | 6 | 2 | 15 |   | 3.0 |
| **DECISION-175** | Signal persistence weighting (consecutive-day signals) | 6 | 2 | 15 |   | 3.0 |
| **DECISION-179** | Memory profiling per backtest run + memory cap enforcem | 6 | 2 | 10 |   | 3.0 |
| **DECISION-215** | A/B test result registry (structured artifacts versione | 6 | 2 | 10 |   | 3.0 |
| **DECISION-219** | GitHub Actions audit — security, schedule, failure aler | 6 | 2 | 10 |   | 3.0 |
| **DECISION-226** | Cache schema versioning (every parquet has schema_versi | 6 | 2 | 10 |   | 3.0 |
| **DECISION-230** | Logging audit + standard (structured JSON, rotation, le | 6 | 2 | 10 |   | 3.0 |
| **DECISION-263** | Burst-day stress test — re-run high-volatility days, ve | 6 | 2 | 10 |   | 3.0 |
| **DECISION-265** | Smoke test power analysis — minimum candidates for ENTE | 6 | 2 | 10 |   | 3.0 |
| **DECISION-282** | Notification cascade — Telegram primary, Email fallback | 6 | 2 | 10 |   | 3.0 |
| **DECISION-319** | AAII auto-refresh missing — committed CSV will go stale | 6 | 2 | 10 |   | 3.0 |
| **DECISION-255** | Norbert's Gambit at funding: use DLR.TO/DLR.U.TO for CA | 3 | 1 | 10 |   | 3.0 |
| **DECISION-020** | News API selection (depends on 002 eval results) | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-023** | Vol-targeted position sizing (BUG-168) | 8 | 3 | 20 |   | 2.7 |
| **DECISION-066** | Granularity standard for all backtest outputs | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-070** | Portfolio-level exit logic | 8 | 3 | 15 |   | 2.7 |
| **DECISION-101** | Earnings strategies post-Phase 0.A | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-109** | Rolling 5yr/1yr walk-forward | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-114** | Live-vs-backtest divergence monitoring | 8 | 3 | 15 |   | 2.7 |
| **DECISION-118** | Prefetch full cross-asset macro (VIX direct, DXY, GLD,  | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-124** | Cross-source smart money clusters (insider+congressiona | 8 | 3 | 15 |   | 2.7 |
| **DECISION-146** | Corporate actions handler (split/dividend/spinoff/renam | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-201** | Dashboard 3 detailed spec (Stage 2 agent overlay analys | 8 | 3 | 15 |   | 2.7 |
| **DECISION-202** | Dashboard 4 detailed spec (Stage 3 paper trading analyt | 8 | 3 | 15 |   | 2.7 |
| **DECISION-246** | Quant finance correctness audit (Sharpe annualization,  | 8 | 3 | 15 | 🔴 | 2.7 |
| **DECISION-273** | Disaster recovery plan — broker-side stops, heartbeat m | 8 | 3 | 15 |   | 2.7 |
| **DECISION-281** | Tax data architecture — design now, populate from Day 1 | 8 | 3 | 15 |   | 2.7 |
| **DECISION-021** | Tier system simplification | 5 | 2 | 20 |   | 2.5 |
| **DECISION-117** | Add file-level checksum + last-validated timestamp to c | 5 | 2 | 10 |   | 2.5 |
| **DECISION-125** | Add Form 144 prefetch (proposed sales — leading indicat | 5 | 2 | 10 |   | 2.5 |
| **DECISION-138** | Cold-start CI test (fresh container in <30 min) | 5 | 2 | 10 |   | 2.5 |
| **DECISION-161** | Decision dependency graph (DAG) | 5 | 2 | 15 |   | 2.5 |
| **DECISION-231** | Audit all except Exception patterns; ensure WARNING+ lo | 5 | 2 | 10 |   | 2.5 |
| **DECISION-240** | Alert tuning — configurable thresholds per event + rate | 5 | 2 | 10 |   | 2.5 |
| **DECISION-287** | Public site failure handling + freshness signal (last-u | 5 | 2 | 10 |   | 2.5 |
| **DECISION-320** | CNN F&G CSV interpolated between key readings — fabrica | 5 | 2 | 10 |   | 2.5 |
| **DECISION-324** | Congressional weight by disclosure_date not transaction | 5 | 2 | 10 |   | 2.5 |
| **DECISION-329** | Module-level global caches (VIX, DXY, AAII, CNN F&G) no | 5 | 2 | 10 |   | 2.5 |
| **DECISION-330** | Cache schema not versioned — schema changes silently mi | 5 | 2 | 10 |   | 2.5 |
| **DECISION-337** | update_trailing_stop ignores intraday extremes for stop | 5 | 2 | 10 |   | 2.5 |
| **DECISION-095** | Monitoring + alerting | 7 | 3 | 15 |   | 2.3 |
| **DECISION-107** | Regime probability (not hard label) | 7 | 3 | 15 |   | 2.3 |
| **DECISION-111** | Stationarity / structural break tests | 7 | 3 | 15 |   | 2.3 |
| **DECISION-134** | USD/CAD currency exposure tracking + optional FX hedge | 7 | 3 | 20 |   | 2.3 |
| **DECISION-147** | Delisting registry + survivorship bias correction | 7 | 3 | 10 |   | 2.3 |
| **DECISION-199** | Dashboard 1 detailed spec (Phase 1B-α backtest analysis | 7 | 3 | 15 |   | 2.3 |
| **DECISION-203** | Dashboard 5 detailed spec (Stage 4 live trading analyti | 7 | 3 | 15 |   | 2.3 |
| **DECISION-212** | Agent-disagreement decomposition (Bull vs Bear, Risk ov | 7 | 3 | 15 |   | 2.3 |
| **DECISION-233** | Daily data quality monitoring (per-ticker NaN/missing/a | 7 | 3 | 15 |   | 2.3 |
| **DECISION-247** | Stats/ML implementation review (HMM, deflated Sharpe, K | 7 | 3 | 15 |   | 2.3 |
| **DECISION-261** | ICT/SMC PIT rules — minimum lag from pattern completion | 7 | 3 | 15 |   | 2.3 |
| **DECISION-278** | Internal trade journal schema — chart snapshot, agent t | 7 | 3 | 15 |   | 2.3 |
| **DECISION-279** | P&L decomposition — separate (signal/timing/exit/sizing | 7 | 3 | 10 |   | 2.3 |
| **DECISION-326** | Walk-forward windows hardcoded calendar dates — no roll | 7 | 3 | 10 | 🔴 | 2.3 |
| **DECISION-300** | yfinance earnings_dates and analyst data return CURRENT | 9 | 4 | 15 | 🔴 | 2.2 |
| **DECISION-064** | Phase 0.A prefetch checklist | 10 | 5 | 30 | 🔴 | 2.0 |
| **DECISION-298** | Cache stores adjusted-close (auto_adjust=True) which ch | 10 | 5 | 15 | 🔴 | 2.0 |
| **DECISION-071** | Smart money refinement (officer roles, 10b5-1 filter, e | 8 | 4 | 20 |   | 2.0 |
| **DECISION-092** | Slippage model = f(size%ADV, vol) | 8 | 4 | 15 |   | 2.0 |
| **DECISION-100** | 17+ categorical breakdown variables | 8 | 4 | 20 | 🔴 | 2.0 |
| **DECISION-106** | Regime inputs 2 → 8+ | 8 | 4 | 20 |   | 2.0 |
| **DECISION-184** | Parallel backtest execution for Stage 1 baseline | 8 | 4 | 15 |   | 2.0 |
| **DECISION-211** | Per-agent ablation studies (drop each agent one at a ti | 8 | 4 | 20 |   | 2.0 |
| **DECISION-266** | Data history extension — push backtest start from 2020  | 8 | 4 | 10 | 🔴 | 2.0 |
| **DECISION-015** | Strategy correlation analysis methodology | 6 | 3 | 20 |   | 2.0 |
| **DECISION-024** | Correlation-adjusted concentration limits (BUG-169) | 6 | 3 | 20 |   | 2.0 |
| **DECISION-104** | Auto-populate Tier 3 momentum watchlist | 6 | 3 | 10 |   | 2.0 |
| **DECISION-128** | Dispersion-conditional circuit breaker | 6 | 3 | 15 |   | 2.0 |
| **DECISION-149** | Regime transition probability matrix | 6 | 3 | 15 |   | 2.0 |
| **DECISION-151** | Sector-level regime classification | 6 | 3 | 15 |   | 2.0 |
| **DECISION-178** | Signal lookup performance benchmark + caching strategy | 6 | 3 | 15 |   | 2.0 |
| **DECISION-217** | Audit and remove dead code (engine.py vs engine/backtes | 6 | 3 | 15 |   | 2.0 |
| **DECISION-229** | Config management upgrade (pydantic + env overrides + c | 6 | 3 | 15 |   | 2.0 |
| **DECISION-285** | Mid-hold agent re-evaluation — does live agent re-rate  | 6 | 3 | 10 |   | 2.0 |
| **DECISION-171** | Docstring standard + sphinx documentation | 4 | 2 | 10 |   | 2.0 |
| **DECISION-239** | Multi-account architecture (TFSA/RRSP/Margin future-pro | 4 | 2 | 15 |   | 2.0 |
| **DECISION-254** | ETF substitution for index strategies: SPY/QQQ/IWM trad | 4 | 2 | 15 |   | 2.0 |
| **DECISION-286** | Wealthsimple replication tracking — log owner-placed ma | 4 | 2 | 10 |   | 2.0 |
| **DECISION-256** | Earnings calendar prefetch (datetime + EPS surprise dat | 9 | 5 | 10 | 🔴 | 1.8 |
| **DECISION-299** | yfinance fetch_info returns CURRENT sector/mkt_cap/IPO  | 9 | 5 | 15 | 🔴 | 1.8 |
| **DECISION-025** | Regime-conditional strategy weighting (BUG-175) | 7 | 4 | 20 |   | 1.8 |
| **DECISION-067** | Add 9 missing exit methods | 7 | 4 | 15 |   | 1.8 |
| **DECISION-108** | Regime persistence model (HMM or smoothing) | 7 | 4 | 15 |   | 1.8 |
| **DECISION-150** | Multi-asset regime detection (equity+credit+commodity+c | 7 | 4 | 20 |   | 1.8 |
| **DECISION-176** | Meta-strategies (boolean AND/OR combinations of base st | 7 | 4 | 20 |   | 1.8 |
| **DECISION-216** | A/B test orchestrator code module (parallel arms with d | 7 | 4 | 20 | 🔴 | 1.8 |
| **DECISION-228** | Fetcher reliability audit (retry/rate-limit/idempotency | 7 | 4 | 20 |   | 1.8 |
| **DECISION-026** | Walk-forward parameter re-optimization (BUG-172) | 5 | 3 | 15 |   | 1.7 |
| **DECISION-142** | Optional market-neutral construction (long stock + shor | 5 | 3 | 20 |   | 1.7 |
| **DECISION-148** | Stock-specific adaptive momentum lookback (vol-adjusted | 5 | 3 | 15 |   | 1.7 |
| **DECISION-157** | Synthetic broker outage testing during Stage 3 (chaos e | 5 | 3 | 15 |   | 1.7 |
| **DECISION-159** | Regulatory event handler (SEC/DOJ investigations, sanct | 5 | 3 | 20 |   | 1.7 |
| **DECISION-200** | Dashboard 2 detailed spec (Phase 0.D ICT/SMC signal aud | 5 | 3 | 15 |   | 1.7 |
| **DECISION-204** | Dashboard 6 detailed spec (cross-phase comparison water | 5 | 3 | 15 |   | 1.7 |
| **DECISION-253** | Routing decision for interlisted securities: evaluate T | 5 | 3 | 20 |   | 1.7 |
| **DECISION-276** | OMS layer or use IBKR algos? Integrate IBKR TWAP/VWAP r | 5 | 3 | 15 |   | 1.7 |
| **DECISION-093** | Migrate live to AWS/GCP/DO before Stage 4 | 8 | 5 | 20 |   | 1.6 |
| **DECISION-267** | Trade event store schema — fields per trade + storage f | 8 | 5 | 15 |   | 1.6 |
| **DECISION-141** | Sector-neutral hedge overlay (long position + short sec | 6 | 4 | 20 |   | 1.5 |
| **DECISION-143** | IPO/lockup/secondary offering systematic framework | 6 | 4 | 20 |   | 1.5 |
| **DECISION-234** | Ticker lifecycle event handler (CUSIP/ISIN tracking acr | 6 | 4 | 20 |   | 1.5 |
| **DECISION-251** | Dependency injection audit (refactor for testability wi | 6 | 4 | 20 |   | 1.5 |
| **DECISION-268** | Paper-vs-backtest comparison methodology — Bayesian pos | 6 | 4 | 15 |   | 1.5 |
| **DECISION-314** | Circuit breakers levels 3 and 4 (intraday halt, market  | 6 | 4 | 15 |   | 1.5 |
| **DECISION-303** | S&P 500 constituent list is current membership applied  | 10 | 7 | 20 | 🔴 | 1.4 |
| **DECISION-098** | Test coverage 70% before Stage 3 | 7 | 5 | 15 | 🔴 | 1.4 |
| **DECISION-222** | Test naming and structure audit; regression tests for t | 7 | 5 | 15 |   | 1.4 |
| **DECISION-258** | Options chain snapshot cache (OI + IV + put-call ratio) | 7 | 5 | 10 |   | 1.4 |
| **DECISION-272** | Stage 4 hosting migration plan — target platform, deplo | 7 | 5 | 15 |   | 1.4 |
| **DECISION-322** | Market cap from yfinance.info CURRENT not historical —  | 7 | 5 | 15 |   | 1.4 |
| **DECISION-102** | Market-Level / Correlation-Factor strategies | 8 | 6 | 30 |   | 1.3 |
| **DECISION-259** | ICT/SMC signal pre-computation cache (FVG/BOS/CHoCH/ord | 8 | 6 | 10 | 🔴 | 1.3 |
| **DECISION-257** | Quarterly fundamentals prefetch — explicit field/source | 9 | 7 | 15 | 🔴 | 1.3 |
| **DECISION-145** | IV delta vs historical pre-earnings pattern as signal | 5 | 4 | 20 |   | 1.2 |
| **DECISION-185** | Incremental backtest updates for daily data refresh | 5 | 4 | 15 |   | 1.2 |
| **DECISION-343** | Pandas-ta deprecation warning on pandas 4.0 — plan repl | 6 | 5 | 15 |   | 1.2 |
| **DECISION-099** | 11 missing strategy categories (Pairs, Calendar, Cross- | 7 | 8 | 20 |   | 0.9 |
| **DECISION-027** | Online learning / feedback loop (BUG-173) | 3 | 5 | 15 |   | 0.6 |

---
*Regenerated April 2026 (post-Pass-49) — 274 pending decisions ranked by impact/cost ratio.*

---

# BUG TRIAGE — Pending Bug Prioritization (added Pass 52 per owner direction)

**Note:** Bugs are tracked separately from decisions per owner direction Pass 52: "TRIAGE should include bugs too although those would be a separate set all together. Note that Decisions will impact code. We will do decisions first, eliminate non applicable bugs and then solve for what is still remaining."

**Approach:**
- Decisions resolve first (per owner sequencing)
- Bug priority computed assuming current decision state
- Some bugs may become NON-APPLICABLE after relevant decisions resolve (e.g., a bug in code that gets refactored per a decision)
- Re-triage bugs after decision-resolution session

**OPEN bug counts (verified by INDEX row count, Pass 52):**
- CRITICAL: 20
- HIGH: 75 (post-Pass-52 Stage 5/5.5 +5: BUG-270, 271, 272, 273, 274)
- MEDIUM: 102
- LOW: 25
- Total OPEN: 256+ (some severity-uncoded entries)

## Top OPEN BUGs by severity + cheapness — for focused-batch resolution session

This is a **starter list**, not exhaustive. Generated Pass 52 Stage 5.5 from highest-impact-per-effort cluster. To be expanded systematically in future passes.

### CRITICAL severity OPEN — must triage all 20

The following 20 CRITICAL bugs are OPEN. Each warrants individual review during decision-first sequencing:
- BUG-026 — VIX proxy is VXX price (regime classifier broken)
- BUG-027 — `regime_confidence()` built but never called (dead code)
- BUG-057 — Integration tests missing 15 critical scenarios
- BUG-063 — Email approval system 6 critical design gaps
- BUG-068 — CLAUDE.md missing 5 critical recent decisions
- BUG-129 — No regime-conditional parameter tuning
- BUG-185 — Wikipedia views prefetch failed entirely (verified still OPEN Pass 52 Stage 5.5)
- BUG-191 — No prefetch validation gate (verified still OPEN; predictions confirmed Stage 5.5)
- (12 more — see AUDIT_INDEX for full list)

### HIGH severity, cheap-fix OPEN bugs (Stage 5.5 surfaced)

Highest leverage per Pass 52 Stage 5.5 finding — these are <20 lines of code total to fix and unblock the smart-money agent pipeline:

| Bug | Severity | Effort (lines) | Impact |
|---|---|---|---|
| BUG-270 | HIGH | ~10-15 | insider_signal: 100% silent failure → recovers all insider signal |
| BUG-271 | HIGH | ~5-8 | gov_contracts: 99.4% silent failure → recovers contract signal |
| BUG-272 | HIGH | ~3 | lobbying: 98.8% silent failure → cheapest fix; recovers lobbying for ~76% of tickers |
| BUG-273 | HIGH | ~3 | congressional: silent crash on populated dates |
| BUG-274 | HIGH | ~10 (+ schema verify) | institutional: SharesChange column missing |

**Total ~30-50 lines of code recovers the smart-money portion of the agent pipeline.** Should resolve as a batch.

### Pre-existing prefetch-empty bugs (no code fix; data/subscription side)

| Bug | Severity | Open since | Action |
|---|---|---|---|
| BUG-053 | HIGH | (early passes) | Finnhub news cache 100% empty — investigate or remove |
| BUG-181 | MEDIUM | Pass 17 | Finnhub silent prefetch failure — same root |
| BUG-185 | CRITICAL | Pass 18 | Wikipedia prefetch 100% empty — verify endpoint or remove |
| BUG-186 | HIGH | Pass 18 | 29 institutional files empty (AAPL, ABBV, AMZN) + Pass 52 finding: populated tickers only have 5 months data |
| BUG-187 | HIGH | Pass 18 | WSB mentions 14-month gap |
| BUG-190 | MEDIUM | Pass 18 | 4 Quiver endpoints not in prefetch (Senate, Twitter, Off-Exchange, App Downloads) |

### Test infrastructure (existing PENDING decisions; not bugs but critical)

These are decisions that, once resolved, would have caught BUG-270 through 274:
- DEC-098 PENDING — 70% test coverage gate before Stage 3
- DEC-221 PENDING — pytest --cov measurement + CI gate
- DEC-222 PENDING — Regression tests for top-20 critical bugs (Stage 5/5.5 says expand to top-25)
- DEC-265 PENDING — Smoke test power analysis (Stage 5 forward-link: scope to include input validation)

## Re-triage discipline — after decision resolution

Per owner direction "Decisions will impact code. We will do decisions first, eliminate non applicable bugs and then solve for what is still remaining":

1. Resolve decisions in focused-batch session
2. After each decision resolves, scan OPEN bugs for:
   - Bugs in code paths that get refactored → may become NON-APPLICABLE
   - Bugs whose underlying assumption changes → may become INVALID
   - Bugs that the decision explicitly fixes → close as RESOLVED with cross-ref
3. Re-prioritize remaining OPEN bugs
4. Implement fixes for remaining

This sequencing prevents fixing bugs in code that's about to be replaced.

---
*Bug triage section added Pass 52 per owner direction. Initial coverage = top severity + Stage 5.5 surfaced bugs. Future passes should expand to systematically prioritize all 256 OPEN bugs.*
---

# DEPENDENCY MAPPING (added Pass 52 per owner direction)

**Owner direction (Pass 52):** "Ensure dependencies are mapped in triage of decisions and triage of bugs."

**Scope of this section:** STARTER PASS — maps dependencies for highest-impact decisions and bugs. Full mapping of all 252 pending decisions + 269 OPEN bugs requires a dedicated future pass. This section captures the dependencies most consequential for sequencing the focused-batch resolution session.

**Notation:**
- `A → B` means "A blocks B" (A must resolve before B can resolve cleanly)
- `A ↔ B` means "joint resolution" (must resolve together; partial fix of one creates regression in the other)
- `A | B` means "either-or" (one of these is sufficient; not both required)
- `A ⊃ B` means "A subsumes B" (resolving A automatically resolves B)

## Decision dependencies — top 20 by impact

| Decision | Blocks | Blocked by | Joint with | Notes |
|---|---|---|---|---|
| **DEC-098** (test coverage gate) | DEC-221, DEC-222 | none | DEC-265 | Test infra precondition for all bug-fix verification |
| **DEC-221** (pytest --cov + CI gate) | DEC-222 | DEC-098 | — | Measurement before requirement |
| **DEC-222** (regression tests for top-20 bugs) | bug-fix verification | DEC-098, DEC-221 | DEC-265 | Would have caught BUG-005, 270-277 |
| **DEC-265** (smoke test power analysis) | Phase 1B re-run | — | DEC-222 | Stage 5 forward-link — scope to include input validation |
| **DEC-345** (ICT timeframe) | DEC-345-A/B/C/D, DEC-350 | none | DEC-045 | RESOLVED; opens implementation-detail decisions |
| **DEC-345-A** (HTF zone types) | DEC-345 implementation | DEC-345 (resolved) | DEC-345-B, DEC-345-C, DEC-345-D | Single batch resolution recommended |
| **DEC-345-D** (liquidity primitives) | strategy-level stop-sweep filter | DEC-345 (resolved) | — | smartmoneyconcepts.liquidity() |
| **DEC-348** (event-cal strategy gating) | mean-reversion strategy correctness | DEC-304 (resolved Pass 50) | DEC-349 | Calendar exists; consumption is gap |
| **DEC-349** (asymmetric event window) | DEC-348 | none | DEC-348 | Refines primitive that DEC-348 consumes |
| **DEC-350** (multi-TF strategy testing) | strategy-TF optimization | cache layer multi-interval | DEC-345 implementation | Same cache precondition as DEC-345 |
| **DEC-351** (anchored VWAP) | institutional-context strategies | none | DEC-352 | New primitive |
| **DEC-352** (13F price-level mapping) | institutional-context strategies | BUG-186 (data) + BUG-274 (consumption) | DEC-351 | Requires BUG-186 + BUG-274 fixed first |
| **DEC-353** (R/R ratio sweep) | exit method comparison v2 | none | — | Trivial code; resolves quickly |
| **DEC-354** (chart pattern strategies) | strategy universe expansion | — | BUG-111 (retest) | Joint with retest variants |
| **DEC-217** (dead code removal: engine.py) | code hygiene | — | BUG-204 | engine.py vs engine/backtest.py duplicate |
| **DEC-308** (cache 20-day rejection) | possibly invalid | — | — | Pass 52 verification: prediction may be wrong; needs owner verify |
| **DEC-073** (Quiver Smart Score) | Phase 1C smart-money primary signal | — | — | Verify before subscribing more APIs |
| **DEC-035** (Canadian tax) | — | — | — | Owner-deferred PENDING |
| **DEC-270** (Canadian tax pair) | — | — | — | Owner-deferred PENDING; pair with DEC-035 |
| **DEC-191** (validation gate) | Phase 1B re-run + API subscriptions | — | BUG-191 | CRITICAL OPEN since Pass 18 |

## Bug dependencies — Stage 5/5.5 cluster + cross-references

| Bug | Blocks | Blocked by | Joint with | Notes |
|---|---|---|---|---|
| **BUG-005** (CRITICAL — strategies field mismatch) | All agent reasoning | none | BUG-276 | MUST fix jointly with BUG-276 (sortable cache key) |
| **BUG-276** (HIGH — sorted on dicts) | Agent cache when strategies populate | BUG-005 (currently masks it) | BUG-005 | Crashes immediately when BUG-005 fixed |
| **BUG-270** (HIGH — insider column mismatch) | insider_signal correctness | none | — | ~10-15 LOC fix |
| **BUG-271** (HIGH — gov_contracts no Date) | gov_contracts signal | BUG-284 (prefetch side) | BUG-284 | Joint fix: build Date from Qtr+Year in prefetch |
| **BUG-272** (HIGH — lobbying string concat) | lobbying signal | none | — | ~3 LOC fix |
| **BUG-273** (HIGH — congressional Chamber/House) | congressional_signal correctness | none | — | ~3 LOC fix |
| **BUG-274** (HIGH — institutional SharesChange) | institutional_signal correctness | BUG-186 (data side, 5-mo coverage + 29 empty) | DEC-352 | DEC-352 (price mapping) needs BUG-274 fixed |
| **BUG-277** (HIGH — classify_regime fails) | regime classification | none | BUG-026, BUG-234 | Caller-chain trace needed for severity confirmation; if engine uses directly, severity → CRITICAL |
| **BUG-278** (MEDIUM — yield_curve no cache) | macro snapshot in restricted-network | none | — | Standalone fix |
| **BUG-279** (MEDIUM — get_ohlcv reverse-date) | input validation | none | — | Standalone fix |
| **BUG-280** (LOW — earnings None silent) | Risk Agent earnings input | — | — | Defensive sentinel return |
| **BUG-281** (MEDIUM — tier duplicate) | drift risk | — | DEC-217 | Same pattern as BUG-215 |
| **BUG-282** (LOW — category ignored) | site_generator correctness | — | — | Standalone |
| **BUG-283** (LOW — invalid tier silent) | site_generator robustness | — | — | Standalone |
| **BUG-284** (MEDIUM — prefetch DATE_FIELDS) | prefetch correctness | none | BUG-271 | Joint fix recovers gov_contracts pipeline |
| **BUG-185** (CRITICAL — wikipedia 100% empty) | — | none | — | OPEN since Pass 18; verify Quiver endpoint or remove |
| **BUG-186** (HIGH — institutional 29 empty + 5-mo gap) | DEC-352, BUG-274 effective testing | none | — | OPEN since Pass 18; data-side, requires Quiver verification |
| **BUG-053** + **BUG-181** (Finnhub empty) | news sentiment input | — | — | OPEN; verify endpoint or remove |
| **BUG-072** (validator false-pass) | Phase 1B safety | none | DEC-265 | CRITICAL prerequisite for any agent re-run |
| **BUG-191** (validation gate) | Phase 1B re-run, API subscriptions | none | BUG-072 | CRITICAL OPEN since Pass 18 |
| **BUG-111** (retest variants missing) | strategy coverage | — | DEC-354 | Joint resolution with chart patterns |
| **BUG-146** + **BUG-152** (Volume Profile) | institutional-context strategies | — | DEC-351 | Joint with anchored VWAP |
| **BUG-232** (intraday HIGH for stops) | trailing stop correctness | — | DEC-313, DEC-337 | Joint resolution |
| **BUG-233** (circuit breaker L3+4) | exit reason completeness | — | DEC-314 | Joint |
| **BUG-204** (engine.py dead code) | code hygiene | — | DEC-217 | Joint |

## Critical resolution sequence (entering focused-batch session)

Per owner sequencing rule: "decisions first → eliminate non-applicable bugs → fix remainder."

**Phase A: Test infrastructure decisions (unblocks safe bug-fix verification)**
1. DEC-098 → DEC-221 → DEC-222 → DEC-265 (joint resolution)
2. Outcome: regression-test framework in place; bug fixes can be verified

**Phase B: Validation gate (CRITICAL prerequisites for Phase 1B re-run)**
3. DEC-191 + BUG-191 + BUG-072 (joint)
4. Outcome: validate_phase1b_data.py upgraded; pass-then-burn-money pattern fixed

**Phase C: Cascade fix — smart-money pipeline**
5. BUG-005 + BUG-276 (joint, ~5 lines)
6. BUG-270, 271, 272, 273, 274 (~30 lines total)
7. BUG-284 (joint with BUG-271; ~5 lines)
8. BUG-277 caller-chain trace + fix
9. Outcome: smart-money + regime classification working; tier distribution should shift from 93.7% LOW to balanced

**Phase D: Strategy coverage decisions**
10. DEC-345-A/B/C/D batch (HTF primitives)
11. DEC-348 + DEC-349 paired (event suppression)
12. DEC-350 (multi-TF strategy testing)
13. DEC-351 + DEC-352 (anchored VWAP + 13F mapping; DEC-352 requires BUG-186/274 fixed first)
14. DEC-353 (R/R sweep)
15. DEC-354 + BUG-111 (chart patterns + retest variants)

**Phase E: Hygiene + medium-severity**
16. BUG-281, 282, 283 (site_generator)
17. BUG-278, 279, 280 (defensive)
18. DEC-217 + BUG-204 (dead code removal)
19. BUG-232 + DEC-313 + DEC-337 (intraday HIGH for stops)
20. BUG-233 + DEC-314 (circuit breakers)

## Honest scope statement

**This dependency map is a STARTER pass — it covers ~50 of the highest-impact items out of ~520 total OPEN/PENDING items.** Full mapping requires:
- Walk every PENDING decision; identify what it blocks and what blocks it
- Walk every OPEN bug; identify dependencies on data-side / decision-side / other bugs
- Cross-link in INDEX with `Depends-on:` / `Blocks:` columns
- Re-triage by Impact / (Eng × Dependency-depth) ratio

**Estimated effort for full mapping:** 1-2 dedicated audit passes. Worth doing before the focused-batch resolution session begins, OR can be done incrementally as each bundle is approached.

*Dependency mapping starter added Pass 52. Full mapping deferred to dedicated future pass; current scope sufficient for sequencing the immediate focused-batch resolution session.*

---

## Dependency mapping batch 2 — second tier (Pass 52, owner directive: continue)

**Coverage this batch:** Phase 1B methodology, risk management (Group C), strategy/regime adaptation (Group D), exits batch X6, smart money batch X7, granularity batch X8. ~50 additional items mapped.

| Decision | Blocks | Blocked by | Joint with | Notes |
|---|---|---|---|---|
| **DEC-014** (Phase 1B passing criteria) | Phase 1B → 1C transition | DEC-098/221/222 (test infra) | DEC-015, DEC-016 | Joint Group B resolution |
| **DEC-015** (Strategy correlation methodology) | Phase 1B verdicts | none | DEC-014 | Methodology question |
| **DEC-016** (Threshold calibration) | Strategy verdicts; depends on BUG-130 | BUG-130 fix | DEC-014 | Calibration depends on which strategies actually fire correctly post-cascade-fix |
| **DEC-018** (Cooldown after stop-out) | Risk management; BUG-133 fix | none | — | Standalone |
| **DEC-019** (Liquidity filter timing) | BUG-135 fix; BUG-238 | BUG-238 (HIGH OPEN) | — | Liquidity filter market-cap fail-open already a bug |
| **DEC-020** (News API selection) | Phase 1C news | DEC-002 results | BUG-053/181 (Finnhub empty) | Phase 1C precondition |
| **DEC-021** (Tier system simplification) | Tier code refactor | DEC-345 implementation | BUG-281 (tier duplicate) | Joint with site_generator vs engine cleanup |
| **DEC-022** (Drawdown-aware sizing) | Risk management | none | DEC-023, DEC-024 | Group C resolution |
| **DEC-023** (Vol-targeted sizing) | Risk management | DEC-022 | DEC-022 | Joint |
| **DEC-024** (Correlation-adjusted concentration) | Portfolio risk | DEC-015 (correlation methodology) | DEC-022, DEC-023 | Group C resolution |
| **DEC-025** (Regime-conditional strategy weighting) | Strategy execution | BUG-277 (regime classifier broken) | DEC-026 | Cannot resolve until regime classifier works |
| **DEC-026** (Walk-forward param re-optimization) | Continuous validation | DEC-014 | — | Methodology question |
| **DEC-027** (Online learning) | — | DEC-026 | — | Far-future |
| **DEC-034** (Daily loss limits live) | Stage 3 live trading | none | DEC-035 | Stage 3 prep |
| **DEC-035** + **DEC-270** (Canadian tax) | Stage 4 live trading | CPA consult | each other | Owner-deferred PENDING |
| **DEC-037** (Characterization-test-first) | Phase 0.A approach | none | DEC-038 | Methodology |
| **DEC-038** (Layered execution + iteration budgets) | Phase 0.A approach | DEC-037 | DEC-037 | Joint |
| **DEC-043** (Retune framework) | Continuous optimization | DEC-026 | — | Phase 1+ infrastructure |
| **DEC-062** (Output schema 5-tier mapping) | TradingAgents pipeline correctness | DEC-061 RESOLVED | BUG-005 cascade | Cannot validate while BUG-005 broken |
| **DEC-063** (Universe refresh automation) | Quarterly universe maintenance | none | — | Phase 0.A prefetch |
| **DEC-064** (Phase 0.A prefetch checklist) | Phase 0.A start | none | DEC-065 | Joint Phase 0.A entry |
| **DEC-065** (Validate stored data quality before Phase 1B-α) | Phase 1B run | none | BUG-072, BUG-191 | Same root as BUG-072/191 |
| **DEC-066** (Granularity standard for outputs) | All output writers | none | DEC-067, DEC-068, DEC-069 | Affects exit method comparison |
| **DEC-067** (Add 9 missing exit methods) | Exit comparison completeness | DEC-353 (R/R minimum) | DEC-068, DEC-069 | Must enforce 2:1 R/R from DEC-353 in new methods |
| **DEC-068** (Bootstrap CI + pairwise sig for exits) | Exit comparison validity | DEC-067 | — | Statistics |
| **DEC-069** (Per-regime exit selection) | Exit method assignment | BUG-277 (regime broken) | DEC-070 | Cannot assign per-regime if regime broken |
| **DEC-070** (Portfolio-level exit logic) | Portfolio risk | DEC-067, DEC-069 | — | Top-level; depends on per-trade and per-regime first |
| **DEC-071** (Smart money refinement: officer roles, 10b5-1) | Smart-money signal quality | BUG-270 (insider broken) | DEC-073 | Cannot refine until extraction works |
| **DEC-072** (Separate WSB from smart money) | Signal taxonomy | none | DEC-071 | Categorization |
| **DEC-073** (Adopt Quiver pre-built composites) | Phase 1C smart money | BUG-185/053/181 (data-side) | — | Owner verify before subscribing more APIs |
| **DEC-079** (Level 2 earnings gap) | Earnings handling | none | DEC-348 | Joint with event suppression |
| **DEC-080** (t-stat + Bonferroni) | Strategy significance | DEC-353 (downstream R/R) | BUG-018, BUG-038, BUG-275 | Joint statistical methodology |
| **DEC-081** (Sharpe + Sortino + tx cost sensitivity) | Strategy metrics | DEC-246 (quant correctness audit) | DEC-080, DEC-110, DEC-129/130/131/132 | Quant methodology batch |
| **DEC-110** (Deflated Sharpe) | Strategy metrics | DEC-080 | DEC-081 | Joint quant |
| **DEC-129** (Live-vs-backtest Sharpe equivalence) | Stage 3 → Stage 4 gate | DEC-081 | DEC-130, DEC-131, DEC-132 | Validation criteria batch |
| **DEC-130** (Capacity stress test 5x) | Stage 3 → Stage 4 gate | DEC-129 | DEC-131, DEC-132 | Validation criteria |
| **DEC-131** (Agent value-add minimum) | Phase 1C decision | DEC-129 | DEC-132 | A/B test verdict |
| **DEC-132** (Annual Sharpe variance < 0.5) | Stability validation | DEC-129 | — | Validation criteria |
| **DEC-205-209** (A/B framework) | A/B testing | DEC-098/221/222 (test infra) | each other | RESOLVED Pass 52; cited for completeness |
| **DEC-210** (Net Sharpe contribution) | Agent ROI accounting | DEC-205-209 RESOLVED | — | Phase 1C decision |
| **DEC-246** (Quant finance correctness audit) | Sharpe annualization, DD, vol periodicity | DEC-098/222 | DEC-080, DEC-081, DEC-110 | Parent decision for metrics edge cases |
| **DEC-257** (Quarterly fundamentals prefetch) | Phase 0.A | none | — | 🔴 Phase 0.A blocker |
| **DEC-259** (ICT/SMC pre-computation cache) | DEC-345 implementation | cache layer multi-interval | DEC-345-A/B/C/D | Cache extension precondition |
| **DEC-288** OBSOLETE | — | — | — | Closed Pass 52 Round 1 |
| **DEC-291** DEFERRED | — | — | — | Closed Pass 52 Round 1 |
| **DEC-298** (Cache adjusted-close vs as-of-date) | PIT correctness | none | DEC-299/300/301/302/303 | 🔴 Phase 0.A blocker; PIT batch |
| **DEC-299** (yfinance fetch_info CURRENT sector/mkt_cap) | PIT correctness | none | DEC-298 | 🔴 PIT batch |
| **DEC-300** (yfinance earnings_dates, analyst data CURRENT) | PIT correctness | none | DEC-298 | 🔴 PIT batch |
| **DEC-301** (FRED data revisions) | PIT correctness | none | DEC-298 | 🔴 PIT batch |
| **DEC-302** (Survivorship in static CSV) | PIT correctness | DEC-303 | DEC-298 | 🔴 PIT batch |
| **DEC-303** (S&P 500 historical membership) | PIT correctness | none | DEC-302 | 🔴 PIT batch |
| **DEC-304** RESOLVED Pass 50 | — | — | — | Event calendar (already done) |
| **DEC-313** (update_trailing_stop intraday HIGH) | Trailing stop correctness | none | BUG-232, DEC-337 | Joint trio |
| **DEC-314** (Circuit breakers L3+4) | Exit reason completeness | none | BUG-233 | Joint pair |
| **DEC-327** (Short-borrow cost duplicated) | Cost accounting | none | — | Code hygiene |
| **DEC-337** (intraday extremes for stops) | Trailing stop correctness | none | BUG-232, DEC-313 | Joint trio |
| **DEC-341** RESOLVED Pass 52 | — | — | — | Round 1 complete |
| **DEC-342** OBSOLETE | — | — | — | Round 1 complete |
| **DEC-346** (Multidim categorical verdict matrix) | Strategy verdict format | none | DEC-066 (granularity) | Affects all output |
| **DEC-347** (Lagging-indicator dominance) | Signal universe | DEC-345 (RESOLVED) | DEC-345-A | Joint with HTF impl |
| **DEC-350** (Multi-TF testing) | Strategy execution | cache layer multi-interval | DEC-345 | Same precondition as DEC-345 |
| **DEC-351** (Anchored VWAP) | Institutional context | none | DEC-352 | New primitive |
| **DEC-352** (13F price-level mapping) | Institutional context | BUG-186, BUG-274 | DEC-351 | Data-side bugs first |
| **DEC-354** (Chart pattern strategies) | Strategy universe expansion | none | BUG-111 | Joint with retest |

## Bug dependencies — second tier (Pass 52)

| Bug | Blocks | Blocked by | Joint with | Notes |
|---|---|---|---|---|
| **BUG-018** (Bonferroni hardcoded 60) | Statistical correctness | DEC-080 | BUG-038, BUG-275 | Statistics cluster |
| **BUG-026** (CRITICAL VIX proxy is VXX) | Regime classification | none | BUG-027, BUG-277, BUG-234 | Regime cluster |
| **BUG-027** (CRITICAL regime_confidence dead code) | Regime classification | none | BUG-026, BUG-277 | Regime cluster |
| **BUG-038** (No min Sharpe in Bonferroni) | Statistical filtering | DEC-080 | BUG-018, BUG-275 | Statistics cluster |
| **BUG-041** (min_market_cap too low) | Liquidity filter | none | BUG-238 | Liquidity cluster |
| **BUG-053** (CRITICAL Finnhub news 100% empty) | News sentiment | data side | BUG-181 | OPEN since early passes |
| **BUG-064** (Phase 1C prerequisites undocumented) | Phase 1C kickoff | DEC-064 | — | Process |
| **BUG-068** (CRITICAL CLAUDE.md missing 5 critical decisions) | Context completeness | none | — | Process |
| **BUG-072** (HIGH validate_phase1b_data false-pass) | Phase 1B safety | none | BUG-191, DEC-065 | Validation gate |
| **BUG-079** (HIGH stop fills assumed at stop price) | Exit price accuracy | none | BUG-106, BUG-78 | Slippage cluster |
| **BUG-093** (No execution layer) | Stage 3 paper trading | DEC-067, DEC-070 | BUG-094 | Stage 3 prep |
| **BUG-094** (Stage 3 cannot run as designed) | Stage 3 launch | BUG-093 | — | Stage 3 prep |
| **BUG-095** (No portfolio-level state) | Portfolio risk | none | DEC-070 | Joint with portfolio exit |
| **BUG-101** (88.1% trades are overlapping re-entries) | Backtest validity | none | BUG-102 | Trade-log cluster |
| **BUG-102** (3.5× same-day duplicate inflation) | Trade count accuracy | BUG-101 | — | Trade-log cluster |
| **BUG-103** (Smart money prefetched but not consulted at runtime) | Smart-money signal | none | BUG-270/271/272/273/274 | Cascade root |
| **BUG-106** (HIGH Perfect stop fills slippage 0) | Exit realism | none | BUG-79, BUG-78 | Slippage cluster |
| **BUG-129** (CRITICAL no regime-conditional param tuning) | Strategy adaptation | BUG-277 (regime broken) | DEC-025 | Cannot tune until regime classifier works |
| **BUG-130** (Threshold calibration) | DEC-016 | none | — | Calibration |
| **BUG-133** (Cooldown after stop-out) | DEC-018 | none | — | Risk |
| **BUG-135** (Liquidity filter timing) | DEC-019 | none | — | Liquidity |
| **BUG-146** (HIGH no Volume Profile strategies) | Strategy universe | BUG-152 | DEC-351 | Joint primitives |
| **BUG-152** (HIGH Volume Profile primitives not computed) | Strategy universe | none | BUG-146, DEC-351 | Joint primitives |
| **BUG-168** (DEC-023 vol sizing) | DEC-023 | none | DEC-023 | Risk |
| **BUG-169** (DEC-024 concentration) | DEC-024 | none | DEC-024 | Risk |
| **BUG-170** (DEC-022 drawdown sizing) | DEC-022 | none | DEC-022 | Risk |
| **BUG-172** (DEC-026 walk-forward retune) | DEC-026 | none | DEC-026 | Methodology |
| **BUG-173** (DEC-027 online learning) | DEC-027 | none | DEC-027 | Far-future |
| **BUG-175** (DEC-025 regime-conditional weighting) | DEC-025 | BUG-277 | DEC-025 | Cannot resolve until regime works |
| **BUG-185** (CRITICAL wikipedia 100% empty) | smart-money completeness | none | — | Data side |
| **BUG-186** (HIGH 29 institutional empty + 5-mo gap) | Institutional signal + DEC-352 | none | BUG-274, DEC-352 | Data side; blocks DEC-352 |
| **BUG-187** (HIGH WSB 14-month gap) | WSB signal | none | DEC-072 | Data side |
| **BUG-191** (CRITICAL no prefetch validation gate) | Phase 1B safety + API subscriptions | none | BUG-072, DEC-065 | Validation gate |
| **BUG-204** (LOW engine.py dead code) | Code hygiene | none | DEC-217 | Joint cleanup |
| **BUG-207** (Type hints 0% screener+engine) | Type checking | none | — | Code quality |
| **BUG-209** (81 except blocks; some swallow errors) | Error visibility | none | various silent-failure bugs | Audit-revealed pattern |
| **BUG-230** RESOLVED Pass 48 | — | — | — | Cited for completeness |
| **BUG-231** RESOLVED Pass 48 | — | — | — | Cited for completeness |
| **BUG-232** (HIGH update_trailing_stop ignores intraday HIGH) | Trailing stop correctness | none | DEC-313, DEC-337 | Joint trio |
| **BUG-233** (HIGH Circuit breakers L3+4 not implemented) | Exit reason completeness | none | DEC-314 | Joint pair |
| **BUG-234** (HIGH VIX hard thresholds flip on single print) | Regime stability | none | BUG-026, BUG-277 | Regime cluster |
| **BUG-235** (HIGH AAII pub-lag not respected) | PIT sentiment | none | BUG-236 | AAII cluster |
| **BUG-236** (HIGH AAII auto-refresh missing) | PIT sentiment freshness | none | BUG-235 | AAII cluster |
| **BUG-237** (HIGH CNN F&G interpolated) | PIT sentiment | none | — | Sentiment integrity |
| **BUG-238** (HIGH Liquidity filter market-cap fail-open) | Liquidity correctness | none | BUG-041 | Liquidity cluster |
| **BUG-239** (HIGH Sector reclass retro-applied) | PIT sector | none | DEC-298 PIT batch | Joint with PIT cluster |
| **BUG-241** (HIGH Institutional 13F PIT late filers) | Institutional PIT | none | BUG-186, BUG-274 | Institutional cluster |

## Honest scope statement — batch 2

**Coverage: ~50 additional decisions + ~50 additional bugs mapped this batch. Cumulative: ~100 of ~520 items mapped (~19%).**

Significant clusters now visible:
- **Regime cluster:** BUG-026/027/277/234, DEC-025, BUG-129, BUG-175 — all blocked by classify_regime fix
- **PIT cluster:** DEC-298/299/300/301/302/303 + BUG-239 + BUG-241 — joint Phase 0.A blocker batch
- **Validation gate cluster:** BUG-072/191, DEC-065 — joint resolution unblocks Phase 1B safely
- **Sentiment cluster:** BUG-235/236/237, BUG-053/181 + AAII cluster
- **Slippage cluster:** BUG-79/106/78 — exit-price-realism cluster
- **Smart money cascade:** BUG-005/270/271/272/273/274/276 + DEC-352 dependence on BUG-186/274
- **Trailing stop cluster:** BUG-232 + DEC-313 + DEC-337 — joint trio
- **Quant statistics cluster:** DEC-080/081/110/129/130/131/132 + DEC-246 + BUG-018/038/275

**Remaining for future batches:** ~420 of ~520 items still unmapped (~81%). Continuing in subsequent passes.

*Dependency mapping batch 2 added Pass 52. Cumulative ~19% coverage. Cluster patterns emerging give clear sequencing for focused-batch resolution session.*

---

## Pass 53 Update — Phase 1A Restoration Triage Impact

**Trigger:** Phase 1A restoration (DEC-486/487/488 PROPOSED Pass 53).

**New high-priority decisions for triage:**

| DEC | Status | Impact | Why approve immediately |
|---|---|---|---|
| DEC-486 (Phase 1A restoration) | PROPOSED | 10 (Stage 2 effectiveness) | Phase 1B agent overlay cannot run without Phase 1A baseline; gates entire downstream Sprint 7+ work |
| DEC-487 (Phase 1A-α cube) | PROPOSED | 10 (Stage 2 effectiveness) | Cube methodology must be built before $300 1B-α run; pre-agent baseline gate prevents wasted budget |
| DEC-488 (Phase 1A-β scale validation) | PROPOSED | 9 (insurance) | $0 API cost insurance against $300 + 37-40h re-run cost if 1B-α infrastructure failure |

**Impact on existing pending counts:**

PROPOSED count update post Pass 53 turn:
- Pre-Pass-53: 13 PROPOSED (DEC-469-481)
- Post-Pass-53: 16 PROPOSED (DEC-469-481 + DEC-486-488)
- Pass 53 batch should approve all 16 together for atomic Sprint 0 readiness

**Triage recommendation:** Owner approve DEC-486/487/488 alongside DEC-482/483/484/485 (walk-forward + universe + FMP-alternative) as single batch to unblock Sprint 6.5 + Sprint 0A Day 1 simultaneously. All 16 PROPOSED decisions block Stage 2 substantive work.

---

## Pass 53 Addendum — Post Sprint-1-Pre-Flight Decision Batch (Stream 3 chunk B)

Pass 53 progression after the prior triage entry — DEC-486/487/488 owner-approved RESOLVED-DECIDED + 6 new DECs added.

**Decision count delta this Pass 53 turn (post-pre-flight cumulative):**

| Status | Pre-Pass-53 | Post-Sprint-1-Pre-Flight Batch | Post-Pre-Flight Cumulative (current) |
|---|---|---|---|
| Total decisions | 472 | 484 (+12) | 490 (+18) |
| RESOLVED-DECIDED | 367 | 379 (+12) | 384 (+17) |
| PROPOSED | 13 | 13 (DEC-486/487/488 flipped to RESOLVED; +0 net) | 16 (+3 — DEC-491/492/493 added Sprint 2) |

**Pass 53 NEW decisions logged this Pass post-Sprint-1 batch (6 net):**

| DEC | Status | Sprint | Triage priority |
|---|---|---|---|
| DEC-491 | PROPOSED | Sprint 2 | Trade-capture fragility — Parquet format. Awaits owner approval on parquet-only vs hybrid. |
| DEC-492 | PROPOSED | Sprint 2 (HARD-COUPLED to DEC-491) | signals_at_entry filter removal — preserve string/list signals. Awaits owner approval on filter removal scope. |
| DEC-493 | PROPOSED | Sprint 2 | trade_id schema field. Awaits owner approval on format choice. |
| DEC-494 | RESOLVED-DECIDED | Sprint 0A | Tier 2 / refresh_extended_universe.py alignment with DEC-483. NDX-non-S&P moved to T1c per DEC-483; refresh script docstring/logic updates. |
| DEC-495 | RESOLVED-DECIDED | Stage 3+ implementation | Stage 3+ archived watchlist for tickers rotating out of all 5 buckets. Spec locked; implementation Stage 3+. |
| DEC-496 | RESOLVED-DECIDED | Sprint 0A (historical) + Sprint 5 (ongoing) | Tier 3 momentum methodology — Jegadeesh-Titman 12-1 month classic. |

**Pass 53 DEC body updates (no status change — clarifications):**
- DEC-303 — source clarification (S&P DJI primary; Wikipedia + browse fallback under L88 exception)
- DEC-332 — composite weights body completed (was truncated since Pass 48)
- DEC-477 — B++ format clarification (NULL pre-window handling)
- DEC-483 — DEC-368→DEC-370 attribution fix in body + S&P DJI source change for index_rebalance_events.parquet
- DEC-370 — source spec added (S&P DJI primary; fallback)

**Pass 53 cumulative PROPOSED decisions awaiting owner approval (16 total):**
- DEC-469-481 (13) — pre-Pass-53 cluster, unchanged status
- DEC-491/492/493 (3) — Sprint 2 trade-capture fragility, awaits implementation specifics

**Triage recommendation Pass 53 cumulative:** DEC-486/487/488 + DEC-482/483/484/485/490 + DEC-494/495/496 already RESOLVED-DECIDED Pass 53 — the previously-blocking Sprint 6.5 / Sprint 0A / Sprint 5 critical-path is unblocked. Remaining 16 PROPOSED are: (a) DEC-469-481 cluster — Pre-Pass-53 enterprise architecture work (Sprint 7 statistical methodology + AgentGateConfig); (b) DEC-491/492/493 — Sprint 2 trade-capture fragility (additive improvements; no critical-path block).

**Cross-references:**
- AUDIT.md Pass 53 narrative entries
- AUDIT_INDEX.md DEC-491-496 rows
- ENGINEERING_REGISTER.md Sprint 0A/2/5 additions blocks
- DOCUMENTATION_REGISTER.md Pass 53 post-pre-flight entry

