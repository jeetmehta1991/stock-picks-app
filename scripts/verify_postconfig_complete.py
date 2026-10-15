#!/usr/bin/env python
"""Every completed cube must carry a COMPLETE post-config ledger. Mechanically.

B1699, owner catch. The runbook has said since it was written:

    MANDATORY POST-CONFIG ANALYSIS (owner directive - run after EVERY config,
    unprompted). "Skipping a step is a silent miss."

I ran 1-2 steps per turn and waited to be asked for the rest, four times. When
the owner pointed at it I VERIFIED the text was already there and wrote a ticket
saying it "needs mechanical enforcement like #221, not another sentence."

**That ticket was itself another sentence.** Ticketing the need for a gate is not
building the gate - the same deferral, one level up, which is exactly what the
GENERALIZATION MANDATE forbids.

And the reason no existing hook caught it: `verify_turn_compliance.py` has TEN
gates and every one of them checks how work is REPORTED or COMMITTED - verdict
denominators, orphan rules, unverified claims, artifact drift, the compliance
marker. **Not one checks whether mandatory work RAN.** A turn could skip the
entire post-config sequence and every gate would pass, because each gate audits
the description of the work rather than its existence.

This closes that hole. For every cube that finished, a ledger entry must exist
with all NINE steps dispositioned. Silence is not a disposition.

S6-B2440 (owner-approved 2026-08-30): neither is a DEFERRAL, for the four
JUDGMENT steps - 42 skips citing a review batch that never existed had passed
this gate unchallenged (L721).

B2520 (owner ruling 2026-09-01: "Why are some steps skipped after each config?
They should ideally not get skipped at all!!!"): SKIPPED is terminal for NO
step. Every one of the nine steps closes only as DONE (it ran, with evidence)
or N/A (it cannot apply to this config, with the reason). The battery
(scripts/run_postconfig.py, invoked by scripts/postconfig_landing.py from the
engine itself the moment a cube lands) records every step, so a SKIPPED row
can now only come from a hand edit - and it blocks until dispositioned.

Exit 0 = every completed cube has a complete ledger.
Exit 2 = a cube exists with a step that is neither DONE nor N/A-with-a-reason.
Exit 3 = the ledger is unreadable (fail CLOSED).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEDGER = ROOT / "output_audit" / "postconfig_ledger.json"

# The nine steps the runbook mandates, in order.
STEPS = [
    "1_cube_sanity",
    "2_grade_with_config_params",
    "3_outlier_discrepancy_sweep",
    "4_three_leg_spot_check",
    "5_adversarial_lens_review",
    "6_post_fix_recheck",
    "6b_equivalence_class_check",
    "7_implement_in_engine",
    "8_verdict_with_denominators",
]
# S6-B2440 (owner-approved 2026-08-30, council recommendation): SKIPPED stopped
# being TERMINAL for the four JUDGMENT steps.
#
# WHY. Measured at S6-B2436: across all 31 Step-1 configs AND the Step-2 config,
# the four judgment steps were SKIPPED, every one carrying the reason
# "PENDING-WAVE-REVIEW: the wave-level review batch performs this step" - naming
# a batch that has never existed. The old TERMINAL set accepted SKIPPED with ANY
# reason, so the gate audited whether a decision was RECORDED and never whether
# the work was DONE (L721). A deferral to a process nobody built satisfied a
# mandatory control 42 times.
#
# B2520 closed the other half: SKIPPED is terminal for NO step, AUTO steps
# included. The five AUTO steps had kept SKIPPED "because a skip there is a real
# operational disposition" - and MEASURED, the skips it admitted were not:
# step 2 SKIPPED on every non-smc cube with the wrong diagnosis "pre-B2138
# cube" (a family the grader could not dispatch), step 4 SKIPPED on every
# institutional cube because no spot-checker existed for the family. Both were
# missing MECHANISMS recorded as dispositions. The remedy is the mechanism
# (grade_institutional_config.py, spot_check_institutional.py, a fail-closed
# family registry) plus a gate that no longer accepts the excuse.
#
# A deferral is not a disposition. Only DONE (it ran, evidence) or N/A (it
# cannot apply to this config, reason) close a step - any step.
JUDGMENT_STEPS = frozenset({
    "5_adversarial_lens_review",
    "6_post_fix_recheck",
    "7_implement_in_engine",
    "8_verdict_with_denominators",
})
TERMINAL = {"DONE", "N/A"}
TERMINAL_JUDGMENT = TERMINAL


def terminal_for(step: str) -> set:
    """The accepting states for one step - the same two for every step since
    B2520 (kept as a function: two pinned tests and the doc renderer call it,
    and a future per-step distinction belongs here, not in a caller)."""
    return TERMINAL_JUDGMENT if step in JUDGMENT_STEPS else TERMINAL


def is_closed(row) -> bool:
    """A step is closed only by a terminal status carrying its evidence: DONE
    with evidence, or N/A with a reason. An N/A with nothing behind it is a
    skip wearing a different word (L642: the absent case is the guarded case)."""
    if not isinstance(row, dict) or row.get("status") not in TERMINAL:
        return False
    return bool(str(row.get("evidence") or row.get("reason") or
                    row.get("note") or "").strip())


_TOOLS: dict = {}


def _family_tools(strategy: str) -> dict:
    """The battery tools block for a strategy - SPECS[...]["tools"], the
    registry run_postconfig._tools reads; {} for a strategy outside it."""
    if strategy not in _TOOLS:
        scripts = str(ROOT / "scripts")
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        import producer_variant_table as pvt
        _TOOLS[strategy] = (pvt.SPECS.get(strategy) or {}).get("tools") or {}
    return _TOOLS[strategy]


def leg2_gap(key: str, entry: dict, *, oa: pathlib.Path | None = None,
             tools_of=None) -> str | None:
    """S6-B3173 (B3139q-r70i, L919): a DONE step 2 owes BOTH legs.

    B2569 made step 2 two legs on every landing, and the battery writes DONE
    only when both ran (run_postconfig: ok2 and okf). A HAND completion
    bypasses that: config 1 of S6-B3171 was recorded DONE on the family
    grade alone, and is_closed() - which reads the status word and its
    evidence - passed it. So a DONE step 2 whose family declares
    tools.free_levels must have its leg-2 artifact on disk.

    The family is read from the leg-1 artifact's own strategy field; an
    entry without a readable leg-1 artifact is not judged here. MEASURED at
    landing over the 166-key ledger: 103 DONE step-2 entries, 11 of them
    with no leg-1 artifact under their key (pre-adapter probe and smc-era
    cubes, none a hand completion), and 1 of the 59 free-level-family
    entries without its leg-2 artifact - the hand-completed one."""
    row = entry.get("2_grade_with_config_params")
    if not isinstance(row, dict) or row.get("status") != "DONE":
        return None
    oa = oa if oa is not None else ROOT / "output_audit"
    art = oa / f"{key}_free_levels.json"
    if art.exists():
        return None
    try:
        strat = json.loads((oa / f"{key}_grid_auto.json")
                           .read_text(encoding="utf-8")).get("strategy")
    except (OSError, ValueError):
        return None
    if not strat or not (tools_of or _family_tools)(strat).get("free_levels"):
        return None
    return (f"2_grade_with_config_params [DONE, but leg 2 never ran: "
            f"{art.name} is absent while {strat} declares tools.free_levels "
            "- S6-B3173]")


def completed_cubes() -> list[str]:
    """A cube that exists is a config that finished and owes a ledger entry."""
    out = []
    for d in sorted(ROOT.glob("output_*")):
        if (d / "trade_exit_detail.csv").exists():
            out.append(d.name)
    return out


def leg_keys(ledger: dict, cube: str) -> list:
    """S6-B2918: the ledger keys a PAIRED cube per graded leg
    ("<cube>__<strategy>"), because one directory can carry a long/short
    pair graded one leg at a time. This gate enumerates cubes from the
    FILESYSTEM, so without this it would look up the bare directory name,
    find nothing, report every step missing and exit 2 - blocking the turn
    gate on the owner-mandatory landing path (B2520).

    Returns every leg key present, or the bare cube name when there are
    none - so the 119 of 120 cubes that carry no riders are unaffected."""
    legs = sorted(k for k in ledger
                  if isinstance(k, str) and k.startswith(cube + "__"))
    return legs or [cube]


# ---------------------------------------------------------------------------
# S6-B3156: is a post-config battery RUNNING on a cube right now?
# ---------------------------------------------------------------------------
# The supervisor appends its landing record only at the END of a battery, so
# this gate counted a cube whose battery was still running as owing every step
# and printed its remedy - and that remedy, postconfig_landing.py --cube <dir>
# --force, followed mid-battery started a SECOND battery on the same cube,
# because nothing refused one (found at the b3154 landing, B3139q-r68s).
# Liveness is read from the PROCESS TABLE - the B3099 lesson behind
# pyramid_gate._engine_inflight: a marker or heartbeat says a writer once ran,
# only the table says it runs now - and an unreadable table is 'unknown', which
# every caller treats as possibly running (fail closed). The marker the
# claimant writes supplies only the START TIME, so a hung battery cannot hide
# an incomplete ledger forever.
INFLIGHT_MARKER = "postconfig_inflight.json"
BATTERY_SCRIPTS = ("postconfig_landing.py", "run_postconfig.py")
# CHOSEN, not measured: 2 h. Criterion - more than 5x the longest battery on
# record when the bound was set: 1,296 s across 74 landing events in
# output_audit/postconfig_landings.jsonl (median 32 s, p95 567 s; measured
# 2026-10-13 at B3139q-r68x), rounded up to a whole hour. A live battery older
# than this BLOCKS with an investigate message, never the --force remedy.
INFLIGHT_STALE_S = 2 * 3600
_UNREAD = object()


def _process_rows():
    """(pid, argv) for every running python - pyramid_gate's reader, one
    definition (L593). None when the table cannot be read. The test seam."""
    try:
        import pyramid_gate as _pg
        return _pg._python_argvs()
    except Exception:                               # noqa: BLE001 - fail closed
        return None


def _battery_cube(argv):
    """The cube DIR NAME a python argv runs a battery on, or None. The script
    is found past interpreter options (pyramid_gate._script_index), so `-c`
    code that merely names a battery script is not a run of it (B1603). Both
    `--cube X` and `--cube=X`; a path reduces to its last component, and a
    path naming the cube file itself to its parent - how the supervisor reduces
    it, so every spelling of one cube compares equal."""
    if not argv:
        return None
    try:
        import pyramid_gate as _pg
        si = _pg._script_index(argv)
    except Exception:                               # noqa: BLE001
        return None
    if si is None:
        return None
    if str(argv[si]).replace("\\", "/").rsplit("/", 1)[-1] not in BATTERY_SCRIPTS:
        return None
    rest = [str(x) for x in argv[si + 1:]]
    for j, tok in enumerate(rest):
        if tok == "--cube" and j + 1 < len(rest):
            val = rest[j + 1]
        elif tok.startswith("--cube="):
            val = tok.split("=", 1)[1]
        else:
            continue
        parts = [p for p in val.replace("\\", "/").split("/") if p]
        if not parts:
            return None
        if parts[-1] == "trade_exit_detail.csv" and len(parts) > 1:
            return parts[-2]
        return parts[-1]
    return None


def read_inflight_marker(cube_dir):
    """The claimant's marker, None when absent, {'unreadable': True} when
    present but not a JSON object (it still says a battery once started)."""
    p = pathlib.Path(cube_dir) / INFLIGHT_MARKER
    if not p.is_file():
        return None
    try:
        m = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"unreadable": True}
    return m if isinstance(m, dict) else {"unreadable": True}


def battery_in_flight(cube_dir, *, rows=_UNREAD, now=None, exclude=()) -> dict:
    """Is a post-config battery RUNNING on this cube? Returns {state, pids,
    marker, age_s, why} with state one of:

      live     a python process runs a battery script naming this cube (the
               venv launcher and its interpreter both appear); age_s comes from
               the marker when the marker's pid is one of them, else None
      unknown  the process table is unreadable, or a python whose command line
               cannot be read exists and nothing matched - callers treat it as
               possibly running (fail closed)
      stale    no such process, but a marker remains: a battery started and
               never finished (killed) - NOT running
      none     neither

    `rows` (pass None for an unreadable table), `now` and `exclude` (the
    caller's own pids) are the seams. Never raises."""
    import time as _t
    marker = None
    try:
        cube = pathlib.Path(cube_dir).name
        marker = read_inflight_marker(cube_dir)
        rows = _process_rows() if rows is _UNREAD else rows
        if rows is None:
            return {"state": "unknown", "pids": [], "marker": marker,
                    "age_s": None, "why": "process table unreadable"}
        ex = {int(x) for x in exclude if x}
        pids = sorted({int(pid) for pid, argv in rows
                       if int(pid) not in ex and _battery_cube(argv) == cube})
        if pids:
            age = None
            if marker and marker.get("pid") in pids:
                try:
                    age = ((_t.time() if now is None else now)
                           - float(marker["started"]))
                except (KeyError, TypeError, ValueError):
                    age = None
            return {"state": "live", "pids": pids, "marker": marker,
                    "age_s": age, "why": ""}
        blind = [pid for pid, argv in rows if argv is None and int(pid) not in ex]
        if blind:
            return {"state": "unknown", "pids": [], "marker": marker, "age_s": None,
                    "why": f"python pid {blind[0]} has an unreadable command line"}
        if marker is not None:
            return {"state": "stale", "pids": [], "marker": marker,
                    "age_s": None, "why": "a marker with no running battery"}
        return {"state": "none", "pids": [], "marker": None, "age_s": None,
                "why": ""}
    except Exception as exc:                        # noqa: BLE001 - never raise
        return {"state": "unknown", "pids": [], "marker": marker, "age_s": None,
                "why": f"in-flight check failed: {exc!r}"}


def claim_inflight(cube_dir, *, source: str, fingerprint=None) -> dict:
    """Write THIS process's marker into the cube dir (temp file + os.replace,
    so a reader never sees half a marker) and return it. The supervisor and an
    unsupervised battery claim before the battery starts and release in a
    finally; a kill skips the release, which is why liveness never comes from
    the marker (a killed claimant's marker reads 'stale')."""
    import os
    import time as _t
    m = {"pid": os.getpid(), "started": _t.time(),
         "started_iso": _t.strftime("%Y-%m-%dT%H:%M:%S"),
         "source": source, "fingerprint": fingerprint}
    p = pathlib.Path(cube_dir) / INFLIGHT_MARKER
    tmp = p.with_name(f"{p.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(json.dumps(m, sort_keys=True), encoding="utf-8")
        os.replace(tmp, p)
    except OSError as exc:
        m["write_error"] = repr(exc)
    return m


def release_inflight(cube_dir, claim) -> bool:
    """Remove the marker only while it is still THIS claim's (same pid and
    start) - a later claimant's marker is never deleted. True when removed."""
    if not claim:
        return False
    cur = read_inflight_marker(cube_dir)
    if (not cur or cur.get("pid") != claim.get("pid")
            or cur.get("started") != claim.get("started")):
        return False
    try:
        (pathlib.Path(cube_dir) / INFLIGHT_MARKER).unlink()
        return True
    except OSError:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--only", help="check just this config name")
    a = ap.parse_args()

    if LEDGER.exists():
        try:
            ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"FAIL-CLOSED: ledger unreadable: {exc!r}")
            return 3
    else:
        ledger = {}

    cubes = completed_cubes()
    if a.only:
        cubes = [c for c in cubes if c == a.only]

    incomplete = []
    dir_of = {}
    for c in cubes:
        # S6-B2918: EVERY graded leg of a paired cube must be complete -
        # checking one leg would let the other ship ungraded.
        for k in leg_keys(ledger, c):
            entry = ledger.get(k, {})
            missing = [s for s in STEPS if not is_closed(entry.get(s))]
            gap = leg2_gap(k, entry)
            if gap:
                missing.append(gap)
            if missing:
                incomplete.append((k, missing))
                dir_of[k] = c

    # S6-B3156: a cube whose battery is RUNNING is being dispositioned now -
    # blocking on it forced a wait the turn cannot shorten, and the --force
    # remedy printed for it started a SECOND battery. Live and younger than
    # INFLIGHT_STALE_S -> IN FLIGHT (not blocking); live and older -> HUNG
    # (blocks, investigate, never --force); an unreadable table or a stale
    # marker -> blocks as before, with a note saying which.
    inflight, hung, notes = [], [], {}
    if incomplete:
        rows = _process_rows()
        states: dict = {}
        still = []
        for k, missing in incomplete:
            c = dir_of[k]
            if c not in states:
                states[c] = battery_in_flight(ROOT / c, rows=rows)
            st = states[c]
            if st["state"] == "live":
                age = st.get("age_s")
                if age is not None and age > INFLIGHT_STALE_S:
                    hung.append((k, missing, st))
                else:
                    inflight.append((k, st))
                continue
            if st["state"] == "unknown":
                notes[k] = (f"whether a battery is running on {c} is UNKNOWN "
                            f"({st.get('why')}) - check before re-running it")
            elif st["state"] == "stale":
                mk = st.get("marker") or {}
                notes[k] = (f"a battery started {mk.get('started_iso', '?')} "
                            f"(pid {mk.get('pid', '?')}) is no longer running "
                            "and never finished")
            still.append((k, missing))
        incomplete = still
    live_keys = {k for k, _st in inflight}

    if not a.quiet:
        print("=== POST-CONFIG LEDGER (B1699) ===")
        # B1814b: RUN and SKIPPED are reported SEPARATELY. "9 of 9
        # dispositioned" counted a SKIPPED step toward completion, which is
        # right for the gate's contract and wrong for the question a reader
        # actually asks - "did the analysis RUN?". MEASURED when the owner
        # asked: 4 of 36 step-instances across the sweep configs were SKIPPED,
        # all of them step 6, and nothing in this output said so.
        total_skipped = 0
        for c in [k for c0 in cubes for k in leg_keys(ledger, c0)]:
            e = ledger.get(c, {})
            # S6-B3173: a DONE step 2 whose leg 2 never ran is not a step
            # that RAN, and the mark below must say what the verdict says
            # (S6-B2440 / L558 - a label never contradicts its number).
            gap = leg2_gap(c, e)
            ran = (sum(1 for s in STEPS if e.get(s, {}).get("status") == "DONE")
                   - (1 if gap else 0))
            # S6-B2443: SKIPPED and N/A are DIFFERENT facts and the gate already
            # treats them differently for judgment steps, so the display must
            # not lump them under one word (same label-vs-truth class as the
            # COMPLETE mark above). "deferred" is a promise; "N/A" is a reasoned
            # exclusion.
            skipped = [s for s in STEPS
                       if e.get(s, {}).get("status") == "SKIPPED"]
            na = [s for s in STEPS if e.get(s, {}).get("status") == "N/A"]
            total_skipped += len(skipped)
            # S6-B2440: the mark must agree with the VERDICT. It used to count
            # every SKIPPED toward completion, so this line printed COMPLETE for
            # a config the gate then blocked on three lines later - a reader
            # must never see a label contradicting the number beside it (L558).
            mark = ("COMPLETE" if all(is_closed(e.get(s)) for s in STEPS)
                    and not gap
                    else "IN FLIGHT" if c in live_keys else "INCOMPLETE")
            tail = f"  [{len(skipped)} SKIPPED: {', '.join(skipped)}]" if skipped else ""
            if na:
                tail += f"  [{len(na)} N/A: {', '.join(na)}]"
            print(f"  {mark:10} {c}: {ran} of {len(STEPS)} RUN{tail}")
        print(f"\n  {len(cubes)} cubes | {len(incomplete) + len(hung)} incomplete | "
              f"{total_skipped} step(s) SKIPPED"
              + (f" | {len(inflight)} IN FLIGHT, not blocking (S6-B3156)"
                 if inflight else ""))
        if total_skipped:
            print("  NOTE (B2520): a SKIPPED step satisfies this gate for NO "
                  "step. A deferral is NOT a disposition and BLOCKS - only DONE "
                  "(with evidence) or N/A (with a reason) close a step. Run "
                  "scripts/postconfig_landing.py --cube <dir> --force to record "
                  "every step from the battery.")

    if not a.quiet:
        for k, st in inflight:
            age = st.get("age_s")
            print(f"  IN FLIGHT (S6-B3156) {k}: battery running now (pid "
                  f"{', '.join(str(p) for p in st['pids'])}; age "
                  + ("unknown" if age is None else f"{age:.0f} s")
                  + ") - not blocking; its supervisor is recording these steps "
                  "and appends its landing record when it ends")
    if incomplete:
        print("\nBLOCK: a finished cube owes a complete post-config ledger. "
              "The runbook calls skipping a step a silent miss, so a step with no "
              "entry is not 'pending' - it is missing, and SKIPPED is the same "
              "miss with a label (B2520). Record DONE with evidence, or N/A with "
              "a reason - scripts/postconfig_landing.py --cube <dir> --force "
              "records every step from the battery.")
        for c, missing in incomplete:
            print(f"  {c}: {', '.join(missing)}"
                  + (f"  [S6-B3156: {notes[c]}]" if c in notes else ""))
    if hung:
        print(f"\nBLOCK (S6-B3156): a post-config battery has been RUNNING for "
              f"more than {INFLIGHT_STALE_S // 3600} h - over 5x the longest "
              "battery on record when the bound was set. Investigate that "
              "process; do NOT start a second battery (the supervisor refuses "
              "one while it runs).")
        for k, missing, st in hung:
            print(f"  {k}: pid(s) {', '.join(str(p) for p in st['pids'])} running "
                  f"{st['age_s'] / 3600:.1f} h; open: {', '.join(missing)}")
    return 2 if (incomplete or hung) else 0


if __name__ == "__main__":
    sys.exit(main())

def zero_output_runs(root=None) -> list[str]:
    """Runs that COMPLETED and produced nothing (B1855 / L566).

    The signature of a silently-pruned run, confirmed causally at S6-B1849a:
    demand pruning kept 2 of 33 producers, the screener passed 0/10 on every
    one of 249 days, and the run exited 0 with no error. Same window with
    `DEMAND_PRUNING=0` produced 20 trades and 75 files.

    This is deliberately INDEPENDENT of the post-config ledger. `#223` accepts
    `N/A`, and I dispositioned four probe dirs `N/A` myself for a reason I
    still think correct - which removed the only check positioned to see
    `trades=0`. A detector that a waiver can switch off is not a detector.

    Returns dir names, never raises: a broken probe must not break a caller.
    """
    import json as _json
    import pathlib as _p

    base = _p.Path(root) if root else ROOT
    out = []
    for d in sorted(base.glob("output_*")):
        st = d / "engine_state.json"
        if not st.is_file():
            continue
        try:
            js = _json.loads(st.read_text(encoding="utf-8"))
        except Exception:
            continue
        if js.get("status") != "complete":
            continue                      # still running is not empty
        trades = js.get("trades_so_far")
        if trades is None:
            continue                      # older schema: cannot judge
        if trades == 0 and not (d / "trade_log.csv").is_file():
            out.append(d.name)
    return out
