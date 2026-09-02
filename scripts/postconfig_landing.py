#!/usr/bin/env python
"""The ONE post-config landing supervisor: battery -> report -> commit -> push
-> notify -> durable landing record. Runs the moment a cube lands, from EVERY
launch path, with no exceptions.

B2520 (owner ruling 2026-09-01): "Why don't the mandatory post config analysis
steps run automatically after config lands? Have faced this repeatedly despite
of it being a part of the workflow? ... Once the config lands, i want it to run
automatically no exceptions and share results with me."

WHY A SUPERVISOR AND NOT ANOTHER CALL SITE. The battery was invoked from ONE
orchestrator (run_wave.py) after the engine returned; a direct run_phase1a.py
launch, a --resume-from-checkpoint relaunch, and a chain that died between the
engine and the call got nothing (MEASURED: output_icg_cfg1 has no gate receipt
and its grid was hand-built at B2511). Rule 4 of the execution-discipline skill
(L637): the fix for a guard that shares its subject's control flow is ONE
supervisor outside it, not seven patches. So:

  * backtest/run_phase1a.py calls THIS script right after the cube is written -
    every launch path (chain / wave / sweep / direct / resume) ends there;
  * run_wave.py calls it too, and --if-not-landed makes the second call a no-op:
    the landing record (output_audit/postconfig_landings.jsonl) is keyed by cube
    name + a fingerprint of trade_exit_detail.csv (size:mtime_ns);
  * "share results with me" is FOUR channels, none of which depends on the
    session that launched the run being alive (rule 8, L641): the durable
    jsonl record with reported_to_owner=false, the regenerated single report,
    a scoped git commit + push of the audit artifacts, and a desktop toast. The
    Stop hook (scan_undelivered_landing) then refuses to end a turn until the
    landing has been reported to the owner in the response, and the turn
    preamble injector prints every undelivered landing at the top of the next
    turn. Silence is never the record of a landing.

Exit code = the battery's (0 no FAIL / 2 FAIL present); 2 also when there is
no cube to land (fail closed, L642). Reporting failures never mask a battery
result - each channel records its own outcome in the landing event.

Usage:
  python scripts/postconfig_landing.py --cube output_<dir> [--if-not-landed]
      [--force] [--no-git] [--no-notify] [--step1-cube | --step2-cube]
      [--source engine-hook|run_wave|manual]
Env: POSTCONFIG_LANDING_NO_GIT=1 disables commit+push (tests / ad-hoc probes);
     POSTCONFIG_LANDINGS_PATH=<file> redirects the landing record (tests).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

AUDIT = ROOT / "output_audit"
LEDGER = AUDIT / "postconfig_ledger.json"
REPORT = AUDIT / "POSTCONFIG_REPORT.md"
# POSTCONFIG_LANDINGS_PATH redirects the landing record (tests isolate their
# fake cubes from the live record the Stop hook reads).
LANDINGS = Path(os.environ.get("POSTCONFIG_LANDINGS_PATH")
                or (AUDIT / "postconfig_landings.jsonl"))
CUBE_FILE = "trade_exit_detail.csv"
INDEX_LOCK_RETRIES = 5
INDEX_LOCK_WAIT_S = 3.0
PUSH_TIMEOUT_S = 180
TOAST_TIMEOUT_S = 20


def _now() -> str:
    return _dt.datetime.now().isoformat(timespec="seconds")


def fingerprint(cube_dir: Path) -> str | None:
    """size:mtime_ns of the cube file - a cheap identity for 'this landing'."""
    p = cube_dir / CUBE_FILE
    if not p.is_file():
        return None
    st = p.stat()
    return f"{st.st_size}:{st.st_mtime_ns}"


def read_landings(path: Path = LANDINGS) -> list[dict]:
    """Every landing event, oldest first; a torn line is skipped, never fatal."""
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if isinstance(ev, dict):
            out.append(ev)
    return out


def last_landing(cube: str, path: Path = LANDINGS) -> dict | None:
    for ev in reversed(read_landings(path)):
        if ev.get("cube") == cube:
            return ev
    return None


def append_landing(event: dict, path: Path = LANDINGS) -> None:
    """Locked append (parallel arms land concurrently - S6-B2205a class)."""
    import filelock
    path.parent.mkdir(parents=True, exist_ok=True)
    with filelock.FileLock(str(path) + ".lock", timeout=60):
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, sort_keys=True) + "\n")


def undelivered_events(events: list[dict]) -> list[dict]:
    """Landings whose LAST event still says reported_to_owner=false - the
    record is append-only and the reader takes the last event per cube.
    Split out (B2520, #241) so the Stop-hook gate can be exercised on an
    in-memory list from the incident corpus without touching the record."""
    latest: dict[str, dict] = {}
    for ev in events:
        if isinstance(ev, dict) and ev.get("cube"):
            latest[ev["cube"]] = ev
    return [ev for ev in latest.values() if not ev.get("reported_to_owner")]


def undelivered(path: Path = LANDINGS) -> list[dict]:
    """Landings whose LAST event still says reported_to_owner=false."""
    return undelivered_events(read_landings(path))


def mark_reported(cubes: list[str], path: Path = LANDINGS, *, by: str = "") -> int:
    """Append a reported=true event per cube (append-only; the reader takes
    the LAST event per cube). Returns how many were marked."""
    n = 0
    for c in cubes:
        prev = last_landing(c, path)
        if prev is None or prev.get("reported_to_owner"):
            continue
        ev = dict(prev)
        ev.update({"reported_to_owner": True, "reported_ts": _now(),
                   "reported_by": by or "verify_turn_compliance"})
        append_landing(ev, path)
        n += 1
    return n


# ---------------------------------------------------------------------------
# the channels
# ---------------------------------------------------------------------------
def run_battery(cube_dir: Path, *, step1: bool, step2: bool) -> int:
    cmd = [sys.executable, str(ROOT / "scripts" / "run_postconfig.py"),
           "--cube", str(cube_dir), "--write-ledger"]
    if step1:
        cmd.append("--step1-cube")
    elif step2:
        cmd.append("--step2-cube")
    print(f"[landing] battery: {' '.join(cmd[1:])}", flush=True)
    return subprocess.run(cmd, cwd=str(ROOT)).returncode


def render_report() -> tuple[bool, str]:
    try:
        import postconfig_doc as _pcd
        text = _pcd.build()
        REPORT.write_text(text, encoding="utf-8")
        return True, f"{REPORT.name} regenerated ({len(text.splitlines())} lines)"
    except Exception as exc:                        # noqa: BLE001 - report ANY
        return False, f"report NOT regenerated: {type(exc).__name__}: {exc}"


def ledger_steps(cube: str) -> tuple[dict[str, str], list[str]]:
    """(status per step, blocking steps) for one cube, judged by the GATE's own
    is_closed - so a step the battery never wrote (absent row) and an N/A with
    no reason both count as blocking (L642: the absent case is the guarded
    case), and this supervisor can never report a cube cleaner than
    verify_postconfig_complete would."""
    from verify_postconfig_complete import STEPS, is_closed
    try:
        entry = json.loads(LEDGER.read_text(encoding="utf-8")).get(cube) or {}
    except (OSError, ValueError):
        entry = {}
    steps = {s: str((entry.get(s) or {}).get("status") or "MISSING") for s in STEPS}
    blocking = [s for s in STEPS if not is_closed(entry.get(s))]
    return steps, blocking


def lens_findings(cube: str) -> list[str]:
    """Every WARN/FAIL lens, evidence UNTRUNCATED (B2211: the measured values
    sit at the end of a lens line; a cut removes exactly the numbers)."""
    p = AUDIT / f"{cube}_lenses.json"
    if not p.is_file():
        return ["step-5 lens artifact absent"]
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"lens artifact unreadable: {exc!r}"]
    return [f"{r.get('lens')} {r.get('level')}: {r.get('evidence')}"
            for r in doc.get("lenses") or []
            if r.get("level") in ("WARN", "FAIL")]


def _git(args: list[str], *, timeout: float | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True,
                          text=True, timeout=timeout)


QUEUE = ROOT / "EXECUTION_QUEUE.md"
# CRLF, built without escapes: L638 - backslashes do not survive a heredoc,
# and this literal was mangled into a real line break on the first attempt.
_ROW_END = chr(13) + chr(10)


def _append_landing_queue_row(cube: str, battery_exit: int, summary: str) -> bool:
    """S6-B2520g (B2522): one EXECUTED ledger row per landing.

    A landing is a work event, so it belongs in the queue the owner reads -
    and staging it is also what lets the automated commit clear the C8
    queue-anchor gate honestly instead of via an exemption. Returns whether a
    row was appended; a failure here must never stop the landing from being
    RECORDED, so it degrades to False and the commit is skipped rather than
    attempted and rejected.
    """
    try:
        tid = f"S6-LANDING-{cube}-{_now().replace(':', '').replace('-', '')[:15]}"
        one_line = " ".join(str(summary).split())[:600]
        row = (f"| **{tid}** | **EXECUTED** | P1 | "
               f"**Post-config battery landed for `{cube}` (battery exit "
               f"{battery_exit})** | _reason:_ EXECUTED - recorded automatically "
               f"by scripts/postconfig_landing.py at {_now()} (B2520 owner "
               f"ruling: every landing runs the battery and reaches the owner). "
               f"{one_line} |" + _ROW_END)
        with QUEUE.open("ab") as f:
            f.write(row.encode("utf-8"))
        return True
    except Exception:
        return False


def commit_and_push(cube: str, battery_exit: int, summary: str) -> dict:
    """Scoped commit of the AUDIT artifacts only - never a cube dir (L735 /
    CHECKLIST #166), never the landings jsonl (it is the record of what was
    reported, so it changes after the commit). A push rejection is recorded,
    never auto-rebased (HARD RULE: never force / never rebase unattended)."""
    out = {"committed": False, "pushed": False, "note": ""}
    # S6-B2520g (B2522): the FIRST real exercise of this function found it could
    # never succeed. It staged audit artifacts only, and the repo's own C8
    # queue-anchor gate REFUSES any commit that does not stage
    # EXECUTION_QUEUE.md - so every automated landing commit was rejected at
    # preflight, silently, with the rejection recorded as a note nobody read.
    # The honest fix is to SATISFY the gate rather than bypass it with
    # GIT_QUEUE_EXEMPT: a landing IS a work event, so it earns a ledger row,
    # and that row is what the owner reads. Stubs could never have caught this
    # - the gate lives in a git hook, outside every mock.
    queue_row = _append_landing_queue_row(cube, battery_exit, summary)
    paths = [LEDGER, REPORT] + [AUDIT / f"{cube}_{k}.json"
                                for k in ("grid_auto", "spot_check", "lenses")]
    if queue_row:
        paths.append(QUEUE)
    rel = [str(p.relative_to(ROOT)).replace("\\", "/") for p in paths if p.is_file()]
    if not rel:
        out["note"] = "no audit artifacts on disk to commit"
        return out
    add = _git(["add", "--", *rel])
    if add.returncode != 0:
        out["note"] = f"git add failed: {add.stderr.strip()[:200]}"
        return out
    staged = _git(["diff", "--cached", "--quiet", "--", *rel])
    if staged.returncode == 0:
        out["note"] = "nothing to commit (artifacts unchanged)"
        return out
    msg = (f"B2520 landing: {cube} post-config battery exit {battery_exit}\n\n"
           f"{summary}\n\nRecorded automatically by scripts/postconfig_landing.py "
           f"at {_now()}; artifacts only, never the cube dir (CHECKLIST #166).\n")
    for attempt in range(1, INDEX_LOCK_RETRIES + 1):
        c = subprocess.run(["git", "commit", "-q", "-F", "-", "--", *rel],
                           cwd=str(ROOT), input=msg, capture_output=True, text=True)
        if c.returncode == 0:
            break
        if "index.lock" in (c.stderr or "") and attempt < INDEX_LOCK_RETRIES:
            time.sleep(INDEX_LOCK_WAIT_S)
            continue
        out["note"] = f"git commit failed: {(c.stderr or c.stdout).strip()[:200]}"
        return out
    head = _git(["rev-parse", "--short", "HEAD"])
    out["committed"] = head.stdout.strip() if head.returncode == 0 else True
    try:
        p = _git(["push", "-q", "origin", "HEAD"], timeout=PUSH_TIMEOUT_S)
        out["pushed"] = p.returncode == 0
        if p.returncode != 0:
            out["note"] = f"push rejected/failed (NOT rebased): {p.stderr.strip()[:200]}"
    except subprocess.TimeoutExpired:
        out["note"] = f"push timed out after {PUSH_TIMEOUT_S}s"
    return out


def toast(title: str, body: str) -> tuple[bool, str]:
    """Desktop toast, best-effort, Windows only; never raises."""
    if platform.system() != "Windows":
        return False, "toast: not Windows"
    esc = lambda s: s.replace("'", "''")  # noqa: E731
    ps = (
        "[Windows.UI.Notifications.ToastNotificationManager, "
        "Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; "
        "$t = [Windows.UI.Notifications.ToastNotificationManager]::"
        "GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
        "$n = $t.GetElementsByTagName('text'); "
        f"$n.Item(0).AppendChild($t.CreateTextNode('{esc(title)}')) | Out-Null; "
        f"$n.Item(1).AppendChild($t.CreateTextNode('{esc(body)}')) | Out-Null; "
        "[Windows.UI.Notifications.ToastNotificationManager]::"
        "CreateToastNotifier('stock-picks-app').Show("
        "[Windows.UI.Notifications.ToastNotification]::new($t))")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive",
                            "-Command", ps], capture_output=True, text=True,
                           timeout=TOAST_TIMEOUT_S)
        return (r.returncode == 0,
                "toast shown" if r.returncode == 0
                else f"toast failed: {(r.stderr or r.stdout).strip()[:120]}")
    except Exception as exc:                        # noqa: BLE001
        return False, f"toast failed: {type(exc).__name__}: {exc}"


# ---------------------------------------------------------------------------
def land(cube_dir: Path, *, source: str, if_not_landed: bool, force: bool,
         no_git: bool, no_notify: bool, step1: bool, step2: bool) -> int:
    cube = cube_dir.name
    fp = fingerprint(cube_dir)
    if fp is None:
        print(f"[landing] FAIL: no {CUBE_FILE} under {cube_dir} - nothing landed "
              "(fail closed, L642)")
        return 2
    if if_not_landed and not force:
        prev = last_landing(cube)
        if prev and prev.get("fingerprint") == fp:
            print(f"[landing] {cube} already landed at {prev.get('ts')} "
                  f"(battery_exit {prev.get('battery_exit')}, source "
                  f"{prev.get('source')}); fingerprint {fp} unchanged - no-op")
            return int(prev.get("battery_exit") or 0)

    t0 = time.time()
    print(f"=== POST-CONFIG LANDING: {cube} (source {source}, fingerprint {fp}) ===",
          flush=True)
    battery_exit = run_battery(cube_dir, step1=step1, step2=step2)
    steps, blocking = ledger_steps(cube)
    findings = lens_findings(cube)
    report_ok, report_note = render_report()

    summary = (f"steps: " + ", ".join(f"{s}={st}" for s, st in sorted(steps.items()))
               + f"; blocking: {blocking or 'none'}; lens findings: "
               + (f"{len(findings)} -> " + " | ".join(findings) if findings else "0"))
    git = {"committed": False, "pushed": False, "note": "git disabled"}
    git_allowed = (not no_git and os.environ.get("POSTCONFIG_LANDING_NO_GIT") != "1"
                   and ((cube_dir / "run_manifest.json").is_file() or force))
    if git_allowed:
        git = commit_and_push(cube, battery_exit, summary)
    elif not no_git and os.environ.get("POSTCONFIG_LANDING_NO_GIT") != "1":
        git["note"] = "git skipped: no run_manifest.json beside the cube (ad-hoc run; --force overrides)"

    notify = (False, "notify disabled")
    if not no_notify:
        notify = toast(f"Config landed: {cube}",
                       f"battery exit {battery_exit}; blocking {len(blocking)}; "
                       f"lens findings {len(findings)}; committed "
                       f"{git['committed'] or 'no'}, pushed {git['pushed']}")

    event = {"cube": cube, "ts": _now(), "fingerprint": fp, "source": source,
             "step_flags": ("step1" if step1 else "step2" if step2 else "derived"),
             "battery_exit": battery_exit, "steps": steps, "blocking": blocking,
             "findings": findings, "report_ok": report_ok, "report_note": report_note,
             "committed": git["committed"], "pushed": git["pushed"],
             "git_note": git["note"], "toast": notify[1],
             "elapsed_s": int(time.time() - t0), "reported_to_owner": False}
    try:
        append_landing(event)
    except Exception as exc:                        # noqa: BLE001
        rec = f"LANDING RECORD NOT WRITTEN: {type(exc).__name__}: {exc}"
    else:
        # the path label must never turn a written record into "NOT WRITTEN"
        # (a POSTCONFIG_LANDINGS_PATH outside the repo has no relative form)
        try:
            rec = f"recorded -> {LANDINGS.relative_to(ROOT)}"
        except ValueError:
            rec = f"recorded -> {LANDINGS}"

    print(f"\n=== LANDING REPORT: {cube} ===")
    print(f"  battery exit {battery_exit}; {len(steps)} steps recorded; blocking "
          f"{blocking or 'none'}")
    for s, st in sorted(steps.items()):
        print(f"    {st:<5} {s}")
    print(f"  lens findings: {len(findings)}")
    for f_ in findings:
        print(f"    - {f_}")
    print(f"  report: {report_note}")
    print(f"  git: committed {git['committed']}, pushed {git['pushed']}"
          + (f" ({git['note']})" if git["note"] else ""))
    print(f"  notify: {notify[1]}")
    print(f"  {rec}; reported_to_owner=false until the owner sees it in a turn")
    print(f"=== END LANDING {cube} ({int(time.time() - t0)}s) ===", flush=True)
    return battery_exit


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cube", required=True, help="cube dir (name or path)")
    ap.add_argument("--if-not-landed", action="store_true",
                    help="no-op when this cube (same fingerprint) already landed")
    ap.add_argument("--force", action="store_true",
                    help="land again even if recorded; also allows git without a manifest")
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--no-notify", action="store_true")
    ap.add_argument("--step1-cube", action="store_true")
    ap.add_argument("--step2-cube", action="store_true")
    ap.add_argument("--source", default="manual",
                    choices=("engine-hook", "run_wave", "manual"))
    a = ap.parse_args()
    cube_dir = Path(a.cube)
    if not cube_dir.is_absolute():
        cube_dir = ROOT / a.cube
    if cube_dir.name == CUBE_FILE:
        cube_dir = cube_dir.parent
    return land(cube_dir.resolve(), source=a.source, if_not_landed=a.if_not_landed,
                force=a.force, no_git=a.no_git, no_notify=a.no_notify,
                step1=a.step1_cube, step2=a.step2_cube)


if __name__ == "__main__":
    raise SystemExit(main())
