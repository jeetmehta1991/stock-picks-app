"""S6-B2948 (owner-approved rec, ruling 2026-09-22): the session-independent
chain watchdog - S6-B2573f.c built.

THE GAP WAS DURABILITY, NOT LOUDNESS: every halt already fires four ways,
but the hourly reporter is a session cron that dies with the Claude session
while a 36-config chain runs for days. This watchdog is ONE TICK, designed
to be run every 15 minutes by Windows Task Scheduler - a principal that
outlives every session. Each tick it:

  1. reads output_audit/chain_halts.jsonl for halts still marked
     reported_to_owner=false (reusing run_serial_chain's own readers -
     one definition of "undelivered", not two);
  2. finds the newest output_*/run_heartbeat.json and measures staleness;
  3. decides via assess(): ALERT on an undelivered halt, or on a stale
     heartbeat while the chain log says the chain is still live; QUIET
     when the log's tail says CHAIN DONE or the heartbeat is fresh;
  4. appends its reading to output_audit/chain_watch.jsonl (durable,
     any session can reconstruct what the watchdog saw and when);
  5. raises a desktop toast on ALERT (best-effort, the halt() contract).

Exit 0 = quiet, 1 = alert raised. Idempotent; safe to run at any time,
chain or no chain.

REGISTRATION - the half the owner runs (S6-B2203b, ONE elevated command).
From an ELEVATED PowerShell, so the task survives logoff and sessions:

    schtasks /Create /TN StockPicksChainWatchdog /SC MINUTE /MO 15 ^
      /TR "\"C:\\Users\\jeetm\\Github\\stock-picks-app\\.venv\\Scripts\\python.exe\" \"C:\\Users\\jeetm\\Github\\stock-picks-app\\scripts\\chain_watchdog.py\"" ^
      /RU SYSTEM /RL HIGHEST /F

(No .venv? Use the python.exe that runs the chain.) A NON-elevated
per-user fallback - runs only while jeetm is logged in, still
session-independent - drops /RU SYSTEM /RL HIGHEST from the same command.
Verify with: schtasks /Query /TN StockPicksChainWatchdog
Remove with:  schtasks /Delete /TN StockPicksChainWatchdog /F

run_serial_chain.py logs at CHAIN START whether this task is registered,
so an unwatched multi-day chain announces itself at every future launch.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCH_LOG = ROOT / "output_audit" / "chain_watch.jsonl"
CHAIN_LOG = ROOT / "output_audit" / "serial_chain.log"
STALE_AFTER_MIN = 45  # supervisor heartbeats land minutes apart; 45 is generous
TASK_NAME = "StockPicksChainWatchdog"


def newest_heartbeat() -> tuple[Path | None, float | None, dict | None]:
    """Newest run_heartbeat.json under output_*/ and its age in minutes."""
    best: Path | None = None
    for p in ROOT.glob("output_*/run_heartbeat.json"):
        if best is None or p.stat().st_mtime > best.stat().st_mtime:
            best = p
    if best is None:
        return None, None, None
    age_min = (time.time() - best.stat().st_mtime) / 60.0
    try:
        doc = json.loads(best.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        doc = None
    return best, age_min, doc


def chain_state(log_tail: str) -> str:
    """'done' | 'halted' | 'live' | 'unknown' from the chain log's tail."""
    if not log_tail:
        return "unknown"
    for line in reversed(log_tail.splitlines()):
        if "CHAIN DONE" in line:
            return "done"
        if "CHAIN HALT" in line:
            return "halted"
        if "LAUNCH " in line or "CHAIN START" in line or "finished:" in line:
            return "live"
    return "unknown"


def assess(undelivered: list, hb_age_min: float | None, state: str, *,
           stale_after_min: float = STALE_AFTER_MIN) -> tuple[str, list]:
    """The tick's verdict, pure over its inputs (pin-testable).

    ALERT on any undelivered halt regardless of state; ALERT on a stale or
    absent heartbeat only while the chain is live (a done or halted chain
    legitimately stops beating - the halt path alerts separately)."""
    reasons = []
    if undelivered:
        reasons.append(f"{len(undelivered)} undelivered halt(s): "
                       + ", ".join(e.get("wave", "?") for e in undelivered[:5]))
    if state == "live":
        if hb_age_min is None:
            reasons.append("chain live but NO heartbeat file found")
        elif hb_age_min > stale_after_min:
            reasons.append(f"heartbeat stale {hb_age_min:.0f} min "
                           f"(> {stale_after_min:.0f}) while chain live")
    return ("ALERT" if reasons else "QUIET"), reasons


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from run_serial_chain import read_halts, undelivered_halt_events

    undelivered = undelivered_halt_events(read_halts())
    hb_path, hb_age, hb_doc = newest_heartbeat()
    try:
        tail = CHAIN_LOG.read_text(encoding="utf-8", errors="replace")[-4000:]
    except OSError:
        tail = ""
    state = chain_state(tail)
    verdict, reasons = assess(undelivered, hb_age, state)

    rec = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "verdict": verdict,
        "reasons": reasons,
        "chain_state": state,
        "undelivered_halts": len(undelivered),
        "heartbeat": {
            "path": str(hb_path.relative_to(ROOT)) if hb_path else None,
            "age_min": round(hb_age, 1) if hb_age is not None else None,
            "sim_day": (hb_doc or {}).get("sim_day_index"),
            "pid": (hb_doc or {}).get("pid"),
        },
    }
    try:
        WATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with WATCH_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except OSError as exc:
        print(f"watch record NOT written ({exc!r})", file=sys.stderr)

    print(f"chain watchdog {verdict}: state={state} "
          f"hb_age={rec['heartbeat']['age_min']} "
          f"undelivered={len(undelivered)}"
          + (" - " + "; ".join(reasons) if reasons else ""))
    if verdict == "ALERT":
        try:
            from postconfig_landing import toast
            ok, why = toast("CHAIN WATCHDOG ALERT", "; ".join(reasons)[:180])
            print(f"toast {'shown' if ok else 'not shown'}: {why}")
        except Exception as exc:  # toast is best-effort by contract
            print(f"toast failed ({exc!r})", file=sys.stderr)
        return 1
    return 0


def registered() -> bool:
    """Best-effort: is the scheduled task present? (schtasks query)."""
    try:
        r = subprocess.run(["schtasks", "/Query", "/TN", TASK_NAME],
                           capture_output=True, timeout=15)
        return r.returncode == 0
    except Exception:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
