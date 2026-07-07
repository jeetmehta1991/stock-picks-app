# Stage 4 — Trend Confluence & Chart-Pattern Residual Cluster Walks

> **B1029 STATUS BANNER 2026-06-27 doc-sync:** ALL WALKS 1-5 41-of-41 RESOLVED B984-B993 per CLAUDE.md banner. Cluster walks across 220 strategies CLOSED (B722 -3 + B874 -2 + B1010 +1 = 220 / 217 active). R5 LAUNCHED 2026-06-27 B1028 on AWS i-0940a53c75d049381 (Master 1929 ops x 4y window 2022-05-05 to 2026-05-05). Banners below indicating PENDING/RUNNING/DEFER status from B691-B750-era are HISTORICAL.


> **B750 STATUS BANNER (2026-06-14) — CLUSTER B SCAFFOLDING + INITIAL WALKS.**
>
> This is the SECOND of three new cluster docs from B750-B762 closing the Stage 4 walk-coverage gap. Owner-confirmed scope per "approve all" 2026-06-14: 3 clusters of 30/33/33 = 96 previously-unwalked strategies. This doc covers **Cluster B = Trend Confluence & Chart-Pattern Residual (33 strategies)**.
>
> **Source of truth:** commit `86f7d76c0` (HEAD as of B750 2026-06-14 09:43 UTC). Roster pinned at `len(ALL_STRATEGIES) = 221`. Unwalked-set derivation per Cluster A B750 banner discipline (header-strict walk-section grep).
>
> Same disciplines as Cluster A apply: CHECKLIST #105 (producer source-read mandatory), `feedback_walk_step3_must_read_producer_source`, `feedback_no_rushing_per_strategy_tweak`, `feedback_minimum_fire_count_gate_before_cube`. Patterns A/F/G/J/N/Q/S/T/W carried from Cluster A + prior clusters.
>
> **Sequencing notes:** B750 ships framework + 3 sample walks (B-3 golden_cross_50_200 + B-13 supertrend_ichimoku_adx + B-29 xs_low_beta_long). Remaining 30 walks ship in B754-B757 at 5-10 per batch.

---

## Audience

### 1. External reviewer (Cluster-B-specific differentiators)

If you've reviewed Cluster A, the things that will be different here:

1. **Cluster B is heterogeneous by design.** Cluster A had a single dominant theme (timing indicators / oscillators). Cluster B splits across (a) MA-cross + trend-confluence, (b) multi-timeframe alignment, (c) factor / cross-sectional strategies, (d) chart-pattern Class 7 NEW additions, (e) pivot-confluence residuals. The cluster is unified by "non-oscillator, non-event" residuals rather than a single mechanism.

2. **Factor/cross-sectional sub-cluster (B.10) is structurally different.** The `xs_*` strategies (xs_low_beta_long, xs_momentum_*) consume CROSS-SECTIONAL signals computed at universe-level (rank-based deciles), not per-ticker technical signals. Producer is `cross_sectional.py`, not `technical.py`. Per B716 measurement gap, these strategies require `cross_sectional.compute_cross_sectional_features` per-as_of producer wireup which is part of B690 TIER 2 harness work. Likely measurement-blocked pre-B690b.

3. **Chart-pattern Class 7 NEW sub-cluster (B.9) was added in B685+B686.** These 4 strategies (hammer_at_support_long, head_and_shoulders_top_short, triangle_descending_short, inverted_cup_and_handle_short) were registered as inverse mirrors per `feedback_long_short_inverse_audit` but were NEVER cluster-walked. Their producers (chart_patterns.py + new producer for inverted cup) live with the existing Chart+Candle cluster walks. Cluster B includes them per "unwalked = anywhere" rule.

4. **Pattern T (MA-cross redundancy with EMA-trend gate) is the dominant pattern.** 5 of the 6 MA-cross strategies layer a 50-SMA or 200-EMA trend gate on top of the MA-cross signal. This collinear gate is the #1 marginal-contribution candidate for Pattern J consolidation post-B690b.

5. **Pattern J consolidation expected to be aggressive.** MA-cross variants (5 strategies) → likely 1 underlying primitive + parameter sweep. Factor variants (6 strategies) → likely 2-3 underlying factor combinations. Total Cluster B 33 → ~15-18 effective primitives post-J.

### 2. Future readers

Cluster B captured the "trend/factor/pattern residuals" that didn't fit the existing 8 cluster docs because they're heterogeneous individually but coherent as a "non-oscillator non-event" residual. The factor sub-cluster (B.10) is the most likely to spawn its own cluster doc in the future — once cross_sectional.py producer wireup completes via B690, the 6 factor strategies + any new BAB/quality/value additions could justify a separate "Factor & Cross-Sectional" cluster doc post-cube.

---

## Methodology adaptations for the Trend Confluence & Chart-Pattern Residual cluster

### M1 — MA-cross variants vs single underlying signal

MA-cross strategies (golden_cross_9_21, _20_50, _50_200, _volume) all consume the same underlying producer logic (`compute_ema_crosses`). Each variant differs only in the EMA pair (9/21, 20/50, 50/200) and any added gates (volume confirmation, trend gate). Pattern J disposition options:

- (a) DELETE-WRAPPERS: keep one canonical MA-cross strategy + cube parameter-sweep on EMA pair
- (b) CONSOLIDATE: collapse to 1 strategy + parameter
- (c) RETAIN-AS-VARIANTS: if measurement shows distinct alpha across timescales

### M2 — Confluence strategies as gate-stacking

Strategies like supertrend_ichimoku_adx, macd_ichimoku, break_retest_confluence stack 3+ trend-confluence gates. Per `feedback_minimum_fire_count_gate_before_cube`: 3+ gates dramatically reduce fire rate. Walks compute a-priori fire-count projection per strategy.

### M3 — Multi-timeframe strategies use weekly/monthly producer

monthly_bias_momentum_long, weekly_bias_pullback_long/short, htf_aligned_breakout_long/short consume multi_timeframe.py producer (resampled weekly/monthly bars). Per B689 harness re-run, multi_timeframe was wired into the precompute. Producer-PIT discipline: weekly/monthly resample MUST be backward-looking (close of week N for week N's data, not week N+1).

### M4 — Factor strategies require cross_sectional.py producer

`xs_*` strategies require per-as_of universe-level rank computation. Per B716: cross_sectional.compute_cross_sectional_features needs full OHLCV dict + as_of refactor as part of B690 TIER 2 harness. Walks document the measurement blocker; strategy-level analysis still proceeds.

### M5 — Chart-Pattern Class 7 NEW (B.9) inherits Chart+Candle cluster methodology

The 4 chart-pattern Class 7 NEW strategies share producer methodology with the existing Chart+Candle cluster (chart_patterns.py + cluster-doc B678). Walks cross-reference STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md Pattern Y (Bulkowski retest absorption) where applicable.

### M6 — Pattern T (MA-cross + trend-gate collinearity) is the new cluster signature

Pattern T concern: if a strategy fires `ema_50_200_golden_cross` AND ALSO requires `price_above_ema_200`, the golden cross itself implies price is above 200-EMA most of the time (mathematically: if 50-EMA crosses above 200-EMA, price is typically above 200-EMA). The trend gate is collinear with the crossover signal; marginal information ≈ 0.

Walks compute a-priori collinearity per strategy. Cube post-B690b empirically measures via gate-correlation diagnostic.

---

## Reviewer findings response matrix

> Pre-emptive placeholder per B750 Cluster A pattern.

| Reviewer round | Findings | Response | Batch |
|---|---|---|---|
| _Pending_ | Awaiting external reviewer pass on B750 framework + sample walks | — | OPEN |

---

## Cluster scope inventory (33 strategies)

| Sub-family | Count | Strategies |
|---|---|---|
| **B.1 MA-Cross** | 5 | `golden_cross_9_21` (dual), `golden_cross_20_50` (dual), `golden_cross_50_200` (dual), `golden_cross_volume` (dual), `death_cross_50_200_volume` (short) |
| **B.2 EMA-50 + Volume** | 2 | `simple_below_ema_50_short`, `vol_spike_2x_below_ema_50_short` |
| **B.3 Ichimoku confluence** | 3 | `ichimoku_cloud_breakdown` (short), `supertrend_ichimoku_adx` (dual), `macd_ichimoku` (dual) |
| **B.4 MACD short** | 2 | `macd_crossover_short`, `supertrend_macd_short` |
| **B.5 Multi-Timeframe** | 5 | `monthly_bias_momentum_long`, `weekly_bias_pullback_long`, `weekly_bias_pullback_short`, `htf_aligned_breakout_long`, `htf_aligned_breakout_short` |
| **B.6 Squeeze** | 1 | `squeeze_setup_long` |
| **B.7 Pivot-confluence** | 3 | `pivot_fib_confluence` (dual), `prev_day_high_break` (long), `r1_break_retest` (dual) |
| **B.8 Break-retest confluence** | 1 | `break_retest_confluence` (dual) |
| **B.9 Chart-Pattern Class 7 NEW** | 4 | `hammer_at_support_long` (B685), `head_and_shoulders_top_short` (B685), `inverted_cup_and_handle_short` (B686), `triangle_descending_short` (B685) |
| **B.10 Factor / Cross-Sectional** | 6 | `xs_low_beta_long`, `xs_combined_momentum_low_ivol`, `xs_momentum_top_decile`, `xs_momentum_bottom_decile_short`, `xs_momentum_quality_combined`, `xs_quality_top_quintile_long` |
| **B.11 Macro headwind (DISABLED)** | 1 | `dxy_headwind_multinational_short` (DISABLED-MISSING-PRODUCER per CLAUDE.md) |

Sub-family count = 5+2+3+2+5+1+3+1+4+6+1 = 33 ✓

**Direction split:**
- LONG-only: ~10 (hammer_at_support, htf_aligned_breakout_long, monthly_bias_momentum, prev_day_high_break, squeeze_setup, weekly_bias_pullback_long, xs_low_beta, xs_combined_momentum, xs_momentum_top, xs_quality)
- SHORT-only: ~12 (death_cross_50_200_volume, simple_below_ema_50, vol_spike_2x_below_ema_50, ichimoku_cloud_breakdown, macd_crossover_short, supertrend_macd_short, head_and_shoulders_top_short, triangle_descending_short, inverted_cup_and_handle_short, htf_aligned_breakout_short, weekly_bias_pullback_short, xs_momentum_bottom_decile_short)
- DUAL: ~10
- DISABLED: 1

---

## Cross-strategy patterns (Cluster B)

### Pattern T — MA-cross + trend-gate collinearity (CARRIED from Cluster A; refined here)

The dominant Cluster B pattern. Affects all 5 MA-cross strategies and the 3 Ichimoku-confluence strategies.

Disposition options per strategy:
- (a) drop the collinear trend gate (cleanest if cube measurement confirms collinearity)
- (b) replace with non-collinear trend-strength gate (ADX > 25 or 200-EMA-slope-positive)
- (c) keep both and accept (status quo)

### Pattern J — MA-cross variants are reskins (CARRIED + refined for Cluster B)

5 MA-cross strategies all consume `compute_ema_crosses` producer. Variant axes: EMA pair (9/21, 20/50, 50/200) × confirmation gate (volume, trend). Post-B690b: gate-redundancy diagnostic expected to consolidate 5 → 1-2 underlying primitives + cube parameter-sweep on EMA pair.

Factor cluster (B.10) has 6 variants from BAB / momentum-decile / quality combinations. Pattern J expected: ~3-4 underlying factor combinations.

### Pattern U — Multi-timeframe weekly/monthly producer PIT discipline (NEW)

MTF strategies consume weekly/monthly resampled bars. Producer-PIT failure mode: if weekly close-of-week is sampled at midweek (Wednesday) and current bar is Friday, lookahead. Walks must verify multi_timeframe.py resample uses backward-only window (close of week N derived from bars up to Friday of week N, indexed at Friday of week N or earlier).

Per B689 multi_timeframe wireup: PIT verification pending. Producer-audit ticket needed.

### Pattern V — Factor strategies require universe-level computation (NEW)

`xs_*` strategies require per-as_of cross-sectional rank computation. Producer is universe-level (ranks across all T1a tickers at as_of). Per B716: cross_sectional.compute_cross_sectional_features needs B690 TIER 2 harness wireup. Walks document this measurement blocker.

### Pattern Y — Bulkowski retest absorption (CARRIED from B678 Chart+Candle)

Chart-pattern Class 7 NEW strategies (B.9) inherit Pattern Y from Chart+Candle cluster — retest patterns require LOWER volume than initial break (supply absorption thesis). Walks verify each Class 7 NEW strategy implements vol_below_avg gate on retest bar.

### Patterns carried (no new instances expected unless surfaced per walk)

- Pattern A (regime affinity defaults)
- Pattern F (silent-gap default-True post-B663 sweep)
- Pattern G (hardcoded threshold)
- Pattern N (effective-N below IID)
- Pattern Q (STATE vs EVENT)
- Pattern S (asymmetric expectancy LONG vs SHORT)
- Pattern W (deterministic-duplicate post-tightening)

---

## Cluster current state table

| # | Slug | Strategy | Direction | Sub-family | Producer | Walked? | Status |
|---|---|---|---|---|---|---|---|
| B-1 | `strat_golden_cross_9_21` | EMA-9/21 cross + 50-SMA | dual | B.1 MA-Cross | technical.py | ❌ pending B754 | active |
| B-2 | `strat_golden_cross_20_50` | EMA-20/50 cross + 200-EMA | dual | B.1 MA-Cross | technical.py | ❌ pending B754 | active |
| B-3 | `strat_golden_cross_50_200` | EMA-50/200 golden cross | dual | B.1 MA-Cross | technical.py | ⏳ B750 walked | active |
| B-4 | `strat_golden_cross_volume` | Golden cross + volume confirm | dual | B.1 MA-Cross | technical.py | ❌ pending B754 | active |
| B-5 | `strat_death_cross_50_200_volume` | Death cross + volume | short | B.1 MA-Cross | technical.py | ❌ pending B754 | active |
| B-6 | `strat_simple_below_ema_50_short` | Below 50-EMA simple short | short | B.2 EMA-50 | technical.py | ❌ pending B755 | active (B717 ceiling flagged) |
| B-7 | `strat_vol_spike_2x_below_ema_50_short` | Vol spike + below 50-EMA | short | B.2 EMA-50 | technical.py | ❌ pending B755 | active |
| B-8 | `strat_ichimoku_cloud_breakdown` | Ichimoku cloud breakdown short | short | B.3 Ichimoku | technical.py | ❌ pending B755 | active |
| B-9 | `strat_macd_ichimoku` | MACD + Ichimoku confluence | dual | B.3 Ichimoku | technical.py | ❌ pending B755 | active |
| B-10 | `strat_macd_crossover_short` | MACD bearish crossover | short | B.4 MACD | technical.py | ❌ pending B755 | active |
| B-11 | `strat_supertrend_macd_short` | Supertrend + MACD short | short | B.4 MACD | technical.py | ❌ pending B755 | active |
| B-12 | `strat_pivot_fib_confluence` | Pivot + Fibonacci confluence | dual | B.7 Pivot | technical.py | ❌ pending B755 | active |
| B-13 | `strat_supertrend_ichimoku_adx` | Supertrend + Ichimoku + ADX | dual | B.3 Ichimoku | technical.py | ⏳ B750 walked | active |
| B-14 | `strat_break_retest_confluence` | Breakout retest + MACD + EMA | dual | B.8 Break-retest | technical.py | ❌ pending B756 | active |
| B-15 | `strat_prev_day_high_break` | Previous-day high break | long | B.7 Pivot | technical.py | ❌ pending B756 | active |
| B-16 | `strat_r1_break_retest` | R1 pivot break + retest | dual | B.7 Pivot | technical.py | ❌ pending B756 | active |
| B-17 | `strat_squeeze_setup_long` | Squeeze fire-up + setup | long | B.6 Squeeze | technical.py | ❌ pending B756 | active |
| B-18 | `strat_hammer_at_support_long` | Hammer candle at pivot support | long | B.9 Class 7 NEW | chart_patterns.py + technical.py | ❌ pending B756 | active (B685) |
| B-19 | `strat_head_and_shoulders_top_short` | H&S top reversal short | short | B.9 Class 7 NEW | chart_patterns.py | ❌ pending B756 | active (B685; STATUS EXPLORATORY per B732 parallel to inverse) |
| B-20 | `strat_inverted_cup_and_handle_short` | Inverted cup-and-handle short | short | B.9 Class 7 NEW | chart_patterns.py (B686 new producer) | ❌ pending B757 | active (B686) |
| B-21 | `strat_triangle_descending_short` | Descending triangle short | short | B.9 Class 7 NEW | chart_patterns.py | ❌ pending B757 | active (B685) |
| B-22 | `strat_htf_aligned_breakout_long` | HTF-aligned breakout long | long | B.5 Multi-Timeframe | multi_timeframe.py + technical.py | ❌ pending B757 | active (B720 DELETED then revisited? verify) |
| B-23 | `strat_htf_aligned_breakout_short` | HTF-aligned breakout short | short | B.5 Multi-Timeframe | multi_timeframe.py | ❌ pending B757 | active |
| B-24 | `strat_monthly_bias_momentum_long` | Monthly bias + momentum | long | B.5 Multi-Timeframe | multi_timeframe.py | ❌ pending B757 | active |
| B-25 | `strat_weekly_bias_pullback_long` | Weekly bias + daily pullback | long | B.5 Multi-Timeframe | multi_timeframe.py | ❌ pending B757 | active |
| B-26 | `strat_weekly_bias_pullback_short` | Weekly bias + daily pullback short | short | B.5 Multi-Timeframe | multi_timeframe.py | ❌ pending B757 | active |
| B-27 | `strat_xs_combined_momentum_low_ivol` | XS momentum + low IVOL | long | B.10 Factor | cross_sectional.py | ❌ pending B757 | active (measurement-blocked pre-B690) |
| B-28 | `strat_xs_momentum_top_decile` | XS momentum top decile | long | B.10 Factor | cross_sectional.py | ❌ pending B757 | active (measurement-blocked) |
| B-29 | `strat_xs_low_beta_long` | BAB (Frazzini-Pedersen 2014) | long | B.10 Factor | cross_sectional.py | ⏳ B750 walked | active (measurement-blocked) |
| B-30 | `strat_xs_momentum_bottom_decile_short` | XS momentum bottom decile short | short | B.10 Factor | cross_sectional.py | ❌ pending B757 | active (measurement-blocked) |
| B-31 | `strat_xs_momentum_quality_combined` | XS momentum + quality | long | B.10 Factor | cross_sectional.py | ❌ pending B757 | active (measurement-blocked) |
| B-32 | `strat_xs_quality_top_quintile_long` | XS quality top quintile | long | B.10 Factor | cross_sectional.py | ❌ pending B757 | active (measurement-blocked) |
| B-33 | `strat_dxy_headwind_multinational_short` | DXY headwind multinational | short | B.11 Macro | foreign_rev_pct (MISSING per CLAUDE.md) | ❌ pending B757 | **DISABLED-MISSING-PRODUCER** |

**Walk batch sequencing:** B750 = 3 walks; B754 = B-1/B-2/B-4/B-5; B755 = B-6/B-7/B-8/B-9/B-10/B-11/B-12; B756 = B-14/B-15/B-16/B-17/B-18/B-19; B757 = B-20/B-21/B-22/B-23/B-24/B-25/B-26/B-27/B-28/B-30/B-31/B-32/B-33.

---

## Per-strategy walks (B750 initial 3 — Steps 1-7)

### B-3. `strat_golden_cross_50_200` (MA-cross trend, batched B718)

**Step 1 — Strategy registration + docstring claim**

[screener.py:1123](backtest/signals/screener.py#L1123)

```python
def strat_golden_cross_50_200(s):
    fl = s.get("ema_50_200_golden_cross")
    fs = s.get("ema_50_200_death_cross") and not _short_borrow_trap_active(s)
    return _strat3(fl, fs, "trend",
        ["ema_50_200_golden_cross"], ["ema_50_200_death_cross", "borrow_ok"],
        ["EMA-50 crossed above EMA-200  -  golden cross  -  structural shift bullish"],
        ["EMA-50 crossed below EMA-200  -  death cross  -  structural shift bearish"])
```

No docstring. Claim from gate: golden cross / death cross as structural trend shift signal.

This is the CANONICAL golden cross — 50-EMA crosses above 200-EMA. Classic 1970s-era trend-following signal (Granville, Joseph; Faith Curtis "Way of the Turtle" 2007).

**Step 2 — Gate-by-gate analysis**

LONG (1 gate):
1. `ema_50_200_golden_cross` — EVENT signal: 50-EMA crossed above 200-EMA today

SHORT (2 gates):
1. `ema_50_200_death_cross` — EVENT signal: 50-EMA crossed below 200-EMA today
2. `not _short_borrow_trap_active(s)` — B718 borrow gate

Effective gate count: LONG=1 / SHORT=2.

**This is the SIMPLEST gate-stack in Cluster B.** Only the cross-event triggers fire. No additional confirmation gates. This contrasts with golden_cross_9_21 and golden_cross_20_50 which BOTH add trend-gate confirmations.

**Step 3 — Producer source read (CHECKLIST #105)**

Producers:
- `ema_50_200_golden_cross`, `ema_50_200_death_cross`: `compute_ema_crosses(...)` in [technical.py](backtest/signals/technical.py). EVENT signal (fires only on bar of crossing). PIT-clean.
- `_short_borrow_trap_active`: B718 borrow guard.

Producer-source verdict: EVENT-clean. PIT-clean. B718 borrow gate present. CLEAN.

**Step 4 — Signal-docstring vs producer-reality check**

- "EMA-50 crossed above EMA-200" — VERIFIED.
- "structural shift bullish" — qualitative claim, not testable; CLEAN as narrative.

Verdict: docstring ⊆ producer reality. No overclaim. CLEAN.

**Step 5 — Regime affinity check**

Not set in registry. Falls through to default "no affinity = all regimes."

Per Pattern A: docstring claims "structural shift bullish" — implies bull regime is expected outcome. Gate doesn't enforce a separate regime gate. The cross itself signals regime change; no doc-vs-registry mismatch.

**Step 6 — Missing-inverse audit**

LONG/SHORT both present (_strat3 dual). Symmetric mechanical mirror via EVENT inverse. Per `feedback_long_short_inverse_audit`: inverse exists.

**Pattern S verdict:** Golden cross has bull-drift tailwind; death cross has bull-drift headwind + borrow. Cube expected LONG PASS / SHORT marginal-or-FAIL.

**Pattern N concern:** Golden/death crosses cluster around regime transitions (2018-Q4, 2020-Q1, 2022-Q1-Q3). Effective-N inflation ≈ 5-10× depending on T1a universe correlation at fire bar. Raw 50/yr might be ~5-10 IID-equivalent events.

**Step 7 — Bundled disposition recommendations**

| Category | Finding | Action | Class |
|---|---|---|---|
| **F (silent-gap)** | No default-True patterns | CLEAN | — |
| **F (borrow gate)** | B718 explicit gate present | CLEAN | — |
| **G (hardcoded threshold)** | None — pure event signal | CLEAN | — |
| **J (marginal contribution)** | Compare against golden_cross_9_21, _20_50, _volume, death_cross_50_200_volume — same producer family | Post-B690b: gate-redundancy diagnostic on 5 MA-cross variants | **Class 6 DEFERRED-POST-B690b (cross-ref `S4-B750-PATTERN-J-MA-CROSS-CONSOLIDATION-AUDIT`)** |
| **N (effective-N)** | Cross events cluster at regime transitions; effective-N << raw N | Cube infra ticket cluster-wide | **Class 8 CUBE-INFRA** |
| **T (collinearity)** | Single-gate strategy — NO collinear trend gate added. CLEAN per Pattern T. | No action | CLEAN |
| **S (asymmetric expectancy)** | SHORT death-cross faces bull drift + borrow | Document; cube empirically validates | **Class 6 DEFERRED-POST-CUBE** |

**Disposition recommendation: KEEP-AS-IS. Status post-B750: PRE-CUBE-CLEAN.**

A-priori fire-count projection: Golden/death crosses are RARE events — ~1-3 per ticker per several years. T1a 2020-2026 universe-wide: estimated 50-150 fires LONG-side, ~30-80 SHORT-side. **Likely PASS_CUBE on raw count but FAIL on Pattern N effective-N adjustment.** EXPLORATORY classification candidate per W5m precedent.

---

### B-13. `strat_supertrend_ichimoku_adx` (Confluence, batched B630)

**Step 1 — Strategy registration + docstring claim**

[screener.py:2264](backtest/signals/screener.py#L2264)

```python
def strat_supertrend_ichimoku_adx(s):
    # B630 sweep: positive symmetric supertrend_bearish (B630 producer)
    fl = (s.get("supertrend_bullish") and s.get("ichi_above_cloud") and s.get("adx_strong"))
    fs = (s.get("supertrend_bearish") and s.get("ichi_below_cloud") and s.get("adx_strong")) and not _short_borrow_trap_active(s)
    return _strat3(fl, fs, "confluence", ...)
```

No standalone docstring. Claim from context_bullets: "Supertrend + Ichimoku cloud + ADX — three trend systems bullish / bearish."

**Step 2 — Gate-by-gate analysis**

LONG (3 gates):
1. `supertrend_bullish` — STATE signal (Supertrend system long)
2. `ichi_above_cloud` — STATE signal (price above Ichimoku Kumo)
3. `adx_strong` — STATE signal (ADX > 25 or 30 typically)

SHORT (4 gates):
1. `supertrend_bearish` — B630 producer-additive symmetric inverse
2. `ichi_below_cloud`
3. `adx_strong`
4. `not _short_borrow_trap_active(s)`

Effective gate count: LONG=3 / SHORT=4.

**All STATE gates.** This is a textbook gate-stacking-without-EVENT-trigger strategy. Fire fires every bar where all 3 STATE conditions are simultaneously True.

**Step 3 — Producer source read (CHECKLIST #105)**

Producers:
- `supertrend_bullish`, `supertrend_bearish`: `compute_supertrend(...)` in technical.py. STATE signal. B630 added symmetric `supertrend_bearish`. B655 T10 redesign added EVENT variant `supertrend_flip_recent_long_5d` but this strategy still consumes the STATE.
- `ichi_above_cloud`, `ichi_below_cloud`: `compute_ichimoku(...)`. STATE.
- `adx_strong`: `compute_adx(...)`. STATE.

Producer-source verdict: All STATE-based. Pattern Q candidate (cluster-level). PIT-clean (Supertrend, Ichimoku, ADX are past-only smoothings).

**Step 4 — Signal-docstring vs producer-reality check**

- "Three trend systems bullish" — TRUE structurally but is STATE-only, doesn't distinguish fresh trend confluence from sustained trend confluence. Pattern Q.

Verdict: docstring ⊆ producer reality. No overclaim BUT TEMPORALITY MISMATCH risk.

**Step 5 — Regime affinity check**

Not set in registry. Falls through to default. Per Pattern A: confluence implicitly signals "trending regime" — but gates don't separately enforce regime. Trending regime IS the signal here.

**Step 6 — Missing-inverse audit**

LONG/SHORT both present (_strat3 dual). Symmetric. Per `feedback_long_short_inverse_audit`: inverse exists.

**Pattern S verdict:** Confluence triad has bull-drift tailwind on LONG, headwind + borrow on SHORT.

**Pattern T concern:** Supertrend + Ichimoku cloud + ADX trending are all TREND-CONFLUENCE signals that fire together in trending markets. High collinearity expected. Marginal-contribution audit critical post-B690b.

**Pattern N concern:** Trend-confluence persists for weeks during trending regimes. Effective-N severely inflated relative to IID. ~10-15× inflation factor estimated.

**Pattern Q concern (HIGHEST PRIORITY):** All 3 gates are STATE. Fire rate inflated by ~5-10× vs EVENT-based equivalent. Cluster A B655 T10 precedent: convert to EVENT-based via `_state_flip_recent_5d` producer-additive signal. This is the textbook over-firing strategy.

**Step 7 — Bundled disposition recommendations**

| Category | Finding | Action | Class |
|---|---|---|---|
| **F (silent-gap)** | B630 symmetric `supertrend_bearish` present | CLEAN | — |
| **F (borrow gate)** | B718 explicit gate present | CLEAN | — |
| **Q (STATE vs EVENT)** | All 3 gates STATE — strategy over-fires during trending regimes | EVENT-conversion candidate per B655 T10: emit `supertrend_flip_recent_5d` AND `ichi_above_cloud_break_recent_5d` AND `adx_cross_25_recent_5d`; strategy fires on cross OR fresh confluence | **Class 2 LOOSEN/TIGHTEN (queue `S4-B750-B-13-Q-EVENT-CONVERSION`); HIGH-PRIORITY pre-cube** |
| **T (gate collinearity)** | Supertrend + Ichimoku + ADX-strong are all trend-confluence signals; high collinearity expected | Post-B690b: gate-redundancy diagnostic | **Class 6 DEFERRED-POST-B690b** |
| **J (marginal contribution)** | Compare against macd_ichimoku, supertrend_macd_short — Ichimoku is shared signal across 3+ strategies | Post-B690b: cluster-wide redundancy audit | **Class 6 DEFERRED-POST-B690b** |
| **N (effective-N)** | Trend confluence persists weeks; effective-N inflation 10-15× | Cube infra ticket | **Class 8 CUBE-INFRA** |

**Disposition recommendation: KEEP-AS-IS PENDING Q EVENT-conversion. Status post-B750: PRE-CUBE-CLEAN POST-FIXES.** Pattern Q is the highest-priority Cluster B fix — produces measurable over-firing in B660 if not addressed.

A-priori fire-count projection: 3 STATE gates simultaneously True ~15-25% of bars in trending regimes. T1a 2020-2026 universe-wide: estimated 30,000-50,000 LONG-side fires (over B710 5K ceiling). **Likely FAIL_OVER_CEILING per B710 family.** Pattern Q EVENT-conversion expected to drop by 90-95% to 1,500-5,000/yr (PASS_CUBE range).

---

### B-29. `strat_xs_low_beta_long` (Factor / BAB, batched B220 + B358 cell-audit)

**Step 1 — Strategy registration + docstring claim**

[screener.py:3228](backtest/signals/screener.py#L3228)

```python
def strat_xs_low_beta_long(s):
    """Batch 220: Betting-against-beta (Frazzini-Pedersen 2014 JFE;
    Blitz-van Vliet 2024 JPM update). Long bottom-2-decile beta names.
    Low-beta names systematically outperform on a risk-adjusted basis.

    Batch 358 (2026-05-25 owner-approved cell-audit Bucket C Option A):
    REMOVED the price_above_ema_200 bull-regime gate. The published BAB
    Sharpe is across the full sample (not bull-only). Cell audit data
    showed (xs_low_beta_long x atr_trail_1x in neutral regime) lost
    -6.22% mean PnL on n=30 - the strategy was firing in neutral regime
    when the EMA gate let through (low-beta absolute returns lag in
    strong-bull regimes per BAB literature; bear / neutral is where
    absolute alpha is captured). Removing the gate aligns the
    implementation with the published full-sample edge."""
```

Claim: "Betting-against-beta (Frazzini-Pedersen 2014) — low-beta bottom-2-decile + not-high-IVOL. B358 removed 200-EMA gate per Bucket C cell audit."

Citations: Frazzini A., Pedersen L.H. (2014) JFE "Betting Against Beta" + Blitz D., van Vliet P. (2024) JPM update.

**Step 2 — Gate-by-gate analysis**

LONG (2 gates):
1. `s.get("xs_low_beta_decile", False)` — cross-sectional rank: in bottom-2-decile beta vs SPY
2. `s.get("xs_avoid_high_ivol", True)` — NOT in high-IVOL decile (quality filter)

LONG-only (no short side; BAB literature is long-only).

Effective gate count: LONG=2.

**Step 3 — Producer source read (CHECKLIST #105)**

Producers:
- `xs_low_beta_decile`, `xs_avoid_high_ivol`: `cross_sectional.compute_cross_sectional_features(...)` in [cross_sectional.py](backtest/signals/cross_sectional.py). Universe-level per-as_of rank computation. Returns BOOLEAN: True if ticker is in bottom-2-decile beta on as_of bar.

**Producer-PIT discipline:** Beta computation lookback = typically 252-day rolling regression of ticker returns vs SPY returns. Per B716: cross_sectional.compute_cross_sectional_features requires full OHLCV dict + as_of refactor for B690 TIER 2 harness. Until B690 wireup completes, producer fires 0 in B660 measurement (confirmed by B716 per CLAUDE.md).

**Measurement-blocked status:** Per B716 banner + B660 result. B690 + B690b required before strategy fires on cube.

Producer-source verdict: PIT-clean methodology (past 252 returns are past-only). MEASUREMENT-BLOCKED pre-B690.

**Step 4 — Signal-docstring vs producer-reality check**

- "Frazzini-Pedersen 2014" citation — VERIFIED methodology
- "Bottom-2-decile beta" — VERIFIED gate
- "Not high-IVOL" — VERIFIED gate
- "B358 removed 200-EMA gate" — VERIFIED via git blame (Batch 358 commit)
- Cell-audit evidence (xs_low_beta_long × atr_trail_1x neutral regime -6.22% PnL n=30) — VERIFIED via PHASE_1A_BETA_STAGE_D_LOSER_CELL_AUDIT.md

Verdict: docstring ⊆ producer reality + sound empirical lineage. CLEAN.

**Step 5 — Regime affinity check**

Not set in registry post-B358 (the bull-only regime affinity was implicit via 200-EMA gate, removed B358 per cell-audit).

Per Pattern A: docstring CLAIMS "bear / neutral is where absolute alpha is captured" — implicit bear/neutral regime affinity. But registry has no explicit affinity. Doc-vs-registry mismatch.

**Recommendation:** Add explicit `STRATEGY_REGIME_AFFINITY['xs_low_beta_long'] = {bear, neutral}` per B358 cell-audit finding. CURRENT registry default `all regimes` lets strategy fire in bull (when it underperforms) — costs alpha.

**Step 6 — Missing-inverse audit**

NO SHORT inverse. Per BAB literature: it's a long-only anomaly. SHORT of high-beta is a separate strategy (`xs_momentum_bottom_decile_short` is the closest mirror but tests momentum not beta).

Per `feedback_long_short_inverse_audit`: inverse intentionally absent due to data-source asymmetry (low-beta long is alpha; high-beta short would face borrow + squeeze + crowding). Per `feedback_asymmetric_data_sources_break_mechanical_inverse`: this is the correct treatment.

**Pattern S verdict:** LONG-only is consistent with literature. Asymmetric expectancy is structural (low-beta = institutional preference; high-beta = retail-favored), not a strategy-design issue.

**Step 7 — Bundled disposition recommendations**

| Category | Finding | Action | Class |
|---|---|---|---|
| **F (silent-gap)** | Default-False on `xs_low_beta_decile`; Default-True on `xs_avoid_high_ivol` (acceptable: producer fires explicit False only for high-IVOL) | CLEAN | — |
| **F (borrow gate)** | LONG-only; no borrow consideration | N/A | — |
| **Pattern A (regime affinity)** | Docstring claims bear/neutral but registry says all regimes; B358 removed 200-EMA but didn't add explicit affinity | Add `STRATEGY_REGIME_AFFINITY['xs_low_beta_long'] = {bear, neutral}` per B358 cell-audit lineage | **Class 2 LOOSEN/TIGHTEN (queue `S4-B750-B-29-REGIME-AFFINITY-ADD`)** |
| **V (cross-sectional producer)** | Measurement-blocked pre-B690 cross_sectional wireup | Per B690 critical path | **Class 6 DEFERRED-POST-B690 (cross-ref B716 ticket)** |
| **J (factor consolidation)** | 6 xs_* strategies share cross_sectional producer; potential consolidation post-B690b | Post-B690b: factor-cluster Pattern J audit | **Class 6 DEFERRED-POST-B690b (cross-ref `S4-B750-PATTERN-J-FACTOR-CLUSTER-CONSOLIDATION-AUDIT`)** |
| **N (effective-N)** | Cross-sectional rank changes monthly typically; effective-N concern depends on rebalance frequency | Cube infra ticket | **Class 8 CUBE-INFRA** |

**Disposition recommendation: KEEP-AS-IS + Class 2 regime-affinity addition + DEFERRED B690 measurement. Status post-B750: STRATEGY-CLEAN; MEASUREMENT-BLOCKED.**

A-priori fire-count projection: Bottom-2-decile beta + not-high-IVOL = ~10-20% of T1a universe at any time. With monthly rebalance ≈ 1-2 fires/ticker per year. T1a 2020-2026 universe-wide: estimated 1,000-3,000/yr LONG-side IF cross_sectional wireup landed. Post-B690b measurement TBD.

---

## B750 cluster walk completion wrap-up (Cluster B)

### Disposition summary (3 walks shipped)

| Walk | Strategy | Status | Class actions surfaced |
|---|---|---|---|
| B-3 | golden_cross_50_200 | KEEP-AS-IS (CLEAN single-gate event signal) | J + N + S |
| B-13 | supertrend_ichimoku_adx | KEEP-AS-IS PENDING Pattern Q EVENT-conversion (HIGH-PRIORITY pre-cube) | Q + T + J + N |
| B-29 | xs_low_beta_long | KEEP-AS-IS + regime-affinity addition; MEASUREMENT-BLOCKED pre-B690 | A (regime) + V (cross_sectional) + J + N |

**Pattern Q (STATE vs EVENT) is the highest-priority Cluster B finding.** Affects all 3 Ichimoku-confluence strategies + 5 MA-cross strategies + likely 10+ other walks. Cluster-wide producer-additive EVENT-conversion candidate.

**Pattern V (cross_sectional producer wireup pre-B690) is the measurement gate for all 6 factor strategies.** Per B716: blocks measurement until B690 TIER 2 harness lands.

**Pattern T (MA-cross + trend-gate collinearity) is the Cluster-B-specific finding** — relevant for B-1/B-2/B-4 walks pending in B754.

### NEW EXECUTION_QUEUE tickets surfaced (B750)

1. `S4-B750-PATTERN-Q-CLUSTER-B-EVENT-CONVERSION-SWEEP` — producer-additive sweep across all STATE-based trend-confluence strategies; emit `_state_flip_recent_5d` EVENT variants per B655 T10 precedent. HIGH-PRIORITY pre-cube. PENDING-OWNER-APPROVAL.
2. `S4-B750-PATTERN-J-MA-CROSS-CONSOLIDATION-AUDIT` — 5 MA-cross variants consolidation candidate; post-B690b gate-redundancy diagnostic. DEFERRED-POST-B690b.
3. `S4-B750-PATTERN-J-FACTOR-CLUSTER-CONSOLIDATION-AUDIT` — 6 xs_* strategies consolidation candidate; post-B690b. DEFERRED-POST-B690b (cross-ref B716).
4. `S4-B750-PATTERN-U-MULTI-TIMEFRAME-PRODUCER-PIT-VERIFY` — multi_timeframe.py weekly/monthly resample PIT discipline audit; producer-audit template (B699/B700/B735). Affects 5 MTF strategies. PENDING-OWNER-APPROVAL.
5. `S4-B750-B-13-Q-EVENT-CONVERSION` — strat_supertrend_ichimoku_adx STATE-to-EVENT conversion (3 gates). PENDING-OWNER-APPROVAL.
6. `S4-B750-B-29-REGIME-AFFINITY-ADD` — `STRATEGY_REGIME_AFFINITY['xs_low_beta_long'] = {bear, neutral}` per B358 cell-audit + BAB literature. PENDING-OWNER-APPROVAL.
7. `S4-B750-B-19-HEAD-SHOULDERS-TOP-SHORT-EXPLORATORY-VERIFY` — verify strat_head_and_shoulders_top_short inherits B732 EXPLORATORY status from inverse (h&s bottom long). PENDING-VERIFICATION-B756.

### Owner decision gates (B750 Cluster B surfaces)

| Decision | Severity | Pre-cube urgency |
|---|---|---|
| Cluster-B Pattern Q EVENT-conversion sweep approval | **HIGH** | Pre-cube preferred (10+ strategies expected over B710 5K ceiling otherwise) |
| Pattern J MA-cross + Factor consolidation post-B690b | HIGH | Post-B690b (waits on measurement) |
| Pattern U multi_timeframe.py PIT audit | MEDIUM | Pre-cube preferred |
| B-29 xs_low_beta regime-affinity addition | LOW | Pre-cube (small fix) |
| B-19 h&s top short EXPLORATORY verification | LOW | Pre-cube doc-only |

---

## Cluster-wide methodology references

### Producer modules touched by Cluster B

- `backtest/signals/technical.py` — MA-crosses, MACD, Supertrend, Ichimoku, ADX, PSAR
- `backtest/signals/multi_timeframe.py` — weekly/monthly bias signals (B-5 sub-cluster)
- `backtest/signals/chart_patterns.py` — chart-pattern Class 7 NEW (B-9 sub-cluster); B686 inverted-cup new producer
- `backtest/signals/cross_sectional.py` — beta deciles, momentum deciles, IVOL deciles, quality (B-10 sub-cluster); B690 TIER 2 wireup required

### Citations (selected)

- **Granville J. (1976)** — *New Strategy of Daily Stock Market Timing for Maximum Profit* — Golden cross / death cross methodology basis
- **Faith C. (2007)** — *Way of the Turtle* — Long-MA-cross trend-following discipline
- **Murphy J. (1999)** — *Technical Analysis of the Financial Markets* — Ichimoku cloud canonical reference
- **Frazzini A., Pedersen L.H. (2014)** — JFE "Betting Against Beta" — basis of strat_xs_low_beta_long
- **Blitz D., van Vliet P. (2024)** — JPM update on BAB anomaly persistence
- **Asness C., Moskowitz T., Pedersen L.H. (2013)** — JF "Value and Momentum Everywhere" — basis of strat_xs_combined_momentum_low_ivol
- **Jegadeesh-Titman (1993)** — *Returns to Buying Winners and Selling Losers* — basis of XS momentum decile strategies
- **Bulkowski T. (2005)** — *Encyclopedia of Chart Patterns* — chart-pattern Class 7 NEW reference (B-9 sub-cluster)
- **Edwards-Magee (1948)** — *Technical Analysis of Stock Trends* — H&S top + triangle reference

### Forensic-fix lineage

- **B220 (2026-05-18)** — Factor / cross-sectional strategy registration (BAB + momentum-quality)
- **B358 (2026-05-25)** — Cell-audit Bucket C: removed 200-EMA gate from xs_low_beta_long per neutral-regime -6.22% PnL data
- **B630 (2026-06-07)** — Producer-additive symmetric `supertrend_bearish` (closes silent-gap)
- **B655 (2026-06-09)** — T10 supertrend redesign STATE→EVENT pattern (precedent for Cluster B Pattern Q)
- **B685 (2026-06-10)** — Class 7 NEW chart-pattern mirrors: head_and_shoulders_top_short + triangle_descending_short + hammer_at_support_long
- **B686 (2026-06-10)** — Class 7 NEW inverted_cup_and_handle_short + new producer compute_inverted_cup_and_handle
- **B689 (2026-06-11)** — Measurement harness extension for chart_patterns + multi_timeframe + smc_ict producers; B660 re-run launched
- **B716 (2026-06-12)** — Cross-sectional producer wireup confirmed required for B690 (xs_* strategies measurement-blocked)
- **B718a-d (2026-06-12)** — Explicit `borrow_ok` gate refactor on all short-emitting strategies in this cluster
- **B722 (2026-06-12)** — strat_po3_htf_aligned_long/_short DELETED per Pattern F deterministic-subset finding (NOT in Cluster B as a consequence)
- **B732 (2026-06-12)** — strat_head_and_shoulders_bottom_long EXPLORATORY (inverse of B-19 head_and_shoulders_top_short)
- **B744 (2026-06-13)** — Static borrow-gate lint shipped

### Cross-strategy patterns lineage (CARRIED + NEW)

- **Pattern A** — B577 STRATEGY_REGIME_AFFINITY survey (cross-applied via B-29 finding)
- **Pattern F** — B611 reviewer + B663 sweep + B718 refactor
- **Pattern J** — B714 routing framework (cluster-wide audit candidate for B.1 + B.10)
- **Pattern N** — B710 effective-N + W5 council
- **Pattern Q** — B643 W5 + B655 T10 EVENT-conversion precedent (HIGH-PRIORITY Cluster B finding)
- **Pattern S** — B611 + B713 + B710 (asymmetric SHORT expectancy)
- **Pattern T (carried from Cluster A; refined for Cluster B)** — MA-cross + trend-gate collinearity
- **Pattern U (NEW B750)** — multi-timeframe producer PIT discipline (weekly/monthly resample)
- **Pattern V (NEW B750)** — cross-sectional producer requires universe-level computation (B690 TIER 2 dependent)
- **Pattern Y** — Bulkowski retest absorption (carry from Chart+Candle for B.9 sub-cluster)
- **Pattern W** — B718 hull_rsi deterministic-duplicate

---

## B750 cluster walk status

| Walk | Status | Batch |
|---|---|---|
| B-3 golden_cross_50_200 | ✅ Walked B750 | 2026-06-14 |
| B-13 supertrend_ichimoku_adx | ✅ Walked B750 | 2026-06-14 |
| B-29 xs_low_beta_long | ✅ Walked B750 | 2026-06-14 |
| All other B-1..B-33 walks | ⏳ Pending B754-B757 | — |

**Progress: 3/33 walked (9%) — framework + 3 sample walks shipped B750.**

---

### Cross-cluster status snapshot (post-B750)

| Cluster Doc | Status | Walks | Cross-cluster patterns shared with Cluster B |
|---|---|---|---|
| All 8 prior cluster docs | External review complete + walks complete | 132 | Patterns F + J + N + S + T + W (various) |
| [STAGE_4_OSCILLATOR_MEAN_REVERSION_CLUSTER_WALKS.md](STAGE_4_OSCILLATOR_MEAN_REVERSION_CLUSTER_WALKS.md) | B750 framework + 3 sample walks | 3/30 | Patterns F + G + J + N + Q + R + S + T + W |
| **STAGE_4_TREND_CONFLUENCE_CHART_PATTERN_RESIDUAL_CLUSTER_WALKS.md (THIS DOC)** | **B750 framework + 3 sample walks** | **3/33** | **Patterns F + J + N + Q + S + T + U (new) + V (new) + W + Y** |
| STAGE_4_CONTEXT_EVENT_CALENDAR_CLUSTER_WALKS.md | Scheduled B758+ | 0/33 | (TBD) |

**Stage 4 cluster-walk coverage post-B750 (both Cluster A + B docs):** 132 + 3 + 3 = **138 walked (62%)** / 83 remaining unwalked (38%). Target: 96-walk completion across B751-B762.

---

**B750 Cluster B deliverables:** doc scaffolding + Patterns A-Y framework + 33-strategy state table + 3 walks (B-3 + B-13 + B-29) + 7 NEW EXECUTION_QUEUE tickets + cross-cluster snapshot update.

**Per `feedback_pyramid_per_addressal`:** pyramid runs end-of-batch with B750 commit alongside Cluster A doc.

**Per `feedback_strategy_counts_by_buckets_each_turn`:** 221 registered / 0 deprecated / 1 missing-producer / 220 active. Cluster B walks: 3/33 (9% post-B750). Total Stage 4 walked: 138/221 (62%).
