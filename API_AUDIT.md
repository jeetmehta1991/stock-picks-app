# API Endpoint Utilization Audit (DEC-410)

**Status:** IN PROGRESS — Pass 52 walkthrough cadence
**Scope:** ALL APIs across all phases (Pass 52 turn 19 owner-approved one-time CHECKLIST #56 override)
**Deliverable:** sub-decisions DEC-442+ logged based on findings; OpenBB consumption gap resolution; consolidation/deprecation recommendations

---

## Audit framework

Each API section answers four owner-mandated strategic questions (Pass 52 turn 20):

1. **Can this API be used in a better way?** (Beyond current consumption)
2. **Are we using everything offered by this API that can help the project?** (Endpoint utilization completeness)
3. **Is the cost worth it?** (Cost-benefit per API)
4. **Can the benefits and coverage offered by this API replace the need of some other APIs?** (Consolidation potential)

Plus 6-dimension cross-reference per DEC-410 schema:
1. Subscription tier + cost + rate limits
2. Available endpoints with PIT-safety/lookback/free-flag/used-flag
3. Currently consumed code references (file:function)
4. Gaps (endpoints in tier NOT consumed)
5. Use-case cross-reference (endpoints → 60+ strategies, ~11 agents, ~17 cube dims, BUGs)
6. Caching & rate-limit feasibility (S&P 500 × 5yr per DEC-411)

Plus hypothesis-driven framing: 2-4 explicit hypotheses per API to test in implementation.

### Honest knowledge limit (per CHECKLIST #51)

Endpoint inventories below are based on training data + audit cross-references. Subscription tiers and pricing change frequently. **Owner verification of current tier specs required before sub-decisions are finalized.** Hypotheses are framed as questions to answer during implementation, not pre-verified facts.

### Tiers

- **Tier 1** — Currently in PROJECT_PLAN section 10 (10 APIs)
- **Tier 2** — Mentioned in AUDIT.md as alternatives (5 APIs)
- **Tier 3** — Social/sentiment alternatives (2 APIs)
- **Tier 4** — Library-based data sources (3 libraries)

---

# Tier 1 APIs

## 1. yfinance — Currently primary OHLCV; multiple OPEN BUGs

### Subscription tier
- **FREE** (no API key required; uses Yahoo Finance public endpoints via library)
- Rate limits: aggressive throttling; documented Codespaces blocking (BUG-19)
- Reliability: known periodic outages; library deprecation risk (Yahoo has changed APIs multiple times)

### Available endpoints (via yfinance Python library)

| Endpoint | Returns | PIT-safe? | Currently used? |
|---|---|---|---|
| `Ticker.history()` | OHLCV bars (daily, weekly, monthly) | PARTIAL — auto_adjust=True causes drift (BUG-109/265) | YES |
| `Ticker.info` | Snapshot dict (PE, market_cap, sector, etc.) | NO — current snapshot only (BUG-218 CRITICAL OPEN) | LIMITED (~70 tickers per BUG-46) |
| `Ticker.financials` | Annual income statement | LIMITED (period_end only, no filing_date — CAV-070) | NO |
| `Ticker.quarterly_financials` | Quarterly income statement | LIMITED | NO |
| `Ticker.balance_sheet` | Balance sheet | LIMITED | NO |
| `Ticker.cashflow` | Cash flow | LIMITED | NO |
| `Ticker.earnings_dates` | Past + upcoming earnings | YES | LIMITED (BUG-280, BUG-013) |
| `Ticker.news` | Recent news (~10 items) | YES (date-stamped) | NO |
| `Ticker.options` | Option chains | YES | NO |
| `Ticker.recommendations` | Analyst recommendations history | LIMITED | NO |
| `Ticker.recommendations_summary` | Recommendation counts | LIMITED | NO |
| `Ticker.upgrades_downgrades` | Rating changes | LIMITED | NO |
| `Ticker.major_holders` | Institutional + insider holdings | NO (current only) | NO |
| `Ticker.institutional_holders` | 13F holdings | LIMITED | NO |
| `Ticker.dividends` | Dividend history | YES | NO (auto_adjust handles implicitly) |
| `Ticker.splits` | Split history | YES | NO (auto_adjust handles implicitly) |
| `Ticker.actions` | Combined splits + dividends | YES | NO |
| `Ticker.calendar` | Upcoming earnings + ex-div dates | YES | LIMITED |
| `Ticker.isin` | ISIN code | YES | NO |
| `Ticker.sustainability` | ESG scores | NO (current only) | NO |
| `download(tickers=[...], threads=True)` | Bulk OHLCV | PARTIAL | YES (cache.py) |

### Currently consumed code references

```
backtest/data/cache.py — get_ohlcv() bulk + per-ticker via yf.download
backtest/data/fetcher.py — per-ticker yf.Ticker calls
backtest/data/macro.py — VIX (^VIX) and DXY via yf.download
backtest/data/smart_money.py — fallback path for some lookups
backtest/data/universe.py — ticker metadata via Ticker.info
```

### Gaps (endpoints not consumed but available in free tier)

- `Ticker.options` — deferred per DEC-258
- `Ticker.recommendations` + `upgrades_downgrades` — analyst rating change strategies could exist; no current consumer
- `Ticker.institutional_holders` (13F) — Quiver provides better; redundant
- `Ticker.calendar` — could supplement DEC-256 if Polygon has gaps
- `Ticker.news` — superseded by Polygon news (DEC-440)
- `Ticker.sustainability` (ESG) — no current consumer; ESG strategies not in 60-strategy roster

### Use-case cross-reference

| Function | Currently consumed by | DEC-422 cube dims | Open BUGs |
|---|---|---|---|
| OHLCV daily history | ALL 60 strategies (foundation) | ALL 17 cube dims | BUG-19, BUG-46, BUG-62, BUG-109, BUG-265 |
| `.info` snapshot | universe.py (sector, mkt_cap) | sector dim, cap_band dim | BUG-218 (CRITICAL), BUG-179, BUG-46 |
| `.earnings_dates` | days_to_next_earnings() | days_to_earnings dim | BUG-280, BUG-013 |
| VIX / DXY | macro.py | VIX cube dim | None directly |

### Caching & rate-limit feasibility

- Daily OHLCV S&P 500 × 5yr: ~640K rows. yfinance can do this in 1-2 hours but **fails reliably in Codespaces** (BUG-19) — silent fallback issue
- `.info` calls: documented BUG-013 — ~106,000 live calls during backtest (catastrophic)
- `.earnings_dates`: BUG-280 silent None on block — unreliable in current env

### Owner question answers (Pass 52 turn 20)

**Q1: Can yfinance be used in a better way?**
NO meaningfully. The fundamental issue is reliability (BUG-19 Codespaces blocking, deprecation risk) and PIT correctness (BUG-218 CRITICAL OPEN, BUG-109 auto_adjust drift). The library does what it does; we cannot make it more reliable. The "better way" is to STOP relying on it for primary OHLCV.

**Q2: Are we using everything offered?**
~30% of available endpoints used. Unused endpoints (options, recommendations, ESG) have no current consumer per #57 — correct to skip. The under-utilization is NOT the problem; the problem is unreliability of WHAT we do use.

**Q3: Is the cost worth it?**
**Cost = $0 but reliability cost is HIGH.** Per the BUG inventory:
- BUG-218 CRITICAL OPEN
- BUG-109 HIGH OPEN (data drift; backtest non-reproducibility)
- BUG-179 HIGH OPEN
- BUG-19 (Codespaces blocking)
- BUG-46 (market_cap snapshot only 70 tickers)
- BUG-13 (106K live calls)
- BUG-265 + BUG-280 + CAV-070

**Hidden cost ≈ multiple weeks of debugging + ongoing reliability risk.** The "free" cost is misleading.

**Q4: Can yfinance be replaced by another API?**
**YES — Polygon $30/mo (DEC-441 just approved) covers all yfinance use cases:**
- OHLCV daily → Polygon `/v2/aggs/...` (PIT-clean, no auto_adjust drift)
- Sector / market_cap → Polygon `/v3/reference/tickers` (PIT-correct historical via reference endpoints)
- Earnings dates → Polygon events endpoint (DEC-256)
- VIX / DXY → Polygon also has these (or keep FRED for macro)

**Recommendation: Demote yfinance to fallback role only after Polygon prefetch lands. Resolves 6 OPEN BUGs (BUG-218, 109, 179, 46, 19, 265, 280, 13) simultaneously.** This is the single highest-leverage architectural change in the audit.

### Hypotheses to test in implementation

**H-yfinance-1 (HIGH leverage):** Polygon daily OHLCV equals or exceeds yfinance quality on test sample → demote yfinance to fallback. (= H1 from prior turn for Polygon)

**H-yfinance-2 (HIGH leverage):** Polygon reference data (sector, market_cap PIT) replaces yfinance `.info` → resolves BUG-218 CRITICAL + BUG-179 + BUG-46.

**H-yfinance-3 (MEDIUM leverage):** Polygon events endpoint replaces yfinance `.earnings_dates` → resolves BUG-280 + BUG-013.

### Sub-decision candidates (PROPOSED, not LOGGED — per L131/CHECKLIST #51)

- **DEC-442 PROPOSED** — Demote yfinance to fallback OHLCV source after Polygon prefetch validation. Resolves BUG-19/46/62/109/265.
- **DEC-443 PROPOSED** — Replace yfinance `.info` with Polygon reference endpoints. Resolves BUG-218/179.
- **DEC-444 PROPOSED** — Deprecate `days_to_next_earnings()` via yfinance live calls; route through DEC-256 Polygon earnings cache. Resolves BUG-280/013.

### yfinance verdict

**Demote to fallback after Polygon prefetch validates.** Keep available for VIX/DXY (free macro tickers Polygon also covers but yfinance works fine here) and as last-resort fallback. Free tier has hidden costs that justify the migration.

---

## 2. Polygon — Just-approved $30/mo subscription (DEC-441)

### Subscription tier
- **Stocks Starter $29/month** (per DEC-441)
- Rate limits: typically 5 calls/sec or unlimited per-minute on most endpoints; verify on signup
- Historical depth: 5+ years included on most endpoints; 15min delayed real-time

### Available endpoints (deep dive)

| Endpoint | Returns | PIT-safe? | Stage 1-2 use? |
|---|---|---|---|
| `/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}` | OHLCV bars (any interval) | YES | YES (DEC-441 OHLCV replacement) |
| `/v3/reference/tickers/{ticker}` | Ticker metadata (sector, mkt_cap PIT) | YES | YES (replaces yfinance.info) |
| `/v3/reference/tickers/{ticker}/events` | Earnings, dividends, splits events | YES | YES (DEC-256) |
| `/v3/reference/financials` | Quarterly fundamentals (filing_date native) | YES | YES (DEC-257) |
| `/v2/reference/news` | News articles + sentiment scores | YES (publish_date) | YES (DEC-440) |
| `/v3/reference/splits` | Historical splits | YES | Implicit |
| `/v3/reference/dividends` | Historical dividends | YES | Implicit |
| `/v1/indicators/sma/{ticker}` | Precomputed SMA | YES | NO (we compute) |
| `/v1/indicators/ema/{ticker}` | Precomputed EMA | YES | NO (we compute) |
| `/v1/indicators/rsi/{ticker}` | Precomputed RSI | YES | NO (we compute) |
| `/v1/indicators/macd/{ticker}` | Precomputed MACD | YES | NO (we compute) |
| `/v3/quotes/{ticker}` | Historical NBBO (intraday bid-ask) | YES | NO (slippage calibration potential) |
| `/v3/trades/{ticker}` | Historical trades (tick) | YES | NO (out of scope) |
| `/v2/snapshot/locale/us/markets/stocks/tickers` | All-tickers snapshot | NO (real-time) | NO (Stage 3+) |
| `/v1/marketstatus/now` | Current market status | NO (real-time) | NO (Stage 3+) |
| `/v1/marketstatus/upcoming` | Holidays, half-days | YES | LOW (existing pandas_market_calendars works) |
| `/v3/reference/conditions` | Trade/quote condition codes | YES | LOW |
| Options aggregates (multi-endpoint) | Options OHLC, OI, IV | YES | NO (DEC-258 deferred) |
| `/v2/last/trade/{ticker}` | Last trade price | NO (real-time) | NO (Stage 3+) |
| Treasury yields endpoint | US treasury yields | YES | NO (FRED authoritative) |

### Currently consumed code references

**ZERO** — Polygon not yet consumed. Subscription approved (DEC-441) but not implemented.

### Gaps

All endpoints are gaps (greenfield). The 4-5 we've decided to use (OHLCV, events, financials, news, reference) are committed but not yet implemented. The remaining 12+ are not committed.

### Use-case cross-reference

| Endpoint | Strategies | Agents | Cube dims | BUGs resolved |
|---|---|---|---|---|
| Aggregate bars (daily) | ALL 60 (replacement foundation) | ALL technical | ALL 17 | BUG-19, BUG-46, BUG-62, BUG-109, BUG-265 |
| Reference tickers (PIT) | universe management | None | sector dim, cap_band dim | BUG-218 (CRITICAL), BUG-179 |
| Events (earnings) | Earnings strategies (DEC-101) | Macro, Sentiment | days_to_earnings dim | BUG-13, BUG-280 |
| Financials | Fundamental strategies | Fundamental | smart money score, cap_band PIT | (CAV-070 mitigation via filing_date native) |
| News | Sentiment strategies | Sentiment | (potential news cube dim) | BUG-053, BUG-181 (per DEC-440) |
| Aggregate bars (intraday) | None Stage 2 | None Stage 2 | VIX intraday path, slippage | BUG-86 (CPI release timing precision) |
| Precomputed indicators | None directly | None directly | None | DEC-439 differential reference (Layer 5 strengthening) |
| Quotes (intraday bid-ask) | None Stage 2 | None Stage 2 | None | DEC-130 slippage calibration (deferred but data needed now for default) |
| Splits/dividends | All (PIT corrections) | None | None | BUG-109 mitigation |
| Options | Deferred per DEC-258 | None | None | None |
| Snapshots | None Stage 2 | None | None | None |
| Trades (tick) | None | None | None | None (out of scope) |

### Caching & rate-limit feasibility

- Daily aggregates S&P 500 × 5yr: ~640K rows. At Starter rate, ~1-2 hours full prefetch.
- Earnings events: 509 × ~20 quarters = ~10K rows. Trivial.
- Financials: 509 × ~20 quarters × 50 fields = ~510K cells. ~2-3 hours.
- News: rate-limited; need to verify but likely sufficient.
- Quotes (intraday) for slippage calibration: SELECTIVE only (sample 20 tickers × 30 days). Trivial.
- Reference data: <1 minute total.

### Owner question answers

**Q1: Can Polygon be used in a better way?**
YES significantly. Beyond the 4 jobs already approved (DEC-256/257/440/441 reference), three high-leverage uses are currently NOT scoped:
- Replace yfinance OHLCV (resolves 5 BUGs)
- Precomputed indicators as DEC-439 differential reference (zero-cost catch mechanism strengthening)
- Intraday quotes for slippage calibration (DEC-422 cell schema credibility)

**Q2: Are we using everything offered?**
At committed scope (4 endpoints): NO — we'd use ~25% of the tier. With proposed expansions (H-yfinance-1, H2 indicators, H3 slippage): ~60%. The remaining 40% (snapshots, real-time, tick trades) is correctly deferred (Stage 3+ or no consumer).

**Q3: Is the cost worth it?**
**$30/mo for 7+ use cases is exceptional value:**
- Earnings calendar (replaces broken Finnhub)
- News (replaces broken Finnhub + 25-ticker AV)
- Fundamentals (replaces unresolved OpenBB)
- Reference data (PIT correctness)
- OHLCV (replaces unreliable yfinance — 5 BUGs)
- Differential testing reference (DEC-439 strengthening)
- Slippage calibration (DEC-422 credibility)

Opportunity cost analysis: replacing yfinance alone closes 5 OPEN BUGs that would otherwise require weeks of debugging. **$30/mo pays for itself in week 1.**

**Q4: Can Polygon replace other APIs?**
YES — Polygon can effectively replace:
- yfinance (OHLCV, .info, earnings_dates) — demote to fallback
- Alpha Vantage (per DEC-440 already approved)
- Finnhub free-tier (per BUG-053/181 supersession)
- OpenBB (per DEC-410 expanded — likely "remove from scope")
- Potentially partial FRED replacement (treasury yields) — but FRED authoritative, keep FRED

**Net architecture simplification: 8 sources → 4 (Polygon + Quiver + FRED + AAII/CNN). Largest consolidation in the project.**

### Hypotheses (renumbered for cross-API consistency)

**H-polygon-1 (HIGH):** Daily OHLCV equals/exceeds yfinance quality. If TRUE → demote yfinance, resolve 5 BUGs.

**H-polygon-2 (HIGH):** Reference endpoints provide PIT-correct sector + market_cap historical → replace yfinance.info.

**H-polygon-3 (HIGH):** Precomputed indicators serve DEC-439 layer 5 differential reference at zero additional cost → strengthens catch-mechanism defense.

**H-polygon-4 (MEDIUM):** Intraday quotes enable Stage 2 slippage calibration → DEC-422 sharpe_at_5bps/10bps/20bps credibility.

### Sub-decision candidates (PROPOSED)

- **DEC-445 PROPOSED** — Polygon precomputed indicators integration as DEC-439 layer 5 differential reference.
- **DEC-446 PROPOSED** — Polygon intraday quotes selective fetch for slippage calibration sample (20 tickers × 30 days).
- **DEC-447 PROPOSED** — Polygon reference tickers PIT consumption pattern (replaces yfinance.info).

### Polygon verdict

**Highest-leverage API in the entire stack.** $30/mo pays for itself many times over. Three additional sub-decisions (DEC-445/446/447) beyond the 4 already approved should be considered.

---

## 3. FRED — Currently consumed for macro; PIT-correct via ALFRED (DEC-301)

### Subscription tier
- **FREE** (API key required; FRED_API_KEY env var)
- Rate limits: 120 requests/minute (generous for our scope)
- Historical depth: full series history (decades for most series)
- ALFRED archival endpoint provides vintage (PIT-correct) data per DEC-301 RESOLVED

### Available endpoints (FRED has 800,000+ series; here's category-level inventory)

| Category | Example series | PIT? | Currently used? |
|---|---|---|---|
| Yield curve / rates | T10Y2Y, DGS10, DGS2, DGS30, FEDFUNDS | YES (ALFRED) | PARTIAL (T10Y2Y, DGS10, FEDFUNDS in SERIES_MAP) |
| Inflation | CPIAUCSL, T10YIE, PCEPI | YES (ALFRED) | PARTIAL (CPIAUCSL, T10YIE) |
| Employment | UNRATE, PAYEMS, ICSA | YES (ALFRED) | PARTIAL (UNRATE) |
| GDP | GDPC1, A191RL1Q225SBEA | YES (ALFRED) | NO |
| Credit spreads | BAA10Y, AAA10Y, HY spreads | YES | PARTIAL (BAA10Y) |
| Money supply | M2SL, MZMSL | YES | NO |
| Industrial production | INDPRO, CAPACITYUTIL | YES | NO |
| Housing | HOUST, MORTGAGE30US | YES | NO |
| Consumer | UMCSENT, PCE | YES | NO |
| International | DEXUSEU, DEXJPUS | YES | NO (FX via yfinance currently) |
| Commodity | DCOILWTICO, GOLDAMGBD228NLBM | YES | NO |
| Sector indices | (multiple) | YES | NO |

### Currently consumed code references

```
backtest/data/macro.py — _fred_series() with ALFRED PIT support
SERIES_MAP = {
  "T10Y2Y": "yield_curve",
  "FEDFUNDS": "fed_funds",
  "UNRATE": "unemployment",
  "CPIAUCSL": "cpi",
  "T10YIE": "inflation_exp",
  "DGS10": "treasury_10y",
  "BAA10Y": "corp_spread",
}
```
**7 series consumed out of 800,000+ available.** Coverage is highly selective by design.

### Gaps

The "gap" framing doesn't fit FRED — there are 800K+ series, most irrelevant. Real question is: **which OTHER series should we add for Stage 2 use cases?**

Candidates for additions:
- **DGS2** (2-year treasury) — needed for full yield curve shape (currently only T10Y2Y spread + DGS10)
- **VIXCLS** (CBOE VIX from FRED) — alternative VIX source; FRED is authoritative; replaces yfinance ^VIX (BUG-19 risk)
- **HY spread series** — credit risk dimension for DEC-422 cube
- **DTWEXBGS** (Trade-Weighted Dollar Index) — alternative to yfinance DXY
- **ICSA** (initial jobless claims) — weekly leading indicator
- **MORTGAGE30US** — housing-sensitive sector exposure dim
- **DCOILWTICO** (WTI oil) — energy sector regime input
- **NFCIRESTBORR** (financial conditions index) — composite macro

### Use-case cross-reference

| Series | Strategies | Agents | Cube dims | BUGs resolved |
|---|---|---|---|---|
| T10Y2Y | Macro Agent | Macro | yield_curve_state dim (DEC-422) | None directly |
| FEDFUNDS | Macro Agent | Macro | (potential rate cycle dim) | None |
| UNRATE, CPIAUCSL | Macro Agent | Macro | (macro regime feature) | None |
| **VIXCLS (proposed)** | All vol-aware strategies | Risk | VIX_level_band dim | BUG-19 (yfinance ^VIX failure mode) |
| **DTWEXBGS (proposed)** | None Stage 2; potential currency/exporter strategies | Macro | None | (currency dim addition) |
| **DGS2 (proposed)** | None directly | Macro | yield_curve_state dim refinement | None |
| **ICSA (proposed)** | None Stage 2 | Macro | (weekly macro dim) | None |

### Caching & rate-limit feasibility

- 800K+ series × 5yr = trivially small per series (~1300 rows daily, ~260 weekly)
- Bulk prefetch all 7 currently-used series: <1 minute
- Adding 5-10 more series: <5 minutes
- ALFRED vintage queries: slightly slower but still trivial at our scale
- Rate limit (120/min) far exceeds our usage

### Owner question answers

**Q1: Can FRED be used in a better way?**
YES — significant unused coverage. Three patterns:
- **Add VIXCLS** to replace yfinance ^VIX (BUG-19 mitigation)
- **Add DTWEXBGS** to replace yfinance DXY
- **Expand series for cube dimensions** (DGS2 for yield curve shape, HY for credit, ICSA for weekly leading indicator)

**Q2: Are we using everything offered?**
NO — we use 7 series; FRED has 800K+. Most are irrelevant, but ~10 specific additions would meaningfully strengthen Stage 2 macro coverage.

**Q3: Is the cost worth it?**
ABSOLUTELY — free tier, generous rate limits, ALFRED PIT correctness already implemented per DEC-301. Best cost-quality ratio in the entire stack.

**Q4: Can FRED replace other APIs?**
PARTIAL: FRED can replace yfinance for ^VIX (resolves BUG-19 for that specific use case) and DXY. Cannot replace OHLCV, news, sentiment, earnings — different data domains.

### Hypotheses

**H-fred-1 (HIGH):** VIXCLS from FRED is more reliable than yfinance ^VIX in Codespaces (resolves BUG-19 partial).

**H-fred-2 (MEDIUM):** Adding DGS2 + HY spread + ICSA to SERIES_MAP measurably improves macro signal coverage for Macro Agent and DEC-422 cube dimensions.

**H-fred-3 (LOW):** ALFRED archival endpoint produces materially different values than current FRED endpoint for past observations (PIT correctness validation; if NO, DEC-301 mitigation may be over-engineered).

### Sub-decision candidates (PROPOSED)

- **DEC-448 PROPOSED** — Expand FRED SERIES_MAP with VIXCLS (replaces yfinance ^VIX), DTWEXBGS (replaces DXY), DGS2, HY spread, ICSA. Effort ~0.5d (just config addition + prefetch script update).
- **DEC-449 PROPOSED** — Validate DEC-301 ALFRED PIT mitigation produces materially different values than current FRED on test sample (validates BUG-86 fix scope was appropriate).

### FRED verdict

**Best free API in the stack.** Already PIT-correct per DEC-301. Underutilized — adding ~5-10 more series resolves BUG-19 partial + improves cube coverage. Zero-cost expansion.

---

# Batch 1 summary

| API | Verdict | Sub-decisions PROPOSED |
|---|---|---|
| **yfinance** | **Demote to fallback after Polygon validates** — multiple BUGs resolved | DEC-442/443/444 |
| **Polygon** | **Highest-leverage API in stack** — 7+ use cases at $30/mo; 3 additional sub-decisions beyond the 4 approved | DEC-445/446/447 |
| **FRED** | **Best free API** — already PIT-correct; expand SERIES_MAP for ~5-10 new series | DEC-448/449 |

**8 sub-decisions proposed.** None logged yet pending owner approval.

**Next batch (Batch 2):** Quiver, Finnhub, AAII, CNN F&G — smart money + sentiment APIs.

---
## 4. Quiver Quantitative — Currently consumed; multiple under-used endpoints + BUGs

### Subscription tier
- **Free tier** currently in use (per `backtest/data/smart_money.py` comment "Quiver Quantitative free tier: congressional, insider, 13F, analyst revisions")
- Premium: $50-100/month per PROJECT_PLAN section 10
- Rate limits: free tier is restrictive; documented as limiting in audit history
- Quiver retention status per PROJECT_PLAN: "✓ (final repair) for Stage 1-2"

### Available endpoints (Quiver tier overview)

| Endpoint | Returns | PIT-safe? | Currently used? |
|---|---|---|---|
| `/historical/congresstrading/{ticker}` | Congressional trades | YES | YES |
| `/historical/senatetrading/{ticker}` | Senate trades (separate) | YES | NO (BUG-190) |
| `/historical/housetrading/{ticker}` | House trades (separate) | YES | NO (BUG-190 implied) |
| `/historical/insidertrading/{ticker}` | Insider transactions (Form 4) | YES | YES |
| `/historical/13f/{ticker}` | Institutional 13F filings | YES (if filing_date captured per DEC-396) | YES |
| `/historical/analystratings/{ticker}` | Analyst rating changes | YES | YES (analyst revisions) |
| `/historical/govcontracts/{ticker}` | Government contract awards | YES (if Date field used per BUG-284) | YES (BUG-284 — date filter broken) |
| `/historical/lobbying/{ticker}` | Lobbying spend | YES | NO |
| `/historical/wikipedia/{ticker}` | Wikipedia traffic per ticker | YES | NO |
| `/historical/reddittraders/{ticker}` | Reddit trader activity (sentiment proxy) | YES | NO (BUG-190 — Twitter/Reddit/Off-Exchange/AppDownload not in prefetch) |
| `/historical/twittersentiment/{ticker}` | Twitter sentiment per ticker | YES | NO (BUG-190) |
| `/historical/offexchange/{ticker}` | Off-exchange / dark-pool volume | YES | NO (BUG-190) |
| `/historical/appdownloads/{ticker}` | App download stats (consumer signal) | YES | NO (BUG-190) |
| `/historical/sec13f/{ticker}` | Alternative 13F endpoint | YES | NO |
| `/live/...` | Real-time variants | NO (real-time) | NO (Stage 3+ only) |

### Currently consumed code references

```
backtest/agents/pipeline.py — Quiver in agent context
backtest/data/smart_money.py — _quiver_get() with cache-first lookups
backtest/engine/backtest.py — agent integration
backtest/run_phase1a.py — top-level runner
scripts/prefetch_quiver.py — prefetch script (BUG-284 date filter broken)
scripts/run_quiver_vscode.ps1 — Windows runner
scripts/validate_phase1b_data.py — validation
```

### Gaps (endpoints in tier NOT consumed — documented in BUG-190)

Per BUG-190 MEDIUM OPEN: "Quiver endpoints not in prefetch (Senate, Twitter, Off-Exchange, App Downloads)"

Specific gaps:
- **Senate trading separate** (currently bundled with congressional) — granularity loss
- **House trading separate** — same granularity issue
- **Lobbying spend** — leading indicator for regulatory tailwinds
- **Wikipedia traffic** — attention/awareness proxy
- **Reddit trader activity** — sentiment proxy
- **Twitter sentiment** — sentiment proxy
- **Off-exchange / dark pool volume** — institutional flow signal
- **App downloads** — consumer/product traction

### Use-case cross-reference

| Endpoint | Strategies | Agents | Cube dims | BUGs |
|---|---|---|---|---|
| Congressional trading | Smart money strategies | Smart Money | smart_money_score dim | None |
| Insider transactions | Smart money strategies | Smart Money | smart_money_score dim | None |
| 13F institutional | Smart money strategies | Smart Money | smart_money_score dim | DEC-396/BUG-241 (filing_date) |
| Analyst ratings | Analyst-change strategies | Sentiment | (analyst rating dim potential) | None |
| Government contracts | Defense/healthcare strategies | Macro | (sector tailwind dim potential) | BUG-284 (date filter broken) |
| Lobbying (UNUSED) | Regulatory strategies | Macro | (regulatory dim potential) | BUG-190 |
| Wikipedia (UNUSED) | Attention strategies | Sentiment | (attention dim potential) | BUG-190 |
| Reddit/Twitter (UNUSED) | Sentiment strategies | Sentiment | (sentiment_score dim feeder) | BUG-190 |
| Off-exchange (UNUSED) | Smart money strategies | Smart Money | (institutional flow proxy) | BUG-190 |
| App downloads (UNUSED) | Consumer strategies | Fundamental | (product traction proxy) | BUG-190 |

### Caching & rate-limit feasibility

- Free tier rate-limited; 9 endpoints × 509 tickers = ~4,500 prefetch calls per category
- Documented as constraining; PROJECT_PLAN suggests $50-100/mo premium for higher limits
- DEC-396 (filing_date capture) implementation pending — affects 13F PIT correctness
- BUG-284 (gov_contracts date filter broken) — date-based queries silently skip correctly

### Owner question answers

**Q1: Can Quiver be used in a better way?**
YES significantly. We use ~4-5 of 13+ endpoints. Per BUG-190, Senate/Twitter/Reddit/Off-Exchange/App Downloads are tier-available but not prefetched. Each represents a distinct signal class:
- Off-exchange volume → institutional flow (different from 13F)
- Lobbying → regulatory tailwind (leading indicator)
- Wikipedia/Reddit/Twitter → retail attention/sentiment (cube `sentiment_score` dim feeder)

Three architectural improvements:
1. Fix BUG-190 by extending `prefetch_quiver.py` to 8+ additional endpoints
2. Fix BUG-284 (gov_contracts date filter)
3. Implement DEC-396 (13F filing_date capture for PIT)

**Q2: Are we using everything offered?**
NO — ~30-40% of available endpoints used. The unused endpoints aren't speculative additions; they're documented gaps (BUG-190).

**Q3: Is the cost worth it?**
**Mixed.** Free tier IS being used and provides genuine value (smart money score is a meaningful cube dim). However:
- Free tier is rate-limited; full S&P 500 prefetch is slow (per audit history)
- Premium ($50-100/mo) would resolve rate limits and likely unlock additional endpoints
- **PROJECT_PLAN lists "Quiver retention pending Phase 0.A repair completion"** — suggesting retention itself is conditional

Recommendation: **resolve free-tier endpoint coverage first** (BUG-190, BUG-284, DEC-396). If free tier is used to its full extent, decide on premium upgrade based on whether more data quality / rate is needed.

**Q4: Can Quiver replace or be replaced by other APIs?**
Quiver is **largely irreplaceable for its primary use cases** at this price point:
- Congressional/insider trading: not available cheaply elsewhere
- 13F: also available via SEC EDGAR free, but Quiver provides cleaner aggregation
- Analyst ratings: yfinance/Polygon also provide; Quiver's coverage may be deeper
- Off-exchange / dark pool: Quiver-unique at retail price point
- Twitter/Reddit sentiment: alternatives exist (Stocktwits direct API) but Quiver bundles them

**Cannot consolidate Quiver away.** However, can consolidate analyst ratings (Quiver vs yfinance vs Polygon) — likely Quiver authoritative.

### Hypotheses

**H-quiver-1 (HIGH):** Fixing BUG-190 (extend prefetch to 8+ endpoints) materially strengthens Smart Money / Sentiment / Macro agents — net cube `sentiment_score`, `smart_money_score`, regulatory tailwind become available.

**H-quiver-2 (MEDIUM):** Free tier with full endpoint coverage is sufficient; premium upgrade ($50-100/mo) provides marginal benefit only if S&P 500 prefetch rate becomes bottleneck.

**H-quiver-3 (LOW):** SEC EDGAR free could supplement Quiver 13F at the cost of integration complexity; not worth it given Quiver bundles it.

### Sub-decision candidates (PROPOSED)

- **DEC-450 PROPOSED** — Extend `prefetch_quiver.py` to 8+ unused endpoints (Senate, House, Lobbying, Wikipedia, Reddit, Twitter, Off-Exchange, App Downloads). Resolves BUG-190. ~2-3 days.
- **DEC-451 PROPOSED** — Fix BUG-284 (gov_contracts date filter via Qtr+Year reconstruction or full Date field re-prefetch). ~0.5d.
- **DEC-452 PROPOSED** — Quiver premium upgrade decision after BUG-190 fix lands; evaluate based on rate-limit experience during full S&P 500 prefetch.

### Quiver verdict

**Keep free tier; fix BUG-190/284 + DEC-396 to maximize free-tier value before considering premium upgrade.** Three sub-decisions proposed; effort ~3-4 days total.

---

## 5. Finnhub — Severely scope-reduced post-DEC-440 supersession

### Subscription tier
- **Free tier** currently used (FINNHUB_API_KEY env var)
- Rate limits: ~60 calls/min on free tier (documented as causing BUG-053 "8-hour prefetch with empty results")
- Paid tiers: $25-150/month for higher rates

### Available endpoints (Finnhub free tier)

| Endpoint | Returns | PIT-safe? | Currently used? |
|---|---|---|---|
| `/news?category=general` + `/company-news` | News articles | YES | YES (broken — BUG-053/181) |
| `/calendar/earnings` | Earnings calendar | YES | NO (DEC-256 chose Polygon) |
| `/quote` | Real-time quote | NO | NO |
| `/stock/profile2` | Company profile | LIMITED | NO |
| `/stock/financials-reported` | SEC filings (free tier limited) | LIMITED | NO |
| `/stock/recommendation` | Analyst recommendations | LIMITED | NO |
| `/stock/peers` | Peer companies | LIMITED | NO |
| `/stock/insider-transactions` | Insider transactions | LIMITED | NO (Quiver authoritative) |
| `/stock/insider-sentiment` | Aggregated insider sentiment | LIMITED | NO |
| `/stock/social-sentiment` | Social sentiment | LIMITED | NO |
| `/stock/uspto-patent` | Patent filings | LIMITED | NO |
| `/stock/visa-application` | H1B/visa applications | LIMITED | NO |
| `/stock/lobbying` | Lobbying activity | LIMITED | NO (Quiver authoritative) |
| `/stock/usa-spending` | Government contracts | LIMITED | NO (Quiver authoritative) |
| `/stock/congressional-trading` | Congress trading | LIMITED | NO (Quiver authoritative) |
| `/economic` | Economic data | LIMITED | NO (FRED authoritative) |

### Currently consumed code references

```
backtest/agents/pipeline.py — Finnhub in agent context
backtest/data/smart_money.py — fallback path
scripts/prefetch_finnhub_news.py — broken news prefetch (BUG-053/181)
```

### Gaps (mostly N/A — Finnhub scope is shrinking)

Post-DEC-440 supersession, Finnhub's primary use case (news) is replaced by Polygon. Other endpoints are duplicates of better sources:
- Earnings → Polygon (DEC-256)
- Insider/Congressional → Quiver (authoritative)
- Lobbying / Gov contracts → Quiver
- Economic → FRED (authoritative)
- Recommendations → yfinance / Polygon

**Genuinely Finnhub-unique endpoints in free tier:**
- USPTO patent filings (no other source in our stack)
- Visa applications (H1B as hiring signal)
- Insider sentiment (aggregated, vs raw insider transactions from Quiver)

### Use-case cross-reference

| Endpoint | Currently consumed by | Strategy/Agent fit | Verdict |
|---|---|---|---|
| News | Sentiment Agent (broken) | Replaced by Polygon | Deprecate post-DEC-440 |
| USPTO patents (UNUSED) | None | Innovation/IP strategy potential | Speculative — no current consumer |
| Visa applications (UNUSED) | None | Hiring/growth signal | Speculative — no current consumer |
| Insider sentiment aggregate (UNUSED) | None | Smart money score enhancement | Marginal vs Quiver raw insider |

### Caching & rate-limit feasibility

- Free tier rate limit (~60/min) caused BUG-053 (8hr prefetch yielded empty files at S&P 500 scale)
- Even if news use case stays (it doesn't post-DEC-440), free tier insufficient
- Paid tier ($25-150/mo) duplicates Polygon coverage — bad value

### Owner question answers

**Q1: Can Finnhub be used in a better way?**
NOT MEANINGFULLY. Free tier rate limits + endpoint redundancy with better sources (Polygon, Quiver, FRED) means Finnhub has shrinking unique value.

**Q2: Are we using everything offered?**
NO — but the unused endpoints don't have consumers per #57. USPTO patents and visa applications are interesting in theory but no current strategy needs them.

**Q3: Is the cost worth it?**
NO — even free tier has hidden cost (BUG-053/181 broken integration, debugging time). Paid tier is bad value (duplicates Polygon). **Recommendation: deprecate Finnhub entirely from project.**

**Q4: Can Finnhub replace or be replaced?**
**Finnhub is replaced by Polygon (news) + Quiver (smart money) + FRED (macro) + yfinance (basic).** No reverse direction — Finnhub doesn't replace anything we have.

### Hypotheses

**H-finnhub-1 (HIGH):** Polygon news + Quiver smart money + FRED macro fully cover Finnhub's used scope post-DEC-440 → Finnhub has zero remaining unique value in our stack.

**H-finnhub-2 (LOW):** USPTO patents / visa applications could be useful for innovation-focused strategies → speculative, no current consumer per #57.

### Sub-decision candidates (PROPOSED)

- **DEC-453 PROPOSED** — Deprecate Finnhub from project entirely. Remove `prefetch_finnhub_news.py`, remove `FINNHUB_API_KEY` from config requirements, mark BUG-053/181 RESOLVED via deprecation (already WILL_RESOLVE_VIA_DEC-440 — final closure). Net architecture simplification: 1 fewer API to maintain.

### Finnhub verdict

**Deprecate entirely.** Polygon DEC-441 fully supersedes. Single sub-decision proposed. Architectural simplification.

---

## 6. AAII Sentiment Survey — Currently consumed; pub-lag BUGs

### Subscription tier
- **FREE** (CSV download from AAII; no API key)
- Update frequency: weekly (Wednesday survey, Thursday publication)
- Historical depth: full back to 1987

### Available data (single CSV, simple structure)

| Field | Returns | PIT-safe? | Currently used? |
|---|---|---|---|
| `survey_date` | Wednesday of survey week | NO directly (BUG-235) | YES |
| `bullish_pct` | % bullish | YES (post pub-lag) | YES |
| `neutral_pct` | % neutral | YES (post pub-lag) | YES |
| `bearish_pct` | % bearish | YES (post pub-lag) | YES |
| Spread (bullish - bearish) | Computed sentiment indicator | YES | YES (typically) |
| 8-week moving average | Smoothed | YES | NO |

### Currently consumed code references

Search shows AAII consumed but heavily through agent cache (JSON files in `backtest/agents/cache/`); no clear single-file integration point. Likely consumed via macro.py global or agent context.

### Gaps

The data is essentially complete (single CSV with 5 fields). No "endpoints" to add. Issues are operational:
- BUG-235 HIGH OPEN: pub-lag not respected (Wed survey marked tradeable Wed instead of Thu)
- BUG-236 HIGH OPEN: auto-refresh missing — committed CSV will go stale
- BUG-246 MEDIUM OPEN: module globals (incl. AAII) not multi-process safe
- DEC-318 PENDING (DEC-389 sub-decision): pub-lag treatment fix

### Use-case cross-reference

| Field | Strategies | Agents | Cube dims |
|---|---|---|---|
| Bullish/Bearish/Neutral % | Contrarian sentiment strategies | Sentiment | aaii_extreme dim (DEC-422) |
| Spread (bull-bear) | Extreme-sentiment reversal | Sentiment | aaii_extreme dim |
| 8-week MA (UNUSED) | Smoothed regime | Sentiment | (potential smoothed sentiment dim) |

### Caching & rate-limit feasibility

- CSV download is small (~38 years × 52 weeks = ~2000 rows total)
- No rate limit (it's a static file); auto-refresh weekly
- Storage trivial

### Owner question answers

**Q1: Can AAII be used in a better way?**
PARTIAL. Data is what it is (5 fields). Better USE means:
- Fix BUG-235 (pub-lag respect) per DEC-318
- Fix BUG-236 (auto-refresh)
- Consider 8-week MA as additional cube feature

**Q2: Are we using everything offered?**
~70% — primary fields used; 8-week MA derived metric NOT used currently.

**Q3: Is the cost worth it?**
ABSOLUTELY — free, simple, well-defined sentiment input. Per-cube AAII dim per DEC-422 makes it directly useful.

**Q4: Can AAII replace or be replaced?**
**Cannot be replaced cheaply.** AAII is a unique investor sentiment survey not duplicated elsewhere. CNN F&G is composite (different methodology). AAII is institutional-survey-based; specific value.

### Hypotheses

**H-aaii-1 (HIGH):** Fixing BUG-235 (pub-lag respect) per DEC-318 fixes a PIT correctness violation that currently leaks Wed survey into Wed trades.

**H-aaii-2 (LOW):** 8-week MA as derived feature adds marginal value beyond raw sentiment.

### Sub-decision candidates (PROPOSED)

No new sub-decisions — DEC-318/389 already cover the BUG-235 fix scope. AAII is well-handled.

### AAII verdict

**Keep as-is; ensure DEC-318 implementation fixes BUG-235/236 pub-lag.** No architectural change needed.

---

## 7. CNN Fear & Greed Index — Currently consumed; minor

### Subscription tier
- **FREE** (CNN scraping or unofficial JSON endpoints)
- Update frequency: daily during market hours
- Historical depth: limited; CNN doesn't publish full archive officially (alternative scraping or third-party archives)

### Available data

| Field | Returns | PIT-safe? | Currently used? |
|---|---|---|---|
| `fear_greed_value` (0-100) | Composite sentiment index | LIMITED (history reconstruction unreliable) | YES |
| `fear_greed_classification` | Extreme Fear / Fear / Neutral / Greed / Extreme Greed | LIMITED | YES |
| Sub-component (7 indicators making up the composite) | Individual components | LIMITED | NO |

### Currently consumed code references

Like AAII — consumed through agent cache + macro.py global (BUG-246 module globals not multi-process safe).

### Gaps

- Sub-component indicators (7 underlying signals: stock price momentum, stock price strength, etc.) NOT used — only composite
- Historical depth limited (CNN doesn't archive officially)
- No formal API; scraping fragile

### Use-case cross-reference

| Field | Strategies | Agents | Cube dims |
|---|---|---|---|
| Composite F&G value | Sentiment strategies | Sentiment | cnn_fg_band dim (DEC-422) — 5 bands |
| Sub-components (UNUSED) | None directly | Sentiment | None | 

### Owner question answers

**Q1: Can CNN F&G be used in a better way?**
MARGINALLY. Sub-components could be unpacked but no current consumer per #57. Composite is what we use; that's correct.

**Q2: Are we using everything offered?**
~50% (composite yes, sub-components no). But sub-components don't have consumer fit.

**Q3: Is the cost worth it?**
FREE; cube dim adds value. **Yes — minimal cost, modest benefit.** Caveat: scraping fragility means data quality risk (vs FRED/AAII which are stable sources).

**Q4: Can CNN F&G replace or be replaced?**
- CANNOT replace AAII (different methodology)
- CANNOT be cheaply replaced (no equivalent free composite sentiment)
- Premium alternatives (Refinitiv StarMine, Bloomberg) exist but $$$$

### Hypotheses

**H-cnn-1 (LOW):** Sub-component indicators add cube dimensions worth slicing on → speculative, defer until use case identified.

**H-cnn-2 (MEDIUM):** Scraping reliability over 5-year backtest is acceptable; if not, accept data gaps as caveat.

### Sub-decision candidates (PROPOSED)

No new sub-decisions — current use is appropriate scope.

### CNN F&G verdict

**Keep as-is; no architectural change.** Minor data source.

---

# Batch 2 summary

| API | Verdict | Sub-decisions PROPOSED |
|---|---|---|
| **Quiver** | Keep free tier; fix BUG-190/284 + DEC-396 to maximize value before premium upgrade | DEC-450, 451, 452 |
| **Finnhub** | **DEPRECATE entirely** — Polygon supersedes; architectural simplification | DEC-453 |
| **AAII** | Keep as-is; DEC-318 implementation fixes BUG-235/236 | None new |
| **CNN F&G** | Keep as-is; minor source | None new |

**4 additional sub-decisions PROPOSED (DEC-450 through DEC-453).**
**Cumulative Batch 1+2: 12 sub-decisions PROPOSED.**

**Next batch (Batch 3):** OpenBB, Alpha Vantage (deprecation), Unusual Whales, Ortex — fundamentals + Stage 3+ APIs.

---
## 8. OpenBB — PROJECT_PLAN says ✓ Stage 1-2, code shows ZERO consumption (consumption gap)

### Subscription tier
- **FREE** open-source SDK (Python `openbb` package)
- No API key required for core functionality (some integrations require third-party keys)
- Self-hosted; aggregates multiple data providers

### Available data (OpenBB SDK is meta-aggregator; here's high-level coverage)

| Capability | Underlying source | PIT-safe? | Currently used? |
|---|---|---|---|
| Fundamentals (income / balance sheet / cash flow) | yfinance + FMP + SEC EDGAR routing | LIMITED (depends on routing) | NO (zero consumption) |
| OHLCV history | yfinance + others | PARTIAL | NO |
| Macro indicators | FRED + others | YES (FRED-routed) | NO |
| News | Multiple providers | YES | NO |
| Analyst estimates | yfinance + others | LIMITED | NO |
| Insider transactions | SEC EDGAR + others | YES | NO |
| Crypto / forex | Various | LIMITED | NO |
| Options chains | yfinance + others | YES | NO |
| Earnings calendar | Multiple | YES | NO |
| Economic calendar | Various | YES | NO |
| Screener (custom queries) | Aggregated | LIMITED | NO |

### Currently consumed code references

**ZERO.** Despite PROJECT_PLAN section 10 listing OpenBB as ✓ for Stage 1-2 ("Fundamentals (replaces scraping)"), grep shows no imports, no calls, no integration anywhere.

**This is the "OpenBB consumption gap" formally flagged per DEC-410 + DEC-441.**

### Gaps

ENTIRE SCOPE — OpenBB is conceptually approved but never implemented. The 6 owner-mandated questions help resolve: should it be?

### Use-case cross-reference

Critical question: **what would OpenBB give us that Polygon (DEC-441) doesn't?**

| Use case | OpenBB | Polygon (DEC-441) | Delta |
|---|---|---|---|
| Fundamentals | yfinance / FMP / SEC routing | Native `/v3/reference/financials` with filing_date | Polygon better (PIT) |
| OHLCV | yfinance routing | Native `/v2/aggs/...` | Polygon better |
| News | Multiple | Native `/v2/reference/news` | Equal-to-better |
| Earnings calendar | Multiple | Events endpoint (DEC-256) | Equal |
| Macro | FRED-routed | FRED native (we already use directly) | FRED native better (DEC-301 ALFRED) |
| Insider transactions | SEC EDGAR routing | Not Polygon scope | Quiver authoritative |
| Options | yfinance | DEC-258 deferred | DEC-258 deferred |
| Screener | Aggregated multi-source | Not Polygon scope | OpenBB unique IF needed |
| Crypto / forex | Various | Some Polygon coverage | Out of scope |

**Net OpenBB unique value post-DEC-441: limited screener functionality only. All major use cases better covered by direct API integrations.**

### Caching & rate-limit feasibility

- OpenBB SDK depends on underlying provider rate limits (yfinance, FMP, SEC EDGAR free)
- Adds an integration layer that could obscure source-level errors
- Each fetch goes through SDK → underlying provider → response
- Latency and complexity overhead not justified for our scope

### Owner question answers

**Q1: Can OpenBB be used in a better way?**
Hypothetically yes (it's never been used). But "better way" framing assumes some baseline use; we have none. **The real question is: should there BE any use?**

**Q2: Are we using everything offered?**
NO — using 0% of capabilities. PROJECT_PLAN said ✓ but code never integrated.

**Q3: Is the cost worth it?**
Cost is integration effort (~3-5 days greenfield SDK integration). Per #57 use-case mapping, what does OpenBB give us that DEC-441 Polygon + Quiver + FRED doesn't? Nothing significant for Stage 0+Stage 2.

**Q4: Can OpenBB replace or be replaced?**
- **Reverse direction confirmed:** Polygon + Quiver + FRED collectively replace OpenBB's Stage 0+Stage 2 scope.
- OpenBB unique value (screener / multi-source aggregation) has no current consumer per #57.

### Hypotheses

**H-openbb-1 (DEFINITIVE):** Polygon (DEC-441) + Quiver + FRED collectively cover all OpenBB use cases for Stage 0+Stage 2 → OpenBB has zero unique remaining value at current scope.

**H-openbb-2 (LOW):** Future Phase 1C+ screener use cases could justify OpenBB integration → speculative, no current consumer per #57.

### Sub-decision candidates (PROPOSED)

- **DEC-454 PROPOSED** — Remove OpenBB from project scope. Update PROJECT_PLAN section 10 to remove OpenBB row. Resolves DEC-410 OpenBB consumption gap dual treatment per audit-as-source-of-truth principle (audit > PROJECT_PLAN). Net architecture: 1 fewer API to consider.

### OpenBB verdict

**REMOVE FROM PROJECT SCOPE.** Polygon DEC-441 supersedes; OpenBB has no unique value for Stage 0+Stage 2 use cases. Screener-driven future use cases can revisit at Phase 1C+. Single sub-decision PROPOSED.

---

## 9. Alpha Vantage — Already DEC-440 marked for Polygon replacement; this audit formalizes deprecation

### Subscription tier
- **FREE** with `ALPHAVANTAGE_API_KEY`
- Rate limits: 5 calls/min, 500 calls/day on free tier
- Paid tiers: $50-150/mo for higher limits
- Per DEC-440: replaced by Polygon (DEC-441 subscription)

### Available endpoints (Alpha Vantage, current consumption)

| Endpoint | Returns | PIT-safe? | Currently used? |
|---|---|---|---|
| `/news?function=NEWS_SENTIMENT` | News + sentiment scores | YES (publish_date) | YES (broken — 25-ticker cap, severe rate limits) |
| `/query?function=TIME_SERIES_DAILY_ADJUSTED` | OHLCV daily | YES | NO (yfinance authoritative) |
| `/query?function=INCOME_STATEMENT` | Annual income | LIMITED | NO |
| `/query?function=BALANCE_SHEET` | Balance sheet | LIMITED | NO |
| `/query?function=CASH_FLOW` | Cash flow | LIMITED | NO |
| `/query?function=EARNINGS` | Earnings history | YES | NO |
| `/query?function=EARNINGS_CALENDAR` | Upcoming earnings | YES | NO |
| `/query?function=ECONOMIC_INDICATORS` | Macro data | LIMITED | NO (FRED authoritative) |
| `/query?function=COMMODITIES` | Commodity prices | LIMITED | NO |
| `/query?function=CRYPTO_*` | Crypto data | LIMITED | NO |
| `/query?function=FX_DAILY` | Forex daily | LIMITED | NO |
| `/query?function=TECHNICAL_INDICATORS` | Precomputed indicators | YES | NO (Polygon offers via H-polygon-3) |
| `/query?function=COMPANY_OVERVIEW` | Company snapshot | NO (current only) | NO |

### Currently consumed code references (per DEC-440 marked for deprecation)

```
backtest/agents/pipeline.py — AV in agent context
backtest/data/smart_money.py — AV fallback path  
scripts/prefetch_alphavantage_news.py — AV news prefetch (25-ticker cap limited)
```

### Gaps

Most endpoints unused. Per DEC-440, Alpha Vantage scope is shrinking to deprecation, not expanding.

### Use-case cross-reference

| Endpoint | Currently consumed by | Polygon (DEC-441) replacement | Verdict |
|---|---|---|---|
| News sentiment | Sentiment Agent (broken — 25 ticker cap) | `/v2/reference/news` (DEC-440) | Replaced |
| Daily OHLCV (UNUSED) | None | `/v2/aggs/...` | Polygon better |
| Income statement (UNUSED) | None | `/v3/reference/financials` (filing_date) | Polygon better (PIT) |
| Earnings (UNUSED) | None | Events endpoint (DEC-256) | Polygon better |
| Macro (UNUSED) | None | FRED native | FRED authoritative |
| Technical indicators (UNUSED) | None | Polygon precomputed (H-polygon-3) | Polygon better (DEC-439 differential reference fit) |
| FX / Crypto / Commodities (UNUSED) | None | Out of scope | Out of scope |

### Caching & rate-limit feasibility

- Free tier 5 calls/min → essentially unusable at S&P 500 scale
- 25-ticker cap on AV's documented historical news limit blocks coverage
- Paid tier $50-150/mo duplicates Polygon coverage at higher cost
- **No path to making Alpha Vantage viable for our scope.**

### Owner question answers

**Q1: Can Alpha Vantage be used in a better way?**
NO — already marked for deprecation per DEC-440. Free tier rate limits are blocking; paid tier bad value vs Polygon.

**Q2: Are we using everything offered?**
~5% (only news, broken). Most endpoints unused.

**Q3: Is the cost worth it?**
NO — free tier has hidden cost (25-ticker cap blocking coverage). Paid tier duplicates Polygon.

**Q4: Can Alpha Vantage replace or be replaced?**
**Replaced by Polygon (DEC-441) confirmed per DEC-440.** Alpha Vantage replaces nothing in our stack.

### Hypotheses

**H-av-1 (DEFINITIVE):** Polygon DEC-441 fully covers all Alpha Vantage scope post-DEC-440 → AV has zero remaining unique value.

### Sub-decision candidates (PROPOSED)

- **DEC-455 PROPOSED** — Alpha Vantage deprecation timeline: (a) preserve existing AV cache parquet artifacts for transition; (b) remove AV from active prefetch scripts; (c) remove ALPHAVANTAGE_API_KEY from required config (mark optional during transition); (d) full removal post-Polygon news prefetch validation. Joint with DEC-440. ~0.5d cleanup.

### Alpha Vantage verdict

**Deprecate per DEC-440 confirmed; DEC-455 formalizes timeline.** Single sub-decision proposed.

---

## 10. Unusual Whales — Stage 3+ (inventory only per Pass 52 turn 19 override)

### Subscription tier
- **$50/month** (per PROJECT_PLAN section 10)
- Rate limits: typically generous on retail tier
- Stage 3+ scope per CHECKLIST #56; consumption decisions DEFERRED

### Available endpoints (Unusual Whales focuses on options flow + dark pool + congressional)

| Endpoint | Returns | PIT-safe? | Stage 1-2 use? |
|---|---|---|---|
| Options flow (real-time + historical) | Bullish/bearish flow, sweeps, blocks | LIMITED (real-time scoring) | NO (Stage 3+) |
| Unusual options activity alerts | Filtered alerts | LIMITED | NO (Stage 3+) |
| Dark pool prints | Dark pool transactions | LIMITED | NO (Stage 3+) |
| Congressional trading | Congress trades | YES | NO (Quiver authoritative for Stage 0+Stage 2) |
| Insider trading | Form 4 filings | YES | NO (Quiver authoritative) |
| Earnings calendar | Earnings dates | YES | NO (Polygon DEC-256 for Stage 0+Stage 2) |
| Short volume | Aggregated short volume | LIMITED | NO (Stage 3+) |
| Off-exchange volume | Off-exchange/block trades | LIMITED | NO (Quiver covers partial) |
| ETF flows | ETF inflow/outflow | LIMITED | NO (Stage 3+) |
| Greeks / IV surface | Options pricing dynamics | YES | NO (DEC-258 deferred) |
| Sector flows | Sector-level capital flow | LIMITED | NO (Stage 3+) |

### Currently consumed code references

**ZERO** — Stage 3+ scope; not yet consumed. Correct per CHECKLIST #56.

### Gaps

ENTIRE SCOPE — not yet consumed. Audit captures inventory for future Phase 1C / Stage 3+ planning.

### Use-case cross-reference (Stage 3+ POTENTIAL — not current)

| Endpoint | Future strategies | Future agents | Future cube dims |
|---|---|---|---|
| Options flow | Options-flow strategies (Phase 1C+) | Options Agent (potential) | options_sentiment dim (potential) |
| Dark pool prints | Smart money strategies | Smart Money | (institutional flow dim potential) |
| Greeks / IV surface | Volatility strategies | Risk | (IV regime dim potential) |
| Sector flows | Sector rotation strategies | Macro | sector dim feeder enhancement |
| Earnings calendar | (Already covered by Polygon Stage 0+Stage 2) | None | None |

### Owner question answers

**Q1: Can Unusual Whales be used in a better way?**
N/A — not in current scope. At Stage 3+ scope when paper-trading begins, options-flow strategies become candidate consumers.

**Q2: Are we using everything offered?**
Using 0% (correct per CHECKLIST #56 deferral).

**Q3: Is the cost worth it?**
$50/mo at Stage 3+ scope evaluation, NOT current. Per #57: only worth it when consumers exist (options strategies). Currently no consumers.

**Q4: Can Unusual Whales replace or be replaced?**
- Cannot replace Polygon/Quiver/FRED for Stage 0+Stage 2 scope.
- Has Quiver-overlapping endpoints (Congressional, insider) — Quiver authoritative at lower cost.
- **Unique value: options flow + dark pool prints + Greeks** — Stage 3+ specific.

### Hypotheses (Stage 3+ scope, not Stage 1-2)

**H-uw-1 (Stage 3+ ONLY):** Options flow + dark pool data add measurable signal value once Phase 1C options-flow strategies are added to roster.

### Sub-decision candidates

**NONE NEW** — DEFERRED_TO_STAGE_3 status. When/if Phase 1C options-flow strategies are scoped, revisit Unusual Whales subscription decision then.

### Unusual Whales verdict

**Inventory documented. Decision DEFERRED_TO_STAGE_3 per CHECKLIST #56.** Subscription evaluation re-opens at Phase 1C+ when options-flow strategies are scoped.

---

## 11. Ortex — Stage 3+ (inventory only per Pass 52 turn 19 override)

### Subscription tier
- **$40/month** (per PROJECT_PLAN section 10)
- Rate limits: typically generous on retail tier
- Stage 3+ scope per CHECKLIST #56; consumption decisions DEFERRED

### Available endpoints (Ortex focuses on short interest + borrow rates)

| Endpoint | Returns | PIT-safe? | Stage 1-2 use? |
|---|---|---|---|
| Short interest (daily est.) | Estimated daily short interest | LIMITED (daily reporting lag) | NO (Stage 3+) |
| Cost to borrow (CTB) | Borrow rate curve | NO (real-time) | NO (Stage 3+) |
| Days to cover (DTC) | Liquidity-adjusted short | LIMITED | NO (Stage 3+) |
| Short squeeze score | Composite squeeze indicator | LIMITED | NO (Stage 3+) |
| Available shares to short | Loan availability | NO (real-time) | NO (Stage 3+) |
| Historical short interest (bi-monthly NYSE/Nasdaq) | Settled short interest | YES (publish_date) | NO (Stage 3+) |
| ETF short data | ETF-level shorts | LIMITED | NO (Stage 3+) |
| FTD (failed-to-deliver) | Settlement failures | YES | NO (Stage 3+) |

### Currently consumed code references

**ZERO** — Stage 3+ scope; not yet consumed. Correct per CHECKLIST #56.

### Gaps

ENTIRE SCOPE — not yet consumed.

### Use-case cross-reference (Stage 3+ POTENTIAL)

| Endpoint | Future strategies | Future agents | Future cube dims |
|---|---|---|---|
| Short interest + DTC | Short squeeze strategies | Smart Money | short_interest_band dim (potential) |
| Cost to borrow | Long/short cost-aware strategies | Risk | borrow_cost dim (potential) |
| Squeeze score | Squeeze trigger strategies | Smart Money | None directly |
| FTD | Settlement-stress strategies | None directly | None |

### Owner question answers

**Q1: Can Ortex be used in a better way?**
N/A — not in current scope. Stage 3+ when squeeze/short-aware strategies enter roster.

**Q2: Are we using everything offered?**
Using 0% (correct per CHECKLIST #56 deferral).

**Q3: Is the cost worth it?**
$40/mo at Stage 3+ scope, NOT current. Short-aware strategies are speculative for our roster.

**Q4: Can Ortex replace or be replaced?**
- Free alternative for historical short interest: NYSE/Nasdaq publish bi-monthly settlement data (free via SEC, manually scrapeable).
- For DAILY estimates + borrow rates, Ortex is largely unique at retail price point.
- Bloomberg / Refinitiv have similar at much higher cost.

### Hypotheses (Stage 3+ scope)

**H-ortex-1 (Stage 3+ ONLY):** Short interest + DTC + borrow rates add measurable signal value if Phase 1C+ short-aware strategies are scoped.

**H-ortex-2 (LOW):** Free bi-monthly NYSE/Nasdaq short interest could substitute for daily estimates if precision is non-critical → speculative cost-saving.

### Sub-decision candidates

**NONE NEW** — DEFERRED_TO_STAGE_3 status.

### Ortex verdict

**Inventory documented. Decision DEFERRED_TO_STAGE_3 per CHECKLIST #56.** Re-evaluate at Phase 1C+ when short-aware strategies scoped. Free NYSE/Nasdaq alternative noted for cost-conscious revisit.

---

# Batch 3 summary

| API | Verdict | Sub-decisions PROPOSED |
|---|---|---|
| **OpenBB** | **REMOVE FROM PROJECT SCOPE** — Polygon DEC-441 supersedes; zero unique value for Stage 0+2 | DEC-454 |
| **Alpha Vantage** | Deprecate timeline per DEC-440 | DEC-455 |
| **Unusual Whales** | DEFERRED_TO_STAGE_3 — inventory only per #56 override | None new |
| **Ortex** | DEFERRED_TO_STAGE_3 — inventory only per #56 override | None new |

**2 additional sub-decisions PROPOSED.**
**Cumulative Batch 1+2+3: 14 sub-decisions PROPOSED, NOT LOGGED yet.**

**Next batch (Batch 4):** Tier 2 (Tiingo, IEX Cloud, FMP, SEC EDGAR, Refinitiv/Bloomberg), Tier 3 (Reddit, Stocktwits), Tier 4 libraries (smartmoneyconcepts, pandas-datareader, fredapi). Then summary turn.

---
# Tier 2 APIs — Alternatives mentioned in AUDIT.md (none currently consumed)

## 12. Tiingo

### Subscription tier
- **Free tier** (limited): 500 calls/hour, 1 year history
- **Power $10/mo**: more history, more endpoints
- **Premium $50/mo**: full coverage, real-time

### Available endpoints (Tiingo)

| Endpoint | Returns | PIT-safe? | Currently used? |
|---|---|---|---|
| `/iex/{ticker}/prices` | Daily OHLCV | YES | NO |
| `/tiingo/daily/{ticker}/prices` | Adjusted daily OHLCV | YES | NO |
| `/iex/?tickers=...` | Real-time IEX quote | NO | NO |
| `/tiingo/news` | News articles | YES | NO |
| `/tiingo/fundamentals/{ticker}/daily` | Fundamental ratios daily | LIMITED | NO |
| `/tiingo/fundamentals/{ticker}/statements` | Income/balance/cash flow | LIMITED | NO |
| `/tiingo/crypto` | Crypto data | LIMITED | NO |
| `/tiingo/fx` | Forex | LIMITED | NO |

### Owner question answers

**Q1-Q2:** Zero consumption; would offer overlapping coverage with Polygon DEC-441.

**Q3 — Cost worth it?**
- Free tier 1-yr history is insufficient for our 5-yr scope
- Power $10/mo + Premium $50/mo overlap with Polygon $30/mo
- **Worse value than Polygon for our use cases.**

**Q4 — Replace others?**
NO. Polygon DEC-441 covers Tiingo's strengths (OHLCV, news, fundamentals) at equal or better quality.

### Verdict: NOT NEEDED

No sub-decisions proposed. Document as "considered alternative; rejected per DEC-441 Polygon supersession."

---

## 13. IEX Cloud

### Subscription tier
- **Status: SUNSETTING.** IEX Cloud was discontinued by IEX Group August 2024 (publicly announced); legacy users transitioned through 2024.
- **Effectively unavailable for new integrations.**

### Owner question answers

All four questions moot — IEX Cloud is no longer a viable option as of mid-2024.

### Verdict: REMOVE FROM PROJECT_PLAN consideration

IEX Cloud is no longer purchasable. No sub-decision proposed. **Honest knowledge limit:** my training data on IEX Cloud sunsetting is approximate; owner may want to verify current status before fully striking from PROJECT_PLAN. If IEX successor service exists, scope appropriately.

---

## 14. Financial Modeling Prep (FMP)

### Subscription tier
- **Free tier**: 250 calls/day, limited fundamentals
- **Starter $14/mo, Premium $29/mo, Ultimate $79/mo**
- Strengths: fundamentals depth, decent rate limits at paid tiers

### Available endpoints (FMP)

| Endpoint | Returns | PIT-safe? | Currently used? |
|---|---|---|---|
| `/api/v3/historical-price-full/{ticker}` | OHLCV | YES | NO |
| `/api/v3/income-statement/{ticker}` | Income statement | LIMITED | NO |
| `/api/v3/balance-sheet/{ticker}` | Balance sheet | LIMITED | NO |
| `/api/v3/cash-flow/{ticker}` | Cash flow | LIMITED | NO |
| `/api/v3/key-metrics/{ticker}` | Computed ratios | YES | NO |
| `/api/v3/financial-growth/{ticker}` | Growth metrics | YES | NO |
| `/api/v3/discounted-cash-flow/{ticker}` | DCF valuation | LIMITED | NO |
| `/api/v3/earning-calendar` | Earnings calendar | YES | NO |
| `/api/v3/stock-news` | News | LIMITED | NO |
| `/api/v3/insider-trading/{ticker}` | Insider transactions | YES | NO |

### Owner question answers

**Q1-Q2:** Zero consumption.

**Q3 — Cost worth it?**
- $29/mo Premium overlaps with Polygon $30/mo
- FMP strength is **fundamentals-specific depth** (DCF, growth metrics computed)
- Could be cheaper than Polygon if ONLY fundamentals were needed — but we need OHLCV, news, etc. too

**Q4 — Replace others?**
PARTIALLY: FMP fundamentals could substitute Polygon `/v3/reference/financials` IF Polygon coverage proves inadequate per H-polygon hypotheses. Otherwise duplicate.

### Verdict: HOLD AS BACKUP option

If DEC-257 implementation reveals Polygon fundamentals coverage gaps for S&P 500 (verified during DEC-410 implementation, not pre-decided), FMP $29/mo is the cheapest alternative. Otherwise NOT NEEDED.

**No sub-decision proposed currently.** Conditional: revisit only if Polygon fundamentals fail.

---

## 15. SEC EDGAR

### Subscription tier
- **FREE** (US government; no API key required)
- Rate limits: ~10 requests/sec (very generous)
- Historical depth: full back to 1993+
- Format: XBRL filings (parsing complexity)

### Available data (SEC EDGAR)

| Data | Returns | PIT-safe? | Currently used? |
|---|---|---|---|
| 10-K / 10-Q filings | Quarterly/annual financials with native filing_date | YES (authoritative) | NO |
| 8-K filings | Material events (M&A, executive changes, etc.) | YES | NO |
| Form 4 (insider transactions) | Insider buy/sell with filing_date | YES | NO (Quiver authoritative for current scope) |
| Form 13F (institutional holdings) | Quarterly institutional positions | YES | NO (Quiver authoritative) |
| Form 13D/13G (>5% holders) | Major stake changes | YES | NO |
| Form S-1 (IPO filings) | New issuance disclosures | YES | NO |
| Form DEF 14A (proxy statements) | Compensation, governance | YES | NO |
| Form 4 timely-disclosure | Same-day insider | YES | NO |

### Owner question answers

**Q1: Better way?**
SEC EDGAR is the **authoritative regulatory source** with native filing_date — every other data provider derives from EDGAR. Better-way framing: parse EDGAR directly for highest-quality PIT correctness.

**Q2: Are we using everything offered?**
ZERO. EDGAR is fully unused.

**Q3: Cost worth it?**
**FREE.** No subscription cost. **Only cost is XBRL parsing complexity** — significant engineering effort (~5-10 days for full parser if doing fresh; libraries like `edgartools` or `python-secedgar` reduce this).

**Q4: Can SEC EDGAR replace others?**
- **Polygon `/v3/reference/financials`** — EDGAR is the underlying source; Polygon parses + serves. Direct EDGAR access could be more PIT-correct but slower / harder.
- **Quiver 13F + insider** — EDGAR is the authoritative source; Quiver aggregates.
- **Realistic answer:** EDGAR is the "ground truth" everyone derives from, but the **engineering cost of direct integration outweighs benefit when paid aggregators exist.**

### Verdict: HOLD AS PIT-VALIDATION TOOL

EDGAR could serve as **differential testing reference** per DEC-439 layer 5 catch mechanism. Polygon fundamentals vs EDGAR fundamentals comparison would catch parsing errors in either source.

### Sub-decision candidate (PROPOSED)

- **DEC-456 PROPOSED** — SEC EDGAR as DEC-439 differential testing reference for fundamentals PIT correctness. Sample 10 tickers × 4 quarters; parse via `edgartools` library; compare against Polygon `/v3/reference/financials` for same. Catches common-mode failures per CAV-068. ~2 days. **Stage 0+Stage 2 IN scope** as catch mechanism, not primary data source.

### SEC EDGAR verdict

**HOLD AS DIFFERENTIAL REFERENCE** — DEC-456 PROPOSED for DEC-439 layer 5 strengthening. Not primary source; not Stage 3+ deferred. Free + authoritative + zero ongoing cost = good fit for catch-mechanism use.

---

## 16. Refinitiv / Bloomberg

### Subscription tier
- **Bloomberg Terminal: $24,000+/year per seat**
- **Refinitiv Eikon: $22,000+/year per seat**
- Rate limits: typically generous; data quality is institutional-grade
- Used by hedge funds, banks, asset managers

### Available endpoints

Comprehensive — covers everything in our stack at higher quality. Bloomberg has BBG identifiers, Refinitiv has RIC codes; both have full corporate actions, fundamentals, earnings, options, fixed income, FX, commodities, news, sentiment, ESG, etc.

### Owner question answers

**Q1-Q2:** Zero consumption; would be massively over-spec for retail-scale strategy.

**Q3 — Cost worth it?**
**ABSOLUTELY NOT** for our scope. $22K-24K/year vs Polygon $30/mo = ~700-800x cost difference. The marginal data-quality improvement does not justify the cost at retail capital scale ($10K-50K+ Stage 4 target per PROJECT_PLAN).

**Q4 — Replace others?**
TECHNICALLY YES (Bloomberg/Refinitiv replace literally every other API in the stack). PRACTICALLY NO (cost-prohibitive).

### Verdict: NOT NEEDED — for institutional reference only

Document as "institutional reference; not viable at retail scale." No sub-decision proposed.

---

# Tier 3 APIs — Social / sentiment alternatives

## 17. Reddit (PRAW or Pushshift)

### Subscription tier
- **Reddit API: FREE** with rate limits + recent policy changes (post-2023 monetization)
- Pushshift archive: was free, now restricted
- PRAW (Python Reddit API Wrapper): free Python interface

### Available data

| Data | Returns | PIT-safe? | Currently used? |
|---|---|---|---|
| WallStreetBets posts/comments | Retail sentiment per ticker | YES | NO |
| Subreddit-specific (e.g. /r/investing, /r/SecurityAnalysis) | Discussion volume + sentiment | YES | NO |
| Post upvotes / mentions over time | Attention proxy | YES | NO |

### Owner question answers

**Q1: Better way?**
N/A — zero consumption.

**Q2: Are we using everything?**
ZERO.

**Q3: Cost worth it?**
- Free + access policy changes (Reddit's 2023 API monetization push) = unstable
- Engineering cost: significant (subreddit scraping, sentiment classification)
- **Quiver `/historical/reddittraders/` already provides Reddit signals as part of bundled access** — per Batch 2 finding (DEC-450 PROPOSED to extend Quiver prefetch to include Reddit endpoint)

**Q4: Replace others?**
- **Quiver covers Reddit signals (via DEC-450 PROPOSED).** Direct Reddit API integration = duplicate.

### Verdict: NOT NEEDED — Quiver supersedes

No sub-decision proposed. Direct Reddit access not needed; Quiver Reddit endpoint handles this within DEC-450 PROPOSED scope.

---

## 18. Stocktwits

### Subscription tier
- **Free public API**: limited (community-tier)
- **StreamingHub paid**: enterprise pricing, not retail-friendly
- Rate limits restrictive on free tier

### Available data

| Data | Returns | PIT-safe? | Currently used? |
|---|---|---|---|
| Symbol stream | Real-time messages per ticker | NO (stream) | NO |
| Symbol sentiment | Bullish/bearish ratio per ticker | LIMITED | NO |
| Trending tickers | Top mentioned tickers | NO (real-time) | NO |
| Watchlist counts | Aggregate retail interest | LIMITED | NO |

### Owner question answers

**Q1: Better way?**
N/A — zero consumption.

**Q2: Are we using everything?**
ZERO.

**Q3: Cost worth it?**
- Free tier rate-limited
- Quiver `/historical/twittersentiment/` proxy covers similar retail sentiment via Twitter (per DEC-450 PROPOSED)
- Stocktwits-specific value: bullish/bearish per-message tagging by users (Twitter doesn't have this) — but unique value per #57 has no current consumer

**Q4: Replace others?**
- Partially overlaps with Quiver Twitter sentiment endpoint (DEC-450 scope)
- Bullish/bearish tagging is unique but speculative consumer fit

### Verdict: NOT NEEDED — speculative consumer fit

No sub-decision proposed. Document as "considered; deferred until specific consumer use case emerges."

---

# Tier 4 — Library-based data sources

## 19. smartmoneyconcepts (Phase 0.D fork — DEC-045)

### Subscription tier
- **FREE** open-source Python library (joeanton719/smartmoneyconcepts)
- Per DEC-045 RESOLVED: forked into Phase 0.D as ICT/SMC pattern detector
- Computes signals from OHLCV (no external API calls)

### Available capabilities

| Capability | Returns | PIT-safe? | Currently used? |
|---|---|---|---|
| Fair Value Gap (FVG) | FVG levels + active flags | YES (computed from past bars) | NO directly (DEC-259 will use) |
| Break of Structure (BOS) | BOS event boolean | YES | NO directly |
| Change of Character (CHoCH) | CHoCH event boolean | YES | NO directly |
| Order Blocks | OB level identification | YES | NO directly |
| Liquidity Grabs | Liquidity grab event | YES | NO directly |
| Premium/Discount zones | Range-based zones | YES | NO directly |

### Currently consumed code references

**ZERO direct imports** in current code. DEC-045 RESOLVED scope says "Phase 0.D forked library" — implementation status not yet verified per pre-flight findings in Theme 3 walkthrough (DEC-259 explicitly notes Phase 0.D verification needed before consumption).

### Owner question answers

**Q1: Better way?**
The library IS the source for ICT/SMC patterns — no alternative. Better-way framing: ensure library is properly forked + integrated per Phase 0.D before DEC-259 consumes it.

**Q2: Are we using everything offered?**
ZERO currently. DEC-259 (just approved Theme 3) proposes consumption.

**Q3: Cost worth it?**
FREE. Engineering cost: ~2-3 days per DEC-259 (cache prefetch + integration).

**Q4: Replace others?**
NO replacement — ICT/SMC patterns are unique to this methodology.

### Verdict: ALREADY SCOPED via DEC-045 + DEC-259

No new sub-decision. Phase 0.D fork status verification is the open question (per DEC-259 dependency). When verified operational, DEC-259 implementation proceeds.

---

## 20. pandas-datareader

### Subscription tier
- **FREE** Python library; multi-source aggregator (similar role to OpenBB but lighter)

### Available capabilities

| Source | Coverage | PIT-safe? | Currently used? |
|---|---|---|---|
| FRED | Macro series | YES | NO (we use raw FRED HTTP) |
| Yahoo Finance | OHLCV | PARTIAL | NO |
| Google Finance | Discontinued | N/A | NO |
| Stooq | International markets | LIMITED | NO |
| OECD | Macro indicators | YES | NO |
| Eurostat | EU statistics | YES | NO |
| World Bank | Global indicators | YES | NO |

### Owner question answers

**Q1-Q2:** Zero consumption.

**Q3 — Cost worth it?**
- Free, but adds an abstraction layer (pandas-datareader → underlying provider → response)
- Same critique as OpenBB: indirection obscures source-level errors
- We already use FRED via direct `requests.get()` (cleaner)
- Polygon, Quiver have native libraries

**Q4 — Replace others?**
NO. Direct API integrations are cleaner than aggregator layers for our scope.

### Verdict: NOT NEEDED

No sub-decision proposed. Document as "considered; rejected — direct API integrations preferred."

---

## 21. fredapi

### Subscription tier
- **FREE** Python library (mortada/fredapi)
- Wrapper around FRED HTTP API

### Currently consumed code references — CORRECTION FROM PRIOR BATCHES

**Pre-flight finding:** I previously assumed fredapi was being used per "fredapi" mention in audit. **Verified: macro.py uses raw `requests.get()` against FRED HTTP API directly, NOT fredapi library.** The fredapi mention in AUDIT.md was likely an alternative considered but not adopted.

### Owner question answers

**Q1: Better way?**
Switching from raw `requests.get()` to fredapi library is a marginal stylistic improvement (less boilerplate, slightly cleaner). Not a meaningful "better way."

**Q2-Q3:** Zero consumption (correctly so — direct HTTP works fine).

**Q4 — Replace?**
fredapi could replace our raw HTTP FRED calls but adds dependency for negligible gain. ALFRED PIT support per DEC-301 is implemented in our raw HTTP path; fredapi may not natively support ALFRED queries.

### Verdict: NOT NEEDED

Direct HTTP integration in macro.py is appropriate. ALFRED PIT support per DEC-301 stays in raw HTTP path. No sub-decision proposed.

---

# Batch 4 summary

| API | Tier | Verdict | Sub-decisions PROPOSED |
|---|---|---|---|
| **Tiingo** | 2 | NOT NEEDED — Polygon supersedes | None |
| **IEX Cloud** | 2 | UNAVAILABLE (sunsetting/sunset 2024) | None |
| **FMP** | 2 | HOLD AS BACKUP if Polygon fundamentals fail | None (conditional) |
| **SEC EDGAR** | 2 | **HOLD AS DEC-439 DIFFERENTIAL REFERENCE** for fundamentals PIT validation | DEC-456 |
| **Refinitiv/Bloomberg** | 2 | NOT NEEDED — institutional pricing prohibitive | None |
| **Reddit** | 3 | NOT NEEDED — Quiver covers via DEC-450 PROPOSED | None |
| **Stocktwits** | 3 | NOT NEEDED — speculative consumer fit | None |
| **smartmoneyconcepts** | 4 | ALREADY SCOPED via DEC-045 + DEC-259 | None |
| **pandas-datareader** | 4 | NOT NEEDED — direct API integrations preferred | None |
| **fredapi** | 4 | NOT NEEDED — direct HTTP works; ALFRED PIT preserved | None |

**1 additional sub-decision PROPOSED** (DEC-456 SEC EDGAR as DEC-439 differential reference).
**Cumulative Batch 1+2+3+4: 15 sub-decisions PROPOSED, NOT LOGGED yet.**

**Critical correction:** fredapi was misclassified as consumed in prior reasoning. It's NOT consumed. macro.py uses direct HTTP. This is a #43 prior-art lapse self-caught during Batch 4 pre-flight.

**Next: Batch 5 summary turn — consolidating findings, full sub-decision logging proposal (DEC-442 through DEC-456), architectural simplification recap, owner approval batch.**

---
# Batch 5 — Summary, Architecture Simplification, Sub-Decision Logging Proposal

## Findings consolidation

### 17 APIs audited across 4 tiers

| Tier | Count | APIs |
|---|---|---|
| 1 — PROJECT_PLAN section 10 | 10 | yfinance, Alpha Vantage, Polygon, OpenBB, Quiver, Unusual Whales, Ortex, FRED, AAII, CNN F&G |
| 2 — AUDIT alternatives | 5 | Tiingo, IEX Cloud, FMP, SEC EDGAR, Refinitiv/Bloomberg |
| 3 — Social/sentiment | 2 | Reddit, Stocktwits |
| 4 — Library-based | 3 | smartmoneyconcepts, pandas-datareader, fredapi |
| **Note: Finnhub** | (Tier 1 inferred) | (was implicit in active stack via prior consumption; deprecated this audit) |

### Per-API verdict matrix

| API | Status post-audit | Sub-decisions PROPOSED |
|---|---|---|
| **Polygon** | NEW PRIMARY (DEC-441 active; expand to 7+ uses) | DEC-445/446/447 |
| **Quiver** | KEEP free tier; expand endpoints | DEC-450/451/452 |
| **FRED** | KEEP authoritative macro; expand SERIES_MAP | DEC-448/449 |
| **AAII** | KEEP as-is; DEC-318 fixes BUG-235/236 | None new |
| **CNN F&G** | KEEP as minor source | None new |
| **yfinance** | DEMOTE to fallback after Polygon validates | DEC-442/443/444 |
| **Alpha Vantage** | DEPRECATE per DEC-440 (timeline) | DEC-455 |
| **Finnhub** | DEPRECATE entirely (Polygon supersedes) | DEC-453 |
| **OpenBB** | REMOVE from project scope (consumption gap) | DEC-454 |
| **SEC EDGAR** | HOLD as DEC-439 differential reference | DEC-456 |
| **Tiingo** | NOT NEEDED | None |
| **IEX Cloud** | UNAVAILABLE (sunset 2024) | None |
| **FMP** | CONDITIONAL backup (Polygon fundamentals fail) | None (conditional) |
| **Refinitiv/Bloomberg** | NOT NEEDED (institutional cost prohibitive) | None |
| **Reddit** | NOT NEEDED (Quiver covers via DEC-450) | None |
| **Stocktwits** | NOT NEEDED (speculative consumer fit) | None |
| **smartmoneyconcepts** | ALREADY scoped via DEC-045 + DEC-259 | None |
| **pandas-datareader** | NOT NEEDED (direct API integrations preferred) | None |
| **fredapi** | NOT NEEDED (direct HTTP works; ALFRED preserved) | None |

---

## Architectural simplification trajectory

### Before this audit (Stage 0+Stage 2 active stack)

9 active sources (broken or planned):
1. yfinance (primary OHLCV; multiple BUGs)
2. Alpha Vantage (news, broken at scale)
3. Finnhub (news, broken via BUG-053/181)
4. Polygon (planned per DEC-440 but not subscribed)
5. OpenBB (PROJECT_PLAN says ✓ but never integrated)
6. Quiver (smart money, partially used)
7. FRED (macro, well-integrated)
8. AAII (sentiment, BUG-235/236)
9. CNN F&G (sentiment, minor)

### After audit + DEC-441 + sub-decisions adopted (target state)

4 active primary sources:
1. **Polygon** ($30/mo) — OHLCV, news, fundamentals, earnings, reference, indicators (DEC-439 differential), slippage calibration
2. **Quiver** (free tier; potential premium) — congressional, insider, 13F, analyst, lobbying, Wikipedia, Reddit, Twitter, off-exchange, app downloads
3. **FRED** (free) — macro time series with ALFRED PIT
4. **AAII + CNN F&G** (free) — sentiment cube dimensions

Plus:
- **yfinance** demoted to fallback (still in code; secondary role)
- **SEC EDGAR** as differential reference for DEC-439

Removed: Alpha Vantage, Finnhub, OpenBB.

### Cost analysis

| State | Monthly cost |
|---|---|
| Before (broken/aspirational mix) | $0 (Quiver free + Finnhub free + AV free) |
| After (Polygon primary) | **$30/mo Polygon + $0 Quiver free = $30/mo total** |
| Stage 3+ additional | +$50 Unusual Whales + $40 Ortex + $50-100 Quiver premium = $140-190/mo extra |

**Net Stage 0+Stage 2 monthly cost: $30** (confirmed budget per DEC-441).

### BUGs resolution trajectory

After all sub-decisions adopt:

| BUG | Severity | Status post-resolution path |
|---|---|---|
| BUG-218 (yfinance .info CRITICAL) | CRITICAL | Resolved by DEC-443 (Polygon reference replaces .info) |
| BUG-053 (Finnhub news empty) | HIGH | Already WILL_RESOLVE_VIA_DEC-440; DEC-453 finalizes |
| BUG-109 (yfinance auto_adjust drift) | HIGH | Resolved by DEC-442 (Polygon OHLCV demotes yfinance) |
| BUG-179 (yfinance .info live) | HIGH | Resolved by DEC-443 |
| BUG-181 (Finnhub silent empty) | MEDIUM | Already WILL_RESOLVE_VIA_DEC-440; DEC-453 finalizes |
| BUG-190 (Quiver endpoints not in prefetch) | MEDIUM | Resolved by DEC-450 |
| BUG-46 (market_cap snapshot 70 tickers) | (severity pending) | Resolved by DEC-443 |
| BUG-19 (yfinance Codespaces blocked) | (severity pending) | Resolved by DEC-442 (partial: VIX/DXY) and DEC-448 (FRED VIXCLS replaces) |
| BUG-265 (yfinance auto_adjust hardcoded) | LOW | Resolved by DEC-442 |
| BUG-280 (days_to_next_earnings None silent) | LOW | Resolved by DEC-444 |
| BUG-13 (106K live yfinance calls) | UNKNOWN | Resolved by DEC-444 |
| BUG-284 (gov_contracts date filter broken) | MEDIUM | Resolved by DEC-451 |
| BUG-235 (AAII pub-lag) | HIGH | Already covered by DEC-318/389 |
| BUG-236 (AAII auto-refresh missing) | HIGH | Already covered by DEC-318/389 |

**14 BUGs in resolution path through DEC-410 audit findings.** This is the audit's true value — not just inventorying APIs but identifying bug-resolution sequencing.

---

## Sub-decision logging proposal — owner approval batch

15 sub-decisions PROPOSED across batches 1-4. Per L131/CHECKLIST #51, holding for explicit owner approval before logging. Proposed log status for each:

### Polygon expansion (Batch 1, 3 sub-decisions)

- **DEC-445** — Polygon precomputed indicators integration as DEC-439 layer 5 differential reference
- **DEC-446** — Polygon intraday quotes selective fetch for slippage calibration sample (20 tickers × 30 days)
- **DEC-447** — Polygon reference tickers PIT consumption pattern (replaces yfinance.info)

### yfinance demotion (Batch 1, 3 sub-decisions)

- **DEC-442** — Demote yfinance to fallback OHLCV after Polygon prefetch validation
- **DEC-443** — Replace yfinance .info with Polygon reference endpoints (resolves BUG-218 CRITICAL + BUG-179)
- **DEC-444** — Deprecate days_to_next_earnings via yfinance live calls (resolves BUG-280/013)

### FRED expansion (Batch 1, 2 sub-decisions)

- **DEC-448** — Expand SERIES_MAP with VIXCLS, DTWEXBGS, DGS2, HY spread, ICSA (~0.5d config + prefetch update)
- **DEC-449** — Validate DEC-301 ALFRED PIT mitigation produces materially different values on test sample

### Quiver expansion (Batch 2, 3 sub-decisions)

- **DEC-450** — Extend prefetch_quiver.py to 8+ unused endpoints (Senate, House, Lobbying, Wikipedia, Reddit, Twitter, Off-Exchange, App Downloads). Resolves BUG-190. ~2-3 days.
- **DEC-451** — Fix BUG-284 (gov_contracts date filter via Qtr+Year reconstruction or full Date field re-prefetch). ~0.5d.
- **DEC-452** — Quiver premium upgrade decision after BUG-190 fix lands; conditional on rate-limit experience

### Finnhub deprecation (Batch 2, 1 sub-decision)

- **DEC-453** — Deprecate Finnhub from project entirely. Remove prefetch_finnhub_news.py; mark FINNHUB_API_KEY optional; close BUG-053/181 via deprecation. ~0.5d cleanup.

### OpenBB removal (Batch 3, 1 sub-decision)

- **DEC-454** — Remove OpenBB from project scope. Update PROJECT_PLAN section 10. Resolves DEC-410 OpenBB consumption gap dual treatment. ~0.25d documentation.

### Alpha Vantage deprecation (Batch 3, 1 sub-decision)

- **DEC-455** — Alpha Vantage deprecation timeline: preserve cache, remove from active prefetch, full removal post-Polygon news validation. Joint with DEC-440. ~0.5d cleanup.

### SEC EDGAR (Batch 4, 1 sub-decision)

- **DEC-456** — SEC EDGAR as DEC-439 differential reference for fundamentals PIT validation. Sample 10 tickers × 4 quarters via edgartools library; compare against Polygon. ~2 days. Stage 0+Stage 2 IN scope as catch mechanism.

### Total effort estimate (sub-decision implementation)

| Sub-decision | Effort |
|---|---|
| DEC-442 (yfinance OHLCV demotion) | absorbed into Polygon OHLCV prefetch implementation |
| DEC-443 (yfinance .info replacement) | ~1d |
| DEC-444 (yfinance earnings live deprecation) | absorbed into DEC-256 implementation |
| DEC-445 (Polygon indicators) | ~1d |
| DEC-446 (Polygon intraday slippage sample) | ~1d |
| DEC-447 (Polygon reference PIT) | absorbed into DEC-443 |
| DEC-448 (FRED SERIES_MAP expansion) | ~0.5d |
| DEC-449 (DEC-301 ALFRED validation) | ~0.5d |
| DEC-450 (Quiver endpoints extension) | ~2-3d |
| DEC-451 (Quiver gov_contracts date fix) | ~0.5d |
| DEC-452 (Quiver premium decision) | ~0.25d evaluation only |
| DEC-453 (Finnhub deprecation) | ~0.5d |
| DEC-454 (OpenBB removal) | ~0.25d |
| DEC-455 (Alpha Vantage deprecation) | ~0.5d |
| DEC-456 (SEC EDGAR differential) | ~2d |
| **Total net new effort** | **~10-12 days** (much absorbed into adjacent work) |

This is in addition to the underlying DEC-410 audit effort (~10-14 days for the audit itself, now complete via batches 1-4).

---

## DEC-410 closure status

**DEC-410 is READY FOR RESOLVED CLOSURE upon:**

1. Owner approval of 15 sub-decisions (DEC-442 through DEC-456) — batch approval
2. Sub-decisions logged in AUDIT_INDEX.md with PENDING status
3. DEC-410 status flipped PENDING → RESOLVED with cross-reference to all 15 sub-decisions
4. API_AUDIT.md committed (already done across 4 batches)

DEC-410 deliverable per its scope: "API_AUDIT.md committed; sub-decisions logged per gap" — both met upon owner approval.

---

## Honest acknowledgments (per L132 transparency standard)

Across the 4-batch audit:

1. **#43 prior-art lapse self-caught (Batch 4):** fredapi misclassified as consumed in earlier reasoning. Verified ZERO direct imports. Corrected within turn.

2. **Knowledge limits flagged per #51 throughout:** Endpoint inventories are training-data-derived hypotheses, not verified facts. Sub-decisions should treat hypotheses as questions to verify during implementation, not pre-confirmed answers.

3. **Stage 3+ APIs (Unusual Whales, Ortex):** included for inventory only per Pass 52 turn 19 "this instance" override. Consumption decisions remain CHECKLIST #56 scoped (deferred to Phase 1C / Stage 3 prep theme).

4. **CHECKLIST #56 override expires post-Batch 5:** going forward, scope filter resumes (Phase 0 + Stage 2 only). Stage 3+ decisions deferred per L135.

---

## Owner approval batch — pending

**Approve all 15 sub-decisions (DEC-442 through DEC-456) for logging?** OR specific approve/defer/reject per sub-decision?

If batch-approve all 15: I log all sub-decisions, mark DEC-410 RESOLVED, commit + push, and audit is closed.

If selective: please specify which to approve, defer, or reject.


---

## Pass 53 Update — API Audit Phase Mapping Update

**Trigger:** Phase 1A restoration (DEC-486/487/488 PROPOSED Pass 53).

**Phase mapping clarifications:**

API_AUDIT.md uses original Phase 1A/1B/1C/1D taxonomy from PROJECT_PLAN_ARCHIVE. Pass 53 restoration introduces sub-phase distinction:

| Reference in this doc | Pass 53 canonical mapping |
|---|---|
| "Phase 1B" (in subscription consumption notes) | Now refers to Phase 1B (agent overlay, Sprint 7); PRIOR rules-only phase = Phase 1A (Sprint 6.5) |
| "Phase 1C+" (in deferral notes) | Now refers to Phase 1C+ (Sprint 8 strategy categories); unchanged |
| "Stage 3+" (in deferral notes) | Unchanged |

**Subscription scope per phase (Pass 53):**

| API | Phase 1A (Sprint 6.5, rules-only) | Phase 1B (Sprint 7, agent overlay) | Phase 1B-α (Sprint 7-8, combined) |
|---|---|---|---|
| Polygon Stocks Starter (DEC-441/479 — $29/mo) | YES (OHLCV + reference) | YES | YES |
| Quiver paid (DEC-450 — ~$50-100/mo) | YES (smart money confluence) | YES (also via OurFundamentalsToolkit) | YES |
| FRED + ALFRED (free) | YES (regime classifier) | YES | YES |
| AAII + CNN F&G (free scrape) | YES | YES | YES |
| Anthropic API (DEC-058 LLM) | NO (--no-agents flag) | YES (~$50-100 dev cost) | YES (~$300 1B-α budget per DEC-059) |
| FMP (DEC-461) | NO | YES (toolkit consumption) | YES |
| Ortex (DEC-468) | YES (smart money signal direct read) | YES (toolkit consumption) | YES |
| Unusual Whales (DEFERRED_TO_STAGE_3) | NO | NO | NO |

**Phase 1A subscription pre-requisites (Sprint 6.5 entry):**
- Polygon Stocks Starter active ($29/mo)
- Quiver paid active (DEC-450)
- FRED API key configured (free)
- AAII + CNN F&G workflows operational from Sprint 1
- Anthropic API key NOT YET required (Phase 1A is `--no-agents`)

**Phase 1B subscription pre-requisites (Sprint 7 entry):**
- All Phase 1A subscriptions active
- Anthropic API key configured + budget pre-loaded
- FMP active (per Pass 52 turn 133 verification of DEC-460 negative — FMP mandatory)
- Ortex wired (DEC-468 implementation)

