# Vendored External Libraries

Per **DEC-045** (fork-first architecture; Pass 27 RESOLVED-DECIDED) + **DEC-508** + **CHECKLIST #71** (external library fork integration mandate Pass 53).

External libraries are forked into `vendored/` with pinned upstream commit hashes. They are NOT installed from PyPI directly — we use editable installs against this directory so the version is reproducibly locked.

## Forked libraries

### smartmoneyconcepts

| Field | Value |
|---|---|
| **Upstream URL** | https://github.com/joshyattridge/smartmoneyconcepts |
| **Upstream version (PyPI)** | 0.0.27 |
| **Pinned commit hash** | `1b62fd6c41e1f508e7ed76831a039fa4c82d42f6` |
| **Short hash** | `1b62fd6` |
| **Commit date** | 2026-04-03 |
| **Forked date** | 2026-05-05 (Pass 53 Sprint 0A Batch 15 kickoff) |
| **License** | MIT (see `vendored/smartmoneyconcepts/LICENSE`) |
| **Install** | `pip install -e vendored/smartmoneyconcepts` |
| **Phase A status** | IN PROGRESS — Tier 1 unit tests scaffolded; PIT regression scaffolded; ~10/100 tests written |
| **Phase B status** | NOT STARTED — pending Phase A completion + Dashboard 2 (DEC-200) |
| **Phase C status** | NOT STARTED — pending Phase B completion |

**API surface (smc class methods):**
- `fvg(ohlc, join_consecutive=False)` — Fair Value Gap detection
- `swing_highs_lows(ohlc, swing_length=50)` — Swing high/low identification (precursor to BOS/CHoCH)
- `bos_choch(...)` — Break of Structure / Change of Character
- `ob(...)` — Order Block
- `liquidity(ohlc, swing_highs_lows, range_percent=0.01)`
- `previous_high_low(ohlc, time_frame='1D')`
- `sessions(...)`
- `retracements(ohlc, swing_highs_lows)`

**Phase A test files:**
- `backtest/tests/test_smartmoneyconcepts_unit.py` — Tier 1 unit tests (synthetic OHLCV)
- `backtest/tests/test_smartmoneyconcepts_pit.py` — Tier 1 PIT correctness regression (freezegun)
- `backtest/tests/test_smartmoneyconcepts_integration.py` — Tier 2 integration (PENDING)
- `backtest/tests/test_smartmoneyconcepts_performance.py` — Tier 2 performance (PENDING)
- `backtest/tests/test_smartmoneyconcepts_statistical.py` — Tier 3 statistical sanity (PENDING)
- `backtest/tests/test_smartmoneyconcepts_adversarial.py` — Tier 3 adversarial random walk (PENDING)
- `backtest/tests/test_smartmoneyconcepts_xvalidation.py` — Tier 3 cross-validation (PENDING)

**Build sequence (Phase A → B → C per DEC-508 + CHECKLIST #71):**
1. Phase A — All Tier 1 + 2 + 3 tests pass; ≥90% coverage; library NOT imported outside test files; owner approval → Phase B
2. Phase B — Library imported; signals computed for full universe → `data_prefetch/ict_smc/{ticker}.parquet` but strategies disabled; Dashboard 2 (DEC-200) launched; owner validates 20-50 signals; PIT regression on full universe; owner approval → Phase C
3. Phase C — Strategies enabled; A/B vs baseline; DEC-084 lookahead red-flag check; walk-forward per DEC-505 (4 OOS folds × 1y)

**Reproducibility:**
To reproduce the exact library state at fork point:
```bash
cd vendored/smartmoneyconcepts
git checkout 1b62fd6c41e1f508e7ed76831a039fa4c82d42f6
```

If upstream commits made AFTER our pinned hash become relevant, owner approval required to update pin (re-running Phase A tests against new commit hash).

**License compliance:**
MIT licensed. Source attribution preserved in `vendored/smartmoneyconcepts/LICENSE`. Our project is fork-first per DEC-045; the fork is a TOOL we depend on, not a dependency we redistribute.
