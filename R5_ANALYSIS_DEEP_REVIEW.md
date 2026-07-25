<!-- Source: per CHECKLIST #77; B1376 owner-requested deep self-review of the R5 strategy analysis chain (B1366-B1375). Findings are code-verified (EXECUTED) this session. -->

# R5 Analysis - Deep Self-Review (2026-07-25)

**Scope:** the full R5 analysis chain - cube merge (B1366), 5-Gate optimizer (B1368),
per-cell walk-forward (B1369-B1371), --all-cells loose/robust (B1371), conditional
per-regime + OOS validation (B1372-B1374), and PASSED_STRATEGY_EXIT_LIST.md (B1375).
Owner directive: "deep review of your work... any formula or calculation errors? any
mistakes? any misses? Council this. Very thorough."

**Verdict:** the pipeline is directionally sound and one real bug (Sharpe annualization,
B1371) was already fixed, but the "passed" set is **softer than it reads** and one
**data-integrity contamination is material**. Nothing here is deploy-grade until findings
1 and 6 are fixed and the analysis re-run.

---

## Findings (most-severe first; all EXECUTED this session)

### F6 [HIGH - MATERIAL] Delisting-collapse extreme returns contaminate the cube
- **Evidence:** 906 cube rows have `|pnl_pct| > 500%`, **all on `SBNY`** (Signature Bank,
  FDIC-seized March 2023 -> price ~$0). Global `max(pnl_pct) = 264,900%`, `min = -4,134%`.
  Affected strategies incl. `pairs_mean_reversion_long` (227 rows - and it is one of the 17
  conditional survivors), `dc20_break_retest` (62), `week_opening_gap_fill_up` (62), etc.
- **Why it happens:** the survivorship-free 614-ticker universe (by design) includes tickers
  that collapsed in-window. Near-zero post-collapse prices make `(exit-entry)/entry` explode.
  A single +264,900% trade dominates a cell's mean AND std -> both the cumulative-return and
  the Sharpe of any affected cell are unreliable.
- **Impact:** every metric (Sharpe, cumulative return, WR is unaffected) for cells containing
  these trades is distorted; the "passing" status of contaminated cells is untrustworthy.
- **Fix (S6-B1375-WINSORIZE):** winsorize per-trade `pnl_pct` (e.g. cap at +/-300%, or exclude
  post-collapse bars for delisted tickers) and RE-RUN the whole gate/conditional/doc chain.
  Also add a hard data-integrity assert (`|pnl_pct| <= K`) to the merge.

### F1 [HIGH] Sharpe is GROSS - no transaction cost / slippage
- **Evidence:** `trade_exit_detail.csv` has no cost/slippage/net column; `pnl_pct` is gross.
  The passing criteria's cost-sensitivity AUTO-FAIL (`metrics.py`) was never applied in the
  walk-forward.
- **Impact:** every Sharpe in the passed list is pre-friction; net-of-cost is lower and the
  marginal cells (esp. short-hold, high-turnover) will fail.
- **Fix (S6-B1375-NET-OF-COST):** apply round-trip cost + slippage (per the engine's cost model)
  and re-derive the passing set + cost-sensitivity ratio.

### F2 [HIGH] Small-sample noise, no confidence intervals
- **Evidence:** ~14% of qualifying cells are n=30-40. At n=36 the annualized-Sharpe 95% CI
  half-width is ~+/-1.6, so a 0.7 point estimate is statistically indistinguishable from 0.
  The 2.0-2.7 top Sharpes sit on n=30-40.
- **Impact:** point Sharpes overstate reliability; ranking by point Sharpe over-selects noise.
- **Fix (S6-B1375-SHARPE-CI):** report Sharpe CIs / require higher n / shrink toward 0; prefer
  the lower CI bound for gating.

### F3 [MEDIUM-HIGH] The loose-613 is not a true train/test holdout
- **Evidence:** `--all-cells` counts cells clearing >=0.7 in >=1 (loose) / >=2 (robust) of 4
  annual folds, selected from the SAME 2022-2026 window (4758 cells x 4 folds, multiple-testing
  UNCORRECTED). Only the 17 regime-conditional overrides used a genuine IS-pick(2022-2025) /
  OOS-measure(2025-2026) split.
- **Impact:** the 613/115 are "annual-consistency" evidence, weaker than the 17; the loose-613
  false-positive rate is inflated by uncorrected multiple testing.
- **Fix (S6-B1375-OOS-HOLDOUT):** hold out a final year (or apply Bonferroni/BH-FDR across the
  4758) so the 613 has the same rigor as the 17.

### F4 [MEDIUM] Dual: pooled-pass != per-direction-pass
- **Evidence:** the 82 were selected on POOLED (strategy x exit) cells; a dual can clear pooled
  yet have neither direction clear (e.g. `awesome_oscillator` short best-fold OOS 0.25). The doc
  now splits by direction; failing directions are DROP candidates, not deployables.
- **Fix (S6-B1375-DUAL-FORMULA):** the doc's per-direction rows currently show the strategy-level
  compact entry-gate for both; split the dual `fires` (long-leg vs short-leg) per row.

### F5 [MEDIUM] Crisis regime absent
- **Evidence:** no (strategy x exit x crisis) slice reaches n>=30 in the 2022-2026 window.
- **Impact:** this system is designed to buy dips in crisis; there is zero crisis-regime evidence
  in the passed set. Deployments have no crisis validation.

### Checked and CLEARED
- **Annualization inflation - MINOR.** Only 20/2287 passing folds have <2-day holds (median 15.8d);
  the `sqrt(252/avg_hold)` factor is not materially inflating the top cells.
- **Sharpe annualization bug - ALREADY FIXED (B1371, L223):** per-trade vs annualized mismatch that
  had collapsed passers 613->10; corrected to match `metrics.py::_sharpe`.

---

## Recommended fix order (all local/free; owner-gated)
1. **F6 winsorize + F1 net-of-cost** - re-run the gate/conditional/doc chain. These change every
   number and are prerequisite to any "deploy" or $300 1B-alpha language.
2. **F2 CIs + F3 holdout/multiple-testing** - re-grade the 613 to the 17's rigor.
3. **F4 dual per-direction formula + drop-flag; F5 note crisis gap.**

## Cross-references
- `PASSED_STRATEGY_EXIT_LIST.md` (the artifact under review) + its KNOWN LIMITATIONS header
- `scripts/walk_forward_r5_cells.py` (`--all-cells`, `--by`, `--validate-conditional`)
- `scripts/build_passed_strategy_exit_list.py` (the doc generator)
- `LEARNINGS.md` L223 (Sharpe annualization), L224 (IS-pick/OOS-measure), L225 (gross/small-n/not-OOS), L226 (delisting-collapse winsorization)
- `EXECUTION_QUEUE.md` B1369-B1376 + tickets S6-B1375-* / S6-B1376-WINSORIZE
