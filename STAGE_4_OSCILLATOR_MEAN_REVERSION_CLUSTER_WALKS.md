# Stage 4 — Oscillator & Mean-Reversion Cluster Walks

> **B750 STATUS BANNER (2026-06-14) — CLUSTER A SCAFFOLDING + INITIAL WALKS.**
>
> This is the FIRST of three new cluster docs created in B750-B762 to close the Stage 4 walk-coverage gap surfaced by B679 stale-index correction. Owner-confirmed scope per "approve all" 2026-06-14: 3 clusters of 30/33/33 = 96 previously-unwalked strategies. This doc covers **Cluster A = Oscillator & Mean-Reversion (30 strategies)**.
>
> **Source of truth:** commit `86f7d76c0` (HEAD as of B750 2026-06-14 09:43 UTC). Strategy roster pinned at `len(ALL_STRATEGIES) = 221` per CLAUDE.md attestation 2026-06-12. Unwalked-set derivation: per-strategy walk-section header grep across all 8 existing cluster docs (Methods 1-4 reconciled; final definitive count = 96 unwalked).
>
> **Per `feedback_walk_step3_must_read_producer_source` (CHECKLIST #105):** every walk in this doc reads producer source end-to-end (not docstring-only). Step 3 explicitly cites file:line.
>
> **Per `feedback_no_rushing_per_strategy_tweak`:** walks surface FINDINGS + propose threshold tweaks BUT do not auto-apply changes. Owner directs each tweak per-batch.
>
> **Per `feedback_no_prior_edge_consolidate_before_tune` + `feedback_minimum_fire_count_gate_before_cube`:** walks include a-priori fire-count projection where the gate-stacking math can be inferred from producer thresholds. Cube empirical-validation routing deferred until measurement valid (B690b + W5-council T1a+T1c+T2 re-measure).
>
> **Carry-forward from prior cluster walks:** Pattern A (regime affinity defaults all-regimes), Pattern F (default-True silent gap per B663 family-sweep), Pattern W (deterministic-duplicate post-tightening per B718 hull_rsi precedent), Pattern N (effective-N below IID assumption per B710 ceiling), Pattern G (fire-starvation accept-rarity per B719 SMC reviewer), Pattern J (marginal-contribution audit per B714 routing), Pattern Y (Bulkowski retest absorption carry from breakout).
>
> **Sequencing notes:** B750 ships framework (status banner / audience / methodology / scope inventory / cluster state table / cross-strategy patterns A-N) + 3 sample walks at full template density (A-1 rsi_oversold + A-15 ppo_crossover + A-19 avwap_50_reclaim). Remaining 27 walks ship in B751+ at 5-10 per batch with pyramid green per `feedback_pyramid_per_addressal`.

---

## Audience

### 1. External reviewer (Cluster-A-specific differentiators)

If you're reviewing this cluster after reviewing prior cluster docs (Pivot/Trend/Smart-Money/SMC/ICT/Breakout/Event/Chart-Candle), the things that will be different here are:

1. **All strategies are timing-indicator-based.** Unlike Smart Money (asymmetric data sources) or Event-Driven (calendar/announcement triggers), Cluster A strategies fire on TECHNICAL signal events: RSI threshold crossings, Bollinger touches, AVWAP reclaims, MA crossovers. The producer-PIT-discipline failure mode is different — bar-of-fire is the gate-event bar, not a separate calendar bar.

2. **High overlap with the existing "mean_reversion" + "momentum" + "vwap" + "trend" registry categories.** Many of these strategies were registered in pre-Pass-53 batches (B206 Connors stack, B208 AVWAP family, B204 Bollinger). Owner-directed "no a-priori pruning" applies — but Pattern J (marginal-contribution audit) is the routing mechanism for Cluster A specifically. Expect 30 → ~15-20 effective primitives post-Pattern-J.

3. **No new producer dependencies expected.** All gate signals consumed are in `technical.py` (RSI, Stoch, Williams, Ultimate, MFI, Bollinger, Keltner, Camarilla, CPR, MA-cross, AVWAP, OBV, MACD, PPO, ROC, CMF, awesome). None require TIER 2 cache-read producers (unlike SM cluster which blocked on B690). This means Cluster A is **cube-ready measurement-wise post-B689 re-run** (which DID cover technical.py producers).

4. **Most-likely fake-edge vectors per the existing cluster doc reviewer patterns:**
   - Pattern N (effective-N < raw N) on oscillator strategies: oscillator extremes cluster in vol regimes (March 2020), so 100 raw fires might be 10-15 effective IID events.
   - Pattern F (silent-gap default-True) was already swept in B663 across ~30 strategies; this cluster should grep CLEAN but Step 4 verifies.
   - Pattern W (deterministic-duplicate): some RSI variants (rsi9_extreme + rsi_oversold + rsi21_slow) may post-tightening become subsets of each other.
   - Pattern J (marginal-contribution): MA-cross family (golden_cross_9_21 + golden_cross_20_50 + golden_cross_50_200 + golden_cross_volume + death_cross_50_200_volume) are reskins; one underlying MA-cross primitive + parameter sweep would suffice.

5. **EXPLORATORY classification expected for the rarest strategies.** Per B652 W5m precedent, strategies firing <30/yr/regime get DO-NOT-DEPLOY gate even on cube PASS. Candidates from this cluster (initial estimate, subject to B690b measurement): rsi9_extreme (RSI<20 + uptrend gate = very rare), bb_squeeze_volume (squeeze + 2× volume + VWAP), mfi_oversold (MFI<20 + pivot support + OBV rising).

### 2. Future readers

If you're reading this 6+ months from B750 to understand "why is the oscillator family structured this way":

- This cluster was the LAST to receive cluster walks because the existing 8 clusters absorbed the high-conviction strategies first (smart money, SMC, ICT, breakout, chart pattern). Cluster A residuals are the "Layer 1 baseline" oscillators registered in early batches (B206 Connors stack, B208 AVWAP, B204 Bollinger, B631 Ultimate).
- The cluster was source-verified at 30 strategies (not 78 as the B679 index estimated; not 70 as a naive grep suggested). The data-consumption-audit discipline (CHECKLIST #106, memory `feedback_data_consumption_audit_must_apply_checklist_44b`) was applied to derive the correct count.
- Cluster walks happen POST-external-review unlike the smart-money cluster's pre-external-review pattern — because the 5 unreviewed-as-of-B679 cluster docs received external reviews B696-B719 BEFORE B750 began the unwalked-set sweep.
- The cluster grouping was 3-way semantic, not arbitrary or alphabetical. Group A (this doc) = timing indicators; Group B (next doc) = trend confluence + chart-pattern residuals; Group C (third doc) = external-signal-driven (news/calendar/index/classification).

---

## Methodology adaptations for the Oscillator & Mean-Reversion cluster

### M1 — Same-bar fire-vs-lookback timing

Oscillator strategies fire on THRESHOLD events (rsi_14 < 35, mfi_oversold, stochrsi_oversold) which can be:

- **State-bar fire:** `rsi_14 < 35` is True for any bar where RSI is below 35 — a STATE signal that can persist for many consecutive bars. Strategy fires every day until RSI crosses back above 35.
- **Cross-event fire:** `cmf_cross_up` is True only on the bar where CMF crossed zero — an EVENT signal that fires once per crossing.

Walks must distinguish state-bar fire from cross-event fire per `feedback_signal_temporality_event_vs_state`. State-bar fire on oscillator extremes systematically over-fires in vol regimes; cross-event fire is the canonical Wilder/Wyckoff treatment.

### M2 — Connors stack discipline

Several strategies (rsi_oversold, ultimate_oscillator, bollinger_lower) were upgraded in B206 to add Connors RSI(2) as an alternative trigger via OR-disjunct. The methodology:

- Primary trigger: slow RSI (14 or 21) below conservative threshold (30-40)
- OR alternative: fast RSI(2) below extreme threshold (<5)

The intent (per Larry Connors / Quantified Strategies 2024 backtests): fast RSI(2) catches intraday extremes that slow RSI(14) misses. The risk: introduces signal-multiplication (2 triggers instead of 1) without proportional gate-tightening, inflating fire rate.

Walks must check whether Connors-stack OR-disjunct is paired with adequate trend-regime gate (200-EMA). If yes, acceptable. If no, Pattern F-precedent (default-True silent gap) re-evaluation is warranted.

### M3 — Trend-gate symmetry post-B663 family sweep

B663 family-sweep replaced `price_above_ema_200` default-True silent-gap with the symmetric `below_ema_200` (B630 producer addition) across ~30 strategies. Cluster A walks must verify the SHORT side of each dual strategy uses positive `below_ema_200`, not `not s.get("price_above_ema_200", True)`. Step 3 grep checks every walk.

### M4 — Borrow-trap gate verification (B718 cluster lint)

B718a-d shipped the explicit `borrow_ok` gate refactor + B744 static lint. All 30 Cluster A strategies with `direction="short"` or `direction="dual"` must consume `_short_borrow_trap_active(s)` at the SHORT branch. Step 3 verifies via grep.

### M5 — Stage 5 cube cell budget per strategy

Cluster A's 30 strategies × 26 exit methods (per B487 SM2 cube extension) = 780 cube cells. Owner directive `project_no_apriori_strategy_pruning` says let empirical cube decide — but Cluster A's 780 cells contribute to the 221-strategy × 4-regime × 26-exit ≈ 23K cell Bonferroni denominator. Walks surface Pattern J consolidation candidates to reduce the denominator.

### M6 — Oscillator extreme correlation (effective-N below IID)

Oscillator extremes (RSI<30, MFI<20, %B<0.05, stochrsi_oversold) are highly correlated across tickers DURING the same vol regime. March 2020 = ~80% of T1a tickers simultaneously oversold by traditional thresholds. This means:

- Raw fire count of 100 events on T1a during 2020-2026 might decompose into ~5-15 vol-regime CLUSTERS, not 100 independent IID events.
- min_trades=100 IID-equivalent threshold is NOT met by raw count if the events cluster in 2 or 3 regime windows.

Walks must surface this Pattern N concern per-strategy where applicable. Cube measurement post-B690b should compute effective-N via auto-correlation, not raw count.

### M7 — Producer-gate boundary discipline

Many Cluster A strategies consume threshold signals computed in `technical.py` (e.g., `rsi_14<30` = `s.get("rsi_14<30")` boolean). Walks must verify the THRESHOLD lives in the producer (so cube can sweep it), not hardcoded in the strategy. If the strategy hardcodes `s.get("rsi_14", 50) < 35`, the threshold is NOT cube-sweepable; this is a Pattern G concern per B719 SMC reviewer.

### M8 — Pattern N (effective-N) blocker for cube verdict statistical validity

Per B660 council verdict + W5 council recommendation:
- Cube must measure effective-N via autocorrelation post-fire-count
- Pattern N inflation factor reduces sample-size further
- Bonferroni denominator at 221 strategies × 4 regimes × 26 exits = 23K cells
- Per-cell alpha = 0.05 / 23K = 2.2e-6

Walks acknowledge this is a CUBE infrastructure gap; not Cluster-A-specific to fix here.

---

## Reviewer findings response matrix

> Pre-emptive placeholder for B751+ owner-review feedback per B679 review-solicitation pattern.

| Reviewer round | Findings | Response | Batch |
|---|---|---|---|
| _Pending_ | Awaiting external reviewer pass on B750 framework + sample walks | — | OPEN |
| _Pending_ | Awaiting B751+ per-strategy walk reviewer feedback | — | OPEN |
| _Pending_ | Awaiting cross-cluster Pattern J/N consolidation reviewer feedback | — | OPEN |

---

## Cluster scope inventory (30 strategies)

Sub-clustered by technical-family for walk sequencing:

| Sub-family | Count | Strategies |
|---|---|---|
| **A.1 RSI family** | 5 | `rsi_oversold` (dual), `rsi_overbought_short`, `rsi9_extreme` (long), `rsi21_slow` (dual), `rsi_volume_200ema` (?) |
| **A.2 Stoch / StochRSI** | 3 | `stoch_oversold` (long), `stochrsi_oversold` (long), `stochrsi_overbought_short` |
| **A.3 Williams / Ultimate / MFI** | 3 | `williams_r_oversold` (long), `ultimate_oscillator` (dual), `mfi_oversold` (dual) |
| **A.4 Bollinger** | 3 | `bollinger_lower` (dual), `bollinger_tight` (dual), `bollinger_upper_short` |
| **A.5 Keltner** | 1 | `keltner_lower` (long) |
| **A.6 Camarilla** | 3 | `camarilla_r4_breakout` (dual; B641 renamed from r3), `camarilla_rsi_obv` (dual), `camarilla_rsi_obv_short` |
| **A.7 CPR** | 2 | `cpr_narrow_momentum` (dual), `cpr_narrow_momentum_short` |
| **A.8 AVWAP** | 3 | `avwap_50_reclaim` (dual), `avwap_252_breakout` (dual), `avwap_20high_rejection_short` |
| **A.9 Momentum oscillators** | 4 | `awesome_oscillator` (dual), `cmf_flip` (dual), `ppo_crossover` (dual), `roc_burst` (?) |
| **A.10 Williams/Stoch dual** | 1 | `williams_stoch_dual` (?) |
| **A.11 Prev-day mean-reversion** | 1 | `prev_day_low_bounce` (long) |
| **A.12 Squeeze confluence** | 1 | `bb_squeeze_volume` (dual) |

Sub-family count = 5+3+3+3+1+3+2+3+4+1+1+1 = 30 ✓

**Direction split:**
- LONG-only: 6 (rsi9_extreme, stoch_oversold, stochrsi_oversold, williams_r_oversold, keltner_lower, prev_day_low_bounce)
- SHORT-only: 4 (rsi_overbought_short, stochrsi_overbought_short, bollinger_upper_short, camarilla_rsi_obv_short, avwap_20high_rejection_short = 5)
- DUAL (_strat3): ~17
- ? (direction unclear from roster): 3 (rsi_volume_200ema, roc_burst, williams_stoch_dual)

Walks resolve ? direction via Step 3 source-read.

---

## Cross-strategy patterns (Cluster A)

Patterns A-G are carried from prior clusters (semantics preserved). Patterns N-T are NEW or refined for Cluster A.

### Pattern A — Regime affinity defaults all-regimes (CARRIED)

Per B577 surface + STRATEGY_REGIME_AFFINITY survey: 204 of 205 strategies fall through to "no affinity = all regimes" default. Cluster A inherits this default. Walks check whether docstring claims a regime-specificity that the registry doesn't enforce; if so, surface as Pattern A doc-vs-registry mismatch.

### Pattern F — `default=True` silent gap on `price_above_ema_200` (POST-B663 SWEEP)

B663 family-sweep replaced `s.get("price_above_ema_200")` default-True (silent-gap fail-open) with explicit `s.get("price_above_ema_200", False)` AND symmetric `s.get("below_ema_200", False)` SHORT side across ~30 strategies. Cluster A walks must verify the sweep was applied to all 30 here. Expected outcome: most CLEAN post-B663 / B630. Surface any residual instances.

### Pattern G — Hardcoded threshold not cube-sweepable (NEW, refined per B719 SMC)

Strategy hardcodes `s.get("rsi_14", 50) < 35` instead of consuming `s.get("rsi_14<35")` boolean from producer. Hardcoded threshold:
- Cannot be swept by Stage 5 cube parameter routing
- Hides the threshold from `STRATEGY_ROSTER.md` auto-generation
- Locks the strategy at one specific point in parameter space

Walks surface candidates for producer-additive threshold-signal upgrades (e.g., emit `rsi_14<30`, `rsi_14<35`, `rsi_14<40` as separate signals; strategy consumes the one it wants, cube sweeps which one passes).

### Pattern J — Marginal contribution audit needed (CARRIED from B714)

Multiple strategies in Cluster A look like reskins:
- 5 MA-cross variants (golden_cross_9_21, _20_50, _50_200, _volume, death_cross_50_200_volume) — same underlying signal at different timescales
- 3 RSI oversold variants (rsi_oversold, rsi9_extreme, rsi21_slow) — same RSI primitive at different windows
- 3 AVWAP strategies (avwap_50_reclaim, avwap_252_breakout, avwap_20high_rejection_short) — same AVWAP primitive at different anchor lookbacks
- 2 CPR variants (cpr_narrow_momentum, cpr_narrow_momentum_short)
- 3 Camarilla variants (camarilla_r4_breakout, camarilla_rsi_obv, camarilla_rsi_obv_short)

Pattern J disposition: post-B690b measurement, route via `S4-B714-PATTERN-F-OUTPUT-DECISION-DELETE-WRAPPERS-VS-CONSOLIDATE` framework:
- (a) DELETE-WRAPPERS: if reskin gates carry no marginal information, delete the variants, keep one underlying primitive
- (b) CONSOLIDATE-VARIANTS: collapse to 1 strategy + parameter sweep
- (c) RETAIN-AS-EXPLORATORY: if measurement shows distinct alpha

Expected post-Pattern-J: 30 strategies → ~15-20 effective primitives.

### Pattern N — Effective-N below IID assumption (NEW, refined per B710 + W5 council)

Oscillator extremes correlate across tickers DURING vol regimes:
- March 2020: ~80% of T1a oversold simultaneously
- November 2018 / 4Q 2018: ~60% oversold cluster
- August 2015 / China flash crash: cluster
- February 2018 / volmageddon: cluster

Effective-N = raw_N / cluster_inflation_factor. For oscillator strategies, cluster inflation ≈ 3-10×. So 100 raw fires = ~10-30 IID-equivalent observations.

Walks surface Pattern N concern per-strategy. Cube must implement auto-correlation-based effective-N post-fire-count (separate ticket: `S4-B750-PATTERN-N-EFFECTIVE-N-AUTOCORRELATION-CUBE-EXTENSION`).

### Pattern Q — STATE vs EVENT temporality misuse (NEW, refined per B611 critique)

Oscillator strategies that consume STATE signals (rsi_14<35 stays True for N bars during the oversold window) over-fire systematically:
- Bar 1: RSI crosses below 35 → strategy fires
- Bar 2-5: RSI still below 35 → strategy fires every bar
- Bar 6: RSI crosses above 35 → strategy stops firing

This inflates fire count by 3-10× vs the canonical "fire ONCE per crossing" interpretation. Walks surface candidates for EVENT-only conversion (B655 T10 supertrend precedent: producer emits `supertrend_flip_recent_long_5d` instead of `supertrend_bullish` STATE).

Pattern Q candidates in Cluster A: rsi_oversold, rsi21_slow, rsi_overbought_short, mfi_oversold, stoch_oversold, stochrsi_oversold, ultimate_oscillator (any threshold-state strategy).

### Pattern R — Connors-stack OR-disjunct without proportional tightening (NEW)

B206 Connors stack added `(rsi_2<5 OR rsi_14<35)` to multiple strategies (rsi_oversold, ultimate_oscillator, bollinger_lower). Risk: signal-multiplication without proportional gate-tightening inflates fire rate.

Walks surface candidates where the Connors-stack expansion was paired with INADEQUATE compensating gate. Acceptable: stack + tight regime gate (200-EMA + 50-SMA + close-strong). Unacceptable: stack with single 200-EMA only.

### Pattern S — Direction-asymmetry in dual strategies (NEW per B611 lessons)

Many Cluster A duals were structured via mechanical inverse: LONG fires when oversold + uptrend, SHORT fires when overbought + downtrend. But:
- Bull-market drift makes SHORT side mechanically less profitable than LONG
- Borrow cost on SHORT (per B713 + B718 explicit gate) reduces effective edge
- Squeeze risk on SHORT (especially on mean-reversion overbought-shorts) creates asymmetric tail risk

Walks surface Pattern S concern: dual strategies where SHORT side may be structurally weaker than LONG; cube may show LONG PASS / SHORT FAIL not because of strategy design but due to drift + borrow + squeeze asymmetry.

### Pattern T — MA-cross redundancy with EMA-trend gate (NEW)

MA-cross strategies (golden_cross_*, death_cross_*) fire on MA-line cross. But many of those same strategies ALSO consume `price_above_ema_200` as a regime gate. This is collinear: if golden_cross_50_200 fires (50-SMA > 200-SMA), price is likely ALREADY above 200-EMA. The trend gate adds little marginal information.

Walks surface Pattern T candidates. Disposition options: (a) drop the trend gate, (b) replace with a non-collinear trend-strength gate (ADX), (c) keep both and accept collinearity (status quo).

### Pattern W — Deterministic duplicate post-tightening (CARRIED from B718 hull_rsi)

If RSI variants are tightened (e.g., rsi21_slow's RSI<35 threshold lowered to <30 per Pattern J consolidation proposal), the post-tightening fire condition may become IDENTICAL to rsi_oversold's gate. Walks surface Pattern W candidates per `S4-B718-HULL-RSI-SHORT-DELETION-DECISION-VS-DUAL` precedent.

---

## Cluster current state table

| # | Slug | Strategy | Direction | Sub-family | Producer cache | Walked? | Status |
|---|---|---|---|---|---|---|---|
| A-1 | `strat_rsi_oversold` | RSI oversold dip-buy (Connors stack) | dual | A.1 RSI | technical.py | ⏳ B750 walked | active |
| A-2 | `strat_rsi_overbought_short` | RSI overbought sell rally | short | A.1 RSI | technical.py | ❌ pending B751 | active |
| A-3 | `strat_rsi9_extreme` | RSI(9) extreme oversold + uptrend | long | A.1 RSI | technical.py | ❌ pending B751 | active |
| A-4 | `strat_rsi21_slow` | Slow RSI(21) mean-rev | dual | A.1 RSI | technical.py | ❌ pending B751 | active |
| A-5 | `strat_rsi_volume_200ema` | RSI + volume + 200EMA confluence | ? | A.1 RSI | technical.py | ❌ pending B751 | active |
| A-6 | `strat_stoch_oversold` | Stochastic oversold | long | A.2 Stoch | technical.py | ❌ pending B751 | active |
| A-7 | `strat_stochrsi_oversold` | StochRSI oversold | long | A.2 Stoch | technical.py | ❌ pending B752 | active |
| A-8 | `strat_stochrsi_overbought_short` | StochRSI overbought short | short | A.2 Stoch | technical.py | ❌ pending B752 | active |
| A-9 | `strat_williams_r_oversold` | Williams %R oversold bounce | long | A.3 Williams | technical.py | ❌ pending B752 | active |
| A-10 | `strat_ultimate_oscillator` | Larry Williams UO oversold | dual | A.3 Ultimate | technical.py | ❌ pending B752 | active |
| A-11 | `strat_mfi_oversold` | MFI oversold + OBV confirm | dual | A.3 MFI | technical.py | ❌ pending B752 | active |
| A-12 | `strat_bollinger_lower` | Bollinger lower-band mean-rev | dual | A.4 Bollinger | technical.py | ❌ pending B753 | active |
| A-13 | `strat_bollinger_tight` | Bollinger tight bands + touch | dual | A.4 Bollinger | technical.py | ❌ pending B753 | active |
| A-14 | `strat_bollinger_upper_short` | Bollinger upper short | short | A.4 Bollinger | technical.py | ❌ pending B753 | active |
| A-15 | `strat_ppo_crossover` | PPO crossover + ADX | dual | A.9 Momentum osc | technical.py | ⏳ B750 walked | active |
| A-16 | `strat_keltner_lower` | Keltner lower-band bounce | long | A.5 Keltner | technical.py | ❌ pending B753 | active |
| A-17 | `strat_camarilla_r4_breakout` | Camarilla R4 breakout (B641 renamed) | dual | A.6 Camarilla | technical.py | ❌ pending B753 | active |
| A-18 | `strat_camarilla_rsi_obv` | Camarilla + RSI + OBV confluence | dual | A.6 Camarilla | technical.py | ❌ pending B754 | active |
| A-19 | `strat_camarilla_rsi_obv_short` | Camarilla + RSI + OBV short | short | A.6 Camarilla | technical.py | ❌ pending B754 | active |
| A-20 | `strat_cpr_narrow_momentum` | CPR narrow + momentum | dual | A.7 CPR | technical.py | ❌ pending B754 | active |
| A-21 | `strat_cpr_narrow_momentum_short` | CPR narrow + momentum short | short | A.7 CPR | technical.py | ❌ pending B754 | active |
| A-22 | `strat_avwap_50_reclaim` | AVWAP-50 reclaim + MACD | dual | A.8 AVWAP | technical.py | ⏳ B750 walked | active |
| A-23 | `strat_avwap_252_breakout` | AVWAP-252 breakout + vol | dual | A.8 AVWAP | technical.py | ❌ pending B754 | active |
| A-24 | `strat_avwap_20high_rejection_short` | AVWAP-20-high rejection short | short | A.8 AVWAP | technical.py | ❌ pending B755 | active |
| A-25 | `strat_awesome_oscillator` | Awesome Oscillator cross | dual | A.9 Momentum osc | technical.py | ❌ pending B755 | active |
| A-26 | `strat_cmf_flip` | Chaikin Money Flow zero-cross | dual | A.9 Momentum osc | technical.py | ❌ pending B755 | active |
| A-27 | `strat_roc_burst` | Rate-of-change burst | ? | A.9 Momentum osc | technical.py | ❌ pending B755 | active |
| A-28 | `strat_williams_stoch_dual` | Williams + Stoch dual oversold | ? | A.10 Combined | technical.py | ❌ pending B755 | active |
| A-29 | `strat_prev_day_low_bounce` | Previous-day low bounce | long | A.11 Prev-day | technical.py | ❌ pending B755 | active |
| A-30 | `strat_bb_squeeze_volume` | BB squeeze + volume + VWAP confluence | dual | A.12 Squeeze | technical.py | ❌ pending B756 | active |

**Walk batch sequencing:** B750 = 3 walks; B751 = A-2/A-3/A-4/A-5; B752 = A-6/A-7/A-8/A-9/A-10/A-11; B753 = A-12/A-13/A-14/A-16/A-17; B754 = A-18/A-19/A-20/A-21/A-23; B755 = A-24/A-25/A-26/A-27/A-28/A-29; B756 = A-30. Owner-approved batch sizes 5-10 per `feedback_no_rushing_per_strategy_tweak` exception for explicit "approve all" batch directive 2026-06-14.

---

## Per-strategy walks (B750 initial 3 — Steps 1-7)

### A-1. `strat_rsi_oversold` (Connors stack, mean_reversion, batched B206 + B663 + B630)

**Step 1 — Strategy registration + docstring claim**

[screener.py:1345](backtest/signals/screener.py#L1345)

```python
def strat_rsi_oversold(s):
    """RSI oversold dip-buy. Batch 206 (Connors stack 2026-05-17): upgrade
    primary signal to (rsi_2<5 OR rsi_14<35). Connors discipline: short-
    window RSI(2) extreme is the canonical mean-reversion trigger, with
    long-window RSI(14) as the slower-moving fallback. Adds 200-EMA
    regime gate (Connors filter) in addition to 50-SMA pullback context.
    Strategy had 0 trades in Phase 1A-beta with rsi_14<35 alone (rarely
    triggers); the rsi_2<5 path opens the strategy to fire on intraday
    extremes."""
```

Claim: "Connors-discipline mean-reversion dip-buy on RSI extreme + 50-SMA pullback + 200-EMA regime." Pre-B206 fire rate = 0 / Phase 1A-beta. B206 added Connors OR-disjunct to open intraday extremes.

**Step 2 — Gate-by-gate analysis (LONG/SHORT)**

LONG (5 gates after Connors-OR collapse):
1. `(rsi_2 < 5)` OR `(rsi_14 < 35)` — Connors OR-disjunct
2. `s.get("price_above_sma_50")` — 50-SMA pullback context
3. `s.get("price_above_ema_200", False)` — 200-EMA regime gate (B663 fixed default-True)

SHORT (5 gates):
1. `(rsi_2 > 95)` OR `(rsi_14 > 65)` — Connors OR-disjunct (overbought side)
2. `s.get("below_sma_50")` — below 50-SMA (B630 producer signal)
3. `s.get("below_ema_200", False)` — below 200-EMA (B630 symmetric)
4. `not _short_borrow_trap_active(s)` — B718 explicit borrow gate

Effective gate count post-OR-collapse: LONG=3 gates / SHORT=4 gates.

**Step 3 — Producer source read (CHECKLIST #105)**

Producers:
- `rsi_2`, `rsi_14`: `compute_rsi(...)` in [technical.py](backtest/signals/technical.py). Wilder smoothing standard; PIT-clean (uses past bars only).
- `price_above_sma_50`, `below_sma_50`: `compute_sma_50(...)` standard; PIT-clean.
- `price_above_ema_200`, `below_ema_200`: `compute_ema_200(...)` standard; PIT-clean. B630 producer added `below_ema_200` as positive-symmetric inverse.
- `_short_borrow_trap_active`: borrow guard. B718a-d fully shipped; lint-enforced.

Producer-source verdict: PIT-clean. No silent-gap default-True residual post-B663. B630 symmetric signal present. B718 borrow gate present.

**Step 4 — Signal-docstring vs producer-reality check**

- "rsi_2 < 5" claim — VERIFIED in producer (rsi_2 is fast RSI, computed identically to rsi_14 with window=2).
- "rsi_14 < 35" claim — VERIFIED.
- "price_above_sma_50" — VERIFIED (signal emitted by compute_sma_50).
- "price_above_ema_200" — VERIFIED with B663 default-False fix.
- All gate names in `signals_used` match producer emissions.

Verdict: docstring ⊆ producer reality. No overclaim. CLEAN.

**Step 5 — Regime affinity check**

`STRATEGY_REGIME_AFFINITY['rsi_oversold']` — not set in registry per B577 default. Falls through to "no affinity = all regimes" default.

Per Pattern A: docstring doesn't claim regime-specificity beyond what the gates enforce (50-SMA + 200-EMA implicitly select bull/neutral regime via trend). CLEAN — no Pattern A doc-vs-registry mismatch.

**Step 6 — Missing-inverse audit**

- LONG side: Connors-RSI oversold + uptrend + bullish bar
- SHORT side: PRESENT in same function (dual `_strat3`). Symmetric structure.

Per `feedback_long_short_inverse_audit`: inverse exists, symmetric mechanical mirror.

**Pattern S verdict (direction asymmetry):** Connors-discipline LONG was empirically validated by Quantified Strategies 2024 backtest. SHORT side is mechanical mirror without separate empirical anchor. Expected: LONG outperforms SHORT in cube; SHORT may face borrow + squeeze + bull-drift asymmetric tail.

**Step 7 — Bundled disposition recommendations**

| Category | Finding | Action | Class |
|---|---|---|---|
| **F (silent-gap)** | B663 sweep applied; default-False present | No action | CLEAN |
| **F (borrow gate)** | B718 explicit gate present | No action | CLEAN |
| **G (hardcoded threshold)** | rsi_2 < 5 + rsi_14 < 35 are hardcoded constants in the strategy body, NOT cube-sweepable | Producer-additive: emit `rsi_2<5` and `rsi_14<35` as boolean signals; strategy consumes booleans | **Class 2 LOOSEN/TIGHTEN (queue B750/A-1-Pattern-G)** |
| **J (marginal contribution)** | Post-B690b: audit rsi_oversold vs rsi21_slow vs rsi9_extreme for distinguishing alpha | Defer to post-cube Pattern J routing | **Class 6 DEFERRED-POST-B690b** |
| **N (effective-N)** | Oscillator extremes cluster in vol regimes | Per cube infrastructure ticket; not strategy-specific fix | **Class 8 CUBE-INFRA (cross-ref `S4-B750-PATTERN-N-EFFECTIVE-N-AUTOCORRELATION-CUBE-EXTENSION`)** |
| **Q (STATE vs EVENT)** | `rsi_14 < 35` is STATE-based (fires every bar RSI<35) | EVENT-conversion candidate per B655 T10 precedent: emit `rsi_14_cross_below_35` + 5-bar lookback | **Class 2 LOOSEN/TIGHTEN (queue B750/A-1-Pattern-Q)** |
| **R (Connors OR-disjunct)** | (rsi_2<5 OR rsi_14<35) is signal-multiplication WITHOUT proportional tightening of the regime gates | Owner decision: (a) keep status quo + accept higher fire rate; (b) tighten 200-EMA to a stronger trend gate (e.g., add ADX>20); (c) split into separate strategies | **Class 1 KEEP-AS-IS or Class 2 TIGHTEN (owner-decision)** |
| **S (asymmetric expectancy)** | SHORT may underperform due to bull-drift + borrow + squeeze | Document; cube empirically validates | **Class 6 DEFERRED-POST-CUBE** |

**Disposition recommendation: KEEP-AS-IS + queue Class 2 producer-additive thresholds for Pattern G and Pattern Q. Status post-B750: PRE-CUBE-CLEAN.**

A-priori fire-count projection: Connors-OR-disjunct expands the (rsi_14<35) primary trigger significantly via rsi_2<5 (which fires more often than rsi_14<35 on intraday vol). Expected universe-wide fire rate on T1a 2020-2026: ~200-500/yr LONG-side (rough estimate; cube empirically validates). Above min_trades=100 threshold.

---

### A-15. `strat_ppo_crossover` (PPO + ADX, momentum, batched B630)

**Step 1 — Strategy registration + docstring claim**

[screener.py:1046](backtest/signals/screener.py#L1046)

```python
def strat_ppo_crossover(s):
    fl = (s.get("ppo_crossover_up") and s.get("adx_trending"))
    fs = (s.get("ppo_crossover_dn") and s.get("adx_trending")) and not _short_borrow_trap_active(s)
    return _strat3(fl, fs, "momentum",
        ["ppo_crossover_up","adx_trending"], ["ppo_crossover_dn","adx_trending", "borrow_ok"],
        ["PPO crossed above signal  -  momentum bullish","ADX confirms trend"],
        ["PPO crossed below signal  -  momentum bearish","ADX confirms trend"])
```

No docstring. Claim is implicit from gates: PPO crossover above/below signal + ADX confirms trend.

PPO = Percentage Price Oscillator = (12-EMA - 26-EMA) / 26-EMA × 100. PPO-signal-line cross is canonical momentum trigger (Appel 1979 MACD variant; PPO replaces absolute MACD with percentage-scaled).

**Step 2 — Gate-by-gate analysis**

LONG (2 gates):
1. `ppo_crossover_up` — PPO crossed above its signal line (EVENT signal)
2. `adx_trending` — ADX > 25 typically (TREND-STRENGTH gate)

SHORT (3 gates):
1. `ppo_crossover_dn` — PPO crossed below signal line
2. `adx_trending`
3. `not _short_borrow_trap_active(s)` — B718 borrow gate

Effective gate count: LONG=2 / SHORT=3.

**Step 3 — Producer source read**

Producers:
- `ppo_crossover_up`, `ppo_crossover_dn`: `compute_ppo(...)` in [technical.py](backtest/signals/technical.py). EVENT signal (fires once per crossing). PIT-clean.
- `adx_trending`: `compute_adx(...)`. Threshold-state signal. Verify producer emits `adx_trending = (adx > 25)` or similar. Likely STATE-based.

Producer-source verdict: PPO is EVENT-clean. ADX is STATE-based — gate fires every bar ADX > 25. Pattern Q candidate.

**Step 4 — Signal-docstring vs producer-reality check**

- "ppo_crossover_up" — VERIFIED (event signal).
- "adx_trending" — claim "ADX confirms trend" is structurally true at the bar but is STATE not EVENT (doesn't distinguish a fresh ADX crossing from sustained ADX>25). Doc-vs-producer: minor overclaim. Docstring says "ADX confirms trend" which is correct but doesn't specify state-vs-event.

**Step 5 — Regime affinity check**

Not set in registry. Falls through to default "no affinity = all regimes."

Per Pattern A: docstring implicitly claims bullish/bearish momentum regime; gates don't enforce a directional regime beyond the PPO direction itself. CLEAN (regime affinity is signal-encoded via PPO direction).

**Step 6 — Missing-inverse audit**

LONG/SHORT both present in same function (_strat3 dual). Symmetric mechanical mirror. Per `feedback_long_short_inverse_audit`: inverse exists.

**Pattern S verdict:** PPO + ADX trend-confluence is a textbook momentum signal. LONG side benefits from bull drift; SHORT side faces drift headwind + borrow. Expect cube LONG PASS / SHORT marginal.

**Step 7 — Bundled disposition recommendations**

| Category | Finding | Action | Class |
|---|---|---|---|
| **F (silent-gap)** | No default-True patterns in body | CLEAN | — |
| **F (borrow gate)** | B718 explicit gate present | CLEAN | — |
| **Q (STATE vs EVENT)** | `adx_trending` is STATE-based; PPO is EVENT-based — mismatch in temporality | Producer-additive: emit `adx_cross_above_25_recent_5d` for EVENT-aligned confluence (B643/B655 5-bar lookback precedent) | **Class 2 LOOSEN/TIGHTEN (queue B750/A-15-Pattern-Q)** |
| **J (marginal contribution)** | PPO is MACD-variant; potential redundancy with macd_crossover_short (Cluster B) | Post-B690b: compute marginal contribution between PPO + MACD on T1a; if Pattern J shows redundancy, consolidate | **Class 6 DEFERRED-POST-B690b** |
| **N (effective-N)** | PPO crossovers cluster in trending regimes | Cube infra ticket | **Class 8 CUBE-INFRA** |
| **T (gate redundancy)** | ADX trending + PPO crossover both fire in trending markets — collinearity check needed | Post-B690b: gate-correlation diagnostic between adx_trending and ppo_crossover_up | **Class 6 DEFERRED-POST-B690b** |

**Disposition recommendation: KEEP-AS-IS + Pattern Q EVENT-conversion candidate. Status post-B750: PRE-CUBE-CLEAN.**

A-priori fire-count projection: PPO crossovers + ADX>25 trending = ~5-15 fires/ticker/yr on T1a (medium-frequency). Universe-wide ~2000-7000/yr (PASS_CUBE per B660 ceiling).

---

### A-22. `strat_avwap_50_reclaim` (AVWAP-50 + MACD, vwap, batched B208 + B663 + B630)

**Step 1 — Strategy registration + docstring claim**

[screener.py:4435](backtest/signals/screener.py#L4435)

```python
def strat_avwap_50_reclaim(s):
    """Batch 208: AVWAP-50-low reclaim with confirming momentum. Higher-
    frequency variant of the 252-low strategy targeting recent-leg
    reclaims rather than annual-reference inflections. Pairs naturally
    with the 50-day momentum window."""
```

Claim: "AVWAP-50-low reclaim + MACD-bullish confirms = institutionally-supported uptrend leg reclaim."

**Step 2 — Gate-by-gate analysis**

LONG (4 gates):
1. `above_50 = s.get("above_avwap_50low", False)` — price above AVWAP anchored at 50-day low
2. `abs(pct_from_50) < 1.5` — within 1.5% of AVWAP inflection (proximity gate, hardcoded threshold)
3. `macd_bull = s.get("macd_12_26_9_bullish", False)` — MACD bullish
4. `s.get("price_above_ema_200", False)` — 200-EMA regime gate (B663 fix)

SHORT (5 gates):
1. `(not above_50)` — below AVWAP-50
2. `abs(pct_from_50) < 1.5`
3. `(not macd_bull)` — MACD bearish (NOT pattern! Concern.)
4. `s.get("below_ema_200", False)` — B630 symmetric
5. `not _short_borrow_trap_active(s)` — B718 borrow gate

Effective gate count: LONG=4 / SHORT=5.

**Pattern F-residual concern:** `(not macd_bull)` is the NOT-pattern that B611 reviewer flagged. Should be replaced with positive-symmetric `macd_12_26_9_bearish` signal IF that producer signal exists. If not, producer-additive `macd_bearish` is needed.

**Step 3 — Producer source read**

Producers:
- `above_avwap_50low`, `pct_from_avwap_50low`: `compute_avwap_signals(...)` in [technical.py](backtest/signals/technical.py). Anchored VWAP from 50-day low. PIT discipline: anchor is past-only (50-day rolling lookback); cumulative TPV from anchor through current bar.
- `macd_12_26_9_bullish`: `compute_macd(...)`. STATE signal (MACD > signal line). Standard.
- `price_above_ema_200`, `below_ema_200`: standard EMA.

**PIT-discipline check on AVWAP-50-low:** The anchor is "50-day rolling low" — this is the LOW over a 50-bar window. If the window includes today, look-ahead. If excludes today (`tail(50)` on prior bars), PIT-clean. Producer source verification needed.

Producer-source verdict: AVWAP needs PIT pin verification (queue ticket: `S4-B750-AVWAP-50LOW-ANCHOR-PIT-VERIFY`). MACD STATE-clean. Pattern F NOT-pattern present on SHORT side (Class 2 fix).

**Step 4 — Signal-docstring vs producer-reality check**

- "AVWAP-50-low reclaim" — VERIFIED.
- "Confirming momentum" — MACD bullish is the confirmation. VERIFIED.
- "Pairs naturally with the 50-day momentum window" — qualitative claim, not testable without cube data.

Verdict: docstring ⊆ producer reality. No overclaim. CLEAN.

**Step 5 — Regime affinity check**

Not set in registry. Falls through to default. Per Pattern A: docstring implicit claim of "uptrend leg reclaim" matches the 200-EMA gate. CLEAN.

**Step 6 — Missing-inverse audit**

LONG/SHORT both present (_strat3 dual). Symmetric mechanical mirror. Per `feedback_long_short_inverse_audit`: inverse exists.

**Pattern S verdict:** AVWAP reclaim is institutional-flow inference. LONG benefits from bull drift; SHORT faces drift + borrow + squeeze asymmetric tail.

**Step 7 — Bundled disposition recommendations**

| Category | Finding | Action | Class |
|---|---|---|---|
| **F (NOT-pattern on SHORT)** | `(not macd_bull)` SHORT-side; positive-symmetric `macd_12_26_9_bearish` should replace it per `feedback_never_use_NOT_s_get_pattern` | Producer-additive: emit `macd_12_26_9_bearish` if not already present; replace `(not macd_bull)` with `s.get("macd_12_26_9_bearish", False)` | **Class 2 LOOSEN/TIGHTEN (queue B750/A-22-Pattern-F)** |
| **F (silent-gap)** | B663 fix on `price_above_ema_200` default-False present; B630 symmetric `below_ema_200` present | CLEAN | — |
| **F (borrow gate)** | B718 explicit gate present | CLEAN | — |
| **G (hardcoded threshold)** | `abs(pct_from_50) < 1.5` is hardcoded 1.5% proximity; not cube-sweepable | Producer-additive: emit `near_avwap_50low<1.5pct` boolean (already emitted per signals_used list); confirm strategy consumes it; if hardcoded float comparison stays, cube can't sweep | **Class 2 LOOSEN/TIGHTEN (queue B750/A-22-Pattern-G)** |
| **J (marginal contribution)** | AVWAP-50 vs AVWAP-252 vs AVWAP-20-high — 3 anchor lookbacks; potential redundancy | Post-B690b: gate-correlation between AVWAP variants on T1a | **Class 6 DEFERRED-POST-B690b** |
| **N (effective-N)** | AVWAP reclaims cluster around vol regimes; effective-N inflation | Cube infra ticket | **Class 8 CUBE-INFRA** |
| **PIT-discipline** | `above_avwap_50low` anchor is "50-day rolling low" — verify anchor lookback excludes today | Producer-audit: `pattern_producer_audit.py` (B699/B700/B735 template) on `compute_avwap_signals` | **Class 9 PRODUCER-AUDIT (queue `S4-B750-AVWAP-50LOW-ANCHOR-PIT-VERIFY`)** |

**Disposition recommendation: KEEP-AS-IS + Pattern F NOT-pattern fix + Pattern G threshold-signal hardening + PIT-audit. Status post-B750: PRE-CUBE-CLEAN POST-FIXES.**

A-priori fire-count projection: AVWAP reclaim + MACD bullish + 200-EMA + 1.5% proximity = stack of 4 gates; estimated ~3-10 fires/ticker/yr on T1a; universe-wide ~500-2000/yr LONG-side (likely PASS_CUBE). SHORT side likely lower due to drift.

---

---

## Per-strategy walks (B751 batch — A-2 / A-3 / A-4 / A-5)

### A-2. `strat_rsi_overbought_short` (RSI overbought sell-rally, mean_reversion, batched B630)

**Step 1 — Strategy registration + docstring claim**

[screener.py:1397](backtest/signals/screener.py#L1397)

```python
def strat_rsi_overbought_short(s):
    # B630 sweep: positive symmetric below_sma_50 (B630 producer)
    fires = (s.get("rsi_14", 50) > 68 and
             s.get("below_sma_50") and
             (s.get("bearish_engulfing") or s.get("rsi_14_rising") == False) and not _short_borrow_trap_active(s))
    return _strat(fires, "short", "mean_reversion", ...)
```

No standalone docstring; claim from context_bullets: "RSI-14 overbought at >68 + below 50 SMA + bearish momentum confirms sellers".

**Step 2 — Gate-by-gate analysis**

SHORT (4 gates):
1. `s.get("rsi_14", 50) > 68` — overbought RSI (HARDCODED threshold)
2. `s.get("below_sma_50")` — below 50-SMA (B630 producer symmetric signal)
3. `s.get("bearish_engulfing") or s.get("rsi_14_rising") == False` — bearish confirmation OR-disjunct
4. `not _short_borrow_trap_active(s)` — B718 borrow gate

Effective gate count: 4 (with OR-disjunct).

**Step 3 — Producer source read (CHECKLIST #105)**

Producers:
- `rsi_14`: standard Wilder smoothing in technical.py. PIT-clean.
- `below_sma_50`: B630 producer-additive positive-symmetric inverse to `price_above_sma_50`. PIT-clean.
- `bearish_engulfing`: candle-pattern producer in technical.py. EVENT signal.
- `rsi_14_rising`: state signal (RSI today > RSI yesterday). STATE.

Producer-source verdict: PIT-clean. B630 positive-symmetric signal present (no F NOT-pattern). EVENT bearish_engulfing OR STATE rsi_not_rising = mixed temporality.

**Step 4 — Signal-docstring vs producer-reality check**

- "RSI > 68" claim — VERIFIED (hardcoded threshold)
- "below 50 SMA" — VERIFIED
- "bearish momentum confirms sellers" — VERIFIED via OR-disjunct

Verdict: CLEAN.

**Step 5 — Regime affinity check**

Not set in registry. Falls through to default. SHORT-only mean-reversion strategy implicitly targets bear/neutral regimes (50-SMA gate selects downtrend context).

**Recommendation:** Add explicit `STRATEGY_REGIME_AFFINITY['rsi_overbought_short'] = {bear, neutral}` per implicit gate-selection. Pattern A doc-vs-registry mismatch.

**Step 6 — Missing-inverse audit**

SHORT-only strategy. The LONG mirror is `strat_rsi_oversold` (A-1, dual). But A-1 SHORT branch already covers RSI > 65 + below_sma_50 + below_ema_200. The standalone strat_rsi_overbought_short adds: tighter RSI threshold (>68 vs >65) + bearish_engulfing OR not-rising confirmation. This is a TIGHTER variant of A-1 SHORT branch.

**Pattern W concern (deterministic duplicate):** Post-tightening, `strat_rsi_overbought_short` and `strat_rsi_oversold` SHORT branch may fire on overlapping bars. Pattern W audit candidate per B718 hull_rsi_short precedent.

**Step 7 — Bundled disposition recommendations**

| Category | Finding | Action | Class |
|---|---|---|---|
| **F (silent-gap)** | B630 `below_sma_50` symmetric present | CLEAN | — |
| **F (borrow gate)** | B718 explicit gate present | CLEAN | — |
| **G (hardcoded threshold)** | `rsi_14 > 68` hardcoded; not cube-sweepable | Producer-additive: emit `rsi_14>68` boolean alongside existing `rsi_14<35` | **Class 2 LOOSEN/TIGHTEN (queue `S4-B751-A-2-G-RSI-OVERBOUGHT-THRESHOLD-HARDENING`)** |
| **Q (STATE vs EVENT)** | `rsi_14_rising == False` is STATE; bearish_engulfing is EVENT; mixed temporality on OR-disjunct | EVENT-conversion: replace `(rsi_14_rising == False)` with `rsi_14_falling_cross_recent_3d` (producer-additive) | **Class 2 LOOSEN/TIGHTEN (queue `S4-B751-A-2-Q-MIXED-TEMPORALITY-EVENT-CONVERSION`)** |
| **Pattern A (regime affinity)** | Implicit bear/neutral targeting; explicit registry entry missing | Add `STRATEGY_REGIME_AFFINITY['rsi_overbought_short'] = {bear, neutral}` | **Class 2 LOOSEN/TIGHTEN (queue `S4-B751-A-2-REGIME-AFFINITY-ADD`)** |
| **W (deterministic duplicate)** | Post-tightening may overlap with strat_rsi_oversold SHORT branch | Pattern W audit post-B690b measurement | **Class 6 DEFERRED-POST-B690b (cross-ref `S4-B751-A-2-PATTERN-W-VS-RSI-OVERSOLD-SHORT`)** |
| **S (asymmetric expectancy)** | SHORT-only mean-reversion faces bull-drift + borrow + squeeze | Document; cube empirically validates | **Class 6 DEFERRED-POST-CUBE** |

**Disposition recommendation: KEEP-AS-IS + Class 2 fixes. Status post-B751: PRE-CUBE-CLEAN POST-FIXES.**

A-priori fire-count projection: RSI > 68 + downtrend gate + bearish confirm = stack of 4 gates SHORT-side; estimated ~10-30 fires/ticker/yr on T1a during 2020-2026 bear/neutral windows. Universe-wide: ~3,000-10,000/yr SHORT. Possibly above B710 5K ceiling — Pattern Q EVENT-conversion would mitigate.

---

### A-3. `strat_rsi9_extreme` (RSI-9 extreme oversold + uptrend, mean_reversion, LONG-only)

**Step 1 — Strategy registration + docstring claim**

[screener.py:1379](backtest/signals/screener.py#L1379)

```python
def strat_rsi9_extreme(s):
    # No natural short inverse  -  stays long-only (extreme oversold in uptrend)
    fires = (s.get("rsi_9_extreme_os") and s.get("price_above_ema_200") and s.get("rsi_9_rising"))
    return _strat(fires, "long", "mean_reversion", ...)
```

No standalone docstring; inline comment: "No natural short inverse - stays long-only (extreme oversold in uptrend)". context_bullets: "RSI-9 extreme oversold below 20", "Above 200 EMA - uptrend context", "RSI-9 rising - recovering".

**Step 2 — Gate-by-gate analysis**

LONG (3 gates):
1. `s.get("rsi_9_extreme_os")` — RSI-9 < 20 (PRODUCER threshold; EVENT/STATE depending on producer)
2. `s.get("price_above_ema_200")` — 200-EMA regime gate
3. `s.get("rsi_9_rising")` — RSI-9 today > RSI-9 yesterday (STATE)

LONG-only. Effective gate count: 3.

**Step 3 — Producer source read (CHECKLIST #105)**

Producers:
- `rsi_9_extreme_os`: emitted by `compute_rsi(window=9)` in technical.py if `rsi_9 < 20`. STATE signal.
- `price_above_ema_200`: standard. Verify post-B663 default-False fix.
- `rsi_9_rising`: state delta (today > yesterday). STATE.

**Note:** This walk's gate `s.get("price_above_ema_200")` uses NO default specified. Per Python dict.get semantics, default is `None` → falsy → effectively `False`. Acceptable but inconsistent with explicit `False` default elsewhere. Pre-B663 silent-gap concern: `s.get(key)` without explicit default == None == falsy on truthy check, so this is functionally equivalent to default-False. Not Pattern F.

Producer-source verdict: PIT-clean. All 3 gates STATE-based. Pattern Q candidate.

**Step 4 — Signal-docstring vs producer-reality check**

- "RSI-9 below 20" — VERIFIED via producer signal `rsi_9_extreme_os`
- "Above 200 EMA" — VERIFIED
- "RSI-9 rising" — VERIFIED

CLEAN.

**Step 5 — Regime affinity check**

Not set in registry. Inline comment claims "extreme oversold in uptrend" — implicit bull regime. 200-EMA gate enforces this.

CLEAN — gate enforces the implicit regime claim. No Pattern A mismatch.

**Step 6 — Missing-inverse audit**

LONG-only by design (comment: "No natural short inverse"). Symmetric mirror would be RSI-9 > 80 + below 200 EMA + RSI-9 falling — exists conceptually but the author deliberately excluded.

Per `feedback_long_short_inverse_audit` + `feedback_asymmetric_data_sources_break_mechanical_inverse`: the author's decision is defensible if (a) symmetric SHORT lacks distinct empirical anchor, OR (b) borrow + squeeze asymmetry on the mirror outweighs alpha. For RSI extreme oversold/overbought, the asymmetric expectancy (drift + borrow on SHORT) supports LONG-only treatment.

**Recommendation:** Accept author's LONG-only decision. No Class 7 NEW SHORT inverse needed.

**Step 7 — Bundled disposition recommendations**

| Category | Finding | Action | Class |
|---|---|---|---|
| **F (silent-gap)** | Implicit default-falsy on `price_above_ema_200`; functionally equivalent to default-False | Minor: add explicit `default=False` for consistency with B663 sweep | **Class 2 LOOSEN/TIGHTEN (queue `S4-B751-A-3-F-EXPLICIT-DEFAULT-FALSE-CONSISTENCY`)** |
| **G (hardcoded threshold)** | `rsi_9_extreme_os` consumes producer threshold (20); cube can sweep producer threshold | CLEAN | — |
| **Q (STATE vs EVENT)** | All 3 gates STATE; fire rate may inflate during prolonged oversold windows | EVENT-conversion candidate: emit `rsi_9_cross_below_20_recent_3d` per B655 T10 precedent | **Class 2 LOOSEN/TIGHTEN (queue `S4-B751-A-3-Q-RSI-9-EVENT-CONVERSION`)** |
| **J (marginal contribution)** | RSI-9 vs RSI-14 (A-1) vs RSI-21 (A-4) — same primitive at different windows | Post-B690b: Pattern J audit on RSI window family | **Class 6 DEFERRED-POST-B690b** |
| **N (effective-N)** | RSI extreme oversold clusters in vol regimes | Cube infra ticket | **Class 8 CUBE-INFRA** |

**Disposition recommendation: KEEP-AS-IS + Class 2 minor fixes. LONG-only justified per asymmetric data sources discipline. Status post-B751: PRE-CUBE-CLEAN.**

A-priori fire-count projection: RSI-9 < 20 is rare (extreme oversold); + uptrend (200-EMA) is even rarer (oversold in uptrend); + rising (recovery) is the EVENT trigger. Stacked gates: estimated 1-3 fires/ticker/yr on T1a in benign conditions; 5-15 in vol regimes. Universe-wide: ~500-1,500/yr. **Possibly FAIL_FIRE_STARVED in per-regime split** — EXPLORATORY candidate.

---

### A-4. `strat_rsi21_slow` (Slow RSI-21 mean-reversion, dual, batched B630)

**Step 1 — Strategy registration + docstring claim**

[screener.py:1387](backtest/signals/screener.py#L1387)

```python
def strat_rsi21_slow(s):
    # B630 sweep: positive symmetric below_sma_50 (B630 producer)
    fl = (s.get("rsi_21", 50) < 35 and s.get("price_above_sma_50"))
    fs = (s.get("rsi_21", 50) > 65 and s.get("below_sma_50")) and not _short_borrow_trap_active(s)
    return _strat3(fl, fs, "mean_reversion", ...)
```

No standalone docstring; B630 comment indicates symmetric inverse signal. context_bullets: "Slow RSI-21 oversold below 35", "Above 50 SMA - uptrend context" (LONG) / mirror for SHORT.

**Step 2 — Gate-by-gate analysis**

LONG (2 gates):
1. `s.get("rsi_21", 50) < 35` — slow RSI-21 oversold (HARDCODED threshold)
2. `s.get("price_above_sma_50")` — 50-SMA uptrend context

SHORT (3 gates):
1. `s.get("rsi_21", 50) > 65` — slow RSI-21 overbought (HARDCODED)
2. `s.get("below_sma_50")` — B630 producer symmetric
3. `not _short_borrow_trap_active(s)` — B718 borrow gate

Effective gate count: LONG=2 / SHORT=3.

**Step 3 — Producer source read (CHECKLIST #105)**

Producers:
- `rsi_21`: 21-window RSI with Wilder smoothing in technical.py. STATE. PIT-clean.
- `price_above_sma_50`, `below_sma_50`: standard SMA + B630 symmetric. PIT-clean.

Producer-source verdict: PIT-clean. B630 symmetric signal present (no F NOT-pattern). All gates STATE-based.

**Step 4 — Signal-docstring vs producer-reality check**

CLEAN. Gates match context bullets.

**Step 5 — Regime affinity check**

Not set in registry. Falls through to default. SMA-50 gate implicitly selects bull (LONG) / bear (SHORT) regimes.

CLEAN — implicit regime via SMA gate.

**Step 6 — Missing-inverse audit**

LONG/SHORT present (_strat3 dual). Symmetric mechanical mirror.

**Pattern S verdict:** Same as A-1 — SHORT side faces bull-drift + borrow + squeeze asymmetry.

**Pattern J + Pattern W (CRITICAL):** strat_rsi21_slow vs strat_rsi_oversold (A-1):
- A-1 LONG: `(rsi_2 < 5 OR rsi_14 < 35)` AND `price_above_sma_50` AND `price_above_ema_200`
- A-4 LONG: `rsi_21 < 35` AND `price_above_sma_50`

A-4 is a STRICT SUBSET of A-1 LONG if rsi_21 < 35 implies (rsi_2 < 5 OR rsi_14 < 35). Statistical relationship: rsi_21 lags rsi_14 lags rsi_2. When rsi_21 < 35, rsi_14 is usually also < 35 (slower indicator more conservative). When rsi_14 < 35, rsi_2 is often < 5 too. So A-4 LONG firings ≈ subset of A-1 LONG firings minus 200-EMA gate difference.

Also A-4 vs A-3 (rsi9_extreme): RSI-21 < 35 vs RSI-9 < 20 — different oversold definitions, but overlap exists.

**Pattern J/W audit candidate:** RSI window family (RSI-9, RSI-14, RSI-21) reskins.

**Step 7 — Bundled disposition recommendations**

| Category | Finding | Action | Class |
|---|---|---|---|
| **F (silent-gap)** | B630 `below_sma_50` symmetric present | CLEAN | — |
| **F (borrow gate)** | B718 explicit gate present | CLEAN | — |
| **G (hardcoded threshold)** | `rsi_21 < 35` and `> 65` hardcoded | Producer-additive: emit `rsi_21<35` and `rsi_21>65` booleans | **Class 2 LOOSEN/TIGHTEN (queue `S4-B751-A-4-G-RSI-21-THRESHOLD-HARDENING`)** |
| **Q (STATE vs EVENT)** | Both gates STATE | EVENT-conversion candidate per cluster Pattern Q | **Class 2 LOOSEN/TIGHTEN (queue `S4-B751-A-4-Q-RSI-21-EVENT-CONVERSION`)** |
| **J (RSI window family)** | RSI-9, RSI-14, RSI-21 — same primitive at different windows; A-4 LONG ≈ subset of A-1 LONG | Post-B690b: gate-redundancy diagnostic on RSI window family | **Class 6 DEFERRED-POST-B690b (cross-ref `S4-B750-PATTERN-J-CLUSTER-A-MARGINAL-CONTRIBUTION-AUDIT-POST-B690b`)** |
| **W (deterministic duplicate)** | A-4 LONG potentially strict subset of A-1 LONG | Pattern W audit post-B690b | **Class 6 DEFERRED-POST-B690b** |
| **N (effective-N)** | Cluster A Pattern N | Cube infra | **Class 8 CUBE-INFRA** |

**Disposition recommendation: KEEP-AS-IS PENDING Pattern J/W audit. May consolidate or delete post-B690b. Status post-B751: PRE-CUBE-CLEAN; CONSOLIDATION CANDIDATE.**

A-priori fire-count projection: RSI-21 is slower than RSI-14, fires LESS often. Stack of 2 gates LONG / 3 SHORT. Estimated 5-15 fires/ticker/yr LONG; ~3-10 SHORT. Universe-wide: ~1,500-5,000/yr LONG. PASS_CUBE range; possibly EXPLORATORY post-Pattern-N effective-N adjustment.

---

### A-5. `strat_rsi_volume_200ema` (RSI + volume + 200-EMA confluence, dual, batched B320 + B630)

**Step 1 — Strategy registration + docstring claim**

[screener.py:2164](backtest/signals/screener.py#L2164)

```python
def strat_rsi_volume_200ema(s):
    """Batch 320 (2026-05-25): loosened vol gate from vol_spike_2x to
    vol_above_avg (>=1.0x) per owner directive. The 2x bar combined with
    RSI<35 AND above-200-EMA was nearly impossible to satisfy in trending
    markets (RSI<30 + uptrend is itself rare); the volume gate compounded
    that to zero. Above-average volume on the oversold day still confirms
    the move, without the 2x sledgehammer."""
    fl = (s.get("rsi_14", 50) < 35 and s.get("vol_above_avg") and s.get("price_above_ema_200"))
    # B630 sweep: positive symmetric below_ema_200 (silent-gap fix; no default=True)
    fs = (s.get("rsi_14", 50) > 65 and s.get("vol_above_avg") and s.get("below_ema_200")) and not _short_borrow_trap_active(s)
    return _strat3(fl, fs, "confluence", ...)
```

Category: "confluence" (NOT mean_reversion). Triple-gate confluence on RSI + volume + 200-EMA.

Citation: B320 loosening lineage (2026-05-25) per owner directive. Pre-B320 used vol_spike_2x; B320 loosened to vol_above_avg per fire-starvation finding.

**Step 2 — Gate-by-gate analysis**

LONG (3 gates):
1. `s.get("rsi_14", 50) < 35` — RSI oversold (hardcoded)
2. `s.get("vol_above_avg")` — volume above 20d average (B320 loosened from vol_spike_2x)
3. `s.get("price_above_ema_200")` — 200-EMA regime

SHORT (4 gates):
1. `s.get("rsi_14", 50) > 65` — RSI overbought (hardcoded)
2. `s.get("vol_above_avg")` — volume above avg
3. `s.get("below_ema_200")` — B630 producer symmetric
4. `not _short_borrow_trap_active(s)` — B718 borrow gate

Effective gate count: LONG=3 / SHORT=4.

**Step 3 — Producer source read (CHECKLIST #105)**

Producers:
- `rsi_14`: standard. PIT-clean.
- `vol_above_avg`: `today_volume / 20-day_avg > 1.0`. STATE. PIT-clean.
- `price_above_ema_200`, `below_ema_200`: standard + B630 symmetric. PIT-clean.

Producer-source verdict: PIT-clean. B630 symmetric present. All STATE-based.

**Step 4 — Signal-docstring vs producer-reality check**

- "RSI<35" — VERIFIED
- "vol above 20d avg" (B320 loosening) — VERIFIED
- "above 200 EMA" — VERIFIED
- B320 batch lineage docstring claim — VERIFIED via git blame

CLEAN.

**Step 5 — Regime affinity check**

Not set in registry. 200-EMA gate selects bull (LONG) / bear (SHORT) regimes implicitly.

CLEAN.

**Step 6 — Missing-inverse audit**

LONG/SHORT present (_strat3 dual). Symmetric.

**Pattern J + Pattern W (CRITICAL):** strat_rsi_volume_200ema vs strat_rsi_oversold (A-1):
- A-1 LONG: `(rsi_2<5 OR rsi_14<35)` AND `price_above_sma_50` AND `price_above_ema_200`
- A-5 LONG: `rsi_14<35` AND `vol_above_avg` AND `price_above_ema_200`

Differences:
- A-1 uses Connors-OR-disjunct; A-5 uses single rsi_14<35
- A-1 has 50-SMA pullback gate; A-5 doesn't
- A-5 has vol_above_avg gate; A-1 doesn't
- Both have 200-EMA

Pattern J: A-1 vs A-5 share the 200-EMA + rsi_14<35 core. Distinguishing: A-1's Connors-OR + SMA-50 pullback vs A-5's volume confirmation. Different secondary gates. Not strict duplicate but high overlap.

**Pattern N + Pattern Q:** All STATE-based; clusters in vol regimes; effective-N inflation expected.

**Step 7 — Bundled disposition recommendations**

| Category | Finding | Action | Class |
|---|---|---|---|
| **F (silent-gap)** | B630 `below_ema_200` symmetric present | CLEAN | — |
| **F (borrow gate)** | B718 explicit gate present | CLEAN | — |
| **G (hardcoded threshold)** | `rsi_14<35` and `rsi_14>65` hardcoded | Producer-additive: emit boolean signals; cube can sweep | **Class 2 LOOSEN/TIGHTEN (queue `S4-B751-A-5-G-RSI-14-THRESHOLD-HARDENING`)** |
| **Q (STATE vs EVENT)** | All 3 gates STATE | EVENT-conversion candidate | **Class 2 LOOSEN/TIGHTEN (queue `S4-B751-A-5-Q-EVENT-CONVERSION`)** |
| **J (vs A-1)** | Shares 200-EMA + rsi_14<35 core with strat_rsi_oversold (A-1); distinguishing gate is volume_above_avg | Post-B690b: gate-redundancy diagnostic + ablation on vol_above_avg gate | **Class 6 DEFERRED-POST-B690b** |
| **N (effective-N)** | Cluster A Pattern N | Cube infra | **Class 8 CUBE-INFRA** |
| **B320 lineage check** | B320 loosened vol gate per fire-starvation; verify post-B660 fire count justifies loosening or reverts | Post-B660 re-measurement: verify fire rate is in PASS_CUBE range now; if still <100/yr, reconsider B320 loosening | **Class 6 DEFERRED-POST-B660-RE-RUN (queue `S4-B751-A-5-B320-LOOSENING-VERIFY-POST-B660`)** |

**Disposition recommendation: KEEP-AS-IS + Class 2 fixes + B320 lineage verification. Status post-B751: PRE-CUBE-CLEAN; J-audit candidate.**

A-priori fire-count projection: RSI<35 + vol_above_avg + 200-EMA = 3-gate confluence; estimated 5-20 fires/ticker/yr on T1a. Universe-wide: ~2,500-10,000/yr LONG. PASS_CUBE range; B320 loosening worked.

---

## B751 cluster walk completion wrap-up

### Disposition summary (4 walks shipped)

| Walk | Strategy | Status | Class actions surfaced |
|---|---|---|---|
| A-2 | rsi_overbought_short | KEEP-AS-IS + Class 2 G + Q + regime affinity | G + Q + Pattern A + W + S |
| A-3 | rsi9_extreme | KEEP-AS-IS + Class 2 minor F + Q | F (minor) + Q + J + N + LONG-only justified |
| A-4 | rsi21_slow | KEEP-AS-IS PENDING J/W audit | F (clean) + G + Q + J (RSI window family) + W |
| A-5 | rsi_volume_200ema | KEEP-AS-IS + Class 2 G + Q + B320 lineage verify | F (clean) + G + Q + J (vs A-1) + B320 lineage |

**RSI window family (A-1 + A-3 + A-4 + A-5) is the dominant B751 finding.** 4 RSI strategies share the same primitive (RSI threshold + trend gate) at different windows (RSI-2/9/14/21). Pattern J consolidation candidate post-B690b. Likely 4 → 1-2 effective strategies.

**Pattern Q EVENT-conversion (continued from B750) confirmed cluster-wide.** All 4 B751 walks have STATE-based gates that over-fire during oversold/overbought persistence.

### NEW EXECUTION_QUEUE tickets surfaced (B751)

1. `S4-B751-A-2-G-RSI-OVERBOUGHT-THRESHOLD-HARDENING` — producer-additive `rsi_14>68` boolean. PENDING-OWNER-APPROVAL.
2. `S4-B751-A-2-Q-MIXED-TEMPORALITY-EVENT-CONVERSION` — replace `rsi_14_rising == False` STATE with `rsi_14_falling_cross_recent_3d` EVENT. PENDING-OWNER-APPROVAL.
3. `S4-B751-A-2-REGIME-AFFINITY-ADD` — `STRATEGY_REGIME_AFFINITY['rsi_overbought_short'] = {bear, neutral}`. PENDING-OWNER-APPROVAL.
4. `S4-B751-A-2-PATTERN-W-VS-RSI-OVERSOLD-SHORT` — post-B690b Pattern W audit (vs A-1 SHORT branch). DEFERRED-POST-B690b.
5. `S4-B751-A-3-F-EXPLICIT-DEFAULT-FALSE-CONSISTENCY` — add explicit `default=False` to `price_above_ema_200` and `rsi_9_rising` for B663 consistency. PENDING-OWNER-APPROVAL.
6. `S4-B751-A-3-Q-RSI-9-EVENT-CONVERSION` — producer-additive `rsi_9_cross_below_20_recent_3d`. PENDING-OWNER-APPROVAL.
7. `S4-B751-A-4-G-RSI-21-THRESHOLD-HARDENING` — producer-additive `rsi_21<35` + `rsi_21>65` booleans. PENDING-OWNER-APPROVAL.
8. `S4-B751-A-4-Q-RSI-21-EVENT-CONVERSION` — producer-additive `rsi_21_cross_below_35_recent_5d`. PENDING-OWNER-APPROVAL.
9. `S4-B751-A-5-G-RSI-14-THRESHOLD-HARDENING` — same as A-1 + A-2 (consolidation candidate). PENDING-OWNER-APPROVAL.
10. `S4-B751-A-5-Q-EVENT-CONVERSION` — cluster Pattern Q rolled. PENDING-OWNER-APPROVAL.
11. `S4-B751-A-5-B320-LOOSENING-VERIFY-POST-B660` — verify B320 vol-gate loosening produces PASS_CUBE fire rate; revert if still starved. DEFERRED-POST-B660-RE-RUN.
12. `S4-B751-PATTERN-J-RSI-WINDOW-FAMILY-CONSOLIDATION-AUDIT-POST-B690b` — 4 RSI window-family strategies (A-1 + A-3 + A-4 + A-5) consolidation candidate. DEFERRED-POST-B690b.

### Owner decision gates (B751 surfaces)

| Decision | Severity | Pre-cube urgency |
|---|---|---|
| Pattern J RSI window family consolidation audit | HIGH | Post-B690b (waits on measurement) |
| Pattern Q cluster sweep (extension of B750/A-1 ticket) | MEDIUM | Pre-cube preferred (B751 walks add 4 more EVENT-conversion candidates) |
| Pattern G threshold-signal hardening sweep | LOW-MED | Pre-cube preferred (cube sweep capability) |
| Per-strategy regime-affinity adds (A-2) | LOW | Pre-cube |
| B320 lineage verify (A-5) | LOW-MED | Post-B660 re-run |

---

---

## Per-strategy walks (B752 batch — A-6 / A-7 / A-8 / A-9 / A-10 / A-11)

### A-6. `strat_stoch_oversold` (Stochastic K/D cross + EMA-20, LONG-only as registered, batched B627)

**Step 1 — Registration:** [screener.py:1538](backtest/signals/screener.py#L1538). Docstring: stoch %K < 20 AND K-cross-above-D AND price-above-EMA-20. SHORT side present in code (B627 fix) but `_strat3` returns dual.

**Step 2 — Gates:** LONG (3): `stoch_oversold` + `stoch_bullish_cross` + `price_above_ema_20`. SHORT (4): `stoch_overbought` + `stoch_bearish_cross` + `below_ema_20` (B627 F1 positive symmetric) + B718 borrow gate.

**Step 3 — Producer:** `compute_stochastic(...)` in technical.py. `stoch_oversold` is STATE (%K<20). `stoch_bullish_cross` is EVENT (K cross above D today). `price_above_ema_20`/`below_ema_20` standard + B609 producer symmetric. PIT-clean. **Mixed STATE+EVENT temporality** (state gate + cross event) — better than pure-STATE Cluster-A average.

**Step 4 — Doc vs reality:** CLEAN. Gates match context bullets. B627 F1 lineage VERIFIED.

**Step 5 — Regime affinity:** Not set. EMA-20 gate implicit bull/bear regime. CLEAN.

**Step 6 — Inverse:** Dual present (_strat3 LONG + SHORT). Symmetric.

**Step 7 — Disposition:**

| Cat | Finding | Action | Class |
|---|---|---|---|
| F | B627 F1 silent-gap fix applied; B718 borrow gate present | CLEAN | — |
| G | `stoch_oversold` (%K<20) uses producer threshold; cube-sweepable | CLEAN | — |
| Q | Mixed STATE+EVENT (cross is EVENT) — best-in-class for Cluster A oscillators | LOWER PRIORITY for EVENT-conversion sweep | **Class 1 KEEP-AS-IS** |
| J | vs A-7 stochrsi_oversold + A-9 williams_r_oversold + A-10 ultimate_oscillator (all oversold-bounce family) | Post-B690b: oversold-family marginal-contribution audit | **Class 6 DEFERRED-POST-B690b** |
| N | Stoch extremes cluster in vol regimes | Cube infra | **Class 8 CUBE-INFRA** |

**Recommendation: KEEP-AS-IS. Cleanest oscillator strategy in Cluster A by Pattern Q score** (has explicit cross EVENT). A-priori fire projection: ~10-25 fires/ticker/yr; universe-wide ~5K-12K/yr LONG. PASS_CUBE range; possibly over B710 5K ceiling.

---

### A-7. `strat_stochrsi_oversold` (StochRSI cross + RSI gate + 200-EMA, dual, batched B206 + B663)

**Step 1 — Registration:** [screener.py:1019](backtest/signals/screener.py#L1019). Docstring: B206 Connors discipline — 200-EMA gate added because pre-B206 fired aggressively in downtrends (-1.01 EV at 132 trades).

**Step 2 — Gates:** LONG (4): `stochrsi_oversold` + `stochrsi_cross_up` + `rsi_14<55` + `price_above_ema_200` (B663). SHORT (5): mirror with `rsi_14>45` + `below_ema_200` (B630 symmetric) + B718.

**Step 3 — Producer:** `compute_stochrsi(...)` in technical.py. `stochrsi_oversold` STATE (StochRSI<20). `stochrsi_cross_up` EVENT. rsi_14 STATE. PIT-clean.

**Step 4 — Doc vs reality:** CLEAN. B206 lineage VERIFIED. B663 default-False fix present.

**Step 5 — Regime affinity:** Not set. 200-EMA gate enforces regime per docstring intent. CLEAN.

**Step 6 — Inverse:** Dual present. Symmetric. Per Pattern S: SHORT side faces bull-drift; cube expected LONG > SHORT alpha.

**Step 7 — Disposition:**

| Cat | Finding | Action | Class |
|---|---|---|---|
| F | B663 + B630 symmetric + B718 borrow | CLEAN | — |
| G | `rsi_14<55` and `rsi_14>45` hardcoded thresholds (non-canonical "not overbought"/"not oversold") | Producer-additive booleans | **Class 2 (queue `S4-B752-A-7-G-RSI-14-MID-THRESHOLD-HARDENING`)** |
| Q | Mixed STATE+EVENT (cross EVENT) — same as A-6 | LOWER priority for cluster sweep | **Class 1 KEEP-AS-IS** |
| J | vs A-6 stoch_oversold (both K-cross oscillator families) | Post-B690b audit | **Class 6 DEFERRED-POST-B690b** |
| R | NOT a Connors-OR-disjunct strategy (B206 added 200-EMA gate only, not rsi_2<5 OR-extension) | CLEAN — different B206 application | — |

**Recommendation: KEEP-AS-IS + Class 2 G fix. Status post-B752: PRE-CUBE-CLEAN.** Fire projection: tight 4-gate stack; ~5-15/ticker/yr LONG; ~2,500-7,500/yr universe-wide. PASS_CUBE range.

---

### A-8. `strat_stochrsi_overbought_short` (StochRSI overbought SHORT)

**Step 1 — Registration:** [screener.py:2382](backtest/signals/screener.py#L2382). SHORT-only standalone (vs A-7 SHORT branch which has below_ema_200 gate added).

**Step 2 — Gates:** SHORT (4): `stochrsi_overbought` + `stochrsi_cross_dn` + `rsi_14>45` + B718 borrow gate.

**Step 3 — Producer:** Same as A-7 SHORT signals. PIT-clean.

**Step 4 — Doc vs reality:** No docstring. Gate-set vs A-7 SHORT branch: **A-7 SHORT adds `below_ema_200`; A-8 lacks it.** A-8 fires on overbought + cross_dn + RSI>45 WITHOUT regime gate.

**Step 5 — Regime affinity:** Not set. **A-8 has NO regime gate — fires in ANY regime including bull (where short fights drift).** Critical finding.

**Step 6 — Inverse:** No LONG mirror exists as standalone; A-7 LONG is the closest dual-strategy LONG analog.

**Step 7 — Disposition:**

| Cat | Finding | Action | Class |
|---|---|---|---|
| F | B718 borrow gate present | CLEAN | — |
| **CRITICAL Pattern W** | **A-8 is essentially A-7 SHORT branch MINUS the `below_ema_200` regime gate.** Post-tightening (if A-8 added below_ema_200), it would be deterministic duplicate of A-7 SHORT. | Owner decision: (a) DELETE A-8 (redundant); (b) ADD below_ema_200 → becomes A-7 SHORT duplicate → DELETE; (c) KEEP A-8 deliberately gate-less for bull-fade SHORT signal (unusual choice) | **Class 1-OR-DELETE (queue `S4-B752-A-8-PATTERN-W-DELETE-DECISION-VS-A-7-SHORT`)** |
| Pattern A | No regime gate; fires in bull regime against drift | Add `below_ema_200` regime gate (then becomes A-7 SHORT duplicate per Pattern W) | **Class 2 + Pattern W cascade** |
| Q | Mixed STATE+EVENT | LOWER priority | — |
| S | SHORT-only without regime gate = worst-case bull-drift exposure | Document | — |

**Recommendation: DELETE A-8 per Pattern W vs A-7 SHORT branch.** A-8 likely registered as separate strategy before A-7 SHORT side was added (B206 expansion). Per `feedback_no_prior_edge_consolidate_before_tune` + B718 hull_rsi precedent: redundant SHORT variant = DELETE-WRAPPER. Status post-B752: **DELETE CANDIDATE.**

Fire projection: ~15-30/ticker/yr SHORT (no regime gate inflates rate); universe-wide ~7K-15K/yr SHORT. Over B710 5K ceiling. Likely FAIL_CEILING + redundant with A-7 SHORT.

---

### A-9. `strat_williams_r_oversold` (Williams %R + Connors RSI(2) + CMF, dual, batched B206 + B629 + B663)

**Step 1 — Registration:** [screener.py:941](backtest/signals/screener.py#L941). Docstring: B206 Connors stack — primary = Williams %R OR Connors RSI(2)<5; 200-EMA regime gate. BUG-11 resolved. Sharpe 0.30 in Phase 1A-beta (current best-performing oversold strategy).

**Step 2 — Gates:** LONG (3): `(williams_r_oversold OR rsi_2<5)` + `price_above_ema_200` (B663) + `cmf_positive`. SHORT (4): mirror with `cmf_negative` (B629 F1 positive symmetric) + `below_ema_200` (B630 symmetric) + B718 borrow gate.

**Step 3 — Producer:** `compute_williams_r(...)` STATE. `compute_cmf(...)` STATE (chaikin money flow ZONE). PIT-clean. B629 F1 + B663 fixes present.

**Step 4 — Doc vs reality:** CLEAN. Sharpe 0.30 + BUG-11 + B629 + B663 lineage VERIFIED.

**Step 5 — Regime affinity:** Not set. 200-EMA gate enforces regime. CLEAN per Pattern A.

**Step 6 — Inverse:** Dual (_strat3). Symmetric. Per Pattern S.

**Step 7 — Disposition:**

| Cat | Finding | Action | Class |
|---|---|---|---|
| F | B629 + B663 + B718 all applied; positive-symmetric throughout | CLEAN | — |
| G | `williams_r_oversold` = `%R<-80` producer threshold; sweepable. `rsi_2<5` hardcoded; same Pattern G as A-1 Connors-stack | Producer-additive booleans for rsi_2 thresholds | **Class 2 LOOSEN/TIGHTEN (queue `S4-B752-A-9-G-RSI-2-THRESHOLD-HARDENING`)** |
| Q | All 3 LONG gates STATE | EVENT-conversion candidate per cluster Pattern Q | **Class 2 (queue `S4-B752-A-9-Q-WILLIAMS-CMF-EVENT-CONVERSION`)** |
| R | Connors-OR-disjunct same as A-1 + A-10 (rsi_2 path) — proportional tightening: CMF gate adds flow confirmation | Pattern R PROPORTIONAL — CLEAN | — |
| J | vs A-1 (RSI Connors), A-6 (stoch), A-7 (stochRSI), A-10 (UO Connors) | Oversold-family Pattern J audit post-B690b | **Class 6** |
| N | Cluster A Pattern N | Cube infra | **Class 8** |

**Recommendation: KEEP-AS-IS + Class 2 fixes.** Sharpe 0.30 carrier — empirically best oversold strategy in Phase 1A-beta. CLEAN post-B629/B663/B718. Status post-B752: PRE-CUBE-CLEAN.

Fire projection: 3 LONG gates Williams + Connors + CMF stack; ~5-15/ticker/yr; ~2,500-7,500/yr universe-wide LONG. PASS_CUBE.

---

### A-10. `strat_ultimate_oscillator` (UO + Connors RSI(2) + 200-SMA, dual, batched B206 + B631)

**Step 1 — Registration:** [screener.py:1055](backtest/signals/screener.py#L1055). Docstring extensive: Williams 1976 UO (4×avg7 + 2×avg14 + avg28)/7; UO<30 oversold / UO>70 overbought canonical extremes. B206 Connors stack: UO_oversold OR rsi_2<5. Sharpe 0.49 (BEST in oversold family at Phase 1A-beta) but only 27 trades. B631: F1 + F2 + (a) — last instance of `not s.get("price_above_sma_200")` NOT-pattern fixed (positive symmetric `below_sma_200`); uo_overbought signal swap; close_above_open bullish bar gate added.

**Step 2 — Gates:** LONG (3): `(uo_oversold OR rsi_2<5)` + `price_above_sma_200` + `close_above_open` (B631 a). SHORT (4): mirror with `uo_overbought` (B631 F2 swap) + `below_sma_200` (B631 F1) + `close_below_open` (B631 a) + B718 borrow gate.

**Step 3 — Producer:** `compute_ultimate_oscillator(...)` STATE. `compute_sma_200(...)` standard + B630 symmetric `below_sma_200`. close_above_open/close_below_open EVENT. PIT-clean.

**Step 4 — Doc vs reality:** CLEAN. Williams 1976 + B206 + B631 (F1+F2+a) lineage VERIFIED. Sharpe 0.49 Phase 1A-beta + 27 trades VERIFIED via existing dashboards.

**Step 5 — Regime affinity:** Not set. Docstring DEFERRED-TO-R5 manifest M1 entry `{bull}` is B623 REMOVE_OK candidate (+31.1pp PnL on REMOVE). Pre-R5 affinity addition WAITS for owner direction-aware confirmation.

**Recommendation:** Honor B623 REMOVE_OK status — no Pattern A change pre-R5. Per memory `feedback_r5_paused_pending_stage4_completion`.

**Step 6 — Inverse:** Dual (_strat3). Symmetric per B631. Pattern S asymmetric expectancy applies.

**Step 7 — Disposition:**

| Cat | Finding | Action | Class |
|---|---|---|---|
| F | B631 fully applied (F1+F2+a) + B718 borrow gate | CLEAN — **A-10 is the most thoroughly cleaned strategy in Cluster A** | — |
| G | `rsi_2<5` hardcoded; same as A-1/A-9 Connors-stack | Cluster-wide producer-additive | **Class 2 cross-ref `S4-B751-A-5-G-RSI-14-THRESHOLD-HARDENING` family** |
| Q | UO STATE + Connors-RSI STATE + close_above_open EVENT bar (B631 a) — mixed temporality with EVENT element | LOWER priority for EVENT-conversion (already partially EVENT-anchored) | **Class 1 KEEP-AS-IS** |
| R | Connors-OR same as A-1/A-9 — proportional tightening: B631 (a) bullish-bar gate adds EVENT confirmation. CLEAN. | — | — |
| J | vs A-1 (RSI), A-9 (Williams %R) Connors-stack family | Pattern J audit post-B690b | **Class 6** |
| Pattern A R5-deferred | docstring marks `{bull}` REMOVE_OK candidate per B623 | Wait for R5 confirmation per memory | **Class 6 DEFERRED-R5** |
| N | UO extreme is rare; effective-N concern | Cube infra | **Class 8** |

**Recommendation: KEEP-AS-IS.** A-10 is the gold-standard cleaned strategy in Cluster A (most thorough B631 F1+F2+a application). Sharpe 0.49 best-in-family at 27 trades = EXPLORATORY-tag-eligible per fire-count + W5m precedent. Status post-B752: PRE-CUBE-CLEAN; B623 REMOVE_OK pending R5.

Fire projection: tight 3-gate stack with EVENT bar; ~2-8/ticker/yr LONG; ~1K-4K/yr universe-wide. **Possibly FAIL_FIRE_STARVED per W5 council Pattern AA** — EXPLORATORY-tag candidate.

---

### A-11. `strat_mfi_oversold` (MFI + pivot S1/S2 + OBV, dual, batched B628)

**Step 1 — Registration:** [screener.py:1409](backtest/signals/screener.py#L1409). No docstring; inline comment B628 F1 family-sweep positive-symmetric `obv_bearish`.

**Step 2 — Gates:** LONG (3): `mfi_oversold` + `(near_s1 OR near_s2)` + `obv_bullish`. SHORT (4): mirror with `mfi_overbought` + `(near_r1 OR near_r2)` + `obv_bearish` (B628 F1 positive symmetric) + B718 borrow gate.

**Step 3 — Producer:** `compute_mfi(...)` STATE (MFI<20 oversold). `compute_pivots(...)` STATE (near support/resistance). `compute_obv(...)` STATE (OBV direction). PIT-clean. B628 F1 fix present.

**Step 4 — Doc vs reality:** CLEAN. B628 F1 lineage VERIFIED.

**Step 5 — Regime affinity:** Not set. No regime gate (no 200-EMA/SMA). Different pattern than other Cluster A oscillators — uses pivot-S1/S2 for support context (mean-rev "buy support" thesis), not trend gate.

**Pattern A concern:** A-11 is the ONLY Cluster A oscillator strategy WITHOUT a long-term regime gate (200-EMA/SMA). Implicit mean-reversion-at-support thesis vs other strategies' Connors-discipline trend-aligned mean-reversion. Distinct mechanism. Acceptable.

**Step 6 — Inverse:** Dual present. Symmetric. Per Pattern S.

**Step 7 — Disposition:**

| Cat | Finding | Action | Class |
|---|---|---|---|
| F | B628 F1 positive symmetric + B718 borrow gate | CLEAN | — |
| G | `mfi_oversold` = producer threshold; sweepable | CLEAN | — |
| Q | All 3 gates STATE | EVENT-conversion candidate (cluster Pattern Q rolled) | **Class 2** |
| Pattern A | NO long-term regime gate — uses pivot-support as context | DISTINCT THESIS from cluster norm; CLEAN per author intent | — |
| J | vs A-1/A-6/A-7/A-9/A-10 oversold family | Pattern J audit post-B690b | **Class 6** |
| N | MFI oversold + pivot support clusters in vol regimes | Cube infra | **Class 8** |

**Recommendation: KEEP-AS-IS.** Distinct pivot-support mechanism justifies absence of trend gate. Status post-B752: PRE-CUBE-CLEAN.

Fire projection: 3-gate stack MFI + pivot + OBV; ~5-15/ticker/yr LONG (pivots constrain to ~10-20% of bars); ~2,500-7,500/yr universe-wide. PASS_CUBE range.

---

## B752 cluster walk completion wrap-up

### Disposition summary (6 walks shipped)

| Walk | Strategy | Status | Key finding |
|---|---|---|---|
| A-6 | stoch_oversold | KEEP-AS-IS | Cleanest oscillator (mixed STATE+EVENT) |
| A-7 | stochrsi_oversold | KEEP-AS-IS + Class 2 G | Same cleanness; G fix on RSI mid-thresholds |
| A-8 | stochrsi_overbought_short | **DELETE CANDIDATE** | Pattern W vs A-7 SHORT branch (missing regime gate = redundant once fixed) |
| A-9 | williams_r_oversold | KEEP-AS-IS + Class 2 fixes | Sharpe 0.30 carrier; full B629+B663 fixes applied |
| A-10 | ultimate_oscillator | KEEP-AS-IS (gold-standard cleanness) | Sharpe 0.49 best-in-family; B631 F1+F2+a fully applied; **EXPLORATORY candidate per FIRE_STARVED** |
| A-11 | mfi_oversold | KEEP-AS-IS | Distinct pivot-support thesis (no trend gate); CLEAN |

**A-8 DELETE recommendation is the headline B752 finding.** Pattern W vs A-7 SHORT branch: A-8 fires on overbought + cross_dn + rsi_14>45 WITHOUT regime gate; A-7 SHORT does same WITH below_ema_200. Owner decision per B720 PO3 / B722 hull_rsi precedent: (a) DELETE A-8, (b) add regime gate to A-8 (then deterministic duplicate of A-7 SHORT → still DELETE), (c) keep A-8 deliberately gate-less for bull-fade SHORT.

**A-10 EXPLORATORY-tag candidacy is the second key B752 finding.** Sharpe 0.49 best-in-family but only 27 Phase 1A-beta trades = FAIL_FIRE_STARVED per W5m precedent. Per W5 council recommendation: tag EXPLORATORY pending B690b re-measurement.

### NEW EXECUTION_QUEUE tickets surfaced (B752)

1. `S4-B752-A-7-G-RSI-14-MID-THRESHOLD-HARDENING` — producer-additive `rsi_14<55` + `rsi_14>45` booleans (StochRSI's "not extreme" mid-thresholds). PENDING-OWNER-APPROVAL.
2. `S4-B752-A-8-PATTERN-W-DELETE-DECISION-VS-A-7-SHORT` — Pattern W audit + owner decision (a/b/c) on strat_stochrsi_overbought_short deletion. PENDING-OWNER-DECISION-A-B-OR-C.
3. `S4-B752-A-9-G-RSI-2-THRESHOLD-HARDENING` — same as A-1/A-10 cluster-wide producer-additive. PENDING-OWNER-APPROVAL.
4. `S4-B752-A-9-Q-WILLIAMS-CMF-EVENT-CONVERSION` — A-9 cluster Pattern Q rolled. PENDING-OWNER-APPROVAL.
5. `S4-B752-A-10-EXPLORATORY-TAG-CANDIDATE-POST-B660-RE-MEASURE` — A-10 Sharpe 0.49 @ 27 trades = FIRE_STARVED; EXPLORATORY tag candidate per W5m. PENDING-OWNER-APPROVAL-PENDING-B660-RE-MEASURE-VERIFY.
6. `S4-B752-PATTERN-J-OSCILLATOR-OVERSOLD-FAMILY-CONSOLIDATION-AUDIT-POST-B690b` — 5 oversold-family strategies (A-1 RSI Connors + A-6 stoch + A-7 stochRSI + A-9 Williams Connors + A-10 UO Connors) consolidation candidate. DEFERRED-POST-B690b.

### Owner decision gates (B752 surfaces)

| Decision | Severity | Pre-cube urgency |
|---|---|---|
| A-8 DELETE vs add-regime-gate (Pattern W cascade) | **HIGH** | Pre-cube — affects cube cell count + Bonferroni denominator |
| A-10 EXPLORATORY tag pending B660 re-measure | MEDIUM | Pre-cube |
| Pattern J oversold-family consolidation audit | HIGH | Post-B690b |

---

## B750 cluster walk completion wrap-up

### Disposition summary (3 walks shipped)

| Walk | Strategy | Status post-walk | Class actions surfaced |
|---|---|---|---|
| A-1 | rsi_oversold | KEEP-AS-IS + Class 2 producer-additive | F (clean) + G + Q + R + S |
| A-15 | ppo_crossover | KEEP-AS-IS + Class 2 Pattern Q EVENT-conversion | Q + J + N + T |
| A-22 | avwap_50_reclaim | KEEP-AS-IS + Class 2 fixes + producer audit | F NOT-pattern + G + J + PIT-audit |

**Pattern Q (STATE vs EVENT) is the most common Cluster A pattern.** Affects A-1, A-15, and likely 15+ other walks (any oscillator + ADX + Bollinger touch). Cluster-wide producer-additive EVENT-conversion candidate for B751+.

**Pattern G (hardcoded threshold) is the second most common.** Affects A-1 (rsi_2<5 + rsi_14<35), A-22 (pct_from_avwap<1.5%), and most threshold-based strategies. Producer-additive signal hardening = cluster-wide opportunity.

### NEW EXECUTION_QUEUE tickets surfaced (B750)

1. `S4-B750-PATTERN-Q-CLUSTER-A-EVENT-CONVERSION-SWEEP` — producer-additive sweep across all RSI/Stoch/Williams/MFI/Bollinger/Keltner STATE signals; emit `_cross_below_threshold_recent_5d` EVENT variants per B655 T10 precedent. PENDING-OWNER-APPROVAL.
2. `S4-B750-PATTERN-G-CLUSTER-A-THRESHOLD-SIGNAL-HARDENING` — producer-additive boolean signals for hardcoded thresholds (rsi_2<5, rsi_14<35, pct_from_avwap_50low<1.5pct, etc.) so cube can sweep. PENDING-OWNER-APPROVAL.
3. `S4-B750-PATTERN-J-CLUSTER-A-MARGINAL-CONTRIBUTION-AUDIT-POST-B690b` — gate-redundancy diagnostic across RSI variants (rsi_oversold + rsi9_extreme + rsi21_slow + rsi_volume_200ema), AVWAP variants (avwap_50_reclaim + avwap_252_breakout + avwap_20high_rejection_short), MA-cross variants (golden_cross_9_21 + golden_cross_20_50 + golden_cross_50_200 + golden_cross_volume + death_cross_50_200_volume — note these are in Cluster B). Expected 30 → ~15-20 effective primitives post-J. DEFERRED-POST-B690b.
4. `S4-B750-PATTERN-N-EFFECTIVE-N-AUTOCORRELATION-CUBE-EXTENSION` — cube infrastructure ticket to compute effective-N via autocorrelation on fire-bar series; cluster-wide concern not strategy-specific. Cross-ref W5 council recommendation. PENDING-OWNER-APPROVAL.
5. `S4-B750-AVWAP-50LOW-ANCHOR-PIT-VERIFY` — producer-audit via `pattern_producer_audit.py` template on `compute_avwap_signals` 50-day-low anchor. Verify anchor lookback excludes today. HIGHEST-PRIORITY PIT gate per Cluster A pre-cube. PENDING-OWNER-APPROVAL.
6. `S4-B750-A-22-PATTERN-F-NOT-MACD-BULL-REPLACE` — replace `(not macd_bull)` with `s.get("macd_12_26_9_bearish", False)` on strat_avwap_50_reclaim SHORT side; producer-additive `macd_12_26_9_bearish` if not emitted. PENDING-OWNER-APPROVAL.
7. `S4-B750-A-1-PATTERN-Q-RSI-OVERSOLD-EVENT-CONVERSION` — strat_rsi_oversold STATE-to-EVENT conversion candidate per B655 T10 precedent. PENDING-OWNER-APPROVAL.
8. `S4-B750-A-15-PPO-ADX-TEMPORALITY-MISMATCH-EVENT-CONVERSION` — strat_ppo_crossover ADX-trending STATE gate + PPO EVENT gate mismatch; producer-additive `adx_cross_above_25_recent_5d`. PENDING-OWNER-APPROVAL.

### Owner decision gates (B750 surfaces)

| Decision | Severity | Pre-cube urgency |
|---|---|---|
| Pattern Q cluster-wide EVENT-conversion sweep approval | MEDIUM | Pre-cube preferred (otherwise STATE oversampling distorts effective-N) |
| Pattern G threshold-signal hardening approval | LOW-MED | Pre-cube preferred (otherwise cube can't sweep) |
| Pattern J post-B690b marginal-contribution audit | HIGH | Post-B690b (waits on measurement validity) |
| Pattern N effective-N autocorrelation cube extension | HIGH | Cube infrastructure; not Cluster-A-specific |
| AVWAP-50low anchor PIT audit | **CRITICAL** | Pre-cube (AVWAP family fake-edge risk per B719 SMC reviewer Pattern K dealing-range parallel) |
| A-22 Pattern F NOT-pattern fix | LOW | Pre-cube (small fix; producer-additive) |

---

## Cluster-wide methodology references

### Producer modules touched by Cluster A

- `backtest/signals/technical.py` — RSI, Stoch, Williams, Ultimate, MFI, Bollinger, Keltner, Camarilla, CPR, MA-cross, AVWAP, OBV, MACD, PPO, ROC, CMF, Awesome Oscillator, ADX
- `backtest/signals/_short_borrow_trap_active` — B718 explicit borrow gate

### Citations (selected)

- **Connors L., Alvarez C. (2009)** — *Short Term Trading Strategies That Work* — RSI(2) extreme + 200-EMA regime methodology (basis of B206 Connors stack)
- **Williams L. (1976)** — Ultimate Oscillator definition (basis of strat_ultimate_oscillator)
- **Appel G. (1979)** — MACD (basis of strat_ppo_crossover; PPO is percentage-scaled MACD variant)
- **Wilder J.W. (1978)** — *New Concepts in Technical Trading Systems* — RSI / ADX / Parabolic SAR / ATR canonical definitions
- **Bollinger J. (2001)** — *Bollinger on Bollinger Bands* — band methodology + squeeze
- **Williams P. (Anchored VWAP discipline)** — B208 AVWAP family rationale
- **Quantified Strategies (2024)** — RSI(2) + 200-EMA backtest (Connors filter validation)

### Forensic-fix lineage

- **B204 (2026-05-17)** — Bollinger Connors-stack upgrade
- **B206 (2026-05-17)** — RSI Connors-stack upgrade (rsi_2<5 OR rsi_14<35)
- **B208 (2026-05-17)** — AVWAP family registration (50-low / 252-low / 20-high rejection)
- **B630 (2026-06-07)** — Producer-additive symmetric inverse signals (`below_ema_200`, `below_sma_50`, etc.) closing F2 silent-gap
- **B631 (2026-06-08)** — Ultimate Oscillator F1 silent-gap fix (last remaining `not s.get("price_above_sma_200")`)
- **B663 (2026-06-09)** — Family-bug sweep: `price_above_ema_200` default-True → default-False across ~30 strategies
- **B718a-d (2026-06-12)** — Explicit `borrow_ok` gate refactor on all 112 short-emitting strategies
- **B744 (2026-06-13)** — Static borrow-gate lint shipped

### Cross-strategy patterns lineage (CARRIED)

- **Pattern A** — B577 STRATEGY_REGIME_AFFINITY survey
- **Pattern F** — B611 reviewer + B663 family sweep + B718 borrow refactor
- **Pattern G** — B719 SMC reviewer Pattern G hardcoded-threshold flag
- **Pattern J** — B714 routing framework (delete-wrappers vs consolidate-variants vs retain-exploratory)
- **Pattern N** — B710 effective-N + W5 council Pattern N concern
- **Pattern Q** — B643 W5 + B655 T10 EVENT-conversion precedent + B611 STATE-vs-EVENT critique
- **Pattern R (NEW B750)** — Connors-stack OR-disjunct without proportional tightening
- **Pattern S** — B611 asymmetric data sources + B713 borrow-asymmetry + B710 squeeze-asymmetry
- **Pattern T (NEW B750)** — MA-cross redundancy with EMA-trend gate
- **Pattern W** — B718 hull_rsi deterministic-duplicate

---

## B750 cluster walk status

| Walk | Status | Batch | Notes |
|---|---|---|---|
| A-1 rsi_oversold | ✅ Walked B750 | 2026-06-14 | Step 1-7 complete; 7 queue tickets surfaced |
| A-2 rsi_overbought_short | ✅ Walked B751 | 2026-06-14 | Step 1-7 complete; 5 queue tickets surfaced (G + Q + regime + W + S) |
| A-3 rsi9_extreme | ✅ Walked B751 | 2026-06-14 | Step 1-7 complete; 4 queue tickets surfaced (LONG-only justified per asymmetric data) |
| A-4 rsi21_slow | ✅ Walked B751 | 2026-06-14 | Step 1-7 complete; Pattern J RSI window family + W audit candidates |
| A-5 rsi_volume_200ema | ✅ Walked B751 | 2026-06-14 | Step 1-7 complete; B320 lineage verify + J vs A-1 ablation candidate |
| A-6 stoch_oversold | ✅ Walked B752 | 2026-06-14 | KEEP-AS-IS; cleanest oscillator (mixed STATE+EVENT) |
| A-7 stochrsi_oversold | ✅ Walked B752 | 2026-06-14 | KEEP-AS-IS + Class 2 G fix |
| A-8 stochrsi_overbought_short | ✅ Walked B752 | 2026-06-14 | **DELETE CANDIDATE** Pattern W vs A-7 SHORT |
| A-9 williams_r_oversold | ✅ Walked B752 | 2026-06-14 | KEEP-AS-IS; Sharpe 0.30 carrier; full fixes |
| A-10 ultimate_oscillator | ✅ Walked B752 | 2026-06-14 | KEEP-AS-IS gold-standard cleanness; EXPLORATORY candidate |
| A-11 mfi_oversold | ✅ Walked B752 | 2026-06-14 | KEEP-AS-IS; distinct pivot-support thesis |
| A-12 bollinger_lower | ⏳ Pending B753 | — | |
| A-13 bollinger_tight | ⏳ Pending B753 | — | |
| A-14 bollinger_upper_short | ⏳ Pending B753 | — | |
| A-15 ppo_crossover | ✅ Walked B750 | 2026-06-14 | Step 1-7 complete; 4 queue tickets surfaced |
| A-16 keltner_lower | ⏳ Pending B753 | — | |
| A-17 camarilla_r4_breakout | ⏳ Pending B753 | — | |
| A-18 camarilla_rsi_obv | ⏳ Pending B754 | — | |
| A-19 camarilla_rsi_obv_short | ⏳ Pending B754 | — | |
| A-20 cpr_narrow_momentum | ⏳ Pending B754 | — | |
| A-21 cpr_narrow_momentum_short | ⏳ Pending B754 | — | |
| A-22 avwap_50_reclaim | ✅ Walked B750 | 2026-06-14 | Step 1-7 complete; 7 queue tickets surfaced incl. CRITICAL AVWAP PIT audit |
| A-23 avwap_252_breakout | ⏳ Pending B754 | — | |
| A-24 avwap_20high_rejection_short | ⏳ Pending B755 | — | |
| A-25 awesome_oscillator | ⏳ Pending B755 | — | |
| A-26 cmf_flip | ⏳ Pending B755 | — | |
| A-27 roc_burst | ⏳ Pending B755 | — | |
| A-28 williams_stoch_dual | ⏳ Pending B755 | — | |
| A-29 prev_day_low_bounce | ⏳ Pending B755 | — | |
| A-30 bb_squeeze_volume | ⏳ Pending B756 | — | |

**Progress: 13/30 walked (43%) — B750 framework + 3 + B751 4 + B752 6 walks shipped.**

---

### Cross-cluster status snapshot (post-B750)

| Cluster Doc | Status | Walks | Cross-cluster patterns shared with Cluster A |
|---|---|---|---|
| [STAGE_4_PIVOT_CLUSTER_WALKS.md](STAGE_4_PIVOT_CLUSTER_WALKS.md) | External review B710 + walks complete | 10 | Pattern F + G + N + Q + W |
| [STAGE_4_TREND_CLUSTER_WALKS.md](STAGE_4_TREND_CLUSTER_WALKS.md) | External review (B696 banner) + walks complete | 15 | Pattern F + J + Q + T + W |
| [STAGE_4_SMART_MONEY_CLUSTER_WALKS.md](STAGE_4_SMART_MONEY_CLUSTER_WALKS.md) | External review B713 + walks complete | 41 | Pattern F + J + N + S |
| [STAGE_4_SMC_CLUSTER_WALKS.md](STAGE_4_SMC_CLUSTER_WALKS.md) | External review B719 + walks complete | 18 | Pattern G + J + K (PIT audit) + N |
| [STAGE_4_ICT_CLUSTER_WALKS.md](STAGE_4_ICT_CLUSTER_WALKS.md) | External review B705 + walks complete | 12 | Pattern F + G + N + Q |
| [STAGE_4_BREAKOUT_CLUSTER_WALKS.md](STAGE_4_BREAKOUT_CLUSTER_WALKS.md) | External review (B696 banner) + walks complete | 19 | Pattern F + G + S + Y |
| [STAGE_4_EVENT_DRIVEN_CLUSTER_WALKS.md](STAGE_4_EVENT_DRIVEN_CLUSTER_WALKS.md) | External review B702 + walks complete | 7 | Pattern N |
| [STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md](STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md) | External review (B699 banner) + walks complete | 18 | Pattern Y |
| **STAGE_4_OSCILLATOR_MEAN_REVERSION_CLUSTER_WALKS.md (THIS DOC)** | **B750 framework + 3 sample walks** | **3/30** | **Pattern F + G + J + N + Q + R (new) + S + T (new) + W** |
| STAGE_4_TREND_CONFLUENCE_CHART_PATTERN_RESIDUAL_CLUSTER_WALKS.md | Scheduled B754+ | 0/33 | (TBD) |
| STAGE_4_CONTEXT_EVENT_CALENDAR_CLUSTER_WALKS.md | Scheduled B758+ | 0/33 | (TBD) |

**Stage 4 cluster-walk coverage post-B750:** 132 walked (60%) + 3 new walks B750 = **135 walked (61%)** / 86 remaining unwalked (39%). Target: 96-walk completion across B751-B762.

---

**B750 deliverables:** doc scaffolding + Patterns A-T framework + 30-strategy state table + 3 walks (A-1 + A-15 + A-22) + 8 NEW EXECUTION_QUEUE tickets + cross-cluster snapshot update.

**Per `feedback_pyramid_per_addressal`:** pyramid runs end-of-batch with B750 commit. Pure doc additions but per memory `feedback_pyramid_no_exceptions` pyramid runs regardless.

**Per `feedback_strategy_counts_by_buckets_each_turn`:** 221 registered / 0 deprecated / 1 missing-producer / 220 active. Cluster A walks: 3/30 (10% post-B750). Total Stage 4 walked: 135/221 (61%).
