# Engineering Register — Implementation Tracking

**Generated:** Pass 52 turn 42
**Purpose:** Per-sub-decision tracking from audit-decided to engineering-implemented
**Status semantics:**
- **RESOLVED-DECIDED:** owner-approved spec; engineering not yet started or in progress
- **RESOLVED-IMPLEMENTED:** engineering complete + tests passing per sub-decision Test Signals + verified
- **BLOCKED_ON_X:** decided but waiting on prerequisite

---

## Cadence

- **1-week sprints**
- **Sprint demo** at end of each week: working code + verified test signals
- **Owner reviews demo** + approves batch status flip RESOLVED-DECIDED → RESOLVED-IMPLEMENTED for completed sub-decisions
- **Engineer:** owner-self with Claude Code pair programming
- **Branch model:** feature branch per sprint; PR to main; merge after owner approval

---

## Sprint Roadmap

### Sprint 1 — Phase 0.A Polygon Foundation (Week 1)

**Entry criteria:**
- Polygon Stocks Starter $30/mo subscription active (DEC-441 owner-action: subscribe)
- API key in `.env` and Codespaces secret
- main branch in clean state

**Sub-decisions in scope:**
| DEC-N | Description | Test signals (verification criteria) | Branch | PR | Status |
|---|---|---|---|---|---|
| DEC-441 | Polygon $30/mo subscription | API key configured; sample fetch returns non-empty | (no code) | (owner action) | RESOLVED-DECIDED |
| DEC-256 | Polygon earnings prefetch | Non-empty parquet ≥95% S&P 500; days_to_earnings computable; PIT loader rejects EPS_actual queries with as_of < report_date | sprint1/dec-256 | - | RESOLVED-DECIDED |
| DEC-257 | Polygon→yfinance fundamentals | All 15 required fields ≥90% S&P 500 × 20 quarters; PIT loader rejects fields with as_of < estimated filing_date | sprint1/dec-257 | - | RESOLVED-DECIDED |
| DEC-440 | Polygon news endpoint | Non-empty news cache for sample; sentiment score field populates | absorbed in DEC-256 | - | RESOLVED-DECIDED |
| DEC-261 | ICT/SMC PIT N+1 lag rule | Synthetic FVG forms at bar 100 → strategy entry at bar 101 open | sprint1/dec-261 | - | RESOLVED-DECIDED |
| DEC-260 | Cache freshness assertion | Synthetic stale cache raises CacheStaleError; fresh cache passes; allow-listed stale ticker passes with warning | sprint1/dec-260 | - | RESOLVED-DECIDED |

**Exit criteria:**
- All 6 sub-decisions' test signals pass
- Sample backtest run uses Polygon as primary source for OHLCV/earnings/fundamentals
- All 6 promoted to RESOLVED-IMPLEMENTED on owner approval

**Effort:** ~7-9 engineering days
**Critical-path:** YES

---

### Sprint 2 — Engine Bug Fixes Tier A (Week 1-2, parallel with Sprint 1)

**Entry criteria:**
- Sprint 1 not blocking Sprint 2 directly (parallel-friendly)
- Cache infrastructure understood

**Sub-decisions in scope (13):**
DEC-381/382/383/384/388/389/390/391/392/394/397/398/399 — all RESOLVED-DECIDED.

| Group | DEC-N | Test signal |
|---|---|---|
| Cache | DEC-381/382/383 | Front-extension fail-fast; min(20,available) flag; zero-volume preserved with is_halted col |
| Stops | DEC-384 | Intraday HIGH/LOW used; trailing stop reflects intraday extreme |
| Regime | DEC-388 | VIX 5-day SMA hysteresis (≥40 enter, <35 exit) |
| Sentiment | DEC-389/390/391 | AAII pub-lag 1-day shift; auto-refresh script + GH Actions; CNN F&G last-published with age_days |
| Universe | DEC-392/394 | Liquidity filter fail-closed with enum reasons; sector_history.csv loaded |
| Methodology | DEC-397 | Rolling 4yr/1yr train/oos windows configurable |
| Costs | DEC-398/399 | Borrow cost path investigated; consolidated to backtest.engine.costs |

**Exit criteria:** all 13 test signals pass; promote to RESOLVED-IMPLEMENTED.
**Effort:** ~9 engineering days
**Critical-path:** YES (cache/stops are foundational)

---

### Sprint 3 — Phase 0.B Portfolio Class (Week 2-3, sequential after Sprint 2)

**Entry criteria:**
- Sprint 2 cache fixes (DEC-381/382/383) merged
- BUG-095 scope clarified

**Sub-decisions in scope:**
| DEC-N | Description | Test signal |
|---|---|---|
| (no DEC; this implements BUG-095 fix) | Portfolio class with state (open positions, equity curve, peak equity) | All open positions tracked; equity curve continuous; peak_equity monotonic |
| DEC-070 | Portfolio-level exit logic | Drawdown trigger (>30%) flattens portfolio; market-wide breaker integration |
| DEC-076 | Factor exposure breaker | Aggregate exposure threshold halts new entries in that factor |

**Exit criteria:**
- BUG-095 closed via Portfolio class implementation
- DEC-070, DEC-076 promoted PENDING-BLOCKED → RESOLVED-IMPLEMENTED

**Effort:** ~5-7 engineering days
**Critical-path:** YES (blocks Phase 1B-α run)

---

### Sprint 4 — DEC-410 Audit Findings (Week 2-3, parallel with Sprint 3)

**Sub-decisions in scope (15):** DEC-442/443/444/445/446/447/448/449/450/451/453/454/455/456 + DEC-441 verification.

| Group | DEC-N | Test signal |
|---|---|---|
| yfinance demotion | DEC-442/443/444 | yfinance demoted to fallback; .info replaced; earnings live calls eliminated |
| Polygon expansion | DEC-445/446/447 | Precomputed indicators match our pandas; intraday quotes for slippage; reference PIT |
| FRED expansion | DEC-448/449 | Joint with DEC-407 — see Sprint 7. ALFRED PIT validated. |
| Quiver expansion | DEC-450/451 | All paid endpoints prefetched; gov_contracts date filter works |
| Cleanup | DEC-453/454/455 | Finnhub/OpenBB/AV deprecated and removed |
| EDGAR | DEC-456 | EDGAR vs Polygon fundamentals divergence ≤ tolerance |

**Effort:** ~5-7 engineering days
**Critical-path:** Some items (DEC-443 BUG-218 fix) yes; others parallel-friendly

---

### Sprint 5 — Universe Management (Week 3-4, parallel)

**Sub-decisions in scope (12):** DEC-363/364/365/372/373/374/375/376/378/379/380/457

| Group | DEC-N | Test signal |
|---|---|---|
| ETFs + Tier 3 size | DEC-363/364 | LIT/DBB/COPX in universe; Tier 3 = 100 |
| Russell 1000 | DEC-365 | Russell 1000 mid-cap add ≈ 500 names with tier liquidity |
| Tier 2 phases | DEC-372/373/374 | GH Actions monthly; --validate mode; historical backfill 2010-2024 |
| Tier 3 phases | DEC-375/376 | MAX_TICKERS=100; GH Actions automation |
| Spinoff detector | DEC-378/379/380 | NASDAQ symbol diff; SEC EDGAR Form 10-12B; Polygon corporate actions |
| Liquidity filter | DEC-457 | Tier-specific thresholds applied; rejection rate < 30% per tier |

**Effort:** ~5-8 engineering days
**Critical-path:** Tier 2 & 3 + Russell 1000 needed for full universe; can defer DEC-374 (historical backfill)

---

### Sprint 6 — Phase 0.E Catch-Mechanism Defense (Week 4-5, parallel)

**Sub-decisions in scope (5):** DEC-417/436/437/438/439

| DEC-N | Description |
|---|---|
| DEC-417 | Test-run audit gate retroactive validation |
| DEC-436 | CI/CD gate (smoke + property + characterization) |
| DEC-437 | Property-based testing (hypothesis library) |
| DEC-438 | Characterization tests for known-good behaviors |
| DEC-439 | Differential testing (pandas vs numpy + Polygon vs SEC EDGAR) |

**Effort:** ~7-10 engineering days
**Critical-path:** Required for Phase 1B-α confidence

---

### Sprint 7 — Statistical Methodology (Week 5-6, parallel)

**Sub-decisions in scope (16):** DEC-400/401/402/403/404/405/406/407/408/409/412/413/414/415/416/423 (+ DEC-411 blocked on DEC-298)

Implementation per Theme X4 Block 3 sequencing in AUDIT_INDEX.md.

**Effort:** ~17-19 engineering days

---

### Sprint 8 — Strategy Categories (Week 6-7, parallel — NOT critical path)

**Sub-decisions in scope (5):** DEC-367/368/369/370/371

**Effort:** ~14-18 engineering days

---

### Sprint 9 — Phase 1B-α Run (Week 5-6 earliest)

**Entry criteria:**
- Sprints 1-6 RESOLVED-IMPLEMENTED
- Universe stable; cube populating per DEC-422

**Output:** Phase 1B-α backtest results across 60 strategies × dimensional cube cells

---

## Critical Path Gate

**Phase 1B-α cannot run until:**
- Sprint 1 RESOLVED-IMPLEMENTED (Phase 0.A foundation)
- Sprint 2 RESOLVED-IMPLEMENTED (engine bug fixes Tier A)
- Sprint 3 RESOLVED-IMPLEMENTED (Phase 0.B Portfolio class)
- Sprint 4 partial — at minimum DEC-443 (yfinance .info replacement; resolves BUG-218 CRITICAL)
- Sprint 6 RESOLVED-IMPLEMENTED (Phase 0.E catch mechanisms)

**Estimate: ~21-25 engineering days minimum critical path; ~30-40 days realistic with parallelism.**

---

## Verification gate process (per sprint)

1. Engineer (owner) implements sub-decision per spec text
2. Test signals from sub-decision text pass in CI
3. Owner reviews demo at sprint end
4. Owner approves batch status flip RESOLVED-DECIDED → RESOLVED-IMPLEMENTED for the completed sub-decisions
5. ENGINEERING_REGISTER updated; AUDIT_INDEX status flipped; commit + push

---

*Per CHECKLIST #43/#46/#47/#56/#57. Pass 52 turn 42.*
