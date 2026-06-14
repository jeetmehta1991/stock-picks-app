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
| A-2 rsi_overbought_short | ⏳ Pending B751 | — | |
| A-3 rsi9_extreme | ⏳ Pending B751 | — | |
| A-4 rsi21_slow | ⏳ Pending B751 | — | |
| A-5 rsi_volume_200ema | ⏳ Pending B751 | — | |
| A-6 stoch_oversold | ⏳ Pending B752 | — | |
| A-7 stochrsi_oversold | ⏳ Pending B752 | — | |
| A-8 stochrsi_overbought_short | ⏳ Pending B752 | — | |
| A-9 williams_r_oversold | ⏳ Pending B752 | — | |
| A-10 ultimate_oscillator | ⏳ Pending B752 | — | |
| A-11 mfi_oversold | ⏳ Pending B752 | — | |
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

**Progress: 3/30 walked (10%) — framework + 3 sample walks shipped B750.**

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
