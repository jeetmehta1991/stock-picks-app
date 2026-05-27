# Stage D 150-tkr Pilot — Batch 381 validation report

**Source (per CHECKLIST #77 canonical-source attribution):** owner directive 2026-05-26 "Execute till batch 381" + queued in `PHASE_1A_BETA_OPTIMIZATION_FRAMEWORK.md` §7. Pilot validates Batch 377 (`--no-portfolio-cap` for `--phase=1a-beta`) + Batch 379+380 deliverables before any Phase 1A-β full re-run (Batch 382 paused per owner directive).

## Run config

- Universe: 150 Stage D stratified tickers (`scripts/stage_d_tickers.txt`)
- Window: 2024-01-01 → 2025-01-01 (~252 trading days, 1y)
- Engine: `BacktestEngine(no_portfolio_cap=True)` — auto-enabled for `--phase=1a-beta`
- Workers: pool=8
- Wall time: ~70 min local (start 20:36, finish 21:49)
- Sample-passing rate: 79-91/92 tickers/day after liquidity gate

## Headline result vs prior 1A-β baseline

| Metric | Prior 1A-β (4y, 1937 tkr, cap@25) | Stage D pilot (1y, 150 tkr, NO CAP) |
|---|---:|---:|
| Strategies fired | 31 | 39 |
| Cap-saturation skips | ~36,700 | 0 |
| Top strategies | buyback_8k=86 / orb_long=66 | cpr_narrow_bullish=31 / po3_bullish=24 |

## 21 newly-firing strategies (the cap-removal payoff)

These strategies fired in the pilot but did NOT fire in the prior 1A-β single-batch (lost-firing or PRODUCER_LAYER_ZERO previously):

| Strategy | Pilot fires | Prior status |
|---|---:|---|
| ichimoku_cloud_breakout | 9 | 6,821 candidates → 0 (lost-firing per Batch 376 forensic) |
| smc_order_block_bounce | 7 | PRODUCER_LAYER_ZERO previously |
| smc_choch_reversal | 6 | PRODUCER_LAYER_ZERO previously |
| ultimate_oscillator | 6 | lost-firing previously |
| smc_inverse_fvg | 5 | PRODUCER_LAYER_ZERO previously |
| pivot_r1_breakout | 4 | 9,314 candidates → 0 (lost-firing per forensic) |
| bollinger_tight | 3 | lost-firing previously |
| stochrsi_oversold | 3 | lost-firing previously |
| smc_bos_continuation | 3 | PRODUCER_LAYER_ZERO previously |
| supertrend_macd | 3 | lost-firing previously |
| macd_crossover | 3 | lost-firing previously |
| adx_initiation | 2 | lost-firing previously |
| smc_fvg_retest_long | 1 | PRODUCER_LAYER_ZERO previously |
| smc_bos_retest_entry | 1 | PRODUCER_LAYER_ZERO previously |
| smc_discount_long | 1 | PRODUCER_LAYER_ZERO previously |
| Plus 6 more (donchian_10_breakout, mfi_oversold, etc.) | 1 each | lost-firing |

**Critical insight: 9 of the 49 PRODUCER_LAYER_ZERO strategies ARE producing candidates now** that cap is removed. The Batch 379 audit's "cov=0%" finding partially reflected DOWNSTREAM gate-rejection — these strategies were producing candidates but couldn't pass the cap → no fire → no signal_at_entry sample → cov appeared 0%.

This means the 49 PRODUCER_LAYER_ZERO list overestimates true producer gaps. Re-audit with the pilot trade-log will refine the count of GENUINE producer-side silent gaps.

## NEW finding — DD halt fires repeatedly when cap removed

When cap is removed and many positions enter, the portfolio drawdown grows past DEC-515 Level 6 threshold (15% portfolio DD = halt). The pilot saw DD halt fire at 8+ distinct DD levels (-22.5% / -23.5% / -25.0% / -31.0% / -34.3% / -36.2%):

```
1054 ticker_already_open_concurrent_block_bug61
 810 level_6_halt_dd_-0.310
 510 level_6_halt_dd_-0.343
 510 level_6_halt_dd_-0.362
 450 level_6_halt_dd_-0.250
 270 level_6_halt_dd_-0.235
 240 level_6_halt_dd_-0.225
```

**Implication for Phase 1A-β cube evaluation:**
- Phase 1A-β does NOT deploy actual capital - it's a per-(strategy × exit × regime) cell-verdict computation.
- The DD halt is a CAPITAL-PROTECTION gate designed for live trading, NOT a cell-verdict gate.
- For Phase 1A-β cube evaluation, the DD halt should ALSO be removed (similar to the cap).
- For Phase 1B-α agent overlay testing, the DD halt re-engages (because Phase 1B-α uses Anthropic API budget = real cost).

**Owner decision needed for Batch 382:**
- (a) Add `--no-dd-halt` flag, auto-enable for `--phase=1a-beta` (like Batch 377 did for cap)
- (b) Keep DD halt; accept that Phase 1A-β trade counts cap at ~halt-trigger threshold
- (c) Raise DD halt threshold from 15% to 50% for 1A-β (capital-loss-evaluation only)

## Ticker-uniqueness BUG-61 gate

`ticker_already_open_concurrent_block_bug61` fired 1054 times in the pilot. This is the one-position-per-ticker rule. For cube evaluation, this is a real-world constraint, but the cube replay already simulates all 25 exits per trade, so we don't strictly need to admit multiple concurrent positions per ticker to evaluate exit-method effectiveness. **Recommendation**: keep the ticker-uniqueness gate even for Phase 1A-β.

## Pilot success criteria

| Criterion | Target | Actual | Status |
|---|---|---:|---|
| Cap-saturation skips = 0 | 0 | 0 | OK |
| Newly firing strategies | >=10 | 21 | OK |
| Engine pipeline runs clean | no crashes | clean | OK |
| Trade-rate uplift | >=3x per ticker-day | varies; DD-halt-bound | WARN |
| DD halt response | bounded by halt threshold | repeatedly firing | WARN new finding |

## What Batch 382 (paused) would do

If/when owner unpauses:
1. Apply DD-halt decision from owner above
2. Re-launch Phase 1A-β full (1937 tkrs × 4y) on Hetzner with intermediate-progress monitor
3. Use `scripts/monitor_phase_1a_beta_health.sh` to track cumulative trade count vs baseline 7.13 trades/day
4. Abort early at < 0.5× baseline ratio

## Deliverables

- `PHASE_1A_BETA_STAGE_D_PILOT_BATCH_381.md` (this doc)
- `PHASE_1A_BETA_STAGE_D_PILOT_BATCH_381.json` (machine-readable summary)
- `output_stage_d_batch381_pilot/` (full backtest output: trade_log, cube, verdict_cube, skipped, etc.)

## Cross-references

- `PHASE_1A_BETA_OPTIMIZATION_FRAMEWORK.md` (Batch 378)
- `PHASE_1A_BETA_PRODUCER_ZERO_AUDIT.json` (Batch 379)
- `PHASE_1A_BETA_THRESHOLD_OPTIMIZATION.json` (Batch 380)
- Memory `feedback_monitor_intermediate_counts.md`
- Batch 377: `--no-portfolio-cap` auto-enable
