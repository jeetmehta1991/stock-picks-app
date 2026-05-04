# Project Progress
**Updated:** April 25, 2026 — End of Day

---

## Current Blocker
Quiver API returning 500 errors on all endpoints since ~3pm EST. Retry tomorrow morning.

---

## Data Status

| Data | Status |
|---|---|
| OHLCV 509 tickers to March 2026 | ✅ |
| Quiver congressional | ✅ 509/509 |
| Quiver insider | ✅ 509/509 |
| Quiver institutional 13F | ⚠️ 51/509 — API outage |
| Quiver gov_contracts | ❌ 0/509 — API outage |
| Quiver lobbying | ❌ 0/509 — API outage |
| Quiver wikipedia | ❌ 0/509 — API outage |
| Quiver wallstreetbets | ❌ 0/509 — API outage |
| Alpha Vantage news | 🔄 4 batches running on GitHub Actions |
| FRED macro to March 2026 | ✅ |
| AAII sentiment | ✅ 325 readings |
| CNN Fear & Greed | ✅ 1,630 readings |

---

## What Was Done Today (April 25)

### Major Code Fixes (5 comprehensive audits)
- Fixed CRITICAL bug: smart_money_score returned wrong keys — all agent SM context was empty
- Fixed trailing stop to use intraday low/high (not close) — more realistic
- Fixed walk-forward: now two windows, sector-adjusted, INSUFFICIENT_OOS_DATA verdict
- Fixed survivorship bias: now hold-adjusted per trade
- Fixed crisis regime: now allows longs at 50% size (was blocking all — contradicted buy-the-dip)
- Fixed exit strategies (12 methods): all now use intraday low/high
- Fixed VIX/DXY: now reads from OHLCV cache, not live yfinance during backtest
- Fixed economic calendar: extended to March 2026
- Fixed Quiver live API fallback: disabled during backtest (prevents rate limit exhaustion)
- Added congressional age weighting: <30d full, 30-60d 50%, >60d excluded
- Added portfolio context to Decision Agent: sees open positions, sector concentration
- Added Kelly criterion to all strategy metrics
- Fixed Sharpe ratio: per-trade annualisation (not sqrt(252) which is for daily returns)
- Added sector concentration logging output
- Added portfolio compounding return with tier-based position sizing
- Added strategy-specific signals to Technical Agent (not just generic 10)
- Removed 40-day max hold period (illogical forced exit)
- Added AVOID tier correctly returned by confidence tier function
- Added preliminary_tier and agent_reasoning stored on every trade
- MAE/MFE now accumulated across full trade duration (was single day)
- Two-stage tiering fully implemented and tested
- Replaced Finnhub with Alpha Vantage news (better AI scores, full history, free)

### Tests
- 7/7 integration tests passing
- 29/29 unit tests passing
- End-to-end smoke test framework created

### Documentation
- PROJECT_PLAN.md: complete rewrite as flowing narrative for non-technical reader
- LEARNINGS.md: restructured as universal principles for all future projects

---

## Tomorrow Morning Actions

**Laptop (Git Bash) — check Quiver first:**
```bash
python -c "
import os, requests
token = os.environ.get('QUIVER_API_KEY','')
r = requests.get('https://api.quiverquant.com/beta/historical/congresstrading/AAPL',
    headers={'Authorization': f'Token {token}'}, timeout=10)
print(r.status_code, r.text[:60])
"
```

If 200 → run:
```bash
export QUIVER_API_KEY="your-key" ; python scripts/prefetch_quiver.py
```

**Check Alpha Vantage news batches on GitHub Actions** — all 4 should be green.

**After all data complete → run pre-run validation:**
```bash
python scripts/validate_phase1b_data.py
```

**Then 25-ticker batch test:**
```bash
nohup python backtest/run_phase1a.py --phase 1b --output-dir output_1b_test --start 2022-01-01 --end 2022-01-31 > batch_test.log 2>&1 &
tail -f batch_test.log
```

---

## PASS 53 STATUS UPDATE (Phase 1A Restoration)

**Discovery:** Phase 1A reference was inadvertently dropped from PROJECT_PLAN §3 sub-phases when Pass 52 turn 119 absorbed DEC-014 into DEC-422+426. PROJECT_PLAN_ARCHIVE.md confirmed Phase 1A v3 was COMPLETE (67 instruments × 4yr × 6,942 trades).

**Resolution:** DEC-486/487/488 PROPOSED + DEC-489 RESOLVED-DECIDED restore Phase 1A as 3 distinct sub-phases (1A baseline → 1A-α rules-only cube → 1A-β scale validation) preceding Phase 1B agent overlay.

**Updated Stage 2 sprint sequence:**

```
Sprint 0 (pre-flight) — owner subscriptions + DEC approvals
       ↓
Sprint 1 (Phase 0.A Polygon foundation, ~7-9d)
       ↓
Sprint 2 (Engine bug fixes Tier A, ~9d, parallel with Sprint 1)
       ↓
Sprint 3 (Phase 0.B Portfolio class, ~5-7d, sequential after Sprint 2)
       ↓
Sprint 4 (DEC-410 audit findings, ~5-7d, parallel with Sprint 3)
Sprint 5 (Universe management, ~5-8d, parallel with Sprint 3)
       ↓
Sprint 6 (Phase 0.E catch-mechanism, ~14-19d, parallel with Sprint 4-5)
       ↓
Sprint 6.5 — NEW Pass 53 (~19-27d engineering + ~26-33h compute):
  - Phase 1A: rules-only baseline (~6-8d + ~20-25h compute)
  - Phase 1A-α: rules-only cube + verdict + dashboards (~10-14d) ← Owner gate Sharpe ≥ 0.7 OOS
  - Phase 1A-β: production-scale dry-run (~3-5d + ~6-8h compute) ← Owner gate to commit $300 1B-α budget
       ↓
Sprint 7 (Phase 1B agent overlay, gated by Sprint 6.5 Phase 1A-α gate)
       ↓
Sprint 7-8 (Phase 1B-α combined cube run, gated by Sprint 6.5 Phase 1A-β cleared)
       ↓
Sprint 9 (Phase 1B-α verdict + dashboards review)
       ↓
Stage 2 → Stage 3 GO/NO-GO decision
```

**Pass 53 priorities pre-Sprint-1 (NOW):**
1. Owner approval of DEC-486/487/488 (Phase 1A restoration)
2. Owner approval of DEC-482 (walk-forward expanding window 2y+/6mo × 5 folds for 5y Polygon Stocks Starter window)
3. Owner approval of DEC-483 (R1000 + NDX universe expansion)
4. Owner decision on DEC-484/485 (FMP free alternative — SEC EDGAR direct vs drop financials)
5. Owner Polygon Stocks Starter subscription (per directive: "tonight")
6. Verify BUG-007 (API key guard blocks no-agent run) is resolved before Sprint 6.5 starts
7. Sprint 1 Day 1 begins after above complete

**Estimated total Stage 2 effort post-Phase-1A-restoration:** ~50-70 engineering days from Sprint 1 start to Phase 1B-α-ready (was ~30-40d pre-restoration).


---

## PASS 53 SPRINT 1 READINESS (post-batch approval)

**Pass 53 batch decision approval completed this turn (11 decisions).**

**Sprint 1 has zero formally-PENDING decisions.** It is genuinely ready to start once Polygon subscription is active.

**Pre-flight checklist for Sprint 1 Day 1:**

| Item | Status | Owner action |
|---|---|---|
| Polygon Stocks Starter $29/mo subscription | PENDING | Subscribe tonight |
| API key configured in local VS Code `.env` | PENDING | Add post-subscription |
| AAII URL accessible from local VS Code | UNVERIFIED | Verify Sprint 0 Day 1 |
| CNN F&G URL accessible from local VS Code | UNVERIFIED | Verify Sprint 0 Day 1 |
| SEC EDGAR domain accessible (for DEC-484 Sprint 4 + DEC-368 Sprint 5) | UNVERIFIED | Verify Sprint 0 Day 1 |
| BUG-007 API key guard verified for `--no-agents` | OPEN | Resolution before Sprint 6.5 (NOT Sprint 1 blocker) |

**Sprint 1 effort: ~25-35 engineering days (was ~7-9d pre-Pass-53; expanded by sub-tier universe scope + walk-forward driver)**

**After Sprint 1 cache complete + Sprints 2-6 Tier A bug fixes + catch mechanisms:**
→ Sprint 6.5 Phase 1A baseline run (~6-8d + ~20-25h compute)
→ Sprint 6.5-7 Phase 1A-α rules-only cube + dashboards (~10-14d)
→ Sprint 7 Day 1 Phase 1A-β scale validation (~3-5d + ~6-8h compute)
→ Owner gate: rules-only Sharpe ≥ 0.7 OOS authorizes Phase 1B agent overlay
→ Sprint 7 Phase 1B agent overlay
→ Sprint 7-8 Phase 1B-α $300 cube run
→ Stage 2 → Stage 3 GO/NO-GO

**Total path Sprint 1 Day 1 → Stage 2 verdict: ~50-70 engineering days realistic**

