#!/usr/bin/env python
"""B2192 (owner standing directive 2026-08-25): the AUTONOMOUS serial chain.

"All configs are to be launched automatically and autonomously in a serial
fashion without my prompting. The mandatory post config analysis is to be run
each time a config lands autonomously."

Session-held crons advance chains only while a session lives - three restarts
tonight proved that channel unreliable. This runner IS the chain: launched
once, DETACHED (Task Scheduler owns it), it waits for any in-flight
predecessor, then runs each remaining spec through run_wave IN ORDER - and
run_wave already carries the whole per-config contract (manifest -> gate ->
receipt -> legs -> battery with steps 1/2/4 + M1-M10 -> ledger -> summary).
No session anywhere is needed for the band to complete.

RULES ENFORCED:
- SKIP a spec whose wave summary already reads COMPLETE (idempotent restarts).
- STOP the chain on any non-COMPLETE outcome (FAILED / INCOMPLETE) - the
  no-relaunch rule is the owner's; a dead link halts the chain for a human.
- WAIT (poll 60s) for a predecessor summary named via --wait-for; if it
  arrives non-COMPLETE, stop without launching anything.

Usage:
  python scripts/run_serial_chain.py \
      [--wait-for output_audit/<predecessor>_wave_summary.json] \
      --specs output_audit/a_spec.json output_audit/b_spec.json ...
Chain log: output_audit/serial_chain.log (append; every decision recorded -
"no silent misses" is the owner's third clause).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "output_audit" / "serial_chain.log"


def log(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def summary_status(spec: dict) -> str | None:
    """COMPLETE / FAILED-ish / None (no summary yet) for a spec's wave."""
    p = ROOT / "output_audit" / f"{spec['wave']}_wave_summary.json"
    if not p.exists():
        return None
    try:
        j = json.loads(p.read_text(encoding="utf-8"))
        return str(j["results"][0].get("status"))
    except (ValueError, KeyError, IndexError) as exc:
        log(f"UNREADABLE summary {p.name}: {exc!r} - treating as FAILED")
        return "UNREADABLE"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wait-for", default=None,
                    help="predecessor wave-summary path to wait on")
    ap.add_argument("--specs", nargs="+", required=True)
    a = ap.parse_args()

    if a.wait_for:
        wp = ROOT / a.wait_for
        log(f"CHAIN START - waiting on predecessor {wp.name}")
        while not wp.exists():
            time.sleep(60)
        pred = json.loads(wp.read_text(encoding="utf-8"))["results"][0]
        log(f"predecessor landed: {pred.get('status')}")
        if pred.get("status") != "COMPLETE":
            log("CHAIN HALT - predecessor did not COMPLETE; nothing launched "
                "(the no-relaunch rule; a human decides)")
            return 1

    for spec_path in a.specs:
        spec = json.loads((ROOT / spec_path).read_text(encoding="utf-8"))
        st = summary_status(spec)
        if st == "COMPLETE":
            log(f"SKIP {spec['wave']} - already COMPLETE (idempotent restart)")
            continue
        if st is not None:
            log(f"CHAIN HALT at {spec['wave']} - existing summary reads {st}; "
                "a human decides")
            return 1
        log(f"LAUNCH {spec['wave']} via run_wave (battery included per B2177)")
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "run_wave.py"),
             "--spec", spec_path], cwd=str(ROOT))
        st = summary_status(spec)
        log(f"{spec['wave']} finished: run_wave exit {r.returncode}, "
            f"summary status {st}")
        if st != "COMPLETE":
            log(f"CHAIN HALT - {spec['wave']} did not COMPLETE; remaining "
                "specs NOT launched (a human decides)")
            return 1

    log("CHAIN DONE - every spec COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
