#!/usr/bin/env python
"""S6-B3395 (B3139q-r178): the Step-2 holdout-read doors' shared checks - ONE
definition for both offline readers, scripts/offline_holdout_read.py (the
depth read) and scripts/breadth_step2_read.py (the breadth read) (L593).

RUNBOOK RULES THIS MODULE MECHANIZES (census S6-B3344, cluster M-HOLD):
  * section 1.1 item 2 and F4 (census line 300): the Step-2 cell is COMMITTED
    before any holdout code path runs - step1_uncommitted refuses a Step-1
    artifact that is untracked, staged but not committed, or modified. The
    ordering IS the pre-registration: a read taken off an uncommitted
    artifact has no commit hash to show the cell preceded the read.
  * section 2.7 row 5 (census line 880): Step 2 refuses an unreconciled
    Step 1 - require_multiplicity, moved here from breadth_step2_read
    (S6-B2836a, B2839) so the depth read runs the check the breadth read
    has run since B2839. breadth_step2_read imports it back, so
    breadth_step2_read.require_multiplicity still resolves.
  * section 0.3 (census line 140) and section 1.1 item 6 (census line 323),
    Batch 7b: ONE owner-worded Step-2 read, a re-read DECLARED, and holdout
    reads COUNTED project-wide - the ledger below (output_audit/
    holdout_reads.jsonl), which both offline readers consult before the read
    and append to when the read is taken.
  * Batch 7c: section 4.4 item 6 (census line 1146) at the engine door -
    run_wave refuses a Step-2 launch that re-reads a recorded config, and the
    battery records each engine grade (engine_launch_refusals, engine_grade);
    the fourth door, scripts/declared_row_holdout_read.py (S6-B3140c), checks
    the owner's word and the ledger; and the frozen census of every
    holdout-touching file, by class (CENSUS_CSV, holdout_touching_files).
  * Batch 7d (owner ruling 2026-11-03 'A approved'): the five campaign
    readers that read holdouts before the ledger are doors too
    (campaign_door, campaign_record) and their past reads are backfilled;
    the R5-era programme scripts and the roster reports stay classed only.

MEASURED before the change (B3139q-r177, scratchpad r177 prereg_all.py):
18 tracked artifacts carry a preregistration_candidate; 6 are unread and
not void; 2 of those 6 lack a multiplicity block, and both are for an
ADMITTED strategy the closed-strategy refusal already refuses - so the
multiplicity door changes the outcome of 0 of the 6 reads still possible.
12 of 12 tracked *_step1_is_surface files were committed and clean.

FAILS CLOSED (L642): git that cannot run, a path outside the repository, a
missing artifact, a ledger line that does not parse - each is a refusal,
never a pass.
"""
from __future__ import annotations

import ast
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The breadth reader's control strategy since B2678 (runbook section 3.5),
# shared with the depth reader's control comparison (S6-B3395, T6).
CONTROL_DEFAULT = "pead_long_high_yoy_growth_only"


def require_multiplicity(art: dict, source: str) -> None:
    """S6-B2836a (B2839): a Step-2 holdout read may only follow a Step-1 whose
    MULTIPLICITY BLOCK RECONCILED. Under the B2836 no-pruning ruling the full
    combination population touches the holdout, so the trials-count honesty
    lives entirely in Step-1's multiplicity instrument - and this reader
    previously never looked (found by the B2836 enforcement-map grep).
    FAIL CLOSED on the absent key (L642: the absent case is the case the
    guard exists for), and on any value other than True.
    """
    mult = art.get("multiplicity")
    if not isinstance(mult, dict) or "reconciles" not in mult:
        raise SystemExit(
            f"REFUSED: {source} carries NO multiplicity block - Step-1 must "
            "run the runbook section 1.4 multiplicity instrument before any holdout read "
            "(S6-B2836a; fail closed on absence)")
    if mult.get("reconciles") is not True:
        raise SystemExit(
            f"REFUSED: {source} multiplicity.reconciles = "
            f"{mult.get('reconciles')!r} - a non-reconciled Step-1 cannot "
            "feed a holdout read (S6-B2836a)")


def step1_uncommitted(path, *, root=None) -> str | None:
    """None when `path` is a Step-1 artifact that is tracked and clean in the
    repository; otherwise the refusal naming what is wrong.

    A staged-but-uncommitted new file is in git's index, so `ls-files` alone
    would pass it; `status --porcelain` shows it as 'A ', which refuses - the
    rule asks for a COMMIT, not a stage. `root` is the repository to check
    (the module's own repository unless a caller names another)."""
    rootp = Path(root or ROOT).resolve()
    p = Path(path)
    if not p.is_absolute():
        p = rootp / p
    try:
        rel = p.resolve().relative_to(rootp).as_posix()
    except ValueError:
        return (f"REFUSED (S6-B3395, runbook 1.1 item 2 / F4): {path} is outside "
                "the repository, so it cannot be committed - a holdout read rests "
                "on a Step-1 artifact committed BEFORE any holdout code path runs")
    if not p.exists():
        return f"REFUSED (S6-B3395): the Step-1 artifact {path} does not exist"
    try:
        tracked = subprocess.run(
            ["git", "-C", str(rootp), "ls-files", "--error-unmatch", "--", rel],
            capture_output=True, text=True, timeout=30)
        status = subprocess.run(
            ["git", "-C", str(rootp), "status", "--porcelain", "--", rel],
            capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return (f"REFUSED (S6-B3395): git could not be run ({type(exc).__name__}) "
                "- the committed-artifact check fails closed (L642)")
    if tracked.returncode != 0:
        return (f"REFUSED (S6-B3395, runbook 1.1 item 2 / F4): {rel} is not tracked "
                "- commit the Step-1 artifact BEFORE any holdout code path runs; "
                "the commit is the pre-registration")
    if status.returncode != 0 or status.stdout.strip():
        return (f"REFUSED (S6-B3395, runbook 1.1 item 2 / F4): {rel} has uncommitted "
                f"changes ({status.stdout.strip()[:40]!r}) - the cell a read admits on "
                "must be the committed one")
    return None


# ---------------------------------------------------------------------------
# THE HOLDOUT-READ LEDGER (S6-B3395 Batch 7b; runbook 0.3, 1.1 item 6, 4.4
# item 6). Owner ruling 2026-11-03, verbatim 'A approved': option (a) - the
# reads are counted at the Step-2 doors, the recorded reads are backfilled,
# and a frozen list of every file that touches holdout performance makes a
# new one fail until it is classed (the list is Batch 7c).
#
# WHY A LEDGER, MEASURED (B3139q-r177): the owner's word is not one-shot
# (owner_word.refusals passes whenever a row quotes the words), the depth
# read refused a re-read only at its own --out, and the breadth read
# overwrote --out and took --prior-read on the caller's word - so
# output_audit/b2646_pead_step2_postfix.json re-read the pead surface with no
# machine-readable label (S6-B2644c's row records it in prose only).
#
# THE SUBJECT. Offline doors: one read per (strategy, leg) - a later read of
# the same subject is a RE-READ, DECLARED by naming the read it repeats.
# Both doors share the subject, because a breadth read after the depth
# verdict is 'a read of their own, labelled DISCLOSED-RE-READ when the
# subject's holdout was already read' (runbook 0.1, BREADTH IS STEP 3). The
# engine door: one read per (strategy, leg, config) - the waterfall spends
# one read per slate config BY RULING (runbook 1.1 item 1), so the next
# config is a new read, counted not refused, while a renamed wave of the
# SAME config is a re-read. A leg of None or 'both' overlaps every leg.
#
# THE ENGINE CONFIG IS THE ARM'S ENV (engine_identity) - what the engine ran
# with, the same dict in the spec at launch and in the landed manifest at
# grading: MEASURED equal on 7 of 7 recorded engine reads (B3139q-r179,
# scratchpad r178/manifest_env_probe.py). The grader's own config dict rides
# beside it as grid_config and is never matched on: the battery's generic
# derivation reproduces it from a spec for 3 of the 7 (icg names P9_span,
# pairs adds an identity label, LEVER4 nests the budget by strategy), so a
# launch could not compute it. A support variable in the env (EMA_PAIRS)
# is part of the identity - a re-read whose support env changed reads as a
# new config, the one way this key can under-refuse.
#
# A READ IS RECORDED WHEN IT IS TAKEN - right after the holdout rows are
# computed, before the artifact is written - so a crash between the two
# over-counts, the conservative direction. The control comparison's look at
# the CONTROL's holdout is not a read of the control's campaign (a baseline,
# never a re-test - S6-B3139g); each read's artifact names its control and
# that comparison's status, so those looks are counted from the artifacts.
# ---------------------------------------------------------------------------
LEDGER_PROD = ROOT / "output_audit" / "holdout_reads.jsonl"
ENV_KEY = "HOLDOUT_READS_LEDGER"
# Batch 7d (owner ruling 2026-11-03 'A approved'): the five campaign readers
# that read holdouts before the ledger existed are doors now, each by name
CAMPAIGN_DOORS = ("b2701_smc_lsr_step2", "composite_variant_test",
                  "grade_family_siblings", "institutional_companion_grid",
                  "family_pregate")
DOORS = ("offline_holdout_read", "breadth_step2_read", "engine_step2",
         "declared_row_holdout_read") + CAMPAIGN_DOORS


def ledger_path() -> Path:
    """The production ledger - except inside a pytest run, where the test
    conftest points ENV_KEY at a per-test temp file. The override is honoured
    ONLY while PYTEST_CURRENT_TEST is set, so a production read can never
    point the evidence this gate reads at another file (L596: an escape gets
    the stricter matcher); every subprocess a test starts inherits both."""
    alt = os.environ.get(ENV_KEY)
    if alt and os.environ.get("PYTEST_CURRENT_TEST"):
        return Path(alt)
    return LEDGER_PROD


def entries(path=None) -> list:
    """Every recorded read in file order. An absent ledger is empty; a line
    that does not parse, or names no strategy or read_id, REFUSES - an
    unreadable ledger is not an empty one (L580)."""
    p = Path(path) if path else ledger_path()
    if not p.exists():
        return []
    out = []
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except ValueError:
            raise SystemExit(f"REFUSED (S6-B3395): {p} line {n} is not JSON - an "
                             "unreadable read ledger is not an empty one (L580)") from None
        if not isinstance(e, dict) or not e.get("strategy") or not e.get("read_id"):
            raise SystemExit(f"REFUSED (S6-B3395): {p} line {n} names no strategy or "
                             "read_id - fail closed (L642)")
        out.append(e)
    return out


def _legs_overlap(a, b) -> bool:
    a, b = str(a or "both").lower(), str(b or "both").lower()
    return a == "both" or b == "both" or a == b


def config_identity(config) -> str | None:
    """A config dict as its key-sorted JSON - a wave's NAME is never part of
    it, so a renamed wave of one config is one subject."""
    if config is None:
        return None
    return json.dumps(config, sort_keys=True, separators=(",", ":"))


def engine_identity(env) -> str:
    """The engine door's config key: the arm's env (spec arms[N].env at launch,
    the landed manifest's arms[0].env at grading), key-sorted. An arm with no
    env - a production config - is the empty dict, itself an identity."""
    return config_identity({str(k): str(v) for k, v in dict(env or {}).items()})


def prior_reads(strategy, leg=None, *, config=None, path=None) -> list:
    """The recorded reads of this subject. config=None (the offline doors) sees
    every read of the strategy on an overlapping leg; a config identity (the
    engine door) sees only that config's reads."""
    found = []
    for e in entries(path):
        if e.get("strategy") != strategy or not _legs_overlap(e.get("leg"), leg):
            continue
        if config is not None and e.get("config") != config:
            continue
        found.append(e)
    return found


def reread_refusal(strategy, leg=None, *, declared=None, config=None, door,
                   path=None) -> str | None:
    """None when this read may proceed: no prior read of the subject and no
    declaration, or a DECLARED re-read naming one of the recorded reads.
    Otherwise the refusal. A read whose subject names no strategy refuses -
    it could not be counted (L642)."""
    if not strategy:
        return (f"REFUSED ({door}, S6-B3395): the Step-1 artifact names no strategy, "
                "so the read cannot be counted against the holdout-read ledger")
    prior = prior_reads(strategy, leg, config=config, path=path)
    ids = [e["read_id"] for e in prior]
    subj = f"{strategy} ({leg or 'both legs'}" + (f", config {config}" if config else "") + ")"
    if declared:
        if declared in ids:
            return None
        return (f"REFUSED ({door}, S6-B3395): the declared re-read {declared!r} is not a "
                f"recorded read of {subj}; the ledger records {ids}")
    if not prior:
        return None
    return (f"REFUSED ({door}, S6-B3395, runbook 0.3 / 4.4 item 6): the ledger records "
            f"{len(prior)} holdout read(s) of {subj}: {ids[:4]} - one Step-2 read, then "
            "the campaign closes; a re-read is DECLARED, naming the read it repeats, on "
            "the owner's word")


def read_id_refusal(read_id, *, door, path=None) -> str | None:
    """A read's id is its artifact's path, so it is recorded once: an --out
    that already names a recorded read is that read's record, and a re-read
    writes a NEW artifact (declaring the old one)."""
    taken = [e for e in entries(path) if e.get("read_id") == str(read_id)]
    if not taken:
        return None
    return (f"REFUSED ({door}, S6-B3395): {read_id} is already the artifact of a "
            f"recorded holdout read ({taken[0].get('ts')}) - the artifact of a read is "
            "its record; a re-read writes a new --out and declares the read it repeats")


def _dominant_end(path: Path) -> str:
    """The line ending the file already uses most (L850) - the rule of
    postconfig_landing._row_end, which is bound to the queue path. chr() form
    for the reason that helper records: escapes do not survive a heredoc."""
    try:
        raw = path.read_bytes()
    except OSError:
        return chr(10)
    crlf = raw.count(bytes([13, 10]))
    return chr(13) + chr(10) if crlf * 2 > raw.count(bytes([10])) else chr(10)


def record(*, read_id, strategy, leg, door, artifact, source, owner_word=None,
           rereads=(), config=None, ts=None, backfilled=False, declared=None,
           grid_config=None, path=None) -> dict:
    """Append one read to the ledger and return the entry. Refuses an unknown
    door, a read with no strategy, and an engine read with no config identity
    - the ledger never holds an entry its own reader would refuse or could not
    match. `declared` says whether the read carried a re-read declaration:
    True or False for a read with one or without one, None for a first read
    with none. `grid_config` (engine reads) is the grader's own config dict,
    recorded for the reader of the ledger and never matched on."""
    if door not in DOORS:
        raise SystemExit(f"REFUSED (S6-B3395): unknown door {door!r} - one of {DOORS}")
    if not strategy or not read_id:
        raise SystemExit("REFUSED (S6-B3395): a read names its strategy and read_id")
    if door == "engine_step2" and config is None:
        raise SystemExit("REFUSED (S6-B3395): an engine read names its config identity "
                         "(engine_identity of the arm's env)")
    entry = {"read_id": str(read_id), "strategy": strategy, "leg": leg or "both",
             "door": door, "config": config, "grid_config": grid_config,
             "artifact": str(artifact),
             "source": None if source is None else str(source),
             "owner_word": owner_word, "rereads": list(rereads),
             "ts": ts or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "backfilled": bool(backfilled), "declared": declared}
    p = Path(path) if path else ledger_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    end = _dominant_end(p)
    with open(p, "ab") as fh:
        fh.write((json.dumps(entry, sort_keys=True) + end).encode("utf-8"))
    return entry


def repo_rel(path) -> str:
    """A repository-relative, forward-slash form of a path - the read_id and
    the backfill both use it, so one read carries one id. A path outside the
    repository keeps its absolute form."""
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    try:
        return p.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


# ---------------------------------------------------------------------------
# THE ENGINE DOOR (S6-B3395 Batch 7c; runbook 4.4 item 6, census line 1146),
# two halves on one identity, engine_identity of the arm's env:
#   * AT LAUNCH, run_wave refuses a Step-2 spec whose arm would re-read a
#     (strategy, config) the ledger records, unless the arm DECLARES the
#     recorded read it repeats (REREADS_ARM_KEY) - before anything is archived
#     or written, beside the B3104 guard, which keys on the wave's own summary
#     and so passed a RENAMED wave of a config already read.
#   * AT GRADING, the battery (run_postconfig.run_family, step 2) records the
#     read its grader took - once per grid artifact, so re-running the battery
#     on one landing re-grades the same read - and an undeclared re-read that
#     reached grading (a launch outside run_wave) fails step 2 closed.
# A launch knows no leg (the graders set it), so it checks every leg - the
# refusing direction; the grading records the grader's leg.
# ---------------------------------------------------------------------------
REREADS_ARM_KEY = "holdout_rereads"


def arm_rereads(arm) -> list:
    """The recorded reads an arm declares it repeats - one read_id or a list."""
    v = arm.get(REREADS_ARM_KEY) if isinstance(arm, dict) else None
    if v is None:
        return []
    return [str(x) for x in (v if isinstance(v, (list, tuple)) else [v]) if str(x).strip()]


def engine_launch_refusals(spec, strategies, *, path=None) -> list:
    """run_wave's half, for a Step-2 spec ("step": 2): a refusal per (arm,
    strategy) whose arm env the ledger already records with no declaration
    naming one of those reads, and per declared id that is no recorded read.
    [] for any other spec, and for an empty strategy list - launch_refusals,
    which runs next, refuses a subset that names none."""
    if not isinstance(spec, dict) or spec.get("step") != 2:
        return []
    known = {e["read_id"] for e in entries(path)}
    errs = []
    for arm in spec.get("arms") or []:
        if not isinstance(arm, dict):
            continue
        tag, declared = arm.get("tag"), arm_rereads(arm)
        errs += [f"REFUSED (engine_step2, S6-B3395): arm {tag!r} declares "
                 f"{REREADS_ARM_KEY} {d!r}, which is not a recorded read"
                 for d in declared if d not in known]
        config = engine_identity(arm.get("env"))
        for s in strategies:
            ids = [e["read_id"] for e in prior_reads(s, None, config=config, path=path)]
            if ids and not set(ids) & set(declared):
                errs.append(f"arm {tag!r}: " + reread_refusal(
                    s, None, config=config, door="engine_step2", path=path)
                    + f" (name it in the arm's {REREADS_ARM_KEY})")
    return errs


def engine_grade(grid_path, grid, arm, *, strategy=None, owner_word=None,
                 path=None) -> tuple:
    """The battery's half: record the read a Step-2 grader took. Returns
    (refusal or None, evidence). `strategy` is the strategy the battery
    graded (run_family's family); the grid's own `strategy`, when present,
    must agree - a disagreement refuses, and with neither the read is
    refused, never recorded under a guess (L642). A grid already recorded is
    a re-grade of the same read and appends nothing. A read of a recorded
    (strategy, leg, arm env) with no declaration naming one of those reads is
    recorded declared=False and returned as the refusal - the run passed no
    launch door and its verdict is not admissible."""
    read_id = repo_rel(grid_path)
    if any(e.get("read_id") == read_id for e in entries(path)):
        return None, f"{read_id} already recorded - a re-grade of the same read"
    grid = grid if isinstance(grid, dict) else {}
    s2 = grid.get("step2") if isinstance(grid.get("step2"), dict) else {}
    own = grid.get("strategy")
    if strategy and own and own != strategy:
        return (f"REFUSED (engine_step2, S6-B3395): the grid grades {own!r} while the "
                f"battery graded {strategy!r} - the read cannot be attributed"), ""
    strategy, leg = strategy or own, s2.get("leg")
    if not strategy:
        return ("REFUSED (engine_step2, S6-B3395): neither the battery nor the grid "
                "names the strategy, so the read cannot be counted"), ""
    config = engine_identity((arm or {}).get("env") if isinstance(arm, dict) else None)
    prior = [e["read_id"] for e in prior_reads(strategy, leg, config=config, path=path)]
    named = [d for d in arm_rereads(arm) if d in prior]
    why = (reread_refusal(strategy, leg, config=config, door="engine_step2", path=path)
           if prior and not named else None)
    cube = grid.get("cube")
    record(read_id=read_id, strategy=strategy, leg=leg, door="engine_step2",
           artifact=read_id, source=repo_rel(cube) if cube else None,
           owner_word=owner_word, rereads=prior, config=config,
           grid_config=grid.get("config"),
           declared=(bool(named) if prior else None), path=path)
    return why, (f"{read_id} recorded in the holdout-read ledger; earlier reads of "
                 f"this config: {prior or 'none'}")


# ---------------------------------------------------------------------------
# THE CAMPAIGN DOORS (S6-B3395 Batch 7d; owner ruling 2026-11-03, verbatim
# 'A approved'). Five readers graded campaigns' holdouts before the ledger
# existed - b2701_smc_lsr_step2, composite_variant_test, grade_family_siblings,
# institutional_companion_grid, family_pregate - and a re-run of any of them is
# a campaign re-read. Each now calls campaign_door before it touches a holdout
# (the owner's word checked against its ledger row; --out new; every strategy
# it will read either unread in the ledger or DECLARED re-read by --rereads)
# and campaign_record once the read is taken. A multi-strategy read records
# one entry per strategy, read_id '<artifact>#<strategy>'; a declaration naming
# an artifact names every per-strategy read of it. The R5-era programme
# scripts and the roster reports stay classed only (the same ruling).
# ---------------------------------------------------------------------------
def campaign_read_id(artifact, strategy) -> str:
    return f"{repo_rel(artifact)}#{strategy}"


def _names(declared, read_id) -> bool:
    return read_id == declared or read_id.startswith(str(declared) + "#")


def campaign_door(door, strategies, *, out, ruling, ruling_ticket, rereads=(),
                  path=None) -> dict:
    """The gate a campaign reader passes BEFORE its holdout read. Raises
    SystemExit with the first refusal; returns {'word', 'prior'} - prior being
    each strategy's recorded reads, the history its record carries."""
    import owner_word
    if door not in CAMPAIGN_DOORS:
        raise SystemExit(f"REFUSED (S6-B3395): {door!r} is not a campaign door")
    word = {"ticket": str(ruling_ticket or "").strip(),
            "verbatim": owner_word.normalise(ruling)}
    errs = owner_word.refusals(word, door=f"{door} holdout read")
    if errs:
        raise SystemExit(errs[0])
    if not strategies:
        raise SystemExit(f"REFUSED ({door}, S6-B3395): no strategy named, so the "
                         "read cannot be counted")
    if Path(out).exists():
        raise SystemExit(f"REFUSED ({door}, S6-B3395): {out} exists - the artifact of "
                         "a holdout read is its record; a re-read writes a new --out "
                         "and declares the read it repeats with --rereads")
    known = [e["read_id"] for e in entries(path)]
    for d in rereads:
        if not any(_names(d, r) for r in known):
            raise SystemExit(f"REFUSED ({door}, S6-B3395): --rereads {d!r} names no "
                             "recorded holdout read")
    prior = {}
    for s in strategies:
        ids = [e["read_id"] for e in prior_reads(s, None, path=path)]
        if ids and not any(_names(d, r) for d in rereads for r in ids):
            raise SystemExit(reread_refusal(s, None, door=door, path=path)
                             + " (declare it with --rereads)")
        prior[s] = ids
    return {"word": word, "prior": prior}


def campaign_record(door, artifact_doc, *, out, word, prior, rereads=(),
                    path=None) -> list:
    """Record the read once it is TAKEN: one entry per strategy the artifact
    about to be written actually read (_campaign_shape of that same dict, the
    backfill's own definition, so live and backfilled entries agree). Returns
    the read ids recorded."""
    shape = _campaign_shape(artifact_doc)
    if shape is None or shape[0] != door:
        raise SystemExit(f"REFUSED ({door}, S6-B3395): the artifact is not this "
                         "door's shape, so its read cannot be counted")
    ids = []
    for s in shape[1]:
        named = [r for r in (prior or {}).get(s, [])
                 if any(_names(d, r) for d in rereads)]
        e = record(read_id=campaign_read_id(out, s), strategy=s, leg=None, door=door,
                   artifact=repo_rel(out), source=None, owner_word=word,
                   rereads=named, declared=True if named else None, path=path)
        ids.append(e["read_id"])
    return ids


def _campaign_shape(d):
    """(door, the strategies whose holdout it read) for an artifact one of the
    five campaign readers wrote, else None - each recognised by its own
    top-level keys. Measured B3139q-r181: 7 tracked artifacts, 75 strategy
    reads, none matching two shapes."""
    if not isinstance(d, dict):
        return None
    if "admission_bearing" in d and "peeked_lines" in d and d.get("strategy"):
        return "b2701_smc_lsr_step2", [d["strategy"]]
    if "variants" in d and "v1_v2_identity" in d:
        return "composite_variant_test", sorted({r["strategy"] for r in d.get("rows") or []})
    if isinstance(d.get("siblings"), dict) and "prereg" in d:
        return "grade_family_siblings", sorted(
            s for s, r in d["siblings"].items() if isinstance(r, dict) and "holdout_n" in r)
    if "family" in d and "trials_total" in d and "rows" in d:
        # a live run names every strategy it processed (strategies_read); an
        # artifact written before 7d names those with a graded row or a skip
        if d.get("strategies_read"):
            return "institutional_companion_grid", sorted(d["strategies_read"])
        return "institutional_companion_grid", sorted(
            {r["strategy"] for r in d.get("rows") or []}
            | {s["strategy"] for s in d.get("skipped_axis_strategy_pairs") or []})
    if isinstance(d.get("members"), dict) and "overlap" in d and "cube" in d:
        return "family_pregate", sorted(
            s for s, r in d["members"].items()
            if isinstance(r, dict) and "holdout_gradable_exits" in r)
    return None


# ---------------------------------------------------------------------------
# THE FROZEN CENSUS (S6-B3395 Batch 7c, the owner's option (a)): every non-test
# .py under scripts/ and backtest/ that touches holdout performance - calls a
# function or method named holdout, names the HO_START / HO_END bounds, or
# carries the holdout start date outside a docstring - is listed with its class
# in CENSUS_CSV, and test_b3395c fails while the scan and the list differ: a new
# file is classed - a door that counts its reads, or the reason it needs none -
# before it lands. 50 files at B3139q-r180 - the 50th is this module's own
# date constant (the 7c comment said 49, written before that constant landed).
# ---------------------------------------------------------------------------
CENSUS_CSV = ROOT / "output_audit" / "holdout_touching_files.csv"
HO_DATE_LITERAL = "2025-05-05"
CENSUS_CLASSES = {
    "LEDGER_DOOR": "consults and appends to the holdout-read ledger",
    "ENGINE_GRADER": "a battery grade script; run_postconfig records its read",
    "READ_COMPANION": "runs inside a counted read, on that read's own rows",
    "REPRODUCTION": "re-derives a recorded read's own numbers; refuses on a mismatch",
    "ROSTER_REPORT": "re-grades admitted or R5-funnel lines whose reads are spent",
    "R5_PROGRAMME": "R5/R6-era programme analysis of the R5 cube's holdout "
                    "(runbook 1.1 item 6's prior spends)",
    "COUNT_ONLY": "counts trades in the holdout window; computes no performance",
    "IN_SAMPLE_ONLY": "uses the boundary to stay inside the in-sample window",
    "WINDOW_DEFINITION": "defines or checks the window; reads no performance",
}


def _census_hits(tree) -> set:
    docs = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if (n.body and isinstance(n.body[0], ast.Expr)
                    and isinstance(n.body[0].value, ast.Constant)):
                docs.add(id(n.body[0].value))
    hits = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and (
                (isinstance(n.func, ast.Name) and n.func.id == "holdout")
                or (isinstance(n.func, ast.Attribute) and n.func.attr == "holdout")):
            hits.add("call")
        elif ((isinstance(n, ast.Name) and n.id in ("HO_START", "HO_END"))
              or (isinstance(n, ast.Attribute) and n.attr in ("HO_START", "HO_END"))):
            hits.add("bound")
        elif (isinstance(n, ast.Constant) and isinstance(n.value, str)
              and HO_DATE_LITERAL in n.value and id(n) not in docs):
            hits.add("literal")
    return hits


def holdout_touching_files(root=None) -> dict:
    """{repo-relative path: sorted hit kinds} over every non-test .py under
    scripts/ and backtest/. A file that does not parse is listed as
    'unparseable' - never silently skipped (L642)."""
    rootp = Path(root or ROOT)
    out = {}
    for d in ("scripts", "backtest"):
        for p in sorted((rootp / d).rglob("*.py")):
            if "tests" in p.parts or "__pycache__" in p.parts:
                continue
            try:
                tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                out[p.relative_to(rootp).as_posix()] = ["unparseable"]
                continue
            hits = _census_hits(tree)
            if hits:
                out[p.relative_to(rootp).as_posix()] = sorted(hits)
    return out


def census_rows(path=None) -> dict:
    """{path: row} from CENSUS_CSV; a row whose class is not a CENSUS_CLASSES
    key, or a duplicate path, refuses."""
    import csv
    p = Path(path) if path else CENSUS_CSV
    rows = {}
    with open(p, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r.get("class") not in CENSUS_CLASSES:
                raise SystemExit(f"REFUSED (S6-B3395): {p} classes {r.get('path')} as "
                                 f"{r.get('class')!r}, not one of {sorted(CENSUS_CLASSES)}")
            if r["path"] in rows:
                raise SystemExit(f"REFUSED (S6-B3395): {p} lists {r['path']} twice")
            rows[r["path"]] = r
    return rows


# ---------------------------------------------------------------------------
# BACKFILL - the reads taken before the ledger existed, read off the tracked
# artifacts they left (B3139q-r177 measured 23: 9 depth, 7 breadth, 7 engine).
# Three artifact shapes were recognised at 7b; Batch 7c added the fourth, the
# declared-row read (S6-B3140c), whose one tracked read predates two committed
# pairs entries - so a recognised shape can LENGTHEN an earlier entry's
# derivable history, and an entry keeps what was known when it was written
# (test_b3395b requires its rereads to be a subset of what git derives now).
# Batch 7d added the five campaign readers' shapes (_campaign_shape: 7 tracked
# artifacts, 75 strategy reads, one entry per strategy). A later-recognised read
# can also make a recorded FIRST read a re-read: the b2633 family pre-gate read
# pead_with_smart_money_long's holdout before the b2651 Step-2 read did, so
# b2651 derives declared False where the ledger recorded None - the one change
# test_b3395b accepts beside a longer rereads list. Within one commit git
# cannot order two reads; the read_id order decides, a stated tie-break.
# Each is dated by the commit that first added its artifact, so the order is
# reproducible from git alone; a re-read is marked by whether its artifact
# carried a re-read label (the depth read's rerun_of_spent_holdout, the
# breadth read's DISCLOSED-RE-READ provenance), so b2646's unlabelled re-read
# is recorded as the fact it is.
# ---------------------------------------------------------------------------
def _first_added(relpath: str, root: Path) -> str:
    r = subprocess.run(["git", "-C", str(root), "log", "--diff-filter=A",
                        "--format=%cI", "--", relpath],
                       capture_output=True, text=True, timeout=60)
    lines = [x for x in r.stdout.splitlines() if x.strip()]
    if r.returncode != 0 or not lines:
        raise SystemExit(f"REFUSED (S6-B3395): no first-add commit for {relpath} - "
                         "a backfilled read is dated by git or not at all")
    stamp = datetime.fromisoformat(lines[-1])
    return stamp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tracked_spec_envs(rootp: Path) -> dict:
    """{cube dir name: {engine_identity, ...}} over the tracked wave specs - a
    wave's arm lands in output_<wave>_<tag>, so each landed cube names the
    spec arm that launched it."""
    ls = subprocess.run(["git", "-C", str(rootp), "ls-files", "output_audit/*_spec.json"],
                        capture_output=True, text=True, timeout=60)
    if ls.returncode != 0:
        raise SystemExit("REFUSED (S6-B3395): git ls-files failed - fail closed")
    out: dict = {}
    for relpath in [x for x in ls.stdout.splitlines() if x.strip()]:
        try:
            s = json.loads((rootp / relpath).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(s, dict) or "wave" not in s:
            continue
        for arm in s.get("arms") or []:
            if isinstance(arm, dict):
                out.setdefault(f"output_{s['wave']}_{arm.get('tag')}", set()).add(
                    engine_identity(arm.get("env")))
    return out


def _engine_config(relpath: str, cube, spec_envs: dict) -> str:
    """The engine read's identity from the tracked spec arm that produced its
    cube; no spec, or specs disagreeing on the env, REFUSES (L642)."""
    hit = next((p for p in Path(str(cube or "")).parts if p in spec_envs), None)
    ids = spec_envs.get(hit) or set()
    if len(ids) != 1:
        raise SystemExit(f"REFUSED (S6-B3395): {relpath}'s cube {cube!r} maps to "
                         f"{len(ids)} tracked spec env(s) - an engine read is "
                         "identified by the arm that launched it, or not at all")
    return next(iter(ids))


def backfill_candidates(root=None) -> list:
    """The ledger entries the tracked read artifacts imply, oldest first -
    what test_b3395b compares the committed ledger's backfilled entries with."""
    rootp = Path(root or ROOT)
    ls = subprocess.run(["git", "-C", str(rootp), "ls-files", "output_audit/*.json"],
                        capture_output=True, text=True, timeout=60)
    if ls.returncode != 0:
        raise SystemExit("REFUSED (S6-B3395): git ls-files failed - fail closed")
    spec_envs = _tracked_spec_envs(rootp)
    found = []
    for relpath in [x for x in ls.stdout.splitlines() if x.strip()]:
        try:
            d = json.loads((rootp / relpath).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        camp = _campaign_shape(d)
        if camp is not None:
            ts = _first_added(relpath, rootp)
            hrl = d.get("holdout_read_ledger") if isinstance(d.get("holdout_read_ledger"), dict) else {}
            prov = d.get("provenance") if isinstance(d.get("provenance"), list) else []
            label = bool(hrl.get("rereads")) or any(
                str(p).startswith("DISCLOSED-RE-READ") for p in prov)
            for s in camp[1]:
                found.append({"read_id": f"{relpath}#{s}", "strategy": s, "leg": None,
                              "door": camp[0], "config": None, "artifact": relpath,
                              "grid_config": None, "source": None,
                              "owner_word": d.get("owner_word"), "ts": ts,
                              "declared": label})
            continue
        if not isinstance(d, dict) or not d.get("strategy"):
            continue
        s2 = d.get("step2") if isinstance(d.get("step2"), dict) else {}
        if d.get("step") == 2 and "sweep_artifact" in d:
            door, leg = "offline_holdout_read", (d.get("subject") or {}).get("direction")
            source, config = d["sweep_artifact"], None
            declared = d.get("rerun_of_spent_holdout") is True
        elif "ruling_verbatim" in d and "step1_artifact" in d:
            door, leg = "breadth_step2_read", d.get("leg")
            source, config = d["step1_artifact"], None
            declared = str((d.get("provenance") or {}).get("label", "")).startswith(
                "DISCLOSED-RE-READ")
        elif s2.get("holdout_read") is True:
            door, leg = "engine_step2", s2.get("leg")
            source = d.get("cube")
            config = _engine_config(relpath, source, spec_envs)
            declared = None
        elif "free_levels_artifact" in d and "declared_exit" in d:
            door, leg = "declared_row_holdout_read", None
            source, config = d.get("cube"), None
            declared = (d.get("holdout_read_ledger") or {}).get("rereads") not in (None, [])
        else:
            continue
        found.append({"read_id": relpath, "strategy": d["strategy"], "leg": leg,
                      "door": door, "config": config, "artifact": relpath,
                      "grid_config": d.get("config") if door == "engine_step2" else None,
                      "source": repo_rel(source) if source else None,
                      "owner_word": d.get("owner_word"),
                      "ts": _first_added(relpath, rootp),
                      "declared": declared})
    found.sort(key=lambda e: (e["ts"], e["read_id"]))
    for i, e in enumerate(found):
        e["rereads"] = [p["read_id"] for p in found[:i]
                        if p["strategy"] == e["strategy"]
                        and _legs_overlap(p["leg"], e["leg"])
                        and (e["door"] != "engine_step2" or p.get("config") == e["config"])]
        if not e["rereads"] and not e["declared"]:
            e["declared"] = None
    return found


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="S6-B3395: the holdout-read ledger")
    ap.add_argument("--backfill", action="store_true",
                    help="list the reads the tracked artifacts imply (dry unless --write)")
    ap.add_argument("--write", action="store_true",
                    help="with --backfill: append the entries not already recorded")
    ap.add_argument("--list", action="store_true", help="print the recorded reads")
    a = ap.parse_args(argv)
    if a.list:
        for e in entries():
            print(f"{e['ts']}  {e['door']:<22} {e['strategy']} ({e.get('leg')}) "
                  f"{e['read_id']}  rereads={e.get('rereads')}")
        return 0
    if not a.backfill:
        ap.print_help()
        return 2
    cands = backfill_candidates()
    have = {(e["read_id"], e["door"]) for e in entries()}
    new = [c for c in cands if (c["read_id"], c["door"]) not in have]
    by_door = {}
    for c in cands:
        by_door[c["door"]] = by_door.get(c["door"], 0) + 1
    print(f"recorded reads the tracked artifacts imply: {len(cands)} {by_door}; "
          f"already in the ledger: {len(cands) - len(new)}; to append: {len(new)}")
    for c in cands:
        mark = "re-read" if c["rereads"] else "first"
        lab = "" if c["declared"] is None else (" DECLARED" if c["declared"] else
                                                " UNDECLARED")
        print(f"  {c['ts']}  {c['door']:<22} {c['strategy']} ({c['leg'] or 'both'})"
              f"  {mark}{lab}  {c['read_id']}")
    if a.write:
        for c in new:
            record(read_id=c["read_id"], strategy=c["strategy"], leg=c["leg"],
                   door=c["door"], artifact=c["artifact"], source=c["source"],
                   owner_word=c["owner_word"], rereads=c["rereads"],
                   config=c["config"], ts=c["ts"], backfilled=True,
                   declared=c["declared"], grid_config=c["grid_config"])
        print(f"appended {len(new)} to {ledger_path()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
