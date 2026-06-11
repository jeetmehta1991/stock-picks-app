# B702 Phase-0 Production Audit — `compute_pead_signals` vs Bitemporal Hazards

<!-- Source: scripts/run_b702_production_audit_pead.py + scripts/earnings_feed_pit_audit.py per CHECKLIST #77 -->

**Date:** 2026-06-11
**Tool:** [scripts/earnings_feed_pit_audit.py](scripts/earnings_feed_pit_audit.py) (external reviewer, B702-saved) + [scripts/run_b702_production_audit_pead.py](scripts/run_b702_production_audit_pead.py) (production wrapper)
**Subject:** [backtest/signals/pead.py:compute_pead_signals](backtest/signals/pead.py)
**Discipline:** validate-against-known-ground-truth — auditor earned trust via [scripts/validate_earnings_feed_pit_audit.py](scripts/validate_earnings_feed_pit_audit.py) before being deployed.

---

## 0. Validator gate (precondition)

The auditor MUST pass its own 4-case validation before any production verdict is meaningful. Result:

```
honest producer all-PASS:            PASS
peeker caught on exactly H1+H2:       PASS
ALL CHECKS: PASS
```

Selectivity check: the peeker is caught on **exactly** the two cases where peeking changes the answer (value_restatement, date_reanchor) and correctly passes the two non-discriminating cases (yago_base_restatement — restatement was already public; gap_contamination — peeker derives from EPS). A blanket-flagger would be a useless auditor. This one discriminates.

---

## 1. Production verdict

| Case | Hazard | Verdict |
|---|---|---|
| `value_restatement` | H2 (EPS restated post-announcement) | **PASS_PIT_CLEAN** |
| `yago_base_restatement` | H2 (year-ago base restated, already public) | **PASS_PIT_CLEAN** |
| `date_reanchor` | H1 (event date moved earlier in later vintage) | **PASS_PIT_CLEAN** |
| `gap_contamination` | H3 (signal derivable from EPS at ann close) | **PIT_CONSERVATIVE** (see §3) |

**Bottom line:** `compute_pead_signals` is **PIT-honest on all bitemporal hazards (H1, H2)** when paired with a properly-maintained prefetch boundary. H3 is producer-conservative — stricter than the bitemporal model requires — and adds PIT safety, not removes it.

---

## 2. Method

The production-audit wrapper at [scripts/run_b702_production_audit_pead.py](scripts/run_b702_production_audit_pead.py) does the following per probe date:

1. Filters the bitemporal facts to as-known-at-as_of state (applies restatement ONLY if `restated_known_from <= as_of`).
2. Writes the resulting facts to a temp Polygon-style `<TICKER>.parquet` matching the schema [load_quarterly_eps](backtest/signals/pead.py#L75) reads.
3. Clears `load_quarterly_eps.cache_clear()` (functools.lru_cache).
4. Forces `close[T-1] = 100` and `close[T+1] = 105` around each announcement date so `ann_return = +5%` — this **isolates** PIT-correctness from the producer's `pead_positive_surprise = (yoy > 0 AND ann_return > 0.02)` definitional layer. Without this, all `pead_positive_surprise` probes fail because the auditor's random prices generate ann_return below the +2% threshold — a false PIT-bug signal.
5. Slices prices to `<= as_of` (mimics [backtest.py:824](backtest/engine/backtest.py#L824)).
6. Calls `compute_pead_signals(ticker, prices_sliced, as_of)`.
7. Maps producer output keys to auditor keys: `earnings_eps_yoy_growth` → `yoy_surprise`.

This wrapper is the simplest way to test the producer + cache as a system: if you write only as-known values to the cache, does the producer compute as-known outputs?

---

## 3. H3 PIT-conservative explanation

The auditor's H3 case expects `pead_positive_surprise=True` at `as_of=ann_date` — the hazard model is: a signal can fire on the announcement bar's close using only EPS knowable at announcement. Our producer responds `False` at `as_of=ann_date` because:

- `earnings_announcement_return = close[T+1] / close[T-1] - 1` (see [pead.py:249-253](backtest/signals/pead.py#L249))
- At `as_of=T`, the engine's pre-slice means `len(ohlcv_df) = T+1`, so the guard `pos + 1 < len(ohlcv_df)` returns False.
- `earnings_announcement_return` is not computed → `pead_positive_surprise` is not set.
- First fire-eligible bar is `as_of >= T+1`, at which point T+1's close is realized.

**This is producer-conservative behavior — stricter than the bitemporal model requires.** A signal that fires on T using EPS alone is theoretically valid under the auditor's reference definition (and would be PIT-honest). Our producer refuses to fire until T+1 to also use the announcement-day price reaction (`ann_return`) — a stronger, secondary confirmation. This adds PIT safety, not removes it.

**Interpretation:** the producer does not have an H3 lookahead bug; the auditor's H3 expectation models a different (more permissive) PEAD definition. Both are PIT-honest at the bar of fire; our producer is stricter.

---

## 4. Residual concerns NOT addressed by this audit

The audit tests the producer's algorithm. It does **not** test:

1. **Prefetch boundary integrity** — if Polygon's prefetch script overwrites a `filing_date` or replaces an EPS value with a restated one, the producer trusts the cache. The `S4-B702-EV-PREFETCH-IMMUTABILITY-AUDIT` ticket addresses this separately.
2. **Caller contract on slicing** — the producer's H3 conservatism + H1 PASS BOTH depend on the engine pre-slicing OHLCV to `<= as_of` ([backtest.py:824](backtest/engine/backtest.py#L824)). A future caller (notebook, sandbox, alt-engine) passing un-sliced OHLCV could violate this. The `S4-B702-EV-PHASE-0-PRODUCER-COMMENT-PIN` ticket adds an explicit docstring contract.
3. **`compute_yoy_surprise_signal`** ([earnings_surprise_yoy.py](backtest/signals/earnings_surprise_yoy.py)) — thin wrapper on top of `compute_pead_signals` that reads `earnings_eps_yoy_growth` and emits `yoy_surprise_high` / `yoy_surprise_negative` booleans. Inherits PEAD's PIT-correctness on the underlying field. Not separately audited.
4. **Real Polygon cache vendor-behavior** — the audit synthesizes bitemporal facts. Whether Polygon actually rewrites `filing_date` on re-pulls is a vendor-side question (`S4-B702-EV-PREFETCH-IMMUTABILITY-AUDIT`).

---

## 5. Impact on B660 re-run interpretation

When the AWS B660 re-run's PEAD numbers land (`b660_outputs/result_shard_*.json` → merged JSON), they can be interpreted as **PIT-trustable conditional on the prefetch boundary**, NOT PENDING-PIT. This unblocks PEAD strategy verdicts in Stage 5 cube empirical validation.

The prefetch-boundary caveat means: if `S4-B702-EV-PREFETCH-IMMUTABILITY-AUDIT` later shows Polygon overwrites filing_dates on re-pulls, PEAD numbers would need a second-pass audit. Until then, the producer-level audit is the strongest PIT-correctness verdict available pre-cube.

---

## 6. CHECKLIST compliance

Applied: #45 (per-recommendation pre-flight via validator gate), #67 (per-turn doc sync — this report + queue ticket resolution coming together), #69 (test pyramid — 2 new scripts + 1 wrapper, no existing-test regressions since added to scripts/ not backtest/), #77 (canonical source headers on all 3 new files), #94 (per-turn EXECUTION_QUEUE update with B702 ticket resolutions), #105 (Step-3 producer source-read informed the verdict interpretation).
