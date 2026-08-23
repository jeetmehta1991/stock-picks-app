# DRAFT — CHECKLIST items #187–#192 + #237 (B2023, per the C1 ruling 2026-08-22)

**STATUS: DRAFT — OWNER APPROVAL REQUIRED. Not merged into CHECKLIST.md; drafts are not
self-merging (C1: "I DRAFT the 7 unwritten CHECKLIST items from their live gates and
citations; OWNER APPROVES the batch before merge").**

Why these exist: B1971 measured that these seven numbers are cited **94 times** across
LEARNINGS, EXECUTION_QUEUE, SKILL.md and the gate script (per-item: #237 ×22, #187 ×18,
#191 ×16, #190 ×11, #192 ×10, #188 ×9, #189 ×8) **and none is defined in CHECKLIST.md** —
the rules are live (five have running gates), only their definitions are absent. Each
draft below is derived from the live gate's own behavior and the L-entries that created
the rule, not invented.

**Known numbering collision to resolve at approval (L468):** the #187–#193 block was
appended without checking existing numbering. Today the LIVE universe-launch gate prints
"CHECKLIST **#193** / L445" for the rule the L468-era tier map assigns to **#187**. Two
clean resolutions: (a) approve #187 as drafted and repoint the gate message #193→#187, or
(b) fold the launch rule into the existing #193 and retire the #187 references. Drafted
below as (a); the choice is the owner's.

---

### #187 — UNIVERSE ARTIFACT VERIFIED AT LAUNCH (B1602 / L445)

**A config launch without a verified universe once cost 3.3 h × 2 searching an abandoned
A–C chunk** — 380 of 381 tickers started with A, B or C and nobody had looked at the list.

Any `run_phase1a.py` launch requires `verify_universe_artifact.py <tickers-file>
--compare-cube <baseline cube>` run **in the same turn**, exit 0, with the verdict pasted.
A deliberately narrow file (a timing slice) is permitted only with its narrowness stated
in writing where the run is recorded.

*Enforced by:* `scan_unverified_universe` (`verify_turn_compliance.py:589`), blocking.
*Lineage:* L445; `r5_universe_381.txt`; the B2018 Stop-hook fire on the sw30/sw50 launch.

### #188 — A MISS ACKNOWLEDGED IS A MISS RECORDED (B1573 / L-Phase-5 arc)

**Acknowledging a miss in prose is not recording it.** A response that admits an error,
a stale claim, or a skipped step and moves on leaves the miss with no durable artifact —
the exact failure Phase 5 exists to prevent.

Any turn whose response acknowledges a miss must, in the same turn, carry the Phase-5
artifacts: LEARNINGS entry + CHECKLIST item or explicit "compliance failure against item
N" + EXECUTION_QUEUE ticket + fix-or-ticket (+ mechanism per #236).

*Enforced by:* `scan_unrecorded_miss` (`verify_turn_compliance.py:3883`), blocking.
*Lineage:* B1577 (the gate's first catch: a monitor tick acknowledging nothing).

### #189 — NO UNTESTED CAUSE (B1587 / L455)

**A hypothesis presented as a finding is a fabrication, and a wrong cause is worse than
no cause — it closes the investigation.** L455's "probable cause is the warmup guard" was
disproven by one command; the affected rows sat at bars 799–1158.

If a cause can be tested with a command you already know how to run, RUN IT before naming
the cause. If it cannot be tested cheaply, the cause is **UNKNOWN — RCA NEEDED**, ticketed.
A causal claim never enters a durable artifact without EXECUTED evidence beside it.

*Enforced by:* `scan_unverified_cause` (`verify_turn_compliance.py:393`), blocking on
cause-language with no run-evidence language in the same turn.
*Lineage:* L455; the B2019 misattribution (L617) is the newest instance of the class.

### #190 — A FIX TOUCHES ITS DOWNSTREAM ARTIFACT (B1602)

**A commit whose message says FIX / DEFECT / RCA and touches no downstream artifact is
either self-contained or an unrecorded invalidation — and the reader cannot tell which.**

Any FIX-class commit must touch a downstream artifact or a queue entry; a genuinely
self-contained fix states "self-contained" in its queue row, which satisfies the gate.
(Companion of #196, which governs re-checking conclusions the fix invalidates.)

*Enforced by:* the FIX-commit scan (`verify_turn_compliance.py:563`), blocking.

### #191 — ANCHOR THE RULE (B1597 / L464)

**A rule recorded only in LEARNINGS is a story, not a gate.** Measured: 24 L-entries
stated a generalized rule; 18 were referenced in neither CHECKLIST nor the skill — a
75 % orphan rate — and every orphaned rule decayed while every scripted rule held.

Every L-entry stating a generalized rule MUST, in the same turn, be anchored by a NEW
CHECKLIST item citing the L-number, or an explicit citation of an EXISTING item that
already covers it.

*Enforced by:* `scan_orphan_rule` (`verify_turn_compliance.py:464`), blocking.
*Lineage:* L464; carried in SKILL.md ("ANCHOR-THE-RULE RULE").

### #192 — AN ANCHOR IS A HOME, NOT A MENTION (B1599 / L466)

**Claiming a rule is anchored because an entry MENTIONS an item number is the anchoring
defect one level up.** L465 was called anchored because it mentioned #190 and #191;
neither item stated its rule — the mention pointed at a house with nobody home.

When citing an existing item as a rule's anchor, the cited item must actually STATE the
rule (or be amended in the same turn so it does). A number in prose is not an anchor.

*Tier:* judgment (prose) — no scan can tell a home from a mention. *Durability backstop:*
`test_b1971_no_new_dangling_checklist_citation` (shrink-only ratchet: a citation of an
undefined item can never be newly introduced).

### #237 — RETROACTIVE SWEEP ON EVERY NEW RULE AND EVERY CLASS FIX (B1757 / L512-arc)

**A rule added without sweeping for existing instances leaves the siblings the
GENERALIZATION MANDATE calls non-compliant; a class fixed at one site leaves the site you
were not chasing.** The sweep that found these seven items missing was itself a #237 sweep.

Any turn that adds or tightens a rule, or fixes an instance of a defect class, states in
the response **what ELSE was scanned for this class, and what it found** — naming the
search executed, with a zero-findings answer stated as such (a zero is a finding).

*Enforced by:* the retro-sweep scan (`verify_turn_compliance.py:3426`), blocking.
*Lineage:* B1970 (the collector had the same bold-requirement as the gate being fixed);
B1971 (the sweep that found this item undefined); L603/L605.

---

**Approval mechanics:** on owner approval these seven blocks merge into CHECKLIST.md
verbatim (with any owner edits), the #187-vs-#193 gate-message collision is resolved per
the owner's (a)/(b) choice above, and `test_b1971_no_new_dangling_checklist_citation`'s
frozen dangling set shrinks by seven — the ratchet's designed direction.
