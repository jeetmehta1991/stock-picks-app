# Comprehensive Producer Coverage Report

<!-- Source: per CHECKLIST #77 canonical-source; Council 283 B1223 2026-07-07 -->

**Compiled:** 2026-07-07 (B1223 Council 283)
**Universe:** Batch A 133 tickers × 4 quarterly 2024 test dates
**Governance:** CHECKLIST #154 + #155 + L199 + L200

## Executive Summary

Comprehensive audit of **14 producer categories** across data-source-dependent, OHLCV-derived, and universal signal producers. Two critical findings surfaced (B1214 shares_outstanding NULL bug; B1216 institutional 30% data gap) plus one systemic finding (Council 278 loosening had bounded uplift on data-gap-limited strategies).

## Coverage Matrix

| Producer | Coverage % | Type | Impact | Bug/Gap? |
|---|---:|---|---|---|
| sec_edgar (8-K/Item 1.01) | **97.7%** | Per-ticker | Excellent | None |
| short_interest (DTC) | **97.7%** | Per-ticker | Excellent | None |
| **short_interest_pct** | **0.0%** | Per-ticker | 🔴 CRITICAL | Producer NEVER emits (shares_outstanding NULL) |
| search_volume (pytrends) | **99.2%** | Per-ticker | Excellent | 1 zero-cov (SPY) |
| PEAD earnings | **85.0%** | Per-ticker | Good | 15% zero-cov (mostly ETFs) |
| news_sentiment (Polygon) | **84.2%** | Per-ticker | Good | 16% zero-cov (small/growth) |
| earnings_yoy | **78.9%** | Per-ticker | Good | 21% zero-cov |
| congressional (QuiverQuant) | **67.7%** | Per-ticker | Moderate | 32% zero-cov |
| **institutional (13F)** | **30.1%** | Per-ticker | 🔴 DATA GAP | 70% zero-cov (constant → source gap) |
| insider (Form 4) | 18.8% | Per-ticker | Event-rarity | Partly natural sparsity |
| index_rebalance | 10.5% | Per-ticker | Event-based | Only fires around rebalance events |
| volume_profile | 100%* | OHLCV-derived | Excellent | *30-ticker sample; limited by OHLCV cache 84% |
| ict_po3 | 100%* | OHLCV-derived | Excellent | *30-ticker sample |
| calendar_effects | 100% | Universal | Excellent | Deterministic; B1180 verified |
| macro_events pre_fomc | 100% | Universal | Excellent | 4/4 test dates |
| cot_positioning (7 series) | 100% | Universal | Excellent | All 7 macro series 4/4 dates |
| cross_asset (bond/equity) | 100% | Universal | Excellent | 6 signals 4/4 dates |

## Critical Findings

### 🔴 Finding #1: short_interest_pct producer bug (B1214)
- Producer emits `days_to_cover` reliably (97.7%) but NEVER emits `short_interest_pct`
- Root cause: `shares_outstanding` is NULL in FINRA data cache
- Producer code: `short_interest.py:132-133` requires `so > 0` to emit
- **Blast radius: strat_squeeze_setup_long** (requires `si_pct >= 0.20`) - permanently unfireable
- Classification: **BLOCKED_UPSTREAM_SHORT_INTEREST_PCT**

### 🔴 Finding #2: Institutional 13F data gap (B1216)
- Only 30.1% of Batch A tickers have 13F data
- CONSTANT across all 4 dates → fundamental data source gap (not event-rarity)
- **Blast radius: 20 institutional strategies** = 10.4% of all Batch A strategies
- Classification: **COVERAGE_LIMITED_INSTITUTIONAL**
- Council 278 loosening (B1173/B1174/B1197) of these strategies had bounded uplift potential

### 🟡 Finding #3: News sentiment coverage gap (B1211)
- 84.2% effective universe; 15.8% zero-coverage (21 tickers)
- Per-date variation reveals data-vintage limitation (Q3/Q4 2024 sparser)
- **Blast radius: 6 news strategies**
- Sample bias in earlier B1204 audit (mega-caps only) was misleading

## Strategy Impact Classification (192 Batch A strategies)

| Classification | Count | % | Action |
|---|---:|---:|---|
| **UNAFFECTED** | 157 | 81.8% | No producer dependency issue |
| **COVERAGE_LIMITED_INSTITUTIONAL** | 20 | 10.4% | Fire on ~30% of Batch A |
| **COVERAGE_LIMITED_NEWS** | 6 | 3.1% | Fire on ~84% |
| **COVERAGE_LIMITED_INSIDER** | 4 | 2.1% | Event-rarity primarily |
| **COVERAGE_LIMITED_PEAD** | 3 | 1.6% | Fire on ~85% |
| **BLOCKED_UPSTREAM_SHORT_INTEREST_PCT** | 1 | 0.5% | squeeze_setup_long BLOCKED |

## Sprint 5 Prioritization (data-source expansion)

Ordered by strategy blast radius:

### 🔴 HIGHEST: S5-B1216-INSTITUTIONAL-13F-COVERAGE-EXPANSION
- Affects: 20 strategies (10% of Batch A)
- Effort: 2-3 days
- Options:
  - (a) Additional 13F snapshot ingestion (WhaleWisdom / Fintel / direct EDGAR 13F-HR)
  - (b) Fallback to Polygon /v3/reference/tickers for institutional-holdings
- Impact: 30% → 80% coverage → 8+ strategies get 2-3x fire uplift

### 🟡 HIGH: S5-B1214-SHARES-OUTSTANDING-DATA-GAP-FIX
- Affects: 1 strategy (strat_squeeze_setup_long BLOCKED)
- Effort: 1 day
- Options:
  - (a) Polygon `/v3/reference/tickers` has `shares_outstanding_common` (RECOMMENDED)
  - (b) Polygon financials_json `weighted_average_shares_outstanding`
- Impact: Unblocks strategy entirely (0% → 97%+ coverage)

### 🟢 MED: S5-B1212-SECONDARY-NEWS-SOURCE
- Affects: 6 news strategies
- Effort: 2 days
- Options:
  - (a) Finnhub news API for 21 zero-coverage tickers
  - (b) AlphaVantage news sentiment
- Impact: 84% → ~95% coverage

## Canonical Output Files

Per CHECKLIST #154 all producer audits saved to `output_audit/`:
- news_coverage_batch_a.json (B1211)
- short_interest_coverage_batch_a.json (B1214)
- pead_coverage_batch_a.json (B1215)
- insider_coverage_batch_a.json (B1216)
- institutional_coverage_batch_a.json (B1216)
- congressional_coverage_batch_a.json (B1218)
- sec_edgar_coverage_batch_a.json (B1218)
- search_volume_coverage_batch_a.json (B1220)
- index_rebalance_coverage_batch_a.json (B1220)
- earnings_yoy_coverage_batch_a.json (B1221)
- cot_positioning_coverage_batch_a.json (B1221)
- cross_asset_coverage_batch_a.json (B1221)
- ohlcv_derived_and_universal_producers_coverage.json (B1222)
- strategy_vs_producer_coverage_matrix.json (B1217)
- **PRODUCER_COVERAGE_COMPREHENSIVE_REPORT.md** (this file, B1223)

## Canonical Audit Scripts

- `scripts/measure_producer_coverage.py` (B1214+) - generic per-ticker producer audit template
- `scripts/measure_news_coverage_batch_a.py` (B1211) - news-specific canonical
- `scripts/cross_audit_strategies_vs_coverage.py` (B1217) - strategy-vs-coverage matrix

## Governance Codified

- CHECKLIST #154 - Data-source coverage audit MANDATORY before "producer verified" claims
- CHECKLIST #155 - BLOCKED_UPSTREAM classification for data-gap strategies
- L199 - Data-source coverage audit methodology (3-audit-chain from Council 279-280)
- L200 - Strategy-vs-producer cross-audit + Sprint 5 prioritization framework

## Council 278-283 Cumulative Progress

| Council | Batches | Focus | Outcome |
|---|---|---|---|
| 278 | B1188-B1204 | 40 SKIP strategies loosened | 39 code + 1 DELETE + news audit |
| 279 | B1205-B1210 | 11 silent misses remediated | Column regen + pin tests + spirit-match codified |
| 280 | B1211-B1213 | News coverage refined + #154 codified | 84.2% news effective universe |
| 281 | B1214-B1216 | 3 producer audits | Critical bug + institutional gap surfaced |
| 282 | B1217-B1219 | Cross-audit + 2 more producer audits + #155 | 22 strategies classified BLOCKED/LIMITED |
| 283 | B1220-B1223 | 5 more producer audits + comprehensive report | 14 producers audited total |

**Total: 36 batches, 40 strategies materially improved, 3 Sprint 5 tickets queued, 5 new CHECKLIST items (#151-#155), 4 new lessons (L197-L200), 14 canonical audit outputs, 3 canonical audit scripts, 1 comprehensive report.**
