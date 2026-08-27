#!/usr/bin/env python
"""S6-B2227 / L670: sample COMMIT CHARGE across firings, not free physical RAM.

WHY THIS EXISTS AND WHY IT WATCHES A DIFFERENT NUMBER THAN EVERY PRIOR MONITOR:
the runs die of commit exhaustion, and every capacity figure in the plan is
WORKING SET. Measured on the live 18-process pool 2026-08-27: the python tree
held 42.63 GB of private commit against 6.16 GB of working set - a ratio of
6.93 - while free PHYSICAL memory read a comfortable 2.11 GB in the same instant
the box had 1.28 GB of commit left, 97.8pct used.

**Working set is RESIDENT pages; commit is reserved address space backed by RAM
plus pagefile. The allocation that FAILS is a commit.** A monitor watching the
working-set side reports health right up to the failure, which is the behaviour
observed across three deaths.

MEASURED COST OF THE THING THIS PROTECTS (B2229c, the figure S6-B2227d owed):
a THREE-TEST pytest run consumed 1.183 GB of commit and drove available commit
from 1.292 GB to 0.109 GB - within 109 MB of exhaustion. That is import cost,
not per-test cost, so it is close to the floor for ANY pytest invocation here.

DESIGN, per the L667 rule that a conclusion about a moving quantity must be
re-dated rather than retired: this samples ACROSS INVOCATIONS and escalates on
N consecutive readings under the floor, never on a single point. One reading
cannot distinguish a steady state from a transient near a checkpoint write.

Exit codes: 0 healthy, 1 unreadable (refuses to judge), 2 BREACH.
State lives in output_audit/_commit_watch.json so consecutive runs accumulate
evidence rather than re-deciding from one sample.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "output_audit"

# The floor is the MEASURED cost of the lightest real pytest invocation
# (1.183 GB, B2229c) plus a margin. Below this, a pyramid cannot run without
# risking the live wave - which is the decision this watchdog exists to inform.
DEFAULT_FLOOR_GB = 1.5


def read_commit() -> dict | None:
    """Read commit limit/available from the OS. None if unreadable.

    Uses Win32_OperatingSystem TotalVirtualMemorySize / FreeVirtualMemory,
    which are the commit LIMIT and AVAILABLE COMMIT in KB - NOT the physical
    figures. Naming them explicitly because reading the wrong pair is the
    entire defect this script was written for.
    """
    ps = ("$os = Get-CimInstance Win32_OperatingSystem; "
          "Write-Output ('{0} {1} {2}' -f $os.TotalVirtualMemorySize, "
          "$os.FreeVirtualMemory, $os.FreePhysicalMemory)")
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    parts = out.stdout.split()
    if len(parts) != 3:
        return None
    try:
        limit_kb, avail_kb, phys_kb = (int(float(p)) for p in parts)
    except ValueError:
        return None
    return {"commit_limit_gb": round(limit_kb / 1048576, 3),
            "commit_avail_gb": round(avail_kb / 1048576, 3),
            "phys_free_gb": round(phys_kb / 1048576, 3),
            "commit_used_pct": round(100 * (limit_kb - avail_kb) / limit_kb, 1),
            "read_at": time.time()}


def check(floor_gb: float = DEFAULT_FLOOR_GB,
          breach_after: int = 2) -> tuple[int, str]:
    """Compare against this script's own previous samples.

    breach_after = how many CONSECUTIVE readings under the floor before
    escalating. Two is the minimum that separates a transient from a state,
    which is why the default is 2 and not 1 (L667: a conclusion about a moving
    quantity rests on more than one reading).
    """
    cur = read_commit()
    if cur is None:
        return 1, ("CANNOT READ COMMIT CHARGE - refusing to judge. A monitor "
                   "that cannot read its quantity must not report health.")
    st_path = AUDIT / "_commit_watch.json"
    prev = (json.loads(st_path.read_text(encoding="utf-8"))
            if st_path.exists() else {})
    under = int(prev.get("consecutive_under", 0))
    under = under + 1 if cur["commit_avail_gb"] < floor_gb else 0
    cur["consecutive_under"] = under
    cur["floor_gb"] = floor_gb
    st_path.parent.mkdir(parents=True, exist_ok=True)
    st_path.write_text(json.dumps(cur, indent=1), encoding="utf-8")

    base = (f"commit_avail={cur['commit_avail_gb']}GB of "
            f"{cur['commit_limit_gb']}GB ({cur['commit_used_pct']}pct used), "
            f"phys_free={cur['phys_free_gb']}GB, floor={floor_gb}GB")
    if under >= breach_after:
        return 2, (f"COMMIT BREACH: available commit has been under the floor "
                   f"for {under} consecutive readings ({base}). A pytest run "
                   f"costs a MEASURED 1.183GB of commit (B2229c), so a pyramid "
                   f"cannot run without risking the live wave. NOTE the physical "
                   f"reading is NOT the signal - it looked comfortable at "
                   f"2.11GB while commit sat at 1.28GB (L670).")
    if under:
        return 0, (f"UNDER FLOOR once ({base}) - one reading is a transient, "
                   f"not a state; {breach_after - under} more to escalate")
    return 0, f"HEALTHY ({base})"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor-gb", type=float, default=DEFAULT_FLOOR_GB)
    ap.add_argument("--breach-after", type=int, default=2)
    a = ap.parse_args()
    code, msg = check(a.floor_gb, a.breach_after)
    print(msg)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
