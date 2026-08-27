#!/usr/bin/env python
"""B2281 (S6-B2278 option 4, owner-approved 2026-08-27): no-console chain launch.

WHY THIS EXISTS. Two chains have died with LastTaskResult 0xC000013A
(STATUS_CONTROL_C_EXIT). The scheduled task runs `cmd.exe /c "... python
run_serial_chain.py ..."`, so the whole tree shares cmd's CONSOLE, and any
console-control event - a window close, a Ctrl+C, a logoff broadcast - kills
the chain. The sender was never identified (S6-B2278: two candidate senders
DISPROVEN by reading the task settings - battery policy off, idle stop inert);
what survived every disproof is that the tree HAS a console.

THE FIX IS STRUCTURAL, NOT PRIVILEGED: launch the chain as a DETACHED_PROCESS
with CREATE_NO_WINDOW. A process with no console cannot RECEIVE console-control
events, so the 0xC000013A class is closed by construction - no elevation, and
the user's git identity (which the post-config battery needs for its
commit+push) stays intact. Elevation to SYSTEM was considered and REJECTED:
it would immunise against console kills but put ~/.git-credentials out of
scope, trading a loud death for silent push failures.

WHAT THIS DOES NOT ADDRESS, stated per L680 (independent failure modes): the
DuplicateHandle spawn-privilege class that killed the run at sim-day 230 on
2026-08-27. That is guarded separately by probe_pool_spawn at every arm launch
(SPAWN_REFUSED in seconds instead of a 1.7h loss).

B2229 WIRING (approved fold-in): before launching, sample the COMMIT CHARGE -
the quantity that actually fails (L670) - via commit_watchdog and REFUSE the
launch below the floor. The absent reading also refuses (L642: a guard fails
closed on the absent input).

Usage:
    python scripts/launch_chain_noconsole.py --specs-list output_audit/b2197_chain_specs_v2_no_sp21.txt
    python scripts/launch_chain_noconsole.py --specs a_spec.json b_spec.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "output_audit" / "b2213_chain_restart.log"
PID_FILE = ROOT / "output_audit" / "_chain_pid.json"

# DETACHED_PROCESS: no console inherited, none created - console-control
# events cannot reach the child. CREATE_NO_WINDOW alone is NOT enough (the
# child still gets an invisible console, and CTRL_CLOSE style events can
# still be delivered to it). CREATE_NEW_PROCESS_GROUP: a Ctrl+C aimed at any
# ancestor's group does not propagate.
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
LAUNCH_FLAGS = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

COMMIT_FLOOR_GB = 3.0  # refuse a ~22h launch with less commit headroom than
                       # two configs' peak; the chain itself needs ~2-4 GB and
                       # death-by-commit is the class that killed three runs.


def commit_gate(floor_gb: float = COMMIT_FLOOR_GB,
                reading_gb: float | None = None) -> tuple[bool, str]:
    """Refuse the launch when free COMMIT (not physical RAM) is under floor.

    L642: the absent reading REFUSES - an unreadable counter is not a pass.
    """
    if reading_gb is None:
        try:
            sys.path.insert(0, str(ROOT / "scripts"))
            import commit_watchdog
            r = commit_watchdog.read_commit()  # None when unreadable, no raise
        except Exception as exc:
            return False, f"REFUSE: commit charge unreadable ({exc}) - L642"
        if r is None:
            return False, "REFUSE: commit charge unreadable (None) - L642"
        # key verified against the live API this batch (L690: the chain, not
        # the leaf's imagined name - the first draft said 'free_gb').
        reading_gb = r["commit_avail_gb"]
    if reading_gb < floor_gb:
        return False, (f"REFUSE: {reading_gb:.2f} GB free commit < "
                       f"{floor_gb:.2f} GB floor - the failing quantity (L670)")
    return True, f"commit ok: {reading_gb:.2f} GB free >= {floor_gb:.2f} GB floor"


def build_cmd(specs: list[str]) -> list[str]:
    py = ROOT / ".venv" / "Scripts" / "python.exe"
    return [str(py), str(ROOT / "scripts" / "run_serial_chain.py"),
            "--specs", *specs]


def launch(specs: list[str]) -> int:
    ok, msg = commit_gate()
    print(msg)
    if not ok:
        return 2
    log = open(LOG, "ab")
    env = dict(__import__("os").environ, PYTHONPATH=".")
    proc = subprocess.Popen(
        build_cmd(specs), cwd=str(ROOT), env=env,
        stdout=log, stderr=subprocess.STDOUT,
        creationflags=LAUNCH_FLAGS,
        close_fds=False,
    )
    PID_FILE.write_text(json.dumps({
        "pid": proc.pid,
        "launched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "launcher": "launch_chain_noconsole.py (B2281, DETACHED_PROCESS)",
        "specs": specs,
        "log": str(LOG),
    }, indent=1), encoding="utf-8")
    print(f"[B2281] chain launched DETACHED pid={proc.pid}; no console attached; "
          f"log={LOG.name}; pid file={PID_FILE.name}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs", nargs="*", default=None)
    ap.add_argument("--specs-list", default=None,
                    help="file with one spec path per line")
    a = ap.parse_args()
    specs = list(a.specs or [])
    if a.specs_list:
        specs += Path(a.specs_list).read_text().split()
    if not specs:
        print("no specs given"); return 1
    return launch(specs)


if __name__ == "__main__":
    sys.exit(main())
