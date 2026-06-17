# R5 Pre-Launch Triage Audit (Council 10 Verdict Execution)

# Source: per CHECKLIST #77 + #44(b) runtime probe; inputs are EXECUTION_QUEUE.md (triage items), CLAUDE.md banner (step ii/v/vii claims), scripts/extract_proposed_changes.py + scripts/aws_batch395_launch.py + scripts/optimize_strategies_from_cube.py (script existence), backtest/config.py:226-242 (SWAP #73-75), backtest/tests/test_unit.py (G2 count assert), output_audit/*.json + *.parquet + *.log (artifact existence)

**Status:** EXECUTED 2026-06-17 (Batch 883)
**Authority:** Council 10 verdict approved by owner; "audit ALL remaining items for ghost-status BEFORE Day 1 execution"
**Method:** Runtime probe per CHECKLIST #44(b) on each pre-R5 triage item

---

## Summary Table

| # | Item | Status | Risk | Action |
|---|---|---|---|---|
| **G1** | SHA pin | REAL trivial | None | 5-min mechanical |
| **G2** | Strategy count assert (219) | REAL verified | None | test_unit.py exists |
| **G3** | Pyramid full re-run | REAL | Wall-clock ~1h45min | Background launch |
| **G4** | AWS spot capacity probe | REAL **+ DISCREPANCY** | Instance-type mismatch with Council 7 | Reconcile c7a.4xlarge vs c7a.8xlarge |
| **G5** | Optimizer schema-pin on R4 | REAL upstream-only | Needs ~30-60min optimizer dry-run | Background launch |
| **#2** | 351 R4 atomic rows | **GHOST → RESOLVED-VIA-STAGE-4-WALK-OUTPUTS B883** | None per Council 10 | No action |
| **#5** | 18 substantive pyramid items | **REAL + LIST-NOT-CONSOLIDATED** | Specific 18 not enumerated as artifact | Derive from B814-B824 deferred subset |
| **#6** | Fire-bar matrix FULL | PARTIAL (smoke shipped B756; full B812 PID-died) | Re-launch with PID-guard | Background launch |
| **#11** | Stage 5 SWAP #73-75 | REAL + SPECIFIC | None | Apply 3 candidates from `config.py:226-242` |
| **#13** | B660 v2 scope decision | **UNDERSPECIFIED** | "v2" scope not defined anywhere | Owner-clarify what changes in v2 |

**Net of audit:** 8 active items + 1 RESOLVED (#2). **2 items have hidden underspecification (G4 + #13).** **1 item needs upstream derivation (#5).**

---

## Per-Item Audit Detail

### G1 — SHA pin + tag `r5-launch-candidate`
- **Real?** Yes. Trivial `git rev-parse HEAD` + tag command.
- **Risk:** None.
- **Action:** Execute when launch decision lands.

### G2 — Strategy count assert (219)
- **Real?** Yes. `backtest/tests/test_unit.py` contains `assert len(ALL_STRATEGIES) == 219` per B814-B824 sweep.
- **Verified:** `python -c "from backtest.signals.screener import ALL_STRATEGIES; print(len(ALL_STRATEGIES))"` returns 219 per B874 deletion.
- **Risk:** None.
- **Action:** `pytest -k "strategy_count" -q` at launch.

### G3 — Pyramid full re-run
- **Real?** Yes. Baseline ~1882 tests per CLAUDE.md.
- **Risk:** Wall-clock ~1h45min; xdist parallel load.
- **Action:** Background launch; not foreground-blocking.

### G4 — AWS spot capacity probe (**DISCREPANCY FLAGGED**)
- **Real?** Yes. `scripts/aws_batch395_launch.py` exists.
- **DISCREPANCY:** Launch script docstring says `c7a.4xlarge ~$0.86/hr`. Council 7 plan + Batch 424 history reference `c7a.8xlarge ~$9.30 / 5h`. **Two different instance types.**
- **Risk:** If we probe wrong instance type, we get false-positive capacity. Compute cost also differs.
- **Action:** Owner-decision needed — which instance type does R5 actually launch on? Reconcile config + launch script vs documented plan.

### G5 — Optimizer schema-pin on R4 cube
- **Real?** Yes. `scripts/optimize_strategies_from_cube.py` exists.
- **Risk:** Optimizer was last run pre-B566 (~2 weeks pre-roster-change); 219 vs old count may misalign cube cells.
- **Action:** Run optimizer dry-run on `output_batch395_final/` to verify 219 × 26 schema. ~30-60min background-launchable.

### #2 — 351 R4 atomic rows → **RESOLVED PER COUNCIL 10**
- **Real?** No — ghost artifact (ephemeral output from B566 extractor; not regenerated since).
- **Replacement:** Stage 4 cluster walks already produced approved mutations per walk (B603/B636/B645/B685/B686/B722/B874/etc.). Each walk = Stage 4 atomic approval.
- **Action:** None. Mark step (ii) `RESOLVED-VIA-STAGE-4-WALK-OUTPUTS B883`. Update CLAUDE.md banner.

### #5 — 18 substantive pyramid items
- **Real?** Yes per CLAUDE.md banner ("B586/B533/B465 + 15 singletons").
- **GAP:** The specific 18-item list is NOT consolidated as an artifact. B814-B824 fixed 73 pyramid failures (per commit messages: 8+3+4+7+7+4+15+12+4+7+3 = 74 across 11 batches); 18 are the DEFERRED subset, but identifying which 18 requires reading each test file's skip/xfail markers.
- **Risk:** Without consolidation, owner can't review the 18 individually.
- **Action:** Claude-task: enumerate the 18 by grep'ing `@pytest.mark.skip` + `@pytest.mark.xfail` markers added in B814-B824. ~30min.

### #6 — Fire-bar matrix FULL run
- **Status:** PARTIAL. SHIPPED-SMOKE per B756 (verified: `output_audit/fire_bar_matrix_cluster_a_smoke.parquet` + `_demo.parquet` exist; B756 commit log confirms). B812 FULL attempt PID-died (per B827; `output_audit/b812_fire_bar_matrix_full.log` exists).
- **Risk:** Re-launch must include PID-guard fix per `feedback_check_existing_pids_before_long_background_launch`.
- **Action:** Read B812 log → identify crash root cause → PID-guard fix → background re-launch. ~30min Claude + 14h background runtime.

### #11 — Stage 5 SWAP #73-75
- **Real?** Yes + SPECIFIC. Located at `backtest/config.py:226-242` as `B834-RECOMMEND-SWAP-DEFERRED` comments:
  - **#73:** `stochrsi_oversold` (R4 cube Sharpe basis; defer per B834)
  - **#74:** `po3_bullish` → `class_time_stop`
  - **#75:** `cpr_narrow_bullish` → `regime_flip`
- **Context:** #71 williams_r_oversold + #72 institutional_cluster_long already shipped B835.
- **Risk:** Per `feedback_strategy_x_exit_cell_analysis` cell-level evidence; these are owner-decision items.
- **Action:** Owner reviews 3 swap proposals + decision. ~10min owner review.

### #13 — B660 v2 measurement re-run scope (**UNDERSPECIFIED**)
- **B660 v1:** EXISTS at `output_audit/fire_count_measured_b660_full_universe.json` (verified). Full universe T1a 2020-2026.
- **B660 v2:** **SCOPE NOT DEFINED.** Owner mentioned "B660 v2 scope needed pre-R5 or absorb into R5" but never specified what v2 includes that v1 doesn't. Possible interpretations:
  - (a) Re-measure post-roster-change (219 vs prior count)
  - (b) Extend universe (add T2/T3 per #58 expansion)
  - (c) Different temporal slice
  - (d) Different methodology (per `feedback_minimum_fire_count_gate_before_cube` extensions)
- **Risk:** Without scope, "do B660 v2" is uncloseable.
- **Action:** Owner-clarify what v2 must measure that v1 didn't, OR mark RESOLVED-VIA-V1-SUFFICIENT.

---

## Critical Findings from Audit

1. **G4 instance-type discrepancy** (c7a.4xlarge vs c7a.8xlarge) — owner-decision required before AWS probe.
2. **#5 18-item list not consolidated** — Claude derivation task before owner review.
3. **#13 B660 v2 scope is a ghost item** — needs owner-clarification or RESOLVED-VIA-V1.
4. **#2 confirmed ghost** — RESOLVED via Council 10 verdict; CLAUDE.md banner needs update to reflect.

## Corrected Day 1 Plan (Updated from Council 9)

Pre-Day 1 (now): owner decisions on:
- G4 instance type
- #13 B660 v2 scope (or mark v1-sufficient)
- #2 banner update to RESOLVED-VIA-STAGE-4-WALK-OUTPUTS

Day 1 AM (Claude, ~2h):
- G1 SHA pin (5 min)
- G2 strategy count assert (1 min)
- G4 AWS probe (5 min) — once instance type decided
- G5 optimizer schema-pin dry-run launch (background ~30-60min)
- #5 derive the 18-item list from B814-B824 skip/xfail markers (~30min)
- #6 fire-bar matrix PID-guard fix + background re-launch (~30min Claude + 14h background)

Day 1 PM (Owner, ~30min):
- Review #5 18-item list (~20min)
- Review #11 Stage 5 SWAP #73-75 (~10min)

Day 2: Awaiting fire-bar matrix completion + pyramid green confirmation + optimizer schema-pin verdict.

Day 3: R5 launch trigger if all gates green.

**Realistic timeline post-audit: 2-3 days, NOT 5-7 days.** The audit revealed less work than Council 9 assumed (#2 ghost; #5 list-derivation cheap; #11/G4/G5 small).

---

## Owner-Decision Queue (Surfaced for Owner)

1. **G4:** R5 instance type — c7a.4xlarge (launch script) or c7a.8xlarge (Council 7 plan)?
2. **#13:** B660 v2 scope — what does v2 measure that v1 didn't? OR mark RESOLVED-VIA-V1-SUFFICIENT.
3. **#2 banner update:** Approve CLAUDE.md banner update marking step (ii) RESOLVED-VIA-STAGE-4-WALK-OUTPUTS per Council 10.

Once these 3 decisions land, Claude can execute Day 1.
