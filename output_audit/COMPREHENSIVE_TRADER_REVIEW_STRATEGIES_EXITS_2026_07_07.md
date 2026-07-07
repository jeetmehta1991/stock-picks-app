<!-- Source: per CHECKLIST #77 canonical-source; Council 294 B1248 2026-07-07 comprehensive trader review; B1249 correction 2026-07-08 -->
# COMPREHENSIVE TRADER REVIEW — 219 Strategies + 26 Exit Methods

> **🔶 B1249 CORRECTION (2026-07-08, Council 295) — Truth-Standard visible retraction.** This review flagged "4 name↔formula mismatches (possible silent gate loss)" and "2 OR-arm thesis-bypass bugs". Source verification (screener.py read, B1249) found **all six are INTENTIONAL owner-approved changes with stale names/labels, not silent losses**: `macd_ichimoku` cloud gates dropped B1139 (Council 253); `xs_quality_top_quintile_long` quintile→tercile B1193; `xs_momentum_with_smart_money_long` SM-gate dropped B1194; `vol_spike_2x_below_ema_50_short` 2x→1.5x B1200; `smc_equal_highs_sweep_short` + `turtle_soup_short` OR-arms added B1202 (all Council 278). The residual issues are (a) stale NAMES pending a rename/doc-sync decision and (b) the design question of whether B1202 OR-arms dilute thesis — answerable from Batch B trade logs sliced by which arm fired. `supertrend_macd_short` STATE-gate inconsistency IS confirmed genuine (still `supertrend_bearish` STATE per B630 while its long sibling was EVENT-converted B655). All findings ticketed in EXECUTION_QUEUE B1249.
**Date:** 2026-07-07 | **Batch:** B1248 (Council 294) | **Status:** RECOMMENDATIONS ONLY — every change below requires explicit owner approval before implementation (Critical Rule: no strategy/threshold change without sign-off)

## 0. Evidence base (all numbers EXECUTED this review unless marked otherwise)

| Artifact | What it provides |
|---|---|
| `output_batch_A_150/exit_compare.csv` | 3,458 strategy x exit cells (150-ticker Batch A run): trades, win rate, PF, ROI, max DD, hold days, composite score |
| `STRATEGY_ROSTER.md` (B1238) | All 219 gate formulas + producers (parsed 219/219 this review) |
| `backtest/engine/exit_strategies.py` | 26 exit implementations + composite_score() read at source |
| `len(ALL_STRATEGIES)` = 219 | Registry ground truth re-derived this review |
| Coverage math | 132 of 219 strategies produced >=3 trades on Batch A; **87 fire-starved** (already ledgered via Councils 235-237 quiet-fire CSV) |

**Sample caveats (DERIVED):** Batch A = 150 tickers, window dominated by 2022-2026 (mostly bull tape). "medPF" below = median profit factor across all 26 exits for that strategy — an *entry-edge robustness* proxy (a real entry edge should survive most exits). Cells with 3-10 trades are directional evidence only, NOT statistical verdicts (PASSING_CRITERIA requires n>=30/regime). `lead_lag_sector_rotation` appears in exit_compare (792 trades) but is not in the current 219 registry — data-lineage orphan, flagged for reconciliation.

---

## 1. TEN SYSTEMIC FINDINGS (what a desk head flags first)

**P0-1. The composite score selects for win rate, not expectancy.** `composite_score()` (exit_strategies.py:1567-1578) weights 40% win rate / 30% PF (clipped to 0 below PF 1.0) / 30% DD. Result: `hybrid_50pct_target` is the "recommended" exit for 30 of 132 strategies despite **median PF 0.735 and median ROI -16.4%** — the classic high-win-rate / negative-expectancy trap (takes profit at 50%-to-target, lets losers ride to a wide stop). A trader ranks exits by expectancy x frequency (avg R, PF, tail control), never by raw WR. **Rec: re-weight to ~15% WR / 45% PF (unclipped, log-scaled) / 25% DD / 15% avg-R, then re-run the cube replay. This single fix re-prices the entire best-exit map.**

**P0-2. `earnings_blackout` is a pseudo-buy-and-hold contaminating comparisons.** Median hold 692 days, median DD -219%: when no earnings calendar is known it rides to end-of-data (exit_strategies.py:524-528). The 250-day hold guardrail correctly blocks it from `recommended=True`, but it still tops raw-metric views (it "wins" 8 of 17 rows in PHASE_1A_BETA_BEST_EXIT_PER_STRATEGY.json). Its apparent alpha is market beta. **Rec: pair earnings_blackout with a 60d max-hold companion so it measures the blackout effect, not buy-and-hold; exclude `no_earnings_known` rides from cube scoring entirely.**

**P0-3. The SHORT book bleeds structurally.** The bottom-25 entry edges are ~80% SHORT (`52w_low_breakdown_pullback_short` PF 0.11, `turtle_soup_short` 0.24, `stochrsi_overbought_short` 0.42, `pead_short*` 0.36-0.42, `smc_*_short` 0.17-0.54, `week_opening_gap_fill_down` 0.44, `risk_off_bond_equity_short` 0.44, `xs_momentum_bottom_decile_short` 0.52). Equities drift up ~8-10%/yr; shorting into drift without regime conditioning is negative carry. Industry practice (AQR short-leg research; every prop desk): shorts need (a) bear/crisis regime gates, (b) a short max-hold (5-15d — shorts are trades, not investments), (c) a catalyst or distribution evidence, not merely inverted long logic. **Rec: hard STRATEGY_REGIME_AFFINITY = {bear, crisis} for ALL standalone SHORTs (waivable per strategy on cube evidence); rank SHORT cube cells preferentially against time-stop exits; elevate `feedback_structural_symmetry_not_economic_symmetry` from lesson to gate.**

**P0-4. Tight trailing stops are systematically dead.** `atr_trail_1x`, `trailing_5pct`, `mfe_lockin_trail`, `smart_money_reversal`, `atr_trail_vix_conditional`, `atr_trail_mae_conditional` cluster at ~21% median WR / PF ~0.42 / negative median ROI. A 1x-ATR trail sits inside daily noise for the median S&P name (ATR-multiple literature — Wilder 1978, LeBeau & Lucas 1992 — uses 2.5-3.5x). `atr_trail_1x` won the Phase 1A v3 archive on 29 tickers; that result did NOT generalize to 150. **Rec: retire the "atr_trail_1x default" assumption; promote `breakeven_plus_trail` (the ONLY exit with positive median ROI +41.6% and median PF 1.89 across all strategies) plus a chandelier at 2.5-3x on 22-bar extremes as default trend-exit candidates.**

**P1-5. 87 of 219 strategies are unmeasurable (fire-starved) on Batch A.** Already ledgered (Councils 235-237; 160 LOOSEN_GATE actions shipped B1188-B1204). This review adds a structural cause: ~25 of the 87 stack 4-6 AND-gates; five 40%-permissive gates joint-fire on ~1% of bars before the thesis even matters. **Rec: adopt a "3-gate budget" — thesis gate + ONE location/trend filter + ONE confirmation; overflow conditions become score-based (n_confirm >= k of m), the pattern `52w_high_breakout` already uses.**

**P1-6. Mean-reversion entries are mostly noise as specified.** `bollinger_lower` medPF 0.47, `morning_star` 0.48, `stochrsi_oversold` 0.60, `williams_r_oversold` 0.84, `cmf_flip` 0.84. Canonical daily mean reversion (Connors RSI-2; Bollinger %b) only works with: uptrend qualifier (mostly present), *deep* oversold (RSI-2 < 5 — ours are mostly RSI-14 < 40, far too shallow), and the **specific exit: close > 5-day SMA or a 2-5 day time stop — which is MISSING from our 26**. Mean-rev entries paired with trailing stops whipsaw by construction. **Rec: add `ma_exit_sma5_cross` + `time_stop_5d`; deepen oversold gates (rsi_2 < 5 class); re-rank the family.**

**P1-7. The confluence + institutional long block is the real edge.** `golden_cross_20_50` 2.69, `macd_ichimoku` 2.67, `vix_backwardation_long` 2.51, `bollinger_tight` 2.45, `smc_liquidity_sweep_reversal` 2.37, `smc_discount_long` 2.20, factor longs (`xs_quality` 1.75, `xs_momentum_top_decile` 1.70), institutional persistence (1.28-1.36 band), and every smart-money sleeve beats its base. Matches literature: trend + institutional confirmation + quality tilt. **Rec: Batch B capital-allocation logic should concentrate here; `_has_smart_money_buy` confluence is the single most reliable win-rate lift gate in the codebase (DERIVED from sleeve-vs-base pairs).**

**P1-8. Missing canonical exits.** Gaps vs industry standard: (a) Connors 5-SMA-cross exit for mean reversion; (b) opposite-band exit (enter lower BB, exit mid/upper band); (c) volatility-scaled profit target (k*ATR) paired with time stop; (d) `multi_tier_partial` exits far too early (median hold 4.2d, PF 0.58 — the 1/3-at-1R tier dominates outcomes); (e) staged trail tightening by holding age (LeBeau crawl). **Rec: add (a)-(c); re-tune (d) to 1/2-at-2R + trail remainder; deprecate the six dead 1x-class trails after one confirming cube pass.**

**P1-9. Regime affinity is unset for ~90% of the roster.** Roster shows "(no affinity = all regimes)" nearly everywhere; the per-regime verdict system then discovers affinity empirically, but wastes cube trades on regime-incoherent fires (breakout longs in bear, oversold longs in crisis). **Rec: seed ex-ante affinity priors from strategy logic (breakout/momentum-long={bull,neutral}; mean-rev-long={bull,neutral}; SHORT={bear,crisis}; capitulation/VIX={crisis,bear}); cube evidence overrides. Raises per-regime n where it matters.**

**P1-10. Producer-boolean single-gate strategies concentrate model risk.** 9+ strategies are `[Producer boolean] X` — all logic inside one producer function, no independent confirmation, thresholds invisible at strategy level (`52w_high_breakout_pullback_long`, both 52w SM sleeves, `activist_13d_long`, `m_and_a_target_long`, `mmbm_long`, `squeeze_breakout`...). **Rec: surface producer-internal thresholds into the roster; add minimum one market-context gate (trend or volume) at strategy level so a producer bug cannot silently fire the whole book.**

---
## 2. EXIT METHOD REVIEW — all 26, individually

Empirical columns: median across 133 strategy-cells with >=3 trades (EXECUTED from exit_compare.csv). "x best" = times chosen recommended=True by current composite (which P0-1 says is miscalibrated — read with that caveat).

| # | Exit | med WR | med PF | med ROI% | med DD% | med hold d | x best | Trader verdict + recommendation |
|---|---|---|---|---|---|---|---|---|
| 1 | `breakeven_plus_trail` | 0.27 | **1.89** | **+41.6** | -28.2 | 27.7 | 22 | **The best exit in the book.** Classic asymmetry: move stop to breakeven after initial move, trail loosely; low WR, big winners. KEEP as the default trend-exit candidate. Tune: entry->breakeven trigger distance deserves a cube sweep (1R vs 1.5R). |
| 2 | `regime_flip` | 0.50 | 1.26 | +19.9 | -54.2 | 28.8 | 7 | Sound concept (exit when regime turns against position); numbers identical to time_stop_20d in this sample suggesting flips rarely trigger inside 20d — verify fire rate. KEEP; consider crisis-only fast path (exit within 1 bar of crisis flag for longs). |
| 3 | `time_stop_20d` | 0.50 | 1.26 | +19.9 | -54.2 | 28.8 | 6 | Solid neutral benchmark; every book needs a pure time exit as the null hypothesis. KEEP. Note: identical medians to regime_flip imply regime_flip degenerates to its 20d fallback — check implementation coupling. |
| 4 | `class_time_stop` | 0.50 | 1.13 | +11.4 | -59.2 | 42.5 | 16 | Per-category max-days is the right idea (momentum 25d vs event 10d etc.). KEEP; audit the category map — median hold 42.5d says several categories default too long (default=momentum/25d masks unmapped categories, see P1-10 pattern). |
| 5 | `time_stop_10d` | 0.50 | 1.09 | +7.5 | -37.2 | 14.5 | 11 | The correct default for SHORTs and event trades (PEAD window is ~10d). KEEP; pair preferentially with the SHORT book (P0-3). |
| 6 | `r_multiple_3r` | 0.26 | 1.10 | +4.0 | -27.2 | 8.6 | 0 | 3R target / 1R-class stop: positive expectancy at 26% WR = math works (0.26x3 > 0.74x1). KEEP; underrated by WR-weighted composite (P0-1). |
| 7 | `next_pivot_target` | 0.53 | 0.96 | -3.4 | -30.4 | 10.9 | 7 | Structure-aware target (exit at next pivot level) — professional concept, near-breakeven result. KEEP; improve: use R2/S2 (not R1/S1) as target for breakout entries — R1 is too close, truncates winners. |
| 8 | `fixed_4r_2r` | 0.33 | 0.98 | -3.9 | -43.1 | 18.8 | 0 | 2:1 R:R (DEC-353 compliant) but 33% WR needs >2:1 realized to profit; 2R stop is wide (DD -43%). MARGINAL — candidate to merge into a k*ATR vol-scaled target family (P1-8c). |
| 9 | `r_multiple_2r` | 0.33 | 0.97 | -2.0 | -24.0 | 6.3 | 10 | Same math trap: 33% WR x 2R = breakeven before costs. Its 10 "best" picks come from WR-friendly cells. MARGINAL; prefer 3R sibling. |
| 10 | `hybrid_50pct_target` | **0.65** | 0.74 | -16.4 | -79.6 | 84.8 | **30** | **P0-1 poster child.** Highest WR, negative expectancy, 85-day median hold, catastrophic -80% median DD. Takes half at 50%-to-target then holds remainder too long. DEMOTE from default-candidate; re-tune to take-half-at-1R + trail with hard 30d cap, then re-test. |
| 11 | `ma_exit_ema9` | 0.33 | 0.86 | -8.7 | -31.4 | 7.8 | 6 | EMA9 cross exit is too fast for daily swing entries (whipsaw), too slow for scalps. MARGINAL. Better sibling: add SMA5-cross for the mean-rev family (Connors canonical, P1-8a). |
| 12 | `trailing_15pct` | 0.33 | 0.88 | -24.8 | -74.6 | 87.7 | 3 | 15% fixed trail = position rides huge drawdowns (med DD -75%). A fixed-% trail ignores per-name vol — inferior to ATR-scaled by construction. DEPRECATION CANDIDATE (keep only if some strategy's cube cell demands it). |
| 13 | `atr_trail_2x` | 0.32 | 0.88 | -8.2 | -38.0 | 15.8 | 1 | Better than 1x but still sub-1 PF. Industry chandelier default is 3x on 22-bar high; our 2x from entry-anchor is tighter still. TUNE: anchor trail on highest-high-since-entry (chandelier style), not rolling from current bar. |
| 14 | `chandelier_3x` | 0.20 | 0.78 | -11.6 | -34.0 | 13.8 | 2 | Correct construction (22-bar high, 3x ATR) but 20% WR here — suggests entries mostly never move 3xATR in favor (entry quality problem, not exit problem: see P1-5/P1-6). KEEP as trend-exit benchmark; expect this to shine once entry gates fixed. |
| 15 | `earnings_blackout` | 0.56 | 2.00 | +628.7 | -219.2 | 691.8 | 0 | **P0-2.** Not an exit — a buy-and-hold with an earnings veto. All headline numbers are beta. FIX: 60d max-hold companion + exclude no_earnings_known rides from scoring. The underlying idea (flatten before earnings) is sound risk practice and worth measuring cleanly. |
| 16 | `multi_tier_partial` | 0.44 | 0.58 | -18.5 | -22.6 | 4.2 | 7 | 1/3 at 1R + 1/3 at 2R + 1/3 trail — median hold 4.2d says the first tier fires and the remainder stops out fast. Partial-taking at 1R caps the right tail that pays for the book. RE-TUNE: 1/2 at 2R + 1/2 breakeven-trail (P1-8d). |
| 17 | `reverse_signal` | 0.22 | 0.46 | -23.1 | -30.0 | 5.0 | 2 | Exit when opposite signal fires. Conceptually elegant, empirically noise — opposite signals on daily bars fire constantly. DEPRECATION CANDIDATE except for the few strategies whose cube cell selects it (bollinger_tight best-cell PF 20.0 is a 7-trade fluke, n too small). |
| 18 | `smc_mitigation_zone` | 0.29 | 0.43 | -19.2 | -26.4 | 3.3 | 2 | Exits at SMC mitigation zones — 3.3d median hold = fires almost immediately. Zone density too high on daily bars. RESTRICT to SMC-family strategies only (its design intent) instead of all-strategy cube. |
| 19 | `trailing_10pct` | 0.33 | 0.71 | -28.6 | -59.7 | 44.1 | 0 | Between 5% (too tight) and 15% (too loose) — inherits both flaws, vol-blind. DEPRECATION CANDIDATE; ATR-scaled family covers this. |
| 20 | `trailing_5pct` | 0.29 | 0.52 | -24.3 | -35.3 | 14.1 | 0 | 5% fixed trail inside normal weekly noise for most names. DEPRECATE (P0-4). |
| 21 | `atr_trail_1x` | 0.21 | 0.42 | -24.8 | -31.8 | 5.0 | 0 | **The old default, empirically dead at scale** (P0-4). 1xATR = median 1-2 day stop-out. DEPRECATE as default; keep in cube only as the tight-trail benchmark. |
| 22 | `atr_trail_vix_conditional` | 0.22 | 0.45 | -19.7 | -31.9 | 5.7 | 0 | Widens trail when VIX high — right instinct, but base is 1x-class so still dead. RE-BASE on 2.5-3x chandelier then re-test; VIX conditioning is worth keeping. |
| 23 | `atr_trail_mae_conditional` | 0.21 | 0.42 | -24.8 | -31.8 | 5.0 | 0 | Identical medians to atr_trail_1x — the MAE-conditional branch almost never engages. Verify per-strategy MAE table population; if sparse, this is a silent no-op (CHECKLIST #106 class). RE-BASE + verify data. |
| 24 | `mfe_lockin_trail` | 0.21 | 0.43 | -24.6 | -32.4 | 4.6 | 0 | Locks in after favorable excursion — but tight base trail kills it before MFE accrues. RE-BASE wider; concept is sound (LeBeau crawl, P1-8e). |
| 25 | `smart_money_reversal` | 0.21 | 0.42 | -23.6 | -31.8 | 4.9 | 0 | Exit on SM flip. Median 4.9d hold says it degenerates to its fallback trail (SM flips are quarterly-grain data, can't fire at daily cadence). Numbers = 1x-trail clone. RESTRICT to SM-family strategies + re-base fallback wider. |
| 26 | `break_even_at_1r` | 0.08 | 0.47 | -13.7 | -28.8 | 9.5 | 1 | 8% median WR — moving stop to breakeven at exactly 1R gets tagged by normal retracement almost every time (breakeven stops sit at maximum-touch price levels). The industry lesson: breakeven + small buffer (0.2-0.3R) or wait for 1.5R. RE-TUNE with buffer. |

**Exit-suite verdict:** 26 methods but effectively 4 families (time stops, R-multiple targets, trails, event/structure exits) with 6 near-clones in the dead 1x-trail cluster. After P0-1 composite fix + P1-8 additions + deprecations, a 18-20 method suite covers more design space with less redundancy. Every exit should also carry a max-hold backstop (only time stops and class_time_stop have one today; earnings_blackout demonstrably does not).

---
## 3. STRATEGY REVIEW — all 219, by family

Columns: **Batch A** = trades n / median-PF-across-exits (FS = fire-starved, <3 trades on Batch A; verdict then rests on gate analysis + quiet-fire CSV). Verdicts: **KEEP** (edge evident or thesis sound as specified) / **TUNE** (specific gate change recommended) / **RESTRUCTURE** (thesis sound, specification wrong) / **CUT-CANDIDATE** (empirically dead + no structural fix apparent; final verdict always belongs to the cube per `no_apriori_pruning` — CUT here means "deprioritize capital, keep measuring").

### F1. 52-week high/low + break-retest (10)

The 52w-high effect is real (George & Hwang 2004 JF — 52w-high proximity beats momentum). Our LONG implementations underperform their literature because gates demand the breakout bar close strong AND volume-spike simultaneously — the GH effect is about *proximity persistence*, not breakout-day fireworks.

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `52w_high_breakout` | 9 / 0.26 | TUNE. SCORE>=1-of-5 confirmation is good design, but n=9 on 150 tickers x 4y = still starved for a 503-name universe; and medPF 0.26 says the fires it does take are chase entries. Add GH-style alternative trigger: within 2% of 52w-high for 5+ consecutive days (persistence, not breakout bar). |
| `52w_high_breakout_pullback_long` | 8 / 0.38 | TUNE. Producer-boolean (P1-10). The pullback-to-breakout-level thesis is the right way to trade 52w highs; surface producer thresholds, require pullback low >= breakout level - 0.5 ATR (tight retest), add vol_below_avg on retest bar (absorption). |
| `52w_high_breakout_with_smart_money_long` | FS | KEEP thesis (SM confluence is the book's best lift, P1-7) — starvation inherited from base 52w gate; fixing base fixes sleeve. |
| `52w_high_breakout_with_smart_money_vol_below_long` | 5 / 1.42 | KEEP. Only 5 trades but positive through most exits; the vol-below-avg variant (quiet accumulation) matches Wyckoff absorption logic better than the spike variant. |
| `52w_low_breakdown` | FS | RESTRUCTURE per P0-3: 52w-low names in an S&P universe are value-trap territory with squeeze risk; require regime={bear,crisis} + days_to_cover<3 (avoid crowded shorts) instead of just NOT short_borrow_trap. |
| `52w_low_breakdown_pullback_short` | 17 / **0.11** | CUT-CANDIDATE. Worst measured entry in the book. Shorting a bounce in a 52w-low name in a bull tape = catching rallies in names being bought for mean reversion. If kept: bear-regime-only + catalyst gate (negative PEAD or concentrated insider sell). |
| `52wh_break_retest` | FS | TUNE. Dual gates stack 5 ANDs (P1-5): year_high_break_retest AND near_52w_high AND above_ema200 AND close_above_open AND top-40pct-close. Drop the last two (retest bars close weak by nature — that IS the entry opportunity). |
| `52wl_break_retest_short` | FS | Same 5-AND stack + P0-3. Bear-regime-only; drop close-position gates. |
| `break_retest_volume` | 44 / 0.95 | TUNE. Near-breakeven across exits — the OBV gate is a weak confirm. Swap obv_bullish for retest-bar vol_below_avg + breakout-bar vol_spike_15x memory (breakout on volume, retest on quiet — Bulkowski's highest-probability sequence). |
| `break_retest_confluence` | 28 / 0.47 | RESTRUCTURE. 7 AND gates (P1-5 worst offender) yet still negative — the MACD+EMA20+EMA50 stack all measure the same trend (collinear per `feedback_avwap_redundant_with_ema_trend_filter` logic). Cut to: retest + ONE trend gate + quiet-volume retest. |
| `inside_bar_breakout` | 27 / **1.55** | KEEP. Inside-bar + ADX>20 + VWAP = compression-then-expansion with trend context; one of the few breakout entries with measured edge. Consider NR7 (narrowest-range-7) qualifier to select the tightest coils (Crabel lineage). |
| `volume_spike_breakout` | 10 / 0.52 | TUNE. DC20-break + vol_above_avg + AVWAP + close-position gates — vol_above_avg is a weak spike proxy (50%-permissive); use vol_spike_17x consistent with 52w sibling, drop the AVWAP arm (collinear with the DC20 level itself). |

### F2. Donchian / channel (6)

Turtle-lineage; canonical is 20d entry with 10d exit channel (we have no channel EXIT — gap, P1-8).

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `donchian_10_breakout` | 31 / 0.53 | TUNE. DC10 is noise-grain on daily S&P names; the added macd+close-position gates don't rescue it. Either lengthen to DC20/DC55 (turtle canonical) or accept as bull-regime-only. |
| `donchian_breakout_long` | FS | TUNE. vol_spike_12x + macd + 2 close-position gates on top of DC10 = 5-AND starvation (P1-5). 3-gate budget: dc10_breakout_up + vol_spike_12x only. |
| `donchian_breakout_retest_long` | 50 / 1.06 | KEEP. Best of family; retest logic + quiet volume is correct. Consider DC20->DC55 variant for trend-quality tickers. |
| `donchian_breakdown_short` | 6 / 0.76 | P0-3 standard treatment (bear-regime + 10d time-stop pairing). |
| `donchian_breakdown_retest_short` | 6 / **0.11** | CUT-CANDIDATE (with `52w_low_breakdown_pullback_short`, worst pair in book). Retest-shorts in bull tape = shorting successful retests. Bear-only if kept. |
| `dc20_break_retest` | 30 / 0.81 | TUNE. Sound structure; the B682 vol_below_avg swap was right. Add: retest must hold above/below the DC20 level (level integrity), currently proximity-only. |

### F3. Bollinger / Keltner / Squeeze (7)

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `bollinger_tight` | 7 / **2.45** | KEEP — 4th best entry in book. BB(20,1.5)/(20,2.0) reclaim + RSI + trend qualifier is the Connors pattern done right. Starved at n=7 though: widen the reclaim window 3d->5d, keep everything else. |
| `bollinger_lower` | 29 / 0.47 | TUNE per P1-6: reclaim-from-lower on RSI-14<40 is too shallow. Deepen to rsi_2<5 OR rsi_14<30; pair with new SMA5-cross exit. adx_ok gate: verify it's not a no-op (CHECKLIST #106). |
| `bollinger_upper_short` | FS | RESTRUCTURE. Requires BB-touch AND rsi>65 AND shooting_star same bar = 3 rare events coinciding (P1-5). Score-based: touch + 1-of-{rsi>65, shooting_star, bearish_engulfing}. P0-3 regime gate. |
| `keltner_lower` | FS | TUNE. KC-touch + candle + OBV stack; candle-OR-list is good, OBV redundant with candle logic. Drop obv gate; add above_ema_200 (currently missing trend qualifier — mean-rev long without trend filter is how crisis losses happen). |
| `bb_squeeze_volume` | FS | TUNE. Squeeze-fire (TTM squeeze lineage — Carter) + vol confirmation is sound; starvation implies squeeze_fire producer threshold too strict — audit producer BB-inside-KC parameters (20,2.0,1.5 canonical). |
| `squeeze_breakout` | 39 / 1.03 | KEEP. Producer-boolean (P1-10: surface thresholds) but works. Direction-split: currently long-only on squeeze_fire_up; a squeeze_fire_dn short (bear-regime) is the missing mirror. |
| `squeeze_setup_long` | FS | KEEP thesis, monitor. B1240/B1241 restored strict SI>=20%+DTC>=8 gates; genuinely rare setup (short-squeeze fuel + SM + catalyst + technical trigger = the full Minervini/O'Neil squeeze stack). Rarity is the point; EXPLORATORY treatment per fire-count gate. |

### F4. Trend crosses & overlays (18)

Golden/death crosses are the most-studied signals in retail literature; academic verdict (Brock-Lakonishok-LeBaron 1992, updated) — weak standalone, useful as regime filters. Ours confirm: crosses fire rarely and medPFs sit near 1 except where confluence helps.

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `golden_cross_20_50` | 6 / **2.69** | KEEP — best measured entry (small n). 20/50 crosses are infrequent per name; 150-ticker universe gives it breadth. No changes; let Batch B accumulate n. |
| `golden_cross_50_200` | 8 / 0.79 | KEEP as regime-grade signal but recognize: by the time 50 crosses 200, ~70% of the move has happened (industry consensus); it's a HOLD-confirmation not an ENTRY. Pair with pullback-entry variant: cross active + first RSI<40 dip. |
| `golden_cross_9_21` | 38 / 1.25 | KEEP. Fast cross + SMA50 filter works; the sweet spot of the family. |
| `golden_cross_volume` | FS | CUT-CANDIDATE (redundancy): 50/200 cross + volume is `golden_cross_50_200` with an extra starving gate — volume on cross day is meaningless (crosses are lagging computations, not events market participants see). Fold into base. |
| `death_cross_50_200_volume` | FS | Same redundancy + P0-3. Death cross AS REGIME INPUT is valuable — as a short-entry, it's 70%-too-late. Convert into regime_filter input rather than standalone short. |
| `supertrend_macd` | 6 / 1.87 | KEEP. B655 EVENT-conversion (flip-recent-5d) was correct; positive result validates it. |
| `supertrend_macd_short` | FS | TUNE to match long's EVENT pattern — it still uses STATE `supertrend_bearish` (99% True per B655 audit!) + macd + adx. Convert to supertrend_flip_recent_short_5d. **This is a known-broken STATE gate on the short side — inconsistency between the pair.** |
| `supertrend_ichimoku_adx` | FS | TUNE. Triple-system confluence (supertrend+ichimoku+ADX) = 3 slow systems agreeing after the move. Loosen: 2-of-3 score. |
| `tema_dema` | 130 / 0.69 | CUT-CANDIDATE. TEMA/DEMA crosses are smoothing-of-smoothing; 130 trades of sub-1 PF is a real sample saying no edge. Cube gets final word. |
| `parabolic_sar_flip` | 50 / 0.52 | CUT-CANDIDATE. PSAR flips on daily equities whipsaw notoriously (Wilder designed it for trending commodities); ADX gate didn't save it (n=50, PF 0.52). |
| `parabolic_sar_flip_short` | FS | Same; P0-3. The standalone short without even the ADX gate is strictly worse. |
| `hull_rsi` | 46 / 0.61 | TUNE. Hull MA is fast-and-smooth but the B722 EVENT-conversion left rsi gates dropped (B656); currently trend-only. Re-add ONE momentum qualifier (rsi_14 40-65 band = trending-not-exhausted). |
| `ichimoku_cloud_breakout` | 5 / 1.17 | KEEP. Full Ichimoku confluence (cloud break + TK + weekly) is a legitimately complete system; starved because complete systems fire rarely. Fine. |
| `ichimoku_cloud_breakdown` | FS | P0-3 treatment; also still STATE-based (ichi_below_cloud) vs long's EVENT (break_recent_5d) — **pair inconsistency, same class as supertrend_macd_short**. |
| `ichimoku_tk_cross` | 17 / 0.34 | CUT-CANDIDATE. TK cross alone (no cloud position) is the weakest Ichimoku signal — literature (Elliot/Linton studies) shows TK-cross-alone underperforms; our 0.34 agrees. Fold into cloud_breakout as its trigger. |
| `adx_initiation` | FS | TUNE. ADX-cross-20 + DI-direction is a fine trend-initiation concept (Wilder). Starvation: adx_cross_up_20 is a rare EVENT; widen to 5d lookback window (B643 pattern). |
| `simple_below_ema_50_short` | 171 / 0.63 | CUT-CANDIDATE. Single-gate short (below EMA50 recent) fires constantly (n=171) and loses; the definition of shorting drift. If kept: bear-regime-only converts this into a legitimate momentum short. |
| `vol_spike_2x_below_ema_50_short` | 8 / 0.60 | TUNE. NAME BUG CLASS (`feedback_vol_spike_naming_convention`): formula uses vol_spike_15x (1.5x) but name says 2x. Align name<->gate; then P0-3 treatment. |

### F5. Momentum oscillators (21)

The noisiest family. Industry reality: oscillator crosses on daily bars are entry TIMING refinements, not standalone edges. Every strategy here that pairs an oscillator with trend+location survives; every naked cross bleeds.

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `macd_crossover` | 159 / 0.86 | TUNE. Naked MACD cross, n=159, PF 0.86 — textbook noise. Add trend qualifier (above_ema_200 for LONG branch — currently NONE on long side per roster). |
| `macd_crossover_short` | 11 / 1.55 | KEEP (surprise winner, small n). Its `NOT short_borrow_trap` is its only gate — monitor whether the 11-trade result survives Batch B before celebrating. |
| `macd_fast_crossover` | 419 / 0.80 | CUT-CANDIDATE. MACD(8,21,5) fires 3x more often (n=419!) with less edge. Redundant-with-worse vs base MACD. |
| `macd_ichimoku` | 5 / 2.67 | KEEP — but roster shows its formula is just the MACD cross (the ichimoku legs appear dropped; SHORT line = plain macd cross). **AUDIT: roster formula vs name mismatch — if ichimoku gates were silently lost, this is a producer-audit finding (CHECKLIST #157 class).** |
| `ppo_crossover` | 48 / 1.09 | KEEP. PPO ~= MACD normalized; ADX gate helps. Redundancy check vs macd_crossover post-Batch B (keep the better one). |
| `awesome_oscillator` | 59 / 1.04 | KEEP marginal. AO cross + EMA20 position; Bill Williams lineage. Breakeven-ish; low priority. |
| `roc_burst` | 14 / 1.80 | KEEP. Rate-of-change turn + volume spike = momentum ignition, solid. |
| `force_index_breakout` | 239 / 0.75 | TUNE. Elder's force index needs his OWN system context (13-EMA of FI, pullback entries); our cross+EMA20 fires n=239 = far too permissive. Use FI(13) cross with 2d persistence. |
| `cmf_flip` | 254 / 0.84 | TUNE. CMF zero-cross + shallow RSI fires n=254. Chaikin's own usage: CMF divergence at range extremes, not zero-crosses. Require price at 20d range extreme. |
| `mfi_oversold` | FS | KEEP structure (MFI + pivot location + OBV is proper confluence); starvation from triple-AND. 2-of-3 score. |
| `rsi_oversold` | 30 / 0.84 | TUNE per P1-6: rsi_2<7 OR rsi_14<40 — the OR arm at RSI14<40 is shallow noise; tighten to rsi_2<5 standalone (Connors canonical), keep trend gates. |
| `rsi_overbought_short` | FS | P0-3; also rsi>65 + below_sma50 conflicts — overbought NAMES below trend are squeeze fuel. Require distribution evidence (cmf_negative). |
| `rsi21_slow` | FS | CUT-CANDIDATE. RSI-21 40/60 band crosses = the slowest, shallowest version of a signal whose fast deep version (rsi_2) is the only one with literature support. |
| `rsi9_extreme` | FS | KEEP. rsi_9 extreme-oversold + trend qualifier is the right shape; check producer threshold (extreme = <10? surface it, P1-10). |
| `rsi_volume_200ema` | FS | TUNE. RSI<40 + vol_above_avg + trend — vol-spike on an oversold bar often marks capitulation continuation, not reversal. Swap to vol_below_avg (selling exhausted). |
| `stoch_oversold` | 6 / 0.72 | MARGINAL. Stoch cross + EMA20; fold into stochrsi variants (redundant family, keep best 2 of 4 post-Batch B). |
| `stochrsi_oversold` | 145 / 0.60 | TUNE. n=145 PF 0.60: StochRSI(14) oversold-cross fires constantly. Add location gate (near_s1 OR bb_lower_touch) — oscillator + location is the only validated pattern in this family. |
| `stochrsi_overbought_short` | 300 / 0.42 | CUT-CANDIDATE. n=300, PF 0.42 — the single biggest PnL bleeder measured. Shorting overbought in a bull market, 300 times. Bear-regime-only + location if kept at all. |
| `williams_r_oversold` | 197 / 0.84 | TUNE. Same as stochrsi_oversold: add location. The rsi_2<5 OR-arm rescues some fires. |
| `williams_stoch_dual` | 28 / 1.42 | KEEP — validates the oscillator+location thesis (dual oscillator + pivot-level list, PF 1.42 vs 0.60-0.84 for naked cousins). This is the family's template. |
| `ultimate_oscillator` | 11 / 0.63 | MARGINAL. UO multi-timeframe blend is defensible; small n negative. Low priority; keep measuring. |


### F6. Candles (8)

Nison-canon patterns. Industry truth: candle patterns have near-zero standalone edge (Marshall et al. 2006 exhaustive test); they earn their keep ONLY as triggers at pre-identified levels. Our level-anchored ones confirm; our naked ones bleed.

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `bullish_engulfing_support` | 10 / **2.04** | KEEP — candle+pivot-level+OBV = the correct template. |
| `hammer_at_support_long` | 5 / 0.73 | KEEP structure; small n. Consider adding vol_below_avg (Spring test bar, B650 precedent). |
| `doji_at_support` | FS | TUNE. doji + wide-level + vol_spike_12x: doji on a volume spike is indecision-on-churn, contradictory. Drop vol gate or invert to vol_below_avg. |
| `doji_at_resistance_short` | 9 / 0.18 | CUT-CANDIDATE + same contradiction. Doji is the weakest reversal candle to short on. |
| `shooting_star_short` | FS | TUNE. Candle-list + level + RSI>65 is proper anatomy; 3-AND with rare components starves it (P1-5). Widen: rsi>60. P0-3 regime gate. |
| `morning_star` | 151 / 0.48 | RESTRUCTURE. n=151 PF 0.48 — a 3-bar pattern firing that often means the producer's star-body/gap tolerances are too loose (Nison requires gap-down star, we likely accept any small body — AUDIT producer). Then anchor at support level like engulfing template. |
| `three_white_soldiers` | 98 / 0.79 | TUNE. n=98 says producer tolerances loose here too; canonical 3WS after a DECLINE (reversal), ours fires mid-trend (continuation-chase). Add: preceding 10d decline gate. |
| `three_black_crows_short` | 83 / 0.51 | Same producer-tolerance audit + P0-3. After-advance requirement missing. |

### F7. Pivots / Camarilla / CPR (16)

Floor-trader pivots on DAILY equity bars are an intraday toolkit stretched to swing horizon — the family's persistent mediocrity here is structural, not parametric. The exceptions: multi-day capitulation/blowoff sequences (W5 redesign) and confluence stacks.

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `pivot_r1_breakout` | 21 / 0.97 | MARGINAL. R1 is one vol-unit from yesterday's close — breakout above it is a coin flip. R2 variant is the tradeable one. |
| `pivot_r2_continuation` | FS | KEEP thesis (R2 + ADX + EMA-alignment = real continuation), starved by vol_spike_2x on top. Drop to vol_above_avg. |
| `pivot_r3_blowoff_short` | FS | KEEP EXPLORATORY per B643-B652 lineage (Wyckoff buying-climax logic is sound; rare by design; DO-NOT-DEPLOY gate until cube). |
| `pivot_s1_bounce` | 40 / 0.65 | TUNE. S1-touch + hammer/pin + OBV — S1 is too shallow a dip for S&P names (hit weekly). Migrate to S2 or require confluence with AVWAP/EMA50. |
| `pivot_s2_bounce` | FS | KEEP; the deeper-level version starves because S2+RSI<45+candle triple-AND is rare — 2-of-3 score it. |
| `pivot_s3_capitulation` | FS | KEEP EXPLORATORY (B643 redesign is thoughtful: capitulation lookback + turn trigger + quiet-vol test = Wyckoff Spring/Test done right; rare-but-strong accepted per owner W5-i). |
| `pivot_fib_confluence` | FS | TUNE. Pivot+fib+candle triple-AND — score 2-of-3. |
| `r1_break_retest` | 176 / 0.94 | TUNE. n=176 (fires a lot), breakeven-ish. The AVWAP gate (above_avwap_20low) is collinear with the retest level (`feedback_avwap_redundant_with_ema_trend_filter` class). Simplify to retest + macd + quiet-vol. |
| `camarilla_r4_breakout` | 30 / 0.67 | TUNE. R4 breakout (correct level per B641 re-anchor) but vol_above_avg alone confirms weakly. Add close_in_top_40pct (currently absent here, present in cousins). |
| `camarilla_s3_bounce` | FS | KEEP; S3+RSI<40+OBV triple-AND starves — 2-of-3 score. |
| `cpr_narrow_bullish` | 103 / 0.76 | TUNE. cpr_narrow_tight (B654 0.05) + above-CPR + AVWAP + EMA200 = 4 gates measuring 2 things. Drop AVWAP arm (collinear with EMA200). n=103 PF 0.76 says narrow-CPR-day thesis needs directional confirmation, not more trend gates — add first-hour-range proxy: close_above_open. |
| `cpr_narrow_momentum` | 25 / 1.07 | KEEP marginal; the RSI+MACD version of the above; watch redundancy with sibling post-Batch B; keep the better. |
| `cpr_narrow_momentum_short` | 61 / 0.52 | P0-3 treatment; n=61 bleeding. |
| `prev_day_high_break` | 20 / 1.06 | KEEP marginal. PDH break + vol + VWAP = fine day-structure momentum. |
| `prev_day_low_bounce` | 31 / 0.90 | MARGINAL. Near-PDL + hammer + CMF: acceptable anatomy, indifferent result. Low priority. |
| `prev_day_low_breakdown` | 6 / 1.72 | KEEP (small-n positive; the only pivot-family SHORT that works — PDL break is a genuine momentum event, not a fade). |

### F8. Chart patterns (12)

Bulkowski statistics are the reference. Detection quality is everything: pattern producers with loose tolerances manufacture noise (see F6 morning_star lesson). Most of this family is fire-starved — that is EXPECTED for real patterns (a clean cup-and-handle appears ~1-2x/yr/name); the starvation concern inverts here: if a pattern strategy ISN'T rare, its producer is too loose.

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `cup_and_handle_long` | FS | KEEP EXPLORATORY (B685 marker). O'Neil canonical; B660 0-fire says detector too strict — audit `detect_cup_and_handle` rim/depth tolerances vs O'Neil spec (12-33% depth, 7-65wk length scaled to daily). |
| `cup_and_handle_retest_long` | 9 / 0.46 | TUNE. Neckline-retest variant fires (retests are more common than fresh breaks) but PF 0.46 — likely catching failed breakouts. Require retest holds ABOVE neckline (level integrity gate, same F2 dc20 rec). |
| `inverted_cup_and_handle_short` | FS | P0-3 + same detector audit (B686 producer). |
| `double_bottom_long` | FS | KEEP; Bulkowski's highest-reliability reversal. Detector audit: require 2-6wk bottom spacing + 3%+ trough depth; then Eve/Adam variants later. |
| `flag_bull_long` | FS | KEEP. flag_bull_broke + EMA200 is already minimal — starvation is detector-side (flagpole % + flag-tightness params). |
| `flag_bull_retest_long` | FS | KEEP; correct anatomy (retest + quiet vol). Detector-side audit shared with above. |
| `flag_bear_retest_short` | FS | P0-3 + detector audit. |
| `head_and_shoulders_bottom_long` | FS | KEEP; detector audit (neckline slope tolerance is where H&S detectors usually break). |
| `head_and_shoulders_top_short` | 12 / 0.43 | TUNE. Fires but loses — H&S tops in bull tape get bought. Require neckline BREAK (not just pattern-detected + below EMA200): roster shows no break gate. **Possible F1-class silent gap: pattern-detected != pattern-completed.** |
| `triangle_ascending_long` | FS | KEEP. B1121-class detect_triangle producer audit already queued (0-fire on SPY 6y = LIKELY BROKEN per Council 236 blocker #2). Producer fix is the whole story here. |
| `triangle_ascending_retest_long` | FS | Blocked by same producer. |
| `triangle_descending_short` | FS | Blocked by same producer + P0-3 when unblocked. |

### F9. SMC — Smart Money Concepts (18)

ICT/SMC on daily bars: the zone logics (discount/premium, OTE) and liquidity sweeps translate; the microstructure claims (order blocks, FVG fills as "institutional footprints") are contested. Our data agrees with that split: sweep/discount/OTE longs are top-decile; OB-bounce and FVG-retests bleed.

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `smc_liquidity_sweep_reversal` | 16 / **2.37** | KEEP — 5th best entry. Sweep + structure-shift confirm is the SMC pattern with real crowd logic (stop-run then reversal). |
| `smc_discount_long` | 14 / **2.20** | KEEP — 6th best. Buying discount zone WITH structure confirmation = buying dips with rules. |
| `smc_ote_long` | 14 / 1.42 | KEEP. 62-79% retracement entry + BOS is disciplined pullback-buying. |
| `smc_ote_short` | 11 / 0.64 | P0-3 standard treatment. |
| `smc_premium_short` | 10 / 0.45 | P0-3; also premium-zone shorting in bull drift = fading strength without a catalyst. Require sweep evidence (equal-highs swept) as extra gate. |
| `smc_bos_continuation` | 25 / 0.74 | TUNE. BOS + trend + vol + RSI>50 — by the time BOS confirms on daily bars the move is extended (same lag class as golden_cross_50_200). Prefer the retest sibling. |
| `smc_bos_retest_entry` | 56 / 0.50 | TUNE. Retest version SHOULD be the better one but PF 0.50 at n=56 — suspect retest-zone tolerance too wide (catching continuation-failures). Producer audit: retest proximity parameter. |
| `smc_choch_reversal` | 73 / 0.69 | TUNE. CHoCH+FVG at n=73 = detector too permissive (CHoCH should be rare). Tighten swing-point definition (larger swing lookback). |
| `smc_breaker_block_long` | 164 / 0.72 | RESTRUCTURE. n=164!! Breaker blocks are supposed to be scarce; producer emits zone-active STATE, strategy fires daily while state true (STATE-vs-EVENT class, `feedback_signal_temporality_event_vs_state`). Convert to first-touch EVENT. |
| `smc_breaker_block_short` | 89 / 0.54 | Same STATE->EVENT conversion + P0-3. |
| `smc_order_block_bounce` | 100 / 0.47 | Same STATE->EVENT + n=100 bleeding; OB-zone density on daily bars is too high — keep only HTF (weekly-derived) OBs. |
| `smc_mitigation_block_long` | FS | KEEP measuring (fresh B-additions); apply first-touch EVENT pattern from birth. |
| `smc_mitigation_block_short` | FS | Same + P0-3. |
| `smc_fvg_retest_long` | FS | TUNE. FVG-retest fires never while OB fires 100x — inconsistent zone-density between sibling producers; audit gap-size threshold. |
| `smc_fvg_retest_short` | 8 / 0.32 | P0-3. |
| `smc_inverse_fvg` | 81 / 0.88 | MARGINAL. Inverse-FVG (failed gap becomes opposite zone) + vol; n=81 near-breakeven. Watch; deprioritize. |
| `smc_equal_lows_sweep_long` | 41 / 0.78 | TUNE. Sweep-of-equal-lows + FVG: the sweep leg is right (cousin of liquidity_sweep_reversal); the FVG-active gate dilutes it. Require the sweep bar to CLOSE back above the swept level (reclaim confirmation) instead. |
| `smc_equal_highs_sweep_short` | 22 / 0.25 | Same reclaim-confirmation fix + P0-3; currently the OR-arm (smc_bos_bearish) lets it fire without any sweep at all — **gate-logic bug class: OR-arm bypasses the thesis gate.** |

### F10. ICT (10)

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `judas_swing_long` | FS | KEEP. Sweep-down + pivot-proximity + reversal close = daily-translated Judas; starved by near_pivot tolerance — widen. |
| `judas_swing_short` | FS | Same + P0-3. |
| `turtle_soup_long` | 24 / 0.91 | TUNE. Raschke original requires the swept low be a 20-DAY low (major liquidity); ours accepts any sweep + above_prev_low. Add 20d-low qualifier — this is THE defining gate of the setup. |
| `turtle_soup_short` | 20 / 0.24 | Same missing 20d-high qualifier + the OR-arm bypass bug (smc_bos_bearish arm fires without sweep) + P0-3. |
| `mmbm_long` | 124 / 0.84 | RESTRUCTURE. Producer-boolean po3_mmbm_setup at n=124 = way too permissive for a "market-maker buy model" (should be rare accumulation structure). Producer audit + P1-10 threshold surfacing. |
| `mmsm_short` | 247 / 0.57 | Same, worse (n=247 bleeding) + P0-3. |
| `po3_bullish` | 128 / 0.70 | EXPLORATORY already (B722) — data confirms: n=128 PF 0.70. Keep DO-NOT-DEPLOY. |
| `po3_bearish` | 172 / 0.94 | Same. |
| `week_opening_gap_fill_up` | 106 / 1.13 | KEEP. Gap-down fill LONG works (n=106, PF>1) — consistent with gap-fill literature (down-gaps fill more reliably). |
| `week_opening_gap_fill_down` | 122 / 0.44 | CUT-CANDIDATE as specified. Shorting gap-UPS in a bull tape = fading strength repeatedly (n=122, PF 0.44). Industry: up-gaps in uptrends RUN, not fill. Bear-regime-only if kept. |

### F11. VWAP / AVWAP (3)

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `avwap_50_reclaim` | 89 / 0.67 | TUNE. Reclaim of 50d-low-anchored VWAP + MACD + EMA200: n=89 PF 0.67. Reclaim EVENTs need a hold qualifier — require close above AVWAP 2 consecutive days (reclaim-and-hold, not reclaim-bar). |
| `avwap_252_breakout` | 32 / 0.82 | MARGINAL. Yearly-anchor AVWAP break; near-breakeven. The missing anchor that matters: EARNINGS-anchored AVWAP (institutional cost-basis since last report — Brian Shannon's core use). See Part 4 missing-producers. |
| `avwap_20high_rejection_short` | FS | TUNE. 6-gate AND stack (P1-5 worst): rejection + proximity + candle + vol + EMA200 + borrow = starved. 3-gate budget: rejection-proximity + candle + borrow. |

### F12. Volume profile (3)

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `poc_magnet_long` | 14 / 1.54 | KEEP. Above-POC proximity + trend = value-area acceptance logic, works. |
| `naked_poc_retest_long` | 52 / 1.22 | KEEP (vindicates the B1035 un-disablement). Naked-POC magnet is a professional-grade concept; n=52 PF 1.22 solid. |
| `value_area_breakout_long` | FS | TUNE. VA-breakout + vol + trend triple-AND starves; drop vol_above_avg (VA-break IS the volume event). |

### F13. Multi-timeframe (5)

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `htf_aligned_breakout_long` | 29 / 0.96 | KEEP marginal. PDH-break + weekly/monthly alignment; breakeven now, right shape. Add clearance qualifier (above_prev_high_clearance_atr_05 like monthly sibling). |
| `htf_aligned_breakout_short` | 18 / 0.30 | P0-3 treatment. |
| `weekly_bias_pullback_long` | FS | KEEP. Weekly-bull + daily RSI<45 dip is the canonical MTF pullback; starved because weekly_bias_bull producer coverage sparse — producer audit (temporal coverage class, CHECKLIST #156). |
| `weekly_bias_pullback_short` | FS | Same + P0-3. |
| `monthly_bias_momentum_long` | 7 / 0.65 | MARGINAL. Monthly bias + clearance; small n. Keep measuring. |

### F14. Institutional 13F / persistence (20)

The 13F block is the book's deepest bench (P1-7): persistence/conviction variants all cluster PF 1.2-1.6. Two structural notes: (a) 13F data is 45-day-lagged quarterly — all these are STATE signals; the momentum/breakout-triggered variants correctly convert state->timing; the naked-state ones hold longer and mean less. (b) 20 strategies from ONE data source = concentration; the B832 SPOF sentinels matter (Council 236 blocker #3).

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `institutional_buy_momentum_long` | 80 / 1.21 | KEEP. State + MACD timing, n=80 — a workhorse. |
| `institutional_cluster_long` | 93 / 1.04 | KEEP. |
| `institutional_committed_growth_long` | 10 / 1.62 | KEEP — B1230/B1216 coverage fix will raise n. |
| `institutional_high_conviction_long` | 117 / 0.97 | TUNE. new_positions>=3 + EMA50 only — weakest gate in family (new positions without size context). Add position-size floor if producer emits it. |
| `institutional_multi_quarter_persistence_long` | 15 / 1.00 | KEEP measuring. |
| `institutional_persistence_breakout_long` | 19 / 0.90 | KEEP. |
| `institutional_persistence_momentum_long` | 26 / 0.94 | KEEP. |
| `institutional_persistent_holders_long` | 49 / 1.28 | KEEP. |
| `institutional_recent_init_momentum_long` | 25 / 1.36 | KEEP — family's best risk-adjusted (fresh 13F initiations + momentum timing = literature-supported alpha, Chen-Jegadeesh-Wermers class). |
| `institutional_strong_conviction_long` | 47 / 1.29 | KEEP. |
| `institutional_breakout_confirmation_long` | 14 / 0.95 | KEEP. |
| `institutional_oversold_long` | FS | KEEP; starved by RSI<40-on-13F-name coincidence — widen RSI<45 (persistence_oversold sibling uses 45). |
| `institutional_persistence_oversold_long` | FS | KEEP; same widening already at 45; starvation likely persistence-producer coverage (B1216 gap) — re-measure post-fix. |
| `institutional_persistence_volume_long` | FS | Same producer-coverage dependency. |
| `institutional_recent_init_volume_long` | FS | Same. |
| `institutional_volume_confirmation_long` | FS | Same class. |
| `institutional_increased_with_directors_long` | FS | KEEP thesis (13F + insider = two independent smart-money sources); starved by coincidence-of-rare-events — this is a genuinely rare high-value setup, accept low n. |
| `institutional_insider_combo_long` | FS | Same (OR-composite should fire MORE than components — starvation here is suspicious; audit `institutional_buy` producer key). |
| `institutional_with_directors_long` | FS | Same rare-coincidence class. |
| `institutional_with_officers_long` | FS | Same. |

### F15. Insider / SEC events (5)

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `insider_cluster_long` | FS | KEEP + AUDIT. Cluster insider buying is top-3 documented anomalies (Lakonishok-Lee 2001); FS here is a data-coverage red flag, not thesis failure (Council 236 blocker #3 — B832 sentinels tripped during Batch A). Re-measure post news/insider producer fixes. |
| `insider_cluster_with_director_long` | FS | Same. |
| `insider_cluster_concentrated_sell_short` | 16 / 0.77 | KEEP measuring (B1010 design was careful); concentrated-sell is the only defensible insider short. |
| `activist_13d_long` | 16 / 0.61 | TUNE. 13D-filed-within-30d producer-boolean: activist stakes pop on ANNOUNCEMENT day; entering any time in 30d window buys the post-pop drift which is flat (Brav-Jiang). Narrow to <=5d from filing. |
| `m_and_a_target_long` | 110 / 0.89 | RESTRUCTURE. n=110 for M&A-8K-within-30d is too many fires — producer likely matching generic 8-K Item 1.01 (material agreements) not merger agreements (the EV-7 population-mixing lesson repeating). Tighten parse to merger keywords; EXPLORATORY until then. |

### F16. News sentiment (6)

All six were starved pre-B1243 (Council 280: 84.2% coverage, gaps); the Finnhub fallback (98.5% for 2025+) changes their forward prospects but NOT their 2020-2024 backtest visibility (L201). Verdicts are provisional pending re-run.

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `news_momentum_long` | FS | KEEP; 6-gate AND (P1-5) — drop close-position gates, keep sentiment + zscore + DC20 break. |
| `news_momentum_short` | FS | Same, 8 gates! Worst gate-stack in the book. 3-gate budget + P0-3. |
| `news_reversal_long` | FS | KEEP; the -10%-drop + sentiment-shift contrarian shape is good (overreaction literature); 6 gates -> 4. |
| `news_reversal_short` | FS | Same + P0-3. |
| `news_sentiment_long` | 16 / 0.85 | KEEP measuring post-B1243. |
| `news_sentiment_shift_long` | 5 / 0.28 | KEEP measuring; shift>0.3 on >=2 articles is thin evidence for a fire — raise article floor to 3 (matching sibling). |

### F17. PEAD / earnings (5)

PEAD is the most-replicated anomaly in finance (Ball-Brown 1968 onward) — but modern S&P large-caps drift far less (crowding); the small/mid tail is where PEAD lives. Batch B's T3 universe matters more for this family than any other.

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `pead_long` | 9 / 0.73 | KEEP. Canonical positive-surprise drift; expect better on T3. |
| `pead_long_high_yoy_growth_only` | 253 / 0.91 | TUNE. n=253 vs sibling's 9?! The yoy_surprise_high producer fires 28x more than pead_positive_surprise — threshold audit (B709 phi=0.297 finding said DIFFERENT population, but 28x cardinality says the yoy gate is too loose, not just different). |
| `pead_short` | 30 / 0.36 | P0-3 + PEAD-short is the weak leg in literature too (drift asymmetric). Bear-regime + 10d time-stop only. |
| `pead_short_negative_yoy_growth` | 139 / 0.42 | Same + cardinality audit as its long sibling. |
| `pead_with_insider_confirmation_long` | FS | KEEP; rare-coincidence (PEAD window x insider cluster) is genuinely rare — accept. |

### F18. Calendar (6)

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `halloween_seasonal_long` | FS | KEEP. Nov-Apr effect fires 1x/yr/name by design — FS expected; verify producer emits on first day correctly. |
| `january_effect_small_cap_long` | FS | KEEP but note: January small-cap effect has faded post-2000 in literature; cap_band gate limits it to micro/small which barely exist in Batch A (S&P 150) — will only be measurable on T3. |
| `pre_holiday_long` | 6 / 0.70 | KEEP measuring (pre-holiday drift is well-documented, small edge). |
| `totm_long` | 12 / 0.59 | KEEP measuring. Turn-of-month is robust in indices; single-name application dilutes it — consider ETF-only application (SPY/QQQ) per DEC-118 instruments. |
| `pre_fomc_long_sleeve` | 21 / 1.31 | KEEP. Pre-FOMC drift (Lucca-Moench) — n=21 PF 1.31 consistent with literature. |
| `pre_fomc_quality_momentum_long` | FS | KEEP; quality-filtered variant starves (FOMC-day x top-quintile coincidence); fine, rare by design. |

### F19. Index events (4)

All four blocked by the missing `index_rebalance_events.parquet` (Council 236 blocker #1; Sprint 5 DEC-380). No verdict possible until data lands — the effects (add-drift, deletion-reversal) are well-documented but SHRINKING post-2010 (index-arb crowding); set expectations accordingly.

| Strategy | Batch A | Verdict |
|---|---|---|
| `post_inclusion_drift_long` | FS | BLOCKED_UPSTREAM (DEC-380). |
| `post_inclusion_reversal_short` | 9 / 0.46 | Partially fires (uses lifecycle events?); audit which producer feeds it — if it fires while siblings starve, key mismatch likely (CHECKLIST #157). |
| `post_deletion_drift_short` | FS | BLOCKED_UPSTREAM. |
| `pre_rebalance_long` | FS | BLOCKED_UPSTREAM. |

### F20. Cross-asset / macro (4)

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `vix_backwardation_long` | 19 / **2.51** | KEEP — 3rd best entry. VIX term-structure inversion + quality names = buying panic with quality filter. Textbook (term-structure literature). Consider size-up tier in crisis regime. |
| `gold_silver_risk_off_long` | FS | KEEP; defensive-sector rotation on gold signal; starved by sector-membership x signal coincidence on 150 tickers — fine on full universe. |
| `risk_off_bond_equity_short` | 104 / 0.44 | RESTRUCTURE. n=104 PF 0.44 — the bond-signal STATE persists for weeks (STATE-vs-EVENT again) so it shorts equities daily through 2022-2023 rate panic and gets squeezed in every rally. Convert to signal-onset EVENT + 10d time stop. |
| `sector_rotation_defensive_long` | FS | KEEP; same defensive-rotation shape as gold sibling. NOTE: `lead_lag_sector_rotation` orphan in exit_compare (792 trades, medPF 0.90) suggests a predecessor was deleted — verify no roster-lineage loss (L-audit). |

### F21. Factor / cross-sectional (6)

The xs_ block is quietly excellent (P1-7): implemented as monthly-refreshed cross-sectional ranks with proper deciles — closest thing to institutional practice in the book.

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `xs_momentum_top_decile` | 32 / **1.70** | KEEP. J-T momentum + ivol/max screens = the reference implementation. |
| `xs_momentum_bottom_decile_short` | 143 / 0.52 | P0-3. Momentum-short leg loses exactly as AQR documents (short leg of momentum is where crashes live). Bear-regime-only + never in high-vol (momentum crashes happen in vol spikes — Daniel-Moskowitz). |
| `xs_momentum_quality_combined` | 7 / 0.30 | KEEP measuring; n=7 too small to judge a double-screen. |
| `xs_combined_momentum_low_ivol` | FS | KEEP; triple-screen starves on 150 tickers — expected, fine at full universe. |
| `xs_quality_top_quintile_long` | 9 / 1.75 | KEEP (formula says top_tercile while name says quintile — **name-formula mismatch, same class as vol_spike naming; align**). |
| `xs_low_beta_long` | 13 / 1.00 | KEEP. Betting-against-beta; needs the leverage/sizing overlay to shine (BAB is a sizing strategy, not a picking strategy — note for Stage 4). |

### F22. Smart-money sleeves + filters (12)

Sleeve pattern (base AND smart-money) = the book's most reliable win-rate lift (P1-7). All sleeves inherit base starvation; fix bases first.

| Strategy | Batch A | Verdict |
|---|---|---|
| `bollinger_tight_with_smart_money_long` | 16 / 0.96 | KEEP (base is 2.45 — sleeve should exceed; SM gate may be keying on sparse data during Batch A per B832 sentinels; re-measure). |
| `donchian_breakout_with_smart_money_long` | 14 / 0.74 | KEEP measuring post-SM-data-fix. |
| `macd_bullish_with_smart_money_long` | FS | KEEP; base macd_crossover fires n=159 so sleeve FS = SM-data gap evidence (same B832 trail). |
| `mfi_oversold_with_smart_money_long` | FS | KEEP; base also FS. |
| `rsi_oversold_with_smart_money_long` | FS | KEEP; base fires n=30 — same SM-data gap signature. |
| `squeeze_breakout_with_smart_money_long` | 7 / 1.74 | KEEP — works even in sparse-SM conditions. |
| `pead_with_smart_money_long` | 7 / 0.79 | KEEP measuring. |
| `xs_low_beta_with_smart_money_long` | 11 / 1.47 | KEEP. |
| `xs_momentum_with_smart_money_long` | 7 / 1.60 | KEEP — but roster formula shows NO smart-money gate (xs_momentum_top_decile AND ema200 only)! **Name-formula mismatch / possible silent gate loss — AUDIT (CHECKLIST #157).** |
| `52w_high_breakout_with_smart_money_long` | FS | (reviewed F1) |
| `52w_high_breakout_with_smart_money_vol_below_long` | 5 / 1.42 | (reviewed F1) |
| `short_borrow_trap_avoid` | n/a | KEEP as filter (not a strategy — emits avoid). DTC>5 threshold is standard. Post-B1240 shares_outstanding fix, verify si_pct-based variant feasible (dtc-only today). |

### F23. Classification change (11)

All 11 fire-starved. Root cause is shared: `classification_changed_recent` (sector reclassification events) are RARE per name (~1 per name per decade) — 11 strategies dividing one rare event = 10 too many. Industry: sector reclassification drift is a real but tiny anomaly (index-tracking flows).

| Strategy | Verdict |
|---|---|
| `classification_change_recent_long` | KEEP as the family representative. |
| `classification_change_breakout_long`, `classification_change_momentum_long`, `classification_change_oversold_long`, `classification_change_volume_long`, `classification_change_to_tech_long`, `classification_change_with_insider_long`, `classification_change_with_institutional_long` | CONSOLIDATE-CANDIDATE: 8 conditional variants of one rare event can never individually reach n>=30; measure via the representative's trade-log sliced by these conditions post-cube (the B620 squeeze_setup_event_only precedent — answerable from trade log, not separate strategies). |
| `classification_change_from_tech_short`, `classification_change_to_defensive_short` | Same consolidation + P0-3. |

### F24. Pairs (2)

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `pairs_mean_reversion_long` | 277 / 0.99 | RESTRUCTURE. z<-2 entry is right; but PAIRS TRADING REQUIRES THE HEDGE LEG — we trade the long leg naked (n=277, PF 0.99 = the cointegration signal works but unhedged carries full market beta). Also missing z-exit: needs exit at z=0 (the canonical pairs exit; none of our 26 exits knows z). Either implement dollar-neutral pair execution or re-scope as "cointegration-dislocation single-leg" EXPLORATORY. |
| `pairs_mean_reversion_short` | 200 / 0.55 | Same, worse (naked short leg in bull tape). The half_life>=5 gate is backwards for shorts — fast-reverting pairs are the safe shorts. |

### F25. ORB (2)

| Strategy | Batch A | Verdict + recommendation |
|---|---|---|
| `orb_stocks_in_play_long` | 15 / 1.17 | KEEP. Gap>1.5% + vol 2x + trend = daily-bar adaptation of Stocks-in-Play (Zarattini-Aziz); works. |
| `orb_stocks_in_play_short` | 10 / 0.99 | KEEP measuring (best-behaved short in the book at breakeven; gap-down momentum is a real short catalyst — the exception to P0-3 catalyst rule, keep 10d time stop). |

---

## 4. MISSING STRATEGIES — gaps vs industry-standard coverage

Ranked by (evidence strength in literature) x (data already cached) x (fit to existing engine). All are Class 7 NEW candidates requiring owner approval + DEC entries. None require new paid data except where noted.

| # | Missing strategy | Thesis + source | Data status |
|---|---|---|---|
| M1 | **Relative-strength line vs sector ETF** (Mansfield RS / IBD-style) | Buy names making RS-line new highs BEFORE price 52w high — the single most-used institutional momentum refinement; we rank momentum cross-sectionally (xs_) but never vs OWN SECTOR | OHLCV cached (name + sector ETF) — computable today |
| M2 | **Earnings-anchored AVWAP reclaim** (Shannon, "Maximum Trading Gains with Anchored VWAP" 2023) | Institutional cost-basis since last earnings; reclaim = holders in profit = support. Our AVWAP anchors are highs/lows only (F11 gap) | OHLCV + earnings dates cached |
| M3 | **VCP — volatility contraction pattern** (Minervini) | Successive tightening pullbacks into pivot; the modern refinement of cup-handle. We have squeeze (BB-in-KC) but not multi-leg contraction sequencing | OHLCV; needs new producer |
| M4 | **Pocket pivot** (O'Neil/Morales) | Up-day volume > max down-day volume of last 10 sessions inside a base — accumulation tell BEFORE breakout; complements our breakout-day-biased book | OHLCV; trivial producer |
| M5 | **Gap-and-go continuation** (distinct from our gap-FILL strategies) | Up-gap >2% holding above open at close in uptrend = institutional repricing; our gap book only fades (F10 finding: fades lose on up-gaps) | OHLCV cached |
| M6 | **Buyback announcement drift** (restore EV-7 properly) | 8-K/press-release buyback announcements drift positively (Ikenberry); B682 deleted for population-mixing — restore with proper repurchase-plan parse | SEC EDGAR cached; parser work |
| M7 | **Dividend initiation / large increase** | Initiations drift +2-4% over quarters (Michaely et al.) | Polygon dividends endpoint cached |
| M8 | **Insider CEO/CFO-specific cluster weight** | Officer buys outperform director buys ~2x (Cohen-Malloy-Pomorski "decoding inside information") — we count roles equally in most gates | Quiver cached; gate refinement not new data |
| M9 | **Short-interest DECLINE + price strength** (squeeze aftermath long) | SI drop quarter-over-quarter + uptrend = structural buyer exhaustion of bears; complements squeeze_setup_long (which needs HIGH SI) | FINRA cached post-B1240 |
| M10 | **Sector momentum rotation long** (top-2 sector ETFs monthly) | Classic tactical allocation (Faber); we HAD lead_lag_sector_rotation (792 orphan trades!) — restore intentionally on the 27 T1-ETFs | ETF OHLCV cached |
| M11 | **Quality-minus-junk tilt short overlay** (AQR QMJ) | Junk-decile shorts in bear regimes only — gives the SHORT book a factor-grade catalyst | Fundamentals partially cached (OpenBB) |
| M12 | **Overnight-gap earnings straddle proxy** — SKIP (options out of scope Stage 2; note for Phase 1C Unusual Whales) | — | — |
| M13 | **Trend-following on T1-ETFs with vol-targeting** (Carver "Systematic Trading" position-scaled) | Our whole book is entry/exit binary; ETF sleeve with continuous vol-target sizing is the diversifier with the best documented Sharpe | ETF OHLCV cached; needs sizing-overlay engine work (Stage 4 fit) |
| M14 | **Failed-breakout reversal (2B / Sperandeo)** | Break of 20d high that closes back inside range within 2 bars -> fade. We trade breakouts and retests but never the FAILURE — highest-expectancy pattern in choppy regimes; also gives the SHORT book its missing technical catalyst | OHLCV; trivial producer |
| M15 | **Consecutive down-days + quality (buy-the-blood)** | 4-6 consecutive red closes on quality names = canonical institutional dip-buy (RenTec-documented reversal horizon 3-5d) | OHLCV; trivial producer |

**Explicitly NOT missing (verified present):** momentum (xs_), low-beta, quality, PEAD, insider cluster, 13F persistence, index events, seasonality, VIX structure, pairs, SMC/ICT suite, news momentum+reversal, gap fills, 52w-high effect, squeeze setups. The roster's BREADTH is genuinely comprehensive — the gaps are refinement-grade, not category-grade.

---

## 5. PRODUCER + GATE OPTIMIZATION PROGRAM (win rate up / drawdown down / ROI up)

Cross-cutting levers, ordered by expected impact per unit of work. Each is a recommendation requiring owner approval; none change code by this document.

**Lever 1 — Fix the exit-selection score (P0-1).** Nothing else matters until best-exit selection optimizes expectancy. Re-weight composite; re-run cube replay (existing infra, ~hours). Expected effect: ROI-optimal exits replace WR-optimal; drawdown medians improve mechanically because hybrid_50pct's -80% DD cells stop winning.

**Lever 2 — Regime-gate the SHORT book (P0-3).** ~35 standalone SHORTs currently fire all-regimes into 2022-2026 drift. Seeding affinity={bear,crisis} converts the measured -0.1 to -0.6 PF bleed into conditional exposure that only activates when shorts actually work. Expected effect: largest single drawdown reduction available; win rate of the aggregate book rises because the worst fires never happen.

**Lever 3 — STATE->EVENT conversion sweep (5 confirmed offenders).** `smc_breaker_block_*` (n=164/89), `smc_order_block_bounce` (n=100), `risk_off_bond_equity_short` (n=104), `mmsm_short`/`mmbm_long` (n=247/124), `supertrend_macd_short` + `ichimoku_cloud_breakdown` (pair-inconsistency with their EVENT-converted siblings). The B655/B722 conversion pattern is proven; these six re-fires-daily-while-state-true strategies are the book's volume bleeders. Expected effect: trade count drops ~800 on Batch A scale, almost all from negative-expectancy fires.

**Lever 4 — 3-gate budget for the 25 worst gate-stacks (P1-5).** Score-based (k-of-m) conversion for gates beyond thesis+trend+confirmation. Expected effect: 87 fire-starved shrinks toward ~40 (the rest are legitimately-rare setups + producer bugs already ticketed).

**Lever 5 — Producer-tolerance audits where n is anomalous.** Too-loose: morning_star (151), three_white_soldiers (98), mmbm/mmsm, m_and_a_target (110), yoy_surprise (253/139), smc_choch (73). Too-strict: detect_triangle (0, known), cup_handle (0), squeeze_fire (bb_squeeze FS), weekly_bias coverage. Pattern: **when a pattern strategy fires often, distrust the producer before the thesis** — rare patterns firing frequently = loose detector manufacturing noise. Expected effect: win-rate lift concentrated in candle/chart-pattern families.

**Lever 6 — Reclaim/retest integrity gates.** Recurring micro-fix across families: retest entries must verify the LEVEL HELD (close back above/below reclaimed level, 1-2 bar persistence), not proximity-only. Applies to: dc20_break_retest, cup_and_handle_retest, smc_bos_retest, avwap_50_reclaim, smc_equal_lows/highs sweeps, 52wh/52wl retests. Expected effect: converts the "retest strategies underperform their breakout siblings" anomaly (backwards vs literature) into the expected ordering.

**Lever 7 — OR-arm thesis-bypass audit.** `smc_equal_highs_sweep_short` and `turtle_soup_short` fire WITHOUT their defining sweep via `OR smc_bos_bearish` arms; grep the roster for OR-arms that bypass the named thesis of the strategy. Cheap fix, direct win-rate lift on affected names.

**Lever 8 — Name<->formula alignment sweep.** Found this review: `vol_spike_2x_below_ema_50_short` (gate is 1.5x), `xs_quality_top_quintile_long` (gate is tercile), `xs_momentum_with_smart_money_long` (NO SM gate in formula), `macd_ichimoku` (no ichimoku legs visible). Four in one review pass = there are more. Systematic sweep + pin tests per `feedback_doc_count_drift_must_be_test_pinned` spirit.

**Lever 9 — Exit-suite completion (P1-8).** Add SMA5-cross, opposite-band, k*ATR-target+time pairs; re-tune multi_tier (2R first tier) and break_even_at_1r (+0.25R buffer); deprecate the 6 dead 1x-clones post-confirmation. Expected effect: mean-reversion family (currently exit-orphaned) gets its canonical exit; cube design space widens where it's thin.

**Lever 10 — Per-strategy stop-distance from MAE distribution.** `per_strategy_mae_75th_pct_of_winners()` already exists (exit_strategies.py:985) but conditions a dead 1x trail. Reuse it to set INITIAL stop distance per strategy (stop just beyond 75th-pct MAE of winners = statistically-fitted stop). This is the standard quant-desk method (sits behind "optimal f" / Kelly-fraction sizing too). Expected effect: direct drawdown reduction without truncating winners.

---

## 6. PRIORITIZED RECOMMENDATION QUEUE (owner approval gates each)

| P | Item | Batches est. |
|---|---|---|
| P0 | Lever 1 composite re-weight + cube replay re-run | 1-2 |
| P0 | Lever 2 SHORT regime-affinity seeding (~35 strategies, mechanical) | 2-3 (batch-cap) |
| P0 | P0-2 earnings_blackout max-hold companion + scoring exclusion | 1 |
| P1 | Lever 3 STATE->EVENT six offenders | 2 |
| P1 | Lever 7 OR-arm bypass fixes (2 known) + grep sweep | 1 |
| P1 | Lever 8 name-formula alignment (4 known) + sweep | 1-2 |
| P1 | Lever 9 exit additions (3 new) + 2 re-tunes | 2 |
| P2 | Lever 4 3-gate-budget conversions (top-25 stacks) | 3-5 |
| P2 | Lever 5 producer-tolerance audits (6 loose + 4 strict) | 3-4 |
| P2 | Lever 6 retest-integrity gates (8 strategies) | 2 |
| P2 | F23 classification-change consolidation decision | 1 |
| P2 | F24 pairs: hedge-leg decision (implement or EXPLORATORY re-scope) | 1 |
| P3 | Lever 10 MAE-fitted stops | 2 |
| P3 | M1/M2/M4/M5/M14/M15 new strategies (cached-data, trivial producers) | 3-4 |
| P3 | M3/M6-M11/M13 new strategies (producer/parser work) | later sprint |

**What this review does NOT recommend:** wholesale strategy deletion. Per `no_apriori_pruning`, every CUT-CANDIDATE above stays registered and measured; CUT means capital-deprioritized pending cube verdict. The empirical basis here is one 150-ticker batch — Batch B (1,787 tickers) is the verdict-grade sample, and several verdicts above (especially small-n KEEPs and all SHORT-book conclusions) should be re-derived from it before any roster surgery.

---
*Review methodology: every number EXECUTED from exit_compare.csv / roster parse / source read this session (B1248). No sub-agent output used. Literature citations are from model knowledge (UNVERIFIED class) — flag any for source-check before citing externally.*
