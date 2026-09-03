#!/usr/bin/env python
"""B2214 (L658, compliance failure vs L411/S6-B1534e): kill a wave's processes
by VERIFIED IDENTITY, never by process name.

Source: the target wave's output_<dir>/run_heartbeat.json (which records the
engine's own pid) plus each candidate process's COMMAND LINE from
Win32_Process; per CHECKLIST #77.

THE MISS THIS CLOSES: restarting a config, I ran the equivalent of
`Get-Process python | Stop-Process -Force` - twice. That is a force-sweep BY
NAME across the whole machine. It takes out pytest runs, other Claude
sessions, unrelated notebooks, anything else spelled "python". It happened to
be survivable here only because nothing else was running; that is luck, not
design. The rule is older than this incident (L411): get the PID, VERIFY its
command line, then stop it by id.

WHAT THIS DOES:
  1. reads the wave's heartbeat to learn the ENGINE PARENT pid,
  2. enumerates python processes with their command lines,
  3. keeps only those whose command line names the wave's output directory
     (the parent) or whose parent chain leads to it (the pool workers),
  4. prints every candidate with its pid and command-line fragment,
  5. kills ONLY those, by pid - and refuses entirely if the heartbeat is
     missing, because an unidentified target is not a target.

--dry-run prints the kill list and stops. Default is dry-run: a destructive
default is how a safety tool becomes the hazard it replaces.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _ps(cmd: str) -> str:
    r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                       capture_output=True, text=True)
    return (r.stdout or "") + (r.stderr or "")


def candidates(out_dir: str) -> list[tuple[int, int, str]]:
    """(pid, parent_pid, command_line) for python processes naming out_dir."""
    raw = _ps("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
              "ForEach-Object { \"$($_.ProcessId)|$($_.ParentProcessId)|"
              "$($_.CommandLine)\" }")
    rows = []
    for line in raw.splitlines():
        parts = line.split("|", 2)
        if len(parts) != 3 or not parts[0].strip().isdigit():
            continue
        rows.append((int(parts[0]), int(parts[1]), parts[2]))
    # the parent names the output dir on its command line; workers are spawned
    # children of it and carry a multiprocessing bootstrap instead, so they are
    # matched through the parent chain rather than by string.
    named = {p for p, _, c in rows if out_dir in c}
    # B2577 (S6-B2573g.c): the wave's ROOT is run_wave.py, whose command line
    # names the SPEC (`--spec output_audit/<spec>.json`), never the out_dir -
    # so the old match left run_wave alive above a killed engine, and it went
    # on to run the battery over a dead cube. Walk UP from every named process
    # while the ancestor is wave-side (run_wave / launch_sweep) and stop at
    # run_serial_chain, which HALTs by design on the non-COMPLETE wave and
    # must never be killed.
    by_pid = {p: (pp, c) for p, pp, c in rows}
    roots: set[int] = set()
    for p in named:
        pp = by_pid[p][0]
        while pp in by_pid and pp not in roots and _wave_side(by_pid[pp][1]):
            roots.add(pp)
            pp = by_pid[pp][0]
    keep = [(p, pp, c) for p, pp, c in rows
            if p in named or p in roots or pp in named]
    return keep


def _wave_side(cmd: str) -> bool:
    return (("run_wave.py" in cmd or "launch_sweep.py" in cmd)
            and "run_serial_chain" not in cmd)


def launches(keep: list[tuple[int, int, str]]) -> int:
    """Distinct LAUNCHES among `keep`. MEASURED B2577: the venv's python.exe is
    a launcher that spawns the real interpreter with the SAME command line
    (creation ~20 ms apart), so every launch shows up as two pids and a
    count of pids overstates the tree twofold. A process whose PARENT is in
    the list with an identical command line is that parent's interpreter
    twin, not a second launch."""
    by_pid = {p: c for p, _, c in keep}
    return sum(1 for p, pp, c in keep if not (pp in by_pid and by_pid[pp] == c))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True,
                    help="the wave's output directory name, e.g. "
                         "output_b2197_sw20sp50_sw20sp50")
    ap.add_argument("--execute", action="store_true",
                    help="actually kill; omit for a dry run (the default)")
    a = ap.parse_args()

    hb = ROOT / a.out_dir / "run_heartbeat.json"
    if not hb.exists():
        print(f"REFUSING: no heartbeat at {hb} - the engine pid is unknown, "
              "and an unidentified target is not a target.")
        return 2
    engine_pid = json.loads(hb.read_text(encoding="utf-8")).get("pid")
    print(f"heartbeat names engine pid {engine_pid}")

    keep = candidates(a.out_dir)
    if not keep:
        print("no matching processes - nothing to kill (this is a real result, "
              "not an error)")
        return 0
    print(f"{len(keep)} process(es) = {launches(keep)} launch(es) matched by "
          "command line / parent chain (a venv launcher and its interpreter "
          "twin count once):")
    for pid, ppid, cmd in keep:
        print(f"  pid {pid} (parent {ppid}): {cmd[:110]}")
    if not a.execute:
        print("DRY RUN - pass --execute to kill exactly these pids")
        return 0
    ids = ",".join(str(p) for p, _, _ in keep)
    print(_ps(f"Stop-Process -Id {ids} -Force -ErrorAction SilentlyContinue; "
              f"Start-Sleep -Seconds 3; "
              f"'survivors: ' + (Get-Process -Id {ids} -ErrorAction "
              "SilentlyContinue | Measure-Object).Count").strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
