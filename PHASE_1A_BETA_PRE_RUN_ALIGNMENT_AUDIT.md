# Phase 1A-beta pre-run alignment audit

**Source** (per CHECKLIST #77 canonical-source attribution):
- Owner directive 2026-05-25 Batch 360: comprehensive alignment audit before Phase 1A-beta cube re-run.
- Code SSOT: `backtest/signals/screener.py::ALL_STRATEGIES`, `backtest/engine/exit_strategies.py::EXIT_STRATEGIES`, `backtest/config.py::DEPRECATED_STRATEGIES`.
- Trade results SSOT: `output_phase_1a_beta_merged_local/trade_log.csv` + `output_audit/trade_exit_detail_phase_1a_beta_rebuilt.csv`.
- Generator: `scripts/drift_audit_pre_phase_1a_beta.py`.

## 1. Live authoritative values (code + trade results)

| Fact | Live value | Source |
|---|---|---|
| `strategy_total` | 186 | code/trade-log |
| `deprecated_count` | 0 | code/trade-log |
| `strategy_active` | 186 | code/trade-log |
| `exit_method_total` | 25 | code/trade-log |
| `strategy_exit_override_count` | 11 | code/trade-log |
| `agent_count_dec_057` | 11 | code/trade-log |
| `regime_count` | 4 | code/trade-log |
| `phase_1a_beta_actual_wall_hours` | 10.5 | code/trade-log |
| `phase_1a_beta_pool_speedup_target` | 4-8x | code/trade-log |
| `trade_log_trades` | 7191 | code/trade-log |
| `trade_log_strategies_fired` | 66 | code/trade-log |
| `trade_log_exit_reasons` | 17 | code/trade-log |
| `trade_log_tickers` | 1380 | code/trade-log |
| `trade_log_regimes_fired` | {'bull': np.int64(3810), 'bear': np.int64(2910), 'neutral': np.int64(471)} | code/trade-log |
| `trade_log_sum_pp` | -11387.15 | code/trade-log |
| `trade_log_wr_pct` | 29.87 | code/trade-log |
| `cube_rows` | 178875 | code/trade-log |
| `cube_strategies_fired` | 49 | code/trade-log |
| `cube_exit_methods` | 25 | code/trade-log |
| `cube_cells` | 1225 | code/trade-log |
| `tests_collected` | 2536 | code/trade-log |

## 2. Drift summary by document

Drifts split: ACTIVE_CLAIM (forward-looking doc citing stale count) vs HISTORICAL_NARRATIVE (audit/bug doc describing past drift, context-only).

| Doc | Drift hits | Classification |
|---|---:|---|
| `API_AUDIT.md` | 1 | ACTIVE_CLAIM |
| `AUDIT.md` | 113 | HISTORICAL_NARRATIVE |
| `AUDIT_INDEX.md` | 7 | HISTORICAL_NARRATIVE |
| `AUDIT_TRIAGE.md` | 1 | HISTORICAL_NARRATIVE |
| `BUG_REGISTER.md` | 4 | HISTORICAL_NARRATIVE |
| `BUILD_PLAN_PROGRESS.md` | 1 | ACTIVE_CLAIM |
| `DETAILED_PROJECT_PLAN.md` | 16 | ACTIVE_CLAIM |
| `EXPLANATION.md` | 1 | ACTIVE_CLAIM |
| `LEARNINGS.md` | 5 | HISTORICAL_NARRATIVE |
| `PROJECT_PLAN.md` | 2 | ACTIVE_CLAIM |
| `PROJECT_PLAN_ARCHIVE.md` | 17 | HISTORICAL_NARRATIVE |
| `STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md` | 1 | ACTIVE_CLAIM |
| `STRATEGY_REGISTER.md` | 2 | ACTIVE_CLAIM |
| `STRATEGY_ROSTER_FULL.md` | 6 | ACTIVE_CLAIM |
| `TRADINGAGENTS_DATA_AUDIT.md` | 1 | ACTIVE_CLAIM |
| `TRADING_RULES_AND_INFORMATION.md` | 8 | ACTIVE_CLAIM |

**Total drift hits**: 186
**Active drifts (need fix)**: 39
**Historical drifts (context-only)**: 147
**Docs scanned**: 53
**Docs missing from filesystem**: 0: []

## 3. ACTIVE drift detail (forward-looking docs needing fix)

### API_AUDIT.md

| Line | Key | Stated | Live | Snippet |
|---:|---|---:|---:|---|
| 175 | `strategy_count` | 60 | 186 | `\| OHLCV daily history \| ALL 60 strategies (foundation) \| ALL 17 cube dims \| BUG-19, BUG-46, BUG-62, BUG-109, BUG-265` |

### BUILD_PLAN_PROGRESS.md

| Line | Key | Stated | Live | Snippet |
|---:|---|---:|---:|---|
| 30 | `strategy_count` | 102 | 186 | `### Day 1 (May 20): 102 strategies + T1.1-T1.5 wirings + T2 24-DEC queue + T5b precompute + Stage 3 dashboard MVP` |

### DETAILED_PROJECT_PLAN.md

| Line | Key | Stated | Live | Snippet |
|---:|---|---:|---:|---|
| 51 | `agent_count` | 6 | 11 | `- §2.6 Agent overlay architecture (TradingAgents Pattern 2)` |
| 449 | `strategy_count` | 199 | 186 | `**Why 5 primary + 12 drilldown:** Original cube design (TRADING_RULES §21.1) had 17+ dimensions. Adversarial Pass 4 (GAP` |
| 559 | `strategy_count` | 118 | 186 | `**Total strategy roster:** ~108-118 strategy classes when Layer 1+2+3+4 fully implemented. Aligns with STRATEGY_REGISTER` |
| 571 | `exit_method_count` | 17 | 25 | `**Canonical source:** `TRADING_RULES_AND_INFORMATION.md` §8 — full enumeration of the 17 exit methods, parameter spec pe` |
| 574 | `exit_method_count` | 17 | 25 | `- DEC-067 — 17 exit methods canonical list (RESOLVED-DECIDED, Pass 39)` |
| 649 | `agent_count` | 6 | 11 | `## §2.6 Agent overlay architecture (TradingAgents Pattern 2)` |
| 653 | `agent_count` | 12 | 11 | `**12 agent roles per `propagate(ticker, as_of_date)` call (11 active + Reflection):**` |
| 2440 | `exit_method_count` | 17 | 25 | `12. **`volume_climax` exit method missing (DEC-327)** — DEC-067 lists 17 exit methods; volume_climax variant had no impl` |
| 2444 | `exit_method_count` | 17 | 25 | `14. **`rsi_extreme` exit method missing (DEC-340)** — DEC-067 lists 17 exit methods; rsi_extreme variant had no implemen` |
| 2635 | `exit_method_count` | 17 | 25 | `\| 067 \| 17 exit methods canonical list \| RESOLVED-DECIDED \|` |
| 3622 | `strategy_count` | 199 | 186 | `- 1015 tickers × 199 strategies (Pass 53 R7-02 fix) × ~100 trades each = potential memory pressure (recompute Sprint 9 d` |
| 4760 | `exit_method_count` | 9 | 25 | `**9 Exit Method Variants (DEC-432/433, ~6-8d — partially in Sprint 2 Phase 0.C; remaining here):**` |
| 4783 | `strategy_count` | 60 | 186 | `The verdict cube is only as good as the strategy roster that populates it. With only Layer 1 baseline (60 strategies), t` |
| 4789 | `exit_method_count` | 9 | 25 | `- **9 exit method variants** give strategies more flexibility; without them, all strategies funnel through ~6 exits, red` |
| 4935 | `exit_method_count` | 17 | 25 | `\| 067 \| 17 exit methods canonical \| RESOLVED-DECIDED \|` |
| 4995 | `exit_method_count` | 9 | 25 | `- DEC-432/433 Pass ~48 — 9 exit method variants` |

### EXPLANATION.md

| Line | Key | Stated | Live | Snippet |
|---:|---|---:|---:|---|
| 53 | `strategy_count` | 119 | 186 | `(Pass 53 update: ~119 strategy classes total per STRATEGY_REGISTER.md across Layers 1-4. Phase 1A active count: ~117 of ` |

### PROJECT_PLAN.md

| Line | Key | Stated | Live | Snippet |
|---:|---|---:|---:|---|
| 232 | `exit_method_count` | 9 | 25 | `**Scope:** Strategy roster additions: chart pattern strategies (DEC-355-362) + DEC-067 9 exit methods + DEC-075 AEP + DE` |
| 388 | `strategy_count` | 60 | 186 | `\| Layer 1 \| Baseline roster (60 strategy classes per archived PROJECT_PLAN section 6) \| 60 \|` |

### PROJECT_PLAN_ARCHIVE.md

| Line | Key | Stated | Live | Snippet |
|---:|---|---:|---:|---|
| 82 | `strategy_count` | 60 | 186 | `**Phase 1A (Complete):** We ran all 60 strategies on a small universe of 67 instruments to make sure the pipeline works ` |
| 90 | `strategy_count` | 60 | 186 | `#### What the 60 Strategies Are` |
| 519 | `strategy_count` | 60 | 186 | `Every one of the 60 strategies in Phase 1B evaluates a single stock in isolation. The only market-level input currently ` |
| 531 | `strategy_count` | 60 | 186 | `**What's missing today:** All 60 strategies apply identically regardless of whether a stock's sector ETF is in an uptren` |
| 663 | `strategy_count` | 60 | 186 | `**Why this matters:** Every one of the current 60 strategies can fire during any regime. None of them explicitly time re` |
| 984 | `strategy_count` | 60 | 186 | `3. PROJECT_PLAN strategy count corrected from "60 strategies" to actual count (BUG-66) — auto-generated from `ALL_STRATE` |
| 1048 | `agent_count` | 6 | 11 | `**Cost estimate:** ~$0.50 (≈100 candidate days × 6 agents × ~$0.001 per call)` |
| 1094 | `agent_count` | 6 | 11 | `- ~1000 trading days × 5 tickers × 6 agents × $0.0001/call = ~$3` |
| 1330 | `agent_count` | 6 | 11 | `- ~1000 days × 5 tickers × 6 agents × $0.001/Sonnet call = ~$30` |
| 1474 | `strategy_count` | 60 | 186 | `Determine which of 60 strategies, across which market regimes, using which exit method, produce statistically valid trad` |
| 1522 | `strategy_count` | 60 | 186 | `\| 9 \| Minimum trades \| ≥ 500 \| Statistical validity across 60 strategies \|` |
| 1599 | `strategy_count` | 60 | 186 | `## 5. Strategy Universe — 60 Strategies, 7 Categories` |
| 1611 | `strategy_count` | 60 | 186 | `**Short strategy gap:** Only 5 of 60 strategies are short. In bull markets these rarely fire. Phase 1B will validate whi` |
| 1623 | `exit_method_count` | 12 | 25 | `**12 exit methods tested simultaneously** via composite score (40% ROI + 30% profit factor + 30% lowest drawdown):` |
| 1844 | `agent_count` | 6 | 11 | `**Phase 1B cost calculation:** 509 instruments × ~8 candidates/day average × 782 days × $0.00035/Haiku call × 6 agents =` |
| 1977 | `strategy_count` | 60 | 186 | `\| `backtest_results.csv` \| All 60 strategies ranked by all 10 metrics with confidence intervals \|` |
| 2019 | `strategy_count` | 60 | 186 | `## 18. All 60 Strategies — Plain English` |

### STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md

| Line | Key | Stated | Live | Snippet |
|---:|---|---:|---:|---|
| 36 | `exit_method_count` | 17 | 25 | `\| Paper portfolio engine (`backtest/paper_trading/portfolio.py`) \| Track simulated positions + PnL + exit triggers via` |

### STRATEGY_REGISTER.md

| Line | Key | Stated | Live | Snippet |
|---:|---|---:|---:|---|
| 22 | `strategy_count` | 60 | 186 | `## Layer 1 — Baseline Roster (60 strategy classes per PROJECT_PLAN section 6)` |
| 226 | `strategy_count` | 60 | 186 | `**Smart money clarification:** Smart money signals (DEC-124 cross-source confluence; DEC-332 weights; DEC-450 Quiver pai` |

### STRATEGY_ROSTER_FULL.md

| Line | Key | Stated | Live | Snippet |
|---:|---|---:|---:|---|
| 43 | `strategy_count` | 72 | 186 | `## Layer 1 — Baseline roster (✅ IMPLEMENTED; 72 strategies in code at Layer 1 scope)` |
| 622 | `strategy_count` | 203 | 186 | `\| With Layer 4 PENDING (when promoted) \| \| **203 strategy classes** \|` |
| 623 | `strategy_count` | 213 | 186 | `\| With Layer 2D estimate (5-15 mid: 10) \| \| **~213 strategy classes** \|` |
| 645 | `strategy_count` | 199 | 186 | `**Trigger:** External AI 2026-05-06 review identified that ~40-60 of our ~199 strategies are highly correlated (3 RSI va` |
| 650 | `strategy_count` | 199 | 186 | `- `correlation_matrix_<as_of>.parquet` — pairwise return correlations across all 199 strategies on 1y in-sample` |
| 660 | `strategy_count` | 199 | 186 | `**Trigger:** External AI 2026-05-06 review identified that with ~199 strategies × parameter variants × 4 OOS folds (DEC-` |

### TRADINGAGENTS_DATA_AUDIT.md

| Line | Key | Stated | Live | Snippet |
|---:|---|---:|---:|---|
| 1025 | `agent_count` | 6 | 11 | `Note: prior listing of "6 agents (Risk, Fundamental, Sentiment, Technical, Bull/Bear, Decision)" reflected pre-Pattern-2` |

### TRADING_RULES_AND_INFORMATION.md

| Line | Key | Stated | Live | Snippet |
|---:|---|---:|---:|---|
| 341 | `strategy_count` | 119 | 186 | `- [ ] Total strategy roster ~109-119 strategies operational` |
| 671 | `strategy_count` | 199 | 186 | `**Resolution of double-counting concern (Pass 53 adversarial review):** Gate 4 (t-stat ≥ 3.4) and Gate 2 (Bonferroni p <` |
| 1213 | `strategy_count` | 199 | 186 | `**Affected strategies:** All Layer 1-6 strategies EXCEPT explicitly earnings-tolerant: ~190 of 199 strategy classes affe` |
| 1240 | `strategy_count` | 199 | 186 | `**Trigger:** DEC-067 method 9 lists "Signal-reversal exit" but doesn't define which signal reverses. With 199 strategies` |
| 2530 | `agent_count` | 7 | 11 | `### 18.7 Agent Value-Add Gate (per DEC-131 — Two-Gate Refinement)` |
| 2939 | `strategy_count` | 199 | 186 | `1. Strategy roster (Layer 1.I + Layer 6 expansion to 199 strategies)` |
| 2941 | `exit_method_count` | 17 | 25 | `3. Exit-risk methodology (DEC-517-538 + 17 exit methods)` |
| 3007 | `strategy_count` | 199 | 186 | `1. Sprint 1A-α — Rules-only baseline cube (no agents) — `--no-agents` flag, 4 OOS folds, full universe, all 199 strategi` |

## 4. HISTORICAL_NARRATIVE drifts (context-only, no action needed)

- `AUDIT.md`: 113 hits (audit/bug doc historical prose)
- `AUDIT_INDEX.md`: 7 hits (audit/bug doc historical prose)
- `AUDIT_TRIAGE.md`: 1 hits (audit/bug doc historical prose)
- `BUG_REGISTER.md`: 4 hits (audit/bug doc historical prose)
- `LEARNINGS.md`: 5 hits (audit/bug doc historical prose)
- `PROJECT_PLAN_ARCHIVE.md`: 17 hits (audit/bug doc historical prose)

## 5. False positives (regex hit but not actually drift)

Lines explicitly whitelisted as canonical-source-of-truth listings
(e.g., CANONICAL_FACTS Acceptable-phrasing-variants section) or
correct-but-regex-matched statements (CLAUDE.md '11 active agents').

**False positive count**: 8

- `CANONICAL_FACTS.md`: 7 false-positive hits
- `CHECKLIST.md`: 1 false-positive hits

## 6. Fix priority order (forward-looking docs only)

**HIGH** (directly informs Phase 1A-beta cube re-run scope):

- `BUILD_PLAN_PROGRESS.md`: 1 drifts
- `STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md`: 1 drifts
- `STRATEGY_REGISTER.md`: 2 drifts
- `STRATEGY_ROSTER_FULL.md`: 6 drifts
- `TRADINGAGENTS_DATA_AUDIT.md`: 1 drifts

**MEDIUM** (project-plan reference docs; impact next-batch planning):

- `DETAILED_PROJECT_PLAN.md`: 16 drifts
- `PROJECT_PLAN.md`: 2 drifts
- `TRADING_RULES_AND_INFORMATION.md`: 8 drifts
- `EXPLANATION.md`: 1 drifts

**LOW** (specialized / less-frequently-read docs):

- `API_AUDIT.md`: 1 drifts
- `PROJECT_PLAN_ARCHIVE.md`: 17 drifts
