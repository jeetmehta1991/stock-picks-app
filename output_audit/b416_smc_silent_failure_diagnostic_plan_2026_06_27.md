# B416 SMC Silent-Failure Root-Cause Diagnostic Plan (2026-06-27)

**Finding:** 0 of 29,159 trades carried `smc_*` keys in the R4 AWS cube, despite 18 wired SMC strategies + producer + signal-merge call at `screener.py:8091-8111`.

**Diagnostic mechanism:** B901 `EMIT_RAW_SIGNAL_FIRES=1` per-strategy raw-fire counter (`screener.py:55-86, 8385-8393`) + B416 silent-producer empty/failure loggers (`screener.py:91-129`) + B458 `log_silent_failure("smc_ict.import_smartmoneyconcepts")` (`smc_ict.py:46`).

## Seven Hypotheses + Diagnostic Queries

| # | Hypothesis | Diagnostic query (Phase C smoke) | Discriminating signature |
|---|---|---|---|
| H1 | Vendored library import fails in AWS env (path / Cython / numpy ABI) | grep AWS worker logs for `smc_ict.import_smartmoneyconcepts` via `silent_failure_logger`; check `vendored/smartmoneyconcepts/` packaged in lambda zip | `_SMC_AVAILABLE=False` -> `compute_smc_signals` returns `{}` immediately (line 117); 18 SMC strategies absent from `raw_signal_fires.<pid>.csv` |
| H2 | Library imports but raises on per-call (insufficient history / dtype) | grep logs for `Batch 416 silent-producer failure ... producer=smc_ict` (`_log_silent_producer_failure`, line 8111) | exception logged; raw-fires empty for SMC; `_log_silent_producer_empty` NOT logged |
| H3 | Producer returns empty dict silently (guard at line 117/120/122 trips) | grep logs for `Batch 416 silent-producer empty-return ... producer=smc_ict.compute_smc_signals` (line 8109) | empty-return logged; raw-fires empty for SMC; likely cause = `len(ohlc) < max(swing_length*2, 100)` window short OR missing OHLC column |
| H4 | Signals computed + present, but every SMC strategy gate fails (logic bug or always-False signal) | Inspect `raw_signal_fires.<pid>.csv` for the 18 `strat_smc_*` rows; cross-check signal dict in a Phase C debug dump | raw-fires = 0 for SMC strategies AND no empty/failure log = signal present but gates never align |
| H5 | Raw-fires > 0 but downstream filter strips trades (close_above_open, regime, MAX_CANDIDATES_PER_DAY, look-ahead audit) | Diff `raw_signal_fires.<pid>.csv` vs `trade_log` smc_* counts; check `direction` + candle color at fire bar | raw > 0, trade_log smc_* = 0; filter is in `screener.py:8401-8419` block |
| H6 | `STRATEGY_REGIME_AFFINITY` excludes SMC strategies from all 4 regimes evaluated | Grep `STRATEGY_REGIME_AFFINITY` for `strat_smc_*` entries; cross-check regime distribution in smoke window | SMC names listed only under regimes absent from smoke date range |
| H7 | Cube cell config-override (Phase B canary / `PHASE_1B_ALPHA_DISABLED_STRATEGIES` / `STRATEGIES_DISABLED_MISSING_PRODUCER`) suppresses SMC at registration | Grep `_DEPRECATED` + `_MISSING_PRODUCER` + any canary flag for `strat_smc_*`; verify SMC names appear in `ALL_STRATEGIES` at AWS-worker startup | SMC names absent from `ALL_STRATEGIES` enumeration log |

## Decision Tree

```
Phase C smoke run with EMIT_RAW_SIGNAL_FIRES=1 + WARNING-level logs:

  Step 1: SMC names in ALL_STRATEGIES enumeration?
    NO  -> H7 (registration suppression). Fix: remove from disabled set.
    YES -> Step 2.

  Step 2: smc_ict.import_smartmoneyconcepts failure logged?
    YES -> H1 (AWS import). Fix: package vendored/ in deploy artifact;
           pin numpy ABI; verify Cython build.
    NO  -> Step 3.

  Step 3: Batch 416 silent-producer failure (smc_ict) logged?
    YES -> H2 (per-call exception). Fix: read exception_type from log;
           harden producer for dtype/shape edge case.
    NO  -> Step 4.

  Step 4: Batch 416 silent-producer empty-return (smc_ict) logged?
    YES -> H3 (guard trip). Fix: inspect ohlc len/columns at first
           empty-return; likely insufficient-history floor.
    NO  -> Step 5.

  Step 5: raw_signal_fires.csv has strat_smc_* rows with count > 0?
    NO  -> H4 (signal present, gates never align) OR H6 (regime affinity).
           Fix: dump signals dict for one fire-bar; verify gates +
           cross-check STRATEGY_REGIME_AFFINITY membership.
    YES -> H5 (downstream filter). Fix: diff raw-fires vs trade_log;
           identify which filter (close_above_open most likely for SMC).
```

## Recommended Fix Per Most-Likely Cause

**Most-likely (Council prior):** H1 (vendored library not packaged) or H3 (insufficient history floor of `max(swing_length*2, 100) = 100` bars).

- H1 fix: add `vendored/smartmoneyconcepts/` to AWS deploy manifest; add `import smc` smoke test at worker init that fails-fast (not silent).
- H3 fix: log first-empty `len(ohlc)` value to confirm; if floor too aggressive for AWS cube date window, lower to 60 with explicit empirical justification.

**Pre-flight sweep before Phase C:** verify `EMIT_RAW_SIGNAL_FIRES=1` in AWS bootstrap + log-level WARNING captured to CloudWatch + raw-fires sidecar reaches merge step.
