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
- ENGINE HASH (B2575, S6-B2573i): before each launch the chain hashes the
  engine path (backtest/**/*.py minus tests) and records it in
  output_audit/serial_chain_engine_hash.json keyed by wave. A spec whose
  hash differs from the previous spec's is an engine change MID-CHAIN - the
  cubes on either side are different populations (B2574: a fix to the
  checkpoint writer landed between minq8 and mult1.0 of the b2527 chain,
  and nothing recorded which cubes ran under which engine). Default HALT
  for a human; `--on-engine-change continue` or `"engine_change_accepted":
  true` in the spec lets it proceed, with the change logged and the
  spec's hash record carrying `changed_from`.

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


ENGINE_HASH_RECORD = ROOT / "output_audit" / "serial_chain_engine_hash.json"
HALTS = ROOT / "output_audit" / "chain_halts.jsonl"


def read_halts(path: Path | None = None) -> list[dict]:
    """Every HALT event ever recorded (append-only jsonl; unreadable lines skipped).
    `path` resolves at CALL time (a default bound at def time would pin the
    production file under a test's monkeypatch)."""
    path = HALTS if path is None else path
    if not Path(path).exists():
        return []
    out = []
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            ev = json.loads(ln)
        except ValueError:
            continue
        if isinstance(ev, dict) and ev.get("wave"):
            out.append(ev)
    return out


def undelivered_halt_events(events: list[dict]) -> list[dict]:
    """HALTs whose LAST event per wave still says reported_to_owner=false
    (same shape as postconfig_landing.undelivered_events, B2520)."""
    latest: dict[str, dict] = {}
    for ev in events:
        if isinstance(ev, dict) and ev.get("wave"):
            latest[ev["wave"]] = ev
    return [ev for ev in latest.values() if not ev.get("reported_to_owner")]


def undelivered_halts(path: Path | None = None) -> list[dict]:
    return undelivered_halt_events(read_halts(HALTS if path is None else path))


def mark_halt_reported(waves: list[str], path: Path | None = None, *, by: str = "") -> int:
    """Append a reported=true event per wave; the reader takes the last."""
    path = HALTS if path is None else path
    latest = {ev["wave"]: ev for ev in read_halts(path)}
    n = 0
    with Path(path).open("a", encoding="utf-8") as f:
        for w in waves:
            prev = latest.get(w)
            if prev is None or prev.get("reported_to_owner"):
                continue
            ev = dict(prev)
            ev.update({"reported_to_owner": True,
                       "reported_ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                       "reported_by": by or "verify_turn_compliance"})
            f.write(json.dumps(ev) + "\n")
            n += 1
    return n


def halt(wave: str, reason: str, remaining: list[str], path: Path | None = None) -> int:
    """B2577 (S6-B2573f.a): a chain HALT is an EVENT the owner must see, not a
    log line. The b2527 chain would have stopped silently at any of its four
    HALT paths - the only reader of serial_chain.log is whoever remembers to
    open it (L721 shape). Every HALT now (1) logs, (2) appends a durable
    record with reported_to_owner=false that the Stop hook (scan_chain_halt)
    refuses to let a turn end over until the response carries
    `CHAIN HALT REPORT: <wave>`, and (3) raises a desktop toast, best-effort.
    Returns the chain's exit code (1) so every HALT path is `return halt(...)`."""
    path = HALTS if path is None else path
    line = f"CHAIN HALT at {wave} - {reason}; remaining specs NOT launched (a human decides)"
    log(line)
    ev = {"wave": wave, "reason": reason, "remaining": list(remaining),
          "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
          "log_line": line, "reported_to_owner": False}
    try:
        with Path(path).open("a", encoding="utf-8") as f:
            f.write(json.dumps(ev) + "\n")
    except OSError as exc:
        log(f"HALT RECORD NOT WRITTEN ({exc!r}) - the toast and log line are the only trace")
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from postconfig_landing import toast
        ok, why = toast(f"CHAIN HALT at {wave}", reason[:180])
        log(f"toast {'shown' if ok else 'not shown'}: {why}")
    except Exception as exc:  # the toast is best-effort by contract
        log(f"toast failed {exc!r}")
    return 1


def cleanup_task(task_name: str) -> None:
    """CHAIN DONE self-cleanup (S6-B2573g.a): unregister the Task Scheduler
    task that ran this chain. MEASURED B2577 (scratchpad probe, twice): a
    task's process SURVIVES `Unregister-ScheduledTask` of its own task - the
    proof file written 2 s after the unregister was present - so this is safe
    as the chain's last act. Before this, every finished chain stayed
    registered in state Ready (b2197 + b2213 were still there a week later)."""
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "launch_detached.py"),
         "--cleanup", task_name], cwd=str(ROOT), capture_output=True, text=True)
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    log(f"task cleanup {task_name}: exit {r.returncode} {out[:160]}")


def engine_path_hash() -> tuple[str, int]:
    """Content hash of the engine path: every backtest/**/*.py except the
    tests tree, in sorted relative-path order (path + bytes)."""
    import hashlib
    h = hashlib.sha256()
    n = 0
    for f in sorted((ROOT / "backtest").rglob("*.py")):
        rel = f.relative_to(ROOT).as_posix()
        if rel.startswith("backtest/tests/"):
            continue
        h.update(rel.encode())
        h.update(f.read_bytes())
        n += 1
    return h.hexdigest()[:16], n


def engine_hash_gate(wave: str, prev: dict | None, accepted: bool) -> tuple[bool, dict]:
    """Record this wave's engine hash; refuse (False) when it differs from
    the previous launch's hash and the change is not accepted."""
    digest, n = engine_path_hash()
    rec = {"wave": wave, "engine_hash": digest, "files": n,
           "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        book = json.loads(ENGINE_HASH_RECORD.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        book = {}
    if prev and prev.get("engine_hash") != digest:
        rec["changed_from"] = {"wave": prev.get("wave"),
                               "engine_hash": prev.get("engine_hash")}
        rec["accepted"] = bool(accepted)
    book[wave] = rec
    ENGINE_HASH_RECORD.write_text(json.dumps(book, indent=1), encoding="utf-8")
    if "changed_from" in rec and not accepted:
        log(f"ENGINE CHANGE at {wave}: hash {digest} != {prev.get('engine_hash')} "
            f"(recorded at {prev.get('wave')}); {n} files hashed - not accepted")
        return False, rec
    if "changed_from" in rec:
        log(f"ENGINE CHANGE at {wave} ACCEPTED: hash {digest} != "
            f"{prev.get('engine_hash')} (recorded at {prev.get('wave')})")
    else:
        log(f"engine hash {digest} ({n} files) at {wave}")
    return True, rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wait-for", default=None,
                    help="predecessor wave-summary path to wait on")
    ap.add_argument("--specs", nargs="+", required=True)
    ap.add_argument("--on-engine-change", choices=("halt", "continue"),
                    default="halt",
                    help="B2575: what to do when the engine path hash moves "
                         "between two launches of this chain (default halt)")
    ap.add_argument("--task-name", default=None,
                    help="B2577: the Task Scheduler task running this chain; "
                         "unregistered by the chain itself at CHAIN DONE")
    a = ap.parse_args()
    prev_hash: dict | None = None

    if a.wait_for:
        wp = ROOT / a.wait_for
        log(f"CHAIN START - waiting on predecessor {wp.name}")
        while not wp.exists():
            time.sleep(60)
        pred = json.loads(wp.read_text(encoding="utf-8"))["results"][0]
        log(f"predecessor landed: {pred.get('status')}")
        if pred.get("status") != "COMPLETE":
            return halt(wp.name.replace("_wave_summary.json", ""),
                        f"predecessor read {pred.get('status')}, not COMPLETE; "
                        "nothing launched (the no-relaunch rule)", a.specs)

    for spec_path in a.specs:
        spec = json.loads((ROOT / spec_path).read_text(encoding="utf-8"))
        st = summary_status(spec)
        if st == "COMPLETE":
            log(f"SKIP {spec['wave']} - already COMPLETE (idempotent restart)")
            continue
        if st is not None:
            return halt(spec["wave"], f"existing summary reads {st}",
                        a.specs[a.specs.index(spec_path):])
        ok, prev_hash = engine_hash_gate(
            spec["wave"], prev_hash,
            accepted=(a.on_engine_change == "continue"
                      or bool(spec.get("engine_change_accepted"))))
        if not ok:
            return halt(spec["wave"],
                        "the engine path changed since the previous launch of "
                        "this chain and neither the spec (engine_change_accepted) "
                        "nor --on-engine-change continue accepts it",
                        a.specs[a.specs.index(spec_path):])
        log(f"LAUNCH {spec['wave']} via run_wave (battery included per B2177)")
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "run_wave.py"),
             "--spec", spec_path], cwd=str(ROOT))
        st = summary_status(spec)
        log(f"{spec['wave']} finished: run_wave exit {r.returncode}, "
            f"summary status {st}")
        if st != "COMPLETE":
            return halt(spec["wave"],
                        f"run_wave exit {r.returncode}, summary status {st}",
                        a.specs[a.specs.index(spec_path) + 1:])

    log("CHAIN DONE - every spec COMPLETE")
    if a.task_name:
        cleanup_task(a.task_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
