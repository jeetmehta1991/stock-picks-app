# B771 PATTERN T MA-CROSS ANALYTICAL COLLINEARITY AUDIT (Cluster B B-1 to B-5) -- VERDICT

# per CHECKLIST #77 + #44(b) + #69 + #94 + #105 + #106 + #107
# Source: B769 council TIER 1 ticket S4-B769-COUNCIL-CLUSTER-B-PATTERN-T-MA-CROSS-ANALYTICAL-COLLINEARITY-AUDIT-DETERMINISTIC
# Source: backtest/signals/screener.py (strat_golden_cross_9_21 / _20_50 / _50_200 / _volume / death_cross_50_200_volume)
# Source: backtest/signals/technical.py:651-674 (compute_ema_sma producer)
# per memory: feedback_no_a_priori_strategy_pruning.md + feedback_local_changes_default_global_needs_approval.md

## B769 council TIER 1 question

> "Run analytical (not empirical) producer-source audit on Cluster B MA-cross strategies (B-1 golden_cross_9_21 + B-2 golden_cross_20_50 + B-3 golden_cross_50_200 + B-4 golden_cross_volume + B-5 death_cross_50_200_volume). If golden_cross_50_200 fires, price is near-definitionally above 200-EMA -- so price_above_ema_200 confirmation gate adds ~0 marginal info. Flag dead-weight confirmation gates pre-cube. Per chairman + Reviewer 4 caveat: producer edge cases (NaN handling, lookback init, gap-up) mean 'implied within ~1 bar' is not 100% -- audit must report exceptions."

## VERDICT: NO DEAD-WEIGHT CONFIRMATION GATES IN CLUSTER B MA-CROSS FAMILY

**0 HIGH-collinearity / 2 MEDIUM / 3 CLEAN out of 5 strategies.** Council's claim that "several confirmation gates can be flagged dead weight pre-cube" is **REFUTED for Cluster B MA-cross** -- no removable gates surfaced.

The council's general PRINCIPLE (Pattern T HIGH-collinearity = dead gate) remains correct. The specific Cluster B MA-cross APPLICATION did not find any HIGH-collinearity instances. The canonical example the council cited (golden_cross_50_200 + price_above_ema_200) does NOT exist as written -- B-3 canonical golden_cross_50_200 has NO trend confirmation gate. B-2 has price_above_ema_200 but the CROSS is at a different timescale (ema_20_50, not ema_50_200), so the gate adds genuine information.

## Per-strategy verdict

### B-1 strat_golden_cross_9_21 -- MEDIUM collinearity

```python
fl = (s.get("ema_9_21_golden_cross") and s.get("price_above_sma_50"))
fs = (s.get("ema_9_21_death_cross") and s.get("below_sma_50")) and not _short_borrow_trap_active(s)
```

- Cross signal: `ema_9_21_golden_cross` (fast 9/21 timescale)
- Trend gate: `price_above_sma_50` / `below_sma_50` (medium 50 timescale)
- Collinearity analysis: cross at 9/21 can fire BEFORE price recovers above SMA-50 (early-trend signal precedes confirmation). Mathematical proof of non-determinism: in a deep drawdown recovery, EMA_9 can cross EMA_21 (early swing-trade signal) while price is still below SMA_50 (long-term recovery incomplete). Gate filters these early-recovery false starts.
- **VERDICT: MEDIUM** -- gate adds genuine information; not dead weight.

### B-2 strat_golden_cross_20_50 -- MEDIUM collinearity

```python
fl = (s.get("ema_20_50_golden_cross") and s.get("price_above_ema_200"))
fs = (s.get("ema_20_50_death_cross") and s.get("below_ema_200")) and not _short_borrow_trap_active(s)
```

- Cross signal: `ema_20_50_golden_cross` (medium 20/50 timescale)
- Trend gate: `price_above_ema_200` / `below_ema_200` (long 200 timescale)
- Collinearity analysis: cross at 20/50 can fire BEFORE price gets back above EMA_200 (mid-recovery). The 20/50 cross is a medium-term swing signal; EMA_200 is the long-term regime. These are at different timescales -- mathematically possible for cross to fire when price is still below EMA_200.
- **VERDICT: MEDIUM** -- gate adds genuine information; trend-context filter.

### B-3 strat_golden_cross_50_200 -- CLEAN (no trend gate)

```python
fl = s.get("ema_50_200_golden_cross")
fs = s.get("ema_50_200_death_cross") and not _short_borrow_trap_active(s)
```

- Cross signal: `ema_50_200_golden_cross` (long 50/200 timescale)
- Trend gate: NONE (only the cross + borrow gate on SHORT side)
- Collinearity analysis: this is the SIMPLEST gate-stack in Cluster B. Council's canonical example "golden_cross_50_200 + price_above_ema_200 confirmation = dead weight" does NOT exist in code -- there is no such gate on this strategy. Council's claim was hypothetical-as-written.
- **VERDICT: CLEAN** -- no Pattern T issue; no removable gate to flag.

### B-4 strat_golden_cross_volume -- CLEAN (orthogonal volume gate)

```python
fl = (s.get("ema_50_200_golden_cross") and s.get("vol_spike_2x"))
fs = (s.get("ema_50_200_death_cross") and s.get("vol_spike_2x")) and not _short_borrow_trap_active(s)
```

- Cross signal: `ema_50_200_golden_cross` (long timescale)
- Confirmation gate: `vol_spike_2x` (VOLUME DIMENSION, orthogonal to trend)
- Collinearity analysis: volume is a fundamentally DIFFERENT axis from trend. Volume spike cannot be deterministically implied by EMA cross. Gate is in a different dimension entirely.
- **VERDICT: CLEAN** -- orthogonal confluence (price-trend + volume), not collinear confirmation.

### B-5 strat_death_cross_50_200_volume -- CLEAN (orthogonal volume gate)

```python
fires = (s.get("ema_50_200_death_cross") and s.get("vol_spike_2x")) and not _short_borrow_trap_active(s)
```

- Same as B-4 SHORT side; orthogonal volume + cross.
- **VERDICT: CLEAN** -- no Pattern T issue.

## Summary table

| Strategy | Cross | Trend gate | Verdict | Reasoning |
|---|---|---|---|---|
| B-1 golden_cross_9_21 | ema_9_21 (fast) | price_above_sma_50 (medium) | **MEDIUM** | Different timescales; gate adds confirmation info |
| B-2 golden_cross_20_50 | ema_20_50 (medium) | price_above_ema_200 (long) | **MEDIUM** | Different timescales; gate is long-term regime filter |
| B-3 golden_cross_50_200 | ema_50_200 (long) | NONE | **CLEAN** | No confirmation gate; canonical simplest stack |
| B-4 golden_cross_volume | ema_50_200 (long) | vol_spike_2x (volume) | **CLEAN** | Orthogonal axis; not collinear |
| B-5 death_cross_50_200_volume | ema_50_200 (long) | vol_spike_2x (volume) | **CLEAN** | Orthogonal axis; not collinear |

**0 HIGH / 2 MEDIUM / 3 CLEAN.** Same finding as B763 grep audit (which found 0 HIGH + 6 MEDIUM cluster-wide across 221 strategies).

## Reviewer 4 caveat checked (producer edge-case audit)

Producer source `backtest/signals/technical.py:651-674` (compute_ema_sma):

```python
def compute_ema_sma(df: pd.DataFrame) -> dict:
    result = {}
    for fast, slow in [(9,21),(20,50),(50,200)]:
        if len(df) < slow + 2:
            continue
        ef  = df["close"].ewm(span=fast, adjust=False).mean()
        es  = df["close"].ewm(span=slow, adjust=False).mean()
        ...
        result[f"ema_{fast}_{slow}_golden_cross"] = efv > esv and efp <= esp
        result[f"ema_{fast}_{slow}_death_cross"]  = efv < esv and efp >= esp
        ...
```

Edge-case audit per Reviewer 4:

1. **NaN handling:** `_safe_float()` wraps each .iloc read -- returns 0.0 on NaN/missing. Could cause false negatives (golden cross missed) but not false positives. **NOT a contamination path.**
2. **Lookback initialization:** `if len(df) < slow + 2: continue` -- requires slow+2 bars (52 bars for 50/200 cross). Below threshold, signal not emitted at all. **NOT a contamination path** -- safe-fail to no-signal.
3. **Gap-up open:** EMA computed on `close`, not `open`. A gap-up on the cross bar doesn't affect whether `efv > esv` (today's EMA values are based on accumulated closes). **Not a contamination concern at signal-level.**
4. **Cross-bar definition:** `efp <= esp` uses yesterday's <=; tied EMAs yesterday + crossed today = fires. Edge case: if yesterday EMA_50 == EMA_200 exactly (rare), the cross still fires. **Conservative; not a contamination path.**

**Edge-case audit verdict: producer is robust to all 4 edge cases. No contamination paths.**

## Validation against existing B763 grep audit

B763 `scripts/pattern_t_family_grep_audit.py` ran on all 221 strategies (SHIPPED 2026-06-15) and found:
- 0 PATTERN_T_HIGH
- 6 PATTERN_T_MEDIUM (including golden_cross_20_50, golden_cross_9_21, awesome_oscillator, force_index_breakout, stoch_oversold, stochrsi_oversold)

B771 deterministic per-strategy audit on Cluster B confirms B763's verdict at finer granularity: B-1 + B-2 are MEDIUM (confirmed in B763); B-3 + B-4 + B-5 are CLEAN (no MA-cross + same-window trend-gate). Convergent finding.

## Council's claim REFUTED for Cluster B (general principle holds)

Council asserted: "the collinearity is analyzable now from the producer logic (it's a near-deterministic relationship, not an empirical question requiring measurement)... several of these confirmation gates can be flagged as dead weight before the cube ever runs."

**For Cluster B specifically:** 0 dead-weight gates surfaced. Council's specific concrete example (golden_cross_50_200 + price_above_ema_200) does NOT exist in code as written. The canonical B-3 has NO confirmation gate; B-2 has price_above_ema_200 but the CROSS is at a different timescale (20/50, not 50/200), so the gate is at a genuinely different scale and adds information.

**General principle stands:** if a strategy DID have golden_cross_X_Y + price_above_ema_Y at matching timescales, that would be HIGH-collinearity dead weight by transitivity (X cross Y implies X > Y at fire bar; if close > X is also gated, then close > Y is near-implied). The B-1/B-2 MEDIUM cases have NON-matching timescales and so retain information.

Per First Principles advisor + Reviewer 2: "pure-logic, deterministic, low-cost to verify from producer source." VERIFIED: deterministic verdict requires no cube run.

## Follow-up tickets surfaced

**NONE.** No dead-weight gates surfaced. No removal actions required. 

The verdict UNBLOCKS downstream decision on B-1 + B-2: keep gates as-is (MEDIUM collinearity, gate-information confirmed). No need to wait for cube to validate gate-removal hypothesis.

## CHECKLIST #107 reconciliation (B771)

- **Findings surfaced:** 1 primary (5-strategy collinearity verdict: 0 HIGH / 2 MEDIUM / 3 CLEAN -- council's pre-cube-dead-weight claim REFUTED for Cluster B MA-cross)
- **Tickets filed:** 0 NEW + 1 annotation (existing #52 COMPLETED-EMPIRICAL with verdict)
- **Audit-clean: YES**

Cumulative ticket count post-B771: 129 unique S4-B7XX tickets (no change; #52 closed not added).

## Strategy counts (unchanged)

221 ALL_STRATEGIES / 0 DEPRECATED / 1 STRATEGIES_DISABLED_MISSING_PRODUCER / **220 active.** No strategies modified.

## Memory + checklist compliance

- `feedback_no_a_priori_strategy_pruning.md` -- no strategies modified; analytical verdict only
- `feedback_local_changes_default_global_needs_approval.md` -- per-strategy analysis; no global changes
- CHECKLIST #44(b) -- producer source + 4-edge-case audit applied
- CHECKLIST #67 -- doc-sync same turn
- CHECKLIST #69 -- pyramid mandatory (842/842 unchanged; no code changes)
- CHECKLIST #77 -- canonical-source header
- CHECKLIST #94 -- queue-mandatory-per-turn (annotation on #52)
- CHECKLIST #105 -- producer source read end-to-end
- CHECKLIST #106 -- producer-data audit precedent
- CHECKLIST #107 -- findings-vs-tickets reconciliation (sixth batch using new discipline)
