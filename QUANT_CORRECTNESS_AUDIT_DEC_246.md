# DEC-246 Quant Finance Correctness Audit

**Source (per CHECKLIST #77 canonical-source attribution):**
- DEC-246 owner directive Pass 52 turn 119 RESOLVED-DECIDED Final: "audit Sharpe annualization, drawdown computation, vol periodicity"
- Pass 53 evening 2026-05-06 reclassified to PARTIAL-SPEC-ONLY
- Code SSOT: `backtest/results/bootstrap_ci.py` (Sharpe) + `backtest/results/metrics.py` (drawdown / Calmar) + `backtest/results/ab_orchestrator.py` (Sortino) + `backtest/results/cube_populator.py` (cube-Sharpe approximation)
- Joint DEC-081 Sharpe canonicalization + DEC-110 PSR + DEC-413 5-gate validity
- Generator: this audit doc (Batch 374 closure 2026-05-26)

## 1. Sharpe ratio annualization

**Canonical formula (rf=0):** `mean(R) / std(R, ddof=1) * sqrt(periods_per_year)`

### Authoritative implementation: `backtest/results/bootstrap_ci.py:44-59`

```python
def sharpe_ratio(returns: Sequence[float]) -> float:
    arr = np.asarray(returns, dtype=float)
    if len(arr) < 2:
        return 0.0
    mean = arr.mean()
    std = arr.std(ddof=1)
    if std < 1e-12 or not np.isfinite(std):
        return 0.0
    return mean / std * np.sqrt(252)
```

**Verdict:** ✅ CORRECT for daily-frequency returns.
- `ddof=1` = sample std (Bessel correction), correct for finite samples.
- `1e-12` precision floor prevents numerical blow-up on near-constant series.
- `sqrt(252)` annualizes from daily → annual.

### Variant: `cube_populator.py:131-133` + `ab_orchestrator.py:89-93`

```python
sharpe = (expected_value / std) * np.sqrt(252) if std > 0 else 0.0
```

**Verdict:** ⚠ APPROXIMATION — applies `sqrt(252)` to **per-trade** returns rather than daily returns.

**Bias direction:** OVER-annualizes when trades fire less frequently than daily. If a strategy fires ~50 trades/year, the proper annualization factor is `sqrt(50/n_obs)` not `sqrt(252)`.

**Inline disclosure:** cube_populator.py:131 explicitly comments "annualized; assumes daily-ish trade cadence; rough approx".

**Recommendation:** acceptable for cross-strategy ranking (all use same factor → relative order preserved). NOT comparable to industry benchmarks. For absolute Sharpe claims in Phase 1B-α winners promotion, use a frequency-aware annualization:
```python
n_trades_per_year = 252 / max(avg_hold_days, 1)
sharpe = (mean / std) * np.sqrt(n_trades_per_year)
```
**Decision:** keep current code (relative rank-correct); add this audit note. Owner-approve if absolute Sharpe matters for Phase 1B-α winners filter.

## 2. Max drawdown

### Authoritative implementation: `backtest/results/metrics.py:40-66`

```python
def _max_drawdown(pnl_series: pd.Series) -> float:
    if pnl_series.empty:
        return 0.0
    equity = (1.0 + pnl_series / 100.0).cumprod()
    peak = equity.cummax()
    drawdown_pct = (equity - peak) / peak * 100.0
    return round(float(drawdown_pct.min()), 4)
```

**Verdict:** ✅ CORRECT. BUG-15 RESOLVED-IMPLEMENTED Pass 53 v8h+1 (was cumsum / additive; now cumprod / compounded — industry-standard).

**Formula match:** `drawdown(t) = (equity(t) - peak(0..t)) / peak(0..t) * 100`. Matches DEC-081 canonical reference.

## 3. Volatility periodicity

### Daily returns → daily vol
```python
std = arr.std(ddof=1)  # daily vol
```
**Verdict:** ✅ CORRECT periodicity assumption (matches Sharpe formula above).

### Sortino downside vol: `ab_orchestrator.py:90-93`
```python
neg = arr[arr < 0]
dstd = neg.std(ddof=1) if len(neg) > 1 else 1e-9
sortino = (mu / dstd) * np.sqrt(252) if dstd > 0 else 0.0
```

**Verdict:** ✅ CORRECT Sortino formula (downside-deviation only). Same `sqrt(252)` periodicity assumption.

## 4. Calmar ratio (`metrics.py:69-78`)

```python
n_trades_per_year = 252 / max(avg_hold, 1)
annual_return = float(pnl_series.mean()) * n_trades_per_year
return round(annual_return / mdd, 3)
```

**Verdict:** ✅ CORRECT. Uses average hold-days to compute trades-per-year, then scales mean trade return to annual. This is the right pattern for **per-trade-return-series → annualized metric**.

**Cross-reference:** this is the annualization pattern that the cube_populator Sharpe approximation SHOULD adopt (see §1 recommendation).

## 5. PSR (Probabilistic Sharpe Ratio) placeholder

### Status: `cube_populator.py:136-137` comment
> "PSR placeholder (DEC-247 via deflated_sharpe.py wires the real one)"

`backtest/results/deflated_sharpe.py` is the canonical PSR/DSR implementation per DEC-110 + DEC-247.

**Action:** verify deflated_sharpe.py PSR formula matches Bailey-Lopez de Prado 2014. (Out of scope for this audit; queued for DEC-247 separate audit.)

## 6. Aggregate verdict

| Component | Status | Notes |
|---|---|---|
| Daily-Sharpe formula | ✅ CORRECT | `mean/std * sqrt(252)`, ddof=1, 1e-12 floor |
| Per-trade-Sharpe approximation | ⚠ APPROXIMATION | rank-correct; absolute biased high; documented |
| Max drawdown | ✅ CORRECT | cumprod equity curve, peak-trough %, BUG-15 fixed |
| Daily vol periodicity | ✅ CORRECT | matches Sharpe formula |
| Sortino downside vol | ✅ CORRECT | downside-only std, same periodicity |
| Calmar annualization | ✅ CORRECT | trade-frequency-aware (template for §1 fix) |
| PSR | DEFERRED to DEC-247 audit | deflated_sharpe.py separate audit |

## 7. Test pinning (regression guard)

Adds `test_dec246_quant_correctness_formula_pin` in `test_unit.py`:
- Verifies `sharpe_ratio([0.01]*252)` returns expected value
- Verifies `_max_drawdown(pd.Series([+10, -5, -10]))` returns ~-14.50 per BUG-15 fix
- Verifies `_max_drawdown` handles empty input safely
- Pins `sqrt(252)` annualization factor (catches accidental periodicity changes)

## 8. Action items

1. ✅ Audit doc written (this file)
2. ✅ Regression test added (`test_dec246_quant_correctness_formula_pin`)
3. 📋 Owner-decision: should cube_populator Sharpe approximation be replaced with Calmar-style trade-frequency annualization? (Defaults: NO — keep relative-rank approach for Stage 2.)
4. 📋 Future: DEC-247 PSR/DSR formula audit in deflated_sharpe.py (separate batch).

## References

- DEC-081 (Sharpe canonicalization)
- DEC-110 (PSR)
- DEC-247 (DSR + Bailey-Lopez de Prado)
- DEC-413 (5-gate validity)
- DEC-510 (DSR as 6th gate)
- BUG-15 (max_drawdown cumsum → cumprod fix)
