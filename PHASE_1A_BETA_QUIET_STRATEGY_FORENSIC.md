# Phase 1A-β Quiet-Strategy Forensic

**Created:** Batch 315a 2026-05-24 (owner directive: forensic pass before Stage D).
**Source:** `output_phase_1a_beta_merged_local/trade_log.csv` (7191 trades, 66 fired strategies).
**Universe:** 1937 tkrs × 4y (T1a+T1c+T2+T3+ETFs).

## Counts
- Active strategies in screener at Phase 1A-β run time (Batch 218 deprecation in force): **125**
- Active strategies in screener AS OF 2026-05-25 (Batch 316a reversed Batch 218; DEPRECATED_STRATEGIES emptied for empirical validation): **148**
- The next Stage D + Phase 1A-β re-run will iterate all 148 strategies; the additional 23 are largely literature-null (Zakamulin / Marshall-Cahan / Park-Irwin / Horton / Hudson-Atanasova) and are expected to fire trades but produce verdict=FAIL. Confirmation overturns the deprecation with empirical evidence; rejection re-validates the prior decision.
- Fired ≥1 trade in Phase 1A-β: **66**
- **Quiet (0 trades): 60** at time of run.

## Already addressed in Batches 312-314 (11 strategies)
**Will fire post-Stage-D re-run, no further forensic work required:**

| Strategy | Root cause | Fixed in |
|---|---|---|
| `pead_long`, `pead_short`, `pead_with_insider_confirmation_long` | BUG-288: fiscal_year-as-string + Schema-B OHLCV in PEAD producer | Batch 312-PEAD |
| `xs_quality_top_quintile_long`, `xs_momentum_quality_combined`, `vix_backwardation_long` | BUG-289: `financials_json` stored as Python-repr STRING; `isinstance(fj, dict)` always False | Batch 312-QUALITY |
| `january_effect_small_cap_long` | BUG-290: `cap_band` consumed but no producer at signal-compute time | Batch 314 |
| `news_sentiment_long` | Batch 278 tightening too aggressive (momentum AND + count≥5) | Batch 314 Cat-2 B+C |
| `poc_magnet_long` | Threshold 2% too tight at Phase 1A-β scale | Batch 314 Cat-3 A (→4%) |
| `naked_poc_retest_long` | Threshold 1% too tight at Phase 1A-β scale | Batch 314 Cat-3 B (→2%) |

## 49 REMAINING — categorized

### Category A: Tight-by-design / literature-canonical rare conditions (13)
**Expected ≤5 fires/year — not a bug; reframe expectations or accept.**

| Strategy | Why rare |
|---|---|
| `52w_high_breakout` | Hits 52-week high — ~3-5% of S&P 500 in trending bull only |
| `52w_low_breakdown` | Symmetric short — even rarer; bear-regime gated |
| `52wh_break_retest` | Sequential 52w break THEN retest — compounds rarity |
| `bb_squeeze_volume` | Bollinger squeeze + volume confirm |
| `squeeze_breakout` | TTM squeeze release |
| `cup_and_handle_long` | O'Neil CANSLIM canonical pattern |
| `head_and_shoulders_bottom_long` | Inverse H&S chart pattern |
| `double_bottom_long` | Double-bottom chart pattern |
| `triangle_ascending_long` | Ascending triangle pattern |
| `flag_bull_long` | Bull flag pattern |
| `inside_bar_breakout` | Narrow-range day inside prior day's range |
| `pre_holiday_long`, `halloween_seasonal_long`, `totm_long` | Specific calendar windows (~10-20 days/yr) |

**Recommendation:** Re-run Stage D with current code; if any still 0 trades on 117 tkrs × 4y, reconsider gate strictness on a case-by-case basis. **No code change needed pre-Stage-D**.

### Category B: Data-missing producers (22)
**Producer returns `{}` because backing data file/cache absent. Strategies legitimately cannot fire until data lands.**

| Group | Strategies | Blocker |
|---|---|---|
| Index rebalance (4) | `post_inclusion_drift_long`, `post_inclusion_reversal_short`, `post_deletion_drift_short`, `pre_rebalance_long` | `data_prefetch/derived/index_rebalance_events.parquet` missing (Sprint 5 deliverable, DEC-380) |
| Pairs trading (2) | `pairs_mean_reversion_long`, `pairs_mean_reversion_short` | `data_prefetch/derived/cointegrated_pairs_t1a/*.parquet` missing (T5b precompute, Sprint 1) |
| Pre-FOMC (2) | `pre_fomc_long_sleeve`, `pre_fomc_quality_momentum_long` | Pre-FOMC window producer present but FOMC schedule data may be incomplete in cache; need verification |
| Cross-asset (3) | `gold_silver_risk_off_long`, `dxy_headwind_multinational_short`, `sector_rotation_defensive_long` | UUP/DXY/GLD/SLV/sector-ETF caches incomplete; `cross_asset_signals` returns partial dict |
| Multi-timeframe HTF (2) | `weekly_bias_pullback_long`, `weekly_bias_pullback_short` | Weekly/monthly bias computation per-ticker; may produce `{}` when insufficient history |
| SMC/ICT (4) | `smc_equal_highs_sweep_short`, `smc_equal_lows_sweep_long`, `smc_mitigation_block_long`, `smc_mitigation_block_short` | smartmoneyconcepts library returns sparse signals; need verification of producer-vs-consumer key match |
| News-shift (1) | `news_sentiment_shift_long` | Requires multi-day sentiment delta; Polygon news cache may not have enough density |
| Insider (1) | `insider_cluster_with_director_long` | Requires director-role flag in Quiver insider parquet — verify producer populates this key |
| Volatility regime (1) | `vix_backwardation_long` | Already addressed by Batch 312-QUALITY (depends on `xs_quality_decile`); double-check post-Stage-D |
| Misc (2) | `pivot_fib_confluence` | Requires pivot + fib alignment on same day; both producers exist so likely rare-not-broken — recheck |

**Recommendation:** Each "data-missing" sub-group needs its own follow-up:
- Index rebalance + pairs: Sprint-5/Sprint-1 deliverable (blocks ~6 strategies)
- Pre-FOMC, cross-asset, SMC, insider, news-shift: per-producer verification batch (test what's emitted for known dates with cached data; identify gap)
- Multi-timeframe HTF: producer-existence verification

### Category C: Possibly-silent-gap (case-by-case, 14)
**Producers exist + consumers exist + gates aren't obviously tight — need per-strategy investigation to determine why 0 trades.**

| Strategy | Required gates | Investigation hypothesis |
|---|---|---|
| `avwap_20high_rejection_short` | `above_avwap_20high` + rejection candle | Short gate; rejection condition may be too narrow |
| `camarilla_rsi_obv`, `camarilla_rsi_obv_short` | Triple combo Camarilla + RSI + OBV | Triple-AND too narrow |
| `cpr_narrow_momentum_short` | Narrow CPR + bearish momentum | Specific CPR width definition rare |
| `donchian_10_breakout`, `donchian_breakdown_short` | 10-day Donchian channel break | Donchian-10 captures many already-traded breakouts via other strategies (cannibalization) |
| `ichimoku_cloud_breakdown` | Bearish cloud break | Short; bear-only gate cuts firing window |
| `keltner_lower` | Keltner lower-band touch | Mean-rev short; may be heavily contested by other oversold strategies |
| `prev_day_low_breakdown` | Break of prior-day low | Short; very rare in bull markets |
| `rsi9_extreme`, `rsi_overbought_short`, `rsi_volume_200ema` | RSI 9 / 14 + volume / 200-EMA | Combos may overlap with other RSI-based strategies; check overlap math |
| `supertrend_ichimoku_adx`, `supertrend_macd_short` | Triple-AND combinations | Triple-AND combos rare by combinatorics |
| `break_retest_volume` | Break + retest + volume | Sequential 3-event requirement |
| `value_area_breakout_long` | VP value-area break + vol_spike_2x | Vol_spike retained per Dalton-Jones-Dalton; may still be tight at Phase 1A-β scale |

**Recommendation:** Targeted forensic batches (1-2 strategies per batch). For each:
1. Smoke run on 5 known tickers + 2024 H1 with debug log of gate evaluations
2. Identify which gate(s) fail most often
3. Decide per-strategy: loosen (owner-approved), remove from active list, or accept as rare

### Batch 319 (2026-05-25) — Cat-C gate audit (per-strategy boolean structure)

Static read of each Cat-C strategy's gate. **Not a smoke run** — that requires Stage D
re-run on actual data. This is a starting-hypothesis pass to inform owner-approved
loosens.

| Strategy | Direction | Gate structure (informal) | Hypothesis why 0 trades |
|---|---|---|---|
| `avwap_20high_rejection_short` | short | `above_avwap_20high` + rejection candle + 200-EMA-aware | Short on AVWAP-20-high rejection; bull markets rarely produce sustained rejection at this level |
| `camarilla_rsi_obv` | long | `near_cam_r3` + `obv_bullish` + `cmf_positive` triple | Near Camarilla R3 is rare AND triple-confirmation makes it rarer |
| `camarilla_rsi_obv_short` | short | symmetric short | Same triple-AND, less common in bull regime |
| `cpr_narrow_momentum_short` | short | `cpr_narrow` + `below_cpr` + bearish MACD | Narrow CPR is rare; combine with directional move = very rare |
| `donchian_10_breakout` | long | `dc10_breakout_up` + `vol_spike_15x` + `macd_bullish` | Triple-AND with vol_spike_1.5x; volume gate likely cuts firing window |
| `donchian_breakdown_short` | short | `dc10_breakout_dn` + `vol_spike_15x` + bearish MACD | Symmetric short; less common in bull |
| `ichimoku_cloud_breakdown` | short | `ichi_below_cloud` + `ichi_tk_cross_dn` + `adx_trending` | Cloud breakdown rare in bull regimes |
| `keltner_lower` | long | `kc_touch_lower` + `hammer` OR `obv_bullish` | Mean-rev short; competes with bollinger_lower / williams_oversold (cannibalization) |
| `prev_day_low_breakdown` | short | `below_prev_low` + `vol_spike_15x` + `not above_vwap` | Short condition; bull market rarity |
| `rsi9_extreme` | long | `rsi_9_extreme_os` + `rsi_9_rising` + `price_above_ema_200` | Same-day extreme oversold AND rising is unusual sequence — typically rising = bounce already started |
| `rsi_overbought_short` | short | `rsi_14 > 70` + `bearish_engulfing` + `not price_above_sma_50` | Short combo; rare in trending bull |
| `rsi_volume_200ema` | long | `rsi_14 < 30` + `vol_spike_2x` + `price_above_ema_200` | RSI<30 AND above 200-EMA is uncommon (oversold but in uptrend) |
| `supertrend_ichimoku_adx` | long | `supertrend_bullish` + `ichi_above_cloud` + `adx_strong` triple | Triple-trend-confirmation; very few tickers will satisfy all three concurrently |
| `supertrend_macd_short` | short | symmetric to long; bearish ST + bearish MACD + ADX | Triple-AND short; bull regime rare |
| `break_retest_volume` | long | `resistance_break_retest` + `obv_rising` + `vol_spike_2x` + 200-EMA | 4-AND sequential break-then-retest pattern |

**Recommendation buckets for owner approval (Batches 320-322):**
- **Bucket-1 (likely-loosen candidates):** `donchian_10_breakout`, `rsi_volume_200ema`, `break_retest_volume` — drop volume-spike requirement OR relax thresholds; their AND-cascade is the bottleneck, not the underlying logic. Owner-approve loosen → Stage-D re-run shows whether firing rate is reasonable.
- **Bucket-2 (regime-specific):** all the SHORT strategies (`avwap_20high_rejection_short`, `donchian_breakdown_short`, `cpr_narrow_momentum_short`, `ichimoku_cloud_breakdown`, `prev_day_low_breakdown`, `rsi_overbought_short`, `supertrend_macd_short`) — these are STRUCTURALLY rare in the 2022-2026 bull-dominant window. Don't loosen; instead codify "expected fire rate ≤5/year" + revisit when bear-window data accumulates.
- **Bucket-3 (compete-cannibalization):** `keltner_lower`, `rsi9_extreme`, `camarilla_rsi_obv*` — these may not be 0 trades because of the gate, but because the candidate ranking + per-day cap (now 30 post-Batch-314) cuts them off. Need Stage-D re-run to confirm before code changes.

**Next step:** owner reviews Bucket-1/2/3 split + approves specific loosens before any code lands. Smoke-data confirmation requires the Stage-D Hetzner re-run that's queued for after Batches 316-318 land.

## Execution sequence proposal
1. **Stage D Hetzner re-run** with current Batches 307+308+312+314+315a code — validates that the 11 already-fixed strategies fire as expected, narrows the "remaining 49" before forensic batches start
2. **Cat-B subgroup batches** (data-missing) — Sprint 1 (pairs precompute) + Sprint 5 (index rebalance events) unblock 6 strategies cleanly; per-producer verification batches for the rest
3. **Cat-C targeted forensics** — 5-10 batches of 1-2 strategies each (in priority order: rsi/donchian/keltner first since they have known consumers)
4. **Cat-A acceptance** — these are expected rare; codify expected ≤5 fires/year in test, don't loosen gates

**Total estimated effort:** ~10 batches across 5-7 working sessions, gated by owner approval per per-DEC autonomous-wiring policy.
