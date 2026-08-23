# Phase 1A-beta pre-run alignment audit

**Source** (per CHECKLIST #77 canonical-source attribution):
- Owner directive 2026-05-25 Batch 360: comprehensive alignment audit before Phase 1A-beta cube re-run.
- Code SSOT: `backtest/signals/screener.py::ALL_STRATEGIES`, `backtest/engine/exit_strategies.py::EXIT_STRATEGIES`, `backtest/config.py::DEPRECATED_STRATEGIES`.
- Trade results SSOT: `output_phase_1a_beta_merged_local/trade_log.csv` + `output_audit/trade_exit_detail_phase_1a_beta_rebuilt.csv`.
- Generator: `scripts/drift_audit_pre_phase_1a_beta.py`.

## 1. Live authoritative values (code + trade results)

| Fact | Live value | Source |
|---|---|---|
| `strategy_total` | 213 | code/trade-log |
| `deprecated_count` | 0 | code/trade-log |
| `missing_producer_count` | 0 | code/trade-log |
| `missing_producer_list` | [] | code/trade-log |
| `strategy_active` | 213 | code/trade-log |
| `exit_method_total` | 26 | code/trade-log |
| `cube_cells_active` | 5538 | code/trade-log |
| `strategy_exit_override_count` | 41 | code/trade-log |
| `agent_count_dec_057` | 11 | code/trade-log |
| `regime_count` | 4 | code/trade-log |
| `phase_1a_beta_actual_wall_hours` | 10.5 | code/trade-log |
| `phase_1a_beta_pool_speedup_target` | 4-8x | code/trade-log |
| `phase_1a_beta_aws_instance_type` | c7a.4xlarge | code/trade-log |
| `phase_1a_beta_aws_parallel_instances` | 5 | code/trade-log |
| `phase_1a_beta_aws_pool_workers_per_instance` | 12 | code/trade-log |
| `phase_1a_beta_aws_per_instance_compute_hours` | 3.0 | code/trade-log |
| `phase_1a_beta_actual_wall_hours_note` | 10.5h = Hetzner single-machine baseline 2026-05-24 (run_phase1a --phase 1a-beta full T1a x 4yr without multiprocessing pool). Distinct from AWS R4 run 2026-05-31 (output_batch395_final/) which was 5 c7a.4xlarge spot instances x ~3h each = ~3h wall-clock (parallel) at ~$7.80 cost per B884 instance-type decision. For R5 planning use AWS keys not actual_wall_hours. | code/trade-log |
| `tests_collected` | 5996 | code/trade-log |

## 2. Drift summary by document

Drifts split: ACTIVE_CLAIM (forward-looking doc citing stale count) vs HISTORICAL_NARRATIVE (audit/bug doc describing past drift, context-only).

| Doc | Drift hits | Classification |
|---|---:|---|
| `AUDIT.md` | 113 | HISTORICAL_NARRATIVE |
| `AUDIT_INDEX.md` | 7 | HISTORICAL_NARRATIVE |
| `BUG_REGISTER.md` | 4 | HISTORICAL_NARRATIVE |
| `CANONICAL_FACTS.md` | 7 | ACTIVE_CLAIM |
| `DETAILED_PROJECT_PLAN.md` | 3 | ACTIVE_CLAIM |
| `LEARNINGS.md` | 8 | HISTORICAL_NARRATIVE |
| `PROJECT_PLAN_ARCHIVE.md` | 17 | HISTORICAL_NARRATIVE |
| `TRADING_RULES_AND_INFORMATION.md` | 1 | ACTIVE_CLAIM |

**Total drift hits**: 160
**Active drifts (need fix)**: 11
**Historical drifts (context-only)**: 149
**Docs scanned**: 31
**Docs missing from filesystem**: 4: ['PHASE_1A_BETA_QUIET_STRATEGY_FORENSIC.md', 'PHASE_1A_BETA_STAGE_D_LOSER_CELL_AUDIT.md', 'PHASE_1A_BETA_SURVIVOR_ROSTER.md', 'STRATEGY_ROSTER_FULL.md']

## 3. ACTIVE drift detail (forward-looking docs needing fix)

### CANONICAL_FACTS.md

| Line | Key | Stated | Live | Snippet |
|---:|---|---:|---:|---|
| 55 | `agent_count` | 6 | 11 | `Five compounding factors drove the 11-vs-6 agent drift (and several other latent drifts):` |
| 56 | `strategy_count` | 60 | 213 | `1. No single source of truth per quantitative fact — every doc independently states "6 agents", "60 strategies", etc.` |
| 56 | `agent_count` | 6 | 11 | `1. No single source of truth per quantitative fact — every doc independently states "6 agents", "60 strategies", etc.` |
| 85 | `agent_count` | 6 | 11 | `**Definition:** "Agent" in this project means a discrete LangGraph node in TradingAgents v0.2.4 that issues one or more ` |
| 117 | `agent_count` | 6 | 11 | `**Acceptable phrasing variants:** "11 active agents", "11 active LLM nodes", "12 total LLM nodes per propagate() (11 act` |
| 177 | `strategy_count` | 60 | 213 | `**Acceptable phrasing variants (B1035 2026-06-27 updated per Council 129 Option-6 owner-approved naked_poc + m_and_a re-` |
| 177 | `strategy_count` | 72 | 213 | `**Acceptable phrasing variants (B1035 2026-06-27 updated per Council 129 Option-6 owner-approved naked_poc + m_and_a re-` |

### DETAILED_PROJECT_PLAN.md

| Line | Key | Stated | Live | Snippet |
|---:|---|---:|---:|---|
| 95 | `agent_count` | 6 | 11 | `- §2.6 Agent overlay architecture (TradingAgents Pattern 2)` |
| 693 | `agent_count` | 6 | 11 | `## §2.6 Agent overlay architecture (TradingAgents Pattern 2)` |
| 697 | `agent_count` | 12 | 11 | `**12 agent roles per `propagate(ticker, as_of_date)` call (11 active + Reflection; live agent_count=11 per DEC-057):**` |

### PROJECT_PLAN_ARCHIVE.md

| Line | Key | Stated | Live | Snippet |
|---:|---|---:|---:|---|
| 82 | `strategy_count` | 60 | 213 | `**Phase 1A (Complete):** We ran all 60 strategies on a small universe of 67 instruments to make sure the pipeline works ` |
| 90 | `strategy_count` | 60 | 213 | `#### What the 60 Strategies Are` |
| 519 | `strategy_count` | 60 | 213 | `Every one of the 60 strategies in Phase 1B evaluates a single stock in isolation. The only market-level input currently ` |
| 531 | `strategy_count` | 60 | 213 | `**What's missing today:** All 60 strategies apply identically regardless of whether a stock's sector ETF is in an uptren` |
| 663 | `strategy_count` | 60 | 213 | `**Why this matters:** Every one of the current 60 strategies can fire during any regime. None of them explicitly time re` |
| 984 | `strategy_count` | 60 | 213 | `3. PROJECT_PLAN strategy count corrected from "60 strategies" to actual count (BUG-66) — auto-generated from `ALL_STRATE` |
| 1048 | `agent_count` | 6 | 11 | `**Cost estimate:** ~$0.50 (≈100 candidate days × 6 agents × ~$0.001 per call)` |
| 1094 | `agent_count` | 6 | 11 | `- ~1000 trading days × 5 tickers × 6 agents × $0.0001/call = ~$3` |
| 1330 | `agent_count` | 6 | 11 | `- ~1000 days × 5 tickers × 6 agents × $0.001/Sonnet call = ~$30` |
| 1474 | `strategy_count` | 60 | 213 | `Determine which of 60 strategies, across which market regimes, using which exit method, produce statistically valid trad` |
| 1522 | `strategy_count` | 60 | 213 | `\| 9 \| Minimum trades \| ≥ 500 \| Statistical validity across 60 strategies \|` |
| 1599 | `strategy_count` | 60 | 213 | `## 5. Strategy Universe — 60 Strategies, 7 Categories` |
| 1611 | `strategy_count` | 60 | 213 | `**Short strategy gap:** Only 5 of 60 strategies are short. In bull markets these rarely fire. Phase 1B will validate whi` |
| 1623 | `exit_method_count` | 12 | 26 | `**12 exit methods tested simultaneously** via composite score (40% ROI + 30% profit factor + 30% lowest drawdown):` |
| 1844 | `agent_count` | 6 | 11 | `**Phase 1B cost calculation:** 509 instruments × ~8 candidates/day average × 782 days × $0.00035/Haiku call × 6 agents =` |
| 1977 | `strategy_count` | 60 | 213 | `\| `backtest_results.csv` \| All 60 strategies ranked by all 10 metrics with confidence intervals \|` |
| 2019 | `strategy_count` | 60 | 213 | `## 18. All 60 Strategies — Plain English` |

### TRADING_RULES_AND_INFORMATION.md

| Line | Key | Stated | Live | Snippet |
|---:|---|---:|---:|---|
| 2574 | `agent_count` | 7 | 11 | `### 18.7 Agent Value-Add Gate (per DEC-131 — Two-Gate Refinement)` |

## 4. HISTORICAL_NARRATIVE drifts (context-only, no action needed)

- `AUDIT.md`: 113 hits (audit/bug doc historical prose)
- `AUDIT_INDEX.md`: 7 hits (audit/bug doc historical prose)
- `BUG_REGISTER.md`: 4 hits (audit/bug doc historical prose)
- `LEARNINGS.md`: 8 hits (audit/bug doc historical prose)
- `PROJECT_PLAN_ARCHIVE.md`: 17 hits (audit/bug doc historical prose)

## 5. False positives (regex hit but not actually drift)

Lines explicitly whitelisted as canonical-source-of-truth listings
(e.g., CANONICAL_FACTS Acceptable-phrasing-variants section) or
correct-but-regex-matched statements (CLAUDE.md '11 active agents').

**False positive count**: 1

- `CHECKLIST.md`: 1 false-positive hits

## 6. Fix priority order (forward-looking docs only)

**HIGH** (directly informs Phase 1A-beta cube re-run scope):


**MEDIUM** (project-plan reference docs; impact next-batch planning):

- `DETAILED_PROJECT_PLAN.md`: 3 drifts
- `TRADING_RULES_AND_INFORMATION.md`: 1 drifts
- `CANONICAL_FACTS.md`: 7 drifts

**LOW** (specialized / less-frequently-read docs):

- `PROJECT_PLAN_ARCHIVE.md`: 17 drifts
