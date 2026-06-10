# Stage 4 Breakout Cluster Walks — Per-Strategy Deep-Dive Audit

> **B676 status banner (2026-06-10, owner-directed autonomous continuation):** SIXTH per-cluster Stage 4 walk doc. Owner directive *"continue autonomously"* after B675 ICT cluster walk. Cluster contains **19 strategies** in `breakout` category — the LARGEST remaining unwalked cluster. Many have prior batch-level walks (B582/B586/B587/B589/B590/B591/B594/B595/B596/B598/B605/B608/B612/B626/B654) that collectively constitute "implementation" walks but NOT the systematic CHECKLIST #105 7-step methodology per-strategy. This doc IS that systematic walk.
>
> **Source of truth.** Code references reflect current state at commit `cba27db74` (post-B675 ICT walk).
>
> **CARRY-FORWARD from prior cluster walks + B673/B674 external reviewer critique:** **Pattern A** (default-True silent-gap), **Pattern M** (no peer-reviewed citation — partial; some breakouts cite George-Hwang 2004 JF + Bulkowski 2005 which ARE legitimate), **Pattern N** (intra-cluster collinearity — 19 strategies on a small primitive set), **Pattern O** (hardcoded tolerances — many in breakout cluster), **Pattern Q** (no-empirical-citation cluster-wide partial applicability), **Pattern F** (marginal-contribution audit), **Pattern G** (low-fire-combo EXPLORATORY). NEW patterns specific to this cluster surface in §[Cross-strategy patterns](#cross-strategy-patterns-breakout-cluster).
>
> Per `feedback_no_rushing_per_strategy_tweak` + `project_no_apriori_strategy_pruning` + foundational sequence (B660 in flight): all fires/yr projections PENDING B660; no code changes in this batch (B676 is doc-only).

---

## Audience

Two:

1. **External reviewer** — for you: the breakout cluster differs from prior clusters because (a) the underlying patterns are the MOST academically-grounded in the whole strategy roster — George-Hwang 2004 JF 52-week-high momentum anomaly, Bulkowski 2005 chart-pattern empirical work, classical breakout literature (Faith 2007 Turtle Trading, Connors + Raschke 1996, Wilder 1978) ALL apply legitimately. **Pattern M / Pattern Q (no peer-review) DO NOT APPLY** to the same degree as ICT/SMC/smart-money clusters. (b) The cluster has the **MOST forensic-fix evidence** of any cluster — B589 added `close_in_top_40pct_of_range`, B590 added ATR-band filter, B608 obv_bullish refactor, B654 cpr_narrow_tight all came from explicit post-1A-alpha forensic findings; the strategies are EMPIRICAL-FIX-anchored, not just owner-spec. (c) **CC1 next-open-after-gap concern from B673** PARTIALLY applies — breakout strategies DO have a gap-after-detection issue but it's a momentum-continuation gap (price keeps going up after the breakout), not a mean-reversion gap (M&A target-style). Capturable fraction is higher than M&A targets. (d) The cluster has **STRONG intra-family redundancy** — 4 of 19 are 52w-high/low variants, 6 of 19 are Donchian variants, 4 of 19 are retest-pattern variants — Pattern N intra-cluster collinearity is acute.

2. **Future readers** — [Cluster scope inventory](#cluster-scope-inventory) below.

---

## Methodology adaptations for breakout cluster

### 1. Legitimate academic anchor — Pattern M / Pattern Q DO NOT apply to most strategies

Unlike the SMC + ICT clusters (where Pattern M / Q applied to 10+ of 12+ strategies), the breakout cluster has GENUINE peer-reviewed methodology backing for most strategies:

| Strategy | Citation | Peer-review level |
|---|---|---|
| **52w_high_breakout family** | George-Hwang 2004 JF "The 52-Week High and Momentum Investing" | ✅ Top finance journal; documented anomaly |
| **52w_high_breakout_pullback_long + 52w_low_breakdown_pullback_short** | Bulkowski 2005 *Encyclopedia of Chart Patterns* retest-on-lower-volume thesis | ✅ Published, widely-cited chart-pattern methodology |
| **Donchian breakout family** | Faith 2007 *The Way of the Turtle* (Dennis-Eckhardt Turtle Trading) + Donchian's original 1960s work | ✅ Classical trend-following methodology |
| **break_retest family** | Bulkowski 2005 retest absorption thesis | ✅ Same as 52w-retest family |
| **Force index breakout** | Elder 1993 *Trading for a Living* | ✅ Published methodology (cited in B626 docstring) |
| **squeeze_breakout** | Carter 2008 TTM Squeeze | ⚠ Trader-methodology book; less peer-reviewed than the above but widely accepted |
| **inside_bar_breakout** | Classical price-action literature | ⚠ No specific peer-reviewed citation; generic pattern recognition |
| **volume_spike_breakout family** | Lo + Wang 2000 RFS volume-as-information + Akarim + Sevim 2013 (volume-price relationship) | ✅ Peer-reviewed |
| **classification_change_breakout_long** | Brogaard-Heath-Saadi 2019 reclassification literature | ✅ JFE-tier peer-review |

**Pattern Q applies WEAKLY to:** inside_bar_breakout (no specific cite); squeeze_breakout (trader-book not peer-review).

### 2. Forensic-fix density — Pattern A (default-True silent-gap) almost fully swept

The breakout cluster has the most B-batch forensic-fix evidence of any cluster:

| Forensic batch | Fix | Cluster impact |
|---|---|---|
| **B582** | `break_52w_high` / `break_52w_low` producer fix (was buggy DC20-anchored) | 52w_high_breakout + 52w_low_breakdown |
| **B584** | Donchian 10 breakout producer fix (excludes today from window) | donchian_10_breakout + donchian_breakdown_short + donchian_breakout_long |
| **B586** | vol_spike_17x + sector_outperforming_spy added to 52w_high_breakout | 52w_high_breakout |
| **B589** | close_above_open + close_in_top_40pct_of_range added across breakout family | ALL post-B589 strategies (15 of 19) |
| **B590** | 52w_pullback redesign: stable pre-breakout reference + ATR band + 3-candle time filter | 52w_high_breakout_pullback_long + 52w_low_breakdown_pullback_short |
| **B591** | donchian_10_breakout LOCAL signals (dc10_breakout_up_1pct + dc10_strong_breakout_up) | donchian_10_breakout |
| **B594/B596** | donchian_breakout_retest_long + donchian_breakdown_retest_short LOCAL strong variants | dc20_resistance_break_retest_strong + symmetric short |
| **B598** | above_avwap_20low / below_avwap_20high producer (B598/B612 symmetric pair) | volume_spike_breakout + r1_break_retest |
| **B605** | 52wh_break_retest + 52wl_break_retest_short producers (NEW Class 7 inverse) | 52wh_break_retest + 52wl_break_retest_short |
| **B608** | break_retest_volume obv_bullish refactor (B617) | break_retest_volume |
| **B612 F2** | below_avwap_20high silent-gap fix (positive symmetric pair) | volume_spike_breakout SHORT + retest SHORT + r1_break_retest SHORT |
| **B626** | force_index_breakout: F1 silent-gap fix + (a) bullish-bar gate + F2 docstring | force_index_breakout |
| **B630** | below_ema_200 producer-additive sweep across screener.py | ALL breakout strategies with `below_ema_200` |
| **B663** | Pattern A default-True → False WAVE 1 family sweep | ALL breakout strategies with `price_above_ema_200` |

**Net effect:** Pattern A is essentially CLEAN across the breakout cluster post-B663. Pattern N (intra-cluster collinearity) is the cluster's dominant concern.

### 3. CC1 next-open-after-gap haircut — applies BUT in continuation direction not mean-reversion

Breakout strategies have a structural gap-after-detection feature: when a breakout fires (e.g., 52w_high_breakout), price often gaps up ON the breakout bar — the engine detects at close and enters next-open after another potential gap up. Unlike B673 CC1 (M&A target: gap UP then mean-reversion DOWN — engine buys at the wrong time), breakout entry IS in the same direction as the continuation pattern. So next-open IS at a higher price than detection close BUT in the trade's favor — the engine "pays the gap" but the trade benefits if continuation persists.

**Net:** CC1 partially applies but is LESS damaging than the M&A target case. The capturable-after-gap haircut is smaller (the gap is part of the move, not against it).

### 4. Cluster's dominant concern: intra-family redundancy (Pattern N)

19 strategies on a small primitive set:

| Primitive | Strategies |
|---|---|
| `break_52w_high` / `break_52w_low` (B582 producer) | 52w_high_breakout + 52w_low_breakdown + (cross-cluster with 52w_high_breakout_with_smart_money_long via smart_money_sleeve walked B613) |
| `near_52w_high_retest_long` / `near_52w_low_retest_short` (B590 producer) | 52w_high_breakout_pullback_long + 52w_low_breakdown_pullback_short |
| `year_high_break_retest_long` / `year_low_break_retest_short` (B605 producer) | 52wh_break_retest + 52wl_break_retest_short |
| `resistance_break_retest` / `support_break_retest` (B-anchored on DC20) | break_retest_volume + dc20_break_retest |
| `dc10_breakout_up` / `_dn` (B584 producer) | donchian_breakout_long + donchian_breakdown_short |
| `dc10_breakout_up_1pct` / LOCAL `dc10_strong_breakout_up` (B591) | donchian_10_breakout |
| `dc20_resistance_break_retest_strong` / `_support_*` LOCAL (B594/596) | donchian_breakout_retest_long + donchian_breakdown_retest_short |
| `force_index_cross_up` / `_dn` (Elder methodology producer) | force_index_breakout |
| `squeeze_on_release` (TTM Squeeze) | squeeze_breakout (+ squeeze_breakout_with_smart_money_long walked SM-36) |
| `inside_bar` + ADX | inside_bar_breakout |
| `vol_spike_15x` + `dc10_breakout_up` | volume_spike_breakout + volume_spike_breakout_retest |
| `below_prev_low` | prev_day_low_breakdown |

**13 distinct primitives across 19 strategies** ⇒ effective hypothesis count ≈ 13, not 19. **2 sub-families have heavy overlap:** 52w-family (4 strategies) + Donchian-family (6 strategies). Pattern N intra-cluster ablation is the cluster's flagship cube test.

### 5. CHECKLIST (r) timeframe-mismatch concern — partial applicability

Several breakout strategies combine **daily-bar signals** (52w/Donchian/inside_bar EVENT triggers) with **higher-timeframe trend gates** (EMA-200 = ~10 months of data; sector_outperforming_spy = 20 days). CHECKLIST (r) timeframe-mismatch concern applies but ALL strategies use the gates AS confluence (not contradiction), so the mismatch is mild.

---

## Reviewer findings response matrix

> Pre-emptive matrix awaiting external reviewer pass on this doc.

| # | Finding | Severity | Status | Action |
|---|---|---|---|---|
| _F-pending_ | Awaiting external reviewer | — | OPEN | Will tabulate post-review |

---

## Cluster scope inventory

**19 strategies in `breakout` category.** Sub-cluster grouping:

| Sub-cluster | # strategies | Strategies |
|---|---|---|
| **A — 52-week breakout family (4)** | 4 | BR-1 `strat_52w_high_breakout` / BR-2 `strat_52w_high_breakout_pullback_long` / BR-3 `strat_52w_low_breakdown` / BR-4 `strat_52w_low_breakdown_pullback_short` |
| **B — 52w break-retest family (2)** | 2 | BR-5 `strat_52wh_break_retest` / BR-6 `strat_52wl_break_retest_short` |
| **C — Generic break-retest family (2)** | 2 | BR-7 `strat_break_retest_volume` (dual) / BR-8 `strat_dc20_break_retest` (dual) |
| **D — Donchian family (5)** | 5 | BR-9 `strat_donchian_10_breakout` (dual) / BR-10 `strat_donchian_breakout_long` / BR-11 `strat_donchian_breakdown_short` / BR-12 `strat_donchian_breakout_retest_long` / BR-13 `strat_donchian_breakdown_retest_short` |
| **E — Volume-spike breakout family (2)** | 2 | BR-14 `strat_volume_spike_breakout` / BR-15 `strat_volume_spike_breakout_retest` |
| **F — Misc breakout (4)** | 4 | BR-16 `strat_force_index_breakout` (dual) / BR-17 `strat_inside_bar_breakout` / BR-18 `strat_prev_day_low_breakdown` / BR-19 `strat_squeeze_breakout` |

**Cross-cluster overlap (walked in smart-money cluster):**
- `strat_52w_high_breakout_with_smart_money_long` (SM-34, B613-closed) — confluence wrap over BR-1
- `strat_52w_high_breakout_with_smart_money_vol_below_long` (SM-35, B613-closed) — B-twin
- `strat_squeeze_breakout_with_smart_money_long` (SM-36, Pattern E candidate) — confluence wrap over BR-19
- `strat_donchian_breakout_with_smart_money_long` (SM-39, Pattern E candidate) — confluence wrap over BR-10

---

## Cross-strategy patterns (breakout cluster)

### Pattern T (NEW for breakout): forensic-fix density — strategies are POST-FIX designs needing cube re-validation

**Affects:** all 19 (varying depth).

**Concern:** breakout cluster has the most B-batch forensic-fix evidence (see §2 methodology). The post-fix designs need cube re-validation — symmetric with B262/B278 forensic-fix re-validation tickets from SMC cluster. Pattern T parallels the smart-money cluster's "B262 + B278 fix re-validation" but at CLUSTER scope (12+ batches affected this cluster).

**Step 7 disposition:** every walk should note its post-fix lineage + flag whether cube re-validates the latest fix design.

### Pattern N (carried + EXTENDED): intra-family redundancy is acute

**Affects:** all 19. Specifically:
- 52w-family: 4 strategies (BR-1/2/3/4) on `break_52w_*` + `near_52w_*_retest_*`
- Donchian-family: 6 strategies (BR-9/10/11/12/13 + smart_money wrap SM-39) on DC10/DC20
- Break-retest family: 4 strategies (BR-5/6/7/8) on retest primitives at different anchors

**Within-cluster effective hypothesis count ≈ 13 (not 19);** cube replay marginal-contribution test required.

### Pattern U (NEW for breakout): 5-gate post-B589 family signature

**Affects:** 8 strategies (BR-1, BR-3, BR-5, BR-9, BR-10, BR-11, BR-12, BR-13).

**Concern:** post-B589 the breakout family standardized on a 5-gate signature: `breakout EVENT + vol_confirm + macd_confirm + close_above_open + close_in_top_40pct_of_range`. This is a CLEAN design pattern but creates Pattern N risk — 8 strategies share most of their gate structure.

**Step 7 disposition:** cube replay should explicitly compare the 5-gate variants pairwise to surface which differ economically vs cosmetically.

### Pattern V (NEW for breakout): Bulkowski 2005 retest absorption thesis — vol_below_avg gate

**Affects:** 6 strategies — BR-2, BR-4, BR-5, BR-6, BR-12, BR-13 (all retest strategies use `vol_below_avg` per Bulkowski thesis).

**Concern:** the Bulkowski "retest forms on lower volume than initial break" thesis is empirically published BUT cited generically. Cube replay against breakouts WITHOUT vol_below_avg confluence settles whether the retest variants earn registry slots.

### Pattern A (carried) — Pattern A ✅ verified clean post-B663 + B630

All 19 strategies use `price_above_ema_200` (default-False post-B663) or `below_ema_200` (B630 producer-additive). 0 silent-gap instances per grep.

### Pattern O (carried + EXTENDED for breakout)

Hardcoded tolerances:
- `vol_spike_17x` = 1.7x (B586 owner-pick from 1.5x-2x range)
- `vol_spike_15x` = 1.5x (Donchian + dc20_break_retest)
- `vol_above_avg` = 1.0x (donchian_10_breakout)
- `vol_below_avg` = <1.0x (Bulkowski retest family)
- ATR band coefficients: `0.5*ATR(14)` (B592 dc10_strong_breakout + B594 dc20_strong); `1.5*ATR(14)` (B605 52wh/52wl break_retest)
- `0.99` / `1.01` factors (B590 pullback retest "below peak / above trough" thresholds)
- `close_in_top_40pct_of_range` / `close_in_bottom_40pct_of_range` = 40% bar position
- `3pct` retest tolerance (B590 pullback variant)
- `breakout_3_candles_old` (B590 time filter)

**~10 hardcoded parameters** across the cluster; sensitivity-untested.

---

## Cluster current state table

| BR # | Function name | Direction | Sub-cluster | Key gates | Has EMA gate | Pattern flags | Walk status |
|---|---|---|---|---|---|---|---|
| BR-1 | `strat_52w_high_breakout` | long | A 52w | 5-gate post-B589 | ❌ (sector ETF substitute) | T + U + V | ⏳ Walked B676 |
| BR-2 | `strat_52w_high_breakout_pullback_long` | long | A 52w | B590 7-condition aggregated | ❌ | T + V (Bulkowski) | ⏳ Walked B676 |
| BR-3 | `strat_52w_low_breakdown` | short | A 52w | 5-gate post-B589 inverse | ❌ | T + U + B671 borrow-trap | ⏳ Walked B676 |
| BR-4 | `strat_52w_low_breakdown_pullback_short` | short | A 52w | B590 inverse | ❌ | T + V + B671 borrow-trap | ⏳ Walked B676 |
| BR-5 | `strat_52wh_break_retest` | long | B 52w-retest | 7-gate B605 | ✅ | T + V (Bulkowski) + U | ⏳ Walked B676 |
| BR-6 | `strat_52wl_break_retest_short` | short | B 52w-retest | 7-gate B605 inverse | ✅ | T + V + U + B671 borrow-trap | ⏳ Walked B676 |
| BR-7 | `strat_break_retest_volume` | dual | C generic-retest | 4-gate dual B608 | ❌ (OBV substitute) | T + V + obv_bullish (B617 refactor) | ⏳ Walked B676 |
| BR-8 | `strat_dc20_break_retest` | dual | C generic-retest | 3-gate dual | ❌ (ADX substitute) | T + Pattern N (DC20 reskin of BR-7) | ⏳ Walked B676 |
| BR-9 | `strat_donchian_10_breakout` | dual | D Donchian | 6-gate dual B591 LOCAL strong | ❌ | T + U + ATR-band | ⏳ Walked B676 |
| BR-10 | `strat_donchian_breakout_long` | long | D Donchian | 5-gate post-B589 | ❌ (MACD substitute) | T + U + Pattern N | ⏳ Walked B676 |
| BR-11 | `strat_donchian_breakdown_short` | short | D Donchian | 5-gate B595 inverse | ❌ | T + U + B671 borrow-trap | ⏳ Walked B676 |
| BR-12 | `strat_donchian_breakout_retest_long` | long | D Donchian | 5-gate B596 strong | ❌ | T + V + U | ⏳ Walked B676 |
| BR-13 | `strat_donchian_breakdown_retest_short` | short | D Donchian | 5-gate B596 strong inverse | ❌ | T + V + U + B671 borrow-trap | ⏳ Walked B676 |
| BR-14 | `strat_volume_spike_breakout` | dual | E vol-spike | Multi-gate AVWAP family | ✅ EMA + AVWAP | T + Pattern N (DC10 reskin) | ⏳ Walked B676 |
| BR-15 | `strat_volume_spike_breakout_retest` | dual | E vol-spike | Multi-gate B596 retest variant | ✅ | T + Pattern N + V | ⏳ Walked B676 |
| BR-16 | `strat_force_index_breakout` | dual | F misc | 3-gate B626 (Elder 1993) | EMA-20 | T + B626 forensic-fix | ⏳ Walked B676 |
| BR-17 | `strat_inside_bar_breakout` | long | F misc | 3-gate (inside_bar + ADX + VWAP) | ❌ (VWAP substitute) | Pattern Q + B621 FAIL_FIRE projected | ⏳ Walked B676 |
| BR-18 | `strat_prev_day_low_breakdown` | short | F misc | TBD-gate (below_prev_low family) | ❌ | T + B671 borrow-trap | ⏳ Walked B676 |
| BR-19 | `strat_squeeze_breakout` | dual | F misc | 2-gate (squeeze_on_release + bar) | ❌ (close_above/below_open) | Pattern Q (Carter 2008) + Pattern N (cross-cluster SM-36) | ⏳ Walked B676 |

**Net cluster state:**
- 19 functions / 28 (strategy × direction) cells (9 dual via `_strat3`)
- 3 with EMA gate; 16 without (substituted by sector ETF / OBV / ADX / MACD / VWAP / TTM-squeeze)
- Pattern A ✅ verified clean across cluster
- Pattern N is the dominant concern (13 effective primitives over 19 strategies)
- 6 strategies use Bulkowski 2005 retest absorption thesis (Pattern V)
- 8 strategies in 5-gate post-B589 family (Pattern U)
- 7 SHORT strategies subject to B671 centralized borrow-trap gate (BR-3, BR-4, BR-6, BR-11, BR-13, BR-15 SHORT branch, BR-16 SHORT branch, BR-18, BR-19 SHORT branch)

---

## Per-strategy walks

### BR-1. `strat_52w_high_breakout` (Batch 586+589, 52w family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 5-gate LONG; **George-Hwang 2004 JF momentum anchor — best-anchored breakout strategy.** Cluster-wide canonical 5-gate post-B589 design template.

#### Step 1 — Read the code

[screener.py:1615-1636](backtest/signals/screener.py#L1615-L1636):

```python
def strat_52w_high_breakout(s):
    fires = (s.get("break_52w_high")
             and s.get("vol_spike_17x")
             and s.get("sector_outperforming_spy")
             and s.get("close_above_open")
             and s.get("close_in_top_40pct_of_range"))
```

**5-gate LONG.** Canonical 5-gate post-B589 family signature.

| Gate | Meaning |
|---|---|
| `break_52w_high` | EVENT (B582 producer): today's close > prior 252-day max-HIGH (excludes today) |
| `vol_spike_17x` | EVENT: today's volume > 1.7x trailing 20-bar mean (B586 owner-picked) |
| `sector_outperforming_spy` | STATE (B586): sector SPDR ETF 20-day return > SPY 20-day return |
| `close_above_open` | EVENT: bullish bar |
| `close_in_top_40pct_of_range` | EVENT (B589): close in top 40% of today's H-L range |

#### Step 2 — Classify

- Category: `breakout`; LONG; B291 default; last touched B589

#### Step 3 — Producer source-read + temporality

- `break_52w_high`: B582 producer fix — true when today's close > max(HIGH, 252-day window ending YESTERDAY)
- `vol_spike_17x`: bar-of-fire EVENT — `volume[-1] / volume[-21:-1].mean() > 1.7`
- `sector_outperforming_spy`: STATE — sector ETF 20d / SPY 20d
- `close_above_open` + `close_in_top_40pct_of_range`: bar-of-fire EVENTs from candle structure
- EVENT/STATE: 4 EVENT + 1 STATE

**EVENT-anchored structure with quality close-strength gate.** Best-in-class temporality.

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "George-Hwang 2004 JF - new highs attract buyers" | ✅ **REAL CITATION** — George + Hwang 2004 Journal of Finance "The 52-Week High and Momentum Investing" documents the anomaly. Anchor citation is legitimate peer-reviewed top-tier finance |
| "Volume >1.7x confirms institutional conviction" | ⚠ **Pattern O** — 1.7x is owner-pick from 1.5x-2x range; not empirically calibrated against actual volume distributions |
| "Sector ETF outperforming SPY 20d - trade strong sectors only" | ✅ Defensible at the relative-strength level |
| "Bullish bar with close in top 40% of range - strong-close signal (B589 added)" | ✅ B589 addition is a forensic-fix improvement; close-strength gate is canonical price-action discipline |
| Implicit "5-gate filter produces high-quality breakouts" | ⚠ **CC1 partial** — 52w breakouts gap (price keeps going); engine enters next-open at higher price than detection close. Capturable continuation > capturable headline but the gap is the entry cost |

#### Step 5 — OPEN_INVESTIGATIONS grep

- Pattern N cross-cluster with SM-34 `strat_52w_high_breakout_with_smart_money_long` (B613-closed Pattern E) + SM-35 B-twin
- B582 + B586 + B589 forensic-fix lineage (Pattern T)
- Pattern O `vol_spike_17x` calibration unverified

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — BR-3 `strat_52w_low_breakdown`
- Economic symmetry: ⚠ **Equity upward drift bias** — 52w-high breakouts more common than 52w-low breakdowns in upward-drift equity. SHORT side has lower fire count + carries B671 borrow-trap

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-cluster-anchor citation ✅** | George-Hwang 2004 JF is REAL anchor; cluster-positive | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-pattern-N cross-cluster** | SM-34 + SM-35 confluence wraps walked B613; SM-39 donchian wrap; cube ablation should surface confluence-wrap marginal contribution | MEDIUM | Pattern N |
| **F-pattern-U canonical 5-gate template** | Standard breakout family signature; ablation against 4-gate / 3-gate baselines | MEDIUM | Pattern U |
| **F-pattern-T forensic-fix lineage** | B582 + B586 + B589 (3 fixes); post-fix design needs cube re-validation | MEDIUM | Pattern T |
| **F-CC1 partial gap-after-detection** | Continuation breakout gaps in trade direction; engine entry pays the gap | LOW-MEDIUM | CC1 |
| **F-pattern-O vol_spike_17x calibration** | Owner-pick threshold; cube sensitivity sweep (1.5x / 1.7x / 2.0x) | LOW | Pattern O |
| F-fire-count | 5-gate AND restrictive; projected ~40-100/yr universe-wide; PASS likely | INFO | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo (best-anchored breakout strategy; minimal changes warranted) |
| (b) Cube ablation marginal-contribution test for sector_outperforming_spy gate (the most-recently-added gate) |
| (c) Cube sensitivity sweep `vol_spike_17x` threshold |
| (d) Cross-cluster Pattern N ablation with SM-34 + SM-35 + SM-39 |
| **(e) RECOMMENDED — (a) + (d). BR-1 is the cluster's flagship strategy; cross-cluster ablation against confluence wraps is the highest-leverage test. Pre-cube no code change.** |

**My recommendation: (e).**

**Awaiting owner direction on BR-1:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (e)
2. Pattern N flagship cross-cluster ablation scope confirmation
3. Pattern O vol_spike_17x sensitivity sweep priority

---

### BR-2. `strat_52w_high_breakout_pullback_long` (Batch 586+590, 52w family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 1-gate LONG (single-boolean consumer) but the producer encodes 7 conditions; B590 redesign anchor.

#### Step 1 — Read the code

[screener.py:1639-1655](backtest/signals/screener.py#L1639-L1655):

```python
def strat_52w_high_breakout_pullback_long(s):
    fires = s.get("near_52w_high_retest_long", False)
```

**1-gate LONG (Pattern S shell over multi-condition producer flag).** The single signal `near_52w_high_retest_long` encodes B590-redesigned 7-condition aggregated logic.

#### Step 2 — Classify

- Category: `breakout`; LONG; last touched B590 (post-B587 redesign)

#### Step 3 — Producer source-read + temporality

`near_52w_high_retest_long` is a producer flag encoding 7 conditions per docstring:
- (a) breakout_occurred: max CLOSE in last 30 trading days > year_high_pre30
- (b) within_3pct_high: today's close within ±3% of year_high_pre30
- (c) today_below_peak: today's close < 30-day max close × 0.99
- (d) vol_below_avg (Bulkowski retest): today's volume / 20-bar avg < 1.0
- (e) close_above_open: bullish reversal bar
- (f) breakout_3_candles_old: time filter — at least 3 trading days elapsed since first breakout bar
- (g) within_atr_band_long: today's close ≥ year_high_pre30 − ATR(14)

EVENT/STATE: predominantly EVENT-shaped at bar of fire.

**Pattern S concern (single-gate shell):** the strategy is a 1-line consumer; B590's 7-condition AND logic is invisible at the call site. Same anti-pattern as ICT-5/6/11/12.

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Classical breakout pullback" | ✅ Defensible — breakout-pullback pattern is canonical price-action methodology |
| "Bulkowski 2005 retest absorption thesis (vol_below_avg)" | ✅ Real citation; well-anchored |
| "Higher conviction than chase-the-breakout" | ⚠ Empirical claim without B-batch validation; cube settles |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B590 forensic-redesign (Pattern T)
- Pattern S single-gate shell

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — BR-4 `strat_52w_low_breakdown_pullback_short`

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-S single-gate shell** | 1-line consumer over 7-condition producer; B590 logic invisible at call site | MEDIUM | Pattern S |
| **F-pattern-V Bulkowski anchor** | Citation legitimate ✅ | INFO / ✅ POSITIVE | Pattern V |
| **F-pattern-T B590 redesign re-validation** | Post-fix design needs cube validation | MEDIUM | Pattern T |
| F-fire-count | 7-condition AND restrictive; projected ~20-50/yr universe-wide; borderline | MEDIUM | F4 |

**Options:** (a) status quo / (b) cube validates B590 redesign / (c) Pattern S explicit-gate refactor (expose conditions at strategy level) / **(d) RECOMMENDED — (b) post-B660 cube replay validates B590 design.**

**My recommendation: (d).**

**Awaiting owner direction on BR-2:**
1. (a)/(b)/(c)/(d) — recommendation (d)

---

### BR-3. `strat_52w_low_breakdown` (Batch 586+587+589, 52w family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 5-gate SHORT; symmetric inverse of BR-1.

#### Step 1 — Read the code

[screener.py:2378-2398](backtest/signals/screener.py#L2378-L2398):

```python
fires = (s.get("break_52w_low") and s.get("vol_spike_17x")
         and s.get("sector_underperforming_spy")
         and s.get("close_below_open") and s.get("close_in_bottom_40pct_of_range"))
```

**5-gate SHORT.** Symmetric mirror of BR-1.

#### Step 2-7 (compact — symmetric with BR-1)

- Category `breakout`; SHORT; B291 default; B589 family
- George-Hwang 2004 JF momentum applies inverse-symmetrically (52w-low names continue lower in literature)
- **B671 DTC>8 borrow-trap gate applies**
- Fire-count: 52w-low breakdowns less common than 52w-high breakouts in upward-drift equity; projected ~25-70/yr universe-wide
- Same Pattern T + U + Pattern N concerns

**Options:** same as BR-1; bundled. **My recommendation: (e) bundled with BR-1.**

**Awaiting owner direction on BR-3:** bundled with BR-1.

---

### BR-4. `strat_52w_low_breakdown_pullback_short` (Batch 586+590, 52w family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 1-gate SHORT; symmetric mirror of BR-2.

[screener.py:1658-1669](backtest/signals/screener.py#L1658-L1669) — symmetric. `near_52w_low_retest_short` producer flag encodes B590-mirror 7-condition logic. **B671 borrow-trap.** Fire-count ~10-30/yr universe-wide.

**Options:** same as BR-2; bundled. **My recommendation: (d) bundled.**

**Awaiting owner direction on BR-4:** bundled with BR-2.

---

### BR-5. `strat_52wh_break_retest` (Batch 605, 52w-retest family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **7-gate LONG**; B605 NEW (52w-anchored, NOT DC20-anchored — fixes prior bug in resistance_break_retest). Has EMA gate ✅ (most-gated breakout strategy in cluster).

#### Step 1 — Read the code

[screener.py:2543-2596](backtest/signals/screener.py#L2543-L2596):

```python
fl = (s.get("year_high_break_retest_long")
      and s.get("near_52w_high")
      and s.get("price_above_ema_200")
      and s.get("close_above_open")
      and s.get("close_in_top_40pct_of_range")
      and s.get("vol_below_avg")
      and s.get("above_avwap_20low"))
```

**7-gate LONG.** Most-gated breakout strategy + AVWAP confluence + B605 NEW retest anchor.

| Gate | Meaning |
|---|---|
| `year_high_break_retest_long` | EVENT (B605 producer): some bar 2-8 ago closed > year_high; subsequent bar's LOW touched within 1.5×ATR; today's close >= year_high |
| `near_52w_high` | STATE: today's close >= 98% of 252-day max high |
| `price_above_ema_200` | STATE: long-term uptrend |
| `close_above_open` | EVENT: bullish bar |
| `close_in_top_40pct_of_range` | EVENT (B589): strong close |
| `vol_below_avg` | EVENT (Bulkowski retest): volume / 20-bar avg < 1.0 |
| `above_avwap_20low` | STATE: close > AVWAP anchored at trailing 20-bar low |

#### Step 2 — Classify

- Category: `breakout`; LONG; B291 default; last touched B612 (B598 producer adds above_avwap_20low)

#### Step 3 — Producer source-read + temporality

- `year_high_break_retest_long`: B605 NEW producer (replaces buggy DC20-anchored `resistance_break_retest` per B605 F1 bug-fix walk)
- All other gates verified
- EVENT/STATE: 4 EVENT + 3 STATE

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "(B605 NEW; 52w-anchored, NOT DC20-anchored)" | ✅ Forensic-fix from B605 walk — B605 identified resistance_break_retest as DC20-anchored bug; created year_high_break_retest_long as correct 52w-anchored replacement |
| "Bulkowski 2005 retest absorption thesis (vol_below_avg)" | ✅ Real anchor |
| "AVWAP confluence (B598/B612 symmetric pair)" | ✅ B612 F2 forensic-fix established symmetric pair |
| "near_52w_high" + "year_high_break_retest" co-occurrence | ⚠ Possibly redundant — `year_high_break_retest_long` already implies "near year_high" structurally; the `near_52w_high` gate at 98% may be near-tautological |

#### Step 5 — OPEN_INVESTIGATIONS grep

- Pattern T: B605 forensic-fix + B612 F2 silent-gap fix lineage
- Pattern N: 7-gate AND with possible internal redundancy (near_52w_high + year_high_break_retest_long)

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — BR-6 `strat_52wl_break_retest_short`

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-T B605 forensic-fix** | Replaces buggy DC20-anchored predecessor; needs cube validation | MEDIUM | Pattern T |
| **F-internal-redundancy** | near_52w_high + year_high_break_retest_long are likely correlated; gate marginal contribution unknown | MEDIUM | Pattern N |
| **F-pattern-V Bulkowski + AVWAP confluence** | Multiple legitimate anchors | INFO / ✅ POSITIVE | Pattern V |
| F-fire-count | 7-gate AND very restrictive; projected ~15-40/yr universe-wide; borderline FAIL min_trades=30 per regime | MEDIUM | F4 |

**Options:** (a) status quo / (b) drop near_52w_high gate (redundant with year_high_break_retest_long) / (c) cube ablation for near_52w_high marginal contribution / **(d) RECOMMENDED — (c) post-B660 cube settles redundancy.**

**My recommendation: (d).**

**Awaiting owner direction on BR-5:**
1. (a)/(b)/(c)/(d) — recommendation (d)
2. Pattern N internal-redundancy ablation scope

---

### BR-6. `strat_52wl_break_retest_short` (Batch 605, 52w-retest family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 7-gate SHORT; symmetric mirror of BR-5.

[screener.py:2598-2640](backtest/signals/screener.py#L2598-L2640) — symmetric with `year_low_break_retest_short` + `near_52w_low` + `below_ema_200` + `close_below_open` + `close_in_bottom_40pct_of_range` + `vol_below_avg` + `below_avwap_20high`. **B612 F2 silent-gap fix anchors B-twin.** **B671 borrow-trap gate applies.** Fire-count rarer than BR-5 (~10-25/yr).

**Options:** same as BR-5; bundled. **My recommendation: (d) bundled.**

**Awaiting owner direction on BR-6:** bundled with BR-5.

---

### BR-7. `strat_break_retest_volume` (Batch 608+617, generic-retest family, walked B676 — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 4-gate dual; B617 obv_bullish refactor (switched from obv_rising for symmetric OBV).

#### Step 1 — Read the code

[screener.py:2642-...](backtest/signals/screener.py#L2642):

```python
fl = (s.get("resistance_break_retest") and s.get("obv_bullish")    # B617
      and s.get("close_above_open") and s.get("vol_below_avg"))
fs = (s.get("support_break_retest") and s.get("obv_bearish")
      and s.get("close_below_open") and s.get("vol_below_avg"))
```

**4-gate dual.** Combines DC20-anchored retest primitive + OBV-direction + bullish/bearish bar + Bulkowski vol_below_avg.

#### Step 2 — Classify

- Category: `breakout`; dual; B291 default; last touched B617 (OBV refactor)

#### Step 3 — Producer source-read + temporality

- `resistance_break_retest` / `support_break_retest`: DC20-anchored multi-bar pattern (B608)
- `obv_bullish` / `obv_bearish`: STATE OBV direction (B617 positive symmetric)
- `close_above/below_open`: bar-of-fire EVENT
- `vol_below_avg`: EVENT
- EVENT/STATE: 3 EVENT + 1 STATE per direction

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "BUG-111 multi-bar pattern (DC20)" | ✅ B608 was Stage 4 walk that fixed this pattern |
| "Bulkowski 2005 retest absorption thesis" | ✅ Real |
| "B617: switched from obv_rising to obv_bullish for symmetric" | ✅ Forensic-fix; B617 refactor |

#### Step 5 — OPEN_INVESTIGATIONS grep

- Pattern T: B608 + B617 forensic lineage
- Pattern N: cross-strategy with BR-8 `strat_dc20_break_retest` (both consume resistance/support_break_retest)

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Already dual
- **B671 borrow-trap applies SHORT side**

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-N BR-7 vs BR-8 reskin** | Both consume DC20 retest primitive; BR-7 adds OBV+vol+bar; BR-8 adds vol_spike_15x+ADX. Different gate stacks but same underlying signal | MEDIUM-HIGH | Pattern N |
| **F-pattern-T B608+B617 forensic** | Post-fix design needs cube validation | MEDIUM | Pattern T |
| F-pattern-V | Bulkowski legitimate | INFO / ✅ | Pattern V |
| F-fire-count | 4-gate AND projected ~25-60/yr per direction; modest PASS likely | INFO | F4 |

**Options:** (a) status quo / (b) cube BR-7 vs BR-8 ablation / **(c) RECOMMENDED — (b) post-B660 flagship Pattern N intra-cluster test.**

**My recommendation: (c).**

**Awaiting owner direction on BR-7:**
1. (a)/(b)/(c) — recommendation (c)
2. BR-7 vs BR-8 cube ablation as Pattern N flagship

---

### BR-8. `strat_dc20_break_retest` (generic-retest family, walked B676 — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate dual; consumes same DC20 retest primitive as BR-7 but with different confluence gates.

#### Step 1 — Read the code

[screener.py:2449-...](backtest/signals/screener.py#L2449):

```python
fl = (s.get("resistance_break_retest") and s.get("vol_spike_15x") and s.get("adx_trending"))
fs = (s.get("support_break_retest") and s.get("vol_spike_15x") and s.get("adx_trending"))
```

**3-gate dual.** DC20 retest + vol_spike + ADX (no Bulkowski vol_below_avg; uses ADX trend filter instead).

#### Step 2-7 (compact — Pattern N reskin of BR-7)

- Category `breakout`; dual; B291 default; **N.B.: BR-8's `vol_spike_15x` gate CONTRADICTS Bulkowski thesis — Bulkowski says retest should be LOWER volume, but BR-8 requires HIGHER volume**. Possible thesis-bug — retest with vol spike may be the initial breakout bar, not the retest
- `adx_trending` is a trend-strength gate
- Pattern N with BR-7 (same DC20 retest primitive)
- **B671 borrow-trap SHORT side**
- Fire-count: vol_spike_15x is restrictive; projected ~20-50/yr per direction

**F-thesis-bug:** `vol_spike_15x` on a "retest" pattern contradicts Bulkowski 2005 retest-on-lower-volume thesis. Either (a) BR-8 was designed for a different concept (continuation-on-high-volume, not Bulkowski retest) but named ambiguously, or (b) the vol gate is wrong.

**Options:** (a) status quo / (b) cube BR-7 vs BR-8 ablation / (c) thesis-bug clarification — rename BR-8 OR swap vol_spike → vol_below_avg / **(d) RECOMMENDED — (b) + (c). Cube settles; thesis-clarification batch should explicitly state whether BR-8 is "retest" or "continuation."**

**My recommendation: (d).**

**Awaiting owner direction on BR-8:**
1. Recommendation (d)
2. Thesis-bug clarification — vol_spike on retest is contradictory naming

---

### BR-9. `strat_donchian_10_breakout` (Batch 591+592, Donchian family, walked B676 — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **6-gate dual**; B591 LOCAL strong-breakout variant; ATR-band filter (B592).

#### Step 1 — Read the code

[screener.py:1744-...](backtest/signals/screener.py#L1744):

```python
fl = (s.get("dc10_breakout_up_1pct") and s.get("vol_above_avg")
      and s.get("macd_12_26_9_bullish") and s.get("close_above_open")
      and s.get("close_in_top_40pct_of_range") and s.get("dc10_strong_breakout_up"))
```

**6-gate dual.** B591 LOCAL signals (`dc10_breakout_up_1pct` 1% slack + `dc10_strong_breakout_up` ATR-band).

#### Step 2-7 (compact)

- Category `breakout`; dual; B291 default; B591/B592 forensic
- Pattern T: B591 + B592 redesigned this strategy from scratch (B591 added 1pct slack + strong-breakout LOCAL; B592 closed ATR-band)
- Pattern U: post-B589 5-gate family + 1 LOCAL strong gate = 6 gates
- Pattern N: cross-strategy with BR-10 (donchian_breakout_long) and BR-12 (donchian_breakout_retest_long)
- **B671 borrow-trap SHORT**
- Fire-count: 6-gate AND very restrictive; projected ~15-40/yr per direction; borderline

**Options:** (a) status quo / (b) cube Pattern T re-validation + cube Pattern N intra-Donchian ablation (BR-9 vs BR-10 vs BR-12) / **(c) RECOMMENDED — (b) flagship Donchian-family ablation.**

**My recommendation: (c).**

**Awaiting owner direction on BR-9:**
1. (a)/(b)/(c) — recommendation (c)
2. Donchian-family flagship Pattern N ablation (6 Donchian strategies; effective hypothesis count ≈ 3)

---

### BR-10. `strat_donchian_breakout_long` (Batch 595, Donchian family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 5-gate LONG; canonical post-B589 Donchian breakout.

#### Step 1 — Read the code

[screener.py:2314-...](backtest/signals/screener.py#L2314):

```python
fires = (s.get("dc10_breakout_up") and s.get("vol_spike_15x")
         and s.get("macd_12_26_9_bullish") and s.get("close_above_open")
         and s.get("close_in_top_40pct_of_range"))
```

**5-gate LONG.** Post-B589 family; Donchian-10 breakout (0.2% slack per B584) + vol_spike + MACD + bullish-bar + close-strength.

#### Step 2-7 (compact)

- Category `breakout`; LONG; last touched B595
- Pattern U canonical 5-gate post-B589
- Pattern N: BR-10 vs BR-9 (different DC10 slack: 0.2% vs 1%; BR-10 weaker breakout requirement)
- **Faith 2007 Turtle Trading** classical anchor
- Fire-count: 5-gate moderately restrictive; projected ~30-80/yr universe-wide; PASS likely

**Options:** (a) status quo / (b) cube Pattern N flagship Donchian-family ablation (5+ strategies; effective N ≈ 3). **My recommendation: (b).**

**Awaiting owner direction on BR-10:** bundled with BR-9 in Donchian-family flagship.

---

### BR-11. `strat_donchian_breakdown_short` (Batch 595, Donchian family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 5-gate SHORT; symmetric mirror of BR-10.

[screener.py:2281-...](backtest/signals/screener.py#L2281) — symmetric. `dc10_breakout_dn` + `vol_spike_15x` + `macd_bearish` + `close_below_open` + `close_in_bottom_40pct_of_range`. **B671 borrow-trap.** Fire-count ~15-50/yr (rarer than BR-10).

**Options:** bundled with BR-10. **My recommendation: (b) bundled.**

**Awaiting owner direction on BR-11:** bundled.

---

### BR-12. `strat_donchian_breakout_retest_long` (Batch 596, Donchian family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 5-gate LONG; B596 LOCAL strong variant; Bulkowski retest.

[screener.py:2343-...](backtest/signals/screener.py#L2343):

```python
fires = (s.get("dc20_resistance_break_retest_strong") and s.get("vol_below_avg")
         and s.get("macd_12_26_9_bullish") and s.get("close_above_open")
         and s.get("close_in_top_40pct_of_range"))
```

**5-gate LONG.** B594 LOCAL `dc20_resistance_break_retest_strong` (0.5×ATR strong filter beyond resistance_break_retest); Bulkowski vol_below_avg; MACD; bullish-bar; close-strength.

#### Step 2-7 (compact)

- Pattern T: B594 + B596 forensic LOCAL strong variant
- Pattern V Bulkowski thesis (legitimate citation)
- Pattern N: BR-12 vs BR-7 (different anchor — BR-12 uses DC20-strong; BR-7 uses generic DC20)
- Pattern U canonical 5-gate
- Fire-count: 5-gate restrictive; projected ~15-40/yr; borderline

**Options:** bundled with Donchian-family + retest-family Pattern N flagship. **My recommendation: cube ablation.**

**Awaiting owner direction on BR-12:** bundled.

---

### BR-13. `strat_donchian_breakdown_retest_short` (Batch 596, Donchian family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 5-gate SHORT; symmetric mirror of BR-12.

[screener.py:1811-...](backtest/signals/screener.py#L1811) — symmetric with B594 LOCAL strong + Bulkowski. **B671 borrow-trap.** Fire-count ~10-30/yr.

**Options:** bundled. **My recommendation:** bundled with Donchian-family flagship.

**Awaiting owner direction on BR-13:** bundled.

---

### BR-14. `strat_volume_spike_breakout` (E vol-spike family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Multi-gate dual; AVWAP-confluence + Donchian variant.

[screener.py:1562-...](backtest/signals/screener.py#L1562) — combines `dc10_breakout_up/dn` + `vol_spike_15x` + AVWAP gates (B598 + B612 F2 producer-additive fix for SHORT side silent-gap).

#### Step 2-7 (compact)

- Pattern T: B598 + B612 F2 forensic-fix lineage
- Pattern N: cross-strategy with BR-10 (donchian_breakout_long; same dc10 primitive) — likely high correlation
- **B671 borrow-trap SHORT**
- Pattern Q FAIL_FIRE_STARVED flagged in B621 audit (~0.07/yr universe-wide projected estimator)
- Fire-count: B621 estimator says HIGH RISK FAIL; cube empirical confirms or refutes

**Options:** (a) status quo / (b) cube validates B621 estimator; if confirmed <30/yr → EXPLORATORY marker / (c) Pattern N cube ablation BR-14 vs BR-10.

**My recommendation: (b) + (c) bundled. EXPLORATORY marker candidate if B621 estimator confirmed.**

**Awaiting owner direction on BR-14:**
1. Pattern G EXPLORATORY disposition pending B660 measurement
2. Pattern N ablation against BR-10

---

### BR-15. `strat_volume_spike_breakout_retest` (E vol-spike family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Multi-gate dual; retest variant of BR-14.

[screener.py:1845-...](backtest/signals/screener.py#L1845) — retest variant. **B621 estimator: 0.01/yr universe-wide projected (HIGHEST RISK FAIL_FIRE_STARVED in the entire roster).** Pattern G EXPLORATORY DEPLOYMENT-BLOCK candidate.

**Options:** (a) status quo / (b) **EXPLORATORY marker pre-cube per B621 estimator + W5m precedent / (c) DELETE candidate per B620 squeeze_setup_event_only_long precedent (FAIL_FIRE_STARVED → delete).** Per `project_no_apriori_strategy_pruning`: do NOT auto-delete; surface options.

**My recommendation:** Bundle Pattern G + post-B660 measurement; if cube confirms < 5/yr → owner-direction on (b) EXPLORATORY vs (c) DELETE per B620 precedent.

**Awaiting owner direction on BR-15:**
1. Pattern G EXPLORATORY vs DELETE decision (post-B660)
2. Cross-ref `S5-FIRE-COUNT-CANDIDATES` ticket (BR-15 is on the 5 REAL FAIL list)

---

### BR-16. `strat_force_index_breakout` (F misc family, walked B676 — DUAL, B626 forensic-fixed)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **B626 FORENSIC-FIXED CASE** — pre-B626 SHORT side used `not s.get("price_above_ema_20")` NOT-pattern silent-gap; B626 F1 swap + F2 docstring + (a) bullish/bearish bar gate.

#### Step 1 — Read the code

[screener.py:1683-...](backtest/signals/screener.py#L1683):

```python
fl = (s.get("force_index_cross_up") and s.get("price_above_ema_20")
      and s.get("close_above_open"))
fs = (s.get("force_index_cross_dn") and s.get("below_ema_20")  # B626 F1
      and s.get("close_below_open"))                            # B626 (a)
```

**3-gate dual post-B626.** Elder 1993 Force Index methodology + EMA-20 trend filter + bullish/bearish bar (B626 family standardization).

#### Step 2 — Classify

- Category: `breakout`; dual; last touched B626

#### Step 3 — Producer source-read + temporality

- `force_index_cross_up` / `_dn`: EVENT — Force Index zero-line cross (Elder methodology)
- `price_above_ema_20` / `below_ema_20`: STATE
- `close_above/below_open`: EVENT

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Elder 1993 *Trading for a Living* Force Index methodology" | ✅ **REAL CITATION** — Alexander Elder's published methodology |
| B626 F1 silent-gap fix | ✅ Forensic-fix |
| B626 (a) bullish/bearish bar family standardization | ✅ Pattern U family-template applied |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B626 fix lineage (Pattern T)
- Family-bug surfaced B626 walk: 2 other strategies (strat_awesome_oscillator + strat_stoch_oversold SHORT sides) use same NOT-pattern; queued

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Already dual + **B626 swap made SHORT side fail-safe** (positive symmetric)

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-T B626 forensic** | Post-fix design needs cube validation | MEDIUM | Pattern T |
| **F-elder-1993-anchor ✅** | Legitimate published methodology | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-cluster-family-bug carry** | `not s.get("price_above_ema_20")` family with 2 other strategies (deferred R5) | MEDIUM | family-bug |
| F-fire-count | force_index cross + EMA-20 alignment + bullish bar; projected ~30-80/yr per direction; PASS likely | INFO | F4 |

**Options:** (a) status quo (B626 post-fix design is sound) / (b) cube validates B626 fix / **(c) RECOMMENDED — (b) post-B660 + family-bug sweep on the 2 sibling strategies.**

**My recommendation: (c).**

**Awaiting owner direction on BR-16:**
1. (a)/(b)/(c) — recommendation (c)
2. Family-bug sweep scope (strat_awesome_oscillator + strat_stoch_oversold SHORT)

---

### BR-17. `strat_inside_bar_breakout` (F misc family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate LONG; **Pattern Q candidate** (no specific peer-reviewed citation for inside_bar; generic price-action methodology).

#### Step 1 — Read the code

[screener.py:1672-1680](backtest/signals/screener.py#L1672-L1680):

```python
fires = (s.get("inside_bar") and s.get("adx_trending") and s.get("above_vwap"))
```

**3-gate LONG.** inside_bar pattern + ADX trend strength + above-VWAP.

#### Step 2-7 (compact)

- Category `breakout`; LONG; B291 default
- **Pattern Q:** no specific peer-reviewed citation for inside_bar; generic price-action pattern
- No EMA-200 gate (VWAP substitute)
- Fire-count: inside_bar is common but ADX_trending + above_vwap narrows; projected ~50-150/yr; PASS likely

**Options:** (a) status quo / (b) cite a published methodology if available (e.g., Brian Shannon's *Maximum Trading Gains with Anchored VWAP* for VWAP); pure docstring honesty / **(c) RECOMMENDED — (a) + minor docstring polish to acknowledge Pattern Q.**

**My recommendation: (c).**

**Awaiting owner direction on BR-17:**
1. Pattern Q docstring caveat
2. Cube validation for status-quo design

---

### BR-18. `strat_prev_day_low_breakdown` (F misc family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. SHORT-side breakdown strategy.

[screener.py:2400-...](backtest/signals/screener.py#L2400) — uses `below_prev_low` primitive. **B671 borrow-trap.**

#### Step 2-7 (compact)

- Category `breakout`; SHORT
- Producer `below_prev_low` is a standard candle-pattern primitive from technical.py
- Pattern Q (no specific cite); generic price-action methodology
- Fire-count: below_prev_low is moderately common; PASS likely

**Options:** (a) status quo / (b) docstring caveat (Pattern Q) / cube validation.

**My recommendation: (a) + (b).**

**Awaiting owner direction on BR-18:** Pattern Q reframe.

---

### BR-19. `strat_squeeze_breakout` (F misc family, walked B676 — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate dual; TTM Squeeze (Carter 2008).

#### Step 1 — Read the code

[screener.py:1553-1561](backtest/signals/screener.py#L1553-L1561):

```python
# (compact; squeeze_on_release + close_above_open / close_below_open)
```

**2-gate dual.** TTM squeeze-release EVENT + bullish/bearish bar.

#### Step 2-7 (compact)

- Category `breakout`; dual; **Carter 2008 TTM Squeeze methodology** — Pattern Q WEAK (trader-book, not peer-reviewed but widely accepted)
- Pattern N cross-cluster with SM-36 `strat_squeeze_breakout_with_smart_money_long` (smart-money sleeve confluence wrap; walked B673)
- **B671 borrow-trap SHORT**
- Fire-count: squeeze-release rare; projected ~10-30/yr per direction; borderline

**Options:** (a) status quo / (b) cube ablation BR-19 vs SM-36 confluence wrap — settles whether smart-money sleeve adds marginal alpha / (c) Pattern Q docstring caveat. **My recommendation: (b) bundled with SM-36 disposition.**

**Awaiting owner direction on BR-19:**
1. Cube cross-cluster Pattern N ablation BR-19 vs SM-36
2. Pattern Q TTM-squeeze methodology citation level

---

## B676 cluster walk completion wrap-up

> All 19 breakout strategies now have full per-walk template coverage:

- **Sub-cluster A — 52w family (4):** BR-1 + BR-2 + BR-3 + BR-4 (George-Hwang 2004 JF + Bulkowski 2005 anchors)
- **Sub-cluster B — 52w break-retest (2):** BR-5 + BR-6 (B605 forensic-fix replaces DC20-anchored bug)
- **Sub-cluster C — Generic break-retest (2):** BR-7 + BR-8 (BR-8 thesis-bug — vol_spike on retest contradicts Bulkowski)
- **Sub-cluster D — Donchian family (5):** BR-9 + BR-10 + BR-11 + BR-12 + BR-13 (Faith 2007 Turtle anchor)
- **Sub-cluster E — Vol-spike (2):** BR-14 + BR-15 (BR-15 is the cluster's worst Pattern G fire-starve case per B621 0.01/yr estimator)
- **Sub-cluster F — Misc (4):** BR-16 (Elder 1993 + B626 forensic) + BR-17 (Pattern Q) + BR-18 (Pattern Q) + BR-19 (Carter 2008)

**Total fully-expanded: 19 of 19. CLUSTER WALK COMPLETE.**

### Bundled disposition recommendations summary

| Pattern | Strategies | Disposition |
|---|---|---|
| **A (default-True silent-gap)** | ✅ All 19 clean post-B663/B630 sweep | ✅ RESOLVED |
| **M (peer-review citation)** | LEGITIMATE for 15 of 19 (George-Hwang 2004 + Bulkowski 2005 + Elder 1993 + Faith 2007 + Lo-Wang 2000); Pattern Q applies to BR-17/18/19 (and weakly to BR-8 thesis bug) | DOCUMENTATION-ONLY; cluster-positive vs SMC/ICT |
| **N (intra/cross-cluster collinearity)** | 19 strategies on 13 primitives; effective N ≈ 13; Donchian-family 5 strategies on 3 effective + 52w-family 4 on 2 effective + retest-family 4 on 2 effective | Cube replay flagship Pattern N ablations: (1) Donchian-family BR-9/10/11/12/13; (2) 52w-family BR-1/2/3/4; (3) retest-family BR-7/8/12/13 |
| **T (forensic-fix density)** | 12+ batches with forensic fixes: B582/B584/B586/B587/B589/B590/B591/B592/B594/B595/B596/B598/B605/B608/B612/B617/B626/B663 — Pattern T re-validation candidates: BR-5/6 (B605 NEW retest anchor); BR-7 (B608+B617); BR-9 (B591+B592); BR-15 (B621 FAIL_FIRE); BR-16 (B626) | Cube re-validation of post-fix designs |
| **O (hardcoded tolerances)** | ~10 free parameters: vol_spike thresholds, ATR coefficients, retest tolerances, close-strength 40% | Config-parameterization for cube sweep |
| **V (Bulkowski retest absorption)** | 6 strategies (BR-2/4/5/6/12/13) — legitimate cited thesis | Cluster-positive |
| **U (5-gate post-B589 family)** | 8 strategies (BR-1/3/5/9/10/11/12/13) — canonical template | Pattern N ablation against 4-gate / 3-gate variants |
| **CC1 next-open gap (carried)** | All 19 (in continuation direction; LESS damaging than M&A target case) | Documentation-only haircut |
| **Pattern G low-fire-combo** | BR-15 (0.01/yr B621 estimator — WORST in roster); BR-2/4 (B590 7-condition restrictive); BR-9 (6-gate AND); BR-5/6 (7-gate AND); BR-14 (0.07/yr B621); BR-12/13 | Post-B660 EXPLORATORY marker decisions |
| **Pattern S single-gate shell** | BR-2 + BR-4 (B590 7-condition logic in producer flag); BR-17 + BR-19 (simple gate stack) | Documentation; consider explicit-gate refactor for BR-2/BR-4 |
| **BR-8 thesis-bug** | vol_spike on "retest" contradicts Bulkowski thesis | Owner decision: rename to "continuation" OR swap to vol_below_avg |
| **B671 SHORT borrow-trap** | 7 SHORT strategies subject (BR-3/4/6/11/13 + BR-7/16/19 SHORT branches + BR-15 SHORT + BR-18) | Already centralized B671 (pending revert per B673 reviewer architectural concern) |

### Queue tickets surfaced (recap)

NEW B676 tickets:

- `S4-BR-CLUSTER-PATTERN-N-FLAGSHIP-CUBE-ABLATIONS` — three sub-family ablations: Donchian (5 strategies), 52w-family (4 strategies), retest-family (4 strategies)
- `S4-BR8-VOL-SPIKE-VS-BULKOWSKI-THESIS-BUG-CLARIFICATION` — BR-8 `vol_spike_15x` on "retest" pattern contradicts Bulkowski thesis; rename or swap
- `S4-BR-PATTERN-O-CONFIG-PARAMETERIZATION` — ~10 hardcoded breakout parameters
- `S4-BR-PATTERN-T-FORENSIC-FIX-CUBE-REVALIDATION` — 12+ batches of forensic-fixes need cube re-validation
- `S4-BR-PATTERN-Q-INSIDE-BAR-CITATION-DOCSTRING-CAVEAT` — BR-17/18/19 + weak BR-8

EXISTING tickets cross-referenced:
- `S5-FIRE-COUNT-CANDIDATES` — BR-14 + BR-15 explicitly on the 5 REAL FAIL list
- `S5-RSI-DEFAULT-50-FAMILY` — N/A for breakout cluster
- `S5-MARGINAL-CONTRIBUTION-SCORING` — breakout cluster Pattern N is 4th-highest-leverage application (after smart-money 13F sleeve test, SMC, ICT)

---

## Cluster-wide methodology references

- **Producers:** [backtest/signals/technical.py](backtest/signals/technical.py) for break_52w_high/low, near_52w_high/low_retest, year_high/low_break_retest (B605), resistance/support_break_retest, dc10/dc20_breakout*, vol_spike_15x/17x, sector_outperforming/underperforming_spy, close_above/below_open, close_in_top/bottom_40pct_of_range, ATR(14), MACD, OBV, ADX, Force Index, inside_bar, near_pivot, AVWAP variants, squeeze_on_release; [backtest/signals/smc_ict.py](backtest/signals/smc_ict.py) NOT consumed by breakout cluster
- **Strategies:** [backtest/signals/screener.py](backtest/signals/screener.py) — 19 functions across lines 1553-2640
- **Citations:**
  - George + Hwang 2004 JF "The 52-Week High and Momentum Investing" — BR-1, BR-3
  - Bulkowski 2005 *Encyclopedia of Chart Patterns* retest absorption thesis — BR-2, BR-4, BR-5, BR-6, BR-12, BR-13
  - Faith 2007 *The Way of the Turtle* + Donchian 1960s — Donchian family BR-9 through BR-13
  - Elder 1993 *Trading for a Living* — BR-16
  - Carter 2008 TTM Squeeze — BR-19
  - Lo + Wang 2000 RFS volume-as-information — BR-14, BR-15 (volume-spike)
  - Akarim + Sevim 2013 — volume-price relationship (BR-14, BR-15)
- **Forensic-fix lineage (Pattern T):** B582 + B584 + B586 + B587 + B589 + B590 + B591 + B592 + B594 + B595 + B596 + B598 + B605 + B608 + B612 + B617 + B626 + B630 + B663

---

## B676 cluster walk status

| Item | Status |
|---|---|
| Doc infrastructure (header + adaptations + inventory + patterns + state table) | ✅ B676 |
| Per-strategy walks BR-1 through BR-19 (19 walks at full / compact-mirror template density) | ✅ B676 |
| External reviewer pass | ⏳ post-walk-completion |
| Cluster-wide post-walk findings synthesis | ⏳ post-reviewer |

**Cumulative B676: 19 of 19 walks fully expanded. CLUSTER WALK COMPLETE.**

### Cross-cluster status snapshot (post-B676)

| Cluster | Doc | Status | Strategy count |
|---|---|---|---|
| Pivot | [STAGE_4_PIVOT_CLUSTER_WALKS.md](STAGE_4_PIVOT_CLUSTER_WALKS.md) | ✅ Complete | ~10 |
| Trend | [STAGE_4_TREND_CLUSTER_WALKS.md](STAGE_4_TREND_CLUSTER_WALKS.md) | ✅ Complete | ~12 |
| Smart Money (data-source) | [STAGE_4_SMART_MONEY_CLUSTER_WALKS.md](STAGE_4_SMART_MONEY_CLUSTER_WALKS.md) | ✅ Complete + B674 reviewer-critique | 41 (post-B670: 39 + 2 Class 7 NEW in momentum_trend) |
| SMC (pure price-action) | [STAGE_4_SMC_CLUSTER_WALKS.md](STAGE_4_SMC_CLUSTER_WALKS.md) | ✅ Complete | 18 |
| ICT (pure price-action) | [STAGE_4_ICT_CLUSTER_WALKS.md](STAGE_4_ICT_CLUSTER_WALKS.md) | ✅ Complete | 12 |
| **Breakout** | **[STAGE_4_BREAKOUT_CLUSTER_WALKS.md](STAGE_4_BREAKOUT_CLUSTER_WALKS.md) (THIS DOC)** | **✅ Complete (B676)** | **19** |
| Event-driven | — | ⏳ Pending | ~10 |
| Chart pattern | — | ⏳ Pending (many individually walked B636/B639/B641) | ~9 |
| Candle | — | ⏳ Pending (individually walked) | ~5 |
| Classification change | — | Partially covered in smart-money sub-cluster D | ~10 |

**Total Stage 4 walks: 6 cluster docs complete; ~112 of ~222 strategies have per-cluster CHECKLIST #105 7-step walks.** Remaining clusters: event-driven (10) + chart_pattern (9) + candle (5) + classification (covered partially) = ~24 strategies pending cluster-walk coverage (excluding classification-change which is partially in smart-money sub-cluster D).
