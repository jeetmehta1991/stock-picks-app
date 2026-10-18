# B3203 - RCA: why strategies are not passing the tightening workflow

Owner ask (2026-10-18, verbatim): "Lets take a step back and assess by these strategies are not
passing. Do a deep RCA and identify if any issues in our tightening workflow and strategy. Should
we be going anything else even if its curve fitting?"

Evidence classes marked per claim: EXECUTED (run this turn), READ (file:line this turn),
DERIVED (arithmetic shown), or stale-with-source.

## 1. The funnel, measured

| stage | population | result | evidence |
|---|---|---|---|
| R5 full-universe run | ~196 distinct strategies graded | 2-3 organic qualifiers (~1-1.5 pct) | stale-with-source: R5 merged cube, owner 2026-09-03 ruling context |
| Step-2 admissions to date | 16 | 12 of 16 GRID-SELECTED-OWNER-RULED; 3 of 16 IS-HOLDOUT-INVERSION; 1 PEEKED; 1 ONE-EPISODE-HOLDOUT; 2 of 16 carry none of grid-selected/peeked/inversion (smc_breaker_block_long, pead_long_high_yoy_growth_only) | EXECUTED: counted from phase_1b_step2_admissions.json this turn |
| Status lanes | 225 registered | 16 admitted / 41 stalled-campaign / 130 not-started / 3 closed-negative / 4 owner-closed (with npoc) / 8 pruned-duplicate | READ: STRATEGY_OPTIMISATION_STATUS.md Totals (pre-rebuild: owner-closed 3) |
| Last 3 full campaigns | three_white_soldiers, pairs, naked_poc | 2 admitted on BREADTH lines, both label-carrying (tws IS-HOLDOUT-INVERSION IS -0.421; pairs ONE-EPISODE-HOLDOUT + CONTROL-THIN); npoc closed | READ: campaign log J/K sections + admissions json |

## 2. Root causes, ranked by strength of evidence

**RC1 - most base signals have no edge for tightening to find.** Tightening SELECTS a subset of a
strategy's fires; a subset of a no-edge signal is noise with fewer trades. Direct measurement on
npoc (EXECUTED/READ): the own-knob offline grid's best cell 0.620 sits BELOW the 100-permutation
null's q95 of 0.917 (p 0.6733, K.4) - the search surface is statistically flat - and all 12 engine
Step-1 configs graded below production's own IS Sharpe 0.558 (best 0.523, K.14). Base rate: R5's
~1-1.5 pct organic qualification across ~196 strategies. The terrain - S&P-500 daily bars,
2022-2026 - is the most heavily mined corner of public markets; literature patterns there are
mostly arbitraged residue.

**RC2 - the 1-year holdout Sharpe >= 1.0 gate is a weak discriminator at our sample sizes
(DERIVED, Lo 2002: SE(annualised SR over T years) ~ sqrt((1 + SR^2/2)/T)).** On a 1-year holdout:
true SR 0.0 -> SE 1.00 -> P(printed SR >= 1.0) ~ 16 pct; true SR 0.7 -> SE 1.12 -> P ~ 39 pct;
true SR 1.0 -> P = 50 pct. Pass likelihood ratio (true-0.7 vs noise) ~ 2.4 : 1. So the gate
rejects ~61 pct of genuinely deployable 0.7-Sharpe strategies AND passes ~1 in 6 pure-noise
candidates - which predicts BOTH the mass failures and the 3 of 16 inversion-labelled admissions.
The internal holdout nulls (e.g. npoc K.8 family-best p 0.236 = chance-shaped) are the mechanism
that catches the noise passes; they are working as designed.

**RC3 - depth is exhausted; breadth is where passes come from, and breadth is where multiplicity
lives.** 3 of 3 recent campaigns' own-knob (depth) searches found nothing beyond noise; the two
admissions came from companion screens over ~522 candidate signals (BH-FDR at screen, one holdout
read), and both carry selection-risk labels. npoc's breadth followed the identical shape (IS
p 0.0099) and died at the holdout read (0 of 425) - the expected outcome of the same process when
the luck does not hold.

**RC4 - design tension: per-regime philosophy, pooled admission gate (READ: config.py
PASSING_CRITERIA; roster_core.py LIVE_GATES).** The system's stated design deploys per regime
(criterion #11: PASS in >= 1 regime at the 0.5 per-regime threshold - min_sharpe_per_regime in backtest/config.py, B1387; the CLAUDE.md table said 0.7 until this batch, stale since B1387), but the six live Step-2
gates use POOLED holdout Sharpe >= 1.0 - a regime-specific strategy is diluted by regimes it was
never meant to trade in.

**RC5 - engine compute is spent after the verdict is knowable.** npoc's depth flatness (p 0.6733)
was measured OFFLINE on 2026-10-14, before the ~38 engine-hours of Step-1 chains ran (12 configs x
2.6-4.2 h, K.12-K.14). The workflow permitted the engine leg without surfacing "the null already
prices this at noise" as a blocking recommendation.

## 3. Should we curve-fit?

No. The programme's own record shows what deliberate fitting buys: the rows closest to it -
grid-selected lines, re-read holdouts - are exactly the admissions carrying
IS-HOLDOUT-INVERSION / DISCLOSED-RE-READ / ONE-EPISODE labels, i.e. the ones most likely to be
chance (RC2: a noise candidate passes ~16 pct of the time, so searching more candidates
mechanically manufactures passes). Those failures surface later, in Stage-3 paper trading, at
full cost and delay. The yield problem is real, but the fix is changing the UNIT and VENUE of the
test, not the honesty of it.

## 4. Options (each is an owner decision; none shipped)

| id | option | what it buys | case against |
|---|---|---|---|
| S6-B3204 | **A. Portfolio-unit evaluation now** - build the blended Phase-1B portfolio from the 33 deployable (+ graded near-misses) and grade Sharpe/MDD at the PORTFOLIO level, per the B1436/B1437 rulings. DERIVED: SR_p = n x SRbar / sqrt(n + n(n-1) x rhobar); 20 strategies at true 0.4, rhobar 0.10 -> ~1.05; rhobar 0.25 -> ~0.75. Zero engine hours - the cubes exist | correlations estimated in-window are optimistic; needs a holdout-window portfolio read before anything deploys |
| S6-B3205 | **B. Per-regime admission lane** - admit at the pre-registered per-regime threshold (0.5, best regime; min_sharpe_per_regime, backtest/config.py, B1387), deploy only in-regime. Not curve fitting: criterion #11 has been in the passing criteria since Pass 53 | per-regime holdout samples are small (the 15-trade floor will bind often); adds regime-classification risk at deploy time |
| S6-B3206 | **C. Permutation-null early-stop as a mandatory pre-engine gate** - offline Step-1 null p > 0.20 on the depth surface refuses the engine chain absent an explicit owner override. Measured saving: ~38 engine-hours on npoc alone | the offline null sees only persisted-magnitude knobs; a resim-only knob could hide an effect it cannot price (npoc's P1 ema_span was that class - it, too, was flat) |
| S6-B3207 | **D. Recalibrate the holdout gate** - e.g. holdout ci_lo > 0 with n >= 30 in place of point-Sharpe >= 1.0, or a 2-year holdout (re-cutting the IS/HO boundary) | any loosening admits more noise - only safe if A becomes the binding downstream risk control; a boundary re-cut invalidates banked reads |

**Recommendation: A, then C, then B; D only alongside A.** A changes the question to the one the
programme actually needs answered (does the BOOK clear the bar), costs nothing in engine hours,
and makes D safe to consider. C stops the known waste. B uses machinery already specified.

Generated B3139q-r72c, 2026-10-18. Sources named inline; admission label counts and the npoc
figures re-derived this turn.

CORRECTED B3139q-r72d: the per-regime Sharpe floor is 0.5 (min_sharpe_per_regime, backtest/config.py, owner-approved B1387), not the 0.7 two sites above first said - the stale source was CLAUDE.md criteria row 10, fixed and pinned (test_b3208) in the same batch. Decision B is accordingly CHEAPER than first stated.

## Status (B3139q-r72h, 2026-10-18)

- A (S6-B3204): EXECUTED and CLOSED on the owner's word ("S6-B3204 (A) close approved").
  output_audit/b3204_portfolio_eval.json: in-sample book Sharpe 0.129 vs SPY 0.594 over the same
  window; holdout 4.679 vs 1.972 (commit b5a19f49f). The selection-free reading sits below holding SPY.
- C (S6-B3206): EXECUTED - the depth-null declaration gate inside launch_refusals, the no-surface case
  per the owner's ruling "A" (this batch).
- B (S6-B3205), D (S6-B3207): OPEN, the owner's word; the A result argues against loosening admission.
