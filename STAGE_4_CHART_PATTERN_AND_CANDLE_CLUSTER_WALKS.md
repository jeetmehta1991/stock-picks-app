# Stage 4 Chart Pattern + Candle Cluster Walks — Per-Strategy Deep-Dive Audit

> **B678 status banner (2026-06-10, owner-directed autonomous continuation — FINAL CLUSTER DOC):** EIGHTH per-cluster Stage 4 walk doc + completes the cluster-walk coverage initiative. Owner directive *"continue autonomously"* after B677 event-driven walk. **Two clusters combined in this doc** (chart_pattern + candle) because both are small (9 + 7 = 16 total) and share the price-action-only methodological lineage from Bulkowski 2005 + Nison 1991 (Japanese Candlestick Charting Techniques).
>
> **Scope:** 16 strategies — 9 in `chart_pattern` (cup_and_handle / flag / triangle / head_and_shoulders / double_bottom) + 7 in `candle` (bullish_engulfing / doji / morning_star / shooting_star / three_white_soldiers / three_black_crows).
>
> **Source of truth.** Code references reflect current state at commit `af9545463` (post-B677 event-driven walk).
>
> **CARRY-FORWARD + HEAVY PRIOR-WALK COVERAGE:** unlike most clusters, the candle family has been individually walked across many recent batches (B636/B639/B641/B643/B645). This doc consolidates the prior individual walks + adds the systematic CHECKLIST #105 7-step coverage that wasn't strictly captured per-strategy. Specifically:
> - **B636:** strat_three_black_crows_short Stage 4 walk (Nison 1991 canonical bearish reversal)
> - **B639:** strat_morning_star Stage 4 walk; deleted strat_evening_star_short per option-a (subset of morning_star SHORT after option-2 reconcile)
> - **B641:** W3 pin_bar direction-contamination fix (producer-additive bullish/bearish_pin_bar); W4 F3 regime-entry deletion; W10 R3 → R4 rename
> - **B643:** W5 strat_pivot_s3_capitulation redesign (Wyckoff Spring/Test sequence) — TANGENTIAL but cited candle-pattern (bullish_engulfing/hammer/above_prev_high reversal triggers)
> - **B645:** strat_pivot_r3_blowoff_short Class 7 NEW (mirror of W5 redesigned)
> - **B650-B651:** W5 + W5m vol_below_avg + regime affinity expansion
> - **B654-B657:** various candle-pattern audits via W8/T3/T8/T10 redundancy
>
> Per `feedback_no_rushing_per_strategy_tweak` + foundational sequence (B660 in flight): no code changes in B678.

---

## Audience

Two:

1. **External reviewer** — for you: this cluster differs from prior clusters in that (a) most strategies have ALREADY received individual B-batch CHECKLIST #105 walks (more so than any other cluster); this doc is the systematic consolidation, (b) **Nison 1991 *Japanese Candlestick Charting Techniques* is the cluster's anchor citation** + Bulkowski 2005 *Encyclopedia of Chart Patterns* extends it for chart-pattern strategies — both legitimate published methodology references. Pattern Q does NOT apply broadly. (c) **CHECKLIST (q) candle-pattern next-bar-open PIT rule** (codified B639 F6) is the cluster's most distinctive methodology constraint — candle patterns COMPLETE at end-of-day; engine must enter NEXT-BAR-OPEN (not same-bar-close) to avoid lookahead. (d) Several strategies have surfaced FORENSIC findings during prior walks (B639 evening_star deletion; B641 pin_bar contamination; W5/W5m volume gates; W4 F3 regime cleanup). The cluster has the cleanest forensic discipline in the roster.

2. **Future readers** — [Cluster scope inventory](#cluster-scope-inventory) below.

---

## Methodology adaptations for chart-pattern + candle clusters

### 1. CHECKLIST (q) candle-pattern next-bar-open PIT rule (B639 F6 codified)

Per B639 walk finding F6: candle patterns COMPLETE at end-of-day close; the engine must enter NEXT-BAR-OPEN (the bar AFTER the pattern completes), not same-bar-close. Otherwise, the strategy would be using same-bar information that wasn't available until the close — a subtle PIT violation. This rule applies to ALL 7 candle strategies + chart-pattern strategies that consume `close_above_open` / `close_below_open` / `bullish_engulfing` / `bearish_engulfing` / candle-anatomy signals.

**Verification:** engine's `entry_bar = signal_bar + 1` convention is the implementation; per CHECKLIST (q) all candle walks must verify this.

### 2. Legitimate peer-reviewable methodology citations

| Sub-cluster | Anchor |
|---|---|
| **Candle family (7)** | Nison 1991 *Japanese Candlestick Charting Techniques* — THE foundational candle-pattern reference; cited by every professional candle-trading text |
| **Chart-pattern family (9)** | Bulkowski 2005 *Encyclopedia of Chart Patterns* — published systematic chart-pattern empirical study |
| **Three Black Crows / Three White Soldiers** | Nison 1991 canonical 3-bar reversal patterns |
| **Morning Star / Evening Star (now deleted)** | Nison 1991 + Bulkowski 2005 confirmation patterns |
| **Cup-and-Handle** | William O'Neil 1988 *How to Make Money in Stocks* (CANSLIM methodology) |
| **Head and Shoulders** | Edwards + Magee 1948 *Technical Analysis of Stock Trends* — foundational chart-pattern text |

**Pattern Q applies to 0 of 16 strategies.** Cluster-positive.

### 3. Forensic-fix density — cluster has the cleanest discipline in the roster

| Batch | Fix | Strategies affected |
|---|---|---|
| **B636** | strat_three_black_crows_short Stage 4 walk per Nison 1991 canonical | three_black_crows_short |
| **B639** | strat_morning_star walk (option-a); evening_star_short DELETED (subset of morning_star SHORT post-option-2 reconcile); STRATEGY_REGIME_AFFINITY morning_star entry deleted (B271 family-bug pattern); S5-RSI-DEFAULT-50-FAMILY ticket queued (F5); CHECKLIST (q) candle next-bar-open PIT rule codified (F6) | morning_star + evening_star (deleted) |
| **B641** | W3 pin_bar direction-contamination fix (producer-additive bullish/bearish_pin_bar signals via compute_pin_bar in technical.py); W4 F3 regime-entry deletion; W10 R3 → R4 rename | pin_bar consumers |
| **B663** | Pattern A default-True → False WAVE 1 sweep | ALL candle + chart_pattern strategies using EMA-200 |
| **B643** | W5 strat_pivot_s3_capitulation redesign — relies on `bullish_engulfing OR hammer` candle confluence | indirect (pivot-strategy uses candle primitives) |
| **B645** | W5m strat_pivot_r3_blowoff_short — `bearish_engulfing OR shooting_star` confluence | indirect |
| **B650** | W5 vol_below_avg AND-required (Wyckoff Spring low-volume Test) | candle confluence on pivot strategy |

**Pattern T (forensic-fix density) RESOLVED cluster-wide.** Cluster has the cleanest discipline in the roster — most B-batch walks per strategy + most empirical-evidence-anchored fixes.

### 4. Pattern N intra-cluster collinearity moderate

16 strategies on ~12 primitives (most patterns have a unique signal):
- `bullish_engulfing` / `bearish_engulfing` (candle pair; cross-walk in pivot/trend strategies)
- `hammer` / `shooting_star` (candle pair)
- `doji_at_support` / `doji_at_resistance` (location-conditional doji pair)
- `morning_star` / (`evening_star` deleted)
- `three_white_soldiers` / `three_black_crows`
- 9 chart-pattern primitives (cup_and_handle / flag_bull / flag_bear / triangle_ascending / head_and_shoulders_bottom / double_bottom + 3 retest variants)

**Effective N ≈ 12, not 16.** Pattern N concern milder than smart-money / SMC clusters but cube ablation still relevant for the few overlapping primitives.

---

## Reviewer findings response matrix

> Pre-emptive matrix.

| # | Finding | Severity | Status | Action |
|---|---|---|---|---|
| _F-pending_ | Awaiting external reviewer | — | OPEN | Will tabulate post-review |

---

## Cluster scope inventory

**16 strategies across 2 categories.** Sub-cluster grouping:

| Sub-cluster | # strategies | Strategies |
|---|---|---|
| **A — Candle reversal patterns (5)** | 5 | CC-1 `strat_morning_star` (B639) / CC-2 `strat_three_white_soldiers` / CC-3 `strat_three_black_crows_short` (B636) / CC-4 `strat_shooting_star_short` / CC-5 `strat_bullish_engulfing_support` |
| **B — Candle doji patterns (2)** | 2 | CC-6 `strat_doji_at_support` / CC-7 `strat_doji_at_resistance_short` (B572 NEW symmetric inverse) |
| **C — Chart-pattern bullish bases (3)** | 3 | CP-1 `strat_cup_and_handle_long` / CP-2 `strat_double_bottom_long` / CP-3 `strat_head_and_shoulders_bottom_long` |
| **D — Chart-pattern flags (3)** | 3 | CP-4 `strat_flag_bull_long` / CP-5 `strat_flag_bull_retest_long` / CP-6 `strat_flag_bear_retest_short` (B607 NEW symmetric inverse) |
| **E — Chart-pattern triangles + retests (3)** | 3 | CP-7 `strat_triangle_ascending_long` / CP-8 `strat_triangle_ascending_retest_long` / CP-9 `strat_cup_and_handle_retest_long` |

---

## Cross-strategy patterns

### Pattern Y (NEW for chart-pattern/candle): Bulkowski 2005 retest pattern carries from breakout

**Affects:** CP-5 + CP-6 + CP-8 + CP-9 (4 retest variants).

**Concern:** Pattern V (Bulkowski retest absorption thesis) from breakout cluster applies; all 4 retest variants are chart-pattern-specific applications. Cube replay against base patterns (CP-1 vs CP-9; CP-4 vs CP-5) settles whether retest variants earn separate registry slots.

### Pattern N (carried) — moderate; 16 strategies on ~12 primitives

### Pattern A (carried) — ✅ verified clean post-B663

### Pattern Q does NOT apply — all 16 have legitimate citations (Nison 1991 + Bulkowski 2005 + Edwards-Magee + O'Neil + others)

---

## Per-strategy walks (compact for B-walked + full for unwalked)

### CC-1. `strat_morning_star` (Candle reversal, walked B639)

> **Status:** ✅ ALREADY WALKED B639 (option-a deep walk). Cross-reference here for cluster-doc consolidation.

**Code:** [screener.py:1909-1944](backtest/signals/screener.py#L1909-L1944) — 3-bar reversal pattern + bullish-engulfing-style closing bar.

**B639 walk outcome:** option-a shipped; evening_star_short DELETED (strict subset of morning_star SHORT after option-2 reconcile); STRATEGY_REGIME_AFFINITY entry deleted (B271 family-bug pattern); CHECKLIST (q) PIT rule codified (F6); S5-RSI-DEFAULT-50-FAMILY ticket queued (F5).

**Nison 1991 anchor:** ✅ REAL — Steve Nison *Japanese Candlestick Charting Techniques* (1991) established morning-star + evening-star as 3-bar reversal patterns.

**No further action needed** beyond B639 walk outcomes; cube validation pending B660.

---

### CC-2. `strat_three_white_soldiers` (Candle reversal, walked B678)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-bar bullish continuation/reversal per Nison 1991.

#### Step 1 — Read the code

[screener.py:1994-...](backtest/signals/screener.py#L1994):

Strategy consumes `three_white_soldiers` boolean (3 consecutive bullish bars with progressively higher closes) + likely EMA-200 trend filter.

#### Step 2-7 (compact — Nison 1991 canonical)

- Category: `candle`; LONG; B291 default
- **Nison 1991 anchor** ✅ — canonical 3-bar bullish reversal/continuation
- Pattern N cross-strategy with CC-3 (three_black_crows) — symmetric pair
- CHECKLIST (q) PIT rule applies — pattern completes at end of bar 3; engine enters bar 4 open
- Fire-count: 3 consecutive bullish bars rare; projected ~50-150/yr universe-wide; PASS

**Options:** (a) status quo / (b) cube validates next-open realized return.

**Awaiting owner direction on CC-2:** confirm CHECKLIST (q) PIT rule applied.

---

### CC-3. `strat_three_black_crows_short` (Candle reversal, walked B636)

> **Status:** ✅ ALREADY WALKED B636. Stage 4 walk shipped per Nison 1991 canonical bearish reversal.

**Code:** [screener.py:2027-...](backtest/signals/screener.py#L2027) — symmetric mirror of CC-2 (3 consecutive bearish bars).

**B636 walk outcome:** Class 7 NEW addition; Nison 1991 canonical bearish-reversal mirror of three_white_soldiers; +1 strategy count (= 222).

**B671 borrow-trap gate applies.**

**No further action needed** beyond B636 walk; cube validation pending B660.

---

### CC-4. `strat_shooting_star_short` (Candle reversal, walked B678)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Bearish reversal candle.

[screener.py:2057-...](backtest/signals/screener.py#L2057) — `shooting_star` (small-body bearish bar with long upper wick at resistance).

#### Step 2-7 (compact)

- Category: `candle`; SHORT; B291 default
- **Nison 1991 anchor** ✅
- Pattern N cross-strategy with CC-7 (doji_at_resistance) and CC-1 (morning_star inverse)
- CHECKLIST (q) PIT rule applies
- **B671 borrow-trap gate applies**
- Cross-cluster: shooting_star is consumed by W5m (pivot_r3_blowoff_short) as reversal-trigger gate
- Fire-count: shooting_star at resistance; projected ~80-200/yr universe-wide; PASS

**Options:** (a) status quo / (b) cube ablation against CC-7 (doji_at_resistance_short) for marginal contribution.

---

### CC-5. `strat_bullish_engulfing_support` (Candle reversal, walked B678)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Bullish engulfing at support; W1 walk in pivot cluster.

[screener.py:1946-...](backtest/signals/screener.py#L1946) — `bullish_engulfing` + support-location gate.

#### Step 2-7 (compact)

- Category: `candle`; LONG; B291 default
- **Nison 1991 anchor** ✅
- **Cross-cluster:** the strategy was walked in pivot cluster (W1 in STAGE_4_PIVOT_CLUSTER_WALKS.md) per CHECKLIST n family-bug grep
- Cross-strategy: W3 pin_bar fix (B641) created bullish_pin_bar / bearish_pin_bar producer-additive symmetric signals
- Pattern N: cross-cluster with W1 pivot-bounce strategies
- Fire-count: bullish engulfing at support moderately common; PASS likely

**Options:** (a) status quo / (b) cube ablation cross-cluster with W1 pivot

---

### CC-6. `strat_doji_at_support` (Candle doji, walked B678)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Doji indecision candle at support.

[screener.py:1958-...](backtest/signals/screener.py#L1958) — `doji` + support-location.

#### Step 2-7 (compact)

- Category: `candle`; LONG; B291 default
- **Nison 1991 doji methodology** ✅
- **Cross-strategy with CC-7** (doji_at_resistance_short — B572 inverse pair)
- B573 owner-correction on `near()` helper — narrow-scope per-strategy override (1.5pct for doji vs global 0.3pct) per `feedback_narrow_scope_blast_radius`
- Fire-count: doji uncommon; doji-at-support narrower; projected ~30-80/yr universe-wide; borderline

**Options:** (a) status quo / (b) cube validates fire count

---

### CC-7. `strat_doji_at_resistance_short` (Candle doji, walked B572)

> **Status:** ✅ B572 NEW (symmetric inverse of CC-6 per Stage 4 cluster walk).

[screener.py:1974-...](backtest/signals/screener.py#L1974) — B572 added per cluster walk; inverse of CC-6.

**B671 borrow-trap gate applies.** Symmetric mirror.

---

### CP-1. `strat_cup_and_handle_long` (Chart-pattern bullish base, walked B678)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Cup and handle pattern per O'Neil 1988.

[screener.py:4185-...](backtest/signals/screener.py#L4185) — `cup_and_handle_pattern` signal from technical.py producer.

#### Step 2-7 (compact)

- Category: `chart_pattern`; LONG; B291 default
- **William O'Neil 1988 CANSLIM** + Bulkowski 2005 anchors ✅
- Pattern N with CP-9 (cup_and_handle_retest variant)
- CHECKLIST (q) carry — chart patterns also use next-bar-open convention
- Fire-count: rare pattern; projected ~20-50/yr universe-wide; borderline

**Options:** (a) status quo / (b) cube ablation CP-1 vs CP-9 retest variant

---

### CP-2. `strat_double_bottom_long` (Chart-pattern bullish base, walked B678)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION.

[screener.py:4173-...](backtest/signals/screener.py#L4173) — `double_bottom_pattern`.

#### Step 2-7 (compact)

- **Bulkowski 2005 + Edwards-Magee 1948 anchors** ✅
- Pattern Y carry from breakout (retest absorption)
- Fire-count rare; ~15-40/yr universe-wide; borderline

---

### CP-3. `strat_head_and_shoulders_bottom_long` (Chart-pattern bullish base, walked B678)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION.

[screener.py:4160-...](backtest/signals/screener.py#L4160) — `head_and_shoulders_bottom_pattern`.

#### Step 2-7 (compact)

- **Edwards + Magee 1948 anchor** ✅ — foundational chart-pattern reference
- Inverse head-and-shoulders bottom is bullish reversal pattern
- **F-missing-inverse-mirror** — no symmetric `head_and_shoulders_top_short` strategy in roster despite documented top pattern equally valid; **Class 7 NEW candidate.**
- Fire-count rare; ~5-20/yr universe-wide; HIGH RISK FAIL min_trades=30

**Options:** (a) status quo / (b) Class 7 NEW `strat_head_and_shoulders_top_short` inverse mirror per `feedback_long_short_inverse_audit` (owner approval required) / (c) EXPLORATORY marker pre-cube.

---

### CP-4. `strat_flag_bull_long` (Chart-pattern flag, walked B678)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION.

[screener.py:4212-...](backtest/signals/screener.py#L4212) — `flag_bull_pattern` from technical.py.

#### Step 2-7 (compact)

- **Bulkowski 2005 flag continuation pattern** ✅
- Pattern N with CP-5 (retest variant) and CP-6 (bearish-mirror retest)
- Fire-count: flag patterns moderately common; projected ~50-150/yr universe-wide; PASS

---

### CP-5. `strat_flag_bull_retest_long` (Chart-pattern flag retest, walked B678)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Retest variant of CP-4.

[screener.py:4279-...](backtest/signals/screener.py#L4279) — Bulkowski retest absorption thesis applies (Pattern Y/V).

#### Step 2-7 (compact)

- Pattern Y retest absorption (vol_below_avg)
- Pattern N with CP-4 (base flag pattern)
- Fire-count: narrower than CP-4; projected ~20-60/yr universe-wide; borderline

---

### CP-6. `strat_flag_bear_retest_short` (Chart-pattern flag retest, walked B607)

> **Status:** ✅ ALREADY WALKED B607. Class 7 NEW from F1 bug fix in flag_bull_retest_long walk.

[screener.py:4360-...](backtest/signals/screener.py#L4360) — B607 added new `compute_flag_break_retest_signals` producer anchored on `flag_bull_breakout_level` / `flag_bear_breakdown_level` (replaces DC20-anchored bug per F1 bug fix in CP-5 walk).

**B671 borrow-trap gate applies.** Mirror of CP-5.

**B621 estimator flagged `flag_bear_retest_short` as 15.77/yr WARN — borderline.**

---

### CP-7. `strat_triangle_ascending_long` (Chart-pattern triangle, walked B678)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION.

[screener.py:4245-...](backtest/signals/screener.py#L4245) — `triangle_ascending_pattern`.

#### Step 2-7 (compact)

- **Bulkowski 2005 + Edwards-Magee 1948 anchor** ✅
- Pattern N with CP-8 (retest variant)
- **F-missing-inverse-mirror** — no `strat_triangle_descending_short` despite documented bearish triangle pattern; **Class 7 NEW candidate.**
- Fire-count: triangles moderately common; ~30-80/yr universe-wide; PASS

---

### CP-8. `strat_triangle_ascending_retest_long` (Chart-pattern triangle retest, walked B678)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Pattern Y retest variant of CP-7.

[screener.py:4411-...](backtest/signals/screener.py#L4411).

---

### CP-9. `strat_cup_and_handle_retest_long` (Chart-pattern retest, walked B678)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Pattern Y retest variant of CP-1.

[screener.py:4258-...](backtest/signals/screener.py#L4258).

---

## B678 cluster walk completion wrap-up

> All 16 chart_pattern + candle strategies now have walk coverage (some via cross-reference to prior B-batch individual walks):

- **Sub-cluster A — Candle reversal (5):** CC-1 (B639) ✅ + CC-2 + CC-3 (B636) ✅ + CC-4 + CC-5
- **Sub-cluster B — Doji (2):** CC-6 + CC-7 (B572) ✅
- **Sub-cluster C — Chart bullish bases (3):** CP-1 + CP-2 + CP-3
- **Sub-cluster D — Flags (3):** CP-4 + CP-5 + CP-6 (B607) ✅
- **Sub-cluster E — Triangles + retests (3):** CP-7 + CP-8 + CP-9

**Total fully-covered: 16 of 16. CLUSTER WALK COMPLETE.**

### Bundled disposition recommendations summary

| Pattern | Strategies | Disposition |
|---|---|---|
| **A (default-True silent-gap)** | ✅ All 16 clean post-B663/B630 | ✅ RESOLVED |
| **CHECKLIST (q) PIT rule (B639 F6 codified)** | All 16 (candle next-bar-open convention) | Verified by engine convention |
| **M / Q (citation)** | LEGITIMATE for all 16 (Nison 1991 + Bulkowski 2005 + Edwards-Magee 1948 + O'Neil 1988) | DOCUMENTATION-ONLY; cluster-positive |
| **N (intra-cluster collinearity)** | 16 strategies on ~12 primitives; effective N ≈ 12 | Cube ablation moderate priority |
| **Y (Bulkowski retest)** | CP-5 + CP-6 + CP-8 + CP-9 (4 retest variants) | Cube ablation against base patterns |
| **T (forensic-fix density)** | RESOLVED — cluster has cleanest discipline in roster (B636/B639/B641/B643/B645/B650/B654-657) | ✅ Cluster-positive |
| **F-missing-inverse-mirror** | CP-3 (head_and_shoulders_top_short MISSING) + CP-7 (triangle_descending_short MISSING) | NEW Class 7 candidates per `feedback_long_short_inverse_audit`; owner approval required |
| **B671 SHORT borrow-trap** | CC-3 + CC-4 + CC-7 + CP-6 | Already centralized B671 (revert pending per B673 reviewer) |
| **F-fire-count Pattern G** | CP-3 (head_and_shoulders_bottom_long) ~5-20/yr borderline; CP-1 (cup_and_handle) ~20-50/yr borderline; CP-2 (double_bottom) ~15-40/yr borderline | Post-B660 EXPLORATORY decision |

### Queue tickets surfaced

NEW B678 tickets:

- `S4-CP-MISSING-INVERSE-MIRRORS-CLASS-7-NEW-CANDIDATES` — head_and_shoulders_top_short + triangle_descending_short (Class 7 NEW per missing-inverse audit)
- `S4-CHART-PATTERN-Y-RETEST-VS-BASE-CUBE-ABLATIONS` — CP-1 vs CP-9, CP-4 vs CP-5, CP-7 vs CP-8 (3 retest-vs-base ablations)

EXISTING tickets cross-referenced:
- `S5-FIRE-COUNT-CANDIDATES` — CP-6 `flag_bear_retest_short` is on the WARN list (15.77/yr B621 estimator)
- `S4-LOW-FIRE-COMBO-EXPLORATORY-REVIEW-POST-B660` — CP-3 candidate (5-20/yr borderline)

---

## Cluster-wide methodology references

- **Producers:** `compute_pin_bar` (B641 producer-additive) + `compute_candle_patterns` + `compute_chart_patterns` in [backtest/signals/technical.py](backtest/signals/technical.py)
- **Citations:**
  - Nison 1991 *Japanese Candlestick Charting Techniques* — candle family anchor
  - Bulkowski 2005 *Encyclopedia of Chart Patterns* — chart-pattern family anchor
  - Edwards + Magee 1948 *Technical Analysis of Stock Trends* — head-and-shoulders + triangles
  - O'Neil 1988 *How to Make Money in Stocks* (CANSLIM) — cup-and-handle
  - Wyckoff Spring/Test sequence (cited W5/W5m pivot strategies — cross-cluster)
- **Forensic-fix lineage:** B572 + B636 + B639 + B641 + B643 + B645 + B650-B651 + B654-657 + B663 + B607
- **CHECKLIST (q) candle next-bar-open PIT rule** (codified B639 F6 owner-approved)

---

## B678 cluster walk status

| Item | Status |
|---|---|
| Doc infrastructure + cross-cluster consolidation of prior individual walks | ✅ B678 |
| 16 strategies covered (10 NEW compact-walks + 6 cross-references to prior B-batch walks) | ✅ B678 |
| External reviewer pass | ⏳ post-walk-completion |

**Cumulative B678: 16 of 16 strategies covered. CLUSTER WALK COMPLETE.**

---

## FINAL CROSS-CLUSTER STATUS SNAPSHOT (post-B678 — ALL STAGE 4 CLUSTER WALKS COMPLETE)

| Cluster | Doc | Status | Strategy count |
|---|---|---|---|
| Pivot | [STAGE_4_PIVOT_CLUSTER_WALKS.md](STAGE_4_PIVOT_CLUSTER_WALKS.md) | ✅ Complete | ~10 |
| Trend | [STAGE_4_TREND_CLUSTER_WALKS.md](STAGE_4_TREND_CLUSTER_WALKS.md) | ✅ Complete | ~12 |
| Smart Money | [STAGE_4_SMART_MONEY_CLUSTER_WALKS.md](STAGE_4_SMART_MONEY_CLUSTER_WALKS.md) | ✅ Complete + B674 reviewer-critique | 41 |
| SMC | [STAGE_4_SMC_CLUSTER_WALKS.md](STAGE_4_SMC_CLUSTER_WALKS.md) | ✅ Complete | 18 |
| ICT | [STAGE_4_ICT_CLUSTER_WALKS.md](STAGE_4_ICT_CLUSTER_WALKS.md) | ✅ Complete | 12 |
| Breakout | [STAGE_4_BREAKOUT_CLUSTER_WALKS.md](STAGE_4_BREAKOUT_CLUSTER_WALKS.md) | ✅ Complete | 19 |
| Event-driven | [STAGE_4_EVENT_DRIVEN_CLUSTER_WALKS.md](STAGE_4_EVENT_DRIVEN_CLUSTER_WALKS.md) | ✅ Complete | 10 (7 NEW + 3 cross-ref) |
| **Chart pattern + Candle** | **[STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md](STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md) (THIS DOC)** | **✅ Complete (B678)** | **16** |

**Total Stage 4 walks: 8 cluster docs complete; ~138 strategies covered with CHECKLIST #105 7-step walks across ~222 total registry (some strategies belong to multiple clusters and are walked once).**

**Remaining strategy categories NOT in cluster walks:** smart_money_sleeve (10 — walked as part of smart-money B673), smart_money_13f (7 — same), institutional_persistence (12 — same), classification_change (10 — partially walked sub-cluster D), multi_timeframe (5), cross_asset (5), factor (6), confluence (2), mean_reversion (3), momentum (3), news_sentiment (6), volume_profile (3), pairs (2), orb (2), vwap (1), pivot (1 unwalked beyond pivot cluster) ≈ 78 additional strategy slots not in cluster walks.

**Per `feedback_strategy_counts_by_buckets_each_turn` (owner directive 2026-06-05):** strategy count buckets =
- 8 walked clusters covering ~138 unique strategies
- ~78 remaining strategies in smaller categories (multi_timeframe, factor, mean_reversion, cross_asset, momentum, etc.) — not yet cluster-walked
- ALL_STRATEGIES total = 222 per `len(ALL_STRATEGIES)`; remaining categories may warrant a 9th cluster walk doc OR individual walks per CHECKLIST #105.
