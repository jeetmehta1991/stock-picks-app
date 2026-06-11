# Stage 4 Breakout Cluster Walks — Per-Strategy Deep-Dive Audit

> **B696 PENDING SUMMARY (2026-06-11) — what's STILL OPEN from the external reviewer's recommendations.**
>
> Below is the cluster-wide status of EVERY reviewer recommendation as of commit `ab5daee6c`. The pattern: **tools shipped, evidence not yet gathered, no per-strategy parameter changes made.** Per project rule *"Never change rules, filters, thresholds, or parameters without approval"*, every per-strategy fix below is owner-gated.
>
> **What IS done:**
> - All 4 diagnostic tools shipped + validated: [`trigger_followthrough.py`](scripts/trigger_followthrough.py) (3/3 synthetic checks PASS), [`diagnose_zero_fires.py`](scripts/diagnose_zero_fires.py), [`verify_silent_gap_fix.py`](scripts/verify_silent_gap_fix.py), [`conditional_information_gate_diagnostic.py`](backtest/engine/conditional_information_gate_diagnostic.py) (B687, 15/15 PASS).
> - BR-7 / BR-8 silent-gap re-verified CLEAN post-B617 (reviewer Finding #3 sub-question closed; redundancy concern remains open).
> - Selective-reading methodology correction (Finding #2) shipped as banner addenda to chart-pattern / SMC / ICT / event-driven / smart-money docs.
> - 24 reviewer-mapped tickets registered in [EXECUTION_QUEUE.md](EXECUTION_QUEUE.md) (every recommendation traceable to a ticket).
> - B660 re-run infrastructure (B695 + B696) on AWS — in flight as of this banner; will produce trustworthy fire counts post-B689 producer wire-in.
>
> **What is NOT done — full pending matrix:**
>
> | # | Reviewer item | Tool/data needed | Blocked by | Owner action required |
> |---|---|---|---|---|
> | 1 | **BR-1 zero diagnosis** — confirm "empty conjunction" vs "harness gap" | `diagnose_zero_fires.py` (✅ shipped) | B660 re-run completion (in flight); current local OHLCV cache works for single-ticker smoke | NO — Claude can run diagnostic + report; owner reviews verdict |
> | 2 | **BR-1 conjunction loosen** (±1-bar window OR 3-of-4 score) | Code edit in `screener.py` `strat_52w_high_breakout` | Finding #1 diagnosis above must show empty-conjunction first | YES — owner approval per `feedback_local_changes_default_global_needs_approval` |
> | 3 | **BR-7/BR-8 retest re-anchor** (confirmed reclaim, not loose 1.5×ATR band) | Code edit in `screener.py` `strat_break_retest_volume` + `strat_dc20_break_retest` | None | YES — owner approval |
> | 4 | **BR-7/BR-8 OBV switch** to `obv_bullish` (20-bar baseline; producer already emits this; strategies ignore it) | Code edit replacing 5-bar OBV window | None | YES — owner approval |
> | 5 | **Pattern N outcome-correlation matrix** (replace primitive-counting) | `conditional_information_gate_diagnostic.py` (✅ shipped) + cube return panel | B668 cube replay (depends on C5 survivorship + C6 cost-aware) | NO — Claude runs once data lands |
> | 6 | **CC1 gap-haircut measurement** (detection-close fill vs next-open) | Per-strategy winners list + bar-level OHLC | B660 re-run trade-log (not just fire counts) | NO — Claude runs once data lands |
> | 7 | **52w sector ETF reframe** + conditional_add_test on `sector_outperforming_spy` | `conditional_add_test()` in trigger_followthrough.py (✅ shipped) | B660 re-run gives fire mask; can run on local cache for preview | NO — Claude can run + report |
> | 8 | **Anti-fakeout #1: Break-clearance margin** sweep (0.3-0.5×ATR) | `sweep_threshold()` (✅ shipped) | Available NOW on local OHLCV | NO — Claude runs sweep + reports; owner approves any code change |
> | 9 | **Anti-fakeout #2: Close-location tighten** (40% → 25-30%) sweep | `sweep_threshold()` (✅ shipped) | Available NOW | NO — Claude runs sweep + reports |
> | 10 | **Anti-fakeout #3: Volume comparison correctness** (breakout = expansion / retest = contraction) audit | Source-read audit | Available NOW | NO — Claude does audit + reports |
> | 11 | **Anti-fakeout #4: Immediate-reclaim filter** add-test | `conditional_add_test()` (✅ shipped) | Available NOW | NO — Claude runs + reports |
> | 12 | **Anti-fakeout #5: Pre-break compression** add-test (HIGHEST-VALUE; missing everywhere except BR-19) | `conditional_add_test()` (✅ shipped) + new compression signal | Need compression producer signal (volatility-contraction ratio OR BB-width-inside-Keltner percentile) | NO — Claude can build producer signal + run; owner reviews |
> | 13 | **Anti-fakeout #6: Extension filter** add-test (RSI not >75 OR distance-from-EMA-20 cap) | `conditional_add_test()` (✅ shipped) | Available NOW | NO — Claude runs + reports |
> | 14 | **RVOL z-score replace fixed multiples** (cluster-wide) | NEW producer signal `vol_z_score_N_day` in `technical.py` | Producer code addition | YES — owner approval for new producer signal |
> | 15 | **Retest family reclaim-bar trigger** (BR-2/4/5/6/12/13) — fire on bounce not touch | Code edit in `screener.py` for 6 strategies | None | YES — owner approval per strategy |
> | 16 | **Retest family tolerance tighten** (1.5×ATR → 0.5-0.75×ATR) | Code edit | sweep_threshold can validate threshold first | YES — owner approval |
> | 17 | **Retest family dry-up tighten** (vol_below_avg → <0.7× breakout-bar) | Code edit + new producer signal (breakout-bar volume reference) | Producer + code changes | YES — owner approval |
> | 18 | **Short breakdowns: apply B594/B596 strong-break clearance to ALL shorts** | Code edit in 5 strategies | None | YES — owner approval |
> | 19 | **Donchian raw-vs-overlay timing test** (subtractive; drop lagging MACD-STATE gate) | sweep_threshold + follow-through comparison | Available NOW | NO — Claude runs comparison + reports; owner approves drop |
> | 20 | **Donchian channel period sweep** (DC10 vs DC20 — currently fixed by lineage) | sweep_threshold | Available NOW | NO — Claude runs sweep + reports |
> | 21 | **BR-14/15 vol-spike RVOL z + earnings blackout + AVWAP-reclaim for BR-15** | RVOL z producer + Finnhub earnings cache (TIER 2) + code change | TIER 2 producer wire-in (B690) for earnings; RVOL z is independent | YES — owner approval |
> | 22 | **BR-16 force_index fold-into-confirmation** (delete as standalone OR keep as gate on BR-1/BR-10) | conditional_add_test on force-index vs other breakouts + delete decision | Available NOW | YES — owner approval to delete strategy |
> | 23 | **BR-17 inside-bar continuation context gate** (replace ADX with base-tightness) | Base-tightness producer + code change | Producer + code changes | YES — owner approval |
> | 24 | **BR-19 squeeze release-anchor verify + tightness sweep** | sweep_threshold + source-read | Available NOW | NO — Claude verifies + reports; owner approves any change |
> | 25 | **Earnings blackout on volume-triggered breakouts** (BR-1/14/15/19) | Finnhub earnings cache wire-in | B690 TIER 2 harness | YES — owner approval for earnings filter |
> | 26 | **Follow-through horizon per-strategy sweep** (2-3 horizon settings reported) | trigger_followthrough.py extension to multi-horizon mode | Tool refinement (~30 LOC) | NO — Claude refines tool when scope reaches it |
> | 27 | **Book-level distinctness post-tuning** (outcome correlation matrix on tuned-survivors) | conditional_information_gate_diagnostic.py | Tuning complete first; B668 cube data | NO — runs once dependencies land |
>
> **Critical interpretation:**
> - **18 of 27 items** require owner approval before code change (strategy modifications)
> - **9 of 27 items** I can run autonomously NOW (diagnostic-only, no parameter changes) and report findings; owner then decides whether to act
> - **3 items** blocked on B668 cube replay (Pattern N outcome correlation, CC1 gap haircut, book-level distinctness)
> - **3 items** blocked on B690 TIER 2 producers (smart-money / event-driven Finnhub cache for earnings blackout)
> - **2 items** require new producer signals (RVOL z-score #14, compression #12) — small additions to technical.py
>
> **My standing recommendation:** while B660 re-run completes (~3h on AWS), run the 9 read-only sweeps (#1, #7-#11, #13, #19, #20, #24) on the local OHLCV cache + produce a markdown report with the actual sweep curves. That report becomes the evidence base for the per-strategy owner decisions. Zero code changes, ~30-45 min of compute, produces ~9 sweep-result tables you can decide from.
>
> Confirm the standing recommendation and I'll kick off the read-only sweeps now while AWS does its work.
>
> ---
>
> **B693 STATUS BANNER (2026-06-11) — EXTERNAL REVIEW INCORPORATED + TRIGGER-FOLLOW-THROUGH TOOL SHIPPED.** An external adversarial review of this doc surfaced 7 cluster-level findings + a per-strategy trigger-optimization sheet + 6 anti-fakeout parameters + a working diagnostic tool (`scripts/trigger_followthrough.py` validated all-3-checks PASS on synthetic ground truth). Reviewer's framing principle, applied across the cluster: **"a measured zero must be diagnosed, not assumed"** — the B691 banner's blanket "false negative pending re-run" disposition of all 6 FAIL_FIRE_STARVED is a one-directional reading of the evidence (favorable measurements LOCKED, unfavorable PENDING). Distinguishing harness-gap zeros from empty-conjunction zeros requires a positive test, now scaffolded at [`scripts/diagnose_zero_fires.py`](scripts/diagnose_zero_fires.py). The cluster's central trigger-quality concerns are now operational rather than rhetorical.
>
> **7 reviewer findings (severity-ordered):**
>
> | # | Finding | B693 disposition |
> |---|---|---|
> | **#1 (CRITICAL)** | BR-1 flagship measured **0 fires** in B660, doc still rates "PASS likely" 300 lines later, contradictions unreconciled. Most likely cause: same-bar 5-way AND of `break_52w_high + vol_spike_17x + sector_outperforming_spy + close_above_open + close_in_top_40pct` is structurally empty — not a harness gap. | ✅ DIAGNOSTIC TOOL SHIPPED: [`scripts/diagnose_zero_fires.py`](scripts/diagnose_zero_fires.py) distinguishes "signal absent from dict" (harness gap) from "signals present but AND is empty" (empty conjunction) per reviewer's two-part test. **OWNER ACTION: ticket `S4-B693-BR-1-ZERO-DIAGNOSIS` queued for resolution before any re-run conclusion.** |
> | **#2 (CRITICAL methodology)** | "False negative" is being used as an unfalsifiable escape hatch — every favorable B660 number (24 PASS) is LOCKED, every unfavorable number (6 FAIL) is PENDING-RERUN. The same selective-reading pattern shipped in 5 cluster docs in B691. When favorable data is trusted and unfavorable data is provisional pending a fix, measurement can no longer disconfirm. | ✅ DISPOSITION CHANGE: each "false negative" claim now requires a positive test before being labeled. NEW METHODOLOGY: (a) confirm gate signal literally absent from dict (not just zero-fire), (b) confirm with signal present, other gates leave non-empty surviving set. Applies cluster-wide. **Amending B691 banners on chart-pattern/SMC/ICT/event-driven docs to reflect this** (B691 banner shipped a one-directional reading; B693 corrects). |
> | **#3 (HIGH)** | BR-7 (`break_retest_volume`) measured 41,868 LONG + 25,015 SHORT; BR-8 (`dc20_break_retest`) measured 38,554 + 23,672. The 25k SHORT counts match the silent-gap bug signature from the original W2/W3 walks. | ✅ VERIFIED B693 via [`scripts/verify_silent_gap_fix.py`](scripts/verify_silent_gap_fix.py): post-B617 4-gate SHORT uses positive `s.get(...)` AND-chained ([screener.py:2730-2733](backtest/signals/screener.py#L2730-L2733)) with NO `not s.get(...)` patterns. Missing keys → None → falsy → AND fails. **NO SILENT-GAP post-B617.** 25k SHORT fires are REAL fires. **REDUNDANCY concern (BR-7 = BR-8 = Donchian = 52w-retest variants firing on the same trade) is the real explanation; queued as `S4-B693-BR-7-BR-8-REDUNDANCY-VS-DONCHIAN`.** |
> | **#4 (HIGH)** | Pattern N's "effective hypothesis count ≈ 13" is computed by counting distinct primitives (syntactic) when it should be measured via pairwise outcome correlation / marginal contribution from the B660 return panel. The 13 count is probably HIGHER than the real effective N because cross-primitive correlation in a breakout cluster (everything fires on the same up-moves) is large. | Queued: `S4-B693-PATTERN-N-OUTCOME-CORRELATION-NOT-PRIMITIVE-COUNT` — replace primitive-counting with outcome-correlation matrix using post-B668 cube return panel. The B687 conditional-information diagnostic plugs in directly. |
> | **#5 (MEDIUM)** | CC1 (continuation gap) reasoning is half-right: the gap IS in the trade's direction, but that means you enter at a worse price on every winning breakout — systematic haircut on exactly the winners. The doc dismisses this as "LOW-MEDIUM"; for momentum-continuation strategies the post-breakout-gap fill is often the largest determinant of edge survival. | Queued: `S4-B693-CC1-GAP-HAIRCUT-MEASURE-DETECTION-VS-NEXT-OPEN` — compare detection-close fill vs next-open fill on B660 winners; quantify the haircut. |
> | **#6 (MEDIUM)** | The 52w family's "sector ETF substitute" framing for `sector_outperforming_spy` is wrong: it's a sector relative-strength filter, not a trend filter. A stock making a 52-week high IS in an uptrend (EMA-gate redundant); meanwhile the sector gate vetoes good breakouts for sector-rotation reasons unrelated to the stock. **Probable culprit for BR-1's zero fires.** | Queued: `S4-B693-52W-SECTOR-ETF-REFRAME-AND-AB-TEST` — reframe + conditional_add_test on `sector_outperforming_spy` to determine if it earns its slot. |
> | **#7 (cluster-positive)** | Real citations (George-Hwang 2004 JF, Bulkowski 2005, Turtle), B660 actually landed (vs SMC/ICT speculative), redundancy self-flagged as flagship, forensic-fix density real. Best-anchored cluster in the series. | ✅ Preserved in framing |
>
> **6 anti-fakeout parameters (reviewer's framework — most are missing from the cluster):**
>
> 1. **Break-clearance margin** (ATR-scaled, ~0.3-0.5×ATR, swept) — present only on B594/B596 "strong variants"; should be on EVERY breakout/breakdown. Most general anti-fakeout filter; separates real break from one-tick poke. → Queued cluster-wide: `S4-B693-CLUSTER-CLEARANCE-ATR-SWEEP`.
> 2. **Close location within bar** (tighten from 40% → top 25-30%, swept) — currently arbitrary 40%, probably too loose. High-information, low-cost. → Queued: `S4-B693-CLOSE-LOCATION-25-30PCT-SWEEP`.
> 3. **Volume confirmation — right comparison** — breakouts need EXPANSION (RVOL z ≥ threshold), retests need CONTRACTION (retest-bar < 0.7× breakout-bar). Cluster sometimes uses wrong one. → Queued: `S4-B693-VOLUME-COMPARISON-CORRECTNESS-AUDIT`.
> 4. **Immediate-reclaim filter** (one-bar confirmation, sweep N=1-2 bars) — MOSTLY MISSING. Cleanest fakeout tell: break happens then price reclaims the level within 1-2 bars. Highest value on SHORTS specifically (snapback/stop-run dynamic). → Queued: `S4-B693-IMMEDIATE-RECLAIM-FILTER-ADD-TEST`.
> 5. **Pre-breakout compression** (volatility-contraction ratio OR BB-width-inside-Keltner percentile, swept) — **MISSING EVERYWHERE except BR-19**; reviewer's "most likely to raise conditional follow-through." BR-19 squeeze is the in-house compression template to generalize. → Queued: `S4-B693-CLUSTER-PRE-BREAK-COMPRESSION-ADD-TEST`.
> 6. **Extension filter** (cap distance-from-anchor: close within X×ATR of 20-EMA, or RSI not >75) — MISSING. Targets exhaustion-breakout fakeout (distinct from compression: compression looks at the base, extension at how far price has already run). → Queued: `S4-B693-CLUSTER-EXTENSION-FILTER-ADD-TEST`.
>
> **Per-strategy trigger-optimization (reviewer's consolidated sheet):**
>
> | Strategy | Re-tune | Add | Specific values | Queued ticket |
> |---|---|---|---|---|
> | **BR-1** 52w_high_breakout (flagship; zero fires) | vol_spike_17x → RVOL z; close_top_40pct → top-25-30% | ±1-bar confirmation window OR 3-of-4 score; break-clearance margin; pre-break compression; immediate-reclaim; conditional_add_test on sector_outperforming_spy | window=1-2; close top 25-30%; clearance 0.3-0.5×ATR | `S4-B693-BR-1-ZERO-DIAGNOSIS-+-CONJUNCTION-LOOSEN` |
> | **BR-2/4/5/6/12/13** retest family | Retest tolerance 1.5×ATR → 0.5-0.75×ATR; vol_below_avg → <0.7× breakout-bar volume | Reclaim-bar trigger (fire on bounce not touch); freshness window N bars | tolerance 0.5-0.75×ATR; dry-up <0.7×; freshness N=5-15 swept | `S4-B693-RETEST-FAMILY-RECLAIM-BAR-TIGHTEN-FRESHNESS` |
> | **BR-3/11/18 + BR-6/13 shorts** | Apply B594/B596 strong-break ATR clearance to ALL shorts (not just some) | Immediate-reclaim filter (highest value here); confirmation-bar | clearance 0.5×ATR symmetric to longs | `S4-B693-SHORT-BREAKDOWNS-CLEARANCE-+-RECLAIM` |
> | **BR-7/BR-8** 40k-fire pair | Retest tolerance hard-tighten; OBV switch to `obv_bullish` (20-bar baseline; **producer already emits; strategy ignores per B617 post-fix code**) OR retest-bar-specific volume; verify silent-gap is fixed (✅ done B693 — clean post-B617) | Clearance margin + reclaim confirmation + compression | retest-bar volume not 5-bar; OBV from 20-bar baseline | `S4-B693-BR-7-BR-8-RE-ANCHOR-+-REDUNDANCY-ABLATION` |
> | **BR-9/10/12** Donchian | Test raw channel-break vs post-B589 5-gate overlay (overlay may be DELAYING the trigger past the breakout moment); sweep channel period DC10 vs DC20 (currently fixed by lineage) | Replace lagging MACD-STATE gate with clearance margin (doesn't lag) | DC10-DC20 sweep; raw-vs-5-gate follow-through diff | `S4-B693-DONCHIAN-RAW-VS-OVERLAY-+-CHANNEL-PERIOD` |
> | **BR-14/BR-15** volume-spike | vol_spike_15x → RVOL z-score | Close-location + clearance + earnings blackout (single biggest false-spike source); AVWAP-reclaim trigger for BR-15 | RVOL z ≥ 2.0 swept; blackout ±2 bars | `S4-B693-VOL-SPIKE-RVOL-Z-+-AVWAP-RECLAIM` |
> | **BR-16** force_index | Repurpose as confirmation gate on BR-1/BR-10, not standalone | conditional_add_test on force-index cross given a real breakout already fired | — | `S4-B693-BR-16-FOLD-INTO-CONFIRMATION` |
> | **BR-17** inside_bar | Gate to continuation context (inside bars within/after trend leg or at base-edge, not random); replace ADX proxy with base-tightness | — | continuation context only | `S4-B693-BR-17-CONTINUATION-CONTEXT-+-BASE-TIGHTNESS` |
> | **BR-19** squeeze | Sweep squeeze-tightness threshold; confirm fires on release bar (EVENT) not squeeze state (STATE) | — | BB-width-inside-Keltner percentile sweep | `S4-B693-BR-19-RELEASE-ANCHOR-CONFIRM` |
>
> **Reviewer's 7-item refined priority order** (entry-only, by follow-through-impact / unit effort):
>
> 1. **BR-1 conjunction fix** (±1-bar / 3-of-4) — rescues the flagship from zero
> 2. **BR-7/BR-8 re-anchor + silent-gap re-verify (✅ done B693, clean) + retest-bar volume**
> 3. **Retest family reclaim-bar trigger** (BR-2/4/5/6/12/13) — touch→bounce
> 4. **Cluster-wide RVOL z-score + ATR-scaled clearance margin**
> 5. **Add compression + reclaim-confirmation via `conditional_add_test`** — the two highest-value missing anti-fakeout parameters
> 6. **Donchian raw-vs-5-gate timing test** — subtractive optimization
> 7. **Earnings blackout on all volume-triggered strategies** — coinflip removal
>
> **4 optimization discipline principles (apply to every sweep above):**
> 1. **Optimize on conditional follow-through, not returns** (exit-free path metric).
> 2. **Sweep coarse grid, pick the plateau center, not the peak** — a value best at exactly 0.47 and bad at 0.4/0.5 is noise; a value good across 0.3-0.5 is real.
> 3. **Hold out time** — tune 2020-2022, validate persistence on 2023-2025. A fakeout filter that only works in-sample isn't a fakeout filter.
> 4. **Add a parameter only if `conditional_add_test` shows it lifts follow-through GIVEN existing gates already pass** — stops you stacking redundant anti-fakeout gates that just shrink fires for no conditional gain. (This is the B687 gate-redundancy diagnostic in follow-through units.)
>
> **Tool framing — three complementary diagnostics (all shipped):**
>
> | Tool | Axis | Question | Status |
> |---|---|---|---|
> | [`backtest/engine/conditional_information_gate_diagnostic.py`](backtest/engine/conditional_information_gate_diagnostic.py) (B687) | Outcome conditional on OTHER gates | Does this gate add CONDITIONAL information about the outcome given the others? | Module + 15-pin validation; awaits cube replay (B668) |
> | [`scripts/trigger_followthrough.py`](scripts/trigger_followthrough.py) (B693) | Outcome conditional on the trigger firing | Did the move materialize (target-first) or invalidate (stop-first) over N bars? | Module + validation harness all-3-checks PASS on synthetic ground truth |
> | [`scripts/diagnose_zero_fires.py`](scripts/diagnose_zero_fires.py) + [`scripts/verify_silent_gap_fix.py`](scripts/verify_silent_gap_fix.py) (B693) | Did the strategy have any chance to fire | Is the zero a harness gap, an empty conjunction, or an auto-passing gate? | Scaffolds; methodology validated on BR-7 (clean post-B617) |
>
> **Reviewer's tool-trustworthiness story (worth preserving):** the first validation harness run FAILED. The synthetic-market constructor I (claude) reproduced had a bug — the quality-driven drift didn't actually persist over the 12-bar horizon, so the barrier race saw noise. The tool correctly reported "no edge" rather than flattering bad data. The reviewer (and now I) fixed the synthetic, not the tool. A diagnostic that refuses to flatter is the only kind worth shipping; this one has that discipline.
>
> **One caveat the reviewer explicitly stated:** the trigger-follow-through tool's target/stop/horizon defaults (2×ATR / 1×ATR / 10 bars) are themselves choices. A trigger can look well- or poorly-timed depending on them. Sweep them per strategy, OR report follow-through across 2-3 horizon settings so a parameter isn't declared good only because it suits one barrier geometry. Queued: `S4-B693-FOLLOWTHROUGH-HORIZON-PER-STRATEGY-OR-MULTI`.
>
> **Closing caveat:** tuning each strategy in isolation to the same follow-through boundary will make them MORE correlated, not less (Pattern N concern intensifies). The per-strategy tuning above must be followed by a book-level distinctness pass: which tuned-survivors still pick up distinct opportunities? Otherwise you get 19 well-timed versions of about 4 trades. Queued: `S4-B693-BOOK-LEVEL-DISTINCTNESS-POST-TUNING`.
>
> ---
>
> **B691 STATUS BANNER (2026-06-11) — MOSTLY TRUSTWORTHY ✅ / `htf_aligned_*` subset PENDING-B689-RERUN.** B660 measurement landed [2026-06-11 02:30 UTC](output_audit/fire_count_measured_b660_full_universe.json) showing **24 PASS_CUBE / 6 FAIL_FIRE_STARVED for the 30-strategy breakout cluster** (broader than the original 19 in this doc — includes 52w_high/low, donchian, bollinger, dc20, value_area, break_retest variants registered as `breakout` category). Most strategies in this cluster use only `technical.py` producers (compute_donchian / compute_bollinger / compute_break_retest_signals / compute_52w_break_retest_signals / compute_pivot_break_retest_signals) — those B660 numbers are TRUSTWORTHY and the B689 re-run will NOT change them.
>
> **TRUSTWORTHY subset (sample of 24 PASS_CUBE):**
> | Strategy | LONG | SHORT | Verdict |
> |---|---:|---:|---|
> | 52w_high_breakout_pullback_long | 8,132 | 0 | ✅ PASS |
> | 52w_low_breakdown_pullback_short | 0 | 3,989 | ✅ PASS |
> | 52wh_break_retest | 6,790 | 0 | ✅ PASS |
> | 52wl_break_retest_short | 0 | 1,315 | ✅ PASS |
> | break_retest_confluence | 38,554 | 23,672 | ✅ PASS (very high — investigate redundancy in cube) |
> | break_retest_volume | 41,868 | 25,015 | ✅ PASS |
> | bollinger_lower | 7,018 | 5,675 | ✅ PASS |
> | bollinger_tight | 23,850 | 19,269 | ✅ PASS |
> | bollinger_upper_short | 0 | 477 | ✅ PASS |
> | volume_spike_breakout | 1,820 | 0 | ✅ PASS |
> | volume_spike_breakout_retest | 359 | 0 | ✅ PASS |
> | squeeze_breakout | 1,820 | 0 | ✅ PASS |
>
> **PENDING-B689-RERUN subset (6 FAIL_FIRE_STARVED → ~2 are FALSE NEGATIVES):**
> | Strategy | B660 LONG | B660 SHORT | Likely status post-rerun |
> |---|---:|---:|---|
> | htf_aligned_breakout_long | 0 | 0 | 🔴 FALSE-NEGATIVE — needs `multi_timeframe.compute_htf_alignment` (TIER 1, wired B689) |
> | htf_aligned_breakout_short | 0 | 0 | 🔴 FALSE-NEGATIVE — same |
> | 52w_high_breakout | 0 | 0 | ⚠ Mixed — may resolve in re-run if blocked on different harness gap; review |
> | 52w_low_breakdown | 0 | 0 | ⚠ Mixed — same as above |
> | classification_change_breakout_long | 0 | 0 | 🔴 FALSE-NEGATIVE TIER 2 (B690) — needs `index_rebalance` producer (deferred) |
> | squeeze_setup_long | 0 | 0 | 🔴 FALSE-NEGATIVE TIER 2 (B690) — needs `short_interest` producer for SI gate |
>
> All `PENDING B660` labels for the `htf_aligned_*` pair are now **PENDING-B660-RERUN-B689** (resolves ~2026-06-12 12:30). `classification_change_breakout_long` + `squeeze_setup_long` are **PENDING-B690** (TIER 2 wait). The 24 PASS_CUBE rows are LOCKED.
>
> **B676 status banner (2026-06-10, owner-directed autonomous continuation):** SIXTH per-cluster Stage 4 walk doc. Owner directive *"continue autonomously"* after B675 ICT cluster walk. Cluster contains **19 strategies** in `breakout` category — the LARGEST remaining unwalked cluster. Many have prior batch-level walks (B582/B586/B587/B589/B590/B591/B594/B595/B596/B598/B605/B608/B612/B626/B654) that collectively constitute "implementation" walks but NOT the systematic CHECKLIST #105 7-step methodology per-strategy. This doc IS that systematic walk.
>
> **Source of truth.** Code references reflect current state at commit `cba27db74` (post-B675 ICT walk).
>
> **CARRY-FORWARD from prior cluster walks + B673/B674 external reviewer critique:** **Pattern A** (default-True silent-gap), **Pattern M** (no peer-reviewed citation — partial; some breakouts cite George-Hwang 2004 JF + Bulkowski 2005 which ARE legitimate), **Pattern N** (intra-cluster collinearity — 19 strategies on a small primitive set), **Pattern O** (hardcoded tolerances — many in breakout cluster), **Pattern Q** (no-empirical-citation cluster-wide partial applicability), **Pattern F** (marginal-contribution audit), **Pattern G** (low-fire-combo EXPLORATORY). NEW patterns specific to this cluster surface in §[Cross-strategy patterns](#cross-strategy-patterns-breakout-cluster).
>
> Per `feedback_no_rushing_per_strategy_tweak` + `project_no_apriori_strategy_pruning` + foundational sequence (B660 in flight): all fires/yr projections PENDING B660; no code changes in this batch (B676 is doc-only).

---

## Audience

Two:

1. **External reviewer** — for you: the breakout cluster differs from prior clusters because (a) the underlying patterns are the MOST academically-grounded in the whole strategy roster — George-Hwang 2004 JF 52-week-high momentum anomaly, Bulkowski 2005 chart-pattern empirical work, classical breakout literature (Faith 2007 Turtle Trading, Connors + Raschke 1996, Wilder 1978) ALL apply legitimately. **Pattern M / Pattern Q (no peer-review) DO NOT APPLY** to the same degree as ICT/SMC/smart-money clusters. (b) The cluster has the **MOST forensic-fix evidence** of any cluster — B589 added `close_in_top_40pct_of_range`, B590 added ATR-band filter, B608 obv_bullish refactor, B654 cpr_narrow_tight all came from explicit post-1A-alpha forensic findings; the strategies are EMPIRICAL-FIX-anchored, not just owner-spec. (c) **CC1 next-open-after-gap concern from B673** PARTIALLY applies — breakout strategies DO have a gap-after-detection issue but it's a momentum-continuation gap (price keeps going up after the breakout), not a mean-reversion gap (M&A target-style). Capturable fraction is higher than M&A targets. (d) The cluster has **STRONG intra-family redundancy** — 4 of 19 are 52w-high/low variants, 6 of 19 are Donchian variants, 4 of 19 are retest-pattern variants — Pattern N intra-cluster collinearity is acute.

2. **Future readers** — [Cluster scope inventory](#cluster-scope-inventory) below.

---

## Methodology adaptations for breakout cluster

### 1. Legitimate academic anchor — Pattern M / Pattern Q DO NOT apply to most strategies

Unlike the SMC + ICT clusters (where Pattern M / Q applied to 10+ of 12+ strategies), the breakout cluster has GENUINE peer-reviewed methodology backing for most strategies:

| Strategy | Citation | Peer-review level |
|---|---|---|
| **52w_high_breakout family** | George-Hwang 2004 JF "The 52-Week High and Momentum Investing" | ✅ Top finance journal; documented anomaly |
| **52w_high_breakout_pullback_long + 52w_low_breakdown_pullback_short** | Bulkowski 2005 *Encyclopedia of Chart Patterns* retest-on-lower-volume thesis | ✅ Published, widely-cited chart-pattern methodology |
| **Donchian breakout family** | Faith 2007 *The Way of the Turtle* (Dennis-Eckhardt Turtle Trading) + Donchian's original 1960s work | ✅ Classical trend-following methodology |
| **break_retest family** | Bulkowski 2005 retest absorption thesis | ✅ Same as 52w-retest family |
| **Force index breakout** | Elder 1993 *Trading for a Living* | ✅ Published methodology (cited in B626 docstring) |
| **squeeze_breakout** | Carter 2008 TTM Squeeze | ⚠ Trader-methodology book; less peer-reviewed than the above but widely accepted |
| **inside_bar_breakout** | Classical price-action literature | ⚠ No specific peer-reviewed citation; generic pattern recognition |
| **volume_spike_breakout family** | Lo + Wang 2000 RFS volume-as-information + Akarim + Sevim 2013 (volume-price relationship) | ✅ Peer-reviewed |
| **classification_change_breakout_long** | Brogaard-Heath-Saadi 2019 reclassification literature | ✅ JFE-tier peer-review |

**Pattern Q applies WEAKLY to:** inside_bar_breakout (no specific cite); squeeze_breakout (trader-book not peer-review).

### 2. Forensic-fix density — Pattern A (default-True silent-gap) almost fully swept

The breakout cluster has the most B-batch forensic-fix evidence of any cluster:

| Forensic batch | Fix | Cluster impact |
|---|---|---|
| **B582** | `break_52w_high` / `break_52w_low` producer fix (was buggy DC20-anchored) | 52w_high_breakout + 52w_low_breakdown |
| **B584** | Donchian 10 breakout producer fix (excludes today from window) | donchian_10_breakout + donchian_breakdown_short + donchian_breakout_long |
| **B586** | vol_spike_17x + sector_outperforming_spy added to 52w_high_breakout | 52w_high_breakout |
| **B589** | close_above_open + close_in_top_40pct_of_range added across breakout family | ALL post-B589 strategies (15 of 19) |
| **B590** | 52w_pullback redesign: stable pre-breakout reference + ATR band + 3-candle time filter | 52w_high_breakout_pullback_long + 52w_low_breakdown_pullback_short |
| **B591** | donchian_10_breakout LOCAL signals (dc10_breakout_up_1pct + dc10_strong_breakout_up) | donchian_10_breakout |
| **B594/B596** | donchian_breakout_retest_long + donchian_breakdown_retest_short LOCAL strong variants | dc20_resistance_break_retest_strong + symmetric short |
| **B598** | above_avwap_20low / below_avwap_20high producer (B598/B612 symmetric pair) | volume_spike_breakout + r1_break_retest |
| **B605** | 52wh_break_retest + 52wl_break_retest_short producers (NEW Class 7 inverse) | 52wh_break_retest + 52wl_break_retest_short |
| **B608** | break_retest_volume obv_bullish refactor (B617) | break_retest_volume |
| **B612 F2** | below_avwap_20high silent-gap fix (positive symmetric pair) | volume_spike_breakout SHORT + retest SHORT + r1_break_retest SHORT |
| **B626** | force_index_breakout: F1 silent-gap fix + (a) bullish-bar gate + F2 docstring | force_index_breakout |
| **B630** | below_ema_200 producer-additive sweep across screener.py | ALL breakout strategies with `below_ema_200` |
| **B663** | Pattern A default-True → False WAVE 1 family sweep | ALL breakout strategies with `price_above_ema_200` |

**Net effect:** Pattern A is essentially CLEAN across the breakout cluster post-B663. Pattern N (intra-cluster collinearity) is the cluster's dominant concern.

### 3. CC1 next-open-after-gap haircut — applies BUT in continuation direction not mean-reversion

Breakout strategies have a structural gap-after-detection feature: when a breakout fires (e.g., 52w_high_breakout), price often gaps up ON the breakout bar — the engine detects at close and enters next-open after another potential gap up. Unlike B673 CC1 (M&A target: gap UP then mean-reversion DOWN — engine buys at the wrong time), breakout entry IS in the same direction as the continuation pattern. So next-open IS at a higher price than detection close BUT in the trade's favor — the engine "pays the gap" but the trade benefits if continuation persists.

**Net:** CC1 partially applies but is LESS damaging than the M&A target case. The capturable-after-gap haircut is smaller (the gap is part of the move, not against it).

### 4. Cluster's dominant concern: intra-family redundancy (Pattern N)

19 strategies on a small primitive set:

| Primitive | Strategies |
|---|---|
| `break_52w_high` / `break_52w_low` (B582 producer) | 52w_high_breakout + 52w_low_breakdown + (cross-cluster with 52w_high_breakout_with_smart_money_long via smart_money_sleeve walked B613) |
| `near_52w_high_retest_long` / `near_52w_low_retest_short` (B590 producer) | 52w_high_breakout_pullback_long + 52w_low_breakdown_pullback_short |
| `year_high_break_retest_long` / `year_low_break_retest_short` (B605 producer) | 52wh_break_retest + 52wl_break_retest_short |
| `resistance_break_retest` / `support_break_retest` (B-anchored on DC20) | break_retest_volume + dc20_break_retest |
| `dc10_breakout_up` / `_dn` (B584 producer) | donchian_breakout_long + donchian_breakdown_short |
| `dc10_breakout_up_1pct` / LOCAL `dc10_strong_breakout_up` (B591) | donchian_10_breakout |
| `dc20_resistance_break_retest_strong` / `_support_*` LOCAL (B594/596) | donchian_breakout_retest_long + donchian_breakdown_retest_short |
| `force_index_cross_up` / `_dn` (Elder methodology producer) | force_index_breakout |
| `squeeze_on_release` (TTM Squeeze) | squeeze_breakout (+ squeeze_breakout_with_smart_money_long walked SM-36) |
| `inside_bar` + ADX | inside_bar_breakout |
| `vol_spike_15x` + `dc10_breakout_up` | volume_spike_breakout + volume_spike_breakout_retest |
| `below_prev_low` | prev_day_low_breakdown |

**13 distinct primitives across 19 strategies** ⇒ effective hypothesis count ≈ 13, not 19. **2 sub-families have heavy overlap:** 52w-family (4 strategies) + Donchian-family (6 strategies). Pattern N intra-cluster ablation is the cluster's flagship cube test.

### 5. CHECKLIST (r) timeframe-mismatch concern — partial applicability

Several breakout strategies combine **daily-bar signals** (52w/Donchian/inside_bar EVENT triggers) with **higher-timeframe trend gates** (EMA-200 = ~10 months of data; sector_outperforming_spy = 20 days). CHECKLIST (r) timeframe-mismatch concern applies but ALL strategies use the gates AS confluence (not contradiction), so the mismatch is mild.

---

## Reviewer findings response matrix

> Pre-emptive matrix awaiting external reviewer pass on this doc.

| # | Finding | Severity | Status | Action |
|---|---|---|---|---|
| _F-pending_ | Awaiting external reviewer | — | OPEN | Will tabulate post-review |

---

## Cluster scope inventory

**19 strategies in `breakout` category.** Sub-cluster grouping:

| Sub-cluster | # strategies | Strategies |
|---|---|---|
| **A — 52-week breakout family (4)** | 4 | BR-1 `strat_52w_high_breakout` / BR-2 `strat_52w_high_breakout_pullback_long` / BR-3 `strat_52w_low_breakdown` / BR-4 `strat_52w_low_breakdown_pullback_short` |
| **B — 52w break-retest family (2)** | 2 | BR-5 `strat_52wh_break_retest` / BR-6 `strat_52wl_break_retest_short` |
| **C — Generic break-retest family (2)** | 2 | BR-7 `strat_break_retest_volume` (dual) / BR-8 `strat_dc20_break_retest` (dual) |
| **D — Donchian family (5)** | 5 | BR-9 `strat_donchian_10_breakout` (dual) / BR-10 `strat_donchian_breakout_long` / BR-11 `strat_donchian_breakdown_short` / BR-12 `strat_donchian_breakout_retest_long` / BR-13 `strat_donchian_breakdown_retest_short` |
| **E — Volume-spike breakout family (2)** | 2 | BR-14 `strat_volume_spike_breakout` / BR-15 `strat_volume_spike_breakout_retest` |
| **F — Misc breakout (4)** | 4 | BR-16 `strat_force_index_breakout` (dual) / BR-17 `strat_inside_bar_breakout` / BR-18 `strat_prev_day_low_breakdown` / BR-19 `strat_squeeze_breakout` |

**Cross-cluster overlap (walked in smart-money cluster):**
- `strat_52w_high_breakout_with_smart_money_long` (SM-34, B613-closed) — confluence wrap over BR-1
- `strat_52w_high_breakout_with_smart_money_vol_below_long` (SM-35, B613-closed) — B-twin
- `strat_squeeze_breakout_with_smart_money_long` (SM-36, Pattern E candidate) — confluence wrap over BR-19
- `strat_donchian_breakout_with_smart_money_long` (SM-39, Pattern E candidate) — confluence wrap over BR-10

---

## Cross-strategy patterns (breakout cluster)

### Pattern T (NEW for breakout): forensic-fix density — strategies are POST-FIX designs needing cube re-validation

**Affects:** all 19 (varying depth).

**Concern:** breakout cluster has the most B-batch forensic-fix evidence (see §2 methodology). The post-fix designs need cube re-validation — symmetric with B262/B278 forensic-fix re-validation tickets from SMC cluster. Pattern T parallels the smart-money cluster's "B262 + B278 fix re-validation" but at CLUSTER scope (12+ batches affected this cluster).

**Step 7 disposition:** every walk should note its post-fix lineage + flag whether cube re-validates the latest fix design.

### Pattern N (carried + EXTENDED): intra-family redundancy is acute

**Affects:** all 19. Specifically:
- 52w-family: 4 strategies (BR-1/2/3/4) on `break_52w_*` + `near_52w_*_retest_*`
- Donchian-family: 6 strategies (BR-9/10/11/12/13 + smart_money wrap SM-39) on DC10/DC20
- Break-retest family: 4 strategies (BR-5/6/7/8) on retest primitives at different anchors

**Within-cluster effective hypothesis count ≈ 13 (not 19);** cube replay marginal-contribution test required.

### Pattern U (NEW for breakout): 5-gate post-B589 family signature

**Affects:** 8 strategies (BR-1, BR-3, BR-5, BR-9, BR-10, BR-11, BR-12, BR-13).

**Concern:** post-B589 the breakout family standardized on a 5-gate signature: `breakout EVENT + vol_confirm + macd_confirm + close_above_open + close_in_top_40pct_of_range`. This is a CLEAN design pattern but creates Pattern N risk — 8 strategies share most of their gate structure.

**Step 7 disposition:** cube replay should explicitly compare the 5-gate variants pairwise to surface which differ economically vs cosmetically.

### Pattern V (NEW for breakout): Bulkowski 2005 retest absorption thesis — vol_below_avg gate

**Affects:** 6 strategies — BR-2, BR-4, BR-5, BR-6, BR-12, BR-13 (all retest strategies use `vol_below_avg` per Bulkowski thesis).

**Concern:** the Bulkowski "retest forms on lower volume than initial break" thesis is empirically published BUT cited generically. Cube replay against breakouts WITHOUT vol_below_avg confluence settles whether the retest variants earn registry slots.

### Pattern A (carried) — Pattern A ✅ verified clean post-B663 + B630

All 19 strategies use `price_above_ema_200` (default-False post-B663) or `below_ema_200` (B630 producer-additive). 0 silent-gap instances per grep.

### Pattern O (carried + EXTENDED for breakout)

Hardcoded tolerances:
- `vol_spike_17x` = 1.7x (B586 owner-pick from 1.5x-2x range)
- `vol_spike_15x` = 1.5x (Donchian + dc20_break_retest)
- `vol_above_avg` = 1.0x (donchian_10_breakout)
- `vol_below_avg` = <1.0x (Bulkowski retest family)
- ATR band coefficients: `0.5*ATR(14)` (B592 dc10_strong_breakout + B594 dc20_strong); `1.5*ATR(14)` (B605 52wh/52wl break_retest)
- `0.99` / `1.01` factors (B590 pullback retest "below peak / above trough" thresholds)
- `close_in_top_40pct_of_range` / `close_in_bottom_40pct_of_range` = 40% bar position
- `3pct` retest tolerance (B590 pullback variant)
- `breakout_3_candles_old` (B590 time filter)

**~10 hardcoded parameters** across the cluster; sensitivity-untested.

---

## Cluster current state table

| BR # | Function name | Direction | Sub-cluster | Key gates | Has EMA gate | Pattern flags | Walk status |
|---|---|---|---|---|---|---|---|
| BR-1 | `strat_52w_high_breakout` | long | A 52w | 5-gate post-B589 | ❌ (sector ETF substitute) | T + U + V | ⏳ Walked B676 |
| BR-2 | `strat_52w_high_breakout_pullback_long` | long | A 52w | B590 7-condition aggregated | ❌ | T + V (Bulkowski) | ⏳ Walked B676 |
| BR-3 | `strat_52w_low_breakdown` | short | A 52w | 5-gate post-B589 inverse | ❌ | T + U + B671 borrow-trap | ⏳ Walked B676 |
| BR-4 | `strat_52w_low_breakdown_pullback_short` | short | A 52w | B590 inverse | ❌ | T + V + B671 borrow-trap | ⏳ Walked B676 |
| BR-5 | `strat_52wh_break_retest` | long | B 52w-retest | 7-gate B605 | ✅ | T + V (Bulkowski) + U | ⏳ Walked B676 |
| BR-6 | `strat_52wl_break_retest_short` | short | B 52w-retest | 7-gate B605 inverse | ✅ | T + V + U + B671 borrow-trap | ⏳ Walked B676 |
| BR-7 | `strat_break_retest_volume` | dual | C generic-retest | 4-gate dual B608 | ❌ (OBV substitute) | T + V + obv_bullish (B617 refactor) | ⏳ Walked B676 |
| BR-8 | `strat_dc20_break_retest` | dual | C generic-retest | 3-gate dual | ❌ (ADX substitute) | T + Pattern N (DC20 reskin of BR-7) | ⏳ Walked B676 |
| BR-9 | `strat_donchian_10_breakout` | dual | D Donchian | 6-gate dual B591 LOCAL strong | ❌ | T + U + ATR-band | ⏳ Walked B676 |
| BR-10 | `strat_donchian_breakout_long` | long | D Donchian | 5-gate post-B589 | ❌ (MACD substitute) | T + U + Pattern N | ⏳ Walked B676 |
| BR-11 | `strat_donchian_breakdown_short` | short | D Donchian | 5-gate B595 inverse | ❌ | T + U + B671 borrow-trap | ⏳ Walked B676 |
| BR-12 | `strat_donchian_breakout_retest_long` | long | D Donchian | 5-gate B596 strong | ❌ | T + V + U | ⏳ Walked B676 |
| BR-13 | `strat_donchian_breakdown_retest_short` | short | D Donchian | 5-gate B596 strong inverse | ❌ | T + V + U + B671 borrow-trap | ⏳ Walked B676 |
| BR-14 | `strat_volume_spike_breakout` | dual | E vol-spike | Multi-gate AVWAP family | ✅ EMA + AVWAP | T + Pattern N (DC10 reskin) | ⏳ Walked B676 |
| BR-15 | `strat_volume_spike_breakout_retest` | dual | E vol-spike | Multi-gate B596 retest variant | ✅ | T + Pattern N + V | ⏳ Walked B676 |
| BR-16 | `strat_force_index_breakout` | dual | F misc | 3-gate B626 (Elder 1993) | EMA-20 | T + B626 forensic-fix | ⏳ Walked B676 |
| BR-17 | `strat_inside_bar_breakout` | long | F misc | 3-gate (inside_bar + ADX + VWAP) | ❌ (VWAP substitute) | Pattern Q + B621 FAIL_FIRE projected | ⏳ Walked B676 |
| BR-18 | `strat_prev_day_low_breakdown` | short | F misc | TBD-gate (below_prev_low family) | ❌ | T + B671 borrow-trap | ⏳ Walked B676 |
| BR-19 | `strat_squeeze_breakout` | dual | F misc | 2-gate (squeeze_on_release + bar) | ❌ (close_above/below_open) | Pattern Q (Carter 2008) + Pattern N (cross-cluster SM-36) | ⏳ Walked B676 |

**Net cluster state:**
- 19 functions / 28 (strategy × direction) cells (9 dual via `_strat3`)
- 3 with EMA gate; 16 without (substituted by sector ETF / OBV / ADX / MACD / VWAP / TTM-squeeze)
- Pattern A ✅ verified clean across cluster
- Pattern N is the dominant concern (13 effective primitives over 19 strategies)
- 6 strategies use Bulkowski 2005 retest absorption thesis (Pattern V)
- 8 strategies in 5-gate post-B589 family (Pattern U)
- 7 SHORT strategies subject to B671 centralized borrow-trap gate (BR-3, BR-4, BR-6, BR-11, BR-13, BR-15 SHORT branch, BR-16 SHORT branch, BR-18, BR-19 SHORT branch)

---

## Per-strategy walks

### BR-1. `strat_52w_high_breakout` (Batch 586+589, 52w family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 5-gate LONG; **George-Hwang 2004 JF momentum anchor — best-anchored breakout strategy.** Cluster-wide canonical 5-gate post-B589 design template.

#### Step 1 — Read the code

[screener.py:1615-1636](backtest/signals/screener.py#L1615-L1636):

```python
def strat_52w_high_breakout(s):
    fires = (s.get("break_52w_high")
             and s.get("vol_spike_17x")
             and s.get("sector_outperforming_spy")
             and s.get("close_above_open")
             and s.get("close_in_top_40pct_of_range"))
```

**5-gate LONG.** Canonical 5-gate post-B589 family signature.

| Gate | Meaning |
|---|---|
| `break_52w_high` | EVENT (B582 producer): today's close > prior 252-day max-HIGH (excludes today) |
| `vol_spike_17x` | EVENT: today's volume > 1.7x trailing 20-bar mean (B586 owner-picked) |
| `sector_outperforming_spy` | STATE (B586): sector SPDR ETF 20-day return > SPY 20-day return |
| `close_above_open` | EVENT: bullish bar |
| `close_in_top_40pct_of_range` | EVENT (B589): close in top 40% of today's H-L range |

#### Step 2 — Classify

- Category: `breakout`; LONG; B291 default; last touched B589

#### Step 3 — Producer source-read + temporality

- `break_52w_high`: B582 producer fix — true when today's close > max(HIGH, 252-day window ending YESTERDAY)
- `vol_spike_17x`: bar-of-fire EVENT — `volume[-1] / volume[-21:-1].mean() > 1.7`
- `sector_outperforming_spy`: STATE — sector ETF 20d / SPY 20d
- `close_above_open` + `close_in_top_40pct_of_range`: bar-of-fire EVENTs from candle structure
- EVENT/STATE: 4 EVENT + 1 STATE

**EVENT-anchored structure with quality close-strength gate.** Best-in-class temporality.

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "George-Hwang 2004 JF - new highs attract buyers" | ✅ **REAL CITATION** — George + Hwang 2004 Journal of Finance "The 52-Week High and Momentum Investing" documents the anomaly. Anchor citation is legitimate peer-reviewed top-tier finance |
| "Volume >1.7x confirms institutional conviction" | ⚠ **Pattern O** — 1.7x is owner-pick from 1.5x-2x range; not empirically calibrated against actual volume distributions |
| "Sector ETF outperforming SPY 20d - trade strong sectors only" | ✅ Defensible at the relative-strength level |
| "Bullish bar with close in top 40% of range - strong-close signal (B589 added)" | ✅ B589 addition is a forensic-fix improvement; close-strength gate is canonical price-action discipline |
| Implicit "5-gate filter produces high-quality breakouts" | ⚠ **CC1 partial** — 52w breakouts gap (price keeps going); engine enters next-open at higher price than detection close. Capturable continuation > capturable headline but the gap is the entry cost |

#### Step 5 — OPEN_INVESTIGATIONS grep

- Pattern N cross-cluster with SM-34 `strat_52w_high_breakout_with_smart_money_long` (B613-closed Pattern E) + SM-35 B-twin
- B582 + B586 + B589 forensic-fix lineage (Pattern T)
- Pattern O `vol_spike_17x` calibration unverified

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — BR-3 `strat_52w_low_breakdown`
- Economic symmetry: ⚠ **Equity upward drift bias** — 52w-high breakouts more common than 52w-low breakdowns in upward-drift equity. SHORT side has lower fire count + carries B671 borrow-trap

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-cluster-anchor citation ✅** | George-Hwang 2004 JF is REAL anchor; cluster-positive | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-pattern-N cross-cluster** | SM-34 + SM-35 confluence wraps walked B613; SM-39 donchian wrap; cube ablation should surface confluence-wrap marginal contribution | MEDIUM | Pattern N |
| **F-pattern-U canonical 5-gate template** | Standard breakout family signature; ablation against 4-gate / 3-gate baselines | MEDIUM | Pattern U |
| **F-pattern-T forensic-fix lineage** | B582 + B586 + B589 (3 fixes); post-fix design needs cube re-validation | MEDIUM | Pattern T |
| **F-CC1 partial gap-after-detection** | Continuation breakout gaps in trade direction; engine entry pays the gap | LOW-MEDIUM | CC1 |
| **F-pattern-O vol_spike_17x calibration** | Owner-pick threshold; cube sensitivity sweep (1.5x / 1.7x / 2.0x) | LOW | Pattern O |
| F-fire-count | 5-gate AND restrictive; projected ~40-100/yr universe-wide; PASS likely | INFO | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo (best-anchored breakout strategy; minimal changes warranted) |
| (b) Cube ablation marginal-contribution test for sector_outperforming_spy gate (the most-recently-added gate) |
| (c) Cube sensitivity sweep `vol_spike_17x` threshold |
| (d) Cross-cluster Pattern N ablation with SM-34 + SM-35 + SM-39 |
| **(e) RECOMMENDED — (a) + (d). BR-1 is the cluster's flagship strategy; cross-cluster ablation against confluence wraps is the highest-leverage test. Pre-cube no code change.** |

**My recommendation: (e).**

**Awaiting owner direction on BR-1:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (e)
2. Pattern N flagship cross-cluster ablation scope confirmation
3. Pattern O vol_spike_17x sensitivity sweep priority

---

### BR-2. `strat_52w_high_breakout_pullback_long` (Batch 586+590, 52w family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 1-gate LONG (single-boolean consumer) but the producer encodes 7 conditions; B590 redesign anchor.

#### Step 1 — Read the code

[screener.py:1639-1655](backtest/signals/screener.py#L1639-L1655):

```python
def strat_52w_high_breakout_pullback_long(s):
    fires = s.get("near_52w_high_retest_long", False)
```

**1-gate LONG (Pattern S shell over multi-condition producer flag).** The single signal `near_52w_high_retest_long` encodes B590-redesigned 7-condition aggregated logic.

#### Step 2 — Classify

- Category: `breakout`; LONG; last touched B590 (post-B587 redesign)

#### Step 3 — Producer source-read + temporality

`near_52w_high_retest_long` is a producer flag encoding 7 conditions per docstring:
- (a) breakout_occurred: max CLOSE in last 30 trading days > year_high_pre30
- (b) within_3pct_high: today's close within ±3% of year_high_pre30
- (c) today_below_peak: today's close < 30-day max close × 0.99
- (d) vol_below_avg (Bulkowski retest): today's volume / 20-bar avg < 1.0
- (e) close_above_open: bullish reversal bar
- (f) breakout_3_candles_old: time filter — at least 3 trading days elapsed since first breakout bar
- (g) within_atr_band_long: today's close ≥ year_high_pre30 − ATR(14)

EVENT/STATE: predominantly EVENT-shaped at bar of fire.

**Pattern S concern (single-gate shell):** the strategy is a 1-line consumer; B590's 7-condition AND logic is invisible at the call site. Same anti-pattern as ICT-5/6/11/12.

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Classical breakout pullback" | ✅ Defensible — breakout-pullback pattern is canonical price-action methodology |
| "Bulkowski 2005 retest absorption thesis (vol_below_avg)" | ✅ Real citation; well-anchored |
| "Higher conviction than chase-the-breakout" | ⚠ Empirical claim without B-batch validation; cube settles |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B590 forensic-redesign (Pattern T)
- Pattern S single-gate shell

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — BR-4 `strat_52w_low_breakdown_pullback_short`

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-S single-gate shell** | 1-line consumer over 7-condition producer; B590 logic invisible at call site | MEDIUM | Pattern S |
| **F-pattern-V Bulkowski anchor** | Citation legitimate ✅ | INFO / ✅ POSITIVE | Pattern V |
| **F-pattern-T B590 redesign re-validation** | Post-fix design needs cube validation | MEDIUM | Pattern T |
| F-fire-count | 7-condition AND restrictive; projected ~20-50/yr universe-wide; borderline | MEDIUM | F4 |

**Options:** (a) status quo / (b) cube validates B590 redesign / (c) Pattern S explicit-gate refactor (expose conditions at strategy level) / **(d) RECOMMENDED — (b) post-B660 cube replay validates B590 design.**

**My recommendation: (d).**

**Awaiting owner direction on BR-2:**
1. (a)/(b)/(c)/(d) — recommendation (d)

---

### BR-3. `strat_52w_low_breakdown` (Batch 586+587+589, 52w family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 5-gate SHORT; symmetric inverse of BR-1.

#### Step 1 — Read the code

[screener.py:2378-2398](backtest/signals/screener.py#L2378-L2398):

```python
fires = (s.get("break_52w_low") and s.get("vol_spike_17x")
         and s.get("sector_underperforming_spy")
         and s.get("close_below_open") and s.get("close_in_bottom_40pct_of_range"))
```

**5-gate SHORT.** Symmetric mirror of BR-1.

#### Step 2-7 (compact — symmetric with BR-1)

- Category `breakout`; SHORT; B291 default; B589 family
- George-Hwang 2004 JF momentum applies inverse-symmetrically (52w-low names continue lower in literature)
- **B671 DTC>8 borrow-trap gate applies**
- Fire-count: 52w-low breakdowns less common than 52w-high breakouts in upward-drift equity; projected ~25-70/yr universe-wide
- Same Pattern T + U + Pattern N concerns

**Options:** same as BR-1; bundled. **My recommendation: (e) bundled with BR-1.**

**Awaiting owner direction on BR-3:** bundled with BR-1.

---

### BR-4. `strat_52w_low_breakdown_pullback_short` (Batch 586+590, 52w family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 1-gate SHORT; symmetric mirror of BR-2.

[screener.py:1658-1669](backtest/signals/screener.py#L1658-L1669) — symmetric. `near_52w_low_retest_short` producer flag encodes B590-mirror 7-condition logic. **B671 borrow-trap.** Fire-count ~10-30/yr universe-wide.

**Options:** same as BR-2; bundled. **My recommendation: (d) bundled.**

**Awaiting owner direction on BR-4:** bundled with BR-2.

---

### BR-5. `strat_52wh_break_retest` (Batch 605, 52w-retest family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **7-gate LONG**; B605 NEW (52w-anchored, NOT DC20-anchored — fixes prior bug in resistance_break_retest). Has EMA gate ✅ (most-gated breakout strategy in cluster).

#### Step 1 — Read the code

[screener.py:2543-2596](backtest/signals/screener.py#L2543-L2596):

```python
fl = (s.get("year_high_break_retest_long")
      and s.get("near_52w_high")
      and s.get("price_above_ema_200")
      and s.get("close_above_open")
      and s.get("close_in_top_40pct_of_range")
      and s.get("vol_below_avg")
      and s.get("above_avwap_20low"))
```

**7-gate LONG.** Most-gated breakout strategy + AVWAP confluence + B605 NEW retest anchor.

| Gate | Meaning |
|---|---|
| `year_high_break_retest_long` | EVENT (B605 producer): some bar 2-8 ago closed > year_high; subsequent bar's LOW touched within 1.5×ATR; today's close >= year_high |
| `near_52w_high` | STATE: today's close >= 98% of 252-day max high |
| `price_above_ema_200` | STATE: long-term uptrend |
| `close_above_open` | EVENT: bullish bar |
| `close_in_top_40pct_of_range` | EVENT (B589): strong close |
| `vol_below_avg` | EVENT (Bulkowski retest): volume / 20-bar avg < 1.0 |
| `above_avwap_20low` | STATE: close > AVWAP anchored at trailing 20-bar low |

#### Step 2 — Classify

- Category: `breakout`; LONG; B291 default; last touched B612 (B598 producer adds above_avwap_20low)

#### Step 3 — Producer source-read + temporality

- `year_high_break_retest_long`: B605 NEW producer (replaces buggy DC20-anchored `resistance_break_retest` per B605 F1 bug-fix walk)
- All other gates verified
- EVENT/STATE: 4 EVENT + 3 STATE

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "(B605 NEW; 52w-anchored, NOT DC20-anchored)" | ✅ Forensic-fix from B605 walk — B605 identified resistance_break_retest as DC20-anchored bug; created year_high_break_retest_long as correct 52w-anchored replacement |
| "Bulkowski 2005 retest absorption thesis (vol_below_avg)" | ✅ Real anchor |
| "AVWAP confluence (B598/B612 symmetric pair)" | ✅ B612 F2 forensic-fix established symmetric pair |
| "near_52w_high" + "year_high_break_retest" co-occurrence | ⚠ Possibly redundant — `year_high_break_retest_long` already implies "near year_high" structurally; the `near_52w_high` gate at 98% may be near-tautological |

#### Step 5 — OPEN_INVESTIGATIONS grep

- Pattern T: B605 forensic-fix + B612 F2 silent-gap fix lineage
- Pattern N: 7-gate AND with possible internal redundancy (near_52w_high + year_high_break_retest_long)

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — BR-6 `strat_52wl_break_retest_short`

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-T B605 forensic-fix** | Replaces buggy DC20-anchored predecessor; needs cube validation | MEDIUM | Pattern T |
| **F-internal-redundancy** | near_52w_high + year_high_break_retest_long are likely correlated; gate marginal contribution unknown | MEDIUM | Pattern N |
| **F-pattern-V Bulkowski + AVWAP confluence** | Multiple legitimate anchors | INFO / ✅ POSITIVE | Pattern V |
| F-fire-count | 7-gate AND very restrictive; projected ~15-40/yr universe-wide; borderline FAIL min_trades=30 per regime | MEDIUM | F4 |

**Options:** (a) status quo / (b) drop near_52w_high gate (redundant with year_high_break_retest_long) / (c) cube ablation for near_52w_high marginal contribution / **(d) RECOMMENDED — (c) post-B660 cube settles redundancy.**

**My recommendation: (d).**

**Awaiting owner direction on BR-5:**
1. (a)/(b)/(c)/(d) — recommendation (d)
2. Pattern N internal-redundancy ablation scope

---

### BR-6. `strat_52wl_break_retest_short` (Batch 605, 52w-retest family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 7-gate SHORT; symmetric mirror of BR-5.

[screener.py:2598-2640](backtest/signals/screener.py#L2598-L2640) — symmetric with `year_low_break_retest_short` + `near_52w_low` + `below_ema_200` + `close_below_open` + `close_in_bottom_40pct_of_range` + `vol_below_avg` + `below_avwap_20high`. **B612 F2 silent-gap fix anchors B-twin.** **B671 borrow-trap gate applies.** Fire-count rarer than BR-5 (~10-25/yr).

**Options:** same as BR-5; bundled. **My recommendation: (d) bundled.**

**Awaiting owner direction on BR-6:** bundled with BR-5.

---

### BR-7. `strat_break_retest_volume` (Batch 608+617, generic-retest family, walked B676 — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 4-gate dual; B617 obv_bullish refactor (switched from obv_rising for symmetric OBV).

#### Step 1 — Read the code

[screener.py:2642-...](backtest/signals/screener.py#L2642):

```python
fl = (s.get("resistance_break_retest") and s.get("obv_bullish")    # B617
      and s.get("close_above_open") and s.get("vol_below_avg"))
fs = (s.get("support_break_retest") and s.get("obv_bearish")
      and s.get("close_below_open") and s.get("vol_below_avg"))
```

**4-gate dual.** Combines DC20-anchored retest primitive + OBV-direction + bullish/bearish bar + Bulkowski vol_below_avg.

#### Step 2 — Classify

- Category: `breakout`; dual; B291 default; last touched B617 (OBV refactor)

#### Step 3 — Producer source-read + temporality

- `resistance_break_retest` / `support_break_retest`: DC20-anchored multi-bar pattern (B608)
- `obv_bullish` / `obv_bearish`: STATE OBV direction (B617 positive symmetric)
- `close_above/below_open`: bar-of-fire EVENT
- `vol_below_avg`: EVENT
- EVENT/STATE: 3 EVENT + 1 STATE per direction

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "BUG-111 multi-bar pattern (DC20)" | ✅ B608 was Stage 4 walk that fixed this pattern |
| "Bulkowski 2005 retest absorption thesis" | ✅ Real |
| "B617: switched from obv_rising to obv_bullish for symmetric" | ✅ Forensic-fix; B617 refactor |

#### Step 5 — OPEN_INVESTIGATIONS grep

- Pattern T: B608 + B617 forensic lineage
- Pattern N: cross-strategy with BR-8 `strat_dc20_break_retest` (both consume resistance/support_break_retest)

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Already dual
- **B671 borrow-trap applies SHORT side**

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-N BR-7 vs BR-8 reskin** | Both consume DC20 retest primitive; BR-7 adds OBV+vol+bar; BR-8 adds vol_spike_15x+ADX. Different gate stacks but same underlying signal | MEDIUM-HIGH | Pattern N |
| **F-pattern-T B608+B617 forensic** | Post-fix design needs cube validation | MEDIUM | Pattern T |
| F-pattern-V | Bulkowski legitimate | INFO / ✅ | Pattern V |
| F-fire-count | 4-gate AND projected ~25-60/yr per direction; modest PASS likely | INFO | F4 |

**Options:** (a) status quo / (b) cube BR-7 vs BR-8 ablation / **(c) RECOMMENDED — (b) post-B660 flagship Pattern N intra-cluster test.**

**My recommendation: (c).**

**Awaiting owner direction on BR-7:**
1. (a)/(b)/(c) — recommendation (c)
2. BR-7 vs BR-8 cube ablation as Pattern N flagship

---

### BR-8. `strat_dc20_break_retest` (generic-retest family, walked B676 — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate dual; consumes same DC20 retest primitive as BR-7 but with different confluence gates.

#### Step 1 — Read the code

[screener.py:2449-...](backtest/signals/screener.py#L2449):

```python
fl = (s.get("resistance_break_retest") and s.get("vol_spike_15x") and s.get("adx_trending"))
fs = (s.get("support_break_retest") and s.get("vol_spike_15x") and s.get("adx_trending"))
```

**3-gate dual.** DC20 retest + vol_spike + ADX (no Bulkowski vol_below_avg; uses ADX trend filter instead).

#### Step 2-7 (compact — Pattern N reskin of BR-7)

- Category `breakout`; dual; B291 default; **N.B.: BR-8's `vol_spike_15x` gate CONTRADICTS Bulkowski thesis — Bulkowski says retest should be LOWER volume, but BR-8 requires HIGHER volume**. Possible thesis-bug — retest with vol spike may be the initial breakout bar, not the retest
- `adx_trending` is a trend-strength gate
- Pattern N with BR-7 (same DC20 retest primitive)
- **B671 borrow-trap SHORT side**
- Fire-count: vol_spike_15x is restrictive; projected ~20-50/yr per direction

**F-thesis-bug:** `vol_spike_15x` on a "retest" pattern contradicts Bulkowski 2005 retest-on-lower-volume thesis. Either (a) BR-8 was designed for a different concept (continuation-on-high-volume, not Bulkowski retest) but named ambiguously, or (b) the vol gate is wrong.

**Options:** (a) status quo / (b) cube BR-7 vs BR-8 ablation / (c) thesis-bug clarification — rename BR-8 OR swap vol_spike → vol_below_avg / **(d) RECOMMENDED — (b) + (c). Cube settles; thesis-clarification batch should explicitly state whether BR-8 is "retest" or "continuation."**

**My recommendation: (d).**

**Awaiting owner direction on BR-8:**
1. Recommendation (d)
2. Thesis-bug clarification — vol_spike on retest is contradictory naming

---

### BR-9. `strat_donchian_10_breakout` (Batch 591+592, Donchian family, walked B676 — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **6-gate dual**; B591 LOCAL strong-breakout variant; ATR-band filter (B592).

#### Step 1 — Read the code

[screener.py:1744-...](backtest/signals/screener.py#L1744):

```python
fl = (s.get("dc10_breakout_up_1pct") and s.get("vol_above_avg")
      and s.get("macd_12_26_9_bullish") and s.get("close_above_open")
      and s.get("close_in_top_40pct_of_range") and s.get("dc10_strong_breakout_up"))
```

**6-gate dual.** B591 LOCAL signals (`dc10_breakout_up_1pct` 1% slack + `dc10_strong_breakout_up` ATR-band).

#### Step 2-7 (compact)

- Category `breakout`; dual; B291 default; B591/B592 forensic
- Pattern T: B591 + B592 redesigned this strategy from scratch (B591 added 1pct slack + strong-breakout LOCAL; B592 closed ATR-band)
- Pattern U: post-B589 5-gate family + 1 LOCAL strong gate = 6 gates
- Pattern N: cross-strategy with BR-10 (donchian_breakout_long) and BR-12 (donchian_breakout_retest_long)
- **B671 borrow-trap SHORT**
- Fire-count: 6-gate AND very restrictive; projected ~15-40/yr per direction; borderline

**Options:** (a) status quo / (b) cube Pattern T re-validation + cube Pattern N intra-Donchian ablation (BR-9 vs BR-10 vs BR-12) / **(c) RECOMMENDED — (b) flagship Donchian-family ablation.**

**My recommendation: (c).**

**Awaiting owner direction on BR-9:**
1. (a)/(b)/(c) — recommendation (c)
2. Donchian-family flagship Pattern N ablation (6 Donchian strategies; effective hypothesis count ≈ 3)

---

### BR-10. `strat_donchian_breakout_long` (Batch 595, Donchian family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 5-gate LONG; canonical post-B589 Donchian breakout.

#### Step 1 — Read the code

[screener.py:2314-...](backtest/signals/screener.py#L2314):

```python
fires = (s.get("dc10_breakout_up") and s.get("vol_spike_15x")
         and s.get("macd_12_26_9_bullish") and s.get("close_above_open")
         and s.get("close_in_top_40pct_of_range"))
```

**5-gate LONG.** Post-B589 family; Donchian-10 breakout (0.2% slack per B584) + vol_spike + MACD + bullish-bar + close-strength.

#### Step 2-7 (compact)

- Category `breakout`; LONG; last touched B595
- Pattern U canonical 5-gate post-B589
- Pattern N: BR-10 vs BR-9 (different DC10 slack: 0.2% vs 1%; BR-10 weaker breakout requirement)
- **Faith 2007 Turtle Trading** classical anchor
- Fire-count: 5-gate moderately restrictive; projected ~30-80/yr universe-wide; PASS likely

**Options:** (a) status quo / (b) cube Pattern N flagship Donchian-family ablation (5+ strategies; effective N ≈ 3). **My recommendation: (b).**

**Awaiting owner direction on BR-10:** bundled with BR-9 in Donchian-family flagship.

---

### BR-11. `strat_donchian_breakdown_short` (Batch 595, Donchian family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 5-gate SHORT; symmetric mirror of BR-10.

[screener.py:2281-...](backtest/signals/screener.py#L2281) — symmetric. `dc10_breakout_dn` + `vol_spike_15x` + `macd_bearish` + `close_below_open` + `close_in_bottom_40pct_of_range`. **B671 borrow-trap.** Fire-count ~15-50/yr (rarer than BR-10).

**Options:** bundled with BR-10. **My recommendation: (b) bundled.**

**Awaiting owner direction on BR-11:** bundled.

---

### BR-12. `strat_donchian_breakout_retest_long` (Batch 596, Donchian family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 5-gate LONG; B596 LOCAL strong variant; Bulkowski retest.

[screener.py:2343-...](backtest/signals/screener.py#L2343):

```python
fires = (s.get("dc20_resistance_break_retest_strong") and s.get("vol_below_avg")
         and s.get("macd_12_26_9_bullish") and s.get("close_above_open")
         and s.get("close_in_top_40pct_of_range"))
```

**5-gate LONG.** B594 LOCAL `dc20_resistance_break_retest_strong` (0.5×ATR strong filter beyond resistance_break_retest); Bulkowski vol_below_avg; MACD; bullish-bar; close-strength.

#### Step 2-7 (compact)

- Pattern T: B594 + B596 forensic LOCAL strong variant
- Pattern V Bulkowski thesis (legitimate citation)
- Pattern N: BR-12 vs BR-7 (different anchor — BR-12 uses DC20-strong; BR-7 uses generic DC20)
- Pattern U canonical 5-gate
- Fire-count: 5-gate restrictive; projected ~15-40/yr; borderline

**Options:** bundled with Donchian-family + retest-family Pattern N flagship. **My recommendation: cube ablation.**

**Awaiting owner direction on BR-12:** bundled.

---

### BR-13. `strat_donchian_breakdown_retest_short` (Batch 596, Donchian family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 5-gate SHORT; symmetric mirror of BR-12.

[screener.py:1811-...](backtest/signals/screener.py#L1811) — symmetric with B594 LOCAL strong + Bulkowski. **B671 borrow-trap.** Fire-count ~10-30/yr.

**Options:** bundled. **My recommendation:** bundled with Donchian-family flagship.

**Awaiting owner direction on BR-13:** bundled.

---

### BR-14. `strat_volume_spike_breakout` (E vol-spike family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Multi-gate dual; AVWAP-confluence + Donchian variant.

[screener.py:1562-...](backtest/signals/screener.py#L1562) — combines `dc10_breakout_up/dn` + `vol_spike_15x` + AVWAP gates (B598 + B612 F2 producer-additive fix for SHORT side silent-gap).

#### Step 2-7 (compact)

- Pattern T: B598 + B612 F2 forensic-fix lineage
- Pattern N: cross-strategy with BR-10 (donchian_breakout_long; same dc10 primitive) — likely high correlation
- **B671 borrow-trap SHORT**
- Pattern Q FAIL_FIRE_STARVED flagged in B621 audit (~0.07/yr universe-wide projected estimator)
- Fire-count: B621 estimator says HIGH RISK FAIL; cube empirical confirms or refutes

**Options:** (a) status quo / (b) cube validates B621 estimator; if confirmed <30/yr → EXPLORATORY marker / (c) Pattern N cube ablation BR-14 vs BR-10.

**My recommendation: (b) + (c) bundled. EXPLORATORY marker candidate if B621 estimator confirmed.**

**Awaiting owner direction on BR-14:**
1. Pattern G EXPLORATORY disposition pending B660 measurement
2. Pattern N ablation against BR-10

---

### BR-15. `strat_volume_spike_breakout_retest` (E vol-spike family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Multi-gate dual; retest variant of BR-14.

[screener.py:1845-...](backtest/signals/screener.py#L1845) — retest variant. **B621 estimator: 0.01/yr universe-wide projected (HIGHEST RISK FAIL_FIRE_STARVED in the entire roster).** Pattern G EXPLORATORY DEPLOYMENT-BLOCK candidate.

**Options:** (a) status quo / (b) **EXPLORATORY marker pre-cube per B621 estimator + W5m precedent / (c) DELETE candidate per B620 squeeze_setup_event_only_long precedent (FAIL_FIRE_STARVED → delete).** Per `project_no_apriori_strategy_pruning`: do NOT auto-delete; surface options.

**My recommendation:** Bundle Pattern G + post-B660 measurement; if cube confirms < 5/yr → owner-direction on (b) EXPLORATORY vs (c) DELETE per B620 precedent.

**Awaiting owner direction on BR-15:**
1. Pattern G EXPLORATORY vs DELETE decision (post-B660)
2. Cross-ref `S5-FIRE-COUNT-CANDIDATES` ticket (BR-15 is on the 5 REAL FAIL list)

---

### BR-16. `strat_force_index_breakout` (F misc family, walked B676 — DUAL, B626 forensic-fixed)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **B626 FORENSIC-FIXED CASE** — pre-B626 SHORT side used `not s.get("price_above_ema_20")` NOT-pattern silent-gap; B626 F1 swap + F2 docstring + (a) bullish/bearish bar gate.

#### Step 1 — Read the code

[screener.py:1683-...](backtest/signals/screener.py#L1683):

```python
fl = (s.get("force_index_cross_up") and s.get("price_above_ema_20")
      and s.get("close_above_open"))
fs = (s.get("force_index_cross_dn") and s.get("below_ema_20")  # B626 F1
      and s.get("close_below_open"))                            # B626 (a)
```

**3-gate dual post-B626.** Elder 1993 Force Index methodology + EMA-20 trend filter + bullish/bearish bar (B626 family standardization).

#### Step 2 — Classify

- Category: `breakout`; dual; last touched B626

#### Step 3 — Producer source-read + temporality

- `force_index_cross_up` / `_dn`: EVENT — Force Index zero-line cross (Elder methodology)
- `price_above_ema_20` / `below_ema_20`: STATE
- `close_above/below_open`: EVENT

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Elder 1993 *Trading for a Living* Force Index methodology" | ✅ **REAL CITATION** — Alexander Elder's published methodology |
| B626 F1 silent-gap fix | ✅ Forensic-fix |
| B626 (a) bullish/bearish bar family standardization | ✅ Pattern U family-template applied |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B626 fix lineage (Pattern T)
- Family-bug surfaced B626 walk: 2 other strategies (strat_awesome_oscillator + strat_stoch_oversold SHORT sides) use same NOT-pattern; queued

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Already dual + **B626 swap made SHORT side fail-safe** (positive symmetric)

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-T B626 forensic** | Post-fix design needs cube validation | MEDIUM | Pattern T |
| **F-elder-1993-anchor ✅** | Legitimate published methodology | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-cluster-family-bug carry** | `not s.get("price_above_ema_20")` family with 2 other strategies (deferred R5) | MEDIUM | family-bug |
| F-fire-count | force_index cross + EMA-20 alignment + bullish bar; projected ~30-80/yr per direction; PASS likely | INFO | F4 |

**Options:** (a) status quo (B626 post-fix design is sound) / (b) cube validates B626 fix / **(c) RECOMMENDED — (b) post-B660 + family-bug sweep on the 2 sibling strategies.**

**My recommendation: (c).**

**Awaiting owner direction on BR-16:**
1. (a)/(b)/(c) — recommendation (c)
2. Family-bug sweep scope (strat_awesome_oscillator + strat_stoch_oversold SHORT)

---

### BR-17. `strat_inside_bar_breakout` (F misc family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate LONG; **Pattern Q candidate** (no specific peer-reviewed citation for inside_bar; generic price-action methodology).

#### Step 1 — Read the code

[screener.py:1672-1680](backtest/signals/screener.py#L1672-L1680):

```python
fires = (s.get("inside_bar") and s.get("adx_trending") and s.get("above_vwap"))
```

**3-gate LONG.** inside_bar pattern + ADX trend strength + above-VWAP.

#### Step 2-7 (compact)

- Category `breakout`; LONG; B291 default
- **Pattern Q:** no specific peer-reviewed citation for inside_bar; generic price-action pattern
- No EMA-200 gate (VWAP substitute)
- Fire-count: inside_bar is common but ADX_trending + above_vwap narrows; projected ~50-150/yr; PASS likely

**Options:** (a) status quo / (b) cite a published methodology if available (e.g., Brian Shannon's *Maximum Trading Gains with Anchored VWAP* for VWAP); pure docstring honesty / **(c) RECOMMENDED — (a) + minor docstring polish to acknowledge Pattern Q.**

**My recommendation: (c).**

**Awaiting owner direction on BR-17:**
1. Pattern Q docstring caveat
2. Cube validation for status-quo design

---

### BR-18. `strat_prev_day_low_breakdown` (F misc family, walked B676)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. SHORT-side breakdown strategy.

[screener.py:2400-...](backtest/signals/screener.py#L2400) — uses `below_prev_low` primitive. **B671 borrow-trap.**

#### Step 2-7 (compact)

- Category `breakout`; SHORT
- Producer `below_prev_low` is a standard candle-pattern primitive from technical.py
- Pattern Q (no specific cite); generic price-action methodology
- Fire-count: below_prev_low is moderately common; PASS likely

**Options:** (a) status quo / (b) docstring caveat (Pattern Q) / cube validation.

**My recommendation: (a) + (b).**

**Awaiting owner direction on BR-18:** Pattern Q reframe.

---

### BR-19. `strat_squeeze_breakout` (F misc family, walked B676 — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate dual; TTM Squeeze (Carter 2008).

#### Step 1 — Read the code

[screener.py:1553-1561](backtest/signals/screener.py#L1553-L1561):

```python
# (compact; squeeze_on_release + close_above_open / close_below_open)
```

**2-gate dual.** TTM squeeze-release EVENT + bullish/bearish bar.

#### Step 2-7 (compact)

- Category `breakout`; dual; **Carter 2008 TTM Squeeze methodology** — Pattern Q WEAK (trader-book, not peer-reviewed but widely accepted)
- Pattern N cross-cluster with SM-36 `strat_squeeze_breakout_with_smart_money_long` (smart-money sleeve confluence wrap; walked B673)
- **B671 borrow-trap SHORT**
- Fire-count: squeeze-release rare; projected ~10-30/yr per direction; borderline

**Options:** (a) status quo / (b) cube ablation BR-19 vs SM-36 confluence wrap — settles whether smart-money sleeve adds marginal alpha / (c) Pattern Q docstring caveat. **My recommendation: (b) bundled with SM-36 disposition.**

**Awaiting owner direction on BR-19:**
1. Cube cross-cluster Pattern N ablation BR-19 vs SM-36
2. Pattern Q TTM-squeeze methodology citation level

---

## B676 cluster walk completion wrap-up

> All 19 breakout strategies now have full per-walk template coverage:

- **Sub-cluster A — 52w family (4):** BR-1 + BR-2 + BR-3 + BR-4 (George-Hwang 2004 JF + Bulkowski 2005 anchors)
- **Sub-cluster B — 52w break-retest (2):** BR-5 + BR-6 (B605 forensic-fix replaces DC20-anchored bug)
- **Sub-cluster C — Generic break-retest (2):** BR-7 + BR-8 (BR-8 thesis-bug — vol_spike on retest contradicts Bulkowski)
- **Sub-cluster D — Donchian family (5):** BR-9 + BR-10 + BR-11 + BR-12 + BR-13 (Faith 2007 Turtle anchor)
- **Sub-cluster E — Vol-spike (2):** BR-14 + BR-15 (BR-15 is the cluster's worst Pattern G fire-starve case per B621 0.01/yr estimator)
- **Sub-cluster F — Misc (4):** BR-16 (Elder 1993 + B626 forensic) + BR-17 (Pattern Q) + BR-18 (Pattern Q) + BR-19 (Carter 2008)

**Total fully-expanded: 19 of 19. CLUSTER WALK COMPLETE.**

### Bundled disposition recommendations summary

| Pattern | Strategies | Disposition |
|---|---|---|
| **A (default-True silent-gap)** | ✅ All 19 clean post-B663/B630 sweep | ✅ RESOLVED |
| **M (peer-review citation)** | LEGITIMATE for 15 of 19 (George-Hwang 2004 + Bulkowski 2005 + Elder 1993 + Faith 2007 + Lo-Wang 2000); Pattern Q applies to BR-17/18/19 (and weakly to BR-8 thesis bug) | DOCUMENTATION-ONLY; cluster-positive vs SMC/ICT |
| **N (intra/cross-cluster collinearity)** | 19 strategies on 13 primitives; effective N ≈ 13; Donchian-family 5 strategies on 3 effective + 52w-family 4 on 2 effective + retest-family 4 on 2 effective | Cube replay flagship Pattern N ablations: (1) Donchian-family BR-9/10/11/12/13; (2) 52w-family BR-1/2/3/4; (3) retest-family BR-7/8/12/13 |
| **T (forensic-fix density)** | 12+ batches with forensic fixes: B582/B584/B586/B587/B589/B590/B591/B592/B594/B595/B596/B598/B605/B608/B612/B617/B626/B663 — Pattern T re-validation candidates: BR-5/6 (B605 NEW retest anchor); BR-7 (B608+B617); BR-9 (B591+B592); BR-15 (B621 FAIL_FIRE); BR-16 (B626) | Cube re-validation of post-fix designs |
| **O (hardcoded tolerances)** | ~10 free parameters: vol_spike thresholds, ATR coefficients, retest tolerances, close-strength 40% | Config-parameterization for cube sweep |
| **V (Bulkowski retest absorption)** | 6 strategies (BR-2/4/5/6/12/13) — legitimate cited thesis | Cluster-positive |
| **U (5-gate post-B589 family)** | 8 strategies (BR-1/3/5/9/10/11/12/13) — canonical template | Pattern N ablation against 4-gate / 3-gate variants |
| **CC1 next-open gap (carried)** | All 19 (in continuation direction; LESS damaging than M&A target case) | Documentation-only haircut |
| **Pattern G low-fire-combo** | BR-15 (0.01/yr B621 estimator — WORST in roster); BR-2/4 (B590 7-condition restrictive); BR-9 (6-gate AND); BR-5/6 (7-gate AND); BR-14 (0.07/yr B621); BR-12/13 | Post-B660 EXPLORATORY marker decisions |
| **Pattern S single-gate shell** | BR-2 + BR-4 (B590 7-condition logic in producer flag); BR-17 + BR-19 (simple gate stack) | Documentation; consider explicit-gate refactor for BR-2/BR-4 |
| **BR-8 thesis-bug** | vol_spike on "retest" contradicts Bulkowski thesis | Owner decision: rename to "continuation" OR swap to vol_below_avg |
| **B671 SHORT borrow-trap** | 7 SHORT strategies subject (BR-3/4/6/11/13 + BR-7/16/19 SHORT branches + BR-15 SHORT + BR-18) | Already centralized B671 (pending revert per B673 reviewer architectural concern) |

### Queue tickets surfaced (recap)

NEW B676 tickets:

- `S4-BR-CLUSTER-PATTERN-N-FLAGSHIP-CUBE-ABLATIONS` — three sub-family ablations: Donchian (5 strategies), 52w-family (4 strategies), retest-family (4 strategies)
- `S4-BR8-VOL-SPIKE-VS-BULKOWSKI-THESIS-BUG-CLARIFICATION` — BR-8 `vol_spike_15x` on "retest" pattern contradicts Bulkowski thesis; rename or swap
- `S4-BR-PATTERN-O-CONFIG-PARAMETERIZATION` — ~10 hardcoded breakout parameters
- `S4-BR-PATTERN-T-FORENSIC-FIX-CUBE-REVALIDATION` — 12+ batches of forensic-fixes need cube re-validation
- `S4-BR-PATTERN-Q-INSIDE-BAR-CITATION-DOCSTRING-CAVEAT` — BR-17/18/19 + weak BR-8

EXISTING tickets cross-referenced:
- `S5-FIRE-COUNT-CANDIDATES` — BR-14 + BR-15 explicitly on the 5 REAL FAIL list
- `S5-RSI-DEFAULT-50-FAMILY` — N/A for breakout cluster
- `S5-MARGINAL-CONTRIBUTION-SCORING` — breakout cluster Pattern N is 4th-highest-leverage application (after smart-money 13F sleeve test, SMC, ICT)

---

## Cluster-wide methodology references

- **Producers:** [backtest/signals/technical.py](backtest/signals/technical.py) for break_52w_high/low, near_52w_high/low_retest, year_high/low_break_retest (B605), resistance/support_break_retest, dc10/dc20_breakout*, vol_spike_15x/17x, sector_outperforming/underperforming_spy, close_above/below_open, close_in_top/bottom_40pct_of_range, ATR(14), MACD, OBV, ADX, Force Index, inside_bar, near_pivot, AVWAP variants, squeeze_on_release; [backtest/signals/smc_ict.py](backtest/signals/smc_ict.py) NOT consumed by breakout cluster
- **Strategies:** [backtest/signals/screener.py](backtest/signals/screener.py) — 19 functions across lines 1553-2640
- **Citations:**
  - George + Hwang 2004 JF "The 52-Week High and Momentum Investing" — BR-1, BR-3
  - Bulkowski 2005 *Encyclopedia of Chart Patterns* retest absorption thesis — BR-2, BR-4, BR-5, BR-6, BR-12, BR-13
  - Faith 2007 *The Way of the Turtle* + Donchian 1960s — Donchian family BR-9 through BR-13
  - Elder 1993 *Trading for a Living* — BR-16
  - Carter 2008 TTM Squeeze — BR-19
  - Lo + Wang 2000 RFS volume-as-information — BR-14, BR-15 (volume-spike)
  - Akarim + Sevim 2013 — volume-price relationship (BR-14, BR-15)
- **Forensic-fix lineage (Pattern T):** B582 + B584 + B586 + B587 + B589 + B590 + B591 + B592 + B594 + B595 + B596 + B598 + B605 + B608 + B612 + B617 + B626 + B630 + B663

---

## B676 cluster walk status

| Item | Status |
|---|---|
| Doc infrastructure (header + adaptations + inventory + patterns + state table) | ✅ B676 |
| Per-strategy walks BR-1 through BR-19 (19 walks at full / compact-mirror template density) | ✅ B676 |
| External reviewer pass | ⏳ post-walk-completion |
| Cluster-wide post-walk findings synthesis | ⏳ post-reviewer |

**Cumulative B676: 19 of 19 walks fully expanded. CLUSTER WALK COMPLETE.**

## B680 Self-Critique Iteration 2 — Cross-Cutting Feasibility Findings

> **Status (B680 self-critique iteration 2026-06-10):** owner directive *"Just update all docs"* — proceed with adversarial self-critique in lieu of external reviewer pass.

### Cross-cutting feasibility findings (Claude self-critique 2026-06-10)

| # | Finding | Verification | Severity | Status |
|---|---|---|---|---|
| **CC-A** | **BR-8 thesis-bug is a CONFIRMED design contradiction that the walk identified but didn't escalate appropriately.** `strat_dc20_break_retest` consumes `vol_spike_15x` (HIGHER volume) on what its name calls "retest" — but Bulkowski 2005 (the cluster's anchor citation for retest patterns) explicitly states retests form on LOWER volume than the initial break (supply absorption thesis). **The strategy is either (a) named wrong and is actually a "continuation" strategy, or (b) coded wrong and should use `vol_below_avg`.** Either is fixable; the walk surfaced both options but deferred. **This is a 100%-confidence design bug** — not "may be an issue" — and should ship a fix or rename pre-cube to avoid contaminating cube data with a strategy whose thesis-implementation mismatch will produce uninterpretable results. | ✅ Verified by reading Bulkowski 2005 reference + strategy code | **HIGH (confirmed bug)** | ✅ **RESOLVED-B682** — owner-approved 2026-06-10 fix shipped: `vol_spike_15x` → `vol_below_avg` swap on BOTH LONG and SHORT directions (preserves strategy name + structure; aligns vol gate with Bulkowski 2005 thesis). Cross-strategy consistency restored with BR-2/BR-4/BR-5/BR-6/BR-7/BR-12/BR-13 (all use vol_below_avg). Test pin `test_batch682_dc20_break_retest_long_fires_on_vol_below_avg` + symmetric SHORT verified. |
| **CC-B** | **BR-15 `strat_volume_spike_breakout_retest` at 0.01/yr B621 estimator is essentially a ZERO-FIRE strategy that consumes cube budget + multi-testing budget for nothing.** 0.01/yr universe-wide projection = 1 fire every 100 years across 503 names. **Even allowing 100× under-estimate (estimator-to-actual ratio), this is ~1 fire/yr — below `min_trades=30` per regime by 1.5 orders of magnitude.** The strategy CANNOT be statistically validated by ANY cube replay; its registration consumes correction budget; per B620 squeeze_setup_event_only_long precedent (DELETED for FAIL_FIRE_STARVED at 2.5 fires/yr), BR-15 is an immediate DELETION candidate per `project_no_apriori_strategy_pruning` explicit owner override on confirmed empirical failure. **Walk noted this but deferred to "EXPLORATORY or DELETE post-B660"; B620 precedent argues delete pre-B660 since the B621 estimator's accuracy has been validated within ±10% on multiple strategies.** | ✅ B621 estimator + B620 precedent | **HIGH** | ✅ **RESOLVED-B682-DELETED** — owner-approved 2026-06-10 deletion per B620 precedent. Strategy function removed; ALL_STRATEGIES registry entry removed; 222 → 221 (one of 4 B682 deletions). Test files modified per B670 precedent (test_batch600 + test_batch612 converted to deletion-verification; test_silent_gap_pyramid + test_unit + test_batch621 updated). |
| **CC-C** | **Pattern N intra-family sub-cluster collinearity is WORSE than the walk admitted: Donchian family is 6 strategies on 1 underlying primitive (DC10/DC20 break-up/down).** BR-9 (donchian_10_breakout) + BR-10 (donchian_breakout_long) + BR-11 (donchian_breakdown_short) + BR-12 (donchian_breakout_retest_long) + BR-13 (donchian_breakdown_retest_short) + cross-cluster SM-39 (donchian_breakout_with_smart_money_long) = **6 strategies on ONE primitive class with the only differentiation being gate-count + slack-tolerance (0.2% vs 1%) + retest variant.** Walk noted "effective N ≈ 13" for the cluster overall but Donchian sub-family alone is 6 → effective N ≈ 2 (continuation + retest in each direction). The cluster's actual effective N is closer to 8 not 13 once Donchian + 52w + retest sub-families are properly collapsed. | Mechanical from gate-set inspection | HIGH | NEW — extend existing `S4-BR-CLUSTER-PATTERN-N-FLAGSHIP-CUBE-ABLATIONS` |
| **CC-D** | **CC1 next-open-after-gap is LESS BENIGN than the walk framed it.** Walk said breakout gaps are "in continuation direction therefore less damaging" — but 52w-high breakouts gap UP, engine enters next-open at UP price, and breakout-FAILURE patterns (false breakouts) typically reverse hard. **For the WIN cases the engine pays the gap but profits; for the LOSE cases the engine pays the gap AND eats the reversal.** Asymmetric: gap-cost is paid every trade; gap-benefit only on wins. **Net realized return is materially lower than backtest assumption of close-to-close.** This is a systematic bias the cube cannot eliminate without intraday data + actual gap statistics. Should ship gap-haircut sensitivity flag pre-cube. | Mechanical from engine entry mechanism | MEDIUM-HIGH | NEW — `S4-BR-CC1-ASYMMETRIC-GAP-COST-HAIRCUT` |
| **CC-E** | **Pattern T forensic-fix density is a cluster-positive note but creates a HIDDEN cube-validation debt.** 12+ batches of forensic fixes (B582 through B663) — none have been validated under post-B660 full-universe cube replay. **The cluster's "cleanest discipline in roster" framing is actually "cleanest fix log; no validation."** Each forensic fix was made on observed empirical evidence at the time but the cumulative post-fix design may have over-fit to observed failures + lost the natural diversity that captures unobserved failures. **Re-validation queue size: ~12 batches × ~2-3 strategies per batch = 25-35 strategy-fix-validation cells, on top of the standard 19-strategy × 26-exit cube grid.** This is a non-trivial cube budget allocation. | Mechanical from forensic-fix lineage | MEDIUM | NEW — `S4-BR-PATTERN-T-CUBE-REVALIDATION-BUDGET-ALLOCATION` |
| **CC-F** | **Pattern O ~10 hardcoded thresholds collectively constitute a SUBSTANTIAL hidden free-parameter space.** vol_spike_15x / vol_spike_17x / ATR coefficients (0.5x / 1.5x) / retest tolerances (0.5% / 1% / 3%) / 40% close-strength / breakout_3_candles_old / 99/101 pullback ratios. **At 10 parameters with ~3 plausible values each = 59,049 configuration variants.** Even sampling 1% of this space = 590 configurations × cube cells = unfeasible. **The cluster's "calibrated" thresholds are owner-picks or empirical-observation choices; treating them as fixed in cube validation OVERSTATES the cluster's robustness — any single threshold deviation could flip the cube verdict.** | Mechanical from parameter inventory | MEDIUM | NEW — `S4-BR-PATTERN-O-FREE-PARAMETER-SPACE-DOCUMENT-SCOPE-LIMITATION` |
| **CC-G** | **Pattern U 5-gate post-B589 family signature creates HIDDEN inverse-correlation traps.** 8 strategies (BR-1/3/5/9/10/11/12/13) all consume `close_above_open` (LONG) or `close_below_open` (SHORT) + `close_in_top_40pct_of_range` / `close_in_bottom_40pct_of_range`. **These two gates are MECHANICALLY correlated** — `close_in_top_40pct` strongly implies `close_above_open` (a strong close in top-40% almost always means bullish bar). Including both is double-counting bullishness intensity. **Pattern U "canonical template" is a methodological habit but has internal collinearity that inflates apparent confluence.** Cube ablation should remove one or the other and measure the marginal contribution; likely shows the second gate is near-no-op. | Mechanical from candle anatomy | MEDIUM | NEW — `S4-BR-PATTERN-U-INTERNAL-COLLINEARITY-CLOSE-ABOVE-OPEN-VS-TOP-40-PCT` |

### Per-strategy reframings (Claude self-critique)

| Strategy | Walk disposition | Self-critique reframing | Action |
|---|---|---|---|
| **BR-8** `strat_dc20_break_retest` | RECOMMENDED (d) — cube settles + thesis clarification | **CONFIRMED design bug.** Pre-cube fix required: rename to "continuation" OR swap vol gate to `vol_below_avg`. Owner decision. | Pre-cube fix |
| **BR-15** `strat_volume_spike_breakout_retest` | RECOMMENDED — EXPLORATORY or DELETE post-B660 | **Pre-cube DELETE per B620 precedent.** Estimator confidence is high enough; B620 precedent established at 2.5/yr (BR-15 is at 0.01/yr — 250× worse case). | Pre-cube DELETE owner-decision |
| **BR-5** `strat_52wh_break_retest` | RECOMMENDED (d) — cube settles redundancy | **Internal-redundancy concern (near_52w_high + year_high_break_retest_long) is mechanical not empirical.** year_high_break_retest_long REQUIRES today's close >= year_high; near_52w_high requires close >= 98% of year_high. The intersection is near-tautological. **DROP near_52w_high pre-cube; it's adding zero information.** | Pre-cube gate-drop |
| **BR-9** `strat_donchian_10_breakout` | RECOMMENDED (c) — flagship Donchian-family ablation | **6-gate AND with B591 + B592 forensic-additions; Pattern G fire-starve risk acute.** Projected ~15-40/yr per direction is best-case under independence assumption; with realistic correlation, likely 5-15/yr per direction. Pre-cube fire-count projection candidate for EXPLORATORY route. | Pre-cube fire-count projection |

### Net effect on B676 walk dispositions

- **BR-8 thesis-bug + BR-15 deletion** PROMOTED to pre-cube actions (not post-B660 deferrals)
- **Pattern N effective-N estimate** REVISED DOWN from 13 to ~8 (Donchian + 52w + retest sub-families more collapsed than walk admitted)
- **CC1 gap-haircut** asymmetric in lose-cases not just win-cases
- **Pattern U canonical template** internal-collinearity NEW concern (close_above_open + close_in_top_40pct overlap)
- **Pattern T forensic-fix cube re-validation** budget allocation NEW concern

### Queue tickets surfaced by self-critique (B680)

- `S4-BR-8-THESIS-BUG-IMMEDIATE-FIX-OR-RENAME` (HIGH; CC-A; pre-cube)
- `S4-BR-15-DELETION-PER-B620-PRECEDENT-PRE-B660` (HIGH; CC-B; pre-cube)
- `S4-BR-CC1-ASYMMETRIC-GAP-COST-HAIRCUT` (MEDIUM-HIGH; CC-D)
- `S4-BR-PATTERN-T-CUBE-REVALIDATION-BUDGET-ALLOCATION` (MEDIUM; CC-E)
- `S4-BR-PATTERN-O-FREE-PARAMETER-SPACE-DOCUMENT-SCOPE-LIMITATION` (MEDIUM; CC-F)
- `S4-BR-PATTERN-U-INTERNAL-COLLINEARITY-CLOSE-ABOVE-OPEN-VS-TOP-40-PCT` (MEDIUM; CC-G)
- `S4-BR-5-NEAR-52W-HIGH-GATE-DROP-PRE-CUBE` (per-strategy reframing)

---

## B679 Iteration 2 Preparation — Review Solicitation Guide

> **Status (post-B679 format alignment):** READY FOR EXTERNAL REVIEWER + OWNER FEEDBACK on Iteration 2. The smart-money cluster doc received 2 review rounds (B669 + B673 → B674); this breakout cluster doc is READY FOR YOUR 2ND-WAVE FEASIBILITY CRITIQUE.
>
> **Recommended review structure (parallel to B673 smart-money review):**
>
> | Review axis | What to look for in Breakout | Smart-money parallel |
> |---|---|---|
> | **CC-A: Engine entry feasibility** | Breakout strategies gap in CONTINUATION direction (less damaging than SM-4 mean-reversion case); engine pays the gap but trade benefits if continuation persists. Capturable fraction higher than M&A target but not unity | CC1 (partial; in-direction) |
> | **CC-B: Forensic-fix density** | 19 batches of forensic fixes (B582 through B663). Post-fix designs need cube re-validation symmetric with B262/B278 from smart-money | Pattern T NEW; symmetric with B262/B278 |
> | **CC-C: Citation discipline** | 15 of 19 strategies have LEGITIMATE peer-reviewed anchors (George-Hwang 2004 JF + Bulkowski 2005 + Faith 2007 + Elder 1993 + Lo-Wang 2000). Pattern M / Q applies only to 4 (BR-17/18/19 + BR-8 thesis-bug). Cluster-positive | Pattern M / Q narrow application |
> | **CC-D: BR-8 thesis-bug** | `vol_spike_15x` on "retest" pattern contradicts Bulkowski retest-on-lower-volume thesis. Either rename strategy OR swap to `vol_below_avg`. Owner decision pending | Per-strategy reframing |
> | **CC-E: BR-15 Pattern G severity** | B621 estimator projects 0.01/yr universe-wide — WORST in entire roster. EXPLORATORY-or-DELETE decision per B620 squeeze_setup_event_only_long precedent | Pattern G / W5m precedent |
> | **CC-F: Intra-family Pattern N** | 19 strategies on 13 primitives → effective N ≈ 13. Donchian-family 5 on 3 + 52w-family 4 on 2 + retest-family 4 on 2. Three flagship sub-family cube ablations | CC7 effective N |
> | **CC-G: Pattern O hardcoded** | ~10 free parameters (vol_spike thresholds, ATR coefficients, retest tolerances, 40% close-strength). Cube sensitivity sweep candidates | Pattern O carry |
>
> Provide feedback in B673-style severity-ranked critique; B679 will incorporate as B679-incorporation batch.

---

### Cross-cluster status snapshot (post-B679 — index at [STAGE_4_CLUSTER_WALKS_INDEX.md](STAGE_4_CLUSTER_WALKS_INDEX.md))

8 cluster docs / ~138 strategies covered. Review status:

| Cluster | Doc | Strategies | Owner review | Iteration 2 ready |
|---|---|---|---|---|
| Pivot | [STAGE_4_PIVOT_CLUSTER_WALKS.md](STAGE_4_PIVOT_CLUSTER_WALKS.md) | ~10 | ✅ 2 rounds | (already iterated) |
| Trend | [STAGE_4_TREND_CLUSTER_WALKS.md](STAGE_4_TREND_CLUSTER_WALKS.md) | ~12 | ✅ Companion | (already iterated) |
| Smart Money | [STAGE_4_SMART_MONEY_CLUSTER_WALKS.md](STAGE_4_SMART_MONEY_CLUSTER_WALKS.md) | 41 | ✅ 2 rounds (B669 + B673 → B674) | (already iterated) |
| SMC | [STAGE_4_SMC_CLUSTER_WALKS.md](STAGE_4_SMC_CLUSTER_WALKS.md) | 18 | ❌ AWAITING | READY |
| ICT | [STAGE_4_ICT_CLUSTER_WALKS.md](STAGE_4_ICT_CLUSTER_WALKS.md) | 12 | ❌ AWAITING | READY |
| **Breakout (THIS DOC)** | **[STAGE_4_BREAKOUT_CLUSTER_WALKS.md](STAGE_4_BREAKOUT_CLUSTER_WALKS.md)** | **19** | **❌ AWAITING** | **READY** |
| Event-driven | [STAGE_4_EVENT_DRIVEN_CLUSTER_WALKS.md](STAGE_4_EVENT_DRIVEN_CLUSTER_WALKS.md) | 10 | ❌ AWAITING | READY |
| Chart+Candle | [STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md](STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md) | 16 | ❌ AWAITING | READY |
