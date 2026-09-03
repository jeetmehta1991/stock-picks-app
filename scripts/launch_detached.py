#!/usr/bin/env python
"""B2188 (S6-B2184a, owner-approved): launch a wave DETACHED from the session.

WHY: session restarts killed five engine legs across three events (S6-B2184a
census). Engines were children of the session's background shell; when the
session died, Windows tore the tree down. A Task Scheduler task is owned by
the scheduler service - it survives ANY session event.

THE LAPTOP TRAP, measured before this worked: schtasks-CLI tasks default to
"start only if on AC power", so on a laptop they register, /run reports
SUCCESS, and the task sits at Status: Queued forever (observed live at
B2188). Registration therefore goes through PowerShell's
Register-ScheduledTask with -AllowStartIfOnBatteries
-DontStopIfGoingOnBatteries, which executed the proof payload in 8 seconds
on this same box.

Usage:
  python scripts/launch_detached.py --spec output_audit/<spec>.json
  python scripts/launch_detached.py --chain --batch b2574
      --specs output_audit/<a>_spec.json output_audit/<b>_spec.json
      [--wait-for output_audit/<predecessor>_wave_summary.json]
      [--time-limit-hours 48]
  python scripts/launch_detached.py --selftest
  python scripts/launch_detached.py --cleanup <task_name>

B2574 (S6-B2573e class) --chain: the b2527 chain was HAND-registered from a
hand-written output_audit/_b2527_chain.cmd because this script only knew
single waves - the launch path a runbook can cite did not exist for the
thing actually running. --chain writes output_audit/_<batch>_chain.cmd
(the same template, plus --wait-for when given), refuses a spec that does
not parse or a batch whose chain task is already Running, registers
stockpicks_chain_<batch>_<ts> with the chain-sized ExecutionTimeLimit, and
records the OBSERVED task state in output_audit/_<batch>_chain_task.json.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run_ps(script: str) -> subprocess.CompletedProcess:
    ps1 = ROOT / "output_audit" / "_detached_launcher.ps1"
    ps1.write_text(script, encoding="utf-8")
    return subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(ps1)], capture_output=True, text=True)


def _register_and_start(name: str, exe: str, args: str,
                        hardened: bool = False,
                        time_limit_hours: int = 12) -> subprocess.CompletedProcess:
    """B2203a HARDENING (S6-B2202a class): hardened=True registers the task
    under the SYSTEM principal (session 0, no interactive console), so a
    console-control event in the user's session - window close, logoff,
    Ctrl+C propagation - cannot reach the task tree. MEASURED INCIDENT: the
    b2197 chain task, registered interactively, died 0xC000013A
    (STATUS_CONTROL_C_EXIT) at 2026-08-26T14:33:21Z mid-config with zero OS
    resource events; ~19 min downtime. Trade-off, stated: a SYSTEM task's
    files are SYSTEM-owned (admin users still read them) and its environment
    is not the user's - launch commands must carry absolute paths, which
    ours already do.

    B2528 - time_limit_hours: Task Scheduler's ExecutionTimeLimit bounds the
    WHOLE task run, and 12 h was sized for ONE wave (~2.9 h measured). A
    16-config serial chain projects at 38-47 h, so the default would have
    killed it about four configs in, overnight, with the chain log simply
    stopping - a guard whose bound nobody multiplied out against the job it
    was guarding (L637). The parameter DEFAULTS to 12 so every single-wave
    caller is byte-identical; a chain passes its own bound. Size it ABOVE the
    projected upper end with margin, never at it: this is a backstop for a
    hung task, and a backstop set at the expected duration kills healthy work
    (L734, where a 3x wall backstop died on exactly that arithmetic).
    """
    principal = ('$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" '
                 '-LogonType ServiceAccount -RunLevel Highest\n'
                 if hardened else "")
    principal_arg = " -Principal $principal" if hardened else ""
    script = f"""
$action = New-ScheduledTaskAction -Execute "{exe}" -Argument '{args}'
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours {time_limit_hours})
{principal}Register-ScheduledTask -TaskName "{name}" -Action $action -Settings $settings{principal_arg} -Force | Out-Null
Start-ScheduledTask -TaskName "{name}" -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
# B2559 (S6-B2529a): report the task we OBSERVE, never the one we intended.
# This block used to print `registered_and_started` unconditionally, so a
# DENIED Register-ScheduledTask still reported success and the caller's grep
# passed - my first chain launch said LAUNCHED with no task in existence.
$t = Get-ScheduledTask -TaskName "{name}" -ErrorAction SilentlyContinue
if ($t) {{
    $info = Get-ScheduledTaskInfo -TaskName "{name}"
    Write-Output ("registered_and_started " + "{name}" + " state=" + $t.State + " last_result=" + $info.LastTaskResult)
}} else {{
    Write-Output ("register_failed " + "{name}" + " - the task does not exist after Register-ScheduledTask")
}}
"""
    return _run_ps(script)


def launch(spec_path: str, hardened: bool = False) -> int:
    spec = json.loads((ROOT / spec_path).read_text(encoding="utf-8"))
    name = f"stockpicks_wave_{spec['wave']}_{int(time.time())}"
    log = ROOT / "output_audit" / f"{spec['wave']}_detached.log"
    args = (f'/c "cd /d {ROOT} && set PYTHONPATH=. && '
            f'{sys.executable} scripts\\run_wave.py --spec {spec_path} '
            f'>> {log} 2>&1"')
    r = _register_and_start(name, "cmd.exe", args, hardened=hardened)
    out = (r.stdout or "") + (r.stderr or "")
    # B2559 (S6-B2529a): `registered_and_started` alone was emitted whether or
    # not the task existed. The success line now carries `state=`, written only
    # from a Get-ScheduledTask that returned an object, so requiring it means
    # the caller is reading an OBSERVATION rather than an intention.
    if r.returncode != 0 or "registered_and_started" not in out or "state=" not in out:
        print(f"DETACHED LAUNCH FAILED: {out.strip()[:400]}")
        return 1
    print(f"DETACHED LAUNCH OK: task={name}")
    print(f"  spec={spec_path}")
    print(f"  stdout -> {log}")
    print(f"  cleanup when done: python scripts/launch_detached.py --cleanup {name}")
    return 0


def chain_cmd_text(specs: list[str], log: Path, wait_for: str | None,
                   task_name: str | None = None) -> str:
    """The .cmd body Task Scheduler runs. Single-threaded BLAS (the engine
    forks a screen pool; nested BLAS threads oversubscribe the box), repo
    root cwd, PYTHONPATH=., stdout+stderr appended to the chain log.
    B2577: `task_name` (None = byte-identical to the b2527 golden shape)
    passes the task's own name so run_serial_chain can unregister it at
    CHAIN DONE."""
    wait = f"--wait-for {wait_for} " if wait_for else ""
    wait += f"--task-name {task_name} " if task_name else ""
    lines = [
        "@echo off",
        f"cd /d {ROOT}",
        "set PYTHONPATH=.",
        "set OPENBLAS_NUM_THREADS=1",
        "set OMP_NUM_THREADS=1",
        "set MKL_NUM_THREADS=1",
        f'"{sys.executable}" scripts\\run_serial_chain.py {wait}--specs '
        + " ".join(specs) + f' >> "{log}" 2>&1',
        "exit /b %ERRORLEVEL%",
    ]
    return "\r\n".join(lines) + "\r\n"


def chain_task_running(batch: str) -> str | None:
    """Name of an already-Running stockpicks_chain_<batch>_* task, or None
    (feedback_check_existing_pids_before_long_background_launch)."""
    r = _run_ps(
        f'Get-ScheduledTask -TaskPath "\\" -ErrorAction SilentlyContinue | '
        f'Where-Object {{ $_.TaskName -like "stockpicks_chain_{batch}_*" '
        f'-and $_.State -eq "Running" }} | '
        f'ForEach-Object {{ Write-Output $_.TaskName }}')
    names = [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]
    return names[0] if names else None


def launch_chain(batch: str, specs: list[str], wait_for: str | None,
                 time_limit_hours: int, hardened: bool = False) -> int:
    if not batch.replace("_", "").isalnum():
        print(f"CHAIN LAUNCH REFUSED: batch {batch!r} must be alphanumeric/_")
        return 2
    waves = []
    for sp in specs:
        try:
            j = json.loads((ROOT / sp).read_text(encoding="utf-8"))
            waves.append(j["wave"])
        except (OSError, ValueError, KeyError) as exc:
            print(f"CHAIN LAUNCH REFUSED: spec {sp} unreadable or has no 'wave': {exc!r}")
            return 2
    if wait_for and not wait_for.endswith("_wave_summary.json"):
        print(f"CHAIN LAUNCH REFUSED: --wait-for must name a *_wave_summary.json, got {wait_for}")
        return 2
    running = chain_task_running(batch)
    if running:
        print(f"CHAIN LAUNCH REFUSED: {running} is already Running for batch {batch}")
        return 2
    log = ROOT / "output_audit" / f"{batch}_chain_detached.log"
    cmd = ROOT / "output_audit" / f"_{batch}_chain.cmd"
    # B2577: the name is chosen BEFORE the .cmd is written so the chain can
    # unregister its own task at CHAIN DONE (S6-B2573g.a).
    name = f"stockpicks_chain_{batch}_{int(time.time())}"
    cmd.write_text(chain_cmd_text(specs, log, wait_for, task_name=name),
                   encoding="utf-8")
    r = _register_and_start(name, "cmd.exe", f'/c "{cmd}"', hardened=hardened,
                            time_limit_hours=time_limit_hours)
    out = (r.stdout or "") + (r.stderr or "")
    ok = (r.returncode == 0 and "registered_and_started" in out and "state=" in out)
    state_line = next((ln for ln in out.splitlines() if "registered_and_started" in ln
                       or "register_failed" in ln), out.strip()[:200])
    record = {"task": name, "batch": batch, "order": waves, "specs": specs,
              "wait_for": wait_for, "cmd_file": cmd.name,
              "time_limit_hours": time_limit_hours, "hardened": hardened,
              "verified_task": state_line.strip(), "launched": ok,
              "log": str(log).replace("\\", "/"),
              "registered_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    (ROOT / "output_audit" / f"_{batch}_chain_task.json").write_text(
        json.dumps(record, indent=1), encoding="utf-8")
    if not ok:
        print(f"DETACHED CHAIN LAUNCH FAILED: {out.strip()[:400]}")
        return 1
    print(f"DETACHED CHAIN LAUNCH OK: task={name}")
    print(f"  specs={len(specs)} order={waves}")
    print(f"  wait_for={wait_for}")
    print(f"  cmd -> {cmd}")
    print(f"  stdout -> {log}")
    print(f"  observed: {state_line.strip()}")
    print(f"  cleanup at CHAIN DONE: the chain unregisters {name} itself (B2577); "
          f"after a HALT: python scripts/launch_detached.py --cleanup {name}")
    return 0


def selftest(hardened: bool = False) -> int:
    """Prove detachment end-to-end with a file-writing payload."""
    proof = ROOT / "output_audit" / "_detached_selftest.txt"
    proof.unlink(missing_ok=True)
    name = f"stockpicks_selftest_{int(time.time())}"
    r = _register_and_start(name, "cmd.exe", f'/c echo detached> "{proof}"',
                            hardened=hardened)
    deadline = time.time() + 30
    while time.time() < deadline and not proof.exists():
        time.sleep(1)
    _run_ps(f'Unregister-ScheduledTask -TaskName "{name}" -Confirm:$false')
    if proof.exists():
        print("SELFTEST PASS: the Task Scheduler service executed the payload "
              "outside the session's process tree (battery-allowed settings)")
        proof.unlink()
        return 0
    print(f"SELFTEST FAIL: {(r.stdout or r.stderr).strip()[:300]}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--hardened", action="store_true",
                    help="register under SYSTEM (session 0) - immune to "
                         "console-control kills (B2203a; the 0xC000013A class)")
    ap.add_argument("--cleanup")
    ap.add_argument("--chain", action="store_true",
                    help="register a run_serial_chain over --specs (B2574)")
    ap.add_argument("--batch", help="chain batch id, e.g. b2574")
    ap.add_argument("--specs", nargs="+", help="chain specs in run order")
    ap.add_argument("--wait-for", default=None,
                    help="predecessor *_wave_summary.json the chain waits on")
    ap.add_argument("--time-limit-hours", type=int, default=48,
                    help="chain ExecutionTimeLimit; size ABOVE wait + run (B2528)")
    a = ap.parse_args()
    if a.selftest:
        return selftest(hardened=a.hardened)
    if a.chain:
        if not (a.batch and a.specs):
            print("--chain needs --batch and --specs")
            return 2
        return launch_chain(a.batch, a.specs, a.wait_for, a.time_limit_hours,
                            hardened=a.hardened)
    if a.cleanup:
        r = _run_ps(f'Unregister-ScheduledTask -TaskName "{a.cleanup}" -Confirm:$false; '
                    f'Write-Output "deleted {a.cleanup}"')
        print((r.stdout or r.stderr).strip())
        return r.returncode
    if not a.spec:
        print("--spec required (or --selftest / --cleanup)")
        return 2
    return launch(a.spec, hardened=a.hardened)


if __name__ == "__main__":
    raise SystemExit(main())
