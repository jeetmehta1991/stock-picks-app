# Stage 4 Trend Cluster Walks — living doc

> **What this document is.** Stage 4 walk bundle for the trend-indicator cluster. Per cluster-organization policy (owner directive 2026-06-09), this is the second per-cluster walk doc after `STAGE_4_PIVOT_CLUSTER_WALKS.md`. **PROSPECTIVE** state — surfacing options + recommendations + owner decision form. Once owner picks dispositions, this doc evolves into a post-action report (same shape as the pivot cluster doc).
>
> **Audience.** Same as the pivot cluster doc — assumes ZERO prior knowledge; every term defined once; every threshold explained. Foundations (signals, regime classification, 7-step methodology) and CHECKLIST extensions (r) / (s) / Step 1.5 are documented in [`STAGE_4_PIVOT_CLUSTER_WALKS.md`](STAGE_4_PIVOT_CLUSTER_WALKS.md#foundations). Read that doc's Foundations section first if anything below is unfamiliar.
>
> **Scope.** 10 trend-cluster strategies — momentum crossovers (MACD slow + fast), trend-following (Hull RSI, Parabolic SAR long + short, TEMA/DEMA), Ichimoku (TK cross + cloud breakout), ADX initiation, Supertrend+MACD confluence. Mostly DUAL `_strat3` strategies; one explicit SHORT-only single direction.
>
> **Source of truth.** Code references reflect current state at commit `b38e533f3` (post-B646).
>
> **What's different from the B640 pivot bundle.** Two important methodology changes shipped during the pivot cluster review-cycle (B641-B646) that apply uniformly to this walk:
> 1. **Fire-count MEASUREMENT, not projection.** Each strategy's fire-count comes from `scripts/measure_fire_count.py` running against actual 220-ticker T1a OHLCV history, with pairwise gate-correlation matrix + independence-ratio diagnostic. The independence-product projection used in B640 was biased in both directions and is no longer authoritative. (B641 measurement reversed 4 of 5 B640 FAIL_FIRE_STARVED labels.)
> 2. **CHECKLIST extensions (r), (s), Step 1.5 applied uniformly.** Timeframe-mismatch check (less acute for trend indicators — they're daily-bar appropriate), EVENT/STATE timing-fragility flag (more relevant here — many trend signals are STATE), and `_strat3` avoid-branch dead-code analysis.

---

## Table of contents

1. [Cluster current state](#cluster-current-state) — read this first if you're short on time
2. [Cross-cutting findings](#cross-cutting-findings) — B271 family-bug status across the cluster
3. [Per-strategy walks (T1-T10)](#per-strategy-walks)
4. [Bundled action items](#bundled-action-items)
5. [Owner decision form](#owner-decision-form)

---

## Cluster current state

| T# | Strategy | Direction | Category | Gate count | Regime affinity | B271 risk | Measured fires/yr (univ) | Indep ratio | REDUNDANCY concern? |
|---|---|---|---|---|---|---|---:|---:|---|
| T1 | `macd_crossover` | dual | momentum | 1 per direction | none (B291 default) | ✅ clean | **8,506** PASS_CUBE | 0.019 | ⚠ Extreme fire rate — but it's a literal 1-gate strategy (MACD cross is one EVENT). Not redundant; just frequent. Maybe over-firing on noise. |
| T2 | `macd_fast_crossover` | dual | momentum | 1 per direction | explicit `{bull}` | ⚠ B271 candidate — DEFERRED R5 M1 | **13,730** PASS_CUBE | 0.031 | Same as T1 — 1-gate; frequent crosses on faster periods (8/21/5). |
| T3 | `hull_rsi` | dual | momentum | 4 per direction (post-B656) | none (B617 REMOVED) | ✅ clean (post-B617) | **23,898** PASS_CUBE (pre-B656) | 0.059 | ✅ **B656 RESOLVED: NOT redundancy** — per-gate audit found NO extreme NO-OP gate (all 5 gates 38-53% True); honest confluence (hull_bullish × price_above_hull correlate +0.41 measuring distinct Hull semantics; not redundant). Option A+C: status-quo confluence + dropped rsi_9>50 accidentally-safe no-op (B654 W8 RSI precedent). 5 → 4 distinct gates. SHORT-side `(not above_200)` NOT-pattern queued separately as `S4-T3-NOT-ABOVE-200-EMA-PATTERN`. |
| T4 | `parabolic_sar_flip` | dual | trend | 2 per direction | explicit `{bear}` | ⚠ B271 — DEFERRED R5 M1 | **3,635** PASS_CUBE | 0.023 | EVENT (flip) + STATE (adx_trending). 2-gate is reasonable; high rate driven by adx_trending being common. |
| T5 | `parabolic_sar_flip_short` | SHORT (single) | trend | 2 | explicit `{bear, crisis, neutral}` (= B291 default) | ✅ N/A | **1,834** PASS_CUBE | 1.033 | Same gate set as T4 SHORT side — duplicate concern still applies (per T5 walk). Indep ratio ≈ 1.0 = gates roughly independent (rare). |
| T6 | `tema_dema` | dual | trend | 2 per direction | explicit `{bear}` | ⚠ B271 — DEFERRED R5 M1 | **5,760** PASS_CUBE | 0.003 | EVENT (cross) + STATE (price vs TEMA). High rate driven by frequent TEMA/DEMA crosses on volatile names. |
| T7 | `ichimoku_tk_cross` | dual | trend | 2 per direction | none (B291) | ✅ clean | **2,080** PASS_CUBE | 0.005 | EVENT (TK cross) + STATE (cloud position). Modest fire rate. |
| T8 | `ichimoku_cloud_breakout` | dual | trend | 4 per direction | none (B291) | ✅ clean | **24,776** PASS_CUBE (pre-B657; expected slight drop with stricter weekly Kumo defaults) | 0.009 | ✅ **B657 RESOLVED: NOT redundancy** — same finding as T3 (gates 38-51% True; honest Ichimoku multi-component confluence). Option E (A+D): status-quo on 4-gate confluence + swap `weekly_above_cloud`/`weekly_below_cloud` defaults True→False (closes T8 portion of `S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY`). |
| T9 | `adx_initiation` | dual | trend | 2 per direction | explicit `{bear}` | ⚠ B271 — DEFERRED R5 M1 | **1,611** PASS_CUBE | 0.249 | EVENT (adx_cross_up) + STATE (di_bull/bear). Modest fire rate. |
| T10 | `supertrend_macd` | dual | trend | 3 per direction (post-B655) | explicit `{bull}` | ⚠ B271 — DEFERRED R5 M1 | **772** PASS_CUBE (B655 measured -97.7% drop from 32,913 → 772; -25× fire rate) | 0.004 | ✅ **B655 RESOLVED: extreme NO-OP camouflage confirmed + fixed** — `supertrend_bullish` was 99.19% True on the random-30 sample (Supertrend trailing indicator stays bullish for long stretches). Option B template: NEW producer-additive `supertrend_flip_recent_long_5d` / `_short_5d` (B643/B645 lookback pattern; B574 narrow-scope; only T10 consumes the new signals). Strategy switched from STATE supertrend_bullish to EVENT-anchored lookback. **Genuine timing alpha restored.** |

**Source:** [`output_audit/fire_count_measured_b648_w5m_trend_random30.json`](output_audit/fire_count_measured_b648_w5m_trend_random30.json) — 30 random tickers (seed 42) × 2022-2024 × B648-corrected ×16.77 projection scale.

**Per critique #2 corrected methodology (see [pivot cluster doc](STAGE_4_PIVOT_CLUSTER_WALKS.md#what-the-independence-ratio-is-telling-us)):** high fire rate + low independence ratio + all-STATE gates is the SIGNATURE that NEEDS investigation — could be redundancy/no-op OR honest confluence. **Per-gate "what does this screen out" audit is the diagnostic.** Outcomes across the trend cluster (B655 + B656 + B657 walks 2026-06-09):

| Strategy | Per-gate audit found | Pattern | Resolution |
|---|---|---|---|
| **T10 supertrend_macd** | 99.19% True on `supertrend_bullish` = EXTREME NO-OP | Same as W8 / T10 = no-op camouflage | B655 option B: EVENT-anchored lookback `supertrend_flip_recent_long_5d` replaces STATE; **measured 33k → 772/yr (-97.7%)** |
| **T3 hull_rsi** | NO extreme NO-OP (all 5 gates 38-53% True); hull_bullish × price_above_hull = +0.41 distinct Hull semantics from different angles | Honest confluence + 1 RSI noop | B656 option A+C: status-quo confluence + drop rsi_9>50/<50 |
| **T8 ichimoku_cloud_breakout** | NO extreme NO-OP (38-51% True); honest Ichimoku multi-component confluence; BUT default-True silent-gap on weekly Kumo (same class as W6/W7/W8 LONG AVWAP) | Honest confluence + default-True asymmetric | B657 option E (A+D): status-quo confluence + default-True→False on weekly Kumo |

**Methodology lesson:** not all "high fire rate + all-STATE" strategies are redundancy. The per-gate audit ("what does THIS screen out that the others don't?") is the diagnostic that distinguishes honest confluence (gates measure distinct aspects correlating at firing time) from no-op camouflage (one gate is near-always-True providing false precision).

**Caveats per B649 framing (PRELIMINARY measured / pending full-universe verification):** 30 tickers across one regime arc; per critique #1 these numbers remain hypotheses pending `S5-FIRE-COUNT-MEASURED-RUN-FULL`. Trend strategies in particular over-fire on large-cap uptrending names in 2022-2024 — the magnitudes are likely OVER-stated for the full universe.

**5 of 10 strategies carry single-direction regime affinity entries despite being dual.** This is the B271 family-bug pattern (mass-edit single-direction-era entries that cap both directions when strategy becomes dual). However, ALL 5 are **already deferred** under existing `S5-REGIME-AFFINITY-21-DEFERRED` (B624 manifest M1) — owner directive: no STRATEGY_REGIME_AFFINITY changes until R5 cube produces direction-aware per-(strategy, direction, regime) Sharpe data. So this cluster's B271 instances are queue-resolved already; the walks below confirm-and-note rather than propose fix.

**No NEW B271 family-bug instances surfaced by this walk.**

**5 of 10 strategies carry single-direction regime affinity entries despite being dual.** This is the B271 family-bug pattern (mass-edit single-direction-era entries that cap both directions when strategy becomes dual). However, ALL 5 are **already deferred** under existing `S5-REGIME-AFFINITY-21-DEFERRED` (B624 manifest M1) — owner directive: no STRATEGY_REGIME_AFFINITY changes until R5 cube produces direction-aware per-(strategy, direction, regime) Sharpe data. So this cluster's B271 instances are queue-resolved already; the walks below confirm-and-note rather than propose fix.

**No NEW B271 family-bug instances surfaced by this walk.**

**Strategy bucket counts** (per `feedback_strategy_counts_by_buckets_each_turn`, source-of-truth `ALL_STRATEGIES` at b38e533f3):
- Total registered: **222** | Active for cube: 221 | Deprecated: 0 | Disabled: 1 | EXPLORATORY: 2 (W5 + W5 mirror from pivot cluster)

---

## Cross-cutting findings

### CC1. B271 family-bug status: ALREADY DEFERRED

5 strategies in this cluster (T2 macd_fast_crossover, T4 parabolic_sar_flip, T6 tema_dema, T9 adx_initiation, T10 supertrend_macd) carry explicit single-direction `STRATEGY_REGIME_AFFINITY` entries despite being dual `_strat3` strategies. Pattern identical to the pivot cluster's W3/W4 fixes (B641 shipped delete-and-fall-back-to-B291). BUT: these 5 are B617 KEPT as `# B418 cube override; direction-disagg validation pending`. Per `S5-REGIME-AFFINITY-21-DEFERRED` (B624 manifest M1), no further STRATEGY_REGIME_AFFINITY map changes until R5 cube emits direction-aware Sharpe data.

**Action: NO new tickets needed; all 5 entries are already on the M1 queue.** The walks below reconfirm the pattern but do not propose delete.

### CC2. CHECKLIST (r) timeframe-mismatch: low risk

Unlike pivot/Camarilla/CPR (which ARE intraday-by-design tools mis-applied on daily bars), the trend-cluster indicators (MACD, Hull MA, EMA, Parabolic SAR, TEMA/DEMA, Ichimoku, ADX, Supertrend) are **all designed for any timeframe**. Their definitions don't reset overnight. CHECKLIST (r) hazard doesn't apply to this cluster.

### CC3. CHECKLIST (s) EVENT/STATE timing-fragility: notable on some strategies

Several gates in this cluster are STATE-signals (hull_bullish, supertrend_bullish, ichi_above_cloud, price_above_tema). The crossover events (macd_crossover_up, adx_cross_up, tema_cross_up, psar_flip_up, ichi_tk_cross_up) are EVENT. Strategies that mix STATE + STATE (no EVENT) trigger CHECKLIST (s) F-timing-fragility. Per-strategy classification in walks below.

### CC4. Avoid-branch dead-code (Step 1.5): mostly mutually-exclusive

Most dual strategies in this cluster use mutually-exclusive crossover pairs (cross_up vs cross_dn) — the avoid branch is structurally dead. Recorded per-strategy below.

### CC5. AVWAP-style default-True asymmetry: only T8

T8 `ichimoku_cloud_breakout` has `weekly_long_ok = s.get("ichi_weekly_above_cloud", True)` AND `weekly_short_ok = s.get("ichi_weekly_below_cloud", True)` — BOTH default-True. Different asymmetry pattern than the pivot cluster's W6/W7 (which had LONG default-True + SHORT default-False). T8's both-default-True means missing weekly Kumo signals auto-pass for BOTH directions, which is the same auto-pass-on-missing class as pivot W6/W7 but symmetrically applied. Worth queuing for the same `S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY` ticket (extend its scope to include T8 weekly Kumo defaults).

---

## Per-strategy walks

### T1. `strat_macd_crossover`

#### Step 1 — Code

[screener.py:644-650](backtest/signals/screener.py#L644-L650):

```python
def strat_macd_crossover(s):
    fl = s.get("macd_12_26_9_crossover_up")
    fs = s.get("macd_12_26_9_crossover_dn")
    return _strat3(fl, fs, "momentum",
        ["macd_12_26_9_crossover_up"], ["macd_12_26_9_crossover_dn"],
        ["MACD 12/26/9 crossed above zero  -  momentum turning positive"],
        ["MACD 12/26/9 crossed below zero  -  momentum turning negative"])
```

| Gate | Meaning | Threshold |
|---|---|---|
| **LONG** `macd_12_26_9_crossover_up` | MACD histogram crossed FROM <=0 TO >0 today — momentum turning positive | Boolean EVENT |
| **SHORT** `macd_12_26_9_crossover_dn` | MACD histogram crossed FROM >=0 TO <0 today — momentum turning negative | Boolean EVENT |

**Pure 1-gate strategy. The simplest in the cluster.**

#### Step 2 — Classify
- Category: `momentum` (per source declaration; trend-adjacent)
- Dual via `_strat3`
- STRATEGY_REGIME_AFFINITY: **no entry** → B291 direction-aware default
- Last touched: original implementation

#### Step 3 — Producer source + temporality
- `macd_12_26_9_crossover_up` / `_dn` at [technical.py:368-394](backtest/signals/technical.py#L368-L394). Cross-event = current hist sign-change from prior bar. **EVENT** signal.

#### Step 4 — Doc-vs-thesis
Context bullets accurate. "Momentum turning positive/negative" matches what the gate detects. ✅

#### Step 5 — OPEN_INVESTIGATIONS
No matches.

#### Step 6 — Missing-inverse / economic-symmetry / Step 1.5 avoid-branch
- Dual ✅ structurally symmetric.
- Producer cross_up vs cross_dn are mutually exclusive → `_strat3` avoid-branch is dead code (Step 1.5 record).
- Economic symmetry: MACD is direction-symmetric by construction (signed histogram). ✅ no asymmetry concern.

#### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None — strategy is clean | — |
| **F2** | Minimal context bullet only; could cite Appel 1979 *Moving Average Convergence-Divergence Trading Method* + note this is the SIMPLEST possible MACD strategy (no trend filter, no volume confirmation) | LOW |
| **F-timing-fragility** | 1 EVENT gate per direction — fine (timing is unambiguously on the EVENT) | — N/A |

**Options:**

| Option | Description |
|---|---|
| **(A)** F2 docstring add (Appel 1979 source citation + framing as "raw MACD cross — no filters"). **RECOMMENDED.** |
| (B) Status quo |
| (C) Add trend filter (ema_50_200_bullish/_bearish per B634 producer-additive symmetric pair). Could improve quality but adds a STATE gate to a clean 1-EVENT strategy. Trade-off: more selective, more co-correlated with `strat_supertrend_macd` (T10) which already has MACD + trend filters. |

**My recommendation: (A).** Clean 1-gate strategy; the raw cross is its identity. Adding filters duplicates T10 (`supertrend_macd`). Doc-only is the right touch.

---

### T2. `strat_macd_fast_crossover`

#### Step 1 — Code

[screener.py:653-659](backtest/signals/screener.py#L653-L659):

```python
def strat_macd_fast_crossover(s):
    fl = s.get("macd_8_21_5_crossover_up")
    fs = s.get("macd_8_21_5_crossover_dn")
    return _strat3(fl, fs, "momentum",
        ["macd_8_21_5_crossover_up"], ["macd_8_21_5_crossover_dn"],
        ["Fast MACD 8/21/5 crossed above zero  -  early momentum shift bullish"],
        ["Fast MACD 8/21/5 crossed below zero  -  early momentum shift bearish"])
```

Identical structure to T1 but uses MACD(8,21,5) instead of (12,26,9). Faster periods = earlier crossover = more signals + more noise.

#### Step 2 — Classify
- STRATEGY_REGIME_AFFINITY: **explicit `{"bull"}`** entry — DEFERRED per R5 manifest M1 (B617 KEPT as `# B418 cube override; direction-disagg validation pending`)
- Dual + single-direction-era entry = B271 family-bug PATTERN but **already on M1 deferred queue**

#### Step 3 — Producer source + temporality
- `macd_8_21_5_crossover_up` / `_dn` at [technical.py:368-394](backtest/signals/technical.py#L368-L394). Same compute path as T1 but with fast=8 slow=21 sig=5. **EVENT** signal.

#### Step 4 — Doc-vs-thesis
Context bullets accurate; "early momentum shift" honestly describes the faster-period nature.

#### Step 5 — OPEN_INVESTIGATIONS
No matches.

#### Step 6 — Missing-inverse / Step 1.5 avoid-branch
- Dual ✅ symmetric.
- Mutually exclusive crosses → avoid branch dead.

#### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None | — |
| F2 | Minimal context; could cite Appel + note the speed/noise trade-off | LOW |
| **F3 (DEFERRED)** | STRATEGY_REGIME_AFFINITY `{bull}` is a B271 family-bug candidate — dual strategy with single-direction entry — but DEFERRED per R5 manifest M1 / S5-REGIME-AFFINITY-21-DEFERRED. **No new ticket; no walk-time action.** | — |

**Options:**

| Option | Description |
|---|---|
| **(A)** F2 docstring add — note speed/noise + B418 cube source + R5 deferral. **RECOMMENDED.** |
| (B) Status quo |

**My recommendation: (A).**

---

### T3. `strat_hull_rsi`

#### Step 1 — Code

[screener.py:662-698](backtest/signals/screener.py#L662-L698) — 5 gates per direction:

```python
fl = (s.get("hull_bullish") and s.get("price_above_hull")
      and s.get("rsi_9", 50) > 50 and adx_trend_ok
      and above_200)
fs = (s.get("hull_bearish") and s.get("price_below_hull")
      and s.get("rsi_9", 50) < 50 and adx_trend_ok
      and (not above_200))
```

| Gate | EVENT/STATE | Meaning |
|---|---|---|
| `hull_bullish` / `hull_bearish` | **STATE** | Hull MA value > prior Hull MA value (slope-up) |
| `price_above_hull` / `price_below_hull` | **STATE** | Close vs Hull MA |
| `rsi_9 > 50` / `< 50` | **STATE** | 9-period RSI above/below midpoint |
| `adx_trending` or `adx>20` | **STATE** | ADX-14 > 25 (Wilder strength threshold) |
| `price_above_ema_200` / `(not above_200)` | **STATE** | 200-EMA regime gate (B358 cell-audit fix) |

**5 STATE gates per direction. ZERO EVENT gates.** Strategy fires on a continuous "everything is aligned bullish" composite — not on any specific timing event.

#### Step 2 — Classify
- STRATEGY_REGIME_AFFINITY: **B617 REMOVED** explicit entry (`{bull, neutral}`) — uses B291 direction-aware default
- Last touched: B358 (added 200-EMA regime gate) + B634 (symmetric producer swap)

#### Step 3 — Producer + temporality
- Hull MA at [technical.py:1083-1087](backtest/signals/technical.py#L1083-L1087) — slope sign of Hull(period=10) value vs prior bar (STATE — Hull is slow-moving)
- `price_above_hull` / `price_below_hull` — STATE
- All five gates STATE. No EVENT.

#### Step 4 — Doc-vs-thesis
Docstring present (B358 + B634 history). Honestly framed as a momentum-trend composite. ✅

#### Step 5 — OPEN_INVESTIGATIONS
No matches.

#### Step 6 — Missing-inverse / Step 1.5
- Dual symmetric ✅ (post-B634 producer-additive `hull_bearish` + `price_below_hull`).
- `hull_bullish` and `hull_bearish` are NOT strictly mutually-exclusive (Hull slope sign is binary so they could not both be true, but the relevant question is whether the FULL `fl ∧ fs` is structurally impossible). Inspecting: `fl` requires `hull_bullish` + `rsi>50` + `above_200`; `fs` requires `hull_bearish` + `rsi<50` + `not above_200`. Hull bullish vs bearish is mutually exclusive → avoid branch IS dead. ✅
- Economic symmetry: Hull is direction-symmetric; RSI threshold is symmetric around 50; 200-EMA is binary above/below. ✅

#### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None | — |
| F2 | Docstring present ✅ | — |
| **F-timing-fragility (s)** | **5 STATE gates, 0 EVENT gates per direction.** Strategy has NO bar-of-fire timing alpha — the "fire" is a continuous regime-alignment composite. CHECKLIST (s) HIGH severity if docstring claims timing attribution. Inspecting docstring: it doesn't claim "confirms the timing of" anything — says "Hull MA + RSI(9) momentum" + "ADX>20 cuts false-signal rate" + "200-EMA regime gate." This is honest STATE framing — no overclaim. So F-timing-fragility is **LOW** (design choice, not docstring lie). | LOW |

**The deeper question:** is a 5-STATE-gate composite a useful strategy? It fires on EVERY bar that meets the 5 conditions — which means the strategy is essentially "what % of the time is everything aligned bullish/bearish?" with regime-on-regime selectivity but no bar-of-fire trigger. Could fire 100+ days in a row in a sustained trend. The bar-of-fire entry into a 100-day trend at day 50 produces the same trade as entry at day 5. **The strategy may be over-firing on the "everything aligned" condition.** Worth measuring.

**Options:**

| Option | Description |
|---|---|
| **(A) Status quo** — let measurement + cube data validate. **RECOMMENDED** pending measured fires/yr. |
| (B) Add EVENT gate — e.g. `hull_cross_up` (slope-change EVENT) instead of `hull_bullish` (slope STATE). Would require producer addition. Reduces fire-count but adds timing alpha. |
| (C) Drop ADX gate — it's redundant with hull_bullish + 200-EMA + price_above_hull (all asserting "trending up"). Reviewer noted this kind of over-specification on W7. |

**My recommendation: (A) for now.** Per CHECKLIST (s) the strategy is honestly STATE-framed; not overclaiming. If measured fire-count is excessive (>>500/yr/direction), revisit with (B) or (C).

---

### T4. `strat_parabolic_sar_flip`

#### Step 1 — Code

[screener.py:908-914](backtest/signals/screener.py#L908-L914):

```python
def strat_parabolic_sar_flip(s):
    fl = (s.get("psar_flip_up") and s.get("adx_trending"))
    fs = (s.get("psar_flip_dn") and s.get("adx_trending"))
    return _strat3(fl, fs, "trend", ...)
```

| Gate | EVENT/STATE | Meaning |
|---|---|---|
| `psar_flip_up` / `psar_flip_dn` | **EVENT** | Parabolic SAR flipped from above-price → below-price (or vice versa) today — Wilder 1978 |
| `adx_trending` | **STATE** | ADX>25 |

#### Step 2 — Classify
- STRATEGY_REGIME_AFFINITY: **explicit `{"bear"}`** — DEFERRED per R5 manifest M1 (B617 KEPT)
- B271 family-bug PATTERN but already on M1 queue

#### Step 3-6 — Standard
- Producer at [technical.py:789-790](backtest/signals/technical.py#L789-L790) — BUG-055 RESOLVED true flip (not approximation). EVENT.
- ADX_trending STATE.
- Mutually exclusive flips → avoid branch dead.
- Economic symmetry ✅.

#### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None | — |
| F2 | No docstring; could cite Wilder 1978 *New Concepts in Technical Trading Systems* | LOW |
| F-timing-fragility | 1 EVENT + 1 STATE per direction. Timing on the flip-event is honest. ✅ | — |
| **F3 (DEFERRED)** | `{bear}` regime entry deferred per R5 M1 | — |

**Options:**

| Option | Description |
|---|---|
| **(A)** F2 docstring add (Wilder source + B358-era ADX-trending rationale). **RECOMMENDED.** |
| (B) Status quo |

**My recommendation: (A).**

---

### T5. `strat_parabolic_sar_flip_short`

#### Step 1 — Code

[screener.py:1911-1917](backtest/signals/screener.py#L1911-L1917):

```python
def strat_parabolic_sar_flip_short(s):
    fires = (s.get("psar_flip_dn") and s.get("adx_trending"))
    return _strat(fires, "short", "trend", ...)
```

Same gate set as T4 SHORT side, but as a single-direction strategy.

#### Step 2 — Classify
- STRATEGY_REGIME_AFFINITY: **explicit `{"bear", "crisis", "neutral"}`** — matches B291 SHORT default exactly
- Last touched: original implementation

#### Step 3-6 — Standard

#### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None | — |
| F2 | No docstring; could cite Wilder 1978 | LOW |
| **F-duplicate concern** | The gate set `psar_flip_dn AND adx_trending` is IDENTICAL to T4's SHORT side. This is **double-counting potential** — when T4's SHORT side fires (under {bear} regime affinity), T5 also fires (under {bear, crisis, neutral}). Need to clarify: are T4 and T5 redundant? | MEDIUM |
| F3 | Explicit regime entry `{bear, crisis, neutral}` EQUALS B291 SHORT default — entry is redundant but not wrong. | LOW |

**The duplicate-concern question:** T4 is dual `_strat3` so its SHORT side fires in `{bear}` (per the explicit `{bear}` affinity). T5 is single-direction SHORT and fires in `{bear, crisis, neutral}` (per its explicit entry which matches B291 default). So:
- In `bear`: both T4 SHORT side + T5 fire ← double-count
- In `crisis` / `neutral`: only T5 fires (T4 capped to bear)
- In `bull`: neither fires

This isn't strictly a bug (the engine accepts duplicate registrations) but the cube would log two trades on every T4-SHORT bar. **Owner-decision question:** delete T5 + expand T4's regime affinity to `{bear, crisis, neutral}` for the SHORT side?

But T4 is DUAL and the regime entry caps BOTH directions — so expanding to {bear, crisis, neutral} would also affect T4's LONG side (which currently fires in {bear} only — itself a B271 family-bug instance deferred per R5 M1).

**Cleanest resolution depends on the R5 manifest M1 resolution of T4's regime entry.** Until then: status quo + flag the duplication.

**Options:**

| Option | Description |
|---|---|
| **(A) Status quo** — flag duplication but defer resolution to R5 M1 closure. Note F2 docstring queued. **RECOMMENDED.** |
| (B) Delete T5 immediately (T4 SHORT side covers it albeit only in bear) — Loses crisis/neutral SHORT fires. |
| (C) Delete T5 + delete T4's `{bear}` regime entry → both directions of T4 fall back to B291 (LONG `{bull, neutral}`; SHORT `{bear, crisis, neutral}`) → T4 SHORT covers T5 fully. Touches B271 family-bug deferral; not action-safe per M1. |
| (D) Defer T5 to a separate "duplicate-cleanup" pass post-R5 |

**My recommendation: (A).** Don't touch the R5-deferred T4 affinity entry; flag T5/T4 duplication as a known issue post-R5.

---

### T6. `strat_tema_dema`

#### Step 1 — Code

[screener.py:917-924](backtest/signals/screener.py#L917-L924):

```python
def strat_tema_dema(s):
    fl = (s.get("tema_cross_up") and s.get("price_above_tema"))
    fs = (s.get("tema_cross_dn") and s.get("price_below_tema"))
    return _strat3(fl, fs, "trend", ...)
```

| Gate | EVENT/STATE | Meaning |
|---|---|---|
| `tema_cross_up` / `_dn` | **EVENT** | TEMA crossed above/below DEMA today (Patrick Mulloy 1994 triple-exponential MA system) |
| `price_above_tema` / `price_below_tema` | **STATE** | Close vs TEMA (B634 producer-additive symmetric pair) |

#### Step 2 — Classify
- STRATEGY_REGIME_AFFINITY: **explicit `{"bear"}`** — DEFERRED per R5 M1
- B271 family-bug pattern + already on queue

#### Step 3-6 — Standard
- Mutually exclusive crosses → avoid branch dead.
- 1 EVENT + 1 STATE per direction — honest timing.

#### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None — B634 already fixed positive-symmetric `price_below_tema` | — |
| F2 | No docstring; could cite Mulloy 1994 *Smoothing Data With Faster Moving Averages* | LOW |
| F3 (DEFERRED) | `{bear}` regime entry deferred per R5 M1 | — |

**Options:**

| Option | Description |
|---|---|
| **(A)** F2 docstring add. **RECOMMENDED.** |
| (B) Status quo |

**My recommendation: (A).**

---

### T7. `strat_ichimoku_tk_cross`

#### Step 1 — Code

[screener.py:927-939](backtest/signals/screener.py#L927-L939):

```python
def strat_ichimoku_tk_cross(s):
    fl = (s.get("ichi_tk_cross_up") and s.get("ichi_above_cloud"))
    fs = (s.get("ichi_tk_cross_dn") and s.get("ichi_below_cloud"))
    return _strat3(fl, fs, "trend", ...)
```

| Gate | EVENT/STATE | Meaning |
|---|---|---|
| `ichi_tk_cross_up` / `_dn` | **EVENT** | Tenkan-Sen crossed above/below Kijun-Sen today (Ichimoku Kinko Hyo, Hosoda 1969) |
| `ichi_above_cloud` / `ichi_below_cloud` | **STATE** | Close strictly above/below the Senkou Span A/B (Kumo) cloud |

#### Step 2 — Classify
- STRATEGY_REGIME_AFFINITY: **no entry** → B291 default
- Last touched: B634 sweep — converted from `not s.get("ichi_below_cloud")` (silent-gap NOT pattern + semantic drift "above OR in cloud") to positive `ichi_above_cloud` (strict above; in-cloud no longer fires)

#### Step 3-6 — Standard
- B634 already fixed the NOT pattern.
- Mutually exclusive crosses → avoid branch dead.
- Economic symmetry ✅.

#### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None — B634 fixed | — |
| F2 | No docstring; could cite Hosoda 1969 / Ichimoku Kinko Hyo + note the B634 strict-above semantic | LOW |

**Options:**

| Option | Description |
|---|---|
| **(A)** F2 docstring add. **RECOMMENDED.** |
| (B) Status quo |

**My recommendation: (A).**

---

### T8. `strat_ichimoku_cloud_breakout`

#### Step 1 — Code

[screener.py:942-973](backtest/signals/screener.py#L942-L973) — 4 gates per direction:

```python
weekly_long_ok = s.get("ichi_weekly_above_cloud", True)
weekly_short_ok = s.get("ichi_weekly_below_cloud", True)
fl = (s.get("ichi_above_cloud") and s.get("ichi_tk_bullish")
      and s.get("adx_trending") and weekly_long_ok)
fs = (s.get("ichi_below_cloud") and s.get("ichi_tk_bearish")
      and s.get("adx_trending") and weekly_short_ok)
```

| Gate | EVENT/STATE | Meaning |
|---|---|---|
| `ichi_above_cloud` / `ichi_below_cloud` | STATE | Daily close vs Kumo cloud |
| `ichi_tk_bullish` / `ichi_tk_bearish` | STATE | Tenkan vs Kijun (above/below, no cross requirement) |
| `adx_trending` | STATE | ADX>25 |
| `ichi_weekly_above_cloud` / `ichi_weekly_below_cloud` (default-True) | STATE | Multi-TF weekly Kumo position (Linda Bradford Raschke gate) |

**All 4 gates STATE per direction. ZERO EVENT.** Plus default-True on the weekly Kumo gate — same auto-pass-on-missing class as pivot W6/W7 + W8 (queued S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY).

#### Step 2 — Classify
- STRATEGY_REGIME_AFFINITY: **no entry** → B291 default
- Last touched: B207 (added weekly Kumo gate per Raschke multi-TF research)

#### Step 3 — Producer + temporality
All STATE — Ichimoku components are smoothed averages; cloud position is multi-bar accumulated state.

#### Step 4 — Doc-vs-thesis
Docstring present, cites Raschke + B207 rationale + acknowledges weekly gate default-True for backward-compat.

#### Step 5 — OPEN_INVESTIGATIONS
No matches.

#### Step 6 — Missing-inverse / Step 1.5
- Dual symmetric ✅.
- `ichi_above_cloud` vs `ichi_below_cloud` mutually exclusive → avoid branch dead.
- Economic symmetry ✅.

#### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None — B207 docstring honestly acknowledges default-True backward-compat | — |
| F2 | Docstring present ✅ | — |
| **F-timing-fragility (s)** | **4 STATE gates, 0 EVENT per direction.** Same fragility class as T3 Hull RSI — strategy fires on a continuous "everything aligned" composite. CHECKLIST (s) HIGH if docstring overclaims timing; docstring says "full bullish structure" + "multi-TF regime confirm" which is honestly STATE framing — no overclaim. **LOW** severity. | LOW |
| **F-default-True-symmetric** | Both `weekly_long_ok` AND `weekly_short_ok` default-True. Different asymmetry pattern than pivot W6/W7 (where LONG default-True + SHORT default-False) — here both are True. Net effect: when weekly Kumo signals are missing (insufficient daily history <260 bars), BOTH directions auto-pass the gate. Symmetric auto-pass-on-missing. Should be extended into the same severity-unification queue ticket. | MEDIUM (queue) |

**Options:**

| Option | Description |
|---|---|
| **(A) Status quo** + extend `S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY` ticket scope to include T8 weekly Kumo (will need a verification of weekly-Kumo emit-rate; if mostly emitted, the default doesn't matter; if often missing, the strategy is auto-passing frequently). **RECOMMENDED.** |
| (B) Swap both defaults to False (strict — require weekly Kumo data). Cuts fires on the early-history portion of the backtest where weekly Kumo isn't computable. Lossy. |
| (C) Defer all decisions to Stage 5 cube + measurement |

**My recommendation: (A).**

---

### T9. `strat_adx_initiation`

#### Step 1 — Code

[screener.py:976-983](backtest/signals/screener.py#L976-L983):

```python
def strat_adx_initiation(s):
    fl = (s.get("adx_cross_up") and s.get("adx_di_bull"))
    fs = (s.get("adx_cross_up") and s.get("adx_di_bear"))
    return _strat3(fl, fs, "trend", ...)
```

| Gate | EVENT/STATE | Meaning |
|---|---|---|
| `adx_cross_up` | **EVENT** | ADX(14) crossed up through 25 today (trend strength threshold; Wilder 1978) |
| `adx_di_bull` / `adx_di_bear` | **STATE** | DI+ > DI- (bullish) / DI- > DI+ (bearish) — direction reading |

**Interesting structure:** LONG and SHORT both share the SAME `adx_cross_up` EVENT — only the DI+/DI- direction-reading distinguishes. **They can theoretically both fire (avoid)** if `adx_di_bull` and `adx_di_bear` were both True, but they're mutually exclusive by definition (DI+ > DI- vs DI- > DI+).

#### Step 2 — Classify
- STRATEGY_REGIME_AFFINITY: **explicit `{"bear"}`** — DEFERRED per R5 M1
- B271 family-bug — already queue-resolved

#### Step 3 — Producer + temporality
- `adx_cross_up` EVENT (today's threshold cross from below)
- `adx_di_bull` / `adx_di_bear` STATE
- 1 EVENT + 1 STATE per direction — honest timing

#### Step 4-6 — Standard

#### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None (B634 already added `adx_di_bear` positive symmetric producer) | — |
| F2 | No docstring; could cite Wilder 1978 ADX system + note the DI-direction-reading approach | LOW |
| F3 (DEFERRED) | `{bear}` regime entry deferred per R5 M1 | — |

**Options:**

| Option | Description |
|---|---|
| **(A)** F2 docstring add. **RECOMMENDED.** |
| (B) Status quo |

**My recommendation: (A).**

---

### T10. `strat_supertrend_macd`

#### Step 1 — Code

[screener.py:986-994](backtest/signals/screener.py#L986-L994):

```python
def strat_supertrend_macd(s):
    fl = (s.get("supertrend_bullish") and s.get("macd_12_26_9_bullish") and s.get("adx", 0) > 20)
    fs = (s.get("supertrend_bearish") and s.get("macd_12_26_9_bearish") and s.get("adx", 0) > 20)
    return _strat3(fl, fs, "trend", ...)
```

| Gate | EVENT/STATE | Meaning |
|---|---|---|
| `supertrend_bullish` / `_bearish` | STATE | Supertrend indicator value above/below price (continuous regime) |
| `macd_12_26_9_bullish` / `_bearish` | STATE | MACD histogram > 0 / < 0 (continuous regime) |
| `adx > 20` | STATE | ADX-14 > 20 (Wilder strength) |

**3 STATE gates per direction. ZERO EVENT.** Same fragility class as T3 / T8.

#### Step 2 — Classify
- STRATEGY_REGIME_AFFINITY: **explicit `{"bull"}`** — DEFERRED per R5 M1
- B271 family-bug — queue-resolved

#### Step 3-6 — Standard
- All STATE.
- Supertrend bullish vs bearish mutually exclusive → avoid branch dead.
- Economic symmetry ✅ (B630 sweep added macd_bearish + supertrend_bearish positive symmetric).

#### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None (B630 fixed) | — |
| F2 | No docstring; could cite Supertrend (Olivier Seban) + MACD (Appel) + B418 cube override rationale | LOW |
| **F-timing-fragility (s)** | 3 STATE gates per direction. Continuous-alignment composite, no bar-of-fire EVENT. Same class as T3/T8. **LOW** severity since docstring doesn't overclaim timing. | LOW |
| F3 (DEFERRED) | `{bull}` regime entry deferred per R5 M1 | — |

**Options:**

| Option | Description |
|---|---|
| **(A)** F2 docstring add. **RECOMMENDED.** |
| (B) Status quo |
| (C) Replace `macd_bullish` (STATE) with `macd_crossover_up` (EVENT) on LONG, mirror for SHORT — adds timing alpha to a STATE composite. Trade-off: less selective day-to-day, more selective at the cross point. |

**My recommendation: (A).** Don't restructure pre-cube. (C) is a Stage 5+ design question.

---

## Bundled action items

If you approve a batch of these, my proposed implementation order:

### Tier 1 — definite ships (no judgment needed):
- T1 / T2 / T4 / T6 / T7 / T9 / T10 — F2 docstring adds (7 strategies)
- T5 — F2 docstring add + flag T4/T5 duplication as a known issue post-R5

### Tier 2 — defer pending measurement / R5:
- T3 `hull_rsi` — measurement determines if 5-STATE composite over-fires; possibly drop ADX or convert hull_bullish to hull_cross_up EVENT post-cube
- T8 `ichimoku_cloud_breakout` — extend `S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY` ticket scope to include T8 weekly Kumo defaults; no auto-fix
- T10 `supertrend_macd` — defer EVENT-gate consideration to Stage 5+

### Tier 3 — already in deferred queue (no walk-time action):
- T2 / T4 / T6 / T9 / T10 STRATEGY_REGIME_AFFINITY entries — all 5 are on `S5-REGIME-AFFINITY-21-DEFERRED` (B624 manifest M1); confirmed-and-noted, no new tickets

### Tier 4 — measurement gates:
- All 10 strategies pending `output_audit/fire_count_measured_trend_cluster.json` (background run); fire-count verdict may shift any of the above recommendations

---

## Owner decision form

Indicate per strategy. Quick-pick:

**T1 `macd_crossover`:** (A) F2 doc [RECOMMENDED] / (B) status quo / (C) add trend filter
**T2 `macd_fast_crossover`:** (A) F2 doc [RECOMMENDED] / (B) status quo
**T3 `hull_rsi`:** (A) status quo + measurement-gated decision [RECOMMENDED] / (B) add EVENT gate / (C) drop ADX
**T4 `parabolic_sar_flip`:** (A) F2 doc [RECOMMENDED] / (B) status quo
**T5 `parabolic_sar_flip_short`:** (A) F2 doc + flag T4/T5 duplication [RECOMMENDED] / (B) delete T5 / (C) delete T5 + delete T4 affinity entry / (D) defer
**T6 `tema_dema`:** (A) F2 doc [RECOMMENDED] / (B) status quo
**T7 `ichimoku_tk_cross`:** (A) F2 doc [RECOMMENDED] / (B) status quo
**T8 `ichimoku_cloud_breakout`:** (A) status quo + extend default-True queue ticket [RECOMMENDED] / (B) strict default-False / (C) Stage 5 defer
**T9 `adx_initiation`:** (A) F2 doc [RECOMMENDED] / (B) status quo
**T10 `supertrend_macd`:** (A) F2 doc [RECOMMENDED] / (B) status quo / (C) EVENT-gate restructure

### Format for your reply

Easiest: **type the option letters in order**, e.g.:

```
A A A A A A A A A A
```

(That's the recommendation slate — 9 F2 doc-only adds + T5 flag + T8 ticket-extend.)

Or per-strategy override:

```
T1=A T2=A T3=A T4=A T5=A T6=A T7=A T8=A T9=A T10=A
```

Measurement results from background run will append to this doc when available; any FAIL_FIRE_STARVED labels would shift Tier 2 strategies (T3/T8/T10) into deeper-redesign options similar to W5 in the pivot cluster doc.

Awaiting decisions.

---

## Cross-cluster status snapshot (post-B679 — index at [STAGE_4_CLUSTER_WALKS_INDEX.md](STAGE_4_CLUSTER_WALKS_INDEX.md))

> Added B679 format alignment. Trend cluster doc was companion to pivot cluster — reviewer findings absorbed into pivot doc per B652/B660 close.

8 cluster docs / ~138 strategies covered. Review status:

| Cluster | Doc | Strategies | Owner review | Iteration 2 ready |
|---|---|---|---|---|
| Pivot | [STAGE_4_PIVOT_CLUSTER_WALKS.md](STAGE_4_PIVOT_CLUSTER_WALKS.md) | ~10 | ✅ 2 rounds | (already iterated) |
| **Trend (THIS DOC)** | **[STAGE_4_TREND_CLUSTER_WALKS.md](STAGE_4_TREND_CLUSTER_WALKS.md)** | **~12** | **✅ Companion to pivot review** | **(already iterated)** |
| Smart Money | [STAGE_4_SMART_MONEY_CLUSTER_WALKS.md](STAGE_4_SMART_MONEY_CLUSTER_WALKS.md) | 41 | ✅ 2 rounds (B669 + B673 → B674) | (already iterated) |
| SMC | [STAGE_4_SMC_CLUSTER_WALKS.md](STAGE_4_SMC_CLUSTER_WALKS.md) | 18 | ❌ AWAITING | READY |
| ICT | [STAGE_4_ICT_CLUSTER_WALKS.md](STAGE_4_ICT_CLUSTER_WALKS.md) | 12 | ❌ AWAITING | READY |
| Breakout | [STAGE_4_BREAKOUT_CLUSTER_WALKS.md](STAGE_4_BREAKOUT_CLUSTER_WALKS.md) | 19 | ❌ AWAITING | READY |
| Event-driven | [STAGE_4_EVENT_DRIVEN_CLUSTER_WALKS.md](STAGE_4_EVENT_DRIVEN_CLUSTER_WALKS.md) | 10 | ❌ AWAITING | READY |
| Chart+Candle | [STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md](STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md) | 16 | ❌ AWAITING | READY |
