"""S6-B3102a (B3104): the identity of a wave RUN, and the chain's
launch / skip / halt decision, in ONE place (L561: one pattern, one
definition - run_serial_chain decides with it, run_wave records with it).

THE DEFECT. run_serial_chain keyed its idempotent-restart SKIP on the wave
NAME: an existing <wave>_wave_summary.json reading COMPLETE -> SKIP, any other
status -> HALT. MEASURED 2026-09-24 on the c14 Step-1 re-run - an
owner-approved same-name re-run on a fixed engine - the chain would have
logged SKIP and ended "CHAIN DONE - every spec COMPLETE" having run nothing;
the old summary was archived by hand to get it launched. The discarded
Step-2 wave's GATE_REFUSED summary would HALT its restart the same way.

WHY A SPEC HASH ALONE IS NOT THE FIX (council B3104, 5 advisors).
  * Spec files are edited IN PLACE after runs: the b3089 Step-2 spec now
    differs from the copy its own summary embeds by two note fields AND
    allow_engine_drift. Launching whenever the spec differs (option A, 5 of 5
    against) would re-read a Step-2 holdout over a notes edit, unattended.
  * A deliberate re-run on a fixed engine needs NO spec change, so a hash
    comparison alone still SKIPs it silently - the original defect (the
    Contrarian and First Principles advisors).
  Intent cannot be inferred from content in either direction; it is DECLARED.

THE RULE - decide(), in order:
  1. no summary on disk                                  -> LAUNCH
  2. unreadable summary                                  -> HALT
  3. written by THIS chain run and the same identity:
       COMPLETE -> SKIP (the reboot restart the SKIP exists for);
       any other status -> HALT (no automatic relaunch after a failure)
  4. spec["supersedes_summary"] == that summary's identity -> LAUNCH
       (a DECLARED re-run; run_wave archives the old summary and the new
       one records the lineage)
  5. written by THIS chain run, identity changed         -> HALT (the spec
       was edited mid-chain; declare a re-run if that was the intent)
  6. a token that names some OTHER identity              -> HALT (stale or
       mistyped: it would otherwise re-run nothing, or the wrong thing)
  7. a summary from ANY OTHER run (every pre-B3104 summary included)
                                                         -> HALT, printing
       the exact token line that would declare a re-run and, for Step 2,
       that the re-run reads the holdout again.
The token is ONE-SHOT by construction: it names the identity of the summary
it replaces, while the new summary's identity is the digest of a spec that
CONTAINS the token - so the two can never be equal again, and a later chain
that still lists the spec halts at rule 6 instead of re-running it.

"THIS chain run" is run_serial_chain's --task-name (the Task Scheduler task,
which a reboot restart re-executes with the same name) or a fresh id for a
console chain, which has no restart path. run_wave records it from
SERIAL_CHAIN_RUN_ID; a direct run_wave call records None, which no chain
treats as its own.

IDENTITY = sha256 (16 hex) of the AUTHORED spec as canonical JSON (sorted
keys), minus two sets:
  * ANNOTATIONS - free text that cannot change a run. MEASURED over the 104
    wave specs in output_audit/ on 2026-09-25: top-level note, _doc and every
    key ending _note or _basis (_fires_basis 38, pool_workers_note 16, _doc 2,
    wall_clock_projection_basis 2, _drift_note / _rerun_basis / _resume_note /
    _window_note / note 1 each); arm-level note (59) and env_note (38). EVERY
    OTHER KEY COUNTS, an unknown one included - the fail-closed direction.
  * RUNTIME KEYS run_wave adds to the copy it embeds in a summary:
    _spec_path always; _resolved_scope, window and tickers_file when the
    phase-table resolver ran (_resolved_scope marks that). A step-declaring
    spec may not type window or tickers_file itself (phase_table.
    spec_refusals, B2713), so removing them reconstructs the authored spec;
    a grandfathered legacy spec that typed them reconstructs to a DIFFERENT
    identity, which halts - the loud direction.
"""
from __future__ import annotations

import hashlib
import json

TOKEN_KEY = "supersedes_summary"
COMPLETE = "COMPLETE"
LAUNCH, SKIP, HALT = "LAUNCH", "SKIP", "HALT"

ANNOTATION_EXACT = frozenset({"note", "_doc"})
ANNOTATION_SUFFIXES = ("_note", "_basis")
RUNTIME_ALWAYS = ("_spec_path",)
RUNTIME_WHEN_RESOLVED = ("_resolved_scope", "window", "tickers_file")


def is_annotation(key) -> bool:
    return isinstance(key, str) and (
        key in ANNOTATION_EXACT or key.endswith(ANNOTATION_SUFFIXES))


def _without_annotations(spec: dict) -> dict:
    out = {k: v for k, v in spec.items() if not is_annotation(k)}
    arms = out.get("arms")
    if isinstance(arms, list):
        out["arms"] = [{k: v for k, v in a.items() if not is_annotation(k)}
                       if isinstance(a, dict) else a for a in arms]
    return out


def spec_digest(spec: dict) -> str:
    """The identity of an AUTHORED spec - as read from its file, before
    run_wave adds anything to it."""
    canon = json.dumps(_without_annotations(spec), sort_keys=True,
                       separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canon.encode("ascii")).hexdigest()[:16]


def authored_from_embedded(embedded: dict) -> dict:
    """The authored spec, reconstructed from the copy a summary embeds."""
    s = dict(embedded)
    for k in RUNTIME_ALWAYS:
        s.pop(k, None)
    if "_resolved_scope" in s:
        for k in RUNTIME_WHEN_RESOLVED:
            s.pop(k, None)
    return s


def summary_digest(summary: dict) -> str | None:
    """The identity of the spec that produced a summary: the recorded
    spec_sha256 when run_wave wrote one (B3104 on), else reconstructed from
    the embedded spec; None when neither exists."""
    rec = summary.get("spec_sha256")
    if isinstance(rec, str) and rec:
        return rec
    emb = summary.get("spec")
    if isinstance(emb, dict):
        return spec_digest(authored_from_embedded(emb))
    return None


def summary_status(summary: dict) -> str | None:
    try:
        return str(summary["results"][0].get("status"))
    except (KeyError, IndexError, TypeError, AttributeError):
        return None


UNREADABLE = "UNREADABLE"


def read_summary(root, wave: str):
    """The summary on disk for `wave` under <root>/output_audit, read ONE way
    for both callers (run_serial_chain before a launch, run_wave before its
    archive): the parsed dict, None when absent, or UNREADABLE - an
    unreadable summary is not an absent one (L580), and decide() halts on it."""
    from pathlib import Path
    p = Path(root) / "output_audit" / f"{wave}_wave_summary.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return UNREADABLE


def token_line(identity) -> str:
    if not identity:
        # a summary with no spec to identify cannot be named by a token
        return ("(no token can name it - the summary embeds no spec; move it "
                "aside by hand)")
    return f'"{TOKEN_KEY}": "{identity}"'


def _holdout_note(spec: dict) -> str:
    return (" - a Step-2 re-run READS THE HOLDOUT AGAIN and needs the owner's "
            "explicit word first (runbook 0.6)" if spec.get("step") == 2 else "")


def decide(spec: dict, summary, *, chain_run_id) -> tuple[str, str]:
    """(action, reason) for one spec. `summary` is the parsed summary dict,
    None when no summary is on disk, anything else when it is unreadable."""
    if summary is None:
        return LAUNCH, "no summary on disk"
    if not isinstance(summary, dict):
        return HALT, "the existing summary is unreadable"
    status = summary_status(summary)
    have = summary_digest(summary)
    want = spec_digest(spec)
    token = spec.get(TOKEN_KEY)
    here = bool(chain_run_id) and summary.get("chain_run_id") == chain_run_id
    if here and have == want:
        if status == COMPLETE:
            return SKIP, "COMPLETE, written by this chain run (idempotent restart)"
        return HALT, (f"this chain run's summary reads {status}; a run that stopped "
                      "non-COMPLETE is never relaunched automatically")
    if token and have and token == have:
        return LAUNCH, (f"declared re-run: {TOKEN_KEY} names the existing summary "
                        f"{have} (status {status}); run_wave archives it"
                        + _holdout_note(spec))
    if here:
        return HALT, (f"the spec changed after this chain ran it (identity {have} -> "
                      f"{want}); to re-run it, add {token_line(have)}"
                      + _holdout_note(spec))
    if token:
        return HALT, (f"{TOKEN_KEY} is {token!r} but the existing summary's identity "
                      f"is {have!r} (status {status}) - a stale or mistyped token. If "
                      "this spec is done, remove it from --specs; to re-run it, set "
                      + token_line(have) + _holdout_note(spec))
    return HALT, (f"a summary from another run exists (status {status}, identity "
                  f"{have}, chain_run_id {summary.get('chain_run_id')!r}). If this "
                  "spec is done, remove it from --specs; to re-run it, add "
                  + token_line(have) + " to the spec" + _holdout_note(spec))


def step2_rerun_refusal(spec: dict, summary) -> str | None:
    """run_wave's guard AT THE ACTUATOR (council B3104: the unconditional
    archive in run_wave is where a second read happens, and run_wave is also
    called directly). A COMPLETE Step-2 summary is a spent holdout read, so
    archiving it and running again needs the declared token naming it.
    Recognises Step 2 by `"step": 2` only: a legacy spec that types its
    window instead of declaring a step (65 of the 104 wave specs on
    2026-09-25) is not recognised - the chain's decide() still halts on it."""
    if not isinstance(summary, dict) or spec.get("step") != 2:
        return None
    if summary_status(summary) != COMPLETE:
        return None
    have = summary_digest(summary)
    if have and spec.get(TOKEN_KEY) == have:
        return None
    return (f"REFUSED (S6-B3102a): a COMPLETE Step-2 summary exists (identity "
            f"{have}); running again re-reads the holdout - the one-way door - and "
            f"needs the owner's explicit word recorded as {token_line(have)} in "
            "the spec. Nothing was archived or written.")
