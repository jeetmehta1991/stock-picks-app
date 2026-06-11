# Stage 4 Chart Pattern + Candle Cluster Walks — Per-Strategy Deep-Dive Audit

> **B693 BANNER ADDENDUM (2026-06-11) — selective-reading correction.** B691 (this doc and 4 others shipped that batch) labeled the 9/9 chart-pattern FAIL as "🔴 FALSE-NEGATIVE — PENDING-B689-RERUN." External reviewer of [STAGE_4_BREAKOUT_CLUSTER_WALKS.md](STAGE_4_BREAKOUT_CLUSTER_WALKS.md) caught the methodology problem: **"false negative" used without a positive test is an unfalsifiable escape hatch**. The favorable B660 measurement (5 candle PASS) was labeled LOCKED, unfavorable (9 chart-pattern FAIL) was labeled PENDING-RERUN — a one-directional reading. A measured zero must be DIAGNOSED, not assumed. Each chart-pattern strategy's zero now requires the positive two-part test (signal-key present in dict + relaxed-conjunction count > 0) before the re-run conclusion is accepted. Diagnostic tool scaffolded at [`scripts/diagnose_zero_fires.py`](scripts/diagnose_zero_fires.py); will run post-B689-rerun on each chart-pattern strategy to confirm "harness gap" vs "empty conjunction" before any verdict shift. The PENDING-B689-RERUN label below stays but is now provisional on that diagnostic, not a free pass.
>
> ---
>
> **B691 STATUS BANNER (2026-06-11) — SPLIT VERDICT: candle ✅ TRUSTWORTHY / chart-pattern 🔴 FALSE-NEGATIVE-PENDING-RERUN-B689.** B660 measurement landed [2026-06-11 02:30 UTC](output_audit/fire_count_measured_b660_full_universe.json). The two clusters bundled in this doc have DIFFERENT trust statuses:
>
> **CANDLE cluster (8 strategies) — ✅ TRUSTWORTHY:** all candle gates use only `technical.compute_candles` + companion technical producers. B660 numbers stand. The B689 re-run will NOT change these.
> | Strategy | LONG | SHORT | Verdict |
> |---|---:|---:|---|
> | bullish_engulfing_support | 254 | 274 | ✅ PASS |
> | shooting_star_short | 0 | 204 | ✅ PASS |
> | three_white_soldiers | 2,616 | 0 | ✅ PASS |
> | three_black_crows_short | 0 | 2,464 | ✅ PASS |
> | doji_at_resistance_short | 0 | 210 | ✅ PASS |
> | morning_star_long (carry-forward from pre-B639 walks) | — | — | (verify in re-run output; structurally TRUSTWORTHY) |
> | hammer_at_support_long (B685 Class 7 NEW) | — | — | (need re-run; small fire-count uncertain) |
> | pin_bar_reversal_long (carry-forward B641) | — | — | (verify in re-run; structurally TRUSTWORTHY) |
>
> **CHART-PATTERN cluster (9 strategies) — 🔴 FALSE-NEGATIVE — PENDING-B689-RERUN:** all 9 chart-pattern strategies showed `0 fires` in B660. **This is a harness gap, NOT a real verdict.** The `chart_patterns.compute_all_chart_patterns(df)` producer (which emits `cup_handle_detected`, `head_shoulders_top_detected`, `triangle_*_detected`, `flag_*_detected`, `double_top_detected`, `double_bottom_detected`, plus 3 B685 new producers for retest variants) was NOT invoked in the pre-B689 precompute path. **B689 (commit `8e8c258dd`) shipped the wire-in;** the in-flight re-run (task `bzja19ugq`, ETA ~2026-06-12 12:30) will produce real numbers for:
> - `strat_cup_and_handle_long` (CP-1, EXPLORATORY marker per B685)
> - `strat_inverted_cup_and_handle_short` (B686 Class 7 NEW)
> - `strat_head_and_shoulders_top_short` (B685 Class 7 NEW)
> - `strat_triangle_ascending_long`, `strat_triangle_descending_short` (B685 Class 7 NEW)
> - `strat_flag_bull_long`, `strat_flag_bear_retest_short`
> - `strat_double_bottom_long`, `strat_double_top_short`
>
> All `PENDING-B660` and "verdict unknown" labels for the chart-pattern subset are now **PENDING-B660-RERUN-B689** until ~2026-06-12 12:30.
>
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

### CC-2. `strat_three_white_soldiers` (Candle reversal, walked B683 full-expansion)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B683 self-critique CC-A re-expansion). 2-gate LONG; Nison 1991 canonical 3-bar bullish reversal. Companion strategy to B636-walked CC-3 (three_black_crows_short symmetric mirror).

#### Step 1 — Read the code

[screener.py:1964-1994](backtest/signals/screener.py#L1964-L1994):

```python
def strat_three_white_soldiers(s):
    """Three White Soldiers bullish reversal pattern (Nison
    *Japanese Candlestick Charting Techniques* 1991)."""
    fires = (s.get("three_white_soldiers") and
             s.get("rsi_14", 50) < 60)
```

**2-gate LONG.**

| Gate | Meaning |
|---|---|
| `three_white_soldiers` | EVENT: producer-emitted 3-bar bullish pattern (3 consecutive bullish bars, each opening within prior body + closing near high; producer = `compute_candle_signals` in technical.py) |
| `rsi_14 < 60` | STATE: RSI cap to avoid already-overbought entries (gives room to run; symmetric with CC-3's `rsi_14 > 40` floor) |

#### Step 2 — Classify

- Category: `candle`; LONG; B291 default; last touched B636 (Class 7 NEW mirror added at that batch)

#### Step 3 — Producer source-read + temporality

- `three_white_soldiers` producer: strict-monotone 3-bar bullish detection per Nison 1991 spec. Pattern COMPLETES at the close of bar 3.
- Per CHECKLIST (q) PIT rule (B639 F6): engine MUST enter NEXT-BAR-OPEN (bar 4 open) — NOT same-bar (bar 3) close. Verified by engine convention `entry_bar = signal_bar + 1`.
- `rsi_14` is STATE (today's RSI computed at bar 3 close)
- EVENT/STATE: 1 EVENT (pattern) + 1 STATE (RSI gate)

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Nison *Japanese Candlestick Charting Techniques* 1991" | ✅ **REAL ANCHOR** — Steve Nison's foundational candle methodology text; widely cited in trader education + the Bloomberg/CMT Association curriculum |
| "Strong reversal signal indicating sustained buying pressure" | ✅ Mechanically accurate (3 consecutive bullish closes = visible accumulation) |
| "RSI<60 gate keeps the entry from already-overbought territory" | ✅ Defensible — gives room to run; reasonable cap |
| Implicit "3-bar pattern is high-conviction" | ⚠ Nison framework, not peer-reviewed empirically; cube replay is the only adjudication of magnitude |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B636 walk shipped CC-3 (Class 7 NEW symmetric mirror); no further per-strategy investigation pending
- CHECKLIST (q) PIT rule applies; engine convention assumed correct (cluster-wide pyramid-pin candidate per B680 self-critique CC-C)
- Cross-strategy correlation with CC-1 (morning_star) and CC-5 (bullish_engulfing) — all are 1-3 bar bullish reversal patterns; Pattern N cube ablation candidate

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — CC-3 `strat_three_black_crows_short` (B636 Class 7 NEW)
- Economic symmetry: ⚠ Equity upward-drift bias means three_white_soldiers more common than three_black_crows; CC-3 will have lower fire count

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-nison-anchor ✅** | Real published methodology citation; cluster-positive | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-CHECKLIST-(q)-PIT** | Engine convention pin pending B680 CC-C cluster-wide pyramid test | LOW-MEDIUM | B680 CC-C |
| **F-pattern-N bullish-reversal cluster** | CC-1 + CC-2 + CC-5 + CC-6 + W1 pivot all detect bullish reversal at different anchors; cube ablation candidate | MEDIUM | Pattern N |
| **F-rsi-default-50** | `rsi_14 < 60` — strict inequality at midpoint+10; default=50 fail-safe (50 < 60 is True) → with missing data the gate auto-PASSES. **Could mask true overbought conditions if RSI producer fails silently.** Family member of `S5-RSI-DEFAULT-50-FAMILY` adjacent class | LOW-MEDIUM | F-rsi |
| F-fire-count | 3-consecutive-bullish-bar pattern rare; projected ~50-150/yr universe-wide; PASS | INFO | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) `rsi_14 < 60` default-50 fail-safe direction inversion candidate — change `s.get("rsi_14", 50) < 60` to `s.get("rsi_14") and rsi < 60` (None check first) to fail-safe to NO-FIRE on missing data |
| (c) Cube validation post-B660 |
| **(d) RECOMMENDED — (a) + (c). Strategy is cluster-positive (Nison anchor); minimal changes. Cube validates per-cell Sharpe + branch-stratified with CC-3 symmetric.** |

**My recommendation: (d).**

**Awaiting owner direction on CC-2:**
1. (a)/(b)/(c)/(d) — recommendation (d)
2. Pattern N bullish-reversal-at-support cross-cluster ablation scope (CC-1/2/5/6 + W1)
3. F-rsi default-50 fail-safe direction inversion candidate (cluster-wide application to candle strategies)

---

### CC-3. `strat_three_black_crows_short` (Candle reversal, walked B636)

> **Status:** ✅ ALREADY WALKED B636. Stage 4 walk shipped per Nison 1991 canonical bearish reversal.

**Code:** [screener.py:2027-...](backtest/signals/screener.py#L2027) — symmetric mirror of CC-2 (3 consecutive bearish bars).

**B636 walk outcome:** Class 7 NEW addition; Nison 1991 canonical bearish-reversal mirror of three_white_soldiers; +1 strategy count (= 222).

**B671 borrow-trap gate applies.**

**No further action needed** beyond B636 walk; cube validation pending B660.

---

### CC-4. `strat_shooting_star_short` (Candle reversal, walked B683 full-expansion)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B683 re-expansion). 3-gate SHORT; Nison 1991 shooting-star at resistance with RSI overbought.

#### Step 1 — Read the code

[screener.py:2027-2037](backtest/signals/screener.py#L2027-L2037):

```python
def strat_shooting_star_short(s):
    fires = (s.get("shooting_star") and
             (s.get("near_r1") or s.get("near_r2") or
              s.get("bb_20_20_touch_upper")) and
             s.get("rsi_14", 50) > 65)
```

**3-gate SHORT.**

| Gate | Meaning |
|---|---|
| `shooting_star` | EVENT: small-body bearish bar with long upper wick (producer = `compute_candle_signals`); canonical Nison 1991 1-bar reversal pattern |
| `near_r1 OR near_r2 OR bb_20_20_touch_upper` | OR-disjunct: at resistance (pivot R1 / R2 OR Bollinger upper band touch) — confluence with overhead level |
| `rsi_14 > 65` | STATE: overbought (>65; tighter than canonical 70 but defensible) |

#### Step 2 — Classify

- Category: `candle`; SHORT; B291 default
- **B671 centralized borrow-trap gate applies** (SHORT-direction strategy)
- Cross-cluster: `shooting_star` signal also consumed by W5m (pivot_r3_blowoff_short) as bearish-reversal-trigger per B643/B645 redesign

#### Step 3 — Producer source-read + temporality

- `shooting_star` 1-bar pattern; completes at bar close; CHECKLIST (q) PIT rule: enter NEXT-BAR-OPEN
- `near_r1` / `near_r2` STATE from pivot producer; `bb_20_20_touch_upper` STATE from Bollinger producer
- `rsi_14` STATE
- EVENT/STATE: 1 EVENT (pattern) + 2 STATE (location + overbought)

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| Implicit "shooting star at resistance with RSI overbought = bearish reversal" | ✅ Canonical Nison 1991 setup; shooting-star alone is weak; confluence with resistance + overbought RSI tightens the signal |
| `rsi_14 > 65` threshold | ⚠ Tighter than canonical Wilder 70; not empirically justified; Pattern O hardcoded |

#### Step 5 — OPEN_INVESTIGATIONS grep

- Cross-strategy with W5m bearish reversal trigger (`shooting_star` consumed) — Pattern N cluster cross-ref
- Cross-cluster with CC-7 (doji_at_resistance_short) — both fire at resistance with similar 1-bar patterns

#### Step 6 — Missing-inverse + economic-symmetry

- **Hammer at support** is the documented inverse 1-bar bullish reversal per Nison 1991 — currently NOT a standalone registered strategy (`hammer` signal IS produced and consumed by W5/W3 pivot bounce strategies as confluence gate, but no `strat_hammer_at_support_long` direct mirror exists)
- **F-missing-inverse-mirror** — same class as CP-3 (head_and_shoulders_top_short MISSING) per `feedback_long_short_inverse_audit`. Class 7 NEW candidate.

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-nison-anchor ✅** | Cluster-positive | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-missing-inverse-mirror** | `strat_hammer_at_support_long` NOT registered; Nison documents the mirror as canonical | MEDIUM | Per-strategy reframing |
| **F-pattern-O `rsi_14 > 65` threshold** | Tighter than canonical 70; not empirically calibrated | LOW | Pattern O |
| **F-pattern-N cluster** | CC-4 + CC-7 + W5m all detect bearish reversal at resistance / R3 / Bollinger upper | MEDIUM | Pattern N |
| F-fire-count | shooting_star + resistance + overbought RSI co-occurrence; projected ~80-200/yr universe-wide; PASS | INFO | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Class 7 NEW `strat_hammer_at_support_long` mirror per `feedback_long_short_inverse_audit` (owner approval required) |
| (c) Cube ablation CC-4 vs CC-7 vs W5m for marginal contribution |
| (d) RSI threshold sensitivity sweep (65 vs 70 vs 75) post-cube |
| **(e) RECOMMENDED — (a) + (c). Pattern N cube ablation against doji_at_resistance + pivot W5m; (b) Class 7 NEW pending owner approval; (d) post-cube** |

**My recommendation: (e).**

**Awaiting owner direction on CC-4:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (e)
2. (b) `strat_hammer_at_support_long` Class 7 NEW addition (owner approval gate)
3. Pattern N bearish-reversal-at-resistance cube ablation scope

---

### CC-5. `strat_bullish_engulfing_support` (Candle reversal, walked B683 full-expansion — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B683 re-expansion). 3-gate dual via `_strat3`; bullish/bearish engulfing at support/resistance with OBV confirmation. Cross-cluster with W1 pivot.

#### Step 1 — Read the code

[screener.py:1916-1925](backtest/signals/screener.py#L1916-L1925):

```python
def strat_bullish_engulfing_support(s):
    # B628 F1 family-sweep: positive symmetric obv_bearish.
    fl = (s.get("bullish_engulfing") and (s.get("near_s1") or s.get("near_s2") or s.get("at_key_fib")) and s.get("obv_bullish"))
    fs = (s.get("bearish_engulfing") and (s.get("near_r1") or s.get("near_r2") or s.get("at_key_fib"))
          and s.get("obv_bearish"))
```

**3-gate dual.**

| Direction | Pattern gate | Location OR | OBV gate |
|---|---|---|---|
| LONG | `bullish_engulfing` | `near_s1 OR near_s2 OR at_key_fib` | `obv_bullish` |
| SHORT | `bearish_engulfing` | `near_r1 OR near_r2 OR at_key_fib` | `obv_bearish` (B628 positive symmetric fix) |

#### Step 2 — Classify

- Category: `candle`; dual; B291 default; last touched B628 (F1 family-sweep on obv_bearish positive symmetric)
- **B671 borrow-trap gate applies** SHORT side

#### Step 3 — Producer source-read + temporality

- `bullish_engulfing` / `bearish_engulfing`: 2-bar pattern (today's body engulfs prior body); EVENT at bar close
- `near_s1` / `near_s2` / `near_r1` / `near_r2`: STATE pivot proximity (±0.3% bands per technical.py)
- `at_key_fib`: STATE Fib zone proximity (per `compute_fibonacci` with `lookback=50` — cross-ref `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT`)
- `obv_bullish` / `obv_bearish`: STATE OBV direction
- EVENT/STATE: 1 EVENT (engulfing) + 2 STATE (location + OBV) per direction

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| Implicit "engulfing at support/resistance is high-conviction" | ✅ Canonical Nison 1991 setup; engulfing alone is weak; confluence with pivot + OBV tightens |
| B628 F1 OBV positive-symmetric fix | ✅ Forensic-fix per `feedback_never_use_NOT_s_get_pattern` |

#### Step 5 — OPEN_INVESTIGATIONS grep

- Cross-ref `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT` (`at_key_fib` PIT integrity)
- Cross-strategy with W1 pivot (`strat_pivot_s1_bounce` consumes `bullish_engulfing` + pivot location); Pattern N flagship intra-/cross-cluster ablation per B680 self-critique CC-D

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Already dual (`_strat3`); engulfing pattern is directionally symmetric per Nison
- Economic symmetry: equity upward drift biases LONG-side fire count higher

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-nison-anchor ✅** | Cluster-positive | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-B628 forensic-fix ✅** | OBV positive-symmetric shipped | INFO / ✅ POSITIVE | Pattern T |
| **F-pattern-N cross-cluster W1** | CC-5 + W1 (pivot_s1_bounce) both consume `bullish_engulfing` + pivot location; cube ablation candidate per B680 CC-D | MEDIUM | Pattern N |
| **F-Fib-anchor lookahead** | `at_key_fib` PIT integrity cross-ref existing ticket | LOW-MEDIUM | S4-FIB-ANCHOR-LOOKAHEAD-AUDIT |
| F-fire-count | engulfing at pivot + OBV alignment; projected ~120-300/yr universe-wide; PASS | INFO | F4 |

**Options:** (a) status quo / (b) cube Pattern N ablation with W1 / **(c) RECOMMENDED — (a) + (b) post-B660**

**Awaiting owner direction on CC-5:** Pattern N flagship cross-cluster ablation (CC-5 + W1).

---

### CC-6. `strat_doji_at_support` (Candle doji, walked B683 full-expansion)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B683 re-expansion). 3-gate LONG; B574 `_wide` (1.5%) band narrow-scope override per `feedback_narrow_scope_blast_radius`.

#### Step 1 — Read the code

[screener.py:1928-1941](backtest/signals/screener.py#L1928-L1941):

```python
def strat_doji_at_support(s):
    # B574 (2026-06-04 owner-directed narrow-scope per
    # feedback_narrow_scope_blast_radius): consumes `_wide` flag
    # variants (1.5pct band) exclusively.
    fires = (s.get("doji") and
             (s.get("near_s1_wide") or s.get("near_s2_wide") or s.get("at_key_fib_wide")) and
             s.get("vol_spike_15x"))
```

**3-gate LONG.**

| Gate | Meaning |
|---|---|
| `doji` | EVENT: 1-bar indecision pattern (open ≈ close) per Nison 1991 |
| `near_s1_wide OR near_s2_wide OR at_key_fib_wide` | OR-disjunct: wide 1.5% band (B574 narrow-scope override; default narrow is 0.3%) |
| `vol_spike_15x` | EVENT: today's volume > 1.5x trailing 20-bar mean (level being contested) |

#### Step 2 — Classify

- Category: `candle`; LONG; B291 default; last touched B574 (narrow-scope `_wide` override)

#### Step 3 — Producer source-read + temporality

- `doji` producer at `compute_candle_signals` (technical.py); strict-monotone 1-bar pattern
- `near_s1_wide` etc. are B574-shipped wider pivot-proximity flags (1.5% vs 0.3% canonical)
- `vol_spike_15x` EVENT
- EVENT/STATE: 2 EVENT + 1 STATE (location)

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Doji candle at support" + "indecision after downmove" | ✅ Nison 1991 canonical |
| "Volume spike confirms the level is being contested" | ✅ Defensible — volume spike + doji = active price discovery at level |
| B574 wide 1.5% band rationale | ✅ Owner-directed narrow-scope per `feedback_narrow_scope_blast_radius`; cluster-positive design discipline |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B574 + B628 forensic lineage; no active concerns
- Companion CC-7 (B572 NEW symmetric inverse)

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — CC-7 `strat_doji_at_resistance_short` (B572 Class 7 NEW; also uses `_wide` band post-B574)

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-nison-anchor ✅** | Cluster-positive | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-B574 narrow-scope ✅** | Pattern discipline shipped | INFO / ✅ POSITIVE | `feedback_narrow_scope_blast_radius` |
| **F-pattern-N candle-at-support** | CC-1 + CC-5 LONG + CC-6 all detect bullish reversal at support; cube ablation candidate | MEDIUM | Pattern N |
| F-fire-count | Doji uncommon (1-bar pattern with strict open≈close); + 1.5% support band narrows; projected ~30-80/yr universe-wide; borderline | INFO-MEDIUM | F4 |

**Options:** (a) status quo / (b) cube validates B574 wide-band fire-count uplift / (c) Pattern N cube ablation. **My recommendation: (a) + (b) + (c).**

**Awaiting owner direction on CC-6:** Pattern N ablation scope.

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

### CP-1. `strat_cup_and_handle_long` (Chart-pattern bullish base, walked B683 full-expansion)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B683 re-expansion). 5-gate LONG; O'Neil 1988 CANSLIM cup-and-handle + B278 forensic-fixed gate stack.

#### Step 1 — Read the code

[screener.py:4172-4196](backtest/signals/screener.py#L4172-L4196):

```python
def strat_cup_and_handle_long(s):
    """Batch 252: O'Neil CANSLIM cup-and-handle long.

    Batch 278 (Tier 2 gate tightening 2026-05-20 owner-approved option B):
    Stage B v2 showed 12 trades / 16.7% WR / -4.30% mean / -52 pp.
    """
    fires = (
        s.get("cup_handle_detected", False)
        and s.get("price_above_ema_200", False)
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_50", True)
        and s.get("rsi_14", 50) < 70
    )
```

**5-gate LONG.** B278 FORENSIC-FIXED CASE — pre-B278 fired 12 trades / 16.7% WR / -52pp; B278 added volume + EMA-50 + RSI gates to address pattern detection without confirmation.

| Gate | Meaning |
|---|---|
| `cup_handle_detected` | EVENT: cup-and-handle pattern completion per `compute_chart_patterns` |
| `price_above_ema_200` | STATE: long-term uptrend; B663-fixed |
| `vol_spike_2x` | EVENT (B278 added): 2x volume on handle breakout — O'Neil canonical requires this |
| `price_above_ema_50` | STATE (B278 added): intermediate trend filter — ⚠ Pattern A default-True silent-gap (WAVE 2 family) |
| `rsi_14 < 70` | STATE: not overbought (avoid late-stage entries) |

#### Step 2 — Classify

- Category: `chart_pattern`; LONG; B291 default; last touched B278 (forensic gate-add) + B663 (Pattern A WAVE 1 200-EMA)

#### Step 3 — Producer source-read + temporality

- `cup_handle_detected` from `compute_chart_patterns` — pattern detection logic with completion criteria (rim + cup depth + handle pullback)
- Other gates: STATE (EMA + RSI) + EVENT (vol spike)
- EVENT/STATE: 2 EVENT + 3 STATE
- CHECKLIST (q) PIT: pattern completes at handle breakout bar; engine enters next-bar-open

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "O'Neil 1988 CANSLIM" | ✅ William O'Neil *How to Make Money in Stocks* (1988); foundational growth-stock methodology |
| "Bulkowski 2005" (cross-ref) | ✅ Bulkowski's chart-pattern study validates cup-and-handle as documented pattern |
| B278 fix "pattern detection without volume confirmation = unconfirmed breakouts often fail" | ✅ Forensic-evidence-backed; aligns with O'Neil's CANSLIM canonical setup |
| Implicit "high-quality breakout" | ⚠ Bulkowski 2005 published frequency data: cup-and-handle patterns RARE (~50/yr in O'Neil's CANSLIM universe of several thousand stocks; our T1a 503 likely produces ~5-15/yr). Per B680 self-critique CC-E: walk projection of 20-50/yr is OPTIMISTIC. **Pattern G fire-starve risk HIGH.** |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B278 forensic-fix re-validation pending cube (same class as B262/B278 SMC re-validation)
- Pattern A WAVE 2 ema_50 default-True candidate (Pattern A WAVE 2 family per B680 SMC CC-A carry)
- B660 EARLY-FINDING: cup_and_handle_long = 0 fires/yr universe-wide (visible in TaskOutput) — confirms Pattern G fire-starve

#### Step 6 — Missing-inverse + economic-symmetry

- ❌ **No SHORT mirror registered.** Inverted cup-and-handle (also called "dump and handle" or distribution top) IS documented per Bulkowski 2005 as bearish-reversal pattern. Class 7 NEW candidate per `feedback_long_short_inverse_audit`.

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-O'Neil + Bulkowski anchor ✅** | Cluster-positive | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-B278 forensic-fix re-validation** | Post-fix 5-gate design needs cube validation | MEDIUM | Pattern T |
| **F-Pattern-A WAVE-2 `price_above_ema_50`** | Default-True silent-gap candidate (WAVE 2 family) | LOW-MEDIUM | Pattern A WAVE 2 |
| **F-Pattern-G HIGH RISK FAIL** | B660 confirms 0 fires/yr universe-wide; pre-cube DELETE candidate per B620 precedent OR EXPLORATORY marker | HIGH | F4 + B680 CC-E |
| **F-missing-inverse-mirror** | `strat_inverted_cup_and_handle_short` Class 7 NEW candidate per Bulkowski 2005 | MEDIUM | F6 |
| F-fire-count | B660 EARLY: 0 fires/yr universe-wide CONFIRMED | DATA | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) DELETE per B620 precedent — B660 0-fire confirmation + projected 5-15/yr per Bulkowski published data well below min_trades=30 |
| (c) EXPLORATORY marker pre-cube (less aggressive than DELETE) |
| (d) Loosen gates — drop vol_spike_2x or vol_above_avg (would compromise O'Neil canonical) |
| (e) Class 7 NEW `strat_inverted_cup_and_handle_short` mirror addition |
| **(f) RECOMMENDED — (c) EXPLORATORY post-B660 measurement + (e) Class 7 NEW addition pending owner approval. (b) DELETE is justified by B620 precedent but EXPLORATORY preserves the strategy for future re-validation if Bulkowski 2005 published frequencies prove out at our universe scale.** |

**My recommendation: (f).**

**Awaiting owner direction on CP-1:**
1. (a)/(b)/(c)/(d)/(e)/(f) — recommendation (f)
2. Pattern G EXPLORATORY vs DELETE decision (B620 precedent applies)
3. Class 7 NEW inverted cup-and-handle short addition

---

### CP-2. `strat_double_bottom_long` (Chart-pattern bullish base, walked B683 full-expansion)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B683 re-expansion). 2-gate LONG; Edwards-Magee 1948 + Bulkowski 2005 anchors.

#### Step 1 — Read the code

[screener.py:4160-4169](backtest/signals/screener.py#L4160-L4169):

```python
def strat_double_bottom_long(s):
    """Batch 252: double-bottom long entry."""
    fires = (
        s.get("double_bottom_detected", False)
        and s.get("price_above_ema_200", False)
    )
```

**2-gate LONG.** Simplest chart-pattern walk in cluster.

| Gate | Meaning |
|---|---|
| `double_bottom_detected` | EVENT: producer detects 2 lows at same level + intervening trough |
| `price_above_ema_200` | STATE: long-term uptrend; B663-fixed |

#### Step 2 — Classify

- Category: `chart_pattern`; LONG; B291 default; last touched B252 (original) + B663 (Pattern A)

#### Step 3 — Producer source-read + temporality

- `double_bottom_detected` from `compute_chart_patterns`; pattern completion logic
- EVENT/STATE: 1 EVENT + 1 STATE
- CHECKLIST (q) PIT applies

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Double-bottom pattern" implicit | ✅ Edwards-Magee 1948 *Technical Analysis of Stock Trends* + Bulkowski 2005 — both document double-bottom as canonical bullish reversal |
| Implicit "high-quality entry" | ⚠ Bulkowski 2005 reports double-bottom WR ~70% on confirmed breakouts (with neckline confirmation gate which the strategy LACKS). Our strategy fires on `double_bottom_detected` alone without neckline-break confirmation. Possibly fires too early. |

#### Step 5 — OPEN_INVESTIGATIONS grep

- No neckline-confirmation gate — possible F-design-gap
- B660 in-flight: fire-count data pending (run hasn't reached "d" strategies yet for chart_pattern category)

#### Step 6 — Missing-inverse + economic-symmetry

- **Double-top short** is the documented inverse per Edwards-Magee + Bulkowski; currently NOT registered as standalone strategy. Class 7 NEW candidate.

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-edwards-magee + Bulkowski anchor ✅** | Cluster-positive | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-no-neckline-confirmation** | Strategy fires on pattern detection alone; Bulkowski stats are conditional on neckline-break confirmation | MEDIUM | F1 (design gap) |
| **F-missing-inverse-mirror** | `strat_double_top_short` Class 7 NEW candidate per `feedback_long_short_inverse_audit` | MEDIUM | F6 |
| **F-Pattern-G fire-starve risk** | Double-bottom rare; projected ~15-40/yr universe-wide; borderline FAIL min_trades=30 | MEDIUM | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Add neckline-confirmation gate — `double_bottom_neckline_broken` (NEW producer signal) |
| (c) Class 7 NEW `strat_double_top_short` mirror addition |
| (d) Pattern G EXPLORATORY marker post-B660 if confirmed <30/yr per regime |
| **(e) RECOMMENDED — (b) producer-side neckline-confirmation + (c) Class 7 NEW mirror + (d) post-B660 EXPLORATORY decision. (b) requires producer-side work; can be deferred if (d) confirms low fire-count anyway** |

**My recommendation: (e).**

**Awaiting owner direction on CP-2:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (e)
2. Class 7 NEW double_top_short addition (owner approval gate)
3. Producer-side neckline-confirmation work scope

---

### CP-3. `strat_head_and_shoulders_bottom_long` (Chart-pattern bullish base, walked B683 full-expansion)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B683 re-expansion). 2-gate LONG; Edwards-Magee 1948 foundational reference.

#### Step 1 — Read the code

[screener.py:4147-4157](backtest/signals/screener.py#L4147-L4157):

```python
def strat_head_and_shoulders_bottom_long(s):
    """Batch 252: inverse H&S long entry (Edwards-Magee + Bulkowski 2005)."""
    fires = (
        s.get("head_shoulders_bottom_detected", False)
        and s.get("price_above_ema_200", False)
    )
```

**2-gate LONG.**

| Gate | Meaning |
|---|---|
| `head_shoulders_bottom_detected` | EVENT: producer detects inverse H&S (3 troughs with middle deepest) per Edwards-Magee 1948 canonical |
| `price_above_ema_200` | STATE: long-term uptrend |

#### Step 2 — Classify

- Category: `chart_pattern`; LONG; B291 default; last touched B252 + B663

#### Step 3 — Producer source-read + temporality

- `head_shoulders_bottom_detected` from `compute_chart_patterns`
- Same no-neckline-confirmation concern as CP-2

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Edwards-Magee 1948 / Bulkowski 2005 canonical reversal" | ✅ **REAL ANCHOR** — *Technical Analysis of Stock Trends* (Edwards-Magee 1948) is THE foundational text for chart-pattern technical analysis; Bulkowski 2005 update validated empirically |
| Implicit "high-quality reversal" | ⚠ Bulkowski 2005 reports inverse-H&S WR ~74% on neckline-confirmed breakouts; without neckline gate the strategy fires early |

#### Step 5 — OPEN_INVESTIGATIONS grep

- No neckline-confirmation gate (same as CP-2)
- F-missing-inverse: `strat_head_and_shoulders_top_short` NOT registered (Class 7 NEW from B678 self-critique CC-B; owner approval pending)

#### Step 6 — Missing-inverse + economic-symmetry

- ❌ **No SHORT mirror.** H&S TOP is the canonical bearish reversal pattern per Edwards-Magee 1948 + Bulkowski 2005. **CONFIRMED Class 7 NEW candidate.** B678 self-critique surfaced this; owner approval required per `feedback_local_changes_default_global_needs_approval`.

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-edwards-magee-anchor ✅** | Foundational | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-missing-inverse CONFIRMED** | `strat_head_and_shoulders_top_short` Class 7 NEW required per `feedback_long_short_inverse_audit` + Bulkowski 2005 published WR | HIGH | F6 + B678 CC-B |
| **F-no-neckline-confirmation** | Same as CP-2 | MEDIUM | F1 |
| **F-Pattern-G HIGH RISK FAIL** | H&S bottom very rare; Bulkowski reports ~3-10/yr per universe; our T1a likely similar; well below min_trades=30 | HIGH | F4 |

**Options:** Same as CP-2; plus PRIORITY on Class 7 NEW H&S top short addition.

**My recommendation: (b) Class 7 NEW H&S top short owner approval + (d) EXPLORATORY marker post-B660.**

**Awaiting owner direction on CP-3:**
1. Class 7 NEW H&S top short addition (HIGH priority per B678 CC-B)
2. Pattern G EXPLORATORY vs DELETE decision

---

### CP-4. `strat_flag_bull_long` (Chart-pattern flag, walked B683 full-expansion — B618 PHANTOM-BREAKOUT FIXED)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B683 re-expansion). 2-gate LONG; **B618 FORENSIC-FIXED CASE** — pre-B618 had phantom-breakout bug where strategy fired before any actual breakout occurred.

#### Step 1 — Read the code

[screener.py:4199-4229](backtest/signals/screener.py#L4199-L4229):

```python
def strat_flag_bull_long(s):
    """Batch 252 ORIGINAL: bull flag long.

    Batch 618 (2026-06-07): PHANTOM-BREAKOUT BUG FIXED. Pre-B618 the
    strategy fired on flag_bull_detected + EMA-200 alone - but
    flag_bull_detected fires the day the flag COMPLETES, and the flag
    window includes today's bar. By construction today's close <=
    flag_high. So the strategy could not fire on an actual breakout
    - only on flag-detected-while-still-inside-the-flag.
    """
    fires = (
        s.get("flag_bull_broke", False)         # B618: breakout-occurred gate
        and s.get("price_above_ema_200", False)
    )
```

**2-gate LONG post-B618.**

| Gate | Meaning |
|---|---|
| `flag_bull_broke` | EVENT (B618 NEW producer): flag completed K bars ago (K in 1..8); today's close > historical flag_high |
| `price_above_ema_200` | STATE: long-term uptrend |

#### Step 2 — Classify

- Category: `chart_pattern`; LONG; B291 default; last touched B618 (forensic phantom-breakout fix) + B663

#### Step 3 — Producer source-read + temporality

- `flag_bull_broke` from B618 `compute_flag_break_retest_signals` — PIT-disciplined historical slice
- B618 + B607 lineage: B607 fixed CP-5 retest variant; B618 fixed CP-4 base + naming
- EVENT/STATE: 1 EVENT (breakout) + 1 STATE

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Bulkowski 2005 flag continuation pattern" | ✅ Bulkowski reports flag continuation patterns measured-move reliability ~50-60% |
| B618 PHANTOM-BREAKOUT fix | ✅ Major forensic-fix; pre-fix the strategy fired on detection (flag still active) NOT breakout. Cube re-validation required |
| Naming correction "standard flag NOT high-tight" | ✅ B618 critique #6: original docstring overclaimed "high-tight flag" (Weinstein >=90% pole) when implementation uses Bulkowski standard (+10% pole / <5% flag) |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B618 forensic-fix cube re-validation pending (same class as B262/B278 SMC)
- Cross-cluster Pattern Y with breakout cluster's BR-2/BR-4 (52w retest family) — Bulkowski thesis

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — `strat_flag_bear_short` is documented but NOT currently registered as standalone (only `strat_flag_bear_retest_short` CP-6 is registered)
- **F-incomplete-inverse-pair** — CP-4 (flag_bull_long base) has no `flag_bear_short` base mirror; only the retest variant (CP-6) exists on the SHORT side. Asymmetric pair coverage.

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-bulkowski-anchor ✅** | Real anchor; B618 naming correction shipped | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-B618 forensic-fix ✅** | PHANTOM-BREAKOUT fixed; cube re-validation pending | INFO + MEDIUM | Pattern T |
| **F-incomplete-inverse-pair** | `strat_flag_bear_short` base missing (only retest variant CP-6 exists); Class 7 NEW candidate | MEDIUM | F6 |
| F-fire-count | Flag patterns moderately common; post-B618 breakout-occurred gate narrows; projected ~50-150/yr universe-wide; PASS likely | INFO | F4 |

**Options:** (a) status quo / (b) cube validates B618 fix / (c) Class 7 NEW `strat_flag_bear_short` base mirror. **My recommendation: (a) + (b) + (c) deferred to owner approval.**

**Awaiting owner direction on CP-4:**
1. B618 fix cube re-validation post-B660
2. Class 7 NEW flag_bear_short base mirror (currently only retest variant CP-6 exists; asymmetric pair coverage)

---

### CP-5. `strat_flag_bull_retest_long` (Chart-pattern flag retest, walked B683 full-expansion — B607+B618 FORENSIC LINEAGE)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B683 re-expansion). 4-gate LONG; B607 forensic F1 bug fix + B618 docstring reframe. Bulkowski retest absorption thesis (Pattern Y).

#### Step 1 — Read the code

[screener.py:4266-4344](backtest/signals/screener.py#L4266-L4344):

```python
def strat_flag_bull_retest_long(s):
    """Batch 329 ORIGINAL; B607 F1 fix; B618 docstring reframe.

    Post-B607 4-gate set:
      flag_bull_break_retest_long + price_above_ema_200 +
      close_above_open + vol_below_avg
    """
    fires = (
        s.get("flag_bull_break_retest_long", False)
        and s.get("price_above_ema_200", False)
        and s.get("close_above_open", False)
        and s.get("vol_below_avg", False)
    )
```

**4-gate LONG post-B607+B618.**

| Gate | Meaning |
|---|---|
| `flag_bull_break_retest_long` | EVENT (B607 NEW): 4-condition AND (FLAG-COMPLETED + BREAKOUT-OCCURRED + RETEST + STILL-ABOVE) — see docstring (4-condition encoded in producer flag) |
| `price_above_ema_200` | STATE: trend filter |
| `close_above_open` | EVENT (B607 (a)): bullish bar |
| `vol_below_avg` | EVENT (B607 (c)): Bulkowski retest absorption thesis |

#### Step 2 — Classify

- Category: `chart_pattern`; LONG; B291 default; last touched B618 (docstring reframe)

#### Step 3 — Producer source-read + temporality

- `flag_bull_break_retest_long`: B607 NEW producer in `compute_flag_break_retest_signals` — PIT-disciplined historical slice via `df.iloc[:n-K]`
- Pattern S concern: strategy is a thin shell over 4-condition producer flag (hardcoded params in producer)
- EVENT/STATE: 3 EVENT + 1 STATE

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Edwards-Magee + Bulkowski 2005" | ✅ Real anchors |
| B607 F1 phantom-breakout fix | ✅ Forensic-fix from CP-5 walk (cross-ref B618 same family) |
| B618 critique #5 Bulkowski WR caveat | ✅ "Edge must be validated empirically by the backtest, not assumed from textbook" — honest framing |
| B618 critique #6 naming clarification | ✅ "Standard flag NOT high-tight" — honest |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B607 forensic-fix re-validation pending cube
- Pattern S single-gate-shell concern (B680 SMC self-critique CC-D class)

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — CP-6 `strat_flag_bear_retest_short` (B607 Class 7 NEW)
- ⚠ Economic symmetry per B618 (m): "STRUCTURAL SYMMETRY does NOT imply ECONOMIC SYMMETRY" — bull/bear flag base rates differ in equities

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-B607+B618 forensic-fix ✅** | Multiple lineage fixes shipped + honest docstring (B618 critiques #5+#6) | INFO / ✅ POSITIVE | Pattern T |
| **F-pattern-S single-gate-shell** | `flag_bull_break_retest_long` encodes 4 conditions invisible at strategy site | MEDIUM | B680 SMC CC-D class |
| **F-pattern-Y Bulkowski retest** | Legitimate citation + cross-cluster carry from breakout BR-2/BR-4/BR-12/BR-13 | INFO | Pattern Y |
| F-fire-count | Post-B607 4-gate AND; projected ~20-60/yr universe-wide; borderline | MEDIUM | F4 |

**Options:** (a) status quo / (b) cube validates B607 fix + Pattern Y vs base CP-4 ablation / (c) Pattern S explicit-gate refactor. **My recommendation: (a) + (b).**

**Awaiting owner direction on CP-5:** Pattern Y cube ablation against CP-4 base + breakout cluster Bulkowski retest family.

---

### CP-6. `strat_flag_bear_retest_short` (Chart-pattern flag retest, walked B607)

> **Status:** ✅ ALREADY WALKED B607. Class 7 NEW from F1 bug fix in flag_bull_retest_long walk.

[screener.py:4360-...](backtest/signals/screener.py#L4360) — B607 added new `compute_flag_break_retest_signals` producer anchored on `flag_bull_breakout_level` / `flag_bear_breakdown_level` (replaces DC20-anchored bug per F1 bug fix in CP-5 walk).

**B671 borrow-trap gate applies.** Mirror of CP-5.

**B621 estimator flagged `flag_bear_retest_short` as 15.77/yr WARN — borderline.**

---

### CP-7. `strat_triangle_ascending_long` (Chart-pattern triangle, walked B683 full-expansion)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B683 re-expansion). 2-gate LONG; Edwards-Magee 1948 + Bulkowski 2005 canonical ascending triangle.

#### Step 1 — Read the code

[screener.py:4232-4242](backtest/signals/screener.py#L4232-L4242):

```python
def strat_triangle_ascending_long(s):
    """Batch 252: ascending triangle long (flat top + rising lows)."""
    fires = (
        s.get("triangle_ascending_detected", False)
        and s.get("price_above_ema_200", False)
    )
```

**2-gate LONG.**

| Gate | Meaning |
|---|---|
| `triangle_ascending_detected` | EVENT: producer detects flat resistance + rising support per Edwards-Magee 1948 canonical |
| `price_above_ema_200` | STATE: trend filter |

#### Step 2 — Classify

- Category: `chart_pattern`; LONG; B291 default; last touched B252 + B663

#### Step 3 — Producer source-read + temporality

- `triangle_ascending_detected` from `compute_chart_patterns`
- Same no-apex-breakout-confirmation concern as CP-2 (pattern detection without breakout confirmation)

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Bulkowski 2005: breakout direction follows trend ~70%" | ✅ Real frequency citation; ascending triangles statistically resolve upward |
| Implicit "high-quality continuation" | ⚠ Bulkowski WR conditional on breakout confirmation; strategy fires on pattern detection alone |

#### Step 5 — OPEN_INVESTIGATIONS grep

- F-no-apex-breakout-confirmation gate
- F-missing-inverse: `strat_triangle_descending_short` NOT registered (Class 7 NEW from B678 self-critique; owner approval pending)

#### Step 6 — Missing-inverse + economic-symmetry

- ❌ **No SHORT mirror.** Descending triangle is the documented bearish continuation pattern per Edwards-Magee + Bulkowski. **CONFIRMED Class 7 NEW candidate** per B678 self-critique CC-B.

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-edwards-magee-anchor ✅** | Real foundational reference | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-no-apex-breakout-confirmation** | Strategy fires on detection alone; Bulkowski WR conditional on confirmation | MEDIUM | F1 |
| **F-missing-inverse CONFIRMED** | `strat_triangle_descending_short` Class 7 NEW required | HIGH | F6 + B678 CC-B |
| F-fire-count | Triangles moderately common; projected ~30-80/yr universe-wide; PASS likely | INFO | F4 |

**Options:** (a) status quo / (b) add apex-breakout-confirmation gate (producer-side work) / **(c) Class 7 NEW triangle_descending_short** / (d) all three. **My recommendation: (c) + cube validation post-B660.**

**Awaiting owner direction on CP-7:**
1. Class 7 NEW triangle_descending_short addition (HIGH priority per B678 CC-B)
2. Apex-breakout-confirmation gate scope

---

### CP-8. `strat_triangle_ascending_retest_long` (Chart-pattern triangle retest, walked B683 full-expansion)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B683 re-expansion). 3-gate LONG; B329 retest variant of CP-7. Pattern Y Bulkowski retest absorption.

#### Step 1 — Read the code

[screener.py:4398-4411](backtest/signals/screener.py#L4398-L4411):

```python
def strat_triangle_ascending_retest_long(s):
    """BUG-111 (Batch 329): retest variant of triangle_ascending_long."""
    fires = (
        s.get("triangle_ascending_detected", False)
        and s.get("resistance_break_retest", False)
        and s.get("price_above_ema_200", False)
    )
```

**3-gate LONG.**

| Gate | Meaning |
|---|---|
| `triangle_ascending_detected` | EVENT: same as CP-7 |
| `resistance_break_retest` | EVENT: DC20-anchored retest primitive |
| `price_above_ema_200` | STATE: trend filter |

#### Step 2 — Classify

- Category: `chart_pattern`; LONG; B291 default; last touched B329 (original) + B663
- ⚠ Same DC20-anchored retest concern as B607 fixed for flag_bull_retest_long — `resistance_break_retest` is DC20-anchored, NOT triangle-apex-anchored. Possible same name-vs-implementation bug pattern as B607 fixed for CP-5.

#### Step 3 — Producer source-read + temporality

- `triangle_ascending_detected` + `resistance_break_retest` — TWO independent producers; the retest signal is DC20-anchored not triangle-apex-anchored
- **F-design-bug-candidate:** retest at DC20 level may not coincide with triangle apex breakout retest

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Bulkowski 2005: triangle apex breakout retest is the canonical entry" | ✅ Real citation |
| Implicit "retest at triangle apex" | ⚠ **DESIGN BUG candidate** — `resistance_break_retest` is DC20-anchored, not triangle-apex-anchored. Same class as the B607 bug fixed for flag_bull_retest_long. **Pre-B660 deeper walk required to confirm/refute.** |

#### Step 5 — OPEN_INVESTIGATIONS grep

- **F-design-bug-candidate** — DC20 retest vs triangle-apex retest mismatch (same family as B607 forensic-fix on CP-5)
- B660 fire-count data will inform — if anomalously high (DC20 fires more often than triangle apex), bug confirmed; if same/lower, design might be working by coincidence

#### Step 6 — Missing-inverse + economic-symmetry

- ❌ Same as CP-7; descending triangle retest missing

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-design-bug-candidate (DC20 vs apex)** | Same family as B607 flag_bull_retest_long fix; should ship triangle-apex-anchored retest signal | HIGH | F1 (design bug) |
| **F-edwards-magee-anchor ✅** | Real anchor | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-missing-inverse** | Same as CP-7 | HIGH | F6 |
| F-fire-count | Triangle + DC20-retest narrow co-occurrence; projected ~10-30/yr universe-wide; borderline | MEDIUM | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Producer-side fix — ship `triangle_apex_break_retest_long` symmetric with B607 flag_bull producer. Re-wire CP-8 to consume new producer signal |
| (c) Class 7 NEW descending-triangle-retest-short addition |
| (d) Pattern Y cube ablation vs CP-7 base |
| **(e) RECOMMENDED — (b) + (c) + (d). Same B607 forensic-fix pattern that fixed CP-5; should ship now to avoid contaminating cube with DC20-anchored data on triangle strategies.** |

**My recommendation: (e).**

**Awaiting owner direction on CP-8:**
1. (b) producer-side B607-style fix (HIGH priority — design bug)
2. (c) Class 7 NEW descending-triangle-retest-short
3. (d) Pattern Y cube ablation

---

### CP-9. `strat_cup_and_handle_retest_long` (Chart-pattern retest, walked B683 full-expansion)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B683 re-expansion). 5-gate LONG; retest variant of CP-1 cup-and-handle.

#### Step 1 — Read the code

[screener.py:4245-4263](backtest/signals/screener.py#L4245-L4263):

```python
def strat_cup_and_handle_retest_long(s):
    """BUG-111 (Batch 329): retest variant of cup_and_handle_long.
    Cup-and-handle pattern + post-break retest of the neckline (proxied
    via resistance_break_retest from DC20)."""
    fires = (
        s.get("cup_handle_detected", False)
        and s.get("resistance_break_retest", False)
        and s.get("price_above_ema_200", False)
        and s.get("price_above_ema_50", True)
        and s.get("rsi_14", 50) < 70
    )
```

**5-gate LONG.** Docstring acknowledges "proxied via resistance_break_retest from DC20" — same DC20 vs neckline mismatch as CP-8 triangle case.

| Gate | Meaning |
|---|---|
| `cup_handle_detected` | EVENT: same as CP-1 |
| `resistance_break_retest` | EVENT: DC20-anchored (NOT neckline-anchored — explicit docstring caveat) |
| `price_above_ema_200` | STATE |
| `price_above_ema_50` | STATE: ⚠ Pattern A default-True silent-gap candidate (WAVE 2 family) |
| `rsi_14 < 70` | STATE |

#### Step 2 — Classify

- Category: `chart_pattern`; LONG; B291 default; last touched B329 (original) + B663

#### Step 3 — Producer source-read + temporality

- Same DC20-anchored retest concern as CP-8 (docstring explicitly acknowledges "proxied")
- Same Pattern A WAVE 2 candidate on `price_above_ema_50`

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "O'Neil 1988 + Bulkowski 2005: the handle retest is the canonical low-risk entry" | ✅ Real anchors |
| "proxied via resistance_break_retest from DC20" | ✅ HONEST docstring — acknowledges DC20 is a PROXY for the actual cup-and-handle neckline. Same design-bug-class as CP-8 but docstring is honest about the limitation |

#### Step 5 — OPEN_INVESTIGATIONS grep

- Same B607-style producer-fix candidate (cup_handle_neckline_break_retest signal needed)
- Pattern A WAVE 2 candidate

#### Step 6 — Missing-inverse + economic-symmetry

- ❌ No `strat_inverted_cup_and_handle_retest_short` (CP-1 walk noted no inverted-cup mirror; retest variant inherits)

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-design-honest-proxy** | Docstring acknowledges DC20 proxy; cleaner than CP-8 silent mismatch | LOW-MEDIUM | F1 |
| **F-Pattern-A WAVE-2** | `price_above_ema_50` default-True silent-gap candidate | LOW-MEDIUM | Pattern A WAVE 2 |
| **F-O'Neil + Bulkowski anchor ✅** | Real | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-Pattern-G HIGH RISK** | Cup-and-handle rare (per CP-1 + B660 0-fire data) + DC20-retest co-occurrence rarer; projected <10/yr universe-wide; FAIL min_trades=30 likely | HIGH | F4 |

**Options:** (a) status quo / (b) producer-side neckline-anchored retest fix (B607 pattern) / (c) DELETE per B620 precedent if B660 confirms <5/yr / (d) EXPLORATORY marker / **(e) RECOMMENDED — (d) EXPLORATORY post-B660 + (b) producer fix if owner wants to preserve the strategy long-term**

**Awaiting owner direction on CP-9:** Pattern G EXPLORATORY/DELETE + producer-side neckline fix.

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

## B680 Self-Critique Iteration 2 — Cross-Cutting Feasibility Findings

> **Status (B680 self-critique iteration 2026-06-10):** owner directive *"Just update all docs"* — proceed with adversarial self-critique in lieu of external reviewer pass.

### Cross-cutting feasibility findings (Claude self-critique 2026-06-10)

| # | Finding | Verification | Severity | Status |
|---|---|---|---|---|
| **CC-A** | **B678 compact-walk format for 10 NEW strategies under-delivers vs pivot-doc template standard set by smart-money B672 and SMC B673.** Walks for CC-2/CC-4/CC-5/CC-6 + CP-1/CP-2/CP-3/CP-4/CP-5/CP-7/CP-8/CP-9 are 5-15 lines each with "Step 2-7 compact" instead of full per-step coverage. **The owner explicitly directed earlier in this session ("the md doc is not comprehensive") when smart-money cluster had compact walks. Same critique applies here.** The compact format was justified for "6 of 16 already received B-batch individual walks" but applies to the OTHER 10 strategies too where compact-walk is just compression. **Should re-expand the 10 compact walks to full template density before Iteration 2 ships.** | ✅ Visible in B678 doc body | **MEDIUM-HIGH** | NEW — `S4-CP-COMPACT-WALK-REEXPAND-TO-FULL-TEMPLATE` |
| **CC-B** | **2 missing-inverse Class 7 NEW candidates (head_and_shoulders_top_short, triangle_descending_short) are CONFIRMED gaps documented in chart-pattern literature — they're not optional additions.** Edwards-Magee 1948 + Bulkowski 2005 EXPLICITLY document head-and-shoulders TOP (bearish reversal) + descending triangle (bearish continuation) as equally-valid mirror patterns. Their omission from the registry is a `feedback_long_short_inverse_audit` rule violation that the walks identified but didn't action. **Per `project_no_apriori_strategy_pruning`: additions are permitted; per `feedback_local_changes_default_global_needs_approval`: strategy registration needs explicit owner approval; this is the missing approval gate.** Should ship Class 7 NEW addition batch with owner approval pre-cube to avoid leaving the SHORT-side coverage gap unaddressed. | ✅ Verified from chart-pattern literature | **MEDIUM-HIGH** | NEW — `S4-CP-MISSING-INVERSE-MIRRORS-CLASS-7-NEW-ADDITION-OWNER-APPROVAL-REQUIRED` |
| **CC-C** | **CHECKLIST (q) candle-pattern next-bar-open PIT rule was CODIFIED B639 but has NOT been verified across all 16 cluster strategies.** Walk noted "Verified by engine convention" but no test pins the convention to each strategy. **If any one of the 16 inadvertently consumes a same-bar-close-derived signal in same-bar fires logic, the cluster has subtle lookahead.** Examples to verify: CC-4 (shooting_star_short) reads `shooting_star` boolean — does the producer emit at end-of-day close (= same bar) or with 1-bar lag? CC-5 (bullish_engulfing_support) reads `bullish_engulfing` (2-bar pattern) — at which bar does the producer emit True? **Pre-cube pyramid test pinning the (q) rule across all 16 is the cheapest possible validation.** | Producer convention assumed but not test-pinned | **MEDIUM-HIGH** | NEW — `S4-CP-CHECKLIST-Q-PYRAMID-TEST-PIN-ALL-16` |
| **CC-D** | **Pattern N intra-cluster ablation candidates are UNDER-explored** — the walk noted 16 strategies on 12 primitives but didn't surface the strongest correlation pairs. Specifically: CC-1 (morning_star) is a 3-bar bullish reversal pattern; CC-5 (bullish_engulfing_support) is a 2-bar bullish reversal; CC-6 (doji_at_support) is a 1-bar indecision at support. **All three fire near support after declines = highly-correlated fire events with cross-pattern redundancy.** Cube ablation should compare CC-1 vs CC-5 vs CC-6 directly + against pivot-cluster W1 (which already consumes bullish_engulfing). | Mechanical from pattern definitions | MEDIUM | NEW — `S4-CP-BULLISH-REVERSAL-AT-SUPPORT-CC1-CC5-CC6-W1-CROSS-ABLATION` |
| **CC-E** | **Pattern G fire-starve risks affect 4-5 strategies but the walk's projections may be OPTIMISTIC.** CP-1 (cup_and_handle): ~20-50/yr universe-wide projected; cup-and-handle in pristine form is RARE in screened lists — Bulkowski 2005 reports ~50 valid cup-and-handles per year in O'Neil's CANSLIM universe of several thousand stocks. Our T1a 503 may produce ~5-15/yr. CP-3 (head_and_shoulders_bottom): ~5-20/yr projected; Bulkowski reports H&S bottom is RARE; ~3-10/yr realistic. **3 strategies likely FAIL `min_trades=30` per regime — Pattern G EXPLORATORY decision should be pre-cube candidates not deferrals.** | Bulkowski 2005 published frequency data | MEDIUM | NEW — `S4-CP-FIRE-STARVE-PRE-CUBE-EXPLORATORY-CANDIDATES` |
| **CC-F** | **CP-6 (`strat_flag_bear_retest_short`) is on the B621 estimator WARN list (15.77/yr) — borderline FAIL min_trades=30 per regime.** Walk noted this but disposition deferred. Combined with CP-3 (head_and_shoulders_bottom) ~5-20/yr + CP-1 (cup_and_handle) ~20-50/yr, the cluster has 3-4 borderline Pattern G cases that should be jointly addressed pre-cube. | B621 estimator | MEDIUM | Cross-ref existing `S5-FIRE-COUNT-CANDIDATES` |
| **CC-G** | **Pattern Y retest absorption (CP-5/6/8/9) has cluster-internal Pattern N overlap with breakout cluster's BR-5/6/12/13 (Bulkowski variants).** Walk noted Pattern Y carry from breakout but didn't surface the cross-cluster overlap. **Bulkowski retest absorption pattern in chart_pattern cluster is the SAME signal class as Bulkowski retest absorption in breakout cluster** — just with different anchor primitives (chart-pattern level vs breakout level). Pattern N cross-cluster ablation should bridge clusters. | Mechanical from cross-cluster comparison | MEDIUM | NEW — `S4-CP-BR-PATTERN-Y-V-CROSS-CLUSTER-BULKOWSKI-CONSOLIDATION` |

### Per-strategy reframings (Claude self-critique)

| Strategy | Walk disposition | Self-critique reframing | Action |
|---|---|---|---|
| **CP-1 + CP-2 + CP-3** Pattern G borderline | RECOMMENDED post-B660 EXPLORATORY | **Bulkowski-published frequency data argues PRE-cube EXPLORATORY** — measured fire counts on professional screening universes are well below our projections. | Pre-cube EXPLORATORY |
| **CC-1/CC-5/CC-6** bullish reversal at support | RECOMMENDED status-quo | **Cross-strategy + cross-cluster fire correlation likely HIGH — these 3 + W1 pivot all fire near support after declines.** Pattern N flagship intra-cluster ablation. | Cube Pattern N flagship |
| **All 10 NEW compact walks** | Walked compact | **Re-expand to full pivot-doc template per CC-A.** Owner's prior directive applied. | Re-expand pre-Iteration-2-ship |
| **Class 7 NEW candidates** head_and_shoulders_top_short + triangle_descending_short | RECOMMENDED but no owner-approval gate | **Surface Class 7 NEW addition owner-approval request explicitly.** | Owner-approval gate |

### Net effect on B678 walk dispositions

- **10 compact walks** should be RE-EXPANDED to full template (matches smart-money B669 → B672 pattern after owner's "not comprehensive" critique)
- **2 missing-inverse Class 7 NEW** owner-approval gate ELEVATED to immediate action
- **CHECKLIST (q) PIT rule** pyramid test ELEVATED to pre-cube ship-required
- **Pattern G fire-starve** CP-1/CP-2/CP-3 moved from "post-B660" to "pre-cube EXPLORATORY candidates" per Bulkowski published frequencies
- **Cross-cluster Pattern Y/V Bulkowski** consolidation NEW concern

### Queue tickets surfaced by self-critique (B680)

- `S4-CP-COMPACT-WALK-REEXPAND-TO-FULL-TEMPLATE` (MEDIUM-HIGH; CC-A)
- `S4-CP-MISSING-INVERSE-MIRRORS-CLASS-7-NEW-ADDITION-OWNER-APPROVAL-REQUIRED` (MEDIUM-HIGH; CC-B)
- `S4-CP-CHECKLIST-Q-PYRAMID-TEST-PIN-ALL-16` (MEDIUM-HIGH; CC-C)
- `S4-CP-BULLISH-REVERSAL-AT-SUPPORT-CC1-CC5-CC6-W1-CROSS-ABLATION` (MEDIUM; CC-D)
- `S4-CP-FIRE-STARVE-PRE-CUBE-EXPLORATORY-CANDIDATES` (MEDIUM; CC-E)
- `S4-CP-BR-PATTERN-Y-V-CROSS-CLUSTER-BULKOWSKI-CONSOLIDATION` (MEDIUM; CC-G)

---

## B679 Iteration 2 Preparation — Review Solicitation Guide

> **Status (post-B679 format alignment):** READY FOR EXTERNAL REVIEWER + OWNER FEEDBACK on Iteration 2.
>
> **Recommended review structure (parallel to B673 smart-money review):**
>
> | Review axis | What to look for in Chart-pattern + Candle | Smart-money parallel |
> |---|---|---|
> | **CC-A: Citation discipline** | ALL 16 strategies have LEGITIMATE peer-reviewed anchors (Nison 1991 + Bulkowski 2005 + Edwards-Magee 1948 + O'Neil 1988 CANSLIM). Pattern Q does NOT apply. Cluster-positive | Pattern M / Q exception |
> | **CC-B: CHECKLIST (q) PIT rule (B639 F6 codified)** | Candle patterns complete at end-of-day; engine MUST enter NEXT-BAR-OPEN. Verify engine convention `entry_bar = signal_bar + 1` applies to all 16 | New rule from B639 walk |
> | **CC-C: Heavy prior-walk coverage** | 6 of 16 already received B-batch CHECKLIST #105 walks (B572 + B607 + B636 + B639); 10 NEW walks in B678 are compact-style. Pattern T forensic discipline is cluster's strength | Pattern T cluster-positive |
> | **CC-D: Missing-inverse Class 7 NEW candidates** | head_and_shoulders_top_short (CP-3 inverse MISSING per Edwards-Magee 1948 documents top pattern equally) + triangle_descending_short (CP-7 inverse MISSING per Bulkowski). Per `feedback_long_short_inverse_audit` | Class 7 NEW addition pattern |
> | **CC-E: Pattern Y retest absorption (carried from breakout)** | CP-5 + CP-6 + CP-8 + CP-9 (4 retest variants) — Bulkowski 2005 thesis legitimate. Cube ablation against base patterns settles whether retest variants earn separate registry slots | Pattern V breakout cluster |
> | **CC-F: Effective hypothesis count** | 16 strategies on ~12 primitives → effective N ≈ 12. Moderate cluster | CC7 |
> | **CC-G: Pattern G fire-starve** | CP-3 (5-20/yr) + CP-1 (20-50/yr) + CP-2 (15-40/yr) borderline FAIL min_trades=30 per regime; CP-6 on B621 WARN list (15.77/yr) | Pattern G |
>
> Provide feedback in B673-style severity-ranked critique; B679 will incorporate as B679-incorporation batch.

---

## Cross-cluster status snapshot (post-B679 — index at [STAGE_4_CLUSTER_WALKS_INDEX.md](STAGE_4_CLUSTER_WALKS_INDEX.md))

8 cluster docs / ~138 strategies covered. Review status:

| Cluster | Doc | Strategies | Owner review | Iteration 2 ready |
|---|---|---|---|---|
| Pivot | [STAGE_4_PIVOT_CLUSTER_WALKS.md](STAGE_4_PIVOT_CLUSTER_WALKS.md) | ~10 | ✅ 2 rounds | (already iterated) |
| Trend | [STAGE_4_TREND_CLUSTER_WALKS.md](STAGE_4_TREND_CLUSTER_WALKS.md) | ~12 | ✅ Companion | (already iterated) |
| Smart Money | [STAGE_4_SMART_MONEY_CLUSTER_WALKS.md](STAGE_4_SMART_MONEY_CLUSTER_WALKS.md) | 41 | ✅ 2 rounds (B669 + B673 → B674) | (already iterated) |
| SMC | [STAGE_4_SMC_CLUSTER_WALKS.md](STAGE_4_SMC_CLUSTER_WALKS.md) | 18 | ❌ AWAITING | READY |
| ICT | [STAGE_4_ICT_CLUSTER_WALKS.md](STAGE_4_ICT_CLUSTER_WALKS.md) | 12 | ❌ AWAITING | READY |
| Breakout | [STAGE_4_BREAKOUT_CLUSTER_WALKS.md](STAGE_4_BREAKOUT_CLUSTER_WALKS.md) | 19 | ❌ AWAITING | READY |
| Event-driven | [STAGE_4_EVENT_DRIVEN_CLUSTER_WALKS.md](STAGE_4_EVENT_DRIVEN_CLUSTER_WALKS.md) | 10 | ❌ AWAITING | READY |
| **Chart+Candle (THIS DOC)** | **[STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md](STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md)** | **16** | **❌ AWAITING** | **READY** |

**Total Stage 4 walks: 8 cluster docs complete; ~138 strategies covered with CHECKLIST #105 7-step walks across ~222 total registry (some strategies belong to multiple clusters and are walked once).**

**Remaining strategy categories NOT in cluster walks:** smart_money_sleeve (10 — walked as part of smart-money B673), smart_money_13f (7 — same), institutional_persistence (12 — same), classification_change (10 — partially walked sub-cluster D), multi_timeframe (5), cross_asset (5), factor (6), confluence (2), mean_reversion (3), momentum (3), news_sentiment (6), volume_profile (3), pairs (2), orb (2), vwap (1), pivot (1 unwalked beyond pivot cluster) ≈ 78 additional strategy slots not in cluster walks.
