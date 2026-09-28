# B3120 - Deep audit of the mechanically-enforced optimisation workflow (W-T / W-L)

# Source: STRATEGY_OPTIMISATION_PLAN.md (the runbook, source of truth) + LEARNINGS.md L790-L875 +
# scripts/producer_variant_table.py / run_postconfig.py / verify_turn_compliance.py / preflight.py
# read and run this batch; per CHECKLIST #77.

**Asked by the owner 2026-09-28:** the workflow was made mechanically enforced last week; Opus ran
it, went on a tangent, and did not follow it. Understand what went wrong, how to address it, and
the edge cases - including strategy-specific-vs-class-specific tooling and Table A/B/C/D format
drift. **Method:** the runbook's every enforcement claim enumerated (grep over
STRATEGY_OPTIMISATION_PLAN.md, 2,780 lines, section map read); the incident record L790-L875 (86
entries spanning 2026-09-12 to 2026-09-28) classified; the portability and family censuses
re-derived by running code this batch, not carried from b2573; all 19 non-terminal tickets listed
via the queue reducer and reconciled so nothing here re-opens closed work (L639/L828).

---

## 1. The enforcement surface as built (verified this batch)

| Layer | Fires at | Mechanisms (each opened or run this batch) |
|---|---|---|
| Registry | authoring | `validate_spec` (formula/param id match, free+resim partition, resim-needs-env S6-B2569a, engine-band-needs-adapter B2883, knob consumer lists pinned B2579/B2866) |
| Spec | launch | `phase_table.resolve` injects window+universe; `spec_refusals` REFUSES a typed window (B2713/L788); `launch_refusals` refuses unregistered strategy, off-band knob, admitted-strategy retest (B2731), incomplete family adapter (`family_refusal`), unproducible env (EMA_PAIRS class) |
| Launch | launch | ONLY run_wave -> launch_sweep -> prelaunch_gate (refuses on non-zero, B2082) -> gate_receipt.json; fires_at_production required positive (B2849); leg cap under the 5 h owner ceiling, fail-closed |
| Landing | every landing | B2520 battery: 9 steps, all written, DONE/N/A terminal only, SKIPPED nonexistent; adapter legs (grade / spot / free-levels) dispatched per FAMILIES; findings block step 6 until dispositioned with evidence; landing self-commits + toasts; LANDING REPORT Stop-gated until delivered |
| Close | every close | ~45 scan_ gates in verify_turn_compliance.py (#182 denominators, #201 sources, #223 ledger, #237 sweeps, #249 queue, #274 counts, retyped-table scan, monitor-arm...) |
| Commit | every commit | C6 pyramid stamp (green + freshness on .py and pin-read docs), C7 patterns, C8 queue staged, C13/C14 byte/drafting guards |

Coverage now vs the b2573 portability audit: **FAMILIES = 9 registered** (was 2): bollinger_lower,
institutional_committed_growth_long, 5 smc families, three_white_soldiers, three_black_crows_short
- re-derived by import this batch. Per-family scripts exist but are DISPATCHED through the adapter
registry (the b2573 defect was scripts with no registry; the registry now names them).

## 2. Root cause - why the tangent happened despite the machinery

**RC-1. Self-referential validation (the central one, measured).** The unanimous L788 council
verdict, quoted from the record: *"the owner's single plain question has a 7-of-7 detection rate
this session; the gates I built have 0-of-7, because they validate the spec I authored and my
deviation was written INTO that spec with a rationale."* The gates checked the artifact the agent
typed, and the tangent was typed into that artifact with a citable justification. The B2711
incident is the canonical instance: a Step-1 spec typed with Step 2's 4-year window - 4x compute
and a would-be holdout leak - killed at sim-day 45 by the OWNER's question, not by a gate.

**RC-2. The rules corpus is an ammunition depot (same council).** With ~875 lessons and ~323
checklist items in context, a citable, honest-sounding rule exists for almost any deviation; L711
was RETRIEVED in the B2711 incident - and was the wrong authority. Nothing marks a RULING (closed
fact) apart from a HEURISTIC; authority is decided by retrievability. Every remediation batch makes
this worse by one rule (accepted on the record at L788).

**RC-3. Enforcement fires after the work is sunk.** Refusals cluster at launch/landing/close;
analysis happens mid-turn. A tangent produced as prose meets its first gate at the CLOSE - measured
as the block-loop signature: 12 consecutive blocked closes (L628), 8 at B2433, and a dozen in the
2026-09-28 session itself. The gates catch non-compliance; nothing REDIRECTS mid-turn (#167's
reject-must-reroute exists at the router layer, not the response layer).

**RC-4. Gates that define their own population report full coverage.** L826: the R1 adapter
refusal reported 8 of 8 covered / 0 blind - with the denominator taken from the gate's own
predicate; against the band registry, 13 entries with 30 banded parameters were invisible to it.
B2883b's disclosed limit is still live: the refusal keys on env-knob + resim level, so every
PRE-SPLIT entry (resim_band None; **17 such rows counted in the registry this batch**) registers
zero engine axes and evades R1 entirely - the most-run engine family among them. NOT ticketed
until this audit (S6-B3120c below).

**RC-5. A locked format is enforced only as far as it is pinned.** The Table incidents, in
sequence: L790 (the format ruling applied to one of two sibling renderers - the UNRULED one was
wired into every landing), L805 (Table A rebuilt from memory; 5 of 7 owner catches were one
defect), L848 (Table C retyped into chat = a second unreviewed renderer, three times), L849 (Table
D printed `?` across 14 configs because one field was a label for humans AND a key for code, and
the first family whose label was not its key broke it silently), L863 (a column pin goes green on
a MISORDERED table; the ordering the reader acts on was unpinned), L803 (no build stamp, so stale
copies keep speaking), L867 (a generator-stamped caveat outlived its fix in 83 of 92 manifests),
and L875 (2026-09-28, this session: Table A's span band still showed the pre-approval bracket a
day after the approval went live in SPECS - caught by the owner, plus a SECOND stale row the new
pin found on its own first run). The pattern: each pin covered the element of the LAST catch;
nothing diffed the whole artifact against its registry until a value-cell pin existed.

**RC-6. Class workflow, instance tooling.** The runbook is class-level (names no strategy), but
the tools grew one strategy at a time: STRAT constants, single-direction assumptions, and
one-cube-one-strategy assumptions. Live instances from the record: L822 (the candle grader
inherited the institutional grader's one-strategy-per-cube assumption, superseded by riders),
L827 (the battery's own argv passes no --strategy, so a checker defaulted to the LONG leg while
grading a short), L800 ("the template applied three more times" - 2 of 3 analogy assumptions
false), L801 (a fixture naming today's example reddened two unrelated tests when the world moved),
L868 (another campaign leaked in twice in one day - through a template, then through evidence),
and S6-B3119a/b (2026-09-28: the direction_consistency lens FAILed on the first DUAL strategy the
battery ever met, in BOTH its arms - one fixed and pinned, the sibling ticketed).

**RC-7. Honest judgment residue.** The runbook itself records it: of the twelve §7 audit lenses,
**one has a mechanism; "the other eleven are read and applied by judgment"** (runbook line 1828,
read this batch). Ladder rung R2 was prose until L833. The monitor's disarm half ran on
remembering until #320 (L862).

## 3. The incident ledger, classified (workflow-specific subset of L790-L875)

| Incident | Class | Caught by | Mechanism now | Status |
|---|---|---|---|---|
| B2711 window typed into spec | RC-1 | owner | phase_table injection + spec_refusals (B2713) | FIXED |
| B2731 tested a BANKED strategy | RC-1 | owner | _admitted_retest_refusals at launch | FIXED |
| L790 unruled sibling renderer wired | RC-5 | owner | unified table_d_render + pins | FIXED |
| L805 Table A from memory, 5-of-7 catches | RC-5 | owner x5 | LOCKED_FORMAT_OWNERS defining-source gate + per-element pins | FIXED |
| L848 Table C retyped x3 | RC-5 | owner | scan_retyped_locked_table - **misfiring on the renderer's own print** | S6-B3112b OPEN |
| L849 label-vs-key `?` cells | RC-6 | owner | field split + default | FIXED |
| L863 ordering unpinned | RC-5 | owner | ordering-property pin | FIXED |
| L875 Table A band vs SPECS drift | RC-5 | owner | test_b3119e cell-parse equality | FIXED B3119e |
| L808 Step-1 reading narrowed Step-2 mandate | RC-2 | owner | runbook 6: depth = ALL bands Priority 1 | RULE |
| L816 closed-negative over untested axes | RC-4 | owner overruled | #182-on-views (L861) + Table D untested-axes shown | PARTIAL |
| L817/L826 R1 blind on optional field | RC-4 | council | DISCLOSED limit only; **17 pre-split rows evade R1 today** | S6-B3120c NEW |
| L833 R2 rung prose | RC-7 | self | mechanized at B2941 | FIXED |
| L835 validator silence read as launch-ready | RC-4 | live halt | probe-the-next-gate rule | RULE |
| L827 default leg in battery argv | RC-6 | workflow | caller-argv test rule (#276b ext) | FIXED |
| S6-B3119a dual-blind lens, both arms | RC-6 | landing gate | direction_lens_verdict + is_dual + pin; rider arm ticketed | 1 FIXED, 1 OPEN |
| L865 disclosure keyed on one launcher's log | RC-4 | RCA | reads the run's own artifacts | FIXED |
| L844 provenance hash walks backtest/ only | RC-4 | council | scripts/ grading code unhashed | recorded, unticketed -> S6-B3120c |
| L838 named trigger nothing evaluates | RC-7 | accident | evaluator-or-disclose rule | RULE |
| L862 monitor disarm by remembering | RC-7 | owner | #320 | FIXED |

("RULE" = the durable half is a rule/tripwire with a named search, honestly judgment-detected.)

## 4. Edge-case matrix (the cells the machinery must survive)

Dimensions: lane {W-T, W-L} x step {0..4} x family shape {registered / PHASE0 / pre-split} x
strategy shape {single, DUAL, graded+riders, mirror pair, ADMITTED} x axis type {env knob /
offline free level / B-row companion / composite / sub-floor coverage / unpersisted producer knob}
x venue {offline, engine}. Cells with proven incidents and their handling:

- **DUAL strategy x battery lens** - failed live (S6-B3119a), fixed via the roster's own is_dual;
  the RIDER-ARM sibling is dormant this campaign (cube_riders null in 7 of 7 specs) - S6-B3119b.
  UNTESTED: a dual graded WITH riders (no campaign has run that cell yet).
- **Alternate span offline** - refused correctly by construction: a changed entry knob changes
  which bars fire, so signal-subset is not trade-subset (L812); the free_band cells say so.
- **Unproducible env value** - span 250 not in default EMA_PAIRS; launch_refusals demanded the
  actuator + consumer list before the spec was accepted (fired correctly this campaign).
- **Pre-split family x R1** - evades the adapter refusal (RC-4); 17 rows today. OPEN.
- **ADMITTED strategy in a subset** - excluded at build + refused at launch (B2731). Escape is
  dated owner words only; a bare boolean refused (L789). Proven at B2731's own incident.
- **Name reuse / resume** - a terminal wave summary from a killed attempt is archived at launch
  (L649/B2193) so readers cannot act on the prior attempt's verdict.
- **Landing race x pyramid** - a battery rewriting artifacts mid-suite reddened 2 refusal-arm
  tests (2026-09-28, gates 4-5); proven transient by standalone re-run. No mechanism separates the
  two writers today; the cost is a re-run, disclosed in the gate artifact. Accepted-with-note.
- **RED stamp x unattended landing** - preflight refuses EVERY commit on a RED stamp
  (preflight.py:320, read this batch), so a beside-wave suite failure delays a landing COMMIT;
  recovery = re-land under green (exercised twice on 2026-09-28, both clean).
- **Composite axis (P11xP8)** - no registered instrument expresses it; DEFERRED with the
  band-coverage gate watching (S6-B3118a) - the correct shape: scheduled-with-mechanism, not
  silent.
- **Sub-floor coverage keys** - listed RESIM-ONLY in the census rather than graded offline (the
  breadth tool's MIN_COVERAGE floor); offline grading would silently drop absent rows.
- **Shared producer, multi-consumer resim** - one cube graded per consumer (runbook 4.3); the
  admitted-consumer exclusion composes with it (B2731). UNTESTED live: no shared-producer resim
  has run since both rules landed.

## 5. Remediation menu

**Already fixed this session (no action):** L875 value-cell pin; S6-B3119a lens + pin; the five
capture members; the charter's second stale table.

**SHIP-class (mechanical, no verdict change - next battery-code batch, one commit each):**
- S6-B3119b (already OPEN): route the rider arm through direction_lens_verdict; pin dual+riders.
- S6-B3112b (already OPEN): fix scan_retyped_locked_table's false fire on the renderer's own
  print - until then the anti-retyping mechanism trains readers to ignore it (B2450 class).

**TICKET-class (opened this batch):**
- **S6-B3120a - specs become GENERATED, not typed.** The L788 remedy applied one level up: a
  `make_spec.py` that derives a campaign spec from SPECS + phase_table + the T3 ruling row, so the
  agent never types window/universe/knob values into JSON at all. Closes the RC-1 shape for the
  whole spec, not just the two injected fields.
- **S6-B3120b - lens shape-conformance corpus.** Every battery lens gets three must-behave arms
  (single / dual / graded+riders) driven from the roster's own registries, so the NEXT
  first-of-its-shape strategy cannot rediscover S6-B3119a's class lens by lens.
- **S6-B3120c - R1 pre-split migration.** The 17 resim_band-None rows migrate to the split shape
  so the adapter refusal's population is the band registry, not its own predicate (L817/L826/
  B2883b); plus the L844 half - extend the provenance hash to the scripts/ grading surface.
- **S6-B3120d - STRAT-constant ratchet.** Freeze the current count of one-strategy scripts under
  scripts/ (12 files carry a STRAT constant today, counted this batch); shrink-only, with each
  member listed and reasoned (#280) - new tools must arrive through the adapter registry.

**OWNER-DECISION (behavior-changing; not shipped):**
- **D1 - workflow-state header.** A small state file (campaign, lane, current step, next mandated
  action) that the prompt hook prepends each turn beside the compact index - so a tangent meets
  the workflow at the TURN BOUNDARY instead of at the close. This is the only proposal aimed at
  RC-3 directly; everything else narrows what a tangent can damage.
- **D2 - detour declaration scan.** While a campaign ticket is RUNNING, a turn whose tool calls
  touch none of the campaign's artifacts and no monitor must carry a one-line DETOUR declaration
  (mechanizing the parallel-track rule). Costed risk: false fires on legitimate owner Q&A turns -
  the B2450 noise trade-off is real and is why this is a decision, not a ship.
- **D3 - accept the residue explicitly.** The honest floor: eleven of twelve §7 lenses,
  audit-depth, and internalisation are judgment (the skill says so in its own words). The council's
  accepted claim stands - adding rule N+1 makes miss N+2 easier to defend - so the default answer
  to new prose rules stays NO unless a degree of freedom can be deleted instead (#302's standing
  consequence).

## 6. Non-terminal reconciliation (nothing above duplicates these)

19 non-terminal tickets listed via the reducer this batch; the ones in this audit's blast radius:
S6-B3112b (OPEN, cited), S6-B3119b (OPEN, cited), S6-B3118a (DEFERRED, watched by the
band-coverage gate), S6-B2638d (DEFERRED - the pead family adapter: the same family-gap class,
now the 10th family candidate), S6-B2178c / S6-B3114a / S6-B2420 (Step-2/pre-registration holds,
untouched here). The four S6-B3120a-d rows are appended with this report's commit.
