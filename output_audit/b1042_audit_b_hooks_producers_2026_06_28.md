# Source: Council 136 Option-7 + feedback_monitor_design_vs_operational_gap per CHECKLIST #77.

# B1042 Audit-B: Hooks / Observers + Producer-Wiring End-to-End

**Date:** 2026-06-28
**Scope:** Council 136 Option-7 design-vs-armed audit (sub-agent Audit-B)
**Categories:** CAT-3 (hooks/observers/callbacks) + CAT-4 (producer wiring)
**Mode:** READ-ONLY; no code changes

---

## CAT-3 - Hooks / Observers / Callbacks

### Glob result
```
backtest/**/*hook*.py        -> 0 matches
backtest/**/*observer*.py    -> 0 matches
backtest/**/*callback*.py    -> 0 matches
backtest/**/*listener*.py    -> 0 matches
backtest/**/*plugin*.py      -> 0 matches
```

### Function-name probe
Grep `backtest/**` for `def (pre_run_hook|post_run_hook|on_trade_open|on_trade_close|on_phase_complete|on_error|on_bar|on_signal|on_fill|register_hook|register_callback|register_observer)` -> **0 matches**.

Grep `backtest/engine/backtest.py` for any of `hook|callback|observer|listener|plugin` (case-insensitive) -> **0 matches**.

### CAT-3 Verdict
**No hook/observer/callback subsystem exists in this codebase.** The engine is monolithic-loop architecture (backtest.py:process_day_for_ticker drives screen_instrument inline). Nothing to register; nothing to be DEFINED-ONLY. Zero DESIGN-VS-ARMED gap surface in CAT-3.

**Counts:** Total hooks/callbacks = 0 / REGISTERED = 0 / DEFINED-ONLY = 0 / DEPRECATED = 0.

---

## CAT-4 - Producer Wiring (inject_* + compute_*_signals end-to-end)

### inject_*_signals from `backtest/data/signal_loader.py`

| inject_* fn | Producer module | Caller in screener.py | data_prefetch path | Consumer keys (sample) | Verdict |
|---|---|---|---|---|---|
| `inject_news_sentiment_signals` | `news_sentiment.compute_news_sentiment_signals` | screener.py:8176 | `polygon/news/` (1,927 files) | `news_sentiment_mean`, `news_count_7d` | WIRED |
| `inject_institutional_persistence_signals` | `institutional_persistence_consumer.compute_persistence_signals` | screener.py:8078 | `derived/institutional_persistence_t1a/{2022-2026}-01-01.parquet` (5 files) | `persistent_holders_4q`, `total_active_holders` | WIRED (consumer in EXPLORATORY per B979) |
| `inject_short_interest_signals` | `short_interest.compute_short_interest_signals` | screener.py:8023 | `finra/short_interest/` (1,926 files) | `short_interest_pct`, `days_to_cover` | WIRED |
| `inject_search_volume_signals` | `search_volume.compute_search_volume_signals` | screener.py:8180 | `pytrends/` (1,417 files; ~73% coverage of 1929 ops universe) | `search_volume_spike`, `retail_attention_score` | WIRED (partial coverage) |
| `inject_earnings_surprise_yoy_signals` | `earnings_surprise_yoy.compute_yoy_surprise_signal` | screener.py:8019 | shares `polygon/financials/` (1,938 files) | `yoy_surprise_high`, `yoy_surprise_negative` | WIRED |
| `inject_pead_signals` | `pead.compute_pead_signals` | screener.py:8014 | `polygon/financials/` (1,938 files) | `within_pead_window`, `pead_positive_surprise` | WIRED |
| `inject_classification_change_signals` | `universe.get_classification_change_signals` | screener.py:8045 | `sector_history.csv` | `classification_changed_recent` | WIRED (B910 sector_history staleness flagged elsewhere; producer call wired) |
| `inject_insider_buying_signals` | `insider_buying.compute_insider_cluster_signals` | screener.py:8029 | `quiver/insider/` (1,942 files) | `insider_cluster_active`, `insider_director_buyers_30d` | WIRED |
| `inject_insider_signal_keys` (**B1034 silent-gap fix**) | `smart_money.insider_signal` | screener.py:8040 | shares `quiver/insider/` | `concentrated_sell`, `cfo_buy`, `large_dollar_buy`, `ceo_buy`, `director_only_buy` | WIRED (B1034 fix verified by Grep: B1010 strat_insider_cluster_concentrated_sell_short consumes `concentrated_sell` at screener.py - wired) |
| `inject_institutional_signals` | `smart_money.institutional_signal` | screener.py:8060 | `quiver/institutional/` (1,942 files) | `institutional_signal`, `institutional_new_positions` (B918 typo fixed) | WIRED |

**Total inject_*_signals = 10. WIRED end-to-end = 10. BROKEN = 0.** B1034 fix (W3/W4 finding for B1010 concentrated_sell silent-gap) is intact at screener.py:8040.

### Non-inject producers called directly in `screen_instrument` (screener.py:8083-8315)

These bypass signal_loader and call `compute_*` producers inline (legacy path). Each wrapped in try/except silent-failure logger.

| Producer call | Module | data_prefetch | Consumer keys | Verdict |
|---|---|---|---|---|
| `compute_pre_fomc_signals` | macro_events | `fred/` rate data | `days_until_fomc` | WIRED |
| `compute_smc_signals` | smc_ict (vendored) | runtime-derived | `smc_*` 28 keys | WIRED (B1039 Phase C signoff complete) |
| `compute_po3_signals` + `compute_week_opening_gap_signals` | ict_producers | runtime-derived | `po3_*`, `week_opening_gap_*` | WIRED |
| `compute_sector_strength_signals` | sector_strength | shares OHLCV cache | `sector_outperforming_spy` | WIRED |
| `compute_all_chart_patterns` | chart_patterns | runtime-derived | `head_and_shoulders_top`, etc. | WIRED |
| `compute_index_rebalance_signals` | index_rebalance | `derived/index_rebalance_events.parquet` | `recent_index_addition` | WIRED |
| `compute_pair_signals_for_ticker` | pairs_trading | `derived/cointegrated_pairs_t1a/` | `pair_zscore_long`, etc. | WIRED |
| `get_all_cot_signals` | cot_positioning | `cftc/` (19 series parquets) | `cot_*` series | WIRED |
| `compute_housetrading_signals` | congressional_alt_data | `quiver/housetrading/` (1,938 files) | `housetrading_recent_buy` | WIRED |
| `compute_gov_contracts_signals` | congressional_alt_data | `quiver/gov_contracts/` (1,942 files) | `gov_contract_award_recent` | WIRED |
| `compute_lobbying_signals` | congressional_alt_data | `quiver/lobbying/` (1,942 files) | `lobbying_spike` | WIRED |
| `compute_patentmomentum_signals` | congressional_alt_data | `quiver/patentmomentum/global.parquet` (1 universe-wide file, 6.9 MB) | `patent_momentum_score` | WIRED (universe-wide format by design) |
| `compute_offexchange_signals` | congressional_alt_data | `quiver/offexchange/` (1,851 files) | `offexchange_pct_high` | WIRED |
| `compute_corporatedonors_signals` | congressional_alt_data | `quiver/corporatedonors/global.parquet` (1 file, 253 KB) | `corporate_donor_match` | WIRED (universe-wide) |
| `compute_sec_edgar_signals` | sec_edgar_extractor | `sec_edgar_decoded/{8_K,SC_13D,SC_13D_A,SC_13G}/` | `8k_item_1_01_filed_within_30d`, `sc_13d_filed_within_30d` | WIRED (B1035 m_and_a_target_long re-enabled, EXPLORATORY) |
| `_cached_calendar_signals` | calendar_effects | runtime-derived | calendar_seasonal_* | WIRED |
| `_cached_cross_asset_signals` | cross_asset | `polygon/ohlcv_daily/` ETF proxies | `vix_term_contango`, `dxy_*` | WIRED |
| `compute_volume_profile` + `compute_period_pocs` | volume_profile | runtime-derived from OHLCV | `vp_*`, `naked_poc_count`, `naked_poc_nearest_distance_pct` | WIRED (B1035 reverted B975 disablement; consumer at screener.py:6479-6480) |
| multi_timeframe (`compute_po3_signal` + `compute_weekly_bias` + `compute_monthly_bias` + `compute_htf_alignment`) | multi_timeframe | runtime-derived | `po3_*`, `weekly_bias_*`, `htf_aligned_*` | WIRED |

### Producers in `backtest/signals/` NOT directly called by screen_instrument

| Producer | Status | Notes |
|---|---|---|
| `technical.compute_break_retest_signals` / `compute_52w_break_retest_signals` / `compute_pivot_break_retest_signals` | WIRED via `compute_all_signals` (screener.py:8315 path) | Aggregator entry, not orphan |
| `technical_panel.compute_panel_signals_for_as_of` | WIRED via engine OPT-C Phase 4 panel-cache prime | Pre-computed at engine init |
| `chart_patterns.compute_flag_break_retest_signals` / `compute_triangle_apex_break_retest_signals` / `compute_cup_handle_neckline_break_retest_signals` | WIRED via `compute_all_chart_patterns` aggregator | Confirmed via aggregator dispatch |
| `cross_asset.compute_bond_equity_signals` / `compute_vix_term_structure_signals` / `compute_sector_rotation_signals` / `compute_gold_silver_ratio_signals` / `compute_dxy_signals` | WIRED via `compute_cross_asset_signals` aggregator | Single entry point at screener.py:8267 |
| `cot_positioning.compute_cot_series_signals` | WIRED via `get_all_cot_signals` aggregator | Per-series helper |

**No orphan producers found.** All `compute_*_signals` functions are either: (a) directly called from screen_instrument, (b) reachable through an aggregator that screen_instrument calls, or (c) part of an inject_* function called from screen_instrument.

### `register_*_signals` probe
Grep `register_\w+_signals` -> **0 matches.** Codebase does not use a registry pattern for signals; each producer is imported lazy-inline at the consumer site.

---

## Cross-reference: STRATEGIES_DISABLED_MISSING_PRODUCER vs EXPLORATORY_STRATEGIES

`backtest/config.py:1105-1107` (canonical):
```
STRATEGIES_DISABLED_MISSING_PRODUCER = { "dxy_headwind_multinational_short" }
```
- Reason: `foreign_rev_pct` producer not implemented in any signals module.
- Grep confirms no `foreign_rev_pct` producer in `backtest/signals/`. **Disablement justified.**
- B1035 reversed B975 (naked_poc) + B984 (m_and_a) after sub-agent runtime probes confirmed producers exist; this leaves dxy_headwind as the sole disabled entry - consistent with CLAUDE.md banner.

`backtest/engine/multiple_testing_correction.py:70-115` `EXPLORATORY_STRATEGIES` (12 entries) - none correspond to missing producers; tagged for fire-count-starved / disputed-measurement reasons. No overlap with DISABLED_MISSING_PRODUCER (correct partition).

---

## Taxonomy Patterns Observed

| Pattern | Occurrences | Examples |
|---|---|---|
| **A** - hook defined but never registered | 0 | (no hook subsystem) |
| **B** - inject called but producer returns empty | 0 confirmed | (would need runtime probe; all 10 inject paths have data_prefetch populated) |
| **C** - producer emits but no strategy consumes | 0 confirmed | All producers traced have >=1 consumer in screener.py |
| **D** - producer claim "RESOLVED" but path broken | 0 currently active | Previously: B1010 silent-gap (FIXED B1034); B975/B984 false-disable (FIXED B1035). Per B1035 disposition, no residual D-class gap. |

---

## Sub-pattern: Universe-wide single-file producers

Two producers ship as `global.parquet` (universe-wide):
- `quiver/patentmomentum/global.parquet` (6.9 MB)
- `quiver/corporatedonors/global.parquet` (253 KB)

These are **NOT broken**; the consumer functions in `congressional_alt_data.py` are designed for this format. No DESIGN-VS-ARMED gap. Note for future audits: file-count audits should not flag single-file universe-wide producers as suspicious unless their consumer expects per-ticker layout.

---

## Sub-pattern: Partial-coverage data path

| Producer | Coverage | Note |
|---|---|---|
| `pytrends` | 1,417 / 1,929 ops universe (~73%) | Producer wired correctly; coverage gap is data-acquisition rate-limit, not wiring. Strategies on uncovered tickers will silent-fail (s.get default-False) - consistent with `feedback_signal_temporality_event_vs_state` STATE-signal handling. |
| `quiver/offexchange` | 1,851 / 1,929 (~96%) | Acceptable |

These are not DESIGN-VS-ARMED gaps; they are coverage-density issues outside Audit-B scope.

---

## Recommendations (None - Read-only audit)

Per `feedback_audit_recommendations_against_existing_directives`, all dispositions surfaced here cross-reference existing CLAUDE.md / banner state:
- No new WIRE / DELETE / ARCHIVE / DOCUMENT-AS-MANUAL recommendations.
- The pattern `B` (B1010-class silent-gap) was already remediated by B1034; B1042 sub-agent Audit-B confirms the fix is intact.
- Pattern `D` claims previously surfaced (B975 naked_poc; B984 m_and_a) were correctly REVERSED by B1035 - these are not residual gaps.

**Audit-B Summary:**

| Counter | Value |
|---|---|
| Total hooks/callbacks | 0 |
| REGISTERED | 0 |
| DEFINED-ONLY (DESIGN-VS-ARMED) | 0 |
| DEPRECATED | 0 |
| Total `inject_*_signals` | 10 |
| WIRED end-to-end | 10 |
| BROKEN | 0 |
| Orphan `compute_*_signals` | 0 |
| `register_*_signals` registry | None (architecture choice) |
| `STRATEGIES_DISABLED_MISSING_PRODUCER` mismatches | 0 (dxy_headwind producer absence confirmed) |

**Verdict for CAT-3 + CAT-4:** No new DESIGN-VS-ARMED gaps detected. All previously-found Pattern-B silent-gaps (B1010 concentrated_sell) and Pattern-D false-claims (B975, B984) have already been remediated by B1034 / B1035. Audit-B is GREEN.
