# Stage 4 SMC (Smart Money Concepts) Pure Price-Action Cluster Walks — Per-Strategy Deep-Dive Audit

> **B673 status banner (2026-06-10, owner-approved cluster-walk launch):** owner directive *"create comprehensive walk doc for the next cluster"* + AskUserQuestion answer **"SMC pure price-action (12)"**. This is the FOURTH per-cluster Stage 4 walk doc following the pivot + trend + smart-money cluster doc precedents. The owner explicitly distinguished SMC pure price-action from the data-source smart-money cluster just completed in B672 (B672j commit `ad72c1e6a`).
>
> **Scope correction:** the AskUserQuestion option labeled "SMC pure price-action (12)" actually maps to **18 strategies** in the `smc` category per `STRATEGY_ROSTER.md` lines 169-186 + `len([f for f in dir(screener) if f.startswith("strat_smc_")]) = 18`. The "12" was a stale count derived from incomplete grep. This doc covers all 18 SMC strategies + structural reference to 2 Layer 2D ICT strategies (`strat_turtle_soup_long` + `strat_turtle_soup_short`) that share producer semantics with SMC but live in a separate category. **Total in-scope: 18 SMC + 2 ICT-Turtle-Soup = 20 strategies referenced; 18 with full walks.**
>
> **No prior cluster walk on these strategies.** Roster shows 5 with `Y (B570)` reviewed status — but B570 was the "Stage 4 owner-decision tool + first 7 Class-6 Defer flips" batch (commit `5444bb815`), which applied owner-decision tooling to set status flags (Deferred / Approved / etc.) WITHOUT running the per-strategy 7-step deep-dive walk per CHECKLIST #105. All 18 SMC strategies receive their FIRST CHECKLIST #105 walk in this doc.
>
> **Source of truth.** Code references reflect current state at commit `780e7b150` (post-B672 EXECUTION_QUEUE update). Producer: [backtest/signals/smc_ict.py](backtest/signals/smc_ict.py); strategies: [backtest/signals/screener.py:3208-3543](backtest/signals/screener.py#L3208-L3543).

> **Foundational sequence (carried from B665 commitment + reaffirmed B672):** B660 measured-fire-count run still in flight on laptop (PID 9988; ~25% complete; ETA ~5hr); B668 cube replay with `cube_compose_verdict.csv` populated awaiting B660 land; B669 survivorship execution awaiting B660 land. **All fires/yr projections in this doc are PENDING B660** per the same discipline applied to smart-money cluster doc — projections from independence-product math are diagnostic-only NOT measured. Per `feedback_no_rushing_per_strategy_tweak`: each walk surfaces options + WAITS for owner direction; no auto-action.

---

## Audience

Two:

1. **External reviewer** who issued the adversarial audits on the pivot + smart-money clusters. For you: the SMC cluster is materially different from both prior clusters because (a) signals are **PURE PRICE-ACTION** computed from OHLCV alone (no alt-data dependency), (b) the producer is a **VENDORED THIRD-PARTY LIBRARY** (joshyattridge/smartmoneyconcepts under DEC-508 Phase A) — single-point-of-failure for all 18 strategies, (c) most SMC primitives have a structural **DETECTION LAG of 20-80 bars** due to swing-confirmation requirement (Batch 273 fix); the `event_recency_bars=90` parameter controls fire-frequency-vs-staleness tradeoff and is a hidden tunable, (d) the underlying ICT methodology has **NO PEER-REVIEWED LITERATURE** — it's a YouTube-era trading framework with one unaudited Quantum Algo Mar 2026 backtest (61% WR / 2.17 PF / +2.27R on 10-asset 2,600-trade 26-month sample), (e) most strategies have **inherent multi-test exposure**: BOS continuation + BOS retest + CHOCH reversal + OB bounce + FVG retest all measure overlapping "institutional re-entry to recently-imbalanced zone" semantics. The walk methodology adapts to these differences — see [Methodology adaptations for SMC cluster](#methodology-adaptations-for-smc-cluster) section.

2. **Future readers** (owner, Claude in later sessions, new collaborators). The [Cluster scope inventory](#cluster-scope-inventory) is your orientation; per-strategy walks below.

---

## Methodology adaptations for SMC cluster

### 1. Vendored library dependency — `joshyattridge/smartmoneyconcepts` under DEC-508 Phase A

All 18 strategies depend on a single vendored library (`vendored/smartmoneyconcepts/smartmoneyconcepts.py`) imported into [backtest/signals/smc_ict.py:39-48](backtest/signals/smc_ict.py#L39-L48):

```python
with contextlib.redirect_stdout(io.StringIO()):
    try:
        from vendored.smartmoneyconcepts.smartmoneyconcepts import smc as _smc
        _SMC_AVAILABLE = True
    except Exception as _e:
        log_silent_failure("smc_ict.import_smartmoneyconcepts", _e)
        _smc = None
        _SMC_AVAILABLE = False
```

**Failure mode:** if the library import fails (version bump, environment delta, dependency conflict), `_SMC_AVAILABLE=False` and `compute_smc_signals` returns `{}`. All 18 strategies degrade together to "no signal → no fire." Step 5 OPEN_INVESTIGATIONS grep must check that B458 silent-failure logging is wired (✅ confirmed at line 46).

**Cross-strategy implication:** unlike the smart-money cluster where 41 strategies span 5 producers (13F + 13D + insider Form 4 + congressional + classification), SMC has 18 strategies sharing ONE producer. A library bug affects all 18 simultaneously. Per `feedback_walk_step3_must_read_producer_source`: the library source itself must be in scope for the walk; not just `smc_ict.py`'s wrapper.

### 2. Detection-lag dependency — `event_recency_bars=90` hidden tunable

Per Batch 273 fix documented at [smc_ict.py:51-72](backtest/signals/smc_ict.py#L51-L72):

> *"SMC library has intrinsic detection lag from swing-confirmation requirement. Using tail(N) for 'recently active' base signals (BOS/CHOCH/OB/liquidity) misses events because detection happens 20-80 bars after the event itself. This helper finds the last non-zero event by index and checks recency relative to current_idx instead of relative to the tail. Per empirical sweep on AAPL (1255 bars, swing_length=20): a 90-bar recency window catches the most-recent BOS in ~30% of days (vs ~0% with a 5-bar tail)."*

**The 90-bar `event_recency_bars` parameter is a free tuning knob with material alpha impact.** Increase → more fires + more staleness; decrease → fewer fires + fresher events but lower min_trades risk. Currently HARDCODED in [smc_ict.py:81](backtest/signals/smc_ict.py#L81) as the default `event_recency_bars=90`. Affects:
- `smc_bos_bullish` / `smc_bos_bearish`
- `smc_choch_bullish` / `smc_choch_bearish`
- `smc_ob_bullish_active` / `smc_ob_bearish_active`
- `smc_liquidity_swept_up` / `smc_liquidity_swept_dn`

NOT affected (use a different recency window or no decay):
- `smc_fvg_bullish_active` / `smc_fvg_bearish_active` — use `fvg_lookback=5` tail (FVG events are denser per producer comment line 168-171)
- `smc_*_retest_*_zone` — point-in-time price-in-zone check; no decay
- `smc_inverse_fvg_*` — point-in-time mitigated-and-flipped check; no decay
- `smc_dealing_range_pct` + `smc_in_discount_zone` + `smc_in_premium_zone` — uses `dealing_range_lookback=50`

**Step 7 should ALWAYS flag whether the strategy consumes `event_recency_bars`-bearing signals.** If yes, fire-count sensitivity to the 90-bar default is non-trivial.

### 3. PIT integrity — multiple producer-side fixes (B273 + B390 + B555 + B556)

The SMC producer has been bug-fixed multiple times for sparse-event slicing failures:
- **B273**: `_most_recent_event_within` helper added (BOS/CHOCH/OB/liquidity sparse-event lag)
- **B390**: `liquidity` events filter-then-tail (was missing 100% of sweeps pre-fix)
- **B555**: OPT-C SMC panel cache layer (must produce identical results to per-call compute; PIT integrity verified via separate test)
- **B556**: FVG + OB filter-then-tail consistency with B390 liquidity fix

Each walk's Step 3 must confirm the producer code path is the post-fix version + Step 5 grep OPEN_INVESTIGATIONS for any active producer-side concerns.

### 4. Bar-of-fire EVENT vs continuous STATE — SMC-specific temporality

Unlike the smart-money cluster where Pattern B (STATE-as-EVENT) was the dominant concern, SMC signals span the EVENT/STATE spectrum on a different axis:

| Signal class | Temporality | Lag profile | Step 7 concern |
|---|---|---|---|
| **Point-in-time zone-active** (FVG retest, OB mitigation, dealing range, OTE) | EVENT-shaped boundary | 0-day | Lookahead risk in zone-definition (see §5 dealing_range_lookback) |
| **Recency-windowed event** (BOS, CHOCH, OB active, liquidity sweep) | **STATE**-as-EVENT-with-90-bar-decay | 20-80 bar detection lag + up to 90-bar recency window | Pattern I detection-lag dependency |
| **Confluence composition** (CHOCH + FVG, BOS + retest near, liquidity-sweep + CHOCH/BOS) | Variable | Depends on the most-lagging component | Pattern N internal overlap |

Per CHECKLIST (s): the recency-windowed events ARE EVENT-class for purposes of "did something happen at bar of fire" but DEGRADE on the staleness axis as the window approaches its 90-bar tail. Strategies using these as the primary trigger must accept this degradation OR add a fresher confirmation gate (vol_spike_2x + RSI direction, B262/B278 pattern).

### 5. Lookahead risk class — `dealing_range_lookback=50` shares the S4-FIB-ANCHOR-LOOKAHEAD-AUDIT pattern

Per [smc_ict.py:406-418](backtest/signals/smc_ict.py#L406-L418):

```python
if len(ohlc) >= dealing_range_lookback:
    window = ohlc.tail(dealing_range_lookback)
    hi = float(window["high"].max())
    lo = float(window["low"].min())
```

The `dealing_range_lookback=50` parameter selects the high/low anchors over the trailing 50 bars. **If `ohlc` is ever passed with bars beyond `as_of`, the dealing-range anchors peek into the future** — identical lookahead-vector class as `compute_fibonacci` per `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT` (EXECUTION_QUEUE.md ticket). Engine slicing convention is `df[df.index.date <= as_of]` BUT no explicit test asserts the SMC variant. Step 7 of `strat_smc_discount_long` + `strat_smc_premium_short` MUST surface this.

### 6. ICT methodology has no peer-reviewed academic support

Unlike the smart-money cluster which had Cohen-Malloy-Pomorski 2012, Cohen-Frazzini-Malloy 2008, Yan-Zhang 2009, Akbas-Jiang-Koch 2024 RFS citations (all peer-reviewed JF/JFE/RFS), the ICT/SMC framework is a **YouTube-era trading methodology** with no peer-reviewed publications:
- **Inner Circle Trader** = Michael J. Huddleston (pseudonym) — 2007+ trading-room methodology; no journal publications
- **Smart Money Concepts** = community-coined umbrella for ICT-derived concepts
- **Joshyattridge/smartmoneyconcepts library** = open-source community implementation; not peer-validated
- **Quantum Algo Mar 2026 backtest** = unaudited YouTube channel backtest (10 assets / 2,600 trades / 26 months); cited in `compute_smc_signals` docstring lines 19-22 as empirical backing BUT (i) NOT independent of the library author's frame, (ii) NOT validated against survivorship (left-tail likely deleted), (iii) NOT validated against multi-testing correction (the 18 strategies + 5 exits = 90 cells over 26 months is heavily over-fitted in a 2,600-trade sample).

**Step 4 doc-vs-thesis MUST flag the citation void.** Honest framing per `feedback_signal_temporality_event_vs_state` + `feedback_avwap_redundant_with_ema_trend_filter` distinct-failure-mode tests: SMC strategies are *plausible* per the methodology's internal logic but lack the academic-evidence anchor that the smart-money cluster's CMP / CFM citations supplied. Cube replay + Bailey-LdP deflated Sharpe + Hansen SPA + BH-FDR (per `backtest/engine/multiple_testing_correction.py` B667 + B668) is the ONLY path to empirical adjudication.

### 7. Internal multi-test exposure — 18 strategies on ~7 primitives

The 18 SMC strategies consume only 6 primitive boolean signals from the producer (FVG / OB / BOS / CHOCH / liquidity / dealing-range) + 2 derived (retest zone, mitigated-flip). **Combinatorially, the 18 strategies are dense compositions of those 7-ish primitives** — the joint information set is meaningfully smaller than 18 × independent signal stacks would suggest. This creates internal multi-test inflation EVEN BEFORE adding the cluster's cells to the broader 222-strategy family. Specifically:

- **6 dual strategies via `_strat3()`** (inverse_fvg, bos_continuation, choch_reversal, bos_retest_entry, order_block_bounce, liquidity_sweep_reversal) → 12 (strategy × direction) cells from 6 functions
- **12 single-direction strategies** (smc_fvg_retest_long, smc_fvg_retest_short, smc_breaker_block_long, smc_breaker_block_short, smc_mitigation_block_long, smc_mitigation_block_short, smc_discount_long, smc_premium_short, smc_ote_long, smc_ote_short, smc_equal_highs_sweep_short, smc_equal_lows_sweep_long)

→ **24 (strategy × direction) cells from 18 functions ON 7 primitives = ~3.4× density per primitive.** Step 7 of every walk must surface the Pattern N (internal multi-test) concern + the post-cube branch-stratified ablation that would settle which compositions earn independent registry slots.

---

## Reviewer findings response matrix

> Pre-emptive matrix awaiting external reviewer critique. After this doc's first read by the reviewer, findings will be tabulated here following the smart-money cluster precedent.

| # | Finding | Severity | Status | Action |
|---|---|---|---|---|
| _F-pending_ | Awaiting external reviewer pass on the SMC walk | — | OPEN | Will be tabulated post-review |

---

## Cluster scope inventory

**18 SMC strategies + 2 referenced ICT-Turtle-Soup (`turtle_soup_long` + `turtle_soup_short` in `chart_pattern` category, not walked here).** The 18 SMC strategies group into 6 sub-clusters by underlying ICT/SMC primitive:

| Sub-cluster | # strategies | Strategies |
|---|---|---|
| **A — Fair Value Gap (FVG) family** | 3 | SMC-1 `smc_fvg_retest_long` / SMC-2 `smc_fvg_retest_short` / SMC-3 `smc_inverse_fvg` (dual) |
| **B — Order Block (OB) family** | 4 | SMC-4 `smc_breaker_block_short` / SMC-5 `smc_breaker_block_long` / SMC-6 `smc_mitigation_block_long` / SMC-7 `smc_mitigation_block_short` |
| **C — Dealing range (premium/discount) family** | 2 | SMC-8 `smc_discount_long` / SMC-9 `smc_premium_short` |
| **D — Optimal Trade Entry (OTE) family** | 2 | SMC-10 `smc_ote_long` / SMC-11 `smc_ote_short` |
| **E — Liquidity sweep family** | 3 | SMC-12 `smc_equal_highs_sweep_short` / SMC-13 `smc_equal_lows_sweep_long` / SMC-18 `smc_liquidity_sweep_reversal` (dual) |
| **F — BOS / CHOCH structural family** | 4 | SMC-14 `smc_bos_retest_entry` (dual) / SMC-15 `smc_bos_continuation` (dual) / SMC-16 `smc_choch_reversal` (dual) / SMC-17 `smc_order_block_bounce` (dual) |

**Note on numbering:** SMC-N numbers run 1-18 in the order strategies are defined in screener.py for consistency with code-reading order. Sub-cluster grouping above is logical; not strictly contiguous.

**Cross-cluster overlap:** none with smart-money cluster (which is data-source-derived); 2 referenced strategies share PRODUCER (`strat_turtle_soup_long` / `_short` in chart_pattern category use the same `smc_liquidity_swept_*` signals but live in a separate category per B580 Layer 2D ICT inline-spec wiring). Per `feedback_strategy_roster_doc_maintenance`: STRATEGY_ROSTER.md is the single source of truth; this doc cross-refs but doesn't re-declare counts.

---

## Cross-strategy patterns (Pattern I-Q new for SMC cluster + Patterns A/F/G carried from prior clusters)

### Pattern I — Detection-LAG dependency on `event_recency_bars=90` hidden tunable (NEW for SMC)

**Affects:** 12 of 18 strategies that consume recency-windowed events (BOS, CHOCH, OB-active, liquidity-sweep). Specifically: SMC-3 (inverse_fvg) ✘ (uses point-in-time mitigated check, not recency), SMC-4/5 (breaker_block; uses point-in-time mitigated-flip), SMC-6/7 (mitigation_block; uses point-in-time in-zone), SMC-12/13 (equal_*_swept; uses `Swept` flag with 50-bar recency), SMC-14 (bos_retest_entry; uses 0.5% near-test on BOS Level over last 20 BOS events), SMC-15 (bos_continuation; consumes `smc_bos_bullish` from 90-bar recency), SMC-16 (choch_reversal; consumes `smc_choch_bullish` from 90-bar recency), SMC-17 (order_block_bounce; consumes `smc_ob_bullish_active` from 90-bar recency), SMC-18 (liquidity_sweep_reversal; consumes `smc_liquidity_swept_*` from 90-bar recency).

**Concern:** 90-bar window = ~4 months. A "BOS bullish" signal can fire 4 months after the actual structural break — by which time the structural backdrop may have changed entirely. Strategies that AND a "fresh" confirmation (B262 inverse_fvg + B278 bos_continuation pattern: `vol_spike_2x OR force_index_breakout`) mitigate the staleness; strategies without a freshness gate carry full staleness exposure.

**Step 7 disposition:** every walk consuming recency-windowed events must surface (a) which freshness gate (if any) mitigates staleness; (b) post-B660 sensitivity test of fire-count vs. tighter recency windows (e.g., 30 / 45 / 90 sweep); (c) candidate Class 2 LOOSEN/TIGHTEN of `event_recency_bars` as a free parameter cube can adjudicate.

### Pattern J — FVG / OB / BOS / CHOCH semantic overlap (NEW for SMC)

**Affects:** all 18 strategies. The 6 primitive signals (FVG, OB, BOS, CHOCH, liquidity, dealing-range) all measure variations of **"institutional re-entry to a recently-imbalanced zone"**:

- FVG = 3-bar imbalance (price gap)
- OB = last opposing candle before impulse (institutional accumulation/distribution zone)
- BOS = break of prior structural high/low (continuation event)
- CHOCH = first break of structure against prior trend (reversal event)
- Liquidity sweep = price takes out stops above/below equal-highs/lows (stop-hunt event)

These are NOT independent signals — they are different angular projections of the same underlying "where did institutions act" question. Cube replay must apply marginal-contribution scoring per `S5-MARGINAL-CONTRIBUTION-SCORING` C3 ticket: scoring each strategy as `book_with_X.sharpe - book_without_X.sharpe` rather than standalone Sharpe.

**Step 7 disposition:** every walk consuming 2+ primitives must surface Pattern J marginal-contribution concern. Cross-ref `S5-MARGINAL-CONTRIBUTION-SCORING` + this cluster as the highest-leverage application beyond the smart-money 13F sleeve test (`S5-13F-SLEEVE-MARGINAL-CONTRIBUTION-TEST`).

### Pattern K — `dealing_range_lookback=50` lookahead-vector class (NEW for SMC)

**Affects:** 2 strategies — SMC-8 `smc_discount_long` + SMC-9 `smc_premium_short` (both consume `smc_in_discount_zone` / `smc_in_premium_zone`).

**Concern:** identical lookahead-vector class as `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT` for `compute_fibonacci`. The 50-bar trailing dealing-range max/min selects high/low anchors from a window that MUST be PIT-sliced before passing to the producer. Engine convention is `df[df.index.date <= as_of]` but no explicit test pins SMC-8/9 against future-data peeking.

**Step 7 disposition:** SMC-8 + SMC-9 walks queue a producer-PIT test ticket symmetric with `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT`. Low-confidence-but-no-test class; producer is most likely correct given engine convention but verification is cheap.

### Pattern L — Vendored library single-point-of-failure (NEW for SMC)

**Affects:** all 18 strategies.

**Concern:** library import failure → `_SMC_AVAILABLE=False` → all 18 strategies degrade to no-fire simultaneously. B458 silent-failure logging is wired (✅ confirmed at `smc_ict.py:46`) but the silent-fail mode produces a "no-signal → no-fire" pattern that mimics "no opportunity" in cube outputs. Distinguishable from genuine no-opportunity only via the silent_failure log + sentinel-test runs.

**Step 5 OPEN_INVESTIGATIONS** must confirm B458 logging is still active + the library version is pinned. Step 7 disposition: queue a periodic library-version-sentinel check (low-priority but cheap).

### Pattern M — Backtest provenance unaudited (NEW for SMC)

**Affects:** all 18 strategies (cited in producer docstring lines 19-22).

**Concern:** Quantum Algo Mar 2026 backtest cited as empirical backing (61% WR / 2.17 PF / +2.27R on 10 assets / 2,600 trades / 26 months) is (i) NOT independent of the library author's frame, (ii) NOT survivorship-validated (left-tail likely deleted), (iii) NOT multi-testing-corrected (18 strategies × ~5 exits = 90 cells on 2,600 trades = severely under-powered), (iv) NOT cited in any peer-reviewed publication, (v) sample is a 10-asset universe (vs our T1a 503 names). Treating this as evidence of expected alpha is overclaim per `feedback_signal_temporality_event_vs_state` doc-vs-thesis discipline.

**Step 4 doc-vs-thesis** of every walk should flag the Quantum Algo citation when present. Honest reframe: "Quantum Algo Mar 2026 reports 61% WR / 2.17 PF on a 10-asset sample; our cube replay against T1a 503 names + multi-testing correction is the ONLY adjudication path."

### Pattern N — Internal multi-test inflation (NEW for SMC; carry-over from §7 methodology adaptation)

**Affects:** all 18 strategies. 24 (strategy × direction) cells on ~7 primitives.

**Concern:** Cluster-internal Bonferroni / FDR inflation is materially higher than the per-strategy walk's Pattern F (cross-cluster) concern. The SMC cluster alone is a 24-cell × 26-exit ~624-cell subset of the broader cube; if all 18 strategies share 7 primitives, the effective independent test count is closer to 7-14 than 18.

**Step 7 disposition:** cube replay with multi-testing correction (B667 + B668 already shipped) handles this at the program level via `cube_select_with_multiple_testing()`. But intra-cluster collinearity ablation (which compositions earn registry slots after correction) is a CLUSTER-SCOPED test beyond C2 — queued as new ticket post-walk.

### Pattern O — Hardcoded tolerance constants (NEW for SMC)

**Affects:** 3 strategies depending on hardcoded thresholds in producer:
- SMC-14 `smc_bos_retest_entry` consumes `smc_bos_retest_*` produced with `tol = 0.005` (0.5%) hard-coded at [smc_ict.py:310](backtest/signals/smc_ict.py#L310)
- SMC-12 / SMC-13 `smc_equal_*_swept` consume `liquidity_range_pct=0.01` (1%) hard-coded as the equal-level cluster tolerance
- SMC-8 / SMC-9 / SMC-3 / SMC-15 / SMC-16 / SMC-17 / SMC-18 consume `event_recency_bars=90` (Pattern I) and `dealing_range_lookback=50` (Pattern K)

**Concern:** these tolerances are free parameters with no empirical basis cited; they should be either (a) config-driven (in `backtest/config.py`) so cube can sweep, (b) documented as DELIBERATE methodology choice with cited rationale, or (c) sensitivity-tested post-B660 to confirm they're not artifacts.

**Step 7 disposition:** queue a producer-side config-parameterization ticket post-B660 measured-fire-count baselines.

### Pattern A (carried from prior clusters) — `price_above_ema_200` / `below_ema_200` default handling

**Status:** ✅ already SWEPT per B663 + B630. All 18 strategies use either `s.get("price_above_ema_200", False)` (B663 fixed default-True → False) or `s.get("below_ema_200", False)` (B630 producer-additive positive symmetric). Verified via grep of screener.py SMC functions: 0 remaining default-True instances.

**Step 1 confirmation:** each walk should note "Pattern A confirmed FIXED" + commit reference.

### Pattern F (cross-cluster, carried from smart-money) — marginal-contribution audit

**Status:** Pattern J above (FVG/OB/BOS overlap) is the SMC-specific specialization of cross-cluster Pattern F. Cross-ref `S5-MARGINAL-CONTRIBUTION-SCORING` + `S5-13F-SLEEVE-MARGINAL-CONTRIBUTION-TEST` (smart-money) + this cluster's intra-cluster collinearity test (Pattern N) as 3 applications of the same methodology.

### Pattern G (cross-cluster, carried from smart-money) — low-fire-combo EXPLORATORY

**Status:** several SMC strategies project low fires/yr due to Pattern I detection-LAG + Pattern J overlapping primitives (specifically SMC-12 + SMC-13 equal-highs/lows sweep family + the BOS+FVG/OB+RSI confluence strategies). Cross-ref `S4-LOW-FIRE-COMBO-EXPLORATORY-REVIEW-POST-B660` for the active ticket; SMC candidates added per walks below.

---

## Cluster current state table

| SMC # | Function name | Direction | Sub-cluster | Primary signal(s) | Confluence gates | B663/B630 ✓ | Pattern flags | Walk status |
|---|---|---|---|---|---|---|---|---|
| SMC-1 | `strat_smc_fvg_retest_long` | long | A FVG | `smc_fvg_retest_long_zone` | `price_above_ema_200` | ✅ | J | ⏳ Walked B673 |
| SMC-2 | `strat_smc_fvg_retest_short` | short | A FVG | `smc_fvg_retest_short_zone` | `below_ema_200` | ✅ | J | ⏳ Walked B673 |
| SMC-3 | `strat_smc_inverse_fvg` | dual | A FVG | `smc_inverse_fvg_bullish` / `_bearish` | `vol_confirms` (vol_spike_2x OR force_index_breakout) + 200-EMA | ✅ | B262 forensic-fixed; J + M | ⏳ Walked B673 |
| SMC-4 | `strat_smc_breaker_block_short` | short | B OB | `smc_breaker_block_bearish` | `below_ema_200` | ✅ | I + J | ⏳ Walked B673 |
| SMC-5 | `strat_smc_breaker_block_long` | long | B OB | `smc_breaker_block_bullish` | `price_above_ema_200` | ✅ | I + J | ⏳ Walked B673 |
| SMC-6 | `strat_smc_mitigation_block_long` | long | B OB | `smc_mitigation_block_long` | `price_above_ema_200` + `rsi_14<50` | ✅ | I + J | ⏳ Walked B673 |
| SMC-7 | `strat_smc_mitigation_block_short` | short | B OB | `smc_mitigation_block_short` | `below_ema_200` + `rsi_14>50` | ✅ | I + J | ⏳ Walked B673 |
| SMC-8 | `strat_smc_discount_long` | long | C dealing range | `smc_in_discount_zone` + (`smc_bos_bullish` OR `smc_choch_bullish`) | `price_above_ema_200` | ✅ | I + J + K | ⏳ Walked B673 |
| SMC-9 | `strat_smc_premium_short` | short | C dealing range | `smc_in_premium_zone` + (`smc_bos_bearish` OR `smc_choch_bearish`) | `below_ema_200` | ✅ | I + J + K | ⏳ Walked B673 |
| SMC-10 | `strat_smc_ote_long` | long | D OTE | `smc_ote_long_zone` + (`smc_bos_bullish` OR `smc_choch_bullish`) | (none — no EMA gate) | ✅ N/A | I + J + missing-trend-filter | ⏳ Walked B673 |
| SMC-11 | `strat_smc_ote_short` | short | D OTE | `smc_ote_short_zone` + (`smc_bos_bearish` OR `smc_choch_bearish`) | (none — no EMA gate) | ✅ N/A | I + J + missing-trend-filter | ⏳ Walked B673 |
| SMC-12 | `strat_smc_equal_highs_sweep_short` | short | E liquidity | `smc_equal_highs_swept` + `smc_fvg_bearish_active` | (none — no EMA gate) | ✅ N/A | I + J + missing-trend-filter + G fire-starve | ⏳ Walked B673 |
| SMC-13 | `strat_smc_equal_lows_sweep_long` | long | E liquidity | `smc_equal_lows_swept` + `smc_fvg_bullish_active` | (none — no EMA gate) | ✅ N/A | I + J + missing-trend-filter + G fire-starve | ⏳ Walked B673 |
| SMC-14 | `strat_smc_bos_retest_entry` | dual | F structural | `smc_bos_retest_long` / `smc_bos_retest_short` | EMA-200 | ✅ | I + J + O | ⏳ Walked B673 |
| SMC-15 | `strat_smc_bos_continuation` | dual | F structural | `smc_bos_bullish` / `smc_bos_bearish` | `vol_confirms` + RSI direction + EMA-200 | ✅ | B278 post-forensic gates; I + J | ⏳ Walked B673 |
| SMC-16 | `strat_smc_choch_reversal` | dual | F structural | `smc_choch_bullish` + `smc_fvg_bullish_active` (LONG); symmetric SHORT | (no EMA gate; FVG-confluence only) | ✅ N/A | I + J + missing-trend-filter | ⏳ Walked B673 |
| SMC-17 | `strat_smc_order_block_bounce` | dual | F structural | `smc_ob_bullish_active` + `rsi_14<45`; symmetric SHORT | EMA-200 | ✅ | I + J | ⏳ Walked B673 |
| SMC-18 | `strat_smc_liquidity_sweep_reversal` | dual | E liquidity | `smc_liquidity_swept_*` + (`smc_choch_*` OR `smc_bos_*`) | (no EMA gate; CHOCH/BOS confluence only) | ✅ N/A | I + J + missing-trend-filter | ⏳ Walked B673 |

**Net cluster state:**
- 18 functions / 24 (strategy × direction) cells
- 12 with EMA-200 trend gate; 6 without (SMC-10, SMC-11, SMC-12, SMC-13, SMC-16, SMC-18 — all use BOS/CHOCH/FVG structural-confluence as the trend proxy)
- Pattern A (B663/B630): ✅ all 12 EMA-consumers verified post-sweep
- Pattern I (90-bar recency): 11 strategies affected
- Pattern J (primitive overlap): all 18 affected
- Pattern K (dealing_range lookahead): SMC-8 + SMC-9
- Pattern O (hard-coded tolerances): SMC-12, SMC-13, SMC-14 directly + producer-wide implicit

---

## Per-strategy walks

### SMC-1. `strat_smc_fvg_retest_long` (Batch 216, FVG family, walked B673)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate LONG; canonical ICT FVG-retest continuation entry.

#### Step 1 — Read the code

[screener.py:3208-3220](backtest/signals/screener.py#L3208-L3220):

```python
def strat_smc_fvg_retest_long(s):
    """Batch 216 (SMC expansion 2026-05-18 owner-approved): price returned
    to an unmitigated bullish Fair Value Gap zone -> long entry.
    FVG = institutional 3-bar imbalance; retests of bullish FVGs are
    canonical ICT continuation entries."""
    fires = (
        s.get("smc_fvg_retest_long_zone", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "smc",
        ["smc_fvg_retest_long_zone", "price_above_ema_200"],
        ["Price inside unmitigated bullish Fair Value Gap zone",
         "Above 200 EMA (regime gate)"])
```

**2-gate LONG strategy.** Simplest SMC walk in the cluster.

| Gate | Meaning |
|---|---|
| `smc_fvg_retest_long_zone` | EVENT-shaped boundary: today's close is INSIDE an unmitigated bullish FVG zone (3-bar imbalance where bar -2's high < bar 0's low); `MitigatedIndex` from library is 0/NaN/non-current |
| `price_above_ema_200` | Long-term uptrend; B663-fixed default False |

#### Step 2 — Classify

- Category: `smc`
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B663 (Pattern A WAVE 1 family sweep — confirmed `price_above_ema_200` default is False post-sweep per smc_ict.py grep)

#### Step 3 — Producer source-read + temporality

- `smc_fvg_retest_long_zone` is computed at [smc_ict.py:174-205](backtest/signals/smc_ict.py#L174-L205) via FVG primitive's `Top`/`Bottom`/`MitigatedIndex` columns. Logic: iterate last 20 ACTUAL FVG events (B556 filter-then-tail fix); for each, check `is_mitigated = (MitigatedIndex set AND < current_idx)` AND `in_zone = (close >= bot AND close <= top)`; if `not is_mitigated AND in_zone AND fvg_val == 1` → `retest_long = True`.
- Lag: 0-day (point-in-time zone-active check at bar of fire)
- `price_above_ema_200` STATE

**EVENT/STATE composition:** 1 EVENT-shaped (zone-active) + 1 STATE. ✅ Canonical cross-EVENT/STATE structure where the EVENT IS the timing trigger. NOT a Pattern B candidate.

**Pattern J concern:** the FVG primitive is correlated with OB primitive (both measure "institutional imbalance zone"); strategies SMC-1 + SMC-6 may surface high correlation in cube replay.

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "FVG = institutional 3-bar imbalance" | ✅ Producer implementation matches — `_smc.fvg(ohlc)` returns Top/Bottom of the 3-bar gap |
| "retests of bullish FVGs are canonical ICT continuation entries" | ⚠ **Pattern M** — canonical per ICT methodology BUT no peer-reviewed validation; cube-replay is the only adjudication path |
| Implicit "unmitigated FVG retest is high-probability entry" | ⚠ Quantum Algo Mar 2026 backtest cited cluster-wide but not specifically for FVG retest; per-component breakdown not in producer citation |

#### Step 5 — OPEN_INVESTIGATIONS grep

- No active investigations on SMC-1 specifically
- Producer-level: B556 filter-then-tail fix is the current state (no successor bug)
- Library-level: Pattern L vendored library SPOF concern applies generically

#### Step 6 — Missing-inverse + economic-symmetry

- **Inverse EXISTS** — SMC-2 `strat_smc_fvg_retest_short` is the symmetric mirror
- Economic symmetry: ✅ price-action signal; both directions equally valid per FVG semantics

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-J primitive overlap** | FVG retest + OB mitigation + OB bounce + breaker block all measure overlapping "institutional zone re-entry"; SMC-1 marginal contribution test needed | MEDIUM | Pattern J / S5-MARGINAL-CONTRIBUTION-SCORING |
| **F-pattern-M unaudited backtest** | Quantum Algo Mar 2026 cited cluster-wide; per-strategy contribution unknown until cube replay | MEDIUM | Pattern M |
| F-pattern-A | `price_above_ema_200` default False ✅ confirmed | ✅ SHIPPED B663 | — |
| F-fire-count | FVG retests are dense (~ every 5-15 bars per ticker per producer comment); projected fire count moderate-high; Step 7 expects PASS on min_trades=30 | INFO | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Add freshness gate symmetric with SMC-3 B262 fix — `vol_spike_2x OR force_index_breakout` to reduce stale-retest false positives |
| (c) Branch-stratified cube replay surfacing Pattern J overlap with SMC-6 (mitigation_block_long) + SMC-17 LONG (order_block_bounce) |
| **(d) RECOMMENDED — (c). Pattern J adjudication is the highest-leverage SMC ablation. Pre-cube no code change; the strategy is simple + structurally sound + already EMA-gated. (b) is a Class 2 LOOSEN/TIGHTEN candidate AFTER cube data settles whether SMC-1 carries distinct alpha from the OB family.** |

**My recommendation: (d).**

**Awaiting owner direction on SMC-1:**
1. (a)/(b)/(c)/(d) — recommendation (d)
2. Confirm Pattern J cube-replay ablation scope (which strategies to compare; SMC-1 vs SMC-6 + SMC-17 LONG is the minimum test)

---

### SMC-2. `strat_smc_fvg_retest_short` (Batch 216, FVG family, walked B673)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate SHORT; symmetric mirror of SMC-1.

#### Step 1 — Read the code

[screener.py:3223-3232](backtest/signals/screener.py#L3223-L3232):

```python
def strat_smc_fvg_retest_short(s):
    """Batch 216: bearish FVG retest -> short entry. Symmetric to long."""
    fires = (
        s.get("smc_fvg_retest_short_zone", False)
        and s.get("below_ema_200", False)  # B630 sweep
    )
    return _strat(fires, "short", "smc",
        ["smc_fvg_retest_short_zone", "price_below_ema_200"],
        ["Price inside unmitigated bearish Fair Value Gap zone",
         "Below 200 EMA (bear regime)"])
```

**2-gate SHORT strategy.** Symmetric mirror of SMC-1.

| Gate | Meaning |
|---|---|
| `smc_fvg_retest_short_zone` | EVENT-shaped boundary: close inside unmitigated bearish FVG (3-bar imbalance where bar -2's low > bar 0's high) |
| `below_ema_200` | Long-term downtrend; B630 producer-additive positive symmetric (NOT default-True NOT-pattern) |

#### Step 2-6 (compact — symmetric with SMC-1)

- Category `smc`; SHORT direction; B291 default; last touched B630/B663
- Producer: [smc_ict.py:174-205](backtest/signals/smc_ict.py#L174-L205) symmetric branch (`fvg_val == -1`)
- EVENT/STATE: 1 EVENT-shaped + 1 STATE; canonical structure
- Pattern A B630 producer-additive ✅
- Pattern J primitive-overlap same as SMC-1
- Inverse: SMC-1 (long mirror); economic-symmetry ✅ price-action
- **B671 centralized borrow-trap gate applies** via `_strat()` inspect-frame consult (added B671): when `direction == "short"` AND `_short_borrow_trap_active(s)`, fires forced to False

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-J primitive overlap (SHORT-side)** | Symmetric mirror's marginal contribution vs SMC-7 (mitigation_block_short) + SMC-17 SHORT (order_block_bounce_short) | MEDIUM | Pattern J |
| **F-borrow-cost asymmetry** | SHORT side carries borrow-cost burden that SMC-1 LONG doesn't; B671 centralized DTC > 8 gate applies pre-fire | LOW | F5 carryover |
| F-pattern-A | `below_ema_200` B630 producer-additive ✅ | ✅ SHIPPED B630 | — |
| F-fire-count | Bearish-FVG retests rarer than bullish (equity upward drift); projected ~60-70% of SMC-1 fire count; should still PASS min_trades=30 | INFO | F4 |

**Options:** (a) status quo / (b) freshness gate symmetric with SMC-3 / (c) cube-replay Pattern J + branch-stratify SHORT vs LONG asymmetry / **(d) RECOMMENDED — (c)**

**My recommendation: (d) bundled with SMC-1 disposition.**

**Awaiting owner direction on SMC-2:** same as SMC-1; bundled.

---

### SMC-3. `strat_smc_inverse_fvg` (Batch 216 + B262 forensic-fixed, FVG family, walked B673 — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **B262 FORENSIC-FIXED CASE** — original signal fired 478 trades (40% of all flow) with 24.7% WR = -1659pp = ~95% of aggregate loss in Phase 1A-alpha. B262 added regime gate + volume confirmation gates. Walk surfaces (a) is the post-fix design empirically validated, (b) does the cube vindicate the fix?

#### Step 1 — Read the code

[screener.py:3235-3269](backtest/signals/screener.py#L3235-L3269):

```python
def strat_smc_inverse_fvg(s):
    """Batch 216: Inverse FVG - bullish FVG was invalidated (price closed
    below) -> the zone flips role and acts as resistance (short).
    Symmetric for bearish FVG invalidated upward (long).
    ICT 'IFVG' concept: a failed institutional imbalance becomes the new
    opposing reference.

    Batch 262 fix (Pass 53 Day 9+ 2026-05-20 post-1A-alpha forensic):
    Original signal fired 478 trades (40% of all flow) with 24.7% WR /
    -3.47% mean PnL = -1659pp total contribution = ~95% of aggregate loss.
    Root cause: no regime gate, no volume confirmation, no momentum filter.
    Fired on every IFVG flag indiscriminately.

    Added confluence gates:
    - 200-EMA regime alignment (long above, short below)
    - vol_spike OR price_acceleration confirms institutional follow-through
      (IFVG breakdown without volume = false signal per ICT canon)
    """
    fl_base = s.get("smc_inverse_fvg_bullish", False)
    fs_base = s.get("smc_inverse_fvg_bearish", False)
    above_200 = s.get("price_above_ema_200", False)
    below_200 = s.get("below_ema_200", False)
    vol_confirms = s.get("vol_spike_2x", False) or s.get("force_index_breakout", False)
    fl = fl_base and above_200 and vol_confirms
    fs = fs_base and below_200 and vol_confirms
    return _strat3(fl, fs, "smc",
        ["smc_inverse_fvg_bullish", "price_above_ema_200", "vol_confirms"],
        ["smc_inverse_fvg_bearish", "price_below_ema_200", "vol_confirms"],
        ["Inverse FVG bullish + 200-EMA gate + volume confirms",
         "ICT IFVG role-flip with institutional follow-through"],
        ["Inverse FVG bearish + 200-EMA gate + volume confirms",
         "ICT IFVG role-flip with institutional follow-through"])
```

**3-gate dual strategy.** Most heavily-gated SMC strategy due to B262 forensic-fix.

**Each direction fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `smc_inverse_fvg_bullish` (LONG) / `_bearish` (SHORT) | EVENT-shaped point-in-time: FVG was mitigated AND price now opposite side (bullish FVG below price after invalidation → LONG; bearish FVG above price after invalidation → SHORT) |
| `price_above_ema_200` (LONG) / `below_ema_200` (SHORT) | Regime gate added B262 |
| `vol_confirms` = `vol_spike_2x OR force_index_breakout` | Volume confirmation added B262 |

#### Step 2 — Classify

- Category: `smc`
- Direction: dual via `_strat3`
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 dual default
- Last touched: B262 (forensic fix); B630/B663 verified

#### Step 3 — Producer source-read + temporality

- `smc_inverse_fvg_bullish` / `_bearish` computed at [smc_ict.py:194-206](backtest/signals/smc_ict.py#L194-L206) — checks last 20 ACTUAL FVG events for `is_mitigated` AND price now opposite side of zone (close < Bottom for bearish flip; close > Top for bullish flip)
- Lag: 0-day point-in-time check
- `price_above_ema_200` / `below_ema_200` STATE
- `vol_spike_2x` is genuine EVENT (today's volume >= 2x trailing 20-bar mean); `force_index_breakout` is EVENT (today's force index crosses breakout threshold)

**EVENT/STATE composition:** 2 EVENT (inverse_fvg + vol_confirms) + 1 STATE (200-EMA) per direction. **Strongest EVENT-anchored structure in the cluster** after the B262 fix.

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Original signal fired 478 trades (40% of all flow) with 24.7% WR = -1659pp" | ✅ **B262 forensic confirmed empirically** in Phase 1A-alpha. The fix is evidence-based, not theoretical. |
| "Inverse FVG = failed institutional imbalance becomes the new opposing reference" | ✅ Canonical ICT IFVG concept; implementation matches |
| "vol_spike OR price_acceleration confirms institutional follow-through" | ✅ Defensible — without volume, an IFVG break is a stop-hunt; with volume, it's institutional follow-through |
| Implicit "post-B262 fix the strategy is sound" | ⚠ **Pattern M** — B262 fixed the empirical disaster but the fix has not been re-validated against a full-universe cube replay; pre-B660 the fix is plausible but unproven |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B262 forensic precedent IS the active concern; post-B660 cube replay must surface whether the post-fix design is empirically sound on the full T1a universe
- Cross-ref: B262 is the canonical "kill the loser by gating not deleting" precedent — a model for Pattern E confluence wraps + W5 / W5m EXPLORATORY markers + low-fire-combo dispositions

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Already dual (`_strat3`); both directions fire under B262 fix
- Economic symmetry: ✅ price-action; both IFVG bullish AND bearish are valid per ICT semantics

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-B262 fix re-validation** | The 95%-aggregate-loss fix must be re-validated under post-B660 cube replay on T1a 503 names. If the fix is empirically sound, the strategy is the cluster's most-forensic-evidence-anchored design | HIGH | F1 |
| **F-pattern-J FVG overlap** | Inverse_fvg + FVG retest (SMC-1/SMC-2) both consume FVG primitive at different stages; marginal contribution audit | MEDIUM | Pattern J |
| **F-pattern-M unaudited Quantum Algo** | Quantum Algo backtest cited cluster-wide does NOT include the post-B262-fix design; verdict is from the broken pre-fix version | HIGH | Pattern M |
| F-fire-count | Post-fix gates triple-AND reduce fires materially; projected ~30-80/yr universe-wide per direction; borderline PASS min_trades=30 | INFO | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo (post-B262-fix) |
| (b) Tighter regime gate — `price_above_ema_50 AND price_above_ema_200` (multi-timeframe regime confluence) |
| (c) Looser regime gate — drop 200-EMA + keep volume; pure EVENT-anchored design |
| **(d) RECOMMENDED — (a) + post-B660 cube replay re-validation of B262 fix is the empirical adjudication path. If cube vindicates the fix, the strategy is the cluster's design-template; if it doesn't, the strategy should be DELETED per B262's own precedent of evidence-based intervention.** |
| (e) EXPLORATORY marker pre-cube (analogous to W5/W5m) — exclude from selection budget while keeping for cube-replay coverage |

**My recommendation: (d).** B262 represents the gold standard for SMC-strategy disposition methodology — gate-add fix based on empirical disaster. The post-fix design deserves a clean post-B660 cube test to settle whether the fix landed.

**Awaiting owner direction on SMC-3:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (d)
2. Confirm post-B660 cube-replay re-validation scope on B262 fix
3. Whether to surface B262 forensic precedent as a cluster-wide methodology citation (canonical model for gate-add-instead-of-delete dispositions)

---

### SMC-4. `strat_smc_breaker_block_short` (Batch 216, OB family, walked B673)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate SHORT — bullish OB mitigated downward becomes resistance.

#### Step 1 — Read the code

[screener.py:3272-3283](backtest/signals/screener.py#L3272-L3283):

```python
def strat_smc_breaker_block_short(s):
    """Batch 216: Breaker block short - bullish OB that was mitigated +
    price now below bottom -> the OB flips role and becomes resistance.
    Classic ICT 'breaker block' reversal setup."""
    fires = (
        s.get("smc_breaker_block_bearish", False)
        and s.get("below_ema_200", False)  # B630 sweep
    )
    return _strat(fires, "short", "smc",
        ["smc_breaker_block_bearish", "price_below_ema_200"],
        ["Bullish Order Block mitigated + price below - role flipped to resistance",
         "Below 200 EMA (bear regime)"])
```

**2-gate SHORT strategy.** Variant of inverse-FVG concept applied to Order Blocks.

| Gate | Meaning |
|---|---|
| `smc_breaker_block_bearish` | EVENT-shaped point-in-time: bullish OB was mitigated AND price now below OB Bottom (role flip to resistance) |
| `below_ema_200` | Bear regime |

#### Step 2-3 — Producer + temporality

- `smc_breaker_block_bearish` at [smc_ict.py:258-265](backtest/signals/smc_ict.py#L258-L265) — checks last 20 ACTUAL OB events (B556 filter-then-tail) for `is_mitigated AND ob_val == 1 AND close < float(bot)` → True
- OB primitive uses `event_recency_bars=90` via `_most_recent_event_within` (Pattern I applies indirectly through `smc_ob_bullish_active` STATE; but `smc_breaker_block_*` reads OB events directly via filter-then-tail of last 20 events — NOT recency-windowed)
- Lag: 0-day point-in-time check (mitigated-and-flipped)
- 1 EVENT-shaped + 1 STATE

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Bullish OB that was mitigated + price now below bottom → resistance flip" | ✅ Implementation matches ICT canon |
| "Classic ICT breaker block reversal setup" | ⚠ Pattern M — canonical per ICT methodology BUT no peer-reviewed validation |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B556 producer fix is current state
- No active investigations specific to SMC-4

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — SMC-5 `strat_smc_breaker_block_long`
- Economic symmetry: ✅ price-action

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-J OB-family overlap** | Breaker block + mitigation block + order block bounce all consume OB primitive at different stages; marginal contribution audit | MEDIUM | Pattern J |
| **F-borrow-cost** | B671 centralized DTC>8 gate applies | LOW | F5 carryover |
| **F-no-freshness-gate** | Unlike SMC-3 (B262 fix added vol_confirms), SMC-4 has no volume confirmation. The B262 forensic precedent may apply — pre-cube speculation that breaker-block-without-volume is high false-positive risk symmetric with B262 inverse_fvg-without-volume | MEDIUM | F1 + B262 precedent |
| F-pattern-A | `below_ema_200` B630 producer-additive ✅ | ✅ SHIPPED B630 | — |
| F-fire-count | Breaker block events rare (mitigated OBs are rare); projected ~10-30/yr universe-wide per direction; borderline FAIL min_trades=30 | MEDIUM | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Add `vol_confirms` gate symmetric with SMC-3 B262 fix — guards against breaker block being a stop-hunt without follow-through |
| (c) Branch-stratified cube replay surfacing OB-family overlap with SMC-7 (mitigation_block_short) + SMC-17 SHORT |
| **(d) RECOMMENDED — (b) + (c). The B262 precedent argues a freshness gate is the canonical SMC-strategy hardening pattern; SMC-4 lacks it. Post-B660 cube replay settles whether the gate-add improves vs status quo.** |
| (e) EXPLORATORY marker pre-cube — low-fire-combo class |

**My recommendation: (d).** The B262 forensic-fix precedent strongly suggests volume confirmation is a near-universal SMC-strategy hardening per ICT methodology itself ("IFVG breakdown without volume = false signal per ICT canon"); applying it symmetrically to breaker-block is the consistent design choice.

**Awaiting owner direction on SMC-4:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (d)
2. Whether (b) freshness-gate addition is a global SMC-cluster pattern (apply to SMC-5, SMC-6, SMC-7, SMC-10, SMC-11, SMC-12, SMC-13, SMC-14, SMC-16, SMC-17, SMC-18) or per-strategy decision
3. Pattern N (intra-cluster collinearity ablation) cube-replay scope

---

### SMC-5. `strat_smc_breaker_block_long` (Batch 216, OB family, walked B673)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate LONG; symmetric mirror of SMC-4.

#### Step 1 — Read the code

[screener.py:3286-3296](backtest/signals/screener.py#L3286-L3296):

```python
def strat_smc_breaker_block_long(s):
    """Batch 216: Breaker block long - bearish OB that was mitigated +
    price now above top -> flips to support."""
    fires = (
        s.get("smc_breaker_block_bullish", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "smc",
        ["smc_breaker_block_bullish", "price_above_ema_200"],
        ["Bearish Order Block mitigated + price above - role flipped to support",
         "Above 200 EMA (regime gate)"])
```

**2-gate LONG strategy.** Symmetric mirror of SMC-4.

#### Step 2-7 (compact — symmetric with SMC-4)

- Category `smc`; LONG; B291 default; last touched B663
- Producer: [smc_ict.py:258-265](backtest/signals/smc_ict.py#L258-L265) symmetric branch
- Same Pattern J + no-freshness-gate concern as SMC-4
- Same fire-count concern (rare mitigated OB events)
- Pattern A B663 ✅

**Options:** same as SMC-4; bundled. **My recommendation: (d) bundled with SMC-4.**

**Awaiting owner direction on SMC-5:** bundled with SMC-4.

---

### SMC-6. `strat_smc_mitigation_block_long` (Batch 216, OB family, walked B673)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate LONG — price entering unmitigated bullish OB zone.

#### Step 1 — Read the code

[screener.py:3299-3313](backtest/signals/screener.py#L3299-L3313):

```python
def strat_smc_mitigation_block_long(s):
    """Batch 216: Price entering an UN-mitigated bullish Order Block
    zone - the institutional zone is being mitigated NOW. Lower-risk
    entry than waiting for the OB to fully play out; pairs naturally
    with subsequent CHoCH/BOS confirmation."""
    fires = (
        s.get("smc_mitigation_block_long", False)
        and s.get("price_above_ema_200", False)
        and s.get("rsi_14", 50) < 50
    )
    return _strat(fires, "long", "smc",
        ["smc_mitigation_block_long", "price_above_ema_200", "rsi_14<50"],
        ["Price inside bullish Order Block zone - mitigation underway",
         "Above 200 EMA (regime gate)",
         "RSI pullback context (not overbought)"])
```

**3-gate LONG strategy.** Mitigation_block is the "early entry" variant of order-block trading — enter as the OB is being mitigated NOW (lower-risk than waiting).

| Gate | Meaning |
|---|---|
| `smc_mitigation_block_long` | EVENT-shaped: price inside UN-mitigated bullish OB (`is_mitigated == False AND in_zone == True AND ob_val == 1`) |
| `price_above_ema_200` | Long-term uptrend |
| `rsi_14 < 50` | Pullback context — not overbought |

#### Step 2-3 — Classify + producer

- Category `smc`; LONG; B291 default; last touched B663
- Producer: [smc_ict.py:268-272](backtest/signals/smc_ict.py#L268-L272); `mitigation_long = True` when `not is_mitigated AND in_zone AND ob_val == 1`
- 1 EVENT-shaped + 2 STATE
- Pattern I applies indirectly — the OB primitive itself uses 90-bar recency for the "active" STATE but breaker/mitigation reads OB events from filter-then-tail of last 20 directly. Different staleness profile than SMC-17 order_block_bounce which DOES consume `smc_ob_bullish_active` STATE.

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Price entering an UN-mitigated bullish OB zone" | ✅ Implementation matches |
| "Lower-risk entry than waiting for the OB to fully play out" | ⚠ Pattern M — canonical per ICT but no peer-reviewed validation. The "lower-risk" claim is unverified outside the ICT framework. |
| "RSI pullback context (not overbought)" | ⚠ **F-rsi-default-50 hazard** per `S5-RSI-DEFAULT-50-FAMILY` ticket — `s.get("rsi_14", 50) < 50` with default=50 means missing data fails the gate (50 < 50 is False). Fail-safe ✅. But: default=50 also means an RSI exactly at 50 fails the gate. **Strict-inequality on default-value-AT-threshold = the canonical S5-RSI-DEFAULT-50 family member.** B654 W8 fix precedent (drop the gate) may apply if cube shows the gate is near-no-op. |

#### Step 5 — OPEN_INVESTIGATIONS grep

- **`S5-RSI-DEFAULT-50-FAMILY`** ticket directly applies — SMC-6 + SMC-7 are family members
- B556 producer fix is current state

#### Step 6 — Missing-inverse

- ✅ Inverse EXISTS — SMC-7 `strat_smc_mitigation_block_short` (symmetric with `rsi_14 > 50` rally context)

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-J OB-family overlap** | SMC-6 + SMC-4/SMC-5 + SMC-17 LONG share OB primitive; marginal contribution audit | MEDIUM | Pattern J |
| **F-rsi-default-50 hazard** | `rsi_14 < 50` strict-inequality on default-50; family member of `S5-RSI-DEFAULT-50-FAMILY`. B654 W8 precedent (drop the gate) may apply post-cube | MEDIUM | F-rsi-50 |
| F-pattern-A | `price_above_ema_200` ✅ | ✅ SHIPPED B663 | — |
| F-fire-count | Mitigation events more common than breaker-block (unmitigated OBs are common); projected ~30-90/yr universe-wide; PASS likely | INFO | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Drop `rsi_14<50` gate per B654 W8 precedent (S5-RSI-DEFAULT-50-FAMILY resolution option a) — would raise fire count slightly + remove near-no-op gate |
| (c) Tighten `rsi_14<50` to `rsi_14<45` (canonical pullback band; per `feedback_minimum_fire_count_gate_before_cube`) — actual pullback rather than coin-flip midpoint |
| (d) Branch-stratified cube replay — keep status quo + cube settles RSI-gate marginal contribution |
| **(e) RECOMMENDED — (d). RSI-gate is the candidate Class 2 LOOSEN/TIGHTEN; cube empirical settles whether to drop (b) or tighten (c). Pre-cube no code change.** |

**My recommendation: (e).**

**Awaiting owner direction on SMC-6:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (e)
2. Whether RSI-default-50 family-bug sweep should bundle SMC-6 + SMC-7 with broader screener.py grep (per `S5-RSI-DEFAULT-50-FAMILY` ticket scope)

---

### SMC-7. `strat_smc_mitigation_block_short` (Batch 216, OB family, walked B673)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate SHORT; symmetric mirror of SMC-6.

#### Step 1 — Read the code

[screener.py:3316-3327](backtest/signals/screener.py#L3316-L3327):

```python
def strat_smc_mitigation_block_short(s):
    """Batch 216: Symmetric mitigation block short."""
    fires = (
        s.get("smc_mitigation_block_short", False)
        and s.get("below_ema_200", False)  # B630 sweep
        and s.get("rsi_14", 50) > 50
    )
    return _strat(fires, "short", "smc",
        ["smc_mitigation_block_short", "price_below_ema_200", "rsi_14>50"],
        ["Price inside bearish Order Block zone - mitigation underway",
         "Below 200 EMA (bear regime)",
         "RSI rally context (not oversold)"])
```

**3-gate SHORT strategy.** Symmetric with SMC-6 with `rsi_14 > 50` rally context. Same `S5-RSI-DEFAULT-50-FAMILY` hazard symmetric direction.

#### Step 2-7 (compact — symmetric with SMC-6)

- Same Pattern J + same RSI-default-50 family hazard
- B671 centralized DTC>8 gate applies
- Fire-count slightly lower than SMC-6 (bearish OBs less common than bullish in upward-drift equity)
- Pattern A B630 ✅

**Options:** same as SMC-6; bundled. **My recommendation: (e) bundled.**

**Awaiting owner direction on SMC-7:** bundled with SMC-6.

---

### SMC-8 through SMC-18 — AWAITING B673b+ EXPANSION

> **Status:** ⏳ COMPACT WALKS BELOW; FULL PIVOT-DOC TEMPLATE EXPANSION QUEUED FOR B673b-c (follow-on commits). Per `feedback_no_rushing_per_strategy_tweak` + the B672 multi-commit precedent: ship doc infrastructure + first 7 walks at full template density in B673; expand remaining 11 walks (SMC-8 through SMC-18) across 2-3 follow-on commits.

#### Compact summary table for follow-on expansion (Sub-clusters C, D, E, F)

| SMC # | Function | Primary findings to expand | Key cross-references |
|---|---|---|---|
| **SMC-8** | `strat_smc_discount_long` | Pattern K dealing_range lookahead-vector + Pattern N internal multi-test + EMA-200 gate | S4-FIB-ANCHOR-LOOKAHEAD-AUDIT |
| **SMC-9** | `strat_smc_premium_short` | Same Pattern K + symmetric mirror; B671 borrow-trap | Same |
| **SMC-10** | `strat_smc_ote_long` | NO EMA gate (relies on BOS/CHOCH confluence for trend); Pattern I + Pattern J + Fib-zone 62-79% retracement free parameter | S4-FIB-ANCHOR-LOOKAHEAD-AUDIT cross-ref (OTE uses retracements primitive) |
| **SMC-11** | `strat_smc_ote_short` | Symmetric mirror SMC-10; B671 borrow-trap | Same |
| **SMC-12** | `strat_smc_equal_highs_sweep_short` | Equal-highs sweep + bearish FVG confluence; B390 producer fix; Pattern G low-fire-combo + Pattern O liquidity_range_pct=0.01 hardcoded; NO EMA gate | S4-LOW-FIRE-COMBO-EXPLORATORY-REVIEW-POST-B660 |
| **SMC-13** | `strat_smc_equal_lows_sweep_long` | Symmetric mirror SMC-12 | Same |
| **SMC-14** | `strat_smc_bos_retest_entry` (dual) | DUAL; Pattern O tol=0.005 (0.5%) BOS retest hardcoded near-test; B556 producer fix; Pattern I (BOS recency 90-bar) | Pattern O config-parameterization ticket candidate |
| **SMC-15** | `strat_smc_bos_continuation` (dual) | DUAL; B278 forensic-fix precedent (added vol_confirms + RSI direction); EMA-200; Pattern I + Pattern N | B278 precedent vs B262 precedent (both forensic-add-gate fixes) |
| **SMC-16** | `strat_smc_choch_reversal` (dual) | DUAL; CHOCH + FVG-active confluence; NO EMA gate; Pattern I + Pattern J | — |
| **SMC-17** | `strat_smc_order_block_bounce` (dual) | DUAL; OB-active + RSI<45 LONG / >55 SHORT (asymmetric thresholds vs SMC-6/7 50/50); EMA-200; Pattern I consumed via `smc_ob_*_active` STATE | S5-RSI-DEFAULT-50-FAMILY (45/55 thresholds; not on default-50 boundary) |
| **SMC-18** | `strat_smc_liquidity_sweep_reversal` (dual) | DUAL; liquidity_swept_* + CHOCH OR BOS confluence; NO EMA gate; Pattern I + Pattern J + Pattern N (combinatorial overlap with SMC-12/13 sweeps) | Cross-strategy overlap with SMC-12/13 + SMC-16 |

---

## Outstanding queue tickets surfaced (SMC cluster)

| Ticket slug | Status | Source |
|---|---|---|
| `S4-SMC-CLUSTER-PATTERN-J-CUBE-ABLATION` (NEW) | DEFERRED-POST-B660-CUBE | Pattern J primitive overlap across all 18 strategies — needs cube-replay marginal-contribution audit symmetric with `S5-13F-SLEEVE-MARGINAL-CONTRIBUTION-TEST` |
| `S4-SMC-CLUSTER-PATTERN-N-INTRA-CLUSTER-COLLINEARITY` (NEW) | DEFERRED-POST-B660-CUBE | 24 cells on 7 primitives; intra-cluster effective-test-count audit |
| `S4-SMC-PATTERN-K-PIT-AUDIT` (NEW) | PENDING-PIT-AUDIT | SMC-8/9 dealing_range_lookback=50 lookahead-vector class; symmetric with S4-FIB-ANCHOR-LOOKAHEAD-AUDIT |
| `S4-SMC-PATTERN-O-CONFIG-PARAMETERIZATION` (NEW) | DEFERRED-NEAR-TERM | event_recency_bars=90 + dealing_range_lookback=50 + tol=0.005 + liquidity_range_pct=0.01 hardcoded; move to config.py for cube sensitivity sweeps |
| `S4-SMC-B262-FIX-CUBE-REVALIDATION` (NEW) | DEFERRED-POST-B660-CUBE | SMC-3 post-B262-fix design has not been validated against full-universe cube; gate of B262 forensic precedent's empirical claim |
| `S4-SMC-PATTERN-M-QUANTUM-ALGO-AUDIT` (NEW) | DEFERRED-POST-B660-CUBE | Per-strategy contribution to Quantum Algo Mar 2026 61% WR / 2.17 PF claim is unknown; cube replay against T1a 503 names is the only adjudication |
| `S5-RSI-DEFAULT-50-FAMILY` (EXISTING) | DEFERRED-STAGE-5 | SMC-6 + SMC-7 are family members |
| `S4-LOW-FIRE-COMBO-EXPLORATORY-REVIEW-POST-B660` (EXISTING) | DEFERRED-POST-B660-MEASUREMENT-EXPLICIT-OWNER-ROUND-2-HOLD | SMC-12 + SMC-13 (equal-highs/lows sweep) candidates for the existing low-fire-combo list |
| `S5-MARGINAL-CONTRIBUTION-SCORING` (EXISTING) | DEFERRED-STAGE-5 | SMC cluster is the second-highest-leverage application of C3 methodology after the smart-money 13F sleeve test |

---

## Cluster-wide methodology references

- **Producer:** [backtest/signals/smc_ict.py](backtest/signals/smc_ict.py) — wraps `vendored/smartmoneyconcepts/smartmoneyconcepts.py` (joshyattridge/smart-money-concepts under DEC-508 Phase A)
- **Strategies:** [backtest/signals/screener.py:3208-3543](backtest/signals/screener.py#L3208-L3543) — 18 functions
- **Forensic precedents:** B262 (inverse_fvg gate-add post-1A-alpha forensic; 95%-loss fix), B278 (bos_continuation gate-add); B273 (event_recency window fix); B390 (liquidity producer filter-then-tail fix); B556 (FVG + OB producer filter-then-tail fix); B555 (OPT-C panel cache); B458 (silent-failure logging); B630 (below_ema_200 producer-additive sweep); B663 (Pattern A WAVE 1 ema_200 default-True → False sweep); B671 (centralized SHORT borrow-trap gate via inspect-frame consult)
- **Owner-decision tooling reference:** B570 (Stage 4 owner-decision tool — set 5 SMC strategies to "Deferred" status via tool, NOT via per-strategy 7-step walk per CHECKLIST #105)
- **Vendored library:** [vendored/smartmoneyconcepts/smartmoneyconcepts.py](vendored/smartmoneyconcepts/smartmoneyconcepts.py) — single-point-of-failure for all 18 strategies (Pattern L)
- **Unaudited empirical citation:** Quantum Algo Mar 2026 backtest (61% WR / 2.17 PF / +2.27R; 10 assets; 2,600 trades; 26 months) — see Pattern M
- **Cluster status sequencing:** PENDING B660 measured-fire-count + B668 cube replay + B669 survivorship execution. No empirical disposition pre-B660 per `feedback_no_rushing_per_strategy_tweak` + B665 foundational re-prioritization commitment.

---

## B673 cluster walk status

| Item | Status |
|---|---|
| Doc infrastructure (header + adaptations + inventory + patterns + state table) | ✅ B673 |
| Per-strategy walks SMC-1 + SMC-2 + SMC-3 + SMC-4 + SMC-5 + SMC-6 + SMC-7 (7 walks at full template density) | ✅ B673 |
| Per-strategy walks SMC-8 + SMC-9 + SMC-10 + SMC-11 (sub-clusters C + D) | ⏳ B673b |
| Per-strategy walks SMC-12 + SMC-13 + SMC-14 (sub-cluster E lead-in + structural F lead-in) | ⏳ B673c |
| Per-strategy walks SMC-15 + SMC-16 + SMC-17 + SMC-18 (sub-cluster F completion) | ⏳ B673d |
| External reviewer pass | ⏳ post-walk-completion |
| Cluster-wide post-walk findings synthesis | ⏳ post-reviewer |

**Cumulative B673: 7 of 18 walks fully expanded; remaining 11 queued for B673b-d follow-on commits.**
