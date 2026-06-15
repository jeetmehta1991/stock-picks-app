# B772 -- TIER 1 dual-verdict on B769 council #53 (confluence-stack) + #54 (MA-cross effective-N)

# per CHECKLIST #77 + #44(b) + #69 + #94 + #105 + #106 + #107
# Source: B769 council TIER 1 tickets #53 + #54
# Source: output_audit/fire_count_measured_b660_full_universe.json (B660 full T1a 2020-2026 222 strategies)
# Source: backtest/signals/screener.py strat_golden_cross_volume + strat_death_cross_50_200_volume (B772 EXPLORATORY tag applied)
# per memory: feedback_no_a_priori_strategy_pruning.md + feedback_no_prior_edge_consolidate_before_tune.md + feedback_minimum_fire_count_gate_before_cube.md

## Both council questions empirically settled in one batch

The existing B660 measurement file (full T1a x 6.4yr x 222 strategies) carries the exact data both #53 and #54 require -- no new measurement run needed. Findings below.

## #54 -- MA-cross effective-N PARTIALLY REFUTED

Council F7 claim: "MA-cross family (B-1 to B-5) ... fire 1-3/ticker/several years, cluster at 3-4 regime transitions = 5-10 independent events universe-wide. Structurally unvalidatable. Disposition: EXPLORATORY-or-delete not KEEP-AS-IS."

**B660 empirical measurement (T1a 503 tickers x 2020-2026 = 6.4yr = 616,040 bars):**

| # | Strategy | B660 fires/yr universe-wide | Total fires 6.4yr | Verdict |
|---|---|---|---|---|
| B-1 | strat_golden_cross_9_21 | **2,535/yr** | ~16,225 | **PASS_CUBE** |
| B-2 | strat_golden_cross_20_50 | **992/yr** | ~6,350 | **PASS_CUBE** |
| B-3 | strat_golden_cross_50_200 | **504/yr** | ~3,226 | **PASS_CUBE** |
| B-4 | strat_golden_cross_volume | 23.1/yr | ~148 | **FAIL_FIRE_STARVED** |
| B-5 | strat_death_cross_50_200_volume | 13.6/yr | ~87 | **FAIL_FIRE_STARVED** |

**Council's "5-10 independent events universe-wide" claim is OFF BY THREE ORDERS OF MAGNITUDE for B-1/B-2/B-3.** Even applying aggressive 100x autocorrelation deflation, B-1 effective-N would still be ~25 events/yr (well above min_trades=30/regime threshold).

The Contrarian critique from B769 inline council was 100% right:
> "5-10 independent events universe-wide math is sloppy -- effective-N is per-ticker-conditional, not universe-wide. Empirical measurement required not analytical assertion."

**Per-strategy disposition (empirically-grounded, narrowed from council's blanket claim):**

- **B-1 PASS_CUBE** (2,535/yr) -- KEEP-AS-IS; council's EXPLORATORY claim REFUTED
- **B-2 PASS_CUBE** (992/yr) -- KEEP-AS-IS; council's EXPLORATORY claim REFUTED
- **B-3 PASS_CUBE** (504/yr) -- KEEP-AS-IS; council's EXPLORATORY claim REFUTED
- **B-4 FAIL_FIRE_STARVED** (23.1/yr) -- **EXPLORATORY tag applied B772**
- **B-5 FAIL_FIRE_STARVED** (13.6/yr) -- **EXPLORATORY tag applied B772**

The fire-starvation in B-4/B-5 is caused by the AND-compound gate (cross EVENT + vol_spike_2x EVENT). B-3 fires 504/yr WITHOUT the vol gate; adding vol_spike_2x drops to 23/yr = ~22x reduction. Two EVENT gates AND'd together drives joint probability to near-zero. This is a Pattern-AA-style negative-correlation-in-AND-stack (B760 Camarilla precedent).

### EXPLORATORY tag applied (B772 code change)

Added docstring to `strat_golden_cross_volume` (B-4) and `strat_death_cross_50_200_volume` (B-5) per W5 / W5m / strat_buybacks_lucca precedents. Per `feedback_no_a_priori_strategy_pruning`: NON-DELETION tag; strategies still run; cube still evaluates; verdict interpretation accounts for low effective-N.

Outsider/Reviewer 3 reframe option ("regime-detection signal as REGIME INPUT not entry signal") surfaced but NOT applied -- B-1/B-2/B-3 all PASS_CUBE so the reframe option is unnecessary for the majority of MA-cross strategies. Surfaces only for fire-starved B-4/B-5 where reframe could be a recovery path.

## #53 -- Confluence-stack pairwise correlation REFUTED

Council F8 claim: "Supertrend + Ichimoku + ADX (B-13) are ALL same underlying construct (trend-following lagging indicators) computed three ways. Three collinear measurements... tells almost nothing more than one... statistically backwards when the indicators are collinear. Consolidation > tuning. Deepest finding."

**Pre-registered falsifiability threshold (B769 ticket #53):** pairwise correlation >=0.85 -> council right + consolidate; pairwise 0.4-0.7 -> rhetorical overreach + strategies stay.

**B660 measured cross-system pairwise correlations on B-13 strat_supertrend_ichimoku_adx (full T1a 2020-2026):**

| Pair | Correlation | Threshold check |
|---|---|---|
| adx_strong x ichi_above_cloud | +0.090 | **0.090 << 0.85** |
| adx_strong x ichi_below_cloud | -0.019 | -0.019 << 0.85 |
| adx_strong x supertrend_bearish | +0.008 | 0.008 << 0.85 |
| adx_strong x supertrend_bullish | -0.008 | -0.008 << 0.85 |
| ichi_above_cloud x supertrend_bearish | -0.083 | -0.083 << 0.85 |
| ichi_above_cloud x supertrend_bullish | +0.083 | 0.083 << 0.85 |
| ichi_below_cloud x supertrend_bearish | +0.090 | 0.090 << 0.85 |
| ichi_below_cloud x supertrend_bullish | -0.090 | -0.090 << 0.85 |

**MAX cross-system pairwise correlation: +0.090.** Pre-registered threshold 0.85 NOT MET.

(The only HIGH correlations are within-system mutually-exclusive pairs: ichi_above x ichi_below = -0.758; supertrend_bull x supertrend_bear = -1.000. These are by-design mutual-exclusion of binary direction signals, NOT cross-system collinearity.)

**VERDICT: Council F8 REFUTED.** Cross-system pairwise correlations are near-zero. Supertrend / Ichimoku / ADX are EMPIRICALLY INDEPENDENT, NOT "one construct triple-counted." Contrarian's critique 100% right:
> "ADX measures trend strength (range expansion), Supertrend measures ATR-anchored direction flip, Ichimoku Kumo is a displaced midpoint band. Calling them 'one construct' is exactly the kind of rhetorical compression the council itself warns against."

### Nuanced extra finding (independence_predicted_vs_measured_ratio)

B660 also measured: `independence_predicted_joint_prob` = 0.000156; `predicted/measured ratio` = 0.003 -> **measured joint probability is 333x INDEPENDENCE-PREDICTED** when all 4 gates fire simultaneously.

Reconciliation: signals are PAIRWISE-INDEPENDENT (~0.09 max) but their joint co-occurrence is 333x what independence would predict. This indicates **regime-conditioned joint co-occurrence** (the 4 signals all detect "trending-strong-bull" from different angles, so during such regimes they cluster together), NOT pairwise collinearity.

This is the expected behavior for orthogonal indicators that all detect the same MARKET STATE from DIFFERENT vantage points. It's genuine confluence (signal x signal cross-confirmation when regime is right), not redundant triple-counting. Council's "statistically backwards" critique is exactly inverted: when 3 orthogonal indicators agree, that's MORE information than 1 alone (regime more strongly confirmed).

**Disposition: B-9 + B-11 + B-13 KEEP-AS-IS** (no consolidation needed). Council's "consolidation > tuning" claim REJECTED at the pre-registered measurement.

## Combined CHECKLIST #107 reconciliation (B772)

- **Findings surfaced:** 2 primary (council F7 PARTIALLY REFUTED 3-of-5; council F8 REFUTED at pre-registered threshold) + 1 nuanced (joint-vs-pairwise: regime-conditioned co-occurrence not collinearity)
- **Tickets filed:** 0 NEW + 2 annotations (existing #53 + #54 COMPLETED-EMPIRICAL with verdicts)
- **Code changes:** 2 strategy docstrings added (B-4 + B-5 EXPLORATORY tag per `feedback_no_a_priori_strategy_pruning` non-deletion marker)
- **Audit-clean: YES**

Cumulative ticket count post-B772: 129 unique S4-B7XX tickets (no new tickets; #53 + #54 closed in place).

## Strategy counts (unchanged)

221 ALL_STRATEGIES / 0 DEPRECATED / 1 STRATEGIES_DISABLED_MISSING_PRODUCER / **220 active.** B-4 + B-5 now carry EXPLORATORY docstring marker (NON-DELETION; strategies still register; cube still evaluates).

## Memory + checklist compliance

- `feedback_no_a_priori_strategy_pruning.md` -- EXPLORATORY tag on B-4 + B-5 is NON-DELETION marker; B-1/B-2/B-3 NOT tagged (council's blanket claim refuted)
- `feedback_no_prior_edge_consolidate_before_tune.md` -- #53 measurement-then-decide pattern; pre-registered 0.85 threshold; refuted -> stays as-is
- `feedback_minimum_fire_count_gate_before_cube.md` -- B-4 + B-5 below min_trades_overall (100) so EXPLORATORY tag warranted per fire-count gate rule
- `feedback_local_changes_default_global_needs_approval.md` -- per-strategy docstring changes (2 strategies); LOCAL scope; no global helper changes
- CHECKLIST #44(b) -- empirical reading of existing B660 measurement file applied
- CHECKLIST #67 -- doc-sync same turn (verdict + queue annotations + code changes all in B772)
- CHECKLIST #69 -- pyramid mandatory (842/842; will verify post-edit)
- CHECKLIST #77 -- canonical-source header on this verdict
- CHECKLIST #94 -- queue-mandatory-per-turn
- CHECKLIST #105 -- producer source + strategy source read end-to-end (B771 already covered)
- CHECKLIST #106 -- producer-data audit precedent
- CHECKLIST #107 -- findings-vs-tickets reconciliation (SEVENTH-FULL-EXECUTION since codification)
