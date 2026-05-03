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

