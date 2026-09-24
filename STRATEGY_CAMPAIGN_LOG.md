<!-- B3096 (2026-09-24). Strategy- and family-specific records moved out of the optimisation runbook
     when it became class-level. Bodies are copied BYTE-FOR-BYTE from
     archive/2026-09-24-strategy-optimisation-plan-pre-B3096/STRATEGY_OPTIMISATION_PLAN.md
     at the line ranges named under each heading. The part and section headings are new, and a
     heading INSIDE a moved block is demoted to #### (its text unchanged); nothing else is edited. -->

# Strategy Campaign Log - per-strategy and per-family records

`STRATEGY_OPTIMISATION_PLAN.md` is the class-level procedure and names no strategy. **This file is where the measured instances live:** dated slates, per-family decisions, worked examples, launch instances and the measurements behind the runbook's rules. It is a RECORD, not an authority - where a record below states a rule, the runbook is the rule's current home, and a record's old section references (SS10.1, §11.2b2, STEP 3.2 ...) resolve through the runbook's APPENDIX M.

**Adding to it:** a new campaign's records are appended under its family's part (or a new part), with the date and the batch; never edit a record's body to make it current - add a dated line.

## Contents

- **A. PROGRAMME RECORDS** - A.1, A.2, A.3, A.4, A.5, A.6, A.7, A.8, A.9, A.10
- **B. smc FAMILY (the breaker pair is FINALISED and ADMITTED - owner 2026-09-03 / 2026-09-12)** - B.1, B.2, B.3, B.4, B.5, B.6, B.7, B.8, B.9, B.10, B.11, B.12, B.13, B.14, B.15, B.16
- **C. INSTITUTIONAL FAMILY (CLOSED)** - C.1, C.2, C.3
- **D. PEAD FAMILY (CLOSED)** - D.1, D.2, D.3
- **E. CROSS-SECTIONAL MOMENTUM (xs_momentum_top_decile, vwap_extension, xs_low_beta)** - E.1, E.2, E.3
- **F. CANDLE FAMILY (three_white_soldiers / three_black_crows_short - IN CAMPAIGN)** - F.1, F.2, F.3, F.4, F.5, F.6
- **G. FAMILY EXAMPLES OF CLASS-LEVEL COMMANDS AND ARTIFACTS** - G.1, G.2, G.3, G.4, G.5, G.6, G.7, G.8
- **H. SHARED LAUNCH MEASUREMENTS (both families)** - H.1, H.2

---

## A. PROGRAMME RECORDS

### A.1 Supersession banner, B1500-B1510 (old §0a)

*Source lines 14-26, verbatim.*

#### 0a. SUPERSESSION BANNER — B1500-B1510 (2026-08-10)

The first worked example (`smc_breaker_block_long`) ran end-to-end and **corrected four load-bearing
claims in this plan.** Read this before Sections 2.2 / 2.3 / 2.3a, which are marked inline.

| # | claim as originally written | corrected by measurement |
|---|---|---|
| 1 | "no resimulation is required for tightening" | **Only for SUBSET-SAFE parameters.** A parameter that can ADD fires (`swing_length`, EMA `span`) produces trades R5 never took, and the cube holds no P&L for those. §2.3a corrected. |
| 2 | population = 41 strategies at n>300 | **The band is built on UNVERIFIED n.** The worked example's measured holdout n is **147**, not the 356 carried — it was never in the n>300 band. **The whole partition must be re-derived from measured n (S6-B1502a).** |
| 3 | tunable surface = numerics in the gate expression | **Wrong layer.** The surface is the transitive closure of the PRODUCER parameters. A strategy whose gate is two booleans still had 6 producer parameters (L355). |
| 4 | cost scales with combinations | **Cost = ENGINE RUNS = product of the fire-ADDING bands only.** 4,000 combinations needed **20** runs, not 4,000 (L371). |

**Reporting is now standardised and mechanically enforced — see §6.**

### A.2 Step-1 window - the three constraints cannot all be met, B1817 (old §0b)

*Source lines 28-60, verbatim.*

#### 0b. STEP-1 WINDOW — THE THREE CONSTRAINTS CANNOT ALL BE MET (B1817, MEASURED)

**`S6-B1605c` withdrew the acceptance of Step 1 reading the holdout and proposed moving Step 1 to
`2023-05-05 -> 2025-05-05`. That remedy CONTRADICTS the 2026-08-17 ruling** in SS10.1: *"2022-23 data
is not wanted even for exit selection. Both phases run 2024-05-05 -> 2026-05-05."*

Three standing constraints, and no window satisfies all three:

| constraint | source |
|---|---|
| holdout LOCKED to `2025-05-05 -> 2026-05-05` | SS0, owner 2026-08-09 |
| no 2022-23 data, even for exit selection | SS10.1, owner 2026-08-17 |
| Step 1 must not rank on the holdout | `S6-B1605c`, owner 2026-08-17 (*"undo"*) |

**The obvious compromise is measurably self-defeating.** A Step-1 window of
`2024-05-05 -> 2025-05-05` honours all three by construction, but MEASURED on the four existing
cubes it keeps only **50-56 pct of entries**:

```
cfg1              330 entries  ->  183 (55.5pct) before the holdout boundary
cfg2              420          ->  236 (56.2pct)
w1_sw20_span21    320          ->  167 (52.2pct)
w1_sw20_span50    302          ->  152 (50.3pct)
```

**At the FULL sample, `--min-n 10` still leaves 32-60 pct of the grid `NO_EXIT_SELECTABLE`.** Halving
the sample pushes most of it back to unanswerable, so the window fix destroys the search it is meant
to make trustworthy.

**Therefore `S6-B1605c` and `S6-B1696c` are ONE decision, not two.** Restoring the sample at a
holdout-respecting window needs the universe lever - 100 -> ~200 tickers, roughly doubling fires at
~2x runtime (`S6-B1696c` option (a)). **That is the only path that satisfies every constraint; it
pays in runtime rather than in correctness or data policy.**

### A.3 Open owner decisions, live as of B1510 (old §8)

*Source lines 737-762, verbatim.*

#### 8. OPEN OWNER DECISIONS (live as of B1510)

> **2026-08-23 (B2042): E1 DROPPED as a roster path (owner ruling).** The five-arm pilot
> closes as measurement only; Phase-1B admission runs ONLY through this document's
> 0->1->2->3 protocol at its ruled shapes, and noise-elimination verification happens in
> the protocol's own Step 2 on the remaining Tier-1a tickers - not via ad-hoc validation.
> Canonical rows: S6-B1505b (closure) / S6-B2018a (unblocked).
>
> **2026-08-22 (B2016): the A-I owner ruling set resolved this table's live members.** E1 approved -
> the P1 swing sweep {10,20,30,50} runs on SP50 at the ruled 1y search window (arms in flight,
> `output_b2016_e1/run_manifest.json`); F1 `EMA_PAIRS` plumb SHIPPED (B2016); F2 spans 100/250
> NOT approved yet; E5 concurrency cap N=2. Ledger rows under S6-B1505b / S6-B1518a are canonical.

| ticket | decision |
|---|---|
| **S6-B1508a** | 10-ticker timed run to establish the multi-ticker slope (~6 min). **Removes the last unknown from the cost model.** |
| **S6-B1507b** | Add EMA spans 100/250? They do NOT exist in `compute_ema_sma` — producer edit, NEW-GATE class. |
| **S6-B1505a** | Test-universe policy: SP50 vs R5-fired vs full T1a, with a retention-ratio precheck. |
| **S6-B1509a** | Wire `max_drawdown` / `calmar` / `deflated_sharpe` into `roster_core.evaluate()` as reported-not-gated. |
| **S6-B1502a** | Re-derive the whole band partition from MEASURED holdout n before Phase 1 is scoped. |
| **S6-B1505b** | Approve engine resimulation for P1/P6 — gated on S6-B1508a's number. |

**Standing rule (`feedback_ask_before_adding_gates_vs_threshold_only`):** whether optimisation may
ADD a gate or stays threshold-only is situational — **ask every time**. Label every knob
EXISTING-THRESHOLD or NEW-GATE before building any grid.


### A.4 Standing open decisions the run-safety work fed (old REFERENCE block)

*Source lines 2344-2355, verbatim.*

#### Standing open decisions this section feeds (owner)

1. **Venue** (S6-B2107a): local pilot FAILED its gate at the old cap on measured
   evidence; at 5h a config fits un-chunked. Hetzner auction remains ruled, gated on a
   completed local strategy.
2. **W-B relaunch**: no run is in flight; sw50's resume is one command (its spec carries resume=true), sw30's requires the one-line spec edit FIRST (resume=false as written - L646: a recovery quoted as cheap must have its config opened, because this one would have restarted day 0 over a day-57 checkpoint); neither is taken
   without the owner's word (feedback_ask_before_relaunching_corrected_version).
3. **regime_flip retirement** (S6-B2139a): refused on stale evidence — 42 of 95 rows in
   the post-fix reference cube are REAL flips.
4. **Wave methodology**: four completed configs = ONE grid under four cross-config
   settings, zero above the 0.333 noise floor; the council's falsification/breadth
   alternatives are on record (B2142 council).

### A.5 Programme state 2026-09-07, B2631

*Source lines 2693-2730, verbatim.*

#### PROGRAMME STATE 2026-09-07 (B2631) — icg CLOSED, family CLOSED, working order

**Verdict chain (artifacts named; this section supersedes the Step-1-era section below for
programme state, which is kept for design lineage):**
- **Step 2 (the pre-registered holdout shot, span9):** FAIL, 5 of 6 gates — holdout sharpe 0.757
  vs the 1.0 bar on 1,107 holdout trades (4,616 full-period); PF 2.64 / sortino 2.60 / PSR 1.0 /
  both min-trade gates all PASS. Exit mismatch DISCLOSED per owner ruling 2(i): IS selected
  breakeven_plus_trail, the pre-registered regime_flip recorded and never read on holdout.
  Artifact: output_audit/output_icg_step2_span9_step2_span9_grid_auto.json (step2 block).
- **Family closure (owner ruling 2026-09-06 "Option (c) with pre-registration, then (b)"):**
  the 19 siblings graded FAIL by the pre-registered offline pass — pooled_sharpe fails 19 of 19;
  R1 (non-shared-holdout trigger) fired 0 of 19; the challenge-test holdout-peek bound cleared
  1.0 in 0 of 480 cells (family ceiling 0.852 even with hindsight exit selection). Artifacts:
  output_audit/b2628_family_pass_prereg.json (registered BEFORE the run),
  output_audit/b2628_institutional_family_grades.json (every row carries overlap-with-icg).
  Family basis: 6x trade overlap (29,397 summed entries -> 4,866 union), measured on
  output_r5_merged_1_7/trade_exit_detail.csv.
- **Council verdict (owner-convened, recorded S6-B2627):** no engine campaigns on collinear
  siblings; a family-collinearity PRE-GATE runs before every future campaign-target selection
  (S6-B2627a, helper to build). Known data gap: AAPL and GOOGL 13F files are EMPTY (S6-B2630).

**TIGHTENING band accounting (measured, from output_audit/b1453_phase_1b_roster.json —
best-cell holdout n > 300, excluding the 4 rostered longs; supersedes the unverified 41):**
**43 total = 10 DONE (all institutional_, closed FAIL) + 2 disabled-in-band (macd_crossover_short,
macd_ichimoku) + 31 PENDING.**

**WORKING ORDER for the pending 31 (per the S6-B2418 owner-decision row, option 1 = icg consumed;
best-cell numbers are SELECTED maxima, a sequencing key only):**
1. **pead_long_high_yoy_growth_only** (0.704, n=422, PF 3.14) — S6-B2418 option 2; a DIFFERENT
   producer chain (earnings/YoY growth), per the council's chain-diversity requirement.
   **DONE - ADMITTED to the roster (B2645/B2646; psr computes 0.9998 post-fix); family CLOSED at B2647 by pre-registered sibling pass. See the FAMILY CLOSED paragraph in the campaign section.**
2. rsi_oversold_with_smart_money_long (0.735, n=618) — ranked higher but FLAGGED in S6-B2418
   (roster-family similarity; consolidate before tune).
3. macd_crossover (0.708, n=422) + macd_fast_crossover (0.646, n=589) — the macd family goes
   through the pre-gate as a unit.
4. avwap_252_breakout (0.640, n=314), force_index_breakout (0.625, n=417),
   r1_break_retest (0.602, n=398), then the remainder of the 31.
The pick is the owner's (S6-B2418 stands OPEN); no launch without it.

### A.6 Grid-stage multiplicity priced + the gradability census, B2676/B2677

*Source lines 3000-3019, verbatim.*

#### GRID-STAGE MULTIPLICITY PRICED + THE GRADABILITY CENSUS (B2676/B2677)

S6-B2638a EXECUTED: offline_level_sweep.py now carries a permutation null
(--null-perms; magnitudes shuffled across fires, identical grid re-graded; maxima are
SYNTHETIC and price the search, never performance; two-arm pin
test_b2676_permutation_null_prices_the_grid). RETRO-PRICE of the pead 390-trial grid
(200 perms, seed 13, output_audit/b2676_pead_null_retroprice.json): observed best IS
1.475 vs null best-of-390 q50 0.905 / q95 1.205 / q99 1.351 -> p 0.005 (0 of 200
reached it) - the pead Step-1 best survives its multiplicity price. CALIBRATION
READING: on this population a 390-trial search manufactures ~1.2 at q95 by luck, so a
bare 1.0 IS bar is inside search-luck range - every future offline campaign should run
--null-perms and read its best against ITS OWN null.

S6-B2638c EXECUTED: scripts/offline_gradability_census.py - 217 actives mapped onto
the persisted keyspace (837 keys, 2,000 stride-sampled trades):
**160 FULLY-FREE / 36 PARTIAL / 21 NEEDS-ENGINE** (b2677_offline_gradability_census
.json). 160 of 217 backlog campaigns are offline-seconds instead of 16-40 engine
hours. Two reader defects self-caught by the L644 hand-read of anchors before quoting:
a head-sample keyspace missed sparse true-only keys, and boolean .get(k, False) gates
are reconstructable with absent=False (the B2674 lesson) - fixed, anchors re-verified.

### A.7 Optimisation population by bucket and family, B2632

*Source lines 3171-3241, verbatim.*

#### OPTIMISATION POPULATION BY BUCKET AND FAMILY (B2632, owner directive 2026-09-07)

**Accounting (derived live at B2632; every term from the registry + config disabled sets +
the measured-band artifact output_audit/b1453_phase_1b_roster.json):**

| bucket | count |
|---|---|
| Active registered | 215 |
| - Roster (qualified, not to optimize) | 7 |
| - institutional_* family (closed, executed grades, B2612-B2628) | 20 |
| **= REMAINING to optimize** | **188** |

**Roster 7 (4 longs + 3 retained short mirrors):** `xs_momentum_top_decile`, `52w_high_breakout_pullback_long`, `xs_momentum_with_smart_money_long`, `smc_breaker_block_long`, `smc_breaker_block_short`, `52w_low_breakdown_pullback_short`, `xs_momentum_bottom_decile_short`

**institutional_* 20 (closed):** `institutional_breakout_confirmation_long`, `institutional_buy_momentum_long`, `institutional_cluster_long`, `institutional_committed_growth_long`, `institutional_high_conviction_long`, `institutional_increased_with_directors_long`, `institutional_insider_combo_long`, `institutional_multi_quarter_persistence_long`, `institutional_oversold_long`, `institutional_persistence_breakout_long`, `institutional_persistence_momentum_long`, `institutional_persistence_oversold_long`, `institutional_persistence_volume_long`, `institutional_persistent_holders_long`, `institutional_recent_init_momentum_long`, `institutional_recent_init_volume_long`, `institutional_strong_conviction_long`, `institutional_volume_confirmation_long`, `institutional_with_directors_long`, `institutional_with_officers_long`

**The 188 remaining, grouped by FAMILY (name-prefix heuristic - a family is CONFIRMED or
split only by the S6-B2627a collinearity pre-gate's measured trade overlap, which runs before
any family's campaign target is picked). Band tags per member: (T) tightening holdout n>300,
(M) mid-band 100<n<=300, (L) low-n 0<n<=100, (-) no graded cell in R5. Split: 29 T / 52 M /
41 L / 66 no-cell. 41 multi-member families cover 138 strategies; 50 are singletons.**

- **smc** (16) [-:4 L:6 M:5 T:1]: `smc_bos_continuation`(-), `smc_bos_retest_entry`(L), `smc_choch_reversal`(L), `smc_discount_long`(L), `smc_equal_highs_sweep_short`(M), `smc_equal_lows_sweep_long`(M), `smc_fvg_retest_long`(-), `smc_fvg_retest_short`(L), `smc_inverse_fvg`(M), `smc_liquidity_sweep_reversal`(T), `smc_mitigation_block_long`(-), `smc_mitigation_block_short`(-), `smc_order_block_bounce`(M), `smc_ote_long`(L), `smc_ote_short`(L), `smc_premium_short`(M)
- **news** (7) [-:4 L:2 M:1]: `news_momentum_long`(-), `news_momentum_short`(-), `news_reversal_long`(-), `news_reversal_short`(-), `news_sentiment_long`(M), `news_sentiment_shift_long`(L), `news_sentiment_short`(L)
- **pivot** (7) [-:5 L:1 M:1]: `pivot_fib_confluence`(-), `pivot_r1_breakout`(M), `pivot_r2_continuation`(-), `pivot_r3_blowoff_short`(-), `pivot_s1_bounce`(L), `pivot_s2_bounce`(-), `pivot_s3_capitulation`(-)
- **donchian** (6) [M:6]: `donchian_10_breakout`(M), `donchian_breakdown_retest_short`(M), `donchian_breakdown_short`(M), `donchian_breakout_long`(M), `donchian_breakout_retest_long`(M), `donchian_breakout_with_smart_money_long`(M)
- **pead** (6) [-:2 M:2 T:2]: `pead_long`(-), `pead_long_high_yoy_growth_only`(T), `pead_short`(M), `pead_short_negative_yoy_growth`(T), `pead_with_insider_confirmation_long`(-), `pead_with_smart_money_long`(M)
- **xs** (6) [-:2 L:3 M:1]: `xs_combined_momentum_high_ivol_short`(M), `xs_combined_momentum_low_ivol`(L), `xs_low_beta_long`(-), `xs_low_beta_with_smart_money_long`(L), `xs_momentum_quality_combined`(L), `xs_quality_top_quintile_long`(-)
- **52w** (4) [-:3 L:1]: `52w_high_breakout`(-), `52w_high_breakout_with_smart_money_long`(-), `52w_high_breakout_with_smart_money_vol_below_long`(L), `52w_low_breakdown`(-)
- **bollinger** (4) [-:1 L:1 M:2]: `bollinger_lower`(M), `bollinger_tight`(-), `bollinger_tight_with_smart_money_long`(M), `bollinger_upper_short`(L)
- **golden** (4) [-:2 L:1 M:1]: `golden_cross_20_50`(L), `golden_cross_50_200`(-), `golden_cross_9_21`(M), `golden_cross_volume`(-)
- **pre** (4) [-:4]: `pre_fomc_long_sleeve`(-), `pre_fomc_quality_momentum_long`(-), `pre_holiday_long`(-), `pre_rebalance_long`(-)
- **rsi** (4) [-:1 L:1 M:1 T:1]: `rsi_overbought_short`(-), `rsi_oversold`(M), `rsi_oversold_with_smart_money_long`(T), `rsi_volume_200ema`(L)
- **avwap** (3) [-:1 M:1 T:1]: `avwap_20high_rejection_short`(-), `avwap_252_breakout`(T), `avwap_50_reclaim`(M)
- **cpr** (3) [M:2 T:1]: `cpr_narrow_bullish`(M), `cpr_narrow_momentum`(M), `cpr_narrow_momentum_short`(T)
- **flag** (3) [-:3]: `flag_bear_retest_short`(-), `flag_bull_long`(-), `flag_bull_retest_long`(-)
- **ichimoku** (3) [L:1 M:2]: `ichimoku_cloud_breakdown`(L), `ichimoku_cloud_breakout`(M), `ichimoku_tk_cross`(M)
- **insider** (3) [-:2 L:1]: `insider_cluster_concentrated_sell_short`(L), `insider_cluster_long`(-), `insider_cluster_with_director_long`(-)
- **macd** (3) [M:1 T:2]: `macd_bullish_with_smart_money_long`(M), `macd_crossover`(T), `macd_fast_crossover`(T)
- **post** (3) [-:2 L:1]: `post_deletion_drift_short`(-), `post_inclusion_drift_long`(-), `post_inclusion_reversal_short`(L)
- **prev** (3) [M:3]: `prev_day_high_break`(M), `prev_day_low_bounce`(M), `prev_day_low_breakdown`(M)
- **supertrend** (3) [-:1 L:2]: `supertrend_ichimoku_adx`(-), `supertrend_macd`(L), `supertrend_macd_short`(L)
- **triangle** (3) [-:1 L:1 M:1]: `triangle_ascending_long`(L), `triangle_ascending_retest_long`(-), `triangle_descending_short`(M)
- **break** (2) [M:1 T:1]: `break_retest_confluence`(M), `break_retest_volume`(T)
- **camarilla** (2) [L:1 T:1]: `camarilla_r4_breakout`(T), `camarilla_s3_bounce`(L)
- **cup** (2) [-:1 L:1]: `cup_and_handle_long`(L), `cup_and_handle_retest_long`(-)
- **doji** (2) [L:2]: `doji_at_resistance_short`(L), `doji_at_support`(L)
- **head** (2) [L:2]: `head_and_shoulders_bottom_long`(L), `head_and_shoulders_top_short`(L)
- **htf** (2) [L:1 M:1]: `htf_aligned_breakout_long`(L), `htf_aligned_breakout_short`(M)
- **judas** (2) [-:2]: `judas_swing_long`(-), `judas_swing_short`(-)
- **mfi** (2) [-:1 L:1]: `mfi_oversold`(-), `mfi_oversold_with_smart_money_long`(L)
- **orb** (2) [-:1 L:1]: `orb_stocks_in_play_long`(-), `orb_stocks_in_play_short`(L)
- **pairs** (2) [T:2]: `pairs_mean_reversion_long`(T), `pairs_mean_reversion_short`(T)
- **parabolic** (2) [M:1 T:1]: `parabolic_sar_flip`(M), `parabolic_sar_flip_short`(T)
- **po3** (2) [M:1 T:1]: `po3_bearish`(T), `po3_bullish`(M)
- **poc** (2) [M:2]: `poc_magnet_long`(M), `poc_magnet_short`(M)
- **squeeze** (2) [-:1 M:1]: `squeeze_breakout`(M), `squeeze_setup_long`(-)
- **stochrsi** (2) [T:2]: `stochrsi_overbought_short`(T), `stochrsi_oversold`(T)
- **three** (2) [T:2]: `three_black_crows_short`(T), `three_white_soldiers`(T)
- **turtle** (2) [L:1 T:1]: `turtle_soup_long`(L), `turtle_soup_short`(T)
- **week** (2) [M:2]: `week_opening_gap_fill_down`(M), `week_opening_gap_fill_up`(M)
- **weekly** (2) [-:2]: `weekly_bias_pullback_long`(-), `weekly_bias_pullback_short`(-)
- **williams** (2) [M:1 T:1]: `williams_r_oversold`(T), `williams_stoch_dual`(M)

- **singletons** (50): `52wh_break_retest`(-), `52wl_break_retest_short`(-), `activist_13d_long`(-), `adx_initiation`(-), `awesome_oscillator`(M), `bb_squeeze_volume`(M), `bullish_engulfing_support`(M), `cmf_flip`(T), `consec_downdays_quality_long`(-), `dc20_break_retest`(T), `death_cross_50_200_volume`(-), `double_bottom_long`(L), `earnings_avwap_reclaim_long`(-), `failed_breakout_2b_short`(-), `force_index_breakout`(T), `gap_and_go_long`(-), `gold_silver_risk_off_long`(-), `halloween_seasonal_long`(-), `hammer_at_support_long`(L), `hull_rsi`(M), `inside_bar_breakout`(M), `inverted_cup_and_handle_short`(L), `january_effect_small_cap_long`(-), `keltner_lower`(-), `m_and_a_target_long`(M), `mmbm_long`(T), `mmsm_short`(T), `monthly_bias_momentum_long`(-), `morning_star`(T), `naked_poc_retest_long`(T), `pocket_pivot_long`(-), `ppo_crossover`(M), `r1_break_retest`(T), `risk_off_bond_equity_short`(L), `roc_burst`(M), `rs_line_sector_leader_long`(-), `rsi21_slow`(-), `rsi9_extreme`(-), `sector_rotation_defensive_long`(-), `shooting_star_short`(L), `short_borrow_trap_avoid`(-), `simple_below_ema_50_short`(T), `stoch_oversold`(L), `tema_dema`(M), `totm_long`(L), `ultimate_oscillator`(L), `value_area_breakout_long`(L), `vix_backwardation_long`(M), `vol_spike_2x_below_ema_50_short`(M), `volume_spike_breakout`(M)

**Family-level reading (the analyze-by-families directive):** the campaign unit is the
FAMILY, not the registration - the institutional closure measured 20 names collapsing to
~1.2 independent bets. Before any family's campaign: run the pre-gate (overlap + band
clustering + the median-exit holdout beside the best-cell key), pick ONE representative,
and let its verdict plus a pre-registered sibling pass close the family, as B2628 did.

### A.8 On-ramp registrations - which strategies each R-row was satisfied for (old §11.1 last column)

*Source: the last column of the old §11.1 table, lines 3458-3467, verbatim.*

| row | Exists today for (as of B3095) |
|---|---|
| R1 | smc, institutional; **candle pair PROMOTED to SPECS at B2897 and NOW CLEAN - family_refusal returns the empty string for both legs as of S6-B2900, FAMILIES 6 -> 8, FAMILY_REFUSALS 2 -> 0, and launch_refusals against the real repo root returns 0 for the pair. The gap MOVED TWICE before closing, which is the gate working rather than a stall: `tools` block lacks [spot_check] -> (B2899 built `scripts/spot_check_candle.py`, MEASURED 120 of 120 sampled rows agreeing across 3 configs and 2 directions) -> `tools.grade` lacks [cube] -> CLOSED at S6-B2900 by `scripts/grade_candle_config.py`. That last gap was NOT a missing string: the leg pointed at `offline_level_sweep.py`, which has no `--cube` flag, requires `--band-ruling`, emits an unsubstituted argv token from `_flag_args`, parses `--production` as a float (the candle wick level is the EMPTY STRING, meaning no bound), demands a status stamp equal to git HEAD, is in-sample by construction so it can never emit the Step-2 gate verdict the battery fails closed without, and pins CUBE/TRADE_LOG to `output_r5_merged_1_7` as MODULE CONSTANTS - so wiring it would have graded the wrong cube while faithfully stamping whichever flags it was handed. The new grader delegates EVERY statistic to `roster_core` (measured: zero self-computed statistics, 12 delegations), takes the graded strategy from the manifest's `strategy_subset` via `run_postconfig.graded_and_riders` rather than by counting strategies - because a long/short pair run in one engine pass puts BOTH legs in one cube (B2721) and a count would refuse the campaign's own shape - and VERIFIES the four CANDLE_* flags against the landed arm's env, refusing on mismatch and on an absent env block. MEASURED end to end on a rider-bearing cube of 85,020 real rows: graded three_white_soldiers alone (41,496 of them), 26 exits ranked, and `run_postconfig.grid_step2_graded` returns True on the emitted grid. **That remainder is now CLOSED at S6-B2904: `scripts/grade_free_levels_candle.py` is wired as the `free_levels` leg on both entries, so P6's free band is graded on every landing (B2569 / #290). It is offline and costs zero engine hours - rsi_14 sits in signals_at_entry for 1596 of 1596 soldiers and 1674 of 1674 crows rows of output_r5_merged_1_7/trade_log.csv, coverage 1.0000 - and it mirrors the producer's STRICT comparison (`rsi_14<60` / `rsi_14>40`, screener.py:2607 and :2637), reproduction-gated at the production bound before any level is graded. MEASURED on the R5 cube, reproduction 1596 and 1674 covered with 0 unverifiable and 0 failed: every free level DEGRADES both legs monotonically as it tightens - soldiers ci_lo 0.035 at 54.42 down to -0.028 at 41.97, crows -0.057 at 45.094 down to -0.247 at 58.812 - so the axis offers nothing on current evidence. THE HONEST LIMIT IS DISCLOSED IN THE ARTIFACT, not papered over: a subset of SIGNALS is not a subset of TRADES (L812), because a tighter bound frees occupancy and would admit trades present in no cube, so every trade count is a LOWER BOUND and the verdicts are candidates rather than admissions. On the R5 cube the correction is UNQUANTIFIABLE - 391,782 of 391,782 occupancy rows carry the pre-B2905 literal stamp - while cubes written after B2905 carry a real per-strategy count.** **DISCLOSED LIMIT (B2883b): the adapter refusal keys on an env knob PLUS a `resim_band` level off production, so it is SILENT on the pre-B2467 entry shape that never split free/resim - MEASURED, `smc_breaker_block_long` carries `resim_band: None` on all 6 params and registers ZERO engine axes, so the most-run engine family in the repo evades this gate entirely. It covers new entries and misses legacy ones; R1 is NOT closed. Widening it to refuse any env knob with no free/resim split would refuse all five smc entries today, which is the refuse-everything failure - that migration is a separate backlogged batch.** |
| R2 | smc, institutional |
| R3 | smc (3 of 4 - no free-levels leg), institutional (4 of 4) |
| R4 | `tighten_breaker_block.py` (smc), `grade_institutional_config.py` (institutional) |
| R5 | `grade_free_levels_institutional.py` (institutional); **`scripts/offline_level_sweep.py` is the GENERIC one (B2638)** - the axis map is an argument, so a new strategy is a new `--axes`, not a new script |
| R6 | `spot_check_trades.py` (smc), `spot_check_institutional.py` (institutional), **`spot_check_candle.py` (candle pair, B2899 - leg A re-derives the anatomy from raw bars and never imports the producer, which is what makes the agreement evidence rather than a tautology)** |
| R7 | `verify_engine_implemented.py` (smc); inline grep in `run_institutional` |
| R8 | ENFORCED for smc + institutional (B2578 knobs, B2579 consumer lists) |
| R9 | institutional |
| **R10 (ADVISORY - NEVER BLOCKING)** | MEASURED on output_r5_merged_1_7: three_white_soldiers rsi_14<60 reproduces the landed set exactly (1596 kept = 1596 landed, coverage 1.0000) and all 4 levels clear the floor 321/273/197/121; three_black_crows_short rsi_14>40 likewise (1674 = 1674) at 470/389/289/171 |

### A.9 Status-view programme counts (old §11.2b3a)

*Source lines 3731-3734, 3767-3774, verbatim.*

as work to start.** L802 records the miss it exists to prevent: a ranking built from the
strategies' properties and none of the ledger's recommended the institutional family, which
was already finished - 9 of the 14 Phase-1B admissions are institutional, and 2 of the 6
strategies named were themselves admitted.

**Tightening candidates by family, largest first (re-measured at B2827 on the B2825 build):**
news_sentiment 6, candle 5, momentum 5, mean_reversion 4, confluence 4, smc 3, then pivot /
volume_profile / pairs at 2 each. **institutional_persistence appears NOWHERE in this table
any more, deliberately:** the "institutional_persistence 5" the B2808-era sentence carried
here were closed-family residue sitting in lanes the pre-B2825 vocabulary could not evict -
measured at B2827, all five are TERMINAL (4 PRUNED-DUPLICATE under the Jaccard-0.70 canonical
rule, 1 CLOSED-NEGATIVE from the b2628 family pass) and zero members of that family remain in
any tightening lane. The institutional family is DONE: worked, judged, admitted-or-discarded.

### A.10 The 38 strategies whose entry condition moved after R5, B2806 (old §11.2b4)

*Source lines 3790-3875, verbatim.*

#### 11.2b4 THE 38 STRATEGIES WHOSE ENTRY CONDITION MOVED AFTER R5 (B2806, owner-directed 2026-09-13)

**Why this list exists.** R5 (`output_r5_merged_1_7`, trade_log dated 2026-07-24) is the
comparison basis for every offline read. A strategy's ENTRY CONDITION - the boolean in
`screener.py` deciding whether it fires on a bar - may have been edited since. Where it
was, R5 records a population the current condition would NOT produce, and any figure read
off those rows describes a strategy that no longer exists in that form.

**MEASURED 2026-09-13** by AST-diffing every `strat_*` function between the R5-era screener
commit `fee970996` and HEAD:

| | count |
|---|---|
| strategy functions at R5 | 219 |
| strategy functions now | 223 |
| present in both | 210 |
| **entry condition CHANGED since R5** | **38 (18.1%)** |
| added since R5 | 13 |
| **unchanged - R5 is a clean basis** | **172** |

**THE 38, by family**

- **smc / ICT (4)** - `smc_breaker_block_long`, `smc_breaker_block_short`,
  `smc_liquidity_sweep_reversal`, `smc_order_block_bounce`
- **Institutional / smart money (6)** - `institutional_committed_growth_long`,
  `institutional_insider_combo_long`, `institutional_volume_confirmation_long`,
  `xs_low_beta_with_smart_money_long`, `xs_momentum_with_smart_money_long`,
  `52w_high_breakout_with_smart_money_vol_below_long`
- **Cross-sectional (3)** - `xs_momentum_bottom_decile_short`,
  `xs_quality_top_quintile_long`, `pairs_mean_reversion_long`
- **Trend / momentum indicators (9)** - `awesome_oscillator`, `cmf_flip`,
  `ichimoku_cloud_breakdown`, `ichimoku_tk_cross`, `macd_ichimoku`, `supertrend_macd`,
  `supertrend_macd_short`, `tema_dema`, `avwap_50_reclaim`
- **Breakout / retest (7)** - `break_retest_volume`, `dc20_break_retest`,
  `prev_day_high_break`, `52wl_break_retest_short`, `52w_low_breakdown_pullback_short`,
  `camarilla_r4_breakout`, `avwap_20high_rejection_short`
- **Patterns / events / other (9)** - `head_and_shoulders_top_short`, `morning_star`,
  `news_momentum_long`, `pead_short_negative_yoy_growth`, `m_and_a_target_long`,
  `risk_off_bond_equity_short`, `simple_below_ema_50_short`,
  `vol_spike_2x_below_ema_50_short`, `pairs_mean_reversion_short`

**THE 38 IS AN UPPER BOUND ON BEHAVIOURAL CHANGE.** The diff counts any code difference, so
a rename or a configurable-span swap is included. MEASURED examples of each kind:

- `institutional_committed_growth_long` changed `price_above_ema_200` ->
  `price_above_ema_{STRAT_EMA_SPAN}`: **identical at the default span 200**, no thesis change.
- `institutional_insider_combo_long` changed `institutional_buy` **OR**
  `insider_cluster_active` -> **AND**: a real tightening.
- `institutional_volume_confirmation_long` gained `stoch_d >= 45.63`: a real tightening.

**ROSTER EXPOSURE: 3 of 14 admitted strategies are in the 38, and 0 of 3 are at risk.** Each
changed BEFORE its admission was graded, so every admission used the current condition -
`smc_breaker_block_long` (artifact 2026-08-30), `institutional_committed_growth_long`
(2026-09-10), `xs_low_beta_with_smart_money_long` (2026-09-11), each with ZERO edits to its
function after its artifact. The other 11 admitted are unchanged since R5.

**HOW THIS BINDS THE WORKFLOW - it is the STEP 0.6 check, made concrete.** Before reading any
R5 figure for a strategy, re-evaluate its CURRENT condition against the persisted
`signals_at_entry` of its recorded fires and state the survival rate. MEASURED for four:

| strategy | R5 fires | still satisfy the current condition |
|---|---|---|
| `turtle_soup_short` (not in the 38) | 1,880 | 1,880 (100.0%) |
| `smc_liquidity_sweep_reversal` | 2,933 | 151 (5.1%) |
| `smc_order_block_bounce` | 1,340 | 0 - the gate key post-dates the cube |
| `smc_breaker_block_long` / `_short` | 948 / 1,598 | 0 / 0 - same reason |

**A LOW SURVIVAL RATE IS NOT A VERDICT ON THE STRATEGY (owner ruling 2026-09-13).** Owner,
verbatim: *"Just because the logic changed for sweep-liquidity strategy and we have just 151
fires it doesn't mean that the strategy is bad or has no edge. It's simply then a question of
varying thresholds within producers to find the best combination. That also qualifies it for
strategy optimization even if it's loosening."*

This corrects a reading filed the same day that called hub-1 "not worth engine hours". The
OFFLINE path is tightening-only BY CONSTRUCTION - a looser level admits bars the cube never
recorded - but the ENGINE has no such limit, and DEPTH over all producer bands INCLUDING
loosening is Priority 1 (11.2b2b). MEASURED on a seeded 120-fire sample of the 2,782
bos-only R5 fires (118 of the 120 were diagnosable; the percentages divide by 118), re-deriving the liquidity primitive at wider clusters: **0.0% gain a sweep
at production 0.01 (the control), 4.2% at 0.02, 10.2% at 0.03** - which scales to roughly
+117 and +284 fires against 151 at production - and those figures are a LOWER BOUND (S6-B2810d): a bar carrying a sweep at 0.02/0.03 plus a CHoCH-only confirmation never fired under the OLD gate, is absent from the cube, and is invisible to this measurement. A knob that plausibly triples the fire count
is a depth axis, not a reason to skip the strategy.

**Rule.** A strategy in the 38 is NOT disqualified and NOT trusted on its R5 numbers. It gets
the survival check first, the result recorded in its spec `note` and queue row, and - where
the current condition is rare - the LOOSENING half of its producer bands scheduled as an
engine depth sweep rather than treated as a dead end.

---

## B. smc FAMILY (the breaker pair is FINALISED and ADMITTED - owner 2026-09-03 / 2026-09-12)

### B.1 Worked example - smc_breaker_block_long, B1500-B1510 (old §7)

*Source lines 646-734, verbatim.*

#### 7. WORKED EXAMPLE — `smc_breaker_block_long` (B1500-B1510)

> **B2117c ANNOTATION:** this worked example was built against the STATE breaker gate
> (`smc_breaker_block_bullish`). **B2114 (owner-approved via the A1 design section 4)
> converted both breaker legs to the retest-EVENT keys
> (`smc_breaker_block_*_retest_recent_5d`)** - the STATE reference cube
> (`output_b2114_ref`) is the comparator. The example's METHOD stands; its gate
> expressions describe the retired anchor.

The first strategy taken end-to-end. Recorded because the method's failure modes only became
visible by running it.

#### 7.1 What was found

**The gate looked untunable and had 6 producer parameters behind it.** `fires = breaker_bullish AND
price_above_ema_200` — two booleans, no numbers. Following each to its producer surfaced
`swing_length`, `close_mitigation`, `tail N`, OB-age recency, the break test, and EMA `span`.

**The signal was saturated.** `smc_breaker_block_bullish` fired on **124 of 124 bars** on AAPL.
Instrumenting the QUALIFYING EVENT rather than the aggregate rate explained why: it is an `OR` over
the last 20 order blocks with **no time limit**, so one block aged 294-469 bars, with price 7.5-60%
away, latches TRUE forever. `tail(20)` is a COUNT window where a TIME window was intended
(S6-B1500a). Same class as B654 `cpr_narrow` (87% True) and B655 `supertrend_bullish` (99.19%).

**Two populations, cleanly separable.** Across 5 tickers: latches at 17-54% distance and 343-407
bars old; true retests at 0.8-0.9% and 49-133 bars. An empty gap on BOTH axes (distance 3-7%, age
134-294), and the axes agree on which bars are which — that gap is what set the bands.

**The tightening DIRECTION was backwards.** A breaker block is a RETEST, so the lever is an UPPER
bound on distance, not a lower one. The original framing would have selected harder for the latches
(L359).

#### 7.2 Result

**0 of 200 combinations passed, across 3 of 6 applicable producers.**
24 gradable, 164 NO_EXIT_SELECTABLE, 12 BELOW_POWER_FLOOR.

| knob | effect |
|---|---|
| OB-age cap <=180 | 352 -> 109 fires, Sharpe **0.473 -> 0.563** — the filter genuinely works |
| `close_mitigation=True` | helps in **12 of 12** matched cells, median **+0.005**, best **+0.059** |
| `tail N` | **inert** — the qualifying event is always among the newest 3 |
| `break_pct_max` (owner-approved NEW-GATE) | **0 of 160 combinations gradable** — economically the cleanest discriminator, statistically unusable at n=352 |

**All 24 gradable cells fail on `pooled_sharpe` alone**; the other five gates pass everywhere. The
best cell reaches 0.617 and then fails TWO gates, because the filtering that lifted the ratio cut
holdout n to 115 and PSR reads sample size.

**The decisive number is not Sharpe.** The R5 baseline's `ci_lo` is **-0.034**. Since a subset
cannot have a tighter confidence interval than its parent, no tightening can produce a subset whose
interval excludes zero. That is a stronger argument than the Sharpe gap because it concerns sample,
not effect size (S6-B1509b).

#### 7.3 Cost model, measured

| quantity | value |
|---|---|
| full factorial | **4,000** |
| subset-safe subspace (derives free per run) | 200 |
| **distinct engine runs** | **20** (4 `swing_length` x 5 EMA `span`) |
| **measured: 1 ticker x 1 config, full window** | **~35 min** (2.11 s/sim-day x 1,003 days) |
| 20 configs at ONE ticker | ~12 h |
| multi-ticker slope | **UNVERIFIED — S6-B1508a** |

**Deliberately not extrapolated to 161 or 503 tickers.** An earlier producer-only estimate came in
**9x light** against the first real engine measurement (L367); per-sim-day cost may amortise across
tickers rather than scale linearly, and a ~6-minute run at 10 tickers settles it.

#### 7.4 Universe finding

The SP50 subset (top 50 by market cap; **50/50 reconciled against T1a, 50/50 with cached OHLCV**)
retains only **31 of 352 fires across 11 of 50 tickers**. All 40 combinations returned
NO_EXIT_SELECTABLE — not a bad result, NO result. **Measure the retention ratio BEFORE running under
any universe restriction, and halt below the gates' n-floor** (L365, S6-B1505c). Two disclosed
limits on the subset itself: only 249 of 503 T1a actives carry `market_cap`, so it is the top 50 of
249 rankable; and selection uses TODAY's cap over a 2022-2026 window, which is survivorship-
flavoured — acceptable for tuning, not for a verdict (S6-B1504a/b).

#### 7.5 What this example changes about the method

1. **Start at the producer layer, always.** The gate expression is not the tunable surface.
2. **Instrument the qualifying event before tuning anything.** Saturation usually means a stale
   member of a disjunction is latching, not that a threshold is loose.
3. **Classify every parameter subset-safe vs fire-adding first.** It decides both the cost model
   and what can be graded offline.
4. **Check retention before restricting the universe.**
5. **A strategy can be un-rescuable for sample reasons rather than edge reasons** — `ci_lo` < 0 on
   the baseline is a stop sign that no amount of tightening addresses.


### B.2 Config assignments as RUN, S6-B1537b (old REFERENCE — ENGINE CONTROLS)

*Source lines 2093-2117, verbatim.*

#### Config assignments as RUN (S6-B1537b, recovered B1915)

The table above gives the sweep knobs and their DEFAULTS. It never recorded
which value each config actually ran, which is the fact `S6-B1537b` says must
never be re-asked. **Recovered from the run's own record,
`output_audit/b1576_par.log`** — not from a plan, a note, or memory:

| config | `SMC_SWING_LENGTH` | `STRAT_EMA_SPAN` | exit | cube rows | wall |
|---|---|---|---|---|---|
| `output_cfg1` | `20` | `200` | 0 | 8,581 | 11,891 s (198.2 min) |
| `output_cfg2` | `10` | `50` | 0 | 10,921 | 11,973 s (199.6 min) |

**`cfg1` is the production anchor** — both knobs at their defaults — so cfg1 vs
cfg2 moves BOTH knobs at once and is not a single-variable comparison. Two
later cubes, `output_w1_sw20_span21` and `output_w1_sw20_span50`, vary the span
alone against `sw=20`.

**Timing measured B1915 from `b1576_cfg1.log` / `b1576_cfg2.log`:** end-to-end
198.1 / 199.5 min, of which the day loop is 195.9 / 197.3 and post-processing
is **2.2 / 2.1 min — 1.1%**. Post-processing is NOT on the slow path, and
re-costing the 20-config sweep on end-to-end rather than day-loop moves it
**32.9 h → 33.3 h (1.2%)**. That costing assumes the **measured** 2-way
concurrency; **3-way and above is unvalidated pending the peak-RSS measurement
(`S6-B1552a`)** — a wall-clock that divides by N says nothing about N copies
fitting in RAM.

### B.3 Demand pruning - measured effect on one strategy (old REFERENCE — WHAT GETS SKIPPED)

*Source lines 2147-2154, verbatim.*

**Measured effect on `smc_breaker_block_long` (1 strategy):**
- Technical: **32 of 33 producers skipped**, 512 → 46 keys, 95.8pct off `compute_all_signals`
- SMC: **3 of 6 primitives skipped** (`retracements` 46.7pct + `fvg` 28.1pct + `bos_choch` 18.1pct of
  SMC cost), 91.5pct off `compute_smc_signals`. `ob`, `liquidity`, `swings` always run.

**SMC redundancy is automatic.** 22 strategies read `smc_*` keys; each keeps exactly the primitives
it needs — verified on `smc_fvg_retest_long` (keeps fvg), `smc_ote_long` (keeps bos_choch +
retracements), `smc_bos_continuation` (keeps bos_choch).

### B.4 Step-2 slate - per-config cost and the applied slate (old STEP 2 ENTRY)

*Source lines 898-922, verbatim.*

**COST, PROJECTED PER CONFIG - NOT FROM THE MEDIAN (S6-B2364).** Source:
output_audit/serial_chain.log, 26 START/DONE timestamp pairs. Step-1 durations at identical
ticker-years range 1.32h (sw30sp50) to 4.04h (sw50sp20), median 1.68h - so runtime is NOT
purely ticker-year-driven and a median-scaled figure is wrong for a SELECTED slate. Scaling
each config by ITS OWN base at 544x4y over 200x1y = 10.88x:

| config | step-1 | step-2 projected | 5h legs |
|---|---|---|---|
| sw50sp50 | 1.71h | **18.7h** | 4 |
| sw30sp150 | 1.59h | **17.3h** | 4 |
| sw50sp20 | 4.04h | **43.9h** | 9 |
| **top-3 serial** | | **~80h (3.3 days)** | |
| top-2, dropping sw50sp20 | | ~36h (1.5 days) | |

**The median-based figure said ~55h and understated by ~25h**, because the third-ranked
config is also the SLOWEST of the 26 - selection on `is_ci_lo` is not independent of runtime.
Same shape as L708: a statistic computed over a population and applied to a selected subset.
**Still an ESTIMATE** - linearity in ticker-years is assumed, and the 1.32-4.04h spread at
constant ticker-years is direct evidence that assumption is imperfect. The first cube settles it.

Applied to the completed b2197 program this yields, in order: **sw50sp50 (+1.250), sw30sp150
(+1.214), sw50sp20 (+0.930)** - the top 3 that advance. The next two under the old
5-slate rule were sw30sp20 (+0.816, first holder of the triplicate signature; sw30sp50 and
sw30sp100 collapse into it) and sw50sp9 (+0.724); both are recorded here so a later
widening does not have to re-derive them.

### B.5 Waterfall instance and cost profile (old STEP 2 EXECUTION)

*Source lines 972-974, 984-987, verbatim.*

**SMC INSTANCE (the campaign this was ruled on, DATED - not the procedure):**
`<C1>`=sw50sp50, `<C2>`=sw30sp150, `<C3>`=sw50sp20, `<K>`=300,
`<STRATEGY>`=`smc_breaker_block_long`.

**COST PROFILE.** Best case 18.7h (config 1 qualifies). Then 36.0h. Worst case 80.0h (all three run
and none qualifies). The waterfall is therefore **never more expensive than the flat top-3 slate and
usually cheaper** - and the rank order happens to be cost-favourable, because the 43.9h config sorts
LAST, so it is only paid for if the two cheap ones both fail.

### B.6 Decisions ruled - all six, and the 2026-08-30 rulings, verbatim

*Source lines 1000-1079, verbatim.*

#### DECISIONS RULED - ALL SIX (owner, 2026-08-29, S6-B2375)

**D1 - RULED: ROBUST. [SUPERSEDED 2026-08-30, S6-B2409 - preserved as history.]** *"D1 robust that
said the config runs to be run in its entirety."* Two things: the stop condition was **ROBUST, not
bare PASS** - a qualifier whose holdout-Sharpe margin was below the 0.333 selection-noise floor was
PROVISIONAL and did **not** stop the waterfall; and **a config always runs to completion** - all
300 combinations are graded before the stop test, so the waterfall never halts mid-config.
**The 2026-08-30 ruling retired the ROBUST half in its entirety** (*"noise floor is 0.333 meaning
that the result has to be more than 1.333 in the holdout period to qualify. Remove the 0.333
selection-noise floor requirement in its entirety"*): the stop condition is now bare PASS over the
six gates. The run-to-completion half of D1 STANDS. Note for the record (L633, disagreement stated
once): D2's no-BH-FDR ruling was recorded as partly weighing on the D1 ROBUST hurdle; with that
hurdle retired, `psr >= 0.95` is the remaining significance-style control on a qualifier.

> **CONSEQUENCE RESOLVED BY THE SAME RULING.** The flagged case - a program terminating NEGATIVE
> while holding a gate-clearing cell - can no longer occur: a gate-clearing cell now stops the
> waterfall itself. Config 1's qualifier (retained by ruling 2 of 2026-08-30, S6-B2410) closes the
> question S6-B2407 raised.

#### DECISIONS RULED 2026-08-30 (S6-B2409 / S6-B2410) - the floor retired; the qualifier retained

**RULING 1 (S6-B2409), owner verbatim:** *"noise floor is 0.333 meaning that the result has to be
more than 1.333 in the holdout period to qualify. Remove the 0.333 selection-noise floor
requirement in its entirety."* Implemented same day: `roster_core.robust_status` ->
`qualifier_margin` (margin as a plain number, no floor, no label); `SELECTION_NOISE_FLOOR` deleted
from the roster builder; the grid payload's `provisional_qualifiers` key -> `qualifiers` (every
PASS row); the postconfig renderers no longer frame any value against a floor; pins rewritten
(test_b2409_*). My prior recommendation of the floor as the grid-stage selection-noise control is
recorded as overruled (L633 - stated once, ruling governs).

**RULING 2 (S6-B2410), owner verbatim:** *"Lets retain the break_pct_max 0.02, close_mitigation
True, age_bars_max None, exit time_stop_10d, tail_n (20) combination."* That is config 1
(sw50sp50)'s qualifying parameter set at its tail_n=20 member - `smc_breaker_block_long`, P1
swing_length=50, P6 span=50, close_mitigation=True, break_pct_max=0.02, age_bars_max=None,
tail_n=20, exit `time_stop_10d`; holdout sharpe 1.152, profit factor 1.937, sortino 1.925, psr
1.0, holdout_n 41, full_period_n 180 (S6-B2399 grid). The three passers were ONE parameter set
differing only in tail_n {10, 20, 2}; the owner's pick resolves that tie explicitly (#165 - no
criterion of mine).

**CONSEQUENCE UNDER THE AMENDED WATERFALL:** config 1 holds a qualifier, so **the stop condition
is MET - configs 2 and 3 are not run** and `smc_breaker_block_long` closes POSITIVE for Step 2.
S6-B2407 (the PROVISIONAL-worth question) closes as mooted. Engine implementation of the retained
combination (battery judgment step 7_implement_in_engine) is ticketed S6-B2411 - the retention
ruling approves the parameter set; the wiring is follow-on work, not auto-executed.

**ROSTER-DOCUMENT ADMISSION (S6-B2413, owner instruction 2026-08-30).** The retained combination
is rendered in PHASE_1B_ROSTER.md under *Step-2 admissions (owner-ruled)* - identity from
`output_audit/phase_1b_step2_admissions.json`, metrics re-derived at render time from the b2399
grid artifact by exact combination+exit match (never hand-copied), refuse-loud when the evidence
row cannot be located or did not PASS. This closes S6-B2411's roster-integration part; its engine
wiring and battery judgment steps remain open.

**D2 - RULED: no BH-FDR.** *"this doesn't apply. Apply config runs we will analyze the 300
combinations and select the one that passes all gates. If its multiple combinations, we select the
one with the best sharpe. No bh fdr needed here."* No multiplicity correction is applied across a
config's 300 combinations. **My recommendation was the opposite and is recorded as overruled** (L633:
the disagreement is stated once, then the ruling governs). **Two things weigh in the ruling's
favour and are worth recording**, since they were not part of my original framing: the D1 ROBUST
requirement is itself a substantial hurdle beyond bare gate-clearing, and `psr >= 0.95` is already a
significance-style gate on the Sharpe estimate - so the procedure is not uncontrolled, it simply
controls selection by MARGIN rather than by family-wise error rate.

**D3 - RULED: best Sharpe.** Where several combinations qualify, **the highest Sharpe advances**.
This supersedes the production-closest convention I recommended. *Reading made explicit:* "Sharpe"
here is the **holdout pooled Sharpe** - the gated quantity at `roster_core.py` `pooled_sharpe`, not
the in-sample `is_sharpe` Step 1 ranked on. **Note this is coherent with D1 rather than in tension
with it:** ROBUST is defined BY the Sharpe margin, so the best-Sharpe qualifier is also the one most
likely to be ROBUST.

**D4 - RULED: confirmed.** The waterfall supersedes the ranked-list goal recorded at S6-B2242. Under
it, a config-1 stop means configs 2 and 3 are never measured and **no cross-config ranking will
exist**. Accepted.

**D5 - RULED: approved.** Order stays the mechanical rank order - sw50sp50, sw30sp150, sw50sp20 -
which is also cost-favourable, since the 43.9h config sorts last and is paid for only if both cheap
ones fail.

**D6 - RULED: closes this strategy.** If all three fail, `smc_breaker_block_long` closes NEGATIVE and
the program moves to the next of the 207-strategy optimisation backlog. **The METHOD is not on
trial** - the negative result is evidence about this strategy.

### B.7 Step-2 pre-triage - the worked example (old STEP 2 PRE-TRIAGE)

*Source lines 1082-1127, verbatim.*

#### STEP 2 PRE-TRIAGE - EXECUTED, AND THE METHOD CHANGED (S6-B2369)

**MANDATORY before any Step-2 cube, PER CAMPAIGN (B3089).** It is not a
one-time step: it projects THIS family's Step-1 `full_period_n` past THIS
campaign's trade floors, so a run recorded for one strategy says nothing about
another. The smc record below is the WORKED EXAMPLE and the method; every new
family runs its own and records the result beside it. **The text previously
read "It has now been RUN, and the answer is recorded here", which for any
reader outside the smc campaign asserted a mandatory gate had already passed.**

**THE METHOD CHANGED, and this supersedes the `measure_fire_count.py` step approved earlier the same
day.** That tool sweeps only 2 of the 6 config axes and counts ENTRY FIRES, an upper bound. The
Step-1 grids already on disk carry `full_period_n` **per combination, for the exit each combination
actually selected, across all 6 axes** - a strictly better instrument requiring no engine run. Two
findings made this possible and are worth recording:

- **Every Step-1 `holdout_n` is EXACTLY 0 - all 5,354 gradable rows across all 26 grids.** Step 1
  runs `2024-05-05 -> 2025-05-05`, ending exactly at `HO_START`, so `roster_core.holdout()` returns an
  empty frame BY CONSTRUCTION. **Therefore `PASS: 0, FAIL: 0` across all 7,800 Step-1 combinations is
  a STRUCTURAL fact about the window, not a quality verdict** - the gate branch has never executed in
  this program, and no Step-1 artifact says anything about whether a combination can clear a gate.
- `full_period_n` IS populated at Step 1 (over its 200 ticker-years), so it projects.

**THE PROJECTION.** Step-1 scope 200 ticker-years; Step-2 full period 544 x 4 = 2,176 (**10.88x**) and
Step-2 holdout 544 x 1 = 544 (**2.72x**). A combination needs Step-1 `full_period_n` > 6.9 for the
75 bar and > 5.5 for the 15 bar, so **the full-period bar binds**.

| config | gradable of 300 | worst `full_period_n` | projects to full / holdout | clear BOTH floors |
|---|---|---|---|---|
| sw50sp50 | 100 | 10 | 109 / 27 | **100 of 100** |
| sw30sp150 | 194 | 11 | 120 / 30 | **194 of 194** |
| sw50sp20 | 100 | 10 | 109 / 27 | **100 of 100** |

**RESULT: 394 of 394 gradable combinations across all three configs project past both trade floors,
the WORST by a 45% margin.** The pre-triage excludes nothing. **Its real value is the inversion it
delivers: the trade floors will NOT be what stops these configs - the four STATISTICAL gates
(pooled_sharpe, profit_factor, sortino, psr) will decide, one way or the other.** This contradicts
the earlier expectation, recorded here so it is not repeated, that the thin-n leaders were the ones at
risk of failing the trade floors.

**LIMITATION, stated so the projection is not over-read:** it assumes the measured 2024-25 fire rate
holds across 2022-2026. **No Step-1 config ran a single day of 2022-23** - that era was excluded until
this same day's ruling admitted it - so the rate in the added two years is UNMEASURED, and 2022 in
particular was a distinct regime. If the rate there is materially lower the projection falls; the
worst margin is 45%, so the rate would have to be roughly a third of the 2024-25 rate in the added
years before the floor binds.

### B.8 Step 3 validate - the three configs (old STEP 3)

*Source lines 1656-1669, verbatim.*

**THE THREE CONFIGS - SMC INSTANCE (B3089: this is a dated result, not the
procedure).** Derived by the mechanical rule in STEP 2 ENTRY over 26 of 26 smc
Step-1 grids on `step1_ranking[0].is_ci_lo`. Any other family re-derives its own
slate by the same rule; see THE CANDLE INSTANCE below for a second worked
derivation.

| order | config | is_ci_lo | is_sharpe | fires | exit chosen |
|---|---|---|---|---|---|
| 1 | **sw50sp50** | +1.250 | 4.301 | 14 | time_stop_10d |
| 2 | **sw30sp150** | +1.214 | 4.807 | 11 | time_stop_10d |
| 3 | **sw50sp20** | +0.930 | 3.915 | 14 | time_stop_10d |

Recorded so a later widening need not re-derive them: sw30sp20 (+0.816, first holder of a
triplicate signature - sw30sp50 and sw30sp100 collapse into it) and sw50sp9 (+0.724).

### B.9 Step-2 launch instance b2399 - spec and runtime (old STEP 3.2 / 3.3)

*Source lines 1852-1854, 1868-1876, verbatim.*

**SMC INSTANCE (b2399, historical - smc_breaker_block is finalised):** wave b2399_step2_sw50sp50,
arm env SMC_SWING_LENGTH=50 and STRAT_EMA_SPAN=50 (backtest/config.py:2473 reads SMC_SWING_LENGTH).
It predates phase-table injection, so it typed tickers_file and window.

**SMC INSTANCE (b2399, historical):** two heartbeat readings four minutes apart, uncontended -
sim_day_index 6 -> 9 across elapsed_hours 0.2668 -> 0.3335, **3 sim-days in 4.00 minutes = 1.333
min/day at pool_workers 10**, 22.4 h for the window against a manifest projection of 18.7 h scaled
from Step 1, about 20 percent optimistic. **That first attempt was stopped on commit exhaustion**
(owner ruling, option b): PowerShell could not start (Windows 0x5AF, *The paging file is too small
for this operation to complete*), a plain file read raised MemoryError, and GlobalMemoryStatusEx
read **2.08 GB pagefile available at 93 percent load**, then 46.49 GB at 50 percent after the stop.
It relaunched at pool_workers 6, max_legs 10. Those readings were taken against a 63.63 GB commit
limit this box no longer has (47.63 GB after the 2026-09-23 restart).

### B.10 The battery on the first family - accepted asymmetry, spot-check scope, engine knobs (old MANDATORY POST-CONFIG ANALYSIS)

*Source lines 2453-2506, 2512-2532, 2540-2551, 2646-2673, verbatim.*

**ACCEPTED ASYMMETRY - RESTATED 2026-08-21 (owner ruling (b)).** The 2026-08-17 version of this
note said cfg1/cfg2 were degraded *"while the 18 remaining configs carry a live one"*. **That was
false, and the correction matters more than the acceptance.**

`exit_regime_flip` needs TWO inputs - `regime_by_date` and `regime_at_entry` - supplied in two
separate batches. MEASURED via `rc.measure_degraded_exits` on **all four existing cubes**:

```
output_cfg1              time_stop_20d == regime_flip     written Aug 15
output_cfg2              time_stop_20d == regime_flip     written Aug 15
output_w1_sw20_span21    time_stop_20d == regime_flip     written Aug 18 13:21
output_w1_sw20_span50    time_stop_20d == regime_flip     written Aug 18 13:21
```

**Wave 1 is degraded too**, because it ran hours BEFORE B1682 - whose own commit title reads
*"I fixed ONE OF THE TWO things the exit needed, and called it done"*. B1622 supplied the first
input; B1680 then found the fix had never run.

**OWNER RULING 2026-08-21: accept it.** Not re-running wave 1 (~5.8 h) or cfg1/cfg2 (~6.6 h).

**What this commits us to, stated so nobody re-derives it:**

- **All four existing cubes carry `regime_flip` as a 20-day time stop**, i.e. a duplicate of
  `time_stop_20d` under another name. Their effective exit family is **25, not 26**.
- **Every config run from now carries a LIVE `regime_flip`** - both inputs are in the code
  (`backtest.py:2650` sets the field, `:3106` passes it, `exit_strategies.py` injects both).
  **FALSIFIED AT FIRST MEASUREMENT 2026-08-22 (B2018, S6-B2018a P0).** The two first
  post-B1682 cubes (`output_b2016_e1_sw10`/`sw20`) STILL collapse `time_stop_20d ==
  regime_flip`: every regime_flip row exits via the cap branch (`regime_flip_max_days_20`),
  and `regime_changed_during_hold` is `'no'` on all 4,472 sw10 rows while 27 of 172 holds
  span one of the 6 in-window regime transitions. "Both inputs are in the code" was a
  code-presence claim; the runtime says the flip is never seen. Not fixed mid-E1 (frozen
  code keeps arms comparable; the collapse is identical in every arm).
  **FIXED 2026-08-23 (B2043, S6-B2018a)** after the drop-E1 ruling dissolved the hold: the map
  now rides in the pool task payload (the never-called setter and its orphan global are
  DELETED), the flip branch is pin-proven end-to-end through run_exit_comparison, detail rows
  record a real `exit_regime`, and exit_context no longer fabricates "no" for
  regime_changed_during_hold (absent reads "unknown"). Every pre-B2043 cube remains cap-only;
  cubes from now carry a LIVE flip branch - the comparability note above still governs.
- **Therefore `regime_flip` is NOT comparable between the four existing cubes and any later one.**
  Rankings are unaffected - no `regime_flip` appears in either wave-1 top-10 - so what is lost is
  comparability on that one exit, not the identity of the winners.
- **Never quote "best of 26" for these four.** `roster_core.measure_degraded_exits(cube)` MEASURES
  it from any cube, so this needs no date bookkeeping:

```bash
python -c "import sys;sys.path.insert(0,'.');import scripts.roster_core as rc,pathlib; \
  print(rc.measure_degraded_exits(rc.load_cube(pathlib.Path('output_cfg<N>/trade_exit_detail.csv'))))"
```

MEASURED 2026-08-17 on cfg2: **3 collapsed pairs**, not one -
`atr_trail_mae_conditional`==`atr_trail_1x`, `reverse_signal`==`atr_trail_mae_conditional`,
`time_stop_20d`==`regime_flip`. That independently reproduces the known **26 exits -> 23
effective** (L460). **Never quote "best of 26" without running this first.**

**SCOPE, verified against code (B1631):**

| leg | what it does | file |
|---|---|---|
| re-derivation | P1-P6 rebuilt from raw parquet under PIT, calling the vendored LIBRARY | `spot_check_trades.py:58` |
| **engine** | **`compute_smc_signals` called at the same bar with the config's own parameters** | **added B1631** |
| execution | entry is a real trading day, exit >= entry, `hold_days` matches the calendar distance, `pnl_pct` sign-consistent | `spot_check_trades.py:101` |

**OHLCV-only is CORRECT here, and not by luck.** `smc_breaker_block_long` has exactly two gates -
`smc_breaker_block_bullish` and `price_above_ema_{span}` - both OHLCV-derived, and under
`--cube-isolation` `backtest.py:2379-2380` sets `size_pct = CUBE_ISOLATION_SIZE_PCT`, bypassing
tier sizing. That matters because tier GATES ENTRY otherwise (LOW -> 0.0 size -> the trade is
SKIPPED, L418/B1544), which would make `smart_money_score` an unchecked entry input.
**At Phase 1B, with tier sizing live and the full roster running, OHLCV-only coverage is NOT
sufficient** - the smart-money leg re-enters the entry path and must be checked too.

**Two legs could only say THAT they disagreed.** Adding the engine makes it three-way, so a
disagreement localises: engine+cube agreeing against the re-derivation means the CHECKER is wrong
(L457); re-derivation+engine agreeing against the cube means the RUN is wrong.

**Expected: 100pct agreement on all three, 0 execution failures.** Anything less is a finding.

Step 4 is a STANDARD, not a check written for one strategy. OHLCV-only coverage is complete for
`smc_breaker_block_long` because it reads two price-derived signals - **a property of the STRATEGY,
not of the check.** The rest of the roster reads smart-money, news, earnings, short-interest,
index-event and filing signals, and an OHLCV-only re-derivation would certify those **without ever
reading the input that gates them**, producing output identical to a real verification.

MEASURED across the roster: **185 of 222 strategies have at least one input the spot check cannot
verify**; `smc_breaker_block_long` is in the 37 that pass, so THIS sweep is covered - proven, not
assumed. The gate is fail-CLOSED: an unclassified key counts as unverifiable, because an
unrecognised input is precisely the one nobody thought about.

**Before the spot check certifies any strategy, this must exit 0.**

**STATUS 2026-08-17 (B1617 re-verified): all 6 swept parameters REACH the engine.** When this
step was written, four did not - the history is kept because it is what the step exists to catch.

| | status | env knob |
|---|---|---|
| P1 `swing_length` | **IMPLEMENTED** | `SMC_SWING_LENGTH` |
| P2 `close_mitigation` | **IMPLEMENTED (B1616)** | `SMC_OB_CLOSE_MITIGATION` |
| P3 `tail_n` | **IMPLEMENTED (B1616)** | `SMC_OB_TAIL_N` |
| P4 `age_bars_max` | **IMPLEMENTED (B1616)** | `SMC_BREAKER_AGE_BARS_MAX` |
| P5 `break_pct_max` | **IMPLEMENTED (B1616)** | `SMC_BREAKER_BREAK_PCT_MAX` |
| P6 `ema span` | **IMPLEMENTED** | `STRAT_EMA_SPAN` |

*Until B1616 the last four existed ONLY in the offline grader. cfg2's graded winner - 68 fires at
Sharpe 2.239 - would have run live as 420 fires at Sharpe 0.789 with a different exit method,
because the engine applied neither cap. That is `regime_flip` (L461) moved from exits to entry
gates.*

**Because they are now real engine knobs, the remaining admission step is a REPRODUCTION CHECK
that was previously impossible:** re-run the config with the candidate's env knobs set, and confirm
the cube reproduces the graded fire set exactly. **Admission without it ships a backtest nobody has
executed.**

**BLAST RADIUS - set a knob and you move more than one strategy** (MEASURED B1617):
`SMC_OB_TAIL_N` and `SMC_OB_CLOSE_MITIGATION` reach **5** strategies (both breaker legs, both
mitigation-block legs, `strat_pre_rebalance_long`), `close_mitigation` also alters `ob_df` and so
`strat_smc_order_block_bounce`; the two breaker caps reach **2** (LONG and SHORT). Harmless while
the sweep runs ONE strategy under `--cube-isolation`; at Phase 1B, with the full roster in one run,
a knob tuned for the long leg would silently retune five other strategies. S6-B1617b.

### B.11 smc family campaign - pre-gate, wave-1 bands, hub-1 Step 1 (B2690-B2694)

*Source lines 3098-3169, verbatim.*

#### SMC FAMILY CAMPAIGN OPENED - PRE-GATE VERDICT: TWO HUBS + INDEPENDENTS (B2690, owner word 2026-09-11)

Owner word 'Lets start with smc family'. Pre-gate run on the 15 pending members
(breaker_block pair FINALISED and excluded; bos_retest_entry is a funnel qualifier,
roster row 6) - output_audit/b2690_smc_pregate.json, 105 pairs measured, 64 with shared
entries. STRUCTURE: NOT a uniform collapse - a HUB pattern:
- CLUSTER A, hub smc_liquidity_sweep_reversal (T, 2,933 trades / 570 holdout): CONTAINS
  bos_continuation 100pct, discount_long 86pct, premium_short 77pct, equal_highs_sweep
  64pct, ote_long 62pct, ote_short 54pct of those members' trades.
- CLUSTER B, hub smc_order_block_bounce (T, 1,340 / 352): contains mitigation_block
  short 82.5pct / long 80pct (5 and 40 trades - both sub-gate anyway); premium_short
  47pct, discount_long 45pct shared with it.
- QUASI-INDEPENDENT: inverse_fvg (M, 953/231), equal_lows_sweep_long (M, 382/113,
  ~zero overlap), choch_reversal (551/95), fvg_retest_long (61/17, best-exit HO 2.492 -
  thin), fvg_retest_short (288/60).
Best-vs-median exit holdout gaps are wide family-wide (selection inflation visible on
the artifact's face). CAMPAIGN PLAN (B2628 pattern, bands owner-reviewed before any
Step-1 per 11.2c): WAVE 1 = two hub campaigns - liquidity_sweep_reversal and
order_block_bounce, both T-band and offline-free per the B2677 census - each with the
11.2b2 two legs (depth knobs + companion breadth) and contained-sibling pre-registered
passes; WAVE 2 = inverse_fvg + equal_lows_sweep_long; the thin L-band members ride
their hubs' verdicts or wait for the next cube. NEXT: Step-0 knob inventory for the two
hubs, then the band proposal to the owner.

#### SMC WAVE-1 BAND PROPOSAL - AWAITING OWNER REVIEW (B2691, 11.2c gate)

Companion screen for the smc family run IS-only (6,128 entries, 650 signals, one
BH-FDR pass per exit): 100 ts10 + 255 bept survivors, 56 consistent under both
(b2691_smc_companions_{ts10,bept,consistent}.json). PROPOSED Step-1 bands, offline,
levels = retention quantiles 0.2/0.4/0.6/0.8 on each hub's OWN fires at grid time,
all exits with npt barred from selection, per-leg grading, null-perms priced:

HUB 1 smc_liquidity_sweep_reversal (T, 2,933/570) - DEPTH: confirmation-arm split
{either(prod) / choch-only / bos-only} x leg {long/short} (boolean subset-safe
splits; the gate is boolean-only so leg/arm splits ARE the depth axes). BREADTH (one
rep per survivor cluster): monthly_momentum_6m >=, bb_20_20_bandwidth <=,
vp_close_near_poc_pct <=, atr_pct <=, bullish_engulfing =True (long leg only,
thesis-aligned reversal candle), gap_up_2pct =False.

HUB 2 smc_order_block_bounce (T, 1,340/352) - DEPTH: rsi_14 threshold band long
{45(prod), 40, 35, 30} / short {55, 60, 65, 70} (persisted numeric, subset-safe
tightenings) x leg split. BREADTH: same axes minus the engulfing.

Wave-1 trials ~1,300 per hub; multiplicity priced per grid (the B2676 null pattern).
Contained-sibling pre-registered passes ride each hub verdict (B2628). NOTHING RUNS
until the owner's band word; Step-2 needs its own word.

#### SMC HUB-1 STEP-1 LANDED (B2694, owner band word 'Lets proceed with step 1')

scripts/smc_lsr_step1.py on the approved 11-row band: reproduction gate exact (2,933
fires = b2690), 598 graded IS cells, holdout untouched
(output_audit/b2694_smc_lsr_step1.json). READINGS: (1) THREE OF FOUR numeric breadth axes were swept (bb_bandwidth, vp_poc_pct,
atr_pct) and found nothing - best IS 0.284 vs their own 100-perm null q95 0.408,
p 0.2079; the FOURTH, monthly_momentum_6m (the screen's rank-1), was
COVERAGE-SKIPPED at 0.942 < 0.98 and is UNTESTED on this hub, not refuted
(B2696 correction - the artifact's SKIP row had been dropped from the summary).
B2698 (owner option (b) 2026-09-12) RE-SWEPT monthly_momentum_6m under a WIDENED
COVERAGE RULE (grade only the covered 94.2% of IS fires, 5.8% gap disclosed on the
artifact's face; the 0.98 floor stands elsewhere): best cell >=0.0871 (q80) @
breakeven_plus_trail IS 0.486 ci_lo 0.222 n 445/581, and the q40 line 0.475 ci_lo
0.327 n 1335/1710; single-axis permutation null q95 0.235, p 0.0099 - the ONE axis
that was untested is the ONE that clears its own null (the other three sat inside
theirs at p 0.2079). Verdict binds the covered subpopulation only; holdout NOT read
(output_audit/b2698_momentum_resweep.json + standard-form .md). (2) The LEADER is B5 -
bullish_engulfing on the LONG leg: IS 2.078 ci_lo 1.474 at class_time_stop, positive
ci_lo across ~9 exits (not single-exit fragile), n 111 IS / 129 full; DISCLOSURE: the
boolean axes sat outside the numeric null, a 2-candidate x exits search - stated, not
hidden. (3) DEPTH: long >> short everywhere (long/either 0.607 bept vs short negative);
choch_only cells are tiny (n 10-41 - the arm split mostly collapses to bos). POWER for
the candidate: full 129 >= 75, projected holdout ~18 >= 15 - both floors clear on
counts. PRE-REGISTRATION CANDIDATE: LONG leg + bullish_engulfing confirmation; Step-2
one read awaits the owner's word (S6-B2694a).

### B.12 Hub-1 depth - STEP 0 done and the producer reach (old §11.2b2b, §11.2s item 2)

*Source lines 3621-3642, 3971-3973, verbatim.*

STEP 0 DONE (B2706): all three hub-1 producer knobs are engine-reachable -
SMC_SWING_LENGTH (B1616), SMC_LIQUIDITY_RANGE_PCT + SMC_EVENT_RECENCY_BARS
(B2706, bite-proven on cached data, pinned test_b2706). The 44-config
factorial awaits Step 1: band spec + manifest + prelaunch gate + the venue
word (B2107 rules).

**SHARED-PRODUCER RESIM REUSE (B2707, owner philosophy verbatim 2026-09-12:
"we will do a resim and re use the data for shared producer fot offline
cube generation").** A producer-band resim is a FAMILY asset, never a
one-strategy expense: the P1-P3 knobs are GLOBAL, so one variant config
recomputes every smc_* signal, and every strategy whose gate reads them
fires against the variant in the same run. THEREFORE each variant config
MUST run with the FULL smc consumer set active (Step-1 spec enumerates the
consumers by grepping every gate expression for smc_* keys - no
strategy-subset pruning that drops a family member), persist
signals_at_entry as standard, and carry the variant identity in the cube
dir name + run_manifest (the icg wave pattern). Each landed variant cube
then serves later smc campaigns' depth legs OFFLINE **within its producer reach, which B2735 MEASURED rather than assumed: a SMC_SWING_LENGTH factorial reaches 19 of the 22 consumers (17 of 22 reachable AND open, the 2 breaker legs being admitted-closed), because `swing_highs_lows(swing_length)` feeds exactly four primitives - `ob`, `bos_choch`, `liquidity`, `retracements` (smc_ict.py:375/453/503/559). It reaches NEITHER of the swing-independent sources: `fvg` takes no swings (smc_ict.py:298) and dealing-range is a raw high/low window (smc_ict.py:583), so smc_fvg_retest_long, smc_fvg_retest_short and smc_inverse_fvg read only swing-independent keys and their depth needs its OWN axis (SMC_LIQUIDITY_RANGE_PCT feeds `liquidity`; the FVG parameters are a separate lever). Producer map: output_audit/b2735_smc_producer_map.json** - hub 2
(order_block_bounce) and the Wave-2 independents take their producer-band
depth from these 44 cubes with ZERO additional engine hours, the same way
offline campaigns filter R5 today. The band_coverage_gate accepts these
cubes as resim evidence via resim_configs / --resim-evidence.

2. **OPEN consumers only:** the subset excludes ADMITTED strategies (the launch gate
   refuses them - B2731, banked lines are closed) and every B2825 terminal status. The
   smc precedent: 19 of 22 consumers in reach, 17 reachable AND open.

### B.13 The factorial lineage behind the coordinate-descent interaction check (old §11.2b2d item 4)

*Source lines 3662-3668, verbatim.*

   **INTERACTION CHECK (B2823, owner-approved 2026-09-16 closing S6-B2822d):** after the
   CD passes converge, run ONE confirmation config at the predicted joint optimum IF that
   point differs from every already-run config - cost at most 1 extra run against the ~23
   a two-axis grid saves - and record predicted-vs-measured in the campaign row. A
   material gap re-opens the full-grid question FOR THAT FAMILY. Lineage: the programme's
   one resim success, the breaker's admitted sw50sp50 line, came from a FACTORIAL, and
   coordinate descent alone cannot see a joint optimum off its axes.

### B.14 B2701 - hub-1 Step 2, the one holdout read

*Source lines 4044-4072, verbatim.*

#### B2701 - smc hub-1 STEP-2: the one holdout read, CLEAN NEGATIVE (2026-09-12)

Owner word verbatim: "proceed, engulfing + momentum q40 both pre-registered"
(S6-B2694a). F4 honored: the two-cell pre-registration was COMMITTED
(output_audit/b2701_prereg.json, 301cded1a) before the reader existed. ONE
offline read graded the holdout six-gate line for every Step-1 cell x exit
(602 lines meeting the 15-trade holdout floor; the remainder sat below it).

VERDICT - NO ADMISSION, pre-registration SPENT:
- Cell A (bullish_engulfing long @ class_time_stop): IS 2.078 -> HOLDOUT
  -0.37 (ci_lo -1.722, n 18); 2 of 6 gates (both count legs only). The
  Step-1 leader did not survive its first out-of-sample contact.
- Cell B (monthly_momentum_6m >= -0.1122 q40, covered subpop @
  breakeven_plus_trail): HOLDOUT 0.331 (ci_lo -0.02, n 375); 5 of 6 gates -
  pf 1.566, sortino 1.744, psr 0.9952, both counts - failing ONLY
  pooled_sharpe (0.331 < 1.0). A real but sub-bar signature.
- 0 of 602 lines clear all six (best peeked 0.565) - the whole grid is
  below the bar out of sample, so nothing was lost by pre-registering.
- Controls (11.2b2): engulfing on pead control lift -0.393; momentum lift
  +0.038 - no general-structure story.

Campaign disposition - CORRECTED B2702 (owner-caught; the original line
here read CLOSED-NEGATIVE): the OFFLINE leg (8 of 11 Table A axes: arm,
leg, six breadth axes) is NEGATIVE out of sample; the DEPTH leg over the
producer bands (P1 swing_length, P2 liquidity_range_pct, P3
event_recency_bars - resim) was NOT RUN and is Priority 1 (S6-B2702a,
band + venue word pending). The strategy carries NO verdict until the
depth leg runs; production unchanged meanwhile. Artifacts: b2701_smc_lsr_step2.json + .md (Step-2 unified
form, full length).

### B.15 Hub-1's depth campaign blocked on registration (old §11.2b2c)

*Source lines 4074-4144, verbatim.*

#### 11.2b2c HUB-1's DEPTH CAMPAIGN IS BLOCKED ON REGISTRATION, AND THE FIRST ATTEMPT GRADED THE WRONG STRATEGY (B2731-B2737, owner-caught 2026-09-12)

**What was attempted and retracted.** The S6-B2702a depth factorial was
launched twice - b2709 (pilot) and b2712 (config 1) - and BOTH declared
`smc_breaker_block_long` as the graded strategy. That strategy is ADMITTED to
Phase 1B at S6-B2410 (holdout 1.152), so the runs re-searched a banked
decision while hub-1, the actual subject, rode along UNGRADED as one of 21
riders. MEASURED: config 1 spent 2.41 h (elapsed_s 8668,
b2712_smc_sw10_wave_summary.json results[0]) and left 305 hub-1 entries
unread in its cube. **Every number reported from b2712 is RETRACTED as
campaign evidence** - its Table C funnel row and Table D ranks 12/13 (is_ci_lo
+0.803 n 13, +0.766 n 12) describe the closed strategy. Owner ruling, verbatim:
*"We stop testing the strategies once they are in the phase 1B unless you get
specific over rides from me!!"*

**Why it could happen, stated as a REGISTRATION fact rather than an excuse.**
MEASURED at B2737: **1 of 22 smc consumers has a SPECS entry in
`producer_variant_table` and is a registered post-config battery family - and
it is `smc_breaker_block_long`, the admitted one.** `launch_refusals` refuses
any graded strategy with no SPECS entry (S6-B2573b: the battery would fail
closed at landing AFTER the engine spend), so hub-1 was NOT launchable, and
the only launchable smc strategy was the one that must not be re-tested. The
generic family adapter exists (S6-B2573a, `tools` block per SPECS entry); the
hub-1 INSTANCE was never registered.

**Two gates now close the class:**
- **B2731** - `phase1b_admitted()` + `_admitted_retest_refusals()`, wired into
  `launch_refusals`: an ADMITTED graded strategy is REFUSED AT LAUNCH. The
  escape is the owner's dated words in the spec under
  `owner_override_retest_admitted[<strategy>]`; a bare boolean is refused
  (L789). Verified retroactively against the real `b2712_smc_sw10_spec.json` -
  the refusal fires. Pin `test_b2731`, five arms. CHECKLIST #304 / L791.
- **B2733** - a HOLE in B2731 found one batch later: it read only
  `phase_1b_step2_admissions.json`, while PHASE_1B_ROSTER.md retains
  `smc_breaker_block_short` and `pead_short_negative_yoy_growth` as Step-2
  admissions that appear NOWHERE in that JSON. Both sources now unioned,
  fail-closed; admitted set 14 -> 16. Pin `test_b2733` guards its own premise.

**Blast radius, measured not assumed (B2734, #237 sweep over 70 of 70
manifests, classified per L643): 3 DEFECTS** - b2207a_lockprobe_p1, b2709
pilot, b2712 - all three `smc_breaker_block_long`. **59 ran in the correct
search-then-admit order, including 18 of 18 `icg_*` configs, so the
institutional campaign is CLEAN.** Also measured: only 2 of 70 cubes declare
`cube_riders`, which bounds the offline salvage to swing_length=10 and
retracts an overclaim quantified over all variant cubes.

**THEREFORE the ruled order for hub-1 (11.2b2b unchanged: DEPTH is Priority 1,
BREADTH Priority 2).** Hub-1's BREADTH leg is already SPENT - 8 of 11 Table A
axes ran offline and B2701's single holdout read was a clean negative (0 of 602
lines clear six gates). Its DEPTH leg over the producer bands (P1
swing_length, P2 liquidity_range_pct, P3 event_recency_bars) remains the ONLY
unrun mandatory leg, so the strategy still carries NO verdict (CHECKLIST #299
/ L785). The sequence, each step gated by 11.2c:

1. **REGISTER hub-1** - a SPECS entry with its Table A producer bands plus a
   `tools` adapter block, and registration as a post-config battery family.
   Without this the launch gate refuses, correctly. (S6-B2732a)
2. **BAND REVIEW** - the owner reviews hub-1's depth band (the three producer
   knobs and their levels) before anything runs.
3. **OFFLINE SALVAGE FIRST, ZERO ENGINE COST** - b2712's cube already carries
   305 hub-1 entries at swing_length=10, so config 1 of the depth band is
   gradable by re-pointing the graded subset at hub-1 and re-running the
   battery. This is the B2707 reuse doctrine paying for itself against the
   misaim.
4. **THE REMAINING ENGINE CONFIGS** - re-specced with hub-1 graded and the full
   smc consumer set as riders (B2707), at the ruled Step-1 shape (200 tickers x
   1 year ending at the IS/HO boundary, injected by `phase_table.resolve` and
   not typeable). Measured rate 2.41 h/config. Venue word required (B2107).
5. **G1 + G2 RIDE IT** - per B2735 the same cubes serve the depth legs of 17 of
   22 open consumers offline, which is why G1 and G2 are worked as one campaign
   rather than nineteen.

### B.16 The first worked boolean formula (old §6.1's example, moved B3096 after an audit found it in neither file)

*Source lines 372-410, verbatim.*

```
=============================== PRODUCER LAYER ===============================

P1  swings  =  swing_highs_lows( ohlc, swing_length = 20 )
                   -> a bar is a swing high if its high is the highest
                      across swing_length bars BEFORE and AFTER it
                   PARAMETER: swing_length = 20   (library default is 50)

P2  ob_df   =  ob( ohlc, swings, close_mitigation = False )
                   -> emits, per detected block:  OB (+1 bull / -1 bear),
                      Top, Bottom, MitigatedIndex
                   PARAMETER: close_mitigation = False
                      False -> a block counts as mitigated when the HIGH/LOW
                               pierces it
                      True  -> only when the CLOSE pierces it  (stricter)

P3  events  =  ob_df[ OB != 0 ].tail( 20 )
                   PARAMETER: tail N = 20     (hardcoded literal, not an argument)

P4  per event e:   e.is_mitigated = ( MitigatedIndex > 0 )
                                    AND ( MitigatedIndex < today_index )
                   -> no parameter; derived from P2's MitigatedIndex

P5  per event e:   e.broken_up    = ( close > e.Top )
                   -> no parameter; strict inequality, zero buffer

P6  ema_50_200 =  compute_ema_sma( df )      # pairs (9,21),(20,50),(50,200)
       price_above_ema_200  =  close > EMA(close, span = 200)
                   PARAMETER: span = 200, emitted only from the (50,200) pair

=============================== STRATEGY LAYER ===============================

breaker_bullish  =  AT LEAST ONE event e in P3 satisfies ALL of:
                        ( e.OB == -1 )          <- bearish block      [from P2]
                        AND ( e.is_mitigated )                        [from P4]
                        AND ( e.broken_up )                           [from P5]

fires            =  ( breaker_bullish )  AND  ( price_above_ema_200 ) [from P6]
```

---

## C. INSTITUTIONAL FAMILY (CLOSED)

### C.1 Current programme - institutional_committed_growth_long Step 1 (S6-B2481..B2499)

*Source lines 3245-3382, verbatim.*

#### CURRENT PROGRAMME — institutional_committed_growth_long STEP 1 (S6-B2481..B2499, 2026-09-01)

**Inventory** — `SPECS["institutional_committed_growth_long"]` in
`producer_variant_table.py`: 9 parameters P1-P9. P1-P3 NOT-SWEPT-BY-DESIGN (PIT
lag / share-class floor / gap tolerance — availability and hygiene, not edge
knobs). The per-level free/resim split corrected the factorial 31,500 → 700
(L726). **Ruled Step-1 design: 17 engine configs** — baseline + P4 {2,3,6,8} +
P5 {2,3,6,8} + P6 {1.0,1.25,1.5} + P9 spans {9,20,50,100,150} — **plus 4 FREE
cache-graded levels** (P7 {5,11,14}, P8 {6}) that need no engine run because both
counts persist in `signals_at_entry` — coverage is NOT 100 % (B2569 correction of
this line's own claim, L749 class): measured 96.2 % of fired rows carry the
committed key on R5 (S6-B2504) and 93.83 % on cfg1 (23 resume-restored rows empty,
S6-B2512; span9/span20/span50 measure 100 %). **The free levels are graded on
EVERY landing by the battery** (`step2_free_levels`, reproduction-gated, B2569) —
the one-time R5-cube grading at S6-B2504 was the N1 class bug, not the design.
P7 resim {1,2} and P8 resim {2,3} are recorded in the band and deliberately NOT
scheduled — **and are UNRUNNABLE as specced: the screener hardcodes both
thresholds (screener.py:6646-6648) and no env knob exists** (§0.7
band-completeness defect; owner decision S6-B2569a: strike, or build the knob and
schedule 4 configs at ~+10-12 h serial).
The P9 band excludes producer-offered span 21 (owner directive 2026-08-31; the
b2197 ledger measured it a near-duplicate of 20 that did not earn a run).

**Mechanism (S6-B2484)** — the persistence producer is parameterised via env
`INST_MIN_CONSECUTIVE_QUARTERS` / `INST_GROWTH_LOOKBACK_QUARTERS` /
`INST_GROWTH_MULTIPLE`, with variant artifacts written to tagged caches via
`INST_PERSIST_CACHE_TAG` through ONE shared helper (`persistence_cache_dir`)
imported by producer AND consumer so the two cannot drift. Untagged = the
production path the rest of the 13F family reads, byte-identical (defaults ARE
production; 60-ticker equivalence run recorded 0 mismatches, S6-B2484). The
`persistent_holders_4q`/`_8q` chains (other strategies' inputs) are deliberately
untouched.

**Offline pre-screen (S6-B2485, corrected S6-B2498)** — all 11 producer configs
materialised at a MEASURED 283 s/config (~52 min; the shipped 104.6 s claim was a
warm one-snapshot sample, understated 2.7×). The screen compares the PRIMARY and
FALLBACK partitions pairwise (both Jaccards; a duplicate verdict needs both high)
plus per-year fallback rate against that year's baseline, over the full artifact
AND the 200-ticker sweep universe. Artifact: `output_audit/b2485_prescreen.json`.
**Results:** `minq2`/`minq3` are NEAR-DUPLICATES of baseline on both partitions
(primary 0.940/0.964, fallback 0.906/0.929) — dropping them from the engine queue
saves ~3.4 h of ~29 h, an owner decision. `mult1.5`/`lookback2`/`minq8` nearly
TRIPLE the 2022 fallback rate (0.329/0.304/0.253 vs baseline 0.124) — the B1230
fallback-switch hazard MEASURED: those configs shift the strategy's early-year
identity toward the fallback arm. Fallback membership diverges MORE than primary
on all 11 baseline pairs, which is why the primary-only screen was corrected. The
screen CANNOT see which fallback members clear `institutional_increased >= 5` —
that column is not in the artifact; the residual stays with the engine.

**Status (B2531, 2026-09-02) — cfg1 LANDED and configs 2-17 are RUNNING.**
VERIFIED against primaries, not against this document: `output_icg_cfg1/
engine_state.json` reads `status: complete`, `trade_log.parquet` holds 373
trades, and all nine post-config ledger steps are terminal ({DONE, N/A}, gate
`verify_postconfig_complete.py` COMPLETE). Best of 24 exits ranked
`breakeven_plus_trail` at is_sharpe 0.263 / is_ci_lo -0.087 on 8,952 IS rows —
Step-1 is ranking only, no admission (B1608). One open finding: 23 of 373 rows
carry an empty `signals_at_entry`, RCA CLOSED at S6-B2512 (they are exactly the
closed trades restored at `resume_sim_day=47`; historical, unrecoverable, and
they gate nothing).

**BOTH OWNER RULINGS ARE RESOLVED — the text below this paragraph said they were
pending, and that staleness nearly produced a wrong call.** S6-B2491 is
IMPLEMENTED in `backtest/engine/backtest.py::kill_decision`: the cap gates on
ACTIVE hours — wall-clock minus CREDITED machine sleep, where only gaps of
30 minutes or more earn credit — and BOTH gating sites (the supervisor thread
and the in-loop cap) call that one function. The fail direction is conservative:
with no credit accrued it reduces exactly to the old wall-clock kill. There is
no wall-clock backstop, deliberately: a 3x backstop was designed and then killed
by its own boundary matrix, because any overnight sleep exceeds 3x a sane cap
and it would have killed the very incident it was meant to survive (L734).
S6-B2481 (resume go) was given and the resume landed. Reading the superseded
text, an overnight chain looks unlaunchable; the code had already closed it
(L664 — a secondary record preserving a state the primary has moved past).

**THE TWO HOUR FIGURES ARE DIFFERENT THINGS, and this section previously used
only one of them.** **5 h is the CEILING** — the owner's hard cap (B2107, raised
from 3 h on 2026-08-24), which no local run may exceed. **4.0 h is the value
actually ENFORCED** — `leg_cap_hours` in every spec, passed to the engine as
`--max-run-hours` (`run_wave.py:173`). cfg1 used 4.0 and all 16 B2527 specs use
4.0. So the engine kills a leg at 4.0 h of ACTIVE time; 5 h is the bound that
choice has to respect.

**Launch path for configs 2-17 — EXECUTED 2026-09-02 (B2527/B2529), chain RUNNING.**
The owner's go was given in the launch turn; 16 specs (`output_audit/
b2527_icg_*_spec.json`) run serially under one detached Task Scheduler task via
`run_serial_chain.py`, ordered by expected information so an early halt loses
least: the 5 unmeasured P9 spans, then the 3 producer configs the S6-B2485
pre-screen measured as most divergent, then the unranked middle, then
`minq3`/`minq2`, which that same pre-screen measured as near-duplicates of
baseline. Pre-launch gates all executed: `prelaunch_gate.py` exit 0 (it failed
exit 3 first, on field names — which is why it is run and not assumed), tickers
sha256-pinned at 200, subset asserted SOLO and confirmed at runtime by
`[B1425 STRATEGY_SUBSET_FILE] requested 1, matched 1/219`, and all 11 tagged
precomputes asserted present because a missing cache falls back to the untagged
production artifact and would run a silent duplicate of the baseline. Projection
38-47 h serial from cfg1's measured rate. Two defects were caught before they
cost a night: the detached task's `ExecutionTimeLimit` was 12 h against a 38-47 h
chain (B2528), and `launch_detached` reported success on a DENIED registration
(S6-B2529a, still open). The original note follows.

**Launch path for configs 2-17 (original)** — no new code: `run_wave.py` arms already carry
per-arm env (run_wave.py:190-202), so a wave spec whose arms set
`INST_PERSIST_CACHE_TAG=<tag>` (producer configs) or `STRAT_EMA_SPAN=<span>`
(P9 configs) launches the set under the existing chain, monitor and post-config
battery. The spec + manifest are written at launch time per §1.0-§1.3; launch
requires the owner's explicit go in the launch turn.

**Couplings and cautions** — TWO couplings, one per knob class, and both make
every config in this programme SOLO-SUBSET-ONLY. (1) env knob: `STRAT_EMA_SPAN`
is read by smc_breaker_block_long / _short AND this strategy
(screener.py:4407/4442/6656) — never set it on a multi-strategy run. (2)
artifact tag (S6-B2499b, found auditing consumers): `INST_PERSIST_CACHE_TAG`
re-routes the WHOLE persistence artifact for the engine process, and
`committed_growth_holders` is ALSO consumed by `strat_simple_below_ema_50_short`
(screener.py:6144, the B1422 selectivity gate) — so a tagged producer-config run
with more than the target strategy in its subset silently alters that
strategy's gate input too. `strat_institutional_multi_quarter_persistence_long`
(screener.py:6611) reads `persistent_holders_4q`, which this sweep measurably
does not move. Table D's `sw`/`sp` and all D-2 axes are smc-spec keys (see
§6.4b caveat, S6-B2500).

**Free-level status (B2569 — supersedes the "cheapest next action" line that stood
here, which pointed at S6-B2501 work EXECUTED 2026-09-01 and then superseded by the
per-config directive).** The battery now grades the P7/P8 free levels on every
landing (`step2_free_levels`), gated on reproducing the landed baseline at
production levels first. Executed retroactively on all 4 landed cubes — every one
reproduces (span9 609/609, span20 531/531, span50 405/405, cfg1 350/350 covered
with the 23 S6-B2512 rows counted and excluded) — and the verdict with its
denominators is: **0 of 4 free levels beat baseline on ANY landed config (0 of 16
level×config cells); every P7 tightening costs 31-79 % of fires and drops top
ci_lo; p8_6 is a 4-6-trade no-op.** Artifacts:
`output_audit/output_icg_*_free_levels.json`; audit `output_audit/b2569_icg_programme_audit.md`.

**Step-1 leaderboard after 4 of 17 landings (ranking only, no admission — B1608):**
span9 `regime_flip` is_ci_lo **+0.167** / is_sharpe 0.489 / 609 fires; span20
`breakeven_plus_trail` −0.015 / 0.300 / 531; span50 `breakeven_plus_trail` −0.067 /
0.288 / 405; cfg1 (baseline, span200) `breakeven_plus_trail` −0.087 / 0.263 / 373.
The span axis is measuring as the live one; span100/span150 land next in the chain.

### C.2 Companion screen, companion-axis result, 13F depth, admission doctrine applied, full grid, composite variant test (B2657-B2674)

*Source lines 2873-2966, 2981-2998, verbatim.*

#### COMPANION-SIGNAL SCREEN - institutional family (B2657, owner green-light 2026-09-09)

**The owner's challenge:** the 20-strategy institutional family failed on low sharpe, yet
institutional direction should indicate momentum - so what separates its WINNING trades from its
losers? **Instrument:** `scripts/institutional_companion_screen.py` - 3,719 unique IS entries
(29,411 fires deduplicated across the collinear family), 595 persisted signals tested against
per-trade pnl at TWO fixed exits (time_stop_10d + breakeven_plus_trail; no exit selection), one
BH-FDR at q=0.05 per run, and only SAME-SIGN survivors under both exits kept: **29 of 595**.
Artifacts: output_audit/b2657_inst_companions_{ts10,bept,consistent}.json. A SCREEN, not a gate.

**THE PATTERN (top consistent discriminators):** price-momentum confirmation. pct_from_avwap_20low
tops the list (Q5-Q1 spread +40.8 pnl points at ts10, +43.9 at bept; Q5 mean +40.97 vs Q1 +0.21 on
n 3,464) with pct_from_avwap_50low, xs_max_anomaly, roc_12, pct_change_10d, rsi_9, ppo_hist and
bb pctb behind it - institutional fires on an ALREADY-CONFIRMED tape win; institutional
accumulation against a flat tape is the family's noise. Macro overlays survive too
(cot_copper_commercials rho +0.15-0.18, cot_ndx/dxy pctiles, gold_silver), and sector_strongest_rs
is NEGATIVE (-34 to -37: the most-crowded sector underperforms). Notably: no raw VOLUME metric
survived both-exit FDR - the tape confirmation that matters is PRICE, not volume.

**Why this is immediately actionable at zero engine hours:** the top discriminators are PERSISTED
MAGNITUDES, so a companion-confirmation axis (e.g. pct_from_avwap_20low >= t) is a TIGHTENING and
sweeps offline through `offline_level_sweep.py` on any institutional strategy's existing fires -
the S6-B2657a campaign. The 13F DEPTH producers (fund segregation / conviction size / breadth /
skilled-subset - S6-B2656's directions) are separately buildable from the cached vendor data:
sec13f + sec13fchanges schemas VERIFIED (Fund, Ticker, ReportPeriod, filing Date for PIT, Value,
Shares, Change, Change_Pct, Held) - S6-B2657b.
#### COMPANION-AXIS CAMPAIGN RESULT - the control REFUTES the institutional reading (B2658)

**S6-B2657a executed with the pre-declared control, and the control decided it.** The roc_12
companion axis swept offline on the institutional representative vs the pead control (same
levels {-999 sentinel, -6.5, -2.2, 0, 2.14, 6.99}, IS-only, artifacts
output_audit/b2658_{icg_companion,pead_control}_step1.json):

| roc_12 >= | icg IS sharpe (lift) | control IS sharpe (lift) |
|---|---|---|
| none | 0.537 | 0.748 |
| 2.14 | 0.614 (+0.077) | 1.458 (+0.710) |
| 6.99 | 0.658 (+0.121), n 235 | 1.620 (+0.872), n 141 |

**Verdict with denominators: the tape-confirmation lift is a GENERAL momentum effect, 6x
stronger on the event-driven control than on the institutional representative (+0.710 vs +0.121
at the 2.14 level) - the B2657 screen's discriminators were measured across the pooled family
(3,719 entries) where cross-sectional spread dominates, and do NOT rescue icg within-strategy.**
NO forward pre-registration is written for icg on this evidence: its best filtered cell (IS
0.658) sits far under the 1.0 gate before any holdout decay. The pead lift is noted as context
only - that family is CLOSED and admitted; its drift-tightening already banks the momentum-
adjacent effect. The remaining live path for the owner's institutional conviction is the 13F
DEPTH producers (S6-B2657b): fund skill/type/size from data_prefetch/quiver/institutional
(1,942 per-ticker files, panel spans 2015-03-31..2025-12-31 measured on MSFT - the bulk
sec13f/sec13fchanges globals are single-snapshot 500k-row caps and are NOT the historical
source).
#### 13F DEPTH PRECOMPUTE BUILT - forward-usable, with a measured density caveat (B2659)

**S6-B2657b delivered.** `scripts/build_13f_depth_precompute.py` streams the 1,941 per-ticker
fund-level files (89 empty, reconciling the b2635 census exactly) into two derived tables under
data_prefetch/derived/inst_depth_13f: depth_by_ticker_quarter (60,627 rows - held/init/exit/
add/reduce counts, breadth_delta, init value sums, small-filer vs mega-filer segregation at
<100 / >500 positions, availability_q90 PIT stamp) and fund_scale (117,729 fund-quarters).
VERIFIED at build: breadth identity 0 violations of 58,775; PIT impossibilities 0 of 60,627;
one raw recount exact (44 = 44).

**THE HONEST LIMIT, measured:** panel density ramps 344,688 -> 967,066 funds-held across the
last 10 quarters (2.8x), so n_init / n_exit conflate real initiations with coverage growth -
HISTORICAL breadth flows are not backtestable from this panel as-is. Density-robust columns:
n_add / n_reduce (intersection-based). Depth GATES therefore ride the FORWARD window (the same
posture as the b2652-class preregistrations), and a full historical 13F snapshot feed is the
data-acquisition decision S6-B2659a puts to the owner.
#### ADMISSION DOCTRINE RULED + the icg companion holdout read (B2660, owner 2026-09-10)

**OWNER RULING (supersedes the forward-window conditionality):** *"As long as the strategy
works well in the holdout period and clears all gates it is good enough to go to phase 1b."*
A cell clearing all six live gates on the holdout IS admissible regardless of prior reads or
selection provenance; provenance labels (peeked etc.) stay on rows as information, and forward
registrations become ADDITIONAL evidence, never a strike condition. The selection-inflation
risk was flagged and stands on record; the ruling is the owner's.

**Applied immediately:** the icg roc_12 companion cells were graded on the holdout
(output_audit/b2660_icg_companion_step2.json): **0 of 156 (cell, exit) lines clear all six
gates** - best cell (roc>=6.99, ma_exit_ema9) holdout sharpe 0.485, 4 of 6. S6-B2657a is
CLOSED FAIL under the owner's own standard as well.
#### THE FULL INSTITUTIONAL GRID - 299 all-six-gate holdout qualifiers across 17 of 20 (B2662)

**Owner-directed breadth (after catching the narrow B2658 execution):** all 20 institutional
strategies x 7 axes (ask-1 knobs institutional_new_positions / institutional_increased - both
PERSISTED numerics - plus ask-2 companions xs_max_anomaly, roc_12, cot_copper_commercials,
sector_strongest_rs as an avoid-gate, pct_from_avwap_20low) x retention levels x 26 exits =
**13,104 trials, 11,544 above the power floor, 299 clearing ALL SIX holdout gates, spread over
17 of 20 strategies** (scripts/institutional_companion_grid.py; output_audit/b2662_inst_grid).
Axis mix among qualifiers: xs_max_anomaly 153, sector-avoid 61, copper commercials 37,
new_positions 32, roc_12 7, avwap 5, increased 4. Top lines: HO sharpe 3.132 (breakout_
confirmation + xs_max_anomaly, n 34/128), 2.877, 2.723. Under the B2660 admission doctrine
every qualifier is admissible; the 13,104-trial max-selection risk is DISCLOSED on the artifact
and stands flagged. OWNER SCOPE DECISION (S6-B2662a): admit what - all, top-1 per strategy, or
review-first; and gate-wiring (NEW-GATE class) needs per-strategy approval regardless.

#### COMPOSITE VARIANT TEST - the upgrade thesis fails on this data (B2674, owner-ruled)

S6-B2654 executed per the owner's 'Test composite upgrades' ruling (2026-09-10):
scripts/composite_variant_test.py graded the 3 tightened _has_smart_money_buy variants
across the 7 hard-gate consumers (8 call sites minus the B1195 annotation-only one) x
all exits = 728 lines, IS + all-six holdout gates, faithfulness gate on baseline
reconstruction (output_audit/b2674_composite_variant_test.json). VERDICT, denominators
on their face: v1(drop institutional_buy) = v2(strong-replaces-buy) SET-IDENTICAL on 7
of 7 (measured, not assumed); v3(drop cfo) is a NO-OP on 7 of 7 (identical n and
metrics - the cfo leg admits zero unique fires anywhere, generalising the peadsm 4-of-4
overlap); v1 removes 8-17pct of fires and makes the two already-passing cells slightly
WEAKER (mfi 1.267 -> 1.127; xs_low_beta 1.510 -> 1.480 holdout at ts10). 0 of 7
consumers improve their six-gate outcome under any variant -> the composite stays AS-IS,
now on evidence rather than caution; ceo/director loosenings remain next-cube.
SIDE-FINDING: xs_low_beta_with_smart_money_long BASELINE clears all six non-npt gates
(ts10 HO 1.510 psr 0.995 PF 2.286 n 73/452; also r_multiple_2r 1.296) and sits in
NEITHER the roster nor the admissions - candidate ticketed S6-B2674a for the owner
(IS -0.198: the IS/holdout inversion travels as a provenance label).

### C.3 Two-legs lineage (old §11.2b2)

*Source lines 3584-3589, verbatim.*

Lineage: the institutional family got both legs only after an owner catch (B2658 narrow
-> B2662 full grid); top_decile then ran depth-only (B2667: 3 own-knob axes, zero
companion axes - output_audit/b2667_topdecile_step1.json) because the rectification was
recorded family-locally. A campaign spec queued BEFORE a template change is re-checked
against the template AT EXECUTION. Both legs stay inside the standing approval flow
(11.2c): bands reviewed before Step 1, one owner-worded Step-2 read, admissions ruled.

---

## D. PEAD FAMILY (CLOSED)

### D.1 Campaign - pead_long_high_yoy_growth_only, Step 1 offline through family closed (B2633-B2651)

*Source lines 2748-2871, verbatim.*

#### CURRENT CAMPAIGN - pead family / pead_long_high_yoy_growth_only (B2633, owner go 2026-09-07)

**Pre-gate EXECUTED first (scripts/family_pregate.py, artifact
output_audit/b2633_pead_pregate.json) - and it SPLITS the family, the first live proof the
instrument earns its place:**
- **LONG cluster (the campaign):** representative `pead_long_high_yoy_growth_only` (2,116 R5
  trades, T-band, best-exit holdout 0.844 vs MEDIAN-exit 0.228 - the large selection lift is
  stated up front per the B2631 objection); `pead_long` (138 trades, 87% contained in the
  representative, holdout n=4 ungradable) and `pead_with_smart_money_long` (656 trades, 88%
  contained) close by pre-registered sibling pass after the representative's verdict, the B2628
  pattern.
- **SHORT cluster (NOT campaigned on this evidence):** `pead_short` + `pead_short_negative_yoy_growth`
  - 87% mutually overlapping, ZERO overlap with the longs, and NEGATIVE holdout everywhere
  (best -0.237/-0.390, medians -1.4 to -1.6). They ride the mirror policy; no engine hours.
- `pead_with_insider_confirmation_long`: no rows in the R5 cube (no-cell bucket) - nothing to
  measure offline; falls to the loosening programme.

**Phase 0 - DONE at B2634, and Step 1 DONE at B2638 (see the STEP-1 LANDED OFFLINE section below, which supersedes the 'next' framing in this paragraph).** Producer surface
read so far: backtest/signals/pead.py (`compute_pead_signals`, drift_window_days=60) and
backtest/signals/earnings_surprise_yoy.py (YOY_GROWTH_LONG_THRESHOLD +0.05 /
SHORT -0.05); gates `within_pead_window AND yoy_surprise_high` (screener.py:5041). The
inventory MUST prove each parameter reaches the engine (SS11.2 gate 2 - the S6-B2569a
unrunnable-level class: a threshold hardcoded at the producer with no env knob cannot be swept
as specced) and enumerate the transitive closure down to the earnings data source. No engine
launch before the SPECS entry, Table A, and the ruled Step-1 design exist - and none without
the owner's launch word.

#### STEP-1 LANDED OFFLINE - pead_long_high_yoy_growth_only (B2638, council 2026-09-07)

**THE CAMPAIGN NEEDS ZERO ENGINE HOURS, and that is now MEASURED, not assumed.** Every
magnitude the two live gates threshold was persisted at fire time: coverage 2,116 of 2,116
fires = 1.000, and re-applying the PRODUCTION levels returns 2,116 of 2,116 landed fires
= 1.0000. So a tighter level is a SUBSET of the landed fire set, and Step-1 is a filter,
not a simulation. Instrument: `scripts/offline_level_sweep.py` (generic - the axis map is
an argument, pead is its first caller, per the owner's run-producers-once directive).
Artifact: `output_audit/b2638_pead_step1_is_surface.json`.

**CORRECTION to the B2634 Table A framing.** That table listed SEVEN parameters. Reading
the producers shows only TWO of the 7 reach THIS strategy's gate: P3 `drift_window_days`
gates `within_pead_window` (pead.py:179) and P6 `YOY_GROWTH_LONG_THRESHOLD` gates
`yoy_surprise_high` (earnings_surprise_yoy.py:81). P4/P5/P7 gate `pead_positive_surprise` /
`pead_negative_surprise` (pead.py:259-265), which screener.py:5041 never reads - they are
SIBLING knobs, live for the short and standard variants only. Table A is the FAMILY's
producer surface; this strategy's search space is 3 x 5 = 15 cells, all 15 gradable.

**Step-1 result (IN-SAMPLE ONLY, 2022-05-05..2025-05-05; no gates per B1608; holdout NOT
read).** Best pooled Sharpe over 26 exits per cell:

| drift window | yoy>=0.05 | 0.10 | 0.20 | 0.35 | 0.50 |
|---|---|---|---|---|---|
| <=20d | 1.473 | **1.475** | 1.347 | 1.300 | 1.261 |
| <=40d | 1.003 | 1.094 | 0.968 | 0.841 | 0.800 |
| <=60d (production) | 0.748 | 0.851 | 0.772 | 0.714 | 0.721 |

**The drift-window axis is monotone at 5 of 5 threshold levels** (tighter window strictly
better, every time) - which is the Bernard-Thomas PEAD prediction that drift is strongest
immediately post-announcement and decays. Five independent confirmations of one ordering is
a structural signature, not a lucky cell. **The surprise-size axis is NOT monotone**: it
peaks at 0.10 and decays in 3 of 3 rows - consistently, so the shape is real, but bigger
surprises do not help.

**The variance-mining hypothesis is REFUTED for this grid.** The council's Contrarian and
Outsider both predicted the winner would be the tightest, smallest-n cell winning on noise.
Measured: the tightest cell (20d / 0.50, 384 IS trades) ranks 5th at 1.261; the winner
(20d / 0.10) holds 792 IS trades of the 1,694 available and 196 holdout trades. The lift
comes from the axis with the literature prediction, not from sample shrinkage.

**PRE-REGISTRATION (recorded BEFORE any holdout read - that ordering is the whole point).**
Cell: `drift_window_days<=20, yoy_growth_long_threshold>=0.10, exit time_stop_10d`.
**Trials searched: 390** (15 cells x 26 exits) - the number a grid-stage multiplicity
correction needs, and which B2376 measured as ABSENT from the pipeline (BH-FDR runs at the
roster stage across strategies; PSR is a single-candidate statistic, blind to trials).

**The candidate-cap objection, costed and void (L645).** A tightened gate could only be
non-exact if the engine had TRUNCATED candidates at `max_candidates_per_day=30`, since the
freed slots would hold trades never simulated. MEASURED: pead has a 48-fire day against
that cap, which is positive evidence the cap did not apply - `backtest.py:2417` bypasses it
under cube isolation (`_cand_iter = candidates if self.cube_isolation`). Subsetting is
exact for this cube. The sweep re-checks this per strategy and DISCLOSES when a cube offers
no such evidence.

**NOT on the critical path: the family battery adapter.** The 9-step post-config battery
fires only from the engine's landing hook (`run_phase1a.py:713`). No engine run means no
landing, so the adapter buys this campaign nothing; it stays ticketed for whenever a pead
engine run is actually launched.

**STEP 2 EXECUTED (B2644, owner-fired 2026-09-08: 'build the reader and run step 2').**
Reader: `scripts/offline_holdout_read.py` (all 390 lines in one read per the F5 design; refuses
a second read of the spent holdout). Artifact: `output_audit/b2644_pead_step2_holdout.json` +
its table. **VERDICT: FAIL, 5 of 6 gates.** The pre-registered cell's holdout: sharpe **1.148**
vs the 1.0 bar (PASS, +0.148 over the gate), PF 1.91 vs 1.3 PASS, sortino 2.366 vs 1.0 PASS,
n 196 holdout / 988 full PASS+PASS - **the single failing gate is PSR, which returns None**
(denominator_invalid: 1 - skew x SR + excess_kurt/4 x SR^2 = 1 - 1.334x1.148 + 0.181x1.318 =
-0.29, computed from the cell's own moments). MEASURED across the read: PSR is None on 46 of
390 lines whose median holdout sharpe is 1.264, vs 0.382 for the 344 computable lines - the
gate goes incomputable precisely on strongly-skewed winners. Whether an incomputable PSR reads
FAIL (current, fail-closed) or NOT-EVALUABLE (the B2012 three-state precedent for inf PF) is an
OWNER DECISION - S6-B2644a - because it decides this admission; changing a gate after it failed
the cell in front of me is the B2459 class and was not done. Peek bound (diagnostic, labelled):
25 of 390 peeked lines clear all six gates, sharpe 1.001..1.463; none can be promoted off this
read. The Step-1 selection VALIDATED out of sample: production cell holdout 0.844 -> chosen
cell 1.148.

**CORRECTION (B2651, owner-caught 2026-09-08).** pead_with_smart_money_long was earlier waved off as "contained, adds nothing" - WRONG on two counts: containment bars a second independent BET, not a better strategy, and the collinearity ruling cited is a compute-economy rule that does not apply to a zero-engine-hour campaign (L775). Graded honestly on the holdout its IS-star cell is ungradable (n=13) and 0 of 48 IS-selected cells clear 6/6, but 1 hindsight cell clears at holdout sharpe 1.308 > the parent's 1.148 - so it gets its OWN pre-registered Step-2 (S6-B2651), not a dismissal. **RULED 2026-09-09 (option 1; a peeked-admission option was chosen and rolled back the same turn):** the winning old-holdout cell is FORWARD pre-registered - committed before any post-2026-05-05 data exists (output_audit/b2652_peadsm_forward_prereg.json) - and gets ONE six-gate read on the first cube spanning >= 12 forward months; qualify -> roster, else the strategy closes FAIL with no re-pick. 

**FAMILY CLOSED (B2645-B2647, owner rulings 2026-09-08).** The representative was ADMITTED to
PHASE_1B_ROSTER.md (B2645: psr noted missing under ruling (a); B2646's units fix then made psr
COMPUTE at 0.9998 - 6 of 6 gates, no ruling needed - and re-judged the whole roster funnel,
3 -> 7 graded cells, deployable 15). Its declared mirror `pead_short_negative_yoy_growth` is
counted in the roster roll-up. The two contained longs closed by the PRE-REGISTERED sibling
pass (output_audit/b2647_pead_sibling_pass_prereg.json committed BEFORE grading, results in
b2647_pead_sibling_pass.json): `pead_long` 87% contained, own grade BELOW_POWER_FLOOR (holdout
n=4); `pead_with_smart_money_long` 88.3% contained, own IS-selected line holdout sharpe 0.17 /
psr 0.635 - both CONTAINED-IN-ADMITTED-REPRESENTATIVE per the rule fixed in advance.
`pead_short` stays un-campaigned (negative holdout throughout the pre-gate);
`pead_with_insider_confirmation_long` has no rows in the EXIT-EXPANDED cube - CORRECTED at B2649: the trade log holds 10 CLOSED trades for it (2022-11..2025-05, dropped at cube expansion, cause UNKNOWN - RCA S6-B2649c); 10 trades in 4 years is 7.5x under the 75-trade full-period gate by construction, the insider-cluster leg being True on ~1 of 140 base pead bars. NEXT per the working order:
`rsi_oversold_with_smart_money_long` (FLAGGED consolidate-before-tune, S6-B2418), then the
macd family through the collinearity pre-gate.

**OPEN, owner-gated: the single holdout read.** It is a one-way door - firing it ends the
pre-registration for this strategy forever, and the production cell's holdout (0.844 best
exit) is already known. Recommended gating: run the permutation / block-bootstrap null over
the same 390-trial max-selection FIRST, so the holdout number is read against a calibrated
threshold instead of a bare 1.0. See S6-B2638a/b/c.

### D.2 PEAD resim knobs wired + exploratory bucket reconciled (B2686/B2687)

*Source lines 3081-3096, verbatim.*

#### PEAD RESIM KNOBS WIRED + EXPLORATORY BUCKET RECONCILED (B2686/B2687, owner word 2026-09-11)

S6-B2645a EXECUTED: PEAD_DRIFT_WINDOW_DAYS + PEAD_YOY_LONG_THRESHOLD env knobs wired at
signal_loader.py's two bare call sites - kwargs built only when set, production
byte-identical unset; pinned by test_b2686_pead_env_knobs_reach_the_producers (recorder
arms both directions). The admitted pead cell (drift<=20 / yoy>=0.10) is now
RESIM-CAPABLE; the SPECS entry's engine-reachability note corrected in place
(producer_variant_table.py). Band membership for any resim sweep stays a band-review
call (11.2c).

S6-B2636a EXECUTED (build) - premise decayed and re-measured: the importable registry
EXISTS (multiple_testing_correction.EXPLORATORY_STRATEGIES:70, 25 live members) vs 51
docstring-marked; reconciliation in output_audit/b2687_exploratory_reconciliation.json
- 33 marked-not-in-registry + 7 in-registry-unmarked. MEMBERSHIP is owner-ruled: the
33-name promotion menu awaits the owner's word (S6-B2687a); the 7 unmarked need only
cosmetic docstring lines.

### D.3 The first offline campaign's measurements (old §11.2b)

*Source lines 3495-3500, 3565-3567, verbatim.*

Step 1 is a filter over the existing cube. MEASURED for `pead_long_high_yoy_growth_only`: signal
coverage 2,116 of 2,116 fires, and re-applying the production levels returns 2,116 of 2,116
landed fires - so the subset is exact and the whole Step-1 grid costs no engine time.
**Wall-clock MEASURED: 103.9 s** for 15 cells x 26 exits = 390 gradings, dominated by loading the
4.9M-row cube CSV - against 16-40 h for one engine config. This is the owner's
run-producers-once directive in its strongest form: the producers already ran, in R5.

  N x M cells. Only the UNPREDICTED axes spend multiplicity budget. MEASURED for pead: the
  drift-window axis is monotone at 5 of 5 levels of the surprise-size axis (the Bernard-Thomas
  prediction), while surprise-size peaks mid-range at 0.10 in 3 of 3 rows.

---

## E. CROSS-SECTIONAL MOMENTUM (xs_momentum_top_decile, vwap_extension, xs_low_beta)

### E.1 Top_decile breadth Step 1 landed offline (B2673)

*Source lines 2967-2980, verbatim.*

#### TOP_DECILE BREADTH STEP-1 LANDED OFFLINE (B2673, owner word 'Proceed' 2026-09-11)

First campaign run under 11.2b2's two-legs rule and the first use of the extracted
scripts/breadth_step1_grid.py (parameterized by strategy - the L754 contract; the
institutional grid remains the family-hardcoded first instance). Base = the ADMITTED depth
line (xs_momentum_12_1 >= 0.529); reproduction gate matched the admission artifact exactly
(IS 0.751, full n 128). 7 companion axes x IS-retention-quantile levels x exits = 650
graded IS lines, 0 axes coverage-skipped, npt excluded from ranking, HOLDOUT UNTOUCHED
(output_audit/b2673_topdecile_breadth_step1.json). Power floors (15 holdout / 75 full,
counts only): 4 of 7 axes have a viable line; best = pct_from_vwap >= 36.63 /
time_stop_10d, IS 1.928 (ci_lo 0.521) n 52/84 vs base IS 0.751. Step-2 one holdout read is
S6-B2671c, awaiting its own owner word; any qualifier gets the pead control-family
comparison (promoted B2658 rule) before an admission proposal.


### E.2 Top_decile Step 2, the vwap-extension pair, the option-C re-ruling, xs_low_beta (B2678-B2685)

*Source lines 3021-3079, verbatim.*

#### TOP_DECILE BREADTH STEP-2 READ + CONTROL VERDICTS (B2678, owner word 2026-09-11)

S6-B2671c executed on the owner's word ('S6-b2671c proceed'; DISCLOSED-RE-READ - the
subject holdout was first read at B2668, disclosure accepted). ONE read of all 650
registered b2673 cells via scripts/breadth_step2_read.py (shared build_frame with
Step-1 so the steps cannot drift; fail-closed --ruling):
**66 of 650 cells clear all six non-npt gates**
(output_audit/b2678_topdecile_breadth_step2.json). Baseline = the admitted depth line,
HO 2.183 n 41/128 at ts10 - REPRODUCED exactly by the monthly_above_sma_12 cell, which
is a measured NO-OP on this base (True on 128 of 128 base fires), an incidental
verification of the B2668 admission. CONTROL VERDICTS (pead control, promoted B2658
rule): pct_from_vwap's big lift (HO 3.085 vs 2.183) is CONTROL-REFUTED as general
structure (control lift +0.864 vs subject +0.90); monthly_above_sma_12 likewise
(+0.776). news_sentiment_30d >= 0.188 is the one subject-specific axis (control lift
-0.019) and adds +0.13 HO at a LOWER ci_lo (0.494 vs 0.586) on fewer holdout trades
(32 vs 41). Admission options ticketed S6-B2678a for the owner; recommendation: admit
nothing new - the depth line stands as top_decile's final form.

#### VWAP-EXTENSION STANDALONE PAIR WIRED + PROXY READ (B2680, owner word 2026-09-11)

S6-B2679 executed on the owner's word ('Lets build and test such strategies'): Class 7
pair strat_vwap_extension_momentum_long/_short wired same-turn (221 -> 223 registered,
both EXPLORATORY + DO-NOT-DEPLOY pending cube; threshold 35.0 CHOSEN - midpoint of the
owner-approved ~35-40 band, to be band-swept at the pair's OWN Step-1 on next-cube
fires; mirror per B1382, asymmetry surfaced; lint pin
test_b2680_vwap_extension_pair_fires_correctly; four F-002 pins -> 223; roster + drift
snapshot regenerated). PROXY FEASIBILITY READ (PROXY-POPULATION label - entries are
bars where SOME recorded R5 strategy fired, 52,725 unique, coverage 1.0000; NOT the
standalone's true universe; output_audit/b2680_vwap_extension_proxy.json): 6,550
long-proxy entries -> holdout 0.228 at breakeven_plus_trail, -0.349 at time_stop_10d -
0 of 2 exits near the gates. HONEST REVISION: the filter's lift lives in the
INTERSECTION with already-selective entries (top_decile 3.085, pead control 1.708),
not in the raw condition on a broad population - the standalone thesis is WEAK at the
naive threshold on the proxy; the next cube gives the true-universe verdict.

#### TOP_DECILE RE-RULED TO OPTION C - the breadth stack ADMITTED (B2684, owner word 2026-09-11)

S6-B2678b: the owner re-ruled the B2678a option-A decision to OPTION C on the B2682
per-year evidence (filtered beats base 4 of 4 gradable years; 2022 = abstention).
Admitted line: depth xs_momentum_12_1 >= 0.529 AND breadth pct_from_vwap >= 36.6266,
time_stop_10d - HO 3.085 ci_lo 1.200 psr 0.999 PF 4.829 n 32/84, IS 1.928; metrics
re-derived fresh and asserted equal to the b2678 Step-2 row (fail-closed) in
output_audit/b2684_topdecile_breadth_admission_grid.json; admission entry SUPERSEDED in
place with the full chain (B2668 -> B2678a A -> B2678b C) and labels
CONTROL-REFUTED-ATTRIBUTION + DISCLOSED-RE-READ + GRID-SELECTED. Deployable stays 28
distinct (same strategy set); the B787 EXPLORATORY tag rides; engine wiring of BOTH
added gates remains the S6-B2411-class NEW-GATE build. The A-ruling's rationale (one
tape factor double-counted across strategies) survives as a PORTFOLIO-level concern -
flagged for the Phase-1B blended review where max_drawdown/calmar re-engage.

#### XS_LOW_BETA ADMITTED AT BASELINE (B2685, owner word 2026-09-11)

S6-B2674a resolved by 'All open tickets implement now': xs_low_beta_with_smart_money_long admitted at its BASELINE time_stop_10d line - no
added gate, so no engine change is needed for this row. HO 1.510 psr 0.995 PF 2.286
n 73/452, IS -0.198 (the IS/holdout-inversion label rides). Metrics re-derived fresh
and asserted equal to the B2674 measurement row (fail-closed) in
output_audit/b2685_xslowbeta_admission_grid.json; roster re-rendered -> 29 distinct
(test_b2417 moved 28 -> 29). Surfaced by an owner-ruled measurement, not a search grid;
it also clears at r_multiple_2r (1.296), so the line is not single-exit fragile.

### E.3 Approval-flow violation lineage, L779 (old §11.2c)

*Source lines 4007-4011, verbatim.*

The B2660 admission doctrine (all-six-holdout-gates = admissible) sets the CRITERION; it does
not waive the per-stage APPROVALS above. Violation lineage: L779 - the top_decile campaign ran
band design, the Step-2 spend and admission on 'start the queued campaign' alone; the owner
caught it and RATIFIED the admission after the fact (2026-09-10), and this section exists so
ratification is never needed again.

---

## F. CANDLE FAMILY (three_white_soldiers / three_black_crows_short - IN CAMPAIGN)

### F.1 The candle instance - second worked derivation, S6-B3089 (old STEP 3)

*Source lines 1679-1768, verbatim.*

#### THE CANDLE INSTANCE - SECOND WORKED DERIVATION (S6-B3089, 2026-09-23)

Added because the Step-2 procedure had been written as one campaign's story:
61 family-specific tokens across 42 lines, including procedural steps reading
*"Config 1 = sw50sp50"* and a MANDATORY pre-triage marked *"It has now been
RUN"*. A rule with two instances is much harder to mistake for a narrative.

**FAMILY:** `three_white_soldiers` (candle_anatomy). `<K>` = 1 knob-cell x 24
registered exits per config, NOT 300.

**STEP-1 BASIS, verified not assumed.** 18 landed configs, `_sweep_200.txt`
(200 tickers, confirmed 200 lines), window `2024-05-05 -> 2025-05-05` - so
exactly **200 ticker-years**, which is what makes the 10.88x Step-2 scaling
apply unchanged. Each config's cube holds `rows / results_n_exits` trades per
cell; verified `rows / 24 == fires == admit.full_period_n` on 18 of 18.

**THE SLATE, by the mechanical rule in STEP 2 ENTRY** (rank on
`step1_ranking[0].is_ci_lo`, duplicate-signature collapse, ties to the
deterministic lower config index, take the first 3). No signature collapsed -
all 18 best-rows carry distinct signatures:

| order | config | knobs (body/step/wick) | is_ci_lo | is_sharpe | IS n | tier |
|---|---|---|---|---|---|---|
| 1 | **c14** | 0.5 / 0.0 / 0.3 | +0.225 | 0.993 | 98 | MID |
| 2 | **c08** | 0.3 / 0.0 / 0.3 | +0.075 | 0.630 | 181 | DEEP |
| 3 | **c13** | 0.5 / 0.0 / None | +0.067 | 0.720 | 137 | DEEP |

Next two, recorded so a later widening need not re-derive them: c01
(+0.048, n 560) and c04 (+0.040, n 240).

**READ THE TIER BEFORE THE RANK.** The slate leader is the SHALLOWEST of the
three - n=98 against 181 and 137 - and across all 432 graded cells only **10
carry a positive lower bound**. This is the effect the tier column exists to
expose (RANK IS NOT TRUSTWORTHINESS), and it is why the tier column was
restored to the unified renderer at B3088.

**PRE-TRIAGE (mandatory, run for THIS family per B3089).** Step-1 scope 200
ticker-years; Step-2 full period 544 x 4 = 2,176 (**10.88x**), Step-2 holdout
544 x 1 = 544 (**2.72x**). Projecting each config's WORST per-cell count:

| config | worst Step-1 n | projects to full (bar 75) | projects to holdout (bar 15) | verdict |
|---|---|---|---|---|
| c14 | 98 | 1,066 | 267 | **clears both** |
| c08 | 181 | 1,969 | 492 | **clears both** |
| c13 | 137 | 1,491 | 373 | **clears both** |

**RESULT: the pre-triage excludes nothing, by a margin of more than 13x on the
binding bar.** As in the smc campaign, the trade floors will not be what
decides this strategy - the four statistical gates will. **The same limitation
rides:** no candle Step-1 config ran a day of 2022-23, so the fire rate in the
two added years is UNMEASURED.

**COST, projected per config from ITS OWN Step-1 base (S6-B2364's rule, never a
median):**

| config | step-1 measured | step-2 projected at 10.88x | legs at the 4.5h cap |
|---|---|---|---|
| c14 | 1.989h | **21.6h** | 5 |
| c08 | 2.004h | **21.8h** | 5 |
| c13 | 1.506h | **16.4h** | 4 |
| **slate serial, if the waterfall never stops** | | **~59.8h (2.5 days)** | 14 |

The waterfall means only config 1's 21.6h is committed at launch. **B2107's 5h
hard cap is satisfied by LEGGING, not by shortening the run** - `leg_cap_hours`
4.5 with `max_legs` 6 - which is the sanctioned mechanism and the one the smc
Step-2 template uses.

**SPEC SHAPE - the window and universe are NOT typed.** `phase_table.resolve(2)`
injects window `2022-05-05 -> 2026-05-05` and `output_audit/r5_universe_544.txt`
from the phase table above, and `spec_refusals` refuses a spec that types them
(B2713/L788). A Step-2 candle spec therefore declares `step: 2`,
`step1_cube: false`, the leg cap, an explicit `pool_workers`, and one arm
carrying the config's four `CANDLE_*` env knobs - and nothing else about scope.

**THE 2026-08-30 AMENDMENT (S6-B2409).** The original D1 stop condition was *qualifies AND is
ROBUST* - ROBUST meaning the holdout Sharpe cleared the 1.0 gate by more than the 0.333
selection-noise floor (i.e. holdout > 1.333). The owner retired that floor and the
ROBUST/PROVISIONAL split **in their entirety**: clearing the six gates IS qualification and IS the
stop condition. In code, roster_core.qualifier_margin(holdout_sharpe) reports the margin over the
live pooled gate as a plain number - no floor argument, no label - and the grid payload's
qualifier key is `qualifiers` (every PASS row). The old mechanics (robust_status, the floor
constant, the provisional_qualifiers key) are removed and pinned removed
(test_b2409_floor_retired_margin_measures_live_gate). Applied retroactively to config 1: its 3
gate-clearing combinations (one parameter set, tail_n variants) are QUALIFIERS, so **the waterfall
stop condition is MET at config 1 and configs 2/3 are not run**. The owner retained the tail_n=20
member (ruling 2 of the same date, S6-B2410).

**NO separate baseline run is needed** (L423) - all six gates are ABSOLUTE thresholds, so admission
depends on a candidate's own metrics. Valid on the appended universe because `--cube-isolation`
bypasses the candidate cap (backtest.py:1763).

### F.2 Step-2 launch instance c14 - spec, the drift incident, runtime (old STEP 3.2 / 3.3)

*Source lines 1847-1850, 1832-1845, 1862-1866, verbatim.*

**CANDLE INSTANCE (three_white_soldiers c14, B3089):** output_audit/b3089_candle_tws_c14_step2_spec.json;
arm env CANDLE_N_BARS=3, CANDLE_MIN_BODY_PCT=0.5, CANDLE_MIN_STEP_PCT=0.0, CANDLE_MAX_WICK_PCT=0.3
(backtest/config.py:2487-2490 - the wick knob's None level is the empty string); fires_at_production
199 from the family's step-0.5 smoke.

- **`allow_engine_drift: true` IS THE TEMPLATE VALUE - `false` KILLS A MULTI-LEG WAVE AT ITS
  FIRST LEG BOUNDARY AFTER ANY COMMIT (S6-B3093).** `drift_check` in `scripts/launch_sweep.py` has
  TWO halves: it refuses whenever HEAD differs from the manifest's `frozen_sha` - so a queue row
  or a monitor report refuses the next leg exactly as an engine commit would - AND it refuses when
  an engine-consumed path is DIRTY (uncommitted; launch_sweep.py:77-81). **`true` turns off BOTH**
  (launch_sweep.py:70-71 returns before either runs), so the rule it leaves is *no engine EDIT OR
  commit until landing*, and the monitor must `git status` the engine paths, not only `git log`.
  (B3094 CORRECTION: this bullet first said the check *does not look at engine code* - false.) This project commits every turn (CHECKLIST #67 / #94). **MEASURED
  2026-09-24:** the candle c14 Step-2 wave ran leg 1 to its 4.5 h cap at sim-day 329, then leg 2
  was REFUSED because four queue-only commits had moved HEAD; `git diff` over `backtest/` between
  the pinned sha and HEAD was empty. With `true`, the safety rests on the rule the `run_wave.py`
  B2174 comment names - **no engine edit or commit until the wave lands** - so keep it. `false` is right
  only for a single-leg run. Pinned by
  test_b3093_drift_check_refuses_any_commit_not_only_engine_commits.

**CANDLE INSTANCE (three_white_soldiers c14, pool_workers 6):** leg 1 of attempt 2 ran uncontended
from sim-day 0 to 329 inside its 4.5 h cap - **49.49 s/sim-day** by the B2127 rate line in
output_audit/b3091_c14_step2_launch.log - so the whole window is about 13.8 h. Free commit fell to
**1.58 GB** at 02:49 and Windows grew the system-managed page file, taking the commit limit from
47.63 to 49.65 GB, with no low-memory event (output_audit/c14_step2_monitor_readings.jsonl).

### F.3 Actuation measurement, S6-B2860 (old §11.0b)

*Source lines 3413-3418, 3420-3424, verbatim.*

**THE CLASS.** Table A may define a band for a producer parameter that the producer does not
contain. MEASURED at S6-B2860: the candle anatomy bands P1.1-P1.4 named n_bars, a body
percentage, a step magnitude and a wick cap; `compute_candles` had the literal 3 inside
`range(1,4)` and NO body, step or wick test at all. Three of the four parameters did not exist
in any form. The ruled Step-1 SEARCH is *all fire-adding configs*, so with no actuator the
search had nothing to vary and 54 configs would have produced 54 BYTE-IDENTICAL runs.

**WHY IT SURVIVED.** `validate_spec` refused a resim level with no env NAME, and offered the
escape *strike them or add the knob*. It never checked that a declared name is READ: a spec
declaring `CANDLE_TOTALLY_FAKE_KNOB_NOBODY_READS` validated CLEAN (measured B2866). So the
escape could be satisfied by typing a name - the L751 class, where a flag accepted, stamped
into the artifact and never applied is worse than one that errors.

### F.4 Regime-map evidence on the soldiers' own cubes (added B3096 from ledger rows S6-B3094c / S6-B3095)

Source: the ledger rows S6-B3094c (restated at B3095 on this family's artifacts only) and S6-B3095 in `EXECUTION_QUEUE.md`, 2026-09-24. c14's Step-1 cube came from a RESUMED invocation (its gate receipt carries `--resume-from-checkpoint`) and records real regime flips only from 2025Q1 - 23 of its 98 `regime_flip` rows; c08 and c13 ran fresh (no resume flag) and record them from 2024Q3. A resume of the c14 Step-2 wave would carry the regime map only for days from 330 on. The owner answered option (a) - fix the engine first, rebuilding the map and its day-to-day state at every leg start - and then said "Pause" before any edit; the fix is BLOCKED on the owner's word (runbook §4.8).

### F.5 The Step-0.6 survival example, S6-B2822 (old §11.2 row 0.6, with its table header)

*Source lines 3477-3478 and 3481, verbatim - the old §11.2 table's header and its row 0.6, joined as one table.*

| Step | Do | Command / mechanism | Must leave | Gate to the next step |
|---|---|---|---|---|
| 0.6 | **BRANCH: is every swept level OFFLINE-FREE?** For each parameter, ask whether the MAGNITUDE it thresholds was persisted in `signals_at_entry` at fire time. If EVERY scheduled level is a tightening of a persisted magnitude, Step 1 needs NO engine run - go to SS11.2b and skip steps 1-1.4. If ANY level loosens, or reads a magnitude the cube does not carry, that level is engine-only and the normal path applies to it | `scripts/offline_level_sweep.py` (its four refusals answer this mechanically: reproduction, coverage, join, truncation) | the decision recorded in the spec's `note` and in the queue row, per parameter | a level called free must REPRODUCE the landed fire set at the production values - anything below 1.0 means the persisted magnitude is not the quantity the engine thresholded, and the sweep refuses. **B2822 branch for the 38 changed-since-R5 (11.2b4): run the SURVIVAL FILTER FIRST and reproduce against the SURVIVING subset** - for a strategy whose entry condition moved, the raw landed set contains old-gate fires by construction and a 1.0 reproduction against it is impossible for the wrong reason (morning_star survives 46.2%); the free-level contract binds the current-gate fires |

### F.6 The two-Sharpe-column ruling and its measurement on this family's configs (old §6.4, S6-B3021)

*Source lines 472-472, verbatim.*

**TWO SHARPE COLUMNS, OWNER RULING 2026-09-23 (S6-B3021 option c).** The single column `best IS-Sharpe` NAMED a maximum and CARRIED the Sharpe of the best-`is_ci_lo` row. Selecting on `is_ci_lo` is correct and deliberate (L455 - a higher Sharpe can carry a negative lower bound); the LABEL was not, and it silently broke the B2182 diagnostic below, which states that `max - median` IS the selection artifact. MEASURED across the 14 landed candle configs: 2 disagree - `candle_tws_c06` printed 0.310 against a true max of 0.379 and `candle_tws_c12` printed 0.205 against 0.394, both maxima sitting on a DIFFERENT exit - so the artifact read 0.651 and 0.703 against a true 0.720 and 0.892. **`max IS-Sharpe` is computed over the GRADED POPULATION, the same rows as the median, never over `step1_ranking`** (top 10 by ci_lo, a SELECTED set - L708): the two coincide for candle at 24 graded rows and need not for a family with hundreds of combinations, and `max - median` must come from one population or it is not a difference. Pinned by `test_b3023_table_c_carries_max_and_selected_sharpe_separately`, whose fixture asserts the two columns DISAGREE (a fixture where they match would stop testing the thing) and which checks `max >= selected` across every landed candle artifact.

---

## G. FAMILY EXAMPLES OF CLASS-LEVEL COMMANDS AND ARTIFACTS

### G.1 Step 0.5 smoke - the first family's instrument (old STEP 0)

*Source lines 1305-1311, verbatim.*

Instrument the qualifying event first. **FAMILY EXAMPLE (smc) - generic form (SS11.2 step 0.5):
count the strategy's fires on 6 megacaps at production params via the producer or precompute
(institutional used `build_institutional_persistence_precompute.py` + a `python -c` count):**
```bash
PYTHONPATH=. python scripts/instrument_breaker_block.py --ticker AAPL \
  --start 2022-05-05 --end 2026-05-05 --out output_audit/<STRATEGY>_instr.json
```

### G.2 Step-1 spec and knob examples (old STEP 1.3)

*Source lines 1476-1483, 1488-1500, verbatim.*

```bash
#### spec: copy output_audit/b2527_icg_span50_spec.json, change ONLY strategy_subset / wave / arms[0].env
PYTHONPATH=.:scripts python scripts/launch_detached.py --chain --batch <bNNNN> \
  --specs output_audit/<bNNNN>_<STRATEGY>_cfg<N>_spec.json [more specs, information order] \
  [--wait-for output_audit/<running wave>_wave_summary.json]
#### -> Task Scheduler task stockpicks_chain_<bNNNN>_<ts> (observe it Running - S6-B2529a);
#### per spec: run_wave.py -> launch_sweep.py -> prelaunch_gate.py -> run_phase1a.py, gate_receipt.json
```

```bash
STRATEGY_SUBSET_FILE=output_audit/_subset_<STRATEGY>.txt \
OPTIMIZATION_MODE=1 \
SMC_SWING_LENGTH=<P1_value> STRAT_EMA_SPAN=<P6_value> \
PYTHONPATH=. python backtest/run_phase1a.py \
  --tickers-file output_audit/_sweep_200.txt \
  --phase 1a-beta --cube-isolation \
  --no-agents --no-news --no-git --no-walk-forward \
  --screen-pool-workers 3 \
  --start 2024-05-05 --end 2025-05-05 \
  --max-run-hours 4.0 \
  --output-dir output_<STRATEGY>_cfg<N>
```

### G.3 Grader and renderer examples (old STEP 2 GRADE)

*Source lines 1603-1611, 1627-1637, verbatim.*

**FAMILY EXAMPLE (smc) - generic form: the family grader named in SS11.1 R4 (institutional:
`grade_institutional_config.py --cube output_icg_<cfg> --min-consecutive-quarters <P4>
--growth-lookback-quarters <P5> --growth-multiple <P6> --span <P9>`); the battery runs it on every
landing (B2520), so this hand form is for a re-grade only:**
```bash
PYTHONPATH=.:scripts python scripts/tighten_breaker_block.py \
  --cube output_<STRATEGY>_cfg<N>/trade_exit_detail.csv \
  --out output_audit/<STRATEGY>_cfg<N>_grid.json
```

**Generate the locked artifact. Since B2579 (S6-B2573c) `--keys` DEFAULTS to the family's own
`tools.grid_keys` (smc `close_mitigation,break_pct_max,age_bars_max,tail_n`; institutional
`combo`), so pass it only to override - the smc keys spelled out below are that default, not a
value to copy onto another family:**
```bash
PYTHONPATH=. python scripts/producer_variant_table.py \
  --strategy <STRATEGY> \
  --results output_audit/<STRATEGY>_cfg<N>_grid.json \
  --keys close_mitigation,break_pct_max,age_bars_max,tail_n \
  --out output_audit/PRODUCER_VARIANT_TABLE_<STRATEGY>.md
```

### G.4 Battery step 2 - family grader and free-levels commands (old MANDATORY POST-CONFIG ANALYSIS step 2)

*Source lines 2392-2427, verbatim.*

#### 2. Grade - with the CONFIG'S OWN parameters (PER FAMILY - B2569 generalisation)

**This step is family-dispatched, never strategy-specific prose.** The battery
(`run_postconfig.py::FAMILIES`) fails CLOSED on a strategy with no registered grader; this doc
previously showed only the smc command, which is how an entire analysis step (free levels) got
executed once at strategy level and never per config (the N1 class bug, b2569 audit). The step
has TWO legs on every landing and step 2 is DONE only when BOTH succeed:

**(a) the family grader, at the manifest's own parameters (FAMILY EXAMPLES - both registered
families. Since B2579 a third family is ONE declaration: a `tools` adapter block in its SPECS entry
(keys / grid_keys / grade / spot_check / single_combination, optional free_levels + engine_anchors),
from which `run_postconfig.family_entry` builds the row - an incomplete block is not a family and
`run_postconfig.FAMILY_REFUSALS` says which piece is missing, so the B2578 launch gate refuses the
spec before the engine spends the hours):**
```bash
#### smc_breaker_block family:
PYTHONPATH=".;scripts" python scripts/tighten_breaker_block.py --cube output_cfg<N>/trade_exit_detail.csv \
  --swing-length <THE SW THIS CONFIG RAN> --min-n 10 --out output_audit/<batch>_cfg<N>_grid.json
#### institutional_committed_growth family:
PYTHONPATH=".;scripts" python scripts/grade_institutional_config.py --cube output_icg_<cfg> \
  --min-consecutive-quarters <P4> --growth-lookback-quarters <P5> --growth-multiple <P6> --span <P9>
```
**Parameters MUST match the run.** The smc grader RE-DERIVES every fire; a mismatch silently
drops the fires that do not reproduce - cfg2 lost 167 of 420 that way (L454); the union
diagnosis-loss gate aborts above 2pct. The institutional grader REFUSES non-production P7/P8
values (L751 - they are artifact stamps, not filters).

**(b) the FREE levels of every PERSISTED parameter, on THIS config's cube:**
```bash
PYTHONPATH=".;scripts" python scripts/grade_free_levels_institutional.py --cube output_icg_<cfg>
```
Levels come from SPECS `free_band` (single source). The tool gates itself: every covered landed
trade must RE-PASS the production gate offline (REPRODUCTION line printed) before any level is
graded - a reproduction failure exits 2 and the battery FAILS step 2 closed. Empty
`signals_at_entry` rows (S6-B2512 class) are counted and excluded, never silently failed. A new
family's free-levels grader is part of registering the family, not a later enhancement.

### G.5 Battery step 4 - the first family's spot-check command

*Source lines 2509-2511, verbatim.*

```bash
PYTHONPATH=. python scripts/spot_check_trades.py   --cube output_cfg<N>/trade_exit_detail.csv --n 50   --swing-length <SW> --ema-span <SPAN>
```

### G.6 The pre-B3096 run table's family examples (old §11.2, STEP 0-4 numbering)

*Source lines 3477-3478, 3480-3480, 3482-3482, verbatim.*

| Step | Do | Command / mechanism | Must leave | Gate to the next step |
|---|---|---|---|---|

| 0.5 | Instrument ONE ticker at the production params to see fires exist (family example: `instrument_breaker_block.py` for smc; institutional used the precompute builder + a `python -c` count). Generic form: count fires of the strategy on 6 megacaps at production params | family script or `python -c` | a fire count > 0 recorded in the spec's `note` | fires > 0 (a 0 here is a producer defect, not a search) |

| 1 | Write ONE spec per fire-adding combination (`output_audit/<batch>_<cfg>_spec.json`: `strategy_subset`, `tickers_file` = `_sweep_200.txt`, window, `arms[0].env` with every knob, `max_run_hours` <= 5, `resume`); copy an existing spec (`b2527_icg_span50_spec.json`) and change ONLY the knob values + names | spec file | the spec, diffed against its template in the turn | every knob in `arms[0].env` is a declared SPECS knob at a band level - `launch_refusals` (B2578) refuses the spec otherwise, and `launch_sweep.arm_env_matches` refuses an UNSET or mismatched one in the process env |

### G.7 Recovery-probe template (old §11.2l L3)

*Source lines 3946-3947, 3951-3951, verbatim.*

| # | Do | Mechanism | Artifact | Gate to next |
|---|---|---|---|---|

| L3 | **RECOVERY PROBE - where feasible (owner-ruled 2026-09-16).** FEASIBLE = the producer recomputes offline from cached OHLCV (the diagnose_* pattern; smc primitives and derived-precompute families qualify). Run the producer at each looser level over the L0 population's bars; measure the share gaining the binding leg; scale to a projected fire count, STATED AS A LOWER BOUND (bars where no consumer fired are invisible). A band whose probe projects BELOW the 100 floor is proposed only with a PROBE-BELOW-FLOOR label. INFEASIBLE producers are labelled PROBE-INFEASIBLE with the reason, and **starvation alone plus the owner's band word suffices** | a diagnose_-family script per producer (diagnose_smc_lsr is the template) | the probe artifact with per-level recovery shares | probe run, or PROBE-INFEASIBLE named |

### G.8 Table C / Table D / exit-registry artifacts of the first family (old §6.4-§6.5)

*Source lines 487-487, 509-513, 573-578, 593-598, 613-628, verbatim.*

**Superseded text (B2138/B2141, kept for lineage).** The funnel row itself carries the BAND VALUES, comma-separated and semicolon-delimited: `P1=20(fixed); P2=False,True; P3=1,2,3,5,10,20; P4=60,120,180,250,None; P5=0.01,0.02,0.03,0.05,None; P6=200(fixed)` - the values for each SEARCHED axis and the fixed VALUE for the two cross-config axes. B2141 replaced counts with values because two configs that searched DIFFERENT grids of the same width are indistinguishable by count alone. The delimiter is a SEMICOLON: a pipe splits the cell into six columns and destroys the table, which is what the first render showed. Values sort numerically through ONE shared helper used by both this column and the block below (L593: two sorts of the same values diverge on the first edit) - so a pasted row says which axes carried the search without a second table. P1 and P6 are read from the artifact's own `config` block, which `tighten_breaker_block.py` has recorded since B2138; before that they were written NOWHERE, which is why a swing-10 cube could be re-graded as swing-20 (S6-B2136) and why pre-B2138 artifacts read `?` there.

**PARAMETERS TESTED (added B2137, owner directive; family-complete since B2585).** Beneath the funnel, a second block names the bands each config exercised, one column per parameter of its family - the same derivation and the same markers as the funnel cell above, so the two renders cannot contradict each other. For the SMC family that is P1..P6, read from the result rows' own parameter keys; for the institutional family it is P1..P9:

| config | P1 swing_length | P2 close_mitigation | P3 tail_n | P4 age_bars_max | P5 break_pct_max | P6 span |
|---|---|---|---|---|---|---|
| `cfg1` | not recorded | 2: False, True | 6: 1, 2, 3, 5, 10, 20 | 5: 60, 120, 180, 250, None | 5: 0.01, 0.02, 0.03, 0.05, None | not recorded |

**TABLE D-2 IS RETIRED — B2725, OWNER CATCH. Its axis columns are now columns of TABLE D itself, and the landing report emits no D-2 section.** MEASURED CAUSE: there were TWO Table D renderers. `table_d_render.py` was built to the B2699 ruling (one unified table, a column per producer band) and renders the OFFLINE level-sweep artifacts; `producer_variant_table.table_d` renders the GRID artifacts and kept this split, which B2723 then wired into every landing - making the shape the owner had rejected the one MECHANICALLY REGENERATED per config. The duplicated `sw`/`sp` columns are gone because they ARE P1 and P6. Pin: `test_b2725_landing_table_d_is_unified_with_every_producer_band` (five arms, fail-proofed by deleting a band from the header); CHECKLIST #303 / L790. The superseded rationale is preserved below for lineage and NO LONGER GOVERNS. A second
table rather than more columns because at 18 columns a markdown table wraps, which
is exactly how Table C lost four columns three times. Columns: `# | config |
P1 swing | P2 close_mit | P3 tail_n | P4 age_bars | P5 break_pct | P6 span |
npt_excl`. P2-P5 were already in every ranked row's `admit` dict and simply never
displayed — hiding four of six swept axes was a display defect, not a data gap.

**SCOPE CAVEAT (S6-B2499 audit finding):** the `sw`/`sp` columns and ALL SIX D-2
axes are read from HARDCODED keys of the smc_breaker_block spec
(`P1_swing_length`, `close_mitigation`, `tail_n`, `age_bars_max`, `break_pct_max`,
`P6_span`). A grid from another family renders `None` in those cells — it degrades
legibly rather than crashing, but reusing Table D for the institutional family
needs a per-strategy axis map keyed off SPECS. Ticketed S6-B2500.

**`regime_flip` is NOT a third deprecation - it was FIXED, and the difference is measurable per
cube.** The recorded defect (L526 / S6-B1771) is real and permanent for the cubes it describes:

| cube | era | regime_flip rows | real flips | fallback `regime_flip_max_days_20` |
|---|---|---|---|---|
| `output_cfg1` | pre-B2043 | 330 | **0** | 330 (100pct) |
| `output_w1_sw20_span21` | pre-B2043 | 320 | **0** | 320 (100pct) |
| `output_b2114_ref` | post-B2043 | 95 | **42** | 53 (56pct) |

B2043 root-caused it: `set_worker_regime_map` was defined and NEVER CALLED (one occurrence in
the codebase - its own definition), beside a placeholder that fabricated a "no" answer. Both
fixed; the flip branch went live. `roster_core.measure_degraded_exits` confirms it per cube -
the four pre-fix cubes still collapse the `time_stop_20d`/`regime_flip` pair, and the post-fix
reference cube lists only `reverse_signal` -> `atr_trail_1x`. **This is why the runbook measures
degeneracy per cube (#252) instead of maintaining a list: a hand-kept list of broken exits goes
stale the moment one is repaired, and a stale list nearly retired a working exit at B2139.**

---

## H. SHARED LAUNCH MEASUREMENTS (both families)

### H.1 The memory-ceiling rules as written with both families' measurements (old STEP 3.3)

*Source lines 1878-1893, verbatim.*

**Three rules this produced, each of which cost something to learn:**

- **A pyramid alongside a live wave is not free.** On the smc b2399 run the engine alone ran 48-58 GB committed of 63.63;
  engine **plus** a pytest run hit 62.03 GB with **1.61 GB free** - the exhaustion class S6-B2237
  records as having killed three prior runs. Do not run the full suite against a live wave.
  **SEQUENCE IT BEFORE THE LAUNCH - there is no leg-boundary window (B3091).** This bullet used
  to say *defer the commit to a leg boundary*, and the third bullet below measured why that
  cannot work: run_wave's leg loop respawns the engine and *the tree came back within
  seconds*. So every commit that needs a pyramid is made and pushed BEFORE the wave launches,
  and the next one waits for landing. **MEASURED AGAIN 2026-09-23 (S6-B3091):** the candle
  Step-2 wave at pool 6 ran beside two pyramids; Windows logged low-virtual-memory events at
  22:56, 23:10 and 23:12 (a pytest at 11.1 GB, then an engine worker at 5.5 GB), the box became
  unresponsive and was restarted from the Start menu, and the run died at sim-day 19 of 1,003.
  `scripts/pyramid_gate.py` now records `engine_inflight` from the engine's own
  `run_heartbeat.json`, because its `chain_inflight` field reads only `serial_chain.log` and
  printed **none** at both ends while that wave ran - a direct run_wave launch never writes there.

### H.2 Monitoring rates (old STEP 3.4)

*Source lines 1911-1913, verbatim.*

- **The diff interval must exceed the expected per-unit time.** At the campaign's own measured rate
  (CANDLE INSTANCE 49.49 s/sim-day; SMC INSTANCE about 1.3-2.0 min/day), a
  60-second window showing no movement is normal, not a stall.
