# B784 -- CHECKLIST #108 pre-flight applied to #38-#48 B766 council bundle

# per CHECKLIST #77 + #108 + #94 + #105 + #107
# Source: B779 owner directive "Approve all other recs" (B766 council bundle approval)
# Source: CHECKLIST #108 (B777 codification per B776 M3 memo)
# Source: backtest/signals/screener.py per-strategy gate logic
# per memory: feedback_audit_recommendations_against_existing_directives.md + feedback_no_rushing_per_strategy_tweak.md + feedback_no_a_priori_strategy_pruning.md

## Purpose

Per CHECKLIST #108 (codified B777): gate-MODIFICATIONS on EXISTING strategies require per-turn pre-flight surfacing (a) conditional-return hypothesis, (b) fire-count projection, (c) validation plan, (d) literature/empirical precedent. Per `feedback_audit_recommendations_against_existing_directives`: check new directives against prior owner directives before applying.

Owner directive 2026-06-15 13:25 UTC "Approve all other recs" approved the B766 council bundle including 11 per-strategy tickets #38-#48. Per `feedback_no_rushing_per_strategy_tweak`: one strategy per batch.

This pre-flight surfaces:
- which tickets are TRACTABLE NOW (single-batch)
- which require PRODUCER-SIDE work (multi-batch)
- which CONFLICT with prior owner directives (need re-approval scope clarification)

## Per-ticket pre-flight

### #38 RSI family fire-on-cross-not-state (A-1 / A-4 / A-5)

**Reviewer rec:** A-1 rsi_oversold, A-4 rsi21_slow, A-5 rsi_volume_200ema fire on STATE (rsi_14<35 stays True for many bars during oversold episode). Apply A-3 rsi9_extreme's pattern: producer-additive `rsi_14_cross_up_recent_3d` per B655 T10 + B722 hull_rsi precedents.

**CHECKLIST #108 pre-flight:**
- (a) Hypothesis: mean-reversion's "right entry" = turn not extreme (Wyckoff Spring + Connors capitulation). STATE-form over-fires; EVENT-form is selective.
- (b) Fire-count projection: STATE rsi_14<35 fires ~20-30% of bars in oversold periods → EVENT rsi_14_cross_up_recent_3d fires once per oversold episode = ~10x reduction. Pre-fix rsi_oversold (A-1) was Sharpe 0.30 carrier in Phase 1A-beta per cluster doc (= passes cube). Post-fix may push below min_trades=30/regime; depends on universe + period.
- (c) Validation plan: cube cell measurement of A-1/A-4/A-5 post-conversion vs current STATE-form baseline; expected ~10x fire reduction with comparable or improved per-trade edge.
- (d) Precedent: B655 T10 supertrend EVENT-conversion (10x reduction; precedent for Pattern Q application); B722 hull_rsi STATE->EVENT.

**Tractability:** REQUIRES PRODUCER-SIDE NEW SIGNAL (rsi_14_cross_up_recent_3d producer-additive). Multi-batch work: B785+ ship producer + apply per strategy with CHECKLIST #108 fire-count projection + verify post-fix in measurement.

**Status:** PENDING-MULTI-BATCH (producer first; then per-strategy via #108)

### #39 A-1 Connors OR-disjunct emphasis correction

**Reviewer rec:** A-1 strat_rsi_oversold uses `(rsi_2 < 5 OR rsi_14 < 35)` with EQUAL emphasis. Per Connors+Alvarez 2009: RSI(2)<5 is selective; RSI(14)<35 is noisy fallback. Tune: make RSI(2)<5 PRIMARY, drop or down-weight RSI(14)<35.

**Status from B768 ANNOTATION on ticket #39:** **PARTIALLY REFUTED.** Demo edge-prior measured `rsi_14_lt_30` Sharpe@10d=0.281 (STRONGEST of 14 triggers); hit_rate 63%; pnl +184bp/10d. RSI(14)<30 is genuine documented edge, NOT noisy fallback. Reviewer's emphasis-backward claim does NOT survive direct measurement at threshold 30. Strategy's actual gate is 14<35 (looser); cube will measure that.

**Tractability:** NO ACTION NEEDED. Recommendation REVISED to KEEP OR-disjunct pending cube. Already annotated.

**Status:** COMPLETED-EMPIRICAL B768 (refuted by edge-prior test)

### #40 RSI family capitulation-volume gate

**Reviewer rec:** None of A-1/A-3/A-4/A-5 require evidence the oversold is EXHAUSTING (capitulation volume + higher low forming + reversal bar). Producer-additive `capitulation_recent_3d` = (vol_spike_2x_on_down_day_recent_3d AND drying_volume_on_turn).

**CHECKLIST #108 pre-flight:**
- (a) Hypothesis: capitulation-volume confirms exhaustion (Wyckoff Selling Climax + Connors capitulation); reduces false-positive on persistent downtrends.
- (b) Fire-count projection: composite AND-of-2-events → likely massive fire-count reduction (90%+). Pre-fix A-1 ~2,500/yr → post-fix may drop to ~250/yr (still above min_trades=100; per-regime risk).
- (c) Validation plan: cube cell measurement; compare A-1 with vs without capitulation gate; A/B per-regime.
- (d) Precedent: B650 W5 vol_below_avg AND-required (Wyckoff Spring precedent shipped B650); same mechanism. B652 W5m EXPLORATORY-tag for capitulation-gate fire-starve risk.

**Tractability:** REQUIRES PRODUCER-SIDE NEW SIGNAL (`vol_spike_2x_on_down_day_recent_3d` + `drying_volume_on_turn` + `capitulation_recent_3d` composite). Same multi-batch pattern as #38.

**Status:** PENDING-MULTI-BATCH

### #41 A-5 vol_above_avg WRONG-DIRECTION fix

**Reviewer rec:** A-5 strat_rsi_volume_200ema uses `vol_above_avg`. Wrong direction for mean-reversion entry. Replace with composite `vol_spike_on_down_day_recent + vol_below_avg_on_turn`. STRATEGY BUG not tune.

**CONFLICT WITH PRIOR OWNER DIRECTIVE (B320 2026-05-25):**

B320 docstring on strat_rsi_volume_200ema:
> "Batch 320 (2026-05-25): loosened vol gate from vol_spike_2x to vol_above_avg (>=1.0x) per owner directive. The 2x bar combined with RSI<35 AND above-200-EMA was nearly impossible to satisfy in trending markets (RSI<30 + uptrend is itself rare); the volume gate compounded that to zero."

Owner explicitly LOOSENED from vol_spike_2x → vol_above_avg in B320 because the tight gate FIRE-STARVED the strategy.

Reviewer's proposed change: replace vol_above_avg with vol_spike_on_down + vol_below_avg_on_turn. This RE-TIGHTENS the gate (composite AND-of-2-events). Likely returns to FIRE-STARVED state.

Per `feedback_audit_recommendations_against_existing_directives`: surface BEFORE applying. The B779 "approve all other recs" likely was a bundle-level approval; owner may not have noticed the B320 conflict on #41 specifically.

**CHECKLIST #108 pre-flight:**
- (a) Hypothesis: capitulation+drying-vol confirms reversal (Wyckoff); reviewer position
- (b) Fire-count projection: B320 docstring directly states `vol_spike_2x + RSI<35 + above_ema_200` was "nearly impossible" -> "zero". Reviewer's `vol_spike_on_down + vol_below_avg_on_turn + RSI<35 + above_ema_200` is even tighter (4-condition AND with vol_spike_on_down being even rarer than vol_spike_2x).
- (c) Validation plan: would need new producer + cube measurement
- (d) Precedent: B320 owner directive AGAINST tightening this specific strategy

**Tractability:** **BLOCKED-PENDING-OWNER-DECISION** on directive scope.

Owner-decision options:
- (i) Keep B320 (vol_above_avg stays); REJECT reviewer rec #41 with citation to B320
- (ii) Override B320 (apply reviewer rec); accept fire-starve risk
- (iii) Split into 2 strategies: vol_above_avg version + vol_spike_capitulation version; cube measures both

**Status:** BLOCKED-PENDING-OWNER-DECISION (B320 conflict)

### #42 A-6 / A-9 Williams-Stoch Pattern J pair audit

**Reviewer rec:** Williams %R is algebraically near-identical to Stochastic %K by construction. A-9 strat_williams_r_oversold + A-6 strat_stoch_oversold likely Pattern J duplicates. Run B709 phi-correlation precompute.

**CHECKLIST #108 pre-flight:**
- (a) Hypothesis: phi-correlation on fire-bar streams >= 0.70 -> Pattern J consolidation candidate; <0.70 -> distinct.
- (b) Fire-count projection: ANALYTICAL test; no gate-modification yet.
- (c) Validation plan: B709-style phi-correlation on existing B756 fire-bar matrix output.
- (d) Precedent: B709 PEAD-restore precedent (phi=0.297 < 0.70 threshold -> restore both); B722 hull_rsi DELETE (phi >= 0.85 deterministic-duplicate).

**Tractability:** **TRACTABLE NOW** (analytical; uses existing B756 fire-bar matrix output if A-6 + A-9 are in cluster A registry).

**Status:** TRACTABLE B785+

### #43 A-11 MFI obv anti-selection conditional-add-test

**Reviewer rec:** A-11 strat_mfi_oversold requires obv_bullish. Fresh decline into oversold means OBV has been FALLING; requiring obv_bullish may ANTI-SELECT. Run B709-style conditional-add-test.

**CHECKLIST #108 pre-flight:**
- (a) Hypothesis: obv_bullish gate during oversold conditions filters out the real reversion opportunities (anti-selection); empirical test required.
- (b) Fire-count projection: ANALYTICAL test; gate-modification depends on result.
- (c) Validation plan: measure win-rate with vs without obv_bullish gate on existing B689 fire-bar data.
- (d) Precedent: B709 conditional-add-test methodology.

**Tractability:** **TRACTABLE NOW** if A-11 fire-bar data available in B756 output.

**Status:** TRACTABLE B785+

### #44 A-12 Bollinger band-walk-in-downtrend continuation-failure

**Reviewer rec:** A-12 strat_bollinger_lower fires on BB lower-band touch. In strong downtrend, price WALKS the lower band -> touch is CONTINUATION signal not reversion. Fix: fire on BAND RE-ENTRY (close back inside band after touch/close outside), not touch.

**CHECKLIST #108 pre-flight:**
- (a) Hypothesis: BB lower-touch in strong downtrend is continuation; band-re-entry filters band-walks.
- (b) Fire-count projection: re-entry is a 2-bar EVENT (touch -> reclaim); ~5-10x less frequent than touch alone. Pre-fix fire rate ~1,808 fires (B768 smoke) -> post-fix ~180-360 fires; still above min_trades.
- (c) Validation plan: producer-side new `bb_lower_reclaim_recent_3d` signal; cube cell measurement comparing band-touch vs band-reclaim variants.
- (d) Precedent: B655 T10 supertrend EVENT-conversion (reclaim/flip pattern).

**Tractability:** REQUIRES PRODUCER-SIDE NEW SIGNAL.

**Status:** PENDING-MULTI-BATCH

### #45 A-12 BB pctb threshold cube-sweepable

**Reviewer rec:** A-12 uses hardcoded %b threshold. Should be SWEPT not fixed; producer-additive `bb_pctb_lt_threshold` boolean per Pattern G cube-sweepability.

**CHECKLIST #108 pre-flight:**
- (a) Hypothesis: BB pctb threshold optimal varies by regime / volatility; cube-sweepability enables per-cell verdict.
- (b) Fire-count projection: producer-additive (parallel-variant); existing strategy unchanged. Pattern G cube-sweepability is the precedent (B654 cpr_narrow_tight pattern).
- (c) Validation plan: producer emits family of bb_pctb_lt_{0.05,0.10,0.15,0.20} booleans; cube sweep finds optimum.
- (d) Precedent: B654 cpr_narrow_tight 0.05/0.15 variants.

**Tractability:** REQUIRES PRODUCER-SIDE NEW SIGNAL.

**Status:** PENDING-MULTI-BATCH

### #46 AVWAP proximity ATR-scaled

**Reviewer rec:** A-22 + A-23 + A-24 use FIXED percent proximity (1.5%, 2.0%, 1.0%). 1.5% means different things on 15%-vol name vs 60%-vol name. Replace with ATR-scaled proximity (0.5 × 20-bar ATR / price). Producer-additive `near_avwap_X_atr_scaled`.

**Tractability:** REQUIRES PRODUCER-SIDE NEW SIGNAL.

**Status:** PENDING-MULTI-BATCH

### #47 AVWAP reclaim entry firing-logic formalization

**Reviewer rec:** A-22 avwap_50_reclaim fires on STATE (`above_avwap_50low`). Reclaim is an EVENT not a STATE. Producer-additive `avwap_50_reclaim_recent_3d` per B655 T10 EVENT-conversion pattern.

**Tractability:** REQUIRES PRODUCER-SIDE NEW SIGNAL.

**Status:** PENDING-MULTI-BATCH

### #48 A-17 / A-20 / A-21 Camarilla CPR timeframe-mismatch structural decision

**Reviewer rec:** A-17 + A-20 + A-21 are intraday tools on daily bars. Parameter tuning won't fix structural mismatch. Owner decision: (a) move to intraday; (b) reframe as daily momentum drop pivot-precision language; (c) DELETE per timeframe-mismatch.

**Tractability:** OWNER-DECISION REQUIRED (no engineering action without owner choice between a/b/c).

**Status:** PENDING-OWNER-DECISION

## #38-#48 bundle status summary

| # | Ticket | Status | Action |
|---|---|---|---|
| 38 | RSI fire-on-cross-not-state | PENDING-MULTI-BATCH | Producer + per-strategy via #108 |
| 39 | Connors OR-disjunct emphasis | COMPLETED-EMPIRICAL B768 (refuted) | NO ACTION |
| 40 | RSI capitulation-volume gate | PENDING-MULTI-BATCH | Producer + per-strategy |
| **41** | A-5 vol_above_avg WRONG-DIRECTION | **BLOCKED-PENDING-OWNER-DECISION** | **B320 directive conflict** |
| 42 | Williams-Stoch Pattern J pair | **TRACTABLE NOW** | B785+ analytical |
| 43 | MFI obv anti-selection | **TRACTABLE NOW** | B785+ analytical |
| 44 | A-12 BB band-walk continuation | PENDING-MULTI-BATCH | Producer + per-strategy |
| 45 | A-12 BB pctb cube-sweepable | PENDING-MULTI-BATCH | Producer-additive sweep |
| 46 | AVWAP proximity ATR-scaled | PENDING-MULTI-BATCH | Producer-additive |
| 47 | AVWAP reclaim EVENT-conversion | PENDING-MULTI-BATCH | Producer-additive |
| 48 | Camarilla CPR timeframe-mismatch | **PENDING-OWNER-DECISION** | a / b / c choice |

## Key surfacings requiring owner input

**Items needing explicit owner direction beyond "approve all other recs":**

1. **#41 B320 conflict**: B320 explicitly loosened from vol_spike_2x → vol_above_avg per owner directive (RSI<35 + 200-EMA + vol_spike was "nearly impossible to satisfy"). Reviewer rec #41 proposes RE-TIGHTENING via vol_spike_on_down + vol_below_avg_on_turn (4-condition AND). Owner can:
   - (i) Keep B320 / REJECT #41 → annotate ticket REJECTED with B320 citation
   - (ii) Override B320 / apply #41 → accept likely fire-starve return; tag EXPLORATORY pre-cube
   - (iii) Split into 2 strategies → cube measures both versions
2. **#48 Camarilla CPR**: 3 strategies need structural-decision a/b/c (intraday move OR reframe-as-momentum OR DELETE). Owner picks.

**Tractable-now items the autonomous loop CAN ship without further owner input:**

3. **#42 Williams-Stoch Pattern J** -- analytical; uses B756 fire-bar matrix if available
4. **#43 MFI obv anti-selection** -- analytical; uses existing B689 data
5. **#38 + #40 + #44 + #45 + #46 + #47**: each is a producer-side new signal + per-strategy CHECKLIST #108 walk. Doable but multi-batch each. Per `feedback_no_rushing_per_strategy_tweak`: one strategy per batch. Approximately 6 producer-side new signals × per-strategy walks = ~10-15 batches B786-B800-ish to complete the bundle.

## Recommendations

1. **Surface #41 + #48 to owner** in B784 commit + queue (this batch); proceed when owner provides direction
2. **Tractable next batches** B785/B786: #42 + #43 analytical Pattern J audits (each one batch)
3. **Multi-batch sequence** B787+: per-strategy producer-additive walks for #38/#40/#44/#45/#46/#47 (approximately 6+ batches each)

## CHECKLIST #107 reconciliation (B784)

- **Findings surfaced:** 1 primary (CHECKLIST #108 pre-flight applied to 11 bundle items; 2 BLOCKED-PENDING-OWNER, 2 TRACTABLE NOW, 6 PENDING-MULTI-BATCH, 1 already-COMPLETED-EMPIRICAL) + 1 nuanced (B320 vs #41 directive conflict)
- **Tickets filed:** 0 NEW + 11 annotations on existing #38-#48 (each gets CHECKLIST #108 pre-flight result + tractability scope)
- **Audit-clean: YES**

Cumulative ticket count post-B784: 133 unique S4-B7XX tickets (no change; all in-place annotations).

## Strategy counts (unchanged)

221 / 0 / 1 / **220 active**.

## Memory + checklist compliance

- `feedback_audit_recommendations_against_existing_directives.md` -- #41 B320 conflict surfaced BEFORE applying; #48 owner-decision flagged
- `feedback_no_rushing_per_strategy_tweak.md` -- per-strategy split; multi-batch plan respects one-strategy-per-batch
- `feedback_no_a_priori_strategy_pruning.md` -- no strategies modified; only CHECKLIST #108 pre-flight applied
- `feedback_local_changes_default_global_needs_approval.md` -- N/A (no code changes)
- CHECKLIST #44(b) -- N/A (not data-consumption audit)
- CHECKLIST #67 -- doc-sync same-turn
- CHECKLIST #69 -- pyramid (unchanged 842/842)
- CHECKLIST #77 -- canonical-source headers
- CHECKLIST #94 -- queue-mandatory-per-turn
- CHECKLIST #105 -- strategy source read end-to-end for each ticket
- CHECKLIST #106 -- N/A
- CHECKLIST #107 -- findings-vs-tickets reconciliation (NINETEENTH-FULL-EXECUTION)
- CHECKLIST #108 -- FIRST FULL APPLICATION TO A BUNDLE; 11 items pre-flighted; 2 BLOCKED + 2 TRACTABLE + 6 PENDING + 1 DONE
