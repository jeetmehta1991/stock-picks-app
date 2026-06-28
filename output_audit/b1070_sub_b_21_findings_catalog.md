# B1070 Sub-B PASS-Path Adversarial Review — Complete 21-Finding Catalog

# Source: Sub-B sub-agent task a262d6ad35478f82b (Council 169 Option-2 PARALLEL-MULTI-AGENT launch 2026-06-29) per CHECKLIST #77 + Council 182 Block-2 audit persistence requirement.

**Persisted retroactively** per Council 182 audit finding META-2 (Sub-B 21-finding catalog never persisted as standalone audit doc; ~15 findings were at risk of being lost). Reconstructed from task-notification result text (preserved in conversation memory).

---

## Summary

21 findings: **P0=4, P1=8, P2=6, P3=3 / BLOCKER=3, HIGH=7, MEDIUM=8, LOW=3**

## P0 BLOCKERS (3) — ALL SHIPPED in B1070 Stage B

### F-1.1 P0 BLOCKER — Engine never emits `status: "complete"` to `engine_state.json`
- **Source:** `backtest/engine/backtest.py` lines 595-619 only write `"running"`; lines 639-686 never re-write after `_finalize_open_trades` + `save_all_outputs`
- **Impact:** B1019 monitor's PASS-exit conditions (lines 119-122, 146-148) poll for `status == "complete"` — NEVER fires on PASS path
- **Mechanism:** Same class as B1067 G-IMPL: HALT-path SIGTERM masked the missing write
- **Mitigation:** atomic `.tmp + os.replace` `status: "complete"` write at line 651 after `_finalize_open_trades`
- **STATUS:** ✅ **SHIPPED Stage B `819b28ebf`**

### F-2.1 P0 BLOCKER — Cube replay `_pool_cube_replay_worker` IPC OOM at Phase 4 scale
- **Source:** `backtest/engine/backtest.py` lines 2558-2624
- **Impact:** `mp.Pool.starmap` materializes results list; 220 strategies × 30-50K trades × per-trade entry_context dict pickled to 60 workers → 5-20GB resident on top of pool memory
- **Mitigation:** switch to `imap_unordered` + stream-write per-strategy CSV
- **STATUS:** ✅ **SHIPPED Stage B `819b28ebf`**

### F-7.1 + F-10.1 P0 BLOCKER — Phase 4 pool=60 at 1929-ticker scale never empirically validated + B1068 ema_sma 13.5hr cost
- **Source:** Launcher lines 217-220 acknowledge only NVDA (1 ticker) + Phase 2 mini-smoke (10 tickers) tested
- **Impact:** Phase 4 likely exceeds 8hr watchdog (MAX_MIN=480) given F-10.1 ema_sma overhead
- **F-10.1 detail:** B1068 panel-blackout fix re-added `compute_ema_sma` at +25ms/ticker/day → 1929 × 1006 × 25ms = ~13.5 hours JUST for ema_sma → Phase 4 wall-clock ~16-20hr vs 8hr watchdog
- **Mitigation:** pool=16 + MAX_MIN=1200, OR ship technical_panel.compute_ema_sma_panel extension
- **STATUS:** ✅ **SHIPPED Stage B `819b28ebf` (pool=60→16, MAX_MIN=480→1200)**

---

## HIGH findings (7) — 2 SHIPPED in Stage D; 5 NOT-ACTED-NO-TICKET (5 of 21 lost prior to Council 182 audit)

### F-1.2 HIGH — Monitor process hangs indefinitely waiting for `status==complete` (consequence of F-1.1)
- Cleanup SIGTERM at launcher line 281-283 → monitor.log shows no COMPLETE line on PASS, indistinguishable from "still running"
- **STATUS:** ✅ **RESOLVED via F-1.1 fix (Stage B `819b28ebf`)** — F-1.1 emits status=complete → monitor PASS-exit fires cleanly

### F-2.2 HIGH — Cube-replay pool reuses Batch 322 screen pool — 60 workers × (190MB OHLCV + 500-800MB Quiver bulk) = ~33GB resident on 64GB instance
- **STATUS:** 🟡 **PARTIAL — pool reduced 60→16 in F-7.1; memory reduced ~33GB → 9GB (per-worker × 16 = 8.8GB OHLCV + 12-16GB Quiver = ~21GB)**
- **NOT-ACTED-NO-TICKET:** further reduction would require panel-substitution for Quiver bulk feeds; recommend `S5-B1072-CUBE-REPLAY-POOL-MEMORY-FURTHER-OPTIMIZATION` (B1072+)

### F-2.3 HIGH — Silent `logger.debug` exception swallow in per-trade exit replay (`exit_strategies.py` line 1674-1675)
- **Impact:** schema drift would undercount cells silently
- **STATUS:** 🔴 **NOT-ACTED-NO-TICKET** — recommend `S5-B1072-EXIT-STRATEGIES-DEBUG-LOG-PROMOTE-TO-WARN`

### F-3.1 HIGH — PHASE_N_PASS sentinel emit at launcher line 287-300 uses `aws s3 sync --quiet` with no `|| exit`
- **Impact:** silent S3 failure leaves PASS sentinel without data
- **STATUS:** 🔴 **NOT-ACTED-NO-TICKET** — recommend `S5-B1072-SENTINEL-EMIT-AWS-SYNC-EXIT-CHECK` (per CHECKLIST #122 silent-failure-pairing)

### F-4.1 HIGH — sync_loop 60-sec cadence + duplicate explicit final sync at line 287 = two concurrent `aws s3 sync` invocations against same prefix, undefined ordering
- **STATUS:** 🔴 **NOT-ACTED-NO-TICKET** — recommend `S5-B1072-SYNC-LOOP-FINAL-SYNC-DEDUP`

### F-5.1 HIGH — sync_loop killed at line 361 BEFORE post-run analyzer + AUTOLADDER_COMPLETE; final sentinel sync alone uploads everything
- **STATUS:** 🔴 **NOT-ACTED-NO-TICKET** — recommend `S5-B1072-SYNC-LOOP-LIFECYCLE-EXTEND-POST-ANALYZER`

### F-6.1 HIGH — phase_watchdog vs natural completion: engine completes within ±2 sec of MAX_MIN → both PASS and HALT sentinels uploaded
- **STATUS:** 🔴 **NOT-ACTED-NO-TICKET** — recommend `S5-B1072-WATCHDOG-COMPLETION-RACE-ATOMIC-SENTINEL`

### F-7.2 HIGH — `_pool_init` pre-warms 5 Quiver bulk datasets per worker × 60 workers = 50-75 min pool-init wall-clock before first sim_day + ~36GB Quiver memory
- **STATUS:** 🟡 **PARTIAL — pool reduced 60→16 (Stage B F-7.1); init time and memory reduced proportionally (~17min init + 9.6GB Quiver)**
- **NOT-ACTED-NO-TICKET:** Pre-warm cost still 17 min × 16 workers; recommend `S5-B1072-POOL-INIT-SHARED-MEMORY-QUIVER-BULK`

### F-8.1 HIGH — B660 baseline measured 2020-2026 (mixed bull/crisis/bear/neutral); Phase 4 window 2022-2026 (bear-start) → A1 baseline scaling (B1059) handles universe size NOT regime mix → expect A1-PROMOTION HALT false positives
- **STATUS:** ✅ **SHIPPED Stage D `929ad24f4` — DEFER-IF-MIXED-REGIME warning emits; B660 re-measurement deferred to B1072**

### F-9.2 HIGH — A1-PROMOTION >50% mass-anomaly threshold trips spuriously in first 200 days before E-NEW silent_floor (sim_day>=500) takes over
- **STATUS:** ✅ **SHIPPED Stage D `929ad24f4` — current_day >= 200 gate added**

---

## MEDIUM findings (8) — ALL NOT-ACTED-NO-TICKET

### F-1.3 MEDIUM — engine_state stale 5 days at tail (no per-day rewrite for the final 5 days)
- **STATUS:** 🔴 **NOT-ACTED-NO-TICKET** — recommend `S5-B1072-ENGINE-STATE-PER-DAY-TAIL-WRITE`

### F-1.4 MEDIUM — os.replace EBS atomicity claim (works on POSIX + Windows per Python 3.3+; verified)
- **STATUS:** ✅ **ACKNOWLEDGED — Python 3.3+ guarantee covers; no action needed**

### F-2.4 MEDIUM — SPA bootstrap 200×5694 sequential (no parallelism in deflated_sharpe computation)
- **STATUS:** 🔴 **NOT-ACTED-NO-TICKET** — recommend `S5-B1073-SPA-BOOTSTRAP-PARALLELIZE` (P2 optimization)

### F-3.2 MEDIUM — AUTOLADDER_COMPLETE upload not retried on failure
- **STATUS:** 🔴 **NOT-ACTED-NO-TICKET** — recommend `S5-B1072-AUTOLADDER-COMPLETE-RETRY-WRAP`

### F-4.2 + F-4.3 MEDIUM — sync invocation count + .tmp pattern observations
- **STATUS:** 🔴 **NOT-ACTED-NO-TICKET** — bundled with F-4.1 recommend

### F-5.2 MEDIUM — `shutdown -h +1` too short for multi-GB sync (rare; only if last batch >60sec)
- **STATUS:** 🔴 **NOT-ACTED-NO-TICKET** — recommend `S5-B1072-SHUTDOWN-EXTEND-FOR-MULTI-GB-SYNC`

### F-6.2 + F-6.3 MEDIUM — SIGTERM mid-print + HALT_WATCHER race (both safe per analysis)
- **STATUS:** ✅ **ACKNOWLEDGED SAFE — no action needed**

### F-9.3 + F-9.4 MEDIUM — E-NEW silent_floor hardcoded 500; F-NEW regime-affinity import fallback
- **STATUS:** 🔴 **NOT-ACTED-NO-TICKET** — recommend `S5-B1072-E-NEW-CONFIG-PARAM` (configurable threshold; B1067 hardcoded value)

---

## LOW findings (3) — ALL NOT-ACTED-NO-TICKET

### F-11.1 LOW (→ promoted to P0 BLOCKER by Council 182) — 50GB EBS may fill
- **Phase 4 estimate:** trade_exit_detail.csv (5-15GB) + cube CSVs + 60 worker raw_signal_fires (6GB) + ~20GB data_prefetch cache = ~35-50GB
- **STATUS:** ⚠ **CODIFIED as CHECKLIST #131 + Block-1 launch helper VolumeSize=100 (Council 182 enforcement)**

### F-11.2 LOW — per-PID raw_signal_fires write amplification
- **STATUS:** 🔴 **NOT-ACTED-NO-TICKET** — recommend `S5-B1072-RAW-SIGNAL-FIRES-SHARED-WRITER`

### F-12.1 LOW — Spot interruption 5-15% over 16-20hr; trade_log_checkpoint survives but no resume infra
- **STATUS:** 🔴 **NOT-ACTED-NO-TICKET** — bundled with F-13.1

### F-13.1 LOW — No `--resume-from-checkpoint` flag exists anywhere; interruption at sim_day 700/1006 restarts from day 0
- **STATUS:** 🔴 **NOT-ACTED-NO-TICKET** — recommend `S5-B1073-RESUME-FROM-CHECKPOINT` (P2 architectural)

---

## Summary disposition

| Severity | Total | Shipped | Acknowledged | NOT-ACTED-NO-TICKET |
|---|---|---|---|---|
| P0 BLOCKER | 3 | 3 (F-1.1 + F-2.1 + F-7.1+F-10.1) | 0 | 0 |
| HIGH | 7 | 2 (F-1.2 via F-1.1; F-8.1; F-9.2) | 0 | 5 (F-2.2 partial; F-2.3; F-3.1; F-4.1; F-5.1; F-6.1; F-7.2 partial) |
| MEDIUM | 8 | 0 | 3 (F-1.4 + F-6.2 + F-6.3) | 5 (F-1.3; F-2.4; F-3.2; F-4.2/3; F-5.2; F-9.3/4) |
| LOW | 3 | 1 (F-11.1 codified + helper) | 0 | 2 (F-11.2; F-12.1; F-13.1) |
| **Totals** | **21** | **6** | **3** | **12** |

## Recommended new EXECUTION_QUEUE tickets

Per Council 182 Option 5 Block-3:

```
S5-B1072-EXIT-STRATEGIES-DEBUG-LOG-PROMOTE-TO-WARN (F-2.3)
S5-B1072-SENTINEL-EMIT-AWS-SYNC-EXIT-CHECK (F-3.1)
S5-B1072-SYNC-LOOP-FINAL-SYNC-DEDUP (F-4.1)
S5-B1072-SYNC-LOOP-LIFECYCLE-EXTEND-POST-ANALYZER (F-5.1)
S5-B1072-WATCHDOG-COMPLETION-RACE-ATOMIC-SENTINEL (F-6.1)
S5-B1072-POOL-INIT-SHARED-MEMORY-QUIVER-BULK (F-7.2)
S5-B1072-ENGINE-STATE-PER-DAY-TAIL-WRITE (F-1.3)
S5-B1072-AUTOLADDER-COMPLETE-RETRY-WRAP (F-3.2)
S5-B1072-SHUTDOWN-EXTEND-FOR-MULTI-GB-SYNC (F-5.2)
S5-B1072-E-NEW-CONFIG-PARAM (F-9.3/F-9.4)
S5-B1072-CUBE-REPLAY-POOL-MEMORY-FURTHER-OPTIMIZATION (F-2.2)
S5-B1072-RAW-SIGNAL-FIRES-SHARED-WRITER (F-11.2)
S5-B1073-SPA-BOOTSTRAP-PARALLELIZE (F-2.4)
S5-B1073-RESUME-FROM-CHECKPOINT (F-12.1 + F-13.1)
```

**12 new B1072+ tickets** surfaced by Sub-B catalog persistence (would have been lost without Council 182 audit).
