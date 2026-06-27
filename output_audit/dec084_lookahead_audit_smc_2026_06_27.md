# DEC-084 Lookahead Audit - SMC Strategy Family

# Source: Council 132 Sub-agent #6 + scripts/smc_pit_audit.py (B735) per CHECKLIST #77.
# C-1 declaration Section 4 PENDING lookahead red-flag check.

**Council 132 Sub-agent #6** | 2026-06-27 | C-1 Phase C Item Section 4

## Scope

DEC-084 red-flag lookahead check on 18 SMC strategies + `event_recency_bars=90` + `dealing_range_lookback=50` parameters + Pattern K (B262 forensic) dealing-range PIT lookahead concern.

## Method

1. Read `backtest/signals/smc_ict.py` `compute_smc_signals` (433 lines)
2. Read `backtest/signals/smc_panel_cache.py` (182 lines) - primitive cache + PIT-slicing contract
3. Read all 18 SMC strategy bodies (`screener.py:3904-4250`)
4. Traced engine call-path: `backtest.py:819-826 ohlcv_pit slice` -> `screener.py:8608 screen_instrument(df_pit)` -> `screener.py:8099 compute_smc_signals(df)`
5. Ran `scripts/smc_pit_audit.py` (B735 H1/H2/H3 hazard probes) against live producer with `SMC_PHASE=PRODUCTION`

## Audit Results (3 hazards x producer)

| Hazard | Verdict | Evidence |
|---|---|---|
| **H1 SWING-FORMATION CONFIRMATION LAG** | FAIL_PEEKED_FUTURE_BARS (probe-as-truth gap, not peeking - see note) | At swing+k bars, harness expected `swing_high_confirmed=True`; producer returned False both PIT and FULL -> producer is *conservative* (under-fires) not peeking. NOT A LOOKAHEAD violation. |
| **H2 DEALING-RANGE EXTREMA RE-ANCHOR (Pattern K / B262)** | **FAIL_PEEKED_FUTURE_BARS - CONFIRMED HAZARD** | At as_of=2024-03-19, PIT=108.0 [OK], FULL=115.0 ❌. PIT-vs-FULL **disagree** -> producer's `dealing_range_high` is non-causal when called with full series. |
| **H3 PANEL-CACHE EDGE CONTAMINATION** | PASS_PIT_CLEAN | as_of-stability probe at swing-1: PIT and FULL agree (both False). No edge leak detected. |

## Engine Call-Path Verification

| Boundary | Slicing | PIT-safe? |
|---|---|---|
| `backtest.py:819` `ohlcv_pit = df[df.index.date <= as_of]` | Sliced | [OK] |
| `screener.py:1062` `screen_universe(ohlcv_pit, ...)` | Sliced received | [OK] |
| `screener.py:8608` sequential `screen_instrument(ticker, df, ...)` | df IS ohlcv_pit's value (sliced) | [OK] |
| `screener.py:8099` `compute_smc_signals(df, ticker=ticker)` | df is PIT-sliced | [OK] |
| `smc_panel_cache.get_primitives_at` | swing-dependent: `iloc[:current_idx - swing_length + 1]` | [OK] (per B554 contract) |
| **H2 hazard reachability in production** | **Engine PIT-slices before producer call -> H2's "FULL mode" is NOT a production code-path** | **MITIGATED-BY-ENGINE-BOUNDARY** |

**Conclusion: the H2 FAIL is a producer-internal latent hazard, not an active runtime lookahead.** Engine slicing at `_process_day` masks it. BUT: if anyone calls `compute_smc_signals(full_df)` outside the engine (e.g., dashboard, ad-hoc notebook, smoke test, parallel worker via `_pool_init` if df not pre-sliced), they will get **non-causal** dealing_range_high values.

## Per-Strategy Verdict (18 SMC strategies)

All 18 strategies (`strat_smc_fvg_retest_long/short`, `inverse_fvg`, `breaker_block_long/short`, `mitigation_block_long/short`, `discount_long`, `premium_short`, `ote_long/short`, `equal_highs_sweep_short`, `equal_lows_sweep_long`, `bos_retest_entry`, `bos_continuation`, `choch_reversal`, `order_block_bounce`, `liquidity_sweep_reversal`) consume **only** boolean / scalar signals emitted by `compute_smc_signals`. No strategy reads `ohlc` directly; no strategy re-derives swings. Therefore PIT-safety = `compute_smc_signals` PIT-safety.

| Strategy group (count) | Signals consumed | PIT verdict (in production engine call-path) |
|---|---|---|
| FVG family (3): retest_long/short, inverse_fvg | `smc_fvg_*`, `smc_inverse_fvg_*` | **PASS** (FVG primitive has 1-bar lookahead masked by cache `iloc[:current_idx]`) |
| OB / breaker / mitigation (5) | `smc_ob_*`, `smc_breaker_block_*`, `smc_mitigation_block_*` | **PASS** (swing-dependent; cache masks `swing_length=20` bars) |
| Discount/Premium (2) + OTE (2) | `smc_in_*_zone`, `smc_dealing_range_pct`, `smc_ote_*_zone` | **FLAG-CONDITIONAL** (Pattern K H2 latent; production-safe per engine boundary) |
| BOS / CHoCH (3) + Liquidity sweep (3) | `smc_bos_*`, `smc_choch_*`, `smc_liquidity_*`, `smc_equal_*_swept`, `smc_bos_retest_*` | **PASS** (event_recency_bars=90 reads HISTORICAL events within `ohlc.tail(N)`-equivalent; past-only by construction since `ohlc` is already sliced) |

## Findings

1. **H2 Pattern K hazard confirmed in isolation but production-safe.** `dealing_range_high` re-anchors when later more-extreme bars exist. Mitigated by engine PIT-slicing. **Remediation ticket (RECOMMEND-DO-NOT-AUTO-FIX per L86/L95):** `S5-SMC-DEALING-RANGE-PRODUCER-HARDEN` - make `compute_smc_signals` defensive: clamp `ohlc` to `ohlc.iloc[:as_of_idx+1]` even if caller passes full df. Surface in EXECUTION_QUEUE for owner approval.

2. **`event_recency_bars=90` is PIT-safe.** `_most_recent_event_within` reads `series[series != 0].iloc[-1]` on the sliced df - all events are by construction at indices <= `current_idx`. No future leak.

3. **`dealing_range_lookback=50` is PIT-safe in production.** `window = ohlc.tail(50)` of a sliced df = last 50 PAST bars. The H2 hazard fires only when `ohlc` is full-series.

4. **B262 forensic (-1659pp IFVG contribution) was NOT a lookahead - it was a missing-confluence-gates issue** already remediated B262 by adding 200-EMA + vol_spike/force_index_cross_up gates. Confirmed via `strat_smc_inverse_fvg` body (lines 3931-3971).

5. **Latent risk: `_pool_init` workers (`screener.py:8503-8505`) re-slice per-call.** Sequential and parallel paths both slice before `screen_instrument`. No drift.

6. **Recommendation:** add a docstring caveat to `compute_smc_signals` that callers MUST pre-slice ohlc to `as_of` (currently implicit via engine convention); add unit test in `test_unit.py` asserting H2 PIT-vs-FULL stability after the producer harden.

## Conclusion

**18/18 SMC strategies PIT-CLEAN in current engine call-path.** Pattern K H2 latent producer hazard surfaced but blocked by engine boundary. Two remediation tickets recommended (DO NOT auto-fix per owner directive):
- `S5-SMC-DEALING-RANGE-PRODUCER-HARDEN` (clamp ohlc inside producer)
- `S5-SMC-PIT-UNIT-TEST` (assert H2 PIT/FULL stability in test_unit.py)

Council 132 Sub-agent #6 complete.
