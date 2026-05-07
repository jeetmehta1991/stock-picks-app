# PREFETCH_COVERAGE_AUDIT.md — Pass 53 Day-9 v8h comprehensive prefetch audit

Owner directive 2026-05-07: *"This is exactly what i mean that we should pre fetch ALL available endpoints and corresponding dimensions. We can choose to not use it but if we have it all prefetched we can be flexible and quick in addressing.... Data quality and comprehensiveness is the foundation."*

This doc audits every prefetched data source against:
1. **Endpoint coverage** — does the source have other endpoints we're not fetching?
2. **Dimension coverage** — for each endpoint, are we fetching all available dimensions (per-ticker / global / historical / per-form / etc.)?
3. **Universe coverage** — does the prefetch span the full 1937-ticker Master Universe (or relevant subset)?

Last full inventory: 2026-05-07 evening. Master Universe = 1937 unique tickers.

---

## Pass 53 Day-9 v8h evening FIELD-LEVEL DEEP DIVE per owner directive 2026-05-07 (round 2)

**Owner correction 2026-05-07 evening:** *"What i mean by dimensions in an API endpoint is that we earlier had downloaded an API but didnt prefetch time column. So the coverage for that API endpoint was high, but essentially erroneous because the time dimension wasnt prefetched. So thats the gap we also need to analyze for all API endpoints and within each API endpoint are all dimensions being prefetched?"*

**Acknowledged framing miss:** the prior deep-dive (round 1) audited ENDPOINT + UNIVERSE coverage but NOT FIELD-LEVEL completeness within each endpoint. This round corrects that. Method: read parquet schema of one cached file per endpoint + compare to API spec.

### Owner-confirmed scope this turn:
- **Polygon Stocks Starter** (paid — current)
- **Polygon Indices Basic** (FREE — owner can add at no cost) — **opportunity**
- **Polygon Options Basic** (FREE) — **opportunity**
- **Polygon Futures Basic** (FREE) — **opportunity**
- **Polygon Currencies Basic** (FREE) — **opportunity**
- **Quiver Trader plan** (current) — confirmed
- No new paid subscriptions

### Field-level audit headline findings (sorted by severity)

| # | Source | Issue | Severity | INV |
|---|---|---|---|---|
| 1 | Quiver `gov_contracts` | NO date column — only `Qtr+Year`. Lost DateSigned/AwardingAgency/DepartmentDescription/ContractDescription per Quiver API. Amount stored as STRING. **EXACT pattern owner cited.** | CRITICAL | INV-024 |
| 2 | Quiver `topshareholders` + `etfholdings` | NO date column — current snapshot only (INV-008 already logged) | HIGH | INV-008 (existing) |
| 3 | SEC EDGAR all 11 forms | Filing metadata only (`primary_doc` URL not parsed). Lost Form 4 transaction details (shares/price/officer/director-flag), 8-K material event types, 13D/G holder positions, 10-K/10-Q line items. Without parsing: just "X ticker filed Form Y on Z date" — non-actionable for signals. | CRITICAL | INV-025 |
| 4 | Polygon financials | `financials_json` stored as STRING — income statement / balance sheet / cash flow line items not extracted. Can't query revenue / EPS / FCF directly. | HIGH | INV-026 |
| 5 | Polygon news | **No per-ticker `insights` array** captured. We have article-level `sentiment` + `sentiment_reasoning` but Polygon API returns INSIGHTS = list of {ticker, sentiment, sentiment_reasoning} per article. For multi-ticker articles, we lose ticker-specific sentiment. | HIGH | INV-027 |
| 6 | OHLCV cache | Missing `vwap` + `transactions` count from Polygon `/v2/aggs/.../day` response. VWAP useful for execution-cost modeling; transactions count for liquidity scoring. | MEDIUM | INV-028 |
| 7 | Polygon events | Only `ticker_change` events captured. Polygon spec lists `splits`, `dividends`, `delisting`, `name_change`, `merger` as event types. Many events lost. | MEDIUM | INV-029 |
| 8 | Polygon reference | Missing: address, branding (logo/icon URLs), total_employees, FIGI codes (composite_figi/share_class_figi useful for cross-source matching), description. | LOW-MEDIUM | INV-030 |
| 9 | Quiver `congressional` | Missing: District, State, Industry, Sector, Filing URL per Quiver API spec. | MEDIUM | INV-031 |
| 10 | AV news cache | Aggregated DAILY only — lost per-article (title, summary, source, URL, ticker_sentiment). Cannot reconstruct article-level info. | MEDIUM | INV-032 |
| 11 | Finnhub news AAPL | 0 rows in cached parquet — data integrity gap. INV-016 escalates from "S&P-only-stale" to "actively-empty-for-some-tickers". | HIGH | INV-016 (existing) |
| 12 | Quiver `institutional` AAPL | 0 rows in cached parquet — INV-007 still active. Per-ticker fetch broken; bulk works. | HIGH | INV-007 (existing) |
| 13 | Wikipedia, pytrends, Quiver sec13fchanges, Quiver offexchange, Quiver corporatedonors, Quiver patentmomentum, CNN F&G `date` field, Apewisdom `snapshot_date` | `date` columns stored as STRING (not pandas datetime64). Functional — engine can `pd.to_datetime` at read time — but indicates the prefetch lost type info during write. PIT cutoff queries become string-comparison-correct only with ISO-8601 format. | LOW (typing) | INV-033 |

### Per-source field-level matrix

#### Polygon news (`data_prefetch/polygon/news/AAPL.parquet`, 21621 rows, 12 cols)
- HAVE: ticker, id, published_utc, title, description, article_url, amp_url, publisher_name, publisher_homepage_url, sentiment (article-level), sentiment_reasoning (article-level), all_tickers
- MISSING per Polygon `/v2/reference/news` spec:
  - **`insights`** (list of per-ticker {ticker, sentiment, sentiment_reasoning}) — CRITICAL miss; for multi-ticker articles we lose ticker-specific sentiment
  - `keywords` (article keywords/tags)
  - `image_url`
  - `author`
- **Action:** re-prefetch news with full schema. ~4-6h at full universe.

#### Polygon financials (AAPL.parquet, 86 rows, 11 cols)
- HAVE: ticker, filing_date, period_of_report_date, fiscal_period, fiscal_year, start_date, end_date, cik, company_name, source_filing_url, **financials_json (STRING — unparsed)**
- MISSING per Polygon `/vX/reference/financials` spec (within `financials_json`):
  - Income statement: revenue, cost_of_revenue, gross_profit, operating_expenses, operating_income, net_income, eps_basic, eps_diluted, weighted_average_shares
  - Balance sheet: total_assets, total_liabilities, stockholders_equity, current_assets, current_liabilities, long_term_debt
  - Cash flow: cash_from_operations, cash_from_investing, cash_from_financing, capex, free_cash_flow
  - `tickers` array (multi-ticker filings — some financials cover multiple share classes)
  - `acceptance_datetime_utc` (more granular than filing_date)
- **Action:** parse financials_json into structured columns + reread cache. ~30 min processing on existing cache (no new API calls).

#### Polygon events (AAPL.parquet, 1 row, 4 cols)
- HAVE: ticker, event_type, event_date, **details_json (STRING — unparsed)**
- MISSING: only ticker_change events present; spec lists splits, dividends, delisting, name_change, merger
- **Action:** re-prefetch with `?types=ticker_change,splits,dividends,delisting,name_change` query. ~1h.

#### Polygon reference (AAPL.parquet, 1 row, 16 cols)
- HAVE: ticker, name, market_cap, share_class_shares_outstanding, weighted_shares_outstanding, sic_code, sic_description, primary_exchange, type, active, currency_name, cik, list_date, delisted_utc, homepage_url, fetched_at
- MISSING per spec:
  - `address` (street/city/state/zip — useful for geographic strategies)
  - `branding` (logo_url, icon_url)
  - `total_employees`
  - `phone_number`
  - `description` (company description text)
  - `composite_figi`, `share_class_figi` (FIGI identifiers)
  - `round_lot`
- **Action:** add fields to `prefetch_polygon_reference.py` + re-prefetch. ~1h.

#### Quiver congressional (AAPL.parquet, 1087 rows, 16 cols)
- HAVE: Representative, BioGuideID, ReportDate, TransactionDate, Ticker, Transaction, Range, House, Amount, Party, last_modified, TickerType, Description, ExcessReturn, PriceChange, SPYChange
- MISSING per Quiver API spec:
  - `District` (congressional district)
  - `State`
  - `Industry`, `Sector`
  - `Filing` (URL to filing)
- **Action:** when re-prefetching, extend to capture these fields. (Currently in flight as `b3xny7m35` BG — won't be in this run; future run.)

#### Quiver gov_contracts (AAPL.parquet, 66 rows, 4 cols) — **CRITICAL FIELD GAP**
- HAVE: Ticker, Amount (STRING type), Qtr (int), Year (int)
- MISSING per Quiver `/historical/govcontracts/{ticker}` API spec — this is the EXACT pattern owner cited:
  - **`Date`** (when contract was awarded — DAILY granularity, not quarterly aggregate)
  - **`AwardingAgency`** (who awarded — DOD, NASA, GSA, etc.)
  - **`DepartmentDescription`**
  - **`ContractDescription`** (contract subject text)
  - **`Amount` should be numeric** (currently STRING)
- **Severity:** CRITICAL — the data we have is severely impoverished. Qtr+Year aggregate cannot do PIT cutoff at daily level. Strategy "buy on gov contract win" cannot be implemented at all without DateSigned. Currently mid-flight in BG `b3xny7m35` re-prefetch — will need a SECOND re-prefetch with extended field set after this audit.
- **Action:** edit `prefetch_quiver.py` save logic to capture all returned fields (currently must be filtering); re-launch.

#### Quiver insider (AAPL.parquet, 249 rows, 16 cols)
- HAVE: Ticker, Date, Name, AcquiredDisposedCode, TransactionCode, Shares, PricePerShare, SharesOwnedFollowing, fileDate, officerTitle, isDirector, isOfficer, isTenPercentOwner, isOther, directOrIndirectOwnership, uploaded
- COMPLETE — both Date (transaction) and fileDate (when filed) present. DEC-512 BUG-INSIDER-PIT correctly uses fileDate. **Resolved.**

#### Quiver institutional (AAPL.parquet) — INV-007 STILL ACTIVE
- 0 rows. Per-ticker fetch broken. Bulk endpoint `quiver/sec13fchanges/global.parquet` (500K rows) works. **Action:** wire engine consumers to use bulk parquet, deprecate per-ticker.

#### Quiver topshareholders (AAPL.parquet, 1 row, 2 cols) — INV-008
- ownership / ownership_options as JSON-string objects. NO date. NO structured top-N rows.
- **Action:** parse JSON into structured rows + add `as_of_date` column. Schedule periodic snapshot capture for PIT history (Stage 3+).

#### Quiver etfholdings (AAPL.parquet, 703 rows, 5 cols) — INV-008
- ETF Symbol, Holding Name, Holding Symbol, % of ETF, Value ($). **NO date** — current snapshot only.
- **Action:** add daily snapshot capture going forward (cron) for ETF flow signals.

#### SEC EDGAR all 11 forms (AAPL Form 4: 586 rows, 6 cols) — **CRITICAL FIELD GAP**
- HAVE: ticker, cik, form, filing_date, accession_number, primary_doc
- MISSING — all of the structured filing CONTENT:
  - Form 4: TransactionDate, ReportingOwner.Name, OfficerTitle, IsDirector, IsOfficer, IsTenPercentOwner, Transaction.SecurityType, Transaction.Shares, Transaction.PricePerShare, Transaction.AcquiredDisposed
  - 8-K: ItemNumber (1.01 acquisition / 2.02 results / 5.02 officer change / 8.01 other), CompanyText, Items array
  - SC 13D: ReportingOwner, PercentOfClass, Shares, AcquisitionDate, PurposeOfTransaction
  - 10-K/10-Q: link to financial-tag (XBRL) data
  - DEF 14A: ProxyType, ItemDetails
- **Severity:** CRITICAL. We have "filed-on-date" only — useful for "filing event happened" signals (e.g., 8-K within last 5 days = catalyst), but nothing about WHAT was filed.
- **Action:** Two paths:
  1. Parse `primary_doc` XML/HTML for each filing → very expensive (~1700 tickers × 11 forms × N filings each)
  2. Use SEC EDGAR full-text-search + structured-data XBRL feeds → faster, smaller scope. **Recommended.**
- **Effort:** ~20-30h to add structured content fetch.

#### CNN F&G daily (253 rows, 4 cols)
- HAVE: timestamp (int64 epoch), score, rating, date (string)
- COMPLETE for the composite endpoint. 7 sub-components in separate parquets per DEC-498. Confirmed.
- Note: `timestamp` and `date` redundant; `rating` is regime label ("Greed"/"Extreme Greed"). Schema is fine.

#### AAII (325 rows, 5 cols)
- HAVE: date, bullish, neutral, bearish, bull_bear_spread
- MISSING per AAII publication:
  - `8_week_avg` (8-week MA of bull-bear spread — published WITH the survey)
  - `historical_avg` (long-term avg)
  - `s&p_500_close` (S&P close on survey date — for context)
- AAII also publishes (separate endpoints, not yet cached):
  - **Asset Allocation Survey** (monthly: stocks/bonds/cash %)
  - **Investor Confidence Index** (quarterly)
- **Action:** add 3 missing fields to weekly + add 2 separate endpoints. ~1h.

#### CFTC COT (e-mini SP500: 1293 rows, 87 cols)
- 87 columns — comprehensive financial-disagg breakdown. **No fields missing.**
- Note: `report_date` is `object` (string) — should be datetime. INV-033 typing.

#### FRED VIXCLS (1623 rows, 2 cols: date, value)
- COMPLETE — but limited to 2020-01-01 onward per `prefetch_macro.py` `DATE_START`. VIXCLS goes back to 1990. **Action:** consider extending DATE_START for backtesting beyond 2020.

#### ALFRED — same series schema, with realtime_start/realtime_end vintage params
- **PROBE NEEDED:** does our ALFRED cache include realtime_start + realtime_end columns? If not, the vintage data is the SAME as FRED current (no PIT-revision benefit). **This is the test the audit hasn't yet run.**

#### Wikipedia (AAPL.parquet, 1855 rows, 3 cols)
- HAVE: date (STRING), views, article
- COMPLETE — but date is string. INV-033.

#### pytrends (AAPL.parquet, 262 rows, 4 cols)
- HAVE: ticker, date (STRING), search_volume_index, query_label
- MISSING dimensions:
  - `interest_by_region` (state-level geographic dimension)
  - `related_queries` (co-search analysis)
  - `related_topics`
- **Action:** add 3 dimensional endpoints. ~3-4h rate-limited.

#### Quiver offexchange (AAPL.parquet, 3937 rows, 5 cols)
- HAVE: Ticker, Date (STRING), OTC_Short, OTC_Total, DPI
- COMPLETE for FINRA off-exchange. INV-033 typing.

#### Apewisdom (global.parquet, 2310 rows, 8 cols)
- HAVE: rank, ticker, name, mentions, upvotes, rank_24h_ago, mentions_24h_ago, snapshot_date (STRING)
- MISSING per Apewisdom API:
  - `subreddits` (which subreddits — currently the global feed only)
  - `sentiment` (positive/negative count)
- **Action:** add 4 subreddit-specific endpoints + sentiment dimension.

#### Quiver news bulk (1500 rows, 6 cols)
- HAVE: url, time, headline, category, summary, image
- **NO ticker column** — articles categorized by category only. Cannot do per-ticker news lookup from this endpoint.
- **Action:** verify this is the only Quiver news endpoint; if per-ticker exists, prefetch that.

#### Quiver sec13fchanges (500K rows, 10 cols)
- HAVE: Date (STRING), ReportPeriod, Ticker, Fund, Change, Change_Share, Change_Pct, Held, Held_Normalized, Close
- COMPLETE bulk. INV-033 typing.

#### Quiver corporatedonors (25K rows, 11 cols)
- HAVE: BioGuideID, CandidateName, CompanyCMTENM, TransactionDate (STRING), TransactionAmount, Ticker, CommitteeName, Cycle, TransactionType, CompanyCMTEID, Uploaded
- COMPLETE. INV-033 typing.

#### Quiver patentmomentum (5.83M rows, 3 cols)
- HAVE: ticker, date (STRING), momentum
- **MINIMAL fields** — Quiver Patents API likely has more (granted_patents, pending_patents, citations, R&D_spend per Quiver docs).
- **Action:** verify Quiver Patents endpoint full field set + extend.

#### Finnhub news (AAPL.parquet) — INV-016 ESCALATES
- 0 rows for AAPL specifically. Other tickers may also be empty. Universe coverage 509 files but content per file unknown.
- **Action:** spot-check 5-10 other tickers for empty parquets; re-prefetch any that are 0-row.

#### AV news (CCI.parquet, 303 rows, 8 cols)
- HAVE: date, sentiment_mean, sentiment_weighted, article_count, bullish_count, bearish_count, max_relevance, sentiment_direction
- **AGGREGATED DAILY** — per-article info lost. AV `NEWS_SENTIMENT` API returns: title, url, time_published, authors, summary, banner_image, source, category_within_source, source_domain, topics, overall_sentiment_score, overall_sentiment_label, ticker_sentiment[].
- **Action:** re-prefetch with raw-article schema preserved + roll up to daily as derived view, not as primary cache.

#### OHLCV cache (AAPL.parquet, 1255 rows, 6 cols) — **MISSING KEY FIELDS**
- HAVE: date, open, high, low, close, volume
- MISSING from Polygon `/v2/aggs/.../day` response:
  - **`vwap`** (volume-weighted average price — execution-cost benchmark)
  - **`transactions`** (number of trades per bar — liquidity scoring)
- **Action:** edit `prefetch_polygon_ohlcv_daily.py` to capture these + re-prefetch. ~6-8h. INV-028.

### Polygon FREE plan inventory (Indices / Options / Futures / Currencies Basic)

Owner confirmed: can add 4 free Polygon plans alongside paid Stocks Starter. Inventory:

#### **Polygon Indices Basic (FREE)**

Direct index aggregates (no ETF proxy needed):

| Endpoint | Description | Phase 1A use |
|---|---|---|
| `/v2/aggs/ticker/I:SPX/range/.../day` | S&P 500 INDEX (vs SPY ETF) | Cleaner regime classifier |
| `/v2/aggs/ticker/I:NDX/range/.../day` | Nasdaq-100 INDEX (vs QQQ) | Same |
| `/v2/aggs/ticker/I:DJI/range/.../day` | Dow Jones INDEX (vs DIA) | Same |
| `/v2/aggs/ticker/I:RUT/range/.../day` | Russell 2000 INDEX (vs IWM) | Cleaner small-cap regime |
| `/v2/aggs/ticker/I:VIX/range/.../day` | VIX INDEX direct | **RESOLVES BUG-VIX-PROXY permanently** |
| `/v2/aggs/ticker/I:VIX9D/range/.../day` | 9-day VIX | Term-structure short end |
| `/v2/aggs/ticker/I:VIX3M/range/.../day` | 3-month VIX | DEC-513 #7 native (vs FRED VXVCLS) |
| `/v2/aggs/ticker/I:VIX6M/range/.../day` | 6-month VIX | Extended term-structure |
| `/v2/aggs/ticker/I:VVIX/range/.../day` | VVIX (vol of VIX) | **RESOLVES INV-010 (VVIXCLS 400 from FRED)** |
| `/v2/aggs/ticker/I:OEX/range/.../day` | S&P 100 | Mega-cap regime |
| `/v2/aggs/ticker/I:MID/range/.../day` | S&P 400 mid-cap | Mid-cap regime |
| `/v2/aggs/ticker/I:SML/range/.../day` | S&P 600 small-cap | Small-cap regime |
| `/v2/aggs/ticker/I:NYA/range/.../day` | NYSE Composite | Broad-market regime |
| `/v2/aggs/ticker/I:COMP/range/.../day` | Nasdaq Composite | Broad-tech regime |
| `/v3/reference/tickers?market=indices` | Indices universe list | Reference |
| `/v3/snapshot/indices` | Current snapshot | Real-time (Stage 3+) |

**Use cases:** native VIX (resolves BUG-VIX-PROXY structurally), VIX term-structure direct (resolves INV-010 VVIX gap from FRED), regime classifier on direct indices vs ETF proxies (no tracking error).

**Estimated prefetch:** ~14 series × 6 years × 1 daily fetch = trivial (~10 min wall clock). **HIGH VALUE per dollar (zero $ added).**

#### **Polygon Options Basic (FREE)**

| Endpoint | Description | Use case |
|---|---|---|
| `/v3/reference/options/contracts?underlying_ticker={t}` | Option chain universe per ticker | Per-ticker chain fetch |
| `/v3/reference/options/contracts/{contract}` | Per-contract metadata (strike, expiry, type) | Reference |
| `/v2/aggs/ticker/O:AAPL250117C00200000/range/.../day` | OHLCV per option contract | Vol surface, OI history |
| `/v3/snapshot/options/{ticker}` | Current chain snapshot per ticker | Stage 3+ |
| `/v3/snapshot/options/{ticker}/{contract}` | Per-contract snapshot | Stage 3+ |

**Derived signals possible:**
- **Put/call ratio per ticker** (volume + OI) — bullish/bearish positioning
- **Implied vol surface** — forward-looking vol expectations
- **IV rank/percentile** — how expensive options are vs history
- **Skew** (OTM put IV vs OTM call IV) — tail-risk pricing
- **Term structure** of IV — short vs long-dated vol
- **Unusual options activity** (volume vs OI vs avg) — institutional flow
- **Gamma exposure (GEX)** approximation — dealer-positioning signal

**Caveat:** Options chains explode in size. AAPL has ~500-1000 contracts at any time × 6 years history = potentially 10-50 GB. Need careful prefetch strategy: just OI+IV+volume daily aggregates per contract, NOT every tick.

**Estimated:** ~10-30h initial prefetch + ongoing daily updates. **HIGH VALUE for Phase 1B+ (options-flow strategies).**

#### **Polygon Futures Basic (FREE)**

| Symbol | Description | Use case |
|---|---|---|
| ES (e-mini SP500) | S&P 500 futures | Term structure vs SPX index |
| NQ (e-mini Nasdaq) | NDX futures | Same |
| RTY (e-mini Russell) | RUT futures | Same |
| YM (e-mini Dow) | DJI futures | Same |
| VX (VIX futures) | VIX futures | **VIX futures curve — major contango/backwardation signal**; cross-validates CFTC COT |
| CL (WTI crude) | Oil futures | Term structure vs USO ETF; macro signal |
| GC (gold) | Gold futures | Term structure vs GLD ETF |
| SI (silver) | Silver futures | Same vs SLV |
| HG (copper) | Copper futures | Industrial-cycle signal |
| ZB / ZN / ZF / ZT (treasuries) | Treasury futures | Yield-curve positioning vs FRED DGS |
| 6E / 6J / 6B / 6A / 6C / 6S | Currency futures (EUR/JPY/GBP/AUD/CAD/CHF) | Cross-validate Polygon Currencies |
| ZC / ZS / ZW (corn/soy/wheat) | Agriculturals | Inflation signal |

**Estimated:** ~25 contracts × 6 years × daily = ~5 min × 25 = ~2h wall clock. **MEDIUM-HIGH VALUE** (term structure signals not currently captured).

#### **Polygon Currencies Basic (FREE)**

| Pair | Use case |
|---|---|
| C:EURUSD | DXY major component (57.6% weight) |
| C:USDJPY | DXY (13.6%); risk-off proxy |
| C:GBPUSD | DXY (11.9%) |
| C:USDCAD | DXY (9.1%); commodity-currency cross |
| C:USDCHF | DXY (3.6%); risk-off proxy |
| C:USDAUD | Risk-on currency cross |
| C:USDNZD | Same |
| C:USDCNY | Asia-EM proxy |
| C:USDMXN | LATAM proxy |
| C:USDINR | Asia-EM proxy |

**Estimated:** ~10 pairs × 6 years × daily = trivial (~30 min). **MEDIUM VALUE** — gives us native DXY computation (vs FRED DTWEXBGS aggregate or UUP ETF proxy) + cross-currency risk-on/off signals.

### Recommended action plan (per #76 column-c)

#### Tier F — FIELD-LEVEL re-prefetches (existing endpoints, schema-fix)

| # | Action | Est. effort | Priority |
|---|---|---|---|
| F1 | Quiver gov_contracts: re-fetch with full field set (Date, AwardingAgency, etc.) | 1-2h | **P0** (CRITICAL gap) |
| F2 | Polygon news: re-prefetch with `insights` array | 4-6h | P1 |
| F3 | Polygon financials: parse financials_json into structured columns (no API calls — local processing) | 30 min | P1 |
| F4 | Polygon events: re-prefetch with `?types=ticker_change,splits,dividends,delisting` | 1h | P2 |
| F5 | Polygon reference: extend to capture address/branding/employees/FIGI/description + re-prefetch | 1h | P2 |
| F6 | OHLCV: extend prefetch_polygon_ohlcv_daily.py to capture `vwap` + `transactions` + re-prefetch | 6-8h | P1 |
| F7 | SEC EDGAR: parse primary_doc structured data (XBRL for 10-K/Q; XML for Form 4 etc.) | 20-30h | P1 |
| F8 | Quiver congressional: re-fetch with District/State/Industry/Sector | (next BG) | P2 |
| F9 | AV news: re-fetch raw articles (not aggregated) | 10-15h | P1 |
| F10 | Finnhub news: spot-check 5-10 tickers for empty parquets; re-fetch any 0-row | 1-2h + re-prefetch | P1 |
| F11 | All STRING-date columns → datetime: write migration script | 1h | P2 (cosmetic) |

#### Tier G — NEW Polygon FREE plan prefetches

| # | Plan | Est. effort | Priority |
|---|---|---|---|
| G1 | Indices Basic: 14 series × 6 years (SPX/NDX/DJI/RUT/VIX/VIX9D/VIX3M/VIX6M/VVIX/OEX/MID/SML/NYA/COMP) | ~10 min | **P0** (resolves BUG-VIX-PROXY + INV-010) |
| G2 | Futures Basic: ~25 contracts (ES/NQ/RTY/VX/CL/GC/SI/HG/ZB-N-F-T/6E-J-B-A-C-S/ZC-S-W) | ~2h | P1 |
| G3 | Currencies Basic: ~10 pairs (EURUSD/USDJPY/GBPUSD/etc.) | ~30 min | P1 |
| G4 | Options Basic: chains + IV + OI for top 100 most-liquid tickers as starter (full universe later) | ~10-30h | P1-P2 |

**Combined estimated wall time: ~80-100h additional fetch (parallelizable, mostly unattended).**

### Subscription confirmations resolved
- ✓ Polygon Stocks Starter (paid, current)
- ✓ Polygon Indices/Options/Futures/Currencies Basic (FREE — owner confirmed adding)
- ✓ Quiver Trader plan (current)
- ✗ NO new paid subscriptions (per owner directive)

---

## Pass 53 Day-9 v8h evening DEEP DIVE per owner directive 2026-05-07

**Owner directive:** *"I want all data downloaded from API endpoints with all dimensions pre-fetched. No exceptions. Even if its relevant later on beyond phase 1A, i need to download it now. I am going to pause API subscriptions so i need it all downloaded even if we do not have plan to use it. Download broad everything and use as needed is the goal."*

**Goal:** comprehensive audit beyond surface-level — every API, every endpoint we have access to (paid or free), every dimension. Surface every gap, abnormality, and "doesn't look normal" issue.

**Method per #76:** column (a) observation = filesystem inventory + script read + checkpoint cross-check; column (b) verification at audit time = (1) `ls data_prefetch/**` filesystem walk, (2) `ls backtest/data/cache/**` legacy walk, (3) `ls scripts/prefetch_*.py` + `ls .github/workflows/prefetch_*.yml` script inventory, (4) `grep os.environ.get .._API_KEY` keyholder probe, (5) FRED↔ALFRED diff, (6) `_checkpoint.json` ↔ filesystem diff, (7) read of `prefetch_macro.py` + `prefetch_polygon_reference.py` + `prefetch_apewisdom_daily.py` for canonical-source verification; column (c) recommendation = bottom of section.

### Deep-dive headline findings (sorted by severity)

| # | Finding | Severity | Action |
|---|---|---|---|
| 1 | **8 NEW INV flags** logged this audit (INV-015..INV-022) — silent gaps + drift | varies | per-INV |
| 2 | **Alpha Vantage news cached only 25 files** (letter range C..X partial) — prefetch died mid-run | HIGH | INV-015 |
| 3 | **Finnhub news 509 files = S&P-only** (NOT expanded to 1937 Master Universe) | HIGH | INV-016 |
| 4 | **Polygon dividends/splits canonical paths = 1 file each** — corp_actions prefetch never completed at universe scope | HIGH (P0/Phase 1B) | INV-017 |
| 5 | **prefetch_macro.py SERIES dict (21) ≠ cache state (57)** — script doc out-of-sync with actual cache; canonical-source rule violated | MEDIUM (process) | INV-020 |
| 6 | **NO prefetch scripts exist for AAII / CNN F&G / FRED-extras / ALFRED / pytrends / Wikipedia / CFTC** — orphan cache dirs without canonical refresh path | MEDIUM (operational debt) | INV-021 |
| 7 | **ALFRED 7-series gap behind FRED** (recent Tier C additions didn't propagate to vintage cache) | MEDIUM | INV-019 |
| 8 | **Polygon snapshot / market_status / reference_meta stub dirs (2-3 files each)** — looks like smoke-test artifacts, not real prefetch | LOW (low-priority endpoints) | INV-018 |
| 9 | **Legacy `backtest/data/cache/quiver/` directory empty** but not deleted | LOW (housekeeping) | INV-022 |
| 10 | DEC-491 trade_log.parquet silent degrade (caught earlier this session) | MEDIUM | INV-014 (already logged) |

### Per-API endpoint inventory + gap matrix

(format = column-(a) observation / column-(b) verification step / column-(c) recommendation)

#### **A. Polygon Stocks Starter ($29/mo)** — verified via API_AUDIT.md §2

| Endpoint | Cached? | Coverage | Verified | Recommendation | Priority | Blocker |
|---|---|---|---|---|---|---|
| `/v2/aggs/ticker/{t}/range/.../day` (OHLCV) | YES | 2123 (109%) | filesystem + smoke earlier | Already complete. | — | resolved |
| `/v2/reference/news` | YES | 1926 (99.4%) | filesystem | Top-up missing 11 tickers (~5 min) | P2 | non-blocking |
| `/vX/reference/financials` | YES | 1746 (90.1%) | filesystem | Top-up missing 191 (~30 min) | P1 | Phase 1B |
| `/v3/reference/tickers/{t}` | IN FLIGHT | BG `b9xczleu2` ~1133/1937 | live BG read | Wait for BG to complete (~30 min more); confirms 100% | P0 | **Phase 1A** |
| `/v3/reference/tickers/{t}/events` | YES | 1687 (87.1%) | filesystem | Top-up missing 250 (~30 min). Spec says other event types (delisting, IPO, etc.) possible — only ticker_change observed; probe other types. | P1 + new probe | Phase 1B |
| `/v3/reference/dividends` | **PARTIAL** | 1 file canonical / 2 legacy | filesystem + INV-017 | NEW PREFETCH at 1937 universe scope. Estimated 2-3h. | P1 | Phase 1B |
| `/v3/reference/splits` | **PARTIAL** | 1 file canonical / 2 legacy | filesystem + INV-017 | NEW PREFETCH at 1937 universe. Estimated 2-3h. | P1 | Phase 1B |
| `/v1/indicators/sma` `/ema` `/rsi` `/macd` | NO | 0 | not-cached + API_AUDIT.md confirms NO | Polygon-precomputed indicators — we compute locally, but **owner directive says download anyway**. Estimated 4 endpoints × 1937 = 7748 fetches. ~3-5h. | P2 (per owner directive) | non-blocking |
| `/v3/quotes/{t}` (NBBO historical) | NO | 0 | API_AUDIT.md NO | Useful for slippage calibration. Stocks Starter includes 5+ years intraday. Storage cost ~5-50 GB depending on resolution. **Per owner directive: download.** Probe for tier limits first. | P2 | non-blocking — new infrastructure |
| `/v3/trades/{t}` (tick) | NO | 0 | API_AUDIT.md OUT OF SCOPE | Tick data — high storage. **Per owner: download.** Probe storage feasibility first. | P3 | informational |
| `/v3/snapshot/locale/us/markets/stocks/tickers` | STUB | 2 files | filesystem | Real-time only — not prefetchable at historical cadence. Daily-snapshot capture possible going forward. **Per owner: set up daily capture.** | P2 | Stage 3+ |
| `/v1/marketstatus/now` | STUB | 2 files | filesystem | Real-time only. Daily capture going forward. | P3 | informational |
| `/v1/marketstatus/upcoming` (holidays) | STUB | files unclear | filesystem | Static reference — small. **Cache once.** ~5 min. | P2 | non-blocking |
| `/v3/reference/conditions` | NO | 0 | API_AUDIT.md NO | Trade/quote condition codes — small static reference. ~5 min. | P3 | informational |
| `/v3/reference/exchanges` | NO | 0 | not-cached | Exchange list — small static. ~2 min. | P3 | informational |
| `/v2/snapshot/locale/us/markets/stocks/gainers` | NO | 0 | not-cached | Real-time gainers — daily snapshot going forward. | P3 | Stage 3+ |
| `/v2/snapshot/locale/us/markets/stocks/losers` | NO | 0 | not-cached | Same. | P3 | Stage 3+ |
| `/v1/open-close/{t}/{date}` | NO | 0 | not-cached | Per-ticker daily summary. Overlap with `/v2/aggs/.../day` — redundant. | P3 | skip |
| `/v2/last/trade/{t}` | NO | 0 | API_AUDIT.md OUT OF SCOPE | Real-time only. | — | skip |
| Treasury yields endpoint | NO | 0 | FRED authoritative | Skip — FRED has more series + ALFRED vintage. | — | skip |
| Options endpoints | NO | 0 | NOT in Stocks Starter tier | **Verify subscription tier** — Options Starter is separate ($79/mo). If we DON'T have it, can't download. **OWNER QUESTION: do we have Options Starter access?** | TBD | confirm tier first |

#### **B. Quiver Trader (~$150/yr)** — verified by current BG `bsu432hbt` + API_AUDIT.md

| Endpoint | Cached? | Coverage | Verified | Recommendation | Priority | Blocker |
|---|---|---|---|---|---|---|
| `historical/congresstrading/{t}` | IN FLIGHT | 1864/1937 (96%) | live BG | wait + commit on completion | P0 | **Phase 1A** |
| `live/insiders?ticker={t}` | IN FLIGHT | 509 baseline | BG queued | wait | P0 | **Phase 1A** |
| `live/sec13f?ticker={t}` | IN FLIGHT | 509 baseline | BG queued | wait | P0 | **Phase 1A** |
| `historical/govcontracts/{t}` | IN FLIGHT | 509 baseline | BG queued | wait | P0 | **Phase 1A** |
| `historical/lobbying/{t}` | IN FLIGHT | 509 baseline | BG queued | wait | P1 | Phase 1B |
| `historical/wikipedia/{t}` (Quiver mirror) | DELETED (INV-006/013) | 0 effective | filesystem | leave as-is — canonical at `data_prefetch/wikipedia/` | — | resolved |
| `historical/wallstreetbets/{t}` | IN FLIGHT | 509 baseline | BG queued | wait | P1 | Phase 1B |
| `live/offexchange?ticker={t}` (dark pool) | YES | 1851 (95.6%) | filesystem | Top-up missing 86 | P2 | non-blocking |
| `live/sec13fchanges?ticker={t}` | bulk | 1 global parquet | filesystem | Already canonical bulk | — | resolved |
| `live/topshareholders?ticker={t}` | YES | 1937 (100%) | filesystem | INV-008 — no PIT dim. Schedule 1×/quarter snapshot capture. | P3 | Stage 3+ |
| `live/etfholdings?ticker={t}` | YES | 1563 (80.7%) | filesystem | Top-up missing 374 | P2 | non-blocking |
| `live/corporatedonors?ticker={t}` | bulk | 1 global parquet | filesystem | Already canonical bulk | — | resolved |
| `live/patentmomentum?ticker={t}` | bulk | 1 global parquet | filesystem | INV-N — patent momentum bulk only goes to 2022; **probe Quiver for 2024-2026 extension** | P2 | new probe |
| `live/quivernews?ticker={t}` | bulk | 1 global parquet | filesystem | Bulk only; OK | — | resolved |
| **MISSING per Quiver docs** | | | | | | |
| `live/twitter?ticker={t}` | NO | 0 | INV-012 verified 0 records for AAPL | Probe 5 different tickers — if any data, prefetch all 1937. | P2 (per owner) | new probe |
| `live/iposcalendar` | NO | 0 | INV-012 verified 404 | Probe again with correct path; if 404, defer | P3 | confirm |
| `live/spacs` | NO | 0 | INV-012 404 | Same | P3 | confirm |
| `live/optionsflow?ticker={t}` | NO | 0 | INV-012 404 | Confirm not in Trader plan | P3 | confirm |
| `live/earningsbeats?ticker={t}` | NO | 0 | INV-012 404 | Confirm not in Trader plan | P3 | confirm |
| `live/dividends?ticker={t}` | NO | 0 | not-probed | Probe — if exists, use over Polygon (Quiver has 0% gap) | P2 | new probe |
| `live/splits?ticker={t}` | NO | 0 | not-probed | Same | P2 | new probe |
| `live/senateindustry?ticker={t}` | NO | 0 | not-probed | Senate-only sub-feed — probe | P2 | new probe |
| `live/housemtg?ticker={t}` | NO | 0 | not-probed | House Member Trades sub-feed — probe | P2 | new probe |
| `live/snptrend` | NO | 0 | not-probed | S&P 500 sentiment trend — probe | P2 | new probe |
| `live/redditpoliticians` | NO | 0 | not-probed | Reddit politicians — probe | P3 | new probe |
| `live/swaps` | NO | 0 | not-probed | Swaps reporting — probe | P3 | new probe |

#### **C. SEC EDGAR (free)** — 11 forms cached

| Form Type | Cached? | Coverage | Recommendation | Priority |
|---|---|---|---|---|
| 4 (insider) | YES | 1717/1937 (88.6%) | Top-up missing 220 (~1h) | P1 |
| 8-K | YES | 1715/1937 (88.5%) | Top-up missing 222 (~1h) | P1 |
| SC 13D | YES | 1715/1937 (88.5%) | Top-up missing 222 (~2h) | P1 |
| SC 13G | YES | 1722/1937 (88.9%) | Top-up missing 215 (~1h) | P2 |
| 10-K | YES | 1683/1937 (86.9%) | Top-up missing 254 (~2h) | P1 |
| 10-Q | YES | 1683/1937 (86.9%) | Same | P1 |
| DEF 14A (proxy) | YES | 1683/1937 (86.9%) | Top-up missing 254 (~1h) | P2 |
| S-1 | YES | 1683/1937 (86.9%) | Same | P2 |
| S-1/A | YES | 1683/1937 (86.9%) | Same | P2 |
| SC 13D/A | YES | 1683/1937 (86.9%) | Same | P2 |
| SC 13G/A | YES | 1683/1937 (86.9%) | Same | P2 |
| **MISSING forms** | | | | |
| Form 3 (initial insider stmt) | NO | 0 | NEW prefetch | P2 |
| Form 5 (annual insider stmt) | NO | 0 | NEW prefetch | P3 |
| 11-K (employee benefits) | NO | 0 | NEW prefetch | P3 |
| 6-K (foreign filer) | NO | 0 | NEW prefetch — covers ADRs / cross-listed | P2 |
| 20-F (foreign annual) | NO | 0 | NEW prefetch | P2 |
| 40-F (Canadian annual) | NO | 0 | NEW prefetch | P3 |
| 425 (M&A solicitation) | NO | 0 | NEW prefetch — useful for M&A strategy signals | P2 |
| 13F-HR (institutional bulk) | NO | 0 | Skip — Quiver `sec13fchanges` redundant | — |
| S-3 (shelf registration) | NO | 0 | NEW prefetch — pre-issuance signal | P3 |
| F-1 (foreign IPO) | NO | 0 | NEW prefetch — T2 enrichment | P3 |
| SD (specialized disclosures) | NO | 0 | NEW prefetch | P3 |
| 144 (Rule 144 insider) | NO | 0 | NEW prefetch — insider sale notice | P2 |
| POS AM (post-effective amend) | NO | 0 | NEW prefetch | P3 |
| 8-A12B / 8-A12G (registration) | NO | 0 | NEW prefetch | P3 |

#### **D. FRED (free)** — 57 series cached

INV-020 surfaced: `prefetch_macro.py` SERIES dict has 21 entries; cache has 57. The 36-series gap was populated by some other mechanism (not in `scripts/`, not in `.github/workflows/`). **Canonical source rule violated** — the prefetcher script is no longer the source of truth for what's actually fetched.

Cached series (alphabetical): A191RL1Q225SBEA, AAA, AAA10Y, AHETPI, BAA, BAA10Y, BAMLC0A0CM, BAMLC0A4CBBB, BAMLH0A0HYM2, CCSA, CIVPART, CPIAUCSL, CPILFESL, DCOILWTICO, DFEDTARU, DFF, DGS1, DGS10, DGS1MO, DGS2, DGS30, DGS3MO, DGS5, DGS6MO, DTWEXBGS, FEDFUNDS, FYFSGDA188S, GDP, GDPC1, HOUST, ICSA, INDPRO, M2SL, MORTGAGE30US, NFCI, PAYEMS, PCEPI, PCEPILFE, PERMIT, PPIACO, PPIFIS, RECPROUSM156N, RSAFS, STLFSI4, T10Y2Y, T10Y3M, T10YIE, T5YIE, TB3SMFFM, U6RATE, UMCSENT, UNRATE, USPRIV, USREC, VIXCLS, VXVCLS, WALCL.

**Recommended additions (per owner directive — broad-everything):**
- TIPS yields: DFII5, DFII10, DFII30 (real yields)
- Forward inflation: T5YIFR (5y5y forward breakeven)
- Productivity: OPHNFB, ULCNFB
- Labor sub-aggregates: USCONS, USTRADE, USMINE, USINFO, USFIRE, USEHS, USLAH, USSERV, USGOVT
- Regional Fed indices: KCFSI, NYFRBLAUP
- Money supply: M1SL, BOGMBASE
- Consumer credit: TOTALSL
- Housing: CSUSHPINSA, MSPUS
- Manufacturing: AMTMNO (new orders), AMTMTI (inventories)
- Yield curves (additional points): DGS20, DGS3
- Fed balance sheet detail: WALCL (have), TREAST, WGS10YR
- Foreign curves (sample): IRLTLT01DEM156N (Germany 10y), IRLTLT01GBM156N (UK), IRLTLT01JPM156N (Japan)
- Commodities prices: PCOPP (copper), PWHEAMTUSDM (wheat)
- Volatility: VXOCLS (old VIX), VXNCLS (NDX)
- Currencies: DEXUSEU, DEXJPUS, DEXUSUK, DEXCHUS

**Estimated:** 25-30 new series × 1 fetch each = ~3-5 min wall clock. Trivial.

#### **E. ALFRED (free)** — 50 series, 7 behind FRED

Missing series (per FRED↔ALFRED diff): DCOILWTICO, DTWEXBGS, INDPRO, RSAFS, TB3SMFFM, VIXCLS, VXVCLS — these are the Tier C additions made this session that didn't propagate to ALFRED prefetch. INV-019.

**Action:** mirror new FRED additions to ALFRED. Same prefetch logic, different endpoint (`/series/observations` → `/series/observations` w/ `realtime_start` param). ~5 min.

#### **F. AAII Sentiment (free, manual)** — 1 file (weekly)

Only endpoint AAII publishes is the weekly survey (Bullish/Neutral/Bearish %). No other data feeds. Cache is current. **No gaps. Done.**

INV-021 flag: no canonical prefetch script in `scripts/` for AAII — sentiment.py reads parquet but parquet was populated by some external means.

#### **G. CNN Fear & Greed (free, scrape)** — composite + 7 components

DEC-498 confirmed the 7 sub-components (junk_bond_demand, market_momentum_sp500, market_volatility_vix, put_call_options, safe_haven_demand, stock_price_breadth, stock_price_strength). All 7 cached. **Done.**

INV-021 flag: no canonical prefetch script in `scripts/` for CNN F&G.

#### **H. CFTC COT (free, Socrata)** — 19 contracts

Comprehensive financial coverage (e-mini SP500/NDX/RUT/Dow/VIX/treasury 2y/5y/10y/ultra/bond, fed funds, copper, gold, silver, dxy, eur/usd, jpy/usd, natural gas, wti). **Recommended additions (per owner — broad everything):**
- Agricultural: corn, wheat, soybeans, cattle, lean hogs, sugar, cotton, cocoa, coffee, OJ — ~10 contracts
- Other financials: 2-year+ Eurodollar, SOFR, GBP/USD, AUD/USD, CHF/USD, CAD/USD, NZD/USD — ~7 contracts
- Energy: Brent crude, heating oil, gasoline, propane — ~4 contracts
- Metals: platinum, palladium, lead, zinc, tin, aluminum — ~6 contracts

**Estimated:** ~27 new contracts × 1 endpoint = ~5 min. Trivial.

#### **I. Apewisdom (free, public)** — 1 file (global daily)

Cached endpoint: `/api/v1.0/filter/all-stocks` (top-trending across all subreddits). Other Apewisdom endpoints:
- `/api/v1.0/filter/wallstreetbets` — WSB-only timeline
- `/api/v1.0/filter/stocks` — r/stocks subreddit-only
- `/api/v1.0/filter/stockmarket` — r/stockmarket
- `/api/v1.0/filter/options` — r/options
- `/api/v1.0/filter/CryptoCurrency` — out of scope
- Per-ticker historical (if API supports — needs probe)

**Recommended:** add 4 subreddit-specific endpoints; probe per-ticker history. ~30 min.

#### **J. pytrends (Google Trends free)** — 1417/1937 (73.2%)

Only per-ticker SVI cached. Other dimensions:
- `interest_by_region(ticker)` — geographic (state-level)
- `related_queries(ticker)` — co-search analysis
- `related_topics(ticker)`
- `trending_searches(country='united_states')` — daily trending
- `realtime_trending_searches(country='united_states')`
- `top_charts(year, geo)` — top searches per year

**Recommended:**
- Top-up missing 520 ticker SVI (~3-4h, rate-limited)
- Add `interest_by_region` per ticker (1937 × 1 call)
- Add `related_queries` per ticker (1937 × 1 call)
- Add daily `trending_searches` going forward (cron)

**Estimated:** ~8-12h total, rate-limited. P2 priority.

#### **K. Wikipedia Pageviews (free)** — 1414/1937 (73.0%)

Cached: per-ticker daily pageviews. Other dimensions:
- Article revision history (volume of edits per day)
- Backlinks count
- Article categories
- Bytes-changed (proxy for content volatility)

**Recommended:**
- Top-up missing 523 tickers (~2h)
- Add daily revision counts per ticker (~2h)

#### **L. Alpha Vantage (free + premium tier?)** — 25 files news ONLY

INV-015 surfaced: AV news cached only 25 files (alphabetical range C..D, X — partial). Looks like prefetch died mid-alphabet. **Major under-coverage.**

**Other AV endpoints we don't use:**
- `TOP_GAINERS_LOSERS` — daily
- `LISTING_STATUS` — current + delisted tickers
- `EARNINGS_CALENDAR` — full historical earnings calendar
- `IPO_CALENDAR` — upcoming IPOs
- `INCOME_STATEMENT` / `BALANCE_SHEET` / `CASH_FLOW` — overlap with Polygon financials, but AV has older history
- `EARNINGS` (historical EPS surprises) — useful for PEAD strategies
- `OVERVIEW` (company overview)
- `EARNINGS_CALL_TRANSCRIPTS` (premium)
- `TIME_SERIES_INTRADAY_EXTENDED` — historical intraday
- `TECHNICAL_INDICATORS` — 60+ indicators (overlap; we compute)
- `COMMODITIES` — WTI / Brent / NG / Copper / Aluminum / Wheat / Corn / Sugar / Coffee / etc.
- `ECONOMIC_INDICATORS` — overlap with FRED
- `NEWS_SENTIMENT` (cached partial)

**Recommended:**
- Resolve INV-015: re-prefetch news at full 1937 universe
- New: TOP_GAINERS_LOSERS daily snapshot
- New: EARNINGS_CALENDAR (full historical + upcoming)
- New: EARNINGS (per-ticker EPS surprises)
- New: COMMODITIES (10+ contracts)

**Estimated:** ~10-15h for full re-prefetch + 4 new endpoints. P1 (news P0 if Phase 1B uses sentiment).

#### **M. Finnhub (free tier)** — 509 files news ONLY (S&P-only)

INV-016 surfaced: Finnhub cache locked at S&P 500 universe — never expanded to 1937.

**Other Finnhub endpoints we don't use:**
- `/stock/profile2` — company profile (sector, industry, IPO date, market cap)
- `/stock/insider-transactions` — overlap with Quiver/SEC; potential cross-validation
- `/stock/insider-sentiment` — Finnhub-derived
- `/calendar/earnings` — earnings calendar
- `/calendar/ipo` — IPO calendar
- `/stock/split` — splits
- `/stock/dividend` — dividends
- `/stock/peers` — peer companies (useful for sector-relative strategies)
- `/stock/recommendation` — analyst recommendation trends
- `/stock/price-target` — analyst price targets
- `/stock/eps-surprise` — EPS surprises
- `/stock/revenue-estimate` — revenue estimates
- `/stock/eps-estimate` — EPS estimates
- `/stock/upgrade-downgrade` — rating changes
- `/stock/social-sentiment` — Reddit/Twitter sentiment
- `/news` — general market news
- `/economic/calendar` — economic events calendar
- `/scan/pattern` — pattern recognition
- `/scan/support-resistance` — automated S/R
- `/calendar/economic`
- `/news-sentiment`

**Recommended:**
- Resolve INV-016: re-prefetch news at full 1937
- New: profile2 (sector cross-check vs Polygon)
- New: insider-sentiment + recommendation + price-target + eps-surprise + upgrade-downgrade — analyst layer for Phase 1B+
- New: social-sentiment + scan endpoints — pattern/sentiment overlay

**Estimated:** ~8-12h. P1.

### Cross-cutting summary

**Total newly-identified gaps to close (per owner "broad everything"):**
- Polygon: 7+ endpoints (indicators, quotes, holidays, conditions, exchanges, snapshot daily-capture)
- Quiver: 8+ endpoints to probe + 4-5 confirmed missing
- SEC EDGAR: 13 missing form types
- FRED: 25-30 additional series
- ALFRED: 7 series gap
- CFTC: 27 additional contracts
- Apewisdom: 4 subreddit endpoints + per-ticker history probe
- pytrends: top-up 520 + 3 dimensional adds
- Wikipedia: top-up 523 + revision counts
- Alpha Vantage: 5+ endpoints + news re-prefetch
- Finnhub: 15+ endpoints + news re-prefetch

**Estimated total wall time** (mostly unattended, rate-limited):
- P0 (Phase 1A blockers actively in flight): Quiver BG ~6h + Polygon reference BG ~1h
- P1 (Phase 1B blockers): ~30-40h aggregate
- P2 (broader / informational per owner directive): ~50-80h aggregate
- P3 (very informational): ~10-20h aggregate

**Total: ~90-150 hours of API fetch wall time** (most parallelizable; truly elapsed ~24-48h with concurrent jobs).

### Subscription confirmation needed (owner action)

Before scheduling P2/P3 prefetches, confirm:
1. **Polygon Options Starter** subscription? (separate from Stocks Starter $29/mo)
2. **Polygon Indices Starter** subscription? (for SPX/NDX/VIX direct vs ETF proxy)
3. **Quiver Trader plan tier** — does it include twitter/optionsflow/earningsbeats? (INV-012 saw 404 but verification was 1-ticker)
4. **AlphaVantage premium tier?** (free is rate-limited; premium has higher cap + earnings transcripts)
5. **Finnhub paid tier?** (free has 60/min; basic paid is much more)
6. **Any other paid APIs** I haven't enumerated? (Tradier, IEX Cloud, IBKR data feed, OpenBB Pro, Refinitiv?)

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
