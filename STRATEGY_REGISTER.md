# Strategy Register — Single Source-of-Truth

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

## Layer 1 — Baseline Roster (60 strategy classes per PROJECT_PLAN section 6)

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

---

## Counting convention notes

- **"60 baseline" in PROJECT_PLAN counts classes, not variants.** A strategy with both long and short entry logic counts as 1 class.
- **120+ strategies achievable** when:
  - All 4 layers implemented (~108-118 classes)
  - Long/short variants counted separately (~+30-40)
  - Multi-TF variants per DEC-350 counted (~+60 if non-ICT roster doubled)
- **Class count vs variant count** — the project's authoritative count uses **classes** unless otherwise specified.

---

## Open enumeration gaps

These are not decisions to make today; they're documentation gaps to close before Phase 0.D and Sprint 8 (strategy categories implementation) begins:

1. **Layer 2A — ICT/SMC strategy enumeration:** confirm 6 patterns × variants = N classes
2. **Layer 2B — Earnings momentum class enumeration:** specific classes within "earnings momentum" umbrella
3. **Layer 2C — Calendar strategy class enumeration:** specific calendar strategies (Sell-in-May, etc.)
4. **Layer 3B — DEC-371 within-category catalog enumeration:** ≥10 gaps not yet itemized

These gaps will be closed during sprint planning for Phase 0.D (Sprint 7 in ENGINEERING_REGISTER.md) and Sprint 8 (strategy categories).

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
| Phase 1A (rules-only baseline, Sprint 6.5) | Full Layer 1+2+3+4 (~109-119 classes) | NO | YES — DEC-124 confluence + DEC-332 weights |
| Phase 1A-α (rules-only cube, Sprint 6.5-7) | Same as 1A — analyzes 1A trade outcomes | NO | (signals already in 1A trades) |
| Phase 1A-β (full-scale dry-run, Sprint 7 D1) | Same as 1A — production scale | NO | (signals already in 1A trades) |
| Phase 1B (agent overlay, Sprint 7) | Same as 1A — agent layer added on top | YES — TradingAgents 12-agent pipeline | (signals enriched via OurFundamentalsToolkit) |
| Phase 1B-α (combined cube, Sprint 7-8) | Aggregates 1A + 1B trade outcomes across 3 A/B arms | (varies per arm) | (varies per arm) |

**Implication:** Strategy roster does NOT change between Phase 1A and Phase 1B. Same ~109-119 strategy classes fire in both. The DIFFERENCE between phases is whether agent overlay sits on top of rules+smart-money output, NOT which strategies fire.

**Smart money clarification:** Smart money signals (DEC-124 cross-source confluence; DEC-332 weights; DEC-450 Quiver paid endpoints) are part of RULES-BASED screening, NOT agent overlay. They feed strategy entry signals + tier preliminary assignment in BOTH Phase 1A and Phase 1B. This is preserved from PROJECT_PLAN_ARCHIVE Phase 1A v3 architecture: "We ran all 60 strategies on a small universe of 67 instruments to make sure the pipeline works correctly" — strategies fired without agents in 1A v3, same pattern preserved Pass 53.

