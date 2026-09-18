#!/usr/bin/env python
"""B2856 (S6-B2854b): stop a pyramid gate AND its subprocess tree.

THE INCIDENT: TaskStop on the launching shell killed only the wrapper; the
python gate and its pytest child survived - at B2854 four processes were
killed by hand-verified PID, two of them racing on one output artifact and
one measuring a stale tree. On Windows nothing propagates a parent's death
to its children, so a stopper must address the TREE: taskkill /T on the
gate's own PID, which pyramid_gate now records in a pidfile beside its
artifact (removed on normal completion - a leftover pidfile marks a killed
or crashed gate).

Dry-run by DEFAULT (the kill_wave_tree.py precedent); --force to kill.
FAIL CLOSED both ways (L642/L658): no pidfile -> refuse and say why; PID's
command line not a pyramid_gate -> refuse, because PIDs are reused and an
unidentified target is not a target.

Usage:
    python scripts/kill_gate_tree.py --out output_audit/bNNNN_gate.json
    python scripts/kill_gate_tree.py --out output_audit/bNNNN_gate.json --force
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def _cmdline(pid: int, probe=None) -> str:
    """The live command line of `pid`, '' if the process is gone.
    `probe` is the test seam (#241)."""
    if probe is not None:
        return probe(pid)
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         f"(Get-CimInstance Win32_Process -Filter 'ProcessId={int(pid)}')"
         ".CommandLine"],
        capture_output=True, text=True, timeout=30)
    return (r.stdout or "").strip()


def stop_tree(out: str, *, force: bool = False, probe=None,
              killer=None) -> str:
    pidfile = Path(str(out) + ".pid")
    if not pidfile.is_file():
        raise SystemExit(
            f"REFUSED: no pidfile at {pidfile} - either the gate completed "
            "(pidfile removed on exit) or it predates B2856. Triage by hand "
            "with Get-CimInstance filtered on pyramid_gate; never kill by "
            "name.")
    pid = int(pidfile.read_text(encoding="utf-8").strip())
    cmd = _cmdline(pid, probe)
    if "pyramid_gate" not in (cmd or ""):
        raise SystemExit(
            f"REFUSED: PID {pid} is not a live pyramid_gate (command line "
            f"{cmd[:120]!r}) - the PID was reused or the pidfile is stale; "
            "nothing killed (L658: an unidentified target is not a target).")
    if not force:
        return (f"DRY-RUN: would run taskkill /PID {pid} /T /F "
                f"(verified: {cmd[:120]}) - re-run with --force to kill")
    if killer is None:
        def killer(p):
            return subprocess.run(
                ["taskkill", "/PID", str(int(p)), "/T", "/F"],
                capture_output=True, text=True, timeout=30)
    r = killer(pid)
    rc = getattr(r, "returncode", 0)
    if rc != 0:
        raise SystemExit(
            f"taskkill exited {rc}: {getattr(r, 'stdout', '')} "
            f"{getattr(r, 'stderr', '')}")
    return f"KILLED the tree rooted at PID {pid} (taskkill /T /F)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True,
                    help="the gate artifact whose .pid sidecar names the "
                         "tree root")
    ap.add_argument("--force", action="store_true",
                    help="actually kill (default is dry-run)")
    a = ap.parse_args()
    print(stop_tree(a.out, force=a.force))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
