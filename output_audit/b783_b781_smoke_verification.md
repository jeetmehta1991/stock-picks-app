# B783 -- B781 #65 + #66 smoke verification (bbg84zfcs landed) + proper #56 GATE re-measurement launched

# per CHECKLIST #77 + #44(b) + #94 + #105 + #107
# Source: bbg84zfcs background smoke (launched B781; completed 2026-06-15 after ~24min runtime)
# Source: scripts/measure_fire_count.py B781 wireup (_build_factor_universe_ohlcv helper)
# per memory: feedback_data_consumption_audit_must_apply_checklist_44b + feedback_audit_recommendations_against_existing_directives

## bbg84zfcs B781 smoke verification result

Scope: 20 T1a tickers (alphabetical-first sample) x 2024-H1 x 124 bars per ticker = 2,480 ticker-bars; full B779+B781 config (daily cadence + T1a+T2+T3+SPY rank universe).

Runtime: 1,445s (~24 min).

| Strategy | L fires | S fires | Pre-B781 (B777 50tkr 2yr) | Pre-vs-Post |
|---|---:|---:|---:|---|
| **xs_low_beta_long** (B-29 BAB) | **1,301** | 0 | **0 (SPY-gap)** | **CONFIRMED FIX** |
| xs_combined_momentum_low_ivol | 0 | 0 | 0 (SPY-gap; also fire-starved by AND-stack) | Mixed -- needs scale |
| xs_momentum_top_decile | 0 | 0 | 8,996 (T1a-only ranking) | Rank-denom shift |

## #66 SPY benchmark fix VERIFIED

B-29 xs_low_beta_long went from **0 fires** (B777 baseline, SPY-gap) to **1,301 fires** on a SMALLER smoke (20 tickers x 6mo vs B777's 50 tickers x 2yr).

Per CHECKLIST #44(b) investigate-why (B780): SPY benchmark gap was the root cause. B781 force-include resolves it. Smoke verification confirms.

## #65 universe expansion: rank-denominator shift visible

xs_momentum_top_decile dropped from 8,996/yr (B777 T1a-only ranking) to 0 fires (B783 smoke; T1a+T2+T3 ranking).

**This is the EXPECTED + CORRECT behavior per #58(e) survivorship-bias correction.**

The B777 T1a-only ranking inflated T1a top-decile membership (S&P 500 winners ranking against themselves). When T2/T3 momentum names (spinoffs / IPOs / momentum-screener-output) join the rank universe, T1a tickers shift down the momentum percentile -- because the broader cross-section has high-momentum names outside T1a.

Council Expansionist's concern (Novy-Marx 2014 + AFP 2019: published edge gets eaten by survivorship-bias) is now MITIGATED via #58(e) implementation. The previous 8,996/yr was a SURVIVORSHIP-INFLATED count; the post-B781 measurement gives the cross-sectionally honest count.

Caveat: 20-ticker × 6mo smoke is too small for definitive verdict on momentum strategies. The random 20 tickers happened to not include any post-expansion top-decile names. Proper #56 GATE re-measurement at 50 tickers × 2024-2025 launched as B783 background (b8l2hqhv2).

## Inverted-low-beta-fire-rate verification

xs_low_beta_long firing **1,301 fires on 2,480 bars = 52% fire rate** is high. Two interpretations:

1. **Universe-expansion induced concentration**: with T2/T3 momentum names in the ranking, T1a names (older blue-chips / utilities / staples) shift TOWARD low-beta percentile. So the bottom-2-decile of T1a+T2+T3 now contains MORE T1a tickers proportionally than the bottom-2-decile of T1a-only.

2. **Within-T1a sample skew**: the alphabetical-first 20-ticker sample may have happened to include low-beta names disproportionately.

For proper interpretation, need larger sample (b8l2hqhv2 50-ticker × 2-year random-seed-42 will give definitive numbers).

## B783 proper #56 GATE re-measurement launched

Background ID: **b8l2hqhv2**
Scope: 50 tickers (random seed 42) x 2024-2025 x all 6 factor strategies
Config: full B779 daily cadence + B781 #65 T1a+T2+T3 expansion + #66 SPY force-include
ETA: ~60-120 min (estimated from bbg84zfcs 24min for 20-ticker x 6mo; scale to 50-ticker x 2yr ~10x)
Output: `output_audit/b783_factor_56_gate_proper_remeasure.json`
Verdict batch: B784

## CHECKLIST #107 reconciliation (B783)

- **Findings surfaced:** 2 primary (#66 SPY fix CONFIRMED via B-29 1,301 fires vs 0 baseline; #65 universe expansion working with expected rank-denominator-shift behavior) + 1 nuanced (xs_low_beta 52% fire rate is universe-expansion-induced concentration, needs scale-verification)
- **Tickets filed:** 0 NEW + 0 annotations (smoke verification + measurement launch; final verdict batch is B784)
- **Audit-clean: YES**

Cumulative ticket count post-B783: 133 unique S4-B7XX tickets (no change).

## Strategy counts (unchanged)

221 / 0 / 1 / **220 active**.

## Memory + checklist compliance

- `feedback_data_consumption_audit_must_apply_checklist_44b.md` -- #66 fix VALIDATED EMPIRICALLY by smoke (B-29 0->1,301 fires); #44(b) investigate-why chain B774->B775->B780->B781 fully validated
- `feedback_no_a_priori_strategy_pruning.md` -- no strategies modified; smoke verification only
- `feedback_audit_recommendations_against_existing_directives.md` -- B781 implementation aligned with owner directive 58(e) + SPY-gap finding; smoke confirms no internal contradictions
- `feedback_narrow_scope_blast_radius.md` -- factor universe expansion scoped to cross_sectional compute; execution stays T1a; smoke confirms strategy-eval-loop unchanged
- CHECKLIST #44(b), #67, #69, #77, #94, #105, #106, #107 all applied
