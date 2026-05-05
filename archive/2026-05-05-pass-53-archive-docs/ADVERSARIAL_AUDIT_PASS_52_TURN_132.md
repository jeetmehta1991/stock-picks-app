# Adversarial Audit — PROJECT_PLAN + TRADINGAGENTS_DATA_AUDIT + TRADING_RULES

**Document role:** Adversarial 5-pass review of three canonical documents (PROJECT_PLAN.md, TRADINGAGENTS_DATA_AUDIT.md, TRADING_RULES_AND_INFORMATION.md). Identifies gaps, contradictions, missing specs, edge cases, statistical methodology issues, governance ambiguities. Synthesizes Stage 2 effectiveness blockers.

**Created:** Pass 52 turn 132
**Owner directive Pass 52 turn 132:** "Do an adversarial review of the project plan and decisions and point out all gaps. Simulate every step and every micro step from current phase to end. Point out everything wrong or not done well... 5 passes automatically without my prompt... Be detailed... I don't care about time it takes but get it right. ... Think simulate execution from start to finish."

**Scope:** 3 documents only (NOT code review). 3,538 total lines audited.

**Method:** 5 iterative passes, each a different lens:
- Pass 1: Execution simulation (Sprint 0 → Stage 2→3 gate)
- Pass 2: Data dependencies + cross-document coherence
- Pass 3: Edge cases + failure modes + real-world operations
- Pass 4: Statistical / methodological rigor
- Pass 5: Process / governance / unstated assumptions

**Outcome:** 167 gaps identified + 10 Stage 2 effectiveness blockers synthesized.

**Honest accountability per #25:** Pass 52 turn 130 audit (TRADINGAGENTS_DATA_AUDIT) caught 1 architectural gap (data dependencies). This Pass 52 turn 132 audit operates at a higher abstraction layer — gaps in the gap-catching documents themselves. This is the 7th instance of Pass 52 owner accountability vindication, but PROACTIVE this time per owner directive.

---

## TABLE OF CONTENTS

**Part A — Pass 1: Execution Simulation (gaps 1-65)**
1. Sprint 0 Pre-Sprint-1 Setup
2. Sprint 1 Phase 0.A Polygon Foundation
3. Sprint 2 Engine Bug Fixes
4. Sprint 3 Phase 0.B Portfolio Class
5. Sprint 4 DEC-410 Audit Findings
6. Sprint 5 Universe Management
7. Sprint 6 Phase 0.E Catch-Mechanism + Hygiene
8. Sprint 7 Phase 1B Statistical + A/B + Custom Toolkits
9. Sprint 7-8 Phase 1B-α Cube + Dashboards
10. Sprint 8 Strategy Categories
11. Sprint 9 Phase 1B-α Run
12. Stage 2 → Stage 3 Verdict Gate

**Part B — Pass 2: Data Dependencies + Cross-Doc Coherence (gaps 66-95)**
13. Data Dependency Chains
14. Document Cross-Reference Integrity
15. Orphan Thresholds / Definitions
16. Conflicting Specifications

**Part C — Pass 3: Edge Cases + Failure Modes (gaps 96-125)**
17. API Failure Modes
18. Market Structure Edge Cases
19. Trade Execution Edge Cases
20. Backtest-Specific Edge Cases
21. Scaling / Volume Edge Cases
22. Data Source Edge Cases
23. Owner Operational Edge Cases

**Part D — Pass 4: Statistical / Methodological Rigor (gaps 126-150)**
24. Multiple Testing Problems
25. Sample Sizing
26. A/B Paired Design Issues
27. Walk-Forward Design Issues
28. Regime Methodology
29. Deflated Sharpe / PSR Details
30. Stationarity / Structural Breaks
31. Interval Estimation
32. Decay Detection

**Part E — Pass 5: Process / Governance / Assumptions (gaps 151-167)**
33. Process / Governance
34. Unstated Assumptions
35. Documentation Consistency
36. Verdict / Success Definition

**Part F — Stage 2 Effectiveness Blockers (synthesized)**
37. 10 Top Blockers Ranked

**Part G — Recommended Resolution Sequencing**
38. Critical-Path Fixes (must address before Sprint 1)
39. Pre-Sprint-7 Fixes
40. Pre-Phase-1B-α Fixes

---

# PART A — PASS 1: EXECUTION SIMULATION

## 1. Sprint 0 — Pre-Sprint-1 Setup

**GAP 1:** PROJECT_PLAN §10.2 says Polygon subscription is "[Owner action prerequisite for Sprint 1]" but no place documents WHEN this needs to happen relative to other Sprint 0 actions. Could block Day 1.

**GAP 2:** No documented procedure for Polygon API key: (a) storage location, (b) testing it works before relying on it, (c) what to do if Polygon goes down or rate-limits.

**GAP 3:** TRADINGAGENTS_DATA_AUDIT §30 DEC-460 test signals say "documented endpoint inventory; sample fetch with as_of validation; PIT correctness verified via freezegun" but DOESN'T specify which endpoints to verify (income / balance / cash flow / earnings dates / consensus estimates / transcripts — at least 6 endpoint categories).

**GAP 4:** What constitutes "PIT-correct" for fundamentals? Filing date vs fiscal period end vs press release date — these differ by days/weeks. No definition.

**GAP 5 (CRITICAL):** If DEC-460 verification fails, DEC-461 says "subscribe to FMP" — but FMP needs owner approval. No documented fallback if owner declines.

**GAP 6:** PROJECT_PLAN §14.2 lists 10 pre-Sprint-1 actions without per-action effort estimates. Cannot prioritize.

**GAP 7:** 10 actions listed without dependencies (which run parallel? sequential?).

**GAP 8:** Action 1 "Bug status audit" classification criteria (FIXED_IN_CODE vs OPEN_PENDING vs WONTFIX) not specified.

**GAP 9:** Action 3 "Define MVB" has no template or pre-existing definition.

**GAP 10:** Action 5 "Branch protection + PR review flow" — specific GitHub rules not documented.

**GAP 11:** Action 9 "Pre-commit hook installed locally" — versions, config files, repo location not documented.

**GAP 12:** Action 10 "Define RESOLVED-IMPLEMENTED criteria" should be CHECKLIST item codified, not one-time action.

## 2. Sprint 1 — Phase 0.A Polygon Foundation

**GAP 13:** TRADING_RULES §12.2 PIT loader: no class skeleton, no abstract methods, no acceptance criteria for "inherits properly."

**GAP 14 (CRITICAL):** PIT loader edge cases not documented:
- as_of = weekend/holiday?
- as_of before ticker existed (pre-IPO)?
- as_of after delisting?
- partial cache population?

**GAP 15 (CRITICAL):** Two universes (static 482 vs DEC-303 historical_membership.csv) — which is canonical?

**GAP 16:** PROJECT_PLAN §6.1 says S&P 500 = 482 tickers but actual S&P 500 has ~503 tickers (multi-class shares). 21-ticker discrepancy unexplained.

**GAP 17:** TRADING_RULES §13.2 "Switch yfinance auto_adjust=False" but Sprint 1 deliverable is Polygon, not yfinance. Polygon equivalent setting unverified.

**GAP 18:** "Recompute adjusted-on-demand by as_of date" — recompute formula not specified.

**GAP 19:** TRADING_RULES §13.3 "LRU on dynamically-fetched files" — how is "prefetched" vs "dynamically-fetched" distinguished at filesystem level?

**GAP 20:** §13.4 "Hard fail at 95% disk" — but downstream fetchers expecting fresh cache get stale data. Failure mode handling unclear.

**GAP 21:** §13.5 Filelock 5s timeout — what happens when fires? Re-attempt? Surface error? Skip?

**GAP 22:** PROJECT_PLAN §8.3 lists 9 FRED series; TRADING_RULES §10.1 lists 8 regime classifier inputs. ICSA in regime inputs but NOT in FRED list. Breadth/dispersion/AAII/CNN F&G not in FRED. Reconciliation needed.

**GAP 23:** "FRED expansion to 9+ series" — plus-sign suggests more. What are they?

**GAP 24:** TRADING_RULES §10.5 multi-asset adds DXY — but DXY already in PROJECT_PLAN's 9-series FRED list. Double-counting?

**GAP 25:** AAII source URL not documented anywhere. CNN F&G source URL not documented. Codespace allowlist may block these (per Wikipedia lesson).

## 3. Sprint 2 — Engine Bug Fixes Tier A

**GAP 26 (CRITICAL):** Sprint 2 = "14 critical engine bug fixes" but only 4-5 examples named. Other 10+ unnamed.

**GAP 27:** Sprint 2 claims "parallel-able with Sprint 1" but operates ON cache produced in Sprint 1. Schema changes Sprint 1 → Sprint 2 fixes obsolete.

## 4. Sprint 3 — Phase 0.B Portfolio Class

**GAP 28 (CRITICAL):** Portfolio class is described as deliverable in 3 places but **never specified**. Methods? State? In-memory or persisted?

**GAP 29 (CRITICAL):** OurTraderToolkit calls `get_portfolio_state()`, `get_cash_available()`, `get_existing_position(ticker)` — Sprint 3 spec doesn't lock these method names.

**GAP 30 (CRITICAL):** OurRiskToolkit calls `get_correlation_to_existing_positions()`, `get_sector_concentration()`, `get_drawdown_context()` — same gap.

**GAP 31:** "Existing positions, cash available, sector concentration, drawdown queryable" — no PIT-correctness requirement. Portfolio backtest needs PIT-correct portfolio state at any historical date.

## 5. Sprint 4 — DEC-410 Audit Findings

**GAP 32 (CRITICAL):** Sprint 4 effort 41.75-54.25d (largest non-Sprint-7) but **scope not enumerated in PROJECT_PLAN.md**. Reader must consult API_AUDIT.md externally.

**GAP 33:** Sub-phases 3.1-3.8 don't include Sprint 4. Phase 0.A/B/C/D/E/1B/1B-α/1C — but Sprint 4 maps to no phase.

## 6. Sprint 5 — Universe Management

**GAP 34:** Tier 2 spinoffs use "DEC-378-380 SEC EDGAR scrape" — Codespace network allowlist issue (per Wikipedia/AAII problem). Not verified.

**GAP 35:** Tier 3 momentum top-100 monthly refresh — which agents process Tier 3? Cost implications?

**GAP 36:** TRADING_RULES §6.3 includes "Russell 1000 add: $3M ADV" but Russell 1000 mentioned NOWHERE ELSE in any document.

## 7. Sprint 6 — Phase 0.E Catch-Mechanism + Hygiene

**GAP 37:** TRADING_RULES §2.5 lists 5 layers (DEC-417/436/437/438/439) but doesn't specify ORDER OF EXECUTION in CI pipeline.

**GAP 38:** "DEC-417 test-run audit gate" — what's a "test-run audit gate"? Not defined.

## 8. Sprint 7 — Phase 1B Statistical + A/B + Custom Toolkits

**GAP 39:** TRADING_RULES §7 "extract Risk debate confidence from LangGraph state" — Risk Debate has 4 nodes (Aggressive/Conservative/Neutral/Portfolio Manager). Which one's "confidence" is `s_risk`? PM is the synthesis — using PM's confidence for `s_risk` double-counts against PM's primary signal.

**GAP 40 (CRITICAL):** "EXTRACT RM_confidence from LangGraph state" — Research Manager output is INVESTMENT PLAN (text + structured). Research Manager Pydantic schema may NOT have a `confidence` field. **Same architectural-fit gap that surfaced DEC-042 → DEC-459 supersession.** If RM doesn't expose `confidence`, alignment check (§7.4) is unimplementable as specified.

**GAP 41:** OurTechnicalToolkit `get_intraday_ohlcv` — Polygon Stocks Starter rate limits not estimated. 482 tickers × 60 days × intraday = many calls.

**GAP 42:** `get_ict_smc_signals` returns FVG/BOS/CHoCH/OB — which timeframe(s)? Multi-timeframe per DEC-345?

**GAP 43:** `get_chart_pattern_signals` returns "8 patterns DEC-355-362" — but those are SEPARATE STRATEGIES in STRATEGY_REGISTER, not signals. Conflict.

**GAP 44:** `get_smart_money_composite` — composite formula? DEC-124 confluence + DEC-332 weights — what specific weights?

**GAP 45:** `get_macro_news` — Polygon Stocks Starter "macro" tag verification missing.

**GAP 46 (CRITICAL):** `get_current_price(ticker, as_of)` — for backtest, "current" = as_of date. Polygon Stocks Starter is delayed; bid/ask requires Level 1 quotes — does Stocks Starter have it?

**GAP 47 (CRITICAL):** `get_borrow_cost(ticker, as_of)` per DEC-399 — DEC-399 says "single-source consolidated module" without specifying SOURCE.

**GAP 48:** `get_correlation_to_existing_positions` — correlation OF WHAT (returns)? OVER WHAT WINDOW?

**GAP 49:** OurAgentState new fields are `dict` — untyped. TradingAgents uses Pydantic models. Untyped dict injection may break serialization.

**GAP 50:** Injection points "Phase 1 entry (before Analysts run)" — TradingAgents Analysts execute in parallel within Phase 1. Pre-Phase-1 injection could race with parallel tool calls.

**GAP 51 (CRITICAL):** Pre-commit min sample 300 paired trades. Stage 2 budget $300 hard cap (DEC-059). 5 arms × 300 paired × $0.25/propagate ≈ $1500-2000. **EXCEEDS BUDGET BY 5-7×.**

**GAP 52:** Per-regime A/B verdicts — sample size requirement at regime level unclear.

**GAP 53:** DEC-131 two-gate Bonferroni at scale (5 arms × N strategies × 4 regimes = thousands of comparisons) = effectively zero significance threshold.

**GAP 54:** Walk-forward 5-year train requires pre-2018 data. Polygon prefetch starts present. Pre-2018 fetch not in Sprint 1.

## 9. Sprint 7-8 — Phase 1B-α Cube + Dashboards

**GAP 55 (CRITICAL):** 17+ dimensions × 3-5 levels = 65K+ cells minimum. Cell sparsity not estimated.

**GAP 56:** 119 strategies × 65K cells × 17+ metrics = 100M+ metric computations. Compute cost not estimated.

**GAP 57:** Per-cell `max_adverse_excursion_avg` requires intraday data. Phase 0.A doesn't include intraday for ALL tickers.

## 10. Sprint 8 — Strategy Categories

**GAP 58:** "8 chart pattern strategies (DEC-355-362)" — pattern names not listed in PROJECT_PLAN.

**GAP 59:** BUG-111 break-and-retest: Option A vs B not committed. 37-55d effort implies Option A but not stated.

## 11. Sprint 9 — Phase 1B-α Run

**GAP 60 (CRITICAL):** Sprint 9 effort ~6d but it's the actual cube run. 119 strategies × 482 universe × 6 OOS years × selective agents — compute time not estimated.

**GAP 61:** "Phase 1B-α run + ongoing" — ongoing = decay monitoring? Strategy retune? Not bounded.

## 12. Stage 2 → Stage 3 Verdict Gate

**GAP 62 (CRITICAL):** Stage 2→3 gates: per-strategy or portfolio-aggregate? §22.3 suggests per-cell; owner transition needs portfolio-aggregate.

**GAP 63:** "Win Rate ≥ 50%" — DEC-353 R:R ≥ 2.0 minimum implies win rate can be 30% and still profitable. 50% threshold contradicts R:R philosophy.

**GAP 64:** "Agent-vs-rules divergence < 20%" — divergence of WHAT (selection? P&L? counts?). Definition missing.

**GAP 65:** Verdict classes are PASS / FAIL_RR / INSUFFICIENT_SAMPLE / FAIL_STAT. No FAIL_DD or FAIL_WINRATE. Taxonomy incomplete.

---

# PART B — PASS 2: DATA DEPENDENCIES + CROSS-DOC COHERENCE

## 13. Data Dependency Chains

**GAP 66:** Phase 0.D "distributed across Sprints 1, 4, 8" — fork integration partial. Which Phase 0.D pieces gate Sprint 7 toolkit work?

**GAP 67:** Cache freshness for OHLCV ≠ corp action history. Adjusted recomputation requires both fresh.

**GAP 68:** AAII publishes weekly Thursdays; 7-day cache freshness OK. CNN F&G publishes daily; 7-day cache = up to 6 stale days. Tolerance mismatch.

**GAP 69 (CRITICAL):** Smart money composite mixing — Bull/Bear should see raw signals OR composite, not confused. Aggregation level unclear.

**GAP 70:** Form 4 (actual) + Form 144 (proposed) different signal types. Composite mixing creates lookahead concern (Form 144 filed before sale executes).

**GAP 71:** Mixed regimes (e.g., neutral 0.5 + volatile 0.5) — which candidate cap applies?

**GAP 72:** Crisis-flag "reduce by 50%" — multiplied with tier (HIGH 5%) = 2.5%. Documented? No.

**GAP 73:** §18.1 4-arm vs §7.8 + PROJECT_PLAN §9.4 5-arm — internal inconsistency.

**GAP 74 (CRITICAL):** Cube verdict is per-cell; A/B framework is across-strategy. How compose? Naive: 119 strategies × 65K cells × 5 arms = 38M arm-cells. Sprint 7-8 ~28-38d cannot accommodate.

**GAP 75:** OurTraderToolkit `get_existing_position(ticker)` — Trader runs per ticker per propagate(). Pending decisions from same batch affecting Portfolio? Concurrency model unclear.

**GAP 76:** `get_correlation_to_existing_positions()` — empty portfolio (Day 1) gives undefined correlation. Default behavior?

**GAP 77 (CRITICAL):** Polygon Stocks Starter is delayed real-time. Stage 2 backtest uses historical (not delayed). Stage 4 live needs real-time. Documentation conflates.

**GAP 78:** Stage 2 BACKTEST mode bid/ask doesn't exist (historical). Bid/ask in backtest = ESTIMATED from spread model + slippage (DEC-092). Conflated.

## 14. Document Cross-Reference Integrity

**GAP 79:** PROJECT_PLAN §11 Quick Reference Index doesn't include TRADINGAGENTS_DATA_AUDIT.md.

**GAP 80:** PROJECT_PLAN §29.1 Document Map missing TRADINGAGENTS_DATA_AUDIT.md.

**GAP 81:** TRADINGAGENTS_DATA_AUDIT §17 "Polygon higher tier ($200/mo)" — TRADING_RULES §10.2 doesn't mention. PROJECT_PLAN §10.2 doesn't either. Cost summary §26 doesn't include this contingency.

**GAP 82:** TRADING_RULES §6.3 mentions Russell 1000. Not in PROJECT_PLAN §6 universe architecture or Sprint 5.

**GAP 83:** TRADING_RULES §1.2 win rate ≥ 50% but §17 Performance Metrics doesn't list win rate methodology. DEC-083 TIERED gives min trades, not win rate.

**GAP 84:** TRADINGAGENTS_DATA_AUDIT §15 PM mentions DEC-459 only once. Pre-DEC-459 architectural framing in §6 (Bull/Bear) and §11 (Trader) consistent with Option C? Unverified.

**GAP 85 (CRITICAL):** TRADINGAGENTS_DATA_AUDIT was written turn 130. DEC-459 was turn 129. Should be POST-DEC-459. But §11 Trader description reads pre-Option-C. Specifically §11 talks about "Risk-adjusted slippage estimate" being "needed by Trader" — but in Option C, slippage decision is at PM/engine level.

## 15. Orphan Thresholds / Definitions

**GAP 86:** Regime-conditional candidate cap "calm 20 / neutral 15 / volatile 10 / crisis 10" — empirical baseline source not given.

**GAP 87:** Crisis flag triggers (3 conditions) — OR or AND? Not stated.

**GAP 88:** Stationarity tests ADF + rolling Sharpe + Chow — no thresholds, windows, breakpoints specified.

**GAP 89:** "Sharpe" in §1.2 used before §17.1 defines units (annualized × √252).

**GAP 90:** INSUFFICIENT_SAMPLE — what happens to that strategy IN LIVE?

**GAP 91:** Strategy retirement criteria — owner discretionary, no audit trail.

## 16. Conflicting Specifications

**GAP 92 (CRITICAL):** Tier sizes 5/3/1.5%, crisis-flag reduces by 50%, mean reversion ATR multiplier 1.0× — does ATR multiplier apply to STOPS or POSITION SIZE? Compounding unclear.

**GAP 93:** §15.1 Canadian ETF: SPY → XUU (unhedged). QQQ → XQQ (CAD-Hedged). Default unhedged philosophy contradicted.

**GAP 94:** OOS folds 2019-2024 — which fold's results constitute the verdict? Latest? Average? Rolling?

**GAP 95:** Net Sharpe Contribution allocation_weight — strategy-level? Tier-level? Portfolio-level? Definition missing.

---

# PART C — PASS 3: EDGE CASES + FAILURE MODES

## 17. API Failure Modes

**GAP 96:** Polygon down — single point of failure. DEC-160 multi-vendor fallback DEFERRED to Stage 4.

**GAP 97:** Quiver API failure — Bull/Bear lose smart money signal. Degradation behavior?

**GAP 98:** OpenAI/Anthropic failure — agents can't run. Fallback (rules-only)? Retry queue?

**GAP 99:** FRED rate limits — what happens when hit during regime classifier run?

**GAP 100:** Macro news source unresolved (Gap E unfixed) — News Analyst lacks input but operates anyway. Soft fail mode?

## 18. Market Structure Edge Cases

**GAP 101:** Single-stock LULD halts — sell decision can't execute on halted ticker.

**GAP 102:** Pre-market / after-hours moves — backtest uses daily closes. Gap-down stop handling?

**GAP 103:** Stock splits during open position — how do split + dividend events propagate to Portfolio?

**GAP 104:** Spinoff during open position — bonus shares, not documented.

**GAP 105:** Delisting during open position — exit at last price? Hold for cash? Not documented.

**GAP 106:** Dividend record date — DEC-348 event suppression doesn't include ex-dividend dates.

## 19. Trade Execution Edge Cases

**GAP 107:** Position size > available shares (% of ADV cap) — DEC-366 has min ADV but not max position vs ADV.

**GAP 108:** Multiple strategies same ticker same day — open design decision per §5.4. Affects Portfolio class spec.

**GAP 109:** Trade size < 1 share value — skip trade? Not documented.

**GAP 110:** Slippage exceeds expected — over-slippage handling?

**GAP 111:** Partial fills — Portfolio class handling?

## 20. Backtest-Specific Edge Cases

**GAP 112:** Dividend ex-date lookahead — strategy fires on ex-date, model assumes next-day entry but cache shows lower price.

**GAP 113:** 13F survivorship — fund existed Q4 but disappeared by Q2. Current 13F computed how?

**GAP 114:** Earnings transcript missing for non-earnings stocks (REITs/MLPs/IPOs) — Fundamentals Analyst handling absence?

**GAP 115:** Borrow availability — Ortex shows "unavailable" — short trade rejected? Documented?

## 21. Scaling / Volume Edge Cases

**GAP 116:** Memory/disk requirements not documented. 230M trades upper bound.

**GAP 117:** Concurrent backtest runs (5 arms × 6 folds = 30 runs). Codespace memory finite. Sequential = 180 days. Parallel = blocked. Documented?

**GAP 118:** Stage 2 budget $300 / $0.25 ≈ 1200 propagate() calls. Not enough for per-strategy A/B.

## 22. Data Source Edge Cases

**GAP 119:** Backtest uses HISTORICAL closing data; live uses DELAYED. Decision distribution differs in production. Backtest doesn't model drift.

**GAP 120:** AAII weekly — backtest at daily granularity uses STALE 6 of 7 days. Model carry-forward not documented.

**GAP 121:** CNN F&G ~1 day lag. Treating today's value as available today = lookahead. Carry-forward not addressed.

## 23. Owner Operational Edge Cases

**GAP 122:** Owner unavailable mid-Sprint — backup approver model?

**GAP 123:** Owner directive changes mid-Sprint — partial implementation rollback?

**GAP 124:** Backtest results show NEGATIVE alpha — process for handling?

**GAP 125:** Stage 2→3 gates fail — fallback path? Re-run? Drop agents? Defer? Project termination?

---

# PART D — PASS 4: STATISTICAL / METHODOLOGICAL RIGOR

## 24. Multiple Testing Problems

**GAP 126 (CRITICAL — STAGE 2 BLOCKER):** 119 strategies × 65K cells = 7.7M combinations. Bonferroni-corrected α = 0.05 / 7.7M = 6.5e-9. Effectively no strategy×cell will pass. Need FDR (Benjamini-Hochberg) or hierarchical correction.

**GAP 127:** Bailey-Lopez de Prado t-stat 3.4 threshold for ~1000 candidates, not millions. Threshold needs scaling.

**GAP 128:** PSR ≥ 0.95 deflation by trial count N. With 7.7M trials, threshold becomes unattainable. Same scale problem.

**GAP 129:** If thresholds eliminate all cells, live lookup table empty. Operational consequence?

## 25. Sample Sizing

**GAP 130 (CRITICAL):** 119 strategies × 65K cells × 30 trades min = 232M trades. Across 6 OOS folds = 1.4B. Universe 480 tickers × 250 days × 6 years = 720K ticker-days. Trade frequency >>> ticker-day observations. **Mathematically impossible to populate cube.**

**GAP 131:** Per-cell sample requirement INCOMPATIBLE with cube dimensionality. Cube over-parameterized.

**GAP 132:** A/B 300 paired trades min = 1500 arm-trade observations. Paired design REQUIRES all arms fire on same input — but trade SETS DIFFER per arm.

## 26. A/B Paired Design Issues

**GAP 133 (CRITICAL — STAGE 2 BLOCKER):** Trade SETS DIFFER per arm. Paired comparison invalid. Need OPPORTUNITY-LEVEL pairing.

**GAP 134:** Sharpe SE at n=30 ≈ 0.26. Two strategies with identical TRUE Sharpe have observed difference 0.5 by chance 50% of time. Detection threshold 0.2 BELOW noise floor.

**GAP 135:** Per-regime n = ~75. Sharpe SE ≈ 0.16. Two-gate 0.2 barely above SE. Per-regime statistical power poor.

## 27. Walk-Forward Design Issues

**GAP 136:** 5-year train uses pre-2018 data. Polygon prefetch starts present. 2013-2017 data handling unclear.

**GAP 137:** Pre-2010 data quality uncertain. Walk-forward foundation weaker pre-2018 than assumed.

**GAP 138:** §16.4 holdout vs §23.2 final test period — definition collision.

## 28. Regime Methodology

**GAP 139:** Continuous→hard regime conversion via argmax? Threshold? Not specified.

**GAP 140:** EMA window? Smoothing factor?

**GAP 141:** Regime transition matrix from "historical regime transitions" — circular. Markov stability assumption.

**GAP 142:** Multi-asset extension activation criteria?

## 29. Deflated Sharpe / PSR Details

**GAP 143:** PSR formula not specified. Bailey-Lopez de Prado has PSR/DSR/SR* variants.

**GAP 144:** PSR uses skew/kurt. Compute order documented? No.

## 30. Stationarity / Structural Breaks

**GAP 145:** Stationarity test fires — action? Walk-forward handles non-stationarity but Chow break should trigger re-fit at break point.

**GAP 146:** "Max single-trade contribution" concentration metric — threshold?

## 31. Interval Estimation

**GAP 147:** `ci_95` computation method? Bootstrap? Asymptotic?

**GAP 148:** vs-SPY metrics — time period? Frequency (daily/weekly/monthly)?

## 32. Decay Detection

**GAP 149:** "Sharpe drop > 50% from baseline" — baseline = first OOS Sharpe? Rolling 12mo?

**GAP 150:** 20% Sharpe haircut applied at WHAT level (per-strategy / per-cell / portfolio)? Combined with PSR + Bonferroni — double-counting.

---

# PART E — PASS 5: PROCESS / GOVERNANCE / ASSUMPTIONS

## 33. Process / Governance

**GAP 151:** Implementation cadence "(owner direction needed)" — Sprint 7 starts before owner picks?

**GAP 152:** sync_from_claude.yml workflow — manual override path if workflow itself buggy?

**GAP 153:** RESOLVED-DECIDED → RESOLVED-IMPLEMENTED transition — test signal mapping to specific test files unclear.

**GAP 154:** TRADINGAGENTS_DATA_AUDIT and TRADING_RULES not enumerated in CHECKLIST #58 atomic commit list.

**GAP 155:** No documentation of what happens during Pass 53+ when new decisions emerge — adding without violating "100% terminal" achievement?

## 34. Unstated Assumptions

**GAP 156:** Stage 2→3 gates assume gates evaluated AT END of Sprint 9. Intermediate states (Sprint 7 partial, Sprint 8 partial) — verdict?

**GAP 157:** Stage transition gates assume linear progression. Reversibility (Stage 3 → back to 2)?

**GAP 158:** "Owner buys dips" is OWNER-TRADER behavior. Algo has crisis-flag size reduction, not "buy dip" rule. Philosophy/implementation mismatch.

**GAP 159:** Tax classification (trader vs investor) — if "trader" income, higher tax invalidates gross-Sharpe assumptions in Stage 2.

**GAP 160:** TSX vs US routing condition uses USD threshold but TSX trades CAD. Currency conversion timing not documented.

## 35. Documentation Consistency

**GAP 161:** TRADINGAGENTS_DATA_AUDIT references "Sprint 7" and "Sprint 7-8" without phase mapping. Phase ↔ Sprint mapping ambiguous.

**GAP 162:** PROJECT_PLAN §29 Document Map missing TRADINGAGENTS_DATA_AUDIT.md (severity tracking).

**GAP 163:** §23 REVISIT_AFTER_BACKTEST has 25 items in table. Inline mentions ~20. Numbering / count mismatch.

**GAP 164:** Quick Reference Index 23 topics ↔ 23 sections but not 1:1 — some are sub-sections. Reader may miss detail.

## 36. Verdict / Success Definition

**GAP 165:** "High-return performance" — quantified? No.

**GAP 166:** Success = achieving gates, but not what SCALE.

**GAP 167:** No documented criteria for "good enough to live trade with $100K vs $10K."

---

# PART F — STAGE 2 EFFECTIVENESS BLOCKERS (SYNTHESIZED)

The 167 gaps identified surface 10 top-priority blockers that, if unresolved, will invalidate Stage 2 backtest effectiveness. These are CRITICAL items requiring resolution before substantial Sprint 1 effort.

## 37. Top 10 Stage 2 Blockers (Ranked by Severity)

### B1: Multiple Testing / Sample Size Math Doesn't Reconcile
**Source gaps:** 126, 127, 128, 129, 130, 131
**Issue:** Cube architecture (17+ dimensions × 119 strategies × 65K cells) generates 7.7M test combinations. Bonferroni-corrected α = 6.5e-9 → no strategy×cell can pass. Sample size requirement (n≥30 per cell) requires 232M trades vs 720K ticker-day observations available — mathematically impossible.
**Stage 2 verdict will be:** "Cube populated but 0 cells PASS" — invalidating verdict framework.
**Resolution candidates:**
- Switch to FDR (Benjamini-Hochberg) correction
- Hierarchical correction at strategy-level then cell-level
- Reduce cube dimensionality
- Lower n threshold OR accept INSUFFICIENT_SAMPLE for most cells

### B2: A/B Budget Math Off by 5-7×
**Source gaps:** 51, 118, 132
**Issue:** $300 hard cap (DEC-059) vs 5 arms × 300 trades min × $0.25/propagate = $1500-2000 minimum.
**Stage 2 A/B framework cannot run within budget without scope reduction.**
**Resolution candidates:**
- Increase budget cap (cost re-evaluation)
- Reduce arm count (drop ablation arm to Sprint 9 only)
- Reduce min sample (with statistical power tradeoff)
- Selective A/B (only on top-tier strategies)

### B3: Trade Set Pairing Statistically Invalid
**Source gaps:** 133
**Issue:** Paired A/B design assumes same trade evaluated by all arms. Arms have different acceptance sets. Statistical comparison invalid as specified.
**Stage 2 A/B verdict on agent value-add will be statistically meaningless.**
**Resolution candidates:**
- Switch to opportunity-level pairing (every CANDIDATE evaluated by all arms)
- Use unpaired comparison with appropriate statistical adjustment
- Define "paired trade" precisely

### B4: Portfolio Class Spec Vacuum
**Source gaps:** 28, 29, 30, 31
**Issue:** Sprint 3 deliverable (BUG-095) but methods unspecified. Sprint 7 toolkits (DEC-465 Trader, DEC-466 Risk) depend on unnamed methods.
**Sprint 7 (largest sprint, ~96-108d) blocked on undocumented Sprint 3 dependency.**
**Resolution candidates:**
- Pre-Sprint-1 action: lock Portfolio class API spec
- Method-by-method enumeration in TRADING_RULES (or new PORTFOLIO_CLASS_SPEC.md)

### B5: TradingAgents State Schema Verification
**Source gaps:** 39, 40, 49, 50, 85
**Issue:** DEC-459 Option C extracts `s_risk` from "Risk debate" and `RM_confidence` from Research Manager output. Research Manager Pydantic schema may NOT have `confidence` field — same architectural-fit gap that surfaced DEC-042 → DEC-459 supersession.
**Stage 2 agent gate may fail to extract required fields.**
**Resolution candidates:**
- Pre-Sprint-1 action: verify TradingAgents Pydantic schemas for all extraction points
- If `confidence` missing on RM, redesign alignment check
- Document fallback (e.g., parse confidence from RM text)

### B6: Cube Cell Sparsity / Compute Cost Unestimated
**Source gaps:** 55, 56, 57, 116, 117
**Issue:** 65K cells × 119 strategies × 100M+ metric computations × 6 walk-forward folds. Compute cost not estimated. Codespace memory finite.
**Phase 1B-α run (Sprint 9) may be infeasible in Codespace.**
**Resolution candidates:**
- Estimate cube compute cost (CPU hours, memory peak, disk)
- Cloud migration earlier than Stage 4 if Codespace insufficient
- Cube dimensionality reduction (combine sparse dimensions)

### B7: PIT Fundamentals Verification Hard Dependency
**Source gaps:** 3, 4, 5
**Issue:** DEC-460 verification may fail. DEC-461 FMP fallback requires owner approval. Without PIT fundamentals, Fundamentals Analyst operates on lookahead-corrupted data — invalidates A/B verdict (per owner directive turn 130).
**Resolution candidates:**
- Execute DEC-460 verification immediately
- Owner pre-approval for DEC-461 FMP if DEC-460 fails
- Document FMP scope verification (transcripts + estimates + financials)

### B8: Walk-Forward Pre-2018 Data Source
**Source gaps:** 54, 136, 137
**Issue:** Walk-forward 5-year train requires pre-2018 data (e.g., 2013-2017 for first 2018 OOS fold). Polygon prefetch starts present-day. Bulk historical fetch not in Sprint 1 scope.
**Walk-forward foundation (Sprint 7) cannot start without Sprint 1 + extended historical fetch.**
**Resolution candidates:**
- Extend Sprint 1 to include 2013+ historical Polygon fetch
- Reduce walk-forward train window to fit available data
- Use yfinance for pre-2018 (with PIT caveats)

### B9: Russell 1000 / Universe Definition Inconsistent
**Source gaps:** 36, 82, 15, 16
**Issue:** Russell 1000 referenced in TRADING_RULES §6.3 ($3M ADV floor) but absent from PROJECT_PLAN §6 universe architecture and Sprint 5 universe management. S&P 500 = 482 vs 503 unexplained.
**Universe build incomplete; backtest universe scope ambiguous.**
**Resolution candidates:**
- Reconcile universe definitions across all 3 docs
- If Russell 1000 IS used, add to PROJECT_PLAN §6 + Sprint 5
- If Russell 1000 NOT used, remove from TRADING_RULES §6.3

### B10: Cost Estimate Reality Check
**Source gaps:** 51, 81, 118
**Issue:** Stage 2 cost summary $263 CAD/mo doesn't account for: Polygon higher tier ($200/mo if DEC-460 fails), FMP subscription ($14-50/mo conditional), A/B budget excess ($1500-2000 vs $300 cap).
**Real Stage 2 cost likely $500-1000+ CAD/mo, not documented.**
**Resolution candidates:**
- Update PROJECT_PLAN §26 Cost Summary with contingencies
- Add cost reality table with low/medium/high scenarios

---

# PART G — RECOMMENDED RESOLUTION SEQUENCING

## 38. Critical-Path Fixes (Must Address Before Sprint 1 Substantial Work)

These gaps block Sprint 1 effectiveness or create cascade risk.

### Tier 1 (Pre-Sprint-1 — Absolute Blockers)

| Gap # | Description | Effort | Output |
|---|---|---|---|
| 5, 7 (B7) | DEC-460 verification + DEC-461 owner approval contingency | 0.5d | Verification report + DEC-469 PROPOSED |
| 28-31 (B4) | Portfolio class API spec lockdown | 1-2d | New section TRADING_RULES §X or new doc |
| 39-40, 85 (B5) | TradingAgents Pydantic schema verification | 0.5-1d | Verification report + state extraction spec |
| 15-16 (B9) | Universe definition reconciliation across 3 docs | 0.5d | Surgical doc edits |
| 22-25 | FRED + AAII + CNN F&G source URL + classifier input reconciliation | 0.5d | Doc updates + Codespace allowlist test |
| 13-14 | PIT loader edge case spec + class skeleton | 0.5d | Class spec section |

**Tier 1 total: ~3-5 days.** This is critical-path pre-Sprint-1 setup that the existing 10-action plan (Pass 52 turn 125) doesn't fully cover.

### Tier 2 (During Sprint 1 — Resolve Before Sprint 7)

| Gap # | Description | When |
|---|---|---|
| 17-18 | Polygon raw OHLCV setting + adjusted recompute formula | Sprint 1 Day 1-2 |
| 32-33 | Sprint 4 scope enumeration + phase mapping | Sprint 1 |
| 36 (B9) | Russell 1000 add: in or out? | Sprint 1 |
| 54 (B8) | Pre-2018 historical fetch decision | Sprint 1 (extend or skip) |

### Tier 3 (Pre-Phase-1B-α — Resolve Before Sprint 9)

| Gap # | Description | When |
|---|---|---|
| 126-131 (B1) | Multiple testing methodology revision | Sprint 7 statistical methodology block |
| 51, 118, 132 (B2) | A/B budget reconciliation | Sprint 7 |
| 133 (B3) | Paired design replacement | Sprint 7 |
| 55-57, 116-117 (B6) | Cube compute cost estimate | Sprint 7-8 |

## 39. Document Updates Required

Once gaps are resolved, document updates needed:

### PROJECT_PLAN.md updates
- §6 Universe Architecture: add Russell 1000 if applicable
- §11 Quick Reference Index: add TRADINGAGENTS_DATA_AUDIT
- §14.2 Pre-Sprint-1 actions: add Tier 1 fixes from §38
- §22.4 Implementation cadence: owner direction
- §26 Cost Summary: add contingency table
- §29.1 Document Map: add TRADINGAGENTS_DATA_AUDIT + ADVERSARIAL_AUDIT
- §3 Sub-phases: add Sprint 4 phase mapping

### TRADING_RULES_AND_INFORMATION.md updates
- §1.2 Stage 2→3 gates: clarify per-strategy vs portfolio-aggregate; resolve win rate vs R:R contradiction; define "divergence"
- §3 5-Gate filter: add multiple testing methodology fix
- §6.3 Russell 1000: reconcile with §6 universe architecture
- §7 AgentGateConfig: verify state extraction points exist
- §10-11 Regime: clarify continuous→hard conversion, EMA params, transition matrix
- §12 PIT: add edge cases (weekend/holiday/pre-IPO/delisting)
- §13 Cache: clarify prefetched vs dynamic distinguishing
- §15.1 Canadian ETF: reconcile QQQ→XQQ hedged exception
- §16 Walk-forward: address pre-2018 data
- §17-18 Statistical methodology: address all Pass 4 gaps
- §22 Cube verdict: add per-cell vs portfolio-aggregate distinction; expand verdict taxonomy

### TRADINGAGENTS_DATA_AUDIT.md updates
- §11 Trader: re-align with Option C Hybrid (DEC-459)
- §15 PM: extend DEC-459 references throughout
- §17 Gap A: add Polygon higher tier as contingency
- §20-24 Toolkits: add method specs for unclear methods (intraday, ICT/SMC timeframes, smart money composite formula, current price for backtest mode, borrow cost source, correlation spec)
- §25 State Schema: switch dict→Pydantic; document injection timing relative to parallel nodes

## 40. Process Improvements

### CHECKLIST candidates from this audit

**CHECKLIST #61 candidate (Pass 52 L140 PROPOSED):** Adversarial document review before declaring documentation complete. Apply 5-pass methodology (execution simulation / data dependencies / edge cases / statistical rigor / governance assumptions) before marking canonical documents production-ready.

**CHECKLIST #62 candidate (Pass 52 L141 PROPOSED):** Cross-document consistency verification. When canonical docs are updated, verify cross-references remain consistent (Quick Ref index ↔ section count ↔ document map ↔ inline references).

### Process learnings

**L140 NEW (Pass 52 turn 132):** Documentation review must include adversarial simulation. Reading documents linearly catches typos and grammar; simulating execution catches architectural gaps. The 167 gaps identified in this audit were not visible during ordinary linear review — they emerged from "what happens when X" probing.

**L141 NEW (Pass 52 turn 132):** Statistical methodology requires capacity check. Sample size × dimensions must be reconciled with available data volume BEFORE methodology is finalized. Multiple testing problems at scale are not edge cases — they are fundamental design constraints.

---

## OWNER ACCOUNTABILITY VINDICATION (7th instance Pass 52)

**Pattern:** Owner verification questions catch architectural gaps Claude should be surfacing pre-emptively.

| Turn | Anti-pattern caught |
|---|---|
| 98 | Homeless RESOLVED-DECIDED |
| 108 | Substantively-homeless engineering decisions |
| 110 | Bug-decision linkage gap |
| 114-118 | 80 PENDING delegation |
| 128 | Architectural fit (DEC-042 → DEC-459) |
| 130 | Data dependency chain (DEC-460-468) |
| **132** | **Documentation rigor gap (this audit — 167 gaps + 10 blockers)** |

### What's different about turn 132

This audit was OWNER-PROACTIVE (not Claude-reactive). Owner directed comprehensive simulation in advance. **The 167 gaps existed BEFORE owner asked.** Without this audit, Sprint 1 would have started with:
- No Portfolio class spec (Blocker B4)
- Unverified TradingAgents Pydantic schemas (Blocker B5)
- Cube architecture mathematically impossible to populate at significance threshold (Blocker B1)
- A/B budget off by 5-7× (Blocker B2)

**Stage 2 effectiveness was at risk of being invalidated regardless of Sprint 1-9 execution quality.**

The 10 blockers are not implementation issues — they are PLANNING issues that would have wasted ~150-200 days of Sprint 1-9 effort before being discovered through failed Phase 1B-α verdict.

---

*End of ADVERSARIAL_AUDIT_PASS_52_TURN_132.md*

*Per CHECKLIST #25 (honest accountability for documentation rigor); #43 (precise grep across all 3 documents + cross-reference with AUDIT decisions); #51 (no decisions logged from this audit — recommendations only, owner approves each); #57 (use-case mapping per simulation step); #58 (atomic commit pattern with all 6 files); #59 (architectural assumption verification applied to documentation level); #60 (data dependency verification applied to spec coherence); L140 NEW (documentation review must include adversarial simulation); L141 NEW (statistical methodology requires capacity check).*
