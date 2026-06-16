# B807 #33 LATENT-COLLAPSE PHI-CORRELATION AUDIT VERDICT (Cluster A)

# per CHECKLIST #77 + #94 + #105 + #107
# Source: output_audit/fire_bar_similarity_cluster_a_demo.parquet (B760 demo 50 tickers x 1yr 2024)
# Source: B785 + B787 individual phi-correlation audits (Williams-Stoch + RSI family)
# per memory: feedback_no_a_priori_strategy_pruning + feedback_audit_recommendations_against_existing_directives

## Council First Principles + Reviewer 3 claim

> "30 strategies encode 4-7 latent factors (oscillator-oversold + band-touch + AVWAP-pullback + pivot-support + capitulation-volume-reversal + RSI(2)-extreme). Cluster strategies into latent groups by phi >= 0.70."

## EMPIRICAL VERDICT: REFUTED

| Phi tier | Pairs | % of 486 |
|---|---:|---:|
| phi >= 0.85 (DELETE threshold per B722 hull_rsi precedent) | **0** | 0% |
| phi >= 0.70 (CONSOLIDATION threshold per First Principles + B709 PEAD precedent) | **0** | 0% |
| 0.50 - 0.70 (MEDIUM correlation) | 3 | 0.6% |
| 0.30 - 0.50 (LOW correlation) | 9 | 1.9% |
| **phi < 0.30 (essentially independent)** | **474** | **97.5%** |

**0 of 486 pairs cross the phi >= 0.70 latent-collapse threshold.** Council's "30 → 4-7 latents" hypothesis empirically refuted at the fire-stream level.

## Top-10 highest phi pairs (none qualify for consolidation)

| Strategy A | Strategy B | Direction | Phi |
|---|---|---|---:|
| cpr_narrow_momentum | cpr_narrow_momentum_short | SHORT | +0.693 |
| bollinger_lower | bollinger_tight | SHORT | +0.518 |
| bollinger_lower | bollinger_tight | LONG | +0.512 |
| stochrsi_overbought_short | stochrsi_oversold | SHORT | +0.420 |
| rsi_oversold | williams_r_oversold | LONG | +0.398 |
| rsi_oversold | williams_r_oversold | SHORT | +0.374 |
| bollinger_lower | rsi_volume_200ema | LONG | +0.366 |
| camarilla_r4_breakout | roc_burst | SHORT | +0.355 |
| bollinger_lower | rsi_volume_200ema | SHORT | +0.352 |
| bollinger_tight | rsi_volume_200ema | LONG | +0.331 |

**Note:** highest phi (0.693) is the **same-strategy dual-direction pair** (cpr_narrow_momentum LONG vs cpr_narrow_momentum_short SHORT). This is NOT a distinct latent — it's the SHORT branch of the LONG strategy registered as a separate `_short` strategy. Excluding same-strategy dual-direction pairs, the highest cross-strategy phi is 0.52 (bollinger_lower vs bollinger_tight) — also below the 0.70 threshold.

## Interpretation

Cluster A strategies have **DIVERSE empirical fire patterns** despite reviewer's algebraic-similarity intuition. Gate-stack diversity (different oscillator thresholds, different regime gates, different confirmation gates) produces nearly-disjoint fire streams even for underlying-signal-similar strategies (Williams %R + Stoch %K = same construct algebraically but phi=0.398 — measurably distinct populations).

This aligns with prior individual phi audits:
- **B785 #42** Williams-Stoch oversold: phi LONG=+0.024 / SHORT=-0.002
- **B787 #35** RSI family (4 strategies): max phi=+0.10
- **B807 #33** ALL 486 Cluster A pairs: max phi=+0.69 (same-strategy dual); next 0.52

## Connection to council's broader claims

This refutes:
- First Principles advisor's "30 strategies wear 4-7 latents in costume" hypothesis
- Reviewer 3's same-class claim
- Council's "Bonferroni denominator is partly fictional" → empirical evidence supports DISTINCT hypotheses count = strategy count

This SUPPORTS:
- Contrarian advisor's caveat: "ADX vs Supertrend vs Ichimoku Kumo are not actually identical constructs" (gate-stack diversity moderates underlying-signal similarity)
- B709 PEAD-restore precedent (phi=0.297 < 0.70 → retain both)
- B722 hull_rsi DELETE precedent (phi >= 0.85 → DELETE; NO Cluster A pairs hit this)

## CHECKLIST #107 reconciliation (B807)

- **Findings surfaced:** 1 primary (#33 phi >= 0.70 threshold NOT MET by ANY Cluster A pair; council's latent-collapse hypothesis REFUTED)
- **Tickets filed:** 0 NEW + 1 annotation on #33 (REFUTED-EMPIRICAL)
- **Audit-clean: YES**

## Cumulative ticket count post-B807

134 unique S4-B7XX tickets (no change).

## Strategy counts (unchanged)

221 / 0 / 1 / **220 active**. No strategies modified.
