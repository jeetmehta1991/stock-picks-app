# Phase 1A-beta optimization framework (Batch 378)

**Source (per CHECKLIST #77 canonical-source attribution):** owner directive 2026-05-26 — "Execute 1 2 3" (per-strategy producer audit + per-(strategy×exit) cube analysis + cap triage) + threshold-optimization for fired strategies. Companion to `PHASE_1A_BETA_PER_STRAT_EXIT_FORENSIC.md`.

## 1. Why 99.96% of candidates were rejected (the compounding math)

Phase 1A-β single-batch produced ~970,000 ticker-day candidates (1,237 avg passing screener × ~784 trading days) → only **361 trades** = **0.037% conversion rate**. The 99.96% rejection is the compound effect of 4 independent gate layers:

### Gate layer 1: Portfolio cap (Batch 203 + DEC-185)
- `min(LIVE_TRADING_RULES["max_open_positions"]=25, regime_position_count_cap(regime))`
- Regime caps: bull=40, neutral=25, bear=15, crisis=10, unknown=5
- Effective cap = `min(25, 40) = 25` (bull) / `min(25, 15) = 15` (bear) / etc.
- **At 1937-ticker scale**, 25 slots/day = 1.3% admission rate per day (25/1937)
- **Worst hit**: `pivot_r1_breakout` produced 9,314 candidates → 2,918 (31%) rejected by cap, 1,858 (20%) by bear-affinity → 0 fired
- **STATUS: REMOVED for Phase 1A-β** per Batch 377 owner directive (`--no-portfolio-cap` auto-enabled for `--phase=1a-beta`)

### Gate layer 2: Regime affinity (Batch 203 + Batch 293)
- Each strategy declared in `STRATEGY_REGIME_AFFINITY` dict (regime_selector.py:67-200)
- ~70 strategies narrowed to subsets like `{bull, neutral}` or `{bear, crisis}` only
- Phase 1A-β 4y regime distribution: bull 53% / bear 40% / neutral 7%
- A `{bull, neutral}` strategy is BLOCKED on bear days = -40% opportunity
- A `{bear, crisis}` strategy is BLOCKED on bull+neutral days = -60% opportunity
- **Batch 370 Fix 2 already restored** 4 calendar strategies to include `bear`
- **STATUS: PARTIALLY ADDRESSED**. Per-strategy regime-affinity audit recommended for remaining narrowings — see workstream 1 follow-on.

### Gate layer 3: Event suppression (DEC-348)
- FOMC d0/d1, CPI d0, NFP d0, OPEX d-1 windows BLOCK non-event-bypass strategies
- ~12-15 FOMC days/year + 12 CPI + 12 NFP + 12 OPEX = ~50 blocked days/year
- 4y window = ~200 blocked days out of 1008 = **~20% of all trading days blocked**
- `STRATEGIES_BYPASS_EVENT_SUPPRESSION` set (config.py:863) contains 3 strategies (`pre_fomc_long_sleeve`, `pre_fomc_quality_momentum_long`, `buyback_8k_recent_long`) that are exempt
- **STATUS: INTENTIONAL** per DEC-348 — captures stale opportunity-windowing
- **Optimization**: review per-strategy whether the bypass list should expand (e.g., should `pead_long` bypass since PEAD is event-driven?)

### Gate layer 4: Per-strategy entry gates (in `strat_*` function bodies)
- Each strategy's gate condition compounds AND-clauses (e.g., `s.get("rsi_14") < 30 AND s.get("price_above_ema_200") AND s.get("vol_spike_2x")`)
- Typical 3-AND-clause compound = ~5-15% admission rate per ticker-day
- Many strategies have 4-6 AND-clauses → admission rate < 1% per ticker-day
- **STATUS: PER-STRATEGY OPTIMIZATION** — this is Workstream 2 territory below

### Compounding math (worked example)

Take a typical `{bull, neutral}` long strategy with 3 entry AND-clauses each firing 30%:
```
1937 candidates/day x
  60% regime-eligible (bull+neutral) x
  80% non-event-blackout x
  (0.30)^3 = 2.7% AND-clause admission x
  ~75% sector liquidity gate x
  cap 25/admitted = 9% (when 100 admitted) [REMOVED]
  = ~0.05% conversion
```
Multiply: 1937 × 0.60 × 0.80 × 0.027 × 0.75 × 0.09 ≈ **1.7 trades/day**

Over 1008 days = **1,700 trades** for this hypothetical strategy. Multiply by 50 active strategies × overlap = a few thousand total.

Reality: 31 active strategies × 7-15 fires/each avg = 361 trades. **Cap was the dominant choke**, blocking thousands of admitted candidates per day. Removing the cap (Batch 377) should restore 5-20× more trades per strategy.

---

## 2. 155 quiet vs 49 PRODUCER_LAYER_ZERO — what's the difference?

| Bucket | Count | What it means | Diagnostic signature |
|---|---:|---|---|
| **155 quiet** | total | Strategy is registered + active, but fired 0 trades in Phase 1A-β | `tl['strategy'] not in fired_set` |
| **106 GATE_FILTERED** | subset | Strategy GENERATED candidates but the engine REJECTED ALL of them | `appears in skipped_trades.csv` with non-zero count |
| **49 PRODUCER_LAYER_ZERO** | subset | Strategy NEVER generated a single candidate — the per-strategy `strat_*` function never returned `fires=True` for any ticker-day | `does NOT appear in skipped_trades.csv` (engine never saw a candidate to skip) |

**The diagnostic distinction matters:**
- **GATE_FILTERED** strategies: producer + gate logic both work; engine downstream rejection (cap / regime / event-suppression / DD-halt / ticker-uniqueness). FIX: remove/loosen the engine gate (Batch 377 already removes the cap).
- **PRODUCER_LAYER_ZERO** strategies: gate condition is false-always for every ticker-day. Either (a) compound AND-clause too restrictive, (b) referenced signal key never set, or (c) the gate logic has a silent bug.

### Are there silent bugs in the 49 PRODUCER_LAYER_ZERO?

**Likely yes, in clusters.** The 49 strategies fall into 4 producer families with shared dependencies:

| Family | n | Likely root cause hypothesis | Fix-batch est. |
|---|---:|---|---|
| **SMC / ICT** | 18 | `backtest/signals/smc_ict.py` emits keys like `smc_bos_bullish`, `smc_choch_bearish`, `smc_fvg_bullish_active`, `smc_premium_zone_active`, etc. If the vendored smartmoneyconcepts library returns empty/None at the universe scale, the compound `s.get("smc_X", False)` returns False always. **Action**: instrument `compute_smc_signals` to log fire-rate per emitted key; verify ≥ 1% of ticker-days have each. | ~1 day |
| **classification_change** | 9 | `backtest/data/universe.py::get_classification_change_signals` emits `classification_changed_recent`, `days_since_classification_change`, `new_sector`. Producer requires sector-history from PIT data — if classification events are rare (<10/year per ticker) the AND-compound with `price_above_ema_200` + `resistance_break_retest` is multiplicative tiny. **Action**: verify emit rate per ticker-day; consider loosening AND-compound to OR. | ~0.5 day |
| **institutional** | 4 | `backtest/data/smart_money.py::institutional_signal` emits `institutional_new_positions`, `institutional_high_conviction`, `institutional_recent_init_*`. 13F-filing-derived signals fire only on filing dates (~quarterly per ticker) = ~4 events/year/ticker. AND-compound with `price_above_ema_50` further reduces. **Action**: verify filing-event emit rate; relax threshold compound. | ~0.5 day |
| **candlestick + RSI variants** | 9 | `evening_star`, `shooting_star`, `bullish_engulfing`, `rsi_9_extreme_os`, `rsi_9_rising`, `rsi_14_rising`, `rsi_21`, `bb_20_20_touch_upper`. Some of these signal keys may not be emitted by `compute_all_signals`; producer-side gap. **Action**: grep producer modules for each key; add if missing. | ~0.5 day |
| **others (camarilla, AVWAP, triangle, weekly_bias_pullback, squeeze_breakout, williams_stoch_dual, gold_silver, sector_rotation_defensive)** | 9 | Mixed; each needs individual audit | ~1 day |

**Total estimated effort**: 3.5 engineering days for full producer-zero audit + per-family fix.

---

## 3. Workstream 1 — PRODUCER_LAYER_ZERO audit framework

**Methodology** (executable framework, not yet executed at scale):

1. For each of the 49 PRODUCER_LAYER_ZERO strategies:
   - Extract `s.get("KEY")` references from the `strat_*` function body
   - Sample 100 random ticker-day pairs from the screener-passed universe
   - For each, evaluate the gate condition AND log which clause first returned False
   - Aggregate: which gate clause is the dominant fail point per strategy?

2. Cross-reference the dominant-fail key against the producer:
   - If key is NEVER set anywhere → producer gap (add producer)
   - If key is set but fires < 5% of ticker-days → low-rate producer (consider loosening or removing the clause)
   - If key fires 50%+ but the gate compounds AND with multiple low-rate clauses → relax the compound (OR instead of AND, or threshold tweak)

3. Per-family fixes:
   - SMC: vendored library audit + emit-rate instrumentation
   - classification_change: producer emit-rate check + AND→OR loosen
   - institutional: 13F filing-date alignment audit
   - candlestick/RSI: producer-key existence audit

**Concrete deliverable from this batch:** `PHASE_1A_BETA_BEST_EXIT_PER_STRATEGY.json` covers the 31 FIRED strategies. Workstream 1 (producer-zero audit) is queued as Batch 379 owner-approved scope.

---

## 4. Workstream 2 — per-(strategy × exit_method) cube analysis + best-exit recommendations

**Deliverable: `PHASE_1A_BETA_BEST_EXIT_PER_STRATEGY.json`** (17 strategies with cube cells n ≥ 5)

For each fired strategy, the best exit method by Sharpe-proxy = `mean / std × sqrt(n)`. Selected highlights:

| strategy | best_exit | n | WR | PF | mean_pp | sharpe_proxy |
|---|---|---:|---:|---:|---:|---:|
| `xs_low_beta_long` | `earnings_blackout` | 28 | 75.0% | 3.39 | +13.32 | +2.37 |
| `pre_fomc_long_sleeve` | `earnings_blackout` | 6 | 83.3% | 23.73 | +8.25 | +1.76 |
| `po3_bullish` | `earnings_blackout` | 19 | 63.2% | 3.40 | +17.94 | +1.46 |
| `pead_long` | `multi_tier_partial` | 6 | 66.7% | 4.63 | +1.36 | +1.41 |
| `xs_quality_top_quintile_long` | `trailing_15pct` | 22 | 45.5% | 2.96 | +10.07 | +1.11 |
| `xs_momentum_top_decile` | `earnings_blackout` | 8 | 50.0% | 2.17 | +27.12 | +0.83 |
| `orb_stocks_in_play_short` | `r_multiple_2r` | 21 | 38.1% | 1.28 | +1.39 | +0.48 |
| `po3_bearish` | `next_pivot_target` | 5 | 60.0% | 1.38 | +1.31 | +0.27 |
| `vix_backwardation_long` | `hybrid_50pct_target` | 9 | 33.3% | 0.74 | -1.72 | -0.41 |

**Pattern: `earnings_blackout` exit dominates for several strategies.** This is the most aggressive "let it run unless earnings within 5 days" rule. It works particularly well for momentum-quality strategies (xs_*, po3_*) that benefit from holding through trend continuation.

**Pattern: `trailing_15pct` works for quality + xs strategies.** Wide trailing stop preserves trend.

**Pattern: `vix_backwardation_long` has NO positive-Sharpe exit at n ≥ 9.** Strategy itself is loss-making across all tested exits.

**STRATEGY_EXIT_OVERRIDE update recommendation** (per Phase 1B-α deployment mode, not Phase 1A-β backtest): adopt these best-exit assignments. Pre-deployment owner review required because:
- n is small (5-28 per cell) → high variance
- WR/PF based on per-trade returns, not annualized
- Cube replay assumes all exits could execute (no liquidity/slippage haircut differential)

---

## 5. Per-strategy threshold-optimization hypotheses (owner-asked addendum)

For each fired strategy, audit the entry-gate thresholds against empirical signal distributions to identify loosenable AND-clauses. **Methodology to execute in Batch 379:**

1. For each FIRED strategy, dump `signals_at_entry` distributions across fired trades
2. Compare against the strategy's gate thresholds — which thresholds are NEVER stressed (i.e., always far exceeded)? Those are LOOSE clauses and not the binding constraint.
3. Which thresholds are RIGHT AT the boundary in 80%+ of fires? Those are the BINDING constraint.
4. Loosen the binding constraint by 10-25% and re-run; expect ~2-5× more fires
5. Owner approval required before any threshold change (per CLAUDE.md hard rule)

**Current Top-10 fired strategies — initial hypotheses (manual review):**

| strategy | n | binding-clause hypothesis | optimization candidate |
|---|---:|---|---|
| `buyback_8k_recent_long` | 86 | 8K-filing recency window | extend window 7d → 14d? |
| `orb_stocks_in_play_long` | 66 | ATR-relative move + volume | relax ATR multiplier 1.5x → 1.2x? |
| `xs_low_beta_long` | 28 | xs_low_beta_decile + price_above_ema_200 | already optimized (earnings_blackout exit, +13.32pp/trade) |
| `htf_aligned_breakout_long` | 24 | weekly_bias_bull + daily breakout | check weekly_bias fire-rate |
| `xs_quality_top_quintile_long` | 22 | xs_quality_decile >= 9 | relax to >= 8 (Batch 373 noted this already) |
| `orb_stocks_in_play_short` | 21 | ATR-down + volume_spike | relax volume gate? |
| `po3_bullish` | 19 | weekly + daily bullish + close > yesterday | already optimized (+17.94pp/trade) |
| `vix_backwardation_long` | 9 | vix_term_backwardation + xs_quality >= 8 | strategy is loss-making; consider disabling pending review |
| `xs_momentum_top_decile` | 8 | xs_momentum_decile >= 10 | relax to >= 9 |
| `pead_long` | 6 | within_pead_window + positive_surprise | already restricted; expand surprise threshold |

**Action**: per-strategy threshold tuning to be executed Batch 379 with owner approval per threshold change (CLAUDE.md: "Never change rules, filters, thresholds, or parameters without approval").

---

## 6. Workstream 3 — cap-saturation triage (MOOT after Batch 377)

The cap was the dominant rejection layer (~56 strategies blocked). Batch 377 removed the cap for Phase 1A-β cube evaluation (`--no-portfolio-cap` auto-enabled when `--phase=1a-beta`). Re-engaged for Phase 1B-α production-like.

**Next 1A-β run will admit all 56 previously-cap-blocked strategies' candidates.** Expected trade count: 5,000-15,000 (vs 361 prior). Need to confirm via partial Stage D 150-tkr pilot before launching full 1937-tkr run.

---

## 7. Recommended next batches

1. **Batch 379**: Workstream 1 executes — instrument `strat_*` functions with logging that records which AND-clause first returned False for each non-fire. Run partial Stage D 150-tkr to capture per-strategy clause-fail distribution. Cluster the 49 PRODUCER_LAYER_ZERO into "true producer gap" vs "compound-too-restrictive" buckets.

2. **Batch 380**: Workstream 2 threshold-optimization — per fired strategy, propose 1-2 threshold relaxations based on empirical distributions in `signals_at_entry`. Owner-approval-gate every change.

3. **Batch 381** (only after 379 + 380): Stage D 150-tkr pilot RE-RUN with:
   - `--no-portfolio-cap` (Batch 377)
   - Producer-gap fixes from Batch 379
   - Threshold relaxations from Batch 380
   - Compare trade-count + verdict-cube vs baseline; if 10-50× more trades → proceed Phase 1A-β full 1937-tkr.

4. **Batch 382**: Phase 1A-β full re-run on Hetzner with intermediate-progress monitor armed (`scripts/monitor_phase_1a_beta_health.sh`).

---

## References

- `PHASE_1A_BETA_PER_STRAT_EXIT_FORENSIC.md` (Batch 376)
- `PHASE_1A_BETA_BEST_EXIT_PER_STRATEGY.json` (Batch 378 deliverable)
- Memory `feedback_monitor_intermediate_counts.md` (Batch 377 process learning)
- DEC-426 5-Gate validity (Batch 375 wired to config)
- Batch 377 `--no-portfolio-cap` flag (this batch's structural fix)
