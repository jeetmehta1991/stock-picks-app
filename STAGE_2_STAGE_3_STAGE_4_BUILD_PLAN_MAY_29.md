# STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md

**Authored:** 2026-05-19 (Pass 53 Day 9+ Batch 240)
**Goal:** Maximum Claude-assisted build work on Max plan credits before May 29 downgrade to Pro plan. Post-May-29 operation is `python scripts/X.py` triggers + light Claude sessions for analysis.
**Supersedes:** original "execute all phases by May 29" framing — that's compute-bound; reframe is "build all infrastructure now, run compute later."

---

## 1. Phase summary table (canonical)

### Stage 2 — Backtest validation

| Phase | Purpose | Universe | Timeframe | Strategies | Cost (USD) | Compute time | Inputs | Outputs | Gate to advance |
|---|---|---|---|---|---|---|---|---|---|
| **1A-α** *(in-flight)* | T1a sanity + cube methodology | 642 (T1a + ETFs) | 2022-05-05 → 2026-05-05 (4y) | 86 (Layer 1 + dead-evidence-pruned) | $0 | ~24h | Polygon OHLCV cache + 86 strategies + smart_money composite | Per-(strategy × regime) verdict matrix; rules-only Sharpe; PBO; DSR per strategy; Dashboards 2+3 | Sharpe ≥ 0.7 OOS + PBO < 0.6 + ≥1 strategy passes 9 criteria |
| **1A-β** *(THE BIG ONE)* | **Exhaustive search — find winners** | **1937 (Master Dedup all 5 tiers)** | **2022-05-05 → 2026-05-05 (4y)** | **~180 (Layer 1 + T1.1-T1.5 + Phase 1C+ full roster)** | **$0** | **~5-7 days at 5-batch parallel** | All Phase 1A-α infrastructure + T1.1-T1.5 wirings + Phase 1C+ strategies + T5b pairs precompute + T2 engine quality fixes | Per-(strategy × exit-method × regime) winners list; full-universe trade log; refreshed cube + dashboards | Pipeline integrity (no crashes) + ≥10 strategies pass 9 criteria → Phase 1B-α |
| **1B-α** | Agents on winners (does agent overlay improve ROI?) | **Winners only** — tickers where winning strategy×exit combos fire | Same 4y | Only winning (strategy × exit × regime) combos from 1A-β | **~$50-150** (Haiku; $300 ceiling pre-approved) | ~37-40h compute over 2-3 nights | 1A-β winners list + 11-agent LangGraph pipeline + DEC-422 cube populator + A/B framework | A/B verdict per winner (agent-adds / agent-hurts / neutral); 5-Gate verdict; loss attribution; per-trade explainability; Dashboard 3 populated | DEC-131 gate: agent_sharpe − rules_sharpe ≥ 0.2 net Sharpe → Stage 3 |
| 1C/1D | Extended categories + extended-window stress (optional, parallel) | Same as 1A-β | Extended (2020-01 → 2026-05 incl. COVID) | Subset of winners or full | $0-200 | TBD | 1A-β winners + extended OHLCV | Stress-test robustness verdict | Owner-defined |

### Stage 3 — Paper trading (post-1B-α)

| Module | Purpose | Universe | Frequency | Cost | Inputs | Outputs |
|---|---|---|---|---|---|---|
| Daily picks generator | Top 10 candidates each market day from winning strategies | Subset where winners fire | Daily 8 AM ET | $0 | Phase 1B-α verdicts + day's market data | Email with 10 candidates + risk context |
| Paper portfolio | Track simulated positions + PnL | 10-25 concurrent positions | Daily | $0 | Daily picks + close prices | Position log + PnL report |
| Stage 3 dashboard | Live paper-trading dashboard | Same | Real-time | $0 | Paper portfolio | Web UI for performance review |

### Stage 4 — Live trading (post-Stage-3 validation)

| Module | Purpose | Universe | Frequency | Cost | Inputs | Outputs |
|---|---|---|---|---|---|---|
| Live picks + approval | Same as Stage 3 but with owner-email approval gate | Same | Daily | $0 (Anthropic API for any Claude calls) | Daily picks + market data | Owner-approval-pending email |
| Live execution | IB API order placement on owner-approved trades | Same | Daily | IB tiered commission | Approved picks | Filled trades log |
| Live monitoring | Real-time PnL + risk + circuit-breaker enforcement | Same | Real-time | $5-15/mo AWS Lightsail | Position state + market data | Real-time dashboard + alerts |

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

## 3. 10-day build plan (May 19 PM → May 29)

| Day | Date | Work | Output |
|---|---|---|---|
| 0 | May 19 PM | T0 script + T5b script + T1 drafts + INV reclassifications + TRIAGE_PREP | ✅ Already committed |
| 1 | May 20 Wed | Phase 1A-α close-out (automated) + T1.1-T1.5 wirings (16 strategies) + T2 24-DEC engine quality fixes (overnight autonomous) + T5b precompute background | 102 strategies registered; engine quality up |
| 2 | May 21 Thu | Phase 1C+ strategy implementations Wave 1: DEC-355-362 chart patterns + DEC-067 9 exit methods + DEC-368 Calendar + DEC-370 Index Rebalance | +30 strategies → 132 |
| 3 | May 22 Fri | Phase 1C+ Wave 2: DEC-345 ICT/SMC + DEC-350 multi-TF + DEC-352 13F price-level + DEC-371 + DEC-174/175 | +30-50 strategies → ~180 |
| 4 | May 23 Sat | **LAUNCH Phase 1A-β** (1937 × ~180 × 4y) — 5-batch parallel. Parallel: Phase 1B Sprint 7 infra begins (11-agent LangGraph wiring) | 1A-β running |
| 5 | May 24 Sun | 1A-β computes. Claude: AgentGateConfig + A/B orchestrator (DEC-216) + TradingAgents toolkit matrix | 1B agent pipeline ready |
| 6 | May 25 Mon | 1A-β computes. Claude: DEC-422 cube populator + DEC-426 5-Gate verdict + DEC-120 loss attribution + DEC-119 explainability + Dashboard 3 expansion | 1B-α cube ready |
| 7 | May 26 Tue | 1A-β likely completes. Run T0 close-out → winners list. Build `scripts/extract_phase_1a_beta_winners.py` | Phase 1A-β verdict; winners list |
| 8 | May 27 Wed | Phase 1B-α smoke (5 winners × 30 days, ~$3) + demo (20 winners × 1 quarter, ~$10). Stage 3 paper trading skeleton built | Smoke + demo verified |
| 9 | May 28 Thu | Phase 1B-α full launch (winners-only, ~$50-150). Stage 4 IB integration + AWS Lightsail Docker config | 1B-α running |
| 10 | May 29 Fri | Final polish + POST_MAY_29_OPERATION_GUIDE.md + final commit | Plan complete; downgrade |

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

## 7. Risks (top 5)

1. **Phase 1A-β at 180 strategies × 1937 tkrs may take 7-10 days, not 5-7.** Could push 1B-α run post-May-29.
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
