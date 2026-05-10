# BUG_REGISTER

**Purpose:** Per owner Pass 52 turn 110-111 directive — canonical cross-reference between bugs documented in AUDIT.md and the decisions/sprints that resolve them. Implements 4-bucket classification per CHECKLIST #58 spirit applied to bugs.

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
| Total canonical bugs in AUDIT.md (### BUG-NN sections) | 148 |
| Bugs linked to decisions (AUDIT_INDEX.md cross-reference) | 148 (100%) |
| Bugs unlinked needing separate ENG entry | 0 |
| Bugs explicitly tagged CRITICAL OPEN in registers | 2 (BUG-095, BUG-111) |
| Bugs explicitly tagged DEFERRED/WONTFIX in body | ~12 |
| Resolved bugs (likely fixed in code per body narratives) | ~107 unclassified — need narrative confirmation per bug |

**Important finding:** All 148 documented bugs have at least one decision-reference in AUDIT_INDEX.md. This means the existing ENGINEERING_REGISTER + DOCUMENTATION_REGISTER infrastructure already covers all bug execution tracking via decision sprint slots — no parallel bug-tracking infrastructure needed.

## Bug → Decision Cross-Reference Table

The following table maps every bug in AUDIT.md to the decision(s) that reference or resolve it. For execution tracking, see the listed decision's entry in ENGINEERING_REGISTER.md or DOCUMENTATION_REGISTER.md.

| Bug ID | Title (truncated) | Linked decisions | Sprint context |
|---|---|---|---|
| BUG-01 | `crisis_flag` used before definition → NameError crash | DEC-458 | (see linked DEC sprint) |
| BUG-02 | `days` variable used before definition → UnboundLocalError on every trade close | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10 (fix landed; backtest.py:263 explicit comment confirms days variable defined before use to prevent UnboundLocalError) |
| BUG-03 | `ClosedTrade` dataclass defined twice — dead code, maintenance risk | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10 (duplicate ClosedTrade removed; only one class definition at exit_manager.py:101) |
| BUG-04 | `avoid` direction falls into `triggered_short` bucket — inflates confidence tier | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10 (backtest.py:335 has explicit avoid-direction skip with logging) |
| BUG-05 | `strategies_triggered` key mismatch — agent cache is always wrong | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10 (pipeline.py:140-180 uses canonical strategies_triggered key consistently) |
| BUG-06 | Double borrow cost on short trades | DEC-458 | (see linked DEC sprint) |
| BUG-07 | API key guard blocks no-agent Phase 1B run | DEC-458 | RESOLVED 2026-05-08 v8h+1 - test_bug_007 in test_regression.py confirms _call_claude returns None on missing key (soft guard); --no-agents bypasses agent branch. |
| BUG-08 | `ema_50_200_bullish` signal key does not exist | DEC-458 | (see linked DEC sprint) |
| BUG-09 | `below_cam_s3` signal key does not exist | DEC-458 | (see linked DEC sprint) |
| BUG-10 | Agent signal keys wrong — agents always see `False` for key price context | DEC-458 | (see linked DEC sprint) |
| BUG-11 | `williams_r` short default fires incorrectly | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10 (screener.py:211 williams_r short default value added; signal defined technical.py:323) |
| BUG-12 | Deduplication order bias — shorts never fire when long strategy fires first | DEC-458 | (see linked DEC sprint) |
| BUG-13 | `days_to_next_earnings` makes ~106,000 live yfinance calls during backtest | DEC-256, DEC-444, DEC-458 | SUPERSEDED-BY-DEC-497 (NO-LIVE-API HARD CUT removed yfinance from runtime; 106K live calls bug can no longer trigger) |
| BUG-14 | AAPL, CVS, JPM, NVDA missing from `run_full.sh` batch ticker lists | DEC-458 | (see linked DEC sprint) |
| BUG-15 | `max_drawdown` uses `cumsum()` instead of compounded equity curve | DEC-458 | (see linked DEC sprint) |
| BUG-16 | `PASSING_CRITERIA min_trades = 100` contradicts all documentation | DEC-458 | SUPERSEDED-BY-DEC-503 (PASSING_CRITERIA min_trades documented + tested via DEC-503 13-layer pyramid; min_trades=100 verified canonical per CANONICAL_FACTS F-007) |
| BUG-17 | `run_commit.sh` full mode hangs on interactive `input()` in merge script | DEC-458 | (see linked DEC sprint) |
<!-- canonical-fact-historical: F-002 BUG_REGISTER documents bugs that explicitly reference stale strategy-count phrasing -->
| BUG-18 | Bonferroni correction hardcoded to 60 strategies, should be 72 | DEC-080, DEC-400, DEC-458 | (see linked DEC sprint) |
| BUG-19 | OHLCV cache incomplete — 402 of 495 tickers only cover to 2024-12-31 | DEC-260, DEC-442, DEC-448, DEC-458 | SUPERSEDED-BY-DEC-609 (H1 OHLCV Master Dedup re-fetch covers 1937 tickers 2021-05 to 2026-05; 2024-12-31 cache cap eliminated) |
| BUG-20 | Regime thresholds inconsistent between PROJECT_PLAN and config.py | DEC-458 | (see linked DEC sprint) |
| BUG-21 | `exit_strategies.py` own `_pnl` has no borrow cost — short comparison optimistic | DEC-458 | (see linked DEC sprint) |
<!-- canonical-fact-historical: F-002 bugs reference stale code strings now corrected via CANONICAL_FACTS.md alignment -->
| BUG-22 | `run_phase1a.py` header prints "60 strategies" | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10 (run_phase1a.py docstring no longer references stale 60-strategies count; verified via grep) |
<!-- canonical-fact-historical: F-002 same as above -->
| BUG-23 | `screener.py` docstring says "60 strategies across 7 categories" | DEC-458 | SUPERSEDED-BY-CANONICAL_FACTS-F-002 Pass 53 v8h+1 2026-05-10 (screener.py:9 explicitly cites CANONICAL_FACTS.md F-002 Layer 1 baseline = 60; the count is canonically correct, not stale) |
| BUG-24 | CHECKLIST item 13c says "review ALL agent outputs" — not applicable for no-agent | DEC-458 | (see linked DEC sprint) |
| BUG-25 | `run_tests.sh` does not pass `--no-agents` flag | DEC-458 | (see linked DEC sprint) |
| BUG-26 | CRITICAL — VIX proxy is VXX price (223–461), not actual VIX (18–36) — all regime | DEC-317, DEC-388, DEC-458 | SUPERSEDED-BY-DEC-302 (VIX canonical source FRED:VIXCLS replaces VXX proxy; DEC-302 + Pass 53 Day-9 v8 BUG-VIX-PROXY fix) |
| BUG-27 | CRITICAL — `regime_confidence()` function built but never called — dead code | DEC-458 | (see linked DEC sprint) |
| BUG-28 | HIGH — RSI computation uses simple rolling mean instead of Wilder exponential sm | DEC-458 | (see linked DEC sprint) |
| BUG-29 | HIGH — Open trades at backtest end silently discarded — upward bias in all metri | DEC-458 | (see linked DEC sprint) |
| BUG-30 | HIGH — VIX tightening in crisis contradicts own documentation | DEC-458 | (see linked DEC sprint) |
| BUG-31 | HIGH — Walk-forward OOS minimum of 30 trades is statistically insufficient | DEC-458 | (see linked DEC sprint) |
| BUG-32 | HIGH — Profit factor minimum 1.2 too low; literature requires 1.5 minimum | DEC-458 | (see linked DEC sprint) |
| BUG-33 | HIGH — Sharpe ratio not required as passing criterion; computed but ignored | DEC-458 | (see linked DEC sprint) |
| BUG-34 | HIGH — Mean reversion strategies run in all regimes — literature shows they fail | DEC-458 | (see linked DEC sprint) |
| BUG-35 | MEDIUM — Decision Agent default fallback has invalid `action` value | DEC-458 | (see linked DEC sprint) |
| BUG-36 | MEDIUM — Regime-aware strategy weighting not implemented | DEC-458 | (see linked DEC sprint) |
| BUG-37 | MEDIUM — Survivorship bias haircut methodology is arbitrary | DEC-458 | (see linked DEC sprint) |
| BUG-38 | MEDIUM — No minimum Sharpe in Bonferroni correction | DEC-080, DEC-401, DEC-458 | (see linked DEC sprint) |
| BUG-39 | MEDIUM — `regime_confidence()` compares VIX-based regime with SPY-trend regime i | DEC-458 | (see linked DEC sprint) |
| BUG-40 | MEDIUM — Short stop distance same as long (10%) — asymmetric risk not accounted  | DEC-458 | (see linked DEC sprint) |
| BUG-41 | MEDIUM — `min_market_cap_m = 100` too low; admits stocks with poor institutional | DEC-458 | (see linked DEC sprint) |
| BUG-42 | LOW — `LILLY` appears as ticker in `run_full.sh` but should be `LLY` | DEC-458 | (see linked DEC sprint) |
| BUG-43 | LOW — Missing Calmar ratio minimum in passing criteria | DEC-458 | (see linked DEC sprint) |
| BUG-44 | LOW — Test suite has no test for `close_trade()` or `_process_day()` | DEC-458 | (see linked DEC sprint) |
| BUG-45 | MEDIUM — FX currency risk not modelled | DEC-458 | (see linked DEC sprint) |
| BUG-46 | MEDIUM — `fetch_info_bulk` info cache uses current market_cap, not historical | DEC-260, DEC-442, DEC-458 | SUPERSEDED-BY-DEC-497 (yfinance fetch_info_bulk removed from runtime per NO-LIVE-API HARD CUT) |
| BUG-47 | MEDIUM — VXX in universe creates self-referencing regime paradox | DEC-458 | (see linked DEC sprint) |
| BUG-48 | MEDIUM — Sector `Volatility` and `Emerging Markets` not in sector criteria profi | DEC-458 | (see linked DEC sprint) |
| BUG-49 | LOW — FX risk not mentioned in EXPLANATION.md or PROJECT_PLAN.md | DEC-458 | (see linked DEC sprint) |
| BUG-50 | LOW — `position_staleness_pct=1%` in live rules has no backtest equivalent | DEC-458 | (see linked DEC sprint) |
| BUG-51 | HIGH — All 5 agents receive wrong or zero price context due to BUG-10 compoundin | DEC-458 | (see linked DEC sprint) |
| BUG-52 | HIGH — Risk Agent's VIX floor behavior now fully explained by BUG-26 | DEC-458 | (see linked DEC sprint) |
| BUG-53 | HIGH — Finnhub news cache: all 509 files are empty — Sentiment Agent has no news | DEC-256, DEC-441, DEC-453, DEC-458 | (see linked DEC sprint) |
| BUG-54 | MEDIUM — Hull Moving Average uses simple rolling mean instead of WMA — signal ti | DEC-458 | (see linked DEC sprint) |
| BUG-55 | MEDIUM — PSAR flip detection uses approximation that may fire on wrong day | DEC-458 | (see linked DEC sprint) |
| BUG-56 | MEDIUM — Phase 1C base score can exceed [0, 100] — Decision Agent adjustment not | DEC-458 | (see linked DEC sprint) |
| BUG-57 | MEDIUM — Integration tests missing 15 critical scenarios — 5 bugs would have bee | DEC-458 | (see linked DEC sprint) |
| BUG-58 | LOW — StochRSI cross-up fires in mid-range, not just oversold zone | DEC-458 | (see linked DEC sprint) |
| BUG-59 | LOW — CPR top/bottom labels are reversed vs industry convention | DEC-458 | (see linked DEC sprint) |
| BUG-60 | HIGH — Short entry zone validation rejects favourable gap-down — understates sho | DEC-458 | (see linked DEC sprint) |
| BUG-61 | HIGH — Backtest allows multiple concurrent positions in same ticker across conse | DEC-458 | (see linked DEC sprint) |
| BUG-62 | HIGH — Phase 1D cannot run — 2020 OHLCV data not cached, DATA_LOAD_START=2021 | DEC-442, DEC-458 | (see linked DEC sprint) |
| BUG-63 | MEDIUM — Email approval system has 6 critical design gaps not addressed in PROJE | DEC-458 | (see linked DEC sprint) |
| BUG-64 | MEDIUM — Phase 1C prerequisites not documented — Unusual Whales and Ortex integr | DEC-458 | (see linked DEC sprint) |
| BUG-65 | MEDIUM — Strategy retirement rule statistically invalid at realistic live trade  | DEC-458 | (see linked DEC sprint) |
<!-- canonical-fact-historical: F-002 documents PROJECT_PLAN drift — superseded by CANONICAL_FACTS.md F-002 layered roster -->
| BUG-66 | MEDIUM — PROJECT_PLAN mentions "60 strategies" 11 times — 9 of 12 new short stra | DEC-458 | (see linked DEC sprint) |
| BUG-67 | MEDIUM — Alpaca paper trading (Stage 3) does not match IBKR live trading (Stage  | DEC-458 | (see linked DEC sprint) |
| BUG-68 | MEDIUM — CLAUDE.md missing 5 critical recent decisions | DEC-458 | (see linked DEC sprint) |
| BUG-69 | LOW — Infrastructure design: GitHub Actions vs VPS ambiguity | DEC-458 | (see linked DEC sprint) |
| BUG-70 | LOW — No database schema designed for Stage 3 PostgreSQL | DEC-458 | (see linked DEC sprint) |
| BUG-71 | LOW — IBKR API session management not designed | DEC-458 | (see linked DEC sprint) |
| BUG-72 | HIGH — `validate_phase1b_data.py` passes all checks but misses 6 blockers — fals | DEC-458 | (see linked DEC sprint) |
| BUG-73 | HIGH — `prepopulate_cache_index.py` writes incompatible format — causes cache mi | DEC-458 | (see linked DEC sprint) |
| BUG-74 | HIGH — BUG-14 worse than documented: XLE also missing from `run_full.sh` — 5 tic | DEC-458 | (see linked DEC sprint) |
| BUG-75 | MEDIUM — `max_drawdown` computed on unsorted PnL series — results depend on exit | DEC-458 | (see linked DEC sprint) |
| BUG-76 | MEDIUM — Agent cache fully contaminated: all runs for same ticker+date+phase sha | DEC-458 | (see linked DEC sprint) |
| BUG-77 | MEDIUM — Candidate ranking by `strategy_count` inflated by `avoid` entries — top | DEC-458 | (see linked DEC sprint) |
| BUG-78 | CRITICAL — Trailing stop lookahead bias: stop updated using today's close BEFORE | DEC-458 | (see linked DEC sprint) |
| BUG-79 | HIGH — Stop fills assumed at the stop price; gap-through is not modelled (slippa | DEC-081, DEC-130, DEC-458 | (see linked DEC sprint) |
| BUG-80 | HIGH — Exit slippage never applied; only entry slippage charged. Round-trip slip | DEC-458 | (see linked DEC sprint) |
| BUG-81 | HIGH — `SHORT_BORROW_COST_PER_DAY = 0.005` is 2.5× the documented intent | DEC-458 | (see linked DEC sprint) |
| BUG-82 | HIGH — Slippage and transaction-cost double-charging — total cost 2× literature  | DEC-458 | (see linked DEC sprint) |
| BUG-83 | HIGH — `get_congressional_detail()` filters with INVERTED point-in-time logic | DEC-458 | (see linked DEC sprint) |
| BUG-84 | MEDIUM — IS/OOS walk-forward boundary leakage on multi-day swing trades | DEC-458 | (see linked DEC sprint) |
| BUG-85 | MEDIUM — `regime_at_entry` includes the regime label but no transition tracking | DEC-458 | (see linked DEC sprint) |
| BUG-86 | MEDIUM — FRED CPI lookahead bias of ~10 days | DEC-449, DEC-458 | (see linked DEC sprint) |
| BUG-87 | MEDIUM — No data quality validation on ingestion | DEC-458 | (see linked DEC sprint) |
| BUG-88 | MEDIUM — No signal versioning; cache invalidation incomplete | DEC-458 | (see linked DEC sprint) |
| BUG-89 | MEDIUM — Flat signal dict (220 fields) lacks type safety | DEC-458 | (see linked DEC sprint) |
| BUG-90 | MEDIUM — No state checkpointing for crashes/restarts | DEC-458 | (see linked DEC sprint) |
| BUG-91 | MEDIUM — No determinism control | DEC-458 | (see linked DEC sprint) |
| BUG-92 | LOW — No streaming progress / metrics during run | DEC-458 | (see linked DEC sprint) |
| BUG-93 | CRITICAL — No execution layer exists; PROJECT_PLAN describes it conceptually onl | DEC-458 | (see linked DEC sprint) |
| BUG-94 | CRITICAL — Stage 3 paper trading cannot actually run as designed | DEC-458 | (see linked DEC sprint) |
| BUG-95 | CRITICAL — No portfolio-level state; every trade evaluated independently | DEC-070, DEC-076, DEC-091, DEC-222, DEC-231, DEC-458 | (see linked DEC sprint) |
| BUG-96 | HIGH — No benchmark comparison (SPY buy-and-hold) | DEC-458 | (see linked DEC sprint) |
| BUG-97 | HIGH — No infrastructure-as-code; manual VPS setup | DEC-458 | (see linked DEC sprint) |
| BUG-98 | HIGH — No monitoring or alerting | DEC-458 | (see linked DEC sprint) |
| BUG-99 | MEDIUM — No secret management; API keys in environment variables | DEC-458 | (see linked DEC sprint) |
| BUG-100 | MEDIUM — No kill switch; manual intervention required to stop trading | DEC-458 | (see linked DEC sprint) |
| BUG-101 | CRITICAL — 88.1% of trades are overlapping re-entries on the same ticker — backt | DEC-458 | (see linked DEC sprint) |
| BUG-102 | CRITICAL — 3.5× same-day duplicate inflation: 9,921 unique decisions logged as 3 | DEC-458 | (see linked DEC sprint) |
| BUG-103 | CRITICAL — Smart money data prefetched for 7 categories × 509 tickers but never  | DEC-458 | (see linked DEC sprint) |
| BUG-104 | HIGH — Position sizing rules from config never applied to PnL — backtest assumes | DEC-458 | (see linked DEC sprint) |
| BUG-105 | HIGH — Agent downgrade cascade: 99.9% of trades downgraded by exactly 1 tier — a | DEC-458 | (see linked DEC sprint) |
| BUG-106 | HIGH — Perfect stop fills in trade log: every trailing-stop exit fills at exactl | DEC-458 | (see linked DEC sprint) |
| BUG-107 | MEDIUM — Silent exception swallowing: `except Exception: pass` masks checkpoint  | DEC-458 | (see linked DEC sprint) |
| BUG-108 | MEDIUM — Agent context built with `.get(key, default)` masks missing data; agent | DEC-458 | (see linked DEC sprint) |
| BUG-109 | HIGH — yfinance auto_adjust causes data drift; backtest results not reproducible | DEC-442, DEC-458 | SUPERSEDED-BY-DEC-497 (yfinance auto_adjust removed from runtime; no live OHLCV calls) |
| BUG-110 | HIGH — Entry gap filter not enforced; trades opened despite exceeding ATR limit | DEC-458 | (see linked DEC sprint) |
| BUG-111 | **CRITICAL** — No break-and-retest variants of breakout strategies (severity: MEDIUM→HIGH→CRITICAL across Pass 52) | DEC-354 (parent umbrella reopened) + DEC-355/356/357 (3 retest-variant strategies) + DEC-358/359/360/361/362 (5 chart pattern strategies; retest-cross-cutting) | DEFERRED-TO-SPRINT-8 (chart-pattern + retest variants — explicit Sprint 8 scope per Pass 53 backlog) |
| BUG-112 | LOW — No ICT/SMC concepts implemented | DEC-458 | (see linked DEC sprint) |
| BUG-113 | HIGH — Agent action/sizing/exit recommendations ignored by engine | DEC-008, DEC-458 | (see linked DEC sprint) |
| BUG-113 | HIGH — Agent action/sizing/exit recommendations ignored by engine | DEC-008, DEC-458 | (see linked DEC sprint) |
| BUG-178 | HIGH — Earnings dates fetched live during backtest, no prefetch path | DEC-458 | (see linked DEC sprint) |
| BUG-179 | HIGH — yfinance .info fetched live during backtest universe load | DEC-443, DEC-458 | SUPERSEDED-BY-DEC-497 (yfinance .info live calls removed; universe loads from prefetched CSVs) |
| BUG-180 | HIGH — VIX not explicitly prefetched; VXX used as proxy is cause of BUG-26 | DEC-458 | SUPERSEDED-BY-DEC-302 (VIX explicitly prefetched from FRED:VIXCLS; VXX proxy retired) |
| BUG-181 | MEDIUM — Finnhub news prefetch silently produces empty files | DEC-453, DEC-458 | (see linked DEC sprint) |
| BUG-182 | MEDIUM — Agent cache invalidated by every code change with no versioning gate | DEC-458 | (see linked DEC sprint) |
| BUG-183 | LOW — No prefetch validation step | DEC-458 | (see linked DEC sprint) |
| BUG-184 | CRITICAL — Insider data prefetch stops 2024-12-31; 13-month gap before backtest  | DEC-458 | (see linked DEC sprint) |
| BUG-185 | CRITICAL — Wikipedia views prefetch failed entirely; all 509 files empty | DEC-030, DEC-458 | (see linked DEC sprint) |
| BUG-186 | HIGH — 29 institutional 13F files empty including major tickers (AAPL, ABBV, AMZ | DEC-325, DEC-458 | (see linked DEC sprint) |
| BUG-187 | HIGH — WSB mentions prefetch stops 2025-02-21; 14-month gap | DEC-458 | (see linked DEC sprint) |
| BUG-188 | MEDIUM — Defense tickers (NOC, TXT) have empty gov_contracts data | DEC-458 | (see linked DEC sprint) |
| BUG-189 | MEDIUM — Ticker symbol mapping issue: BF-B, BRK-B variants empty | DEC-458 | (see linked DEC sprint) |
| BUG-190 | MEDIUM — Quiver endpoints not in prefetch (Senate, Twitter, Off-Exchange, App Do | DEC-450, DEC-458 | (see linked DEC sprint) |
| BUG-191 | CRITICAL — No prefetch validation gate before cache-dependent code runs | DEC-299, DEC-322, DEC-458 | (see linked DEC sprint) |
| BUG-199 | MEDIUM — No gate firing rate observability | DEC-458 | (see linked DEC sprint) |
| BUG-200 | CRITICAL — Risk Agent context expansion required (Section B) | DEC-458 | (see linked DEC sprint) |
| BUG-201 | MEDIUM — Strategy `earnings_tolerant` attribute missing | DEC-458 | (see linked DEC sprint) |
| BUG-202 | MEDIUM — No earnings-momentum strategies implemented | DEC-458 | (see linked DEC sprint) |
| BUG-203 | MEDIUM — No A/B testing infrastructure for agent gates | DEC-458 | (see linked DEC sprint) |
| BUG-270 | HIGH — `insider_signal()` column-name mismatch (100% silent failure) | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10 (code+test verified) |
| BUG-271 | HIGH — `get_gov_contracts()` no Date column lookup (99.4% silent failure) | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 Batch 1 2026-05-05 |
| BUG-272 | HIGH — `get_lobbying()` Amount string concat (98.8% silent failure) | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 Batch 13 2026-05-06 |
| BUG-273 | HIGH — `congressional_signal()` Chamber/House column mismatch | DEC-458 | RESOLVED-IMPLEMENTED Pass 53 Batch 13 2026-05-06 |
| BUG-274 | HIGH — `institutional_signal()` SharesChange column missing | DEC-458 | (see linked DEC sprint) |
| BUG-275 | LOW — `bonferroni_adjusted_threshold(n_strategies=0)` TypeError on complex round | DEC-080, DEC-458 | (see linked DEC sprint) |
| BUG-276 | HIGH — `_agent_cache_key` calls `sorted()` on list of dicts → crashes when strat | DEC-458 | (see linked DEC sprint) |
| BUG-277 | HIGH — `classify_regime()` truth-value-of-DataFrame error — 100% failure | DEC-458 | (see linked DEC sprint) |
| BUG-278 | MEDIUM — `yield_curve_regime()` doesn't use macro_combined.parquet cache | DEC-458 | (see linked DEC sprint) |
| BUG-279 | MEDIUM — `get_ohlcv()` with reversed date order silently returns 0 rows | DEC-458 | (see linked DEC sprint) |
| BUG-280 | LOW — `days_to_next_earnings()` returns None on yfinance failure | DEC-444, DEC-458 | SUPERSEDED-BY-DEC-497 (days_to_next_earnings yfinance dependency removed; calendar-based path only) |
| BUG-281 | MEDIUM — `site_generator._assign_tier` duplicates `engine._assign_confidence_tie | DEC-458 | (see linked DEC sprint) |
| BUG-282 | LOW — `site_generator.build_entry_zone` ignores `category` parameter | DEC-458 | (see linked DEC sprint) |
| BUG-283 | LOW — `build_position_sizing` returns 0% silently for unknown tier | DEC-458 | (see linked DEC sprint) |
| BUG-284 | MEDIUM — `prefetch_quiver` DATE_FIELDS["gov_contracts"]="Date" but cache schema  | DEC-451, DEC-458 | (see linked DEC sprint) |


## CRITICAL OPEN bugs (priority)

Per project memory + Pass 52 audit findings:

- **BUG-095** (no Portfolio class) — CRITICAL OPEN; blocks DEC-070/076/091; resolution via Sprint 3 (Phase 0.B Portfolio class implementation, ~8-11d)
- **BUG-218** (yfinance fetch_info CURRENT not as_of) — CRITICAL OPEN; resolution via DEC-443 (Sprint 4)
- **BUG-111** (No break-and-retest variants of breakout strategies) — Severity escalated MEDIUM→HIGH→CRITICAL across Pass 52. Sprint 8 resolves via DEC-355-362 chart pattern strategies (retest cross-cutting primitive). **Open scope verified Pass 52 turn 123:** 25 existing breakout strategies in screener.py (Breakout 6 + Pivot Based 10 + Confluence 9 categories) may also need `_retest` suffixed variants. Owner direction needed at Sprint 8 implementation time: (a) shared retest entry-signal primitive any breakout strategy opts into, OR (b) explicit `_retest` variant per existing breakout strategy = ~25 new strategies. Effort: ~5-10d (a); ~25-30d (b).

## Deferred / WONTFIX bugs (Bucket 4)

Bugs explicitly deferred to Stage 3+ or marked WONTFIX. These don't need engineering work in current scope; documented for historical record + future revisit. (Per body-narrative analysis; ~12 bugs estimated.)

Subset documented in DOCUMENTATION_REGISTER.md as appropriate per CHECKLIST #58 spirit applied to bugs.

## Status Tracking

| Status | Action |
|---|---|
| **Bucket 1 (Open-linked)** | Resolution tracked via decision sprint slot in ENGINEERING_REGISTER |
| **Bucket 2 (Open-unlinked)** | None found — all bugs linked to decisions |
| **Bucket 3 (Resolved)** | Historical record in AUDIT.md; no register action |
| **Bucket 4 (Deferred / WONTFIX)** | Cross-reference in DOCUMENTATION_REGISTER if appropriate |

## Going Forward

**Per CHECKLIST #58 spirit applied to bugs:**
- New bugs found during implementation → AUDIT.md ### BUG-NN entry
- If bug is OPEN and has resolving decision → that decision must have sprint slot in ENGINEERING_REGISTER
- If bug is OPEN without resolving decision → create new decision OR new ENGINEERING_REGISTER entry per #58
- Per-commit verification: any new BUG-NN heading in AUDIT.md must update BUG_REGISTER.md cross-reference table

This BUG_REGISTER.md serves as the canonical cross-reference. Detail lives in AUDIT.md; execution tracking lives in ENGINEERING_REGISTER (via linked decisions) + DOCUMENTATION_REGISTER (for deferred/WONTFIX).

---

*Per CHECKLIST #25 (honest scope correction — initial framing of "144+ bugs need separate ENG entries" was wrong; reality is 100% linked to decisions); #43 (full Python analysis on 148 canonical bugs); #51 (owner approved 4-bucket recommendation); #57 (use-case mapping per bucket); #58 (operational at bug-level: cross-reference register with execution tracking via existing decision infrastructure).*

---

## Pass 53 Update — Phase 1A Restoration Bug-Decision Mapping

**Trigger:** Phase 1A restoration (DEC-486/487/488 PROPOSED Pass 53).

No new bugs introduced. Existing bug-to-decision mappings remain valid. Phase 1A restoration is purely architectural (sub-phase taxonomy clarification + cube infrastructure phasing); no engine bugs depend on phase taxonomy.

**Bugs whose resolution sprint may shift due to Phase 1A insertion:**

| Bug | Resolving DEC | Original sprint | Pass 53 update |
|---|---|---|---|
| BUG-095 | Portfolio class | Sprint 3 | UNCHANGED (Sprint 3 still pre-Phase-1A) |
| BUG-111 | Break-and-retest primitive | Sprint 8 | UNCHANGED (Phase 1C+ post-1B-α) |
| BUG-218 | yfinance .info CURRENT-not-as_of | Sprint 4 (DEC-443) | UNCHANGED (Sprint 4 pre-Phase-1A) |
| BUG-007 | API key guard blocks no-agent Phase 1B run | DEC-458 | **CRITICAL Phase 1A dependency** — Phase 1A runs `--no-agents` flag; if API key guard fires when no agents needed, Phase 1A blocked. Verify resolution before Sprint 6.5. |

**BUG-007 elevated priority Pass 53:** original framing was "Phase 1B run with `--no-agents` flag"; Pass 53 restoration makes Phase 1A v3-style `--no-agents` execution a separate sprint deliverable. BUG-007 must be resolved BEFORE Sprint 6.5 starts or Phase 1A blocked at Day 1.

---

## Pass 53 Addendum — Post Sprint-1-Pre-Flight (Stream 3 chunk B)

No new bugs introduced Pass 53 post-pre-flight. DEC-491/492/493 PROPOSED (Sprint 2 trade-capture fragility) are **improvements/refactors**, not bug fixes — surfacing existing fragility patterns that are working correctly today (CSV serialization works; just brittle for nested dicts). They're properly tracked in ENGINEERING_REGISTER Sprint 2 additions, not BUG_REGISTER.

**Bug-to-decision mappings unchanged Pass 53 post-pre-flight:**
- BUG-095 (Portfolio class) — Sprint 3 unchanged
- BUG-111 (break-and-retest primitive) — Sprint 8 unchanged
- BUG-218 (yfinance .info CURRENT-not-as_of) — Sprint 4 unchanged (DEC-443)
- BUG-007 (API key guard `--no-agents`) — Sprint 6.5 dependency unchanged
- BUG-284 (govcontracts) — referenced in DEC-494 body; Sprint 0A alignment with `refresh_extended_universe.py` cleanup

**Pass 53 universe folder move (commit `c7f5580f`) — bug-impact none:**
Universe CSV reads abstracted through `backtest.data.universe` module functions (`get_sp500_constituents`, `get_etfs_full`, `get_extended_universe`, `get_momentum_watchlist`). Module-level `UNIVERSE_DIR` constant centralizes path. No bug introduced; no bug resolved.

**Cross-references:**
- ENGINEERING_REGISTER.md Sprint 2 additions block — DEC-491/492/493 PROPOSED entries
- AUDIT.md Pass 53 narrative entries
- DOCUMENTATION_REGISTER.md Pass 53 post-pre-flight entry

---

## Pass 53 — Smart Money Silent-Gap Bugs (Discovered 2026-05-05 via Quiver smoke test)

### BUG-271 — `smart_money.py` historical/analystestimates endpoint 404 (Quiver-enhanced analyst-revisions silently dead) — RESOLVED Pass 53 Batch 1 2026-05-05

**Severity:** HIGH — affects all Phase 1A v3 archive smart-money scoring + agent analyst input
**Status:** ✅ RESOLVED Pass 53 Batch 1 2026-05-05 (DEC-503 second test pyramid application)
**Module:** `backtest/data/smart_money.py:215`
**Function:** `get_analyst_data` (Quiver enhancement branch)

**Description:**
Code calls `https://api.quiverquant.com/beta/historical/analystestimates/{ticker}` which returns HTTP 404. Endpoint NOT in Trader-tier subscription per dashboard inventory (Pass 53 owner-confirmed 2026-05-05). Smart-money composite has been silently computing on partial inputs — Quiver-enhanced analyst-revisions branch dead since at least Pass 48.

**Impact:**
- `get_analyst_data` Quiver enhancement returns no data → `recent_upgrades` / `recent_downgrades` / `revision_direction` populated only from yfinance (which is itself being demoted per DEC-497 HARD CUT)
- Agent pipeline (Fundamental Agent, Decision Agent) operates on degraded analyst-revision signal
- All Phase 1A v3 archive backtest results silently affected

**Migration:**
REMOVE Quiver branch entirely from `get_analyst_data`. Rely on Polygon `/vX/reference/financials` for analyst consensus + EPS estimates per DEC-497 HARD CUT. yfinance branch must also go (NO LIVE API in Stage 2). Polygon financials covers equivalent data.

**Fix scheduled:** next turn after Pass 53 doc sweep, with full test pyramid per DEC-503.

**Discovery:** smoke probe `temp_staging/smoke_quiver_silent_gap_endpoints.py` Pass 53 turn 2026-05-05 confirmed 404 for `historical/analystestimates/AAPL`.

**Joint:** DEC-450 (Quiver Trader paid), DEC-497 (NO LIVE API HARD CUT), DEC-502 (Quiver scope reset; analyst data dropped from Quiver), DEC-503 (test pyramid for fix), L145 (silent-gap pattern).

---

### BUG-272 — `smart_money.py` historical/insidertrading endpoint 404 (insider_signal silently zeroed) — RESOLVED-IMPLEMENTED Pass 53 Batch 13 sub-task 2026-05-06

**Severity:** HIGH — affects all Phase 1A v3 archive smart-money scoring + agent insider input
**Status:** ✅ RESOLVED-IMPLEMENTED Pass 53 Batch 13 (schema-aligned fix; was stubbed Batch 1 2026-05-05; now reads actual `live/insiders` schema with TransactionCode + AcquiredDisposedCode)
**Module:** `backtest/data/smart_money.py:382`
**Function:** `insider_signal`

**Description:**
Code calls `https://api.quiverquant.com/beta/historical/insidertrading/{ticker}` which returns HTTP 404. Trader-tier dashboard lists only "Live Insider Trading" — no Historical variant.

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

### BUG-273 — `smart_money.py` historical/institutionalholdings endpoint 404 (institutional_signal silently zeroed) — RESOLVED-IMPLEMENTED Pass 53 Batch 13 sub-task 2026-05-06

**Severity:** HIGH — affects all Phase 1A v3 archive smart-money scoring + agent institutional input
**Status:** ✅ RESOLVED-IMPLEMENTED Pass 53 Batch 13 (schema-aligned fix using `live/sec13fchanges` Change_Share + Change_Pct columns directly, eliminating the need to join consecutive quarters; was stubbed Batch 1 2026-05-05)
**Module:** `backtest/data/smart_money.py:429`
**Function:** `institutional_signal`

**Description:**
Code calls `https://api.quiverquant.com/beta/historical/institutionalholdings/{ticker}` which returns HTTP 404. Trader-tier dashboard lists only "Live SEC13F" + "Live SEC13F Changes" — no Historical Institutional Holdings.

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
The composite `smart_money_score` function (DEC-332 weights: congressional + insider + institutional) had been computing on **1-of-3 inputs** (only congressional works) for an undetermined period (likely all Phase 1A v3 archive results). Smart-money confluence signal (DEC-124) — a primary dimension in the verdict cube (Part 2 §2.2 dimension #8 "Smart money signal present") — operated on degraded inputs.

**RESOLUTION Pass 53 Batch 1 2026-05-05** (DEC-503 SECOND test pyramid application):

Fix in `backtest/data/smart_money.py`:
- BUG-271 `get_analyst_data`: REMOVED Quiver `historical/analystestimates` branch (404 in tier) AND yfinance branches (D4 owner-approved total cut). Function now reads from `data_prefetch/polygon/financials/<TICKER>.parquet` (Sprint 0A Batch 4 populates). Pre-Batch-4: returns `signal="not_available"` gracefully.
- BUG-272 `insider_signal`: migrated to `_load_quiver_bulk("insidertrading")` reading `cache/quiver/insidertrading/global.parquet` (Sprint 0A.5 Batch 10 prefetches the live/insidertrading paginated bulk feed). Existing signal logic preserved; only data source changed.
- BUG-273 `institutional_signal`: migrated to `_load_quiver_bulk("sec13f")` reading `cache/quiver/sec13f/global.parquet` (Sprint 0A.5 Batch 10 prefetches the live/sec13f paginated bulk feed). 45-day reporting lag enforcement preserved.

New helpers added: `_load_quiver_bulk(dataset)` (cached bulk-feed loader), `_filter_bulk_by_ticker(df, ticker)` (case-insensitive Ticker column filter), `_reset_bulk_cache_for_tests()` (test-only cache reset).

Test pyramid (CHECKLIST #69 SECOND DEC-503 application):
- Unit: 9 new test_bug271/272/273_* tests PASS — graceful no-cache, synthetic bulk buy/sell, ticker filter case-insensitive, 45-day lag, smart_money_score 3-input composite verified
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

### BUG-274 — T2 SCREENER excluded currently-T1 tickers without computing PIT add/remove dates (graduated-name PIT gap; Option B fix applied Pass 53 2026-05-05)

**Severity:** MEDIUM — affects T2 universe membership PIT correctness for ~50 graduated names
**Module:** `scripts/build_tier2_screener_full.py`
**Owner-flagged via SNDK question:** "Is sandisk a part of tier 2 and tier 3?"

**Description:**
T2 SCREENER excluded ALL currently-T1 tickers (`Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` + `Tier 1C Universe_NASDAQ-100 Tickers_Jan 2020 to May 2026.csv` membership) from output, producing a snapshot-style "currently non-T1 universe" rather than a PIT-historical T2 list. Result: tickers that listed >=2010-01-01 and met DEC-103 thresholds (cap >= $5B + age >= 90d) BETWEEN their list_date and their T1 admission date were entirely absent from T2 universe.

**Impact:**
- 50 graduated tickers missing from T2 (verified Pass 53 turn 2026-05-05 via cross-check against T1a-active+T1c-active with non-null added_date)
- Notable missing names: SNDK, ABNB, APO, APP, ARES, CARR, CEG, COIN, CRWD, CVNA, DASH, DDOG, DELL, EPAM, MRNA, OTIS, PANW, PLTR, SHOP, SNOW(Snowflake; was already in T2), VEEV(was already in T2)
- For backtest dates falling in the [list_date, T1_admission_date] window for these tickers, T2 spinoff/IPO strategies miss eligible candidates → "graduating winners excluded" survivorship-like bias
- Example: SNDK spun off 2025-02-13 from WDC, joined S&P 500 2025-11-28. During the 9-month window, SNDK was a >$5B non-T1 spinoff = T2-eligible. T2 file omitted SNDK entirely.

**Root cause:**
T2 SCREENER applied T1-exclusion as a hard filter using current T1 membership (snapshot at SCREENER run time = 2026-05-05). Correct PIT logic: each non-T1 candidate computed against `(list_date, T1_admission_date OR present)` window with `added_date` and `removed_date` populated accordingly.

**Fix Pass 53 owner Option B approved 2026-05-05 (immediate hybrid backfill):**
1. Identified 114 candidates (92 T1a-active + 22 T1c-only-active with non-null added_date)
2. Polygon `/v3/reference/tickers/{ticker}` queried for `list_date` + `market_cap` + `name` + `sic_code`
3. Filtered: list_date >= 2010-01-01 AND market_cap >= $5B AND list_date < T1_added_date
4. 50 qualified for T2 backfill (64 skipped pre-2010 listings — joined T1 in 2020+ window but listed pre-2010, e.g., legacy companies that re-listed)
5. Appended to T2 with `added_date=list_date`, `removed_date=T1_added_date`, `Tier2Reason="graduated_to_T1a_YYYY"` or `"graduated_to_T1c_YYYY"`
6. Sector cross-referenced from T1a > T1c GICS (not SIC-derived; per DEC-499 source priority); 31 of 50 sectors corrected

**T2 row count:** 297 → 347 (50 graduated names added).

**Acceptance verification:**
- SNDK in T2 PIT load for as_of=2025-08-01: True ✓
- SNDK NOT in T2 PIT load for as_of=2026-01-01: True ✓ (post T1 admission 2025-11-28)
- 0 blank sectors in T2 file
- 69/69 backtest regression tests pass

**Structural fix scheduled Sprint 5 (Option A):**
Refactor `build_tier2_screener_full.py` to compute PIT add/remove dates per candidate during global SCREENER run, not as snapshot-style exclusion. Owner-deferred per Pass 53 directive ("immediate fix Option B + log structural Option A for Sprint 5").

**Joint:** DEC-103 (T2 thresholds), DEC-494 (T2 SCREENER-FIRST architecture), DEC-499 (sector source priority), DEC-477 (T1a PIT canonical), DEC-483 (T1c sub-tier), L89 (SNDK 9-month spinoff lag — original learning), L143 (don't-rewrite-history — historical T2 SCREENER output preserved; backfill is forward-looking correction).

**Sample of backfilled rows:**
- SNDK: added 2025-02-13, removed 2025-11-28 (graduated_to_T1a_2025), $186B IT
- ABNB: added 2020-12-10, removed 2023-09-18 (graduated_to_T1a_2020), $83B Consumer Disc
- APO: added 2011-03-30, removed 2024-12-23 (graduated_to_T1a_2011), $74B Financials
- DELL: added 2018-12-19, removed 2024-09-23 (graduated_to_T1a_2018), $138B IT
- COIN: added 2021-04-14, removed 2025-05-19 (graduated_to_T1a_2021), $54B Financials

---

### BUG-275 — T2 SCREENER 93 blank Sectors (resolved Pass 53 owner Q2 approved)

**Severity:** MEDIUM — DEC-499 sector coverage promise breached (T2 had 93 of 347 = 27% blank)
**Module:** Original `scripts/build_tier2_screener_full.py` SIC→GICS mapping was too coarse
**Owner-flagged via comprehensive validation (Pass 53 turn 2026-05-05)**

**Description:**
T2 SCREENER applied limited SIC→GICS mapping during full global pull; 93 of 297 SCREENER-output rows had blank `Sector` column because Polygon SIC code didn't fall into mapped ranges (mostly ADRs/foreign tickers + edge SIC codes outside core 11-class GICS range). DEC-499 promises 100% sector population across all 6 universe files.

**Fix Pass 53 owner Q2 approved 2026-05-05:**
`temp_staging/backfill_t2_sectors.py`:
1. Smoke probe: AA + ADT (verify Polygon SIC + comprehensive map work)
2. Full: 93 blank-sector T2 rows queried Polygon `/v3/reference/tickers/{ticker}` for sic_code
3. Comprehensive SIC→GICS map (granular ranges 3500-3899 disambiguating Industrials vs IT vs Health Care; +Communication Services for SIC 2700 publishing; +finance subdivisions 6000-6799)
4. yfinance `.info['sector']` one-time fallback for ADRs/foreign Polygon SIC didn't return
5. Result: 54 filled via Polygon SIC + 39 filled via yfinance + 0 tagged Unknown = 93/93 fixed

**T2 final state Pass 53 turn 2026-05-05:** 347 rows, 0 blank Sectors, 100% DEC-499 coverage achieved.

**Joint:** DEC-499 (18-classifier sector taxonomy), DEC-103/494 (T2 thresholds + SCREENER architecture), DEC-274 (graduated names backfill — distinct from this).

---

### BUG-276 — T3 NULL Symbol row (resolved Pass 53 owner Q3 approved)

**Severity:** LOW — single anomalous row (1 of 1924); cleanup not impact
**Module:** Original T3 SCREENER returned NaN Symbol for one monthly snapshot

**Description:**
T3 row idx 1134 had `Symbol=NaN, Company=NaN, Sector=Unknown, added_date=2025-09-01, removed_date=2025-10-01, MomentumScore=1.323, LastPrice=7.04`. Likely Polygon SIC lookup returned a record with NULL ticker symbol; T3 SCREENER didn't filter this out.

**Fix Pass 53 owner Q3 approved 2026-05-05:**
`temp_staging/fix_t3_null_symbol.py` — single `dropna(subset=["Symbol"])` operation. T3 rows: 1924 → 1923.

**Joint:** DEC-104/364 (T3 momentum methodology), DEC-496 (T3 SCREENER architecture).

