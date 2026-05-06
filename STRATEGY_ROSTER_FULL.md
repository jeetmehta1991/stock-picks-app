# STRATEGY_ROSTER_FULL.md — Complete per-strategy enumeration across all layers

**Created:** Pass 53 — 2026-05-06 (owner directive Option 2: consolidate every named strategy + close 4 open enumeration gaps)
**Purpose:** Single canonical view of every individually-named strategy class across Layer 1 (implemented) and Layer 2-4 (planned/proposed). Sub-doc to [CANONICAL_FACTS.md F-002](CANONICAL_FACTS.md).
**Authority:** Layer 1 names are SSOT-anchored to [`backtest/signals/screener.py:812`](backtest/signals/screener.py#L812) `ALL_STRATEGIES` registry. Layer 2-4 names are sourced from [STRATEGY_REGISTER.md](STRATEGY_REGISTER.md) + the listed DECs. **Layer 2B / 2C / 3B drafts are PROPOSED — awaiting owner approval; not yet RESOLVED-DECIDED.**

---

## Status legend

| Marker | Meaning |
|---|---|
| **✅ IMPLEMENTED** | Code exists in `screener.py`; runs in Phase 1A backtest today |
| **✅ RESOLVED-DECIDED** | Strategy class decided via DEC; spec frozen; implementation scheduled |
| **⚠ DRAFT-PROPOSED** | Name + concept drafted in this doc; **awaiting owner approval** before RESOLVED-DECIDED |
| **⏸ PENDING-FORM** | Layer 2D form-derived ICT — owner-driven enumeration once form operational |
| **🔴 PENDING-DEC** | Sub-decision flagged but not yet drafted/decided |

**Phase activation:** when each strategy fires depends on layer + sprint sequencing — Layer 1 fires now (Phase 1A); Layer 2 activates Phase 0.D (Sprint 7); Layer 3 activates Phase 1C+ (Sprint 8); Layer 4 activates per-DEC.

---

## Layer 1 — Baseline roster (✅ IMPLEMENTED; 72 strategies in code)

**Code SSOT:** `backtest/signals/screener.py:812` `ALL_STRATEGIES` dict. **PROJECT_PLAN.md §7.4** mirrors at category level.

**Counts:** 60 baseline (long-direction) + 12 dedicated shorts = **72 implemented**. Per LIMITATIONS_CAVEATS_ASSUMPTIONS.md CAV documenting code-vs-plan delta: code has 72 strategy classes. The 12 short variants extend the 60-baseline scope; not drift.

### Layer 1.A — Pivot (10 strategies)

| # | Strategy ID | Direction | Logic summary |
|---|---|---|---|
| 1 | `pivot_s1_bounce` | long | Pivot S1 support bounce |
| 2 | `pivot_s2_bounce` | long | Pivot S2 deeper-support bounce |
| 3 | `pivot_s3_capitulation` | long | Pivot S3 capitulation reversal |
| 4 | `pivot_r1_breakout` | long | Pivot R1 breakout continuation |
| 5 | `pivot_r2_continuation` | long | Pivot R2 continuation breakout |
| 6 | `cpr_narrow_bullish` | long | Narrow CPR (Central Pivot Range) bullish bias |
| 7 | `camarilla_s3_bounce` | long | Camarilla S3 reversal bounce |
| 8 | `camarilla_r3_breakout` | long | Camarilla R3 breakout |
| 9 | `prev_day_high_break` | long+short | Previous day high break (volume + VWAP confirm); short on prev-low break |
| 10 | `prev_day_low_bounce` | long | Previous day low bounce |

### Layer 1.B — Momentum (9 strategies)

| # | Strategy ID | Direction | Logic summary |
|---|---|---|---|
| 11 | `macd_crossover` | long | MACD signal-line bullish crossover |
| 12 | `macd_fast_crossover` | long | MACD fast (5/10/9) crossover |
| 13 | `hull_rsi` | long | Hull MA flip up + RSI confirmation |
| 14 | `williams_r_oversold` | long | Williams %R oversold reversal |
| 15 | `roc_burst` | long | Rate-of-change burst |
| 16 | `awesome_oscillator` | long | Awesome Oscillator bullish saucer/twin-peaks |
| 17 | `stochrsi_oversold` | long | StochRSI oversold reversal |
| 18 | `ppo_crossover` | long | PPO signal crossover |
| 19 | `ultimate_oscillator` | long | Ultimate Oscillator divergence-based reversal |

### Layer 1.C — Trend (9 strategies)

| # | Strategy ID | Direction | Logic summary |
|---|---|---|---|
| 20 | `golden_cross_50_200` | long | 50 SMA crosses above 200 SMA |
| 21 | `golden_cross_9_21` | long | Faster 9/21 EMA cross |
| 22 | `golden_cross_20_50` | long | 20/50 SMA cross |
| 23 | `parabolic_sar_flip` | long | PSAR bullish flip |
| 24 | `tema_dema` | long | TEMA crosses above DEMA |
| 25 | `ichimoku_tk_cross` | long | Ichimoku Tenkan-Kijun cross |
| 26 | `ichimoku_cloud_breakout` | long | Price breaks above Ichimoku cloud |
| 27 | `adx_initiation` | long | ADX > 25 with +DI dominant |
| 28 | `supertrend_macd` | long | SuperTrend bullish + MACD aligned |

### Layer 1.D — Mean Reversion (11 strategies)

| # | Strategy ID | Direction | Logic summary |
|---|---|---|---|
| 29 | `rsi_oversold` | long | RSI(14) < 30 reversal |
| 30 | `rsi9_extreme` | long | RSI(9) extreme < 20 |
| 31 | `rsi21_slow` | long | RSI(21) slow oversold |
| 32 | `rsi_overbought_short` | short | RSI > 70 reversal short |
| 33 | `mfi_oversold` | long | MFI < 20 + pivot support + OBV rising |
| 34 | `cmf_flip` | long | Chaikin Money Flow bullish flip |
| 35 | `bollinger_lower` | long | Bollinger lower band touch reversion |
| 36 | `bollinger_tight` | long | Bollinger band tightness pre-breakout reversion |
| 37 | `bollinger_upper_short` | short | Bollinger upper band touch + RSI overbought short |
| 38 | `keltner_lower` | long | Keltner channel lower bounce |
| 39 | `stoch_oversold` | long | Stochastic oversold cross above 20 |

### Layer 1.E — Breakout (6 strategies)

| # | Strategy ID | Direction | Logic summary |
|---|---|---|---|
| 40 | `squeeze_breakout` | long | TTM Squeeze fire-up break |
| 41 | `volume_spike_breakout` | long+short | Donchian breakout + volume spike + VWAP align |
| 42 | `52w_high_breakout` | long | 52-week high break with volume |
| 43 | `inside_bar_breakout` | long | Inside bar break + ADX trending + above VWAP |
| 44 | `force_index_breakout` | long | Elder Force Index breakout |
| 45 | `donchian_10_breakout` | long | Donchian 10-period breakout |

### Layer 1.F — Candle (6 strategies)

| # | Strategy ID | Direction | Logic summary |
|---|---|---|---|
| 46 | `morning_star` | long | Morning Star reversal pattern |
| 47 | `bullish_engulfing_support` | long | Bullish engulfing at support |
| 48 | `doji_at_support` | long | Doji indecision at support |
| 49 | `three_white_soldiers` | long | Three White Soldiers continuation |
| 50 | `shooting_star_short` | short | Shooting Star at resistance |
| 51 | `evening_star_short` | short | Evening Star reversal short |

### Layer 1.G — Confluence (9 strategies)

| # | Strategy ID | Direction | Logic summary |
|---|---|---|---|
| 52 | `rsi_volume_200ema` | long | RSI oversold + volume + above 200 EMA |
| 53 | `macd_ichimoku` | long | MACD bullish + Ichimoku cloud breakout |
| 54 | `bb_squeeze_volume` | long+short | Bollinger squeeze + volume + VWAP align |
| 55 | `pivot_fib_confluence` | long | Pivot level + Fibonacci confluence |
| 56 | `golden_cross_volume` | long | Golden cross + volume confirmation |
| 57 | `cpr_narrow_momentum` | long | Narrow CPR + momentum confirm |
| 58 | `camarilla_rsi_obv` | long | Camarilla level + RSI + OBV |
| 59 | `supertrend_ichimoku_adx` | long | SuperTrend + Ichimoku + ADX triple confluence |
| 60 | `williams_stoch_dual` | long | Williams %R + Stochastic dual oversold |

### Layer 1.H — Dedicated shorts (12 strategies)

#### Trend shorts (4)

| # | Strategy ID | Direction | Logic summary |
|---|---|---|---|
| 61 | `death_cross_50_200_volume` | short | 50 SMA crosses below 200 SMA + volume |
| 62 | `supertrend_macd_short` | short | SuperTrend bearish + MACD bearish |
| 63 | `ichimoku_cloud_breakdown` | short | Price breaks below Ichimoku cloud |
| 64 | `parabolic_sar_flip_short` | short | PSAR bearish flip |

#### Momentum shorts (3)

| # | Strategy ID | Direction | Logic summary |
|---|---|---|---|
| 65 | `macd_crossover_short` | short | MACD bearish crossover |
| 66 | `hull_rsi_short` | short | Hull MA flip down + RSI bearish |
| 67 | `stochrsi_overbought_short` | short | StochRSI overbought reversal short |

#### Breakdown shorts (3)

| # | Strategy ID | Direction | Logic summary |
|---|---|---|---|
| 68 | `donchian_breakdown_short` | short | Donchian channel breakdown |
| 69 | `52w_low_breakdown` | short | 52-week low breakdown |
| 70 | `prev_day_low_breakdown` | short | Previous day low breakdown + volume + below VWAP |

#### Confluence shorts (2)

| # | Strategy ID | Direction | Logic summary |
|---|---|---|---|
| 71 | `camarilla_rsi_obv_short` | short | Camarilla resistance + RSI + OBV short |
| 72 | `cpr_narrow_momentum_short` | short | Narrow CPR + bearish momentum confluence |

**Layer 1 total: 72 strategy classes (60 long-baseline + 12 shorts).**

---

## Layer 2 — Phase 0.D additions (DEC-045)

Phase 0.D activation gated on smartmoneyconcepts library Phase A/B/C completion per DEC-508 + CHECKLIST #71. Sprint 7 implementation.

### Layer 2A — ICT/SMC pattern strategies (✅ RESOLVED-DECIDED at pattern level; class enumeration PENDING)

Per DEC-259 enumeration. Each pattern supports 1-2 strategy classes (entry on pattern formation; entry on pattern confirmation/retest).

| # | Pattern | Strategy variants | Source | Status |
|---|---|---|---|---|
| 73 | FVG (Fair Value Gap) fill | `fvg_fill_long` + `fvg_fill_short` | smartmoneyconcepts library | RESOLVED at pattern level; 2-class variant split PENDING owner |
| 74 | BOS (Break of Structure) trend continuation | `bos_continuation_long` + `bos_continuation_short` | smartmoneyconcepts | Same |
| 75 | CHoCH (Change of Character) reversal | `choch_reversal_long` + `choch_reversal_short` | smartmoneyconcepts | Same |
| 76 | Order Block bounce | `order_block_bounce_long` + `order_block_bounce_short` | smartmoneyconcepts | Same |
| 77 | Liquidity Grab reversal | `liquidity_grab_reversal_long` + `liquidity_grab_reversal_short` | smartmoneyconcepts | Same |
| 78 | Premium-Discount zone trade | `premium_discount_long` + `premium_discount_short` | smartmoneyconcepts | Same |

**Layer 2A: 6 pattern types × 2 directional variants = 12 strategy classes (PENDING formal class enumeration in DEC commit).**

### Layer 2B — Earnings Momentum strategies (⚠ DRAFT-PROPOSED; owner-approval-gated)

Per DEC-045: "Build (~1 week, custom strategy logic)". Layer 1 already includes "Earnings momentum (post-EPS beat drift)" in Fundamental category — Layer 2B is **incremental beyond Layer 1's earnings-momentum class**. The 4 drafts below extend earnings-event handling with finer-grained variants.

| # | Strategy ID (DRAFT) | Direction | Logic summary | Inputs | Status |
|---|---|---|---|---|---|
| 79 | `pre_earnings_iv_crush_front_run` | long+short | Front-run options-IV deflation post-event; entry 1-3 days pre-EPS, exit on IV crush | Polygon Options (DEC-506 deferred) + earnings dates | ⚠ DRAFT — DEC-145 candidate |
| 80 | `guidance_raise_momentum` | long | Buy on raised guidance from 8-K filings; PEAD variant filtered by guidance language | SEC EDGAR 8-K (Sprint 4 parser) + Polygon news | ⚠ DRAFT — overlaps DEC-485-dropped transcripts; uses 8-K text only |
| 81 | `surprise_magnitude_pead` | long+short | PEAD scaled by EPS surprise magnitude (top decile of surprise drives stronger drift) | Polygon financials EPS surprise (Sprint 4 parser) | ⚠ DRAFT |
| 82 | `earnings_cluster_sector_drift` | long+short | Sector-wide earnings clustering (≥30% of sector reporting same day) creates drift in laggards (those reporting later in the cluster) | Polygon earnings dates + sector taxonomy (DEC-499) | ⚠ DRAFT |

**Layer 2B: 4 DRAFT-PROPOSED strategy classes — owner approval required to mark RESOLVED-DECIDED.**

### Layer 2C — Calendar / Seasonal strategies (⚠ DRAFT-PROPOSED; owner-approval-gated)

Per DEC-045: "Build (~1 week, trivial date math)". 5 academic-literature classics. **Note overlap with Layer 3B DEC-368** — proposed resolution: Layer 2C is the implementation home; Layer 3B DEC-368 is the meta-decision. Don't double-count.

| # | Strategy ID (DRAFT) | Direction | Logic summary | Inputs | Status |
|---|---|---|---|---|---|
| 83 | `sell_in_may_short` | short | Historical May 1 - Oct 31 weakness in equities; SPY-relative short overlay | Calendar dates only | ⚠ DRAFT |
| 84 | `january_effect_smallcap` | long | January smallcap rally (Russell 2000 vs S&P 500 spread); first 5 trading days of January | Calendar + sector ETF (IWM vs SPY) | ⚠ DRAFT |
| 85 | `santa_rally_long` | long | Dec 24 - Jan 2 (the "Santa Claus rally"); positive expectancy historically | Calendar dates only | ⚠ DRAFT |
| 86 | `fomc_drift` | long+short | Pre/post-FOMC drift — long leading into meeting day (T-2, T-1); short the day after if hawkish surprise | Calendar (FOMC meeting dates per DEC-304) + DEC-348 FOMC suppression coordination | ⚠ DRAFT — coordinate with DEC-348 |
| 87 | `turn_of_month` | long | Last 4 trading days of month + first 3 of next month (Lakonishok-Smidt anomaly) | Calendar dates only | ⚠ DRAFT |

**Layer 2C: 5 DRAFT-PROPOSED strategy classes — owner approval required.**

### Layer 2D — ICT form-derived strategies (⏸ PENDING-FORM; owner-driven enumeration)

Per owner directive Pass 53 ("doesnt yet include additional ICT strategies that will be derived from the form"). Layer 2D is reserved for ICT pattern strategies that emerge once the owner-designed strategy intake **form** is operational. The form will likely capture: pattern type, timeframe, entry/exit zone definitions, risk-reward, and any required additional signals beyond smartmoneyconcepts library defaults.

| # | Strategy ID | Status | Notes |
|---|---|---|---|
| TBD | (form-derived; count expected 5-15) | ⏸ PENDING-FORM | Owner populates this section after form operational; no Claude-drafted names per directive |

**Layer 2D: TBD — count likely 5-15 once form operational.**

---

## Layer 3 — Pass 52 RESOLVED-DECIDED additions

### Layer 3A — Chart pattern strategies (✅ RESOLVED-DECIDED; DEC-355-362)

Per DEC-355-362 closure Pass 52 turn 51. 8 base classes (10 if DEC-358 is split into 3 — Wedge / Triangle / Pennant counted separately).

| # | Strategy ID | Direction | DEC | Pattern |
|---|---|---|---|---|
| 88 | `trendline_break_retest_long` | long | DEC-355 | Trendline break + retest |
| 89 | `trendline_break_retest_short` | short | DEC-355 | Trendline break + retest (bearish) |
| 90 | `channel_breakout_retest_long` | long | DEC-356 | Channel breakout + retest |
| 91 | `channel_breakout_retest_short` | short | DEC-356 | Channel breakout + retest (bearish) |
| 92 | `range_breakout_retest_long` | long | DEC-357 | Range breakout + retest |
| 93 | `range_breakout_retest_short` | short | DEC-357 | Range breakout + retest (bearish) |
| 94 | `wedge_continuation_long` | long | DEC-358a | Wedge continuation |
| 95 | `wedge_continuation_short` | short | DEC-358a | Wedge continuation (bearish) |
| 96 | `triangle_continuation_long` | long | DEC-358b | Triangle continuation |
| 97 | `triangle_continuation_short` | short | DEC-358b | Triangle continuation (bearish) |
| 98 | `pennant_continuation_long` | long | DEC-358c | Pennant continuation |
| 99 | `pennant_continuation_short` | short | DEC-358c | Pennant continuation (bearish) |
| 100 | `head_shoulders_top_short` | short | DEC-359 | Head & Shoulders top reversal |
| 101 | `inverse_head_shoulders_long` | long | DEC-359 | Inverse H&S reversal |
| 102 | `double_top_short` | short | DEC-360 | Double top reversal |
| 103 | `double_bottom_long` | long | DEC-360 | Double bottom reversal |
| 104 | `cup_handle_long` | long | DEC-361 | Cup & Handle (bullish) |
| 105 | `cup_handle_inverse_short` | short | DEC-361 | Inverted Cup & Handle (bearish) |
| 106 | `flag_continuation_long` | long | DEC-362 | Flag continuation |
| 107 | `flag_continuation_short` | short | DEC-362 | Flag continuation (bearish) |

**Layer 3A: 20 strategy classes if all directional variants counted (8 DEC base × 2 directions; with DEC-358 split into 3 patterns × 2 = 6).**

### Layer 3B — Strategy categories (⚠ DRAFT-PROPOSED for individual strategies; categories ✅ RESOLVED-DECIDED at DEC level)

Per DEC-367-371 closure Pass 52. The DECs decided **categories + count ranges**; individual strategy names within each category are drafted below.

#### DEC-367 — Pairs / Stat Arb (3-5 strategies; ⚠ DRAFT)

| # | Strategy ID (DRAFT) | Direction | Logic summary | Status |
|---|---|---|---|---|
| 108 | `pair_trade_z_score` | long+short | Classic z-score pair entry/exit (within-sector cointegration); SPY-relative | ⚠ DRAFT |
| 109 | `cointegrated_basket_revert` | long+short | Multi-stock cointegration vector; basket revert when residual exceeds 2σ | ⚠ DRAFT |
| 110 | `sector_pair_momentum` | long+short | Within-sector pair-relative momentum (long winner, short loser) | ⚠ DRAFT |
| 111 | `etf_basket_arb` | long+short | ETF vs underlying basket NAV arbitrage when divergence > liquidity-cost | ⚠ DRAFT |

#### DEC-368 — Calendar / Seasonal (overlap with Layer 2C)

**Resolution:** Implement in Layer 2C. DEC-368 retained as meta-decision; no separate Layer 3B Calendar strategies enumerated.

#### DEC-369 — Cross-Asset (3-5 strategies; ⚠ DRAFT)

| # | Strategy ID (DRAFT) | Direction | Logic summary | Status |
|---|---|---|---|---|
| 112 | `dollar_weakness_commodity_long` | long | DXY weakness regime → commodity-sector long (XLE / XLB / GSCI proxy) | ⚠ DRAFT |
| 113 | `bond_yield_spike_short` | short | Sharp DGS10 rise (>2σ daily) → equity short (rate-sensitive sectors first) | ⚠ DRAFT |
| 114 | `gold_silver_ratio_extreme` | long+short | GSR > 90 (silver oversold relative) → silver long; GSR < 60 → gold long | ⚠ DRAFT |
| 115 | `tlt_spy_correlation_break` | long+short | Bond-equity correlation flip from negative to positive (regime transition) — short-term contrarian | ⚠ DRAFT |

#### DEC-370 — Index Rebalance (2 strategies; ⚠ DRAFT)

| # | Strategy ID (DRAFT) | Direction | Logic summary | Status |
|---|---|---|---|---|
| 116 | `sp500_inclusion_drift_long` | long | Front-run S&P 500 inclusion announcement (T+1 to effective date) — index-fund forced buying | ⚠ DRAFT |
| 117 | `nasdaq100_rebalance_drift` | long+short | NDX annual rebalance front-run (long inclusions; short deletions) | ⚠ DRAFT |

#### DEC-371 — Within-Layer-1 category gaps (≥10 strategies; ⚠ DRAFT)

DEC-371 specified at least 10 within-category gaps not yet itemized. The drafts below close that enumeration gap. **All ⚠ DRAFT — owner approval required.** Numbered to fill specific gaps in existing Layer 1 categories.

| # | Strategy ID (DRAFT) | Layer 1 category gap | Direction | Logic summary | Status |
|---|---|---|---|---|---|
| 118 | `pivot_m_pattern_short` | Pivot — bearish M-pattern | short | M-pattern (double-top variant) at pivot R1/R2 with bearish divergence | ⚠ DRAFT |
| 119 | `pivot_w_pattern_long` | Pivot — bullish W-pattern | long | W-pattern (double-bottom variant) at pivot S1/S2 with bullish divergence | ⚠ DRAFT |
| 120 | `momentum_macd_histogram_pivot` | Momentum — histogram pivots | long+short | MACD histogram peak/trough reversal (faster than crossover) | ⚠ DRAFT |
| 121 | `trend_aroon_cross` | Trend — Aroon | long+short | Aroon Up/Down cross + ADX confirm | ⚠ DRAFT |
| 122 | `mean_reversion_zscore_2sigma` | Mean Rev — z-score | long+short | Pure 20-day z-score > 2σ revert | ⚠ DRAFT |
| 123 | `breakout_consolidation_volume` | Breakout — consolidation | long+short | N-day consolidation range break with volume expansion | ⚠ DRAFT |
| 124 | `candle_hammer_at_support` | Candle — hammer | long | Hammer at pivot/MA support + volume | ⚠ DRAFT |
| 125 | `candle_hanging_man_short` | Candle — hanging man | short | Hanging man at resistance + volume | ⚠ DRAFT |
| 126 | `confluence_smartmoney_technical` | Confluence — smart money + TA | long+short | Smart money composite ≥+4 (per §10.8) AND any Layer 1 technical fires | ⚠ DRAFT |
| 127 | `confluence_macro_regime_filter` | Confluence — macro filter | long+short | Layer 1 strategy fires + macro regime ✅ for direction (e.g., bull regime + long fire) | ⚠ DRAFT |
| 128 | `breakout_post_earnings_gap_fill` | Breakout — earnings gap | long+short | Post-earnings gap that doesn't fill within 3 days → continuation in gap direction | ⚠ DRAFT |

**Layer 3B totals (DRAFT):** 4 (DEC-367) + 0 Calendar (overlap → 2C) + 4 (DEC-369) + 2 (DEC-370) + 11 (DEC-371) = **21 DRAFT-PROPOSED strategy classes.**

---

## Layer 4 — PENDING strategy-additive sub-decisions (✅ DECs named; spec PENDING owner approval)

Per STRATEGY_REGISTER.md Layer 4. DECs are logged but not yet RESOLVED-DECIDED for implementation.

| # | DEC | Strategy ID (when implemented) | Direction | Logic summary | Status |
|---|---|---|---|---|---|
| 129 | DEC-141 | `sector_neutral_hedge_overlay` | overlay | Long basket + short sector ETF to neutralize sector beta | 🔴 PENDING-DEC |
| 130 | DEC-142 | `market_neutral_long_short_spy` | overlay | Long basket + short SPY to neutralize market beta | 🔴 PENDING-DEC |
| 131 | DEC-143 | `ipo_lockup_secondary_offering_systematic` | long+short | Systematic framework: post-IPO lockup expiration (T+180), secondary-offering announcements | 🔴 PENDING-DEC (2-3 sub-strategies) |
| 132 | DEC-145 | `iv_delta_pre_earnings_pattern` | long+short | IV delta vs historical pre-earnings pattern (overlaps Layer 2B `pre_earnings_iv_crush_front_run`) | 🔴 PENDING-DEC |
| 133 | DEC-176 | (meta) `boolean_combination_strategies` | overlay | Boolean AND/OR combinations of existing strategies — multiplier on existing roster, not net-new classes | 🔴 PENDING-DEC (multiplier; not a class addition) |

**Layer 4 totals: 4 PENDING strategy classes + 1 PENDING multiplier (DEC-176).**

---

## Aggregate counts (closing the open-enumeration-gap status)

| Layer | Status | Count (after Option 2 drafts) |
|---|---|---|
| Layer 1 (✅ IMPLEMENTED) | Code SSOT | **72** (60 baseline + 12 shorts) |
| Layer 2A (✅ patterns RESOLVED; class split PENDING) | DEC-259 | **12** (6 patterns × 2 directional variants) |
| Layer 2B (⚠ DRAFT) | DEC-045 | **4** (4 strategies — was "3-5 estimated") |
| Layer 2C (⚠ DRAFT) | DEC-045 | **5** (5 strategies — was "4-6 estimated") |
| Layer 2D (⏸ PENDING-FORM) | Owner-driven | **TBD 5-15** (pending form) |
| Layer 3A (✅ RESOLVED) | DEC-355-362 | **20** (10 base × 2 directional; with DEC-358 split into 3) |
| Layer 3B (⚠ DRAFT, except DEC-368→Layer-2C) | DEC-367/369/370/371 | **21** (4+4+2+11; DEC-368 absorbed into Layer 2C) |
| Layer 4 (🔴 PENDING-DEC) | DEC-141/142/143/145/176 | **4 strategies + 1 multiplier** |
| **Sub-total of NAMED classes (excluding Layer 2D PENDING-FORM)** | | **138 strategy classes** |
| With Layer 2D estimate (5-15 mid: 10) | | **~148 strategy classes** |

**Closure of STRATEGY_REGISTER.md "Open enumeration gaps" (per Pass 53 Option 2):**

| Gap (per STRATEGY_REGISTER.md §"Open enumeration gaps") | Status after this doc |
|---|---|
| 1. Layer 2A — confirm 6 patterns × variants = N classes | **PROPOSED 12 classes** (6 × 2 directional) — owner approval to confirm directional split |
| 2. Layer 2B — Earnings momentum class enumeration | **DRAFT 4 names** above — owner approval required |
| 3. Layer 2C — Calendar strategy class enumeration | **DRAFT 5 names** above — owner approval required |
| 4. Layer 3B — DEC-371 within-category catalog (≥10 itemized) | **DRAFT 11 names** above — owner approval required |

---

## How to use this doc

**For implementers:** Layer 1 names match `screener.py` exactly — implement against those identifiers. Layer 2-4 names are DRAFT until owner approves; **do not implement DRAFT strategies without explicit RESOLVED-DECIDED status promotion**.

**For owner-review workflow:**
1. Owner reads Layers 2B / 2C / 3B drafts above
2. Owner approves / edits / rejects each per-strategy proposal
3. Approved strategies promoted: ⚠ DRAFT-PROPOSED → ✅ RESOLVED-DECIDED in this doc + AUDIT_INDEX.md DEC promotion
4. Sprint 7 / Sprint 8 implements approved set

**For Layer 2D (form-derived ICT):** Owner populates the Layer 2D table after form operational; this section is reserved/empty until then.

**For drift prevention:** This doc is sub-canonical to [CANONICAL_FACTS.md F-002](CANONICAL_FACTS.md). When this doc updates, F-002 layered roster summary should re-sync. Run `pytest backtest/tests/test_canonical_facts_alignment.py` to verify.

---

## Cross-references

- [`CANONICAL_FACTS.md` F-002](CANONICAL_FACTS.md) — strategy-roster fact (this doc is the per-strategy enumeration)
- [`STRATEGY_REGISTER.md`](STRATEGY_REGISTER.md) — layered-roster summary (categorical; this doc supersedes for per-strategy detail)
- [`PROJECT_PLAN.md` §7.4](PROJECT_PLAN.md) — Layer 1 by-category restored inline
- [`backtest/signals/screener.py:812`](backtest/signals/screener.py#L812) — `ALL_STRATEGIES` registry (Layer 1 SSOT for code)
- [`PROJECT_PLAN_ARCHIVE.md` §5/§6](PROJECT_PLAN_ARCHIVE.md) — original 60-baseline detailed enumeration
- [`AUDIT_INDEX.md`](AUDIT_INDEX.md) — DECs: 045 / 103 / 104 / 124 / 141 / 142 / 143 / 145 / 176 / 259 / 355-362 / 367-371

---

*Per CHECKLIST #1 (owner-approved Option 2); #25 (Layer 2D PENDING per directive — no Claude drafts); #43 (cross-doc — links to CANONICAL_FACTS + STRATEGY_REGISTER + PROJECT_PLAN + screener.py); #45 (this); #58 (atomic codification — single doc); #67/#67.b (per-turn doc sync — will commit + push this turn).*
