# R5 Pre-Committed Sharpe-Band Decision Tree

**Status:** OWNER-APPROVED (Batch 882, 2026-06-17)
**Authority:** Council 7 verdict (this session); owner directive "R5 -> agents -> papertrade, no changes"
**Purpose:** Lock the post-R5 decision rule BEFORE R5 launches, per Outsider Council 7: *"If you can't write the decision tree in 10 minutes without convening another council, you're not ready to spend the $9.30."*
**Falsifiability:** Any deviation from these branches post-R5 must be logged as an explicit override commit referencing this file's SHA at decision time.

---

## Decision Tree

R5 outputs an OOS Sharpe verdict per Stage 3 optimizer's selected (strategy x exit) cells. The branch below is read AS-IS at result time; the rule is the rule.

| R5 OOS Sharpe band | Action | Budget commit |
|---|---|---|
| **>= 0.7** | PROCEED to Phase 1B-alpha agents over R5 PASS cells | Full $300 Haiku budget |
| **0.5 - 0.7** (exclusive of 0.7) | PROCEED to agents over $50 stratified sub-sample of R5 PASS cells; full $300 commit gated on sub-sample lift >= 0.05 absolute Sharpe vs cube baseline | $50 first; $300 conditional |
| **< 0.5** | STOP. Defer to Stage 4 walks completion (Cluster B-E unwalked per Council 4 audit) BEFORE R6 retry. No agent spend. | $0 |
| **Zero PASS cells** (Bonferroni m=5,694 yields 0 cells passing per-regime gates) | STOP. Do not spend $300 on empty cell set. Architectural review required before R6. | $0 |

---

## Mid-R5 Abort

Per Executor Council 7 + `feedback_monitor_intermediate_counts`:
- Arm Monitor for per-100-day cumulative-trade-count vs B395 baseline
- ABORT R5 if >2x deviation at 15% completion (~30-50 day mark)
- ABORTed R5 reverts to "STOP / Stage 4 completion" branch above (treated as < 0.5 outcome)

## Reputational Caveat

Per Contrarian Council 7 + Council 4 audit: the OOS Sharpe verdict R5 produces is on a CONTAMINATED holdout (474 grep matches for 2025/2026 dates in EXECUTION_QUEUE.md alone; 800+ batches of researcher-degrees-of-freedom across the 2025-2026 window). Any external citation of R5 OOS Sharpe MUST disclose this contamination. Internal action proceeds per the table above; external claims do not.

## Override Protocol

If owner decides post-R5 to deviate from the tree:
1. Commit an explicit override file `output_audit/r5_override_<batch>_<reason>.md`
2. Reference this file's SHA at decision time
3. State why the band's pre-committed action is being overridden
4. Acknowledge the override as a Council 8-equivalent decision

No silent deviation. The point of pre-committing is that the rule is the rule until explicitly overridden in writing.

---

## Council Provenance

- **Council 7 (this session):** synthesized execution plan + this decision tree; 5 advisors converged on pre-committed Sharpe bands as the bottleneck (not the cube)
- **Council 4:** documented holdout contamination (474 grep matches)
- **Owner directive (this session):** "R5 -> agents -> papertrade, no changes" -- overrules Councils 2/3/4/5 methodology proposals

## Signatures

- **Owner:** approved Council 7 verdict 2026-06-17 (chat directive "Approved")
- **Claude:** authored per Council 7 verdict; committed as Batch 882
- **Timestamp:** 2026-06-17 (commit timestamp authoritative per git log)

---

*This file is the governance contract for R5. It does not change unless explicitly overridden via the protocol above.*
