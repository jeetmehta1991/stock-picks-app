# Survivorship Verification Methodology — W5 LONG + W5m SHORT Adversarial Test

**Status:** APPROVED B667 (2026-06-09 owner-approved all 4 decisions). Harness scaffold `scripts/measure_survivorship_sensitivity.py` ships in B666 + ready-to-execute post-B660. Per Decision 1 (approved), the harness EXECUTION is deferred until B660 (full-universe representative-sample measurement) lands.

**Originally:** DRAFT — Batch 666 (2026-06-09 owner-approved foundational re-prioritization commitment per B665 critique #9 + critique C5).

**B667 outcome — owner-approved decisions:**

| # | Question | Approved decision |
|---|---|---|
| 1 | Run harness now or wait for B660 first? | **Wait for B660 first** (foundational sequence integrity) |
| 2 | Sensitivity thresholds? | **0.5pp / 2pp** (robust / moderate / high) |
| 3 | Cross-strategy sweep scoping? | **Separate batch** (W5 + W5m first; cluster-wide follows post-cube empirical) |
| 4 | Action on high-sensitivity verdict? | **Confirm DO-NOT-DEPLOY + flag for deletion in post-cube batch** (no auto-delete per `project_no_apriori_strategy_pruning`) |

**Execution sequence (B667 owner-approved):**
1. B660 lands → re-populate all per-strategy fire counts with full-universe representative numbers (in flight)
2. B669 (next data-batch after B660 lands) executes the survivorship harness against W5 + W5m using the post-B660 fire counts; reports per-strategy survivorship sensitivity verdict against 0.5pp / 2pp thresholds
3. If W5 or W5m show high sensitivity (≥2pp inflation): confirm DO-NOT-DEPLOY architecturally + flag for owner-decision in a post-cube batch
4. B670+ (later sequence) extends the survivorship sweep cluster-wide per Decision 3

**Source:** External-AI 2nd-wave critique C5 (Pass 53 B641 audit): *"Survivorship bias lethal to W5 + deep-dip longs (left tail deleted from survivor universe)"* + queue ticket `S5-SURVIVORSHIP-T1A-VERIFY`.

**Audience:** External reviewer + owner + future Claude. Pre-reading: this doc assumes familiarity with the W5 + W5m EXPLORATORY + DO-NOT-DEPLOY status established in [STAGE_4_PIVOT_CLUSTER_WALKS.md](STAGE_4_PIVOT_CLUSTER_WALKS.md#w5-strat_pivot_s3_capitulation).

---

## Why this document exists

W5 (`pivot_s3_capitulation`) buys deep S3 capitulation + reversal-trigger within a 5-day window. W5m (`pivot_r3_blowoff_short`) sells deep R3 blowoff + bearish-reversal-trigger within a 5-day window. Both strategies are designed to enter on price extremes (capitulation = -5σ moves; blowoff = +5σ moves).

**The survivorship hazard (per critique C5):** the T1a active universe (503 names at as_of=2026-05-31) is the survivor set — the 111 names delisted during the 2020-2026 window are excluded by default in any "active T1a" lookup. Strategies that buy capitulation in survivor universes show artificial alpha because the falling-knife names that DIDN'T bounce — that kept falling and got delisted — are systematically excluded from the test sample.

**Symmetrically for W5m SHORT:** the squeeze risk is structurally biased against shorts. A strategy that shorts blowoff tops in a survivor universe shows artificial alpha because the rare-but-catastrophic squeeze cases that took prices to multi-bagger highs (GME, AMC, MSTR, etc.) and then permanently re-rated higher are mostly STILL in the survivor universe — but the strategy might have entered short before the squeeze and stopped out at catastrophic loss. The survivor-universe Sharpe averages across "survived the squeeze" + "squeezed out" but the latter is rare in survivor data.

**DEC-477 T1a canonical PIT file:** the `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` includes 614 rows — 503 currently-active + 111 historical-removed-during-window. This is the survivorship-aware universe; the PIT filter `(added_date IS NULL OR added_date ≤ as_of) AND (removed_date IS NULL OR removed_date > as_of)` correctly includes a ticker IFF it was in the index at as_of, regardless of what happened later.

**The question this methodology answers:** does W5 + W5m's apparent alpha change materially when measured against the full (survivor + delisted-during-window) universe vs. the active-only universe?

---

## Methodology

### Three universe modes for adversarial comparison

| Mode | Definition | Ticker count |
|---|---|---|
| **SURVIVOR_ONLY** | Active T1a at as_of=2026-05-31 (removed_date IS NULL) | 503 |
| **DELISTED_ONLY** | Historical-removed-during-window (removed_date BETWEEN 2020-01-01 AND 2026-05-31) | 111 |
| **FULL** | SURVIVOR_ONLY + DELISTED_ONLY, with PIT filter applied per-bar | 614 |

For each mode, run W5 + W5m + measure per-fire outcomes.

### Per-fire outcome metrics

For every fire bar in each mode, record:

| Metric | Description |
|---|---|
| **fire_date** | Bar of strategy entry |
| **direction** | "long" (W5) or "short" (W5m) |
| **entry_price** | Next-bar open (per engine PIT discipline) |
| **exit_date_1bar** | Single-bar return for null comparison |
| **return_1bar** | 1-day forward return from entry |
| **return_5bar** | 5-day forward return |
| **return_20bar** | 20-day forward return (matches Cohen-Malloy-Pomorski class hold horizons) |
| **return_atr_trail** | Return under the default atr_trail_1x exit (matches actual engine deployment) |
| **delisted_within_6mo** | True if ticker delisted within 6 months after fire bar (survivor-only proxy for "knife continued falling") |
| **squeezed_within_6mo** | True if ticker price doubled within 6 months after fire (W5m-relevant; squeeze risk realized) |
| **max_drawdown_during_hold** | Worst drawdown during the atr-trail hold (MAE) |
| **max_runup_during_hold** | Best runup during the atr-trail hold (MFE) |

### Per-mode aggregate metrics

For each (strategy, mode) pair, compute:

| Metric | Why |
|---|---|
| **n_fires** | Sample size; if SURVIVOR_ONLY has 95% of fires, the delisted tail is providing little statistical contribution |
| **mean_return_atr_trail** | The actual engine-deployment-relevant return |
| **mean_return_20bar** | Calibration vs. Cohen-Malloy-Pomorski 20-day horizon |
| **hit_rate** | % of fires with positive atr-trail return |
| **mean_drawdown** | Average MAE |
| **mean_runup** | Average MFE |
| **blow_up_rate** | % of fires where `delisted_within_6mo = True` (W5) or `squeezed_within_6mo = True` (W5m) |

### Adversarial diff

For each strategy, the SURVIVOR_ONLY vs FULL diff is the survivorship sensitivity signature:

| Diff | What it says |
|---|---|
| `mean_return_atr_trail[SURVIVOR_ONLY] - mean_return_atr_trail[FULL]` | If positive, strategy benefits from survivorship (survivor-only returns are inflated) |
| `hit_rate[SURVIVOR_ONLY] - hit_rate[FULL]` | If positive, survivor-only win rate is inflated |
| `blow_up_rate[FULL] - blow_up_rate[SURVIVOR_ONLY]` | The fires that DID delist/squeeze, by definition only visible in FULL — a positive number is the survivorship hazard quantified |

**Verdict thresholds (initial; owner approves per discipline):**
- If `survivor_inflation < 0.5pp` → strategy is robust to survivorship (low concern)
- If `0.5pp ≤ survivor_inflation < 2pp` → moderate sensitivity (acknowledge in docstring + cube replay both modes)
- If `survivor_inflation ≥ 2pp` → high sensitivity (EXPLORATORY → DO-NOT-DEPLOY confirmation OR deletion)

**Per `project_no_apriori_strategy_pruning`:** even high-sensitivity strategies don't get auto-deleted; the verdict feeds the next batch's owner decision.

---

## Harness implementation

`scripts/measure_survivorship_sensitivity.py` (ships with this batch as ready-to-run; not yet executed per discipline).

### CLI

```sh
# W5 + W5m only (the EXPLORATORY pair)
python scripts/measure_survivorship_sensitivity.py \
    --strategies pivot_s3_capitulation pivot_r3_blowoff_short \
    --modes survivor_only delisted_only full \
    --start 2020-01-01 --end 2026-05-31 \
    --output output_audit/survivorship_sensitivity_w5_w5m.json

# All EXPLORATORY + DO-NOT-DEPLOY strategies (currently just W5 + W5m, but extensible)
python scripts/measure_survivorship_sensitivity.py --exploratory-only --output ...

# All registered strategies (long-running; for cluster-wide survivorship audit)
python scripts/measure_survivorship_sensitivity.py --all --output ...
```

### Output schema

```json
{
    "as_of": "2026-05-31",
    "modes": {
        "survivor_only": {"n_tickers": 503, "definition": "..."},
        "delisted_only": {"n_tickers": 111, "definition": "..."},
        "full": {"n_tickers": 614, "definition": "..."}
    },
    "strategies": {
        "pivot_s3_capitulation": {
            "by_mode": {
                "survivor_only": {
                    "n_fires": 92,
                    "mean_return_atr_trail": 0.018,
                    "mean_return_20bar": 0.024,
                    "hit_rate": 0.57,
                    "mean_mae": -0.041,
                    "mean_mfe": 0.062,
                    "blow_up_rate": 0.00
                },
                "delisted_only": {
                    "n_fires": 14,
                    "mean_return_atr_trail": -0.083,
                    "mean_return_20bar": -0.151,
                    "hit_rate": 0.21,
                    "mean_mae": -0.118,
                    "mean_mfe": 0.022,
                    "blow_up_rate": 0.79
                },
                "full": {
                    "n_fires": 106,
                    "mean_return_atr_trail": 0.005,
                    "mean_return_20bar": -0.001,
                    "hit_rate": 0.52,
                    "mean_mae": -0.052,
                    "mean_mfe": 0.057,
                    "blow_up_rate": 0.10
                }
            },
            "survivor_sensitivity": {
                "return_inflation_pp": 1.3,
                "hit_rate_inflation_pp": 5.0,
                "blow_up_rate_hidden_pp": 10.0,
                "verdict": "moderate sensitivity"
            }
        },
        "pivot_r3_blowoff_short": {
            "by_mode": {...},
            "survivor_sensitivity": {...}
        }
    }
}
```

The numbers above are illustrative placeholders — actual values come from running the harness.

---

## Per `feedback_minimum_fire_count_gate_before_cube` (CHECKLIST (e)) — power check

| Sample | Expected n_fires per strategy | Statistical power |
|---|---|---|
| SURVIVOR_ONLY × 6 years | ~50-100 fires depending on strategy | Per-mode usable |
| DELISTED_ONLY × 6 years | ~5-15 fires per strategy (small sample) | Per-mode statistically weak; diff against survivor still informative |
| FULL × 6 years | ~60-115 fires per strategy | Per-mode usable |

The DELISTED_ONLY sample is small by construction (111 names × variable bars × low fire rates per strategy). The harness reports the small-sample caveat in output. The KEY diagnostic remains the FULL vs SURVIVOR_ONLY return diff, which has enough samples in both modes for statistical meaning.

---

## Cross-strategy sweep (extension, separate batch)

Beyond W5 + W5m, the same survivorship sensitivity audit can run against any other strategy. Initial priority list (post-B660 owner-decision sequencing):

| Strategy | Why prioritize |
|---|---|
| SM-1, SM-2 insider_cluster | Cohen-Malloy-Pomorski 2012 alpha thesis explicitly conditions on crisis; survivorship may inflate published insider-buying alpha |
| SM-9, SM-23 institutional_distribution / capitulation | B665 Pattern C — `institutional_negative` SHORT may exhibit reverse survivorship (delisted-during-window names where institutions exited are SAMPLED in DELISTED_ONLY; not in SURVIVOR_ONLY) |
| Mean-reversion strategies (RSI<35, bollinger_lower, etc.) | Symmetric W5-class — they buy oversold conditions; survivorship-amplified |
| Capitulation-adjacent (anything with `near_s3`, `rsi_14 < 30`, `vol_spike` triggers) | Same family-bug class as W5 |

This extension is queued as `S5-SURVIVORSHIP-T1A-CLUSTER-SWEEP` — runs after the W5 + W5m initial verdict + after B660 lands.

---

## Open questions for owner decision

| # | Question | Recommended | Alternatives |
|---|---|---|---|
| 1 | Run harness now, or wait for B660 to land first | **Wait for B660 first** — B660 establishes per-strategy fire counts on the FULL universe; the survivorship-sensitivity harness uses fire counts as inputs; running survivorship before B660 = redo when B660 lands | Run now (W5 + W5m only — narrow scope) |
| 2 | Sensitivity threshold for "moderate" vs "high" | 0.5pp / 2pp recommended | Higher / lower thresholds |
| 3 | Cross-strategy sweep — run as separate batch or bundled with W5 + W5m | Separate batch (W5 + W5m first; cluster-wide sweep follows) | Bundled |
| 4 | What to do if W5 + W5m show high sensitivity | Confirm DO-NOT-DEPLOY (architectural) + flag for deletion in post-cube-empirical batch | Auto-delete (overrides `project_no_apriori_strategy_pruning`) |

**Recommendation #1 trade-off explicitly stated:** running C5 harness BEFORE B660 lands gives a survivorship-sensitivity number on the OLD measure_fire_count baseline (which is sampling-driven per B665 critique #4). The number can be re-computed after B660 lands using full-universe representative fire counts. But the survivorship-sensitivity DIFF (survivor_only vs full) is computable now without B660; the SCALE of the diff is the open question.

**My recommendation is "wait for B660 first"** because the foundational re-prioritization commitment explicitly sequences B660 → C2 → C5. Running C5 in parallel with the C2 draft and B660 in-flight makes sense as design/scaffolding (this doc + the harness script), but executing the survivorship measurement before the foundational universe baseline lands would re-create the same sampling-discipline failure mode the B665 critique exposed.

---

## End of C5 methodology draft

**Status:**
- Policy doc: AWAITING owner approval on 4 questions
- Harness script: `scripts/measure_survivorship_sensitivity.py` ships in B666 as ready-to-run; NOT executed yet per discipline

**Next step after owner approval:**
1. **If "wait for B660":** queue the harness run for the batch after B660 lands; no immediate action
2. **If "run now":** execute the harness against W5 + W5m only (narrow scope); report verdict in a sibling batch
3. **Either way:** the harness scaffolding is ready (script + this methodology doc)

**Reviewer-relevant note:** this draft addresses critique C5 AT THE METHODOLOGY LEVEL. The DEC-477 T1a 111 delisted-during-window names are already cataloged in the canonical PIT file; the harness adds the survivor_only / delisted_only / full mode toggle on top of existing infrastructure. The actual empirical verdict on whether W5 + W5m show survivorship sensitivity is the deliverable of a future batch once methodology + sequencing are owner-approved.
