"""S6-B3066: sample the resource that actually fails, from OUTSIDE the engine.

WHY THIS EXISTS. S6-B3058 closed blaming CPU contention from my own pyramid
runs. S6-B3065 refuted that on a better read of the same data: the direct
duty-FRACTION correlation with runtime is +0.086, and the most-contended candle
config ran at fleet median while the least-contended ran slower. What survives
is that the engine did IDENTICAL work 2.95x slower - c13 and c15 both covered
249 sim-days with 137 and 132 closed trades under one engine hash, at 1.5003 h
against 4.4266 h. Sleep, code drift and orphan processes are all ruled out.

The leading hypothesis is MEMORY, not CPU: a single pytest process was measured
holding a 9502 MB working set on a 16009 MB box with 874 MB free. Page eviction
damages a run AFTER the evicting process exits, which is exactly why a
concurrency instrument reads ~0 while the aftermath persists - L670's rule,
measure the quantity that FAILS rather than the one the OS surfaces first.

That hypothesis CANNOT be tested from what is on disk: run_heartbeat.json is a
single final snapshot and the wave summary carries only a total, so whether a
config was slow throughout or degraded partway is unanswerable retrospectively.
There are 17 configs left to collect it from.

WHY IT IS EXTERNAL. Instrumenting the engine's own heartbeat would edit
backtest/ mid-campaign, and the S6-B2984 chain-contamination rule forbids that:
a config imports whatever code is on disk when it STARTS, so an edit mid-chain
leaves early and late configs on different code and silently corrupts the
comparison the campaign exists to make. This file is not under backtest/ and is
not in run_serial_chain.BATTERY_PATHS, so it changes neither the engine hash nor
the battery hash - VERIFIED, not assumed, by test_b3066_sampler_is_off_the_hot_paths.

It is a RECORDER, never a gate. It reads, appends one JSON object per sample to
output_audit/resource_samples.jsonl, and exits. It refuses nothing, kills
nothing, and cannot fail a run - a disclosure that could break what it observes
would be worse than no disclosure (the S6-B3061 principle).

USAGE
    python scripts/resource_sampler.py --interval 60 --minutes 0
        --interval  seconds between samples (default 60)
        --minutes   stop after N minutes; 0 means run until killed
        --out       override the output path
        --once      take exactly one sample and exit (used by the pins)
"""
from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# S6-B2921/L846: resolve the tree by MARKER and refuse one the marker does not
# confirm - a script run from a draft location otherwise reads a nonexistent
# tree and reports confidently about it.
ROOT = Path(__file__).resolve().parent.parent
if not (ROOT / "backtest").is_dir() or not (ROOT / "EXECUTION_QUEUE.md").is_file():
    raise SystemExit(
        "resource_sampler: %s is not the stock-picks-app tree (no backtest/ "
        "and EXECUTION_QUEUE.md) - refusing rather than sampling the wrong "
        "machine state into the wrong file" % ROOT)

OUT = ROOT / "output_audit" / "resource_samples.jsonl"

# S6-B3066 / #122: every broad except in this file records WHY it fired here,
# and sample() copies it into the record. A recorder whose failures are silent
# produces a series where a gap and a zero look identical - which is the exact
# defect this sampler exists to stop happening to the engine's runtime.
_ERRORS: dict = {}

# The engine's process names, so a sample can attribute memory rather than only
# total it. Matched as substrings of the command line.
ENGINE_MARKERS = ("run_phase1a.py", "run_wave.py", "launch_sweep.py",
                  "run_serial_chain.py")
MINE_MARKERS = ("pytest", "pyramid_gate.py")


def _ps_rows() -> list[dict]:
    """Every python process with its working set and command line.

    PowerShell is authoritative for Windows process truth
    (feedback_powershell_authoritative_for_windows_process_truth); bash ps is
    stale here and was measured stale in this very session. Returns [] rather
    than raising - a recorder must not be able to break what it observes.
    """
    ps = (
        "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
        "Select-Object ProcessId,WorkingSetSize,CommandLine | ConvertTo-Json "
        "-Compress -Depth 3"
    )
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive",
                            "-Command", ps],
                           capture_output=True, text=True, timeout=30)
        data = json.loads((r.stdout or "").strip() or "[]")
    except Exception as exc:
        # #122 / L641: an EMPTY list is indistinguishable from "no python
        # processes are running", which is a real and meaningful reading. A
        # recorder must never let a failed read impersonate a measurement.
        _ERRORS["ps_rows"] = type(exc).__name__
        return []
    if isinstance(data, dict):
        data = [data]
    rows = []
    for d in data or []:
        try:
            rows.append({"pid": int(d.get("ProcessId") or 0),
                         "ws_mb": round((d.get("WorkingSetSize") or 0) / 1048576.0, 1),
                         "cmd": (d.get("CommandLine") or "")[:400]})
        except Exception as exc:
            # same class: a dropped row shrinks a total silently, so count it
            _ERRORS["ps_row_skipped"] = (
                _ERRORS.get("ps_row_skipped", 0) + 1
                if isinstance(_ERRORS.get("ps_row_skipped"), int) else 1)
            _ERRORS.setdefault("ps_row_error", type(exc).__name__)
            continue
    return rows


def _os_memory() -> dict:
    """Commit charge and physical RAM.

    L670: the failing allocation asks for COMMIT, and free physical RAM can read
    comfortable in the same instant commit is nearly exhausted - so both are
    recorded and commit is recorded first.
    """
    ps = (
        "$o=Get-CimInstance Win32_OperatingSystem; "
        "$c=Get-CimInstance Win32_ComputerSystem; "
        "[pscustomobject]@{"
        "commit_limit_mb=[math]::Round($o.TotalVirtualMemorySize/1KB,0);"
        "commit_free_mb=[math]::Round($o.FreeVirtualMemory/1KB,0);"
        "phys_total_mb=[math]::Round($c.TotalPhysicalMemory/1MB,0);"
        "phys_free_mb=[math]::Round($o.FreePhysicalMemory/1KB,0);"
        "cpus=$c.NumberOfLogicalProcessors} | ConvertTo-Json -Compress"
    )
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive",
                            "-Command", ps],
                           capture_output=True, text=True, timeout=30)
        return json.loads((r.stdout or "").strip() or "{}")
    except Exception as exc:
        # {} makes every memory field null, and null reads as "not measured"
        # with no way to tell a failed query from an unsupported platform.
        _ERRORS["os_memory"] = type(exc).__name__
        return {}


def _inflight() -> str:
    """Which serial-chain config is running, via the chain log's own reducer
    shape - a LAUNCH with no matching finished line (L737)."""
    import re
    log = ROOT / "output_audit" / "serial_chain.log"
    try:
        if not log.exists():
            return "none"
        pend: dict[str, bool] = {}
        for line in log.read_text(encoding="utf-8", errors="replace").split("\n"):
            m = re.match(r"\S+Z LAUNCH (\S+)", line)
            if m:
                pend[m.group(1)] = True
                continue
            m = re.match(r"\S+Z (\S+) finished", line)
            if m:
                pend.pop(m.group(1), None)
        return ",".join(sorted(pend)) if pend else "none"
    except Exception:
        return "unknown"


def _engine_progress(wave: str) -> dict:
    """sim_day_index and elapsed_hours from the running config's heartbeat.

    This is what turns a memory reading into a RATE: sim-days per hour is the
    quantity the 2.95x anomaly is expressed in, and reading it beside memory is
    the whole point of sampling rather than snapshotting at the end.
    """
    if not wave or wave in ("none", "unknown"):
        return {}
    try:
        for d in sorted((ROOT).glob("output_%s_*" % wave)):
            hb = d / "run_heartbeat.json"
            if hb.is_file():
                j = json.loads(hb.read_text(encoding="utf-8"))
                return {"wave_dir": d.name,
                        "sim_day_index": j.get("sim_day_index"),
                        "elapsed_hours": j.get("elapsed_hours"),
                        "closed_trades": j.get("closed_trades"),
                        "open_trades": j.get("open_trades")}
    except Exception as exc:
        # CHECKLIST #122: never swallow silently. A sample that could not read
        # the heartbeat must SAY so - otherwise a gap in the series reads as
        # "no engine was running" rather than "the read failed", which is
        # exactly L641's silence-is-not-evidence defect in a recorder whose
        # whole purpose is to make an absence answerable.
        return {"progress_read_error": type(exc).__name__}
    return {"progress_read_error": "no run_heartbeat.json under output_%s_*"
            % wave}


def sample() -> dict:
    """One observation. Never raises - but never silent either."""
    _ERRORS.clear()
    procs = _ps_rows()
    mem = _os_memory()
    wave = _inflight()

    def _sum(markers):
        return round(sum(p["ws_mb"] for p in procs
                         if any(m in p["cmd"] for m in markers)), 1)

    engine_mb = _sum(ENGINE_MARKERS)
    mine_mb = _sum(MINE_MARKERS)
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "commit_limit_mb": mem.get("commit_limit_mb"),
        "commit_free_mb": mem.get("commit_free_mb"),
        "phys_total_mb": mem.get("phys_total_mb"),
        "phys_free_mb": mem.get("phys_free_mb"),
        "cpus": mem.get("cpus"),
        "python_procs": len(procs),
        "engine_ws_mb": engine_mb,
        "my_tooling_ws_mb": mine_mb,
        "chain_inflight": wave,
    }
    cl, cf = rec["commit_limit_mb"], rec["commit_free_mb"]
    rec["commit_used_pct"] = (round(100.0 * (1 - cf / cl), 1)
                              if cl and cf is not None else None)
    rec.update(_engine_progress(wave))
    if _ERRORS:
        rec["read_errors"] = dict(_ERRORS)
    return rec


def append(rec: dict, out: Path = OUT) -> None:
    """Append one line. Bytes, with an explicit newline - never write_text,
    which re-encodes every ending in the file (L756/L858)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    line = (json.dumps(rec, sort_keys=True) + chr(10)).encode("utf-8")
    with io.open(out, "ab") as fh:
        fh.write(line)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--interval", type=float, default=60.0)
    ap.add_argument("--minutes", type=float, default=0.0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--once", action="store_true")
    a = ap.parse_args(argv)
    out = Path(a.out) if a.out else OUT

    if a.once:
        rec = sample()
        append(rec, out)
        print(json.dumps(rec, sort_keys=True))
        return 0

    deadline = time.time() + a.minutes * 60 if a.minutes else None
    n = 0
    while True:
        rec = sample()
        append(rec, out)
        n += 1
        sys.stdout.write(
            "%s inflight=%s phys_free=%sMB commit_used=%s%% engine=%sMB "
            "mine=%sMB sim_day=%s\n"
            % (rec["ts"], rec["chain_inflight"], rec["phys_free_mb"],
               rec["commit_used_pct"], rec["engine_ws_mb"],
               rec["my_tooling_ws_mb"], rec.get("sim_day_index")))
        sys.stdout.flush()
        if deadline and time.time() >= deadline:
            break
        time.sleep(max(1.0, a.interval))
    print("samples written: %d -> %s" % (n, out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
