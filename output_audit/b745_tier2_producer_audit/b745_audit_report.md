# B745 TIER 2 Producer Audit Report (finding-grade)

# Source: scripts/audit_tier2_producer_caches.py per CHECKLIST #77

Probe ticker: `AAPL`  |  Probe as_of: `2024-06-28`  |  Total producers audited: **16**

## Headline finding (pre-audit investigation, 2026-06-13)

**The B689 audit claim that `patentmomentum` and `corporatedonors` had STUB caches (1 entry each) is FALSE.**
Direct probe of the underlying parquets:
- `data_prefetch/quiver/patentmomentum/global.parquet`: **5,830,800 rows** (5.8M; 6.9MB)
- `data_prefetch/quiver/corporatedonors/global.parquet`: **25,000 rows** across 432 unique tickers

This means the 'silent-gap risk' framing inverts: data IS present.
The audit below confirms whether each producer READS + EMITS correctly + whether consuming strategies actually fire.

## Per-producer classification

| # | Producer | Module | Mechanism | Path | Data rows | Unique tickers | Smoke emits | Smoke keys | Error |
|---|---|---|---|---|---:|---:|---|---|---|
| 1 | `compute_insider_cluster_signals` | `insider_buying` | module_dict | **A** | 1,000,000 | 7,275 | NO | (empty) |  |
| 2 | `compute_persistence_signals` | `institutional_persistence_consumer` | module_dict | **A** | 500,000 | 1 | NO | (empty) |  |
| 3 | `compute_short_interest_signals` | `short_interest` | module_dict | **A** | 3,830 | 1,926 | YES | days_to_cover, short_interest_observations, short_interest_settlement_date |  |
| 4 | `compute_sec_edgar_signals` | `sec_edgar_extractor` | module_dict | **A** | 451 | 18,708 | YES | 8k_item_1_01_filed_within_30d, 8k_item_5_02_filed_within_7d |  |
| 5 | `compute_news_sentiment_signals` | `news_sentiment` | module_dict | **A** | 1,500 | 1 | YES | news_article_count, news_bearish_pct, news_bullish_pct |  |
| 6 | `compute_pead_signals` | `pead` | lru_cache | **A** | 2,876 | 1,937 | YES | days_since_last_earnings, earnings_announcement_return, earnings_eps_yoy_growth |  |
| 7 | `compute_yoy_surprise_signal` | `earnings_surprise_yoy` | none | **B** | 2,876 | 1,937 | YES | days_since_last_earnings, earnings_eps_yoy_growth, within_pead_window |  |
| 8 | `compute_search_volume_signals` | `search_volume` | module_dict | **A** | 13,100 | 1,417 | YES | search_volume_index_recent, search_volume_observations, search_volume_zscore_30d |  |
| 9 | `compute_index_rebalance_signals` | `index_rebalance` | none | **B** | 0 | 0 | NO | (empty) |  |
| 10 | `compute_housetrading_signals` | `congressional_alt_data` | module_dict | **A** | 1,276 | 1,937 | YES | house_buy_count_90d, house_cluster_buy, house_cluster_sell |  |
| 11 | `compute_gov_contracts_signals` | `congressional_alt_data` | module_dict | **A** | 905 | 1,941 | YES | gov_contracts_4q_sum, gov_contracts_last_qtr_amount, gov_contracts_qoq_growth |  |
| 12 | `compute_lobbying_signals` | `congressional_alt_data` | module_dict | **A** | 2,371 | 1,941 | YES | lobbying_amount_1y, lobbying_amount_q, lobbying_amount_yoy |  |
| 13 | `compute_patentmomentum_signals` | `congressional_alt_data` | module_dict | **A** | 5,830,800 | 1,595 | YES | patent_momentum_90d_avg, patent_momentum_above_avg, patent_momentum_recent |  |
| 14 | `compute_offexchange_signals` | `congressional_alt_data` | module_dict | **A** | 132,704 | 1,851 | YES | dpi_30d_avg, dpi_elevated, dpi_recent |  |
| 15 | `compute_corporatedonors_signals` | `congressional_alt_data` | module_dict | **A** | 25,000 | 432 | NO | (empty) |  |
| 16 | `compute_cross_sectional_features` | `cross_sectional` | needs_ohlcv_dict | **C** | 2,876 | 1,937 | YES | xs_avoid_high_ivol, xs_avoid_high_max, xs_beta |  |

## Path classification summary

### PATH A -- existing module-level cache; call as-is in measure_fire_count.py  (13 producers)

- **`compute_insider_cluster_signals`** (insider_buying)
    - data: `data_prefetch/quiver/insiders/global.parquet` -- rows=1,000,000, tickers=7,275
    - smoke: emits=False, error=none
    - consumed by 10 strategy(s): strat_classification_change_with_insider_long, strat_insider_cluster_long, strat_insider_cluster_with_director_long, strat_institutional_increased_with_directors_long, strat_institutional_insider_combo_long, strat_institutional_with_directors_long...
- **`compute_persistence_signals`** (institutional_persistence_consumer)
    - data: `data_prefetch/quiver/sec13fchanges` -- rows=500,000, tickers=1
    - smoke: emits=False, error=none
    - consumed by 2 strategy(s): strat_institutional_committed_growth_long, strat_institutional_multi_quarter_persistence_long
- **`compute_short_interest_signals`** (short_interest)
    - data: `data_prefetch/finra/short_interest` -- rows=3,830, tickers=1,926
    - smoke: emits=True, error=none
    - consumed by 2 strategy(s): strat_short_borrow_trap_avoid, strat_squeeze_setup_long
- **`compute_sec_edgar_signals`** (sec_edgar_extractor)
    - data: `data_prefetch/sec_edgar` -- rows=451, tickers=18,708
    - smoke: emits=True, error=none
- **`compute_news_sentiment_signals`** (news_sentiment)
    - data: `data_prefetch/quiver/quivernews` -- rows=1,500, tickers=1
    - smoke: emits=True, error=none
    - consumed by 7 strategy(s): strat_news_momentum_long, strat_news_momentum_short, strat_news_reversal_long, strat_news_reversal_short, strat_news_sentiment_long, strat_news_sentiment_shift_long...
- **`compute_pead_signals`** (pead)
    - data: `data_prefetch/polygon/financials` -- rows=2,876, tickers=1,937
    - smoke: emits=True, error=none
    - consumed by 9 strategy(s): strat_pead_long, strat_pead_long_high_yoy_growth_only, strat_pead_short, strat_pead_short_negative_yoy_growth, strat_pead_with_insider_confirmation_long, strat_pead_with_smart_money_long...
- **`compute_search_volume_signals`** (search_volume)
    - data: `data_prefetch/pytrends` -- rows=13,100, tickers=1,417
    - smoke: emits=True, error=none
- **`compute_housetrading_signals`** (congressional_alt_data)
    - data: `data_prefetch/quiver/housetrading` -- rows=1,276, tickers=1,937
    - smoke: emits=True, error=none
- **`compute_gov_contracts_signals`** (congressional_alt_data)
    - data: `data_prefetch/quiver/gov_contracts` -- rows=905, tickers=1,941
    - smoke: emits=True, error=none
- **`compute_lobbying_signals`** (congressional_alt_data)
    - data: `data_prefetch/quiver/lobbying` -- rows=2,371, tickers=1,941
    - smoke: emits=True, error=none
- **`compute_patentmomentum_signals`** (congressional_alt_data)
    - data: `data_prefetch/quiver/patentmomentum/global.parquet` -- rows=5,830,800, tickers=1,595
    - smoke: emits=True, error=none
- **`compute_offexchange_signals`** (congressional_alt_data)
    - data: `data_prefetch/quiver/offexchange` -- rows=132,704, tickers=1,851
    - smoke: emits=True, error=none
- **`compute_corporatedonors_signals`** (congressional_alt_data)
    - data: `data_prefetch/quiver/corporatedonors/global.parquet` -- rows=25,000, tickers=432
    - smoke: emits=False, error=none

### PATH B -- no cache; needs module-level cache added  (2 producers)

- **`compute_yoy_surprise_signal`** (earnings_surprise_yoy)
    - data: `data_prefetch/polygon/financials` -- rows=2,876, tickers=1,937
    - smoke: emits=True, error=none
    - consumed by 10 strategy(s): strat_pead_long, strat_pead_long_high_yoy_growth_only, strat_pead_short, strat_pead_short_negative_yoy_growth, strat_pead_with_insider_confirmation_long, strat_pead_with_smart_money_long...
- **`compute_index_rebalance_signals`** (index_rebalance)
    - data: `Backtesting universe/index_rebalance_events.parquet` -- rows=0, tickers=0
    - smoke: emits=False, error=none
    - consumed by 4 strategy(s): strat_post_deletion_drift_short, strat_post_inclusion_drift_long, strat_post_inclusion_reversal_short, strat_pre_rebalance_long

### PATH C -- needs ohlcv_dict or full-universe data  (1 producers)

- **`compute_cross_sectional_features`** (cross_sectional)
    - data: `data_prefetch/polygon/financials` -- rows=2,876, tickers=1,937
    - smoke: emits=True, error=none
    - consumed by 7 strategy(s): strat_pre_fomc_quality_momentum_long, strat_pre_rebalance_long, strat_xs_combined_momentum_low_ivol, strat_xs_momentum_bottom_decile_short, strat_xs_momentum_quality_combined, strat_xs_momentum_top_decile...

### PATH D -- data missing/sparse/broken; consuming strategies may be effectively dead  (0 producers)

_(none)_

---

## Owner action items

- **Path A producers**: wire directly in B752 (measure_fire_count.py `_compute_tier2_signals_for_bar` helper); no producer-side changes.
- **Path B producers** (if any): add module-level `_BY_TICKER` cache in B749/B750 per-producer mini-batches.
- **Path C producer** (cross_sectional): B751 ships `_compute_cross_sectional_signals_for_date` harness helper -- ONLY AFTER B746 PIT-invariance audit PASSES.
- **Path D producers** (if any): B748 ships loud-failure wrappers + queues dead-strategy Pattern F tickets per consuming strategy.