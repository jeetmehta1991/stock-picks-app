#!/usr/bin/env python
"""Classify a run's summary log: COMPLETE / DEAD_WITHOUT_ENDING / RUNNING.

B2158 (S6-B2157a, L641). THE DEFECT THIS CLOSES: launch_sweep writes its
`CFG=... EXIT=... ELAPSED=...` line only after the engine subprocess returns,
so killing the launcher leaves a log whose SHAPE is identical to a run still
in flight. MEASURED across all 5 summary logs: 2 unfinished, both from kills
I performed, and nothing in either log said so.

A kill signal skips every write path the launcher could use, so the writer
cannot be made honest - the READER has to be. This combines the log with a
live process check, and the rule it enforces is ONE-DIRECTIONAL: absence of a
completion line NEVER reads as RUNNING unless a live pid proves it.

Usage:
  python scripts/classify_run_log.py output_audit/<wave>_summary.log
  python scripts/classify_run_log.py --all
Exit 0 always - this is a reporter, not a gate.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_PS_QUERY = (
    "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
    "Where-Object { $_.CommandLine -like '*run_phase1a*' -or "
    "$_.CommandLine -like '*launch_sweep*' } | "
    "Select-Object -ExpandProperty ProcessId"
)


def live_engine_pids() -> set:
    """PIDs of running engine processes, Windows-authoritative (L569).

    bash ps can report a stale view on this platform, so ask the OS through
    its own tool. A failure here returns EMPTY, which is the safe direction:
    it makes an unfinished log read DEAD rather than inventing a live run.
    """
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command", _PS_QUERY],
            capture_output=True, text=True, timeout=60)
        return {int(x) for x in out.stdout.split() if x.strip().isdigit()}
    except Exception:
        return set()


def classify(log: Path, pids: set | None = None) -> dict:
    log = Path(log)
    if not log.exists():
        return {"log": str(log), "status": "ABSENT", "launches": 0,
                "completions": 0, "note": "no such log"}
    text = log.read_text(encoding="utf-8", errors="replace")
    launches = len(re.findall(r"^LAUNCH ", text, re.M))
    completions = len(re.findall(r"^CFG=", text, re.M))
    if launches == 0:
        return {"log": str(log), "status": "EMPTY", "launches": 0,
                "completions": completions, "note": "no launch recorded"}
    if completions >= launches:
        return {"log": str(log), "status": "COMPLETE", "launches": launches,
                "completions": completions,
                "note": "every launch recorded an ending"}
    live = live_engine_pids() if pids is None else pids
    # THE ONE-DIRECTIONAL RULE (L641): no ending AND no live process = DEAD.
    # Silence is never evidence of work in progress.
    status = "RUNNING" if live else "DEAD_WITHOUT_ENDING"
    note = (f"live engine pids {sorted(live)}" if live else
            "no completion line AND no live engine process - the run was "
            "killed or crashed; its log cannot say so, because a kill skips "
            "the writer (L641)")
    return {"log": str(log), "status": status, "launches": launches,
            "completions": completions, "note": note}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("log", nargs="?", default=None)
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if not a.all and not a.log:
        print("give a log path or --all")
        return 0
    logs = (sorted((ROOT / "output_audit").glob("*_summary.log"))
            if a.all else [Path(a.log)])
    pids = live_engine_pids()
    for lg in logs:
        r = classify(lg, pids)
        print(f"{r['status']:<20} {Path(r['log']).name:<34} "
              f"{r['completions']}/{r['launches']} endings - {r['note']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
