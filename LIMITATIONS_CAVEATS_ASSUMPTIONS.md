# LIMITATIONS_CAVEATS_ASSUMPTIONS.md

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
**Caveat:** Pre-resolution, sp500_tickers.csv contained 485 CURRENT S&P 500 tickers. Every backtest 2010-2026 used this exact list. Companies that were in S&P 500 then but exited (Lehman, GM 2008, Sears, etc.) are invisible. Companies that weren't in S&P then but are now (TSLA before Dec 2020, NVDA before Nov 2001) are still tradeable in pre-membership backtests. Both directions inflate backtest performance.
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
**Caveat:** PROJECT_PLAN.md specifies 60 strategies in 7 categories (pivot 10, momentum 9, trend 9, mean reversion 11, breakout 6, candle 6, confluence 9). Code has 72 strategies. The delta is 12 short variants added per intra-pass owner approvals. **No PROJECT_PLAN drift gaps exist** — all 60 designed strategies are implemented. The 12 short variants extend scope; they don't drift.
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
**Caveat:** Sharpe daily and Sortino require per-day OHLC for every open position throughout each holding period. For 5-year backtest with avg 20-day holds and ~1000 trades per strategy, that's ~20,000 daily PnL points to track. Across 60-72 strategies, ~1.2M-1.4M data points. Manageable storage but not free.
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
