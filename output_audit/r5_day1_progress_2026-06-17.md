# R5 Day 1 Triage Progress (Batch 885)

# Source: B883 triage audit + B884 decisions #1/#3 + owner decision #13(b) + live execution

**Status:** IN_PROGRESS 2026-06-17 (Batch 885)
**Authority:** Council 10 verdict approved B883; owner decision #13(b) delta-only

---

## Day 1 Execution Status

### COMPLETED

| Gate/Item | Result |
|---|---|
| **G1** SHA pin | `a8cff9a1d682f5d0e079e63200542bba37223f51` saved to `r5_launch_candidate_sha.txt` |
| **G2** Strategy count assert | PASS — `len(ALL_STRATEGIES) == 219` |
| **G4** AWS instance type | c7a.8xlarge spot @ $0.52/hr × 3 instances × 5h = **$7.80/run** (B884) |
| **#2** 351 R4 atomic rows | RESOLVED-VIA-STAGE-4-WALK-OUTPUTS (B883 + CLAUDE.md banner update B884) |

### IN PROGRESS

| Item | Status |
|---|---|
| **#13 B660 v2 delta-only** | LAUNCHED background 21:58Z (20 strategies); estimated ~1-2h; log: `output_audit/b885_v2_delta_launch.log`; output: `output_audit/fire_count_measured_b885_v2_delta.json` |
| **G3** Pyramid full re-run | Not yet launched (will run post-B885 commit) |
| **G5** Optimizer schema-pin | Not yet launched (will run post-B885 commit) |
| **#6** Fire-bar matrix FULL re-launch | PID-guard fix pending |
| **#11** Stage 5 SWAP #73-75 | Surface to owner for review |

### NEW FINDING: #5 "18 substantive pyramid items" is INHERITED LANGUAGE

Audit per CHECKLIST #44(b) runtime probe:

- CLAUDE.md banner cites "(vii) 18 substantive pyramid items (B586/B533/B465 + 15 singletons)" with no consolidated artifact.
- Pyramid grep finds only **5 unconditional `@pytest.mark.skip(reason=...)` markers**:
  1. test_batch537_opt_b_panel_technical.py (B840)
  2. test_batch538_panel_wire_in_parity_gate.py (B840)
  3. test_batch568_preflight_cross_sweep.py (B839)
  4. test_engine_optimization_parity.py (B841)
  5. test_performance.py (B841)
- 6 `@pytest.mark.xfail` markers exist; uncounted in CLAUDE.md banner.
- No discrete list of "18 substantive items" exists anywhere in codebase.

**SAME GHOST-PATTERN AS #2 (351 rows).** Per Outsider Council 10 diagnostic: inherited language with no current anchor.

**Recommendation: Run the full pyramid. Whatever fails IS the deferred list.** Mark them properly with `@pytest.mark.skip(reason="<ticket>")` rather than treating "18" as a target count to clear.

---

## #11 Stage 5 SWAP #73-75 Review (surface for owner)

Located at `backtest/config.py:226-242` as `B834-RECOMMEND-SWAP-DEFERRED`:

| # | Strategy | Proposed exit override | Source |
|---|---|---|---|
| **#73** | strat_stochrsi_oversold | (basis: R4 cube Sharpe) | B834 cell-level evidence |
| **#74** | strat_po3_bullish | `class_time_stop` | B834 cell-level evidence |
| **#75** | strat_cpr_narrow_bullish | `regime_flip` | B834 cell-level evidence |

Context: #71 williams_r_oversold + #72 institutional_cluster_long already shipped B835.

**Owner decision needed:** approve / reject / hold-for-R5 each of #73, #74, #75?

---

## Owner Decision Queue (3 items)

1. **#5 corrective action:** Run full pyramid; treat actual failures as the "18 substantive items" list — approve?
2. **#11 SWAP #73-75:** Approve / reject / hold each?
3. **Day 1 continuation:** While B660 v2 runs background, should Claude proceed with G3 pyramid + G5 optimizer + #6 fire-bar in parallel, OR wait for B660 v2 first?

---

## Realistic Day 1 Timeline (updated)

- T+0 (now): B660 v2 running background (~1-2h remaining)
- T+5min: G3 pyramid launch background (~1h45min)
- T+10min: G5 optimizer schema-pin launch (~30-60min)
- T+15min: #6 fire-bar PID-guard fix + re-launch (~14h background)
- T+30min: surface #11 SWAPs + #5 corrective action to owner
- T+2h: B660 v2 complete → commit results
- T+2h: G3 pyramid complete → review failures, update #5 list
- T+2.5h: G5 optimizer complete → verify schema alignment

**Day 1 closes ~T+3h if all foreground work parallelizes.**
