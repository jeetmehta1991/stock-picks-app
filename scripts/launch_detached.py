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
  python scripts/launch_detached.py --selftest
  python scripts/launch_detached.py --cleanup <task_name>
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
Start-ScheduledTask -TaskName "{name}"
Start-Sleep -Seconds 3
$info = Get-ScheduledTaskInfo -TaskName "{name}"
Write-Output ("registered_and_started " + "{name}" + " last_result=" + $info.LastTaskResult)
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
    if r.returncode != 0 or "registered_and_started" not in out:
        print(f"DETACHED LAUNCH FAILED: {out.strip()[:400]}")
        return 1
    print(f"DETACHED LAUNCH OK: task={name}")
    print(f"  spec={spec_path}")
    print(f"  stdout -> {log}")
    print(f"  cleanup when done: python scripts/launch_detached.py --cleanup {name}")
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
    a = ap.parse_args()
    if a.selftest:
        return selftest(hardened=a.hardened)
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
