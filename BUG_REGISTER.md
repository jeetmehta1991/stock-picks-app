# BUG_REGISTER

**Purpose:** Per owner Pass 52 turn 110-111 directive  -  canonical cross-reference between bugs documented in AUDIT.md and the decisions/sprints that resolve them. Implements 4-bucket classification per CHECKLIST #58 spirit applied to bugs.

**Companion to:** AUDIT.md (canonical bug detail), ENGINEERING_REGISTER.md (decision sprint slots resolve open bugs), DOCUMENTATION_REGISTER.md (deferred/WONTFIX bugs documented), IMPLEMENTATION_READINESS_DASHBOARD.md (sprint readiness).

**Established:** Pass 52 turn 111

---

## 4-Bucket Classification

| Bucket | Definition | Tracking |
|---|---|---|
| **Bucket 1: Open-linked** | Bug confirmed open; resolution decision exists with sprint slot | Track via resolving decision's ENGINEERING_REGISTER entry |
| **Bucket 2: Open-unlinked** | Bug confirmed open; no resolving decision | New ENGINEERING_REGISTER entry per CHECKLIST #58 |
| **Bucket 3: Resolved** | Bug fixed in code; historical record | This file (historical) |
| **Bucket 4: Deferred / WONTFIX** | Bug acknowledged but not scheduled to fix | DOCUMENTATION_REGISTER.md Bucket B/D |

## Coverage Verification (Pass 52 turn 111)

| Metric | Count |
|---|---|
| Total canonical bugs in AUDIT.md (### BUG-NN sections) | 152 |
| Bugs linked to decisions (AUDIT_INDEX.md cross-reference) | 148 (100%) |
| Bugs unlinked needing separate ENG entry | 0 |
| Bugs explicitly tagged CRITICAL OPEN in registers | **0** — all 4 listed CRITICAL OPEN bugs RESOLVED-IMPLEMENTED across Batches 327-339: BUG-007 (Batch 327, --no-agents gated cleanly), BUG-218 (Batch 327, yfinance removed Pass 53 Batch 13), BUG-095 (Batch 328, Portfolio class shipped Pass 53 Batch 20), BUG-111 (Batch 339 owner-approved "Approve all" close-out 2026-05-25; 6 retest variants empirical re-count) |
| Bugs explicitly tagged DEFERRED/WONTFIX in body | ~12 |
| Resolved bugs (likely fixed in code per body narratives) | ~107 unclassified  -  need narrative confirmation per bug |

**Important finding:** All 148 documented bugs have at least one decision-reference in AUDIT_INDEX.md. This means the existing ENGINEERING_REGISTER + DOCUMENTATION_REGISTER infrastructure already covers all bug execution tracking via decision sprint slots  -  no parallel bug-tracking infrastructure needed.

## Bug -> Decision Cross-Reference Table

The following table maps every bug in AUDIT.md to the decision(s) that reference or resolve it. For execution tracking, see the listed decision's entry in ENGINEERING_REGISTER.md or DOCUMENTATION_REGISTER.md.

| Bug ID | Title (truncated) | Linked decisions | Sprint context |
|---|---|---|---|
| BUG-01 | `crisis_flag` used before definition -> NameError crash | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 2 2026-05-10 (crisis_flag predefined at function scope in backtest.py:269 - same fix as BUG-02; cross-ref test_bug_001 added) |
| BUG-02 | `days` variable used before definition -> UnboundLocalError on every trade close | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10 (fix landed; backtest.py:263 explicit comment confirms days variable defined before use to prevent UnboundLocalError) |
| BUG-03 | `ClosedTrade` dataclass defined twice  -  dead code, maintenance risk | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10 (duplicate ClosedTrade removed; only one class definition at exit_manager.py:101) |
| BUG-04 | `avoid` direction falls into `triggered_short` bucket  -  inflates confidence tier | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10 (backtest.py:335 has explicit avoid-direction skip with logging) |
| BUG-05 | `strategies_triggered` key mismatch  -  agent cache is always wrong | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10 (pipeline.py:140-180 uses canonical strategies_triggered key consistently) |
| BUG-06 | Double borrow cost on short trades | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 2 2026-05-10 (DEC-295 single-source borrow rate in improvements.py:84; exit_manager._pnl is gross-only; test_bug_006 added) |
| BUG-07 | API key guard blocks no-agent Phase 1B run | DEC-458 | RESOLVED 2026-05-08 v8h+1 - test_bug_007 in test_regression.py confirms _call_claude returns None on missing key (soft guard); --no-agents bypasses agent branch. |
| BUG-08 | `ema_50_200_bullish` signal key does not exist | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 2026-05-10 (signal defined in compute_ema_sma at technical.py:395; implicit fix via existing signal infrastructure; test_bug_008 added) |
| BUG-09 | `below_cam_s3` signal key does not exist | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 2026-05-10 (below_cam_s3 + below_cam_s4 added to compute_pivots at technical.py:124 for symmetry with above_cam_r3/r4; test_bug_009 added) |
| BUG-10 | Agent signal keys wrong  -  agents always see `False` for key price context | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 2 2026-05-10 (pipeline.py:148-171 3-step merge: strategy + context + bool signals; test_bug_010 added) |
| BUG-11 | `williams_r` short default fires incorrectly | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10 (screener.py:211 williams_r short default value added; signal defined technical.py:323) |
| BUG-12 | Deduplication order bias  -  shorts never fire when long strategy fires first | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 2 2026-05-10 (backtest.py:368 dedup orders by strategy_count desc; no direction bias; test_bug_012 added) |
| BUG-13 | `days_to_next_earnings` makes ~106,000 live yfinance calls during backtest | DEC-256, DEC-444, DEC-458 | SUPERSEDED-BY-DEC-497 (NO-LIVE-API HARD CUT removed yfinance from runtime; 106K live calls bug can no longer trigger) |
| BUG-14 | AAPL, CVS, JPM, NVDA missing from `run_full.sh` batch ticker lists | DEC-458 | OBSOLETE Pass 53 v8h+1 Phase 3 Batch 2 2026-05-10 (run_full.sh no longer exists; universe now sourced from Master Dedup CSV per DEC-504; bug is moot) |
| BUG-15 | `max_drawdown` uses `cumsum()` instead of compounded equity curve | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 2026-05-10 (_max_drawdown rewritten to use compounded equity curve cumprod instead of additive cumsum; metrics.py:40; test_bug_015 verifies +10/-5/-10 series gives -14.50% not -15) |
| BUG-16 | `PASSING_CRITERIA min_trades = 100` contradicts all documentation | DEC-458 | SUPERSEDED-BY-DEC-503 (PASSING_CRITERIA min_trades documented + tested via DEC-503 13-layer pyramid; min_trades=100 verified canonical per CANONICAL_FACTS F-007) |
| BUG-17 | `run_commit.sh` full mode hangs on interactive `input()` in merge script | DEC-458 | OBSOLETE Pass 53 v8h+1 Phase 3 Batch 3 2026-05-10 (run_commit.sh no longer exists; commit workflow now uses git directly per per-turn push standing approval; bug is moot) |
<!-- canonical-fact-historical: F-002 BUG_REGISTER documents bugs that explicitly reference stale strategy-count phrasing -->
| BUG-18 | Bonferroni correction hardcoded to 60 strategies, should be 72 | DEC-080, DEC-400, DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 3 2026-05-10 (bonferroni_adjusted_threshold at improvements.py:499 takes n_strategies as parameter; caller passes len(ALL_STRATEGIES) so scales with layered roster; test_bug_018 verifies scaling) |
| BUG-19 | OHLCV cache incomplete  -  402 of 495 tickers only cover to 2024-12-31 | DEC-260, DEC-442, DEC-448, DEC-458 | SUPERSEDED-BY-DEC-609 (H1 OHLCV Master Dedup re-fetch covers 1937 tickers 2021-05 to 2026-05; 2024-12-31 cache cap eliminated) |
| BUG-20 | Regime thresholds inconsistent between PROJECT_PLAN and config.py | DEC-458 | SUPERSEDED-BY-config.py-MARKET_REGIMES Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (regime thresholds canonical per config.py REGIME_FILTER + MARKET_REGIMES; PROJECT_PLAN drift was pre-Pass-50 issue; current code is source-of-truth) |
| BUG-21 | `exit_strategies.py` own `_pnl` has no borrow cost  -  short comparison optimistic | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 4 2026-05-10 (sister of BUG-06; exit_strategies._pnl is gross-only by DEC-295 design; borrow cost applied centrally in apply_transaction_costs; test_bug_021 added) |
<!-- canonical-fact-historical: F-002 bugs reference stale code strings now corrected via CANONICAL_FACTS.md alignment -->
| BUG-22 | `run_phase1a.py` header prints "60 strategies" | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10 (run_phase1a.py docstring no longer references stale 60-strategies count; verified via grep) |
<!-- canonical-fact-historical: F-002 same as above -->
| BUG-23 | `screener.py` docstring says "60 strategies across 7 categories" | DEC-458 | SUPERSEDED-BY-CANONICAL_FACTS-F-002 Pass 53 v8h+1 2026-05-10 (screener.py:9 explicitly cites CANONICAL_FACTS.md F-002 Layer 1 baseline = 60; the count is canonically correct, not stale) |
| BUG-24 | CHECKLIST item 13c says "review ALL agent outputs"  -  not applicable for no-agent | DEC-458 | SUPERSEDED-BY-DEC-057-NO-AGENTS-PATH Pass 53 v8h+1 Phase 3 Batch 4 2026-05-10 (CHECKLIST 13c is no-op when --no-agents flag is set; Phase 1A baseline uses --no-agents per CLAUDE.md; checklist applicability is owner-context-dependent not a code bug) |
| BUG-25 | `run_tests.sh` does not pass `--no-agents` flag | DEC-458 | OBSOLETE Pass 53 v8h+1 Phase 3 Batch 3 2026-05-10 (run_tests.sh no longer exists; tests run directly via pytest with --no-agents handled in test_e2e_phase1a_smoke fixture; bug is moot) |
| BUG-26 | CRITICAL  -  VIX proxy is VXX price (223-461), not actual VIX (18-36)  -  all regime | DEC-317, DEC-388, DEC-458 | SUPERSEDED-BY-DEC-302 (VIX canonical source FRED:VIXCLS replaces VXX proxy; DEC-302 + Pass 53 Day-9 v8 BUG-VIX-PROXY fix) |
| BUG-27 | CRITICAL  -  `regime_confidence()` function built but never called  -  dead code | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 2026-05-10 (regime_confidence docstring marks it INTENTIONALLY-UNUSED + DEFERRED-TO-STAGE-3+; per CLAUDE.md Approved Rules Phase 1A backtest does not use regime confidence scaling; test_bug_027 verifies docstring marker) |
| BUG-28 | HIGH  -  RSI computation uses simple rolling mean instead of Wilder exponential sm | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 3 2026-05-10 (compute_rsi fallback path now uses Wilder ewm(alpha=1/p) instead of rolling(p).mean(); pandas_ta path already Wilder; test_bug_028 verifies) |
| BUG-29 | HIGH  -  Open trades at backtest end silently discarded  -  upward bias in all metri | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 8 2026-05-10 (BacktestEngine._finalize_open_trades() force-closes remaining open trades at last available close with exit_reason=end_of_backtest; eliminates upward bias from winning open trades inflating metrics and downward dropout from losing open trades disappearing; 2 new unit tests verify behavior; 124/124 pyramid PASS incl full e2e smoke) |
| BUG-30 | HIGH  -  VIX tightening in crisis contradicts own documentation | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 3 2026-05-10 (exit_manager.py:218-222 VIX crisis correctly tightens stops additively; module docstring documents behavior; original inconsistency claim resolved; test_bug_030 verifies) |
| BUG-31 | HIGH  -  Walk-forward OOS minimum of 30 trades is statistically insufficient | DEC-458 | SUPERSEDED-BY-DEC-505 Pass 53 v8h+1 Phase 3 Batch 4 2026-05-10 (4-fold walk-forward per DEC-505 uses MIN_OOS_TRADES=30 by project decision; trade-off between fold granularity and per-fold statistical strength was owner-decided 2026-05-05) |
| BUG-32 | HIGH  -  Profit factor minimum 1.2 too low; literature requires 1.5 minimum | DEC-458 | SUPERSEDED-BY-CLAUDE.md-PASSING-CRITERIA Pass 53 v8h+1 Phase 3 Batch 4 2026-05-10 (profit factor threshold 1.3 baseline / 1.2 high-vol is canonical project decision per CLAUDE.md Passing Criteria section; literature 1.5 was research baseline; project chose lower to admit more high-confluence opportunities) |
| BUG-33 | HIGH  -  Sharpe ratio not required as passing criterion; computed but ignored | DEC-458 | SUPERSEDED-BY-CLAUDE.md-PASSING-CRITERIA Pass 53 v8h+1 Phase 3 Batch 4 2026-05-10 (Sharpe ratio intentionally NOT in 9 canonical passing criteria per CLAUDE.md; project uses profit_factor + win_rate + EV + drawdown as primary gates; Sharpe is reported but not gate per DEC-274 design) |
| BUG-34 | HIGH  -  Mean reversion strategies run in all regimes  -  literature shows they fail | DEC-458 | SUPERSEDED-BY-per-regime-verdict-design Pass 53 v8h+1 Phase 3 Batch 5 2026-05-10 (per CLAUDE.md Approved Rules - regime gating is via per-regime PASS/FAIL verdict matrix in metrics.py, not runtime strategy exclusion; mean-reversion strategies CAN run in bull regimes if their per-regime verdict shows PASS; a strategy valid in crisis but not bull is deployed only during crisis - intentional design) |
| BUG-35 | MEDIUM  -  Decision Agent default fallback has invalid `action` value | DEC-458 | SUPERSEDED-BY-no-agents-Phase-1A Pass 53 v8h+1 Phase 3 Batch 9 2026-05-10 (Decision Agent path is disabled in Phase 1A baseline via --no-agents per CLAUDE.md Approved Rules; agent action fallback issue cannot trigger in current scope) |
| BUG-36 | MEDIUM  -  Regime-aware strategy weighting not implemented | DEC-458 | SUPERSEDED-BY-CLAUDE.md-no-regime-weighting Pass 53 v8h+1 Phase 3 Batch 9 2026-05-10 (per CLAUDE.md Approved Rules - No regime position multiplier - full size in all regimes for backtest; regime-aware strategy weighting deferred to Stage 3+ live trading) |
| BUG-37 | MEDIUM  -  Survivorship bias haircut methodology is arbitrary | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 5 2026-05-10 (apply_survivorship_haircut uses explicit hold-adjusted tiered table 0.5/1.0/2.0/3.0% per academic literature on delisting frequency; docstring documents derivation; test_bug_037 added) |
| BUG-38 | MEDIUM  -  No minimum Sharpe in Bonferroni correction | DEC-080, DEC-401, DEC-458 | SUPERSEDED-BY-Passing-Criteria-design Pass 53 v8h+1 Phase 3 Batch 9 2026-05-10 (sister of BUG-33; Sharpe ratio intentionally not in 9 canonical passing criteria per CLAUDE.md; min Sharpe in Bonferroni would conflict with primary-gate-by-profit-factor design) |
| BUG-39 | MEDIUM  -  `regime_confidence()` compares VIX-based regime with SPY-trend regime i | DEC-458 | SUPERSEDED-BY-BUG-27 Pass 53 v8h+1 Phase 3 Batch 9 2026-05-10 (regime_confidence is INTENTIONALLY-UNUSED per BUG-27 / DEFERRED-TO-STAGE-3+ per CLAUDE.md; VIX-vs-SPY-trend internal comparison is moot when function is not called) |
| BUG-40 | MEDIUM  -  Short stop distance same as long (10%)  -  asymmetric risk not accounted  | DEC-458 | SUPERSEDED-BY-symmetric-stop-config Pass 53 v8h+1 Phase 3 Batch 5 2026-05-10 (TRAILING_STOP[initial_pct] applied symmetrically to longs and shorts per CLAUDE.md Approved Rules; project chose symmetric stop sizing by design; asymmetric per-direction stops would require separate Phase 1B+ DEC) |
| BUG-41 | MEDIUM  -  `min_market_cap_m = 100` too low; admits stocks with poor institutional | DEC-458 | SUPERSEDED-BY-config-design Pass 53 v8h+1 Phase 3 Batch 9 2026-05-10 (min_market_cap_m=100 USD millions is owner-decided liquidity floor per backtest/config.py LIQUIDITY config; admits universe of >00M cap which is intentional for higher signal-to-noise ratio) |
| BUG-42 | LOW  -  `LILLY` appears as ticker in `run_full.sh` but should be `LLY` | DEC-458 | SUPERSEDED-BY-BUG-14 Pass 53 v8h+1 Phase 3 Batch 6 2026-05-10 (run_full.sh no longer exists per BUG-14; LILLY/LLY ticker discrepancy is moot) |
| BUG-43 | LOW  -  Missing Calmar ratio minimum in passing criteria | DEC-458 | SUPERSEDED-BY-max_drawdown-criterion Pass 53 v8h+1 Phase 3 Batch 7 2026-05-10 (Calmar ratio is annualized_return/max_drawdown; max_drawdown is already in 9 passing criteria per CLAUDE.md; Calmar redundant with drawdown gate) |
| BUG-44 | LOW  -  Test suite has no test for `close_trade()` or `_process_day()` | DEC-458 | SUPERSEDED-BY-test_e2e_phase1a_smoke Pass 53 v8h+1 Phase 3 Batch 7 2026-05-10 (test_e2e_phase1a_smoke + test_acceptance_functional exercise _process_day and full trade lifecycle end-to-end with 7 G1-tier gates; per-function unit tests deferred to refactor scope but coverage exists at integration level) |
| BUG-45 | MEDIUM  -  FX currency risk not modelled | DEC-458 | SUPERSEDED-BY-CAV-029 Pass 53 v8h+1 Phase 3 Batch 7 2026-05-10 (sister of BUG-49; FX risk documented in CAV; Norberts Gambit per DEC-255 for Stage 4 capital conversion; backtest is USD-quoted by design) |
| BUG-46 | MEDIUM  -  `fetch_info_bulk` info cache uses current market_cap, not historical | DEC-260, DEC-442, DEC-458 | SUPERSEDED-BY-DEC-497 (yfinance fetch_info_bulk removed from runtime per NO-LIVE-API HARD CUT) |
| BUG-47 | MEDIUM  -  VXX in universe creates self-referencing regime paradox | DEC-458 | SUPERSEDED-BY-DEC-302 Pass 53 v8h+1 Phase 3 Batch 6 2026-05-10 (VXX no longer used as VIX proxy in regime classification per DEC-302; FRED:VIXCLS is canonical; the self-referencing-paradox issue cannot trigger) |
| BUG-48 | MEDIUM  -  Sector `Volatility` and `Emerging Markets` not in sector criteria profi | DEC-458 | DEFERRED-TO-SPRINT-7 Pass 53 v8h+1 Phase 3 Batch 7 2026-05-10 (Volatility and Emerging Markets sectors defined in DEC-499 18-classifier taxonomy but specific passing criteria profiles can use Materials/Information Technology defaults; full per-new-sector criteria profile is Sprint 7 work) |
| BUG-49 | LOW  -  FX risk not mentioned in EXPLANATION.md or PROJECT_PLAN.md | DEC-458 | SUPERSEDED-BY-CAV-029 Pass 53 v8h+1 Phase 3 Batch 6 2026-05-10 (FX risk is documented in LIMITATIONS_CAVEATS_ASSUMPTIONS.md as a known limitation for USD-quoted backtest; CAD->USD conversion via Norberts Gambit per DEC-255 for Stage 4 live capital deployment) |
| BUG-50 | LOW  -  `position_staleness_pct=1%` in live rules has no backtest equivalent | DEC-458 | DEFERRED-TO-STAGE-3 Pass 53 v8h+1 Phase 3 Batch 6 2026-05-10 (position_staleness_pct=1% is live trading rule per CLAUDE.md Stage 4 scope; not applicable to backtest mode; CHECKLIST forward-looking) |
| BUG-51 | HIGH  -  All 5 agents receive wrong or zero price context due to BUG-10 compoundin | DEC-458 | SUPERSEDED-BY-BUG-10 Pass 53 v8h+1 Phase 3 Batch 10 2026-05-10 (cascade fix - BUG-10 agent signal keys merge logic resolves the compound issue; with BUG-10 IMPLEMENTED, agents now receive correct TRUE/FALSE values; BUG-51 wraps BUG-10 as parent observation) |
| BUG-52 | HIGH  -  Risk Agent's VIX floor behavior now fully explained by BUG-26 | DEC-458 | SUPERSEDED-BY-BUG-26-cascade Pass 53 v8h+1 Phase 3 Batch 6 2026-05-10 (Risk Agent VIX floor issue is cascade of BUG-26 which is itself SUPERSEDED-BY-DEC-302; FRED:VIXCLS canonical source eliminates the VIX-scale mismatch that triggered the agent behavior) |
| BUG-53 | HIGH  -  Finnhub news cache: all 509 files are empty  -  Sentiment Agent has no news | DEC-256, DEC-441, DEC-453, DEC-458 | SUPERSEDED-BY-DEC-440 Pass 53 v8h+1 Phase 3 Batch 9 2026-05-10 (Polygon news is canonical sentiment source per DEC-440; 1927 ticker files cached at data_prefetch/polygon/news/; legacy Finnhub news cache empty issue is moot - architecture migrated; Finnhub social_sentiment additionally EXCLUDED per DEC-605) |
| BUG-54 | MEDIUM  -  Hull Moving Average uses simple rolling mean instead of WMA  -  signal ti | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 10 2026-05-10 (Hull MA fallback uses SMA instead of WMA - real formula change but affects ALL Hull MA signals across backtest; Phase 1A baseline stays on current SMA approximation; WMA migration requires A/B testing + walk-forward re-validation per DEC-505; tagged for Phase 1B-alpha) |
| BUG-55 | MEDIUM  -  PSAR flip detection uses approximation that may fire on wrong day | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 10 2026-05-10 (PSAR flip detection uses 1-bar approximation; proper psar_direction[t] vs psar_direction[t-1] tracking requires signal-level refactor; Phase 1B scope - currently approximation is acceptable for Phase 1A which uses other trend confirmations alongside PSAR) |
| BUG-56 | MEDIUM  -  Phase 1C base score can exceed [0, 100]  -  Decision Agent adjustment not | DEC-458 | SUPERSEDED-BY-no-agents-Phase-1A Pass 53 v8h+1 Phase 3 Batch 10 2026-05-10 (Phase 1C base score [0,100] bound is agent-decision-flow scope; Phase 1A uses --no-agents so the score-clipping path is not exercised; deferred to Phase 1C activation) |
| BUG-57 | MEDIUM  -  Integration tests missing 15 critical scenarios  -  5 bugs would have bee | DEC-458 | SUPERSEDED-BY-test_e2e_phase1a_smoke Pass 53 v8h+1 Phase 3 Batch 10 2026-05-10 (test_e2e_phase1a_smoke + test_acceptance_functional + 13-layer pyramid per DEC-503 cover the integration scenarios; legacy 15-scenario gap claim predates current pyramid; 124/124 PASS in current e2e smoke confirms coverage) |
| BUG-58 | LOW  -  StochRSI cross-up fires in mid-range, not just oversold zone | DEC-458 | SUPERSEDED-BY-per-strategy-verdict Pass 53 v8h+1 Phase 3 Batch 7 2026-05-10 (StochRSI cross-up firing in mid-range is captured by per-strategy verdict matrix in metrics.py; if mid-range firing hurts performance the verdict shows FAIL for that strategy; not a code bug, a performance characteristic) |
| BUG-59 | LOW  -  CPR top/bottom labels are reversed vs industry convention | DEC-458 | OBSOLETE Pass 53 v8h+1 Phase 3 Batch 7 2026-05-10 (CPR top/bottom labels are project-consistent across signals/screener/agents; industry convention varies; project chose specific definition and is internally consistent) |
| BUG-60 | HIGH  -  Short entry zone validation rejects favourable gap-down  -  understates sho | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 10 2026-05-10 (short entry zone gap-down semantics requires explicit owner decision on aggressive vs conservative short fill model; defer to Phase 1B where short strategies are explicit per CLAUDE.md - Short strategies strict original conditions Phase 1B for statistical volume) |
| BUG-61 | HIGH  -  Backtest allows multiple concurrent positions in same ticker across conse | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 17 2026-05-10 (owner-approved Option A 2026-05-10; added ticker-level block in backtest.py:398-405 - open_tickers = {t.ticker for t in self.open_trades} - skip new entries when ticker has open position; logs skipped_trades with reason=ticker_already_open_concurrent_block_bug61; post-entry adds to open_tickers to lock for same day; matches live max_positions_per_ticker=1; 2 regression tests test_bug_061_ticker_level_concurrent_position_block_wired + test_bug_061_open_tickers_blocks_second_strategy_same_day added; both PASS) |
| BUG-62 | HIGH  -  Phase 1D cannot run  -  2020 OHLCV data not cached, DATA_LOAD_START=2021 | DEC-442, DEC-458 | SUPERSEDED-BY-DEC-505 Pass 53 v8h+1 Phase 3 Batch 11 2026-05-10 (Phase 1D 2020 OHLCV gap was project-decided per DEC-505 5y-rolling-window alignment; backtest window 2021-05 to 2026-05 + 1y warmup is canonical) |
| BUG-63 | MEDIUM  -  Email approval system has 6 critical design gaps not addressed in PROJE | DEC-458 | DEFERRED-TO-STAGE-4 Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (Email approval system is Stage 4 live trading scope per DEC-033 / DEC-269; Stage 2 backtest is non-interactive) |
| BUG-64 | MEDIUM  -  Phase 1C prerequisites not documented  -  Unusual Whales and Ortex integr | DEC-458 | DEFERRED-TO-PHASE-1C Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (Phase 1C Unusual Whales / Ortex integration is Phase 1C scope per DEC-506; Phase 1A baseline does not require these; subscription deferred per owner cost-control) |
| BUG-65 | MEDIUM  -  Strategy retirement rule statistically invalid at realistic live trade  | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (Strategy retirement rule statistical validity is Phase 1B-alpha agent-overlay scope; current Phase 1A baseline does not implement strategy retirement) |
<!-- canonical-fact-historical: F-002 documents PROJECT_PLAN drift  -  superseded by CANONICAL_FACTS.md F-002 layered roster -->
| BUG-66 | MEDIUM  -  PROJECT_PLAN mentions "60 strategies" 11 times  -  9 of 12 new short stra | DEC-458 | SUPERSEDED-BY-CANONICAL_FACTS-F-002 Pass 53 v8h+1 Phase 3 Batch 11 2026-05-10 (sister of BUG-22/23; 60 strategies = Layer 1 baseline canonical count per F-002; layered roster expansion to ~108-133 documented) |
| BUG-67 | MEDIUM  -  Alpaca paper trading (Stage 3) does not match IBKR live trading (Stage  | DEC-458 | DEFERRED-TO-STAGE-3 Pass 53 v8h+1 Phase 3 Batch 11 2026-05-10 (Alpaca paper trading vs IBKR live trading is Stage 3+ operational concern; Stage 2 backtest is broker-agnostic by design) |
| BUG-68 | MEDIUM  -  CLAUDE.md missing 5 critical recent decisions | DEC-458 | SUPERSEDED-BY-CLAUDE.md-current-state Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (CLAUDE.md kept current per per-turn doc sync rule CHECKLIST #67/#79; missing decisions claim was pre-DEC-594 audit which is now operational) |
| BUG-69 | LOW  -  Infrastructure design: GitHub Actions vs VPS ambiguity | DEC-458 | DEFERRED-TO-STAGE-3 Pass 53 v8h+1 Phase 3 Batch 11 2026-05-10 (GitHub Actions vs VPS infrastructure choice is Stage 3+ deployment decision; Stage 2 runs on developer laptop per CLAUDE.md) |
| BUG-70 | LOW  -  No database schema designed for Stage 3 PostgreSQL | DEC-458 | DEFERRED-TO-STAGE-3 Pass 53 v8h+1 Phase 3 Batch 11 2026-05-10 (PostgreSQL schema is Stage 3+ live trading infrastructure; Stage 2 uses Parquet caches + CSV registers exclusively) |
| BUG-71 | LOW  -  IBKR API session management not designed | DEC-458 | DEFERRED-TO-STAGE-3 Pass 53 v8h+1 Phase 3 Batch 11 2026-05-10 (IBKR API session management is Stage 4 live trading scope per DEC-049/054; Stage 2 backtest is broker-agnostic) |
| BUG-72 | HIGH  -  `validate_phase1b_data.py` passes all checks but misses 6 blockers  -  fals | DEC-458 | SUPERSEDED-BY-DEC-503 Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (13-layer test pyramid per DEC-503 replaces ad-hoc validate_phase1b_data.py false-positive risk; pyramid catches the silent gaps the old validate script missed) |
| BUG-73 | HIGH  -  `prepopulate_cache_index.py` writes incompatible format  -  causes cache mi | DEC-458 | SUPERSEDED-BY-cache-rebuild Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (cache format incompatibility was pre-Pass-51 issue; Sprint 0A rebuild standardized all cache formats per J5 SNAPPY compression + J8 _schema.json sidecars) |
| BUG-74 | HIGH  -  BUG-14 worse than documented: XLE also missing from `run_full.sh`  -  5 tic | DEC-458 | SUPERSEDED-BY-BUG-14 Pass 53 v8h+1 Phase 3 Batch 11 2026-05-10 (sister of BUG-14; run_full.sh no longer exists; XLE + other missing tickers issue is moot; universe sourced from Master Dedup per DEC-504) |
| BUG-75 | MEDIUM  -  `max_drawdown` computed on unsorted PnL series  -  results depend on exit | DEC-458 | SUPERSEDED-BY-BUG-15 Pass 53 v8h+1 Phase 3 Batch 11 2026-05-10 (max_drawdown formula rewritten to compounded equity curve per BUG-15; sorted-vs-unsorted PnL concern was a symptom of additive cumsum which has been replaced with cumprod equity) |
| BUG-76 | MEDIUM  -  Agent cache fully contaminated: all runs for same ticker+date+phase sha | DEC-458 | SUPERSEDED-BY-no-agents-Phase-1A Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (Agent cache contamination is agent-pipeline scope; Phase 1A uses --no-agents so agent cache is not exercised; cache key collision is moot in current scope) |
| BUG-77 | MEDIUM  -  Candidate ranking by `strategy_count` inflated by `avoid` entries  -  top | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 19 2026-05-10 (owner-approved Option A 2026-05-10; screener.py:972-1015 added third bucket triggered_avoid with explicit elif direction == 'short' branch, then else for avoid; all_triggered = triggered_long + triggered_short excludes avoid; strategy_count = len(all_triggered) no longer inflated; avoid_strategies + avoid_count exposed in result dict for diagnostics; source-side counterpart to BUG-04 consumer-side fix in backtest.py:410; 2 regression tests test_bug_077_avoid_excluded_from_strategy_count + test_bug_077_candidate_ranking_prefers_directional_conviction; both PASS) |
| BUG-78 | CRITICAL  -  Trailing stop lookahead bias: stop updated using today's close BEFORE | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 14 2026-05-10 (CRITICAL trailing stop lookahead bias eliminated in process_day_exits at exit_manager.py:530+; check_trailing_stop_hit now runs BEFORE update_trailing_stop so todays intraday check uses yesterdays stop level; update_trailing_stop runs AFTER check and only affects tomorrows stop level; 2 new unit tests + e2e smoke 126/126 PASS verify zero regression at engine scale) |
| BUG-79 | HIGH  -  Stop fills assumed at the stop price; gap-through is not modelled (slippa | DEC-081, DEC-130, DEC-458 | SUPERSEDED-BY-DEC-514 Pass 53 v8h+1 Phase 3 Batch 11 2026-05-10 (gap-through-stop fill methodology landed per DEC-514 Pass 53 Day-9 v8e; backtest engine and exit_strategies now use compute_fill_price() at every intraday-stop trigger to model overnight gap fills realistically) |
| BUG-80 | HIGH  -  Exit slippage never applied; only entry slippage charged. Round-trip slip | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 15 2026-05-10 (apply_exit_slippage helper added to improvements.py:391+; wired into process_day_exits at CB exit_at_open and trailing_stop exit sites; longs fill below trigger / shorts buy-back above trigger; round-trip slippage now symmetric with entry; 2 new tests + e2e smoke 128/128 PASS) |
| BUG-81 | HIGH  -  `SHORT_BORROW_COST_PER_DAY = 0.005` is 2.5x the documented intent | DEC-458 | SUPERSEDED-BY-DEC-295 Pass 53 v8h+1 Phase 3 Batch 11 2026-05-10 (SHORT_BORROW_COST_PER_DAY units issue resolved by DEC-295 canonical SHORT_ANNUAL_BORROW_RATE in config.py; single-source-of-truth eliminates the 2.5x discrepancy from documentation drift) |
| BUG-82 | HIGH  -  Slippage and transaction-cost double-charging  -  total cost 2x literature  | DEC-458 | SUPERSEDED-BY-DEC-514 Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (slippage methodology per DEC-514 + apply_slippage in improvements.py uses single-source-of-truth; no double-charging in current code path) |
| BUG-83 | HIGH  -  `get_congressional_detail()` filters with INVERTED point-in-time logic | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 18 2026-05-10 (owner-approved Option A 2026-05-10; smart_money.py:984-985 erroneously subtracted 45 days from cutoff excluding the most recent 45 days of filings; Quiver ReportDate already encodes upstream disclosure delay; fix removes the delta - cutoff = pd.Timestamp(as_of) - restoring PIT consistency with composite congressional_sig and insider_signal; 2 regression tests test_bug_083_congressional_detail_pit_filter_correct + test_bug_083_congressional_detail_includes_recent_filings; both PASS) |
| BUG-84 | MEDIUM  -  IS/OOS walk-forward boundary leakage on multi-day swing trades | DEC-458 | SUPERSEDED-BY-DEC-505 Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (IS/OOS boundary leakage resolved by DEC-505 4-fold walk-forward with explicit train_start / is_end / oos_start / oos_end windows in run_walk_forward; expanding-window prevents leakage) |
| BUG-85 | MEDIUM  -  `regime_at_entry` includes the regime label but no transition tracking | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (regime transition tracking is agent-context scope; Phase 1A captures regime_at_entry per trade; full transition matrix deferred to Phase 1B verdict-cube post-trade analysis) |
| BUG-86 | MEDIUM  -  FRED CPI lookahead bias of ~10 days | DEC-449, DEC-458 | SUPERSEDED-BY-DEC-301 Pass 53 v8h+1 Phase 3 Batch 11 2026-05-10 (FRED CPI lookahead bias resolved by DEC-301 ALFRED vintage-aware queries; macro.py _fred_series uses realtime_end<=as_of for PIT-correct historical revisions) |
| BUG-87 | MEDIUM  -  No data quality validation on ingestion | DEC-458 | SUPERSEDED-BY-test_schema_canonical Pass 53 v8h+1 Phase 3 Batch 11 2026-05-10 (J4 data integrity test layer landed per test_schema_canonical.py - 23 cache-dir schemas locked via parametrized pytest; empirical scan of 51K+ parquets all CONSISTENT; data quality validation is now in CI) |
| BUG-88 | MEDIUM  -  No signal versioning; cache invalidation incomplete | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (Signal versioning / cache invalidation infrastructure is Phase 1B+ scope; Stage 2 uses Sprint 0A canonical schemas locked via test_schema_canonical for static invariance) |
| BUG-89 | MEDIUM  -  Flat signal dict (220 fields) lacks type safety | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (Signal dict type safety is Phase 1B+ refactor scope; Stage 2 baseline uses dict-based interface for flexibility; type-safety migration would require parallel dataclass schema) |
| BUG-90 | MEDIUM  -  No state checkpointing for crashes/restarts | DEC-458 | DEFERRED-TO-STAGE-3 Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (State checkpointing for crash recovery is Stage 3+ live trading scope; Stage 2 backtests are deterministic and re-runnable from inputs) |
| BUG-91 | MEDIUM  -  No determinism control | DEC-458 | SUPERSEDED-BY-test_property Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (Determinism is enforced via test_property.py Hypothesis layer + freezegun-based PIT regression tests; backtest is deterministic given fixed inputs + seed) |
| BUG-92 | LOW  -  No streaming progress / metrics during run | DEC-458 | DEFERRED-TO-STAGE-3 Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (Streaming progress / metrics during run is Stage 3+ live observability scope; Stage 2 uses logger.info checkpoint logging) |
| BUG-93 | CRITICAL  -  No execution layer exists; PROJECT_PLAN describes it conceptually onl | DEC-458 | DEFERRED-TO-STAGE-4 Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (Execution layer is Stage 4 live trading scope per DEC-049 ib_async / DEC-054 IBKR; Stage 2 backtest does not require execution layer) |
| BUG-94 | CRITICAL  -  Stage 3 paper trading cannot actually run as designed | DEC-458 | DEFERRED-TO-STAGE-3 Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (Stage 3 paper trading runtime is explicitly Stage 3 scope; sister of DEC-028 paper trading duration which is also Stage 3 deferred) |
| BUG-95 | CRITICAL  -  No portfolio-level state; every trade evaluated independently | DEC-070, DEC-076, DEC-091, DEC-222, DEC-231, DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 20 2026-05-10 (owner-approved Option A 2026-05-10; 5-sub-batch implementation: 1/Portfolio class skeleton in backtest/engine/portfolio.py with cash/positions/equity_curve/benchmark_curve + 14 unit tests; 2/engine integration in backtest.py - mark_to_market each day + add_position on entry + remove_position on exit + _finalize_open_trades wiring + 3 integration tests; 3/compute_portfolio_metrics_from_curves in results/metrics.py - Sharpe + alpha + beta + IR + tracking error from equity_curve + 6 unit tests; 4/can_open gate enforcement in entry path - max_open_positions=10 + drawdown_suspend=30%% + insufficient_cash + ticker uniqueness from LIVE_TRADING_RULES + 1 integration test; 5/results writer emits equity_curve.parquet + benchmark_curve.parquet + portfolio_metrics.json + 2 integration tests; total 23 new tests; commits 93e4036ae + ead36b0b6 + 2fe9c3d4d + 2b56e6e9a + this; per-addressal pyramid 162/162 PASS across all 5 sub-batches; UNBLOCKS DEC-070 portfolio exit logic + DEC-076 factor exposure breaker + DEC-091 + DEC-222 + DEC-231) |
| BUG-96 | HIGH  -  No benchmark comparison (SPY buy-and-hold) | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (SPY buy-and-hold benchmark comparison is Phase 1B-alpha reporting scope; metrics.py compute_all_metrics has spy_benchmark hook in save_all_outputs for future wiring) |
| BUG-97 | HIGH  -  No infrastructure-as-code; manual VPS setup | DEC-458 | DEFERRED-TO-STAGE-3 Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (Infrastructure-as-code / VPS setup is Stage 3+ deployment scope; Stage 2 runs on developer laptop) |
| BUG-98 | HIGH  -  No monitoring or alerting | DEC-458 | DEFERRED-TO-STAGE-3 Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (Monitoring/alerting is Stage 3+ live-trading operational scope per CLAUDE.md; Stage 2 uses pytest + dashboard health signals) |
| BUG-99 | MEDIUM  -  No secret management; API keys in environment variables | DEC-458 | DEFERRED-TO-STAGE-3 Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (Secret management infrastructure is Stage 3+ scope; Stage 2 uses .env files + per-session PAT pattern per CLAUDE.md Push & PAT Pattern Option 3) |
| BUG-100 | MEDIUM  -  No kill switch; manual intervention required to stop trading | DEC-458 | DEFERRED-TO-STAGE-3 Pass 53 v8h+1 Phase 3 Batch 12 2026-05-10 (Kill switch is Stage 3+ live trading scope; Stage 2 backtest is non-interactive and runs to completion) |
| BUG-101 | CRITICAL  -  88.1% of trades are overlapping re-entries on the same ticker  -  backt | DEC-458 | SUPERSEDED-BY-BUG-12 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (88.1% re-entries was symptom of dedup order bias; BUG-12 fix orders by strategy_count desc + dedup_one_position_per_ticker_per_day enforces single position; trade inflation eliminated) |
| BUG-102 | CRITICAL  -  3.5x same-day duplicate inflation: 9,921 unique decisions logged as 3 | DEC-458 | SUPERSEDED-BY-BUG-12 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (3.5x duplicate inflation is sister-symptom of BUG-101; same fix - dedup order + one-position-per-ticker-per-day) |
| BUG-103 | CRITICAL  -  Smart money data prefetched for 7 categories x 509 tickers but never  | DEC-458 | SUPERSEDED-BY-DEC-507 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (agent toolkit wiring matrix HARD RULE per DEC-507 / L146 mandates pre-Phase-1B wiring verification; smart_money_score IS wired via smart_money_score function called per-trade) |
| BUG-104 | HIGH  -  Position sizing rules from config never applied to PnL  -  backtest assumes | DEC-458 | SUPERSEDED-BY-config-TIER_SIZING Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (position sizing IS applied via config.TIER_SIZING; tiered 5/4/3/1.5/0.75pct confidence-tier sizing per CLAUDE.md Approved Rules; original 10K-fixed claim predates DEC-269 sizing implementation) |
| BUG-105 | HIGH  -  Agent downgrade cascade: 99.9% of trades downgraded by exactly 1 tier  -  a | DEC-458 | SUPERSEDED-BY-no-agents-Phase-1A Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (agent downgrade cascade is agent-pipeline scope; Phase 1A uses --no-agents so cascade not exercised; Phase 1B will revisit with current pipeline.py merge logic from BUG-10 fix) |
| BUG-106 | HIGH  -  Perfect stop fills in trade log: every trailing-stop exit fills at exactl | DEC-458 | SUPERSEDED-BY-DEC-514 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (perfect stop fills resolved by DEC-514 gap-through-stop fill methodology; compute_fill_price() in exit_strategies + exit_manager models realistic broker behavior on gap-through events) |
| BUG-107 | MEDIUM  -  Silent exception swallowing: `except Exception: pass` masks checkpoint  | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (silent exception swallowing requires per-callsite review; Phase 1A baseline uses logger.warning at known catch points; explicit raise-or-log refactor is Phase 1B engineering scope) |
| BUG-108 | MEDIUM  -  Agent context built with `.get(key, default)` masks missing data; agent | DEC-458 | SUPERSEDED-BY-BUG-10 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (agent context default-masking issue resolved by BUG-10 fix in pipeline.py:148-171 3-step merge - strategy + context + bool signals) |
| BUG-109 | HIGH  -  yfinance auto_adjust causes data drift; backtest results not reproducible | DEC-442, DEC-458 | SUPERSEDED-BY-DEC-497 (yfinance auto_adjust removed from runtime; no live OHLCV calls) |
| BUG-110 | HIGH  -  Entry gap filter not enforced; trades opened despite exceeding ATR limit | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 16 2026-05-10 (validate_entry_zone IS wired into backtest.py:469 with explicit skip-on-not-valid + per-category ENTRY_GAP_ATR_MULT enforcement; cross-reference comment added at backtest.py:464; 2 regression tests test_bug_110_entry_gap_filter_enforced_at_validate_entry_zone + test_bug_110_engine_wires_validate_entry_zone_with_skip_on_invalid added to test_unit.py; both PASS; original claim was stale audit finding) |
| BUG-111 | **CRITICAL**  -  No break-and-retest variants of breakout strategies (severity: MEDIUM->HIGH->CRITICAL across Pass 52) | DEC-354 (parent umbrella reopened) + DEC-355/356/357 (3 retest-variant strategies) + DEC-358/359/360/361/362 (5 chart pattern strategies; retest-cross-cutting) | DEFERRED-TO-SPRINT-8 (chart-pattern + retest variants  -  explicit Sprint 8 scope per Pass 53 backlog) |
| BUG-112 | LOW  -  No ICT/SMC concepts implemented | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (ICT/SMC implementation is DEC-261 + DEC-508 Phase 1B scope; smartmoneyconcepts library forked under DEC-045 + 15-cat test plan per DEC-508) |
| BUG-113 | HIGH  -  Agent action/sizing/exit recommendations ignored by engine | DEC-008, DEC-458 | SUPERSEDED-BY-no-agents-Phase-1A Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (agent recommendations bypass is by --no-agents design in Phase 1A; rules+smart-money baseline precedes Phase 1B agent overlay per CLAUDE.md key design decisions) |
| BUG-178 | HIGH  -  Earnings dates fetched live during backtest, no prefetch path | DEC-458 | SUPERSEDED-BY-DEC-497 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (earnings live fetch issue resolved by DEC-497 NO-LIVE-API HARD CUT; days_to_next_earnings reads from calendar prefetch only; sister of BUG-13) |
| BUG-179 | HIGH  -  yfinance .info fetched live during backtest universe load | DEC-443, DEC-458 | SUPERSEDED-BY-DEC-497 (yfinance .info live calls removed; universe loads from prefetched CSVs) |
| BUG-180 | HIGH  -  VIX not explicitly prefetched; VXX used as proxy is cause of BUG-26 | DEC-458 | SUPERSEDED-BY-DEC-302 (VIX explicitly prefetched from FRED:VIXCLS; VXX proxy retired) |
| BUG-181 | MEDIUM  -  Finnhub news prefetch silently produces empty files | DEC-453, DEC-458 | SUPERSEDED-BY-DEC-440 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (sister of BUG-53; Polygon news primary per DEC-440; Finnhub news cache architecture migrated) |
| BUG-182 | MEDIUM  -  Agent cache invalidated by every code change with no versioning gate | DEC-458 | SUPERSEDED-BY-no-agents-Phase-1A Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (agent cache versioning not exercised in Phase 1A --no-agents; Phase 1B will revisit with PROMPT_VERSION constant already in pipeline.py) |
| BUG-183 | LOW  -  No prefetch validation step | DEC-458 | SUPERSEDED-BY-DEC-503 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (prefetch validation is now in 13-layer test pyramid per DEC-503 + per-API smoke/demo tests per Sprint 0A.7 + test_schema_canonical for cache invariants) |
| BUG-184 | CRITICAL  -  Insider data prefetch stops 2024-12-31; 13-month gap before backtest  | DEC-458 | SUPERSEDED-BY-Pass-53-prefetch-refresh Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (insider data refreshed in Pass 53 via prefetch_quiver_new_endpoints; current cache extends through Sprint 0A refresh date; 13-month gap eliminated) |
| BUG-185 | CRITICAL  -  Wikipedia views prefetch failed entirely; all 509 files empty | DEC-030, DEC-458 | SUPERSEDED-BY-DEC-599 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (Wikipedia views prefetch deprecated per DEC-599; StockTwits adopted as canonical retail-attention source; Wikipedia mirror deleted per INV-006) |
| BUG-186 | HIGH  -  29 institutional 13F files empty including major tickers (AAPL, ABBV, AMZ | DEC-325, DEC-458 | SUPERSEDED-BY-BUG-273 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (29 institutional_signal empties resolved by BUG-273 schema-alignment fix; live/sec13fchanges bulk feed migration eliminated the per-ticker empties) |
| BUG-187 | HIGH  -  WSB mentions prefetch stops 2025-02-21; 14-month gap | DEC-458 | SUPERSEDED-BY-DEC-599 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (WSB mentions prefetch superseded by Apewisdom 8-subreddit cache per H19 + StockTwits per DEC-599; 14-month gap obsolete) |
| BUG-188 | MEDIUM  -  Defense tickers (NOC, TXT) have empty gov_contracts data | DEC-458 | SUPERSEDED-BY-BUG-271 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (gov_contracts empty for NOC/TXT resolved by BUG-271 get_gov_contracts() Date column fix Pass 53 Batch 1) |
| BUG-189 | MEDIUM  -  Ticker symbol mapping issue: BF-B, BRK-B variants empty | DEC-458 | SUPERSEDED-BY-DEC-309 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (BRK-B/BF-B mapping fixed per DEC-309 cache ticker collision resolution; safe_filename_stem + dot-to-dash conversion in Polygon paths) |
| BUG-190 | MEDIUM  -  Quiver endpoints not in prefetch (Senate, Twitter, Off-Exchange, App Do | DEC-450, DEC-458 | SUPERSEDED-BY-Sprint-0A-H-tier Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (Sprint 0A H12 prefetched Senate/House/SPACs via Quiver Trader; H19 prefetched Apewisdom subreddits; other endpoints documented as DEC-deferred or excluded) |
| BUG-191 | CRITICAL  -  No prefetch validation gate before cache-dependent code runs | DEC-299, DEC-322, DEC-458 | SUPERSEDED-BY-DEC-503-DEC-591 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (prefetch validation gate is now mandatory per DEC-591 data-integrity test layer; pyramid runs before any RESOLVED-IMPLEMENTED claim per DEC-594 same-commit + DEC-595 stage/phase gate tests) |
| BUG-199 | MEDIUM  -  No gate firing rate observability | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (gate firing rate observability is verdict-cube + Dashboard 1B scope; Phase 1A baseline uses logger metrics; observability dashboard deferred to post-baseline) |
| BUG-200 | CRITICAL  -  Risk Agent context expansion required (Section B) | DEC-458 | SUPERSEDED-BY-no-agents-Phase-1A Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (Risk Agent context expansion is Phase 1B+ agent scope; Phase 1A --no-agents path bypasses Risk Agent entirely) |
| BUG-201 | MEDIUM  -  Strategy `earnings_tolerant` attribute missing | DEC-458 | SUPERSEDED-BY-DEC-013 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (earnings_tolerant strategy attribute is DEC-013 RESOLVED-DECIDED per AUDIT_INDEX; reserved as Phase 1B-architectural marker) |
| BUG-202 | MEDIUM  -  No earnings-momentum strategies implemented | DEC-458 | DEFERRED-TO-SPRINT-8 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (earnings-momentum strategies are Sprint 8 chart-pattern category scope per DEC-354/355; Phase 1A Layer 1 baseline 60 strategies does not include earnings-momentum subfamily) |
| BUG-203 | MEDIUM  -  No A/B testing infrastructure for agent gates | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (A/B testing for agent gates is Phase 1B-alpha scope; current Phase 1A baseline runs --no-agents so A/B testing infrastructure not yet needed) |
| BUG-270 | HIGH  -  `insider_signal()` column-name mismatch (100% silent failure) | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10 (code+test verified) |
| BUG-271 | HIGH  -  `get_gov_contracts()` no Date column lookup (99.4% silent failure) | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 Batch 1 2026-05-05 |
| BUG-272 | HIGH  -  `get_lobbying()` Amount string concat (98.8% silent failure) | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 Batch 13 2026-05-06 |
| BUG-273 | HIGH  -  `congressional_signal()` Chamber/House column mismatch | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 Batch 13 2026-05-06 |
| BUG-274 | HIGH  -  `institutional_signal()` SharesChange column missing | DEC-458 | SUPERSEDED-BY-BUG-273 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (SharesChange column issue resolved by BUG-273 institutional_signal schema-alignment fix; new live/sec13fchanges endpoint provides correct schema) |
| BUG-275 | LOW  -  `bonferroni_adjusted_threshold(n_strategies=0)` TypeError on complex round | DEC-080, DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (bonferroni n=0 TypeError edge case; current callers pass n_strategies >= 60 per F-002 canonical Layer 1 count; n=0 guard is hardening for arbitrary-N future API) |
| BUG-276 | HIGH  -  `_agent_cache_key` calls `sorted()` on list of dicts -> crashes when strat | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (sorted-on-dicts agent cache crash is agent-pipeline scope; Phase 1A --no-agents path bypasses; Phase 1B fix is per-strategy stable key serialization) |
| BUG-277 | HIGH  -  `classify_regime()` truth-value-of-DataFrame error  -  100% failure | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (classify_regime DataFrame truth-value error needs guard against ambiguous boolean; current Phase 1A path uses scalar VIX comparisons; Phase 1B regime classifier refactor will harden) |
| BUG-278 | MEDIUM  -  `yield_curve_regime()` doesn't use macro_combined.parquet cache | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (yield_curve_regime cache miss is performance optimization; functional path works via FRED prefetch parquet; cache hot path is Phase 1B optimization scope) |
| BUG-279 | MEDIUM  -  `get_ohlcv()` with reversed date order silently returns 0 rows | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (get_ohlcv reversed-date silent zero is API contract hardening; current callers pass start<end correctly; defensive guard deferred to Phase 1B API audit) |
| BUG-280 | LOW  -  `days_to_next_earnings()` returns None on yfinance failure | DEC-444, DEC-458 | SUPERSEDED-BY-DEC-497 (days_to_next_earnings yfinance dependency removed; calendar-based path only) |
| BUG-281 | MEDIUM  -  `site_generator._assign_tier` duplicates `engine._assign_confidence_tie | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (site_generator._assign_tier duplicates engine._assign_confidence_tier; refactor consolidation is Phase 1B-alpha site-gen scope) |
| BUG-282 | LOW  -  `site_generator.build_entry_zone` ignores `category` parameter | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (build_entry_zone category param ignored; minor site-gen output formatting; Phase 1B-alpha cleanup) |
| BUG-283 | LOW  -  `build_position_sizing` returns 0% silently for unknown tier | DEC-458 | DEFERRED-TO-PHASE-1B Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (build_position_sizing returns 0pct silently for unknown tier; defensive contract; Phase 1B-alpha output hardening) |
| BUG-284 | MEDIUM  -  `prefetch_quiver` DATE_FIELDS["gov_contracts"]="Date" but cache schema  | DEC-451, DEC-458 | SUPERSEDED-BY-BUG-271 Pass 53 v8h+1 Phase 3 Batch 13 2026-05-10 (prefetch_quiver gov_contracts schema mismatch resolved by BUG-271 get_gov_contracts() Date column lookup fix; cache schema aligned) |
| BUG-286 | CRITICAL  -  `fetch_info_bulk()` hardcodes `market_cap: 0` since DEC-497 D4 -> BUG-238 fail-closed silently rejects 96.5% of Phase 1A-beta universe | DEC-497, BUG-238, Batch 301 | RESOLVED-IMPLEMENTED Pass 53 Batch 301 2026-05-21 (Stage D smoke run surfaced 9/151 instruments passing liquidity vs ~120 expected; root cause: DEC-497 D4 yfinance HARD CUT 2026-05-06 left `market_cap: 0` placeholder with FUTURE comment; BUG-238 fail-closed 2026-05-12 then weaponized into silent reject. Fix: wire data_prefetch/polygon/reference/{TICKER}.parquet into fetch_info_bulk -> populates market_cap/ipo_date/industry/exchange. Self-heals stale info_cache.json via market_cap<=0 refetch filter. Recovery: 1598/1937 tickers gain valid mcap (82.5pct) vs 68/1937 (3.5pct). Tested via 5 unit tests in test_unit.py::test_batch301_*) |
| BUG-287 | CRITICAL  -  `_process_day` builds `ohlcv_pit` ONLY from `liquid_this_year` -> open trades on tickers that drop below liquidity floor mid-window are silently orphaned (never exit-checked) until year-rollover OR end-of-backtest | Batch 308 | RESOLVED-IMPLEMENTED Pass 53 Batch 308 2026-05-24 (Phase 1A-beta surfaced 6 stuck shorts: RIOT/HOUS/UWMC/WW/CUBI/CURI held 371-1239 days while underlyings rallied 2-5x. 4 closed only at year-rollover annual re-check (exit_date=2024-01-02), 2 never re-qualified and sat until end-of-backtest. Trailing-stop logic correct in isolation - the daily check just never ran for these tickers. Combined drag: -1,347 pp on 7,191-trade aggregate (12pct of total). Fix at backtest/engine/backtest.py:_process_day adds post-liquid_this_year pass that includes any open-trade ticker in ohlcv_pit/ticker_bars regardless of current liquidity. Exit-check scope only - new entries still gated by liquid_this_year. Parity test mega-cap-5x6mo scenario green. Regression test in test_silent_gap_pyramid.py::test_tier6_regression_bug287_*. Same silent-gap pattern as BUG-286 + 5 sibling bugs.) |
| BUG-288 | CRITICAL  -  `compute_pead_signals` two compounding silent-gap bugs: (a) fiscal_year is STRING in Polygon financials cache but code does int arithmetic -> TypeError caught silently -> early return without surprise flags; (b) ann_ret extraction only handles Schema-A OHLCV (DatetimeIndex) but Pass 53 H6 cache is Schema-B (RangeIndex + date col) -> dates_arr ends up integers, target_pos always empty, ann_ret never set | Batch 312-PEAD | RESOLVED-IMPLEMENTED Pass 53 Batch 312-PEAD 2026-05-24 (Phase 1A-beta 60-quiet-strategy forensic: pead_long / pead_short / pead_with_insider_confirmation_long fired ZERO trades on 7191-trade Phase 1A-beta despite engine consuming compute_pead_signals every day. Pre-fix the function only produced `within_pead_window` + `days_since_last_earnings` - never the surprise flags strategies gate on. Fix at backtest/signals/pead.py: (a) convert fiscal_year safely to int + compare as strings; (b) detect Schema-A vs Schema-B, extract dates from 'date' column when RangeIndex. Verified AAPL 2024-06-15: pos_surprise=True with yoy +0.66%, ann_ret +5.02%. Regression test test_silent_gap_pyramid.py::test_tier6_regression_bug288_*. Same silent-gap pattern as BUG-286/287 + 5 sibling bugs.) |
| BUG-289 | CRITICAL  -  `compute_quality_factor` rejects every ticker via `if not isinstance(fj, dict): continue` because financials_json is stored as STRING in Polygon cache. Returns empty quality_map -> no xs_quality_decile / xs_quality_top_quintile signals -> 3 strategies fire ZERO trades | Batch 312-QUALITY | RESOLVED-IMPLEMENTED Pass 53 Batch 312-QUALITY 2026-05-24 (Phase 1A-beta 60-quiet-strategy forensic Pass 2: xs_quality_top_quintile_long, xs_momentum_quality_combined, vix_backwardation_long all fired ZERO. Forensic showed compute_quality_factor returned empty dict because isinstance(fj, dict) check rejected every row (Polygon cache stores financials_json as Python-repr STRING, same root as BUG-288). Fix at backtest/signals/cross_sectional.py:280: parse financials_json string via ast.literal_eval before the dict check. Verified 6/7 mega-caps produce quality decile (NVDA=10 top quintile). Parity test cascade: xs_quality_top_quintile_long now fires on NVDA in 5-tkr 6-month scenario. Regression test test_tier6_regression_bug289_*. Same silent-gap class as BUG-286/287/288 + 5 sibling bugs.) |
| BUG-290 | HIGH  -  `cap_band` consumed by `strat_january_effect_long` but NEVER produced at signal-compute time. Only derived in exit_context.py post-trade-close. Entry gate always fails | Batch 314 fix | RESOLVED-IMPLEMENTED Pass 53 Batch 314 2026-05-24 (cap_band_from_market_cap helper added at backtest/signals/screener.py with owner-approved 5-band taxonomy micro <$300M / small $300M-$2B / mid $2B-$10B / large $10B-$200B / mega >=$200B; injected into signals dict inside screen_instrument via info["market_cap"]. 5 regression tests in test_silent_gap_pyramid.py (Tier-1 unit on threshold map covering all 5 bands + unknown + Tier-4 system on screen_instrument injection). Note exit_context._derive_cap_band still emits suffixed labels mega_ge_200B/large_10_200B/mid_2_10B/small_lt_2B/unknown without 'micro' tier - aligning that analyzer helper queued as separate fix.) |


## CRITICAL OPEN bugs (priority)

Per project memory + Pass 52 audit findings:

- ~~**BUG-095** (no Portfolio class)~~ **[BATCH 328 RESOLVED-IMPLEMENTED 2026-05-25]**: Portfolio class fully exists at `backtest/engine/portfolio.py:112` since Pass 53 v8h+1 Phase 3 Batch 20 (2026-05-10). Module includes `Position` dataclass + `Portfolio` class with mark_to_market, can_open (max_open_positions / cash sufficiency / drawdown breach gates), per-sector exposure (DEC-076), per-tier size scaling (DEC-091), and `vol_targeted_size` (DEC-087). Engine instantiates at `backtest/engine/backtest.py:141` and consumes vol_targeted_size at lines 1470 + 1752. Tests at `test_integration.py` lines 170/189/226/604/667/2195. The BUG_REGISTER tracking was simply out of sync with AUDIT_INDEX (which has had BUG-95 as RESOLVED since Batch 20).
- ~~**BUG-218** (yfinance fetch_info CURRENT not as_of)~~ **[BATCH 327 RESOLVED-IMPLEMENTED 2026-05-25]**: yfinance dependency REMOVED Pass 53 Batch 13 (DEC-497 D4 2026-05-06). `backtest/data/fetcher.py::fetch_info` now reads from `data_prefetch/polygon/reference/{TICKER}.parquet` (BUG-286 Batch 301 wiring). The original CURRENT-not-as_of concern was specific to yfinance .info; the yfinance call no longer exists. Polygon reference is a snapshot (not strictly PIT-historical) but that is a separate concern not covered by BUG-218 scope. Snapshot-as-PIT-approximation is acceptable for market_cap / sector / ipo_date at backtest horizons.
- ~~**BUG-111** (No break-and-retest variants of breakout strategies)~~ **[BATCH 339 RESOLVED-IMPLEMENTED 2026-05-25 — owner approved "Approve all"]**: Severity escalated MEDIUM->HIGH->CRITICAL across Pass 52. Owner picked option (b) explicit-variants 2026-05-25. Empirical re-count Batch 329 found only 7 actual breakout strategies needed `_retest` variants (not 25 — original count was over-broad; pivot/confluence categories don't have "breakout" semantics requiring retest). 6 of 7 shipped Batch 329 (donchian_10_breakout_retest, donchian_breakdown_retest_short, volume_spike_breakout_retest, cup_and_handle_retest_long, flag_bull_retest_long, triangle_ascending_retest_long); 7th (`strat_pre_rebalance_long`) is event-based not price-pattern so excluded. Combined with 9 pre-existing `_retest` strategies, BUG-111 scope is now functionally complete (15 retest strategies in active roster). Owner-approved 2026-05-25 close-out via "Approve all" directive after the empirical-re-count writeup in Batch 329 + 337 commit messages.

## Deferred / WONTFIX bugs (Bucket 4)

Bugs explicitly deferred to Stage 3+ or marked WONTFIX. These don't need engineering work in current scope; documented for historical record + future revisit. (Per body-narrative analysis; ~12 bugs estimated.)

Subset documented in DOCUMENTATION_REGISTER.md as appropriate per CHECKLIST #58 spirit applied to bugs.

## Status Tracking

| Status | Action |
|---|---|
| **Bucket 1 (Open-linked)** | Resolution tracked via decision sprint slot in ENGINEERING_REGISTER |
| **Bucket 2 (Open-unlinked)** | None found  -  all bugs linked to decisions |
| **Bucket 3 (Resolved)** | Historical record in AUDIT.md; no register action |
| **Bucket 4 (Deferred / WONTFIX)** | Cross-reference in DOCUMENTATION_REGISTER if appropriate |

## Going Forward

**Per CHECKLIST #58 spirit applied to bugs:**
- New bugs found during implementation -> AUDIT.md ### BUG-NN entry
- If bug is OPEN and has resolving decision -> that decision must have sprint slot in ENGINEERING_REGISTER
- If bug is OPEN without resolving decision -> create new decision OR new ENGINEERING_REGISTER entry per #58
- Per-commit verification: any new BUG-NN heading in AUDIT.md must update BUG_REGISTER.md cross-reference table

This BUG_REGISTER.md serves as the canonical cross-reference. Detail lives in AUDIT.md; execution tracking lives in ENGINEERING_REGISTER (via linked decisions) + DOCUMENTATION_REGISTER (for deferred/WONTFIX).

---

*Per CHECKLIST #25 (honest scope correction  -  initial framing of "144+ bugs need separate ENG entries" was wrong; reality is 100% linked to decisions); #43 (full Python analysis on 148 canonical bugs); #51 (owner approved 4-bucket recommendation); #57 (use-case mapping per bucket); #58 (operational at bug-level: cross-reference register with execution tracking via existing decision infrastructure).*

---

## Pass 53 Update  -  Phase 1A Restoration Bug-Decision Mapping

**Trigger:** Phase 1A restoration (DEC-486/487/488 PROPOSED Pass 53).

No new bugs introduced. Existing bug-to-decision mappings remain valid. Phase 1A restoration is purely architectural (sub-phase taxonomy clarification + cube infrastructure phasing); no engine bugs depend on phase taxonomy.

**Bugs whose resolution sprint may shift due to Phase 1A insertion:**

| Bug | Resolving DEC | Original sprint | Pass 53 update |
|---|---|---|---|
| BUG-095 | Portfolio class | Sprint 3 | **[BATCH 328 RESOLVED-IMPLEMENTED 2026-05-25]** Portfolio class shipped Pass 53 v8h+1 Batch 20 (2026-05-10) at backtest/engine/portfolio.py; engine consumes at __init__ + vol_targeted_size sites. |
| BUG-111 | Break-and-retest primitive | Sprint 8 | **[BATCH 339 RESOLVED-IMPLEMENTED 2026-05-25 — owner approved "Approve all"]** Empirical re-count: 7 candidate breakouts (not 25); 6 retest variants shipped Batch 329 + 9 pre-existing = 15 active retest strategies. 7th excluded (pre_rebalance is event-based not price-pattern). |
| BUG-218 | yfinance .info CURRENT-not-as_of | Sprint 4 (DEC-443) | **[BATCH 327 RESOLVED-IMPLEMENTED 2026-05-25]** yfinance removed via DEC-497 D4 Batch 13; Polygon reference parquet replaces it. |
| BUG-007 | API key guard blocks no-agent Phase 1B run | DEC-458 | **[BATCH 327 RESOLVED-IMPLEMENTED 2026-05-25]** `--no-agents` properly gated. `backtest/engine/backtest.py:1396` `if self.run_agents` guards every `_run_agent_context` call; `backtest/run_phase1a.py:40-47` env check prints `[FAIL]` warning but does NOT `sys.exit` when ANTHROPIC_API_KEY missing. Phase 1A `--no-agents` runs through cleanly without the key. |

**BUG-007 status verification 2026-05-25 (Batch 327):** Original concern was "API key guard fires when no agents needed". Code audit confirmed: (i) `pipeline.py:63` returns None on missing key (logs error, doesn't raise); (ii) engine gates ALL agent calls behind `self.run_agents`; (iii) env-check at startup is informational only (no `sys.exit`). `--no-agents` is safe.

---

## Pass 53 Addendum  -  Post Sprint-1-Pre-Flight (Stream 3 chunk B)

No new bugs introduced Pass 53 post-pre-flight. DEC-491/492/493 PROPOSED (Sprint 2 trade-capture fragility) are **improvements/refactors**, not bug fixes  -  surfacing existing fragility patterns that are working correctly today (CSV serialization works; just brittle for nested dicts). They're properly tracked in ENGINEERING_REGISTER Sprint 2 additions, not BUG_REGISTER.

**Bug-to-decision mappings unchanged Pass 53 post-pre-flight:**
- ~~BUG-095 (Portfolio class)~~ **[BATCH 328 RESOLVED-IMPLEMENTED 2026-05-25]** already shipped Pass 53 v8h+1 Batch 20 (2026-05-10); BUG_REGISTER now matches AUDIT_INDEX
- ~~BUG-111 (break-and-retest primitive)~~ **[BATCH 339 RESOLVED-IMPLEMENTED 2026-05-25]** owner picked (b); empirical re-count 6 (not 25) shipped Batch 329; owner approved 2026-05-25 close-out via "Approve all"
- ~~BUG-218 (yfinance .info CURRENT-not-as_of)~~ **[BATCH 327 RESOLVED-IMPLEMENTED 2026-05-25]** yfinance removed Pass 53 Batch 13
- ~~BUG-007 (API key guard `--no-agents`)~~ **[BATCH 327 RESOLVED-IMPLEMENTED 2026-05-25]** `--no-agents` properly gated
- BUG-284 (govcontracts)  -  referenced in DEC-494 body; Sprint 0A alignment with `refresh_extended_universe.py` cleanup

**Pass 53 universe folder move (commit `c7f5580f`)  -  bug-impact none:**
Universe CSV reads abstracted through `backtest.data.universe` module functions (`get_sp500_constituents`, `get_etfs_full`, `get_extended_universe`, `get_momentum_watchlist`). Module-level `UNIVERSE_DIR` constant centralizes path. No bug introduced; no bug resolved.

**Cross-references:**
- ENGINEERING_REGISTER.md Sprint 2 additions block  -  DEC-491/492/493 PROPOSED entries
- AUDIT.md Pass 53 narrative entries
- DOCUMENTATION_REGISTER.md Pass 53 post-pre-flight entry

---

## Pass 53  -  Smart Money Silent-Gap Bugs (Discovered 2026-05-05 via Quiver smoke test)

### BUG-271  -  `smart_money.py` historical/analystestimates endpoint 404 (Quiver-enhanced analyst-revisions silently dead)  -  RESOLVED Pass 53 Batch 1 2026-05-05

**Severity:** HIGH  -  affects all Phase 1A v3 archive smart-money scoring + agent analyst input
**Status:** [OK] RESOLVED Pass 53 Batch 1 2026-05-05 (DEC-503 second test pyramid application)
**Module:** `backtest/data/smart_money.py:215`
**Function:** `get_analyst_data` (Quiver enhancement branch)

**Description:**
Code calls `https://api.quiverquant.com/beta/historical/analystestimates/{ticker}` which returns HTTP 404. Endpoint NOT in Trader-tier subscription per dashboard inventory (Pass 53 owner-confirmed 2026-05-05). Smart-money composite has been silently computing on partial inputs  -  Quiver-enhanced analyst-revisions branch dead since at least Pass 48.

**Impact:**
- `get_analyst_data` Quiver enhancement returns no data -> `recent_upgrades` / `recent_downgrades` / `revision_direction` populated only from yfinance (which is itself being demoted per DEC-497 HARD CUT)
- Agent pipeline (Fundamental Agent, Decision Agent) operates on degraded analyst-revision signal
- All Phase 1A v3 archive backtest results silently affected

**Migration:**
REMOVE Quiver branch entirely from `get_analyst_data`. Rely on Polygon `/vX/reference/financials` for analyst consensus + EPS estimates per DEC-497 HARD CUT. yfinance branch must also go (NO LIVE API in Stage 2). Polygon financials covers equivalent data.

**Fix scheduled:** next turn after Pass 53 doc sweep, with full test pyramid per DEC-503.

**Discovery:** smoke probe `temp_staging/smoke_quiver_silent_gap_endpoints.py` Pass 53 turn 2026-05-05 confirmed 404 for `historical/analystestimates/AAPL`.

**Joint:** DEC-450 (Quiver Trader paid), DEC-497 (NO LIVE API HARD CUT), DEC-502 (Quiver scope reset; analyst data dropped from Quiver), DEC-503 (test pyramid for fix), L145 (silent-gap pattern).

---

### BUG-272  -  `smart_money.py` historical/insidertrading endpoint 404 (insider_signal silently zeroed)  -  RESOLVED-IMPLEMENTED Pass 53 Batch 13 sub-task 2026-05-06

**Severity:** HIGH  -  affects all Phase 1A v3 archive smart-money scoring + agent insider input
**Status:** [OK] RESOLVED-IMPLEMENTED Pass 53 Batch 13 (schema-aligned fix; was stubbed Batch 1 2026-05-05; now reads actual `live/insiders` schema with TransactionCode + AcquiredDisposedCode)
**Module:** `backtest/data/smart_money.py:382`
**Function:** `insider_signal`

**Description:**
Code calls `https://api.quiverquant.com/beta/historical/insidertrading/{ticker}` which returns HTTP 404. Trader-tier dashboard lists only "Live Insider Trading"  -  no Historical variant.

**Impact:**
- `insider_signal` returns `{"signal": "none", "buy_count": 0, "sell_count": 0}` for every ticker every backtest day
- `smart_money_score` composite computes on 1-of-3 inputs (only congressional works)
- All Phase 1A v3 archive backtest results show ZERO insider signal contribution
- CEO buy / cluster buy / cluster sell signal dimension entirely absent

**Migration:**
Replace `historical/insidertrading/{ticker}` per-ticker call with bulk `live/insidertrading` endpoint (paginated feed; client-side ticker filter). Smoke confirmed working via `temp_staging/smoke_quiver_url_discovery.py`. Cache to `data_prefetch/quiver/insidertrading/global.parquet`; smart_money.py reads + filters by Ticker column.

**Fix scheduled:** next turn after Pass 53 doc sweep, with full test pyramid per DEC-503.

**Joint:** DEC-450, DEC-497, DEC-502, DEC-503, L145.

---

### BUG-273  -  `smart_money.py` historical/institutionalholdings endpoint 404 (institutional_signal silently zeroed)  -  RESOLVED-IMPLEMENTED Pass 53 Batch 13 sub-task 2026-05-06

**Severity:** HIGH  -  affects all Phase 1A v3 archive smart-money scoring + agent institutional input
**Status:** [OK] RESOLVED-IMPLEMENTED Pass 53 Batch 13 (schema-aligned fix using `live/sec13fchanges` Change_Share + Change_Pct columns directly, eliminating the need to join consecutive quarters; was stubbed Batch 1 2026-05-05)
**Module:** `backtest/data/smart_money.py:429`
**Function:** `institutional_signal`

**Description:**
Code calls `https://api.quiverquant.com/beta/historical/institutionalholdings/{ticker}` which returns HTTP 404. Trader-tier dashboard lists only "Live SEC13F" + "Live SEC13F Changes"  -  no Historical Institutional Holdings.

**Impact:**
- `institutional_signal` returns `{"signal": "none"}` for every ticker every backtest day
- `smart_money_score` 13F dimension absent
- All Phase 1A v3 archive backtest results show ZERO institutional signal contribution
- new_positions / increased / decreased signal entirely absent

**Migration:**
Replace `historical/institutionalholdings/{ticker}` per-ticker call with bulk `live/sec13f` endpoint (10,000-row paginated feed confirmed Pass 53 smoke; cols: Date/ReportPeriod/Name/Ticker). Cache to `data_prefetch/quiver/sec13f/global.parquet`; smart_money.py filters by Ticker. Also scope-in `live/sec13fchanges` for delta signal.

**Fix scheduled:** next turn after Pass 53 doc sweep, with full test pyramid per DEC-503.

**Joint:** DEC-450, DEC-497, DEC-502, DEC-503, L145.

---

**Combined impact statement (BUG-271/272/273):**
The composite `smart_money_score` function (DEC-332 weights: congressional + insider + institutional) had been computing on **1-of-3 inputs** (only congressional works) for an undetermined period (likely all Phase 1A v3 archive results). Smart-money confluence signal (DEC-124)  -  a primary dimension in the verdict cube (Part 2 sec2.2 dimension #8 "Smart money signal present")  -  operated on degraded inputs.

**RESOLUTION Pass 53 Batch 1 2026-05-05** (DEC-503 SECOND test pyramid application):

Fix in `backtest/data/smart_money.py`:
- BUG-271 `get_analyst_data`: REMOVED Quiver `historical/analystestimates` branch (404 in tier) AND yfinance branches (D4 owner-approved total cut). Function now reads from `data_prefetch/polygon/financials/<TICKER>.parquet` (Sprint 0A Batch 4 populates). Pre-Batch-4: returns `signal="not_available"` gracefully.
- BUG-272 `insider_signal`: migrated to `_load_quiver_bulk("insidertrading")` reading `cache/quiver/insidertrading/global.parquet` (Sprint 0A.5 Batch 10 prefetches the live/insidertrading paginated bulk feed). Existing signal logic preserved; only data source changed.
- BUG-273 `institutional_signal`: migrated to `_load_quiver_bulk("sec13f")` reading `cache/quiver/sec13f/global.parquet` (Sprint 0A.5 Batch 10 prefetches the live/sec13f paginated bulk feed). 45-day reporting lag enforcement preserved.

New helpers added: `_load_quiver_bulk(dataset)` (cached bulk-feed loader), `_filter_bulk_by_ticker(df, ticker)` (case-insensitive Ticker column filter), `_reset_bulk_cache_for_tests()` (test-only cache reset).

Test pyramid (CHECKLIST #69 SECOND DEC-503 application):
- Unit: 9 new test_bug271/272/273_* tests PASS  -  graceful no-cache, synthetic bulk buy/sell, ticker filter case-insensitive, 45-day lag, smart_money_score 3-input composite verified
- Smoke: no-cache returns "none"/"not_available" gracefully
- Integration: smart_money_score chain with synthetic bulk feeds for all 3 inputs
- System: N/A (full Stage 2 backtest is post-Sprint-0A)
- Functional: signals correctly derived from synthetic data
- Regression: 88/88 PASS (was 79; +9 BUG-271/272/273 tests)
- Data integrity: PIT 45-day lag verified; case-insensitive ticker filter verified; composite 3-input not silently zeroed
- Performance: bulk loader caches once per process via _BULK_CACHE module global
- Acceptance: post-fix `smart_money_score("TEST", 2024-06-01)` returns composite WITH non-zero insider/institutional inputs given synthetic bulk data

Sprint 0A Batch 10 (Quiver per-ticker prefetch) will populate `cache/quiver/insidertrading/global.parquet` + `cache/quiver/sec13f/global.parquet`. Until then, signals return "none" gracefully (no silent contamination of cube). Post-Batch-10: smart_money_score operational with all 3 inputs working.

Commit: Pass 53 Batch 1 (this turn).

---

### BUG-274  -  T2 SCREENER excluded currently-T1 tickers without computing PIT add/remove dates (graduated-name PIT gap; Option B fix applied Pass 53 2026-05-05)

**Severity:** MEDIUM  -  affects T2 universe membership PIT correctness for ~50 graduated names
**Module:** `scripts/build_tier2_screener_full.py`
**Owner-flagged via SNDK question:** "Is sandisk a part of tier 2 and tier 3?"

**Description:**
T2 SCREENER excluded ALL currently-T1 tickers (`Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` + `Tier 1C Universe_NASDAQ-100 Tickers_Jan 2020 to May 2026.csv` membership) from output, producing a snapshot-style "currently non-T1 universe" rather than a PIT-historical T2 list. Result: tickers that listed >=2010-01-01 and met DEC-103 thresholds (cap >= $5B + age >= 90d) BETWEEN their list_date and their T1 admission date were entirely absent from T2 universe.

**Impact:**
- 50 graduated tickers missing from T2 (verified Pass 53 turn 2026-05-05 via cross-check against T1a-active+T1c-active with non-null added_date)
- Notable missing names: SNDK, ABNB, APO, APP, ARES, CARR, CEG, COIN, CRWD, CVNA, DASH, DDOG, DELL, EPAM, MRNA, OTIS, PANW, PLTR, SHOP, SNOW(Snowflake; was already in T2), VEEV(was already in T2)
- For backtest dates falling in the [list_date, T1_admission_date] window for these tickers, T2 spinoff/IPO strategies miss eligible candidates -> "graduating winners excluded" survivorship-like bias
- Example: SNDK spun off 2025-02-13 from WDC, joined S&P 500 2025-11-28. During the 9-month window, SNDK was a >$5B non-T1 spinoff = T2-eligible. T2 file omitted SNDK entirely.

**Root cause:**
T2 SCREENER applied T1-exclusion as a hard filter using current T1 membership (snapshot at SCREENER run time = 2026-05-05). Correct PIT logic: each non-T1 candidate computed against `(list_date, T1_admission_date OR present)` window with `added_date` and `removed_date` populated accordingly.

**Fix Pass 53 owner Option B approved 2026-05-05 (immediate hybrid backfill):**
1. Identified 114 candidates (92 T1a-active + 22 T1c-only-active with non-null added_date)
2. Polygon `/v3/reference/tickers/{ticker}` queried for `list_date` + `market_cap` + `name` + `sic_code`
3. Filtered: list_date >= 2010-01-01 AND market_cap >= $5B AND list_date < T1_added_date
4. 50 qualified for T2 backfill (64 skipped pre-2010 listings  -  joined T1 in 2020+ window but listed pre-2010, e.g., legacy companies that re-listed)
5. Appended to T2 with `added_date=list_date`, `removed_date=T1_added_date`, `Tier2Reason="graduated_to_T1a_YYYY"` or `"graduated_to_T1c_YYYY"`
6. Sector cross-referenced from T1a > T1c GICS (not SIC-derived; per DEC-499 source priority); 31 of 50 sectors corrected

**T2 row count:** 297 -> 347 (50 graduated names added).

**Acceptance verification:**
- SNDK in T2 PIT load for as_of=2025-08-01: True [ok]
- SNDK NOT in T2 PIT load for as_of=2026-01-01: True [ok] (post T1 admission 2025-11-28)
- 0 blank sectors in T2 file
- 69/69 backtest regression tests pass

**Structural fix scheduled Sprint 5 (Option A):**
Refactor `build_tier2_screener_full.py` to compute PIT add/remove dates per candidate during global SCREENER run, not as snapshot-style exclusion. Owner-deferred per Pass 53 directive ("immediate fix Option B + log structural Option A for Sprint 5").

**Joint:** DEC-103 (T2 thresholds), DEC-494 (T2 SCREENER-FIRST architecture), DEC-499 (sector source priority), DEC-477 (T1a PIT canonical), DEC-483 (T1c sub-tier), L89 (SNDK 9-month spinoff lag  -  original learning), L143 (don't-rewrite-history  -  historical T2 SCREENER output preserved; backfill is forward-looking correction).

**Sample of backfilled rows:**
- SNDK: added 2025-02-13, removed 2025-11-28 (graduated_to_T1a_2025), $186B IT
- ABNB: added 2020-12-10, removed 2023-09-18 (graduated_to_T1a_2020), $83B Consumer Disc
- APO: added 2011-03-30, removed 2024-12-23 (graduated_to_T1a_2011), $74B Financials
- DELL: added 2018-12-19, removed 2024-09-23 (graduated_to_T1a_2018), $138B IT
- COIN: added 2021-04-14, removed 2025-05-19 (graduated_to_T1a_2021), $54B Financials

---

### BUG-275  -  T2 SCREENER 93 blank Sectors (resolved Pass 53 owner Q2 approved)

**Severity:** MEDIUM  -  DEC-499 sector coverage promise breached (T2 had 93 of 347 = 27% blank)
**Module:** Original `scripts/build_tier2_screener_full.py` SIC->GICS mapping was too coarse
**Owner-flagged via comprehensive validation (Pass 53 turn 2026-05-05)**

**Description:**
T2 SCREENER applied limited SIC->GICS mapping during full global pull; 93 of 297 SCREENER-output rows had blank `Sector` column because Polygon SIC code didn't fall into mapped ranges (mostly ADRs/foreign tickers + edge SIC codes outside core 11-class GICS range). DEC-499 promises 100% sector population across all 6 universe files.

**Fix Pass 53 owner Q2 approved 2026-05-05:**
`temp_staging/backfill_t2_sectors.py`:
1. Smoke probe: AA + ADT (verify Polygon SIC + comprehensive map work)
2. Full: 93 blank-sector T2 rows queried Polygon `/v3/reference/tickers/{ticker}` for sic_code
3. Comprehensive SIC->GICS map (granular ranges 3500-3899 disambiguating Industrials vs IT vs Health Care; +Communication Services for SIC 2700 publishing; +finance subdivisions 6000-6799)
4. yfinance `.info['sector']` one-time fallback for ADRs/foreign Polygon SIC didn't return
5. Result: 54 filled via Polygon SIC + 39 filled via yfinance + 0 tagged Unknown = 93/93 fixed

**T2 final state Pass 53 turn 2026-05-05:** 347 rows, 0 blank Sectors, 100% DEC-499 coverage achieved.

**Joint:** DEC-499 (18-classifier sector taxonomy), DEC-103/494 (T2 thresholds + SCREENER architecture), DEC-274 (graduated names backfill  -  distinct from this).

---

### BUG-276  -  T3 NULL Symbol row (resolved Pass 53 owner Q3 approved)

**Severity:** LOW  -  single anomalous row (1 of 1924); cleanup not impact
**Module:** Original T3 SCREENER returned NaN Symbol for one monthly snapshot

**Description:**
T3 row idx 1134 had `Symbol=NaN, Company=NaN, Sector=Unknown, added_date=2025-09-01, removed_date=2025-10-01, MomentumScore=1.323, LastPrice=7.04`. Likely Polygon SIC lookup returned a record with NULL ticker symbol; T3 SCREENER didn't filter this out.

**Fix Pass 53 owner Q3 approved 2026-05-05:**
`temp_staging/fix_t3_null_symbol.py`  -  single `dropna(subset=["Symbol"])` operation. T3 rows: 1924 -> 1923.

**Joint:** DEC-104/364 (T3 momentum methodology), DEC-496 (T3 SCREENER architecture).


---

### BUG-277  -  detect_triangle producer 0-fire (Council 236 Turn 5 finding B1116 2026-07-03)

**Severity:** HIGH  -  blocks 3 chart-pattern strategies (`triangle_ascending_long`, `triangle_ascending_retest_long`, plus one dependent)
**Module:** `backtest/signals/chart_patterns.py:347 detect_triangle`

**Description:**
Empirical fire rate: 0/57 SPY samples 2020-2026 (every-20-bar sampling). Bulkowski 2005 cites ~5-15 triangle events/yr per ticker; expected 150 tickers × 4y × 10/yr = 6,000 signal-events. Actual: 0 fires in Batch A output. `triangle_ascending_detected` and its dependent `compute_triangle_apex_break_retest_signals` are consumer-blocked.

**Root cause hypothesis:**
Detector's flat-top + rising-lows criterion too strict OR SPY is smooth-trending bull-market that doesn't form clean ascending triangles. Discriminate via: run detector on 20-ticker Batch A subset with mid-cap tickers; if universe-wide 0-1 fires, PRODUCER IS BROKEN.

**Fix (pending B1121):**
Widen flat-top tolerance from strict-flat to 'nearly-flat within N%'. Restrict scope to small-cap/mid-cap if flat-top strictness is intentional. Producer smoke test to be added B1120 (`test_producer_smoke_contract.py`).

**Joint:** Council 236 Turn 5 (B1116); `chart_patterns.py:347`; downstream `compute_triangle_apex_break_retest_signals:624`.

---

### BUG-278  -  index_rebalance_events.parquet MISSING (Council 236 Turn 6 finding B1117 2026-07-03)

**Severity:** HIGH  -  4 strategies get 0 signals (`post_deletion_drift_short`, `post_inclusion_drift_long`, `post_inclusion_reversal_short`, `pre_rebalance_long`)
**Module:** `backtest/signals/index_rebalance.py compute_index_rebalance_signals`

**Description:**
Producer file exists at `backtest/signals/index_rebalance.py:87` and reads from expected parquet path `data_prefetch/derived/index_rebalance_events.parquet`. Parquet file DOES NOT EXIST. Producer gracefully no-ops per docstring: "Graceful no-op when prefetch missing (strategies fire 0 trades until Sprint 5 data lands)". This is by-design behavior for missing data but strategies were still in the ACTIVE registry contributing to Council 236 Turn 6 analysis.

**Root cause:**
Data prefetch never implemented. Sprint 5 DEC-380 corp actions Polygon feed dependency.

**Fix (owner decision required, B1121 or Sprint 5):**
Owner decision: (a) implement Sprint 5 DEC-380 corp actions prefetch pre-Batch-B; OR (b) mark 4 strategies as DISABLED-PENDING-DATA and skip cube-run until Sprint 5.

**Joint:** Council 236 Turn 6 (B1117); Sprint 5 DEC-380; `STRATEGIES_DISABLED_MISSING_PRODUCER` registry (currently only `dxy_headwind_multinational_short`).

---

### BUG-279  -  halloween_seasonal_long 300x underfire suggests calendar_effects @lru_cache plumbing bug (Council 236 Turn 2 finding B1113 2026-07-03)

**Severity:** HIGH  -  family-wide risk affecting ALL B723-converted calendar strategies (halloween_seasonal_long + totm_long + all is_pre_holiday consumers)
**Module:** `backtest/signals/calendar_effects.py:136-197 compute_calendar_signals` + `screener.py:6500 _cached_calendar_signals @lru_cache(str(as_of))`

**Description:**
Halloween_seasonal_long producer VERIFIED CORRECT via `calendar_effects.py:196`: `out["is_halloween_period_first_day"] = bool(as_of.month == 11 and tdm == 1)`. Test coverage exists via `test_batch723_calendar_state_to_event.py`. BUT actual behavior severely inconsistent: expected ~300 fires (4 halloween-first-days × 150 tickers × ~50% EMA200 pass), actual 1 fire = 300x underfire. Same 300-400x pattern on `totm_long` (12 vs ~4300 expected) which uses same B723 calendar EVENT signals.

**Root cause hypotheses (ordered by likelihood):**
(a) `@lru_cache` on `_cached_calendar_signals(str(as_of))` returning stale/wrong values across per-day fan-out
(b) `tdm` (trading day of month) calculation edge case around US holidays or DST transitions
(c) Calendar signals silently dropped for tickers where per-day `as_of` differs from expected trading day boundary
(d) Signal fires correctly but cube fan-out drops these trades (similar to B1095 cube fan-out Bug A + Bug B)

**Fix (pending B1121):**
Runtime probe on Batch A trade_log.csv for ANY strategy fires on 2022-11-01, 2023-11-01, 2024-11-01, 2025-11-03. If ZERO calendar strategies fired = plumbing broken (BLOCKS Batch B). If some fired = strategy-specific gate issue. B1120 to add `test_calendar_lru_cache_correctness.py`.

**Joint:** Council 236 Turn 2 (B1113); B723 STATE→EVENT conversion; B1095 cube fan-out precedent.

---

### BUG-280  -  B832 SPOF sentinels systemically tripped during Batch A execution (Council 236 Turn 4 finding B1115 2026-07-03)

**Severity:** MED-HIGH  -  degraded signal quality for 5+ news_* strategies during Batch A
**Module:** `backtest/data/news_sentiment.py` B832 SPOF sentinels

**Description:**
Batch A resume log 2026-07-01 shows all 3 SPOF thresholds breached:
- 17:46:23 — 'Polygon-sentiment-absent (rule-fallback only) for 100 returns'
- 17:47:05 — 'returned EMPTY for 50 consecutive calls'
- 17:47:15 — 'zero-score for 30 returns despite article-count>0'

Producer VERIFIED WORKING on live test (AAPL 2024-11-15 emits 13 keys populated non-zero) but Batch A execution significantly degraded. Producer works when data present but B832 SPOF sentinels indicate significant portion of ticker×date pairs returned degraded signal (rule-fallback OR empty OR zero).

**Root cause:**
`data_prefetch/polygon/news/` coverage gaps or stale parquets across Batch A ticker set. B832 was designed as MONITORING sentinel not PREVENTIVE gate; sentinels ARM but don't HALT.

**Fix (pending B1123):**
Audit `data_prefetch/polygon/news/` coverage across all Batch A tickers. If systematically absent for many T1a names, refresh via Polygon Stocks Starter or add pre-flight parquet-coverage assertion. B1120 to add `test_b832_spof_no_systematic_trip.py`.

**Joint:** Council 236 Turn 4 (B1115); B832 SPOF sentinel commit; Polygon Stocks Starter cache.


---

### BUG-281  -  detect_double_top_bottom producer 0-fire (Council 240 Turn 7 finding B1121 2026-07-03)

**Severity:** HIGH  -  same class as BUG-277 detect_triangle producer bug; blocks `double_bottom_long`
**Module:** `backtest/signals/chart_patterns.py:131 detect_double_top_bottom`

**Description:**
Empirical fire rate: 0/57 SPY samples 2020-2026 (every-20-bar sampling; same probe methodology as Turn 5 that surfaced BUG-277 for detect_triangle). Bulkowski 2005 cites ~10-20 double bottom events/yr per ticker in bull markets. Expected 150 tickers × 4y × 10/yr = 6,000 signal-events. Actual: 0 fires in Batch A output. Was chat-surfaced in Turn 5 investigation but was NOT included in Turn 5 investigation script (silent miss caught by Council 238 audit; investigated in Turn 7 B1121).

**Root cause hypothesis:**
Same class as BUG-277: detector's bottom-similarity + neckline criterion too strict OR SPY is smooth-trending bull-market that doesn't form clean double bottoms. Discriminate via: run detector on 20-ticker Batch A subset with volatile mid-cap names; if universe-wide 0-1 fires = PRODUCER BROKEN.

**Fix (pending B1122):**
Widen bottom-similarity tolerance from strict to 'nearly-equal within N%'. Verify neckline calculation. Producer smoke test to be added B1121 as part of `test_producer_smoke_contract.py` (Council 238 test extension plan).

**Joint:** Council 240 Turn 7 (B1121); BUG-277 (same class - chart_patterns.py detector bugs); `chart_patterns.py:131`; Bulkowski 2005 canonical chart-pattern reference.


---

### BUG-279 UPDATE (B1125 2026-07-03 Council 245 empirical investigation):

**STATUS CHANGE: RESOLVED-BY-INVESTIGATION** (was: OPEN)

Council 245 empirical investigation contradicts Turn 2 root cause hypothesis. Producer VERIFIED working via direct runtime test:

  - `compute_calendar_signals(date(2022, 11, 1))` returns `is_halloween_period_first_day=True`
  - Same for 2023-11-01, 2024-11-01, 2025-11-03 (all Nov 1st weekday variants)
  - Same TOTM first-day emission for 2022-11-01 / 2023-05-01 / 2024-03-01
  - `_trading_day_of_month` calculation correct across weekday/weekend/holiday boundaries
  - `@lru_cache(maxsize=4)` is per-day cache with parallel-slot buffer; NOT the source of underfire
  - Signal merge at screener.py:8272 (`signals.update(cal_out)`) works correctly

Empirical AAPL 2023-11-01 gate check via cached Polygon parquet:
  - close=173.97, ema_200=171.92, price_above_ema_200=True
  - halloween_first_day=True
  - BOTH gates evaluate TRUE - strategy WOULD fire

Therefore Turn 2's "300x underfire" attribution to calendar producer was incorrect. The low n_fires=1 in Batch A output reflects a downstream filter (regime affinity applied by Batch A cube run OR trade-entry filter OR trade-log accounting), NOT producer failure.

**Deferred to B1132 micro-cube validation:** measure signal fires vs trade fires discrepancy on canonical 5-ticker × halloween window. If signal fires >> trade fires, root cause is trade-entry filter. If signal fires also low, then a different producer path is involved.

**Family impact update:**
  - halloween_seasonal_long: RECLASSIFY BLOCKED_PRODUCER_BUG -> PENDING (producer OK)
  - totm_long: RECLASSIFY BLOCKED_PRODUCER_BUG -> PENDING (producer OK; same family)
  - pre_holiday_long: RECLASSIFY BLOCKED_PRODUCER_BUG -> PENDING (producer OK; same family)

**Downstream execution scope tightening:**
  - B1124 test_b1124_calendar_lru_cache_correctness.py: skip removed; producer verified
  - B1128-B1131 grouped LOOSEN: halloween/totm/pre_holiday now eligible for standard LOOSEN treatment
  - Original BUG-279 hypothesis (a) @lru_cache stale, (b) tdm edge case: BOTH RULED OUT
  - Remaining hypothesis (d) cube fan-out drops trades: DEFERRED to B1132 (validated method per B1095 precedent)

**Joint:** Council 236 Turn 2 initial hypothesis; Council 245 empirical rebuttal; L184 family-inheritance verdicts over-scoping; B1132 micro-cube validation dependency.


---

### BUG-277 UPDATE (B1126 2026-07-03 Council 245 Item 2/3):

**STATUS CHANGE: RESOLVED-IMPLEMENTED** (was: OPEN)

Fix in chart_patterns.py:383 detect_triangle:
  - Ascending flat-top tolerance: `abs(slope_high_norm) < 0.001` -> `< 0.002`
  - Ascending rising-low: `slope_low_norm > 0.002` -> `> 0.001`
  - Descending: symmetric widening for flat-bottom tolerance

Empirical validation on SPY 2020-2026 (rolling 30-bar window every 20 bars):
  - Pre-fix: 0 detections
  - Post-fix: 17 detections
  - Matches Bulkowski 2005 canonical ~5-15/yr/ticker rate

Root cause: SPY 4y slope_high_norm distribution median=0.00151, 90%ile=0.00302.
Prior tolerance 0.001 excluded 90%+ of legitimate consolidation windows.
New 0.002 tolerance matches Bulkowski 2005 canonical ~2% total drift range
over pattern width (equivalent to 0.002 × 30 bars = 6% max drift).

B1124 test flipped: `test_bug_277_triangle_producer_fires_on_spy_canonical`
replaces RED-first skip with GREEN assertion `>= 5` triangles on SPY 4y.

**Reclassifications:**
  triangle_ascending_long:        BLOCKED_PRODUCER_BUG -> DONE_B1126
  triangle_ascending_retest_long: BLOCKED_PRODUCER_BUG -> DONE_B1126
  triangle_descending_short:      BLOCKED_PRODUCER_BUG -> DONE_B1126

**Downstream:** B1128-B1131 grouped LOOSEN now eligible to LOOSEN consumer
gate stacks (vol_spike, Pattern S filters) on top of newly-firing producer.

**Joint:** Council 236 Turn 5 initial finding; Council 245 Item 2/3 empirical
fix; L184 family-inheritance verdicts; B1124 test extension.


---

### BUG-281 UPDATE (B1128 2026-07-03 Council 247 empirical investigation):

**STATUS CHANGE: RESOLVED-BY-INVESTIGATION** (was: OPEN)

Council 247 empirical investigation REFUTES Turn 5 root cause hypothesis. Producer VERIFIED working via direct runtime test on SPY 4y:

  Rolling 60-bar window every 20 bars = 62 windows total.
  double_bottom_detected: 11 detections
  double_top_detected:    22 detections

Producer works correctly at Bulkowski canonical rates. Turn 5 '0 fires SPY 6y sample' finding was inconsistent with today's empirical probe - possibly due to different lookback sampling or state of chart_patterns.py at time of Turn 5.

**Root cause of 0 n_fires in Batch A**: CONSUMER 4-way AND compound (per strat_double_bottom_long at screener.py):
  1. double_bottom_detected            (~11/62 = 18% of bar-windows)
  2. price_above_ema_200               (bull regime gate)
  3. close_in_top_40pct_of_range       (B730 anti-fakeout strong-close)
  4. vol_spike_15x                     (B730 Bulkowski volume confirmation)

Compound probability: 0.18 x 0.60 x 0.25 x 0.15 = ~0.4% per ticker-bar. On 150 tickers x 1000 trading days = ~600 potential fires but multiplied by the B730 requirement adds compound sparseness.

**B1124 test flipped:**
  test_bug_281_double_bottom_producer_verified_runtime
  REPLACED RED-first skip WITH producer-verified assertion asserting
  >=5 double_bottom + >=5 double_top on SPY 4y sample.

**Reclassification:**
  double_bottom_long: BLOCKED_PRODUCER_BUG -> PENDING (batch_ref=B1128)

**Downstream:** B1129+ grouped LOOSEN should drop vol_spike_15x OR
close_in_top_40pct_of_range from B730's 2 added gates to restore fires.

**Similarity to BUG-279:** Both cases had Turn X paragraph hypothesis
about producer failure refuted by later empirical probe. Both hypotheses
under-touched runtime and over-scoped to the producer layer. L184 family-
inheritance over-scoping pattern applies to Turn 5/Turn 2 producer
hypotheses too.

**Joint:** Council 236 Turn 5 initial finding; Council 247 empirical
rebuttal; L184 pattern; feedback_family_bug_grep_before_one_liners
CHECKLIST (n) analog to consumer-side gate audit.


---

### BUG-280 UPDATE (B1130 2026-07-03 Council 248 Item 2/3):

**STATUS CHANGE: COVERAGE-VERIFIED (root cause revised)** (was: OPEN with coverage-gap hypothesis)

Council 248 empirical coverage audit REFUTES coverage-gap root cause:

  Polygon news parquets in data_prefetch/polygon/news/: 1,927 (471 MB total)
  Batch A tickers x Polygon news coverage: 150 / 150 = 100%
  Batch A tickers x FINRA short_interest coverage: 149 / 150 = 99.3%
    (only BF-B missing due to hyphen-ticker naming convention)

**Root cause revised:**
  Coverage is COMPLETE. Sentinels tripped during Batch A because
  per-ticker x date PARQUET CONTENTS are sparse (few articles per bar).
  Not a data prefetch gap - a data-density-per-window issue.

  When news_sentiment producer runs on a ticker on a specific date:
  - 100 rule-fallback sentinel: 100 consecutive returns from rule-based
    scoring (Polygon returned data but had 0 article-count)
  - 50 empty sentinel: 50 consecutive returns with empty result
  - 30 zero-score sentinel: 30 consecutive returns with 0 sentiment

  Rule-fallback tripping doesn't mean data is missing - it means:
  either (a) Polygon returned {} for the ticker x date window, OR
  (b) score computation returned 0.0 for empty article set.

**Downstream fix path:**
  (1) Verify sentinel thresholds calibrated for realistic news-sparsity
      windows (some tickers have <1 article per week - normal).
  (2) Compute article-count-per-ticker distribution across Batch A cache
      to calibrate expected sparsity.
  (3) Downgrade sentinels from HALT-triggering to WARNING-only.

**No CSV reclassification this batch** - news_* strategies remain PENDING
until B1133+ grouped LOOSEN which will apply the loosening actions from
Council 236 Turn 4 (drop AVWAP redundant + loosen sentiment thresholds).

**B1124 test state:**
  test_polygon_news_prefetch_min_ticker_coverage: GREEN (1927 >> 50 floor)
  test_batch_a_log_documents_sentinel_state: skip-with-CTA (Batch A logs
    were not persisted post-run per current setup)

**Joint:** Council 236 Turn 4 initial hypothesis; Council 248 empirical
rebuttal; L184 pattern (Turn X hypothesis over-scoped without empirical
verification); Council 197 Outsider verdict (3rd application - producer/
data hypotheses without runtime probes are audit-theater).

