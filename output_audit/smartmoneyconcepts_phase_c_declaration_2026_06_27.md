# smartmoneyconcepts Library — Phase C Declaration (DRAFT)

**Date:** 2026-06-27 | **Batch context:** P1 wiring audit follow-up (W3 finding) | **Status:** OWNER-DECISION REQUIRED
**Library:** `vendored/smartmoneyconcepts` pinned `1b62fd6c41e1f508e7ed76831a039fa4c82d42f6` (upstream joshyattridge/smartmoneyconcepts 0.0.27)
**Governing rule:** DEC-508 (3-phase A/B/C external-library fork integration mandate) + CHECKLIST #71
**Recommendation:** **DO NOT auto-declare Phase C.** Two viable paths surfaced — owner picks.

---

## 1. Current Phase status

Per `vendored/MANIFEST.md`: Phase A "IN PROGRESS"; Phase B "NOT STARTED"; Phase C "NOT STARTED".
**Per actual runtime state (W3 wiring audit 2026-06-27):** library is being consumed in PRODUCTION by 18 SMC strategies in `backtest/signals/screener.py` (`strat_smc_fvg_retest_long/short`, `strat_smc_inverse_fvg`, `strat_smc_breaker_block_long/short`, `strat_smc_mitigation_block_long/short`, `strat_smc_discount_long`, `strat_smc_premium_short`, `strat_smc_ote_long/short`, `strat_smc_bos_continuation_*`, `strat_smc_liquidity_sweep_*`, etc.). Strategies fire (post-B689 wire-in) and signals flow through `signal_loader.py` → engine entries → `trade_log.parquet`. **Effective state: Phase B canary running de-facto without explicit Phase B → C owner-approval gate having been crossed.** Doc-vs-reality drift = the declared gap.

---

## 2. Phase A — DEC-508 Tier 1/2/3 checklist

| Category | File | Status |
|---|---|---|
| Tier 1 unit (synthetic OHLCV) | `test_smartmoneyconcepts_unit.py` | ✅ PRESENT |
| Tier 1 PIT regression (freezegun) | `test_smartmoneyconcepts_pit.py` | ✅ PRESENT |
| Tier 2 integration (cache + composition) | `test_smartmoneyconcepts_integration.py` | ✅ PRESENT |
| Tier 2 performance | `test_smartmoneyconcepts_performance.py` | 🔴 PENDING |
| Tier 3 statistical sanity | `test_smartmoneyconcepts_statistical.py` | 🔴 PENDING |
| Tier 3 adversarial random-walk | `test_smartmoneyconcepts_adversarial.py` | 🔴 PENDING |
| Tier 3 cross-validation | `test_smartmoneyconcepts_xvalidation.py` | 🔴 PENDING |
| ≥90% line coverage | (any) | 🔴 NOT MEASURED |

**Verdict: Phase A 3/7 test files; 4 Tier 2/3 categories absent. Coverage threshold unverified.**

---

## 3. Phase B canary — DEC-508 checklist

| Item | Status | Evidence |
|---|---|---|
| Signals computed for full universe → `data_prefetch/ict_smc/{ticker}.parquet` | ⚠ MIXED | `smc_panel_cache.py` PIT-risk caveat documented; B554 parity test unresolved |
| Strategies DISABLED during canary | 🔴 VIOLATED | 18 SMC strategies LIVE in screener.py |
| Dashboard 2 (DEC-200) validates 20-50 signals | 🔴 NOT DONE | Dashboard 2 not launched |
| PIT regression on full universe | 🔴 NOT DONE | Only synthetic-OHLCV PIT run |
| Owner approval Phase B → C | 🔴 NEVER GIVEN | No record in EXECUTION_QUEUE or AUDIT |

---

## 4. Phase C — DEC-508 checklist (would-be promotion)

| Gate | Status |
|---|---|
| Strategies enabled | ✅ Already firing (anomalous; happened pre-declaration) |
| A/B vs baseline | 🔴 PENDING — no isolated rules-only-vs-rules+SMC comparison run |
| DEC-084 red-flag lookahead check | 🔴 PENDING — `event_recency_bars=90` + `dealing_range_lookback=50` + B262 forensic Pattern K dealing-range PIT lookahead concern unresolved |
| DEC-505 walk-forward (4 OOS folds × 1y) | 🔴 PENDING |
| B416 silent-failure root cause | 🔴 UNRESOLVED — 0 of 29,159 trades carried `smc_*` keys in AWS cube despite producer returning 28 keys in isolation; B416 added diagnostic logging but root cause never declared closed |
| Tier 4 visual + manual owner sign-off | 🔴 PENDING |
| Vendored-library SPOF sentinel test (B719 finding) | 🔴 PENDING — startup test asserting `smc` importable + key methods present has not been added to pyramid |

---

## 5. Recommendation

**Option-A (RECOMMEND): GATE-BEHIND-CANARY-FLAG.** Add `SMC_PHASE = "B-CANARY"` constant + per-strategy `if SMC_PHASE != "C": return _strat(False, ...)` short-circuit. Resolves doc-reality drift while preserving R5 cube measurability via a one-line flag flip when gaps close. Owner closes gaps in §4 + flips flag to `"C"`. Pyramid-safe.

**Option-B: DECLARE PHASE C WITH EXPLICIT GAPS LOG.** Update `MANIFEST.md` Phase C → IN PROGRESS with embedded gap-log (§4 entries verbatim). Honest documentation; no behavioral change; cube continues. Risk: B262-class disaster recurs without the gates DEC-508 was built to enforce.

**Option-C: HARD-DISABLE 18 SMC STRATEGIES until §4 gaps close.** Maximally conservative. Loses 18 strategies from R5 cube. R5 cube cells 217×26 → 199×26.

Council-style ranking: **Option-A** strictly dominates Option-B on safety + dominates Option-C on cube preservation; owner picks final.

---

## 6. Owner-action checklist (Tier 4 sign-off + Phase C gate-close items)

- [ ] Pick Option A / B / C
- [ ] If A: approve `SMC_PHASE` flag + initial value `"B-CANARY"` (≤30-line diff)
- [ ] Approve Phase A debt closure batch (write 4 missing test files; measure coverage ≥90%)
- [ ] Approve B416 root-cause investigation batch (forensic on 29,159-trade SMC-key absence)
- [ ] Approve DEC-505 walk-forward fold run for 18 SMC strategies (4 OOS × 1y)
- [ ] Approve DEC-084 lookahead red-flag audit on Pattern K dealing-range path + `event_recency_bars=90`
- [ ] Approve vendored-library SPOF sentinel test add (B719 finding; cheap)
- [ ] Visual review of 20-50 SMC signals on Dashboard 2 (DEC-200 prerequisite — owner to launch dashboard or waive)
- [ ] Sign-off statement in AUDIT.md declaring Phase C OPEN (with or without gaps logged)

**No code edits in this batch.** This is the declaration draft only.
