<!-- Source: per CHECKLIST #77; auto-built by scripts/build_passed_strategy_exit_list.py from the R5 cube (output_r5_merged_1_7) + STRATEGY_ROSTER.md. Do NOT hand-edit; regenerate. -->

# Passed Strategy -> Exit List (R5, TRUE-HOLDOUT graded)

**Generated:** B1378 | **Cube:** `output_r5_merged_1_7` (614 tickers, 7 batches, 2022-05-05 -> 2026-05-05)

> **This list is graded on a TRUE HOLDOUT (B1378).** The exit is picked using ONLY 2022-05 -> 2025-05 (IS folds 1-3); the final year 2025-05 -> 2026-05 (F4) is a holdout no selection decision ever saw, and the **Verdict column is decided by the holdout alone**. Sharpes are ANNUALIZED, NET of 20bps round-trip cost, winsorized +/-300% (F1+F6, B1377), and carry a Lo(2002) 95% CI. Deep review: `R5_ANALYSIS_DEEP_REVIEW.md`.

## Headline - what goes to the next phase

| | Cells (strategy x direction x exit) | Evidence |
|---|---|---|
| **A. EVIDENCED long** | **22** | holdout Sharpe >= 0.5 + BH-FDR + CI lower bound > 0 |
| **B. Directive mirrors, measured** | **12** | in the cube, and ALL of them FAILED the holdout |
| **C. Directive mirrors, unmeasured** | **3** | never backtested - exit TBD |
| **TOTAL** | **37** | of which 22 carry forward evidence |

**This is NOT strategies x 26.** Each promoted strategy carries exactly ONE exit - chosen on in-sample data, graded on the held-out year - so the cube's 26-exit dimension is already collapsed. 22 evidenced strategies = 22 cells. (A full cube RE-RUN, a measurement exercise rather than a deployment roster, would be 222 x 26 = 5,772 cells.)

### Grading population behind those cells

| Outcome | Rows (strategy x direction) | Strategies |
|---|---|---|
| **PASS** (holdout Sharpe >= 0.5 AND survives BH-FDR q<0.05) | **29** | **29** |
| PASS-noFDR (cleared 0.7 but not multiple-testing-survivable) | 14 | 14 |
| DROP (holdout Sharpe < 0.5 - selected-in-sample, failed live-forward) | 146 | 122 |
| UNEVAL (holdout n<30 - no honest verdict) | 40 | 37 |
| TOTAL graded rows (every strategy x direction in the cube) | 229 | 178 |

**Breadth after de-duplication (B1381):** the 29 promoted strategies contain 7 near-duplicates (Jaccard >= 0.70 on the (ticker, entry_date) trade set, all inside the 13F/smart-money family) -> **22 distinct strategies**. Their daily return streams give an **effective number of bets of 7.2** (vs 4.9 before de-dup): this roster is far less diversified than its count suggests, and position sizing should be set against the effective number, not the headline.

| Kept | Redundant duplicates folded into it |
|---|---|
| `institutional_committed_growth_long` | `institutional_cluster_long`, `institutional_insider_combo_long`, `institutional_multi_quarter_persistence_long`, `institutional_persistent_holders_long`, `institutional_strong_conviction_long`, `rsi_oversold_with_smart_money_long` |
| `institutional_persistence_breakout_long` | `institutional_breakout_confirmation_long` |

**Does the old screen have predictive power?** Holdout hit-rate (Sharpe >= 0.7) is **36.5%** for rows the pre-holdout LOOSE screen selected (74 rows) vs **13.9%** for rows it rejected (115 rows). The screen carries real but modest signal - it roughly doubles the hit rate; it does not identify winners on its own.

Of the 29 PASS rows, **29** also have a 95% CI lower bound above 0 (F2: the rest are point-estimate passes whose CI still straddles 0 at this n).

**How to read a row:** IS F1-F3 are the selection folds (the exit was chosen to maximise their MEAN, not their max - a single lucky year cannot win the pick). HOLDOUT F4 is the verdict fold. `n<30` = below the statistical-power floor, un-evaluable. Cum = full-window Sharpe / trades / win-rate / summed per-trade return% (includes IS; context only, not a gate).

**Method / caveats:**
- Sharpe = ANNUALIZED per-trade x sqrt(252/avg_hold), matching `metrics.py::_sharpe` (B1371 fix).
- NET of 20bps T1a round-trip (config.py DEC-612) + winsorized +/-300% (SBNY delisting collapse).
- **BH-FDR** (Benjamini-Hochberg, q=0.05) across the holdout family; the repo's canonical correction per B982. Selection used IS only, so each row contributes exactly ONE holdout test.
- **Regime-conditional rows (Cond=Y):** exit varies by `regime_at_entry`, assigned once at entry and held to close; the regime->exit map is shown before `||` in the last column.
- Dual strategies appear as TWO rows, each showing **its own leg's** entry gates (F4 fix).


**KNOWN LIMITATIONS (what is still NOT proven):**
1. **[APPLIED B1377] Net-of-cost + winsorized.** REMAINING: shorts exclude borrow cost (short rows are optimistic); the formal cost-sensitivity RATIO gate is not computed.
2. **[APPLIED B1378 - F2] Sharpe CIs** are reported. At n=30-40 the CI half-width is large; prefer rows whose CI lower bound clears 0, and treat point Sharpes above 2 at low n as noise.
3. **[APPLIED B1378 - F3] True holdout + BH-FDR.** REMAINING: the holdout is ONE year (2025-26, a bull-leaning tape) - it is a real out-of-sample test but not a multi-regime one.
4. **[APPLIED B1378 - F4] Per-leg entry gates** now render per direction.
5. **Crisis regime absent** (n<30 in the 2022-26 window) - this system is meant to buy dips in crisis; NO crisis-regime evidence exists in this set.
6. **Not a deploy list.** Exit assignment (`STRATEGY_EXIT_OVERRIDE`) is a strategy change and requires explicit owner approval; paper trading is the next filter, not this table.


## A0. SHORT MIRROR COVERAGE (owner standing directive 2026-07-25)

*"Whichever long strategies go to the next phase, their mirror short symmetrical strategies are by default to be added."* Applied to the 29 promoted LONG strategies:

| Status | Count | Meaning |
|---|---|---|
| REGISTERED-DUAL | 10 | strategy already trades both legs - short ships automatically |
| REGISTERED-STANDALONE | 5 | a symmetric short strategy already exists in the roster |
| MISSING-BUILDABLE | 0 | no mirror registered -> Class 7 NEW_STRATEGY to wire |
| NOT-DEFENSIBLE | 13 | long-only DATA SOURCE (13F/insider/congress/buyback) - B611 precedent |

> **Three warnings the directive should be read against.** (1) *Economic asymmetry*: equities drift up, shorts pay borrow and carry unbounded squeeze risk, so a structurally symmetric short is NOT expected to earn its long's return - it must be sized and judged separately. (2) *No forward evidence*: **zero** short rows clear the holdout in this cube (the window holds ~5 downtrend months in 48), so mirrors ship UNVALIDATED-BY-CONSTRUCTION and should be tagged EXPLORATORY until a bear-inclusive window tests them. (3) *Worse than unvalidated for some*: **12 of the mirrors already exist in this cube and their own holdout evidence is NEGATIVE** (see the 'Mirror's OWN holdout evidence' column) - adding those is a deliberate override of measured evidence on the argument that the window under-samples bear tape, not an absence of data. See L229.

| Promoted LONG | Mirror status | Short mirror | Mirror's OWN holdout evidence | Note |
|---|---|---|---|---|
| `avwap_252_breakout` | **REGISTERED-DUAL** | `avwap_252_breakout (short leg)` | -0.565 (n=154) -> **DROP** | already trades both directions; the short leg ships with it |
| `break_retest_confluence` | **REGISTERED-DUAL** | `break_retest_confluence (short leg)` | -0.24 (n=296) -> **DROP** | already trades both directions; the short leg ships with it |
| `bullish_engulfing_support` | **REGISTERED-DUAL** | `bullish_engulfing_support (short leg)` | -0.038 (n=152) -> **DROP** | already trades both directions; the short leg ships with it |
| `cpr_narrow_bullish` | **REGISTERED-DUAL** | `cpr_narrow_bullish (short leg)` | -0.505 (n=153) -> **DROP** | already trades both directions; the short leg ships with it |
| `force_index_breakout` | **REGISTERED-DUAL** | `force_index_breakout (short leg)` | -0.506 (n=417) -> **DROP** | already trades both directions; the short leg ships with it |
| `institutional_breakout_confirmation_long` | **NOT-DEFENSIBLE** | `-` | - | long-only data source (institutional) - B611 precedent; a mechanical inverse would be economically false |
| `institutional_cluster_long` | **NOT-DEFENSIBLE** | `-` | - | long-only data source (institutional) - B611 precedent; a mechanical inverse would be economically false |
| `institutional_committed_growth_long` | **NOT-DEFENSIBLE** | `-` | - | long-only data source (institutional) - B611 precedent; a mechanical inverse would be economically false |
| `institutional_high_conviction_long` | **NOT-DEFENSIBLE** | `-` | - | long-only data source (institutional) - B611 precedent; a mechanical inverse would be economically false |
| `institutional_insider_combo_long` | **NOT-DEFENSIBLE** | `-` | - | long-only data source (institutional, insider) - B611 precedent; a mechanical inverse would be economically false |
| `institutional_multi_quarter_persistence_long` | **NOT-DEFENSIBLE** | `-` | - | long-only data source (institutional) - B611 precedent; a mechanical inverse would be economically false |
| `institutional_persistence_breakout_long` | **NOT-DEFENSIBLE** | `-` | - | long-only data source (institutional) - B611 precedent; a mechanical inverse would be economically false |
| `institutional_persistence_oversold_long` | **NOT-DEFENSIBLE** | `-` | - | long-only data source (institutional) - B611 precedent; a mechanical inverse would be economically false |
| `institutional_persistent_holders_long` | **NOT-DEFENSIBLE** | `-` | - | long-only data source (institutional) - B611 precedent; a mechanical inverse would be economically false |
| `institutional_strong_conviction_long` | **NOT-DEFENSIBLE** | `-` | - | long-only data source (institutional) - B611 precedent; a mechanical inverse would be economically false |
| `macd_fast_crossover` | **REGISTERED-DUAL** | `macd_fast_crossover (short leg)` | -0.201 (n=589) -> **DROP** | already trades both directions; the short leg ships with it |
| `mfi_oversold_with_smart_money_long` | **NOT-DEFENSIBLE** | `-` | - | long-only data source (smart_money) - B611 precedent; a mechanical inverse would be economically false |
| `news_sentiment_long` | **REGISTERED-STANDALONE** | `news_sentiment_short` | - | symmetric short already registered |
| `pead_long_high_yoy_growth_only` | **REGISTERED-STANDALONE** | `pead_short_negative_yoy_growth` | -0.847 (n=496) -> **DROP** | symmetric short already registered (curated pair - no name transform finds it) |
| `poc_magnet_long` | **REGISTERED-STANDALONE** | `poc_magnet_short` | - | symmetric short already registered |
| `r1_break_retest` | **REGISTERED-DUAL** | `r1_break_retest (short leg)` | -0.266 (n=398) -> **DROP** | already trades both directions; the short leg ships with it |
| `rsi_oversold` | **REGISTERED-DUAL** | `rsi_oversold (short leg)` | 0.079 (n=169) -> **DROP** | already trades both directions; the short leg ships with it |
| `rsi_oversold_with_smart_money_long` | **NOT-DEFENSIBLE** | `-` | - | long-only data source (smart_money) - B611 precedent; a mechanical inverse would be economically false |
| `rsi_volume_200ema` | **REGISTERED-DUAL** | `rsi_volume_200ema (short leg)` | -0.149 (n=74) -> **DROP** | already trades both directions; the short leg ships with it |
| `smc_breaker_block_long` | **REGISTERED-STANDALONE** | `smc_breaker_block_short` | -0.7 (n=427) -> **DROP** | symmetric short already registered |
| `smc_inverse_fvg` | **REGISTERED-DUAL** | `smc_inverse_fvg (short leg)` | -0.234 (n=139) -> **DROP** | already trades both directions; the short leg ships with it |
| `totm_long` | **NOT-DEFENSIBLE-ANOMALY** | `-` | - | one-directional calendar/seasonal anomaly - the inverse of 'returns cluster positively' is 'no effect', not 'returns cluster negatively'; no short thesis |
| `xs_combined_momentum_low_ivol` | **REGISTERED-STANDALONE** | `xs_combined_momentum_high_ivol_short` | - | symmetric short already registered (curated pair - no name transform finds it) |
| `xs_momentum_with_smart_money_long` | **NOT-DEFENSIBLE** | `-` | - | long-only data source (smart_money) - B611 precedent; a mechanical inverse would be economically false |

## A. EVIDENCED - 22 long cells (the only cells with forward evidence)

Holdout Sharpe >= 0.5, survives BH-FDR q<0.05, and 95% CI lower bound above 0. One exit per strategy, picked on IS (2022-05 -> 2025-05) and graded on the untouched 2025-05 -> 2026-05 holdout.

| Strategy | Dir | Best Exit (IS-picked) | Cond | IS F1 | IS F2 | IS F3 | HOLDOUT F4 | 95% CI lo | WR/payoff | R:R ok | >=0.7 | BH q<0.05 | Verdict | Cum Sharpe/n/WR/ret% | Entry gate (this leg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `avwap_252_breakout` | long | `breakeven_plus_trail` | N | 0.272(514) | 0.563(245) | 0.677(450) | **0.532**(314) | 0.246 | 0.363/3.6 | no | no | YES | PASS | 0.475/1523/0.394/9410.4% | LONG: ( reclaim_252_long AND vol_ok ) |
| `break_retest_confluence` | long | `breakeven_plus_trail` | N | -0.05(225) | 0.608(147) | 0.237(103) | **0.52**(143) | 0.134 | 0.315/5.09 | no | no | YES | PASS | 0.338/618/0.257/1222.0% | LONG: (resistance_break_retest AND macd_12_26_9_bullish AND price_above_ema_20 AND price_above_ema_50 AND close_above_open AND close_in_top_40pct_of_range AND vol_below_avg) |
| `bullish_engulfing_support` | long | `breakeven_plus_trail` | N | -0.106(139) | 0.694(83) | 0.671(104) | **0.725**(83) | 0.167 | 0.301/7.22 | no | YES | YES | PASS | 0.535/409/0.301/1228.6% | LONG: (bullish_candle AND (near_s1 OR near_s2 OR at_key_fib) AND obv_bullish) |
| `cpr_narrow_bullish` | long | `breakeven_plus_trail` | N | 0.116(162) | 0.664(108) | 0.41(119) | **0.568**(114) | 0.157 | 0.377/4.51 | no | no | YES | PASS | 0.408/503/0.29/1735.4% | LONG: ( cpr_narrow_tight AND above_cpr AND (above_avwap_50low) AND (price_above_ema_200) ) |
| `force_index_breakout` | long | `breakeven_plus_trail` | N | 0.135(464) | 0.496(190) | 0.604(298) | **0.519**(259) | 0.181 | 0.309/5.42 | no | no | YES | PASS | 0.44/1211/0.302/3553.2% | LONG: (force_index_cross_up AND price_above_ema_20 AND close_above_open) |
| `institutional_committed_growth_long` | long | `breakeven_plus_trail` | N | -0.248(300) | 0.538(342) | 0.51(633) | **0.638**(666) | 0.437 | 0.383/4.54 | no | no | YES | PASS | 0.484/1941/0.308/6019.3% | ( n_grow>=3 AND price_above_ema_200 ) |
| `institutional_high_conviction_long` | long | `breakeven_plus_trail` | N | -0.258(498) | 0.561(556) | 0.441(681) | **0.561**(738) | 0.377 | 0.328/5.44 | no | no | YES | PASS | 0.429/2473/0.3/6569.1% | ( institutional_new_positions>=3 AND price_above_ema_50 ) |
| `institutional_persistence_breakout_long` | long | `breakeven_plus_trail` | N | -0.686(130) | 0.649(145) | 0.354(121) | **0.683**(136) | 0.317 | 0.404/6.0 | no | no | YES | PASS | 0.475/532/0.303/1756.0% | ( institutional_increased>=3 AND resistance_break_retest AND price_above_ema_200 ) |
| `institutional_persistence_oversold_long` | long | `breakeven_plus_trail` | N | -0.067(103) | 0.389(121) | 0.459(293) | **0.517**(199) | 0.14 | 0.357/3.49 | no | no | YES | PASS | 0.412/716/0.3/1561.1% | ( institutional_increased>=3 AND rsi_14<45 AND price_above_ema_200 ) |
| `macd_fast_crossover` | long | `breakeven_plus_trail` | N | 0.353(718) | 0.438(318) | 0.617(498) | **0.537**(378) | 0.264 | 0.333/4.8 | no | no | YES | PASS | 0.451/1912/0.335/7005.3% | LONG: macd_8_21_5_crossover_up |
| `mfi_oversold_with_smart_money_long` | long | `breakeven_plus_trail` | N | 0.448(56) | 0.403(46) | 0.492(69) | **0.839**(71) | 0.113 | 0.366/4.45 | no | YES | YES | PASS | 0.54/242/0.314/636.5% | base_fires AND _has_smart_money_buy(s) |
| `news_sentiment_long` | long | `breakeven_plus_trail` | N | 0.112(343) | 0.555(226) | 0.501(164) | **0.635**(173) | 0.214 | 0.353/4.97 | no | no | YES | PASS | 0.405/906/0.296/2625.4% | ( news_sentiment_mean>0.3 AND news_article_count>=3 AND price_above_ema_200 ) |
| `pead_long_high_yoy_growth_only` | long | `breakeven_plus_trail` | N | 0.29(811) | 0.648(460) | 0.659(423) | **0.585**(422) | 0.361 | 0.308/7.05 | no | no | YES | PASS | 0.539/2116/0.325/8149.5% | ( within_pead_window AND yoy_surprise_high ) |
| `poc_magnet_long` | long | `time_stop_10d` | N | 0.28(164) | 0.702(120) | 0.654(154) | **0.808**(151) | 0.134 | 0.603/1.14 | no | YES | YES | PASS | 0.599/589/0.577/550.4% | ( vp_close_near_poc_pct<0.03 AND vp_close_above_poc AND price_above_ema_200 ) |
| `r1_break_retest` | long | `breakeven_plus_trail` | N | 0.29(702) | 0.421(256) | 0.583(431) | **0.501**(338) | 0.222 | 0.299/4.95 | no | no | YES | PASS | 0.428/1727/0.324/6173.8% | LONG: (r1_break_retest_long AND above_r1 AND macd_12_26_9_bullish AND close_above_open AND close_in_top_40pct_of_range AND vol_below_avg AND above_avwap_20low) |
| `rsi_oversold` | long | `breakeven_plus_trail` | N | -0.867(173) | 0.561(298) | 0.246(222) | **0.596**(293) | 0.327 | 0.321/5.92 | no | no | YES | PASS | 0.405/986/0.241/2173.2% | LONG: ( (rsi_2<7 OR rsi_14<40) AND price_above_sma_50 AND above_200 ) |
| `rsi_volume_200ema` | long | `earnings_blackout` | N | 0.842(37) | 0.278(36) | 0.58(97) | **0.545**(63) | 0.062 | 0.635/1.4 | no | no | YES | PASS | 0.54/233/0.618/1146.6% | LONG: (rsi_14<40 AND vol_above_avg AND price_above_ema_200) |
| `smc_breaker_block_long` | long | `breakeven_plus_trail` | N | 0.188(112) | 0.471(135) | 0.434(345) | **0.693**(356) | 0.408 | 0.393/4.77 | no | no | YES | PASS | 0.497/948/0.325/2999.3% | ( smc_breaker_block_bullish AND price_above_ema_200 ) |
| `smc_inverse_fvg` | long | `regime_flip` | N | -0.108(101) | 0.996(61) | 1.046(141) | **0.813**(92) | 0.193 | 0.587/2.01 | YES | YES | YES | PASS | 0.693/395/0.559/1136.7% | LONG: (smc_inverse_fvg_bullish) AND (price_above_ema_200) AND (vol_spike_2x OR force_index_cross_up) |
| `totm_long` | long | `breakeven_plus_trail` | N | 0.214(91) | 0.474(95) | 0.614(71) | **0.963**(86) | 0.291 | 0.314/10.27 | no | YES | YES | PASS | 0.547/343/0.271/1527.0% | is_totm_window_first_day AND price_above_ema_200 |
| `xs_combined_momentum_low_ivol` | long | `breakeven_plus_trail` | N | -0.725(65) | n<30 | 0.601(87) | **0.962**(35) | 0.188 | 0.371/9.73 | no | YES | YES | PASS | 0.531/211/0.251/853.5% | ( xs_momentum_top_quintile AND xs_ivol_decile<=4 AND price_above_ema_200 ) |
| `xs_momentum_with_smart_money_long` | long | `breakeven_plus_trail` | N | 0.409(176) | 0.701(94) | 0.697(226) | **0.952**(162) | 0.503 | 0.457/5.04 | no | YES | YES | PASS | 0.687/658/0.394/3737.7% | ( xs_momentum_top_decile AND price_above_ema_200 ) |

## B. DIRECTIVE MIRRORS with measured evidence - 12 cells

Short mirrors of the promoted longs that ALREADY EXIST in the cube. They ship under the owner's mirror-by-default directive, **not** on evidence: every one of them FAILED the holdout. Carrying them is a deliberate override, justified by the window holding only ~5 downtrend months in 48 (L229). Size them separately from Section A.

| Parent LONG | Short mirror | Mirror's exit | Mirror's OWN holdout Sharpe | Verdict |
|---|---|---|---|---|
| `pead_long_high_yoy_growth_only` | `pead_short_negative_yoy_growth` | `class_time_stop` | -0.847 (n=496) | **DROP** |
| `smc_breaker_block_long` | `smc_breaker_block_short` | `atr_trail_2x` | -0.7 (n=427) | **DROP** |
| `avwap_252_breakout` | `avwap_252_breakout (short leg)` | `hybrid_50pct_target` | -0.565 (n=154) | **DROP** |
| `force_index_breakout` | `force_index_breakout (short leg)` | `hybrid_50pct_target` | -0.506 (n=417) | **DROP** |
| `cpr_narrow_bullish` | `cpr_narrow_bullish (short leg)` | `breakeven_plus_trail` | -0.505 (n=153) | **DROP** |
| `r1_break_retest` | `r1_break_retest (short leg)` | `breakeven_plus_trail` | -0.266 (n=398) | **DROP** |
| `break_retest_confluence` | `break_retest_confluence (short leg)` | `breakeven_plus_trail` | -0.24 (n=296) | **DROP** |
| `smc_inverse_fvg` | `smc_inverse_fvg (short leg)` | `breakeven_plus_trail` | -0.234 (n=139) | **DROP** |
| `macd_fast_crossover` | `macd_fast_crossover (short leg)` | `breakeven_plus_trail` | -0.201 (n=589) | **DROP** |
| `rsi_volume_200ema` | `rsi_volume_200ema (short leg)` | `earnings_blackout` | -0.149 (n=74) | **DROP** |
| `bullish_engulfing_support` | `bullish_engulfing_support (short leg)` | `breakeven_plus_trail` | -0.038 (n=152) | **DROP** |
| `rsi_oversold` | `rsi_oversold (short leg)` | `breakeven_plus_trail` | 0.079 (n=169) | **DROP** |

## C. DIRECTIVE MIRRORS without any data - 3 cells (exit TBD)

Wired in B1382 under the same directive. They have never been backtested, so **no exit can be assigned from measurement**. Open owner decision: inherit the long parent's exit as a default, or hold exit-TBD until a bear-inclusive window runs. All are tagged EXPLORATORY and excluded from the multiple-testing family.

| Parent LONG | Short mirror | Exit | Evidence |
|---|---|---|---|
| `news_sentiment_long` | `news_sentiment_short` | *TBD - never backtested* | none |
| `poc_magnet_long` | `poc_magnet_short` | *TBD - never backtested* | none |
| `xs_combined_momentum_low_ivol` | `xs_combined_momentum_high_ivol_short` | *TBD - never backtested* | none |

## Appendix - entry-gate formulas for the 22 evidenced cells (exact per-leg `fires` expression)

- **`avwap_252_breakout`** [long, vwap]: `fl = ( reclaim_252_long and vol_ok # B1139 dropped: rsi_14 < 70 (Shannon canonical doesn't require) )`
- **`break_retest_confluence`** [long, confluence]: `fl = (s.get("resistance_break_retest") and s.get("macd_12_26_9_bullish") and s.get("price_above_ema_20") and s.get("price_above_ema_50") and s.get("close_above_open") and s.get("close_in_top_40pct_of_range")  # B728 strong-close and s.get("vol_bel...`
- **`bullish_engulfing_support`** [long, candle]: `fl = (bullish_candle and (s.get("near_s1") or s.get("near_s2") or s.get("at_key_fib")) and s.get("obv_bullish"))`
- **`cpr_narrow_bullish`** [long, pivot]: `fl = ( s.get("cpr_narrow_tight") and s.get("above_cpr") and avwap_long_ok and above_200 )`
- **`force_index_breakout`** [long, breakout]: `fl = (s.get("force_index_cross_up") and s.get("price_above_ema_20") and s.get("close_above_open"))`
- **`institutional_committed_growth_long`** [long, institutional_persistence]: `fires = ( committed_growth_ok and s.get("price_above_ema_200", False) )`
- **`institutional_high_conviction_long`** [long, smart_money_13f]: `fires = ( s.get("institutional_new_positions", 0) >= 3 and s.get("price_above_ema_50", False) )`
- **`institutional_persistence_breakout_long`** [long, institutional_persistence]: `fires = ( s.get("institutional_increased", 0) >= 3  # B1163: was >= 5 and s.get("resistance_break_retest", False) and s.get("price_above_ema_200", False) )`
- **`institutional_persistence_oversold_long`** [long, institutional_persistence]: `fires = ( s.get("institutional_increased", 0) >= 3  # B1160: was >= 5 and s.get("rsi_14", 50) < 45  # B1160: was < 40 and s.get("price_above_ema_200", False) )`
- **`macd_fast_crossover`** [long, momentum]: `(predicate not extracted - read source)`
- **`mfi_oversold_with_smart_money_long`** [long, smart_money_sleeve]: `(predicate not extracted - read source)`
- **`news_sentiment_long`** [long, news_sentiment]: `fires = ( s.get("news_sentiment_mean", 0.0) > 0.3  # B1136: was > 0.5 (Lopez-Lira-Tang 2023) and s.get("news_article_count", 0) >= 3 and s.get("price_above_ema_200", False) )`
- **`pead_long_high_yoy_growth_only`** [long, event_driven]: `fires = ( s.get("within_pead_window", False) and s.get("yoy_surprise_high", False) )`
- **`poc_magnet_long`** [long, volume_profile]: `fires = ( s.get("vp_close_near_poc_pct", 1.0) < 0.03  # B1201: 0.02 -> 0.03 spirit-match and s.get("vp_close_above_poc", False) and s.get("price_above_ema_200", False) )`
- **`r1_break_retest`** [long, pivot]: `fl = (s.get("r1_break_retest_long") and s.get("above_r1") and s.get("macd_12_26_9_bullish") and s.get("close_above_open") and s.get("close_in_top_40pct_of_range") and s.get("vol_below_avg") and s.get("above_avwap_20low"))`
- **`rsi_oversold`** [long, mean_reversion]: `fl = ( (rsi_2 < 7 or rsi_14 < 40)  # B1147: was (rsi_2<5 or rsi_14<35) and s.get("price_above_sma_50") and above_200 )`
- **`rsi_volume_200ema`** [long, confluence]: `fl = (s.get("rsi_14", 50) < 40 and s.get("vol_above_avg") and s.get("price_above_ema_200"))`
- **`smc_breaker_block_long`** [long, smc]: `fires = ( s.get("smc_breaker_block_bullish", False) and s.get("price_above_ema_200", False) )`
- **`smc_inverse_fvg`** [long, smc]: `(predicate not extracted - read source)`
- **`totm_long`** [long, calendar]: `(predicate not extracted - read source)`
- **`xs_combined_momentum_low_ivol`** [long, factor]: `fires = ( s.get("xs_momentum_top_quintile", False)  # B1193: was top_decile and s.get("xs_ivol_decile", 5) <= 4   # B1193: was <=3; bottom 40% IVOL and s.get("price_above_ema_200", False) )`
- **`xs_momentum_with_smart_money_long`** [long, smart_money_sleeve]: `fires = ( s.get("xs_momentum_top_decile", False) and s.get("price_above_ema_200", False) )`

---
*The DROP (146), UNEVAL (40) and PASS-noFDR (14) populations were removed from this document per owner directive 2026-07-26 so it reads as the deployment list. They remain in full, with all metrics, in `output_r5_merged_1_7/passed_strategy_exit_holdout_graded.json` - regenerate this file with `python scripts/build_passed_strategy_exit_list.py`.*