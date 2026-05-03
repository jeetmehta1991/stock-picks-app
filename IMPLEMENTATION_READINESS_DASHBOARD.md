# Implementation Readiness Dashboard

**Generated:** Pass 52 turn 36
**Source-of-truth:** AUDIT_INDEX.md + AUDIT.md history
**Decision counts:** 461 total / 312 PENDING / 114 RESOLVED / 10 DEFERRED_TO_STAGE_3 / 2 BLOCKED_ON_BUG-095 / 23 other

---

## TL;DR — what to do now

**Phase 0 sub-phase status determines everything.** Implementation readiness is gated by a small set of foundational decisions that unblock most downstream work.

The order is: **Phase 0.A prefetch → Phase 0.B Portfolio class → Phase 0.E catch mechanisms → Phase 0.D smartmoneyconcepts** → then Stage 2 backtest engine work runs in parallel → then Phase 1B-α run.

Approximate net-new implementation time post Pass 52 decisions: **40-55 engineering days** before Phase 1B-α can run.

---

## What's READY TO START IMPLEMENTING NOW (no decision blockers)

These have been decided, scoped, and have no upstream blockers. Owner can hand them to engineering as work items today.

### Group A — Phase 0.A Polygon prefetch foundation (~7-9 days)

| Decision | Scope | Effort | Resolves |
|---|---|---|---|
| **DEC-441** | Polygon Stocks Starter $30/mo subscription setup | 0.5d | Unblocks all Polygon work |
| **DEC-256** | Earnings calendar prefetch via Polygon events endpoint | ~2d | BUG-013, BUG-280, days_to_earnings cube dim |
| **DEC-257** | Quarterly fundamentals prefetch (Polygon→yfinance fallback) | ~3-4d | Unblocks DEC-393 (market_cap_pit) |
| **DEC-440** | Polygon news endpoint integration (replaces broken Finnhub) | absorbed in DEC-256 | BUG-053, BUG-181, sentiment cube |
| **DEC-261** | ICT/SMC PIT N+1 lag rule documentation | ~0.5d | DEC-259 prerequisite |
| **DEC-260** | Cache freshness assertion (uniform CacheStaleError) | ~1d | BUG-19 silent fallback class |

### Group B — Critical engine-bug fixes (Tier A from THEME_X53_SEQUENCING.md, ~9 days)

| Decision | Scope | Effort | Resolves |
|---|---|---|---|
| **DEC-381** | Cache get_ohlcv symmetric front-extension | ~1d | Cache silent truncation |
| **DEC-382** | Cache 20-day floor → min(20, available) + LIMITED_HISTORY flag | ~0.5d | Tier 2 ticker exclusion |
| **DEC-383** | Remove zero-volume drop in cache writes | ~0.5d | Halted-stock invisibility |
| **DEC-384** | update_trailing_stop intraday HIGH/LOW signature | ~1d | BUG-232 (trailing-stop lookahead) |
| **DEC-388** | VIX 5-day SMA + hysteresis regime input | ~0.5d | Regime classifier flapping |
| **DEC-389** | AAII pub-lag fix (1 trading day shift) | ~0.5d | BUG-235 HIGH OPEN |
| **DEC-390** | AAII auto-refresh script + GH Actions workflow | ~0.5d | BUG-236 HIGH OPEN |
| **DEC-391** | CNN F&G interpolation → last-published with age_days | ~0.5d | Interpolation lookahead |
| **DEC-392** | apply_liquidity_filter fail-closed + DEC-457 tier-specific | ~1.5d combined | DEC-321 + DEC-366 |
| **DEC-394** | Static sector_history.csv major reclassifications | ~1d | Sector PIT partial fix |
| **DEC-397** | Replace hardcoded calendar with rolling train/oos windows | ~1d | Methodology inflexibility |
| **DEC-398** | Borrow cost path investigation | ~0.5d | Diagnostic before consolidation |
| **DEC-399** | Borrow cost consolidation | ~1d | Code path duplication |

### Group C — DEC-410 audit findings (~5-7 days)

| Decision | Scope | Effort |
|---|---|---|
| **DEC-442** | Demote yfinance to fallback OHLCV (after Polygon validates) | absorbed in Polygon prefetch |
| **DEC-443** | Replace yfinance .info with Polygon reference | ~1d (BUG-218 CRITICAL fix) |
| **DEC-444** | Deprecate days_to_next_earnings via yfinance live calls | absorbed in DEC-256 |
| **DEC-445** | Polygon precomputed indicators as DEC-439 differential reference | ~1d |
| **DEC-446** | Polygon intraday quotes for slippage calibration sample | ~1d |
| **DEC-447** | Polygon reference tickers PIT consumption pattern | absorbed in DEC-443 |
| **DEC-448** | Expand FRED SERIES_MAP (+VIXCLS, DTWEXBGS, DGS2, HY, ICSA) | ~0.5d |
| **DEC-449** | Validate DEC-301 ALFRED PIT mitigation | ~0.5d |
| **DEC-450** | Extend prefetch_quiver.py to ALL paid-tier endpoints | ~3-5d (was 2-3d pre-correction) |
| **DEC-451** | Fix BUG-284 gov_contracts date filter | ~0.5d |
| **DEC-453** | Deprecate Finnhub from project entirely | ~0.5d |
| **DEC-454** | Remove OpenBB from PROJECT_PLAN section 10 | ~0.25d |
| **DEC-455** | Alpha Vantage deprecation timeline | ~0.5d |
| **DEC-456** | SEC EDGAR as DEC-439 differential reference | ~2d |

### Group D — Universe management (~5-8 days)

| Decision | Scope | Effort |
|---|---|---|
| **DEC-363** | LIT/DBB/COPX commodity ETFs | ~0.5d |
| **DEC-364** | Tier 3 momentum size 50→100 | ~0.5d |
| **DEC-372** | Tier 2 GH Actions monthly automation | ~1d |
| **DEC-373** | Tier 2 --validate mode | ~0.5d |
| **DEC-374** | Tier 2 historical-membership backfill 2010-2024 | ~3-5d |
| **DEC-375** | Tier 3 code changes (50→100 in build_momentum_watchlist) | ~0.5d |
| **DEC-376** | Tier 3 GH Actions automation | ~0.5d |
| **DEC-378** | NASDAQ symbol-directory weekly diff (spinoff detector phase 1) | ~1d |
| **DEC-379** | SEC EDGAR Form 10-12B feed scraping | ~2d |
| **DEC-380** | Polygon Reference corporate-actions integration | ~1d |
| **DEC-365** | Russell 1000 universe expansion Phase A | ~1d |
| **DEC-457** | DEC-366 tier-specific liquidity filter implementation | ~1.5d (joint with DEC-392) |
| **DEC-394** | Static sector_history.csv | ~1d (also in Group B) |

### Group E — Strategy category gaps (Theme X1 Block 2, ~14-18 days)

| Decision | Scope | Effort | Notes |
|---|---|---|---|
| **DEC-368** | Calendar/Seasonal strategies (4-5 strategies) | ~2-3d | Cheap; date-based filters |
| **DEC-371** | Within-category gaps catalog | ~1d | Documentation deliverable |
| **DEC-367** | Pairs/Stat Arb (3-5 strategies) | ~5-7d | Cointegration framework + paired execution |
| **DEC-369** | Cross-Asset (3-5 strategies) | ~5-7d | TLT/GLD/UUP/USO intermarket; FRED expansion ready |
| **DEC-370** | Index Rebalance (2 strategies) | ~3-5d | S&P/Russell calendar + frontrun |

### Group F — Phase 0.E catch-mechanism defense (~7-10 days)

| Decision | Scope | Effort |
|---|---|---|
| **DEC-417** | Test-run audit gate retroactive validation | ~3d (one-time) |
| **DEC-436** | CI/CD gate (smoke + property + characterization) | ~2d |
| **DEC-437** | Property-based testing (hypothesis library) | ~2d |
| **DEC-438** | Characterization tests for known-good behaviors | ~1d |
| **DEC-439** | Differential testing (pandas vs numpy + Polygon vs SEC EDGAR) | ~2d (joint with DEC-445/456) |

---

## What's BLOCKED on a specific dependency

These have decided scope but cannot start until prerequisite work lands.

### Blocked on Phase 0.A prefetch (DEC-256/257)

| Decision | Blocked-on | Effort post-blocker |
|---|---|---|
| **DEC-393** | DEC-257 Polygon fundamentals (PIT shares outstanding) | ~1d |

### Blocked on DEC-450 (Quiver paid-tier prefetch extension)

| Decision | Blocked-on | Effort post-blocker |
|---|---|---|
| **DEC-396** | DEC-450 Quiver 13F prefetch with filing_date capture | ~1-2d |

### Blocked on DEC-298 (PIT cache rebuild — currently PENDING separate)

| Decision | Blocked-on | Effort post-blocker |
|---|---|---|
| **DEC-411** | DEC-298 cache rebuild + PIT auto_adjust=False | ~1d |
| **DEC-377** | DEC-298 PIT OHLCV (Tier 3 historical-recomputation) | ~3-5d |

### Blocked on Phase 0.B Portfolio class (BUG-095 CRITICAL OPEN)

| Decision | Blocked-on | Effort post-blocker |
|---|---|---|
| **DEC-070** | BUG-095 Portfolio class implementation (Phase 0.B) | ~3-5d |
| **DEC-076** | BUG-095 + DEC-070 (sequencing chain) | ~2-3d |

### Blocked on Phase 0.D smartmoneyconcepts fork verification

| Decision | Blocked-on | Effort post-blocker |
|---|---|---|
| **DEC-259** | Phase 0.D smartmoneyconcepts library operational | ~2-3d |

---

## What's AWAITING OWNER DECISION (substantive scope choices)

None currently — all open Pass 52 owner-decision items closed.

(For reference: Block 3 of Theme X1 was the last open block; DEC-365/366/457 closed turn 35.)

---

## What's CRITICAL OPEN (must resolve before Phase 1B-α can run)

### Critical OPEN bugs (21 total — sample, full list in AUDIT_INDEX)

- **BUG-218** — yfinance fetch_info CURRENT not as_of (resolved by DEC-443)
- **BUG-095** — No portfolio-level state; every trade evaluated independently (resolved by Phase 0.B Portfolio class implementation)
- **BUG-NN** — Trailing stop lookahead bias (resolved by DEC-313/337/384)
- **BUG-NN** — VIX proxy is VXX price not actual VIX (regime classifier broken; needs investigation — likely DEC-388 covers)
- **BUG-NN** — Email approval system 6 critical design gaps (Stage 4 scope; deferred)
- **BUG-NN** — Stage 3 paper trading cannot actually run as designed (Stage 3 scope; deferred)

### Critical decisions still PENDING-with-blocker

- **DEC-298** — PIT cache rebuild auto_adjust=False (PENDING; blocks DEC-411 + DEC-377)
- **DEC-070/076** — Portfolio-level breakers (BLOCKED_ON_BUG-095; resolves only after Phase 0.B Portfolio class lands)
- **BUG-095 Portfolio class** — not a decision, but a CRITICAL implementation gap

---

## Implementation sequencing (recommended order)

### Sprint 1 (Phase 0.A foundation) — ~7-9 days

1. DEC-441 Polygon subscription setup
2. DEC-256 Polygon earnings prefetch
3. DEC-257 Polygon fundamentals prefetch
4. DEC-440 Polygon news (absorbed)
5. DEC-260 Cache freshness assertion
6. DEC-261 ICT/SMC PIT lag rule

**Unblocks:** DEC-393, DEC-444 (yfinance earnings deprecation), Polygon-dependent work

### Sprint 2 (Engine bug fixes Tier A) — ~9 days

DEC-381/382/383/384/388/389/390/391/392/394/397/398/399 (parallel-friendly per THEME_X53_SEQUENCING.md)

### Sprint 3 (Phase 0.B Portfolio class) — ~5-7 days [CRITICAL — blocks DEC-070/076]

Implement Portfolio class addressing BUG-095. Per CLAUDE.md / PROJECT_PLAN — this is the critical missing infrastructure.

**Unblocks:** DEC-070, DEC-076

### Sprint 4 (DEC-410 audit findings) — ~5-7 days

DEC-442/443/444/445/446/447/448/449/450/451/453/454/455/456 (parallel where possible)

**Unblocks:** DEC-396 (after DEC-450)

### Sprint 5 (Universe management) — ~5-8 days

DEC-363/364/365/372/373/375/376/378/379/380/394/457

### Sprint 6 (Phase 0.E catch mechanisms + Architecture Hygiene) — ~14-19 days

DEC-417/436/437/438/439 (catch mechanisms) + DEC-217/218/219/220 (X33 architecture hygiene Pass 52 turn 95). DEC-220 fix priority HIGH (~0.5d) — resolves Pass 52 parallel-session attribution + reduces silent-overwrite risk on main.

### Sprint 7 (Strategy categories) — ~14-18 days

DEC-368/371 (cheap first), then DEC-367/369/370 (heavier)

### Sprint 8 (Remaining theme work)

Themes not fully walked: X4 Statistical Methodology (~25 PENDING), X54 Medium-Severity (~13), X55 Strategy Coverage (~11), X49 Thin Areas (~9), X36 Data Quality (~9), X3 Architecture (~9), X7 Smart Money + Regimes (~8), X58 Phase 1B-α Dimensional (~7)

### Sprint 9 (Phase 1B-α run) — gated by Sprints 1-6 completion

Run actual backtest with full universe + agents + dimensional cube.

---

## Approximate timeline

**To run Phase 1B-α with full readiness:**
- Sprint 1 (Phase 0.A): ~7-9 days
- Sprint 2 (Engine fixes): ~9 days (parallel with Sprint 1)
- Sprint 3 (Phase 0.B Portfolio class): ~5-7 days (sequential after Sprint 2)
- Sprint 4 (DEC-410 audit): ~5-7 days (parallel with Sprint 3)
- Sprint 5 (Universe): ~5-8 days (parallel with Sprint 3)
- Sprint 6 (Phase 0.E + Architecture Hygiene): ~14-19 days (parallel with Sprint 4-5)

**Critical path:** Sprint 1 → Sprint 2 → Sprint 3 → Phase 1B-α run = **~21-25 days minimum**.

**Realistic timeline accounting for parallelism:** ~30-40 engineering days from Sprint 1 start to Phase 1B-α-ready state.

**Total work scope (everything PENDING):** much larger; Sprint 7-8 strategy categories + remaining themes can run during/after first Phase 1B-α run.

---

## What's NOT on the critical path (can defer or run later)

- Tier 2 historical backfill (DEC-374, ~3-5d) — strategies need Tier 2 functional but historical 2010-2024 backfill can wait
- Tier 3 historical recomputation (DEC-377, ~3-5d) — blocked on DEC-298 anyway
- Strategy category additions DEC-367/369/370 (~14-18d) — Phase 1B-α can run with current 60-strategy roster; new categories enhance not gate
- DEC-446 intraday slippage calibration — calibration data nice-to-have for DEC-422 cell schema; can fall back to assumed values
- Sprint 8 remaining themes (~80+ PENDING) — most are X4 statistical methodology refinements that don't gate first backtest run

---

## Dashboard-status legend

- **READY** = decided, scoped, no blockers; can be assigned to engineering today
- **BLOCKED** = decided + scoped, but waiting on prerequisite
- **AWAITING OWNER** = needs owner direction on scope/approval (currently empty)
- **CRITICAL OPEN** = bug or decision that blocks Phase 1B-α run
- **DEFERRED** = correctly out of current scope (Stage 3+, Phase 1C+, etc.)

---

*Per CHECKLIST #43/#46/#47/#56/#57. Pass 52 turn 36. Generated with reversibility framework lens — implementation readiness scored on decision certainty + dependency-clear status.*

---

## Phase 2 Batch 1 Updates (Pass 52 turn 101)

Per CHECKLIST #58 — sprint readiness updates for newly-tracked decisions.

### Updated Sprint Effort Estimates

| Sprint | Previous | Revised | Delta | New decisions |
|---|---|---|---|---|
| Sprint 1 (Phase 0.A foundation) | ~7-9d | ~9-12d | +2-3d | DEC-040 (PIT loader) |
| Sprint 4 (DEC-410 audit findings) | ~5-7d | ~9-12d | +4-5d | DEC-072 (WSB sep), DEC-092 (slippage) |
| Sprint 5 NEW (Position Sizing) | n/a | ~3.5d | +3.5d new | DEC-086/087/088 (Kelly/vol-targeted/portfolio vol) |
| Sprint 6 (Phase 0.E + Hygiene + new) | ~14-19d | ~22-29d | +8-10d | DEC-067 (9 exits), DEC-075 (AEP), DEC-096 (reproducibility) |
| Sprint 7 (Statistical Methodology) | ~17-19d | ~27-29d | +10d | DEC-081/082/083/085 + DEC-106 |

### Total Stage 2 Implementation Effort

- Previous estimate: ~30-40 engineering days realistic
- Phase 2 Batch 1 revised: ~50-65 engineering days realistic
- Anticipated further revisions in Batches 2-6 (158 decisions remaining unclassified)

### Critical Path Implications

Critical path remains Sprint 1 → Sprint 2 → Sprint 3 → Phase 1B-α run. Newly-added decisions parallel-able with critical path:
- DEC-040 (Sprint 1) is on critical path; +2-3d delay
- DEC-072/092 (Sprint 4) are parallel
- Sprint 5 NEW block parallel with Sprints 4-5
- Sprint 6 additions parallel
- Sprint 7 additions on critical path before Phase 1B-α

Critical path effort revised: previously ~21-25 days minimum → ~28-35 days minimum (post-Phase-2-Batch-1).


---

## Phase 2 Batch 2 Updates (Pass 52 turn 103)

Per CHECKLIST #58 — sprint readiness updates for newly-tracked decisions.

### Updated Sprint Effort Estimates

| Sprint | Pre-Batch-2 | Post-Batch-2 | Delta | New decisions |
|---|---|---|---|---|
| Sprint 6 (Phase 0.E + Hygiene + new) | ~22-29d | ~23.5-30.5d | +1.5d | DEC-113 (Stage 2 portion ~0.5d), DEC-189 (~1d) |
| Sprint 7 (Statistical Methodology) | ~27-29d | ~36.5-38.5d | +9.5d | DEC-107/108/109/110/111/144/152 |
| Sprint 7-8 (Phase 1B-α / Strategy Categories) | unchanged | unchanged | absorbed | DEC-199 (Dashboard 1 spec absorbed in DEC-430) |

### Total Stage 2 Implementation Effort

- Pre-Batch-2: ~50-65 engineering days realistic
- Post-Batch-2: ~60-75 engineering days realistic
- Anticipated further revisions in Batches 3-6 (128 decisions remaining unclassified)

### Critical Path Implications

Critical path components affected by Batch 2:
- Sprint 7 +9.5d on critical path (statistical methodology gates Phase 1B-α)
- Sprint 6 +1.5d parallel (architecture hygiene non-blocking)
- DEC-109 walk-forward BLOCKED on DEC-298 PIT cache rebuild

Critical path effort revised: previously ~28-35d minimum → ~37-45d minimum (post-Phase-2-Batch-2).


---

## Phase 2 Batch 3 Updates (Pass 52 turn 105)

Per CHECKLIST #58 — sprint readiness updates for newly-tracked decisions. **Largest delta yet.**

### Updated Sprint Effort Estimates

| Sprint | Pre-Batch-3 | Post-Batch-3 | Delta | New decisions |
|---|---|---|---|---|
| Sprint 1 (Phase 0.A foundation) | ~9-12d | ~11.5-14.5d | +2.5d | DEC-225/227/235 (cache + calendar) |
| Sprint 4 (DEC-410 audit findings) | ~9-12d | ~16-22d | +7-10d | DEC-228/234/252 (fetcher + ticker lifecycle + IBKR commission) |
| Sprint 5 NEW position sizing | ~3.5d | ~3.5d | unchanged | (no Batch 3 additions) |
| Sprint 6 (Phase 0.E + Hygiene + new) | ~23.5-30.5d | ~37.5-47d | +14-16.5d | DEC-205/206 (A/B foundation), DEC-222/229/230/231/232/233/241 (test/config/logging/exception/data-quality/time-in-market) |
| Sprint 7 (Statistical Methodology + A/B operational) | ~36.5-38.5d | ~45.5-47.5d | +9d | DEC-207-210/212/215/216/242 (A/B operational + distribution analysis) |
| Sprint 7-8 (Phase 1B-α Dashboard + Strategies) | ~3-5d (Dashboard 1 only) | ~10-14d | +7-9d | DEC-200 (Dashboard 2 ~3-4d) + DEC-201 (Dashboard 3 ~4-5d) |
| Sprint 9 (Phase 1B-α run + ongoing) | n/a | ~2.5d | +2.5d new | DEC-211 ablation post-Phase-1B-α + DEC-214 quarterly re-validation |

### Total Stage 2 Implementation Effort

- Pre-Batch-3: ~60-75 engineering days realistic
- Post-Batch-3: ~95-115 engineering days realistic
- Anticipated further revisions in Batches 4-6 (98 decisions remaining unclassified)

### Critical Path Implications

Critical path components affected by Batch 3:
- Sprint 4 +7-10d on critical path (cost stack + reliability)
- Sprint 6 +14-16.5d parallel (architecture hygiene + A/B foundation non-blocking)
- Sprint 7 +9d on critical path (A/B operational gates Phase 1B-α verdict interpretation)
- Sprint 9 NEW (~2.5d) post-Phase-1B-α run scope
- DEC-211 ablation + DEC-214 quarterly re-validation are operational, not critical-path-blocking

Critical path effort revised: previously ~37-45d minimum → ~46-56d minimum (post-Phase-2-Batch-3).


---

## Phase 2 Final Sweep Updates (Pass 52 turn 107)

Per CHECKLIST #58 — sprint readiness updates for ALL remaining homeless decisions. **Phase 2 COMPLETE.**

### Final Sprint Effort Estimates (Phase 2 Complete)

| Sprint | Pre-Phase-2 | Post-Final-Sweep | Total Delta |
|---|---|---|---|
| Sprint 1 (Phase 0.A) | ~7-9d | ~17.5-23.5d | +10-15d |
| Sprint 2 (Engine Bug Fixes Tier A) | ~9d | ~23-27d | +14-18d |
| Sprint 3 (Phase 0.B Portfolio Class) | ~5-7d | ~8-11d | +3-4d |
| Sprint 4 (DEC-410 Audit Findings) | ~5-7d | ~30-41d | +25-34d (LARGEST) |
| Sprint 5 (Universe Management) | ~5-8d | ~6.5d | -ish (consolidation) |
| Sprint 5 NEW (Position Sizing) | n/a | ~3.5d | new |
| Sprint 6 (Phase 0.E + Hygiene) | ~7-10d | ~37.75-47.25d | +30-37d |
| Sprint 7 (Statistical Methodology + A/B) | ~17-19d | ~63.5-69.5d | +46-50d (MASSIVE) |
| Sprint 7-8 (Phase 1B-α Dimensional Cube) | gated | ~24-33d | new tracked |
| Sprint 8 (Strategy Categories) | ~50-60d | ~30-45d | -ish (consolidation; some absorbed Sprint 7) |
| Sprint 9 (Phase 1B-α run + ongoing) | n/a | ~2.5d | new |

### Total Stage 2 Implementation Effort (FINAL)

- Pre-Phase-2: ~30-40 engineering days
- Post-Phase-2-Batch-1: ~50-65 engineering days
- Post-Phase-2-Batch-2: ~60-75 engineering days
- Post-Phase-2-Batch-3: ~95-115 engineering days
- **Post-Phase-2-Final-Sweep: ~247-313 engineering days realistic**

### Critical Path Reality Check

Sprint 4 (DEC-410 + cost stack + reliability) and Sprint 7 (Statistical Methodology + A/B + cluster work) are now both critical-path heavy. Previous critical path estimate of ~21-25 days minimum was significantly understated.

**Realistic critical path post-Phase-2-Final-Sweep: ~100-130 engineering days minimum.**

### Implications

This is a **major reality-check** for project timeline. The retroactive audit revealed that the true Stage 2 engineering scope was ~6-8x larger than the original ~30-40 day estimate suggested. The hidden scope was in homeless RESOLVED-DECIDED decisions that had implementation work in scope text but no sprint-tracker entry.

Owner accountability call-out turn 98 was warranted — without retroactive audit, project would have entered Sprint 1 implementation with massively understated timeline expectations. With Phase 2 complete, sprint planning is now grounded in true scope.

Going forward: CHECKLIST #58 prevents recurrence by requiring sprint-tracker assignment in same commit as RESOLVED-DECIDED status flip.


---

## Phase 2 Cleanup Batch Updates (Pass 52 turn 109)

Per CHECKLIST #58 — sprint readiness updates for 22 substantively-homeless decisions now properly tracked.

### Updated Sprint Effort Estimates (Cleanup Batch)

| Sprint | Pre-Cleanup | Post-Cleanup | Delta | New decisions |
|---|---|---|---|---|
| Sprint 1 (Phase 0.A) | ~17.5-23.5d | ~23-29d | +5.5d | DEC-259/382/383/390/391 |
| Sprint 2 (Engine Bug Fixes Tier A) | ~23-27d | ~25.5-30.5d | +2.5-3.5d | DEC-313/321/399 |
| Sprint 4 (DEC-410 Audit Findings) | ~30-41d | ~33.75-46.25d | +3.75-5.25d | DEC-301/449/451/454/455 (DEC-444/447 absorbed) |
| Sprint 5 (Universe Management) | ~6.5d | ~11.5-13.5d | +5-7d | DEC-366/373/376/379 |
| Sprint 8 (Strategy Categories) | ~30-45d | ~36-54d | +6-9d | DEC-368/370/371 |

### Total Stage 2 Implementation Effort (FINAL POST-CLEANUP)

- Pre-cleanup: ~247-313 engineering days realistic
- **Post-cleanup: ~270-340 engineering days realistic**

### Critical Path Reality Check (UPDATED)

Critical path components affected by cleanup:
- Sprint 1 +5.5d (Phase 0.A foundation; on critical path)
- Sprint 4 +3.75-5.25d net-new (cost stack + DEC-410 cleanup; on critical path)
- Sprint 5 +5-7d (universe management; partially critical-path)
- Sprint 8 +6-9d (strategy categories; parallel-able)

**Critical path effort revised: ~100-130d minimum → ~110-145 engineering days minimum.**

### Substantive Homelessness Pattern Resolved

Owner caught the substantive homelessness gap turn 108 ("Any resolved homeless decisions not yet in registers?") — 22 decisions were textually mentioned in IMPLEMENTATION_READINESS_DASHBOARD but lacked proper ENGINEERING_REGISTER sprint slots with test signals + effort estimates. This violated the spirit of CHECKLIST #58 even though they technically appeared in a register.

Pattern now resolved: every RESOLVED-DECIDED engineering decision has proper sprint-table entry with test signals + effort. Going forward, CHECKLIST #58 enforces this from creation, not just textual mention.


---

## Walkthrough 4 Updates (Pass 52 turn 113)

Per CHECKLIST #58 — sprint readiness updates for Walkthrough 4 decisions.

### Updated Sprint Effort Estimates

| Sprint | Pre-W4 | Post-W4 | Delta | New decisions |
|---|---|---|---|---|
| Sprint 6 (Phase 0.E + Hygiene) | ~37.75-47.25d | ~39.25-48.75d | +1.5d | DEC-138 (cold-start CI test) |

### Total Stage 2 Implementation Effort

- Pre-W4: ~270-340 engineering days realistic
- Post-W4: ~271.5-341.5 engineering days realistic (minimal change; W4 was mostly supersessions/deferrals)

### Critical Path Implications

DEC-138 cold-start CI test fits Sprint 6 architecture hygiene block; parallel-able / non-blocking. No critical path change.

### Stage 3+ Deferred Cluster (data history)

DEC-158 + DEC-266 + DEC-298 (BLOCKED) form coherent Stage 3+ data-history evaluation cluster. Empirical gate post-Phase-1B-α: does extending history beyond 2018-01-01 baseline improve walk-forward Sharpe stability materially? If yes → activate ~5-7d data-history extension. If no → DEC-109 Option B 2018-01-01 baseline remains canonical.


---

## Bulk Sweep Batch B (Risk Management) Updates (Pass 52 turn 115)

| Sprint | Pre-B | Post-B | Delta |
|---|---|---|---|
| Sprint 4 | ~33.75-46.25d | ~34.25-46.75d | +0.5d |
| Sprint 6 | ~39.25-48.75d | ~42.25-51.75d | +3d |

Total Stage 2: ~271.5-341.5 → ~275-345 engineering days


---

## Batch C Updates (Pass 52 turn 117)

| Sprint | Pre-C | Post-C | Delta |
|---|---|---|---|
| Sprint 1 | ~17.5-23.5d | ~18-24d | +0.5d |
| Sprint 6 | ~42.25-51.75d | ~50.25-62.75d | +8-11d (largest) |
| Sprint 7 | ~63.5-69.5d | ~64-70d | +0.5d |
| Sprint 9 | ~2.5d | ~3.5d | +1d |

DEC-251 FLAGGED HARD-REVERSIBILITY — awaiting owner approval before sprint slot assignment.


---

## Bulk Sweep Final (Batches D-K + DEC-251) Updates (Pass 52 turn 119)

### Sprint Effort Estimates (FINAL POST-SWEEP)

| Sprint | Pre-Sweep | Post-Sweep | Total Delta from Pass 52 Start |
|---|---|---|---|
| Sprint 1 (Phase 0.A) | ~18-24d | ~20.5-26.5d | +13.5-17.5d (3x growth) |
| Sprint 2 (Engine Bug Fixes) | ~25.5-30.5d | ~25.5-30.5d (unchanged) | +16.5-21.5d (3x) |
| Sprint 3 (Portfolio class) | ~8-11d | ~8-11d | +3-4d |
| Sprint 4 (DEC-410 audit) | ~34.25-46.75d | ~41.75-54.25d | +36.75-47.25d (8x growth) |
| Sprint 5 (Universe management) | ~11.5-13.5d | ~13.5-15.5d | +8.5-7.5d |
| Sprint 5 NEW Position Sizing | ~3.5d | ~3.5d | new |
| Sprint 6 (Phase 0.E + Hygiene) | ~50.25-62.75d | ~62.25-76.75d | +55.25-66.75d (largest absolute, 6-7x) |
| Sprint 7 (Statistical Methodology + A/B) | ~64-70d | ~74.5-83.5d | +57.5-64.5d (3-4x) |
| Sprint 7-8 (Phase 1B-α Cube + Dashboards) | ~24-33d | ~28-38d | +25-33d |
| Sprint 8 (Strategy categories) | ~36-54d | ~37-55d | +1d |
| Sprint 9 (Phase 1B-α + ongoing) | ~3.5d | ~6d | new + 2.5d |

### Total Stage 2 Implementation Effort (FINAL)

- Pass 52 start: ~30-40d
- Post-sweep: **~310-385 engineering days realistic**

### Critical Path Reality Check (FINAL)

- Pass 52 start: ~21-25d minimum
- Post-sweep: **~125-160 engineering days minimum**

### Total scope expansion vs original Pass 52 starting estimate

- 8-10x scope expansion vs original ~30-40d estimate
- Hidden in homeless + substantively-homeless decisions: ~280-345 days of engineering work

### Owner Vindication

Owner accountability call-out turn 98 + verification questions turn 108 + bug coverage question turn 110 + bulk-sweep delegation turn 114-118 together revealed:
- True Stage 2 scope is 8-10x larger than original estimate
- Hidden scope was distributed across:
  * Homeless RESOLVED-DECIDED decisions (Phase 2 audit — 217 decisions)
  * Substantively-homeless engineering decisions (Phase 2 cleanup — 22 decisions)
  * Bug-decision linkage gap (BUG_REGISTER cross-reference — 148 bugs)
  * 80 PENDING decisions converted to RESOLVED-DECIDED (this sweep — sprint slots assigned)
- Going forward CHECKLIST #58 prevents recurrence at all 4 levels

