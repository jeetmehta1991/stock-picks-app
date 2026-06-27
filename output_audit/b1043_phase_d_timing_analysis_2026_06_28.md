# Source: Council 137 + Council 138 + feedback_monitor_design_vs_operational_gap per CHECKLIST #77.

# B1043 Phase D Timing + Auto-Timeout Analysis

**Date:** 2026-06-28  
**Sub-agent:** Council 137 Option-4 Sub-agent C  
**Source files audited:**

- `scripts/launch_r5_master_4y_v2.sh` (per-phase MAX_MIN config; lines 49, 267-270)
- `backtest/run_phase1a.py` (engine `--warn-run-hours` / `--max-run-hours`; lines 197-207, 251-259)
- `backtest/engine/backtest.py` (wall-time guard; lines 457-540; per-day loop at 467; pool wiring at 1093, 2540)
- `backtest/config.py` (`PARALLEL_BACKTEST_EXECUTOR = "ProcessPoolExecutor"`, line 1521)
- `CLAUDE.md` banner (line 4 - "B1028 expected $1.20-2.70")
- Phase C v1 + v2 smoke wall-clocks (memory rule `feedback_phase_ladder_timing_validation`)

---

## 1. Per-phase EXPECTED wall-clock (empirical, from Phase C smokes)

**Empirical anchor - Phase C smoke (NVDA x 22 trading days x 219 strategies x 26 exits):**

- **C v1 (B1028):** 10:08 engine wall-clock = **608 s** for 1 ticker x 22 bars x 219 strats
- **C v2 (B1041+B1042):** 10:17 engine wall-clock = **617 s** (SMC computing path)

This gives a baseline of **~28 s / bar / ticker** at `--screen-pool-workers=60` with 1 ticker (pool is idle - only 1 ticker per day, so all 60 workers wait on 1 task per day). The per-ticker-bar cost will drop massively when pool saturates.

**Pool saturation behavior:** `screen_universe()` parallelizes the per-ticker screen across workers per day (`backtest.py:1095-1100`). Per-day cost is `ceil(N_tickers / 60) x per_ticker_bar_cost`. When N_tickers >= 60 the pool is fully saturated; when N_tickers <= 60 cost ≈ per_ticker_bar_cost (worst-case task dominates).

**Per-bar cost models:**
- Phase 1 (N=1, pool idle): ~28 s/bar
- Phase 2 (N=10, pool idle): ~28 s/bar (worst-of-10 ≈ single)
- Phase 3 (N=50, pool near-idle): ~28-30 s/bar
- Phase 4 (N=1929, pool saturated 32x over): ~28 x (1929/60) = **~900 s/bar = 15 min/bar**

Wait - that extrapolation is **alarming**. Let me re-anchor: 608 s / 22 bars / 1 ticker / 219 strategies = **~0.13 s per (bar x ticker x 219-strategy-screen)** when measured serially. The pool overhead, worker init, and per-day teardown dominate at N=1.

**Calibration check - fire-rate x per-bar:** Smoke produced 7 trades in 22 bars x 1 ticker - very low fire rate. Phase 4 fire-count budget (per `output_audit/b660_fire_count_measured.json`): ~5,694 cells x N_fires/yr. Most engine time is screening, not trade execution. So per-ticker-bar screen cost is the bottleneck.

### Per-phase expected wall-clock (low/best/high estimates)

| Phase | N_tickers | Bars | Per-day cost (s) | Engine wall-clock | + Boot/sync overhead |
|---|---|---|---|---|---|
| Phase 1 (NVDA) | 1 | 1006 | ~27.6 | **~7.7 hr** (NVDA alone x 4y at 22-bar smoke rate) | + 5 min |
| Phase 2 (10 tickers) | 10 | 1006 | ~28 (pool absorbs) | **~7.8 hr** | + 5 min |
| Phase 3 (50 tickers) | 50 | 1006 | ~30 (pool still absorbs <=60) | **~8.4 hr** | + 5 min |
| Phase 4 R5 (1929) | 1929 | 1006 | ~28 x ceil(1929/60) = ~28 x 33 = ~924 | **~258 hr (~10.8 days)** | + 5 min |

**This is the worst-case extrapolation if Phase C smoke per-ticker-bar cost holds linearly.**

### Re-calibration - pool init dominates smoke

Phase C smokes had 22 bars only. The 608s = **pool init + 22 x per_bar + teardown**. If init+teardown ≈ 300 s, then per_bar ≈ (608-300)/22 ≈ 14 s/bar (1 ticker, idle 60-pool). At N=1929 saturated pool, per_bar ≈ 14 x 33 ≈ **462 s/bar = ~7.7 min/bar**.

Then Phase 4: 1006 x 462 = **464,772 s = ~129 hr = ~5.4 days**.

### Owner-banner claim reconciliation

CLAUDE.md banner says "B1028 expected $1.20-2.70" on c6a.16xlarge spot (~$1.05/hr). That implies **1.1-2.6 hours wall-clock total** - incompatible with both extrapolations above unless the engine is dramatically faster on saturated pool than the smoke implied. Either:

1. The Phase C smoke is dominated by pool-init/teardown that is amortized across 1006 bars (true bar cost ~5-10 s on saturated pool -> 1.4-2.8 hr matches banner). **Or**
2. The banner estimate was a Council 110 / 119 / 121 memory-based estimate that was never re-verified after the Phase C smoke timing was measured. Per `feedback_phase_ladder_timing_validation`, B1028 already had this exact failure mode (30-min estimate, 1h 38m actual).

**Honest finding:** The PROJECT does NOT have an empirical Phase 4-size measurement. The 1.20-2.70 figure is unverified.

---

## 2. Per-phase MAX_MIN auto-timeout (from launch script)

From `scripts/launch_r5_master_4y_v2.sh` lines 267-270:

| Phase | Tickers | MAX_MIN | MAX hours |
|---|---|---|---|
| Phase 1 | NVDA (1) | **30** | 0.50 |
| Phase 2 | 10 names | **60** | 1.00 |
| Phase 3 | 50 stride | **90** | 1.50 |
| Phase 4 R5 | Master 1929 | **240** | **4.00** |
| Smoke | NVDA x 1mo | **15** (line 49) | 0.25 |

**Cumulative ladder MAX_MIN = 420 min = 7.0 hr** (Phase 1+2+3+4 sequential).

Watchdog is `phase_watchdog()` lines 158-168 - sleeps `MAX_MIN x 60` then `kill -9` engine + writes `PHASE_X_TIMEOUT_HALT` sentinel. Granularity: **single sleep** (not polled), so the timeout fires exactly at MAX_MIN.

---

## 3. Engine self-timeout config

From `backtest/run_phase1a.py:251-259`:

```python
if args.phase == "1a-beta" and args.warn_run_hours is None:
    args.warn_run_hours = 4.0
if args.phase == "1a-beta" and args.max_run_hours is None:
    args.max_run_hours = 6.0
```

- `--warn-run-hours = 4.0` (single WARN log line; non-fatal)
- `--max-run-hours = 6.0` (engine flushes `trade_log_checkpoint.csv` + `sys.exit(1)`)

Checked every 20 trading days in main loop (`backtest.py:487, 513`).

**Conflict matrix (which timeout fires first):**

| Phase | shell MAX_MIN | engine max-run-hours | WINNER |
|---|---|---|---|
| Phase 1 | 30 min (0.5 hr) | 6.0 hr | **shell @ 30 min** |
| Phase 2 | 60 min (1.0 hr) | 6.0 hr | **shell @ 60 min** |
| Phase 3 | 90 min (1.5 hr) | 6.0 hr | **shell @ 90 min** |
| Phase 4 | 240 min (4.0 hr) | 6.0 hr | **shell @ 240 min** |

Engine self-kill never fires under current config - shell watchdog always pre-empts. WARN at 4.0 hr fires only on Phase 4 if it crosses the 4-hr mark (which is also the shell HALT).

---

## 4. Cumulative ladder timing

- Cumulative MAX_MIN cap: **7.0 hr** (30+60+90+240)
- Boot+install+data-sync overhead pre-Phase 1: ~5-10 min
- Auto-shutdown post-completion: `sudo shutdown -h +1` (1 min grace for final S3 sync; line 276)
- Spot cost ceiling at $1.50/hr x 7 hr = **$10.50 max** before timeouts cascade

CLAUDE.md banner $1.20-2.70 implies expected ~1-2.5 hr total. **5x headroom** between expected and shell cap.

---

## 5. Risk assessment

### RISK A - Phase 4 MAX_MIN=240 may be too tight

If Phase 4 actually takes >4 hr (one of the extrapolations above puts it at 5.4 days, the other at 2-3 hr), the watchdog will `kill -9` the engine and write `PHASE_4_TIMEOUT_HALT`. The `trade_log_checkpoint.csv` flush at `max_run_hours=6.0` will NOT fire because the shell kills the engine before the engine reaches 6 hr. **Silent partial-cube data loss is possible** - checkpoints land every 100 days via `_emit_milestone_telemetry("100D")` (backtest.py:482).

### RISK B - Per `feedback_phase_ladder_timing_validation` - empirical anchor missing

B1028 had a 30-min estimate that became a 1h 38m actual. The current Phase 1-4 MAX_MIN ladder is based on `MAX_PHASE_MIN=15` smoke + extrapolated guesses, **not empirical Phase 4-size measurement**. Per the memory rule, a Phase 2 or Phase 3 wall-clock observation MUST be taken before Phase 4 cascades.

### RISK C - Engine max-run-hours never fires -> no engine-side recovery

Because shell watchdog (240 min) < engine kill (360 min), the engine's defensive checkpoint flush (`backtest.py:521-534`) is dead code. If shell `kill -9` doesn't flush checkpoint, partial Phase 4 output is whatever the 60s sync_loop captured last.

### RISK D - `sudo shutdown -h +1` may be too short

Final S3 sync of full Phase 4 output_dir + sentinels in 60 seconds. Phase 4 output_dir for 1929 tickers x 4y could be 100-500 MB. At typical EC2-S3 throughput (~80 MB/s), this is feasible - but `sync_loop` having run continuously every 60s should mean delta-sync is small. **Low risk.**

### RISK E - phase_watchdog 60s granularity

Watchdog uses a single `sleep $((MAX_MIN * 60))` (line 162) - NOT polled. Granularity is `MAX_MIN x 60s` x 1 sample. **No granularity risk** since the kill is precise.

---

## 6. Recommendations

1. **(P0) Pre-Phase-D Phase 2 timing validation.** Launch Phase 1+2 standalone (60 min cap is small enough to risk), measure actual wall-clock, and extrapolate to Phase 4 with empirical confidence interval. Without this, Phase 4 MAX_MIN=240 is an unverified guess.

2. **(P0) Raise Phase 4 MAX_MIN to 360.** Match the engine's `--max-run-hours=6.0` so the engine's checkpoint flush has a chance to fire BEFORE the shell `kill -9`. Or alternatively, drop engine to `--max-run-hours=3.5` to ensure engine self-kill always fires first.

3. **(P1) Add Phase 4 mid-run progress sentinel.** Engine already emits "100D" telemetry. Wrap that to write `PHASE_4_PROGRESS_<X>D` sentinels to S3 so owner can see fractional completion without grep'ing engine.log.

4. **(P1) Extend `sudo shutdown -h +1` to `+3`.** 3 min grace for final S3 sync at near-zero added cost (1-2 cents).

5. **(P2) Document the banner $1.20-2.70 source.** Per CHECKLIST #41, memory-based cost estimates are not acceptable without verification. Either anchor the figure to Phase 2/3 measured wall-clock x spot price or drop it from the banner.

---

## Summary

Per-phase MAX_MIN auto-timeouts: Phase 1 = 30 min, Phase 2 = 60 min, Phase 3 = 90 min, Phase 4 = **240 min (4 hr)**. Cumulative ladder cap = **7.0 hr**. Engine self-kill `--max-run-hours=6.0` never fires because shell watchdog pre-empts on every phase. Expected wall-clock for Phase 4 is **unverified empirically** - Phase C smoke is too small to extrapolate (pool init dominates). Owner banner $1.20-2.70 (~1-2.5 hr at spot) is a Council-era estimate, not a measured value. Per `feedback_phase_ladder_timing_validation` (B1028 lesson), this is exactly the failure mode that produced the 1h 38m actual vs 30-min estimate. **STRONG RECOMMENDATION: run Phase 1+2 standalone first; extrapolate Phase 4 from measured Phase 2/3 wall-clock before committing to MAX_MIN=240.**
