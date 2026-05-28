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
| `missing_producer_count` | 1 | code/trade-log |
| `missing_producer_list` | ['dxy_headwind_multinational_short'] | code/trade-log |
| `strategy_active` | 185 | code/trade-log |
| `exit_method_total` | 25 | code/trade-log |
| `cube_cells_active` | 4625 | code/trade-log |
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
| `tests_collected` | 2587 | code/trade-log |

## 2. Drift summary by document

Drifts split: ACTIVE_CLAIM (forward-looking doc citing stale count) vs HISTORICAL_NARRATIVE (audit/bug doc describing past drift, context-only).

| Doc | Drift hits | Classification |
|---|---:|---|
| `AUDIT.md` | 113 | HISTORICAL_NARRATIVE |
| `AUDIT_INDEX.md` | 7 | HISTORICAL_NARRATIVE |
| `AUDIT_TRIAGE.md` | 1 | HISTORICAL_NARRATIVE |
| `BUG_REGISTER.md` | 4 | HISTORICAL_NARRATIVE |
| `LEARNINGS.md` | 5 | HISTORICAL_NARRATIVE |
| `PROJECT_PLAN_ARCHIVE.md` | 17 | HISTORICAL_NARRATIVE |

**Total drift hits**: 147
**Active drifts (need fix)**: 0
**Historical drifts (context-only)**: 147
**Docs scanned**: 53
**Docs missing from filesystem**: 0: []

## 3. ACTIVE drift detail (forward-looking docs needing fix)

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

**False positive count**: 12

- `CANONICAL_FACTS.md`: 7 false-positive hits
- `CHECKLIST.md`: 1 false-positive hits
- `DETAILED_PROJECT_PLAN.md`: 3 false-positive hits
- `TRADING_RULES_AND_INFORMATION.md`: 1 false-positive hits

## 6. Fix priority order (forward-looking docs only)

**HIGH** (directly informs Phase 1A-beta cube re-run scope):


**MEDIUM** (project-plan reference docs; impact next-batch planning):


**LOW** (specialized / less-frequently-read docs):

- `PROJECT_PLAN_ARCHIVE.md`: 17 drifts
