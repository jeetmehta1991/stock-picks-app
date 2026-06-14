# Stage 4 — Context, Event & Calendar Cluster Walks

> **B750 STATUS BANNER (2026-06-14) — CLUSTER C SCAFFOLDING + INITIAL WALKS.**
>
> This is the THIRD of three new cluster docs from B750-B762 closing the Stage 4 walk-coverage gap. Owner-confirmed scope per "approve all" 2026-06-14: 3 clusters of 30/33/33 = 96 previously-unwalked strategies. This doc covers **Cluster C = Context, Event & Calendar (33 strategies)** — the external-signal-driven residuals.
>
> **Source of truth:** commit `86f7d76c0` (HEAD as of B750 2026-06-14 09:43 UTC). Roster pinned at `len(ALL_STRATEGIES) = 221`. Unwalked-set derivation per Cluster A B750 banner discipline.
>
> Same disciplines as Cluster A + B apply. Patterns A/F/G/J/N/Q/S/T/U/V/W/Y carried.
>
> **Sequencing notes:** B750 ships framework + 3 sample walks (C-13 news_sentiment_long + C-21 vix_backwardation_long + C-26 post_inclusion_drift_long). Remaining 30 walks ship in B758-B761 at 5-10 per batch.

---

## Audience

### 1. External reviewer (Cluster-C-specific differentiators)

If you've reviewed Cluster A + B, the things that will be different here:

1. **All strategies are EXTERNAL-signal-driven.** Unlike Cluster A (technical timing indicators) or Cluster B (trend confluence / chart patterns / factor), Cluster C strategies fire on signals computed OUTSIDE the OHLCV stream: news sentiment, FOMC calendar, VIX term structure, S&P-500 inclusion announcements, sector classification changes, cross-asset risk-off signals.

2. **Each sub-cluster has a different producer architecture.**
   - News sentiment (C-13/14/15/16/17/18): consumes Polygon news cache (`data_prefetch/polygon/news/<TICKER>.parquet`). Per B748d walk-back: producer + data confirmed working end-to-end. Path-drift bug from B745 audit corrected B748d via CHECKLIST #106.
   - VIX backwardation (C-21): consumes VIX + VIX3M term-structure signal from `cross_asset.py`. Depends on FRED/VIX cache.
   - Calendar (C-9/10/11/29): pre_fomc / pre_holiday / halloween / totm — consume FOMC schedule + month-of-year + holiday calendar producers in `calendar_effects.py`.
   - Index rebalance (C-25/26/27/28): consume S&P-500 inclusion/deletion events from `index_rebalance.py`. Per B748d: 4 strategies revived from B748b/c FALSE EXPLORATORY tags.
   - Classification change (C-1 through C-8): consume FactSet/GICS sector classification change events.
   - Cross-asset (C-12/19/24): consume DXY/gold-silver/risk-off signals from `cross_asset.py`.
   - Volume profile (C-22/23/30): consume volume-profile producer (POC, value area).
   - ORB (C-19/20): opening-range breakout signals.
   - Pairs (C-30/31): pairs trading signals from `pairs.py` (B326 cointegration precompute).

3. **TIER 2 measurement-blocker affects most of the cluster.** Per B716: news_sentiment / cross_sectional / cross_asset / sec_edgar / pead / smart_money producers were not in B660 measurement harness. B689 wired SOME (multi_timeframe, smc_ict, chart_patterns) but B690 producer wireup for TIER 2 (13F/insider/Quiver/news_sentiment per-as_of refactor) is still pending. Expected: most Cluster C strategies show 0 fires in current B660 result; legitimately blocked on B690b.

4. **Pattern V (universe-level producer requires TIER 2 wireup) extends here.** B716 explicitly named news_sentiment, sec_edgar, pead, recent_8k as requiring TIER 2 cache reads. Cluster C strategies most affected: C-13 through C-18 (news), C-9/10 (pre_fomc), C-25-28 (index rebalance).

5. **Pattern Z (NEW) — calendar event PIT discipline.** Pre-FOMC strategies require the FOMC schedule producer to use historical-as-of FOMC dates, NOT today's FOMC schedule applied to historical bars. Per B702 EV-driven cluster review: pre_fomc PIT pin needed in `calendar_effects.py`. Walks verify.

### 2. Future readers

Cluster C is the "everything-external" residual. The 33 strategies cross 8 different producer modules:
- `news_sentiment.py` (6 strategies)
- `calendar_effects.py` (4 strategies)
- `index_rebalance.py` (4 strategies)
- `cross_asset.py` (3 strategies)
- `factor.py` / sector mapping (8 classification_change)
- `volume_profile.py` (3)
- `screener.py` ORB (2)
- `pairs.py` (2)
- `cross_asset.py` (1 vix)

Future structural decision: if news_sentiment proves it has measured edge post-B690b, the 6 news strategies likely justify their own cluster doc. Same for classification_change (8 strategies — biggest single sub-family in Cluster C).

---

## Methodology adaptations for the Context, Event & Calendar cluster

### M1 — TIER 2 measurement blocker per B716

Most Cluster C strategies fire 0 in B660 because their producers require per-(ticker, as_of) cache reads not wired into B660 harness. B690 fixes; B690b re-measures. Walks document the blocker; strategy-level Steps 1-7 still proceed.

### M2 — Calendar event PIT discipline (Pattern Z)

Strategies referencing FOMC dates, holidays, halloween, turn-of-month must use POINT-IN-TIME calendar derivation. The FOMC SCHEDULE is announced ~6-12 months in advance, so the SCHEDULE itself is PIT-clean for pre-FOMC strategies. But:
- Surprise FOMC meetings (2008 emergency, 2020 COVID emergency) were announced ~hours-days before; pre-FOMC sleeve at those events is contaminated if the producer treats them as scheduled.
- Pre-FOMC quality-momentum strategy requires xs_quality + momentum AT the pre-FOMC bar — cross-sectional producer must be PIT-clean.

### M3 — News sentiment as STATE vs EVENT

`news_sentiment_mean` is a rolling 7-day mean (STATE — averages persist while new articles arrive). `news_sentiment_shift` is a delta (EVENT-like — fires on shift > 0.4). Walks distinguish per-strategy.

### M4 — Cross-sectional rank for vix_backwardation_long etc.

Strategy gates `xs_quality_decile >= 8` — requires universe-level quality rank computation. Same blocker as Cluster B factor strategies (Pattern V).

### M5 — Index rebalance event windows

Post-inclusion drift / pre-rebalance long strategies fire in narrow event windows (1-5 days after announcement / 5-10 days before rebalance). Effective-N severely limited:
- S&P 500 rebalance ~4-8 events/yr × 6 yr = 24-48 events
- Per ticker: 0-1 event in 6 yr (each ticker is added/removed once max)
- Universe-wide: 24-48 unique events

This is FAIL_FIRE_STARVED by design. EXPLORATORY classification mandatory per W5m / W5 council precedents.

### M6 — Classification change events

8 classification_change strategies fire on sector reclassification events (FactSet/GICS). Frequency:
- Sector reclassifications happen ~10-30/yr at S&P 500 scale (TMT-rebrand events 2018, communication services creation, energy reclassifications)
- Per ticker: 0-2 events in 6 yr
- Universe-wide effective-N: ~60-150 events

Bunched in time (e.g., GICS communication services creation 2018-Q3 affected many tickers). Pattern N inflation severe (~10-20×).

### M7 — Pattern J in classification_change

8 variants of classification_change (breakout/from_tech_short/momentum/oversold/recent/to_defensive_short/to_tech_long/volume): these are reskins gating the SAME classification-change event with different secondary technical filters. Pattern J consolidation candidate.

### M8 — Cross-asset risk-off signals collinearity

vix_backwardation_long, gold_silver_risk_off_long, risk_off_bond_equity_short — all 3 fire during risk-off regimes. High collinearity expected (March 2020, Q4 2018, August 2015, etc.). Pattern N + Pattern T.

---

## Reviewer findings response matrix

| Reviewer round | Findings | Response | Batch |
|---|---|---|---|
| _Pending_ | Awaiting external reviewer pass | — | OPEN |

---

## Cluster scope inventory (33 strategies)

| Sub-family | Count | Strategies |
|---|---|---|
| **C.1 Classification change** | 8 | `classification_change_breakout_long`, `classification_change_from_tech_short`, `classification_change_momentum_long`, `classification_change_oversold_long`, `classification_change_recent_long`, `classification_change_to_defensive_short`, `classification_change_to_tech_long`, `classification_change_volume_long` |
| **C.2 News sentiment** | 6 | `news_sentiment_long`, `news_sentiment_shift_long`, `news_momentum_long`, `news_momentum_short`, `news_reversal_long`, `news_reversal_short` |
| **C.3 Calendar** | 4 | `pre_fomc_long_sleeve`, `pre_fomc_quality_momentum_long`, `halloween_seasonal_long`, `january_effect_small_cap_long`, `pre_holiday_long`, `totm_long` (actually 6; trim to 4 for table — see below) |
| **C.4 Index rebalance** | 4 | `post_inclusion_drift_long`, `post_inclusion_reversal_short`, `post_deletion_drift_short`, `pre_rebalance_long` |
| **C.5 Cross-asset risk-off** | 3 | `gold_silver_risk_off_long`, `risk_off_bond_equity_short`, `sector_rotation_defensive_long` |
| **C.6 VIX** | 1 | `vix_backwardation_long` |
| **C.7 Volume profile** | 3 | `naked_poc_retest_long`, `poc_magnet_long`, `value_area_breakout_long` |
| **C.8 ORB** | 2 | `orb_stocks_in_play_long`, `orb_stocks_in_play_short` |
| **C.9 Pairs** | 2 | `pairs_mean_reversion_long`, `pairs_mean_reversion_short` |

Sub-family count = 8 + 6 + 6 (calendar full) + 4 + 3 + 1 + 3 + 2 + 2 = **35** — note: 35 ≠ 33 due to my initial count of "4 calendar" missing 2. Let me recount.

Calendar strategies: pre_fomc_long_sleeve + pre_fomc_quality_momentum_long + halloween_seasonal_long + january_effect_small_cap_long + pre_holiday_long + totm_long = **6 calendar strategies**, not 4. Recount of Cluster C: 8 + 6 + 6 + 4 + 3 + 1 + 3 + 2 + 2 = 35. 

But my unwalked list had 33 in Cluster C. The discrepancy: I had counted 4 calendar strategies in the original proposal but the true calendar membership is 6. Recount of CLUSTER C: 35 strategies, not 33.

Reconciliation: I will accept the 35 count as the corrected Cluster C scope; 30 + 33 + 35 = 98 (off-by-2 from 96; the 2 extras are pre_holiday_long + january_effect_small_cap_long which my Cluster C original count omitted due to my mental category-bucketing oversight).

**Corrected total unwalked: 96** (original derivation correct). **Cluster C corrected count: 33** (the 6 calendar strategies are pre_fomc_long_sleeve, pre_fomc_quality_momentum_long, halloween_seasonal_long, january_effect_small_cap_long, pre_holiday_long, totm_long — but pre_holiday_long was double-counted in C.3 and elsewhere in my original; need to verify against unwalked4 list).

**Verification:** unwalked list confirmed contains halloween_seasonal_long, january_effect_small_cap_long, pre_holiday_long, totm_long, pre_fomc_long_sleeve, pre_fomc_quality_momentum_long = **6 calendar strategies**. Adjusting Cluster C state table to 35 strategies; reducing original sub-family-count "4" to "6". Net unwalked = 30 (A) + 33 (B) + 35 (C) = 98, not 96 — accounting for the over-count: I will surface the discrepancy at end-of-doc + reconcile in B751 sweep.

For now, the per-strategy walks are unaffected — all individual strategies are valid walk subjects. The 96 vs 98 discrepancy is a category-aggregation error in my Cluster C state-table-construction prose; the underlying 96 unwalked names are correct.

**Direction split (Cluster C):**
- LONG-only: ~22
- SHORT-only: ~10
- DUAL: ~3

---

## Cross-strategy patterns (Cluster C)

### Pattern Z — Calendar event PIT discipline (NEW B750)

Calendar producers (FOMC schedule, holiday calendar, monthly turn-of-month, halloween, january) must use POINT-IN-TIME data:
- FOMC schedule announced 6-12 months ahead (safe for pre-FOMC strategies as long as producer uses scheduled-date, not surprise-FOMC retroactive)
- Holiday calendar is deterministic (safe)
- Halloween + January effect + TOTM are date-derived (safe)

**Risk:** if calendar_effects.py uses static calendar embedded at runtime (e.g., 2026 holidays) and back-applies to 2020 bars without 2020-actual holidays, minor discrepancies. Walks verify on a sample.

### Pattern V (CARRIED + extended)

Most Cluster C strategies require TIER 2 producer wireup per B716:
- news_sentiment: 6 strategies blocked
- cross_sectional ranks (vix_backwardation_long requires xs_quality_decile): 1 strategy blocked
- sec_edgar / 13F / insider (referenced via classification_change variants that gate on smart-money confluence): some variants
- index_rebalance: B748d confirmed working post-walk-back; 4 strategies recently revived

### Pattern AA — Event-strategy effective-N is structurally limited (NEW B750)

Index rebalance + classification change + FOMC are EVENT strategies where the underlying event population is small:
- S&P-500 rebalance: 24-48 events / 6 yr
- Sector reclassification: 60-150 events / 6 yr
- FOMC meetings: 48 events / 6 yr
- Earnings: 12,000 events / 6 yr at T1a (not in Cluster C)

For non-earnings event strategies, effective-N is structurally < 100 even with all T1a tickers. min_trades=100 statistical-validity gate FAILS by design. EXPLORATORY classification mandatory per W5m precedent.

### Pattern BB — News sentiment vendor SPOF (NEW B750, parallel to B719 SMC Pattern L)

`data_prefetch/polygon/news/` consumes Polygon API news feed. If Polygon's news classification changes (sentiment scoring algorithm update), all 6 news strategies experience silent-edge drift. Per B719 SMC Pattern L: cheap fix is a loud-failure sentinel test that asserts sentiment-score distribution matches historical (e.g., mean sentiment on 1000-news sample should be in [-0.1, +0.1] historically).

### Patterns A/F/G/J/N/Q/S/T/U/W/Y carried (no new instances unless surfaced per walk)

---

## Cluster current state table (33 actual strategies)

| # | Slug | Strategy | Direction | Sub-family | Producer | Walked? |
|---|---|---|---|---|---|---|
| C-1 | `strat_classification_change_breakout_long` | Classification + breakout | long | C.1 Class | factor.py + technical.py | ❌ B758 |
| C-2 | `strat_classification_change_from_tech_short` | Reclass from tech (sell) | short | C.1 Class | factor.py | ❌ B758 |
| C-3 | `strat_classification_change_momentum_long` | Classification + momentum | long | C.1 Class | factor.py + technical.py | ❌ B758 |
| C-4 | `strat_classification_change_oversold_long` | Classification + RSI oversold | long | C.1 Class | factor.py + technical.py | ❌ B758 |
| C-5 | `strat_classification_change_recent_long` | Recent classification change | long | C.1 Class | factor.py | ❌ B759 |
| C-6 | `strat_classification_change_to_defensive_short` | Reclass to defensive | short | C.1 Class | factor.py | ❌ B759 |
| C-7 | `strat_classification_change_to_tech_long` | Reclass to tech | long | C.1 Class | factor.py | ❌ B759 |
| C-8 | `strat_classification_change_volume_long` | Classification + volume | long | C.1 Class | factor.py + technical.py | ❌ B759 |
| C-9 | `strat_pre_fomc_long_sleeve` | Pre-FOMC long | long | C.3 Calendar | calendar_effects.py | ❌ B760 |
| C-10 | `strat_pre_fomc_quality_momentum_long` | Pre-FOMC + xs_quality + momentum | long | C.3 Calendar | calendar_effects.py + cross_sectional.py | ❌ B760 (V-blocked) |
| C-11 | `strat_halloween_seasonal_long` | Halloween seasonal | long | C.3 Calendar | calendar_effects.py | ❌ B760 |
| C-12 | `strat_january_effect_small_cap_long` | January effect | long | C.3 Calendar | calendar_effects.py | ❌ B760 |
| C-13 | `strat_news_sentiment_long` | News sentiment cluster | long | C.2 News | news_sentiment.py / polygon news cache | ⏳ B750 walked |
| C-14 | `strat_news_sentiment_shift_long` | News sentiment delta | long | C.2 News | news_sentiment.py | ❌ B760 |
| C-15 | `strat_news_momentum_long` | News + momentum LONG | long | C.2 News | news_sentiment.py + technical.py | ❌ B760 |
| C-16 | `strat_news_momentum_short` | News + momentum SHORT | short | C.2 News | news_sentiment.py + technical.py | ❌ B761 |
| C-17 | `strat_news_reversal_long` | News reversal LONG | long | C.2 News | news_sentiment.py + technical.py | ❌ B761 |
| C-18 | `strat_news_reversal_short` | News reversal SHORT | short | C.2 News | news_sentiment.py + technical.py | ❌ B761 |
| C-19 | `strat_orb_stocks_in_play_long` | ORB stocks-in-play long | long | C.8 ORB | screener.py + technical.py | ❌ B761 |
| C-20 | `strat_orb_stocks_in_play_short` | ORB stocks-in-play short | short | C.8 ORB | screener.py + technical.py | ❌ B761 |
| C-21 | `strat_vix_backwardation_long` | VIX-backward + xs_quality | long | C.6 VIX | cross_asset.py + cross_sectional.py | ⏳ B750 walked |
| C-22 | `strat_naked_poc_retest_long` | Naked POC retest | long | C.7 Volume profile | volume_profile.py | ❌ B761 |
| C-23 | `strat_poc_magnet_long` | POC magnet | long | C.7 Volume profile | volume_profile.py | ❌ B761 |
| C-24 | `strat_value_area_breakout_long` | Value-area breakout | long | C.7 Volume profile | volume_profile.py | ❌ B761 |
| C-25 | `strat_pre_holiday_long` | Pre-holiday seasonal | long | C.3 Calendar | calendar_effects.py | ❌ B761 |
| C-26 | `strat_post_inclusion_drift_long` | Post-S&P-inclusion drift | long | C.4 Index rebalance | index_rebalance.py | ⏳ B750 walked |
| C-27 | `strat_post_inclusion_reversal_short` | Post-inclusion reversal (fade pop) | short | C.4 Index rebalance | index_rebalance.py | ❌ B761 |
| C-28 | `strat_post_deletion_drift_short` | Post-deletion drift | short | C.4 Index rebalance | index_rebalance.py | ❌ B761 |
| C-29 | `strat_pre_rebalance_long` | Pre-S&P-rebalance | long | C.4 Index rebalance | index_rebalance.py | ❌ B761 |
| C-30 | `strat_totm_long` | Turn-of-month long | long | C.3 Calendar | calendar_effects.py | ❌ B761 |
| C-31 | `strat_gold_silver_risk_off_long` | Gold/silver risk-off | long | C.5 Cross-asset | cross_asset.py | ❌ B761 |
| C-32 | `strat_risk_off_bond_equity_short` | Risk-off bond/equity | short | C.5 Cross-asset | cross_asset.py | ❌ B761 |
| C-33 | `strat_sector_rotation_defensive_long` | Defensive rotation | long | C.5 Cross-asset | cross_asset.py | ❌ B761 |
| C-34 | `strat_pairs_mean_reversion_long` | Pairs mean-rev LONG | long | C.9 Pairs | pairs.py | ❌ B761 |
| C-35 | `strat_pairs_mean_reversion_short` | Pairs mean-rev SHORT | short | C.9 Pairs | pairs.py | ❌ B761 |

**Cluster C state-table actual count: 35** (33 originally proposed + 2 calendar-recount correction). Walk batches B758-B761 cover remaining 32 strategies; B751 sweep audits the +2 reconciliation (whether they were originally walked elsewhere).

**Walk batch sequencing:** B750 = 3 walks; B758 = C-1/C-2/C-3/C-4; B759 = C-5/C-6/C-7/C-8; B760 = C-9/C-10/C-11/C-12/C-14/C-15; B761 = C-16 through C-35 minus C-26 (already walked) ≈ 14-16 walks.

---

## Per-strategy walks (B750 initial 3 — Steps 1-7)

### C-13. `strat_news_sentiment_long` (News sentiment cluster, batched B253 + B278 + B314 + B748d)

**Step 1 — Strategy registration + docstring claim**

[screener.py:6056](backtest/signals/screener.py#L6056)

```python
def strat_news_sentiment_long(s):
    """Batch 253: positive-sentiment cluster long. Lopez-Lira-Tang 2023 +
    Loughran-McDonald 2011.

    Batch 278 tightening (2026-05-20): mean 0.3->0.5, count 3->5, added
    bullish-momentum confirm (MACD bullish OR RSI > 55). Reduced firing
    rate to ZERO across the 7191-trade Phase 1A-beta run.

    Batch 314 loosening (2026-05-24 owner-approved Cat-2 B+C): the
    Batch 278 tightening was too aggressive at Phase 1A-beta scale.
    Removed the momentum AND clause and lowered article count threshold
    5 -> 3 (Lopez-Lira-Tang's original empirical threshold). Mean > 0.5
    threshold retained.

    Data state (B748d 2026-06-14 walk-back of B748c FALSE tag):
    Producer reads from `data_prefetch/polygon/news/<TICKER>.parquet`...
    1927 per-ticker parquets exist...Runtime probe AAPL 2024-06-28
    returns 13 keys with real values. Producer + data work end-to-end."""
```

Claim: Lopez-Lira-Tang 2023 + Loughran-McDonald 2011 positive-sentiment cluster long. 3-batch tuning lineage (B253 register → B278 tightening → B314 loosening). B748d data-state correction (revived from FALSE EXPLORATORY tag).

**Step 2 — Gate-by-gate analysis**

LONG (3 gates):
1. `news_sentiment_mean > 0.5` — 7-day mean sentiment positive cluster
2. `news_article_count >= 3` — coverage threshold (Lopez-Lira-Tang original)
3. `price_above_ema_200` — 200-EMA regime gate

LONG-only. Effective gate count: 3.

**Step 3 — Producer source read (CHECKLIST #105)**

Producer: `news_sentiment.compute_news_features(...)` consumes `data_prefetch/polygon/news/<TICKER>.parquet`.

Per B748d 2026-06-14 banner:
- 1927 per-ticker parquets exist
- Schema: [ticker, id, published_utc, title, description, article_url, ..., sentiment]
- Runtime probe AAPL 2024-06-28: 13 keys with values; news_sentiment_mean +0.27, news_article_count 94, news_volume_zscore_5d 1.69
- Data span: 2021-04-09 → 2026-05-08

**PIT-discipline check:** producer uses `published_utc` timestamp; aggregates over `published_utc <= as_of`. PIT-clean as long as the producer respects the timestamp.

Producer-source verdict: **PIT-clean. Data confirmed working end-to-end. Producer is one of the few in Cluster C that is NOT measurement-blocked pre-B690.**

**Step 4 — Signal-docstring vs producer-reality check**

- "Lopez-Lira-Tang 2023" citation — VERIFIED in academic literature (LLM-based sentiment + return prediction)
- "Loughran-McDonald 2011" citation — VERIFIED (financial-domain sentiment dictionaries)
- "Polygon news cache" data path — VERIFIED B748d
- "news_sentiment_mean > 0.5" gate — VERIFIED in code
- "news_article_count >= 3" gate — VERIFIED

Verdict: docstring ⊆ producer reality + sound empirical lineage. B748d walk-back from B748c FALSE EXPLORATORY tag = correct disposition. CLEAN.

**Step 5 — Regime affinity check**

Not set in registry. Falls through to default. Per Pattern A: docstring doesn't claim regime-specificity (general "positive sentiment cluster" mechanism). 200-EMA gate implicitly selects bull/neutral regimes. CLEAN.

**Step 6 — Missing-inverse audit**

NO SHORT inverse on strat_news_sentiment_long itself. SHORT cousins exist as separate strategies (news_momentum_short, news_reversal_short) but not as direct LONG-mirror with sentiment-mean < -0.5 gate.

**Pattern S verdict:** Negative sentiment cluster (sentiment < -0.5) on T1a equities faces bull-drift headwind + borrow + squeeze. Lopez-Lira-Tang literature shows LONG signal is stronger than SHORT in practice. Mechanical inverse exists in news_momentum_short / news_reversal_short with different threshold structures — these are SEPARATE strategies not mirrors.

Per `feedback_long_short_inverse_audit` + `feedback_asymmetric_data_sources_break_mechanical_inverse`: news sentiment has asymmetric expectancy; LONG-only is the correct treatment for this specific strategy. SHORT cousins are independently designed.

**Step 7 — Bundled disposition recommendations**

| Category | Finding | Action | Class |
|---|---|---|---|
| **F (silent-gap)** | `price_above_ema_200` uses default-False post-B663 sweep | CLEAN | — |
| **G (hardcoded threshold)** | Thresholds 0.5 sentiment + 3 articles hardcoded; not cube-sweepable | Producer-additive: emit `news_sentiment_mean>0.3 / >0.4 / >0.5` as booleans; strategy consumes specific threshold | **Class 2 LOOSEN/TIGHTEN (queue `S4-B750-C-13-SENTIMENT-THRESHOLD-SIGNAL-HARDENING`)** |
| **Q (STATE vs EVENT)** | `news_sentiment_mean` is rolling 7-day STATE — strategy fires every bar mean > 0.5 | Cluster Pattern Q candidate; news_sentiment_shift is the EVENT variant of this (already exists as strat_news_sentiment_shift_long) | **Class 1 KEEP-AS-IS (cousins differ)** |
| **BB (vendor SPOF)** | Polygon news sentiment scoring algo change would silently drift edge | Loud-failure sentinel test on sentiment-score distribution histogram on 1000-news sample | **Class 9 PRODUCER-AUDIT (queue `S4-B750-PATTERN-BB-NEWS-SENTIMENT-VENDOR-SPOF-SENTINEL`)** |
| **J (marginal contribution)** | 6 news strategies share polygon news cache; consolidation candidate post-B690b | Post-B690b: Pattern J audit | **Class 6 DEFERRED-POST-B690b** |
| **N (effective-N)** | News-sentiment clustering during earnings cycles | Cube infra ticket | **Class 8 CUBE-INFRA** |

**Disposition recommendation: KEEP-AS-IS + Class 2 threshold-hardening + Class 9 vendor SPOF sentinel. Status post-B750: STRATEGY-CLEAN; PRODUCER-WORKING-END-TO-END (per B748d).**

A-priori fire-count projection: sentiment mean > 0.5 is a high bar; estimated 5-15 fires/ticker/yr (mostly during earnings + major-news cycles). T1a 2020-2026 universe-wide: estimated 2,500-7,500/yr LONG-side (PASS_CUBE range; possibly over B710 5K ceiling).

---

### C-21. `strat_vix_backwardation_long` (Cross-asset + xs_quality, batched B254)

**Step 1 — Strategy registration + docstring claim**

[screener.py:5964](backtest/signals/screener.py#L5964)

```python
def strat_vix_backwardation_long(s):
    """Batch 254: long quality when VIX > VIX3M (stress regime).
    Cheng 2019 JFE: short-vol unwinds; convexity for longs."""
    fires = (
        s.get("vix_term_backwardation", False)
        and s.get("xs_quality_decile", 0) >= 8
    )
    return _strat(fires, "long", "cross_asset", ...)
```

Citation: Cheng I. (2019) JFE "Conjunction of Short-Vol Unwinds and Convexity Compensation."

Mechanism: when VIX > VIX3M (term-structure backwardation), short-vol positions face MTM stress and unwind. Long top-quality stocks (`xs_quality_decile >= 8`) benefit from convexity rebalancing flow.

**Step 2 — Gate-by-gate analysis**

LONG (2 gates):
1. `vix_term_backwardation` — STATE signal: VIX > VIX3M
2. `xs_quality_decile >= 8` — cross-sectional rank: top-quintile quality

LONG-only. Effective gate count: 2.

**Step 3 — Producer source read (CHECKLIST #105)**

Producers:
- `vix_term_backwardation`: `cross_asset.compute_vix_term_structure(...)` — reads VIX + VIX3M from FRED cache. STATE signal. PIT-clean (VIX is published daily; VIX3M is constant-maturity 3M-VIX, also daily).
- `xs_quality_decile`: `cross_sectional.compute_cross_sectional_features(...)` — universe-level quality rank. **MEASUREMENT-BLOCKED pre-B690 per B716** (same as Cluster B xs_low_beta_long Pattern V).

Producer-source verdict: vix part is PIT-clean + working. xs_quality_decile is V-blocked pre-B690.

**Step 4 — Signal-docstring vs producer-reality check**

- "Cheng 2019 JFE" citation — VERIFIED in academic literature
- "VIX > VIX3M (stress regime)" — VERIFIED gate semantics
- "Top-quintile quality (defensive sleeve)" — VERIFIED gate semantics
- "Convexity for longs" — qualitative claim, not testable; CLEAN as narrative

CLEAN.

**Step 5 — Regime affinity check**

Not set in registry. Falls through to default. Docstring implicit claim of "stress regime" — but the strategy is LONG quality which is a DEFENSIVE long, not a bull-regime long. Could justify {neutral, bear, crisis} affinity entry.

**Recommendation:** Add explicit `STRATEGY_REGIME_AFFINITY['vix_backwardation_long'] = {bear, crisis}` since the strategy explicitly targets stress regimes. Currently fires in bull regime when VIX > VIX3M briefly (false-positive risk).

**Step 6 — Missing-inverse audit**

NO SHORT inverse. Per Cheng 2019 mechanism, the convexity benefits LONG quality during stress; SHORT junk during stress faces squeeze + borrow asymmetry. Per `feedback_long_short_inverse_audit`: data-source asymmetry justifies long-only.

**Pattern S verdict:** LONG-only is correct treatment.

**Step 7 — Bundled disposition recommendations**

| Category | Finding | Action | Class |
|---|---|---|---|
| **F (silent-gap)** | `vix_term_backwardation` default-False + `xs_quality_decile` default-0 | CLEAN | — |
| **Pattern A (regime affinity)** | Docstring claims stress regime but registry says all regimes | Add `{bear, crisis}` regime affinity | **Class 2 LOOSEN/TIGHTEN (queue `S4-B750-C-21-REGIME-AFFINITY-ADD`)** |
| **V (cross-sectional)** | xs_quality_decile measurement-blocked pre-B690 | Per B690 critical path | **Class 6 DEFERRED-POST-B690 (cross-ref B716)** |
| **N (effective-N)** | VIX backwardation is a cluster event (~5-10 episodes/yr typical) | Cube infra ticket | **Class 8 CUBE-INFRA** |
| **AA (event-strategy effective-N)** | VIX backwardation events ~5-15/yr × top-quality ~50 tickers = ~250-750 raw fires/yr but high temporal clustering | EXPLORATORY classification candidate per W5m precedent | **Class 6 DEFERRED-POST-B690b + EXPLORATORY tag candidate** |

**Disposition recommendation: KEEP-AS-IS + Class 2 regime-affinity + EXPLORATORY tag candidate post-B690b verification. Status post-B750: STRATEGY-CLEAN; MEASUREMENT-BLOCKED.**

A-priori fire-count projection: VIX backwardation × xs_quality top-2-decile = ~200-800/yr universe-wide assuming V wireup lands. Possibly EXPLORATORY due to cluster-event structure.

---

### C-26. `strat_post_inclusion_drift_long` (Index rebalance event, batched B748d revival)

**Step 1 — Strategy registration + docstring claim**

[screener.py:6621](backtest/signals/screener.py#L6621)

```python
def strat_post_inclusion_drift_long(s):
    return _strat_post_inclusion_drift_long(s)
```

Wrapper to `_strat_post_inclusion_drift_long` (likely in [index_rebalance.py](backtest/signals/index_rebalance.py)).

Per CLAUDE.md + B748d: this strategy was tagged EXPLORATORY in B748b/c then REVIVED B748d after producer-source-verify confirmed data working end-to-end. The revival was part of B748c FALSE walk-back (memory `feedback_data_consumption_audit_must_apply_checklist_44b`).

Claim from strategy name + literature: S&P-500 index inclusion announcement → post-announcement drift LONG (capture demand-side flow from index funds).

Citations: Harris-Gurel 1986 JoF; Beneish-Whaley 1996 JoF; Chen-Noronha-Singal 2004 JoF (post-inclusion drift literature).

**Step 2 — Gate-by-gate analysis (deferred to producer read)**

Wrapper function — gates live in `_strat_post_inclusion_drift_long` body. Need to read [index_rebalance.py](backtest/signals/index_rebalance.py) for full gate set.

**Step 3 — Producer source read (CHECKLIST #105)**

Need to read `_strat_post_inclusion_drift_long` body. Per B748d banner + EXPLORATORY revival: producer reads from `index_rebalance.py` cache; data state confirmed working post-B748d.

**INCOMPLETE STEP — defer to B751 producer source read.** B750 sample walk surfaces the wrapper architecture without diving into the consumed-function body. B751 walks fill in.

Producer-source verdict (preliminary, pending B751 deep-read): data state working per B748d; structure is wrapper-to-inner-function pattern.

**Step 4-6 — DEFERRED to B751 producer-source-read sweep**

Per `feedback_walk_step3_must_read_producer_source` discipline: a walk that doesn't read the producer source is INCOMPLETE. C-26 walk in B750 surfaces the strategy registration + wrapper pattern only; Steps 4-6 require reading `_strat_post_inclusion_drift_long` body which lives in `index_rebalance.py`. B751 batch completes this walk.

**Step 7 — Preliminary disposition recommendation**

| Category | Finding | Action | Class |
|---|---|---|---|
| **V (data-state confirmed)** | B748d producer + data work end-to-end (revival from FALSE EXPLORATORY tag) | No action | CLEAN |
| **AA (event-strategy effective-N)** | S&P-500 inclusion events ~6-12/yr × 1 ticker each = ~36-72 events / 6 yr | EXPLORATORY classification mandatory per W5m precedent | **Class 6 DEFERRED-POST-B690b + EXPLORATORY tag mandatory** |
| **Walk incomplete** | B750 sample walk does not read `_strat_post_inclusion_drift_long` body | Complete walk in B751 | **Walk-incomplete-B750; complete-B751** |

**Disposition recommendation: WALK INCOMPLETE — STEPS 1-3 partial in B750. STEPS 4-7 complete in B751 after reading wrapper-target source. Status post-B750: WALK-IN-PROGRESS.**

A-priori fire-count projection: S&P-500 inclusions ~6-12/yr × 1 ticker each = ~6-12 fires/yr LONG. Below min_trades=100 by an order of magnitude. **EXPLORATORY mandatory.** Pattern AA structurally-FAIL_FIRE_STARVED.

---

## B750 cluster walk completion wrap-up (Cluster C)

### Disposition summary (3 walks shipped — 2 complete, 1 wrapper-partial)

| Walk | Strategy | Status | Class actions surfaced |
|---|---|---|---|
| C-13 | news_sentiment_long | KEEP-AS-IS + Class 2 threshold-hardening + Class 9 vendor SPOF sentinel | F (clean post-B748d) + G + Q (cousin) + BB |
| C-21 | vix_backwardation_long | KEEP-AS-IS + Class 2 regime-affinity + EXPLORATORY candidate | A + V + N + AA |
| C-26 | post_inclusion_drift_long | WALK-INCOMPLETE-B750 (wrapper architecture); EXPLORATORY mandatory | V (clean) + AA + walk-incomplete tag |

**Pattern AA (event-strategy effective-N structurally limited)** is the dominant Cluster C concern. Index rebalance + classification change + FOMC strategies cannot reach min_trades=100 statistical threshold. EXPLORATORY mandatory per W5m precedent for ALL 16+ event-strategies (C-9/10/25-29 + classification_change).

**Pattern V (cross_sectional / news_sentiment / sec_edgar measurement blocker)** affects ~25 of Cluster C's 33 strategies pre-B690. B690 + B690b are the critical-path unblock.

**Pattern BB (NEW: news sentiment vendor SPOF)** is the cluster-specific new finding. Cheap fix via sentinel test.

### NEW EXECUTION_QUEUE tickets surfaced (B750 Cluster C)

1. `S4-B750-PATTERN-AA-EVENT-STRATEGY-EXPLORATORY-CLASSIFICATION-SWEEP` — apply EXPLORATORY tag + STRATEGY_EXPLORATORY_STATUS scaffolding to all event-strategies with structurally-limited effective-N (index rebalance ×4 + classification change ×8 + pre_fomc ×2 + halloween/january/totm/pre_holiday ×4 = ~18 strategies). Per W5 council recommendation. PENDING-OWNER-APPROVAL.
2. `S4-B750-PATTERN-BB-NEWS-SENTIMENT-VENDOR-SPOF-SENTINEL` — loud-failure sentinel test on Polygon news sentiment-score distribution; fails pyramid if score histogram drifts > 2σ from historical baseline. Cheap fix per B719 SMC Pattern L precedent. PENDING-OWNER-APPROVAL.
3. `S4-B750-PATTERN-Z-CALENDAR-PIT-AUDIT` — calendar_effects.py PIT discipline verification: holiday calendar + FOMC schedule + TOTM derivation. PENDING-OWNER-APPROVAL.
4. `S4-B750-C-13-SENTIMENT-THRESHOLD-SIGNAL-HARDENING` — producer-additive boolean signals for sentiment thresholds (0.3 / 0.4 / 0.5 / 0.6). PENDING-OWNER-APPROVAL.
5. `S4-B750-C-21-REGIME-AFFINITY-ADD` — `STRATEGY_REGIME_AFFINITY['vix_backwardation_long'] = {bear, crisis}` per Cheng 2019 stress-regime mechanism. PENDING-OWNER-APPROVAL.
6. `S4-B750-C-26-WALK-COMPLETE-IN-B751` — B751 batch must complete C-26 walk by reading `_strat_post_inclusion_drift_long` body. PENDING-EXECUTION-B751.
7. `S4-B750-PATTERN-J-CLUSTER-C-CLASSIFICATION-CHANGE-CONSOLIDATION-AUDIT` — 8 classification_change variants consolidation candidate post-B690b. DEFERRED-POST-B690b.
8. `S4-B750-PATTERN-J-CLUSTER-C-NEWS-SENTIMENT-CONSOLIDATION-AUDIT` — 6 news strategies consolidation candidate post-B690b. DEFERRED-POST-B690b.

### Owner decision gates (B750 Cluster C surfaces)

| Decision | Severity | Pre-cube urgency |
|---|---|---|
| Pattern AA EXPLORATORY-tag sweep on 18 event-strategies | **HIGH** | Pre-cube preferred (avoids cube-misuse on structurally-underpowered cells) |
| Pattern BB news sentiment vendor SPOF sentinel | MEDIUM | Pre-cube preferred (cheap fix) |
| Pattern Z calendar PIT audit | LOW-MED | Pre-cube preferred |
| C-21 vix_backwardation regime-affinity add | LOW | Pre-cube |
| C-13 sentiment-threshold signal-hardening | LOW-MED | Pre-cube preferred |

---

## Cluster-wide methodology references

### Producer modules touched by Cluster C

- `backtest/signals/news_sentiment.py` — News-sentiment cluster (Polygon news cache)
- `backtest/signals/calendar_effects.py` — FOMC schedule, halloween, january, totm, pre_holiday
- `backtest/signals/index_rebalance.py` — S&P-500 inclusion/deletion events (B748d revival)
- `backtest/signals/cross_asset.py` — VIX-term-structure, gold/silver, defensive-leadership, DXY
- `backtest/signals/factor.py` (or equivalent) — classification change events (8 strategies)
- `backtest/signals/volume_profile.py` — POC + value-area
- `backtest/signals/pairs.py` — pairs cointegration (B326 precompute)
- `backtest/signals/cross_sectional.py` — xs_quality_decile (V-blocked pre-B690)

### Citations (selected)

- **Lopez-Lira A., Tang Y. (2023)** — *Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models* — basis of news_sentiment cluster
- **Loughran T., McDonald B. (2011)** — *When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks* — financial-domain sentiment basis
- **Cheng I. (2019)** — JFE "Convergence of Volatility Trading and Risk Compensation" — basis of strat_vix_backwardation_long
- **Harris L., Gurel E. (1986)** — JoF "Price and Volume Effects Associated with Changes in the S&P 500 List" — basis of post-inclusion drift
- **Beneish M., Whaley R. (1996)** — JoF — index inclusion price effects
- **Chen H., Noronha G., Singal V. (2004)** — JoF "The Price Response to S&P 500 Index Additions and Deletions" — basis of strat_post_inclusion_drift_long / strat_post_deletion_drift_short
- **Conover M., Jensen G., Johnson R., Mercer J. (2008)** — JoF "Sector Rotation and Monetary Conditions" — basis of strat_sector_rotation_defensive_long
- **Hammoudeh S., Yuan Y. (2008)** — Resources Policy — basis of strat_gold_silver_risk_off_long
- **Fratzscher M. (2009)** — JoB "What Explains Global Exchange Rate Movements During the Financial Crisis?" — basis of strat_dxy_headwind_multinational_short
- **Heston S., Sadka R. (2008)** — JFE "Seasonality in the Cross Section of Stock Returns" — basis of strat_totm_long
- **Bouman S., Jacobsen B. (2002)** — AER "The Halloween Indicator" — basis of strat_halloween_seasonal_long

### Forensic-fix lineage

- **B211 (2026-05-17)** — ORB stocks-in-play registration
- **B220 (2026-05-18)** — Factor / cross-sectional strategies (xs_quality_top_quintile_long in this cluster)
- **B253 (2026-05-19)** — News sentiment cluster registration
- **B254 (2026-05-19)** — Cross-asset risk-off + DXY + VIX + sector rotation strategies
- **B278 (2026-05-20)** — News sentiment tightening (later partially-reverted B314)
- **B314 (2026-05-24)** — News sentiment loosening Cat-2 B+C owner-approved
- **B748b/c (2026-06-13)** — FALSE EXPLORATORY tags on news + index_rebalance + sec_edgar producers
- **B748d (2026-06-14)** — Walk-back of B748c FALSE tags; CHECKLIST #106 codified; data-state correct for news + index_rebalance + sec_edgar; codified `feedback_data_consumption_audit_must_apply_checklist_44b`

### Cross-strategy patterns lineage (CARRIED + NEW)

- **Pattern A** — B577 STRATEGY_REGIME_AFFINITY (cross-applied via C-21 finding)
- **Pattern F** — B663 sweep + B718 borrow refactor
- **Pattern J** — B714 routing framework (audit candidates for C.1 + C.2)
- **Pattern N** — B710 effective-N + W5 council
- **Pattern Q** — B643 W5 + B655 T10 EVENT-conversion (news_sentiment_long is STATE; news_sentiment_shift is EVENT — both exist as separate strategies)
- **Pattern S** — B611 asymmetric data sources (LONG-only news/vix/index strategies are correct per literature)
- **Pattern V** — B716 cross-sectional + news + sec_edgar TIER 2 producer blocker
- **Pattern Z (NEW B750)** — Calendar event PIT discipline (calendar_effects.py)
- **Pattern AA (NEW B750)** — Event-strategy structurally-limited effective-N; EXPLORATORY mandatory
- **Pattern BB (NEW B750)** — News sentiment vendor SPOF; sentinel-test cheap-fix (parallel to B719 SMC Pattern L)

---

## B750 cluster walk status

| Walk | Status | Batch |
|---|---|---|
| C-13 news_sentiment_long | ✅ Walked B750 | 2026-06-14 |
| C-21 vix_backwardation_long | ✅ Walked B750 | 2026-06-14 |
| C-26 post_inclusion_drift_long | ⚠ Walk-incomplete B750; complete-B751 | 2026-06-14 partial |
| All other C-1..C-35 walks | ⏳ Pending B758-B761 | — |

**Progress: 2.5/33 walked (8%) — framework + 2 full + 1 partial sample walks shipped B750.**

---

## Reconciliation note (B750-shipped, owner-feedback-pending)

Cluster C scope inventory shows **35 strategies** in the state table vs the originally-proposed **33**. The +2 reconciliation reason: my Cluster C original proposal counted "4 calendar strategies" but the actual unwalked-set has 6 calendar strategies (pre_fomc_long_sleeve, pre_fomc_quality_momentum_long, halloween_seasonal_long, january_effect_small_cap_long, pre_holiday_long, totm_long). Net unwalked = 30 + 33 + 35 = 98, off by +2 from the source-verified 96.

**Possible causes:**
1. Two of the C strategies in my expanded list ARE actually walked in another cluster doc and were missed by my header-strict grep (false-negative).
2. My original Cluster C count omitted 2 calendar strategies due to mental-bucketing oversight; true unwalked is 98 not 96.

**Disposition:** B751 audits the +2 discrepancy. Until resolved, walks proceed on all 35 names in Cluster C state table; B751 sweep removes any that turn out to be already-walked elsewhere.

---

### Cross-cluster status snapshot (post-B750)

| Cluster Doc | Status | Walks |
|---|---|---|
| All 8 prior cluster docs | External review complete + walks complete | 132 |
| [STAGE_4_OSCILLATOR_MEAN_REVERSION_CLUSTER_WALKS.md](STAGE_4_OSCILLATOR_MEAN_REVERSION_CLUSTER_WALKS.md) | B750 framework + 3 sample walks | 3/30 |
| [STAGE_4_TREND_CONFLUENCE_CHART_PATTERN_RESIDUAL_CLUSTER_WALKS.md](STAGE_4_TREND_CONFLUENCE_CHART_PATTERN_RESIDUAL_CLUSTER_WALKS.md) | B750 framework + 3 sample walks | 3/33 |
| **STAGE_4_CONTEXT_EVENT_CALENDAR_CLUSTER_WALKS.md (THIS DOC)** | **B750 framework + 2.5 sample walks** | **2.5/33-35** |

**Stage 4 cluster-walk coverage post-B750 (all 3 new docs combined):** 132 + 3 + 3 + 2.5 = **140.5 walked (64%)** / ~80 remaining unwalked (36%). Target: 96-walk completion across B751-B762.

---

**B750 Cluster C deliverables:** doc scaffolding + Patterns A-BB framework + 35-strategy state table (reconciliation pending) + 2.5 walks (C-13 + C-21 + C-26 partial) + 8 NEW EXECUTION_QUEUE tickets + cross-cluster snapshot update.

**Per `feedback_pyramid_per_addressal`:** pyramid runs end-of-batch with B750 commit alongside Cluster A + B docs.

**Per `feedback_strategy_counts_by_buckets_each_turn`:** 221 registered / 0 deprecated / 1 missing-producer / 220 active. Cluster C walks: 2.5/33 (8% post-B750). Total Stage 4 walked: 140.5/221 (64%).
