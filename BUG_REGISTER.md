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
| BUG-02 | `days` variable used before definition → UnboundLocalError on every trade close | DEC-458 | (see linked DEC sprint) |
| BUG-03 | `ClosedTrade` dataclass defined twice — dead code, maintenance risk | DEC-458 | (see linked DEC sprint) |
| BUG-04 | `avoid` direction falls into `triggered_short` bucket — inflates confidence tier | DEC-458 | (see linked DEC sprint) |
| BUG-05 | `strategies_triggered` key mismatch — agent cache is always wrong | DEC-458 | (see linked DEC sprint) |
| BUG-06 | Double borrow cost on short trades | DEC-458 | (see linked DEC sprint) |
| BUG-07 | API key guard blocks no-agent Phase 1B run | DEC-458 | (see linked DEC sprint) |
| BUG-08 | `ema_50_200_bullish` signal key does not exist | DEC-458 | (see linked DEC sprint) |
| BUG-09 | `below_cam_s3` signal key does not exist | DEC-458 | (see linked DEC sprint) |
| BUG-10 | Agent signal keys wrong — agents always see `False` for key price context | DEC-458 | (see linked DEC sprint) |
| BUG-11 | `williams_r` short default fires incorrectly | DEC-458 | (see linked DEC sprint) |
| BUG-12 | Deduplication order bias — shorts never fire when long strategy fires first | DEC-458 | (see linked DEC sprint) |
| BUG-13 | `days_to_next_earnings` makes ~106,000 live yfinance calls during backtest | DEC-256, DEC-444, DEC-458 | (see linked DEC sprint) |
| BUG-14 | AAPL, CVS, JPM, NVDA missing from `run_full.sh` batch ticker lists | DEC-458 | (see linked DEC sprint) |
| BUG-15 | `max_drawdown` uses `cumsum()` instead of compounded equity curve | DEC-458 | (see linked DEC sprint) |
| BUG-16 | `PASSING_CRITERIA min_trades = 100` contradicts all documentation | DEC-458 | (see linked DEC sprint) |
| BUG-17 | `run_commit.sh` full mode hangs on interactive `input()` in merge script | DEC-458 | (see linked DEC sprint) |
| BUG-18 | Bonferroni correction hardcoded to 60 strategies, should be 72 | DEC-080, DEC-400, DEC-458 | (see linked DEC sprint) |
| BUG-19 | OHLCV cache incomplete — 402 of 495 tickers only cover to 2024-12-31 | DEC-260, DEC-442, DEC-448, DEC-458 | (see linked DEC sprint) |
| BUG-20 | Regime thresholds inconsistent between PROJECT_PLAN and config.py | DEC-458 | (see linked DEC sprint) |
| BUG-21 | `exit_strategies.py` own `_pnl` has no borrow cost — short comparison optimistic | DEC-458 | (see linked DEC sprint) |
| BUG-22 | `run_phase1a.py` header prints "60 strategies" | DEC-458 | (see linked DEC sprint) |
| BUG-23 | `screener.py` docstring says "60 strategies across 7 categories" | DEC-458 | (see linked DEC sprint) |
| BUG-24 | CHECKLIST item 13c says "review ALL agent outputs" — not applicable for no-agent | DEC-458 | (see linked DEC sprint) |
| BUG-25 | `run_tests.sh` does not pass `--no-agents` flag | DEC-458 | (see linked DEC sprint) |
| BUG-26 | CRITICAL — VIX proxy is VXX price (223–461), not actual VIX (18–36) — all regime | DEC-317, DEC-388, DEC-458 | (see linked DEC sprint) |
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
| BUG-46 | MEDIUM — `fetch_info_bulk` info cache uses current market_cap, not historical | DEC-260, DEC-442, DEC-458 | (see linked DEC sprint) |
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
| BUG-109 | HIGH — yfinance auto_adjust causes data drift; backtest results not reproducible | DEC-442, DEC-458 | (see linked DEC sprint) |
| BUG-110 | HIGH — Entry gap filter not enforced; trades opened despite exceeding ATR limit | DEC-458 | (see linked DEC sprint) |
| BUG-111 | **CRITICAL** — No break-and-retest variants of breakout strategies (severity: MEDIUM→HIGH→CRITICAL across Pass 52) | DEC-354 (parent umbrella reopened) + DEC-355/356/357 (3 retest-variant strategies) + DEC-358/359/360/361/362 (5 chart pattern strategies; retest-cross-cutting) | Sprint 8 (DEC-355-362) + open scope: 25 existing breakout strategies in screener.py potentially need retest variants — verification needed |
| BUG-112 | LOW — No ICT/SMC concepts implemented | DEC-458 | (see linked DEC sprint) |
| BUG-113 | HIGH — Agent action/sizing/exit recommendations ignored by engine | DEC-008, DEC-458 | (see linked DEC sprint) |
| BUG-113 | HIGH — Agent action/sizing/exit recommendations ignored by engine | DEC-008, DEC-458 | (see linked DEC sprint) |
| BUG-178 | HIGH — Earnings dates fetched live during backtest, no prefetch path | DEC-458 | (see linked DEC sprint) |
| BUG-179 | HIGH — yfinance .info fetched live during backtest universe load | DEC-443, DEC-458 | (see linked DEC sprint) |
| BUG-180 | HIGH — VIX not explicitly prefetched; VXX used as proxy is cause of BUG-26 | DEC-458 | (see linked DEC sprint) |
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
| BUG-270 | HIGH — `insider_signal()` column-name mismatch (100% silent failure) | DEC-458 | (see linked DEC sprint) |
| BUG-271 | HIGH — `get_gov_contracts()` no Date column lookup (99.4% silent failure) | DEC-458 | (see linked DEC sprint) |
| BUG-272 | HIGH — `get_lobbying()` Amount string concat (98.8% silent failure) | DEC-458 | (see linked DEC sprint) |
| BUG-273 | HIGH — `congressional_signal()` Chamber/House column mismatch | DEC-458 | (see linked DEC sprint) |
| BUG-274 | HIGH — `institutional_signal()` SharesChange column missing | DEC-458 | (see linked DEC sprint) |
| BUG-275 | LOW — `bonferroni_adjusted_threshold(n_strategies=0)` TypeError on complex round | DEC-080, DEC-458 | (see linked DEC sprint) |
| BUG-276 | HIGH — `_agent_cache_key` calls `sorted()` on list of dicts → crashes when strat | DEC-458 | (see linked DEC sprint) |
| BUG-277 | HIGH — `classify_regime()` truth-value-of-DataFrame error — 100% failure | DEC-458 | (see linked DEC sprint) |
| BUG-278 | MEDIUM — `yield_curve_regime()` doesn't use macro_combined.parquet cache | DEC-458 | (see linked DEC sprint) |
| BUG-279 | MEDIUM — `get_ohlcv()` with reversed date order silently returns 0 rows | DEC-458 | (see linked DEC sprint) |
| BUG-280 | LOW — `days_to_next_earnings()` returns None on yfinance failure | DEC-444, DEC-458 | (see linked DEC sprint) |
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

