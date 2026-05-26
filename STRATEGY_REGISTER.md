# Strategy Register — Single Source-of-Truth

**2026-05-26 Batch 372 LIVE COUNT:** `len(ALL_STRATEGIES) = 186` registered; `DEPRECATED_STRATEGIES = 0` (Batch 316a empty); `STRATEGIES_DISABLED_MISSING_PRODUCER = 1` (Batch 372 disabled `dxy_headwind_multinational_short` pending foreign_rev_pct producer); **185 active for Phase 1A-β cube** (185 × 25 = 4,625 cells, down from 4,650 pre-Batch-372). The "60" figure below refers to the Layer 1 baseline only; the live total spans Layer 1 + Layer 2 + Layer 3 + Wave 3 additions + Batch 316a un-deprecated literature-null strategies.

**2026-05-15 Batch 178 status:** No strategy roster changes this session. Phase 1A backtest pipeline operates on Layer 1 baseline (60 strategies) per CANONICAL_FACTS.md F-002. Live per-strategy ranking on https://jeetmehta1991.github.io/stock-picks-app/dashboard_phase_1a/#strategies tab.

**Generated:** Pass 52 turn 53
**Purpose:** Canonical enumeration of all trading strategies in the project (current + projected + pending decision)
**Sourcing rules:**
- PROJECT_PLAN section 6 = baseline 60 strategies
- DEC-045 / DEC-259 / DEC-261 = Phase 0.D ICT/SMC additions
- Pass 52 RESOLVED-DECIDED additions (DEC-355-362, DEC-367-371) = chart pattern + strategy categories
- Pass 52 PENDING strategy-additive sub-decisions (DEC-141/142/143/145/176)

**Counting convention adopted Pass 52:**
- **Strategy class** = unique entry/exit logic (e.g., "RSI divergence reversal")
- **Strategy variant** = same class with parametric difference (e.g., "RSI divergence — long" vs "RSI divergence — short")
- The register counts **classes** (not variants) to match PROJECT_PLAN's "60" baseline. Variants are listed separately for transparency.

---

## Layer 1 — Baseline Roster (60 strategy classes per PROJECT_PLAN section 6 = baseline; live `len(ALL_STRATEGIES)`=186 Pass 53 includes later layers)

| Category | Count | Examples |
|---|---|---|
| Momentum / Trend | 12 | 50/200 SMA cross, breakout from base, sector momentum rotation |
| Mean Reversion | 10 | Oversold bounce, RSI divergence, Bollinger reversion |
| Smart Money | 8 | Congressional cluster buy, insider cluster buy, 13F accumulation |
| Volatility | 7 | VIX spike fade, IV crush, post-earnings drift |
| Fundamental | 8 | Earnings momentum, analyst upgrade clusters, buyback announcements |
| Macro / Regime | 6 | Yield curve trades, crisis dip-buying, sector rotation |
| Event-Driven | 9 | Spinoffs, M&A arbitrage, post-IPO drift, earnings PEAD |
| **Total Layer 1** | **60** | |

Detailed enumeration of the 60 baseline classes preserved in `PROJECT_PLAN_ARCHIVE.md` sections 5 and 6.

---

## Layer 2 — Phase 0.D Additions (ICT/SMC + Earnings Momentum + Calendar)

Per DEC-045 (RESOLVED-DECIDED Pass 27), Phase 0.D adds new strategies via:

### Layer 2A — ICT/SMC Strategies (via smartmoneyconcepts library fork)

DEC-259 enumerates 6 ICT/SMC pattern types as signal primitives. Each pattern can support 1-2 strategy classes (entry on pattern formation; entry on pattern confirmation/retest). Initial enumeration:

| Strategy Class | Source Pattern | Direction | Status |
|---|---|---|---|
| FVG (Fair Value Gap) fill | FVG | Long + Short variants | Phase 0.D PENDING enumeration |
| BOS (Break of Structure) trend continuation | BOS | Long + Short variants | Phase 0.D PENDING enumeration |
| CHoCH (Change of Character) reversal | CHoCH | Long + Short variants | Phase 0.D PENDING enumeration |
| Order Block bounce | Order Block | Long + Short variants | Phase 0.D PENDING enumeration |
| Liquidity Grab reversal | Liquidity Grab | Long + Short variants | Phase 0.D PENDING enumeration |
| Premium-Discount zone trade | Premium/Discount | Long + Short variants | Phase 0.D PENDING enumeration |
| **Layer 2A subtotal** | **6 classes** | (12+ variants) | |

### Layer 2B — Earnings Momentum Strategies (custom build per DEC-045)

Per DEC-045: "Build (~1 week, custom strategy logic)". Audit doesn't enumerate specific classes. Estimated 3-5 classes typical for earnings momentum (pre-earnings drift, post-earnings drift, guidance-driven momentum, surprise-driven momentum).

| Strategy Class | Status |
|---|---|
| Earnings momentum strategies (count: estimated 3-5; not formally enumerated) | Phase 0.D PENDING enumeration |
| **Layer 2B subtotal** | **3-5 classes (estimated)** |

### Layer 2C — Calendar Strategies (custom build per DEC-045)

Per DEC-045: "Build (~1 week, trivial date math)". Audit doesn't enumerate specific classes. Conventional calendar strategies in academic literature: Sell-in-May, January effect, Santa rally, FOMC drift, end-of-month effect, turn-of-year effect.

| Strategy Class | Status |
|---|---|
| Calendar strategies (count: estimated 4-6; not formally enumerated) | Phase 0.D PENDING enumeration |
| **Layer 2C subtotal** | **4-6 classes (estimated)** |

### Layer 2 — Total Phase 0.D Additions

**Estimated 13-17 strategy classes** added during Phase 0.D implementation. Not yet formally enumerated as individual decisions; this is a gap.

---

## Layer 3 — Pass 52 RESOLVED-DECIDED Additions

### Layer 3A — Chart Pattern Strategies (DEC-355-362, X55 closure turn 51)

| Strategy Class | DEC | Direction Variants |
|---|---|---|
| Trendline break + retest | DEC-355 | Long + Short |
| Channel breakout + retest | DEC-356 | Long + Short |
| Range breakout + retest | DEC-357 | Long + Short |
| Wedge / Triangle / Pennant continuation (3 patterns) | DEC-358 | Long + Short per pattern |
| Head & Shoulders + Inverse | DEC-359 | Long (inverse) + Short (top) |
| Double top / Double bottom | DEC-360 | Long (bottom) + Short (top) |
| Cup & Handle / Inverted | DEC-361 | Long + Short |
| Flag / Pennant continuation | DEC-362 | Long + Short |
| **Layer 3A subtotal** | | **8 base classes (10 if DEC-358 counted as 3)** |

### Layer 3B — Strategy Categories (DEC-367-371, X1 Block 2 closure turn 33)

| Strategy Class Range | DEC | Specified Range |
|---|---|---|
| Pairs / Stat Arb strategies | DEC-367 | 3-5 strategies |
| Calendar / Seasonal strategies | DEC-368 | 4-5 strategies (overlaps with Layer 2C) |
| Cross-Asset strategies | DEC-369 | 3-5 strategies |
| Index Rebalance strategies | DEC-370 | 2 strategies |
| Within-category gaps catalog | DEC-371 | ≥10 within-category gaps |
| **Layer 3B subtotal** | | **22-27 strategies (with overlap caveat on DEC-368)** |

### Layer 3 — Total Pass 52 RESOLVED-DECIDED

**~30-35 strategy classes added** (8 chart patterns + ~22-27 categories, minus DEC-368/Layer-2C overlap of ~4-5 strategies).

---

## Layer 4 — PENDING Strategy-Additive Sub-Decisions

Sub-decisions that, on owner approval and engineering implementation, would add new strategy classes:

| DEC | Description | Estimated Strategy Class Count |
|---|---|---|
| DEC-141 | Sector-neutral hedge overlay | 1 (overlay variant) |
| DEC-142 | Market-neutral long+short SPY | 1 (overlay variant) |
| DEC-143 | IPO/lockup/secondary offering systematic framework | 2-3 |
| DEC-145 | IV delta vs historical pre-earnings pattern | 1 |
| DEC-176 | Meta-strategies (boolean AND/OR combinations) | Multiplier on existing (not additive class) |
| **Layer 4 subtotal** | | **~5-6 classes (DEC-176 not counted)** |

---

## Total Roster Summary

| Layer | Status | Strategy Classes |
|---|---|---|
| Layer 1 (PROJECT_PLAN baseline) | DOCUMENTED + IMPLEMENTED | 60 |
| Layer 2 (Phase 0.D adds) | DECIDED at category level; class enumeration PENDING | ~13-17 |
| Layer 3 (Pass 52 RESOLVED-DECIDED) | RESOLVED-DECIDED | ~30-35 |
| Layer 4 (PENDING strategy-additive) | PENDING owner approval | ~5-6 |
| **Projected total at full implementation** | | **~108-118 classes** |
| **With long/short variants counted** | | **~150-200+ variants** |
| **With multi-TF variants per DEC-350 (daily + weekly)** | | **~200-300+ variants** |

## Pass 53 Day 9+ 2026-05-19 — Phase 1A-β scope clarification

Per owner directive 2026-05-19 (codified in [STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md](STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md)):

**Phase 1A-β tests ALL strategies × ALL exits × ALL regimes across the FULL 1937-tkr Master Dedup universe.** No pre-filtering. Roster scope = ~180 strategies (Layer 1 baseline 60 + T1.1-T1.5 batch 229-233 modules 16 + Phase 1C+ implementations ~100). Exit method roster = ~17 (DEC-067 canonical 17 methods + Batch 226/227 extensions). Total cells evaluated = ~180 × 17 × 4 regimes = ~12,240 (strategy × exit × regime) cells.

**Output:** `winners.parquet` with per-(strategy × exit × regime) priority tier:
- **P1 (must test with agents in Phase 1B-α):** passes all 11 overall criteria + DEC-426 5-Gate validity
- **P2 (optional):** per-regime PASS in ≥1 regime
- **P3 (skip):** below per-regime PASS

Phase 1B-α agents apply ONLY to P1 winners to test whether agent overlay optimizes ROI of already-validated baselines. This is the canonical workflow — NOT applying agents to full universe.

---

## Counting convention notes

- **"60 baseline" in PROJECT_PLAN counts classes, not variants.** A strategy with both long and short entry logic counts as 1 class.
- **120+ strategies achievable** when:
  - All 4 layers implemented (~108-118 classes)
  - Long/short variants counted separately (~+30-40)
  - Multi-TF variants per DEC-350 counted (~+60 if non-ICT roster doubled)
- **Class count vs variant count** — the project's authoritative count uses **classes** unless otherwise specified.

---

## Status update (Pass 53 — 2026-05-06; UPDATED post owner "Approve all")

**Per-strategy enumeration is now in [STRATEGY_ROSTER_FULL.md](STRATEGY_ROSTER_FULL.md) (Pass 53 Option 2 + owner "Approve all" 2026-05-06).** Owner Pass 53 turn:

1. Option 2 generated a consolidated per-strategy table for all layers with DRAFT-PROPOSED names for Layer 2A directional split (12), Layer 2B (4), Layer 2C (5), Layer 3B (21).
2. Owner "Approve all" 2026-05-06 promoted all 42 DRAFT-PROPOSED items → ✅ RESOLVED-DECIDED.
3. Layer 2D form-derived ICT remains ⏸ PENDING-FORM (owner-driven; no Claude drafts per directive).
4. Layer 4 remains 🔴 PENDING-DEC (per-DEC promotion separate; DEC-141/142/143/145/176).

**This doc (STRATEGY_REGISTER.md) remains canonical for the layered-roster summary** (categorical counts + DEC mapping). For individual strategy names, refer to [STRATEGY_ROSTER_FULL.md](STRATEGY_ROSTER_FULL.md).

**Aggregate post Pass 53 "Approve all":** 134 RESOLVED-DECIDED + IMPLEMENTED named classes; 138 with Layer 4 promotion; ~148 with Layer 2D form-derived estimate.

---

## Open enumeration gaps — CLOSED Pass 53 owner "Approve all" 2026-05-06

| Gap | Pre-Pass-53 status | Post-Pass-53 status |
|---|---|---|
| 1. Layer 2A — ICT/SMC strategy enumeration: confirm 6 patterns × variants = N classes | OPEN | ✅ CLOSED — 12 classes (6 patterns × 2 directional) |
| 2. Layer 2B — Earnings momentum class enumeration | OPEN | ✅ CLOSED — 4 named strategies in [STRATEGY_ROSTER_FULL.md](STRATEGY_ROSTER_FULL.md) Layer 2B |
| 3. Layer 2C — Calendar strategy class enumeration | OPEN | ✅ CLOSED — 5 named strategies in [STRATEGY_ROSTER_FULL.md](STRATEGY_ROSTER_FULL.md) Layer 2C; DEC-368 absorbed |
| 4. Layer 3B — DEC-371 within-category catalog enumeration: ≥10 gaps not itemized | OPEN | ✅ CLOSED — 11 named strategies in [STRATEGY_ROSTER_FULL.md](STRATEGY_ROSTER_FULL.md) Layer 3B (DEC-371 sub-section) |

All 4 gaps resolved. Implementation tracked per Sprint 7 (Phase 0.D) and Sprint 8 (Phase 1C+) per STRATEGY_ROSTER_FULL.md "Implementation sequencing" section.

---

## Sourcing

- `PROJECT_PLAN.md` section 6 (line 99) — baseline 60 strategies
- `PROJECT_PLAN_ARCHIVE.md` sections 5, 6 — detailed enumeration of 60 baseline
- `AUDIT_INDEX.md` — DEC-045 (Phase 0.D fork), DEC-259 (ICT/SMC cache patterns)
- `AUDIT_INDEX.md` — DEC-355-362 (chart pattern strategies, RESOLVED-DECIDED Pass 52)
- `AUDIT_INDEX.md` — DEC-367-371 (strategy categories, RESOLVED-DECIDED Pass 52)
- `AUDIT_INDEX.md` — DEC-141/142/143/145/176 (PENDING strategy-additive)

---

*Per CHECKLIST #43/#46/#47/#56/#57. Pass 52 turn 53.*

---

## Pass 53 Update — Phase 1A Strategy Scope Clarification

**Trigger:** Phase 1A restoration (DEC-486/487/488 PROPOSED).

**Strategy roster scope per phase:**

| Phase | Strategy roster | Agent overlay | Smart money signals |
|---|---|---|---|
| Phase 1A (rules-only baseline, Sprint 6.5) | Full Layer 1+2+3+4 (live 2026-05-25 Batch 360: **186 classes**; was "~109-119" pre-Batch-316a) | NO | YES — DEC-124 confluence + DEC-332 weights |
| Phase 1A-α (rules-only cube, Sprint 6.5-7) | Same as 1A — analyzes 1A trade outcomes | NO | (signals already in 1A trades) |
| Phase 1A-β (full-scale dry-run, Sprint 7 D1) | Same as 1A — production scale | NO | (signals already in 1A trades) |
| Phase 1B (agent overlay, Sprint 7) | Same as 1A — agent layer added on top | YES — TradingAgents 12-agent pipeline | (signals enriched via OurFundamentalsToolkit) |
| Phase 1B-α (combined cube, Sprint 7-8) | Aggregates 1A + 1B trade outcomes across 3 A/B arms | (varies per arm) | (varies per arm) |

**Implication:** Strategy roster does NOT change between Phase 1A and Phase 1B. Same **185 active strategy classes** fire in both (186 registered live `len(ALL_STRATEGIES)` 2026-05-26 Batch 372; minus 1 disabled in `STRATEGIES_DISABLED_MISSING_PRODUCER` per Batch 372; was "~109-119" pre-Batch-316a). The DIFFERENCE between phases is whether agent overlay sits on top of rules+smart-money output, NOT which strategies fire.

**Smart money clarification:** Smart money signals (DEC-124 cross-source confluence; DEC-332 weights; DEC-450 Quiver paid endpoints) are part of RULES-BASED screening, NOT agent overlay. They feed strategy entry signals + tier preliminary assignment in BOTH Phase 1A and Phase 1B. This is preserved from PROJECT_PLAN_ARCHIVE Phase 1A v3 architecture: "We ran all 60 strategies on a small universe of 67 instruments to make sure the pipeline works correctly" (historical quote; was 60 Layer-1 baseline, live 186 Pass 53) — strategies fired without agents in 1A v3, same pattern preserved Pass 53.


---

## Pass 53 Update Continuation — Phase 1A Skipped Strategies (DEC-490 RESOLVED-DECIDED)

**Per DEC-484 (financials deferred to Sprint 4 SEC EDGAR) + DEC-485 (transcripts dropped from Stage 2), 2 Layer 1 Fundamental strategies SKIP in Phase 1A:**

| Strategy ID | Reason for skip | Phase 1B status | Stage 3 status |
|---|---|---|---|
| `buyback_announcements` | Needs 10-Q/10-K share-count delta from full financials (DEC-484) | ACTIVATES once SEC EDGAR financials cache operational (Sprint 4 → Sprint 7 chain) | Active |
| `guidance_driven_momentum` | Needs earnings call transcripts for guidance language (DEC-485 dropped) | REMAINS SKIPPED through Stage 2 | REVISIT — owner may subscribe FMP $14-50/mo if Stage 2 verdict warrants transcripts re-introduction |

**Phase 1A trade log behavior:**
- These 2 strategies tagged `SKIPPED_NO_FUNDAMENTALS_PHASE_1A` flag
- Zero Phase 1A trade entries for buyback_announcements or guidance_driven_momentum strategy_id
- Cube cells for these 2 strategies remain INSUFFICIENT_SAMPLE in Phase 1A-α verdict

**Layer 1 Fundamental category effective Phase 1A roster: 6 of 8 strategies fire.**
- ✓ Earnings momentum (uses Polygon earnings dates + EPS)
- ✓ Analyst upgrade clusters (uses Quiver paid analyst rating changes)
- ✗ Buyback announcements (SKIPPED — needs SEC EDGAR Sprint 4)
- ✓ Post-earnings PEAD (uses Polygon earnings + EPS surprise)
- ✓ Pre-earnings positioning (uses Polygon earnings + IV)
- ✗ Guidance-driven momentum (SKIPPED — transcripts dropped DEC-485)
- ✓ Surprise-driven momentum (uses Polygon EPS surprise)
- ✓ Earnings season pre/post (uses Polygon earnings dates)

**Layer 2 Earnings Momentum (DEC-045) effective Phase 1A roster:** Same logic. Strategies that fire on earnings dates + EPS = active. Strategies that fire on transcript guidance = SKIPPED.

**Total Phase 1A active strategy count:** ~117 of ~119 classes fire (2 skipped per DEC-490).

---

## Pass 53 Addendum — Post Sprint-1-Pre-Flight (Stream 3 chunk B)

No new strategies added Pass 53 post-pre-flight. Strategy roster (~119 classes; ~117 active in Phase 1A per DEC-490) is unchanged from the prior Phase 1A Restoration entry above.

**Pass 53 changes that DO affect strategy execution context (but not roster size):**

| Pass 53 change | Effect on strategy execution |
|---|---|
| §2A Signal Universe Catalogue (TRADING_RULES NEW) | Canonical reference for ~265-275 signal fields strategies consume. Strategies should reference §2A for available signals rather than scattered code comments. |
| §10.8 Smart Money Composite (TRADING_RULES NEW) | Composite weights matrix `+4/+2/+1/-3/-1` + composite labels by score now canonical for `smart_money_composite` strategy filter (tier upgrade logic + multi-source confluence strategies). |
| §13.12 API Endpoint Inventory (TRADING_RULES NEW) | Strategies reading specific endpoints should reference §13.12 for canonical source per signal category. |
| DEC-494 Tier 2 alignment (refresh_extended_universe.py NDX-non-S&P removal) | DEC-370 Index Rebalance strategies (Layer 3B) reference T1c (`Tier 1C Universe_NASDAQ-100 Tickers_Jan 2020 to May 2026.csv`) for NDX events, NOT Tier 2 Universe_Spinoffs and Recent IPOs_Sep 2014 to May 2026.csv. Phase 1C+ scope. |
| DEC-496 Tier 3 momentum methodology | Tier 3 Universe_Momentum Top-100_Jun 2022 to May 2026.csv populate uses Jegadeesh-Titman 12-1 (DEC-496). Strategies that fire on Tier 3 names get this universe via universe.py `get_momentum_watchlist()` — schema preserves `added_date`/`removed_date` for PIT correctness. |
| DEC-491/492/493 PROPOSED Sprint 2 trade-capture fragility | Affects strategy POST-EXECUTION analysis (trade_log Parquet format, signals_at_entry preservation, trade_id schema). No effect on strategy entry/exit logic itself. |
| Universe folder move (commit `c7f5580f`) | Strategies that programmatically read universe CSVs now use `backtest.data.universe` module loaders via `UNIVERSE_DIR` constant. No code change required for strategies using existing `get_*` functions. |

Phase 1A active count remains ~117 of ~119 (per DEC-490).

**Cross-references:**
- TRADING_RULES.md §2A canonical signal universe
- TRADING_RULES.md §10.8/§10.9 smart money composite + adjacent
- DOCUMENTATION_REGISTER.md Pass 53 post-pre-flight entry
- AUDIT.md Pass 53 narrative entries

