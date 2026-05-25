# BUILD_PLAN_PROGRESS.md

**Purpose:** Live tracker of `STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md` commitments vs reality. Created 2026-05-24 (Batch 311) per owner directive to prevent further drift between plan and execution.

**Rule:** Every batch that closes a gap below MUST update this file in the same commit. Items move from `[MISSING]` -> `[PARTIAL]` -> `[DONE]` with evidence (file path / commit hash). No silent re-prioritization without updating this tracker.

**Source canonical:** STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md (build plan from Pass 53 Day 9+ 2026-05-19, 10-day window May 19 PM -> May 29).

---

## Status legend
- `[DONE]` — committed, tested, present in main
- `[PARTIAL]` — some commits landed but spec incomplete
- `[MISSING]` — nothing committed
- `[DEFERRED]` — explicitly skipped per owner / reality re-prioritization
- `[BLOCKED]` — dependency not yet ready

---

## Day-by-day status

### Day 0.5 (May 19 evening): Phase 1C+ Wave 1 + Sprint 7 start

| Commitment | Status | Evidence |
|---|---|---|
| chart_patterns.py (DEC-355-362) | [DONE] | `backtest/signals/chart_patterns.py` |
| cube_populator.py (DEC-422) | [DONE] | `backtest/results/cube_populator.py` (275 lines, 6 functions) |
| paper_trading/ skeleton | [DONE] | `dashboard_stage_3/` covers paper trading; module renamed in `backtest/live_trading/` for stage 4 |

### Day 1 (May 20): 102 strategies + T1.1-T1.5 wirings + T2 24-DEC queue + T5b precompute + Stage 3 dashboard MVP

| Commitment | Status | Evidence / Gap |
|---|---|---|
| 1A-α close-out | [DONE] | `scripts/run_t0_close_out.py` |
| 102 strategies registered | [DONE] | `ALL_STRATEGIES` has 148 by today; 125 active post-DEC-218 |
| **T1.1 pairs_trading wiring (Batch 240)** | **[PARTIAL]** | Strategies `pairs_mean_reversion_long/short` REGISTERED in ALL_STRATEGIES but fired 0 trades in Phase 1A-β. T5b precompute output MISSING. Drafted at `IMPLEMENTATION_DRAFTS_T1.md` T1.1 section but no `Batch 240` markers in screener.py. |
| **T1.2 news_sentiment wiring (Batch 241)** | **[PARTIAL]** | news_sentiment_score column IS in trade_log (engine consumes it). But strategies `news_sentiment_long`, `news_sentiment_shift_long` fired 0 trades. Drafted at T1.2 but production-wired with different naming OR strategy-side gate too restrictive. |
| **T1.3 calendar_effects wiring (Batch 242)** | **[PARTIAL]** | `is_totm_window`, `is_january`, `is_pre_holiday` etc. ARE in signals (visible in trade_log signals_at_entry). But `totm_long`, `pre_holiday_long`, `halloween_seasonal_long`, `january_effect_small_cap_long` fired 0 trades. Batch 293 tightened regime affinity — may have over-restricted. |
| **T1.4 cross_asset wiring (Batch 243)** | **[PARTIAL]** | `bond_equity_ratio`, `gold_silver_ratio` ARE in signals. But `gold_silver_risk_off_long`, `risk_off_bond_equity_short`, `vix_backwardation_long`, `dxy_headwind_multinational_short` fired 0 trades. DXY uses UUP proxy (known limitation). |
| **T1.5 volume_profile wiring (Batch 244)** | **[PARTIAL]** | VP signals (`vp_poc`, `vp_value_area_high`, `vp_above_value_area`) ARE in trade_log. But `naked_poc_retest_long`, `poc_magnet_long`, `value_area_breakout_long` fired 0 trades. |
| **T2 24-DEC engine quality queue** | **[NEEDS-AUDIT]** | No `T2 24-DEC` markers found in code. Needs per-DEC audit to confirm which of the 24 quality fixes landed. |
| **T5b cointegrated-pairs precompute** | **[MISSING]** | `data_prefetch/pairs*` is absent. Approved May 19 ("APPROVE - run during T0->T1 idle window"). Output file never produced. Directly explains pairs_mean_reversion_* zero-trades. |
| Stage 3 dashboard MVP | [DONE] | `dashboard_stage_3/` present |

### Day 2 (May 21): ~150 strategies + agents + Stage 4 IB skeleton

| Commitment | Status | Evidence / Gap |
|---|---|---|
| **Phase 1C+ Wave 3 multi-TF** | **[PARTIAL]** | 4 strategies: `htf_aligned_breakout_long/short`, `po3_htf_aligned_long/short`. Plan expected ~10. |
| **Phase 1C+ Wave 3 13F-based** | **[MISSING]** | 0 strategies with "13f" or "institutional" in name registered as standalone entries. (institutional_signal IS computed and fed to other strategies, but no dedicated 13F-trigger strategies.) |
| **Phase 1C+ Wave 3 classification_change** | **[MISSING]** | 0 strategies with "classif" in name. None implemented. |
| **Phase 1C+ Wave 3 persistence** | **[MISSING]** | 0 strategies with "persist" in name. None implemented. |
| Phase 1B AgentGateConfig | [DONE] | `backtest/agents/agent_gate_config.py` |
| Phase 1B A/B orchestrator | [DONE] | `backtest/results/ab_orchestrator.py` |
| Stage 4 IB skeleton | [DONE] | `backtest/live_trading/ib_executor.py` |
| **150 strategies registered** | **[PARTIAL]** | Have 148. ~30 Wave 3 strategies missing. |

### Day 3 (May 22): 180 strategies + Phase 1B Sprint 7 + Stage 3 website + Stage 4 risk

| Commitment | Status | Evidence / Gap |
|---|---|---|
| Phase 1C+ Wave 4 ICT/SMC | [DONE] | 18 SMC strategies registered: `smc_bos_continuation`, `smc_bos_retest_entry`, `smc_choch_reversal`, `smc_inverse_fvg`, etc. |
| Phase 1B Sprint 7 cube_populator | [PARTIAL] | `cube_populator.py` present (275 lines) but post-merge cube slices NOT in `output_phase_1a_beta_merged_local/` (no `exit_by_*.csv` files; only trade-log + IS/OOS report). Per-batch outputs have them; merge job doesn't re-aggregate. |
| Stage 3 website + email digest | [DONE] | `dashboard_stage_3/` |
| Stage 4 risk overlay | [DONE] | `backtest/live_trading/risk_overlay.py` |
| **180 strategies total** | **[MISSING]** | Have 148. ~32 strategies short of target. Wave 3 backlog. |

### Day 4 (May 23): Phase 1A-β LAUNCH + speedup levers

| Commitment | Status | Evidence / Gap |
|---|---|---|
| **Lever A: 5->6 batches** | **[DEVIATED]** | Plan: 6 batches. Reality: 5 batches initially (all timed out at 5h 50m on GH Actions); re-split to 25 batches (per Batch 305 fix); 16 of 25 timed out; final run on Hetzner CPX62 with 25 batches succeeded ~11h. Net: 6-batch RAM-constrained design infeasible on GH Actions; reality required smaller batches + bigger box. |
| Lever B: pre-filter strategies | [DEFERRED-CORRECTLY] | Owner rejected May 19. N/A. |
| **Lever C: vectorize signal-once-per-ticker-day** | **[INVESTIGATION-NEEDED]** | Approved May 19 (~10-15% speedup). Per-Batch-315a static audit `compute_all_signals(df)` already runs ONCE per ticker-day at [screener.py:2808](backtest/signals/screener.py#L2808) — the N-times-per-ticker claim in original plan does not match current screener flow. Real Lever-C win likely comes from CROSS-ticker vectorization (compute panel-level signals for all 1937 tkrs in one pandas op vs 1937 separate calls). Needs profiling to confirm hot path BEFORE refactor. Deferred to Batch 316 after profile. |
| **Lever D: Polars over Pandas** | **[INVESTIGATED, DEFERRED]** | Polars 1.41 installed Batch 317 2026-05-25. Measured `polars.read_parquet` 2.2x faster than `pandas.read_parquet` on AAPL OHLCV (67KB, 3.4ms -> 1.6ms). Projected savings on full 1937-tkr session-init load: **3.6 seconds** out of 11h Phase 1A-beta run (<0.01%). The original "5-10% speedup" plan estimate was wrong — actual ROI is near-zero because (i) OHLCV loads are session-init only, (ii) hot path per profile is per-call compute (pandas math, not I/O), (iii) pandas<->polars boundary conversions would eat most of the gain. Deferred pending higher-impact migration target. |
| **Skip-unused signal producers** | **[BATCH-315a IMPLEMENTED]** | Module-level cache for `index_rebalance._load_events` + `pairs_trading._load_pair_snapshots`. Replaces ~2M per-call `Path.exists()` filesystem probes with 1 probe per session. Behavior preserved. Static cross-key audit showed 0 fully-orphan producer modules (consumers exist in same-module strat defs; my initial "100% orphan" claim was wrong). Per-key orphan deletion (chart_patterns, multi_timeframe, cross_asset have 24/18/20 candidate orphan keys per regex audit) queued as Batch 315b after thorough per-key verification. |
| **316b: insider_buying per-ticker pre-grouped cache** | **[IMPLEMENTED]** | Profile-driven: was 31% of `screen_instrument` wall-clock (full-DataFrame filter per call). Post-fix: O(1) ticker dict lookup + small per-ticker date filter. 4748 ticker keys indexed. Cache built once at first call; pre-filtered to `AcquiredDisposedCode=='A' AND TransactionCode=='P'`. Parity green (behavior-preserving). |
| **315b: per-key orphan deletion (chart_patterns / multi_timeframe / cross_asset)** | **[INVESTIGATED, DEFERRED]** | Per-function audit Batch 334 2026-05-25: NO compute_* function in cross_asset.py (5 functions) or multi_timeframe.py (4 functions) is fully orphan — every function has at least 1 consumed key, so whole-function skip is NOT SAFE. Per-key deletion (stripping unused keys from output dict) has marginal speedup (~microseconds per call) + maintenance risk (any new strategy could expect a dropped key). Deferred pending Stage D verdict data to confirm which keys are actually load-bearing; per-key deletion only warranted after empirical evidence. |
| **316c: compute_smc_signals field-selection** | **[INVESTIGATED, NO-WIN]** | Audit Batch 334 2026-05-25: smc_ict.py outputs 28 keys, ALL 28 consumed by active strategies (0% orphan). Field-selection has zero opportunity. The 28% wall-clock SMC profile finding comes from the underlying FVG/OB compute (vendored smartmoneyconcepts library), not orphan keys. Optimization target would be the library itself (multi-day vendoring refactor with Tier-1 correctness regression per DEC-508). Defer to a focused library-fork batch. |
| **320: Cat-C Bucket-1 gate loosens** | **[IMPLEMENTED]** | Owner-approved 2026-05-25. `donchian_10_breakout` + `rsi_volume_200ema`: `vol_spike_15x`/`vol_spike_2x` -> new `vol_above_avg` (>=1.0x). `break_retest_volume`: dropped `vol_spike_2x` entirely per Bulkowski (volume elevated on break, low on retest). Golden regen verified twice (12/12 rows changed; same count). |
| **321: process-pool infrastructure** | **[IMPLEMENTED]** | `_pool_init` + `_worker_screen_ticker` + `screen_universe(pool=...)` parameter. Workers hold ohlcv_dict in module-global; per-call work-tuple stays small (no df pickling). Sequential vs pool-path parity validated via in-process DummyPool in tests. Engine wiring (Batch 322) queued — needs smoke run on real Stage D + measured comparison before flipping the switch in `BacktestEngine._process_day`. |
| **322: engine pool wiring** | **[IMPLEMENTED]** | `BacktestEngine.__init__` adds `screen_pool_workers: int = 0` kwarg (0 = sequential, default). `_init_screen_pool()` lazy-builds the pool via `mp.get_context("spawn")` on the first `_process_day` call when `workers > 0`. `_teardown_screen_pool()` runs at end of `run()`. CLI flag `--screen-pool-workers N` added to `run_phase1a.py`. Defaults preserve pre-Batch-322 sequential behavior; parity test (workers=0) green. Real multiprocess parity validation deferred to owner-driven smoke run via `scripts/smoke_test_screen_pool.py` (byte-by-byte trade_log diff between workers=0 and workers=N on a Stage-D scenario). Hetzner CPX62 theoretical 4-8x speedup when enabled. |
| AWS Lightsail Docker | [DONE] | `Dockerfile` present |
| **Phase 1A-β actually launched** | **[DONE]** | 2026-05-24, 7191 trades, see `output_phase_1a_beta_merged_local/` |

### Day 5-7 (May 24-26): Phase 1A-β computes + dashboards + extract_winners

| Commitment | Status | Evidence / Gap |
|---|---|---|
| Phase 1A-β runs to completion | [DONE] | 7191 trades, ~10.5h wall on Hetzner CPX62 |
| `extract_phase_1a_beta_winners.py` | [DONE] | `scripts/extract_phase_1a_beta_winners.py` (need to verify it works against the actual merged output schema) |
| **`winners.parquet` with `combo_id`** | **[MISSING]** | trade_log.csv does NOT have a `combo_id` column. Plan specifically required this for winners pipeline. `extract_phase_1a_beta_winners.py` likely needs to derive combo_id from `(strategy, exit_reason, regime, ...)` at extraction time, but spec says combo_id should be in the trade_log itself. |
| Stage 3 journal + dashboard polish | [PARTIAL] | dashboard_stage_3 exists; polish status unclear |
| Stage 4 monitoring | [NEEDS-AUDIT] | risk_overlay present; monitoring pipeline status unclear |

### Day 8 (May 27): Phase 1A-β verdict + Phase 1B-α smoke ($3) + demo ($10)

| Commitment | Status | Evidence / Gap |
|---|---|---|
| Phase 1A-β verdict extracted | [PARTIAL] | This conversation produced the verdict (9 surviving cells, BUG-287 found, 60 quiet strategies identified). But `winners.parquet` not formally generated via `extract_phase_1a_beta_winners.py`. |
| Phase 1B-α smoke runner | ⚠ **[STUB - per Batch 345 audit 2026-05-25]** | `scripts/run_phase_1b_alpha_smoke.py` exists but **does NOT execute agents** — validates pre-flight + budget + winners.parquet existence + writes manifest.json; explicitly notes `"Full agent execution requires Phase 1B Sprint 7 langgraph_pipeline.py"`. See PHASE_1B_AUDIT_2026_05_25.md. |
| Phase 1B-α demo runner | ⚠ **[STUB]** | Same STUB pattern as smoke. |

### Day 9 (May 28): Phase 1B-α full launch

| Commitment | Status | Evidence / Gap |
|---|---|---|
| Phase 1B-α full runner | ⚠ **[STUB - per Batch 345 audit 2026-05-25]** | `scripts/run_phase_1b_alpha.py` is a STUB. Line 110-114 explicit: "Full agent execution requires Phase 1B Sprint 7 langgraph_pipeline.py". See PHASE_1B_AUDIT_2026_05_25.md. |
| Actually launched | [PENDING] | Phase 1B-α has NOT run. Blocked on owner per-regime / per-classifier analysis of Phase 1A-β results (Batch 310 directive) **AND** on building langgraph_pipeline.py + vendoring TradingAgents (Sprint 7 scope, 76-85 engineering days per PROJECT_PLAN.md §3.10). |

### Day 10 (May 29): POST_MAY_29_OPERATION_GUIDE.md

| Commitment | Status |
|---|---|
| POST_MAY_29_OPERATION_GUIDE.md | [DONE] |

---

## Summary of all gaps

### Path C "Execute B C12" status (owner directive 2026-05-25)

| Item | Status | Notes |
|---|---|---|
| **C12** Cat-C Bucket-2 rare-by-design test pins | [BATCH 340 SHIPPED] | 3 regression tests pin 7 short strategies as expected-rare; no code change. |
| **B#4** Russell + NDX index_rebalance events | [BATCH 341 PARTIAL SHIPPED] | NDX shipped (118 events from T1c CSV → 338 total in parquet); Russell deferred to Sprint 5 / DEC-380 FTSE feed. Strategies fire on NDX via generic 'add'/'drop' substring match — no screener.py code change needed. |
| **B#5** Pre-FOMC schedule | [BATCH 342 SHIPPED] | `scripts/build_fomc_calendar.py` + `data_prefetch/fred/fomc_calendar.parquet` (57 meetings 2020-2026). Pre-FOMC producer now emits `pre_fomc_d1` / `pre_fomc_d0` / `pre_fomc_window` / `days_until_fomc` keys. Unblocks `pre_fomc_long_sleeve` + `pre_fomc_quality_momentum_long`. |
| **B#6** UUP + DXY OHLCV cache | [DEFERRED] | UUP and DXY OHLCV missing from `data_prefetch/polygon/ohlcv_daily/`. Stage 2 HARD CUT NO-LIVE-API rule precludes runtime fetch. Sprint 1 data-prefetch deliverable. Affects `dxy_headwind_multinational_short` (Cat-B). |
| **B#7** Multi-timeframe HTF weekly_bias | [NO TRUE GAP] | Audited 2026-05-25: producer emits 9 keys including `weekly_bias_bull/bear` + `weekly_above_ema_10/20` + `weekly_momentum_pos`. Strategies correctly wired; rare-fire is data/regime-driven not code bug. |
| **B#8** SMC/ICT 4 strategies | [NO TRUE GAP] | Audited 2026-05-25: producer emits `smc_equal_highs_swept`, `smc_equal_lows_swept`, `smc_mitigation_block_long/short`. Strategy gates read matching keys. No name mismatch found. |
| **B#9** News sentiment shift | [NO TRUE GAP] | Audited 2026-05-25: `compute_news_sentiment_signals` emits `news_sentiment_shift` key. Strategy `news_sentiment_shift_long` reads matching key. Wired correctly. |
| **B#10** Quiver insider director-role | [NO TRUE GAP] | Audited 2026-05-25: `data_prefetch/quiver/insiders/global.parquet` has `isDirector` column populated for 458,292 of 1,000,000 rows (~46%). `insider_buying.compute_insider_cluster_signals` derives `insider_director_buyers_30d` correctly. |
| **B#11** True multi-quarter persistence precompute | [DEFERRED] | Single-quarter proxies in Batches 333+336+337+338 are sufficient for Stage D validation. Multi-quarter precompute infrastructure refinement queued for future Sprint. |
| **Batch 348** Look-ahead-bias audit | [SHIPPED 2026-05-25] | `scripts/audit_look_ahead_bias.py` written; ran static AST scan against `backtest/signals/` + `backtest/engine/` + empirical Stage D trade-log scan. Verdict: **0 confirmed look-ahead-bias defects.** 5 static findings reviewed by hand — all 5 false positives (3 false-positives in docstrings/comments, 2 false-positives because `df` is pre-truncated to `as_of` at [backtest.py:585](backtest/engine/backtest.py#L585) before reaching `compute_pead_signals`). 0 empirical findings across 35 strategies / 410 trades. Phase 1A-beta full re-run **not blocked** by look-ahead audit. Conversation-summary reference to "46 look-ahead-bias-flagged strategies" had no materialized artifact; this audit supersedes the unverified count. Report: `output_audit/look_ahead_bias_audit.md`. |
| **Batch 349** Sprint 7 Phase A vendoring scaffold | [SHIPPED 2026-05-25] | TauricResearch/TradingAgents v0.2.5 vendored to `vendored/tradingagents/` (commit `61522e1` 2026-05-17; 61 .py files; 437KB; Apache 2.0). `vendored/MANIFEST.md` updated with Phase A/B/C build sequence + Python 3.14 wheel incompatibility caveat (langchain-core 0.3.81 + langgraph 0.4.8 deps have no 3.14 wheels today; Phase 1B-α execution requires Python 3.12 on Hetzner). `backtest/agents/langgraph_pipeline.py` skeleton added with `Phase1BAlphaConfig` + `build_pipeline()` + `run_phase_1b_alpha()` entry point bridging AgentGateConfig (DEC-459) to upstream's `TradingAgentsGraph(selected_analysts=...)` API. 13 Phase A scaffold tests in `backtest/tests/test_langgraph_pipeline_phase_a.py` (vendor presence + config dataclass + pipeline-descriptor shape + manifest write + propagate-fn injection point). Full suite: 1038 tests pass (unit 682 + integration 149 + phase_1b_agents 35 + silent_gap 145 + look_ahead 14 + langgraph_phase_a 13). Sprint 7 Phase A: KICKOFF complete; Tier 1 unit-coverage + toolkit adapters land in subsequent batches. |
| **Batch 350** Sprint 7 Phase A toolkits + state augmentation | [SHIPPED 2026-05-25] | New `backtest/agents/toolkits/` package per TRADINGAGENTS_DATA_AUDIT.md Part D: `our_technical_toolkit.py` (5 methods: get_polygon_ohlcv + get_technical_signals + get_regime_context + get_liquidity_metrics + get_sector_relative_strength) + `our_fundamentals_toolkit.py` (5 methods: get_pit_financials + get_earnings_history + get_insider_transactions + get_congressional_trades + get_13f_holdings; all PIT-filtered by filing/disclosure date) + `our_news_toolkit.py` (3 methods: get_polygon_news + get_fred_event_log + get_analyst_rating_changes) + `our_trader_toolkit.py` (SCAFFOLD, 4 methods returning sentinel dicts pending BUG-095 Portfolio class) + `our_risk_toolkit.py` (PARTIAL: get_volatility_regime / get_macro_stress_signals / get_event_proximity / get_crisis_flags REAL; Portfolio-dependent methods SCAFFOLD). State augmentation module (`state_augmentation.py`) exposes `AugmentedAgentState` TypedDict mirroring upstream + 7 project extensions per audit Part E, with `build_augmented_state(ticker, as_of, toolkits)` builder. 28 Phase A tests in `backtest/tests/test_toolkits_phase_a.py` covering T1 unit (cache-miss schema + DEC-021 sizing + PIT property) + T2 smoke (toolkit instantiation) + T3 integration (build_augmented_state populates all 9 keys + LLM-mocked propagate hook receives state) + T6 regression (scaffold sentinel flags pinned). Full pyramid 1066 PASS / 0 FAIL (unit 682 + integration 149 + phase_1b_agents 35 + silent_gap 145 + look_ahead 14 + langgraph_phase_a 13 + toolkits_phase_a 28). |

---

### Critical (block correctness)

1. ~~**Wave 3 strategies missing**~~ **[WAVE 3 COMPLETE — Batch 338 2026-05-25 Path C]** All 30/30 Wave 3 strategies shipped across Batches 330-338: **10 13F-based** (Batches 330+331+336), **10 classification_change** (Batches 332+335+337 with producer at universe.get_classification_change_signals + symmetric from_tech flag), **10 persistence-proxy** (Batches 333+336+337+338 using Batch-330 producer's institutional counts + insider director/officer keys). True multi-quarter persistence precompute (333b infrastructure refinement) deferred to a future Sprint - current single-quarter proxies are sufficient for Stage D validation.
2. ~~**T5b cointegrated-pairs precompute missing**~~ **[BATCH 326 SHIPPED 2026-05-25]**: `scripts/build_t5b_pairs_precompute.py` + smoke snapshot at `data_prefetch/derived/cointegrated_pairs_t1a/2024-01-01.parquet` (7 cointegrated pairs from 8 mega-caps). Owner-runnable full T1a multi-snapshot job (~15-25 min per snapshot × 5 annual snapshots = ~1.5-2h offline).
3. ~~**`combo_id` column missing from trade_log**~~ **[BATCH 324 SHIPPED 2026-05-25]**: `combo_id = "{strategy}__{exit_reason}__{regime}"` derived at write time in `backtest/results/writer.py`. Winners pipeline can read it directly.
4. **60 of 125 active strategies fired zero trades** (Phase 1A-β output). Silent-gap candidates needing forensic per-strategy investigation. **6 closed by Batch 312 sub-batches 2026-05-24**: BUG-288 (PEAD trio: `pead_long`, `pead_short`, `pead_with_insider_confirmation_long`); BUG-289 (Quality trio: `xs_quality_top_quintile_long`, `xs_momentum_quality_combined`, `vix_backwardation_long`). **+1 closed by Batch 314 cap_band producer 2026-05-24**: BUG-290 RESOLVED-IMPLEMENTED unblocks `january_effect_long` (cap_band now produced in `screen_instrument` from `info.market_cap` via owner-approved 5-band taxonomy micro <$300M / small $300M-$2B / mid $2B-$10B / large $10B-$200B / mega >=$200B). **+4 strategies loosened by Batch 314 owner-approved gate changes**: Cat-2 B+C `strat_news_sentiment_long` (dropped momentum AND clause + article count 5 -> 3); Cat-3 A `strat_poc_magnet_long` (2% -> 4% POC distance); Cat-3 B `strat_naked_poc_retest_long` (1% -> 2% naked-POC distance); Cat-5 A `MAX_CANDIDATES_PER_DAY` default 10 -> 30 (admits Phase-1A-beta strategies starved by per-day cap). 49 remaining quiet candidates per PHASE_1A_BETA_QUIET_STRATEGY_FORENSIC.md. **Batch 316a 2026-05-25 owner directive: REVERSED Batch 218 deprecation; +23 previously-deprecated strategies re-activated for Stage D + Phase 1A-β empirical validation** (DEPRECATED_STRATEGIES set emptied; filter wiring retained for future re-pruning). Active strategy count 125 -> 148. Bonferroni/DSR denominator grows ~17% (owner-accepted tradeoff for empirical-over-a-priori validation). Quiet count for next Stage D may grow because un-deprecated strategies are largely literature-null (Zakamulin/Marshall-Cahan/etc.) — expected to fire trades but produce verdict=FAIL; if confirmed, codify with empirical evidence rather than citations alone.

### Important (impact downstream)

5. **Speedup Lever C (vectorize signals)** — Day 4 deliverable. Profile-first per Batch 315a finding (existing `compute_all_signals` already runs once per ticker-day; real win is cross-ticker panel vectorization). Phase 1A-β took ~10.5h on Hetzner CPX62; target with C+D+pool+skip-unused: <2h.
6. **Speedup Lever D (Polars)** — Day 4 deliverable. Investigated Batch 317 2026-05-25, DEFERRED with measurement evidence (3.6s savings on 11h run = <0.01% ROI). See Lever D row above.
7. ~~**Sprint 7 cube_populator post-merge**~~ **[BATCH 345 D9 SHIPPED 2026-05-25]** — `scripts/merge_batch_outputs.py` now concats `trade_exit_detail.csv` across batches + re-aggregates the full exit cube (1D `exit_by_<dim>.csv` for all CONTEXT_COLUMN_NAMES dims + `exit_method_multi_dim_cube.csv` + `exit_sweet_spots.csv` + `exit_pairwise_dominance.csv` + `exit_strategy_comparison.csv` + `exit_strategy_best.csv`). Right semantics (re-aggregate from per-trade detail vs N×duplicate concat of derived slices). Regression test pins the code path.
8. **T2 24-DEC engine quality queue** — Day 1 deliverable. **[BATCH 345 D10 AUDIT COMPLETE 2026-05-25]** All 8 priority DECs (DEC-062, DEC-138, DEC-216, DEC-230, DEC-231, DEC-234, DEC-246, DEC-365) audited via AUDIT_INDEX cross-reference: **all 8 are PARTIAL-IMPL-HELPER-ONLY** (helpers exist; engine call-path doesn't consume per memory rule "wired = engine-consumed"). Remaining 16 DECs are category-coded in IMPLEMENTATION_PLAN.md without explicit numbers; full audit deferred to T2 autonomous-wiring queue (12-18h effort per per-DEC standing approval). The T2 queue itself runs as a separate autonomous workstream after Stage D / Phase 1A-β.

### Confirmed DONE (no further action)

9. chart_patterns.py / cube_populator / AgentGateConfig / A/B orchestrator / Phase 1B-α runners / Dockerfile / Stage 3 dashboard / Stage 4 IB skeleton + risk overlay / walk-forward 4-fold / DSR / PSR / Chow / ADF / POST_MAY_29 guide

---

## Root cause of the drift

1. **No per-Day audit checkpoint during the May 19-29 sprint.** Each batch executed in isolation without cross-referencing the plan's Day-N deliverables.
2. **Wave 3 (13F/classification/persistence) was skipped.** Highest-volume planned addition (~30 strategies) but never started — likely de-prioritized when Phase 1A-α / Phase 1A-β timing pressure dominated.
3. **Speedup levers C/D were approved on paper but never built.** They fell off the radar when Phase 1A-β launch path moved to GH Actions / Hetzner with a different optimization surface (parallelism via more batches, not vectorization).
4. **No live progress tracker** (this file) was maintained — drift accumulated invisibly.

---

## Going forward

1. **Every batch that closes a gap must update this file** in the same commit (no exceptions).
2. **Plan-vs-reality audits before each major run** — verify all Day-N commitments DONE before triggering a Phase-level launch.
3. **Surface drift as a CHECKLIST gate** — add a per-turn check: "if this batch involves a phase launch, are all prior-Day commitments in BUILD_PLAN_PROGRESS.md status [DONE]?"

See `STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md` for the original plan and `PHASE_1A_BETA_SURVIVOR_ROSTER.md` for the empirical roster output.
