<!-- Source: per CHECKLIST #77 canonical-source; Council 287 B1233 2026-07-07 doc-sync sweep -->

<!-- 🟢 COUNCIL 278-287 SYNC BANNER (B1233 2026-07-07) — READ FIRST BEFORE THIS DOC -->
> **Doc-sync status:** This document may contain references stale as of 2026-06-27 or earlier. The current state below overrides any stale references in the body until the next full-rewrite.
>
> **Current canonical values (as of 2026-07-07 B1231):**
> - `len(ALL_STRATEGIES) = 219` (was 220 pre-B1189 DELETE of dxy_headwind_multinational_short; was 221 pre-B874)
> - `STRATEGIES_DISABLED_MISSING_PRODUCER = set()` (was `{dxy_headwind_multinational_short}` pre-B1189)
> - Active strategies for Phase 1A-β cube: 219; cube cells 219×26 = 5,694
> - Test count: **858 passed, 2 skipped** on `test_unit.py + test_integration.py`
> - **CHECKLIST items:** #1–#157 (added #151-#157 in Councils 279-285)
> - **LEARNINGS lessons:** through L202 (added L197-L202 in Councils 279-285)
> - **Latest batch:** B1231 (Council 285)
>
> **Recent Council 278-287 milestones (chronological):**
> - Council 278 (B1188-B1204): 40 SKIP strategies loosened per CSV recommendations
> - Council 279 (B1205-B1210): 11 silent misses remediated + L197 + CHECKLIST #151-#153
> - Council 280 (B1211-B1213): News coverage refined (84.2%) + CHECKLIST #154 codified
> - Council 281 (B1214-B1216): short_interest_pct producer bug + institutional 30% gap surfaced
> - Council 282 (B1217-B1219): Cross-audit 192 strategies + CHECKLIST #155
> - Council 283 (B1220-B1223): 5 more producer audits + comprehensive report
> - Council 284 (B1224-B1228): All 25+ producers audited + historical 2020-2023 spot-check + L201 + CHECKLIST #156
> - Council 285 (B1229-B1231): 2 critical bugs FIXED with graceful degradation + L202 + CHECKLIST #157
> - Council 287 (B1232-B1236 in progress): Stage 4 walks archived + doc-sync sweep
>
> **Stage 4 walks: ARCHIVED 2026-07-07 to `archive/2026-07-07-stage-4-walks-complete/`** (Council 121+ 2026-06-27 owner-approved completion). Any `STAGE_4_*.md` reference in this doc now points to archived location.
>
> **Producer coverage (all 25+ producers audited Councils 280-284):**
> - news_sentiment 84.2% / short_interest_dtc 97.7% / **short_interest_pct 0%** (bug; graceful-degradation fix in B1229) / pead 85% / insider 18.8% (event-rarity) / **institutional_signal 85%** (B1230 corrected from B1216's 30% misattribution) / congressional 67.7% / sec_edgar 97.7% / search_volume 99.2% / index_rebalance 10.5% (event) / earnings_yoy 78.9% / cot_positioning 100% / cross_asset 100% (5 fns) / calendar_effects 100% / macro_events 100% / OHLCV-derived (chart_patterns/technical/dec513/multi_timeframe/cross_sectional/ict_producers/volume_profile/smc_ict/pairs_trading) all 100% (bounded by ~84% OHLCV cache)
> - **Critical historical finding (B1227):** news_sentiment 0% in 2020; short_interest_dtc 0% in 2020; institutional 0% in 2020-2021. Backtest interpretation must annotate producer coverage TIMELINE.
>
> **Sprint 5 tickets queued (post-Council 285 priorities):**
> - S5-B1214-SHARES-OUTSTANDING (HIGH; 1 strategy; 1d) - remove B1229 fallback when data ships
> - S5-B1216-INSTITUTIONAL-13F (MED after B1230 correction; 1 strategy; 1-2d) - expand T1a persistence file
> - S5-B1212-SECONDARY-NEWS (MED; 6 strategies; 2d) - Finnhub/AlphaVantage fallback
>
> **Comprehensive coverage report:** `output_audit/PRODUCER_COVERAGE_COMPREHENSIVE_REPORT.md`

---

# AUDIT_BACKLOG.md — Master Implementation Backlog (Pass 53 Review-Cycle)

> **STALE BANNER 2026-06-27:** Last meaningful update 2026-05-15 (43 days). Document covers Pass 53 review-cycle which CLOSED per DEC-589. Subsequent Phase 1A-β R4 + Stage 4 walks (B984-B993 ALL WALKS 1-5 RESOLVED) + B978-B1028 R5 launch work tracked in **PATH_TO_PHASE_1B_ALPHA.md §13 + EXECUTION_QUEUE.md + CLAUDE.md banner**, NOT here. INV-046 (only OPEN item, line 42) RESOLVED per Council 78 B978 honest-finding pivot (TIER 2 wireup verified). Recommend archival to `archive/` post-R5 verdict. Active execution: B1028 R5 LAUNCHED 2026-06-27 on AWS i-0940a53c75d049381.

## Pass 53 Day 9+ Batch 178 (2026-05-15 launch day) — 0 strict blockers

Session 2026-05-15 closed Batches 166-178. Highlights:
- Matrix anomalies 19 → 3 (all pre-existing); FUNC-DEAD coupling oscillation fixed (Batch 171 / L151)
- DEFERRED bugs 90 → 76 (Batch 170 SUPERSEDED reclassification)
- API CACHED 84 → 109 (Batches 172-175); inventory truth-up resolved 25-row staleness gap (L154)
- Sprint 6.5 Phase 1A Trade Summary Dashboard delivered early (Batch 177) — live at `https://jeetmehta1991.github.io/stock-picks-app/dashboard_phase_1a/`
- Wikipedia revisions 0 → 99.9% (Batches 174-178; L153 rate-limit lesson)
- Doc-builder perf: 188s → 6.2s (Batch 168 canonical-ID pre-extraction; L152 suffix-aware fix)
- 4 new lessons added: L151-L154

Phase 1A May 15 launch ready. 0 blockers; Day-8 verification ritual items 1-5 ✅.

## Pass 53 Day-9 v8h+1 close (2026-05-08/09) — T0 triage + 13-layer pyramid + 8 new DECs logged

**8 new DECs logged 2026-05-09 (DEC-597 → DEC-604) - retroactive batch closing the
decision-register gap from prior turns where decisions were implemented but not
formally logged in AUDIT_INDEX.md:**

| DEC | Title | Status | First commit |
|---|---|---|---|
| DEC-597 | Test pyramid 9 -> 13 layer amendment | RESOLVED-DECIDED | `c97d31c5b` |
| DEC-598 | Pyramid 4-state cells + per-ID override | RESOLVED-DECIDED | `bc0373e7e` |
| DEC-599 | StockTwits adoption / pytrends DEFERRED | RESOLVED-DECIDED | `74226e118` / `9673eccca` |
| DEC-600 | Polygon Options ep1 active / ep2 on-demand | RESOLVED-DECIDED | `aa4d2a279` |
| DEC-601 | AAII extended sentiment 13-col integration | RESOLVED-DECIDED | `74226e118` |
| DEC-602 | Per-addressal pyramid mandate (CHECKLIST #78) | RESOLVED-DECIDED | `a32060e74` |
| DEC-603 | All-docs sweep mandate (CHECKLIST #79) | RESOLVED-DECIDED | `a32060e74` |
| DEC-604 | 2-hour drift cron + structural detector | RESOLVED-DECIDED | `f1d7bce1e` / `e67659ddf` |

**T0 blocker triage (Pass 53 v8h+1) outcome:**

| Item | Status | Resolution |
|---|---|---|
| BUG-007 | RESOLVED | regression test in `test_regression.py` (`7a175f7c2`) |
| INV-023 | RESOLVED | Quiver Unicode bug fixed; ASCII regression gate active |
| INV-038 | RESOLVED-PARTIAL | Polygon Indices Basic activated 2/13 (CBOE/S&P license-gated remainder) |
| INV-016 | RESOLVED | Finnhub news Master Universe expansion 1941 ticker files |
| INV-027 | RESOLVED | Polygon news insights_json backfilled 1924 tickers / 449 MB |
| INV-046 | OPEN HIGH | engine pnl > 100% (test_g1 single-trade 106.06%) — root cause investigation pending |
| INV-015 / INV-032 | SURFACED | AlphaVantage news premium tier needed (~$50/mo) |
| INV-025 | SURFACED | SEC EDGAR XBRL parser 20-30h infra build |

**5 of 8 T0 RESOLVED, 1 OPEN (INV-046), 2 SURFACED for owner.**

**Net delta vs v5 close:**
- DEC-503 amended (9 -> 13 layers); 4 new test files (`test_property/snapshot/contract/compatibility.py`).
- 2 new prefetch sources committed (StockTwits + Finnhub social_sentiment script-only).
- Polygon Options chain reference cached for full universe.
- AAII sentiment cache schema expanded 5-col -> 13-col.
- Dashboard expanded: Reference tab (5 sections), Automation tab, Next Up auto-ranker, structural drift detector.
- 2 new CHECKLIST HARD RULES (#78 per-addressal pyramid, #79 all-docs sweep).
- 2-hour auto-drift-sweep cron live.

**Phase 1A May 15 launch readiness: 1 OPEN blocker (INV-046).** Pyramid 982 pass / 1 fail (the INV-046 finding itself) / 14 skipped / 5 xfailed.

**Phase 1A + downstream scope clarification 2026-05-10:** DEC-606 EXCLUDES Finnhub financials_reported COMPLETELY from all phases (Phase 1A + 1B + 1C+ + Stage 3 + Stage 4). Superseded by SEC EDGAR XBRL + Polygon financials. CAV-076 logged. CAV-075 confirms 246-ticker SEC-unfileable ceiling is delisting/acquisition (empirical 0/246 in SEC active map).

**Phase 1A scope clarification 2026-05-09:** DEC-605 EXCLUDES Finnhub social_sentiment data from Phase 1A baseline (premium-locked; budget reserved). CAV-074 logged. Apewisdom + StockTwits + Polygon news insights_json cover the retail-attention signal at free tier.

---

## Pass 53 Day-9-evening v5 close (2026-05-07 evening) — final NIL-gap state pre-Phase-1A

| Bucket | Count | Action |
|---|---|---|
| COMPLIANT (artifact path in body + exists) | 30 | None |
| ANNOTATED_COMPLIANT (annotated path + exists) | 82 | None |
| ANNOTATED_NO_DIRECT_TEST (audit-trail justified) | 3 | None |
| KNOWN_COMPLIANT (allowlist) | 13 | None |
| TEST_SIGNAL_REFERENCED_IN_CODE | 4 | None |
| PARTIAL_SPEC_ONLY (proper status; awaiting build) | 79 | Sprint 7+ build queue |
| SUPERSEDED + DEFERRED + INACTIVE + PROPOSED + NO_TRIGGER | 307 | None |
| **🔴 SPEC_WITHOUT_BUILD** | **0** | ✅ |
| **🔴 TEST_SIGNAL_UNVERIFIED** | **0** | ✅ |
| **TOTAL** | **518** | |

**Phase 1A May 15 BLOCKERS: 0** ✅

**Day 9 v8b-v8f Phase-1A blocker closures (this session, 2026-05-07):**
- R3-01 DEC-514 gap-through-stop fill methodology — ✅ FIXED `0b593d1f`/`dbce0da3` (-20.5pp bias quantified)
- R3-02 DEC-515 Level 6 DD-from-peak CB — ✅ WIRED Day-9 v4 + N5
- R3-03 DEC-516 regime-flip exit — ✅ WIRED Day-9 v4
- R1-11 DEC-510 Deflated Sharpe Ratio — ✅ IMPLEMENTED (`deflated_sharpe.py`, DEC-247 lib)
- R2-17 DEC-512 PIT-fundamentals audit — ✅ COMPLETE `6f79a503` (BUG-INSIDER-PIT fixed: ~6d lookahead removed)
- BUG-VIX-PROXY (not in original review) — ✅ FIXED `8d1b3b9a` (FRED VIXCLS prefetch + 4-tier source priority)
- 16 L146/DEC-507 wiring gaps — ✅ closed/documented Wave A-D (`ea1679d9`/`b245484e`/`0891bd28`/`cce55afa`)

**Pyramid: 628 PASS + 11 SKIP + 5 xfail in 69s** (was 165 pre-Day-9; +463 across all closures).

**Day 9 v8g additions (this session, 2026-05-07 evening — owner directive "Implement P0, P1, verification/hygiene, sprint 0A in parallel"):**
- R3-04 DEC-517 R-multiple exits — ✅ IMPLEMENTED `7ceaed29` (3 new EXIT_STRATEGIES methods + 14 tests)
- R3-05 DEC-518 Earnings-blackout — ✅ IMPLEMENTED `686e0036` (4-strategy tolerant list + 7 tests)
- R3-06 DEC-519 Strategy-to-exit mapping — ✅ COMPLETE via existing counterfactual cube (no new code; documented)
- R3-08 DEC-521 Per-class time stops — ✅ IMPLEMENTED `686e0036` (20-category default map + 8 tests)
- R2-02 DEC-513 #1 Realized vol — ✅ IMPLEMENTED `d148fd19`
- R2-04 DEC-513 #4 Correlation matrix — ✅ IMPLEMENTED `23140972`
- R2-05 DEC-513 #5 Overnight/intraday split — ✅ IMPLEMENTED `d148fd19`
- R2-06 DEC-513 #6 Gap classification — ✅ IMPLEMENTED `d148fd19`
- R2-08 DEC-513 #8 52-week distance continuous — ✅ IMPLEMENTED `d148fd19`
- R2-18 DEC-513 #10 signal_age_days — ✅ IMPLEMENTED helper `d148fd19` (caller wiring Sprint 7)
- R1-09 DEC-509 Correlation cluster gate — ✅ IMPLEMENTED `23140972` (verdict-cube wiring Sprint 7)
- PIT-verification audit Batch 7 — ✅ COMPLETE (BUG-DONATIONS-PIT fixed; ETF/topshareholders documented as no-PIT-dimension; 14 tests)
- Hygiene: .gitignore for output_smoke_*/output_dress_rehearsal/ added `7ceaed29`

**Pyramid post-v8g: 702 PASS + 11 SKIP + 5 xfail in 67s** (+74 from Day-9 v8f).

**Remaining Sprint pre-Phase-1A items (not implemented this session — multi-day each):**
- R2-01 DEC-511 Cat 7 (5 modules — cross-sectional ranking, breadth, factor exposures, signal architecture)
- R2-03 DEC-513 #2/#3 betas + factor exposures (need benchmark + FF3 data)
- R2-09 DEC-513 #7 VIX3M + VVIX (need FRED prefetch additions)
- R2-10 Cat 7 §7.2 breadth indicators
- R2-11 DEC-513 #9 FINRA short interest (new data source)
- R3-07 DEC-520 Signal-reversal exit_when() predicate (per-strategy refactor)
- R4-01 DEC-539 regime training/labeling

These are **NOT Phase 1A blockers** — Phase 1A baseline runs without them.

Day 9 buffer L149 spec-without-build remediation count: 13 instances caught + closed
1. cache.py Schema-B blindness
2. cache.py index.json staleness
3. cache.py weekend boundary strict-check
4. engine.py crisis_flag UnboundLocalError
5. WF-1 walk-forward 2-window → 4-fold (DEC-505)
6. DEC-153 regime-stratified split (lib build)
7. DEC-401 Holm-Bonferroni (lib build)
8. DEC-423 bootstrap CI (lib build)
9. DEC-515 Level 6 CB (lib build)
10. DEC-516 regime-flip exit (lib build)
11. DEC-578 7-gate verdict composer (lib build)
12. DEC-515 Level 6 CB engine wiring (N5)
13. DEC-578 verdict cube writer wiring (N6)

All in same-commit per DEC-594. Remediation pattern: lib build + engine wiring + tests + AUDIT_INDEX annotation all atomic.

---

## Pass 53 late-evening 2026-05-06 — DEC-594/595 retroactive audit findings (Day 2-3 remediation)

**Owner directive (verbatim):** *"This is the biggest mistake. I was forced to do multiple runs of audit cycles because of all issues till date. I have already lost 300$ on a failed phase 1B run. WE cant make more mistakes! Test at every stage and be comprehensive in testing"*

**Structural fix codified this turn:** DEC-594 (Test-Artifact Same-Commit HARD RULE) + DEC-595 (Stage/Phase Gate Executable Tests) + CHECKLIST #73 + L149 (spec-without-build meta-pattern).

**Retroactive DEC audit results** (`scripts/audit_decs_for_artifacts.py` ran 2026-05-06; full report `AUDIT_DECS_ARTIFACTS_REPORT.json`):

| Classification | Count | Action required |
|---|---|---|
| COMPLIANT | 19 | None — artifact path in DEC body + exists |
| KNOWN_COMPLIANT | 13 | None — pre-allowlisted |
| TEST_SIGNAL_REFERENCED_IN_CODE | 4 | None — test code references DEC ID |
| SUPERSEDED | 29 | None — absorbed by another DEC |
| DEFERRED | 49 | None — out of stage scope |
| INACTIVE_STATUS (OBSOLETE/BLOCKED_ON/FAIL_RR) | 13 | None — non-active |
| PROPOSED_OR_PENDING | 13 | None — not yet RESOLVED-DECIDED |
| NO_TRIGGER | 202 | None — no test/gate keywords |
| **🔴 SPEC_WITHOUT_BUILD** | **43** | **Day 2-3 remediation: build artifact OR demote to PARTIAL-SPEC-ONLY** |
| **🟡 TEST_SIGNAL_UNVERIFIED** | **132** | **Day 4-5 remediation: code-grep for matching tests; annotate DEC body with path or demote** |
| TOTAL | 517 | — |

**Breakdown of 43 SPEC_WITHOUT_BUILD by criticality:**

- **1 CRITICAL** (RESOLVED-IMPLEMENTED): DEC-477 (T1a canonical) — has tests in `test_unit.py` but DEC body lacks path annotation. Day 2 fix: annotate.
- **4 PHASE-1A relevant**: DEC-014 (Phase 1B passing criteria — superseded by 422+426), DEC-153 (regime-stratified splits — methodology DEC), DEC-423 (bootstrap CI per-cell), DEC-497 (Sprint 0A — has data-integrity test via DEC-591). Day 2-3 triage.
- **38 OTHER RESOLVED-DECIDED**: methodology DECs spanning various scopes. Day 3 triage.

**Day 2-3 remediation protocol** (Day 2 = May 7; Day 3 = May 8):

For each of 43 SPEC_WITHOUT_BUILD findings:

1. Re-read DEC body in detail
2. Search code (`backtest/tests/`, `scripts/`, `backtest/`) for related logic
3. Decision tree:
   - (a) Test EXISTS → annotate DEC body with path; mark COMPLIANT in next audit run
   - (b) Test PARTIALLY exists → build remaining; same-commit per DEC-594
   - (c) Test does NOT exist + DEC mandates one → build; same-commit
   - (d) Test does NOT exist + DEC is process/data-only → no artifact required (but DEC body should explicitly say so)
4. Update DEC status if needed (RESOLVED-DECIDED → PARTIAL-SPEC-ONLY → RESOLVED-DECIDED again post-build)

**Day 4-5 remediation protocol** (132 TEST_SIGNAL_UNVERIFIED):

Each has a "Test signal:" pattern in DEC body but no explicit code reference. Approach:

1. Extract test_signal description from DEC body (regex `Test signal[s]?:\s*(.+?)(?:\.|;|$)`)
2. Code-grep `backtest/tests/test_unit.py` + `test_integration.py` for matching pattern
3. If found: annotate DEC body with file path + line range
4. If not found: demote to PARTIAL-SPEC-ONLY; queue test build

**Audit script + report committed same-commit as DEC-594/595** (DEC-594 self-compliance demonstration).

**Cross-references:**
- DEC-594 (parent rule — Test-Artifact Same-Commit HARD RULE)
- DEC-595 (parent rule — Stage/Phase Gate Executable Tests)
- CHECKLIST #73 (HARD RULE codification)
- L148 (test pyramid layered failure mode)
- L149 (spec-without-build meta-pattern)
- `scripts/audit_decs_for_artifacts.py` (this audit script)
- `AUDIT_DECS_ARTIFACTS_REPORT.json` (full machine-readable report)
- `backtest/tests/test_gates.py` (6 phase gates, gate 1 PASS today)

**Status:** 175 DECs queued for Day 2-3 (43 SPEC_WITHOUT_BUILD) + Day 4-5 (132 TEST_SIGNAL_UNVERIFIED) remediation. Tracking continues until 100% before May 15 Phase 1A start. If remediation count exceeds 9-day window capacity, owner reviews + reapproves Phase 1A start date per DEC-590 ±2-business-day slippage tolerance.

---



**Created:** 2026-05-06 (Pass 53 final review-cycle turn)
**Authority:** Per owner directive 2026-05-06 — *"No more audit cycles. But everything flagged till now will need to be addressed."* This file is the **single source of truth** for what's been flagged across the 7-review Pass 53 cycle, what's resolved, and what remains.
**Closed:** Per **DEC-589 audit-iteration ceiling**, the Pass 53 review-cycle is CLOSED. Future external-AI feedback goes to a separate `AUDIT_BACKLOG_FUTURE.md` for post-Phase-1A-run consideration only.
**Implementation begin:** **2026-05-15** (per **DEC-590** owner-approved 2026-05-06; Q3 = A, 9 days from today).

---

## Aggregate metrics

| Metric | Value |
|---|---|
| Total review-takes Pass 53 | **7** |
| Total findings flagged | **~155** |
| Total DECs codified | **~80 new in Pass 53** (DEC-509 through DEC-590) |
| Total code commits | **~12 commits** (DEC drafting; Pass 53 prefetch backfill; Layer 5/6 spec; etc.) |
| Total inline TRADING_RULES bug fixes | **10** (Pass 53 turn ~6) |
| Total Sprint pre-Phase-1A scope | **~49-70 days** |
| **Findings resolved (DEC drafted or inline fixed)** | **~140** |
| **Findings deferred to backlog (P2-P4)** | **~15** |
| **Findings deferred to AUDIT_BACKLOG_FUTURE.md (post-Phase-1A)** | **future-cycle only** |

---

## Status legend

| Marker | Meaning |
|---|---|
| ✅ **RESOLVED-INLINE** | Bug fixed via direct text edit in spec docs (no DEC; mechanical correction) |
| 🟢 **RESOLVED-DECIDED + IMPLEMENTATION-PENDING** | DEC drafted; spec frozen; implementation queued for Sprint pre-Phase-1A or 7 |
| 🟡 **RESOLVED-DECIDED + BACKLOG** | DEC drafted at backlog level; implementation post-Phase-1B-α |
| 🔴 **PROPOSED** | Pre-DEC; awaiting owner approval (legacy items only — Pass 53 review cycle CLOSED per DEC-589) |
| 🔵 **DEFERRED** | Acknowledged but not actionable in Stage 2 (subscription gates, intraday data, paid feeds) |
| ⚠ **DOC-DRIFT-PENDING** | Known doc-drift; will be resolved by DEC-588 reconciliation pass |

---

## Source reviews + commits

| # | Review focus | Commit(s) | Findings | DECs codified |
|---|---|---|---|---|
| 1 | Strategy roster (Layer 5/6 + symmetry + methodology) | `1ac6f1d4`, `bc98e3f2` | ~30 | DEC-509/510 + Layer 1.I 38 + Layer 5 flag + Layer 6 27 |
| 2 | Signal universe (Cat 7 + PIT audit + P1 signals) | `3d0ef631` | ~20 | DEC-511/512/513 |
| 3 | Exit / risk / fill methodology | `2218ec0d` | ~30 | DEC-514-538 (14 active + 11 backlog) |
| 4 | Regime classification + smart money | `1f27cbe1` | ~30 | DEC-539-565 (10 P0+P1 + 17 backlog) |
| 5 | Adversarial TRADING_RULES (P0+P1+DEC-588) | `240215f8` | ~25 | DEC-559 promoted + 566/569/582-588 + 567/568/570-580 |
| 6 | Adversarial Q4 (endogeneity-loop) | `8002dc9c` | 1 | DEC-581 |
| 7 | Project plan adversarial (this turn — backlog only) | `<this turn>` | ~17 | DEC-589 + DEC-590 + 10 P0 inline fixes; rest deferred |

---

## Review 1 — Strategy roster (commits `1ac6f1d4` + `bc98e3f2`)

| ID | Severity | Title | DEC / Resolution | Status | Sprint |
|---|---|---|---|---|---|
| R1-01 | P0 | Cross-sectional ranking strategies missing | Layer 6A 8 strategies (172-179) | 🟢 | Sprint 7 + DEC-511 prerequisite |
| R1-02 | P0 | Volatility-regime strategies | Layer 6B 3 strategies (180-182) | 🟢 | Sprint 7 |
| R1-03 | P0 | Overnight/gap drift strategies | Layer 6C 5 strategies (183-187; ORB excluded as intraday) | 🟢 | Sprint 7 (DEC-513 prerequisite) |
| R1-04 | P0 | Insider/institutional flow | Layer 6D 1 (188); 4 dups; 2 Ortex-deferred | 🟢 / 🔵 | Sprint 7 / DEC-506 |
| R1-05 | P0 | Breadth/market-internals | Layer 6E 4 strategies (189-192) | 🟢 | Sprint 7 (DEC-511 Cat 7 prerequisite) |
| R1-06 | P0 | Post-event drift beyond earnings | Layer 6F 2 strategies (193-194); 5 dups of Layer 1 Event-Driven | 🟢 | Sprint 7 |
| R1-07 | P0 | Microstructure swing setups | Layer 6G 4 strategies (195-198); 1 deferred (intraday VP) | 🟢 / 🔵 | Sprint 7 |
| R1-08 | P0 | Direction asymmetry Layer 1 | Layer 1.I 38 new shorts (134-171) — buy-the-dip + sell-the-rip philosophy | ✅ | Sprint 7 |
| R1-09 | P0 | Strategy correlation will inflate apparent diversity | DEC-509 correlation cluster gate | ✅ | IMPLEMENTED Day-9 v8g (`23140972`) — `backtest/engine/correlation_cluster.py`: compute_correlation_matrix + cluster_strategies + flag_redundant_variants. 15 tests. Verdict-cube integration deferred to Sprint 7. |
| R1-10 | P0 | No regime conditioning | Layer 5 regime-eligibility flag schema (172 strategies tagged) | 🟢 | Sprint 7 |
| R1-11 | P0 | Multiple-testing problem | DEC-510 Deflated Sharpe Ratio (F-009 6th gate) | ✅ | IMPLEMENTED — `backtest/results/deflated_sharpe.py` (DEC-247 PSR + DSR with Bailey-LdP 2014 formula; 22 tests in `test_partial_spec_artifacts_v2.py`) |
| R1-12 | P1 | Cost modeling underspecified | DEC-095/092/122/280 already exist; reviewer missed | ✅ | Already in code |
| R1-13 | P2 | Layer 2D form-derived ICT hole | PENDING-FORM owner-driven enumeration | 🔴 | Owner-gated |

---

## Review 2 — Signal universe (commit `3d0ef631`)

| ID | Severity | Title | DEC / Resolution | Status | Sprint |
|---|---|---|---|---|---|
| R2-01 | P0 | Cross-sectional ranks missing | DEC-511 Category 7 (5 modules) | 🟢 | Sprint pre-Phase-1A |
| R2-02 | P0 | Realized vol as first-class signal | DEC-513 #1 (3 horizons) | ✅ | IMPLEMENTED Day-9 v8g (`d148fd19`) — `dec513_extended_signals.compute_realized_vol` (10d/20d/60d annualized). 4 tests. |
| R2-03 | P0 | Beta + factor exposures | DEC-513 #2 + #3 + Cat 7 §7.4 | 🟢 | Sprint pre-Phase-1A |
| R2-04 | P0 | Correlation matrices | DEC-513 #4 + Cat 7 §7.3 | ✅ | IMPLEMENTED Day-9 v8g (`23140972`) — `correlation_cluster.compute_correlation_matrix` (N×N pairwise Pearson). 5 tests. |
| R2-05 | P0 | Overnight/intraday split | DEC-513 #5 | ✅ | IMPLEMENTED Day-9 v8g (`d148fd19`) — `dec513_extended_signals.compute_overnight_intraday_split`. 2 tests. |
| R2-06 | P0 | Gap classification | DEC-513 #6 | ✅ | IMPLEMENTED Day-9 v8g (`d148fd19`) — `compute_gaps` (size/bucket/fill T+1/T+3/T+5). 4 tests. |
| R2-07 | P2 | Volume profile / POC / HVN | Deferred (intraday VP needed); DEC-526 P2 backlog uses daily approx | 🟡 | Post-Phase-1B-α |
| R2-08 | P0 | 52-week distance continuous | DEC-513 #8 | ✅ | IMPLEMENTED Day-9 v8g (`d148fd19`) — `compute_extremes` (8 fields: 52w/20d/252d distance pct + ATR-norm). 5 tests. |
| R2-09 | P0 | VIX term structure (VIX3M, VVIX) | DEC-513 #7 | 🟢 | Sprint pre-Phase-1A |
| R2-10 | P0 | Breadth indicators incomplete | Cat 7 §7.2 (DEC-511) | 🟢 | Sprint pre-Phase-1A |
| R2-11 | P0 | Short interest data absent | DEC-513 #9 (FINRA free) | 🟢 | Sprint pre-Phase-1A |
| R2-12 | P1 | SEC Form 4 detail (raw codes) | Sprint 4 SEC EDGAR parser (already cached Pass 53 Batch 11) | 🟢 | Sprint 4 |
| R2-13 | P1 | 13F whale-following per-manager pattern | DEC-526 P2 backlog | 🟡 | Post-Phase-1B-α |
| R2-14 | P1 | Analyst price-target revision continuous | DEC-552 backlog | 🟡 | Phase 1B-α tunable |
| R2-15 | P3 | Macro surprise data (Citi ESI) | Paid; deferred | 🔵 | Stage 3+ |
| R2-16 | P3 | FX cross-rates beyond DXY | Lower priority | 🔵 | Stage 3+ |
| R2-17 | P0 | PIT-fundamentals filing-date audit | DEC-512 (pre-Phase-1A blocker) | ✅ | COMPLETE Day-9 v8f (`6f79a503`) — 7-item audit run, 6/7 PASS as-is, item 6 BUG-INSIDER-PIT fixed (Quiver insider Date→fileDate, ~6d lookahead removed). 9 regression tests. |
| R2-18 | P1 | Universal `signal_age_days` field | DEC-513 #10 | ✅ | IMPLEMENTED Day-9 v8g (`d148fd19`) — `dec513_extended_signals.attach_signal_age` helper. Caller integration into 7 categories: Sprint 7 schema migration. |
| R2-19 | P1 | 90-day decay sensitivity | DEC-123 REVISIT_AFTER_BACKTEST (Class B per DEC-581) | 🟡 | Phase 1B-α tuning |
| R2-20 | P1 | Sentiment thresholds untuned | DEC-072 + DEC-581 Class B | 🟡 | Phase 1B-α tuning |
| R2-21 | P2 | Per-ticker vs universe-level architectural split | DEC-511 Cat 7 (architectural addition) | 🟢 | Sprint pre-Phase-1A |
| R2-22 | P3 | Aggregator visibility / registry pattern | Refactor pre-Phase-1B-α | 🟡 | Implementation concern |
| R2-23 | P3 | Output schema standardization | DEC-511 §7 contract (recommended for Cat 1-6 too) | 🟡 | Incremental |
| R2-24 | P2 | Caching invalidation versioning | DEC-512 audit covers Polygon revisions; ALFRED gives PIT FRED | 🟡 | DEC-512 implementation |

---

## Review 3 — Exit / risk / fill (commit `2218ec0d`)

| ID | Severity | Title | DEC | Status | Sprint |
|---|---|---|---|---|---|
| R3-01 | P0 | Gap-through-stop fill methodology missing | DEC-514 (silent backtest bug; Phase 1A blocker) | ✅ | FIXED Day-9 v8e (`0b593d1f` + `dbce0da3`) — `compute_fill_price()` helper + 12 sites refactored + 22 regression tests. H3 quantified -20.5pp pre-fix bias on 25-tkr × 1y sample. |
| R3-02 | P0 | DD-from-peak portfolio breaker missing | DEC-515 (Level 6) | ✅ | WIRED Day-9 v4 + N5 — `backtest/engine/circuit_breakers.py` Level6State + update_level_6_state + halt branch in `process_day_exits`. 4 tests in test_n5_n6_wiring.py + 5 in test_n1_n2_artifacts.py. |
| R3-03 | P0 | Regime-flip exit (symmetric to Layer 5) | DEC-516 | ✅ | WIRED Day-9 v4 — `exit_regime_flip` in EXIT_STRATEGIES registry. 3 regression tests in test_n1_n2_artifacts.py. |
| R3-04 | P1 | R-multiple exits missing | DEC-517 (3 new exit methods #18-20) | ✅ | IMPLEMENTED Day-9 v8g (`7ceaed29`) — 3 new exits in EXIT_STRATEGIES: r_multiple_2r/3r/break_even_at_1r. 14 regression tests. |
| R3-05 | P1 | Earnings-blackout exit | DEC-518 | ✅ | IMPLEMENTED Day-9 v8g (`686e0036`) — exit_earnings_blackout + 4-strategy tolerant list (DEC-013). 7 tests. |
| R3-06 | P1 | Strategy-to-exit mapping (compete vs single) | DEC-519 (multiple compete; first-trigger wins) | ✅ | IMPLEMENTED via counterfactual cube (run_exit_comparison) — every trade tested against all exits; first-trigger wins behavior natively supported. |
| R3-07 | P1 | Signal-reversal exit precise definition | DEC-520 (exit_when() predicate) | 🟢 | DEFERRED — requires per-strategy refactor across 60+ classes. Sprint 7. |
| R3-08 | P1 | Per-strategy-class time stops | DEC-521 | ✅ | IMPLEMENTED Day-9 v8g (`686e0036`) — exit_class_time_stop + CATEGORY_TIME_STOPS_DAYS (20 categories). 8 tests. |
| R3-09 | P2 | Trailing-stop ATR floor (vol-collapse trap) | DEC-522 | 🟡 | P2 backlog |
| R3-10 | P2 | Scale-out beyond 50/50 | DEC-523 | 🟡 | P2 backlog |
| R3-11 | P2 | News / 8-K-driven exit | DEC-524 (post-Sprint 4 SEC EDGAR parser) | 🟡 | Sprint 4+ |
| R3-12 | P2 | Sector/market exit overlay (SPY < 50-SMA kill) | DEC-525 | 🟡 | P2 backlog |
| R3-13 | P2 | Pattern-target exit Layer 3A | DEC-526 (measured-move + Fib) | 🟡 | P2 backlog |
| R3-14 | P2 | MAE/MFE empirical exit calibration | DEC-527 (cross-validated percentiles 75th not 90th per DEC-579) | 🟡 | Phase 1B-α |
| R3-15 | P3 | Volatility-target position exit | DEC-528 | 🔴 | P3 backlog |
| R3-16 | P3 | Correlation-spike portfolio breaker Level 8 | DEC-529 (depends on DEC-511 §7.3) | 🔴 | P3 backlog |
| R3-17 | P3 | Profit-protect ratchet stops | DEC-530 | 🔴 | P3 backlog |
| R3-18 | P3 | DD-from-peak per-trade exit | DEC-531 | 🔴 | P3 backlog |
| R3-19 | P3 | Time-stop + profit conditional | DEC-532 | 🔴 | P3 backlog |
| R3-20 | P3 | Adverse-selection slippage on stops | DEC-533 | 🔴 | P3 backlog |
| R3-21 | P3 | Long/short asymmetry (borrow recall + dividend liability + forced buy-in) | DEC-534 | 🔴 | P3 backlog |
| R3-22 | P3 | Exit-as-function-of-signal-quality | DEC-535 | 🔴 | P3 backlog |
| R3-23 | P4 | Underspecification fixes (vol-breakout dir / volume-spike dir / multi-TF / time-decay / chandelier 22d / SuperTrend dual-use) | DEC-536 single doc cleanup | 🟡 | Cleanup |
| R3-24 | P4 | Hybrid 50% scale-out tunable | DEC-537 | 🔴 | Phase 1B-α tunable |
| R3-25 | P4 | Liquidity-conditional slippage refinement | DEC-538 | 🔴 | Stage 3+ |

---

## Review 4 — Regime classification + smart money (commit `1f27cbe1`)

| ID | Severity | Title | DEC | Status | Sprint |
|---|---|---|---|---|---|
| R4-01 | P0 | Regime training/labeling mechanism | DEC-539 (hand-labeled + cross-validation) | 🟢 | Sprint pre-Phase-1A |
| R4-02 | P0 | Regime probability consumption pattern | DEC-540 (Schmitt binarization) | 🟢 | Sprint pre-Phase-1A |
| R4-03 | P0 | Regime classifier validation methodology | DEC-541 (baseline vs SPY-200SMA) | 🟢 | Sprint pre-Phase-1A |
| R4-04 | P0 | Collapse 6 → 4 regime classes | DEC-542 (matches F-006) | 🟢 | Sprint pre-Phase-1A |
| R4-05 | P0 | Stage 2 vs Stage 3+ regime-input parity | DEC-543 (freeze inputs) | 🟢 | Sprint pre-Phase-1A |
| R4-06 | P1 | Asymmetric EMA smoothing | DEC-544 (fast-in 5d / slow-out 20d) | 🟢 | Sprint pre-Phase-1A |
| R4-07 | P1 | EMA + transition-matrix integration | DEC-545 (Bayesian) | 🟢 | Sprint pre-Phase-1A |
| R4-08 | P1 | Schmitt-trigger + min-duration | DEC-546 | 🟢 | Sprint pre-Phase-1A |
| R4-09 | P1 | Smart money veto symmetry | DEC-547 (symmetric +5/-5) | 🟢 | Sprint pre-Phase-1A |
| R4-10 | P1 | Sector regime distinct from market | DEC-548 (two-level hierarchy) | 🟢 | Sprint pre-Phase-1A |
| R4-11 | P2 | Cluster_buy/sell threshold symmetry | DEC-549 | 🟡 | P2 backlog |
| R4-12 | P2 | Smart money signal normalization (gov/lobbying/news) | DEC-550 | 🟡 | P2 backlog |
| R4-13 | P2 | Regime × smart money interaction | DEC-551 | 🟡 | P2 backlog |
| R4-14 | P2 | Regime-conditional smart money weighting | DEC-552 | 🟡 | Phase 1B-α tunable |
| R4-15 | P3 | Equity-bond correlation as regime input | DEC-553 | 🔴 | P3 backlog |
| R4-16 | P3 | Sector dispersion direction | DEC-554 | 🔴 | P3 backlog |
| R4-17 | P3 | CFTC COT promotion to regime input | DEC-555 | 🔴 | P3 backlog |
| R4-18 | P3 | Smart money tunability extension to structure | DEC-556 | 🔴 | Post-Phase-1B-α |
| R4-19 | P3 | "Decreased > increased" stability fix | DEC-557 | 🔴 | P3 backlog |
| R4-20 | P3 | "new_pos ≥ 3" universe-normalization | DEC-558 | 🔴 | P3 backlog |
| R4-21 | P0 | VIX SMA 5d vs 21d threshold reconciliation | DEC-559 (PROMOTED P3→P0; standardize 5d) | ✅ | Sprint pre-Phase-1A |
| R4-22 | P3 | Score tier boundaries documented in source-mix | DEC-560 | 🔴 | Cleanup |
| R4-23 | P4 | ICE BofA HY OAS preferred over BAA10Y | DEC-561 | 🔴 | P4 backlog |
| R4-24 | P4 | TED/SOFR-OIS dollar-funding stress | DEC-562 | 🔴 | P4 backlog |
| R4-25 | P4 | Senate-vs-House priority documentation | DEC-563 | 🔴 | Cleanup |
| R4-26 | P4 | NAAIM exposure index | DEC-564 | 🔴 | P4 backlog |
| R4-27 | P4 | Commodity term structure | DEC-565 | 🔴 | P4 backlog |

---

## Review 5 — Adversarial TRADING_RULES (commit `240215f8`)

| ID | Severity | Title | DEC | Status | Sprint |
|---|---|---|---|---|---|
| R5-01 | P0 | Bonferroni × t-stat double-counting | DEC-582 | ✅ | Inline-fixed §3.2 |
| R5-02 | P0 | Walk-forward 2018-2021 OHLCV source | DEC-583 (truncate to 2021-05+) | ✅ | Inline-fixed §16.2 |
| R5-03 | P0 | §6.2 max-loss cap math wrong | DEC-584 | ✅ | Inline-fixed §6.2 |
| R5-04 | P0 | Strategy/exit count drift (119→199, 17→20) | DEC-585 | ✅ | Inline replace |
| R5-05 | P0 | §9.6 vs §9.2 circuit breaker priority | DEC-586 | ✅ | Inline-fixed §9.6 |
| R5-06 | P0 | §11.1 vs Layer 5 regime-block contradiction | DEC-587 | ✅ | Inline-fixed §11.1 |
| R5-07 | P0 | "What happens on failure" branches missing | DEC-566 | 🟢 | Sprint pre-Phase-1A (per-gate table) |
| R5-08 | P0 | Cube primary vs drilldown dimensions | DEC-569 | 🟢 | Sprint pre-Phase-1A |
| R5-09 | P0 | TRADING_RULES doc-reconciliation pass | DEC-588 (~3-5 days; propagates DEC-509-565 across §s) | 🟢 | Sprint pre-Phase-1A |
| R5-10 | P1 | PM confidence calibration check | DEC-567 (Brier-score) | 🟡 | Phase 1B production gate |
| R5-11 | P1 | Walk-forward fold aggregation methodology | DEC-568 (pooled-trade Sharpe) | 🟡 | Sprint pre-Phase-1A |
| R5-12 | P1 | Event calendar extension | DEC-570 | 🟡 | Sprint pre-Phase-1A |
| R5-13 | P1 | Corporate-action exit handling | DEC-571 | 🟡 | Sprint 4+ |
| R5-14 | P1 | Cache freshness-policy table | DEC-572 | 🟡 | Sprint pre-Phase-1A |
| R5-15 | P1 | Slippage floor + half-spread modeling | DEC-573 | 🟡 | Sprint pre-Phase-1A |
| R5-16 | P1 | Borrow rate model | DEC-574 | 🟡 | Sprint pre-Phase-1A |
| R5-17 | P1 | Performance metrics correctness (DTB3 / Sortino MAR / L-moments) | DEC-575 | 🟡 | Sprint pre-Phase-1A |
| R5-18 | P1 | Promote DEC-512 to hard checklist gate | DEC-576 | 🟡 | Sprint pre-Phase-1A |
| R5-19 | P1 | Unify gate_score vs PM confidence | DEC-577 | 🟡 | Cleanup |
| R5-20 | P1 | F-009 7th gate effect-size floor (5bps) | DEC-578 | 🟢 | Sprint pre-Phase-1A |
| R5-21 | P1 | MAE/MFE cross-validated percentiles | DEC-579 | 🟡 | Phase 1B-α |
| R5-22 | P1 | Vol-targeting vs tier-sizing precedence | DEC-580 | 🟡 | Sprint pre-Phase-1A |

---

## Review 6 — Adversarial Q4 (commit `8002dc9c`)

| ID | Severity | Title | DEC | Status | Sprint |
|---|---|---|---|---|---|
| R6-01 | P0 | Tuning methodology + endogeneity-loop protection | DEC-581 (5-component: Class A/B + hold-out folds + tuning Bonferroni + joint/marginal + audit trail + cycle prevention) | 🟢 | Sprint pre-Phase-1A |

---

## Review 7 — Project plan adversarial (this turn — backlog only per DEC-589)

**This turn: 10 P0 items applied as inline fixes; all other findings deferred per DEC-589 audit ceiling.**

### P0 inline fixes applied this turn

| ID | Severity | Title | Resolution | Status |
|---|---|---|---|---|
| R7-01 | P0 | Cube cell count math 254K vs 848K (3.3× error) | Recalculate; reconcile with sample-size requirements | ✅ INLINE this turn |
| R7-02 | P0 | Strategy count 108-118 vs 199 vs 109-119 across 3 docs | Global replace → 199 (per DEC-585) | ✅ INLINE this turn |
| R7-03 | P0 | Codespace → local VS Code (6+ stale refs) | Global replace | ✅ INLINE this turn |
| R7-04 | P0 | Budget contradictions $75 vs $225 vs $300 | Reconcile to $300 cap (per F-001 11-agent × 0.0035 USD × 1.35 CAD × candidate-days) | ✅ INLINE this turn |
| R7-05 | P0 | Effort math sums 344-431 vs published 310-385 | Recompute; update §1.3 to match itemized sum | ✅ INLINE this turn |
| R7-06 | P0 | Phase 1B-α run time 37-40h (DEC-109) vs 20-32h (DEC-505) | Update §9.7 to DEC-505 4-fold timing | ✅ INLINE this turn |
| R7-07 | P0 | Tier 1 universe count 509 vs 1015 within same doc | Reconcile §2.3 vs §7.5.1 (use F-005 1,937 master) | ✅ INLINE this turn |
| R7-08 | P0 | Test count "36/36" obsolete (~370+ tests now) | Replace with "all tests pass per F-007" | ✅ INLINE this turn |
| R7-09 | P0 | Cube definition 8 vs 17 dims — DEC-471 PROPOSED, DEC-569 RESOLVED | Reconcile via DEC-569 (5 primary + 12 drilldown) | ✅ INLINE this turn |
| R7-10 | P0 | Circuit breaker Level 5 missing from Sprint 2 §5.1 bug list | Add Level 5 + DEC-515 Level 6 to Sprint 2 scope | ✅ INLINE this turn |

### P1+ deferred to AUDIT_BACKLOG_FUTURE.md (per DEC-589 ceiling)

These ~17 findings from Review 7 are flagged but NOT codified as new DECs (audit ceiling). They go to `AUDIT_BACKLOG_FUTURE.md` for post-Phase-1A-run consideration:

| ID | Severity | Title | Disposition |
|---|---|---|---|
| R7-P1-01 | P1 | CI-based Sharpe gates (vs point estimates) | Deferred to backlog file |
| R7-P1-02 | P1 | PASS cell count quantitative floor (e.g., > 100 cells) | Deferred |
| R7-P1-03 | P1 | Stage 3 "divergence < 20%" precise definition | Deferred |
| R7-P1-04 | P1 | Stage 4-5 "stable for ≥ 6 months" quantitative threshold | Deferred |
| R7-P1-05 | P1 | Haiku → Sonnet model-switch validation methodology | Deferred |
| R7-P1-06 | P1 | Effort buffer (~30% contingency) | Owner-side calendar planning, not spec |
| R7-P1-07 | P1 | Run-halt-mid-fold contradiction (R-3 vs §9.4) | Implementation concern; surfaces in Sprint 7 |
| R7-P1-08 | P1 | `snapshot_at` performance bottleneck | Implementation concern; Sprint 3 |
| R7-P1-09 | P1 | Mean-correlation API design (should be max not mean) | Implementation concern; Sprint 3 |
| R7-P1-10 | P1 | Cost reconciliation: $300 budget vs actual Pattern 2 propagate cost (likely 3-10×) | Pre-Phase-1B-α validation: 10-call cost test |
| R7-S1-01 | Strategic | CC-1 Documentation governance (6,103 lines + 13 docs growing linearly) | Deferred — accept as ongoing maintenance burden |
| R7-S1-02 | Strategic | CC-3 Decision-to-code ratio ∞:0 | DEC-590 implementation begin date addresses |
| R7-S1-03 | Strategic | CC-4 Owner SPOF (succession plan) | Deferred to Stage 4+ |
| R7-S1-04 | Strategic | CC-5 No "cost of not shipping" tracking | Deferred |
| R7-S1-05 | Strategic | CC-6 Audit cycle not converging | DEC-589 audit ceiling addresses |
| R7-S1-06 | Strategic | CC-7 Optimistic effort estimates (2-3× off) | Owner calendar planning; +30% buffer recommended |
| R7-S1-07 | Strategic | CC-2 Pass-based versioning (calendar dates sparse) | Cleanup pass (low priority) |

---

## Implementation roadmap (Sprint pre-Phase-1A, ordered)

Per DEC-590 implementation begin **2026-05-15** (9 days from today). Cumulative scope: **~49-70 engineering days**.

### Week 1 (2026-05-15 → 2026-05-21) — Pre-Phase-1A foundation

1. **DEC-588 doc-reconciliation pass (Day 1-3)** — Propagate DEC-509-565 across TRADING_RULES §s; cleanup doc-drift; ~3 days
2. **DEC-512 PIT-fundamentals filing-date audit (Day 4-5)** — 7-item audit checklist; targeted fixes; ~2 days
3. **DEC-514 backtest fill methodology (Day 5)** — Implement gap-through-stop + intraday EOD fill rules; ~0.5-1 day
4. **DEC-515 Level 6 DD-from-peak portfolio breaker (Day 6)** — `backtest/engine/circuit_breakers.py`; ~0.5 day

### Week 2 (2026-05-22 → 2026-05-28) — Signal layer foundation

5. **DEC-511 Category 7 universe-level signals (Days 7-13)** — 5 NEW source files; ~5-7 days
6. **DEC-513 P1 signal additions (parallel; Days 7-15)** — Realized vol + beta + factor + correlation + overnight/gap + 52w-distance + VIX3M + FINRA + signal_age_days; ~12-18 days (overlaps with Cat 7)

### Week 3-4 (2026-05-29 → 2026-06-11) — Regime + agent toolkit

7. **DEC-539-543 regime P0 (Days 14-20)** — Hand-label + classifier validation + 6→4 collapse + Stage 2/3 parity; ~5-7 days
8. **DEC-544-548 regime P1 (Days 18-21)** — Asymmetric EMA + Bayesian + Schmitt + sector regime; ~3-4 days
9. **DEC-509 correlation cluster (Days 22-23)** — Phase 1A-α gate; ~1-2 days
10. **DEC-510 / DEC-578 Deflated Sharpe + 7th gate (Days 23-24)** — F-009 6→7-gate; ~1 day
11. **DEC-581 endogeneity protection (Days 25-27)** — Tuning methodology infrastructure; ~2-3 days

### Week 5+ (2026-06-12 onward) — Sprint 7 (TradingAgents + custom toolkits)

12. **DEC-462-468 + DEC-516 (Sprint 7 scope; ~96-108d)** — `OurTechnicalToolkit` + `OurFundamentalsToolkit` + `OurNewsToolkit` + `OurTraderToolkit` + `OurRiskToolkit` + `OurAgentState` + Ortex wiring + regime-flip exit
13. Layer 1.I 38 shorts + Layer 5 flag schema + Layer 6 27 strategies in code
14. R-PHA-001 to R-PHA-005 mitigations (FVG +3-bar lag, swing_length lag for retracements, 2*swing_length safe window for BOS/CHOCH)

### Phase 1A acceptance gate

Phase 1A run blocked until ALL Sprint pre-Phase-1A 🟢 items are RESOLVED-DECIDED + IMPLEMENTED:
- DEC-512 audit closed
- DEC-514 fill methodology coded + tested
- DEC-515 Level 6 implemented
- DEC-509 correlation cluster runnable
- DEC-510 + DEC-578 7-gate operational
- DEC-511 Category 7 + DEC-513 P1 signals computed
- DEC-539 regime labels in place
- DEC-588 doc-reconciliation complete

### Phase 1B-α tuning batch (post-Phase-1A run)

Per DEC-581 endogeneity protection: 10 grouped tuning experiments consuming 1 hold-out fold. Class B parameters (~14 of 34 REVISIT items) tuned single-shot.

### Backlog (P2-P4) — defer to post-Phase-1B-α

P2 backlog DECs: DEC-522/523/524/525/526/527/549/550/551/552 — implement based on Phase 1B-α verdict findings.
P3-P4 backlog: DEC-528-538/553-565 — lower priority; Stage 3+ or skip.

---

## DEC-589 — Audit-iteration ceiling (Pass 53 owner-approved 2026-05-06)

**Rule:** Pass 53 review-cycle is **CLOSED**. The 7th external-AI review (project plan adversarial) is the LAST review whose findings are codified into Pass 53 DECs. Future external-AI feedback proceeds as follows:

1. **All future review findings → `AUDIT_BACKLOG_FUTURE.md`** (separate file; no auto-codification)
2. **Review-take findings reviewed only post-Phase-1A-run** (after we have empirical data on what actually matters)
3. **Decision criterion:** if a Phase 1A-α run finding aligns with a backlog item, promote to DEC + immediate fix; otherwise stay in backlog
4. **Audit-iteration cap:** 7 reviews this Pass. Future Passes (54+) capped at 3 reviews unless Phase 1A-α results demand more

**Rationale:** Per CC-6 critique (Review 7) — the audit cycle was not converging. Each review found new gaps that were generated by prior review approvals. After 7 cycles + ~80 DECs codified + 0 application code shipped, **marginal utility of additional review approaches zero**. Implementation needs to start with imperfect spec; iteration happens via empirical Phase 1A-α data, not speculative review.

**Source:** DEC-589

---

## DEC-590 — Implementation begin date 2026-05-15 (Pass 53 owner-approved 2026-05-06)

**Rule:** Implementation of the cumulative ~80-DEC Pass 53 spec begins **2026-05-15** (9 calendar days from today, 2026-05-06).

**Rationale:** Per CC-3 critique (Review 7) — decision-to-code ratio is ∞:0. 12+ months of planning preceded any implementation. The audit-iteration ceiling (DEC-589) closes the spec phase. DEC-590 sets a hard deadline for breaking the planning-paralysis cycle.

**Phasing:**
- 2026-05-06 → 2026-05-14: 9-day buffer for owner final review of Pass 53 cumulative state
- **2026-05-15: implementation begins** with Sprint pre-Phase-1A roadmap above
- ~49-70 days engineering = ~10-14 calendar weeks at full-time = **target Phase 1A-α run by ~Aug-Sep 2026**

**Owner can override DEC-590 via explicit DEC-591 if critical pre-implementation issue surfaces.** Otherwise the date holds.

**Source:** DEC-590

---

## Pass 53 review-cycle FINAL summary

| Component | Count |
|---|---|
| External-AI review takes | **7** |
| Total findings flagged | **~155** |
| DECs codified Pass 53 (DEC-509 → DEC-590) | **~82** |
| P0 findings (must fix pre-Phase-1A) | **~50** — all RESOLVED |
| P1 findings (Sprint pre-Phase-1A or Sprint 7) | **~40** — all RESOLVED |
| P2-P4 backlog (post-Phase-1B-α) | **~50** |
| Strategic risks (CC-1 to CC-7 from Review 7) | **7** — addressed via DEC-589/590 + accepted as ongoing |
| Inline TRADING_RULES bug fixes | **15** (5 from Review 5 + 10 from Review 7) |
| Code commits Pass 53 | **~14** (DEC drafting + spec; Pass 53 prefetch backfill; Layer 5/6/1.I; alignment tests) |
| **Aggregate Sprint pre-Phase-1A scope** | **~49-70 engineering days** |
| **Implementation begin** | **2026-05-15** |

**Pass 53 review-cycle: ✅ CLOSED.** Implementation begins per DEC-590. All flagged items addressed (resolved, deferred, or backlogged).

---

## Cross-references

- `AUDIT_INDEX.md` — DEC entries DEC-509 through DEC-590
- `AUDIT.md` — narrative entries per Pass 53 turn
- `STRATEGY_ROSTER_FULL.md` — F-002 strategy roster (199 classes; Layer 1-6)
- `TRADING_RULES_AND_INFORMATION.md` — §10 regime + §8 exits + §3 gates + §11 fill methodology + §23 tuning methodology
- `CANONICAL_FACTS.md` — F-001 through F-013 + F-009 7-gate update
- `DETAILED_PROJECT_PLAN.md` — Sprint pre-Phase-1A roadmap + Phase 1A-α through Phase 1B-α phasing
- `AUDIT_BACKLOG_FUTURE.md` — created post-Phase-1A; future review findings go here
