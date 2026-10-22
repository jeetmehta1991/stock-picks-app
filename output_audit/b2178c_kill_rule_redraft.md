# DECISION PACKAGE, REDRAFTED - the kill rule and the gate philosophy (S6-B2178c, B3139q-r102)

Written for the owner. It replaces, for decision purposes, output_audit/b2182_gate_philosophy_decision.md
(2026-08-26), which stays on disk as the record of what was asked then. The council's verdict at B3139
was that the old package was stale and had to be redrafted before any re-raise. The re-raise trigger
has now fired: the owner ruled on 2026-10-22, verbatim "Addendum Approve all your recommendations", over
a recommendation that naked_poc_retest_long's closed programme counts as the second programme at the
institutional shape.

## What changed since the old package

| Old package said | Now |
|---|---|
| "Sub-floor" meant below the 0.333 selection-noise floor | That floor was retired in its entirety on 2026-08-30 (S6-B2409). The rule as written has no threshold left |
| Its example case was smc_breaker_block_long: 5 configs, best is_ci_lo +0.259 against the 0.333 floor | smc_breaker_block_long was ADMITTED on 2026-08-30 (S6-B2410), at swing 50 / span 50, from a later config whose Step-1 rank-1 row read is_ci_lo +1.250 (output_audit/TABLE_D_b2197_final.md) |
| The selected-exit correlation re-run is "one command, zero engine runs" | scripts/build_strategy_return_correlation.py takes no arguments and reads only the production-exit trade log; a selected-exit mode does not exist (PROPOSED-NOT-BUILT) |

## Decision 2 - the pre-registered kill rule (the decision this ticket holds)

**The rule as proposed:** a strategy whose Step-1 grid sits entirely below the floor after ONE
full-shape config is retired from the backlog, re-openable only by an explicit owner word naming new
evidence.

**What the three programmes that reached that condition went on to do:**

| programme | its Step-1 record | outcome |
|---|---|---|
| smc_breaker_block_long | first config cfg1, best is_ci_lo +0.129 (output_audit/b2179_table_c_all5.md) - below the floor | ADMITTED 2026-08-30 (S6-B2410) from the swing-50 band, a later config |
| institutional_committed_growth_long | 16 configs, 5 of 15 clean positive, nothing clearing the bar (S6-B2178c, 2026-09-04) | ADMITTED 2026-09-10 (B2664) from the companion/knob grid, review tag GRID-SELECTED-OWNER-RULED |
| naked_poc_retest_long | 12 Step-1 configs, best is_ci_lo 0.262, 12 of 12 below production's IS Sharpe 0.558; one Step-2 holdout read cleared 0 of 425 cells (campaign log K.14-K.15) | CLOSED by the owner's word 2026-10-18: "Given low sharpe i do not think there is a likelyhood that this strategy will pass" |

So 2 of the 3 strategies the rule would have retired after one config were later admitted, and the
third was closed by the owner's own judgment after 12 configs, without the rule. The rule's own example
is one of the two admissions.

**Options:**

- **(a) DROP the kill rule.** Campaign closure stays the owner's word, as it was for naked_poc_retest_long
  and bollinger_lower. Recorded with the table above as the reason.
- **(b) Replace retirement with a checkpoint.** After N Step-1 engine configs with no Step-2 qualifier,
  the campaign stops and returns to the owner for a continue-or-close word - a prompt, never an
  automatic retirement. N is the owner's to set; nothing is armed until then. This is a process change
  and needs its own build (a counter in the campaign register and a refusal at launch).
- **(c) Keep deferring.**

**RECOMMENDATION: (a).** The evidence runs against the rule: on the only population measured, it would
have retired 2 of 3 strategies that went on to be admitted, and the one programme that genuinely ended
negative was closed by the owner's word without it. Option (b) saves engine hours only where the owner
would not have closed a campaign anyway, and that saving is unmeasured.

## Decision 1 - per-strategy gate vs portfolio-level validation (deferred 2026-08-25)

The owner deferred it as premature until roughly 20 strategies carry graded, selected-exit results.
**That condition is met:** 23 distinct strategies on the Phase 1B roster carry one - 16 Step-2
admissions and 7 funnel cells (scripts/phase1b_membership.py, run 2026-10-22). The measurement the old
package named as its next step - the correlation analysis at selected-exit grain - is not built: the
script reads production exits only.

- **(a) Build the selected-exit mode and run it** (zero engine runs; the streams come from each admitted
  line's own Step-2 cube at its selected exit). Cost UNMEASURED until the per-cube trade filter is
  written; ticketed if chosen.
- **(b) Keep deferring.**

**RECOMMENDATION: (a)** - the condition the owner set has arrived, and the question it re-opens
(whether the admitted lines together clear 1.0 as a portfolio) is the question Phase 1B asks next.
This changes no admission and no gate; it measures.
