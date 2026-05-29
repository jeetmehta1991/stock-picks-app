# EXECUTION_QUEUE.md — Project-level sequential execution queue

**Owner directive 2026-05-29 (Batch 432):** *"We have been jumping all over the place and the items get missed. Lets bring order to the chaos."*

**Purpose.** Single ordered list of the next project-level execution items. The **top of the queue is the next thing Claude executes**. Items can be reordered, but whatever sits at the top still executes next. This is the project-level analogue of per-session todos — it survives across sessions.

**Distinction from todos.** TodoWrite tracks in-session task state for *one* conversation. This queue tracks *project-level* obligations across sessions. A todo is "what am I doing in this conversation"; a queue item is "what is the project's next milestone."

---

## Rules

1. **Top item is next execution.** When work is needed and the queue is non-empty, the top `PENDING` (or `DEFERRED` re-activated) item runs next.
2. **Mandatory update each turn (CHECKLIST #94).** Every turn that produces meaningful changes must end with a queue sweep — advance status, mark complete, add newly-discovered items, surface deferrals. Failure to update = non-compliance.
3. **Reorder freely.** Owner or Claude can reorder via Edit. The new top runs next.
4. **DEFERRED keeps its position.** A `DEFERRED` item is skipped *without losing its slot*. The next non-deferred `PENDING` item runs first; the deferred item stays where it was so it surfaces again next time the queue is consulted.
5. **DONE moves to the completed log.** Once done, remove from the active queue and append a one-line entry to the completed log (most recent first).
6. **Status enum.**
   - `PENDING` — queued, not yet started.
   - `IN_PROGRESS` — actively being worked on this session.
   - `BLOCKED` — cannot proceed without an external unblock (waiting on owner / external system / dependency); explain blocker in Notes.
   - `DEFERRED` — owner-directed skip-without-loss; retains queue position.
   - `DONE` — finished; move to completed log and remove from active queue.
7. **One IN_PROGRESS at a time.** Like TodoWrite, only one item is `IN_PROGRESS` at any moment so the focus is unambiguous.
8. **Item identifiers stable.** Use a short kebab-case slug per item (`cube-batch-5-merge`) so the same item is referenceable across turns even after reorder.
9. **No silent drops.** If an item is removed without completing, explain the reason in the completed log (e.g., `dropped — superseded by Y`).
10. **Owner authority.** Owner can add, reorder, defer, or drop any item by message. Claude cannot drop an item without owner instruction.

---

## Active queue (top = next)

| # | Slug | Item | Status | Notes |
|---|---|---|---|---|
| 1 | `cube-batch-5-merge` | Phase 1A-β cube re-run batch_5 completion + merge via `aws_batch395_merge.py` | IN_PROGRESS | batch_5 ~60% complete at 01:16Z 2026-05-29; ETA ~30-40 min. Then download to `output_batch395_final/` + per-cell forensic refresh. |
| 2 | `cube-optimizer-rerun` | Re-run `scripts/optimize_strategies_from_cube.py` on fresh cube | PENDING | Stage 3 of locked workflow. Produces refreshed `output_optimization_candidates_2026_05_28/` JSONs + `optimization_summary.md`. |
| 3 | `cube-walk-forward` | Run `scripts/walk_forward_batch414_cells.py` on fresh cube cells | PENDING | DEC-505 4-fold expanding-window walk-forward. Prior result LOCKED 1A-α gate at 0.419 OOS Sharpe; this re-run uses Batches 414/415/416/421 fixes. |
| 4 | `smc-silent-failure-rootcause` | Surface SMC silent-failure root cause from L2 logs in fresh cube engine output | PENDING | Batch 416 instrumented producer call sites; SMC keys absent on prior cube. AWS-environment-specific failure mode expected in `_log_silent_producer_failure` log lines. |
| 5 | `dashboard-batch430-verify` | Verify all tabs render post-Batches 430 + 433 | BLOCKED | **Batch 433 (1de4d213c) fixed Tab 2 Regime** — owner screenshot showed verdict cells empty because renderer read top-level entry keys (best_regimes / regime_verdicts / overall_win_rate / total_trades / passes_all) AS regime names; actual verdicts are nested under `entry.regime_verdicts`. Cells now read the nested location + 3 summary columns (Trades / Win % / Passes) appended. **Owner action:** hard-refresh again. Confirm: Tab 2 Regime shows colored PASS / FAIL / INSUFFICIENT_DATA cells with regime-year names (covid_crisis_2020, etc.) as columns + 3 summary cols on right. Other tabs (1, 3-13, Exits, Trades) should also render after refresh. If any still blank: F12 → Console errors. |
| 6 | `1a-alpha-gate-decision` | Owner decision on 1A-α gate state post-fresh-cube + walk-forward | PENDING | Requires items 1-4 complete. Gate currently LOCKED at OOS Sharpe 0.419 < 0.7. If reopens: $300 Phase 1B-α budget eligible. If still locked: loop back to cube optimization. |
| 7 | `phase-1b-alpha-launch` | Phase 1B-α agent overlay run ($300 Haiku budget) | DEFERRED | Owner-gated behind 1A-α gate (item 6). Scope: agents-only validation per owner directive 2026-05-26 — strategies and exits decided in Phase 1A-β. |
| 8 | `25-negative-sharpe-deprecation` | 25 all-negative-Sharpe strategies — deprecation decision | DEFERRED | Per owner standing rule `project_no_apriori_strategy_pruning`: empirical-only. Awaits fresh-cube per-cell verdicts (item 3). |
| 9 | `unarchive-list-eval` | Owner unarchive-list evaluation (currently archived but might come back) | PENDING | Owner mentioned considering unarchiving a few; awaits owner pick. List of 21 archived in `archive/2026-05-28-pre-1a-alpha-gate/docs/`. |

---

## Completed log (most recent first; one line per item)

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
- 2026-05-28 — `cube-shape-a-launch` — Batches 424 (948769bf2) + parallel orchestrator: launched Shape A 3 × c7a.8xlarge spot cube re-run; batch_1/2/3/4 _COMPLETE; batch_5 in progress.

---

## Cross-references

- `CHECKLIST.md` #94 — mandatory per-turn queue update.
- `MONITORING_FRAMEWORK.md` — L0-L7 stack (cube run monitor sits in L4 layer).
- `PHASE_1A_BETA_STATUS.md` — Phase 1A-β living doc (Stage 1-6 batch ship list).
- `PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md` — locked 6-stage workflow that items 1-4 implement.
- `CLAUDE.md` HARD RULES — owner approval, no-new-md-without-approval (`feedback_no_write_only_md_files`), full-pyramid mandate (CHECKLIST #69/#93).
