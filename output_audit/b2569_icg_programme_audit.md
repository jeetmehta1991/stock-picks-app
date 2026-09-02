# B2569 — Audit of the ICG Step-1 programme turns (B2465 → B2568), owner-directed 2026-09-02

# Source: git log B2465..B2568 + output_icg_*/trade_log.parquet + output_audit/postconfig_{landings.jsonl,ledger.json} + scripts/{producer_variant_table.py,grade_*,run_postconfig.py} + backtest/signals/screener.py:6640-6660 + EXECUTION_QUEUE.md rows S6-B2481..S6-B2568 (per CHECKLIST #77)

**Directive (owner, verbatim intent):** audit and address every mistake made over the recent
turns since the institutional_committed_growth_long strategy work started; address the CLASS,
not the instance; make the workflow repeatable for ALL strategies; first, reproduce span9's
landed 609 fires at production levels before believing anything the re-scorer reports.

**Method:** every commit B2465→B2568 read from `git log`; every load-bearing claim in the
plan's CURRENT PROGRAMME section checked against its primary (cube files, landing ledger,
battery ledger, SPECS, screener source, queue rows); the re-scorer executed against all four
landed cubes. Misses already self-recorded in the batch record are LISTED (not re-litigated);
findings NEW to this audit are numbered N1–N6 with dispositions.

---

## 0. The approved first step — EXECUTED, ALL FOUR CUBES REPRODUCE

`grade_free_levels_institutional.py --cube <dir>` now gates itself: every covered landed
trade must re-pass the production gate (P7=3, P8=5) offline before any level is graded.

| cube | landed | covered | empty signals (S6-B2512) | re-passed | verdict |
|---|---|---|---|---|---|
| output_icg_span9_span9 | **609** | 609 | 0 | **609** | **PASS** |
| output_icg_span20_span20 | 531 | 531 | 0 | 531 | PASS |
| output_icg_span50_span50 | 405 | 405 | 0 | 405 | PASS |
| output_icg_cfg1 | 373 | 350 | 23 (excluded + counted, never silently failed) | 350 | PASS |

Cross-tool consistency for free: span9's baseline level through the free grader re-derives
the landing grade's exact top ranking (regime_flip, ci_lo +0.167, n=609) — the re-scorer and
`grade_institutional_config.py` agree on the untouched population.

**Free-level verdict with denominators: 0 of 4 free levels beat baseline on ANY of the 4
landed configs (0 of 16 level×config cells).** Every P7 tightening costs 31–79 % of fires and
drops top ci_lo (span9: +0.167 → −0.150 at p7_5); p8_6 is a 4–6-trade no-op everywhere.
Same shape as the R5-cube pass (S6-B2504). Artifacts:
`output_audit/output_icg_{cfg1,span9_span9,span20_span20,span50_span50}_free_levels.json`.

---

## N1 — THE CLASS BUG (owner's headline): a per-config band member was graded once, at strategy level, and never wired

The ruled Step-1 design (S6-B2499 row) counts "17 engine configs **+ 4 FREE cache-graded
levels**" as ONE band. The free levels are therefore part of EVERY config's grade. What
happened instead: S6-B2501/B2504 graded them ONCE against the R5 merged cube (544×4y — not
even the Step-1 shape) and the per-config battery never ran them on cfg1, span9, span20, or
span50.

**Three separate chances to wire it were missed:**
1. **B2504** shipped the correct tool — hardcoded to the R5 cube, no `--cube`, no ticket for
   per-config use.
2. **B2520** built the engine-invoked battery and registered the institutional family — the
   free levels were named in the grader's docstring ("grader-only levels, S6-B2504") and
   still not given a battery leg.
3. **B2527** pre-registered all 16 wave specs — the pre-spend manifest counted the free
   levels as band coverage ("136 points" framing, called out at B2567's council) with no
   mechanism to produce them per config.

**Class statement:** a check that the runbook owes EVERY config is not satisfied by one
hand-run execution at strategy level. The B2520 battery exists precisely because six prior
asks each drew an instance fix (L736/#288 "count the asks") — and the very first analysis
step added AFTER the battery shipped repeated the pattern the battery was built to kill.

**Disposition: FIXED B2569, class-level.**
- `grade_free_levels_institutional.py` parameterised (`--cube`), reproduction-gated, levels
  derived from `SPECS` free_band (single source — no hand-typed copy to drift).
- `run_postconfig.run_institutional` gains a `step2_free_levels` leg; step 2 is DONE only if
  BOTH the config grade AND the free-levels grade succeed; a reproduction failure FAILS the
  step closed. Every future landing runs it with no session involvement.
- Retroactively executed on all 4 landed cubes (table above).
- Pins: `test_b2569_free_level_reproduction_gate_and_specs_derivation`,
  `test_b2569_battery_runs_free_levels_on_every_institutional_landing`.
- CHECKLIST **#290** codifies the class rule; **L752** records the lesson.

## N2 — The runbook's mandatory-analysis §2 was never generalized per family

`STRATEGY_OPTIMISATION_PLAN.md` § MANDATORY POST-CONFIG ANALYSIS step 2 ("Grade — with the
CONFIG'S OWN parameters") showed **only the smc command** (`tighten_breaker_block.py
--swing-length …`). The battery generalized per family at B2520; the runbook did not. An
Opus session following the doc for a non-smc strategy has no instruction to follow — the
exact repeatability failure the owner names. **Disposition: FIXED B2570** — §2 rewritten
family-generic (family grader + free-levels grader, both battery-invoked, doc names the
dispatch).

## N3 — The plan still claims "100 % measured coverage" for the persisted counts

CURRENT PROGRAMME: "both counts persist in signals_at_entry at 100 % measured coverage."
Corrected TWICE by measurement (96.2 % on R5, S6-B2504; 93.83 % on cfg1, B2567) and still
standing in the plan. L749's exact class (a correctly-sourced figure can still be stale), in
the programme's own section. **Disposition: FIXED B2570** (text corrected with both numbers).

## N4 — The plan's "cheapest next action" pointed at completed, superseded work

"Grade the P7/P8 FREE levels off the existing R5 cube (S6-B2501)" — S6-B2501 EXECUTED
2026-09-01, then the per-config directive superseded the R5-cube framing entirely.
**Disposition: FIXED B2570** (line replaced with the standing per-landing mechanism).

## N5 — Table A / SPECS band advertises levels the programme cannot measure (P7 resim {1,2}, P8 resim {2,3})

The owner's question, answered with evidence:

1. **Why aren't they in the configs?** The ruled Step-1 design scheduled 17 engine configs
   (P4/P5/P6/P9 sweeps); the P7/P8 looser levels were "recorded in the band and
   deliberately NOT scheduled" (plan, S6-B2499/S6-B2501 rows). No owner ruling row records
   an explicit decision to exclude them — it was a session design choice inside the 17-config
   scoping.
2. **The deeper fact that was never flagged:** they are not merely unscheduled — they are
   **unrunnable as specced**. P7/P8 are hardcoded in the screener
   (`backtest/signals/screener.py:6646-6648`: `n_grow >= 3`, `n_incr >= 5`); grep confirms
   **no env knob exists** (`INST_MIN_COMMITTED*`/`FALLBACK*` absent from screener, config,
   and the precompute builder). Every other swept parameter got an actuation mechanism
   (INST_* env ×3, STRAT_EMA_SPAN); P7/P8's looser side got a band entry and nothing else.
3. **Why this is a class defect:** free grading moves ONE direction — tighter (a raised
   threshold selects a subset; a lowered one admits trades no cube contains, §0a #1). So for
   every PERSISTED threshold parameter, the looser side is ENGINE-ONLY **by construction**,
   and a band that lists looser levels must, at pre-registration time, either (a) schedule
   them with an actuation mechanism, or (b) strike them with an explicit
   NOT-MEASURED-BY-DESIGN disposition. P7/P8's resim levels are neither — dead rows that
   inflate apparent band coverage. Flagged nowhere across B2465 (Table A), B2467 (per-level
   split), B2481–B2499 (design), B2527 (pre-registration).

**Disposition: OWNER DECISION — S6-B2569a** (see queue). Options costed:
- **(a) Strike** P7 {1,2} / P8 {2,3} from the band; SPECS + Table A annotated
  NOT-MEASURED-BY-DESIGN with this reason. Cost 0. The free-level evidence (0/16 cells
  improve on tightening) says nothing about loosening, but loosening a noise-dominated
  fallback arm (P8 at 2 admits `institutional_increased ∈ {2,3,4}` rows) weakens the thesis
  the strategy is named for.
- **(b) Schedule** them: 1-line-class screener change (B1519 env pattern:
  `INST_MIN_COMMITTED_GROWTH` / `INST_FALLBACK_MIN_INCREASED`) + 4 engine configs appended
  to the chain ≈ **+10–12 h serial** at the measured 2.4–2.9 h/config, $0.
- The runbook rule (band completeness at pre-registration) ships either way — B2570 adds it
  to STEP 0 and the §1.0 pre-launch gate as a mandatory check.

## N6 — L751 was recorded and its instance fix left unshipped

B2568 recorded the lesson ("a parameter accepted, recorded, and never applied") and left
`grade_institutional_config.py` still accepting-and-ignoring `--min-committed-growth` /
`--fallback-min-increased`. Between B2568 and this audit, any invocation with a
non-production value would still have shipped an identical grade stamped as a different
measurement. **Disposition: FIXED B2569** — `refuse_nonproduction()` exits 2 on any
non-production value, pointing at the free-levels tool;
pin `test_b2569_institutional_grader_refuses_nonproduction_admit` asserts by EXECUTION
(L750).

---

## Self-recorded miss ledger, B2465 → B2568 (36 entries — already carrying instance fixes; listed for the class view)

| batch | miss (compressed) | class artifact |
|---|---|---|
| B2498 | pre-screen cost claim understated 2.7× (warm one-snapshot sample) | measured re-run |
| B2507 | boundary matrix run AFTER design, killed own 3× backstop | L734 |
| B2509/B2526 | tracked-status assumed, not asked; the rule's author violated it same-turn | L735 |
| B2511 | cfg1 grid built from an uncommitted scratchpad script | committed as B2520 grader |
| B2512 | 23/373 cfg1 rows empty signals_at_entry | RCA closed S6-B2512 |
| B2515/B2516 | battery wired to launcher, not engine; automation deferred to a phantom batch | B2520 rewire |
| B2520p | lens tally on a guessed field name (0-WARN illusion) | #289 |
| B2522 | delivery path could never have worked; truncation ate a test | re-exercised B2523a |
| B2523 | council count asserted from impression (5-of-5, not 4-of-5) | correction |
| B2524 | append log read by two ad-hoc readers → two wrong counts in one turn | one-reader rule |
| B2528 | detached task 12 h limit vs 38–47 h chain | fixed pre-launch |
| B2529 | launcher reported success twice on launches that never happened | L738, S6-B2529a, B2559 |
| B2530a/b | overstated own alarm; "plateau" that was an oscillating band | corrections |
| B2531 | plan staleness nearly produced a wrong call (rulings already resolved) | L664 applied |
| B2532 | figure attributed to a command that never produced it | S6-B2532a pin (B2562) |
| B2533/34/36 | 15-line edit → 36,465-line diff, cause UNKNOWN, ticketed not guessed | L739 + sweep |
| B2535 | pool_workers 10→4 on 15 unstarted configs | measured, seconds |
| B2538 | chosen value beside a measured one inherited unearned authority | L740 |
| B2540 | ALL 16 specs lacked the 4 plain keys the battery grader reads (SMC-template copy) | repaired; battery failed closed as designed; S6-B2540a |
| B2541/42 | Table C had never rendered the ICG family | render fixed |
| B2544/45 | "nothing calls this" claimed repo-wide from one file | L742 + durability |
| B2546 | engine hardened for session death; owner's channel left session-scoped | L743; span9/span20 M10 receipt FAILs dispositioned |
| B2547–49 | monitor-armed gate failed both directions; remedy was session-only | pins |
| B2550 | a gate that cannot fire on its own example | L744 |
| B2551 | MECHANICALLY ENFORCED claims with no enforcer named | sweep |
| B2552 | uncosted self-disparaging estimate escaped the bias check | L745 |
| B2554/55 | gate could not decode its own output / erased its own evidence | fixed + pins |
| B2556–58 | two-arm pin proved two arms, not two directions; ratchet forgot its why | L746/L747 |
| B2561 | assertion matched the comment, not the code | L748 |
| B2563 | correctly-sourced figure, stale by the time it was used | L749 |
| B2564 | Phase-5 mechanism satisfied by phrase, not file touch | fixed |
| B2565 | gate's message described a check the code didn't perform | L750 |
| B2567 | P7/P8 free-grading flags are labels; wrong file; coverage not 100 % | approval held → this turn |
| B2568 | parameter accepted, recorded, never applied | L751 (instance fix landed B2569, see N6) |

**Pattern the ledger shows (and the owner named):** the lessons are being recorded
faithfully and their CLASS fixes lag — N1 and N6 are both cases where the lesson/tool existed
and the wiring that makes it self-executing did not. #290 exists to close that specific gap:
a check owed per-config is not DONE until a supervisor runs it unprompted.

---

## Chain status at audit time (primaries, not this doc)

4 of 17 engine configs landed (cfg1, span9, span20, span50 — all reproduction-PASS, all
battery-terminal); span100 RUNNING (dir present, workers started 16:46); 11 specs queued
behind it, serial, ordered by expected information. span9 is the standout so far:
regime_flip is_ci_lo +0.167 / is_sharpe 0.489 / 609 fires vs baseline cfg1's
breakeven_plus_trail −0.087 / 0.263 / 373. Step-1 is ranking only — no admission (B1608).
