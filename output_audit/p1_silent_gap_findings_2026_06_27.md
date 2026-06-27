# P1 Silent-Gap Findings — Owner-Action Memo

# Source: B1033 wiring audit (4 parallel sub-agents W1+W2+W3+W4) + Council 128
# Option-6 verdict per owner directive 2026-06-27 "Address all bugs ... very
# comprehensive review and implement them. Council this. Checklist compliance
# is mandatory." per CHECKLIST #77.

## Purpose

Comprehensive wiring-audit surfaced 4 critical findings. Council 128 verdict
RECOMMENDED Option-6: fix clear bugs (F1 + F4) this turn; surface F2 + F3
strategy re-enable decisions to owner per `feedback_no_a_priori_strategy_
pruning` + `feedback_audit_recommendations_against_existing_directives`.
This memo captures all 4 findings + actions taken + owner-action items.

## Finding-1: B1010 concentrated_sell silent-gap (CLEAR BUG — FIXED B1034)

**Evidence** (W1 + W4 wiring audit):
- B1010 `strat_insider_cluster_concentrated_sell_short` (Council 103 owner-
  approved Class 7 NEW; screener.py:3482) consumes `s.get("concentrated_sell", False)`
- Producer: `smart_money.insider_signal()` (smart_money.py:519+) emits
  `concentrated_sell` key
- BUT: `smart_money.insider_signal()` was NEVER CALLED in `screen_instrument`
  path of screener.py
- Only `inject_insider_buying_signals` (via `insider_buying.compute_insider_
  cluster_signals`) was called — which emits `insider_cluster_active` +
  `insider_*_buyers_30d` family ONLY
- **Result**: B1010 strategy CANNOT FIRE in current code; `concentrated_sell`
  always defaults False; owner-approved strategy structurally inert

**Same-class silent-gap signals also affected** (not yet consumed by any
active strategy but produced by same producer):
- `cfo_buy`, `large_dollar_buy`, `ceo_buy`, `director_only_buy`, `cluster_buy`,
  `signal`, `buy_count`, `sell_count`

**Action taken THIS BATCH (B1034)**:
- Added `inject_insider_signal_keys()` to `backtest/data/signal_loader.py`
- Calls `smart_money.insider_signal(ticker, as_of)` per-(ticker, as_of) pure
- Injects all 9 keys into `signals` dict
- Added invocation in `screener.py:screen_instrument` alongside existing
  `inject_insider_buying_signals` call
- Smoke test: NVDA 2026-04-01 returns all 9 keys including `concentrated_sell`
- Pyramid: GREEN 848 + 2 skipped post-fix

**Status**: ✅ RESOLVED-IMPLEMENTED B1034

## Finding-2: naked_poc_retest_long wrong-disable (OWNER DECISION NEEDED)

**Evidence** (W1 + W4 confirm):
- `STRATEGIES_DISABLED_MISSING_PRODUCER` in `backtest/config.py:1099` lists
  `naked_poc_retest_long`
- Rationale (per B975 2026-06-21 + CLAUDE.md banner): "naked_poc_count +
  naked_poc_nearest_distance_pct producers never implemented in volume_
  profile.py"
- **ACTUAL state**: Both keys ARE emitted at `screener.py:8255-8259`
  via `compute_period_pocs` (volume_profile.py:152)
- Code:
  ```python
  period_pocs = compute_period_pocs(df, period_lookback=252, n_periods=6)
  if period_pocs:
      close = float(df["close"].iloc[-1])
      signals["naked_poc_count"] = len(period_pocs)
      if close > 0:
          signals["naked_poc_nearest_distance_pct"] = min(
              abs(close - p) / close for p in period_pocs
          )
  ```
- B975 rationale appears stale; producer DID land but possibly emits 0 in
  test windows that B975 sampled

**Owner-action options**:
- **Option-2a**: Re-enable `naked_poc_retest_long` (remove from STRATEGIES_
  DISABLED_MISSING_PRODUCER set); 217 → 218 active strategies; cube cells
  217 × 26 → 218 × 26
- **Option-2b**: Keep disabled + update CLAUDE.md banner with corrected
  rationale (e.g., "naked POC threshold tuning pending Stage 5 walk")
- **Option-2c**: Runtime probe AAPL 2024-06-30 → if `naked_poc_count > 0`
  populates → re-enable per Option-2a

**Council 128 recommendation**: Option-2c (runtime probe before re-enable;
defer to owner per `feedback_no_a_priori_strategy_pruning`)

**Status**: 🔴 OWNER DECISION

## Finding-3: m_and_a_target_long wrong-disable + contradiction (OWNER DECISION)

**Evidence** (W1 + W2 + W4 all surface):
- `STRATEGIES_DISABLED_MISSING_PRODUCER` in `backtest/config.py` lists
  `m_and_a_target_long`
- Rationale (per B984 2026-06-21 + CLAUDE.md banner): "8k_item_1_01_filed_
  within_30d producer never reliably implemented" + cites EV-7 buyback_8k_
  recent_long DELETED per CC-B 8-K population-mixing
- **ACTUAL state**: `8k_item_1_01_filed_within_30d` IS produced by
  `compute_sec_edgar_signals` (screener.py:8226 + sec_edgar_extractor.py:206)
- **CONTRADICTION**: `strat_m_and_a_target_long` docstring at screener.py:
  4799-4807 (B748d 2026-06-13) EXPLICITLY states "Producer + data work end-
  to-end" with **B748d 3/3 KNOWN events fire** evidence
- B984 Council 88 disabling appears to CONTRADICT B748d's own walk-back

**Owner-action options**:
- **Option-3a**: Re-enable per B748d evidence (3/3 KNOWN events fire); 217
  → 218 active
- **Option-3b**: Keep disabled + reconcile docstring to match config (update
  4799-4807 with B984 explanation)
- **Option-3c**: Investigate B984 rationale vs B748d evidence — possibly
  the disabling reason was DIFFERENT from "producer missing" (e.g., signal
  population-mixing concern); update docstring + config rationale

**Council 128 recommendation**: Option-3c (reconcile contradiction;
investigate why B984 disabled despite B748d evidence; defer re-enable
decision to owner)

**Status**: 🔴 OWNER DECISION + RECONCILIATION

## Finding-4: writer.py raw-signal counter (R5 BLOCKER per W4)

**Evidence** (W4 wiring audit):
- `backtest/results/writer.py` has no per-strategy raw-fire counter
- R4 cube only emitted `trade_log.csv` / `.parquet`
- Cannot distinguish "strategy never evaluated" from "all filtered"
- Precedent: `smc_breaker_block` had 16,631 fires/yr in B660-ext but 0
  trades in R4 cube — root cause undiagnosable without per-strategy raw
  signal counts

**Owner-action options**:
- **Option-4a**: Add `per_strategy_raw_signal_count` dict to writer output
  schema (~30 min code change; +1 column in strategy_regime_matrix.json)
- **Option-4b**: Defer to Phase D R5 — accept that some strategies' silent-
  skip will be hidden in cube (precedent: smc_breaker_block 0-trade mystery)
- **Option-4c**: Implement writer.py counter + new unit test

**Council 128 recommendation**: Option-4c BUT requires owner approval per
L86/L95 (any engine code change before R5 launch requires explicit owner
gate). Surface as owner-decision; do NOT auto-implement per
`feedback_audit_recommendations_against_existing_directives`.

**Status**: 🔴 OWNER DECISION (R5 BLOCKER claim from W4 should be owner-
adjudicated; alternative is documented forensic gap acceptable for R5)

## Summary table

| # | Finding | Status this turn | Owner action needed |
|---|---|---|---|
| F1 | B1010 concentrated_sell silent-gap | ✅ RESOLVED-IMPLEMENTED B1034 | None (auto-fixed) |
| F2 | naked_poc_retest_long wrong-disable | 🔴 Surfaced | Re-enable per Option-2c probe OR keep disabled with reconciled rationale |
| F3 | m_and_a_target_long wrong-disable + contradiction | 🔴 Surfaced | Reconcile B984 vs B748d; decide re-enable per Option-3c |
| F4 | writer.py raw-signal counter (R5 BLOCKER claim) | 🔴 Surfaced | Approve Option-4c engine change pre-R5 OR accept forensic gap |

## Recommendations sequence

1. Owner reviews this memo
2. Owner decides F2 + F3 (strategy re-enable OR reconciled rationale update)
3. Owner decides F4 (writer.py change pre-R5 OR defer)
4. Per F2/F3/F4 decisions, B1035+ executes accordingly
5. Phase C smoke + Phase D R5 launch proceeds per Council 127

## Cross-references

- B1010 (Council 103 owner-approved Class 7 NEW)
- B975 + B984 (owner-approved disable decisions; now revisited)
- B748d (m_and_a B748 walk evidence)
- Council 128 verdict (Option-6 fix-clear-bugs + memo)
- W1 + W4 wiring audits (B1033)
- `feedback_no_a_priori_strategy_pruning` (re-enable needs owner)
- `feedback_audit_recommendations_against_existing_directives` (B975/B984
  reversals need separate owner approval)
- L86/L95 cost discipline (engine changes pre-R5 need owner gate)
