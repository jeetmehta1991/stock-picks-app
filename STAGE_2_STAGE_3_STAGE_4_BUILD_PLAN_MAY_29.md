# STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md

**Authored:** 2026-05-19 (Pass 53 Day 9+ Batch 240)
**Goal:** Maximum Claude-assisted build work on Max plan credits before May 29 downgrade to Pro plan. Post-May-29 operation is `python scripts/X.py` triggers + light Claude sessions for analysis.
**Supersedes:** original "execute all phases by May 29" framing — that's compute-bound; reframe is "build all infrastructure now, run compute later."

---

## 1. Phase summary table (canonical)

### Stage 2 — Backtest validation

| Phase | Purpose | Universe | Timeframe | Strategies × Exits × Regimes | Cost (USD) | Compute | Inputs | Outputs | Gate to advance |
|---|---|---|---|---|---|---|---|---|---|
| **1A-α** *(in-flight)* | T1a sanity + cube methodology | 642 (T1a + ETFs) | 2022-05-05 → 2026-05-05 (4y) | 86 strats × ~17 exits × 4 regimes = ~5,848 cells | $0 | ~24h | Polygon OHLCV cache + 86 strategies + smart_money composite + 17 exit methods (DEC-067 canonical + Batch 226/227 extensions) | Per-(strategy × exit × regime) verdict matrix; rules-only Sharpe; PBO; DSR per strategy; Dashboards 2+3 | Sharpe ≥ 0.7 OOS + PBO < 0.6 + ≥1 combo passes 11 criteria |
| **1A-β** *(THE BIG ONE)* | **Exhaustive search — find winning combos** | **1937 (Master Dedup all 5 tiers)** | **2022-05-05 → 2026-05-05 (4y)** | **~180 strats × ~17 exits × 4 regimes = ~12,240 cells** | **$0** | **~3-4 days at 6-batch parallel + lever C + lever D** | All 1A-α infrastructure + T1.1-T1.5 wirings + Phase 1C+ strategies + T5b pairs precompute + T2 engine quality fixes + speedup levers A/C/D | **`winners.parquet`** with per-(strategy × exit × regime) priority-tiered list (P1/P2/P3 per criteria below); full-universe trade log with `combo_id` column; refreshed cube + dashboards | Pipeline integrity (no crashes) + ≥10 Priority-1 combos identified → Phase 1B-α |
| **1B-α** | Agents on Priority-1 winners (does agent overlay improve ROI?) | **Winners only** — tickers where Priority-1 combos fire | Same 4y | Only Priority-1 combos from 1A-β (typically 20-40 combos) | **~$50-150** (Haiku; $300 ceiling pre-approved) | ~37-40h compute over 2-3 nights | `winners.parquet` + 11-agent LangGraph pipeline + DEC-422 cube populator + A/B orchestrator (DEC-216) + AgentGateConfig (DEC-459) | A/B verdict per Priority-1 combo (agent-adds / agent-hurts / neutral); 5-Gate verdict; loss attribution (DEC-120); per-trade explainability (DEC-119); Dashboard 3 populated | DEC-131 gate: agent_sharpe − rules_sharpe ≥ 0.2 net Sharpe on ≥3 combos → Stage 3 |
| 1C | Strategy categories expansion (already absorbed into 1A-β roster) | Same as 1A-β | Same 4y | Implemented as part of 1A-β ~180 roster | $0 | Same as 1A-β | Phase 1C+ strategies merged into ALL_STRATEGIES pre-1A-β launch | Identified in 1A-β winners output | Owner-defined |
| 1D | Extended-window stress test (incl COVID 2020) | Same as 1A-β | 2020-01 → 2026-05 (~6y) | Same ~180 + 17 exits | $0 | ~5-6 days at 6-batch parallel | All 1A-β infrastructure + extended OHLCV cache (already in `data_prefetch/`) | Per-combo robustness verdict across crisis regime | Optional; owner-defined |

### Winners criteria (canonical for `winners.parquet` priority tiers)

| Priority | Criteria | Phase 1B-α treatment |
|---|---|---|
| **P1 — MUST test with agents** | Passes ALL 11 overall criteria (CLAUDE.md) **AND** passes DEC-426 5-Gate (n≥30, p<0.05 Bonferroni-corrected, PSR≥0.95, t-stat≥3.4, R:R≥2.0) | Run 11-agent pipeline; A/B vs rules-only baseline |
| **P2 — could test if budget allows** | Per-regime PASS in ≥1 regime (Sharpe≥0.7, WR≥55%, PF>1.3, ≥30 trades/regime) but not all 11 overall | Test only if Priority-1 spend leaves headroom under $50-150 cap |
| **P3 — skip** | Less than per-regime PASS or fails 5-Gate | Excluded from Phase 1B-α; documented as no-edge baseline |

**The 11 criteria reference** (per [CLAUDE.md](CLAUDE.md) passing-criteria table): Win rate (1), Profit factor (2), Expected value (3), Win/Loss ratio (4), Max DD (5), Total ROI (6), Smart money lift (7), Macro correlation (8), Min trades (9), Sharpe (10), Per-regime verdict (11).

### Stage 3 — Paper trading (BUILT BY MAY 29; activates post-1B-α verdict)

| Module | Purpose | Universe | Frequency | Cost | Inputs | Outputs |
|---|---|---|---|---|---|---|
| Daily picks generator (`scripts/run_paper_morning.py`) | Top 10 candidates each market day from Priority-1 combos | Subset where combos fire | Daily 8 AM ET | $0 | `winners.parquet` (P1 combos) + day's market data + smart_money composite | Email with 10 candidates + per-pick rationale |
| Paper portfolio engine (`backtest/paper_trading/portfolio.py`) | Track simulated positions + PnL + exit triggers via 17 exit methods | 10-25 concurrent positions | Daily | $0 | Daily picks + EOD close prices | Position log + PnL parquet + journal entry |
| **Stage 3 dashboard** (`/dashboard_stage_3/`) | Live paper-trading performance dashboard | All paper positions | Real-time on refresh | $0 | Paper portfolio + journal | Web UI: performance, per-combo attribution, drawdown |
| **Public picks website** (`/picks/`) | Daily candidates publicly visible (read-only) | Same | Daily refresh | $0 | site_picks JSON | HTML on GitHub Pages |
| **Email digest** (cron) | Daily picks + EOD PnL summary | Same | Daily | $0 | Picks + portfolio | Email to jeetmehta1991@gmail.com |
| **Performance journal** (`/dashboard_stage_3/journal/`) | Day-by-day journal entries auto-generated | Same | Daily | $0 | Paper portfolio state diff | Markdown journal page (per-day) |

### Stage 4 — Live trading (BUILT BY MAY 29; activates post-Stage-3 validation)

| Module | Purpose | Universe | Frequency | Cost | Inputs | Outputs |
|---|---|---|---|---|---|---|
| Live picks + approval (`scripts/run_live_morning.py`) | Same as Stage 3 but with owner-email approval gate | Same | Daily | $0 (Anthropic API only for Claude calls) | Daily picks + market data | Owner-approval-pending email |
| Live execution (`backtest/live_trading/ib_executor.py`) | IB API order placement on owner-approved trades; bracket orders (entry + stop + target per strategy) | Same | Daily | IB tiered commission | Approved picks + IB Gateway session | Filled trades log |
| Live risk overlay (`backtest/live_trading/risk_overlay.py`) | DEC-515 Level 6 portfolio DD breaker + circuit breakers + 5%/4%/3%/1.5%/0.75% tier sizing | Same | Real-time | $0 | Position state + market data + regime | Halt signals; trade-size adjustments |
| Live monitoring (AWS Lightsail container) | Real-time PnL + risk + alerting + auto-restart | Same | Real-time | **$5-15/mo AWS Lightsail (BUILT BUT NOT ACTIVATED)** | Position state + market data | Real-time dashboard + email alerts on circuit-breaker fires |
| **Deploy + DR** (`scripts/deploy_live.sh` + `terraform/`) | One-shot AWS deploy + disaster recovery procedures | n/a | One-time setup | $5-15/mo when activated | AWS account credentials + IB account credentials | Live cluster |

---

## 2. Architecture flow

```
Phase 1A-α (in-flight) ──→ Phase 1A-β (full exhaustive)
                                  │
                                  ▼
                          Winning (strategy × exit × regime) combos identified
                                  │
                                  ▼
                          Phase 1B-α: agents ON WINNERS ONLY
                                  │
                                  ▼
                          A/B verdict per winner (agent-adds / agent-hurts / neutral)
                                  │
                                  ├─ Pass DEC-131 gate → Stage 3 (paper trade winners-with-agents)
                                  └─ Fail DEC-131 gate → Stage 3 (paper trade winners-rules-only)
                                  │
                                  ▼
                          Stage 4 — Live trade after Stage 3 validates
```

---

## 3. 10-day build plan (May 19 PM → May 29) — REVISED PARALLEL EXECUTION

**Insight:** Source-file edits are PARALLEL-SAFE while 1A-α procs run (Python imports modules at startup; on-disk edits don't affect in-memory bytecode). Only ANOTHER backtest job competes for CPU. So Phase 1C+ implementations + Phase 1B Sprint 7 + Stage 3/4 skeletons can ALL begin TODAY in parallel with 1A-α.

| Day | Date | Work (parallel-safe; no engine-running conflict) | Output |
|---|---|---|---|
| 0 | May 19 PM | T0/T5b/T1 drafts + INV reclass + TRIAGE_PREP committed earlier this session | ✅ Already committed |
| **0.5** | **May 19 evening** | **Phase 1C+ Wave 1 begins NOW: chart_patterns.py (DEC-355-362); Phase 1B Sprint 7 begins: cube_populator.py (DEC-422); Stage 3 skeleton: paper_trading/ module** | First commits in flight |
| 1 | May 20 Wed | 1A-α close-out (automated via scripts/run_t0_close_out.py) + T1.1-T1.5 wirings applied + T2 24-DEC engine quality queue + T5b precompute background. **Parallel: Phase 1C+ Wave 2 + Phase 1B agent pipeline + Stage 3 dashboard** | 102 strategies; Stage 3 dashboard MVP |
| 2 | May 21 Thu | Phase 1C+ Wave 3 (multi-TF, 13F, classification, persistence). Phase 1B AgentGateConfig + A/B orchestrator. Stage 4 IB skeleton begins. | ~150 strategies; agents wired |
| 3 | May 22 Fri | Phase 1C+ Wave 4 (ICT/SMC additions). Phase 1B Sprint 7 complete. Stage 3 website + email digest. Stage 4 risk overlay. | ~180 strategies; Stage 3 complete |
| 4 | May 23 Sat | **LAUNCH Phase 1A-β** (1937 × ~180 × ~17 exits × 4y) with 6-batch parallel + lever C + lever D. Stage 4 AWS Lightsail Docker. | 1A-β running |
| 5-7 | May 24-26 | 1A-β computes (~3-4 days). Claude: Stage 3 journal + dashboard polish + Stage 4 monitoring. Build `extract_phase_1a_beta_winners.py`. | Stage 3+4 complete; 1A-β verdict pending |
| 8 | May 27 Tue | 1A-β verdict + winners.parquet extracted. Phase 1B-α smoke ($3) + demo ($10). | Winners list; 1B framework verified |
| 9 | May 28 Wed | Phase 1B-α full launch (Priority-1 winners only, ~$50-150). | 1B-α running |
| 10 | May 29 Thu | Final polish + POST_MAY_29_OPERATION_GUIDE.md + final commit. 1B-α run continues into post-downgrade compute (Claude-credit-free). | Plan complete; downgrade |

---

## 4. Build-vs-operate matrix (what runs on which credits)

| Activity | Claude credit cost | Days available |
|---|---|---|
| **PRE-May-29 (Max plan — high credits):** |
| Writing new code, strategies, infrastructure | HIGH | 10 days remaining |
| Designing dashboards, cube populators, agent wiring | HIGH | 10 days |
| Multi-step debugging | HIGH | 10 days |
| Comprehensive audits | HIGH | 10 days |
| Test pyramid expansion | MEDIUM | 10 days |
| **POST-May-29 (Pro plan — low credits):** |
| Running pre-built scripts (`python scripts/X.py`) | ZERO | Indefinite |
| Compute time (backtests, paper trades, live execution) | ZERO | Indefinite |
| Owner reviewing dashboards | ZERO | Indefinite |
| Light analysis ("did 1B-α pass the gate?") | LOW | Several sessions/month |
| Dashboard regen via build scripts | LOW | Several sessions/month |
| Bug fix on a specific module | LOW-MEDIUM | A few sessions/quarter |

---

## 5. Post-May-29 operating mode

**Owner runs without Claude:**
```bash
# Phase 1A-β verdict extraction (if 1A-β finished post-May-29)
python scripts/run_t0_close_out.py
python scripts/extract_phase_1a_beta_winners.py

# Phase 1B-α agent run on winners
python scripts/run_phase_1b_alpha_smoke.py     # $3
python scripts/run_phase_1b_alpha_demo.py      # $10
python scripts/run_phase_1b_alpha.py           # $50-150 (winners-only)
python scripts/run_phase_1b_alpha_dashboard.py # refresh Dashboard 3

# Stage 3 paper trading (daily cron-able)
python scripts/run_paper_morning.py            # daily picks + email
python scripts/run_paper_end_of_day.py         # PnL update
python scripts/run_paper_dashboard.py          # refresh Stage 3 dashboard

# Stage 4 (when ready)
python scripts/deploy_live.sh                  # one-shot AWS Lightsail deploy
python scripts/run_live_morning.py             # live picks + owner-approval email
python scripts/run_live_end_of_day.py          # reconciliation
```

**Owner uses light Claude for (~1 session/week):**
- Phase 1A-β winner analysis (~1 session, ~$5 token cost)
- Phase 1B-α A/B verdict review (~1 session, ~$5 token cost)
- Stage 2 → Stage 3 transition support
- Specific bug fixes
- Strategy roster tuning based on paper-trading observations

---

## 6. Confirmed owner decisions (2026-05-19)

1. ✅ **Reframe approved** — build infrastructure pre-May-29, operate post-May-29
2. ✅ **Broker:** IB only
3. ✅ **Cloud:** AWS Lightsail $5/mo, BUILT BUT NOT ACTIVATED until owner triggers post-May-29
4. ✅ **Email:** jeetmehta1991@gmail.com
5. ✅ **$300 Phase 1B-α budget pre-approved** (actual likely ~$50-150 due to winners-only scope)
6. ✅ **Phase 1A-β scope: ALL strategies × ALL tickers × ALL timeframes** (1937 × ~180 × 4y; no reduction)
7. ✅ **Phase 1C+: all 11 categories** (chart patterns + 9 exits + Calendar + Index Rebalance + multi-TF + ICT/SMC + 13F + classification + persistence)
8. ✅ **A/B framework: winners-only** (no arbitrary pilot universe; A/B = winner-without-agent vs winner-with-agent)

---

## 6.4 Phase 1A-β CUBE-MODE SCOPE (owner directive 2026-05-25 Batch 357)

**Canonical Phase 1A-β scope is the full strategy × exit cube, not single-config-per-strategy.**

Per owner directive 2026-05-25: "Phase 1A beta will compulsorily analyse each strategy and exit combination. For each entry, every exit will be simulated!!!! No exceptions."

### Cube dimensions
- **186 strategies** (`len(ALL_STRATEGIES)` 2026-05-25; DEPRECATED_STRATEGIES empty per Batch 316a) **× 25 exit methods** (`len(EXIT_STRATEGIES)` 2026-05-25) = **4,650 potentially-fired cells**.
- Each cell = independent backtest verdict for `(strategy, exit_method)` pair.
- Prior runs (2026-05-24 output_phase_1a_beta_merged_local) used single-config mode → 167 cells fired naturally via runtime dispatch. Cube mode fires every (admissible-entry × every-exit) deterministically.

### Engine change required (Step 2 of owner's 4-step plan)
- `BacktestEngine._process_day` enters a candidate trade once per `(ticker, day, strategy)` admission.
- New: for each admitted entry, fan out across all 25 exit methods. Each fan-out arm is an independent simulation that:
  - Starts at the same entry_price + entry_date
  - Computes exit_date + exit_price using its assigned exit_method's rule
  - Records a separate trade_log row with `exit_method` column set
- Trade log schema gains `exit_method` column distinct from `exit_reason` (exit_reason still records WHICH circuit-breaker/regime-flip/etc. fired within the method).
- `cube_populator.py` re-aggregates the cube post-merge.

### Compute estimate
- Naive: 25× single-config compute. Single-config Phase 1A-β was ~10.5h on Hetzner CPX62 → cube mode projects ~250h naive = ~10.4d.
- Optimizations available:
  - **Pool fan-out at the exit-method axis** (independent simulations parallelizable; reuse Batch 322 multiprocessing pool)
  - **Short-circuit on dominated exits** (if exit X is strictly worse than exit Y on first N trades of a strategy, skip X — optional, defer)
  - **Stratified subsample first** (run cube on Stage D 150 tkrs × 4y first to validate; full 1937 tkrs as final pass)
- Realistic target: 24-48h on Hetzner CPX62 with pool fan-out + Stage D smoke.

### Storage estimate
- Trade log: 7,191 → ~180,000 rows (25× factor). ~50MB CSV → ~1.2GB CSV. Parquet compression: ~80MB.
- Per-cell aggregates: 4,650 rows × ~40 metrics = ~190K cells in cube_populator output.

### Phase 1A-β cube success criteria (cell-level)
- Every cell with n ≥ 30 trades gets a verdict (PASS / FAIL / INSUFFICIENT_DATA) against CLAUDE.md passing criteria.
- PASS cells go to winners.parquet → Phase 1B-α agent overlay testing.
- Per-regime cell verdicts: each cell × 7 historical regimes = 4,650 × 7 = 32,550 per-regime evaluations.

### Memory + doc references
- `project_phase_1a_beta_is_exit_cube.md` (memory) — canonical scope assertion.
- `PHASE_1A_BETA_STAGE_D_LOSER_CELL_AUDIT.md` (Batch 356) — observed cells under single-config mode; cube mode supersedes Bucket E.
- `output_audit/phase1a_beta_recat.md` — per-cell recat output (single-config; will be reproduced under cube mode).

### Deployment vs backtest distinction (preserved)
- `STRATEGY_EXIT_OVERRIDE` config in `backtest/config.py` remains for **live trading / paper trading** mode (Stage 3+): each deployed strategy picks ONE exit per cube verdict.
- Phase 1A-β **backtest** mode is cube; Stage 3+ **deployment** mode is single-config-per-strategy chosen from cube winners.

---

## 6.5 Phase 1A-β compute speedup levers (owner-approved 2026-05-19)

| Lever | Speedup | Status | Detail |
|---|---|---|---|
| **A. Increase batches 5→6** | ~20% | **APPROVED** (10-batch INFEASIBLE on 15.4 GB RAM; 6 is max safe with ~0.6 GB margin) | Will require 32 GB RAM upgrade for >6 batches |
| **B. Pre-filter dead strategies via smoke** | ~15-25% | **REJECTED** (owner: test all strategies, don't pre-filter) | n/a |
| **C. Vectorize signal-once-per-ticker-day** | ~10-15% | **APPROVED** | Audit existing `compute_all_signals` flow; ensure no per-strategy recompute |
| **D. Polars over Pandas for parquet reads** | ~5-10% | **APPROVED** | Add Polars to requirements; replace heavy Pandas read_parquet in OHLCV loader |
| **Combined A+C+D** | **~30-40%** | **5-7d → ~3-4d** | Net Phase 1A-β compute estimate |

## 7. Risks (top 5)

1. **Phase 1A-β at 180 strategies × 1937 tkrs may take 3-4 days even with levers; if levers under-deliver, 5-6 days.** Could push 1B-α run post-May-29.
   - **Mitigation:** Compute is Claude-credit-free, so post-May-29 launch is fine. Worst case: owner reviews 1A-β verdict in ~$5 Claude session post-downgrade.

2. **Phase 1C+ implementations may surface bugs in module-level signal code.**
   - **Mitigation:** Each strategy gets unit + smoke pyramid before merge. Bug surface limited per-strategy.

3. **TradingAgents prompts may need iteration on smoke output.**
   - **Mitigation:** Phase 1B-α smoke ($3) + demo ($10) gates catch this before full $50-150 commit.

4. **Stage 4 IB integration is complex; may exceed Day 9 budget.**
   - **Mitigation:** Build skeleton + Docker container + AWS terraform; defer real IB account integration to single post-downgrade Claude session.

5. **Owner unavailable for any of 4-5 gate review sessions in 10 days.**
   - **Mitigation:** Gates run autonomously where safe; explicit OWNER-AWAITING tags on commits where blocked.

---

## 8. References

- **Phase definitions:** [PROJECT_PLAN.md §3.6-3.11](PROJECT_PLAN.md)
- **Current track plan + tools:** [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) (T0-T7 tracks)
- **T1.1-T1.5 strategy drafts:** [IMPLEMENTATION_DRAFTS_T1.md](IMPLEMENTATION_DRAFTS_T1.md)
- **INV triage prep:** [TRIAGE_PREP_2026_05_19.md](TRIAGE_PREP_2026_05_19.md)
- **T0 close-out automation:** [scripts/run_t0_close_out.py](scripts/run_t0_close_out.py)
- **T5b cointegrated pairs precompute:** [scripts/precompute_cointegrated_pairs.py](scripts/precompute_cointegrated_pairs.py)
- **A/B test DECs:** DEC-131, DEC-207-216, DEC-242 (see AUDIT_INDEX.md)
- **Stage 2 → Stage 3 gate criteria:** PROJECT_PLAN.md §5.1 + TRADING_RULES_AND_INFORMATION.md §1.2

---

## 9. CHECKLIST compliance for this plan

- ✅ #45 — compliance via per-addressal turns during execution
- ✅ #67 — doc lands same-turn as related decisions
- ✅ #69 — full 13-tier pyramid mandate preserved per addressal at apply time
- ✅ #70 — TradingAgents toolkit wiring matrix called out in Day 5
- ✅ #71 — N/A (no external library fork in this plan)
- ✅ #75 — commit per addressal
- ✅ #77 — phase scope verified against PROJECT_PLAN.md, not memory
- ✅ #78 — per-addressal pyramid mandate preserved
