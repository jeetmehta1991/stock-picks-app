#!/usr/bin/env python
"""B2219 (L656 reader-side half): detect a STALLED run from OUTSIDE the engine.

Source: the active wave's output_<dir>/run_heartbeat.json (written by the
B2148 supervisor) plus this script's own previous sample; per CHECKLIST #77.

WHY THIS EXISTS AND WHY IT IS A SCRIPT: the durable fix for L656 is a progress
watchdog inside the supervisor - but the supervisor lives in
backtest/engine/backtest.py (lines 603/628/911, verified), and the
no-engine-edits-while-a-wave-runs rule bars touching it for as long as the
queue is long. The queue is ~21 configs at ~2h each, so the moratorium's
length equals the queue's length: the monitor could not be fixed until after
the run it exists to protect. That is self-sealing, and the council named it.

The detection does NOT need to live in the engine. The supervisor already
publishes sim_day_index; a reader can compare it against its OWN previous
sample and answer the only question that matters:

    IS THE COUNTER ADVANCING?

which is the L656 rule exactly - liveness needs a counter only the WORK can
advance, diffed across two observations. Heartbeat freshness proves the
supervisor thread lives, never the day loop; a fresh file beside a frozen
counter IS the stall signature. Measured: a dead pool was reported "alive and
cruising" for 51 minutes off a 0.0-minute-old heartbeat.

Exit codes: 0 advancing, 1 no heartbeat / unreadable, 2 STALLED.
State is kept in output_audit/_progress_watch_<wave>.json so consecutive
invocations (a cron, a loop) accumulate evidence rather than re-deciding
from one sample.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "output_audit"


def sample(out_dir: str) -> dict | None:
    hb = ROOT / out_dir / "run_heartbeat.json"
    if not hb.exists():
        return None
    try:
        d = json.loads(hb.read_text(encoding="utf-8"))
    except ValueError:
        return None
    return {"sim_day_index": d.get("sim_day_index"),
            "closed_trades": d.get("closed_trades"),
            "elapsed_hours": d.get("elapsed_hours"),
            "timestamp": d.get("timestamp"), "pid": d.get("pid"),
            "read_at": time.time()}


def check(out_dir: str, stall_after: int = 2) -> tuple[int, str]:
    """Compare against this script's own previous sample.

    stall_after = how many CONSECUTIVE unchanged observations before calling
    it. Two is the minimum that can distinguish "slow" from "stopped", which
    is why the default is 2 rather than 1: one unchanged reading is a slow
    day, two across separate invocations is a counter that is not moving.
    """
    cur = sample(out_dir)
    if cur is None:
        return 1, f"NO HEARTBEAT at {out_dir}/run_heartbeat.json - cannot judge"
    st_path = AUDIT / f"_progress_watch_{out_dir}.json"
    prev = (json.loads(st_path.read_text(encoding="utf-8"))
            if st_path.exists() else {})
    unchanged = int(prev.get("unchanged", 0))
    same_counter = (prev.get("sim_day_index") is not None
                    and prev.get("sim_day_index") == cur["sim_day_index"]
                    and prev.get("closed_trades") == cur["closed_trades"])
    unchanged = unchanged + 1 if same_counter else 0
    cur["unchanged"] = unchanged
    st_path.write_text(json.dumps(cur, indent=1), encoding="utf-8")

    age_min = "unknown"
    if cur["timestamp"]:
        try:
            import datetime as _dt
            ts = _dt.datetime.strptime(cur["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
            ts = ts.replace(tzinfo=_dt.timezone.utc)
            age_min = round(
                (_dt.datetime.now(_dt.timezone.utc) - ts).total_seconds() / 60, 1)
        except ValueError:
            # B2128 ratchet: no silent swallow. An unparseable timestamp is a
            # DISCLOSURE - the heartbeat's own clock field is malformed, which
            # a reader must see rather than have quietly replaced by "unknown".
            age_min = f"UNPARSEABLE timestamp {cur['timestamp']!r}"

    base = (f"sim_day_index={cur['sim_day_index']} "
            f"closed={cur['closed_trades']} pid={cur['pid']} "
            f"heartbeat_age_min={age_min}")
    if unchanged >= stall_after:
        return 2, (f"STALLED: the progress counter has not moved across "
                   f"{unchanged} consecutive observations while the heartbeat "
                   f"stays fresh ({base}). A fresh heartbeat proves the "
                   f"supervisor THREAD lives, not the day loop (L656). "
                   f"Confirm with two CPU samples of pid {cur['pid']} plus a "
                   f"worker, then grep the wave log for Traceback/"
                   f"AssertionError/BrokenPipe. DO NOT relaunch - a human "
                   f"decides.")
    if same_counter:
        return 0, (f"UNCHANGED once ({base}) - one unchanged reading is a slow "
                   f"day, not a stall; {stall_after - unchanged} more to call it")
    return 0, f"ADVANCING ({base})"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True,
                    help="the active wave's output directory name")
    ap.add_argument("--stall-after", type=int, default=2)
    a = ap.parse_args()
    code, msg = check(a.out_dir, a.stall_after)
    print(msg)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
