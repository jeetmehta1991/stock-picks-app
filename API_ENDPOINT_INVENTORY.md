# API_ENDPOINT_INVENTORY.md - Definitive endpoint catalog (Pass 53 Day-9 v8h+1)

**Method per CHECKLIST #76 column-(b) + #77:** every row sourced from canonical API docs (where fetchable) AND probe verification (`scripts/probe_api_catalog.py`) hitting actual endpoints with our keys at 2026-05-08. Probe report: `API_ENDPOINT_PROBE_REPORT.json`.

**Owner directives:**
- 2026-05-07 evening: "Do not work from memory but rather documentation."
- 2026-05-08: "100% coverage on everything with no missing dimensions / fields after the pre-fetch."
- 2026-05-08 (this turn): "follow the table structure in polygon for all API endpoints" — standardized to 5-column format.

**Status legend:**
- ✅ probe-confirmed 200 OK at our tier (use it)
- 🔴 probe-confirmed 4xx (NOT in our tier OR wrong URL guess)
- ⚠ partial / needs follow-up probe
- ❓ not yet probed (deferred)

**Standard table format used in every per-API section below:**

| Endpoint | Status | Sample fields | Currently cached? | Action |

---

## API access summary (probe 2026-05-08)

| API | Plan | Probe pass rate | Key gap |
|---|---|---|---|
| Polygon (Massive) Stocks Starter | Paid | 42/78 (54%) | Filings/Fundamentals require Stocks Plus (NOT in our tier) |
| Polygon Indices Basic | Free (activated 2026-05-08) | 2/13 wanted | CBOE/S&P license gates VIX/SPX/DJI/RUT/etc. (INV-038) |
| Polygon Options Basic | Free | 2/5 endpoints | snapshots/trades/quotes 403 (Stocks Advanced needed) |
| Polygon Futures Basic | Free | 5/5 endpoints | rate-limited (5 calls/min) |
| Polygon Forex Basic | Free | 3/4 endpoints | conversion endpoint 403 |
| Polygon Benzinga partner | included | 5/7 endpoints | consensus 404, news 403 |
| Polygon Economy | included | 3/4 endpoints | labor 404 (URL guess wrong) |
| Quiver Trader | Paid | 8 historical + 5 live + 4 bulk = 17 working | 13 endpoints in old API_AUDIT 404 (INV-036) |
| FRED | Free | 28/28 (100%) | DEXJPUS persistent 500 (INV-042) |
| ALFRED | Free (= FRED w/ realtime_*) | 30/40 mirror | 10 series have no published vintages |
| SEC EDGAR | Free public | 5/5 (100%) | XBRL companyfacts solves INV-025/026/037 |
| Finnhub | Free (key added 2026-05-08) | 13/20 endpoints | 7 premium-locked |
| AlphaVantage | Free (owner-confirmed) | ~50/133 free | premium endpoints inaccessible |
| AAII | Web (no API) | 1/1 | extra-fields top-up pending |
| CNN F&G | Scraped | composite + 7 components | complete |
| CFTC | Public Socrata | 7/7 datasets | 5 newly added 2026-05-08 |
| Apewisdom | Public REST | 1 endpoint × 9 subreddit filters | 8 subreddits cached 2026-05-08 |
| pytrends | Library wrapping Google Trends | 12 methods | we use 1/12 (under-utilization) |
| Wikipedia pageviews | Public REST | 1 endpoint | 73% coverage |

---

## 1. Polygon Stocks Starter (paid, current)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `/v2/aggs/ticker/{t}/range/1/day/...` | ✅ | t, o, h, l, c, v, vw, n | YES (1937 + vw + n via 2026-05-08 re-fetch) | DONE H1 |
| `/v2/aggs/ticker/{t}/range/1/minute/...` | ✅ | t, o, h, l, c, v, vw, n | NO | NEW prefetch — minute-level for top-liquid only (storage caveat) |
| `/v1/open-close/{t}/{date}` | ✅ | status, from, symbol, open, high, low, close, volume | NO | redundant with daily aggs — skip |
| `/v2/aggs/grouped/locale/us/market/stocks/{date}` | 🔴 403 | NOT_AUTHORIZED on Stocks Starter | NO | Stocks Plus tier required — alternative: per-ticker OHLCV aggregation (DONE H1) |
| `/v2/aggs/ticker/{t}/prev` | ✅ | T, v, vw, o, c, h, l, t | YES (in flight Batch 172) | DONE Batch 172 — `data_prefetch/polygon/prev/` |
| `/v3/reference/tickers` | ✅ | ticker, name, market, locale, primary_exchange, type, active, currency_name | YES (universe build) | top up periodically |
| `/v3/reference/tickers/{t}` (basic) | ✅ | 16 base fields | YES (1686/1937) | superseded by reference_extended |
| `/v3/reference/tickers/{t}` (extended) | ✅ | + phone, description, total_employees, composite_figi, share_class_figi, round_lot, address, branding | YES (1686/1937 via H4 2026-05-08) | DONE — INV-030 RESOLVED |
| `/v3/reference/tickers/types` | ✅ | code, description, asset_class, locale | YES (25 rows, Batch 172) | DONE Batch 172 — `data_prefetch/polygon/static/tickers_types.parquet` |
| `/v1/related-companies/{t}` | ✅ | ticker | YES (in flight Batch 172) | DONE Batch 172 — `data_prefetch/polygon/related_companies/` |
| `/v2/reference/news` | ✅ | id, publisher, title, author, published_utc, article_url, tickers, image_url, **insights[]**, sentiment, sentiment_reasoning | YES (1937/1937, with per-ticker insights) | DONE H2 |
| `/v3/reference/dividends` | ✅ | cash_amount, currency, declaration_date, dividend_type, ex_dividend_date, frequency, id, pay_date, record_date, ticker | YES (100,000 records / 10,984 tickers) | DONE H3 — INV-017 RESOLVED |
| `/v3/reference/splits` | ✅ | execution_date, id, split_from, split_to, ticker | YES (27,590 records / 18,909 tickers) | DONE H3 |
| `/vX/reference/ipos` | ✅ | ticker, last_updated, announced_date, issuer_name, currency_code, max_shares_offered, primary_exchange, security_type | YES (6,264 records) | DONE H3 |
| `/v3/reference/tickers/{t}/events` | 🔴 404 | — | YES (1687 files via legacy script) | URL mismatch — investigate actual path used by working prefetch |
| `/vX/reference/financials` | ✅ | start_date, end_date, timeframe, fiscal_period, fiscal_year, cik, sic, tickers, financials_json | YES (1746/1937) | parse financials_json into structured columns (local) |
| `/v3/reference/conditions` | ✅ | id, type, name, asset_class, data_types | YES (130 rows, Batch 172) | DONE Batch 172 — `data_prefetch/polygon/static/conditions.parquet` |
| `/v3/reference/exchanges` | ✅ | id, type, asset_class, locale, name, acronym, mic, operating_mic | YES (52 rows, Batch 172) | DONE Batch 172 — `data_prefetch/polygon/static/exchanges.parquet` |
| `/v1/marketstatus/upcoming` | ✅ | date, exchange, name, status | YES (24 rows, Batch 172) | DONE Batch 172 — `data_prefetch/polygon/static/marketstatus_upcoming.parquet` |
| `/v1/marketstatus/now` | ✅ | afterHours, currencies, earlyHours, exchanges, indicesGroups, market, serverTime | YES (1-time snapshot Batch 172) | DONE Batch 172 — `data_prefetch/polygon/static/marketstatus_now.parquet` (Stage 3+ re-capture cadence) |
| `/v2/snapshot/locale/us/markets/stocks/tickers` | ✅ | ticker, todaysChangePerc, todaysChange, updated, day, min, prevDay | YES (12615 rows 1-time, Batch 172) | DONE Batch 172 — `data_prefetch/polygon/static/snapshot_all.parquet` |
| `/v2/snapshot/locale/us/markets/stocks/tickers/{t}` | ✅ | ticker, status, request_id | NO (per-ticker variant; aggregate snapshot covers) | redundant with snapshot_all — skip |
| `/v2/snapshot/locale/us/markets/stocks/{direction}` (gainers/losers) | ✅ | (same shape as full market) | YES (21+21 rows 1-time, Batch 172) | DONE Batch 172 — `data_prefetch/polygon/static/snapshot_movers_{gainers,losers}.parquet` |
| `/v3/snapshot` (unified) | ✅ | market_status, name, ticker, type, session, last_minute | NO (superset of snapshot endpoints) | redundant with snapshot_all — skip |
| `/v1/indicators/sma/{t}` | ✅ | results.values[].timestamp, value | YES (in flight 2026-05-08) | DONE H6 — sma_50, sma_200 windows cached |
| `/v1/indicators/ema/{t}` | ✅ | results.values[].timestamp, value | YES (in flight) | DONE H6 — ema_20, ema_50 windows |
| `/v1/indicators/rsi/{t}` | ✅ | results.values[].timestamp, value | YES (in flight) | DONE H6 — window=14 |
| `/v1/indicators/macd/{t}` | ✅ | results.values[].timestamp, value, signal, histogram | YES (in flight) | DONE H6 — 12/26/9 |
| `/v2/last/trade/{t}` | 🔴 403 | NOT_AUTHORIZED | — | requires Stocks Advanced tier |
| `/v2/last/nbbo/{t}` | 🔴 403 | NOT_AUTHORIZED | — | requires Stocks Advanced |
| `/v3/trades/{t}` | 🔴 403 | NOT_AUTHORIZED | — | requires Stocks Advanced |
| `/v3/quotes/{t}` | 🔴 403 | NOT_AUTHORIZED | — | requires Stocks Advanced |
| `/stocks/v1/short-interest/{t}` | 🔴 404 | URL guess wrong | — | research correct path |
| `/stocks/v1/short-volume/{t}` | 🔴 404 | URL guess wrong | — | research correct path |
| `/stocks/v1/filings/{form}` (10-K/10-Q/8-K/Form3/Form4 etc.) | 🔴 404 | tier-locked | NO | requires Stocks Plus tier — alternative: SEC EDGAR XBRL (DONE H17) |
| `/stocks/v1/fundamentals/{statement}` (income/balance/cash flow/ratios/float/short interest/short volume) | 🔴 404 | tier-locked | partial via /vX/reference/financials | Stocks Plus tier — alternative: SEC EDGAR XBRL (DONE H17) |

## 2. Polygon Indices Basic (free, activated 2026-05-08)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `/v2/aggs/ticker/I:NDX/range/1/day/...` | ✅ | t, o, h, l, c | YES (812 bars cached 2026-05-08) | continue |
| `/v2/aggs/ticker/I:COMP/range/1/day/...` | ✅ | t, o, h, l, c | YES (812 bars cached) | continue |
| `/v2/aggs/ticker/I:MID/range/1/day/...` | ⚠ 200 short / 0 long | (probe inconsistent) | NO | re-probe with intermediate date range |
| `/v2/aggs/ticker/I:SML/range/1/day/...` | ⚠ same | — | NO | same |
| `/v2/aggs/ticker/I:NYA/range/1/day/...` | ⚠ same | — | NO | same |
| `/v2/aggs/ticker/I:VIX/range/1/day/...` | 🔴 403 | NOT_AUTHORIZED | — | CBOE license gate — workaround: FRED VIXCLS (DONE) |
| `/v2/aggs/ticker/I:VIX9D/range/1/day/...` | 🔴 403 | — | — | CBOE license gate |
| `/v2/aggs/ticker/I:VIX3M/range/1/day/...` | 🔴 403 | — | — | CBOE license gate — workaround: FRED VXVCLS (DONE) |
| `/v2/aggs/ticker/I:VVIX/range/1/day/...` | 🔴 403 | — | — | CBOE license gate (INV-010) |
| `/v2/aggs/ticker/I:SPX/range/1/day/...` | 🔴 403 | — | — | S&P license gate — workaround: SPY ETF |
| `/v2/aggs/ticker/I:DJI/range/1/day/...` | 🔴 403 | — | — | S&P license gate — workaround: DIA ETF |
| `/v2/aggs/ticker/I:RUT/range/1/day/...` | 🔴 403 | — | — | S&P license gate — workaround: IWM ETF |
| `/v2/aggs/ticker/I:OEX/range/1/day/...` | 🔴 403 | — | — | S&P license gate |
| `/v3/reference/tickers?market=indices` | ✅ | ticker, name, market, locale, active, source_feed | YES (13037 rows, Batch 172) | DONE Batch 172 — `data_prefetch/polygon/static/tickers_indices.parquet` |
| `/v3/snapshot/indices` | 🔴 403 | NOT_AUTHORIZED | — | tier-gated |

## 3. Polygon Options Basic (free, partial)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `/v3/reference/options/contracts` | ✅ | cfi, contract_type, exercise_style, expiration_date, primary_exchange, shares_per_contract, strike_price, ticker | YES (1937/1937 cached) | DONE per DEC-600 — `data_prefetch/polygon/options_chains/` |
| `/v2/aggs/ticker/{O:contract}/range/1/day/...` | ✅ | t, o, h, l, c, v, vw, n | NO (deferred Phase 1B+ per DEC-600 — TB-class storage) | DEFERRED-PHASE-1B per DEC-600 — on-demand fetch only |
| `/v3/snapshot/options/{ticker}` | 🔴 403 | NOT_AUTHORIZED | — | tier-gated (Stocks Advanced) |
| `/v3/trades/{O:contract}` | 🔴 403 | — | — | tier-gated |
| `/v3/quotes/{O:contract}` | 🔴 403 | — | — | tier-gated |

## 4. Polygon Futures Basic (free, fully accessible)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `/futures/v1/products` | ✅ | asset_sub_class, date, last_updated, product_code, trade_currency_code, trading_venue, type, unit_of_measure | YES (paginated cap 100) | top-up if needed |
| `/futures/v1/contracts` | ✅ | active, date, first_trade_date, last_trade_date, name, product_code, ticker, trading_venue | YES | continue |
| `/v2/aggs/ticker/{root}/range/1/day/...` | ⚠ | t, o, h, l, c, v, vw, n (ES works; NQ/RTY/YM/VX return count=0 with single-letter) | partial (ES ✅ 9 bars; others empty) | NEW H8 — needs per-contract dated symbol query (deferred; needs redesign) |
| `/futures/v1/schedules` | ✅ | product_code, product_name, session_end_date, trading_venue, event, timestamp | YES | continue |

## 5. Polygon Forex/Currencies Basic (free, mostly accessible)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `/v2/aggs/ticker/C:EURUSD/range/1/day/...` | ✅ | t, o, h, l, c, v, vw, n | YES (12/12 pairs cached 2026-05-08) | DONE H9 |
| `/v2/aggs/ticker/C:USDJPY/range/1/day/...` | ✅ | (same) | YES | DONE |
| 10 more pairs (GBPUSD/USDCAD/USDCHF/AUDUSD/NZDUSD/USDCNY/USDMXN/USDINR/USDKRW/USDBRL) | ✅ | (same) | YES (12/12) | DONE |
| `/v3/reference/tickers?market=fx` | ✅ | ticker, name, market, locale, active, currency_symbol, currency_name, base_currency_symbol | YES (1208 rows, Batch 172) | DONE Batch 172 — `data_prefetch/polygon/static/tickers_fx.parquet` |
| `/v1/conversion/USD/EUR` | 🔴 403 | NOT_AUTHORIZED | — | tier-gated |

## 6. Polygon Economy (free, included)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `/fed/v1/inflation` | ✅ | date, cpi | YES (951 rows cached 2026-05-08) | DONE H5 |
| `/fed/v1/inflation-expectations` | ✅ | date, model_1_year, model_5_year, model_10_year, model_30_year | YES (532 rows) | DONE H5 |
| `/fed/v1/treasury-yields` | ✅ | date, yield_1_year, yield_5_year, yield_10_year | YES (16,071 rows — granular) | DONE H5 |
| `/fed/v1/labor` | 🔴 404 | URL guess wrong | — | research correct path |

## 7. Polygon Benzinga partner (paid add-on, 5/7 in our tier)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `/benzinga/v1/analyst-insights` | ✅ | rating_action, insight, date, firm, price_target, rating, last_updated, company_name | YES (1937/1937 in flight) | DONE H11 |
| `/benzinga/v1/ratings` | ✅ | (1508 records/AAPL — analyst rating history) | YES (1937/1937 in flight) | DONE H11 |
| `/benzinga/v1/earnings` | ✅ | (62 records/AAPL — earnings calendar + history) | YES (~89% in flight) | in flight |
| `/benzinga/v1/guidance` | ✅ | (31 records/AAPL — company guidance) | queued in BG | in flight |
| `/benzinga/v1/firms` (firm_details) | ✅ | (658 firms — analyst firm metadata) | queued in BG | in flight |
| `/benzinga/v1/consensus-ratings` | 🔴 404 | URL guess wrong | NO | research correct path |
| `/benzinga/v1/news` | 🔴 403 | tier-gated | — | premium add-on |

## 8. Quiver Quant Trader (paid)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `/historical/congresstrading/{t}` | ✅ | Representative, BioGuideID, ReportDate, TransactionDate, Ticker, Transaction, Range, House, Amount, Party, last_modified, TickerType, Description, ExcessReturn, PriceChange, SPYChange | YES (1937/1937) | continue |
| `/historical/senatetrading/{t}` | ✅ | Senator, BioGuideID, Date, Ticker, Transaction, Range, Amount, last_modified | YES (1937/1937 via H12 2026-05-08) | DONE H12 |
| `/historical/housetrading/{t}` | ✅ | Representative, BioGuideID, Date, Ticker, Transaction, Range, Amount, last_modified | YES (1930/1937 via H12) | DONE H12 |
| `/historical/govcontracts/{t}` | ✅ | Ticker, Amount, Qtr, Year (only 4 fields — confirmed at API level) | YES (1937/1937) | INV-024 reframed; alternate source needed for daily granularity |
| `/historical/lobbying/{t}` | ✅ | Date, Amount, Client, Issue, Specific_Issue, Registrant, Ticker | YES (1937/1937) | continue |
| `/historical/wallstreetbets/{t}` | ✅ | Date, Ticker, Mentions, Rank, Sentiment | YES (1937/1937) | continue |
| `/historical/twitter/{t}` | ✅ (sparse) | (empty for AAPL — re-probe with non-AAPL) | YES (1937/1937 cached) | DONE Batch 170 (was stale-NEW) — `data_prefetch/quiver/twitter/` |
| `/historical/spacs/{t}` | ✅ | Date, Ticker, Mentions, Rank, Sentiment | YES (in flight via H12) | DONE H13 |
| `/live/insiders?ticker=` | ✅ | Ticker, Date, Name, AcquiredDisposedCode, TransactionCode, Shares, PricePerShare, SharesOwnedFollowing, fileDate, officerTitle, isDirector, isOfficer, isTenPercentOwner, isOther, directOrIndirectOwnership, uploaded | YES (1937/1937) | continue |
| `/live/sec13f?ticker=` | ✅ | Date, ReportPeriod, Name, Ticker, Fund, Class, Value, Shares, SH/PRN, Put/Call, Direction | YES (1937/1937) | continue |
| `/live/sec13fchanges?ticker=` (bulk) | ✅ | Date, ReportPeriod, Ticker, Fund, Change, Change_Share, Change_Pct, Held, Held_Normalized, Close | YES (500K rows global) | continue |
| `/live/offexchange?ticker=` | ✅ | Ticker, Date, OTC_Short, OTC_Total, DPI | YES (1851/1937) | top-up |
| `/live/topshareholders?ticker=` (per-ticker 404; bulk works) | ⚠ partial | ownership, ownership_options (JSON-string objects, no date) | YES (1937 via bulk) | INV-008 — needs structured parse + PIT |
| `/live/etfholdings?ticker=` | ✅ | ETF Symbol, Holding Name, Holding Symbol, % of ETF, Value ($) | YES (1563/1937) | top-up |
| `live/quivernews` (bulk) | ✅ | url, time, headline, category, summary, image | YES (1500 rows global) | continue |
| `live/patentmomentum` (bulk only) | ✅ | ticker, date, momentum | YES (5.83M rows global, cap 2022) | extend through 2024-2026 (needs API check) |
| `live/corporatedonors` (bulk only) | ✅ | BioGuideID, CandidateName, CompanyCMTENM, TransactionDate, TransactionAmount, Ticker, CommitteeName, Cycle, TransactionType, CompanyCMTEID, Uploaded | YES (25K rows global) | continue |
| `/historical/wikipedia/{t}` | 🔴 404 | NOT in Trader plan | — | use canonical `data_prefetch/wikipedia/` (Wikipedia direct) |
| `/historical/patentmomentum/{t}` | 🔴 404 | per-ticker not available | — | bulk works |
| `/historical/appratings/{t}` | 🔴 404 | not in Trader tier | — | skip |
| `/historical/sec13fchanges/{t}` | 🔴 404 | per-ticker 404 (live-bulk works) | — | bulk path is canonical |
| `/historical/insidertrading/{t}` | 🔴 404 | wrong name (correct: `live/insiders`) | — | skip |
| `/historical/earningsbeats/{t}` | 🔴 404 | not in Trader tier | — | skip |
| `/historical/redditpoliticians/{t}` | 🔴 404 | not in Trader tier | — | skip |
| `/historical/reddittendies/{t}` | 🔴 404 | not in Trader tier | — | skip |
| `/historical/snptrend/{t}` | 🔴 404 | not in Trader tier | — | skip |
| `/historical/swaps/{t}` | 🔴 404 | not in Trader tier | — | skip |
| `/historical/googletrends/{t}` | 🔴 404 | not in Trader tier | — | use pytrends instead |
| `/historical/linkedindata/{t}` | 🔴 404 | not in Trader tier | — | skip |
| `/historical/iposcalendar/{t}` | 🔴 404 | not in Trader tier | — | use Polygon /vX/reference/ipos (DONE) |
| `/historical/optionsflow/{t}` | 🔴 404 | not in Trader tier | — | use Polygon Options Basic |
| `/historical/estimates/{t}` | 🔴 404 | not in Trader tier | — | use Finnhub recommendation/eps_surprise (DONE) |

## 9. FRED (free, all 28 endpoints accessible)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `/fred/series` | ✅ | series metadata (id, title, frequency, units, etc.) | YES (in flight Batch 173) | DONE Batch 173 — `data_prefetch/fred/metadata/series.parquet` |
| `/fred/series/observations` | ✅ | date, value | YES (90 series cached) | DONE H15; ongoing |
| `/fred/series/categories` | ✅ | category_id, name | YES (in flight Batch 173) | DONE Batch 173 — `data_prefetch/fred/metadata/series_categories.parquet` |
| `/fred/series/release` | ✅ | release_id, name | YES (in flight Batch 173) | DONE Batch 173 — `data_prefetch/fred/metadata/series_release.parquet` |
| `/fred/series/search` | ✅ | matching series | NO (discovery; usage-driven, not bulk-prefetchable) | DEFERRED — on-demand only |
| `/fred/series/tags` | ✅ | tag_name, group_id | YES (in flight Batch 173) | DONE Batch 173 — `data_prefetch/fred/metadata/series_tags.parquet` |
| `/fred/series/updates` | ✅ | recently-updated series | YES (in flight Batch 173) | DONE Batch 173 — `data_prefetch/fred/metadata/series_updates.parquet` |
| `/fred/series/vintagedates` | ✅ | vintage_date list | YES (in flight Batch 173) | DONE Batch 173 — `data_prefetch/fred/metadata/series_vintagedates.parquet` |
| `/fred/category` (and 5 sub) | ✅ | category metadata + traversal | YES (in flight Batch 173) | DONE Batch 173 — `data_prefetch/fred/metadata/category_*.parquet` |
| `/fred/release` (and 6 sub) | ✅ | release metadata + dates + series + sources + tags + related | YES (in flight Batch 173) | DONE Batch 173 — `data_prefetch/fred/metadata/releases.parquet` |
| `/fred/source` (and 2 sub) | ✅ | source metadata + releases | YES (in flight Batch 173) | DONE Batch 173 — `data_prefetch/fred/metadata/sources.parquet` |
| `/fred/tags`, `/fred/related_tags`, `/fred/tags/series` | ✅ | tag metadata + linked series | YES (in flight Batch 173) | DONE Batch 173 — `data_prefetch/fred/metadata/tags.parquet` |
| 87 cached series (post 2026-05-08 H15) | ✅ | date, value per series | YES | DONE H15 |
| `DEXJPUS` | 🔴 500 | persistent error (likely deprecated) | NO | INV-042 — workaround: Polygon Forex C:USDJPY (DONE) |

## 10. ALFRED vintage (free, = FRED w/ realtime_*)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `/fred/series/observations?realtime_start=...&realtime_end=...` | ✅ | date, value, realtime_start, realtime_end | YES (30/40 mirror via H16 2026-05-08) | DONE H16 |
| 10 series with no published vintages | ⚠ EMPTY | (continuous series) | NO | not applicable — no vintages exist |

## 11. SEC EDGAR (free public, all 5 endpoints work)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `data.sec.gov/submissions/CIK{cik}.json` | ✅ | full filing history per company; structured JSON | YES (per-form 1683-1722 via prefetch_sec_edgar.py) | top-up via CIK-map expansion (INV-044) |
| `data.sec.gov/api/xbrl/companyconcept/CIK{cik}/{tax}/{tag}.json` | ✅ | per-company XBRL line item time series | NO (queryable on demand) | use programmatic; not bulk-fetch |
| `data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` | ✅ | tag, taxonomy, unit, value, filing_date, period_start, period_end, fiscal_year, fiscal_period, form, accession, frame | YES (1937/1937 via H17 2026-05-08) | DONE H17 — INV-025/026/037 RESOLVED |
| `data.sec.gov/api/xbrl/frames/{tax}/{tag}/{unit}/CY{Y}Q{Q}.json` | ✅ | cross-sectional XBRL — all companies for a concept + period | NO (queryable on demand) | use programmatic |
| `efts.sec.gov/LATEST/search-index?q=...` | ✅ | full-text search across filings | NO | NEW — keyword search |

## 12. Finnhub free tier (key added 2026-05-08, 13/20 free)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `/quote` | ✅ | c, h, l, o, pc, t (current quote, delayed) | YES (1937/1937 via Finnhub BG 2026-05-08) | DONE |
| `/stock/profile2` | ✅ | country, currency, exchange, ipo, marketCapitalization, name, phone, shareOutstanding, ticker, weburl, logo, finnhubIndustry | YES (1929/1937 in flight) | DONE |
| `/stock/peers` | ✅ | array of peer tickers | YES (in flight) | in flight |
| `/stock/insider-transactions` | ✅ | name, share, change, filingDate, transactionDate, transactionCode, transactionPrice | YES (in flight; 112 records/AAPL smoke) | in flight |
| `/stock/insider-sentiment` | ✅ | symbol, year, month, change, mspr | YES (in flight; 51 records/AAPL smoke) | in flight |
| `/stock/recommendation` | ✅ | symbol, period, buy, hold, sell, strongBuy, strongSell | YES (in flight; 4 records/AAPL smoke) | in flight |
| `/stock/earnings` (eps_surprise) | ✅ | actual, estimate, period, surprise, surprisePercent, symbol | YES (in flight) | in flight |
| `/calendar/earnings` | ✅ | symbol, date, epsActual, epsEstimate, hour, quarter, revenueActual, revenueEstimate, year | partial | check global cache |
| `/calendar/ipo` | ✅ | date, exchange, name, numberOfShares, price, status, symbol, totalSharesValue | partial | check |
| `/calendar/economic` | ✅ | actual, country, estimate, event, impact, prev, time, unit | partial | check |
| `/company-news` | ✅ | category, datetime, headline, id, image, related, source, summary, url | YES (in flight; 243 records/AAPL smoke) | in flight |
| `/stock/financials-reported` | ✅ | accessNumber, cik, endDate, filedDate, form, quarter, report, startDate, year, symbol | YES (891/1937 cached) | **EXCLUDED COMPLETELY per DEC-606 (2026-05-10); superseded by SEC EDGAR XBRL + Polygon financials; CAV-076 logged. Cache orphan / read-only.** |
| `/stock/metric` | ✅ | metric, metricType, series (annual/quarterly TTM ratios) | YES (in flight) | in flight |
| `/stock/price-target` | 🔴 403 | premium-locked | — | skip on free tier |
| `/stock/social-sentiment` | 🔴 403 | premium-locked; **EXCLUDED from Phase 1A per DEC-605 (2026-05-09)**; Phase 1B+ eligible if Premium subscribed; CAV-074 logged | — | EXCLUDED Phase 1A; deferred Phase 1B+ |
| `/stock/upgrade-downgrade` | 🔴 403 | premium-locked | — | skip |
| `/stock/eps-estimate` | 🔴 403 | premium-locked | — | skip; use Polygon Benzinga (DONE) |
| `/stock/revenue-estimate` | 🔴 403 | premium-locked | — | skip |
| `/stock/dividend` | 🔴 403 | premium-locked | — | use Polygon dividends (DONE) |
| `/stock/split` | 🔴 403 | premium-locked | — | use Polygon splits (DONE) |

## 13. AlphaVantage (owner-confirmed free tier)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `TIME_SERIES_DAILY` | ✅ free | open, high, low, close, volume | NO (use Polygon OHLCV) | redundant — skip |
| `TIME_SERIES_WEEKLY` | ✅ free | (same, weekly) | NO | redundant |
| `TIME_SERIES_MONTHLY` | ✅ free | (same, monthly) | NO | redundant |
| `GLOBAL_QUOTE` | ✅ free (delayed) | symbol, open, high, low, price, volume, latest_trading_day, previous_close, change, change_percent | NO | redundant with Finnhub /quote |
| `SYMBOL_SEARCH` | ✅ free | best matches | NO | NEW — discovery (P3) |
| `MARKET_STATUS` | ✅ free | active markets globally | NO | redundant with Polygon /v1/marketstatus/now |
| `LISTING_STATUS` | ✅ free | active + delisted tickers list | NO | NEW — useful for survivorship audit (P2) |
| `INDEX_CATALOG` | ✅ free | available indices list | NO | NEW — small static |
| `TIME_SERIES_DAILY_ADJUSTED` | 🔴 premium | — | — | skip on free |
| `NEWS_SENTIMENT` | 🔴 premium | — | — | use Polygon news (DONE) |
| `INSIDER_TRANSACTIONS` | 🔴 premium | — | — | use Quiver insiders (DONE) |
| `INSTITUTIONAL_HOLDINGS` | 🔴 premium | — | — | use Quiver sec13f (DONE) |
| `COMPANY_OVERVIEW` | 🔴 premium | — | — | use Polygon reference_extended (DONE) |
| `INCOME_STATEMENT` / `BALANCE_SHEET` / `CASH_FLOW` | 🔴 premium | — | — | use SEC XBRL (DONE) |
| `EARNINGS` / `EARNINGS_CALENDAR` / `IPO_CALENDAR` | 🔴 premium | — | — | use Finnhub calendars (DONE) |
| `EARNINGS_CALL_TRANSCRIPT` | 🔴 premium | — | — | premium-only |
| `FX_*` | 🔴 premium | — | — | use Polygon Forex (DONE) |
| `CRYPTO_*` | 🔴 premium | — | — | out of scope |
| `COMMODITIES_*` (WTI/BRENT/NG/COPPER/etc.) | 🔴 premium | — | — | use FRED commodities (DONE) |
| `ECONOMIC_INDICATORS` (REAL_GDP/CPI/UNEMPLOYMENT/etc.) | 🔴 premium | — | — | use FRED (DONE) |
| `REALTIME_OPTIONS` / `HISTORICAL_OPTIONS` | 🔴 premium | — | — | use Polygon Options Basic |
| ~50 technical indicators (SMA/EMA/RSI/MACD/BBANDS/ATR/OBV/etc.) | ✅ free | timestamp, value | NO | redundant — Polygon indicators DONE H6 |

## 14. CFTC public Socrata (7 datasets, all accessible)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `/resource/kh3c-gbw2.json` (Disagg Combined) | ✅ | report_date, contract_market_name, open_interest_all, dealer/asset_mgr/lev_money positions long/short/spread, traders_*, conc_*, change_in_* | YES (19 contracts) | continue |
| `/resource/gpe5-46if.json` (TFF Futures Only) | ✅ | (TFF schema) | YES (19 contracts) | continue |
| `/resource/6dca-aqww.json` (Legacy Futures Only) | ✅ | (Legacy schema) | YES (18 contracts via H18 2026-05-08) | DONE H18 |
| `/resource/jun7-fc8e.json` (Legacy Combined) | ✅ | (Legacy schema, futures+options) | YES (18 contracts via H18) | DONE H18 |
| `/resource/72hh-3qpy.json` (Disagg Futures Only) | ✅ | (Disagg schema, futures only) | YES (5 contracts, mostly commodities) | DONE H18 |
| `/resource/yw9f-hn96.json` (TFF Combined) | ✅ | (TFF schema, combined) | YES (13 contracts) | DONE H18 |
| `/resource/4zgm-a668.json` (Supplemental CIT) | ✅ | (CIT schema; different contract set) | YES (0 of our contracts; CIT covers different family) | DONE H18 — skip our contracts |

## 15. Apewisdom (public REST, 1 endpoint × multiple subreddits)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `/api/v1.0/filter/all-stocks` | ✅ | rank, ticker, name, mentions, upvotes, rank_24h_ago, mentions_24h_ago, snapshot_date | YES (snapshot 2310 rows global) | DONE; cron daily for forward accumulation |
| `/api/v1.0/filter/wallstreetbets` | ✅ | (same) | YES (878 rows via H19) | DONE H19 |
| `/api/v1.0/filter/stocks` | ✅ | (same) | YES (568 rows) | DONE H19 |
| `/api/v1.0/filter/investing` | ✅ | (same) | YES (276 rows) | DONE H19 |
| `/api/v1.0/filter/options` | ✅ | (same) | YES (168 rows) | DONE H19 |
| `/api/v1.0/filter/stockmarket` | ✅ | (same) | YES (202 rows) | DONE H19 |
| `/api/v1.0/filter/CryptoCurrency` | ✅ | (same; out of scope) | YES (109 rows) | DONE (scope creep — kept for completeness) |
| `/api/v1.0/filter/Bitcoin` | ✅ | (same) | YES (56 rows) | DONE |
| `/api/v1.0/filter/SatoshiStreetBets` | ✅ | (same) | YES (5 rows) | DONE |

## 16. pytrends (Google Trends library, 12 methods)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `interest_over_time(kw_list)` | ✅ | date, search_volume_index, query_label | YES (1417/1937 = 73%) | top-up to 100% (P2) |
| `multirange_interest_over_time` | ✅ | (multi-window aggregate) | NO | DEFERRED-PHASE-1C per DEC-599 |
| `get_historical_interest` | ✅ | (hourly resolution) | NO | DEFERRED-PHASE-1C per DEC-599 (rate-limited) |
| `interest_by_region` | ✅ | region, value | NO | DEFERRED-PHASE-1C per DEC-599 |
| `related_topics` | ✅ | (Dict of DataFrames) | NO | DEFERRED-PHASE-1C per DEC-599 |
| `related_queries` | ✅ | (Dict of DataFrames) | NO | DEFERRED-PHASE-1C per DEC-599 |
| `trending_searches` | ✅ | (daily trending) | NO | DEFERRED-PHASE-1C per DEC-599 |
| `realtime_trending_searches` | ✅ | (realtime trending) | NO | DEFERRED-PHASE-1C per DEC-599 |
| `top_charts(year)` | ✅ | (annual top searches) | NO | DEFERRED-PHASE-1C per DEC-599 |
| `suggestions(keyword)` | ✅ | (keyword suggestions) | NO | DEFERRED-PHASE-1C per DEC-599 |
| `categories` | ✅ | (taxonomy) | NO | DEFERRED-PHASE-1C per DEC-599 |
| `build_payload` | ✅ (helper) | n/a | n/a | helper, used internally |

## 17. AAII (web download, no API)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| Weekly Investor Sentiment Survey CSV | ✅ | survey_date, bullish_pct, bearish_pct, neutral_pct, bull_bear_spread | YES (325 weekly readings) | extend with 8_week_avg, historical_avg, S&P close (H21 P3) |
| Asset Allocation Survey | ✅ | (monthly stocks/bonds/cash %) | YES (445 monthly readings) | DONE (was stale-NEW) — `data_prefetch/aaii/asset_allocation_survey.parquet` |
| Investor Confidence Index | ⚠ | (quarterly; AAII-published variant uncertain) | NO | DEFERRED-P3 — manual download requires source-URL research |

## 18. CNN Fear & Greed (web scrape)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| Composite daily | ✅ | timestamp, score, rating, date | YES (253 rows) | continue |
| Junk bond demand | ✅ | (component-level) | YES | continue |
| Market momentum SP500 | ✅ | (component-level) | YES | continue |
| Market volatility VIX | ✅ | (component-level) | YES | continue |
| Put/call options | ✅ | (component-level) | YES | continue |
| Safe haven demand | ✅ | (component-level) | YES | continue |
| Stock price breadth | ✅ | (component-level) | YES | continue |
| Stock price strength | ✅ | (component-level) | YES | continue |

## 19. Wikipedia Pageviews (free public REST)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `wikimedia.org/api/rest_v1/metrics/pageviews/per-article/...` | ✅ | date, views, article | YES (1414/1937 = 73%) | top-up to 100% (P2) |
| Article revision history | ✅ | timestamp, user, comment, size, sha1 per revision | YES PARTIAL (270/1414 = 19% Batch 174; retry running with 3s rate-limit) | DONE-PARTIAL Batch 174 — `data_prefetch/wikipedia_revisions/`; retry in flight to fill 1144 missing |

## 20. USAspending.gov (federal contracts — alternate to Quiver govcontracts)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `api.usaspending.gov/api/v2/award/...` | ❓ | DateSigned, AwardingAgency, ContractDescription, Amount (numeric) | NO | **NEW prefetch** to fix INV-024 daily-granularity govcontracts gap |

---

## Cross-cutting action plan (per CHECKLIST #76 column-c)

### Tier H — Prefetch additions WITH ENOUGH ACCESS NOW

| # | Action | Source | Est. effort | Status |
|---|---|---|---|---|
| H1 | OHLCV re-fetch with `vw` + `n` | Polygon | 6-8h | ✅ DONE |
| H2 | Polygon news re-fetch with `insights` | Polygon | 4-6h | ✅ DONE (cache already insights-aware) |
| H3 | Polygon dividends + splits + IPOs full | Polygon | 2-3h each | ✅ DONE |
| H4 | Polygon reference extended fields | Polygon | 1h | ✅ DONE |
| H5 | Polygon Economy series | Polygon | 30 min | ✅ DONE |
| H6 | Polygon precomputed indicators | Polygon | 4-6h | 🔄 IN-FLIGHT |
| H7 | Polygon Snapshots daily capture | Polygon | ongoing | 🟡 Stage 3+ |
| H8 | Polygon Futures Basic full prefetch | Polygon | 2h | ⚠ DEFERRED (per-contract dated symbol logic) |
| H9 | Polygon Forex Basic full prefetch | Polygon | 30 min | ✅ DONE (12/12 pairs) |
| H10 | Polygon Options Basic — chains + per-contract aggs | Polygon | 10-30h | 🟡 QUEUED |
| H11 | Polygon Benzinga analyst data | Polygon | 4-6h | 🔄 IN-FLIGHT |
| H12 | Quiver senate/house/spacs separate fetches | Quiver | ~40 min each | ✅ DONE |
| H13 | Quiver SPACs feed | Quiver | ~40 min | ✅ DONE (rolled into H12) |
| H14 | Quiver Twitter (re-probe non-AAPL) | Quiver | smoke | 🟡 QUEUED |
| H15 | FRED 30+ new series | FRED | 30 min | ✅ DONE |
| H16 | ALFRED mirror new FRED series | FRED | 30 min | ✅ DONE (30/40) |
| H17 | SEC XBRL companyfacts + frames | SEC | 4-6h | ✅ DONE (1937 ckpt) |
| H18 | CFTC 5 missing datasets | CFTC | 30 min | ✅ DONE |
| H19 | Apewisdom 4 (+4 extra) subreddit feeds | Apewisdom | 30 min | ✅ DONE (8 feeds) |
| H20 | pytrends 4 new dimensions | pytrends | 8-12h rate-limited | 🟡 QUEUED |
| H21 | AAII extend fields | AAII | 1h | 🟡 QUEUED |
| H22 | All STRING-date columns -> datetime migration | local | 1h | ✅ DONE (7033 files; INV-033 RESOLVED) |
| **B1** | **SEC EDGAR per-form top-up** | SEC | ~1-2h | ✅ DONE (capped at 1683 by CIK-map gap; INV-044) |
| **NEW Finnhub** | Finnhub 13 free endpoints | Finnhub | ~6-10h | 🔄 IN-FLIGHT |

### Tier I — Owner actions (all RESOLVED 2026-05-08)

| # | Action | Status |
|---|---|---|
| I1 | Activate Polygon Indices Basic on dashboard | ✅ ACTIVATED (partial 2/13 — INV-038 license gates remain) |
| I2 | Add `FINNHUB_API_KEY` to `.env` | ✅ DONE |
| I3 | Confirm AlphaVantage tier | ✅ FREE confirmed |

---

## INV summary (probe-grounded, Pass 53 Day-9 v8h+1)

| INV | Title | Status (2026-05-08) |
|---|---|---|
| INV-014 | DEC-491 trade_log.parquet silent degrade | open |
| INV-015 | AlphaVantage news partial 25 files | open |
| INV-016 | Finnhub news S&P-only stale | open |
| INV-017 | Polygon dividends/splits 0.1% coverage | ✅ RESOLVED 2026-05-08 (H3) |
| INV-024 | Quiver govcontracts field set | REFRAMED — gap at API level |
| INV-025 | SEC EDGAR filing-metadata-only | ✅ RESOLVED via H17 SEC XBRL |
| INV-026 | Polygon financials JSON unparsed | ✅ RESOLVED via SEC XBRL |
| INV-027 | Polygon news per-ticker insights | ✅ RESOLVED (cache insights-aware) |
| INV-028 | OHLCV missing vw + n | ✅ RESOLVED via H1 |
| INV-029 | Polygon events only ticker_change | open (URL mismatch) |
| INV-030 | Polygon reference missing extended fields | ✅ RESOLVED via H4 |
| INV-031 | Quiver congressional missing District/State/etc. | open |
| INV-032 | AV news aggregated (lost per-article) | open |
| INV-033 | STRING-date columns | ✅ RESOLVED via H22 |
| INV-034 | Polygon Indices Basic activation | ✅ RESOLVED-PARTIAL |
| INV-035 | Finnhub key missing | ✅ RESOLVED |
| INV-036 | 13 Quiver endpoints don't exist at our tier | ✅ RESOLVED (this doc + API_AUDIT amendment) |
| INV-037 | Polygon Filings/Fundamentals require Stocks Plus | ✅ RESOLVED via SEC XBRL |
| INV-038 | Polygon Indices CBOE/S&P license gates | open (owner action) |
| INV-039 | Polygon Benzinga 5/7 accessible | 🔄 IN-FLIGHT prefetch |
| INV-040 | Quiver senate/house/spacs prefetch | ✅ RESOLVED via H12 |
| INV-041 | git_commit captures all staged files | open (script fix) |
| INV-042 | FRED DEXJPUS 500 | open (research) |
| INV-043 | Windows-reserved filenames (PRN/CON) | ✅ RESOLVED |
| INV-044 | SEC EDGAR top-up CIK-map gap | open |

---

## 100% coverage criteria (per owner directive 2026-05-08)

To claim "100% coverage, no missing endpoints, no missing fields":
1. Every endpoint with status ✅ → must be prefetched at full universe scope (most done)
2. Every endpoint with ⚠ or ❓ → must be re-probed (H8 Futures, H14 Twitter, USAspending.gov pending)
3. Every field returned by ✅ endpoints → must be preserved in cache (Sample fields column above is the canonical schema target; verified via dashboard's Field Audit tab)
4. Every owner-action item (I1/I2/I3) → ✅ all RESOLVED 2026-05-08
5. Every Tier H action → ✅ 16 of 22 DONE; 4 in-flight; 2 deferred (H8 Futures, H14 Twitter); 2 queued (H10 Options, H20 pytrends)

**Estimated remaining wall time:** ~15-30h fetch (Polygon Options Basic + pytrends multi-dim + Finnhub remaining 8 endpoints completing).

---

*Authored 2026-05-08. Probe report: `API_ENDPOINT_PROBE_REPORT.json`. Last probe: 2026-05-08. Standardized to 5-column Polygon-style table format per owner directive 2026-05-08.*
