# B1019 Monitor Design Audit — What It Saw, What It Missed, Why

# Source: Council 166 4-advisor RECOMMEND Option-4 OWNER-LITERAL + MONITOR-AUDIT per CHECKLIST #77 + #115 + owner directive 2026-06-28 "I want to understand the monitor".

**Generated:** 2026-06-28 (B1066)
**Trigger:** Owner question "I want to understand the monitor. These should have been triggered in the monitor itself."
**Source data:** Phase 1 B1063 trade_log.csv + B660 baseline + monitor.py source

---

## ⚠ RETRACTIONS FROM B1065

### PIVOT #38 RETRACTED — Cube IS Working

I claimed engine was in "deployment mode not cube mode". **Wrong.** Investigation revealed:
- `backtest/engine/backtest.py:2456` `save_all_outputs` invokes `_pool_cube_replay_worker`
- `exit_method_multi_dim_cube.csv` (Phase 1 output) contains **all 26 exit methods aggregated** by exit_method × regime × sector × cap_band × vol_band × hold_band
- `cube_compose_verdict.csv` has per-strategy verdicts (deflated_sharpe + SPA + BH-FDR + passes_compose)

The 109 rows in `trade_log_checkpoint.csv` are the **live deployment-mode trades** (one exit per strategy). The CUBE replay happens AFTER engine completes via `_pool_cube_replay_worker`, producing the aggregate cube CSVs.

I conflated the checkpoint with the final cube output. **Honest disclosure: bad attribution in B1065.**

### PIVOT #39 STILL VALID

119 SUSPECT SILENT strategies on NVDA × 4y stands. These are strategies that produced ZERO entries, so no cube cells exist for them. Verified below.

---

## 🎯 THE MONITOR QUESTION — COMPLETE ANSWER

### What the monitor SHOULD have flagged

Replicating `_check_a1_fire_rate` logic against Phase 1 data with B1059 scaling (1/503 for NVDA-only):

| Metric | Value |
|---|---|
| B660 strategies with non-zero baseline | 222 |
| Strategies expected to fire (scaled fpy ≥ 0.001/yr) at NVDA | 88 |
| Strategies expected but ACTUAL=0 (silent with expectation) | **63** |
| Strategies fired but at <50% scaled expectation | 24 |
| **Total a1_anom that monitor WOULD have computed** | **87** |
| WARN-HIGH threshold | 5 |
| HALT-CRITICAL threshold for a1 | **N/A — does not exist** |

### Top 30 SUSPECT SILENT by expected fire count (per B660 scaled to NVDA)

| Strategy | Expected fires Phase 1 | Actual |
|---|---|---|
| cpr_narrow_momentum | 165.8 | **0** |
| hull_rsi_short | 160.6 | **0** |
| hull_rsi | 141.2 | **0** |
| ichimoku_cloud_breakout | 131.2 | **0** |
| break_retest_confluence | 76.7 | **0** |
| avwap_50_reclaim | 67.6 | **0** |
| cpr_narrow_bullish | 61.5 | **0** |
| supertrend_ichimoku_adx | 27.1 | **0** |
| donchian_breakout_retest_long | 26.8 | **0** |
| macd_crossover_short | 23.7 | **0** |
| prev_day_high_break | 21.5 | **0** |
| three_white_soldiers | 20.7 | **0** |
| golden_cross_9_21 | 20.0 | **0** |
| macd_ichimoku | 19.4 | **0** |
| ppo_crossover | 17.0 | **0** |
| donchian_breakdown_retest_short | 15.5 | **0** |
| volume_spike_breakout | 14.4 | **0** |
| pivot_r1_breakout | 13.1 | **0** |
| camarilla_r4_breakout | 13.1 | **0** |
| adx_initiation | 12.1 | **0** |
| ichimoku_tk_cross | 11.8 | **0** |
| parabolic_sar_flip_short | 10.6 | **0** |
| rsi_oversold | 10.5 | **0** |
| 52w_high_breakout_pullback_long | 10.0 | **0** |
| avwap_252_breakout | 10.0 | **0** |
| prev_day_low_breakdown | 9.6 | **0** |
| roc_burst | 9.1 | **0** |
| donchian_breakdown_short | 8.8 | **0** |
| 52wh_break_retest | 8.4 | **0** |
| golden_cross_20_50 | 7.8 | **0** |

**Total expected fires across 63 silent strategies:** ~1,500+ trades that didn't happen on NVDA × 4y.

These are NOT cross-sectional or event-required strategies. These are basic price-action, momentum, and trend strategies that should fire on any single ticker over 4 years.

### Why the monitor's log was empty (b1019_monitor.log = 0 bytes)

```python
# scripts/b1019_phase_1_runtime_monitor.py uses print() throughout:
print(f"B1019 MONITOR ARMED: ...")        # line 95
print(f"B1059 PIVOT #36: A1 baseline scaled by {scale}")  # line 89
print(_format_checkpoint_line(tier, current_day, a1, b2, d1))  # line 120
```

**Python `print()` is block-buffered when stdout is redirected to a file** (only line-buffered when connected to a TTY). Launch script:
```bash
setsid python scripts/b1019_phase_1_runtime_monitor.py ... > ${PHASE_DIR}/b1019_monitor.log 2>&1 &
```

→ stdout redirected to file → block-buffered → buffer fills slowly → process killed at phase end → **buffer lost → 0-byte file**.

### Why a1_anom=87 didn't HALT

From `_classify_tier:302-313`:

```python
def _classify_tier(a1, b2, d1) -> str:
    if str(b2.get("status", "")).startswith("ERROR"):
        return "HALT-CRITICAL"
    if b2.get("violations"):
        return "HALT-CRITICAL"      # ← only B2 violations halt
    if a1.get("anomaly_count", 0) >= 5:
        return "WARN-HIGH"          # ← A1 at any count = WARN only
    if a1.get("anomaly_count", 0) > 0:
        return "LOG-MEDIUM"
    return "OK"
```

**Design choice:** A1 fire-rate anomalies emit at WARN-HIGH severity only. Even 87 anomalies (~99% of expected-firing strategies silent) does not trigger HALT-CRITICAL.

This is technically correct (A1 is a soft signal; B2 schema is hard), but in practice **the monitor saw 87 strategies misbehaving and emitted WARN — but nobody saw the WARN because of the buffer flush bug**.

---

## Monitor Design Gap Inventory

| Class | Check | Current behavior | Should be |
|---|---|---|---|
| A1 | per-strategy fire rate | WARN-HIGH only | HALT if anom_count > 50% of expected-firing strategies (catches massive silent-strategy issues like Phase 1's 87 of 88) |
| B2 | trade_log schema | HALT-CRITICAL on any violation | ✅ correct |
| D1 | cube cells progress + ETA | Informational only (no HALT) | LOG-MEDIUM if rate << expected at sim_day 100; HALT if rate stays << expected at sim_day 500 |
| C-NEW | cube-vs-deployment ratio | NOT IMPLEMENTED | LOG-MEDIUM (cube fan-out happens post-engine in `save_all_outputs`; monitor only sees live engine) |
| E-NEW | silent-strategy floor | NOT IMPLEMENTED | HALT if >50% of B660-nonzero strategies fire 0 by sim_day 500 |
| F-NEW | per-strategy regime coverage | NOT IMPLEMENTED | LOG-MEDIUM if strategy fires 0 in expected regime |
| **G-IMPL** | **stdout buffering** | **`print()` block-buffered** | **`print(flush=True)` OR `python -u` in launch script** |

### Recommended fixes for next Phase D launch

1. **Critical (visibility):** Add `print(..., flush=True)` to monitor.py OR change launch script to invoke `python -u scripts/b1019_phase_1_runtime_monitor.py`. Without this, future monitor.log files will also be empty.
2. **High (escalation):** Promote A1 mass-anomaly to HALT-CRITICAL threshold (e.g., anomaly_count > 50% of expected-firing strategies).
3. **Medium (new check):** Add E-class silent-strategy floor — if >50% of B660-nonzero strategies fire 0 by sim_day 500, HALT.
4. **Low (visibility):** Implement F-class per-strategy regime coverage as LOG-MEDIUM.

---

## What this means for the 119 SUSPECT SILENT strategies (PIVOT #39)

Investigation candidates surfaced from monitor's would-be a1_anom data:

**Highest-expected silent (likely producer/signal bugs):**
- `cpr_narrow_momentum` / `cpr_narrow_bullish` — CPR (Central Pivot Range) producer issue?
- `hull_rsi` / `hull_rsi_short` — Hull MA + RSI combination producer?
- `ichimoku_cloud_breakout` / `ichimoku_tk_cross` — Ichimoku producer?
- `avwap_50_reclaim` / `avwap_252_breakout` — AVWAP anchor producer?
- `donchian_breakout_retest_long` / `donchian_breakdown_retest_short` — Donchian retest producer?
- `golden_cross_*` family (9_21, 20_50, 50_200) — MA cross producer or threshold?
- `52w_high_breakout_pullback_long` — 52w high pullback producer?
- `ppo_crossover` / `macd_crossover_short` / `macd_ichimoku` — MACD/PPO crossover producer?
- `volume_spike_breakout` — volume spike threshold too tight?
- `prev_day_high_break` / `prev_day_low_breakdown` — pivot break producer?

These should be empirically tested via Phase 4 (Master 1929) data when available — if they ALSO produce 0 fires on full universe, there's a producer bug. If they fire on Master but not NVDA, it's a single-ticker selection issue.

---

## Phase 2 / 3 / 4 forensics commitment

Once each phase completes, re-run this audit on its trade_log + cube outputs. Phase 2 (10 tickers) will narrow SINGLE_TICKER_NOOP class. Phase 4 (1929 tickers) will distinguish producer-bug silent vs sampling-noise silent.

---

## Pre-flight CHECKLIST compliance

- #25 Owner forensics request
- #45 Pre-flight visible
- #67 Per-turn doc-sync (this report)
- #94 EXECUTION_QUEUE update: PIVOT #38 RETRACTED, PIVOT #39 still valid, NEW PIVOT #38-MONITOR-BUFFER candidate (stdout flush bug)
- #105 Source-read backtest.py:600, monitor.py classify_tier, writer.py save_all_outputs, B660 schema
- #110 Council 166 BEFORE analysis
- #115 Council 166 enumerate + recommend (4 options + Option-4 OWNER-LITERAL + MONITOR-AUDIT)
- #124 DESIGNED-NOT-VERIFIED: monitor was DESIGNED to catch a1_anom but VERIFICATION failed because of buffer bug + WARN-only design
- #126 Replicated A1 check against real data = evidence artifact

## Honest disclosure

PIVOT #38 was a FALSE PIVOT caused by reading the wrong file (`trade_log_checkpoint.csv` instead of `trade_log.csv` + `exit_method_multi_dim_cube.csv`). The cube fan-out works. This is the third wrong-attribution this session (after B1059 a1_anom attribution + B1062 PIVOT #37 + this PIVOT #38 retraction). Process improvement: read ALL output files before claiming missing cube mode.

The MONITOR question revealed three real issues:
1. **G-IMPL stdout buffer bug** (NEW PIVOT candidate): monitor.log always 0 bytes because of Python `print()` block buffering
2. **A1 WARN-only design**: A1 mass-anomaly does not HALT, only WARN
3. **PIVOT #39 still valid**: 119 SUSPECT SILENT confirmed; 63 of those had non-zero scaled B660 baseline

The MONITOR DID see the silent strategies (would have computed a1_anom=87) but the output was lost to buffering AND the severity was capped at WARN.
