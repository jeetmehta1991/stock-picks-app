# B1068 PIVOT #39 — Suspect Silent Strategy Investigation

**Date:** 2026-06-28
**Source:** Phase D B1063 Phase 1 NVDA × 4y backtest
**Trade log:** `C:/Users/jeetm/AppData/Local/Temp/phase_d_b1063_phase1_final/trade_log.csv`
**Bars observed:** 1,255 NVDA daily bars (2021-05-06 → 2026-05-07; ~1,045 evaluable post 200-bar warmup)
**Trades produced:** 124 (across 42 strategies)
**Investigation method:** read-only static + runtime probe of `signals_at_entry` payload across all 124 entry rows + producer-level reruns on NVDA OHLCV cache + runtime introspection of panel signal path.

---

## 1. Executive Summary

**Primary root cause (HIGH confidence) — affects ~9 of 30 silent strategies (30%):**

A previously-undocumented producer-coverage bug in the panel-signal short-circuit path
(`USE_PANEL_TECHNICAL_SIGNALS=True` default in `backtest/config.py`) causes a SYSTEMATIC
BLACKOUT of three signal families:

  1. `below_ema_{9,20,21,50,200}` (all SHORT regime gates) — MISSING from 124/124 trade
     payloads (100% miss). 122 consumers in `screener.py`.
  2. `price_above_ema_{fast,slow}_break_recent_5d` and `below_ema_{fast,slow}_break_recent_5d`
     (B721/B722 EVENT-anchored regime-flip signals) — MISSING from 124/124. 18 consumers.
  3. `ema_{9_21,20_50,50_200}_bearish` (B634 symmetric SHORT trend signals) — MISSING from
     124/124. 4 consumers.

`compute_all_signals(df, skip_indicators={"rsi", "ema_sma", "simple_returns"})` skips
`compute_ema_sma`. The panel replacement `technical_panel.compute_panel_signals_for_as_of`
emits only the LONG/bullish/cross subset that existed when Batch 538 OPT-B was shipped; it
was never updated when B609/B634/B721/B722 added below_ema/bearish/break_recent_5d
producers. Result: any strategy gated on these signals **defaults to False every bar**
when the panel path is active.

**Secondary root cause (HIGH confidence) — affects ~3 of 30:** Single-regime affinity
filters (`{'bear'}` only) on LONG-side momentum strategies (`ppo_crossover`,
`adx_initiation`, `prev_day_high_break`), reducing 4y NVDA fire opportunity to ≤50 days.
Combined with already low EVENT base rates, brings expectation under 1.

**Tertiary root cause (MEDIUM confidence) — affects ~12 of 30:** Post-B722/B725/B779
STATE→EVENT conversion semantics. B660 baseline fire-counts were measured PRE-conversion
on STATE flags firing 12K-34K/yr universe-wide. Per B655 precedent, EVENT versions reduce
by ~95%. At NVDA-only scale + NVDA-2022-2026 strong-uptrend regime (rare 200-EMA flips),
EVENT-baselined expectations of 8-166 fires/4y can plausibly be 0-2.

**Quaternary (LOW-MEDIUM confidence) — affects ~3 of 30:** Strategy logic on entry-bar
sample-of-124 shows joint TRUE that doesn't manifest as that-strategy fires in trade_log
(e.g., `three_white_soldiers` joint TRUE on 4 bars but 0 trades; `adx_initiation` joint
TRUE on 4 bars but 0 trades). Suggests a fire-suppression mechanism downstream of my
trade-log probe (likely the panel-blackout above causing those entry decisions to be
made on a DIFFERENT signal dict where one gate evaluates False); but I cannot fully
attribute in the time budget. Flagged as OTHER.

**Category percentages (best-estimate, top-30 silent strategies):**

| Category | Count | % | Strategies |
|---|---|---|---|
| PRODUCER_BUG (panel-blackout below_ema/break_recent_5d) | 9 | 30% | hull_rsi, ichimoku_cloud_breakout, supertrend_ichimoku_adx, cpr_narrow_bullish, cpr_narrow_momentum, golden_cross_20_50, rsi_oversold, break_retest_confluence, avwap_50_reclaim |
| THRESHOLD_TOO_TIGHT (post-B722/B725 EVENT conversion + NVDA scale) | 8 | 27% | macd_ichimoku, ichimoku_tk_cross, golden_cross_9_21, supertrend_ichimoku_adx (overlap), avwap_252_breakout, 52w_high_breakout_pullback_long, 52wh_break_retest, donchian_breakout_retest_long |
| EXPECTED_AT_NVDA_SCALE (regime affinity + low joint) | 5 | 17% | ppo_crossover, adx_initiation, prev_day_high_break, three_white_soldiers, parabolic_sar_flip_short |
| OTHER (signal-payload joint TRUE but no fire; needs further investigation) | 5 | 17% | macd_crossover_short, prev_day_low_breakdown, donchian_breakdown_short, donchian_breakdown_retest_short, camarilla_r4_breakout |
| SIGNAL_NAME_DRIFT | 0 | 0% | (no clear cases found; B641 R3→R4 was already renamed) |
| Misc / overlapping categories | 3 | 10% | volume_spike_breakout, pivot_r1_breakout, roc_burst (each has plausible multiple causes) |

**Note on hull_rsi_short:** The input list contains `hull_rsi_short` (expected 161 fires).
That strategy was **DELETED at B722** (2026-06-12 per Pattern W duplicate-of-hull_rsi-SHORT-branch).
It is correctly absent. The 161 expected-fires figure carried over from B660 pre-deletion
baseline; the silent-list generator did not honor the deletion. CATEGORY: NOT_REGISTERED.

---

## 2. Per-Strategy Table

Legend: PB=PRODUCER_BUG, TT=THRESHOLD_TOO_TIGHT, SND=SIGNAL_NAME_DRIFT,
EXP=EXPECTED_AT_NVDA_SCALE, OTH=OTHER, NR=NOT_REGISTERED. Confidence: H/M/L.
"Joint TRUE / 124" = strategy logic evaluated as TRUE on observed entry bars in
`signals_at_entry` payload (NOT all 1,045 bars; biased to bars where some strategy fired,
but useful indicator).

| # | Strategy | Cat | Conf | Joint TRUE / 124 (regime-filtered) | Root Cause | Fix Suggestion |
|---|---|---|---|---|---|---|
| 1 | cpr_narrow_momentum | PB | H | 0 (LONG req `price_above_ema_200` ✓ + `cpr_narrow_tight` 32 TRUE + `macd_bullish` + ✗ `below_ema_200` for SHORT) | SHORT branch blocked by `below_ema_200` missing from panel (100% miss); LONG joint also limited by `cpr_narrow_tight` (0.05 threshold per B718) | Fix panel emission of `below_ema_*` + verify LONG cell fires on full universe (cpr_narrow_tight is restrictive but legitimate) |
| 2 | hull_rsi_short | NR | H | N/A | **DELETED Batch 722** (Pattern W duplicate of hull_rsi SHORT branch) | Remove from silent-list generator |
| 3 | hull_rsi | PB | H | LONG depends on `price_above_ema_200_break_recent_5d` (0/124 miss); SHORT depends on `below_ema_200_break_recent_5d` (0/124 miss) | **PRIMARY PRODUCER_BUG.** Strategy consumes `*_break_recent_5d` signals that the panel path never emits | Fix `technical_panel.py` to emit `*_break_recent_5d` OR remove `ema_sma` from skip set |
| 4 | ichimoku_cloud_breakout | TT | H | LONG (`ichi_above_cloud_break_recent_5d` 8 TRUE, `ichi_tk_bullish` 65, `adx_trending` 51, `ichi_weekly_above_cloud` 75; joint ≈ 4); SHORT mirror with 6/56/51/20 | EVENT conversion (B725) collapses STATE-based fires to break-event bars + 4-gate confluence requirement; per B655 precedent ~95% reduction from B660 STATE baseline | Acceptable post-B725; cube-measure; if fires < 30/regime tag EXPLORATORY |
| 5 | break_retest_confluence | PB | H | LONG joint 1/124, SHORT joint 0/124 | SHORT side hard-blocked by panel-missing `below_ema_20` + `below_ema_50` + `macd_12_26_9_bearish` is panel-present (69 TRUE) but below_ema gates kill it; LONG joint also pinched by 7-gate stack | Same panel fix as #3 |
| 6 | avwap_50_reclaim | PB | H | LONG req `avwap_50low_reclaim_recent_3d` (13 TRUE) + `macd_bullish` (55) + `price_above_ema_200` (75); joint observed 1/124; SHORT req `below_ema_200` (0/124 miss) | LONG legitimately scarce (EVENT × MACD × regime); SHORT BLOCKED by panel-missing below_ema_200 | Same panel fix as #3 + cube-measure LONG post-fix |
| 7 | cpr_narrow_bullish | PB | H | LONG (`cpr_narrow_tight` 32 + `above_cpr` + `above_avwap_50low` 97 + `price_above_ema_200` 75); SHORT all gates incl `below_ema_200` (0 miss) and `below_avwap_50low` (23 TRUE) | SHORT blocked by panel-missing below_ema_200; LONG should fire — investigate why 62 fires/4y not observed (NVDA-uptrend skew + 0.05 cpr_narrow_tight threshold) | Same panel fix as #3; cube-measure LONG |
| 8 | supertrend_ichimoku_adx | TT | H | LONG `supertrend_flip_recent_long_5d` 1/124 TRUE × `ichi_above_cloud_break_recent_5d` 8 × `adx_strong` 7; joint ≈ 0; SHORT symmetric | B779 SYMMETRIC EVENT conversion stacks 3 EVENT-rate signals; expected ~6/yr SHORT per B779 docstring; NVDA-strong-uptrend = 0 SHORT flips. LONG flips also rare | Acceptable post-B779; cube-measure; tag EXPLORATORY if FAIL_FIRE_STARVED |
| 9 | donchian_breakout_retest_long | TT | M | `dc20_resistance_break_retest_strong` (TRUE on some entries) + `vol_below_avg` 70 + `macd_bullish` 55 + `close_above_open` 39 + `close_in_top_40pct` 42; joint observed 1/124 | 5-gate confluence with Bulkowski low-volume retest requirement; NVDA's high-volume uptrend rarely has low-volume retest pattern | Acceptable; cube-measure; consider if convergence with `donchian_20_breakout_retest` is duplicative (B596 convergence note) |
| 10 | macd_crossover_short | OTH | M | SHORT `macd_12_26_9_crossover_dn` 4 TRUE + bear-affinity (50 days); joint regime-filtered ≈ 2 | Joint TRUE but 0 trades in log; suggests `_short_borrow_trap_active` may be triggering OR the entry-bar signal-payload doesn't match decision-time signals (panel-path discrepancy) | Verify `_short_borrow_trap_active(s)` evaluation; if NVDA on hard-to-borrow list it would suppress all SHORT |
| 11 | prev_day_high_break | EXP | H | LONG `above_prev_high` 30 + `vol_spike_15x` 6 + `above_vwap` 89; affinity {'bear'} only! 50 bear days only; joint regime-filtered ≈ 0 | Anomalous LONG-side strategy gated to bear-only affinity in `regime_selector.STRATEGY_REGIME_AFFINITY` — likely affinity-config bug. Also vol_spike_15x rare on NVDA (institutional buying not gappy) | Audit regime affinity for `prev_day_high_break` (LONG strategy bear-only is unusual); also vol gate tightness for NVDA |
| 12 | three_white_soldiers | OTH | M | `three_white_soldiers` 5 TRUE + `rsi_14<60` filtered = 4 ; affinity {'bull','bear'}; expected ≥4 fires but observed 0 | Joint TRUE on 4 entry bars in log but `three_white_soldiers` does not appear in `strategy` column. Same panel-payload-vs-decision-payload discrepancy as #10 | Investigate fire-emit path; verify rsi_14 in panel matches what compute_all_signals returns at non-panel path |
| 13 | golden_cross_9_21 | TT | H | LONG `ema_9_21_golden_cross` 2 TRUE + `price_above_sma_50` 70; joint 1/124 | EMA-9/21 cross is canonical EVENT signal; NVDA had ~2 crosses per year in this window. Single-cross visibility | Acceptable; expected ~8 per 4y on most names; NVDA-strong-trend may have fewer |
| 14 | macd_ichimoku | TT | H | LONG `macd_12_26_9_crossover_up` 5 + `ichi_above_cloud` 63; joint 2/124 | MACD crossover is EVENT (~few/yr); paired with cloud-above STATE means EVENT-rate dominates; B660 baseline 19 fires/4y is right order-of-magnitude | Acceptable; cube-measure |
| 15 | ppo_crossover | EXP | H | LONG `ppo_crossover_up` 5 + `adx_trending` 51; joint 2/124; **affinity bear-only**; regime-filtered = 1 | PPO crossover is EVENT-rate; affinity-filtered to 50 bear days; expected ~1-2 fires/4y for NVDA | Audit if bear-only affinity for `ppo_crossover` is intentional (LONG signal restricted to bear is unusual) |
| 16 | donchian_breakdown_retest_short | OTH | M | `dc20_support_break_retest_strong` 1 TRUE + `vol_below_avg` 70 + `macd_bearish` 69 + `close_below_open` 85 + `close_in_bottom_40pct` 56; joint observed 0/124 | 5-gate SHORT confluence; `dc20_support_break_retest_strong` only TRUE 1/124 (very rare on NVDA uptrend); also `_short_borrow_trap_active` may apply | Cube-measure on full universe; NVDA-specific rarity expected |
| 17 | volume_spike_breakout | TT | M | LONG `dc20_breakout_up` 10 + `vol_spike_15x` 6 + `above_avwap_20low` 91 + `close_above_open` 39 + `close_in_top_40pct` 42; joint 0/124 | 5-gate confluence with vol_spike + close-strength; B597 walk explicitly loosened vol_spike_2x→15x but NVDA's institutional uptrend has low vol-spike incidence | Acceptable but verify on diverse tickers; NVDA has unusually low vol-spike profile |
| 18 | pivot_r1_breakout | TT | M | LONG `above_r1` 21 + `vol_spike_15x` 6 + `macd_bullish` 55 + `above_avwap_252low` + `above_avwap_50low` 97; joint 1/124 | 5-gate breakout confluence; `vol_spike_15x` is the binding constraint on NVDA | Acceptable; cube-measure |
| 19 | camarilla_r4_breakout | OTH | M | LONG `above_cam_r4` 19 + `vol_spike_2x` 2; joint 1/124 | 2-gate strategy that should fire SOMETIMES; observed 1 entry-bar match but 0 trade. Same OTH pattern as #10/#12 | Investigate emit path; vol_spike_2x is extremely rare on NVDA (2/124) — primary binding constraint |
| 20 | adx_initiation | EXP/OTH | H/M | LONG `adx_cross_up` 7 + `adx_di_bull` 58; joint 4/124; affinity {'bear'} regime-filtered = 4 | Joint TRUE on 4 bear-bar entries but 0 trades — OTH discrepancy pattern. EXP component: affinity-bear-only is restrictive for an EVENT strategy | Investigate emit; LONG strategy bear-only affinity unusual |
| 21 | ichimoku_tk_cross | TT | H | LONG `ichi_tk_cross_up` 3 + `ichi_above_cloud` 63; joint 0/124 | Cross EVENT rate ~few/yr; AND cloud-above; NVDA-uptrend mostly has TK bullish already so few crosses up | Acceptable; expected for momentum-stable names |
| 22 | parabolic_sar_flip_short | EXP | H | `psar_flip_dn` 5 + `adx_trending` 51; affinity {neutral,bear,crisis}; joint regime-filtered 2 | NVDA uptrend = few PSAR-down flips with ADX-trending confirm | Acceptable |
| 23 | rsi_oversold | PB+TT | H | LONG `(rsi_2<5 OR rsi_14<35)` 7 + `price_above_sma_50` 70 + `price_above_ema_200` 75; joint observed = small; SHORT `below_ema_200` missing | LONG: NVDA rarely oversold (uptrend); SHORT: panel-blackout `below_ema_200` + `below_sma_50` | Same panel fix as #3; LONG legitimately rare for strong uptrend |
| 24 | 52w_high_breakout_pullback_long | TT | H | LONG `near_52w_high_retest_long` 2 TRUE / 124 | Strategy gated on producer `near_52w_high_retest_long` which is rare (4 conditions: prior_year_high broken in 10d + within 1% + low vol + bullish bar) | Acceptable producer rarity; cube-measure on diverse universe |
| 25 | avwap_252_breakout | TT | H | LONG `avwap_252low_reclaim_recent_3d` 7 + `vol_spike_15x` 6 + `rsi_14<70`; joint 0/124 | B802 EVENT-conversion expected ~127/yr universe (32/regime). At NVDA-only ~0.25/regime expected; observed 0 plausible | Acceptable per B802 projection; cube-measure on full universe |
| 26 | prev_day_low_breakdown | OTH | M | SHORT `below_prev_low` 33 + `vol_spike_15x` 6 + `below_vwap` (probably 35); joint observed ≈ 0; affinity {neutral,bear,crisis} | Joint TRUE rate low due to vol_spike binding; same OTH discrepancy if joint TRUE = 1+ but 0 trades | Audit vol_spike_15x on NVDA |
| 27 | roc_burst | TT | M | LONG `roc_turning_up` 1 + `vol_spike_15x` 6; joint 0/124 | EVENT-rate × vol gate; NVDA vol-spike rarity is binding | Acceptable; cube-measure on diverse universe |
| 28 | donchian_breakdown_short | OTH | M | `dc10_breakout_dn` 7 + `vol_spike_15x` 6 + `macd_bearish` 69 + `close_below_open` 85 + `close_in_bottom_40pct` 56; joint 2/124 | Joint TRUE 2 but 0 trades — same OTH discrepancy. Also `_short_borrow_trap_active` may apply | Investigate emit path + borrow trap |
| 29 | 52wh_break_retest | TT | H | LONG 7-gate confluence on `year_high_break_retest_long` (16 TRUE!) × `near_52w_high` 26 × `price_above_ema_200` 75 × `close_above_open` 39 × `close_in_top_40pct` 42 × `vol_below_avg` 70 × `above_avwap_20low` 91; joint observed 0/124 | 7-gate stacked confluence — combinatorial collapse despite each gate being moderately TRUE. The simultaneous bullish-bar + strong-close + low-vol-retest + 52w-anchor is a rare configuration | Reconsider gate stacking; B605 walk added 4 gates simultaneously which may have over-tightened |
| 30 | golden_cross_20_50 | PB | H | LONG `ema_20_50_golden_cross` 3 + `price_above_ema_200` 75; SHORT `ema_20_50_death_cross` 2 + `below_ema_200` (0/124 miss) | LONG marginally restrictive; SHORT BLOCKED by panel-missing below_ema_200 | Same panel fix as #3 |

---

## 3. Recommended Priority Order for Fixes

**P0 — Single highest-leverage fix:**

**Fix #1: Restore producer coverage in panel-signal path** (`backtest/signals/technical_panel.py`)

Add emission of:
- `below_ema_{9,20,21,50,200}` (mirror of `price_above_ema_*`)
- `below_sma_{50,200}` (mirror of `price_above_sma_*`)
- `ema_{9_21,20_50,50_200}_bearish` (mirror of `_bullish`)
- `price_above_ema_{fast,slow}_break_recent_5d` (B722 EVENT)
- `below_ema_{fast,slow}_break_recent_5d` (B721 EVENT)

Impact: Unblocks 9 of 30 silent strategies (30%) — every SHORT-side regime-gated strategy
(122 consumers of `below_ema_*` in screener.py) + 18 consumers of `*_break_recent_5d`.
This is the highest-ROI single fix in this audit.

**Alternative if panel-fix is risky:** Remove `"ema_sma"` from the `skip = {...}` set at
`screener.py:7990`. Cost: ~25ms/ticker/day re-paid (B538 OPT-B Phase 7 speedup partially
reversed). Compatible with all consumers immediately.

**Verification gate (per CHECKLIST #126):** After fix, re-run NVDA × 4y and verify
`below_ema_200` appears in 100% of `signals_at_entry` payloads + at least one of
{hull_rsi, golden_cross_20_50 SHORT, cpr_narrow_bullish SHORT, rsi_oversold SHORT,
break_retest_confluence SHORT} produces trades.

**P1 — Audit single-regime affinity for LONG-side EVENT strategies** (`backtest/engine/regime_selector.py`)

Anomalous entries (LONG-direction strategies restricted to bear-only):
- `prev_day_high_break` → affinity `{'bear'}` — LONG-side strategy on bear-only is suspicious
- `ppo_crossover` → affinity `{'bear'}`
- `adx_initiation` → affinity `{'bear'}`

These may be legitimate per-regime tuning (bear-regime momentum oversold-bounces?) but
the assignments warrant owner review. Impact: 3-5 of 30.

**P2 — Investigate OTHER cases** (5 of 30: macd_crossover_short, three_white_soldiers,
adx_initiation, camarilla_r4_breakout, donchian_breakdown_short, prev_day_low_breakdown)

For each, joint-TRUE entry bars exist in `signals_at_entry` but the strategy did not emit
a trade. Hypotheses:
- `_short_borrow_trap_active(s)` is True on NVDA (suppresses all SHORT). Verify NVDA's
  ETB/HTB status in cache.
- `signals_at_entry` snapshot was taken AFTER `panel_signals.update()` merge but BEFORE
  `inject_*_signals` calls modified the dict — so trade_log JSON differs from decision-time dict.
- Strategy logic short-circuits via Python falsiness on a numeric signal I missed.

Recommended diagnostic: add per-strategy `would_fire` audit logger (instrument
`screen_instrument` to emit each-strategy-evaluation result to a separate parquet for one
NVDA × 4y smoke run).

**P3 — Accept-and-tag for EVENT-conversion / NVDA-scale strategies** (15 of 30)

For strategies in TT/EXP categories, the silence is BY DESIGN per B655/B722/B725/B779/B802
STATE→EVENT conversion. They should be measured at full-universe scale (503 tickers × 4y =
2,012 ticker-years vs. 4 ticker-years for NVDA-only). Expected fires on the full universe:

| Strategy | NVDA-only obs | Full-universe expected (per B660 baseline / 95% reduction) |
|---|---|---|
| hull_rsi (post panel fix) | 0 | ~140-200/4y (28/yr × 95% reduction × 503 tickers) |
| ichimoku_cloud_breakout (post panel fix) | 0 | ~130-180/4y |
| cpr_narrow_momentum LONG (post panel fix) | 0 | ~166/4y as B660 baseline |

If fires < 30/regime at full universe, tag EXPLORATORY per B644/B772/B773 precedent.

---

## 4. Honest Caveats

1. **I did not run the actual screener / engine end-to-end** to confirm fix #1's impact.
   The signal-payload analysis is from STORED trade-log JSON; the decision-time dict may
   differ. Recommend smoke-running 1 ticker × 4mo post-fix to verify before launching
   full universe.

2. **OTHER category (5 strategies) has unexplained discrepancy** — joint-TRUE on entry
   bars in `signals_at_entry` but 0 trades. The most likely explanation is a
   payload-vs-decision-time signal mismatch, but I could not pin the exact mechanism in
   the time budget. The panel-blackout hypothesis (Fix #1) WOULD explain it for SHORT
   strategies whose gates depend on `below_ema_*` (macd_crossover_short, prev_day_low_breakdown,
   donchian_breakdown_short, donchian_breakdown_retest_short) IF the screener's strategy
   evaluation reads from a different dict than what gets stored. For LONG strategies
   (three_white_soldiers, camarilla_r4_breakout, adx_initiation) the panel hypothesis
   doesn't fit — these need direct strategy-evaluation logging to diagnose.

3. **NVDA-specific bias** — NVDA in 2022-05 → 2026-05 had extraordinary uptrend with rare
   200-EMA cross-down events, low vol-spike incidence, sustained high RSI. Many gates
   that screen "rare events" become near-impossible. Several strategies classified TT
   may actually fire at expected rates on more cyclical tickers. The B660 baseline of
   "expected fires" was computed at 503-ticker universe scale and naively divided by 503
   for NVDA — this assumes uniform fire-rates per ticker, which is empirically false
   (NVDA-specific factor loadings deviate substantially from universe mean).

4. **`_short_borrow_trap_active` was not probed.** Multiple OTH strategies have SHORT-side
   logic with this gate. If NVDA is borrow-difficult during any window, all SHORT
   strategies on NVDA suppress. Verify before concluding the OTH category is a real bug.

5. **Producer existence was verified for `break_recent_5d` family** by direct invocation
   of `compute_ema_sma` on NVDA 1,255-bar window (43 fires of `price_above_ema_200_break_recent_5d`
   + 41 fires of `below_ema_200_break_recent_5d` over 1,045 evaluable bars). The producer
   WORKS; the panel path SKIPS it. The bug is integration not production.

6. **hull_rsi_short on the silent list is itself a bug** — strategy was deleted at B722
   per Pattern W duplicate finding. The list-generator at B660 measurement time (pre-B722)
   needs to be updated to honor `STRATEGIES_DISABLED_MISSING_PRODUCER` + deleted-strategies
   set. Per CLAUDE.md banner: `len(ALL_STRATEGIES) = 220` post-B1035.

7. **Time budget impact:** I deep-investigated ~15 of 30 strategies thoroughly (producer
   verification + signal-payload probes + regime affinity). The remaining 15 are
   categorized by pattern-matching on the deep ones + reading docstrings. Confidence is
   stated per row.

---

## Appendix: Key Files & Line Numbers

| Component | File | Line |
|---|---|---|
| Panel-signal short-circuit (root-cause-1) | `backtest/signals/screener.py` | 7989-7994 |
| `USE_PANEL_TECHNICAL_SIGNALS=True` default | `backtest/config.py` | (search constant) |
| Panel producer `compute_panel_signals_for_as_of` | `backtest/signals/technical_panel.py` | — |
| `compute_ema_sma` (FULL producer, skipped by panel) | `backtest/signals/technical.py` | 723-799 |
| `_break_recent_5d` producer | `backtest/signals/technical.py` | 766-799 |
| `STRATEGY_REGIME_AFFINITY` (root-cause-2) | `backtest/engine/regime_selector.py` | — |
| `compute_all_signals(df, skip_indicators=...)` | `backtest/signals/screener.py` | (compute_all_signals def) |
| Trade-log entry-bar snapshot | `backtest/engine/backtest.py` | 2162-2179 |

