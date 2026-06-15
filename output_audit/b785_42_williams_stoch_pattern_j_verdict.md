# B785 -- #42 Williams-Stoch Pattern J phi-correlation -- VERDICT: REFUTED at fire-stream level

# per CHECKLIST #77 + #108 + #94 + #105 + #107
# Source: output_audit/fire_bar_similarity_cluster_a_demo.parquet (B760 demo 50 tickers x 1yr 2024)
# Source: B709 PEAD-restore phi-correlation methodology
# per memory: feedback_no_a_priori_strategy_pruning.md + feedback_no_prior_edge_consolidate_before_tune.md

## Council reviewer claim (B766 #42)

> "Williams %R is algebraically near-identical to Stochastic %K by construction (both normalize price location within a lookback range; differ only in inversion sign and divisor). A-9 strat_williams_r_oversold + A-6 strat_stoch_oversold are likely Pattern J duplicates the doc didn't pair. Run B709 phi-correlation precompute on A-6 vs A-9 fire-sets specifically. Likely deletion candidate."

## CHECKLIST #108 pre-flight

- (a) **Hypothesis:** phi-correlation on fire-bar streams >= 0.70 -> Pattern J consolidation candidate; >= 0.85 -> deterministic-duplicate / DELETE per B722 hull_rsi precedent. <0.70 -> REFUTED.
- (b) **Fire-count projection:** ANALYTICAL test only; no gate-modification yet. (No code changes.)
- (c) **Validation plan:** read existing B760 fire-bar similarity Parquet output; extract Williams-Stoch pair; compare against 0.70 / 0.85 thresholds.
- (d) **Literature/empirical precedent:** B709 PEAD-restore (phi=0.297 -> RESTORE both); B722 hull_rsi DELETE (phi >= 0.85 deterministic-duplicate).

## Empirical result (B760 demo: 50 tickers x 1yr 2024)

| Direction | n stoch fires | n williams fires | n intersection | Jaccard | **phi** | Verdict |
|---|---:|---:|---:|---:|---:|---|
| **LONG** | 10 | 464 | 2 | 0.0042 | **+0.024** | REFUTED (<< 0.70) |
| **SHORT** | 6 | 149 | 0 | 0.0000 | **-0.002** | REFUTED (<< 0.70) |

**Both directions phi << 0.70 Pattern J consolidation threshold.** Far below 0.85 DELETE threshold.

## Why council was right about signals but wrong about strategies

Council's underlying observation (correct): Williams %R and Stochastic %K are algebraically similar:
```
Williams %R = (highest_n - close) / (highest_n - lowest_n) * (-100)
Stochastic %K = (close - lowest_n) / (highest_n - lowest_n) * 100
```
They are SAME calculation up to sign and offset; the signal series are linearly inverse.

**But Pattern J operates at the STRATEGY FIRE-STREAM level, not the underlying-signal level.**

strat_stoch_oversold (A-6) gate stack: stoch_k < 20 + price_above_ema_20 + close_below_open + ...
strat_williams_r_oversold (A-9) gate stack: williams_r < -80 + price_above_ema_200 + above_sma_50 + ...

Different OSC THRESHOLD (20 vs -80; though equivalent in raw OSC space) + different CONFIRMATION GATES (EMA-20 + close-direction vs EMA-200 + SMA-50). The combined fire-stream is empirically nearly DISJOINT (intersection 2 out of 474 LONG; 0 out of 155 SHORT).

**Council's algebraic-identity premise was correct; the strategy-level consequence was wrong.** Gate-stack diversity is the moderator.

## Connection to wider Pattern J landscape

B709 PEAD-restore established: phi=0.297 is BELOW 0.70 threshold -> distinct populations -> both strategies retained.

B722 hull_rsi DELETE established: phi >= 0.85 with IDENTICAL gates -> deterministic-duplicate -> DELETE.

B785 Williams-Stoch: phi <= 0.024 -> distinct populations -> **both strategies retained** with no consolidation. Aligned with B709 PEAD-restore precedent.

## Verdict + recommendation

**REJECT Pattern J consolidation for A-6 + A-9.** Keep both strategies as-is. Council reviewer's rec #42 is empirically refuted at the fire-stream level.

**No code changes.** Both strategies stay active.

## Note: caveats on the test

- Demo is 50 tickers x 1yr 2024 = 12,348 ticker-bars. Small sample; Williams fires 464 / Stoch fires 10 = 47:1 fire-rate ratio is suspicious (different gate-tightness levels).
- The fire-count asymmetry (Stoch only 10 fires LONG vs Williams 464) suggests Stoch's gate stack is much TIGHTER than Williams's. This is a separate observation (could be Pattern G threshold sweepability candidate for Stoch) but doesn't change the phi-correlation REFUTED verdict.
- The Pattern J question (are A-6 + A-9 redundant?) is answered NO. Whether A-6 is OVER-RESTRICTED is a separate ticket if surfaced empirically (not a B766 rec).

## CHECKLIST #107 reconciliation (B785)

- **Findings surfaced:** 1 primary (#42 Pattern J REFUTED at phi=0.024 LONG / -0.002 SHORT) + 1 nuanced (Stoch:Williams fire-rate 1:47 asymmetric -- separate Pattern G candidate not in scope of #42)
- **Tickets filed:** 0 NEW + 1 annotation on #42 (REFUTED-EMPIRICAL B785)
- **Audit-clean: YES**

Cumulative ticket count post-B785: 133 unique S4-B7XX tickets (no change).

## Strategy counts (unchanged)

221 / 0 / 1 / **220 active.**

## Memory + checklist compliance

- `feedback_no_a_priori_strategy_pruning.md` -- no strategies modified; analytical verdict only
- `feedback_no_prior_edge_consolidate_before_tune.md` -- measurement-then-decide pattern with pre-registered 0.70/0.85 thresholds; REFUTED outcome -> NO consolidation per rule
- `feedback_audit_recommendations_against_existing_directives.md` -- empirical evidence supersedes algebraic-identity intuition; explicit pre-registered threshold protocol applied
- CHECKLIST #44(b) -- N/A (no data-consumption audit; analytical-only)
- CHECKLIST #67 -- doc-sync same-turn
- CHECKLIST #69 -- pyramid (unchanged 842/842)
- CHECKLIST #77 -- canonical-source headers
- CHECKLIST #94 -- queue-mandatory-per-turn
- CHECKLIST #105 -- N/A (no producer walks; existing fire-bar matrix consumed)
- CHECKLIST #106 -- N/A
- CHECKLIST #107 -- findings-vs-tickets reconciliation (TWENTIETH-FULL-EXECUTION)
- CHECKLIST #108 -- pre-flight applied (a-d above)
