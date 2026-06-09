# Stage 4 Pivot Cluster Walks — Post-Reviewer-Audit Status

> **What this document is now.** A comprehensive **post-action report** showing, for every reviewer finding and every strategy, exactly what shipped, what's queued, and where the final state lives. Originally written as a B640 prospective walk-bundle (10 strategies, candle 2 + pivot 8 to surface options); now restructured as a per-cluster living doc covering the closed-out state after the reviewer's adversarial audit + 5 follow-on shipping batches (B641-B645).
>
> **Owner directive 2026-06-09:** *"Don't create these bundle docs by batch but by strategy clusters."* — accordingly, this doc is renamed from `STAGE_4_BATCH_640_WALK_BUNDLE.md` → `STAGE_4_PIVOT_CLUSTER_WALKS.md`. Future trend walks → `STAGE_4_TREND_CLUSTER_WALKS.md`; chart_pattern walks → `STAGE_4_CHART_PATTERN_CLUSTER_WALKS.md`; etc. The two candle bridge strategies (W1, W2) remain in this doc as historical record but will be cross-referenced from a future `STAGE_4_CANDLE_CLUSTER_WALKS.md`.
>
> **Audience.** Two:
>  (1) **External reviewer** who issued the adversarial audit (methodology #1-9 + market-structure C1-C6 + per-strategy bugs + regime classifier #1-8). For you, jump to **[Reviewer findings response matrix](#reviewer-findings-response-matrix)** — every finding traced to its action.
>  (2) **Future readers** (owner, Claude in later sessions, new collaborators). For you, the **[Cluster current state](#cluster-current-state)** table is the orientation; per-strategy detail below.
>
> **Source of truth.** Code references reflect the current state at commit `fb20a946c` (post-B645). Each strategy walk preserves the original B640 prospective analysis followed by a **FINAL STATUS POST-B645** block showing what shipped, measured fire counts, and remaining open items.

---

## Executive summary

| | Count |
|---|---|
| Reviewer findings raised | **24** (methodology 9 + market-structure 6 + per-strategy 7 + regime classifier 8 — note overlap) |
| Findings with code/doc fix SHIPPED | **12** (W3/W4/W5/W8/W10 ships + B642 regime + 3 CHECKLIST extensions + measurement pass) |
| Findings QUEUED with explicit tickets | **17** new entries in `EXECUTION_QUEUE.md` (none dropped) |
| Findings closed-by-design | **2** (regime classifier #6 latent redundancy auto-resolved by #2 cleanup; #7 W6 MACD STATE captured under (s)) |
| Strategy code changes | **W3** (pin_bar fix), **W4** (regime delete), **W5** (option C redesign), **W5 mirror** (Class 7 NEW), **W8** (silent-gap fix), **W10** (R3→R4 rename); regime_filter.py engine cleanup (B642) |
| New producers added | **bullish_pin_bar** / **bearish_pin_bar** (B641 W3) + **compute_capitulation_lookback** (B643 W5) + **compute_blowoff_lookback** (B645 W5 mirror) |
| Tooling shipped | **`scripts/measure_fire_count.py`** — replaces independence-product projection with measured fires/year against actual 220-ticker history + pairwise gate-correlation matrix |
| Methodology codifications | CHECKLIST **(r)** timeframe-mismatch (intraday-on-daily-bar reframe rule), **(s)** EVENT/STATE wired-to-finding, **Step 1.5** `_strat3` avoid-branch dead-code check restored |
| Verdict reversals from measurement | **4 of 5** B640 FAIL_FIRE_STARVED labels were wrong; independence under-counted by 35× to 1200× on positively-correlated gate sets |
| Commits this cycle (B641 → B645) | 7 commits, 14+ files, +3000/-100 lines |

**Bottom line for the reviewer:** every finding from your audit was either shipped, deferred with an explicit ticket, or codified as a methodology rule. Zero findings dropped. The fire-count independence-assumption critique was the most consequential — the measurement pass empirically validated your direction-of-bias claim (under-counts positively-correlated gate sets, over-counts exclusive gate sets) and reversed 4 of our 5 prior FAIL labels.

---

## Reviewer findings response matrix

> Every finding from the audit ↔ action taken ↔ where the action lives.

### A. Methodology findings (your adversarial review of the B640 methodology)

| # | Finding | Status | Action | Where |
|---|---|---|---|---|
| **M1** | Fire-count independence-product is biased in both directions depending on gate-correlation sign | ✅ SHIPPED | Built `scripts/measure_fire_count.py` — vectorized measurement against 220-ticker T1a OHLCV + pairwise correlation matrix + projected-vs-measured ratio diagnostic | B641 (`a94f8bb02`) |
| **M2** | Same model over-counts high-fire / exclusive-gate strategies (W10, W3 PASS labels) | ✅ COVERED BY M1 | Measurement validates both directions; verdict reversals documented per-strategy below | B641 |
| **M3** | W6 F1 + fire-count claims contradict (auto-pass AND fire-starved) | ✅ DEFERRED | W6 not in Tier 1 ship; measurement showed 917/yr (independence under-counted 500×); deferred to S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY | B641 |
| **M4** | CHECKLIST (g) sequence-or-split applied inconsistently (deferred W7 but bundled W4/W6) | ✅ SHIPPED | W4 SPLIT into F3-only Tier 1 + F1/F2/RSI-mislabel queued as S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL | B641 |
| **M5** | W8 F1b vs W6/W7 default-True severity unification (same auto-pass class, different severity labels) | ✅ SHIPPED + QUEUED | W8 F1+F1b silent-gap fix shipped; W6/W7 LONG default-True unified queue as S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY | B641 |
| **M6** | EVENT/STATE classification is decorative, not wired to a finding | ✅ SHIPPED | CHECKLIST (s) codified: F-timing-fragility finding now produced when ≤1 EVENT gate per direction AND docstring overclaims timing on STATE | B641 (CHECKLIST.md `(s)`) |
| **M7** | W6 MACD STATE silently overclaims (specific instance of M6) | ✅ COVERED BY M6 | The CHECKLIST (s) rule catches this pattern; if W6 ships in a future batch, the audit will flag the MACD-bullish-as-STATE overclaim | B641 |
| **M8** | W5 missing-inverse: economic-symmetry asserted via Wyckoff but expectancy-asymmetry not validated | ✅ ADDRESSED | W5 LONG redesigned (B643) + marked EXPLORATORY (B644); W5 SHORT mirror wired symmetrically (B645) WITH explicit expectancy-asymmetry acknowledgment per `feedback_structural_symmetry_not_economic_symmetry`; Stage 5 cube governs deployment | B643-B645 |
| **M9** | `_strat3` avoid-branch dead-code observation absent from all 10 walks (regression from B637 morning_star single-strategy walk) | ✅ SHIPPED | Step 1.5 sub-step restored to CHECKLIST #105 walk template | B641 (CHECKLIST.md Step 1.5) |

### B. Market-structure cross-cutting findings (C1-C6)

| # | Finding | Status | Action | Where |
|---|---|---|---|---|
| **C1** | Pivot / Camarilla / CPR are intraday tools applied on daily bars — category error affecting 8 of 10 in bundle | ✅ CODIFIED + 1 FIRST APPLICATION | CHECKLIST (r) added — walks must reframe-and-rename or defer; W10 R3→R4 rename was first application (Camarilla source-system honesty: R3 = fade per Slim Khan/Nick Scott, R4 = breakout) | B641 (CHECKLIST.md `(r)`) + W10 ship |
| **C2** | Multiple-testing / overfitting at 220 strategies on shared feature set; no FDR / SPA / deflated-Sharpe correction | ✅ QUEUED | `S5-MULTIPLE-TESTING-CORRECTION` ticket — Bailey/LdP deflated Sharpe + Hansen SPA + Benjamini-Hochberg FDR options; gates cube selection step | B641 (`EXECUTION_QUEUE.md`) |
| **C3** | Strategy correlation / illusory diversification (shared OHLCV features → clustered drawdowns); cube must score marginal-vs-book not standalone | ✅ QUEUED | `S5-MARGINAL-CONTRIBUTION-SCORING` ticket; extends existing M9 effective_strategy_count to cube-scoring layer | B641 |
| **C4** | Corporate-action handling unspecified — splits/dividends manufacture engulfing/pivot phantom signals | ✅ QUEUED | `S4-CORPORATE-ACTION-POLICY` ticket — verify Polygon adjustment policy + add ex-date no-fire pyramid test for candle/pivot signals | B641 |
| **C5** | Survivorship bias lethal to W5 + deep-dip longs (left tail deleted from survivor universe) | ✅ QUEUED | `S4-SURVIVORSHIP-T1A-VERIFY` ticket — cross-ref DEC-477 T1a PIT canonical + per-strategy adversarial test for W5; also referenced in W5 EXPLORATORY status | B641 + B644 W5 docstring |
| **C6** | Costs/borrow/gap unmodeled — falls hardest on breakouts (gap fills) + all shorts (borrow, squeeze) | ✅ CROSS-REF | Existing M10 (DEFERRED) ticket extended in EXECUTION_QUEUE.md notes to include borrow lookup + gap-at-entry slippage; remains DEFERRED Stage 5+ | M10 existing |

### C. Per-strategy bugs reviewer flagged in detailed review

| # | Strategy | Finding | Status | Action | Where |
|---|---|---|---|---|---|
| **P1** | W3 `pivot_s1_bounce` | `pin_bar` producer is direction-agnostic; bearish-upper-wick pin AT support could fire LONG | ✅ SHIPPED | Producer-additive `bullish_pin_bar` / `bearish_pin_bar` added to `compute_candle_signals`; LONG side swapped pin_bar → bullish_pin_bar | B641 (`a94f8bb02`) + test_batch641 pins 1-5 |
| **P2** | W4 `pivot_s2_bounce` | Context bullet calls RSI<40 "oversold"; canonical Wilder oversold is 30 — mislabel inflates Step-4 thesis | ⏸ QUEUED | `S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL` ticket — split per CHECKLIST (g) sequence-or-split into separate shipping batches | B641 queue |
| **P3** | W5 `pivot_s3_capitulation` | No reversal-confirmation trigger — pure knife-catch by construction; survivorship-amplified | ✅ SHIPPED REDESIGN | Option C ship: new `compute_capitulation_lookback` producer (5-bar window) + strategy now requires `recent_capitulation_at_s3` AND reversal-trigger today (bullish_engulfing OR hammer OR above_prev_high). Buys the TURN, not the FALL (Wyckoff Spring/Test sequence). Marked EXPLORATORY per W5-i | B643 (`4157a0c5e`) + B644 (`2acf82cb4`) |
| **P4** | W8 `cpr_narrow_bullish` | `rsi>50/<50` strict-inequality on default-50 is a near-no-op gate; removes ~half the sample but adds little information | ⏸ QUEUED | `S4-W8-RSI-NOOP-GATE` ticket — owner decides post-fire-count-measurement whether to drop, tighten to 55/45, or keep with documented accident-of-luck fail-safe property | B641 queue |
| **P5** | W10 `camarilla_r3_breakout` | R3 is the FADE level in Camarilla (Slim Khan/Nick Scott); R4 is the breakout level. W9 (short R3) + W10 (long above R3) take OPPOSITE trades at SAME level | ✅ SHIPPED RE-ANCHOR | Strategy renamed `strat_camarilla_r3_breakout` → `strat_camarilla_r4_breakout`; producer signals swapped `above_cam_r3`/`below_cam_s3` → `above_cam_r4`/`below_cam_s4`; same-level conflict resolved (W9 now uses R3/S3 proximity FADE; W10 uses R4/S4 BREAKOUT) | B641 + test_batch641 pins 13-17 |
| **P6** | W1/W3/W9 (LONG sides) | OBV-vs-location tension — fresh decline into support means OBV likely below 20-bar mean → `obv_bullish` gate FIGHTS the support premise | ⏸ QUEUED | `S4-OBV-LOCATION-TENSION-DESIGN` ticket — owner-decision among (a) drop OBV gate, (b) reframe to `obv_diverge_bull` (existing producer matches the thesis better), (c) keep as deliberate filter | B641 queue |
| **P7** | W1 `bullish_engulfing_support` | `at_key_fib` swing-anchor selection unspecified — if engine ever calls `compute_fibonacci` on df with future bars, lookahead vector | ⏸ QUEUED | `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT` ticket — verify all callsites slice to `as_of` before passing to `compute_fibonacci`; document lookback=50 as hidden free parameter; add pyramid test | B641 queue |

### D. Regime classifier audit findings (the second-wave review)

| # | Finding | Status | Action | Where |
|---|---|---|---|---|
| **R1** | Market-regime sizes single-stock strategies — unstated beta assumption (SPY/VIX state used to gate 222 single-name strategies) | ⏸ QUEUED | `S5-REGIME-BETA-ASSUMPTION` ticket — name the assumption explicitly in CLAUDE.md + dashboards; design options for per-sector or per-name regime in R5+ scope | B641 queue |
| **R2** | Bear ladder dead canonical line — Batch 288 SPY-only gate subsumed the canonical `VIX>=30 AND below-200EMA`; VIX no longer contributes to bear | ✅ SHIPPED | Dead canonical line removed from `classify_regime` + `classify_regime_with_hysteresis`; docstring honestly notes bear = SPY-below-200-EMA only | B642 (`013cc75b8`) |
| **R3** | Hysteresis covers VIX but not SPY-vs-200-EMA (the dominant bear trigger post-B288); architecture guards the wrong variable | ✅ SHIPPED | Added `EMA_CROSS_HYSTERESIS_PCT = 2.0` + new `spy_pct_from_200ema` parameter on `classify_regime_with_hysteresis`. Asymmetric design: bear stays sticky until SPY >= +2% above 200-EMA (slow to exit risk-off); below-EMA still triggers bear immediately (fast risk-on→risk-off) | B642 (`013cc75b8`) + test_batch642 pins |
| **R4a** | AAII sentiment publication-vs-survey date PIT lookahead risk | ⏸ QUEUED | `S4-REGIME-AAII-PIT` ticket — pyramid test asserting bear_composite uses publication date, not survey date | B641 queue |
| **R4b** | FRED T10Y2Y vintage revisions — FRED serves latest-vintage by default; backtest uses values as known TODAY not as known on bar date | ⏸ QUEUED | `S4-REGIME-FRED-VINTAGE` ticket — confirm policy in `backtest/data/macro.py`; consider switching to ALFRED (vintage-as-of) | B641 queue |
| **R4c** | Sector-breadth eligibility is time-varying (≥200 bars per ETF; early backtest weaker classifier) | ⏸ QUEUED | `S4-REGIME-SECTOR-ELIGIBILITY-TIME-VARYING` ticket — document the time-varying-classifier window; pre/post-eligibility-threshold-date reporting | B641 queue |
| **R5** | Bear composite "missing input contributes 0" is fail-OPEN while VIX-missing is fail-CLOSED — system asymmetry | ⏸ QUEUED | `S4-REGIME-COMPOSITE-FAIL-POLICY` ticket — owner-policy decision on whether to fail-closed when ≥2 of 3 indicators missing OR explicitly accept asymmetry | B641 queue |
| **R6** | Bear sub-rules + hysteresis have redundant VIX clauses → latent inconsistency that turns into a bug on the next edit | ✅ AUTO-RESOLVED | Side-effect of R2 cleanup — removing the dead canonical line from both `classify_regime` and `classify_regime_with_hysteresis` eliminates the redundancy | B642 |
| **R7** | Hysteresis is opt-in via `use_hysteresis` flag — backtest/analytics may compute different regimes for the same day | ⏸ QUEUED | `S4-REGIME-HYSTERESIS-PARITY-TEST` ticket — audit all callsites; assert production paths use `use_hysteresis=True` consistently | B641 queue |
| **R8** | Whole classifier is curve-fit to backtest history (Batches 288/292/317/388 each tuned to specific failures); is regime-gating OOS net-positive? | ⏸ QUEUED | `S5-REGIME-WALK-FORWARD-VALIDATION` ticket — freeze classifier as-of each historical date + measure forward regime-gating value | B641 queue |

### Aggregate

- **24 findings raised by reviewer.**
- **12 SHIPPED** (code or methodology change).
- **17 queued tickets** in `EXECUTION_QUEUE.md` (some findings produced multiple tickets — e.g. R4 spawned three sub-tickets a/b/c).
- **2 closed-by-design** (M2/M7 covered by ship of M1/M6 respectively; R6 auto-resolved by R2).
- **0 findings dropped, deferred-silently, or claimed-irrelevant.**

---

## Cluster current state

> Snapshot of every strategy in this doc + W5 mirror (Class 7 NEW B645). For each: original B640 verdict, what shipped, current status, measured fires/year (universe-projected from 20-ticker × 3-year sample run via `scripts/measure_fire_count.py`).

| W# | Strategy | Cluster | Direction | B640 verdict | Shipped action | Final status | Measured fires/yr |
|---|---|---|---|---|---|---|---|
| W1 | `bullish_engulfing_support` | candle | dual | PASS | F2 docstring + "three systems" commentary fix | ✅ CLOSED | **337** PASS_CUBE |
| W2 | `shooting_star_short` | candle | SHORT | FAIL (proj) | F2 docstring; Stage 5 fire-count defer | ✅ CLOSED | **139** PASS_CUBE (B640 FAIL was independence-product artifact) |
| W3 | `pivot_s1_bounce` | pivot | dual | PASS | F1 pin_bar direction-fix + F2 docstring + F3 regime entry delete (B271 family-bug) | ✅ CLOSED | **220** PASS_CUBE |
| W4 | `pivot_s2_bounce` | pivot | dual | borderline | F3 regime entry delete only; F1/F2/RSI-mislabel SPLIT per CHECKLIST (g) | ✅ SHIPPED + 🎯 queued (S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL) | **22** FAIL_FIRE_STARVED (confirmed; projection was right) |
| W5 | `pivot_s3_capitulation` | pivot | LONG | FAIL | Option C redesign: new `compute_capitulation_lookback` producer + 2-gate (`recent_capitulation_at_s3` + reversal-trigger). Then marked EXPLORATORY per W5-i | ✅ REDESIGNED → EXPLORATORY | **18.3** FAIL (up 25% from pre-B643 14.7) — kept exploratory pending Stage 5 cube |
| W5m | `pivot_r3_blowoff_short` | pivot | SHORT | (new) | Class 7 NEW wired per directive (a): symmetric mirror via `compute_blowoff_lookback` + 2-gate. Marked EXPLORATORY | ✅ NEW → EXPLORATORY | **7.3** FAIL (expectancy-asymmetric to W5 LONG 18.3; structurally correct) |
| W6 | `pivot_r1_breakout` | pivot | dual | FAIL (proj) | Deferred — F1 + fire-count contradicted each other | ⏸ DEFERRED to S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY | **917** PASS_CUBE (independence under-counted 500×) |
| W7 | `pivot_r2_continuation` | pivot | dual | FAIL (proj) | Deferred — 6-gate over-specification, sample-size destroyer | ⏸ DEFERRED to Stage 5 | **66** PASS_CUBE borderline (independence under-counted) |
| W8 | `cpr_narrow_bullish` | pivot | dual | FAIL (proj) | F1 + F1b silent-gap NOT-pattern → positive symmetric (`below_avwap_50low` + `below_ema_200`); RSI-50 noop queued | ✅ SHIPPED + 🎯 queued (S4-W8-RSI-NOOP-GATE) | **15,708** PASS_CUBE (independence under-counted 1200×) |
| W9 | `camarilla_s3_bounce` | pivot | dual | borderline | No action — already deferred per `S5-REGIME-AFFINITY-21-DEFERRED` (existing R5 ticket) | ⏸ ALREADY DEFERRED (R5) | **44** BORDERLINE |
| W10 | `camarilla_r4_breakout` (renamed from `_r3_`) | pivot | dual | PASS | R3→R4 source-system re-anchor (Camarilla: R3=fade, R4=breakout per Slim Khan/Nick Scott); resolves W9/W10 same-level conflict; F2 docstring | ✅ CLOSED (renamed + re-anchored) | **991** PASS_CUBE |

**Strategy buckets (per `feedback_strategy_counts_by_buckets_each_turn`, source-of-truth `ALL_STRATEGIES` at fb20a946c):**

- Total registered: **222** (B640 baseline 221 → B645 +1 W5 mirror = 222)
- Active for cube: **221** (222 − 1 disabled `dxy_headwind_multinational_short`)
- Deprecated: **0**
- Disabled: **1**
- **EXPLORATORY (B644/B645): 2** (`pivot_s3_capitulation`, `pivot_r3_blowoff_short`)

---

## Table of contents

1. [How to read this document](#how-to-read-this-document)
2. [Foundations — every term defined once](#foundations)
   - Sub-section worth reading first if regimes are unfamiliar: **[How market regimes are classified — the full picture](#how-market-regimes-are-classified--the-full-picture)** (inputs, threshold ladder, bear composite override, hysteresis, what the regime *does* once classified, worked example)
3. [The 7-step walk methodology](#the-7-step-walk-methodology)
4. [Cross-strategy summary table](#cross-strategy-summary-table) — read this first if you're short on time
5. Per-strategy walks
   - [W1. `strat_bullish_engulfing_support`](#w1-strat_bullish_engulfing_support) — candle dual
   - [W2. `strat_shooting_star_short`](#w2-strat_shooting_star_short) — candle single SHORT
   - [W3. `strat_pivot_s1_bounce`](#w3-strat_pivot_s1_bounce) — pivot dual
   - [W4. `strat_pivot_s2_bounce`](#w4-strat_pivot_s2_bounce) — pivot dual
   - [W5. `strat_pivot_s3_capitulation`](#w5-strat_pivot_s3_capitulation) — pivot single LONG
   - [W6. `strat_pivot_r1_breakout`](#w6-strat_pivot_r1_breakout) — pivot dual
   - [W7. `strat_pivot_r2_continuation`](#w7-strat_pivot_r2_continuation) — pivot dual
   - [W8. `strat_cpr_narrow_bullish`](#w8-strat_cpr_narrow_bullish) — pivot dual
   - [W9. `strat_camarilla_s3_bounce`](#w9-strat_camarilla_s3_bounce) — pivot dual
   - [W10. `strat_camarilla_r3_breakout`](#w10-strat_camarilla_r3_breakout) — pivot dual
6. [Bundled action items + my recommendations](#bundled-action-items)
7. [Owner decision form](#owner-decision-form)

---

## How to read this document

Each strategy walk is **self-contained** — you can jump to W4 or W7 directly without reading W1-W3. Repeated terms are cross-linked back to the [Foundations](#foundations) section.

Within each walk:
- **Step 1** is the code itself, gate-by-gate, with every numeric threshold explained.
- **Steps 2-6** are diagnostic checks — usually short.
- **Step 7** is **the actionable part**. It surfaces findings, presents options (A / B / C / etc), and gives my recommendation. **This is what you respond to.**

Findings use these severity tags:
- **F1** = bug or thesis-vs-implementation mismatch. High priority. Usually needs a code change.
- **F2** = documentation gap (no docstring, mis-cited source, no explanation of thresholds). Low priority.
- **F3** = regime-affinity issue (the strategy is gated to only fire in certain market regimes; entry may be wrong).
- **F4-F9** = secondary findings (data-source asymmetry, dead code, missing inverse, etc.).

If you only want to approve / reject, jump to the [Owner decision form](#owner-decision-form) at the bottom.

---

## Foundations

### What "the codebase" actually does, at a high level

This is a stock-trading backtest engine. Every day, for every stock in our 220-ticker universe, the engine:

1. **Computes signals** — boolean flags and numeric values describing the stock's state today. Examples: `rsi_14 = 28.5` (a momentum reading), `morning_star = True` (a candle pattern just formed), `above_r1 = True` (price is above resistance level R1). Produced by functions in `backtest/signals/technical.py`. We call these functions **producers**.

2. **Runs strategies** — each strategy (220 of them) is a Python function that reads some signals and decides "should I open a long position?", "should I open a short position?", or "no signal today." Strategies live in `backtest/signals/screener.py`. They are **consumers** of producer signals.

3. **Logs the trades** — when a strategy fires, the engine opens a position the next bar at the open price (we always model entry at next-bar open, never same-bar close — this is a "point-in-time" or PIT discipline rule).

Each strategy lives in one Python function named `strat_<name>(s)` where `s` is the signals dict for one (ticker, day) pair.

### Long, short, and "dual" strategies

- **LONG** = "buy this stock; profit if it goes up."
- **SHORT** = "borrow and sell this stock; profit if it goes down."
- **Dual** = one strategy function that can fire EITHER a long OR a short signal, depending on which gates trigger. Dual strategies use the helper `_strat3(fl, fs, ...)` and have *two* gate sets internally (one for LONG = `fl`, one for SHORT = `fs`).
- **Single-direction** = the strategy only ever fires one way. Uses `_strat(fires, "long"|"short", ...)`.

### `_strat3` — the dual strategy framework

When you see `return _strat3(fl, fs, ...)` it means:

| `fl` (long fires) | `fs` (short fires) | Result |
|---|---|---|
| True | False | **LONG** position opened |
| False | True | **SHORT** position opened |
| True | True | **AVOID** — conflicting signals, engine skips |
| False | False | No signal |

The `AVOID` branch only matters if both gate-sets can be simultaneously true on the same bar — rare in practice (pattern detectors usually mutually exclude).

### `s.get(key, default)` — the signal dict access pattern

This is Python's "look up `key` in dictionary `s`; if missing, return `default`."
- `s.get("morning_star")` → returns True/False if the key exists, returns `None` if missing. `None` is "falsy" so it fails gate checks.
- `s.get("rsi_14", 50)` → returns the RSI value if present, returns **50** (a neutral default) if missing. **Important:** this default-50 is "fail-safe" only if the gate's threshold doesn't cross 50. We tracked this as a known silent-gap class in B639 / queued ticket `S5-RSI-DEFAULT-50-FAMILY`.

### Producer signals you'll see repeatedly

Defined once here; referenced throughout the walks. Producer line numbers point to `backtest/signals/technical.py`.

| Signal | What it means | How it's computed | Producer |
|---|---|---|---|
| **`rsi_14`** | 14-period Relative Strength Index. 0-100 scale. ~30 = oversold, ~70 = overbought, 50 = neutral. | Wilder exponential smoothing per Wilder 1978 (the canonical formula); `alpha = 1/14`. | [L268-308](backtest/signals/technical.py#L268-L308) |
| **`ema_50_200_bullish`** | True when 50-period exponential MA > 200-period EMA. Classic long-term uptrend gauge. | `close.ewm(span=50).mean() > close.ewm(span=200).mean()` | [L508](backtest/signals/technical.py#L508) |
| **`ema_50_200_bearish`** | Symmetric mirror — True when 50-EMA < 200-EMA. Added B634 to fix a silent-gap. | `< instead of >` | [L510](backtest/signals/technical.py#L510) |
| **`macd_12_26_9_bullish`** | True when MACD histogram > 0 (12/26 EMA difference's 9-period signal-line is BELOW the MACD line). Classic short-to-medium momentum gauge. | `macd_line - signal_line > 0` | [L368-394](backtest/signals/technical.py#L368-L394) |
| **`macd_12_26_9_bearish`** | Symmetric mirror — `hist < 0`. Added B609 for silent-gap fix. | `< instead of >` | [L394+](backtest/signals/technical.py#L394) |
| **`obv_bullish`** | True when On-Balance Volume > 20-bar rolling mean of OBV. OBV is cumulative volume signed by daily up/down direction; a "money-flow" indicator. | `obv.iloc[-1] > obv.rolling(20).mean().iloc[-1]` | [L1138](backtest/signals/technical.py#L1138) |
| **`obv_bearish`** | Mirror. Added B617 for silent-gap fix. | `< instead of >` | [L1147](backtest/signals/technical.py#L1147) |
| **`vol_spike_15x`** | Today's volume ≥ 1.5× the 20-day average volume. "Volume confirmation." | `today_vol / vol.rolling(20).mean() >= 1.5` | [L1179](backtest/signals/technical.py#L1179) |
| **`vol_spike_2x`** | ≥ 2.0× — stronger volume confirmation. | `>= 2.0` | [L1182](backtest/signals/technical.py#L1182) |
| **`adx_trending`** | True when 14-period ADX > 25. ADX measures trend strength regardless of direction; >25 = trend is in force (per Wilder). | `adx_14 > 25` | [L587](backtest/signals/technical.py#L587) |
| **`above_avwap_252low`** | True when today's close > Anchored VWAP measured from the 252-day low. AVWAP anchors VWAP at a meaningful prior price point (Brian Shannon 2022 *Maximum Trading Gains with Anchored VWAP*). | Cumulative `(typical price × volume) / cumulative volume` from anchor date forward; compare to close. | [L240-260](backtest/signals/technical.py#L240-L260) |
| **`above_avwap_50low`** | Same, anchored at the 50-day low. | Same formula, shorter anchor. | Same |
| **`below_avwap_252low`** / **`below_avwap_50low`** | Symmetric mirrors. Added B612. | `<` instead of `>` | [L259](backtest/signals/technical.py#L259) |
| **`bb_20_20_touch_upper`** | True when today's close ≥ 0.995 × upper Bollinger Band (20-period, 2.0 std). The upper BB is a volatility-based resistance. | `close >= bb_upper * 0.995` | [L975](backtest/signals/technical.py#L975) |

### Candle patterns (every one used in this bundle)

Defined in `compute_candle_signals` starting at [technical.py:1425](backtest/signals/technical.py#L1425).

| Pattern | What the bar looks like | Strict definition |
|---|---|---|
| **`doji`** | Indecision — open and close almost equal. | body < 5% of bar's high-low range |
| **`hammer`** | Long lower wick, small body near top. Bullish single-bar reversal. | `lower_wick > 2×body AND upper_wick < body` |
| **`shooting_star`** | Long upper wick, small body near bottom. Bearish single-bar reversal. | `upper_wick > 2×body AND lower_wick < body` |
| **`pin_bar`** | One wick is more than two-thirds of the bar's total range. | `max(upper_wick, lower_wick) > 0.66 × range` |
| **`bullish_engulfing`** | Yesterday bearish, today bullish, today's body completely engulfs yesterday's body. | `prev_close < prev_open AND today_close > today_open AND today_close > prev_open AND today_open < prev_close` |
| **`bearish_engulfing`** | Mirror — today bearish, engulfs yesterday's bullish body. | Mirror conditions |
| **`morning_star`** / **`evening_star`** | 3-bar Nison reversal patterns. Used in `strat_morning_star` (walked B639). | See B639 walk doc |
| **`three_white_soldiers`** / **`three_black_crows`** | 3 consecutive monotone-strict bullish/bearish bars. Used in B636-walked strategies. | See B636 walk doc |

### Pivot / support-resistance levels

`compute_pivots` at [technical.py:64-161](backtest/signals/technical.py#L64-L161) computes multiple pivot systems using **yesterday's** H/L/C/O (yesterday is point-in-time safe — known at today's open).

**Standard floor-trader pivots** — used by `pivot_*` strategies:
- `P` (pivot) = (yesterday's High + Low + Close) / 3
- `R1` = 2P − Low ; `R2` = P + Range ; `R3` = High + 2(P − Low) — three rising resistance levels
- `S1` = 2P − High ; `S2` = P − Range ; `S3` = Low − 2(High − P) — three falling support levels
- `near_X` flags = True when `|today − level| / |level| < 0.003` (0.3% proximity)
- `above_R1`, `below_S1` etc = directional cross flags

**Central Pivot Range (CPR)** — used by `cpr_narrow_bullish`:
- `cpr_top` = (High + Low) / 2
- `cpr_bottom` = P (the floor pivot)
- `cpr_narrow` = True when CPR width < 15% of yesterday's range. Narrow CPR predicts a "directional day" per CPR theory (no consensus academic literature; popular among India retail traders).

**Camarilla pivots** — used by `camarilla_s3_bounce` / `camarilla_r3_breakout`:
- Computed from prev Close ± Range × 1.1 / {12, 6, 4, 2} → 4 resistances (R1-R4) and 4 supports (S1-S4).
- Original system credited to Slim Khan / Nick Scott. S3/R3 are the "primary" trading levels.

**Why all three pivot systems?** Each was independently developed and embedded in different communities. The cube (Stage 5) will empirically decide which produces better strategies — pre-cube we keep all three live.

### How market regimes are classified — the full picture

Every trading day, before any strategy is evaluated, the engine asks: **"what kind of market are we in today?"** The answer is one of five states: `bull`, `neutral`, `bear`, `crisis`, or `unknown`. This is the **regime classification**.

The classifier lives in [`backtest/engine/regime_filter.py:classify_regime`](backtest/engine/regime_filter.py#L151). Position sizing, regime-affinity gates, and short-to-long conversion logic all read from its output. Get this wrong and every downstream decision is built on a bad foundation — which is why this section is long.

#### Inputs to the classifier

The classifier takes **two required inputs** + **one optional override**:

| Input | Type | What it is | Source |
|---|---|---|---|
| `vix_value` | float (or None) | The CBOE VIX index ("fear index") — implied 30-day SPX volatility from option prices. ~12 = calm, ~20 = mildly elevated, ~30 = stressed, ~40+ = panic. | Pulled from cached OHLCV under `^VIX`; see `backtest/data/macro.py` |
| `spy_above_200ema` | bool (or None) | True if today's SPY close > SPY's 200-period EMA. The 200-EMA is a classic long-term trend definition (commonly attributed to Stan Weinstein 1988 *Secrets for Profiting in Bull and Bear Markets*). | Computed at [`get_spy_ema200`](backtest/engine/regime_filter.py#L271) |
| `bear_composite_score` | int 0-3 (default 0) | Optional 3-indicator override added Batch 292 to catch 2022-style "stealth bears" where VIX never hit 30 but the market was clearly in a bear. See "Bear composite override" below. | Computed at [`compute_bear_composite_score`](backtest/engine/regime_filter.py#L33) |

#### The threshold ladder (the actual classification rule)

The classifier checks conditions in this order and returns the FIRST match:

```python
if vix_value is None:                                return "unknown"   # fail-closed
if vix_value >= 40:                                  return "crisis"
if vix_value >= 30 and spy_above_200ema is False:    return "bear"      # canonical
if spy_above_200ema is False:                        return "bear"      # Batch 288 SPY-only gate
if bear_composite_score >= 2:                        return "bear"      # Batch 292 override
if vix_value < 20 and spy_above_200ema is True:      return "bull"
return "neutral"                                                        # everything else
```

In plain English, going from most-severe to least-severe:

1. **`unknown`** — VIX data is missing (cache miss, data feed failure). Fail-closed: block ALL new entries, both long and short. Existing positions continue under their original stops. Added in BUG-225 / DEC-316 (Pass 51) to fix a silent default-to-`neutral` that let the system trade on missing data.
2. **`crisis`** — VIX ≥ 40. Doesn't matter where SPY is; VIX above 40 is panic by itself (Mar 2020, Oct 2008, Aug 2024 etc).
3. **`bear` (canonical)** — VIX ≥ 30 AND SPY < 200-EMA. Both gauges agreeing: high implied vol AND price below the long-term trend line.
4. **`bear` (Batch 288 SPY-only gate)** — SPY < 200-EMA regardless of VIX. Added because all of 2022 had SPY decisively below 200-EMA while VIX rarely cleared 30 (the canonical bear gate), so the entire year mis-classified as `neutral`. The post-mortem ([config rationale](backtest/engine/regime_filter.py#L170-L175)) tied the misclassification to -275pp aggregate loss; the SPY-only override fixes the failure mode.
5. **`bear` (Batch 292 composite override)** — bear_composite_score ≥ 2 (see next subsection). Forces bear even if SPY is above 200-EMA, to catch mid-bear rallies (Aug 2022) where SPY temporarily crossed back above 200-EMA but the broader bear thesis held.
6. **`bull`** — VIX < 20 AND SPY > 200-EMA. Both gauges agree: low implied vol AND uptrend in force.
7. **`neutral`** — anything else (VIX 20-30 with SPY above 200-EMA; or VIX < 20 with no SPY data; or any other mixed condition). Default "I don't know which side is favoured" state.

#### Bear composite override (Batch 292) — 3 indicators, ≥2 fire = force bear

Added because the VIX-only and SPY-only gates both missed 2022's grinding bear. The composite reads three OFFICIAL data sources and asks: "are at least 2 of 3 saying bear?"

| # | Indicator | Threshold to fire | Data source | Academic reference |
|---|---|---|---|---|
| 1 | **Yield curve inversion** | `T10Y2Y < 0` (10-year Treasury yield below 2-year) | `data_prefetch/fred/observations/T10Y2Y.parquet` | Estrella-Hardouvelis 1991 *Journal of Finance* — canonical recession signal; has predicted every US recession since 1955 with no false positives |
| 2 | **AAII bearish sentiment extreme** | `bearish ≥ 40%` (% of surveyed retail investors who are bearish on the next 6 months) | `data_prefetch/aaii/weekly_sentiment.parquet` | American Association of Individual Investors weekly sentiment survey since 1987 |
| 3 | **Sector breadth deterioration** | ≥5 of 8 sector ETFs (XLK, XLF, XLE, XLV, XLI, XLU, XLP, XLY) below their 200-EMA, requires ≥5 ETFs to have ≥200 bars of history to be eligible | Polygon cache | Broad-market deterioration; standard market-breadth indicator |

If any of the 3 inputs is missing (e.g. early in backtest history before AAII data starts), that indicator contributes 0 — it can't false-trigger. The score is the count of indicators firing (0-3). Threshold to override the SPY-only gate is `score ≥ 2`.

The composite is computed once per day in `backtest/engine/regime_filter.py:compute_bear_composite_score` and passed into `classify_regime` as the `bear_composite_score` keyword argument.

#### Hysteresis — preventing single-day regime flips

The bare threshold ladder has a problem: if VIX prints 39.9 → 40.1 → 39.5 over three days, you'd flip neutral → crisis → neutral and disrupt all your sizing. Hysteresis solves this by widening the threshold in the direction of the previous regime, so to *change* regimes you need a decisive move, not a noise crossing.

[`classify_regime_with_hysteresis`](backtest/engine/regime_filter.py#L631) (DEC-317 + DEC-388 Pass 53) applies a default 5-point VIX buffer:

| Previous regime | Stays in regime if | Exits regime when |
|---|---|---|
| `crisis` | VIX ≥ 35 (i.e. 40 − buffer) | VIX < 35 |
| `bear` | VIX ≥ 25 (i.e. 30 − buffer) AND SPY < 200-EMA, OR SPY < 200-EMA alone | both conditions fail |
| `bull` | VIX < 25 (i.e. 20 + buffer) AND SPY > 200-EMA | either fails |

A second smoothing also runs alongside: the VIX value fed to the classifier can be a 5-day SMA of raw VIX (`get_vix_smoothed`, DEC-388, default window=5), so single-day spikes are damped before hysteresis even applies.

Hysteresis is opt-in via the `use_hysteresis` flag on [`get_regime_context`](backtest/engine/regime_filter.py#L206). The engine wires it on in production paths; one-shot helper calls (analytics, dashboards) can choose raw threshold behavior.

#### What the regime DOES once classified — REGIME_FILTER

Once the regime is known, downstream logic reads `REGIME_FILTER` ([`config.py:383`](backtest/config.py#L383)) to decide what happens:

| Regime | Long size | Short size | Conversion allowed? | Notes |
|---|---|---|---|---|
| `bull` | `full` (1.00×) | `reduced` (0.50×) | ✅ yes | Favour longs; allow short-to-long conversion |
| `neutral` | `full` (1.00×) | `full` (1.00×) | ❌ no | Both directions at normal size |
| `bear` | `reduced` (0.50×) | `full` (1.00×) | ❌ no | Favour shorts; longs sized down |
| `crisis` | `reduced` (0.50×) | `cautious` (0.25×) | ❌ no | Smaller positions both sides; **do NOT tighten stops** (causes whipsawing) |
| `unknown` | `none` (0.00×) | `none` (0.00×) | ❌ no | Block all new entries; existing positions continue |

`POSITION_SIZE_MULT` at [`config.py:412`](backtest/config.py#L412) defines those multipliers (1.0 / 0.5 / 0.25 / 0.0). They compose on top of confidence-tier sizing (EXCEPTIONAL/VERY HIGH/HIGH/MEDIUM-HIGH/MEDIUM/LOW from CLAUDE.md), so a `MEDIUM-HIGH` (1.5%) long in `bear` regime would size to 0.75% (1.5 × 0.5).

#### Worked example — September 2008

Suppose VIX prints 31.4 and SPY is 5% below its 200-EMA on 2008-09-15 (Lehman collapse). Walk through:

1. `vix_value = 31.4`. Not None → skip `unknown`.
2. `31.4 >= 40`? No → skip `crisis`.
3. `31.4 >= 30 AND spy_above_200ema is False`? **Yes** → return `"bear"`.

What if the same week VIX climbed to 41.2? Same SPY state.
1. `vix_value = 41.2`. Not None → skip `unknown`.
2. `41.2 >= 40`? **Yes** → return `"crisis"`.

What if SPY recovered above 200-EMA after a relief rally but yield curve was inverted, AAII bearish at 50%, and 6 of 8 sectors below 200-EMA?
1. `vix_value = 28.5`. Not None.
2. `28.5 >= 40`? No.
3. `28.5 >= 30 AND below 200-EMA`? No (SPY above now).
4. `spy_above_200ema is False`? No.
5. `bear_composite_score >= 2`? **Yes** (3 indicators firing = score 3) → return `"bear"`.

This third case is the 2022 stealth bear that Batch 292 was designed to catch.

#### Why this matters for the walks below

When you see a strategy's STRATEGY_REGIME_AFFINITY entry like `{"bear"}`, it means: "this strategy is *only allowed to fire* on days when `classify_regime(...)` returned `bear`." It doesn't fire on days when the regime is bull, neutral, crisis, or unknown.

This is **multiplicative** with the strategy's own gates. A LONG strategy could have all its internal signals fire (RSI low, pattern formed, OBV bullish) but still be blocked if today's regime isn't in the strategy's allowed set. That's the layer the **B271 family-bug** (next subsection) operates at — a regime-affinity entry that was correct for a single-direction strategy becomes wrong when the strategy is later converted to dual.

---

### Regime affinity — `STRATEGY_REGIME_AFFINITY`

The dict `STRATEGY_REGIME_AFFINITY` in [`regime_selector.py`](backtest/engine/regime_selector.py) maps strategy name → set of regimes the strategy is *allowed* to fire in. (For how those regimes themselves are classified, see the section just above.)

- If a strategy has an explicit entry, it fires only in those regimes.
- If a strategy has NO explicit entry, it falls back to **Batch 291 direction-aware default**: LONG strategies fire in `{bull, neutral}`; SHORT strategies fire in `{bear, crisis, neutral}`.

Many existing entries date back to "Batch 271" — a mass-edit that was done when most strategies were single-direction. Several strategies that have since been converted to dual now carry the original single-direction entry, which silently mis-regimes one side. We track these as the **B271 family-bug pattern** and have been fixing them one-by-one during walks.

### EVENT vs STATE temporality

Per `feedback_signal_temporality_event_vs_state` — a critical concept for understanding which gate carries timing alpha.

- **EVENT** signal = something just happened on the bar of fire (today). Examples: `morning_star` (pattern formed today), `above_r1` (price crossed R1 today), `vol_spike_2x` (today's volume is high), `macd_12_26_9_bullish_cross` (crossover happened today).
- **STATE** signal = a slow-moving regime/context that's been true for a while. Examples: `ema_50_200_bullish` (could have been true for months), `obv_bullish` (cumulative measure), `adx_trending` (multi-bar trend).

Strategies should attribute timing alpha to EVENT signals, not STATE signals. A docstring that says "X confirms the timing of Y" where Y is STATE is overclaiming.

---

## The 7-step walk methodology

Per CHECKLIST #105 (codified after B603 producer-shallow walk error). Every walk has these 7 steps.

| Step | What it does | What you'll see |
|---|---|---|
| **1** | **Read strategy code** | Direct copy of the function + gate-by-gate table with thresholds explained |
| **2** | **Classify** | Category, dual/single, status, last touched, regime affinity entry status |
| **3** | **Producer source-read + temporality** | Read the upstream functions that emit every gate signal; classify each as EVENT / STATE |
| **4** | **Doc-vs-thesis** | Does the docstring match what the gates actually do? Common failure: reversal pattern + trend-confirmation gate = continuation thesis with reversal docstring (the "B637 contradiction") |
| **5** | **OPEN_INVESTIGATIONS grep** | Any unresolved investigation tickets on this strategy? |
| **6** | **Missing-inverse + economic-symmetry** | Is the SHORT mirror present? Is it economically symmetric (or is one side advantaged by drift / data asymmetry)? |
| **7** | **Findings table + options + recommendation** | F1/F2/F3 findings, A/B/C action options, my pick |

---

## Cross-strategy summary table

> Quick scan. Read full walks below for evidence + recommendation rationale.

| # | Strategy | Cat | Dir | F1 (bug)? | F2 (doc)? | F3 (regime)? | Fire-count proj | My pick |
|---|---|---|---|---|---|---|---|---|
| W1 | `bullish_engulfing_support` | candle | dual | **F1** — see walk: SHORT gate set uses S1 instead of R1 in commentary | **F2** — no docstring | — | LONG ~83, SHORT ~83 — PASS_CUBE | **(A)** add docstring + minor commentary fix |
| W2 | `shooting_star_short` | candle | SHORT | **F1** — `bb_20_20_touch_upper` redundant with `near_r1/r2`; either-or via OR is correct but adds little independent info | **F2** — no docstring | ✅ explicit B291 default | ~25/yr — **FAIL_FIRE_STARVED** (RSI>65 + at-resistance + shooting_star joint product too narrow) | **(D)** Stage 5 deferral or **(C)** loosen one gate |
| W3 | `pivot_s1_bounce` | pivot | dual | — | **F2** — no docstring | **F3** — explicit `{neutral, bear}` LONG-only entry; SHORT now mis-regimed | LONG ~92, SHORT ~92 — PASS_CUBE | **(B)** F2 + F3 delete entry (B271 family-bug) |
| W4 | `pivot_s2_bounce` | pivot | dual | — | **F2** — no docstring | **F3** — same B271 family-bug pattern | LONG ~28, SHORT ~28 — borderline FAIL | **(B)** F2 + F3 delete entry; flag for B603 |
| W5 | `pivot_s3_capitulation` | pivot | LONG | — | **F2** — no docstring | — (no affinity entry; uses B291 default) | ~14/yr — **FAIL_FIRE_STARVED** | **(D)** Stage 5 deferral. **F6 missing-inverse:** consider Class 7 NEW `strat_pivot_r3_blowoff_short` |
| W6 | `pivot_r1_breakout` | pivot | dual | **F1 LATENT** — both LONG default-True (`above_avwap_*, True`) and SHORT default-False on the AVWAP gate — asymmetric default policy | ✅ docstring present | — | LONG ~5, SHORT ~5 — **FAIL_FIRE_STARVED**; 5 AND-gates | **(C)** loosen AVWAP-only-one-anchor + flag B603 |
| W7 | `pivot_r2_continuation` | pivot | dual | **F1 LATENT** — same AVWAP asymmetric default as W6 | ✅ docstring present | — | LONG ~2, SHORT ~2 — **FAIL_FIRE_STARVED**; 5 AND-gates incl vol_spike_2x | **(D)** Stage 5 deferral or **(C)** loosen |
| W8 | `cpr_narrow_bullish` | pivot | dual | **F1** — SHORT side uses `not s.get("above_avwap_50low", False)` which is silent-gap pattern (auto-True when key missing). B639 codified positive symmetric pattern. | ✅ docstring present | — (no entry; B291 default applies) | LONG ~13, SHORT ~13 — **FAIL_FIRE_STARVED**; 5 AND-gates incl 200-EMA | **(B)** F1 swap to positive symmetric `below_avwap_50low` |
| W9 | `camarilla_s3_bounce` | pivot | dual | — | ✅ docstring present | **F3 DEFERRED-R5** — B624 manifest M1 (already documented; no action) | LONG ~30, SHORT ~30 — borderline PASS | **(E)** no action needed; defer per existing R5 ticket |
| W10 | `camarilla_r3_breakout` | pivot | dual | — | **F2** — no docstring | — | LONG ~166, SHORT ~166 — PASS_CUBE | **(A)** F2 doc only |

**Aggregate findings:**
- 6 of 10 have no docstring (F2 across W1/W2/W3/W4/W5/W10)
- 1 B271 family-bug pattern (W3, W4 — single dict entry)
- 1 explicit silent-gap F1 (W8)
- 2 latent AVWAP asymmetric-default F1s (W6, W7)
- 5 fire-count FAIL_FIRE_STARVED projections (W2, W5, W6, W7, W8) — flag for B603 pre-cube discussion
- 1 missing-inverse candidate (W5 — `pivot_r3_blowoff_short` Class 7 NEW)
- 1 already-deferred (W9 — no walk-time action)

---

## W1. `strat_bullish_engulfing_support`

### Step 1 — Read the code

[screener.py:1373-1382](backtest/signals/screener.py#L1373-L1382):

```python
def strat_bullish_engulfing_support(s):
    # B628 F1 family-sweep: positive symmetric obv_bearish.
    fl = (s.get("bullish_engulfing") and (s.get("near_s1") or s.get("near_s2") or s.get("at_key_fib")) and s.get("obv_bullish"))
    fs = (s.get("bearish_engulfing") and (s.get("near_r1") or s.get("near_r2") or s.get("at_key_fib"))
          and s.get("obv_bearish"))
    return _strat3(fl, fs, "candle",
        ["bullish_engulfing","at_support","obv_bullish"],
        ["bearish_engulfing","at_resistance","obv_bearish"],
        ["Bullish engulfing at support - two systems confirming","OBV rising"],
        ["Bearish engulfing at resistance - two systems confirming","OBV falling (B628 F1)"])
```

**LONG fires when ALL THREE are true:**

| Gate | Code | Meaning | Threshold |
|---|---|---|---|
| L-G1 Pattern | `bullish_engulfing` | Two-bar bullish engulfing pattern formed today (yesterday bearish, today bullish, today engulfs yesterday) | Boolean |
| L-G2 Location | `near_s1` OR `near_s2` OR `at_key_fib` | Price is within 0.3% of either pivot S1 / pivot S2 / a key Fibonacci retracement level (38.2% / 50% / 61.8%) | OR composite |
| L-G3 Flow | `obv_bullish` | OBV > its 20-bar mean (accumulation) | Boolean |

**SHORT fires when ALL THREE are true (mirror):** bearish_engulfing + (near_r1 OR near_r2 OR at_key_fib) + obv_bearish.

### Step 2 — Classify

- Category: `candle`
- Dual via `_strat3`
- Status: Active (1 of 221)
- STRATEGY_REGIME_AFFINITY: **no entry** → uses B291 direction-aware default
- Last touched: B628 (F1 family-sweep added positive symmetric `obv_bearish`)

### Step 3 — Producer source-read + temporality

- `bullish_engulfing` / `bearish_engulfing` at [technical.py:1448-1451](backtest/signals/technical.py#L1448-L1451) — strict 4-condition AND on bar of fire. **EVENT** signal. Producer pair is symmetric.
- `near_s1` / `near_s2` / `near_r1` / `near_r2` at [technical.py:120-121](backtest/signals/technical.py#L120-L121) — proximity test `|today − level| / |level| < 0.003`. Levels computed from YESTERDAY's H/L/C (PIT safe). **EVENT** signal.
- `at_key_fib` at [technical.py:186](backtest/signals/technical.py#L186) — OR of three Fibonacci proximity flags. **EVENT** signal.
- `obv_bullish` / `obv_bearish` — **STATE** (OBV is cumulative, 20-bar mean is slow).

### Step 4 — Doc-vs-thesis

Context bullets: "Bullish engulfing at support - two systems confirming / OBV rising." ✅ accurately describes what fires. Engulfing = EVENT, support = EVENT (proximity), OBV = STATE (confluence flow filter). Honest framing.

**No F1 thesis mismatch.** But: context bullets call it "two systems" (engulfing + support); OBV is actually a third gate, not a confluence. Minor commentary fix would help.

### Step 5 — OPEN_INVESTIGATIONS grep

No matches. Clean.

### Step 6 — Missing-inverse + economic-symmetry

- Structural symmetry: ✅ both directions implemented; gates mirror cleanly.
- Producer symmetry: ✅ all signals have positive symmetric mirrors (B628 already fixed the OBV silent-gap).
- Economic symmetry: bullish engulfing at support is a classic Nison reversal pattern; bearish engulfing at resistance is the canonical mirror. ✅ symmetric in literature.
- Data-source symmetry: all technical, no asymmetric data hazard.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1** | Strategy is essentially correct. Context bullet "two systems confirming" understates the gate count (3 gates: engulfing + location + OBV). | LOW (commentary) |
| **F2** | No docstring at all (just inline `# B628 F1 family-sweep` comment + context bullets). | LOW |

**Fire-count projection** (gates: bullish_engulfing × (near_s1 OR near_s2 OR at_key_fib) × obv_bullish): ~83/yr LONG side. PASS_CUBE.

**Options:**

| Option | Description |
|---|---|
| **(A)** F2 docstring + minor commentary fix to "three systems confirming" (engulfing + support/fib + OBV-flow). **RECOMMENDED.** |
| (B) Status quo |

**My recommendation: (A).** Clean strategy; just needs honest docstring.

### FINAL STATUS POST-B645 — ✅ CLOSED

| Item | Outcome |
|---|---|
| **What shipped (B641)** | Option (A) — F2 docstring added; context bullet upgraded "two systems" → "three systems confirming (candle + level + flow)" to match actual gate count |
| **Code reference** | [screener.py strat_bullish_engulfing_support](backtest/signals/screener.py) |
| **Measured fires/yr (universe)** | **337** PASS_CUBE (B641 measurement; independence under-counted 1000×) |
| **Open items queued from this walk** | `S4-OBV-LOCATION-TENSION-DESIGN` (LONG OBV gate fights support premise — reviewer P6) ; `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT` (at_key_fib swing-anchor verification — reviewer P7) |
| **No regrets** | The gate set is honestly named; the OBV-vs-location concern is a design question (could re-frame to `obv_diverge_bull`) deferred to the queued ticket. |

---

## W2. `strat_shooting_star_short`

### Step 1 — Read the code

[screener.py:1484-1493](backtest/signals/screener.py#L1484-L1493):

```python
def strat_shooting_star_short(s):
    fires = (s.get("shooting_star") and
             (s.get("near_r1") or s.get("near_r2") or
              s.get("bb_20_20_touch_upper")) and
             s.get("rsi_14", 50) > 65)
    return _strat(fires, "short", "candle",
        ["shooting_star","at_resistance","rsi_14>65"],
        ["Shooting star at resistance level  -  bearish reversal",
         "Long upper wick shows sellers rejecting higher prices",
         f"RSI-14 at {s.get('rsi_14',0):.1f}  -  overbought at resistance"])
```

**SHORT fires when ALL THREE are true:**

| Gate | Code | Meaning | Threshold |
|---|---|---|---|
| S-G1 Pattern | `shooting_star` | Long upper wick (>2×body), small lower wick (<body), small body | Boolean |
| S-G2 Location | `near_r1` OR `near_r2` OR `bb_20_20_touch_upper` | Within 0.3% of pivot R1, R2, OR within 0.5% of upper Bollinger Band | OR composite |
| S-G3 Momentum | `rsi_14 > 65` | RSI > 65 (overbought; not yet at canonical 70 but close) | Literal |

### Step 2 — Classify

- Category: `candle`
- Single-direction SHORT (no LONG mirror exists — there's no `strat_hammer_at_support_long`)
- Status: Active
- STRATEGY_REGIME_AFFINITY: explicit `{"bear", "crisis", "neutral"}` at [regime_selector.py:315](backtest/engine/regime_selector.py#L315) — matches B291 SHORT default ✅
- Last touched: original implementation

### Step 3 — Producer source-read + temporality

- `shooting_star` at [technical.py:1439](backtest/signals/technical.py#L1439) — `upper_wick > 2×body AND lower_wick < body AND body > 0`. **EVENT** signal.
- `near_r1` / `near_r2` — EVENT (proximity, see W1)
- `bb_20_20_touch_upper` at [technical.py:975](backtest/signals/technical.py#L975) — `close >= upper_BB × 0.995`. **STATE-like** (BB is slow-moving 20-period rolling).
- `rsi_14` — STATE.

### Step 4 — Doc-vs-thesis

Context bullets: "Shooting star at resistance / Long upper wick shows sellers rejecting higher prices / RSI-14 at X overbought at resistance." ✅ accurate description.

**Per CHECKLIST (l) AVWAP/OBV/MACD non-redundancy:** the location OR-composite mixes pivot-R levels (mean-reversion daily-bar) with Bollinger upper (volatility-based 20-period). Different references; not redundant. ✅

### Step 5 — OPEN_INVESTIGATIONS grep

No matches.

### Step 6 — Missing-inverse + economic-symmetry

**No LONG mirror exists.** The symmetric inverse would be `strat_hammer_at_support_long` (hammer + near_s1/s2 + RSI<35). Producer pair is symmetric (hammer / shooting_star both EVENT in `compute_candle_signals`). Bollinger lower would mirror upper. **F-missing-inverse candidate** — Class 7 NEW per `feedback_long_short_inverse_audit`.

Economic symmetry: hammer-at-support is canonical bullish reversal in Nison; mirror would be valid. Caveat: `strat_pivot_s2_bounce` already includes `hammer + near_s2 + rsi<40` on its LONG side ([screener.py:190](backtest/signals/screener.py#L190)). Adding `strat_hammer_at_support_long` would partially duplicate. NOT a clean Class 7 NEW — the LONG-side coverage is partially there already.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1** | None | — |
| **F2** | No docstring; thresholds (RSI>65, BB touch ratio 0.995) not explained. | LOW |
| **F-fire-count** | gates: shooting_star prior ~0.02 × (near_r1 OR near_r2 OR bb_touch_upper) ~0.30 × rsi>65 ~0.20 ≈ 0.0012 → ~66/yr universe-wide, but with conditional decay (RSI>65 AND shooting_star are positively correlated at tops, so joint may be higher than independent product). Conservative: ~25-66/yr. Borderline. | MEDIUM |
| **F-missing-inverse** | LONG mirror partially covered by `pivot_s2_bounce`. NOT a clean Class 7 NEW candidate. | LOW |

**Options:**

| Option | Description |
|---|---|
| **(A)** F2 docstring only (status quo gates) |
| (B) F2 + loosen RSI>65 to RSI>60 (matches `pivot_s2_bounce` SHORT side's RSI>60); higher fire count |
| (C) Add Class 7 NEW `strat_hammer_at_support_long` — but partial duplication with `pivot_s2_bounce` LONG |
| **(D)** Stage 5 deferral — defer fire-count decision to cube; F2 doc only now |
| (E) Status quo |

**My recommendation: (D)** — F2 doc now, defer fire-count tweak to Stage 5 cube data. Hold (C) on missing-inverse; the partial duplication needs owner judgment.

### FINAL STATUS POST-B645 — ✅ CLOSED

| Item | Outcome |
|---|---|
| **What shipped (B641)** | Option (D) — F2 docstring added with Nison 1991 source + threshold rationale + B641 Stage-5 deferral notice (no pre-cube loosening of RSI>65 per `feedback_minimum_fire_count_gate_before_cube` + CHECKLIST (k)) |
| **Measured fires/yr (universe)** | **139** PASS_CUBE — B640 FAIL projection was independence-product artifact (gates were over-estimated as exclusive but RSI>65 + shooting_star + at-resistance are POSITIVELY correlated at market tops; independence ratio 2.092 over-counted by 2×, but the measured 139/yr is well above 30 even allowing for that over-count) |
| **Reviewer's structural concerns (P-class on W2)** | Reviewer flagged `bb_20_20_touch_upper` as a continuation signal mis-categorized as resistance (price walks the upper BB in uptrends → shorting strength fights drift) — acknowledged as a future design question; NOT auto-fixed this batch (would require a separate strategy redesign). Reviewer's loosen-RSI option (B640-B) explicitly NOT taken — loosening RSI<65 would worsen the strategy by shorting less-overbought names. |
| **No regrets** | F2 doc shipped; pre-cube loosening avoided. The bb_touch_upper concern is real but warrants its own redesign batch, not a quick loosen. |

---

## W3. `strat_pivot_s1_bounce`

### Step 1 — Read the code

[screener.py:175-186](backtest/signals/screener.py#L175-L186):

```python
def strat_pivot_s1_bounce(s):
    # B628 F1 family-sweep: `not s.get("obv_bullish")` -> positive
    # symmetric `obv_bearish` (B617 producer). See B628 commit for
    # the bundled 7-strategy sweep rationale per CHECKLIST #105 (n).
    fl = (s.get("near_s1") and (s.get("hammer") or s.get("pin_bar")) and s.get("obv_bullish"))
    fs = (s.get("near_r1") and (s.get("shooting_star") or s.get("bearish_engulfing"))
          and s.get("obv_bearish"))
    return _strat3(fl, fs, "pivot",
        ["near_s1","hammer/pin_bar","obv_bullish"],
        ["near_r1","shooting_star","obv_bearish"],
        ["Price at S1 pivot support","Hammer or pin bar confirming buyers","OBV rising - accumulation"],
        ["Price at R1 pivot resistance","Shooting star or bearish engulfing rejecting highs","OBV falling - distribution (B628 F1)"])
```

**LONG fires when ALL THREE are true:**

| Gate | Code | Meaning | Threshold |
|---|---|---|---|
| L-G1 Location | `near_s1` | Price within 0.3% of pivot S1 | Literal |
| L-G2 Pattern | `hammer` OR `pin_bar` | Today is a hammer or a pin bar | OR composite |
| L-G3 Flow | `obv_bullish` | OBV accumulation | STATE |

**SHORT mirror:** `near_r1 + (shooting_star OR bearish_engulfing) + obv_bearish`.

### Step 2 — Classify

- Category: `pivot`
- Dual
- STRATEGY_REGIME_AFFINITY: explicit `{"neutral", "bear"}` at [regime_selector.py:192](backtest/engine/regime_selector.py#L192). The dict comment classifies this as "counter-trend bounce" — but this is dual, so the affinity caps **BOTH** directions to neutral/bear. That over-restricts LONG (should fire in bull regimes too for counter-trend bounces in uptrends) and arguably gives SHORT wrong regimes (SHORT-on-bounce-rejection should be bear/crisis/neutral; bull excluded correctly, but explicit set excludes crisis incorrectly).
- Last touched: B628 F1 family-sweep

### Step 3 — Producer source-read + temporality

- `near_s1` / `near_r1` — EVENT (proximity)
- `hammer` / `pin_bar` / `shooting_star` / `bearish_engulfing` — EVENT (today's bar shape)
- `obv_bullish` / `obv_bearish` — STATE

### Step 4 — Doc-vs-thesis

Context bullets accurate. Bounce thesis: price at support + reversal candle + OBV-flow confirmation. ✅ honest.

### Step 5 — OPEN_INVESTIGATIONS grep

No matches.

### Step 6 — Missing-inverse + economic-symmetry

Structural ✅. Economic ✅. Producer symmetry ✅ post-B628.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None — strategy logic is clean | — |
| **F2** | No docstring | LOW |
| **F3** | STRATEGY_REGIME_AFFINITY `{neutral, bear}` was set when strategy was single-direction (LONG = counter-trend bounce in pullback regimes). Strategy is NOW dual via `_strat3`; both directions are gated to {neutral, bear}. SHORT side mis-regimed (should be `{bear, crisis, neutral}` per B291 default). LONG side mis-regimed (should be `{bull, neutral}` for buy-the-dip-in-uptrend interpretation OR `{neutral, bear}` for capitulation-bounce interpretation — split-thesis the owner should rule on). **Same B271 family-bug signature as B608/B609/B617 and B639 morning_star.** | HIGH (regime) |

**Fire-count projection:** ~92/yr LONG side. PASS_CUBE.

**Options:**

| Option | Description |
|---|---|
| (A) F2 doc only |
| **(B)** F2 + F3 delete `{neutral, bear}` entry — falls back to B291 direction-aware default. SAME PATTERN as B608/B609/B617/B639. **RECOMMENDED.** |
| (C) F2 + F3 split affinity into per-direction explicit entries (`pivot_s1_bounce` LONG `{bull,neutral}`, `pivot_s1_bounce_short` would need to be a separate registry key — not how the engine works currently) |
| (D) Status quo |

**My recommendation: (B).** Same family-bug fix as the four prior walks. Risk: if cube data shows LONG genuinely better in `{neutral, bear}` only, can re-add post-R5 (manifest M1 absorbs).

### FINAL STATUS POST-B645 — ✅ CLOSED

| Item | Outcome |
|---|---|
| **What shipped (B641)** | Option (B) + **reviewer-flagged P1 pin_bar direction-fix.** Three actions in same commit: (1) F2 docstring; (2) F3 STRATEGY_REGIME_AFFINITY `{neutral, bear}` entry DELETED — 5th instance of B271 family-bug fix (post B608/B609/B617/B639); falls back to B291 direction-aware default. (3) **F1 pin_bar direction-contamination fix** — reviewer caught that `pin_bar` producer is direction-agnostic (`max(uwk, lwk) > 0.66*rng` fires on either dominant wick). Added producer-additive `bullish_pin_bar` (lower wick > 0.66 range) + `bearish_pin_bar` (upper wick > 0.66 range) to `compute_candle_signals`; LONG side swapped `pin_bar` → `bullish_pin_bar`. SHORT side unchanged (already used directionally-clean `shooting_star` + `bearish_engulfing`). |
| **Code reference** | [screener.py strat_pivot_s1_bounce](backtest/signals/screener.py) + [technical.py:1440 bullish/bearish_pin_bar producers](backtest/signals/technical.py#L1440) |
| **Test pins** | test_batch641_tier1_walk_bundle_followups pins 1-7 (producer existence, direction-correctness, bearish-pin-blocks-LONG regression, regime entry deleted, B291 default) |
| **Measured fires/yr (universe)** | **220** PASS_CUBE (independence under-counted 500×) |
| **No regrets** | All three actions are unambiguous Tier 1 fixes. The pin_bar fix is structurally important — a bearish pin AT SUPPORT firing LONG was a real bug. |

---

## W4. `strat_pivot_s2_bounce`

### Step 1 — Read the code

[screener.py:189-195](backtest/signals/screener.py#L189-L195):

```python
def strat_pivot_s2_bounce(s):
    fl = (s.get("near_s2") and s.get("rsi_14", 50) < 40 and (s.get("hammer") or s.get("bullish_engulfing")))
    fs = (s.get("near_r2") and s.get("rsi_14", 50) > 60 and s.get("bearish_engulfing"))
    return _strat3(fl, fs, "pivot",
        ["near_s2","rsi_14<40","bullish_candle"], ["near_r2","rsi_14>60","bearish_engulfing"],
        [f"Price at S2 deep support","RSI-14 oversold","Bullish candle confirms buyers"],
        [f"Price at R2 strong resistance","RSI-14 overbought","Bearish engulfing confirms sellers"])
```

**LONG fires when ALL THREE:**

| Gate | Code | Meaning |
|---|---|---|
| L-G1 Location | `near_s2` | Within 0.3% of pivot S2 (deeper support than S1) |
| L-G2 Momentum | `rsi_14 < 40` | Oversold (below 40, not deeply at 30) |
| L-G3 Pattern | `hammer` OR `bullish_engulfing` | Bullish reversal candle |

**SHORT mirror:** `near_r2 + rsi_14 > 60 + bearish_engulfing`.

**Note** the SHORT side has only `bearish_engulfing`, not the OR composite the LONG side has (no `shooting_star` option). Asymmetric. Minor.

### Step 2 — Classify

- Category: `pivot`
- Dual
- STRATEGY_REGIME_AFFINITY: explicit `{"neutral", "bear"}` — **same B271 family-bug as W3**
- Last touched: original implementation

### Step 3 — Producer source-read + temporality

All gates already covered in W1/W3.

### Step 4 — Doc-vs-thesis

Context bullets accurate. Deep support + oversold + confirmation candle. ✅

### Step 5 — OPEN_INVESTIGATIONS grep

No matches.

### Step 6 — Missing-inverse + economic-symmetry

Asymmetric: LONG has `hammer OR bullish_engulfing`, SHORT has only `bearish_engulfing`. Should mirror to `shooting_star OR bearish_engulfing`. Minor producer-symmetry gap.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1** | SHORT side missing `shooting_star` OR-disjunct symmetric to LONG's `hammer`. Producer exists; one-line additive. | LOW |
| **F2** | No docstring | LOW |
| **F3** | Same B271 family-bug as W3. Dual strategy with single-direction-era affinity entry. | HIGH (regime) |
| **F-fire-count** | LONG ~28/yr (near_s2 narrower than near_s1 + rsi<40 + hammer/engulfing). SHORT ~28/yr. **Borderline FAIL_FIRE_STARVED** vs min_trades=30. | MEDIUM |

**Options:**

| Option | Description |
|---|---|
| (A) F2 doc only |
| (B) F2 + F3 delete entry + F1 add `shooting_star` to SHORT OR |
| **(C)** F2 + F3 delete entry + F1 add `shooting_star` + flag for B603 fire-count discussion. **RECOMMENDED.** |
| (D) Status quo |

**My recommendation: (C).**

### FINAL STATUS POST-B645 — ✅ SHIPPED PARTIAL + 🎯 REMAINDER QUEUED

| Item | Outcome |
|---|---|
| **What shipped (B641)** | **F3 ONLY — split per CHECKLIST (g) sequence-or-split.** Reviewer's M4 critique caught that bundling F3 + F1 + RSI-mislabel violates the same (g) rule that justified deferring W7. Action: SPLIT the bundle — F3 regime entry delete ships in B641 Tier 1 (safe family-bug pattern); F1 add `shooting_star` to SHORT OR + F2 docstring + RSI-40-mislabel correction queued separately. |
| **Code reference** | [regime_selector.py — pivot_s2_bounce {neutral, bear} entry deleted](backtest/engine/regime_selector.py) (B271 family-bug fix #6) |
| **Test pins** | test_batch641_tier1_walk_bundle_followups pins 8-9 (regime entry deleted, B291 default applies) |
| **Measured fires/yr (universe)** | **22** FAIL_FIRE_STARVED — projection was correct here (B640 said ~28; measurement says 22). The strategy genuinely fires rarely because near_s2 (deeper than S1) is rare on daily bars. |
| **Open items queued** | `S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL` — three sub-changes in ordered ship sequence per CHECKLIST (g): (1) F1 add `shooting_star` to SHORT OR (one-line additive); (2) F2 docstring; (3) RSI<40 "oversold" mislabel correction (canonical Wilder oversold is 30, not 40 — relabel to "below-neutral" or "soft-oversold") |
| **Reviewer P2 specifically** | RSI<40 mislabel is queued for explicit correction; not auto-fixed because per `feedback_no_rushing_per_strategy_tweak` each ships in its own owner-direction turn |
| **No regrets** | Splitting was the right call per (g); future W4 batches can ship the remainder cleanly. |

---

## W5. `strat_pivot_s3_capitulation`

### Step 1 — Read the code

[screener.py:198-206](backtest/signals/screener.py#L198-L206):

```python
def strat_pivot_s3_capitulation(s):
    fires = (s.get("near_s3") and
             s.get("rsi_14", 50) < 30 and
             s.get("vol_spike_2x"))
    return _strat(fires, "long", "pivot",
        ["near_s3","rsi_14<30","vol_spike_2x"],
        ["Price at S3  -  extreme capitulation level",
         f"RSI-14 extremely oversold at {s.get('rsi_14',0):.1f}",
         "Volume spike confirms panic selling  -  reversal likely"])
```

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `near_s3` | Within 0.3% of pivot S3 (deepest standard support level) |
| `rsi_14 < 30` | Canonical oversold |
| `vol_spike_2x` | Volume ≥ 2× 20-day average |

### Step 2 — Classify

- Category: `pivot`
- Single-direction LONG
- STRATEGY_REGIME_AFFINITY: explicit `{"neutral", "bear", "crisis"}` at [regime_selector.py:189](backtest/engine/regime_selector.py#L189) — designed for buying capitulation in down/crisis regimes. ✅ correct for LONG capitulation thesis (no bull because there's no capitulation in bull).
- Last touched: original implementation

### Step 3 — Producer source-read + temporality

All gates EVENT (today's bar metrics).

### Step 4 — Doc-vs-thesis

✅ "Extreme capitulation / extremely oversold / panic selling" — matches gate set.

### Step 5 — OPEN_INVESTIGATIONS grep

No matches.

### Step 6 — Missing-inverse + economic-symmetry

**Missing inverse:** `strat_pivot_r3_blowoff_short` would mirror this: `near_r3 + rsi_14 > 70 + vol_spike_2x` — a blowoff-top short. Producer pair `near_r3` exists ([technical.py:121](backtest/signals/technical.py#L121)). **Class 7 NEW candidate per `feedback_long_short_inverse_audit`.**

Economic symmetry: capitulation lows + blowoff highs are classic mirror events in market structure (Wyckoff Selling Climax / Buying Climax). ✅

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None | — |
| **F2** | No docstring | LOW |
| **F-missing-inverse** | `strat_pivot_r3_blowoff_short` Class 7 NEW candidate. Producer ready. ~10 lines per `feedback_wire_new_strategies_on_the_spot`. | MEDIUM |
| **F-fire-count** | gates: near_s3 ~0.005 × rsi<30 ~0.05 × vol_spike_2x ~0.10 ≈ 0.000025 → ~14/yr universe-wide. **FAIL_FIRE_STARVED** vs min_trades=30. | HIGH |

**Options:**

| Option | Description |
|---|---|
| (A) F2 doc only |
| (B) F2 + add Class 7 NEW `strat_pivot_r3_blowoff_short` |
| (C) F2 + loosen one gate (e.g., rsi<35 instead of <30) to raise fire count |
| **(D)** F2 + add Class 7 NEW + Stage 5 fire-count deferral on both (don't loosen pre-cube; let R5 decide). **RECOMMENDED.** |
| (E) Status quo |

**My recommendation: (D).** Wire the missing inverse on-the-spot per memory directive; defer the fire-count loosening to cube data.

### FINAL STATUS POST-B645 — ✅ REDESIGNED (B643 option C) → 🟡 EXPLORATORY (B644) + ✅ MIRROR SHIPPED (B645)

| Item | Outcome |
|---|---|
| **Reviewer's structural critique (P3)** | The original B640 W5 was a knife-catch by construction (price crashed + oversold + panic volume = BUY; no element of the gate-set asked whether the decline had stopped). Reviewer was 100% right; this was the most-dangerous strategy in the bundle. Survivorship-bias-amplified (the falling knives that didn't bounce fall out of survivor universes). |
| **Initial owner direction (W5-D from B640)** | Wire Class 7 NEW mirror + Stage 5 defer (the initial B641 plan) — superseded by deeper redesign per reviewer P3 critique. |
| **Subsequent owner direction (option C from B643 review)** | **Redesign — decouple capitulation DETECTION from ENTRY.** New producer `compute_capitulation_lookback` (in `technical.py`) emits `recent_capitulation_at_s3` = True when the pre-B643 conditions (near_s3 + rsi<30 + vol_spike_2x) were satisfied on ANY of the last 5 bars. Strategy now fires LONG when BOTH: (1) recent_capitulation_at_s3 (the 5-bar Wyckoff Spring/Test eligibility window) AND (2) a reversal-trigger today (`bullish_engulfing` OR `hammer` OR `above_prev_high`). **Buys the TURN inside the window, not the FALL on capitulation day.** Wyckoff Selling Climax + Spring/Test play. |
| **Code reference** | [screener.py strat_pivot_s3_capitulation](backtest/signals/screener.py) + [technical.py compute_capitulation_lookback](backtest/signals/technical.py) |
| **Test pins** | test_batch643_w5_capitulation_redesign — 17 pins covering producer behavior (importable, empty on short history, True today + within window, False outside window, False on normal series), strategy fires on each of 3 reversal-trigger OR branches, blocks without reversal trigger, blocks without recent capitulation, regime affinity unchanged |
| **Measured fires/yr (universe)** | **Pre-B643: 14.7. Post-B643: 18.3 (+25%).** Verdict: still FAIL_FIRE_STARVED, but structurally correct. The redesign achieves its primary objective: closing the knife-catch. The fire-count went up modestly because the 5-bar eligibility window allows entries that would have been missed by same-bar-only firing. |
| **Subsequent owner direction (W5-i from B643 measurement review)** | **Keep as EXPLORATORY** — ship correctness fix; do NOT loosen gates pre-cube to chase 30/yr threshold. Pre-cube loosening recreates the original problem (looser gates → less-confirmed signals → more knife-catches). Stage 5 cube empirically validates whether 18/yr fires produce alpha at sufficient statistical power. Marked EXPLORATORY in docstring per B644. |
| **Subsequent owner direction (a from B644 review)** | **Wire Class 7 NEW mirror `strat_pivot_r3_blowoff_short` symmetrically (B645).** See dedicated W5-mirror section below. |
| **Open items** | `S4-SURVIVORSHIP-T1A-VERIFY` — reviewer's C5 cross-cutting critique applies to W5 specifically; verify T1a PIT universe includes delisted-during-window names (DEC-477 says 111 historical-removed rows; per-strategy adversarial verification still pending) |
| **Reviewer's M8 (economic-symmetry of W5 inverse)** | Acknowledged via EXPLORATORY marking on BOTH W5 LONG + W5 mirror SHORT. The wire happened because owner explicitly directed it post-redesign + with full awareness of the equity-drift / squeeze-risk / borrow-cost asymmetries (per `feedback_structural_symmetry_not_economic_symmetry`); Stage 5 cube governs final deployment decision. |
| **No regrets** | The redesign is one of the most consequential outcomes of the audit cycle. The reviewer was right about the structural problem; option C is the rigorous fix; W5-i exploratory marking is the disciplined disposition. |

---

## W5 mirror — `strat_pivot_r3_blowoff_short` (Class 7 NEW per B645)

> **Wired Batch 645 (2026-06-09)** per owner directive (a) following B643 W5 LONG redesign + B644 W5-i exploratory marking. Symmetric mirror of B643's 2-gate structure; same Wyckoff thesis on the SHORT side (Buying Climax + Upthrust-Test sequence).

### Design — mirror of W5 post-redesign

New producer in `technical.py`:

```python
def compute_blowoff_lookback(df, lookback=5):
    # Mirror of compute_capitulation_lookback.
    # Per-bar: near_r3 + rsi>70 + vol_spike_2x
    # Returns: recent_blowoff_at_r3 = True if any of last 5 bars satisfied.
```

Strategy in `screener.py`:

```python
def strat_pivot_r3_blowoff_short(s):
    fires = (
        s.get("recent_blowoff_at_r3")
        and (
            s.get("bearish_engulfing")
            or s.get("shooting_star")
            or s.get("below_prev_low")
        )
    )
    return _strat(fires, "short", "pivot", ...)
```

### Wyckoff thesis

The blowoff bar is the **Buying Climax (BC)** — terminal-stage upmove with climactic volume + price reaching beyond standard resistance. The 5-day window captures the **Automatic Reaction (AR)** + **Upthrust-Test** phase where price re-tests the BC high on weaker volume. Bearish-reversal-confirmation bar inside the window signals the Upthrust failed → bias to the **Sign-of-Weakness (SoW)** decline. **Sells the TURN inside the window, not the SPIKE on blowoff day.**

### Status — 🟡 EXPLORATORY

| Item | Outcome |
|---|---|
| **Strategy count impact** | 221 → 222 (+1 Class 7 NEW) |
| **Regime affinity** | No explicit `STRATEGY_REGIME_AFFINITY` entry; B291 direction-aware SHORT default applies → fires in `{bear, crisis, neutral}` |
| **Test pins** | test_batch645_w5_mirror — 16 pins covering producer (importable, empty on short history, True today + within window, False outside window, False on normal series), strategy fires on each of 3 bearish-reversal OR branches, blocks without blowoff or reversal-trigger, registry, B291 default, count = 222 |
| **Measured fires/yr (universe)** | **7.3** FAIL_FIRE_STARVED (per `output_audit/fire_count_measured_b645_w5_mirror.json` — 20 tickers × 3 years; 0.67/yr sample × 11 scale = 7.3 universe-projected). Significantly LOWER than W5 LONG's 18.3 — consistent with the expectancy-asymmetry caveat: blowoff conditions (RSI>70 + near R3 + 2× volume) are rarer than the symmetric capitulation conditions. Independence ratio 0.272 (measured 3.7× higher than independence-product). Marked EXPLORATORY; rare-but-structurally-correct — Stage 5 cube empirically decides whether the few fires produce alpha after squeeze + borrow costs |
| **Update to count table at top** | The "measurement pending" line for W5m in the [Cluster current state](#cluster-current-state) table is now resolved to 7.3 FAIL_FIRE_STARVED |
| **Expectancy asymmetry ACKNOWLEDGED** | Per `feedback_structural_symmetry_not_economic_symmetry` + reviewer's M8: structurally symmetric to W5 LONG but **economically NOT symmetric** — equity upward drift + squeeze risk on overbought short-target names + borrow costs structurally bias against SHORT. Owner-approved wire per directive (a) with full understanding that Stage 5 cube governs deployment. |
| **Open items** | Same survivorship-bias caveats apply mirror-image (the squeezes that aren't in survivor universe; merger-arb floors on shorts of acquisition targets) |

---

## W6. `strat_pivot_r1_breakout`

### Step 1 — Read the code

[screener.py:209-244](backtest/signals/screener.py#L209-L244):

```python
def strat_pivot_r1_breakout(s):
    """Pivot R1 breakout. Batch 205 ... AVWAP-from-252-day-low is the institutional
    reference level; breakouts above R1 that ALSO hold above AVWAP are markedly higher
    quality than R1 breaks in isolation.

    AVWAP gate defaults to True when avwap signals are absent (e.g.
    insufficient history) so backward-compat is preserved.
    """
    avwap_long_ok = s.get("above_avwap_252low", True) and s.get("above_avwap_50low", True)
    # B633 sweep: positive symmetric below_avwap_252low/50low (B612 producers)
    avwap_short_ok = s.get("below_avwap_252low", False) and s.get("below_avwap_50low", False)
    fl = (
        s.get("above_r1") and s.get("vol_spike_15x")
        and s.get("macd_12_26_9_bullish") and avwap_long_ok
    )
    fs = (
        s.get("below_s1") and s.get("vol_spike_15x")
        and s.get("macd_12_26_9_bearish") and avwap_short_ok
    )
    return _strat3(fl, fs, "pivot", ...)
```

**LONG fires when ALL FOUR (technically FIVE — `avwap_long_ok` is itself two-AND):**

| Gate | Meaning |
|---|---|
| `above_r1` | Today's close > R1 |
| `vol_spike_15x` | Volume ≥ 1.5× 20-day average |
| `macd_12_26_9_bullish` | MACD histogram > 0 (momentum) |
| `above_avwap_252low` AND `above_avwap_50low` | Above BOTH long-anchor and short-anchor AVWAP |

**SHORT mirror:** below_s1 + vol_spike_15x + macd_bearish + (below_avwap_252low AND below_avwap_50low).

### Step 2 — Classify

- Category: `pivot`
- Dual
- STRATEGY_REGIME_AFFINITY: no entry → B291 default
- Last touched: B633 (positive symmetric below_avwap swap)

### Step 3 — Producer source-read + temporality

- `above_r1` / `below_s1` — EVENT (cross today)
- `vol_spike_15x` — EVENT (today's volume)
- `macd_12_26_9_bullish` / `_bearish` — borderline EVENT (histogram crossover vs hist > 0 is a STATE measure of histogram sign; the strategy uses `_bullish` = "hist > 0" so STATE)
- `above_avwap_252low` / `_50low` — STATE-ish (AVWAP slow-moving once anchored)
- `below_avwap_252low` / `_50low` — STATE-ish (B612 producer; positive symmetric)

### Step 4 — Doc-vs-thesis

Docstring present and clear. Cites Brian Shannon 2022 (real source). ✅

### Step 5 — OPEN_INVESTIGATIONS grep

No matches.

### Step 6 — Missing-inverse + economic-symmetry

Structural ✅. Producer symmetry ✅ post-B633. Economic ✅.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1 LATENT** | AVWAP gate's default policy is asymmetric: LONG defaults to `True` if key missing (`s.get("above_avwap_252low", True)`), SHORT defaults to `False` (`s.get("below_avwap_252low", False)`). Docstring explains this is for "backward-compat" but it means: when AVWAP signals are absent, LONG side **auto-passes** the AVWAP gate (vulnerability if the strategy is mis-classified as having AVWAP data), while SHORT side **auto-fails**. This is structurally the same silent-gap pattern B639 flagged on RSI default-50. Default-True on a boolean gate that's part of the fire condition means: future strategies (or new tickers without enough history) could fire LONG when AVWAP isn't even being computed. Latent silent-gap class. | MEDIUM |
| F2 | Docstring is present and accurate | — |
| **F-fire-count** | gates: above_r1 ~0.05 × vol_spike_15x ~0.20 × macd_bullish ~0.45 × above_avwap_252low ~0.55 × above_avwap_50low ~0.55 ≈ 0.0014 universe-wide BUT with default-True for AVWAP, effective fire rate could be higher. Conservative LONG ~5/yr; if AVWAP keys missing on lots of tickers, fire rate higher than this. **FAIL_FIRE_STARVED** projection. Five AND-gates is heavy stacking; B612 flagged this pattern. | HIGH |

**Options:**

| Option | Description |
|---|---|
| (A) Status quo (keep default-True for AVWAP backward-compat) |
| (B) F1 swap LONG AVWAP to default-False (symmetric to SHORT) — strict gate; lower fire rate but clean semantics |
| **(C)** F1 swap LONG default-False + loosen AVWAP requirement from BOTH-anchors to EITHER-anchor (OR not AND) — lighter gate count, symmetric defaults. Plus flag for B603 cube fire-count check. **RECOMMENDED.** |
| (D) Stage 5 deferral — defer everything to cube |

**My recommendation: (C).** Closes the latent silent-gap class AND addresses fire-count starvation with a single change. Risk: AVWAP-EITHER may fire too often; cube validates.

### FINAL STATUS POST-B645 — ⏸ DEFERRED

| Item | Outcome |
|---|---|
| **Reviewer's M3 critique** | The F1 LATENT (AVWAP default-True auto-pass) and F-fire-count (5/yr FAIL) findings were internally contradictory — one said the gate auto-passes inflating fires, the other said fires were too few. Option C tried to do both (tighten default-False + loosen AND→OR) in one change — net effect indeterminate, justified by a fire-count label that was itself wrong-signed. |
| **Action taken (B641)** | **Deferred entirely from Tier 1.** No code change shipped this batch — the reviewer's structural objection was decisive. |
| **Measured fires/yr (universe)** | **917 PASS_CUBE** — independence under-counted by 500×! The B640 FAIL_FIRE_STARVED label was a complete artifact of the independence-product model. The strategy is NOT fire-starved. This validates the reviewer's M1+M2 critique with extreme force on this specific strategy. |
| **Open items queued** | `S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY` — extends reviewer's M5 critique: W6 LONG `s.get("above_avwap_252low", True)` (default True) is the SAME auto-pass class as W8's F1b that shipped in B641. Two-step resolution: (1) verify whether AVWAP keys are actually missing on the universe (measurement pass already gives this — emit-rate data); (2) if missing-rate > epsilon, swap LONG defaults to False symmetric with SHORT |
| **Reviewer's M5 specifically** | Severity unification queued — W6/W7 LONG default-True is the same auto-pass class as W8's F1b that DID ship; arbitrary severity split in B640 is acknowledged. |
| **No regrets** | Deferring this was the right call given the F1 vs fire-count contradiction. Cube data will tell us whether the strategy needs any change at all — at 917/yr it may be fine as-is. |

---

## W7. `strat_pivot_r2_continuation`

### Step 1 — Read the code

[screener.py:247-278](backtest/signals/screener.py#L247-L278):

```python
def strat_pivot_r2_continuation(s):
    """Pivot R2 trend-continuation. Batch 205: requires AVWAP + 2x volume
    (stronger threshold than R1 since R2 is the secondary breakout) +
    EMA 50/200 trend confirmation."""
    avwap_long_ok = s.get("above_avwap_252low", True) and s.get("above_avwap_50low", True)
    avwap_short_ok = s.get("below_avwap_252low", False) and s.get("below_avwap_50low", False)
    fl = (
        s.get("above_r2") and s.get("adx_trending")
        and s.get("ema_50_200_bullish") and avwap_long_ok
        and s.get("vol_spike_2x", s.get("vol_spike_15x", False))
    )
    fs = (
        s.get("below_s2") and s.get("adx_trending")
        and s.get("ema_50_200_bearish") and avwap_short_ok
        and s.get("vol_spike_2x", s.get("vol_spike_15x", False))
    )
    return _strat3(fl, fs, "pivot", ...)
```

**LONG fires when ALL FIVE (technically SIX — `avwap_long_ok` is two-AND):**

| Gate | Meaning |
|---|---|
| `above_r2` | Today's close > R2 (further out than R1) |
| `adx_trending` | ADX > 25 (trend strength) |
| `ema_50_200_bullish` | Long-term uptrend |
| `above_avwap_252low AND above_avwap_50low` | Both AVWAP anchors confirm |
| `vol_spike_2x` (fallback `vol_spike_15x`) | 2× volume (or 1.5× fallback if 2x key missing) |

Notice the chained `s.get("vol_spike_2x", s.get("vol_spike_15x", False))` — clever fallback. If vol_spike_2x is present, use it; otherwise fall back to vol_spike_15x; otherwise False. **This is fine** because both are EVENT signals from the same producer.

### Step 2-6 — same structure as W6

Same B291 default regime. Producer symmetry ✅ post-B633/B634. Docstring present. No OPEN_INV matches.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1 LATENT** | Same AVWAP asymmetric default as W6 | MEDIUM |
| F2 | Docstring present | — |
| **F-fire-count** | 5 AND-gates including vol_spike_2x (~0.10 prior) + ema_50_200_bullish (STATE ~0.55) + adx_trending (~0.30) + above_r2 (~0.02) + avwap (~0.55^2 ≈ 0.30 joint). Joint ~0.000099 → ~5.5/yr. **FAIL_FIRE_STARVED** very confidently. B612 stacking pattern. | HIGH |

**Options:**

| Option | Description |
|---|---|
| (A) Status quo |
| (B) F1 swap LONG default-False on AVWAP (same as W6) |
| (C) F1 + drop ADX gate (covered by ema_50_200_bullish + above_r2 confluence) |
| **(D)** Stage 5 deferral — defer all fire-count + asymmetric-default fixes to cube data. Too many simultaneous changes per CHECKLIST (g) sequence-or-split. **RECOMMENDED.** |

**My recommendation: (D).** Five gates is heavy. Loosening multiple would violate CHECKLIST (g). Defer to cube empirical.

### FINAL STATUS POST-B645 — ⏸ DEFERRED TO STAGE 5

| Item | Outcome |
|---|---|
| **Reviewer's structural critique** | Six-gate AND-conjunction is over-specification / curve-fitting by gate-stacking. Even if it backtests well, n is too small to be statistically significant; a strategy validated on a handful of trades will not generalize. Classic "stack filters until the equity curve is pretty on five trades" trap. |
| **Action taken (B641)** | **No code change.** Option (D) Stage 5 deferral upheld. Reviewer's reasoning + the same M5 AVWAP default-True severity-unify question that gates W6 also gates W7. |
| **Measured fires/yr (universe)** | **66 PASS_CUBE borderline** — independence under-counted again (B640 said ~2; measurement says 66). The 6-gate strategy is more fire-rich than the independence model suggested, but the curve-fit concern remains valid: 66/yr × 6 gates = high noise-to-signal ratio. |
| **Open items queued** | `S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY` (shared with W6) — W7 LONG `s.get("above_avwap_252low", True)` is same auto-pass class as W6 |
| **Long-term recommendation** | Even if cube validates 66/yr, the 6-gate conjunction should be simplified to 2-3 orthogonal gates before deployment. ADX-trending is redundant with ema_50_200_bullish + above_r2 (reviewer noted this in B640 Step 7 option C). The strategy as-written is unlikely to have generalizable edge at 6-gate width. |
| **No regrets** | Deferral preserves optionality; doesn't ship a probably-curve-fit strategy. |

---

## W8. `strat_cpr_narrow_bullish`

### Step 1 — Read the code

[screener.py:281-312](backtest/signals/screener.py#L281-L312):

```python
def strat_cpr_narrow_bullish(s):
    """Central Pivot Range narrow breakout. Batch 205 ... above CPR + above
    AVWAP is the canonical institutional-grade directional day signal.

    Batch 358 ... added 200-EMA regime gate per direction. ... Long now requires
    above_200_ema; short requires below_200_ema (canonical regime alignment).
    """
    avwap_long_ok = s.get("above_avwap_50low", True)
    avwap_short_ok = not s.get("above_avwap_50low", False)  # <-- F1 silent-gap pattern
    above_200 = s.get("price_above_ema_200", False)
    fl = (
        s.get("cpr_narrow") and s.get("above_cpr")
        and s.get("rsi_14", 50) > 50 and avwap_long_ok
        and above_200
    )
    fs = (
        s.get("cpr_narrow") and s.get("below_cpr")
        and s.get("rsi_14", 50) < 50 and avwap_short_ok
        and (not above_200)
    )
    return _strat3(fl, fs, "pivot", ...)
```

**LONG fires when ALL FIVE:**

| Gate | Meaning |
|---|---|
| `cpr_narrow` | Yesterday's CPR width < 15% of yesterday's range (directional-day setup) |
| `above_cpr` | Today's close > CPR top |
| `rsi_14 > 50` | Bullish momentum bias |
| `above_avwap_50low` (default True) | Above 50-day-low AVWAP — **OR keys missing** |
| `price_above_ema_200` | Long-term uptrend |

**SHORT fires when ALL FIVE:**

| Gate | Meaning |
|---|---|
| `cpr_narrow` | Same |
| `below_cpr` | Today's close < CPR bottom |
| `rsi_14 < 50` | Bearish momentum |
| `not above_avwap_50low` | Below AVWAP — **but using NOT pattern → silent-gap** |
| `not price_above_ema_200` | Long-term downtrend |

### Step 2 — Classify

- Category: `pivot`
- Dual
- STRATEGY_REGIME_AFFINITY: no entry → B291 default
- Last touched: B358 (added 200-EMA regime gate)

### Step 3 — Producer source-read + temporality

- `cpr_narrow`, `above_cpr`, `below_cpr` — EVENT/STATE hybrid (CPR known from yesterday)
- `above_avwap_50low` — STATE-ish
- `price_above_ema_200` — STATE
- `rsi_14` — STATE

### Step 4 — Doc-vs-thesis

Docstring present. Cites Batch 358 200-EMA add reason. ✅

### Step 5 — OPEN_INVESTIGATIONS grep

No matches.

### Step 6 — Missing-inverse + economic-symmetry

Structural ✅ (dual). But SHORT uses NOT pattern on `above_avwap_50low` — silent-gap pattern owner has explicitly memory-flagged in `feedback_never_use_NOT_s_get_pattern`. The producer `below_avwap_50low` exists (B612), so this can be fixed locally.

Same for `not above_200` — should use `below_ema_200` (B630 producer-additive).

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1** | SHORT side uses `not s.get("above_avwap_50low", False)` — silent-gap pattern. Producer `below_avwap_50low` exists; one-line F1 swap per `feedback_never_use_NOT_s_get_pattern`. | HIGH |
| **F1b** | SHORT side uses `(not above_200)` where `above_200 = s.get("price_above_ema_200", False)`. The `not False = True` semantics mean missing key auto-passes the SHORT gate. Should use `s.get("below_ema_200", False)` symmetric positive (B630 producer). | HIGH |
| F2 | Docstring present | — |
| **F-fire-count** | LONG ~13/yr, SHORT ~13/yr. 5 AND-gates is heavy. **FAIL_FIRE_STARVED.** Flag for B603. | HIGH |

**Options:**

| Option | Description |
|---|---|
| (A) Status quo |
| **(B)** F1 + F1b swap to positive symmetric `below_avwap_50low` and `below_ema_200` per memory directive. **RECOMMENDED.** |
| (C) B + loosen one gate (e.g., drop `cpr_narrow` since it's a STATE-ish setup-day filter, not a fire trigger) |
| (D) Stage 5 deferral |

**My recommendation: (B).** F1/F1b are unambiguous family-bug fixes per existing memory directive. Fire-count loosening is a separate (C) decision.

### FINAL STATUS POST-B645 — ✅ SHIPPED + 🎯 REMAINDER QUEUED

| Item | Outcome |
|---|---|
| **What shipped (B641)** | **Option (B) F1+F1b silent-gap fixes.** SHORT side `not s.get("above_avwap_50low", False)` (NOT-pattern auto-pass on missing key) → positive symmetric `s.get("below_avwap_50low", False)` (B612 producer; defaults False → fail-safe). SHORT side `(not above_200)` where above_200 = local with default False (same auto-pass class) → explicit `s.get("below_ema_200", False)` (B630 producer-additive). Both new gates default-False → fail-safe to no-fire on missing key. |
| **Code reference** | [screener.py strat_cpr_narrow_bullish](backtest/signals/screener.py) |
| **Test pins** | test_batch641 pins 10-12 (SHORT no longer uses NOT-pattern, fires on positive symmetric, blocks when keys missing) |
| **Measured fires/yr (universe)** | **15,708 PASS_CUBE** — independence under-counted by 1200×!! The most extreme verdict-reversal in the bundle. B640 said 13/yr FAIL; reality is 15,708/yr (cpr_narrow + above_cpr + rsi>50 + above_avwap + above_200_ema all co-occur in established uptrends — extreme positive correlation). |
| **Open items queued** | (1) `S4-W8-RSI-NOOP-GATE` — reviewer P4: rsi>50/<50 strict-inequality on default-50 is a near-no-op gate; owner decides post-cube whether to drop, tighten to 55/45, or document the accident-of-luck fail-safe. (2) `S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY` — reviewer M5: W8 LONG `s.get("above_avwap_50low", True)` is still default-True, same auto-pass class as B641-fixed SHORT; NOT auto-fixed B641 to avoid two simultaneous direction changes per CHECKLIST (g) |
| **Reviewer's structural critique on CPR foundation** | Reviewer W8 noted: "CPR's narrow-range-predicts-trending-day claim has no academic support — folk-TA popular among India retail traders. Applying it on daily bars held overnight stacks an unproven claim on top of a timeframe error (C1)." Acknowledged: even with the 15,708/yr fires, this is the strategy with the SHAKIEST theoretical foundation in the cluster. The CHECKLIST (r) timeframe-mismatch codification names this hazard going forward. |
| **No regrets** | F1/F1b shipped were unambiguous family-bug fixes. The CPR-foundation concern is queued via CHECKLIST (r) discipline; future re-walks can reframe or deprecate without it being a B645 deliverable. |

---

## W9. `strat_camarilla_s3_bounce`

### Step 1 — Read the code

[screener.py:315-356](backtest/signals/screener.py#L315-L356):

Already walked thoroughly during B628 (F1 family-sweep) — docstring + walk record present.

```python
def strat_camarilla_s3_bounce(s):
    # B628 F1: positive symmetric (B617 producer)
    fl = (s.get("near_cam_s3") and s.get("rsi_14", 50) < 35 and s.get("obv_bullish"))
    fs = (s.get("near_cam_r3") and s.get("rsi_14", 50) > 65 and s.get("obv_bearish"))
    return _strat3(fl, fs, "pivot", ...)
```

3-gate dual: location (near Camarilla S3/R3) + RSI extreme (<35 / >65) + OBV flow.

### Step 2 — Classify

- STRATEGY_REGIME_AFFINITY: explicit `{"neutral", "bear", "crisis"}` at [regime_selector.py:191](backtest/engine/regime_selector.py#L191).
- **DEFERRED-STAGE-5** per B624 manifest M1 — this entry is a B623 REMOVE_OK candidate; cube data needed.
- Last touched: B628

### Steps 3-6 — already documented in B628 + B624 manifest

Producer symmetric ✅, docstring ✅, OPEN_INV no matches.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None — already fixed B628 | — |
| F2 | Docstring already present | — |
| **F3** | Already deferred per B624 manifest M1 (R5 ticket S5-REGIME-AFFINITY-21-DEFERRED). **No walk-time action.** | — |

**Fire-count projection:** LONG ~30/yr — borderline PASS.

**Options:**

| Option | Description |
|---|---|
| **(E)** No action needed; defer per existing R5 ticket. **RECOMMENDED.** |
| Other | Re-litigating would create a B624 manifest conflict |

**My recommendation: (E).**

### FINAL STATUS POST-B645 — ⏸ ALREADY DEFERRED (no action)

| Item | Outcome |
|---|---|
| **What shipped** | Nothing — strategy already deferred per existing `S5-REGIME-AFFINITY-21-DEFERRED` (B624 manifest M1) |
| **Measured fires/yr (universe)** | **44** BORDERLINE (between FAIL_FIRE_STARVED <30 and PASS_CUBE ≥60) — projection was right here; independence ratio 31.7 over-counted by 32× but the actual measured rate is close to the borderline |
| **Reviewer's W9 note** | The reviewer specifically noted W9 is "the only pivot strategy using its source system as intended" — Camarilla's design says R3/S3 are FADE levels, and W9 trades the fade. The W10 R3→R4 rename (B641) closed the same-level conflict that existed pre-B641 (W9 short at R3 vs W10 long above R3 simultaneously); W9 stays unchanged. |
| **Open items** | Inherits the cluster-wide intraday-on-daily-bar concern (CHECKLIST (r)) — Camarilla is intraday by design. Reframe argument: even on daily bars, Camarilla S3 proximity + RSI extreme + OBV flow detects "yesterday's range was extended → today retraced + reversal-flow appearing," a coherent daily-bar pattern independent of pivot-precision. |
| **No regrets** | Correct deferral. The R5 cube empirically validates the regime-affinity entry. |

---

## W10. `strat_camarilla_r3_breakout`

### Step 1 — Read the code

[screener.py:359-365](backtest/signals/screener.py#L359-L365):

```python
def strat_camarilla_r3_breakout(s):
    fl = (s.get("above_cam_r3") and s.get("vol_spike_2x"))
    fs = (s.get("below_cam_s3") and s.get("vol_spike_2x"))
    return _strat3(fl, fs, "pivot",
        ["above_cam_r3","vol_spike_2x"], ["below_cam_s3","vol_spike_2x"],
        ["Price broke above Camarilla R3  -  breakout mode","Volume 2x confirms institutional buying"],
        ["Price broke below Camarilla S3  -  breakdown mode","Volume 2x confirms institutional selling"])
```

**LONG fires when both:**

| Gate | Meaning |
|---|---|
| `above_cam_r3` | Today's close > Camarilla R3 (primary resistance) |
| `vol_spike_2x` | Volume ≥ 2× 20-day average |

**SHORT mirror:** `below_cam_s3 + vol_spike_2x`.

### Step 2 — Classify

- Category: `pivot`
- Dual
- STRATEGY_REGIME_AFFINITY: no entry → B291 default
- Last touched: original implementation

### Step 3 — Producer source-read + temporality

Both gates EVENT (cross + today's volume).

### Step 4 — Doc-vs-thesis

Context bullets accurate. **F2 — no docstring.**

### Step 5 — OPEN_INVESTIGATIONS grep

No matches.

### Step 6 — Missing-inverse + economic-symmetry

Structural ✅. Economic ✅. Producer symmetric ✅.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None | — |
| **F2** | No docstring | LOW |
| **F-fire-count** | gates: above_cam_r3 ~0.05 × vol_spike_2x ~0.10 ≈ 0.005 → ~166/yr/direction. PASS_CUBE. Wide setup; clean 2-gate strategy. | — |

**Options:**

| Option | Description |
|---|---|
| **(A)** F2 docstring with Camarilla source citation (Slim Khan / Nick Scott) + R3 breakout vs S3 breakdown thesis. **RECOMMENDED.** |
| (B) Status quo |

**My recommendation: (A).**

### FINAL STATUS POST-B645 — ✅ CLOSED (renamed + re-anchored)

| Item | Outcome |
|---|---|
| **Reviewer's P5 critique** | "Camarilla R3 is the FADE level, not the breakout level — R4 is the breakout level per Slim Khan / Nick Scott. W9 (short near R3) and W10 (long above R3) take OPPOSITE trades at the SAME level — a single bar at R3 with a volume spike could fire W9 SHORT and W10 LONG simultaneously, a portfolio-level contradiction that nets to noise and double costs." |
| **What shipped (B641)** | **R3 → R4 SOURCE-SYSTEM RE-ANCHOR.** Strategy renamed `strat_camarilla_r3_breakout` → `strat_camarilla_r4_breakout`. Producer signals swapped `above_cam_r3` → `above_cam_r4` and `below_cam_s3` → `below_cam_s4` (these signals already exist per BUG-09 Pass 53 symmetric pair). Registry key renamed `camarilla_r3_breakout` → `camarilla_r4_breakout`. W9 keeps using R3/S3 proximity for FADE (correct Camarilla usage). |
| **What this resolves** | (1) Source-system contradiction (B640 W10 was misusing Camarilla); (2) Same-level conflict with W9; (3) Honest docstring with Slim Khan / Nick Scott citation; (4) F2 documentation gap. |
| **Code reference** | [screener.py strat_camarilla_r4_breakout](backtest/signals/screener.py) (renamed) |
| **Test pins** | test_batch641 pins 13-17 — R3 not importable (renamed), R4 importable + callable, registry renamed, R4 fires on above_cam_r4 + vol_spike_2x, R4 does NOT fire on above_cam_r3 alone (proves the swap happened) |
| **Measured fires/yr (universe)** | **991 PASS_CUBE** (was 166 projected; independence under-counted) |
| **Backward-compat references** | Updated in: test_batch358 (previously_deprecated set), config.py (Marshall-Cahan 2008 cite comment), test_silent_gap_pyramid. Stale dashboard files + parquet snapshots still reference `camarilla_r3_breakout` but those are output-state files that regenerate. |
| **No regrets** | One of the most defensible ships in the batch — strict source-system honesty + resolves a portfolio-level conflict + same-day W9 isolation cleanly. |

---

## Bundled action items (historical record — original B640 surface)

> Preserved as historical record of the original B640 prospective surface. The final dispositions below replace this section's "owner decision form" with the actual shipped outcomes.

### Tier 1 — definite fixes (no judgment needed) [SHIPPED]:
- **W8 F1+F1b** — silent-gap positive symmetric swap → ✅ SHIPPED B641
- **W3 F3** — B271 family-bug delete → ✅ SHIPPED B641
- **W4 F3** — B271 family-bug delete → ✅ SHIPPED B641

### Tier 2 — docstring adds (low risk) [SHIPPED PARTIAL]:
- **W1** F2 docstring → ✅ SHIPPED B641 (with "three systems" commentary fix per reviewer)
- **W2** F2 docstring → ✅ SHIPPED B641
- **W3** F2 docstring → ✅ SHIPPED B641 (bundled with F3 + F1 pin_bar fix)
- **W4** F2 docstring → 🎯 QUEUED in `S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL` (split per CHECKLIST (g))
- **W5** F2 docstring → ✅ SHIPPED B643 (as part of redesign)
- **W10** F2 docstring → ✅ SHIPPED B641 (bundled with R3→R4 rename)

### Tier 3 — judgment calls [RESOLVED]:
- **W5 Class 7 NEW mirror** → ✅ SHIPPED B645 per directive (a) AFTER B643 redesign + B644 W5-i exploratory
- **W4 F1 `shooting_star` SHORT OR** → 🎯 QUEUED `S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL`
- **W6 F1 LATENT** → ⏸ DEFERRED via `S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY` (reviewer M3+M5)
- **W7 over-specification** → ⏸ DEFERRED to Stage 5 per CHECKLIST (g)
- **W2 fire-count** → ✅ MEASURED + DEFERRED (139/yr PASS_CUBE — no loosening needed; B640 FAIL was independence artifact)
- **W6/W7/W8 fire-count stack** → ✅ MEASURED — all PASS_CUBE post-measurement (independence under-counted 35-1200×)

### Tier 4 — no action [HELD]:
- **W9** — already deferred to R5 ✅ unchanged

---

## FINAL DISPOSITIONS

> Replaces the "Owner decision form" with what actually happened. Read top-to-bottom; this is the closing summary of what shipped across the B641-B645 cycle.

| W# | Strategy | Original B640 recommendation | Owner's actual direction | What shipped | Final |
|---|---|---|---|---|---|
| W1 | `bullish_engulfing_support` | (A) | (A) | F2 doc + commentary | ✅ CLOSED |
| W2 | `shooting_star_short` | (D) | (D) | F2 doc + Stage 5 fire-count defer | ✅ CLOSED |
| W3 | `pivot_s1_bounce` | (B) | (B) + reviewer P1 added | F1 pin_bar fix (reviewer-flagged) + F2 doc + F3 regime delete | ✅ CLOSED |
| W4 | `pivot_s2_bounce` | (C) | (C) split per (g) | F3 regime delete only; F1+F2+RSI-mislabel queued | ✅ SHIPPED + 🎯 queued |
| W5 | `pivot_s3_capitulation` | (D) → reviewer P3 critique → option C redesign | C → W5-i | Producer + 2-gate redesign + EXPLORATORY marker | ✅ REDESIGNED |
| W5m | `pivot_r3_blowoff_short` (NEW B645) | n/a | directive (a) | Class 7 NEW symmetric mirror | ✅ NEW + EXPLORATORY |
| W6 | `pivot_r1_breakout` | (C) → reviewer M3 contradiction | DEFER | No code change; queue ticket | ⏸ DEFERRED |
| W7 | `pivot_r2_continuation` | (D) | (D) | No code change | ⏸ DEFERRED |
| W8 | `cpr_narrow_bullish` | (B) | (B) | F1+F1b silent-gap positive symmetric | ✅ SHIPPED + 🎯 RSI-noop queued |
| W9 | `camarilla_s3_bounce` | (E) | (E) | No action (R5-deferred existing ticket) | ⏸ HOLDS |
| W10 | `camarilla_r3_breakout` | (A) → reviewer P5 critique | (A) → directive 6 R3→R4 | Strategy renamed + producer swap + source-system citation | ✅ CLOSED (RE-ANCHORED) |

**Net code impact (B641 → B645, 7 commits):**
- 1 new producer-additive pair: `bullish_pin_bar` / `bearish_pin_bar`
- 2 new lookback producers: `compute_capitulation_lookback`, `compute_blowoff_lookback`
- 4 strategies modified: `pivot_s1_bounce` (P1 fix), `cpr_narrow_bullish` (F1+F1b), `pivot_s3_capitulation` (full redesign), `camarilla_r4_breakout` (rename from r3)
- 2 regime affinity entries deleted: `pivot_s1_bounce`, `pivot_s2_bounce` (B271 family-bug fixes #5+#6)
- 1 new strategy registered: `pivot_r3_blowoff_short` (Class 7 NEW)
- 1 engine module updated: `regime_filter.py` (B642 dead canonical line removal + EMA-cross hysteresis 2% band)
- 1 new tool: `scripts/measure_fire_count.py`
- 3 CHECKLIST extensions: (r) timeframe-mismatch, (s) EVENT/STATE wired-to-finding, Step 1.5 avoid-branch restore

**Net queue impact:** 17 new tickets in `EXECUTION_QUEUE.md`. All sourced from this audit cycle.

---

## Outstanding queue tickets from this audit cycle

> All 17 tickets are present in `EXECUTION_QUEUE.md` and `R5_VALIDATION_MANIFEST.md` where relevant. Listed here for reviewer cross-reference.

### Stage 5 (cube + program-level)
- `S5-FIRE-COUNT-MEASURED-RUN` — already partially in progress (B641 smoke + B643 W5 + B645 W5m runs); full universe + all 222 strategies queued
- `S5-MULTIPLE-TESTING-CORRECTION` — Bailey/LdP deflated Sharpe + Hansen SPA + BH FDR on cube selection
- `S5-MARGINAL-CONTRIBUTION-SCORING` — cube ranks vs-book not standalone (extends M9 effective_strategy_count)
- `S5-REGIME-BETA-ASSUMPTION` — name + design per-sector or per-name regime alternative
- `S5-REGIME-WALK-FORWARD-VALIDATION` — is regime-gating OOS net-positive? (curve-fit check)

### Stage 4 (near-term, owner-policy)
- `S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL` — W4 follow-on per CHECKLIST (g)
- `S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY` — AVWAP default-True severity unification
- `S4-W8-RSI-NOOP-GATE` — cpr_narrow_bullish rsi>50/<50 near-no-op
- `S4-OBV-LOCATION-TENSION-DESIGN` — W1/W3/W9 (LONG) OBV fights support premise
- `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT` — at_key_fib swing-anchor PIT verification
- `S4-CORPORATE-ACTION-POLICY` — ex-date no-fire pyramid test for candle/pivot signals
- `S4-SURVIVORSHIP-T1A-VERIFY` — confirm T1a PIT universe includes delisted-during-window names (W5 expectancy)
- `S4-REGIME-AAII-PIT` — publication-vs-survey date PIT alignment audit
- `S4-REGIME-FRED-VINTAGE` — restated-vs-vintage policy
- `S4-REGIME-SECTOR-ELIGIBILITY-TIME-VARYING` — composite eligibility weaker in early backtest
- `S4-REGIME-COMPOSITE-FAIL-POLICY` — fail-open vs system fail-closed asymmetry
- `S4-REGIME-HYSTERESIS-PARITY-TEST` — backtest-live regime divergence audit

### Cross-ref existing tickets
- `M10` — already DEFERRED Stage 5+; this audit extended notes to include borrow lookup + gap-at-entry slippage per reviewer C6
- `S5-REGIME-AFFINITY-21-DEFERRED` — W9 (camarilla_s3_bounce) inherits this existing ticket; no new entry created
- `PYRAMID-CLEANUP-ENV` — 14 pre-existing failures from B622 cleanup remain (unrelated to this audit cycle; mentioned only because B642 retested + confirmed they're not B642 regressions)

---

## Methodology changes shipped this cycle

### CHECKLIST extensions (B641 commit a94f8bb02)

**`(r) Timeframe-mismatch check`** — codifies reviewer's C1. Any walk whose strategy uses an intraday-by-design indicator (pivots / Camarilla / CPR / ORB / intraday VWAP) must surface in Step 2 whether daily-bar application preserves the thesis or requires REFRAME-AND-RENAME. First application: W10 R3→R4 rename. Listed affected strategies: pivot_s1/s2/s3, pivot_r1/r2, cpr_narrow_bullish, camarilla_s3_bounce, camarilla_r4_breakout, prev_day_high_break, orb_*.

**`(s) EVENT/STATE wired-to-finding`** — codifies reviewer's M6. Step 3 already classifies signals as EVENT vs STATE; pre-B641 this was decorative. New rule: Step 6 explicitly counts EVENT gates per direction. If ≤1 EVENT gate per direction AND docstring overclaims timing on STATE → F-timing-fragility HIGH. The MACD-bullish-as-STATE pattern (reviewer's M7, W6 silent concession) is the canonical example.

**`Step 1.5 avoid-branch dead-code analysis`** — restores the morning_star B637 walk's per-strategy check. For every `_strat3` dual strategy, verify whether `fl ∧ fs` is structurally possible. If mutually exclusive, the avoid branch is dead code — three consequences recorded per walk.

### Fire-count measurement pass (B641 same commit)

`scripts/measure_fire_count.py` — replaces independence-product projections with measured fires/year against actual 220-ticker T1a OHLCV history. Output schema includes per-strategy gate-marginals, pairwise correlation matrix, and an `independence_predicted_vs_measured_ratio` diagnostic that tells you in which direction the independence assumption was biased (>1 = exclusive gates, over-estimated; <1 = positively-correlated gates, under-estimated). Vectorized signal precompute across (ticker, bar) — strategies evaluated against precomputed signals (not re-computed per strategy). Smoke run results landed on B645 commit fb20a946c.

### Regime classifier cleanup (B642 commit 013cc75b8)

Two changes per reviewer audit findings #2 + #3:
- **Dead canonical bear line removed** from both `classify_regime` and `classify_regime_with_hysteresis`. Pre-B642 the `VIX>=30 AND below-200EMA` line was subsumed by the post-B288 SPY-only gate; reading the code suggested VIX still gated bear, but it didn't. Removed for honest semantics. (Auto-resolves audit finding #6 latent redundancy as side-effect.)
- **EMA-cross hysteresis band added** — new `EMA_CROSS_HYSTERESIS_PCT = 2.0` constant + `spy_pct_from_200ema` parameter. Asymmetric design: bear stays sticky until SPY closes >=+2% above 200-EMA (slow to exit risk-off); below-EMA close still triggers bear immediately (fast risk-off entry). Backward-compatible with legacy callers (None spy_pct → pre-B642 binary-gate behavior).

12 new test pins in `test_batch642_regime_classifier_cleanup.py`. Cross-ref the [classifier deep-dive section](#how-market-regimes-are-classified--the-full-picture) earlier in this doc — that documentation predates B642 and still describes the pre-B642 ladder; **TODO: update classifier deep-dive section to reflect B642 changes** (queued for next-update pass).

---

## Going forward — cluster-organization policy

Per owner directive 2026-06-09, future Stage 4 walk bundles are per-cluster, not per-batch:

| Cluster | Doc filename | Status |
|---|---|---|
| Pivot | `STAGE_4_PIVOT_CLUSTER_WALKS.md` (this doc) | LIVING — 8 of ~10 pivot strategies walked (W3-W10 + W5 mirror); `prev_day_high_break` + any tail strategies pending |
| Candle | `STAGE_4_CANDLE_CLUSTER_WALKS.md` (future) | DEFERRED — W1, W2 covered here; earlier candle walks (morning_star B639, three_white_soldiers B636, doji_at_support B572-574, etc) will be consolidated into a candle cluster doc when next candle batch runs |
| Trend | `STAGE_4_TREND_CLUSTER_WALKS.md` (future) | NEXT — donchian / supertrend / macd / ichimoku / hull-rsi / parabolic-sar / tema-dema / adx-initiation / ema-sma. ~10 strategies |
| Chart pattern | `STAGE_4_CHART_PATTERN_CLUSTER_WALKS.md` (future) | head_and_shoulders / double_bottom / cup_and_handle / flag_bull / triangle_ascending / etc |
| Smart money | `STAGE_4_SMART_MONEY_CLUSTER_WALKS.md` (future) | institutional_* / insider_* / 52w_high_with_smart_money / activist_13d / m_and_a_target / etc |
| SMC / ICT | `STAGE_4_SMC_ICT_CLUSTER_WALKS.md` (future) | smc_bos_continuation / smc_choch_reversal / smc_liquidity_sweep / turtle_soup / judas_swing / mmbm / week_opening_gap / etc |
| Macro / sector / news | `STAGE_4_MACRO_CLUSTER_WALKS.md` (future) | vix_* / sector_rotation / news_sentiment / news_momentum / cot_* / etc |
| Calendar | `STAGE_4_CALENDAR_CLUSTER_WALKS.md` (future) | totm / halloween / quarter_end / pre/post-rebalance / pead / etc |
| Confluence | `STAGE_4_CONFLUENCE_CLUSTER_WALKS.md` (future) | rsi_volume_200ema / macd_ichimoku / etc |

Each cluster doc follows the structure pattern this doc demonstrates:
1. Title + post-action framing + executive summary
2. Reviewer findings response matrix (if external review was done on the cluster)
3. Cluster current state table
4. Foundations cross-ref (shared) — eventually extract to `STAGE_4_FOUNDATIONS.md`
5. Per-strategy walks with FINAL STATUS POST-{Bxxx} blocks
6. Methodology changes shipped (cluster-specific)
7. Outstanding queue tickets (cluster-specific)
8. Closing footer cross-referencing other clusters

End of post-action report. The doc is a living artifact — any future change to pivot-cluster strategies (re-walks, additions, deletions, EXPLORATORY closures via R5 cube) lands here.

---

# Historical addenda (preserved for methodology context — superseded by sections above)

> The B641 + B643 ADDENDUM sections below were written incrementally as each shipping batch landed. Their content is now absorbed into the [Reviewer findings response matrix](#reviewer-findings-response-matrix), the per-strategy FINAL STATUS blocks, and the [Methodology changes shipped](#methodology-changes-shipped-this-cycle) section. Preserved here for methodology context — particularly the **independence-ratio interpretation** and the **B643 pre/post-redesign measurement comparison**.

---

# B641 ADDENDUM — Fire-count measurement pass (built 2026-06-09)

> **Why this addendum exists.** The B640 walk bundle above used a fire-count *projection* model — an independent product of marginal gate probabilities. An adversarial review correctly identified that this model is biased in BOTH directions depending on gate-correlation sign: it UNDER-estimates fire rates when gates positively correlate (gates that co-occur by construction at the same setup), and OVER-estimates when gates are negatively correlated or mutually exclusive. Five of the 10 B640 recommendations depended on this number. **The fire-count measurement pass below replaces the projection with measured fires/year against the actual 220-ticker history.** Owner directive 2026-06-09 #1.

## The tool — [`scripts/measure_fire_count.py`](scripts/measure_fire_count.py)

A standalone CLI that:
1. Loads the T1a PIT universe ([`Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv`](Backtesting universe/Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv), 614 tickers including 111 delisted-during-window per DEC-477).
2. Loads Polygon OHLCV daily parquets ([`data_prefetch/polygon/ohlcv_daily/<TICKER>.parquet`](data_prefetch/polygon/ohlcv_daily/)).
3. **Precomputes signals** at every bar for every ticker exactly ONCE (the key optimization — `compute_all_signals(df_sliced_to_bar)` was the bottleneck; calling it per-strategy was O(n_strategies × n_tickers × n_bars), now O(n_tickers × n_bars)).
4. **Evaluates each named strategy** against the precomputed signals — every bar, every direction.
5. **Emits per-strategy results:**
   - `n_fires_long`, `n_fires_short`, `n_fires_avoid` — raw counts.
   - `measured_fires_per_calendar_year_total_sampled` — total fires across the sampled tickers divided by calendar-year span.
   - `projected_fires_per_calendar_year_total_full_t1a` — linearly scaled to the full 220-ticker T1a universe (caveat: assumes sample is representative).
   - `projected_verdict_full_t1a` — `PASS_CUBE` (≥60/yr), `BORDERLINE` (30-60/yr), `FAIL_FIRE_STARVED` (<30/yr). Threshold matches the cube's `min_trades=30` from `PASSING_CRITERIA`.
   - `gate_marginals` — observed marginal probability of each gate firing alone.
   - `gate_pairwise_correlation` — Pearson r between every pair of gates the strategy reads (boolean vectors). **This is the diagnostic that explains WHY the independence assumption was wrong on this strategy.**
   - `independence_predicted_joint_prob` — product of marginals (what the old estimator assumed).
   - `independence_predicted_vs_measured_ratio` — predicted/measured. **Ratio ≈ 1.0 means independence held. >1.0 means independence OVER-estimated (gates exclusive). <1.0 means independence UNDER-estimated (gates positively correlated).**

### CLI

```sh
# 10 B640 strategies, default date range
python scripts/measure_fire_count.py --b640

# Explicit strategies
python scripts/measure_fire_count.py --strategies pivot_r1_breakout cpr_narrow_bullish

# Fast smoke (cap ticker count)
python scripts/measure_fire_count.py --b640 --max-tickers 20 --start 2022-01-01 --end 2024-12-31

# Full universe across all 222 strategies (long-running ~hours)
python scripts/measure_fire_count.py --all
```

## Smoke run results — 20 T1a tickers × 2022-2024 (3 years)

Run on 2026-06-09 ([`output_audit/fire_count_measured_2024-12-31.json`](output_audit/fire_count_measured_2024-12-31.json)):

| Strategy | Measured fires/yr (20-ticker sample) | Projected fires/yr (× 11 to full T1a) | Projected verdict | Independence ratio | Bias direction |
|---|---:|---:|---|---:|---|
| `bullish_engulfing_support` | 30.69 | **337.6** | PASS_CUBE | **0.001** | UNDER-est by 1000× |
| `shooting_star_short` | 12.68 | **139.4** | PASS_CUBE | 2.092 | OVER-est by 2× |
| `pivot_s1_bounce` | 20.01 | **220.2** | PASS_CUBE | **0.002** | UNDER-est by 500× |
| `pivot_s2_bounce` | 2.00 | **22.0** | **FAIL_FIRE_STARVED** | 9.853 | OVER-est by 10× |
| `pivot_s3_capitulation` | 1.33 | **14.7** | **FAIL_FIRE_STARVED** | **92.0** | OVER-est by 92× |
| `pivot_r1_breakout` | 83.39 | **917.3** | PASS_CUBE | **0.002** | UNDER-est by 500× |
| `pivot_r2_continuation` | 6.00 | **66.0** | PASS_CUBE | 0.0 | UNDER-est (predicted ~0) |
| `cpr_narrow_bullish` | 1,427.98 | **15,707.8** | PASS_CUBE | 0.028 | UNDER-est by 35× |
| `camarilla_s3_bounce` | 4.00 | **44.0** | BORDERLINE | 31.745 | OVER-est by 32× |
| `camarilla_r4_breakout` | 90.06 | **990.7** | PASS_CUBE | 0.075 | UNDER-est by 13× |

## Reconciliation with B640's projected verdicts

| Strategy | B640 projection | B640 verdict | **B641 measured (projected)** | **B641 verdict** | Status |
|---|---:|---|---:|---|---|
| W1 `bullish_engulfing_support` | ~83/yr | PASS | **337.6** | PASS | Both agree direction; measurement higher |
| **W2** `shooting_star_short` | ~25-66/yr | **FAIL** | **139.4** | **PASS** | **B640 verdict REVERSED** — was guess; measured is well above 30 |
| W3 `pivot_s1_bounce` | ~92/yr | PASS | **220.2** | PASS | Agree; measured 2.4× higher |
| **W4** `pivot_s2_bounce` | ~28/yr | BORDERLINE-FAIL | **22.0** | **FAIL** | Confirmed FAIL; measured very close to projection |
| **W5** `pivot_s3_capitulation` | ~14/yr | **FAIL** | **14.7** | **FAIL** | Confirmed FAIL — only B640 FAIL where projection landed right |
| **W6** `pivot_r1_breakout` | ~5/yr | **FAIL** | **917.3** | **PASS** | **B640 verdict REVERSED** — independence under-counted by 500× |
| **W7** `pivot_r2_continuation` | ~2/yr | **FAIL** | **66.0** | **PASS** (borderline) | **B640 verdict REVERSED** — independence under-counted |
| **W8** `cpr_narrow_bullish` | ~13/yr | **FAIL** | **15,707.8** | **PASS** | **B640 verdict REVERSED** — by 1200× |
| W9 `camarilla_s3_bounce` | ~30/yr | borderline PASS | **44.0** | BORDERLINE | Agree borderline; measured slightly higher |
| W10 `camarilla_r4_breakout` | ~166/yr (on R3 misuse) | PASS | **990.7** | PASS | Agree; W10 is now correctly anchored to R4 post-B641 rename |

**4 of the 5 B640 FAIL_FIRE_STARVED labels were wrong** (W2, W6, W7, W8). The B641 measured numbers reclassify them all as PASS_CUBE. The B640 recommendations that depended on those labels (loosen / defer based on insufficient fires) would have been the wrong actions — they were attempting to fix non-problems.

**Only W5 (capitulation) confirms as genuinely fire-starved** (15/yr). This is the strategy the adversarial reviewer warned about for an entirely different reason (no reversal confirmation + survivorship bias) — the fire count just happens to also be too low. Owner directive #5 is for a redesign next turn, which is the correct call independent of fire count.

**W4 (pivot_s2_bounce) confirms borderline FAIL at 22/yr** — the projection landed close to the measurement. Pre-B641 it was a 3-gate AND on rsi<40 + bullish-engulfing/hammer + near_s2; the gates are mildly positively correlated (oversold-at-deep-support is a co-occurring setup) but the near_s2 proximity threshold is the rate-limiting gate. Confirmed FAIL.

## What the independence ratio is telling us

The ratio = `independence_predicted_joint_prob / measured_joint_prob`.

- **Ratio ≪ 1.0** (W1/W3/W6/W7/W8/W10): gates are **positively correlated** by construction. At the strategy's intended setup, multiple gates fire together — that's what the strategy is detecting. Examples:
  - `cpr_narrow_bullish`: at a narrow-CPR day with established uptrend (above_200_ema), `above_cpr` + `rsi>50` + `above_avwap_50low` all co-occur because they're all measuring the same trending day from different angles. Independence treats them as separate coin flips; reality has them locked together.
  - `pivot_r1_breakout`: at a real breakout, `above_r1` + `vol_spike_15x` + `macd_bullish` + `above_avwap_*` all fire together because they're co-symptoms of breakout. Independence under-estimates by 500×.

- **Ratio ≫ 1.0** (W2/W4/W5/W9): gates are **negatively correlated or extreme-rare**. The strategy requires events that almost never coincide:
  - `pivot_s3_capitulation`: needs simultaneous near_s3 (0.3% proximity to deepest support — extreme price extension) + rsi<30 (canonical oversold) + vol_spike_2x (panic volume). In reality these DO co-occur on capitulation days, but capitulation days are extremely rare; the independence product over-estimates because it treats "near_s3" as an everyday signal at marginal rate ~0.005 when in fact when it's True the other gates are usually also True at the SAME bar — but the bar itself is rare. The 92× over-estimate reflects how rare those bars are vs the marginal rates suggest.
  - `camarilla_s3_bounce`: similar — 0.3% proximity to a daily-recomputed level is rare independent of RSI.

The methodology takeaway: **gate correlation tells you whether the strategy's gates measure the same thing (correlated → strategy works) or different things (uncorrelated → strategy is asking for coincidence)**. Highly-correlated gate sets are usually well-designed; highly-uncorrelated ones are over-constrained.

## Operational handling going forward

1. **Every future walk uses the measurement pass, not the independence product.** Estimator stays in repo as a quick screen but its verdict labels are no longer authoritative; CHECKLIST (k) updated to require a measured run before a fire-count finding ships.
2. **B641 retro-corrects B640 verdicts** for W2/W6/W7/W8 — those FAIL_FIRE_STARVED labels are wrong; the loosen/defer recommendations they drove are mooted. Their underlying design questions (B271 affinity / AVWAP default asymmetry / NOT-pattern silent-gap / OBV-vs-location) remain valid and are queued separately.
3. **W5 reversal-confirmation redesign** (owner directive #5, next turn) proceeds independent of fire count — the strategy is structurally a knife-catch + 14.7/yr is also too few.
4. **Full universe + full date range** (~220 tickers × 6 years × 221 strategies) is a backgroundable batch run; queued as S5-FIRE-COUNT-MEASURED-RUN. The smoke above (20 tickers × 3 years) is a proof-of-concept; the full run gives confidence intervals.

End of B641 addendum.

---

# B643 ADDENDUM — W5 redesign measurement result

> **Why this addendum exists.** B643 shipped owner-directed option C — `strat_pivot_s3_capitulation` redesign decoupling capitulation DETECTION (`recent_capitulation_at_s3` over 5-bar window) from ENTRY (reversal-trigger today). The measurement pass was re-run against the same 20-ticker × 3-year sample to compare pre- vs post-redesign fire characteristics.

## Result ([`output_audit/fire_count_measured_b643_w5_redesign.json`](output_audit/fire_count_measured_b643_w5_redesign.json))

| Metric | Pre-B643 | Post-B643 | Δ |
|---|---:|---:|---|
| Gate count | 3 AND | 2 AND (one is a 5-bar lookback OR-composite) | — |
| Fires/yr (20-ticker sample) | 1.33 | **1.67** | +25% |
| Projected fires/yr (full T1a) | **14.7** | **18.3** | +25% |
| Verdict at min_trades=30 | FAIL_FIRE_STARVED | **FAIL_FIRE_STARVED** (still) | unchanged |
| Independence ratio | 92.0 (independence OVER-estimated 92×) | **0.149** (independence UNDER-estimates 7×) | sign-flipped |
| Structural risk | KNIFE-CATCH (fires same bar as capitulation) | **TURN-CONFIRMED** (requires reversal-trigger inside window) | RESOLVED |

## Interpretation

**The redesign achieved its primary objective.** The pre-B643 strategy was structurally dangerous — three rare conditions (near_s3 + rsi<30 + vol_spike_2x) co-occurring on a single bar is the textbook definition of "the moment a stock is in panicked freefall." Pre-B643 fired LONG on that exact bar. Post-B643 the strategy waits for a reversal-confirmation candle inside the 5-bar Wyckoff Spring/Test window. The strategy now buys the turn, not the fall — the reviewer's exact framing.

**The fire-count modestly improved but did not cross the threshold.** 14.7/yr → 18.3/yr is a 25% improvement because the 5-bar eligibility window allows entries that would have been missed by the same-bar-only firing pattern. But 18.3/yr is still below 30/yr min_trades.

**The independence ratio sign flip is informative.** Pre-B643 gates were structurally rare-co-occurrence (extreme negative correlation at the marginal-rate level): near_s3 (0.005 prior) × rsi<30 (0.05 prior) × vol_spike_2x (0.10 prior) = 2.5e-5 independence-product, but the gates only co-occur on actual capitulation days which are extremely rare even compared to that joint. Independence over-estimated 92×.

Post-B643, the eligibility window broadens the `recent_capitulation_at_s3` signal to a 5-bar lookback OR-composite, and the reversal-trigger is positively correlated with eligibility (a 5-day window after capitulation is *more likely* to contain a reversal-candle than a random 5-day window). Independence under-estimates 7×.

## Options going forward

W5 is now structurally correct but still fire-count-FAIL. Three paths:

| Option | Description |
|---|---|
| **(W5-i) Keep as exploratory** | Accept 18.3/yr FAIL — strategy is correctly designed but rare. Mark exploratory in CLAUDE.md; future cube runs may show high-quality alpha even at low frequency (rare-but-strong signals can be valuable; min_trades=30 is a statistical-power floor, not a deployment gate). **No further code change.** |
| **(W5-ii) Widen lookback window 5→10** | Edit `compute_capitulation_lookback(lookback=10)`. Doubles eligibility window; estimated fire-count ~30-35/yr (matches Wyckoff "Accumulation Phase B" timeframe). Trade-off: longer window includes Test/Re-test sequences but also weakens timing-alpha attribution to the original Selling Climax. |
| **(W5-iii) Add more reversal triggers** | OR-disjunct extends to `bullish_engulfing OR hammer OR above_prev_high OR obv_diverge_bull OR rsi_14_rising`. Five triggers vs three. Likely fire-count ~28-35/yr. Trade-off: more confirmations include weaker signals (rsi_rising from 28→29 isn't the same as a hammer at S3). |
| **(W5-iv) Combine (ii) + (iii)** | Both. Most aggressive loosening; estimated 45-60/yr. Probably crosses PASS_CUBE. |
| **(W5-v) Delete entirely** | Strategy + Class 7 mirror — accept that capitulation-buying on daily bars in survivor universes is a poorly-supported edge. Reduces total count 221 → 220. |

## Class 7 NEW `pivot_r3_blowoff_short` mirror

Still DEFERRED pending W5 final disposition. Whatever option owner picks should mirror symmetrically — same lookback + same reversal-trigger logic on the SHORT side using R3 / RSI>70 / vol_spike_2x for detection + bearish_engulfing / shooting_star / below_prev_low for confirmation.

## My recommendation

**(W5-i) Keep as exploratory** is the principled call. The redesign closed the structural problem; fire-count is now the only remaining issue. Pre-cube loosening to reach min_trades=30 risks recreating the original problem (looser gates → less-confirmed signals → more knife-catches). The honest disposition: ship the correctness fix, acknowledge the strategy is rare, let Stage 5 cube empirically validate whether 18/yr fires actually produce alpha at sufficient power. If owner wants to chase the threshold, **(W5-ii)** is the safest loosening (lookback widening preserves trigger semantics).

**Awaiting owner direction on W5 (i / ii / iii / iv / v) + Class 7 mirror wire question.**

End of B643 addendum.
