# STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md

**Authored:** 2026-05-19 (Pass 53 Day 9+ Batch 240)
**Goal:** Maximum Claude-assisted build work on Max plan credits before May 29 downgrade to Pro plan. Post-May-29 operation is `python scripts/X.py` triggers + light Claude sessions for analysis.
**Supersedes:** original "execute all phases by May 29" framing — that's compute-bound; reframe is "build all infrastructure now, run compute later."

---

## 1. Phase summary table (canonical)

### Stage 2 — Backtest validation

| Phase | Purpose | Universe | Timeframe | Strategies × Exits × Regimes | Cost (USD) | Compute | Inputs | Outputs | Gate to advance |
|---|---|---|---|---|---|---|---|---|---|
| **1A-α** *(in-flight)* | T1a sanity + cube methodology | 642 (T1a + ETFs) | 2022-05-05 → 2026-05-05 (4y) | 86 strats × ~25 exits × 4 regimes ≈ ~8,600 cells | $0 | ~24h | Polygon OHLCV cache + 86 strategies + smart_money composite + 25 exit methods (live `len(EXIT_STRATEGIES)` 2026-05-25; DEC-067 canonical + Batch 226/227 + Batches 282-285 extensions) | Per-(strategy × exit × regime) verdict matrix; rules-only Sharpe; PBO; DSR per strategy; Dashboards 2+3 | Sharpe ≥ 0.7 OOS + PBO < 0.6 + ≥1 combo passes 11 criteria |
| **1A-β** *(THE BIG ONE)* | **Exhaustive search — find winning combos** | **1937 (Master Dedup all 5 tiers)** | **2022-05-05 → 2026-05-05 (4y)** | **185 active strats × 25 exits × 4 regimes = 4,625 cube cells × 4 regimes = 18,500 per-regime cells** (186 registered `len(ALL_STRATEGIES) = 186` minus 1 disabled per Batch 372 STRATEGIES_DISABLED_MISSING_PRODUCER; `len(EXIT_STRATEGIES) = 25` 2026-05-26 Batch 372; was "~180 × ~17 = ~12,240" pre-Batch-316a, "186 × 25 = 4,650" pre-Batch-372). | **$0** | **~10.7h pool-off / ~2-3h pool-on (Batch 322 4-8× speedup, parity smoke pending)** | All 1A-α infrastructure + Batch 358 gate fixes + Wave 3 30/30 + T1.1-T1.5 wirings + Phase 1C+ strategies + T5b pairs precompute + T2 engine quality fixes + speedup levers A/C/D | **`winners.parquet`** with per-(strategy × exit × regime) priority-tiered list (P1/P2/P3 per criteria below); full-universe trade log with `combo_id` column + cube `trade_exit_detail.csv`; refreshed cube + dashboards | Pipeline integrity (no crashes) + ≥10 Priority-1 combos identified → Phase 1B-α |
| **1B-α** | Agents on Priority-1 winners (does agent overlay improve ROI?) | **Winners only** — tickers where Priority-1 combos fire | Same 4y | Only Priority-1 combos from 1A-β (typically 20-40 combos) | **~$50-150** (Haiku; $300 ceiling pre-approved) | ~37-40h compute over 2-3 nights | `winners.parquet` + 11-agent LangGraph pipeline + DEC-422 cube populator + A/B orchestrator (DEC-216) + AgentGateConfig (DEC-459) | A/B verdict per Priority-1 combo (agent-adds / agent-hurts / neutral); 5-Gate verdict; loss attribution (DEC-120); per-trade explainability (DEC-119); Dashboard 3 populated | DEC-131 gate: agent_sharpe − rules_sharpe ≥ 0.2 net Sharpe on ≥3 combos → Stage 3 |
| 1C | Strategy categories expansion (already absorbed into 1A-β roster) | Same as 1A-β | Same 4y | Implemented as part of 1A-β 185-active-roster (186 registered minus 1 Batch-372 disabled) | $0 | Same as 1A-β | Phase 1C+ strategies merged into ALL_STRATEGIES pre-1A-β launch | Identified in 1A-β winners output | Owner-defined |
| 1D | Extended-window stress test (incl COVID 2020) | Same as 1A-β | 2020-01 → 2026-05 (~6y) | Same 185 active × 25 exits | $0 | ~5-6 days at 6-batch parallel | All 1A-β infrastructure + extended OHLCV cache (already in `data_prefetch/`) | Per-combo robustness verdict across crisis regime | Optional; owner-defined |

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
| Paper portfolio engine (`backtest/paper_trading/portfolio.py`) | Track simulated positions + PnL + exit triggers via 17 exit methods (planned target; live `len(EXIT_STRATEGIES)`=25 Pass 53) | 10-25 concurrent positions | Daily | $0 | Daily picks + EOD close prices | Position log + PnL parquet + journal entry |
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
| 1 | May 20 Wed | 1A-α close-out (automated via scripts/run_t0_close_out.py) + T1.1-T1.5 wirings applied + T2 24-DEC engine quality queue + T5b precompute background. **Parallel: Phase 1C+ Wave 2 + Phase 1B agent pipeline + Stage 3 dashboard** | 102 strategies (May-20 target; live count 2026-05-25 Batch 360: **186**); Stage 3 dashboard MVP |
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
- **185 active strategies** (186 registered `len(ALL_STRATEGIES)` 2026-05-26; minus 1 disabled in STRATEGIES_DISABLED_MISSING_PRODUCER per Batch 372 — `dxy_headwind_multinational_short` foreign_rev_pct producer absent) **× 25 exit methods** (`len(EXIT_STRATEGIES)` 2026-05-26) = **4,625 potentially-fired cells** (was 4,650 pre-Batch-372).
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
- Per-cell aggregates: 4,625 rows × ~40 metrics = ~185K cells in cube_populator output (was 4,650 / ~190K pre-Batch-372).

### Phase 1A-β cube success criteria (cell-level)
- Every cell with n ≥ 30 trades gets a verdict (PASS / FAIL / INSUFFICIENT_DATA) against CLAUDE.md passing criteria.
- PASS cells go to winners.parquet → Phase 1B-α agent overlay testing.
- Per-regime cell verdicts: each cell × 7 historical regimes = 4,625 × 7 = 32,375 per-regime evaluations (was 32,550 pre-Batch-372).

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
- **INV triage prep:** [TRIAGE_PREP_2026_05_19.md](archive/2026-05-28-pre-1a-alpha-gate/docs/TRIAGE_PREP_2026_05_19.md) (archived Batch 425)
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

---

## 10. B888 — Path to Phase 1B-alpha (Council 14 synthesis, 2026-06-17 / 2026-06-18)

# Source: Council 14 verdict (5 advisors + chairman synthesis) per owner directive 2026-06-17 "Council this. Be extremely thorough" on Phase 1B-α plan + threshold recommendations + metrics integration + dashboard optimizations + R4-R5 delta + R5 fine-tuning. Inputs: PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md (B887 doc-sync state), backtest/results/metrics.py (12 function inventory), backtest/config.py:451-535 (PASSING_CRITERIA threshold stack), dashboard_phase_1a + dashboard_stage_2 + dashboard_sprint0a (catalog), Council 7 binding directive ("R5 -> agents -> papertrade. No changes."), R4 baseline OOS Sharpe 0.419 vs 0.7 gate.

**Owner directive 2026-06-17:** "Suggest what is the best and the simplest way to reach Phase 1B-α? What needs to be done? How do we identify the best unique strategy x exit combinations? What should be the thresholds...? Look at metrics.py and see all the metrics being calculated. What should be integrated into our evaluations? Take a look at the analysis dashboards. Suggest optimizations. How do we compare deltas from R4 to R5? Thinking of R5, how can we fine tune our strategy parameters to get the best value? We have already done 1 round of optimization in stage 4? What should be our target going ahead?"

**Binding constraint (Council 7):** No methodology changes. R5 -> agents -> papertrade sequence preserved. All B888 augmentations are POST-R5 analytical lenses + ablation extraction, not gate replacements.

### 10.1 The 6-Day Path (Tue -> Sun)

| Day | Action | Bottleneck | Cost |
|---|---|---|---|
| Tue (B888 day) | B660 v2 completes; Council 14 chairman verdict surfaced (B888); pre-commit Sharpe-band gate confirmed (B882 still authoritative); owner pre-approves $300 Haiku trigger condition | Owner pre-approval (15 min) | $0 |
| Tue PM -> Wed AM | G3 pyramid + G5 optimizer + #6 fire-bar matrix in sequence (~6-7h overnight; no parallelization to avoid CPU contention with B660 v2) | Compute | $0 |
| Wed | R5 launch on AWS c7a.8xlarge spot 3 instances x 5h = ~$7.80 (B884 instance-type decision) | AWS wall-clock 5-7h | $7.80 |
| Thu AM | Stage 3 winner extraction (`scripts/optimize_strategies_from_cube.py`); B882 decision-tree gate applied; B888 r5_delta_analyzer.py runs | **Owner attention (1h)** | $0 |
| Thu PM -> Sat | Phase 1B-α Haiku run on Priority-1 (deployment-optimized cells) + AGENT-CANDIDATE tag only; mid-run abort watchdog per DEC-131 lookahead | Compute (~37-40h); Haiku $50-150 | $50-150 |
| Sun | DEC-131 gate: agent_sharpe minus rules_sharpe >= 0.2 net on >=3 combos -> advance to Phase 1B full; or stop | Owner | $0 |

**Single sequential bottleneck:** Thursday AM owner sign-off on B882 Sharpe-band decision tree applied to R5 results.

### 10.2 Threshold Stack Simplification (POST-R5 ANALYTICAL LENS, not gate replacement)

**Existing 11-criteria + 5-Gate stack remains canonical** (no methodology change per Council 7). B888 adds a parallel **classification lens** for owner-facing winner identification + dashboard surfacing.

Council 14 First Principles + Outsider diagnosis: 16-knob stack has multicollinearity (Sharpe + Sortino + Calmar all measure risk-adjusted return; PF + WR + W/L are algebraically linked; DSR already corrects for multiple testing). B888 lens replaces it with 4 metrics:

| Metric | B888 lens threshold | Rationale | Existing gate (unchanged) |
|---|---|---|---|
| **PSR** (Probabilistic Sharpe Ratio) | >= 0.95 with explicit n | Captures Sharpe + sample size + skew + kurtosis in one metric per Bailey-Lopez-de-Prado 2012 | min_sharpe_overall 1.0; min_sharpe_per_regime 0.7; min_trades 100/30 |
| **Calmar** (promoted from deflator to primary) | >= **1.0** (was 0.5 deflator) | Drawdown-resilient cells = agent-stable cells per Expansionist Council 14; Phase 1B-α agents over-weight recent losses -> drawdowns kill agent confidence loops | min_calmar 0.5 (unchanged in canonical) |
| **DSR** with confidence interval | DSR > 0 with CI not arbitrary 0.95 | First Principles: DSR is the multiple-testing correction; raw threshold 0.95 + Bonferroni on top = double-counting | min_deflated_sharpe 0.95 (unchanged) |
| **Per-regime PASS** | >= **3** of 4 regimes (was 2) | Contrarian: Carver's >=2-of-4 rule was for ~20 strategies; 218 strategies = 21 combinatorial ways to win = guaranteed false positives. Scale-correction. | min_regimes_passing 2 (unchanged) |

**AUTO-FAIL screens (NEW B888 additions; metrics.py-computed but never gated):**

| Screen | Threshold | Source | Catches |
|---|---|---|---|
| **Chow break-point** | p < 0.05 + post-break Sharpe < 0.3 | Expansionist + Contrarian | Dead-strategy false positives (regime-coincidence; strategy died at 2022-06-13 rate-hike pivot, still coasting on pre-break trades) |
| **ADF stationarity** | p < 0.05 (mean-reverting equity curve) | Expansionist | Whip-saw non-compounders; LLM agents add zero value to non-compounding strategies |
| **Cost-sensitivity Sharpe** | degradation > 30% from base | Built but never gated | Strategies that die under realistic slippage/commission |

### 10.3 Best Unique Strategy x Exit Identification (Best-of-26 Collapse + Soft-Score)

**Council 14 unanimous convergence:** 39,676 cells dilutes signal; collapse to deployment-optimized form.

```
# Pseudocode for scripts/r5_winner_identifier.py (B888 NEW)
for strategy in ALL_STRATEGIES:                       # 218 strategies
    for regime in REGIMES:                            # 7 regimes
        # Best-of-26 collapse
        best_cell = argmax(soft_score(cell) for cell in cells_for(strategy, regime))
        # -> 218 x 7 = 1,526 deployment-optimized cells (vs 39,676 raw)

# Soft-score formula (Expansionist Council 14)
def soft_score(cell):
    return (0.30 * normalized(cell.sharpe)
          + 0.25 * normalized(cell.calmar)
          + 0.20 * normalized(cell.profit_factor)
          + 0.15 * normalized(cell.dsr)
          + 0.10 * (1 - cell.cost_sensitivity))

# Rank by soft-score; emit Priority tiers
P1 = top-N% by soft-score AND passes all AUTO-FAIL screens (Chow + ADF + cost-sensitivity)
P2 = below P1 threshold but per-regime PASS in >=3 of 4 regimes
P3 = below P2; excluded from Phase 1B-α
```

**Output:** `output_audit/winners_r5_b888.parquet` with columns: `[strategy, regime, exit, soft_score, sharpe, calmar, psr, dsr, chow_pvalue, adf_pvalue, cost_sensitivity, priority_tier, agent_candidate_flag, delta_vs_r4]`.

**Asymmetric value (Expansionist):** soft-score ranking surfaces cells just-below ALL-criteria-pass thresholds (e.g., passes everything except 1 metric by 1pp) -- these would die silently under current gate stack. With soft-score, they surface for owner review.

### 10.4 R4 -> R5 Delta Intelligence (FREE Ablation Study)

**Council 14 4-of-5 strongest insight:** R4 + R5 with cumulative B722/B874/B635/B886 changes = the most expensive controlled-ablation study ever assembled. Throwing it away by treating R5 as fresh verdict is throwing away the intelligence.

**B888 NEW script: `scripts/r5_delta_analyzer.py` (to be written before R5 launches).**

For each (strategy x exit x regime) cell present in both R4 and R5:

| Delta condition | Interpretation | Action |
|---|---|---|
| dSharpe >= +0.10 AND attributable to B722-B886 walk | Walk earned its keep | Promote strategy in Priority-1 |
| dSharpe <= -0.10 | Revert candidate; walk overfit | Surface for owner review; potential B889 revert |
| |dSharpe| < 0.05 despite gate changes | Cosmetic walk | Document; no action |
| FAIL-overall -> PASS-per-regime flip | Tier-3 regime-specific deployer (NEW edge discovered) | Add to P2 tier (regime-conditional deployment) |

**Aggregation method (First Principles rigor):** per-cluster Kolmogorov-Smirnov test on Sharpe distribution shift across R4 vs R5. Unit of inference = cluster x regime, not raw per-cell (39,676 cell deltas are noise).

**Visualization:** new dashboard tab "R4-R5 Delta" (see section 10.5).

### 10.5 Dashboard Consolidation (3 -> 1)

**Council 14 First Principles + Outsider:** 3 dashboards fragment by phase rather than by question.

**B888 plan: build `dashboard_stage_4_cube_explorer/` consolidating 4 tabs:**

| Tab | Content | Source |
|---|---|---|
| 1. **Cell Verdict Cube** | Filterable by strategy/exit/regime; soft-score sorted; AUTO-FAIL flags visible; Priority tier badges | r5 trade logs + winners_r5_b888.parquet |
| 2. **R4-R5 Delta** | Per-cell delta-metrics heatmaps; cluster-regime KS test summary; walk-impact attribution | r5_delta_analyzer.py output |
| 3. **Walk-Impact** | Per-batch Stage 4 walk contribution to Sharpe delta (which walks earned their keep) | Delta analyzer aggregated by batch |
| 4. **Phase 1B-α Candidate** | AGENT-CANDIDATE vs MECHANICAL-PURE tagging; agent-overlay decision support | soft-score output + manual tagging |

**Deprecation plan:**
- `dashboard_phase_1a/` -- supersede with Cell Verdict Cube tab; archive after B888+5 batches
- `dashboard_stage_2/` -- supersede with EXECUTION_QUEUE + AUDIT_INDEX integration; archive after B888+5 batches
- `dashboard_sprint0a/` -- convert to static JSON reference data (no JS UI); not user-facing

### 10.6 metrics.py Integration (Sleeping Unicorns)

**Council 14 Expansionist + Contrarian:** metrics.py computes 12 functions; PASSING_CRITERIA reads 6. The 6 unused are the highest-leverage diagnostic gates.

| metrics.py function | Current status | B888 plan |
|---|---|---|
| `_chow_test` (regime break-point) | Computed; not gated | **AUTO-FAIL screen** (B888 lens) -- catches dead-strategy regime-coincidence |
| `_adf_test` (equity curve stationarity) | Computed; not gated | **AUTO-FAIL screen** -- catches whip-saw non-compounders |
| `_cost_sensitivity_sharpe` | Computed; not gated | **AUTO-FAIL screen** -- catches slippage-killed strategies |
| `_kelly_criterion` | Computed; advisory | Surface in dashboard for position-sizing tier validation (not a gate) |
| `_event_window_breakdown` | Computed; advisory | Surface in dashboard for event-driven strategies (PEAD/FOMC/buyback) |
| `_event_conditional_win_rate` | Computed; advisory | Same as above; helps owner triage event-strategy quality |
| `_time_in_market_metrics` | Computed; advisory | Surface in dashboard for capital efficiency comparison |
| `_sortino_ratio` | Computed; gated | Keep canonical gate; demote from B888 lens (redundant with Calmar) |
| `_sharpe` / `_sharpe_daily` | Computed; gated | Keep canonical; lens uses PSR (which incorporates) |
| `_profit_factor` | Computed; gated | Keep canonical; lens uses soft-score weighting |
| `_max_drawdown` | Computed; gated | Keep canonical; lens uses Calmar (which incorporates) |
| `_deflated_sharpe` (DSR) | Computed; gated 0.95 | Keep canonical 0.95; lens uses DSR > 0 with CI |
| `_calmar` | Computed; gated 0.5 | Keep canonical 0.5; lens promotes to 1.0 primary |

**No metrics.py changes required -- just wire the 3 unused gates (Chow/ADF/cost-sensitivity) as AUTO-FAIL screens in `r5_winner_identifier.py`.**

### 10.7 Post-Stage-4 Target (Honest)

**Original Stage 2 BUILD PLAN target:** ">=10 Priority-1 combos identified -> Phase 1B-α."

**B888 corrected target (per Council 14 First Principles):** "By Sunday, produce a ranked list of <=50 deployment-optimized cells with R4-R5 delta-verified edge improvement and pass the Chow+ADF AUTO-FAIL screens."

If subset is **<30 cells** -> project's "218 strategies have edge" premise is empirically falsified. Response: fewer strategies, not more agents. Honest stop-gate.

If subset is **30-50 cells with verified delta improvement** -> Phase 1B-α launches restricted to AGENT-CANDIDATE-tagged cells only (per Expansionist per-cell triage), ~60% Haiku budget savings vs blanket P1 set.

### 10.8 Scripts to Build (B888 + Following Batches)

| Script | When | Effort | Status |
|---|---|---|---|
| `scripts/r5_delta_analyzer.py` | NOW (parallel to B660 v2) | ~2h Claude | B888 priority |
| `scripts/r5_winner_identifier.py` (soft-score + AUTO-FAIL screens) | Pre-R5 (or by Thursday AM) | ~3h Claude | B888-B889 |
| `scripts/eval_r5_sharpe_band.py` (B882 decision tree evaluator) | Pre-R5 | ~1h Claude | B889 |
| `scripts/dec131_mid_run_watchdog.py` (1B-α abort if lookahead detected) | Pre-1B-α | ~1h Claude | B890 |
| `dashboard_stage_4_cube_explorer/` build | Post-R5 | ~4-6h Claude | B891 |

**Total Claude effort:** ~11-13h across B888-B891. None block R5 launch except `r5_delta_analyzer.py` (which is built before R5 lands).

### 10.9 What Stays Vs What Changes

| Element | Status |
|---|---|
| Council 7 "R5 -> agents -> papertrade. No changes." directive | **UNCHANGED** |
| PASSING_CRITERIA 11-criteria + 5-Gate canonical | **UNCHANGED** (no methodology shift) |
| 218 active strategies; no a-priori cull (`feedback_no_a_priori_strategy_pruning`) | **UNCHANGED** |
| DEC-426 5-Gate (n>=30, p<0.05 Bonferroni, PSR>=0.95, t>=3.4, R:R>=2.0) | **UNCHANGED** |
| Phase 1B-α 11-agent pipeline + $300 Haiku budget | **UNCHANGED** |
| DEC-131 gate (agent_sharpe minus rules_sharpe >= 0.2 on >=3 combos) | **UNCHANGED** |
| **B888 lens** (4-metric + AUTO-FAIL screens applied to R5 OUTPUT) | **NEW** -- analytical only, no gate replacement |
| **R4-R5 delta analyzer** | **NEW** -- free ablation extraction |
| **Soft-score ranking + best-of-26 collapse** | **NEW** -- winner identification methodology |
| **Consolidated dashboard** | **NEW** -- 3 -> 1 over B891+ |

### 10.10 Council 14 Diagnostic (Honest Risk Surface)

**Contrarian Council 14 dissent (preserved for honesty):**
- "R4 0.419 OOS came from researcher running 800+ batches against same holdout. True Sharpe possibly below 0.419 or negative."
- "39,676 cells x ~140 walk-mutations x 800 batches ~= 4.4M researcher DoF. At this trial count, Sharpe 1.0 overall = random noise. Honest threshold ~1.8-2.2."
- "Stage 4 walks were optimization round 1 against corrupted oracle. Round 2 needs clean OOS slice (2026-Q2 forward, sealed) before R5 means anything."

**Owner's binding response (Council 7):** "R5 -> agents -> papertrade. No changes." -- overrules the methodology-shift concern. B888 honors directive while extracting maximum delta-intelligence + lens-classification value from the R5 output.

**Honest fallback if R5 OOS Sharpe < 0.5:** B882 Sharpe-band decision tree triggers STOP. Defer Phase 1B-α. Re-architect via clean post-2026 forward-test window (Contrarian's prescription becomes actionable post-failure).
