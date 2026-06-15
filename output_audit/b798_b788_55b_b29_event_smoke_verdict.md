# B798 -- B788 #55(b) B-29 EVENT-on-rank-crossing SMOKE VERDICT (bklplhvtt landed)

# per CHECKLIST #77 + #108 + #94 + #107
# Source: bklplhvtt background (B788 launched 2026-06-15; completed after ~3,822s)
# Source: B786 #56 GATE FINAL verdict (xs_low_beta_long STATE 71,355/yr baseline)
# per memory: feedback_no_a_priori_strategy_pruning + feedback_minimum_fire_count_gate_before_cube + feedback_no_rushing_per_strategy_tweak

## bklplhvtt smoke result

Scope: 20 T1a tickers (alphabetical-first) x 2024 = ~5,000 ticker-bars
Runtime: 3,821.5s (~64 min)
Config: B788 EVENT-form (`xs_low_beta_decile_entry_recent_5d` gate) + B779 daily cadence + B781 T1a+T2+T3+SPY rank universe

**xs_low_beta_long fires: 22 (0.44% of bars)**

## Comparison to baseline

| Form | Source | Fires/yr | Fire-rate |
|---|---|---|---|
| Pre-fix (SPY-gap) | B777 baseline | 0 (silent gap) | 0% |
| STATE (B786) | full T1a x 2024-2025 | **71,355/yr** | ~52% bars |
| **EVENT (B798)** | **20 tk x 2024 smoke; projected to T1a** | **~553/yr** | **0.44% bars** |

**Reduction factor: ~128x** (71,355 → 553). Substantially MORE than the 10x B655 T10 precedent projection.

## Per CHECKLIST #108 (b) fire-count gate check

- 553/yr universe-wide projection from smoke
- Above min_trades_overall=100 (PASS)
- Per-regime: 553 / 4 = ~138/regime (above min_trades=30/regime; PASS)
- Below typical PASS_CUBE level (1K-3K/yr)
- **BORDERLINE-LOW but above gate thresholds**

## Interpretation

Beta changes slowly (rolling 252-day). Most low-beta T1a names (utilities / staples / older blue-chips) sit at bottom-2-decile CONSTANTLY for months. EVENT signal `(today_decile <= 2) AND (5d_ago_decile > 2)` captures NEW additions to bottom-2-decile = rare transitions.

This is the DESIRED behavior (replaces over-firing STATE with selective EVENT) but MORE SELECTIVE than projected. The 5-day window may be TOO SHORT for the slow-moving beta factor; a 21-day or 63-day lookback might capture more transitions.

## Verdict + recommendation

**B788 EVENT-conversion SHIPS** — the gate works as designed:
- Massive reduction from over-firing STATE (71,355 → 553/yr = 128x)
- Above all fire-count gates per CHECKLIST #108
- Cube will measure whether the more-selective fires have BETTER edge per trade

**Owner-decision item for future tuning:** if cube cell shows FAIL_FIRE_STARVED on B-29 at 553/yr, consider widening the EVENT lookback from 5d to 21d. Producer-additive `xs_low_beta_decile_entry_recent_21d` could be added in a future batch.

## B-30 rollout decision (per chairman F4 + #55(b) sequence)

B-30 xs_momentum_bottom_decile_short was BORDERLINE 587/yr in B786 #56 GATE FINAL. EVENT-conversion projection (~128x reduction same as B-29): 587 / 128 ≈ 4.6/yr.

**4.6/yr falls FAR BELOW min_trades=30/regime threshold per CHECKLIST #108.** Per `feedback_minimum_fire_count_gate_before_cube`: do NOT apply EVENT-conversion to B-30. Keep STATE form. Cube measures borrow-aware edge on STATE form.

**B-30 EVENT-conversion REJECTED** per CHECKLIST #108 (b) fire-count gate.

## B-32 rollout decision

B-32 xs_quality_top_quintile_long PASS_CUBE 3,074/yr. EVENT-conversion projection: 3,074 / 128 ≈ 24/yr — BELOW min_trades=30/regime.

**B-32 EVENT-conversion REJECTED** per CHECKLIST #108 (b). Quality factor changes slowly too (financial reports quarterly); EVENT lookback too short.

## Factor sub-cluster EVENT-rollout summary

| Strategy | B786 STATE fire-rate | EVENT projection | Rollout |
|---|---|---|---|
| **B-29 xs_low_beta_long** | 71,355/yr | **553/yr (~128x ↓)** | **SHIPPED B788** |
| B-27 xs_combined_momentum_low_ivol | 0 (compound AND-stack) | N/A | EXPLORATORY-tagged B787 |
| B-28 xs_momentum_top_decile | 43/yr (survivorship-correction) | < 1/yr | EXPLORATORY-tagged B787 |
| B-30 xs_momentum_bottom_decile_short | 587/yr BORDERLINE | 4.6/yr | **STATE retained** (CHECKLIST #108 gate fail) |
| B-31 xs_momentum_quality_combined | 0 (compound) | N/A | EXPLORATORY-tagged B787 |
| B-32 xs_quality_top_quintile_long | 3,074/yr PASS | 24/yr | **STATE retained** (CHECKLIST #108 gate fail) |

**Factor sub-cluster EVENT-rollout COMPLETE:** B-29 only; others STATE-retained per CHECKLIST #108 fire-count gate per-strategy.

## CHECKLIST #107 reconciliation (B798)

- **Findings surfaced:** 1 primary (B788 #55(b) smoke shipped 553/yr above gates; massive 128x reduction) + 1 nuanced (B-30 + B-32 EVENT-rollout rejected per #108 fire-count gate per-strategy projection)
- **Tickets filed:** 0 NEW + 1 annotation on B788 #55(b) verdict (SMOKE VERIFIED; ships)
- **Audit-clean: YES**

## Cumulative ticket count post-B798

134 unique S4-B7XX tickets (no change).

## Strategy counts (unchanged)

221 / 0 / 1 / **220 active**. B-29 EVENT-form shipped B788 (no registration change; gate-only).

## Memory + checklist compliance

- `feedback_no_a_priori_strategy_pruning` -- no a-priori deletions; cube authoritative on 553/yr
- `feedback_minimum_fire_count_gate_before_cube` -- B-30 + B-32 EVENT-rollout rejected per gate
- `feedback_no_rushing_per_strategy_tweak` -- per-strategy decisions per fire-count projection
- `feedback_audit_recommendations_against_existing_directives` -- B786 fire-count evidence + CHECKLIST #108 sequencing both honored
- CHECKLIST #44(b) -- N/A (no data-consumption audit)
- CHECKLIST #67 -- doc-sync same-turn
- CHECKLIST #69 -- pyramid 842/842 (unchanged)
- CHECKLIST #77 -- canonical-source headers
- CHECKLIST #94 -- queue-mandatory-per-turn
- CHECKLIST #105 -- producer + strategy source already read in B788
- CHECKLIST #106 -- producer-data audit chain
- CHECKLIST #107 -- THIRTY-THIRD-FULL-EXECUTION
- CHECKLIST #108 -- (a-d) applied per-strategy for B-29 / B-30 / B-32 rollout decisions
