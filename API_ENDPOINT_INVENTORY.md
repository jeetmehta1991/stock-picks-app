# API_ENDPOINT_INVENTORY.md - Definitive endpoint catalog (Pass 53 Day-9 v8h+1 2026-05-08)

**Method per CHECKLIST #76 column-(b):** every row sourced from canonical API docs (where fetchable) AND probe verification (`scripts/probe_api_catalog.py`) hitting actual endpoints with our keys at 2026-05-08. Probe report at `API_ENDPOINT_PROBE_REPORT.json` (~150 endpoints).

**Owner directive 2026-05-07 (round 4):** no working from memory; ground every claim in docs + probe. End goal: 100% endpoint coverage at our plan tiers + 100% field-level coverage per endpoint.

**Status legend:**
- ✅ = probe-confirmed 200 OK at our tier (use it)
- 🔴 = probe-confirmed 4xx (NOT in our tier, or wrong URL)
- ⚠ = partial / needs follow-up probe
- ❓ = not yet probed (deferred)
- ❌ = doc-listed but no path candidate to probe

---

## API access summary (probe 2026-05-08)

| API | Plan | Probe pass rate | Key gap |
|---|---|---|---|
| Polygon (Massive) | Stocks Starter (paid) | 42/78 (54%) | Indices Basic NOT YET ACTIVATED; Filings/Fundamentals require higher tier |
| Quiver Quant | Trader (paid) | 19/50 (38%) | many endpoints listed in API_AUDIT.md don't exist; senatetrading + housetrading + spacs ARE accessible |
| FRED | Free | 28/28 (100%) | all endpoints work |
| ALFRED | Free (= FRED w/ realtime_*) | 1/1 (100%) | vintage cache should mirror FRED |
| SEC EDGAR | Free public | 5/5 (100%) | all 4 data.sec.gov endpoints + EFTS search work |
| Finnhub | Free (key) | SKIPPED | **`FINNHUB_API_KEY` missing from .env** — INV flag |
| AlphaVantage | Free | inferred from docs | NEWS_SENTIMENT requires premium per docs |
| AAII | Web (no API) | n/a | weekly survey CSV — current cache complete |
| CNN F&G | Scraped | n/a | composite + 7 components cached |
| CFTC | Public Socrata | 7 datasets exist | we have 2/7 |
| Apewisdom | Public REST | 2 endpoints | we have 1/2 effectively |
| pytrends | Library wrapping Google Trends | 12 methods | we use 1/12 |

---

## 1. Polygon (Massive) - probe-confirmed catalog

### Stocks Starter (paid - confirmed in our tier)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `/v2/aggs/ticker/{t}/range/1/day/...` | ✅ | v, vw, o, c, h, l, t, n | YES (1937 tickers) but missing vw + n | F6 P1 — re-fetch with vw + n |
| `/v2/aggs/ticker/{t}/range/1/minute/...` | ✅ | v, vw, o, c, h, l, t, n | NO | NEW prefetch — minute-level for top liquid tickers |
| `/v1/open-close/{t}/{date}` | ✅ | status, from, symbol, open, high, low, close, volume | NO | redundant with daily aggs — skip |
| `/v2/aggs/grouped/locale/us/market/stocks/{date}` | ✅ | T, v, vw, o, c, h, l, t | NO (used for T3 build) | NEW — daily snapshot capture for liquidity ranking |
| `/v2/aggs/ticker/{t}/prev` | ✅ | T, v, vw, o, c, h, l, t | NO | NEW — daily previous-close |
| `/v3/reference/tickers` | ✅ | ticker, name, market, locale, primary_exchange, type, active, currency_name | YES (universe build) | top up |
| `/v3/reference/tickers/{t}` | ✅ | (16 fields cached; missing address/branding/employees/FIGI/desc) | YES (1686/1937) | F5 P2 — extend fields |
| `/v3/reference/tickers/types` | ✅ | code, description, asset_class, locale | NO | NEW small static — cache |
| `/v1/related-companies/{t}` | ✅ | ticker | NO | **NEW — peer-companies signal**, P2 |
| `/v2/reference/news` | ✅ | id, publisher, title, author, published_utc, article_url, tickers, image_url, **insights**, keywords | YES (1926/1937) but missing insights/author/image_url/keywords | F2 P1 — re-fetch with full schema |
| `/v3/reference/dividends` | ✅ | cash_amount, currency, declaration_date, dividend_type, ex_dividend_date, frequency, id, pay_date, record_date, ticker | YES (1 file) | F-new P0 — full universe re-prefetch |
| `/v3/reference/splits` | ✅ | execution_date, id, split_from, split_to, ticker | YES (1 file) | F-new P0 — full universe re-prefetch |
| `/vX/reference/ipos` | ✅ | ticker, last_updated, announced_date, issuer_name, currency_code, max_shares_offered, primary_exchange, security_type | NO | **NEW — IPO signal** |
| `/v3/reference/tickers/{t}/events` | 🔴 404 | — | YES (1687 files via prefetch_polygon_corp_actions.py) | URL mismatch — verify actual path used by working prefetch |
| `/vX/reference/financials` | ✅ | start_date, end_date, timeframe, fiscal_period, fiscal_year, cik, sic, tickers, financials_json | YES (1746/1937) | F3 P1 — local processing to extract line items |
| `/v3/reference/conditions` | ✅ | id, type, name, asset_class, data_types | NO | NEW small static — cache |
| `/v3/reference/exchanges` | ✅ | id, type, asset_class, locale, name, acronym, mic, operating_mic | NO | NEW small static — cache |
| `/v1/marketstatus/upcoming` | ✅ | date, exchange, name, status | NO (stub dir) | NEW — cache once |
| `/v1/marketstatus/now` | ✅ | afterHours, currencies, earlyHours, exchanges, indicesGroups, market, serverTime | NO | NEW — daily snapshot capture |
| `/v2/snapshot/locale/us/markets/stocks/tickers` | ✅ | ticker, todaysChangePerc, todaysChange, updated, day, min, prevDay | NO | NEW — daily snapshot capture |
| `/v2/snapshot/locale/us/markets/stocks/tickers/{t}` | ✅ | ticker, status, request_id | NO | NEW — daily per-ticker snapshot |
| `/v2/snapshot/locale/us/markets/stocks/{direction}` (gainers/losers) | ✅ | (same shape as full market) | NO | NEW — daily top-movers capture |
| `/v3/snapshot` | ✅ | market_status, name, ticker, type, session, last_minute | NO | NEW — unified snapshot |
| `/v1/indicators/sma/{t}` | ✅ | results, status, request_id | NO | **NEW — pre-computed SMA**, P2 (own compute is fine but cache to save time) |
| `/v1/indicators/ema/{t}` | ✅ | results | NO | NEW |
| `/v1/indicators/rsi/{t}` | ✅ | results | NO | NEW |
| `/v1/indicators/macd/{t}` | ✅ | results | NO | NEW |
| `/v2/last/trade/{t}` | 🔴 403 | NOT_AUTHORIZED | — | requires Stocks Advanced |
| `/v2/last/nbbo/{t}` | 🔴 403 | — | — | requires Stocks Advanced |
| `/v3/trades/{t}` | 🔴 403 | — | — | requires Stocks Advanced |
| `/v3/quotes/{t}` | 🔴 403 | — | — | requires Stocks Advanced |
| `/stocks/v1/short-interest/{t}` | 🔴 404 | — | — | URL incorrect; probe other paths |
| `/stocks/v1/short-volume/{t}` | 🔴 404 | — | — | URL incorrect; probe other paths |
| `/stocks/v1/filings/{form}` | 🔴 404 | — | NO | Massive Filings feature requires Stocks Plus tier — NOT in our tier; SEC EDGAR direct is the alternative |
| `/stocks/v1/fundamentals/{statement}` | 🔴 404 | — | partial via /vX/reference/financials | structured fundamentals require Stocks Plus tier |

### Economy (probe-confirmed)

| Endpoint | Status | Sample fields | Currently cached? | Action |
|---|---|---|---|---|
| `/fed/v1/inflation` | ✅ | date, cpi | NO | **NEW — duplicates FRED CPIAUCSL but as alternative source** |
| `/fed/v1/inflation-expectations` | ✅ | date, model_1_year, model_5_year, model_10_year, model_30_year | NO | **NEW — Massive's own inflation expectations model**; richer than FRED T10YIE |
| `/fed/v1/treasury-yields` | ✅ | date, yield_1_year, yield_5_year, yield_10_year | NO | NEW — alternative source for treasury yields |
| `/fed/v1/labor` | 🔴 404 | — | — | URL guess wrong; probe alternatives |

### Indices Basic (FREE plan upgrade — owner said they would add)

**Probe finding: 403 NOT_AUTHORIZED on most index symbols (I:SPX, I:DJI, I:RUT, I:VIX, etc.). Indices Basic is NOT YET ACTIVATED on the account.**

| Symbol | Probe status |
|---|---|
| I:SPX | 🔴 403 |
| I:NDX | ✅ 200 (single exception — odd) |
| I:DJI | 🔴 403 |
| I:RUT | 🔴 403 |
| I:VIX | 🔴 403 |
| I:VIX9D | 🔴 403 |
| I:VIX3M | 🔴 403 |
| I:VVIX | 🔴 403 |
| I:OEX | 🔴 403 |

**ACTION REQUIRED FROM OWNER:** activate Indices Basic plan via massive.com dashboard. Once activated, re-probe + start prefetch.

### Options Basic (PARTIAL access)

| Endpoint | Status | Notes |
|---|---|---|
| `/v3/reference/options/contracts` | ✅ | full chain reference |
| `/v2/aggs/ticker/{O:contract}/range/1/day/...` | ✅ | per-contract OHLCV (vw + n included) |
| `/v3/snapshot/options/{ticker}` | 🔴 403 | NOT_AUTHORIZED |
| `/v3/trades/{O:contract}` | 🔴 403 | — |
| `/v3/quotes/{O:contract}` | 🔴 403 | — |

Conclusion: Options Basic gives us **chains + OHLCV per contract** but not snapshots/trades/quotes. **Sufficient for put/call ratio + volume + OI tracking.** Greeks/IV would need higher tier.

### Futures Basic (FULLY ACCESSIBLE)

| Endpoint | Status | Sample fields |
|---|---|---|
| `/futures/v1/contracts` | ✅ | active, date, first_trade_date, last_trade_date, name, product_code, ticker, trading_venue |
| `/futures/v1/products` | ✅ | asset_sub_class, date, last_updated, product_code, trade_currency_code, trading_venue, type, unit_of_measure |
| `/v2/aggs/ticker/ES/range/1/day/...` | ✅ | v, vw, o, c, h, l, t, n |
| `/v2/aggs/ticker/VX/range/1/day/...` | ✅ | (same) |
| `/futures/v1/schedules` | ✅ | product_code, product_name, session_end_date, trading_venue, event, timestamp |

**ACTION:** prefetch ALL futures contracts available — ~25-30 contracts × 6 years × daily = trivial.

### Currencies/Forex Basic (MOSTLY ACCESSIBLE)

| Endpoint | Status |
|---|---|
| `/v2/aggs/ticker/C:EURUSD/range/1/day/...` | ✅ |
| `/v2/aggs/ticker/C:USDJPY/range/1/day/...` | ✅ |
| `/v3/reference/tickers?market=fx` | ✅ |
| `/v1/conversion/USD/EUR` | 🔴 403 |

### Partner Data

| Endpoint | Status | Notes |
|---|---|---|
| `/benzinga/v1/analyst-insights` | ✅ | rating_action, insight, date, firm, price_target, rating, last_updated, company_name |
| `/etfg/v1/constituents` | 🔴 404 | URL guess wrong; check actual path |
| `/tmx/v1/corporate-events` | 🔴 403 | TMX is paid add-on |

**SURPRISING WIN:** Benzinga analyst data is in our tier! That's analyst recommendations, ratings, price targets, firm details — major Phase 1B+ signal. **NEW prefetch P1.**

---

## 2. Quiver Quant (probe-confirmed)

### Working endpoints (200)

| Endpoint | Path | Sample fields | Currently cached? |
|---|---|---|---|
| congresstrading | `/historical/congresstrading/{t}` | Representative, BioGuideID, ReportDate, TransactionDate, Ticker, Transaction, Range, House (per probe) | YES 1937 |
| **senatetrading** | `/historical/senatetrading/{t}` | Senator, BioGuideID, Date, Ticker, Transaction, Range, Amount, last_modified | **NO — NEW** |
| **housetrading** | `/historical/housetrading/{t}` | Representative, BioGuideID, Date, Ticker, Transaction, Range, Amount, last_modified | **NO — NEW** |
| govcontracts | `/historical/govcontracts/{t}` | **Ticker, Amount, Qtr, Year (only 4 fields — confirmed at API level)** | YES 1937 |
| lobbying | `/historical/lobbying/{t}` | Date, Amount, Client, Issue, Specific_Issue, Registrant, Ticker | YES 1937 |
| wallstreetbets | `/historical/wallstreetbets/{t}` | Date, Ticker, Mentions, Rank, Sentiment | YES 1937 |
| twitter | `/historical/twitter/{t}` | (empty for AAPL — INV-012 confirmed) | NO |
| **spacs** | `/historical/spacs/{t}` | Date, Ticker, Mentions, Rank, Sentiment | **NO — NEW** |
| live insiders | `/live/insiders?ticker=` | Ticker, Date, Name, AcquiredDisposedCode, TransactionCode, Shares, PricePerShare, SharesOwnedFollowing | YES 1937 |
| live sec13f | `/live/sec13f?ticker=` | Date, ReportPeriod, Name, Ticker, Fund, Class, Value, Shares | YES 1937 |
| live sec13fchanges | `/live/sec13fchanges?ticker=` | Date, ReportPeriod, Ticker, Fund, Change, Change_Share, Change_Pct, Held | YES bulk |
| live offexchange | `/live/offexchange?ticker=` | Ticker, Date, OTC_Short, OTC_Total, DPI | YES 1851 |

### NOT in our tier OR wrong path (404)

| Endpoint | Probe path | Status |
|---|---|---|
| historical/wikipedia | `/historical/wikipedia/{t}` | 🔴 404 (NOT in Trader plan) |
| historical/patentmomentum | per-ticker | 🔴 404 (only bulk available) |
| historical/appratings | per-ticker | 🔴 404 |
| historical/sec13fchanges | per-ticker | 🔴 404 (only live-bulk works) |
| historical/insidertrading | `/historical/insidertrading/{t}` | 🔴 404 (different name — `live/insiders` is the working one) |
| historical/earningsbeats | per-ticker | 🔴 404 |
| historical/redditpoliticians | per-ticker | 🔴 404 |
| historical/reddittendies | per-ticker | 🔴 404 |
| historical/snptrend | per-ticker | 🔴 404 |
| historical/swaps | per-ticker | 🔴 404 |
| historical/googletrends | per-ticker | 🔴 404 |
| historical/linkedindata | per-ticker | 🔴 404 |
| historical/iposcalendar | per-ticker | 🔴 404 |
| historical/optionsflow | per-ticker | 🔴 404 |
| historical/estimates | per-ticker | 🔴 404 |
| live topshareholders | per-ticker | 🔴 404 (only bulk works — see existing cache) |

**REFRAMING INV-024:** Quiver govcontracts API actually returns ONLY 4 fields (Ticker/Amount/Qtr/Year). Our prefetch IS faithful — the field-level gap is at the **API level**, not at our prefetch level. The "missing Date / AwardingAgency / DepartmentDescription" hypothesis was WRONG. Daily-granularity gov contracts must come from an alternate source (USAspending.gov direct or SEC EDGAR).

### NEW Quiver endpoints to add

| # | Endpoint | Action |
|---|---|---|
| Q1 | `/historical/senatetrading/{t}` | **NEW prefetch** — 1937 × 1.2s = ~40 min |
| Q2 | `/historical/housetrading/{t}` | **NEW prefetch** — same |
| Q3 | `/historical/spacs/{t}` | **NEW prefetch** — same; SPAC mention timeline |
| Q4 | `/historical/twitter/{t}` (full universe) | re-probe with non-AAPL tickers — INV-012 was 1-ticker test |

---

## 3. FRED (28/28 working)

All endpoints functional. Available beyond what we use today:

| Endpoint | Currently used | Action |
|---|---|---|
| `/fred/series` | NO | NEW — series metadata |
| `/fred/series/observations` | YES | continue |
| `/fred/series/categories` | NO | NEW — find related series |
| `/fred/series/release` | NO | NEW — release schedule |
| `/fred/series/search` | NO | NEW — discovery |
| `/fred/series/tags` | NO | NEW |
| `/fred/series/updates` | NO | NEW — staleness check |
| `/fred/series/vintagedates` | NO | NEW — ALFRED PIT support |
| `/fred/category` + 5 sub-endpoints | NO | NEW — category traversal |
| `/fred/release` + 6 sub-endpoints | NO | NEW — release calendar |
| `/fred/source` + 2 sub-endpoints | NO | NEW |
| `/fred/tags`, `/fred/related_tags`, `/fred/tags/series` | NO | NEW |
| ALFRED vintage observations | partial (50 series) | extend to mirror full FRED set |

**ACTION P0:** add 25-30 important FRED series we don't have (TIPS yields, additional yield-curve points, regional Fed indices, sector employment, Money Market). See INV-N.

---

## 4. SEC EDGAR (5/5 working - all FREE)

| Endpoint | Status | What it provides |
|---|---|---|
| `data.sec.gov/submissions/CIK{cik}.json` | ✅ | Full filing history per company; structured JSON. **MUCH richer than our current prefetch (filing metadata only).** |
| `data.sec.gov/api/xbrl/companyconcept/CIK{cik}/{taxonomy}/{tag}.json` | ✅ | **Per-company XBRL line item time series** — e.g. Revenues over time. Solves INV-025/026 partially! |
| `data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` | ✅ | **All XBRL facts for a company** — comprehensive structured fundamentals |
| `data.sec.gov/api/xbrl/frames/{tax}/{tag}/{unit}/CY{Y}Q{Q}.json` | ✅ | Cross-sectional XBRL — all companies for a given concept + period |
| `efts.sec.gov/LATEST/search-index?q=...` | ✅ | Full-text search across filings |

**MAJOR FINDING:** SEC EDGAR XBRL data API directly provides STRUCTURED fundamentals — solves INV-025 (filing-metadata-only) and INV-026 (financials_json unparsed). We can fetch parsed line items for free.

**ACTION P0:** new prefetch script `scripts/prefetch_sec_xbrl.py` for company facts + frames. ~1937 tickers × 1 call each + frames per concept = manageable.

---

## 5. Finnhub - SKIPPED (NO API KEY)

INV finding: `FINNHUB_API_KEY` not in `.env`. Owner mentioned having a key.

**ACTION REQUIRED FROM OWNER:** add `FINNHUB_API_KEY` to `.env` so probe can run.

Anticipated catalog (from training data — to be probe-verified once key available):
- /quote, /stock/profile2, /stock/peers, /stock/insider-transactions, /stock/insider-sentiment, /stock/recommendation, /stock/price-target, /stock/upgrade-downgrade, /stock/eps-surprise, /stock/revenue-estimate, /stock/eps-estimate, /stock/dividend, /stock/split, /stock/social-sentiment, /calendar/earnings, /calendar/ipo, /calendar/economic, /news, /company-news, /news-sentiment, /scan/pattern, /scan/support-resistance, /etf/holdings, /index/constituents, /stock/financials-reported, /stock/metric, /stock/ownership, /stock/fund-ownership, +others

---

## 6. AlphaVantage (catalog from official docs)

133 functions cataloged from `https://www.alphavantage.co/documentation/` (WebFetch successful). Free tier limited to:
- TIME_SERIES_DAILY/WEEKLY/MONTHLY (NOT _ADJUSTED on free)
- GLOBAL_QUOTE (delayed)
- SYMBOL_SEARCH, MARKET_STATUS, LISTING_STATUS, INDEX_CATALOG
- ~50 technical indicators (SMA, EMA, RSI, MACD, BBANDS, ATR, etc.)

Premium-only (have key but unclear which tier): NEWS_SENTIMENT, INSIDER_TRANSACTIONS, INSTITUTIONAL_HOLDINGS, COMPANY_OVERVIEW, INCOME/BALANCE/CASH_FLOW, EARNINGS_*, IPO_CALENDAR, FX_*, COMMODITIES, ECONOMIC_INDICATORS, REALTIME_OPTIONS, EARNINGS_CALL_TRANSCRIPT, etc.

**ACTION:** verify AV plan tier with owner. If premium, re-probe these (INV-015 fix).

---

## 7. CFTC (7 datasets)

From CFTC docs (WebFetch successful):

| Dataset | Socrata ID | Have? | Action |
|---|---|---|---|
| Legacy Futures Only | 6dca-aqww | NO | NEW — historical-baseline COT (older) |
| Legacy Combined | jun7-fc8e | NO | NEW |
| Disaggregated Futures Only | 72hh-3qpy | NO | NEW |
| Disaggregated Combined | kh3c-gbw2 | YES | continue |
| TFF Futures Only | gpe5-46if | YES | continue |
| TFF Combined | yw9f-hn96 | NO | NEW |
| Supplemental CIT | 4zgm-a668 | NO | NEW — Commercial Index Trader |

**ACTION:** add 5 missing datasets. ~30 min.

---

## 8. Apewisdom (2 endpoints)

From docs:
- `/api/v1.0/filter/{filter}` (single page)
- `/api/v1.0/filter/{filter}/page/{N}` (paginated)

Filters: `all`, `all-stocks`, `all-crypto`, `wallstreetbets`, `stocks`, `investing`, `options`, `CryptoCurrency`, `Bitcoin`, `SatoshiStreetBets`, +7 others.

We currently fetch: `all-stocks` only.

**ACTION:** add subreddit-specific timelines (`wallstreetbets`, `stocks`, `investing`, `options` — 4 new). +9 if we want all.

---

## 9. pytrends (12 methods)

| Method | Currently used | Action |
|---|---|---|
| `interest_over_time` | YES | continue |
| `multirange_interest_over_time` | NO | NEW — multi-window |
| `get_historical_interest` | NO | NEW — hourly resolution |
| `interest_by_region` | NO | NEW — geographic |
| `related_topics` | NO | NEW — co-search |
| `related_queries` | NO | NEW |
| `trending_searches` | NO | NEW — daily trending |
| `realtime_trending_searches` | NO | NEW |
| `top_charts` | NO | NEW — annual top searches |
| `suggestions` | NO | NEW |
| `categories` | NO | NEW — taxonomy |
| `build_payload` | YES (helper) | n/a |

We use 1/12 methods. **MAJOR under-utilization.**

---

## 10. AAII (no API; CSV-only)

Single weekly survey publication. Cache complete (325 weekly readings).

**Missing fields per AAII publication that we don't capture:** 8_week_avg, historical_avg, S&P_500_close. ~1h to add.

**Other AAII publications:** Asset Allocation Survey (monthly), Investor Confidence Index (quarterly) — not yet cached. Both manual download.

---

## 11. CNN Fear & Greed

Composite + 7 components currently cached (per DEC-498). All available components captured.

---

## Cross-cutting action plan (per CHECKLIST #76 column-c)

### Tier H — Prefetch additions WITH ENOUGH ACCESS NOW (no owner action needed)

| # | Action | Source | Est. effort | Priority |
|---|---|---|---|---|
| H1 | OHLCV re-fetch with `vw` + `n` | Polygon | 6-8h | P1 (INV-028) |
| H2 | Polygon news re-fetch with `insights` + author + image_url + keywords | Polygon | 4-6h | P1 (INV-027) |
| H3 | Polygon dividends + splits full universe | Polygon | 2-3h each | P1 (INV-017) |
| H4 | Polygon IPOs + reference fields (address/branding/employees/FIGI) | Polygon | 2h | P2 (INV-030) |
| H5 | Polygon Economy series (inflation, inflation_exp, treasury_yields) | Polygon | 30 min | P2 |
| H6 | Polygon precomputed indicators (SMA/EMA/RSI/MACD) | Polygon | 4-6h | P2 |
| H7 | Polygon Snapshots daily capture (cron) | Polygon | ongoing | P3 (Stage 3+) |
| H8 | **Polygon Futures Basic full prefetch** (~25 contracts × 6 years) | Polygon | 2h | P1 |
| H9 | **Polygon Forex Basic full prefetch** (~10 pairs × 6 years) | Polygon | 30 min | P1 |
| H10 | **Polygon Options Basic** — chains + per-contract aggs for full universe (top liquid first) | Polygon | 10-30h | P1 |
| H11 | Polygon Benzinga analyst data | Polygon | 4-6h | **P1 — major signal** |
| H12 | **Quiver senate/house trading separate fetches** | Quiver | ~40 min each | P1 |
| H13 | Quiver SPACs feed | Quiver | ~40 min | P2 |
| H14 | Quiver Twitter (re-probe with non-AAPL tickers) | Quiver | smoke | P2 |
| H15 | FRED additions (TIPS, productivity, regional Fed, sector employment) | FRED | 30 min | P2 |
| H16 | ALFRED mirror for new FRED series | FRED | 30 min | P2 |
| H17 | **SEC XBRL companyfacts + frames** (structured fundamentals — solves INV-025/026 partially) | SEC | 4-6h | **P0** |
| H18 | CFTC 5 missing datasets (Legacy + Disaggregated Futures Only + TFF Combined + Supp CIT) | CFTC | 30 min | P2 |
| H19 | Apewisdom 4 new subreddit feeds | Apewisdom | 30 min ongoing | P2 |
| H20 | pytrends 4 new dimensions (interest_by_region, related_queries, related_topics, get_historical_interest) | pytrends | 8-12h rate-limited | P2 |
| H21 | AAII extend fields (8wk avg, historical avg, S&P close) | AAII | 1h | P3 |
| H22 | All STRING-date columns -> datetime migration | local | 1h | P3 (INV-033) |

### Tier I — Owner actions required

| # | Action | Owner action |
|---|---|---|
| I1 | Activate Polygon Indices Basic on dashboard | adds free | once active, prefetch I:VIX/I:SPX/I:NDX/I:VIX3M/I:VVIX etc. |
| I2 | Add `FINNHUB_API_KEY` to `.env` | adds key | enables Finnhub probe + prefetch |
| I3 | Confirm AlphaVantage tier | clarifies | unblocks AV NEWS_SENTIMENT re-prefetch |

---

## INV updates from probe

- **INV-024 reframed:** Quiver govcontracts API returns ONLY 4 fields at API level. Our prefetch is faithful. The "Date / AwardingAgency / DepartmentDescription" gap is at the API contract, not at our save logic. Daily-granularity gov contracts requires alternate source (USAspending.gov / SEC).
- **INV-025/026 partially solvable** via SEC EDGAR XBRL companyfacts + frames endpoints (free). Not via Polygon Filings (404 — not in our tier).
- **NEW INV (numbered next): Polygon Indices Basic NOT YET ACTIVATED** — owner action needed.
- **NEW INV: Finnhub API key missing from .env** — owner action needed.
- **NEW INV: 13 Quiver endpoints in API_AUDIT.md don't exist at our Trader tier** (returned 404 on probe). Need API_AUDIT.md correction.

---

## 100% coverage criteria (per owner directive 2026-05-08)

To claim "100% coverage, no missing endpoints, no missing fields":
1. Every endpoint listed above with status ✅ → must be prefetched at full universe scope
2. Every endpoint with ⚠ or ❓ → must be re-probed and resolved to ✅ or 🔴
3. Every field returned by ✅ endpoints → must be preserved in cache
4. Every owner-action item (I1-I3) → resolved
5. Every Tier H action → executed

**Estimated total wall time:** ~80-120h fetch (mostly parallelizable, owner can pause subscriptions afterward).

---

*Authored 2026-05-08. Probe report: `API_ENDPOINT_PROBE_REPORT.json`. Last probe: 2026-05-08.*
