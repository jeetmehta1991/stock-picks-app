# B3096 semantic audit of the class-level optimisation runbook

2026-09-24, batch B3096 (ticket S6-B3096).

Source of truth (per CHECKLIST #77): the archived pre-B3096 text
`archive/2026-09-24-strategy-optimisation-plan-pre-B3096/STRATEGY_OPTIMISATION_PLAN.md`, the
`STRATEGY_OPTIMISATION_PLAN.md` and `STRATEGY_CAMPAIGN_LOG.md` committed with this file, and the code
paths each finding cites.

**What was compared.** The rewritten `STRATEGY_OPTIMISATION_PLAN.md` (class-level, sections 0-8) against
the archived pre-B3096 text (`archive/2026-09-24-strategy-optimisation-plan-pre-B3096/STRATEGY_OPTIMISATION_PLAN.md`,
byte-identical to the plan at commit 3dc28a428). Eight reviewers each took one section range and read old
against new sentence by sentence, opening the code wherever a claim touches it. The mechanical checks below
compare tokens, sentences and figures; this pass compares MEANING: a changed value, a widened scope, a lost
owner reservation, an unsourced addition.

**How findings were handled.** Every finding was re-checked against the archive and the code before its
disposition was written - a reviewer's report is not evidence on its own (execution-discipline, Truth &
Evidence rule 2). The per-finding ledger is reproduced at the end.

| reviewer | sections | findings | fixed | correct as written | archive's own error, marked |
|---|---|---|---|---|---|
| 1 | §0-§1 | 16 | 16 | 0 | 0 |
| 2 | §2 | 13 | 11 | 1 | 1 |
| 3 | §3 + §6 | 5 | 5 | 0 | 0 |
| 4 | §4.1-§4.7 | 14 | 14 | 0 | 0 |
| 5 | §4.7-§4.9 | 13 | 10 | 3 | 0 |
| 6 | §5 | 14 | 14 | 0 | 0 |
| 7 | §7 | 11 | 10 | 1 | 0 |
| 8 | §8 | 14 | 13 | 1 | 0 |
| **total** | | **100** | **93** | **6** | **1** |

## The kinds of drift it found (for the next rewrite)

- **Scope widened when a family name came out.** A pin described as checking "every landed artifact" when
  its glob matches one family's grids (§7.4); a sweep HALT row that no longer said what battery step 1
  checks (§8.7); an owner ruling for one nine-wave sweep restated as a rule for every sweep (§8.7); a kill
  path the archive scoped to the SUPERVISOR restated for every wall-time kill (§8.6, found while verifying).
- **A superseded passage restated as a live rule** (§7.4 cell format).
- **Figures dropped with their passage** - the 7.3 h cost row and its 39.7 h derivation (§8.3), three rank
  figures (§7.5), the 22-effective-exits count (§7.5). The figure probe missed the 7.3 h row because the same
  value occurs in an unrelated sentence (§4.8) - a value-only test passes on a coincidence (S6-B3096h).
- **Unsourced additions, true or not.** Each now carries its source or an "(added B3096)" marker.
- **Imprecision in my own additions** - "first" for "one", a percentage attributed to the wrong file, a
  line citation off by one, a pool setting presented as an optimum.

## Mechanical checks run alongside (final state)

| check | result |
|---|---|
| structure - numbering, references, headings, class-level scan (`check_b3096`) | 72 of 72 PASS; 0 strategy or family tokens |
| fidelity CLI (`scripts/doc_rewrite_coverage.py`) | PASS: 0 citation tokens missing, 0 owner-reservation sentences unmatched, 29 recorded acceptances, 0 stale |
| figures (probe, number-unit spacing normalised) | 295 figures: 145 in the runbook, 127 only in the campaign log (127 of 127 in passages moved verbatim), 23 absent from both, each dispositioned in `b3096_rewrite_coverage_accepted.txt` |
| campaign log | 71 of 71 archive ranges present verbatim (1,733 lines), inner headings demoted as its header states |
| new grid Table D ordering pin | bites: a copy of `producer_variant_table.py` whose two sort sites key on Sharpe inverts the order and fails it |

## Found while verifying a finding, not by a reviewer - S6-B3096g

The rewritten §8.6 said a wall-time kill flushes the open-book checkpoint "through an out-of-loop emitter".
The archive said the SUPERVISOR does, and the code agrees only for the supervisor. The engine has four
`engine_state.json` writers (`backtest/engine/backtest.py`):

| writer | portfolio block (S6-B2387) | open-book checkpoint (S6-B2213a) |
|---|---|---|
| supervisor `_emit_kill_state` (:1006) | written | flushed unconditionally (:1066) |
| in-loop wall-time kill (:1443, state :1494) | NOT written | flushed only inside `if self.closed_trades:` (:1452) |
| periodic checkpoint (:1631, state :1652) | NOT written | flushed unconditionally (:1641) |
| final `complete` state (:1764) | NOT written | not resumable, so moot |

So a resume from an in-loop kill or a periodic checkpoint (every crash-and-resume) restarts portfolio cash
and positions - the engine logs it as a "pre-B2387" checkpoint - and an in-loop kill before the first closed
trade can leave a run the resume refuses. **Scope:** the portfolio half is inert in an isolation cube -
every optimisation run - because isolation never mirrors a trade into the portfolio (`backtest.py:3379-3380`;
exits are guarded by `ticker in self.portfolio.positions`), so its equity never moves and the drawdown
multiplier that could gate entry stays 1.0; it matters for a non-isolated run. The refusal half is
fail-closed in any run. The paused c14 Step-2 checkpoint
(`output_candle_tws_c14_step2_step2_b0.5_s0.0_w0.3/engine_state.json`) was written by the supervisor
(`status` supervisor_active_cap, portfolio block present, 67 of 67 open rows) and is unaffected. Engine code:
ticketed OPEN and owner-gated, held with the paused resume work; nothing was changed.

## The per-finding ledger

### §0-§1 (reviewer 1): 13 findings + 3 unsourced - ALL VERIFIED against archive/code; dispositions:
- A1 FIXED §1.4 psr remaining control (archive 1008-1013 superseded 1057-1061)
- A2 FIXED §1.4 multiplicity: only first family's 3 graders + offline_level_sweep; 2 graders none -> TICKET S6-B3096f
- A3 FIXED §1.7 redundancy audit after loosening (#169) AND tightening (pre-B3096 row)
- A4 FIXED §1.8 NEGATIVE closure also via offline read / sibling pass (archive 3771-3774)
- A5 FIXED §1.6 OPEN consumers only (archive 3971-3972)
- A6 FIXED §1.6 forward pre-registration of an old-holdout sibling cell (archive 2851)
- A7 FIXED §1.6 blast radius: risk (B1617) + resolution S6-B1617b (EXECUTED, suffixed variants)
- A8 FIXED §1.5 restore "if a fire-adding param is added to the graded grid..." (archive 2634-2635)
- A9 FIXED §1.3 venue ruling S6-B2107a precedes non-local launch (archive 3399-3400)
- A10 FIXED §0.2 BOTH enters W-L only if T4 graded nothing rankable (archive 3939-3940)
- A11 FIXED §0.3 TIGHTEN-lane producer-band resim legs in-mandate in that lane (archive 3914-3919); owner-WAIVED already present
- A12 FIXED earlier (holdout read count, 3 sites)
- A13 FIXED §0.1 breadth read: shared one read (§4.4 items 5-6) or own read (§3.6 item 7)
- U1 FIXED cite CLAUDE.md for Stage 2; U2 FIXED hash stamped only when spec declares step (run_wave.resolve_ruled_scope); U3 FIXED mirror row sourced (B1382, B610/B611)
### §2 (reviewer 2): 13 findings - ALL VERIFIED; dispositions:
- B1 FIXED R9 precompute refusal wired for ONE family tag only (producer_variant_table.py:3289)
- B2 FIXED R3 probe: also read run_<family>, 4 legs; family_refusal treats free_levels optional (run_postconfig.py:477-479)
- B3 FIXED R6 class = precompute/consumer/engine; raw-bar re-derivation is one family's stronger form (B2899)
- B4 FIXED item 9 marked: pre-B3096 25/100 floors
- B5 FIXED item 13 restored: hourly PushNotification + */13 sentinel + CronDelete (archive 808)
- B6 FIXED survival check applies to ANY strategy (archive 3847)
- B7 FIXED two lower bounds: survival (S6-B2814) vs gain projection (S6-B2810d)
- B8 FIXED 46.2 pct "first" -> "one changed strategy" (my own B3096 addition, imprecise)
- B9 FIXED four resim levels, not two (archive 1326-1327)
- B10 FIXED item 16 marked: pre-B3096 A+B predates C/D
- B11 FIXED marked: "cannot run Step 1" -> engine Step 1; offline path still open
- B12 CORRECTED AGAINST THE ARCHIVE: --factorial only PRINTS (producer_variant_table.py:4340); the .md is written after grading - marked
- B13 NO CHANGE: LOCAL-mode qualifier matches prelaunch_gate.py:101-126 (LOCAL vs non-local manifests)
### §3 + §6 (reviewer 3): 4 findings + marker notes - ALL VERIFIED; dispositions:
- C1 FIXED T6 readers: breadth labels DISCLOSED-RE-READ; offline refuses only its own --out (--force-rerun overrides)
- C2 FIXED §3.3 reproduction vs SURVIVING subset (B2822); 2,116 of 2,116 kept as the measurement
- C3 FIXED §6.3 item 7: reproduction check = remaining admission step; wiring = NEW-GATE; S6-B2411 DROPPED 2026-09-03 (stale deferral not restored as live)
- C4 FIXED §6.3 item 6: count REGISTERED mirror (S6-B2417); missing mirror under standing directive, EXPLORATORY
- C5 FIXED F5 marker: PROPOSED-NOT-BUILT stale since B2644
### §4.1-§4.7 (reviewer 4): 13 findings + 3 unsourced - ALL VERIFIED; dispositions:
- D1 FIXED tie-break = rule recorded before ranking (first: lowest fire-adding-axis value; later: lower config index - archive 892, 1696)
- D2 FIXED slate only when EVERY Step-1 spec COMPLETE; top-3 + is_ci_lo in queue row (archive 3487)
- D3 FIXED Step 1.7 operator PROPOSES; relaunch waits for owner (CHECKLIST #120 verbatim; owner 2026-08-25)
- D4 FIXED HALT queue row restored (archive 3486)
- D5 FIXED Step 1.3 copy own family's spec, diff vs template in turn; window/tickers injection reconciliation marked (B2713)
- D6 FIXED leverage: "sometimes exactly what the owner wants" (archive 3656-3657)
- D7 FIXED retracted small-slice rule dropped with note (B1877); zero_output_runs kept
- D8 FIXED fixed-list cost sentence restored (archive 1411-1412)
- D9 FIXED L3 floor marked (> 75; pre-B3096 "100")
- D10 FIXED L3 feasibility scoped to families whose primitives re-derive offline
- D11 FIXED _sweep_200 marked (pre-B3096 _sweep_100)
- D12 FIXED 70 pct attributed to _t10 only
- D13 FIXED pool workers: 0 for clean timing; 10 physical cores on this box
- U(4.6) FIXED grading description scoped: first family's grader; Step-1 holdout empty; later graders per their headers
### §4.7-§4.9 (reviewer 5): 13 findings - ALL VERIFIED; dispositions:
- E1 FIXED pre-triage MANDATORY BEFORE ANY STEP-2 CUBE (archive 1084) + added as Step 2.1 item 1
- E2 FIXED Step 2.1 reordered: pyramid+commit before manifest (manifest pins launched HEAD)
- E3 FIXED hand-run correction marked (stale since B2082)
- E4 FIXED baseline arrives free only if production ranks into the slate (archive 1158-1159)
- E5 FIXED median "is wrong for" a selected slate; ~25 h understatement cited (archive 901, 912)
- E6 FIXED restored: marginal winner ENDS the campaign's Step 2 (archive 996-999)
- E7 FIXED owner words: answered "A" then "Pause" (ledger 14341), not "fix first"; backtest.py:2144-2146
- E8 KEEP resumed-rate mis-scale (code matches run_wave.py:242/:87)
- E9 FIXED pool_workers 6 = relaunch value after commit exhaustion, not an optimum
- E10 FIXED crash-and-resume sourced (S6-B3094f item 3)
- E11 KEEP S6-B3093c / L865 (ledger + LEARNINGS sources)
- E12 KEEP "lands or stops" (CHECKLIST #320)
- E13 FIXED tier sentence made descriptive of Table D (archive 559, 1709-1713)
### §5 (reviewer 6): 14 findings - ALL VERIFIED; dispositions:
- F1/F2 FIXED rules 2-3 "judgment step(s)" restored (archive 1997-2001); owner-word re-examination sourced (§1.3, owner 2026-09-12) + marked
- F3 FIXED step 6 admitted-closed exception dated + marked (postdates pre-B3096 wording)
- F4 FIXED cube sanity: fails only UNDECLARED strategies; declared-but-absent rider passes (run_postconfig.py:117-137) - table row + PASS line
- F5 FIXED M8 marked + S6-B2118b trigger kept (first SHORT wave -> P1)
- F6 FIXED M6 carryover marked; S6-B2213a (restore) + S6-B2404 (rename), run_wave.py:323-329
- F7 FIXED regime_flip chronology: time stop before B2043; B1622 never ran (B1680); post-B1682 falsified (B2018); resume loss added B3096 from ledger
- F8 FIXED "other eleven are read and applied by judgment" restored (archive 2585); automated lens battery distinguished
- F9 FIXED re-derive + diag-loss gate and REFUSE are two graders' protections, not a class property
- F10 FIXED step 8 "of 26" marked (pre-B2110 registry)
- F11 FIXED spot-check leg: first family calls vendored library; one family never imports producer (B2899)
- F12 FIXED undelivered() reducer cites L737
- F13 FIXED step flag: engine hook passes none -> manifest window decides (derive_step 398-417); run_wave flag only on fallback (--if-not-landed, postconfig_landing 451-457); ALSO corrected §4.9 Step 2.2 bullet (archive-carried overstatement)
- F14 FIXED "5 of 200" restored; §5.3 heading keeps "canonical for legacy cubes"
### §7 (reviewer 7): 11 findings - ALL VERIFIED; dispositions:
- G1 FIXED §7.4 test_b3023 glob covers one family's grids only (test_unit.py:42860) - scope stated; per-config figures to log F.6
- G2 FIXED §7.4 cell-format paragraph restored as superseded lineage (B2585 replaced the hardcoded list); live rules cited to producer_variant_table.py:4117
- G3 FIXED §7.4 config-block dating: first family's grader since B2138, other families' P<N>_<name> keys since B2542 (producer_variant_table.py:4109)
- G4 FIXED §7.6 multi-leg regime_flip degradation marked "added B3096 from the ledger" (S6-B3094c)
- G5 FIXED first worked formula: archive 372-410 moved verbatim to NEW log B.16; §7.1 pointer + APPENDIX M mapping repointed (were log B.1, which holds only prose)
- G6 FIXED grid Table D ordering had NO pin: NEW test_b3096_grid_table_d_orders_on_the_lower_bound; bite proven by a Sharpe-sorted mutant copy of the renderer (order inverts)
- G7 FIXED §7.5 S6-B2500 registry fallback caveat restored (producer_variant_table.py:3544-3551)
- G8 FIXED §7.6 chronology: B1622 fix never ran (found B1680); post-B1682 claim falsified B2018; B2043 put the map in the payload
- G9 FIXED §7.3 pre-B3096 25/100 floors marked as superseded by the 2026-08-29 rulings
- G10 FIXED dropped measurements restored: 22 effective per cell (dated) and +0.098/n=128, +0.179/n=40, +1.214/n=11; the family-specific 2-of-14 disagreement to log F.6
- G11 NO CHANGE: L652 / #285 generalisation is sourced (CHECKLIST.md:5451)
### §8 (reviewer 8): 10 findings (+ minors) - ALL VERIFIED; dispositions:
- H1 FIXED HALT row = battery step 1 as coded (run_postconfig.py:117-137): an UNDECLARED strategy fails; pre-B3096 "not exactly 1 strategy" marked
- H2 FIXED canonical-rate bullet: the 0.2613 rate is pool=10; sequential 200-ticker runs 85.5-127.9 s/sim-day vs 52.3; pooled Step-2 at 544 ran 80 s (pool 10) and 49.49 s (pool 6) vs 142 (archive 1862-1869, 2237-2240) - the B3096 draft's unsourced "under-projected 1.6-2.4x" was 85.5/52.3 and 127.9/52.3, pool-0 runs against a pool-10 rate
- H3 FIXED Option C scoped to the nine-wave sweep it was ruled for (archive 2206-2208)
- H4 FIXED monitor duties sourced: derive-never-type prompt = L839 + S6-B2972 (the unsourced "named anchor" wording replaced); re-delivery = owner 2026-08-25 (memory)
- H5 FIXED resume text marked added B3096 (archive had none); M6 kept by name, rename marked (S6-B2404)
- H6 FIXED post-processing scoped to ONE-strategy configs; contrast 1.93 of 4.56 h at 182 strategies
- H7 FIXED pool_workers reader = run_wave.py:260; launch_sweep.py has 0 "pool" references (grep) - marked
- H8 FIXED only two early configs' values were recovered from their run log (S6-B1537b); spec-launched configs carry their own
- H9 FIXED timing-A/B ban (L621) separated from the full-suite-beside-a-live-wave ban (commit exhaustion; archive 1882 scope)
- H10 FIXED DEMAND_PRUNING "Set 0 to disable it if..." (archive 2086)
- minor FIXED 7.3 h row + the 39.7 h derivation restored (archive 1169-1170)
- minor FIXED HALT owner-call basis: the table is an owner ruling (§8.7); archive 1361 "left as-is" is consistent
- minor NO CHANGE: backtest.py:212 / B1321 / backtest.py:3054-3055 correct in code; peer-reporter "mandated nowhere" backed by S6-B2548 / S6-B2618a
- minor FIXED failure-modes row "multi-leg regime_flip" marked added B3096
### Found while verifying H5 (not a reviewer finding) - NEW TICKET S6-B3096g:
- §8.6 kill sentence had DRIFTED from the archive ("the supervisor flushes" -> "a wall-time kill flushes"); restored to the supervisor
- MEASURED: 4 engine_state writers - supervisor _emit_kill_state (portfolio block YES, open book unconditional), in-loop kill (portfolio NO, open book only inside `if self.closed_trades:`), periodic (portfolio NO, open book unconditional), final/complete (portfolio NO; not resumable)
- c14's paused checkpoint is status=supervisor_active_cap with portfolio=True and 67/67 open rows - unaffected
- engine code, owner-gated, held with the paused resume cluster; no code changed
