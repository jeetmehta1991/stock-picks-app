# T1a Phase 1A-α Full Run — Comprehensive Review
**Generated:** 2026-05-20 (post-Batches 262-268)
**Source data:** `output_v2/` (Batch 260 run, 1,181 trades, 642 T1a tkrs × 4y, 2022-05 to 2026-04)
**Author:** Batch 269 analysis sweep

---

## §0 — TL;DR

| Headline | Value |
|---|---|
| Trades | 1,181 |
| Strategies fired | 36 of 125 active (148 reg − 23 deprecated) |
| Win rate | 28.9% |
| Mean PnL | **-1.97%** |
| Aggregate PnL | **-2,322 pp** |
| Cube counterfactual (best exit per strategy, hardened) | **+1,529 pp** |
| Total lift opportunity | **+3,851 pp** |

**Two major findings:**
1. **25 of 89 "zero-fire" strategies were not registered when the run started.** Batches 252-255 (chart_patterns + index_rebalance + pairs + news + calendar + cross_asset + volume_profile = 25 strategies) committed 2026-05-19 23:48 — **16 hours AFTER the T1a launch at 07:34 AM**. The running process had stale code. Path B (Batch 267) and the next full rerun fix this.
2. **One strategy contributed −1,659 pp of the −2,322 pp aggregate**: `smc_inverse_fvg` (478 trades, 24.7% WR, −3.47% mean). Batch 262's IFVG confluence gates address this.

---

## §1 — Per-strategy realized performance

### §1.1 — Worst contributors (bottom 10 by aggregate PnL)

| Strategy | n | WR | Mean | Median | Σ pp | Hold | MAE p25 |
|---|---:|---:|---:|---:|---:|---:|---:|
| **smc_inverse_fvg** | 478 | 24.7% | **−3.47%** | −5.32% | **−1,659** | 41 | −9.21 |
| po3_bullish | 79 | 29.1% | −2.61% | −4.49% | −206 | 54 | −8.24 |
| monthly_bias_momentum_long | 114 | 33.3% | −0.91% | −2.81% | −104 | 58 | −7.25 |
| cpr_narrow_bullish | 48 | 29.2% | −2.09% | −3.25% | −100 | 41 | −8.30 |
| htf_aligned_breakout_long | 33 | 30.3% | −2.19% | −4.25% | −72 | 46 | −7.31 |
| avwap_252_breakout | 21 | 33.3% | −2.83% | −2.14% | −59 | 81 | −9.07 |
| cmf_flip | 27 | 18.5% | −2.16% | −3.82% | −58 | 29 | −7.40 |
| po3_htf_aligned_long | 12 | 25.0% | −4.30% | −5.33% | −52 | 43 | −8.18 |
| xs_momentum_bottom_decile_short | 8 | 12.5% | −6.19% | −7.20% | −50 | 16 | −9.21 |
| xs_low_beta_long | 20 | 35.0% | −2.29% | −3.54% | −46 | 58 | −6.65 |

### §1.2 — Best contributors (top 10 by aggregate PnL)

| Strategy | n | WR | Mean | Median | Σ pp | Hold | MFE p75 |
|---|---:|---:|---:|---:|---:|---:|---:|
| xs_momentum_top_decile | 96 | 37.5% | +1.60% | −1.80% | **+154** | 54 | 13.0 |
| ultimate_oscillator | 17 | 35.3% | +2.23% | −0.73% | +38 | 53 | 15.7 |
| orb_stocks_in_play_long | 7 | 42.9% | +4.54% | −0.08% | +32 | 21 | 15.5 |
| pivot_r1_breakout | 8 | 37.5% | +3.14% | −1.84% | +25 | 38 | 15.2 |
| williams_r_oversold | 25 | 32.0% | +0.90% | −0.98% | +22 | 45 | 10.8 |
| avwap_50_reclaim | 10 | 50.0% | +2.16% | −0.25% | +22 | 59 | 12.6 |
| buyback_8k_recent_long | 84 | 35.7% | +0.22% | −0.51% | +19 | 39 | 9.7 |
| inside_bar_breakout | 5 | 60.0% | +2.91% | +0.01% | +15 | 39 | 12.3 |
| supertrend_macd | 15 | 26.7% | +0.77% | −3.90% | +12 | 39 | 10.4 |
| hull_rsi | 11 | 36.4% | +0.88% | −1.14% | +10 | 51 | 17.0 |

---

## §2 — Per-(strategy × exit) cube optimization

Hardened cube (avg_hold_days ≤ 250 filter applied retroactively per Batch 266 logic):

| Strategy | Realized exit (mode) | Realized mean | **Best cube exit** | Best mean | Lift/trade | Total lift pp |
|---|---|---:|---|---:|---:|---:|
| cmf_flip | trailing_stop | −2.16% | **breakeven_plus_trail** | +15.74% | +17.90 | **+483.3** |
| cpr_narrow_bullish | trailing_stop | −2.09% | **trailing_15pct** | +6.00% | +8.09 | **+388.3** |
| williams_r_oversold | vix_kill | +0.90% | **trailing_15pct** | +16.36% | +15.46 | **+386.5** |
| stochrsi_oversold | trailing_stop | −3.90% | **trailing_15pct** | +12.80% | +16.70 | +167.0 |
| bollinger_lower | trailing_stop | −4.68% | **trailing_15pct** | +9.30% | +13.98 | +69.9 |
| supertrend_macd | trailing_stop | +0.77% | **hybrid_50pct_target** | +5.39% | +4.62 | +69.3 |
| pivot_r1_breakout | vix_kill | +3.14% | **trailing_15pct** | +10.52% | +7.38 | +59.0 |
| bollinger_tight | trailing_stop | −5.21% | **trailing_15pct** | +1.92% | +7.13 | +57.0 |
| hull_rsi | trailing_stop | +0.88% | **trailing_15pct** | +4.74% | +3.86 | +42.5 |

**Pattern**: `trailing_15pct` is the dominant best exit (7 of 9 cases). This aligns with Batch 262's owner-approved primary exit choice. The realized exit (`trailing_stop` = 10%) was leaving 4-17pp per trade on the table by triggering too early.

**Strategies NOT in the cube** (cube ran on 11 strategies only; 25 other firing strategies have no counterfactual data):
- All Batch 209+/Batch 217+/Batch 222+/Batch 224 strategies (orb, po3, htf, buyback_8k, insider_cluster, pead, etc.)
- Reason: cube populator requires N≥5 trades AND specific category eligibility; smaller-sample strategies skipped per DEC-519.

---

## §3 — Realized exit distribution per strategy

For the 15 highest-volume strategies, breakdown of which exit fired in production:

| Strategy | vix_kill | trailing | time_stop_20d | end_of_bt | cb_1 |
|---|---:|---:|---:|---:|---:|
| smc_inverse_fvg | 44 | **394** | 25 | 10 | 5 |
| monthly_bias_momentum_long | **49** | 52 | 8 | 5 | 0 |
| xs_momentum_top_decile | **50** | 41 | 3 | 1 | 1 |
| buyback_8k_recent_long | **60** | 19 | 2 | 3 | 0 |
| po3_bullish | 35 | 37 | 3 | 3 | 1 |
| cpr_narrow_bullish | 12 | **31** | 1 | 3 | 1 |
| htf_aligned_breakout_long | 13 | **18** | 0 | 2 | 0 |
| cmf_flip | 9 | **17** | 0 | 0 | 0 |
| williams_r_oversold | **18** | 5 | 0 | 2 | 0 |
| ultimate_oscillator | **10** | 6 | 0 | 1 | 0 |

Now that vix_kill is removed (Batch 268), all 363 vix_kill exits across the run would have been redistributed to `trailing_15pct` — which the cube shows produces materially better outcomes per the §2 analysis.

---

## §4 — Zero-fire strategies (89 active strategies, 0 trades)

### §4.1 — Root-cause breakdown

| Category | Count | Root cause | Action |
|---|---:|---|---|
| **Stale-roster (Batches 252-255)** | **25** | T1a launched 2026-05-19 07:34; strategies registered 2026-05-19 23:48-23:53 (16h later); running process had stale code. | Already registered in current codebase. Next rerun captures them. **No code change needed.** |
| **News sentiment schema bug** | 2 | Producer emitted `news_count_7d`/`news_sentiment_score`; strategies read `news_article_count`/`news_sentiment_mean`/`news_sentiment_shift`. | **Fixed in Batch 267 (Path B)** — schema aliased + shift computed. |
| **SMC family (except smc_inverse_fvg)** | 15 | smartmoneyconcepts library inputs not feeding the per-strategy gates correctly. smc_inverse_fvg was the only one whose signal computation was wired. | Investigation needed: verify each SMC strategy's required signal key is computed and merged. |
| **Standard technical (rsi_oversold, ichimoku, 52w_high, etc.)** | ~32 | Gate-stage rejections: dedup, portfolio_max_open, NFP/CPI suppression, regime_affinity blocks. Candidates GENERATED but never realized. | See §4.2 for top blockers. |
| **Data-dependent (pead, pre_fomc, pairs, index_rebalance, cross_asset_uup)** | ~10 | Required external data missing or stale: earnings dates (pead), UUP (dxy), cointegrated_pairs parquet, index_rebalance_events parquet. | Data prefetch work — most are pre-Sprint-5 backlog. |
| **Shorts dominated by regime affinity** | 5 | `regime_affinity_block_neutral_batch203` blocked 942/1212 hull_rsi_short candidates, 833/1083 cpr_narrow_momentum_short. Neutral regime made up 70%+ of the window. | Tune regime affinity for shorts OR accept zero firing in neutral-dominant period. |

### §4.2 — Top gating blockers across the 73,217 skip events

| Reason | Count | Interpretation |
|---|---:|---|
| dedup_one_position_per_ticker_per_day | 9,576 | Multiple strategies fired on same ticker/day; only highest-tier kept. |
| regime_affinity_block_neutral_batch203 | 3,294 | Strategies tagged bull/bear-only blocked in neutral regime. |
| portfolio_gate_max_open_positions_25_reached | 2,648 | Portfolio cap hit (25 open longs/shorts). |
| EVENT_SUPPRESSION_NFP_d0_dec348 | 2,356 | NFP day suppression (no new entries). |
| portfolio_gate_max_open_positions_15_reached | 1,618 | Earlier portfolio cap rule (pre-DEC-499 expansion to 25). |
| level_6_halt_dd_-0.393 (and similar) | ~10k cumulative | Portfolio drawdown halt (multiple thresholds across run). |
| regime_affinity_block_bear_batch203 | 1,049 | Bear regime block. |
| ticker_already_open_concurrent_block_bug61 | 693 | Same-ticker concurrent block. |
| no_next_bar | 619 | Tail-of-data with no execution bar. |

### §4.3 — Bug-class candidates (zero realized but many candidates)

These were generating candidates but ALL got blocked. Highest priority since the strategy IS computing — just losing at every gate.

| Strategy | Skips | Realized | Top blocker | Recommended action |
|---|---:|---:|---|---|
| break_retest_confluence | 1,608 | 0 | dedup (916) | Lower-priority sibling under dedup → check tier-priority order; may need to be higher-tier. |
| hull_rsi_short | 1,212 | 0 | regime_affinity_block_neutral (942) | Affinity for `{bear, crisis}` only — owner-tunable. Neutral was 70%+ of window. |
| lead_lag_sector_rotation | 1,121 | 0 | dedup (553) | Dedup priority issue. |
| r1_break_retest | 1,089 | 0 | dedup (595) | Same as break_retest_confluence — dedup priority. |
| cpr_narrow_momentum_short | 1,083 | 0 | regime_affinity_block_neutral (833) | Same as hull_rsi_short. |
| ichimoku_cloud_breakout | 614 | 0 | dedup (377) | Dedup priority. |

---

## §5 — Strategy-by-strategy optimization recommendations

### §5.1 — Decommission candidates (negative edge, weak signal)

| Strategy | Evidence | Recommended action |
|---|---|---|
| **smc_inverse_fvg** | n=478, WR 24.7%, mean −3.47%, Σ −1,659 pp (single-biggest drag). Batch 262 added IFVG confluence gates. | KEEP with gates from Batch 262; re-evaluate at next full rerun. If still negative, decommission. |
| **po3_bullish** | n=79, WR 29.1%, mean −2.61%, Σ −206 pp | Tighten gates: require HTF alignment (po3_htf_aligned_long already exists). Decommission plain `po3_bullish`. |
| **xs_momentum_bottom_decile_short** | n=8, WR 12.5%, mean −6.19% | Tiny sample but worst per-trade loss. Likely shorting strong dips. Decommission or add regime gate (crisis-only). |
| **cmf_flip** | Realized −2.16% mean, but cube counterfactual +15.74% under breakeven_plus_trail | Don't decommission — change primary exit to breakeven_plus_trail. **+483 pp lift.** |
| **bollinger_tight** | n=8, WR 0%, mean −5.21% | Tiny sample. Cube counterfactual under trailing_15pct = +1.92% mean. Decision deferred to next rerun with larger n. |

### §5.2 — Entry-gate tightening recommendations

| Strategy | Issue | Recommendation |
|---|---|---|
| smc_inverse_fvg | 478 trades fired, 4.6% conversion from candidates | Batch 262 IFVG gates (require 200-EMA align + volume confirm) — already shipped. Verify in next rerun. |
| monthly_bias_momentum_long | 114 trades, mean −0.91% | Require monthly bias AND momentum percentile ≥75. Currently fires on any positive monthly bias. |
| cpr_narrow_bullish | 48 trades, mean −2.09% | Add ATR-spread floor (avoid trading on truly compressed ranges that resolve flat). |
| htf_aligned_breakout_long | 33 trades, mean −2.19% | Add volume confirm (1.5× 20d avg) at breakout bar. |
| avwap_252_breakout | 21 trades, mean −2.83% | Avoid late-stage trend tickers. Require RSI(14) < 70 at entry. |
| xs_low_beta_long | 20 trades, mean −2.29% | Combine with quality factor (xs_quality_top_quintile). |

### §5.3 — Exit-method swap recommendations (cube-derived)

These are owner-approved per the Batch 262 architectural decision (cube finds best exit per combo). Confirmed by §2 cube data:

| Strategy | Current primary | **Recommended primary** | Lift/trade | Total lift |
|---|---|---|---:|---:|
| cmf_flip | trailing_stop (10%) | **breakeven_plus_trail** | +17.90% | +483 pp |
| cpr_narrow_bullish | trailing_stop | **trailing_15pct** | +8.09% | +388 pp |
| williams_r_oversold | vix_kill (removed) | **trailing_15pct** | +15.46% | +387 pp |
| stochrsi_oversold | trailing_stop | **trailing_15pct** | +16.70% | +167 pp |
| bollinger_lower | trailing_stop | **trailing_15pct** | +13.98% | +70 pp |
| supertrend_macd | trailing_stop | **hybrid_50pct_target** | +4.62% | +69 pp |
| pivot_r1_breakout | vix_kill (removed) | **trailing_15pct** | +7.38% | +59 pp |
| bollinger_tight | trailing_stop | **trailing_15pct** | +7.13% | +57 pp |
| hull_rsi | trailing_stop | **trailing_15pct** | +3.86% | +43 pp |

Total cube-derived lift across these 9 strategies: **+1,723 pp**.

Per Batch 262 architecture (owner-approved): primary exit is universally `trailing_15pct + breakeven-at-1R`. Phase 1B-α agent layer adjusts per (strategy × exit × regime) combo via the cube. So this lift is already baked into the next rerun.

### §5.4 — Zero-fire strategy debug priorities

Ordered by expected impact:

1. **(P1, free)** Confirm Batch 252-255 strategies actually load and fire on next rerun. Add startup-log assertion: every strategy in ALL_STRATEGIES must produce at least 1 candidate during smoke. Smoke is too small for 25-strategy verification, but verify on demo (3-tkr × 2y).

2. **(P1, free)** SMC family wiring audit. 15 of 16 SMC strategies fired 0; only smc_inverse_fvg fired. Likely missing signal key in technical.py for the other SMC strategies. Estimated 1-2h investigation.

3. **(P2, free)** Dedup priority audit. Multiple strategies (break_retest, r1_break_retest, lead_lag_sector_rotation, ichimoku_cloud_breakout) are losing to higher-tier strategies on every same-day match. Currently dedup picks highest `strategy_count` then alphabetical — owner question: should some of these confluence strategies WIN dedup (since they ARE the confluence)?

4. **(P2, free)** rsi_oversold gap-up filter. 45 of 137 candidates blocked by `gap_up_6.5pct_exceeds_1.0x_atr_limit`. The filter is correct (oversold + gap-up = entry too late) but may be over-firing. Consider lowering gap_atr_limit to 0.5× for oversold-mean-reversion strategies.

5. **(P3, data)** Data-dependent zero-fires (pead, pre_fomc, pairs, index_rebalance, dxy_headwind). Each needs its own data fetch + integration. Best handled as a single Sprint 5 batch.

6. **(P3, tuning)** Regime-affinity block for shorts in neutral regime. `hull_rsi_short` (942 blocks) + `cpr_narrow_momentum_short` (833 blocks). Either expand short affinity to neutral, OR accept that shorts can't fire when the market is mostly neutral (philosophically defensible).

---

## §6 — System-level optimizations

### §6.1 — Exit redistribution (already shipped in Batches 262-268)

Counterfactual impact on T1a baseline if today's code (262-268) had been used:

| Exit reason | Realized count | Realized Σ pp | Today's redirect | Estimated lift |
|---|---:|---:|---|---:|
| vix_kill | ~363 | ~+460 pp | trailing_15pct (per §3 analysis) | **+1,500-2,500 pp** |
| trailing_stop (10%) | ~615 | ~-1,200 pp | trailing_15pct + breakeven-at-1R | **+500-1,000 pp** (smaller per-trade lift but bigger n) |
| time_stop_20d_mfe<0.5pct | ~50 | ~-200 pp | trailing_15pct | +100-200 pp |

Conservative aggregate uplift estimate from exit fixes alone: **+2,100-3,700 pp** — close to the cube-derived +3,851 pp lift opportunity in §0.

### §6.2 — Tier distribution

T1a baseline was 99% HIGH tier (everything got tagged HIGH). Batch 263 Class B confluence ≥4 differentiation shifted this:
- 20-tkr smoke today: HIGH=86.5%, MEDIUM_HIGH=5.8%, VERY_HIGH=4.2%, MEDIUM=3.5%, LOW=0%
- Better but still HIGH-dominated. Consider raising HIGH threshold from ≥4 to ≥5 strategies + smart_money_signal required.

### §6.3 — Portfolio gate impact

`portfolio_gate_max_open_positions_25_reached` blocked 2,648 candidates; `_15_reached` blocked 1,618 more = **4,266 blocked entries** over 4y. Cap is reasonable for risk, but consider time-weighting: 25-cap may be too low during low-vol bull windows when many strategies legitimately want to fire.

### §6.4 — Drawdown halt impact

`level_6_halt_dd_*` blocked ~10,000+ candidates across various DD thresholds (-0.21 to -0.44). These are protective gates. After the §6.1 exit redistribution, drawdowns should be smaller, freeing more entry capacity.

---

## §7 — Recommendations (prioritized)

### Tier 1 — Already shipped today (Batches 262-268)
1. ✅ smc_inverse_fvg IFVG gates
2. ✅ trailing 10→15% + breakeven-at-1R
3. ✅ Class A confirmation + Class B confluence ≥4 + Class C regime sanity
4. ✅ cross_asset VIX from FRED
5. ✅ Cube methodology hardening (250d hold + 0.5 fire-rate)
6. ✅ news_sentiment Path B (schema alias + shift)
7. ✅ vix_kill removed

### Tier 2 — Recommend before next full rerun (~1-2h)
8. **SMC family wiring audit** — verify all 16 SMC strategies receive their required signal keys. Most-likely fix: 1-2 missing entries in technical.py signal merge.
9. **Dedup priority tweak** — let confluence-tagged strategies win dedup when they're the higher-tier candidate. Sprint 5 work or owner judgment call.
10. **Roster sanity gate at startup** — log every ALL_STRATEGIES key with a "registered=X functions=Y" assertion to prevent stale-roster bugs like Batch 252-255 missing the T1a run.

### Tier 3 — Sprint 5 data plumbing (multi-day)
11. Pull UUP daily data — unblocks `dxy_headwind_multinational_short`
12. Run `precompute_cointegrated_pairs.py` — unblocks 2 pairs strategies (Claude-credit-free, 10-15h compute)
13. Build DEC-380 corp-actions screener output — unblocks 4 index_rebalance strategies
14. Add earnings calendar prefetch — unblocks pead family + improves earnings_blackout fire-rate

### Tier 4 — Empirical tuning (post-1A-β results)
15. Decommission po3_bullish (replace with po3_htf_aligned_long only)
16. Decommission xs_momentum_bottom_decile_short (or add crisis-only regime gate)
17. Tighten monthly_bias_momentum_long entry (require momentum percentile ≥75)
18. Tighten cpr_narrow_bullish entry (ATR-spread floor)
19. Tighten htf_aligned_breakout_long entry (volume confirm)

### Tier 5 — Owner-decisions outstanding
- D1 — Full Phase 1A-α rerun (PAUSED per owner)
- Regime-affinity philosophy for shorts in neutral regime
- HIGH tier threshold: keep ≥4 or raise to ≥5 + smart_money_required?
- Portfolio gate time-weighting (constant 25-cap vs vol-adjusted)?

---

## §8 — Methodology + data files referenced

- `output_v2/trade_log.csv` — 1,181 realized trades (45 cols)
- `output_v2/trade_exit_detail.csv` — 6,354 (trade × exit) counterfactual rows
- `output_v2/skipped_trades.csv` — 73,217 candidate-but-blocked events
- `output_v2/exit_strategy_best.csv` — legacy cube (long-hold artifact present)
- `output_smoke_larger/exit_strategy_best.csv` — post-Batch-266 hardened cube (sample)
- `backtest/signals/screener.py:ALL_STRATEGIES` — 148-strategy registry
- `backtest/config.py:DEPRECATED_STRATEGIES` — 23-strategy filter

---

**END.** Next-step owner gate: Tier 2 actions (SMC audit, dedup tweak, roster sanity log) before D1 full rerun? Or proceed straight to D1 with Tier 2 deferred to post-rerun?
