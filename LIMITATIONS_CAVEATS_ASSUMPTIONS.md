# LIMITATIONS_CAVEATS_ASSUMPTIONS.md

## 2026-05-15 Day 9+ Batches 172-178 — new caveats

**CAV-NEW-001 — Wikimedia REST per-IP throttle.** Public unauthenticated Wikipedia REST API rate-limits more aggressively than 1 req/0.5s and shows little tolerance even with proper User-Agent. Empirical safe-rate: 5s/request. 2 tickers still 429-blocked even at 5s; retry on subsequent refresh. Phase 1B+ if scaling: register Wikimedia API token / OAuth credentials. (See L153.)

**CAV-NEW-002 — Polygon grouped daily aggs is tier-blocked.** `/v2/aggs/grouped/locale/us/market/stocks/{date}` returns 403 NOT_AUTHORIZED on Stocks Starter (despite inventory previously claiming ACCESSIBLE). Requires Stocks Plus tier ($199+/mo) to access. Per-ticker OHLCV aggregation already DONE (H1) covers the liquidity-ranking use case so no Phase 1A impact. (Reclassified Batch 172.)

**CAV-NEW-003 — Inventory truth can be stale relative to filesystem.** `API_ENDPOINT_INVENTORY.md` "Currently cached?" column can lag actual `data_prefetch/*/` state by weeks. Dashboard builder reads inventory text not filesystem; if inventory says "NO" while parquet exists, dashboard reports false-NOT_CACHED. Truth-up requires empirical scan. (See L154.) Future improvement: dashboard builder auto-detects via filesystem rather than parsing inventory.

**CAV-NEW-004 — `__DEC-NNN` underscore prefix breaks matrix grep.** The verification matrix's `\bDEC-NNN\b` regex doesn't match `__DEC-NNN` (no word boundary before D). Writer.py dict keys using `__DEC-` prefix lose their first DEC tag. Affected single-DEC dict keys silently fall back to DECLARED-ONLY. Acceptable trade-off post Batch 167 — those constants have no genuine engine-call-path consumption anyway. (See L152.)

**CAV-NEW-005 — Phase 1A dashboard reads dev-mode AAPL-only backtest output.** Current `output_v2/*` contains the canonical 130-day AAPL backtest. Dashboard data.js (1.9 MB) reflects this small-scope run. Production-grade dashboard content requires a full multi-ticker × multi-year backtest then `python scripts/build_dashboard_phase_1a.py` to refresh.

---

**Purpose:** Persistent, append-only registry of caveats, limitations, and unverified assumptions across the project. Created Pass 52 per owner directive: "Document all caveats. Create a separate limitations/caveats/assumptions md file and keep adding to it."

**Why this file exists separately from AUDIT.md:**
- AUDIT.md is the historical decision/bug record. Caveats inline in audit prose are scattered across 20,000+ lines and hard to surface for stakeholder review.
- A live trading system that ships with known biases must be transparent about them. This file is the single place where every "we know this isn't perfect, here's why we accepted it" lives.
- When a backtest result is reported, this file should be referenced alongside it. A 2.0 Sharpe is a different claim if the system has documented survivorship bias than if it doesn't.

**Discipline:** Append-only. Caveats are not removed when the underlying issue is resolved — they are marked `RESOLVED Pass N` with a forward-link to the resolving decision/bug. This preserves the historical record of what assumptions were operating during which phase.

**Per L109:** "Nothing is ever deleted from these archive files. Updates supersede but don't replace." Same convention applies here.

**Format for each entry:**
- **Source:** Decision ID, bug ID, or pass that surfaced the caveat
- **Status:** ACTIVE / MITIGATED / RESOLVED Pass N
- **Caveat:** Plain English description
- **Operational impact:** What this means for backtest interpretation or live trading
- **Forward-link:** What resolves it (if not yet resolved, what should resolve it)

---

## Section 1 — Data quality and PIT correctness

### CAV-001 — Adjusted-close drift in OHLCV cache (RESOLVED Pass 52, but historical backtests pre-resolution affected)

**Source:** DEC-298 RESOLVED Pass 52
**Status:** RESOLVED Pass 52 (owner approved sequence); historical backtests pre-resolution still operated under this caveat
**Caveat:** Until DEC-298 implementation lands, OHLCV cache stored yfinance `auto_adjust=True` adjusted-close values. The same historical bar shows different values on different fetch dates as new corporate actions accrue. The same backtest run today and 6 months from now would not produce identical numbers from the same cache.
**Operational impact:** Backtest reproducibility broken for any pre-DEC-298 results. Phase 1B numbers reported before DEC-298 lands should carry "as fetched on YYYY-MM-DD" annotation. After DEC-298 implementation, raw OHLCV + corp actions are stored separately and adjusted-on-demand, fixing reproducibility forward but NOT retroactively.
**Forward-link:** DEC-298 RESOLVED Pass 52 (implementation pending). Regression test required: fetching AAPL OHLCV for as_of=2020-01-01 returns same numbers regardless of when the test runs.

### CAV-002 — Sector / market cap / IPO date are CURRENT not as-of (RESOLVED Pass 52, mitigation only)

**Source:** DEC-299 RESOLVED Pass 52
**Status:** RESOLVED Pass 52 with mitigation; full fix requires Polygon Reference subscription (deferred per BUG-191 sequencing)
**Caveat:** Until Polygon Reference subscription + integration lands, fetch_info() returns current sector / market_cap / IPO date regardless of as_of date passed. A 2018 trade in Match Group reads its current Communication Services classification instead of historical pre-spinoff classification. Sector-rotation strategies reading as-of-2018 sector get current 2026 sector instead.
**Operational impact:** Sector strategies have known systematic bias toward tickers whose CURRENT sector classification matches the strategy thesis. Market-cap filters operate on current market cap regardless of as_of date — small-cap strategies on large-cap tickers may admit positions retroactively that wouldn't have qualified at trade time.
**Mitigation in place (Step 1 of resolution):** Snapshot current fetch_info results to dated CSV. Freezes the survivorship problem to a known date instead of a moving target. Reports must include the snapshot date.
**Forward-link:** Step 2 — subscribe to Polygon Reference (~$30/mo) AFTER BUG-191 validation gate built and consumer code in place. Per BUG-191 sequencing rule.

### CAV-003 — yfinance earnings_dates returns CURRENT, not historical schedule

**Source:** DEC-300 RESOLVED Pass 52
**Status:** RESOLVED Pass 52 with three-step mitigation; analyst data REMOVAL pending Phase 1C
**Caveat:** yfinance's earnings_dates endpoint returns the company's known earnings schedule at the moment of the call. Past earnings dates are accurate (those happened). Future-dated earnings shown vs as_of may have been unscheduled at as_of time, and analyst targets / EPS estimates drift continuously. Earnings-momentum strategies that fire on "high analyst rating + earnings within 14 days" reach back to 2018 trades reading 2026 analyst targets.
**Operational impact:** PEAD strategies are particularly exposed — they assume the analyst miss/beat threshold from analyst's then-known estimate. Strategies are DEC-300-Step-1-mitigated by enforcing earnings_tolerant flag (most strategies don't call earnings_dates). Earnings-tolerant strategies (PEAD, earnings_momentum) still bear residual exposure until PIT earnings calendar built.
**Mitigation in place (Step 1):** earnings_tolerant flag enforced at all call sites; ~80% of strategies don't call earnings_dates anymore.
**Forward-link:** Step 2 — PIT earnings calendar via Polygon News (Phase 1C scope). Step 3 — REMOVE analyst data from PIT-claiming functions until paid PIT analyst-estimate source built. Until then, analyst-target-based strategies should be flagged as Phase-1C-only and not run in Phase 1B.

### CAV-004 — Survivorship bias in S&P 500 constituent list (RESOLVED Pass 52, fix limited by yfinance delisted-ticker availability)

**Source:** DEC-303 RESOLVED Pass 52
**Status:** RESOLVED Pass 52 with phased delivery; some delisted-ticker OHLCV may not be obtainable
**Caveat:** Pre-resolution, Current Snapshot_SP500 Tickers_May 2026.csv contained 485 CURRENT S&P 500 tickers. Every backtest 2010-2026 used this exact list. Companies that were in S&P 500 then but exited (Lehman, GM 2008, Sears, etc.) are invisible. Companies that weren't in S&P then but are now (TSLA before Dec 2020, NVDA before Nov 2001) are still tradeable in pre-membership backtests. Both directions inflate backtest performance.
**Operational impact:** Pre-resolution Phase 1B numbers are biased UP. Crisis-period backtests (2008, 2020 March) particularly affected — bankruptcy-bound tickers were absent from the universe, so the universe never saw the worst losers.
**Resolution path:** Build sp500_membership_history.csv from Wikipedia (free source, manually validated against secondary). Modify get_sp500_constituents(as_of) to filter by added_date/removed_date. Re-run all backtests.
**Residual caveat (cannot be fully resolved):** Some delisted tickers (Lehman, Bear Stearns, etc.) may not have full OHLCV in yfinance — yfinance often removes delisted-ticker bar data entirely. Resolution: either pay for CRSP-style historical data, OR document each missing-data gap and accept that some pre-bankruptcy tickers have incomplete bars. **Recommended:** document the gap; do not pay for CRSP this phase. Each missing-bar ticker should appear in a `delisted_data_gaps.csv` referenced from this file.
**Forward-link:** DEC-302 (joint resolution); future Phase if CRSP subscription approved.

---

## Section 2 — Methodology and statistical caveats

### CAV-005 — DEC-345 ICT/SMC methodology grounded in industry practice, not academic statistics

**Source:** DEC-345 RESOLVED Pass 52
**Status:** ACTIVE — by design
**Caveat:** ICT/SMC (Inner Circle Trader / Smart Money Concepts) is a trader-community framework. There is no peer-reviewed academic paper defining the methodology canonically. The fork-first answer (smartmoneyconcepts library, joshyattridge v0.0.27, MIT) is the implementation approach but the methodology epistemology is industry-practice, not academic.
**Operational impact:** ICT/SMC strategy verdicts in Phase 0.D should not be claimed as having peer-reviewed statistical foundation. They are systematic implementations of practitioner heuristics. The same standard applies to most chart-pattern strategies in DEC-355 through DEC-362 (trendlines, channels, ranges, wedges, head & shoulders, double tops, cup & handle, flags). All chart-pattern methodology is industry-practice grounded.
**Mitigation:** Per CHECKLIST #37, every methodology decision must explicitly state its grounding. ICT/SMC + chart patterns grounded in practitioner consensus + manual sources (TradingView, Bookmap, CMT curriculum, technical-analysis canon — Edwards & Magee 1948, Bulkowski 2005). Defensible, but different epistemic class than peer-reviewed factor research.
**Forward-link:** None — this is an accepted-by-design caveat. Audit any future claim that ICT/SMC strategies have stronger statistical grounding than they do.

### CAV-006 — DEC-345 multi-timeframe scope is 2-timeframe (Weekly/Daily) vs industry-consensus 3-timeframe (Daily/4H/1H)

**Source:** DEC-345 RESOLVED Pass 52
**Status:** ACTIVE — by design (scope discipline)
**Caveat:** Industry consensus for swing trading is 3-timeframe stack (typically Daily/4H/1H). DEC-345 chose 2-timeframe (Weekly/Daily) due to project's hard rule that intraday is out of scope. The 2-timeframe choice trades execution precision for scope discipline. Industry literature is generally written for traders who DO have intraday access; 4H/1H steps are about timing entry within the daily bar.
**Operational impact:** Entry timing within a daily bar will be less precise than 3-timeframe systems. Stop placement may have wider effective slippage because intraday rejection candles are not visible. This is acknowledged tradeoff for the project's daily-bar discipline.
**Forward-link:** None — accepted by design. If intraday scope ever opens (separate future project), revisit.

### CAV-007 — Bailey & Lopez de Prado: 75-trade-per-regime fallback is below ~100-trade floor for stable Sharpe estimation

**Source:** DEC-345 forward-link Pass 52, DEC-246 (parent decision pending)
**Status:** ACTIVE
**Caveat:** Per Bailey & Lopez de Prado (2014), recommended floor for stable Sharpe estimation is ~100 paired trades minimum. DEC-345 retained the existing 75-trade-per-regime fallback. Per-regime sample size requirements may shift once ICT/SMC comes online in Phase 0.D, where signal frequency could drop further under HTF-gated rules.
**Operational impact:** Per-regime verdicts at the 75-trade fallback have wider confidence intervals than industry-standard. Should be re-calibrated with empirical signal-frequency measurement at Phase 0.D entry.
**Forward-link:** DEC-246 (Quant finance correctness audit, PENDING) — should produce per-decision recommendations for sample-size floors.

### CAV-008 — DEC-353 R/R 2:1 minimum invalidates pre-resolution exit_fixed_target results

**Source:** DEC-353 RESOLVED Pass 52
**Status:** ACTIVE until code change lands
**Caveat:** Pre-Pass-52, exit_fixed_target defaulted to target_mult=3.0, stop_mult=2.0 → 1.5R reward per 1R risk. This is BELOW the new 2:1 minimum policy. All historical exit comparisons that included `fixed_3r_2r` as one of 8 exit methods were biased by a sub-minimum RR exit. **Conclusions about which exit method "wins" from pre-Pass-52 backtests are suspect.**
**Operational impact:** Any committed output file that ranks `fixed_3r_2r` as a winning exit method should be re-run after DEC-353 code implementation. Strategies whose verdicts depended on fixed_3r_2r results need re-evaluation.
**Forward-link:** DEC-353 implementation in Phase D — change default to ≥2R, add assert guard, sweep across 2:1, 3:1, 4:1, 5:1.

---

## Section 3 — Cascade-broken signal pipelines (Stage 5/5.5 findings)

### CAV-009 — Smart-money signal pipeline structurally non-functional pre-resolution

**Source:** BUG-005 CRITICAL + BUG-270/271/272/273/274/276 (Pass 52 Stage 5/5.5)
**Status:** ACTIVE — fixes pending in Phase C of focused-batch resolution session
**Caveat:** Per Pass 52 Stage 5.5 runtime probes:
- BUG-005 (CRITICAL): screener emits `strategies` field, pipeline reads `strategies_triggered` — agents reason without strategy context
- BUG-270: insider_signal column-name mismatch — 100% silent failure
- BUG-271: gov_contracts no Date column — 99.4% silent failure
- BUG-272: lobbying Amount string concat — 98.8% silent failure
- BUG-273: congressional_signal Chamber/House mismatch — silent crash on populated dates
- BUG-274: institutional_signal SharesChange column missing
- BUG-276: _agent_cache_key sorts list of dicts (currently masked by BUG-005; will crash when 005 fixed)

**Operational impact:** n=1000 sample of agent cache showed 0% high-conviction tier signals (LOW 93.7%, AVOID 5.7%). The $150 Phase 1B run produced essentially zero actionable swing-trade output. **Any backtest verdicts that claim agent value-add are suspect until the cascade is fixed.** Agent pipeline operated as binary AVOID/LOW system through Phase 1B.
**Forward-link:** Phase C of resolution sequence: BUG-005 + BUG-276 paired (~5 lines), BUG-270/271/272/273/274 (~30 lines total), BUG-277 caller-chain trace + fix. After fix, expect tier distribution to shift from 93.7% LOW to balanced — re-run Phase 1B with corrected pipeline. Until re-run, all tier-based verdicts should be flagged "pre-cascade-fix."

### CAV-010 — Test suite passes 56/56 while 8 HIGH bugs exist in code

**Source:** Pass 52 Stage 5.5 batch 2
**Status:** ACTIVE — DEC-098/221/222/265 test infrastructure pending
**Caveat:** `pytest backtest/tests/test_unit.py` reports `56 passed` cleanly. Yet 8 HIGH bugs (BUG-005 + BUG-270 through 274 + 276 + 277) exist in code. None caught by tests. Tests cover internal logic (tier adjustment, transaction costs, close_trade) but no test exists for the broken Quiver consumption functions.
**Operational impact:** Test suite green-light is NOT sufficient evidence of correctness. Test-driven confidence in any Phase before DEC-222 (regression tests for top-25 critical bugs) lands is misplaced.
**Forward-link:** DEC-222 PENDING — would have caught all 8 with simple non-default-return assertions. Phase A precondition.

### CAV-011 — validate_phase1b_data.py reports ALL CHECKS PASSED while wikipedia 0% populated

**Source:** BUG-072 HIGH OPEN, empirically confirmed Pass 52 Stage 5.5 batch 2
**Status:** ACTIVE — fix is Phase B precondition
**Caveat:** Pass 52 verification: `validate_phase1b_data.py` reports `13 PASSED, 1 WARNING, 0 BLOCKERS — ALL CHECKS PASSED — ready for Phase 1B`. Yet wikipedia cache is 100% empty (0/509 non-empty, marked ✅), gov_contracts only 40% non-empty (203/509, marked ✅). The validator's pass/fail logic is too lenient — it checks "files exist on disk" not "files have data."
**Operational impact:** This is the upstream of the L95 $150 burn. Validator green-lit a run that had broken downstream signal consumption. The "passed validation" claim itself is unreliable.
**Forward-link:** BUG-072 fix should be Phase 0.A blocker. Pass cannot reuse BUG-072-passed validations as evidence of data integrity.

---

## Section 4 — Data source caveats

### CAV-012 — Wikipedia views prefetch 100% empty since Pass 18 (BUG-185 CRITICAL)

**Source:** BUG-185 CRITICAL OPEN since Pass 18
**Status:** ACTIVE
**Caveat:** All 509 wikipedia parquets are 100% empty (0 rows AND 0 columns). Verified Pass 52 still unchanged 30+ passes later. Either Quiver wikipedia endpoint has changed or auth issue. Plus: no consumption code exists for wikipedia data anywhere in project.
**Operational impact:** Wikipedia signal effectively absent from agent inputs. Any documentation or reporting that lists "wikipedia views" as a smart-money input is inaccurate.
**Forward-link:** Per BUG-185: investigate Quiver API for correct endpoint, OR remove wikipedia from prefetch list. Stage 5.5 finding: **recommend removal** since no consumer code exists either way.

### CAV-013 — Finnhub news cache 100% empty (BUG-053 + BUG-181)

**Source:** BUG-053 HIGH + BUG-181 MEDIUM, both OPEN
**Status:** ACTIVE
**Caveat:** All 509 finnhub_news/*.parquet files are 1012 bytes (empty schema only). Verified Pass 52 still unchanged. Combined with AV news only 25/509 populated AND Phase 1B running with `disable_news=True` by default — news sentiment input to agents is functionally absent across the entire pipeline.
**Operational impact:** Sentiment Agent and any news-based reasoning operate with zero news input. `news_sentiment: "not_available"` shows up in 99.4% of cache files. Any agent verdict that cites news context is hallucinated.
**Forward-link:** BUG-053 + BUG-181 should resolve jointly with Phase 1C scope (news re-enable). Until resolved, news-related agent reasoning has zero input.

### CAV-014 — Quiver institutional 13F cache: 29 empty + populated tickers only have 5 months data (BUG-186)

**Source:** BUG-186 HIGH OPEN since Pass 18 + Pass 52 extended finding
**Status:** ACTIVE
**Caveat:** 29 of 509 institutional 13F files entirely empty including major tickers (AAPL, ABBV, AMZN). Of the 67% populated, all sampled have only ~5 months of data (e.g., MSFT 7602 rows but date range 2025-11 to 2026-03). Either Quiver tier caps historical institutional data, or prefetch script has date-range issue.
**Operational impact:** Backtest scope per DEC-158 is 16 years; institutional is unusable for historical backtest until both 29-empty-tickers and 5-month-coverage issues resolve. DEC-352 (13F price-level mapping) blocked by this.
**Forward-link:** Owner verify Quiver subscription tier covers historical 13F. Per BUG-191 rule: do NOT subscribe to higher tier until validation gate built.

### CAV-015 — DEC-308 prediction may be invalid (Pass 52 finding)

**Source:** DEC-308 PENDING since Pass 48
**Status:** UNCLEAR per owner Pass 52 ("2. Unclear")
**Caveat:** Pass 52 runtime probe found DEC-308's prediction (cache get_ohlcv_bulk silently rejects <20 trading days) appears not to manifest in current code. Either decision was based on misreading code, or code was changed without closing decision, or bug exists in different code path.
**Operational impact:** A decision that documents non-existent behavior creates false planning. Owner deferred verification.
**Forward-link:** Owner verification needed. Until verified, treat DEC-308 as documenting a possibly-resolved or never-existed issue.

---

## Section 5 — Architecture and code-hygiene caveats

### CAV-016 — engine.py vs engine/backtest.py duplicate dead code (BUG-204 + DEC-217)

**Source:** BUG-204 LOW OPEN, DEC-217 PENDING
**Status:** ACTIVE
**Caveat:** `backtest/engine.py` (427 LOC) and `backtest/engine/backtest.py` (679 LOC) both define `BacktestEngine` class. engine.py is dead code — imported by nothing. Continued shipping creates confusion (which file represents current logic?) and risk of accidental edit-in-wrong-file (same pattern as BUG-215 RESOLVED ClosedTrade duplicate).
**Operational impact:** Future engineer changing engine logic might edit the wrong file. New regression risk.
**Forward-link:** DEC-217 PENDING — remove engine.py + audit for similar duplicates.

### CAV-017 — site_generator._assign_tier duplicates engine._assign_confidence_tier (BUG-281)

**Source:** BUG-281 MEDIUM OPEN, Pass 52
**Status:** ACTIVE
**Caveat:** Two separate implementations of tier-assignment logic — one in engine (used by backtest), one in site_generator (used by daily picks site). When tier logic changes, must update both. Same pattern as BUG-215 (RESOLVED). Future drift risk.
**Operational impact:** Stage 1 daily picks site may show different tier than backtest engine for the same conditions if drift occurs. Discoverable only by direct comparison or in-prod inconsistency.
**Forward-link:** Extract tier-assignment to single shared utility module (config.py or new utils/tier.py).

### CAV-018 — Type hint coverage 0% in screener.py + engine/backtest.py (BUG-207)

**Source:** BUG-207 MEDIUM OPEN, Pass 47
**Status:** ACTIVE
**Caveat:** Two largest files in the codebase (1020 + 679 LOC) have zero type hints. Blocks mypy adoption. Encourages dict-typed-as-`dict` usage with no signature-level safety.
**Operational impact:** Refactoring is riskier; LLM-assisted code changes have less type-checking-as-spec to anchor on.
**Forward-link:** Phase E hygiene work; not high priority but should be addressed before scaling team.

### CAV-019 — 81 except blocks; some swallow real errors (BUG-209)

**Source:** BUG-209 MEDIUM OPEN, Pass 47
**Status:** ACTIVE — Stage 5.5 runtime probes caught several specific instances
**Caveat:** `grep -c "except" backtest/` returns 81 except blocks across the codebase. Many are bare `except Exception:` followed by `pass` or `return default`. This is the pattern that allowed BUG-270/271/272/273/274 to silently produce empty/default results across the entire smart-money pipeline.
**Operational impact:** Errors are silently absorbed; functions return defaults instead of raising. Caller can't distinguish "no signal" from "code crashed." Test suite passes because no exception escapes.
**Forward-link:** Audit each except block; convert silent-default patterns to raise or log-and-warn. Cross-cutting work; can be done incrementally as each function is touched for other reasons.

---

## Section 6 — Cost and operational caveats

### CAV-020 — Stage 5 cost estimate of $263 CAD/month assumes full API stack

**Source:** Pass 52 confirmation per owner
**Status:** ACTIVE
**Caveat:** $263 CAD/month estimate assumes full API stack: Quiver, Unusual Whales, Ortex, Finnhub, Polygon. Owner has stated NOT YET subscribed to Polygon ($30), UW ($50), Ortex ($40). Currently only Quiver + Finnhub are paid. Stage 5 actual cost ≈ $130-160/month current.
**Operational impact:** Cost reporting that cites "$263/month" assumes future state, not current state.
**Forward-link:** Per BUG-191: do NOT subscribe to additional APIs until consumption code exists and validation gate built. Per CAV-010, test infrastructure (DEC-098/221/222/265) is the precondition for any subscription decision.

### CAV-021 — Email is designated channel for trade approvals (not Telegram or other services)

**Source:** Owner direction prior to Pass 52
**Status:** ACTIVE — by design
**Caveat:** Stage 3 paper trading + Stage 4 live trading approval flow uses email, not Telegram, SMS, or app push notification. Email has higher latency than push (minutes vs seconds) and may be missed in crisis periods.
**Operational impact:** Time-sensitive trade entries (e.g., crisis-regime fast moves) may have approval gap. Owner has accepted this tradeoff for simplicity and audit trail.
**Forward-link:** None — accepted by design. If Stage 3/4 reveals approval-latency issues, revisit.

### CAV-022 — Codespace network allowlist blocks external fetches (e.g., Wikipedia, FRED in sandbox)

**Source:** L96 + Pass 52 yield_curve_regime probe
**Status:** ACTIVE — sandbox-specific, not production
**Caveat:** Codespace runs the agent code but its network allowlist blocks external domains not in: api.anthropic.com, archive.ubuntu.com, github.com, npmjs.com, pypi.org, etc. This blocks Wikipedia scraping (resolved with static CSV per DEC-052), FRED live fetches (BUG-278 — yield_curve_regime live-fetches FRED instead of using cached macro_combined.parquet), and some yfinance live operations.
**Operational impact:** Sandbox tests of any function that calls FRED live will silently degrade to "unknown." Live runs on owner's laptop don't have this restriction; production behavior may differ from sandbox-tested behavior.
**Forward-link:** BUG-278 fix (use macro_combined.parquet cache instead of live FRED) addresses one specific case. Others should be discovered as-needed.

---

## Section 7 — Strategy and scope caveats

### CAV-023 — DEC-355 through DEC-362 chart pattern strategies require shared infrastructure not yet built

**Source:** DEC-355 through DEC-362 PENDING Pass 52
**Status:** ACTIVE
**Caveat:** Owner Pass 52 directive ("each and every price action strategy to be tested — CRITICAL AND MOST IMPORTANT REQUIREMENT") logged 8 chart-pattern decisions. None are implemented. Each requires shared primitives:
- Swing high/low detector (likely fork from smartmoneyconcepts.smc.swing_highs_lows)
- Retest entry-signal primitive (BUG-111 CRITICAL OPEN)
- Linear regression / line-fit for trendline-based patterns
- Neckline detection for reversal patterns
- Cup detection (depth/duration/symmetry — likely custom; smartmoneyconcepts doesn't cover)

**Operational impact:** Until DEC-355-362 implemented, the project's price-action coverage gap that owner flagged as "critical and most important" remains. Estimated effort: substantial — these are 8 distinct strategy classes requiring custom plus library work. Phase D-or-later scope.
**Forward-link:** DEC-345 implementation (smartmoneyconcepts integration) is a precondition. After cache layer multi-interval + smartmoneyconcepts integration land, chart pattern primitives can build on top.

### CAV-024 — Strategy-coverage check: 60 PROJECT_PLAN strategies → 72 in code (60 + 12 short variants); no PROJECT_PLAN drift gaps

**Source:** Pass 52 strategy-coverage redo per L125/CHECKLIST #46
**Status:** ACTIVE (informational)
<!-- canonical-fact-historical: F-002 caveat documenting code-vs-PROJECT_PLAN delta — superseded by CANONICAL_FACTS.md F-002 layered roster -->
**Caveat:** PROJECT_PLAN.md specifies 60 strategies in 7 categories (pivot 10, momentum 9, trend 9, mean reversion 11, breakout 6, candle 6, confluence 9). Code has 72 strategies. The delta is 12 short variants added per intra-pass owner approvals. **No PROJECT_PLAN drift gaps exist** — all 60 designed strategies are implemented. The 12 short variants extend scope; they don't drift. (Pass 53 update: full layered roster per CANONICAL_FACTS.md F-002 = ~108-133 classes; 100+ unique testable strategies projected.)
**Operational impact:** Reporting that compares "designed vs implemented" strategy count should distinguish drift (none) from extension (12 short variants).
**Forward-link:** When DEC-355-362 + DEC-350/351/352/354 + retest variants land, scope expands materially. PROJECT_PLAN should be updated to document the expansion (post-resolution work).

---

## How to add to this file

When a new caveat surfaces:
1. Assign next CAV-NNN number (currently up to CAV-024)
2. Append to relevant Section (1-7), or create new section if it doesn't fit
3. Cross-reference: cite source DEC-N or BUG-N or pass
4. Set Status: ACTIVE / MITIGATED / RESOLVED Pass N
5. State operational impact in plain language for non-technical readers
6. Provide forward-link (what should resolve, when)

When a caveat is resolved:
- Do NOT delete the entry
- Update Status to "RESOLVED Pass N"
- Add resolution note describing what changed
- Preserves historical record of what assumptions were operating during which phase

---

*Created Pass 52 per owner directive: "Document all caveats. Create a separate limitations/caveats/assumptions md file and keep adding to it." Initial population from retroactive scan of AUDIT.md (56 caveat mentions consolidated) + Pass 52 specific caveats. Append-only convention per L109. 24 entries at creation; ongoing additions expected.*

## Section — Pass 52 universe expansion caveats

### CAV-025 — Futures-based commodity ETFs subject to contango drag

**Source:** DEC-363 PENDING (Pass 52, owner-approved scope: LIT + DBB + COPX only)
**Status:** ACTIVE
**Caveat:** DBB (base metals: Cu/Al/Zn/Pb/Ni) is a futures-based ETF. Front-month futures are consistently higher than spot during contango periods (typical for industrial metals). Holding DBB creates systematic drag — may underperform spot base metals even when those underlying metals rise. Equity miner ETFs (COPX in approved scope) avoid contango but introduce equity-market correlation.
**Operational impact:** Backtests using DBB as proxy for "base metals exposure" will systematically underestimate the edge of a true spot trade. When evaluating commodity-correlation strategies, COPX (equity miners) is the preferred-direction representation OR explicitly model the contango drag in the backtest.
**Forward-link:** Resolved when DEC-363 implementation includes contango-drag adjustment, OR DEC-363 narrowed to equity-only (COPX without DBB).

### CAV-026 — LIT lithium ETF concentrated in ~30 holdings

**Source:** DEC-363 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** LIT (Global X Lithium & Battery Tech) holds ~30 names spanning lithium miners, refiners, and battery makers. High idiosyncratic / single-name risk vs broad commodity ETFs (DBC has 14+ underlying commodities). AUM ~$1B as of mid-2025; sufficient liquidity but smaller than GLD/SLV/USO which have $50B+/$8B+/$2B+ respectively.
**Operational impact:** LIT moves on individual constituent news (e.g., Albemarle earnings, Tesla battery announcements) more than a broad-basket lithium price index would. Treat as battery-thematic equity proxy, not pure-play commodity.
**Forward-link:** No resolution path within current scope; alternative ETFs (LITP) are smaller. Accept as design tradeoff.

### CAV-027 — Tier 3 backtest historical-membership problem

**Source:** DEC-364 PENDING (Pass 52 — owner-approved scope: Tier 3 size 50 → 100 ONLY; broader Tier 2+3 backtesting activation NOT yet approved)
**Status:** ACTIVE — applicable when DEC-364 broader scope or DEC-104 (Tier 3 auto-population) is approved
**Caveat:** Backtesting Tier 3 momentum watchlist (100 tickers per Pass 52 owner direction) requires recomputing the watchlist as-of each historical month. A momentum watchlist computed today is not valid for 2018 backtest — the 2018 momentum names were different. ~100 tickers × ~190 months of backtest = 19,000 historical screens; computationally heavy, requires per-month rerun of `build_momentum_watchlist.py` against historical data.
**Operational impact:** If DEC-364 broader scope approved, Tier 3 cannot be naively activated for backtesting by populating a single CSV. Without historical-recomputation, backtests using current Tier 3 watchlist for historical periods will have severe lookahead bias (today's known winners read into 2018 backtest).
**Forward-link:** Resolved when historical-recomputation infrastructure built per DEC-364 broader-scope implementation (when/if approved).

### CAV-028 — Tier 2 spinoff/IPO detection needs paid source

**Source:** DEC-364 PENDING (broader scope NOT yet approved) + DEC-105 PENDING (spinoff detector)
**Status:** PROVISIONAL — applicable when DEC-364 broader scope or DEC-105 is approved
**Caveat:** yfinance does not preserve "first trade date" reliably for historical analysis (some delisted-then-relisted tickers like SNDK lose their original IPO date; spinoffs often inherit parent's listing date). Robust spinoff/IPO detection for Tier 2 requires Polygon Reference (paid), CRSP (academic-paid), or manual M&A archive scrape (brittle).
**Operational impact:** If/when Tier 2 activation approved, will rely on manually-curated CSV with limited historical coverage until paid source integrated. SNDK case (re-listed Feb 2025 post-spinoff) is the canonical example.
**Forward-link:** Resolved when DEC-105 (spinoff detector) lands with paid-source integration OR manual-curation workflow.

### CAV-029 — Russell 1000 historical PIT membership not free

**Source:** DEC-365 PROPOSED (Pass 52 — NOT approved by owner)
**Status:** PROVISIONAL — applicable only if DEC-365 approved
**Caveat:** Russell 1000 historical point-in-time membership is paid (FTSE Russell subscription). Without it, expanding universe to Russell 1000 mid-cap (500 names) creates survivorship bias at 500-ticker scale similar to DEC-303. Backtests for 2018 would use today's Russell 1000 list, excluding companies that exited between 2018 and now and including companies that weren't in then.
**Operational impact:** If DEC-365 Phase A (free, current static list) ever ships, it carries known survivorship bias. Phase B (paid FTSE) is the resolution path.
**Forward-link:** Caveat applies only if DEC-365 approved; resolved by Phase B (FTSE subscription) integration.

### CAV-030 — Universe expansion multiplies subscription costs

**Source:** DEC-365 PROPOSED (Pass 52 — NOT approved by owner)
**Status:** PROVISIONAL — applicable only if DEC-365 approved
**Caveat:** Each new ticker added to universe multiplies prefetch cost across all per-ticker data sources (Quiver smart money, Finnhub news, AV news, OpenBB fundamentals, yfinance OHLCV). The $263 CAD/month Phase 1C cost estimate was based on 500-ticker universe. Expansion to ~1100 instruments (Tier 1 + Tier 2 + Tier 3 + Russell mid-cap + ETFs) would roughly double all per-ticker subscription consumption + storage. Estimated revised cost: $400-500/mo. Russell 2000 expansion (Phase C) would push to $700-1000+/mo.
**Operational impact:** If DEC-365 approved, Phase B / Phase C carry separate cost decision before subscription. Owner cost approval gate required.
**Forward-link:** Caveat applies only if DEC-365 approved; resolved per Phase by owner cost approval at each gate.

### CAV-031 — Liquidity floor excludes legitimate small-cap opportunities

**Source:** DEC-366 PROPOSED (Pass 52 — NOT approved by owner)
**Status:** PROVISIONAL — applicable only if DEC-366 approved
**Caveat:** DEC-366 proposal sets liquidity floor at $300M market cap + $5M ADV. This excludes some legitimate small-cap momentum opportunities (sub-$300M companies with strong technicals). The choice would prioritize execution feasibility (fillable position sizes at Stage 4 capital scale) over coverage breadth.
**Operational impact:** If DEC-366 approved, system will miss high-momentum sub-$300M names. Acceptable tradeoff at Stage 4 ($10K-25K capital) where filling above 5% of ADV creates material slippage. Reviewable annually based on actual Stage 3 paper-trading fill quality.
**Forward-link:** Caveat applies only if DEC-366 approved; annual review per DEC-366; floor adjustable downward if Stage 3 fill quality permits.

## Section — Pass 52 Theme 4 batch 1 engine bug caveats

### CAV-037 — DEC-310 zero-volume cache fix is forward-only

**Source:** DEC-310/DEC-383 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** DEC-383 removes the silent `df = df[df["volume"] > 0]` filter from cache write path. Forward-only migration: existing cached Parquet files retain dropped zero-volume days. Halted days for past dates (pre-DEC-383 implementation) remain missing in current cache. Future events captured correctly.
**Operational impact:** Backtests run on existing cache will not see historical halted days. Halt-resume gap strategies (uncommon but documented edge) cannot fire on pre-fix historical periods. Optional remediation: rebuild full cache from yfinance after DEC-383 lands; high cost (~485 tickers × 16 years of OHLCV refetch + storage).
**Forward-link:** Optional remediation if owner approves cache rebuild.

### CAV-038 — DEC-313 yfinance high/low can include outlier ticks

**Source:** DEC-313/DEC-384 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** yfinance intraday high/low values occasionally include stale prints or outlier ticks (e.g., a bar's high might be 10% above the close due to a single bad tick from a market data error). Using these for trailing-stop updates would create false stop drift.
**Operational impact:** DEC-384 implementation must include outlier filter — high must be within 5% of close AND sanity-check vs prior day. If outlier detected, skip update for that bar (stop stays at prior level). Conservative tradeoff: occasional missed updates on legitimate volatile days; better than false stop drift.
**Forward-link:** Resolved via DEC-384 outlier-filter implementation.

### CAV-039 — DEC-314 Level 3 single-name halt false positives without paid feed

**Source:** DEC-314/DEC-386/DEC-387 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** Robust single-name halt detection requires paid NYSE/Nasdaq halt feed (~$X/mo, Phase C deferred). Free gap-based proxy (gap > 10% intraday without execution data) has false positives — earnings gaps and news-driven spikes are not halts but trigger the same proxy signal.
**Operational impact:** DEC-386 Phase B free proxy acceptable for Phase 1B with documented limitation. Backtests may falsely model "halt exits" on legitimate earnings gap days. Mitigation: cross-reference earnings calendar (DEC-256) — if gap occurs on earnings day, treat as earnings event not halt.
**Forward-link:** Resolved via DEC-387 Phase C paid feed integration (deferred to Stage 3+).

## Section — Pass 52 Theme 4 batch 2 caveats

### CAV-040 — VIX SMA + hysteresis lag tradeoff

**Source:** DEC-317/DEC-388 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** DEC-388 replaces single-print VIX thresholds with `vix_sma_5 = VIX.rolling(5).mean()` + hysteresis bands. This eliminates regime flip-flop on single intraday VIX prints near thresholds, but introduces 2-3 day delay vs single-print detection. In flash crashes (March 2020 day-by-day VIX moves from 12 to 82), the smoothed regime lags actual market stress — system may still be in "neutral" while actual VIX is at crisis levels for 2-3 days.
**Operational impact:** Crisis-period drawdowns may be initially underestimated by ~2-3 days as smoothed VIX catches up. Hysteresis bands (5-pt for crisis, 3-pt for high_vol) help avoid flip-flop but don't eliminate the lag. Per-regime calibration of lookback window (5 days vs 3 days vs 7 days) may be revisited in DEC-016 after Phase 1B-α verdict data.
**Forward-link:** Per-regime lookback calibration possible in DEC-016 (threshold calibration).

### CAV-041 — AAII HTML scraping fragility

**Source:** DEC-319/DEC-390 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** AAII Sentiment Survey at aaii.com/sentimentsurvey is HTML scraping target. Page layout changes break the parser. AAII does not publish a stable CSV download or API endpoint for free-tier access. Long-term reliability unknown; may need monthly health check after deployment.
**Operational impact:** If scraper fails, AAII cache goes stale. Validation gate (DEC-065) catches stale cache but requires manual intervention to re-establish source. Fallback: manual CSV download by data team if scraping breaks.
**Forward-link:** Resolved if AAII publishes stable API; otherwise long-term scraper maintenance overhead.

### CAV-042 — CNN F&G undocumented API risk

**Source:** DEC-320/DEC-391 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** CNN's `production.dataviz.cnn.io/index/fearandgreed/graphdata` is an undocumented endpoint reverse-engineered from the public cnn.com/markets/fear-and-greed page. CNN may change or remove this endpoint without notice. No SLA, no support contract.
**Operational impact:** If endpoint changes, CNN F&G refresh breaks silently. Need monitoring (HTTP 404/500 responses). Fallback: scrape the cnn.com/markets/fear-and-greed page directly. Acceptable risk since F&G is a sentiment input (not an execution-critical signal); strategies can degrade gracefully when F&G unavailable.
**Forward-link:** Resolved if CNN publishes documented API (unlikely); otherwise long-term endpoint monitoring.

### CAV-043 — Fail-closed liquidity filter rejection-rate monitoring

**Source:** DEC-321/DEC-392 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** DEC-392 changes `apply_liquidity_filter` from fail-open to fail-closed: missing market_cap → REJECTS ticker. This is the correct safety policy but will reject some legitimately-valid tickers where yfinance has temporary missing data: new IPOs in their first few days (info field not yet populated by yfinance), tickers in halt (info may be stale during halt), tickers with brief data outages.
**Operational impact:** Universe may shrink by 1-3% post-deployment due to transient data issues. Acceptable tradeoff vs current silent fail-open which let unfillable positions through. Monitoring requirement: log rejection rate by reason (missing_market_cap vs below_min_cap vs below_min_adv vs insufficient_history). If `missing_market_cap` rejections exceed 5% of universe, investigate yfinance quality (may indicate broader data issue, not just edge cases).
**Forward-link:** Annual review of rejection patterns; threshold adjustments if Stage 3 paper-trading shows different fill quality patterns.

## Section — Pass 52 Theme 4 batch 3 caveats

### CAV-044 — Market cap PIT blocked on fundamentals prefetch

**Source:** DEC-322/DEC-393 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** DEC-322 requires `market_cap_pit(ticker, as_of) = close × shares_outstanding(as_of)`. PIT shares outstanding is provided by DEC-257/DEC-383 (Theme 3 fundamentals prefetch). Until that lands, `info.get("marketCap", 0)` continues to return CURRENT value regardless of `as_of` parameter.
**Operational impact:** AAPL 2020-01-01 market_cap reads as ~$3T (current) instead of historical ~$1.3T. TSLA pre-2020 trades read >$1T (current) instead of <$100B (historical). Liquidity filter (DEC-366: $300M floor) admits or rejects based on today's value. Size-factor strategies (small-cap momentum, market-cap-weighted) get wrong inputs throughout history. Phase 1B-α can proceed with documented limitation in any backtest report; size-factor strategies should NOT run until DEC-322 resolves.
**Forward-link:** Resolved when DEC-257/DEC-383 (Theme 3 fundamentals prefetch) lands and DEC-393 (DEC-322 implementation) follows.

### CAV-045 — Free sector history covers 2018+ major reclassifications only

**Source:** DEC-323/DEC-394 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** DEC-394 Phase 1 builds free static `sector_history.csv` from GICS press releases. Coverage scope: Sep 2018 GICS Communication Services creation (FB, GOOG, NFLX, DIS, T, VZ, CMCSA, EA, ATVI, TWTR moves) + individual reclassifications post-2018 (manually researched). Pre-2018 reclassifications and minor sub-sector renames not covered.
**Operational impact:** Pre-2018 backtests using sector signals may have residual misclassification. Acceptable for Phase 1B-α since strategy universe focuses on post-2018 era; revisit if sector strategy verdicts depend heavily on coverage breadth. Phase 2 (DEC-395) Polygon Reference / FactSet provides full PIT but requires subscription.
**Forward-link:** Resolved when DEC-395 Phase 2 (paid sector PIT) approved + integrated.

### CAV-046 — 13F late filers conservative behavior change

**Source:** DEC-325/DEC-396 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** DEC-396 changes 13F PIT lookup from `quarter_end + 45 days` to actual `filing_date`. Some late filers (especially smaller funds with SEC extensions) file 60-180 days post-quarter. Strategies see position data later than current implementation; some positions never appear if filer is consistently late.
**Operational impact:** Smart-money strategies fire later, with some positions invisible. Compared to current implementation (which assumes Day 45 for all filers), new behavior is correctly conservative — eliminates lookahead bias from assumed-on-time filings. Backtest performance may decline slightly for strategies that benefited from the implicit lookahead.
**Forward-link:** No further resolution path — this is the correct PIT behavior; current implementation was the bug.

### CAV-047 — Rolling walk-forward result drift; --anchor-date for reproducibility

**Source:** DEC-326/DEC-397 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** DEC-397 makes walk-forward windows roll relative to `today`. The same backtest run 6 months apart produces different train/test windows because `today` advanced. Result drift is expected behavior — system uses most recent data for the next out-of-sample period.
**Operational impact:** Year-over-year comparisons of "the same backtest" need explicit anchoring. `--anchor-date YYYY-MM-DD` flag locks entire walk-forward computation to a specific reference date for reproducibility in audits, regression tests, and historical comparisons. Without the flag, results legitimately drift.
**Forward-link:** No resolution needed — the drift is the feature; --anchor-date is the reproducibility mechanism.

### CAV-048 — Potential historical short-trade PnL inflation if borrow zero-counted

**Source:** DEC-327/DEC-398/DEC-399 PENDING (Pass 52)
**Status:** ACTIVE — INVESTIGATION PENDING
**Caveat:** Code state shows `improvements.py:80-84` charges borrow cost while `exit_manager.py:140-146` says "handled elsewhere" without charging. DEC-398 investigation will determine whether production path is `improvements` (charged) or `exit_manager` (not charged) or both (double-charged) or neither (zero-charged). If zero-charged in production, all historical short-trade backtest results have inflated net PnL.
**Operational impact:** Magnitude estimate for typical case: 0.5% annual borrow rate × 20-day average hold ÷ 252 trading days ≈ 0.04% per short trade. Across ~30% of backtest trades being shorts and a 4-year backtest, cumulative net PnL inflation could be ~1-2% if zero-counted. Not catastrophic but real. DEC-398 investigation provides exact magnitude; DEC-399 fix consolidates to single shared utility ensuring exactly-once charging.
**Forward-link:** Resolved when DEC-398 (investigate) + DEC-399 (consolidate) lands; document delta in any historical backtest report.

## Section — Pass 52 Theme 5 batch 1 + API audit caveats

### CAV-049 — Bonferroni assumes independence; our strategies highly correlated

**Source:** DEC-080/DEC-400/DEC-401 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** Bonferroni correction for multiple testing assumes independent tests. Our strategy registry has 60 base strategies + 12 short variants (72 total) with high inter-strategy correlation — multiple momentum variants, multiple mean reversion variants, etc. Bonferroni over-corrects when tests are correlated, making it harder for valid edges to clear significance threshold. Holm-Bonferroni step-down is less conservative middle ground; FDR (Benjamini-Hochberg) is least conservative.
**Operational impact:** Default to Bonferroni for safety in initial Phase 1B-α; document tradeoff. After first run shows distribution of strategy results, owner approval gate to switch to Holm or FDR if Bonferroni rejects too many strategies that were intuitively edge-worthy. DEC-401 carries this owner-decision flag.
**Forward-link:** Resolved by DEC-401 owner approval after first Phase 1B-α run reveals correction-method tradeoff in practice.

### CAV-050 — Daily mark-to-market storage cost

**Source:** DEC-081/DEC-402/DEC-403 PENDING (Pass 52)
**Status:** ACTIVE
<!-- canonical-fact-scope: F-002 estimate cites code-current 60-72 range, not full layered roster -->
**Caveat:** Sharpe daily and Sortino require per-day OHLC for every open position throughout each holding period. For 5-year backtest with avg 20-day holds and ~1000 trades per strategy, that's ~20,000 daily PnL points to track. Across the current code (60-72 strategy classes; full layered roster ~108-133 per CANONICAL_FACTS.md F-002 will scale this proportionally), ~1.2M-1.4M data points. Manageable storage but not free.
**Operational impact:** Increases backtest output disk footprint by ~10-20MB per strategy. Compute cost increases proportionally to mark-to-market frequency. Acceptable tradeoff for industry-standard Sharpe/Sortino comparability.
**Forward-link:** No resolution path needed — accepted cost of canonical metrics.

### CAV-051 — Limited crisis coverage in current 4-year backtest scope

**Source:** DEC-082/DEC-405 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** Current backtest scope is 2021-01-04 to 2024-12-31 (4 years × 509 tickers per cache verification). 2008 GFC and 2020 COVID crashes are NOT in this range. Crisis sub-periods within scope are limited to: Q1 2022 invasion-related volatility, March 2023 SVB collapse, Oct 2023 Israel/Hamas escalation, plus 2022 full-year rate-rise bear. These are smaller-magnitude events than 2008/2020.
**Operational impact:** Stress-test verdicts cover only moderate-stress events. Strategies that pass current stress tests may still fail in true tail-risk events (2008-magnitude). Phase 1D (5-year extension) when activated will pull in 2020 COVID. 2008 GFC requires paid CRSP/Polygon Reference for delisted-ticker historical OHLCV (DEC-303 dependency). Document in any Phase 1B-α verdict report.
**Forward-link:** 2020 COVID coverage resolved when Phase 1D 5-year scope activates. 2008 GFC coverage resolved only with paid historical-data subscription.

### CAV-052 — Effective-N correlation correction for trade independence

**Source:** DEC-083/DEC-406 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** Tiered min-trades thresholds (300 daily / 100 regime-gated / 30 event-driven) treat each trade as an independent observation. In practice, trades on highly correlated tickers (e.g., same strategy fired on AAPL/MSFT/GOOG on the same day during a tech rally) are NOT statistically independent. Effective N is lower than raw trade count; statistical power is overstated.
**Operational impact:** DEC-406 reports `effective_n` (Bessel-corrected for cross-trade correlation) alongside raw `n_trades`. A strategy with 300 raw trades but effective_n=120 has the statistical power of ~120 independent trades. Verdict logic should reference effective_n for INSUFFICIENT_OOS_DATA gate, not raw count.
**Forward-link:** Resolved by DEC-406 implementation; calibration of correlation correction may need refinement after first run.

### CAV-053 — Macro correlation tag thresholds are heuristics

**Source:** DEC-085/DEC-407/DEC-408/DEC-409 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** Threshold values for macro correlation tags (vix_sensitive at |corr|>0.3; rate/curve/dollar/credit/inflation/growth/consumer/liquidity_sensitive at |corr|>0.2) are heuristics. Calibration may shift after first run reveals actual correlation distribution across our strategies. Tags labeled "macro-sensitive" should be communicated as data observations, not statistical guarantees.
**Operational impact:** Initial tagging may over- or under-flag strategies. Phase D refinement opportunity: adjust thresholds based on empirical distribution. Strategies tagged sensitive should still run; tag is informational for sizing/regime filters, not exclusion criterion.
**Forward-link:** Refinement after first Phase 1B-α run reveals correlation distribution.

## Section — Pass 52 Theme 5 batch 2 caveats

### CAV-054 — 5yr/1yr walk-forward requires data extension beyond current 4yr scope

**Source:** DEC-109/DEC-411/DEC-412 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** Canonical academic 5yr train / 1yr OOS walk-forward needs ≥6 years of data for 2 OOS rolling windows. Current cache is 2021-01-04 to 2024-12-31 = 4 years. DEC-411 extends to 2018-01-01 enabling 5yr/1yr train-test cycles. Until DEC-411 lands, walk-forward windows are limited to 2yr/1yr or 3yr/1yr (DEC-326's setting).
**Operational impact:** Phase 1B-α walk-forward methodology depends on extended data load. DEC-411 is precondition for DEC-412 rolling 5yr/1yr; sequenced AFTER DEC-298 PIT cache rebuild (joint operation). Strategy verdicts using shorter walk-forward have lower out-of-sample confidence; verdicts will change after DEC-411/412 lands.
**Forward-link:** Resolved when DEC-411 extends data load + DEC-412 implements rolling 5yr/1yr.

### CAV-055 — Deflated Sharpe assumes iid returns; momentum/mean-reversion have autocorrelation

**Source:** DEC-110/DEC-413 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** Bailey et al. (2014) Probabilistic/Deflated Sharpe Ratio formula assumes returns are independent and identically distributed (iid). Our strategy universe includes momentum strategies (positive serial correlation in returns) and mean-reversion strategies (negative serial correlation). The iid assumption is violated; PSR may be biased. Lo (2002) provides autocorrelation-adjusted Sharpe formulas but adds significant complexity.
**Operational impact:** Initial Phase 1B-α uses unadjusted PSR. Strategies tagged "passes PSR threshold" should be interpreted as "likely robust under iid assumption" — not as "definitively robust." Phase D refinement: implement Lo 2002 adjustment for top-N strategies to validate PSR claim.
**Forward-link:** Phase D refinement after first Phase 1B-α run reveals which strategies cluster near PSR=0.95 boundary.

### CAV-056 — 4-year sample limits structural-break detection power

**Source:** DEC-111/DEC-414/DEC-415/DEC-416 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** With 4-year sample (extending to 6 years post-DEC-411), structural break tests have limited statistical power. Chow split-sample test requires n_trades ≥ 600 (300 per half) to be meaningful. Many low-frequency strategies fall short. ADF and rolling-Sharpe tests have sufficient observations (~1000 daily PnL points) but detect only large breaks. Strategies that gradually decay over 2-3 years may not register as "broken" until the decay is severe.
**Operational impact:** DEC-414/415/416 detection is conservative — false negatives (missed breaks) more likely than false positives. Strategies passing all three tests should still be monitored in live trading; statistical tests describe past behavior, not future deployment risk. Phase 1D 5-year extension improves but doesn't eliminate this constraint.
**Forward-link:** No full resolution within current scope; long-term improvement requires multi-decade sample (10+ years) which requires paid historical data subscription.

## Section — Pass 52 Theme 6 + retroactive test-run scope caveats

### CAV-057 — Retroactive test-run validation may flag obsolete decisions

**Source:** DEC-417 PENDING (Pass 52, retroactive scope expansion)
**Status:** ACTIVE
**Caveat:** DEC-417 retroactive scope (all 419 decisions in AUDIT_INDEX.md per Pass 52 owner directive) means decisions logged in earlier passes (Pass 38/39/40/etc.) — some 6+ months old — must also be validated against current system behavior. System has evolved significantly since those decisions were logged: bugs fixed, scope expanded, strategies added. Some older decisions may be obsolete (problem already solved, scope deprecated, methodology superseded).
**Operational impact:** Per-decision validation must allow for `OBSOLETE_BY_TEST_RUN` flag — distinguishes "rec failed test" from "rec no longer applies." Examples likely:
- Pre-DEC-303 decisions about S&P 500 historical membership (now superseded by approved DEC-303 path)
- Pre-Theme-4-batch-1 decisions about cache front-extension (now superseded by DEC-381)
- Pre-Theme-5 decisions about Sharpe annualization (now superseded by DEC-402)
Process: when populating validation table, mark obsolete decisions clearly; do not treat as failures.
**Forward-link:** Resolved when DEC-417 implementation produces full validation table; obsolete decisions get explicit closure status.

### CAV-058 — DEC-129 absolute Sharpe threshold may be lenient at low baselines

**Source:** DEC-129/DEC-418 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** DEC-129 threshold |live_sharpe - backtest_sharpe| ≤ 0.3 is calibrated for typical Sharpe range 0.8-1.5. For low-Sharpe strategies (raw 0.5), 0.3 absolute deviation = 60% of edge — too lenient. For high-Sharpe strategies (raw 2.5), 0.3 is too strict (only 12% deviation allowed when 25-30% live degradation is typical).
**Operational impact:** Initial Stage 3→4 gate uses absolute 0.3 threshold. Phase D refinement candidate: relative threshold (e.g., max 30% Sharpe degradation) or tiered absolute (0.5 for high-Sharpe, 0.2 for low-Sharpe). Strategies near gate boundary should be reviewed manually before Stage 4 promotion.
**Forward-link:** Phase D refinement after first Stage 3 paper trading produces actual live Sharpe distribution.

### CAV-059 — DEC-130 5× capacity stress premature for early Stage 4 capital

**Source:** DEC-130/DEC-419 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** DEC-130 tests strategies at 5× initial capital (e.g., $25K → $125K). Owner's actual Stage 4 deployment capital is ~$25K initially per memory; reaching 5× (~$125K) requires sustained profitability over multiple years. Capacity stress at 5× may be theoretical for the first 1-2 years of live trading.
**Operational impact:** 5× test still valuable as forward-looking gate (preserves Stage 5+ scalability), but immediate Stage 4 deployment can proceed if 1× and 2× tests pass even when 5× fails (CAPACITY_LIMITED tag with size cap). Owner approval for tier system: which strategies tagged CAPACITY_LIMITED can deploy at 1×/2× capital with explicit Stage 5 reassessment.
**Forward-link:** Phase D refinement when Stage 4 capital actually approaches 5× of initial.

### CAV-060 — DEC-131 0.2 Sharpe improvement may be lenient at low baseline

**Source:** DEC-131/DEC-420 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** DEC-131 threshold "agent_sharpe - rules_sharpe ≥ 0.2" is reasonable when rules-only baseline Sharpe ≥ 1.0 (20% relative improvement). At low baseline (0.5), 0.2 improvement = 40% relative — questionable whether the agent overlay's $300 cost is justified. Tighter alternative: minimum absolute Sharpe ≥ 0.7 AND improvement ≥ 0.2.
**Operational impact:** Initial Stage 2 evaluation uses absolute 0.2 threshold. If rules-only baseline turns out poor, agent improvement should be evaluated against absolute Sharpe AND relative improvement. Failure mode (PROJECT_PLAN section 4: "abandon Stage 2 agent overlay") should trigger if absolute agent Sharpe is insufficient regardless of improvement delta.
**Forward-link:** Phase D refinement after Stage 2 backtest reveals actual rules-only baseline Sharpe distribution.

### CAV-061 — DEC-132 variance threshold 0.5 generous; may miss subtle instability

**Source:** DEC-132/DEC-421 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** DEC-132 variance < 0.5 threshold catches extreme cases (e.g., annual Sharpes [1.5, 0.2, 2.0, -0.3] = variance 0.97). Subtler instability (e.g., [1.2, 0.7, 1.1, 0.3] = variance 0.16) passes but shows clear declining edge. Tighter threshold variance < 0.25 would catch this (limits range to ~2× rather than ~5×).
**Operational impact:** Initial Stage 3→4 gate uses variance < 0.5. Strategies near boundary should be reviewed for trend (declining vs stationary). Joint with DEC-415 (rolling Sharpe deviation) — DEC-415 catches trend-decay better than calendar-year variance. Both tests in tandem provide stronger stability signal than either alone.
**Forward-link:** Phase D refinement candidate: tighten threshold or add trend-detection logic alongside variance check.

## Section — Pass 52 Theme 8 (DEC-422 dimensional framework) caveats

### CAV-062 — Combinatorial explosion limits combined-cell density beyond 3 dimensions

**Source:** DEC-422/DEC-425-431 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** DEC-422 dimensional framework slices on ~17 dimensions. Combined slicing of all dimensions simultaneously is statistically infeasible: 60+ strategies × 17 exits × 4 regimes × 11 sectors × 4 cap × 4 vol × 4 days-to-earnings × ... = millions of cells, with average ~10-20 trades total spread across all dimensional combinations. Bayesian shrinkage (Approach C) deferred to Phase D.
**Operational impact:** Methodology hybrid (Approach A + B) handles this:
- Marginal heatmaps (2D slicing per dimension) — statistically valid
- Combined 3D heatmaps for top-20% strategies — moderate validity
- 4D+ combinations infeasible without paid-tier data (longer history) or Bayesian shrinkage (engineering complexity)
Cells with n<30 trades fall back to marginal-best (next-broader cell). Live decision lookup table includes fallback hierarchy. Strategies relying on 4D+ specific conditions ("crisis regime + tech sector + earnings-imminent + high VIX") will likely produce INSUFFICIENT_CONFIDENCE flags; verdict reverts to marginal best across one or two dimensions.
**Forward-link:** Phase D refinement: implement Approach C (Bayesian shrinkage) for top-tier strategies after first Phase 1B-α run reveals which 4D+ cells matter most.

## Section — Pass 52 Theme 7 batch 1 caveats

### CAV-063 — DEC-067 partial implementation blocked on regime classifier + event calendar dependencies

**Source:** DEC-067/DEC-432-434 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** DEC-067 9 new exit methods include 2 with hard dependencies: `exit_volatility_regime` requires DEC-388 (VIX SMA + hysteresis regime classifier, currently PENDING); `exit_macro_event` requires DEC-409 (event-window tags, currently PENDING). Implementation order: methods 1-3 (chandelier/PSAR/supertrend) + indicator implementation first; methods 5-8 (volume_climax/rsi_extreme/partial_scaleout/kelly_target) second; methods 4 (vol_regime) + 9 (macro_event) deferred until deps land.
**Operational impact:** Until DEC-388 + DEC-409 land, EXIT_STRATEGIES dict has 15 methods (8 existing - 1 violator + 1 fixed + 7 new) instead of full 17. Phase 1B-α dimensional framework (DEC-422) operates on 15-method universe initially; expands to 17 when deps land.
**Forward-link:** Resolved when DEC-388 + DEC-409 implementations complete.

### CAV-064 — DEC-070 portfolio-level exit philosophy tension

**Source:** DEC-070 DEFERRED_TO_STAGE_3 (Pass 52)
**Status:** ACTIVE
**Caveat:** PROJECT_PLAN section 12 risk philosophy: "Buy dips in volatile and crisis markets. Most professional systems are forced out of crisis trades by drawdown rules; ours leans in within disciplined size constraints." DEC-070 portfolio drawdown limit (>30% flatten) is in tension with this philosophy. Two paths to reconcile at Stage 3 prep:
- Path A: drawdown limit informational-only (logs warning); does not auto-flatten; owner manually overrides
- Path B: hard limit at 30% auto-flattens regardless of regime; crisis dip-buying gated by current portfolio drawdown state
- Default proposal: Path B with owner-configurable thresholds (warn 20%, freeze entries 25%, flatten 30%)
**Operational impact:** No impact during Phase 1B-α (per-strategy independent evaluation). Owner direction needed at Stage 3 prep theme to resolve which path. Decision shapes whether the system's expressed risk philosophy ("buy crisis dips") is honored or overridden by capital-preservation logic.
**Forward-link:** Resolved at Stage 3 prep theme (post BUG-095 portfolio class fix).

## Section — Pass 52 Phase 0.E catch-mechanism defense + scope filter caveats

### CAV-065 — CI/CD test coverage gaps are blind spot for DEC-436

**Source:** DEC-436 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** GitHub Actions regression pipeline only catches what tests assert. If a behavior is not tested, regression won't be caught. Initial test suite (`test_unit.py` 46KB, `test_integration.py` 6KB, `test_e2e.py` 9KB) covers ~30% of code paths estimated. Full coverage requires sustained test-writing effort beyond initial DEC-436 setup.
**Operational impact:** DEC-436 is necessary but not sufficient. False sense of security risk: "CI passes" ≠ "code correct" — only "code passes existing tests." Mitigated by Layer 3 (DEC-437 property-based) which generates inputs beyond hand-written tests + Layer 4 (DEC-438 characterization) which catches silent behavior changes even without explicit tests.
**Forward-link:** Coverage improvement is ongoing; track test coverage metric in CI dashboard; flag uncovered code paths during reviews.

### CAV-066 — Property completeness limits DEC-437 effectiveness

**Source:** DEC-437 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** Property-based testing via `hypothesis` only catches bugs that violate the defined properties. If a bug exists in computation outside property scope (e.g., wrong sector aggregation that doesn't violate R:R or PIT properties), the bug is not detected by hypothesis. Properties chosen for initial implementation: R:R≥2, PIT correctness, Sharpe symmetry, position size monotonicity, stop direction invariance, FAIL_RR firing.
**Operational impact:** Layer 3 of defense is strong for the 6 chosen invariants but blind to bugs outside them. Mitigation: review property list quarterly; expand as new high-stakes invariants emerge (e.g., when DEC-422 dimensional cube ships, add cube-cell verdict invariants). Combine with Layer 4 (DEC-438 characterization) which catches output changes regardless of whether properties are defined.
**Forward-link:** Property list expansion as project evolves; aim for ~15-20 invariants by Stage 2 backtest run.

### CAV-067 — Golden master quality bounds DEC-438 test quality

**Source:** DEC-438 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** Characterization tests (golden-master / snapshot) capture whatever the current system produces as the "correct" output. If the current system has a bug, the golden master encodes the bug. Future runs that "fix" the bug will be flagged as regressions and require manual review to update the master.
**Operational impact:** Layer 4 catches silent behavior changes but cannot identify wrong-from-day-1 errors. Workflow requirement: golden masters must be reviewed by owner before being captured (not auto-captured); intentional changes require explicit approval to update master. Combine with Layer 3 (DEC-437 property-based) which catches bugs that violate invariants regardless of golden master state.
**Forward-link:** Quarterly review of golden masters to verify they encode intended behavior; refresh masters after major intentional changes.

### CAV-068 — Differential testing common-mode failure blind spot for DEC-439

**Source:** DEC-439 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** Differential testing compares two independent implementations and flags divergence. If both implementations have the same bug (common-mode failure — e.g., both use the same flawed library, both copy-paste from same wrong source), the divergence test passes while the bug persists. Risk highest when implementations are written by same person within short timeframe.
**Operational impact:** Layer 5 valuable only for high-stakes computations and only when implementations are genuinely independent. Mitigation: where possible, use one implementation that's mathematically rigorous (numpy/scipy reference) vs one that's project-idiomatic (pandas DataFrame ops); if both implementations are written project-idiomatic, common-mode risk is high. Combine with Layer 1 (pre-flight checklist) which catches obvious errors regardless of implementation.
**Forward-link:** Use established numerical libraries (numpy/scipy) where possible to reduce common-mode risk; periodic third-party review of high-stakes computations.

### CAV-069 — Pass 52 scope filter retroactive deferrals may need re-walking at Stage 3 prep

**Source:** Owner directive Pass 52 turn 8 ("Phase 0 and 2. Interpretation B")
**Status:** ACTIVE
**Caveat:** Multiple Pass 52 already-approved decisions retroactively deferred to Stage 3 scope per owner filter: DEC-129/130/132 (Theme 6 Validation criteria), DEC-070 (already DEFERRED prior turn), DEC-418/419/421 (sub-decisions). At Stage 3 prep theme, these will be re-walked with then-current code state; original approvals may need updating if system has evolved (similar to OBSOLETE_BY_TEST_RUN flag in CAV-057). Owner directive may surface additional Stage 3+ decisions that should also be deferred.
**Operational impact:** Pending count drops as decisions move to DEFERRED status (counts: ~6 decisions deferred this turn). Active workload reduces; focus narrows to Phase 0 + Stage 2. At Stage 3 prep theme, re-walk batch will be substantial — these decisions accumulate unimplemented during the deferral window.
**Forward-link:** Stage 3 prep theme will need its own focused walkthrough re-examining all DEFERRED_TO_STAGE_3 decisions with then-current system state.

### CAV-070 — Fundamentals filing_date approximation when source lacks explicit field

**Source:** DEC-257 PENDING (Pass 52)
**Status:** ACTIVE
**Caveat:** PIT correctness for fundamentals requires `filing_date` (when 10-K/10-Q became publicly known), not `period_end_date` (when fiscal period ended). Polygon `/v3/reference/financials` provides filing_date; yfinance Ticker.financials does NOT (period_end_date only). Fallback approximation: `estimated_filing_date = period_end_date + 45 days` (standard SEC filing window for 10-Q; 60-90 days for 10-K).
**Operational impact:** When yfinance fallback path activates (Polygon coverage gap or rate-limit), PIT loader uses approximate filing_date. This means a strategy may "see" fundamentals 45 days post-period-end, when in reality filing might have been earlier (e.g., 35 days) or later (e.g., 70 days). Could over-optimistic by ~10-20 days for late filers; under-optimistic by ~5-10 days for early filers. Magnitude: small lookahead/lookback risk.
**Forward-link:** Track which tickers fall back to yfinance during prefetch; flag in CAV-066 property tests; consider tightening to 60-day proxy if backtest results show material sensitivity.

### CAV-071 — Stale code comments can mislead audit if treated as authoritative

**Source:** Pass 52 turn 28 owner correction (Quiver tier misclassification)
**Status:** ACTIVE — methodological caveat
**Caveat:** During DEC-410 audit Batch 2, I (Claude) classified Quiver as "free tier" based on `backtest/data/smart_money.py` line 5 comment ("Quiver Quantitative free tier: congressional, insider, 13F, analyst revisions"). AUDIT.md substantive history has multiple references confirming Quiver paid subscription was active. Owner had to correct the audit. **The code comment was authoritative at time of writing (Pass <X>) but became stale when subscription tier changed; my pre-flight grep on smart_money.py preferred the code comment over AUDIT.md history.**
**Operational impact:** Future API tier audits must grep BOTH code comments AND AUDIT.md substantive history; AUDIT.md takes precedence per audit-as-source-of-truth principle (DEC-410 + DEC-441 + Pass 52 owner directive). When code comment and AUDIT.md disagree, AUDIT.md wins; flag the code comment for update.
**Forward-link:** smart_money.py line 5 comment should be updated post-DEC-450 implementation to reflect paid-tier consumption pattern.

### CAV-072 — Phase 1A omission via DEC-014 absorption (Pass 53 discovery)

**Source:** Pass 53 owner question "Why was phase 1A dropped"
**Status:** RESOLVED via DEC-486/487/488 PROPOSED
**Caveat:** PROJECT_PLAN_ARCHIVE.md confirmed Phase 1A v3 was COMPLETE — 67 instruments × 4 years × 6,942 trades; `atr_trail_1x` confirmed primary exit (20/29 strategy comparisons); 4 strategies flagged WEAK on OOS-2024-only. Pass 52 turn 119 absorbed DEC-014 (Phase 1B passing criteria) into DEC-422 (cube) + DEC-426 (5-gate validity); during this absorption, Phase 1A reference inadvertently dropped from PROJECT_PLAN §3 sub-phases. ADVERSARIAL_AUDIT (Pass 52 turn 132) didn't catch the omission because 5-pass methodology compared current docs against current docs, NOT against archive.
**Operational impact:** Without Phase 1A, A/B Arm A (rules-only) baseline would not have independent validation before agent overlay added in Phase 1B. Phase 1B-α $300 budget could commit before owner knows whether rules-only baseline is viable. Cube methodology bugs would surface during $300 run instead of zero-cost rules-only run preceding it.
**Resolution Pass 53:** DEC-486/487/488 PROPOSED restore Phase 1A as 3 distinct sub-phases (1A baseline → 1A-α rules-only cube → 1A-β scale validation). DEC-489 RESOLVED-DECIDED + CHECKLIST #63 + L142 codify methodology learning that adversarial audit must include archive comparison.
**Forward-link:** All future doc refactors that absorb prior phases must run archive-comparison check per CHECKLIST #63 before declaring "complete." Pattern signature: "DEC-X SUPERSEDED by DEC-Y" + multi-doc refactor = HIGH RISK for archival drop.

### CAV-073 — Audit methodology blind spot during phase compression refactors

**Source:** Pass 53 meta-failure analysis
**Status:** ACTIVE — methodological caveat
**Caveat:** When canonical phase taxonomy compresses (e.g., Phase 1A→1B→1C→1D becomes Phase 0→1B→1B-α→1C+), there's risk that absorbed phase content drops without audit detection. Pre-Pass-53 audit methodology (5-pass adversarial review) compared current docs against current docs — phases archived during compression were invisible.
**Operational impact:** Any phase, sub-phase, or DEC archived during a methodology refactor becomes invisible to within-current-doc audit. Absorbed content lives only in `*_ARCHIVE.md` files; current docs may reference DEC-X as "absorbed by DEC-Y" without flagging which content was absorbed (e.g., empirical results, decision history, methodology notes).
**Resolution:** CHECKLIST #63 (Pass 53) requires archive comparison as standard step in audit methodology. L142 codifies the learning. Future refactors that absorb prior phases must explicitly enumerate what content from absorbed phase is preserved vs dropped.
**Forward-link:** Pattern to watch: any commit message containing "absorbed" + phase reference. Apply CHECKLIST #63 archive comparison before merging.

### CAV-074 — Phase 1A excludes Finnhub social_sentiment (premium-locked; deferred to Phase 1B+)

**Source:** Pass 53 v8h+1 owner-approved 2026-05-09 (DEC-605)
**Status:** ACTIVE — Phase 1A scope caveat
**Caveat:** Phase 1A baseline (rules + smart-money, no agents) does NOT consume Finnhub `/stock/social-sentiment` data even if a Finnhub Premium subscription is added during the Phase 1A run window. Source first becomes eligible at Phase 1B+ News Analyst overlay. Reason: PREMIUM-LOCKED at our current Finnhub free tier (probed 5 high-liquidity tickers 2026-05-08, all 403); ~90% of cross-platform retail-attention signal is already covered by Apewisdom + StockTwits + Polygon news insights_json at zero incremental cost.
**Operational impact:** Phase 1A signal universe excludes one cross-platform retail-attention channel. Marginal — the three free-tier sources (Apewisdom Reddit, StockTwits Twitter-of-finance, Polygon news per-ticker sentiment) cover the same population the Finnhub aggregator would have queried.
**Runtime guard:** zero engine/agent/signal code references `finnhub.social_sentiment` (verified 2026-05-09); script `prefetch_finnhub_social_sentiment.py` is BUILT but is NOT invoked by Phase 1A pipeline. Cache directory `data_prefetch/finnhub/social_sentiment/` is empty.
**Reconsider triggers:** (a) post-Phase-1A Sharpe < 0.7 OOS gate AND post-mortem identifies cross-platform retail sentiment as the gap; (b) Phase 1B News Analyst starves for retail features specifically; (c) Finnhub adds compelling new endpoints at the same tier.
**Forward-link:** DEC-605 (this exclusion); DEC-599 (StockTwits + Apewisdom + Polygon news cover retail layer); CHECKLIST #13/#22/#23/#29 (paid API approval gate). The script flips ON instantly the day Finnhub Premium is added.

### CAV-075 — Sub-100% coverage on SEC EDGAR + Polygon reference is empirically delisting/acquisition (immutable at source)

**Source:** Pass 53 v8h+1 owner-asked verification 2026-05-10
**Status:** ACTIVE — coverage-ceiling caveat (informational; not a remediable gap)
**Caveat:** The 87-89% coverage on `data_prefetch/sec_edgar/*` (11 forms) and 87% on `data_prefetch/polygon/reference_extended/` is NOT a fetch-side bug. Cross-checked the 246 SEC-missing tickers against SEC's authoritative `company_tickers.json`: **0 of 246 are in SEC's active CIK map.** All are delisted, acquired, renamed, or foreign without SEC filer status (e.g. ABMD acquired by JNJ, ANSS by Synopsys, ADS renamed BFH, ALXN by AstraZeneca, AGN by AbbVie, AJRD by L3Harris, AIMC by Regal Rexnord). Polygon reference shows the same overlap — these tickers don't exist in either system because they no longer exist as separately-traded entities.
**Operational impact:** None to address. Phase 1A backtest correctly skips these tickers — they were never tradable in Phase 1A's window OR they were tradable but their data is in our universe under their renamed/successor symbol. Calls to `fetch_ohlcv` / `_load_aaii` / etc. for these tickers should return empty / not-available, which is the correct behavior.
**Resolution:** ACCEPT — this is the realistic ceiling for SEC-filer + Polygon-tracked subset of our 1937-ticker universe.
**Forward-link:** Coverage matrix tab in Sprint 0A dashboard (commentary column references "delisted/foreign/ADR/renamed" for these endpoints); CHECKLIST #76 column-(c) confirms the gap is upstream not downstream.

### CAV-076 — Finnhub financials_reported EXCLUDED COMPLETELY from all downstream phases (superseded by SEC EDGAR XBRL + Polygon financials)

**Source:** Pass 53 v8h+1 owner-approved 2026-05-10 (DEC-606)
**Status:** ACTIVE — total exclusion (Phase 1A + Phase 1B + Phase 1C+ + Stage 3 + Stage 4)
**Caveat:** Finnhub `/stock/financials-reported` data is EXCLUDED from ALL downstream phases — not just Phase 1A. Source coverage is 46% at our free tier (891 of 1937 tickers; remainder requires Finnhub Premium ~$10-30/mo). Authoritative substitutes: (a) `data_prefetch/sec_xbrl/` from SEC EDGAR XBRL companyfacts (1662 tickers, structured, deeper history, free, already cached); (b) `data_prefetch/polygon/financials/` from Polygon `/vX/reference/financials` (1937 tickers, JSON-encoded line items, already paid via Polygon Stocks Starter, already cached). Both substitutes provide deeper history + better PIT semantics + zero incremental cost.
**Operational impact:** Phase 1A pipeline does NOT call any Finnhub-financials reader (verified 2026-05-10 grep — zero engine/agent/signal references). Cache directory `data_prefetch/finnhub/financials_reported/` exists with 891 files but is read-only / orphan. Future agent prompts (Phase 1B+) must consume SEC XBRL or Polygon financials, never Finnhub financials.
**Runtime guard:** zero engine/agent/signal code references `finnhub.financials_reported` (verified 2026-05-10); script `prefetch_finnhub_full.py` is BUILT but is NOT invoked by Phase 1A pipeline.
**Reconsider triggers:** none; this is permanent. SEC XBRL + Polygon financials are structurally superior data sources.
**Forward-link:** DEC-606 (this exclusion); CAV-075 (delisting confirms 246-ticker SEC-unfileable ceiling); test_contract_finnhub_earnings_shape (Finnhub `earnings` endpoint, NOT `financials_reported`, remains valid).

### CAV-083 — Universe 53 days stale (Master CSV 2026-05-05 anchor; today 2026-06-27)

**Source:** 2026-06-27 B1028 R5 launch pre-flight audit + Council 120 verdict.
**Status:** ACTIVE - operational staleness; refresh QUEUED post-R5.
**Caveat:** Master Dedup CSV `Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv` was built 2026-05-05 (53 days stale vs 2026-06-27). PIT-correct for as_of ≤ 2026-05-05. May miss IPOs/spinoffs/momentum changes in the 53-day delta window. R5 launch B1028 documented this caveat in run_metadata.
**Operational impact:** B1028 R5 cube empirical patterns are statistically valid (N=1929 breadth dwarfs 0.5-1% staleness noise) but post-cube DRR (Differential Re-Run) against refresh-delta tickers gates Phase 1B-α promotion.
**Forward-link:** P1-UNIVERSE-REFRESH-POST-R5 (queued) + P1-DRR-DELTA-TICKERS-POST-REFRESH (queued).

---

### CAV-082 — Universe-scope verification gap (B1026 honest-finding pivot #18 + memory rule)

**Source:** 2026-06-27 B1026 wrong-universe HALT incident; owner correction; saved as memory rule `feedback_readiness_audit_must_verify_universe_scope`.
**Status:** ACTIVE - process gap (now mitigated by mandatory 3-way reconciliation).
**Caveat:** Pre-Phase-4+ launches MUST verify universe scope via 3-way reconciliation: (a) PROJECT_PLAN.md spec authority, (b) Master Dedup CSV cardinality, (c) S3 OHLCV cache cardinality. Council artifact chain assumption is NOT authoritative (Council 107/110/113-117 propagated wrong T1a 503 assumption groupthink before PROJECT_PLAN line 193 was reconciled).
**Operational impact:** B1024-B1027 HALT-chain cost $1.41 sunk on wrong-universe attempts before authoritative spec reconciliation. Future Phase-4+ launches must avoid same pattern.
**Forward-link:** B1028 R5 launch (corrected scope; first under new memory rule); `feedback_readiness_audit_must_verify_universe_scope.md`.

---

### CAV-081 — c6a.4xlarge default 8 GB EBS root insufficient for full bootstrap (B1024 HALT)

**Source:** 2026-06-27 B1024 disk-exhaustion incident.
**Status:** RESOLVED via migration to 50 GB gp3 root in B1028.
**Caveat:** AWS c6a.4xlarge default EBS root = 8 GB. Bootstrap requires ~10-11 GB (AL2023 base 3 + git/python/aws-cli 1-2 + venv/pip pandas-ta/scipy/ib_async/openbb/pyarrow 2-3 + data_prefetch sync 2.84 GB). Resulted in `OSError [Errno 28] No space left on device` at ~3 min into bootstrap. Historical AWS Phase 1A launches pre-B1024 may have silently truncated outputs.
**Operational impact:** B1024 $0.26 wasted before HALT-CRITICAL detection.
**Fix applied:** B1028 launch added `--block-device-mappings 'DeviceName=/dev/xvda,Ebs={VolumeSize=50,VolumeType=gp3,DeleteOnTermination=true}'`. Future c6a.* launches must include same parameter.

---

### CAV-080 — AWS spot interruption risk on long-running cube runs

**Source:** 2026-06-27 B1028 R5 launch infrastructure design.
**Status:** ACTIVE - mitigated by cost cap + sentinel architecture.
**Caveat:** AWS spot instances can be terminated with 2-minute notice. R5 cube run on c6a.16xlarge spot for 3-6 hours has non-zero interruption probability. Mitigated by: (a) $5/$10/$20 CloudWatch billing alarms, (b) `AutoTerminateAt=launch+10hr` instance lifetime tag, (c) per-phase S3 sentinel files allowing partial-state recovery, (d) spot ceiling $1.50/hr capping cost per hour.
**Operational impact:** If interrupted mid-run, sentinel state allows owner to inspect partial-phase output in S3 and decide re-launch from last-PASS phase.
**Forward-link:** B1028 run metadata; `feedback_monitor_intermediate_counts`.

---

### CAV-079 — H1 OHLCV Master Dedup prefetch: 8 historically-delisted tickers fail to fetch (DEC-609 H1.b)

**Source:** Pass 53 v8h+1 owner-approved 2026-05-10 (DEC-609 H1.b BG completion).
**Status:** ACTIVE - data-source-availability caveat (not a defect).
**Caveat:** The H1 polygon ohlcv_daily Master Dedup prefetch returned 1924/1932 successful (8 failures): AGN, CXO, ETFC, NBL, RTN, TIF, VAR, WCG. All 8 are M&A casualties / historically delisted equities (Allergan/AGN -> AbbVie 2020; Concho/CXO -> ConocoPhillips 2021; E*TRADE/ETFC -> Morgan Stanley 2020; Noble Energy/NBL -> Chevron 2020; Raytheon/RTN -> RTX 2020; Tiffany/TIF -> LVMH 2021; Varian/VAR -> Siemens 2021; WellCare/WCG -> Centene 2020). Polygon's 5-year rolling window now starts post-delisting for several; surviving tickers are at successor symbols (ABBV, COP, MS, CVX, RTX, etc.) which DO fetch successfully under their new symbols.
**Operational impact:** Master Dedup CSV includes both historical AND active tickers (1937 unique). The 8 missing equities are absent from `data_prefetch/polygon/ohlcv_daily/` but no signal is lost - they appear under successor tickers in the same cache. Phase 1A backtest consumers must be aware that PIT loader will return empty for the 8 delisted symbols on dates after their delisting; that's correct PIT behavior. No code action required.
**Reconsider triggers:** (a) if Phase 1A backtest needs PRE-delisting OHLCV for these 8 names (Polygon 5y rolling cap doesn't reach far enough back for some); fix would be either (i) extending Polygon subscription to a longer window or (ii) populating from a vendor that retains delisted history. Defer until Phase 1B/Stage 3 if backtest demonstrably starves for these 8 tickers' history. (b) Ortex / Bloomberg per-ticker history lookup if needed.
**Forward-link:** DEC-609 (H1 prefetch parent), CAV-075 (sister pattern - SEC EDGAR 246-ticker delisting cap), DEC-504 (Master Dedup with resolved_tier - Master Dedup explicitly includes historical tickers).

---

### CAV-078 — Phase 1A smoke realism floor raised from 100% to 300% absolute (INV-046 RESOLVED-DOCUMENTED)

**Source:** Pass 53 v8h+1 owner-approved 2026-05-10 (DEC-607)
**Status:** ACTIVE — analytics consumer-facing caveat (forever-active until next re-tune)
**Caveat:** The `test_g1_pnl_realistic` smoke gate previously enforced `abs(pnl_pct) < 100%`. Raised to `< 300%` after empirical evidence that legitimate momentum strategies on hot Tier 1a names (NVDA 2023 +200%/4mo, SMCI 2023 +500%/6mo) can produce >100% single-trade returns when held through a multi-month trend. Rapidity gate added (`pnl > 100% AND hold_days < 30`) catches the residual "real bug" pattern (split-adjust, fill-side, decimal mistakes).
**Operational impact:** Downstream analytics or dashboards that read raw smoke `trade_log.csv` should NOT assume a 100% upper bound on `pnl_pct`. Any consumer that hard-coded 100% as a "sanity check" must also raise to 300% (or use the rapidity-gate pattern). Aggregate metrics (Sharpe, Sortino, max drawdown) are not affected because they already accommodate full distribution.
**Reconsider triggers:** (a) Stage 4 live trading shows max single-trade return materially below 100% across a calendar quarter (then floor can be lowered back); (b) new hot-stock pattern emerges with >300% single-trade returns where the trade is verified real (raise floor again); (c) engine refactor that adds genuine leverage / options / 0DTE — full re-derivation required.
**Forward-link:** DEC-607 (this raise), INV-046 (parent diagnostic), `backtest/tests/test_e2e_phase1a_smoke.py::test_g1_pnl_realistic` (the gate).

---

### CAV-077 — Quiver `etfholdings` cache is a static snapshot from unknown date; no working refresh endpoint at our paid tiers

**Source:** Pass 53 v8h+1 owner-approved 2026-05-10 (INV-047)
**Status:** ACTIVE — data-source-deadend caveat (Phase 1B+ research only)
**Caveat:** The existing 1563 files at `data_prefetch/quiver/etfholdings/` (5-col schema: ETF Symbol / Holding Name / Holding Symbol / % of ETF / Value $) came from an unknown / deprecated Quiver endpoint that no longer responds. Probed all candidate Quiver Trader paths (historical/live + camelCase variants + no-version-prefix) — all 404. Probed Polygon Stocks Starter ETF holdings paths — all 404. Cannot refresh from any tier we currently subscribe to.
**Operational impact:** etfholdings data is **a static snapshot**, not a live feed. Phase 1A backtest doesn't consume etfholdings (P2 Phase 1B+ ETF flow proxy). Phase 1B+ research using etfholdings must treat it as a single-point-in-time reference, not a time-series. PIT loader returning "not_available" for as_of < snapshot_date is the correct semantic.
**Resolution paths (owner-pending):** (a) accept static snapshot as-is; (b) paid 3rd-party (FMP / EOD / etfdb ~$30-50/mo); (c) scraping infra (fragile, creates maintenance burden); (d) Quiver support query for correct endpoint (zero cost, unbounded latency). Default = (a) until Phase 1B+ research demonstrates etfholdings provides material lift over zero-cost alternatives.
**Forward-link:** INV-047 (this dead-end record); CHECKLIST #77 (canonical-source rule caught the 404 honestly); DEC-606 sister pattern (Finnhub financials_reported permanently excluded; etfholdings is structurally similar P2-criticality decision but with no superior zero-cost alternative).
