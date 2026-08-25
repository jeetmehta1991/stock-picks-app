# DECISION PACKAGE — gate philosophy + the kill rule (B2182, S6-B2178c)

Two owner decisions, each with its measured case, its counter-case, and a recommendation.
Everything here derives from artifacts on disk with zero engine runs; every figure names its
source. The correlation analysis is output_audit/b2182_strategy_correlation.json (built by
scripts/build_strategy_return_correlation.py from the R5 production trade log, IS window only,
holdout untouched).

## Decision 1 — per-strategy Sharpe-1.0 gate vs portfolio-level validation

**The external feedback's claim:** individual Sharpes of 0.4–0.7 are normal; twenty of them at
pairwise rho 0.25 combine to portfolio Sharpe ~1.0, so the per-strategy gate that passed 3 of
219 filters for the wrong object.

**The measurement (B2182, executed 2026-08-25):** 183 strategies with ≥30 IS trades, 136,622
trades. Average pairwise rho **0.087** — the diversification the claim needs genuinely exists.
But the cross-sectional annualized Sharpe of the production streams is **mean −2.44, median
−1.97**: the average registered strategy LOSES money in-sample at the production-exit grain, so
the combination formula amplifies a negative — N=40 implies portfolio Sharpe **−7.4**. The
honest best case: the **positive-only shrunk-Sharpe subset has n=5** (vix_backwardation_long
0.51, donchian_breakout_long 0.48, pead_with_smart_money_long 0.45, htf_aligned_breakout_long
0.22, totm_long 0.16), rho 0.176, implying portfolio Sharpe **0.62** — under the 1.0 bar.

**Reading:** the portfolio reframe is arithmetically sound and empirically unavailable HERE —
the bottleneck is not gate philosophy but the sign of the cross-section. Combination cannot
rescue negative means; the binding constraint remains candidate quality/discovery, exactly the
First-Principles and Outsider council verdicts.

**Caveats, stated against my own conclusion:** (a) the streams use PRODUCTION exits
(trailing_stop dominates at 68%); the roster's graded cells use SELECTED exits and score
better — the −2.44 mean is partly an exit-configuration artifact, so the true selected-exit
cross-section sits somewhere between this and the grader's view; (b) the IS window contains the
2022–23 bear; (c) winner's-curse caveats cut BOTH ways — the five positives are the maximum of
183 noisy draws.

**RECOMMENDATION:** keep the per-strategy gate; do NOT move to portfolio-level admission on
this evidence. Re-run this analysis at selected-exit grain once ~20 strategies carry graded
cells (one command, zero engine runs) — that is the version that could genuinely re-open the
question.

## Decision 2 — the pre-registered kill rule

**Proposal:** a strategy whose family-pooled Step-1 grid sits entirely under the selection-noise
floor after ONE full-shape config is retired from the optimization backlog without appeal.

**The case:** smc_breaker_block_long consumed FIVE configs (~14 engine-hours) to reach the
verdict one config plus this rule would have delivered — best IS-CI-lo across all five: +0.259,
+0.129, +0.094, −0.140, −0.196 against the 0.333 floor (b2179_table_c_all5.md). The program's
own discovery-over-depth diagnosis predates configs four and five.

**The counter-case (recorded per L633):** one config is one draw of one universe-window pairing;
an unlucky window retires a real edge permanently, and the five-config record above spans a
mid-stream gate redesign, so even it is not five clean draws.

**RECOMMENDATION:** adopt with one appeal: retirement after one sub-floor full-shape config,
reversible only by an explicit owner re-open naming new evidence (a different regime window, a
producer fix, a redesigned gate). This is a GATE CHANGE and requires your approval per the
standing rule — nothing is armed until you rule.

## What was NOT adopted from the feedback, for the record

TPE/Bayesian search, NSGA-II, MCPT, and the vectorbt rebuild — refusal reasons in queue row
S6-B2178-FEEDBACK-EXTRACTION. DSR stays a diagnostic column per your B1436 demotion. The SPP
median-vs-max column ships in Table C (B2182); delete-the-parameter is now a standing design
principle for new producers (plan §6.7).
