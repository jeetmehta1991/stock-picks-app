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
- **Stocks Starter $30/month** (per DEC-441)
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
