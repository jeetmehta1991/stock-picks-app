# PREFETCH_COVERAGE_AUDIT.md — Pass 53 Day-9 v8h comprehensive prefetch audit

Owner directive 2026-05-07: *"This is exactly what i mean that we should pre fetch ALL available endpoints and corresponding dimensions. We can choose to not use it but if we have it all prefetched we can be flexible and quick in addressing.... Data quality and comprehensiveness is the foundation."*

This doc audits every prefetched data source against:
1. **Endpoint coverage** — does the source have other endpoints we're not fetching?
2. **Dimension coverage** — for each endpoint, are we fetching all available dimensions (per-ticker / global / historical / per-form / etc.)?
3. **Universe coverage** — does the prefetch span the full 1937-ticker Master Universe (or relevant subset)?

Last full inventory: 2026-05-07 evening. Master Universe = 1937 unique tickers.

---

## Retrospective enrichment per CHECKLIST #76 (added 2026-05-07 evening)

**Disclosure:** the original audit (commit `c0a3a568`) was a **paper audit only** — file counts, dimension lists, and status fields. It did NOT exercise functional-verification (no smoke runs of prefetch scripts during audit, no pyramid scan over consumer paths, no filesystem↔checkpoint diff, no endpoint discovery probe). Per CHECKLIST #76, this is non-compliant for phase-gating use without retrofit.

This section retrofits the missing column-(b) functional-verification + column-(c) recommendation/blocker-status that #76 now mandates.

### Column (b) — functional-verification gaps surfaced AFTER the original audit

| Bug surfaced AFTER `c0a3a568` | Verification step that would have caught it AT AUDIT TIME | Severity if undetected |
|---|---|---|
| Quiver Unicode print crash (`✓` causing 897 errors) | `python scripts/prefetch_quiver.py --tickers AAPL` smoke + tail output | Cosmetic only; data integrity intact |
| Polygon news schema drift (`tickers` → `all_tickers`) | `pytest backtest/tests/test_polygon_news_smoke.py -q` | Consumer crash on first news read |
| CFTC numeric-as-string dtype | `pytest backtest/tests/test_data_integrity_4_numeric_dtype_cftc_fred -q` | Silent rolling-mean failures downstream |
| CFTC Treasury contract-name typos (INV-011) | Smoke fetch of one Treasury contract slug + assertion | Empty parquets for 5 contracts |
| FRED VVIX 400 (INV-010) | Smoke fetch one series at a time + check 200 response | Silent zero-data series |
| Quiver B5-B10 endpoints 404 (INV-012) | GET each endpoint with one ticker before adding to recommendation list | Wasted Tier-B recommendations |
| Wikipedia checkpoint ghost (INV-013) | `diff <(jq keys _checkpoint.json) <(ls -1 dir/)` for every prefetch | Re-prefetch silently skips deleted dirs |
| Production runner Unicode bug (Phase 1A blocker) | Out of audit scope, but P1.runner integration test added retroactively | Phase 1A May 15 launch blocker |

**Lesson:** every comprehensive audit row must run AT LEAST one of {smoke, pyramid scan, filesystem↔checkpoint diff, API endpoint probe} before the audit is considered complete. See CHECKLIST #76.

### Column (c) — recommendations + priority + blocker-status (retrofit for every red/yellow row)

| Source / endpoint | Coverage | Recommendation | Priority | Blocker for |
|---|---|---|---|---|
| Polygon reference (sector/cap/IPO) | 30.9% 🔴 | Re-prefetch at full 1937 universe (~1-2h) | P0 | **Phase 1A** — `fetch_info()` returns sector=Unknown for 70% of universe; breaks sector-classification + position-sizing |
| Polygon dividends | 0.1% 🔴 | Full historical re-prefetch (~2-3h) | P1 | Phase 1B (no dividend strategies in baseline 60); informational for Phase 1A |
| Polygon splits | 0.1% 🔴 | Full historical re-prefetch (~2-3h) | P1 | Phase 1B; informational for Phase 1A (yfinance OHLCV is split-adjusted) |
| Polygon financials | 90.1% 🟡 | Top-up the missing 191 tickers (~30 min) | P2 | non-blocking — fundamental strategies opt-in; missing tkrs likely de-listed |
| Polygon events (ticker_change) | 87.1% 🟡 | Top-up the missing 250 tickers (~30 min) | P2 | non-blocking — used only for ticker-rename resolution (DEC-500) |
| Quiver congressional | 26.3% 🔴 → ~82% (BG running) | **In progress** — Quiver BG `bsu432hbt`; commit on completion | P0 | **Phase 1A** — smart-money composite signal degenerate at 26.3% |
| Quiver gov_contracts | 26.3% 🔴 | Re-prefetch at 1937 (queued in BG `bsu432hbt`) | P0 | Phase 1A (same composite) |
| Quiver insider per-ticker | 26.3% 🔴 | Re-prefetch at 1937 (queued in BG) | P0 | Phase 1A (same composite); also fixes BUG-INSIDER-PIT |
| Quiver institutional per-ticker | 26.3% + ~18% empty 🔴 | Re-prefetch at 1937 (queued in BG) | P0 | Phase 1A (same composite) |
| Quiver lobbying | 26.3% 🔴 | Re-prefetch at 1937 (queued in BG) | P1 | Phase 1B (lobbying_signal not in Phase 1A baseline) |
| Quiver wallstreetbets | 26.3% 🔴 | Re-prefetch at 1937 (queued in BG) | P1 | Phase 1B (retail-attention not in Phase 1A baseline) |
| Quiver wikipedia mirror | 0% effective 🔴 | **DELETE** — canonical lives at `data_prefetch/wikipedia/` (1414 files) — INV-013 documented; NOT re-prefetching | n/a | resolved (INV-013) |
| Quiver etfholdings | 80.7% 🟡 | Top-up missing 374 ETFs OR accept (no PIT dim — INV-008) | P2 | non-blocking — informational for ETF-flow strategies (Phase 1B+) |
| SEC EDGAR Form 4 | 82.6% 🟡 | Top-up the missing 337 tickers (~1h) | P1 | Phase 1B insider-overlay strategies; not in Phase 1A baseline |
| SEC EDGAR 8-K | 79.7% 🟡 | Top-up the missing 394 tickers (~1h) | P1 | Phase 1B catalyst-event signals |
| SEC EDGAR SC 13D | 64.2% 🔴 | Top-up the missing 693 tickers (~2h) | P1 | Phase 1B activist-overlay |
| SEC EDGAR SC 13G | 86.2% 🟡 | Top-up the missing 268 tickers (~1h) | P2 | non-blocking |
| SEC EDGAR 10-K / 10-Q | 0% 🔴 | NEW prefetch (~4-6h × 2 forms) | P1 | Phase 1B — fundamentals filing-date timing; partially served by Polygon financials for Phase 1A |
| SEC EDGAR DEF 14A | 0% 🟡 | NEW prefetch (~2-3h) | P2 | non-blocking |
| SEC EDGAR S-1/S-1A | 0% 🟡 | NEW prefetch (~1-2h) | P2 | Sprint 5 (T2 IPO enrichment) |
| SEC EDGAR 13D/A + 13G/A amendments | 0% 🟡 | NEW prefetch (~2h) | P2 | Phase 1B+ activist updates |
| FRED missing series (VIX3M / DTWEXBGS / DCOILWTICO / HOUST / PERMIT / RSAFS / IPB50001N) | 0% 🔴 | **DONE** P1 batch — added 19/21 (VVIX + gold deferred per INV-010) | n/a | resolved this session |
| ALFRED vintage gaps | matches FRED | Mirror FRED additions (~30 min) | P2 | non-blocking — vintage primarily for revision-aware strategies (Phase 1C+) |
| CFTC COT (only e-mini SP500) | 1 contract 🔴 | **DONE** P1 batch — extended to 19 contracts | n/a | resolved this session |
| Apewisdom global | 1 file | Per-ticker mention timeline if API supports | P2 | Sprint 5 — retail-attention extension |
| pytrends | 73.2% 🟡 | Top-up missing 520 tickers (~3-4h, rate-limited) | P2 | Phase 1B+ search-attention signal |
| Wikipedia pageviews | 73.0% 🟡 | Top-up missing 523 tickers (~2h) | P2 | non-blocking |

**P0 summary (Phase 1A blockers):** Polygon reference (A1) + 4 Quiver per-ticker endpoints (congressional/gov_contracts/insider/institutional). **All 5 are actively being addressed** — Polygon reference top-up is queued; Quiver BG `bsu432hbt` is in flight (~7h remaining at last check). Once both complete, **0 P0 blockers remain for Phase 1A May 15.**

**P1 summary:** Phase 1B+ work (dividends/splits, lobbying, WSB, SEC EDGAR top-ups + 10-K/10-Q). Not blocking Phase 1A.

**P2 summary:** Sprint 5 / informational. Not blocking any near-term phase.

---

## Summary — Coverage matrix

### Polygon Stocks Starter

| Endpoint | Path | Files | Coverage | Dimension complete? |
|---|---|---|---|---|
| Aggregates daily (OHLCV) | `cache/ohlcv/` | 2123 | **109%** ✅ (over universe) | Daily (no intraday in Stocks Starter) |
| Reference Tickers (sector/cap/IPO/exchange) | `legacy_archive_pass53/reference/` | 599 | **30.9%** 🔴 | Schema OK; coverage incomplete |
| Reference News | `news/` | 1926 | **99.4%** ✅ | Includes per-ticker insights |
| Reference Financials | `financials/` | 1746 | **90.1%** 🟡 | filing_date + period_of_report_date both populated |
| Reference Events (ticker_change) | `events/` | 1687 | **87.1%** 🟡 | Only ticker_change observed; spec says other event types possible |
| Reference Dividends | `legacy_archive_pass53/dividends/` | **2** | **0.1%** 🔴 | Sparse — likely 1500+ tickers actually pay dividends |
| Reference Splits | `legacy_archive_pass53/splits/` | **2** | **0.1%** 🔴 | Same |
| Snapshot endpoints (gainers/losers/most-active universe-snapshot) | — | 0 | **0%** ⚪ | NOT prefetched — Phase 1A doesn't need (real-time snapshots) |
| Grouped daily aggs (universe-wide) | — | 0 | **0%** ⚪ | Used for T3 build, not stored |
| Market Status / Holidays | — | 0 | **0%** ⚪ | Not prefetched |
| Conditions / Exchanges / Markets reference | — | 0 | **0%** ⚪ | Static reference; low priority |

### Quiver Trader

| Dataset | Path | Files | Coverage | Notes |
|---|---|---|---|---|
| congressional | `quiver/congressional/` | 509 | **26.3%** 🔴 | Old prefetch — pre-universe expansion |
| gov_contracts | `quiver/gov_contracts/` | 509 | **26.3%** 🔴 | Same |
| insider (per-ticker) | `quiver/insider/` | 509 | **26.3%** 🔴 | Same |
| insiders (bulk) | `quiver/insiders/global.parquet` | 1 | n/a | Bulk; canonical source |
| institutional (per-ticker) | `quiver/institutional/` | 509 | **26.3%** 🔴 | ~18% empty incl. AAPL — broken prefetch |
| sec13f (full bulk) | `quiver/sec13f/global.parquet` | 1 | n/a | Bulk; ~latest snapshot only |
| sec13fchanges (bulk) | `quiver/sec13fchanges/global.parquet` | 1 | n/a | Canonical; quarterly changes |
| lobbying | `quiver/lobbying/` | 509 | **26.3%** 🔴 | Old prefetch |
| offexchange (dark pool) | `quiver/offexchange/` | 1851 | **95.6%** ✅ | OK |
| topshareholders | `quiver/topshareholders/` | 1937 | **100%** ✅ | OK BUT no PIT dim (current snapshot only — INV-008) |
| wallstreetbets | `quiver/wallstreetbets/` | 509 | **26.3%** 🔴 | Old prefetch |
| wikipedia (Quiver mirror) | `quiver/wikipedia/` | 509 | **0% effective** 🔴 | Files exist but all empty (INV-006) |
| etfholdings | `quiver/etfholdings/` | 1563 | **80.7%** 🟡 | OK BUT no PIT dim (INV-008) |
| corporatedonors | `quiver/corporatedonors/global.parquet` | 1 | n/a | Bulk only; PIT cutoff via TransactionDate works |
| patentmomentum | `quiver/patentmomentum/global.parquet` | 1 | n/a | Bulk 5.8M rows; covers 1595 tickers but only through 2022 |
| quivernews | `quiver/quivernews/global.parquet` | 1 | n/a | General news (not per-ticker); 1500 rows |
| **POSSIBLY MISSING Quiver endpoints** | | | | Need API doc check |
| Twitter sentiment | — | 0 | — | Per-ticker tweet volume + sentiment |
| IPO calendar | — | 0 | — | Upcoming IPOs |
| SPACs tracker | — | 0 | — | SPAC universe + targets |
| Option flow | — | 0 | — | Unusual options activity |
| Earnings beats | — | 0 | — | Historical beats + post-announcement drift |
| Daily candle (price) | — | 0 | — | Overlap with Polygon — skip |

### SEC EDGAR

| Form Type | Path | Files | Coverage | Notes |
|---|---|---|---|---|
| Form 4 (insider transactions) | `sec_edgar/4/` | 1600 | **82.6%** 🟡 | Schema: ticker/cik/form/filing_date/accession_number/primary_doc |
| 8-K (material events) | `sec_edgar/8_K/` | 1543 | **79.7%** 🟡 | Same |
| SC 13D (activist 5%+) | `sec_edgar/SC_13D/` | 1244 | **64.2%** 🔴 | Same |
| SC 13G (passive 5%+) | `sec_edgar/SC_13G/` | 1669 | **86.2%** 🟡 | Same |
| **MISSING form types** | | | | |
| 10-K (annual report) | — | 0 | **0%** 🔴 | Major source for fundamentals timing |
| 10-Q (quarterly report) | — | 0 | **0%** 🔴 | Same |
| 13F-HR (institutional holdings) | — | 0 | **0%** 🟡 | Overlaps Quiver sec13fchanges; can skip |
| DEF 14A (proxy statement) | — | 0 | **0%** 🟡 | Compensation + governance signals |
| Form 3 (initial insider statement) | — | 0 | **0%** ⚪ | Less actionable than Form 4 |
| Form 5 (annual insider statement) | — | 0 | **0%** ⚪ | Less actionable |
| S-1 / S-1/A (IPO registration) | — | 0 | **0%** 🟡 | Pre-IPO data; useful for T2 spinoffs/IPOs |
| 11-K (employee benefit plans) | — | 0 | **0%** ⚪ | Low signal value |
| SC 13D/A + SC 13G/A amendments | — | 0 | **0%** 🟡 | Updates to original 13D/G filings |

### FRED

51 series in `data_prefetch/fred/observations/` — see file listing. **Missing per DEC-513 #7 spec:**
- VIX3M (3-month VIX implied vol)
- VVIX (vol of VIX)
- DTWEXBGS (broad dollar trade-weighted)
- T3MFF / TEDRATE (short-rate stress)
- DCOILWTICO (WTI crude)
- HOUST + PERMIT (housing)
- RSAFS (retail sales)
- IPB50001N (industrial production)

### ALFRED

50 vintage series matching FRED 50. **Same gaps as FRED** for series not yet added.

### Sentiment / search / community

| Source | Path | Files | Coverage | Gaps |
|---|---|---|---|---|
| AAII weekly sentiment | `aaii/weekly_sentiment.parquet` | 1 | global | Could add: allocation survey, investor confidence index |
| CNN F&G daily | `cnn_fg/daily.parquet` + components | 9 | global | Sprint 0A daily has 253 rows; legacy CSV has 1630 — already merged in code |
| CFTC COT | `cftc/cot_emini_sp500.parquet` | **1** | **only e-mini SP500** 🔴 | Missing: NQ, RTY, YM, VIX futures, crude, gold, treasuries, DXY, EUR/USD, etc. |
| Apewisdom | `apewisdom/global.parquet` | **1** | global only | Possibly per-ticker mention timeline available |
| pytrends | `pytrends/` | 1417 | **73.2%** 🟡 | Per-tkr SVI; could add geographic / related-query dims |
| Wikipedia pageviews | `wikipedia/` | 1414 | **73.0%** 🟡 | Per-tkr daily pageviews |

---

## Categorized prefetch gaps

### TIER A — Re-prefetch existing endpoints at full universe scope (cheap, high-value)

| # | Action | Effort | Why |
|---|---|---|---|
| A1 | Polygon reference: 599 → 1937 | 1-2h | Fixes 70% of `fetch_info()` calls returning sector=Unknown |
| A2 | Polygon dividends: 2 → ~1500 | 2-3h | Currently unusable for any dividend-yield strategy |
| A3 | Polygon splits: 2 → ~1500 | 2-3h | Same |
| A4 | Quiver `congressional` 509 → 1937 | 1-2h | Per-ticker rate-limited |
| A5 | Quiver `gov_contracts` 509 → 1937 | 1-2h | Same |
| A6 | Quiver `insider` 509 → 1937 | 1-2h | Same |
| A7 | Quiver `lobbying` 509 → 1937 | 1-2h | Same |
| A8 | Quiver `wallstreetbets` 509 → 1937 | 1-2h | Same |
| A9 | Quiver `etfholdings` 1563 → 1937 | 30 min | Top up |
| A10 | Polygon `financials` 1746 → 1937 | 30 min | Top up; some non-S&P names |
| A11 | Polygon `news` 1926 → 1937 | 5 min | Just a few missing |
| A12 | SEC EDGAR per-form 60-86% → 100% | 1h | Top up |

### TIER B — Add missing Quiver / SEC EDGAR endpoints (medium effort, opens new strategy capability)

| # | Action | Effort | Why |
|---|---|---|---|
| B1 | SEC EDGAR 10-K / 10-Q | 4-6h | 2 new form types × 1937 tkr; major fundamentals timing source |
| B2 | SEC EDGAR DEF 14A (proxy) | 2-3h | Compensation + governance signals |
| B3 | SEC EDGAR S-1 / S-1A (IPO) | 1-2h | IPO universe (T2 enrichment) |
| B4 | SEC EDGAR SC 13D/A + SC 13G/A amendments | 2h | Activist/passive holder updates |
| B5 | Quiver Twitter sentiment per-ticker (if available) | 2-3h | New retail-attention signal |
| B6 | Quiver IPO calendar | 1h | Forward IPO calendar for T2 prep |
| B7 | Quiver SPAC tracker | 1h | SPAC-specific universe |
| B8 | Quiver option flow | 2-3h | Unusual options activity |
| B9 | Quiver earnings beats | 2h | PEAD + post-announcement drift |
| B10 | Quiver patentmomentum extension to 2024-2026 | 2-3h | Currently only through 2022 |

### TIER C — Add missing FRED / CFTC series (cheap, fills DEC-513 gaps)

| # | Action | Effort | Why |
|---|---|---|---|
| C1 | FRED VIX3M + VVIX | 5 min | DEC-513 #7 explicit spec |
| C2 | FRED DTWEXBGS / T3MFF / DCOILWTICO / HOUST / PERMIT / RSAFS / IPB50001N | 15 min | DEC-513 macro signals |
| C3 | CFTC COT additional contracts (NQ/RTY/VIX/crude/gold/treasuries/DXY) | 30-60 min | Currently only e-mini SP500 |

### TIER D — Polygon endpoints not yet used (low priority pre-Phase-1A)

| # | Action | Effort | Why |
|---|---|---|---|
| D1 | Polygon snapshot endpoints | 30 min | Real-time only; Phase 1A doesn't need historical snapshots |
| D2 | Polygon market status / holidays | 5 min | Calendar metadata |
| D3 | Polygon Conditions / Exchanges / Markets reference | 5 min | Static reference data |

### TIER E — Fix broken prefetches

| # | Action | Effort | Why |
|---|---|---|---|
| E1 | Quiver wikipedia mirror — DELETE or repair | 30 min | All 509 files empty (INV-006) |
| E2 | Quiver institutional per-ticker — re-prefetch or accept | 1-2h | ~18% empty (INV-007); bulk works so optional |

---

## Recommended execution order

If owner approves all:

**Day 1 of remaining buffer (today / 2026-05-08):**
- Tier C (FRED + CFTC additions) — 1h total, fills DEC-513 gaps
- Tier A1-A11 (Polygon reference + dividends + splits + Quiver re-prefetches at full universe) — 8-12h aggregate; can run in parallel via background tasks

**Day 2 (2026-05-09):**
- Tier B1 (SEC EDGAR 10-K + 10-Q) — biggest single value-add for fundamentals timing
- Tier A12 (SEC EDGAR per-form top-up) — 1h
- Tier E1/E2 (cleanup) — 1-2h

**Day 3 (2026-05-10):**
- Tier B2-B4 (SEC EDGAR DEF 14A + S-1 + amendments)
- Tier B5-B10 (Quiver new endpoints — depends on what API offers)

**Day 4-5:**
- Buffer for re-runs / data validation / re-running smoke v3+v4 with fuller data
- Locks in all data before May 15 Phase 1A start.

**Estimated total: ~30-50 hours of API fetch time** (mostly unattended; rate-limited).

---

## Decisions needed from owner

1. **Approve all Tier A?** (re-prefetches at full universe scope — high value, mostly mechanical)
2. **Approve Tier B per-item?** (new endpoints — strategic decisions on which signals to enable)
3. **Approve Tier C?** (cheap; fills DEC-513 spec gaps)
4. **Defer Tier D?** (Polygon endpoints not currently needed; low priority)
5. **Tier E1 fix or delete Quiver wikipedia mirror?** (data integrity)

---

*Last updated: 2026-05-07 evening (Pass 53 Day-9 v8h)*
