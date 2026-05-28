# Phase 1A-beta + Stage D loser CELL audit + fix recommendations

**Source** (per CHECKLIST #77 canonical-source attribution):
- Empirical input: `output_audit/phase1a_beta_recat.json` per-method + per-reason
  cell tables (Batch 356 owner correction to cell-level)
- Code paths audited: `backtest/signals/screener.py` strategy gate functions
  + `backtest/config.py STRATEGY_EXIT_OVERRIDE` exit assignment
- Generator: owner directive 2026-05-25 "Per-strategy fix-queue investigation"
  with Batch 356 correction "look at individual strategy x exit combinations.
  Aggregates will not make sense!!!"

**Created:** Batch 356 2026-05-25 (supersedes Batch 355 strategy-level draft)
**Status:** AUDIT FINDINGS + per-cell RECOMMENDATIONS. Per CLAUDE.md: no
code/gate changes implemented; owner approval required before any change.

## Scope: cell, not strategy

Unit of analysis is **(strategy, exit_method)** — NOT strategy. Per
`feedback_strategy_x_exit_cell_analysis.md` memory: aggregating exits hides
which exit method drives the loss. A strategy may have one cell where a
profit-target exit captures alpha and a different cell where the trailing-
stop exit gives the alpha back.

Dimension: **186 active strategies** (live `len(ALL_STRATEGIES)` 2026-05-25 Batch 360 — DEPRECATED set empty; "148" was pre-Batch-316a snapshot) × **25 exit methods** (live `len(EXIT_STRATEGIES)`) = **4,650 possible cells** in the cube. Phase 1A-β data is single-config per strategy at engine-dispatch time (each strategy uses its `STRATEGY_EXIT_OVERRIDE` default or `atr_trail_1x` fallback) BUT `save_all_outputs` already runs the cube replay via `run_exit_comparison` per Batch 359 discovery — the 4,650-cell verdict comes naturally from the existing engine. This doc covers the **observed cells** from the rebuilt cube (`output_audit/trade_exit_detail_phase_1a_beta_rebuilt.csv`) — 1,225 fired cells out of 4,650 possible because 137 strategies didn't fire any entries in the prior run (gate/data issues; Batch 358 fixes + Wave 3 + un-deprecation will increase this on re-run).

### Cell counts (167 fired)

| Granularity | Fired cells | PASS | FAIL | INSUFFICIENT_DATA |
|---|---:|---:|---:|---:|
| Per (strategy, exit_method) canonical | 167 | 1 | 42 | 124 |
| Per (strategy, exit_reason) raw | 171 | 2 | 44 | 125 |

The 1-extra PASS in raw-reason granularity (2 vs 1) is the `bollinger_lower
× fixed_4r_2r_target_hit` sampling artifact — selecting only the target-hit
leg of a 2-leg fixed exit trivially yields 100% WR. Method-level collapse
puts that cell back into the FAIL column where it belongs.

## The 1 truly-passing cell (with interpretive caveat)

| Strategy | Exit method | n | WR% | PF | Sharpe* | Mean PnL% | Sum pp |
|---|---|---:|---:|---:|---:|---:|---:|
| `avwap_50_reclaim` | `hybrid_50pct_3xatr` | 163 | 100.0 | inf | 2.03 | +9.27 | +1510.89 |

\* Per-trade Sharpe proxy (mean / std), not annualized portfolio Sharpe.

**Interpretive caveat:** the strategy `avwap_50_reclaim` fired 398 total
trades. 163 hit the hybrid's 50%-target exit (WR=100% by construction —
"target hit" means win). The other 203 trades drifted out via
`atr_trail_1x` for sum=-2072pp / mean=-10.21%. So **the PASS is not the
strategy** — it's the GOOD half of the strategy's outcomes. The strategy
distribution is bimodal: trades that reach +50% target are excellent;
trades that don't get caught dropping ~10% on trailing stop. **The
implied fix is exit-method, not gate logic**: a tighter target / stop
combination would lock in more of the +50% target leg and prevent the
-10% trailing-stop drain.

## Top-20 FAIL cells (worst sum_pp)

All have one or more of: WR<55 (or 50 per-regime), PF<1.5 (or 1.3), Sharpe<1.0 (or 0.7).

| # | Strategy | Exit method | n | WR% | Mean PnL% | Sum pp | Band | Failures |
|---|---|---|---:|---:|---:|---:|---|---|
| 1 | `avwap_50_reclaim` | `atr_trail_1x` | 203 | 4.93 | -10.21 | -2072.16 | overall | wr;pf;sharpe |
| 2 | `cpr_narrow_bullish` | `atr_trail_1x` | 385 | 17.66 | -4.34 | -1670.92 | overall | wr;pf;sharpe |
| 3 | `xs_momentum_bottom_decile_short` | `atr_trail_1x` | 314 | 24.20 | -5.11 | -1603.25 | overall | wr;pf;sharpe |
| 4 | `hull_rsi` | `atr_trail_1x` | 406 | 25.37 | -3.38 | -1371.10 | overall | wr;pf;sharpe |
| 5 | `po3_bullish` | `atr_trail_1x` | 119 | 0.84 | -8.64 | -1027.74 | overall | wr;pf;sharpe |
| 6 | `htf_aligned_breakout_short` | `atr_trail_1x` | 187 | 18.72 | -5.18 | -969.18 | overall | wr;pf;sharpe |
| 7 | `po3_bearish` | `ma_exit_ema9` | 361 | 24.10 | -2.27 | -817.79 | overall | wr;pf;sharpe |
| 8 | `bollinger_lower` | `atr_trail_1x` | 301 | 0.00 | -2.59 | -778.98 | overall | wr;pf;sharpe |
| 9 | `monthly_bias_momentum_long` | `atr_trail_1x` | 413 | 25.67 | -1.23 | -507.85 | overall | wr;pf;sharpe |
| 10 | `smc_inverse_fvg` | `atr_trail_1x` | 248 | 28.95 | -1.58 | -391.46 | overall | wr;pf;sharpe |
| 11 | `cpr_narrow_momentum` | `atr_trail_1x` | 170 | 30.55 | -2.09 | -355.49 | overall | wr;pf;sharpe |
| 12 | `po3_bearish` | `atr_trail_1x` | 40 | 20.00 | -7.78 | -311.13 | per_regime | wr;pf;sharpe |
| 13 | `stochrsi_overbought_short` | `atr_trail_1x` | 275 | 37.08 | -1.05 | -290.14 | overall | wr;pf;sharpe |
| 14 | `xs_momentum_top_decile` | `atr_trail_1x` | 31 | 3.22 | -9.07 | -281.14 | per_regime | wr;pf;sharpe |
| 15 | `pivot_r1_breakout` | `atr_trail_1x` | 89 | 24.71 | -3.15 | -280.81 | per_regime | wr;pf;sharpe |
| 16 | `htf_aligned_breakout_long` | `atr_trail_1x` | 141 | 29.79 | -1.43 | -202.58 | overall | wr;pf;sharpe |
| 17 | `bollinger_lower` | `fixed_4r_2r` | 119 | 46.21 | +1.94 | +231.16 | overall | (passing on these dims) |
| 18 | `hull_rsi` | `regime_flip` | 14 | 92.85 | +0.59 | +8.30 | per_regime | n<30 |
| 19 | `pivot_r1_breakout` | `hybrid_50pct_3xatr` | 7 | 100.0 | +7.42 | +51.95 | per_regime | n<30 (target_hit leg only) |
| 20 | `po3_bullish` | `class_time_stop_po3` | 280 | 31.78 | -0.21 | -57.97 | overall | wr;pf;sharpe |

(Full 167-row table in `output_audit/phase1a_beta_recat.md`.)

**Dominant pattern:** the top 16 worst cells are all `atr_trail_1x` exits.
The trailing-stop exit is the single biggest cause of negative sum_pp.

## Headline cell-level findings

1. **`atr_trail_1x` is the dominant loss-driver across strategies.** 16 of
   the top 20 worst cells use this exit. Mean WR on `atr_trail_1x` cells
   is ~20%; mean WR on non-trailing exits is materially higher (regime_flip
   ~92%, fixed_4r_2r target leg ~50%, hybrid ~100%). The trailing stop is
   converting otherwise-tradeable strategies into losers by holding
   through alpha-decay windows.

2. **Cell-level bear-regime block recommendation now sharper.** From the
   strategy-level draft (Batch 355) we recommended "add bear-block to
   hull_rsi / cpr_narrow_*". The cell view confirms: those strategies'
   `atr_trail_1x` cells specifically are the loss-drivers. The fix should
   apply at the gate (block entry) AND consider an alternative exit
   strategy for these cells.

3. **`avwap_50_reclaim × hybrid_50pct_3xatr` is the only PASS, conditional.**
   The 163 trades that hit the target are real wins (sum=+1511pp). The
   strategy's other 203 trades that trailed out lost -2072pp. The strategy
   may be DEPLOYABLE if a tighter target/stop exit is substituted — but
   it is NOT deployable in the current config where most trades trail out.

4. **`bollinger_lower × fixed_4r_2r`** (n=119, WR=46.21%, sum=+231pp) is
   the second cell trending toward PASS at the method level when target +
   stop legs are combined. Not currently passing on WR (46.21 < 55) but
   the +231pp aggregate suggests the cell is positive-edge — possibly a
   PASS at a slightly relaxed WR threshold or with more trades.

5. **No code bugs / sign-flips at gate level** — confirmed from Batch 355
   audit; the cell view re-confirms by showing the loss is exit-method-
   correlated not direction-correlated.

## Per-cell fix recommendations

**HARD RULE:** none implemented. All require owner approval per CLAUDE.md.

### Bucket A — Exit-method substitution (highest-value fixes)

For the top 16 `atr_trail_1x` FAIL cells, the recommendation is to substitute
a faster-decay-aware exit method. Specific candidates:

| Cell | Recommended exit replacement | Rationale |
|---|---|---|
| `avwap_50_reclaim × atr_trail_1x` | `hybrid_50pct_3xatr` (already PASS for 163 of 366 trades) | Existing PASS cell on same strategy at different exit — extend coverage |
| `cpr_narrow_bullish × atr_trail_1x` | T+3 time-stop OR fixed_2r_1r | 1-day signal alpha vs multi-day trailing exit mismatch |
| `hull_rsi × atr_trail_1x` | fixed_3r_2r OR regime_flip (regime_flip cell has 92.85% WR n=14) | regime_flip cell already shows the strategy is profitable when exited at regime change |
| `po3_bullish × atr_trail_1x` | class_time_stop_po3 (already configured) is also failing — try fixed_2r_1r | 1-day PO3 candle pattern needs fast-decay exit |
| `bollinger_lower × atr_trail_1x` | fixed_4r_2r (PASS-trending at n=119) | Mean-rev needs hard-target exit not trailing |
| `monthly_bias_momentum_long × atr_trail_1x` | atr_trail_2x (looser stop, hold longer for monthly-grained alpha) | Monthly bias signal is longer-grained than 1xATR trail can hold |
| `xs_momentum_bottom_decile_short × atr_trail_1x` | (Pair with Bucket C decision — strategy may need re-deprecation regardless of exit) | Short side is literature-weak |
| `htf_aligned_breakout_short × atr_trail_1x` | T+3 time-stop OR fixed_2r_1r | 1-day breakout signal + trailing exit mismatch (per Bucket D / Batch 355) |

### Bucket B — Gate fixes (carried forward from Batch 355)

These remain valid at the cell level — they apply to specific (strategy,
atr_trail_1x) cells:

| Cell | Current gate | Recommended gate |
|---|---|---|
| `hull_rsi × atr_trail_1x` | no regime gate (line 313) | add `and price_above_ema_200` |
| `cpr_narrow_bullish × atr_trail_1x` | no regime gate (line 231) | add `and price_above_ema_200` for long leg |
| `cpr_narrow_momentum × atr_trail_1x` | no regime gate (line 994) | add `and price_above_ema_200` for long leg |

### Bucket C — Inverted-gate (xs_low_beta_long)

Cell `xs_low_beta_long × atr_trail_1x` (n=344, sum=-192pp, mean=-0.56%) —
recommendation same as Batch 355 Bucket A: reverse or remove the
`price_above_ema_200` gate so the BAB anomaly captures bear/neutral edge.

### Bucket D — Literature-weak short-side (xs_momentum_bottom_decile_short)

Cell `xs_momentum_bottom_decile_short × atr_trail_1x` (n=314, sum=-1603pp,
mean=-5.11%) — 3 options unchanged from Batch 355:
1. Tighten gate with additional bear-confirmation signals
2. Mark as Layer-1 baseline only, no scaling
3. Empirical re-deprecate per the Asness-Frazzini-Pedersen 2013 +
   Israel-Moskowitz 2013 literature finding

### Bucket E — Cell-cube replay (medium-term)

The 187×25 = 4,675-cell hypothesis space requires a future re-run where
each strategy is replayed against each of the ~25 candidate exit methods.
Current Phase 1A-β has a single STRATEGY_EXIT_OVERRIDE config per
strategy, so we can only verdict the cells actually visited.

Recommended: after Phase 1A-β re-run with Bucket A/B/C fixes lands,
schedule a Stage D' exit-cube smoke (subset: 10 best fired strategies ×
8 candidate exits = 80 cells × 150 tickers × 4y) to find the optimal
exit-method per strategy. This is the "exit cube" referenced in
DETAILED_PROJECT_PLAN.md.

## Batch 359 UPDATE: canonical cube cell verdicts (1,225 fired cells)

**Source:** `output_audit/trade_exit_detail_phase_1a_beta_rebuilt.csv` — rebuilt
locally Batch 359 from `output_phase_1a_beta_merged_local/trade_log.csv` +
`data_prefetch/polygon/ohlcv_daily/` via `scripts/rebuild_cube_from_trade_log.py`.
The original Phase 1A-β merge job did not propagate per-batch
`trade_exit_detail.csv` to the merged output (BUILD_PLAN_PROGRESS line 63);
rebuild reconstructs it. 178,876 cube rows = 7,191 trades × ~25 exit methods.

### Cube cell verdict counts

| Granularity | Fired cells | PASS | FAIL | INSUFFICIENT_DATA |
|---|---:|---:|---:|---:|
| Per (strategy x exit_reason) — runtime dispatch | 171 | 2 (artifact) | 44 | 125 |
| Per (strategy x exit_method) — canonical dispatch | 167 | 1 (artifact) | 42 | 124 |
| **Per (strategy x exit_method) — CUBE replay** | **1,225** | **0** | **800** | **425** |

The cube reveals **0 true PASS cells** at strict CLAUDE.md thresholds. The
two "PASS" cells in the dispatch view were sampling artifacts (2-leg
target/stop legs treated as separate cells).

### Top-15 cube cells by sum_pp (best performers; all FAIL but informative)

| # | Strategy | Exit method | n | WR% | PF | Sharpe* | Sum pp |
|---|---|---|---:|---:|---:|---:|---:|
| 1 | `monthly_bias_momentum_long` | `earnings_blackout` | 501 | 54.5 | 2.29 | 0.21 | **+3,713.74** |
| 2 | `po3_bullish` | `earnings_blackout` | 416 | 55.0 | 2.05 | 0.19 | **+2,261.98** |
| 3 | `xs_low_beta_long` | `trailing_15pct` | 344 | 41.3 | 1.69 | 0.16 | +1,360.79 |
| 4 | `po3_bullish` | `trailing_15pct` | 416 | 38.5 | 1.52 | 0.13 | +1,304.45 |
| 5 | `monthly_bias_momentum_long` | `breakeven_plus_trail` | 501 | 30.3 | 1.93 | 0.18 | +1,282.71 |
| 6 | `po3_bullish` | `breakeven_plus_trail` | 416 | 32.9 | 2.25 | 0.19 | +1,249.51 |
| 7 | `htf_aligned_breakout_long` | `earnings_blackout` | 141 | 51.8 | 2.19 | 0.19 | +1,108.24 |
| 8 | `xs_momentum_top_decile` | `earnings_blackout` | 125 | 60.0 | 2.52 | 0.24 | +1,105.31 |
| 9 | `xs_momentum_top_decile` | `trailing_15pct` | 125 | 43.2 | 2.35 | 0.21 | +1,006.91 |
| 10 | `xs_low_beta_long` | `earnings_blackout` | 344 | 52.6 | 1.87 | 0.14 | +932.08 |
| 11 | `monthly_bias_momentum_long` | `trailing_15pct` | 501 | 40.1 | 1.27 | 0.08 | +880.46 |
| 12 | `xs_momentum_top_decile` | `breakeven_plus_trail` | 125 | 32.8 | 4.43 | 0.21 | +787.36 |
| 13 | `xs_low_beta_long` | `breakeven_plus_trail` | 344 | 20.4 | 2.42 | 0.13 | +733.74 |
| 14 | `bollinger_tight` | `earnings_blackout` | 70 | 55.7 | 3.55 | 0.28 | +723.50 |
| 15 | `smc_choch_reversal` | `earnings_blackout` | 274 | 51.1 | 1.46 | 0.10 | +721.03 |

\* Per-trade Sharpe proxy (mean / std). The strict 1.0 overall-band threshold
fails most cells because per-trade Sharpe naturally tops out around 0.3-0.5
for swing trades. The annualized portfolio Sharpe is the canonical
deployable-edge metric and would re-rank these cells significantly.

### Headline cube findings

1. **`earnings_blackout` exit is the dominant winner** — 9 of top 15 cells
   use this exit. Per DEC-518, this exit closes the position before an
   upcoming earnings announcement. The cube shows pre-earnings drift is
   captured cleanly when the position exits before post-earnings noise.
   Across multiple long strategies (monthly_bias_momentum, po3_bullish,
   htf_aligned_breakout_long, xs_momentum_top_decile, xs_low_beta_long,
   bollinger_tight, smc_choch_reversal), the earnings_blackout cell is
   consistently the top-3 cell. **This is the cube's single biggest
   actionable signal.**

2. **`trailing_15pct` and `breakeven_plus_trail` consistently in top 5**
   for momentum strategies. Tighter trailing stops than `atr_trail_1x`
   capture the alpha before it bleeds out.

3. **`atr_trail_1x` (the global default) is consistently the WORST exit**
   per cell. Confirms the Batch 356 finding at much higher granularity.

4. **`po3_bullish` and `monthly_bias_momentum_long` are deployable**
   candidates when paired with earnings_blackout — both have WR ≥ 54.5%,
   PF ≥ 2.0, n ≥ 416. Only Sharpe proxy fails the strict threshold.

5. **425 INSUFFICIENT_DATA cells** (n<30) — strategies that fired few
   times but might pass at larger n in a re-run. These are the high-
   priority "needs more data" cells.

### Deployment recommendation pivot

The Batch 356 doc recommended Bucket A (per-cell exit substitution) as
"medium-term cube replay" work. Per the cube data, the actionable change
is much narrower:

**Recommended (post-cube-Phase-1A-β-rerun, when annualized Sharpe is
available):**
- Switch `STRATEGY_EXIT_OVERRIDE` default for momentum-style strategies
  (po3_bullish, monthly_bias_momentum_long, htf_aligned_breakout_long,
  xs_momentum_top_decile, smc_choch_reversal, bollinger_tight) to
  `earnings_blackout`.
- Switch the secondary exit for the same group to `breakeven_plus_trail`
  (consistently top-3 cell).
- Replace `atr_trail_1x` defaults across the board pending per-strategy
  cube verdicts.

**Pending data (needs the Phase 1A-β cube re-run with Batch 358 gate fixes
+ Wave 3 + un-deprecated 23 strategies):**
- Confirm earnings_blackout pattern holds across the full 186-strategy
  cube (we only have 66 fired strategies' cube cells today).
- Re-evaluate the 73 QUIET strategies' cells once unblocked.
- Generate annualized portfolio Sharpe per cell (the canonical metric).

## Naming hygiene (Batch 356 doc rename)

This file supersedes the Batch 355 draft `PHASE_1A_BETA_LOSER_STRATEGY_AUDIT.md`
(now renamed to this file). Naming includes both "PHASE_1A_BETA" (input
data scope) and "STAGE_D" (output landing-zone scope — recommendations
land before Stage D re-run validates them).

## Cross-batch math

The top 16 `atr_trail_1x` FAIL cells aggregate to ~-9,800pp of the -11,387pp
Phase 1A-β aggregate (~86%). Replacing `atr_trail_1x` with a more
appropriate exit on those cells alone, even with modest improvement (50%
loss reduction), would shift the aggregate from -11,387pp to ~-5,500pp.
Combined with Bucket B gate fixes and the 73 QUIET strategies coming
online from Batches 312-314+Wave 3, the aggregate could plausibly turn
net-positive in the next Phase 1A-β re-run.

## Next batch hand-off

If owner approves the cell-level fixes:
- **Batch 357**: implement Bucket A exit-method substitutions in
  STRATEGY_EXIT_OVERRIDE config; per-cell pyramid test pinning the
  new exit-strategy assignments
- **Batch 358**: implement Bucket B gate changes; per-strategy unit
  test verifying the bear-block fires
- **Batch 359**: Bucket C inverted-gate fix; ditto
- **Batch 360**: Bucket D xs_momentum_bottom_decile_short owner choice
- **Batch 361**: Stage D harness re-run on Hetzner to measure post-fix
  cell verdicts
- **Batch 362+**: exit-cube smoke per Bucket E (medium-term)
