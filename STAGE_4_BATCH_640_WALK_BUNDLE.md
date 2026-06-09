# Stage 4 Walk Bundle — Batch 640 (2026-06-09)

> **What this document is.** A comprehensive, beginner-friendly walk through 10 trading strategies in the Stage 4 review queue. For each strategy I (Claude) inspect the actual code line by line, trace every signal back to the producer that creates it, check for bugs and thesis mismatches, and surface concrete options for you to approve. Read this end-to-end, then jump to "[Owner decision form](#owner-decision-form)" at the bottom to indicate which option you want per strategy.
>
> **Audience.** Assumes ZERO prior knowledge of this codebase, of Python, or of the underlying market technicals. Every term is defined the first time it appears. Every threshold value (every number) is explained.
>
> **Scope.** 10 strategies — 2 to close out the candle-pattern cluster, then 8 to start the pivot-cluster walks. This replaces what would have been 10 individual one-strategy-per-turn walks at the prior cadence.
>
> **Source of truth.** I read this directly from the current state of `backtest/signals/screener.py`, `backtest/signals/technical.py`, and `backtest/engine/regime_selector.py` at commit `9ed4d9833`. Line numbers cited inline are clickable in the VS Code preview.

---

## Table of contents

1. [How to read this document](#how-to-read-this-document)
2. [Foundations — every term defined once](#foundations)
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

### Regime affinity — `STRATEGY_REGIME_AFFINITY`

Every day the engine classifies the market into one of four **regimes**: `bull`, `neutral`, `bear`, `crisis`. The dict `STRATEGY_REGIME_AFFINITY` in [`regime_selector.py`](backtest/engine/regime_selector.py) maps strategy name → set of regimes the strategy is *allowed* to fire in.

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

---

## Bundled action items

If you approve a batch of these, my proposed implementation order:

### Tier 1 — definite fixes (no judgment needed):
- **W8 F1+F1b** — silent-gap positive symmetric swap (existing memory directive)
- **W3 F3** — B271 family-bug delete (same pattern as 5 prior walks)
- **W4 F3** — B271 family-bug delete

### Tier 2 — docstring adds (low risk):
- **W1, W3, W4, W5, W10** — F2 docstring additions

### Tier 3 — judgment calls (need owner verdict):
- **W5 F-missing-inverse** — wire Class 7 NEW `strat_pivot_r3_blowoff_short`? Owner-yes-or-no.
- **W4 F1** — add `shooting_star` to SHORT OR-disjunct? Symmetric producer fix.
- **W6 F1 LATENT** — fix AVWAP asymmetric default? Two sub-options (strict default-False vs loosen-to-OR).
- **W7** — defer everything?
- **W2 fire-count** — defer or loosen?
- **W6 / W7 / W8** — fire-count stack-of-5-gates problem; flag for B603 standing concern.

### Tier 4 — no action:
- **W9** — already deferred to R5

---

## Owner decision form

Indicate per strategy. Quick-pick possibilities:

**W1 `bullish_engulfing_support`:** (A) F2 + commentary fix [RECOMMENDED]  /  (B) status quo
**W2 `shooting_star_short`:** (A) F2 only  /  (B) F2 + loosen RSI>60  /  (C) add Class 7 inverse  /  (D) F2 + Stage 5 deferral [RECOMMENDED]  /  (E) status quo
**W3 `pivot_s1_bounce`:** (A) F2 only  /  (B) F2 + F3 delete entry [RECOMMENDED]  /  (C) F2 + split affinity  /  (D) status quo
**W4 `pivot_s2_bounce`:** (A) F2 only  /  (B) F2 + F3 delete + F1 shooting_star  /  (C) F2 + F3 delete + F1 + B603 flag [RECOMMENDED]  /  (D) status quo
**W5 `pivot_s3_capitulation`:** (A) F2 only  /  (B) F2 + Class 7 inverse  /  (C) F2 + loosen rsi  /  (D) F2 + Class 7 + Stage 5 deferral [RECOMMENDED]  /  (E) status quo
**W6 `pivot_r1_breakout`:** (A) status quo  /  (B) F1 default-False symmetric  /  (C) F1 + loosen AVWAP to OR + B603 flag [RECOMMENDED]  /  (D) Stage 5 deferral
**W7 `pivot_r2_continuation`:** (A) status quo  /  (B) F1 default-False symmetric  /  (C) F1 + drop ADX  /  (D) Stage 5 deferral [RECOMMENDED]
**W8 `cpr_narrow_bullish`:** (A) status quo  /  (B) F1+F1b positive symmetric swaps [RECOMMENDED]  /  (C) B + drop cpr_narrow  /  (D) Stage 5 deferral
**W9 `camarilla_s3_bounce`:** (E) no action — deferred per R5 ticket [RECOMMENDED]
**W10 `camarilla_r3_breakout`:** (A) F2 docstring [RECOMMENDED]  /  (B) status quo

---

### Format for your reply

Easiest: **just type the option letters in order**, e.g.:

```
A D B C D C D B E A
```

Or a per-strategy override:

```
W1=A W2=D W3=B W4=C W5=D W6=C W7=D W8=B W9=E W10=A
```

I'll then ship as B640 batch — one commit per Tier (T1 first since unambiguous, then T2 docs, then T3 judgment items, T4 skipped).

End-of-bundle. Awaiting decisions.
