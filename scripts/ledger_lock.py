#!/usr/bin/env python
"""B2207 (S6-B2205a): the ONE locked writer for postconfig_ledger.json.

Source: output_audit/postconfig_ledger.json (the battery's shared record);
per CHECKLIST #77.

THE DEFECT THIS CLOSES: both ledger writers (run_wave.py at arm completion,
run_postconfig.py --write-ledger) did an unlocked read-modify-write with a
non-atomic write_text. Two configs landing simultaneously - exactly what a
parallel-config program produces - could interleave: the second read happens
before the first write lands, and the first landing's entry is silently lost;
or a reader catches a half-written file and gets a JSON parse error. The
B2205 council named this the PREREQUISITE for any parallel program on any
hardware, and the owner ordered it built (2026-08-26).

DESIGN (both halves matter):
- MUTUAL EXCLUSION: filelock.FileLock on <ledger>.lock around the whole
  read-modify-write. filelock is already a live dependency (cache.py:48).
- ATOMIC REPLACE: the new content goes to a temp file in the same directory,
  then os.replace() - readers (postconfig_report, verify_postconfig_complete)
  stay lock-free and can never see a torn file: they read the old version or
  the new one, nothing in between.

Timeout is deliberately long (120s): a landing's ledger write contends only
with another landing's, which holds the lock for milliseconds. A timeout here
means something is wedged, and the loud exception is the correct outcome
(a guard must fail closed - L642).
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Callable

import filelock

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "output_audit" / "postconfig_ledger.json"
LOCK_TIMEOUT_S = 120.0


def locked_ledger_update(mutate: Callable[[dict], dict],
                         ledger_path: Path | None = None,
                         timeout_s: float | None = None) -> dict:
    """Read the ledger, apply mutate(ledger) -> ledger, write back atomically.

    The entire read-modify-write holds the sidecar lock, so concurrent
    landings serialize instead of losing updates. Returns the written dict.
    """
    lp = Path(ledger_path) if ledger_path is not None else LEDGER
    lock = filelock.FileLock(str(lp) + ".lock",
                             timeout=LOCK_TIMEOUT_S if timeout_s is None
                             else timeout_s)
    with lock:
        ledger = (json.loads(lp.read_text(encoding="utf-8"))
                  if lp.exists() else {})
        ledger = mutate(ledger)
        fd, tmp = tempfile.mkstemp(dir=str(lp.parent),
                                   prefix=lp.name + ".tmp.")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(json.dumps(ledger, indent=1))
            os.replace(tmp, lp)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
    return ledger
