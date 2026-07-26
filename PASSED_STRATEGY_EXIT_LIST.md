<!-- Source: per CHECKLIST #77; auto-built by scripts/build_passed_strategy_exit_list.py from the R5 cube (output_r5_merged_1_7) + STRATEGY_ROSTER.md. Do NOT hand-edit; regenerate. -->

# Passed Strategy -> Exit List (R5, TRUE-HOLDOUT graded)

**Generated:** B1378 | **Cube:** `output_r5_merged_1_7` (614 tickers, 7 batches, 2022-05-05 -> 2026-05-05)

> **This list is graded on a TRUE HOLDOUT (B1378).** The exit is picked using ONLY 2022-05 -> 2025-05 (IS folds 1-3); the final year 2025-05 -> 2026-05 (F4) is a holdout no selection decision ever saw, and the **Verdict column is decided by the holdout alone**. Sharpes are ANNUALIZED, NET of 20bps round-trip cost, winsorized +/-300% (F1+F6, B1377), and carry a Lo(2002) 95% CI. Deep review: `R5_ANALYSIS_DEEP_REVIEW.md`.

## The funnel - every filter applied, and what each one removed

| # | Stage | Criterion applied | Rows remaining |
|---|---|---|---|
| 0 | Every (strategy x direction) in the cube | - | 229 |
| 1 | Holdout-evaluable | holdout n >= 30 (else UNEVAL) | 189 |
| 2 | Cleared the Sharpe bar | holdout annualized Sharpe >= 0.5 | 43 |
| 3 | Survived multiple testing | BH-FDR q < 0.05 across the holdout family | 29 |
| 4 | Statistically non-zero | Lo(2002) 95% CI lower bound > 0 | 29 |
| 5 | De-duplicated | Jaccard < 0.70 on the trade set (drops near-identical) | 22 |
| 6 | Full canonical criteria | + Sortino, Calmar, PSR, profit factor, min_trades | **3** |

**Read stages 5 and 6 together.** Stage 5 (22) is what this document lists and what goes to the next phase. Stage 6 (3) is how many of those also clear the project's canonical `PASSING_CRITERIA` - see the canonical table below. The gap between them is not a contradiction: stage 5 is a screening bar, stage 6 is the deployment bar.

**On R:R:** win rate and payoff are REPORTED per cell (columns `WR`, `Payoff`, `R:R ok`) but are NOT part of the funnel. `R:R ok` means WR >= 0.5 AND payoff >= 1.5. Only 1 of the 22 satisfies it, so ANDing it in would have deleted 21 of 22 - because the exit that wins selection (`breakeven_plus_trail`) manufactures low-WR / high-payoff by design. Per owner ruling 2026-07-26, Sharpe governs and win rate is a diagnostic; `config.PASSING_CRITERIA["win_rate_gate"]` is now `False` (B1387).

## Verdict criteria - what PASS / DROP / UNEVAL actually mean here

Evaluated on the HOLDOUT fold only (2025-05-05 -> 2026-05-05), on NET winsorized per-trade returns. Sharpe is ANNUALIZED (per-trade x sqrt(252/avg_hold), matching `metrics.py::_sharpe`).

| Verdict | Condition | Meaning |
|---|---|---|
| **UNEVAL** | holdout n < 30 | **untestable, NOT refuted** - below the statistical-power floor. Never read as a failure. |
| **PASS** | n >= 30 AND annualized Sharpe >= 0.5 AND survives BH-FDR q<0.05 | cleared the bar and is distinguishable from multiple-testing luck |
| **PASS-noFDR** | n >= 30 AND Sharpe >= 0.5, FDR not survived | cleared the bar but indistinguishable from luck across the family - watchlist, not deploy |
| **DROP** / **FAIL** | n >= 30 AND Sharpe < 0.5 | tested and refuted (`FAIL` is the same rule in the native-regime gate) |

Reported ALONGSIDE the verdict but **not** gating it: 95% CI lower bound (Lo 2002), a STRICT flag for Sharpe >= 0.7, and the R:R diagnostic (win rate >= 0.5 AND payoff >= 1.5). R:R is deliberately NOT ANDed onto the gate - only 1 of the promoted strategies satisfies it, because the winning exit (`breakeven_plus_trail`) manufactures low-win-rate / high-payoff by design (L231).

**This screen is narrower than the project's canonical `PASSING_CRITERIA`.**

- The gate above checks **three** things: an n-floor, a Sharpe bar (0.5), and a multiple-testing correction.
- `backtest/config.py` carries **14 criteria + 3 AUTO-FAIL screens**.
- `min_sharpe_per_regime` was reconciled to 0.5 (B1387, owner-approved). `min_sharpe_overall` remains 1.0 - out of scope of that approval.
- Win rate is now a DIAGNOSTIC, not a gate (`win_rate_gate = False`, B1387).
- Applying the full canonical set collapses the promoted list from 22 to 3 - table below.

**FULL canonical criteria, measured on the holdout for the promoted cells** (B1387, `scripts/canonical_criteria_check.py`, reusing the `metrics.py` implementations rather than reimplementing them):

| Canonical criterion | Threshold | Promoted cells clearing it |
|---|---|---|
| `min_sharpe_per_regime` | 0.5 | 22 / 22 |
| `min_profit_factor_overall` | 1.3 | 22 / 22 |
| `min_sortino_per_regime` | 0.7 | 22 / 22 |
| `min_psr` | 0.95 | 14 / 22 |
| `min_trades` (overall) | 100 | 16 / 22 |
| `min_calmar` | 0.5 | 8 / 22 |
| **ALL SIX simultaneously** | | **3 / 22** |
| ~~`max_drawdown`~~ | ~~-25%~~ | **MIS-APPLIED to a cube cell - excluded** |
| ~~`min_deflated_sharpe`~~ | ~~0.95~~ | **UNREACHABLE BY CONSTRUCTION - excluded** |

**The 3 clearing every well-specified canonical gate:** `xs_momentum_with_smart_money_long` (Sharpe 0.95, n=162), `smc_breaker_block_long` (0.69, n=356), `institutional_persistence_breakout_long` (0.68, n=136). A 4th, `smc_inverse_fvg`, clears everything except `min_trades`=100. Binding constraints among the valid gates: `min_calmar` (8/22) and `min_psr` (14/22).

> **Two canonical gates are excluded because they are mis-specified for a cube CELL - not because they were inconvenient.** Both are ticketed, not silently dropped.
>
> - **`max_drawdown` >= -25% is a PORTFOLIO criterion.** `metrics.py::_max_drawdown` compounds `(1+pnl/100).cumprod()` - one position reinvested serially. But this cube is ISOLATION-based: every signal opens its own fixed-notional $10,000 trade, trades overlap in time, nothing compounds, and no unified equity curve exists. The artifact is visible in the data: **corr(trade count, max drawdown) = -0.63**, so a cell scores worse purely for having MORE trades. Ticket `S6-B1387-MDD-PORTFOLIO-VS-CELL`.
> - **`min_deflated_sharpe` >= 0.95 is unreachable by construction.** The implementation returns `deflated = sharpe * sqrt(1 - (excess_kurt/4)*sharpe^2)`; that radicand is <= 1, so **DSR <= Sharpe always** (verified: 0 of 22 cells have DSR > Sharpe). Requiring DSR >= 0.95 therefore requires Sharpe >= 0.95, contradicting the owner-approved 0.5 bar. The 0.95 threshold reads as though written for a PROBABILITY (as `min_psr` is) while this implementation returns a scaled Sharpe; 17 of 22 also return None on high kurtosis. Ticket `S6-B1387-DSR-THRESHOLD-SEMANTICS`.
>
> Still not GATED for the promoted set: cost-sensitivity ratio, Chow break-point, ADF (the 3 AUTO-FAIL screens). `canonical_criteria_check.py` emits their raw values into `output_audit/b1387_canonical_criteria.json`.

## Timeframes (DEC-505 walk-forward)

| Window | Dates | Trading days | Role |
|---|---|---|---|
| Warm-up | 2021-05-05 -> 2022-05-05 | ~250 | indicator burn-in; no trades graded |
| **IS fold F1** | 2022-05-05 -> 2023-05-05 | ~251 | selection (reported per-fold as a consistency diagnostic) |
| **IS fold F2** | 2023-05-05 -> 2024-05-05 | ~250 | selection |
| **IS fold F3** | 2024-05-05 -> 2025-05-05 | ~250 | selection |
| **IS pooled** | 2022-05-05 -> 2025-05-05 | 751 | **the exit is picked here** (pooled 3y Sharpe, L230) |
| **HOLDOUT F4** | 2025-05-05 -> 2026-05-05 | 251 | **the verdict** - never seen by any selection step |
| Full cube window | 2022-05-05 -> 2026-05-05 | 1,002 | 4 years, 614 tickers |

**Regime composition of those windows** (market-wide daily label; the regime changed 25 times in 1,002 trading days, ~once per 40 - L232):

| Window | bull | bear | neutral | crisis |
|---|---|---|---|---|
| IS pooled (751 days) | 481 (64%) | 259 (34%) | 11 (1%) | 0 |
| **HOLDOUT (251 days)** | **221 (88%)** | **12 (5%)** | 18 (7%) | 0 |
| Full window (1,002 days) | 702 (70%) | 271 (27%) | 29 (3%) | **0 (0%)** |

> **Read the holdout composition before reading any SHORT result.** The holdout year is 88% bull and holds just 12 bear days, so a pooled holdout grades a short strategy almost entirely on the tape it is built to lose in. That is a property of the WINDOW, not of the strategies. See the native-regime gate below and `scripts/regime_conditional_gate.py`. Note also that **no crisis day exists anywhere in the cube** - this system is designed to buy dips in crisis and has zero crisis evidence.

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

**Three warnings this directive should be read against:**

1. **Economic asymmetry.** Equities drift up; shorts pay borrow and carry unbounded squeeze risk. A structurally symmetric short is not expected to earn its long's return - size and judge it separately.
2. **No forward evidence.** Zero short rows clear the holdout (the window holds ~5 downtrend months in 48). Mirrors ship unvalidated-by-construction; all are tagged EXPLORATORY.
3. **Worse than unvalidated for 12 of them.** Those mirrors already exist in this cube and their own holdout evidence is NEGATIVE (see section B). Adding them overrides measured evidence - defensible only because the window under-samples bear tape (L229).

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

| Strategy | Exit | Verdict | Holdout Sharpe (n) | 95% CI lo | WR | Payoff | R:R ok | >=0.7 | Cond | Regimes with holdout evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| `avwap_252_breakout` | `breakeven_plus_trail` | **PASS** | 0.532 (314) | 0.246 | 0.363 | 3.6 | no | no | N | **bull 0.474**(n=254); bear n=26<30; **neutral 0.77**(n=34) |
| `break_retest_confluence` | `breakeven_plus_trail` | **PASS** | 0.52 (143) | 0.134 | 0.315 | 5.09 | no | no | N | **bull 0.523**(n=131); bear n=3<30; neutral n=9<30 |
| `bullish_engulfing_support` | `breakeven_plus_trail` | **PASS** | 0.725 (83) | 0.167 | 0.301 | 7.22 | no | YES | N | **bull 0.716**(n=67); bear n=6<30; neutral n=10<30 |
| `cpr_narrow_bullish` | `breakeven_plus_trail` | **PASS** | 0.568 (114) | 0.157 | 0.377 | 4.51 | no | no | N | **bull 0.485**(n=88); bear n=9<30; neutral n=17<30 |
| `force_index_breakout` | `breakeven_plus_trail` | **PASS** | 0.519 (259) | 0.181 | 0.309 | 5.42 | no | no | N | **bull 0.265**(n=191); **bear 1.468**(n=32); **neutral 0.497**(n=36) |
| `institutional_committed_growth_long` | `breakeven_plus_trail` | **PASS** | 0.638 (666) | 0.437 | 0.383 | 4.54 | no | no | N | **bull 0.514**(n=540); **bear 1.535**(n=60); **neutral 0.573**(n=66) |
| `institutional_high_conviction_long` | `breakeven_plus_trail` | **PASS** | 0.561 (738) | 0.377 | 0.328 | 5.44 | no | no | N | **bull 0.516**(n=618); **bear 1.389**(n=34); **neutral 0.352**(n=86) |
| `institutional_persistence_breakout_long` | `breakeven_plus_trail` | **PASS** | 0.683 (136) | 0.317 | 0.404 | 6.0 | no | no | N | **bull 0.58**(n=110); bear n=8<30; neutral n=18<30 |
| `institutional_persistence_oversold_long` | `breakeven_plus_trail` | **PASS** | 0.517 (199) | 0.14 | 0.357 | 3.49 | no | no | N | **bull 0.358**(n=160); bear n=26<30; neutral n=13<30 |
| `macd_fast_crossover` | `breakeven_plus_trail` | **PASS** | 0.537 (378) | 0.264 | 0.333 | 4.8 | no | no | N | **bull 0.415**(n=284); **bear 0.983**(n=59); **neutral 0.728**(n=35) |
| `mfi_oversold_with_smart_money_long` | `breakeven_plus_trail` | **PASS** | 0.839 (71) | 0.113 | 0.366 | 4.45 | no | YES | N | **bull 0.676**(n=53); bear n=11<30; neutral n=7<30 |
| `news_sentiment_long` | `breakeven_plus_trail` | **PASS** | 0.635 (173) | 0.214 | 0.353 | 4.97 | no | no | N | **bull 0.42**(n=140); bear n=19<30; neutral n=14<30 |
| `pead_long_high_yoy_growth_only` | `breakeven_plus_trail` | **PASS** | 0.585 (422) | 0.361 | 0.308 | 7.05 | no | no | N | **bull 0.557**(n=354); bear n=26<30; **neutral 0.4**(n=42) |
| `poc_magnet_long` | `time_stop_10d` | **PASS** | 0.808 (151) | 0.134 | 0.603 | 1.14 | no | YES | N | **bull 0.396**(n=125); bear n=11<30; neutral n=15<30 |
| `r1_break_retest` | `breakeven_plus_trail` | **PASS** | 0.501 (338) | 0.222 | 0.299 | 4.95 | no | no | N | **bull 0.33**(n=272); bear n=26<30; **neutral 1.088**(n=40) |
| `rsi_oversold` | `breakeven_plus_trail` | **PASS** | 0.596 (293) | 0.327 | 0.321 | 5.92 | no | no | N | **bull 0.612**(n=278); bear n=4<30; neutral n=11<30 |
| `rsi_volume_200ema` | `earnings_blackout` | **PASS** | 0.545 (63) | 0.062 | 0.635 | 1.4 | no | no | N | **bull 0.423**(n=56); bear n=1<30; neutral n=6<30 |
| `smc_breaker_block_long` | `breakeven_plus_trail` | **PASS** | 0.693 (356) | 0.408 | 0.393 | 4.77 | no | no | N | **bull 0.479**(n=283); **bear 1.883**(n=35); **neutral 0.827**(n=38) |
| `smc_inverse_fvg` | `regime_flip` | **PASS** | 0.813 (92) | 0.193 | 0.587 | 2.01 | YES | YES | N | **bull 0.242**(n=69); bear n=18<30; neutral n=5<30 |
| `totm_long` | `breakeven_plus_trail` | **PASS** | 0.963 (86) | 0.291 | 0.314 | 10.27 | no | YES | N | **bull 0.45**(n=72); bear n=14<30 |
| `xs_combined_momentum_low_ivol` | `breakeven_plus_trail` | **PASS** | 0.962 (35) | 0.188 | 0.371 | 9.73 | no | YES | N | bull n=27<30; bear n=7<30; neutral n=1<30 |
| `xs_momentum_with_smart_money_long` | `breakeven_plus_trail` | **PASS** | 0.952 (162) | 0.503 | 0.457 | 5.04 | no | YES | N | **bull 0.6**(n=126); bear n=24<30; neutral n=12<30 |

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

## C. DIRECTIVE MIRRORS without any data - 3 cells (exit INHERITED from parent)

Wired in B1382 under the same directive. They have never been backtested, so no exit can be assigned from measurement. **Owner decision 2026-07-26: they inherit their long parent's exit as the default.** All are tagged EXPLORATORY and excluded from the multiple-testing family; the inherited exit is a placeholder to be re-measured the first time these run on a bear-inclusive window, not a validated choice.

| Parent LONG | Short mirror | Inherited exit | Source of that exit | Evidence |
|---|---|---|---|---|
| `news_sentiment_long` | `news_sentiment_short` | `breakeven_plus_trail` | inherited from parent (owner decision 2026-07-26) | none - never backtested |
| `poc_magnet_long` | `poc_magnet_short` | `time_stop_10d` | inherited from parent (owner decision 2026-07-26) | none - never backtested |
| `xs_combined_momentum_low_ivol` | `xs_combined_momentum_high_ivol_short` | `breakeven_plus_trail` | inherited from parent (owner decision 2026-07-26) | none - never backtested |

## D. NATIVE-REGIME GATE - does grading each direction in its OWN regime rescue the shorts?

Owner correction 2026-07-26: *"our gates do not test for success of short strategies in bear regimes and success of long strategies in bull regimes specifically."* Correct - the grading above pools the holdout year. `scripts/regime_conditional_gate.py` re-grades every row in the regime it is built for (**long -> `bull` entries, short -> `bear` entries**), pre-registered by direction so it stays one test per row rather than a search over regimes. The exit is likewise picked on IS native-regime data only.

| Direction | Rows | OOS PASS | OOS PASS-noFDR | OOS FAIL | OOS UNEVAL (n<30) | IS PASS | IS FAIL |
|---|---|---|---|---|---|---|---|
| long (graded on bull) | 124 | 11 | 29 | 84 | 25 | 11 | 84 |
| **short (graded on bear)** | 88 | **2** | 4 | 82 | **77** | 2 | 82 |

**What this settles.** The correction was right and the gate is now fixed - but fixing it does NOT rescue the shorts, for a reason worth stating precisely:

1. **77 of 88 short rows are UNEVAL out-of-sample** - not failed, *untestable*. With 12 bear days in the holdout there are fewer than 30 bear-regime trades per strategy. No gate design can extract an out-of-sample verdict from tape that isn't there.
2. **In-sample, where the bear data IS ample** (259 bear days, ~30,000 short-in-bear trades), only **2 of 88** short rows clear 0.5 + BH-FDR (`bollinger_tight`, `ppo_crossover`). So regime-conditioning explains part of the shortfall but not all of it - most shorts underperform even on bear-regime entries.
3. **A caveat that cuts against the bear-conditioned test itself:** per L229, `regime_at_entry == bear` is where LONGS earned most (+1.14%/trade) and shorts lost worst (-2.36%) in this window - the classifier flags 'bear' at high-vol/below-200EMA moments that were, here, near local bottoms. So 'short entered when the label said bear' is closer to *shorting the bottom* than to *shorting a downtrend*.

**Conclusion unchanged, but now for the right reason:** shorts are not refuted, they are *untested*. What they need is a bear-inclusive WINDOW (2008 / 2011 / 2015-16 / 2018 / 2020), not a different gate.


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