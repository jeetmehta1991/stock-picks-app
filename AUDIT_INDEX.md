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
| **DECISION-029-C** | Real-money starting capital — DEFERRED until post-paper-trading evaluation | DEFERRED | Live Trading Operational (Group E) | Pass 43 | 52 |
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
| **DECISION-063** | Universe refresh automation — Pass 52 turn 33 RESOLVED via supersession. Original stub-only Pass 39 entry; substantive scope migrated to Pass 52 sub-decisions DEC-372/373/374 (Tier 2 GH Actions automation phases) + DEC-375/376/377 (Tier 3 momentum watchlist phases) + DEC-378/379/380 (spinoff detector phases). Status flipped to reflect actual state. | RESOLVED | Batch X1 — Data + Universe | Pass 39 | DEC-372,DEC-373,DEC-374,DEC-375,DEC-376,DEC-377,DEC-378,DEC-379,DEC-380 |
| **DECISION-064** | Phase 0.A prefetch checklist — Pass 52 turn 33 RESOLVED via supersession. Original stub-only Pass 39 entry; substantive scope migrated to Theme 3 walkthrough Pass 52: DEC-256 (earnings), DEC-257 (fundamentals), DEC-258 (options chain — in scope per Phase 1C correction), DEC-259 (ICT/SMC), DEC-260 (cache freshness), DEC-261 (PIT lag). | RESOLVED | Batch X1 — Data + Universe | Pass 39 | DEC-256,DEC-257,DEC-258,DEC-259,DEC-260,DEC-261 |
| **DECISION-065** | Validate stored data quality before Phase 1B-α — Pass 52 turn 33 RESOLVED via supersession. Original stub-only Pass 39 entry; substantive scope migrated to DEC-410 audit deliverable (API_AUDIT.md committed) + DEC-260 cache freshness assertion + DEC-417 test-run audit gate retroactive validation. | RESOLVED | Batch X1 — Data + Universe | Pass 39 | DEC-410,DEC-260,DEC-417 |
| **DECISION-066** | Granularity standard for all backtest outputs | PENDING | Batch X8 — Granularity + Breakdowns | Pass 39 | - |
| **DECISION-067** | Add 9 missing exit methods — Pass 52 owner-approved revised scope. 9 new methods: chandelier (DEC-353 compliant ATR mult ≥ 2.5), psar, supertrend, volatility_regime (DEPENDS ON DEC-388), volume_climax, rsi_extreme, partial_scaleout (uses chandelier rest), kelly_target (uses existing Kelly in metrics.py), macro_event (DEPENDS ON DEC-409). Mandatory cleanup: `fixed_3r_2r` violates DEC-353 (3R/2R = 1.5:1, below 2:1 minimum) — modify to `fixed_4r_2r` OR remove from EXIT_STRATEGIES dict (separate BUG-285 logged). 3 new indicators required (supertrend/PSAR/chandelier — not in technical.py). Effort revised from prior ~3-4 days to ~6-8 days. Sub-decisions DEC-432/433/434. CAV-063 acknowledged (BLOCKED partial on DEC-388 + DEC-409 for methods 4 + 9). | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 39 | - |
| **DECISION-068** | Bootstrap CI + pairwise significance for exit comparison — Pass 52 owner-approved (Theme 7 batch 1) + EXPANDED in DEC-423 (Pass 52 Theme 8 dimensional framework). Original scope: per-strategy bootstrap CI + Bonferroni-corrected pairwise (17 exits → C(17,2)=136 pairs). EXPANSION (DEC-423): bootstrap operates at per-cell level within DEC-422 dimensional cube; pairwise comparisons within cell; Bonferroni-correct across all dimensional cells. Cells with n<30 fall back to marginal-best. Joint with DEC-080 (Bonferroni), DEC-110 (PSR), DEC-422 (dimensional framework), DEC-423 (per-cell expansion). Sub-decision DEC-423. | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 39 | - |
| **DECISION-069** | Per-regime exit selection — SUPERSEDED_BY_DEC-422 (Pass 52). Original narrow scope (per-strategy × per-regime exit selection) subsumed by DEC-422 full dimensional space optimization where regime is one of ~17 slicing dimensions. DEC-069's outputs become marginal-analysis subset of DEC-422 framework. Closure: SUPERSEDED. | SUPERSEDED | Batch X6 — Exits + Circuit Breakers | Pass 39 | DEC-422 |
| **DECISION-070** | Portfolio-level exit logic — Pass 52 turn 30 SCOPE CORRECTION per owner directive ("Phase 1C decisions in Stage 1 are not to be deferred; deferrals only for Stage 2"). Originally DEFERRED_TO_STAGE_3 (incorrect phase scope inference). REVERSED to in-scope Stage 2 + Phase 0.B blocked status. Scope: portfolio-level drawdown trigger (>30% flatten), market-wide circuit breaker integration, position count limits. **Blocker:** BUG-095 (CRITICAL OPEN — no Portfolio class; Phase 0.B Portfolio class implementation required first). Sequencing: BUG-095/Phase 0.B → DEC-024 (entry-side concentration) → DEC-070 implementation. Joint with DEC-385 Level 4 market halt (still Stage 3+ deferred). DEC-077 SUPERSEDED_BY_DEC-070 stays. CAV-064 acknowledged philosophy tension with PROJECT_PLAN section 12 buy-crisis-dips. ~3-5 days post-Phase 0.B. | BLOCKED_ON_BUG-095 | Batch X6 — Exits + Circuit Breakers | Pass 52 | DEC-077 |
| **DECISION-071** | Smart money refinement (officer roles, 10b5-1 filter, etc.) | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-072** | Separate WSB from smart money | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-073** | Adopt Quiver pre-built composites | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-074** | Polygon block trades / dark pool eval | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-075** | Adverse-excursion-from-peak (AEP) breaker — Pass 52 owner-approved derived-metric approach. AEP is computable from existing MFE (max_favourable_excursion already tracked in OpenTrade dataclass): `aep_pct = (mfe - exit_pnl) / mfe` for winning trades only; None for losing trades. Per-strategy `mean_aep_pct` aggregate; flag POOR_EXIT_TIMING if mean > 0.5. Per-cell aggregation in DEC-422 schema (already includes max_favourable_excursion_avg). Use AEP as input to DEC-068/423 exit comparison: prefer exits with lower mean AEP controlling for total return. Effort revised from ~1 day to ~0.5 days (no new tracking needed). Sub-decision DEC-435. | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 39 | - |
| **DECISION-076** | Factor exposure breaker — Pass 52 turn 30 SCOPE CORRECTION per owner directive ("Phase 1C decisions in Stage 1 are not to be deferred; deferrals only for Stage 2"). Originally DEFERRED_TO_STAGE_3 (incorrect phase scope inference). REVERSED to in-scope Stage 2 + Phase 0.B blocked status. Portfolio-level factor-exposure breaker (more granular than DEC-070 drawdown trigger): when aggregate exposure to a single factor (sector, beta, momentum, etc.) exceeds threshold across all open positions, halt new entries in that factor. **Blocker:** BUG-095 (CRITICAL OPEN). Sequencing: BUG-095/Phase 0.B → DEC-024 → DEC-070 → DEC-076 (most granular). Philosophy tension with section 12 buy-crisis-dips — owner direction at implementation. ~2-3 days post-Phase 0.B + DEC-070. | BLOCKED_ON_BUG-095 | Batch X6 — Exits + Circuit Breakers | Pass 39 | - |
| **DECISION-077** | Portfolio drawdown breaker — Pass 52 owner-approved SUPERSEDED_BY_DEC-070. Substantive scope (>30% portfolio drawdown trigger, flatten all positions) is already covered verbatim in DEC-070's approved scope (DEFERRED_TO_STAGE_3). DEC-077 redundant; closure: SUPERSEDED. | SUPERSEDED | Batch X6 — Exits + Circuit Breakers | Pass 39 | DEC-070 |
| **DECISION-078** | Stop-out cluster breaker — Pass 52 owner-approved BIFURCATED into DEC-078A (Stage 2 diagnostic, IN SCOPE) + DEC-078B (Stage 3+ live circuit breaker, DEFERRED). Original scope had mixed Stage 2/Stage 3+ implications; bifurcation per CHECKLIST #56. Status: SPLIT — see DEC-078A and DEC-078B. | SPLIT | Batch X6 — Exits + Circuit Breakers | Pass 39 | DEC-078A,DEC-078B |
| **DECISION-078A** | Stop-out cluster diagnostic (Stage 2 in-scope half of DEC-078 split) — per-strategy informational metric. Compute rolling-window stop-out density: if strategy_X has ≥5 stop_loss exit_reasons within 10-trading-day window, flag `STOP_CLUSTER_PATTERN` in per-strategy verdict + DEC-422 cube cell metadata. NO action taken (informational only). Joint with ClosedTrade `exit_reason` field (already exists). Add to DEC-422 dimensional cube schema as derived metric. ~0.5 days. **Test signal:** synthetic case with 5+ stop-outs in 10 days fires flag; case with stops spread across 30 days does NOT fire. | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 52 | - |
| **DECISION-078B** | Stop-out cluster live circuit breaker (Stage 3+ deferred half of DEC-078 split) — when N stop-outs detected within M-day window across all open positions, halt new entries until cooldown. Requires Portfolio state (BUG-095 CRITICAL OPEN). Joint with DEC-070 (portfolio breaker, also DEFERRED). Original scope preserved for Stage 3 prep theme. Status: DEFERRED_TO_STAGE_3. | DEFERRED_TO_STAGE_3 | Batch X6 — Exits + Circuit Breakers | Pass 52 | - |
| **DECISION-079** | Reconcile Level 2 earnings gap with earnings_tolerant — Pass 52: ORIGINAL CONTEXT UNCLEAR per owner Pass 52 turn 11. Owner verbatim: "Even i am unclear about that." Needs research/excavation from Pass 39 origin context to determine substantive scope. May relate to: (a) Level 2 quote-data earnings gap handling, (b) Level 2 circuit-breaker classification per market halts, (c) something specific to earnings_tolerant strategy attribute (DEC-013 RESOLVED Stage 3+ tagged). Status: NEEDS_CLARIFICATION — flag for excavation pass. | NEEDS_CLARIFICATION | Batch X6 — Exits + Circuit Breakers | Pass 39 | - |
| **DECISION-080** | t-stat + Bonferroni — Pass 52 owner-approved. Replace hardcoded `bonferroni_adjusted_threshold(60)` with `len(STRATEGIES_TESTED)` dynamic count. Add t-statistic per strategy alongside p-value. Reporting: raw p, Bonferroni-adjusted p, t-stat. Joint with BUG-018 (HIGH OPEN — same root: hardcoded N=60), BUG-038 (no min Sharpe in Bonferroni), BUG-275. Sub-decisions DEC-400/401. CAV-049 acknowledged (Bonferroni assumes independence; our strategies highly correlated). | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
| **DECISION-081** | Sharpe + Sortino + transaction cost sensitivity — Pass 52 owner-approved. Compute both `sharpe_per_trade` (current) AND `sharpe_daily = sqrt(252) × mean(daily_returns) / std`. Add Sortino with same daily mark-to-market. Transaction cost sensitivity at 0/5/10/20bps round-trip. Joint with DEC-110 (deflated Sharpe), DEC-246 (quant audit), BUG-079/106 (slippage cluster). Sub-decisions DEC-402/403/404. CAV-050 acknowledged (daily mark-to-market storage cost). | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
| **DECISION-082** | Stress-test pass requirements — Pass 52 owner-approved Option A (revised from prior 2008/2020/2022 scope after owner caught error: backtest covers 2021-2024 only, NOT 2008 or 2020). Test only periods within current scope: (1) 2022 Rate-Rise Bear full year — Min Sharpe ≥ 0, Max DD ≤ 20%, Min Win Rate ≥ 40%. (2) Crisis sub-periods within 2021-2024 where VIX > 30 sustained — calibrate per period. Strategy fail ANY stress test → STRESS_TEST_FAILED verdict. Sub-decision DEC-405. CAV-051 acknowledged (limited crisis coverage in current 4yr scope). | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
| **DECISION-083** | Min trades floor — Pass 52 owner-approved revised TIERED (revised from prior single-300-floor after owner caught feasibility error: 300 excludes legitimate event-driven strategies). Daily-frequency / Earnings / Calendar = 300 trades min → INSUFFICIENT_OOS_DATA below. Regime-gated / Crisis-only = 100 trades min → INSUFFICIENT_FREQUENCY → eligible for Phase 1D 5-yr extension. Event-driven (spinoff/IPO/index rebalance/M&A) = 30 trades min → flagged EVENT_DRIVEN_LIMITED_SAMPLE with widened CI. Joint with DEC-014 (Phase 1B passing criteria). Sub-decision DEC-406. CAV-052 acknowledged (effective_n correlation correction). | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
| **DECISION-084** | Audit flag at 70% win rate — Audit flag threshold lowered to 65% win rate (more aggressive | RESOLVED | Batch X4 — Statistical Methodology | Pass 39 | 43 |
| **DECISION-085** | Define macro correlation precisely — Pass 52 owner-approved REVISED COMPREHENSIVE (revised from prior 5-indicator list after owner caught it was too narrow; existing macro.py already pulls 9 series). Use ALL existing FRED series (VIX, DGS10, T10Y2Y, FEDFUNDS, UNRATE, CPIAUCSL, T10YIE, BAA10Y, DXY) PLUS additions: PAYEMS (NFP), MANEMP (manufacturing), UMCSENT (consumer sentiment), RSAFS (retail sales), HOUST (housing starts), INDPRO (industrial production), BAMLH0A0HYM2 (HY spread), M2SL (money supply). Plus event windows: FOMC/CPI/NFP (existing) + earnings season + Russell/S&P rebalance + opex Fridays. ~12-15 correlation tags + 4 event-window tags. Joint with DEC-024 (correlation-adjusted concentration). Sub-decisions DEC-407/408/409. CAV-053 acknowledged (heuristic thresholds). | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
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
| **DECISION-099** | 11 missing strategy categories (Pairs, Calendar, Cross-Asset, Index Rebalance, etc.) — Pass 52 turn 33 RESOLVED via supersession. Pass 52 split into 5 sub-decisions per category with verdicts: DEC-367 (Pairs/Stat Arb — PENDING in scope per Phase 1C/Stage 2 correction), DEC-368 (Calendar/Seasonal — PENDING), DEC-369 (Cross-Asset — PENDING in scope), DEC-370 (Index Rebalance — PENDING in scope), DEC-371 (Within-category gaps catalog — PENDING). | RESOLVED | Batch X1 — Data + Universe | Pass 39 | DEC-367,DEC-368,DEC-369,DEC-370,DEC-371 |
| **DECISION-100** | 17+ categorical breakdown variables | PENDING | Batch X8 — Granularity + Breakdowns | Pass 39 | - |
| **DECISION-101** | Earnings strategies post-Phase 0.A — Pass 52 turn 33 RESOLVED via supersession. Original stub-only Pass 39 entry; substantive scope migrated to DEC-256 (Polygon earnings calendar prefetch via DEC-441) which provides the PIT-correct days_to_earnings dimension required for earnings strategies. Strategy logging itself (specific earnings strategies in 60-strategy roster) is separate scope tracked in strategy roster, not in this batch. | RESOLVED | Batch X1 — Data + Universe | Pass 39 | DEC-256,DEC-441 |
| **DECISION-102** | Market-Level / Correlation-Factor strategies | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-103** | Auto-populate Tier 2 universe (spinoffs, IPOs, $5B+) — Pass 52 turn 33 RESOLVED via supersession. Pass 52 phased implementation: DEC-372 (Phase A — GH Actions monthly automation), DEC-373 (Phase B — --validate mode for missing-data tickers), DEC-374 (Phase C — historical-membership backfill 2010-2024). | RESOLVED | Batch X1 — Data + Universe | Pass 39 | DEC-372,DEC-373,DEC-374 |
| **DECISION-104** | Auto-populate Tier 3 momentum watchlist — Pass 52 turn 33 RESOLVED via supersession. Pass 52 phased implementation: DEC-364 (Tier 3 size 50→100), DEC-375 (Phase A — code changes), DEC-376 (Phase B — GH Actions automation), DEC-377 (Phase C — historical recomputation). | RESOLVED | Batch X1 — Data + Universe | Pass 39 | DEC-364,DEC-375,DEC-376,DEC-377 |
| **DECISION-105** | Spinoff detector — Pass 52 turn 33 RESOLVED via supersession. Pass 52 phased implementation: DEC-378 (Phase 1 — NASDAQ symbol-directory weekly diff, free), DEC-379 (Phase 2 — SEC EDGAR Form 10-12B feed scraping), DEC-380 (Phase 3 — Polygon Reference corporate-actions integration via DEC-441 paid). | RESOLVED | Batch X1 — Data + Universe | Pass 39 | DEC-378,DEC-379,DEC-380 |
| **DECISION-106** | Regime inputs 2 → 8+ | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-107** | Regime probability (not hard label) | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-108** | Regime persistence model (HMM or smoothing) | PENDING | Batch X7 — Smart Money + Regimes | Pass 39 | - |
| **DECISION-109** | Rolling 5yr/1yr walk-forward — Pass 52 owner-approved Option B (extend data load to 2018-01-01 enabling canonical 5yr/1yr; joint with DEC-298 PIT cache rebuild). Train 2018-2022 → OOS 2023; Train 2019-2023 → OOS 2024 = 2 OOS rolling windows. Supersedes DEC-326's 4yr/1yr setting (DEC-326 must update train_window_years 4→5). Joint with DEC-298 (PIT cache rebuild). Sub-decisions DEC-411/412. CAV-054 acknowledged (5yr/1yr requires data extension; canonical academic standard). | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
| **DECISION-110** | Deflated Sharpe (Bailey et al.) — Pass 52 owner-approved. PSR formula in metrics.py: `PSR = Φ((SR - SR*) × sqrt((n-1) / (1 - γ3·SR + ((γ4-1)/4)·SR²)))`. SR* ≈ √(2·ln(72)) ≈ 2.92 for our 72-strategy universe. Threshold PSR ≥ 0.95 = pass; below = noise-dominated. Joint with DEC-080 (Bonferroni), DEC-081 (Sharpe canonicalization), DEC-246 (quant audit). Sub-decision DEC-413. CAV-055 acknowledged (assumes iid; momentum/MR strategies have autocorrelation; Lo 2002 adjustment Phase D). | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
| **DECISION-111** | Stationarity / structural break tests — Pass 52 owner-approved scoped to feasibility. 3 test types: (1) ADF on equity curve (~1000 daily obs, sufficient power); (2) Rolling 1-year Sharpe deviation (>2σ flag); (3) Chow split-sample (only when n_trades ≥ 600; else INSUFFICIENT_SAMPLE flag). Add `statsmodels` to requirements.txt. Output per strategy: `is_stationary`, `rolling_sharpe_stable`, `chow_break_detected` or INSUFFICIENT_SAMPLE. Sub-decisions DEC-414/415/416. CAV-056 acknowledged (4-year sample limits structural-break detection power). | PENDING | Batch X4 — Statistical Methodology | Pass 39 | - |
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
| **DECISION-129** | Live-vs-backtest Sharpe equivalence criterion (within 0.3 to pass Stage 3) — Pass 52 owner-approved THEN RETROACTIVELY DEFERRED per owner Pass 52 directive "Phase 0 and 2. Interpretation B" (Stage 3+ scope out of focus). Original approved scope preserved for Stage 3 prep theme: per-strategy gate `|live_sharpe_6mo - backtest_sharpe_oos_2024| ≤ 0.3`; min 6 months paper trading; STAGE_4_NOT_READY flag. Joint with DEC-130 (also DEFERRED), DEC-093. Sub-decision DEC-418 (also DEFERRED). CAV-058 acknowledged. Status: DEFERRED_TO_STAGE_3 — will be re-walked at Stage 3 prep theme post Phase 0.B portfolio class. | DEFERRED_TO_STAGE_3 | Batch X14 — Validation criteria | Pass 40 | - |
| **DECISION-130** | Capacity stress test (5x capital, Sharpe drop <0.3) — Pass 52 owner-approved THEN RETROACTIVELY DEFERRED per owner Pass 52 directive "Phase 0 and 2. Interpretation B" (Stage 3+ / Stage 4+ scope out of focus). Original approved scope preserved for Stage 3 prep theme: slippage scaling model, replay backtest at 1×/2×/5×, CAPACITY_LIMITED tag. Joint with BUG-079/106/78, DEC-321. Sub-decision DEC-419 (also DEFERRED). CAV-059 acknowledged. Status: DEFERRED_TO_STAGE_3. | DEFERRED_TO_STAGE_3 | Batch X14 — Validation criteria | Pass 40 | - |
| **DECISION-131** | Agent value-add minimum (Sharpe improvement ≥0.2 over rules-only) — Pass 52 owner-approved with two-gate refinement (Pass 52 turn 13). **Two-gate logic:** primary gate `agent_sharpe - rules_sharpe ≥ 0.2` (absolute); secondary gate `(agent_sharpe - rules_sharpe) / max(rules_sharpe, 0.1) ≥ 0.15` (relative); pass if EITHER gate clears + Bonferroni p<0.05 (joint with DEC-080). Catches both failure modes per CAV-060: low-baseline trap (+0.2 absolute is huge proportionally) and high-baseline trap (+0.2 absolute is noise). A/B comparison: Stage 2 candidates run twice (rules-only + agent-overlay) on same trades. Failure mode: abandon Stage 2 agent overlay per PROJECT_PLAN section 4. Cost-justification: $300 cap ÷ Sharpe improvement gates Stage 3+ adoption. Joint with DEC-205-209 (RESOLVED A/B framework), DEC-080 (Bonferroni). Sub-decision DEC-420. **Test signals:** baseline 1.5/agent 1.7 → PASS (absolute clears); baseline 0.5/agent 0.7 → PASS (both gates clear); baseline 1.5/agent 1.55 → FAIL (proportional too small, absolute too small); baseline 0.3/agent 0.5 → PASS (both gates clear). | PENDING | Batch X14 — Validation criteria | Pass 40 | - |
| **DECISION-132** | Annual Sharpe variance < 0.5 stability requirement — Pass 52 owner-approved THEN RETROACTIVELY DEFERRED per owner Pass 52 directive "Phase 0 and 2. Interpretation B" (Stage 3→4 gate, out of current focus). Original approved scope preserved for Stage 3 prep theme: calendar-year Sharpe per strategy, variance threshold < 0.5, ANNUAL_INSTABILITY flag. Joint with DEC-081, DEC-415. Sub-decision DEC-421 (also DEFERRED). CAV-061 acknowledged. Status: DEFERRED_TO_STAGE_3. | DEFERRED_TO_STAGE_3 | Batch X14 — Validation criteria | Pass 40 | - |
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
| **DECISION-152** | Hold-out final test period (never touched during audits) | RESOLVED | Batch X20 — IS/OOS extensions | Pass 40 | 52 |
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
| **DECISION-169** | Owner skills gap audit (statistical, SRE, tax, etc.) — Owner self-assesses skills gap (not | RESOLVED | Batch X26 — Skills | Pass 41 | 52 |
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
| **DECISION-205** | A/B test arm design — minimum 4 arms (rules, full-agents, no-Risk, no-Bull-Bear) | RESOLVED | Batch X32 — Agent A/B Testing | Pass 45 | 52 |
| **DECISION-206** | Paired A/B design — every trade evaluated by every arm in parallel | RESOLVED | Batch X32 — Agent A/B Testing | Pass 45 | 52 |
| **DECISION-207** | Pre-commit minimum sample size per arm (300 paired trades) before declaring winner | RESOLVED | Batch X32 — Agent A/B Testing | Pass 45 | 52 |
| **DECISION-208** | Multi-metric A/B comparison (Sharpe + Sortino + DD + win rate + PF + CVaR + cost) | RESOLVED | Batch X32 — Agent A/B Testing | Pass 45 | 52 |
| **DECISION-209** | Per-regime A/B verdicts — agents pass/fail separately per regime | RESOLVED | Batch X32 — Agent A/B Testing | Pass 45 | 52 |
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
| **DECISION-238** | Pre/after-hours policy (recommendation: NO extended hours) | RESOLVED | Batch X36 — Data Quality + Trading Mechanics | Pass 45 | 52 |
| **DECISION-239** | Multi-account architecture (TFSA/RRSP/Margin future-proofing) | PENDING | Batch X36 — Data Quality + Trading Mechanics | Pass 45 | - |
| **DECISION-240** | Alert tuning — configurable thresholds per event + rate tracking | PENDING | Batch X36 — Data Quality + Trading Mechanics | Pass 45 | - |
| **DECISION-241** | Time-in-market metric (% in any position, % long, % short, % cash) | PENDING | Batch X36 — Data Quality + Trading Mechanics | Pass 45 | - |
| **DECISION-242** | Distribution analysis (skewness, kurtosis, max single-trade contribution) | PENDING | Batch X36 — Data Quality + Trading Mechanics | Pass 45 | - |
| **DECISION-243** | Owner Approval Queue file (pending decisions waiting on owner reply, by age) | PENDING | Batch X37 — Process / Owner Experience | Pass 45 | - |
| **DECISION-244** | SESSION_START.md — Claude reads first in any new session for fast onboarding | PENDING | Batch X37 — Process / Owner Experience | Pass 45 | - |
| **DECISION-245** | Owner experience retrospective (periodic check-in on workflow productivity) | RESOLVED | Batch X37 — Process / Owner Experience | Pass 45 | 52 |
| **DECISION-246** | Quant finance correctness audit (Sharpe annualization, DD computation, vol periodicity) | PENDING | Batch X38 — Knowledge Gaps | Pass 45 | - |
| **DECISION-247** | Stats/ML implementation review (HMM, deflated Sharpe, Kelly — validate against known resul | PENDING | Batch X38 — Knowledge Gaps | Pass 45 | - |
| **DECISION-248** | Owner pre-commitment doc (rules owner commits to before losses) | RESOLVED | Batch X38 — Knowledge Gaps | Pass 45 | 52 |
| **DECISION-249** | Strategy decay metric (rolling 6mo Sharpe per strategy; flag >50% drop) | PENDING | Batch X39 — Strategy Decay + Code Quality | Pass 45 | - |
| **DECISION-250** | Edge decay assumption (discount backtest Sharpe by expected crowding %) | PENDING | Batch X39 — Strategy Decay + Code Quality | Pass 45 | - |
| **DECISION-251** | Dependency injection audit (refactor for testability with mocks) | PENDING | Batch X39 — Strategy Decay + Code Quality | Pass 45 | - |
| **DECISION-252** | Explicit commission model in backtest using real IBKR pricing tables (Tiered + Fixed, with | PENDING | Batch X40 — Cost Modeling Accuracy | Pass 46 | - |
| **DECISION-253** | Routing decision for interlisted securities: evaluate TSX-CAD vs US-NYSE per trade based o | PENDING | Batch X40 — Cost Modeling Accuracy | Pass 46 | - |
| **DECISION-254** | ETF substitution for index strategies: SPY/QQQ/IWM trades evaluate TSX-CAD equivalents (XS | PENDING | Batch X40 — Cost Modeling Accuracy | Pass 46 | - |
| **DECISION-255** | Norbert's Gambit at funding: use DLR.TO/DLR.U.TO for CAD->USD conversion when capital move | PENDING | Batch X40 — Cost Modeling Accuracy | Pass 46 | - |
| **DECISION-256** | Earnings calendar prefetch — Pass 52 owner-approved with Polygon source. Source: Polygon `/vX/reference/tickers/{ticker}/events` + `/v3/reference/financials` (post-DEC-441 subscription). Storage: `backtest/data/cache/earnings/{TICKER}.parquet` columns: `report_date`, `period_end`, `eps_estimate`, `eps_actual`, `eps_surprise_pct`, `surprise_direction`, `time_of_day` (BMO/AMC/During). Coverage: S&P 500 ~509 tickers × 5yr (per DEC-411) ≈ ~10K rows. PIT: report_date PIT-safe; estimate/actual use as-of-date semantics. **Use-case map (per #57):** earnings strategies (DEC-101), `days_to_earnings_bucket` cube dim (DEC-422), `exit_macro_event` (DEC-067), Macro/Sentiment Agents, BUG-13 fix. Finnhub free tier rejected per BUG-053/181 historical empty-cache failure (8hr rate-limit prefetch unreliable at S&P 500 scale). Joint with DEC-440 (Polygon canonical) + DEC-441 (subscription). ~2 days greenfield Polygon integration. **Test signals:** non-empty parquet ≥95% S&P 500; days_to_earnings computable for any (ticker, date); PIT loader rejects EPS_actual queries with as_of < report_date. | PENDING | Batch X41 — Phase 0.A Data Prefetch Gaps | Pass 47 | - |
| **DECISION-257** | Quarterly fundamentals prefetch — Pass 52 owner-approved with Polygon→yfinance fallback (OpenBB dropped from source priority per Polygon coverage). Source priority: Polygon `/v3/reference/financials` (canonical, post-DEC-441) → yfinance Ticker.financials (limited PIT fallback). **Required fields (15):** revenue, gross_profit, operating_income, net_income, eps_basic, eps_diluted, total_assets, total_liabilities, total_equity, cash, debt_lt, debt_st, fcf, capex, shares_outstanding. **Computed fields (9):** PE_ttm, PEG, FCF_yield, debt_equity, ROE, ROA, gross_margin, operating_margin, revenue_growth_yoy. **PIT semantics:** as-of-date filter MUST respect filing_date (not period_end); 10-K filed weeks after fiscal year end (CAV-070 candidate: yfinance lacks filing_date — use period_end + 45-day standard lag proxy). Storage: `backtest/data/cache/fundamentals/{TICKER}.parquet`. **Use-case map (per #57):** fundamental strategies (multiple in 60-strategy roster), Fundamental Agent, Smart Money Score overlay (DEC-422 cube), `cap_band` dim PIT-correct. ~3-4 days greenfield Polygon integration. OpenBB scope likely resolves "remove from project scope" pending DEC-410 audit verification. **Test signals:** all 15 required fields populated ≥90% S&P 500 × 20 quarters; PIT loader rejects fields with as_of < estimated filing_date. | PENDING | Batch X41 — Phase 0.A Data Prefetch Gaps | Pass 47 | - |
| **DECISION-258** | Options chain snapshot cache (OI + IV + put-call ratio) per ticker per day — Pass 52 turn 32 SCOPE CORRECTION per owner directive ("Phase 1C is a sub-phase of Stage 2; in current focus"). Originally DEFERRED_TO_PHASE_1C (incorrect phase scope inference). REVERSED to PENDING in-scope Stage 2. **Use-case map (#57):** no current consumer in 60-strategy roster; `exit_volatility_regime` (DEC-067) uses VIX market + ticker realized vol (not implied IV); DEC-422 cube uses market-wide `vix_level_band` not per-ticker IV. **Implementation note:** in-scope Stage 2 does NOT mean "implement immediately" — per #57 reuse-test, building options infrastructure without consumers is generic-template work. Revisit substantive implementation when options-flow strategy is added to 60-strategy roster (potential future Phase 1C strategy work) OR when `exit_volatility_regime` is upgraded to use implied IV. ~2 days scoped greenfield Polygon options endpoint integration when triggered. **Test signals (when implemented):** Polygon options endpoint returns non-empty IV/OI for ≥80% S&P 500 sample; cube dim potential populates. Joint with DEC-441 (Polygon paid covers options data on Starter tier). | PENDING | Batch X41 — Phase 0.A Data Prefetch Gaps | Pass 47 | - |
| **DECISION-259** | ICT/SMC signal pre-computation cache (FVG/BOS/CHoCH/order blocks) — Pass 52 owner-approved with Phase 0.D smartmoneyconcepts dependency. Source: smartmoneyconcepts library (per DEC-045 RESOLVED — Phase 0.D forked library). Pre-compute per (ticker, date) ICT/SMC field set on cache (computation expensive per-bar; cannot run on every backtest). Storage: `backtest/data/cache/ictsmc/{TICKER}.parquet` columns: `date`, `fvg_count`, `fvg_active_levels` (list), `bos_event` (bool), `choch_event` (bool), `order_block_levels` (list), `liquidity_grab_event` (bool). PIT: native PIT-safe (computed from past OHLCV bars per ICT methodology). Joint with DEC-261 (PIT lag rule). **Use-case map (per #57):** ICT/SMC strategies (DEC-045), pattern-completion exits (potential), Sentiment/Smart Money Agent ICT-event-density signals. **Sequencing dependency:** Phase 0.D smartmoneyconcepts fork operational status to be verified before implementation start. ~2-3 days post-Phase 0.D verification. **Test signals:** non-empty ICT cache ≥95% S&P 500; FVG events match library reference output on test sample; PIT verification (no future-bar peeking). | PENDING | Batch X41 — Phase 0.A Data Prefetch Gaps | Pass 47 | - |
| **DECISION-260** | Cache freshness assertion — Pass 52 owner-approved as patch-level uniform mechanism. Per cache file (parquet), check `max(date)` against backtest target date; if target > max → raise `CacheStaleError(ticker, cache_type, cached_end, requested_date)`. Apply uniformly to: OHLCV, earnings (DEC-256), fundamentals (DEC-257), ICT/SMC (DEC-259), news (DEC-440 Polygon), macro caches. Configuration: `STRICT_CACHE_FRESHNESS = True` default; per-test override via explicit allow-list. **Use-case map (per #57):** backtest engine (fail-fast vs silent stale data); BUG-19 fix (Codespaces blocks yfinance — silent fallback fails); BUG-19 fix (2025-2026 gap for 402 tickers); BUG-46 (market_cap snapshot for only 70 tickers). Joint with DEC-040 PIT loader. ~1 day centralized validator + integration in cache load path + fail-fast test. **Test signals:** synthetic stale cache raises CacheStaleError on backtest run; fresh cache passes silently; allow-listed stale ticker passes with warning logged. | PENDING | Batch X41 — Phase 0.A Data Prefetch Gaps | Pass 47 | - |
| **DECISION-261** | ICT/SMC PIT rules — Pass 52 owner-approved with N+1 lag rule. Pattern completion lag: ICT/SMC patterns complete on bar N (e.g., 3-bar FVG forms at N-2/N-1/N); actionable signal is bar N+1 open at earliest. Rationale: at end-of-day N, pattern is "known" but no further trading possible same day for daily bars; earliest tradable execution is bar N+1 open. For intra-bar events (BOS, CHoCH, liquidity grab): same N+1 rule — events recorded at bar N (close confirms event) but actionable from bar N+1 open. Joint with DEC-040 PIT loader + DEC-259 cache schema (lag computed at consumption time, not stored as offset in cache). **Use-case map (per #57):** ICT/SMC strategies (DEC-259 consumers), PIT loader uniform lag application, backtest correctness. ~0.5 days rule documentation + 2-line check in strategy entry logic. **Test signals:** synthetic FVG forms at bar 100 → strategy entry at bar 101 open (not bar 100); zero-lag entry triggers test failure flag. | PENDING | Batch X41 — Phase 0.A Data Prefetch Gaps | Pass 47 | - |
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
| **DECISION-288** | Legal review of public site — registration check, disclaimer, liability terms BEFORE publi | OBSOLETE | Batch X49 — Thin Areas Surfaced | Pass 47 | 52 |
| **DECISION-289** | Owner-absent contingency — backup contact, POA, vacation-mode auto-flatten | PENDING | Batch X49 — Thin Areas Surfaced | Pass 47 | - |
| **DECISION-290** | Dropped strategy re-evaluation cadence (every 6 months re-test, re-admit if Sharpe restore | PENDING | Batch X49 — Thin Areas Surfaced | Pass 47 | - |
| **DECISION-291** | Triage-based bulk approval — owner approves entire impact-ratio band in single message | DEFERRED | Batch X50 — Process Improvements | Pass 47 | 52 |
| **DECISION-292** | Decision→CHECKLIST migration audit (quarterly, RESOLVED decisions to process rules) | PENDING | Batch X50 — Process Improvements | Pass 47 | - |
| **DECISION-293** | Fix close_trade `days` NameError — confirmed runtime crash via execution. Reorder `pnl = _ | RESOLVED | Batch X51 — CRITICAL Runtime Bugs | Pass 48 | 49 |
| **DECISION-294** | Remove duplicate ClosedTrade dataclass definition in exit_manager.py — pick canonical, del | RESOLVED | Batch X51 — CRITICAL Runtime Bugs | Pass 48 | 49 |
| **DECISION-295** | Reconcile SHORT_BORROW_COST_PER_DAY units — 0.005 ambiguous (per-day decimal vs per-day pe | RESOLVED | Batch X51 — CRITICAL Runtime Bugs | Pass 48 | 50 |
| **DECISION-296** | Fix test_e2e fixture — engine fixture undefined, 7 of 8 e2e tests ERROR at setup | RESOLVED | Batch X51 — CRITICAL Runtime Bugs | Pass 48 | 49 |
| **DECISION-297** | Add unit test for close_trade — would have caught the days bug; same for any function in c | RESOLVED | Batch X51 — CRITICAL Runtime Bugs | Pass 48 | 49 |
| **DECISION-298** | Cache stores adjusted-close — RESOLVED Pass 52 owner approve all: switch auto_adjust=False, store raw OHLCV + corp actions, recompute adjusted-on-demand by as_of date. Caveats logged in LIMITATIONS_CAVEATS_ASSUMPTIONS.md. | RESOLVED | Batch X52 — CRITICAL PIT Correctness | Pass 48 | 52 |
| **DECISION-299** | yfinance fetch_info CURRENT sector — RESOLVED Pass 52 owner approve all: snapshot current results to dated CSV (Step 1, immediate), defer Polygon Reference subscription until BUG-191 validation gate built and consumer code in place (Step 2-3). Caveats logged. | RESOLVED | Batch X52 — CRITICAL PIT Correctness | Pass 48 | 52 |
| **DECISION-300** | yfinance earnings_dates / analyst data CURRENT — RESOLVED Pass 52 owner approve all: tiered approach. Step 1: enforce earnings_tolerant flag at all call sites (~80% exposure reduction). Step 2: PIT earnings calendar via Polygon News (Phase 1C scope). Step 3: REMOVE analyst data from PIT-claiming functions until paid PIT source built. Caveats logged. | RESOLVED | Batch X52 — CRITICAL PIT Correctness | Pass 48 | 52 |
| **DECISION-301** | FRED data revisions completely unhandled — switch to ALFRED (archival FRED) for vintage da | RESOLVED | Batch X52 — CRITICAL PIT Correctness | Pass 48 | 50 |
| **DECISION-302** | VXX used as VIX proxy + UUP used as DXY proxy — quantify tracking error or replace with ac | RESOLVED | Batch X52 — CRITICAL PIT Correctness | Pass 48 | 50 |
| **DECISION-303** | S&P 500 historical membership — RESOLVED Pass 52 owner approve all: build historical_membership.csv from Wikipedia free source (~2 days), modify get_sp500_constituents(as_of) to filter by added_date/removed_date, re-run all backtests (expect material change to crisis-period numbers — correct direction). Caveats logged including delisted-ticker OHLCV gap. | RESOLVED | Batch X52 — CRITICAL PIT Correctness | Pass 48 | 52 |
| **DECISION-304** | CPI/NFP/FOMC dates hardcoded through March 2026 only — auto-extend from FRED FOMC + BLS sc | RESOLVED | Batch X52 — CRITICAL PIT Correctness | Pass 48 | 50 |
| **DECISION-305** | PIT guard `_assert_no_lookahead` logs WARNING but doesn't RAISE — switch to RAISE in backt | RESOLVED | Batch X52 — CRITICAL PIT Correctness | Pass 48 | 50 |
| **DECISION-306** | get_news_sentiment path mismatch — code reads /prefetch/news/ but data lives in /cache/fin | RESOLVED | Batch X52 — CRITICAL PIT Correctness | Pass 48 | 49 |
| **DECISION-307** | Cache get_ohlcv front-extension missing — only fetches missing TAIL; if user requests start earlier than cached_start, silently returns cached range. Pass 52 owner-approved. Add symmetric front-extension: if cached_start > requested_start, fetch [requested_start, cached_start - 1day], prepend, save merged. Fail-fast on yfinance unavailability rather than silent truncation. Sub-decision DEC-381. | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-308** | Cache get_ohlcv_bulk requires >=20 trading days — silently rejects valid cache for shorter histories (newly-listed Tier 2 tickers). Pass 52 owner-approved. Replace hard 20-day floor with min(20, available_days); add LIMITED_HISTORY flag. Strategy-level decides if available is enough. Sub-decision DEC-382. | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-309** | Cache ticker collision: BRK-B and (hypothetical) BRK.B both map to BRK_B.parquet — silent  | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | 51 |
| **DECISION-310** | Cache writes zero-volume days dropped silently (df[volume>0]) — halted/suspended stocks invisible in backtest. Pass 52 owner-approved. Remove `df = df[df["volume"] > 0]` from cache write; add derived `is_halted` column. Forward-only migration (existing cache retains dropped days). Sub-decision DEC-383. CAV-037 acknowledged. | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-311** | Trailing-stop ATR exits use ENTRY-time ATR throughout hold period — should refresh daily;  | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | 51 |
| **DECISION-312** | exit_hybrid_50pct has max_days=252 but 11 other exits don't — comparison metrics not apple | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | 51 |
| **DECISION-313** | update_trailing_stop ignores intraday HIGH — stop only updates at close above prior best. Pass 52 owner-approved. Change signature to (trade, today_high, today_low, today_close, vix); use intraday high (long) / low (short) for highest_high/lowest_low tracking. PIT-honest: if intraday extreme triggers stop same day, exit at stop level not close. Joint with DEC-337 + BUG-232. Sub-decision DEC-384. CAV-038 acknowledged (yfinance high/low outliers). | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-314** | Circuit breakers levels 3 and 4 (intraday halt, market halt) documented but NOT implemented. Pass 52 owner-approved with phased path. Level 4 (market-wide >7%/>13%/>20% S&P drawdown halts) implementable from free SPY data. Level 3 (single-name halt) full coverage requires paid halt feed; gap-based proxy has false positives. Static historical halt table for major events (March 2020). Joint with BUG-233. Sub-decisions DEC-385/386/387. CAV-039 acknowledged. | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-315** | Circuit breakers checked one-at-a-time — if Level 1 + Level 5 both fire same day, Level 5  | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | 51 |
| **DECISION-316** | Regime classifier returns 'neutral' default on missing VIX — should refuse to trade with n | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | 51 |
| **DECISION-317** | VIX hard thresholds (40/30/20) flip regime on single print — needs MA smoothing. Pass 52 owner-approved. Replace single-print thresholds with 5-day SMA + hysteresis bands (crisis: enter ≥40, exit <35; high_vol: enter ≥30, exit <27). Joint with regime cluster (BUG-026/027/234/277). Sub-decision DEC-388. CAV-040 acknowledged (smoothing lag tradeoff). | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-318** | AAII pub-lag treatment missing — survey data marked available on survey-Wed, actually published Thu+. Pass 52 owner-approved. Shift `as_of` lookup by 1 trading day (look up survey from prior week ending Friday before D-2). Add `pub_date = survey_date + 1 trading day` column. Joint with BUG-235. Sub-decision DEC-389. | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-319** | AAII auto-refresh missing — committed CSV will go stale, no refresh script in /scripts. Pass 52 owner-approved. New script `scripts/refresh_aaii_sentiment.py` scraping aaii.com/sentimentsurvey + GitHub Actions weekly Friday morning workflow. Joint with DEC-318 (pub_date column). Sub-decision DEC-390. CAV-041 acknowledged (HTML scraping fragility). | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-320** | CNN F&G CSV interpolated between key readings — fabricated values used as PIT signal. Pass 52 owner-approved. Replace interpolation with last-published-only + (value, age_days) tuple; strategies filter age_days ≤ 3 to avoid stale reads. New refresh script using CNN's production.dataviz.cnn.io endpoint. Existing CSV migrated with `is_interpolated=True` flag for historical values. Joint with BUG-237. Sub-decision DEC-391. CAV-042 acknowledged (CNN API undocumented). | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-321** | Liquidity filter market-cap check skips silently if data missing — fail-open instead of fail-closed. Pass 52 owner-approved. Change `apply_liquidity_filter` behavior: missing/zero market_cap REJECTS ticker (returns False), logs warning. Add `LIQUIDITY_FILTER_FAIL_REASONS` enum (missing_market_cap/below_min_cap/below_min_adv/insufficient_history). Joint with BUG-238 + DEC-366 (liquidity floor thresholds already approved). Sub-decision DEC-392. CAV-043 acknowledged (fail-closed rejection rate monitoring). | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-322** | Market cap from yfinance.info CURRENT not historical — backtesting 2020 trades uses 2026 mkt cap. Pass 52 owner-approved. Compute `market_cap_pit(ticker, as_of) = close × shares_outstanding(as_of)`. **BLOCKED ON DEC-257/DEC-383** (fundamentals prefetch provides PIT shares outstanding). Joint with BUG-191 + DEC-299. Sub-decision DEC-393. CAV-044 acknowledged. | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-323** | Sector reclassifications retro-applied — Meta moved from Comms to Tech; 2020 backtests use current sector. Pass 52 owner-approved phased. Phase 1 (free): static `sector_history.csv` with major known reclassifications (2018+ GICS Comms creation, individual moves). Phase 2 (paid): Polygon Reference / FactSet for full PIT. Engine: `get_sector(ticker, as_of=D)` consults history first. Joint with BUG-239. Sub-decisions DEC-394/395. CAV-045 acknowledged. | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-324** | Congressional weight by disclosure_date not transaction_date — smart-money signal weighted | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | 51 |
| **DECISION-325** | Institutional 13F PIT assumes universal on-time filing — late filers (some big funds) invisible. Pass 52 owner-approved. Capture actual `filing_date` from SEC; PIT lookup `get_institutional_positions(ticker, as_of=D)` returns positions where `filing_date <= D` (NOT `quarter_end + 45 <= D`). Joint with BUG-241 + BUG-186. Sub-decision DEC-396. CAV-046 acknowledged. | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-326** | Walk-forward windows hardcoded calendar dates — no rolling logic per DEC-109; stale after June 2026. Pass 52 owner-approved. Replace hardcoded dates with rolling: `train_window_years=4`, `oos_window_years=1`, computed from `today` (configurable). `--anchor-date` flag for reproducibility. Document in PROJECT_PLAN section 11. Joint with DEC-109 (parent). Sub-decision DEC-397. CAV-047 acknowledged. | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
| **DECISION-327** | Short-borrow cost duplicated across improvements.py + exit_manager.py with different units — pick single source. Pass 52 owner-approved. Investigate live backtest path first (`improvements.py:80-84` charges; `exit_manager.py:140-146` says "handled elsewhere"). Consolidate to shared `backtest.engine.costs.calculate_borrow_cost()` consumed by both paths. Unit test: borrow cost charged exactly once per short trade. Sub-decisions DEC-398/399. CAV-048 acknowledged (potential historical PnL inflation if zero-counted in production). | RESOLVED | Batch X53 — High-Impact Engine Bugs | Pass 48 | - |
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
| **DECISION-341** | universe.py docstring claims Wikipedia fetch but code uses static CSV — fix docstring or i | RESOLVED | Batch X55 — Documentation Sync | Pass 48 | 52 |
| **DECISION-342** | Test pass-rate mis-reported — only 38 of 46 tests run cleanly (7 e2e errors); update repor | OBSOLETE | Batch X55 — Documentation Sync | Pass 48 | 52 |
| **DECISION-343** | Pandas-ta deprecation warning on pandas 4.0 — plan replacement (TA-Lib alternative) | PENDING | Batch X55 — Documentation Sync | Pass 48 | - |
| **DECISION-344** | Slippage threshold ATR/price > 3% likely too high — most S&P large caps never trigger | PENDING | Batch X55 — Documentation Sync | Pass 48 | - |
| **DECISION-345** | ICT/SMC timeframe scope — daily-only vs weekly-HTF + daily-trigger vs full multi-timeframe | RESOLVED | Batch X52 — Round 1 Methodology Gaps | Pass 52 | 52 |
| **DECISION-346** | Multidimensional categorical verdict matrix — supersedes single-dimension regime verdict | PENDING | Batch X52 — Round 1 Methodology Gaps | Pass 52 | - |
| **DECISION-347** | Lagging-indicator dominance — add leading-style signals + regime-condition the lagging ones (1+3 combination) | PENDING | Batch X52 — Round 1 Methodology Gaps | Pass 52 | - |
| **DECISION-348** | Event-calendar suppression — FOMC / earnings / CPI date-aware signal gating | PENDING | Batch X52 — Round 1 Methodology Gaps | Pass 52 | - |
| **DECISION-349** | Asymmetric event window — `is_near_high_impact_event` should use pre_days=1, post_days=2-3 instead of symmetric window_days=2 (per microstructure event-volatility research) | PENDING | Batch X52 — Round 1 Methodology Gaps | Pass 52 | - |
| **DECISION-350** | Multi-timeframe testing for NON-ICT strategies — REFRAMED Pass 52: extension of DEC-345 (RESOLVED multi-TF for ICT/SMC) to remaining 60 non-ICT strategies (MACD, RSI, Bollinger, etc.). Should they be backtested on weekly bars to find optimal TF per strategy? Distinct from DEC-345 which only authorized weekly-HTF-context for ICT signals. | PENDING | Batch X55 — Strategy Coverage Gaps (Pass 52) | Pass 52 | - |
| **DECISION-351** | Anchored VWAP for institutional cost-basis context — SUPERSEDED Pass 52 by existing BUG-147 (no Anchored VWAP strategies, MEDIUM) + BUG-151 (Anchored VWAP not computed, HIGH); duplicate logging caught Pass 52 owner correction | SUPERSEDED | Batch X55 — Strategy Coverage Gaps (Pass 52) | Pass 52 | 52 |
| **DECISION-352** | 13F price-level mapping — map institutional accumulation prices from quarterly 13F filings to current price; identify levels where institutions are above/below water | PENDING | Batch X55 — Strategy Coverage Gaps (Pass 52) | Pass 52 | - |
| **DECISION-353** | Risk-reward ratio sweep — owner resolution Pass 52: 2R reward:risk MINIMUM. Current default `exit_fixed_target(target_mult=3.0, stop_mult=2.0)` = 3R/2R = 1.5:1 R/R, which is BELOW the new 2:1 minimum and must be changed. Sweep across 2:1, 3:1, 4:1, 5:1 to find optimal per-strategy/per-regime RR. NEVER test below 2:1 anywhere in the system. | RESOLVED | Batch X55 — Strategy Coverage Gaps (Pass 52) | Pass 52 | 52 |
| **DECISION-354** | Chart pattern strategies — REOPENED Pass 52 from SUPERSEDED. Prior merge into DEC-099 was incorrect — DEC-099 is category-level (Pairs/Calendar/Cross-Asset/Index Rebalance); chart patterns are within-category strategy specifications. Owner directive Pass 52: each chart pattern must be its own testable strategy. This decision is parent/umbrella; child decisions DEC-355 through DEC-362 enumerate individual pattern classes. | PENDING | Batch X55 — Strategy Coverage Gaps (Pass 52) | Pass 52 | - |
| **DECISION-355** | Trendline break + retest strategy — owner directive Pass 52 CRITICAL/MOST-IMPORTANT. Detect trendline (3+ touches), entry on break + retest of broken trendline. Long and short variants. Per CHECKLIST #46: not in PROJECT_PLAN, not in code, not previously in audit. Owner-NEW must-have. | PENDING | Batch X55 — Strategy Coverage Gaps (Pass 52) | Pass 52 | - |
| **DECISION-356** | Channel breakout + retest strategy — owner directive Pass 52 CRITICAL. Parallel-channel detection (ascending, descending, horizontal), entry on break + retest of channel boundary. Distinct from Keltner Channel (volatility band, already in code) — this is price-action channel from swing highs/lows. Long and short variants. | PENDING | Batch X55 — Strategy Coverage Gaps (Pass 52) | Pass 52 | - |
| **DECISION-357** | Range breakout + retest strategy — owner directive Pass 52 CRITICAL. Horizontal range/consolidation detection (N-day range tightness threshold), entry on breakout + retest of range boundary. Long and short variants. Distinct from inside_bar_breakout (1-bar inside another) — this is multi-day range. | PENDING | Batch X55 — Strategy Coverage Gaps (Pass 52) | Pass 52 | - |
| **DECISION-358** | Wedge / triangle / pennant breakout strategies (continuation patterns) — owner directive Pass 52 CRITICAL. Three distinct continuation patterns: rising wedge, falling wedge, symmetrical triangle, ascending triangle, descending triangle, bullish pennant, bearish pennant. Each with break + retest entry. | PENDING | Batch X55 — Strategy Coverage Gaps (Pass 52) | Pass 52 | - |
| **DECISION-359** | Head & shoulders / inverse head & shoulders strategies (reversal patterns) — owner directive Pass 52 CRITICAL. H&S top (bearish) + inverse H&S (bullish). Neckline break + retest entry. Measured-move target = head-to-neckline distance projected from neckline. | PENDING | Batch X55 — Strategy Coverage Gaps (Pass 52) | Pass 52 | - |
| **DECISION-360** | Double top / double bottom strategies (reversal patterns) — owner directive Pass 52 CRITICAL. Double top (bearish) + double bottom (bullish). Neckline break + retest entry. Tolerance window: peaks/troughs within ~3% of each other; minimum N bars apart. | PENDING | Batch X55 — Strategy Coverage Gaps (Pass 52) | Pass 52 | - |
| **DECISION-361** | Cup & handle / inverted cup & handle strategies — owner directive Pass 52 CRITICAL. Cup & handle (bullish continuation): U-shape base + small handle pullback + breakout above handle resistance + retest. Inverted variant for shorts. | PENDING | Batch X55 — Strategy Coverage Gaps (Pass 52) | Pass 52 | - |
| **DECISION-362** | Flag / pennant continuation strategies — owner directive Pass 52 CRITICAL. Bull flag (after sharp rise: tight downward-sloping consolidation, then breakout up + retest), bear flag (mirror). Distinct from DEC-358 pennant (symmetric) — flag is sloping. | PENDING | Batch X55 — Strategy Coverage Gaps (Pass 52) | Pass 52 | - |
| **DECISION-363** | Expand commodity ETF coverage — owner-approved Pass 52 NARROW SCOPE: lithium + base metals only. Add LIT (Global X Lithium & Battery Tech), DBB (Invesco DB Base Metals: aluminum/zinc/copper/lead/nickel), COPX (Global X Copper Miners equity). Other commodity additions (USO crude oil, UNG natural gas, DBC broad basket, DBA agricultural, CPER copper futures) were proposed but NOT approved by owner — remain PROPOSED pending separate approval. No leveraged variants per existing rule. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-364** | Tier 3 momentum watchlist size 50 → 100 — owner-approved Pass 52 NARROW SCOPE. Verbatim directive: "Tier 3 - expand to 100." Code change: `scripts/build_momentum_watchlist.py` `MAX_TICKERS = 50` → `100`. NOTE: broader proposal to "activate Tier 2 + Tier 3 for Phase 1B backtesting (not just Stage 3+)" was Claude's recommendation but was NOT explicitly approved by owner — remains PROPOSED pending separate approval. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-365** | Universe expansion beyond S&P 500 — PROPOSED Pass 52 (NOT approved — Claude over-inferred from owner's earlier directional statement "no need to restrict to just top 500 tickers"; owner's actual Pass 52 directive was Tier 3 size + lithium/base metals only). Proposal: Add Russell 1000 minus S&P 500 ≈ 500 mid-cap names. Phased Phase A (free, current static), Phase B (paid FTSE), Phase C (Russell 2000 +1000, defer). Total designed universe at full activation: ~1100-1200 instruments. AWAITING OWNER APPROVAL. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-366** | Liquidity floor for universe inclusion (any tier) — PROPOSED Pass 52 (NOT approved — Claude inferred silence as approval; owner never explicitly addressed liquidity floor). Proposal: Min price $5, min ADV $5M USD, min market cap $300M, min trading days ≥250 in past year. Re-evaluate annually. Replaces current `min_market_cap_m=100` (BUG-041 flagged "too low" + BUG-238 fail-open). AWAITING OWNER APPROVAL. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-367** | DEC-099-A — Pairs / Stat Arb category — Pass 52 turn 33 owner-approved as PENDING in scope (Phase 1C is Stage 2 sub-phase per turn 32 correction; not deferred). Cointegration tests (Engle-Granger, Johansen) on top S&P 500 sector pairs; beta-neutral position sizing; paired-trade execution mechanics. **Use-case map (#57):** new strategy category for 60-strategy roster expansion; market-neutral signal independent of regime; could leverage Polygon DEC-441 OHLCV + Quiver paid-tier institutional flow signals (DEC-450). ~5-7 days for cointegration framework + 2-3 paired strategies + backtest integration. **Test signals:** cointegration test produces stable beta on known pair (e.g., KO/PEP); paired position sizing produces dollar-neutral exposure; stop-loss honored on individual leg breach. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-368** | DEC-099-B — Calendar / Seasonal strategies — Pass 52 turn 33 owner-approved PENDING. Cheap to implement (date-based filters); event calendar exists. Examples: Sell-in-May, January effect, Santa rally, FOMC drift, end-of-month rebalancing. **Use-case map (#57):** date-of-year and days-to-event cube dimensions in DEC-422 already capture this — strategies just consume those slicing dims. Integration is logging strategies in roster + verifying cube dim populates correctly. ~2-3 days for 4-5 calendar strategies + backtest integration. **Test signals:** seasonal strategy fires only in date-window-active period; cube dim correctly classifies historical bars by season. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-369** | DEC-099-C — Cross-Asset strategies — Pass 52 turn 33 owner-approved PENDING (Phase 1D is Stage 2 sub-phase per turn 32 correction; not deferred). Needs intermarket data feeds (bonds, oil, dollar). **Use-case map (#57):** TLT/GLD/UUP/USO/DBC cross-correlations as regime filters or signal generators; FRED already provides treasury yields (DEC-448 expansion adds DTWEXBGS dollar index, DCOILWTICO oil); yfinance covers ETFs. New strategies: yield-curve-flattening, dollar-strength-into-tech, oil-down-into-airlines, etc. ~5-7 days for 3-5 cross-asset strategies + intermarket signal infrastructure. **Test signals:** cross-asset signal correlates with target asset historically; entry/exit responds to intermarket regime change. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-370** | DEC-099-D — Index Rebalance strategies — Pass 52 turn 33 owner-approved PENDING (Phase 1C is Stage 2 sub-phase per turn 32 correction; not deferred). Needs S&P/Russell adds-drops calendar; joint with DEC-303 historical membership. **Use-case map (#57):** index inclusion drives forced buying (institutional indexers); known announcement-to-effective date window (~3-7 days); frontrun strategy. Russell rebalance is June; S&P quarterly. Joint with DEC-394 sector_history.csv (Phase 1 static reclassifications) and DEC-378 NASDAQ symbol-directory weekly diff (catches some adds via listing). ~3-5 days for index calendar + 2 frontrun strategies. **Test signals:** historical index add events produce expected price drift in announcement→effective window; strategy entry timing tracks calendar. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-371** | DEC-099-E — Within-category gaps catalog — Pass 52 turn 33 owner-approved PENDING. Catalog of gaps within existing strategy categories already in roster: Russell rebalance for momentum category, pairs reversion for mean reversion, dark pool prints (Quiver DEC-450 paid endpoint) for smart money, gap-fade for breakout, etc. **Use-case map (#57):** documents missing strategy variants within categories without creating new category buckets. Output: catalog document or appended to PROJECT_PLAN strategy roster section. ~1 day cataloging + sub-decisions per gap as scoped. **Test signals:** catalog covers ≥10 within-category gaps; each gap has explicit data-source path identified. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-372** | DEC-103 Phase A — GitHub Actions monthly automation of `refresh_extended_universe.py` (Tier 2 auto-populate). New workflow `.github/workflows/refresh_extended_universe.yml`; calls script with `--write`, commits via PR. ~1 day effort. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-373** | DEC-103 Phase B — Update script with `--validate` mode that flags missing-data tickers (yfinance returning empty info) for manual review rather than silent drop. Catches SNDK-style edge cases where yfinance lags new listings. ~1 day effort. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-374** | DEC-103 Phase C — Tier 2 historical-membership backfill for 2010-2024 spinoffs/IPOs. Manual research per spinoff event (Edgar 10-12B filings, news archives) since yfinance unreliable for re-listed tickers. Output: `tier2_membership_history.csv` with ticker/added_date/removed_date. ~3-5 days effort. CAV-028 acknowledged. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-375** | DEC-104 Phase A — Code changes per DEC-364: MAX_TICKERS 50→100 in `build_momentum_watchlist.py`; update `build_phase1b_universe()` to include Tier 3 alongside Tier 1 + ETFs. ~0.5 days effort. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-376** | DEC-104 Phase B — GitHub Actions monthly automation `.github/workflows/refresh_momentum_watchlist.yml`; calls `build_momentum_watchlist.py --write`, commits via PR. ~1 day effort. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-377** | DEC-104 Phase C — Tier 3 historical-recomputation infrastructure. New script `scripts/backfill_tier3_history.py` that loops over each historical month and recomputes the watchlist using only data available at that month's end. ~100 tickers × ~190 months = 19,000 historical screens. Output: `tier3_membership_history.csv`. Engine `get_momentum_watchlist(as_of=D)` returns active watchlist for calendar month containing D. **BLOCKED ON DEC-298 (PIT OHLCV)**. ~3-5 days post-DEC-298 resolution. CAV-027 acknowledged. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-378** | DEC-105 Phase 1 — NASDAQ symbol-directory weekly diff for spinoff/IPO detection. Source: `ftp.nasdaqtrader.com/SymbolDirectory/nasdaqtraded.txt`. Diff against last week's list, flag new tickers, validate market cap >$5B via yfinance. Output: `spinoff_events.csv` with parent_ticker/spinoff_ticker/distribution_date/market_cap_b/sector. ~2 days effort. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-379** | DEC-105 Phase 2 — SEC EDGAR Form 10-12B feed scraping for 30-90 day spinoff lead time. RSS at `sec.gov/cgi-bin/browse-edgar`. HTML/PDF text extraction non-trivial. ~2-3 days effort. May defer if Phase 1 NASDAQ-diff catches enough spinoffs in practice. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-380** | DEC-105 Phase 3 — Polygon Reference corporate-actions API integration (paid). Cleaner data, structured spinoff events. Subscription cost decision separate from this approval. Defer to post-Phase-1/2 evaluation. ~1 day post-subscription. | PENDING | Batch X1 — Data + Universe | Pass 52 | - |
| **DECISION-381** | DEC-307 implementation — `get_ohlcv` symmetric front-extension. After existing tail-extension check, add: if cached_start > requested_start, fetch [requested_start, cached_start - 1day], prepend, save merged Parquet. Update cache index `start` field. Test: cache 2022-2024 → request 2020-2026 → produces 2020-2026, not silent 2022-2024. Fail-fast on yfinance unavailability. ~1 day. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-382** | DEC-308 implementation — Verify exact 20-day threshold location in cache.py + replace hard floor with `min(20, available_days)` + add `LIMITED_HISTORY` flag in result schema. Strategy level (not cache) decides if available data is sufficient for indicator computation. ~0.5 days. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-383** | DEC-310 implementation — Remove `df = df[df["volume"] > 0]` from cache.py write path; add derived `is_halted = (volume == 0) & (close == previous_close)` column. Forward-only migration (existing cache retains dropped days, refetch optional). ~1 day. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-384** | DEC-313 + DEC-337 joint implementation — Change `update_trailing_stop(trade, today_high, today_low, today_close, vix)` signature; long: use today_high for highest_high tracking; short: use today_low for lowest_low. Outlier filter: high must be within 5% of close + sanity-check vs prior day. PIT-honest stop-trigger: if intraday extreme triggered same day, exit at stop level not close. Joint with BUG-232. ~1-2 days. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-385** | DEC-314 Phase A Level 4 market-wide halts — DEFERRED_TO_STAGE_3 per CHECKLIST #56 (Pass 52 turn 25). Live circuit breaker mechanics only matter when executing real orders; Stage 2 backtest uses static historical halt table for known events (March 2020) instead. Original scope preserved for Stage 3 prep theme. ~2 days post-Stage 3. | DEFERRED_TO_STAGE_3 | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-386** | DEC-314 Phase B Level 3 single-name halts via gap-based proxy — DEFERRED_TO_STAGE_3 per CHECKLIST #56. Live single-name halt machinery is Stage 3+ scope; backtest can use historical static table. Original scope preserved for Stage 3 prep theme. | DEFERRED_TO_STAGE_3 | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-387** | DEC-314 Phase C Paid halt feed integration — DEFERRED_TO_STAGE_3 per CHECKLIST #56. Paid feed only valuable for live trading; backtest does not need real-time halt structured data. Subscription decision deferred until Stage 3 prep. | DEFERRED_TO_STAGE_3 | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-388** | DEC-317 implementation — VIX 5-day SMA + hysteresis. `vix_sma_5 = VIX.rolling(5).mean()` for regime input. Crisis enter ≥40, exit <35 (5-pt band). high_vol enter ≥30, exit <27 (3-pt band). Update `regime_filter.py:38-40` + `improvements.py:394`. Joint with BUG-026/027/234/277. ~1 day. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-389** | DEC-318 implementation — AAII pub-lag fix. In `sentiment.py` AAII consumption: when reading for `as_of=D`, look up survey from prior week ending Friday before D-2. Update CSV schema with `pub_date` column. Document rule in docstring + PROJECT_PLAN section 9. Re-run AAII-consuming backtests to validate pre/post-fix delta. ~0.5-1 day. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-390** | DEC-319 implementation — `scripts/refresh_aaii_sentiment.py` (HTML scrape aaii.com/sentimentsurvey/sent_results) + `.github/workflows/refresh_aaii.yml` schedule Friday 14:00 UTC. Auto-PR weekly delta. Validation gate (DEC-065) checks AAII CSV freshness. ~1 day. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-391** | DEC-320 implementation — Replace CNN F&G interpolation with last-published. Expose `(value, last_published_date, age_days)` tuple. Strategies filter `age_days ≤ 3`. New `scripts/refresh_cnn_fear_greed.py` using `production.dataviz.cnn.io/index/fearandgreed/graphdata`. Migrate existing CSV with `is_interpolated=True` flag for historical. ~1 day. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-392** | DEC-321 implementation — `apply_liquidity_filter` fail-closed. Missing/zero market_cap → REJECTS (returns False), logs warning with `LIQUIDITY_FILTER_FAIL_REASONS` enum. Monitor post-deployment rejection rate; investigate if >5% of universe rejected. ~0.5 days. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-393** | DEC-322 implementation — `market_cap_pit(ticker, as_of) = close × shares_outstanding(as_of)`. Replace `info.get("marketCap", 0)` callers. Validation: AAPL 2020-01-01 ≈ $1.3T (not current $3T). **BLOCKED ON DEC-257/DEC-383** (PIT shares outstanding). ~1-2 days post-resolution. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-394** | DEC-323 Phase 1 — Static `sector_history.csv` with major known reclassifications. Schema: ticker, effective_date, old_sector, new_sector, reason. Coverage: 2018+ GICS Comms creation (FB, GOOG, NFLX, DIS); individual moves post-2018. Source: GICS press releases + S&P Dow Jones Indices. ~2 days research+CSV+integration. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-395** | DEC-323 Phase 2 — Polygon Reference for full sector PIT — Pass 52 turn 30 SCOPE CORRECTION per owner directive. Originally DEFERRED_TO_STAGE_3 (sub-decision text said "defer to Stage 3+" pre-DEC-441 when Polygon was unsubscribed). REVERSED to PENDING in-scope Stage 2 — Polygon paid via DEC-441 already approved; sector PIT data covered by DEC-447 (Polygon reference tickers PIT consumption pattern). **LIKELY SUPERSEDED_BY_DEC-447** — verify during DEC-447 implementation: if Polygon `/v3/reference/tickers` historical sector data covers DEC-323 Phase 2 scope (full sector PIT for 5-year backtest), DEC-395 closes as redundant. If gaps exist (e.g., FactSet-only granularity), DEC-395 retains scope as residual. Joint with DEC-394 (sector_history.csv Phase 1, in scope) + DEC-447 (Polygon reference pattern). ~0.5-1 day verification + integration if not fully superseded. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | DEC-447 |
| **DECISION-396** | DEC-325 implementation — In `quiver` 13F prefetch, capture actual `filing_date` per position. PIT lookup `get_institutional_positions(ticker, as_of=D)` returns positions where `filing_date <= D`. Joint with BUG-241 fix. ~1-2 days. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-397** | DEC-326 implementation — Replace hardcoded calendar dates with rolling: `train_window_years=4` (configurable), `oos_window_years=1` (configurable), computed from `today`. `--anchor-date YYYY-MM-DD` flag locks reference date for reproducibility. Document in PROJECT_PLAN section 11. ~1 day. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-398** | DEC-327 Phase A — Investigate live backtest path: trace whether `improvements.calculate_round_trip_pnl` is production or `exit_manager` is. Quantify whether borrow cost is currently zero/single/double-counted in production runs. ~0.5 days. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-399** | DEC-327 Phase B — Consolidate to shared `backtest.engine.costs.calculate_borrow_cost(trade, hold_days)` consumed by both paths. Remove duplication. Unit test: borrow cost charged exactly once per short trade. Re-run historical short-trade backtests; document net PnL delta. ~0.5 days. | PENDING | Batch X53 — High-Impact Engine Bugs | Pass 52 | - |
| **DECISION-400** | DEC-080 Phase A — Replace hardcoded Bonferroni N=60 with `len(STRATEGIES_TESTED)` dynamic count from strategy registry. Compute t-stat per strategy: `t = mean(returns) / (std(returns) / sqrt(n_trades))`. Reporting includes raw p, Bonferroni-adjusted p, t-stat. Joint with BUG-018 fix. ~1 day. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-401** | DEC-080 Phase B — Add Holm-Bonferroni step-down option (less conservative than Bonferroni for correlated strategies). Add min-Sharpe filter (Sharpe ≥ 0.5) joint with BUG-038. Owner approval gate: Bonferroni vs Holm vs FDR (Benjamini-Hochberg) as default. ~1 day. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-402** | DEC-081 Phase A — Sharpe canonicalization. Compute both `sharpe_per_trade` (current) and `sharpe_daily = sqrt(252) × mean(daily_returns) / std(daily_returns)`. Convert per-trade to daily by mark-to-market: each open position contributes daily PnL change. ~1 day. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-403** | DEC-081 Phase B — Sortino implementation. `sortino = sqrt(252) × mean(daily_returns) / std(daily_returns[daily_returns < 0])`. Same daily mark-to-market as Sharpe daily. ~0.5 days. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-404** | DEC-081 Phase C — Transaction cost sensitivity. Re-run metrics at 4 cost levels: 0bps, 5bps, 10bps, 20bps round-trip. Strategy verdict includes all 4 numbers. Strategy net-positive at 0bps but net-negative at 10bps is NOT viable. ~1 day. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-405** | DEC-082 implementation (Option A scope) — New `backtest/results/stress_tests.py`. Test 2022 full year (Sharpe ≥ 0, DD ≤ 20%, Win Rate ≥ 40%) + crisis sub-periods VIX > 30 sustained within 2021-2024 (Q1 2022 invasion, March 2023 SVB, Oct 2023 escalation; calibrate per period). Strategy verdict includes `stress_test_passed: dict[period -> bool]`. Joint with DEC-014. ~2 days. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-406** | DEC-083 implementation — Tiered min-trades enforcement in strategy verdict logic. Daily-freq/Earnings/Calendar: 300 → INSUFFICIENT_OOS_DATA. Regime-gated/Crisis: 100 → INSUFFICIENT_FREQUENCY (Phase 1D eligible). Event-driven: 30 → EVENT_DRIVEN_LIMITED_SAMPLE flag. Report `effective_n` (Bessel-corrected for correlation) alongside raw n_trades. ~1 day. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-407** | DEC-085 Phase A — Macro indicator expansion. Add 8 FRED series to existing 9: PAYEMS (NFP), MANEMP (manufacturing), UMCSENT (consumer sentiment), RSAFS (retail sales), HOUST (housing starts), INDPRO (industrial production), BAMLH0A0HYM2 (HY spread), M2SL (money supply). Update `macro.py` SERIES_MAP. Add to `macro_combined.parquet` prefetch. ~1 day. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-408** | DEC-085 Phase B — Compute macro correlation tags per strategy. New `compute_macro_correlations(strategy_pnl)` in metrics.py. Returns dict of correlations + tags: vix_sensitive (>0.3), rate/curve/dollar/credit/inflation/growth/consumer/liquidity_sensitive (>0.2). ~1 day. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-409** | DEC-085 Phase C — Event-window tags. Existing FOMC/CPI/NFP calendars + add earnings season start/end (computed), Russell rebalance dates (Jun + Sep), S&P rebalance (quarterly Friday), opex (3rd Friday + EOM). Tag strategies by ±N day window performance variance: fomc_volatile, cpi_volatile, nfp_volatile, earnings_season_dependent. ~1-2 days. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-410** | API endpoint utilization audit — Pass 52 owner-approved CRITICAL TODO with **comprehensive 6-dimension use-case mapping schema** (Pass 52 turn 16 expanded per L136/CHECKLIST #57) **+ EXTENDED SCOPE per Pass 52 turn 19** (one-time CHECKLIST #56 override per owner directive: "extend DEC-410 audit to ALL APIs in the audit md and project plan across all phases"). **Extended in-scope APIs (~17 total):** Tier 1 PROJECT_PLAN section 10 (10 APIs: yfinance, Alpha Vantage [deprecated per DEC-440], Polygon, OpenBB, Quiver, Unusual Whales, Ortex, FRED, AAII, CNN F&G); Tier 2 AUDIT.md alternatives mentioned (Tiingo, IEX Cloud, Financial Modeling Prep, SEC EDGAR, Refinitiv/Bloomberg as institutional reference); Tier 3 social/sentiment (Reddit, Stocktwits); Tier 4 library-based sources (smartmoneyconcepts, pandas-datareader, fredapi). Stage 3+ APIs (Unusual Whales, Ortex) included in this audit ONLY (audit deliverable spans all phases); their CONSUMPTION decisions remain CHECKLIST #56 scoped (deferred until Stage 3+). **Hypothesis-driven framing per Pass 52 turn 19 owner approval:** each API section includes 2-4 explicit hypotheses to test (e.g., for Polygon: H1 daily OHLCV higher-quality than yfinance; H2 precomputed indicators for DEC-439 differential reference; H3 intraday quotes for slippage calibration). Hypotheses become DEC-442+ sub-decisions based on findings. **AUDIT-AS-SOURCE-OF-TRUTH:** API list per audit decisions takes precedence over PROJECT_PLAN section 10 when in conflict (owner Pass 52: "PROJECT_PLAN is outdated, heavily dependent on audit"). **Per-API audit schema (mandatory 6-dimension cross-reference per L136/#57):** (1) Subscription tier + cost + rate limits; (2) Available endpoints — every endpoint with PIT-safety flag, lookback range, free-in-tier flag, currently-used flag; (3) Currently consumed code references (file:function); (4) Gaps — endpoints in tier NOT consumed; **(5) Use-case cross-reference — for each endpoint: which strategies/agents/DEC-422 cube dimensions consume it (or could)? Map endpoints → 60+ strategies, ~11 agents, ~17 cube dimensions; (6) Caching & rate-limit feasibility for S&P 500 × 5-year scope (per DEC-411).** Each meaningful gap becomes candidate sub-decision (DEC-442+). **OpenBB consumption gap (PROJECT_PLAN says ✓, code shows zero):** dual treatment per Pass 52 owner approval — flag in API_AUDIT.md OpenBB section + sub-decision to either consume or remove from project scope (NOT a BUG; it's unresolved scope per audit-as-source-of-truth principle). **Deliverable:** new file `API_AUDIT.md` committed to repo, organized in 4 tiers above. **Effort revised:** ~10-14 days (was ~5-6d for 7 APIs; ~10-14d for ~17 APIs with hypothesis-driven depth per Polygon analysis pattern). **Pre-condition gate before next backtest pass run.** Sub-decisions to be created per API after audit. NO additional cost for inventory phase — leverages existing tier only; subscription decisions for currently-unsubscribed APIs become separate sub-decisions. **Pass 52 turn 22: RESOLVED — API_AUDIT.md committed (4 batches, ~1704 lines, 17 APIs across 4 tiers). 15 sub-decisions DEC-442 through DEC-456 owner-approved and logged covering Polygon expansion, yfinance demotion, FRED expansion, Quiver expansion, Finnhub deprecation, OpenBB removal, Alpha Vantage deprecation timeline, SEC EDGAR differential reference. 14 BUGs in resolution path. Net architectural simplification: 9 sources → 4 active primaries (Polygon $30/mo + Quiver free + FRED + AAII/CNN F&G).** | RESOLVED | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | DEC-442,DEC-443,DEC-444,DEC-445,DEC-446,DEC-447,DEC-448,DEC-449,DEC-450,DEC-451,DEC-452,DEC-453,DEC-454,DEC-455,DEC-456 |
| **DECISION-411** | DEC-109 Phase A — Extend backtest data load from 2021-01-04 to 2018-01-01 (3 additional years). Joint with DEC-298 PIT cache rebuild (auto_adjust=False). Update config DATA_LOAD_START. Refetch ~509 tickers × 3 years OHLCV (free yfinance). ~1 day post-DEC-298 resolution. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-412** | DEC-109 Phase B — Implement rolling 5yr/1yr walk-forward in walk-forward engine. Train: 5-year window. OOS: 1-year window. 2 OOS rolling windows in extended scope: (Train 2018-2022 → OOS 2023; Train 2019-2023 → OOS 2024). Update DEC-326's `train_window_years=4` → `5`; keep `oos_window_years=1`. `--anchor-date` flag preserved. ~1 day post-DEC-411. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-413** | DEC-110 implementation — Deflated Sharpe in metrics.py. Inputs: realized SR, n_trades, return skewness γ3, return kurtosis γ4, total strategies tested N. SR* = √(2·ln(N)). Output per strategy: `psr` field (probability true Sharpe > 0). Threshold PSR ≥ 0.95 = pass. Document in PROJECT_PLAN section 11. Reference Bailey et al. 2014. ~1-2 days. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-414** | DEC-111 Phase A — Add `statsmodels>=0.14.0` to requirements.txt. Implement ADF test on strategy equity curve (~1000 daily PnL observations). Output per strategy: `is_stationary` bool (ADF p < 0.05). ~0.5 days. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-415** | DEC-111 Phase B — Rolling 1-year Sharpe deviation test. Compute Sharpe over 252-day rolling windows; flag strategies where any window deviates >2σ from full-period Sharpe. Output per strategy: `rolling_sharpe_stable` bool, `max_sharpe_deviation` numeric. ~0.5 days. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-416** | DEC-111 Phase C — Chow split-sample structural break test. Only computed when n_trades ≥ 600 (300 per half). Split at midpoint; test if mean returns differ significantly. Output per strategy: `chow_break_detected` bool OR `INSUFFICIENT_SAMPLE` flag. ~1 day. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-417** | Test-run audit gate — Pass 52 owner-approved CRITICAL process gate. **Reframed Pass 52 turn 8 (per owner challenge): DEC-417 is ONE LAYER in multi-layer defense, NOT THE catch mechanism.** Catches approval-vs-implementation gap class only. Other classes (regressions, edge cases, silent behavior changes, implementation bugs, decision-logic errors) need other mechanisms — see DEC-436/437/438/439 (CI/CD + property-based + characterization + differential testing) per Phase 0.E formalization. Plus owner adversarial review (informal, ongoing). **Sequence:** AFTER full data prefetch (DEC-410, DEC-411) AND all themes reviewed: run limited-sample backtest (10 tickers × 60 days × current strategies). For EVERY decision in AUDIT_INDEX.md (~437 total per Pass 52 retroactive scope per owner directive), populate validation table in `AUDIT_TEST_RUN_RESULTS.md`: decision_id, recommendation, test_signal, test_output_expected, test_mismatch_action, test_mismatch_flag (binary). DEFERRED-status decisions (Stage 3+ scope per Pass 52 filter) skip validation until Stage 3 prep theme. Effort ~30 hrs for Phase 0+Stage 2 in-scope decisions (~330 of 437 after deferral). Codified L133 + CHECKLIST #54. CAV-057 acknowledged (retroactive validation may identify obsolete decisions). | PENDING | Batch X57 — Test-Run Audit Gate (Pass 52) | Pass 52 | - |
| **DECISION-418** | DEC-129 implementation — Live-vs-backtest comparison framework. New module `backtest/results/stage3_gate.py`. DEFERRED_TO_STAGE_3 per owner Pass 52 scope filter. Original scope preserved. ~2 days post-Stage 3 paper trading. | DEFERRED_TO_STAGE_3 | Batch X14 — Validation criteria | Pass 52 | - |
| **DECISION-419** | DEC-130 implementation — Capacity stress + slippage model scaling. DEFERRED_TO_STAGE_3 per owner Pass 52 scope filter. Original scope preserved. ~3-4 days post-Stage 4 prep. | DEFERRED_TO_STAGE_3 | Batch X14 — Validation criteria | Pass 52 | - |
| **DECISION-420** | DEC-131 implementation — Agent value-add A/B framework with three-case pairing (Pass 52 turn 13 owner-approved). Run Stage 2 candidates twice: rules-only path + agent-overlay path. Per (ticker, date, signal) tuple, compute one of three cases: (1) rules=YES, agent=YES → `paired_pnl = agent_pnl - rules_pnl`; (2) rules=YES, agent=NO → `counter_pnl = -rules_pnl` (agent disagreement saves/misses rules outcome); (3) rules=NO, agent=YES → `counter_pnl = +agent_pnl` (agent-originated trade); (4) rules=NO, agent=NO → no observation (both correctly skip; not counted). Aggregate: `agent_value_add = sum(paired_pnl) + sum(counter_pnl)`. Compute `agent_sharpe` and `rules_sharpe` from full trade lists; apply DEC-131 two-gate test. Three-case logic prevents bias from disagreement under-counting. ~3 days (was ~2 days; +1 day for three-case correctness). Joint with DEC-205-209 (A/B infrastructure). **Test signals:** rules_yes_agent_no with rules_pnl<0 → counter_pnl>0 (agent saved loss); rules_no_agent_yes with agent_pnl>0 → counter_pnl>0 (agent originated win); paired case with agent_pnl>rules_pnl → paired_pnl>0. | PENDING | Batch X14 — Validation criteria | Pass 52 | - |
| **DECISION-421** | DEC-132 implementation — Calendar-year Sharpe variance computation. DEFERRED_TO_STAGE_3 per owner Pass 52 scope filter. Original scope preserved. ~1 day post-DEC-081 + post-Stage 3 prep. | DEFERRED_TO_STAGE_3 | Batch X14 — Validation criteria | Pass 52 | - |
| **DECISION-422** | Phase 1B-α dimensional space optimization framework — Pass 52 owner-approved CRITICAL meta-decision. Phase 1B-α purpose redefined: NOT a series of patches but the comprehensive discovery system to identify best (strategy, exit_method) pair across full dimensional space, BEFORE AI agents are layered on top. **Output:** multi-dim sparse table where each cell tells the live system "given current state X, the best entry-exit pair is Y with confidence Z." **Dimensions (mandatory + recommended Tier 1+2+4+5; hold duration EXCLUDED — it's an outcome not input):** Strategy (dynamic count, ~60 + DEC-355-362 chart patterns + future additions), Exit method (17 after DEC-067), Regime (4), Sector (11 GICS), Confidence tier (4), Direction (2), Days-to-earnings (4 buckets), Smart money score (3 bands), VIX level (4 bands finer than regime), Yield curve state (3), AAII extreme (3), CNN F&G (5), Cap-band (4), Volatility-bucket (4), Distance from 52wk high (3), Days-to-FOMC/CPI/NFP (3 each), Earnings season binary, Market breadth (3), Relative strength vs sector (3). **Per-cell output schema (REVISED Pass 52 turn 6 per owner correction — original schema omitted ROI/R:R/profit factor):** Performance (`roi_pct`, `sharpe`, `sortino`); R:R + trade quality (`reward_risk_ratio`, `rr_compliance` boolean per DEC-353 2R minimum, `profit_factor`, `expectancy`); Sample (`win_rate`, `n_trades`, `avg_win`, `avg_loss`, `avg_hold_days` as outcome diagnostic); Drawdown/capacity (`max_drawdown`, `calmar`, `max_adverse_excursion_avg`, `max_favourable_excursion_avg`); Cost-adjusted (`roi_after_costs`, `sharpe_at_5bps/10bps/20bps` per DEC-081 phase C); Statistical confidence (`bonferroni_p`, `psr` per DEC-110, `t_stat`, `ci_95`); Fallback metadata (`fallback_used`, `fallback_reason`); **Pair verdict (PASS | FAIL_RR | FAIL_CONFIDENCE | FAIL_DRAWDOWN | INSUFFICIENT_SAMPLE) — FAIL_RR is HARD REJECT regardless of other metrics per DEC-353 2R constraint.** **Methodology:** Hybrid Approach A (marginal heatmaps for stat validity) + Approach B (3D combined for top-N strategies); Approach C (Bayesian shrinkage) deferred to Phase D. **Statistical gates per cell:** n_trades ≥ 30 + Bonferroni p<0.05 + PSR ≥ 0.95 + t-stat ≥ 3.4 + **R:R ≥ 2.0 (DEC-353 hard constraint)**. **Implementation effort:** ~20-28 days (4-6 weeks). **Pre-condition gate before Stage 1 backtest run.** **Test signals (per DEC-417/CHECKLIST #54):** test run produces non-empty cube; at least one cell flagged INSUFFICIENT_SAMPLE; at least one cell with VALID confidence; at least one cell flagged FAIL_RR (verifies hard reject works); roi_pct + reward_risk_ratio + profit_factor + max_drawdown all populate non-zero across cells; cost-adjusted Sharpe at 5/10/20bps differs from base Sharpe (verifies cost sensitivity scaffolding wired). Joint with DEC-410 (API audit), DEC-411 (data extension), DEC-068 (per-cell bootstrap), DEC-069 (SUPERSEDED), DEC-080/081/082/083/085/110/353/388. Sub-decisions DEC-425-431. CAV-062 acknowledged (combinatorial explosion limits combined-cell density beyond 3 dimensions). | PENDING | Batch X58 — Phase 1B-α Dimensional Framework (Pass 52) | Pass 52 | - |
| **DECISION-423** | DEC-068 expansion (per Pass 52 DEC-422) — Bootstrap CI + pairwise significance now operates at PER-CELL level (not per-strategy). For each cell in dimensional cube: 1000 resample bootstrap on cell trades; pairwise (strategy, exit) comparisons within cell; Bonferroni-correct across all cell pairs in dimensional cube. Output per cell: bootstrap CI on Sharpe + pairwise winner. Cells with n<30 trades fall back to marginal-best per dimension. Joint with DEC-422 statistical gates. | PENDING | Batch X4 — Statistical Methodology | Pass 52 | - |
| **DECISION-424** | DEC-069 SUPERSEDED by DEC-422 (Pass 52). Per-regime exit selection was narrow scope; superseded by full dimensional space optimization in DEC-422 where regime is one of ~17 dimensions. DEC-069's narrow methodology (per-strategy × per-regime) becomes a marginal-analysis output of DEC-422's broader framework. Mark DEC-069 SUPERSEDED_BY_DEC-422; close as resolved-via-supersession. | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 52 | - |
| **DECISION-425** | DEC-422 Phase 1: Dimensional slicing infrastructure. Build per-cell aggregation engine in `backtest/results/dim_cube.py`. Inputs: ClosedTrade rows + dimension-extraction functions per slicing var. Output: sparse multi-dim numpy/pandas cube. Memory-efficient (sparse storage; only populated cells stored). ~5-7 days. | PENDING | Batch X58 — Phase 1B-α Dimensional Framework (Pass 52) | Pass 52 | - |
| **DECISION-426** | DEC-422 Phase 2: Per-cell statistical engine. For each populated cell: compute full metrics suite per DEC-422 schema (`roi_pct`, `sharpe`, `sortino`, `reward_risk_ratio`, `profit_factor`, `expectancy`, `win_rate`, `n_trades`, `avg_win`, `avg_loss`, `avg_hold_days`, `max_drawdown`, `calmar`, `max_adverse_excursion_avg`, `max_favourable_excursion_avg`, `roi_after_costs`, `sharpe_at_5bps/10bps/20bps`) + statistical fields (`bonferroni_p`, `psr`, `t_stat`, `ci_95`). Apply **5-gate validity filter:** n≥30 + p<0.05 + PSR≥0.95 + t-stat≥3.4 + **R:R≥2.0 (DEC-353 hard constraint)**. Tag pair_verdict: PASS / FAIL_RR (hard reject) / FAIL_CONFIDENCE / FAIL_DRAWDOWN / INSUFFICIENT_SAMPLE. Cells failing R:R≥2.0 are HARD-REJECTED regardless of other metrics. ~3-4 days. Joint with DEC-080/110/353. | PENDING | Batch X58 — Phase 1B-α Dimensional Framework (Pass 52) | Pass 52 | - |
| **DECISION-427** | DEC-422 Phase 3: Marginal heatmap analysis (Approach A). For each pair (strategy_i, exit_j), compute per-dimension marginal heatmap. Statistically valid for 2D slicing. Output: marginal-best exit per (strategy, dimension) tuple. ~2-3 days. | PENDING | Batch X58 — Phase 1B-α Dimensional Framework (Pass 52) | Pass 52 | - |
| **DECISION-428** | DEC-422 Phase 4: Combined 3D analysis (Approach B). For top-20% strategies from Phase 3, run 3D combined cells (strategy × regime × second-dim). Cells with n<30 fall back to marginal best. ~3-4 days. | PENDING | Batch X58 — Phase 1B-α Dimensional Framework (Pass 52) | Pass 52 | - |
| **DECISION-429** | DEC-422 Phase 5: Live decision lookup table builder. Produce queryable lookup: given current state vector → return (strategy, exit_method, confidence) tuple. Cells with INSUFFICIENT_CONFIDENCE return fallback to higher-aggregate cell. JSON output for live system consumption. ~2 days. | PENDING | Batch X58 — Phase 1B-α Dimensional Framework (Pass 52) | Pass 52 | - |
| **DECISION-430** | DEC-422 Phase 6: Dashboard 1 visualization for multi-dim cube. Streamlit interactive: pick 2 dimensions → display Sharpe heatmap; pick 3 dimensions → display 3D scatter; per-cell drill-down to underlying trades. Filter sliders for all other dimensions. ~3-5 days. Joint with DEC-199 (Dashboard 1 spec). | PENDING | Batch X58 — Phase 1B-α Dimensional Framework (Pass 52) | Pass 52 | - |
| **DECISION-431** | DEC-422 Phase 7: Validation/regression test suite. Synthetic test cases: (1) cell with known statistical properties → verify gates fire correctly; (2) sparse cell → verify INSUFFICIENT_SAMPLE flag; (3) high-correlation strategies → verify Bonferroni adjusts properly; (4) full pipeline integration test on 10-ticker × 60-day sample. ~2-3 days. Joint with DEC-417 test-run audit gate. | PENDING | Batch X58 — Phase 1B-α Dimensional Framework (Pass 52) | Pass 52 | - |
| **DECISION-432** | DEC-067 Phase A — Implement 3 new indicators in `backtest/signals/technical.py`: chandelier exit (highest_high - ATR×N), parabolic SAR (acceleration factor algorithm), supertrend (ATR-band-based directional). Validate against TradingView/standard implementations. Add unit tests. ~2-3 days. | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 52 | - |
| **DECISION-433** | DEC-067 Phase B — Implement 6 simple new exit methods in `backtest/engine/exit_strategies.py`: exit_chandelier (mult ≥ 2.5 per DEC-353), exit_psar, exit_supertrend, exit_volume_climax (vol > 3× ADV + price weakness), exit_rsi_extreme (RSI > 75 with bearish divergence long, mirror short), exit_partial_scaleout (50% off at 2R + chandelier rest), exit_kelly_target (uses metrics._kelly_criterion). Add to EXIT_STRATEGIES dict. ~3 days. | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 52 | - |
| **DECISION-434** | DEC-067 Phase C — Implement 2 dependent new exit methods: exit_volatility_regime (BLOCKED on DEC-388 regime classifier), exit_macro_event (BLOCKED on DEC-409 event windows). Implement after dependencies land. ~1 day post-deps. | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 52 | - |
| **DECISION-435** | DEC-075 implementation — Add `aep_pct` per-trade in metrics.py: `(mfe - exit_pnl) / mfe` for winning trades only; None for losing trades. Per-strategy aggregate `mean_aep_pct`. POOR_EXIT_TIMING flag if mean > 0.5. Add to DEC-422 cell schema as derived field. ~0.5 days. | PENDING | Batch X6 — Exits + Circuit Breakers | Pass 52 | - |
| **DECISION-436** | CI/CD regression pipeline (Phase 0.E formalization) — Pass 52 owner-approved as Layer 2 of multi-layer catch-mechanism defense (Layer 1 = pre-flight checklist; Layer 3 = property-based tests DEC-437; Layer 4 = characterization tests DEC-438; Layer 5 = differential testing DEC-439; DEC-417 = approval-vs-implementation gap layer). GitHub Actions workflow on every commit: run `python -m pytest backtest/tests/` + assert specific behaviors (`vix_threshold == 40`, `exit_method_count >= 17`, `R:R >= 2.0` across all exits per DEC-353, no negative position sizes, no >100% capital allocation). Workflow: `.github/workflows/regression.yml`. Catches: regressions, contract violations, behavioral changes. Misses: errors in tests themselves, errors in unwritten tests. ~2-3 days setup. Phase 0 + Stage 2 in scope per owner Pass 52 filter. **Test signal (per CHECKLIST #54):** workflow runs on PR/push; failing assertions block merge; commit SHA recorded with pass/fail status. CAV-065 acknowledged (test coverage gaps are blind spot — only catches what tests assert). | PENDING | Batch X59 — Phase 0.E Catch-Mechanism Defense (Pass 52) | Pass 52 | - |
| **DECISION-437** | Property-based testing via `hypothesis` library (Phase 0.E formalization) — Pass 52 owner-approved as Layer 3 of multi-layer defense. `hypothesis` generates random inputs across input space; verifies properties hold for ALL generated cases. Target invariants for high-stakes computations: (1) `R:R >= 2.0` for any trade with non-zero stop and target (DEC-353 hard constraint); (2) PIT correctness — `loader.fetch(as_of=D)` never returns rows with date > D (per DEC-040/DEC-050); (3) Sharpe formula symmetry — sign-flip returns produces sign-flipped Sharpe; (4) position size monotonicity — higher confidence tier produces ≥ position size of lower tier given same other inputs; (5) stop never moves against trade direction; (6) FAIL_RR fires for any cell with R:R<2.0 in DEC-422 dimensional cube. Add `hypothesis>=6.0` to requirements.txt. ~3-5 days for high-stakes invariants. Catches: edge cases at scale, boundary conditions, combinatorial test space. Misses: errors in property definitions; bugs that don't violate chosen properties. **Test signal:** hypothesis runs find no counterexamples for defined invariants; if counterexample found, test fails with shrunk minimal failing case. CAV-066 acknowledged (property completeness is the limitation — bugs outside property scope still escape). | PENDING | Batch X59 — Phase 0.E Catch-Mechanism Defense (Pass 52) | Pass 52 | - |
| **DECISION-438** | Characterization / golden-master tests (Phase 0.E formalization) — Pass 52 owner-approved as Layer 4 of multi-layer defense. Capture full output of known-good backtest run as golden master; future runs diff against it. Snapshot key outputs: (a) per-strategy metrics table (Sharpe, ROI, win_rate, R:R, profit_factor, etc. for known seed run); (b) sample trade log (first N trades with entry/exit/PnL); (c) regime-classifier output sequence on known VIX series; (d) DEC-422 dimensional cube cell verdicts on test sample. Diff tooling: any unintended change flagged immediately; intentional changes require manual approval to update master. Storage: `backtest/tests/golden/` directory. ~2-3 days per major output. Catches: silent behavior changes, accidental scope creep, refactoring regressions. Misses: wrong-from-day-1 errors (golden master IS the wrong behavior), intentional changes need manual approval. **Test signal:** golden masters captured; minor refactor produces zero diff; intentional change flagged for review. CAV-067 acknowledged (golden master quality is the bound on test quality — captures whatever current behavior is, including bugs). | PENDING | Batch X59 — Phase 0.E Catch-Mechanism Defense (Pass 52) | Pass 52 | - |
| **DECISION-439** | Differential testing (Phase 0.E formalization) — Pass 52 owner-approved as Layer 5 of multi-layer defense. Run same logic through two independent implementations; flag any divergence. Target highest-stakes computations only (cost-justification: requires writing things twice): (1) R:R computation (pandas-based vs pure-numpy; DEC-353 enforcement); (2) PIT loader (freezegun-based DEC-050 vs separate as_of-filter implementation); (3) Sharpe daily mark-to-market (DEC-081 Phase A) — vectorized vs trade-by-trade. Implement as test fixtures comparing outputs across implementations on identical inputs. ~3-4 days for 3 high-stakes computations. Catches: implementation bugs, edge cases where one implementation is buggy. Misses: bugs present in both implementations (common-mode failure). **Test signal:** both implementations produce identical output to floating-point precision on test sample; divergence triggers test failure with diff details. CAV-068 acknowledged (differential testing only valuable for computations worth writing twice; common-mode failure not caught). | PENDING | Batch X59 — Phase 0.E Catch-Mechanism Defense (Pass 52) | Pass 52 | - |
| **DECISION-440** | Alpha Vantage replaced by Polygon — Pass 52 owner-confirmed (turn 16): "I believe it was polygon. I remember covering in another chat on pricing about polygon." Polygon takes over Alpha Vantage's roles: news sentiment (replaces 25-ticker AV cap), fundamentals where applicable. Alpha Vantage code consumption (backtest/agents/pipeline.py + data/smart_money.py + scripts/prefetch_alphavantage_news.py) marked for deprecation post-Polygon migration. Polygon $30/month subscription — already considered Stage 1-2 in scope per DEC-410. Existing AV cache/parquet artifacts retained for transition period; new prefetches go through Polygon. Joint with DEC-410 (audit treats AV as deprecated and Polygon as canonical news/fundamentals source) + DEC-441 (subscription purchase). Sub-decisions to follow: (a) Polygon news endpoint integration; (b) Polygon fundamentals coverage check; (c) AV code deprecation timeline. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-441** | Polygon Stocks Starter $30/month subscription — Pass 52 owner-approved purchase NOW (Phase 0 prep). Replaces 4 jobs in our system: (1) earnings calendar via DEC-256; (2) news sentiment via DEC-440 (replaces broken Finnhub free tier per BUG-053/181 + AV's 25-ticker cap); (3) fundamentals via DEC-257; (4) reference/corporate actions (splits, dividends, ticker changes for PIT correctness). Cost rationale: $30/mo for 4 use cases vs $0-50/mo Finnhub for 1 broken use case + unresolved fundamentals. Net architecture simplification: 4 sources (AV + Finnhub + OpenBB + ?) → Polygon as primary + yfinance + Quiver (paid tier ~$50-100/mo, already active per owner Pass 52 turn 28 correction; not new cost) + FRED + AAII/CNN. **Stage 2 monthly cost (corrected):** Polygon $30 + Quiver paid $50-100 = $80-130/mo (was $30 in original DEC-441 framing which incorrectly assumed Quiver free tier per stale code comment in smart_money.py). **Use-case map (per #57):** earnings (DEC-256), news (DEC-440), fundamentals (DEC-257), reference data, intraday backups. **OpenBB scope (per DEC-410):** likely "remove from project scope" pending DEC-410 audit verification (Polygon covers OpenBB use cases). **Implementation:** owner purchases $30/mo subscription; API key added to config; Phase 0.A prefetch scripts updated. Effort: ~0.5d subscription setup + integration absorbed into DEC-256/257/440 effort estimates. **Test signals:** Polygon API key configured; sample earnings/news/fundamentals fetch returns non-empty; rate limits documented per DEC-410 audit feasibility dim. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-442** | Demote yfinance to fallback OHLCV after Polygon prefetch validation — Pass 52 owner-approved (DEC-410 Batch 1, Hypothesis H-yfinance-1). Sequence: (a) implement Polygon `/v2/aggs/...` prefetch per DEC-441/DEC-411; (b) sample-test against yfinance for 20 tickers × 50 dates; (c) if Polygon ≥ yfinance quality, switch primary OHLCV to Polygon, demote yfinance to fallback role; (d) yfinance retained for VIX/DXY (or use FRED VIXCLS per DEC-448) and last-resort fallback. **Use-case map (#57):** ALL 60 strategies (foundation), DEC-422 cube ALL 17 dims. **Resolves:** BUG-19 (Codespaces yfinance blocking), BUG-46 (market_cap snapshot), BUG-62 (2020 data missing), BUG-109 (auto_adjust drift), BUG-265 (auto_adjust hardcoded). Effort: absorbed into Polygon OHLCV prefetch. **Test signal:** sample comparison documents Polygon vs yfinance discrepancies; switch confirmed if Polygon non-inferior. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-443** | Replace yfinance .info with Polygon reference endpoints — Pass 52 owner-approved (DEC-410 Batch 1, Hypothesis H-yfinance-2). Replace `Ticker.info` calls (sector, market_cap, IPO date) with Polygon `/v3/reference/tickers/{ticker}` PIT-correct historical reference data. Update `backtest/data/universe.py` and any other `.info` consumers. **Use-case map (#57):** universe management, sector cube dim, cap_band cube dim, fundamental strategies. **Resolves:** BUG-218 (CRITICAL OPEN — yfinance fetch_info CURRENT not as_of), BUG-179 (yfinance .info live during backtest universe load). Joint with DEC-447 (PIT consumption pattern). Effort: ~1d. **Test signal:** sector and market_cap fields populate from Polygon for ≥95% S&P 500; PIT loader rejects current-only queries. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-444** | Deprecate `days_to_next_earnings()` via yfinance live calls — Pass 52 owner-approved (DEC-410 Batch 1, Hypothesis H-yfinance-3). Route all `days_to_next_earnings()` lookups through DEC-256 Polygon earnings cache parquet (`backtest/data/cache/earnings/{TICKER}.parquet`). Remove yfinance.earnings_dates live-call path. **Use-case map (#57):** days_to_earnings_bucket cube dim (DEC-422), exit_macro_event (DEC-067), Macro/Sentiment Agents. **Resolves:** BUG-280 (silent None on yfinance block), BUG-013 (~106K live yfinance calls during backtest). Effort: absorbed into DEC-256 implementation. **Test signal:** zero yfinance live calls during backtest; days_to_next_earnings returns valid value or explicit None with logging. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-445** | Polygon precomputed indicators integration as DEC-439 layer 5 differential reference — Pass 52 owner-approved (DEC-410 Batch 1, Hypothesis H-polygon-3). Use Polygon `/v1/indicators/{sma,ema,rsi,macd}/{ticker}` precomputed values as independent third-party reference for our pandas/numpy implementations. Strengthens DEC-439 differential testing layer 5 catch mechanism. Catches common-mode failures per CAV-068 (would otherwise escape pandas-vs-numpy comparison written by same person). **Use-case map (#57):** DEC-439 catch mechanism, all strategies using SMA/EMA/RSI/MACD. **Test signal:** Polygon RSI matches our computed RSI within float precision on test sample; divergence triggers DEC-439 layer 5 alert. ~1d integration. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-446** | Polygon intraday quotes selective fetch for slippage calibration — Pass 52 owner-approved (DEC-410 Batch 1, Hypothesis H-polygon-4). Fetch Polygon `/v3/quotes/{ticker}` NBBO bid-ask for 20-ticker × 30-day sample across liquidity deciles. Compute typical bid-ask spread by liquidity decile. Use to calibrate `slippage_bps` defaults in DEC-422 cube cell schema (`sharpe_at_5bps/10bps/20bps`) — replacing assumed values with Polygon-calibrated reality. **Use-case map (#57):** DEC-422 cost-adjusted Sharpe credibility, eventual DEC-130 slippage model (Stage 3+ but data needed now for default calibration). ~1d. **Test signal:** spread distribution by liquidity decile populates; default slippage_bps reflects empirical median per liquidity band. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-447** | Polygon reference tickers PIT consumption pattern — Pass 52 owner-approved (DEC-410 Batch 1). Implement query pattern for Polygon `/v3/reference/tickers/{ticker}` with as-of-date semantics for sector and market_cap historical lookup. Replaces yfinance .info live calls. Joint with DEC-443. **Use-case map (#57):** universe management, sector dim, cap_band dim, market_cap_pit (DEC-322 partial fix). Effort: absorbed into DEC-443. **Test signal:** PIT-correct sector and market_cap returnable for any (ticker, as_of_date) pair. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-448** | Expand FRED SERIES_MAP — Pass 52 owner-approved (DEC-410 Batch 1, Hypotheses H-fred-1, H-fred-2). Add to `backtest/data/macro.py` SERIES_MAP: `VIXCLS` (CBOE VIX from FRED, replaces yfinance ^VIX — partial BUG-19 mitigation), `DTWEXBGS` (Trade-Weighted Dollar Index, replaces yfinance DXY), `DGS2` (2-year treasury for full yield curve shape), `BAMLH0A0HYM2` or equivalent HY spread series, `ICSA` (initial jobless claims weekly leading indicator). **Use-case map (#57):** VIX cube dim feeder via authoritative source, yield curve dim refinement, weekly macro signal. ~0.5d config + prefetch update. **Test signal:** all 5 new series populate; existing 7 unchanged; VIXCLS values match within tolerance to historical ^VIX. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-449** | Validate DEC-301 ALFRED PIT mitigation produces materially different values — Pass 52 owner-approved (DEC-410 Batch 1, Hypothesis H-fred-3). Test on sample: query FRED non-vintage vs ALFRED vintage for CPIAUCSL and FEDFUNDS at multiple as_of dates from 2018-2024. Document material difference (revisions to past values). Validates that DEC-301 implementation scope was appropriate (vs over-engineered). **Use-case map (#57):** PIT loader for macro series, BUG-86 fix validation. ~0.5d. **Test signal:** non-trivial difference exists between revised and vintage values for at least one series at multiple dates; if NO difference, flag DEC-301 as potentially over-engineered for re-evaluation. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-450** | Extend `prefetch_quiver.py` to ALL paid-tier endpoints — Pass 52 owner-approved with EXPANDED SCOPE per Pass 52 turn 28 owner correction: "Quiver paid tier already active; all endpoints integrated in Stage 2." Originally framed as 8 unused endpoints (free tier limited); revised to ALL paid-tier endpoints. Add prefetch coverage for full paid-tier inventory: `/historical/senatetrading/`, `/historical/housetrading/`, `/historical/congresstrading/` (already), `/historical/insidertrading/` (already), `/historical/lobbying/`, `/historical/wikipedia/`, `/historical/reddittraders/`, `/historical/twittersentiment/`, `/historical/offexchange/`, `/historical/appdownloads/`, `/historical/13f/` (already, with DEC-396 filing_date capture), `/historical/analystratings/` (already), `/historical/govcontracts/` (already, fix per DEC-451), plus any additional paid-tier endpoints owner verifies during implementation (e.g., SEC enforcement actions, ETF holdings, options flow if covered, M&A rumors). Storage: `backtest/data/cache/quiver/{endpoint}/{TICKER}.parquet`. **Use-case map (#57):** Smart Money / Sentiment / Macro / Fundamental agents, sentiment_score cube dim feeder, regulatory tailwind dim potential, attention dim potential, institutional flow proxy, ESG/governance signals. **Resolves:** BUG-190 (MEDIUM OPEN). Effort revised: ~2-3 days → ~3-5 days for full paid-tier endpoint inventory. **Pre-condition:** owner provides current paid-tier endpoint list during implementation (audit identified gaps based on common paid endpoints; owner authoritative on actual subscription scope). **Test signal:** non-empty parquet ≥80% S&P 500 per endpoint; cube dimensions populate; full paid-tier coverage documented. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-451** | Fix BUG-284 gov_contracts date filter — Pass 52 owner-approved (DEC-410 Batch 2). Quiver `/historical/govcontracts/` returns Date field but cache schema saves only Qtr+Year, breaking date-based queries silently. Fix: re-prefetch with explicit Date column preservation OR reconstruct synthetic date from Qtr+Year midpoint with explicit caveat. **Use-case map (#57):** government contract awards as sector tailwind signal (Defense, Healthcare strategies). **Resolves:** BUG-284 (MEDIUM OPEN). ~0.5d. **Test signal:** gov_contracts date filter returns non-empty results for known recent contracts; filter does not silently drop matching rows. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-452** | Quiver premium upgrade decision — OBSOLETE per Pass 52 turn 28 owner correction. Owner already on Quiver paid tier (~$50-100/mo); upgrade decision moot. Status: OBSOLETE_BY_OWNER_CORRECTION. Original conditional logic (evaluate after DEC-450 prefetch, upgrade if free tier insufficient) does not apply since paid tier was active throughout. Sub-decision retained in audit for traceability. | OBSOLETE | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-453** | Deprecate Finnhub from project entirely — Pass 52 owner-approved (DEC-410 Batch 2, Hypothesis H-finnhub-1). Remove `scripts/prefetch_finnhub_news.py` (broken per BUG-053/181); remove `FINNHUB_API_KEY` from required config (mark optional during transition); strip Finnhub references from `backtest/agents/pipeline.py` and `backtest/data/smart_money.py`. Polygon DEC-441 fully supersedes news (DEC-440); Quiver/FRED/yfinance/Polygon cover all other Finnhub endpoints. **Resolves:** BUG-053 (HIGH WILL_RESOLVE_VIA_DEC-440 → final closure), BUG-181 (MEDIUM WILL_RESOLVE_VIA_DEC-440 → final closure). **Use-case map (#57):** architectural simplification (1 fewer API to maintain). ~0.5d cleanup. **Test signal:** Finnhub references removed from active code; bugs flipped to RESOLVED status; existing Finnhub cache parquet artifacts retained for transition period only. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-454** | Remove OpenBB from project scope — Pass 52 owner-approved (DEC-410 Batch 3, Hypothesis H-openbb-1). Update PROJECT_PLAN section 10 to remove OpenBB row. Resolves DEC-410 OpenBB consumption gap dual treatment per audit-as-source-of-truth principle (audit > PROJECT_PLAN). Polygon DEC-441 + Quiver + FRED collectively cover all OpenBB Stage 0+Stage 2 use cases at higher quality. Future Phase 1C+ screener use cases can revisit. **Use-case map (#57):** architectural simplification (1 fewer aspirational API to consider). ~0.25d documentation. **Test signal:** PROJECT_PLAN section 10 updated; OpenBB references removed from project scope documentation. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-455** | Alpha Vantage deprecation timeline — Pass 52 owner-approved (DEC-410 Batch 3, Hypothesis H-av-1). Sequence: (a) preserve existing AV cache parquet artifacts for transition period; (b) remove AV from active prefetch scripts post-Polygon news prefetch validation; (c) mark `ALPHAVANTAGE_API_KEY` optional in config (was required); (d) strip AV references from `backtest/agents/pipeline.py` and `backtest/data/smart_money.py` post-Polygon stable run. Joint with DEC-440 (already approved AV→Polygon supersession). **Use-case map (#57):** architectural simplification. ~0.5d cleanup spread across migration phases. **Test signal:** AV code paths inactive; existing cache artifacts preserved; ALPHAVANTAGE_API_KEY no longer required. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |
| **DECISION-456** | SEC EDGAR as DEC-439 differential testing reference for fundamentals PIT — Pass 52 owner-approved (DEC-410 Batch 4). Use SEC EDGAR (free, authoritative regulatory source with native filing_date) as independent reference for DEC-439 layer 5 differential testing of Polygon fundamentals. Sample: 10 tickers × 4 quarters; parse via `edgartools` Python library (or equivalent); compare against Polygon `/v3/reference/financials` for same. Catches common-mode failures per CAV-068 (would otherwise escape Polygon-only validation). Stage 0+Stage 2 IN scope as catch mechanism (NOT primary data source — too engineering-expensive). **Use-case map (#57):** DEC-439 layer 5 strengthening, fundamentals PIT correctness validation, BUG-218 CRITICAL mitigation cross-check. ~2 days. **Test signal:** EDGAR vs Polygon fundamentals for sample — divergence triggers investigation; convergence validates Polygon. | PENDING | Batch X56 — API Endpoint Utilization Audit (Pass 52) | Pass 52 | - |

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
| **BUG-053** | HIGH — Finnhub news cache: all 509 files are empty — Sentiment Agent has no news. Pass 52: WILL_RESOLVE_VIA_DEC-440 (Polygon news supersedes Finnhub free tier as canonical news source per DEC-441 subscription purchase). | HIGH | WILL_RESOLVE_VIA_DEC-440 | - |
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
| **BUG-111** | CRITICAL — No break-and-retest variants of breakout strategies (severity upgraded Pass 52 twice: MEDIUM→HIGH then HIGH→CRITICAL per owner "CRITICAL AND MOST IMPORTANT REQUIREMENT" — retest is mandatory entry trigger across DEC-355 through DEC-362 chart pattern strategies; cross-applies to all existing breakout strategies in screener.py categories Breakout (6) + Pivot Based (10) + Confluence (9) where breakout entry is used) | CRITICAL | OPEN | Pass 13 |
| **BUG-181** | MEDIUM — Finnhub news prefetch silently produces empty files. Pass 52: WILL_RESOLVE_VIA_DEC-440 (Polygon news supersedes Finnhub free tier per DEC-441). | MEDIUM | WILL_RESOLVE_VIA_DEC-440 | Pass 17 |
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
| **BUG-264** | universe.py docstring claims Wikipedia fetch but uses static CSV | LOW | RESOLVED | Pass 48 (closed Pass 52) |
| **BUG-265** | yfinance auto_adjust=True hardcoded; no raw price option | LOW | OPEN | Pass 48 |
| **BUG-266** | delay_sec 0.3 magic number undocumented | LOW | OPEN | Pass 48 |
| **BUG-267** | Test e2e takes 4.5 min for 1 passing test — too slow for smoke | LOW | OPEN | Pass 48 |
| **BUG-268** | ETF sector labels hardcoded — new ETFs default to Unknown | LOW | OPEN | Pass 48 |
| **BUG-269** | Quiver _DELAY constant unused — live API never called in backtest | LOW | OPEN | Pass 48 |
| **BUG-270** | insider_signal() column-name mismatch — 100% silent failure (n=500) | HIGH | OPEN | Pass 52 |
| **BUG-271** | get_gov_contracts() no Date column lookup — 99.4% silent failure (n=500) | HIGH | OPEN | Pass 52 |
| **BUG-272** | get_lobbying() Amount string concat — 98.8% silent failure (n=500) | HIGH | OPEN | Pass 52 |
| **BUG-273** | congressional_signal() Chamber/House column mismatch — silent crash on populated dates | HIGH | OPEN | Pass 52 |
| **BUG-274** | institutional_signal() SharesChange column missing — never fires "buy" signal | HIGH | OPEN | Pass 52 |
| **BUG-275** | bonferroni_adjusted_threshold(n=0) raises TypeError on complex round() | LOW | OPEN | Pass 52 |
| **BUG-276** | _agent_cache_key calls sorted() on list of dicts — crashes when strategies fire | HIGH | OPEN | Pass 52 |
| **BUG-277** | classify_regime() truth-value-of-DataFrame error — 100% failure on every probe | HIGH | OPEN | Pass 52 |
| **BUG-278** | yield_curve_regime() doesn't use macro_combined.parquet cache; live-fetches FRED only | MEDIUM | OPEN | Pass 52 |
| **BUG-279** | get_ohlcv() with reversed date order silently returns 0 rows; no error to caller | MEDIUM | OPEN | Pass 52 |
| **BUG-280** | days_to_next_earnings() returns None silently when yfinance live blocked; caller may misread as "no earnings concern" | LOW | OPEN | Pass 52 |
| **BUG-281** | site_generator._assign_tier duplicates engine._assign_confidence_tier — two places to keep in sync, drift-prone | MEDIUM | OPEN | Pass 52 |
| **BUG-282** | site_generator.build_entry_zone ignores `category` parameter — trend and reversal produce identical output | LOW | OPEN | Pass 52 |
| **BUG-283** | site_generator.build_position_sizing returns 0% silently for unknown tier — no error/warning on invalid input | LOW | OPEN | Pass 52 |
| **BUG-284** | prefetch_quiver DATE_FIELDS gov_contracts="Date" but cache schema has Qtr+Year only — date filter silently skipped | MEDIUM | OPEN | Pass 52 |
| **BUG-285** | `fixed_3r_2r` exit method in EXIT_STRATEGIES dict violates DEC-353 RESOLVED Pass 52 (2:1 R:R minimum) — actual ratio is 3R/2R = 1.5:1, BELOW minimum. Surfaced during DEC-067 pre-flight Pass 52 turn 7. Existing-code violation; any prior backtest results that included this exit method have been computed with a non-compliant exit. Fix per DEC-067 owner approval: modify to fixed_4r_2r (4R target / 2R stop = 2:1 R:R) OR remove from EXIT_STRATEGIES dict. | HIGH | OPEN | Pass 52 |
| **BUG-001** | `crisis_flag` used before definition → NameError crash | UNKNOWN | OPEN | - |
| **BUG-002** | `days` variable used before definition → UnboundLocalError on every trade close | UNKNOWN | OPEN | - |
| **BUG-003** | `ClosedTrade` dataclass defined twice — dead code, maintenance risk | UNKNOWN | OPEN | - |
| **BUG-004** | `avoid` direction falls into `triggered_short` bucket — inflates confidence tier | UNKNOWN | OPEN | - |
| **BUG-005** | `strategies_triggered` key mismatch — agent cache is always wrong (severity upgraded Pass 52: CRITICAL — reproducer confirms screener emits `strategies` key, pipeline reads `strategies_triggered`; cache always shows empty list, agents reason without strategy context) | CRITICAL | OPEN | - |
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