# B2573 — Is the strategy-optimisation workflow mechanical enough for Opus to run it across all strategies? (owner-directed audit, 2026-09-02)

# Source: scripts/{run_postconfig.py,producer_variant_table.py,tighten_breaker_block.py,grade_institutional_config.py,grade_free_levels_institutional.py,spot_check_trades.py,spot_check_institutional.py,verify_engine_implemented.py,verify_spotcheck_coverage.py,verify_describing_artifacts.py,postconfig_doc.py,postconfig_landing.py,run_serial_chain.py,run_wave.py,launch_sweep.py,launch_detached.py,launch_chain_noconsole.py,watch_run_progress.py,classify_run_log.py,kill_wave_tree.py,prelaunch_gate.py} + STRATEGY_OPTIMISATION_PLAN.md (2,640 lines) + output_audit/{serial_chain.log,postconfig_ledger.json,postconfig_landings.jsonl} + output_icg_span*/run_manifest.json + Win32_Process listing + Get-ScheduledTask + CronList (per CHECKLIST #77)

**Owner question (verbatim):** "Is the workflow optimized and mechanical in a way for opus to run this across all strategies? What are the steps that opus should follow? Is it all a part of the strategy optimization runbook, is anything missing? Is any of the code used for strategy optimization only relevant for a particular strategy and cant be used for other strategies? ... This includes monitoring standards, sessions survival, workflows not getting triggered or loaded, edge cases, etc. Do a comprehensive audit and add all findings to open tickets."

## 0. Verdict, with denominators

**NOT mechanical.** Of the 9 scripts the post-config battery dispatches or the runbook prescribes for a
strategy's STEP 0-4 path, **7 of 9 are written for exactly one strategy** (READ: a `STRAT =` constant, a
hardcoded band list, a producer-specific re-derivation, or a token set naming one family's engine
symbols). The battery's family registry holds **2 of 219 registered strategies** (`FAMILIES` in
`scripts/run_postconfig.py`), and a strategy outside it FAILS closed at landing - after the engine has
spent its 2-4 hours. Nothing at launch checks membership (EXECUTED grep: `FAMILIES`/`SPECS`/
`producer_variant_table` appear in **0 of 4** launch-path scripts - prelaunch_gate, run_wave,
run_serial_chain, launch_sweep). The runbook has **no single ordered step list**; its generic STEP 0-4
sections carry smc-specific commands at 4 sites and stale numbers at 5 sites (all cited below).

Monitoring and session survival: the durable channels are the heartbeat file, the chain log and the
landing ledger; **every notification channel except the Windows toast is session-held**
(CronCreate, PushNotification) - the chain HALT path writes a log line and nothing else. Two duplicate
hourly crons are armed right now (EXECUTED CronList: `:13` and `:17`), which shows the "arm the
monitor" step is not idempotent either.

Each finding below carries its evidence class and the ticket that now owns it. Every ticket is filed
OPEN in EXECUTION_QUEUE.md (S6-B2573a..S6-B2573i). No code was changed this turn: a chain of 16 specs is
live (4 COMPLETE, span100 running, 11 queued - EXECUTED: process 24172's command line + serial_chain.log),
and the battery/launcher scripts are re-read at every landing/launch, so an edit would take effect
mid-chain (see D2).

## A. Code that only works for one strategy (the owner's "code you developed for the previous strategy")

| # | Finding | Evidence | Ticket |
|---|---|---|---|
| A1 | **The battery family registry is hand-written per strategy and closed.** `FAMILIES = {smc_breaker_block_long, institutional_committed_growth_long}`; each entry names a params extractor + a `run_<family>` function; an unregistered strategy raises at landing. Adding a strategy today means writing ~6 artifacts by hand (params extractor, run_<family>, step-1 grader, free-levels grader, spot-check, step-7 anchor set) before the battery stops failing. There is no adapter CONTRACT (an interface the six pieces must satisfy) and no template. | READ `scripts/run_postconfig.py` `FAMILIES`, `_GRADER_CHECKS`, `run_smc`, `run_institutional`, the unregistered-family raise | S6-B2573a |
| A2 | **No launch-time family check.** A spec whose strategy has no FAMILIES/SPECS/D_AXIS entry launches, runs to completion, and only then FAILS at the battery (the institutional pre-B2520 history: 4 configs landed ungraded). The gate exists at the wrong end of the run. | EXECUTED `grep -n "FAMILIES\|SPECS\|producer_variant" scripts/prelaunch_gate.py scripts/run_wave.py scripts/run_serial_chain.py scripts/launch_sweep.py` -> one comment hit (launch_sweep.py:264), zero checks | S6-B2573b |
| A3 | **The band lives in two places with two schemas.** `tighten_breaker_block.py:35-110` hardcodes `BREAK_PCT_MAX/AGE_BARS_MAX/TAIL_N/CLOSE_MITIGATION` independently of `SPECS`; smc SPECS entries use `band`+`subset_safe`, institutional uses `free_band`+`resim_band`, and `table_a` special-cases both. A third strategy will need a third shape unless the schema is unified. | READ `scripts/tighten_breaker_block.py:35-110`, `scripts/producer_variant_table.py:92-165` | S6-B2573c |
| A4 | **Step 7 (engine-implemented) has two implementations and no generic one.** `verify_engine_implemented.py` is entirely smc (`PARAMS` P1-P6 tokens like `swing_length=_cfg.SMC_SWING_LENGTH`, `CALL_SITE_TOKENS` naming `SMC_OB_*`/`SMC_BREAKER_*`); institutional's step 7 is an inline grep inside `run_institutional`. The anchor set a family needs is not declared anywhere a generic checker could read. | READ `scripts/verify_engine_implemented.py:40-100`; `run_postconfig.py::run_institutional` step-7 block | S6-B2573a (member) |
| A5 | **Spot check is per family with no shared harness.** `spot_check_trades.py` re-derives smc fires (`rederive_fire(df, when, swing_length, ema_span, close_mitigation, tail_n)` calling `smc.swing_highs_lows`); `spot_check_institutional.py` (`STRAT = "institutional_committed_growth_long"`) is a different three-leg design. The three-leg SHAPE (precompute / production consumer / engine record) is generic; only the re-derivation hook is per family. | READ `scripts/spot_check_trades.py:58-106`, `scripts/spot_check_institutional.py:1-56` | S6-B2573a (member) |
| A6 | **Graders are per family and the free-levels leg exists for one family only.** smc grades via `tighten_breaker_block.py`; institutional via `grade_institutional_config.py` (`STRAT =` constant) + `grade_free_levels_institutional.py` (`STRAT =` constant, `OUT` hardcoded to a B2504 path). `_GRADER_CHECKS` lists `step2_free_levels`, but `run_smc` has no such leg - so the #290 rule (every check owed per landing runs unprompted) is already unevenly applied across the two families that exist. | READ `run_postconfig.py` `_GRADER_CHECKS` vs `run_smc`; `grade_free_levels_institutional.py:61-62` | S6-B2573a (member) |
| A7 | **Env knobs cross strategy boundaries silently.** `STRAT_EMA_SPAN` is consumed by smc_breaker_block_long/_short AND institutional; `INST_PERSIST_CACHE_TAG` re-routes `committed_growth_holders`, which `strat_simple_below_ema_50_short` also consumes (screener.py:6144). A sweep on one strategy changes another's inputs, and no SPECS field declares a knob's blast radius, so nothing at launch can warn. (Cube consequence today: none, because the cube runs `--strategies <one>`; roster consequence at Step 3/1B: real.) | READ prior-turn screener.py:6144 + `_institutional_params`/`_smc_params`; UNVERIFIED that no other consumer of STRAT_EMA_SPAN exists beyond the three named | S6-B2573d |
| A8 | **Helper scripts hardcode the first family.** `verify_describing_artifacts.py` (`STRAT = "smc_breaker_block_long"`, imports tighten_breaker_block, names `PRODUCER_VARIANT_TABLE_smc_breaker_block_long.md`); `postconfig_doc.py:172,353`; `verify_postconfig_complete.py:83`; `run_wave.py:39-40,67` docstring; `verify_spotcheck_coverage.py:45` classifies signals by a regex of family names. | EXECUTED grep across scripts/ (prior turn) | S6-B2573a (member) |
| A9 | **Table D falls back to smc columns for an unregistered family** (`_d_family` in producer_variant_table.py) - a wrong-shape render instead of a refusal. Same class as S6-B2566 (a count under the other family's noun). | READ `scripts/producer_variant_table.py:478-520` | S6-B2573c (member) |

## B. The runbook: is there a step list Opus can follow?

| # | Finding | Evidence | Ticket |
|---|---|---|---|
| B1 | **There is no single ordered procedure.** The path is spread over §9 (per-strategy checklist, B1520), §10 (repeatable workflow, B1548), STEP 0 / STEP 1 / STEP 2 ENTRY / STEP 2 EXECUTION / STEP 2 PRE-TRIAGE / STEP 3 / STEP 3.1-3.4 / POST-CONFIG BATTERY / STEP 4 / RUN-SAFETY ARCHITECTURE / MANDATORY POST-CONFIG ANALYSIS / CURRENT PROGRAMME - 2,640 lines with superseded text left inline (§0a supersession banner; §5 "superseded by §8"; the STEP 1 heading at line 1287 carries its own pre-ruling shape; §1.0(b) nested GRAIN-STALE and WRONG-QUANTITY notes; §1.3 retracted demand-pruning note). An operator has to know which paragraph is live. | READ STRATEGY_OPTIMISATION_PLAN.md headings (EXECUTED grep of `^## `/`^### STEP`) | S6-B2573e |
| B2 | **Generic steps carry smc-specific commands.** STEP 0.5 `instrument_breaker_block.py` (line 1263); STEP 1.3 launch env `SMC_SWING_LENGTH=<P1_value> STRAT_EMA_SPAN=<P6_value>` (1427); STEP 2 `tighten_breaker_block.py ... --keys close_mitigation,break_pct_max,age_bars_max,tail_n` (1540-1564); MANDATORY POST-CONFIG ANALYSIS `tighten_breaker_block.py --cube output_cfg<N>` (2192). None is labelled "family example". | EXECUTED grep, line numbers as cited | S6-B2573e |
| B3 | **Stale numbers contradict owner rulings inside the runbook.** Line 1145 `--screen-pool-workers 10` vs line 1432 `3` vs RUN-SAFETY line 2022 "hardcoded 0"; line 1206 "Universe 100 for search" vs the ruled 200 (§10.1, APPENDIX S1-200); line 1209 "$50 CAD cap" vs B2109 $100 total; line 1124 cost model at 100t x 2y; line 1855 says the grid emits `provisional_qualifiers` while line 987 records its rename to `qualifiers` (S6-B2409). | EXECUTED grep, line numbers as cited | S6-B2573e (annotated this turn, see §11 of the runbook) |
| B4 | **The documented launch command is not the launch path.** STEP 1.3 gives a direct `run_phase1a.py` invocation; the live chain runs spec -> `run_serial_chain.py` -> `run_wave.py` -> `launch_sweep.py` -> `run_phase1a.py` (EXECUTED: the process tree, PIDs 24172 -> 21292 -> 27636 -> 3636). The direct command bypasses the gate receipt, the battery hook's spec context, and the chain's halt semantics - the "engine still invocable around the gate" class (S6-B2159b, receipt half built). | EXECUTED Win32_Process listing | S6-B2573e |
| B5 | **No per-family on-ramp checklist and no chain-HALT procedure.** Nothing lists what must exist before the FIRST spec of a new strategy launches, and nothing says what to do when `serial_chain.log` reads HALT (which spec, how to resume the chain from the next spec, whether the halted cube is salvageable). | READ runbook (absence) | S6-B2573e + S6-B2573f |

## C. Monitoring standards and session survival

| # | Finding | Evidence | Ticket |
|---|---|---|---|
| C1 | **Chain HALT is log-only.** `run_serial_chain.py` returns 1 and writes one line to `output_audit/serial_chain.log`; no toast, no push, no file that a Stop hook reads. A halt at 02:00 reaches nobody until someone tails the log. | READ `scripts/run_serial_chain.py` (full) | S6-B2573f |
| C2 | **Hourly reporting is session-held and not idempotent.** The standard (runbook line 788 item 13, §1165-1215, #185/#186) is a CronCreate in the launch turn; CronCreate is session-only (already OPEN as S6-B2548). New this turn: TWO hourly crons are armed for the same chain (`6bdd85fa` at :13 and `9d1dded0` at :17), i.e. re-arming after a restart duplicates rather than replaces. | EXECUTED CronList | S6-B2573f (dup) + S6-B2548 (durability, unchanged) |
| C3 | **The stall detector and the dead-log classifier have no scheduler.** `watch_run_progress.py` (exit 0/1/2 by sim_day diff) and `classify_run_log.py` (no ending + no live pid = DEAD) are hand-run tools; `Get-ScheduledTask` shows only the chain tasks - nothing periodic reads `run_heartbeat.json`. | EXECUTED Get-ScheduledTask; READ both scripts' headers | S6-B2573f |
| C4 | **Stale Task Scheduler entries accumulate.** `stockpicks_chain_b2197` and `stockpicks_chain_b2213` are still registered (State Ready) after their chains finished; `launch_detached.py --cleanup` exists and is not on the chain-done path. | EXECUTED Get-ScheduledTask | S6-B2573g |
| C5 | **A hand-run of the Stop-hook script blocks forever and outlives the tool timeout.** `verify_turn_compliance.py:133` does `sys.stdin.read()`; a self-test launched from a Bash heredoc at 13:42 local is still alive at 18:42 (PIDs 2632/20068, parent bash 18728, 15 ms CPU total). The Bash tool timed out at 2 min and orphaned it. `Stop-Process` was DENIED by the auto-mode classifier this turn, so both processes are still running - owner action or a later interactive turn is needed. Class: any stdin-reading hook script hand-run without `</dev/null`. | EXECUTED Win32_Process + CommandLine read | S6-B2573g |
| C6 | **The battery's newest leg has run on zero landings.** `step2_free_levels` (B2569) shipped after span50 landed (span50 ledger `1_cube_sanity` evidence lists step2_grade_auto/step4/step7 and no free-levels item). span100's landing (~00:15Z, DERIVED from the heartbeat) is the first exercise; per #226 a check nobody has watched fail is indistinguishable from one that cannot. | READ postconfig_ledger.json[output_icg_span50_span50]; EXECUTED heartbeat read | S6-B2573h |
| C7 | **span100 wall-clock margin.** Heartbeat at 22:42Z: sim_day 141, elapsed 1.93 h, cap 4.0 h. At the observed rate (73 days/h) the remaining ~111 days need ~1.5 h -> ~3.45 h total, 0.55 h under the cap. PREDICTION, not a result. | EXECUTED `run_heartbeat.json`; DERIVED | none (watch item) |

## D. Edge cases

| # | Finding | Evidence | Ticket |
|---|---|---|---|
| D1 | **The chain does not hold one code SHA.** The four landed specs froze four different SHAs (span9 c5198baf9, span20 3745e05dc, span50 fb885e91e, span100 bafb5118e) because the battery auto-commits at every landing and working turns commit between specs. The pre-spend rule says a pinned-field change restarts the sequence; the sequence's own mechanism guarantees the change. What the cube actually depends on is the ENGINE path (`backtest/**` + the swept precompute), which no manifest field hashes and no check compares across specs. | EXECUTED `run_manifest.json` reads x4 | S6-B2573i |
| D2 | **Battery and launcher scripts are re-read at each landing/launch, so mid-chain edits take effect on the next spec.** B2569 relied on this (the free-levels leg shipped into a running chain); the same property lets a defective edit land on 11 queued specs with no restart. The runbook does not say which files are "live under a running chain". | READ `postconfig_landing.py` (subprocess per landing); EXECUTED chain process list | S6-B2573i (member) |
| D3 | **Each Python process appears twice in the process table** (venv `python.exe` stub + the interpreter it spawns, identical command line and creation time - 2 x run_serial_chain, 2 x run_wave, 2 x launch_sweep, 2 x run_phase1a). Any liveness or kill logic that counts PIDs by command line double-counts; `kill_wave_tree.py` matches on the out-dir name, which the runbook (line 1693) already flags as missing the run_wave root. Mechanism UNVERIFIED (not read from CPython source); the pairing is EXECUTED. | EXECUTED Win32_Process listing | S6-B2573g (member) |
| D4 | **The runbook's §0.7 band-completeness rule (B2569) has no enforcement point.** `validate_spec` checks shape, not that every `resim_band` level has a proven knob; the P7/P8 defect (S6-B2569a) would pass it again. | READ `producer_variant_table.py::validate_spec` (prior turn) | S6-B2573b (member: the launch gate is where this belongs) |

## E. What Opus should follow - the ordered procedure (now §11 of STRATEGY_OPTIMISATION_PLAN.md)

The procedure is written into the runbook this turn as **§11 MECHANICAL PROCEDURE FOR ANY STRATEGY**
with two parts: (1) the per-family ON-RAMP (the artifacts that must exist, with a `python -c` probe
for each, before the first spec launches) and (2) the ordered STEP 0 -> STEP 4 run list with the exact
command per step and the artifact each step must leave. Items that are tickets (not yet mechanisms)
are labelled PROPOSED-NOT-BUILT inline so the procedure never cites a gate that does not exist (B1335
rule 2).

## F. What is NOT in this audit

- The engine (`backtest/**`) was not audited for portability - the swept parameters reach it via env
  knobs, and the knob pattern (B1519) is generic. The coupling findings (A7) are about who else reads a
  knob, not about the engine.
- The 207-strategy backlog itself: this audit measured the WORKFLOW's readiness, not any strategy.
- Hetzner / AWS venue paths (S6-B2107a): not exercised by the current chain; untested here.
