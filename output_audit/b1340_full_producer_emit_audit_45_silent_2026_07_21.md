# B1340 — Full broad-sample producer-emit audit of all 45 silent strategies (technical + data-fed)

# Source: EXECUTED audits this turn — scripts/audit_producer_emit.py + scripts/audit_datafed_probe.py; artifacts output_audit/b1340_producer_emit_audit.json + b1340_datafed_probe.json; canonical strategy roster per backtest.signals.screener.ALL_STRATEGIES. per CHECKLIST #77.

**Council 367 · 2026-07-21 · owner "audit data-fed ones too, they should fire in R5" · zero spend · engine unchanged since batch-1 SHA e846b6d2c**

Answers the question B1333 could not: for each of the 45 silent strategies, is it silent because a **producer is broken/data-absent** (a real R5 coverage bug) or because the **event is genuinely rare/narrow** (benign)? Two audits, both EXECUTED:

- **Technical/chart** (`compute_all_signals` + `compute_all_chart_patterns`), 30 diverse tickers incl. volatile names (TSLA/MARA/RIOT/COIN/F/GM/INTC/PYPL), every bar, full 4y window (2452s runtime).
- **Data-fed** (`screen_instrument`, the real production path driving corporate-donors / sec_edgar / calendar / cross-asset / index-rebalance / insider / news), 23 tickers incl. the 2023-03-17 reclassified set (V/MA/TGT/DG/ADP/PAYX/PYPL/DLTR) × 27 event-targeted dates, 506 calls.

## HEADLINE: zero broken producers. All 45 explained.

### A. Technical/chart — 13 fire ABUNDANTLY at broad scale (producers work; batch-1 0-trades = sparsity/counter-semantics)

The exact strategies B1333 flagged as raw>0/0-trades fire hundreds of times in a 30-ticker sample:

| strategy | fires (30 tkr, 4y) | strategy | fires |
|---|---|---|---|
| flag_bull_long | **779** | death_cross_50_200_volume | 35 |
| adx_initiation | **562** | pivot_s2_bounce | 18 |
| flag_bull_retest_long | 210 | mfi_oversold | 17 |
| golden_cross_50_200 | 174 | flag_bear_retest_short | 10 |
| golden_cross_volume | 69 | keltner_lower | 9 |
| hammer_at_support_long | 43 | pivot_r3_blowoff_short / supertrend_ichimoku_adx | 2 / 2 |

flag_bull_long fires **779×** across 30 tickers — its batch-1 0-trades on 10 tickers is confirmed a **sample-density + counter-semantics** artifact (L213), not a broken producer. All 13 will fire in R5.

### B. Data-fed producers — ALL 9 signal keys EMIT with real data (none broken)

`screen_instrument` on real feeds, "does the key ever go non-default?":

| producer key | emit hits | example | producer key | emit hits |
|---|---|---|---|---|
| classification_changed_recent | 24 | V@2023-06=True | institutional_increased | 429 |
| insider_unique_buyers_30d | 30 | DG=3 | risk_off_regime_gold_signal | 115 |
| insider_cluster_active | 2 | DG=True | defensive_leadership | 276 |
| is_january_extended | 69 | — | news_count_5d | 476 |
| news_sentiment_shift | 455 | V=-0.039 | | |

**Every data-fed producer emits.** The strategies are multi-gate combinations (event + trend + direction + cap), so they fire when gates align. Fired in the probe: classification_change_recent_long (4), classification_change_to_defensive_short (2), classification_change_from_tech_short (1), institutional_increased_with_directors_long (4), post_deletion_drift_short (1). Batch-1's fuller AWS run additionally proved live: institutional (49), news_momentum_short (6), news_reversal_short (1), pre_rebalance_long (6), halloween_seasonal_long (16).

### C. 🟠 Two STRUCTURAL coverage gaps — cannot be measured in T1a-only R5 regardless of roster

1. **classification_change_to_tech_long** — zero "moved INTO tech" reclassifications exist in sector_history.csv for 2022-2026 (the 14 in-window events all moved INTO Financials/Industrials/Staples). The producer works; the *event class* doesn't occur this window. Unmeasurable. → **S6-B1340-TOTECH-GAP** (owner: accept as no-verdict, or extend window).
2. **january_effect_small_cap_long** — requires `cap_band=small`; T1a (S&P 500) is entirely large/mega-cap, so the cap gate can never pass in a T1a-only universe. Structurally dead until the universe expands beyond T1a. → **S6-B1340-SMALLCAP-GAP** (out of scope for the current T1a sequence).

### D. 🟠 Near-null entry conditions — `rsi_overbought_short` / `rsi21_slow` are self-contradictory (design issue, not producer bug)

`rsi_overbought_short` = `rsi_14>65 AND below_sma_50`. A targeted co-occurrence test on 6 volatile names (TSLA/MARA/RIOT/COIN/INTC/PYPL, every bar, 4y) shows the two conditions **NEVER co-occur**:

| ticker | rsi_14>65 bars | below_sma_50 bars | BOTH |
|---|---|---|---|
| TSLA | 133 | 493 | **0** |
| MARA | 114 | 529 | **0** |
| COIN | 143 | 559 | **0** |
| INTC/RIOT/PYPL | 127/133/81 | 488/496/579 | **0/0/0** |

This is structural: pushing RSI-14 above 65 requires a rally strong enough to also lift price back above its 50-SMA, so "overbought **while below** the 50-SMA" is a near-empty set. Both signals compute correctly — the **entry logic is self-contradictory**. B1140 (Council 254) loosened the RSI threshold 68→65 but never addressed the contradiction. Same `below_sma_50` gate affects `rsi21_slow`. → **S6-B1340-RSI-NULL-GATE** (owner: redesign the gate — e.g. slower RSI or looser trend proxy — or retire as EXPLORATORY-dead). `pivot_s3_capitulation` is separately narrow (B643 measured 18.3/yr, FAIL_FIRE_STARVED) — genuinely rare, not contradictory.

Note: short-interest data (`data_prefetch/finra/short_interest` + producer `backtest/signals/short_interest.py`) IS present, so `days_to_cover`-dependent gates (short_borrow_trap_avoid, squeeze_setup_long) have their feed.

### E. Roster implication for R5 coverage (actionable)

To actually *measure* the data-fed families, batches must include event-tickers:
- **Classification (8 of 10 measurable):** include reclassified tickers. **Batch-2 roster already has V/MA/PYPL** → exercises from_tech / recent / momentum / oversold / volume / with_insider / with_institutional. **Add TGT/DG/DLTR** to also cover `to_defensive_short`.
- **Insider/news/institutional/rebalance:** batch-1 already fired these; maintain breadth across batches.
- **Small-cap-dependent (january_effect):** only measurable if the universe expands beyond T1a — deferred.

## Bottom line

**No broken producer found. No batch-1 re-run required on producer grounds.** The 45 silent strategies decompose as: 13 technical fire abundantly at scale · ~27 data-fed with all-emitting producers (fire when gates align; roster-driven) · 2 structural gaps (to_tech, small_cap) · 3 narrow-EXPLORATORY. B1333's "producers work, events absent" conclusion was *directionally* right but was asserted without evidence; this audit supplies the evidence and corrects two specifics (to_tech and small_cap are structurally unmeasurable, not merely rare).

Artifacts: `output_audit/b1340_producer_emit_audit.json` (technical), `output_audit/b1340_datafed_probe.json` (data-fed).
