#!/usr/bin/env python
# Source: output_<dir>/run_heartbeat.json + output_audit/<wave>_wave_summary.json
# via scripts/watch_run_progress.py, per CHECKLIST #77.
"""B2618 (S6-B2548 P0 + S6-B2573f leg c): a reporter that is a PEER of the
job, not of the turn.

THE CLASS THIS CLOSES: #185/#186 mandate CronCreate for run monitoring, and
CronCreate is SESSION-ONLY - five arming mechanisms have failed with the
session that armed them (S6-B2548 census; the third guard in the 4x cap
overrun postmortem was exactly 'the external cron monitor (session-only, and
it produced no report overnight)'). A reporter armed by a turn dies with the
turn. This one is registered in Task Scheduler with a 15-minute REPEATING
trigger - the same scheduler that owns the detached chain (B2188), so it
inherits the run's lifetime, and each invocation is short-lived so there is
no long process to die between firings.

Per invocation it answers the only questions that matter, reader-side:
  - is the wave summary on disk?           -> DONE (toast once, final line)
  - is the counter advancing?              -> via watch_run_progress.check
    (L656: liveness is a counter only the WORK can advance, diffed across
    two observations; heartbeat freshness proves the writer, never the work)
  - heartbeat gone AND no engine pids?     -> DEAD (toast once)
and appends ONE json line to output_audit/chain_status_durable.jsonl - a
file ANY session can read (L637: the durable channel is a file, never a
session-held pipe), which the hourly report reads instead of re-deriving.

Toasts are deduped through output_audit/_peer_reporter_<wave>.json: DONE and
DEAD toast exactly once; a STALL toasts once per episode (re-arms when the
counter advances again).

CONTRARIAN CONDITION (S6-B2548, adopted verbatim): five arming mechanisms
have failed and zero have been measured surviving end to end - so this ships
as ONE ARMED INSTANCE plus a measurement, and is mandated nowhere until it
has been observed surviving a full session death. Wiring into
launch_detached.py is deferred on that measurement AND on the launch-file
freeze (the Step-2 chain is live).

Registration is NOT hardened (no SYSTEM principal): a toast from session 0
cannot reach the user's desktop, and this task's whole job is reaching the
user. Its loss on logoff is part of what the survival measurement measures.

Usage:
  python scripts/peer_reporter.py --out-dir <cube_dir> --wave <tag> \
      --summary output_audit/<tag>_wave_summary.json          # one sample
  python scripts/peer_reporter.py --register --out-dir ... --wave ... \
      --summary ...                                           # arm the task
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "output_audit"
sys.path.insert(0, str(ROOT / "scripts"))

DURABLE = AUDIT / "chain_status_durable.jsonl"


def _state_path(wave: str) -> Path:
    return AUDIT / f"_peer_reporter_{wave}.json"


def decide(summary_exists: bool, hb_exists: bool, engine_pids: int,
           progress_code: int, prev: dict) -> tuple[str, str | None]:
    """Pure decision: (status, toast_body_or_None). prev carries the dedupe
    flags {'done_toasted','dead_toasted','stall_toasted'}."""
    if summary_exists:
        toast = None if prev.get("done_toasted") else "wave COMPLETE - summary landed"
        return "DONE", toast
    if not hb_exists and engine_pids == 0:
        toast = None if prev.get("dead_toasted") else (
            "run DEAD - no heartbeat and no engine process (L641: absence of "
            "a completion record reads as DEAD)")
        return "DEAD", toast
    if not hb_exists:
        return "GAP", None            # engine alive, heartbeat not yet written
    if progress_code == 2:
        toast = None if prev.get("stall_toasted") else (
            "run STALLED - counter frozen across 2+ observations while the "
            "heartbeat stays fresh (L656)")
        return "STALL", toast
    return "ADVANCING", None


def sample_once(out_dir: str, wave: str, summary: str) -> int:
    import watch_run_progress as wrp
    import classify_run_log as crl
    st_path = _state_path(wave)
    prev = json.loads(st_path.read_text(encoding="utf-8")) if st_path.exists() else {}

    summary_exists = (ROOT / summary).exists()
    hb_exists = (ROOT / out_dir / "run_heartbeat.json").exists()
    pids = len(crl.live_engine_pids()) if not summary_exists else 0
    code, msg = wrp.check(out_dir) if hb_exists else (1, "no heartbeat")

    status, toast_body = decide(summary_exists, hb_exists, pids, code, prev)

    line = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "wave": wave, "status": status, "progress": msg,
            "engine_pids": pids, "reporter": "peer_reporter B2618"}
    with DURABLE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")

    if toast_body:
        from postconfig_landing import toast
        toast(f"stock-picks {wave}", toast_body)
        prev[{"DONE": "done_toasted", "DEAD": "dead_toasted",
              "STALL": "stall_toasted"}[status]] = True
    if status == "ADVANCING":
        prev["stall_toasted"] = False     # re-arm the stall toast per episode
    st_path.write_text(json.dumps(prev), encoding="utf-8")
    print(f"{status}: {msg}")
    return 0


def register(out_dir: str, wave: str, summary: str) -> int:
    """Register the 15-min repeating task; report the task we OBSERVE (B2559)."""
    name = f"stockpicks_peer_reporter_{wave}"
    log = AUDIT / f"_peer_reporter_{wave}.log"
    args = (f'/c "cd /d {ROOT} && set PYTHONPATH=. && '
            f'{sys.executable} scripts\\peer_reporter.py --out-dir {out_dir} '
            f'--wave {wave} --summary {summary} >> {log} 2>&1"')
    script = f"""
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument '{args}'
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 15) `
    -RepetitionDuration (New-TimeSpan -Days 7)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName "{name}" -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
$t = Get-ScheduledTask -TaskName "{name}" -ErrorAction SilentlyContinue
if ($t) {{
    Write-Output ("registered " + "{name}" + " state=" + $t.State)
}} else {{
    Write-Output ("register_failed " + "{name}" + " - the task does not exist after Register-ScheduledTask")
}}
"""
    ps1 = AUDIT / "_peer_reporter_register.ps1"
    ps1.write_text(script, encoding="utf-8")
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy",
                        "Bypass", "-File", str(ps1)],
                       capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    print(out.strip()[:400])
    return 0 if ("registered " in out and "state=" in out) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--wave", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--register", action="store_true")
    a = ap.parse_args()
    if a.register:
        return register(a.out_dir, a.wave, a.summary)
    return sample_once(a.out_dir, a.wave, a.summary)


if __name__ == "__main__":
    raise SystemExit(main())
