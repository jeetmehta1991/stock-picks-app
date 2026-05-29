# EXECUTION_QUEUE.md — Project-level sequential execution queue

**Owner directive 2026-05-29 (Batch 432):** *"We have been jumping all over the place and the items get missed. Lets bring order to the chaos."*

**Owner directive 2026-05-29 (Batch 444, lifecycle clarification):** *"Resolved items need to go down in the queue after being tagged as resolved. If needs a new iteration, needs be tagged as reopened and to be moved to top of queue. Add findings to the queue document as well. Note that such items need to be added in the queue document at each turn! This is mandatory!!!"*

**Purpose.** Single ordered list of the next project-level execution items. The **top of the queue is the next thing Claude executes**. Items can be reordered, but whatever sits at the top still executes next. This is the project-level analogue of per-session todos — it survives across sessions.

**Distinction from todos.** TodoWrite tracks in-session task state for *one* conversation. This queue tracks *project-level* obligations across sessions. A todo is "what am I doing in this conversation"; a queue item is "what is the project's next milestone."

---

## Rules

1. **Top item is next execution.** When work is needed and the queue is non-empty, the top `PENDING` (or `REOPENED`) item runs next.
2. **Mandatory update each turn (CHECKLIST #94).** Every turn that produces meaningful changes — INCLUDING newly-discovered findings, bugs, follow-ups — must end with a queue sweep. Failure to update = non-compliance. Discoveries become queue items the SAME turn they're discovered, not "next time".
3. **Reorder freely.** Owner or Claude can reorder via Edit. The new top runs next.
4. **DEFERRED keeps its position.** A `DEFERRED` item is skipped *without losing its slot*. The next non-deferred `PENDING` item runs first; the deferred item stays where it was so it surfaces again next time the queue is consulted.
5. **RESOLVED moves to the bottom of the active queue (not deleted).** When an item is finished, tag it `RESOLVED` and move it to the end of the active queue table (with the resolution batch / commit / one-line outcome in Notes). Keeping it visible in the active queue — not just a log line — makes the resolution traceable when the same area is touched later. Only TRULY archived items (never coming back) move to the Completed log section.
6. **REOPENED moves to the top.** If a RESOLVED item needs another iteration (regression, incomplete fix, new evidence), tag it `REOPENED` and move it to row #1 of the active queue. Update Notes with what changed.
7. **Status enum.**
   - `PENDING` — queued, not yet started.
   - `IN_PROGRESS` — actively being worked on this session.
   - `BLOCKED` — cannot proceed without an external unblock (waiting on owner / external system / dependency); explain blocker in Notes.
   - `DEFERRED` — owner-directed skip-without-loss; retains queue position.
   - `RESOLVED` — finished + moved to bottom of active queue. Stays visible.
   - `REOPENED` — was RESOLVED, surfaced as needing another iteration; moves to top.
   - `DONE-ARCHIVED` — truly done, never coming back; moved out of active queue into Completed log.
8. **One IN_PROGRESS at a time.** Like TodoWrite, only one item is `IN_PROGRESS` at any moment so the focus is unambiguous.
9. **Item identifiers stable.** Use a short kebab-case slug per item (`smc-silent-failure-rootcause`) so the same item is referenceable across turns even after reorder.
10. **No silent drops.** If an item is removed without RESOLVED tag, explain the reason in the Completed log (e.g., `dropped — superseded by Y`).
11. **Owner authority.** Owner can add, reorder, defer, resolve, reopen, or drop any item by message. Claude cannot drop an item without owner instruction.
12. **Findings become items immediately.** Anything discovered in a status report ("X was supposed to drop but didn't / Y stayed at 100 / Z needs investigation") becomes a queue row that same turn. Don't let findings dangle in chat history.

---

## Active queue (top = next; RESOLVED items sink to the bottom of this table, not removed)

| # | Slug | Item | Status | Notes |
|---|---|---|---|---|
| 1 | `cell-count-static-100-r3-finding` | Investigate why L2 cell count stayed at 100 in R3 (Batch 442 prediction wrong) | PENDING | R3 finding: Batch 442 predicted L2 cell count would RISE with Batches 414/415/416 active (degenerate-cell-filtering theory). It didn't — R3 produced 100 cells, same as R2. 32 cells turned over (new + retired) but total held flat. Some other filter mechanic is at play in `optimize_strategies_from_cube.py::analyze_exit_methods`. Action: read the L2 build path in detail (cube replay → groupby → n filter); count how many candidate cells exist BEFORE the n≥5 filter; identify the actual binding constraint. If it's `--no-portfolio-cap` capping trades-per-cube vs trade count being naturally that flat. |
| 2 | `skipped-bucket-static-47-r3-finding` | Investigate why SKIPPED_AT_ENGINE bucket barely moved (48 → 47) in R3 | PENDING | R3 finding: `--no-portfolio-cap` + `--no-event-suppression` should have collapsed SKIPPED if those gates were the main blockers. Staying at 47 means the remaining cause is structural — liquidity floor (DEC-321/366 ADV minimums) or `tier_too_low` from `_assign_confidence_tier`. Action: open `output_batch395_final/skipped_trades.csv`, group by `skip_reason`, count per reason; for the 47 strategies in this bucket, identify which reason dominates each. Then propose per-strategy tier-move or liquidity-floor tuning. |
| 3 | `smc-silent-failure-rootcause-r3-finding` | Inspect Batch 416 silent-producer engine logs for SMC root cause | PENDING | R3 finding: PRODUCER_LAYER_ZERO_LIKELY stayed at 6 (all SMC strategies). Batch 416 wired `_log_silent_producer_failure` at the `smc_ict` call site to surface the AWS-environment failure mode — but the logs need to be inspected. Action: download `engine.log` from S3 / the cube AMI; grep for `_log_silent_producer_failure` lines; first SMC failure should contain the exception class + traceback. Then fix the AMI/numba/smartmoneyconcepts install issue and queue R4. |
| 4 | `cube-cell-metrics-expansion` | Expand L2 cell schema with 5 tiers of additional metrics (~26 new fields) | PENDING | **Blocked-by:** items #1, #2, #3 (R3 findings) — implement after the 3 investigations close so we know the cube is healthy before adding columns. **Scope (per owner Batch 445 directive):** Tier A (already in metrics.py, surface to L2): sortino / calmar / deflated_sharpe / sharpe_at_5/10/20bps / avg_mae / avg_mfe / mfe_mae_ratio / exit_efficiency / hold_days_median/std/skew / survivorship_sharpe / capital_weighted_sharpe. Tier B (slice existing trade_log columns): wr_with/without_smart_money / wr_by_vix_bucket / wr_by_days_to_earnings / wr_by_event_window. Tier C (new computation): sharpe_ci_95 / oos_sharpe / is_oos_decay / effective_n. Tier D (composite scores): sqn / k_ratio / mar. Tier E (risk mgmt): kelly_fraction / cvar_5pct / risk_of_ruin. **Ship in tier order** (A → B → C → D → E). **Each tier must include the glossary + interpretation rule inline in Tab 13** (per owner Batch 445: "Ensure that you have a glossary and interpretation as stated above in the tab itself for easy reference"). The preview glossary already lives at the bottom of Tab 14 Reference (Batch 445). |
| 5 | `cube-walk-forward-r3` | Run `scripts/walk_forward_batch414_cells.py` on R3 cube cells | PENDING | DEC-505 4-fold expanding-window walk-forward on R3 data. Prior R2 result LOCKED 1A-α gate at OOS Sharpe 0.419. If R3 produces a cell with OOS Sharpe ≥ 0.7 in ≥1 regime, gate opens and Phase 1B-α $300 Haiku budget becomes eligible. **Note:** queue item #4 Tier C consumes the output of this — wire OOS Sharpe back into L2 cells. |
| 6 | `cube-analyst-overlay` | Emit single-run analyst overlays from merged cube trade log so all dashboard tabs have data | PENDING | Cube engine writes per-cell artifacts but skips `equity_curve.parquet`, `portfolio_metrics.json`, `improvements_summary.json`, `strategy_regime_matrix.json`, walk-forward, smart-money, bootstrap, congressional. Need an "analyst" pass over `output_batch395_final/trade_log.csv` calling existing functions in `backtest/results/metrics.py` + `improvements.py` to write the missing JSONs. Then Overview / Tab 4 Equity / Tab 5 Walk-fwd / Tab 6 Smart-$ / Tab 2 Regime stop showing "No data". |
| 7 | `post-run-validation-rc1` | Investigate post-run validation rc=1 from R3 merge | PENDING | Merge bg `bd01668y9` log printed `[FAIL] post-run validation rc=1` without detail (output not captured). Files in place; S3 upload completed. Likely a validation script in `aws_batch395_merge.py` invocation chain. Action: find the validation script, re-run it on `output_batch395_final/` standalone to surface the actual failure reason. |
| 8 | `1a-alpha-gate-decision-r3` | Owner decision on 1A-α gate state after R3 walk-forward | PENDING | Requires item #5 complete. Gate currently LOCKED at OOS Sharpe 0.419 < 0.7. If R3 opens it: $300 Phase 1B-α budget eligible. If still locked: loop back to entry-side optimization (Dim A thresholds / Dim B compound restructure) and queue R4. |
| 9 | `phase-1b-alpha-launch` | Phase 1B-α agent overlay run ($300 Haiku budget) | DEFERRED | Owner-gated behind 1A-α gate (item #8). Scope: agents-only validation per owner directive 2026-05-26 — strategies and exits decided in Phase 1A-β. |
| 10 | `25-negative-sharpe-deprecation` | 25 all-negative-Sharpe strategies — deprecation decision | DEFERRED | Per owner standing rule `project_no_apriori_strategy_pruning`: empirical-only. Awaits R3+ per-cell verdicts (after item #5 walk-forward) so we have OOS data not just IS. |
| 11 | `unarchive-list-eval` | Owner unarchive-list evaluation (currently archived but might come back) | PENDING | Owner mentioned considering unarchiving a few; awaits owner pick. List of 21 archived in `archive/2026-05-28-pre-1a-alpha-gate/docs/`. |
| 12 | `cube-merge-rebuild-r3` | R3 cube re-run COMPLETE + merge + optimizer + rebuild | RESOLVED | All 5 batches `_COMPLETE` 2026-05-29; merge bg `bd01668y9` succeeded; optimizer ran into `output_optimization_candidates_2026_05_29/`; dashboard rebuilt (commit `a7d2c0a4d`); Tab 16 Cube Diff populated; Tab 17/18 added (commit `3eb546b6e`). R3 trades = 29,360 (+201 vs R2). |
| 13 | `dashboard-batch445-verify` | Verify dashboard post-Batches 430/433/434/437/438/440/441/442/443/445 | RESOLVED | All shipped: cube-only source switch (437), tab readability fixes (430/433/434/438/440), Tab 16 Cube Diff (441/442), Tab 17 Iteration Rounds + Tab 18 Cell Cube Comparison + global round banner (443), Tab 14 navigation flowchart + Lens A/B explainer + cube-cell-metrics-expansion preview glossary (445). Hard-refresh dashboard to verify. Will REOPEN if owner reports specific tab issue. |

---

## Completed log (DONE-ARCHIVED — truly closed; most recent first; one line per item)

- 2026-05-29 — `execution-queue-create` — Created EXECUTION_QUEUE.md + CHECKLIST #94 (Batch 432). Owner directive: bring order to chaos.
- 2026-05-29 — `archive-prefetch-api` — Batch 431 (a8b53cfb0): archived PREFETCH_COVERAGE_AUDIT.md + API_AUDIT.md after activity-check verified no Python read/write code refs.
- 2026-05-29 — `dashboard-batch430-fix` — Batch 430 (1af03f282): fixed buildTable `$(window).ready` SyntaxError that killed all DataTable renders + added marked.js for Tab 10 + structured render for Tab 11.
- 2026-05-29 — `archive-impl-readiness-dashboard` — Batch 429 (577177432): archived IMPLEMENTATION_READINESS_DASHBOARD.md (self-superseded).
- 2026-05-28 — `archive-batch318-quant` — Batch 428 (f4191bb7f): archived BATCH_318_PROCESS_POOL_DESIGN + QUANT_CORRECTNESS_AUDIT_DEC_246.
- 2026-05-28 — `archive-sprint1-readme` — Batch 427 (91b7cd4cd): archived SPRINT1_POLYGON_PREFETCH_README (Sprint 1 → 0A rename).
- 2026-05-28 — `archive-audit-triage-post-may29` — Batch 426 (27c512aee): archived AUDIT_TRIAGE.md + POST_MAY_29_OPERATION_GUIDE.md.
- 2026-05-28 — `archive-dated-audits-gitignore` — Batch 425 (574205bce): archived 8 dated audit docs + .gitignore additions (`backtest/agents/cache/`, `/tmp_*`, `/vm_*`) + 4 root tmp orphans deleted.
- 2026-05-28 — `cleanup-prior-outputs` — Batch (ec9c7082b): removed 735 tracked files from 17 superseded `output_*` dirs (2.4M deletion lines).
- 2026-05-28 — `monitoring-framework-update` — Batch (cc9246445): doc-sweep monitoring framework L4 stdout buffering + AWS PATH prereq + pre-launch protocol.
- 2026-05-28 — `cube-shape-a-launch` — Batches 424 (948769bf2) + parallel orchestrator: launched Shape A 3 × c7a.8xlarge spot cube re-run; all 5 batches completed 2026-05-29.

---

## Cross-references

- `CHECKLIST.md` #94 — mandatory per-turn queue update (rule 2 above).
- `MONITORING_FRAMEWORK.md` — L0-L7 stack (cube run monitor sits in L4 layer).
- `PHASE_1A_BETA_STATUS.md` — Phase 1A-β living doc (Stage 1-6 batch ship list).
- `PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md` — locked 6-stage workflow.
- `archive/cube_rounds/rounds.json` — round-by-round registry (Batch 443) consumed by Tabs 17 + 18.
- `CLAUDE.md` HARD RULES — owner approval, no-new-md-without-approval (`feedback_no_write_only_md_files`), full-pyramid mandate (CHECKLIST #69/#93).
